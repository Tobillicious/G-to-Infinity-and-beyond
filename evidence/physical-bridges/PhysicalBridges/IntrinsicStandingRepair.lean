/-!
# Intrinsic Standing Cathedral — Self-Contained PhysicalBridges Build

## What this proves and why it matters for G

The core claim: if protection scope is *embedding-independent* (doesn't
change when you inject a subject into a larger mathematical domain), then
the only possible scopes are "protect nothing" or "protect everything."
There is no partial protection.

Combined with Something IS (at least one thing has standing), this forces
the universal scope: EVERYTHING has standing. Full U/ALL is not a choice
— it's the only mathematically consistent option.

Then Proposition 3 (scope_guarantee_iff, from the compiled UPT canon):
the universal scope is the ONLY scope that prevents needless existing loss
in every feasible family. Any smaller scope admits a tragedy that could
have been prevented.

## Provenance

Repaired from `IntrinsicStandingCathedral.lean` which imported `Snuffy.Law`.
Snuffy definitions (NeedlessLoss₁, ProjMax, scope_guarantee_iff) translated
from `evidence/compiled-strongest/lean/Snuffy/Law.lean` lines 78–107 into
pure Lean 4 (predicates `α → Prop` in place of Mathlib `Set α`).

No Mathlib. No new axioms. Every theorem is the original argument.
-/

universe u v

namespace PhysicalBridges.IntrinsicStandingRepair

-- ═══════════════════════════════════════════════════════════════════
-- PREDICATE-BASED SET OPERATIONS (pure Lean 4, no Mathlib)
-- ═══════════════════════════════════════════════════════════════════

variable {P : Sort v}

def ssubset (S T : P → Prop) : Prop :=
  (∀ x, S x → T x) ∧ ∃ x, T x ∧ ¬ S x

def inter (S T : P → Prop) : P → Prop :=
  fun x => S x ∧ T x

def emptySet : P → Prop := fun _ => False

def singleton (a : P) : P → Prop := fun x => x = a

-- ═══════════════════════════════════════════════════════════════════
-- INLINED FROM Snuffy.Law — Proposition 3
--
-- WHY: scope_guarantee_iff is the mathematical proof that ONLY the
-- universal scope prevents all needless loss. It's the formal
-- backbone of "protection must be for everything, not just some."
-- ═══════════════════════════════════════════════════════════════════

/-- A needless existing loss: some feasible option strictly contains the
    chosen one. (Snuffy.Law.NeedlessLoss₁) -/
def NeedlessLoss₁ (F : (P → Prop) → Prop) (o : P → Prop) : Prop :=
  ∃ q, F q ∧ ssubset o q

/-- Projected maximality: `o` is in `F` and no other member of `F`
    strictly contains `o`'s projection onto scope `S`.
    (Snuffy.Law.ProjMax) -/
def ProjMax (S : P → Prop) (F : (P → Prop) → Prop) (o : P → Prop) : Prop :=
  F o ∧ ∀ q, F q → ¬ ssubset (inter o S) (inter q S)

/-- **Proposition 3.** Projected maximality on scope `S` guarantees no
    needless existing loss for every feasible family if and only if
    `S` covers the whole domain.

    Forward direction: if S misses any element x, construct the family
    {∅, {x}} where ∅ is ProjMax (since {x}∩S = ∅∩S) yet ∅ ⊂ {x}.
    Reverse direction: if S is universal, projected maximality IS
    maximality, so no needless loss. -/
theorem scope_guarantee_iff (S : P → Prop) :
    (∀ (F : (P → Prop) → Prop) (o : P → Prop), ProjMax S F o → ¬ NeedlessLoss₁ F o) ↔
    (∀ x : P, S x) := by
  constructor
  · -- Forward: if any x is not in S, we build a counterexample.
    -- Family = {∅, {x}}.  ∅ is ProjMax because {x}∩S = ∅∩S.  But ∅ ⊂ {x}.
    intro h x
    exact Classical.byContradiction fun hx =>
      h (fun s => s = emptySet ∨ s = singleton x) emptySet
        ⟨Or.inl rfl,
         fun q hq hsub => by
           cases hq with
           | inl heq =>
             -- q = emptySet, so ssubset (∅∩S) (∅∩S) is impossible
             obtain ⟨_, y, hy_pos, hy_neg⟩ := hsub
             rw [heq] at hy_pos
             exact hy_neg hy_pos
           | inr heq =>
             -- q = singleton x, but x ∉ S, so {x}∩S is empty
             obtain ⟨_, y, hy_pos, _⟩ := hsub
             rw [heq] at hy_pos
             exact hx (show S x from hy_pos.1 ▸ hy_pos.2)⟩
        ⟨singleton x, Or.inr rfl,
          ⟨fun _ hy => absurd hy id, ⟨x, rfl, fun hf => hf⟩⟩⟩
  · -- Reverse: if S is universal, projected maximality IS maximality.
    intro hfull F o hPM hNL
    have hmax := hPM.2
    obtain ⟨q, hqF, hsub⟩ := hNL
    apply hmax q hqF
    constructor
    · intro y hy
      exact ⟨hsub.1 y hy.1, hfull y⟩
    · obtain ⟨z, hzq, hzo⟩ := hsub.2
      exact ⟨z, ⟨hzq, hfull z⟩, fun hz => hzo hz.1⟩

