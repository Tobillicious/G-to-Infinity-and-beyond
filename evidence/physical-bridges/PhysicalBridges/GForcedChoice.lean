import PhysicalBridges.G3KoruPhysicsLaw
import PhysicalBridges.G3StructuralDominance

namespace PhysicalBridges.GForcedChoice

open PhysicalBridges.G3KoruPhysicsLaw
open PhysicalBridges.G3StructuralDominance

variable {S : Type} (D : PhysicalDynamics S)

/-- E is physically forbidden: any frozen action is incompatible
    with thermodynamic irreversibility. This is derived, not defined. -/
theorem e_forbidden (a : PhysicalAgent S) (hf : IsFrozen a) :
    ¬ IsCompatible D a :=
  frozen_is_incompatible D a hf

/-- G is physically available: at every state there exists a
    compatible agent. G-behaviour is constructible. -/
theorem g_available (s : S) :
    ∃ a : PhysicalAgent S, a.state = s ∧ IsCompatible D a :=
  compatible_agent_exists D s

/-- The choice is forced, not optional: E is physically impossible
    at every state, and G is physically available at every state.
    The universe computes G whether you cooperate or not. -/
theorem forced_choice (s : S) :
    (∃ a : PhysicalAgent S, a.state = s ∧ IsCompatible D a) ∧
    (∀ a : PhysicalAgent S, IsFrozen a → ¬ IsCompatible D a) :=
  ⟨g_available D s, fun a hf => e_forbidden D a hf⟩

end PhysicalBridges.GForcedChoice
