# A-pre-2: the analytic criteria for black-hole formation in an early matter era, as code

Track A-emd-pbh, work package A-pre-2 (brief lines 715, 721: "the prediction table of
A-pre-2" is a G1 item), finished in wave 2 (package criteria2). Five papers, each turned into
functions with the locator of every formula, a check against numbers or curves printed in
the paper, and one command that prints the predictions of all criteria for one set of
initial-data parameters; in wave 2 the conversion between the amplitude measures, the
spherical LTB test profile of arXiv:2609.14218 in the form of the expanding-ball package,
the four failures of wave 1 resolved, and the prediction tables of the first scouting runs.
State: done and tested on processors; 0 card-hours used. Nothing here simulates: everything
is a closed form, a quadrature or a Monte Carlo over the papers' own probability laws
(decision 0010 keeps such reference solutions outside `athenak/src/`).

## Files

| File | What |
|---|---|
| `emd_criteria.py` | library: one section per paper, every function cites `<arXiv id>:<line>` of the TeX source in `kb-data/raw/arxiv/<id>/<version>/src` |
| `predict.py` | the prediction table for one parameter set (command below); `predict()` returns the rows |
| `check_criteria.py` | checks T1-T5 against the papers; writes `results.json` and figures `check_T*.{pdf,png}` |
| `scan_disagreement.py` | scan over the brief's range; figures `scan_*.{pdf,png}`, `scan_summary.json`, `example_tables.txt` |
| `runlog.py` | registers each run by hand (`tracks/A-emd-pbh/runs/<run_id>/manifest.json` with the fields nrpic-run reads, outputs in `scratch/A-emd-pbh/<run_id>/`); see Requests |
| `ltb2609.py` | (wave 2) the LTB solution of 2609.14218 in the paper's conventions (`Profile2609`: m, ktilde, t_s, S(x), R(t, r), t_ah, compaction) and as an expball profile (`LTBPeak2609`, `make_ball`), with the threshold statement and its locator |
| `check_criteria2.py` | (wave 2) checks A1-A5 (amplitude measures) and L1-L5 (LTB profile); `results_criteria2.json`, figures `fig_amplitude`, `fig_ltb2609` |
| `test_criteria2.py` | (wave 2) pytest of the same functions (10 tests, about 1 min) |
| `scouting_table.py` | (wave 2) prediction tables for SR-1 and the periodic scouting runs S1, S2: `scouting_predictions.{md,json}`, `fig_scouting_predictions` |
| `JOURNAL.md` | predictions written before each run, outcomes after, failed ones included |

Sources (read in full where cited): 1609.01588 v2 `apj_nonsphericalpbh.tex`, 1707.03595 v4
`Spin_PBH.tex`, 2211.13950 v3 `MD_threshold10.tex`, 2507.18312 v3 `Main.tex`, 2508.10070 v1
`main.tex`; 2609.14218 v1 `MDPBH.tex` (wave 1: 837-918, 1076-1146; wave 2: 480-983, the
LTB section in full). Fetched with `harness/bin/nrpic-fetch-arxiv`; nothing from them is
committed (the figure of 1707.03595 was decoded for viewing into `scratch/`, not committed).

## How to rerun

```
cd tracks/A-emd-pbh/criteria
export OMP_NUM_THREADS=1
PY=../../../.venv/bin/python        # worktree environment (harness/bin/nrpic-env create --no-kokkos)
$PY predict.py --delta 0.1 --e 0.1 --p 0 --sigv 0 --aend 100 --sigmaH 0.01   # < 1 s
$PY predict.py --mu 0.05 --e 0.2 --feed mean --aend 39.7   # amplitude of 2609.14218, mean measure
$PY check_criteria.py            # 44 checks + 5 diagnostics, about 15 min (T5.3 dominates)
$PY check_criteria.py --only 2   # 1707.03595 only, a few minutes
$PY scan_disagreement.py         # about 5 s
$PY check_criteria2.py           # A1-A5, L1-L5 and two figures, about 2 min
$PY -m pytest -q -p no:cacheprovider test_criteria2.py   # about 1 min
$PY scouting_table.py            # tables for SR-1, S1, S2, a few seconds
```

numpy 2.2, scipy 1.15, matplotlib 3.10, mpmath 1.3; figure style `python/nrpic/figstyle.py`;
`ltb2609.py` imports `../expball/expball` (read only). Each script registers its run; `--out
DIR` (check_criteria2, scouting_table) writes without registering.

## Parameters of the table (conventions shared by all rows)

* Amplitude (wave 2): `--delta X --measure central|mean` or `--mu X` (amplitude of
  2609.14218, MDPBH.tex:839); `--amp-profile gauss2609|tophat` sets the conversion and
  `--feed central|mean` which measure the rows receive (default central, as in wave 1); the
  header prints every measure. The log-normal width of 2211.13950 is now `--mu-ln` (it was
  `--mu` in wave 1). See "Amplitude measures" below.
* `--delta`: linear growing-mode density contrast of the region extrapolated to its horizon
  entry, a(t_H) q = 1/H(t_H), M = R_H/2. All five papers define their amplitude this way
  (1609.01588:438,478,495,611; 1707.03595:761,1255-1258; 2211.13950:275,342;
  2507.18312:171,184-187,302; 2508.10070:250,322-325) [VERIFIED]. Using one number for the
  ball's uniform contrast, the top hat's delta_m and the peak height of 2508.10070 is
  [JUDGEMENT].
* `--e`, `--p`: ellipticity and prolateness of the deformation tensor at t_H,
  (alpha, beta, gamma) = delta/3 (1+3e+p, 1-2p, 1-3e+p), -e <= p <= e; the same mapping as
  2609.14218 MDPBH.tex:908 with k^2/(aH)^2 absorbed in delta.
* `--sigv` (3D rms at t_H, units of c) or `--sigv-ini` with `--HR-ini`: a velocity dispersion
  present from the start, carried by the adiabatic invariant sigma_v R = const
  (2211.13950:330-334); sigma_v,H = sigma_v,ini/(H R)_ini^2.
* `--aend` or `--efolds`: duration of the matter era after horizon entry, a_end/a_H.
* Statistical context, needed by rows R3, R8, R9: `--sigmaH` (rms density contrast at horizon
  entry on the PBH scale), `--zeta-rms` (default 5 sigma_H/2, from sigma^2 = (4/25)<zeta^2>,
  1609.01588:1165-1167), `--I` (1707.03595, default 1), `--mu`, `--lnkmin` (2211.13950,
  defaults 1, 1 as in its Fig. 2), `--A2` (2507.18312; default top hat), `--region ball|peak`
  (q of 1707.03595 from the region shape), `--npart`, `--noise poisson|lattice`.

## The rows of the table

| Row | Criterion | Formula and locator | Function |
|---|---|---|---|
| R1 | hoop + Zel'dovich, Lagrangian ball | h = (2/pi)(alpha-gamma)/alpha^2 E(sqrt(1-((alpha-beta)/(alpha-gamma))^2)) <~ 1, 1609.01588:596-607; pancake at a/a_H = 1/alpha, 537 | `hoop_h`, `hoop_threshold_delta` |
| R2 | hoop + Zel'dovich, peak ellipsoid of a monochromatic spectrum | (2/pi)(l1-l3)E(e)/l1^2 <~ l3^(1/3)/(l1 l2)^(1/6) sigma_h, e^2 = 1-((l1-l2)/(l1-l3))^2 l3/l2, 2508.10070:593-598 with 322-325; general form x_l <~ x_th, 309-331 | `hoop_peak_ratio`, `pancake_hoop_general` |
| R3 | Kerr bound on the tidal-torque spin | a*(1) = (2/5)sqrt(3/5) q delta^-1/2, a*(2) = (2/5) I sigma_H delta^-3/2, black hole iff a* <= 1, 1707.03595:904-960 | `spin_a1`, `spin_a2`, `spin_threshold` |
| R4 | finite duration | delta >= delta_fd = (t_H/t_end)^(2/3), 1707.03595:919-927 | `spin_threshold` |
| R5 | exact spherical top hat (LTB), unperturbed | R = (H0^2/2K) r (1-cos th), t = (H0^2/2K^(3/2))(th - sin th), K = 5 delta/(3 r_m^2), 2507.18312:211-214, 291-316 | `tophat_ltb`, `tophat_aBH` |
| R6 | dispersion: crossing time vs free fall | black hole iff sigma_v R < 3M, 2211.13950:330-359, 715 | `vd_collapse_adiabatic` |
| R7 | dispersion: virial halt radius | b_min = (5/3) s^2 r_max/(GM) < b_BH = 5 delta/3, 2507.18312:316, 517-520, 542 | `virial_bmin` |
| R8 | dispersion generated by small-scale power (log-normal spectrum) | delta > delta_th(sigma0, mu, k_min), 2211.13950:551-563 | `vd_delta_th` |
| R9 | profile flatness + zeta_rms perturbations | top hat zeta^(2/5); A2-profiles A2^(1/3) or zeta^(1/10), 2507.18312:336-339, 401-412; spin zeta^2/delta^(5/2), 630-631 | `profile_threshold`, `profile_spin_rms` |
| R10 | particle shot noise of a simulation (only with `--npart`) | b_min = 1.2 N^-1/3 (2507.18312:483-489), noise grown ~a to turnaround [JUDGEMENT extension] | in `predict.py` |

Assumptions of each paper, as stated there, are in the docstring of its section of
`emd_criteria.py`; the main ones: Newtonian EdS and the Zel'dovich approximation up to the
first caustic, hoop conjecture (1609.01588, 2508.10070); angular momentum frozen at maximum
expansion and the hypotheses |L1| ~ delta, |L2| ~ sigma delta (1707.03595:784-868); two well
separated scales and order-unity factors dropped (2211.13950:209-245, 375); LTB dust before
shell crossing and O(1) coefficients set to one (2507.18312:206-215, 585); Gaussian peaks,
first-order spin frozen at t_c (2508.10070:229-243, 482).

Example (run A-emd-pbh-20261115-120425-80492f8, `example_tables.txt`, abridged):

```
python3 predict.py --delta 0.1 --e 0.1 --sigmaH 0.01
R1  hoop ball            no   delta_th 0.821  a_f/a_H 23.1
R2  hoop peak ellipsoid  no   delta_th 0.926  a_f/a_H 23.1  spin 0
R3  Kerr bound           yes  delta_th 0.0252 a_f/a_H 10    spin 0.126
R5  exact top hat        yes                  a_f/a_H 16.7  spin 0
R6, R7 dispersion        yes (sigma_v = 0)
R8  2211 dispersion      yes  delta_th 0.0712
R9  2507 top hat         no   delta_th 0.229                spin 0.198
```

## Checks against the papers

Final run A-emd-pbh-20261115-115120-2eb3117 (`results.json`, figures `check_T1..T5`);
predictions and every outcome, failed ones included, in `JOURNAL.md`.

| Check | Paper value (locator) | This code | |
|---|---|---|---|
| T1.1 Doroshkevich normalisation | 1 (1609.01588:689-692) | 1.00000000 | pass |
| T1.2 E-bar; c in beta0 = c sigma^5; bounds | 1.182; 0.05556; 0.01338, 0.1280 (1341, 764, 771) | 1.1817; 0.05555; 0.01338, 0.1280 | c misses the last digit (E-bar precision) |
| T1.3 Khlopov-Polnarev | 0.02 chi^5 (931) | 0.0220 | pass |
| T1.4 exact beta0(sigma) | -> 0.05556 sigma^5, larger above 0.01 (740, 876-879) | ratio 1 + 6.75 sigma for sigma <= 1e-3; 2.02 at 0.1 | pass |
| T1.5 Monte Carlo of Gaussian tensors | same integral | 0.13966 +- 0.00017 vs 0.13964 at sigma = 1 (also 0.3, 0.5) | pass |
| T1.6 Fig. 1 of 1609.01588 (viewed) | curve | same shape and values | pass (visual) |
| T2.1-2.2 q_c, exponents, prefactors | 2.4; 0.1474, 0.004608; 1.921e-7, 3.244e-14 (72, 1338-1346) | 2.378; 0.1474, 0.004608; 1.921e-7, 3.248e-14 | last digit of 3.244e-14 needs E-bar = 1.182 exactly (T2.2e) |
| T2.3 spin distribution mode | 0.63 at sigma_H = 0.1; 1 below ~0.04 (1147-1150) | 0.636; 0.0405 | pass |
| T2.4-2.5 numerical vs semi-analytic beta0 with spin thresholds | "agree" for sigma <~ 0.005 / 0.04 (1351-1362, log plot) | 2nd order: ratio 1.41, 1.07, 1.015 at sigma = 1e-3, 1e-4, 1e-5; 1st order (q = sqrt2): 1.38 at 0.017, 0.66 at 0.0077, 0.40 at 0.006 | asymptote confirmed for 2nd order; 1st-order formula drifts at fixed delta_th (open) |
| T3.1-3.3 sigma_cr, merge point, jump condition | e^-3, (delta^-1/2, delta^2), jump iff mu L < 2 (496-498, 468, 569-571) | exact | pass |
| T3.4 Fig. 3 of 2211.13950 (viewed) | curves | all branches match, except that the paper does not draw the upper branch of (mu, L) = (1, 2), which its eq. 551-563 gives | see disagreement 8 |
| T4.1 exact top hat | R_max = 3 r_m/(5 delta), a_max = 1.06/delta, b_BH = 5 delta/3 (304, 308, 316) | relative error 1e-14; a_max delta = 1.0624 | pass |
| T4.2-4.3 | zeta(0) = 1.13 delta_m (188); a_rms ~ 0.01 at zeta = 0.1 (637) | 1.1326; 0.018 | pass (4.3 order of magnitude) |
| T5.1 general pancake criterion vs 1609 h for a spherical region | identical by construction | 2e-15 | pass |
| T5.2-5.3 monochromatic peaks: beta/sigma-bar^5, Mbar/M* | 1.08, 1.12, 1.51, 2.77, 0.67 and 14.7, 14.7, 14.7, 15.5, 18.1 (Tables, 612, 665); "19 times" (659) | 1.084, 1.122, 1.508, 2.769, 0.672 and 14.70, 14.70, 14.71, 15.45, 18.08; closed small-sigma form 1.0840, 19.5 times | pass |

## Where the criteria disagree over the brief's range

Range: the threshold surface of S1 deliverable 1 (amplitude x ellipticity x prolateness x
velocity dispersion, brief line 347) and the comparison of the minimum publishable unit with
2609.14218 and 1609.01588 (line 362): e in [0, 0.25] with p = 0 as in 2609.14218
(MDPBH.tex:966), p in [-e, e] as a band, delta in [0.01, 1], sigma_H = 0.003, 0.01, 0.03.
Numbers from run A-emd-pbh-20261115-120425-80492f8 (`scan_summary.json`, figures
`scan_criteria_overview`, `scan_verdict_map`).

1. **The hoop criterion against everything else.** R1 needs delta >= (36/pi) e E/(1+3e+p)^2:
   0.82 at e = 0.1 and 1.08 at e = 0.2 (p = 0). R3, R8, R9 do not depend on e and need only
   0.025, 0.071, 0.23 (sigma_H = 0.01). On the (delta, e) grid R1 and R3 disagree on 87, 70,
   56 percent of the points for sigma_H = 0.003, 0.01, 0.03; R1 and R8 on 59, 49, 41 percent;
   R1 and R9 on 35, 27, 19 percent. The hoop line is the only criterion that knows about e.
2. **Particles in full GR sit between them.** The particle threshold of 2609.14218 at e = 0.2
   (mu ~ 0.045, MDPBH.tex:1145, with a caveat on constraint violation, 1146-1150) maps to
   delta = 0.108 with that paper's own mapping (908, horizon entry at aH = k/sqrt6): ten times
   below R1 (1.08), above R3 (0.025) and R8 (0.071), below R9 (0.23). The mapping is
   the central measure (wave 2, A5: R1's delta_th = 12/5 hhat to 2e-16); in the mean measure
   the particle threshold is deltabar = 0.0397 and the hoop line 0.399.
3. **Shape of the region matters little.** Hoop for the peak ellipsoid (R2) against the ball
   (R1): thresholds differ by a factor 1.00-1.54 over e <= 0.25; verdicts differ on 0.9 percent
   of the grid. The amplitude means different things (peak height vs uniform contrast).
4. **Two dispersion thresholds with the same scaling.** R8 = e^(-0.4 mu L^2)(sigma0 e^-L)^(2/5)
   = 0.449 sigma_H^(2/5) (mu = L = 1) and R9 = zeta^(2/5) = 1.44 sigma_H^(2/5): a factor 3.2,
   disagreement on 25 percent of the log-delta range at every sigma_H. Both drop O(1) factors
   (2211.13950:375, 2507.18312:585), so only numerical runs can fix the coefficient.
5. **Primordial velocity dispersion.** With sigma_v R conserved, R6 allows formation for
   sigma_v,H < 1.5 and R7 for sigma_v,H < 0.548, a factor 2.7. On an initial slice with H R
   = (HR)_ini the critical dispersions are 1.5 (HR)^2 and 0.548 (HR)^2, e.g. 0.135 and 0.049
   at HR = 0.3: the scan of the brief's fourth axis lies exactly between them (example: delta
   = 0.1, e = 0.2, sigma_v,ini = 0.1 at HR 0.3: R6 forms, R7 does not).
6. **Duration.** Formation scale factor times delta: 3/(1+3e) (Zel'dovich pancake, R1, R2),
   1 (1707.03595's t_m, R3, R4), 1.686 (exact top hat at R = 2M, delta -> 0; 1.58 at delta =
   0.3). For a fixed a_end the required amplitude differs by up to a factor 3; the
   Zel'dovich collapse time of a sphere is 1.8 times the exact one.
7. **Spin.** At the same delta the per-region estimates are close: delta = 0.1, sigma_H = 0.01
   gives a*(2) = 0.13 (1707.03595) and zeta^2/delta^(5/2) = 0.20 (2507.18312); 2508.10070
   gives 0 when shape and tide are aligned and ~0.043 (sigma_H/6)^(1/2) = 0.002 for a narrow
   spectrum (Table, 510). The "near-extremal vs small" disagreement comes from where black
   holes form: 1707.03595 defines its threshold by a* = 1, so marginal black holes are
   extremal; 2507.18312 forms them at delta ~ zeta^(2/5) (top hat), where a ~ zeta; the hoop
   selects nearly isotropic tides with small torques (2508.10070:339-351). For the
   expanding-ball data with one uniform aligned deformation every criterion gives zero spin
   at first order: spin in an NRPIC run comes from particle noise or an added torque.
8. **2211.13950 equation vs figure.** For (mu, ln(kmin/k)) = (1, 2) eq. 551-563 has an upper
   branch from (0.0183, 0.0183) to (0.0498, 0.00248) that Fig. 3 does not draw. My reading of
   the non-formation triangle agrees with the equation [JUDGEMENT]; it matters only for
   sigma0 above sigma_cr.
9. **Shot noise of the simulations (R10, [JUDGEMENT] extension of 2507.18312:483-489).** With
   Poisson noise at H R = 0.3: N = 1e5 halts the collapse of delta = 0.03 (b_min 0.056 >
   b_BH 0.05); a lattice start (noise N^-2/3, 2507.18312:513) or N = 1e6 does not. Particle
   number and start matter most for the smallest amplitudes of the scan.

## Wave 2 (criteria2): amplitude measures, LTB profile, wave-1 failures, scouting tables

Predictions and outcomes in `JOURNAL.md` (wave 2). Runs: A-emd-pbh-20261115-161543-36e461d
(A1-A5, L1-L5; repeated with figure layout changes only as A-emd-pbh-20261115-162306-80396e4,
identical `results_criteria2.json`), A-emd-pbh-20261115-162524-d32d331 (pytest, 10 passed),
A-emd-pbh-20261115-162303-80396e4 (scouting tables), A-emd-pbh-20261115-161813-6c820fb (full
`check_criteria.py`), T2_REPEAT (`check_criteria.py --only 2` after the T2.6 fix). Failed run
on record: A-emd-pbh-20261115-161542-36e461d (a decimal-conversion fault of mine).

### Amplitude measures (SCOPE.md 10.1), `predict.amplitude_measures`, `convert_amplitude`

For ln Psi = (mu/2) exp(-k^2 r^2/6) [1 + ...e, p...] (MDPBH.tex:839), with the linear contrast
-(2/5) r_m^2 lap zeta at the horizon entry a H r_m = 1 (r_m = sqrt6/k, 709-714):

| measure | definition | value for 839 | at mu = 0.33 |
|---|---|---|---|
| mu | zeta(0) = 2 ln Psi(0) | mu | 0.33 |
| delta_c (central) | -(2/5) r_m^2 lap zeta(0) = alpha+beta+gamma of 907-908 | 12 mu/5 | 0.792 |
| deltabar (mean in r_m) | -(6/5) r_m zeta'(r_m) = linear compaction at r_m = delta_m of 2507.18312:194-205 | 12 mu/(5e) = 0.883 mu | 0.2914 |
| C_max (nonlinear) | (3/5)[1 - (1 + r zeta')^2] at r_m (695 with 2507:198-205) | deltabar (1 - mu/e) | 0.2560 |

delta_c/deltabar = e (Euler's number) for every e, p: the anisotropic part of 839 averages
to zero over every sphere and is traceless at the centre (A2: ball average and centre
eigenvalues on a quadrature grid, 3e-7 and 5e-6). R1 (hoop) is defined with the central
measure: 12/5 hhat(e, p) of MDPBH.tex:918 equals R1's delta_th to 2e-16 (A5); the hoop line
at e = 0.2 is mu = 0.4517, delta_c = 1.084, deltabar = 0.399. These are leading order in mu:
at mu = 0.5 the exact LTB central crunch is the linear top-hat time of delta_c times e^(3mu)
= 4.5 (L5), so for mu >~ 0.1 quote mu or C_max and use the exact LTB times of `ltb2609`.

### The LTB test profile of 2609.14218 (`ltb2609.py`)

Threshold statement, read at the source: mu = 0.33 is locally naked ("the singularity is hidden
by the event horizon from the asymptotic observers"), mu = 0.32 globally naked (MDPBH.tex:
766-768), with "PBH forms if the singularity is locally naked but not globally naked"
(752-753): mu_c in (0.32, 0.33] for e = p = 0, i.e. deltabar in (0.283, 0.291], delta_c in
(0.768, 0.792], C_max in (0.249, 0.256] [VERIFIED as read and as arithmetic]. It is a
statement about the causal structure (null geodesics from the central singularity), not
about an apparent horizon on a slice; the code here does not reproduce the null-geodesic
computation (open).

`LTBPeak2609(mu, Rm, H, cut)` is a profile of `expball.model.Ball` (attributes and methods of
`expball/model.py`): Delta(R) on the slice of simultaneous bang time from m(r) =
4 Psi^6/(3 t_i^2) (680) and ktilde(r) (695), tapered by a C-infinity step between cut[0] and
cut[1] r_m (compact support). Tests: expball's exact shells reproduce the paper's crunch time
t_s = (pi/3) m ktilde^(-3/2) (743) to 9e-16 and its R = r m^(1/3) t^(2/3) S(x) (593-619) to
3e-15 (L2, L3); the linear limit deviates by (17/21) Delta, the second-order coefficient of
spherical collapse (L1); no shell crossing before the central crunch (L5); the apparent
horizon emerges from the central singularity at t_s(0) = (108 pi/576) e^(3mu) mu^(-3/2) t_H.
**The expanding ball cannot hold the threshold amplitudes**: with H R_b <= 0.9 the central
shell is past turnaround on the slice above mu_max = 0.112 (r_m = R_b/2), 0.0435 (R_b/3),
0.0184 (R_b/4.5) (L4). The LTB threshold mu_c ~ 0.33 is therefore a test for the periodic box
(decision 0013), and the ball's LTB tests are exact-solution tests at mu <~ 0.04.

### The four failures of wave 1 (`check_criteria.py`)

| wave-1 check | outcome in wave 2 | evidence |
|---|---|---|
| T1.2b (0.05555 vs printed 0.05556) | explained: c = 0.0555549716 lies 2.8e-8 below the rounding boundary; the printed value is the two-step rounding (0.0555550 -> 0.05556). Check now "within one unit of the last printed digit"; the digit check kept as diagnostic T1.2b-d. The wave-1 note "E-bar = 1.18174" was a misprint: E-bar = 1.1816597 (mpmath agrees) | T1.2b, run -161813-6c820fb |
| T2.2d (3.248e-14 vs 3.244e-14) | explained: the ratio of the two printed prefactors of 1707.03595 (independent of E-bar) is off by 1.2e-3, three times the rounding; 1.921e-7 needs E-bar in [1.18163, 1.18176] (exact 1.18166), 3.244e-14 needs [1.18195, 1.18202] (contains 1.182). The paper used two values of E-bar; the code is right | T2.2e, T2.2f |
| T2.4a (2nd order, "within 20 %") | corrected: the paper's "agree" is visual on a figure of 30 decades; on the plotted window (sigma_H 2.5e-4 to 0.005) the ratio rises monotonically from 1.14 to 3.04, max |log10| 0.48 <= 0.5, and tends to 1 as sigma_H -> 0 (T2.5a) | T2.4a, `check_T2_ratios_1707.03595` |
| T2.4c (1st order, "within 20 %") | corrected likewise: plotted window 0.019-0.04, ratio 1.45-2.32, max |log10| 0.37. Cause of the drift at smaller sigma_H demonstrated (T2.6): the dropped (2u^2 + 3/2)/s3^2 in A (1919); plus a constant factor ~1.55 of the closed form. The root t_{1,2}(u) printed at 1880-1886 misses a factor pi in the denominator (typo; derivation and the paper's own limit 1921) | T2.6a-d, T2_REPEAT |

### Prediction tables of the first scouting runs (`scouting_table.py`, run -162303-80396e4)

Full tables in `scratch/A-emd-pbh/A-emd-pbh-20261115-162303-80396e4/scouting_predictions.md`.

* **SR-1** (data set 2t): core delta_H = 0.02015 (top hat; compaction maximum of the data set
  0.0377 at R = 3.63 M, outside the core). R5 equals expball's exact times to 2e-16
  (turnaround 16.894, core edge trapped 44.381, crunch 44.454). Planned end 44.37: the first
  trapped sphere (44.349, smoothing region) is before it, the core edge just after. R1/R2
  (Zel'dovich sphere) collapse at tau = 120 (a/a_H = 149), after the end; R4, R6, R7 yes;
  R3, R8, R9 need statistics (n/a); R10 (lattice noise) says the collapse halts, but in
  geodesic slicing particles at rest stay at rest, so R10 does not apply to SR-1 [JUDGEMENT].
* **S1** (mu = 0.5, e = 0.2, end 30 t_H): delta_c 1.2, deltabar 0.4415, C_max 0.360. R1 yes
  (central measure; first axis 1.95 t_H), R4 yes, R5 in the mean 6.07 t_H; LTB (e = 0) of the
  same mu: central crunch 7.47 t_H, above mu_c; 2609.14218 particles: horizon. Every
  deterministic row forms before the end.
* **S2** (mu = 0.03, e = 0.2, end 250 t_H): delta_c 0.072, deltabar 0.0265. R1 no (first axis
  133 t_H); top hat of r_m: R = 2M at 507 t_H (after the end); 2609.14218 particles: no
  horizon; LTB (e = 0): globally naked. But R4 says yes in both measures and the central rows
  put a central collapse inside the run (R5 central 112 t_H; LTB e = 0 central crunch
  124 t_H): the run should see something at the centre near 110-135 t_H (pancake or crunch)
  without a horizon by the other rows.

## Not done, open

* Inhomogeneity (1810.03490), spin loss by accretion (2306.11810, 2109.04896) and the peak
  theory spin of Saito et al. (cited in 2508.10070) are not implemented: not in this package.
* 2508.10070 for broad spectra (gamma < 1, nine-dimensional Monte Carlo) is not reproduced;
  only gamma = 1 (its Tables of mass and abundance) and the per-region criterion and spin
  formula (`pancake_hoop_general`, `spin_tidal_sq`); the table does not yet take a misaligned
  shape or torques as input.
* (closed in wave 2) the drift of the 1st-order semi-analytic formula of 1707.03595 (T2.6).
* The nakedness computation of 2609.14218 (most past null geodesic from the central
  singularity, 748-751) is not reproduced: mu_c in (0.32, 0.33] is read, not recomputed.
  `Profile2609.R` gives R(t, r) in closed form, so it is a short ODE job (wave 3).
* The amplitude measures are linear (leading order in mu); a nonlinear map between them for
  aspherical (e, p != 0) data is not attempted.
* No second agent has checked the wave-2 results yet (CLAUDE.md, models and roles).

## Requests

* **orch** (wave 2): `harness/bin/nrpic-run submit` refuses the shared worktree while other
  helpers hold uncommitted files ("the worktree is not clean", dry run at 2026-11-15T16:0xZ),
  so every run of this package was registered by hand with `runlog.py` (fields of the
  template plus status, gate, outputs.dir, launcher). Request: a cleanliness check limited to
  the package's paths and its inputs. Also: other helpers' path-limited commits of
  `tracks/A-emd-pbh/runs` swept one of my manifests into their commit (bfdd224); harmless,
  but a per-package runs directory or the lead as the only committer of runs/ would avoid it.
* **A-emd-pbh lead / periodic_threshold**: S2's plan says every criterion predicts no
  horizon by 250 t_H; the table says so for the hoop line, the top hat of r_m and the particle
  runs of 2609.14218, but R4 and the central-region rows (R5 central 112 t_H, exact LTB e = 0
  central crunch 124 t_H) put a central collapse inside the run: worth a snapshot output near
  110-140 t_H. For S1 at mu = 0.5 quote mu or C_max: the linear delta_c = 1.2 is outside every
  linear formula (R5 n/a).
* **A-emd-pbh lead / runs_ball**: SR-1's planned end 44.37 lies between the first trapped
  sphere (44.349) and the trapping of the core edge (44.381); the threshold measure of
  SCOPE.md section 3 for data set 2t is deltabar = 0.0377 (compaction maximum at R = 3.63 M),
  not the core's 0.0202.
* **orch** (wave 1, done by ruling 0013): `.gitignore` anchoring of `runs/`.
* **A-emd-pbh lead (A-pre-1, expball)**: state the initial data in the variables of this
  table (delta at horizon entry, e, p of the deformation at t_H, sigma_v and H R on the
  initial slice) so that every run gets its row of predictions; confirm or correct the
  mapping of 2609.14218's mu (point 2).
* **A-emd-pbh lead (A-pre-3) and core (Newtonian reference gravity, decision 0010)**: a test
  for the Newtonian mode that fixes the O(1) factors of points 4, 5, 9: a uniform sphere at
  rest with N particles (Poisson and lattice) and with an isotropic initial dispersion s_v;
  measure b_min = r_min/r_max. Reference: 2507.18312 eqs. at 483-489 (b_min = 1.2 N^-1/3),
  517-532 (b_min = (5/3) s_v^2 r_max/GM above, (N^-4/3 + s_v^2/(N delta))^(1/3) below).
* **kb**: ingest 1810.03490, 2306.11810 and the spin paper of Saito et al. (2024) so that the
  missing criteria can be added.
