"""Narrow, actual filesystem effect behind the G3 synthetic evidence gate.

The ONLY external effect is creation of an EMPTY event marker file in a
private, pre-provisioned directory. No arbitrary path, file content, overwrite,
delete, command execution, outbound network, hardware or broad actuator.
Gate and filesystem sink are co-located in a trusted process, with the
untrusted principal denied filesystem access by OS permissions.

Not cross-resource atomic: durable synthetic admission precedes marker creation.
A crash after admission but before marker creation can be recovered by retry,
provided current authority is still valid. Marker creation is idempotent.
"""
import hashlib
import os
import stat


class ProtectedFilesystemSink:
    def __init__(self, gate, directory):
        if not hasattr(gate, "dispatch_synthetic") or gate.ed25519_public_key is None:
            raise ValueError("protected signed-effect gate required")
        # The directory is provisioned by the trusted controller, never by
        # any untrusted request. Fail closed on symlinks and weak permissions.
        descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(descriptor)
            if (not stat.S_ISDIR(info.st_mode) or
                    info.st_mode & 0o077 or info.st_uid != os.geteuid()):
                raise PermissionError("effect directory must be owned and private (0700)")
        except BaseException:
            os.close(descriptor)
            raise
        self.gate = gate
        self.dirfd = descriptor

    @staticmethod
    def _marker_name(event_id):
        return hashlib.sha256(event_id.encode("utf-8")).hexdigest() + ".marker"

    def _verify_existing_marker(self, name):
        """Open the marker itself without following a symlink; sync on replay."""
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW,
                         dir_fd=self.dirfd)
        except (OSError, ValueError):
            return False
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_size != 0 or
                    info.st_nlink != 1 or info.st_uid != os.geteuid() or
                    info.st_mode & 0o077):
                return False
            os.fsync(fd)
            os.fsync(self.dirfd)
            return True
        finally:
            os.close(fd)

    def reconcile_report(self):
        """Read-only local recovery inventory, not permission to replay an action.

        The report needs the trusted sink handle; never expose it on the
        public broker socket. A pending event can be recovered ONLY through
        apply_marker with fresh, valid authorization. Orphans fail closed.
        """
        with self.gate.lock:
            integrity = self.gate.audit()
            if not integrity["ok"]:
                return {"ok": False, "code": integrity["code"]}
            records = self.gate.db.execute(
                "SELECT event_id FROM synthetic_effects").fetchall()
            expected = {self._marker_name(event_id): event_id
                        for (event_id,) in records}
            present = set(os.listdir(self.dirfd))
            unknown = sorted(present - set(expected))
            if unknown:
                return {"ok": False, "code": "unaccounted_files",
                        "count": len(unknown)}
            invalid = sorted(name for name in present if
                             not self._verify_existing_marker(name))
            if invalid:
                return {"ok": False, "code": "marker_integrity",
                        "count": len(invalid)}
            pending = sorted(expected[name] for name in expected if
                             name not in present)
            return {"ok": True, "code": "reconciliation_report",
                    "pending_count": len(pending),
                    "applied_count": len(present),
                    "pending_event_ids": pending}

    def apply_marker(self, event, *, now, permit):
        """Recheck under the SAME gate lock that serializes hold/revocation.

        The marker is a narrow real filesystem effect. A committed DB record
        is not equivalent to the marker: the file must be created/fsynced.
        """
        with self.gate.lock:
            # The recovery inventory MUST be a precondition, not merely an
            # optional diagnostic report. Hold the gate lock across inventory,
            # authorization and filesystem creation to serialize controller
            # holds/revocations and other effects inside this process.
            inventory = self.reconcile_report()
            if not inventory["ok"]:
                return {"ok": False, "code": "effect_store_" + inventory["code"]}
            # Any unrelated previously journaled effect whose real marker is
            # absent must be explicitly recovered or reviewed first. Never
            # silently proceed with another effect after a partial crash.
            if type(event) is not dict or type(event.get("event_id")) is not str:
                return {"ok": False, "code": "invalid_effect_identity"}
            pending = inventory["pending_event_ids"]
            if any(event_id != event["event_id"] for event_id in pending):
                return {"ok": False, "code": "unresolved_prior_effect"}
            result = self.gate.dispatch_synthetic(event, now=now, permit=permit)
            if not result["ok"]:
                return result
            if type(event) is not dict or type(event.get("event_id")) is not str:
                return {"ok": False, "code": "invalid_effect_identity"}
            event_id = event["event_id"]
            if not event_id:
                return {"ok": False, "code": "invalid_effect_identity"}
            name = self._marker_name(event_id)
            # Kernel-enforced exclusive creation makes retry idempotent.
            try:
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o600, dir_fd=self.dirfd)
            except FileExistsError:
                # A previous crash may have occurred BEFORE fsync. Re-open,
                # verify and fsync both the existing marker and its directory.
                if not self._verify_existing_marker(name):
                    return {"ok": False, "code": "marker_integrity"}
                return {"ok": True, "code": "marker_already_applied",
                        "receipt": result["receipt"]}
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(self.dirfd)
            return {"ok": True, "code": "filesystem_marker_applied",
                    "receipt": result["receipt"]}

    def close(self):
        os.close(self.dirfd)
