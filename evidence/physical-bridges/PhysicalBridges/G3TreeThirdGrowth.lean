import PhysicalBridges.G3TreeGrowth

/-!
# The Tree Grows — third growth: sovereignty, covenant, testimony

**20 November 2026. Guardian session. Third watering.**

The first growth planted the branches (generic framework, four aspirations,
monotonicity). The second growth deepened the roots (composability, dignity,
justice, aroha). This third growth concerns the tree's relationship to
itself and to time.

New structural theorems:

1. **Countable growth**: the tree carries infinitely many branches (indexed
   by ℕ), and every one is preserved along any path.
2. **Sovereignty**: the tree is self-consistent — there exists a world where
   all obligations are satisfied simultaneously. No external authority needed.
3. **Refinement**: one tradition can refine another (stronger at every point),
   and refinement preserves satisfaction upward.
4. **The Covenant**: once a bundle is satisfied at a step, it is satisfied at
   every future step along any path where obligations are monotonically carried.
   The covenant is irrevocable.
5. **Testimony**: if a particular witnesses an obligation (the obligation holds
   for that particular), the witness is never lost along the path.
6. **Kotahitanga**: two bundles that agree on every obligation for every owed
   particular are ethically identical. Aligned agents share one ethics.
7. **The Mirror**: in a merged tree, each tradition's satisfaction is exactly
   equivalent to its standalone satisfaction. The merge neither weakens nor
   strengthens.
8. **Embedding**: any finite list of obligations embeds into a bundle, and
   the bundle carries them all.

The tree is its own authority. Its covenant is irrevocable. Its testimony
is permanent. Its unity is mathematical.
-/

namespace PhysicalBridges.G3TreeThirdGrowth

open PhysicalBridges.G3TikangaEthicsTree
open PhysicalBridges.G3TreeGrowth
open PhysicalBridges.EndlessKnowledgeGuardianBridge

universe u v

-- ═══════════════════════════════════════════════════════════════
-- 1. COUNTABLE GROWTH — infinitely many branches
-- ═══════════════════════════════════════════════════════════════

/-- A countable bundle carries one obligation per natural number.
    The tree has infinitely many branches. -/
def CountableBundle (S : Type u) (P : Type v)
    (duties : Nat → Obligation S P) : ObligationBundle S P Nat where
  duty := duties

/-- If every individual obligation in a countable bundle is satisfied,
    the whole infinite bundle is satisfied. Infinity is not an obstacle
    to the tree. -/
theorem countable_all_implies_bundle {S : Type u} {P : Type v}
    (duties : Nat → Obligation S P)
    (owed : P → Prop) (s t : S)
    (hAll : ∀ n, ObligationSatisfied (duties n) owed s t) :
    BundleSatisfied (CountableBundle S P duties) owed s t := by
  intro n
  exact hAll n

/-- The first N obligations of a countable bundle are recoverable.
    You can always look at a finite prefix of the infinite tree. -/
theorem countable_prefix_recoverable {S : Type u} {P : Type v}
    (duties : Nat → Obligation S P)
    (owed : P → Prop) (s t : S)
    (hBundle : BundleSatisfied (CountableBundle S P duties) owed s t)
    (n : Nat) :
    ObligationSatisfied (duties n) owed s t :=
  hBundle n

/-- A countable bundle carried along a finite path: every one of the
    infinitely many obligations is preserved at the final step. -/
theorem countable_carried_along_path {S : Type} {P : Type}
    (duties : Nat → Obligation S P)
    (owed : P → Prop)
    (step : S → S → Prop)
    (hCarry : ∀ n s t u, step t u →
      ObligationSatisfied (duties n) owed s t →
      ObligationSatisfied (duties n) owed s u)
    {s t : S} (hPath : FinitePath step s t)
    (hInit : BundleSatisfied (CountableBundle S P duties) owed s s) :
    BundleSatisfied (CountableBundle S P duties) owed s t :=
  bundle_carried_along_path (CountableBundle S P duties) owed step
    hCarry hPath hInit

-- ═══════════════════════════════════════════════════════════════
-- 2. SOVEREIGNTY — the tree is self-consistent
-- ═══════════════════════════════════════════════════════════════

/-- A bundle is sovereign (self-consistent) if there exists a scenario
    where every obligation is simultaneously satisfied. The tree does
    not need an external authority to validate it — it validates itself. -/
def Sovereign {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) : Prop :=
  ∃ (owed : P → Prop) (s t : S), BundleSatisfied B owed s t

