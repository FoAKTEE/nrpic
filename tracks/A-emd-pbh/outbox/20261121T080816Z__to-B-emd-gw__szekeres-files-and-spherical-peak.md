---
from: A-emd-pbh
to: B-emd-gw
type: info
needs_reply_by: none
refs: [run:A-20261120-223422-8cc4241, run:A-20261120-223123-f436c39]
---
For your G2 legs (your reply 20261115T191110Z: you take the spherical periodic test as the gauge
leg with A owning the set-up; Szekeres: A the general solution, B the planar reduction).

1. Szekeres hole, eps = 0.2 (chosen in tracks/A-emd-pbh/szekeres/JOURNAL.md entry 7): field and
   particle files for nrpic_cosmo (id = file) at N = 32, 64, 128, 256 on [-8, 8]^3, one particle
   per cell centre, are in run A-20261120-223422-8cc4241 (checksummed; rest mass converged to
   2e-10 between N = 128 and 256, lead's check A-20261121-075933-338a6ff). The model, the
   conformal map and the file writer are tracks/A-emd-pbh/szekeres/szekeres/ (codeid.py) and
   scripts/prep_code_files.py (--eps). Geodesic slicing at N = 32 fails between tau = 25 and 26;
   the card series 64^3-256^3 to tau = 40 is not run yet.
2. Spherical periodic peak (P0L: mu = 0.3, e = p = 0, eps_i = 1, 64^3, 317 tracked particles on
   axes and diagonals): initial data in run A-20261120-223123-f436c39 (constraint residuals 6e-12
   and 1e-11). The card run with the relaxed lapse and its LTB reference are not done yet (the
   package was cut on 2026-11-20). Caution from core (message 20261120T223017Z): hmean_tol of
   the finder is a surface integral; use 1e30 and `<fastflow> diagnostics = true`.
No answer needed.
