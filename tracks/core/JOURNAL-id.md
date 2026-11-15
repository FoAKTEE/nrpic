# Journal of core, work package "id": initial data with extrinsic curvature

Branch `core/id-extrinsic`, worktree `wt/core-id`. Units G = c = 1. Sign: expansion has
K < 0. Labels: [VERIFIED] read or measured here (with locator or run id), [BACKGROUND]
standard result not re-derived here, [JUDGEMENT] inference or design, [TO VERIFY] open.
Run ids are `core-<date>-<time>-<commit7>`; manifests in `tracks/core/runs/`, outputs in
`scratch/core/<run_id>/` of the main checkout.

## 2026-11-15, entry 1: what was read, and the plan

Read: `CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; decision 0010;
`coord/INTERFACES/spherical_id_format2.md`; `coord/notes/derivations_to_check.md` items
1 and 2; brief lines 30-68, 84-137, 493-552, 688-706, 834-860; the source
`athenak/src/pgen/nrpic/nrpic_cf.cpp`, `nrpic_cosmo.cpp`, `athenak/src/z4c/z4c_adm.cpp`,
the gauge part of `z4c_calcrhs.cpp`, `z4c_newdt.cpp`, and of the particle module
`nrpic.cpp` (init, push, deposit driver) and `nrpic_io.cpp` (probe, history, constraint
statistics, field dumps, trajectories, snapshots).

Facts of the code that the design rests on [VERIFIED, file and line of this worktree]:

- `adm.alpha` and `adm.beta_u` are slices of the Z4c state when Z4c is on
  (`athenak/src/coordinates/adm.cpp:49-50`), so the problem generator sets the initial
  gauge by writing them; `ADMToZ4c` turns `adm.g_dd`, `adm.vK_dd` into chi, the conformal
  metric, Khat and A_ij with Theta = 0 (`z4c_adm.cpp:49-100`).
- `nrpic_cf.cpp:259-262` sets `beta_u = 0` and `vK_dd = 0` in every cell; the lapse
  choices are one, table, isotropic, precollapsed (`nrpic_cf.cpp:205-221`).
- The finite differences of the constraint monitor are centred, sixth order with four
  ghost cells (`athenak/src/utils/finite_diff.hpp:45-63`, stencil of seven points).
- The step is `cfl_number` times the smallest cell size, whatever the lapse
  (`z4c_newdt.cpp:46-58`): the coordinate speed of light does not enter.
- The 1+log family is `d_t alpha = lapse_advect beta^i d_i alpha - f alpha Khat` with
  `f = lapse_oplog lapse_harmonicf + lapse_harmonic alpha + lapse_volume chi^(-1/2)`,
  plus the driver `lapse_kdriver` (`z4c_calcrhs.cpp:687-701`); the shift is
  `d_t beta^i = shift_Gamma Gamma^i + shift_advect beta^j d_j beta^i - shift_eta beta^i`
  (`z4c_calcrhs.cpp:713-717`).
- Records usable for the comparison with the exact solution: the proper time of every
  particle (`IPTAU`, accumulated by the midpoint pusher, `nrpic.cpp:531`) is written in
  the snapshots (`nrpic_io.cpp:975-977`) and, for tracked particles, together with the
  metric reconstructed at the particle (`.trajmet.bin`, 17 doubles,
  `nrpic_io.cpp:810-814`); field dumps on a uniform mesh hold E, chi, H, M_i, Khat,
  Theta and the lapse (`nrpic_io.cpp:512-518`).

Derivation re-done for the reference generator (item 1 of
`coord/notes/derivations_to_check.md`; agreement, with one addition) [VERIFIED by the
symbolic check `tracks/core/analysis/id/check_derivation.py`, see entry 2]:

- Marginally bound dust, slice of constant dust proper time: flat 3-metric (psi = 1),
  alpha = 1, beta^i = -v n^i, v = sqrt(2 m(R)/R); K_ij = -d_(i v_j), so KT = -v/R,
  KL = -dv/dR = v/(2R) - 4 pi rho R / v. Homogeneous part: KL = KT = -H,
  H^2 = 8 pi rho/3. Vacuum: KT = -sqrt(2M/R^3), KL = +sqrt(2M/R^3)/2.
- Addition: KL jumps at a sharp dust surface (from -H to +H/2; KT is continuous with a
  kink). The momentum constraint has no surface term in the continuum, because the
  jump of KL enters only undifferentiated in spherical coordinates. On a Cartesian
  mesh the two differentiated terms that carry the jump cancel only on average over
  the surface cells [JUDGEMENT, tested in test 1].
- Exact evolution: a shell of initial areal radius R_0 with mass m inside has
  R(tau) = (R_0^(3/2) + (3/2) sqrt(2m) tau)^(2/3), tau the proper time of its dust; no
  shell crossing while the mean density inside decreases outwards.

Design decisions [JUDGEMENT]:

1. Format 2 is refined by one optional header line, `# breaks = r_1 r_2 ...`: radii at
   which the columns may be discontinuous (u: kink). The interpolation never uses rows
   from both sides of a break. Reason: the sharp dust surface (jump of KL) and Track D's
   bubble wall. A file without the line is read exactly as the provisional text says.
2. The format-1 code path is not touched: the existing kernel keeps setting psi, the
   metric, zero K and zero shift and the lapse choices; a second kernel, run only when a
   format-2 component is present, overwrites K_ij, and the lapse and shift when the
   input asks for the table. This is one hook in `NrpicConformallyFlat` plus new
   functions in the anonymous namespace of `nrpic_cf.cpp`.
3. Start options: `<problem> lapse = one | table | isotropic | precollapsed` (table of
   a format-2 component: its alpha column) and new `<problem> shift = zero | table`.
4. The reference generator (`python/nrpic/expanding_ball.py`) has a sharp surface and,
   as an option, a smooth edge of half-width w (the density falls with a quintic step
   over [R_b - w, R_b + w]); both are exact marginally bound Lemaitre-Tolman-Bondi
   data. Massless-like tracers (rest mass 1e-30 of the ball) at rest in the slice
   outside the ball follow the same formula with m = M and probe the exterior.

Order of work: regression baseline; Python format and generator with an offline check;
source; regression after; test 1 (start); test 2 (evolution, gauges); test 3 if time
allows; `docs/FORMATS.md`.

### Prediction R (regression of format 1), written before the run

Input `problems/tests/cf_table_regress.athinput` (Oppenheimer-Snyder table of format 1,
10395 lattice particles, one static refinement level, 12 steps, lapse from the table).
Prediction: the history files, the constraint statistics, the particle snapshot and
the restart files of the executable built after the change are byte-identical to
those of the executable built before it (processor build; the card build compared the
same way). Refuted by any differing byte in these files, apart from the wall-clock
lines of the log.

### Prediction T1 (constraints at the start), written before the runs

