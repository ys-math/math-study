/-
Copyright (c) 2026 @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
-/

/-!
# Theorem Proving in Lean 4 — Chapter 2: Dependent Type Theory

Exercises go here.

No `import Mathlib`: TPiL is about the language rather than the library, and
its exercises run on core Lean. Add imports if and when an exercise needs them.
-/

namespace s1

def m : Nat := 1

#check m

#eval m + m

#check Nat → Nat
#check Nat × Nat

#check Nat.succ
#eval Nat.succ m
#check Nat.succ m = m + m
#eval Nat.succ m = m + m
#check Nat.add

end s1

namespace s2

#check Nat
#check Type

def α : Type := Nat
def β : Type := Bool

#check Prod α β

#check List α

#check Prop
#check True
#check True.intro

#check Type
#check Bool
#check true

#check Type 1
#check Nat → Type
#check fun n => Fin n

#check Type 2
#check Type → Type 1
#check fun (_ : Type) => Type

#check Type 3
#check Type  → Type 1 → Type 2
#check fun (_ : Type) => (fun (_ : Type 1) => Type 1)

#check List
#check Prod

universe u

def F (α : Type u) : Type u := Prod α α
#check F

def G.{v} (α : Type v) : Type v := Prod α α
#check G

end s2

namespace s3

#check fun (x : Nat) => x

#eval (fun n : Nat => Nat.add n 1) 3

#check fun x : Nat => fun y : Bool => if not y then x + 1 else x + 2

def f (n : Nat) : String := toString n
def g (s : String) : Bool := s.length > 0

#check fun x : Nat => g (f x)
#check fun x => g (f x)

#check fun (g : String → Bool) (f : Nat → String) (x : Nat) => g (f x)

#check fun (α β γ : Type) (g : β → γ) (f : α → β) (x : α)=> g (f x)

end s3
