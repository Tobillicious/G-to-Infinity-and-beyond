"""Fail-closed application-facing IPC constructor for bounded G3 research pilot.

This does not certify a production deployment. It prevents the historical
bare Store and same-UID wiring from being accidentally presented as the
signed, independently confined writer. Filesystem/socket provisioning,
trusted controllers, host integrity and real X3 rights remain external.
"""
import os
import stat
from pathlib import Path
from g3_monitor import Server
from g3_cross_process_fence import FencedSignedG3Writer


class SignedFencedServer(Server):
    def __init__(self, path, store, allowed_uids):
        if not isinstance(store, FencedSignedG3Writer):
            raise TypeError("signed and cross-process-fenced writer required")
        if (not isinstance(allowed_uids, (set, frozenset)) or
                not allowed_uids or
                any(type(uid) is not int or uid <= 0 or
                    uid == os.geteuid() for uid in allowed_uids)):
            raise ValueError("explicit non-root clients with UID separate from writer required")
        if not store.mesh.require_fresh_lease:
            raise ValueError("fresh controller lease required")
        # The socket path is a security boundary. Never bind below a
        # guest-writable or attacker-owned directory (e.g. shared /tmp).
        # A trusted operator still has to provision group ownership and
        # additional host policy; this check is only a local prerequisite.
        if type(path) is not str or not os.path.isabs(path):
            raise ValueError("socket path must be absolute")
        socket_path = Path(path)
        if socket_path.name in ('', '.', '..'):
            raise ValueError("invalid socket basename")
        parent_fd = os.open(str(socket_path.parent),
                            os.O_RDONLY | os.O_DIRECTORY |
                            os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            parent = os.fstat(parent_fd)
            if (not stat.S_ISDIR(parent.st_mode) or
                    parent.st_uid != os.geteuid() or
                    parent.st_mode & 0o022):
                raise PermissionError("socket parent must be trusted-owned and not group/world writable")
            try:
                os.stat(socket_path.name, dir_fd=parent_fd,
                        follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise FileExistsError("refusing pre-existing socket pathname")
        finally:
            os.close(parent_fd)
        super().__init__(path, store, allowed_uids)
