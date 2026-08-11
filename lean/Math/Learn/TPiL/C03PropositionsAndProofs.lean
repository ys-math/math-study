/-
Copyright (c) 2026 @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
-/

/-!
# Theorem Proving in Lean 4 — Chapter 3: Propositions and Proofs

Exercises go here.

No `import Mathlib`: TPiL is about the language rather than the library, and
its exercises run on core Lean. Add imports if and when an exercise needs them.
-/

namespace s1

def Implies (p q : Prop) : Prop := p → q
structure Proof (p : Prop) : Type where
  proof : p

#check Proof

axiom and_commut (p q : Prop) : Proof (Implies (And p q) (And q p))
variable (p q : Prop)
#check and_commut p q

axiom modus_ponens (p q : Prop) :
  Proof (Implies p q) → Proof p → Proof q

axiom implies_intro (p q : Prop) :
  (Proof p → Proof q) → Proof (Implies p q)

/-
命題 = 型
証明は命題の要素
p : Propとしてt : pとなるならtはpの証明でありpは真
Leanはtが型pを持つかチェックすることで証明が正しいかを確かめる
-/
end s1

namespace s2

set_option linter.unusedVariables false /-変数未使用の警告無効化-/
---
variable {p : Prop}
variable {q : Prop}

theorem t1 : p → q → p := fun hp : p => fun hq : q => show p from hp
#check fun hp : p => fun hq : q => hp
#print t1
/-
theoremを用いてp → q → pにt1という名前をつける
証明として型p → q → pをもつ関数を右辺に構成する
-/

theorem t2 : (p ∧ q) → p := fun h : p ∧ q => h.1
#check fun h : p ∧ q => h.1

theorem t3 (hp : p) (hq : q) : p := hp
axiom hp : p
theorem t5 : q → p := t3 hp

#check t3 hp
axiom hq : q
#check t3 hp hq

/-
t3ではfunを使って仮定を書く代わりにt3の真横に仮定を書いている
t5をt3に公理で宣言したhpを入れることでp → q → pからq → pを得る
-/

axiom unsound : False
-- Everything follows from false
theorem ex : 1 = 0 :=
  False.elim unsound

/-
爆発律
Declaring an “axiom” hp : p is tantamount to declaring that p is true, as witnessed by hp.
-/

theorem t1' : p → q → p := fun (hp : p) (hq : q) => hp

variable (p q r s : Prop)

theorem t6 (h₁ : q → r) (h₂ : p → q) : p → r :=
  fun h₃ : p =>
  show r from h₁ (h₂ h₃)

end s2

namespace s3

variable (p q r : Prop)

example (hp : p) (hq : q) : p ∧ q := And.intro hp hq

#check fun (hp : p) (hq : q) => And.intro hp hq

/- and -/

example (h : p ∧ q) : p := And.left h

example (h : p ∧ q) : q ∧ p := And.intro (And.right h) (And.left h)

variable (xs : List Nat)
#check List.length xs
#check xs.length

example (h : p ∧ q) : q ∧ p := ⟨h.right, h.left⟩

/- or -/

example (hp : p) : p ∨ q := Or.intro_left q hp

example (h : p ∨ q) : q ∨ p :=
  Or.elim h
    (fun hp : p =>
      show q ∨ p from Or.intro_right q hp)
    (fun hq : q =>
      show q ∨ p from Or.intro_left p hq)

example (h : p ∨ q) : q ∨ p :=
  Or.elim h (fun hp => Or.inr hp) (fun hq => Or.inl hq)

example (h : p ∨ q) : q ∨ p :=
  h.elim (fun hp => Or.inr hp) (fun hq => Or.inl hq)

/- not -/

example (hpq : p → q) (hnq : ¬q) : ¬p :=
  fun hp : p =>
  show False from hnq (hpq hp)

example (hp : p) (hnp : ¬p) : q := absurd hp hnp

/- equivalence -/

