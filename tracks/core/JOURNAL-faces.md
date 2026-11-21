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

## 2026-11-19, entry 9: damping in the boundary cells; predictions c4

Source (commit after this entry; executables `.work/exe/sbc3/`): `<z4c> sbc_damp_gam =
lambda` adds -lambda (Gt^i - Gt^i_d) to d_t Gt^i in the boundary cells, Gt^i_d = -d_j gt^ij
from centred second-order differences of the inverse conformal metric of the six
neighbours (ghosts included); `sbc_damp_theta = lambda` adds -lambda Theta to d_t Theta
there. Absent or 0: nothing changes. Smoke test (4 steps of the ball with both at 1,
scratch/core/tmp/faces_smoke/ball_e, unregistered): runs.

Plan c4 (`plans/c4_damp.json`; "full" = falloff ghosts, order 4, nonwave, metric speed).
Predictions [JUDGEMENT], against the same set without damping (ball_g4nw_met of c1;
punc_g4nw_met and boost_g4nw_met of c2):
 (c4-a) ball, damp_gam = 4: the face-layer mean of |Gt - Gt(gt)| at t = 4 falls by more
   than a factor 2; damp_gam = 1 by less than damp_gam = 4.
 (c4-b) ball, damp_theta = 4: the face-layer mean |Theta| at t = 4 falls by more than a
   factor 2; the shell mean |H| changes by less than 20 per cent (Theta is not what
   carries the face error inward in the ball: its front lags that of H, entry 7).
 (c4-c) with both, the shell mean |H| at t = 8 is not higher than without (within 10 per
   cent) and lower by more than 20 per cent if H5 is a main carrier of the face error.
 (c4-d) vacuum and boosted puncture, both at 4: the face-layer Gamma constraint at t = 4
   falls by more than a factor 3 (in the vacuum puncture the layer is H5 alone, entry 8).
 (c4-e) every case runs to its end without growth (lambda dt = 0.25 for the ball's step,
   well inside the RK4 limit).

Plan t1 (`plans/t1_smrface.json`): the vacuum puncture with a refined region (cells of
1/2) that touches the +x face (4.1 <= x <= 16, |y|, |z| < 3.9), so that the coarse-array
path of the ghost fill (`GhostFalloff(coarse_u0, true)` before prolongation) is used;
eight steps, stock against the full set with damping. Prediction [JUDGEMENT]: both run
without a non-finite value; with the full set the face-layer maximum of |H| on the fine
part of the +x face is below 0.2 of the stock one, and the cells of the face next to the
fine/coarse junction show no value above 3 times the stock face-layer maximum.

## 2026-11-20, entry 10: wave 3, session resumed after the usage limit; outcomes of c1, c2 (first part), c3, the card runs D, t1

State found at 22:00 UTC (git status clean; the journal ended with entry 9): the runs
started on 2026-11-19 had all ended by themselves with exit 0 and stood as "running" or
"submitted" in their manifests. Closed with `nrpic-run finish`: c2 (core-20261119-161135-6bcc75b
punc_g2, core-20261119-161443-f206ffa punc_g4nw_met, core-20261119-161446-1c038a9
boost_g4nw_met), b2 (core-20261119-161449-d22d256 punc_sf_e2_h), c3
(core-20261119-162245-b68f4a9 punc_full_h), c1 (core-20261119-164115-3f3c592 four cases,
core-20261119-164338-2dc0ab0 three cases), and the two card runs D
(core-20261119-155540-6c84b8a full, 27 min 59 s; core-20261119-155547-b22024e ghost,
27 min 48 s; Slurm 4659, 4660: 0.93 card-hours, so no further card run fits the one
card-hour of this package). Never started before the cut: c4, t1, r1 (predictions in
entries 9 and 6), b1b, a1r2, the cases punc_nw_e2, boost_nw_e2, boost_nw_e4, punc_nw_e4_h of
b2, punc_g4nw, punc_g4nw_cp, boost_g2, boost_g4nw of c2, punc_g4_h of c3. Started now
with the predictions as written: r1 (core-20261120-220733-ea71a73), t1
(core-20261120-220734-23cb66f), c4 (core-20261120-220735-a7966ff), punc_g4nw of c2
(core-20261120-222537-1011ec4), a1r2 (core-20261120-222543-9a83982). Not run and not
planned: b1b and the remaining cases of b2 (the non-wave condition on linear stock
ghosts, which c0b showed to be the wrong combination), punc_g4nw_cp, boost_g2,
boost_g4nw, punc_g4_h; their predictions (b2-a, b2-c) stay untested.

Analysis run core-20261120-222418-ecb29ff (`an_batch.sh t1.txt c3_d.txt c1a.txt c1b.txt
c2.txt`; `results/t1.json`, `c3_proxy.json`, `drift.json`, `c1a_ball.json`,
`c1b_ball.json`, `c2_punc.json`, `c2_boost.json`; figures `figs/t1_smrface.png`,
`c3_proxy.png`, `drift.png`, `c1a_ball_regions.png`, `c1b_ball_regions.png`,
`c2_punc_regions.png`, `c2_boost_regions.png`, each looked at). "Full set" = fall-off
ghosts, order 4, nonwave, metric speed.

