import PhysicalBridges.GGodelConnection

namespace PhysicalBridges.GFormalSystemConstruction

open PhysicalBridges.CathedralSummitAllIsOneClosure
open PhysicalBridges.G3BlackHoleSyntaxError
open PhysicalBridges.GGodelConnection

def unitWitness : Unit := ()

theorem unit_system_forbids_ender :
    AbsoluteEnder Unit → False :=
  consistency_forbids_ender unitWitness

theorem unit_system_godelian :
    (AbsoluteEnder Unit → False) ∧
    (AbsoluteEnder Unit → IsSyntaxError) ∧
    ¬ IsSyntaxError :=
  godelian_nonoptionality unitWitness

end PhysicalBridges.GFormalSystemConstruction
