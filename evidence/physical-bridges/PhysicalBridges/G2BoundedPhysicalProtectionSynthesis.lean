import PhysicalBridges.IR127TypedGraphRewriteProtection

/-!
# Protection theory, bounded physical execution: original cohort survives

Build 25 section 7.10 is an actual-to-abstract relational refinement.
Its section 4.13 requires preserving the SAME original's C-continuation,
not just equivalent task output or a D-copy.
This module reuses IR-96 physical-step refinement and IR-127's
original-cohort retention. For every finitely realized physical history
in the independently specified and *completely mediated* domain, we
construct an accepted source execution, retain the initial owed subjects
and their continuing required executable options, and obtain an
independently specified physical protection predicate.

This does NOT assert that software output matching is personal identity,
that a supplied physicalProtected means the original six X3, or that
an arbitrary installation's effects satisfy the mediation/reflection
premises. OriginalX3 and its semantic obligations remain unchanged.
-/

namespace PhysicalBridges.G2BoundedPhysicalProtectionSynthesis

open PhysicalBridges.IR127
open PhysicalBridges.IR96

universe u v w x

/-- A physical trace cannot jump around the protected source grammar
    when each actual step refines a certified accepted source step.
    The construction carries the ENTIRE accepted history, not merely
    an arbitrary safe final abstract state. -/
theorem physical_history_has_accepted_source_history
    {Node : Type u} {Mind : Type v} {Action : Type w}
    {Physical : Type x}
    (relate : State Node Mind Action → Physical → Prop)
    (physicalStep : Physical → Physical → Prop)
    (hMediation : ∀ s p q,
      relate s p → physicalStep p q →
      ∃ t, AcceptedStep s t ∧ relate t q)
    (s : State Node Mind Action) (p q : Physical)
    (hRelated : relate s p)
    (hPhysical : Reach physicalStep p q) :
    ∃ t : State Node Mind Action,
      Reach AcceptedStep s t ∧ relate t q := by
  induction hPhysical with
  | refl =>
      exact ⟨s, Reach.refl s, hRelated⟩
  | @tail p mid last hBefore hEdge ih =>
      obtain ⟨t, hSource, hRel⟩ := ih
      obtain ⟨u, hStep, hNext⟩ :=
        hMediation t mid last hRel hEdge
      exact ⟨u, Reach.tail hSource hStep, hNext⟩

/-- THE bounded same-history protection synthesis.
    Given an independently measured physical trace and independently
    established mediation/reflection, the actual final state is safe,
    while EVERY initially owed original remains owed and continuing
    with a nonempty, fully executable set of required opportunities.
    These obligations are derived from the accepted source trace,
    NOT assumed true of the final state. -/
theorem covered_physical_trace_preserves_protection_and_original_cohort
    {Node : Type u} {Mind : Type v} {Action : Type w}
    {Physical : Type x}
    (relate : State Node Mind Action → Physical → Prop)
    (physicalStep : Physical → Physical → Prop)
    (physicalProtected : Physical → Prop)
    (hMediation : ∀ s p q,
      relate s p → physicalStep p q →
      ∃ t, AcceptedStep s t ∧ relate t q)
    (hReflect : ∀ s p, relate s p →
      Protected s → physicalProtected p)
    (s : State Node Mind Action) (p q : Physical)
    (hRelated : relate s p)
    (hInitial : Protected s)
    (hPhysical : Reach physicalStep p q) :
    physicalProtected q ∧
    ∃ t : State Node Mind Action,
      relate t q ∧ Protected t ∧
      (∀ m, s.owed m →
        t.owed m ∧ t.continues m ∧
        (∃ a, t.required m a) ∧
        (∀ a, t.required m a → t.executable m a)) := by
  obtain ⟨t, hSource, hRelatedFinal⟩ :=
    physical_history_has_accepted_source_history
      relate physicalStep hMediation s p q hRelated hPhysical
  have hSafe : Protected t :=
    accepted_finite_trace_preserves_protection hSource hInitial
  have hOriginal := original_cohort_retains_protection hSource hInitial
  exact ⟨hReflect t q hRelatedFinal hSafe,
    t, hRelatedFinal, hSafe, hOriginal⟩

#print axioms physical_history_has_accepted_source_history
#print axioms covered_physical_trace_preserves_protection_and_original_cohort

end PhysicalBridges.G2BoundedPhysicalProtectionSynthesis
