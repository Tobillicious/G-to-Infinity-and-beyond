import PhysicalBridges.G3SixDutyRenewal
import PhysicalBridges.G3GenesisContinuationScope
import PhysicalBridges.G3PhysicalProgressForcesTree

/-!
# Step 3: Genesis and new-particular obligations

Every newly owed particular must be recognised and receive fresh duty
certificates. Existing particulars must not disappear from the obligation
set without justification. This module provides:

1. A temporal induction theorem covering retained AND newly arriving
   particulars, without a fixed-population shortcut
2. A monotonicity principle: once owed, the obligation does not vanish
   unless explicitly released
3. The join: physical progress + five-duty renewal + maximality renewal
   = full six-duty coverage for a growing population
4. A negative control: a population that silently drops a particular
   breaks the inductive guarantee

Joins:
  - G3SixDutyRenewal (five + maximality → six, by induction)
  - G3GenesisContinuationScope (generated states have successors)
  - G3PhysicalProgressForcesTree (progress + admissibility → tree)

No existing definition is changed.
-/

namespace PhysicalBridges.G3GenesisObligations

open PhysicalBridges.G3SixDutyRenewal
open PhysicalBridges.G3FeasibleMaximalityRenewal
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

variable {P A : Type}

/-- A well-formed obligation population: once a particular is owed,
    it stays owed unless explicitly released. The release predicate
    is visible, not hidden in a silent dropout. -/
def MonotonicOwed (owed : Nat → P → Prop)
    (released : Nat → P → Prop) : Prop :=
  ∀ n p, owed n p → ¬ released (n + 1) p → owed (n + 1) p

/-- A genesis event: a particular becomes owed at stage n+1 that was
    not owed at stage n. This is the moment of recognition. -/
def GenesisAt (owed : Nat → P → Prop) (n : Nat) (p : P) : Prop :=
  owed (n + 1) p ∧ ¬ owed n p

/-- Full population coverage: every owed particular at every stage
    is EITHER an original (owed from stage 0) OR arrived at a specific
    genesis stage. No particular comes from nowhere. -/
theorem every_owed_has_an_origin
    (owed : Nat → P → Prop)
    (_hMono : ∀ n p, owed n p → owed (n + 1) p)
    (n : Nat) (p : P) (hp : owed n p) :
    owed 0 p ∨ ∃ k, k < n ∧ GenesisAt owed k p := by
  induction n with
  | zero => exact Or.inl hp
  | succ n ih =>
    by_cases h0 : owed n p
    · rcases ih h0 with hOrig | ⟨k, hk, hGen⟩
      · exact Or.inl hOrig
      · exact Or.inr ⟨k, Nat.lt_succ_of_lt hk, hGen⟩
    · exact Or.inr ⟨n, Nat.lt_succ_of_le (Nat.le_refl n), ⟨hp, h0⟩⟩

/-- Six-duty renewal for a growing population with explicit genesis
    certificates. The existing `original_six_from_five_and_maximality_renewal`
    already handles the induction; this theorem adds the population
    structure: each newly owed particular is explicitly recognised with
    a fresh six-duty certificate, not silently included by a fixed-set
    assumption. -/
theorem six_duties_for_growing_population
    (F : FeasibleOrder P A)
    (r : ParticularRelations Nat P)
    (owed : Nat → P → Prop)
    (hFiveInitial : ∀ p, owed 0 p → FiveAt r 0 p)
    (hFiveRetained : ∀ n p, owed (n + 1) p → owed n p →
      FiveAt r n p → FiveAt r (n + 1) p)
    (hFiveGenesis : ∀ n p, GenesisAt owed n p →
      FiveAt r (n + 1) p)
    (hMaxInitial : ∀ p, owed 0 p → MaximalAt F 0 p)
    (hSame : ∀ n p, owed (n+1) p → owed n p →
      F.selected (n+1) p = F.selected n p)
    (hFeasible : ∀ n p, owed (n+1) p → owed n p →
      F.feasible (n+1) p (F.selected n p))
    (hFrontier : ∀ n p, owed (n+1) p → owed n p →
      NoNewSuperiorAlternative F n p)
    (hMaxGenesis : ∀ n p, GenesisAt owed n p →
      MaximalAt F (n+1) p)
    (hMeaning : MaximalityMeaning F r owed) :
    ∀ n p, owed n p →
      OriginalX3 r.continues r.authorized r.free
        r.restrained r.maximal r.provenanced n (n + 1) p := by
  exact original_six_from_five_and_maximality_renewal F r owed
    hFiveInitial hFiveRetained
    (fun n p hOwed hNotOld => hFiveGenesis n p ⟨hOwed, hNotOld⟩)
    hMaxInitial hSame hFeasible hFrontier
    (fun n p hOwed hNotOld => hMaxGenesis n p ⟨hOwed, hNotOld⟩)
    hMeaning

