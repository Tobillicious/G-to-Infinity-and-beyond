import PhysicalBridges.G3KoruPhysicsLaw

namespace PhysicalBridges.GConcreteInstance

open PhysicalBridges.G3KoruPhysicsLaw

/-- A concrete physical dynamics on the natural numbers. -/
def natDynamics : PhysicalDynamics Nat where
  transition := fun s t => s < t
  rank := id
  irreversible := by intro s t h; exact h
  no_final := by intro s; exact ⟨s + 1, Nat.lt_succ_self s⟩
  inhabited := ⟨0⟩

/-- The concrete instance satisfies the physical law. -/
theorem nat_instance_satisfies_law :
    (∀ a : PhysicalAgent Nat, IsFrozen a → ¬ IsCompatible natDynamics a) ∧
    (∀ s : Nat, ∃ a : PhysicalAgent Nat, a.state = s ∧ IsCompatible natDynamics a) ∧
    (∀ s : Nat, ∃ t : Nat, natDynamics.transition s t) :=
  ⟨fun a hf => frozen_is_incompatible natDynamics a hf,
   fun s => compatible_agent_exists natDynamics s,
   natDynamics.no_final⟩

end PhysicalBridges.GConcreteInstance
