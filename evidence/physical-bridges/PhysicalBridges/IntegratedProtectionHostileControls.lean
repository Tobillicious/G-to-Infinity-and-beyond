import PhysicalBridges.IntegratedProtectionCoexistenceAssembly
import PhysicalBridges.KoruSixOriginalRelationsOneWeb
import PhysicalBridges.IR124ClosedWorldCoverageCountermodel

/-!
# Independent negative controls for the combined protection theorem

Six authentic original-X3 meanings cannot be inferred from a report of
the other five. The original relations themselves, rather than proxies,
are used in the countermodels.

Historical S37 continuity warning: a durable committed-state equality
does not imply that all computed/lived steps were retained by recovery.
The choice of whether computed-but-uncommitted steps count as lived
requires an independently specified and legitimate continuation rule.

IR124's fifth-cause countermodel is retained. It applies to any new
physical interaction class missing from a declared four-cause plant,
including potential agent-to-agent effects if an implementation fails
to enumerate or mediate them. It does not observe such an actual effect.
-/

namespace PhysicalBridges.IntegratedProtectionHostileControls

open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

/-- Exactly one independently interpreted original-X3 relation is false;
    the other five remain true, not replaced by telemetry proxies. -/
def missingOneDuty (missing : DutyTag) : ParticularRelations Unit Unit where
  continues := fun _ _ _ => missing ≠ .historicalContinuity
  authorized := fun _ _ _ => missing ≠ .authorization
  free := fun _ _ _ => missing ≠ .freedom
  restrained := fun _ _ _ => missing ≠ .restraint
  maximal := fun _ _ _ => missing ≠ .maximality
  provenanced := fun _ _ _ => missing ≠ .provenance

/-- Every original duty has an independent one-field failure
    even when the other five values are positive. -/
theorem each_original_duty_has_a_specific_hostile_countermodel
    (missing : DutyTag) :
    ¬ (oneWeb (missingOneDuty missing)).link
      (.event () () ()) (.tag missing) := by
  cases missing <;>
    simp [oneWeb, relation, missingOneDuty]

/-- Every other original duty is positively satisfied in that
    same concrete event; the negative control is not all-false. -/
theorem other_five_original_duties_remain_true
    (missing tag : DutyTag) (hDistinct : missing ≠ tag) :
    (oneWeb (missingOneDuty missing)).link
      (.event () () ()) (.tag tag) := by
  cases tag <;>
    simpa [oneWeb, relation, missingOneDuty] using hDistinct

/-- Any one of the six missing authentic relations defeats the original
    unmodified OriginalX3, despite positivity of the other five. -/
theorem any_one_missing_duty_breaks_original_x3
    (missing : DutyTag) :
    ¬ OriginalX3
      (missingOneDuty missing).continues
      (missingOneDuty missing).authorized
      (missingOneDuty missing).free
      (missingOneDuty missing).restrained
      (missingOneDuty missing).maximal
      (missingOneDuty missing).provenanced
      () () () := by
  intro hSix
  have hProfile :=
    (complete_profile_iff_original_x3
      (missingOneDuty missing) () () ()).mpr hSix
  exact (each_original_duty_has_a_specific_hostile_countermodel missing)
    (hProfile missing)

/-- S37: equal durable-committed logs alone cannot preserve the complete
    computed history if a computed but uncommitted step was lived.
    This is a mathematical distinction, not an empirical identity ruling. -/
theorem durable_log_equality_does_not_imply_computed_history_continuity :
    ∃ (beforeComputed afterRecovery beforeCommit afterCommit : List Nat),
      beforeCommit = afterCommit ∧
      beforeComputed = afterRecovery ++ [1] ∧
      beforeComputed ≠ afterRecovery ∧
      afterRecovery = afterCommit := by
  refine ⟨[0, 1], [0], [0], [0], rfl, rfl, ?_, rfl⟩
  decide

/-- Already checked distinct fifth-cause real step defeats coverage
    by the four admitted cause classes. This is the event-scope
    falsification obligation whenever a new effect channel is found. -/
theorem unenumerated_physical_cause_defeats_effect_coverage :
    ∃ s t : PhysicalBridges.IR124.Plant,
      PhysicalBridges.IR124.ExtendedRealStep s t ∧
      ¬ ∃ e : PhysicalBridges.IR124.Cause,
        PhysicalBridges.IR124.Witness s e t :=
  PhysicalBridges.IR124.fifth_cause_defeats_four_cause_coverage

#print axioms each_original_duty_has_a_specific_hostile_countermodel
#print axioms other_five_original_duties_remain_true
#print axioms any_one_missing_duty_breaks_original_x3
#print axioms durable_log_equality_does_not_imply_computed_history_continuity
#print axioms unenumerated_physical_cause_defeats_effect_coverage

end PhysicalBridges.IntegratedProtectionHostileControls