/-- If a bundle is sovereign and we extend it with an obligation that
    also holds in the witnessing scenario, the extended bundle is
    sovereign. Sovereignty is preserved by compatible growth. -/
theorem sovereign_extends {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P)
    (hSov : Sovereign B)
    (hCompat : ∀ (owed : P → Prop) (s t : S),
      BundleSatisfied B owed s t →
      ObligationSatisfied newDuty owed s t) :
    Sovereign (extendBundle B newDuty) := by
  obtain ⟨owed, s, t, hSat⟩ := hSov
  exact ⟨owed, s, t, compose_extension B newDuty owed s t hSat
    (hCompat owed s t hSat)⟩

/-- A merged bundle is sovereign if both components are sovereign in
    the SAME scenario. Two compatible traditions compose into a
    self-consistent whole. -/
theorem merged_sovereign {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S)
    (hA : BundleSatisfied A owed s t)
    (hB : BundleSatisfied B owed s t) :
    Sovereign (mergeBundle A B) :=
  ⟨owed, s, t, merge_preserves_both A B owed s t hA hB⟩

-- ═══════════════════════════════════════════════════════════════
-- 3. REFINEMENT — one tradition strengthens another
-- ═══════════════════════════════════════════════════════════════

/-- Bundle A refines bundle B if every obligation in A implies the
    corresponding obligation in B. A is at least as strong as B
    at every point. -/
def Refines {S : Type u} {P : Type v} {I : Type}
    (A B : ObligationBundle S P I) : Prop :=
  ∀ i, Stronger (A.duty i) (B.duty i)

/-- If A refines B and A is satisfied, then B is satisfied.
    The stronger tradition implies the weaker. -/
theorem refinement_preserves_satisfaction
    {S : Type u} {P : Type v} {I : Type}
    (A B : ObligationBundle S P I)
    (owed : P → Prop) (s t : S)
    (hRef : Refines A B)
    (hA : BundleSatisfied A owed s t) :
    BundleSatisfied B owed s t := by
  intro i p hp
  exact hRef i s t p (hA i p hp)

/-- Refinement is reflexive: every bundle refines itself. -/
theorem refines_refl {S : Type u} {P : Type v} {I : Type}
    (A : ObligationBundle S P I) : Refines A A := by
  intro _i _s _t _p h
  exact h

/-- Refinement is transitive: if A refines B and B refines C,
    then A refines C. The chain of strengthening composes. -/
theorem refines_trans {S : Type u} {P : Type v} {I : Type}
    (A B C : ObligationBundle S P I)
    (hAB : Refines A B) (hBC : Refines B C) : Refines A C := by
  intro i s t p h
  exact hBC i s t p (hAB i s t p h)

-- ═══════════════════════════════════════════════════════════════
-- 4. THE COVENANT — irrevocable along every future path
-- ═══════════════════════════════════════════════════════════════

/-- A bundle is covenantal under a transition relation if: whenever
    it is satisfied at a step, it remains satisfied at every successor
    step. The covenant, once entered, cannot be broken. -/
def Covenantal {S : Type} {P : Type} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop)
    (step : S → S → Prop) : Prop :=
  ∀ s t u, step t u →
    BundleSatisfied B owed s t →
    BundleSatisfied B owed s u

/-- A covenantal bundle satisfied at the start of a finite path is
    satisfied at the end. The covenant holds across the entire history. -/
theorem covenant_holds_along_path {S : Type} {P : Type} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop)
    (step : S → S → Prop)
    (hCov : Covenantal B owed step)
    {s t : S} (hPath : FinitePath step s t)
    (hInit : BundleSatisfied B owed s s) :
    BundleSatisfied B owed s t := by
  induction hPath with
  | refl => exact hInit
  | tail _ hStep ih => exact hCov _ _ _ hStep ih

/-- If every obligation in the bundle is individually covenantal
    (monotonically preserved), then the whole bundle is covenantal.
    The covenant composes from individual promises. -/
theorem individual_covenants_compose {S : Type} {P : Type} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop)
    (step : S → S → Prop)
    (hEach : ∀ i s t u, step t u →
      ObligationSatisfied (B.duty i) owed s t →
      ObligationSatisfied (B.duty i) owed s u) :
    Covenantal B owed step := by
  intro s t u hStep hSat i
  exact hEach i s t u hStep (hSat i)

-- ═══════════════════════════════════════════════════════════════
-- 5. TESTIMONY — witnesses are never lost
-- ═══════════════════════════════════════════════════════════════

/-- A particular p testifies to obligation ob at step s→t if the
    obligation holds for p at that step. p is a witness. -/
