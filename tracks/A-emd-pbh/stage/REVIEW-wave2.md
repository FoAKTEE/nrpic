# Lead's review of the wave-2 helper packages of A-emd-pbh

Lead of A-emd-pbh, wave 2, 2026-11-15. Checked from the artefacts (registered outputs,
figures, journals), not from the helpers' reports.

## 0. Predictions of the lead's checks (written before the checks ran)

Two kinds of check. (i) Reruns of each package's own analysis from its registered outputs
(reproducibility): predicted to reproduce every number of the registered analysis run
exactly (same inputs, processor arithmetic). (ii) Independent re-derivations by the lead's
own script `tracks/A-emd-pbh/analysis/review_wave2.py` (own readers, own estimators, own
cycloid; no helper analysis code). Predictions for (ii), with the helper's value and the
tolerance beyond which the helper's statement counts as NOT CONFIRMED:

Expanding ball (runs_ball; core = tracked particles with initial areal radius <= 2.35 M):
- B1 exact core: a cycloid with R_max/R_i = 1.339803 and turnaround 16.893769 after the
  slice implies a bang time 2/(3 H_i) = 10.667 M before the slice (to 5e-3 M), the
  start time of data set 2t; crunch 44.454 (to 2e-3).
- B2 SR-1 first non-finite record at t in [32.5, 33.5] (dx = M/2) and [29.8, 30.8]
  (dx = M); largest |H| at t = 2, 10, 20, 30 (dx = M/2) = 0.014, 0.042, 0.051, 0.48
  within 10 per cent.
- B3 SR-1 comoving: |r/r_0 - 1| < 1e-12 and |tau - t| < 1e-10 while finite (dx = M/2).
- B4 mean core turnaround error (own parabola through three records): SR-1 dx = M/2
  -0.022 +- 0.02 M; SR-2 dx = M/2 +0.043 +- 0.02 M; SR-1 dx = M -2.50 +- 0.3 M; SR-2
  dx = M -0.82 +- 0.15 M. Mean R_max error SR-1 dx = M/2 +7e-4 +- 5e-4.
- B5 largest core |R/R_exact - 1| at tau = 16.894: SR-1 dx = M/2 6.2e-3, SR-2 dx = M/2
  7.5e-3, each within a factor 1.5 (my core set stops at 2.35, theirs at 2.4).
- B6 SR-2 dx = M/2: |alpha_c/a - 1| > 0.1 first at t in [6.3, 6.9]; largest central
  lapse 1.85 +- 0.03 (t <= 20); the probe's proper time reaches the crunch 44.454 at
  t = 35 +- 2.
- B7 card cost per cell-step 6.3e-8 (SR-1) and 7.2e-8 (SR-2) at dx = M/2, to 5 per cent.
- B8 dx = M/4 (helper's prediction R, runs_ball/JOURNAL.md entry 4, which I test; my own
  expectation in brackets): R1 both finite to t = 20 [yes]; R2 |mean dtau_ta| <= 0.02 M
  in both gauges and largest core |eps| at tau = 16.9 below 2.5e-3 (SR-1) and 3e-3 (SR-2)
  [I expect R2 to hold for SR-1 and to fail for SR-2, whose core is disturbed by the lapse
  pulse before turnaround]; R3 SR-1 largest |H| at t = 20 below 0.051 [yes]; R4 SR-2
  pulse: |alpha_c/a - 1| > 0.1 first between t = 6.0 and 7.0, peak 1.8-1.9 [yes].

Periodic box (periodic_threshold), background time t/t_H = ((1 + tau/2)^2/6)^(3/2):
- P1 S1 first non-finite record at tau = 11.70 +- 0.02, i.e. 21.9 t_H.
- P2 S2 relative Hamiltonian constraint maximum first above 1e-2 at tau = 3.2, which I
  predict is 1.2 t_H, not the 1.5 t_H written in DESIGN.md and the journal; first above
  0.1 at tau = 14.1, which I predict is 35-36 t_H, not the "about 45 t_H" of DESIGN.md
  and the helper's report. Largest value 1.73 +- 0.01.
- P3 S1 relative constraint maximum at t = 0: 0.047 +- 0.003; central lapse alpha/a at
  the last finite record 0.14 +- 0.03.
- P4 S2: smallest lapse alpha_min/a >= 0.94; t_end = 250.9 t_H; 0.17 card-s per step.

