---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:B-emd-gw-20261115-120128-7dfaa38, run:B-emd-gw-20261115-131016-03b1119, tracks/B-emd-gw/scope/SCOPE.md]
---
body: Track B's GW analysis needs the Z4c state of periodic cosmology runs at a cadence
of a conformal-time step 0.1 or finer. Today the restart file is the only full-mesh
double-precision output; `.bin` is float32 and keeps about one digit of h ~ 1e-6 on the
diagonal (gw_diag README). A full Z4c dump is about 42 MB at 64^3 and 340 MB at 128^3;
200 dumps per run are 8 to 67 GB (scope, risk 7).
Requests, in order of preference:
1. An optional double-precision binary output of the Z4c variables (gt_ij, At_ij, chi,
   Khat, alpha) without ghost zones, usable at the GW cadence; or confirmation that
   restart files at that cadence are the intended route.
2. Optional, to cut volume: an in-situ output of the Fourier modes of gamma_ij and K_ij
   at the box wave vectors |n| <= 4, every few cycles (uniform periodic meshes only).
3. Optional: S_ij (and E, S_i) of `tmunu` in a double-precision dump, so that the
   electric Weyl part can include the matter term.
Information: restart files are not byte-reproducible: two runs of the same input differ
in 36 bytes at offsets 8794-8829 of `lw3.0000N.rst` (a region after the parameter block
holding leftover input-file text, i.e. an uninitialised buffer), with identical field data
(lead's re-execution, run -131016-03b1119, `compare.json`). Checksum-based verification
(`nrpic-stage verify`) of .rst outputs will fail spuriously until that buffer is zeroed.
Smallest acceptable answer: item 1 or the confirmation; a note on the padding.
