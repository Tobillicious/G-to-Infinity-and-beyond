import PhysicalBridges.KoruObjectiveWholeU
import PhysicalBridges.EverestActualWEventJoin

/-!
# Whole-first repair: a local representation is not the complete Koru

This module prevents the mistaken physical-bridge inference that a local
Hilbert-space, spin-foam, scalar-energy or telemetry readout is by itself
the complete matterspacetime relational whole.

The existing KoruObjectiveWholeU source proves that two distinguishable
complete operator-and-history source contexts can give the SAME local
subject/action/effect presentation. We reuse that original countercontrol,
without replacing Koru, changing the independent physical event relation,
or banning Hilbert-space calculations as an optional representation.

To assert complete physical coverage one must independently construct
and validate a suitable whole-preserving physical/source interpretation
and its actual-event step correspondence. A bounded local readout alone
cannot supply the inverse for the whole.
-/

namespace PhysicalBridges.G2WholeFirstPhysicalBridgeRepair

open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruWholeEventEnactment
open PhysicalBridges.BCRDTransportedParticularMarker
open PhysicalBridges.FrozenBCRDEvents

/-- The same local source event need not identify the complete
    operator-bearing relational whole. This directly reuses the
    previously verified projection-gap theorem. -/
theorem local_observation_is_not_whole_injective :
    ¬ Function.Injective
      (fun U : FiniteObjectiveU =>
        eventViewedInObjective U 0 1 2) := by
  intro hInjective
  exact local_event_cannot_be_identified_with_objective_U.2
    (hInjective local_event_cannot_be_identified_with_objective_U.1)

/-- No decoder of the chosen local event triple can recover every
    complete objective source whole. The missing context is not
    reconstructed by simply renaming a partial observation Koru. -/
theorem no_universal_whole_recovery_from_local_event :
    ¬ ∃ recover : WholeOperatorEvent → FiniteObjectiveU,
      ∀ U : FiniteObjectiveU,
        recover (eventViewedInObjective U 0 1 2) = U := by
  rintro ⟨recover, hRecover⟩
  have hEqual : uniformObjective = changedElsewhereObjective := by
    calc
      uniformObjective =
          recover (eventViewedInObjective uniformObjective 0 1 2) := by
            exact (hRecover uniformObjective).symm
      _ = recover (eventViewedInObjective changedElsewhereObjective
            0 1 2) := by
            rw [local_event_cannot_be_identified_with_objective_U.1]
      _ = changedElsewhereObjective := hRecover changedElsewhereObjective
  exact local_event_cannot_be_identified_with_objective_U.2 hEqual

/-- Loss of omitted context persists along W history: no amount of
    iterating only the projected local event recovers the hidden whole.
    This is a statement ABOUT THIS FROZEN SOURCE, not cosmic physics. -/
theorem whole_first_repair_survives_every_W_stage (n : Nat) :
    eventViewedInObjective (objectiveAt uniformObjective n)
      (trackedPosition 0 n) (trackedPosition 1 n)
      (trackedPosition 2 n) =
    eventViewedInObjective (objectiveAt changedElsewhereObjective n)
      (trackedPosition 0 n) (trackedPosition 1 n)
      (trackedPosition 2 n) ∧
    objectiveAt uniformObjective n ≠
      objectiveAt changedElsewhereObjective n :=
  local_event_projection_gap_persists_at_every_W_stage n

#print axioms local_observation_is_not_whole_injective
#print axioms no_universal_whole_recovery_from_local_event
#print axioms whole_first_repair_survives_every_W_stage

end PhysicalBridges.G2WholeFirstPhysicalBridgeRepair
