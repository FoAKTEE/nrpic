# Evidence for G1 of B-emd-gw

Every run is registered under `tracks/B-emd-gw/runs/<run id>/manifest.json`, outputs under
`scratch/B-emd-gw/<run id>/`. Wave-1 evidence is listed in `stage/G0/EVIDENCE.md`; this
file lists what G1 rests on, waves 1, 2, 2b and 3 (updated by the lead, batch 2a, 2026-11-20).

## Criterion 1 (diagnostics on linear waves)

| What | Files | Runs |
|---|---|---|
| gw_diag on analytic fields (TT, energy, helicity, Psi_4, E, B) | `gw_diag/`, 14 tests | B-emd-gw-20261115-115206-2e6c497, -115637-175cbca |
| gw_diag on AthenaK vacuum output (wave along x) | `gw_diag/figs/athenak_psi4.png` | -113218-0ea0f74, -120128-7dfaa38 |
| periodic Z4c record (linear wave, gauge wave, lapse and shift) | `periodic_z4c/tables/*.md` | wave-1 runs of periodic_z4c |
| verifier: own waves, own runs of the release executable | `stage/G0/VERIFIER.md` C6, C7 | B-20261115-165056-835fddf, -170546-4507b05, -170431-c49964c |
| oblique wave after core's fix (core's evidence) | core message 20261115T1850Z; `tracks/core/interfaces/REQUESTS_B.md` on core/requests-b | core's card test T4 |
| test F: oblique flat wave k = 2 pi (1,1,1), elliptic, N = 16, 32, 48, 64 (core/requests-b executables, now core-v0.4) | `waves/inputs/flat_oblique.athinput`, `waves/README.md` | B-20261119-142016-ee73a03, B-20261119-142233-70d5043, B-20261119-142124-feb2daf (card, N = 64) |
| test X: tensor mode in the matter-era box, N = 16, 32, 48, 64 | `waves/inputs/expanding.athinput`, `waves/scripts/make_expanding_ic.py` | B-20261119-142021-8f4c441, B-20261119-142234-85da208 (wrapper exit 127 after a complete AthenaK run), B-20261119-142108-1e5add9 (data N = 64), B-20261119-142124-feb2daf |
| predictions before the runs; RK4()4[2S] predictor (H1); amplitude scan | `waves/JOURNAL.md`, `results/predict*.json`, `figs/predict_2s.png` | B-20261119-141844-2c5d622, B-20261119-153548-c7338f1, B-20261119-153637-02c822f, B-20261119-154708-89d00ea, B-20261119-154738-30faa29 |
| final analysis, both diagnostics, orders | `waves/results/final_results.json`, `figs/final_*.png` | B-20261119-164402-7438a99 (supersedes B-20261119-163932-5ce4298; failed: B-20261119-145125-51e9f8f) |
| rounding check of X plus at N = 64 (amplitude x10) | `waves/results/x10_*.json`, `figs/x10_check.png` | B-20261119-155747-e3c6a9b (data), B-20261119-155758-458cf17 (card), B-20261120-221708-d8eae03, B-20261120-222234-4e2435d |
| independent verifier (verifier3): own exact solutions, readers, TT, Weyl/Psi_4; verdicts per claim | `stage/G1/verifier3/VERIFIER.md`, `results/`, `figs/` | B-20261120-222342-8cda367, B-20261120-222822-e26afae, B-20261121-025826-80973e3, B-20261121-030121-58fe5dc, B-20261121-030542-b2e3eff, B-20261121-030848-59f89b5 (failed: B-20261120-222232-3d7d57e, B-20261121-025612-ed4a875, B-20261121-030110-52ae004) |
| lead's recheck: two readings compared, third reading of X at N = 64, cause of the plus-amplitude dispute | `stage/REVIEW-wave3.md`, `stage/review_wave3/` | B-20261121-063617-6183015, B-20261121-063835-826c461 |

## Criterion 2 (Newtonian baseline)

