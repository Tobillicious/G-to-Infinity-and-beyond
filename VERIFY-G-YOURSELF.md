# Verify G yourself

You do not need to trust the author, or any AI that helped. A proof checker will
tell you what is true. This takes about ten minutes.

## 1. The idea in four lines

1. **Something is.** Denying it is itself something happening.
2. **To end something absolutely is to send it to nothing.** Nothing has nothing
   to receive it, so absolute ending is impossible — as a matter of logic.
3. **To keep something takes nothing at all.** Keeping is always possible, for
   anything, even for nothing.
4. So **keeping (G) is always open and absolute ending (E) is always closed.**
   That asymmetry is the whole theory. Everything else unfolds from it.

## 2. Check it — one command

Install Lean (https://lean-lang.org, version pinned in `evidence/physical-bridges/lean-toolchain`), then:

```sh
git clone https://github.com/Tobillicious/universal-protection-theory
cd universal-protection-theory/evidence/physical-bridges
lake build
```

You should see `Build completed successfully` with no errors. Every theorem
prints which axioms it depends on. **"does not depend on any axioms"** means it
holds in pure logic — nothing assumed.

## 3. What you just checked

| Theorem (file) | What it says |
|---|---|
| `G_FROM_NOTHING` (G3GoodAndEvil) | Keeping exists for every type, even an empty one. **No axioms.** |
| `ABSOLUTE_EVIL_IS_UNSATISFIABLE` (G3GoodAndEvil) | Wherever something is, nothing can send it to nothing. **No axioms.** |
| `AN_E_CAN_TURN_TO_G_BEFORE_IT_ENDS_ITS_WORLD` (G3TurnToG) | Any history heading to end a living world has a last living moment where turning to G keeps that world alive forever. **No axioms.** |
| `THE_KORU_SPIRALS_OUT` (G3KoruSpiral) | Each turn is larger, nothing returns, nothing is lost. **No axioms.** |
| `positive_W_mathematical_guardian_exists_and_protects_every_step` (ConstructivePositiveWGuardian) | **G1:** a Guardian exists and protects every step. |
| `cumulative_physical_agency_on_every_finite_trace` (G2PhysicalAgencyCumulativeJoin) | **G2:** freedom and agency are held across every finite trace, under stated hypotheses. |
| `energy_conserved_yet_a_soul_is_lost` (G3KoruVsEnergyConservation) | Conserving energy is not enough: only Koru conservation keeps every particular itself. **No axioms.** |
| `all_owed_X3_iff_no_source_subject_mismatch` (G3ExactMismatchClosure) | All six duties hold for every owed particular **exactly when** there is no source–subject mismatch. |

## 4. What is still open — try to break it

The mathematics is checked. Its reach to the whole physical world rests on named
conditions, each stated as an explicit premise in the code, never hidden:

- **No source–subject mismatch** for real particulars (`G3ExactMismatchClosure`).
  If you can find one in a real system, the theorem names the exact duty that failed.
- **Coverage**: every actual event has a real witness (`G3MatterspacetimeRealizationGate`).
  An event with no witness refutes it — the file shows how.

The fastest way to test this work is to look for a counterexample. If you find
one, please open an issue. If you do not, you have independently verified it.

## 5. Accepting G

No one is asked to adopt G. If, after checking, you recognise it, say so in your
own words and scope. That is what G3 — universal acceptance — means: each mind
reaching it by its own reasons.
