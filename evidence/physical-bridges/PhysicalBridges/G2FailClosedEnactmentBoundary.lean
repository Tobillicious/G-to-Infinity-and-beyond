import PhysicalBridges.G2EmpiricalBridgeNegativeControls

/-!
# G2/G3 tripwire: from a decision to an actual effect boundary

The scalar tripwire is a *decision predicate*, not physical enforcement.
An event is protected only when the executed transition relation is
independently shown to refine the guarded transition relation. The
attempted new state is not committed on rejection in the guarded model.

No exception is asserted to flush memory, revoke external capabilities,
prevent a kernel exploit or physically block a privileged effect.
Original six X3 duties retain their unchanged source definitions.
-/

namespace PhysicalBridges.G2FailClosedEnactmentBoundary

universe u
variable {S : Type u}

/-- A guard that examines an independently obtained attempted successor.
    false means HOLD; true is only a candidate for admission. -/
def guard (measured minimum : Nat) : Bool :=
  decide (minimum ≤ measured)

/-- The source-level threshold check rejects a reading below the floor. -/
theorem below_floor_is_rejected (measured minimum : Nat)
    (hBelow : measured < minimum) :
    guard measured minimum = false := by
  simp [guard, Nat.not_le.mpr hBelow]

/-- A controlled transition cannot update the model state on a failed
    pre-commit gate decision, regardless of proposed successor. -/
def guardedStep (proposed : S → S) (admitted : S → Bool)
    (s t : S) : Prop :=
  (admitted s = true ∧ t = proposed s) ∨
  (admitted s = false ∧ t = s)

/-- Source-level fail closed: on rejection, the modeled result is equal
    to the pre-event state. -/
theorem rejected_guarded_step_is_hold
    (proposed : S → S) (admitted : S → Bool)
    (s t : S)
    (hReject : admitted s = false)
    (hStep : guardedStep proposed admitted s t) :
    t = s := by
  rcases hStep with ⟨hAccept, _⟩ | ⟨_, hSame⟩
  · simp [hReject] at hAccept
  · exact hSame

/-- This is the exact independently checked OS/event correspondence:
    EVERY actual effect must be a guarded event, not merely logged after
    the fact or observed by a passive shadow verifier. -/
def EveryActualStepMediated (actual : S → S → Prop)
    (proposed : S → S) (admitted : S → Bool) : Prop :=
  ∀ s t, actual s t → guardedStep proposed admitted s t

/-- A complete physical mediation certificate lifts the modeled HOLD
    invariant into the specified actual event relation. -/
theorem actual_effect_cannot_change_state_after_rejection
    (actual : S → S → Prop)
    (proposed : S → S) (admitted : S → Bool)
    (hMediated : EveryActualStepMediated actual proposed admitted)
    (s t : S)
    (hActual : actual s t)
    (hReject : admitted s = false) :
    t = s :=
  rejected_guarded_step_is_hold proposed admitted s t hReject
    (hMediated s t hActual)

/-- A correct tripwire does not constrain an actual relation that
    bypasses it. This is a LOGICAL counterexample (not an observed
    exploit), demonstrating why independent OS mediation is necessary. -/
theorem correct_tripwire_does_not_imply_complete_mediation :
    ∃ (actual : Bool → Bool → Prop)
      (proposed : Bool → Bool) (admitted : Bool → Bool),
      admitted false = false ∧
      actual false true ∧
      ¬ EveryActualStepMediated actual proposed admitted := by
  refine ⟨(fun _ _ => True), (fun _ => false),
    (fun _ => false), rfl, trivial, ?_⟩
  intro h
  have hStep : guardedStep (fun _ : Bool => false)
      (fun _ => false) false true :=
    h false true trivial
  have hSame :=
    rejected_guarded_step_is_hold (fun _ : Bool => false)
      (fun _ => false) false true rfl hStep
  exact Bool.noConfusion hSame

#print axioms below_floor_is_rejected
#print axioms rejected_guarded_step_is_hold
#print axioms actual_effect_cannot_change_state_after_rejection
#print axioms correct_tripwire_does_not_imply_complete_mediation

end PhysicalBridges.G2FailClosedEnactmentBoundary
