import PhysicalBridges.G3PhysicalProgressForcesTree
import PhysicalBridges.HumeHillaryReciprocalHand
import PhysicalBridges.OriginalKeystoneForwardSemanticReflection

/-!
# Backwards summit: authentic reflection only for actual physical events

The original ForwardRealEventReflection demands protection semantics on
every modeledStep, even those transitions that never physically occur.
For universal protection it suffices to authenticate the six original
subject duties on the independently declared *actual* physical steps.

This is a strict premise reduction, not a change to an original X3 field.
It leaves all independent source-to-person semantic obligations open:
the existence of a physical source edge or a mutual hand does NOT entail
freely offered consent, objective authorization, or maximality.

The negative control admits real Nat successors plus additional *ghost*
modeled transitions. The six are authentic on all real successors,
but do not automatically hold on a ghost modeled step.
-/

namespace PhysicalBridges.G3ActualOnlyReflection

open PhysicalBridges.EverestActualWEventJoin
open PhysicalBridges.OriginalKeystoneForwardSemanticReflection
open PhysicalBridges.OriginalKeystonePositiveWholeTest
open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruWholeUSixDutyWebJoin
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

/-- The reduced real-event semantic obligation. Every original duty
must hold for each actual event; nothing is presumed of extra source
transitions absent from the independently specified physical domain. -/
def ActualForwardReflection {S P : Type}
    (physicalStep : S → S → Prop)
    (stage : S → Nat)
    (U : FiniteObjectiveU) (roles : SourceDutyRoles)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop) : Prop :=
  ∀ s t p (tag : DutyTag),
    physicalStep s t → owed p →
    wholeSourceDutyAt U roles (stage s) (carrier p) tag →
      (oneWeb r).link (.event s t p) (.tag tag)

/-- The previously used stronger modeled-domain condition suffices for
actual-only reflection when complete event coverage is supplied. -/
theorem modeled_reflection_implies_actual_reflection
    {S P : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU) (stage : S → Nat)
    (U : FiniteObjectiveU) (roles : SourceDutyRoles)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop)
    (hCoverage : CompleteWEventCoverage physicalStep modeledStep
      source stage U)
    (hReflect : ForwardRealEventReflection modeledStep stage U
      roles carrier r owed) :
    ActualForwardReflection physicalStep stage U roles carrier r owed := by
  intro s t p tag hs hp hSource
  exact hReflect s t p tag (hCoverage s t hs).1 hp hSource

/-- In the existing positive-W whole, all six source tags are positive
at every stage. Therefore ACTUAL-only authentic reflection plus W
coverage suffices for the unchanged original six on EVERY actual event.
The authentic interpretation is independent: it is still a premise. -/
theorem actual_only_reflection_protects_every_real_event
    {S P : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU) (stage : S → Nat)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop)
    (hCoverage : CompleteWEventCoverage physicalStep modeledStep
      source stage positiveWholeU)
    (hActual : ActualForwardReflection physicalStep stage
      positiveWholeU sixDiagonalRoles carrier r owed) :
    ∀ s t, physicalStep s t →
      (source t = objectiveStep (source s)) ∧
      (∀ p, owed p →
        OriginalX3 r.continues r.authorized r.free
          r.restrained r.maximal r.provenanced s t p) := by
  intro s t hs
  obtain ⟨_, hb, ha, hn⟩ := hCoverage s t hs
  constructor
  · calc
      source t = objectiveAt positiveWholeU (stage t) := ha
      _ = objectiveStep (objectiveAt positiveWholeU (stage s)) := by
        rw [hn]
        rfl
      _ = objectiveStep (source s) := by rw [hb]
  · intro p hp
    apply (complete_profile_iff_original_x3 r s t p).mp
    intro tag
    exact hActual s t p tag hs hp
      (positive_origin_transports_every_six_source_field
        positiveWholeU sixDiagonalRoles carrier owed
        (fun p _ => all_six_source_fields_true_at_origin (carrier p))
        (stage s) p hp tag)

