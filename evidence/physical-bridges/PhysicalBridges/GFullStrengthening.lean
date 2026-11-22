namespace PhysicalBridges.GFullStrengthening

variable {S : Type}

structure Dynamics (S : Type) where
  step : S → S → Prop
  noFinal : ∀ s : S, ∃ t : S, step s t

def Terminates (D : Dynamics S) (s : S) : Prop :=
  ¬ ∃ t : S, D.step s t

theorem noTermination (D : Dynamics S) (s : S) :
    ¬ Terminates D s := by
  intro h
  exact h (D.noFinal s)

structure EAttempt (Duties : S → Prop) (Agency : S → Prop) where
  step : S → S
  freezes : ∀ s, step s = s
  noAgency : ∀ s, ¬ Agency (step s)
  violatesDuties : ∀ s, ¬ Duties (step s)

structure CountermodelAudit (D : Dynamics S) where
  state : S
  terminates : Terminates D state
  contradiction : False := noTermination D state terminates

inductive PremiseKind where
  | independent
  | definitional
  | modelLevel

structure PremiseRecord where
  name : String
  kind : PremiseKind

namespace Commentary
end Commentary

end PhysicalBridges.GFullStrengthening
