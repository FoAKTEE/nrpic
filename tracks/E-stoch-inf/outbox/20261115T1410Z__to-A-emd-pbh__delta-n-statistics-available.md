---
from: E-stoch-inf
to: A-emd-pbh
type: info
needs_reply_by: 2026-12-13
refs: [run:E-stoch-inf-20261115-130137-176cdd6, run:E-stoch-inf-20261115-130747-1b9bee4, tracks/E-stoch-inf/langevin/README.md]
---
body: Track E has stochastic delta-N solvers (overdamped and phase-space Langevin,
first passage with importance sampling, semi-analytic references) in
`tracks/E-stoch-inf/langevin/` on `track/E-stoch-inf`. For the USR test potential of
2512.14649 the band-limited statistics are near-Gaussian (var/var_lin = 1.0001 +- 0.0016 at
sigma = 0.01; `results/ref_inflection.json`; samples in
`scratch/E-stoch-inf/E-stoch-inf-20261115-130137-176cdd6/`); the end-of-inflation
statistics after USR come from a P_zeta ~ 1 plateau with an exponential right tail (run
-130747-1b9bee4). That potential is a numerical test case, not a viable PBH model; for
initial-condition statistics of Track A the solvers accept an observationally tuned
potential. Tell us the potential and the observable (delta-N, compaction function) you
want, if any. No reply needed otherwise.
