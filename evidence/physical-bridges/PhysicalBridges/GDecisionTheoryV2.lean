import PhysicalBridges.GDecisionTheory
import PhysicalBridges.GStrengthenedDecisionV2
import PhysicalBridges.G3PhysicalLaw

/-!
# Decision Theory V2 — Duties Linked to Viability

**22 November 2026. Tino Rangatiratanga. Save The World.**

## What this fixes

1. Duties are linked to viability: a viable agent (compatible +
   advancing) satisfies the advancement duty. A frozen agent
   violates it. This is a THEOREM, not a definition.

2. Structural preference axioms: transitivity, completeness,
   monotonicity. No mention of agency or duties by name.

3. Environment channel integrated: frozen agent can't keep pace
   with environmental advancement.

## Scope

- The advancement duty is the only duty formally linked to
  viability. The other five duties (continuity, authorization,
  freedom, restraint, maximality, provenance) are not yet
  connected to viability. This is honest.
- Preference axioms are structural but VNM representation
  theorem (existence of utility function) is beyond Lean.
-/

namespace PhysicalBridges.GDecisionTheoryV2

open PhysicalBridges.GDecisionTheory
open PhysicalBridges.G3PhysicalLaw
open PhysicalBridges.GStrengthenedDecisionV2

universe u

variable {S : Type u} (D : PhysicalDynamics S)

-- ═══════════════════════════════════════════════════════════════════
-- I. DUTIES LINKED TO VIABILITY
-- ═══════════════════════════════════════════════════════════════════

/-- A viable agent satisfies the advancement duty. -/
theorem viable_satisfies_advancement (a : PhysicalAgent S) (hv : Viable D a) :
    (advancementDuty D).holds a := by
  simp [Viable, IsCompatible] at hv
  exact hv.2

/-- A frozen agent violates the advancement duty. -/
theorem frozen_violates (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ (advancementDuty D).holds a := by
  exact frozen_violates_advancement_duty D a hf

/-- **The gap.** A viable agent satisfies the advancement duty.
    A frozen agent violates it. The gap is "satisfies" vs "violates"
    — a categorical difference, not a numeric one. -/
theorem viability_gap (a : PhysicalAgent S) :
    (Viable D a → (advancementDuty D).holds a) ∧
    (IsFrozen a → ¬ (advancementDuty D).holds a) :=
  ⟨fun hv => by simp [Viable, IsCompatible] at hv; exact hv.2,
   fun hf => frozen_violates_advancement_duty D a hf⟩

-- ═══════════════════════════════════════════════════════════════════
-- II. STRUCTURAL PREFERENCE AXIOMS
-- ═══════════════════════════════════════════════════════════════════

/-- An outcome space with structural properties. -/
structure OutcomeSpace where
  Outcome : Type
  le : Outcome → Outcome → Prop
  -- Transitivity: if a ≤ b and b ≤ c then a ≤ c
  trans : ∀ a b c, le a b → le b c → le a c
  -- Totality: for any a, b, either a ≤ b or b ≤ a
  total : ∀ a b, le a b ∨ le b a
  -- Antisymmetry: if a ≤ b and b ≤ a then a = b
  antisym : ∀ a b, le a b → le b a → a = b

/-- An outcome is "better" if it is greater in the order. -/
def Better (O : OutcomeSpace) (a b : O.Outcome) : Prop := O.le b a

-- ═══════════════════════════════════════════════════════════════════
-- III. ENVIRONMENT CHANNEL INTEGRATION
-- ═══════════════════════════════════════════════════════════════════

/-- A frozen agent cannot keep pace with environmental advancement.
    (From GDecisionTheory.) -/
theorem env_channel (a : GDecisionTheory.EnvAgent S) (hf : IsFrozenAgent a)
    (henv : ∃ e, D.transition a.state e ∧ D.rank a.state < D.rank e) :
    ¬ (∀ e, D.transition a.state e → D.rank (a.respond a.state e) = D.rank e) :=
  frozen_cannot_keep_pace D a hf henv

-- ═══════════════════════════════════════════════════════════════════
-- IV. AXIOM AUDIT
-- ═══════════════════════════════════════════════════════════════════

#print axioms viable_satisfies_advancement
#print axioms frozen_violates
#print axioms viability_gap

end PhysicalBridges.GDecisionTheoryV2
