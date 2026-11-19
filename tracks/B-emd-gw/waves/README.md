# waves: linear gravitational waves with both diagnostics (G1 criterion 1 of Track B)

Helper package of owner B-emd-gw, wave 2b (2026-11-19). Two linear-wave tests of the
Z4c solver of this repository's AthenaK, each analysed with the transverse-traceless
projection and with the Weyl diagnostic of `../gw_diag`, against exact solutions, at three
resolutions. Predictions and outcomes: `JOURNAL.md`. Status: in progress (see Results).

## Contents

| Path | What |
|---|---|
| `inputs/flat_oblique.athinput` | test F: `z4c_linear_wave` (core/requests-b), k = 2 pi (1,1,1), elliptic polarization, four periods |
| `inputs/expanding.athinput` | test X: `nrpic_cosmo` (id = file), matter-dominated box of side 4, lattice at rest, free tensor mode along (1,1,0) |
| `scripts/make_expanding_ic.py` | initial data of test X (particles, NRCOSMO1 fields with a TT Ahat) |
| `scripts/run_flat.sh`, `scripts/run_expanding.sh` | the runs (serial processor executable of core/requests-b, one process per resolution) |
| `scripts/predict.py` | predictions from the Fourier symbol of the code's operators (`wlib/predict.py`) |
| `scripts/analyze.py` | both diagnostics on every dump, errors, orders, figures |
| `wlib/refs.py` | exact references: flat travelling wave, matter-era tensor mode (spherical Bessel), mode coefficients, error measures |
| `wlib/weylref.py` | closed-form Psi_4 of a tensor mode on a flat FLRW slice and its inversion to (P, X, P', X') |
| `wlib/measure.py` | reader of double-precision `bin` dumps; TT and Weyl measurement of one dump |
| `tests/test_refs.py` | checks of the references (5 tests) |
| `results/`, `figs/` | JSON results and PNG figures (PDFs in the run directories) |

## How to rerun

```
cd /data/haiyangw/nrpic/wt/B-emd-gw
python3 -m pytest -q -p no:cacheprovider tracks/B-emd-gw/waves/tests
P=tracks/B-emd-gw/waves
harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --purpose "..." -- python3 $P/scripts/predict.py
harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores 3 --purpose "..." -- bash $P/scripts/run_flat.sh
harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores 3 --purpose "..." -- bash $P/scripts/run_expanding.sh
harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores 8 --purpose "..." -- python3 $P/scripts/analyze.py <flat run id> <expanding run id>
```

## Results

(filled after the runs)

## Requests

(none yet)
