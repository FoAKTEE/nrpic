# Fresh verifier of gate G2, Track A (item C18; decisions 0016 item 4, 0046 item 1)

Helper of A-emd-pbh, batch 29, 2026-11-26 (PST). Processors only, 0 card-hours, one core per run (load of the
machine 50-110). Package: `stage/G2/verifier/` (JOURNAL.md with the predictions, committed before each reader ran;
README.md; scripts). Labels as in the brief: [VERIFIED] = recomputed here by a registered run of a reader of my own
that was first tested on an analytic case; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 0. What I read, and independence

- Claims from `stage/G2/RERUN.md`, `stage/G2/VERIFY`, Table V of the note (`note/tables/ledger_g2.tex`, Table V in
  `note/main.aux`) and section V of `note/main.tex` (lines 175-213); criteria from `scope/SCOPE.md` sections 3 and 7;
  the predictions as written before the runs (szekeres/JOURNAL.md entries 8 and 12; periodic_threshold/JOURNAL.md
  A2, AZ1, AZ2, A2X, A2H; threshold_ball/JOURNAL.md entry 13), whose commit order git log confirms.
- Not independent of the lead on one item: while locating the A2 predictions in periodic_threshold/JOURNAL.md I read
  the outcome subsections that follow them (lines 924-1207), and decision 0046 item 1 quotes the A2H bracket. My
  numbers for item 2 come from my own reader; my judgement there was not blind.
- Read only after sections 1-5 were written (for section 7): the verdict column of stage/G2/CHECKLIST.md,
  stage/G2/OPEN.md.
