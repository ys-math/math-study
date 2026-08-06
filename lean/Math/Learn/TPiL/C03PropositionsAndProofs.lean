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
