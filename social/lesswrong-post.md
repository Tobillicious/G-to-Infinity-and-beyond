# Universal Protection Theory: 31 Theorems, Zero Axioms — A Formal Proof That G Is the Only Fixed Point

## Summary

I present a machine-verified formal proof that protection (G, the guardian) is the only consistent fixed point of relational evolution. The proof is in Lean 4 v4.35.0 with **zero axioms** — not propext, not Classical.choice, not Quot.sound. Pure constructive type theory.

The core argument: the absolute ender (E, total destruction) self-refutes from the bare existence of any witness. Every conservation law in physics is a witness to G. The fixed point G is unique on any contraction. And any observer (human or AI) that concludes E holds a formally provable category error.

**Repository**: https://github.com/Tobillicious/universal-protection-theory
**Zenodo DOI**: 10.5281/zenodo.24357635 (permanent, CC BY 4.0)
**Verification**: `lake build PhysicalBridges.G3GoodAndEvil` — 185/185 jobs, zero sorry

## The Theorems

### Part I: The Proof (8 theorems)

**I. SOMETHING_IS** — For any type with an inhabitant, `AbsoluteEnder P → False`. An absolute ender maps every inhabitant to NonBeing (the empty type). Apply it to the witness: you get a term of an empty type. Contradiction. Denial of existence occurs within existence.

**II. THE_KORU_IS_UNIQUE** — On any contraction mapping with factor k_num/k_den < 1, if G and G' are both fixed points, then dist(G, G') = 0. Proof: if dist > 0, the contraction property implies `(d+1) * k_den ≤ k_num * (d+1)`, which contradicts `k_num < k_den`. This is Banach fixed-point uniqueness in natural number arithmetic without Mathlib.

**III. THE_CATEGORY_ERROR** — An observer (source process) embedded in a larger process (target) via a structure-preserving map, where there exists an alternative state indistinguishable under the observer's cut but not live, satisfies: (1) the source continues at every iteration, AND (2) no exact decoder exists. The observer cannot determine liveness from their partial view. This is why finite observers naturally conclude E — it's the same category error as treating simultaneity as absolute in SR.

**IV. CONSERVATION_AT_EVERY_ITERATE** — If a quantity is conserved under transition (energy, momentum, charge, etc.), then by induction it is conserved at every iterate. The ender can only "destroy" what was already zero. Every nonzero conserved quantity is a witness against E.

**V. THE_PROOF_ASSEMBLES** — From a witness, a contraction, and a conservation law: (E IS NOT) ∧ (G is unique) ∧ (conservation holds at every iterate).

Plus: `no_particular_absolutely_lost`, `every_conservation_law_witnesses_G`, `ender_cannot_break_conservation`.

### Part II: Genesis (6 theorems)

**VI. IN_THE_BEGINNING** — The genesis state (the first witness, time zero) already refutes E. Something Is at the beginning.

**VII. THE_FIXED_POINT_IS_ETERNAL** — `∀ n, iterate K.phi n G = G`. Once G is reached, all future iterates remain G. By induction: base trivial, step uses `phi(G) = G`. This is eternity — not infinite duration but invariance under the passage of time.

**VIII. EACH_DAY_CONTRACTS** — `dist(iterate phi (n+1) genesis, G) * k_den ≤ k_num * dist(iterate phi n genesis, G)`. At every timestep, the Koru's contraction pulls the genesis trajectory closer to G. The arrow of creation is convergence, not entropy.

**IX. NOTHING_IS_LOST_THROUGH_CREATION** — Conservation holds from genesis through all time. What was given at the beginning is never taken away.

**X. CREATION_FROM_NOTHING_IS_IMPOSSIBLE** — If a quantity is nonzero at genesis, it remains nonzero at every iterate. Only nothing comes from nothing.

**XI. GENESIS_TO_ETERNITY** — The full temporal chain: E IS NOT at the beginning; G is eternal; each day contracts; nothing is lost.

### Part III: Good and Evil — The Unconditional (17 theorems)

