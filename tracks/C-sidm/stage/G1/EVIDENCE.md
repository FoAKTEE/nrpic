# C-sidm G1: evidence (artefacts and run ids)

Paths relative to the worktree root `wt/C-sidm`. Manifests `tracks/C-sidm/runs/<run_id>/`;
outputs `scratch/C-sidm/<run_id>/` (untracked). Wave-1 evidence (baseline, specifications,
T0): `../G0/EVIDENCE.md`. Executables: release core-v0.3 of the main checkout
(`.work/build_cpu_v03`, `.work/build_gpu_v03`).

## Collision operator (C-pre-1) on core-v0.3: box tests of `collide/TESTS.md`

| Test | Verdict | Run ids | Lead recheck (run C-20261115-193332-48771b4) |
|---|---|---|---|
| T0 kernels | PASS (wave 1) | C-sidm-20261115-132624-13a77db | - |
| T0b replay of one step | PASS 6/6 dumps | C-20261115-170155-13ff01f | helper's replay rerun: same numbers |
| T1 conservation | PASS (16 + 4 + 2 runs; 1e4 steps) | C-20261115-165500-c67e036, -170741-248af65 | max |dE|/sum MW 2.8e-19; exact sums bit-identical |
| T2 rate | PASS 16/16 | C-20261115-165500-c67e036 | ratio 0.999906-1.000096, z_b -2.20..+2.92, z_a -2.10..+1.58 |
| T3, T4, T5 | PASS 4/4 | C-20261115-170539-28432c3 | T4 0.9924, 0.9792, 0.9959, 1.0088 (window-edge sensitivity 0.5-1.4 se); KS p 0.084-0.987 |
| T6, T7, T8 heat conduction | NOT RUN | - | - |
| T9 unequal masses | PASS (8 seeds) | C-20261115-170814-8a54b43 | |z| <= 1.16; mean energy drift z = 2.42 |
| T10 reproducibility | PASS (no MPI variant) | C-20261115-165902-f9b1c8f | byte-identical records |
| T10b processor vs card | PASS for T2 statistics | C-20261115-170447-cb3b230 (card, 0.014 h), C-20261115-180525-94ddd22 | not recomputed |
| T11 Lorentz covariance | PASS (a, b, c) | C-20261115-171719-7daad65, C-20261115-174651-0ad8612 | counts z = +0.52, -0.21, -1.78, -0.15 |
| Diagnostics D1, D2 | done | C-20261115-180041-f00f777, C-20261115-180434-fd05776 | not recomputed |
| Cost per tested pair | 3.4-3.9e-9 s (A100), 3.3-6.7e-7 s (one core) | C-20261115-180525-94ddd22, C-20261115-165500-c67e036 | processor values recomputed |

Package: `tracks/C-sidm/box_tests/` (README, JOURNAL with predictions, scripts, figs, results).

## Baseline and initial data (C-pre-3, C-pre-4)

| Item | Run ids | Artefacts |
|---|---|---|
| F21 tables, criteria, exact onsets | C-sidm-20261115-120722-38ab057 (wave 1); verifier C-20261115-170630-1037f6a | `gravothermal/`, `../G0/VERIFIER.md` |
| Juttner fluid onset (five indices, b = 0.1-0.5) | C-20261115-165315-7b473b8; recheck C-20261115-193332-48771b4 | `models/results/fluid_onset.json`, `models/figs/fig_fluid_onset.png` |
| Particle models, 5 King + 8 F21 b = 0.1, N = 1e4 and 1e5 | C-20261115-170126-b4f74af, C-20261115-170742-84990ed; checks C-20261115-170221-b1a491c, -171137-9e3c807 (exit 1, see C1), -171723-17d46f0 | `models/` |
| AthenaK reads the F21 b = 0.1 eps-maximum model at 1e5 | C-20261115-174557-8978b36 | `models/figs/fig_smoke.png` |
| K = 1/(rho0_c H_c) for the 13 models | C-20261115-193751-d3872ff | `equilibria/CONVERSION.md` section 5 |
| King b = 1 files at 1e5 for the card runs | C-20261115-165832-fccee3a | `threshold_scan/` |

## Analysis pipeline

| Item | Run ids |
|---|---|
| growth.py: 18/18 published numbers; growth-rate fit G2 failed, D1 cause | C-20261115-170346-298a1ba, C-20261115-170713-cefe1c2 (failed attempt C-20261115-170231-4e68455 kept) |
| box analysis on the box tests | the box-test runs above |

## Beyond G1 (G2 scouting, on record here)

First collisional cluster runs CC1/CC2 at Kn = inf, 10, 1 (card, 1.73 card-hours): runs
C-20261115-171058-c26cfad, C-20261115-171059-4b70228, C-20261115-171059-35441e3, analysis
C-20261115-191420-8538aa4; histories rechecked by the lead (L10). Both King models collapse
with collisions (alpha_min < 0.3 at 72.5, 77.75 M for Kn = 1; 184.25, 206.75 M for Kn = 10)
and not without; rest-mass budget closes to 7.3e-15.

## Wave 2b (2026-11-19): collisions with the metric at each particle (core/collisions-2)

Executable: `scratch/core/exe/core_collisions-2/athena_cpu` (commit f46f159, scouting under
decision 0013); option `<particles> coll_energy = particle`. Package `tracks/C-sidm/box_tests/`
(README section "Wave 2b", JOURNAL predictions R1-R6 written before the runs). Lead's
recheck from the registered outputs: `../REVIEW-wave2.md` section 6 (L13).

| Test | Verdict | Run ids |
|---|---|---|
| R1 T0b, option absent (new executable) | PASS 6/6; every output file byte-identical to the release run C-20261115-170155-13ff01f | C-20261119-141502-95f0200 |
| R2 T0b, coll_energy = particle (version-2 dumps) | PASS 6/6; replay written from the cell-frame text; n_noroot = n_balance = 0 | C-20261119-141711-7db7a6a (failed first attempt C-20261119-141614-e42b5ec kept); mode comparison C-20261119-141854-b2b664d |
| R3 T1, T2 with the option | PASS 16/16 each; counts identical to the release in all 3200 steps | C-20261119-141806-af19c1c |
| R4 T10 with the option | PASS (MeshBlocks 1/8/64, restarts; 385554 collisions as the release) | C-20261119-143041-f94e350 |
| R5 T12 (G2 item) static homogeneous metric alpha0 = 0.8, psi0 = 1.1 | PASS: rate = alpha0 psi0^6 x flat twin with identical counts in every step; analytic ratio 0.99997-1.00009 | C-20261119-143049-0cf699a (driver failed on its figure after the JSON), analysis C-20261119-145925-dbcfb9c |
| R6 King threshold model, first step | cell mode: +8.0(3.4)e-11 of sum M W_p per collision (pair model 1.74e-10); particle mode: canonical energy +1.5-1.9e-21 M per collision | C-20261119-141431-a351ac7, figure C-20261119-142957-c5da7d0 |
| Cost | particle mode 1.68 x cell mode per tested pair (processor, equal load) | C-20261119-143146-226b0e0 |

Heat conduction T6-T8 (package `heat/`, wave-3a helper): in progress, see `OPEN.md` item 1.
