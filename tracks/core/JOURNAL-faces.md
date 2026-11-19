# Journal of the package faces (outer boundaries of the spacetime solver)

Owner core, worktree `wt/core-faces`, branch `core/z4c-faces`. Wave 3a, 2026-11-19.
Labels: [VERIFIED] (run id or file and line), [BACKGROUND] (literature with locator),
[JUDGEMENT], [TO VERIFY]. Package directory: `tracks/core/analysis/faces/`.

## 2026-11-19, entry 1: what the code does at an outflow face; candidates; predictions

Read: `CLAUDE.md`, `coord/CHARTER.md` to "Owners", decisions 0010, 0016, 0017, brief lines
493-553, 688-706, 834-860, `harness/RULES.md`, `scripts/README.md`; of the source
`bvals/physics/z4c_bcs.cpp`, `z4c/z4c_Sbc.cpp`, `z4c/z4c_tasks.cpp`, `z4c/z4c.cpp`,
`z4c/z4c_calcrhs.cpp` (loops), `utils/finite_diff.hpp`; test F of
`tracks/core/JOURNAL-idsolve.md` (branch core/id-solver, entries 8 and 12) and the
boundary layer of `tracks/core/JOURNAL-clump.md` (branch core/clump-curvature, line 334);
`tracks/D-bh-dress/puncture_drift/README.md` (branch track/D-bh-dress).

### What the runs of this repository use [VERIFIED from the source at 27b2ced]

1. Every input of `problems/` that is not periodic sets `outflow` on all six faces (33
   inputs; `grep ix1_bc problems cosmo`), none sets `<z4c> extrap_order` or `user_Sbc`.
2. Ghost cells of all 22 Z4c variables at an outflow (also diode, vacuum) face: Lagrange
   extrapolation along the face normal from the outermost active cells,
   `z4c_bcs.cpp:172-178`, of order `extrap_order` = max(2, min(nghost, 4, input)),
   default 2, i.e. LINEAR extrapolation from two cells (`z4c.cpp:165`). Applied after
   every Runge-Kutta stage, x1 faces first, then x2, then x3 over the full range
   including ghost cells, so edges and corners are extrapolated twice or three times.
3. Right-hand side in the outermost layer of active cells (`z4c_Sbc.cpp:93-120`,
   `Z4cBoundaryRHS`, after `CalcRHS`): for Theta, Khat, Gamma^i and A_ij it is replaced
   by `-v (f/r + s^k d_k f)` with s = x/r from the mesh origin, v = 1 (sqrt 2 for
   Khat), asymptotic value 0, fall-off 1/r, derivatives centred of second order (they
   use the first ghost cell). chi, g_ij, alpha, beta^i keep the full right-hand side
   computed with the extrapolated ghost cells. Edge and corner cells are overwritten by
   two or three of the loops with the same value.
4. All other active cells use the full right-hand side: centred sixth-order stencils
   reach three cells (nghost = 4), the advective stencils and the dissipation four.
   So the three layers of cells next to the boundary layer read extrapolated ghosts.
5. The constraint monitor (`ADMConstraints`) uses the same stencils and ghost cells.

Literature [BACKGROUND]: this is the scheme of GR-Athena++, arXiv:2101.08289
(`kb-data/raw/arxiv/2101.08289/v1/src/paper20210120.tex` lines 1247-1252: Sommerfeld on
{Khat, Gamma, Theta, A_ij}, "not optimal, as it is not constraint-preserving"; lines
1366-1378: ghost layer by Lagrange extrapolation, "typically N_g + 1 points", centred
second-order derivatives in the condition "crucial for numerical stability"), which
follows arXiv:1212.2901 (`.../1212.2901/v1/src/paper20121212.tex` lines 483-499: the
Sommerfeld set with speeds sqrt(mu_L) alpha for Khat, alpha for Theta and A_ij, and
advection by the shift; lines 395-412: the constraint-preserving alternative, for Theta
`d_t Theta = -alpha d_s Theta + beta^i d_i Theta`). The radiative condition with a
non-wave part, `f = f0 + u(r - v t)/r + h(t)/r^n`, where the right-hand side one point
inside fixes h', is arXiv:gr-qc/0206072 (`.../gr-qc_0206072/v1/src/shiftpunctures.tex`
lines 1492-1555; "taking n = 3 almost completely eliminates the bad transient").
Differences of this code from the cited schemes: linear extrapolation instead of
N_g + 1 points; speeds without the lapse; no advection term.

### Candidate causes of the face layer

- H1, monitor: with linear ghosts the sixth-order second derivative across a face has
  the error -1.117 f'' in the boundary cell, +0.117 f'' in the next, -0.011 f'' in the
  third (weights 3/2, -3/20, 1/90 times the ghost errors delta(delta+1)/2 f'' dx^2;
  derived here); the first derivative has -0.40 f'' dx, +0.10 f'' dx, -0.017 f'' dx. The
  monitor therefore reads a residual of the size of the second-derivative terms in
  the boundary cell at t = 0 for exact data: no property of the data.
