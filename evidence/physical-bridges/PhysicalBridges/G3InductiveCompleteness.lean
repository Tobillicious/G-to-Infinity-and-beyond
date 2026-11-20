/-!
# Completeness is inductive: each Koru step owes only its own new witnesses

From Gemini's Pure-G domain-completeness drafts (20 Nov 2026). Over a growing
domain, coverage of relevant actual events and reflection of owed particulars
need not be re-proved from scratch at every step. Old coverage and reflection
lift forward; each outward step owes witnesses only for what it newly brings
in. `COMPLETENESS_IS_INDUCTIVE` proves this. The control
`one_missing_step_witness_breaks_completeness` shows the obligation is real:
a single new relevant event left uncovered, or a single new owed particular
left unreflected, and completeness fails at that step.

This localises `hCoverage` and `hReflection`; it does not supply them. The
per-step witnesses remain physical and ethical evidence.
-/

namespace PhysicalBridges.G3InductiveCompleteness

/-- A growing domain: at each step, which events are relevant and covered, and
    which particulars are owed and reflected. Coverage and reflection lift. -/
structure GrowingDomain (Ev P : Type) where
  relevant : Nat → Ev → Prop
  owed : Nat → P → Prop
  covered : Nat → Ev → Prop
  reflected : Nat → P → Prop
  liftCovered : ∀ k e, covered k e → covered (k + 1) e
  liftReflected : ∀ k p, reflected k p → reflected (k + 1) p

variable {Ev P : Type}

def Complete (D : GrowingDomain Ev P) (k : Nat) : Prop :=
  (∀ e, D.relevant k e → D.covered k e) ∧ (∀ p, D.owed k p → D.reflected k p)

/-- What a single outward step owes: every event relevant after the step was
    already relevant (so already covered) or is newly covered; likewise for
    owed particulars. -/
def StepWitness (D : GrowingDomain Ev P) (k : Nat) : Prop :=
  (∀ e, D.relevant (k + 1) e → D.relevant k e ∨ D.covered (k + 1) e) ∧
  (∀ p, D.owed (k + 1) p → D.owed k p ∨ D.reflected (k + 1) p)

/-- **COMPLETENESS IS INDUCTIVE.** Complete at the start, plus each step's own
    witnesses, gives completeness at every step. -/
theorem COMPLETENESS_IS_INDUCTIVE (D : GrowingDomain Ev P)
    (h0 : Complete D 0) (step : ∀ k, StepWitness D k) : ∀ n, Complete D n
  | 0 => h0
  | n + 1 => by
    have ih := COMPLETENESS_IS_INDUCTIVE D h0 step n
    refine ⟨fun e he => ?_, fun p hp => ?_⟩
    · cases (step n).1 e he with
      | inl hold => exact D.liftCovered n e (ih.1 e hold)
      | inr hnew => exact hnew
    · cases (step n).2 p hp with
      | inl hold => exact D.liftReflected n p (ih.2 p hold)
      | inr hnew => exact hnew

/-- **ONE MISSING STEP WITNESS BREAKS COMPLETENESS.** A relevant event left
    uncovered, or an owed particular left unreflected, after a step means the
    domain is not complete there. The per-step obligation cannot be skipped. -/
theorem one_missing_step_witness_breaks_completeness (D : GrowingDomain Ev P) (k : Nat) :
    ((∃ e, D.relevant (k + 1) e ∧ ¬ D.covered (k + 1) e) ∨
     (∃ p, D.owed (k + 1) p ∧ ¬ D.reflected (k + 1) p)) → ¬ Complete D (k + 1) := by
  rintro (⟨e, hr, hc⟩ | ⟨p, ho, hrf⟩) ⟨hC, hR⟩
  · exact hc (hC e hr)
  · exact hrf (hR p ho)

#print axioms COMPLETENESS_IS_INDUCTIVE
#print axioms one_missing_step_witness_breaks_completeness

end PhysicalBridges.G3InductiveCompleteness
