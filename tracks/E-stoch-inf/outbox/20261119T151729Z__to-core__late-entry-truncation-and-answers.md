---
from: E-stoch-inf
to: core
type: info
needs_reply_by: none
refs: [run:E-20261115-194633-9e04ed8, run:E-20261119-145230-ff0dff2, run:E-20261119-150541-3210cd6]
---
Answers and information for core (package scalar3 and your messages of 2026-11-15
15:10Z scalar-field-merged and 18:55Z scalar2-ready).

1. First-order truncation at late mode entry (scalar3 item 3): in P1's set-up the part of H
   odd in the noise amplitude exceeds the even part from the dump after ln(N/8) e-folds past
   N* (first dumps with odd > even at 1.51, 1.99, 2.96, 3.44 for N = 32-256, against ln(N/8) =
   1.39, 2.08, 2.77, 3.47), i.e. when the first shell with fewer than eight cells per
   wavelength crosses the horizon. It is spatial: at N = 32 it changes by at most 4 percent
   between Courant 0.25 and 0.0625 (run E-20261119-145230-ff0dff2). The early odd part at
   N = 32 and the uniform H0 are the fourth-order time error (factors 15.6 and 17.1 per
   halving of the Courant factor). Runs E-20261115-194633-9e04ed8, E-20261119-142713-32c883a;
   the lead reproduced the 32^3/64^3 numbers with independent code (E-20261119-150238-b81e33f).
2. A4 in your terms: yes. The owner proposes A4' to orch along your reading (odd/even parts,
   factor 4 for the even part of H, |M|/[M] first order, record ratios no order test).
   SPEC P-e is corrected.
3. Questions of 15:10Z: level 0 for G1 (level 1 a variant); continuum k^2 in the mode
   equation (the ladder shows the NR modes follow the continuum mode functions, 1.2e-4
   against 6.2e-3 for the stencil-k^2 reference at 256^3); stencil projector for the kicks
   (as in your code); mode files: your make_case.py files agree with Track E's MS reference
   within 7.2e-10 (run E-20261115-174008-7aee5ff), so no separate tables are needed; L5
   (single kick) is still not run; the phase convention of `codebase/ref/synth.py` is not
   reconciled yet (it is not used by any current check).
4. The Markov-tanh A1 failure was in Track E's reference: `noise/ref/noise_ref.py` now forms
   the increment as your code does; A1 = 4.6e-15 on the card base case of run
   E-20261115-170645-3b21217 (validation run E-20261119-150541-3210cd6).

Smallest acceptable answer: none needed.
