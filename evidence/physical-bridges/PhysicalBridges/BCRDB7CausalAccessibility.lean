import PhysicalBridges.BCRDB7ExactRelationGate

/-!
# B7 causal accessibility: full compound relational gating

Extends the B7 seed (BCRDB7ExactRelationGate) from the two-stage
W→C_LM discrimination to the FULL four-stage compound
W→C_LM→U_MR→C_LM.

The same pinned source operators, the same unitary sequence, applied
to two inputs that differ ONLY in their relational bit (M0 vs M1):

  • From M0 (r=0 sector): W swaps to M1 (r=1), and C_LM activates
    the L–M partial swap in the r=1 sector. The L site receives
    nonzero amplitude. All three subsystems L, M, R participate.

  • From M1 (r=1 sector): W swaps to M0 (r=0), and C_LM is the
    identity in the r=0 sector. The L site stays dark. Only M and R
    exchange amplitude.

This IS state-determined causal accessibility: the relational state
of the input controls which subsystem pairs can exchange information
through the same fixed dynamics. No background geometry is changed
between the two cases; the gating is endogenous.

This does NOT demonstrate continuum geometry emergence, gravitational
dynamics, authentic subject semantics, or universal G3. It is exact
algebraic physics evidence for BCRD B7 (self-determined locality)
within the finite M3d source model.

No changes to any original definition, operator, or prior theorem.
-/

namespace PhysicalBridges.BCRDB7CausalAccessibility

open PhysicalBridges.BCRDComplexM3dStage
open PhysicalBridges.BCRDB7ExactRelationGate
open PhysicalBridges.FrozenBCRDEvents

-- ═══════════════════════════════════════════════════════════════════
-- FULL FOUR-STAGE COMPOUND FROM BOTH RELATIONAL SECTORS
-- ═══════════════════════════════════════════════════════════════════

/-- Full four-stage compound from M1 (relational bit 1).
    W swaps M1→M0 (into r=0 sector), then all controlled stages
    act in the r=0 sector where C_LM is the identity. -/
def fullFromM1 : State :=
  runStages [.endogenousW, .enabledLM, .middleRight, .enabledLM] (basis 3)

-- ═══════════════════════════════════════════════════════════════════
-- 1. FULL COMPOUND OUTPUTS DIFFER
-- ═══════════════════════════════════════════════════════════════════

/-- The full four-stage compounds from M0 and M1 produce different
    quantum states. Same dynamics, different relational input,
    different output. -/
theorem full_compound_outputs_differ :
    fullFourStageRun ≠ fullFromM1 := by
  intro h
  have h1 := congrFun h (1 : Index)
  have bad : fullFourStageRun (1 : Index) ≠ fullFromM1 (1 : Index) := by
    decide +kernel
  exact bad h1

-- ═══════════════════════════════════════════════════════════════════
-- 2. UNITARITY: BOTH OUTPUTS ARE NORM ONE
-- ═══════════════════════════════════════════════════════════════════

/-- Full compound from M0 (r=0 start) is norm one. -/
theorem full_compound_from_M0_norm_one :
    norm2 fullFourStageRun = so :=
  full_compound_source_history_retains_quantum_norm

/-- Full compound from M1 (r=1 start) is norm one. No information
    is lost through the relational gating — it redirects amplitude,
    it does not dissipate it. -/
theorem full_compound_from_M1_norm_one :
    norm2 fullFromM1 = so := by decide +kernel

-- ═══════════════════════════════════════════════════════════════════
-- 3. L-SITE CAUSAL ACCESSIBILITY: THE KEY DISCRIMINATOR
-- ═══════════════════════════════════════════════════════════════════

/-- From M0 start (r=0 → W → r=1 sector): the L site receives
    nonzero amplitude. C_LM activates L–M coupling in the r=1
    sector, and amplitude flows from M to L. -/
theorem L_site_activated_from_r0_start :
    fullFourStageRun (1 : Index) ≠ cz := by decide +kernel

/-- From M1 start (r=1 → W → r=0 sector): the L site stays
    completely dark. C_LM is the identity in the r=0 sector,
    so no amplitude ever reaches L. -/
theorem L_site_dark_from_r1_start :
    fullFromM1 (0 : Index) = cz ∧ fullFromM1 (1 : Index) = cz := by
  decide +kernel

/-- The L-site amplitude is the EXACT discriminator between the
    two relational sectors under the full compound evolution.
    Same operators, same sequence, different relational input,
    different causal pathway to L. -/
theorem L_site_discriminates_relational_sectors :
    fullFourStageRun (1 : Index) ≠ cz ∧
    fullFromM1 (1 : Index) = cz := by
  exact ⟨L_site_activated_from_r0_start,
         (L_site_dark_from_r1_start).2⟩