| What | Files | Runs |
|---|---|---|
| Zel'dovich and ellipsoid baseline, scaling exponents | `baseline/BASELINE.md`, `baseline/results/` | B-emd-gw-20261115-115752-840e994 |
| verifier, scaling at emission | `stage/G0/VERIFIER.md` C8 | B-20261115-170518-c1b61a3 |
| AthenaK Newtonian mode: pancake P1, P2, H1 | `newton_tests/results/pancake.json`, `figs/pancake_*.png` | B-20261115-163556-ad5637f, -163558-20244f2, -165349-81a17bc, -165351-b38db6f, -163629-a96748c, -163653-f6324ea (card, 0.089 card-h); analysis -173904-a7297e3 |
| AthenaK Newtonian mode: ellipsoid N1, N3 | `newton_tests/results/ellipsoid.json`, `figs/ell_*.png` | B-20261115-163613-790095f, -163615-7bc8b30, -163617-085c093, -163618-ea94065, -163620-5b286c1, -163621-0ae44f1; analysis -174405-af11300 |
| lead's recheck | `stage/REVIEW-wave2.md`, `stage/review_wave2/figs/rv_review_newton.png` | B-20261115-190015-4dd3416, -190433-2d1d185 |
| independent verifier (verifier2) of the Newtonian-mode runs: exact sheets, ellipsoid ODE | `stage/G1/VERIFIER.md`, `stage/G1/verifier2/` | B-20261119-142135-e582e09 |

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
| independent verifier (verifier2) of the wave-2 first-source runs: own derivation of s, own readers and reference | `stage/G1/VERIFIER.md`, `stage/G1/verifier2/` | B-20261119-140854-ec1f1c2, B-20261119-141219-b391580, B-20261119-142015-da5ad0f, B-20261119-142332-dd28d1d (supersedes B-20261119-141828-09cebfa, B-20261119-142111-139aa84; failed B-20261119-141813-91cfe8e; stopped B-20261119-141201-1433762) |
| second round (beyond the G1 criteria; G2 legs): jittered nulls, delta = 0.0025, run-to-run floor, parity | `first_source/JOURNAL.md` (P11-P16), `first_source/figs/conv_*.png`, `null_spectrum.png` | data B-20261119-141216-9c98929, B-20261119-141249-2af0df8, B-20261119-142727-02878d1, B-20261119-142733-932e595; card B-20261119-142833-19edd82; analyses B-20261119-155418-80d45af, B-20261119-160530-7bdcb45, B-20261119-160535-6714ac1, B-20261119-160607-ef83373, B-20261119-161519-6e0bc42, B-20261119-161523-b681b5f, B-20261119-161734-a3a1366, B-20261119-163027-f0d304f, B-20261119-163037-6553674, B-20261119-164017-cd1ba52 |
| spatial-gauge piece recomputed independently (verifier3 V4) | `stage/G1/verifier3/VERIFIER.md` section 5 | B-20261121-031220-8b9c4d7, B-20261121-031808-3ef8c39, B-20261121-031833-c0ec479 |

## Working note and schematics (items C10, C11, C16, C17)

| What | Files | Runs |
|---|---|---|
| note v1 (G1 sections, data-flow and architecture schematics) | `note/main.tex`, `note/JOURNAL.md` | B-20261119-142957-ae8b4e2 (supersedes B-20261119-142525-2a55af7) |
| note v2 (criterion 1, second round; 21 pages; figures and tables byte copies of the run) | `note/main.pdf`, `note/figures/`, `note/tables/` | B-20261120-223319-cc5320d (supersedes B-20261120-222732-13e3e41) |

## Population box (G3 design; not a G1 criterion, listed for completeness)

`population/DESIGN.md`, `population/README.md`; runs B-20261119-143828-0ef9b5b,
B-20261119-143832-85cbe25, B-20261119-145324-525e4fd, B-20261119-145715-b18561e,
B-20261119-144134-092e73f, B-20261119-154315-c55b30f, B-20261119-155621-68170ca
(stopped: B-20261119-143348-728c0e5, B-20261119-145328-4b3663f, B-20261119-153724-a6f1ab5,
B-20261119-154528-9306cb1; failed: B-20261119-143836-644f0a9).

## Runs of round 1 closed by the lead, not yet analysed (packages in progress)

B-20261120-222841-acfe21d, B-20261120-222849-3b921b7, B-20261120-222849-e5673dc (waves F2,
XS), B-20261120-222955-c8e16e3, B-20261120-223006-24448ac (flrw_conv, G2),
B-20261120-223236-e213594, B-20261120-223241-f1efd4f (first_source round 3). Failed:
B-20261120-223445-3686145 (shear smoke run, deck error recorded).

## Interface proposals and answers

Outbox of wave 1 (`outbox/20261115T1340Z__*`, 14 messages), of wave 2 and of wave 3 (`outbox/20261121T*`);
core's answers to the eight requests to core: message 20261115T1620Z and
`tracks/core/interfaces/REQUESTS_B.md` (branch core/requests-b): generator fix, double
precision bin output, Weyl timing, thin boxes, jitter, TT initial data deferred, Newtonian
history later, AwA generators not in this release.

## Budget

Card-hours (`nrpic-run budget`, 2026-11-20 23:00 PST): 1.69 at gate G1, 0.31 at gate G2, 0.48 of
wave 1 without a gate: 2.48 in all (sacct: 2.48), of 40 allotted to the next gate.

Release core-v0.4 (tag on f9323185, merged into main 2026-11-21) carries the corrected
oblique generator, the double-precision bin output and the jitter tool that criterion 1 and
the second round used from the tested branch core/requests-b (decision 0013).
