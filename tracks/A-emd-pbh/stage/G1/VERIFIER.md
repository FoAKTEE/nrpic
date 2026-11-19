# VERIFIER.md: independent verification for gate G1 of A-emd-pbh (checklist item C18)

Verifier of wave 2b, fresh context, 2026-11-19. Report name per decision 0016 item 1.
Sections 1-3 were written and committed before I read the track's own review
(`stage/REVIEW-wave2.md`, `stage/G1/REVIEW.md`, `STATUS.md`, `HANDOFF.md`, the journals);
section 4 compares afterwards.

**What I read first.** CLAUDE.md; CHARTER.md to "Owners"; decisions 0010, 0016; the brief at
S1 (335-365) and the track sheet (708-725); `stage/G1/CHECKLIST.md` (to know what C11 and C18
ask); the working note `note/main.tex` with `tables/ledger.tex`, `parameters.tex`; the READMEs
of `note/`, `criteria/`, `newton/`, `runs_ball/` and `newton/SCAN.md` section 7 (for the
claims); the paper sources at the locators the note and the criteria cite; the formats of
the raw files (`coord/INTERFACES/diagnostics.md` section 6). I read the track's code only to
find where a raw number comes from or, after a disagreement, which estimator it used; each
such case is named below.

**How.** Four scripts of my own under `verifier/` (`v_ledger.py`, `v_criteria.py`,
`v_newton.py`, `v_ball.py`, shared helpers `vcommon.py`, driver `run_all.py`); they import
nothing of the track, only the figure style `python/nrpic/figstyle.py`. They read the raw
outputs (AthenaK histories and trajectories, the data-set table, JSON outputs of the track's
runs), check each file against its run's `sha256sums.txt` where one exists, and compute the
references themselves: formulas coded from the paper sources, the exact LTB/cycloid solution
of data set 2t rebuilt from its radial table alone, the cycloid and the cold homogeneous
ellipsoid (Carlson R_D) for the Newtonian runs, areal radius and proper time of every tracked
particle from `ball.traj.bin`/`ball.trajmet.bin`. Predictions were committed before any of my
code ran (`JOURNAL.md` entry 1, commit 2256c86); outcomes in entry 2.

**Registered run:** A-20261119-142905-c813c01 (`nrpic-run submit --package stage/G1
--package note/scripts`, commit c813c01, 4 cores, exit 0). Outputs:
`scratch/A-emd-pbh/A-20261119-142905-c813c01/{ledger,criteria,newton,ball,schem}/`, each with
a JSON of rows (item, claim, mine, verdict, how) and figures; PNG copies in `figs/`.
Rerun: `harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 4 --package
tracks/A-emd-pbh/stage/G1 --package tracks/A-emd-pbh/note/scripts --purpose "..." --
.venv/bin/python tracks/A-emd-pbh/stage/G1/verifier/run_all.py` (about 4 minutes).

Verdicts: CONFIRMED (my own number equals the claim at its printed precision, or within the
stated estimator spread), NOT CONFIRMED (not recomputed, or the evidence does not decide),
WRONG (my number or the source contradicts the claim as written).

## 1. Summary

| Area | Items | CONFIRMED | NOT CONFIRMED | WRONG |
|---|---|---|---|---|
| Ledger of the note (Table VI) and parameter table (Table V) | 42 | 39 | 1 | 2 |
| Analytic criteria (criteria/) | 19 | 19 | 0 | 0 |
| Newtonian mode (newton/) | 17 | 17 | 0 | 0 |
| Expanding ball, wave 2 (runs_ball/) | 12 | 12 | 0 | 0 |
| Statements in the note's text (section 2.5) | 17 | 15 | 0 | 2 |

Every number of the ledger that comes from a computation was recomputed, except the predicted
card-hours of the scouting runs (a cost model). The numbers are right. What is wrong is how
some of them are labelled or stated:

1. **WRONG (label).** Ledger row "read-off collapse time over top-hat time at r_m, mu <= 0.15
   (range; median) 0.80-1.01; 0.86": the range is over mu <= 0.15, but 0.86 is the median over
   all six read-offs (0.8646, including mu = 0.3 with ratio 1.49). Over mu <= 0.15 the median
   is 0.843. Source of the 0.86: `scope_numbers.json` key `median_ratio` of run
   A-20261115-130252-7877b7a.
