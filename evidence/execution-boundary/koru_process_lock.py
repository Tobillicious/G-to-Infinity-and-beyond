"""Opt-in Linux/POSIX interprocess, reentrant effect/control fence.

Research pilot only: cooperating broker/controller processes must use the SAME
lock file and must not have alternate effect capabilities. This is advisory
flock, not an OS sandbox, authenticated administration or a proof that no
privileged path bypasses the contract.
"""
import fcntl
import os
import stat
import threading


class InterprocessRLock:
    """Thread-reentrant exclusive advisory flock over a trusted 0600 inode.

    One open file descriptor per process. Never pass an open descriptor from
    parent to a forked child; initialize a fresh gate/lock in each process.
    """

    def __init__(self, path):
        if not isinstance(path, str) or not path:
            raise ValueError("trusted lock file path is required")
        self._local = threading.RLock()
        self._depth = 0
        flags = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW
        flags |= getattr(os, "O_CLOEXEC", 0)
        fd = os.open(path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                    info.st_uid != os.geteuid() or info.st_mode & 0o077):
                raise PermissionError("lock inode must be trusted and private")
        except BaseException:
            os.close(fd)
            raise
        self._fd = fd
        self._closed = False

    def __enter__(self):
        self._local.acquire()
        try:
            if self._closed:
                raise RuntimeError("closed interprocess lock")
            if self._depth == 0:
                fcntl.flock(self._fd, fcntl.LOCK_EX)
            self._depth += 1
            return self
        except BaseException:
            self._local.release()
            raise

    def __exit__(self, *_):
        try:
            self._depth -= 1
            if self._depth == 0:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            self._local.release()

    def close(self):
        with self._local:
            if self._depth != 0:
                raise RuntimeError("cannot close acquired interprocess lock")
            if not self._closed:
                os.close(self._fd)
                self._closed = True
