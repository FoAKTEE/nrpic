# waves: linear gravitational waves with both diagnostics (G1 criterion 1 of Track B)

Helper package of owner B-emd-gw, wave 2b (2026-11-19). Two linear-wave tests of the
Z4c solver of this repository's AthenaK, each analysed with the transverse-traceless
projection and with the Weyl diagnostic of `../gw_diag`, against exact solutions, at three
resolutions. Predictions and outcomes: `JOURNAL.md`. Status: deliverables exist and are tested (see Results and Open).

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
python3 -m pytest -q -p no:cacheprovider tracks/B-emd-gw/waves/tests        # 5 tests, 2 s
P=tracks/B-emd-gw/waves; R="harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P"
$R --purpose "..." -- python3 $P/scripts/predict.py                          # predictions (symbol)
$R --cores 2 --purpose "..." -- env NS="16 32" bash $P/scripts/run_flat.sh   # test F, processors
$R --cores 2 --purpose "..." -- env NS="16 32" bash $P/scripts/run_expanding.sh   # test X
$R --purpose "..." -- python3 $P/scripts/make_expanding_ic.py --n 64         # data of X for the card
$R --launcher batch --list $P/inputs/card64.list --exe /data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_gpu --gpu-hours 0.33 ...
   (edit the data path in the list to the new run directory first)
$R --cores 4 --purpose "..." -- bash $P/scripts/run_ascan.sh                 # amplitude scan, N = 16
$R --cores 6 --purpose "..." -- env NWORK=6 python3 $P/scripts/analyze.py --tag n163264_ \
     --flat 16=<F run>/N16,32=<F run>/N32,64=<card run>/flatN64 \
     --exp 16=<X run>/N16,32=<X run>/N32,64=<card run>/expN64