-- ═══════════════════════════════════════════════════════════════════
-- 4. R-SITE: UNIVERSALLY ACCESSIBLE (BOTH SECTORS)
-- ═══════════════════════════════════════════════════════════════════

/-- From M0 start: the R site receives nonzero amplitude. -/
theorem R_site_activated_from_r0_start :
    fullFourStageRun (5 : Index) ≠ cz := by decide +kernel

/-- From M1 start: the R site ALSO receives nonzero amplitude.
    U_MR mixes M and R regardless of relational sector.
    R's accessibility is NOT state-gated (unlike L). -/
theorem R_site_activated_from_r1_start :
    fullFromM1 (4 : Index) ≠ cz := by decide +kernel

/-- R-site accessibility is universal: amplitude reaches R from
    BOTH relational starting sectors. This contrast with L's
    state-gated accessibility is what makes the gating selective
    rather than trivial (which would be all-or-nothing). -/
theorem R_site_universal_accessibility :
    fullFourStageRun (5 : Index) ≠ cz ∧
    fullFromM1 (4 : Index) ≠ cz := by
  exact ⟨R_site_activated_from_r0_start,
         R_site_activated_from_r1_start⟩

-- ═══════════════════════════════════════════════════════════════════
-- 5. SECTOR CONFINEMENT: r=0 START STAYS IN r=0
-- ═══════════════════════════════════════════════════════════════════

/-- From M1 start, after W swaps to r=0 sector, the full compound
    produces amplitude ONLY at even indices (r=0 sector: L0, M0, R0).
    All odd-index (r=1 sector) amplitudes are exactly zero.
    The relational sector is preserved through the full compound. -/
theorem r1_start_confined_to_r0_sector :
    fullFromM1 (1 : Index) = cz ∧
    fullFromM1 (3 : Index) = cz ∧
    fullFromM1 (5 : Index) = cz := by decide +kernel

/-- From M0 start, after W swaps to r=1 sector, the full compound
    produces amplitude ONLY at odd indices (r=1 sector: L1, M1, R1).
    All even-index (r=0 sector) amplitudes are exactly zero.
    The two sectors are dynamically isolated. -/
theorem r0_start_confined_to_r1_sector :
    fullFourStageRun (0 : Index) = cz ∧
    fullFourStageRun (2 : Index) = cz ∧
    fullFourStageRun (4 : Index) = cz := by decide +kernel

-- ═══════════════════════════════════════════════════════════════════
-- 6. THREE-BODY PARTICIPATION FROM r=0 START
-- ═══════════════════════════════════════════════════════════════════

/-- From M0 start, the full compound distributes amplitude across
    ALL THREE matter subsystems (L, M, R) in the r=1 sector.
    The state-gated L–M coupling plus sector-independent M–R
    coupling creates a genuine three-body quantum state. -/
theorem three_body_participation_from_r0_start :
    fullFourStageRun (1 : Index) ≠ cz ∧
    fullFourStageRun (3 : Index) ≠ cz ∧
    fullFourStageRun (5 : Index) ≠ cz := by decide +kernel

/-- From M1 start, the full compound distributes amplitude across
    only TWO matter subsystems (M and R) in the r=0 sector.
    L is excluded because the relational gating is off. -/
theorem two_body_only_from_r1_start :
    fullFromM1 (0 : Index) = cz ∧
    fullFromM1 (1 : Index) = cz ∧
    fullFromM1 (2 : Index) ≠ cz ∧
    fullFromM1 (4 : Index) ≠ cz := by decide +kernel

-- ═══════════════════════════════════════════════════════════════════
-- 7. GENUINE SUPERPOSITION (NOT A PERMUTATION)
-- ═══════════════════════════════════════════════════════════════════

/-- The full compound from M0 produces a genuine three-site
    superposition, not any single basis state. -/
theorem full_compound_from_M0_not_any_basis :
    ¬ ∃ k : Index, fullFourStageRun = basis k := by
  intro ⟨k, h⟩
  have h1 := congrFun h (1 : Index)
  have h3 := congrFun h (3 : Index)
  have bad : ∀ j : Index,
      ¬ (fullFourStageRun (1 : Index) = basis j (1 : Index) ∧
         fullFourStageRun (3 : Index) = basis j (3 : Index)) := by
    decide +kernel
  exact bad k ⟨h1, h3⟩

/-- The full compound from M1 produces a genuine two-site
    superposition, not any single basis state. -/
theorem full_compound_from_M1_not_any_basis :
    ¬ ∃ k : Index, fullFromM1 = basis k := by
  intro ⟨k, h⟩
  have h2 := congrFun h (2 : Index)
  have h4 := congrFun h (4 : Index)
  have bad : ∀ j : Index,
      ¬ (fullFromM1 (2 : Index) = basis j (2 : Index) ∧
         fullFromM1 (4 : Index) = basis j (4 : Index)) := by
    decide +kernel
  exact bad k ⟨h2, h4⟩

