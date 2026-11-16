"""Local cross-process commit fence for the *research* signed G3 writer.

One trusted host, one private lock file, one SQLite writer epoch table.
An external revoker and the writer participate in the SAME advisory lock
protocol, enforcing a linear order for local epoch revocations and effects.
It does NOT enforce remote G-Mesh revocation or protect against a privileged
bypass, disobedient writer process, compromised host or power-loss faults.

Do not expose local arm/hold, the lock FD, or SQLite to untrusted callers.
"""
import contextlib
import fcntl
import os
from pathlib import Path
import sqlite3
import stat
import threading

from g3_signed_bridge import SignedG3Writer


class FileFence:
    def __init__(self, path):
        p = Path(path)
        parent = p.parent
        pfd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parent_stat = os.fstat(pfd)
            if (parent_stat.st_uid != os.geteuid() or
                    parent_stat.st_mode & 0o077):
                raise PermissionError("fence parent must be private to trusted writer")
            self.fd = os.open(p.name, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW |
                              os.O_CLOEXEC, 0o600, dir_fd=pfd)
        finally:
            os.close(pfd)
        s = os.fstat(self.fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or
                s.st_uid != os.geteuid() or s.st_mode & 0o077):
            os.close(self.fd)
            raise PermissionError("fence must be a private owned regular file")
        # flock is per open-file description; separate threads in this process
        # also require an ordinary mutex around the shared descriptor.
        self.mutex = threading.RLock()

    @contextlib.contextmanager
    def exclusive(self):
        with self.mutex:
            fcntl.flock(self.fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(self.fd, fcntl.LOCK_UN)

    def close(self):
        os.close(self.fd)


class FencedSignedG3Writer(SignedG3Writer):
    def __init__(self, path, output_dir, *, fence_path, **kwargs):
        self.fence = FileFence(fence_path)
        try:
            # The initial disarm must also serialize against external holders.
            with self.fence.exclusive():
                super().__init__(path, output_dir, **kwargs)
        except BaseException:
            self.fence.close()
            raise

    def write(self, request):
        with self.fence.exclusive():
            return super().write(request)

    def arm(self):
        with self.fence.exclusive():
            return super().arm()

    def hold(self):
        with self.fence.exclusive():
            return super().hold()

    def close(self):
        with self.fence.exclusive():
            super().close()
        self.fence.close()



class VetoBoundFencedSignedG3Writer(FencedSignedG3Writer):
    """Opt-in, deny-only rights-veto integration for the bounded local writer.

    A trusted controller MUST provision the RightsVetoJournal with its own
    FileFence pointing to this writer's identical lock inode, and only its
    trusted API may record withdrawals. The writer reads rights evidence
    under that same interprocess lock, then keeps the lock through the
    actual filesystem link/commit. Absence of withdrawal is NOT consent:
    the inherited signed G3 gate is a separate, synthetic authority check.

    Not a universal X3, physical-control, or authentic-consent guarantee.
    """

    def __init__(self, path, output_dir, *, fence_path, veto_journal,
                 trusted_subjects, trusted_authority_refs, **kwargs):
        # Late import keeps the existing signed research writer usable in
        # isolated test harnesses that do not install rights modules.
        from g3_rights_veto.rights_veto import RightsVetoJournal
        if type(veto_journal) is not RightsVetoJournal:
            raise TypeError("trusted RightsVetoJournal required")
        if (type(trusted_subjects) is not dict or not trusted_subjects or
                any(type(k) is not str or not k or
                    type(v) is not str or not v
                    for k, v in trusted_subjects.items())):
            raise ValueError("nonempty trusted event-to-subject mapping required")
        if (type(trusted_authority_refs) is not dict or
                set(trusted_authority_refs) != set(trusted_subjects) or
                any(type(v) is not str or not v
                    for v in trusted_authority_refs.values())):
            raise ValueError("trusted event authority references required")
        guard = getattr(veto_journal, "publication_fence", None)
        if not isinstance(guard, FileFence):
            raise PermissionError("unbound rights journal cannot enforce publication")
        super().__init__(path, output_dir, fence_path=fence_path, **kwargs)
        try:
            a = os.fstat(self.fence.fd)
            b = os.fstat(guard.fd)
            if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
                raise PermissionError("rights/writer fence inode mismatch")
            if set(self.manifest) != set(trusted_subjects):
                raise PermissionError("subject mapping must cover every permitted event")
            self.veto_journal = veto_journal
            self.trusted_subjects = dict(trusted_subjects)
            self.trusted_authority_refs = dict(trusted_authority_refs)
            self._verify_veto_binding()
        except BaseException:
            self.close()
            raise

    def _verify_veto_binding(self):
        """Fail on missing/swapped journal or fence paths; local host only."""
        j = self.veto_journal
        bound = j.publication_fence
        a = os.fstat(self.fence.fd)
        b = os.fstat(bound.fd)
        if ((a.st_dev, a.st_ino) != (b.st_dev, b.st_ino) or
                not stat.S_ISREG(a.st_mode) or a.st_nlink != 1):
            raise PermissionError("rights/writer fence binding lost")
        rows = j.db.execute("PRAGMA database_list").fetchall()
        main = [entry[2] for entry in rows if entry[1] == "main"]
        if len(main) != 1 or not main[0] or os.path.islink(main[0]):
            raise PermissionError("rights journal identity unavailable")
        p = Path(main[0])
        st = os.stat(p, follow_symlinks=False)
        if (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or
                st.st_uid != os.geteuid() or
                stat.S_IMODE(st.st_mode) != 0o600):
            raise PermissionError("rights journal not private")
        if (str(p.absolute()) != j.bound_db_path or
                (st.st_dev, st.st_ino) != j.bound_db_identity):
            raise PermissionError("rights journal identity mismatch")

    def write(self, request):
        # This lock is also taken by RightsVetoJournal.record_withdrawal
        # for the trusted controller, including across separate processes.
        # A completed withdrawal cannot be overtaken by a later publish.
        with self.fence.exclusive():
            try:
                self._verify_veto_binding()
                if (type(request) is not dict or
                        type(request.get("event")) is not dict or
                        type(request.get("id")) is not str):
                    return {"ok": False, "code": "signed_envelope_required"}
                event_id = request["id"]
                subject = self.trusted_subjects.get(event_id)
                record_ref = self.trusted_authority_refs.get(event_id)
                output_digest = self.manifest.get(event_id)
                if (subject is None or record_ref is None or
                        request["event"].get("authority_ref") != record_ref or
                        output_digest is None):
                    return {"ok": False, "code": "rights_event_mapping_unavailable"}
                journal = self.veto_journal
                with journal.lock:
                    generation = journal._state()  # integrity-checked, live DB
                    veto = journal.inspect(
                        record_ref=record_ref, subject=subject,
                        action="publish", effect_digest=output_digest,
                        expected_generation=generation)
                if (veto.get("local_veto") is not False or
                        veto.get("code") != "no_local_withdrawal_found_not_authorized"):
                    return {"ok": False, "code": "rights_veto_or_unavailable"}
                # Recheck the live process's output write-capabilities at
                # effect time. A successful startup-only host preflight
                # cannot exclude descriptors acquired afterwards.
                # This is a same-process research check, not host-wide
                # revocation or syscall confinement.
                from g3_bound_host_server import (
                    _no_retained_writable_output_handles,
                )
                if not _no_retained_writable_output_handles(self):
                    return {"ok": False,
                            "code": "effect_time_writable_fd_or_unavailable"}
                # Only the already-signed G3+mesh gate may admit this
                # research fixture. The veto check cannot grant permission.
                return super().write(request)
            except (OSError, ValueError, TypeError, RuntimeError, sqlite3.Error,
                    PermissionError):
                return {"ok": False, "code": "rights_evidence_unavailable"}


def revoke_writer(db_path, fence_path):
    """Trusted control-side local hold, serialized against fenced writes.

    This updates ONLY the local writer authority table. It is not remote
    G-Mesh revocation and is not an original-six X3 authorization decision.
    """
    fence = FileFence(fence_path)
    try:
        with fence.exclusive():
            db = sqlite3.connect(db_path, isolation_level=None, timeout=5)
            try:
                db.execute("PRAGMA synchronous=FULL")
                db.execute("BEGIN IMMEDIATE")
                try:
                    result = db.execute(
                        "UPDATE authority SET epoch=epoch+1, halted=1 WHERE id=1")
                    if result.rowcount != 1:
                        raise RuntimeError("missing authority row; deny control")
                    epoch = db.execute(
                        "SELECT epoch FROM authority WHERE id=1").fetchone()[0]
                    db.execute("COMMIT")
                except BaseException:
                    db.execute("ROLLBACK")
                    raise
                return {"ok": True, "code": "local_writer_revoked", "epoch": epoch}
            finally:
                db.close()
    finally:
        fence.close()