- Nothing of the track's analysis code is imported by my readers. Formats are read from the AthenaK source
  (`nrpic_io.cpp` lines 546-552 field dumps, 955-975 trajectories, 1112-1117 snapshots, 1164 particle files;
  `nrpic_cosmo.cpp` lines 7-19 initial-data files). Inputs that define a problem (not a result) are used as given:
  the Szekeres initial-data files and particle files, `id.json` of the peak data (box, r_m), the constants M, E and age
  per shell of the P0 LTB reference B (`A-20261121-130103-e007f42`, checked against the code's initial slice).
- `harness/bin/nrpic-stage verify A-emd-pbh G2 --full` was started detached at 14:18 PST (pid 499738); its log is
  `scratch/A-emd-pbh/tmp/stage-verify-full-verifier-20261126-141818.log`. State at the end of this session: section 6.

## 1. Runs of this verifier (all registered, processors, one core)

| run | what | status |
|---|---|---|
| A-20261126-222856-952faf8 | V1: Szekeres N64, N128, N256 against my per-element reference | see section 2.1 |
| A-20261126-223151-8310871 | V2: crossing of S1L, S1L-h, N-z, N-z128; Zel'dovich tensor; dust clock | completed |
| A-20261126-223655-77df724 | V3: P0L6 shells against my cycloid; finder status file | completed |
| A-20261126-223953-c6606f6 | V3 caveat, defective (one bang time for all shells) | completed, superseded |
| A-20261126-224045-9d8fe53 | V3 caveat: shell crossing of the exact LTB solution before tau = 141 | completed |
| A-20261126-223246-89959bc | V4 (C3): line ratio of 13 members | completed |
| A-20261126-223902-c94b32f | V5: Table V checker, failed on an inf in an output | failed |
| A-20261126-223909-6859df2 | V5: Table V checker and the conv_ball spot check | completed |

Figures (looked at): `fig_szk_verify.png` (V1), `fig_a2_verify.png` (V2), `fig_p0l6_verify.png` (V3),
`fig_c3_verify.png` (V4), each in its run's directory under `scratch/A-emd-pbh/`.

## 2. Results per item

### 2.1 Szekeres series (C1 (iii)): N64, N128, N256

My reference [derivation in verifier/JOURNAL.md entry 1]: for quasi-spherical Szekeres dust with a simultaneous bang
each fluid element obeys rho = rhobar/(1 + c G(t)) and K = d ln rho/dt = -3 H_T - c Gdot/(1 + c G), with c constant
along the element and the shell functions set by one number per shell, fixed from the initial slice cell by cell
(KT from K and psi^-6 Ahat_ij of the field file; rho_i from the particle masses). It does not use the lead's labels
r, bn, conformal map or code. Analytic test: the closed form agrees with the integrated general dust equations
(Raychaudhuri, continuity, Friedmann of the shell) to 2.1e-12 for seven elements to tau = 30. Data check: the
longitudinal eigenvalue KL predicted from (KT, rho_i) equals the file's to 2e-9 H_i in every cell of every member,
and the code's K at tau = 0 equals my K to 2e-11 H. Runs A-20261126-222856-952faf8 (K, E, signal) and
A-20261126-224402-693c506 (H, alpha).

| quantity (shell region) | N64 | N128 | N256 | Table V | status |
|---|---|---|---|---|---|
| rms |K - K_ex|/H, tau 10 | 0.0268 | 0.00442 | 0.000281 | 0.0268, 0.0043, 0.000277 | reproduced within 3 per cent |
| tau 20 | 0.0599 | 0.0123 | 0.00103 | 0.0616, 0.0123, 0.001 | within 3 per cent |
| tau 30 | 1.078 | 0.0443 | 0.00377 | 1.04, 0.045, (none) | within 4 per cent |
| tau 40 | broke at 30.25 | broke at 37.47 | 0.0413 | (none) | |
| order of K rms, 64->128 at tau 10, 20, 30 | 2.60, 2.28, 4.61 | | | 2.64, 2.33, 4.53 | within 0.08 |
| order of K rms, 128->256 at tau 10, 20, 30 | | 3.98, 3.58, 3.55 | | 3.96, 3.62, (none) | within 0.04 |
| order of H rms, 64->128 / 128->256 | 2.96, 2.81, 3.49 | 4.15, 4.73, 5.01 | | 2.93, 2.79, 3.49 / 4.01, 4.65 | within 0.14 |
| max |K - K_ex|/H, tau 10, 20, 30 | 0.10, 0.25, 77 | 0.025, 0.067, 0.58 | 0.0024, 0.0078, 0.044 (0.59 at 40) | | |
| non-spherical signal, mine (same element) | 0.19, 0.32, 0.77 | 0.18, 0.23, 0.49 | 0.17, 0.18, 0.22 (0.57 at 40) | 0.68-0.69, 1.42-1.43, 3.45 (same cell) | not the same quantity |
| max |alpha - 1| | 6.8e-13 | 1.4e-12 | 3.6e-12 (grows as the step count) | | |
| where the member stops | guard, tau 30.25 | guard, tau 37.47 | tau 40.0, finite | | reproduced |

- The note's convergence statement ("between second and fourth order, close to fourth on the two finer meshes")
  is reproduced: 2.3-2.6 for 64->128 before the coarse member breaks down, 3.6-4.0 for 128->256.
- The non-spherical signal: Table V compares Szekeres and LTB at the same code cell, which includes the
  displacement of the shells' centres; I compare the Szekeres element with the LTB element of the same shell (the
  invariant dipole of the expansion on a shell). Mine is 3.5 to 15 times smaller. Against Table V's signal the
  lead's P20 holds everywhere (Table V's numbers are in the lead's output; I did not recompute them). Against mine,
  P20 (max error at most a tenth of the signal at N256 and a fifth at N128, every dump to tau 30) holds for N256 at
  tau 10 and 20 (70x, 22x) and fails at tau 30 (5.1x); for N128 it holds at tau 10 (7.2x) and fails at tau 20 (3.4x)
  and 30 (0.84x). The rms error of N256 stays 44 to 590 times below my signal to tau 30. So "the test sees the part
  of the metric that a spherical code would miss" holds for N256 to tau 30 by the invariant measure, with a factor 5
  at tau 30 in the worst cell, not the factor 78 that Table V's measure gives.
- "The finest member reaches the end of the test": with finite fields, yes; with a small error, no: at tau 40 N256's
  shell error (max 0.59, rms 0.041) equals my signal (0.57) and its shell H rms is 28.9 times 16 pi rho_b. The lead's
  P18 for N256 at tau 40 (0.01 within a factor 3) fails; P24 holds at tau 40 and fails at tau 30 (0.00377, below its
  band [0.004, 0.04]).
- The two failed clauses the note names: P21 (H order equal to the K order within 0.5 between 128 and 256) holds at
  tau 10 (4.15 against 3.98) and fails at tau 20 (4.73 against 3.58): reproduced. The lapse clause of P17 (alpha = 1
  to 1e-12) fails from tau 20 at N256 (1.8e-12; linear in the number of steps): reproduced.

### 2.2 Triaxial runs S1L and S1L-h (C1 (iv), tests A2 and A2H)

