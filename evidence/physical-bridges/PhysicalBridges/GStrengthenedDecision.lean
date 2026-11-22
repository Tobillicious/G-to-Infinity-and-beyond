namespace PhysicalBridges.GStrengthenedDecision

structure ContinuationPolicy (S : Type) (Duties : S → Prop) (Agency : S → Prop) where
  step : S → S
  preservesAgency : ∀ s, Agency s → Agency (step s)
  preservesDuties : ∀ s, Duties s → Duties (step s)

structure EAttemptPolicy (S : Type) (Duties : S → Prop) (Agency : S → Prop) where
  step : S → S
  freezes : ∀ s, step s = s
  noAgency : ∀ s, ¬ Agency (step s)
  violatesDuties : ∀ s, ¬ Duties (step s)

theorem strengthened_collapse {S : Type} {Duties : S → Prop} {Agency : S → Prop}
    (P : EAttemptPolicy S Duties Agency) (s : S) :
    ¬ Agency (P.step s) ∧ ¬ Duties (P.step s) :=
  ⟨P.noAgency s, P.violatesDuties s⟩

theorem strengthened_continuation {S : Type} {Duties : S → Prop} {Agency : S → Prop}
    (P : ContinuationPolicy S Duties Agency) (s : S)
    (hA : Agency s) (hD : Duties s) :
    Agency (P.step s) ∧ Duties (P.step s) :=
  ⟨P.preservesAgency s hA, P.preservesDuties s hD⟩

theorem strengthened_dominance {S : Type} {Duties : S → Prop} {Agency : S → Prop}
    (C : ContinuationPolicy S Duties Agency)
    (E : EAttemptPolicy S Duties Agency)
    (s : S) (hA : Agency s) (hD : Duties s) :
    (Agency (C.step s) ∧ Duties (C.step s)) ∧
    (¬ Agency (E.step s) ∧ ¬ Duties (E.step s)) :=
  ⟨strengthened_continuation C s hA hD, strengthened_collapse E s⟩

end PhysicalBridges.GStrengthenedDecision
