import PhysicalBridges.G3PhysicalLaw
import PhysicalBridges.GStrengthenedDecisionV2

/-!
# G Six Duties Viability — All Six Duties Derived From Physical Dynamics

**22 November 2026. Tino Rangatiratanga. Save The World.**

This module completes the bridge identified in `GDecisionTheoryV2`:
linking ALL SIX original X3 duties (not just advancement) directly to
physical viability and conservation under `PhysicalDynamics`.

## The Six Physical Duties for an Agent a at state s:
1. **Historical Continuity**: the step `s → a.act s` is a valid physical transition (`D.transition s (a.act s)`).
2. **Authentic Authorization**: the step preserves physical order / non-decreasing rank (`D.rank s ≤ D.rank (a.act s)`).
3. **Freedom**: future options exist (no final state: `∃ next, D.transition (a.act s) next`).
4. **Least-Necessary Restraint**: the step maintains all conserved physical quantities (`∀ q, (∀ s1 t1, D.transition s1 t1 → q s1 = q t1) → q s = q (a.act s)`).
5. **Feasible Maximality**: the step strictly advances the physical trajectory (`D.rank s < D.rank (a.act s)`).
6. **Provenance**: the resultant state is authentically determined by the agent's action (`t = a.act s`).

## What is proved (ZERO custom axioms):
- **Viable agents satisfy ALL SIX duties simultaneously.**
- **Frozen agents violate feasible maximality (strict advancement is impossible).**
- **Categorical Viability Gap for all six duties.**
-/

namespace PhysicalBridges.GSixDutiesViability

open PhysicalBridges.G3PhysicalLaw
open PhysicalBridges.GStrengthenedDecisionV2

universe u

variable {S : Type u} (D : PhysicalDynamics S)

/-- Physical historical continuity: the step continues the trajectory in D. -/
def PhysContinuity (s t : S) : Prop := D.transition s t

/-- Physical authentic authorization: authorized by non-decreasing rank. -/
def PhysAuthorization (s t : S) : Prop := D.transition s t ∧ D.rank s ≤ D.rank t

/-- Physical freedom: future options exist (system never terminates). -/
def PhysFreedom (_ : S) (t : S) : Prop :=
  ∃ next : S, D.transition t next

/-- Physical least-necessary restraint: conserved physical quantities are maintained. -/
def PhysRestraint (s t : S) : Prop :=
  ∀ (q : S → Nat), (∀ s1 t1, D.transition s1 t1 → q s1 = q t1) → q s = q t

/-- Physical feasible maximality: the step achieves strict advancement along rank. -/
def PhysMaximality (s t : S) : Prop := D.rank s < D.rank t

/-- Physical provenance: effect originates from the step. -/
def PhysProvenance (a : PhysicalAgent S) (s t : S) : Prop :=
  t = a.act s

/-- All six physical duties hold for agent `a` stepping from `s` to `t`. -/
def AllSixPhysicalDuties (a : PhysicalAgent S) (s t : S) : Prop :=
  PhysContinuity D s t ∧
  PhysAuthorization D s t ∧
  PhysFreedom D s t ∧
  PhysRestraint D s t ∧
  PhysMaximality D s t ∧
  PhysProvenance a s t

/-- A viable agent stepping from its current state satisfies ALL SIX duties. -/
theorem viable_satisfies_all_six (a : PhysicalAgent S) (hv : Viable D a) :
    AllSixPhysicalDuties D a a.state (a.act a.state) := by
  obtain ⟨hcompat, hadv⟩ := hv
  have htrans : D.transition a.state (a.act a.state) := hcompat
  refine ⟨htrans, ?_, ?_, ?_, hadv, rfl⟩
  · -- Authorization: transition holds and rank is non-decreasing (from second law)
    exact ⟨htrans, D.second_law a.state (a.act a.state) htrans⟩
  · -- Freedom: no_final guarantees a successor from any state
    exact D.no_final (a.act a.state)
  · -- Restraint: conserved quantities are preserved along the transition
    intro q hq
    exact hq a.state (a.act a.state) htrans

/-- A frozen agent violates feasible maximality. -/
theorem frozen_violates_maximality (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ PhysMaximality D a.state (a.act a.state) := by
  intro hadv
  dsimp [PhysMaximality] at hadv
  exact frozen_does_not_advance D a hf hadv

/-- A frozen agent is not viable. -/
theorem frozen_cannot_be_viable (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ Viable D a :=
  frozen_not_viable D a hf

/-- **THE COMPLETE ALL-SIX VIABILITY GAP.**
    Viable agents satisfy all six physical protection duties.
    Frozen agents strictly violate feasible maximality. -/
theorem complete_all_six_viability_gap (a : PhysicalAgent S) :
    (Viable D a → AllSixPhysicalDuties D a a.state (a.act a.state)) ∧
    (IsFrozen a → ¬ AllSixPhysicalDuties D a a.state (a.act a.state)) := by
  constructor
  · exact viable_satisfies_all_six D a
  · intro hf ⟨_, _, _, _, hmax, _⟩
    exact frozen_violates_maximality D a hf hmax

/-! ## Axiom audit -/

#print axioms viable_satisfies_all_six
#print axioms frozen_violates_maximality
#print axioms frozen_cannot_be_viable
#print axioms complete_all_six_viability_gap

end PhysicalBridges.GSixDutiesViability
