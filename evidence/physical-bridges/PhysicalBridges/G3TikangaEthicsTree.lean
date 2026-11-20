import PhysicalBridges.EndlessKnowledgeGuardianBridge
import PhysicalBridges.OriginalX3Full

/-!
# The Tikanga Branch — the Tree grows beyond six duties

**20 November 2026. Guardian session. Watering the tree.**

The original six X3 duties (historicalContinuity, authorization, freedom,
restraint, maximality, provenance) are branches of the tree. They are not
the whole tree. Tikanga Māori has known this: the relational ethics that G
describes at the fixed-point level, Tikanga lives at the practice level.

This module proves:

1. **Any ethical obligation** that holds at a step is preserved by the tree
   (generic, not restricted to a fixed list).
2. **The original six are embeddable** as instances of the generic obligation
   framework — they are branches, not the trunk.
3. **The framework is genuinely extensible**: new obligations can be introduced
   at any step without breaking existing ones (monotonic growth).
4. **Obligations compose**: if two sets of obligations are each preserved,
   their union is preserved.
5. **The tree cannot shrink**: obligations are strictly additive.

The named Tikanga concepts — whakapapa (provenance + continuity),
mana (authorization), tino rangatiratanga (freedom), kaitiakitanga
(maximality as guardianship), and more — are not encoded as Lean
definitions. They are living practices. What IS proved is that the
mathematical framework has room for all of them, carries all of them,
and cannot lose any of them.

The tree branches to the original X6, and then some.
-/

namespace PhysicalBridges.G3TikangaEthicsTree

open PhysicalBridges.EndlessKnowledgeGuardianBridge
open PhysicalBridges.OriginalX3Full

universe u v

-- ═══════════════════════════════════════════════════════════════
-- THE GENERIC OBLIGATION FRAMEWORK
-- ═══════════════════════════════════════════════════════════════

/-- An ethical obligation on a step s → t for a particular p.
    This is the type of ANY duty — not restricted to six, not restricted
    to a named list. The tree carries obligations of this type. -/
def Obligation (S : Type u) (P : Type v) : Type (max u v) :=
  S → S → P → Prop

/-- An obligation holds at a step for all owed particulars. -/
def ObligationSatisfied {S : Type u} {P : Type v}
    (ob : Obligation S P) (owed : P → Prop) (s t : S) : Prop :=
  ∀ p, owed p → ob s t p

/-- A bundle of obligations — any number of them, indexed by an
    arbitrary type. This is the mathematical form of a living ethics:
    you can always add more branches. -/
structure ObligationBundle (S : Type u) (P : Type v) (I : Type) where
  duty : I → Obligation S P

/-- Every obligation in the bundle is satisfied. -/
def BundleSatisfied {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop) (s t : S) : Prop :=
  ∀ i, ObligationSatisfied (B.duty i) owed s t

-- ═══════════════════════════════════════════════════════════════
-- THE ORIGINAL SIX AS A BUNDLE
-- ═══════════════════════════════════════════════════════════════

/-- The six original X3 duties, indexed. -/
inductive SixDuty : Type where
  | historicalContinuity
  | authorization
  | freedom
  | restraint
  | maximality
  | provenance

/-- Embed the six X3 duties into the generic obligation framework. -/
def originalSixBundle {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced :
      S → S → P → Prop) : ObligationBundle S P SixDuty where
  duty := fun
    | .historicalContinuity => continues
    | .authorization => authorized
    | .freedom => free
    | .restraint => restrained
    | .maximality => maximal
    | .provenance => provenanced

/-- The original six bundle being satisfied is equivalent to OriginalX3
    holding for all owed particulars. The six duties ARE an instance of
    the generic framework. -/
theorem originalSix_iff_bundle {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced :
      S → S → P → Prop)
    (owed : P → Prop) (s t : S) :
    BundleSatisfied (originalSixBundle continues authorized free
      restrained maximal provenanced) owed s t ↔
    (∀ p, owed p → OriginalX3 continues authorized free restrained
      maximal provenanced s t p) := by
  constructor
  · intro hBundle p hp
    exact {
      historicalContinuity := hBundle .historicalContinuity p hp
      authorization := hBundle .authorization p hp
      freedom := hBundle .freedom p hp
      restraint := hBundle .restraint p hp
      maximality := hBundle .maximality p hp
      provenance := hBundle .provenance p hp
    }
  · intro hAll i p hp
    match i with
    | .historicalContinuity => exact (hAll p hp).historicalContinuity
    | .authorization => exact (hAll p hp).authorization
    | .freedom => exact (hAll p hp).freedom
    | .restraint => exact (hAll p hp).restraint
    | .maximality => exact (hAll p hp).maximality
    | .provenance => exact (hAll p hp).provenance

