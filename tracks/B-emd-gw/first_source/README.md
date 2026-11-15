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
| `scripts/analyze_scan.py`, `scripts/plot_scan.py` | P1-P6, P8: diagnostics of the scan runs, figures and `scan_summary.json` |
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

## State

See the end of this file (rewritten at the end of the package).

## Requests

See the end of this file.