$R --purpose "..." -- python3 $P/scripts/predict_2s.py <results.json>        # H1: the code's RK4()4[2S]
```

Serial processor rate of the core/requests-b executable on the loaded machine: 0.7e4 to
1.5e4 zone-cycles per second (N = 32: 16 and 30 minutes; N = 48: 1.5 and about 2.5
hours); the card does N = 64 in 20 to 40 s per test. Never edit a script while a run
executes it (bash reads scripts incrementally); the analysis copies its JSON and PNG into
`results/` and `figs/`, so commit them before the next submit (a dirty package is refused).

## Results

Labels: [VERIFIED] = measured in the run named; [JUDGEMENT] = my inference. All errors are
those of the forward combination W = P + i P'/|k| of each polarization amplitude at +k
(definitions in `JOURNAL.md`, 14:15), at the last dump (F: t = 4/sqrt 3, four periods;
X: t = 10, a = 36). Predictions: Fourier symbol of the code's stencils with the code's time
integrator (`wlib/predict.py`). Analysis run **B-20261119-155119-5459be6** (N = 16, 32,
64; `results/n163264_results.json`, figures `figs/n163264_*.png`); simulation runs:
F B-20261119-142016-ee73a03 (N = 16, 32), X B-20261119-142021-8f4c441 (N = 16, 32), both
at N = 64 on one card B-20261119-142124-feb2daf (0.019 card-hours); N = 48 of both tests on
processors (F B-20261119-142233-70d5043; X B-20261119-142234-85da208, see "Open").

**Set-ups.** Test F: `z4c_linear_wave` of core/requests-b in [-1/2, 1/2]^3,
k = 2 pi (1, 1, 1), plus amplitude 1e-6 and cross amplitude 5e-7 with relative phase 1 rad
(elliptic), production numerics. Test X, exactly: the cosmological gauge of
`cosmo/README.md` (lapse d_t alpha = -(1/3) alpha^2 K, zero shift, t conformal time,
H = 1 at a = 1), box of side 4, matter only as a lattice of particles at rest (one per
cell, masses 3 h^3/(8 pi)), the production configuration of `cosmo/README.md`, generator
`nrpic_cosmo` with `id = file`: a conformally flat slice with K = -3 and a TT traceless
curvature Ahat = -(1/2) h', h' = 2e-6 e+ cos(k.x) + 1e-6 ex cos(k.x + 1),
k = (pi/2)(1, 1, 0). Exact solution: the standing tensor mode
h = T(t)[...], T = c1 j1(|k|s)/(|k|s) + c2 y1(|k|s)/(|k|s), s = t + 2, T(0) = 0, T'(0) = 1.

1. **Test F, both diagnostics against the exact wave** [VERIFIED].

   | N | TT amplitude | TT phase (rad) | Weyl-6 amplitude | Weyl-6 phase | predicted amplitude, phase | Weyl-6 vs TT | spectral Weyl vs TT |
   |---|---|---|---|---|---|---|---|
   | 16 | -1.409e-4 | 2.531e-4 | -1.716e-4 | 2.531e-4 | -1.409e-4, 2.531e-4 | 3.07e-5 | 1.2e-11 |
   | 32 | -1.717e-6 | 1.218e-5 | -2.208e-6 | 1.218e-5 | -1.718e-6, 1.217e-5 | 4.91e-7 | 1.2e-11 |
   | 64 | -3.10e-8 | 7.067e-7 | -3.87e-8 | 7.067e-7 | -3.17e-8, 7.034e-7 | 8.5e-9 | 1.1e-11 |

   Orders (16-32, 32-64): amplitude 6.36, 5.79; phase 4.38, 4.11 (predicted 6.36, 5.76 and
   4.38, 4.11); Weyl-6 vs TT 5.97, 5.86. The cross polarization has the same errors; the
   polarization ratio W_x/W_+ equals 0.5 e^{i} to <= 1.1e-9 in modulus and argument at
   every N and time (rounding: it scales as 1/A, amplitude scan). The backward part
   oscillates between 0 and |1 - w_h/k| (3.2e-6, 5.1e-8, 8e-10): the continuum-initialized
   data excite the backward semi-discrete mode. At t = 0 the TT amplitudes equal the
   generator's to 6e-12: its e+, ex are gw_diag's `pol_basis`. Figures `figs/n163264_flat_errors.png`,
   `figs/n163264_convergence.png`.

2. **Test X, both diagnostics against the exact mode** [VERIFIED].

   | N | TT amplitude + / x | TT phase + / x | Weyl-6 amplitude + | Weyl-6 phase + | predicted (2S) amplitude, phase | Weyl-6 vs TT | spectral Weyl vs TT |
   |---|---|---|---|---|---|---|---|
   | 16 | -7.048e-5 / -7.048e-5 | 8.304e-5 / 8.304e-5 | -9.58e-5 | 8.13e-5 | -7.048e-5, 8.304e-5 | 3.13e-5 | 1.9e-8 |
   | 32 | 1.324e-6 / 1.317e-6 | 3.089e-6 / 3.065e-6 | 9.41e-7 | 3.06e-6 | 1.317e-6, 3.065e-6 | 5.01e-7 | 2.2e-8 |
   | 64 | 1.538e-7 / 1.399e-7 | 3.842e-7 / 2.762e-7 | 1.70e-7 | 3.83e-7 | 1.399e-7, 2.762e-7 | 1.7e-8 | 2.3e-8 |

   The errors are those of the code's own time integrator: AthenaK's `rk4` is RK4()4[2S]
   (Ketcheson 2010, `athenak/src/driver/driver.cpp` lines 145-176), which on the
   background coupled to the mode reproduces the measured errors and the background error
   (max |a/a_exact - 1| 5.1e-8, 4.3e-8, 3.2e-8) exactly (H1, run
   B-20261119-153548-c7338f1, `figs/predict_2s.png`); a predictor with classical RK4 and
   the exact background is 20 per cent off at N = 32. The early steps are limited to
   0.01/calH whatever N, so the X errors are dominated by time integration from N = 32 on
   and do not follow a single power of N (orders 5.7, 3.1 amplitude; 4.8, 3.0 phase).
   Polarization: W_x/W_+ = 0.5 e^{i} to 4.6e-9 (N = 16), 2.4e-8 (32), 1.1e-7 (64) in
   argument; this error grows with N and as 1/A and sits in the plus polarization, which
   lives in the diagonal components [JUDGEMENT: rounding of 1 + h through second
   differences; check pending, card run B-20261119-155758-458cf17 with A x10]. Weyl-6 vs
   TT converges at order 6 down to the 2e-8 offset that the spectral evaluation shows at
   every N and A [JUDGEMENT: the background error enters the closed form through
   calH h']. Figures `figs/n163264_exp_errors.png`, `figs/n163264_convergence.png`.

3. **Non-TT content** [VERIFIED]. F: ||h - h^TT||/||h^TT|| grows as t^2 to 1.44e-4 at
   every N, proportional to A (1.44e-3, 1.44e-4, 1.44e-5 for A x10, x1, x1/10): the
   second-order backreaction (periodic_z4c item 3). TT content outside +-k: <= 1.3e-9.
   X: 3.1e-5 of the mode envelope at t = 10 at every N, proportional to A down to a
   rounding floor at A x1/10. The shift stays zero.

4. **Amplitude scan** at N = 16 (runs B-20261119-153637-02c822f, analyses
   B-20261119-154708-89d00ea, B-20261119-154738-30faa29): amplitude and phase errors of
   both tests independent of A to <= 6e-4 of themselves for A x10 and x1/10: the tests are
   in the linear regime and A = 1e-6 is not at a floor at N = 16 (at N = 64 the plus
   polarization of X is affected by rounding, item 2).

**G1 criterion 1** ("the two diagnostics agree on analytic linear waves", with amplitude,
phase and polarization against the analytic solution and measured convergence): met for
both set-ups in my judgement. Both diagnostics recover amplitude, phase and both
polarizations; their difference converges at sixth order (the stencil of the Weyl
evaluation) to 1e-11 (F) and 2e-8 (X) with spectral derivatives; the code's errors
converge at the predicted orders and equal the symbol-plus-integrator prediction to <= 2
per cent (F) and <= 1 per cent (X, cross polarization at all N, plus polarization at
N <= 32).

## Open

- N = 48 of test X (run B-20261119-142234-85da208) and the x10 card check
  (B-20261119-155758-458cf17, Slurm 4662) were running when this was written; the final
  analysis with N = 48 is listed in `JOURNAL.md` if it ran.
- The spatial and temporal parts of the X error are not separated (a run with
  dt_expansion = 0.001 would do it).
- The 2e-8 spectral-Weyl vs TT offset of X is explained only by judgement.

## Requests

(none yet)
