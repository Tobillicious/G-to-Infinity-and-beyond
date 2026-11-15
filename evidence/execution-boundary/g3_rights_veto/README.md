# Durable rights withdrawal veto — offline research component

This is a small deny-only, persistent local journal to complement the separate research lanes in PR #472 (signed provenance claim) and PR #473 (subject-specific record triage). It does **not** connect to any G3 writer, offer consent, or grant effect authority.

## Intended guarantee under its limited single-controller threat model

- A trusted controller can record an irreversible local withdrawal of a particular record reference, subject, action and exact effect digest.
- Withdrawals and an increasing generation counter are durably written in one SQLite transaction with WAL and synchronous FULL.
- On restart the control state is explicitly halted, and withdrawn references remain denied.
- Requests bearing stale generation information are denied. An unknown record or a missing withdrawal never gives authorization.
- Journal directory and file must be private to the owning user; symlink DB paths are refused.

## Do not treat as a live rights authority

The trusted controller method is deliberately an in-process API; **no public socket, arm operation, allow operation or application permit exists**. This library cannot validate a person's identity, capacity, voluntariness, representation, consent, provenance or the original six X3 duties. If an attacker can edit/delete/rollback SQLite state or its WAL, compromise the controller identity, or run another instance with the same DB unsafely, the protection model fails. The journal's observed generation is not a remote revocation consistency proof.

All query responses carry `authorizes_effect: false`, `authentic_consent_proved: false` and `original_six_x3_proved: false`. A result of `no_local_withdrawal_found_not_authorized` must **never** be converted into allow. The journal is a *veto evidence component*, not a permission gate.

Additional required work: authenticated controller source, atomic integration with effect commit and revocation ordering, rollback-resistant persistent generation, independent audit, complete application-specific rights/consent rules, and real-world six-X3 correspondence. Do not deploy this component as an authority or infer universal physical G3.

Run offline negative controls:

```sh
cd evidence/execution-boundary/g3_rights_veto
python3 -B -m unittest -v test_rights_veto.py
```
