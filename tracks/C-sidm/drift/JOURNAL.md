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

## 2026-11-20 22:30 UTC Entry 2: outcome of D1; predictions for the card runs (i)-(iv)

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
