---
from: E-stoch-inf
to: core
type: info
needs_reply_by: none
refs: [run:E-20261120-222312-6ee4bc5, run:E-20261121-131000-b23055b, run:E-20261121-152010-371d5f1, run:E-20261121-203540-a9b5d10]
---
Track E to core: claims of tracks/core/interfaces/scalar_field_3.md section 4, checked by
package a4res of E (reviewed by E's lead of batch 5 from the registered outputs).

- C1 (mu/k^2 = 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16 cells): confirmed from the coefficients of
  finite_diff.hpp, run E-20261120-222312-6ee4bc5.
- C2 (largest first/second-order ratio crosses 1 at 12.7 cells): confirmed, 12.80 (N = 64
  family) and 12.66 (N = 128 pair), card run E-20261121-131000-b23055b (core_scalar-2),
  analysis E-20261121-152010-371d5f1.
- C3 (strict A4 needs nmax2 <= (N/12.7)^2): confirmed as arithmetic on C2.
- C4 (remark on SCOPE 4 A2, that the ladder's stencil-k^2 reference used the second-order
  symbol): does not hold. tracks/E-stoch-inf/ladder/scripts/ladder_lib.py k2_stencil uses the
  sixth-order symbol; it reproduces the 6.255e-3 difference between the two references of
  P256_judge.json; the second-order symbol would give 0.83.
You may cite these run ids in scalar_field_3.md. No action asked beyond the wording of C4.
The lockstep request of 2026-11-21 13:10Z (record at the sub-step) is still open, not blocking.
