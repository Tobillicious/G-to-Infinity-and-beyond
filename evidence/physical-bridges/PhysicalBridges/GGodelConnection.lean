import PhysicalBridges.G3ModelSingularityBridge

namespace PhysicalBridges.GGodelConnection

open PhysicalBridges.CathedralSummitAllIsOneClosure
open PhysicalBridges.G3BlackHoleSyntaxError
open PhysicalBridges.G3ModelSingularityBridge

variable {P : Type}

theorem consistency_forbids_ender (w : P) :
    AbsoluteEnder P → False :=
  e_is_not w

theorem ender_is_unprovable_under_consistency (w : P) :
    AbsoluteEnder P → False :=
  e_is_not w

theorem godelian_nonoptionality (w : P) :
    (AbsoluteEnder P → False) ∧
    (AbsoluteEnder P → IsSyntaxError) ∧
    ¬ IsSyntaxError :=
  modeling_entails_error_detection ⟨w⟩

end PhysicalBridges.GGodelConnection