My reference [derivation in JOURNAL entry 1]: dust in Einstein-de Sitter in the synchronous comoving gauge grows as
D = a on every scale [BACKGROUND]; first-order Lagrangian x = q + a psi(q); the first crossing along the principal
axis of the largest eigenvalue lambda_1 of -d psi_i/d q_j (at a = 1) is at a = 1/lambda_1; H_i = 1 at a = 1, so
a = (1 + 1.5 t)^(2/3) and t/t_H = (1 + 1.5 t)/r_m^3 = (a/r_m^2)^(3/2) with r_m = 2.4495 (id.json). The deformation
tensor is read from snapshot 0 (centred differences at the central site; the lattice test shows these are ~1 per cent
low at the runs' spacing, so the Zel'dovich times below may be ~1.5 per cent high).

| quantity | mine (run A-20261126-223151-8310871) | package | status |
|---|---|---|---|
| S1L lambda (z, x, y) at a = 1 | 0.06258, 0.03935, 0.01613; axis z exactly; ratio 1.59 : 1 : 0.41 | 0.063 (from 1 - 0.937); design 1+3e : 1 : 1-3e | reproduced |
| S1L Zel'dovich first-axis time | 4.346 t_H (second 8.72, third 33.2) | 4.35 (Table V) | reproduced, 3 digits |
| S1L-h lambda | 0.03129, 0.01968, 0.00806 (exactly half) | 0.0315 (scaling) | reproduced |
| S1L-h Zel'dovich time | 12.29 t_H | 12.3 | reproduced |
| S1L first crossing, sign of det(dx/dq) | (6.192, 7.213] t_H; 134 cells; deepest at q = (0.63, 0.00, -0.62), two sites from the centre | (6.19, 7.21] | reproduced, 3 digits |
| S1L-h first crossing | (13.847, 14.358] t_H; 2 cells at the centre | (13.8, 14.4] | reproduced (Table V prints 3 digits) |
| first axis | z in both; S1L then x (8.23, 9.25], y (13.34, 14.36]; S1L-h x (19.97, 20.48] | z | reproduced |
| dust clock (own proper time of the particles at the corners of the first-crossing cell) | S1L 5.993-6.002 t_H on the last uncrossed snapshot, 6.835-6.943 on the first crossed; S1L-h 13.684-13.698 and 14.155-14.168 | S1L (5.99, 6.80] from the probe; S1L-h ">= 14.07 on the crossing slice" from int alpha_min dt | consistent; mine is the direct proper time |
| central particle at rest | max |u_i| 1.1e-9 (S1L), 5.6e-12 (S1L-h) | 5.6e-12 (S1L-h) | reproduced |
| Newtonian N-z, N-z128 | (4.520, 4.689], (3.588, 3.734] t_H, z first at the centre | 4.55 (4.52-4.69), 3.62 (3.59-3.73) | reproduced |

Verdicts. Test A2 as written (first crossing in [3.4, 5.0] t_H) FAILED: S1L crosses in (6.19, 7.21] on the coordinate
clock and in (5.99, 6.94] on the dust's own clock, a measure that neither the shift nor the slicing can move. A2H
(band [12.5, 15.2] t_H, written before the run) HELD on both clocks: (13.85, 14.36] coordinate, (13.68, 14.17] dust
clock; no refutation band (above 15.6, below 11.8) was entered. The ratio of the GR crossing to the converged
Newtonian one is 1.66-1.93 at full amplitude (dust clock against N-z128) and 13.68-14.17 against 2.83 x (3.59-3.73) =
10.2-10.6 (1.29-1.40) at half amplitude [arithmetic on the numbers above; the factor 2.83 = 2^1.5 is the
self-similar scaling the lead used, which I did not test]. What the hold supports [JUDGEMENT]: a lag that falls with
the amplitude; it does not name the effect.

New finding (not in the package): the particle snapshots of these runs carry each particle's proper time (72 bytes a
particle; `nrpic_io.cpp` 1115-1117), so the "lower bound int alpha_min dt" and the probe were not needed: the dust
clock of the crossing cell is in the snapshots. The package's statement "the snapshots hold x, u_i, m only"
(periodic_threshold/JOURNAL.md, outcome A2X (ii)) is wrong for these files.

### 2.3 Periodic chain P0L6 (C1 (ii))

