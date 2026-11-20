import PhysicalBridges.BCRDB7CausalAccessibility
import PhysicalBridges.G3BCRDMicroscopicCandidate
import PhysicalBridges.G3PreQGComplete

/-!
# B7 → G3 backwards summit: state-determined locality as pre-QG evidence

Bridges the concrete B7 causal-accessibility evidence (exact relational
gating in the pinned M3d source matrices) to the G3 backwards summit
strategy (everything flows from BCRDIsQG, QG last).

Formalizes state-determined locality as a proposition, instantiates it
from the kernel-checked B7 results, provides a countermodel showing the
property is nontrivial, and states honestly what remains for full QG.

The backwards summit strategy:
  G1 — Something IS (proved, zero axioms)
  G2 — G is unique fixed point (proved, zero axioms)
  G3 — Universality: BCRDIsQG → all six X3 at every event (proved)
  QG — BCRD IS the actual physical dynamics (THE OPEN GATE)

B7 strengthens the case for QG by showing the BCRD source matrices
exhibit state-determined causal structure. It does not close the gate.

No changes to any existing definition, structure, or theorem.
-/

namespace PhysicalBridges.G3BCRDB7PreQGEvidence

open PhysicalBridges.BCRDComplexM3dStage
open PhysicalBridges.BCRDB7CausalAccessibility
open PhysicalBridges.G3BCRDMicroscopicCandidate
open PhysicalBridges.G3PreQGComplete
open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.BCRDActualRelationalFrame
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

-- ═══════════════════════════════════════════════════════════════════
-- 1. WHAT STATE-DETERMINED LOCALITY MEANS (as a Prop)
-- ═══════════════════════════════════════════════════════════════════

/-- State-determined locality: the same dynamics, applied to inputs
    differing only in a relational degree of freedom, produces
    different causal accessibility to a probe subsystem. One input
    activates the probe; the other leaves it dark. -/
def HasStateDeterminedLocality
    {S : Type} (evolve : S → S)
    (accessible : S → Prop) (inputA inputB : S) : Prop :=
  inputA ≠ inputB ∧
  accessible (evolve inputA) ∧
  ¬ accessible (evolve inputB)

-- ═══════════════════════════════════════════════════════════════════
-- 2. THE M3d SOURCE MATRICES HAVE IT
-- ═══════════════════════════════════════════════════════════════════

/-- The fixed four-stage compound evolution: W→C_LM→U_MR→C_LM. -/
def m3dCompoundEvolve (input : State) : State :=
  runStages [.endogenousW, .enabledLM, .middleRight, .enabledLM] input

/-- L1-site accessibility: does L-subsystem in the r=1 sector
    have nonzero amplitude? -/
def L1_accessible (s : State) : Prop := s (1 : Index) ≠ cz

/-- **The pinned M3d source matrices exhibit state-determined
    locality.** The L subsystem is causally accessible from one
    relational sector (M0, r=0 start) and causally inaccessible
    from the other (M1, r=1 start), under the same fixed dynamics.

    Kernel-checked evidence for BCRD B7. -/
theorem bcrd_m3d_has_state_determined_locality :
    HasStateDeterminedLocality m3dCompoundEvolve L1_accessible
      (basis 2) (basis 3) := by
  refine ⟨?_, L_site_activated_from_r0_start,
          fun h => h (L_site_dark_from_r1_start).2⟩
  intro h
  have h2 := congrFun h (2 : Index)
  have : basis 2 (2 : Index) ≠ basis 3 (2 : Index) := by decide +kernel
  exact this h2

-- ═══════════════════════════════════════════════════════════════════
-- 3. COUNTERMODEL: UNIFORM COUPLING FAILS B7
-- ═══════════════════════════════════════════════════════════════════

/-- Uniform coupling cannot exhibit state-determined locality
    because both inputs produce the same accessible output.
    When a dynamics maps every input to the same state, there is
    no relational gating — the antithesis of B7. -/
theorem uniform_coupling_fails_locality
    {S : Type} (evolve : S → S) (accessible : S → Prop)
    (a b : S) (_hab : a ≠ b)
    (hUniform : evolve a = evolve b) :
    ¬ HasStateDeterminedLocality evolve accessible a b := by
  intro ⟨_, hAcc, hInacc⟩
  exact hInacc (hUniform ▸ hAcc)

-- ═══════════════════════════════════════════════════════════════════
-- 4. THE SEMANTIC GAP REMAINS
-- ═══════════════════════════════════════════════════════════════════

/-- B7 state-determined locality is physics evidence. But the
    existing no-go theorem still applies: the W law alone does not
    determine all six original X3 duties for arbitrary subject
    interpretations.

    This conjunction is the honest backwards-summit position:
    genuine physics evidence AND acknowledged semantic gap. -/
theorem b7_evidence_with_semantic_gap :
    HasStateDeterminedLocality m3dCompoundEvolve L1_accessible
      (basis 2) (basis 3) ∧
    ¬ (∀ r : ParticularRelations SourceState Unit,
      ∀ s t, WSourcePhysicalLaw s t →
        OriginalX3 r.continues r.authorized r.free
          r.restrained r.maximal r.provenanced s t ()) :=
  ⟨bcrd_m3d_has_state_determined_locality,
   physical_W_law_alone_does_not_fix_all_subject_duties⟩

-- ═══════════════════════════════════════════════════════════════════
-- 5. WHAT B7 CONTRIBUTES TO THE BACKWARDS SUMMIT
-- ═══════════════════════════════════════════════════════════════════

/-- **BACKWARDS SUMMIT STATUS.**

    PROVED (zero conditions):
      G1: Something IS
      G2: G is unique fixed point

    PROVED (conditional on BCRDIsQG):
      G3: All six X3 at every event, no absolute E, eternal

    EVIDENCE FOR QG (kernel-checked, NOT a proof of QG):
      B7: State-determined causal accessibility in M3d source

    OPEN GATES:
      (a) Continuum/metric emergence from finite relational gating
      (b) Gravitational dynamics from state-dependent coupling
      (c) ForwardRealEventReflection: authentic semantic transfer
      (d) Physical nontermination of the actual dynamics

    This packages B7 evidence with the conditional G3 result. -/
theorem backwards_summit_b7_status :
    HasStateDeterminedLocality m3dCompoundEvolve L1_accessible
      (basis 2) (basis 3) ∧
    (∀ (S P : Type) (B : BCRDIsQG S P),
      ∀ s t, B.physicalStep s t →
        (∀ p, B.owed p →
          OriginalX3 B.r.continues B.r.authorized B.r.free
            B.r.restrained B.r.maximal B.r.provenanced s t p)) :=
  ⟨bcrd_m3d_has_state_determined_locality,
   fun S P B s t hPhys => (if_bcrd_then_all_six_and_no_E B s t hPhys).1⟩

#print axioms bcrd_m3d_has_state_determined_locality
#print axioms uniform_coupling_fails_locality
#print axioms b7_evidence_with_semantic_gap
#print axioms backwards_summit_b7_status

end PhysicalBridges.G3BCRDB7PreQGEvidence
