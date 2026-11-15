import PhysicalBridges.RouteBOriginalSixFirstViolation

/-!
# Guardian–Creator conditional join: previously banked Genesis + original six

This is an additive composition of existing checked joins, not a new
physical premise, proof of God, evidence of human consent, or a change to
the complete Koru / original-six meaning.

Three independently auditable obligations remain:
1. Actual physics refines the canonical source and is nonterminal.
2. Authentic original-six reflections hold for all owed particulars.
3. Each proposed Genesis boundary has an *actual author* (not merely a
   simulator or a syntactically named creator).

The conclusion carries a real modeled Genesis event, an author witness,
and all six unchanged obligations on that very event, for every owed p.
The creator role is not equated with gravity, omniscience, or the God of
any theological tradition.
-/

namespace PhysicalBridges.GuardianCreatorConditionalJoin

open PhysicalBridges.KoruGenesisPhysicalForcingFiretest
open PhysicalBridges.KoruCyclicGenesisForwardJoin
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.RouteBOriginalSixFirstViolation
open PhysicalBridges.CathedralFullX3Assembly

universe u v
variable {P : Type u} {Author : Type v}

/-- The claimed causal authorship of a realized physical transition.
This is an independent predicate, not a label minted by a program. -/
def PhysicallyAuthors
    (authors : Author → ActualState → ActualState → Prop)
    (a : Author) (s t : ActualState) : Prop := authors a s t

/-- Exactly the original six for every particular owed on this edge. -/
def ProtectsAllOwedAtGenesis
    (owed : ActualState → ActualState → P → Prop)
    (r : ParticularRelations ActualState P)
    (s t : ActualState) : Prop :=
  ∀ p, owed s t p → OriginalSixAt r s t p

/-- Existing forward physical Genesis and the original-six Route-B join,
plus separately witnessed physical authorship, yield a Guardian *creator
role* for each modeled boundary. Authorship is not inferred from motion.
-/
theorem conditional_guardian_creator_at_each_genesis
    (M : Nat) (physical : SourceRelation)
    (owed : ActualState → ActualState → P → Prop)
    (r : ParticularRelations ActualState P)
    (authors : Author → ActualState → ActualState → Prop)
    (hRef : RespectsCanonicalSource M physical)
    (hTotal : NoTerminalPhysicalState M physical)
    (hIdentity : ∀ s t p, combinedStep M s t → owed s t p →
      IdentityAndProvenance r s t p)
    (hAgency : ∀ s t p, combinedStep M s t → owed s t p →
      AgencyAndFreedom r s t p)
    (hSteward : ∀ s t p, combinedStep M s t → owed s t p →
      RestraintAndMaximality r s t p)
    (hAuthor : ∀ e o U,
      physical ((e, M, o), U) ((e + 1, 0, o), objectiveStep U) →
      ∃ a : Author,
        PhysicallyAuthors authors a
          ((e, M, o), U) ((e + 1, 0, o), objectiveStep U)) :
    ∀ e o U, ∃ a : Author,
      physical ((e, M, o), U)
        ((e + 1, 0, o), objectiveStep U) ∧
      PhysicallyAuthors authors a
        ((e, M, o), U) ((e + 1, 0, o), objectiveStep U) ∧
      ProtectsAllOwedAtGenesis owed r
        ((e, M, o), U) ((e + 1, 0, o), objectiveStep U) := by
  obtain ⟨hAllSix, hGenesis⟩ :=
    physical_genesis_plus_three_authentic_reflections_yields_original_six
      M physical owed r hRef hTotal hIdentity hAgency hSteward
  intro e o U
  have hPhysical := hGenesis e o U
  obtain ⟨a, hAuthored⟩ := hAuthor e o U hPhysical
  exact ⟨a, hPhysical, hAuthored,
    (fun p hp => hAllSix _ _ p hPhysical hp)⟩

/-- Counterexample inherited from the physical source firetest:
Genesis cannot follow from mere source preservation and a forward
arrow without an independently justified nontermination law. -/
theorem no_unconditional_genesis_from_source_only :
    ¬ ∃ t : Combined,
      interiorOnlyPhysical 1 ((0, 1, true), ordinaryObjective) t :=
  interior_only_really_stops_at_terminus
    1 0 true ordinaryObjective

#print axioms conditional_guardian_creator_at_each_genesis
#print axioms no_unconditional_genesis_from_source_only

end PhysicalBridges.GuardianCreatorConditionalJoin
