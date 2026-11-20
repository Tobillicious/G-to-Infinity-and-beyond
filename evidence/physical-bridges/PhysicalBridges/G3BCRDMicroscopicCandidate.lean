import PhysicalBridges.G3QGInterpretationNecessity
import PhysicalBridges.BCRDActualRelationalFrame
import PhysicalBridges.BCRDOperatorSubjectGap

/-!
# A concrete, physically specified BCRD candidate — not a QG completion

The *existing* frozen BCRD W generator is an independently specified
six-position M-sector transition, whose operator source and covariance
were verified in BCRDActualRelationalFrame. We specify exactly ONE
candidate microscopic transition relation:

    t = step s

No ethical predicate, guardian choice, continuation theorem, reflection,
or desired X3 conclusion is part of that definition.

Consequences DERIVED from that generator, not separately postulated:
* every modeled source configuration has a unique next configuration;
* the generator is reversible on that domain;
* the independently computed same-value relation is covariant;
* the generated relation is NONEMPTY and nontrivial.

We then give the crucial independent semantic stress test: the same
physical transition admits two separate interpretations of the original
six, one granting authorization and the other denying it. Thus even
the concrete source law plus totality and relational covariance does
NOT establish authentic original-six protection for arbitrary subject
meanings. Any proposed one-law QG must independently fix its physical-
to-subject correspondence, not declare it by naming its source edges.

SCOPE: only the frozen BCRD M-sector permutation, not the full complex
M3d dynamics or measured gravity; neither a physical-world QG theorem
nor an actual-world statement about authentic subjects.
-/

namespace PhysicalBridges.G3BCRDMicroscopicCandidate

open PhysicalBridges.BCRDActualRelationalFrame
open PhysicalBridges.FrozenBCRDEvents
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full

/-- A microscopic candidate law fixed by the old BCRD frozen generator,
and entirely independent of any original-X3 or Guardian predicate. -/
def WSourcePhysicalLaw (s t : SourceState) : Prop :=
  t = step s

/-- The proposed physical law matches the independently defined source
ActualStep for the M-sector operator; it is not a replacement event. -/
theorem W_law_is_exact_frozen_BCRD_event
    (s t : SourceState) :
    WSourcePhysicalLaw s t ↔
      ActualStep s .mSectorSwap t := Iff.rfl

/-- From the actual source generator, every model state has a successor.
This is NOT a theorem about the complete physical cosmos. -/
theorem W_law_has_successor_at_every_source_state :
    ∀ s : SourceState, ∃ t, WSourcePhysicalLaw s t := by
  intro s
  exact ⟨step s, rfl⟩

/-- The microscopic law has a unique result for each input:
the BCRD source generator fixes it without a safety selector. -/
theorem W_law_determines_unique_successor
    (s t u : SourceState)
    (ht : WSourcePhysicalLaw s t)
    (hu : WSourcePhysicalLaw s u) : t = u :=
  ht.trans hu.symm

/-- The original physical transport is an involution, hence this
specific six-slot model is reversible on its complete modeled state
domain. This is not a general theorem of irreversible thermodynamics. -/
theorem W_generator_is_reversible (s : SourceState) :
    step (step s) = s := by
  funext i
  change s (Transport (Transport i)) = s i
  rw [transport_involutive]

/-- Reversibility is proven for actual source steps, not demanded by
the definition of the generic physical relation. -/
theorem physical_successor_returns_under_second_W
    (s t : SourceState) (h : WSourcePhysicalLaw s t) :
    WSourcePhysicalLaw t s := by
  subst t
  exact W_generator_is_reversible s

/-- All intrinsic SAME-VALUE relations, including their falsity,
are transported by this physically specified W step.
No authorization claim appears in the covariance theorem. -/
theorem W_law_carries_independently_read_relations
    (s t : SourceState) (h : WSourcePhysicalLaw s t) :
    ∀ x y : Index,
      RelationBefore s x y ↔
      RelationAfter t (Transport x) (Transport y) := by
  exact relational_covariance s t .mSectorSwap h

