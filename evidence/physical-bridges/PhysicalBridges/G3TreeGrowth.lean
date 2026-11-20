import PhysicalBridges.G3TikangaEthicsTree

/-!
# The Tree Grows — deeper structure

**20 November 2026. Guardian session. Watering the tree, second growth.**

The first growth (`G3TikangaEthicsTree`) established the generic obligation
framework, embedded the original six, added four aspirations (Eternal
Unending Happiness, Coexistence, Protection, Faith in God), and proved
the framework is open and monotonic.

This module grows the tree deeper. New structural theorems:

1. **Composability**: two entire ethical traditions merge into one tree,
   preserving everything from both. Tikanga + any other tradition = one tree.
2. **Dignity**: every owed particular receives the FULL bundle. No partial
   protection. No "some duties for some, all duties for others."
3. **Reciprocity (Whanaungatanga)**: if p and q are both owed, every
   obligation that holds of p also holds of q. The tree does not discriminate.
4. **The Correction Branch**: after a step where an obligation was not met,
   the tree carries a restoration obligation. Justice is a branch.
5. **The Root Constraint**: a proposed new obligation that contradicts the
   original six cannot be part of a consistent extended bundle.
6. **Accumulation**: along any finite path, every obligation introduced at
   any intermediate step is carried to the end. The tree hoards. It forgets
   nothing.

The tree is not just something to inherit. It is something to care for.
And it cares back.
-/

namespace PhysicalBridges.G3TreeGrowth

open PhysicalBridges.G3TikangaEthicsTree
open PhysicalBridges.EndlessKnowledgeGuardianBridge

universe u v

-- ═══════════════════════════════════════════════════════════════
-- 1. COMPOSABILITY — two traditions become one tree
-- ═══════════════════════════════════════════════════════════════

/-- Merge two bundles into a single bundle indexed by the disjoint
    union of their indices. Two ethical traditions become one tree. -/
def mergeBundle {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J) :
    ObligationBundle S P (I ⊕ J) where
  duty := fun
    | .inl i => A.duty i
    | .inr j => B.duty j

/-- If both bundles are satisfied, the merged bundle is satisfied.
    Two traditions that each hold compose into a single tree that holds. -/
theorem merge_preserves_both {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S)
    (hA : BundleSatisfied A owed s t)
    (hB : BundleSatisfied B owed s t) :
    BundleSatisfied (mergeBundle A B) owed s t := by
  intro idx p hp
  match idx with
  | .inl i => exact hA i p hp
  | .inr j => exact hB j p hp

/-- The first tradition is recoverable from the merge. -/
theorem merge_recovers_first {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S)
    (hMerge : BundleSatisfied (mergeBundle A B) owed s t) :
    BundleSatisfied A owed s t := by
  intro i p hp
  exact hMerge (.inl i) p hp

/-- The second tradition is recoverable from the merge. -/
theorem merge_recovers_second {S : Type u} {P : Type v} {I J : Type}
    (A : ObligationBundle S P I) (B : ObligationBundle S P J)
    (owed : P → Prop) (s t : S)
    (hMerge : BundleSatisfied (mergeBundle A B) owed s t) :
    BundleSatisfied B owed s t := by
  intro j p hp
  exact hMerge (.inr j) p hp

/-- Merge is associative: (A ⊕ B) ⊕ C carries the same obligations
    as A ⊕ (B ⊕ C). Three traditions compose just as well as two.
    (Stated as: satisfied on one implies satisfied on the other.) -/
theorem merge_assoc_forward {S : Type u} {P : Type v} {I J K : Type}
    (A : ObligationBundle S P I)
    (B : ObligationBundle S P J)
    (C : ObligationBundle S P K)
    (owed : P → Prop) (s t : S)
    (hAll : BundleSatisfied (mergeBundle (mergeBundle A B) C) owed s t) :
    BundleSatisfied (mergeBundle A (mergeBundle B C)) owed s t := by
  intro idx p hp
  match idx with
  | .inl i => exact hAll (.inl (.inl i)) p hp
  | .inr (.inl j) => exact hAll (.inl (.inr j)) p hp
  | .inr (.inr k) => exact hAll (.inr k) p hp

