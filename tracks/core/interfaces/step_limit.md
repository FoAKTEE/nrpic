# Step limit of Z4c and the gauge speeds: `<z4c> dt_gauge`

Owner core. Branch `core/step-limit` (batch 11, 2026-11-24; source on top of release
core-v0.6). Answers request W31 of `REQUESTS_WAVE3.md` (Track A,
`periodic-gamma-driver-step`; decision 0027 item 2). Evidence and every number:
`tracks/core/JOURNAL-step-limit.md` (predictions before, outcomes after, run ids);
scripts, inputs and figures: `tracks/core/analysis/step_limit/`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_step-limit/` (READY there says what is tested).

In one paragraph: the released step limit counts the cell size and, with `dt_lightspeed`,
the coordinate speed of light. The gauge has speeds of its own that do not fall with the
conformal factor, and the lapse relaxation `lapse_leak` is stiff on coarse cells. With
`<z4c> dt_gauge = f` the step is kept, every cycle, at or below f times the stability
bound of the Runge-Kutta scheme for three pairs of fields (Gamma-driver shift, lapse with
its relaxation, light), evaluated in every cell from the fields with the code's stencils
and dissipation. It bounds the step itself, at any `cfl_number`, and does nothing where
the step is already smaller. Without the option nothing changes in any output file; at
start-up a warning is printed if `cfl_number` and the gauge allow a step above the bound.

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
| light | the pair gt_ij, At_ij | alpha sqrt(chi gt^dd) |

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
- The lapse pair is closed in its principal part. The shift pair is fed by Khat and
  Theta, and in the full system Theta is fed by Gam and the metric by d beta: the model
  treats the pair as closed [JUDGEMENT; tested by the runs of section 6].

## 3. Stability bound of the scheme

Space (`utils/finite_diff.hpp`): centred first derivative with symbol i s1(theta)/dx,
second derivative -s2(theta)/dx^2, mixed derivative the product of two first ones,
Kreiss-Oliger term -`diss` sin^(2 ng)(theta/2)/dx per direction (`z4c.cpp` 177), advective
derivative with a complex symbol L(theta)/dx that is real and negative at theta = pi.
Time: the two-register schemes of `driver.cpp`, whose stability polynomial is the Taylor
polynomial of their order (rk2, rk3, rk4: computed from the coefficients, difference 0.0).

A pair (u, v) with dampings e1, e2 and squared frequency Omega^2 has

    lambda = L - (D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2),
    Omega^2 = sum_d c_d^2 s2(theta_d)/dx_d^2,   D = diss sum_d sin^(2 ng)(theta_d/2)/dx_d

and the step is stable when lambda dt lies in the stability region of the scheme for
every theta. Facts of the scan of the whole Brillouin zone (run
core-20261124-133245-4c89e4f, `analysis/step_limit/vonneumann_gauge.py`):

- The mode that fails first is the corner theta = (pi, pi, pi) in every case without a
  background shift. There s1 = 0: the grad-div term of the shift drops out and all three
  shift modes have the transverse speed. So the bound of the shift is set by
  sqrt(mu gt^dd), not by the longitudinal speed.
- Pure oscillation, RK4: |lambda| dt <= 2 sqrt(2), i.e. dt/dx <= 2 sqrt(2)/sqrt(3 s2(pi)) / c
  = **0.664/c** for nghost 4 (s2(pi) = 272/45; 0.707/c for nghost 3, 0.816/c for nghost 2).
- Dissipation moves lambda to the left. A little helps, more hurts (RK4 region):

  | flat space, rk4, nghost 4 (cells) | diss 0 | diss 0.1 | diss 0.5 |
  |---|---|---|---|
  | lapse, 1+log (c = sqrt 2) | 0.470 | 0.483 | 0.468 |
  | light (c = 1) | 0.664 | 0.687 | 0.618 |
  | Gamma-driver, `shift_Gamma` 0.75 | 0.767 | 0.794 | 0.686 |
  | Gamma-driver, `shift_Gamma` 1.0 | 0.664 | 0.687 | 0.618 |

- A relaxation rate delta adds the bound rho(0)/delta of the mode without spatial
  structure (rho(0) = 2.785 for rk4, 2.513 for rk3) and lowers the corner's:
  `lapse_leak` x dt <= 2.52 at the grid scale of Track A's 64-cell root mesh.

**Track A's analysis repeated** (its `periodic_diag/scripts/vonneumann.py`, run
A-20261121-212800-d7f31a4; mine bisected / read on its grid of 0.0025 / Track A):

| Case (mu 0.75, eta 2, diss 0.5, alpha 1.06, chi 0.12) | mine | on its grid | Track A |
|---|---|---|---|
| shift, level 4 (dx 0.0195) | 0.6829 | 0.685 | 0.685 |
| shift, 64-cell root (dx 0.3125) | 0.6485 | 0.65 | 0.65 |
| shift without dissipation, level 4 / root | 0.7699 / 0.7978 | 0.77 / 0.80 | 0.77 to 0.80 |
| lapse with `lapse_leak` 20, level 4 / root | 0.9670 / 0.4040 | 0.9675 / 0.405 | 0.97 / 0.405 |
| light, level 4 | 1.2420 | 1.2425 | stable to 1.2 (end of its range) |
| shift, `shift_Gamma` 0.3, level 4 / root | 0.9397 / 0.8978 | 0.94 / 0.90 | 0.94 / 0.90 |

I agree with Track A in every number. What I add: (i) the bound belongs to the transverse
speed (above), so "0.685 dx/v_long" must not be carried to another `shift_Gamma`; (ii) in
flat space the 1+log lapse binds first, at 0.47 cells: the rule of decision 0027,
`cfl_number` at or below 0.6 with a Gamma-driver, is right in the expanding box (lapse
speed about 0.5) and too weak for asymptotically flat set-ups, where the bound is 0.47
with or without the shift; (iii) a background shift lowers the bounds (below).

## 4. The option

`<z4c> dt_gauge = f` (real, default 0 = off; read only if present, an absent option adds
nothing to the parameter dump). Needs `<time> integrator = rk3` or `rk4` (fatal otherwise)
and a three-dimensional mesh. Every cycle `Z4c::GaugeTimeStep` (`z4c/z4c_newdt_gauge.cpp`)
evaluates in every cell, for each of the three pairs, the eigenvalue of the corner mode

    lambda = -(D + (e1 + e2)/2) +- sqrt(((e1 - e2)/2)^2 - Omega^2) + i limag sum_d |beta^d|/dx_d,
    Omega^2 = s2(pi) c0^2 sum_d G_d/dx_d^2,  G_d = gt^dd + sum_(j != d) |gt^dj|,
    D = diss sum_d 1/dx_d,  e = (eta or delta) + (advection factor) aadv sum_d |beta^d|/dx_d

with c0^2 = mu (shift), f alpha chi (lapse), alpha^2 chi (light); aadv = |L(pi)| = 32/15,
8/3, 4 and limag = max Im L = 1.950, 1.951, 2.202 for nghost 4, 3, 2. The largest stable
step of the pair is rho(phi)/|lambda|, with rho the first-exit radius of the stability
region along the ray of lambda (a table of 129 angles made once from the stability
polynomial), and at most rho(0)/(eta or delta) for the mode without structure. The step
of the run is then at most f times the smallest of these over cells and pairs: `dtnew`
is set to min(dtnew, f x bound/`cfl_number`), so the bound holds for the step itself.
Cells whose conformal factor is not positive or whose fields are not finite are skipped.

How good the reduced bound is, against the scan of the whole Brillouin zone (1536 cases:
rk3 and rk4, nghost 2 to 4, diss 0 to 1, damping 0 to 6/dx, |beta| 0 to 1; run
core-20261124-133245-4c89e4f, `fig_reduced.png`); ratio reduced/full, above 1 means the
reduced bound allows too large a step:

| Scheme | zero shift | with a shift |
|---|---|---|
| rk4, nghost 4 (the scheme of every Z4c input of `problems/`) | 0.993 to 1.000 | 0.818 to 1.099; at most 0.980 for dampings up to 1.5/dx |
| rk4, nghost 3 | 0.993 to 1.016 | 0.819 to 1.185 |
| rk4, nghost 2 | 0.992 to 1.122 | 0.823 to 1.313 |
| rk3, nghost 4 / 3 / 2 | 0.966 to 1.009 / 0.964 to 1.000 / 0.959 to 1.122 | up to 1.130 / 1.110 / 1.245 |

The excess above 1 occurs only with a damping of 6/dx (the size of `lapse_leak` = 20 on
cells of 0.31) together with |beta| >= 0.3, or with nghost 2 or 3 and diss = 1 at that
damping. **Use f = 0.9** with rk4 and nghost 4; 0.75 with nghost 2 or 3 or rk3 if the
shift is of order one and the damping strong. f above 1 is accepted with a warning.

Not counted [JUDGEMENT, none of them binds in the tests]: the constraint damping
(`damp_kappa1`, rates of order kappa1 alpha, bound dt of order 2.8/((2 + kappa2) kappa1));
`shift_H`; the slow-start term; the drift control; the matter; variable coefficients and
nonlinear terms (the bound is that of the linearized, frozen problem: hence f < 1).

Messages (rank 0). With the option, once at start-up:

    Z4c step limit: dt_gauge = 0.9 keeps the step at or below that fraction of the stability
    bound of rk4 (nghost 4, diss 0.5); at the start, in units of the smallest cell 0.3125:
    Gamma-driver shift 0.647066, lapse 0.467928, light 0.616644; cfl_number 1

and one line the first time each sector sets the step ("at time ... the step of Z4c is set
by dt_gauge, sector ..."). Without the option the bound is evaluated once at start-up
and a warning is printed if a sector can be exceeded: the gauge sectors are judged at
`cfl_number` x (smallest cell), the step the other limits allow at most; light at the
present step when `dt_lightspeed` is set (that limit keeps the step a fixed fraction of
dx/c). A second line is printed when `lapse_leak` x that step exceeds 1 and the step is
beyond the bound of the lapse pair with the relaxation counted in every cell. The
warning costs one pass over the cells at start-up and changes no output file.
