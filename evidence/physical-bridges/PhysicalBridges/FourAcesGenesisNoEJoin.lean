import PhysicalBridges.LivingTreeGenerations
import PhysicalBridges.FullPhysicalDomainGuardianAssembly

/-!
# Four Aces and Joker: end-of-modeled-epoch to learned Genesis, with G/no-E gate

Join the existing Living Tree (history-informed candidate Genesis) to the
exact universal original-six physical-domain theorem. This is a test:
the latter is applicable to the learning transition only if its separately
required W coverage and authentic forward reflection hold.

One theorem proves the complete conditional Aces/Joker package at every
finite epoch. The second proves that any learning-driven transition that
deviates from the canonical W next-source cannot satisfy canonical
CompleteWEventCoverage. Do not hide this incompatibility by redefining
genesis or Koru, or by assuming six-X3 in the boundary relation.

"End" means the completed model epoch, not observed thermodynamic heat
death. "No E" excludes the precise source-defined original-six violation
and AbsoluteE; it does not prove physical universe coverage or that every
internal harm is impossible.

No original Koru or X3 definitions are changed.
-/

namespace PhysicalBridges.FourAcesGenesisNoEJoin

open PhysicalBridges.LivingTreeGenerations
open PhysicalBridges.KoruJokerUniverseTrialFeedback
open PhysicalBridges.KoruObjectiveWholeU
open PhysicalBridges.FullPhysicalDomainGuardianAssembly
open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.EverestActualWEventJoin
open PhysicalBridges.OriginalKeystonePositiveWholeTest
open PhysicalBridges.TotalEOriginalX3Bridge

variable {T H E P : Type}

abbrev Tree (T H E : Type) := LivingTree T H E

/-- One entire completed modeled epoch is followed by the next
learned Tree; it is not a cosmological heat-death observation. -/
def learnedBoundary
    (J : JokerExperiment T FiniteObjectiveU H)
    (s t : Tree T H E) : Prop :=
  t = cultivate J s

/-- The positive branch: Hearts (ancestry and continued epochs),
Diamonds (the exact source-Koru), Clubs (all six original X3),
Spades (forward succession), and the Joker (history revises next U).
The no-original-six-violation conclusion is for the supplied domain.
The physical W coverage and authentic reflection are explicit premises. -/
theorem four_aces_joker_genesis_protected_if_physically_reflected
    (J : JokerExperiment T FiniteObjectiveU H)
    (seed : Tree T H E)
    (modeledStep : Tree T H E → Tree T H E → Prop)
    (carrier : P → Index)
    (r : ParticularRelations (Tree T H E) P)
    (owed : P → Prop)
    (hCoverage : CompleteWEventCoverage
      (learnedBoundary J) modeledStep
      (fun s => s.whole) (fun s => s.epoch) positiveWholeU)
    (hReflection : ForwardRealEventReflection
      modeledStep (fun s : Tree T H E => s.epoch)
      positiveWholeU sixDiagonalRoles carrier r owed) :
    ∀ n : Nat,
      let s := grow J seed n
      (cultivate J s).epoch = s.epoch + 1 ∧
      (cultivate J s).ancestors.length = s.ancestors.length + 1 ∧
      (cultivate J s).whole =
        objectiveStep
          (J.enact (J.revise s.theory (J.completedHistory s.whole))) ∧
      (∀ p, owed p →
        OriginalX3 r.continues r.authorized r.free
          r.restrained r.maximal r.provenanced s (cultivate J s) p) ∧
      (¬ ActualX3Violation
        (fun e : Tree T H E × Tree T H E =>
          learnedBoundary J e.1 e.2)
        (fun (_ : Tree T H E × Tree T H E) p => owed p)
        (fun (e : Tree T H E × Tree T H E) p =>
          OriginalX3 r.continues r.authorized r.free
            r.restrained r.maximal r.provenanced e.1 e.2 p)
        (s, cultivate J s)) ∧
      (¬ AbsoluteE
        (fun e : Tree T H E × Tree T H E =>
          learnedBoundary J e.1 e.2)
        (s, cultivate J s)) := by
  intro n
  let s := grow J seed n
  have hStep : learnedBoundary J s (cultivate J s) := rfl
  have hAces :=
    every_physical_event_has_complete_koru_full_six_G_and_no_absolute_E
      (learnedBoundary J) modeledStep
      (fun x : Tree T H E => x.whole)
      (fun x : Tree T H E => x.epoch)
      carrier r owed hCoverage hReflection s (cultivate J s) hStep
  have hGood := hAces.2.2.1
  have hNoAbsolute := hAces.2.2.2
  have hNoViolation :
      ¬ ActualX3Violation
        (fun e : Tree T H E × Tree T H E =>
          learnedBoundary J e.1 e.2)
        (fun (_ : Tree T H E × Tree T H E) p => owed p)
        (fun (e : Tree T H E × Tree T H E) p =>
          OriginalX3 r.continues r.authorized r.free
            r.restrained r.maximal r.provenanced e.1 e.2 p)
        (s, cultivate J s) := by
    intro bad
    rcases bad with ⟨hActual, p, hp, hFails⟩
    exact hFails (hGood p hp)
  refine ⟨rfl, rfl, rfl, hGood, hNoViolation, hNoAbsolute⟩

/-- A necessary compatibility gate. A newly learned source that
is NOT the W-successor of the currently enacted source cannot
be covered by the existing positive-W universal theorem. -/
theorem learned_genesis_non_W_change_refutes_canonical_coverage
    (J : JokerExperiment T FiniteObjectiveU H)
    (modeledStep : Tree T H E → Tree T H E → Prop)
    (s : Tree T H E)
    (hChange : (cultivate J s).whole ≠ objectiveStep s.whole) :
    ¬ CompleteWEventCoverage
      (learnedBoundary J) modeledStep
      (fun x => x.whole) (fun x => x.epoch) positiveWholeU := by
  intro hCoverage
  obtain ⟨_, hBefore, hAfter, hNext⟩ :=
    hCoverage s (cultivate J s) rfl
  apply hChange
  calc
    (cultivate J s).whole =
        objectiveAt positiveWholeU (cultivate J s).epoch := hAfter
    _ = objectiveStep (objectiveAt positiveWholeU s.epoch) := by
      rw [hNext]
      rfl
    _ = objectiveStep s.whole := by rw [hBefore]

#print axioms four_aces_joker_genesis_protected_if_physically_reflected
#print axioms learned_genesis_non_W_change_refutes_canonical_coverage

end PhysicalBridges.FourAcesGenesisNoEJoin
