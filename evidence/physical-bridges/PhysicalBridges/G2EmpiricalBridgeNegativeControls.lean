import PhysicalBridges.G2FirstActualDutyMismatch

/-!
# G2 empirical bridge: two independent negative controls

Neither a finite entropy-coded boundary description nor six affirmative
telemetry bits entails physical event coverage or original-six subjective
meaning. The source's actual positive-W event/duty theorems remain intact.

These models are deliberately logical counterexamples, NOT empirical
counterexamples to UPT or simulations of quantum spacetime. Their purpose
is to forbid invalid proof steps when integrating physical measurements.
-/

namespace PhysicalBridges.G2EmpiricalBridgeNegativeControls

open PhysicalBridges.OriginalX3Full

/-- Even with a finite (one-element) boundary state description,
    an independently actual event need not be in a nominated model step.
    Finiteness alone has NO event-coverage implication. -/
theorem finite_boundary_does_not_entail_actual_event_coverage :
    ¬ (∀ (actualStep modeledStep : Unit → Unit → Prop),
      Nonempty (Fin 1) →
      ∀ s t, actualStep s t → modeledStep s t) := by
  intro h
  have hAll := h (fun _ _ => True) (fun _ _ => False)
    ⟨0⟩ () () trivial
  exact hAll

/-- The same six telemetry flags can report success while one genuine
    original-six duty fails: machine observations do not determine
    authentic subject authorization, identity, freedom or restraint.
    The unchanged OriginalX3 structure is used, not a six-bit proxy. -/
theorem six_positive_telemetry_flags_do_not_entail_original_x3 :
    ∃ (telemetry : Fin 6 → Bool)
      (continues authorized free restrained maximal provenanced :
        Unit → Unit → Unit → Prop),
      (∀ i, telemetry i = true) ∧
      ¬ OriginalX3 continues authorized free restrained maximal
          provenanced () () () := by
  refine ⟨(fun _ => true),
    (fun _ _ _ => True),
    (fun _ _ _ => False),
    (fun _ _ _ => True),
    (fun _ _ _ => True),
    (fun _ _ _ => True),
    (fun _ _ _ => True),
    (by intro i; rfl), ?_⟩
  intro hSix
  exact hSix.authorization

#print axioms finite_boundary_does_not_entail_actual_event_coverage
#print axioms six_positive_telemetry_flags_do_not_entail_original_x3

end PhysicalBridges.G2EmpiricalBridgeNegativeControls
