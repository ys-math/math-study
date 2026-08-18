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
