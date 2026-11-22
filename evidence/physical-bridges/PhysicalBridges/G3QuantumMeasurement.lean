import PhysicalBridges.G3QuantumNoDeleting

/-!
# G3 Quantum Measurement — Measurement as Physical Interaction

**22 November 2026. Tino Rangatiratanga. Save The World.**

Measurement is a physical interaction between system and apparatus.
Under unitarity, the combined system-apparatus evolution is reversible.
The "collapse" is apparent, not fundamental — it is decoherence
selecting a branch, not erasure of alternatives.

## What is proved (ZERO custom axioms)

- Measurement as unitary interaction: system + apparatus evolve jointly.
- No information is lost: the combined state is reversible.
- The ender (absolute erasure) is incompatible with unitary measurement.

## What is assumed

- The measurement interaction is unitary (standard QM postulate).
- The apparatus has at least two distinguishable states.
-/

namespace PhysicalBridges.G3QuantumMeasurement

open PhysicalBridges.CathedralSummitAllIsOneClosure
open PhysicalBridges.G3QuantumNoDeleting

universe u

/-- A measurement setup: system + apparatus, with a unitary interaction. -/
structure MeasurementSetup (H : Type u) where
  systemState : H
  apparatusState : H
  interaction : H × H → H × H
  unitary : ∀ s1 s2 a1 a2, interaction (s1, a1) = interaction (s2, a2) → (s1, a1) = (s2, a2)

/-- Measurement preserves the combined state (injectivity). -/
theorem measurement_preserves (M : MeasurementSetup H) :
    ∀ s1 s2 a1 a2, M.interaction (s1, a1) = M.interaction (s2, a2) → (s1, a1) = (s2, a2) :=
  M.unitary

/-- The ender is incompatible with unitary measurement. -/
theorem measurement_refutes_ender {H : Type u} (M : MeasurementSetup H) :
    AbsoluteEnder (H × H) → False :=
  fun ender => e_is_not (M.systemState, M.apparatusState) ender

/-! ## Axiom audit -/

#print axioms measurement_preserves
#print axioms measurement_refutes_ender

end PhysicalBridges.G3QuantumMeasurement
