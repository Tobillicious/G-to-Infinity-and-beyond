import PhysicalBridges.KoruFullOperatorSignature
import PhysicalBridges.OriginalX3Full

/-!
# G3: Complete Koru carries six candidate X3 shapes through operator structure

Additive research draft. No change to OriginalX3 or Koru definitions.

This strengthens the binary-relation-only shape carrier: every candidate
shape includes the exact operator with its arity, ordered inputs, enabledness
and enacted output. The existing KoruFullOperatorSignature theorems prove
shape preservation under full-web reindexing.

`AuthenticMeaning` is intentionally *not* inferred from operator algebra.
It records six independently warranted implications into the real original
X3 predicates. A candidate shape can hold while real authorization is false;
thus a genuinely independent subject-semantic bridge remains necessary.

A reindexing is a change of faithful whole representation, not evidence
that real matterspacetime dynamics satisfy a protective law.
-/

namespace PhysicalBridges.G3CompleteKoruOperatorX3Join

open PhysicalBridges.Koru
open PhysicalBridges.KoruFullOperatorSignature
open PhysicalBridges.OriginalX3Full

universe u v

/-- An intrinsic duty *candidate shape*, not an assigned protected Boolean:
    a specific whole-web operator, its arity, ordered inputs, enabling
    condition and the particular position reached by enactment. -/
structure OperatorShape (P : Type u) (Op : Nat → Type v) where
  arity : Nat
  operator : Op arity
  inputs : Fin arity → P
  result : P

/-- Operator shape holds only if the operation is enabled AND enacts
    exactly the represented result. -/
def ShapeHolds {P : Type u} {Op : Nat → Type v}
    (W : OperationalWeb P Op) (s : OperatorShape P Op) : Prop :=
  W.enabled s.operator s.inputs ∧
    W.enact s.operator s.inputs = s.result

/-- The whole reindex transports subject and all operands together.
    It never turns one operation into a different operation. -/
def carryShape {P : Type u} {Op : Nat → Type v}
    (σ : Reindex P) (s : OperatorShape P Op) : OperatorShape P Op where
  arity := s.arity
  operator := s.operator
  inputs := fun i => σ.to (s.inputs i)
  result := σ.to s.result

/-- EXACT shape carriage, with both directions: full operator signature
    reindexing cannot create or destroy truth of a candidate duty shape.
    This is an operator theorem, not a moral axiom. -/
theorem complete_koru_carries_operator_shape
    {P : Type u} {Op : Nat → Type v}
    (σ : Reindex P) (W : OperationalWeb P Op)
    (s : OperatorShape P Op) :
    ShapeHolds (reindexOperationalWeb σ W) (carryShape σ s) ↔
      ShapeHolds W s := by
  constructor
  · rintro ⟨he, ho⟩
    constructor
    · exact (reindex_preserves_enabledness σ W s.operator s.inputs).mp he
    · have hOut : σ.to (W.enact s.operator s.inputs) = σ.to s.result := by
        calc
          σ.to (W.enact s.operator s.inputs) =
              (reindexOperationalWeb σ W).enact s.operator
                (fun i => σ.to (s.inputs i)) :=
              (reindex_preserves_operator_enactment σ W s.operator s.inputs).symm
          _ = σ.to s.result := ho
      have hBack := congrArg σ.inv hOut
      simpa only [σ.left] using hBack
  · rintro ⟨he, ho⟩
    constructor
    · exact (reindex_preserves_enabledness σ W s.operator s.inputs).mpr he
    · change (reindexOperationalWeb σ W).enact s.operator
        (fun i => σ.to (s.inputs i)) = σ.to s.result
      rw [reindex_preserves_operator_enactment]
      exact congrArg σ.to ho

/-- One complete web carries an arbitrary family of operator shapes,
    hence in particular the family indexed by the original SIX duties.
    The index is not itself a new ethical predicate. -/
