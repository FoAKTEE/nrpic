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