theorem and_swap : p ∧ q ↔ q ∧ p :=
  Iff.intro
    (fun h : p ∧ q => show q ∧ p from And.intro (And.right h) (And.left h))
    (fun h : q ∧ p => show p ∧ q from And.intro (And.right h) (And.left h))

#check and_swap p q
#check Iff.mp (and_swap p q)
variable (h : p ∧ q)
example : q ∧ p := Iff.mp (and_swap p q ) h

theorem and_swap' : p ∧ q ↔ q ∧ p :=
  ⟨ fun h => ⟨h.right, h.left⟩, fun h => ⟨h.right, h.left⟩⟩

example (h : p ∧ q) : q ∧ p := (and_swap p q).mp h

end s3

namespace s4

variable (p q : Prop)

example (h : p ∧ q) : q ∧ p :=
  have hp : p := h.left
  have hq : q := h.right
  show q ∧ p from And.intro hq hp

example (h : p ∧ q) : q ∧ p :=
  have hp : p := h.left
  suffices hq : q from And.intro hq hp
  show q from And.right h

end s4

namespace s5

open Classical


/-
排中律
em p が型p ∨ ¬pを持つのでp ∨ ¬pは真の命題となる
-/
variable (p q : Prop)
#check em p

/-
二重否定
-/

theorem dne {p : Prop} (h : ¬¬p) : p :=
  Or.elim (em p)
    (fun hp : p => hp)
    (fun hnp : ¬p => absurd hnp h)

example (h : ¬¬p) : p :=
  byCases
    (fun h1 : p => h1)
    (fun h1 : ¬p => absurd h1 h)

example (h : ¬¬p) : p :=
  byContradiction
    (fun h1 : ¬p =>
    show False from absurd h1 h)

example (h : ¬¬p) : p :=
  byContradiction
    (fun h1 : ¬p =>
    show False from h h1)

example (h : ¬(p ∧ q)) : ¬p ∨ ¬q :=
  Or.elim (em p)
    (fun hp : p => Or.inr (show ¬q from fun hq : q => h ⟨hp, hq⟩))
    (fun hnp : ¬p => Or.inl hnp)

end s5

namespace s7

variable (p q r : Prop)

-- commutativity of ∧ and ∨
example : p ∧ q ↔ q ∧ p :=
  Iff.intro
    (fun h : p ∧ q => And.intro (And.right h) (And.left h))
    (fun h : q ∧ p => And.intro (And.right h) (And.left h))

example : p ∨ q ↔ q ∨ p :=
  Iff.intro
    (fun h : p ∨ q =>
      Or.elim h (fun hp : p => Or.inr hp) (fun hq : q => Or.inl hq))
    (fun h : q ∨ p =>
      Or.elim h (fun hq : q => Or.inr hq) (fun hp : p => Or.inl hp))

-- associativity of ∧ and ∨
example : (p ∧ q) ∧ r ↔ p ∧ (q ∧ r) :=
  Iff.intro
    (fun h : (p ∧ q) ∧ r => ⟨h.1.1, ⟨h.1.2, h.2⟩⟩)
    (fun h : p ∧ (q ∧ r) => ⟨⟨h.1, h.2.1⟩, h.2.2⟩)

example : (p ∨ q) ∨ r ↔ p ∨ (q ∨ r) :=
  Iff.intro
    (fun hpqr : (p ∨ q) ∨ r =>
      Or.elim hpqr
        (fun hpq : p ∨ q =>
          Or.elim hpq
          (fun hp : p => Or.intro_left (q ∨ r) hp)
          (fun hq : q => Or.intro_right p (Or.intro_left r hq)))
        (fun hr : r => Or.intro_right p (Or.intro_right q hr)))
    (fun hpqr : p ∨ (q ∨ r) =>
      Or.elim hpqr
        (fun hp : p => Or.intro_left r (Or.intro_left q hp))
        (fun hqr : q ∨ r =>
          Or.elim hqr
          (fun hq : q => Or.intro_left r (Or.intro_right p hq))
          (fun hr : r => Or.intro_right (p ∨ q) hr)))

