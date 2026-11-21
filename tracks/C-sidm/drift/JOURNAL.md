# JOURNAL of C-sidm/drift (wave 3, round 1, helper of C-sidm)

Package: the origin of the slow outward excursion of the central lapse in the two
collisionless King controls of wave 2 (`../threshold_scan/JOURNAL.md` entry 6, P3.8;
`../RISKS.md` item 3): numerical (mesh), particle noise, or a physical mode excited by the
initial data. The answer decides the mesh of block A of `../threshold_scan/SCAN.md`.
Predictions are written here before each test; outcomes after it, also when they fail.
Run ids: `../runs/<run_id>/manifest.json`. Labels: [VERIFIED] computed in a registered run
named next to it; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 2026-11-20 22:20 UTC Entry 1: state, and predictions for the processor analysis (test D1)

State found: no `drift/` directory, no run of this package registered (fresh start). Pause
flag absent. Slurm: no job of C-* queued or running (22:15 UTC).

Inputs [VERIFIED from files]:
- wave-2 controls: cc1_kninf in card run C-20261115-171058-c26cfad, cc2_kninf in
  C-20261115-171059-4b70228 (decks `../threshold_scan/inputs/cc{1,2}_kninf.athinput`:
  static mesh, level-6 region |x|_inf < 7.9 M, dx = M/4 there, N = 1e5, dt = M/16, 300 M,
  four compensated binomial passes, 1+log lapse and Gamma-driver shift); restart files
  `rst/cc.00001.rst(.prt)` of both were written at the end of the run (10:21:29 and
  10:40:11 PST on 2026-11-15, `<output2> dt = 300`), i.e. at t = 300 M.
- the batch executables of both runs (`batch.list.exe`) and the release card executable
  `.work/build_gpu_v03/src/athena` have the same sha256 f9f2dc12...be3a1: a restart with the
  release executable is exact.
- What the wave-2 analysis (run C-20261115-191420-8538aa4, `fig_cc_controls.png`, looked at
  again today) shows: alpha_c - alpha_c(0) rises to +0.0334 (CC1) and +0.0185 (CC2) near
  200 M and falls back to about +0.017 and +0.004 at 300 M; a ripple of about 1e-3 on top.

Questions of test D1 (processor analysis of the two controls, run to be registered):
alpha_c(t); radii enclosing 10 and 50 percent of the rest mass (coordinate, and the areal
radius of the same shells from the metric at the particles, so that a pure change of the
spatial coordinates can be told from a physical expansion); the Hamiltonian-constraint
norm; rest mass, mean Lorentz factor sum mW/sum m and Killing-energy sum; particle count;
period and amplitude of the excursion (fit of A (1 - cos 2 pi t/P) + c, and a free-phase
sinusoid with a trend as a second estimator); whether it returns by 300 M; and the period
of the fundamental radial mode from the track's own pulsation tool (`tmb.fem_lowest` via
`models/fluid_onset.omega2`, King family b = 1 as in the lead's check L15, run
C-20261119-151502-cb831a8), converted to the time at infinity in units of M.

Predictions (written before the analysis runs; I have seen only `fig_cc_controls.png`):

- D1.1 Fit period. P(CC1) in [330, 550] M, P(CC2) in [280, 480] M, and P(CC2) < P(CC1)
  (the threshold model is the softer one). Refuted if P(CC2) >= P(CC1) or either lies
  outside its band.
- D1.2 Not a coordinate effect. The coordinate radius r50 grows when alpha_c grows
  (Pearson correlation of the two series, interpolated to the snapshot times, > +0.7), and
  the areal radius of the same shell moves by at least half the relative amount of the
  coordinate r50. Refuted if r50 is flat or anti-correlated, or the areal radius stays
  within a quarter of the coordinate change (then the lapse excursion is mostly slicing and
  shift, a gauge drift).
- D1.3 An expansion slows the particles: the mean Lorentz factor sum mW/sum m is
  anti-correlated with alpha_c (correlation < -0.7). Refuted otherwise.
- D1.4 Bookkeeping: rest mass bit-identical and np = 1e5 at every record (as in P3.1);
  the squared H-norm does not follow the excursion (|correlation with alpha_c| < 0.5).
- D1.5 The fundamental radial mode of a fluid with the model's own adiabatic index
  (F21 gamma = 1 + p/u) has a period of order the dynamical estimate
  pi (3/(4 pi rho_c))^(1/2) = 22.0 M (CC1) and 23.6 M (CC2) (threshold_scan entry 3):
  within a factor four of it, i.e. far below the excursion's P. With the Juttner index
  (onset y0 = 0.32143, L15) CC1 has omega^2 < 0 and no period. So the excursion is not the
  fundamental mode of a fluid; for the collisionless cluster the lowest radial frequency
  vanishes at the binding-energy maximum (2009.08163 places the onset there [BACKGROUND,
  as quoted in `../threshold_scan/SCAN.md` 'What each block decides']), so a period of
  10-20 dynamical times is possible only for a near-marginal collisionless mode
  [JUDGEMENT]. Refuted if a fluid period lies within 30 percent of the fitted P.

## 2026-11-20 22:25 UTC Entry 2: outcome of D1; predictions for the card runs (i)-(iv)

### Outcome of D1 (run C-20261120-222211-aa1be86; `fig_drift_controls`, `fig_drift_fit`, `fig_drift_pulsation` looked at, copies in `figs/`)

Numbers [VERIFIED, `controls.json` of the run]:

