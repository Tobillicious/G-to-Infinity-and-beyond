import PhysicalBridges.G2BoundedPhysicalProtectionSynthesis
import PhysicalBridges.G3SameEventCapstone

/-!
# One physical domain: original cohort + authentic original-six protection

A non-weakening assembly of two distinct checked source proof lines:
- IR96/IR127: the same physical trace has a certified accepted source
  history, with every originally owed individual continuing and retaining
  all required executable options.
- G3 same-event capstone: every externally declared actual effect refines
  a guarded joint effect, with all six authentic semantic implications.

The two lines share the SAME independently defined realStep domain here.
No new definition of actual physical events, Koru, personhood, consent,
or original-six duties is introduced. The physical refinement and six
semantic reflection evidence remain explicit obligations; an empty real
event domain cannot pretend to be observational proof.
-/

namespace PhysicalBridges.IntegratedProtectionCoexistenceAssembly

open PhysicalBridges.IR127
open PhysicalBridges.IR96
open PhysicalBridges.G2BoundedPhysicalProtectionSynthesis
open PhysicalBridges.G3SameEventCapstone
open PhysicalBridges.ExternalJointEffectRefinement
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.LivingTreeFencedEffects
open PhysicalBridges.FencedOptimiserInstrument
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

universe u v w x

/-- Protection of original individuals and full unchanged OriginalX3
    on a single physical system and its independently supplied history.
    In particular the IR127 Protected source predicate is not used
    as a replacement for genuine six-duty semantic reflection. -/
theorem covered_history_keeps_originals_and_every_actual_step_has_six
    {Node : Type u} {Mind : Type v} {Action : Type w}
    {Physical : Type x} {T H E P : Type} {n : Nat}
    (relate : State Node Mind Action → Physical → Prop)
    (realStep : Physical → Physical → Prop)
    (physicalProtected : Physical → Prop)
    (hMediation : ∀ s p q,
      relate s p → realStep p q →
      ∃ t, AcceptedStep s t ∧ relate t q)
    (hReflect : ∀ s p, relate s p →
      Protected s → physicalProtected p)
    (s : State Node Mind Action) (p q : Physical)
    (hRelated : relate s p)
    (hInitial : Protected s)
    (hPhysical : Reach realStep p q)
    (J : JokerExperiment T FiniteObjectiveU H)
    (read : Physical → Joint T H E n)
    (carrier : P → Fin n)
    (owed : P → Prop)
    (actual : ParticularRelations Physical P)
    (hCoverage : AllActualEffectsRefineJoint J realStep read)
    (hMeaning : AuthenticSixReflections
      realStep read carrier owed actual) :
    physicalProtected q ∧
    (∃ t : State Node Mind Action,
      relate t q ∧ Protected t ∧
      (∀ m, s.owed m →
        t.owed m ∧ t.continues m ∧
        (∃ a, t.required m a) ∧
        (∀ a, t.required m a → t.executable m a))) ∧
    (∀ a b, realStep a b → ∀ z, owed z →
      OriginalX3 actual.continues actual.authorized actual.free
        actual.restrained actual.maximal actual.provenanced a b z) := by
  have hCohort :=
    covered_physical_trace_preserves_protection_and_original_cohort
      relate realStep physicalProtected hMediation hReflect
      s p q hRelated hInitial hPhysical
  have hSix :=
    independently_covered_events_satisfy_original_six
      J realStep read carrier owed actual hCoverage hMeaning
  exact ⟨hCohort.1, hCohort.2, hSix⟩

#print axioms covered_history_keeps_originals_and_every_actual_step_has_six

end PhysicalBridges.IntegratedProtectionCoexistenceAssembly