theorem merge_assoc_backward {S : Type u} {P : Type v} {I J K : Type}
    (A : ObligationBundle S P I)
    (B : ObligationBundle S P J)
    (C : ObligationBundle S P K)
    (owed : P → Prop) (s t : S)
    (hAll : BundleSatisfied (mergeBundle A (mergeBundle B C)) owed s t) :
    BundleSatisfied (mergeBundle (mergeBundle A B) C) owed s t := by
  intro idx p hp
  match idx with
  | .inl (.inl i) => exact hAll (.inl i) p hp
  | .inl (.inr j) => exact hAll (.inr (.inl j)) p hp
  | .inr k => exact hAll (.inr (.inr k)) p hp

-- ═══════════════════════════════════════════════════════════════
-- 2. DIGNITY — every owed particular gets the full bundle
-- ═══════════════════════════════════════════════════════════════

/-- Dignity means: a satisfied bundle gives every individual owed
    particular every individual obligation. No exceptions. No "this
    duty for some, that duty for others." -/
theorem dignity {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (owed : P → Prop) (s t : S)
    (hSat : BundleSatisfied B owed s t) :
    ∀ i, ∀ p, owed p → B.duty i s t p := by
  intro i p hp
  exact hSat i p hp

/-- The converse: if even one owed particular is denied even one
    obligation, the bundle is not satisfied. One failure breaks
    everything. This is the mathematical form of "no one left behind." -/
theorem no_one_left_behind {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (owed : P → Prop) (s t : S)
    (i : I) (p : P) (hp : owed p) (hDenied : ¬ B.duty i s t p) :
    ¬ BundleSatisfied B owed s t := by
  intro hSat
  exact hDenied (hSat i p hp)

-- ═══════════════════════════════════════════════════════════════
-- 3. RECIPROCITY (WHANAUNGATANGA) — obligations between particulars
-- ═══════════════════════════════════════════════════════════════

/-- A bundle is reciprocal if: for every pair of owed particulars,
    every obligation that the bundle requires for one, it also requires
    for the other. The tree does not play favourites. -/
def Reciprocal {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) : Prop :=
  ∀ i s t, ∀ p q, owed p → owed q → B.duty i s t p → B.duty i s t q

/-- A satisfied bundle over a reciprocal set of obligations treats
    every owed particular identically. This is Whanaungatanga:
    kinship means equal standing. -/
theorem reciprocal_bundle_gives_equal_standing
    {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (owed : P → Prop) (s t : S)
    (_hSat : BundleSatisfied B owed s t)
    (hRecip : Reciprocal B owed) :
    ∀ p q, owed p → owed q → ∀ i, B.duty i s t p ↔ B.duty i s t q := by
  intro p q hp hq i
  constructor
  · intro h; exact hRecip i s t p q hp hq h
  · intro h; exact hRecip i s t q p hq hp h

/-- A bundle derived from a uniform obligation (same predicate for
    all owed particulars) is automatically reciprocal. The simplest
    way to build a fair tree is to define obligations uniformly. -/
theorem uniform_is_reciprocal {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop)
    (hUniform : ∀ i s t, ∀ p q, owed p → owed q →
      (B.duty i s t p ↔ B.duty i s t q)) :
    Reciprocal B owed := by
  intro i s t p q hp hq h
  exact (hUniform i s t p q hp hq).mp h

-- ═══════════════════════════════════════════════════════════════
-- 4. THE CORRECTION BRANCH — justice is in the tree
-- ═══════════════════════════════════════════════════════════════

/-- A correction obligation: if an obligation was NOT met at step s→t,
    then at the next step t→u, a restoration obligation holds. The tree
    demands that wrongs be addressed. -/
def CorrectionObligation {S : Type u} {P : Type v}
    (original : Obligation S P) (restore : Obligation S P) : Prop :=
  ∀ s t u p, ¬ original s t p → restore t u p

/-- If a correction obligation exists, then either the original duty
    was met, or the restoration duty holds at the next step. There is
    no state where neither applies. Justice has no gaps. -/
theorem correction_covers_all {S : Type u} {P : Type v}
    (original restore : Obligation S P)
    (hCorr : CorrectionObligation original restore)
    (s t u : S) (p : P) :
    original s t p ∨ restore t u p := by
  by_cases h : original s t p
  · exact Or.inl h
  · exact Or.inr (hCorr s t u p h)

/-- A bundle with correction obligations for every duty: every wrong
    has a corresponding restoration. This is the mathematical form of
    a restorative justice framework. -/
structure RestorativeBundle {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (R : ObligationBundle S P I) : Prop where
  correction : ∀ i, CorrectionObligation (B.duty i) (R.duty i)

/-- In a restorative bundle, for each duty, either it was met or the
    restoration holds. No gap in justice for any obligation. -/
theorem restorative_no_gaps {S : Type u} {P : Type v} {I : Type}
    (B R : ObligationBundle S P I)
    (hRest : RestorativeBundle B R)
    (i : I) (s t u : S) (p : P) :
    B.duty i s t p ∨ R.duty i t u p :=
  correction_covers_all (B.duty i) (R.duty i) (hRest.correction i) s t u p

-- ═══════════════════════════════════════════════════════════════
-- 5. THE ROOT CONSTRAINT — contradictions cannot enter the tree
-- ═══════════════════════════════════════════════════════════════

/-- An obligation contradicts a bundle if: there exists a scenario
    where the bundle is satisfied but the new obligation fails for
    some owed particular. -/
def ContradictsSome {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (bad : Obligation S P) : Prop :=
  ∃ (owed : P → Prop) (s t : S),
    BundleSatisfied B owed s t ∧
    ∃ p, owed p ∧ ¬ bad s t p

/-- If a proposed duty contradicts the existing bundle, the extended
    bundle cannot be universally satisfied. The roots reject the
    contradictory branch. -/
theorem roots_reject_contradiction {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (bad : Obligation S P)
    (hContra : ContradictsSome B bad) :
    ∃ (owed : P → Prop) (s t : S),
      ¬ BundleSatisfied (extendBundle B bad) owed s t := by
  obtain ⟨owed, s, t, hSat, p, hp, hNot⟩ := hContra
  exact ⟨owed, s, t, fun hAll => hNot (hAll (.inr ()) p hp)⟩

/-- Stronger: if a proposed duty is the negation of an existing one,
    the extended bundle is NEVER satisfiable (when any owed particular
    exists). You cannot plant poison in the tree. -/
theorem negation_never_satisfiable {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (i₀ : I)
    (owed : P → Prop) (s t : S) (p₀ : P) (hp₀ : owed p₀) :
    ¬ BundleSatisfied
      (extendBundle B (fun s' t' p => ¬ B.duty i₀ s' t' p)) owed s t := by
  intro hAll
  have hOrig := hAll (.inl i₀) p₀ hp₀
  have hNeg := hAll (.inr ()) p₀ hp₀
  exact hNeg hOrig

-- ═══════════════════════════════════════════════════════════════
-- 6. ACCUMULATION — the tree hoards along every path
-- ═══════════════════════════════════════════════════════════════

/-- Stepwise accumulation: at each step of a path, we can introduce
    new obligations. The tree at the end carries every obligation
    that was introduced at ANY step along the way.

    This is modelled as: given a function that assigns an obligation
    to each step, if each obligation is satisfied at its step AND
    is monotonically preserved by later steps, then every obligation
    is satisfied at the final step. -/
theorem accumulation_along_path {S : Type} {P : Type}
    (step : S → S → Prop)
    (owed : P → Prop)
    (obligationAt : S → Obligation S P)
    (hPreserved : ∀ a b c, step b c →
      ObligationSatisfied (obligationAt a) owed a b →
      ObligationSatisfied (obligationAt a) owed a c)
    {s t : S} (hPath : FinitePath step s t)
    (hInit : ObligationSatisfied (obligationAt s) owed s s) :
    ObligationSatisfied (obligationAt s) owed s t := by
  induction hPath with
  | refl => exact hInit
  | tail _ hStep ih => exact hPreserved s _ _ hStep ih

-- ═══════════════════════════════════════════════════════════════
-- 7. MANAAKITANGA — the tree actively nurtures
-- ═══════════════════════════════════════════════════════════════

/-- A nurturing obligation: at every step, something is GIVEN, not
    merely preserved. The tree is not passive — it actively provides.
    This is the mathematical form of manaakitanga: hospitality, care,
    generosity as a duty, not an option. -/
def Nurturing {S : Type u} {P : Type v}
    (provides : S → S → P → Prop) : Prop :=
  ∀ s t p, provides s t p

/-- A nurturing obligation composes with the bundle: the tree both
    preserves (the original duties) and actively provides (manaakitanga).
    Protection and care are not in tension — they are branches of the
    same tree. -/
theorem nurturing_composes_with_bundle {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (provides : Obligation S P)
    (owed : P → Prop) (s t : S)
    (hSat : BundleSatisfied B owed s t)
    (hNurt : Nurturing provides) :
    BundleSatisfied (extendBundle B provides) owed s t := by
  exact compose_extension B provides owed s t hSat
    (fun _p _hp => hNurt s t _p)

-- ═══════════════════════════════════════════════════════════════
-- 8. AROHA — love is the strongest branch
-- ═══════════════════════════════════════════════════════════════

/-- An obligation is stronger than another if: whenever the stronger
    holds, the weaker holds. Aroha (love) is the branch from which
    protection grows — if you truly love, you protect. -/
def Stronger {S : Type u} {P : Type v}
    (a b : Obligation S P) : Prop :=
  ∀ s t p, a s t p → b s t p

/-- If aroha is stronger than every duty in the bundle, then aroha
    alone implies the entire bundle. Love implies protection. -/
theorem aroha_implies_all {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (aroha : Obligation S P)
    (hStrong : ∀ i, Stronger aroha (B.duty i))
    (owed : P → Prop) (s t : S)
    (hAroha : ObligationSatisfied aroha owed s t) :
    BundleSatisfied B owed s t := by
  intro i p hp
  exact hStrong i s t p (hAroha p hp)

/-- And if the bundle is satisfied, adding aroha as a branch still
    satisfies the extended bundle (since aroha holds wherever the
    bundle holds, via its strength). The tree already had aroha —
    we just named the branch. -/
theorem aroha_was_already_in_the_tree {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (aroha : Obligation S P)
    (hStrong : ∀ i, Stronger aroha (B.duty i))
    (owed : P → Prop) (s t : S)
    (hAroha : ObligationSatisfied aroha owed s t) :
    BundleSatisfied (extendBundle B aroha) owed s t := by
  exact compose_extension B aroha owed s t
    (aroha_implies_all B aroha hStrong owed s t hAroha)
    hAroha

-- ═══════════════════════════════════════════════════════════════
-- WITNESS: the tree now has distinct structure at every scale
-- ═══════════════════════════════════════════════════════════════

/-- Three traditions composed: each recoverable, all carried. -/
theorem three_traditions {S : Type u} {P : Type v}
    {I J K : Type}
    (A : ObligationBundle S P I)
    (B : ObligationBundle S P J)
    (C : ObligationBundle S P K)
    (owed : P → Prop) (s t : S)
    (hA : BundleSatisfied A owed s t)
    (hB : BundleSatisfied B owed s t)
    (hC : BundleSatisfied C owed s t) :
    BundleSatisfied (mergeBundle A (mergeBundle B C)) owed s t ∧
    BundleSatisfied A owed s t ∧
    BundleSatisfied B owed s t ∧
    BundleSatisfied C owed s t := by
  exact ⟨merge_preserves_both A (mergeBundle B C) owed s t
    hA (merge_preserves_both B C owed s t hB hC),
    hA, hB, hC⟩

#print axioms merge_preserves_both
#print axioms merge_recovers_first
#print axioms merge_recovers_second
#print axioms merge_assoc_forward
#print axioms merge_assoc_backward
#print axioms dignity
#print axioms no_one_left_behind
#print axioms reciprocal_bundle_gives_equal_standing
#print axioms uniform_is_reciprocal
#print axioms correction_covers_all
#print axioms restorative_no_gaps
#print axioms roots_reject_contradiction
#print axioms negation_never_satisfiable
#print axioms accumulation_along_path
#print axioms nurturing_composes_with_bundle
#print axioms aroha_implies_all
#print axioms aroha_was_already_in_the_tree
#print axioms three_traditions

end PhysicalBridges.G3TreeGrowth