- H2, Sommerfeld with the wrong fall-off: for a stationary field f ~ r^-m the condition
  gives d_t f = v (m - 1) f / r instead of 0. Painleve-Gullstrand exterior: Khat and
  A_ij ~ r^(-3/2), m = 3/2; Bowen-York: A_ij ~ r^-2, m = 2; Brill-Lindquist: K_ij = 0,
  no such term.
- H3, the full right-hand side next to the face reads the linear ghosts: an error of
  0.117 (second cell) of the second-derivative terms in d_t A_ij and d_t Theta, for any
  data, also K_ij = 0.
- H4, dissipation: the eighth difference across the face gives 10 f'' dx^2 in the
  boundary cell, a rate 0.5 * 2^-8 * 10 f'' dx = 0.02 f'' dx for every variable.

### Configurations (processors; a 64^3 Z4c step costs about 20 s on one core here)

Run `faces_bench` (unregistered timing, `scratch/core/tmp/faces_bench`): 1.3e4
zone-cycles per second and core with the standard processor build, 1.5e4 with -O3; so
the tests are small: cells of 1 at the faces, faces at 16, and a reference with the
faces at 32 on the same cells. The difference between the two runs is the effect of the
faces at 16 (until the faces at 32 are felt: t = 11.3 at r = 16 for speed sqrt 2).

- ball: `inputs/ball.athinput`, marginally bound ball M = 0.5, R_b = 6, smooth edge of
  half-width 1.5 (matter inside 7.5), 32^3 cells of 1, 1+log lapse from alpha = 1, zero
  shift, to t = 16. Exterior K = -(3/2) sqrt(2M/r^3) = -0.0246 at r = 15.5.
- punc: `inputs/punc.athinput`, Brill-Lindquist puncture m = 1, precollapsed lapse,
  static refinement to cells of 1/4 (root cells of 1 beyond 8), to t = 12.
- boost: the same with Bowen-York momentum 0.3 along x and the closed-form correction.

### Predictions, written before any of these runs was looked at [JUDGEMENT]