2. **WRONG (statement).** Note Sec. III A: the scouting data have "a common bang time for every
   shell". True inside the surface taper (|t_bang - t_i| <= 5e-8 for R < 6.5); in the taper
   (6.5 <= R < 9.43) the shells have E = 0 but less mass, so their bang times run from 10.667
   to 13.588 (a decaying mode in the taper). Harmless for the core tests, but the sentence is
   not true as written.
3. **Label defect (values right in code units).** Table V row 1 calls the total Misner-Sharp
   mass M = 1.0096, then quotes R_b/M = 8, HM = 0.0625, t_i/M = 10.667, and Table VI quotes
   tau/M, R_i/M, m_AH/M: all of these are in code units (nominal mass 1). In units of the
   total mass, m_AH/M = 0.0797 (first trapped sphere) and 0.0951 (at the crunch), tau_ta/M =
   16.73. A one-per-cent ambiguity; counted CONFIRMED in the table below with this remark.
4. **Label defect.** Ledger row "threshold delta_c at e = 0.2: hoop, ball, hoop, peak,
   profile, dispersion, spin, duration" has eight names for six values; read "hoop (ball),
   hoop (peak), profile, dispersion, spin, duration".
5. **Stale, not wrong.** The note quotes the wave-1 criteria state (33 of 37 checks, four
   failures); in wave 2 all four were explained or corrected and the current state is 41 of
   41 (plus 4 diagnostics), which I confirm. The note's Sec. V still describes the first
   full-relativity runs as queued and the Newtonian runs as under way; both are done and are
   verified here (sections 2.3, 2.4).
6. **Estimator dependence (runs_ball).** The SR-2 turnaround errors (+0.043 M at M/2, +0.031 M
   at M/4) are reproduced only with a three-point vertex of R(tau); with fit windows of
   +-2, 3, 5 output records the M/4 value is +0.0245, +0.0156, +0.0088, and at M/2 the median
   over core shells is negative (-0.12 to -0.005) while the mean is positive. The SR-1 values
   do not depend on the window. Conclusions resting on the SR-2 turnaround number (that it
   "fails R2's bound") are not robust (section 3, point 1).
7. **Integrity of wave-1 outputs.** The wave-1 runs behind 18 ledger rows (criteria scan,
   checks, constraint convergence, the data-set table) wrote no `sha256sums.txt` and their
   hand-written manifests record no output checksums, so nothing guarantees those files are
   the ones the runs wrote. Mitigation: my reconstruction of the data-set table reproduces its
   own header (M) and the initial metric that four AthenaK runs reconstructed at 1705-1898
   particles (to 6e-6 at M/2, 6e-7 at M/4), and the criteria numbers equal my own closed forms.
   The note's sentence "the outputs of each run are checked against the checksums the run
   recorded" holds only for the runs that recorded them (`note/scripts/common.py` logs "no
   sha256sums.txt (wave-1 run)" and continues).

## 2. Item by item

### 2.1 Ledger of the note (note/tables/ledger.tex) and the parameter table

Run A-20261119-142905-c813c01, `ledger/ledger.json`; figure `figs/fig_v_ledger.png`
(top left h-hat(e,0) against the read-offs; top right read-off collapse times against my
top-hat time of r_m, grey lines mu_fd; bottom left tau_AH(R_i) and tau_c(R_i) with the first
trapped sphere; bottom right the largest coordinate speed of light in geodesic slicing).