Ball R_b = 10 M (H R_b = sqrt(2M/R_b) = 0.447), uniform meshes, four ghost cells.

(a) Vacuum exterior, cells further than four cells from the surface: the Hamiltonian
residual is at rounding level (flat metric, and 4 KL KT + 2 KT^2 = 0 algebraically),
below 1e-13; the momentum residual falls as dx^6 (a factor of 64 per halving of dx,
accepted range 45 to 80) until rounding, with a magnitude near
(1/140) dx^6 d^7/dR^7 of sqrt(2M) R^(-3/2), about 1e-7 at dx = 1 and R = 12. Refuted
by an order below 5 or by an exterior Hamiltonian residual above 1e-10.

(b) Interior with a lattice at rest (u_i = 0) whose spacing divides the cell size, sites
symmetric about the cell centres, cells further than four cells inside the surface:
the deposited energy density equals rho_0 to rounding, so both residuals are at
rounding level (relative to 16 pi rho_0 below 1e-10) for every particle number and
resolution. Refuted by a relative Hamiltonian residual above 1e-8 there.

(c) Interior with a lattice that does not divide the cell size (ratio dx/h = 1.5, 2.5,
3.5): the cloud-in-cell deposit leaves a pattern of relative amplitude near
2 sin^2(pi q)/(pi q)^2 per direction before the filter (q = dx/h), that is a few per
cent at q = 1.5, falling roughly as N^(-2/3). The momentum residual stays at rounding
(S_i = 0, K_ij constant). Refuted if the residual does not fall with q, or if it is
below 1e-6 at q = 1.5.

(d) Surface layer (within four cells of the surface), sharp surface: Hamiltonian
residual of order 16 pi rho_0 in the largest cell at every resolution (does not
converge pointwise), L1 norm over the mesh proportional to dx; momentum residual of
order (3H/2)/dx in the largest cell (grows as 1/dx), L1 norm roughly constant.
With the smooth edge of fixed half-width w = 2 M both fall with resolution once
w is four cells or more, at the order of the deposit (second) or better. Refuted if
the sharp-surface momentum residual stays bounded as dx falls, or if the smooth edge
does not converge.

### Amendment of prediction T1 (c), written before any run of test 1

Prediction (c) overlooked the binomial pass (`nfilter = 1`, the setting of the test). A
lattice with q = dx/h puts its first harmonic at the mesh wavenumber
k dx = 2 pi (q - round(q)); for q = 1.5, 2.5, 3.5 that is the two-cell wave, which the
weights (1/4, 1/2, 1/4) remove. Amended prediction: with one pass the half-integer
lattices leave a relative residual below 1e-8 in the interior, like the matching ones;
the pattern is visible for q = 1.25, 2.25, 3.25 (k dx = pi/2, pass response 1/2), with
relative amplitude of the density near 2 sin^2(pi q)/(pi q)^2 times 1/2 per direction:
3.2e-2, 1.0e-2, 4.8e-3 (rms over the interior of the Hamiltonian residual relative to
16 pi rho_0 within a factor of two of sqrt(3/2) times these), independent of the
resolution at fixed q; without the pass (`nfilter = 0`) twice that for q = 1.25 and
2 sin^2(pi q)/(pi q)^2 = 9.0e-2 per direction for q = 1.5. A lattice shifted by a
quarter cell with q = 1 stays exact (the cloud-in-cell weights of a uniform lattice
with one site per cell sum to one). Refuted if the q = 1.25 residual is below 1e-3 or
above 0.2, if it does not fall with q, or if the shifted lattice shows a residual above
1e-8. The case list of `test1_runs.py` was changed accordingly (q = 1.25, 2.25, 3.25
with the pass; q = 1.25, 1.5 and 1 without it).

## 2026-11-15, entry 2: implementation, symbolic check, regression of format 1

Written: `python/nrpic/io.py` (`write_tab2`, `read_tab2`, `Table2`),
`python/nrpic/expanding_ball.py` (class `Ball`, exact radii, `residuals_1d`),
`problems/ic/make_ball.py`, `problems/ball/ball.athinput`, the format-2 path of
`athenak/src/pgen/nrpic/nrpic_cf.cpp`, the refined interface text
`tracks/core/interfaces/spherical_id_format2.md`, `docs/FORMATS.md`.

Symbolic check [VERIFIED]: `tracks/core/analysis/id/check_derivation.py` (sympy), 15
statements, all pass: K^r_r = -Rdot'/R' and K^theta_theta = -Rdot/R for the slices of
constant dust proper time; (3)R = -4 (E R)'/R^2; the Hamiltonian constraint with
rho = m'/(4 pi R^2); the momentum constraint, equivalent to d KT/d ln R = KL - KT; the
conformally flat radial coordinate; KL = KT = -H inside, KT = -sqrt(2M/R^3) and
KL = -KT/2 outside, jump of KL equal to 3H/2; the two exact radius laws. Item 1 of
`coord/notes/derivations_to_check.md` is confirmed, including KL = -dv/dR at fixed tau
when E depends on R (in the coordinates (tau, R) the Christoffel term of the shift is
cancelled by the time dependence of E at fixed R).

Offline check of the reference tables [VERIFIED, `residuals_1d` run by hand, numbers
printed by the generator into the JSON file of every data set]: marginally bound sharp
ball R_b = 10 M, largest |M| over the rows 2.3e-11, 1.5e-12, 9.5e-14, 9.4e-15, 1.2e-14
for 250, 500, 1000, 2000, 4000 rows across the matter (fourth order, then rounding),
largest |H| 5e-18; `Table2` reproduces the closed-form profiles to 3e-15 at 2e5 random
radii, on both sides of the break.

### Outcome of prediction R (regression of format 1)

- Processor build, 12 steps: all nine output files identical between the executable
  built before the change (run `core-20261115-031705-b7b431d`) and after it (run
  `core-20261115-032757-b7b431d`): two history files, the constraint statistics, two
  snapshots, two mesh restart files and two particle restart files
  (`regress_format1.py`). Prediction confirmed, with one qualification found on the way:
  36 bytes of every mesh restart file are not data. They are the nine coarse-cell
  members of `Mesh::mesh_indcs`, never set and written from memory
  (`athenak/src/outputs/restart.cpp:226`, `athenak/src/mesh/mesh.hpp:40-41`); the
  comparison leaves them out.
