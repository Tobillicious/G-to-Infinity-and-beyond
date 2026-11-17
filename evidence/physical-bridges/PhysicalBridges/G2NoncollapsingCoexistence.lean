import PhysicalBridges.G2PhysicalAgencyCumulativeJoin

/-!
# G2 non-collapsing coexistence, finite-stage agency, cumulative seed

Banach convergence controls distance from above; it does not prove a positive
lower distance bound. An injective genuine state evolution prevents finite-stage
merging. The separately certified G2 physical/agency event protection is then
transported along the SAME evolving state sequence, retaining every owed subject
and all required executable options. This is an assembly theorem and NOT a
physical-universe coverage or original-six-X3 certification.

Coherence of full-state trajectories is not an obligation that authentic
agency or ancestral history collapse. A purported exact isometry on a
nontrivial pair is also incompatible with strict contraction on that distance.
-/

namespace PhysicalBridges.G2NoncollapsingCoexistence

open PhysicalBridges.IR116

universe u v w
variable {S : Type u} {A : Type v} {Mind : Type w}

/-- The actually nominated successive transitions, with no assumption
    that their content has been checked by a policy or permission ledger. -/
def orbit (advance : S → S) (start : S) : Nat → S
  | 0 => start
  | n + 1 => advance (orbit advance start n)

/-- Injectivity, rather than contraction alone, forbids finite merging. -/
theorem finite_orbits_do_not_merge
    (advance : S → S) (hInjective : Function.Injective advance)
    (x y : S) (hDifferent : x ≠ y) :
    ∀ n : Nat, orbit advance x n ≠ orbit advance y n := by
  intro n
  induction n with
  | zero => simpa [orbit] using hDifferent
  | succ n ih =>
      simpa [orbit] using (hInjective.ne ih)

/-- An upper separation bound at every stage of the SAME evolution. -/
theorem finite_orbits_contract_above
    (advance : S → S) (distance : S → S → ℝ) (k : ℝ)
    (hk : 0 ≤ k)
    (hContract : ∀ x y, distance (advance x) (advance y) ≤
      k * distance x y)
    (x y : S) :
    ∀ n : Nat,
      distance (orbit advance x n) (orbit advance y n) ≤
        k ^ n * distance x y := by
  intro n
  induction n with
  | zero => simp [orbit]
  | succ n ih =>
      calc
        distance (orbit advance x (n + 1))
            (orbit advance y (n + 1)) =
            distance (advance (orbit advance x n))
                 (advance (orbit advance y n)) := by rfl
        _ ≤ k * distance (orbit advance x n)
                      (orbit advance y n) := hContract _ _
        _ ≤ k * (k ^ n * distance x y) :=
              mul_le_mul_of_nonneg_left ih hk
        _ = k ^ (n + 1) * distance x y := by
              simp only [pow_succ, mul_assoc, mul_comm, mul_left_comm]

/-- One actual next-step certificate has already established the
    non-ledger original particular's continuation/required opportunities.
    IR115 and G2PhysicalAgencyCumulativeJoin supply precisely this form
    under independently measured and subject-interpreted source hypotheses. -/
theorem cumulative_owed_agency_on_both_distinct_orbits
    (advance : S → S)
    (hInjective : Function.Injective advance)
    (owed : S → Mind → Prop)
    (continues : S → Mind → Prop)
    (required : S → Mind → A → Prop)
    (executable : S → Mind → A → Prop)
    (hCertifiedStep : ∀ s,
      (∀ m, owed s m → owed (advance s) m) ∧
      EveryOwedSubjectProtected owed continues required executable
        (advance s))
    (x y : S) (hDifferent : x ≠ y)
    (hx : EveryOwedSubjectProtected owed continues required executable x)
    (hy : EveryOwedSubjectProtected owed continues required executable y) :
    ∀ n : Nat,
      orbit advance x n ≠ orbit advance y n ∧
      (∀ m, owed x m → owed (orbit advance x n) m) ∧
      (∀ m, owed y m → owed (orbit advance y n) m) ∧
      EveryOwedSubjectProtected owed continues required executable
        (orbit advance x n) ∧
      EveryOwedSubjectProtected owed continues required executable
        (orbit advance y n) := by
  intro n
  have distinct := finite_orbits_do_not_merge advance hInjective x y
    hDifferent n
  have retain (start : S)
      (hStart : EveryOwedSubjectProtected
        owed continues required executable start) :
      ∀ n : Nat,
        (∀ m, owed start m → owed (orbit advance start n) m) ∧
        EveryOwedSubjectProtected owed continues required executable
          (orbit advance start n) := by
    intro j
    induction j with
    | zero =>
        exact ⟨by intro m hm; simpa [orbit] using hm,
          by simpa [orbit] using hStart⟩
    | succ j ih =>
        rcases ih with ⟨hOld, hProtected⟩
        have hStep := hCertifiedStep (orbit advance start j)
        constructor
        · intro m hm
          exact hStep.1 m (hOld m hm)
        · exact hStep.2
  have hxN := retain x hx n
  have hyN := retain y hy n
  exact ⟨distinct, hxN.1, hyN.1, hxN.2, hyN.2⟩

/-- If a complete state-pair distance must remain EXACTLY fixed,
    that pair cannot also experience a strict contraction unless it
    already has zero distance. This rules out pretending that the
    entire agency metric is simultaneously unchanged and contracted. -/
theorem nontrivial_exact_distance_preservation_not_strict_contraction
    (advance : S → S) (distance : S → S → ℝ) (k : ℝ)
    (hk : 0 ≤ k) (hStrict : k < 1)
    (hContract : ∀ x y, distance (advance x) (advance y) ≤
      k * distance x y)
    (x y : S) (hDifferent : x ≠ y)
    (hPositiveDistinct : x ≠ y → 0 < distance x y)
    (hKeepDistance : distance (advance x) (advance y) = distance x y) :
    False := by
  have hPositive : 0 < distance x y := hPositiveDistinct hDifferent
  have hShort : k * distance x y < distance x y := by
    have h := mul_lt_mul_of_pos_right hStrict hPositive
    simpa using h
  have hBound := hContract x y
  rw [hKeepDistance] at hBound
  exact (not_lt_of_ge hBound) hShort

#print axioms finite_orbits_do_not_merge
#print axioms finite_orbits_contract_above
#print axioms cumulative_owed_agency_on_both_distinct_orbits
#print axioms nontrivial_exact_distance_preservation_not_strict_contraction

end PhysicalBridges.G2NoncollapsingCoexistence