| Ledger row | Claim | Mine | Verdict | How |
|---|---|---|---|---|
| locators MDPBH.tex 907-908, 918, 1101-1103, 765-768 | as cited | found at 908, 918, 1102-1103, 766-768 | CONFIRMED | read in kb-data/raw/arxiv/2609.14218/v1/src |
| hhat(0.2,0) | 0.452 | 0.451747 | CONFIRMED | MDPBH.tex:918 coded here (scipy ellipe with m = k^2) |
| largest deviation of hhat from read-offs | 0.0025 | 0.00254 | CONFIRMED | read-offs of the track; the figure hcont.pdf of the paper, rendered and looked at, is consistent with them at reading accuracy |
| mu_fd for t_end = 100, 250, 400, 1000 t_H | 0.089, 0.048, 0.035, 0.019 | 0.08866, 0.04813, 0.03518, 0.01910 | CONFIRMED | (5e/12)(3/20)(12 pi)^(2/3)(t_end/t_H)^(-2/3) |
| slope of read-off collapse times | -1.31 | -1.3123 (mu <= 0.15; all six -1.166) | CONFIRMED | log-log fit; read-offs consistent with alpha.pdf of the paper (looked at) |
| ratio read-off/top hat, mu <= 0.15: range | 0.80-1.01 | 0.802-1.012 | CONFIRMED | my top-hat times equal the track's to 3e-16 |
| same: median | 0.86 | 0.843 (mu <= 0.15); 0.865 over all six | WRONG | finding 1 |
| largest mu in the ball, R_b H_i = 0.9, q = 2, 3, 4 (mean 0.3) | 0.069, 0.031, 0.017 | 0.0688, 0.0306, 0.0172 | CONFIRMED | a_i/a_H = (q/0.9)^2 |
| same, central contrast <= 0.3 | 0.0253, 0.0113, 0.0063 | 0.02531, 0.01125, 0.00633 | CONFIRMED | |
| critical dispersion: virial halt; crossing | 0.55; 1.5 | 0.5477; 1.5 | CONFIRMED | derived here: b_min = (5/3)s^2 r_max/GM (2507.18312:542), b_BH = 5 delta/3 (316), sigma_v R conserved -> sigma_H^2 < 3/10; sigma_v R < 3M (2211.13950:715) -> sigma_H < 3/2 |
| measured cost of the two-overdensity run | 5.41; 0.761 | 5.4099; 0.7608 | CONFIRMED | 13 segment logs of runs/jeans/n1e4_v19 (untracked, no checksums), final cycle 25600 from events.log |
| modelled cost per run (range; median at 1e6) | 1.1-3.5; 2.4 | 1.111-3.540; 2.387 | CONFIRMED | arithmetic over the model rows; the cost model itself not re-derived |
| first scan: runs; card-hours | 65; 155 | 65 x 2.387 = 155.2 | CONFIRMED | 65 taken from SCOPE.md section 5 |
| thresholds at e = 0.2 (six criteria) | 1.08, 1.45, 0.229, 0.0712, 0.0252, 0.01 | 1.084, 1.452, 0.2287, 0.07121, 0.0252, 0.01 | CONFIRMED | my code from the sources (section 2.2); label defect, finding 4 |
| particle threshold of 2609.14218 in delta_c | 0.108 | 12/5 x 0.045 = 0.108 | CONFIRMED | 0.045 is the largest mu without a horizon (MDPBH.tex:1103): the bracket is (0.108, 0.120] |
| checks: passed of total; failing | 33 of 37; T1.2b, T2.2d, T2.4a, T2.4c | same, in both wave-1 runs | CONFIRMED | stale, finding 5 |
| order of norm(M), flat ball, smooth, p = 2; 4 | 2.00; 4.00 | 2.000; 4.000 | CONFIRMED | log2 of norm ratios, N = 128 -> 256, convergence.json of A-emd-pbh-20261115-130402-f5566fb |
| order of norm(M), tapered edge, all cells, p = 2; 4 | 1.99; 3.90 | 1.990; 3.896 | CONFIRMED | same (pairs before: 1.85, 1.96; 3.43, 3.77) |
| order of norm(H); norm(M), top hat, smooth, p = 4 | 4.00; 4.00 | 4.001; 3.999 | CONFIRMED | same |
| order of norm(M), top hat, all cells, p = 4 | -0.50 | -0.504 | CONFIRMED | same |
| order of norm(H); norm(M), smoothed top hat, 256 -> 512 | 3.98; 3.94 | 3.978; 3.939 | CONFIRMED | A-emd-pbh-20261115-122117-aa1c84d |
| two generators; two table evaluators; three exact codes; exterior K | 4.8e-15; 6.9e-18; 1.1e-14; 4.3e-15 | 4.77e-15; 6.94e-18; 1.07e-14; 4.33e-15 | CONFIRMED (transcription) | read from crosscheck.json (checksum ok); not re-run. My own check on data set 2t: K^R_R = -dv/dR holds to 1.6e-11 over the table |
| total M; rest mass | 1.00959; 1.01590 | 1.00959; 1.01590 | CONFIRMED | from the table alone: R = psi^2 rbar, 1+2E = (dR/drbar)^2/psi^4, v = -KT R, m = R(v^2-2E)/2; rest mass = int m'/sqrt(1+2E) |
| core turnaround tau_ta; R_max/R_i | 16.894; 1.3398 | 16.8938; 1.33980 | CONFIRMED | my cycloid per shell; spread over core shells 2e-8 |
| first trapped sphere tau_AH; R_i; m_AH; 2 m_AH | 44.349; 2.742; 0.0805; 0.161 | 44.3493; 2.7418; 0.08051; 0.1610 | CONFIRMED | minimum of tau_AH(R_i), parabola; code units (finding 3) |
| core edge trapped; core crunch | 44.381; 44.454 | 44.3815; 44.4542 | CONFIRMED | |
| m_AH at the crunch | 0.0960 | 0.09602 | CONFIRMED | outermost shell with tau_AH <= tau_c; code units |
| conformal-time coordinate times | 13.82, 49.51, 54.96 | 13.823, 49.506, 54.964 | CONFIRMED | alpha = a/a_i in the core, t = R_i (eta - eta_i)/sqrt(-2E) |
| geodesic slicing reaches the step bound at cfl 0.25 | 42.30 | 42.36 (all shells), 42.38 (core) | CONFIRMED | C_max = 0.618 taken from the track; the track's speed R_i/R omits 1/psi^2, hence 0.06 |
| predicted card-hours of the two scouting runs | 0.15; 0.16 | not recomputed | NOT CONFIRMED | cost model only |
| parameters: psi at the centre; largest 2m/R | 1.0138; 0.236 | 1.01384; 0.2361 (at R = 8.26) | CONFIRMED | |
| parameters: H R_b; R_b; H; t_i; core contrast | 0.5; 8; 0.0625; 10.667; 1 | 0.500; 8; 0.0625; 10.667; 1.0000 | CONFIRMED | units: finding 3 |
| common bang time (R < 6.5) | t_i for every shell | 4.7e-8 | CONFIRMED | |
| common bang time (taper) | t_i for every shell | 10.667 to 13.588 | WRONG | finding 2 |

