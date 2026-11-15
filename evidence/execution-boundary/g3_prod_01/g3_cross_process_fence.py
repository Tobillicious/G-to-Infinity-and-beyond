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