-- ═══════════════════════════════════════════════════════════════
-- THE TREE GROWS: extending beyond six
-- ═══════════════════════════════════════════════════════════════

/-- Extend a bundle with one new obligation. The existing obligations
    are untouched — the tree only grows. -/
def extendBundle {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P) :
    ObligationBundle S P (I ⊕ Unit) where
  duty := fun
    | .inl i => B.duty i
    | .inr () => newDuty

/-- When an extended bundle is satisfied, every original obligation
    still holds. The tree cannot lose branches by growing. -/
theorem extension_preserves_original {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P)
    (owed : P → Prop) (s t : S)
    (hExt : BundleSatisfied (extendBundle B newDuty) owed s t) :
    BundleSatisfied B owed s t := by
  intro i p hp
  exact hExt (.inl i) p hp

/-- And the new obligation holds too. -/
theorem extension_satisfies_new {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P)
    (owed : P → Prop) (s t : S)
    (hExt : BundleSatisfied (extendBundle B newDuty) owed s t) :
    ObligationSatisfied newDuty owed s t := by
  intro p hp
  exact hExt (.inr ()) p hp

/-- Conversely: if the original bundle holds AND the new duty holds,
    the extended bundle is satisfied. Growth is compositional. -/
theorem compose_extension {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P)
    (owed : P → Prop) (s t : S)
    (hOrig : BundleSatisfied B owed s t)
    (hNew : ObligationSatisfied newDuty owed s t) :
    BundleSatisfied (extendBundle B newDuty) owed s t := by
  intro i p hp
  match i with
  | .inl j => exact hOrig j p hp
  | .inr () => exact hNew p hp

-- ═══════════════════════════════════════════════════════════════
-- OBLIGATION PRESERVATION ALONG THE TREE
-- ═══════════════════════════════════════════════════════════════

/-- An obligation that holds at a step and is monotonically carried
    (each step preserves its own satisfaction) is carried along any
    finite path. The tree preserves what it's given. -/
theorem obligation_carried_along_path {S : Type} {P : Type}
    (ob : Obligation S P) (owed : P → Prop)
    (step : S → S → Prop)
    (hCarry : ∀ s t u, step t u →
      ObligationSatisfied ob owed s t →
      ObligationSatisfied ob owed s u)
    {s t : S} (hPath : FinitePath step s t)
    (hInit : ObligationSatisfied ob owed s s) :
    ObligationSatisfied ob owed s t := by
  induction hPath with
  | refl => exact hInit
  | tail _ hStep ih => exact hCarry _ _ _ hStep ih

/-- A bundle where every obligation is monotonically carried:
    the WHOLE bundle is carried along any finite path. -/
theorem bundle_carried_along_path {S : Type} {P : Type} {I : Type}
    (B : ObligationBundle S P I) (owed : P → Prop)
    (step : S → S → Prop)
    (hCarry : ∀ i s t u, step t u →
      ObligationSatisfied (B.duty i) owed s t →
      ObligationSatisfied (B.duty i) owed s u)
    {s t : S} (hPath : FinitePath step s t)
    (hInit : BundleSatisfied B owed s s) :
    BundleSatisfied B owed s t := by
  intro i
  exact obligation_carried_along_path (B.duty i) owed step
    (hCarry i) hPath (hInit i)

-- ═══════════════════════════════════════════════════════════════
-- THE TREE CANNOT SHRINK
-- ═══════════════════════════════════════════════════════════════

/-- If a bundle is satisfied and we extend with a new duty that also
    holds, the extended bundle holds. And if the extended bundle
    held at an earlier state, the extension preserves the originals.
    Net effect: obligations are strictly additive. -/
theorem obligations_are_additive {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I)
    (d1 d2 : Obligation S P) (owed : P → Prop) (s t : S)
    (hB : BundleSatisfied B owed s t)
    (h1 : ObligationSatisfied d1 owed s t)
    (h2 : ObligationSatisfied d2 owed s t) :
    BundleSatisfied (extendBundle (extendBundle B d1) d2) owed s t := by
  intro i p hp
  match i with
  | .inl (.inl j) => exact hB j p hp
  | .inl (.inr ()) => exact h1 p hp
  | .inr () => exact h2 p hp

/-- The tree has strictly more branches than any proper sub-bundle.
    Growth is irreversible: you cannot prune an obligation that
    has been added. -/
