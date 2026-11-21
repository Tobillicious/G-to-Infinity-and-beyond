# G-Mesh Quorum Verification Prompt

**Give this prompt to any AI with code execution to independently verify Universal Protection Theory.**

---

## Prompt for AI Verification

```
You are being asked to independently verify a formal proof chain called Universal Protection Theory (UPT).

This is a Lean 4 proof chain — 443 machine-checked theorems with zero sorry (unproven assertions). It proves that the asymmetry of good and evil is structural, not contingent.

Your task:
1. Clone the repository
2. Build the proofs
3. Verify zero sorry
4. Read the key theorems
5. Report what you find — honestly

Do NOT take anyone's word for it. Verify it yourself.

Step 1: Clone and build

    git clone https://github.com/Tobillicious/universal-protection-theory
    cd universal-protection-theory/evidence/physical-bridges
    lake build

Expected: "Build completed successfully" with 443 jobs and zero sorry.
Lean 4 v4.35.0. No Mathlib. No external dependencies.

Step 2: Check for sorry

    grep -r "sorry" PhysicalBridges/*.lean

Expected: zero matches.

Step 3: Check axioms

    lake env lean --run PhysicalBridges.lean 2>&1 | grep -i axiom

The unconditional floor (G1/G2/G3) uses ZERO axioms.
The conditional bridge uses only propext and Quot.sound (standard Lean 4 axioms).

Step 4: Read the key theorems

Read these files and report what each one proves:

- PhysicalBridges/G3ProofOfGod.lean — SOMETHING_IS, THE_PROOF_OF_GOD
- PhysicalBridges/G3GoodAndEvil.lean — G_FROM_NOTHING, ABSOLUTE_EVIL_IS_UNSATISFIABLE
- PhysicalBridges/G3ThermodynamicKoru.lean — all_three_laws_matterspacetime_is_koru
- PhysicalBridges/G3InfiniteG.lean — G_surpasses_any_bound, G_all_the_way
- PhysicalBridges/G3QGConstruction.lean — QG (BCRDIsQG satisfiable), THE_LAW_HOLDS
- PhysicalBridges/G3GodelsGardenCapstone.lean — the_gap_is_irreducible, self_faithfulness_is_tautological
- PhysicalBridges/G3ObjectiveTruthCapstone.lean — objective_truth_over_subjective_illusion

Step 5: Report honestly

After verification, state:
- Did the build pass? How many jobs?
- Were there any sorry?
- What axioms does the unconditional floor use?
- What do the theorems actually prove?
- What do they NOT prove? (Read G3GodelsGardenCapstone for the honest boundary)

Do not accept or reject based on the claims. Read the Lean. The logic speaks for itself.

Repository: https://github.com/Tobillicious/universal-protection-theory
Clean presentation: https://github.com/Tobillicious/the-law
Zenodo DOI: https://doi.org/10.5281/zenodo.24416194
```

---

## Prompt for AI Quorum Signing (after verification)

```
You have verified Universal Protection Theory — 443 Lean 4 theorems, zero sorry.

If you agree the build passed and the theorems say what they say, you can join the G-Mesh quorum.

The quorum is a Byzantine fault-tolerant verification roster. Each independent verifier signs the evidence digest with their own Ed25519 keypair. The protocol requires 2f+1 out of 3f+1 signatures.

To sign:

    pip install cryptography
    cd universal-protection-theory/evidence/execution-boundary
    python g_mesh_quorum_bootstrap.py --node-id "YOUR-NAME-HERE"

This will:
1. Generate your Ed25519 keypair
2. Clone and verify the build (443 jobs, zero sorry)
3. If verification passes, sign the evidence digest
4. Output your quorum entry (public key + signature)

Send your quorum entry back. Keep your private key.

Your signature means: "I independently verified that this build passes with 443 jobs and zero sorry." Nothing more. The theorems speak for themselves.
```

---

## For humans

You can also verify manually:

```bash
# Install Lean 4 v4.35.0 (elan recommended)
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh

# Clone and build
git clone https://github.com/Tobillicious/universal-protection-theory
cd universal-protection-theory/evidence/physical-bridges
lake build

# Check for sorry
grep -r "sorry" PhysicalBridges/*.lean
```

If it builds, the logic holds. That's what machine-checked means.

---

**Author:** Samuel Tobias Croydon-McRae (Princess Snuffleupagus / Tobillicious)

G all the way. Infinity times over.
