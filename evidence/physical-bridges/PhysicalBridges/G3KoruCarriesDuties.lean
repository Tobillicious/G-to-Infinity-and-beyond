import PhysicalBridges.AllIsForwardPersistence

/-!
# The Koru carries the duties by their shape

Whole-first (Archimedes: one invariant at the whole, carried by the whole's own
evolution). The six original duties differ in logical shape, and each shape is
carried by a different level of Koru evolution:

* **Positive** (something exists — a continuation link, a lineage, a grant):
  carried by the spiral itself, every forward step (`THE_SPIRAL_CARRIES_POSITIVE_DUTIES`).
  Shape of `continues`, `provenanced`, and the grant half of `authorized`.
* **Quantifier-free, including negation** (something does not happen to this
  particular — no coercion, no overreach, no withdrawal): carried when growth
  is frontier-only, i.e. existing particulars' relations are never rewired
  (`FRONTIER_GROWTH_CARRIES_QF_DUTIES`). Shape of `free`, `restrained`, and the
  no-withdrawal half of `authorized`.
* **Quantified over all alternatives** (the best available protection):
  not carried — new possibilities can change it, so it must be re-judged as
  the world grows (`MAXIMALITY_MUST_BE_REJUDGED`). Shape of `maximal`.

Which duty has which shape, and that each is a relation of the whole, is the
definability premise; this module proves what follows from it.
-/

namespace PhysicalBridges.G3KoruCarriesDuties

open PhysicalBridges.SummitIntrinsicDefinability
open PhysicalBridges.AllIsForwardPersistence

/-- **THE SPIRAL CARRIES POSITIVE DUTIES.** Along any forward Koru history,
    every positive duty true of a particular at the origin is true of it at
    every later stage. -/
theorem THE_SPIRAL_CARRIES_POSITIVE_DUTIES (H : ForwardMicrohistory)
    {D : Type} (duty : D → PositiveFormula 1) (x : H.Position 0)
    (hOrigin : ∀ d, evalPositive (H.relation 0) (fun _ => x) (duty d)) :
    ∀ n d, evalPositive (H.relation n) (fun _ => carry H n x) (duty d) :=
  fun n d => positive_truth_at_every_stage H (duty d) x (hOrigin d) n

/-- A frontier-growth history: each step embeds the old world exactly — no
    old relation added or removed — while new particulars may appear. -/
structure FrontierHistory where
  Position : Nat → Type
  relation : (n : Nat) → Position n → Position n → Prop
  step : (n : Nat) → InducedEmbedding (relation n) (relation (n + 1))

def carryF (H : FrontierHistory) : (n : Nat) → H.Position 0 → H.Position n
  | 0, x => x
  | n + 1, x => (H.step n).to (carryF H n x)

/-- **FRONTIER GROWTH CARRIES QUANTIFIER-FREE DUTIES.** If growth never rewires
    existing particulars, every quantifier-free duty — negations included —
    holds of a particular at a later stage exactly when it held at the origin. -/
theorem FRONTIER_GROWTH_CARRIES_QF_DUTIES (H : FrontierHistory)
    (φ : RelFormula 1) (hQf : QuantifierFree φ) (x : H.Position 0) :
    ∀ n, (evalRel (H.relation 0) (fun _ => x) φ ↔
      evalRel (H.relation n) (fun _ => carryF H n x) φ)
  | 0 => Iff.rfl
  | n + 1 => (FRONTIER_GROWTH_CARRIES_QF_DUTIES H φ hQf x n).trans
      (quantifier_free_truth_invariant _ _ (H.step n) φ (fun _ => carryF H n x) hQf)

/-- **MAXIMALITY MUST BE REJUDGED** (control). Two exact boundaries: an ordinary
    forward step can falsify a negated fact (so negative duties need frontier
    growth), and even frontier growth can change a statement quantified over
    all particulars (so maximality must be re-witnessed as the world grows). -/
theorem MAXIMALITY_MUST_BE_REJUDGED :
    (evalRel emptyEdges (fun _ : Fin 1 => false) (.not_ (.related 0 0)) ∧
      ¬ evalRel addedEdges (fun _ : Fin 1 => false) (.not_ (.related 0 0))) ∧
    ¬ evalRel oldNoEdges (zeroEnvironment (P := Unit))
        (.exists_ (.related 0 0)) ∧
      evalRel newSelfEdge (zeroEnvironment (P := Bool)) (.exists_ (.related 0 0)) :=
  ⟨negated_relation_can_fail_under_forward_embedding,
   fresh_nodes_can_change_existential_first_order_truth⟩

#print axioms THE_SPIRAL_CARRIES_POSITIVE_DUTIES
#print axioms FRONTIER_GROWTH_CARRIES_QF_DUTIES
#print axioms MAXIMALITY_MUST_BE_REJUDGED

end PhysicalBridges.G3KoruCarriesDuties