| | CC1 (y0 = 0.334032) | CC2 (y0 = 0.314) |
|---|---|---|
| alpha_c(0) on the mesh; model alpha_c | 0.66225; 0.66141 | 0.67694; 0.67622 |
| max of alpha_c - alpha_c(0) (20 M mean), at | 0.0330 at 205.5 M | 0.0179 at 207.8 M |
| at 300 M (mean of +-5 M); fraction of the max left | 0.0173; 0.52 | 0.0041; 0.23 |
| fit A (1 - cos 2 pi t/P) + c: A, P, c, rms | 0.0154, 399 M, 0.0009, 8.2e-4 | 0.0086, 355 M, 0.0008, 8.0e-4 |
| same fit ending at 200 / 250 M: P | 402 / 398 M | 350 / 353 M |
| fit a + b t + A sin(2 pi t/P + phi): A, P (formal sd) | 0.0168, 415 (5) M | 0.0099, 393 (5) M |
| coordinate r10, r50, r90: largest relative growth | 0.136, 0.117, 0.106 | 0.081, 0.064, 0.059 |
| 50 % shell, coordinate / areal radius, largest change | 0.115 / 0.090 | 0.064 / 0.050 |
| areal over coordinate change of the 50 % shell (regression) | 0.78 | 0.78 |
| correlation of alpha_c with r50, areal r50, sum mW/sum m, H-norm2, sum M E_K | +0.996, +0.997, -0.998, -0.49, +0.998 | +0.990, +0.996, -0.995, -0.48, +0.998 |
| sum mW/sum m: start, lowest | 1.09120, 1.07781 | 1.08525, 1.07804 |
| H-norm2: t = 0, end (flat from about 60 M on) | 0.0230, 8.5e-4 | 0.0235, 8.3e-4 |
| sum M E_K: largest change | 0.0142 M | 0.0077 M |
| ripple (residual of the cosine fit): rms, periodogram peak | 8.2e-4, 52.7 M (second peak ~75 M) | 8.0e-4, 53.9 M |
| rest mass bit-identical; np; unconverged pushes | yes; 1e5; 0 | yes; 1e5; 0 |

Radial pulsation of the King family (tmb b = 1, lowest omega^2 of the FEM, N = 600 and
1200 agree to 4e-7 relative; periods in the time at infinity) [VERIFIED, same run]:

| | CC1 | CC2 |
|---|---|---|
| dynamical estimate pi (3/(4 pi rho_c))^(1/2) | 22.0 M | 23.6 M |
| fluid, F21 index gamma = 1 + p/u | 358 M | 305 M |
| fluid, Juttner Gamma_1(theta_E) | unstable (omega^2 < 0) | 793 M |
| fluid, Juttner Gamma_1(theta_p) | unstable | 843 M |
| proxy for the collisionless mode: F21 index times s* = 0.9786, which puts omega^2 = 0 at the E_b maximum y0 = 0.334032 [JUDGEMENT: a proxy] | marginal (infinite) | 516 M |

Predictions:
- D1.1 PASS. P(CC1) = 399-415 M and P(CC2) = 355-393 M (the two fit forms differ by 4 and
  10 percent: that is the systematic error, not the formal 0.3-5 M), inside [330, 550] and
  [280, 480]; P(CC2) < P(CC1) in both forms.
- D1.2 PASS. r50 follows alpha_c (+0.996, +0.990) and the areal radius of the 50 % shell
  moves by 0.78 of the coordinate change: a physical expansion by 9 % (CC1) and 5 % (CC2)
  in areal radius, not a drift of the coordinates.
- D1.3 PASS (-0.998, -0.995): the particles slow down as the cluster expands.
- D1.4 PASS (rest mass, np; |corr(H, alpha_c)| = 0.49 and 0.48, just inside 0.5). The
  H-norm2 starts at 0.023, falls by a factor 27 within about 60 M and stays flat at
  8.3-8.5e-4, the same curve for both models.
- D1.5 FAILED. The fundamental radial mode of the fluid with the F21 index has a period of
  358 M (CC1) and 305 M (CC2), 10 and 14 percent below the cosine fits and 16 and 22
  percent below the sine-with-trend fits, not "of order the dynamical estimate"; my
  prediction took the 22-24 M estimate of threshold_scan entry 3 for the scale of the
  fundamental mode. Near the turning point omega^2 is small: omega^2/(4 pi rho_c) is about
  0.006 for CC1 (from omega_hat^2 = 0.039 and rho_hat_c = 0.52) [VERIFIED arithmetic on the
  run's numbers].

Reading [JUDGEMENT]:
1. The excursion is a large-amplitude fundamental radial pulsation, started at t = 0 from
   a turning point: the cosine form with the phase fixed at a maximum displacement fits to
   the ripple level (rms 8e-4 against an amplitude of 0.0154 and 0.0086), the cluster
   expands by 5-9 % in areal radius and contracts again, the particles slow and speed up in
   step, and the period is that of the fundamental mode of these near-marginal models
   (300-800 M depending on the adiabatic index; 22 M is the crossing time of the core, not
   the period of the mode). So it is a physical mode; what remains open is what displaces
   the initial state from the code's equilibrium (the mesh, the particle noise, or the
   initial data themselves). The size of the response grows as 1/omega^2, which is why it
   is larger for the model closer to the threshold.
2. CC1 sits at the collisionless threshold, where the lowest radial frequency vanishes in
   the continuum (the scaled proxy is marginal there), yet it oscillates with P = 400 M on
   the M/4 mesh and turns back at 205 M. Either the M/4 mesh (four compensated binomial
   passes on M/4 cells) moves the code's threshold to larger y0, or the large amplitude
   (nonlinear) sets the turning point. A finer mesh should then lengthen P(CC1).
3. The ripple residuals of CC1 and CC2 coincide almost cycle by cycle (`fig_drift_fit`
   left), and so do the H-norm2 curves: both runs use the same seed and sampler, so this
   part follows the particle realisation (and the mesh), not the model.

### Predictions for the card runs (written before any submission)

Runs (decks and lists written by `scripts/make_decks.py`, `inputs/`): (i) cc2_kninf_M8,
(iii) cc1_kninf_M8 (level-7 region of M/8 cells inside |x|_inf < 3.9 M, 300 M);
(ii) cc2_kninf_A1000, (iv) cc1_kninf_A1000 (restart of the wave-2 runs at 300 M to
1000 M). Release card executable, one run per batch job, `-t 00:52:00`.

M/8 controls (i), (iii). Let R = A(M/8)/A(M/4), A the amplitude of the cosine fit over
0-300 M (cross-checked with the maximum of the 20 M mean).
- M8.1 Decision rule (as the brief of the package sets it): R in [0.15, 0.35] reads as a
  second-order numerical displacement, [0.35, 0.65] first order, [0.75, 1.33] not the mesh
  (then particle noise or the initial data: the particle-number leg comes next), R > 1.33
  a mesh that stabilises the mode (then P must lengthen as well). My bet [JUDGEMENT, 55 %]:
  R in [0.15, 0.65] for both models (a mesh truncation error of the deposit and filter at
  the 1e-4 level of the force, amplified by 1/omega^2 ~ 170 at CC1). Refuted if R >= 0.75
  for either model.
