import PhysicalBridges.G3CompleteKoruEventExhaustiveness
import PhysicalBridges.G3MatterspacetimeRealizationGate

/-!
# Complete Koru witnessed events: from physical evidence to Tree coverage

Backwards-summit additive join. Reuses:
* G3MatterspacetimeRealizationGate.PhysicalRepresentation and its
  independently specified actual, recorded and realizes relations;
* CompleteKoruMatterspacetimeCoverage.EventWitness and Classified;
* G3CompleteKoruEventExhaustiveness.EventExhaustive and the existing
  W-coverage sufficiency theorem.

A whole record with operation, ordered inputs, outcome and provenance
does not by itself establish its physical enactment, causal classification
or membership in the canonical W Tree. These remain independently
auditable obligations, not assumptions named 'safety'.

The result supplies canonical W coverage only when an actual event has
a realizing witness and realized events are demonstrably Tree steps.
Countercontrols prevent a missing/unknown or outside-Tree actual event
from being silently erased.
-/

namespace PhysicalBridges.G3WitnessedEventExhaustiveness

open PhysicalBridges.G3CompleteKoruEventExhaustiveness
open PhysicalBridges.G3MatterspacetimeRealizationGate
open PhysicalBridges.G3TreeCoverage
open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.EverestActualWEventJoin
open CompleteKoruMatterspacetimeCoverage

variable {T H E W : Type}

/-- A realizing physical record yields Tree-event inclusion ONLY if
    independent enactment soundness relates its actual realization to
    the already defined Tree. No recorded label is redefined as a step. -/
theorem realizing_witnesses_give_event_exhaustiveness
    (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E)
    (R : PhysicalRepresentation (LivingTree T H E) W)
    (hCoverage : CompletePhysicalCoverage R)
    (hRealizedTree : ∀ w s t, R.realizes w s t → treeStep J seed s t) :
    EventExhaustive J seed R.actual := by
  intro s t hActual
  obtain ⟨w, _, hReal⟩ := hCoverage s t hActual
  exact hRealizedTree w s t hReal

/-- Fully witnessed actual events acquire canonical W coverage from
    independently supplied realization soundness, W-faithful learning
    and aligned seed. The new result is a join, not new physics. -/
theorem complete_witnessed_events_have_W_coverage
    (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E)
    (U : FiniteObjectiveU)
    (R : PhysicalRepresentation (LivingTree T H E) W)
    (hCoverage : CompletePhysicalCoverage R)
    (hRealizedTree : ∀ w s t, R.realizes w s t → treeStep J seed s t)
    (hSeed : seed.whole = objectiveAt U seed.epoch)
    (hFaithful : WFaithful J seed) :
    CompleteWEventCoverage R.actual (treeStep J seed)
      (fun s => s.whole) (fun s => s.epoch) U := by
  exact tree_source_covers_exhausted_physical_domain
    J seed U R.actual hSeed hFaithful
    (realizing_witnesses_give_event_exhaustiveness J seed R
      hCoverage hRealizedTree)

/-- Classified whole witnesses include operation, ordered inputs, outcome,
    provenance, and a cause class that is NOT unknown. Neither this
    classification nor the existence of the record implies consent. -/
theorem actual_event_has_classified_realizing_whole
    {Op Input Output Provenance : Type}
    (R : PhysicalRepresentation (LivingTree T H E)
      (EventWitness Op Input Output Provenance))
    (hCoverage : CompletePhysicalCoverage R)
    (hClassified : ∀ s t w, R.actual s t →
      R.recorded s t = some w → Classified w)
    (s t : LivingTree T H E) (ha : R.actual s t) :
    ∃ w, R.recorded s t = some w ∧
      R.realizes w s t ∧ Classified w := by
  obtain ⟨w, hw, hReal⟩ := hCoverage s t ha
  exact ⟨w, hw, hReal, hClassified s t w ha hw⟩

/-- If an actual, independently enacted event lies outside the Tree,
    physical witness coverage and sound realization-as-Tree cannot
    BOTH hold. The event is not declared invalid or harmful. -/
theorem outside_event_refutes_witnessed_tree_bridge
    (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E)
    (R : PhysicalRepresentation (LivingTree T H E) W)
    (s t : LivingTree T H E)
    (ha : R.actual s t) (hout : ¬ treeStep J seed s t) :
    ¬ (CompletePhysicalCoverage R ∧
       (∀ w s t, R.realizes w s t → treeStep J seed s t)) := by
  rintro ⟨hCoverage, hSound⟩
  have hEx : EventExhaustive J seed R.actual :=
    realizing_witnesses_give_event_exhaustiveness J seed R
      hCoverage hSound
  exact hout (hEx s t ha)

/-- An actual event with a recorded but unknown cause cannot satisfy
    universal classified-record coverage. The record still exists;
    classification failure is not an assertion that the event never
    happened. -/
theorem recorded_unknown_actual_refutes_classification
    {Op Input Output Provenance : Type}
    (R : PhysicalRepresentation (LivingTree T H E)
      (EventWitness Op Input Output Provenance))
    (s t : LivingTree T H E)
    (w : EventWitness Op Input Output Provenance)
    (ha : R.actual s t)
    (hw : R.recorded s t = some w)
    (hUnknown : w.cause = .unknown) :
    ¬ (∀ s t w, R.actual s t →
      R.recorded s t = some w → Classified w) := by
  intro h
  exact (h s t w ha hw) hUnknown

#print axioms realizing_witnesses_give_event_exhaustiveness
#print axioms complete_witnessed_events_have_W_coverage
#print axioms actual_event_has_classified_realizing_whole
#print axioms outside_event_refutes_witnessed_tree_bridge
#print axioms recorded_unknown_actual_refutes_classification

end PhysicalBridges.G3WitnessedEventExhaustiveness