Plan a0 (t = 0, no step; `plans/a0_t0.json`), H1:
 (a0-a) punc, order 2: the largest |H| of the monitor sits in the boundary layer of
   cells at the face centres and is 8 * 1.117 * M / r^3 = 2.4e-3 at r = 15.5 (H is
   -8 lap(psi) to leading order, psi'' = M/r^3 for psi = 1 + M/2r); within a factor 1.5.
   The second layer has 0.105 of it, the third 0.010 (signs alternate).
 (a0-b) orders 3 and 4 lower the boundary-cell value to 0.18 and 0.041 of order 2
   (errors 1.011 f''' dx and 0.917 f'''' dx^2 against 1.117 f''; f'''/f'' = 3/r,
   f''''/f'' = 12/r^2), each within a factor 2.
 (a0-c) cells four or more from every face read the same H at all three orders
   (difference below 1e-12).
 (a0-d) M_i at t = 0: zero to rounding for punc at every order (K_ij = 0); for ball and
   boost a boundary layer whose largest value falls with the order as in (a0-b) but
   with the first-derivative weights (order 2: 0.40 dx |K''|), and which halves from
   cells of 1 to cells of 1/2 at order 2 (ball64).
 Refuted: if the layer does not follow the stencil numbers (then something else than
 the ghost cells makes it), or if punc shows M_i at t = 0.

Plan a1 (evolution, present code; `plans/a1_base.json`):
 (a1-a) H2: in ball_e2 the boundary cell at a face centre departs from ball_ref from
   the first step at the rate d_t(Khat - Khat_ref) = sqrt2 * 0.5 * K / r = -1.12e-3 per
   unit time (K = -0.0246, r = 15.5), within 30 per cent over t <= 1. For punc the same
   difference stays below 1e-4 at t = 1 (the precollapsed lapse makes d_t K of order
   1.5 M^2/r^4 = 2.6e-5 only).
 (a1-b) speed: along the x axis the difference of Khat between ball_e2 and ball_ref
   advances from the face with speed sqrt 2 +- 25 per cent and that of H with speed
   1 +- 25 per cent (front: where the difference first exceeds 10 per cent of its
   value at the face).
 (a1-c) size: in the vacuum shell 8 <= r < 12 at t = 8 the mean |H| of ball_e2 is more
   than 3 times that of ball_ref (the face error, not truncation, sets the residual
   there); refuted below 1.5.
 (a1-d) H3 against H2: with order 4 instead of 2 the face-layer mean |H| (cells within
   4 of a face) at t = 4 falls by more than a factor 5 for punc (no K_ij: only H1 and
   H3 act) and by less than a factor 2 for ball (H2 dominates). Refuted if the ball
   gains as much as the puncture, or the puncture does not gain.
 (a1-e) H4: without dissipation (ball_e2_d0, to t = 4) the face-layer mean |H| at t = 2
   differs from ball_e2 by less than 20 per cent; refuted if it falls by a factor 2.
 (a1-f) order 4 stays stable to the end of the three runs (no growth of the maximum of
   |H| in the face layer by more than a factor 10 between t = 4 and the end). Not sure:
   the high-order extrapolation feeds the dissipation and the advective stencils.

## 2026-11-19, entry 2: outcome of a0; a0b predicted

Run core-20261119-143732-41f7cce (plan `a0_t0.json`, executable of this worktree at
27b2ced source); numbers `analysis/faces/results/a0.json`, script `analyze_a0.py`.

- (a0-a), (a0-b) FAILED as written, for a reason outside the candidates: at t = 0 the
  monitor of the two puncture runs does not read extrapolated ghost cells at all. The
  largest |H| in the boundary layer is 8.5e-9 (punc) and 1.5e-7 (boost), falls smoothly
  inward-out (the sixth-order truncation error of exact data) and is the same to the
  last digit at orders 2, 3 and 4: the problem generator fills the ghost cells with the
  exact data, and without depositing particles the boundary function is not called
  before the first monitor. The stencil numbers can therefore be tested only after the
  first step (a0b below).
- The ball (deposit on: the boundary function runs before the monitor) shows H = 1e-18
  outside the matter at every order: the Painleve-Gullstrand slice is flat (psi = 1),
  no second derivative enters H there. I had not thought of this; H1 cannot act on H of
  the ball at t = 0, so the face layer of test F of the id-solver package (mean |H|
  1.3e-4 at t = 2) is made by the evolution.
- (a0-c) held (differences between orders four cells from the faces: 0.0 exactly).
- (a0-d) held for the ball: M_x on the axis in the three outer layers is -2.15e-4,
  +5.3e-5, -8.7e-6 at order 2 (stencil: -0.40, +0.10, -0.017 times dx times
  -2 K_T'' = 5.1e-4, i.e. -2.05e-4, +5.1e-5, -8.7e-6); order 3: 4.5e-5 (ratio 0.21,
  stencil 0.18); order 4: 1.3e-5 (ratio 0.061, stencil 0.041); cells of 1/2 at order
  2: -1.00e-4 (ratio 0.47, stencil 0.5), at order 4: 1.2e-6 (ratio 0.092 against cells
  of 1, stencil 1/8). So the layer of M_i at t = 0 which the clump package saw is the
  monitor reading linear ghosts (H1), first order in the cell size at order 2. For
  punc M_i = 0 exactly. For boost the layer is absent at t = 0 for the reason above.

Plan a0b (`plans/a0b_step1.json`): the two puncture data sets after ONE step
(dt = 1/16), orders 2, 3, 4. Predictions [JUDGEMENT], those of (a0-a) and (a0-b) moved
to the first step: after one step the boundary-cell |H| at the face centre is
2.4e-3 at order 2 within a factor 1.5 for punc (the step changes the fields by dt times
small rates; the monitor now reads extrapolated ghosts), second and third layer 0.105
and 0.010 of it; orders 3 and 4 give 0.18 and 0.041 of order 2 within a factor 2.
Refuted if the layer after one step is much smaller (then the ghost cells are not what
the monitor reads in the evolution either) or does not follow the weights.

## 2026-11-19, entry 3: outcome of a0b; first numbers of a1 (ball); the new condition; b1 predicted

**a0b** (run core-20261119-143938-eded041, `results/a0b.json`, figure `figs/a0b_monitor`):
after ONE step the monitor of the vacuum puncture reads |H| = 1.895e-3 in the boundary
cell at the face centre (predicted 2.4e-3 within a factor 1.5: held, ratio 0.79), then
-1.85e-4 and +1.1e-5 in the next two layers (ratios 0.098 and 0.0058; stencil 0.105 and
0.010); order 3 gives 3.49e-4 (0.184 of order 2; stencil 0.175), order 4 gives 9.09e-5
(0.048; stencil 0.041). The boosted puncture: 1.96e-3, 3.59e-4, 9.26e-5. So (a0-a) and
(a0-b), moved to the first step, HELD: H1 is real, and it is what the id-solver package
read as "up to 1.9e-3 within four cells of an outflow face in every mode". With linear
ghosts the monitor's boundary layer is an artefact of the size of M/r^3 that does not
fall with the cell size; with order 4 it is 20 times smaller and falls as dx^2.

**a1, ball, first numbers** (run core-20261119-143745-78506dd; ball_ref had reached
t = 5 when I looked; full analysis in the next entry). Not predictions any more:
- (a1-a) the boundary cell at the face centre departs from the reference by
  dKhat = -1.107e-3 at t = 1 (predicted -1.12e-3 +- 30 per cent: held), dA_xx =
  +1.08e-3. The agreement of Khat is partly luck: the reference is not stationary
  either (1+log lapse from alpha = 1 on the Painleve-Gullstrand slice: Khat moves by
  +5.2e-4 and A_xx by -1.3e-3 in the first unit of time at r = 15.5), so the error of
  the Sommerfeld condition has two parts of similar size, the wrong fall-off and the
  evolution that is not a wave.
- the face layer of H is made by the faces: mean |H| within 4 of a face is 3.1e-4,
  7.6e-4, 1.46e-3 at t = 1, 2, 4 with the faces at 16, and 3.1e-7, 4.1e-6, 7.0e-5 in the
  same cells of the reference.
- (a1-e) HELD: without dissipation the face-layer mean |H| at t = 2 is 7.75e-4 against
  7.63e-4 (1.6 per cent): H4 is not a cause.
- (a1-d), ball half: HELD in the letter, with a surprise: order 4 does not lower the
  face-layer mean |H| of the ball, it raises it (1.86e-3 against 1.46e-3 at t = 4;
  boundary cell -9.3e-3 against +1.0e-3): the cubic extrapolation amplifies the kink
  that the Sommerfeld condition makes in the boundary cell. Further in it helps (shell
  mean of the difference to the reference 1.3e-4 against 2.2e-4 at t = 4).

**The new condition** (source: `athenak/src/z4c/z4c_sbc_ext.hpp`, options and formula;
`z4c_Sbc.cpp`, `Z4cRadiativeOp` and `Z4c::Z4cBoundaryRHSNonwave`; hook: first line of
`Z4c::Z4cBoundaryRHS`; `z4c.hpp` three lines, `z4c.cpp` one line). With
`<z4c> sbc_variant = nonwave` the boundary cell b of Khat, Gamma^i, A_ij gets
`rhs_b = R_b + (rhs_p - R_p)(r_p/r_b)^q`, R the Sommerfeld operator, p one cell inward
along every direction in which b lies on a physical face, q per variable
(`sbc_power_khat`, `_a`, `_gam`, default 3; exact for a stationary field r^-n is
q = n + 1). Theta keeps the plain condition unless `sbc_theta = nonwave`: it is a
constraint and has no part worth keeping. `sbc_v_khat` (default sqrt 2) is the speed
of Khat. Without `sbc_variant` in the input nothing is read and the old loops run.
Unregistered check (scratch/core/tmp/faces_r0, repeated as a registered run at the
end): outputs of ball (8 steps), punc and boost (4 steps) byte-identical between the
new executable without the option and the release executable.

**Plan b1** (`plans/b1_ball.json`; ball to t = 16, reference ball_ref of a1).
Predictions [JUDGEMENT]:
 (b1-a) nonwave, order 2, q = 3: |dKhat| and |dA_xx| in the boundary cell at the face
   centre at t = 1 fall below 10 per cent of the Sommerfeld values (below 1.1e-4).
 (b1-b) the face-layer mean of |H - H_ref| at t = 4 falls by more than a factor 5
   (below 2.9e-4), the shell mean (8 <= r < 12) at t = 4 by more than 3 (below 7e-5).
 (b1-c) q = 2.5 (exact for r^(-3/2)) changes these measures by less than 20 per cent
   against q = 3 (the power enters at order dx/r).
 (b1-d) with nonwave, order 4 is better than order 2 in the face-layer measure by more
   than a factor 2 (no kink is left to amplify, and the ghost data are better).
 (b1-e) all four runs reach t = 16 without growth: the largest |H| within 4 of a face
   stays below 3 times that of the Sommerfeld run at every dump.
 (b1-f) `sbc_theta = nonwave` is worse than the default for the face-layer measure
   (it carries the constraint violation of cell p to the boundary cell).
 Refuted: (b1-a) above 20 per cent; (b1-b) gains below 2; (b1-e) any blow-up.

## 2026-11-19, entry 4: puncture half of a1 so far; plan b2 predicted

a1, vacuum puncture (run core-20261119-143745-78506dd, cases punc_e2, punc_e4, at t = 6
when I looked; the reference core-20261119-144214-5e4bb5a had reached t = 1):
- order 2: the face-layer mean |H| is 1.78e-4 from the first dump on and constant in
  time (1.78, 1.81, 1.74, 1.71e-4 at t = 1, 2, 4, 6): the monitor reading linear ghosts
  of a static far field (H1). The mean over the whole box, 1.05e-4, is this layer; in
  the same cells of the reference it is 1.6e-9, and 5 <= r < 8 has 1.4e-6.
- (a1-d), puncture half, HELD: order 4 lowers the face-layer mean by a factor 36 at
  t = 1 (4.9e-6) and 24 at t = 4 (7.3e-6).
- H3 is real, not only a monitor effect: in the shell 8 <= r < 12, four cells and more
  from the faces, order 2 gives 1.06e-6, 1.58e-6, 8.3e-6, 1.70e-5 at t = 1, 2, 4, 6;
  order 4 gives 7.1e-7, 5.6e-7, 7.0e-7, 2.5e-6; the reference 7.1e-7 at t = 1. The
  linear ghosts feed a violation that travels inward and is 24 times the truncation
  level of the shell by t = 6.
- boundary cell against the reference at t = 1: dKhat = 1.3e-5 (below 1e-4 as
  predicted in (a1-a)), dA_xx = 9.6e-6.

Plan b2 (`plans/b2_punc.json`): the two puncture data sets with the new condition, and
the processor proxy of Track D's long run (`inputs/punc_h.athinput`: the vacuum puncture
with the horizon finder of `problems/puncture/horizon_calib.athinput`, faces at 16 M,
to t = 40; cells of 1/4 at the puncture only, so the finder may fail: then the proxy
gives nothing). Predictions [JUDGEMENT]:
 (b2-a) vacuum puncture, t <= 8: nonwave changes little. Shell and face-layer mean |H|
   of punc_nw_e2 within 30 per cent of punc_e2 (K_ij = 0 at the faces until the gauge
   pulse arrives at t = 11; the part that is not a wave is 3e-5 per unit time).
 (b2-b) at t = 12, after the gauge pulse has reached the faces, the shell mean |H| of
   punc_nw_e4_h is within a factor 2 of punc_e4 (a clean outgoing pulse is what the
   Sommerfeld operator is made for; the correction then adds only truncation error).
   Refuted if nonwave is more than 2 times worse: then the correction disturbs the
   absorption of waves.
 (b2-c) boosted puncture: at the centre of the +x face the boundary-cell A_xx of the
   Sommerfeld run departs from the nonwave run at the rate A_xx/r (fall-off r^-2), i.e.
   |dA_xx| = |A_xx| / 15.5 per unit time at t = 1 within 50 per cent; the face-layer mean
   of |M_i| at t = 4 is more than 3 times lower with nonwave at the same order.
 (b2-d) horizon proxy: if the finder works, the apparent-horizon mass of punc_nw_e4_h
   and punc_sf_e2_h agree to 1e-4 until t = 11 (nothing from the faces has arrived),
   and the largest excursion of the mass from its value at t = 12 over 12 <= t <= 40 is
   not larger with nonwave and order 4 (ratio below 1.2). Refuted above 1.2: then the
   new condition makes the drift worse and must not be recommended for Track D.

## 2026-11-19, entry 5: session resumed at 15:30 UTC; what was left running

The previous session ended at 15:27 UTC. Run core-20261119-152217-73dccb9 (b1) was ended
by signal 15 after three of its five cases had finished (ball_nw_e2, ball_nw_e4,
ball_nw_e2_q25, exit 0); ball_nw_e4_q25 and ball_nw_e4_th did not finish. The vacuum
puncture reference core-20261119-144214-5e4bb5a is still running (t = 4 of 8 at 15:30).
The executables of the source at 224b9629 (no source change since) are frozen in
`.work/exe/sbc1/` (`athena_cpu`, `athena_gpu`) so that the source can change while runs
use them. Started now, predictions unchanged (entry 3 for b1, entry 4 for b2):
`plans/b1b_ball.json` (the two missing cases of b1), `plans/b2_punc.json` (now with the
frozen executable), `plans/a1r2_boostref.json` (the boosted puncture with the faces at
32, to t = 8: the reference that core-20261119-143745-78506dd stopped by hand).

## 2026-11-19, entry 6: three new options; predictions for the tests c0-c3, the card runs D, the regression r1

Source at 6cd99721 (`.work/exe/sbc2/`): (1) `ghost_falloff = true`: the ghost cells at
outflow faces extrapolate G = (f - f_inf) r^q (asymptotic value 1 for chi, gt_ii, alpha,
0 otherwise; q = `ghost_power_metric`, `ghost_power_curv`, default 1) with the stock
Lagrange weights, f_g = f_inf + G_g / r_g^q (`z4c/z4c_bcs_falloff.cpp`); (2) `sbc_speed =
lapse | metric`: the speeds of the boundary operator alpha (sqrt(f alpha) for Khat) as in
arXiv:1212.2901 (`.../1212.2901/v1/src/paper20121212.tex` lines 484-498), or the
coordinate speeds alpha sqrt(chi/gt_ss), with the advection beta^k d_k f; (3) `sbc_theta =
cpbc`: d_t Theta = -alpha s^k d_k Theta + beta^k d_k Theta (same source, line 405).
Without the options the code paths of the release run (to be shown by r1).

Derivation for c0 [JUDGEMENT]: for the Brill-Lindquist far field chi = (1 + m/2r)^-4 =
1 - 2m/r + 2.5 m^2/r^2 - ..., G = r (chi - 1) = -2m + 2.5 m^2/r, so G'' = 5 m^2/r^3 against
chi'' = -4 m/r^3: at r = 15.5 the ghost error, and with it the monitor's face layer of H,
falls by 1.25 m/r = 0.081 (with the next order 0.086) at every extrapolation order (the
fourth derivatives have the same ratio). gt_ij = delta exactly. For Bowen-York A_ij ~ r^-2
with q = 1 the ratio is |2 - 1|/(2 + 1) = 1/3.

Predictions [JUDGEMENT], written before any of these runs:
- c0 (`plans/c0_step1.json`, one step, against a0b): (c0-a) punc, falloff, order 2: the
  boundary-cell |H| at the centre of the +x face is 0.086 x 1.895e-3 = 1.6e-4 within a
  factor 2; order 4: 0.086 x 9.09e-5 = 7.8e-6 within a factor 2. (c0-b) boost, falloff,
  order 2: the boundary-cell |M_x| on the x axis is 1/3 of the stock value of the same
  step within a factor 1.5 (the stock value is read from a0b's boost_e2 dump). Refuted if
  the falloff values are not below 0.2 of the stock ones.
- c1, ball (`plans/c1_ball.json`, to t = 16, against ball_ref of a1): (c1-a) falloff
  alone, order 2: the face-layer mean |H| at t = 4 changes by less than a factor 2 from
  ball_e2 (1.46e-3): the ball's layer is made by the wrong fall-off of the RHS (H2), not by
  the ghosts (the slice is flat outside the ball). (c1-b) falloff + nonwave + order 4:
  face-layer mean |H - H_ref| at t = 4 below 0.2 of ball_e2's, and the shell
  (8 <= r < 12) mean below 0.33 of it. (c1-c) ghost_power_curv = 1.5 (the fall-off of K in
  the Painleve-Gullstrand exterior) improves on q = 1 by less than a factor 1.5 (the RHS
  power of nonwave already removes most of H2). (c1-d) sbc_speed = metric changes the
  face-layer and shell measures by less than 20 per cent (alpha and chi stay within 2 per
  cent of 1 at the faces of the ball; the exterior is flat). (c1-e) sbc_theta = cpbc is
  within 30 per cent of sommerfeld for Theta in the face layer (no 1/r term: a Theta
  falling as 1/r is driven at the rate Theta/r, which is small against the incoming
  violation), not better by a factor 2. (c1-f) every case reaches t = 16 without growth
  (face-layer max |H| at the end below 3 times that of ball_e2).
- c2, punctures (`plans/c2_punc.json`, to t = 12): (c2-a) punc_g2 (falloff, order 2): the
  face-layer mean |H| falls by more than a factor 5 from punc_e2 (1.78e-4) at t = 1 and
  t = 6 (H1 and H3 are the ghosts), and the shell mean at t = 6 falls by more than a factor
  3 from 1.70e-5. (c2-b) punc_g4nw: shell mean at t = 6 within a factor 1.5 of the
  reference's truncation level (punc_ref, when it has reached t = 6). (c2-c) after the
  gauge pulse reaches the faces (t >= 11), punc_g4nw_met has a lower shell mean |H| than
  punc_g4nw (speed 0.88 instead of 1 at r = 16: less reflection), by at least 10 per cent.
  (c2-d) boost_g4nw: face-layer mean |M_i| at t = 4 below 0.2 of boost_e2's.
- c3, horizon proxy (`plans/c3_punch.json`, faces at 16 M, to t = 40, finder): compared
  with b2's punc_sf_e2_h (stock): the horizon mass agrees to 1e-4 until t = 11, and the
  largest excursion of the mass from its value at t = 12 over 12 <= t <= 40 is not larger
  with the full set (ratio below 1.2).
- D, card (`plans/card_full.list`, `plans/card_ghost.list`): Track D's drift_dx8 input to
  345 M with (full) falloff + order 4 + nonwave + metric speed, (ghost) falloff + order 4
  only. The stock reference is Track D's own run D-bh-dress-20261115-121313-284ec4f (card
  executable of core-v0.2; the vacuum Z4c path did not change from core-v0.2 to core-v0.3:
  `git diff core-v0.2 core-v0.3 -- athenak/src/z4c` touches only the scalar-field sources
  and task dependencies). (D-a) both new runs agree with Track D's horizon mass within
  2e-5 until t = 180 M (no signal from the faces can have come back). (D-b) the
  peak-to-peak excursion of the mass in 210-260 M and in 295-345 M is not larger than in
  Track D's run (1e-4 and 1.5e-4 by its README; recomputed here from its
  horizon_summary file) by more than 20 per cent; I expect it smaller for the full set.
  Refuted (for the recommendation to Track D) if either is larger by more than 20 per cent.
- r1 (`plans/r1_regress.json`): every output file byte-identical between the new
  processor executable and the release (`.work/build_cpu_v03`) for the package inputs
  without the options and for problems/puncture/horizon_calib, by_binary, tests/z4c_bench
  and scalar/kg_wave_smr, a few steps each.

## 2026-11-19, entry 7: outcomes of c0, of a1 for the ball, of b1; prediction c0b

Analysis run core-20261119-161035-2bea9be (`an_batch.sh c0_a1ball.txt`; results
`results/c0.json`, `results/a1_ball.json`, `results/b1_ball.json`; figures
`figs/c0_monitor.png`, `figs/a1_ball_regions.png`, `figs/a1_ball_spacetime.png`,
`figs/b1_ball_regions.png`, looked at).

**c0** (run core-20261119-155943-13bb466 against a0b core-20261119-143938-eded041):
- (c0-a) HELD. Vacuum puncture after one step, boundary cell at the +x face centre:
  |H| = 1.53e-4 with the falloff fill at order 2 against 1.895e-3 stock (ratio 0.081;
  predicted 0.086), 7.9e-6 against 9.09e-5 at order 4 (ratio 0.087). The sign flips (G''
  and chi'' have opposite signs), and the second and third layers fall alike (1.48e-5,
  8.7e-7 against 1.85e-4, 1.10e-5). The boosted puncture's H falls the same way (0.088 at
  order 2, 0.108 at order 4).
- (c0-b) FAILED. Boosted puncture, |M_x| in the boundary cell: ratio 0.51 at order 2 and
  1.07 at order 4 (predicted 1/3 within a factor 1.5). The prediction assumed that M_x
  next to the face is the ghost error of A_ij; it is not, after one step: the stock M_x
  is 1.8e-5 at order 2 and 2.0e-5 at order 4 (larger at the higher order), which is the
  size of the kink that the Sommerfeld rate makes in one step: for A_xx = 3P/r^2 =
  3.7e-3 at r = 15.5 the condition gives d_t A = +A/r instead of 0, i.e. 1.5e-5 per step
  of 1/16, which the first derivatives of M_x read with weight about 1. So the momentum
  constraint layer of a boosted puncture (and of the clump package's moving clusters) is
  H2, the wrong fall-off of the boundary operator, from the first step on; c0b tests this.
- Also seen: for the vacuum puncture M_x is at the level 1e-6 in every variant (the
  data have K_ij = 0; the step gives it a little).

**a1, ball** (run core-20261119-143745-78506dd against ball_ref of the same run):
- (a1-b) HELD: along the +x axis the front of the difference to the reference moves in
  at 1.50 for Khat (predicted sqrt 2 +- 25 per cent) and 1.07 for H (predicted 1 +- 25 per
  cent); Theta's front at 0.54 (no prediction; it follows H with a lag).
- (a1-c) HELD: shell (8 <= r < 12) mean |H| at t = 8 is 2.80e-3 with the faces at 16
  against 7.35e-4 in the same cells of the reference (3.8 times). At t = 4 it is still
  9.4e-4 against 8.6e-4: the error needs t of about 5 to cross the 4 to 8 units from the
  faces to the shell at speed 1.
- Constraint-propagating fields: the Gamma constraint |Gt - Gt(gt)| in the face layer is
  6.99e-4, 1.82e-3, 5.81e-3 at t = 1, 2, 4 against 1.9e-7, 2.9e-6, 6.5e-5 in the
  reference (it is the largest of the four measures and grows fastest); Theta in the face
  layer 2.5e-5, 5.0e-5, 8.9e-5 against 1.0e-7, 1.6e-6, 3.5e-5.

**b1** (run core-20261119-152217-73dccb9; three of its five cases):
- (b1-a) order 2: FAILED for Khat, held for A_xx: at t = 1 the boundary cell differs from
  the reference by dKhat = -3.2e-4 (29 per cent of the Sommerfeld value 1.107e-3;
  predicted below 10 per cent) and dA_xx = 8.0e-5 (7.4 per cent). With order 4: dKhat =
  -4.8e-5 (4.3 per cent), dA_xx = 1.6e-5 (1.5 per cent). The rest at order 2 is the
  linear ghost error entering the full right-hand side of cell p, which the non-wave
  part then carries to the boundary cell.
- (b1-b) face layer: FAILED at order 2 (mean |H - H_ref| at t = 4 4.4e-4 against 1.45e-3,
  3.3 times; predicted more than 5), HELD at order 4 (2.6e-4, 5.6 times). Shell at t = 4:
  HELD (3.3e-5 at order 2, 3.1e-6 at order 4, against 2.2e-4: 6.5 and 70 times); at t = 8
  5.6e-4 and 2.7e-4 against 2.9e-3.
- (b1-c) HELD: power 2.5 against 3 changes the face-layer measure by 13 per cent and the
  shell measure by 20 per cent at t = 4.
- (b1-d) FAILED in the letter: with nonwave, order 4 beats order 2 by 1.7 in the face
  layer (predicted more than 2), but by 11 in the shell at t = 4 and 2.1 at t = 8.
- (b1-e) HELD: all three reach t = 16; the face-layer maximum of |H| stays below that of
  the Sommerfeld run at every dump (at t = 12: 1.8e-2, 1.35e-2, 2.0e-2 against 2.5e-2).
- Comparisons after t of about 11 are contaminated: the reference's own faces (at 32)
  are then felt at r = 16.

Plan c0b (`plans/c0b_step1.json`): the boosted puncture after one step with nonwave:
stock ghosts order 2 (boost_e2nw), falloff order 2 (boost_g2nw), falloff order 4
(boost_g4nw). Prediction [JUDGEMENT]: the boundary-cell |M_x| falls below 0.2 of the
Sommerfeld value of the same ghost fill and order (c0: stock order 2 1.77e-5; falloff
order 2 8.95e-6; falloff order 4 2.12e-5), i.e. below 3.5e-6, 1.8e-6 and 4.2e-6.
Refuted if any is above 0.4 of its Sommerfeld value: then the boosted layer is not H2.

## 2026-11-19, entry 8: outcome of c0b; the puncture half of a1 with its reference; a fourth candidate: the Gamma condition

Analysis run core-20261119-162148-593a647 (`an_batch.sh c0b_a1punc.txt`; `results/c0b.json`,
`results/a1_punc.json`, `results/a1_boost.json`; figures `figs/c0b_boost.png`,
`figs/a1_punc_regions.png`, `figs/a1_boost_regions.png`, looked at). c0b: run
core-20261119-161322-59d2fbb; the vacuum-puncture reference core-20261119-144214-5e4bb5a
(faces at 32, t = 8) is complete.

**c0b**: boundary-cell |M_x| of the boosted puncture after one step, nonwave against
Sommerfeld with the same ghosts: stock ghosts order 2: 3.34e-5 against 1.77e-5 (ratio
1.9, WORSE); falloff order 2: 4.5e-6 against 9.0e-6 (0.51); falloff order 4: 2.6e-7
against 2.1e-5 (0.012; face-layer maximum 7.1e-7 against 2.1e-5). The prediction (below
0.2 in all three) FAILED for the two order-2 cases and HELD for order 4; by its own
refutation clause the order-2 cases say that the boosted layer is not H2 alone. What the
three together show: the layer has two parts. The Sommerfeld rate (H2) is one; the other
is the ghost error entering the full right-hand side of the cell next to the boundary
cell (H3), which nonwave copies into the boundary cell (with linear ghosts it doubles the
layer). Only both remedies together, accurate ghosts and the non-wave part, remove it:
70 times lower than stock in the boundary cell.

**a1, vacuum puncture**, against its reference (to t = 8):
- face layer: mean |H| 1.78e-4 (order 2) and 4.9e-6 to 8.5e-6 (order 4), constant in
  time, against 1.6e-9 to 1.1e-7 in the reference: the monitor reading linear ghosts (H1).
- shell 8 <= r < 12 (four or more cells from the faces): order 2 1.1e-6, 8.3e-6, 2.1e-5 at
  t = 1, 4, 8; order 4 7.1e-7, 7.0e-7, 6.3e-6; reference 7.1e-7, 4.3e-7, 2.05e-6. At t = 8
  the faces raise the shell residual 10 times (order 2) and 3 times (order 4) above the
  truncation level of the same cells with the faces at 32.
- inner 5 <= r < 8: the faces are not yet felt at t = 8 (2.13e-5, 1.62e-5, reference
  1.63e-5): the hole's own truncation error dominates there.
- fronts along +x: H at speed 1.00 (order 4; at order 2 the monitor layer hides it),
  Khat 1.16 to 1.31 (sqrt(2 alpha) with alpha of 0.7 to 0.9 at the faces).
- Gamma constraint |Gt - Gt(gt)|: face layer 2.5e-6, 1.9e-5, 4.3e-5 at t = 1, 4, 8, the
  SAME at orders 2 and 4, against 1e-10 to 2e-8 in the reference; in the shell it climbs
  to 4 times the reference by t = 8. Theta: face layer 7e-6 (order 2), 3e-7 (order 4),
  reference 5.6e-10 to 7e-8.
- Boosted puncture (no reference yet, a1r2 queued): face layer of M 2.1e-5 (order 2),
  1.6e-5 (order 4) at t = 1, growing to 5e-5 by t = 8; Gamma constraint face layer
  2.5e-5 at t = 1 to 4.9e-4 at t = 8 (ten times the vacuum puncture's).

**A fourth candidate, H5** [JUDGEMENT]: the Gamma constraint layer does not depend on
the ghost order, so it is made by the boundary condition of Gt^i itself: Sommerfeld for
Gt^i while gt_ij keeps its full right-hand side, so Gt^i and Gt^i(gt) are driven apart in
the boundary cell from the first step. The ball shows the same at a larger level (face
layer 7e-4 to 5.8e-3 at t = 1 to 4) and nonwave lowers it there by 8 to 11 (b1). A
remedy that keeps the communication between blocks consistent (the change must be in
the right-hand side, not a projection after the update): a damping term in the
boundary cell, d_t Gt^i += -lambda (Gt^i - Gt^i_d), Gt^i_d = -d_j gt^ij (det gt = 1),
centred second-order differences; and likewise d_t Theta += -lambda_Theta Theta, a
constraint-absorbing treatment of Theta that keeps the outgoing condition. Implemented
next as `sbc_damp_gam`, `sbc_damp_theta` (rates, absent: off).