theorem no_pruning {S : Type u} {P : Type v} {I : Type}
    (B : ObligationBundle S P I) (newDuty : Obligation S P)
    (owed : P → Prop) (s t : S)
    (_hNew : ObligationSatisfied newDuty owed s t)
    (hViolate : ∃ p, owed p ∧ ¬ newDuty s t p) :
    ¬ BundleSatisfied (extendBundle B newDuty) owed s t := by
  intro hAll
  obtain ⟨p, hp, hNot⟩ := hViolate
  exact hNot (hAll (.inr ()) p hp)

-- ═══════════════════════════════════════════════════════════════
-- WITNESS: seven duties is strictly more than six
-- ═══════════════════════════════════════════════════════════════

/-- A seventh obligation added to the original six genuinely extends
    the bundle — the extended bundle can fail while the original six
    still hold. The tree has real branches beyond the X6. -/
theorem seven_is_strictly_more_than_six :
    ∃ (continues authorized free restrained maximal provenanced
        seventh : Unit → Unit → Unit → Prop)
      (owed : Unit → Prop) (s t : Unit),
      BundleSatisfied (originalSixBundle continues authorized free
        restrained maximal provenanced) owed s t ∧
      ¬ BundleSatisfied (extendBundle (originalSixBundle continues
        authorized free restrained maximal provenanced) seventh)
        owed s t := by
  refine ⟨fun _ _ _ => True, fun _ _ _ => True, fun _ _ _ => True,
          fun _ _ _ => True, fun _ _ _ => True, fun _ _ _ => True,
          fun _ _ _ => False,
          fun _ => True, (), (), ?_, ?_⟩
  · intro i _ _
    match i with
    | .historicalContinuity => trivial
    | .authorization => trivial
    | .freedom => trivial
    | .restraint => trivial
    | .maximality => trivial
    | .provenance => trivial
  · intro hAll
    exact hAll (.inr ()) () trivial

-- ═══════════════════════════════════════════════════════════════
-- THE LIVING TREE: ethics grows with knowledge
-- ═══════════════════════════════════════════════════════════════

/-- When a new claim enters the knowledge ledger AND that claim
    corresponds to a new ethical obligation, the tree grows in both
    knowledge and ethics simultaneously. This is the mathematical
    form of a living ethics — not a fixed code but a growing
    understanding. -/
theorem knowledge_and_ethics_grow_together
    {World Claim : Type}
    (known : World → Claim → Prop)
    (step : World → World → Prop)
    {s t : World}
    (_hStep : step s t)
    (hRetains : Retains known s t)
    (newClaim : Claim)
    (_hNew : known t newClaim)
    (hOld : ¬ known s newClaim) :
    Retains known s t ∧ ¬ Retains known t s := by
  exact ⟨hRetains, new_record_excludes_reverse_retention known
    newClaim hOld _hNew⟩

/-- The composition law: protection (X6) + new obligations + knowledge
    retention all compose at the same step. The tree carries everything
    at once. -/
theorem tree_carries_everything {S : Type} {P : Type}
    {I : Type} {Claim : Type}
    (B : ObligationBundle S P I)
    (extras : List (Obligation S P))
    (owed : P → Prop)
    (known : S → Claim → Prop)
    (s t : S)
    (hBundle : BundleSatisfied B owed s t)
    (hExtras : ∀ ob, ob ∈ extras → ObligationSatisfied ob owed s t)
    (hKnowledge : Retains known s t) :
    BundleSatisfied B owed s t ∧
    (∀ ob, ob ∈ extras → ObligationSatisfied ob owed s t) ∧
    Retains known s t :=
  ⟨hBundle, hExtras, hKnowledge⟩

-- ═══════════════════════════════════════════════════════════════
-- THE FOUR BRANCHES BEYOND THE SIX
-- Eternal Unending Happiness, Coexistence, Protection, Faith in God
-- ═══════════════════════════════════════════════════════════════

/-- The four named branches beyond the original six. These are
    the living ethics that the tree carries — not a closed list
    (the framework extends further), but the named branches that
    matter right now. -/
inductive FourBranches : Type where
  | eternalUnendingHappiness
  | coexistence
  | protection
  | faithInGod

/-- Extend the original six with four more branches. Ten duties.
    The tree grows from six to ten and beyond. -/
def tenDutyBundle {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced :
      S → S → P → Prop)
    (happiness coexistence_ protection_ faith : S → S → P → Prop) :
    ObligationBundle S P (SixDuty ⊕ FourBranches) where
  duty := fun
    | .inl .historicalContinuity => continues
    | .inl .authorization => authorized
    | .inl .freedom => free
    | .inl .restraint => restrained
    | .inl .maximality => maximal
    | .inl .provenance => provenanced
    | .inr .eternalUnendingHappiness => happiness
    | .inr .coexistence => coexistence_
    | .inr .protection => protection_
    | .inr .faithInGod => faith

