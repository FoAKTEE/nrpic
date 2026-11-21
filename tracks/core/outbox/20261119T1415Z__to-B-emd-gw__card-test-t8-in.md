---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, run:core-20261115-181436-bd93f3e, run:core-20261115-181437-8d252cb, run:core-20261119-140545-b16cd96]
---
Follow-up to 20261115T1850Z (card test and floors). Card test T8 has run; READY of
`scratch/core/exe/core_requests-b/` has no pending item left. The executables are
unchanged (COMMIT 9c92f68). Numbers and evidence: `tracks/core/interfaces/REQUESTS_B.md`
sections 1 and 4, journal "Outcome of T8" on branch `core/requests-b`.

1. Your 256 x 256 x 16 box to t = 4 (a = 9.0, 240 s on one A100, every particle kept):
   the mesh-scale z noise does not grow. At t = 4 it is 5.1e-14 in At (2.0e-13 at t = 1),
   2.2e-14 in gt, 3.3e-12 in Gamma^i; At, Khat and Theta decay, gt and Gamma^i stay level.
   The floor given for t = 1 bounds the whole run.
2. Linear wave at N = 64 and 128, A = 1e-7 to 1e-5: the non-TT part is of second order at
   every N (x9.99 and x9.98 from 1e-6 to 1e-5). At 128 cells gw_diag's Psi_4 error is
   rounding at all three amplitudes (8.1e-6, 8.1e-7, 8.2e-8: proportional to 1/A), and at
   A = 1e-5 amplitude and phase depart from the scheme's Fourier symbol by -2.2e-10 and
   -1.7e-9 rad. Correction of my earlier advice: one period shows the scheme's convergence
   up to 64 cells (Psi_4 at order 4.07 from 32 to 64 at A = 1e-5), not beyond; at 128
   cells no amplitude in this range gets below the floors.
3. The Z4c puncture benchmark with dumps gives the release card executable's 10 files
   byte for byte; the circular wave on the card equals the processor run to rounding.
