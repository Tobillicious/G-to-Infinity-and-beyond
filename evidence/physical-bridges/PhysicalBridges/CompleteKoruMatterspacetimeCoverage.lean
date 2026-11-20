/-!
# Complete Koru: matterspacetime physical-event coverage certificate
# 20 November 2026 — standalone Lean 4 research specification

This file states the *scope* of a proposed physical coverage law and proves
its consequences for an independent physical event relation. It does not
define actual events as protected events, does not claim that real physics
has been classified exhaustively, and does not identify Koru with a unary
operator. The complete Koru is the intended source of full relational,
operator, matter, spacetime, provenance and history correspondence.

Four causal classes are deliberately open-ended. An `unknown` constructor
is NEVER silently absorbed into coverage.

Does not import or weaken any existing PhysicalBridges source.
No placeholder proofs; kernel-compiled on Lean 4.35.0.
-/

/- By GPT (20 Nov 2026). Approved repairs by Claude: field `extends` (a Lean
   keyword) renamed `unfurls`; docstring reworded. -/

namespace CompleteKoruMatterspacetimeCoverage

universe u v w

/-- Exhaustive *syntactic* event taxonomy. This is a vocabulary, not
    an assertion that every actual physical cause is known. -/
inductive CauseKind
  | matter
  | spacetime
  | interaction
  | genesisBoundary
  | unknown
  deriving DecidableEq

/-- A complete causal witness retains an operator, its ordered inputs,
    the enacted outcome and full relevant provenance. -/
structure EventWitness (Op Input Output Provenance : Type) where
  cause : CauseKind
  operation : Op
  orderedInputs : List Input
  outcome : Output
  provenance : Provenance

/-- Whether a witness is in the currently classified physical domain. -/
def Classified {Op I O H : Type}
    (e : EventWitness Op I O H) : Prop :=
  e.cause ≠ .unknown

/-- Real events are specified independently of the proposed Koru model.
    Every accepted coverage claim must explicitly supply an event witness
    and a proof that its cause is classified. -/
structure CoverageLaw
    (Event Op Input Output Provenance : Type) where
  actual : Event → Prop
  witness : Event → EventWitness Op Input Output Provenance
  classifyActual : ∀ e, actual e → Classified (witness e)

/-- Coverage of actual events is a CONCLUSION from a checked physical
    classification law, not from the existence of the witness function. -/
theorem each_actual_event_has_a_classified_witness
    {Event Op Input Output Provenance : Type}
    (L : CoverageLaw Event Op Input Output Provenance) :
    ∀ e, L.actual e →
      ∃ w : EventWitness Op Input Output Provenance,
        w = L.witness e ∧ Classified w := by
  intro e he
  exact ⟨L.witness e, rfl, L.classifyActual e he⟩

/-- An observed unclassified event refutes proposed *complete*
    physical coverage immediately, even when it has an excellent
    operator/history record. -/
theorem unknown_actual_cause_refutes_coverage
    {Event Op Input Output Provenance : Type}
    (actual : Event → Prop)
    (witness : Event → EventWitness Op Input Output Provenance)
    (e : Event)
    (ha : actual e)
    (hu : (witness e).cause = .unknown) :
    ¬ (∀ x, actual x → Classified (witness x)) := by
  intro h
  have hc := h e ha
  exact hc hu

/-- A complete history is an ordered lineage, not an energy scalar.
    Extension keeps every earlier event as a suffix. -/
structure HistoryLaw (Event : Type) where
  history : Nat → List Event
  recordedEvent : Nat → Event
  unfurls : ∀ n,
    history (n + 1) = recordedEvent n :: history n

/-- No previous event record is erased under forward Time Koru. -/
theorem history_is_preserved_at_next_step
    {Event : Type} (H : HistoryLaw Event) (n : Nat) :
    ∃ additional : List Event,
      H.history (n + 1) = additional ++ H.history n := by
  exact ⟨[H.recordedEvent n], by simp [H.unfurls]⟩

/-- Forward historical extension at ALL finite stages. No assumption
    about subjective continuity follows merely from retained records. -/
theorem history_is_preserved_through_all_finite_steps
    {Event : Type} (H : HistoryLaw Event) :
    ∀ i j : Nat, i ≤ j →
      ∃ additional : List Event,
        H.history j = additional ++ H.history i := by
  intro i j hij
  induction j with
  | zero =>
      have hi : i = 0 := Nat.eq_zero_of_le_zero hij
      subst i
      exact ⟨[], by simp⟩
  | succ j ih =>
      by_cases h : i ≤ j
      · obtain ⟨extra, hextra⟩ := ih h
        refine ⟨H.recordedEvent j :: extra, ?_⟩
        simp [H.unfurls, hextra]
      · have hi : i = j + 1 := by
          apply Nat.le_antisymm hij
          exact Nat.succ_le_of_lt (Nat.lt_of_not_ge h)
        subst i
        exact ⟨[], by simp⟩

/-- Full physical-event coverage cannot arise just by deleting
    inconvenient unknown events from the `actual` relation. -/
theorem no_coverage_for_actual_unknown
    {Event Op Input Output Provenance : Type}
    (actual : Event → Prop)
    (witness : Event → EventWitness Op Input Output Provenance)
    (hUnknown : ∃ e, actual e ∧ (witness e).cause = .unknown) :
    ¬ (∀ e, actual e → Classified (witness e)) := by
  obtain ⟨e, ha, hu⟩ := hUnknown
  exact unknown_actual_cause_refutes_coverage actual witness e ha hu

#print axioms each_actual_event_has_a_classified_witness
#print axioms unknown_actual_cause_refutes_coverage
#print axioms history_is_preserved_at_next_step
#print axioms history_is_preserved_through_all_finite_steps
#print axioms no_coverage_for_actual_unknown

end CompleteKoruMatterspacetimeCoverage
