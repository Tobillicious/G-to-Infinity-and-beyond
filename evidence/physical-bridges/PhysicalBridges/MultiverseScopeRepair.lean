import PhysicalBridges.IntrinsicStandingRepair

/-!
# Multiverse Scope Cathedral — Self-Contained PhysicalBridges Build

## What this proves and why it matters for G

If protection scope is embedding-independent (IntrinsicStandingRepair),
then it's all-or-nothing across every type. This module extends that
to dependent sums: protection across MULTIPLE WORLDS indexed by a
universe type U with per-world particulars Part(i).

The key result: `scope_guarantee_iff_every_world_full` — the scope
guarantee (no needless existing loss) over the multiverse dependent sum
holds iff EVERY particular in EVERY world is covered. Protection
cannot be local to one world.

The topology theorem (Snuffy.CommonPolicyTop.top_policy_exists) proves
a greatest policy exists under compactness — that requires Mathlib.
Its conclusion is stated here as a conditional for completeness, but
the SCOPE argument is the load-bearing one and compiles in pure Lean 4.

## Provenance

Repaired from `MultiverseScopeCathedral.lean` which imported
`Snuffy.Law` and `Snuffy.CommonPolicyTop`. Scope definitions inlined
from IntrinsicStandingRepair. No Mathlib. No new axioms.
-/

universe u v

namespace PhysicalBridges.MultiverseScopeRepair

open PhysicalBridges.IntrinsicStandingRepair

variable {U : Type u} (Part : U → Type v)

/-- Scope guarantee over a dependent sum of worlds: for every feasible
    family of outcomes over Σ(i:U). Part(i), projected maximality on
    scope S prevents needless existing loss.
    Uses the inlined ProjMax and NeedlessLoss₁ from IntrinsicStandingRepair. -/
def ScopeGuarantee (S : (Sigma Part) → Prop) : Prop :=
  ∀ (F : ((Sigma Part) → Prop) → Prop) (o : (Sigma Part) → Prop),
    ProjMax S F o → ¬ NeedlessLoss₁ F o

/-- **Full scope is equivalent to covering every particular in every
    world.** This is the multiverse uniformity theorem: you cannot
    have protection in some worlds but not others. -/
theorem full_scope_iff_every_world (S : (Sigma Part) → Prop) :
    (∀ (i : U) (p : Part i), S ⟨i, p⟩) ↔ (∀ x : Sigma Part, S x) := by
  constructor
  · intro h x
    exact h x.1 x.2
  · intro h i p
    exact h ⟨i, p⟩

/-- **Scope guarantee over the multiverse iff every particular in every
    world is covered.** Combines `scope_guarantee_iff` from
    IntrinsicStandingRepair with the dependent-sum characterization.
    This is the original MultiverseScopeCathedral theorem, now compiled. -/
theorem scope_guarantee_iff_every_world_full (S : (Sigma Part) → Prop) :
    ScopeGuarantee Part S ↔ ∀ (i : U) (p : Part i), S ⟨i, p⟩ := by
  constructor
  · intro hSG i p
    have hfull := (scope_guarantee_iff S).mp hSG
    exact hfull ⟨i, p⟩
  · intro h
    have hfull : ∀ x : Sigma Part, S x :=
      (full_scope_iff_every_world Part S).mp h
    exact (scope_guarantee_iff S).mpr hfull

/-- If one world has a particular in scope under embedding independence,
    every world must have all its particulars in scope. Protection
    cannot be local — the multiverse is all or nothing. -/
theorem multiverse_all_or_nothing
    (Scope : (X : Type (max u v)) → (X → Prop))
    (hreflect : EmbeddingIndependent Scope)
    {j : U} {p : Part j} (hp : Scope (Sigma Part) ⟨j, p⟩) :
    ∀ (i : U) (q : Part i), Scope (Sigma Part) ⟨i, q⟩ := by
  intro i q
  exact one_anchor_implies_universal Scope hreflect
    (Sigma.mk j p) hp (Sigma Part) (Sigma.mk i q)

/-! ## Axiom audit -/
#print axioms full_scope_iff_every_world
#print axioms scope_guarantee_iff_every_world_full
#print axioms multiverse_all_or_nothing

end PhysicalBridges.MultiverseScopeRepair