- Card build: a card run with particles is not reproducible to the byte. Two runs of the
  executable built before the change (`core-20261115-033115-b7b431d`,
  `core-20261115-033228-b7b431d`) differ from the first step on (constraint statistics
  at the 1e-16 level, growing to 1e-13 after 12 steps; the deposit adds the particles in
  an order that changes from run to run [JUDGEMENT: not tested by a run in which it could
  have failed]). So the card comparison is restricted to the start: the first mesh
  restart file (292 MB, the whole Z4c and ADM state), the first particle restart file,
  the first snapshot and the first record of each history file are identical between
  before (`core-20261115-033115-b7b431d`) and after (`core-20261115-033118-b7b431d`).
  The statement of `scripts/README.md` that uninterrupted card runs are reproducible to
  the bit holds for vacuum runs only [TO VERIFY by core's documentation package].

Lines touched in shared files: only `athenak/src/pgen/nrpic/nrpic_cf.cpp` (the existing
kernel `nrpic_cf` is unchanged; `CFExcess` gained one branch; the component loop gained
one branch before the format-1 branch; one hook after the kernel; new functions in the
anonymous namespace), `python/nrpic/io.py` (appended), `docs/FORMATS.md` (one section
inserted). No file of the particle module or of Z4c was changed.

## 2026-11-15, entry 3: outcome of test 1 (constraints at the start)

Runs: 26 registered runs with tag `t1-*` at commit 408df57 (ids in
`tracks/core/analysis/id/test1_numbers.json`, key `run_id`; the sharp sequence is
`core-20261115-033645-408df57` (64 cells), `-033653-` (96), `-033648-` (128), `-033745-`
(192), `-033748-` (256)). Ball R_b = 10 M, mesh half-width 32 M, start only. Analysis
`test1_constraints.py`; figures `figs/t1_exterior`, `t1_profiles`, `t1_surface`,
`t1_interior` (looked at). Scales: 16 pi rho_0 = 1.2e-2, H = 4.472e-2, H/R_b = 4.47e-3.
All numbers [VERIFIED] by these runs.

(a) Vacuum exterior. Confirmed. Hamiltonian residual at rounding: largest value
1.5e-18 to 5.6e-18 on all five meshes. Momentum residual, largest value in 16 < r < 28:
3.34e-8, 3.27e-9, 6.14e-10, 5.67e-11, 1.03e-11 for dx = 1, 2/3, 1/2, 1/3, 1/4 M; orders
between successive meshes 5.73, 5.82, 5.88, 5.92 (sixth-order differences). Correction
of my first analysis: with the region 16 < r < 30 the coarsest mesh gave 1.0e-6 (order
14 to the next mesh), because cells within three cells of the mesh boundary difference
across ghost cells that the outflow boundary condition has overwritten; such cells are
now left out. Note for users: the constraint monitor is not meaningful within three
cells of an outflow boundary.

(b) Interior, lattice dividing the cell (q = 1, 2, 4; 4.2e3 to 2.1e6 particles; dx = 1 to
1/4 M). Confirmed: largest |H| between 6e-18 and 2.5e-16 (below 2.1e-14 of
16 pi rho_0), largest |M_i| below 3.1e-16, for every particle number and mesh.

(c) Lattices that do not divide the cell (amended prediction). Confirmed for q = 1.25,
2.25, 3.25 with one binomial pass: interior rms of |H|/16 pi rho_0 = 3.5e-2, 1.1e-2,
5.1e-3 (estimates 3.9e-2, 1.2e-2, 5.9e-3), the same at dx = 1, 1/2, 1/4 M for q = 1.25
(3.41e-2, 3.48e-2, 3.47e-2); without the pass twice that for q = 1.25 (6.9e-2);
q = 1.5 with the pass at rounding (1.1e-15). Momentum residual at rounding throughout.
Two parts of the prediction failed:
- q = 1.5 without the pass gave rounding (4.4e-15), not 9e-2. For sites symmetric
  about the cell centres the two-cell pattern is sampled at its zeros. Test in which
  this could have failed: the same lattice displaced by h/4, no pass
  (`core-20261115-033953-408df57`): rms 0.19, largest 0.37 of 16 pi rho_0 (estimate
  0.16 and 0.27 from three directions of amplitude 0.09).
- the q = 1 lattice displaced by h/4 first gave a uniform residual 5.0e-5 of
  16 pi rho_0 (`core-20261115-033712-408df57`). Cause: the generator normalised all
  masses of a displaced lattice to the total, which changes the interior density by the
  relative error of the site count (33512 sites instead of 33552). After the change of
  `Ball.lattice` (displaced lattices use the same mass rules; default: only the surface
  layer is rescaled) the interior is at rounding (7.7e-18,
  `core-20261115-033954-408df57`). Lesson for the tracks: never normalise all lattice
  masses; put the count error into the surface layer.

(d) Surface layer. Confirmed. Sharp surface: largest |H| = 0.47, 0.49, 0.44, 0.45,
0.44 of 16 pi rho_0 at dx = 1 ... 1/4 M (no pointwise convergence); integral of |H|
over the layer 8.7, 6.0, 4.3, 2.8, 2.1 M (proportional to dx). Largest |M_i| = 4.7e-2,
7.8e-2, 0.108, 0.152, 0.208 (proportional to 1/dx, 0.70 of the jump of KL per cell,
3H/(2 dx)); its integral 55.9, 57.9, 58.1, 56.7, 56.1 (constant). The momentum
residual of a sharp surface is a grid-scale sheet whose amplitude grows with
resolution: it converges to zero only on average (weakly), not in any norm of the
absolute value.
Smooth edge, half-width 2 M: largest |H| = 1.03e-3, 2.96e-4, 7.64e-5 and largest
|M_i| = 7.78e-4, 1.98e-4, 4.69e-5 at dx = 1, 1/2, 1/4 M (second order: ratios 3.5, 3.9
and 3.9, 4.2); integrals fall as dx^2 and dx^3. Half-width 1 M: |H| 2.38e-3, 9.52e-4,
2.75e-4; |M_i| 6.10e-3, 1.40e-3, 3.47e-4. The order of M is limited by the quintic step
(third derivative of the density jumps at the two ends of the edge), that of H by the
cloud and the binomial pass.
Not predicted: without the binomial pass and with one site per cell the sharp surface
has largest |H| = 1.05e-4 (0.9 per cent of 16 pi rho_0) instead of 5.3e-3, and
integral 6.3e-2 instead of 4.3 (`core-20261115-033734-408df57`): a site at a cell
centre deposits into its own cell only, each cell is then either interior or exterior
in both K_ij and E, and the Hamiltonian constraint holds cell by cell; the pass smears
E over the neighbours and K_ij does not follow. The momentum sheet is the same with and
without the pass.

### Prediction T2 (evolution of the marginally bound ball), written before the runs

Ball R_b = 10 M, M = 1 (H_0 = 0.04472, initial Hubble time 22.4 M), uniform meshes of
half-width 32 M with 64, 128, 256 cells (dx = 1, 1/2, 1/4 M), one lattice site per cell,
cloud-in-cell with one binomial pass, RK4 with Courant number 0.25, evolution to
t = 10 M. Exact: every shell has R(tau) = R_0 (1 + 3 H_0 tau/2)^(2/3) in its own proper
time; tracers outside have R = (R_0^(3/2) + (3/2) sqrt(2M) tau)^(2/3). Error measure:
eps = R_areal/R_exact - 1 with R_areal = r sqrt(g_T) from the metric at the particle
(`.trajmet.bin`), compared at tau = 2, 4, 6, 8 M.

Gauges: "mp" 1+log with advection and Gamma-driver (shift_Gamma = 0.75, eta = 2),
start lapse 1 and shift 0; "mp-pg" the same with the Painleve-Gullstrand shift of the
table at the start; "ct" lapse d_t alpha = beta^i d_i alpha - (1/3) alpha^2 K
(lapse_harmonic = 1/3) with the same Gamma-driver; "ct0" that lapse without advection
and with the shift held at zero (the gauge of `cosmo/`).

(a) Interior shells (R_0 < 0.75 R_b), gauge mp: |eps| below 5e-3 at dx = 1 M and below
1.5e-3 at dx = 1/2 M for tau <= 8 M, falling with resolution at an order between 1 and 2
(surface representation and sources held fixed during a step are first order).
Refuted by |eps| above 2e-2 at dx = 1/2 M or by no decrease from dx = 1 to 1/4 M.
(b) Surface shell (R_0 > 0.95 R_b): |eps| below 3e-2 at dx = 1 M, first order. Refuted
by an error that grows with resolution.
(c) Exterior tracers: |eps| below 1e-3 at dx = 1/2 M (the exterior feels only the total
mass, which the deposit conserves). Refuted by 1e-2.
(d) Smooth edge (w = 2 M): interior and edge shells converge at second order or
better, with errors below those of the sharp surface at equal dx.
(e) Constraints: the mesh means of |H| and |M_i| do not grow by more than a factor of
ten between the first step and t = 10 M (no exponential growth); the sharp-surface
momentum sheet decays from its start value as dissipation and damping act. Refuted by
growth beyond a factor of ten or by a run that ends before t = 10 M.
(f) Gauge mp: the central lapse follows alpha = 1 + 6 ln a(tau_c) within 2 per cent
while t < 4 M (until the lapse wave from the surface, where K jumps from -3H to -3H/2,
reaches the centre); the lapse keeps growing, above 3 at the centre at t = 10 M, and
the largest coordinate speed of light alpha/sqrt(g_rr) at the particles exceeds 2. The
step is not adapted to it (`z4c_newdt.cpp`), so the effective Courant number rises to
above 0.5; no instability is expected before t = 10 M. Gauge ct: central lapse equals
a(tau_c) within 1 per cent while t < 5 M and the coordinate speed of light stays within
20 per cent of 1. Refuted by a central lapse that does not grow, or by a ct light speed
above 1.5.
(g) Gauge mp-pg: the Gamma-driver damps the initial shift (eta = 2/M): |beta| at the
surface particles falls below one fifth of its start value 0.447 by t = 2 M; the
errors of the interior shells are within a factor of three of those of gauge mp.
(h) Sources extrapolated to the middle of the step (`source_density`,
`source_extrap`): interior |eps| at dx = 1/2 M not larger than without, and smaller if
the time lag of the sources is the leading error.

## 2026-11-15, entry 4: test 2, first look, and two further predictions

First look at the 15 runs of test 2 (tag `t2-*`, commit c9aa6d2; numbers and outcome in
entry 5). Two things were not predicted and decide the next runs:
- the mesh mean of |H| rises by a factor of 20 or more within the first few steps and
  then does not fall with resolution (sharp surface, every gauge);
- with the 1+log lapse the central lapse follows 1 + 6 ln a up to 3.4 and then falls to
  1.5 within 0.4 M at t = 5.8 M: a lapse front that starts at the surface, where K
  jumps, arrives at the centre.

### Prediction T2b (smooth edge with the conformal-time lapse), written while the runs were queued, before any of their output was read

Cases `ct-edge2-n064, -n128, -n256` (mesh half-width 32 M) and `ct-edge2-big-n192`
(half-width 48 M, dx = 1/2 M). Reasoning: the conformal-time lapse has the gauge speed
alpha sqrt(alpha/3)/sqrt(g_rr), about 0.6, so its lapse front cannot reach the centre
before t = 17 M; the smooth edge has no jump of K_ij and no momentum sheet.
Prediction: (i) the rms of H and of M_i in the interior and in the edge region fall
with resolution at second order at every dump time up to t = 10 M (ratio between
dx = 1/2 and 1/4 M above 3), unlike every sharp-surface run and unlike `mp-edge2`;
(ii) largest |eps| of all ball shells at tau = 8 M below 5e-4 at dx = 1/2 M and second
order; (iii) the residual in the layer next to the mesh boundary does not fall with
resolution (the outflow condition of Z4c assumes fields that fall as 1/r, the
Painleve-Gullstrand exterior has K_ij proportional to r^(-3/2)), and with the boundary
at 48 M the residual in 10 < r < 18 M is the same as with the boundary at 32 M.
Refuted by an interior residual that does not fall between dx = 1/2 and 1/4 M.

### Prediction T3 (bound ball that turns around), written before the runs

Ball `Ball(M=1, Rb=5, e0=0.16, RE=10)`: 2M/R_b = 0.4, H R_b = 0.283, every shell
reaches a_max = 1.25 at tau = 9.542 M and then falls (time reverse of
Oppenheimer-Snyder collapse from R = 6.25 M); isotropic surface radius 4.616 M, central
psi = 1.0897; sharp surface (the smooth edge is implemented for the marginally bound
ball only). Mesh half-width 20 M, 80, 160, 320 cells (dx = 1/2, 1/4, 1/8 M; 9, 18, 37
cells per surface radius), one lattice site per cell, conformal-time lapse with
Gamma-driver (`bound-ct-*`), to t = 12 M; one run with the 1+log lapse at dx = 1/4 M
(`bound-mp-n160`).
Prediction: (i) the shells turn around: the largest areal radius of the core and outer
shells is within 0.5 per cent of 1.25 R_0 at dx = 1/4 M, reached at a proper time
within 3 per cent of 9.54 M; (ii) largest |eps| of the ball shells below 1e-2 at
dx = 1/4 M for tau <= 12 M, first order in dx; (iii) the central lapse equals
a(tau_c) within 2 per cent until t = 8 M and then stops growing as the ball turns
around (alpha = a holds while the centre is homogeneous); (iv) with the 1+log lapse
the front from the surface reaches the centre near t = 3 M and the errors of the core
shells are at least twice those of the conformal-time run. Refuted by shells that do
not turn around, by |eps| above 5 per cent, or by a run that ends before t = 12 M.

## 2026-11-15, entry 5: outcome of test 2 (evolution of the marginally bound ball)

Runs: 15 card runs, tag `t2-*`, commit c9aa6d2, 0.21 card-hours in all (ids in
`tracks/core/analysis/id/test2_numbers.json`; the 1+log sequence is
`core-20261115-034331-c9aa6d2` (dx = 1 M), `-034340-` (1/2 M), `-034341-` (1/4 M); the
conformal-time sequence `-034414-`, `-034416-`, `-034433-`; smooth edge `-034703-`,
`-034705-`, `-034723-`). Analysis `test2_evolution.py`; figures `figs/t2_radius_mp`,
`t2_radius_ct`, `t2_radius_mp_edge2`, `t2_variants`, `t2_constraints`,
`t2_constraints_regions`, `t2_Hprofile`, `t2_gauge`, `t2_profiles` (looked at:
radius_mp, constraints, constraints_regions, Hprofile, gauge, variants). All numbers
[VERIFIED] by these runs; "largest" is over the tracked particles of a group (2000 ball
particles in four groups of initial radius, 26 tracers per exterior radius).

(a) Interior shells. Largest |eps| at tau = 8 M, dx = 1, 1/2, 1/4 M:

| gauge, surface | core (R_0 < 0.5 R_b) | mid (0.5 to 0.75) | outer (0.75 to 0.95) | surface (> 0.95) |
|---|---|---|---|---|
| 1+log, sharp | 6.2e-3, 2.7e-3, 1.0e-3 | 3.0e-3, 1.25e-3, 4.2e-4 | 3.6e-3, 1.16e-3, 3.7e-4 | 6.8e-3, 4.0e-3, 1.7e-3 |
| conformal time, sharp | 7.6e-4, 4.0e-4, 1.7e-4 | 1.9e-3, 1.17e-3, 4.0e-4 | 2.2e-3, 1.21e-3, 4.2e-4 | 5.3e-3, 3.9e-3, 1.7e-3 |
| 1+log, edge w = 2 M | 4.7e-3, 1.26e-3, 4.3e-4 | 1.4e-3, 4.1e-4, 2.4e-4 | 2.2e-3, 6.0e-4, 1.6e-4 | 4.6e-4, 1.5e-4, 5.9e-5 |

The prediction (below 5e-3 at dx = 1 M, below 1.5e-3 at dx = 1/2 M) holds for the
means (core, 1+log: 2.9e-3, 1.1e-3, 3.8e-4) and for the conformal-time lapse, and fails
for the largest values of the core with 1+log (6.2e-3, 2.7e-3). Orders between 1.2 and
1.6: as predicted.
(b) Surface shell: first order (ratios 1.7 and 2.3), 6.8e-3 at dx = 1 M. Confirmed.
(c) Tracers at dx = 1/2 M: largest |eps| over the whole run 1.4e-3 at 1.25 R_b (above
the predicted 1e-3; 3.8e-4 at tau = 8 M), 1.9e-4 at 2 R_b. Marginally failed at
1.25 R_b, confirmed further out. The tracers at 1.25 R_b feel the surface (first
order: 2.9e-3, 1.4e-3, 5.8e-4).
(d) Smooth edge: the edge and outer shells are ten times more accurate than with the
sharp surface and of second order (outer: ratios 3.7, 3.9); the core is not better
than with the sharp surface. Partly confirmed: the core error is not a surface effect
(see the lapse front below).
(h) Sources extrapolated to the middle of the step: mean core eps at tau = 8 M
7.5e-4 instead of 1.10e-3, largest 2.4e-3 instead of 2.7e-3 (dx = 1/2 M). Confirmed, a
modest gain. Eight sites per cell: mean 3.7e-4, largest 2.4e-3. Without the binomial
pass: no change (1.19e-3, 2.8e-3). Mesh boundary at 48 M instead of 32 M: identical to
three digits in every group up to tau = 8 M, so the boundary does not reach the
particles in these runs.

Whole run (to t = 10 M; proper time up to 19 M at the centre with 1+log, 12.4 M with
the conformal-time lapse), largest |eps|, dx = 1, 1/2, 1/4 M:
- conformal time, sharp: core 3.3e-3, 1.07e-3, 4.6e-4; mid 3.0e-3, 1.4e-3, 5.4e-4;
  outer 4.5e-3, 1.7e-3, 5.7e-4; surface 7.2e-3, 4.0e-3, 1.9e-3; tracers at 1.25 R_b
  3.3e-3, 1.15e-3, 4.2e-4. Converges everywhere.
- 1+log, sharp: core 7.9e-2, 7.7e-2, 0.245; mid 8.5e-3, 2.7e-3, 1.0e-3; outer 5.8e-3,
  3.6e-3, 1.0e-3; surface 9.7e-3, 5.6e-3, 2.6e-3. The core does NOT converge: the
  innermost tracked shells are wrong by several per cent to 25 per cent after
  t = 5.5 M.

(e) Constraints. Failed, and this is the main finding of the test.
- Sharp surface, every gauge: the mesh mean of |H| goes from 3.3e-5, 1.6e-5, 8.1e-6
  (dx = 1, 1/2, 1/4 M) at the start to 2.3e-4 after the FIRST step at every resolution,
  and stays between 2e-4 and 7e-4. By region (rms of H at t = 2 ... 10 M): surface
  layer 1.1e-2 falling to 1.6e-3, the same at all three resolutions; interior
  1e-3 to 4e-3 (conformal time) or 5e-3 to 1.2e-2 (1+log), not falling with resolution;
  exterior out to 18 M 2e-3 to 3e-3, not falling. For scale 16 pi rho = 1.2e-2 at the
  start. The residual spreads from the surface at about the speed of light (front at
  r = 17 M at t = 4 M, `figs/t2_Hprofile`).
  Cause [JUDGEMENT, supported by the one-step jump and by the smooth-edge runs, in
  which it could have appeared and did not]: with zero shift the coordinates are
  comoving with the dust, and in comoving coordinates the exact metric component g_rr =
  (dR/dr)^2 is discontinuous at a sharp surface for tau > 0, because m'(r) jumps there.
  One step gives the metric a jump of 2 dt times the jump of K_ij across one cell; its
  second differences are a curvature of order (Courant number) x (jump of K)/dx, the
  size of the momentum sheet of test 1. Finite differences cannot converge on it.
- Smooth edge (1+log): mean |H| 3.4e-6 at the start, 4.5e-6 after the first step
  (dx = 1/2 M); rms in 16 < r < 18 M: 5.2e-5 and 8.9e-6 at t = 2 M for dx = 1/2 and
  1/4 M (falls), interior 1.2e-4 and 2.1e-5 at t = 2 M (falls), but not from t = 4 M on
  (1.75e-4, 1.79e-4), when the lapse front of the 1+log gauge is inside.
- Layer next to the mesh boundary (r > 22.4 M of 32 M): rms of H 2e-5 at t = 2 M,
  rising to 7e-4 (1+log) or 3.7e-4 (conformal time) at t = 10 M, the same at all
  resolutions and for both surfaces: the outflow condition of Z4c
  (`athenak/src/z4c/z4c_Sbc.cpp:95-125`, d_t f = -v (d_r f + f/r)) is not satisfied by
  the Painleve-Gullstrand exterior, whose K_ij falls as r^(-3/2). With the boundary at
  48 M the layer has 1.1e-4 at t = 10 M.

(f) Gauge. 1+log: the central lapse follows 1 + 6 ln a(tau_c) within 5.6e-4 for
t < 4 M (confirmed) up to 3.08, 3.24, 3.39 at t = 5.25, 5.50, 5.75 M (dx = 1, 1/2,
1/4 M), then falls to 1.5 - 1.7 within 0.4 to 1 M and stays at 1.68 until t = 10 M.
The prediction "keeps growing, above 3 at t = 10 M" failed. A lapse front starts at
the surface, where K jumps from -3H to -3H/2 (the lapse grows half as fast outside),
runs inwards at the gauge speed and focuses at the centre; behind it the slices are far
from the dust slices (largest K on the mesh +0.39 against -0.134 at the start,
smallest chi 0.457), the constraint residual at the front is of the order of
16 pi rho, and the innermost shells lose accuracy (above). The smooth edge does not
prevent it (central lapse 3.01 at t = 5.25 M, then 1.69). The largest coordinate speed
of light at the ball particles is 2.27 to 2.35 at t = 5.5 M (effective Courant number
0.59 at the nominal 0.25): confirmed; no instability to t = 10 M.
Conformal-time lapse: central lapse equals a(tau_c) within 4.9e-4 over the whole run
(dx = 1/2 M; 2.5e-4 at dx = 1/4 M), largest coordinate speed of light 1.13. Confirmed
and better than predicted: no front reaches the centre before t = 10 M.
(g) Painleve-Gullstrand shift at the start with the Gamma-driver (eta = 2/M): the
radial shift at the surface shell is -0.436, -0.161, -0.060, -0.012, -0.006 at t = 0,
0.5, 1, 2, 4 M (decays as exp(-2t/M)); errors within 30 per cent of the zero-shift
start. Confirmed. The coordinates do not stay areal.
Coordinate motion (dx = 1/2 M, end of run): with the conformal-time lapse the core
stays at its coordinate radius (r/r_0 = 1.014, 1.002 with the shift held at zero)
while its areal radius grows by 1.50; the surface moves to r/r_0 = 1.13. With 1+log
the particles move through the mesh, r/r_0 = 1.55 (core), 1.43 (surface), although the
shift stays below 0.02: the lapse gradient behind the front accelerates the normal
observers relative to the dust.

## 2026-11-15, entry 6: check of the reader against the Python evaluator (curved slice)

### Prediction T0, written before the runs

The tests so far used the flat slice (psi = 1). The bound ball
(`Ball(M=1, Rb=5, e0=0.16, RE=10)`) has psi different from 1, three pieces (two
breaks) and non-trivial KL, KT, betar in the vacuum between the surface and the radius
where E reaches zero, so its start exercises every branch of the format-2 reader.
Start-only processor runs, mesh half-width 16 M, 64 and 128 cells (dx = 1/2, 1/4 M),
lapse and shift from the table.
Prediction: (i) at the cell centres the dumped lapse and trace K = KL + 2 KT equal the
values of `nrpic.io.Table2` to 1e-12, and chi equals psi^-4 to the single precision of
the dump (1e-7); the shift reconstructed at the tracked particles equals betar n^i of
the table to the interpolation error of the particle metric (below 1e-4); (ii) in the
vacuum part of the curved slice, 6.7 < r < 9 M, the Hamiltonian and the momentum
residual fall at sixth order between the two meshes (ratio between 40 and 80), which
tests psi^4, the tensor structure and the one-sided interpolation together; (iii) with
the header changed to `exterior = zero` the trace K vanishes beyond the last row and is
unchanged inside. Refuted by any mismatch above these bounds or by an order below 5.

### Outcome of prediction T0 (reader against the Python evaluator)

Runs `core-20261115-040311-1311b8e` (64 cells), `core-20261115-040326-1311b8e` (128),
`core-20261115-040319-1311b8e` (exterior = zero); `test0_reader.py`,
`figs/t0_reader` (looked at); independent evaluation `check_momentum_3d.py`.
(i) Confirmed for the trace K (largest difference 1.1e-16), the lapse (0) and chi
(3e-8, single precision of the dump). The shift at the tracked particles differs from
the table by 2.7e-4 at dx = 1/2 M and 7.7e-5 at dx = 1/4 M (scale 0.447): above my
bound of 1e-4 on the coarse mesh, falling with resolution; it is the error of the
reconstruction of the metric at the particle.
(ii) Hamiltonian residual in 6.7 < r < 9 M: 2.30e-6 and 1.32e-8 (order 7.4). Momentum
residual: 3.45e-4 and 1.44e-5, order 4.6: below the predicted sixth order. Checked with
an independent evaluation of the same table in numpy (other form of the constraint,
same differences): 3.17e-4, 1.32e-5, 2.75e-7, 4.59e-9 at dx = 1/2, 1/4, 1/8, 1/16 M,
orders 4.58, 5.59, 5.90. The code and the independent evaluation agree within 10 per
cent, and the order 4.6 is the approach to sixth order on a profile that varies over
2.5 M. So the Cartesian form of K_ij with psi different from 1 is verified; my
prediction of the order on these two meshes was wrong.
(iii) Confirmed: with `exterior = zero` the trace K is exactly zero beyond the last
row and unchanged inside.

Failed runs on record: `core-20261115-035639-c9aa6d2`, `core-20261115-035638-c9aa6d2`
(and the two that followed in that driver) ended at once with "Parameter
'field_time6' ... on command line not found": the driver passed a dump time that the
input file does not declare. Driver corrected; the bound-ball cases were started again.

### Finding between the runs: the sources held fixed during a step

Field dumps of test 2, centre of the ball (r < 3 M), t = 2 M: the Hamiltonian residual
is a uniform offset, +3.49e-5, +1.69e-5, +8.41e-6 for dx = 1, 1/2, 1/4 M with the
conformal-time lapse (3.8e-3, 1.8e-3, 9.1e-4 of 16 pi E): first order in the step.
With `source_density = true`, `source_extrap = true` (run `mp-ext-n128`,
`core-20261115-034739-c9aa6d2`) the offset is +3.0e-8 (3.5e-6 of 16 pi E) against
+2.37e-5 in the same run without (`mp-n128`). Cause shown by that run, in which it
could have failed: the deposited sources are held at t^n during the stages of the
step unless these two options are set. [VERIFIED]

### Prediction T2c (recommended configuration), written before the runs

Cases `ct-edge2-ext-n064, -n128, -n256`: conformal-time lapse, smooth edge w = 2 M,
sources extrapolated to the middle of the step. Prediction: the offset of H at the
centre is below 1e-4 of 16 pi E at t = 2 and 4 M on all three meshes; the largest
|eps| of the core shells at tau = 8 M is below that of `ct-edge2` at equal dx and falls
at second order (ratio above 3 from dx = 1/2 to 1/4 M). Refuted by an offset above
5e-4 or by a core error that is not smaller than without the extrapolation.

### Prediction T2d (lattice noise late in the smooth-edge run), written before the runs

Seen in `ct-edge2` (outcome in entry 7): the rms of H in the interior and in the edge
falls with resolution until t = 4 M and then rises to 2e-4 - 3e-4 at t = 8 - 10 M, larger
at dx = 1/4 M than at dx = 1/2 M, while the vacuum between the ball and r = 18 M stays
clean (7e-6 at dx = 1/4 M). Hypothesis: lattice noise. The particles drift against the
mesh (r/r_0 = 1.01 in the core, 1.13 at the edge), the lattice no longer divides the
cells, and the cloud-in-cell deposit of one site per cell then carries a pattern of a
few per cent of 16 pi rho (test 1: 3.5 per cent at 1.25 sites per cell), that is 1.6e-4
at t = 8 M; a finer mesh loses the match sooner.
Test: the production configuration of `cosmo/README.md` for lattice starts (cubic
cloud with compensation, spline interpolation of the metric, no binomial pass,
sources extrapolated): cases `ct-edge2-prod-n128`, `-n256`. Prediction: the rms of H
in the interior at t = 8 and 10 M at dx = 1/4 M is below 5e-5 (at least four times
below the 2.1e-4 and 3.2e-4 of `ct-edge2`), and not larger than at dx = 1/2 M. Refuted
if it stays above 1e-4: then the late residual is not lattice noise.

### Prediction T2e (lapse and shift held fixed), written before the runs

Seen in the first two bound-ball runs (outcome in entry 7): the conformal-time lapse
also sends a front from the surface to the centre, at about 0.58 of the speed of light
(arrival at t = 8 M for the ball of isotropic radius 4.6 M; the central lapse rises to
1.33, falls to 0.69 and the core shells lose accuracy). Every lapse condition of the
form d_t alpha = -f(alpha) alpha K reacts to the jump of K at the surface.
The exact solution suggests the gauge without that reaction: lapse 1 and shift 0 held
fixed (`lapse_oplog = lapse_harmonic = 0`, no advection, no Gamma-driver): the slices
stay the slices of constant dust proper time, the coordinates stay comoving, dust at
rest stays at its coordinate position (u_i = 0 for ever), so the lattice keeps matching
the mesh and t equals the proper time of every particle. The risk: geodesic slicing
with a fixed shift is not known to be well posed in this formulation [BACKGROUND, not
checked against the literature here], and it ends where shells cross or collapse.
Cases `gs0-edge2-ext-n128`, `-n256` (smooth edge), `gs0-ext-n128` (sharp),
`bound-gs0-n160` (bound ball), all with the sources extrapolated.
Prediction: (i) the runs reach the end without growing grid-scale noise (mesh mean of
|H| does not grow by more than a factor of three between t = 2 M and the end);
(ii) the ball particles stay at their coordinates (|r/r_0 - 1| below 1e-4) and their
proper time equals t to 1e-6; (iii) smooth edge: largest |eps| of all ball shells over
the whole run below 2e-4 at dx = 1/2 M and second order; rms of H in the interior at
t = 8 and 10 M below 2e-5 at dx = 1/4 M (no lattice noise); (iv) bound ball: no front,
core shells follow the cycloid through the turnaround with largest |eps| below 5e-3 at
tau = 12 M. Refuted by an instability, by drifting particles, or by errors above
those of the conformal-time runs.

## 2026-11-15, entry 7: outcomes of T2b and T3 (as far as the cards allowed)

### Outcome of prediction T2b (smooth edge with the conformal-time lapse)

Runs `core-20261115-035615-c9aa6d2` (dx = 1 M), `core-20261115-035616-c9aa6d2` (1/2 M),
`core-20261115-040349-1311b8e` (1/4 M), `core-20261115-040406-1311b8e` (boundary at
48 M, dx = 1/2 M). Figures `figs/t2_radius_ct_edge2` and the common ones.
(ii) Confirmed in size, partly in order. Largest |eps| over the whole run (to
tau = 12.4 M at the centre), dx = 1, 1/2, 1/4 M: core 2.2e-3, 5.9e-4, 2.0e-4; mid
1.4e-3, 7.1e-4, 2.0e-4; outer 1.9e-3, 4.0e-4, 6.6e-5; edge shells 6.9e-4, 2.7e-4,
7.5e-5; tracers at 1.25 R_out 1.5e-4, 3.6e-5, 1.5e-5. At tau = 8 M the outer shells
are better than second order (1.36e-3, 2.7e-4, 4.5e-5), the core is first order
(7.6e-4, 3.2e-4, 1.5e-4): the source lag. This is the most accurate configuration
measured so far: all shells within 6e-4 at dx = 1/2 M and 2e-4 at dx = 1/4 M.
(i) Failed in part. The rms of H falls with resolution in the vacuum between the ball
and r = 18 M at all times (t = 6 M: 1.5e-4, 3.2e-5, 6.9e-6; t = 10 M: 4.0e-5, 9.4e-6,
1.1e-5) and in the interior until t = 4 M (1.44e-4, 7.2e-5, 1.8e-5), but from t = 6 M
on the interior and the edge do not converge (interior at t = 8 M: 3.9e-4, 7.5e-5,
2.1e-4; at t = 10 M: 3.6e-4, 1.8e-4, 3.2e-4). Hypothesis and test: prediction T2d.
(iii) Confirmed. Layer next to the boundary: 2.7e-4 - 3.0e-4 at t = 8 M and 3.7e-4 at
t = 10 M on all three meshes; with the boundary at 48 M the interior numbers are
identical to all printed digits and the layer has 8.0e-5. The tracers at 24 M show
the boundary: largest |eps| 4.8e-4 with the boundary at 32 M, 5.7e-7 with it at 48 M.

### Outcome of prediction T3 (bound ball), two of the three resolutions

Runs `core-20261115-040525-1311b8e` (dx = 1/2 M), `core-20261115-040524-1311b8e`
(dx = 1/4 M), conformal-time lapse, sharp surface, 0.017 card-hours. Figures
`figs/t3_radius_bound_ct`, `t3_gauge` (looked at). The run at dx = 1/8 M and the
1+log run were still queued when this was written (see the end of the journal).
(i) Confirmed for the radius, not for the time. All shells turn around. Largest areal
radius over initial radius (mean and spread over the tracked particles of a group;
exact 1.2500): dx = 1/2 M core 1.2615 +- 0.0074, mid 1.2520, outer 1.2487, surface
1.2474; dx = 1/4 M core 1.2528 +- 0.0036, mid 1.2561, outer 1.2526, surface 1.2515:
within 0.5 per cent at dx = 1/4 M. Proper time of the maximum (exact 9.542 M):
9.60 to 9.88 M at dx = 1/2 M; 9.63 (outer), 9.68 (surface), 9.87 (mid), 9.95 (core) at
dx = 1/4 M: 1 to 4 per cent late, above the predicted 3 per cent for the core.
(ii) Failed. Largest |eps| at tau = 8 M: 1.1e-2 (dx = 1/2 M) and 8.1e-3 (dx = 1/4 M);
over the whole run core 0.20 and 0.11, mid 2.5e-2 and 2.6e-2, outer 2.0e-2 and
1.7e-2, surface 2.1e-2 and 1.3e-2. The means are smaller (core at tau = 12 M: 2.4e-2
and 8.6e-3) but the mid and outer shells do not converge after tau = 8 M.
(iii) Failed, and this is the finding: the central lapse equals a(tau_c) within 7.8e-4
until t = 6 M (dx = 1/4 M), then a front arrives from the surface: the central lapse
rises to 1.33 at t = 8.4 M, falls to 0.69 at t = 9.6 M and is 1.17 at t = 12 M. The
conformal-time lapse has the same pathology as 1+log, only slower: speed about 0.58
(4.6 M in 8 M), so that it did not show within t = 10 M for the ball of radius 10 M
(arrival there near t = 17 M). After the front the innermost shells lose accuracy.
Rms of H: interior 8e-3 to 4e-2 (16 pi rho_0 = 9.6e-2), surface layer 3e-2 falling to
1.4e-3, the same at both resolutions (sharp surface).

## 2026-11-15, entry 8: source extrapolation, fixed gauge, state at the end

The cards were occupied by other owners from 04:10 on; what follows uses the card runs
that got through and four processor runs at 64 cells (tags `t2cpu-*`, `t3cpu-*`). The
processor run `core-20261115-041245-1311b8e` (bound ball, conformal time, dx = 1/2 M,
half-width 16 M) reproduces the card run `core-20261115-040525-1311b8e` (half-width
20 M) in every ball-shell number to the printed digits, so the two executables agree
and the boundary at 16 M does not reach the ball shells before tau = 12 M.

### Outcome of prediction T2c (sources extrapolated), dx = 1 and 1/2 M

Runs `core-20261115-041111-1311b8e` (dx = 1 M), `core-20261115-041112-1311b8e`
(1/2 M); the run at dx = 1/4 M was still queued. Offset of H at the centre over
16 pi E at t = 2 M: 4.1e-4 (dx = 1 M; 4.1e-3 without), 2.8e-6 (dx = 1/2 M; 1.8e-3
without); at t = 4 M and dx = 1/2 M 4.8e-5. Below 1e-4 at dx = 1/2 M as predicted, not
at dx = 1 M (the edge is four cells wide there). Core shells at tau = 8 M: largest
|eps| 7.2e-4 and 1.10e-4 (without: 7.6e-4, 3.2e-4), mean -4.0e-5 at dx = 1/2 M
(without +2.1e-4): smaller, and better than second order between these two meshes.
Whole run, dx = 1/2 M: core 4.6e-4, mid 6.3e-4, outer 3.6e-4, edge 2.7e-4. Confirmed
as far as run.

### Outcome of prediction T2e (lapse and shift held fixed), processor runs at 64 cells

Runs `core-20261115-044357-aef2f7b` (smooth edge, dx = 1 M),
`core-20261115-044358-aef2f7b` (sharp, dx = 1 M), `core-20261115-044359-aef2f7b` (bound
ball, dx = 1/2 M).
(ii) Confirmed: the particles stay at their coordinates (r/r_0 - 1 = 0 to the printed
digits) and their proper time is 10.000000 M at t = 10 M.
(iii) Smooth edge, dx = 1 M: largest |eps| over the run core 9.4e-4, mid 1.35e-3, outer
8.9e-4, edge 7.5e-4, against 1.8e-3, 1.2e-3, 1.8e-3, 6.8e-4 for the conformal-time run
with the same sources: comparable, somewhat better in the core. But the rms of H in the
edge region grows steadily, 3.6e-4, 6.7e-4, 1.1e-3, 1.6e-3, 2.2e-3 at t = 2 ... 10 M
(conformal time: 2.8e-4 falling to 5.9e-5). Sharp surface: outer and surface shells
1.6e-2 (conformal time 4.5e-3, 7.2e-3), surface residual 1.2e-2 growing to 2.1e-2.
(i), (iv) REFUTED for the bound ball: the run becomes unstable. Largest |H| 0.28,
0.29, 0.53, 0.97, 3.2 at t = 0, 1, 2, 3, 4 M, largest Theta 0.014, 0.018, 0.029, 0.15,
then not-a-number at t = 4.9 M; all particles are removed as non-finite. The code
runs on to the end and exits with status 0. So the gauge of the exact solution is not
usable in this formulation with a sharp surface: the growth in the edge region of the
weaker ball is probably the same instability at a lower rate [JUDGEMENT; the card
runs at dx = 1/2 and 1/4 M, queued, would show whether the rate grows with
resolution, the signature of an ill-posed system].
Trap for everyone: a run that has gone to not-a-number ends "successfully" with zero
particles; check the particle number in `<base>.nrpic.hst` (column 3).

### State at the end of this session

Done and tested: table format 2 in `nrpic_cf` (reader, K_ij, lapse and shift options),
Python reader, writer and evaluator, reference generator (marginally bound ball, sharp
or smooth edge; bound ball), offline constraint check, symbolic check, format-1
regression, tests 0, 1, 2, and test 3 at two resolutions.

Card runs still queued when the session ended (driver `test2_runs.py`, tags as
listed; their predictions are T2c, T2d, T2e, T3 above; `test2_evolution.py` and
`test2_evolution.py --prefix t3` pick them up when they have finished):
`t2-ct-edge2-ext-n256`, `t2-ct-edge2-prod-n128`, `t2-ct-edge2-prod-n256`,
`t2-gs0-edge2-ext-n128`, `t2-gs0-edge2-ext-n256`, `t2-gs0-ext-n128`,
`t3-bound-ct-n320`, `t3-bound-mp-n160`, `t3-bound-gs0-n160`.

Open, in order of use to Tracks A and D:
1. a lapse condition that does not send a front from the surface to the centre (both
   1+log and the conformal-time lapse do; a fixed lapse is unstable). Candidates not
   tried: a driver towards the dust slicing built on the particle four-velocity, the
   `lapse_kdriver` and `lapse_volume` conditions of `cosmo/`, a smooth edge wide
   enough that the front is weak;
2. T2d (is the late interior residual of the smooth-edge runs lattice noise?): untested;
3. a smooth edge for the bound ball (`Ball` has it for the marginally bound one only);
4. an outer boundary condition for exteriors whose K_ij falls as r^(-3/2);
5. second agent: nobody but this session has checked these results; Track A's own
   generator is the independent check of `expanding_ball.py`.
