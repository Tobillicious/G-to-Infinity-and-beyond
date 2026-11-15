"""Research integration: PR #456 signed G-Mesh + G3 gate -> bounded local writer.

All three locks are held across the local write. This is a process-local
serialization demonstration, NOT cross-process atomicity or universal X3.
"""
from g3_monitor import Store, sha
from g_mesh_protocol import GMeshState
from koru_ed25519_permit import verify_ed25519
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
                event.get('event_id') != event_id or len(output.encode('utf-8'))>4096):
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
                    # Reject uncommittable local effects BEFORE consuming
                    # a signed mesh sequence or recording a G3 synthetic
                    # dispatch. These local checks are re-run in Store.write.
                    # All participating *in-process* handlers remain locked.
                    inventory = self.inventory()
                    if not inventory['ok']:
                        return inventory
                    if any(i != event_id for i in inventory['pending']):
                        return {'ok':False,'code':'unresolved_previous_effect'}
                    current_epoch, halted = self._authority()
                    if halted or type(request['epoch']) is not int or current_epoch != request['epoch']:
                        return {'ok':False,'code':'stale_or_halted'}
                    prior=self.db.execute(
                        'SELECT digest,epoch FROM effect WHERE id=?',(event_id,)).fetchone()
                    if prior and prior != (self.manifest[event_id],current_epoch):
                        return {'ok':False,'code':'collision'}
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
                    def commit_time_authority():
                        # Called by Store under the same local mutexes just
                        # before publishing (and before reporting completion).
                        # No handshake replay consumption here.
                        try:
                            fresh_now = self.clock()
                            mesh_now = self.mesh.clock()
                            if (type(fresh_now) is not int or
                                    type(mesh_now) is not int or
                                    fresh_now < 0 or fresh_now != mesh_now):
                                return {'ok':False,'code':'clock_unavailable_at_publish'}
                        except (ValueError, TypeError, OverflowError):
                            return {'ok':False,'code':'clock_unavailable_at_publish'}
                        # Preserve the durable high-water mark even on
                        # expiry/denial. Otherwise a trusted-clock rollback
                        # could revive an apparently live controller lease.
                        observed = self.mesh._transaction(
                            lambda: self.mesh._observe_clock_locked(fresh_now))
                        if not observed[0]:
                            return {'ok':False,'code':'mesh_'+observed[1]}
                        if (fresh_now >= packet['not_after'] or
                                not verify_ed25519(
                                    self.gate.ed25519_public_key,
                                    request['permit'], issuer=self.gate.permit_issuer,
                                    event=event, now=fresh_now)):
                            return {'ok':False,'code':'authority_expired_at_publish'}
                        state = self.mesh.db.execute(
                            'SELECT halted,generation FROM gmesh_state WHERE id=1'
                        ).fetchone()
                        lease = self.mesh.db.execute(
                            'SELECT generation,not_after FROM lease_state WHERE id=1'
                        ).fetchone()
                        floor = self.mesh.db.execute(
                            'SELECT last_seen FROM time_floor WHERE id=1'
                        ).fetchone()
                        if (not state or state[0] or
                                state[1] != packet['generation'] or
                                not lease or lease[0] != state[1] or
                                fresh_now >= lease[1] or
                                not floor or fresh_now < floor[0] or
                                self.mesh.db.execute(
                                    'SELECT 1 FROM revoked_authority WHERE ref=?',
                                    (event['authority_ref'],)).fetchone()):
                            return {'ok':False,'code':'mesh_lease_unavailable_at_publish'}
                        current=self.gate.db.execute(
                            'SELECT halted FROM gate_state WHERE id=1'
                        ).fetchone()
                        if (not current or current[0] or
                                self.gate.db.execute(
                                    'SELECT 1 FROM revoked_authorities '
                                    'WHERE authority_ref=?',
                                    (event['authority_ref'],)).fetchone()):
                            return {'ok':False,'code':'g3_authority_held_at_publish'}
                        clock_guard=self.gate.accept_broker_time(fresh_now)
                        if not clock_guard['ok']:
                            return clock_guard
                        return {'ok':True,'code':'locally_current_at_publish'}

                    minimal={k:request[k] for k in ('op','id','html','epoch')}
                    return super().write(minimal,
                        pre_publish=commit_time_authority)
