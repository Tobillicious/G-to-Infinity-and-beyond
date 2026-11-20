import PhysicalBridges.LivingTreeGenerations
import PhysicalBridges.EverestActualWEventJoin
/-!
# Coverage on the Living Tree: exactly seed alignment plus W-faithful learning

`hCoverage` (canonical complete W-event coverage) is one of the three physical
premises of the proof of God. Over an arbitrary physical domain it is a large
claim. On the Living Tree's own realised events it is exactly two checkable
conditions:

1. the seed matches the objective whole at its epoch, and
2. learning is W-faithful: each learned world advances the whole by exactly one
   objective step.

`COVERAGE_IFF_ALIGNED_AND_W_FAITHFUL` proves the equivalence. On these events
`hRealizes` holds by construction (`tree_realizes_itself`).

Scope, stated plainly: this covers the tree's own events. Whether a physical
domain consists only of such events is a separate closure claim; the
fifth-cause countermodel (`IR124`) shows it cannot be assumed, and
`learned_genesis_non_W_change_refutes_canonical_coverage` shows W-faithfulness
cannot be dropped.
-/

namespace PhysicalBridges.G3TreeCoverage

open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.EverestActualWEventJoin

variable {T H E : Type}

/-- The tree's own realised steps. -/
def treeStep (J : JokerExperiment T FiniteObjectiveU H) (seed : LivingTree T H E)
    (s t : LivingTree T H E) : Prop :=
  ∃ n, s = grow J seed n ∧ t = cultivate J s

/-- W-faithful learning: each learned world advances the whole by exactly one
    objective step. -/
def WFaithful (J : JokerExperiment T FiniteObjectiveU H) (seed : LivingTree T H E) : Prop :=
  ∀ n, (cultivate J (grow J seed n)).whole = objectiveStep (grow J seed n).whole

theorem aligned_every_generation (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E) (U : FiniteObjectiveU)
    (hSeed : seed.whole = objectiveAt U seed.epoch) (hW : WFaithful J seed) :
    ∀ n, (grow J seed n).whole = objectiveAt U (grow J seed n).epoch
  | 0 => hSeed
  | n + 1 => by
    show (cultivate J (grow J seed n)).whole = objectiveAt U ((grow J seed n).epoch + 1)
    rw [hW n, aligned_every_generation J seed U hSeed hW n]
    rfl

/-- **COVERAGE IS SEED ALIGNMENT PLUS W-FAITHFUL LEARNING.** On the tree's own
    realised steps, canonical complete W-event coverage holds exactly when the
    seed matches the objective whole and every learned step advances it by one
    objective step. -/
theorem COVERAGE_IFF_ALIGNED_AND_W_FAITHFUL (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E) (U : FiniteObjectiveU) :
    CompleteWEventCoverage (treeStep J seed) (treeStep J seed)
        (fun s => s.whole) (fun s => s.epoch) U ↔
      (seed.whole = objectiveAt U seed.epoch ∧ WFaithful J seed) := by
  constructor
  · intro hC
    have h0 := hC (grow J seed 0) (cultivate J (grow J seed 0)) ⟨0, rfl, rfl⟩
    refine ⟨h0.2.1, fun n => ?_⟩
    obtain ⟨_, hs, ht, _⟩ := hC (grow J seed n) (cultivate J (grow J seed n)) ⟨n, rfl, rfl⟩
    dsimp only at hs ht
    rw [ht, hs]
    rfl
  · rintro ⟨hSeed, hW⟩ s t ⟨n, rfl, rfl⟩
    exact ⟨⟨n, rfl, rfl⟩, aligned_every_generation J seed U hSeed hW n,
      aligned_every_generation J seed U hSeed hW (n + 1), rfl⟩

/-- The tree's own steps realise themselves: hRealizes holds by construction. -/
theorem tree_realizes_itself (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E) :
    ∀ n, treeStep J seed (grow J seed n) (cultivate J (grow J seed n)) :=
  fun n => ⟨n, rfl, rfl⟩

#print axioms aligned_every_generation
#print axioms COVERAGE_IFF_ALIGNED_AND_W_FAITHFUL
#print axioms tree_realizes_itself

end PhysicalBridges.G3TreeCoverage