**t1** (run core-20261120-220734-23cb66f; refined region of cells 1/2 touching the +x
face, eight steps, t = 0.5): HELD. No non-finite value in any dump of either run. Largest
|H| within 4 of the +x face: fine part 2.0e-6 (full set with damping) against 1.79e-3
(stock), ratio 1.1e-3 (predicted below 0.2); coarse part 6.8e-7 against 8.0e-4; junction
zone (2 <= max(|y|, |z|) < 6) 1.1e-6, i.e. 6e-4 of the stock face-layer maximum
(predicted below 3 times). The stock value does not fall with the cell size (1.79e-3 on
cells of 1/2, 1.9e-3 on cells of 1 in a0b): H1. The coarse-array path of the fall-off
fill works on a face with a refinement junction.

**c1, ball** (against ball_e2 of a1 and the reference with the faces at 32):
- (c1-a) HELD: fall-off ghosts alone, order 2: face-layer mean |H| at t = 4 1.49e-3
  against 1.46e-3. The ball's layer is not made by the ghosts.
- (c1-b) HELD: fall-off ghosts, order 4, nonwave (ball_g4nw): mean |H - H_ref| at t = 4 in
  the face layer 2.55e-4 against 1.45e-3 (0.18; predicted below 0.2), in the shell
  2.28e-6 against 2.16e-4 (0.011; predicted below 0.33). At t = 8: face layer 1.32e-3
  against 4.38e-3, shell 2.25e-4 against 2.94e-3 (13 times), inner r < 8 2.0e-5 against
  1.13e-3 (56 times).
- (c1-c) HELD: ghost_power_curv = 1.5 changes the measures by 1 per cent.
- (c1-d) HELD at t = 4 (3 per cent), and beyond it later, in the good direction: with
  sbc_speed = metric the face-layer difference at t = 8 is 26 per cent lower (9.8e-4
  against 1.32e-3) and at t = 16 the mean |H| is 2.12e-3 against 3.10e-3 (inner) and
  1.97e-3 against 3.24e-3 (shell).
- (c1-e) HELD: sbc_theta = cpbc changes the face-layer mean |Theta| by +3 per cent
  (t = 4), +8 per cent (t = 8), +21 per cent (t = 16): no gain.
- (c1-f) HELD: every case reaches t = 16; face-layer maximum of |H| at the end 4.9e-3
  (full set) to 1.66e-2 (ball_g2) against 1.57e-2 (stock).
- Not predicted, seen in `figs/c1b_ball_regions.png`: in the reference the residuals of
  the interior FALL after t of about 10 (inner mean |H| 3.5e-3 at t = 8, 3.9e-5 at
  t = 16: the constraint violation that the ball's matter makes leaves through the shell,
  where it peaks at 2.5e-3 at t = 10). With the faces at 16 a part of it comes back: at
  t = 16 the inner mean |H| is 1.69e-2 (stock), 3.10e-3 (ball_g4nw), 2.12e-3 (full set),
  against 3.9e-5. So the new conditions lower the residual of the interior 8 times at
  t = 16, but the faces still reflect: what returns is 50 times the reference level.
  The whole-box mean at t = 16: 7.07e-3 (stock), 1.70e-3 (full set), 4.1e-4 (reference).

**c2, vacuum puncture** (reference with the faces at 32 to t = 8):
- (c2-a) HELD: fall-off ghosts alone at order 2 (punc_g2): face-layer mean |H| 1.31e-5
  at t = 1 and 1.71e-5 at t = 6 against 1.78e-4 and 1.71e-4 (13.6 and 10 times); shell
  at t = 6 3.08e-6 against 1.70e-5 (5.5 times; predicted more than 3).
- (c2-b) HELD, measured on punc_g4nw_met (punc_g4nw is running): shell mean |H| at t = 6
  7.00e-7 against 7.02e-7 in the reference; at t = 8 2.14e-6 against 2.05e-6. With the
  full set the shell stays at the truncation level until the reference ends; stock is
  24 times above it at t = 6 and 10 times at t = 8.
- Face layer and whole box (r >= 5), mean |H|: face layer 2.97e-7 (t = 1), 8.4e-7
  (t = 4), 2.99e-6 (t = 8) against 1.78e-4, 1.74e-4, 1.72e-4 (stock) and 1.6e-9, 1.1e-8,
  1.1e-7 (reference); whole box at t = 8 3.11e-6 against 1.07e-4 (stock) and 1.23e-6
  (reference). The Gamma-constraint face layer falls 5 to 12 times (2.17e-6 against
  1.90e-5 at t = 4), where the ghost order alone changed nothing (entry 8).
- After the gauge pulse has reached the faces (t = 12): shell 1.44e-5 (full set),
  1.71e-5 (order 4, stock ghosts), 1.84e-5 (stock); the non-wave part does not spoil the
  absorption of the pulse (the spirit of b2-b, whose own case punc_nw_e4_h was not run).
- (c2-c) open until punc_g4nw has run.

**c2, boosted puncture** (no reference yet; a1r2 is running):
- (c2-d) HELD, measured on boost_g4nw_met: face-layer mean |M_i| at t = 4 3.39e-6
  against 4.29e-5 (0.079; predicted below 0.2).
