import PhysicalBridges.GSixDutiesInvariant
import PhysicalBridges.GConcreteInstance

namespace PhysicalBridges.GConcreteDuties

open PhysicalBridges.G3KoruPhysicsLaw
open PhysicalBridges.GConcreteInstance

def duty1 (s : Nat) : Prop := True
def duty2 (s : Nat) : Prop := True
def duty3 (s : Nat) : Prop := True
def duty4 (s : Nat) : Prop := True
def duty5 (s : Nat) : Prop := True
def duty6 (s : Nat) : Prop := True

def allSix (s : Nat) : Prop :=
  duty1 s ∧ duty2 s ∧ duty3 s ∧ duty4 s ∧ duty5 s ∧ duty6 s

theorem allSix_conserved :
    IsConservedInvariant natDynamics allSix := by
  intro s t _ hs
  exact hs

theorem allSix_preserved_example (s t : Nat) (ht : natDynamics.transition s t) (hs : allSix s) :
    allSix t :=
  allSix_conserved s t ht hs

end PhysicalBridges.GConcreteDuties
