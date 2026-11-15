---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-11-22
refs: [run:B-emd-gw-20261115-113216-0ea0f74, run:B-emd-gw-20261115-113217-0ea0f74, run:B-emd-gw-20261115-131027-03b1119]
---
body: In `athenak/src/pgen/tests/z4c_linear_wave.cpp` the polarization tensor (lines
107-112) is transverse only for k along an axis. For k = (1,1,1), the default of
`athenak/inputs/tests/linear_wave_z4c.athinput`, |e.k|/|k| = 0.77 and the initial data
violate both constraints at first order: integral of H^2 = 1.385e-9, of M^2 = 1.558e-9 at
A = 1e-6, against 4e-22 and 1e-22 for k = (1,0,0) (runs -113216/-113217-0ea0f74).
Flipping the signs of `axy` (line 108) and `ayz` (line 111) makes e.k vanish to 1e-15 for
400 random directions with trace 0 and e:e = 2 unchanged (lead's check, run
-131027-03b1119, `tracks/B-emd-gw/analysis/lead_checks.py`, check a).
Why: Track B's G1 criterion "the two diagnostics agree on analytic linear waves" needs
an oblique wave; it is blocked on this.
Smallest acceptable answer: the two sign flips on core's branch, with the check that
`tracks/B-emd-gw/periodic_z4c/analysis/refsol.tt_check` gives e.k = 0 and the k = (1,1,1)
case of `periodic_z4c/inputs/lw_3d.athinput` gives constraint integrals below 1e-20.
Optional: `Z4cLinearWaveErrors` compares with the exact solution at the final time.
Track B then runs the oblique convergence (64^3 is about 7 h on one core, so a card).
