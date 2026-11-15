# C-sidm/models: initial models, Juttner fluid onset, growth-rate pipeline (wave 2)

Helper package of owner C-sidm (wave 2, work package "models"). It delivers

1. the particle models of the science family the lead chose (truncated Maxwell-Boltzmann
   core of arXiv:2108.11967, "F21", with b = kT(R)/m = 0.1, near its E_b maximum and at
   both fluid onsets) and the five King threshold models, at N = 10^4 and 10^5, built with
   the existing generator chain of `../equilibria/` and checked offline;
2. the fluid onset of the F21 b-family with the adiabatic index of a collision-dominated
   (Juttner) gas;
3. the pipeline that measures collapse times and growth rates of cluster runs
   (`growth.py`), validated on the first paper's runs (`/data/haiyangw/nrpic/runs/st/`)
   against the numbers of `paper/sections/tables/tab_outcomes.tex`.

Everything here is a reference solution or analysis of AthenaK output (decision 0010); no
simulation was run and no card time was used. Predictions and outcomes of every test:
`JOURNAL.md` (entries 1-6). Labels: [VERIFIED] computed in a registered run named here;
[JUDGEMENT]; [TO VERIFY].

## Files

| File | What it is |
|---|---|
| `evstatic_b.py` | `../equilibria/evstatic.py` (commit 904eb96) plus the family `tmb`, kernel (exp((1 - E/E0)/b) - 1)_+; the King lines run with b = 1.0 and give bit-identical results (`diff ../equilibria/evstatic.py evstatic_b.py`: 41 changed lines, header included) |
| `model_set.py` | The 13 models: 5 King rows taken from `../equilibria/models.py`, 8 F21 b = 0.1 rows (table below) |
| `make_models.py` | Builder: `../equilibria/make_equilibria.build` with `ev` -> `evstatic_b`, `models` -> `model_set` rebound (nothing in `equilibria/` edited); adds b, w0 and the resolution of the centre to each JSON |
| `check_models.py` | Offline checks: `../equilibria/check_equilibria.check_model` unchanged (rebound the same way), the F21 cross-check against `../gravothermal/tmb.py`, the King byte-regression |
| `tov_check.py` | Step-size test of the TOV-residual check (entry 5, T1) |
| `fluid_onset.py` | Lowest radial-pulsation eigenvalue of the F21 equilibria (`tmb.fem_lowest`) with five adiabatic indices, roots in w0 and Z(0) |
| `growth.py` | Pipeline: readers, collapse times (first apparent horizon, lapse crossings), crossing times, smoothed log-linear growth fit with a threshold window and a curve_fit second estimator, the first paper's half-swing growth |
| `validate_growth.py` | G1 published numbers, G2 synthetic signals, G3-G6 growth rates of the unstable runs |
| `diag_g2.py` | Diagnosis of the G2 bias (entry 5, D1) |
| `figures.py` | `figs/fig_fluid_onset`, `figs/fig_models`, `figs/fig_growth` (style `python/nrpic/figstyle.py`) |
| `results/` | Copies of the run outputs quoted here (JSON) |
| `figs/` | PNG and PDF of the figure run |

## The models (ADM mass M = 1; stratified sampler, seed 1)

Files `<tag>_stratified_N<N>_s1.{nrp,tab,json}` in
`scratch/C-sidm/C-20261115-170126-b4f74af/` (N = 10^4) and
`scratch/C-sidm/C-20261115-170742-84990ed/` (N = 10^5, 80 MB); not committed, rebuilt by
the commands below. Each JSON carries the `<problem>` and `<particles>` settings for
AthenaK's `nrpic_cf` (table, lapse = table, particle file), as `../equilibria/README.md`
describes. Numbers from `results/index_N100000.json` [VERIFIED]:

| tag | role | w0 (F21) | Z(0) | E_b | R/M | alpha_c | central spacing at 1e4 / 1e5 (M, proper) | per cell of M/4 at 1e4 / 1e5 | N inside n = n_c/2, at 1e5 |
|---|---|---|---|---|---|---|---|---|---|
| tmb01_Z0p5000 | stable side | 2.973024 | 0.50000 | 0.035070 | 20.016 | 0.66667 | 0.270 / 0.125 | 2.4 / 23.8 | 13974 |
| tmb01_Z0p5200 | stable side | 3.069027 | 0.52000 | 0.035152 | 20.202 | 0.65789 | 0.262 / 0.122 | 2.7 / 26.8 | 13674 |
| tmb01_Z0p5331 | fluid onset, Juttner Gamma_1(theta_E) | 3.130772 | 0.53306 | 0.035175 | 20.348 | 0.65229 | 0.257 / 0.119 | 2.9 / 29.0 | 13482 |
| tmb01_Z0p5404 | E_b maximum (F21 turning point) | 3.165241 | 0.54041 | 0.035179 | 20.440 | 0.64918 | 0.254 / 0.118 | 3.0 / 30.2 | 13375 |
| tmb01_Z0p5600 | past the E_b maximum | 3.255887 | 0.56000 | 0.035155 | 20.713 | 0.64103 | 0.248 / 0.115 | 3.4 / 33.8 | 13093 |
| tmb01_Z0p5800 | past the E_b maximum | 3.346754 | 0.58000 | 0.035084 | 21.039 | 0.63291 | 0.241 / 0.112 | 3.8 / 37.8 | 12811 |
| tmb01_Z0p6000 | past the E_b maximum | 3.435919 | 0.60000 | 0.034969 | 21.412 | 0.62500 | 0.235 / 0.109 | 4.2 / 42.1 | 12534 |
| tmb01_Z0p6348 | fluid onset, F21 gamma = 1 + p/u | 3.587099 | 0.63482 | 0.034674 | 22.177 | 0.61169 | 0.225 / 0.104 | 5.0 / 50.5 | 12064 |
| king_y0p31400 | stable (2009.08163 l.1146) | - | 0.47880 | 0.035489 | 13.974 | 0.67622 | 0.305 / 0.142 | 1.6 / 15.7 | 20050 |
| king_y0p32400 | stable | - | 0.49529 | 0.035564 | 13.794 | 0.66877 | 0.299 / 0.139 | 1.7 / 17.2 | 19906 |
| king_y0p33403 | threshold (E_b maximum) | - | 0.51191 | 0.035589 | 13.630 | 0.66141 | 0.293 / 0.136 | 1.9 / 18.8 | 19761 |
| king_y0p34400 | unstable | - | 0.52851 | 0.035564 | 13.481 | 0.65423 | 0.287 / 0.133 | 2.0 / 20.5 | 19616 |
| king_y0p35400 | unstable | - | 0.54524 | 0.035492 | 13.345 | 0.64715 | 0.282 / 0.131 | 2.2 / 22.2 | 19470 |

Z(0) = 1/alpha_c - 1 (F21 main.tex:255-257). y0 = -ln(1 - b w0). "Per cell" counts
macroparticles in a coordinate cube of side M/4 at the centre (n_c N/M0 psi_c^6 dx^3).
The b = 0.1 models are core-halo: R/M = 20-22 against a core radius (n = n_c/2) of
1.7-2.1 M; 12-14 percent of the particles lie inside it (King: 20 percent).

## Results

**Models (entries 5 and 6).** [VERIFIED] M1: the King files at N = 10^4 are byte-identical
to those of run C-sidm-20261115-120610-b4592be (10/10). M2: evstatic_b and `tmb.solve`
(independent variables and quadratures) agree on Z(0), eps, R/M, M0/M to 5e-11; the E_b
maximum lies at Z(0) = 0.54041288 (criteria.json: 0.54041286). M3: every check of
`check_equilibria.check_model` passes for all 13 models at both N except the anisotropic
TOV residual of the three most compact b = 0.1 models (1.1-1.4e-6 against a limit of
1e-6); T1 shows this is the h^2 truncation error of the check's finite difference
(residual ratios 4.00, 3.99 on halving h, all below 9e-8 at h/4). sum m W/psi - M is
+2.2e-4 to +3.0e-4 at 10^4 and -2.2e-5 to -4.0e-5 at 10^5.

**Juttner fluid onset (entry 2).** [VERIFIED, run C-20261115-165315-7b473b8] For b = 0.1
the onset (omega_0^2 = 0) lies at Z(0) = 0.6348 with F21's gamma = 1 + p/u (reproduces
the gravothermal package to 1e-9), but at 0.5331 with Gamma_1 = 1 + 1/c_v of a Juttner gas
at the energy-matched temperature, 0.5317 at theta = p/n, 0.4125 at the Tolman temperature
parameter, 0.5404 with the Juttner 1 + p/u; the E_b maximum is at 0.5404. Same picture
for b = 0.2, 0.3, 0.5 (J_E onset 0.504, 0.498, 0.494, each below the E_b maximum).
[JUDGEMENT] With the index that a collision-dominated gas actually has, the Kn -> 0 anchor
sits just on the stable side of the collisionless E_b maximum (by 0.0074 in Z(0)), not
0.09 above it; the choice of temperature moves it by up to 0.12.

**Growth-rate and collapse-time pipeline (entries 3-5).** [VERIFIED, runs
C-20261115-170346-298a1ba, C-20261115-170713-cefe1c2]
- Collapse and crossing times: all 18 published numbers recovered at their printed
  precision (first apparent horizons 191.0, 104.3, 147.2; M_AH 1.0000, 1.0001, 0.9970;
  macroparticles left 6, 3, 0; alpha_c at the end 0.051, 0.016; alpha_c(0) 0.749; first
  crossings of alpha_c = 0.8 at 59, 88, 86, 91; half-swing growth 1.3e-5 and 1.7e-5 per M).
  The lapse proxy t(alpha_c = 0.2) precedes the first apparent horizon by 1.1-3.3 M.
- Growth rate of the unperturbed y_c = 0.5 model (three compensated samples):
  0.0655 +- 0.0032, 0.0606 +- 0.0055, 0.0602 +- 0.0049 per M (spread 5.5 percent);
  within 7-18 percent over smoothing 5-20 M and windows (0.003, 0.03)-(0.01, 0.1).
