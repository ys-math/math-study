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

namespace s4

def double (n : Nat) : Nat := n + n
#eval double 3

def double' : Nat → Nat := fun x => x + x
#eval double' 3

def doTwice (f : Nat → Nat) (x : Nat) : Nat := f (f x)

#eval doTwice double 3

def compose (α β γ : Type) (g : β → γ) (f : α → β) (x : α) : γ := g (f x)
def square (x : Nat) : Nat := x * x
#eval compose Nat Nat Nat double square 3

end s4

namespace s5

#check let y := 2 + 2; y * y
#eval let y := 2 + 2; y * y

def twice_double (x : Nat) : Nat :=
  let y := x + x; y * y

#eval twice_double 2

def foo := let a := Nat; fun x : a => x + 2
/- def bar := (fun a => fun x : a => x + 2) Nat -/

end s5

namespace s6

variable (α β γ : Type)

def compose (g : β → γ) (f : α → β) (x : α) : γ :=
  g (f x)

#print compose
end s6

namespace s7

  namespace Foo
    def a : Nat := 5
    def f (x : Nat) : Nat := x + 7

    def fa : Nat := f a
    def ffa : Nat := f (f a)

    #check a  #check f  #check fa  #check ffa  #check Foo.fa

  end Foo

  -- #check a  -- error
  -- #check f  -- error
  #check Foo.a#check Foo.f#check Foo.fa#check Foo.ffa

  open Foo

  #check a#check f#check fa#check Foo.fa

open List
#check nil

open Nat
#check succ

end s7

namespace s8

def cons (α : Type) (a : α) (as : List α) : List α := List.cons a as

#check cons Nat
#check cons

#check @List.cons
#check List.cons

section s1
variable (α : Type) (β : α → Type)

#check Σ a : α, β a
end s1

universe u v

def f (α : Type u) (β : α → Type v) (a : α) (b : β a) : (a : α) × β a := ⟨a, b⟩

def g (α : Type u) (β : α → Type v) (a : α) (b : β a) : Σ a : α, β a := Sigma.mk a b

def h1 (x : Nat) : Nat := (f Type (fun α => α) Nat x).2

#eval h1 5

end s8

namespace s9

#check List

universe u
def Lst (α : Type u) : Type u := List α
def Lst.cons (α : Type u) (a : α) (as : Lst α) : Lst α := List.cons a as
def Lst.nil (α : Type u) : Lst α := List.nil
def Lst.append (α : Type u) (as bs : Lst α) : Lst α := List.append as bs

def as : Lst Nat := Lst.nil Nat
def bs : Lst Nat := Lst.cons Nat 5 (Lst.nil Nat)

#check Lst.append Nat as bs
#check Lst.append _ as bs

def ident {α : Type u} (x : α) := x
#check (ident)
#check ident 1
#check ident "Hello"
#check ident true
#check @ident
#check ident
#check @id

#check (List.nil)
#check (id)

end s9
