# Evidence for G1 of B-emd-gw

Every run is registered under `tracks/B-emd-gw/runs/<run id>/manifest.json`, outputs under
`scratch/B-emd-gw/<run id>/`. Wave-1 evidence is listed in `stage/G0/EVIDENCE.md`; this
file lists what G1 rests on, wave 1 and wave 2.

## Criterion 1 (diagnostics on linear waves)

| What | Files | Runs |
|---|---|---|
| gw_diag on analytic fields (TT, energy, helicity, Psi_4, E, B) | `gw_diag/`, 14 tests | B-emd-gw-20261115-115206-2e6c497, -115637-175cbca |
| gw_diag on AthenaK vacuum output (wave along x) | `gw_diag/figs/athenak_psi4.png` | -113218-0ea0f74, -120128-7dfaa38 |
| periodic Z4c record (linear wave, gauge wave, lapse and shift) | `periodic_z4c/tables/*.md` | wave-1 runs of periodic_z4c |
| verifier: own waves, own runs of the release executable | `stage/G0/VERIFIER.md` C6, C7 | B-20261115-165056-835fddf, -170546-4507b05, -170431-c49964c |
| oblique wave after core's fix (core's evidence) | core message 20261115T1850Z; `tracks/core/interfaces/REQUESTS_B.md` on core/requests-b | core's card test T4 |

## Criterion 2 (Newtonian baseline)

| What | Files | Runs |
|---|---|---|
| Zel'dovich and ellipsoid baseline, scaling exponents | `baseline/BASELINE.md`, `baseline/results/` | B-emd-gw-20261115-115752-840e994 |
| verifier, scaling at emission | `stage/G0/VERIFIER.md` C8 | B-20261115-170518-c1b61a3 |
| AthenaK Newtonian mode: pancake P1, P2, H1 | `newton_tests/results/pancake.json`, `figs/pancake_*.png` | B-20261115-163556-ad5637f, -163558-20244f2, -165349-81a17bc, -165351-b38db6f, -163629-a96748c, -163653-f6324ea (card, 0.089 card-h); analysis -173904-a7297e3 |
| AthenaK Newtonian mode: ellipsoid N1, N3 | `newton_tests/results/ellipsoid.json`, `figs/ell_*.png` | B-20261115-163613-790095f, -163615-7bc8b30, -163617-085c093, -163618-ea94065, -163620-5b286c1, -163621-0ae44f1; analysis -174405-af11300 |
| lead's recheck | `stage/REVIEW-wave2.md`, `stage/review_wave2/figs/rv_review_newton.png` | B-20261115-190015-4dd3416, -190433-2d1d185 |

## Baseline data, pipeline validation and the first source

| What | Files | Runs |
|---|---|---|
| initial data of the scan (64^3, 32^3) | `first_source/scripts/build_ic.sh` | B-20261115-161656-03d75e1 (killed, three cases used), -164104-886798f, -165357-37d0477 |
| card scan 64^3 (0.43 card-h) | `first_source/inputs/crossed.athinput`, `batch*.list` | B-20261115-164059-d802e82, -165353-b592d43 |
| processor scan 32^3 | `first_source/scripts/run_cpu_scan.sh` | B-20261115-165525-f7c2004 |
| gauge piece G_tot, T0, tests | `first_source/fslib/gauge.py`, `tests/test_gauge.py`, `figs/t0_gauge.png` | B-20261115-164221-6a6b779 |
| reference s g(tau) | `first_source/results/reference.json` | B-20261115-164157-40b9f6d |
| scan analyses and figures | `first_source/results/scan_summary_{64,32}.json`, `figs/scan_*.png`, `res_compare.png` | B-20261115-174722-ba1048d, -180834-c77a132, -181552-8640a38, -184650-2d155b6, -184817-aefdbbc, -184814-fe015de |
| late rise of the wave-1 dumps, slicing checks | `first_source/results/late_rise_summary.json`, `slicing_*.json`, `figs/late_rise.png`, `slicing_*.png` | B-20261115-164616-a6d9477, -171804-42e975b, -170610-c82b10c, -170728-757e581 |
| lead's recheck | `stage/review_wave2/results/`, `figs/rv_review_first_source.png` | B-20261115-190007-e09a0d2, -190019-b5f5eb6, -190433-2d1d185 |

## Interface proposals and answers

Outbox of wave 1 (`outbox/20261115T1340Z__*`, 14 messages) and of wave 2 (this session);
core's answers to the eight requests to core: message 20261115T1620Z and
`tracks/core/interfaces/REQUESTS_B.md` (branch core/requests-b): generator fix, double
precision bin output, Weyl timing, thin boxes, jitter, TT initial data deferred, Newtonian
history later, AwA generators not in this release.

## Budget

Card-hours: 0.51 at gate G1 (wave 2) + 0.481 of wave 1 without a gate = 0.99 of 40.
