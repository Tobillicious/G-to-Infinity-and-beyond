import PhysicalBridges.G2FirstActualDutyMismatch

/-!
# Two last-mile gates: concrete event-level failure witnesses

We already know from PhysicalSemanticLastMileGates that an actual original-six
violation refutes either complete physical W-event coverage or authentic
forward reflection. This module extracts useful witnesses:
* a concrete independently actual physical edge missing one of the four
  required coverage clauses (model edge, before/after W-readout, stage order);
* OR, with coverage established, the SAME physical edge, owed particular,
  and exact original-six tag with source truth and absent subject truth.

No declaration changes actual physical events, Koru, the six X3 duties,
or the positive W source. The witnesses are conditional on a supplied
violation; they do not claim an observed harm or an empirical oracle.
-/

namespace PhysicalBridges.G2LastMileWitnessAudit

open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruWholeUSixDutyWebJoin
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.OriginalKeystonePositiveWholeTest
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.EverestActualWEventJoin
open PhysicalBridges.G2FirstActualDutyMismatch

/-- A named, independently testable coverage failure on one actual event.
    The W readouts and step order must be authentic, not synthesized from
    controller claims. -/
def CoverageFailureAt {S : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU) (stage : S → Nat)
    (s t : S) : Prop :=
  physicalStep s t ∧
  (¬ modeledStep s t ∨
   source s ≠ objectiveAt positiveWholeU (stage s) ∨
   source t ≠ objectiveAt positiveWholeU (stage t) ∨
   stage t ≠ stage s + 1)

/-- The negation of complete W coverage exposes a concrete real edge and
    one specific failed source-boundary clause, rather than a generic
    'coverage missing' label. -/
theorem failed_complete_coverage_has_actual_counterexample
    {S : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU) (stage : S → Nat)
    (hNotCoverage : ¬ CompleteWEventCoverage physicalStep modeledStep
      source stage positiveWholeU) :
    ∃ s t, CoverageFailureAt physicalStep modeledStep source stage s t := by
  classical
  unfold CompleteWEventCoverage at hNotCoverage
  have ⟨s, hS⟩ := Classical.not_forall.mp hNotCoverage
  have ⟨t, hT⟩ := Classical.not_forall.mp hS
  have hActual : physicalStep s t := by
    by_cases hYes : physicalStep s t
    · exact hYes
    · have hImpossible :
          physicalStep s t →
            modeledStep s t ∧
            source s = objectiveAt positiveWholeU (stage s) ∧
            source t = objectiveAt positiveWholeU (stage t) ∧
            stage t = stage s + 1 := by
        intro hStep
        exact False.elim (hYes hStep)
      exact False.elim (hT hImpossible)
  have hNotJoin :
      ¬ (modeledStep s t ∧
        source s = objectiveAt positiveWholeU (stage s) ∧
        source t = objectiveAt positiveWholeU (stage t) ∧
        stage t = stage s + 1) := by
    intro hJoin
    exact hT (fun _ => hJoin)
  refine ⟨s, t, hActual, ?_⟩
  by_cases hm : modeledStep s t
  · by_cases hb : source s = objectiveAt positiveWholeU (stage s)
    · by_cases ha : source t = objectiveAt positiveWholeU (stage t)
      · right; right; right
        intro hn
        exact hNotJoin ⟨hm, hb, ha, hn⟩
      · exact Or.inr (Or.inr (Or.inl ha))
    · exact Or.inr (Or.inl hb)
  · exact Or.inl hm

/-- Complete first-violation audit: either a W coverage failure
    is exposed on an ACTUAL edge, or the violating original-six
    particular and exact source/subject mismatch can be named. -/
theorem original_six_violation_yields_concrete_last_mile_witness
    {S P : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU) (stage : S → Nat)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop)
    (s t : S) (hPhysical : physicalStep s t)
    (p : P) (hOwed : owed p)
    (hViolation : ¬ OriginalX3 r.continues r.authorized
      r.free r.restrained r.maximal r.provenanced s t p) :
    (∃ u v, CoverageFailureAt
      physicalStep modeledStep source stage u v) ∨
    (modeledStep s t ∧
      ∃ tag : DutyTag,
        wholeSourceDutyAt positiveWholeU sixDiagonalRoles
          (stage s) (carrier p) tag ∧
        ¬ (oneWeb r).link (.event s t p) (.tag tag)) := by
  classical
  by_cases hCoverage : CompleteWEventCoverage
      physicalStep modeledStep source stage positiveWholeU
  · exact Or.inr
      (actual_violation_with_coverage_exposes_specific_tag
        physicalStep modeledStep source stage carrier r owed
        hCoverage s t hPhysical p hOwed hViolation)
  · exact Or.inl
      (failed_complete_coverage_has_actual_counterexample
        physicalStep modeledStep source stage hCoverage)

#print axioms failed_complete_coverage_has_actual_counterexample
#print axioms original_six_violation_yields_concrete_last_mile_witness

end PhysicalBridges.G2LastMileWitnessAudit
