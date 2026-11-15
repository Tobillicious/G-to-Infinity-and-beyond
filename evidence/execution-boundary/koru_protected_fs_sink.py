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

    def apply_marker(self, event, *, now, permit):
        """Recheck under the SAME gate lock that serializes hold/revocation.

        The marker is a narrow real filesystem effect. A committed DB record
        is not equivalent to the marker: the file must be created/fsynced.
        """
        with self.gate.lock:
            result = self.gate.dispatch_synthetic(event, now=now, permit=permit)
            if not result["ok"]:
                return result
            if type(event) is not dict or type(event.get("event_id")) is not str:
                return {"ok": False, "code": "invalid_effect_identity"}
            event_id = event["event_id"]
            if not event_id:
                return {"ok": False, "code": "invalid_effect_identity"}
            name = hashlib.sha256(event_id.encode("utf-8")).hexdigest() + ".marker"
            # Kernel-enforced exclusive creation makes retry idempotent.
            try:
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_NOFOLLOW, 0o600, dir_fd=self.dirfd)
            except FileExistsError:
                # Trust only an empty regular marker owned by this service.
                try:
                    info = os.stat(name, dir_fd=self.dirfd, follow_symlinks=False)
                except OSError:
                    return {"ok": False, "code": "marker_integrity"}
                if (not stat.S_ISREG(info.st_mode) or info.st_size != 0 or
                        info.st_nlink != 1 or info.st_uid != os.geteuid() or
                        info.st_mode & 0o077):
                    return {"ok": False, "code": "marker_integrity"}
                return {"ok": True, "code": "marker_already_applied", "receipt": result["receipt"]}
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            os.fsync(self.dirfd)
            return {"ok": True, "code": "filesystem_marker_applied",
                    "receipt": result["receipt"]}

    def close(self):
        os.close(self.dirfd)
