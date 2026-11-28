# C-sidm G2: evidence (artefacts and run ids), final state

Rewritten in batch 35 (2026-11-28 UTC) after the gate was signed (coord/GATES.md, 2026-11-27,
pass with reservations). The state of 2026-11-24 (runs "queued", "running") is in git history
(`git log -- tracks/C-sidm/stage/G2/EVIDENCE.md`). Paths relative to the worktree root
`wt/C-sidm`; manifests `tracks/C-sidm/runs/<run_id>/manifest.json`; outputs
`scratch/C-sidm/<run_id>/` (untracked) with `sha256sums.txt`. How to redo every number:
`RERUN.md`. Predictions of every card run: `tracks/C-sidm/JOURNAL.md` entries 2026-11-21T20:25Z,
2026-11-24T13:14Z, 2026-11-25T16:02Z (B20.1-B20.3), outcomes in the entries after them.
Executable of every threshold and collisional run: release core-v0.6 card build
(`.work/build_gpu_v06/src/athena`, sha256 ea473498500f...), cfl_number 0.25, no dt_gauge.

## Collisionless threshold of the King family b = 1 (C2, C7, C9)

| Label | Run id | y0, kick | N | Mesh, shift_eta | Fate (alpha_min = 0.3 marker) |
|---|---|---|---|---|---|
| N4c | C-20261125-132112-edf3fbc | 0.334032, none | 1e4 | M/8, 2 | 295.78 M |
| A334s1c | C-20261121-214601-40dc927 | 0.334032, none | 1e5 | M/8, 2 | 534.81 M |
| N6c | C-20261124-221122-928c9eb | 0.334032, none | 1e6 | M/8, 2 | holds 600 M |
| A344s1i | C-20261122-220118-ab099ac | 0.344, in | 1e5 | M/8, 2 | 229.79 M |
| A324s1i | C-20261123-221955-a773578 | 0.324, in | 1e5 | M/8, 2 | holds 600 M |
| N6b344 | C-20261125-224959-d1d4494 | 0.344, in | 1e6 | M/8, 2 | 252.31 M |
| N6b324 | C-20261126-020831-fabf2d7 | 0.324, in | 1e6 | M/8, 2 | holds 600 M |
| A16b344 | C-20261126-043714-8ea1c35 | 0.344, in | 1e6 | M/16, 2 | 217.97 M |
| A16b324 | C-20261126-121449-1d37e77 | 0.324, in | 1e6 | M/16, 2 | holds 600 M |
| N6b344e1 | C-20261126-050124-00e10ae | 0.344, in | 1e6 | M/8, 1 | 252.41 M |
| N6b324e1 | C-20261126-130519-1a79a66 | 0.324, in | 1e6 | M/8, 1 | holds 600 M |

Readers: nseries.py analyses C-20261126-120656-f5c62bb (N-series), -121836-c7a76c1 (bracket),
-124143-b485eac and C-20261127-084538-8e98060 (mesh leg), C-20261126-123219-f734997 and
C-20261127-084417-79c0e4d (gauge leg); horizon status of every collapse time
C-20261125-160207-05b6db1 (no run had the horizon finder). Second readers: the verifier
(C-20261127-090942-697c4b3; equilibrium sequence C-20261127-090849-dcfc1ae, y_max 0.3340322)
and the gate reviewer (C-20261127-232854-8859b86), each reproducing every crossing to 0.05 M.
Literature value: first maximum of the binding energy, King y_max = 0.334
(kb-data/raw/arxiv/2009.08163/v1/src/paper.tex:952-958) [VERIFIED].

## Collisional series CC2 at Kn_c = 10 (C1, C4, C8)

| Label | Run id | Mesh, collision cell, gauge | t_c (marker) |
|---|---|---|---|
| M4s1, M4s2 | C-20261120-221846-797bdbe | M/4, M/4, eta 2 | 206.556, 206.728 M (M4s2 broken after its first excision) |
| D2f2s1, D2f2s2 | C-20261122-141414-399ad97, C-20261124-035054-c06503f | M/8, M/4 | 163.41, 165.65 M |
| D2f1s1, D2f4s1 | C-20261122-144455-6e0992e, -181011-60baef9 | M/8, M/8 and M/2 | 164.01, 165.97 M |
| M16 | C-20261125-044843-2d048b6 | M/16, M/4 | 158.42 M |
| D2eta1 | C-20261126-034500-4b34b1c | M/8, M/4, eta 1 | 164.01 M (failed run: guard stop at 190.375 M) |
| D2ctl | C-20261122-103854-4670b59 | M/8, no collisions | none in 300 M |

Readers: d2_analysis.py C-20261126-121702-b6b1eda (budgets: collision energy below 3.2e-16 of
sum M H to the first excision, momentum below 4e-19, rest mass exact); count test per member and
window in CHECKLIST C8 (VERIFIER.md section 4, C-20261127-090913-97ee992).

## Conductivity (G1 reservation 1)

| Item | Run id | State |
|---|---|---|
| heat_C1, heat_C2 (core-v0.6) | C-20261121-210524-36a658e, C-20261122-183030-2f3a471 | completed; intermediate snapshots deleted by the reduction (OPEN.md) |
| reductions, series | C-20261124-130338-43b5ffa, -130338-c4ac85e; C-20261124-131012-f920f45 | kappa/kappa_1 = 1.020 +- 0.004 (one seed per point, no second check) |
| heat_C1r, heat_C2r (core-v0.8) | queue q0092, q0093 (priority 2) | queued 2026-11-28; predictions HR.0-HR.5 (JOURNAL 2026-11-28T01:59Z) |

## Block A at N = 1e5 (15 runs; unfit for the scan, kept on record)

blockA_delta.py C-20261125-160056-a5b7282 over the fifteen runs listed in its manifest; the
controls decay by finite N (A.4 failed; BA.3 held).

## Package documents

CHECKLIST.md (20 of 20 PASS), OPEN.md, RERUN.md, VERIFY_RESULTS.{md,json} (full pass
2026-11-27T10:40Z), VERIFIER.md (copy of verifier/VERIFIER.md), GATE_REVIEW.md, STAGE_REPORT.md;
note `tracks/C-sidm/note/main.pdf` Sec. V, Figs. 10-12, Table VI (figures of run
C-20261127-084828-b6ca5ce); scope `tracks/C-sidm/scope/SCOPE.md` (G2 clause amended 2026-11-27)
and `scope/SCOPE_G3.md`.