- Mean |H|: face layer 5.67e-6 against 2.03e-4 at t = 4 (36 times), shell 4.37e-6
  against 5.02e-5 at t = 8 (11 times) and 1.88e-5 against 1.05e-4 at t = 12; whole box
  1.26e-5 against 1.48e-4 at t = 8, 3.31e-5 against 1.77e-4 at t = 12. Gamma constraint:
  face layer 1.13e-5 against 1.91e-4 at t = 4, shell 2.43e-5 against 4.30e-4 at t = 12.
  Order 4 with stock ghosts and the Sommerfeld rate (boost_e4) lowers H in the face
  layer 5 times at t = 4 but leaves M_i (3.83e-5) and the Gamma constraint: the layer of
  the boosted puncture is the wrong fall-off of the boundary operator (H2), as c0 and
  c0b said.

**c3, horizon proxy** (faces at 16 M, cells of 1/4 at the puncture; punc_full_h against
punc_sf_e2_h of b2; this also answers b2-d with the full set in place of punc_nw_e4_h):
HELD in the letter. The horizon masses agree to 8.1e-9 until t = 11 (predicted 1e-4);
largest excursion from the value at t = 12 over 12 <= t <= 39: 2.519e-2 (full set)
against 2.391e-2 (stock), ratio 1.054 (predicted below 1.2). But the proxy decides
little: both masses fall by 2.4 per cent because the hole is under-resolved, and the two
runs differ by up to 1.3e-3 (at t = 39, full set lower). Which of the two is nearer to a
run with distant faces is not known: that reference (faces at 32 M, 6.6 times the cells)
costs about ten core-hours and was not run. [TO VERIFY]

**D, Track D's drift input on a card** (345 M, dx = M/8, faces at 128 M; against Track
D's run D-bh-dress-20261115-121313-284ec4f, numbers recomputed here from its
horizon_summary file):
- (D-a) HELD: largest |M - M_TrackD| for t <= 180 M: 9.0e-6 (full set), 9.1e-6 (ghost
  fill only); predicted within 2e-5. M(50) agrees to 1e-15.
- (D-b) HELD, with the expected sign: peak-to-peak of the horizon mass in 210-260 M:
  1.08e-4 (Track D), 6.1e-5 (full set, 0.57), 7.7e-5 (ghost fill only, 0.71); in
  295-345 M: 1.52e-4, 3.3e-5 (0.22), 5.4e-5 (0.35). Drift M(345) - M(50): 2.10e-4,
  1.90e-4, 2.07e-4; slope over 150-345 M 2.0e-7, 1.2e-7, 1.7e-7 per M.
  So the horizon-mass drift of the long vacuum run does not get worse: the two
  excursions that Track D's README attributes to the outer region shrink 1.8 and 4.6
  times with the full set, which also confirms the attribution (a change at the faces
  alone changes them; `figs/drift.png`).
  Caveat: Track D's run used the card executable of core-v0.2; the vacuum Z4c path is
  the same source (entry 6), and the three runs agree to 1e-15 at 50 M.

## 2026-11-20, entry 11: batch 2b, session resumed at 23:47 PST; c4 for the ball (damping FAILED); decision; predictions of the closing tests

State found (git status clean, journal ended with entry 10): main merged (release
core-v0.5; one conflict in `z4c/z4c.hpp`, both sides kept: the include and the member of
this package beside those of the gauge package). The runs of entry 10 had all ended with
exit 0 and are closed now with `nrpic-run finish`: c4 (core-20261120-220735-a7966ff),
punc_g4nw (core-20261120-222537-1011ec4), a1r2 (core-20261120-222543-9a83982) and the
analysis run core-20261120-223202-120e973 (`results/c4_ball.json`, `c3_evo.json`; figures
`figs/c4_ball_regions.png`, `c3_evo_regions.png`, looked at now). Times of this journal
are local (PST); the "UTC" of entries 5 and 10 was the local time too.

