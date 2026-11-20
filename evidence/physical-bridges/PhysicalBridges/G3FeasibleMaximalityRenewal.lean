import PhysicalBridges.G3InductiveCompleteness

/-!
# G3 Time Koru: feasible maximality over genuinely new alternatives

Find-before-build extension of `G3InductiveCompleteness`. The existing
`G3KoruCarriesDuties.MAXIMALITY_MUST_BE_REJUDGED` already proves the logical
point for first-order formulas. Here we give the exact order-theoretic
step certificate for FEASIBLE maximality.

No original X3 definition is altered. `MaximalAt` is a mathematical
model of one component; claiming correspondence to the authentic
OriginalX3 maximality field requires separate physical/ethical evidence.

The improvement is precise: an existing selected option stays maximal
if it remains feasible, is unchanged, and there is no newly feasible
strictly better option. If a new better feasible option appears, the
old selection is NOT maximal, even if its entire history is retained.
-/

/- By GPT (20 Nov 2026). Approved repairs by Claude to the two example proofs
   (`decide` and goal order); general theorems unchanged. -/

namespace PhysicalBridges.G3FeasibleMaximalityRenewal

universe u v

structure FeasibleOrder (P : Type u) (A : Type v) where
  feasible : Nat → P → A → Prop
  better : P → A → A → Prop
  selected : Nat → P → A

/-- Maximality is evaluated against ALL currently feasible alternatives. -/
def MaximalAt {P : Type u} {A : Type v}
    (F : FeasibleOrder P A) (n : Nat) (p : P) : Prop :=
  F.feasible n p (F.selected n p) ∧
  ∀ a, F.feasible n p a → ¬ F.better p (F.selected n p) a

/-- The exact additional condition needed when extending the Koru:
no option that becomes feasible at the new stage is strictly better
than the retained choice, unless it was already feasible earlier. -/
def NoNewSuperiorAlternative {P : Type u} {A : Type v}
    (F : FeasibleOrder P A) (n : Nat) (p : P) : Prop :=
  ∀ a, F.feasible (n+1) p a →
    F.better p (F.selected n p) a → F.feasible n p a

/-- A preserved old choice remains maximal if the old certificate
was valid, the choice remains feasible, and genuinely new options
cannot dominate it. -/
theorem maximality_renews_under_complete_frontier_check
    {P : Type u} {A : Type v}
    (F : FeasibleOrder P A) (n : Nat) (p : P)
    (hOld : MaximalAt F n p)
    (hSame : F.selected (n+1) p = F.selected n p)
    (hFeasible : F.feasible (n+1) p (F.selected n p))
    (hFrontier : NoNewSuperiorAlternative F n p) :
    MaximalAt F (n+1) p := by
  constructor
  · rw [hSame]
    exact hFeasible
  · intro a ha hbetter
    rw [hSame] at hbetter
    have hEarlier : F.feasible n p a := hFrontier a ha hbetter
    exact (hOld.2 a hEarlier) hbetter

/-- **Exact frontier gate.** For a retained feasible choice that was
    maximal in the previous world, the NO-new-superior check is equivalent
    to maximality in the expanded world. No assumption that all newly
    possible options are harmless is hidden in the definition. -/
theorem maximality_iff_no_new_superior_alternative
    {P : Type u} {A : Type v}
    (F : FeasibleOrder P A) (n : Nat) (p : P)
    (hOld : MaximalAt F n p)
    (hSame : F.selected (n+1) p = F.selected n p)
    (hFeasible : F.feasible (n+1) p (F.selected n p)) :
    MaximalAt F (n+1) p ↔ NoNewSuperiorAlternative F n p := by
  constructor
  · intro hMax a ha hBetter
    have hNoBetter := hMax.2 a ha
    have hBetterNew : F.better p (F.selected (n+1) p) a := by
      rw [hSame]
      exact hBetter
    exact False.elim (hNoBetter hBetterNew)
  · intro hFrontier
    exact maximality_renews_under_complete_frontier_check
      F n p hOld hSame hFeasible hFrontier

/-- One newly feasible strictly superior option is a complete,
explicit refutation of the retained choice's maximality. -/
theorem new_superior_option_refutes_old_choice
    {P : Type u} {A : Type v}
    (F : FeasibleOrder P A) (n : Nat) (p : P)
    (hSame : F.selected (n+1) p = F.selected n p)
    (a : A) (ha : F.feasible (n+1) p a)
    (hbetter : F.better p (F.selected n p) a) :
    ¬ MaximalAt F (n+1) p := by
  intro h
  exact (h.2 a ha) (by rw [hSame]; exact hbetter)

/-- A nontrivial finite example: before, only `false` is feasible;
after, `true` becomes feasible and strictly improves on `false`. -/
def twoOptionGrowth : FeasibleOrder Unit Bool where
  feasible := fun n _ a => if n = 0 then a = false else True
  better := fun _ old new => old = false ∧ new = true
  selected := fun _ _ => false

theorem initially_maximal : MaximalAt twoOptionGrowth 0 () := by
  refine ⟨rfl, ?_⟩
  intro a ha hb
  have haf : a = false := ha
  exact Bool.noConfusion (haf.symm.trans hb.2)

theorem newly_feasible_option_breaks_maximality :
    ¬ MaximalAt twoOptionGrowth 1 () :=
  new_superior_option_refutes_old_choice twoOptionGrowth 0 () rfl true trivial ⟨rfl, rfl⟩

/-- At each new stage, old owed particulars need a frontier check;
newly owed particulars require a fresh authentic maximality certificate.
No old certificate is incorrectly extended to a new particular. -/
theorem every_owed_maximality_renews
    {P : Type u} {A : Type v}
    (F : FeasibleOrder P A)
    (owed : Nat → P → Prop)
    (hInitial : ∀ p, owed 0 p → MaximalAt F 0 p)
    (hSame : ∀ n p, owed (n+1) p → owed n p →
      F.selected (n+1) p = F.selected n p)
    (hFeasible : ∀ n p, owed (n+1) p → owed n p →
      F.feasible (n+1) p (F.selected n p))
    (hFrontier : ∀ n p, owed (n+1) p → owed n p →
      NoNewSuperiorAlternative F n p)
    (hNew : ∀ n p, owed (n+1) p → ¬ owed n p →
      MaximalAt F (n+1) p) :
    ∀ n p, owed n p → MaximalAt F n p := by
  intro n
  induction n with
  | zero => exact hInitial
  | succ n ih =>
      intro p hp
      by_cases hPreviouslyOwed : owed n p
      · exact maximality_renews_under_complete_frontier_check
          F n p (ih p hPreviouslyOwed)
          (hSame n p hp hPreviouslyOwed)
          (hFeasible n p hp hPreviouslyOwed)
          (hFrontier n p hp hPreviouslyOwed)
      · exact hNew n p hp hPreviouslyOwed

#print axioms maximality_renews_under_complete_frontier_check
#print axioms maximality_iff_no_new_superior_alternative
#print axioms new_superior_option_refutes_old_choice
#print axioms initially_maximal
#print axioms newly_feasible_option_breaks_maximality
#print axioms every_owed_maximality_renews

end PhysicalBridges.G3FeasibleMaximalityRenewal
