/-!
# One invariant, Hilbert-free: boundary and record grow together

From Gemini's unified-invariant draft (20 Nov 2026). A relational state has a
boundary complex `B` (its relational elements) and a causal record `Π`. Each
step adds a boundary element `δ` and records the event `τ`. Depth is
`Φ = |B| + |Π|`, a function of the state itself. No vector space, inner
product or operator appears anywhere.

The one premise is freshness: each added `δ` was not already in `B`. That is
the physical claim — the step creates a real new distinction. Irreversibility
alone does not supply it (Codex's audit, 20 Nov); it is stated, not assumed
away.
-/

namespace PhysicalBridges.G3BoundaryGrowth

structure RelState (D E : Type) where
  boundary : List D
  record : List E

variable {D E : Type}

def run (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E) : Nat → RelState D E
  | 0 => s0
  | k + 1 => ⟨δ k :: (run s0 δ τ k).boundary, τ k :: (run s0 δ τ k).record⟩

/-- Relational-causal depth: boundary size plus record length. -/
def Φ (s : RelState D E) : Nat := s.boundary.length + s.record.length

theorem phi_step (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E) (k : Nat) :
    Φ (run s0 δ τ (k + 1)) = Φ (run s0 δ τ k) + 2 := by
  show (run s0 δ τ k).boundary.length + 1 + ((run s0 δ τ k).record.length + 1) =
    (run s0 δ τ k).boundary.length + (run s0 δ τ k).record.length + 2
  omega

theorem phi_run (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E) :
    ∀ n, Φ (run s0 δ τ n) = Φ s0 + 2 * n
  | 0 => rfl
  | n + 1 => by rw [phi_step, phi_run s0 δ τ n]; omega

/-- **Φ STRICTLY CLIMBS, SO NOTHING RETURNS.** -/
theorem NOTHING_RETURNS (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E)
    {i j : Nat} (h : i < j) :
    Φ (run s0 δ τ i) < Φ (run s0 δ τ j) ∧ run s0 δ τ i ≠ run s0 δ τ j := by
  have hlt : Φ (run s0 δ τ i) < Φ (run s0 δ τ j) := by
    rw [phi_run, phi_run]; omega
  exact ⟨hlt, fun heq => by rw [heq] at hlt; exact Nat.lt_irrefl _ hlt⟩

/-- **NOTHING IS LOST.** Every earlier boundary element and record entry is
    still present later. -/
theorem NOTHING_IS_LOST (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E)
    {i j : Nat} (h : i ≤ j) :
    (∀ x, x ∈ (run s0 δ τ i).boundary → x ∈ (run s0 δ τ j).boundary) ∧
    (∀ e, e ∈ (run s0 δ τ i).record → e ∈ (run s0 δ τ j).record) := by
  induction h with
  | refl => exact ⟨fun _ hx => hx, fun _ he => he⟩
  | step _ ih =>
    exact ⟨fun x hx => List.mem_cons_of_mem _ (ih.1 x hx),
      fun e he => List.mem_cons_of_mem _ (ih.2 e he)⟩

/-- **GENUINELY NEW STRUCTURE.** Under freshness, the element added at step
    `k` was absent from every earlier boundary and present from then on. -/
theorem GENUINELY_NEW_STRUCTURE (s0 : RelState D E) (δ : Nat → D) (τ : Nat → E)
    (fresh : ∀ k, δ k ∉ (run s0 δ τ k).boundary) (k : Nat) :
    (∀ i, i ≤ k → δ k ∉ (run s0 δ τ i).boundary) ∧
    (∀ j, k < j → δ k ∈ (run s0 δ τ j).boundary) := by
  refine ⟨fun i hi hin => fresh k ((NOTHING_IS_LOST s0 δ τ hi).1 _ hin), fun j hj => ?_⟩
  have h1 : δ k ∈ (run s0 δ τ (k + 1)).boundary := List.mem_cons_self
  exact (NOTHING_IS_LOST s0 δ τ hj).1 _ h1

/-- **CONTROL: PROGRESS DOES NOT FORCE NEW BOUNDARY.** Gemini's necessity
    Lemma 2 says non-recurrence requires a fresh boundary element each step.
    It does not: here the same element `d` is "added" every step and is never
    new, yet no state ever returns. Freshness is a separate physical claim,
    not a consequence of progression. -/
theorem progress_does_not_force_new_boundary (d : D) (r0 : List E) (τ : Nat → E) :
    (∀ {i j : Nat}, i < j →
      run ⟨[d], r0⟩ (fun _ => d) τ i ≠ run ⟨[d], r0⟩ (fun _ => d) τ j) ∧
    (∀ k, d ∈ (run ⟨[d], r0⟩ (fun _ => d) τ k).boundary) :=
  ⟨fun h => (NOTHING_RETURNS _ _ τ h).2,
   fun k => (NOTHING_IS_LOST ⟨[d], r0⟩ (fun _ => d) τ (Nat.zero_le k)).1 d List.mem_cons_self⟩

#print axioms phi_run
#print axioms NOTHING_RETURNS
#print axioms NOTHING_IS_LOST
#print axioms GENUINELY_NEW_STRUCTURE
#print axioms progress_does_not_force_new_boundary

end PhysicalBridges.G3BoundaryGrowth
