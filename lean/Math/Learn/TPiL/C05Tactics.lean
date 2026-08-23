/-
Copyright (c) 2026 @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
-/

/-!
# Theorem Proving in Lean 4 — Chapter 5: Tactics

Exercises go here.

No `import Mathlib`: TPiL is about the language rather than the library, and
its exercises run on core Lean. Add imports if and when an exercise needs them.
-/

namespace s1

theorem test (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
  apply And.intro
  exact hp
  apply And.intro
  exact hq
  exact hp

#print test

variable (p q : Prop)

theorem test' : p → q → p ∧ q ∧ p :=
  fun hp : p => fun hq : q => ⟨hp, ⟨hq, hp⟩⟩

theorem test'' (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
  apply And.intro hp ; exact And.intro hq hp

theorem test''' (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
  apply And.intro
  case left => exact hp
  case right =>
    apply And.intro
    case left => exact hq
    case right => exact hp

theorem test'''' (p q : Prop) (hp : p) (hq : q) : p ∧ q ∧ p := by
  apply And.intro
  · exact hp
  · apply And.intro
    · exact hq
    · exact hp

end s1

namespace s2

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  · intro h
    apply Or.elim (And.right h)
    · intro hq
      apply Or.inl
      apply And.intro
      · exact And.left h
      · exact hq
    · intro hr
      apply Or.inr
      apply And.intro
      · exact And.left h
      · exact hr
  · intro h
    apply Or.elim h
    · intro hpq
      apply And.intro
      · exact And.left hpq
      · apply Or.inl
        exact And.right hpq
    · intro hpr
      apply And.intro
      · exact And.left hpr
      · apply Or.inr
        exact And.right hpr

example (α : Type) : α → α := by
  intro a
  exact a

example (α : Type) : ∀ x : α, x = x := by
  intro x
  exact Eq.refl x

example (p q : α → Prop) : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x := by
  intro ⟨w, hpw, hqw⟩
  exact ⟨w, hqw, hpw⟩

example (p q : α → Prop) : (∃ x, p x ∨ q x) → ∃ x, q x ∨ p x := by
  intro
  | ⟨w, Or.inl h⟩ => exact ⟨w, Or.inr h⟩
  | ⟨w, Or.inr h⟩ => exact ⟨w, Or.inl h⟩

variable (x y z w : Nat)

example (h₁ : x = y) (h₂ : y = z) (h₃ : z = w) : x = w := by
  apply Eq.trans h₁
  apply Eq.trans h₂
  assumption   -- applied h₃

example : ∀ a b c : Nat, a = b → a = c → c = b := by
  intros
  apply Eq.trans
  apply Eq.symm
  assumption
  assumption

example : ∀ a b c : Nat, a = b → a = c → c = b := by unhygienic
  intros
  apply Eq.trans
  apply Eq.symm
  exact a_2
  exact a_1

example : ∀ a b c : Nat, a = b → a = c → c = b := by
  intros
  apply Eq.trans
  apply Eq.symm
  repeat assumption

example (x : Nat) : x = x := by
  revert x
  intro y
  rfl

example (x y : Nat) (h : x = y) : y = x := by
  revert x y
  intros
  apply Eq.symm
  assumption

example : 3 = 3 := by
  generalize 3 = x
  revert x
  intro y
  rfl

example : 2 + 3 = 5 := by
  generalize h : 3 = x
  rw [← h]

end s2

namespace s3

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h with
  | inl hp => apply Or.inr ; exact hp
  | inr hq => apply Or.inl ; exact hq

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h
  apply Or.inr
  assumption
  apply Or.inl
  assumption

example (p : Prop) : p ∨ p → p := by
  intro h
  cases h
  repeat assumption

example (p : Prop) : p ∨ p → p := by
  intro h
  cases h <;> assumption

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h
  · apply Or.inr
    assumption
  · apply Or.inl
    assumption

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h
  case inr h =>
    apply Or.inl
    assumption
  case inl h =>
    apply Or.inr
    assumption

example (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h
  case inr h =>
    apply Or.inl
    assumption
  · apply Or.inr
    assumption

example (p q : Prop) : p ∧ q → q ∧ p := by
  intro h
  cases h with
  | intro hp hq => constructor ; exact hq ; exact hp

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  · intro h
    cases h with
    | intro hp hqr =>
      cases hqr
      · apply Or.inl ; constructor <;> assumption
      · apply Or.inr ; constructor <;> assumption
  · intro h
    cases h with
    | inl hpq =>
      cases hpq with
      | intro hp hq =>
        constructor ; exact hp ; apply Or.inl ; exact hq
    | inr hpr =>
      cases hpr with
      | intro hp hr =>
        constructor ; exact hp ; apply Or.inr ; exact hr

example (p q : Nat → Prop) : (∃ x, p x) → ∃ x, p x ∨ q x := by
  intro h
  cases h with
    | intro x px => constructor ; apply Or.inl ; exact px

example (p q : Nat → Prop) : (∃ x, p x) → ∃ x, p x ∨ q x := by
  intro h
  cases h with
  | intro x px => exists x ; apply Or.inl ; exact px

example (p q : Nat → Prop) : (∃ x, p x ∧ q x) → ∃ x, q x ∧ p x := by
  intro h
  cases h with
  | intro x hpq =>
    cases hpq with
    | intro hp hq =>
      exists x

def swap_pair : α × β → β × α := by
  intro p
  cases p
  constructor <;> assumption

def swap_sum : Sum α β → Sum β α := by
  intro p
  cases p
  · apply Sum.inr ; assumption
  · apply Sum.inl ; assumption

open Nat
example (P : Nat → Prop)
    (h₀ : P 0) (h₁ : ∀ n, P (succ n))
    (m : Nat) : P m := by
  cases m with
  | zero => exact h₀
  | succ m' => exact h₁ m'

example (p q : Prop) : p ∧ ¬p → q := by
  intro h
  cases h
  contradiction

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  · intro h
    match h with
    | ⟨_, Or.inl _⟩ =>
      apply Or.inl ; constructor <;> assumption
    | ⟨_, Or.inr _⟩ =>
      apply Or.inr ; constructor <;> assumption
  · intro h
    match h with
    | Or.inr ⟨_, _⟩ =>
      constructor ; assumption ; apply Or.inr ; assumption
    | Or.inl ⟨_, _⟩ =>
      constructor ; assumption ; apply Or.inl ; assumption

end s3

namespace s4

example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
  intro h
  exact
    have hp : p := h.left
    have hqr : q ∨ r := h.right
    show (p ∧ q) ∨ (p ∧ r) by
      cases hqr with
      | inl hq => exact Or.inl ⟨hp, hq⟩
      | inr hr => exact Or.inr ⟨hp, hr⟩

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  . intro h
    cases h.right with
    | inl hq => exact Or.inl ⟨h.left, hq⟩
    | inr hr => exact Or.inr ⟨h.left, hr⟩
  . intro h
    cases h with
    | inl hpq => exact ⟨hpq.left, Or.inl hpq.right⟩
    | inr hpr => exact ⟨hpr.left, Or.inr hpr.right⟩

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  · intro h
    cases h.right with
    | inl hq =>
      exact Or.inl ⟨h.left, hq⟩
    | inr hr =>
      exact Or.inr ⟨h.left, hr⟩
  · intro h
    cases h with
    | inl hpq =>
      exact ⟨hpq.left, Or.inl hpq.right⟩
    | inr hpr =>
      exact ⟨hpr.left, Or.inr hpr.right⟩

example (n : Nat) : n + 1 = Nat.succ n := by
  show Nat.succ n = Nat.succ n
  rfl

example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
  intro ⟨hp, hqr⟩
  cases hqr with
  | inl hq =>
    have hpq : p ∧ q := And.intro hp hq
    apply Or.inl
    exact hpq
  | inr hr =>
    have hpr : p ∧ r := And.intro hp hr
    apply Or.inr
    exact hpr

example (p q r : Prop) : p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r) := by
  intro ⟨hp, hqr⟩
  cases hqr with
  | inl hq =>
    have : p ∧ q := And.intro hp hq
    apply Or.inl
    exact this
  | inr hr =>
    have : p ∧ r := And.intro hp hr
    apply Or.inr
    exact this

example : ∃ x, x + 2 = 8 := by
  let a : Nat := 3 * 2
  exists a

example (p q r : Prop) : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) := by
  apply Iff.intro
  { intro h;
    cases h.right;
    { show (p ∧ q) ∨ (p ∧ r);
      exact Or.inl ⟨h.left, ‹q›⟩ }
    { show (p ∧ q) ∨ (p ∧ r);
      exact Or.inr ⟨h.left, ‹r›⟩ } }
  { intro h;
    cases h;
    { show p ∧ (q ∨ r);
      rename_i hpq;
      exact ⟨hpq.left, Or.inl hpq.right⟩ }
    { show p ∧ (q ∨ r);
      rename_i hpr;
      exact ⟨hpr.left, Or.inr hpr.right⟩ } }

end s4

namespace s5

example (p q : Prop) (hp : p) : p ∨ q := by
  apply Or.inl ; assumption

example (p q : Prop) (hp : p) (hq : q) : p ∧ q :=
  by constructor <;> assumption

example (p q : Prop) (hp : p) : p ∨ q := by
  first | apply Or.inl; assumption | apply Or.inr; assumption

example (p q : Prop) (hq : q) : p ∨ q := by
  first | apply Or.inl; assumption | apply Or.inr; assumption

example (p q r : Prop) (hp : p) : p ∨ q ∨ r := by
  repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)

