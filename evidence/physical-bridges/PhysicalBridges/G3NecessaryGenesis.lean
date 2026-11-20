/-!
# Necessary Genesis

From the five-axiom architecture (Gemini, 20 Nov 2026), checked in Lean.

A1 Something Is and is actual · A2 the Complete Koru steps outward without
closing · A3 the Time Koru carries the outward step forward, strictly later
than the seed · A4 a step from the actual is actual · A5 what is strictly later
than the seed is new.

`NECESSARY_GENESIS`: in every frame satisfying A1–A5, an actual new
configuration exists. `actualisation_is_load_bearing`: drop A4 alone and Genesis
can fail — order without actualisation leaves the new merely possible. So A4 is
where the physical claim lives, stated as the premise it is.

`NO_CYCLE_OF_ANY_LENGTH` and `ACTUALITY_CARRIES_FORWARD`: along any chain of
realised Koru steps under a strict order, no state returns to any earlier one,
and actuality reaches every step.
-/

namespace PhysicalBridges.G3NecessaryGenesis

/-- Gemini's five-axiom frame (20 Nov 2026). A frame is any model; "necessary"
    means: in every frame satisfying A1–A5. -/
structure GenesisFrame where
  S : Type
  s0 : S
  Act : S → Prop
  koruC : S → S → Prop
  koruT : S → S → Prop
  prec : S → S → Prop
  New : S → S → Prop
  A1 : Act s0
  A2 : ∀ x, Act x → ∃ y, koruC x y ∧ ¬ koruC y x
  A3 : ∀ y, (∃ x, koruC x y) → ∃ z, koruT y z ∧ prec s0 z ∧ ¬ prec z s0
  A4 : ∀ x y z, Act x → koruC x y → koruT y z → Act z
  A5 : ∀ z, prec s0 z → New z s0

/-- **NECESSARY GENESIS.** In every frame satisfying A1–A5, an actual, new
    configuration exists. -/
theorem NECESSARY_GENESIS (F : GenesisFrame) : ∃ z, F.Act z ∧ F.New z F.s0 := by
  obtain ⟨y, hc, _⟩ := F.A2 F.s0 F.A1
  obtain ⟨z, ht, hp, _⟩ := F.A3 y ⟨F.s0, hc⟩
  exact ⟨z, F.A4 F.s0 y z F.A1 hc ht, F.A5 z hp⟩

/-- A frame with every axiom except A4. -/
structure FrameWithoutA4 where
  S : Type
  s0 : S
  Act : S → Prop
  koruC : S → S → Prop
  koruT : S → S → Prop
  prec : S → S → Prop
  New : S → S → Prop
  A1 : Act s0
  A2 : ∀ x, Act x → ∃ y, koruC x y ∧ ¬ koruC y x
  A3 : ∀ y, (∃ x, koruC x y) → ∃ z, koruT y z ∧ prec s0 z ∧ ¬ prec z s0
  A5 : ∀ z, prec s0 z → New z s0

/-- **ACTUALISATION IS LOAD-BEARING.** A1, A2, A3 and A5 all hold, yet no actual
    configuration is new: without A4 the outward step and the later state stay
    merely possible. Genesis needs actualisation, not order alone. -/
theorem actualisation_is_load_bearing :
    ∃ F : FrameWithoutA4, ¬ ∃ z, F.Act z ∧ F.New z F.s0 := by
  refine ⟨⟨Bool, false, fun z => z = false, fun a b => a = false ∧ b = true,
    fun a b => a = true ∧ b = true, fun a b => a = false ∧ b = true,
    fun z _ => z = true, rfl, ?_, ?_, ?_⟩, ?_⟩
  · intro x hx
    exact ⟨true, ⟨hx, rfl⟩, fun h => Bool.noConfusion h.1⟩
  · intro y ⟨x, hx⟩
    exact ⟨true, ⟨hx.2, rfl⟩, ⟨rfl, rfl⟩, fun h => Bool.noConfusion h.1⟩
  · intro z hz
    exact hz.2
  · rintro ⟨z, hA, hN⟩
    rw [hA] at hN
    exact Bool.noConfusion hN

/-- The realised Koru chain (C1–C4): along any chain of realised composite
    steps, no state returns to any earlier one, and actuality carries forward. -/
structure KoruOrder (U : Type) where
  prec : U → U → Prop
  irrefl : ∀ a, ¬ prec a a
  trans : ∀ {a b c}, prec a b → prec b c → prec a c

theorem chain_strict {U : Type} (O : KoruOrder U) (u : Nat → U)
    (step : ∀ k, O.prec (u k) (u (k + 1))) :
    ∀ k d, O.prec (u k) (u (k + d + 1))
  | k, 0 => step k
  | k, d + 1 => O.trans (chain_strict O u step k d) (step (k + d + 1))

/-- **NO CYCLE OF ANY LENGTH.** -/
theorem NO_CYCLE_OF_ANY_LENGTH {U : Type} (O : KoruOrder U) (u : Nat → U)
    (step : ∀ k, O.prec (u k) (u (k + 1))) {k n : Nat} (h : k < n) : u n ≠ u k := by
  intro heq
  obtain ⟨d, rfl⟩ : ∃ d, n = k + d + 1 := ⟨n - k - 1, by omega⟩
  have hp := chain_strict O u step k d
  rw [heq] at hp
  exact O.irrefl _ hp

/-- **ACTUALITY CARRIES FORWARD.** -/
theorem ACTUALITY_CARRIES_FORWARD {U : Type} (Act : U → Prop) (u : Nat → U)
    (realised : ∀ k, Act (u k) → Act (u (k + 1))) (h0 : Act (u 0)) : ∀ n, Act (u n)
  | 0 => h0
  | n + 1 => realised n (ACTUALITY_CARRIES_FORWARD Act u realised h0 n)

#print axioms NECESSARY_GENESIS
#print axioms actualisation_is_load_bearing
#print axioms NO_CYCLE_OF_ANY_LENGTH
#print axioms ACTUALITY_CARRIES_FORWARD

end PhysicalBridges.G3NecessaryGenesis
