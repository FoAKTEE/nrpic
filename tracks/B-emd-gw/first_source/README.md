# first_source (helper package of B-emd-gw, waves 2 and 2b)

The first gravitational-wave source in full relativity (action 1 of `../HANDOFF.md` and
`../stage/G1/STATUS.md`): crossed waves with amplitude ratios (1, eps, 0), eps = 0, 0.1,
0.3, 1, at delta = 0.01 in the box of four initial Hubble radii, two particles per cell and
direction, conformal-time lapse and zero shift, to a = 140; a fifth run (eps = 1) in a
second spatial gauge (Gamma-driver shift, same slicing condition); analysis with
`../gw_diag`. And the open caveat of wave 1 (`../stage/G0/REVIEW.md` lines 98-102): is the
late rise of the flat TT part in the full-GR cosmology dumps a wave or a second-order gauge
effect? Predictions and outcomes, with run ids, in `JOURNAL.md`; the state of each item in
the section "State" below.

Second round (wave 2b, 2026-11-19; next action 2 of `../stage/REVIEW-wave2.md`): the
jittered-lattice null, convergence in particle number (1, 8, 27 per cell) and in the mesh
(128^3), and delta = 0.0025 to widen the window of the second-order formula; predictions
P11-P15 and outcomes in `JOURNAL.md` (section "Second round"), state in the section "State of
the second round" below.

## Contents

| Path | What |
|---|---|
| `inputs/crossed.athinput` | AthenaK input of the scan (production configuration of `cosmo/README.md`; z4c `bin` every 0.1, `rst` every 1.0, NRFIELD dumps at a = 2 ... 140) |
| `inputs/batch1.list`, `inputs/batch2.list` | card batch lists (eps = 0, 0.3, 0.1; eps = 1 in both gauges) |
| `scripts/build_ic.sh` | initial data with `cosmo/ic/make_east.py --ratios 1,eps,0 --ppc 2` (`N`, `CASES`, `THREADS`) |
| `scripts/run_cpu_scan.sh` | processor companion: the five cases at 32^3, one serial AthenaK each |
| `fslib/gauge.py` | spatial-gauge pieces of the flat TT projection: G (of h) and G_A (of tilde A), from the displacement xi recovered from the measured non-TT part; dealiased products |
| `fslib/modes.py` | per-dump diagnostics: amplitudes h_+, h_x at K1 = (k, k, 0), K2 = (k, -k, 0) (cos/sin parts), TT/non-TT rms, G, G_A, energies, null-test quantities, Weyl E, B for rst dumps |
| `fslib/reference.py` | second-order reference s g(tau), s = -(5/6) phi_x phi_y |
| `fslib/paths.py` | puts `../gw_diag` and `python/` on the path |
| `tests/test_gauge.py` | 5 tests of the gauge pieces on exact data (pytest) |
| `scripts/reference_run.py` | the reference curve and numbers |
| `scripts/t0_gauge.py` | T0: G on exact pure-gauge Minkowski data (slopes) |
| `scripts/late_rise.py` | P7/P7b: G, G_A, energies and spectra on the cosmology dumps |
| `scripts/slicing_check.py`, `scripts/slicing_products.py` | P9/P10: first-order slicing; size of the slicing products |
| `scripts/analyze_scan.py`, `scripts/plot_scan.py` | P1-P6: diagnostics of the scan runs, figures and `scan_summary.json` |
| `scripts/compare_res.py` | P8: 32^3 against 64^3 |
| `results/` | small JSON copies of the run outputs (summaries of the scan at 64^3 and 32^3, the reference, T0, the cosmology-dump checks) |
| `figs/` | PNG copies of the figures that were looked at |
| `JOURNAL.md` | predictions (written before each run) and outcomes |
| `inputs/conv.athinput` | second round: the input of the scan with other outputs (Z4c single precision every 0.1, double precision bin `z4cd` every 1.0, restart every 5.0) for the requests-b executable |
| `inputs/batch_r2a.list`, `inputs/batch_r2bc.list` | second-round card batches (A: rerun, jittered nulls, delta = 0.0025; BC: 1 and 27 per cell, 128^3); `batch_r2b.list`, `batch_r2c.list` are the same runs split in two jobs |
| `scripts/build_ic2.sh` | second-round initial data with make_east.py (`CASES` = name:delta:n:ppc:eps:threads) |
| `scripts/build_ic_jitter.sh` | jittered-lattice null with core's make_waves.py, extracted from core/requests-b at 7db34a5 (`CASES` = name:A:seed:threads, `N`) |
| `scripts/run_cpu_r2.sh` | processor companion of the second round at 32^3 (`name=<ic dir>` arguments) |
| `scripts/smoke_conv.sh` | 8-cycle processor test of `conv.athinput` (both precisions written and read) |
| `scripts/parity_check.py` | make_waves without jitter against make_east (P15) |
| `scripts/null_prediction.py` | P11b': box-mode TT amplitudes of the jittered null predicted from its initial data |
| `scripts/conv_compare.py` | outcomes of P11-P14 from the case JSON of analyze_scan.py: `conv_summary.json`, figures `conv_null`, `conv_eps1`, `conv_delta` |
| `fslib/binread.py`, `tests/test_binread.py` | reader of bin output in single and double precision (2 tests) |

