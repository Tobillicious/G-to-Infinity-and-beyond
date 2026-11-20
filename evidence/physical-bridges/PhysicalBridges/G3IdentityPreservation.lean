import PhysicalBridges.KoruSubjectFidelityLift
import PhysicalBridges.BCRDParticularCarrierCriterion

/-!
# Step 2: Identity preservation through transformation

Each identified particular remains distinguishable through the modeled
transformations — not merely that an identifier survives, but that
distinct particulars never merge and each retains its full six-duty
profile across every W stage.

Joins:
  - BCRDTransportedParticularMarker (dynamic markers stay injective)
  - BCRDParticularCarrierCriterion (CarrierAt preserves injectivity)
  - KoruSubjectFidelityLift (source origin + fidelity → six for all)

New results:
  1. Identity and protection compose: injective carrier + fidelity +
     positive origin → distinguishable AND protected at every stage
  2. Collision counterexample: colliding carrier is non-injective
  3. Identity loss implies duty loss: without injectivity, the source
     cannot distinguish two particulars' profiles

No existing definition is changed. No original six, Koru, or carrier
definition is altered.
-/

namespace PhysicalBridges.G3IdentityPreservation

open PhysicalBridges.BCRDTransportedParticularMarker
open PhysicalBridges.BCRDParticularCarrierCriterion
open PhysicalBridges.KoruSubjectFidelityLift
open PhysicalBridges.KoruCompleteOperatorSixX3WebJoin
open PhysicalBridges.KoruOperatorIndexedSubjectSemantics
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.FrozenBCRDEvents

variable {P : Type}

/-- Full identity and protection at every W stage. An injective carrier
    maps distinct particulars to distinct source positions, and those
    positions carry all six original duties through every transformation.
    Both conjuncts — identity AND protection — are proved together from
    the same three hypotheses. Neither is assumed from the other. -/
theorem identity_and_protection_at_every_stage
    (r : ParticularRelations Nat P)
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (hInjective : Function.Injective carrier)
    (hOrigin : ∀ p : P, SixSourceTruth 0 d (roles (carrier p)))
    (hFidelity : WholeSourceFidelity r d roles carrier) :
    ∀ n : Nat,
      Function.Injective (CarrierAt carrier n) ∧
      (∀ p : P, OriginalX3 r.continues r.authorized r.free
        r.restrained r.maximal r.provenanced n (n + 1) p) := by
  exact independent_carrier_and_semantics_jointly_lift
    r d roles carrier hInjective hOrigin hFidelity

/-- Distinguishability is monotone: once two particulars are distinct
    at any stage, they remain distinct at all later stages. The frozen
    source permutation is invertible, so it cannot merge what was apart.
    This holds even without positive source origin or fidelity. -/
theorem distinguishability_persists
    (carrier : P → Index) (hInjective : Function.Injective carrier)
    (p q : P) (hDistinct : p ≠ q)
    (n : Nat) :
    CarrierAt carrier n p ≠ CarrierAt carrier n q := by
  intro hMerge
  have hInj := (carrier_injective_after_iff_before carrier n).mpr hInjective
  exact hDistinct (hInj hMerge)

/-- If a carrier maps two distinct particulars to the same source
    position, they share the same source-edge truth value at every
    stage and every tag. Neither can receive a duty the other lacks.
    Merged identity means merged duty profiles. -/
theorem merged_carrier_forces_identical_source_edges
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (p q : P) (hCollide : carrier p = carrier q)
    (n : Nat) (tag : DutyTag) :
    completeOperatorSourceEdge d roles carrier n p tag ↔
      completeOperatorSourceEdge d roles carrier n q tag := by
  unfold completeOperatorSourceEdge
  rw [hCollide]

/-- A colliding carrier — two distinct Bool values mapped to the same
    source position — is not injective. This is a concrete witness
    that carrier collision is possible and testable. -/
theorem collision_witness :
    ∃ (carrier : Bool → Index),
      ¬ Function.Injective carrier ∧
      carrier true = carrier false := by
  refine ⟨collidingCandidateCarrier, ?_, rfl⟩
  intro h
  have hEq : (true : Bool) = false := h rfl
  exact absurd hEq (by decide)

/-- The constructive contrapositive: if any two particulars receive
    different source-level duty reports at some stage, they MUST have
    had distinct carrier positions from the start. The forward direction
    (merged_carrier_forces_identical_source_edges) gives: same carrier →
    same edges. So different edges → different carrier. -/
theorem independent_source_reports_require_distinct_carrier
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (p q : P) (n : Nat) (tag : DutyTag)
    (hDiff : completeOperatorSourceEdge d roles carrier n p tag ∧
      ¬ completeOperatorSourceEdge d roles carrier n q tag) :
    carrier p ≠ carrier q := by
  intro hCollide
  exact hDiff.2 ((merged_carrier_forces_identical_source_edges
    d roles carrier p q hCollide n tag).mp hDiff.1)

/-- Subject-level protection requires distinct carrier positions:
    if fidelity holds and two particulars have different subject-edge
    truth values, they cannot share a carrier position.
    This joins carrier discrimination with subject-level semantics. -/
theorem independent_subject_protection_requires_distinct_carrier
    (r : ParticularRelations Nat P)
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (hFidelity : WholeSourceFidelity r d roles carrier)
    (p q : P) (n : Nat) (tag : DutyTag)
    (hDiff : subjectEdge r n p tag ∧ ¬ subjectEdge r n q tag) :
    carrier p ≠ carrier q := by
  intro hCollide
  have hSourceP := (hFidelity n p tag).mp hDiff.1
  have hSourceQ : completeOperatorSourceEdge d roles carrier n q tag :=
    (merged_carrier_forces_identical_source_edges
      d roles carrier p q hCollide n tag).mp hSourceP
  exact hDiff.2 ((hFidelity n q tag).mpr hSourceQ)

/-- The full identity-preservation package: given an injective carrier,
    positive origin, and whole-source fidelity, every finite horizon
    preserves:
    (a) carrier injectivity (no merging)
    (b) all six original duties for every particular
    (c) exact source causal traces for every particular
    All three are independent consequences of the same hypotheses. -/
theorem full_identity_preservation_package
    (r : ParticularRelations Nat P)
    (d : SixOperatorSourceDuties)
    (roles : Index → Fin 4 → Index)
    (carrier : P → Index)
    (hInjective : Function.Injective carrier)
    (hOrigin : ∀ p : P, SixSourceTruth 0 d (roles (carrier p)))
    (hFidelity : WholeSourceFidelity r d roles carrier) :
    ∀ n : Nat,
      Function.Injective (CarrierAt carrier n) ∧
      (∀ p : P, OriginalX3 r.continues r.authorized r.free
        r.restrained r.maximal r.provenanced n (n + 1) p) ∧
      (∀ p : P,
        PhysicalBridges.IR96.Reach ActualPositionStep
          (carrier p) (CarrierAt carrier n p)) := by
  intro n
  have ⟨hInj, hSix⟩ := identity_and_protection_at_every_stage
    r d roles carrier hInjective hOrigin hFidelity n
  exact ⟨hInj, hSix, fun p =>
    candidate_carrier_has_exact_source_path carrier p n⟩

#print axioms identity_and_protection_at_every_stage
#print axioms distinguishability_persists
#print axioms merged_carrier_forces_identical_source_edges
#print axioms collision_witness
#print axioms independent_source_reports_require_distinct_carrier
#print axioms independent_subject_protection_requires_distinct_carrier
#print axioms full_identity_preservation_package

end PhysicalBridges.G3IdentityPreservation