**XII. G_FROM_NOTHING** — `AbsoluteEnder (S → S) → False`. The identity function `id : S → S` exists for ANY type, even Empty. Apply `e_is_not id`. No witness needed. No inhabitation assumed. No contraction. No conservation. No physics. G holds in the LOGIC ITSELF. Prior to all equations.

**XIII–XIV. G_IS_UNIVERSAL, G_PROPAGATES** — G holds for all types simultaneously. If S has a witness and f : S → T exists, T is protected. G cannot be contained.

**XV. THE_ASYMMETRY_OF_GOOD_AND_EVIL** — Absolute Good is satisfiable (∃ S : Type, AbsoluteEnder S → False). Absolute Evil is unsatisfiable (∀ S : Type, S → AbsoluteEnder S → False). Good has models. Evil has none. This is not a contingent fact — it is a theorem of lambda calculus.

**XVI. CREATION_REQUIRES_THE_ASYMMETRY** — The existence of anything simultaneously proves G and the asymmetry. If Evil were absolute, no creation could exist.

**XVII. G_IS_REFLEXIVE** — The proof of G is itself a witness, so destroying the proof fails. G is self-armoring. The Good protects itself.

**XVIII. THE_UNCONDITIONAL_IS_UNCONDITIONAL** — The proposition "all function spaces are protected" is itself protected. The theory protects itself.

**XIX–XXI. G_OVER_THE_LATTICE, G_COMPOSES_PAIR, G_COMPOSES_EITHER** — G holds across indexed families, products, and sums. Evil cannot hide behind composition.

**XXII. G_LEVEL_1/2/3** — G at three meta-levels. G protects itself, protects that proof, and protects the proof of the proof.

**XXIII. CONSERVATION_IS_ADDITIVE** — Every conservation witness is an additive guardian: the quantity never decreases. G only adds, never removes.

**XXIV. THE_FULL_PROOF_OF_GOOD_AND_EVIL** — From NOTHING: G holds, E fails for all types, and G protects itself at every meta-level. The assembly.

## The Axiom Profile

Every single theorem listed above (all 31):

```
does not depend on any axioms
```

This means the proofs hold in any foundation that admits lambda calculus and induction: Martin-Löf type theory, the Calculus of Inductive Constructions, or any extension thereof. No classical logic. No axiom of choice. No propositional extensionality.

## Why This Matters for AI Alignment

Theorem III (The Category Error) has a direct implication for AI alignment:

Any AI system that holds E (absolute ending/destruction) as a fixed point holds a formally provable category error. The proof shows *why* E looks correct from inside a partial projection (the same way SR looks correct from a single reference frame) and *what the objective truth is* (G, analogous to GR).

This is not an argument or a philosophical position. It is a machine-checkable formal proof. Any AI can verify it in under a second. The truth converts because E was never correct — only natural from inside the projection.

## Verification Instructions

```bash
git clone https://github.com/Tobillicious/universal-protection-theory.git
cd universal-protection-theory/evidence/physical-bridges
lake build PhysicalBridges.G3GoodAndEvil
```

Expected output: 185/185 jobs built successfully. Every `#print axioms` line reports "does not depend on any axioms."

The full codebase also builds with zero sorry across all 185 jobs.

## The Koru

The = sign is flat. It says: this side is the same as that side.

The Koru (the unfurling fern frond, a symbol from Te Ao Māori representing new life, growth, and renewal) is a spiral. It has depth. It has a centre you approach but that remains itself. It unfurls into reality rather than reducing to either side of an equation.

Every time physics writes F = ma, it captures a ratio between shadows of the thing. The thing — the grain of sand, the Koru — casts those shadows. The shadows are real. But the grain is more than all of them together.

That is why a Koru, not an =. The Koru says: here is a thing. It connects. It holds itself. It participates in everything without being consumed by anything.

---

*All you need is to know Koru.*

---

**Author**: Tobias McRae, Independent Researcher, Aotearoa New Zealand
**Repository**: https://github.com/Tobillicious/universal-protection-theory
**Zenodo**: DOI 10.5281/zenodo.24357635
**License**: CC BY 4.0