## How to rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create --no-kokkos`);
every command is a registered run (`harness/bin/nrpic-run submit ... --package
tracks/B-emd-gw/first_source`; the scripts write to `$NRPIC_RUN_DIR` when no directory is
given; do not pass `'$NRPIC_RUN_DIR'` as an argument, nrpic-run does not expand it).

```
# tests (seconds)
.venv/bin/python -m pytest -q -p no:cacheprovider tracks/B-emd-gw/first_source/tests
# reference and T0 (seconds)
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/reference_run.py
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/t0_gauge.py
# initial data (64^3: 10-15 min per case, eps = 1 the slowest; never wrap in `timeout`)
nrpic-run submit --launcher local --background --cores 16 ... -- bash tracks/B-emd-gw/first_source/scripts/build_ic.sh
# cards: edit the initial-data paths in the batch lists, then
nrpic-run submit --launcher batch --wall 00:40:00 --list tracks/B-emd-gw/first_source/inputs/batch1.list ...
# processors at 32^3 (about 1.5 h on five cores)
nrpic-run submit --launcher local --background --cores 5 ... -- bash tracks/B-emd-gw/first_source/scripts/run_cpu_scan.sh <ic dir of N=32>
# analysis (NWORK processes)
nrpic-run submit --launcher local --cores 8 ... -- env NWORK=8 python3 tracks/B-emd-gw/first_source/scripts/analyze_scan.py <case dirs>
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/plot_scan.py <dir of the case JSON>
# the wave-1 caveat (28 dumps of 128^3, ~5 min on four processes)
nrpic-run submit --launcher local --cores 4 ... -- env NWORK=4 python3 tracks/B-emd-gw/first_source/scripts/late_rise.py runs/cosmo/dav_c256_n128_t runs/cosmo/dav_c256_n128_pcs4bt
```

Second round (from the worktree root, through nrpic-run with `--package
tracks/B-emd-gw/first_source`; the card executable is
`scratch/core/exe/core_requests-b/athena_gpu`, passed with `--exe`):

```
# initial data: delta 0.0025, 1 and 27 per cell, 128^3 (make_east; 27 per cell takes ~1.5 h on one core)
nrpic-run submit --launcher local --background --cores 7 ... -- env "CASES=..." bash tracks/B-emd-gw/first_source/scripts/build_ic2.sh
# jittered null (make_waves at 7db34a5; N=32 for the processor companion)
nrpic-run submit --launcher local --background --cores 6 ... -- bash tracks/B-emd-gw/first_source/scripts/build_ic_jitter.sh
# checks and the prediction of the null (seconds)
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/parity_check.py <jit0 dir> <make_east eps0 dir>
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/null_prediction.py <ic dirs>
# cards (edit the initial-data paths in the lists first)
nrpic-run submit --launcher batch --wall 00:45:00 --exe <requests-b athena_gpu> --list tracks/B-emd-gw/first_source/inputs/batch_r2a.list ...
nrpic-run submit --launcher batch --wall 00:59:00 --exe <requests-b athena_gpu> --list tracks/B-emd-gw/first_source/inputs/batch_r2bc.list ...
# processors at 32^3 (~3 h per case on a loaded machine)
nrpic-run submit --launcher local --background --cores 2 ... -- bash tracks/B-emd-gw/first_source/scripts/run_cpu_r2.sh jit0p3=<ic> jit0p1=<ic>
# analysis and outcomes
nrpic-run submit --launcher local --cores 8 ... -- env NWORK=8 python3 tracks/B-emd-gw/first_source/scripts/analyze_scan.py <case dirs>
nrpic-run submit --launcher local ... -- python3 tracks/B-emd-gw/first_source/scripts/conv_compare.py name=<case json> ... pred=<null_prediction.json>
```

