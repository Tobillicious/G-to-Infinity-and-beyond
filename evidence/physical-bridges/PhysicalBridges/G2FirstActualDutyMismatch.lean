import PhysicalBridges.PhysicalSemanticLastMileGates
import PhysicalBridges.G2SixNodeDutyCorrespondence

/-!
# First-event audit: locate the exact original-six subject mismatch

Reuses existing positive objective-W source and exact six-tag one-web
representation. It does not define real events as safe, infer existence
of an event, or manufacture actual semantic truth.

New testable output: given an independently real event, complete coverage,
an independently owed particular and a genuine missing original-X3 duty,
produce one SPECIFIC missing original duty tag, with its W-source link
positive at the actual observed stage while its authentic subject link
is false on the very same actual event.

The absence of such a witnessed mismatch is a separate semantic
verification target; it cannot be inferred from cryptographic signatures,
the source operator itself or six G-Mesh device reports.
-/

namespace PhysicalBridges.G2FirstActualDutyMismatch

open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.KoruWholeUSixDutyWebJoin
open PhysicalBridges.KoruSixOriginalRelationsOneWeb
open PhysicalBridges.OriginalKeystoneForwardSemanticReflection
open PhysicalBridges.OriginalKeystonePositiveWholeTest
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.EverestActualWEventJoin

/-- Under independently complete real-to-W event coverage, a failure of
    any original-six semantic duty produces a specific source-positive,
    subject-negative tag at the SAME physical event/particular. -/
theorem actual_violation_with_coverage_exposes_specific_tag
    {S P : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU)
    (stage : S → Nat)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop)
    (hCoverage : CompleteWEventCoverage physicalStep modeledStep
      source stage positiveWholeU)
    (s t : S) (hPhysical : physicalStep s t)
    (p : P) (hOwed : owed p)
    (hViolation : ¬ OriginalX3 r.continues r.authorized r.free
      r.restrained r.maximal r.provenanced s t p) :
    modeledStep s t ∧
    ∃ tag : DutyTag,
      wholeSourceDutyAt positiveWholeU sixDiagonalRoles
        (stage s) (carrier p) tag ∧
      ¬ (oneWeb r).link (.event s t p) (.tag tag) := by
  classical
  have hModeled : modeledStep s t := (hCoverage s t hPhysical).1
  have hNotProfile : ¬ completeProfile r s t p := by
    intro hProfile
    exact hViolation ((complete_profile_iff_original_x3 r s t p).mp
      hProfile)
  have hMissing : ∃ tag : DutyTag,
      ¬ (oneWeb r).link (.event s t p) (.tag tag) := by
    exact Classical.not_forall.mp hNotProfile
  obtain ⟨tag, hMissingTag⟩ := hMissing
  have hPositiveSource :
      wholeSourceDutyAt positiveWholeU sixDiagonalRoles
        (stage s) (carrier p) tag :=
    positive_origin_transports_every_six_source_field
      positiveWholeU sixDiagonalRoles carrier owed
      (fun q _ => all_six_source_fields_true_at_origin (carrier q))
      (stage s) p hOwed tag
  exact ⟨hModeled, tag, hPositiveSource, hMissingTag⟩

/-- Exact event-tag mismatch is incompatible with authenticated, correct
    forward reflection. No conditional assumes the full OriginalX3 as a
    disguised sensor result. -/
theorem actual_violation_with_coverage_refutes_forward_reflection_at_tag
    {S P : Type}
    (physicalStep modeledStep : S → S → Prop)
    (source : S → FiniteObjectiveU)
    (stage : S → Nat)
    (carrier : P → Index) (r : ParticularRelations S P)
    (owed : P → Prop)
    (hCoverage : CompleteWEventCoverage physicalStep modeledStep
      source stage positiveWholeU)
    (s t : S) (hPhysical : physicalStep s t)
    (p : P) (hOwed : owed p)
    (hViolation : ¬ OriginalX3 r.continues r.authorized r.free
      r.restrained r.maximal r.provenanced s t p) :
    ¬ ForwardRealEventReflection modeledStep stage positiveWholeU
      sixDiagonalRoles carrier r owed := by
  intro hReflection
  obtain ⟨hModeled, tag, hSource, hBad⟩ :=
    actual_violation_with_coverage_exposes_specific_tag
      physicalStep modeledStep source stage carrier r owed
      hCoverage s t hPhysical p hOwed hViolation
  exact hBad (hReflection s t p tag hModeled hOwed hSource)

#print axioms actual_violation_with_coverage_exposes_specific_tag
#print axioms actual_violation_with_coverage_refutes_forward_reflection_at_tag

end PhysicalBridges.G2FirstActualDutyMismatch
