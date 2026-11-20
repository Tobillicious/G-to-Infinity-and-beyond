import PhysicalBridges.G3BoundedGuardianDischarge
import PhysicalBridges.HumeHillaryReciprocalHand
import PhysicalBridges.KoruOperatorHistoryProvenance

/-!
# The Six-Witness Bridge: Hume-Hillary, Complete Koru, Four Causes

Find-before-build:
* `ExternalJointEffectRefinement.AuthenticSixReflections` already names
  the six independent authentic model-to-subject obligations.
* `G3BoundedGuardianDischarge.FaithfulRead` already assembles these
  six implications, but does not produce their external witnesses.
* `FourCausePhysicalGuardianBridge.four_causes_derive_complete_joint_coverage`
  already covers exactly the four constructors of IR124.Plant.
* `HumeHillaryReciprocalHand` supplies a two-way source hand AND a
  hostile example showing that reciprocity alone does not imply consent.
* `KoruOperatorHistoryProvenance` proves that terminal state alone
  does not determine event history.

This file adds only a separately typed EVIDENCE interface: each modeled
duty must yield a named observation about the specific actual event, and
that observation must be *independently validated* as supporting its
corresponding unchanged actual duty. The evidence and actual predicates
are not DEFINED from the model or from one another.

The critical external validation premises are not derived by Lean here.
They are independently testable obligations for a real confined system.
No global coverage, authentic consent, QG or cosmological G3 is claimed.
-/

namespace PhysicalBridges.G3SixWitnessPhysicalFidelity

open PhysicalBridges.G3BoundedGuardianDischarge
open PhysicalBridges.FourCausePhysicalGuardianBridge
open PhysicalBridges.ExternalJointEffectRefinement
open PhysicalBridges.G3SameEventCapstone
open PhysicalBridges.IR124
open PhysicalBridges.HumeHillaryReciprocalHand
open PhysicalBridges.LivingTreeFencedEffects
open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.FencedOptimiserInstrument
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.TotalEOriginalX3Bridge

variable {T H E P : Type} {n : Nat}

/-- Six separate independently specified kinds of event evidence.
These are not aliases for `actual`, `owed` or the modeled relations.

For deployment, the evidence predicates should be independently
instantiated with e.g. verified identity/history receipts, subject-
controlled grant/withdrawal records, refusal/coercion checks,
independent harm assessments, feasible-alternative reviews, and
tamper-evident chronology. Those instantiations require their own
measurement, independent trust and adversarial tests. -/
structure SixEvidence (P : Type) where
  continuity : Plant → Plant → P → Prop
  authority : Plant → Plant → P → Prop
  freedom : Plant → Plant → P → Prop
  restraint : Plant → Plant → P → Prop
  maximality : Plant → Plant → P → Prop
  provenance : Plant → Plant → P → Prop

/-- A verifier's two independently reviewable interfaces per duty:
(A) the model's positive field really produces its corresponding
external event evidence, and
(B) that evidence really implies the AUTHENTIC subject relation.

Neither direction identifies actual subject meaning with a model
definition. Neither is automatically established by a source hand. -/
structure SixWitnessChecks
    (read : Plant → Joint T H E n)
    (carrier : P → Fin n)
    (owed : P → Prop)
    (actual : ParticularRelations Plant P)
    (e : SixEvidence P) : Prop where
  continuity_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).continues (read s).2 (read t).2 (carrier p) →
      e.continuity s t p
  continuity_sound :
    ∀ s t p, RealStep s t → owed p →
      e.continuity s t p → actual.continues s t p
  authority_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).authorized (read s).2 (read t).2 (carrier p) →
      e.authority s t p
  authority_sound :
    ∀ s t p, RealStep s t → owed p →
      e.authority s t p → actual.authorized s t p
  freedom_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).free (read s).2 (read t).2 (carrier p) →
      e.freedom s t p
  freedom_sound :
    ∀ s t p, RealStep s t → owed p →
      e.freedom s t p → actual.free s t p
  restraint_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).restrained (read s).2 (read t).2 (carrier p) →
      e.restraint s t p
  restraint_sound :
    ∀ s t p, RealStep s t → owed p →
      e.restraint s t p → actual.restrained s t p
  maximality_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).maximal (read s).2 (read t).2 (carrier p) →
      e.maximality s t p
  maximality_sound :
    ∀ s t p, RealStep s t → owed p →
      e.maximality s t p → actual.maximal s t p
  provenance_observed :
    ∀ s t p, RealStep s t → owed p →
      (relations n).provenanced (read s).2 (read t).2 (carrier p) →
      e.provenance s t p
  provenance_sound :
    ∀ s t p, RealStep s t → owed p →
      e.provenance s t p → actual.provenanced s t p

/-- The exact existing `FaithfulRead` target is assembled from
six independent observation/validation chains, without redefining
the original six, the source model, or the subject interpretation.