Not recomputed: the parameter-table rows of the outcome rule (design constants, nothing to
compute), "particle lattice spacing 0.5" and "edge taper half width 1.5; matter edge 9.5"
(taken from the data-set JSON; my table gives the matter edge at rbar = 9.43 with a
threshold of 1e-6 of the largest m'), and the claims sentence ("68 numbers ... two
differences"), which checks the lead's documents and is outside C18.

### 2.2 Analytic criteria (criteria/)

`criteria/criteria.json`, `figs/fig_v_criteria.png` (left: my R1, R2 against e with the
track's points, horizontal R3, R4, R8, R9, star the particle result; right: the integrand
of Ebar^-5 of 1609.01588:766).

| Item | Claim | Mine | Verdict |
|---|---|---|---|
| wave-1 tallies (-115120-2eb3117, -130256-a7374a4) | 37 checks, failing T1.2b, T2.2d, T2.4a, T2.4c | the same | CONFIRMED |
| wave-2 full run -161813-6c820fb | 40 checks, T2.6a-c failed, 4 diagnostics | the same | CONFIRMED |
| wave-2 T2 rerun -163358-9b2d048 | 17 checks, 0 failed | the same | CONFIRMED |
| current state | 41 pass, 4 diagnostics | 41 of 41 | CONFIRMED |
| printed values at 1609:764, 771, 1341 and 1707:1338-1346 | 0.05556; 0.01338, 0.1280; 1.182; 1.921e-7, 0.1474, 3.244e-14, 0.004608 | all found at those lines | CONFIRMED |
| T1.2: Ebar; c | 1.1817; 0.05555 vs paper 0.05556 | 1.1816597; 0.0555549716 | CONFIRMED (the code is right, the paper's last digit is a double rounding) |
| T2.2: prefactors | 1.921e-7; 3.244e-14 | 1.9213e-7; 3.2484e-14, and 3.2437e-14 with Ebar = 1.182 | CONFIRMED (the paper used Ebar = 1.182 for the second) |
| T3.1 sigma_cr | e^-3 | 0.049787 | CONFIRMED |
| T4.1 top hat | a_max delta = 1.06; R_max = 3 r_m/(5 delta) | 1.06241; 0.60000/delta (my cycloid from growing-mode data) | CONFIRMED |
| R1, R2 at e = 0, 0.1, 0.2 | 0, 0.821, 1.084; 0, 0.926, 1.452 | identical to 1e-16 | CONFIRMED |
| R2/R1 over e (p = 0) | 1.0022-1.5429 | the same on the track's 126-point grid | CONFIRMED (lower end = first grid point) |
| R5 a/a_H at R = 2M and turnaround (delta = 0.1, 0.3, 0.03) | 16.69, 10.62; 5.276, 3.541; 56.13, 35.41 | 16.693, 10.624; 5.276, 3.541; 56.125, 35.414 | CONFIRMED |
| R3, R4, R8, R9 (sigma_H = 0.01) | 0.0252, 0.01, 0.0712, 0.229 | the same | CONFIRMED |
| R6, R7 critical sigma_v,H | 1.5; 0.548 | 1.5; 0.5477 | CONFIRMED |
| spins at delta = 0.1 | 0.126; 0.198 | 0.1265; 0.1976 | CONFIRMED |
| amplitude measures | delta_c = 12 mu/5; deltabar = 12 mu/(5e) | 2.4 mu; 0.88291 mu by quadrature of the linear contrast over the ball r_m | CONFIRMED (also by hand: lap zeta(0) = -mu k^2, r_m zeta'(r_m) = -2 mu/e) |
| particle bracket and hoop line in the mean measure | 0.0397; 0.399 | 0.0397; 0.3989 | CONFIRMED |
| C_max at mu = 0.32, 0.33, 0.5 | 0.2493, 0.2560, 0.3603 | the same | CONFIRMED |

Not recomputed: T1.3-T1.6, T2.1, T2.3-T2.6, T3.2-T3.4, T4.2-T4.3, T5.1-T5.3 (Monte Carlo
and figure comparisons), the LTB checks L1-L5 and the scouting tables. Their tallies are
confirmed, not their values.

### 2.3 Newtonian mode (newton/, wave 2)

`newton/newton.json`, `newton_recomputed.json`; figures `figs/fig_v_newton.png` (left:
top-hat errors against my cycloid for three meshes and the card run; right: semi-axes of the
e = 0.2 run against my ellipsoid) and `figs/fig_v_newton_scan.png`. All 52 input files
(histories, ball.json) checksum-verified. Code time + t0 = cosmic time; relative errors of
times are taken against the cosmic time of the reference, as the track does.

| Item | Claim | Mine | Verdict |
|---|---|---|---|
| top hat 128^3, 2.7e5: t_ta; R_max; t(R = R_max/4); softened collapse | +7.16e-4; +4.31e-4; +8.39e-4; +2.59e-4 | +7.18e-4; +4.19e-4; +8.19e-4; +2.66e-4 | CONFIRMED (differences 1e-5 to 2e-5: my vertex and 0.25 of the measured, not the reference, R_max) |
| top-hat convergence factors | 4.0-6.1 per doubling | 4.6, 4.4; 4.6, 4.4; 5.2, 4.6; 6.1, 4.0 | CONFIRMED |
| 2.1e6 vs 2.7e5 particles | 1e-5 | 1.2e-5 | CONFIRMED |
| top-hat energy | 9.5e-5 | 9.50e-5 with norm |W_0| up to t(R_max/4); 2.2e-4 relative to |E_0| | CONFIRMED (normalisation taken from the track's docstring after my first value differed) |
| first collapse along the predicted axis | 14 of 14 | 14 of 14 | CONFIRMED |
| t_1, e = 0.05-0.3 | +2.2e-4 to +6.3e-4 | +1.6e-4 to +6.3e-4 | CONFIRMED (the e = 0.05 point differs by 1.3e-4: vertex window) |
| t_1 of the spindle | +1.5e-3 | +1.49e-3 | CONFIRMED |
| other semi-axes; hoop ratio at t_1 | within 1.2e-3; 6.1e-4 | 1.2e-3; 6.1e-4 at the reference t_1 (the track's choice, from its docstring); 1.5e-3; 8.6e-4 of opposite sign at the measured t_1 | CONFIRMED |
| hoop amplitudes h_1 delta_L | 0.3597, 0.5925, 0.8547, 0.9685, 0.9194, 0.8636 | identical | CONFIRMED |
| my ellipsoid vs the track's reference t_1 | same | 3e-9 | CONFIRMED |
| three amplitudes agree | 5e-7 | 1e-7 | CONFIRMED |
| controls: 64^3 (e = 0.1, 0.2); rotated lattice | +8.8e-4, +1.5e-3; +3.7e-4 | +8.58e-4, +1.52e-3; +3.68e-4 | CONFIRMED |
| card e = 0.2, 2.1e6 particles | +3.7e-4, 9e-6 from 2.7e5 | +3.73e-4, 8.7e-6 | CONFIRMED |
| second collapse t_2 | +3.1e-4, +4.0e-4, +5.6e-4 | +2.7e-4, +3.7e-4, +5.4e-4 | CONFIRMED |
| energy to 0.9 t_1; at the crossing; spindle | <= 1.9e-4; 1.1e-3 to 9.3e-3; 3.0e-2 | 9.3e-5; 1.1e-3 to 9.3e-3; 3.0e-2 (norm |W_0|) | CONFIRMED |

Not recomputed: the full-relativity range of SCAN.md section 8 (`gr_range.py`: seeds, SR
delay, resolution), the cost per cycle, and the 64^3/h050 rows beyond t_1.

### 2.4 Expanding ball, wave 2 (runs_ball/)

`ball/ball.json`, `ball_recomputed.json`; figure `figs/fig_v_ball.png` (left, middle: largest
core error |R/R_exact - 1| against proper time for SR-1 and SR-2 at dx = M, M/2, M/4, grey
line tau_ta; right: core shells of SR-1 at M/2 against my cycloids). 18 trajectory and history
files checksum-verified. My proper time int alpha/W dt over the output records agrees with
the code's own column to 1e-14 (SR-1) and 0.5-2.8e-3 (SR-2, trapezoid on sparse records);
I use the code's column for SR-2. The initial areal radii from the reconstructed metric
agree with psi^2 rbar of the table to 1e-4 (M), 7e-6 (M/2), 6e-7 (M/4).

| Item | Claim | Mine | Verdict |
|---|---|---|---|
| SR-1 breakdown at dx = M/2; M | t = 33.0; 30.3 | first non-positive metric determinant 32.875; 30.25 (athena.log); norm(H) > 1e10 at 33.0; 30.5 | CONFIRMED |
| SR-1 M/2: mean turnaround error; R_max | -0.022 M; +0.07 % | -0.0224; +0.067 % | CONFIRMED (window-independent) |
| SR-2 M/2: mean turnaround error; R_max | +0.043 M; +0.10 % | +0.0434 (three-point vertex); +0.101 % | CONFIRMED, estimator-dependent (finding 6) |
| core max abs(R/R_ex - 1) at tau = 16.9, SR-1 M; M/2 | 5.6e-2; 6.2e-3 | 5.57e-2; 6.22e-3 | CONFIRMED |
| same, SR-2 M; M/2 | 2.1e-2; 7.5e-3 | 2.08e-2; 7.51e-3 | CONFIRMED |
| SR-1 M/4: turnaround; core max at 16.894 | -0.0125 M; 7.6e-4 | -0.0126; 7.61e-4 | CONFIRMED |
| SR-2 M/4: turnaround | +0.031 M | +0.0307 (three-point vertex); +0.0245, +0.0156, +0.0088 with wider windows | CONFIRMED as computed; not robust (finding 6) |
| apparent order M/2 -> M/4 of the core error | 3.0-4.3 | 3.03 (SR-1), 4.40 (SR-2) | CONFIRMED; the M/4 runs have half the box (L = 32 vs 64), so it is not a pure mesh refinement |
| SR-2 central lapse at the core turnaround | 1.85 vs exact 1.34 | 1.862 (M/2), 1.812 (M) | CONFIRMED |

Not recomputed: the horizon statements (SR-2 "largest 2m/R on the axis 0.34", no horizon
found), the gauge-pathology description from the field dumps, the Misner-Sharp mass along
the axis.

### 2.5 Statements in the note's text

| Statement (section) | Verdict | Evidence |
|---|---|---|
| constraints converge at the order of the differences; sharp edges leave a growing band (abstract, IV A) | CONFIRMED | 2.1 |
| two constructions, two readers, three exact solutions agree to rounding (abstract, IV C) | CONFIRMED (transcription of crosscheck.json, not re-run) | 2.1 |
| criteria reproduce the published values, spread over two orders of magnitude (abstract, II C) | CONFIRMED | 1.45/0.01 = 145; 41 of 41 checks |
| hoop function vanishes for e -> 0 and rises with e; reproduces the read-offs (II C) | CONFIRMED | fig_v_ledger, top left |
| particle result an order of magnitude below the hoop line and next to the run-length amplitude (II C) | CONFIRMED | 1.084/0.108 = 10.0; mu_fd(250) = 0.048 inside (0.045, 0.05] |
| particle result between the profile and the dispersion criteria (II C) | CONFIRMED | 0.0712 < 0.108 < 0.229 |
| H1: read-off collapse times follow the top-hat time of r_m (II C) | CONFIRMED as [JUDGEMENT] | ratio 0.80-1.01, slope -1.31 against -1.5 |
| marginally bound ball: 2M/R_b = (H R_b)^2; no anti-trapped sphere below the Hubble radius (III A) | CONFIRMED | nominal M = 1 = (H R_b)^2 R_b/2; largest 2m/R = 0.236 |
| common bang time for every shell (III A) | WRONG | finding 2 |
| first trapped sphere just outside the core edge, before the crunch; core edge after it; mass grows to the crunch (IV B) | CONFIRMED | R_i 2.742 > 2.4; 44.349 < 44.381 < 44.454; 0.0805 -> 0.0960 |
| geodesic slicing: coordinate speed of light of order one until late, then unbounded (IV B) | CONFIRMED | fig_v_ledger, bottom right (at most 1.6 until tau_c - 4) |
| conformal time: turnaround earlier, trapping and crunch later (IV B) | CONFIRMED | 13.82 < 16.89; 49.51 > 44.35; 54.96 > 44.45 |
| ball of three r_m below the particle bracket; two r_m reaches it; both far below the hoop line (III A) | CONFIRMED | 0.031 < 0.045; 0.069 > 0.045; 0.069 is 6.5 times below 0.452 ("an order of magnitude" is loose) |
| the outputs of each run are checked against the checksums the run recorded (App. B) | WRONG for the wave-1 runs | finding 7 |
| all but four checks pass (IV D) | CONFIRMED for wave 1; stale | finding 5 |
| first full-relativity runs queued; Newtonian runs under way (V) | CONFIRMED at its date; stale | finding 5 |
| amplitude conversion delta_c = 12 mu/5 = e_E deltabar (II A) | CONFIRMED | 2.2 |

## 3. Weak points

1. **SR-2 turnaround is not a robust number.** Per-particle turnaround times in SR-2 scatter
   (mean and median have opposite signs at M/2) because the conformal-time lapse pulse makes
   R(tau) of a core shell non-smooth near its maximum; a three-point vertex then picks the
   largest record. Any statement that SR-2 fails or passes a turnaround bound at M/4 should
   use a window-independent estimator (a fit of the core's R(tau) over a fixed proper-time
   interval, or the central density) and quote its spread.
2. **The M/2 -> M/4 comparison changes two things at once.** The M/4 runs use L = 32 instead
   of 64; the "apparent order 3.0-4.3" mixes mesh and boundary effects and the SR-2 errors at
   M/4 are oscillatory (fig_v_ball, middle). A third resolution at fixed L is needed before an
   order is quoted for G2.
3. **Wave-1 outputs have no checksums** (finding 7). Before G2 the lead should either rerun
   the wave-1 producers through `nrpic-run` (they take seconds to minutes) or record the
   present checksums with a note that they were taken on 2026-11-19.
4. **Units of M** (finding 3): fix the labels before the note's numbers are quoted in a
   comparison with Wu and Most, whose masses are total masses.

Small things for core and the docs: `docs/FORMATS.md` line 122 describes `.trajmet.bin` as
records of 12 values; the code (`nrpic_io.cpp:811`) and `coord/INTERFACES/diagnostics.md`
section 6 write 17 (with the proper time, E and S_i).

## C11: data-flow schematic

`note/figures/schem_dataflow.png` and `.svg`, script `note/scripts/schem_dataflow.py`
(style `paperfig.py`, the copy in `note/scripts/`), made in run A-20261119-143347-37240f3
(after a label fix; the first version is in A-20261119-142905-c813c01 `schem/`). Four lanes (expanding ball, periodic box, Newtonian mode, criteria and scope)
through initial data -> AthenaK core-v0.3 -> raw outputs under `scratch/A-emd-pbh/<run id>/`
-> the track's analysis -> products -> `note/scripts/common.py` (checksums) -> `ledger.py`
-> `tables/ledger.tex` -> `main.pdf`; below, registration through `nrpic-run` and the
verifier's independent path. Every file it names exists in the worktree (the cost logs
of `runs/jeans/` in the main checkout). PNG looked at.
It is not yet included in `note/main.tex` (the lead decides where).