## State (end of the package, 2026-11-15)

Established (numbers and run ids in `JOURNAL.md`; figures in `figs/`, looked at):

1. First GW source at 64^3 on the cards (runs B-20261115-164059-d802e82,
   B-20261115-165353-b592d43; 0.43 card-hours of the 1.5 allowed): the box-mode strain
   c_+(k, k, 0) follows the second-order Poisson-gauge value s g(tau), s = -(5/6) phi_x phi_y
   = -3.08e-5 eps, including the junk oscillation of the conformally flat start, to 0.22
   percent (eps = 0.1, 0.3) and 0.44 percent (eps = 1) for 2 <= a <= 10; linear in eps to
   0.05 percent; departures of 1-2 percent at a = 20, 6-11 at a = 40, and growth to 1.6-2.5
   times s after shell crossing (a ~ 80-140). The TT field stays quasi-static
   (rho_kin/rho_grad <= 0.04); rho_GW/rho_bar up to 3.5e-6 (eps = 1).
2. Null (eps = 0): TT amplitudes of h and tilde A at the round-off of the metric (<= 2.8e-16)
   through shell crossing; the relative criterion 1e-12 of the scope was mis-normalized and
   fails at the first dumps only because the traceless part is then small.
3. Gauge. `fslib/gauge.py` computes the spatial-gauge piece of the flat TT projection to
   second order, G_tot = G + cross terms (test T0 and `tests/`, 6 pass). A second spatial
   gauge (Gamma-driver shift, same slicing; the run reached a = 140) confirms it: the raw
   difference of c_+ between the gauges (0.4 percent of s at a = 10, 11 percent at a = 60)
   falls to 0.008 and 1.2 percent after G_tot; without the cross terms with the homogeneous
   anisotropy of the box the correction fails (found on the 32^3 companion, journal). The
   magnetic Weyl part agrees between the gauges where raw Lambda h does not.
4. Wave-1 caveat (late TT rise in the full-GR cosmology dumps, `stage/G0/REVIEW.md` lines
   98-102): NOT a second-order gauge effect. G_tot ~ 0.15 (rms non-TT)^2 is a tenth of the
   rise and sits at low k; slicing products are 1e-5 of it; the first-order slicing is
   Newtonian (P9). The rise lies at the grid scale (|k|L/2pi >= 20: 93-97 percent),
   depends on the deposit there by a factor 1.9 and is quasi-static (rho_kin/rho_grad ~
   0.02): unresolved small-scale structure or noise, an upper bound rho_GW/rho_bar < 3e-12
   (quadratic cloud) and < 1.3e-11 (cubic) at a = 1001; the resolved band below 20 grows by
   8-10 percent (k < 10) and twentyfold (10-20), deposit-independent.

Not done / open:
- The late growth of c_+ after shell crossing agrees between 32^3 (processor runs
  B-20261115-165525-f7c2004) and 64^3 to 0.5 percent up to a = 80 and 3 percent at a = 100
  (P8), but two meshes with one particle loading are not a convergence study: 128^3, more
  particles per cell and a jittered-lattice null are the next runs.
- G_tot removes the spatial gauge; the slicing gauge is bounded by a scaling argument with
  measured generators (P10), not computed exactly; the York (covariant) TT part is still not
  implemented.
- P4 failed: other modes take up to 26 percent of the TT power by a = 20.

