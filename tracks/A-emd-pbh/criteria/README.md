# A-pre-2: the analytic criteria for black-hole formation in an early matter era, as code

Track A-emd-pbh, work package A-pre-2 (brief lines 715, 721: "the prediction table of
A-pre-2" is a G1 item). Five papers, each turned into functions with the locator of every
formula, a check against numbers or curves printed in the paper, and one command that prints
the predictions of all criteria for one set of initial-data parameters. State: done and
tested on processors; 0 card-hours used. Nothing here simulates: everything is a closed form,
a quadrature or a Monte Carlo over the papers' own probability laws (decision 0010 keeps such
reference solutions outside `athenak/src/`).

## Files

| File | What |
|---|---|
| `emd_criteria.py` | library: one section per paper, every function cites `<arXiv id>:<line>` of the TeX source in `kb-data/raw/arxiv/<id>/<version>/src` |
| `predict.py` | the prediction table for one parameter set (command below); `predict()` returns the rows |
| `check_criteria.py` | checks T1-T5 against the papers; writes `results.json` and figures `check_T*.{pdf,png}` |
| `scan_disagreement.py` | scan over the brief's range; figures `scan_*.{pdf,png}`, `scan_summary.json`, `example_tables.txt` |
| `runlog.py` | registers each run (`tracks/A-emd-pbh/runs/<run_id>/manifest.json`, outputs in `scratch/A-emd-pbh/<run_id>/`) |
| `JOURNAL.md` | predictions written before each run, outcomes after, failed ones included |

Sources (read in full where cited): 1609.01588 v2 `apj_nonsphericalpbh.tex`, 1707.03595 v4
`Spin_PBH.tex`, 2211.13950 v3 `MD_threshold10.tex`, 2507.18312 v3 `Main.tex`, 2508.10070 v1
`main.tex`; for the comparison point only, 2609.14218 v1 `MDPBH.tex` (lines 837-918,
1076-1146). Fetched with `harness/bin/nrpic-fetch-arxiv`; nothing from them is committed.

## How to rerun

```
cd tracks/A-emd-pbh/criteria
export OMP_NUM_THREADS=1
python3 predict.py --delta 0.1 --e 0.1 --p 0 --sigv 0 --aend 100 --sigmaH 0.01   # < 1 s
python3 check_criteria.py            # 35+2 checks, about 14 min on one core (T5.3 dominates)
python3 check_criteria.py --quick    # without the monochromatic integrals, about 1 min
python3 scan_disagreement.py         # about 5 s
```

System Python 3 with numpy 2.2, scipy 1.15, matplotlib 3.10; figure style
`python/nrpic/figstyle.py`.

## Parameters of the table (conventions shared by all rows)

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

Example (run A-emd-pbh-20261115-115232-bee5b2e, `example_tables.txt`, abridged):

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
Numbers from run A-emd-pbh-20261115-115232-bee5b2e (`scan_summary.json`, figures
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
   [TO VERIFY] against A-pre-1's definition of the initial amplitude.
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

## Not done, open

* Inhomogeneity (1810.03490), spin loss by accretion (2306.11810, 2109.04896) and the peak
  theory spin of Saito et al. (cited in 2508.10070) are not implemented: not in this package.
* 2508.10070 for broad spectra (gamma < 1, nine-dimensional Monte Carlo) is not reproduced;
  only gamma = 1 (its Tables of mass and abundance) and the per-region criterion and spin
  formula (`pancake_hoop_general`, `spin_tidal_sq`); the table does not yet take a misaligned
  shape or torques as input.
* The drift of the 1st-order semi-analytic formula of 1707.03595 at fixed delta_th (T2.5b) has
  a candidate cause, the dropped (3/2 + 2u^2)/s3^2 term in A, that is not demonstrated.
* No second agent has checked these results yet (CLAUDE.md, models and roles).

## Requests

* **orch**: `.gitignore` line `runs/` also matches `tracks/<ID>/runs/`, so run manifests are
  ignored; the manifests of this package were added with `git add -f`. Anchoring the pattern
  (`/runs/`) would make rule 4 and the ignore list consistent.
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