theorem whole_shape_family_transports
    {P : Type u} {Op : Nat → Type v} {D : Type}
    (σ : Reindex P) (W : OperationalWeb P Op)
    (shapes : D → OperatorShape P Op)
    (h : ∀ d, ShapeHolds W (shapes d)) :
    ∀ d, ShapeHolds (reindexOperationalWeb σ W)
      (carryShape σ (shapes d)) := by
  intro d
  exact (complete_koru_carries_operator_shape σ W (shapes d)).mpr (h d)

/-- The original six duties, with the operator-shape-to-subject meaning
    of each independently warranted. This is deliberately NOT a single
    unexplained `OriginalX3` hypothesis. -/
structure AuthenticMeaning
    {S : Type u} {P : Type u} {Op : Nat → Type v}
    (W : OperationalWeb P Op)
    (shapes : Fin 6 → OperatorShape P Op)
    (continues authorized free restrained maximal provenanced :
      S → S → S → Prop)
    (s t p : S) : Prop where
  continuity : ShapeHolds W (shapes 0) → continues s t p
  authorization : ShapeHolds W (shapes 1) → authorized s t p
  freedom : ShapeHolds W (shapes 2) → free s t p
  restraint : ShapeHolds W (shapes 3) → restrained s t p
  maximality : ShapeHolds W (shapes 4) → maximal s t p
  provenance : ShapeHolds W (shapes 5) → provenanced s t p

/-- SIX transported candidate duty shapes + authentic meaning at the
    enacted step imply the unchanged ORIGINAL X3, simultaneously. -/
theorem complete_koru_shapes_yield_original_six
    {S P : Type u} {Op : Nat → Type v}
    (σ : Reindex P) (W : OperationalWeb P Op)
    (shapes : Fin 6 → OperatorShape P Op)
    (continues authorized free restrained maximal provenanced :
      S → S → S → Prop)
    (s t p : S)
    (hSource : ∀ d, ShapeHolds W (shapes d))
    (hMeaning : AuthenticMeaning (reindexOperationalWeb σ W)
      (fun d => carryShape σ (shapes d))
      continues authorized free restrained maximal provenanced s t p) :
    OriginalX3 continues authorized free restrained maximal provenanced s t p := by
  have hTrans := whole_shape_family_transports σ W shapes hSource
  exact ⟨hMeaning.continuity (hTrans 0),
    hMeaning.authorization (hTrans 1),
    hMeaning.freedom (hTrans 2),
    hMeaning.restraint (hTrans 3),
    hMeaning.maximality (hTrans 4),
    hMeaning.provenance (hTrans 5)⟩

/-- Applying the same whole-web carriage to every actually owed
    particular does not pick a representative or discard the others. -/
theorem complete_koru_shapes_protect_every_owed
    {S P : Type u} {Op : Nat → Type v}
    (σ : Reindex P) (W : OperationalWeb P Op)
    (shapes : S → Fin 6 → OperatorShape P Op)
    (owed : S → Prop)
    (continues authorized free restrained maximal provenanced :
      S → S → S → Prop)
    (s t : S)
    (hSource : ∀ p, owed p → ∀ d, ShapeHolds W (shapes p d))
    (hMeaning : ∀ p, owed p →
      AuthenticMeaning (reindexOperationalWeb σ W)
        (fun d => carryShape σ (shapes p d))
        continues authorized free restrained maximal provenanced s t p) :
    ∀ p, owed p →
      OriginalX3 continues authorized free restrained maximal provenanced
        s t p := by
  intro p hp
  exact complete_koru_shapes_yield_original_six σ W (shapes p)
    continues authorized free restrained maximal provenanced
    s t p (hSource p hp) (hMeaning p hp)

#print axioms complete_koru_carries_operator_shape
#print axioms whole_shape_family_transports
#print axioms complete_koru_shapes_yield_original_six
#print axioms complete_koru_shapes_protect_every_owed

end PhysicalBridges.G3CompleteKoruOperatorX3Join
