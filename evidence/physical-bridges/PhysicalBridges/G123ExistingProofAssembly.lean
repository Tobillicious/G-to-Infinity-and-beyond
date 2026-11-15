import PhysicalBridges.FencedOptimiserInstrument
import PhysicalBridges.ConstructivePositiveWGuardian
import PhysicalBridges.FullPhysicalDomainGuardianAssembly

/-!
# G1–G2–G3: assembly without reconstructing X3

15 November 2026. This is a source-preserving join of existing proofs, NOT a
new definition of X3, a new physical postulate, or a claim that the actual
universe is already covered by the synthetic instrument.

The constructed finite-fence model has:
* G1-type safety: every event carries the entire original-six FullEvent.
* G2-type freedom: the same FullEvent includes freedom, authorization and
  least-necessary restraint, not merely continued existence.
* G3-type continuation: every reachable state has a further protected step,
  and the existing full HistoryGuardian capstone applies.

The original source's distinct G3 wavefront-recovery/work theorem remains
Snuffy.G3Sweep.sweep_bill; it is not conflated with this guardian continuation.

For arbitrary physical events the separate coverage and authentic-forward-
reflection premises of FullPhysicalDomainGuardianAssembly remain in force.
-/

namespace PhysicalBridges.G123ExistingProofAssembly

open PhysicalBridges.FencedOptimiserInstrument
open PhysicalBridges.FullGuardianOrigin
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.CathedralGuardianOnlyCapstone
open PhysicalBridges.AllIsGActualityDischarge

/-- An explicitly constructed G1/G2/G3 guardian lane: all original-six duties
on every reachable event, an actual protected successor at every reachable
state, and the source/history capstone. There is no correspondence or G
hypothesis for THIS fenced mathematical world. -/
theorem fenced_g1_g2_g3_join {n : Nat} (s : World n) :
    FullGuardianState (instrument n) (relations n) s ∧
    RouteBSummit (canonicalInstrument (instrument n) (relations n)) ∧
    HistoryGuardian
      (toSource (canonicalInstrument (instrument n) (relations n))) s := by
  exact ⟨fenced_full_guardian_state s, fenced_route_b n, fenced_capstone s⟩

/-- The unfenced adversary is genuinely counterexample-producing; the fence
blocks the specific destructive proposal while keeping the six-duty join. -/
theorem adversarial_proposal_is_fenced_and_guarded :
    residualHarm demo (unfenced demo endAll) = 1 ∧
    residualHarm demo (guard demo endAll) = 0 ∧
    FullGuardianState (instrument 1) (relations 1) demo := by
  exact ⟨fence_is_load_bearing.2.2.1,
    fence_is_load_bearing.2.2.2.2.2,
    fenced_full_guardian_state demo⟩

#print axioms fenced_g1_g2_g3_join
#print axioms adversarial_proposal_is_fenced_and_guarded

end PhysicalBridges.G123ExistingProofAssembly