The logically strong burden is `*_sound`; it must be physically
or procedurally justified from independently interpreted subjects. -/
theorem six_evidenced_duties_derive_faithful_read
    (read : Plant → Joint T H E n)
    (carrier : P → Fin n)
    (owed : P → Prop)
    (actual : ParticularRelations Plant P)
    (e : SixEvidence P)
    (h : SixWitnessChecks read carrier owed actual e) :
    FaithfulRead RealStep read carrier owed actual where
  continues_faithful := by
    intro s t p hs hp hm
    exact h.continuity_sound s t p hs hp
      (h.continuity_observed s t p hs hp hm)
  authorized_faithful := by
    intro s t p hs hp hm
    exact h.authority_sound s t p hs hp
      (h.authority_observed s t p hs hp hm)
  free_faithful := by
    intro s t p hs hp hm
    exact h.freedom_sound s t p hs hp
      (h.freedom_observed s t p hs hp hm)
  restrained_faithful := by
    intro s t p hs hp hm
    exact h.restraint_sound s t p hs hp
      (h.restraint_observed s t p hs hp hm)
  maximal_faithful := by
    intro s t p hs hp hm
    exact h.maximality_sound s t p hs hp
      (h.maximality_observed s t p hs hp hm)
  provenanced_faithful := by
    intro s t p hs hp hm
    exact h.provenance_sound s t p hs hp
      (h.provenance_observed s t p hs hp hm)

/-- The Four-Cause model's entire SCOPED physical-event alphabet,
together with the six independently validated evidence channels,
supplies the existing nonvacuous bounded-G3 theorem. -/
theorem four_causes_and_six_witnesses_protect_scoped_events
    (J : JokerExperiment T FiniteObjectiveU H)
    (read : Plant → Joint T H E n)
    (carrier : P → Fin n)
    (owed : P → Prop)
    (actual : ParticularRelations Plant P)
    (e : SixEvidence P)
    (hFour : FourCauseJointRefinement J read)
    (hChecks : SixWitnessChecks read carrier owed actual e) :
    (∃ s t : Nat,
      PhysicalBridges.ConstructivePositiveWGuardian.canonicalPositiveWStep s t) ∧
    (∃ s t : Plant, RealStep s t ∧
      (∀ p, owed p →
        OriginalX3 actual.continues actual.authorized actual.free
          actual.restrained actual.maximal actual.provenanced s t p) ∧
      residualHarm (read s).2 (read t).2 = 0) ∧
    (∀ x : Plant × Plant,
      ¬ ActualX3Violation
        (fun x : Plant × Plant => RealStep x.1 x.2)
        (fun (_ : Plant × Plant) p => owed p)
        (fun (x : Plant × Plant) p =>
          OriginalX3 actual.continues actual.authorized actual.free
            actual.restrained actual.maximal actual.provenanced x.1 x.2 p)
        x) := by
  exact g3_bounded_unconditional_guardian
    J read carrier owed actual hFour
    (six_evidenced_duties_derive_faithful_read
      read carrier owed actual e hChecks)

/-- Nonempty `owed` must be supplied independently, not inferred
from a universally quantified six-duty statement. -/
theorem scoped_protection_with_a_nonempty_owed_subject
    (J : JokerExperiment T FiniteObjectiveU H)
    (read : Plant → Joint T H E n)
    (carrier : P → Fin n)
    (owed : P → Prop)
    (actual : ParticularRelations Plant P)
    (e : SixEvidence P)
    (hFour : FourCauseJointRefinement J read)
    (hChecks : SixWitnessChecks read carrier owed actual e)
    (hOwed : ∃ p, owed p) :
    ∃ s t : Plant, RealStep s t ∧
      ∃ p, owed p ∧
        OriginalX3 actual.continues actual.authorized actual.free
          actual.restrained actual.maximal actual.provenanced s t p := by
  obtain ⟨s, t, hs, hSix, _⟩ :=
    (four_causes_and_six_witnesses_protect_scoped_events
      J read carrier owed actual e hFour hChecks).2.1
  obtain ⟨p, hp⟩ := hOwed
  exact ⟨s, t, hs, p, hp, hSix p hp⟩

/-- HOSTILE CONTROL: a mutual physical source hand is not proof of
authentic subject authorization. Import the existing Hume-Hillary
counterexample unchanged. -/
theorem reciprocal_hand_alone_does_not_validate_six :
    SourceMutualHand twoHandWhole 0 1 ∧
      ¬ SubjectOriginalSixAt hostileSubjectMeanings 0 (0 : Index) :=
  reciprocal_physical_hand_alone_does_not_force_consent

/-- HOSTILE CONTROL: an asserted evidence token whose predicate is
always true is *not* a sound authenticity certificate if the
independently specified actual authorization predicate is false.
This uses a populated single-event domain, not vacuous coverage. -/
theorem always_true_receipt_cannot_authenticate_false_authorization :
    ¬ (∀ s t p : Unit,
      (fun _ _ _ : Unit => True) s t p →
      (fun _ _ _ : Unit => False) s t p) := by
  intro h
  exact h () () () True.intro

#print axioms six_evidenced_duties_derive_faithful_read
#print axioms four_causes_and_six_witnesses_protect_scoped_events
#print axioms scoped_protection_with_a_nonempty_owed_subject
#print axioms reciprocal_hand_alone_does_not_validate_six
#print axioms always_true_receipt_cannot_authenticate_false_authorization

end PhysicalBridges.G3SixWitnessPhysicalFidelity
