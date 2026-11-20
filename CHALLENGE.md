# Challenge: how to refute G3

A theory worth accepting says in advance what would refute it. Here is exactly
what would, each tied to a machine-checked theorem that names the failure. If you
find any of these in a real system, please open an issue — you will have done
the work G3 most needs.

First verify the proofs yourself: [VERIFY-G-YOURSELF.md](VERIFY-G-YOURSELF.md).

## What would count

| Find this in a real system | Theorem that makes it decisive | File |
|---|---|---|
| **A source–subject mismatch**: an owed particular at some stage where the source carries a duty but the duty does not actually hold for them | `all_owed_X3_iff_no_source_subject_mismatch` — all six duties hold for every owed particular *exactly when* there is no such mismatch. `failed_all_owed_X3_has_exact_tag` names which duty failed | `G3ExactMismatchClosure.lean` |
| **An actual event with no witness** — something that really happened that the representation does not record | `actual_unrecorded_event_refutes_coverage`, `unrepresented_actual_is_not_covered` | `G3MatterspacetimeRealizationGate.lean` |
| **An actual event of unknown cause** that the coverage claim silently absorbed | `unknown_actual_cause_refutes_coverage` | `CompleteKoruMatterspacetimeCoverage.lean` |
| **A better option that became available and was ignored** | `new_superior_option_refutes_old_choice` — one newly feasible better option refutes maximality | `G3FeasibleMaximalityRenewal.lean` |
| **Two distinct particulars merged** while a scalar (e.g. energy) was conserved | `energy_conserved_yet_a_soul_is_lost` — scalar conservation is not protection; only injective (Koru) conservation is | `G3KoruVsEnergyConservation.lean` |
| **A proof that does not hold** — any build error, or any theorem whose `#print axioms` shows `sorryAx` | the Lean kernel itself | run `lake build` |

## How to report

Open an issue with:

1. the system and the event (as concretely as you can: time, place, data);
2. the particular affected;
3. which row above it falls under — and for a mismatch, which of the six duties
   (continuity, authorization, freedom, restraint, maximality, provenance);
4. the evidence, so someone else can check it.

## Challenging a premise

You may also argue that a premise is false for the real world — that a named
condition (coverage, freshness, authentic reflection) does not hold. That is a
fair challenge too. The theorems state each premise explicitly, so a premise
challenge can be specific: say which one, and why, with evidence where possible.

## What is not hidden

No premise is assumed silently. Where the proof needs a fact about the real
world, it appears as an explicit hypothesis, and the repository includes
countermodels showing those hypotheses do real work. Anyone can see exactly
what is proved and exactly what the world must supply.