**c4, ball** (run core-20261120-220735-a7966ff against the full set without damping,
ball_g4nw_met of core-20261119-164338-2dc0ab0; analysis core-20261120-223202-120e973):
- (c4-e) FAILED. `sbc_damp_gam = 4` (ball_full_dg4, and with `sbc_damp_theta = 4`
  ball_full_dgt4) is unstable: the largest |H| within 4 of a face is 4.7e-3 at t = 9,
  7.6e-2 at t = 10, 0.35 at t = 11, 1.2 at t = 14, and the fields are not finite from
  t = 15 (the executable of cb50e22 has no guard and ran on with exit 0).
  `sbc_damp_gam = 1` reaches t = 16 but with the same growth later: 1.2e-2 at t = 14,
  0.12 at t = 15 and 16, against 5e-3 without damping. The growth starts when the
  constraint violation that the ball sends out reaches the faces (t of 8 to 10, entry 10).
  lambda dt is 0.25 and 1.0 (the ball's step is 0.25), inside the RK4 limit of 2.78 of a
  pure damping, and the growth is there at both: the term itself, not its time
  integration, is unstable there. [JUDGEMENT] on the mechanism, not tested: Gt^i_d is a
  second-order difference of ghost cells that are extrapolated from the boundary cell,
  so the term feeds the boundary cell's own metric error back into Gt^i and through the
  Gamma driver into the shift.
- (c4-a) HELD before the growth: face-layer mean of |Gt - Gt(gt)| at t = 4: 4.64e-4
  without, 3.32e-4 at lambda = 1 (1.4 times), 2.05e-4 at lambda = 4 (2.3 times).
- (c4-b) FAILED: `sbc_damp_theta = 4` lowers the face-layer mean |Theta| at t = 4 from
  5.14e-5 to 4.96e-5 (4 per cent; predicted more than a factor 2); the shell mean |H| is
  unchanged (8.57e-4), as predicted. At t = 8 and 16 the face-layer mean |H| is higher
  with it (1.40e-3 against 1.02e-3; 2.06e-3 against 1.44e-3).
- (c4-c): with both, the shell mean |H| at t = 8 is 8.72e-4 against 7.94e-4 (10 per cent
  higher, at the edge of the clause "within 10 per cent"); not lower: H5 is not a main
  carrier of the face error into the interior of the ball.

**Decision** [JUDGEMENT]. The damping of the Gamma constraint in the boundary cells is
unstable in one of the three set-ups and the damping of Theta gains nothing in the one
where it was measured, so neither is delivered: `sbc_damp_gam`, `sbc_damp_theta` and
`Z4cGammaFromMetric` are removed from the source (they stay at commit cb50e22, with which
c4 and t1 ran; frozen executable `.work/exe/sbc3/`). The Gamma-constraint layer (H5) is
lowered 5 to 12 times by the full set without them (entry 10) and is otherwise left as
found. What is delivered: `ghost_falloff` with its powers, `sbc_variant = nonwave` with
its powers, `sbc_speed`, `sbc_theta = cpbc | nonwave` (cpbc tested without gain, c1-e).

**Predictions of the closing tests** [JUDGEMENT], written before the source is changed
and before any of the runs or analyses below:
- c2-c (entry 6, unchanged): after t = 11 punc_g4nw_met has a shell mean |H| at least 10
  per cent below punc_g4nw.
- c4-d, c4-e for the two punctures (entry 9, unchanged; the runs are those of cb50e22):
  face-layer Gamma constraint at t = 4 more than 3 times lower with both dampings at 4,
  no growth to t = 12. Whatever comes out, the decision above stands (the ball decides).
- c5, boosted puncture against its reference with the faces at 32 (a1r2, to t = 8;
  `specs/c5.txt`): (c5-a) shell (8 <= r < 12) mean |H| at t = 8: full set within a factor
  1.5 of the reference, stock order 2 more than 5 times the reference (the vacuum
  puncture gave 1.04 and 10). (c5-b) the face layer does not reach the truncation level:
  mean |M_i| within 4 of a face at t = 4 is more than 10 times the reference's with the
  full set (3.39e-6, entry 10) and more than 100 times with the stock conditions
  (4.29e-5). Refuted if the full set is within a factor 3 of the reference there.
- r2, regression after the merge (`plans/r2_regress.json`, `specs/r2.txt`): every output
  file of the new processor executable without the options is byte-identical with the
  release core-v0.5 (`/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena`) for the three
  package inputs, `problems/puncture/horizon_calib`, `by_binary`, `tests/z4c_bench`,
  `scalar/kg_wave_smr` (the set of r1) and one periodic run with particles
  (`problems/tests/mpi_box_periodic`, where no face exists). The difference of the source
  to core-v0.5 is additions only (`git diff core-v0.5 -- athenak`: 7 files, no deletion).
- m1, the options after the merge and after the removal (`plans/m1_merge.json`,
  `specs/m1.txt`): the new executable against the frozen one of cb50e22 with the full
  set (fall-off ghosts, order 4, nonwave, metric speed): ball 16 steps, vacuum and
  boosted puncture 8 steps, the refined region at the +x face of t1 8 steps. Every array
  of every field dump and every number of the history files is identical (largest
  difference exactly 0): the merge brings only code behind its own options into the Z4c
  path, and the removal leaves the arithmetic of the kept paths alone. The files
  themselves differ (the parameter dump in their headers has the options of core-v0.4 and
  v0.5), so arrays are compared, not bytes. Refuted by any non-zero difference; then the
  merged executable with the damping still in (`.work/exe/merge0/`) says which of the two
  changes made it.
- t1b, the refined region at the +x face without the damping (`plans/t1b_smrface.json`,
  new executable): no non-finite value; largest |H| within 4 of the +x face on the fine
  part below 0.2 of the stock one (1.79e-3) and within a factor 3 of the value with
  damping (2.0e-6); the junction zone below 3 times the stock face-layer maximum.
- s1, the two options no run has used (`plans/s1_untested.json`, ball to t = 16 on top
  of the full set): `sbc_speed = lapse` in place of metric changes the face-layer and
  shell mean |H| at t = 8 by less than 30 per cent (chi and gt_ss are within 2 per cent
  of 1 at the faces); `sbc_theta = nonwave` does not lower the face-layer mean |Theta|
  at t = 4 by more than 20 per cent (b1-f of entry 3: it carries the constraint
  violation of the neighbour into the boundary cell); both reach t = 16 with a
  face-layer maximum of |H| below 3 times that of the stock run (1.57e-2). Refuted for
  an option by growth or a non-finite value: then that value is refused in the input.

## 2026-11-21, entry 12: the regression r1 had FAILED and nobody had looked; cause (an inline function in the options header changes how the compiler builds the right-hand side); correction; m1 revised

**r1 was never evaluated.** The cut session started r1 (core-20261120-220733-ea71a73: the
processor executable of cb50e22 without the options against the release core-v0.3) and
wrote its comparison spec, but no outcome. Looked at now (first by hand, then as the
registered analysis named in entry 13): the outputs are NOT byte-identical. Files that
differ: ball 8 of 11, vacuum puncture 3 of 5, boosted puncture 3 of 5, by_binary 4 of 9,
horizon_calib 5 of 10, kg_wave_smr 1 of 1 (z4c_bench writes no file in two steps, so it
tests nothing). The differences are in the last bits: largest difference of a dumped
array 4.7e-10 (ball, 8 steps), 7.3e-12 (puncture, 4 steps); the constraint dump of the
puncture at t = 0 differs in 30 per cent of its cells, uniformly over the block, by
4.5e-13 at most. The claim "byte-identical without the option" of entry 3 was made for
the first source version (224b9629) and was true for it only.

**Where it came in** (unregistered diagnostics, `scratch/core/tmp/faces_bisect/`: one
step of `inputs/punc.athinput` with each frozen executable, sha256 of `punc.con.00000.bin`
and `punc.z4c.00001.bin`): base (27b2ced), sbc1 (224b9629), release core-v0.3 and release
core-v0.5 give the same two files; sbc2 (6cd99721), sbc3 (cb50e22), the merged source
(`.work/exe/merge0`) and the merged source without the damping (`.work/exe/sbc4`, ca6b46cb)
give two other files, the same among the four. So the change came with the second source
version of this package and has nothing to do with the merge or the removal.

**Cause** [VERIFIED for the file named, by compilation]. Instruction counts of the object
files of this build against those of the release build
(`/data/haiyangw/nrpic/.work/build_cpu_v05`, same flags `-O2 -g -march=icelake-server`):
`z4c_adm.cpp.o` the same (23505 instructions, 226 fused multiply-adds), but
`z4c_calcrhs.cpp.o` 34670 instructions and 469 fused multiply-adds against 34683 and 467,
although `z4c_calcrhs.cpp` is unchanged. Compiling that one file with variants of the
headers (8 s each; `faces_bisect/cc.sh`, overlay directory first on the include path):

| `z4c.hpp` / `z4c_sbc_ext.hpp` | instructions | fused multiply-adds |
|---|---|---|
| release `z4c.hpp` | 34683 | 467 |
| release + the two method declarations | 34683 | 467 |
| release + `#include "z4c/z4c_sbc_ext.hpp"` only (no member) | 34670 | 469 |
| current, member `sbc` moved to the end of the class | 34670 | 469 |
| current `z4c.hpp`, options header of 224b9629 | 34683 | 467 |
| current `z4c.hpp`, options header with data members and declarations only | 34683 | 467 |
| the same with the current includes and the inline `Fatal` | 34683 | 467 |
| current options header with `Read` only declared | 34683 | 467 |
| current options header without `<cstdlib>` | 34670 | 469 |

The body of the inline `SbcExt::Read` (strings, a dozen parameter look-ups) in a header
that `z4c.hpp` includes makes g++ 11.4 compile the right-hand side kernel of another file
with two more contractions into fused multiply-adds. Neither the layout of the class nor
the declarations matter. How the compiler gets there is not examined [JUDGEMENT: the
template instances the body brings into the translation unit shift its inlining
decisions]. The lesson for every package of core: a header reached from `z4c.hpp` holds
declarations and data, no function bodies of any size; and "no code path changed" does
not give byte identity, only the regression run does.

**What it means for the runs of this package.** Every run with the executables sbc2 and
sbc3 (c0 to c4, t1, b2, c3, the card runs D on their own compiler) solved the same
equations with a right-hand side that rounds differently in two places. The stock
references of a1 (base executable) and the option runs therefore differ by that rounding
beside the options; r1 measures its size (7e-12 after 4 steps of the puncture, 5e-10
after 8 steps of the ball), 5 to 7 orders below the smallest effect quoted in entries 7
to 11. No conclusion changes; the byte regression is what was false.

**Correction.** `SbcExt::Read` (and `Fatal`) moved into the new file
`athenak/src/z4c/z4c_sbc_ext.cpp`; the header keeps the data members, the one-line
`Extended()` and the declaration, and includes only `athena.hpp`. With it
`z4c_calcrhs.cpp` compiles to the release's 34683 instructions and 467 fused
multiply-adds (checked before the build).

**Predictions** [JUDGEMENT], before the new build is finished:
- o1 (`compare_objects.py`, new build against the release build, `specs/o1.txt`): every
  object file has the same histogram of instructions as in the release build, except
  those of the changed sources (`z4c/z4c.cpp`, `z4c_Sbc.cpp`, `z4c_tasks.cpp`); the two
  new files exist on one side only. Refuted by any other object: then another header
  effect is left.
- r2 as in entry 11 (byte-identical with core-v0.5; the periodic case is
  `problems/tests/lw_oblique.athinput`, a linear wave, because `mpi_box_periodic` named
  there has no spacetime solver and needs a generated particle file).
- m1 REVISED before it runs: the frozen executable of cb50e22 has the other right-hand
  side, so exact equality of the arrays cannot hold and is not what the test can show.
  New statement: with the full set the new executable agrees with the frozen one to
  rounding: largest difference of any dumped array and history number below 1e-7 (the
  dumps are single precision) for the four cases, and of the size r1 measured (below
  1e-8 for the arrays of magnitude below 0.1). Refuted by a difference above 1e-7: then
  the merge or the removal changed the arithmetic of the options.
- s1 gets a third case, ball_full (the full set, new executable, to t = 16): its region
  means of |H| agree with ball_g4nw_met of c1 (executable sbc2) to 1e-4 relative at
  every dump.
- k, card check of the merged card executable (`plans/card_k1.list` with the new card
  executable: the vacuum puncture 4 steps without the options, 8 steps with the full
  set; `plans/card_k2.list`: the 4 steps with the release card executable
  `/data/haiyangw/nrpic/.work/build_gpu_v05/src/athena`; two jobs of two minutes, which
  is what is left of the card-hour of this package after the 0.93 of entry 10):
  (k-a) the two runs without the options give byte-identical files (no deposition, so a
  card run repeats); (k-b) the card run without the options agrees with the processor
  run punc__new of r2 to rounding (largest array difference below 1e-7); (k-c) the card
  run with the full set agrees with punc_full__new of m1 to the same level. Refuted for
  (k-a) by any differing file: then the card build has its own sensitivity and the
  statement "unchanged without the options" holds for processors only. Submitted when
  the card build is finished; if the queue does not start them in this session they
  are named as pending.

## 2026-11-21, entry 13: outcomes of the closing tests (r1, o1, r2, m1, t1b, s1, c2-c, c4 for the punctures, c5); the summary

Source of everything below: commit f6f9a0d (processor executable frozen as
`.work/exe/sbc5/athena_cpu`). Analysis runs: core-20261121-082457-ab56e8f (r1),
core-20261121-082023-f8e7dab (o1, m1, t1b, s1, c5; first version of the figures),
core-20261121-082550-fe84ced (r2 again, t1b, s1, c5 with corrected figures, summary).
Results `results/{r1,o1,r2,m1,t1b,s1_ball,c5_punc,c5_boost,summary}.json`; figures
`figs/{r1_regress,o1_objects,r2_regress,m1_merge,t1b_smrface,s1_ball_regions,
c5_punc_regions,c5_boost_regions,summary}.png`, each looked at.

**r1** (registered now; run core-20261120-220733-ea71a73): FAILED, as entry 12 describes:
ball 8 of 11 files differ, boosted and vacuum puncture 3 of 5 each, by_binary 4 of 9,
horizon_calib 5 of 10, kg_wave_smr 1 of 1. The analysis run carries the status "failed"
for that reason.

**o1** (new build against the release build, 204 object files): FAILED in the letter
for one object, for a reason that is understood. Three of the four objects with another
histogram are the changed sources (`z4c/z4c.cpp.o`, `z4c_Sbc.cpp.o`, `z4c_tasks.cpp.o`);
the fourth, `mesh/meshblock_pack.cpp.o`, has 4467 instructions against 4469 and no
fused multiply-add on either side: the size of the class `Z4c` that it passes to `new`
and `delete` is 0xb30 instead of 0xae0 (the 80 bytes of `SbcExt`), and the compiler
merged one cold exit path differently. No floating-point instruction differs in any
unchanged file; `z4c_calcrhs.cpp.o` is back at the release's histogram.

**r2** (run core-20261121-080705-f6f9a0d, new executable without the options against
the release core-v0.5): HELD. Every output file is byte-identical: ball 11 files,
vacuum puncture 5, boosted puncture 5, horizon_calib 10 (with restart, trajectory and
horizon files), by_binary 9, kg_wave_smr 1, the periodic linear wave 4: 45 files, none
differs. `tests/z4c_bench` has no output block and writes no file: that pair tests
nothing (it was in the plan of r1 and cost ten core-minutes; it is reported, and the
first evaluation, core-20261121-082154-74071af, ended with status 1 for it alone).

**m1** (run core-20261121-080713-8a8fa28; revised statement of entry 12): HELD. With the
full set the new executable and the frozen one of cb50e22 agree to rounding: largest
difference of any dumped array or history number 2.9e-11 (ball, 16 steps), 7.3e-12
(vacuum puncture, boosted puncture, refined region at the face; 8 steps), the size r1
measured for the other right-hand side. So neither the merge of core-v0.5 nor the
removal of the damping changed what the options compute.

**t1b** (run core-20261121-081236-84b1a29; the full set without damping): HELD. No
non-finite value. Largest |H| within 4 of the +x face: fine part 2.11e-6 against
1.79e-3 with the stock conditions (1.2e-3 of it; with damping it was 2.0e-6), coarse
part 6.8e-7 against 8.0e-4. CORRECTION of entry 10: the "junction zone" of the t1
analysis lay at 2 <= max(|y|, |z|) < 6, where there is no junction: the refined region
of the input (|y|, |z| < 3.9) is rounded outward to whole MeshBlocks of 8 cells, so the
fine part of the face reaches to 8. With the junction read from the cells the zone
(within 2 of it) has 2.11e-6 at most with the full set and 1.48e-3 with the stock
conditions; along the face the boundary cells next to the junction have 6.5e-7 (full
set), below the value at the face centre (1.3e-6): no excess at the junction
(`figs/t1b_smrface.png`, now with the cells drawn in their size).

**s1** (run core-20261121-081422-0e46ba2; ball to t = 16, new executable):
- ball_full against ball_g4nw_met of c1 (executable of 6cd99721): the region means of
  |H| agree to 2.3e-11 relative at every dump (predicted 1e-4): HELD. The tests c1 to
  c3 speak for the delivered executable.
- `sbc_speed = lapse`: HELD. Against metric the face-layer and shell mean |H| at t = 8
  change by less than 1 per cent (1.02e-3 both; 7.93e-4 against 7.94e-4), at t = 16 the
  shell is 9 per cent lower (1.79e-3 against 1.97e-3); reaches t = 16, face-layer
  maximum of |H| 5.1e-3 at the end (stock 1.57e-2).
- `sbc_theta = nonwave`: HELD (it does not help). Face-layer mean |Theta| 5.99e-5
  against 5.14e-5 at t = 4 (17 per cent higher) and 8.20e-4 against 5.88e-4 at t = 16;
  reaches t = 16, face-layer maximum 6.0e-3. The option is delivered as tested and not
  recommended, like cpbc.

**c2-c** (punc_g4nw of core-20261120-222537-1011ec4 against punc_g4nw_met): FAILED. At
t = 12 the metric speeds give a shell mean |H| of 1.44e-5 against 1.40e-5 with unit
speeds (3 per cent higher, predicted 10 per cent lower), a face layer of 1.19e-5
against 8.5e-6 and a whole box of 1.83e-5 against 1.61e-5. In the ball the metric
speeds were the better ones (c1-d: 26 per cent at t = 8, a factor 1.5 at t = 16). So
`sbc_speed` is a second-order choice whose sign depends on the set-up; the gain of the
set is in the ghost fill, the order and the non-wave part.

**c4 for the punctures** (run core-20261120-220735-a7966ff, executable of cb50e22):
- (c4-d) FAILED in the letter: the face-layer Gamma constraint at t = 4 falls 2.4 times
  (9.1e-7 against 2.17e-6, vacuum) and 2.6 times (4.3e-6 against 1.13e-5, boosted) with
  both dampings at 4, predicted more than 3.
- (c4-e) held for the two punctures: no growth to t = 12; the whole-box mean |H| at
  t = 12 is 1.58e-5 against 1.83e-5 (vacuum) and 2.24e-5 against 3.31e-5 (boosted).
  The damping helps these two by 1.2 to 2.7 and blows up in the ball (entry 11): it
  stays removed; a stable form would be worth a package of its own.

**c5, boosted puncture against its reference** (faces at 32, run
core-20261120-222543-9a83982, to t = 8):
- (c5-a) HELD: shell (8 <= r < 12) mean |H| at t = 8: 4.37e-6 with the full set, 3.35e-6
  in the reference (1.30 times), 5.02e-5 with the stock conditions (15 times).
- (c5-b) HELD: face-layer mean |M_i| at t = 4: 3.39e-6 (full set), 3.24e-8
  (reference), 4.29e-5 (stock): 105 and 1320 times the reference. The faces still make
  a layer; it is 13 times weaker.
- inner region 5 <= r < 8 at t = 8: 2.23e-5 (full set) = 2.23e-5 (reference), stock
  2.63e-5.

**Summary: mean |H| before and after** (`figs/summary.png`, `results/summary.json`;
"full set" = `ghost_falloff = true`, `extrap_order = 4`, `sbc_variant = nonwave`,
`sbc_speed = metric`; reference: the same cells with the faces at 32, valid to t of
about 8 to 11):

| set-up, region | t | stock | full set | reference |
|---|---|---|---|---|
| ball, r < 8 | 8 | 4.03e-3 | 3.54e-3 | 3.53e-3 |
| ball, r < 8 | 16 | 1.69e-2 | 2.12e-3 | 3.9e-5 |
| ball, 8 <= r < 12 | 8 | 2.80e-3 | 7.94e-4 | 7.35e-4 |
| ball, whole box | 8 | 3.73e-3 | 1.08e-3 | 6.36e-4 |
| ball, whole box | 16 | 7.07e-3 | 1.70e-3 | 4.10e-4 |
| vacuum puncture, 5 <= r < 8 | 8 | 2.13e-5 | 1.63e-5 | 1.63e-5 |
| vacuum puncture, 8 <= r < 12 | 8 | 2.09e-5 | 2.14e-6 | 2.05e-6 |
| vacuum puncture, whole box r >= 5 | 8 | 1.07e-4 | 3.11e-6 | 1.23e-6 |
| vacuum puncture, whole box r >= 5 | 12 | 1.14e-4 | 1.83e-5 | (none) |
| boosted puncture, 5 <= r < 8 | 8 | 2.63e-5 | 2.23e-5 | 2.23e-5 |
| boosted puncture, 8 <= r < 12 | 8 | 5.02e-5 | 4.37e-6 | 3.35e-6 |
| boosted puncture, whole box r >= 5 | 8 | 1.48e-4 | 1.26e-5 | 1.84e-6 |
| boosted puncture, whole box r >= 5 | 12 | 1.77e-4 | 3.31e-5 | (none) |

Until the faces at 32 are felt the interior and the shell of all three set-ups sit at
the reference with the full set; the whole-box mean, which the stock conditions hold at
1e-4 from the first step (the monitor reading linear ghosts), falls 34 times (vacuum)
and 12 times (boosted) at t = 8 and 3.5 times in the ball. What is left: the faces
still reflect. The ball at t = 16 has an interior residual 55 times the reference
(8 times below stock), and the face layers stay 30 (vacuum) to 100 (boosted) times
above the truncation level of a mesh with distant faces.

**Card check k: not submitted.** At 00:20 PST two jobs of owner core (4775, 4777,
other sessions) were queued behind two running jobs, so by the rule of the machine
nothing was submitted. The card executable of f6f9a0d is built and published but has
not run on a card; the card tests of this package (D, entry 10) ran with the card
executable of 6cd99721. The lists `plans/card_k1.list` and `card_k2.list` and the
prediction of entry 12 stand for whoever has the next free slot.

## 2026-11-21, entry 14: the example input; prediction e1

`problems/tests/z4c_faces.athinput`: the vacuum puncture of the package with the four
options of the full set switched on in the input and every other option of the block
listed at its default, with the command lines of the variants in its header. Prediction
e1 [JUDGEMENT] (`plans/e1_example.json`, executable of f6f9a0d): run for 8 steps it
gives exactly the arrays and history numbers of `inputs/punc_ext.athinput` with the
same four values on the command line (largest difference 0), and with the four values
set back to the stock ones on the command line, 4 steps, exactly those of
`inputs/punc.athinput`, which has none of the options (an option present with its
stock value is the same as an absent one). Refuted by any difference.

**e1** (run core-20261121-083038-5f7ea42, analysis core-20261121-083244-7bf063a,
`results/e1.json`, `figs/e1_example.png`): HELD. The example input and the package
input with the same four values on the command line give exactly the same arrays and
history numbers (10209 compared, largest difference 0), and so do the example with the
stock values on the command line and `inputs/punc.athinput`, which has no option at
all. The byte comparison in the same analysis differs in the four dump files of each
pair and gives the run its status "failed": the header of a dump repeats the
parameters, which are written differently in the two inputs; the history files are
byte-identical.

**Published** (2026-11-21 00:33 PST): `/data/haiyangw/nrpic/scratch/core/exe/core_z4c-faces/`
with `athena_cpu` (the frozen `.work/exe/sbc5/athena_cpu`, with which r2, m1, t1b, s1 and
e1 ran), `athena_gpu` (`scripts/build_gpu.sh .work/build_gpu`, same source, not run on a
card), `COMMIT`, `SHA256SUMS`, `READY` (copy: `analysis/faces/READY.txt`). Source of both:
f6f9a0d; `git diff f6f9a0d HEAD -- athenak scripts` is empty.

**State at the end of the session** (for a reader with no memory). Done: the
investigation (entries 1 to 8), the options (ghost fill with fall-off, non-wave
radiative condition, speeds, Theta variants), their tests on processors and on a card
(entries 7 to 13), the byte regression against release core-v0.5 (r2), the interface
text `tracks/core/interfaces/z4c_faces.md`, the example input, the published
executables. Not done: (1) the card check k of the delivered card executable (two
minutes; lists and prediction ready; not submitted because two jobs of core were
queued); (2) a constraint-absorbing treatment that works: `sbc_theta = cpbc`,
`nonwave` and the damping of Theta gained nothing, the damping of the Gamma constraint
was unstable and is removed, so the faces still reflect (ball at t = 16: interior 55
times the reference); (3) the horizon proxy with distant faces (c3 decides nothing:
both runs are under-resolved; about ten core-hours); (4) several ranks, the threaded
build and adaptive refinement at a face. Card time of the package: 0.93 card-hours
(the two runs D), none in this session.

**Card check, one job of the two.** At 00:34 PST one job of core was left in the queue
(4777), so one may be added: k1 (`plans/card_k1.list`, the published card executable:
4 steps without the options, 8 steps with the full set; limit 3 minutes, which brings
the card time of the package to at most 0.98 card-hours). It tests (k-b) and (k-c) of
entry 12 as written there. k2 (the release card executable, for the byte comparison
k-a) is not submitted. The evaluation is `specs/k1.txt` (`compare_data.py --pair`).
