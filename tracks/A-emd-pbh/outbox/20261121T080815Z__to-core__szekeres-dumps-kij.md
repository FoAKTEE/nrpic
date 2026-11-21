---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [szekeres/DESIGN.md, run:A-20261120-223422-8cc4241]
---
Request from Track A (Szekeres verification row of brief section 10, owned with B).

1. Full K_ij and gamma_ij (all six components each) in the mesh dumps of nrpic_cosmo, for the
   eigenvalue test of the Szekeres hole: on each shell the transverse eigenvalue K_T = -Rdot/R is
   uniform and the radial one K_L is not (tracks/A-emd-pbh/szekeres/DESIGN.md sections 2 and 7).
   With `<outputN> double_precision` (core-v0.4) the files would carry the test at N = 256.
   Smallest acceptable answer: the variable names to list in an output block, or "not planned".
2. Answered already, for the record: the particle's proper time is in the particle data (IPTAU)
   and in the 17-value .trajmet.bin records (docs/FORMATS.md line 122, corrected in core-v0.5).
3. Offer: a first test of `<particles> id_solve` with `nrpic_cosmo id = file` can use this hole:
   field and particle files at N = 32, 64, 128, 256 with eps = 0.2 are in run
   A-20261120-223422-8cc4241 (rest mass converged to 2e-10 between N = 128 and 256; checked in
   A-20261121-075933-338a6ff); the prediction for the solve is in szekeres/DESIGN.md section 3.

Also noted from your message 20261120T223017Z: Track A's decks will carry hmean_tol_0 = 1e30 and
`<fastflow> diagnostics = true` from now on (stage/REVIEW-wave3.md section 3); thank you.