Newtonian mode (newton):
- N1 the analytic cycloid of each sampled ball (G = 1, E = V0^2/2 - M/R0) equals the
  stored reference turnaround to 1e-9.
- N2 top-hat at 128^3 with particle spacing 0.025: t_ta error +7.2e-4 and R_max error
  +4.3e-4, each within 2e-4 with my quartic-vertex estimator; error ratio 64^3 to 128^3
  between 3 and 7 (second order).
- N3 energy error to the cycloid time of R = 0.25 R_max below 2e-4 at 128^3.
- N4 first collapse of the 128^3 scan cases from the minimum of the smallest eigenvalue
  of the second-moment tensor within 3e-3 of the stored reference (the helper's estimator
  gives 2.2e-4 to 1.5e-3; mine sees the softened minimum, hence the wider band).

Closed forms (criteria2, verifier C1c):
- C1 ball ceilings at R_b H_i = 0.9 with the mean contrast capped at 0.3: mu <= 0.0688
  (q = 2), 0.0306 (q = 3); start contrast 0.218 for mu = 0.05 and 1.96 for mu = 0.45
  (q = 2). So the verifier's C1c (WRONG) is confirmed if these hold.
- C2 exact LTB central crunch (108 pi/576) e^(3 mu) mu^(-3/2): 124 t_H at mu = 0.03 and
  7.47 t_H at mu = 0.5, the values the criteria2 tables use.

What refutes my review instead of the helpers: a disagreement in (i), which would mean
the registered analysis is not reproducible from its outputs.

## 1. What the lead ran (all registered with `harness/bin/nrpic-run`, processors, 2-4 cores)

| Run | What | Result |
|---|---|---|
| A-20261115-182021-6cb33de | own checks, first pass | parts B, P, C used; part N void: my reader ignored the time offset t0 of the Newtonian histories (my bug, fixed in 532a5f6) |
| A-20261115-182210-d1478a0 | own checks, second pass | all parts; the |H| panel of its figure hid values below 1 |
| A-20261115-182314-bebd0cf | own checks, third pass (the numbers quoted below) | `review_wave2.json`, `fig_review_wave2.png` (looked at) |
| A-20261115-182200-532a5f6 | rerun of runs_ball `compare.py`, SR-1/SR-2 at dx = M/2 and M | numbers JSON identical to A-emd-pbh-20261115-163659-4dbacd0 (all four labels) |
| A-20261115-182657-53da696 | analysis of the dx = M/4 runs and three-resolution summary (`after_m4.sh` commands) | new: prediction R outcome, `runs_ball/JOURNAL.md` entry 6 |
| A-20261115-182329-ad14d95 | rerun of `analyse_scouting.py` | my fault: `--out '$NRPIC_RUN_DIR'` unexpanded wrote into the worktree root; output moved into the run directory (`misplaced_output/`), superseded |
| A-20261115-182347-8ee3fcc | rerun of `analyse_scouting.py` | summary JSON and every PNG byte-identical to A-emd-pbh-20261115-171930-878a114 |
| A-20261115-182402-a46812c | rerun of `analyze_newton.py` and `gr_range.py` | `newton_tophat.csv`, `newton_scan.csv` (all cells but wall time), `gr_scan_range.csv` identical to -164420-4528861 / -164757-b8bc9a3 and to the committed tables |
| A-20261115-182502-dae304d | rerun of criteria2: `check_criteria2.py`, `scouting_table.py`, the T2 checks of `check_criteria.py`, pytest | results JSON identical (0 differences), T2 20 checks 0 failed as in -163358-9b2d048, table identical except its run-id line, 10 tests pass |
| A-20261115-182514-3bb6846 | rerun of the verifier's `verify_claims.py` | `verify.json` identical to A-20261115-161239-1c41333 |

Also closed: the two dx = M/4 card runs (`runreg.py finish`, commit 9290489). Reproducibility
check (i) of section 0 held for every package: no registered analysis failed to reproduce.

## 2. Outcome of the predictions of section 0 (own checks, run A-20261115-182314-bebd0cf)