- Known defects: on synthetic signals the log-linear fit is biased by +3 to +4 percent
  and its error is too small (G2 failed); D1 traced this to measuring the departure from
  the first record, which holds the initial mode amplitude; with the exact reference the
  bias is -0.5 to -1.0 percent and with a boxcar of one oscillation period below 0.03
  percent. The radius enclosing 10 percent of the rest mass gives rates 14-33 percent off
  those of alpha_c (G4 failed; 1-1.5 SE). In the kicked collapsing runs the fit measures
  the nonlinear plunge (0.17 per M), not the linear mode (G5).
- Use for the threshold runs [JUDGEMENT]: smoothing width = core oscillation period,
  departure from the model's equilibrium alpha_c, window starting well above the initial
  amplitude, errors from independent samples; a few-percent multiplicative bias in sigma
  does not move the zero of sigma^2 along a sequence.

## How to rerun

From the worktree root (`harness/bin/nrpic-env create --no-kokkos` once; each command is
registered by `nrpic-run` and writes to `$NRPIC_RUN_DIR`):

    R="harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/C-sidm/models --cores 2"
    $R --purpose "fluid onset" -- python3 tracks/C-sidm/models/fluid_onset.py
    $R --purpose "models 1e4" -- python3 tracks/C-sidm/models/make_models.py --N 10000 --seed 1
    $R --purpose "models 1e5" -- python3 tracks/C-sidm/models/make_models.py --N 100000 --seed 1
    $R --purpose "checks 1e4" -- python3 tracks/C-sidm/models/check_models.py --ic scratch/C-sidm/<build 1e4> --N 10000 \
        --king-reference scratch/C-sidm/C-sidm-20261115-120610-b4592be
    $R --purpose "checks 1e5" -- python3 tracks/C-sidm/models/check_models.py --ic scratch/C-sidm/<build 1e5> --N 100000
    $R --purpose "TOV step" -- python3 tracks/C-sidm/models/tov_check.py
    $R --purpose "growth validation" -- python3 tracks/C-sidm/models/validate_growth.py
    $R --purpose "G2 diagnosis" -- python3 tracks/C-sidm/models/diag_g2.py
    $R --purpose "figures" -- python3 tracks/C-sidm/models/figures.py --onset <onset dir> \
        --checks <check 1e4 dir> <check 1e5 dir> --growth <growth dir>

Wall times: fluid onset 3 min, build 35 s (1e4) and 3.5 min (1e5), checks 7-15 min,
validation 1 min, diagnosis 1 min (processors, 0 card-hours).

## Runs of this package (all scouting, processors, 0 card-hours)

| Run id | What | Outcome |
|---|---|---|
| C-20261115-165315-7b473b8 | fluid onset, b = 0.1-0.5, five indices | F1 pass |
| C-20261115-170126-b4f74af | models N = 10^4 | built |
| C-20261115-170221-b1a491c | checks N = 10^4 (exit 1: three TOV-residual checks) | M1, M2 pass; M3 250/253 |
| C-20261115-170742-84990ed | models N = 10^5 | built |
| C-20261115-171137-9e3c807 | checks N = 10^5 | entry 6 |
| C-20261115-170231-4e68455 | growth validation, first attempt (KeyError in the verdicts, no JSON) | failed run, numbers in run.log |
| C-20261115-170346-298a1ba | growth validation | G1 pass, G2 fail, G3 seeds pass, G4 fail, G5 partly, G6 pass |
| C-20261115-170713-cefe1c2 | G2 diagnosis | D1: cause found |
| C-20261115-171723-17d46f0 | TOV step test | T1 pass |
| figures run | entry 6 | |

## Not done

- No AthenaK read test of the b = 0.1 files (the King threshold files were read by
  AthenaK in run C-sidm-20261115-125308-54870b9; the b = 0.1 tables have the same format,
  but a two-cycle `smoke_athenak.py` run on one of them has not been made).
- No perturbed models (the dynamically accessible kick of 2009.08163 is still a request
  to core, `../equilibria/README.md`).
- The growth pipeline's recommended settings (boxcar = oscillation period, reference =
  equilibrium alpha_c) were tested on synthetic signals only, not yet on runs.
- No models at N = 10^6 (the G2 convergence needs them; about 3 min and 60 MB per model
  with this builder) [JUDGEMENT from the 1e5 timing and file size].

## Requests

- C-sidm lead: (1) decide whether the Kn -> 0 anchor is the J_E onset (Z(0) = 0.5331)
  instead of 0.6348 (decision 3 of `stage/G0/REPORT.md`); the G3 design "a model on each
  side of the collisionless threshold" then has the two anchors 0.0074 apart in Z(0).
  (2) Fold the `tmb` family into `../equilibria/evstatic.py` if one solver is preferred
  (bit-identical for King). (3) The radius KS test of `check_equilibria.py` is not an
  independent test (entry 5); replace it or drop it.
- core: none new (the perturbation recipe of `../equilibria/README.md` stands).
- orch: nrpic-run refuses a local run while other helpers of the same owner hold the 16
  cores; helpers of one worktree queue by retrying (this package retried for up to 20
  minutes). A queue in nrpic-run, or a per-helper share, would help.
