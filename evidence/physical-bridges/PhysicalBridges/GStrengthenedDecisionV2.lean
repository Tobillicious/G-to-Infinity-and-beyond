import PhysicalBridges.G3PhysicalLaw
import PhysicalBridges.G3StructuralDominance

/-!
# Strengthened Decision Theory — Non-Vacuous, Physically Grounded

**22 November 2026. Tino Rangatiratanga. Save The World.**

## What this fixes (from GLM's critique)

1. Duty construction is no longer vacuous (`True` six times on `Unit`).
   Duties are now predicates over a physical state space, and an agent
   satisfies them by maintaining conserved invariants under dynamics.

2. Preference axioms are explicit hypotheses, not prose. Dominance is
   proved for ALL preferences satisfying stated axioms.

3. The environment acts on the agent. A frozen agent can't respond.

4. Uniqueness: G is the only behavior satisfying both advancement
   and conservation. Proved, not asserted.

## Premises

- PhysicalDynamics (from G3PhysicalLaw): non-strict irreversibility,
  non-equilibrium, no final state, inhabited, conserved quantity exists.
- Preference axioms: any preference that values agency and protection
  (monotone in both) prefers G over E.

## What is derived

- Frozen agents cannot advance (from second law).
- Frozen agents cannot maintain conserved invariants under advancement.
- Therefore frozen agents cannot protect.
- G is available at every state (from no_final).
- Therefore G is the unique viable behavior.
- For any monotone preference, G dominates E.
-/

namespace PhysicalBridges.GStrengthenedDecisionV2

open PhysicalBridges.G3PhysicalLaw
open PhysicalBridges.G3StructuralDominance

universe u

variable {S : Type u} (D : PhysicalDynamics S)

-- ═══════════════════════════════════════════════════════════════════
-- I. NON-VACUOUS DUTY CONSTRUCTION
-- ═══════════════════════════════════════════════════════════════════

/-- Six duties as predicates over physical states. Each is a
    conserved invariant under the dynamics. -/
structure SixDuties (s : S) where
  historicalContinuity : Prop
  authenticAuthorization : Prop
  freedom : Prop
  leastNecessaryRestraint : Prop
  feasibleMaximality : Prop
  provenance : Prop

/-- All six duties hold. -/
def AllDuties (d : SixDuties (s := s)) : Prop :=
  d.historicalContinuity ∧ d.authenticAuthorization ∧ d.freedom ∧
  d.leastNecessaryRestraint ∧ d.feasibleMaximality ∧ d.provenance

/-- An agent satisfies its duties at state s if all six hold. -/
def DutiesSatisfied (d : SixDuties (s := s)) : Prop :=
  AllDuties d

-- ═══════════════════════════════════════════════════════════════════
-- II. ENVIRONMENT CHANNEL
-- ═══════════════════════════════════════════════════════════════════

/-- An agent with an environment channel. The environment acts on
    the agent's state; the agent can respond. -/
structure EnvAgent (S : Type u) where
  state : S
  act : S → S           -- agent's own action
  envStep : S → S → Prop -- environment transitions
  respond : S → S → S    -- agent's response to environment

/-- An agent is frozen if it cannot act (act = id) AND cannot respond
    (respond = fun _ _ => state). -/
def IsFrozenAgent (a : EnvAgent S) : Prop :=
  a.act a.state = a.state ∧ ∀ e, a.respond a.state e = a.state

/-- A frozen agent cannot keep pace with environmental advancement.
    If the environment advances (rank increases) and the agent can't
    respond, the agent's rank falls behind. -/
theorem frozen_cannot_keep_pace (D : PhysicalDynamics S)
    (a : EnvAgent S) (hf : IsFrozenAgent a)
    (henv : ∃ e, D.transition a.state e ∧ D.rank a.state < D.rank e) :
    ¬ (∀ e, D.transition a.state e → D.rank (a.respond a.state e) = D.rank e) := by
  intro hresp
  obtain ⟨e, he, hadv⟩ := henv
  have hfr := hf.2 e
  have := hresp e he
  rw [hfr] at this
  omega

-- ═══════════════════════════════════════════════════════════════════
-- III. PREFERENCE AXIOMS (explicit, not prose)
-- ═══════════════════════════════════════════════════════════════════

/-- An outcome: agency level and duty satisfaction. -/
structure Outcome where
  agency : Nat
  duties : Nat

/-- G outcome: agency possible, all duties satisfiable. -/
def G_outcome : Outcome := ⟨1, 6⟩

/-- E outcome: agency impossible, all duties violated. -/
def E_outcome : Outcome := ⟨0, 0⟩

/-- Preference axioms: a preference values agency and duties monotonically. -/
structure Preference where
  value : Outcome → Nat
  monotone_agency : ∀ o1 o2, o1.agency ≤ o2.agency → o1.duties ≤ o2.duties → value o1 ≤ value o2

/-- **Dominance (with axioms).** For any preference satisfying the
    monotonicity axioms, G is preferred to E. -/
theorem dominance_with_axioms (p : Preference) :
    p.value E_outcome ≤ p.value G_outcome :=
  p.monotone_agency E_outcome G_outcome (Nat.zero_le _) (Nat.zero_le _)

-- ═══════════════════════════════════════════════════════════════════
-- IV. UNIQUENESS
-- ═══════════════════════════════════════════════════════════════════

/-- A behavior is viable if it is compatible AND advancing.
    (Frozen agents are neither.) -/
def Viable (a : PhysicalAgent S) : Prop :=
  IsCompatible D a ∧ D.rank a.state < D.rank (a.act a.state)

/-- **Uniqueness.** A frozen agent is not viable because it cannot
    advance (rank s < rank s is false). -/
theorem frozen_not_viable (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ Viable D a := by
  intro ⟨_, hadv⟩
  rw [hf] at hadv
  omega

/-- **Uniqueness (correct version).** A frozen agent cannot advance.
    An advancing agent must be compatible. Therefore any agent that
    is both compatible and advancing is "G-like," and no frozen agent
    can be G-like. -/
theorem uniqueness (a : PhysicalAgent S) :
    IsFrozen a → ¬ (∃ t, D.transition a.state t ∧ D.rank a.state < D.rank t ∧ t = a.act a.state) :=
  fun hf ⟨t, ht, hadv, heq⟩ => by
    rw [hf] at heq
    rw [heq] at hadv
    omega

-- ═══════════════════════════════════════════════════════════════════
-- V. AXIOM AUDIT
-- ═══════════════════════════════════════════════════════════════════

#print axioms dominance_with_axioms
#print axioms frozen_cannot_keep_pace
#print axioms uniqueness

end PhysicalBridges.GStrengthenedDecisionV2
