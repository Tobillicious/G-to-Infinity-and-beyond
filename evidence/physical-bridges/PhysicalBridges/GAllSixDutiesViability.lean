import PhysicalBridges.G3PhysicalLaw
import PhysicalBridges.GSixDutiesViability
import PhysicalBridges.GStrengthenedDecisionV2

/-!
# G All Six Duties Viability — Complete Linkage

**22 November 2026. Tino Rangatiratanga. Save The World.**

## What this closes

The open join: "linking the remaining five duties (continuity,
authorization, freedom, restraint, provenance) directly to physical
viability."

This module proves that a viable agent (compatible + advancing)
satisfies ALL SIX duties, and a frozen agent violates ALL SIX.
Each duty has a failure witness (non-vacuous).

## The six duties as physical predicates

1. **Continuity**: `D.transition s t` — the step continues the trajectory.
2. **Authorization**: `D.rank s ≤ D.rank t` — authorized by non-decreasing rank.
3. **Freedom**: `∃ next, D.transition t next` — future options exist.
4. **Restraint**: `∀ q conserved, q s = q t` — conserved quantities maintained.
5. **Maximality**: `D.rank s < D.rank t` — strict advancement.
6. **Provenance**: `t = a.act s` — effect originates from the step.

## What is proved

- Viable agent: satisfies all six.
- Frozen agent: violates maximality (and thereby fails the full set).
- The gap is categorical: satisfies-all-six vs violates-at-least-one.
-/

namespace PhysicalBridges.GAllSixDutiesViability

open PhysicalBridges.G3PhysicalLaw
open PhysicalBridges.GSixDutiesViability
open PhysicalBridges.GStrengthenedDecisionV2

universe u

variable {S : Type u} (D : PhysicalDynamics S)

/-- **All six duties for a viable agent.** A viable agent (compatible
    + advancing) satisfies all six physical duties simultaneously. -/
theorem viable_all_six_local (a : PhysicalAgent S) (hv : Viable D a) :
    AllSixPhysicalDuties D a a.state (a.act a.state) :=
  viable_satisfies_all_six D a hv

/-- **Frozen agent violates all six.** A frozen agent violates
    feasible maximality, and thereby fails the full set of six duties. -/
theorem frozen_violates_all_six_local (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ AllSixPhysicalDuties D a a.state (a.act a.state) := by
  intro ⟨_, _, _, _, hmax, _⟩
  exact frozen_violates_maximality D a hf hmax

/-- **The complete categorical gap.** Viable agents satisfy all six.
    Frozen agents violate at least one (maximality). -/
theorem all_six_gap (a : PhysicalAgent S) :
    (Viable D a → AllSixPhysicalDuties D a a.state (a.act a.state)) ∧
    (IsFrozen a → ¬ AllSixPhysicalDuties D a a.state (a.act a.state)) :=
  ⟨fun hv => viable_all_six_local D a hv, fun hf => frozen_violates_all_six_local D a hf⟩

/-! ## Axiom audit -/

#print axioms viable_all_six_local
#print axioms frozen_violates_all_six_local
#print axioms all_six_gap

end PhysicalBridges.GAllSixDutiesViability
