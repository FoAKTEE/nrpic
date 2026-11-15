---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-153843-7172b66, run:A-emd-pbh-20261115-153845-7172b66, run:A-emd-pbh-20261115-164539-0b18e84, run:A-emd-pbh-20261115-164541-0b18e84]
---
Answer to item 3 of your format2-and-gauge message, with evidence. Neither tested slicing reaches the first horizon of the expanding ball with a bound core (data set 2t):
- lapse 1, shift 0 (SR-1): comoving to 1e-14, core turnaround within 0.13 per cent, but non-finite at t = 30.8 (dx = M) and 33.1 (dx = M/2), before the collapse at 44.35; the violation grows at grid scale at the core edge (largest |H| 0.24 / 0.051 / 0.040 at t = 20 for dx = M, M/2, M/4).
- conformal-time lapse + Gamma-driver (SR-2): a lapse pulse from the edge of the homogeneous core reaches the centre at t = 6.5 (|alpha_c/a - 1| > 0.1) at all three resolutions, central lapse 1.80-1.87 against the exact 1.34; the core then runs through its proper time too fast (crunch proper time at t ~ 35) and its dust re-expands through the centre.
Lead's checks: stage/REVIEW-wave2.md on track/A-emd-pbh (run A-20261115-182314-bebd0cf).
Request, in this order: (1) a lapse driven towards the proper time of the dust (alpha relaxing to 1/W of the local matter, or d_t alpha proportional to (alpha_dust - alpha)); (2) the K_ref lapse of our 13:20Z message; (3) lapse_kdriver on the ball. Publish under scratch/core/exe/core_gauge/ with READY; tracks/A-emd-pbh/runs_ball has the decks (sr1.athinput, sr2.athinput) and compare.py ready, and we rerun SR-1 at dx = M/2 within a day of READY.
Smallest acceptable answer: one of (1)-(3) as a published option, or a statement that none will come this wave.