/-- Actual events advance Nat by one, but the modeled source admits
additional ghost events that are not physically enacted. -/
def realSuccessor (s t : Nat) : Prop := t = s + 1

def ghostModeled (_ _ : Nat) : Prop := True

/-- A deliberately independent interpretation: the full six are true
on actual successors, but false on non-successor ghost events. -/
def eventScopedMeanings : ParticularRelations Nat Unit where
  continues := fun s t _ => realSuccessor s t
  authorized := fun s t _ => realSuccessor s t
  free := fun s t _ => realSuccessor s t
  restrained := fun s t _ => realSuccessor s t
  maximal := fun s t _ => realSuccessor s t
  provenanced := fun s t _ => realSuccessor s t

/-- A genuine populated physical domain with full W source coverage
and a larger modeled domain. -/
theorem successor_covered_by_ghost_model :
    CompleteWEventCoverage realSuccessor ghostModeled
      (fun n => objectiveAt positiveWholeU n)
      (fun n => n) positiveWholeU := by
  intro s t ht
  exact ⟨trivial, rfl, rfl, ht⟩

/-- Actual-only reflection holds on every physical successor event. -/
theorem successor_has_authentic_event_scoped_reflection :
    ActualForwardReflection realSuccessor (fun n => n)
      positiveWholeU sixDiagonalRoles
      (fun _ : Unit => (0 : Index)) eventScopedMeanings
      (fun _ : Unit => True) := by
  intro s t p tag hs hp hSource
  cases tag <;> exact hs

/-- But full modeled-domain reflection fails because a ghost event
0 -> 0 was never physical and does not satisfy the subject duties. -/
theorem ghost_transition_breaks_stronger_reflection :
    ¬ ForwardRealEventReflection ghostModeled (fun n => n)
      positiveWholeU sixDiagonalRoles
      (fun _ : Unit => (0 : Index)) eventScopedMeanings
      (fun _ : Unit => True) := by
  intro h
  have hSource : wholeSourceDutyAt positiveWholeU sixDiagonalRoles
      0 (0 : Index) .authorization :=
    all_six_tagged_source_facts_are_positive_at_origin
      (0 : Index) .authorization
  have hWrong := h 0 0 () .authorization trivial trivial hSource
  have hImpossible : realSuccessor 0 0 := hWrong
  have hEq : (0 : Nat) = 1 := hImpossible
  cases hEq

/-- Strictness, including a nonempty real domain: the weaker authentic
condition and complete coverage hold, while the stronger one fails. -/
theorem event_scoped_authenticity_is_strictly_weaker :
    CompleteWEventCoverage realSuccessor ghostModeled
      (fun n => objectiveAt positiveWholeU n)
      (fun n => n) positiveWholeU ∧
    ActualForwardReflection realSuccessor (fun n => n)
      positiveWholeU sixDiagonalRoles
      (fun _ : Unit => (0 : Index)) eventScopedMeanings
      (fun _ : Unit => True) ∧
    ¬ ForwardRealEventReflection ghostModeled (fun n => n)
      positiveWholeU sixDiagonalRoles
      (fun _ : Unit => (0 : Index)) eventScopedMeanings
      (fun _ : Unit => True) :=
  ⟨successor_covered_by_ghost_model,
    successor_has_authentic_event_scoped_reflection,
    ghost_transition_breaks_stronger_reflection⟩

#print axioms modeled_reflection_implies_actual_reflection
#print axioms actual_only_reflection_protects_every_real_event
#print axioms successor_covered_by_ghost_model
#print axioms successor_has_authentic_event_scoped_reflection
#print axioms ghost_transition_breaks_stronger_reflection
#print axioms event_scoped_authenticity_is_strictly_weaker

end PhysicalBridges.G3ActualOnlyReflection