-- ═══════════════════════════════════════════════════════════════════
-- 8. REVERSIBLE RELATIONAL CONTROL
-- ═══════════════════════════════════════════════════════════════════

/-- W is an involution on the M-sector basis states: applying W
    twice returns to the starting state. The relational switch
    can be toggled on and off. -/
theorem W_is_involution_on_M0 :
    matVec sourceW (matVec sourceW (basis 2)) = basis 2 := by
  apply funext; intro i
  have h : ∀ j : Index,
      matVec sourceW (matVec sourceW (basis 2)) j = basis 2 j := by
    decide +kernel
  exact h i

theorem W_is_involution_on_M1 :
    matVec sourceW (matVec sourceW (basis 3)) = basis 3 := by
  apply funext; intro i
  have h : ∀ j : Index,
      matVec sourceW (matVec sourceW (basis 3)) j = basis 3 j := by
    decide +kernel
  exact h i

-- ═══════════════════════════════════════════════════════════════════
-- 9. DENSITY MATRIX DISTINGUISHABILITY
-- ═══════════════════════════════════════════════════════════════════

/-- The density matrices of the two full compound outputs differ
    at the L1-L1 diagonal entry: nonzero for the r=0 start (which
    activated L–M coupling) and zero for the r=1 start (which did
    not). An experimenter measuring L-site occupation distinguishes
    the relational sectors without disturbing the dynamics. -/
theorem density_L1_diagonal_distinguishes_sectors :
    density fullFourStageRun (1 : Index) (1 : Index) ≠
    density fullFromM1 (1 : Index) (1 : Index) := by
  decide +kernel

/-- The r=1 start has zero L1 density (L is causally inaccessible). -/
theorem density_L1_zero_from_r1_start :
    density fullFromM1 (1 : Index) (1 : Index) = cz := by
  decide +kernel

-- ═══════════════════════════════════════════════════════════════════
-- 10. MASTER THEOREM: STATE-DETERMINED CAUSAL ACCESSIBILITY
-- ═══════════════════════════════════════════════════════════════════

/-- **STATE-DETERMINED CAUSAL ACCESSIBILITY.** The full four-stage
    BCRD compound, applied to inputs differing only in their
    relational bit, produces:

    (1) Different quantum states (relational gating survives all stages)
    (2) Both norm-one (no information lost)
    (3) L accessible from one sector, dark from the other
    (4) R accessible from both sectors
    (5) Three-body vs two-body participation
    (6) Neither output is a basis state (genuine superpositions)
    (7) Density matrices distinguish sectors at L

    This is B7: self-determined locality. The relational state of the
    input controls the causal accessibility structure through the
    SAME fixed unitary dynamics. No external geometry was changed.

    What this does NOT prove: that this finite gating IS gravitational
    spacetime geometry, that the M3d model exhausts physical dynamics,
    or that authentic subject semantics follow from the coupling. -/
theorem state_determines_causal_accessibility :
    fullFourStageRun ≠ fullFromM1 ∧
    norm2 fullFourStageRun = so ∧
    norm2 fullFromM1 = so ∧
    fullFourStageRun (1 : Index) ≠ cz ∧
    fullFromM1 (1 : Index) = cz ∧
    fullFourStageRun (5 : Index) ≠ cz ∧
    fullFromM1 (4 : Index) ≠ cz ∧
    density fullFourStageRun (1 : Index) (1 : Index) ≠
      density fullFromM1 (1 : Index) (1 : Index) := by
  exact ⟨full_compound_outputs_differ,
         full_compound_from_M0_norm_one,
         full_compound_from_M1_norm_one,
         L_site_activated_from_r0_start,
         (L_site_dark_from_r1_start).2,
         R_site_activated_from_r0_start,
         R_site_activated_from_r1_start,
         density_L1_diagonal_distinguishes_sectors⟩

#print axioms full_compound_outputs_differ
#print axioms full_compound_from_M0_norm_one
#print axioms full_compound_from_M1_norm_one
#print axioms L_site_activated_from_r0_start
#print axioms L_site_dark_from_r1_start
#print axioms L_site_discriminates_relational_sectors
#print axioms R_site_activated_from_r0_start
#print axioms R_site_activated_from_r1_start
#print axioms R_site_universal_accessibility
#print axioms r1_start_confined_to_r0_sector
#print axioms r0_start_confined_to_r1_sector
#print axioms three_body_participation_from_r0_start
#print axioms two_body_only_from_r1_start
#print axioms full_compound_from_M0_not_any_basis
#print axioms full_compound_from_M1_not_any_basis
#print axioms W_is_involution_on_M0
#print axioms W_is_involution_on_M1
#print axioms density_L1_diagonal_distinguishes_sectors
#print axioms density_L1_zero_from_r1_start
#print axioms state_determines_causal_accessibility

end PhysicalBridges.BCRDB7CausalAccessibility