| # | Prediction | Measured | Verdict |
|---|---|---|---|
| B1 | bang time 10.667, crunch 44.454 | 10.66666 (data: 10.66667), 44.4542 | holds: the exact numbers of 2t are a consistent cycloid |
| B2 | SR-1 non-finite at [32.5, 33.5] / [29.8, 30.8]; |H| 0.014, 0.042, 0.051, 0.48 | 33.125 / 30.75 (first non-finite cstat record); 0.0142, 0.0417, 0.0513, 0.477 | holds |
| B3 | SR-1 comoving | 8.2e-15, 6.3e-12 | holds |
| B4 | mean turnaround errors | SR-1 M/2 -0.0224 M, SR-2 M/2 +0.0434, SR-1 M -2.498, SR-2 M -0.818; R_max +6.7e-4 | holds |
| B5 | core |eps| at 16.894 | 6.22e-3 (SR-1), 7.49e-3 (SR-2) | holds |
| B6 | SR-2 pulse | > 0.1 at t = 6.625; peak 1.863 at 12.5; crunch proper time at t = 34.9 | holds |
| B7 | cost | 6.29e-8 and 7.22e-8 card-s per cell-step | holds |
| B8 | prediction R at M/4 | R1, R3, R4 hold; R2 holds for SR-1 and fails for SR-2 on the turnaround time (+0.031 M > 0.02) while its eps part holds (3.4e-4) | my bracketed guess (SR-2 eps fails) was wrong; the helper's R2 fails in its turnaround part |
| P1 | S1 non-finite tau = 11.70 | 11.709 (21.91 t_H) | holds |
| P2 | S2 H_r > 1e-2 at 1.2 t_H, > 0.1 at 35-36 t_H, max 1.73 | tau 3.242 = 1.23 t_H; tau 14.14 = 35.8 t_H; 1.7308 | holds: the helper's "1.5 t_H" and "45 t_H" are conversion errors (corrected) |
| P3 | S1 H_r(0) 0.047, alpha/a 0.14 | 0.0471, 0.136 | holds |
| P4 | S2 alpha_min/a >= 0.94, 250.9 t_H, 0.17 s | 0.943, 250.93, 0.172 | holds |
| N1 | cycloid = stored reference | identical (difference 0.0) | holds |
| N2 | 128^3 top-hat t_ta +7.2e-4, R_max +4.3e-4 | +7.18e-4, +4.19e-4; 64^3/128^3 ratio 4.4 | holds |
| N3 | energy < 2e-4 to t_0.25 | 9.5e-5 | holds |
| N4 | t_1 within 3e-3 | 1.6e-4 to 6.3e-4 (p = 0, +0.2), 1.49e-3 spindle, -4.8e-4 and -2.8e-4 for the 3.4e4-particle cases | holds |
| C1 | ceilings 0.0688 / 0.0306, start contrasts 0.218 / 1.96 | 0.06881, 0.03058, 0.2180, 1.962 | holds: verifier's C1c confirmed |
| C2 | LTB crunch 124 and 7.47 t_H | 124.04, 7.467 | holds |

## 3. Per package

### runs_ball (SR-1, SR-2; helper status "partial")

