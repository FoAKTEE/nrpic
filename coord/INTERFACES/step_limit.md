# Step limit of Z4c and the gauge speeds: `<z4c> dt_gauge`

Owner core. Branch `core/step-limit` (batches 11 and 13, 2026-11-24; source of the step
limit: commit 476fe0c on top of release core-v0.6; the published executables are built
from 5c4b644f, which adds the second item of the package, `preempted_runs.md`, and no
change to `z4c/`). Answers request W31 of `REQUESTS_WAVE3.md` (Track A,
`periodic-gamma-driver-step`; decision 0027 item 2). Evidence and every number:
`tracks/core/JOURNAL-step-limit.md` (predictions before, outcomes after, run ids);
scripts, inputs, how to rerun: `tracks/core/analysis/step_limit/README.md`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_step-limit/` (READY there says what is tested).

In one paragraph: the released step limit counts the cell size and, with `dt_lightspeed`,
the coordinate speed of light. The gauge has speeds of its own that do not fall with the
conformal factor, and the lapse relaxation `lapse_leak` is stiff on coarse cells. With
`<z4c> dt_gauge = f` the step is kept, every cycle, at or below f times the stability
bound of the Runge-Kutta scheme for three pairs of fields (Gamma-driver shift; lapse with
its relaxation; conformal factor and Theta, the fastest pair of the rest), evaluated in
every cell from the fields with the code's stencils and dissipation. It bounds the step
itself, at any `cfl_number`, and does nothing where the step is already smaller. Without
the option no output file changes (byte regression against core-v0.6: section 6); at
start-up a warning is printed if `cfl_number` and the gauge allow a step above the bound.
The bounds are bracketed at 3 per cent by runs of the code (section 6). They are lower
than Track A's analysis said: 0.658 cells instead of 0.685 for its Gamma-driver on the
finest level, and in flat space 0.47 for the 1+log lapse and 0.55 for the rest.

## 1. What the released code does [VERIFIED from the source]

`Z4c::NewTimeStep` (`z4c/z4c_newdt.cpp`) sets `dtnew` to the smallest cell size, and with
`<z4c> dt_lightspeed = f_c` to the smaller of that and f_c dx_d/c_d, c_d = alpha
sqrt(chi gt^dd) + |beta^d|. `Mesh::NewTimeStep` (`mesh/mesh.cpp` 615-689) takes
dt = min(2 dt_old, `cfl_number` x dtnew, the particles' limit). One step for all levels.
With `cfl_number = 1.0` and `dt_lightspeed = 0.25` (Track A's periodic deck) the step is
min(dx, 0.25 dx/c) on the finest level and grows to one cell once the coordinate speed of
light has fallen below 0.25, whatever the gauge speeds are.

## 2. Speeds of the gauge sectors as the code evolves them [derivation from `z4c_calcrhs.cpp` 587-596, 629, 658, 696-738 and `z4c_gauge_ext.hpp`]

Frozen coefficients about a slice with lapse alpha, conformal factor chi (chi = psi^-4,
gamma^ij = chi gt^ij), inverse conformal metric gt^ij, shift beta^i; principal parts:

| Sector | Equations | Coordinate speed along x^d (plus the shift) |
|---|---|---|
| lapse | d_t alpha = -f alpha Khat + la beta.d alpha - delta alpha; d_t Khat = -chi gt^ij d_i d_j alpha + beta.d Khat | sqrt(f alpha chi gt^dd); 1+log (f = 2): **sqrt(2 alpha chi gt^dd)** |
| shift | d_t beta^i = mu Gam^i - eta beta^i + sa beta.d beta^i; d_t Gam^i = gt^jk d_j d_k beta^i + (1/3) gt^ij d_j d_k beta^k + beta.d Gam^i | longitudinal **sqrt((4/3) mu gt^dd)**, transverse **sqrt(mu gt^dd)** |
| light | metric and At; conformal factor, Theta and Gam | alpha sqrt(chi gt^dd) |

f = `lapse_oplog` x `lapse_harmonicf` + `lapse_harmonic` x alpha + `lapse_volume`/sqrt(chi)
(+ `lapse_kdriver` x alpha_ref); mu = `shift_Gamma` + alpha^2 `shift_alpha2Gamma`;
eta = `shift_eta` (times the profile of `shift_eta_profile`); la = `lapse_advect`,
sa = `shift_advect`; delta = `lapse_leak` (1 + ln(alpha/`lapse_leak_alpha`)) where the
lapse is at or above its reference, else 0 (the relaxation linearized; it has no
derivative and changes no speed).

- The shift speeds carry neither alpha nor chi (with `shift_alpha2Gamma` they carry
  alpha). In an expanding box, where the speed of light alpha sqrt(chi) falls like the
  inverse scale factor, they stay: sqrt(4 mu/3) = 1 for `shift_Gamma = 0.75`.
- The 1+log lapse moves with sqrt(2/alpha) times the speed of light: in flat space
  (alpha = chi = 1) with sqrt(2), faster than light and than the shift.
- The lapse pair is closed in its principal part and feeds the others; the shift pair is
  fed by Khat and Theta. At the corner of the Brillouin zone, where the bound is set
  (section 3), first derivatives vanish and the three pairs decouple.

## 3. Stability bound of the scheme

Space (`utils/finite_diff.hpp`): centred first derivative with symbol i s1(theta)/dx;
second derivative d_a d_a with the stencil `Dxx`, symbol -s2(theta)/dx^2; mixed derivative
d_a d_b (a != b) the product of two first ones (`Dxy`); Kreiss-Oliger term
-`diss` sin^(2 ng)(theta/2)/dx per direction (`z4c.cpp` 177); advective derivative with a
complex symbol L(theta)/dx that is real and negative at theta = pi. Time: the
two-register schemes of `driver.cpp`, whose stability polynomial is the Taylor polynomial
of their order (rk2, rk3, rk4: computed from the coefficients, difference 0.0).

A pair (u, v) with dampings e1, e2 and squared frequency Omega^2 has

    lambda = L - (D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2)

and the step is stable when lambda dt lies in the stability region of the scheme for
every theta. The mode that fails first is the corner theta = (pi, pi, pi) in every case
scanned without a background shift. There s1 = 0 and s2 = s2max (4, 16/3, 272/45 for
nghost 2, 3, 4), and what matters is **which stencil each second derivative uses**
[VERIFIED, `z4c_calcrhs.cpp` 334-362]:

- Lapse: d_t Khat = -chi sum_d Dxx alpha. Omega^2 = f alpha chi s2max sum_d gt^dd/dx_d^2.
- Shift: in (1/3) gt^ij d_j d_k beta^k the terms j = k are `Dxx`. At the corner
  d_t Gam^i = -s2max (sum_d gt^dd/dx_d^2 + (1/3) gt^ii/dx_i^2) beta^i: the squared speed
  of the corner mode is **(10/9) mu gt**, between the transverse and the longitudinal.
- Conformal factor and Theta: d_t Theta = alpha sum_d Dxx chi + (alpha chi/2) d_k Gam^k,
  d_t chi = (4/3) chi alpha Theta, d_t Gam^k = -(2/3) alpha d_k Theta. In the continuum
  the three give the speed of light; at the corner the terms in Gam vanish and
  Omega^2 = **(4/3) alpha^2 chi** s2max sum_d gt^dd/dx_d^2. The pair is there whatever
  the lapse condition is (not with `use_z4c = false`). Metric and At: alpha^2 chi.

Pure oscillation with RK4 is stable for |lambda| dt <= 2 sqrt(2), i.e.
dt/dx <= 2 sqrt(2)/sqrt(3 s2max)/c = **0.664/c** for nghost 4 (0.707/c, 0.816/c for nghost
3, 2), c the speed of the corner mode. Dissipation moves lambda to the left: a little
helps, more hurts. A relaxation rate delta adds the bound rho(0)/delta of the mode
without spatial structure (rho(0) = 2.785 for rk4, 2.513 for rk3) and lowers the
corner's: `lapse_leak` x dt <= 2.52 at the grid scale of Track A's 64-cell root mesh.

Bounds in cells, rk4, nghost 4, flat space (alpha = chi = 1), from the scan of the whole
Brillouin zone (run core-20261124-140153-9024b06):

| | diss 0 | diss 0.1 | diss 0.5 |
|---|---|---|---|
| lapse, 1+log | 0.470 | 0.483 | 0.468 |
| conformal factor and Theta | 0.575 | 0.593 | 0.554 |
| Gamma-driver, `shift_Gamma` 1.0 | 0.630 | 0.651 | 0.594 |
| Gamma-driver, `shift_Gamma` 0.75 | 0.728 | 0.753 | 0.660 |

**Track A's analysis repeated** (its `periodic_diag/scripts/vonneumann.py`, run
A-20261121-212800-d7f31a4: mu 0.75, eta 2, diss 0.5, alpha 1.06, chi 0.12):

| Case | code's stencils (scan) | Track A's model (my scan) | Track A |
|---|---|---|---|
| shift, level 4 (dx 0.0195) | **0.658** | 0.6829 | 0.685 |
| shift, 64-cell root (dx 0.3125) | **0.625** | 0.6485 | 0.65 |
| shift without dissipation, level 4 / root | 0.730 / 0.756 | 0.7699 / 0.7978 | 0.77 to 0.80 |
| shift, `shift_Gamma` 0.3, level 4 / root | 0.905 / 0.865 | 0.9397 / 0.8978 | 0.94 / 0.90 |
| lapse with `lapse_leak` 20, level 4 / root | 0.967 / 0.404 | the same | 0.97 / 0.405 |
| conformal factor and Theta, level 4 | 1.129 | 1.242 (scalar wave) | stable to 1.2 |

Where I agree with Track A: the cause (the Gamma-driver's speed does not fall with the
conformal factor, the released limit counts light only), the lapse numbers, the stiff
relaxation and its bound, and every number of its model, which my scan reproduces to its
grid step. Where I do not: its matrix takes the product of two first derivatives for
every term of d_j d_k beta^k, the code takes `Dxx` for j = k. With the code's stencils the
shift bound is 3.6 per cent lower (0.658, 0.625). The value without dissipation and
damping, 0.728, is the corner estimate 2 sqrt(2)/sqrt(mu (3 + 1/3) s2max) of Track A's own
journal. Two things its analysis did not have: the pair of conformal factor and Theta
at (4/3) of light, and the flat-space ranking, in which the 1+log lapse binds first.
Both models are in `vonneumann_gauge.py` (`--graddiv`, `--light`); the runs of the code
decide between them (section 6, T2).

Consequence for the rule of decision 0027 (`cfl_number` at or below 0.6 with a
Gamma-driver): it holds in Track A's expanding box with 4 per cent of margin on the root
mesh and 9 on level 4; it does not hold in flat space, where the bound is 0.47 with a
1+log lapse and 0.55 with a harmonic or frozen one, with or without a shift.

## 4. The option

`<z4c> dt_gauge = f` (real, default 0 = off; read only if present, an absent option adds
nothing to the parameter dump; to change it on the command line the input must declare
it). Needs `<time> integrator = rk3` or `rk4` (fatal otherwise) and a three-dimensional
mesh. Every cycle `Z4c::GaugeTimeStep` (`z4c/z4c_newdt_gauge.cpp`) evaluates in every
cell, for each of the three pairs, the eigenvalue of the corner mode

    lambda = -(D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2) + i limag sum_d |beta^d|/dx_d,
    D = diss sum_d 1/dx_d,  e = (eta or delta) + (advection factor) aadv sum_d |beta^d|/dx_d,
    Omega^2 = s2max c0^2 Q,  Q = sum_d G_d/dx_d^2,  G_d = gt^dd + sum_(j != d) |gt^dj|

with c0^2 Q = f alpha chi Q (lapse), mu (Q + (1/3) max_d G_d/dx_d^2) (shift),
(4/3) alpha^2 chi Q (conformal factor and Theta; alpha^2 chi Q with `use_z4c = false`);
aadv = |L(pi)| = 32/15, 8/3, 4 and limag = max Im L = 1.950, 1.951, 2.202 for nghost 4,
3, 2. The largest stable step of the pair is rho(phi)/|lambda|, with rho the first-exit
radius of the stability region along the ray of lambda (a table of 129 angles made once
from the stability polynomial), and at most rho(0)/(eta or delta) for the mode without
structure. The step of the run is then at most f times the smallest of these over cells
and pairs: `dtnew` is set to min(dtnew, f x bound/`cfl_number`), so the bound holds for
the step itself. Cells whose conformal factor is not positive or whose fields are not
finite are skipped. `python/` holds no twin; the twin of the kernel is
`analysis/step_limit/vonneumann_gauge.py` (`reduced_bound`), and the code's start-up
line agrees with it to the six digits printed (section 6, T1).

How good the reduced bound is, against the scan of the whole Brillouin zone (1536 cases:
rk3 and rk4, nghost 2 to 4, diss 0 to 1, damping 0 to 6/dx, |beta| 0 to 1; run
core-20261124-140153-9024b06, `fig_reduced.png`); ratio reduced/full, above 1 means the
reduced bound allows too large a step:

| Scheme | zero shift | with a shift |
|---|---|---|
| rk4, nghost 4 (every Z4c input of `problems/`) | 0.993 to 1.000 | 0.818 to 1.068; at most 0.972 for dampings up to 1.5/dx |
| rk4, nghost 3 | 0.993 to 1.003 | up to 1.14 |
| rk4, nghost 2 | 0.992 to 1.115 | up to 1.26 |
| rk3, nghost 4 / 3 / 2 | 0.966 to 1.000 / 0.964 to 1.000 / 0.959 to 1.094 | up to 1.12 / 1.11 / 1.17 |

With rk4 the excess above 1 occurs only with a damping of 6/dx (the size of `lapse_leak`
= 20 on cells of 0.31) together with a shift |beta| >= 0.3, or with nghost 2 at that
damping and diss = 1; with rk3 it occurs with a shift at any damping. **Use f = 0.9** with
rk4 and nghost 4; 0.75 with rk4 and nghost 2 or 3 if the damping is that strong and
there is a shift, and with rk3 whenever the shift is of order one. f above 1 is
accepted with a warning.

Not counted [JUDGEMENT, none binds in the tests]: the constraint damping (`damp_kappa1`:
rates of order kappa1 alpha, bound dt of order 2.8/((2 + kappa2) kappa1)); `shift_H`; the
slow-start term; the drift control; the matter and the particles; variable coefficients,
level boundaries and nonlinear terms (the bound is that of the linearized, frozen
problem: hence f < 1). With a background shift of order one the advection is treated by
its damping at the corner and its largest phase rate, which is careful by up to 18 per
cent.

Messages (rank 0). With the option, once at start-up:

    Z4c step limit: dt_gauge = 0.9 keeps the step at or below that fraction of the stability
    bound of rk4 (nghost 4, diss 0.5); at the start, in units of the smallest cell 0.3125:
    Gamma-driver shift 0.624306, lapse 0.467928, light 0.551001; cfl_number 1

("light" is the pair of conformal factor and Theta) and one line the first time each
sector sets the step ("at time ... the step of Z4c is set by dt_gauge, sector ...").
Without the option the bound is evaluated once at start-up and a warning is printed if
a sector can be exceeded: the gauge sectors are judged at `cfl_number` x (smallest cell),
the step the other limits allow at most; the third pair at the present step when
`dt_lightspeed` is set (that limit keeps the step a fixed fraction of dx/c). A second
line is printed when `lapse_leak` x that step exceeds 1 and the step is beyond the bound
of the lapse pair with the relaxation counted in every cell. The warning costs one pass
over the cells at start-up and changes no output file.

## 5. Option or default [JUDGEMENT on the evidence of section 6]

The limit stays an **option, off when absent**; the **warning at start-up is on for
everybody** (it prints to the log, changes no output file, and is the one change of this
item that acts without an option). Reasons:

- The released behaviour is a defect only for a run whose step can pass a bound, and
  the warning now says so at start-up, with the sector, the bound in cells and the
  largest `cfl_number` that stays below it. For such a run the result of the release
  was an instability (T2, T3), so nothing worth keeping is lost by switching the option
  on there.
- Every run that is below the bounds is unchanged either way: the three Z4c set-ups of
  the release regression give byte-identical histories with `dt_gauge = 1.0` and the
  limit never sets their step (T6b; their `cfl_number` is 0.25, their smallest bound
  0.48 cells). No deck on the tracks' branch tips other than Track A's periodic one has
  a `<z4c>` block with `cfl_number` at or above 0.5 (journal entry 8).
- What I have not shown is that the bound never binds below `cfl_number` 0.25 in the
  tracks' puncture and horizon runs, where the conformal metric is far from flat
  (gt^dd enters every bound) and the shift is of order one (there the reduced bound is
  careful by up to 18 per cent). A default that changed the step of such a run would
  change a chain between two segments when its executable is renewed, and the tracks'
  runs are compared byte for byte across restarts. So the default is left alone until a
  survey of the tracks' production decks with `dt_gauge = 1.0` has been run (proposed
  for the release after v0.7).

Recommended for new decks: `<z4c> dt_gauge = 0.9` in every deck that evolves a
Gamma-driver shift or a 1+log or relaxed lapse with `cfl_number` above 0.4, and in every
deck with `lapse_leak` on cells where `lapse_leak` x `cfl_number` x dx exceeds 1. The
rule of decision 0027 (`cfl_number` at or below 0.6 with a Gamma-driver) should read: at
or below the bound the warning prints, 0.56 on Track A's root mesh, **0.47 in flat space
with a 1+log lapse**; or `dt_gauge = 0.9`.

## 6. Tests (predictions before, outcomes after: the journal; every run registered)

| Test | What | Outcome | Run |
|---|---|---|---|
| T0 to T0d | reference computation: stencil symbols, stability polynomials of the driver's schemes, scan of the Brillouin zone, Track A's model beside the code's, the reduced bound of the kernel against the scan (1536 cases) | Track A's thresholds reproduced by its model to its grid step; with the code's stencils the shift bound is 3.6 per cent lower; table of section 3; reduced/full in section 4. Two versions of the advection term of the reduced bound were refuted on the way (entries 1, 2) | core-20261124-130414-c77ee7e, -132639-eb9be13, -133245-4c89e4f, -140153-9024b06 |
| T1 | bounds of the start-up line against the Python twin, six gauge settings | agree to 2.4e-6 cells | core-20261124-140144-47691db |
| T2 | flat space with noise 1e-10, one sector binding per group, `cfl_number` at 0.93, 0.97, 1.03, 1.07 of the bound b, and 1.07 b with `dt_gauge = 0.9`; 300 steps | Gamma-driver 1.5 (b = 0.487 cells), 1+log (0.468), frozen lapse and harmonic lapse (0.551, the pair of conformal factor and Theta): stable at 0.93 b and 0.97 b, guard stop or growth by 4e18 at 1.03 b and 1.07 b, stable with the option. The three cases that tell the code's stencils from Track A's model (shift at 0.502 cells, the third pair at 0.568) are unstable, as the code's stencils say. The group for the relaxation (`lapse_leak` 32) did not test it: in flat space the lapse settles below its reference and the relaxation is off | the same |
| T3 | Track A's uniform-mesh reproducer (64^3 cells of 0.3125, `cfl_number` 1.0, `dt_lightspeed` 0.25) without and with `dt_gauge = 0.9` | lapse frozen: onset of growth at t = 8.72 without (Track A 8.1; H_max from 0.0035 to 1.97, the step at one cell), none with (step 0.560 cells, H_max falls to 0.0012). Relaxed lapse (`lapse_leak` 20): onset at t = 3.18 and guard stop at t = 10.764 without (Track A 3.18, 10.76), t = 12 without either with (step 0.32 to 0.34 cells, set by the lapse pair from t = 0.51). This is also the test of the relaxation bound | core-20261124-233050-ae129ee, -233103-faf1f5b; analysis core-20261125-003000-0ad24cb |
| T4 | Track A's refined periodic deck (64^3 root, four static levels, finest cell 0.0195, P0L data) at `cfl_number` 1.0 with `dt_gauge = 0.9`, through the time at which card job 4799 failed (onset at t = 2.40), on processors to t = 3 | no onset, no guard stop; the level-4 step follows the light-speed limit to t = 1.18 and is then held at 0.57 cells by the shift's bound (0.631 cells then; 0.656 at the start); H_max at t = 2, 2.5, 3: 0.0181, 0.0150, 0.0106, within 5 per cent of Track A's run at `cfl_number` 0.5 (0.0190, 0.0143, 0.0108), where job 4799 without the option has 0.0171, 179, 203 | core-20261124-233029-c745838; analysis core-20261125-020445-10806d1; the same on a card, with the control and the run at 0.5: queued, q0036 |
| T5a | cost of evaluating the bound every cycle (32^3, serial, three repetitions) | 0.6 per cent (minima), 1.0 per cent (medians), inside the scatter of 10 per cent; histories identical | core-20261125-001339-5005deb |
| T6a | byte regression against release core-v0.6, twelve set-ups, option absent | PASS, 75 of 75 items identical; again with the final source (handler of the second item): PASS, 75 of 75 | core-20261124-140705-57ba7ce; core-20261125-000250-6dc7307 |
| T6b | east, os, c4 of the regression with `dt_gauge = 1.0` against the same without | histories byte-identical (3, 2, 3 files), the limit never sets the step, no warning without the option; bounds at the start in cells (shift, lapse, third pair): east 1.86, 0.89, 0.54; os 0.60, 0.48, 0.57; c4 1.86, 0.91, 0.55 | core-20261125-003008-668d147 |
| F1 | the deck `problems/tests/z4c_step_limit.athinput` (limit binding) with the serial build of 476fe0c and with the final serial build | 33 files, 216,474 bytes, byte-identical; lines of the step limit identical | core-20261125-003154-965cb92 |

Cost of the smaller step (T3): to t = 12 the run with `dt_gauge = 0.9` takes 77 steps
with the frozen lapse (the unstable run took 65) and 124 with the relaxed lapse. A fixed
`cfl_number` would need 84 steps at 0.5, 114 at 0.35, 131 at 0.3, 155 at 0.25 (estimated
from the step history of the run without the option, not run). So the option costs the
steps of the largest fixed `cfl_number` that is stable: 8 per cent fewer than the remedy
0.5 with the frozen lapse, 5 per cent fewer than 0.3 with the relaxed one.

Example: `problems/tests/z4c_step_limit.athinput` (`athena -i
problems/tests/z4c_step_limit.athinput`; with `z4c/dt_gauge=0.0` on the command line the
warning and the instability).

**T4, cost.** To t = 3 the refined deck takes 322 steps with `dt_gauge = 0.9`; Track
A's run at `cfl_number` 0.5 takes about 540 (0.5 halves the light-speed-limited step
too) and its unstable run at 1.0 about 296 (both estimated from their step histories).
Once the run at 0.5 has reached its cap the ratio per unit time tends to 0.5/0.571 =
0.88. The card job (R0 without the option, R0g with it to t = 6, R1 at 0.5, all with the
final card build) waits in the shared queue as q0036; it will be the first run of
`athena_gpu`.

## 7. Not tested, not counted

- A card run of the final build (q0036 will be the first), and the cost of the bound on
  a card.
- Punctures, horizons, excision, `shift_eta_profile`, `shift_alpha2Gamma`, `lapse_kdriver`,
  rk3, nghost 2 and 3 in runs of the code (the reference computation covers the last
  three; f = 0.75 is the advice there).
- Adaptive refinement: the bound is evaluated on every MeshBlock with its own cell size
  each cycle, so it follows the mesh; no run with refinement that changes.
- Several MPI ranks: the reduction is `MPI_Allreduce` of the minimum, as for the other
  limits; not run.
- The start-up line of a restarted run prints the bounds at the restart, not at t = 0.
- What the bound leaves out is listed at the end of section 4.

## 8. Lines touched in shared files

`athenak/src/z4c/z4c_newdt.cpp` (7 lines: the call of `GaugeTimeStep` after the
light-speed limit), `z4c/z4c.cpp` (4 lines: reading the option, the start-up check),
`z4c/z4c.hpp` (10 lines: three data members, two declarations; no function body),
`CMakeLists.txt` (one line). Everything else is in `z4c/z4c_newdt_gauge.cpp` (new, 413
lines). `scripts/cpu_run.sh` (two corrections of the first session: `wait ... || rc=$?`, so that
under `set -e` the footer of the log is written also when the executable returns a
non-zero status such as the guard's 3; the awk variable `load` renamed `ldavg`).