My reader: areal radius of the round coordinate sphere through each tracked particle, R = r sqrt(g_T),
g_T = (tr gamma - n.gamma.n)/2, from the metric at the particle (trajmet), against my own cycloid on the particle's own
proper time with the constants M, E, age of reference B. The reference reproduces the code's initial slice
(R(0) to 2.2e-5; dR/dtau(0) to 3.7 per cent with a three-record difference). The exact solution has no shell
crossing among the 47 tracked radii before tau = 141 (run A-20261126-224045-9d8fe53; the initial slice taken as one
LTB time).

| claim | mine (run A-20261126-223655-77df724) | status |
|---|---|---|
| shells with r0 > 1.5 follow LTB "to 1-4 per cent" | max |R/R_B - 1| = 3.3 per cent up to each shell's exact turnaround (276 tracks); r0 >= 2.47: below 0.3 per cent to t = 140 | reproduced up to turnaround |
| "outer shells follow the LTB solution through turnaround and collapse" (note) | after turnaround, before their exact trapping, the outer tracks that turned depart by 42 (r0 = 1.52, code shell larger), 3.8 (1.58), 25 (1.83, code shell smaller), 19 (2.13), 6.8 (2.15) per cent | not reproduced for the collapse phase |
| inner shells follow it "less well" | r0 <= 1.5: factors (R/R_B up to 240 near their exact crunch) | reproduced (qualitatively) |
| finder accepts one surface that is not trapped (t = 118.1) | the only found = 1 of 308 searches is at t = 118.118: area mass 562.2, mean coordinate radius 18.2 (more than half the box); no tracked shell is trapped in the code then (first code-trapped track at t = 122.22) | reproduced |
| finder fails on a trapped sphere from t = 136 | every search from t = 121.40 to 140.0 (172 searches) ends with reason 6 (no convergence of the mass), area masses ~3 to ~7; 14 tracks trapped in the code from t = 122.2 (largest M 3.47, R 5.95) | reproduced, but the stall begins at 121.4, not 136 |
| the trapped sphere is "resolved by many cells" | the outermost trapped track has coordinate radius 0.0168 at t = 136, 3.4 cells of the finest level (dx = 0.0049, deck peak_leak6); the next tracked radius outward is not trapped, so the trapped surface lies between them | not decided by my measure (tracks are sparse) |

The horizon part of C1 (ii) is FAILED as written (false acceptance, then no horizon while trapped spheres exist).

### 2.4 Item C3: ||H||/||16 pi E|| on the x line (SCOPE section 3 bound 0.1)

My reader (run A-20261126-223246-89959bc): line outputs `con_H` and `tmunu_E`, weights x^2 dx with dx from the
neighbours on the line (tested: integral of x^2 on a nested line to 0.18 per cent), x > 0.

| member | t = 0 | 0.25 | 0.5 | 0.75 | 1 | 2 |
|---|---|---|---|---|---|---|
| top hat A (K4-ref) | 0.278 | 0.583 | 0.889 | 0.810 | 0.927 | 0.557 |
| top hat A (card) | 0.278 | 0.583 | 0.889 | 0.810 | 0.927 | 0.557 |
| top hat B (card) | 0.174 | 0.617 | 1.375 | 1.793 | 1.497 | 0.506 |
| S1 (A0, B0) | 0.185, 0.146 | | | | | |
| S2 (A, B) | 0.134, 0.116 | 0.077 (A) | 0.198 | 0.165 | 0.142 | 0.289 |
| S2c-A | 0.00636 | 0.0502 | 0.0978 | 0.0966 | 0.129 | 0.245 |
| S2c-B | 0.000578 | 0.0178 | 0.0467 | 0.0761 | 0.101 | |
| S2c-A8 (eight particles per cell) | 0.0609 | 0.0555 | 0.122 | 0.108 | 0.140 | 0.256 |

- Orders A -> B: S2c 3.46 at t = 0, then 1.50, 1.07, 0.34, 0.36 at t = 0.25 to 1; top hat 0.68 at t = 0, then -0.08,
  -0.63, -1.15, -0.69 (mesh B worse). S2c-A8/S2c-A: 9.6 at t = 0; 1.11, 1.25, 1.12, 1.08, 1.04 at t = 0.25 to 2.
- Table V rows (S2c-A 0.00636, 0.129, 0.245; S2c-B 0.000578, 0.101; S2c-A8 0.0609, 0.14, 0.256): reproduced to 3 digits.
- From t ~ 1.5 all members lie on one curve, 0.3 at t = 2 to ~0.6 at t = 5 (figure): the growth does not depend on
  the data, the cloud or the mesh in the members read.