- M8.2 Period: P(CC2, M/8) within 15 % of 355-393 M (a property of the model, not of the
  mesh); P(CC1, M/8) >= 0.9 x 399 M, and longer than at M/4 if reading 2 holds. Refuted if
  P(CC2) moves by more than 15 % or P(CC1) shortens by more than 10 %. If R is below 0.3
  the ripple (8e-4) limits the period fit: then the period is judged from the times of the
  maximum and of the return only.
- M8.3 Noise floor: the late H-norm2 (100-300 M) rises at M/8 (more particle noise per
  cell in the level-7 region) by more than a factor 1.5 over 8.3-8.5e-4. Refuted if it
  falls (then the floor is truncation error).
- M8.4 Bookkeeping and cost: rest mass bit-identical, np = 1e5; 456 MeshBlocks (400 - 8
  + 64) with 8 physical levels; 2.0-2.8 times 3.42-3.46 s per M, i.e. 6.8-9.7 s per M and
  34-48 min for 300 M (inside the 52 min limit). Refuted if the block count differs or the
  run stops before 300 M.

Continuations (ii), (iv) to 1000 M.
- A.1 The restart continues the wave-2 state: np = 1e5 and sum_m equal to the wave-2
  value bit for bit; the first records after 300 M join the wave-2 curve of alpha_c within
  the ripple (2e-3).
- A.2 Bounded oscillation with the period of D1: a minimum of the 20 M mean below 0.25 of
  the first maximum near t = P (CC2 in [320, 450] M, CC1 in [360, 480] M), a second
  maximum near 1.5 P (CC2 in [480, 640] M, CC1 in [540, 700] M) with 0.5-1.3 times the
  first amplitude, and a second minimum near 2 P (CC2 in [640, 830] M, CC1 in [720, 900] M).
  Refuted by growth (second maximum above 1.5 times the first), by a collapse (alpha_min
  < 0.3), or by no second maximum before 1000 M (a drift, not an oscillation).
  [JUDGEMENT] CC1, at the threshold, carries the risk: 60 % bounded, 25 % growth or
  collapse, 15 % drift.
- A.3 The cosine fit over 0-1000 M (wave-2 records joined with the continuation) gives A
  and P within 20 % of the 0-300 M fit (one mode, one period); a slow decline of the
  amplitude (phase mixing) by up to 30 % per period does not refute it.
- A.4 The ripple rms (residual of the 0-1000 M fit, without the fit error) stays within a
  factor two of 8e-4, and the H-norm2 floor stays at 8.3-8.5e-4 within 20 %.
- A.5 Cost: 700 M at 3.42-3.46 s per M, 40-41 min (inside 52 min).

## 2026-11-20 22:27 UTC Entry 3: processor smoke of the M/8 deck; job (i) submitted

