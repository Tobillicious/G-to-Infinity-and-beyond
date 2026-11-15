"""Opt-in G-Mesh lease-gated *empty marker* effect, research fixture only.

The mesh handler and protected G3 gate must live in this one trusted process;
holding mesh.lock through apply_marker serializes LOCAL signed holds with the
marker write. No distributed lock, actual consent or physical X3 proof.
"""
from g_mesh_protocol import GMeshState
from koru_protected_fs_sink import ProtectedFilesystemSink
from koru_shadow import digest


class LeasedFilesystemEffect(ProtectedFilesystemSink):
    requires_mesh_handshake = True

    def __init__(self, gate, directory, *, mesh):
        if not mesh.require_fresh_lease:
            raise ValueError("lease-gated effect requires fail-closed fresh-lease mode")
        if mesh.state != GMeshState.IDLE:
            raise ValueError("mesh must be locally available to initialize")
        super().__init__(gate, directory)
        self.mesh = mesh

    def apply_marker(self, event, *, now, permit, mesh_handshake=None,
                     mesh_signature=None):
        if (type(event) is not dict or type(mesh_handshake) is not dict or
                type(mesh_signature) is not bytes or len(mesh_signature) != 64):
            return {"ok": False, "code": "mesh_envelope_required"}
        # Mesh signed envelope must bind exactly the event that the *existing*
        # G3 Ed25519 permit, synthetic evidence, and marker identity will check.
        if mesh_handshake.get("event_digest") != digest(event):
            return {"ok": False, "code": "mesh_effect_digest_mismatch"}
        # Two independently managed stores: this process lock makes the local
        # check + actual marker effect a single serialized interval wrt
        # calls through THIS mesh instance. Another privileged writer/process
        # can bypass it; production must eliminate those paths.
        with self.mesh.lock:
            valid, reason = self.mesh.process_handshake(
                mesh_handshake, mesh_signature)
            if not valid:
                return {"ok": False, "code": "mesh_" + reason}
            # Existing G3 sink still rechecks its distinct Ed25519 permit,
            # local hold, witnessed context, revocation and journal integrity.
            return super().apply_marker(event, now=now, permit=permit)
