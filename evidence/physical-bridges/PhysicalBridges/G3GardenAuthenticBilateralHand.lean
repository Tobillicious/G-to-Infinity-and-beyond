import PhysicalBridges.HumeHillaryReciprocalHand

/-!
# Garden: bilateral Hume–Hillary hand with unchanged original six

Additive pre-QG research draft (20 November 2026).
The existing Hume–Hillary theorem certifies an authentic offered hand and
the original six for p under explicit source/subject correspondence premises.
This draft proves the same six for the second owed participant q, using the
already established whole-source six equivalences. It does not equate a
reciprocal physical edge with consent.

REVIEW STATUS: not independently Lean-kernel-checked. This file is deliberately
not added to the build root until its import and proof checks are replayed.
No original X3 definitions and no GoodConquersEvil/no_pruning statements change.
-/

namespace PhysicalBridges.G3GardenAuthenticBilateralHand

open PhysicalBridges.HumeHillaryReciprocalHand
open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.BCRDTransportedParticularMarker
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruWholeUDirectedAgency
open PhysicalBridges.KoruWholeUSixDutyWebJoin
open PhysicalBridges.KoruWholeUSubjectSixJoin
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.Koru

/-- A bilateral Garden certificate: the offer and acceptance of two
distinct owed participants are separately authenticated, and both subjects
receive the unchanged original six under independent fidelity and six-origin
hypotheses. The hSourceHand premise is source reciprocity, NOT consent. -/
theorem authentic_bilateral_hand_protects_both
    {P : Type}
    (U : FiniteObjectiveU) (roles : SourceDutyRoles)
    (carrier : P → Index) (r : ParticularRelations Nat P)
    (offer accept : P → P → Prop)
    (owed : P → Prop) (p q : P) (n : Nat)
    (_hp : owed p) (_hq : owed q)
    (hSourceHand : SourceMutualHand U (carrier p) (carrier q))
    (hForwardMeaning :
      (sourceWholeWeb (objectiveAt U n)).link
        (trackedPosition (carrier p) n)
        (trackedPosition (carrier q) n) ↔ offer p q)
    (hReturnMeaning :
      (sourceWholeWeb (objectiveAt U n)).link
        (trackedPosition (carrier q) n)
        (trackedPosition (carrier p) n) ↔ accept q p)
    (hSubjectFidelity : WholeUSubjectFidelity U roles carrier r)
    (hSixOriginP : wholeSourceSixAt U roles 0 (carrier p))
    (hSixOriginQ : wholeSourceSixAt U roles 0 (carrier q)) :
    p ≠ q ∧
    AuthenticMutualHand offer accept p q ∧
    SubjectOriginalSixAt r n p ∧
    SubjectOriginalSixAt r n q := by
  have hFirst := authentic_offered_hand_and_original_six_from_faithful_source
    U roles carrier r offer accept p q n hSourceHand
    hForwardMeaning hReturnMeaning hSubjectFidelity hSixOriginP
  have hSecond : SubjectOriginalSixAt r n q :=
    (faithful_subject_six_iff_one_whole_U_six
      U roles carrier r hSubjectFidelity n q).mpr
        ((one_objective_whole_six_source_truth_iff_origin
          U roles (carrier q) n).mpr hSixOriginQ)
  refine ⟨?_, hFirst.1, hFirst.2, hSecond⟩
  exact hFirst.1.1

/-- A genuinely mutual physical source does NOT itself imply subject
authorization. This imports the existing hostile test unchanged. -/
theorem bilateral_source_hand_is_not_enough :
    SourceMutualHand twoHandWhole 0 1 ∧
    ¬ SubjectOriginalSixAt hostileSubjectMeanings 0 (0 : Index) :=
  reciprocal_physical_hand_alone_does_not_force_consent

#print axioms authentic_bilateral_hand_protects_both
#print axioms bilateral_source_hand_is_not_enough

end PhysicalBridges.G3GardenAuthenticBilateralHand
