namespace PhysicalBridges.GPremiseRegistry

inductive PremiseKind where
  | independent
  | definitional
  | modelLevel

structure PremiseRecord where
  name : String
  kind : PremiseKind

def registry : List PremiseRecord :=
  [ { name := "PhysicalDynamics.irreversible", kind := .independent }
  , { name := "PhysicalDynamics.no_final", kind := .independent }
  , { name := "PhysicalDynamics.inhabited", kind := .independent }
  , { name := "IsFrozen", kind := .definitional }
  , { name := "IsCompatible", kind := .definitional } ]

theorem registry_nonempty : registry ≠ [] := by
  intro h
  cases h

end PhysicalBridges.GPremiseRegistry