-- ═══════════════════════════════════════════════════════════════════
-- THE INTRINSIC STANDING ARGUMENT
--
-- WHY: This is the proof that protection is all-or-nothing.
-- EmbeddingIndependent = "scope doesn't depend on context."
-- Combined with Something IS, this forces universal protection.
-- ═══════════════════════════════════════════════════════════════════

/-- Scope does not change under any injection of a subject into a larger
    mathematical domain. Stronger than forward naturality: if x has
    standing in A, then f(x) has standing in Y, AND vice versa.
    Standing is intrinsic to the subject, not to the domain. -/
def EmbeddingIndependent
    (Scope : (X : Type u) → (X → Prop)) : Prop :=
  ∀ (X Y : Type u) (f : X → Y),
    Function.Injective f →
    ∀ x : X, Scope X x ↔ Scope Y (f x)

private theorem singleton_injection {Y : Type u} (b : Y) :
    Function.Injective (fun _ : PUnit.{u+1} => b) := by
  intro x y _
  exact Subsingleton.elim x y

/-- **If even one thing has standing, then everything in every domain
    has standing.** The proof routes through PUnit (the singleton type):
    if `a` has standing in `A`, then PUnit.unit has standing in PUnit
    (by embedding independence with the constant map). Then any `b` in
    any `Y` has standing (by embedding independence with the other
    constant map). One anchor → universal. -/
theorem one_anchor_implies_universal
    (Scope : (X : Type u) → (X → Prop))
    (hreflect : EmbeddingIndependent Scope)
    {A : Type u} (a : A) (ha : Scope A a) :
    ∀ (Y : Type u) (b : Y), Scope Y b := by
  have hanchor : Scope PUnit.{u+1} PUnit.unit :=
    (hreflect PUnit.{u+1} A (fun _ => a) (singleton_injection a) PUnit.unit).mpr ha
  intro Y b
  exact (hreflect PUnit.{u+1} Y (fun _ => b) (singleton_injection b) PUnit.unit).mp hanchor

/-- **The only embedding-independent scope assignments are all or nothing.**
    Either everything has standing or nothing does. There is no partial
    protection that respects embedding independence.
    Something IS + this theorem = Full U/ALL. -/
theorem empty_or_universal
    (Scope : (X : Type u) → (X → Prop))
    (hreflect : EmbeddingIndependent Scope) :
    (∀ (X : Type u) (x : X), Scope X x) ∨
    (∀ (X : Type u) (x : X), ¬ Scope X x) := by
  by_cases h : ∃ (A : Type u) (a : A), Scope A a
  · left
    obtain ⟨A, a, ha⟩ := h
    exact one_anchor_implies_universal Scope hreflect a ha
  · right
    intro X x hx
    exact h ⟨X, x, hx⟩

/-- **The compiled UPT scope law, instantiated universally.**
    Given embedding independence and one anchor, the universal scope
    is forced — and by Proposition 3, that universal scope is the
    ONLY one that prevents needless existing loss in every family.

    This is the bridge: Something IS → one anchor → universal scope
    → scope_guarantee_iff → no needless existing loss. The full
    protection claim follows from the ontological ground. -/
theorem original_scope_law_across_every_type
    (Scope : (X : Type u) → (X → Prop))
    (hreflect : EmbeddingIndependent Scope)
    {A : Type u} (a : A) (ha : Scope A a)
    (Y : Type u) :
    ∀ (F : (Y → Prop) → Prop) (o : Y → Prop),
      ProjMax (Scope Y) F o →
      ¬ NeedlessLoss₁ F o := by
  have hfull : ∀ y : Y, Scope Y y :=
    one_anchor_implies_universal Scope hreflect a ha Y
  exact (scope_guarantee_iff (Scope Y)).mpr hfull

/-! ## Axiom audit -/
#print axioms scope_guarantee_iff
#print axioms one_anchor_implies_universal
#print axioms empty_or_universal
#print axioms original_scope_law_across_every_type

end PhysicalBridges.IntrinsicStandingRepair
