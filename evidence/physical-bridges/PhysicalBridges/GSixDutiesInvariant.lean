import PhysicalBridges.G3KoruPhysicsLaw
namespace PhysicalBridges.GSixDutiesInvariant

open PhysicalBridges.G3KoruPhysicsLaw

variable {S : Type} (D : PhysicalDynamics S)
variable (d1 d2 d3 d4 d5 d6 : S → Prop)

def AllSix (s : S) : Prop :=
  d1 s ∧ d2 s ∧ d3 s ∧ d4 s ∧ d5 s ∧ d6 s

theorem six_duties_preserved (h : IsConservedInvariant D (AllSix d1 d2 d3 d4 d5 d6)) (s t : S)
    (ht : D.transition s t) (hs : AllSix d1 d2 d3 d4 d5 d6 s) : AllSix d1 d2 d3 d4 d5 d6 t :=
  h s t ht hs

theorem frozen_not_a_legal_transition (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ IsCompatible D a :=
  frozen_is_incompatible D a hf

/-- A frozen action is not a legal transition, so it cannot be a step
    in the dynamics. Conserved duties are preserved only along legal
    transitions; therefore an E-attempt (frozen action) is not a
    dynamics-compatible way to preserve them. -/
theorem e_attempt_not_dynamics_compatible (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ IsCompatible D a :=
  frozen_is_incompatible D a hf

end PhysicalBridges.GSixDutiesInvariant