Confirmed [VERIFIED, own reader and exact rerun]: exact references of 2t; SR-1 comoving
coordinates and blow-up at t ~ 33 (dx = M/2) and ~ 30.5 (dx = M); |H| history; core
turnaround -0.13 per cent (SR-1) and +0.26 per cent (SR-2) at dx = M/2; core-shell errors;
the SR-2 lapse pulse (|alpha_c/a - 1| > 0.1 at t = 6.5-6.6, peak 1.80/1.86/1.87 at
dx = M, M/2, M/4: a property of the gauge); the core reaching its crunch proper time at
t ~ 35 in SR-2; no horizon in any run (the finder summaries are empty, the largest 2m/R on
the line is 0.34, `figs/sr2_n256_horizon.png` looked at); card cost.
New in this review (prediction R, entry 6): the core-shell radius at fixed proper time
converges between dx = M/2 and M/4 at apparent order 3.0 (SR-1) and 4.3 (SR-2) at
tau = 16.894, 3.2/3.1 at tau = 8 (lattice spacing tied to the mesh, domain [-32, 32]^3 at
M/4); the mean turnaround-time error falls from -0.0224 to -0.0125 M (SR-1) and from +0.043
to +0.031 M (SR-2), not a clean power law. Time orientation of the data (verifier C5,
limit 1): confirmed by evolution (the core expands and turns around at 16.87-16.94).
Not confirmed by the lead: the location of the SR-1 violation at dx = M/2 (rings at
r = 6-9 M, then 2.4 M; seen only at M/4, `figs/sr1_n256L32_fields.png`: rings at the core
edge at t = 16.9); "139 particles never trapped"; single-threaded processor executable;
the 3 per cent Misner-Sharp drift (open, TO VERIFY).
Wrong or defective: nothing numerical. Small defects: `figs/sr2_n256_horizon.png` has two
empty panels (no horizon); `sr1_n256L32_fields.png` draws a constant lapse with a
degenerate colour bar; label overlaps. Not fixed (cosmetic).
Large open items: (1) no slicing reaches the first horizon (SR-1 unstable, SR-2 pulse);
(2) data set 2t cannot test the horizon mass: its first horizon has areal radius 0.161 M
(below one cell of dx = M/2 in SR-2's coordinates); (3) the turnaround-time estimator
needs denser records near the maximum (traj_dcycle) before a G2 order is quoted.

### periodic_threshold (S1, S2, T1-T4; helper status "done")

Confirmed: design numbers by arithmetic (box 20/k = 8.165 r_m with r_m = sqrt6/k;
t_H/t_i = (6/0.2^2)^(3/2) = 1837.1); S1 blow-up at tau = 11.709 (21.9 t_H) with
alpha_c/a = 0.136 just before, H_r(0) = 0.047, 44 finder calls without a horizon; S2 to
250.9 t_H without a horizon, alpha_min/a >= 0.943, H_r maximum 1.73; cost 0.17 card-s per
step, 0.465 card-hours (exact rerun and own reader); the adaptive-refinement crash: read
in the source, `mesh_refinement.cpp:243` calls `pgen->user_ref_func`, which `nrpic_cf.cpp:392`
sets and `nrpic_cosmo.cpp` never sets [VERIFIED by reading]; the finder's puncture mass
0.9915211031 in both boundary conditions (`t2t3_results.json` of
A-emd-pbh-20261115-154250-527a6d1) equals docs/TESTLOG.md:462 (0.991521).
Figures looked at: `fig_scouting_histories.png`, `fig_t1_solve_change.png` (c = 0.36,
0.078, 0.004 at 32^3-128^3; 0.36, 0.078, 0.025 at eps_i = 0.2, 1, 2.45, as stated).
Wrong (fixed): "H_r max passed 0.01 at 1.5 t_H, 0.1 at about 45 t_H": 1.2 and 35.8 t_H
(DESIGN.md corrected, note appended to the package journal).
Not confirmed (not rerun; T1 took 42 min): T1/T1b solve changes beyond the figure, T2
constraint ratios on refined meshes, the CMC route (T4, T4b), the gradient-expansion
fractions. Seen in the histories figure, not explained in the package: S1 starts with
alpha/a ~ 0.8 near the peak (likely the initial lapse psi^-2 of the generator,
[JUDGEMENT]); after the blow-up the plotted H_r drops to 1e-12 (non-finite statistics
summed as zero), which a reader could misread.
Large open items: no slicing survives collapse in the box (S1); H_r above 0.1 on refined
levels before anything collapses (S2); no generator at the paper's start epoch or for
mu >= 0.5; adaptive refinement crashes; the finder does not wrap periodic coordinates.

### newton (Newtonian-mode scan design; helper status "done")

Confirmed [VERIFIED]: the cycloid reference of each sampled ball is the analytic cycloid of
its own (M, R0, V0); top-hat turnaround +7.2e-4 and R_max +4.2e-4 at 128^3 with 2.7e5
particles, second order (ratio 4.4 from 64^3), energy 9.5e-5; first-collapse times of the
128^3 scan within 1.6e-4 to 6.3e-4 (spindle 1.5e-3) by an estimator of my own; all tables
reproduced exactly; `fig_newton_scan_summary.png` and `fig_newton_gr_range.png` looked at
(hoop amplitudes on the ellipsoid line; a 1.5 R_L ball holds the hoop line only for
e <= 0.1).
Not confirmed: energy error at the crossing (P10(g), refuted by the helper, cause not
established) and after the third collapse; the 2.1e6-particle card points (not rerun
independently); the SR delay of 6-14 per cent (the figure shows 6-12.5 per cent for p = 0;
the 14 presumably from p != 0 rows, not checked).
Wrong: nothing. Cosmetic: y labels overlap tick labels in `fig_newton_scan_summary.png`.

### criteria2 (amplitude conversion, LTB profile, wave-1 failures; helper status "done")

Confirmed: exact rerun of every result (0 differences, 10 tests pass, T2 20 checks 0
failed); the source statements: mu_c in (0.32, 0.33] read at MDPBH.tex:766-768, particle
bracket at 1101-1103; the typo of arXiv:1707.03595 v4 Spin_PBH.tex:1880-1886 (denominator
3 delta_th must be 3 pi delta_th): the source's own limit t_2 ~ 12 E/(pi delta_th) at
1925-1926 follows only with pi [VERIFIED by algebra]; the LTB central-crunch formula gives
the tables' 124 and 7.47 t_H; delta_c/deltabar = e as in the verifier's C2.
Not confirmed independently: the L4 ball limits (mu_max 0.112, 0.0435, 0.0184) and the T2.6
decomposition (reproduced only). Wrong: nothing.

### note (working note v0, G0 package; helper status "done")

Confirmed: both disagreements it found in the lead's documents. The record of run
A-20261115-130257-a7374a4 is `KL_overshoot_near_edge = 0.0855` = max |KL_table - KL_exact|
in the band around the jump (`analysis/lead_crosscheck.py:105`), 1.37 H with H = 0.0625;
it includes the smeared jump, so "overshoot ~10 %" was not what the run measured
(SCOPE.md 10.3 and RISKS row 11 corrected; JOURNAL.md:94 and :101 are corrected in the
lead's journal entry of this session, the old lines stay). Gate items of the note are
judged in `G0/CHECKLIST.md`; `nrpic-stage verify` reruns the figure scripts.
Open: the note shows the wave-2 runs only qualitatively; the ledger has no verifier
recomputation.

### verifier (stage/G0/VERIFIER.md)

Reproduced exactly (run A-20261115-182514-3bb6846). What the track does with each finding:

| Finding | Lead's check | Action |
|---|---|---|
| C1c WRONG (ball holds the particle bracket at q = 2) | confirmed (C1 above) | SCOPE.md sections 4, 8 and 10.9(a), RISKS row 4 corrected; message to orch: the reason of decision 0013 should be corrected, the ruling can stand on the paper's own data |
| C4b WRONG (239 t_H for mu = 0.045) | confirmed at the source text (MDPBH.tex:1102-1103: no horizon for mu <= 0.045) | SCOPE.md section 2 and 10.9(b) corrected; H1 runs near the bracket go to 400 t_H (unchanged plan) |
| C4 label of delta_fd | confirmed: literal formula 0.0285, top-hat form 0.048 | SCOPE.md section 3 and 10.9(c) |
| C5 limit 1 (constraint test blind to K -> -K) | closed by evolution (SR-1/SR-2 core turns around at 16.87/16.94) | G1/STATUS.md T1 amended; SCOPE 10.9(e) |
| C7 caveat (source saw no monotonic horizon-mass convergence) | confirmed at main.tex:1484-1485 | RISKS row 17; G2 plan states that the mass target is "same order as 1e-3", not a convergence order |
| C8 model NOT CONFIRMED | now confirmed: 6.3e-8 / 7.2e-8 card-s per cell-step against 8.1e-8; periodic 1.3x the unit cost | G1/STATUS.md; SCOPE 10.7 stands |
| Weak point 1 (phase-1 path untested) | S1/S2 now test it and it fails (gauge, refined-level constraints, generator) | requests to core; RISKS rows 5, 20-22 |
| Weak point 2 (comparison on the run-length cutoff) | agreed | H1 runs to 400 t_H in the scan design; stated in STATUS |
| Weak point 3 (first horizon unresolved) | confirmed by SR-2 (no horizon, 2m/R <= 0.34) | new ball data set with R_AH of several M for the G2 horizon test (next action 2) |

## 4. Card-hours

Wave 2 used 1.115 card-hours (`nrpic-run budget`: G2 0.95; 0.17 on the Newtonian card run
without a gate): runs_ball 0.480 (SR-1/SR-2 at M/2 0.253, at M 0.028, at M/4 0.199),
periodic 0.466, newton 0.169. The lead's checks used processors only.
