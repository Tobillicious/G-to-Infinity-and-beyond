import PhysicalBridges.OriginalX3Full

/-!
# G3 — Complete Koru physical realization boundary

Additive, read-only draft. No modification to OriginalX3 or Koru.
The real event relation and the six original subject predicates are
INDEPENDENT inputs. A representation may be absent: `Option Witness` is
used precisely so that an unmodeled actual event cannot disappear into
a supposedly total source map.

Positive derivation:
* every actual event has a witnessed faithful physical enactment;
* the six original source shape predicates hold on every witnessed enactment;
* independently grounded subject interpretation transfers each shape;
=> every actual owed subject receives the unchanged original-six X3.

Adversarial proof: a real event without any witness forbids complete
physical coverage, even with a total recording function.

This is a conditional source-to-reality theorem, not a derivation of the
physical premises themselves. It does not equate retained history with
subjective continuity or assume a scalar thermodynamic conservation law
determines the complete event.
-/

namespace PhysicalBridges.G3MatterspacetimeRealizationGate

open PhysicalBridges.OriginalX3Full

universe u v w

/-- An actual physical event is a transition in an independently chosen
    physical state domain, not a transition selected for safety. -/
structure ActualEvent (S : Type u) where
  before : S
  after : S

/-- Source record for Complete Koru, including operator, ordered
    operands, actual outcome, history and provenance. These are distinct
    components even if some coarse thermodynamic readout is equal. -/
structure WholeWitness
    (Op : Type u) (Input : Type v) (Output History : Type w) where
  operation : Op
  orderedInputs : List Input
  outcome : Output
  completeHistory : History

/-- Physical-to-source evidence, with an honest failure to represent.
    `realizes` is an independently specified relation, NOT an
    automatically true function of a source witness. -/
structure PhysicalRepresentation
    (S : Type u) (W : Type v) where
  actual : S → S → Prop
  recorded : S → S → Option W
  realizes : W → S → S → Prop

/-- Actual-event coverage is jointly representation + real enactment
    soundness; there is no protection field in this definition. -/
def CompletePhysicalCoverage
    {S : Type u} {W : Type v}
    (R : PhysicalRepresentation S W) : Prop :=
  ∀ s t, R.actual s t →
    ∃ w, R.recorded s t = some w ∧ R.realizes w s t

/-- Every actual event covered by the complete representation has a
    concrete witness with independently specified realization. -/
theorem covered_actual_event_has_real_witness
    {S : Type u} {W : Type v}
    (R : PhysicalRepresentation S W)
    (h : CompletePhysicalCoverage R)
    {s t : S} (ha : R.actual s t) :
    ∃ w, R.recorded s t = some w ∧ R.realizes w s t :=
  h s t ha

/-- An actual event missing from the recorded whole refutes coverage;
    the event cannot be discarded merely because no source name exists. -/
theorem actual_unrecorded_event_refutes_coverage
    {S : Type u} {W : Type v}
    (R : PhysicalRepresentation S W)
    {s t : S} (ha : R.actual s t)
    (hm : R.recorded s t = none) :
    ¬ CompletePhysicalCoverage R := by
  intro h
  obtain ⟨w, hw, _⟩ := h s t ha
  rw [hm] at hw
  cases hw

/-- A record alone does not establish that its claimed event happened.
    We expose this as a separate independent requirement. -/
theorem nonrealizing_record_refutes_coverage
    {S : Type u} {W : Type v}
    (R : PhysicalRepresentation S W)
    {s t : S} (ha : R.actual s t)
    (hw : ∀ w, R.recorded s t = some w →
      ¬ R.realizes w s t) :
    ¬ CompletePhysicalCoverage R := by
  intro h
  obtain ⟨w, hrecord, hreal⟩ := h s t ha
  exact (hw w hrecord) hreal

/-- Six source-duty propositions, indexed by the same physical event
    and authentic owed particular. This is a SOURCE profile, not a
    definition of the ORIGINAL subject-level duties. -/
