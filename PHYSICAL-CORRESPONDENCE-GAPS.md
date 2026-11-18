# Physical Correspondence Gaps (PR #657 / G3 Node)

This document records the gap between machine-checked formal results and physical-world guarantees.

## Conditional Status

- Lean 4 proof tree: valid only under accepted axioms and exact arithmetic without hardware corruption.
- G3 node horizon protection: conditional on hardware isolation, bounded latency, and no side-channel interference.
- Escrowed lottery alignment: conditional on honest participation and non-collusion.

## Known Gaps

1. Thermodynamic gap: exact arithmetic proofs do not cover continuous hardware faults, timing side-channels, or cache attacks.
2. Network gap: no formal mapping from abstract state transitions to jitter, Byzantine drops, or clock drift.
3. Agency gap: local avoidance definitions do not yet cover coupled multi-agent resource starvation.
4. Physical correspondence: source-to-world mapping for G1/G2/G3 remains explicit construction work.

## Adversarial Tests Needed

- Asynchronous state-drift injection (15-50ms jitter across 40% of links).
- Cross-node implicit predation via resource exhaustion.
- Side-channel perturbation of G3 node state before hash flush.

## Status

These gaps are tracked, not resolved. Conditional results must be labeled conditional.