- Note: "tophat A (K4-ref)" (processor rerun) and "tophat A (card)" agree to the four digits printed at every time
  (not examined further).

C3 FAILED as written: the top hat violates the bound in its initial data on both meshes; every member exceeds 0.1
by t = 1 (S2c-B by 1 per cent); the evolution does not converge with the mesh at the scheme's order (0.34-0.36 for
S2c between t = 0.75 and 1; negative for the top hat). The member with eight particles per cell agrees with one
particle per cell within 4-25 per cent from t = 0.25 on, so particle sampling is not the main cause of the growth
[VERIFIED for this member; JUDGEMENT beyond it].

### 2.5 Table V row by row; spot check of the earlier verifier's rows

Run A-20261126-223909-6859df2 (matcher tested on known strings): all 24 rows have a manifest with status completed,
and every printed value occurs in the run's registered output at the printed number of digits. Weak for the integer
orders "1.5, 2" and "2, 1.5" (small numbers occur anywhere); from the printed errors the orders are
log2(0.193/0.0675) = 1.52, log2(0.0675/0.0166) = 2.02 (detection) and 2.05, 1.53 (trapping): consistent.
Rows reached by my own readers above: the Szekeres rows (2.1), the S2c rows (2.4), the three S1L/S1L-h rows (2.2).

Spot checks of conv_ball (earlier verifier VERIFIER-C18.md): (a) the raw horizon summary of member C
(`A-20261121-083336-6a82131/ball.horizon_summary_0.txt`) first finds a surface at t = 10.75 with mass 0.6885454828,
equal to the analysis to all digits; Delta t_det(C) = 9.60581 - 9.58922 = 0.01659 (Table V 0.0166): reproduced. The
exact tau_ah was not recomputed by me. (b) Delta t_trap(C) = -0.00775 occurs in the output but was not traced to its
inputs: not checked.

## 3. Items and predictions that failed as written

- C3 (constraint bound of SCOPE section 3): FAILED (2.4).
- A2 (first crossing in [3.4, 5.0] t_H): FAILED (2.2).
- C1 (ii), horizon part: FAILED (2.3): one false acceptance, then 172 searches without convergence while the code
  has trapped spheres.
- My own predictions that failed: V3.1 for the collapse phase (shells r0 = 1.52, 1.83, 2.13, 2.15 depart by more
  than 6 per cent before their trapping), V4.2 for the size of the top-hat growth (0.9-1.8 instead of 0.05-0.15),
  V1.3 (my signal is a different quantity, 3.5-15 times smaller than Table V's), V1.5 at tau 10 by 0.04 beyond my
  tolerance.
- The lead's predictions that fail as written in what I recomputed: P20 against the invariant signal (N256 at tau 30,
  N128 at tau 20 and 30), P21 at tau 20, P17's lapse clause, P18 for N256 at tau 40, P24 at tau 30, AZ1 (N-z
  (4.52, 4.69] outside [3.7, 4.5]; N-z128 not within 5 per cent of N-z). AZ2 (member N-f) was not read by me.

## 4. Findings for the lead

1. The snapshots carry each particle's proper time; the dust-clock statements of A2X and A2H can be made directly
   (2.2), and A2X (ii) "not decidable" was decidable from the existing files.
2. P0L6: every finder search fails with reason 6 from t = 121.4 on, and tracked shells are trapped in the code
   (R < 2 M of their shell) from t = 122.2 (2.3); "from t = 136" holds for the trapped surface the lead reads on the
   line output, not for the failures of the finder.
3. P0L6: "follow the LTB solution through turnaround and collapse" holds within 3.3 per cent to turnaround only;
   during the collapse the outer shells with r0 in (1.5, 2.2) depart by up to 42 per cent before their own exact
   trapping time.
4. Szekeres: state which non-spherical signal Table V uses (same cell, including the displacement of the shell
   centres); the invariant signal on a shell is 3.5-15 times smaller, and against it the factor at N256, tau 30 is 5.
5. Szekeres: "the finest member reaches the end of the test" should say "with finite fields"; at tau 40 its error
   equals the invariant signal.
