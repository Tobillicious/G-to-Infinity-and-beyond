import PhysicalBridges.KoruSubjectFidelityLift

/-!
# G3: exact all-owed duty mismatch closure

Find-before-build assembly of `original_violation_iff_exact_source_subject_mismatch`.
The source operator duties must be independently positive for owed particulars.
Then all original-six subject duties hold at all modeled W stages exactly when
there is no true-source/false-subject mismatch at any such stage.

No redefinitions, placeholder proofs, new axioms, physical-event assumptions, or
representations of actual matterspacetime are introduced.

This is a W-source/subject correspondence result, NOT unconditional G3.
-/

/- Drafted by GPT (20 Nov 2026). Repaired by Claude to compile without Mathlib:
   `by_contra` replaced by `Classical.byContradiction`. -/

namespace PhysicalBridges.G3ExactMismatchClosure

open PhysicalBridges.KoruSubjectFidelityLift
open PhysicalBridges.KoruOperatorIndexedSubjectSemantics
open PhysicalBridges.BCRDTransportedParticularMarker
open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.OriginalX3Full

variable {P : Type}

/-- Exact all-owed mathematical gate; neither side is built into the
source definition. Each failing duty has a named mismatch witness. -/
theorem all_owed_X3_iff_no_source_subject_mismatch
    (r : ParticularRelations Nat P)
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (owed : P → Prop)
    (hOrigin : ∀ p, owed p → SixSourceTruth 0 d (roles (carrier p))) :
    (∀ n p, owed p →
       OriginalX3 r.continues r.authorized r.free
         r.restrained r.maximal r.provenanced n (n + 1) p) ↔
    (∀ n p, owed p →
       ¬ SourceSubjectMismatch r d roles carrier n p) := by
  constructor
  · intro hGood n p hp hMismatch
    have hBad :=
      (original_violation_iff_exact_source_subject_mismatch
        r d roles carrier p n (hOrigin p hp)).mpr hMismatch
    exact hBad (hGood n p hp)
  · intro hNoMismatch n p hp
    apply Classical.byContradiction
    intro hBad
    have hMismatch :=
      (original_violation_iff_exact_source_subject_mismatch
        r d roles carrier p n (hOrigin p hp)).mp hBad
    exact (hNoMismatch n p hp) hMismatch

/-- A counterexample to all-owed protection yields one particular,
one stage and one ORIGINAL six-duty tag where correspondence fails. -/
theorem failed_all_owed_X3_has_exact_tag
    (r : ParticularRelations Nat P)
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (owed : P → Prop)
    (hOrigin : ∀ p, owed p → SixSourceTruth 0 d (roles (carrier p)))
    (n : Nat) (p : P) (hp : owed p)
    (hViolation : ¬ OriginalX3 r.continues r.authorized
       r.free r.restrained r.maximal r.provenanced n (n + 1) p) :
    ∃ tag : DutyTag,
      completeOperatorSourceEdge d roles carrier n p tag ∧
      ¬ subjectEdge r n p tag := by
  exact (original_violation_iff_exact_source_subject_mismatch
    r d roles carrier p n (hOrigin p hp)).mp hViolation

#print axioms all_owed_X3_iff_no_source_subject_mismatch
#print axioms failed_all_owed_X3_has_exact_tag

end PhysicalBridges.G3ExactMismatchClosure