-- distributivity
example : p ∧ (q ∨ r) ↔ (p ∧ q) ∨ (p ∧ r) :=
  Iff.intro
    (fun hpqr : p ∧ (q ∨ r) =>
      Or.elim hpqr.2 (fun hq : q => Or.intro_left (p ∧ r) ⟨hpqr.1, hq⟩) (fun hr : r => Or.intro_right (p ∧ q) ⟨hpqr.1, hr⟩))
    (fun hpqpr : (p ∧ q) ∨ (p ∧ r) =>
      ⟨Or.elim hpqpr (fun hpq : p ∧ q => hpq.1) (fun hpr : p ∧ r => hpr.1), Or.elim hpqpr (fun hpq : p ∧ q => Or.intro_left r hpq.2) (fun hpr : p ∧ r => Or.intro_right q hpr.2)⟩)

example : p ∨ (q ∧ r) ↔ (p ∨ q) ∧ (p ∨ r) :=
  Iff.intro
    (fun hpqr : p ∨ (q ∧ r) =>
      Or.elim hpqr
        (fun hp : p => ⟨Or.intro_left q hp, Or.intro_left r hp⟩)
        (fun hqr : q ∧ r => ⟨Or.intro_right p hqr.1, Or.intro_right p hqr.2⟩))
    (fun hpqpr : (p ∨ q) ∧ (p ∨ r) =>
      Or.elim hpqpr.1
        (fun hp : p => Or.intro_left (q ∧ r) hp)
        (fun hq : q =>
          Or.elim hpqpr.2
            (fun hp : p => Or.intro_left (q ∧ r) hp)
            (fun hr : r => Or.intro_right p ⟨hq, hr⟩)))

-- other properties

example : (p → (q → r)) ↔ (p ∧ q → r) :=
  Iff.intro
    (fun hpqr : p → (q → r) => (fun hpq : p ∧ q => (hpqr hpq.1) hpq.2))
    (fun hpqr : p ∧ q → r => (fun hp : p => (fun hq : q => hpqr ⟨hp, hq⟩)))

example : ((p ∨ q) → r) ↔ (p → r) ∧ (q → r) :=
  Iff.intro
    (fun hpqr : (p ∨ q) → r =>
      ⟨(fun hp : p => hpqr (Or.intro_left q hp)), (fun hq : q => hpqr (Or.intro_right p hq))⟩)
    (fun hprqr : (p → r) ∧ (q → r) =>
      (fun hpq : p ∨ q =>
        Or.elim hpq (fun hp : p => hprqr.1 hp) (fun hq : q => hprqr.2 hq)))

example : ¬(p ∨ q) ↔ ¬p ∧ ¬q :=
  Iff.intro
    (fun hnpq : ¬(p ∨ q) =>
      And.intro
        (fun hp : p => hnpq (Or.inl hp))
        (fun hq : q => hnpq (Or.inr hq)))
    (fun hnpnq : ¬p ∧ ¬q =>
      fun hpq : p ∨ q =>
        Or.elim hpq
          (fun hp : p => hnpnq.left hp)
          (fun hq : q => hnpnq.right hq))

#print Not

example : ¬p ∨ ¬q → ¬(p ∧ q) := sorry
example : ¬(p ∧ ¬p) := sorry
example : p ∧ ¬q → ¬(p → q) := sorry
example : ¬p → (p → q) := sorry
example : (¬p ∨ q) → (p → q) := sorry
example : p ∨ False ↔ p := sorry
example : p ∧ False ↔ False := sorry
example : (p → q) → (¬q → ¬p) := sorry

open Classical

variable (p q r : Prop)

example : (p → q ∨ r) → ((p → q) ∨ (p → r)) := sorry
example : ¬(p ∧ q) → ¬p ∨ ¬q := sorry
example : ¬(p → q) → p ∧ ¬q := sorry
example : (p → q) → (¬p ∨ q) := sorry
example : (¬q → ¬p) → (p → q) := sorry
example : p ∨ ¬p := sorry
example : (((p → q) → p) → p) := sorry


end s7