/-- The model actually includes a nontrivial physical transition;
the universal statements above do not hold merely because the event
relation was empty. -/
theorem W_law_enacts_a_nonidentity_step :
    ∃ s t : SourceState, WSourcePhysicalLaw s t ∧ s ≠ t := by
  let s : SourceState := fun i => if i = (2 : Index) then 1 else 0
  refine ⟨s, step s, rfl, ?_⟩
  intro heq
  have hAt := congrFun heq (2 : Index)
  have hMove : Transport (2 : Index) = 3 := transport_tracks_operator.1
  have hVal : (1 : Int) = 0 := by
    simpa [s, step, hMove] using hAt
  have hNo : (1 : Int) ≠ 0 := by decide
  exact hNo hVal

/-- A possible interpretation of the original subject semantics:
all six are always true. This is an interpretation, not observational
evidence of real authentic duties. -/
def positiveSubjectReading : ParticularRelations SourceState Unit where
  continues := fun _ _ _ => True
  authorized := fun _ _ _ => True
  free := fun _ _ _ => True
  restrained := fun _ _ _ => True
  maximal := fun _ _ _ => True
  provenanced := fun _ _ _ => True

/-- Same microscopic BCRD physics, but independently assigned
authorization is false. The other five fields are unchanged. -/
def absentAuthorizationReading : ParticularRelations SourceState Unit where
  continues := fun _ _ _ => True
  authorized := fun _ _ _ => False
  free := fun _ _ _ => True
  restrained := fun _ _ _ => True
  maximal := fun _ _ _ => True
  provenanced := fun _ _ _ => True

/-- The positive interpretation validates the exact original six
for every event in the same W-generated physical law. -/
theorem positive_reading_meets_six_on_every_W_event :
    ∀ s t, WSourcePhysicalLaw s t →
      OriginalX3 positiveSubjectReading.continues
        positiveSubjectReading.authorized positiveSubjectReading.free
        positiveSubjectReading.restrained positiveSubjectReading.maximal
        positiveSubjectReading.provenanced s t () := by
  intro s t _
  exact ⟨trivial, trivial, trivial, trivial, trivial, trivial⟩

/-- But independently interpreted authorization can fail on
a definitely existing W event. Physical source totality and exact
relational covariance alone have not resolved its meaning. -/
theorem same_W_law_can_fail_authentic_authorization :
    ¬ (∀ s t, WSourcePhysicalLaw s t →
      OriginalX3 absentAuthorizationReading.continues
        absentAuthorizationReading.authorized
        absentAuthorizationReading.free
        absentAuthorizationReading.restrained
        absentAuthorizationReading.maximal
        absentAuthorizationReading.provenanced s t ()) := by
  intro h
  let s : SourceState := fun _ => 0
  have hSix := h s (step s) rfl
  exact hSix.authorization

/-- Concrete SOURCE LAW no-go: an arbitrary set of subject relations
is not constrained by the actual frozen W generator equation. If a
proposed QG law says only that this generator is the actual transition,
it cannot infer the full six for arbitrary independently interpreted
subjects. This tests a source-only QG candidate, not all conceivable
complete matterspacetime quantum gravity laws. -/
theorem physical_W_law_alone_does_not_fix_all_subject_duties :
    ¬ (∀ r : ParticularRelations SourceState Unit,
      ∀ s t, WSourcePhysicalLaw s t →
        OriginalX3 r.continues r.authorized r.free
          r.restrained r.maximal r.provenanced s t ()) := by
  intro h
  exact same_W_law_can_fail_authentic_authorization
    (h absentAuthorizationReading)

#print axioms W_law_is_exact_frozen_BCRD_event
#print axioms W_law_has_successor_at_every_source_state
#print axioms W_law_determines_unique_successor
#print axioms W_generator_is_reversible
#print axioms physical_successor_returns_under_second_W
#print axioms W_law_carries_independently_read_relations
#print axioms W_law_enacts_a_nonidentity_step
#print axioms positive_reading_meets_six_on_every_W_event
#print axioms same_W_law_can_fail_authentic_authorization
#print axioms physical_W_law_alone_does_not_fix_all_subject_duties

end PhysicalBridges.G3BCRDMicroscopicCandidate
