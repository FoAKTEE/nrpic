# first_source (helper package of B-emd-gw, wave 2)

The first gravitational-wave source in full relativity (action 1 of `../HANDOFF.md` and
`../stage/G1/STATUS.md`): crossed waves with amplitude ratios (1, eps, 0), eps = 0, 0.1,
0.3, 1, at delta = 0.01 in the box of four initial Hubble radii, two particles per cell and
direction, conformal-time lapse and zero shift, to a = 140; a fifth run (eps = 1) in a
second spatial gauge (Gamma-driver shift, same slicing condition); analysis with
`../gw_diag`. And the open caveat of wave 1 (`../stage/G0/REVIEW.md` lines 98-102): is the
late rise of the flat TT part in the full-GR cosmology dumps a wave or a second-order gauge
effect? Predictions and outcomes, with run ids, in `JOURNAL.md`; the state of each item in
the section "State" below.

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
