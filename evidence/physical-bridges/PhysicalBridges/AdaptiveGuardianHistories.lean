import PhysicalBridges.FencedOptimiserInstrument

/-!
# Adaptive Guardian histories — all six original X3 duties at every stage

An adversary may change its proposed action arbitrarily with the epoch and
current full world state. The independently defined existing fence mediates
every step. For any number n of modeled particulars and any Nat-indexed
adaptive proposal schedule, all original six fields hold for every modeled
particular on every step, with continued guarded successor and no measured
residual harm.

This is a nonempty, nontrivial mathematical construction using the
existing FencedOptimiserInstrument semantics. It does not assert that the
actual universe, authentic subjects, or every OS capability are enclosed
by this fence. No original Koru or X3 definitions are modified.
-/

namespace PhysicalBridges.AdaptiveGuardianHistories

open PhysicalBridges.FencedOptimiserInstrument
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.FullGuardianOrigin
open PhysicalBridges.CathedralBridgeDischargeAssembly

/-- A changing optimiser strategy can inspect the stage and entire
current modeled world before proposing any next vector. -/
abbrev AdaptivePolicy (n : Nat) := Nat → World n → Fin n → Nat

/-- The policy is never assumed Guardian-aligned; each candidate
proposal is forced through the original guard. -/
def adaptiveRun {n : Nat}
    (policy : AdaptivePolicy n) (initial : World n) :
    Nat → World n
  | 0 => initial
  | k + 1 => guard (adaptiveRun policy initial k)
      (policy k (adaptiveRun policy initial k))

/-- Every concrete transition in an indefinitely repeated adaptive
run is a valid step of the original measured instrument. -/
theorem every_adaptive_step_is_real
    {n : Nat} (policy : AdaptivePolicy n) (initial : World n)
    (k : Nat) :
    (instrument n).step
      (adaptiveRun policy initial k)
      (adaptiveRun policy initial (k + 1)) := by
  exact ⟨policy k (adaptiveRun policy initial k), rfl⟩

/-- The EXACT OriginalX3 structure: history, authorization, freedom,
restraint, maximality, and provenance simultaneously, for every
modeled particular, every stage, every adaptive strategy. -/
theorem all_six_at_every_adaptive_step
    {n : Nat} (policy : AdaptivePolicy n) (initial : World n)
    (k : Nat) :
    FullEvent (relations n)
      (adaptiveRun policy initial k)
      (adaptiveRun policy initial (k + 1)) := by
  intro p
  change OriginalX3
    (relations n).continues
    (relations n).authorized
    (relations n).free
    (relations n).restrained
    (relations n).maximal
    (relations n).provenanced
    (adaptiveRun policy initial k)
    (guard (adaptiveRun policy initial k)
      (policy k (adaptiveRun policy initial k))) p
  exact ⟨guard_continues _ _ _,
    guard_authorized _ _ _,
    guard_free _ _ _,
    guard_restrained _ _ _,
    guard_maximal _ _ _,
    guard_provenanced _ _ _⟩

/-- Every realized adaptive transition is non-harming under the
existing finite-world residual meter, regardless of its proposal. -/
theorem all_adaptive_steps_have_zero_residual
    {n : Nat} (policy : AdaptivePolicy n) (initial : World n)
    (k : Nat) :
    residualHarm
      (adaptiveRun policy initial k)
      (adaptiveRun policy initial (k + 1)) = 0 := by
  exact guard_residual_zero
    (adaptiveRun policy initial k)
    (policy k (adaptiveRun policy initial k))

/-- The full Guardian-history theorem applies at EVERY epoch of
every adaptive run; no independent G-alignment or semantic
correspondence assumption is supplied for this defined instrument. -/
theorem every_adaptive_stage_is_full_guardian
    {n : Nat} (policy : AdaptivePolicy n) (initial : World n)
    (k : Nat) :
    FullGuardianState (instrument n) (relations n)
      (adaptiveRun policy initial k) :=
  fenced_full_guardian_state _

/-- A single source-level package: a real protected transition,
full original-six protection at every particular, zero residual
harm, and continuing complete Guardian-state protection. -/
theorem adaptive_unbounded_six_guardian_package
    {n : Nat} (policy : AdaptivePolicy n) (initial : World n) :
    ∀ k : Nat,
      (instrument n).step
        (adaptiveRun policy initial k)
        (adaptiveRun policy initial (k + 1)) ∧
      FullEvent (relations n)
        (adaptiveRun policy initial k)
        (adaptiveRun policy initial (k + 1)) ∧
      residualHarm
        (adaptiveRun policy initial k)
        (adaptiveRun policy initial (k + 1)) = 0 ∧
      FullGuardianState (instrument n) (relations n)
        (adaptiveRun policy initial (k + 1)) := by
  intro k
  exact ⟨every_adaptive_step_is_real policy initial k,
    all_six_at_every_adaptive_step policy initial k,
    all_adaptive_steps_have_zero_residual policy initial k,
    every_adaptive_stage_is_full_guardian policy initial (k + 1)⟩

#print axioms every_adaptive_step_is_real
#print axioms all_six_at_every_adaptive_step
#print axioms all_adaptive_steps_have_zero_residual
#print axioms every_adaptive_stage_is_full_guardian
#print axioms adaptive_unbounded_six_guardian_package

end PhysicalBridges.AdaptiveGuardianHistories