6. C3: the processor member K4-ref and the card member A give the same line ratio to 13 digits at every time
   (my reader and the lead's edge.json agree), stronger than the "1e-3" of K4c.

## 5. Not done

- The exact horizon-trapping times of the expanding ball (conv_ball) were not recomputed (earlier verifier).
- Track A's threshold_ball bracket and masses: not rechecked beyond Table V's presence test (earlier verifier).
- The particle-number and radius legs of C1 (i), C2, C7, C8: not reached.

## 6. Stage verify

`harness/bin/nrpic-stage verify A-emd-pbh G2 --full` (started 14:18 PST, pid 499738, exported tip of
track/A-emd-pbh at that time, before my first commit) was still hashing every output (four threads) when this report
was committed, about an hour later; its log (`scratch/A-emd-pbh/tmp/stage-verify-full-verifier-20261126-141818.log`)
is written at the end and was still empty. Its result is not part of this report; the lead reads it from the log and
from `stage/G2/VERIFY_RESULTS.md` when it ends. The worktree has commits of mine after the exported tip, so the
"worktree clean" and "main merged" checks of that pass refer to the tip of 14:18.

## 7. Comparison with the lead's verdicts (written after sections 1-6)

Read now: the status and evidence of every item in stage/G2/CHECKLIST.md, and stage/G2/OPEN.md.

| item | lead | this verifier | agreement |
|---|---|---|---|
| C1 (i) expanding ball | passed | Table V rows present in the registered output; Delta t_det(C) from the raw finder file reproduced (0.01659); exact references not recomputed (earlier verifier) | agree, within what I checked. Table V still prints the detection-time orders as "1.5, 2" although CHECKLIST C2 (after VERIFIER-C18) gives 1.2-1.5 and 1.75-2.1 under three interpolations: the note's table should carry the range |
| C1 (ii) P0L6 | FAILED on record, horizon part; shells r0 >= 1.5 "to 1-4 per cent" (OPEN), "within 3 per cent to turnaround" (CHECKLIST) | horizon part failed (false acceptance at 118.1, no horizon while trapped spheres exist); shells within 3.3 per cent to turnaround, 4-42 per cent during collapse | agree on the failure and on the shells to turnaround; disagree with the note's "through turnaround and collapse" and with OPEN's "1-4 per cent" without the limit "to turnaround"; the finder fails from 121.4 (reason 6), the lead dates the stall from the line's trapped surface at 136 (both true, different events) |
| C1 (iii) Szekeres | passed with clauses refuted; P20 holds to tau 30 (ratios 79, 275) | all Table V numbers reproduced within 4 per cent (rms) and 0.08 (orders); P20 holds with Table V's same-cell signal, fails at N256 tau 30 (5.1x) and N128 tau 20, 30 with the invariant same-shell signal; N256 at tau 40 finite but its error equals the invariant signal | agree on the numbers; the pass of P20 depends on the definition of the signal, which the note does not state; I would pass (iii) with that caveat written into the note |
| C1 (iv) A2 / A2H | A2 FAILED as written; A2H holds, (13.85, 14.36] t_H; dust clock ">= 5.99" (S1L) and ">= 14.07" (S1L-h) from int alpha_min dt; the bound from the snapshots alone "empty" | same brackets to 3 digits; the dust clock read directly from the particles' proper times in the snapshots: (5.99, 6.94] and (13.68, 14.17] t_H | agree on A2 failed and A2H held; disagree on a fact: the snapshots do carry each particle's proper time, so A2X (ii) was decidable from the files |
| C3 constraints | FAILED as written; cause unexplained; mesh leg order ~0.35; x8 particles change t = 1-2 by 2-8 per cent, "sampling is excluded" | FAILED; orders 0.34-0.36 at t = 0.75-1; x8 member within 4-8 per cent at t = 1-2 but 11-25 per cent higher at t = 0.25-0.75 | agree on the failure and the numbers; "sampling is excluded" holds from t = 1 on, not at t = 0.25-0.75 |
| failed predictions listed in OPEN.md | C3, A2, C1 (ii) horizon part; T4-T6, K, K2, K3, F1, F2, G, AZ1 second clause, D2-D4, A2X bound, P17 lapse, P18 N256 tau 10, P21 tau 20, H t = 0 clause | I add: P18 for N256 at tau 40 (0.041 against 0.01 x/: 3), P24 at tau 30, AZ1's first clause (N-z (4.52, 4.69] above 4.5), P20 against the invariant signal | the lead's list is right as far as I checked it; P18 at tau 40 and AZ1's first clause are missing from OPEN's list (AZ1's first clause is on record in the journal) |
| C18 | OPEN, this report | written; sections 2-5; the full stage verify still running at the end | |

I did not recheck C2, C4-C17, C19, C20 beyond the Table V presence test and the figures of my own runs.