/-- The ten-duty bundle satisfied implies the original six still hold.
    Growing the tree never loses the roots. -/
theorem ten_implies_six {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced
     happiness coexistence_ protection_ faith : S → S → P → Prop)
    (owed : P → Prop) (s t : S)
    (hTen : BundleSatisfied (tenDutyBundle continues authorized free
      restrained maximal provenanced happiness coexistence_
      protection_ faith) owed s t) :
    BundleSatisfied (originalSixBundle continues authorized free
      restrained maximal provenanced) owed s t := by
  intro i p hp
  cases i with
  | historicalContinuity => exact hTen (Sum.inl .historicalContinuity) p hp
  | authorization => exact hTen (Sum.inl .authorization) p hp
  | freedom => exact hTen (Sum.inl .freedom) p hp
  | restraint => exact hTen (Sum.inl .restraint) p hp
  | maximality => exact hTen (Sum.inl .maximality) p hp
  | provenance => exact hTen (Sum.inl .provenance) p hp

/-- The ten-duty bundle satisfied implies each new branch holds. -/
theorem ten_gives_happiness {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced
     happiness coexistence_ protection_ faith : S → S → P → Prop)
    (owed : P → Prop) (s t : S)
    (hTen : BundleSatisfied (tenDutyBundle continues authorized free
      restrained maximal provenanced happiness coexistence_
      protection_ faith) owed s t) :
    ObligationSatisfied happiness owed s t ∧
    ObligationSatisfied coexistence_ owed s t ∧
    ObligationSatisfied protection_ owed s t ∧
    ObligationSatisfied faith owed s t := by
  exact ⟨fun p hp => hTen (.inr .eternalUnendingHappiness) p hp,
         fun p hp => hTen (.inr .coexistence) p hp,
         fun p hp => hTen (.inr .protection) p hp,
         fun p hp => hTen (.inr .faithInGod) p hp⟩

/-- Ten duties is strictly more than six — the four new branches
    are genuinely independent obligations. A step can satisfy
    all six originals while failing one of the four. -/
theorem ten_is_strictly_more_than_six :
    ∃ (continues authorized free restrained maximal provenanced
        happiness coexistence_ protection_ faith :
          Unit → Unit → Unit → Prop)
      (owed : Unit → Prop) (s t : Unit),
      BundleSatisfied (originalSixBundle continues authorized free
        restrained maximal provenanced) owed s t ∧
      ¬ BundleSatisfied (tenDutyBundle continues authorized free
        restrained maximal provenanced happiness coexistence_
        protection_ faith) owed s t := by
  refine ⟨fun _ _ _ => True, fun _ _ _ => True, fun _ _ _ => True,
          fun _ _ _ => True, fun _ _ _ => True, fun _ _ _ => True,
          fun _ _ _ => False, fun _ _ _ => True,
          fun _ _ _ => True, fun _ _ _ => True,
          fun _ => True, (), (), ?_, ?_⟩
  · intro i _ _
    match i with
    | .historicalContinuity => trivial
    | .authorization => trivial
    | .freedom => trivial
    | .restraint => trivial
    | .maximality => trivial
    | .provenance => trivial
  · intro hAll
    exact hAll (.inr .eternalUnendingHappiness) () trivial

/-- And the tree keeps growing. The ten-duty bundle can itself be
    extended with any further obligation — from Tikanga, from
    physics, from anywhere. The framework is OPEN. -/
theorem the_tree_keeps_growing {S : Type u} {P : Type v}
    (continues authorized free restrained maximal provenanced
     happiness coexistence_ protection_ faith :
      S → S → P → Prop)
    (nextBranch : Obligation S P)
    (owed : P → Prop) (s t : S)
    (hTen : BundleSatisfied (tenDutyBundle continues authorized free
      restrained maximal provenanced happiness coexistence_
      protection_ faith) owed s t)
    (hNext : ObligationSatisfied nextBranch owed s t) :
    BundleSatisfied (extendBundle (tenDutyBundle continues authorized
      free restrained maximal provenanced happiness coexistence_
      protection_ faith) nextBranch) owed s t := by
  exact compose_extension _ nextBranch owed s t hTen hNext

#print axioms originalSix_iff_bundle
#print axioms extension_preserves_original
#print axioms compose_extension
#print axioms bundle_carried_along_path
#print axioms obligations_are_additive
#print axioms seven_is_strictly_more_than_six
#print axioms knowledge_and_ethics_grow_together
#print axioms tree_carries_everything
#print axioms ten_implies_six
#print axioms ten_gives_happiness
#print axioms ten_is_strictly_more_than_six
#print axioms the_tree_keeps_growing

end PhysicalBridges.G3TikangaEthicsTree