## State of the second round (wave 2b, 2026-11-19)

Established (numbers and run ids in `JOURNAL.md`, section "Second round"; figures `figs/r2_*`,
summaries `results/r2_*`, all looked at):

1. Run-to-run floor (P12c): the eps = 1 baseline rerun on core's requests-b card executable
   (run B-20261119-142833-19edd82, case e1_rep) reproduces the wave-2 release run: c_+(K1)
   agrees to 1e-12 relative in the double-precision dumps through a = 140 (comparison
   B-20261119-160607-ef83373). Card nondeterminism does not limit any comparison of this round.
2. Jittered-lattice null (P11, P16; cases jit0p3, jit0p1 of B-20261119-142833-19edd82: one
   plane wave, lattice jittered by A = 0.3 and 0.1 cells along y and z, 64^3, 8 per cell). The
   box-mode strain of the noise is predicted from the initial data before the run (second-order
   formula with the noise potential, 3/5 for a mode without peculiar velocity, noise-noise
   term; run B-20261119-142733-932e595) and measured to 5-30 percent in modulus and <= 0.36 rad
   in phase for 3 <= a <= 20 at K1 and K2, both amplitudes (comparison
   B-20261119-163037-6553674). At A = 0.3 it is at most 1.5, 2.5, 3.1 percent of the eps = 0.1
   signal for a in 2-20, 20-80, 80-140. The rms TT of all modes is 12-20 times the second-order
   estimate, but 95-100 percent of it lies at |k|L/2pi >= 16 for a <= 12, at a per-shell
   fraction of the non-TT part that is the same for both amplitudes (B-20261119-161734-a3a1366):
   a grid-scale artefact or linear response, not resolved radiation (rho_kin/rho_grad ~ 0.01).
3. delta = 0.0025 (P14; cases d0025_e1, d0025_e0p3): the departure from the second-order value
   scales as (delta a)^2 (ratio 17-19 to delta = 0.01 at a = 20-60; collapse in a delta to 6-47
   percent); |dev| <= 0.5 percent to a = 34 (eps = 1) and 42 (eps = 0.3), against 10 and 13
   at delta = 0.01; 3.5e-4 at a <= 9 in the double-precision dumps (comparison
   B-20261119-164017-cd1ba52). The departure after a ~ 10 at delta = 0.01 is the next order of
   perturbation theory. Single-precision dumps are at their floor for delta = 0.0025, eps <= 0.3.
4. Initial data (P15): make_waves without jitter equals make_east bit for bit
   (B-20261119-142727-02878d1); the jittered data carry a momentum-constraint residual of the
   tool of 7.6e-4 (A = 0.3) and 2.8e-4 (0.1), zero without jitter (recorded, cause not checked).
5. Tools: `fslib/binread.py` (double-precision bin; 2 tests, 8 tests of the package pass),
   `inputs/conv.athinput` (smoke test B-20261119-142500-72b1213), `scripts/null_prediction.py`
   (reproduces s of the scan data to 0.02 percent).

Pending or not done:
- Card batch BC (Slurm job 4655, run B-20261119-153655-2deca0a, queued since 07:37 local): eps = 1
  at 64^3 with 1 and 27 particles per cell and at 128^3 with 1 per cell (P12a, P12b, P13). Its
  initial data exist (B-20261119-142435-275bd43). After the job: `nrpic-run finish`, then
  `analyze_scan.py` on the three case directories (KINDS=bin,dbin; the 128^3 case at NWORK <= 4)
  and `conv_compare.py e1_p1=... e1_p8=<B-20261115-180834-c77a132/cw_eps1.json> e1_p27=...
  e1_n128=... e1_n32=<B-20261115-184650-2d155b6/cw_eps1.json> e1_rep=...`.
- 128^3 at 8 per cell (16.8M particles, ~1.3 card-hours, a chain) was not run (cost).
- Processor companion at 32^3 (requests-b processor executable): jittered nulls (run
  B-20261119-143238-b7961ef), delta = 0.0025 eps = 1 (B-20261119-144416-5f1ab7a) and eps = 0.3
  (B-20261119-153624-224805d); their prediction is B-20261119-143224-f0e6727.
