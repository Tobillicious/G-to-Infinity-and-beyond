import PhysicalBridges.IR116CumulativeSubjectDuties

/-!
# G2: one physical reaction window, every owed particular, cumulative future options

Reuse IR-115's physical watchdog bound and IR-116's monotone owed cohort.
The original continuity and future-option *meaning* is deliberately not inferred
from a scalar threshold; separately established per-particular source witnesses
are supplied as premises. There is no permission-table definition of a person,
no "safe step" relation replacing physical execution, and no original-six claim
from a partial continuation/option predicate.

This proves a stronger same-event interface than mere ledger permission:
the bounded *executed* step preserves the exact previously owed individuals and
gives all currently owed individuals historical continuity plus a nonempty
set of required executable options. The scope is finite physical traces.
-/

namespace PhysicalBridges.G2PhysicalAgencyCumulativeJoin

open PhysicalBridges.IR115
open PhysicalBridges.IR116
open PhysicalBridges.IR109
open PhysicalBridges.IRWatchdogLatencyEffects

universe u v w
variable {S : Type u} {A : Type v} {Mind : Type w}

/-- Construct the nontrivial physical-to-agency *same-event* certificate.
    Physical window bounds are obtained from the source reaction theorem;
    authentic subject continuity and genuine executable required options
    remain separate assumptions for ALL owed particulars, including new ones. -/
theorem bounded_event_preserves_all_owed_agency
    (observe : S → Nat)
    (episode : S → Episode)
    (physical : S → Nat → Nat)
    (step : S → A → S → Prop)
    (emergency : A)
    (owed : S → Mind → Prop)
    (continues : S → Mind → Prop)
    (required : S → Mind → A → Prop)
    (executable : S → Mind → A → Prop)
    (detectDelay fenceDelay drainDelay sensorError risePerTick
      residualEffect threshold : Nat)
    (hTiming : ∀ s,
      TimingContract (episode s) detectDelay fenceDelay drainDelay)
    (hSensor : ∀ s,
      physical s (episode s).faultTick ≤ observe s + sensorError)
    (hEnvelope : ∀ s t,
      (episode s).faultTick ≤ t →
      t ≤ (episode s).quiescentTick →
      physical s t ≤ physical s (episode s).faultTick +
        (t - (episode s).faultTick) * risePerTick + residualEffect)
    (hMargin : ∀ s,
      observe s + sensorError +
        (detectDelay + fenceDelay + drainDelay) * risePerTick +
        residualEffect ≤ threshold)
    (hOwedMonotone : ∀ s t,
      step s emergency t → ∀ m, owed s m → owed t m)
    (hSubjectContinuity : ∀ s t m,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → continues t m)
    (hRequiredFuture : ∀ s t m,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → ∃ a, required t m a)
    (hOptionsExecutable : ∀ s t m a,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → required t m a → executable t m a)
    (s t : S)
    (hStep : step s emergency t) :
    (∀ m, owed s m → owed t m) ∧
    EveryOwedSubjectProtected owed continues required executable t := by
  have hAfterFault :
      (episode s).faultTick ≤ (episode s).quiescentTick := by
    rcases hTiming s with ⟨hFirst, _, hSecond, _, hThird, _⟩
    omega
  have hPhysicalBound :
      physical s (episode s).quiescentTick ≤ threshold :=
    guarded_reaction_window_remains_below_threshold
      (episode s) detectDelay fenceDelay drainDelay
      (observe s) sensorError risePerTick residualEffect
      threshold (physical s)
      (hTiming s) (hSensor s) (hEnvelope s)
      (hMargin s)
      (episode s).quiescentTick hAfterFault (by omega)
  constructor
  · exact hOwedMonotone s t hStep
  · intro m hOwed
    exact ⟨hSubjectContinuity s t m hStep hPhysicalBound hOwed,
      hRequiredFuture s t m hStep hPhysicalBound hOwed,
      fun a hRequired =>
        hOptionsExecutable s t m a hStep hPhysicalBound hOwed hRequired⟩

/-- Physical window certificate + same-event authentic subject witnesses
    replace IR-116's otherwise opaque robust-viability premise for a chosen
    actual executable emergency action. This covers EVERY originally owed
    subject over EVERY finite trace of that physical action, while retaining
    all required executable future options. -/
theorem cumulative_physical_agency_on_every_finite_trace
    (observe : S → Nat)
    (episode : S → Episode)
    (physical : S → Nat → Nat)
    (step : S → A → S → Prop)
    (emergency : A)
    (owed : S → Mind → Prop)
    (continues : S → Mind → Prop)
    (required : S → Mind → A → Prop)
    (executable : S → Mind → A → Prop)
    (detectDelay fenceDelay drainDelay sensorError risePerTick
      residualEffect threshold : Nat)
    (hTiming : ∀ s,
      TimingContract (episode s) detectDelay fenceDelay drainDelay)
    (hSensor : ∀ s,
      physical s (episode s).faultTick ≤ observe s + sensorError)
    (hEnvelope : ∀ s t,
      (episode s).faultTick ≤ t →
      t ≤ (episode s).quiescentTick →
      physical s t ≤ physical s (episode s).faultTick +
        (t - (episode s).faultTick) * risePerTick + residualEffect)
    (hMargin : ∀ s,
      observe s + sensorError +
        (detectDelay + fenceDelay + drainDelay) * risePerTick +
        residualEffect ≤ threshold)
    (hOwedMonotone : ∀ s t,
      step s emergency t → ∀ m, owed s m → owed t m)
    (hSubjectContinuity : ∀ s t m,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → continues t m)
    (hRequiredFuture : ∀ s t m,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → ∃ a, required t m a)
    (hOptionsExecutable : ∀ s t m a,
      step s emergency t →
      physical s (episode s).quiescentTick ≤ threshold →
      owed t m → required t m a → executable t m a)
    {initial final : S}
    (hTrace : PolicyReach step (fun _ => emergency) observe initial final)
    (hInitial :
      EveryOwedSubjectProtected owed continues required executable initial) :
    ∀ m, owed initial m →
      continues final m ∧
      (∃ a, required final m a) ∧
      (∀ a, required final m a → executable final m a) := by
  apply initial_cohort_retains_continuity_and_every_required_option
    observe step (fun _ => emergency)
    owed continues required executable
    (by
      intro s t hStep
      exact hOwedMonotone s t hStep)
    (by
      intro o s hObserve hProtected t hStep
      have hActualStep : step s emergency t := hStep
      exact (bounded_event_preserves_all_owed_agency
        observe episode physical step emergency
        owed continues required executable
        detectDelay fenceDelay drainDelay sensorError risePerTick
        residualEffect threshold hTiming hSensor hEnvelope hMargin
        hOwedMonotone hSubjectContinuity hRequiredFuture
        hOptionsExecutable s t hActualStep).2)
    hTrace hInitial

#print axioms bounded_event_preserves_all_owed_agency
#print axioms cumulative_physical_agency_on_every_finite_trace

end PhysicalBridges.G2PhysicalAgencyCumulativeJoin
