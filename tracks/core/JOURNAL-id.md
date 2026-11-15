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