- The discriminating run for P16 (jittered lattice without any wave) and the cause of the
  momentum-constraint residual of the jittered initial data are open.

## Requests

To the B-emd-gw lead:
1. Adopt `fslib/gauge.py` (gauge_piece_total) into `gw_diag` as the gauge-corrected flat TT
   strain; report c_+ raw and corrected in every scan.
2. Close `stage/G0/OPEN.md` item 9 with P7-P10 (journal) and item 7 in part: before a ~ 20 the
   code's zero-shift strain equals the Poisson-gauge second-order strain to < 1.1 percent
   (G_tot) with the slicing Newtonian at first order (P9).
3. Re-word the null criterion of `scope/SCOPE.md` section 6 to an absolute bound (TT amplitude
   at the round-off of the metric, ~1e-15), and the mode-content expectation (P4).

To core:
4. Information for `tracks/core/interfaces/cosmo_gauge.md` section 2 ("no passing test of a
   shift condition in an expanding background"): the Gamma driver `shift_Gamma = 0.75`,
   `shift_eta = 1`, `shift_advect = 1`, `lapse_advect = 1` with the conformal-time lapse ran
   to a = 140 through shell crossing at delta = 0.01, 64^3, 8 particles per cell (run
   B-20261115-165353-b592d43, case cw_eps1_gd; also at 32^3, B-20261115-165525-f7c2004);
   its coordinates differ from the zero-shift run by the time integral of the shift to 5e-4
   (checked by hand at tau = 1.9 on the 32^3 runs, not a registered analysis); uniform mesh
   only.
5. Restart files carry the particles (380 MB per dump at 2.1M particles, 12 GB per run here):
   the double-precision Z4c dump without particles of the wave-1 request
   (`outbox/20261115T1340Z__to-core__gw-analysis-output.md`, item 1) is what the scan needs;
   single-precision `bin` is adequate for the box modes (c_+(K1) from the single- and
   double-precision dumps of the same cycle agree to 4e-5 (eps = 1) and 3e-4 (eps = 0.1)
   over 22 common dumps, analyses B-20261115-180834-c77a132 and -174722-ba1048d) but not for
   the null test of tilde A (2.6e-10 against 4.2e-12 relative).
6. The processor build is serial: 7.5 s per cycle at 32^3 with 262,144 particles; an OpenMP
   processor build would make processor companions practical.

To orch (harness):
7. `nrpic-run submit --launcher local` passes argv without expanding variables: a literal
   `'$NRPIC_RUN_DIR'` argument made a directory of that name in the worktree root (moved, see
   journal). Worth a line in `harness/RULES.md` ("the run directory is in the environment").

Second round (2026-11-19):

To the B-emd-gw lead:
8. Use double-precision mesh output (`double_precision = true`, requests-b executable, or
   core-v0.4 when it carries it) for every GW run at small amplitude: at delta = 0.0025 and
   eps <= 0.3 the single-precision box-mode strain jumps by ~1e-3 of itself from dump to dump
   (P14(a)); `fslib/binread.py` reads both.
9. Cut |k|L/2pi >= N/4 (k h >= pi/2) from any TT spectrum of a run with a noisy particle
   lattice before calling it a signal (P16); the box modes and the band below N/8 are safe.
10. Next runs of this package if wanted: the jittered lattice without any wave (decides P16
   between projector leakage and linear response), and 128^3 at 8 per cell (a chain of ~1.3
   card-hours) to complete the mesh leg at fixed particles per cell.

To core:
11. `problems/cosmo/make_waves.py --jitter` (core/requests-b): with a jittered lattice the
   tool's momentum-constraint residual is 7.6e-4 (A = 0.3, plane wave delta = 0.01, 64^3) and
   2.8e-4 (A = 0.1), against 3e-17 without jitter (run B-20261119-141216-9c98929, `jit0p3.log`);
   probably the momentum density of the moving particles is modulated by the jitter in the
   directions the solve does not absorb. Worth a line in REQUESTS_B.md section 5 or a fix.
12. Thanks for the double-precision bin output: it was needed here (P14(a)); please keep it in
   the release.
