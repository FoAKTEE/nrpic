# waves: linear gravitational waves with both diagnostics (G1 criterion 1 of Track B)

Helper package of owner B-emd-gw, wave 2b (2026-11-19) and wave 3 round 1 (2026-11-20/21).
Linear-wave tests of the Z4c solver of this repository's AthenaK, each analysed with the
transverse-traceless projection and with the Weyl diagnostic of `../gw_diag`, against exact
solutions, at four resolutions: F (flat, k along (1,1,1)), F2 (flat, k along (1,2,0), nonzero
discrete divergence), X (tensor mode in the matter-era box) and XS (X with a ten times smaller
expansion step: the time/space split). Round 1 also moved the two-precision reader and the
gauge piece G_tot into gw_diag. Predictions and outcomes: `JOURNAL.md`. Status: deliverables
exist and are tested; round 1 closed (see Results and Open).

## Contents

| Path | What |
|---|---|
| `inputs/flat_oblique.athinput` | test F: `z4c_linear_wave` (core/requests-b), k = 2 pi (1,1,1), elliptic polarization, four periods |
| `inputs/expanding.athinput` | test X: `nrpic_cosmo` (id = file), matter-dominated box of side 4, lattice at rest, free tensor mode along (1,1,0) |
| `scripts/make_expanding_ic.py` | initial data of test X (particles, NRCOSMO1 fields with a TT Ahat) |
| `scripts/run_flat.sh`, `scripts/run_expanding.sh` | the runs (serial processor executable of core/requests-b, one process per resolution) |
| `scripts/predict.py` | predictions from the Fourier symbol of the code's operators (`wlib/predict.py`) |
| `scripts/predict_2s.py` | test of H1: the code's RK4()4[2S] on the background coupled to the mode, against measured errors |
| `scripts/run_ascan.sh` | amplitude scan (x10, x1/10) of both tests at N = 16 |
| `inputs/card64.list`, `inputs/card64_x10.list` | card batches: both tests at N = 64; X at N = 64 with A x10 |
| `inputs/flat_120.athinput`, `scripts/run_deck.sh` | test F2: `z4c_linear_wave`, k = 2 pi (1,2,0), elliptic, four periods (t = 4/sqrt 5); run script for any deck |
| `inputs/card_r1.list` | card batch of round 1: F2 at N = 64, XS (X with `particles/dt_expansion = 0.001`) at N = 16..64 on the reference data |
| `wlib/z4c_symbol.py`, `scripts/predict_r1.py` | the whole linearized Z4c system of the code about flat space (25 amplitudes per mode, the code's stencils, Kreiss-Oliger, rk4); predictions of F2 and XS |
| `scripts/analyze_r1.py` | both diagnostics on every dump of F2 (`--mode f120`, with Gamma, Theta, Khat and the non-TT part at +k against the symbol) or XS (`--mode xdt`, against the 2S prediction at the new step and the reference) |
| `scripts/xs_split.py` | time and space parts of the X error from the XS analyses and the predictions |
| `scripts/fig_x10.py` | figure and summary of the x10 rounding check |
| `scripts/check_readers.py`, `scripts/check_gauge.py` | checks of gw_diag's `binio.read_bin` and `gauge` against the readers and the module they replace, on real dumps |
| `scripts/analyze.py` | both diagnostics on every dump, errors, orders, figures (`--tag`, `--scale-flat/--scale-exp`) |
| `wlib/refs.py` | exact references: flat travelling wave, matter-era tensor mode (spherical Bessel), mode coefficients, error measures |
| `wlib/weylref.py` | closed-form Psi_4 of a tensor mode on a flat FLRW slice and its inversion to (P, X, P', X') |
| `wlib/measure.py` | reader of double-precision `bin` dumps (superseded by gw_diag's `binio.read_bin`, bit-identical); TT and Weyl measurement of one dump |
| `tests/test_refs.py` | checks of the references (5 tests) |
| `results/`, `figs/` | JSON results and PNG figures (PDFs in the run directories); `final_*` are the reference set |

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
# round 1 (wave 3)
$R --cores 6 --purpose "..." -- env NWORK=6 python3 $P/scripts/analyze.py --tag x10_64_ --scale-flat 10 \
     --scale-exp 10 --flat 64=B-20261119-142124-feb2daf/flatN64 --exp 64=<x10 card run>/expN64x10 --no-figures
$R --purpose "..." -- python3 $P/scripts/fig_x10.py <final run>/final_dumps_exp_N64.json <x10 analysis>/x10_64_dumps_exp_N64.json
$R --purpose "..." -- python3 $P/scripts/predict_r1.py                       # F2 and XS predictions
$R --cores 3 --purpose "..." -- env DECK=$P/inputs/flat_120.athinput NS="16 32 48" bash $P/scripts/run_deck.sh
$R --cores 2 --purpose "..." -- env NS="16 32" EXTRA="particles/dt_expansion=0.001" bash $P/scripts/run_expanding.sh
$R --launcher batch --list $P/inputs/card_r1.list --exe /data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_gpu --gpu-hours 0.2 ...
$R --cores 3 --purpose "..." -- env NWORK=3 python3 $P/scripts/analyze_r1.py --mode f120 --tag f120_ \
     --runs 16=<F2 run>/N16,32=<F2 run>/N32,48=<F2 run>/N48,64=<card run>/f120N64
$R --cores 3 --purpose "..." -- env NWORK=3 python3 $P/scripts/analyze_r1.py --mode xdt --tag xdt_card_ \
     --dt-expansion 0.001 --ref $P/results/final_results.json \
     --ref-dumps /data/haiyangw/nrpic/scratch/B-emd-gw/B-20261119-164402-7438a99 \
     --runs 16=<card run>/xdt3N16,32=<card run>/xdt3N32,48=<card run>/xdt3N48,64=<card run>/xdt3N64
   (the same with --tag xdt_cpu_ --runs 16=<XS run>/N16,32=<XS run>/N32 for the processor runs)
$R --purpose "..." -- python3 $P/scripts/xs_split.py --card $P/results/xdt_card_results.json --cpu $P/results/xdt_cpu_results.json
$R --package tracks/B-emd-gw/gw_diag --purpose "..." -- python3 $P/scripts/check_readers.py <bin files>
$R --package tracks/B-emd-gw/gw_diag --purpose "..." -- python3 $P/scripts/check_gauge.py <z4c bin files>
```

Serial processor rate of the core/requests-b executable on the loaded machine: 0.7e4 to
1.5e4 zone-cycles per second (N = 32: 16 and 30 minutes; N = 48: 1.5 and about 2.5
hours; XS at N = 32, 3585 steps: 2.6 hours); the card does N = 64 in 20 to 40 s per test
and the whole round-1 batch (F2 at 64, XS at 16..64) in 205 s. Analyses take 1 to 4 minutes
on 3 cores. Never edit a script while a run
executes it (bash reads scripts incrementally); the analysis copies its JSON and PNG into
`results/` and `figs/`, so commit them before the next submit (a dirty package is refused).

## Results

Labels: [VERIFIED] = measured in the run named; [JUDGEMENT] = my inference. All errors are
those of the forward combination W = P + i P'/|k| of each polarization amplitude at +k
(definitions in `JOURNAL.md`, 14:15), at the last dump (F: t = 4/sqrt 3, four periods;
X: t = 10, a = 36). Predictions: Fourier symbol of the code's stencils with the code's time
integrator (`wlib/predict.py`). Final analysis run **B-20261119-164402-7438a99**
(`results/final_results.json`, figures `figs/final_flat_errors.png`,
`figs/final_exp_errors.png`, `figs/final_convergence.png`). Simulation runs: F
B-20261119-142016-ee73a03 (N = 16, 32), B-20261119-142233-70d5043 (48); X
B-20261119-142021-8f4c441 (16, 32), B-20261119-142234-85da208 (48; recorded as failed,
exit 127 of its wrapper after a complete AthenaK run, `JOURNAL.md` 16:40); both at N = 64 on
one card, B-20261119-142124-feb2daf (0.019 card-hours).

**Set-ups.** Test F: `z4c_linear_wave` of core/requests-b in [-1/2, 1/2]^3,
k = 2 pi (1, 1, 1), plus amplitude 1e-6 and cross amplitude 5e-7 with relative phase 1 rad
(elliptic), production numerics (nghost 4, RK4, Courant 0.25, KO 0.5, conformal-time
lapse, zero shift). Test X, exactly: the cosmological gauge of `cosmo/README.md` (lapse
d_t alpha = -(1/3) alpha^2 K, zero shift, t conformal time, H = 1 at a = 1), box of side 4,
matter only as a lattice of particles at rest (one per cell, masses 3 h^3/(8 pi)), the
production configuration of `cosmo/README.md`, generator `nrpic_cosmo` with `id = file`: a
conformally flat slice with psi = 1, K = -3, alpha = 1 and the TT traceless curvature
Ahat = -(1/2) h', h' = 2e-6 e+ cos(k.x) + 1e-6 ex cos(k.x + 1), k = (pi/2)(1, 1, 0).
Exact solution: the standing tensor mode h = T(t)[...],
T = c1 j1(|k|s)/(|k|s) + c2 y1(|k|s)/(|k|s), s = t + 2, T(0) = 0, T'(0) = 1.

1. **Test F, both diagnostics against the exact wave** [VERIFIED].

   | N | TT amplitude | TT phase (rad) | Weyl-6 amplitude | Weyl-6 phase | predicted amplitude, phase | Weyl-6 vs TT | spectral Weyl vs TT (forward combination) |
   |---|---|---|---|---|---|---|---|
   | 16 | -1.409e-4 | 2.531e-4 | -1.716e-4 | 2.531e-4 | -1.409e-4, 2.531e-4 | 3.07e-5 | 1.2e-11 |
   | 32 | -1.717e-6 | 1.218e-5 | -2.208e-6 | 1.218e-5 | -1.718e-6, 1.217e-5 | 4.91e-7 | 1.2e-11 |
   | 48 | -1.574e-7 | 2.273e-6 | -2.006e-7 | 2.273e-6 | -1.576e-7, 2.270e-6 | 4.42e-8 | 1.2e-11 |
   | 64 | -3.10e-8 | 7.067e-7 | -3.87e-8 | 7.067e-7 | -3.17e-8, 7.034e-7 | 8.47e-9 | 1.1e-11 |

   Local orders (16-32, 32-48, 48-64): amplitude 6.36, 5.89, 5.65; phase 4.38, 4.14,
   4.06 (Kreiss-Oliger and the fourth-order integrator; predicted 6.36 and 4.38 for the
   first pair); Weyl-6 vs TT 5.97, 5.94, 5.74 (the sixth-order stencil of the Weyl
   evaluation). The cross polarization has the same errors; the polarization ratio
   W_x/W_+ equals 0.5 e^{i} to <= 1.1e-9 in modulus and argument at every N and time
   (rounding: it scales as 1/A). The backward part oscillates between 0 and
   |1 - w_h/k| (maxima 3.2e-6, 5.1e-8, 4.5e-9, 9.7e-10): the continuum-initialized data
   excite the backward semi-discrete mode. At t = 0 the TT amplitudes equal the generator's
   to 6e-12: its e+, ex are gw_diag's `pol_basis`. Wording after verifier3
   (`../stage/G1/verifier3/VERIFIER.md` section 3, claim F5): the TT-Weyl agreement of the last
   column holds for the forward combination W; verifier3's own route gives 6.0e-11 to 6.4e-11;
   with h alone (no time derivative) the two differ by the backward discrete wave
   theta^6/1120 |sin w t| (theta = 2 pi/N; 3.2e-6 at N = 16). "Weyl-6" is gw_diag's
   `weyl.electric_magnetic(order=6)`: Ricci from sixth-order centred first derivatives, the
   seven-point sixth-order stencil for d_a d_a and two first-derivative stencils in turn for
   d_a d_b (`../gw_diag/gwdiag/weyl.py`, `Deriv.d2`), B from sixth-order first derivatives of
   K; other constructions give other Weyl-6 numbers (verifier3: 4-5 per cent in amplitude).

2. **Test X, both diagnostics against the exact mode** [VERIFIED].

   | N | TT amplitude + / x | TT phase + / x | Weyl-6 amplitude + | Weyl-6 phase + | predicted (2S) amplitude, phase | Weyl-6 vs TT | spectral Weyl vs TT |
   |---|---|---|---|---|---|---|---|
   | 16 | -7.048e-5 / -7.048e-5 | 8.304e-5 / 8.304e-5 | -9.58e-5 | 8.13e-5 | -7.048e-5, 8.304e-5 | 3.13e-5 | 1.9e-8 |
   | 32 | 1.324e-6 / 1.317e-6 | 3.089e-6 / 3.065e-6 | 9.41e-7 | 3.06e-6 | 1.317e-6, 3.065e-6 | 5.01e-7 | 2.2e-8 |
   | 48 | 4.362e-7 / 4.250e-7 | 6.478e-7 / 5.880e-7 | 4.24e-7 | 6.44e-7 | 4.250e-7, 5.879e-7 | 4.50e-8 | 2.4e-8 |
   | 64 | 1.538e-7 / 1.399e-7 | 3.842e-7 / 2.762e-7 | 1.70e-7 | 3.83e-7 | 1.399e-7, 2.762e-7 | 1.66e-8 | 2.3e-8 |

   The errors are those of the code's own time integrator: AthenaK's `rk4` is RK4()4[2S]
   (Ketcheson 2010, `athenak/src/driver/driver.cpp` lines 145-176), which applied to the
   uniform background coupled to the mode reproduces the measured errors of the cross
   polarization at every N to <= 0.5 per cent and the background error (max
   |a/a_exact - 1| = 5.1e-8, 4.3e-8, 3.7e-8, 3.2e-8) to two digits (H1, run
   B-20261119-153548-c7338f1, `figs/predict_2s.png`); a classical-RK4 predictor with the
   exact background is 20 per cent off at N = 32. The early steps are limited to
   0.01/calH whatever N, so from N = 32 on the X errors are dominated by time integration
   and follow no single power of N. Polarization: W_x/W_+ = 0.5 e^{i} to 4.5e-9 (N = 16),
   2.4e-8 (32), 6.0e-8 (48), 1.1e-7 (64) in argument; this error sits in the plus
   polarization, which lives in the diagonal components, grows with N, and scales as 1/A
   at N = 16 and at N = 64 (item 5: rounding of the diagonal 1 + h [VERIFIED by the x10
   run]; "through second differences" stays JUDGEMENT). Weyl-6 vs TT converges at sixth
   order (5.97, 5.95) down to an offset of 2e-8 that the spectral evaluation shows at every
   N and A; it is a step effect (item 7: with a ten times smaller step it falls to
   <= 2.8e-10 and Weyl-6 vs TT converges at order 6 down to 8.1e-9 at N = 64). The plus
   amplitudes at N = 48 and 64 (4.362e-7, 1.538e-7) and the plus phase at those N are
   rounding-limited (item 5); the truncation error is the cross value, 1.40e-7 at N = 64,
   which the x10 run gives for both polarizations. They are moduli of the complex mode
   amplitude; verifier3 keeps the part in phase with the exact solution and gets 4.2346e-7
   and 1.3775e-7: a difference of definition, not of data (lead's runs
   B-20261121-063617-6183015, B-20261121-063835-826c461). "Deviates by up to 39 per cent" in
   the criterion paragraph is a statement about the phase.

3. **Non-TT content** [VERIFIED]. F: ||h - h^TT||/||h^TT|| grows as t^2 to 1.44e-4 at
   every N, proportional to A (1.44e-3, 1.44e-4, 1.44e-5 for A x10, x1, x1/10): the
   second-order backreaction (periodic_z4c item 3). TT content outside +-k: <= 1.3e-9.
   X: 3.1e-5 of the mode envelope at t = 10 at every N, proportional to A down to a
   rounding floor at A x1/10. The shift stays zero; the Hamiltonian-constraint norm of X
   is 9.0e-14 (volume integral of H^2) at every N, that of the background.

4. **Amplitude scan** at N = 16 (runs B-20261119-153637-02c822f, analyses
   B-20261119-154708-89d00ea, B-20261119-154738-30faa29): amplitude and phase errors of
   both tests independent of A to <= 6e-4 of themselves for A x10 and x1/10: the tests are
   in the linear regime and A = 1e-6 is not at a floor at N = 16 (at N >= 48 the plus
   polarization of X is affected by rounding, item 2).

5. **x10 rounding check, X at N = 64 with the amplitude x10** [VERIFIED] (card run
   B-20261119-155758-458cf17, 0.0072 card-hours; analysis B-20261120-221708-d8eae03, figure
   B-20261120-222234-4e2435d, `figs/x10_check.png`, `results/x10_check.json`). The
   polarization-ratio error at t = 10 falls 9.86 times (argument, -1.079e-7 -> -1.094e-8) and
   9.62 times (modulus) for ten times the amplitude; the plus errors come to within 1.2 per
   cent (amplitude 1.4154e-7) and 4.8 per cent (phase 2.8952e-7) of the 2S prediction; the
   cross stays on it (+2.0e-10, +2.4e-9; the latter about A^2, a second-order frequency shift
   [JUDGEMENT]). The plus excess of X at N >= 48 is rounding of the diagonal 1 + h (scales as
   1/A). Prediction of 2026-11-19 16:00 confirmed (`JOURNAL.md` 2026-11-20 22:25).

6. **Test F2, k = 2 pi (1,2,0), both diagnostics against the exact wave** [VERIFIED]
   (processors B-20261120-222849-3b921b7 for N = 16, 32, 48; card B-20261120-222841-acfe21d
   for N = 64; analysis B-20261121-125625-7af3965, `results/f120_results.json`,
   `figs/f120_errors.png`, `figs/f120_convergence.png`). Same numerics as F; the discrete
   divergence of the continuum-TT data is not zero along (1,2,0) (relative 4.1e-4 at N = 16,
   1.1e-7 at 64), which drives Gamma^i through the constraint damping and a non-TT part.

   | N | TT amplitude + (symbol) | TT phase + (symbol) | Weyl-6 amplitude | Weyl-6 vs TT | spectral vs TT | non-TT at +k (symbol) |
   |---|---|---|---|---|---|---|
   | 16 | -6.6774e-3 (-6.6774e-3) | 4.3208e-3 (4.3208e-3) | -7.632e-3 | 9.61e-4 | 2.26e-11 | 2.092e-5 (2.092e-5) |
   | 32 | -6.3075e-5 (-6.3076e-5) | 9.4790e-5 (9.4789e-5) | -7.946e-5 | 1.64e-5 | 2.27e-11 | 3.589e-7 (3.588e-7) |
   | 48 | -3.9966e-6 (-3.9970e-6) | 1.1729e-5 (1.1727e-5) | -5.459e-6 | 1.46e-6 | 2.26e-11 | 3.262e-8 (3.204e-8) |
   | 64 | -5.7576e-7 (-5.7643e-7) | 2.9264e-6 (2.9238e-6) | -8.374e-7 | 2.62e-7 | 2.24e-11 | 6.21e-9 (5.74e-9) |

   "Symbol" is the whole linearized Z4c system of the code (`wlib/z4c_symbol.py`), written
   before the runs. Both polarizations equal it to <= 0.12 per cent (amplitude) and 0.09 per
   cent (phase) at every N; local orders 6.73, 6.80, 6.73 (amplitude) and 5.51, 5.15, 4.83
   (phase), the symbol's; the Weyl-6 phase equals the TT phase to 4 digits; Weyl-6 vs TT
   converges at 5.87, 5.96, 5.97 (= 0.80 times the symbol error of the stencil); spectral
   Weyl vs TT (forward combination) 2.2e-11 to 2.3e-11. Polarization ratio 0.5 e^{i} to
   <= 1.4e-9; t = 0 amplitudes equal the generator's to 4.7e-12; backward maxima equal
   |1 - w_h/k| to 0.6 per cent. The non-TT part and Gamma^i at +k follow the symbol (0.02 and
   0.25 per cent at N = 16) and fall at order 5.8-5.9, but Gamma meets a floor of about 1e-15
   to 1e-14 at its nodes from N = 32 on and everywhere at N = 64 (the per-dump prediction F2-4
   failed there; [JUDGEMENT] rounding). Psi_4 sees only the TT wave.

7. **Time and space parts of the X error** [VERIFIED] (XS: card B-20261120-222841-acfe21d at
   N = 16..64, processors B-20261120-222849-e5673dc at N = 16, 32 with the reference script,
   executable and byte-identical data; only `particles/dt_expansion` 0.01 -> 0.001; analyses
   B-20261121-125625-18183ef, B-20261121-130242-7781791, split B-20261121-130317-4e8107e,
   `results/xs_split.json`, `figs/xs_split.png`, `figs/xdt_card_errors.png`). Cross
   polarization at t = 10:

   | N | error at 0.01 amp / phase | at 0.001 (= space part) | time part, measured | time part, 2S |
   |---|---|---|---|---|
   | 16 | -7.048e-5 / 8.304e-5 | -7.8413e-5 / 7.1982e-5 | 7.9328e-6 / 1.1057e-5 | 7.9328e-6 / 1.1057e-5 |
   | 32 | 1.317e-6 / 3.065e-6 | -5.9288e-7 / 1.1463e-6 | 1.9097e-6 / 1.9186e-6 | 1.9097e-6 / 1.9187e-6 |
   | 48 | 4.250e-7 / 5.880e-7 | -3.1549e-8 / 1.0209e-7 | 4.5653e-7 / 4.8588e-7 | 4.5653e-7 / 4.8588e-7 |
   | 64 | 1.399e-7 / 2.762e-7 | -3.1034e-9 / 1.9201e-8 | 1.4299e-7 / 2.5704e-7 | 1.4299e-7 / 2.5704e-7 |

   The 0.001 errors equal the 2S prediction at that step to <= 0.2 per cent (the time part left
   there is <= 8e-10); the measured time part equals the predicted one to 4 digits at every N.
   The space part converges at orders 7.05, 7.23, 8.06 (amplitude) and 5.97, 5.96, 5.81
   (phase), the symbol's. So at the production step the X error is space-dominated at
   N = 16 and set by the expansion step limit from N = 32 on (at N = 64: time 1.43e-7 in
   amplitude, space -3.1e-9). Background at 0.001: |a/a_ex - 1| <= 2.2e-11, |alpha/a - 1| <=
   4.0e-11. The 2e-8 spectral-Weyl vs TT offset of item 2 falls 83 to 305 times (to <= 2.8e-10
   over the run, 6e-11 at t = 10): a step effect; whether through the background in calH h'
   or through the mode's own time error is not separated [JUDGEMENT open]. The plus
   polarization's rounding does not grow with the number of steps (arg R at t = 10 changes by
   0.90 to 1.02 for 5.4 to 10 times more steps; prediction XS-4, a growth with the steps,
   failed): [JUDGEMENT] it is an error rate of the right-hand side fixed by the state. At the
   small step the plus polarization is rounding-limited from N = 48 on.

8. **gw_diag adoption** [VERIFIED]. `../gw_diag/gwdiag/binio.py` (one reader of `bin` output
   in both precisions) equals `wlib/measure.read_bin` and first_source's `binread.read_bin`
   bit for bit on four real dumps, and the old float32 reader on the float32 one (run
   B-20261121-130433-3658490); `../gw_diag/gwdiag/gauge.py` (G, G_tot and `tt_strain`, raw and
   corrected strain) equals first_source's module bit for bit on three real dumps (run
   B-20261121-125606-e2ebf60); gw_diag tests: 26 pass, 2 skip.

**G1 criterion 1** ("the two diagnostics agree on analytic linear waves", here with
amplitude, phase and polarization against the analytic solution and measured
convergence): met for all three set-ups in my judgement [JUDGEMENT], with no open sub-item.
Both diagnostics recover amplitude, phase and both polarizations along (1,1,1) and (1,2,0)
and for the matter-era mode; their difference converges at sixth order (the stencil of the
Weyl evaluation) and is 1e-11 (F), 2e-11 (F2) and, once the step is small, 6e-11 to 3e-10
(X) with spectral derivatives (forward combination); the code's errors equal the
symbol-plus-integrator prediction to <= 2 per cent (F), 0.12 per cent (F2) and 0.5 per cent
(X, cross polarization at every N; the time and space parts separately to 4 digits and 0.2
per cent). The one deviation, the plus polarization of X at N >= 48 (phase up to 39 per
cent above a 4e-7 rad prediction), is rounding of the diagonal metric, shown by the x10 run.

## Open

- The spectral-Weyl vs TT difference of X at the small step (6e-11 at t = 10, spikes to
  2.8e-10 at t = 2 and 6 at every N) is not explained; the 2e-8 offset at the production step
  is a step effect, but its route (background error through calH h', or the mode's own time
  error) is not separated.
- The floor of about 1e-15 to 1e-14 in the mode coefficient of Gamma^i in F2 (and of the
  non-TT part at N = 64 before t = 0.3) is judged rounding, not tested (an x10 run of F2 at
  N = 64 would test it: the floor relative to A should fall tenfold).
- The rounding of the plus polarization is judged an error rate of the right-hand side
  (independent of the step); the mechanism (second differences of 1 + h) is judgement.
- No pending runs. Card time of round 1: 0.0641 card-hours (jobs 4662 and 4745); this
  session (2026-11-21) used none.

## Requests

- **B-emd-gw lead.** (0) Round 1 (2026-11-21): criterion 1 is closed with no open
  sub-item (Results 5-7 and the criterion paragraph): x10 check B-20261120-221708-d8eae03,
  F2 analysis B-20261121-125625-7af3965, split B-20261121-130317-4e8107e; G1 OPEN item 9 and
  first_source request 1 are done (Results 8: gw_diag `binio`, `gauge`). Failed predictions
  on record: F2-4 per dump, XS-3 bound at N = 64 (marginal), XS-4. The README wordings asked
  by verifier3 (F5, X1, "39 per cent", how Weyl-6 is built) are in items 1, 2 and the
  criterion paragraph. (1) G1 criterion 1 (wave 2b): the evidence is the final analysis run
  B-20261119-164402-7438a99 with the simulation runs listed under Results. (2) Trap for HANDOFF.md: restoring a script with git
  does not protect a bash process that is executing it (bash keeps reading the old inode,
  which an in-place editor has already changed); run B-20261119-142234-85da208 ended with
  exit 127 that way after a complete AthenaK run. (3) Done in round 1: gw_diag's
  `binio.read_bin` reads both precisions (Results 8); `readers.read_bin` is unchanged.
- **core.** (1) Done: core/requests-b is in release core-v0.4 (corrected generator,
  double-precision output). Round 1 used the core/requests-b executables so that the runs
  match the reference runs; nothing of this package needs a newer executable. (2) Information, no
  action: `z4c_linear_wave` sets At from the continuum frequency |k|, so the data carry a
  backward semi-discrete mode of relative size |1 - w_h/k|/2 (3.2e-6 of the wave at 16
  cells along (1,1,1)); harmless for the tests, visible in the backward combination.
  (3) The serial processor build runs Z4c at 0.7e4 to 1.5e4 zone-cycles per second on the
  loaded machine (N = 48: 1.5 to 2.3 hours); the threaded build of core-v0.5 now exists
  (not used here: the reference runs are serial and the brief excluded the threaded
  core_build-openmp executable, which lacks the corrected generator).
  (5) Information, no action: along (1,2,0) the continuum-TT data of `z4c_linear_wave` have
  a discrete divergence (relative 4.1e-4 at 16 cells), which the Gamma constraint damping
  turns into a non-TT part of 2.1e-5 of the wave at N = 16 (falls as N^-6); harmless for the
  TT diagnostics (Results 6). (4) Initial data with a TT
  metric part (REQUESTS_B.md item 6) would allow a travelling wave in the expanding box;
  the conformally flat slice with a TT Ahat used here gives the standing wave only.