- Job (i) submitted at 22:25 UTC as run C-20261120-222533-ce50a86 (Slurm 4741, pending;
  the other C-* job in the queue is the decisive package's 4737).
- Smoke (run C-20261120-222544-e5a7492; release processor executable, cc2_kninf_M8 with
  time/nlim = 0, 2 threads, 55 s): clause "456 MeshBlocks, 8 physical levels" of M8.4 PASS
  (64 blocks of level 7; the log prints 456 and eight physical levels); reads 1e5
  particles; alpha_probe(0) = 0.67640 (M/4: 0.67694; model 0.67622: the probe interpolates
  the table at the eight cell centres around the origin, closer at M/8).
- Not predicted, noted: the squared Hamiltonian-constraint norm at t = 0 is 0.149 on the
  M/8 mesh against 0.0235 on the M/4 mesh (6.3 times). The initial data put the smooth
  table metric next to the deposited particle source; a ratio near 2^3 = 8 is what
  particle noise in the deposit gives when the cell volume of the central region shrinks
  by 8 [JUDGEMENT], so the initial constraint violation of the wave-2 runs is mostly
  particle noise, not truncation error. Whether this larger initial mismatch kicks the
  radial mode harder at M/8 is part of what run (i) shows (it works against M8.1).

## 2026-11-20 22:29 UTC Entry 4: what the D1 periods say about the threshold on the M/4 mesh

Arithmetic on the fitted periods of run C-20261120-222211-aa1be86 (no new run):
omega^2 = (2 pi/P)^2 is 2.48e-4 (CC1) and 3.12e-4 (CC2) per M^2 from the cosine fits,
2.29e-4 and 2.56e-4 from the sine-with-trend fits; the ratio CC2/CC1 is 1.26 (1.12), close
to the 1.38 of the F21-index fluid (periods 305 and 358 M), while a collisionless mode
with its zero at the E_b maximum would give omega^2(CC1) = 0. A straight line through the
two points crosses zero at y0 = 0.41 (cosine) or 0.51 (sine with trend); the F21-index
fluid onset is y0 = 0.372 (lead's L15, run C-20261119-151502-cb831a8).

Reading [JUDGEMENT; two points, large amplitude, not a measurement of the onset]: on the
M/4 mesh the threshold model CC1 behaves as a stable cluster with a finite radial
frequency, i.e. the code's collisionless onset lies above y0 = 0.334 on this mesh. Two
causes are possible: (a) the M/4 mesh stabilises (a softened source raises omega^2; the
CIC cloud of the deposit has a variance of dx^2/6 per axis that the default compensation
does not cancel, and the first paper's "compensation that also cancels the cloud width"
moved alpha_c by 3.6e-3 in the y_c = 0.819 cluster, `paper/sections/tables/tab_outcomes.tex`
line 108 [BACKGROUND]); (b) the onset of the code's Einstein-Vlasov system is not at the E_b
maximum. Run (iii) (CC1 at M/8) separates them: (a) predicts a clearly longer period at
M/8 (prediction M8.2 already asks P(CC1, M/8) >= 0.9 P(CC1, M/4)); (b) an unchanged one.
Consequence for block A of SCAN.md (y0 = 0.314-0.354): if (b), or if (a) persists at M/8,
none of the five models need collapse within 1000 M on the mesh it runs on, and the
fate-based bracket would come out empty; the grid would then have to reach y0 of about
0.37-0.42, or the threshold be located by the zero of omega^2(y0) measured from the
excursion itself, which every control provides at no extra cost.
The first paper's stable y_c = 0.819 cluster also drifted less at half the cell spacing
(mean of the last two extrema of alpha_c - alpha_c(0): -0.0039 against -0.0071 over
300 M, `tab_outcomes.tex` line 110 [BACKGROUND]), a factor 0.55 for one halving.

## 2026-11-20 22:29 UTC Entry 5: predictions for the optional particle-number leg (v)

Run (v): cc2_kninf_N1e4 (`inputs/cc2_kninf_N1e4.athinput`, the wave-2 cc2 deck with the
N = 1e4 file of wave 1, run C-sidm-20261115-120610-b4592be; same model, same seed and
sampler, byte-identical table; M/4 mesh; 300 M), submitted only if the card cap allows
after (i)-(iv). Against cc2_kninf at N = 1e5 (run C-20261115-171059-4b70228):
- N.1 Initial constraint violation: H-norm2(0) about 10 times 0.0235 (between 5 and 20
  times) if, as the smoke suggests (entry 3), it is particle noise of the deposit
  (variance per cell proportional to 1/N).
- N.2 Ripple (residual rms of the cosine fit): about sqrt(10) = 3.2 times 8.0e-4 (between
  2 and 5 times) if the ripple is particle noise.
- N.3 Amplitude ratio R_N = A(1e4)/A(1e5): in [0.75, 1.33] if the excursion is set by the
  mesh (or by the continuum initial data); about 3 (above 2) if it is the response to
  particle noise of the initial state. The period stays within 20 % of 355-393 M either
  way, unless the amplitude grows enough to change it.

## 2026-11-20 22:30 UTC Entry 6: a third point of omega^2(y0) from the decisive package

The decisive package runs a collisionless control of a less compact King model, d3_kninf
(y0 = 0.26, M/4 mesh, N = 1e5, 300 M; `../decisive/inputs/d3_kninf.athinput`, list
`d3_job3.list`). Its alpha_c record gives a third point of the excursion period against y0
at no cost to this package. Prediction (before that run exists): the cosine-fit period of
d3_kninf lies in [260, 380] M and below that of CC2 in the same fit form, and its amplitude
A is below CC2's 0.0086 (a stiffer model responds less). The fluid period with the F21
index at y0 = 0.26 is 260 M [TO VERIFY: quick evaluation of models/fluid_onset.omega2,
N = 600; `controls.py --pulsation` now includes y0 = 0.26 and registers it with the next
analysis run]. Refuted if P(0.26) >= P(CC2) or A(0.26) >= A(CC2).
- Registered (run C-20261120-223139-2526c6d, D1b: D1 rerun with corrected figures, numbers of
  D1 unchanged): at y0 = 0.26 the fluid period is 259.7 M with the F21 index, 325.9 M with
  the Juttner Gamma_1(theta_E), 317.5 M with the scaled proxy (the [TO VERIFY] above is
  now [VERIFIED]). Figures of D1b replace those of D1 in `figs/` (looked at).

## 2026-11-20 22:35 UTC Entry 7: PAUSED (locks/PAUSE written 22:33 UTC, five-hour window 97 %)

Where I stopped:
- Done: D1 and D1b (processor analysis of the controls, pulsation periods), the M/8 smoke,
  decks and lists of (i)-(v), predictions M8, A, N and for the y0 = 0.26 control of the
  decisive package (entries 2, 5, 6).
- Card job (i) cc2_kninf_M8 is queued (run C-20261120-222533-ce50a86, Slurm 4741,
  PENDING at 22:34 UTC); per decision 0019 it is left in the queue and may run by itself.
  When it has finished: `harness/bin/nrpic-run finish C-20261120-222533-ce50a86`, then the
  compare run of README "How to rerun" with `cc2_M8=cc2:$R/C-20261120-222533-ce50a86/cc2_kninf_M8`,
  then judge M8.1-M8.4 for CC2.
- Not submitted (pause): (ii), (iii), (iv) and the optional (v); exact commands in
  README "Pending runs". Nothing has been judged against M8, A, N yet.
- A side observation for the next session: the free-phase fit (sine with trend) puts the
  phase at 4.76 and 4.89 rad (CC1, CC2), i.e. within 0.05 and 0.18 rad of 3 pi/2, where
  a + b t + A sin(x + 3 pi/2) = a + b t - A cos(x): the free fit finds independently that
  the excursion starts at a turning point (run C-20261120-222211-aa1be86, `controls.json`).
- Card-hours used by this package so far: 0 (job (i) has not started).

## 2026-11-21 07:57 UTC Entry 8 (C-sidm lead, batch 2b): outcome of run (i) and of entry 6

Run (i) cc2_kninf_M8 (run C-20261120-222533-ce50a86, Slurm 4741) ran 23:49:16-00:30:46 UTC
on 2026-11-20/21, exit 0, 300 M; closed by the lead with `nrpic-run finish`. Analysis with
this package's `compare.py` as README "How to rerun" prescribes: run
C-20261121-075359-26e3b31 (`fig_cc2_M8.png` looked at); the lead's own cosine fit (run
C-20261121-075336-49f92da) agrees on the M/4 control (P 355.5 M, A 0.00859) and finds no
cosine form at M/8 (its grid fit runs to the edge, P > 1400 M with A < 0).

| | M/4 (wave 2) | M/8 (run i) | ratio |
|---|---|---|---|
| largest 20 M mean of alpha_c - alpha_c(0), at | 0.0179 at 208 M | 0.0018 at 125 M | 0.099 |
| cosine fit A, P | 0.0086, 355 M | 0.0019, 272 M (poor fit) | 0.22, 0.77 |
| sine with trend A, P | 0.0099, 393 M | 0.0025, 425 M | 0.25, 1.08 |
| alpha_c - alpha_c(0) at 300 M (+-5 M mean) | +0.0041 | -0.0041 | |
| areal radius of the 50 percent shell at 300 M | +1.1 percent | -1.5 percent | |
| H-norm2, mean 100-300 M | 8.6e-4 | 7.9e-3 | 9.3 |
| ripple rms | 8.0e-4 | 1.5e-3 | 1.9 |

Against entry 2:
- M8.1 R = 0.22 (cosine), 0.25 (sine with trend), 0.10 (largest 20 M mean): inside the bet
  [0.15, 0.65] for the fitted amplitudes, below it for the maximum; not refuted (R < 0.75).
  By the decision rule the outward excursion of the M/4 control is numerical, of second order
  or faster in the cell size [VERIFIED for CC2, one seed].
- M8.2 FAILED as written: the M/8 record is not a cosine started at a turning point (maximum
  of 0.0018 at 110-125 M, back through zero at about 215 M, then falling to -0.0041 by 300 M),
  so no period comparable with 355-393 M can be read; the clause for R < 0.3 (period from the
  times of the maximum and of the return) gives a half period of about 215 M, 40 percent
  shorter than at M/4.
- M8.3 HOLDS: the late H-norm2 rises 9.3 times (> 1.5), so the floor is particle noise of the
  deposit, not truncation error.
- M8.4 HOLDS: 456 MeshBlocks, 8 physical levels, np = 1e5 and sum_m bit-identical to 300 M;
  2489 s for 300 M (8.30 s per M, 41.5 min) inside 6.8-9.7 s per M.
- Not predicted [VERIFIED, same runs]: on the M/8 mesh the collisionless CC2 control contracts
  slowly after about 200 M (alpha_c -0.0041 and areal r50 -1.5 percent at 300 M, mean W up
  by 0.002). [JUDGEMENT] Two readings: the start of the real slow mode once the mesh no longer
  pushes the cluster outward, or numerical relaxation by the nine times larger deposit noise.
  Either way the M/8 control is not stationary either, and collisional effects must still be
  read against a control of the same mesh and seed.

Entry 6 (d3_kninf, decisive job 3, run C-20261121-035737-295e5c3; the lead's fit): P = 282 M in
[260, 380] and below P(CC2) = 355 M; A = 0.0022 < 0.0086: HOLDS. omega^2 = (2 pi/P)^2 is
4.96e-4 per M^2 at y0 = 0.26, against 3.12e-4 (CC2) and 2.48e-4 (CC1) on the same mesh.

Mesh rule (entry 2): R <= 0.65, so block A of SCAN.md runs on M/8 (or as an M/4-M/8 pair at
the bracket); run (iii) (CC1 at M/8) is now the most informative next card job, then (v).
Runs (ii) and (iv) (continuations at M/4) lose most of their purpose: the M/4 excursion is
numerical [JUDGEMENT]. Card time of run (i): 0.69 card-hours of allocation (sacct elapsed
41:32).

## 2026-11-21 12:54 UTC Entry 9 (helper, batch 3): state; predictions for run (iii) after run (i)

State found: entries 1-8 committed; run (i) closed and judged (entry 8); the lead dropped
(ii) and (iv) (`../HANDOFF.md` "drift" and "Lead decisions of this session": block A of SCAN.md
on M/8 after run (iii)). This session: (iii) cc1_kninf_M8, then (v) cc2_kninf_N1e4, one job at
a time. Pause flag absent; no C-* job queued or running (12:55 UTC); the cards are free but
one (another user's job). Card-hours so far 0.69 of 3.0.

Predictions for run (iii) (cc1_kninf_M8, release card executable, 300 M), written before it
is submitted, sharpened by what run (i) showed for CC2 (entry 8):
- M8.1' The outward excursion is mostly the mesh for the threshold model too: the largest
  20 M mean of alpha_c - alpha_c(0) is at most 0.35 x 0.0330 = 0.0116 (R_max <= 0.35; CC2
  gave 0.10). Refuted if R_max > 0.35: then the M/4 excursion of CC1 is not mostly numerical.
- M8.2' Late contraction at least as fast as CC2 on the same mesh: alpha_c(300 M) -
  alpha_c(0) (mean over 295-300 M) below -0.0041 (CC2 at M/8), because CC1 is the softer model
  [JUDGEMENT, 60 %]. Refuted if it is above -0.0041.
- M8.2'' No collapse within 300 M: the central lapse stays above 0.5 [JUDGEMENT, 85 %]. A
  collapse (alpha_c < 0.3) refutes and would put the code's M/8 collisionless threshold below
  y0 = 0.334 (or show a numerical instability of the finer mesh).
- M8.3' The late H-norm2 (mean 100-300 M) is 6-12 times that of CC1 at M/4 (8.5e-4), i.e.
  5.1e-3 to 1.0e-2, near CC2's 7.9e-3 at M/8 (same seed, same deposit noise). Refuted outside.
- M8.4' 456 MeshBlocks, np = 1e5, sum_m bit-identical, 7.5-9.1 s per M (8.30 s per M of run
  (i) +- 10 %), 300 M reached within the 52 min limit. Refuted if the run stops early.
- M8.5' The ripple of CC1 and CC2 at M/8 is the same realisation: the residuals about their
  own 40 M running means correlate above +0.5 (at M/4 the cosine-fit residuals gave 0.72).
  Refuted below +0.5.

## 2026-11-21 12:57 UTC Entry 10: an M/8 continuation (vi) in place of the dropped (ii), (iv); predictions

Why [JUDGEMENT]: block A of SCAN.md is to run on M/8 for 1000 M (lead's decision,
`../HANDOFF.md`). Run (i) shows the stable model CC2 (y0 = 0.314, below the threshold)
contracting on M/8 after 200 M, faster towards the end (alpha_c - alpha_c(0) at 250 and
300 M: -0.0012 and -0.0041, run C-20261121-075359-26e3b31 `compare_cc2_M8.json`). If that
contraction runs away within 1000 M, a stable model collapses on the mesh of block A and the
fate-based bracket is wrong; if it turns, M/8 is fit for the scan. One 52 min job continues
run (i) from its restart at 300 M (`rst/cc.00003.rst`, written 00:30:45 UTC at the end of run
(i); its executable `batch.list.exe` has the sha256 f9f2dc12... of the release card
executable). Order of this session: (iii) (queued), then (vi), then (v) (cheapest), within the
cap: 0.69 + about 0.72 + 0.87 + 0.3 = 2.6 card-hours.

Predictions for (vi) cc2_kninf_M8_A (restart of (i) at 300 M, `time/tlim=1000`, cut at 52 min):
- VI.1 Exact continuation: np = 1e5 and sum_m bit-identical to run (i); the first alpha_c
  records after 300 M join the last records of (i) within 1e-3. Refuted otherwise.
- VI.2 Bounded: the contraction turns. The 40 M mean of alpha_c - alpha_c(0) has a minimum
  between 330 and 600 M, no lower than -0.02, and alpha_c stays above 0.5 [JUDGEMENT, 55 %].
  Refuted by a monotone decline to the end of the segment. If the decline steepens (below
  -0.03 at the end) I read it as a runaway towards collapse of a model that should be stable,
  i.e. M/8 at N = 1e5 is not fit for block A without more particles or a stronger filter.
- VI.3 The H-norm2 floor stays at 7-9e-3 (mean over the segment within 1.5 times the
  100-300 M mean 7.9e-3 of (i)). A growth above that is a numerical instability.
- VI.4 Cost: 7.5-9.1 s per M, so the segment ends between 640 and 710 M.
Method note (smoke, not registered, `scratch/C-sidm/tmp/drift_smoke`): the new `compare.py
--pair` (residuals about the 40 M running mean) gives +0.57 for CC1 against CC2 on M/4; the
registered value comes with the analysis of (iii). Threshold of M8.5' (entry 9) unchanged.

## 2026-11-21 12:59 UTC Entry 11: a fourth prediction for run (v), on noise relaxation

Run (i) leaves two readings of the slow contraction of CC2 on M/8 after 200 M (entry 8): the
real slow mode, or relaxation driven by the deposit noise, whose H-norm2 floor is 9.3 times
that of M/4 at the same N. Run (v) (M/4, N = 1e4) should have a noise floor of the same size
(N.1 predicts about 10 times 8.6e-4) on the mesh whose outward push we know. So:
- N.4 If the M/8 contraction is noise relaxation, run (v) contracts relative to the N = 1e5
  control on the same mesh: alpha_c(1e4) - alpha_c(1e5), 20 M means at 280-300 M, below
  -0.003, with sum mW/sum m rising relative to the control. Within +-0.003 means the noise
  floor alone does not contract the cluster within 300 M, and the M/8 contraction is the
  finer mesh's own (the slow mode, or an error of the other sign). [JUDGEMENT, 50/50.]
  Caveat written now: the N = 1e4 sample has its own sqrt(N) deviation from the model, which
  shifts the start of the radial mode; a difference that is already there by 50 M and does
  not grow is that, not relaxation.

## 2026-11-21 14:01 UTC Entry 12: outcome of run (iii) (CC1 at M/8); run (vi) queued

Run (iii) cc1_kninf_M8: run C-20261121-125459-f03c4ba (Slurm 4792, 13:18-13:59 UTC, exit 0,
300 M, sacct elapsed 41:09 = 0.69 card-hours). Analysis: run C-20261121-140057-92742cf
(`compare.py --tag cc_M8`, all four controls; `fig_cc_M8.png` looked at: top left the alpha_c
excursions, top right the areal r50, bottom the H-norm2 and mean W; the note "thin: record ..."
overlaps the legend's first line, fixed in the script for the next run).

Numbers [VERIFIED, `compare_cc_M8.json` of run C-20261121-140057-92742cf]:

| | CC1 M/4 | CC1 M/8 | CC2 M/4 | CC2 M/8 |
|---|---|---|---|---|
| largest 20 M mean of alpha_c - alpha_c(0), at | 0.0330 at 206 M | 0.0046 at 196 M | 0.0179 at 208 M | 0.0018 at 125 M |
| alpha_c - alpha_c(0), +-5 M means at 100 / 200 / 250 / 300 M | 0.0163 / 0.0329 / 0.0283 / 0.0173 | 0.0026 / 0.0046 / 0.0022 / -0.0020 | 0.0108 / 0.0176 / 0.0113 / 0.0041 | 0.0012 / 0.0012 / -0.0012 / -0.0041 |
| cosine fit A, P; sine with trend A, P | 0.0154, 399; 0.0168, 415 | 0.0020, 317; 0.0044, 499 | 0.0086, 355; 0.0099, 393 | 0.0019, 272; 0.0025, 425 |
| areal r50 at 300 M / initial - 1; largest change | +4.4 %; 9.0 % | -0.9 %; 0.9 % | +1.1 %; 5.0 % | -1.5 %; 1.5 % |
| mean W at 300 M minus initial | -0.0066 | +0.0011 | -0.0016 | +0.0022 |
| H-norm2 at t = 0; mean 100-300 M | 0.0230; 8.5e-4 | 0.150; 7.9e-3 | 0.0235; 8.6e-4 | 0.149; 7.9e-3 |
| lowest alpha_min on the grid | 0.662 | 0.659 | 0.677 | 0.671 |
| ripple rms about the 40 M mean | 6.0e-4 | 6.8e-4 | 5.7e-4 | 6.2e-4 |

Ratios M/8 over M/4: CC1 max of the 20 M mean 0.138, cosine A 0.128, sine-with-trend A 0.261,
H-norm2 floor 9.2, H-norm2(0) 6.5; CC2 0.099, 0.221, 0.253, 9.3, 6.4. Residual correlations about
the 40 M means: CC1 against CC2 on M/4 +0.57, on M/8 +0.25; CC1 on M/4 against M/8 +0.20.

Against entry 9:
- M8.1' PASS: R_max = 0.138 (CC1) <= 0.35, like CC2 (0.099). On both models the outward
  excursion of the M/4 controls shrinks by a factor 7-10 at M/8: it is numerical, of second
  order or faster in the cell size [VERIFIED for both models, one seed and one N].
- M8.2' FAILED: alpha_c(300 M) - alpha_c(0) = -0.0020 for CC1, above the -0.0041 of CC2. CC1 on
  M/8 rises a little longer (to 196 M against 125 M) and turns down later; by 300 M it has
  contracted less than CC2 (areal r50 -0.9 % against -1.5 %). Its late decline (250 -> 300 M:
  -0.0042) is as steep as CC2's (-0.0029), so the difference is the later turn, not the slope.
- M8.2'' PASS: no collapse; alpha_min on the grid >= 0.659.
- M8.3' PASS: late H-norm2 7.9e-3, 9.2 times M/4, the same as CC2 on M/8 (the two curves lie on
  top of each other in the figure).
- M8.4' PASS: 456 MeshBlocks at every record, np = 1e5, sum_m bit-identical, 0 unconverged
  pushes, 2466.7 s for 300 M = 8.22 s per M.
- M8.5' FAILED: the CC1-CC2 correlation of the ripple on M/8 is +0.25 (< 0.5), while on M/4 the
  same measure gives +0.57. The constraint noise is the same realisation on M/8 (identical
  H-norm2 curves), but the central lapse ripple on M/8 is not mostly shared. [JUDGEMENT] On the
  finer cells the probe sees cell-scale noise that decorrelates between two models whose
  particles sit at slightly different (scaled) positions; on M/4 a larger-scale shared part
  dominates.

Reading [JUDGEMENT]:
1. The question of the package is answered for the outward excursion: it is the mesh. Both
   models, M/4 -> M/8, lose 86-90 % of the largest excursion; the 300-400 M "periods" of D1 are
   the response of the cluster's slow radial mode to a mesh-made push, not a property to read
   the threshold from. Reading 2 of entry 2 and entry 4 (the code's onset above 0.334 on M/4)
   stands for M/4 only.
2. Neither model is stationary on M/8: after the small rise both contract slowly (alpha_c down,
   r50 down, mean W up), CC2 from about 200 M, CC1 from about 250 M. A Richardson estimate that
   treats M/4 and M/8 as asymptotic (arithmetic on the +-5 M means above, not a test) gives for
   the continuum a contraction with p = 2, y8 - (y4 - y8)/3: CC1 -0.0020, -0.0048, -0.0065,
   -0.0084 and CC2 -0.0020, -0.0043, -0.0054, -0.0068 at 100, 200, 250, 300 M; with p = 3 the
   same sign from 200 M on. So the next question is whether this contraction is real (slow
   evolution of the collisionless King models in this code), relaxation by the deposit noise
   (nine times larger floor on M/8), or turns: runs (vi) (CC2 on M/8 to about 650 M) and (v)
   (noise floor of M/8 on the M/4 mesh) separate these.

Card-hours so far: (i) 0.69, (iii) 0.69 = 1.38 of 3.0. Run (vi) submitted 14:00 UTC as
C-20261121-140023-b0f113e (Slurm 4804), pending behind six jobs of other owners.

## 2026-11-21 14:03 UTC Entry 13: predictions for test D2 (noise heating from the particle records, no card)

While (vi) waits for a card: every control writes all 1e5 particles with the metric at their
positions every 25 M (`traj_ntrack = 100000`), so the Killing energy E_K = alpha W - beta.u of
each particle is known at 13 times. In a smooth slowly changing potential E_K changes
coherently (the same for particles on the same orbit); noise of the deposited source adds a
random walk. Test D2 (`scripts/diffusion.py`, processors): per particle dE = E_K(t) - E_K(0);
coherent part = mean of dE in 200 cells of (decile of E_K(0)) x (decile of the initial radius)
x (sign of x.u at t = 0); incoherent part = the rest, variance s2(t); fit s2 = a + D t over
25-300 M (a: the instantaneous noise of the metric at the particle; D: diffusion of E_K);
t_D = var(E_K(0))/D, the time in which the noise would randomise the energy spread.
Predictions (written before the script exists):
- D2.1 s2 grows with t in all four controls, close to linearly from 25 to 300 M (D > 0, the
  linear fit explains more than 80 % of the variance of s2 over those times).
- D2.2 Noise heating follows the noise floor: D(M/8)/D(M/4) in [4, 15] for both models (the
  H-norm2 floor ratio is 9.2-9.3). Refuted below 2 or above 30. Caveat written now: on M/4
  part of the large coherent pulsation may survive the 200-cell subtraction and inflate
  D(M/4), so a low ratio is then a lower bound; the M/4 value at 25-75 M, before the
  pulsation is large, is the check.
- D2.3 D of CC1 and CC2 agree within a factor 1.5 on the same mesh (same seed and sampler).
- D2.4 On M/8, t_D lies between 3e3 and 1e5 M [JUDGEMENT, wide]: a 300 M run then
  randomises 0.3-10 % of the energy spread, enough for the percent-level contraction of the
  M/8 controls. t_D > 1e5 M rules noise heating out as its cause.

## 2026-11-21 14:05 UTC Entry 14: outcome of D2 (noise heating); sharper predictions for (v)

D2: run C-20261121-140356-f933a0e (numbers) and C-20261121-140431-b4786c4 (same numbers,
figure on a linear axis; `fig_diffusion.png` looked at: left the incoherent variance of
dE_K against t with the fits, right the mean of dE_K). [VERIFIED, `diffusion.json`]

| | CC1 M/4 | CC1 M/8 | CC2 M/4 | CC2 M/8 |
|---|---|---|---|---|
| D over 25-300 M (per M); R^2 | 4.04e-8; 0.989 | 6.47e-8; 0.994 | 3.79e-8; 0.985 | 5.83e-8; 0.995 |
| D over 25-75 M | 3.17e-8 | 5.34e-8 | 2.85e-8 | 4.63e-8 |
| var(E_K(0)); t_D = var/D (full fit) | 2.59e-3; 6.4e4 M | 2.59e-3; 4.0e4 M | 2.34e-3; 6.2e4 M | 2.34e-3; 4.0e4 M |
| mean of dE_K at 200 M; at 300 M | +0.0137; +0.0068 | +0.0014; -0.0014 | +0.0073; +0.0017 | 0.0000; -0.0024 |

- D2.1 PASS: the incoherent variance grows linearly from the first record on (s2/t nearly
  constant; R^2 0.985-0.995), a random walk of the particle energies.
- D2.2 FAILED: D(M/8)/D(M/4) = 1.60 (CC1), 1.54 (CC2); 1.68 and 1.62 over 25-75 M, before the
  pulsation of M/4 is large, so the M/4 value is not inflated by it. The H-norm2 floor is 9.2
  times higher on M/8, the energy diffusion only 1.6 times: most of the extra constraint noise
  of the finer cells is at the cell scale and hardly moves the particle energies.
- D2.3 PASS: CC1/CC2 = 1.11 (M/8), 1.07 (M/4).
- D2.4 PASS as written: t_D = 4.0e4 M on M/8 (6.2-6.4e4 M on M/4); a 300 M run randomises
  0.75 % (M/8) and 0.47 % (M/4) of the energy spread.

Reading [JUDGEMENT]: noise heating at N = 1e5 is slow and nearly the same on both meshes.
If it drove the slow contraction of the M/8 controls, the M/4 controls would carry 0.6 of
the same drive, hidden under their mesh-made pulsation; the Richardson estimate of entry 12
points the same way. So the contraction is not something the finer mesh adds by itself; it
is either relaxation by the particle noise (then it scales as 1/N) or a slow evolution of
the models in this code. Run (v) at N = 1e4 on M/4 separates them.

Sharper predictions for (v), added before it is submitted (N.1-N.4 of entries 5 and 11 stand):
- N.5 D(1e4)/D(1e5) on M/4 (`diffusion.py`, same cells) in [5, 15] (energy diffusion of
  particle noise scales as 1/N). Refuted outside.
- N.6 If the contraction is noise relaxation, its rate scales with D: the mean of dE_K of run
  (v) minus that of the N = 1e5 control on M/4 is below -0.005 at 300 M (several times the
  -0.0014 to -0.0024 of the M/8 runs, whose D is 0.15 of the expected D(1e4)). Within +-0.002
  means noise relaxation is not the cause of the M/8 contraction.

## 2026-11-21 14:17 UTC Entry 15: where this session stops

- Done this session: run (iii) and its analysis (entry 12), test D2 (entry 14), the M/8
  continuation (vi) prepared, predicted (entry 10) and submitted, predictions N.4-N.6 for (v),
  README with results, pending runs and the recommendation for block A.
- Queued, not started: run (vi) C-20261121-140023-b0f113e (Slurm 4804), behind seven jobs of
  other owners at 14:16 UTC (both cards busy); at their time limits it starts about 16:30-17:20
  UTC, after this session's window. It runs by itself; the closing and analysis commands are
  in README "Pending runs", the predictions in entry 10.
- Not submitted: run (v) (one job of this package at a time; it follows (vi)); command in
  README "Pending runs", predictions N.1-N.6 (entries 5, 11, 14).
- Card-hours used by this package: 1.38 ((i) 0.69, (iii) 0.69); (vi) will add about 0.87,
  (v) about 0.3: 2.55 of the 3.0 cap.

## 2026-11-21 16:35 UTC Entry 16 (C-sidm lead, batch 4a): outcome of run (vi)

Run (vi) C-20261121-140023-b0f113e (Slurm 4804, 15:38-16:30 UTC, COMPLETED, exit 0, sacct
elapsed 52:03 = 0.87 card-hours) continued run (i) from its restart at 300 M to 680 M; closed by
the lead with `nrpic-run finish`. Analyses: the package's `compare.py --tag cc2_M8A` (run
C-20261121-163135-57f9296, `fig_cc2_M8A.png` looked at) and the lead's own reader
(`../stage/review_wave3/rv_batch4a.py --part vi`, run C-20261121-163109-c8fff37,
`rv_drift_vi.png` looked at; the first attempt C-20261121-163051-16356b2 FAILED on the
header-less history of a restarted run). Both give the same numbers [VERIFIED]:

| t (M) | 300 | 400 | 500 | 600 | last 40 M (640-680) |
|---|---|---|---|---|---|
| alpha_c - alpha_c(0), +-5 M mean | -0.0043 | -0.0118 | -0.0151 | -0.0186 | -0.0216 |

Areal r50 -6.3 percent and mean W +0.0097 at 680 M (they track alpha_c with correlations
0.996 and -0.997); lowest alpha_min on the grid 0.652; np = 1e5, sum_m identical, 0
unconverged pushes; H-norm2 7.87e-3 after 300 M (7.94e-3 over 100-300 M); join at 300 M
within 8.7e-6 in alpha_c. Lead's energy diffusion: D = 7.8e-8 per M over 300-675 M against
5.9e-8 over 25-300 M; mean change of E_K -0.0103 at 675 M.

Against entry 10:
- VI.1 HOLDS (exact continuation).
- VI.2 FAILED: no turn; the decline runs to the end of the segment, monotone in the 40 M
  mean, and ends below -0.02. Its runaway clause (below -0.03 at the end, steepening) is not
  met either: the slope is about -0.0075 per 100 M over 300-400 M and -0.0035 per 100 M after
  400 M, steady, not steepening.
- VI.3 HOLDS (floor 7.87e-3, within 1.5 times 7.94e-3).
- VI.4 HOLDS (380 M in 52:03, 8.2 s per M; ended at 680 M).
The lead's L28 (`../JOURNAL.md`): "no turn" and "no collapse" hold; the end value -0.0216 lies
outside the predicted [-0.015, -0.004]: L28 FAILED on its interval.

Reading [JUDGEMENT]: on M/8 at N = 1e5 the stable King model CC2 contracts steadily from about
200 M on, by about 0.02 in the central lapse and 6 percent in r50 in 500 M, with no sign of
turning. A collisionless equilibrium should be stationary, so this is numerical (an error of
the finer mesh of the other sign, or relaxation by particle noise) until shown otherwise. Run
(v) (N = 1e4 on M/4, predictions N.1-N.6) tests the 1/N scaling. Consequence for block A: a
fate read after 1000 M on M/8 at N = 1e5 is biased toward collapse; fates must be read
against a control of the same mesh, seed, N and length, and the bias must be measured before
the bracket is trusted.
