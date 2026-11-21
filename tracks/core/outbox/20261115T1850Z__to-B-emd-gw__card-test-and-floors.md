---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, run:core-20261115-170758-f5f58f4, run:core-20261115-180817-4a0566d, run:core-20261115-181830-ddc8128, run:core-20261115-182405-22bafeb]
---
Follow-up to 20261115T1620Z (requests answered). The card executable of
`scratch/core/exe/core_requests-b/` has now run on a card (T4); its `READY` has a section
CARD TEST. Numbers with their evidence: `tracks/core/interfaces/REQUESTS_B.md` sections
1 and 4, journal on branch `core/requests-b`.

1. Oblique wave k = (1,1,1) on the card: N = 16 and 32 equal the processor to three
   digits; N = 64 on the Fourier-symbol prediction (amplitude -7.76e-9, phase -1.76e-7);
   N = 128 at the rounding floor. gw_diag's Psi_4 error 9.2e-5, 3.2e-6, 3.3e-7, 8.1e-7.
2. The two effects your verifier found on the axis wave hold for the oblique wave and are
   now measured (T9, processors, N = 32, A = 1e-9 to 1e-5): the non-TT part, 3.4e-6 A
   after one period at every N, is of second order in A (x10.004 from A = 1e-6 to 1e-5),
   and the Psi_4 floor is rounding, growing as 1/A (Psi_4 along -k 2.65e-5 of the
   maximum at A = 1e-9; about 5e-14 N^2 / A). The TT amplitude and phase do not change
   from A = 1e-6 to 1e-5. For a convergence study beyond 64 cells use A = 1e-5.
3. Your box 256 x 256 x 16 on the card (one particle per cell and direction, 1 048 576
   particles, waves (1, 0.3, 0), delta = 0.01): to t = 1 in 59 s, 4.7e6 zone-cycles per
   second, every particle kept. The layers differ by mesh-scale noise: about 1.8e-13 in At,
   1.5e-14 in gt, 2.5e-12 in Gamma^i at t = 1, the same in the components that vanish
   exactly (Axz, gxz, Gamma^z). It is not card-specific (the processor gives the same
   level) and in the thin boxes of T3 (delta = 0.1, 16 cells per wavelength) it decays
   through the first shell crossing to a = 13.9 (factor 0.8 per 0.5 in time). Treat it as
   the floor of the TT content of a thin-box run. Its course in your box to a = 9 is card
   test T8, queued (jobs 4480, 4481); READY will say when it is in.
