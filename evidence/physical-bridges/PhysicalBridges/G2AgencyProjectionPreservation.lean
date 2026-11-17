import PhysicalBridges.G2NoncollapsingCoexistence

/-!
# G2: protected agency projection across every enacted finite stage

A full-state injective transition can still merge *agency projections*:
identity of a complete state and identity of a subject are different claims.

This joins the already checked two-orbit cumulative-duty proof to a
commuting subject-transport square. The independent source obligation is
that the physical transition's agency projection equals its independently
verified agency transition, and that this agency transition is injective.
Neither is inferred from contraction, the registry or a permission ledger.

All preservation claims apply to every finite stage of the SAME chosen
evolution. The original six X3 duties and actual-world correspondence
are not silently inferred from this narrower agency/option certificate.
-/

namespace PhysicalBridges.G2AgencyProjectionPreservation

open PhysicalBridges.IR116
open PhysicalBridges.G2NoncollapsingCoexistence

universe u v w z
variable {S : Type u} {Agent : Type v}
variable {Action : Type w} {Mind : Type z}

/-- The independent agency dynamics must commute with the complete-state
    dynamics; full-state injectivity by itself is insufficient. -/
structure AgencyTransport (advance : S → S)
    (agency : S → Agent) where
  nextAgent : Agent → Agent
  nextAgentInjective : Function.Injective nextAgent
  reflectsEnactment : ∀ s, agency (advance s) = nextAgent (agency s)

/-- Along a complete enacted state history, the agency coordinate
    follows exactly the independently specified agency successor. -/
theorem agency_projection_follows_every_stage
    (advance : S → S) (agency : S → Agent)
    (transport : AgencyTransport advance agency)
    (s : S) :
    ∀ n : Nat,
      agency (orbit advance s n) =
        orbit transport.nextAgent (agency s) n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
      calc
        agency (orbit advance s (n + 1)) =
            transport.nextAgent (agency (orbit advance s n)) :=
          transport.reflectsEnactment _
        _ = transport.nextAgent
              (orbit transport.nextAgent (agency s) n) := by rw [ih]
        _ = orbit transport.nextAgent (agency s) (n + 1) := rfl

/-- Different actual agency projections never merge at any finite stage,
    despite potential asymptotic convergence in other coordinates. -/
theorem agency_projections_never_merge
    (advance : S → S) (agency : S → Agent)
    (transport : AgencyTransport advance agency)
    (x y : S) (hDistinctAgency : agency x ≠ agency y) :
    ∀ n : Nat,
      agency (orbit advance x n) ≠
        agency (orbit advance y n) := by
  intro n
  rw [agency_projection_follows_every_stage advance agency transport x n]
  rw [agency_projection_follows_every_stage advance agency transport y n]
  exact finite_orbits_do_not_merge transport.nextAgent
    transport.nextAgentInjective (agency x) (agency y)
    hDistinctAgency n

/-- A single, explicitly certified complete-state evolution now preserves
    both original owed-subject duties and plural agency projections.
    The physical/semantic G2 certificate is not reduced to identity. -/
theorem noncollapsing_owed_agency_on_both_orbits
    (advance : S → S)
    (hInjective : Function.Injective advance)
    (agency : S → Agent)
    (transport : AgencyTransport advance agency)
    (owed : S → Mind → Prop)
    (continues : S → Mind → Prop)
    (required : S → Mind → Action → Prop)
    (executable : S → Mind → Action → Prop)
    (hCertifiedStep : ∀ s,
      (∀ m, owed s m → owed (advance s) m) ∧
      EveryOwedSubjectProtected owed continues required executable
        (advance s))
    (x y : S)
    (hDistinctAgency : agency x ≠ agency y)
    (hx : EveryOwedSubjectProtected owed continues required executable x)
    (hy : EveryOwedSubjectProtected owed continues required executable y) :
    ∀ n : Nat,
      agency (orbit advance x n) ≠ agency (orbit advance y n) ∧
      orbit advance x n ≠ orbit advance y n ∧
      (∀ m, owed x m → owed (orbit advance x n) m) ∧
      (∀ m, owed y m → owed (orbit advance y n) m) ∧
      EveryOwedSubjectProtected owed continues required executable
        (orbit advance x n) ∧
      EveryOwedSubjectProtected owed continues required executable
        (orbit advance y n) := by
  have hDifferent : x ≠ y := by
    intro hxy
    exact hDistinctAgency (congrArg agency hxy)
  intro n
  have hAgency := agency_projections_never_merge
    advance agency transport x y hDistinctAgency n
  have hCumulative := cumulative_owed_agency_on_both_distinct_orbits
    advance hInjective owed continues required executable
    hCertifiedStep x y hDifferent hx hy n
  exact ⟨hAgency, hCumulative⟩

/-- A full-state bijection can erase the difference in one chosen
    projection, even though it preserves all complete-state distinctions.
    This rules out incorrectly identifying global injectivity with
    faithful subject-level transport. -/
theorem full_state_injective_does_not_force_agency_nonmerging :
    ∃ (next : Bool × Bool → Bool × Bool)
      (agency : Bool × Bool → Bool)
      (x y : Bool × Bool),
        Function.Injective next ∧
        agency x ≠ agency y ∧
        agency (next x) = agency (next y) := by
  refine ⟨(fun p => (p.2, p.1)), Prod.fst,
    (true, false), (false, false), ?_, ?_, ?_⟩
  · intro p q h
    cases p with
    | mk a b =>
      cases q with
      | mk c d =>
        cases h
        rfl
  · decide
  · decide

#print axioms agency_projection_follows_every_stage
#print axioms agency_projections_never_merge
#print axioms noncollapsing_owed_agency_on_both_orbits
#print axioms full_state_injective_does_not_force_agency_nonmerging

end PhysicalBridges.G2AgencyProjectionPreservation
