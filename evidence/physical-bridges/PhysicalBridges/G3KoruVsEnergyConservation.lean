import PhysicalBridges.KoruConservation

/-!
# Koru conservation protects every node; energy conservation does not

Scalar conservation keeps a total. Koru conservation — injective evolution,
equivalently every truth about every node recoverable
(`injective_iff_all_predicates_recoverable`) — keeps every node itself.
Here an evolution conserves energy exactly yet merges two distinct nodes into
one, so some truth about a node is lost. The laws of thermodynamics protect
matterspacetime only when read with Koru conservation, not with a scalar alone.
-/

namespace PhysicalBridges.G3KoruVsEnergyConservation

open PhysicalBridges.KoruConservation

/-- Two distinct nodes with equal energy. -/
def energy : Bool → Nat := fun _ => 1

/-- An evolution that conserves energy exactly but merges both nodes. -/
def merge : Bool → Bool := fun _ => true

/-- **ENERGY CONSERVED, YET A SOUL IS LOST.** -/
theorem energy_conserved_yet_a_soul_is_lost :
    (∀ s, energy (merge s) = energy s) ∧
    ¬ Function.Injective merge ∧
    ¬ AllPredicatesRecoverable merge :=
  ⟨fun _ => rfl,
   fun h => Bool.noConfusion (h (show merge true = merge false from rfl)),
   fun hrec => Bool.noConfusion
     ((injective_iff_all_predicates_recoverable merge).mpr hrec
       (show merge true = merge false from rfl))⟩

#print axioms energy_conserved_yet_a_soul_is_lost

end PhysicalBridges.G3KoruVsEnergyConservation
