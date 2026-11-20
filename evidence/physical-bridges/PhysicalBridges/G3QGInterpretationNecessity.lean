import PhysicalBridges.G3SixDutyRenewal
import PhysicalBridges.G3ActualOnlyReflection

/-!
# G3 backwards: semantic non-identifiability of physics-only QG laws

Find-before-build: IR-125 and the original Hume-Hillary controls already
show that source observables, mutual links and an event journal do not
automatically establish genuine consent or the other subject meanings.

This module proves the full generality of the obstruction:

Any proposed QG law which depends ONLY on a physical transition
relation, its whole-W source and time-stage representation cannot entail
the unchanged six-X3 duties for ALL independent interpretations of the
subjects. The same nonempty, total, whole-W-covered physics admits both
an interpretation satisfying all six on actual steps and one denying
authorization on those very same steps.

This is NOT a claim that actual physics is unethical. Rather, a physical
QG law sufficient for G3 must fix, with independently justified content,
how particular-level semantics are recovered from physical events.
Simply naming all-six reflection a QG field would conceal the gap.

No existing theorem, definition, OriginalX3 duty, Koru or GoodConquersEvil
source is changed. The counterexample reuses the existing positiveWholeU.
-/

namespace PhysicalBridges.G3QGInterpretationNecessity

open PhysicalBridges.G3ActualOnlyReflection
open PhysicalBridges.OriginalKeystonePositiveWholeTest
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.EverestActualWEventJoin
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.FrozenBCRDEvents

/-- This QG candidate interface is deliberately physics-only.
It mentions transitions, source states, and physical stage, not
subject-level predicates or authentic interpretations. -/
abbrev PhysicsOnlyLaw :=
  (Nat → Nat → Prop) → (Nat → FiniteObjectiveU) → (Nat → Nat) → Prop

def canonicalPhysicalSource (n : Nat) : FiniteObjectiveU :=
  objectiveAt positiveWholeU n

/-- A source-faithful populated physical model, independent of any
    evaluation of subjects. -/
theorem canonical_physics_has_W_coverage :
    CompleteWEventCoverage realSuccessor realSuccessor
      canonicalPhysicalSource (fun n => n) positiveWholeU := by
  intro s t h
  exact ⟨h, rfl, rfl, h⟩

/-- Every physical state has a genuine next physical transition. -/
theorem canonical_physics_is_nonterminal :
    ∀ s : Nat, ∃ t, realSuccessor s t := by
  intro s
  exact ⟨s + 1, rfl⟩

/-- A benign interpretation can validate each of the exact original
    six duty predicates for every actual transition. -/
def validatingSubjects : ParticularRelations Nat Unit where
  continues := fun s t _ => realSuccessor s t
  authorized := fun s t _ => realSuccessor s t
  free := fun s t _ => realSuccessor s t
  restrained := fun s t _ => realSuccessor s t
  maximal := fun s t _ => realSuccessor s t
  provenanced := fun s t _ => realSuccessor s t

/-- A different independent subject interpretation with precisely
    the same physical transitions and source data, but with false
    authorization even on a real enacted event. -/
def withholdingSubjects : ParticularRelations Nat Unit where
  continues := fun s t _ => realSuccessor s t
  authorized := fun _ _ _ => False
  free := fun s t _ => realSuccessor s t
  restrained := fun s t _ => realSuccessor s t
  maximal := fun s t _ => realSuccessor s t
  provenanced := fun s t _ => realSuccessor s t

/-- All six really hold on actual steps under the validating
    interpretation. No vacuity: the physical relation has successors. -/
theorem validating_subjects_have_all_original_six :
    ∀ s t, realSuccessor s t →
      OriginalX3 validatingSubjects.continues
        validatingSubjects.authorized validatingSubjects.free
        validatingSubjects.restrained validatingSubjects.maximal
        validatingSubjects.provenanced s t () := by
  intro s t h
  exact ⟨h, h, h, h, h, h⟩

/-- But the same actual physical step fails authentic authorization in
    the withholding interpretation, while the other five fields still
    describe that physical step. -/
theorem withholding_subjects_fail_six_on_an_actual_event :
    ¬ (∀ s t, realSuccessor s t →
      OriginalX3 withholdingSubjects.continues
        withholdingSubjects.authorized withholdingSubjects.free
        withholdingSubjects.restrained withholdingSubjects.maximal
        withholdingSubjects.provenanced s t ()) := by
  intro h
  have hs := h 0 1 rfl
  exact hs.authorization

/-- Both subject interpretations share exactly the same independently
    populated and W-complete physical data, but disagree on the six.
    Coverage and nontermination do not settle this semantic difference. -/
theorem identical_complete_physics_permits_opposite_subject_readings :
    CompleteWEventCoverage realSuccessor realSuccessor
      canonicalPhysicalSource (fun n => n) positiveWholeU ∧
    (∀ s : Nat, ∃ t, realSuccessor s t) ∧
    (∀ s t, realSuccessor s t →
      OriginalX3 validatingSubjects.continues
        validatingSubjects.authorized validatingSubjects.free
        validatingSubjects.restrained validatingSubjects.maximal
        validatingSubjects.provenanced s t ()) ∧
    ¬ (∀ s t, realSuccessor s t →
      OriginalX3 withholdingSubjects.continues
        withholdingSubjects.authorized withholdingSubjects.free
        withholdingSubjects.restrained withholdingSubjects.maximal
        withholdingSubjects.provenanced s t ()) :=
  ⟨canonical_physics_has_W_coverage, canonical_physics_is_nonterminal,
    validating_subjects_have_all_original_six,
    withholding_subjects_fail_six_on_an_actual_event⟩

/-- PARAMETRIC NO-GO: for *any* independently stated QG predicate of
    physical transition data only, if it holds of this populated
    source-faithful model then it cannot imply full original-six for
    every unconstrained subject interpretation. A semantic uniqueness or
    physically grounded subject-interpretation theorem is necessary. -/
theorem no_physics_only_QG_implies_six_for_arbitrary_subject_meanings
    (QG : PhysicsOnlyLaw)
    (hQG : QG realSuccessor canonicalPhysicalSource (fun n => n)) :
    ¬ (QG realSuccessor canonicalPhysicalSource (fun n => n) →
      ∀ r : ParticularRelations Nat Unit,
        ∀ s t, realSuccessor s t →
          OriginalX3 r.continues r.authorized r.free
            r.restrained r.maximal r.provenanced s t ()) := by
  intro hUniversal
  have hAll := hUniversal hQG withholdingSubjects
  exact withholding_subjects_fail_six_on_an_actual_event hAll

/-- A useful target for genuine QG: if physically indistinguishable
    subject interpretations are to have uniquely determined ethics,
    they cannot disagree on an authentic duty at any realized event.
    The current model supplies an exact authorization disagreement. -/
theorem canonical_source_does_not_determine_authorization :
    (∃ s t : Nat, realSuccessor s t ∧
      validatingSubjects.authorized s t () ∧
      ¬ withholdingSubjects.authorized s t ()) := by
  exact ⟨0, 1, rfl, rfl, fun h => h⟩

#print axioms canonical_physics_has_W_coverage
#print axioms canonical_physics_is_nonterminal
#print axioms validating_subjects_have_all_original_six
#print axioms withholding_subjects_fail_six_on_an_actual_event
#print axioms identical_complete_physics_permits_opposite_subject_readings
#print axioms no_physics_only_QG_implies_six_for_arbitrary_subject_meanings
#print axioms canonical_source_does_not_determine_authorization

end PhysicalBridges.G3QGInterpretationNecessity
