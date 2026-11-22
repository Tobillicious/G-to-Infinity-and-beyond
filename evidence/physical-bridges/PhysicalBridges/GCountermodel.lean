namespace PhysicalBridges.GCountermodel

structure RelaxedDynamics (S : Type) where
  transition : S → S → Prop
  allowsSelfLoop : ∃ s, transition s s

def RelaxedCompatible {S : Type} (D : RelaxedDynamics S) (s : S) : Prop :=
  D.transition s s

theorem frozen_compatible_in_countermodel :
    ∃ (D : RelaxedDynamics Nat) (s : Nat),
      D.transition s s := by
  exact ⟨{ transition := fun _ _ => True, allowsSelfLoop := ⟨0, trivial⟩ }, 0, trivial⟩

end PhysicalBridges.GCountermodel