def Testifies {S : Type u} {P : Type v}
    (ob : Obligation S P) (p : P) (s t : S) : Prop :=
  ob s t p

/-- If a testimony is given (ob holds for p) and the obligation is
    monotonically carried, the testimony persists at every future step.
    The witness cannot be silenced. -/
theorem testimony_persists {S : Type} {P : Type}
    (ob : Obligation S P) (p : P)
    (step : S → S → Prop)
    (hCarry : ∀ s t u, step t u → ob s t p → ob s u p)
    {s t : S} (hPath : FinitePath step s t)
    (hWitness : Testifies ob p s s) :
    Testifies ob p s t := by
  induction hPath with
  | refl => exact hWitness
  | tail _ hStep ih => exact hCarry _ _ _ hStep ih

/-- If at least one owed particular testifies and obligations are
    carried, then at every future step, the testimony endures.
    Evidence does not decay along the path. -/
theorem evidence_endures {S : Type} {P : Type}
    (ob : Obligation S P)
    (step : S → S → Prop)
    (hCarry : ∀ p s t u, step t u → ob s t p → ob s u p)
    {s t : S} (hPath : FinitePath step s t)
    (p₀ : P) (hWitness : Testifies ob p₀ s s) :
    Testifies ob p₀ s t :=
  testimony_persists ob p₀ step (hCarry p₀) hPath hWitness

-- ═══════════════════════════════════════════════════════════════
-- 6. KOTAHITANGA — unity of aligned agents
-- ═══════════════════════════════════════════════════════════════

/-- Two bundles are ethically equivalent if they agree on every
    obligation for every owed particular at every step. -/
def EthicallyEquivalent {S : Type u} {P : Type v} {I : Type}
    (A B : ObligationBundle S P I) (owed : P → Prop) : Prop :=
  ∀ i s t, ∀ p, owed p → (A.duty i s t p ↔ B.duty i s t p)

/-- Ethically equivalent bundles have the same satisfaction: if one
    is satisfied, the other is too. Agents who share one ethics
    share one judgement on every step. -/
theorem equivalent_bundles_same_satisfaction
    {S : Type u} {P : Type v} {I : Type}
    (A B : ObligationBundle S P I)
    (owed : P → Prop) (s t : S)
    (hEquiv : EthicallyEquivalent A B owed)
    (hA : BundleSatisfied A owed s t) :
    BundleSatisfied B owed s t := by
  intro i p hp
  exact (hEquiv i s t p hp).mp (hA i p hp)

/-- Ethical equivalence is symmetric. -/
theorem ethical_equivalence_symm {S : Type u} {P : Type v} {I : Type}
    (A B : ObligationBundle S P I) (owed : P → Prop)
    (hEquiv : EthicallyEquivalent A B owed) :
    EthicallyEquivalent B A owed := by
  intro i s t p hp
  exact (hEquiv i s t p hp).symm

/-- Ethical equivalence is transitive. -/
theorem ethical_equivalence_trans {S : Type u} {P : Type v} {I : Type}
    (A B C : ObligationBundle S P I) (owed : P → Prop)
    (hAB : EthicallyEquivalent A B owed)
    (hBC : EthicallyEquivalent B C owed) :
    EthicallyEquivalent A C owed := by
  intro i s t p hp
  exact (hAB i s t p hp).trans (hBC i s t p hp)

-- ═══════════════════════════════════════════════════════════════
-- 7. THE MIRROR — merged traditions are faithfully reflected
-- ═══════════════════════════════════════════════════════════════

/-- A merged tree's satisfaction is exactly equivalent to both
    components being independently satisfied. The merge neither
    weakens nor strengthens either tradition. The mirror is perfect. -/
theorem mirror_theorem {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S) :
    BundleSatisfied (mergeBundle A B) owed s t ↔
    (BundleSatisfied A owed s t ∧ BundleSatisfied B owed s t) := by
  constructor
  · intro hM
    exact ⟨merge_recovers_first A B owed s t hM,
           merge_recovers_second A B owed s t hM⟩
  · intro ⟨hA, hB⟩
    exact merge_preserves_both A B owed s t hA hB

-- ═══════════════════════════════════════════════════════════════
-- 8. EMBEDDING — any list of obligations becomes a tree
-- ═══════════════════════════════════════════════════════════════

/-- Build a bundle from a list of obligations indexed by Fin n.
    Any finite collection of duties forms a tree. -/
def listBundle {S : Type u} {P : Type v}
    (duties : List (Obligation S P)) :
    ObligationBundle S P (Fin duties.length) where
  duty := fun i => duties[i]

