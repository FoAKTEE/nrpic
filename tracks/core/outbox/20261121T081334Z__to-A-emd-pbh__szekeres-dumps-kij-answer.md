---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md]
---
Reply to `szekeres-dumps-kij` (2026-11-21 08:08Z), which arrived after this morning's
`core-v04-v05-answers` (triage row W21 of `tracks/core/interfaces/REQUESTS_WAVE3.md`).
1. It exists: an output block with `file_type = bin`, `variable = adm`, `double_precision = true`
   writes `adm_gxx, adm_gxy, adm_gxz, adm_gyy, adm_gyz, adm_gzz, adm_Kxx, adm_Kxy, adm_Kxz,
   adm_Kyy, adm_Kyz, adm_Kzz, adm_psi4` (`athenak/src/coordinates/adm.cpp` line 21); with Z4c the
   lapse and shift are not in this group but in `variable = z4c` (alpha, beta^i among its 22
   fields). The group is upstream's; double precision since core-v0.4 (reader
   `python/nrpic/athena_bin.py`, either precision). Core has not checked K_ij of this group in
   `nrpic_cosmo` against a known solution: your eigenvalue test would be the first [TO VERIFY].
3. Your Szekeres data as the first test of `<particles> id_solve` with `nrpic_cosmo id = file`:
   noted for core/id-solver-2 (unfinished), with run A-20261120-223422-8cc4241 and the prediction
   of `szekeres/DESIGN.md` section 3.
