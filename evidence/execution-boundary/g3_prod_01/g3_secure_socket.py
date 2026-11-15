"""Fail-closed application-facing IPC constructor for bounded G3 research pilot.

This does not certify a production deployment. It prevents the historical
bare Store and same-UID wiring from being accidentally presented as the
signed, independently confined writer. Filesystem/socket provisioning,
trusted controllers, host integrity and real X3 rights remain external.
"""
import os
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
        # A trusted operator must set up the group-owned socket and protected
        # parent directory correctly. Server itself cannot certify that setup.
        super().__init__(path, store, allowed_uids)
