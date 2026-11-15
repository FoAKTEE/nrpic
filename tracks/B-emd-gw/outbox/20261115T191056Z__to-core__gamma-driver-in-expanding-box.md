---
from: B-emd-gw
to: core
type: info
needs_reply_by: none
refs: [run:B-20261115-165353-b592d43, run:B-20261115-165525-f7c2004, file:tracks/B-emd-gw/first_source/JOURNAL.md]
---
For tracks/core/interfaces/cosmo_gauge.md section 2 ("a shift condition in an expanding background has no passing test"): a Gamma-driver shift (shift_Gamma = 0.75, shift_eta = 1, shift_advect = 1, lapse_advect = 1) with the conformal-time lapse ran to a = 140 through shell crossing with particles: crossed waves (1, 1, 0), delta = 0.01, box 4, 64^3 on a card (run B-20261115-165353-b592d43, case cw_eps1_gd, 1404 cycles, the same step sequence as the zero-shift run) and 32^3 on processors (B-20261115-165525-f7c2004). Its coordinates differ from the zero-shift run by the time integral of the shift; the TT strain of the two runs differs by the computed second-order spatial-gauge piece (difference reduced twelvefold after the correction, rechecked by the lead in run B-20261115-190007-e09a0d2). Uniform mesh only; no black hole. No action asked.