example (p q r : Prop) (hq : q) : p ∨ q ∨ r := by
  repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)

example (p q r : Prop) (hr : r) : p ∨ q ∨ r := by
  repeat (first | apply Or.inl; assumption | apply Or.inr | assumption)

example (p q r : Prop) (hp : p) (hq : q) (hr : r) : p ∧ q ∧ r := by
  constructor <;> (try constructor) <;> assumption

example (p q r : Prop) (hp : p) (hq : q) (hr : r) : p ∧ q ∧ r := by
  constructor
  all_goals (try constructor)
  all_goals assumption

example (p q r : Prop) (hp : p) (hq : q) (hr : r) :
      p ∧ ((p ∧ q) ∧ r) ∧ (q ∧ r ∧ p) := by
  repeat (any_goals constructor)
  all_goals assumption

example (p q r : Prop) (hp : p) (hq : q) (hr : r) :
      p ∧ ((p ∧ q) ∧ r) ∧ (q ∧ r ∧ p) := by
  repeat (any_goals (first | constructor | assumption))

end s5

namespace s6

variable (k : Nat) (f : Nat → Nat)
  example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
    rw [h₂]
    rw [h₁]

example (x y : Nat) (p : Nat → Prop) (q : Prop) (h : q → x = y) (h' : p y) (hq : q) : p x := by
  rw [h hq] ; assumption

variable (a b : Nat) (f : Nat → Nat)
example (h₁ : a = b) (h₂ : f a = 0) : f b = 0 := by
  rw [←h₁, h₂]

example (f : Nat → Nat) (a : Nat) (h : a + 0 = 0) : f a = f 0 := by
  rw [Nat.add_zero] at h
  rw [h]

def Tuple (α : Type) (n : Nat) :=
  { as : List α // as.length = n}

example {α} (n : Nat) (h : n = 0) (t : Tuple α n) : Tuple α 0 := by
  rw [h] at t
  exact t

end s6

namespace s7

example (x y z : Nat) : (x + 0) * (0 + y * 1 + z * 0) = x * y := by
  simp

example (x y z : Nat) (p : Nat → Prop) (h : p (x * y)) : p ((x + 0) * (0 + y * 1 + z * 0)) :=
  by simp ; assumption

open List

example (xs : List Nat) : reverse (xs ++ [1, 2, 3]) = [3, 2, 1] ++ reverse xs := by
  simp

example (xs ys : List α) : length (reverse (xs ++ ys)) = length xs + length  ys := by
  simp [Nat.add_comm]

example (x y z : Nat) (p : Nat → Prop)
  (h : p ((x + 0) * (0 + y * 1 + z * 0))) : p (x * y) := by
  simp at h ; assumption

attribute [local simp] Nat.mul_comm Nat.mul_assoc Nat.mul_left_comm
attribute [local simp] Nat.add_assoc Nat.add_comm Nat.add_left_comm

example (w x y z : Nat) (p : Nat → Prop)
        (h : p (x * y + z * w * x)) : p (x * w * z + y * x) := by
  simp at *; assumption

example (x y z : Nat) (p : Nat → Prop)
        (h₁ : p (1 * x + y)) (h₂ : p (x * z * 1))
        : p (y + 0 + x) ∧ p (z * x) := by
  simp at * <;> constructor <;> assumption

variable (k : Nat) (f : Nat → Nat)

example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
  simp [h₁, h₂]

example (h₁ : f 0 = 0) (h₂ : k = 0) : f k = 0 := by
  simp [*]

set_option linter.unusedVariables false
set_option linter.unusedVariables false
example (u w x x' y y' z : Nat) (p : Nat → Prop)
        (h₁ : x + 0 = x') (h₂ : y + 0 = y')
        : x + y + 0 = x' + y' := by
  simp at *
  simp [*]

end s7
