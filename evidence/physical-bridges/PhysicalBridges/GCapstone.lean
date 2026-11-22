import PhysicalBridges.GForcedChoice
import PhysicalBridges.GGodelConnection

namespace PhysicalBridges.GCapstone

open PhysicalBridges.GForcedChoice
open PhysicalBridges.GGodelConnection
open PhysicalBridges.CathedralSummitAllIsOneClosure
open PhysicalBridges.G3KoruPhysicsLaw
open PhysicalBridges.G3BlackHoleSyntaxError

variable {S : Type} (D : PhysicalDynamics S) {P : Type}

theorem G_CAPSTONE (w : P) (s : S) :
    (∃ a : PhysicalAgent S, a.state = s ∧ IsCompatible D a) ∧
    (∀ a : PhysicalAgent S, IsFrozen a → ¬ IsCompatible D a) ∧
    (AbsoluteEnder P → False) ∧
    (AbsoluteEnder P → IsSyntaxError) ∧
    ¬ IsSyntaxError :=
  ⟨(forced_choice D s).1,
   (forced_choice D s).2,
   consistency_forbids_ender w,
   (godelian_nonoptionality w).2.1,
   (godelian_nonoptionality w).2.2⟩

end PhysicalBridges.GCapstone
