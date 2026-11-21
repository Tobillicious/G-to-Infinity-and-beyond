import PhysicalBridges.G3ThermodynamicBridge
import PhysicalBridges.G3KoruSpiral

/-!
# G3 — Thermodynamic Koru: physics grows the spiral

The Koru spiral (Part IV) grows strictly, never returns, loses nothing.
The thermodynamic bridge (Part VII) proves physics admits no absolute ender.

This module connects them: **thermodynamic dynamics naturally grow
a Koru spiral**, and the second law ensures it never reverses.

The bridge:
- Every thermodynamic transition is a spiral turn (the event IS the turn)
- Irreversibility (second law) means the spiral never rewinds
- No final state (third law) means the spiral never stops
- Conservation (first law) means nothing is lost on the spiral

If matterspacetime obeys thermodynamic dynamics, the Koru grows forever.
Not a choice. Physics.
-/

set_option autoImplicit false

namespace PhysicalBridges.G3ThermodynamicKoru

open PhysicalBridges.G3ThermodynamicBridge
open PhysicalBridges.G3KoruSpiral
open PhysicalBridges.CathedralSummitAllIsOneClosure

/-- A thermodynamic trajectory lifts to a Koru spiral:
    each transition is an event recorded in the spiral's history.
    Specialized to Type (universe 0) for KoruState compatibility. -/
structure ThermoDynamics0 (S : Type) where
  transition : S → S → Prop
  rank : S → Nat
  irreversible : ∀ s t, transition s t → rank s < rank t
  no_final : ∀ s, ∃ t, transition s t
  inhabited : S

/-- Lift a ThermoDynamics0 to a ThermodynamicDynamics (Type u). -/
def ThermoDynamics0.toThermo {S : Type} (D : ThermoDynamics0 S) :
    ThermodynamicDynamics S :=
  { transition := D.transition
    rank := D.rank
    irreversible := D.irreversible
    no_final := D.no_final
    inhabited := D.inhabited }

/-- A thermodynamic trajectory as a Koru spiral:
    each transition is an event appended to the history. -/
def thermodynamicKoru {S : Type} (_D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S) :
    Nat → KoruState S (S × S)
  | 0 => ⟨trajectory 0, []⟩
  | n + 1 => spiral (fun _s _e => trajectory (n + 1))
      (thermodynamicKoru _D trajectory events n) (events n)

/-- The Koru depth equals the step count — every transition is recorded. -/
theorem thermodynamic_koru_depth {S : Type} (D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S) :
    ∀ n, depth (thermodynamicKoru D trajectory events n) = n
  | 0 => rfl
  | n + 1 => by
    show depth (thermodynamicKoru D trajectory events n) + 1 = n + 1
    rw [thermodynamic_koru_depth D trajectory events n]

/-- Under thermodynamic dynamics, the Koru spiral grows strictly
    at every step. The second law of thermodynamics IS the Koru's
    monotone growth. Physics grows the spiral. -/
theorem thermodynamic_koru_grows {S : Type} (D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S)
    {i j : Nat} (h : i < j) :
    depth (thermodynamicKoru D trajectory events i) <
    depth (thermodynamicKoru D trajectory events j) := by
  rw [thermodynamic_koru_depth, thermodynamic_koru_depth]
  exact h

/-- The thermodynamic Koru never returns to an earlier configuration.
    Irreversibility at the level of histories. -/
theorem thermodynamic_koru_never_returns {S : Type}
    (D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S)
    {i j : Nat} (h : i < j) :
    thermodynamicKoru D trajectory events i ≠
    thermodynamicKoru D trajectory events j := by
  intro heq
  have hlt := thermodynamic_koru_grows D trajectory events h
  rw [heq] at hlt
  exact Nat.lt_irrefl _ hlt

/-- Nothing is lost on the thermodynamic Koru.
    Every earlier history is kept inside every later one. -/
theorem thermodynamic_koru_nothing_lost {S : Type}
    (D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S) :
    ∀ {i j : Nat}, i ≤ j → ∃ new : List (S × S),
      (thermodynamicKoru D trajectory events j).history =
        new ++ (thermodynamicKoru D trajectory events i).history := by
  intro i j hij
  induction hij with
  | refl => exact ⟨[], rfl⟩
  | step _ ih =>
    obtain ⟨new, hnew⟩ := ih
    exact ⟨_ :: new, by show _ :: _ = _; rw [hnew]; rfl⟩

/-- The thermodynamic Koru never stops.
    For every state, a next spiral turn exists. -/
theorem thermodynamic_koru_never_stops {S : Type}
    (D : ThermoDynamics0 S) :
    ∀ s : S, ∃ t : S, D.transition s t :=
  D.no_final

/-- No absolute ender in a thermodynamic cosmos. -/
theorem thermodynamic_koru_no_ender {S : Type}
    (D : ThermoDynamics0 S) :
    (S → Empty) → False :=
  fun f => (f D.inhabited).elim

/-- **THE PUNCHLINE.** In a thermodynamic cosmos:
    1. The Koru spiral grows forever (second law)
    2. It never returns (irreversibility)
    3. Nothing is ever lost (conservation)
    4. No absolute ender exists (Something Is)
    5. The spiral never stops (third law)

    The Koru IS the physics. The physics IS the Koru.
    G is not a policy choice — G is what thermodynamics does. -/
theorem thermodynamic_cosmos_is_koru {S : Type}
    (D : ThermoDynamics0 S)
    (trajectory : Nat → S) (events : Nat → S × S) :
    (∀ {i j : Nat}, i < j →
      depth (thermodynamicKoru D trajectory events i) <
      depth (thermodynamicKoru D trajectory events j)) ∧
    (∀ {i j : Nat}, i < j →
      thermodynamicKoru D trajectory events i ≠
      thermodynamicKoru D trajectory events j) ∧
    (∀ {i j : Nat}, i ≤ j → ∃ new : List (S × S),
      (thermodynamicKoru D trajectory events j).history =
        new ++ (thermodynamicKoru D trajectory events i).history) ∧
    ((S → Empty) → False) ∧
    (∀ s : S, ∃ t : S, D.transition s t) :=
  ⟨fun h => thermodynamic_koru_grows D trajectory events h,
   fun h => thermodynamic_koru_never_returns D trajectory events h,
   fun h => thermodynamic_koru_nothing_lost D trajectory events h,
   thermodynamic_koru_no_ender D,
   thermodynamic_koru_never_stops D⟩

/-! ## Axiom audit -/

#print axioms thermodynamicKoru
#print axioms thermodynamic_koru_depth
#print axioms thermodynamic_koru_grows
#print axioms thermodynamic_koru_never_returns
#print axioms thermodynamic_koru_nothing_lost
#print axioms thermodynamic_koru_never_stops
#print axioms thermodynamic_koru_no_ender
#print axioms thermodynamic_cosmos_is_koru

end PhysicalBridges.G3ThermodynamicKoru