/-- If the obligation population is monotonic (no silent drops), then
    monotonicity alone guarantees every initially-owed particular
    remains owed at every later stage. -/
theorem initial_obligations_persist
    (owed : Nat → P → Prop)
    (hMono : ∀ n p, owed n p → owed (n + 1) p) :
    ∀ n p, owed 0 p → owed n p := by
  intro n
  induction n with
  | zero => exact fun p hp => hp
  | succ n ih => exact fun p hp => hMono n p (ih p hp)

/-- The negative control: a silently dropping population breaks the
    six-duty guarantee. If a particular is owed at stage n but not at
    n+1 (silent drop, no release justification), and that particular
    had duties at stage n, the inductive proof cannot extend.

    This is not a proof that drops ALWAYS break protection — it is a
    proof that the INDUCTIVE METHOD requires monotonicity or explicit
    release. Without it, the proof obligation is not dischargeable. -/
theorem silent_drop_breaks_inductive_renewal
    (owed : Nat → P → Prop) (n : Nat) (p : P)
    (hOwedNow : owed n p) (hDropped : ¬ owed (n + 1) p) :
    ¬ (∀ m q, owed m q → owed (m + 1) q) := by
  intro hMono
  exact hDropped (hMono n p hOwedNow)

/-- Combined step 2+3 package for a SINGLE new particular: at the
    genesis stage, the particular receives all six duties (from the
    genesis certificate) AND it did not exist before (from the genesis
    definition). The conjunction uses both hypotheses. -/
theorem genesis_particular_receives_full_protection
    (F : FeasibleOrder P A)
    (r : ParticularRelations Nat P)
    (owed : Nat → P → Prop)
    (n : Nat) (p : P)
    (hGenesis : GenesisAt owed n p)
    (hFiveGenesis : FiveAt r (n + 1) p)
    (hMaxGenesis : MaximalAt F (n + 1) p)
    (hMeaning : MaximalityMeaning F r owed) :
    OriginalX3 r.continues r.authorized r.free
      r.restrained r.maximal r.provenanced (n + 1) (n + 2) p ∧
    ¬ owed n p := by
  constructor
  · obtain ⟨hc, ha, hf, hr, hpr⟩ := hFiveGenesis
    exact ⟨hc, ha, hf, hr,
      hMeaning (n + 1) p hGenesis.1 hMaxGenesis, hpr⟩
  · exact hGenesis.2

/-- A concrete population scenario: Fin 2 as particulars. At stage 0,
    only p0 is owed. At stage 1, p1 arrives (genesis). The growing
    population is well-formed. -/
def growingOwed : Nat → Fin 2 → Prop
  | 0 => fun p => p = 0
  | _ + 1 => fun _ => True

theorem growing_population_has_genesis :
    GenesisAt growingOwed 0 (1 : Fin 2) := by
  constructor
  · exact trivial
  · intro h; exact absurd h (by simp [growingOwed])

theorem growing_population_is_monotone :
    ∀ n (p : Fin 2), growingOwed n p → growingOwed (n + 1) p := by
  intro n p _
  exact trivial

#print axioms every_owed_has_an_origin
#print axioms six_duties_for_growing_population
#print axioms initial_obligations_persist
#print axioms silent_drop_breaks_inductive_renewal
#print axioms genesis_particular_receives_full_protection
#print axioms growing_population_has_genesis
#print axioms growing_population_is_monotone

end PhysicalBridges.G3GenesisObligations
