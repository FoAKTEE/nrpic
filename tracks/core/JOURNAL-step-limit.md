# JOURNAL of the work package "step-limit" (owner core, branch core/step-limit, batch 11)

The step limit of Z4c and the gauge speeds (request W31 of `interfaces/REQUESTS_WAVE3.md`
on core/nrpic; decision 0027 item 2). Labels: [VERIFIED] read in a source at the locator
given or measured in a registered run; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY]. Run ids are
directories under `tracks/core/runs/`; outputs under
`/data/haiyangw/nrpic/scratch/core/<run_id>/`. Analysis and figures:
`tracks/core/analysis/step_limit/`. Times are PST of 2026-11-24 unless a date is given.

## Entry 0 (04:51 to 05:40): what was read, the derivation, the design, predictions of T0

### Read

`CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; decisions 0010, 0019, 0027;
Track A's request `track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261121T231546Z__to-core__periodic-gamma-driver-step.md`
and its package `periodic_diag` (README, `scripts/vonneumann.py`, `inputs/diag_uniform.athinput`,
`scripts/run_uniform.sh`, `run_refined.sh`); item W31 of `core/nrpic:tracks/core/interfaces/REQUESTS_WAVE3.md`;
the source: `z4c/z4c_newdt.cpp`, `z4c/z4c_calcrhs.cpp` 560-790, `z4c/z4c_gauge_ext.hpp`,
`z4c/z4c.cpp` 126-177, `utils/finite_diff.hpp` (Dx, Dxx, Dxy, Lx, Diss), `driver/driver.cpp`
100-177, `z4c/z4c_tasks.cpp` 155-184, `z4c/z4c_update.cpp`, `mesh/mesh.cpp` 615-689;
`tracks/core/RELEASE-v0.6.md` (the byte regression and the lesson of core/z4c-faces: a
function body in a header that `z4c.hpp` includes changed the compilation of the unchanged
`z4c_calcrhs.cpp`). State of the worktree: clean, `main` merged by fast-forward, branch
renamed `core/step-limit`; `athenak/src` on main is the source of tag core-v0.6
(`git diff core-v0.6 HEAD -- athenak/src python/nrpic` is empty) [VERIFIED].

### How the code forms the step [VERIFIED by reading]

`Z4c::NewTimeStep` sets `dtnew` = smallest cell size, and with `<z4c> dt_lightspeed = f`
the smaller of that and f dx_d/c_d with c_d = alpha sqrt(chi gt^dd) + |beta^d|
(`z4c_newdt.cpp`). `Mesh::NewTimeStep` takes dt = min(2 dt_old, cfl_number x dtnew, the
particles' own limit) (`mesh.cpp` 624-668). One step for all levels (no subcycling). So
with `cfl_number = 1.0` and `dt_lightspeed = 0.25` the step is min(dx, 0.25 dx/c) on the
finest level: it grows to dx when the coordinate speed of light falls below 0.25, whatever
the gauge speeds are.

### The gauge sectors as the code evolves them [derivation; coefficients VERIFIED by reading]

Frozen coefficients about a slice with lapse alpha, conformal factor chi (chi = psi^-4,
gamma^ij = chi gt^ij), inverse conformal metric gt^ij, shift beta. Principal parts
(`z4c_calcrhs.cpp`: lapse 696-701, Khat 629, shift 722-733, Gam 587-596 and 658):

- Lapse: d_t alpha = -f alpha Khat + la beta.d alpha - delta alpha,
  d_t Khat = -chi gt^ij d_i d_j alpha + beta.d Khat, with
  f = lapse_oplog x lapse_harmonicf + lapse_harmonic x alpha + lapse_volume/sqrt(chi)
  (+ lapse_kdriver x alpha_ref). The relaxation `lapse_leak` adds no derivative; linearized
  where alpha > alpha_ref it damps alpha at the rate delta = lapse_leak (1 + ln(alpha/alpha_ref))
  (`z4c_gauge_ext.hpp` 127-131). Dispersion omega^2 = f alpha chi gt^ij k_i k_j: coordinate
  speed along x^d **v_lapse = sqrt(f alpha chi gt^dd)**, sqrt(2 alpha chi gt^dd) for 1+log.
  In flat space (alpha = chi = 1) this is sqrt(2), faster than light.
- Shift: d_t beta^i = mu Gam^i - eta beta^i + sa beta.d beta^i,
  d_t Gam^i = gt^jk d_j d_k beta^i + (1/3) gt^ij d_j d_k beta^k + beta.d Gam^i + (terms in
  d Khat, d Theta, which feed the shift but are not fed by it in this block), with
  mu = shift_Gamma + alpha^2 shift_alpha2Gamma. Dispersion: longitudinal
  omega^2 = (4/3) mu gt^ij k_i k_j, transverse omega^2 = mu gt^ij k_i k_j: coordinate speeds
  **v_long = sqrt((4/3) mu gt^dd), v_trans = sqrt(mu gt^dd)**, independent of alpha and chi
  (with shift_alpha2Gamma they carry alpha). This is Track A's statement; I agree.
- Light (for comparison, the pair gt_ij, At_ij as a scalar wave): alpha sqrt(chi gt^dd).

The lapse pair is closed in its principal part. The shift pair is fed by Khat and Theta;
in the full system Theta is fed back by Gam and the metric by d beta, so the shift block
is not strictly closed. Track A's model and mine treat it as closed [JUDGEMENT]; whether
that is good enough is decided by runs (T2 below brackets the threshold in the code).

### The discrete bound [derivation]

With centred stencils the first derivative has the symbol i s1(theta)/dx, the second
-s2(theta)/dx^2, the mixed one the product of two first derivatives, the Kreiss-Oliger
term -diss sin^(2 ng)(theta/2)/dx per direction (diss = `<z4c> diss`; `z4c.cpp` 177), the
advective derivative a complex symbol that is real and negative at theta = pi. A pair
(u, v) with u' = -(D + d1) u - p v, v' = q s2 u - (D + d2) v has the eigenvalues

    lambda = -(D + (d1 + d2)/2) +- sqrt(((d1 - d2)/2)^2 - Omega^2),  Omega^2 = p q S2 .

At the grid-scale corner theta = (pi, pi, pi): s1 = 0, so the grad-div term of the shift
drops out there and all three shift modes have Omega^2 = mu s2max sum_d gt^dd/dx_d^2 (the
transverse value, not 4/3 of it); S2 is largest; D = diss sum_d 1/dx_d. The step is stable
when lambda dt lies in the stability region of the integrator. For pure oscillation and
RK4 that is |lambda| dt <= 2 sqrt(2), i.e. without dissipation

    dt/dx <= 2 sqrt(2)/sqrt(3 s2max c^2),   s2max = 272/45 (nghost 4): 0.664/c ,

c the speed of the corner mode: sqrt(mu gt) for the shift (0.767 at mu = 0.75), sqrt(2
alpha chi gt) for 1+log (0.470 in flat space), alpha sqrt(chi gt) for light. Dissipation
moves the eigenvalue to the left, where the RK4 region is narrower along the ray, and the
bound falls (Track A: 0.685 at diss 0.5). A relaxation term adds the bound rho(0)/delta
of the homogeneous mode (2.785/delta for RK4) and shifts the corner pair.

### Design [JUDGEMENT]

Option `<z4c> dt_gauge = f` (off when absent): every cycle the step is kept at or below f
times the smallest, over the cells and the three sectors (shift, lapse, light), of the
largest stable step of the frozen-coefficient pair at the grid-scale corner and of the
homogeneous relaxation, with the stability region of the integrator in use (rk3, rk4)
read from a table of first-exit radii along rays. It is a bound on the step itself
(divided by `cfl_number` before the mesh multiplies with it), so that it acts at any
`cfl_number` and does nothing where the step is already below it. New code in a file of
its own (`z4c/z4c_newdt_gauge.cpp`), hooks: three lines in `z4c_newdt.cpp`, two in
`z4c.cpp`, data members and two declarations in `z4c.hpp`. At start-up the bound is
evaluated once whether or not the option is given, and a warning is printed when
`cfl_number` x (smallest cell) exceeds it or when lapse_leak x that step exceeds its bound.

### Predictions of T0 (the reference computation `analysis/step_limit/vonneumann_gauge.py`), written before it ran

- P0a. The two-register schemes of the driver have the Taylor polynomial of their order as
  stability polynomial (rk2, rk3, rk4), to 1e-12. Refuted: a different polynomial (the
  bound would then need the scheme's own).
- P0b. Kreiss-Oliger symbol equals diss sin^(2 ng)(theta/2) to rounding; s2(pi) = 4, 16/3,
  272/45 and the advective symbol at pi is real, -4, -8/3, -32/15, for nghost 2, 3, 4.
- P0c. My scan of the Brillouin zone reproduces Track A's thresholds to its grid step
  0.0025: shift 0.685 (level 4) and 0.65 (root), 0.77 without dissipation (I expect
  0.767), lapse with leak 20: 0.97 (level 4), 0.405 (root); light stable beyond 1.2 on
  level 4; shift_Gamma 0.3: 0.94 and 0.90. Refuted: a difference above 0.005.
- P0d. The reduced model (corner pair and homogeneous relaxation) gives the full scan's
  threshold within 1 per cent for zero background shift, for nghost 2 to 4, rk3 and rk4,
  dissipation 0 to 1 and relaxation rates up to 6/dx: the corner fails first. With a
  background shift up to 1 it stays within [0.8, 1.02] of the full scan. Refuted: a ratio
  above 1.02 (the reduced model would then allow an unstable step and needs a correction).
- P0e. Flat space, RK4, nghost 4, no dissipation: lapse 0.470, light 0.664, shift
  (mu 0.75) 0.767; with diss 0.5 each about ten per cent lower.
- P0f. lapse_leak x dt at the grid scale of the root mesh: 2.5 (Track A), homogeneous 2.785.

## Entry 1 (05:45 to 06:05): outcome of T0, correction of the advection term, predictions of T0b

Run core-20261124-130414-c77ee7e (`vonneumann_gauge.py`, commit c77ee7e, 13 minutes on one
core; `vonneumann_gauge.json`, figures looked at: `fig_vonneumann.png` clear, the reduced
model's markers sit on the thresholds of the four curves in both panels;
`fig_reduced.png` left panel clear, right panel has its legend over the data and is drawn
again in T0b).

- P0a held: the stability polynomials of rk2, rk3, rk4 as the driver applies them differ
  from the Taylor polynomials by 0.0 (to the last bit of the coefficients).
- P0b held: Kreiss-Oliger symbol minus sin^(2 ng)(theta/2): 0.0; s2(pi) = 4, 5.3333,
  6.0444; advective symbol at pi -4, -2.6667, -2.1333 with imaginary part 4e-16.
- P0c held. Full scan (bisected) / on Track A's grid of 0.0025 / Track A:
  shift level 4: 0.6829 / 0.685 / 0.685; shift root: 0.6485 / 0.65 / 0.65; shift without
  dissipation: 0.7699 (level 4), 0.7978 (root) / 0.77, 0.80 / "0.77 to 0.80" (my 0.767 is
  the value without the damping eta, which raises it); lapse with leak 20: 0.9670 /
  0.9675 / 0.97 (level 4), 0.4040 / 0.405 / 0.405 (root); light 1.2420 (Track A: stable
  to the end of its range, 1.2); shift_Gamma 0.3: 0.9397, 0.8978 / 0.94, 0.90. The 6 x 6
  matrix of the shift gives the same thresholds as the split into pairs (0.6829, 0.6485).
  In every one of these cases the mode that fails first is the corner (pi, pi, pi).
  **I agree with Track A's analysis in all its numbers.** Where I add to it: (i) at the
  corner the shift modes have the transverse speed sqrt(mu gt), so the bound in units of
  the longitudinal speed sqrt(4 mu/3 gt), which Track A's request names, is 0.767 x
  sqrt(4/3) = 0.886 dx/v_long without dissipation; the limit must not be written as
  0.685 dx/v_long with v_long = sqrt(4 mu/3) for other mu (for mu = 0.3 the scan gives
  0.94, the rule would give 1.08); (ii) the lapse sector in flat space, below.
- P0d: for zero shift held for the scheme in use (rk4, nghost 4: reduced/full between
  0.9933 and 1.0000 in 64 cases); partly failed elsewhere: rk4 nghost 3 up to 1.016, nghost
  2 up to 1.122 (both only at diss 1.0 with a damping of 6/dx), rk3 between 0.959 and
  1.009 (nghost 4). **Refuted for a background shift**: with |beta| = 0.3 the reduced
  model allowed steps up to 1.44 times the full scan's, with |beta| = 1 up to 1.56. Cause
  by construction of the model [VERIFIED in the scan: the first unstable mode is then not
  the corner]: at the corner the advective stencil only damps; away from it its symbol
  has an imaginary part (largest 1.950 for nghost 4 at theta = 0.68 pi) that adds to the
  wave frequency.
- P0e: held without dissipation (lapse 0.4697, light 0.6642, shift 0.7670); "ten per cent
  lower with diss 0.5" failed for the lapse: 0.4681 (-0.3 per cent), light 0.6181 (-7),
  shift 0.6856 (-11). With diss 0.1 all three are higher than without (0.4825, 0.6865,
  0.7944): a little dissipation helps, more hurts.
- P0f held: lapse_leak x dt = 2.525 at the grid scale of the root mesh, 2.785 for the mode
  without structure.

Consequence for every owner [VERIFIED in the model, TO VERIFY in the code by T2]: in flat
space with 1+log (alpha = chi = 1) the lapse pair moves with sqrt(2) and binds first, at
dt/dx = 0.47 (rk4, nghost 4, with or without diss 0.5); light at 0.62 to 0.66; the
Gamma-driver with mu = 0.75 at 0.69 to 0.77. The rule of decision 0027, cfl_number at or
below 0.6, is therefore right for the expanding box (where the lapse speed
sqrt(2 alpha chi) is about 0.5) and too weak for asymptotically flat set-ups with 1+log:
there the bound is 0.47. Of the 100 inputs under `problems/` 67 use 0.25, 31 use 1.0
(none of those evolves Z4c with a 1+log lapse as far as their names say; the warning at
start-up will tell), one 0.4, one 0.1 [VERIFIED by grep].

Correction (exploration `scratch/core/tmp/explore_adv.py`, four variants against the full
scan, not registered: a design choice, tested by T0b): the frequency of the corner mode
becomes Omega = sqrt(s2max sum_d c_d^2/dx_d^2) + limag sum_d |beta^d|/dx_d with limag the
largest imaginary part of the advective symbol (2.2018, 1.9510, 1.9501 for nghost 2, 3,
4); the damping of the corner stays. Kernel and Python twin changed alike.

### Predictions of T0b (the same script with the corrected reduced model), written before it ran

- P0g. rk4, nghost 4: reduced/full at most 1.01 in every case of the survey, shift up to
  1 included; at least 0.75 (the model may be up to a quarter too careful with a large
  shift). Refuted: a ratio above 1.01.
- P0h. rk4 nghost 3: at most 1.03. nghost 2 and rk3: at most 1.2, the excess only with
  strong damping. Zero-shift numbers unchanged from T0 (the correction acts only on
  beta).
- P0i. Track A's cases unchanged (no shift in them).

## Entry 2 (06:05 to 06:35 by the first clock reading; by `date` 05:20 to 05:35): outcome of T0b, second correction, T0c

Times of entries 0 and 1 were estimated, not read: `date` gave 05:17 when T0 ended and
05:31 when T0b had ended; entry 0 covers 04:51 to about 05:02, entry 1 about 05:17 to 05:20.

Run core-20261124-132639-eb9be13 (commit eb9be13, 1536 survey cases, 4 minutes).

- P0i held: Track A's cases unchanged to the digits printed.
- P0h: the zero-shift numbers are unchanged (held). The bounds with a shift failed with P0g.
- **P0g refuted**: rk4, nghost 4 with a shift: reduced/full between 0.797 and 1.328; nghost
  3 up to 1.389, nghost 2 up to 1.349, rk3 up to 1.28. The five worst cases all have a
  damping of 6/dx (a relaxation rate of the size of lapse_leak = 20 on the 64-cell root
  mesh) and |beta| = 1: the pair is then overdamped (real eigenvalues), and the second
  version, which added the phase rate of the advection to Omega under the root, lost it
  there. [VERIFIED by recomputing the reduced bound for all 1536 saved full scans with the
  phase rate added to the imaginary part of both eigenvalues instead: script
  `scratch/core/tmp/explore_E.py`, not registered.]

Adopted (third version): lambda = -(D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2)
+ i limag sum_d |beta^d|/dx_d, the phase rate of the advective stencil on both
eigenvalues, the damping of the corner in e1 and e2 as before. This is the structure of
the true symbol when both members are advected alike (the symbol of the advection adds
to both eigenvalues); the simplification is that its damping is taken at the corner and
its phase rate at its maximum.

### T0c (the same script, third version): what the recomputation already gave, to be repeated as a registered run with figures

Not a blind prediction: the numbers below come from the recomputation named above, on
the same survey. T0c is their registered record. rk4, nghost 4: zero shift 0.993 to
1.000; with a shift 0.818 to 1.099, and at most 0.98 whenever the damping is 1.5/dx or
less (the excess up to 1.10 only with a damping of 6/dx and |beta| >= 0.3); rk4 nghost
3 up to 1.19, nghost 2 up to 1.31 (shift sector, damping 6/dx, |beta| = 1), rk3 up to
1.25. Refuted if the registered run gives other numbers. Consequence for the option's
text: the fraction 0.9 covers rk4 with nghost 4 in the whole survey; for nghost 2 or 3
or rk3 with strong damping and a shift of order one a fraction of 0.75 is needed.

## Entry 3 (05:35 to 05:55): tests T1 to T6, written before any of them ran

What ran before this entry besides T0, T0b: one unregistered smoke of the deck
`problems/tests/z4c_step_limit.athinput` (40 steps, `scratch/core/tmp/sl_try1`) to see
that `nrpic_cosmo` starts without a `<particles>` block and that the option is read. It
printed the bounds 0.647066, 0.467928, 0.616644 cells (shift, lapse, light); T1 below is
the registered comparison.

Change to the warning before the tests: the step each sector can meet differs. With
`dt_lightspeed` the step stays a fixed fraction of dx/c, so light is judged at the present
step; the gauge sectors at cfl_number x (smallest cell). Otherwise Track A's deck (light
bound 0.617 cells at the start, where c = 1, step 0.25 cells) would be warned about light.
The relaxation line is printed when lapse_leak x that step exceeds 1 and the step exceeds
the bound of the lapse pair with the relaxation counted in every cell.

Executables: this branch, `.work/build_cpu_sl` (serial), `.work/build_omp_sl` (threaded),
`.work/build_gpu_sl` (card), built from the commit that holds this entry.

### T1: the kernel against its Python twin

Flat space, dx = 0.3125, diss 0.5, rk4, nghost 4, five gauge settings (groups S, L, C, K, D
of `analysis/step_limit/run_flat.py`). Prediction P1: the three bounds of the start-up
line agree with `reduced_sector` to the six digits printed (1e-5 cells). Refuted: a larger
difference in any group.

### T2: the bound bracketed by runs of the code (could fail)

Same deck, noise 1e-10, 300 steps, one sector binding per group, bound b from the model:
cfl_number 0.93 b ("m"), 1.07 b ("p"), 1.07 b with dt_gauge = 0.9 ("g"). "Unstable": the
squared constraint monitor of the history grows by more than 1e6 over its first value,
or a field stops being finite (guard, exit 3).

- P2-S (Gamma-driver, shift_Gamma 1.5, lapse frozen): m stable, p unstable, g stable.
- P2-L (1+log, zero shift; b = 0.468): m stable, p unstable, g stable. This is the test of
  the statement that 1+log in flat space binds at 0.47, below the rule 0.6.
- P2-C (light alone, zero shift, lapse frozen; b = 0.617): m stable, p unstable, g stable.
  Less sure than S and L (four to one): the model treats the metric sector as one scalar
  wave [TO VERIFY].
- P2-K (lapse_leak 32, zero shift; b = 0.2785 from the mode without structure,
  lapse_leak x dt = 2.785): m stable, p unstable, g stable. Three to one: the relaxation
  acts on one side only (alpha above its reference), the model is its linearization.
- P2-D (the deck, 1+log and Gamma-driver 0.75, cfl 1.0): unstable without dt_gauge, with
  the warning at start-up naming the lapse; stable with dt_gauge = 0.9 at a step of
  0.9 x 0.468 = 0.421 cells.
- Warnings: printed in every p case and in D without the option, in no m case; the
  relaxation line in K_p.

What would refute the bound: an m case unstable (a sector fails below the model's bound:
couplings left out, or the metric sector is not a scalar wave), or a g case unstable.
A p case that stays stable would mean the bound is careful or the growth too slow for
300 steps; I would then repeat at 1.2 b before saying which.

### T3: Track A's uniform-mesh reproducer (64^3, dx = 0.3125, cfl_number 1.0, dt_lightspeed 0.25), threaded build, 6 threads

- P3a. G0 (lapse frozen, no dt_gauge) reproduces Track A's G0: warning at start-up naming
  the Gamma-driver shift with a bound of 0.647 cells; the step reaches one cell; the
  cell-to-cell alternation of beta^x on the line grows by more than 1e4 and the onset
  (Track A's definition) falls between t = 7 and 9 (Track A: 8.1).
- P3b. G0g (the same with dt_gauge = 0.9): the step stops at 0.9 x 0.647 = 0.582 cells;
  no onset to t = 12; the alternation of beta^x stays below 1e-6. Refuted by an onset or a
  growing alternation.
- P3c. U0 (relaxed lapse, leak 20, no dt_gauge) reproduces Track A's U0: both warnings at
  start-up (lapse bound 0.404 cells; lapse_leak x step 6.25 against 2.52); jump near
  t = 3.2 and a guard stop before t = 12 (Track A: 3.18 and 10.76).
- P3d. U0g (with dt_gauge = 0.9): the lapse pair sets the step, about 0.9 x 0.33 = 0.30
  cells once the lapse stands above its reference (relaxation rate 20 (1 + ln alpha));
  runs to t = 12 without guard stop and without the jump at 3.2. Two to one: the
  relaxation is one-sided and the root mesh is coarse for T = 0.05.

### T4: Track A's refined periodic deck through the time of its failure (one card job)

List `analysis/step_limit/card_refined.list`, P0L data, cfl_number 1.0.
- P4a. R0 (no dt_gauge, to t = 3.2) repeats card job 4799: level-4 step above 0.685 cells
  from t = 1.7, H_max jumps by more than a hundred between t = 2.3 and 2.7.
- P4b. R0g (dt_gauge = 0.9, to t = 6): the message "set by dt_gauge, sector Gamma-driver
  shift" at t between 1.5 and 1.8; the step stays at 0.9 x 0.682 = 0.614 cells; no jump:
  H_max at t = 2.5 to 3.0 within a factor 3 of R1's, and the run reaches t = 6 (job 4799
  stopped at 4.8). Refuted by a jump or a guard stop.
- P4c. R1 (cfl 0.5, to t = 6) smooth; steps to t = 6: R0g needs 0.6 to 0.75 of R1's.
- Card time: under ten minutes for the three (0.17 s per step in job 4799).

### T5: cost

- P5a. Evaluating the bound every cycle costs less than 2 per cent of a cycle on
  processors (flat box 32^3, cfl 0.25, 40 steps, limit not binding, serial build; three
  repetitions each way) and less than 5 per cent on a card (flat box 128^3, 100 steps).
- P5b. The smaller step: from T3 and T4, steps to the same time with dt_gauge = 0.9
  against cfl_number 1.0 (unstable) and 0.5 (the remedy in use).

### T6: bytes

- P6a. Byte regression against release core-v0.6 (`analysis/release/regress_v04.py`,
  twelve set-ups, option absent): 75 of 75 items identical. Risk named in RELEASE-v0.6.md:
  a change to `z4c.hpp` can change the compilation of `z4c_calcrhs.cpp`; here three data
  members and two declarations were added, no function body.
- P6b. `survey_default.py`: the set-ups of the regression that evolve Z4c (I expect east,
  os, c4), run with dt_gauge = 1.0: histories byte-identical with the runs without it,
  the limit never sets the step (their cfl_number is 0.25, every bound above 0.4 cells),
  no warning without the option.

## Entry 4 (05:40): the card queue, and T4 moved to processors

`squeue` at 05:36: twenty jobs of this account pending on the two cards, six of them of
owner core (5154, 5155 by priority, 5156 to 5159 held: the bisection chains of the lead
session). Two core jobs are queued, so by the rule of the task and of CLAUDE.md I submit
no card job. Consequences:

- T4 runs on processors with the threaded build: `analysis/step_limit/run_refined.sh`,
  case R0g (cfl_number 1.0, dt_gauge = 0.9) to t = 3.0, 4 threads, about 310 cycles at
  about 20 s. The control without the option is Track A's card job 4799 itself (run
  A-20261121-131600-02b5d41, release core-v0.5, the same deck and data; read from
  `scratch/A-emd-pbh/`) and its processor run R2 with zero shift; a control R0 with this
  branch's executable (1.5 hours more) is not run. Predictions P4a and P4c, which need
  R0 and R1 of this branch, wait for the card job; P4b is judged to t = 3.0 instead of 6.
- The card job stays prepared and unsubmitted: `analysis/step_limit/card_refined.list`
  (R0, R0g, R1 of the refined deck). Command in the README of the package and in READY.
- P5a on a card is not measured.

Run core-20261124-134017-8c4e50c (first call of T1/T2) failed before any AthenaK run:
the driver changed directory and then looked for the executable by its relative path.
No result. The three drivers now make the path absolute.

Run core-20261124-134349-3543b27 (first call of T4, R0g) did not start: AthenaK accepts on
the command line only parameters the input declares, and Track A's decks do not declare
`dt_gauge` (exit 1 of AthenaK after 0.1 s; nrpic-run recorded the wrapper's exit 0). No
result. The two copies of Track A's decks in `analysis/step_limit/inputs/` now declare
`dt_gauge = 0.0` (off); their first line says so.

## Entry 5 (05:52): the first call of T1/T2 stopped in its analysis; what its cases showed; cases added

Run core-20261124-134052-fd8eb46 (commit fd8eb46) ran nine cases and stopped: the deck did
not declare `lapse_leak`, so the K cases did not start, and the driver then missed their
history files. The deck now declares `lapse_leak = 0.0` and `lapse_leak_alpha`; the
driver tolerates a missing history. The nine cases that ran are on record in that run's
directory, and I have read their logs, so what follows for S, L, C and D is no longer a
blind test (the complete registered rerun is the record):

- S: m stable (0.470 cells), p stopped by the guard at cycle 58, g stable. P2-S held.
- L: m stable (0.435 cells), p stopped by the guard at cycle 65 (0.501 cells), g stable.
  P2-L held: 1+log in flat space fails just above 0.47 cells.
- D: at cfl 1.0 without the option the guard stops the run at cycle 9, after the warning
  (lapse, bounds 0.647, 0.468, 0.617 cells); with dt_gauge = 0.9 it runs 300 steps at
  0.421 cells and the constraint monitor falls. P2-D held.
- **C: P2-C failed.** With zero shift and the lapse frozen the run at 0.93 b (0.5735
  cells) is stopped by the guard at cycle 149, the one at 1.07 b at cycle 32, and the one
  with dt_gauge = 0.9 (0.555 cells) runs 300 steps but its squared constraint monitor
  ends 14 times above its start (2.9e-13 against 2.0e-14) where S, L, D fall to 4e-18.
  So with a frozen lapse the code is unstable below the bound of the light pair of my
  model. I do not know the cause. Two readings, to be told apart by runs: (a) a step-size
  threshold of the metric sector that lies 10 to 15 per cent below the scalar-wave
  model's (then smaller steps are stable); (b) growth that is not a step-size effect (a
  constant lapse with zero shift is not a gauge in which the system need be well
  behaved; then smaller steps do not help). Either way the group does not test the
  light pair as I intended.

Cases added, with predictions written before they run:

- C_q (0.75 b = 0.462 cells) and C_h (0.5 b = 0.308 cells), frozen lapse, zero shift.
  Reading (a) predicts both stable (monitor falling as in S, L); reading (b) predicts
  growth in both. I lean to (a), three to two.
- Group H: harmonic slicing (`lapse_oplog = 0`, `lapse_harmonic = 1`: d_t alpha =
  -alpha^2 Khat), zero shift. Lapse pair and light pair then have the same speed 1 and
  the same bound b = 0.617 cells. P2-H: m stable (0.573 cells), p unstable, g stable;
  also q and h stable. This is the test of the light bound in a gauge with a dynamical
  lapse. If H_m is unstable, the light bound of the kernel is too high and must be
  lowered before the option is published.

## Entry 6 (05:55 to 06:02): the cause of the failed P2-C; Track A's model and mine corrected; runs stopped

While the complete T1/T2 was running I worked out the corner mode of the pair of the
conformal factor and Theta from the right-hand side, to see whether reading (a) of entry
5 has a mechanism. It has, and the same mechanism changes the shift.

**How the code takes second derivatives [VERIFIED, `z4c_calcrhs.cpp` 334-362].** d_a d_a is
the stencil `Dxx` (symbol -s2/dx^2); only d_a d_b with a != b is `Dxy`, the product of two
first derivatives (symbol -s1_a s1_b/dx^2), which vanishes at the corner theta = pi.

- **Conformal factor and Theta.** d_t Theta = (alpha/2) R + ..., R = 2 sum_d Dxx chi + chi
  d_k Gam^k + ...; d_t chi = (2/3) chi alpha (Khat + 2 Theta); d_t Gam^k = -(2/3) alpha
  d_k (2 Khat + Theta) + .... So d_t^2 Theta = alpha^2 chi [(4/3) sum_d Dxx - (1/3)
  sum_k Dx_k Dx_k] Theta: the speed of light in the continuum, but at the corner the
  second term is zero and omega^2 = (4/3) alpha^2 chi s2max sum_d 1/dx_d^2. The pair is
  there whatever the lapse condition is. With diss 0.5 in flat space the scan gives
  0.5537 cells (reduced 0.5510) instead of the 0.6166 of a scalar wave. This fits the
  three C cases of the aborted run without a free number: 0.555 cells (C_g) marginal
  with slow growth, 0.5735 stopped at cycle 149, 0.660 at cycle 32.
- **Shift.** In (1/3) gt^ij d_j d_k beta^k the terms with j = k are `Dxx`
  (`ddbeta_ddu(a,a,c)`, line 348). At the corner d_t Gam^i = -gt s2max (3 + 1/3)
  beta^i/dx^2: the squared speed of the corner mode is (10/9) mu gt, not mu gt. Track
  A's matrix (its `vonneumann.py`, `shift_eigs`) takes the product of first derivatives
  for all j, k, and so did mine, which I had built on its structure: **my statement of
  entry 1, "I agree with Track A's analysis in all its numbers", stands for its model
  and not for the code.** With the code's stencils (exploration, the corrected script,
  to be registered as T0d): shift 0.6580 cells on level 4 (Track A: 0.685), 0.6252 on
  the 64-cell root (0.65), 0.7276 without dissipation and damping, which is the corner
  estimate 2 sqrt(2)/sqrt(mu (3 + 1/3) s2max) that Track A wrote in its journal before
  its scan and then dropped. The 6 x 6 matrix with the corrected diagonal gives the
  same numbers as the split (0.6580, 0.6252).
- The lapse pair has no such term (sum_d Dxx alpha only): unchanged.

Not yet shown by a run of the code for the shift: the cases S of the aborted run (0.470
stable, 0.540 unstable) agree with both models (old bound 0.505, new 0.487). The complete
T2 below brackets each bound at 3 per cent, which tells them apart.

Runs stopped by me at 05:55 because they used the kernel with the two wrong pairs:
core-20261124-134427-7d49d39 (T4 R0g, 28 cycles, bounds at start 0.682, 0.563, 0.770
cells), core-20261124-134447-65c29bc (T6a, five of twelve set-ups run, no comparison
made), core-20261124-135223-d55b3d8 (T1/T2, three cases). No result is taken from them.

Kernel and Python twin changed alike: shift Omega^2 = mu s2max (sum_d G_d/dx_d^2 + (1/3)
max_d G_d/dx_d^2); third pair (4/3) alpha^2 chi (alpha^2 chi with `use_z4c = false`).
`vonneumann_gauge.py` keeps Track A's model as `--graddiv product --light scalar` and
reports its thresholds beside the code's.

### Predictions of T0d and of the complete T1/T2, written before they run

- P0j (T0d). Track A's thresholds are reproduced by its model (column "A-model") to its
  grid step, as in T0; with the code's stencils the shift is 0.658 (level 4), 0.625
  (root); the third pair 0.554 in flat space with diss 0.5 and 1.13 on level 4 of the card
  deck. Reduced/full for rk4, nghost 4: zero shift 0.99 to 1.00 as before, with a shift
  at most 1.10 (the same structure; I have not recomputed the survey).
- P1'. The three bounds of the start-up line agree with the reduced model to 1e-5 cells
  in all six groups.
- P2'. Bounds b in cells: S 0.4873 (shift), L 0.4679 (lapse), C 0.5510 and H 0.5510
  (conformal factor and Theta; the lapse pair of H is at 0.617), K 0.2785 (relaxation),
  D 0.4679. In every group: 0.93 b and 0.97 b stable, 1.03 b and 1.07 b unstable, 1.07 b
  with dt_gauge = 0.9 stable; D unstable at cfl 1.0 without the option, stable with it.
  S at 1.03 b = 0.502 is below the old bound 0.505 and C, H at 1.03 b = 0.568 below the
  old 0.617: these three cases would be stable if the old model were right. Least sure:
  K (one-sided relaxation) and the 0.97 b cases (3 per cent below a bound that the
  reduced model places 0 to 0.5 per cent below the full scan's).

## Entry 7 (06:10): outcome of T0c and T0d

T0c, run core-20261124-133245-4c89e4f (third version of the advection, still Track A's
model of the shift and a scalar wave for light): the registered numbers are those of the
recomputation (rk4, nghost 4: zero shift 0.9933 to 1.0000; with a shift 0.818 to 1.099,
at most 0.980 for dampings up to 1.5/dx). Figures looked at: `fig_reduced.png` readable
with the legend above the points.

T0d, run core-20261124-140153-9024b06 (commit 476fe0c; second derivatives as the code
takes them; 1536 survey cases; figures looked at: `fig_vonneumann.png`, the four markers
of the reduced model sit on the thresholds in both panels; `fig_reduced.png`, the corner
eigenvalues at threshold lie on the boundary of the RK4 region and the survey points of
all schemes lie between 0.82 and 1.26).

P0j held:

| Case (mu 0.75, eta 2, diss 0.5, alpha 1.06, chi 0.12; rk4, nghost 4) | code's stencils: scan / reduced | Track A's model (my scan) | Track A |
|---|---|---|---|
| shift, level 4 (dx 0.0195) | 0.6580 / 0.6557 | 0.6829 | 0.685 |
| shift, root (dx 0.3125) | 0.6252 / 0.6243 | 0.6485 | 0.65 |
| shift without dissipation, level 4 / root | 0.7303 / 0.7560 | 0.7699 / 0.7978 | 0.77 to 0.80 |
| shift, shift_Gamma 0.3, level 4 / root | 0.9053 / 0.8647 | 0.9397 / 0.8978 | 0.94 / 0.90 |
| lapse with lapse_leak 20, level 4 / root | 0.9670 / 0.4040 | the same | 0.97 / 0.405 |
| conformal factor and Theta, level 4 | 1.1290 / 1.1277 | 1.2420 (scalar wave) | stable to 1.2 |

Flat space (alpha = chi = 1), cells, scan (reduced), diss 0 / 0.1 / 0.5: lapse 1+log 0.4697 /
0.4825 / 0.4681 (0.4679); conformal factor and Theta 0.5752 / 0.5931 / 0.5537 (0.5510);
Gamma-driver 0.75: 0.7276 / 0.7531 / 0.6604 (0.6568); Gamma-driver 1.0: 0.6301 / 0.6507 /
0.5942 (0.5917). The mode that fails first is the corner in every case. The 6 x 6 matrix
with the corrected diagonal equals the split (0.6580, 0.6252). lapse_leak x dt: 2.525 at
the grid scale of the root mesh, 2.785 without structure (unchanged).

Reduced/full over the survey: rk4 nghost 4: zero shift 0.9933 to 1.0000, with a shift
0.818 to 1.068 (at most 0.972 for dampings up to 1.5/dx); rk4 nghost 3: 0.993 to 1.003
and up to 1.14 with a shift; rk4 nghost 2: up to 1.115 and 1.26; rk3: zero shift 0.959 to
1.000 (nghost 4, 3), 1.094 (nghost 2), with a shift up to 1.17. My "at most 1.10" for
rk4, nghost 4 held (1.068).

What Track A's deck was doing, with the corrected bound: the level-4 step of card job
4799 passed 0.658 cells earlier than the 0.685 of its analysis (its own figure puts
0.685 at t = 1.70); its remedy cfl_number 0.5 keeps 24 per cent of margin on level 4
and 20 per cent on the root mesh; the rule of decision 0027 (0.6) keeps 9 and 4 per
cent in the expanding box, and none in flat space with 1+log (0.47) or with a frozen or
harmonic lapse (0.55).

## Entry 8 (06:35): outcome of T1/T2 and of T6a; Track A's message; the K group

**T1/T2**, run core-20261124-140144-47691db (commit 476fe0c, serial build, 27 cases,
`flat_summary.json`; figure `fig_flat.png` looked at: six panels, in five of them the
curves at 0.93 b, 0.97 b and with dt_gauge fall together and the curves at 1.03 b and
1.07 b rise by more than ten decades; the left axis label is clipped at its top).

- P1' held: the bounds of the start-up line minus the reduced model are at most 2.4e-6
  cells in all six groups (six digits are printed).
- P2' held in S, L, C, H, D; failed in K:

| Group (binding pair) | b (cells) | 0.93 b | 0.97 b | 1.03 b | 1.07 b | 1.07 b, dt_gauge 0.9 |
|---|---|---|---|---|---|---|
| S Gamma-driver 1.5, lapse frozen (shift) | 0.4873 | stable | stable | guard, 194 records | guard, 88 | stable at 0.439 |
| L 1+log, zero shift (lapse) | 0.4679 | stable | stable | guard, 151 | guard, 66 | stable at 0.421 |
| C lapse frozen, zero shift (chi and Theta) | 0.5510 | stable | stable | guard, 211 | guard, 86 | stable at 0.496 |
| H harmonic lapse, zero shift (chi and Theta) | 0.5510 | stable | stable | grows 4e18 in C^2, saturates | guard, 84 | stable at 0.496 |
| K 1+log with lapse_leak 32 (relaxation) | 0.2785 | stable | stable | **stable** | **stable** | stable |
| D the deck, cfl 1.0 | 0.4679 | | | | guard after 10 records (no limit) | stable at 0.421 |

  "Stable" in S, L, H, K, D: the squared monitor never exceeds its first value and ends
  near 4e-18. In C (frozen lapse) the monitor rises to 12 to 13 times its start within
  the first records and stays there at all three stable step sizes alike: a plateau, not
  growth (this is what I read as marginal growth in entry 6; the bracket, not that
  reading, is the evidence for the bound).
  The three discriminating cases behaved as the corrected model says and against the old
  one: S at 0.502 cells (old bound 0.505) is unstable; C and H at 0.568 (old bound 0.617)
  are unstable. **The bounds of the shift, the 1+log lapse and the pair of conformal
  factor and Theta are bracketed by the code to 3 per cent.**
- Warnings: printed in every p and b case and in D without the option, in no m or a
  case; the relaxation line in K_p and K_b. As predicted.
- **K failed as a test, and why** [VERIFIED from the step history of K_g and the logs]:
  with dt_gauge the step is 0.2507 cells for the first 18 records (lapse bound 0.2785
  with the relaxation counted where alpha >= alpha_ref) and then returns to cfl x dx =
  0.298: after that no cell has its lapse at or above the reference, the relaxation is
  off, and nothing is stiff. In flat space the 1+log lapse settles at or below
  `lapse_leak_alpha`, so the group cannot test the relaxation bound. The test of that
  bound is the relaxed lapse in an expanding box, where the lapse stays above its
  reference: Track A's U0 (its runs: jump at t = 3.18, guard stop) against U0g (T3).

**T6a**, run core-20261124-140705-57ba7ce: `REGRESSION PASS`, twelve set-ups, 75 of 75
items byte-identical with release core-v0.6 (`.work/build_cpu_v06`), no item of class a,
b or other; no line of the step limit in any of the twelve logs of the new executable
(their cfl_number is 0.25 where Z4c runs). P6a held. The executable is the serial build
of source commit 476fe0c, the one to be published.

**Track A's message** `20261124T133506Z__to-core__refined-mesh-cfl05-result.md` (read
06:33): its refined deck at cfl_number 0.5 ran to t = 140 without a guard stop (P0L, run
A-20261122-235305-4ea0aa5, 14596 steps, 0.189 card-seconds per step; level-4 step at
most 0.5000 cells; H_max 0.018, 0.011, 0.0078 at t = 2, 3, 5; gt^xx <= 1.042). That is the
"R1" of my card list, done by Track A with the release executable; I use it as the
reference for R0g. Decks of the other tracks with cfl_number >= 0.5 on their branch
tips: 13 (D 4, B 4, C 5), none with a `<z4c>` block [VERIFIED by `git grep`]; Track A's
ball decks run 0.25. So Track A's periodic deck was the only one above a bound.

## Entry 9 (15:28 to 15:45, second session, batch 13): state found, predictions of T3 and T4 restated for the corrected kernel

The first session ended at the usage limit at 06:34. Found: branch `core/step-limit`,
worktree clean but for the staged end of run core-20261124-143230-8e3ac3d (committed);
`main` merged (queue cap of decision 0033, shared card queue). The source under
`athenak/`, `scripts/`, `problems/` is unchanged since commit 476fe0c, from which the
three builds `.work/build_{cpu,omp,gpu}_sl` were made (sha256 be2a1a7b..., 4cea2bbb...,
4b336bbe...). Three runs died with the session and give no result:
core-20261124-140133-476fe0c (T4 R0g on processors, 85 cycles to t = 0.505, only the
restart file of t = 0), core-20261124-142735-0dbdf83 (T3 G0, 19 cycles to t = 1.97),
core-20261124-143230-8e3ac3d (T3 U0w ran its one step; U0g killed at once). Done and on
record: T0 to T0d, T1/T2, T6a (entries 1 to 8). Open: T3, T4, T5, T6b, the card run, the
tests section of the interface text, READY, the message to Track A; then the second item.

Seen already in the logs of the dead runs (so not blind): the start-up lines of the
uniform deck. G0: warning for the Gamma-driver shift, bounds 0.624 (shift), 1.857
(lapse, frozen), 0.549 (light) cells of 0.3125, "cfl_number at or below 0.562". U0w: the
same for the lapse (bound 0.384 cells) and the relaxation line (6.25 against 2.40).

Predictions of entry 3 restated with the corrected bounds, before the runs:

- P3a'. G0 (lapse frozen, no dt_gauge): the step reaches one cell; the cell-to-cell
  alternation of beta^x on the line grows by more than 1e4; onset between t = 7 and 9
  (Track A: 8.1). Unchanged but for the bound in the warning (0.624, seen).
- P3b'. G0g (dt_gauge = 0.9): the step stops near 0.9 x 0.624 = 0.562 cells (it follows
  gt^dd, so a few per cent of drift is allowed); no onset to t = 12; the alternation of
  beta^x stays below 1e-6. Refuted by an onset or a growing alternation.
- P3c'. U0 (relaxed lapse, no dt_gauge): jump near t = 3.2 and a guard stop before t = 12
  (Track A: 3.18 and 10.76).
- P3d'. U0g (dt_gauge = 0.9): the lapse pair with the relaxation sets the step, 0.9 x
  0.384 = 0.35 cells at the start and less once the lapse stands above its reference;
  runs to t = 12 without guard stop and without the jump. Two to one, as before.
- P4b'. R0g (refined deck, cfl_number 1.0, dt_gauge = 0.9, processors, to t = 3.0): the
  level-4 step never exceeds 0.9 x 0.656 = 0.590 cells (start-up line of the dead run:
  shift 0.656, lapse 0.563, light 0.695 cells, so the lapse holds the step first, at
  0.507 cells, and the shift later); the message "set by dt_gauge" appears before
  t = 1.8; no jump: H_max at t = 2 and 3 within a factor 3 of Track A's run at cfl 0.5
  (0.018 and 0.011), where job 4799 jumped by more than a hundred between t = 2.3 and
  2.7. Refuted by a jump or a guard stop.

Cores: R0g on 3 threads, G0 and G0g one after the other on 1, U0 and U0g on 1 (6 per
session; the first session's 14 to 21 s per cycle were measured at a load of 25 to 33).
The card job (R0, R0g, R1 of `card_refined.list`, the smoke run of the card build) goes
into the shared queue; its results are not waited for.
