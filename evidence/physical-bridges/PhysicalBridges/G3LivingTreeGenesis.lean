import PhysicalBridges.LivingTreeGenerations

/-!
# Living Tree Genesis: actualisation is not a separate premise

`G3NecessaryGenesis` shows Genesis needs the actualisation axiom A4. On the
Living Tree, A4 is not an extra assumption: the physical premise `hRealizes`
(each cultivated step is a real physical step) already makes every generation
physically actual — reachable from the seed by realised physical steps. So the
physical premises of the proof shrink from four (A4, hRealizes, hCoverage,
hReflection) to three.

`LIVING_TREE_GENESIS`: given only `hRealizes`, every later generation is
physically actual, strictly later, new (never the seed again), and carries
every generation before it.
-/

namespace PhysicalBridges.G3LivingTreeGenesis

open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.KoruObjectiveWholeU

variable {T H E : Type}

/-- Physically actual: reachable from the seed by realised physical steps. -/
inductive PhysicallyActual (physicalStep : LivingTree T H E → LivingTree T H E → Prop)
    (seed : LivingTree T H E) : LivingTree T H E → Prop
  | seed : PhysicallyActual physicalStep seed seed
  | step {s t} : PhysicallyActual physicalStep seed s → physicalStep s t →
      PhysicallyActual physicalStep seed t

/-- A4 on the Living Tree follows from hRealizes. -/
theorem every_generation_is_actual (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E) (physicalStep : LivingTree T H E → LivingTree T H E → Prop)
    (hRealizes : ∀ n, physicalStep (grow J seed n) (cultivate J (grow J seed n))) :
    ∀ n, PhysicallyActual physicalStep seed (grow J seed n)
  | 0 => .seed
  | n + 1 => .step (every_generation_is_actual J seed physicalStep hRealizes n) (hRealizes n)

/-- **LIVING TREE GENESIS.** Given only `hRealizes`: every later generation is
    physically actual, strictly later, new, and carries all before it. -/
theorem LIVING_TREE_GENESIS (J : JokerExperiment T FiniteObjectiveU H)
    (seed : LivingTree T H E) (physicalStep : LivingTree T H E → LivingTree T H E → Prop)
    (hRealizes : ∀ n, physicalStep (grow J seed n) (cultivate J (grow J seed n)))
    (n : Nat) :
    PhysicallyActual physicalStep seed (grow J seed (n + 1)) ∧
    (grow J seed (n + 1)).epoch = seed.epoch + (n + 1) ∧
    grow J seed (n + 1) ≠ seed ∧
    (grow J seed (n + 1)).ancestors.length = seed.ancestors.length + (n + 1) := by
  have hE := epoch_advances_with_learning J seed (n + 1)
  refine ⟨every_generation_is_actual J seed physicalStep hRealizes (n + 1), hE, ?_,
    accumulated_knowledge_grows_each_generation J seed (n + 1)⟩
  intro h
  have := congrArg LivingTree.epoch h
  omega

#print axioms every_generation_is_actual
#print axioms LIVING_TREE_GENESIS

end PhysicalBridges.G3LivingTreeGenesis
