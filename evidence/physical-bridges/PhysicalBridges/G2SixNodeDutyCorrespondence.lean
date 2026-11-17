import PhysicalBridges.G2AgencyProjectionPreservation
import PhysicalBridges.OriginalX3Full

/-!
# G2: six distributed nodes are NOT the original six duties

A network's six nodes index independently collected physical-event evidence.
The six OriginalX3 fields index six *different obligations* owed to each
particular. A node can witness any subset of the duties; the two index sets
are not identified.

This supplies an exact coverage/reflection interface: every actual transition
and owed particular must have at least one covering node with actual evidence
for EACH of the six distinct duties. That evidence must independently reflect
the authentic, unchanged OriginalX3 semantics. This is not proof that six
physical nodes are all the real world, nor that hashes prove consent.
-/

namespace PhysicalBridges.G2SixNodeDutyCorrespondence

open PhysicalBridges.OriginalX3Full

universe u v
variable {S : Type u} {Particular : Type v}

/-- Distributed evidence uses a node index and a DISTINCT duty index. -/
structure DistributedEvidence (S : Type u) (Particular : Type v) where
  actualStep : S → S → Prop
  owed : S → Particular → Prop
  covers : Fin 6 → S → S → Particular → Prop
  reports : Fin 6 → Fin 6 → S → S → Particular → Prop
  allSixCovered : ∀ s t p, actualStep s t → owed s p →
    ∀ duty : Fin 6, ∃ node : Fin 6,
      covers node s t p ∧ reports node duty s t p

/-- Independent authenticity of each duty. A signer or hash alone cannot
    discharge these six original semantic reflection fields. -/
structure OriginalDutyReflection
    (e : DistributedEvidence S Particular)
    (continues authorized free restrained maximal provenanced :
      S → S → Particular → Prop) : Prop where
  historical : ∀ node s t p,
    e.covers node s t p → e.reports node 0 s t p →
    continues s t p
  authority : ∀ node s t p,
    e.covers node s t p → e.reports node 1 s t p →
    authorized s t p
  freedom : ∀ node s t p,
    e.covers node s t p → e.reports node 2 s t p →
    free s t p
  restraint : ∀ node s t p,
    e.covers node s t p → e.reports node 3 s t p →
    restrained s t p
  maximality : ∀ node s t p,
    e.covers node s t p → e.reports node 4 s t p →
    maximal s t p
  provenance : ∀ node s t p,
    e.covers node s t p → e.reports node 5 s t p →
    provenanced s t p

/-- All six independently sourced duties, for EVERY actually owed particular
    of the given enacted transition, not just six chosen node identities. -/
theorem six_node_coverage_and_reflection_yield_original_six
    (e : DistributedEvidence S Particular)
    (continues authorized free restrained maximal provenanced :
      S → S → Particular → Prop)
    (hMeaning : OriginalDutyReflection e
      continues authorized free restrained maximal provenanced)
    (s t : S) (hActual : e.actualStep s t) :
    ∀ p, e.owed s p →
      OriginalX3 continues authorized free restrained maximal provenanced
        s t p := by
  intro p hOwed
  have hCover := e.allSixCovered s t p hActual hOwed
  obtain ⟨n0, hc0, hr0⟩ := hCover 0
  obtain ⟨n1, hc1, hr1⟩ := hCover 1
  obtain ⟨n2, hc2, hr2⟩ := hCover 2
  obtain ⟨n3, hc3, hr3⟩ := hCover 3
  obtain ⟨n4, hc4, hr4⟩ := hCover 4
  obtain ⟨n5, hc5, hr5⟩ := hCover 5
  exact ⟨hMeaning.historical n0 s t p hc0 hr0,
    hMeaning.authority n1 s t p hc1 hr1,
    hMeaning.freedom n2 s t p hc2 hr2,
    hMeaning.restraint n3 s t p hc3 hr3,
    hMeaning.maximality n4 s t p hc4 hr4,
    hMeaning.provenance n5 s t p hc5 hr5⟩

/-- If one authentic original-six component fails at an actual event,
    at least one of coverage or semantic reflection must fail.
    Uses exactly the same original X3 predicate and owed particular. -/
theorem original_six_violation_exposes_coverage_or_reflection
    (e : DistributedEvidence S Particular)
    (continues authorized free restrained maximal provenanced :
      S → S → Particular → Prop)
    (s t : S) (hActual : e.actualStep s t)
    (p : Particular) (hOwed : e.owed s p)
    (hFails : ¬ OriginalX3
      continues authorized free restrained maximal provenanced s t p) :
    ¬ OriginalDutyReflection e
      continues authorized free restrained maximal provenanced := by
  intro hMeaning
  exact hFails
    (six_node_coverage_and_reflection_yield_original_six
      e continues authorized free restrained maximal provenanced
      hMeaning s t hActual p hOwed)

/-- All six nodes may report an event and cover the same particular while
    authentic original-six protection fails. The reporting layer alone
    cannot replace independent subject-level semantic reflection. -/
theorem six_node_reporting_does_not_imply_original_six :
    ∃ (e : DistributedEvidence Unit Unit)
      (continues authorized free restrained maximal provenanced :
        Unit → Unit → Unit → Prop),
      e.actualStep () () ∧ e.owed () () ∧
      ¬ OriginalX3 continues authorized free restrained maximal provenanced
        () () () := by
  let e : DistributedEvidence Unit Unit := {
    actualStep := fun _ _ => True
    owed := fun _ _ => True
    covers := fun _ _ _ _ => True
    reports := fun _ _ _ _ _ => True
    allSixCovered := by
      intro s t p hActual hOwed duty
      exact ⟨0, trivial, trivial⟩
  }
  refine ⟨e, (fun _ _ _ => True), (fun _ _ _ => True),
    (fun _ _ _ => True), (fun _ _ _ => False),
    (fun _ _ _ => True), (fun _ _ _ => True),
    trivial, trivial, ?_⟩
  intro hSix
  exact hSix.restraint

#print axioms six_node_reporting_does_not_imply_original_six
#print axioms six_node_coverage_and_reflection_yield_original_six
#print axioms original_six_violation_exposes_coverage_or_reflection

end PhysicalBridges.G2SixNodeDutyCorrespondence