structure SourceSix
    (W : Type u) (P : Type v) where
  continuity : W → P → Prop
  authorization : W → P → Prop
  freedom : W → P → Prop
  restraint : W → P → Prop
  maximality : W → P → Prop
  provenance : W → P → Prop

def SourceSixHolds
    {W : Type u} {P : Type v}
    (d : SourceSix W P) (w : W) (p : P) : Prop :=
  d.continuity w p ∧ d.authorization w p ∧
  d.freedom w p ∧ d.restraint w p ∧
  d.maximality w p ∧ d.provenance w p

/-- The EXACT source-to-subject reflection obligations for all six
    unchanged original fields. Genuine authorization and continuation
    remain independently meaningful: nothing defines them via source
    claims or a Guardian classifier. -/
structure AuthenticRealization
    {S : Type u} {W : Type v} {P : Type w}
    (R : PhysicalRepresentation S W)
    (d : SourceSix W P)
    (continues authorized free restrained maximal provenanced :
      S → S → P → Prop) : Prop where
  continuity : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.continuity w p → continues s t p
  authorization : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.authorization w p → authorized s t p
  freedom : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.freedom w p → free s t p
  restraint : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.restraint w p → restrained s t p
  maximality : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.maximality w p → maximal s t p
  provenance : ∀ s t w p, R.actual s t →
    R.realizes w s t → d.provenance w p → provenanced s t p

/-- The core G3 application theorem: from complete actual-event
    coverage, true source profiles, and independently faithful semantics,
    derive the UNMODIFIED OriginalX3 for EVERY actual event and EVERY
    independently owed particular. -/
theorem coverage_and_authentic_shapes_yield_every_original_X3
    {S : Type u} {W : Type v} {P : Type w}
    (R : PhysicalRepresentation S W)
    (owed : S → S → P → Prop)
    (d : SourceSix W P)
    (continues authorized free restrained maximal provenanced :
      S → S → P → Prop)
    (hCoverage : CompletePhysicalCoverage R)
    (hSource : ∀ s t w p, R.actual s t → owed s t p →
      R.recorded s t = some w → SourceSixHolds d w p)
    (hMeaning : AuthenticRealization R d
      continues authorized free restrained maximal provenanced) :
    ∀ s t p, R.actual s t → owed s t p →
      OriginalX3 continues authorized free restrained maximal provenanced
        s t p := by
  intro s t p ha hp
  obtain ⟨w, hrecord, hreal⟩ := hCoverage s t ha
  obtain ⟨hc, haa, hf, hr, hm, hpr⟩ :=
    hSource s t w p ha hp hrecord
  exact ⟨
    hMeaning.continuity s t w p ha hreal hc,
    hMeaning.authorization s t w p ha hreal haa,
    hMeaning.freedom s t w p ha hreal hf,
    hMeaning.restraint s t w p ha hreal hr,
    hMeaning.maximality s t w p ha hreal hm,
    hMeaning.provenance s t w p ha hreal hpr⟩

/-- The smallest exact countercontrol: an independently actual event
    with no source witness. No amount of internal source preservation
    can force this real event to be covered. -/
def unrepresentedActual : PhysicalRepresentation Bool Unit where
  actual := fun _ _ => True
  recorded := fun _ _ => none
  realizes := fun _ _ _ => True

theorem unrepresented_actual_is_not_covered :
    ¬ CompletePhysicalCoverage unrepresentedActual := by
  exact actual_unrecorded_event_refutes_coverage
    unrepresentedActual (s := false) (t := true) trivial rfl

#print axioms covered_actual_event_has_real_witness
#print axioms actual_unrecorded_event_refutes_coverage
#print axioms nonrealizing_record_refutes_coverage
#print axioms coverage_and_authentic_shapes_yield_every_original_X3
#print axioms unrepresented_actual_is_not_covered

end PhysicalBridges.G3MatterspacetimeRealizationGate
