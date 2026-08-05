/-
Copyright (c) 2026 @ys-math. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE-APACHE-2.0.
Authors: @ys-math
-/
import Math.Learn.MIL.C02Basics
import Math.Learn.TPiL.C02DependentTypeTheory
import Math.Learn.TPiL.C03PropositionsAndProofs

/-!
# Math

The root module. It imports every module in the library, which is what makes
`lake build` with no target build all of them.

**Maintained by hand.** A file with no import here still compiles in your editor
and is still invisible to `lake build`, so CI will call the repo green while the
file rots. Add the import in the same commit as the file.
-/