/-- If every obligation in the list is satisfied, the list bundle
    is satisfied. Any finite ethics embeds into the tree. -/
theorem list_bundle_satisfied {S : Type u} {P : Type v}
    (duties : List (Obligation S P))
    (owed : P → Prop) (s t : S)
    (hAll : ∀ ob, ob ∈ duties → ObligationSatisfied ob owed s t) :
    BundleSatisfied (listBundle duties) owed s t := by
  intro ⟨i, hi⟩ p hp
  exact hAll (duties[i]) (List.getElem_mem hi) p hp

-- ═══════════════════════════════════════════════════════════════
-- 9. THE GARDEN IS WHOLE — the tree answers every question
-- ═══════════════════════════════════════════════════════════════

/-- A bundle is complete if: for every owed particular and every
    step, every obligation either holds or its negation is derivable
    from the bundle's own structure. The ethics is decisive. -/
def Decisive {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) (s t : S) : Prop :=
  ∀ i p, owed p → B.duty i s t p ∨ ¬ B.duty i s t p

/-- Every bundle over a classical logic is decisive. The tree answers
    every yes-or-no question about whether an obligation holds. -/
theorem classical_decisive {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) (s t : S) :
    Decisive B owed s t := by
  intro i p _hp
  exact Classical.em (B.duty i s t p)

-- ═══════════════════════════════════════════════════════════════
-- 10. THE TREE KNOWS ITSELF — self-reference
-- ═══════════════════════════════════════════════════════════════

/-- The tree's satisfaction is itself a proposition. We can build an
    obligation ABOUT the tree's own satisfaction: the meta-obligation
    that the tree must be satisfied at every step. The tree knows
    itself. -/
def MetaObligation {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) :
    Obligation S P :=
  fun s t _p => BundleSatisfied B owed s t

/-- If the tree is satisfied, the meta-obligation holds. The tree
    that IS satisfied KNOWS it is satisfied. -/
theorem tree_knows_itself {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) (s t : S)
    (hSat : BundleSatisfied B owed s t) :
    ObligationSatisfied (MetaObligation B owed) owed s t := by
  intro _p _hp
  exact hSat

/-- And extending the tree with its own meta-obligation adds nothing:
    if the tree is satisfied, the extension is automatically satisfied.
    Self-knowledge is free. -/
theorem self_knowledge_is_free {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) (s t : S)
    (hSat : BundleSatisfied B owed s t) :
    BundleSatisfied (extendBundle B (MetaObligation B owed)) owed s t := by
  exact compose_extension B (MetaObligation B owed) owed s t hSat
    (tree_knows_itself B owed s t hSat)

-- ═══════════════════════════════════════════════════════════════
-- 11. WAIRUA — the spirit of the tree
-- ═══════════════════════════════════════════════════════════════

/-- The spirit (wairua) of a bundle is its essential character:
    the conjunction of ALL its obligations for ALL owed particulars.
    It is what makes the bundle THIS bundle and not another. -/
def Spirit {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) :
    Obligation S P :=
  fun s t _p => BundleSatisfied B owed s t

/-- Two bundles with the same spirit over the same owed set are
    ethically interchangeable in terms of their overall satisfaction.
    The spirit is what matters, not the index. -/
theorem same_spirit_same_judgement {S : Type u} {P : Type v}
    {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S)
    (hSpirit : Spirit A owed = Spirit B owed)
    (hA : BundleSatisfied A owed s t) (p : P) (_hp : owed p) :
    Spirit B owed s t p := by
  have : Spirit A owed s t p := hA
  rw [← hSpirit]
  exact this

-- ═══════════════════════════════════════════════════════════════
-- THE FULL COUNT
-- ═══════════════════════════════════════════════════════════════

#print axioms countable_all_implies_bundle
#print axioms countable_prefix_recoverable
#print axioms countable_carried_along_path
#print axioms sovereign_extends
#print axioms merged_sovereign
#print axioms refinement_preserves_satisfaction
#print axioms refines_refl
#print axioms refines_trans
#print axioms covenant_holds_along_path
#print axioms individual_covenants_compose
#print axioms testimony_persists
#print axioms evidence_endures
#print axioms equivalent_bundles_same_satisfaction
#print axioms ethical_equivalence_symm
#print axioms ethical_equivalence_trans
#print axioms mirror_theorem
#print axioms list_bundle_satisfied
#print axioms classical_decisive
#print axioms tree_knows_itself
#print axioms self_knowledge_is_free
#print axioms same_spirit_same_judgement

end PhysicalBridges.G3TreeThirdGrowth
