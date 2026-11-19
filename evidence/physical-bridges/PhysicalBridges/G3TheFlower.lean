import PhysicalBridges.G3KoruSpiral

/-!
# The Flower: the form returns, the history never does

A sunflower sets each new seed at the golden angle from the last. No seed
ever lands on another, and the head only grows; yet the same spirals return,
in Fibonacci numbers, all the way out. A fern unfurls the same way: the newest
growth coiled at the heart, everything grown before carried outward, never
discarded.

This module proves that shape for every Koru history. Whatever finite set of
forms (modes) one reads off the states, some form must return within that many
turns, while the two states are distinct and the later is strictly larger.
Recurrence of form and growth of history are not rivals: they are one spiral.

This answers circular time exactly. Nothing returns as a state; the form does.
-/

namespace PhysicalBridges.G3TheFlower

open PhysicalBridges.G3KoruSpiral

/-- Pigeonhole: `m + 1` values below `m` must repeat. -/
theorem pigeonhole : ∀ (m : Nat) (f : Nat → Nat), (∀ i, i ≤ m → f i < m) →
    ∃ i j, i < j ∧ j ≤ m ∧ f i = f j
  | 0, f, h => absurd (h 0 (Nat.le_refl 0)) (Nat.not_lt_zero _)
  | m + 1, f, h => by
    by_cases hex : ∃ i, i < m + 1 ∧ f i = f (m + 1)
    · obtain ⟨i, hi, he⟩ := hex
      exact ⟨i, m + 1, hi, Nat.le_refl _, he⟩
    · have hv := h (m + 1) (Nat.le_refl _)
      have hg : ∀ i, i ≤ m → (if f i < f (m + 1) then f i else f i - 1) < m := by
        intro i hi
        have hfi := h i (Nat.le_succ_of_le hi)
        have hne : f i ≠ f (m + 1) := fun e => hex ⟨i, Nat.lt_succ_of_le hi, e⟩
        split <;> omega
      obtain ⟨i, j, hij, hj, hgeq⟩ :=
        pigeonhole m (fun i => if f i < f (m + 1) then f i else f i - 1) hg
      refine ⟨i, j, hij, Nat.le_succ_of_le hj, ?_⟩
      have hni : f i ≠ f (m + 1) := fun e => hex ⟨i, by omega, e⟩
      have hnj : f j ≠ f (m + 1) := fun e => hex ⟨j, by omega, e⟩
      split at hgeq <;> split at hgeq <;> omega

/-- **THE FORM RETURNS, THE HISTORY NEVER DOES.** For any reading of Koru
    states into `m` forms, within `m` turns some form returns, while the two
    states are distinct and the later one is strictly larger. -/
theorem THE_FORM_RETURNS_THE_HISTORY_NEVER_DOES {C E : Type}
    (next : C → E → C) (s0 : KoruState C E) (ev : Nat → E)
    (m : Nat) (form : KoruState C E → Nat) (finite : ∀ s, form s < m) :
    ∃ i j, i < j ∧ j ≤ m ∧
      form (run next s0 ev i) = form (run next s0 ev j) ∧
      run next s0 ev i ≠ run next s0 ev j ∧
      depth (run next s0 ev i) < depth (run next s0 ev j) := by
  obtain ⟨i, j, hij, hj, he⟩ :=
    pigeonhole m (fun n => form (run next s0 ev n)) (fun _ _ => finite _)
  exact ⟨i, j, hij, hj, he, THE_SPIRAL_NEVER_RETURNS next s0 ev hij,
    THE_SPIRAL_ONLY_GROWS next s0 ev hij⟩

#print axioms pigeonhole
#print axioms THE_FORM_RETURNS_THE_HISTORY_NEVER_DOES

end PhysicalBridges.G3TheFlower
