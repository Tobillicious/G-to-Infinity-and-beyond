"""Research integration: PR #456 signed G-Mesh + G3 gate -> bounded local writer.

All three locks are held across the local write. This is a process-local
serialization demonstration, NOT cross-process atomicity or universal X3.
"""
from g3_monitor import Store, sha
from g_mesh_protocol import GMeshState
from koru_shadow import digest

class SignedG3Writer(Store):
    def __init__(self, path, output_dir, *, gate, mesh, manifest, clock):
        # The manifest is a trusted controller configuration, never from IPC.
        if not mesh.require_fresh_lease or mesh.state != GMeshState.IDLE:
            raise ValueError("fresh lease-enabled, locally available mesh required")
        if not callable(clock) or type(manifest) is not dict:
            raise ValueError("trusted clock and fixed manifest required")
        if any(type(k) is not str or type(v) is not str or len(v)!=64 or
               any(c not in '0123456789abcdef' for c in v)
               for k,v in manifest.items()):
            raise ValueError("invalid trusted content manifest")
        if not hasattr(gate,'dispatch_synthetic'):
            raise ValueError("G3 protected gate required")
        super().__init__(path, output_dir)
        self.gate=gate
        self.mesh=mesh
        self.manifest=dict(manifest)
        self.clock=clock

    def write(self, request):
        if type(request) is not dict or set(request) != {
                'op','id','html','epoch','event','permit',
                'mesh_handshake','mesh_signature'} or request.get('op')!='write':
            return {'ok':False,'code':'signed_envelope_required'}
        event=request['event']
        packet=request['mesh_handshake']
        signature=request['mesh_signature']
        if (type(event) is not dict or type(packet) is not dict or
                type(signature) is not str or len(signature)!=128 or
                any(c not in '0123456789abcdef' for c in signature)):
            return {'ok':False,'code':'bad_signed_envelope'}
        event_id=request['id']
        output=request['html']
        if (type(event_id) is not str or type(output) is not str or
                event.get('event_id') != event_id):
            return {'ok':False,'code':'event_id_mismatch'}
        if self.manifest.get(event_id) != sha(output.encode('utf-8')):
            return {'ok':False,'code':'untrusted_output_bytes'}
        if (packet.get('event_digest')!=digest(event) or
                packet.get('authority_ref')!=event.get('authority_ref')):
            return {'ok':False,'code':'mesh_event_mismatch'}
        try:
            now=self.clock()
            if type(now) is not int or now<0:
                return {'ok':False,'code':'clock_unavailable'}
        except (TypeError, ValueError, OverflowError):
            return {'ok':False,'code':'clock_unavailable'}
        # mesh and gate locks synchronize holds performed through these EXACT
        # in-process handlers. Separate processes need an enforceable fence.
        with self.mesh.lock:
            with self.gate.lock:
                with self.lock:
                    clock_floor=self.gate.accept_broker_time(now)
                    if not clock_floor['ok']:
                        return clock_floor
                    ok,why=self.mesh.process_handshake(packet,bytes.fromhex(signature))
                    if not ok:
                        return {'ok':False,'code':'mesh_'+why}
                    grant=self.gate.dispatch_synthetic(
                        event,now=now,permit=request['permit'])
                    if not grant['ok']:
                        return grant
                    # Still a separate SQLite transaction from the G3 gate.
                    # Failure is never promoted into physical authorization.
                    minimal={k:request[k] for k in ('op','id','html','epoch')}
                    return super().write(minimal)
