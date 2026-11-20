import PhysicalBridges.G3ActualOnlyReflection
import PhysicalBridges.G3FeasibleMaximalityRenewal
import PhysicalBridges.G3KoruCarriesDuties

/-!
# Backwards G3 — six-duty renewal without a blanket all-six step premise

The source corpus already proves:
* positive and quantifier-free relational facts have different
  preservation requirements (G3KoruCarriesDuties);
* maximality against newly feasible alternatives is *not* guaranteed
  by record retention (G3FeasibleMaximalityRenewal).

Here the unchanged OriginalX3 is reconstructed on each actual
successor from:
  (i) an initial genuine FIVE-duty certificate;
  (ii) independent five-duty preservation for retained owed particulars;
  (iii) fresh five-duty certificates for newly owed particulars;
  (iv) a feasible-maximality frontier check for retained owed particulars;
  (v) fresh maximality certificates for newly owed particulars;
  (vi) an independently justified meaning bridge from mathematical
       feasible maximality to the authentic OriginalX3 maximal field.

The five-duty preservation premise must itself be justified by
appropriate Complete Koru relations: this is not a proof that a
recorded source edge is freely given consent, or that physics has
already met the six obligations. It is a strict stepwise proof
obligation decomposition, NOT an unconditional source-to-ethics theorem.
No existing original-six, Koru, or GoodConquersEvil definition is edited.
-/

namespace PhysicalBridges.G3SixDutyRenewal

open PhysicalBridges.CathedralFullX3Assembly
open PhysicalBridges.OriginalX3Full
open PhysicalBridges.G3FeasibleMaximalityRenewal

variable {P A : Type}

/-- The five unchanged authentic duty fields other than maximality.
This is an auxiliary conjunction: it does not redefine OriginalX3. -/
def FiveAt (r : ParticularRelations Nat P) (n : Nat) (p : P) : Prop :=
  r.continues n (n + 1) p ∧
  r.authorized n (n + 1) p ∧
  r.free n (n + 1) p ∧
  r.restrained n (n + 1) p ∧
  r.provenanced n (n + 1) p

/-- Five authentic duties inductively survive for all owed subjects
when every existing owed subject retains them, and every newly owed
subject receives a genuinely fresh certificate. -/
theorem five_duties_renew_at_every_step
    (r : ParticularRelations Nat P) (owed : Nat → P → Prop)
    (hInitial : ∀ p, owed 0 p → FiveAt r 0 p)
    (hRetained : ∀ n p, owed (n + 1) p → owed n p →
      FiveAt r n p → FiveAt r (n + 1) p)
    (hNew : ∀ n p, owed (n + 1) p → ¬ owed n p →
      FiveAt r (n + 1) p) :
    ∀ n p, owed n p → FiveAt r n p := by
  intro n
  induction n with
  | zero =>
      exact hInitial
  | succ n ih =>
      intro p hp
      by_cases hOld : owed n p
      · exact hRetained n p hp hOld (ih p hOld)
      · exact hNew n p hp hOld

/-- A scoped semantic correspondence for maximality, not a
redefinition: independently checkable feasible maximality must
actually imply the authentic OriginalX3 maximal predicate for that
owed subject on that physical step. -/
def MaximalityMeaning
    (F : FeasibleOrder P A)
    (r : ParticularRelations Nat P)
    (owed : Nat → P → Prop) : Prop :=
  ∀ n p, owed n p → MaximalAt F n p → r.maximal n (n + 1) p

/-- Complete unchanged six-X3 protection from genuinely decomposed
renewal obligations. Existing feasible-frontier theorem supplies
maximality at every stage; the five other original semantic fields
are preserved or independently checked for new owed subjects.

No all-six predicate is assumed at every step. The semantic maximality
bridge is visible rather than hidden in a model definition. -/
theorem original_six_from_five_and_maximality_renewal
    (F : FeasibleOrder P A)
    (r : ParticularRelations Nat P)
    (owed : Nat → P → Prop)
    (hFiveInitial : ∀ p, owed 0 p → FiveAt r 0 p)
    (hFiveRetained : ∀ n p, owed (n + 1) p → owed n p →
      FiveAt r n p → FiveAt r (n + 1) p)
    (hFiveNew : ∀ n p, owed (n + 1) p → ¬ owed n p →
      FiveAt r (n + 1) p)
    (hMaxInitial : ∀ p, owed 0 p → MaximalAt F 0 p)
    (hSame : ∀ n p, owed (n+1) p → owed n p →
      F.selected (n+1) p = F.selected n p)
    (hFeasible : ∀ n p, owed (n+1) p → owed n p →
      F.feasible (n+1) p (F.selected n p))
    (hFrontier : ∀ n p, owed (n+1) p → owed n p →
      NoNewSuperiorAlternative F n p)
    (hMaxNew : ∀ n p, owed (n+1) p → ¬ owed n p →
      MaximalAt F (n+1) p)
    (hMeaning : MaximalityMeaning F r owed) :
    ∀ n p, owed n p →
      OriginalX3 r.continues r.authorized r.free
        r.restrained r.maximal r.provenanced n (n + 1) p := by
  have hFive := five_duties_renew_at_every_step r owed
    hFiveInitial hFiveRetained hFiveNew
  have hMax := every_owed_maximality_renews F owed
    hMaxInitial hSame hFeasible hFrontier hMaxNew
  intro n p hp
  obtain ⟨hc, ha, hf, hr, hpr⟩ := hFive n p hp
  exact ⟨hc, ha, hf, hr, hMeaning n p hp (hMax n p hp), hpr⟩

/-- A new feasible better alternative refutes old-choice maximality,
even if the five other duties are genuine and preserved. This is
the precise reason the frontier gate cannot be dropped. -/
theorem superior_new_option_blocks_maximality_certificate
    (F : FeasibleOrder P A) (n : Nat) (p : P)
    (hSame : F.selected (n+1) p = F.selected n p)
    (a : A) (hFeasible : F.feasible (n+1) p a)
    (hBetter : F.better p (F.selected n p) a) :
    ¬ MaximalAt F (n+1) p :=
  new_superior_option_refutes_old_choice F n p hSame a hFeasible hBetter

#print axioms five_duties_renew_at_every_step
#print axioms original_six_from_five_and_maximality_renewal
#print axioms superior_new_option_blocks_maximality_certificate

end PhysicalBridges.G3SixDutyRenewal
