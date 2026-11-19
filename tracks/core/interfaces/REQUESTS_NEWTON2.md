# The Newtonian mode, second pass: requests of tracks B, A, D and core's deferred items

Work package newton2 of core, branch `core/newton-2` (started from `core/requests-adf`),
wave 3a, 2026-11-19. Journal with the predictions and outcomes of every test:
`tracks/core/JOURNAL-newton2.md`. Scripts: `tracks/core/analysis/newton2/` (`cases.py`
runs the cases, `t<n>_*.py` judge them), figures `tracks/core/analysis/newton2/figs/`,
run manifests `tracks/core/runs/`. Interface text of the new options:
`tracks/core/interfaces/newtonian_mode.md` section 7. Labels: [VERIFIED] read or measured
in this package (locator given), [JUDGEMENT], [TO VERIFY].

## 1. Triage

| # | Request (outbox file of the track, or core's list) | Ruling | Reason, and what exists now |
|---|---|---|---|
| B1 | `track/B-emd-gw` `20261115T191056Z__to-core__newtonian-laplacian-order.md`: fourth-order option on periodic uniform meshes, or a spectral solve | ACCEPTED as the spectral solve, done | `<particles> newton_poisson = fft` (section 2.1). A Mehrstellen stencil inside the multigrid module is NOT planned: it would change the smoother, the defect and the restriction of every level of an upstream module that another package edits, for a gain that the Fourier solve gives exactly on the meshes the request names |
| B1 | the same request, on isolated or refined meshes | DECLINED for now | The multigrid solver stays second order there. On isolated domains the track's own test N1 is limited by the first-order error of a thin axis, not by the Laplacian (`newton_tests/README.md` N1) [VERIFIED by reading] |
| B1 | low priority: `d3I` after the remainder step at the end of a run | ANSWERED in the note, corrected in the new file only | The existing columns 37-43 of `<basename>.newton.hst` keep their behaviour (bit-identical rule): after a last step of about 1e-13 they are rounding over the step; drop that record, or choose `tlim` as a multiple of the step. The group history (B2) does not form the quotient after a step below 1e-6 of the one before |
| B2 | `...__to-core__newtonian-species-history.md`: mass, centroid, second moment about the centroid of one species or tag range, physical coordinates with cosmic-time derivatives | ACCEPTED, done | `<particles> newton_ngroup`, file `<basename>.newton.g<g>.hst` (section 2.2): comoving moments with conformal-time derivatives and physical moments with cosmic-time derivatives in the same record |
| A1 | `track/A-emd-pbh` `20261115T183721Z__to-core__newton-mode-followup.md`: which W the history reports; is K + W exact for the cloud-deposited potential | ANSWERED with a test | Section 3 and test T7: column 6 gathers the potential at the particles with the interpolation of the force; neither column 6 nor column 7 is an invariant of the scheme because deposit and gather kernels differ; the drift at shell crossing is a property of the space discretisation, not of the step |
| A2 | the same message, "for the queue": `make_ic.py ball` with `--axes`, `--vgrad`, `--rotate`, the lattice volume radius in the JSON (core's deferred "Zel'dovich ball") | ACCEPTED, done | `problems/newton/make_ic.py ball` (section 2.3), tested against the track's `make_deformed_ball.py` (T4a); also `--background` for a patch inside a homogeneous background (the track's item (f), needed by B's embedded ellipsoid) |
| A3 | `newton-mode-and-ball-ic` item 1, deferred in `REQUESTS_ADF.md`: special-relativistic push | DEFERRED again | Not in this package's list; a change of the kick-drift-kick kernel with its own conservation laws. The track's scan quotes 4 to 5 per cent at delta_L = 0.3 |
| A3 | the same item: snapshots at chosen times | DEFERRED | Output work nobody has asked for again; `snap_dt` exists |
| D1 | `track/D-bh-dress` `20261115T195036Z__to-core__newton-selfforce-doc.md`: state the self-force of a compact sub-cell object in the note (sections 5.2 and 6); does the relativistic mode share it | ANSWERED: note updated, measured map of the self-force (T8); the relativistic mode is [TO VERIFY] | Section 4. The Newtonian measurement is a property of the deposit and gather kernels, which the relativistic mode shares; a direct relativistic test (a single massive particle off a cell centre with constraint-solved data) was not run in this package |
| C1 | core, deferred in `REQUESTS_ADF.md` (D5 item 2): multigrid on refined meshes | TESTED (T6), see section 5 | The moving rotating ball across a static level boundary |
| C2 | the same item: throughput at 256^3 and 384^3 with 2e6 particles on a card | PENDING in the card queue | One card job (run core-20261119-145346-2f89b86, Slurm 4648), section 6 |
| C3 | core, deferred (A2 of `REQUESTS_ADF.md`): the Zel'dovich ball | done with A2 above | |

## 2. What was implemented

Each item: files and lines touched (other packages change the same directories),
options, test, numbers. Existing results are unchanged when the new options are absent
(T10, section 7).

### 2.1 Fourier Poisson solver on periodic uniform meshes (B1)

New file `athenak/src/particles/nrpic_newton_fft.cpp`. Options in `<particles>`, read
only if present:

| Option | Default | Meaning |
|---|---|---|
| `newton_poisson` | `multigrid` | `fft`: the potential of the deposited density by Fourier transform, Phi_k = -four_pi_G rho_k/K^2(k), Phi_0 = 0. Needs a uniform mesh that is periodic in all directions, all MeshBlocks in one pack, and cell numbers per direction that are products of 2, 3, 5 and 7 (fatal error otherwise). The `<gravity>` block stays (it holds `four_pi_G` and the potential array; the multigrid module is built and never called) |
| `newton_fft_symbol` | `spectral` | `spectral`: K^2 = k^2, the continuum operator, the Nyquist mode included. `seven_point`: K^2 = sum_d (2/h_d)^2 sin^2(k_d h_d/2), the symbol of the seven-point Laplacian of the multigrid solver: the same potential to rounding, without iteration |

Deposit, filter, cloud compensation, ghost cells, gather and diagnostics are those of the
mode; only the solve is replaced. Columns 48 and 50 of `<basename>.newton.hst` (defect,
V cycles) are zero. The transform is written with Kokkos kernels (the code base has no
Fourier library): the density is copied into one array of the mesh, each direction is
transformed line by line (one line per thread, in place, mixed radix 2, 3, 5, 7), the
symbol is applied, and the three inverse passes follow. Memory: four real arrays of the
size of the mesh. Restart: unchanged (the potential of the dump is the state).

Touched outside the new file: `particles/particles.hpp` (members `nw_fft*`, three
methods), `particles/nrpic_newton.cpp` (`NrpicNewtonInit`: one call; `NrpicNewtonPotential`:
the branch around the multigrid call), `CMakeLists.txt` (one line).

Tests T1 and T2 (section 7).

### 2.2 Second moments of particle groups (B2)

New file `athenak/src/particles/nrpic_newton_groups.cpp`. Options in `<particles>`, read
only if present:

| Option | Default | Meaning |
|---|---|---|
| `newton_ngroup` | 0 | number of groups, at most 8 |
| `newton_group<g>_species` | -1 | species of group g = 1 .. n (-1: every species) |
| `newton_group<g>_tag_min`, `_tag_max` | -1 | first and last tag (position in the particle file) of the group; -1: no bound |
| `newton_group<g>_x1`, `_x2`, `_x3` | middle of the mesh | reference point: in a periodic direction a position enters as its image nearest to this point, so that a patch narrower than half the box around it is not cut by the wrap |

One record per record of `<basename>.newton.hst` goes to `<basename>.newton.g<g>.hst`
(62 columns, text; six components are xx, xy, xz, yy, yz, zz):

| Columns | Content |
|---|---|
| 1-4 | time t of the run, cycle, scale factor a, cosmic time T = int_0^t a dt |
| 5, 6 | number of particles and rest mass M of the group (particles with m > 0) |
| 7-9, 10-12 | centroid X (comoving, the image nearest to the reference point) and its velocity dX/dt |
| 13-18, 19-24, 25-30 | I_ij = sum m (x - X)_i (x - X)_j, comoving, and its first and second derivative in t, with the velocity dx/dt = p/a and the acceleration g/a - (a'/a) dx/dt that the kick applies (external gravity included), centroid motion removed |
| 31-36, 37 | third derivative in t: difference quotient of columns 25-30 over the last step, and the mid-step time it belongs to |
| 38-43, 44-49, 50-55 | J_ij = a^2 I_ij, the second moment in physical coordinates r = a x, and dJ/dT = 2 a' I + a I', d2J/dT2 = (2 a''/a) I + (3 a'/a) I' + I'' (primes: derivatives in t) |
| 56-61, 62 | d3J/dT3: difference quotient of columns 50-55 over the last step in cosmic time, and the mid-step cosmic time |

Without expansion a = 1, T = t and the two sets coincide. The trace-free quadrupole of
the brief and of arXiv:2605.04487 is Q_ij = J_ij - delta_ij J_kk/3; the quadrupole-formula
power is (G/5c^5) Q'''_ij Q'''_ij with columns 56-61. The sums cost one more gather per
particle; they are formed only for the recorded states and the states one cycle before
them (`hist_dcycle`). The third derivatives are not formed after a step below 1e-6 of
the one before. Restart: nothing is stored; the sums of the dump's state are formed again
at the start of the continued run (T3d: the continued files are identical).

Touched outside the new file: `particles/particles.hpp` (members `nw_grp*`, three
methods), `particles/nrpic_newton.cpp` (`NrpicNewtonInit`: one call;
`NrpicNewtonInitialize` and `NrpicNewtonFinishStep`: one call each after the kick;
`NrpicNewtonWriteHistory`: one call at its end), `CMakeLists.txt` (one line).

Tests T3 and T4b (section 7).

### 2.3 Deformed ball and background in the test generator (A2, C3)

`problems/newton/make_ic.py ball` (the generator of the tests of the mode) gains:
`--axes S1 S2 S3` (positions x = centre + S xi of the lattice points xi), `--vgrad D1 D2
D3` (velocity D xi added), `--rotate SEED` (random rotation of the lattice before the
selection), `--background X0 X1 NB RHO` (species 1 at rest on an NB^3 lattice of the box
outside the deformed ball, mass RHO per unit volume). With any of them the centre of
mass and the net momentum of the ball are set to `--center` and `--velocity`, and the
JSON records `r_vol` (volume radius of the lattice ball), `r_mom`, `semi_axes`, the
rotation matrix, `nball`, `nbackground`. Without them the particle file is the one the
generator wrote before, byte for byte (T10 uses it).
For the Zel'dovich ball of Track A: S_i = a0 (1 - a0 lambda_i), D_i = H0 a0 (1 - 2 a0
lambda_i), `--radius 1 --mass 0.5`. The references of the track (`ellipsoid.evolve`,
cycloid) stay in the track's script; core's generator writes the particles and the
radii the references need.

Test T4a (section 7).

## 3. Which energy the history reports (answer to Track A)

[VERIFIED by reading `nrpic_newton.cpp`, `NrpicNewtonKick` and `NrpicNewtonWriteHistory`]
Column 6 is W = sum_p m_p Phi(x_p)/(2a) with Phi gathered at the particle by the
interpolation that also gives the force (Catmull-Rom, or the cubic spline with
`interp = bspline`), plus the external potentials in full. Column 7 is the mesh sum
int (rho - <rho>) Phi dV/(2a) of the deposited (and filtered) density.

Neither is an invariant of the scheme. With the deposit kernel S_d (the cloud) and the
gather kernel S_g, the derivative of column 6 with respect to a particle position is
(m_p/2) [grad(S_g * Phi) + grad(S_d * Phi~)](x_p), where Phi~ is the potential of the
density deposited with S_g; the force that the kick applies is m_p grad(S_g * Phi). The
two agree only if S_d = S_g. The defect is a truncation error where the density is smooth
on the mesh and of order one for structure below a cell, such as a sheet at its
crossing. [JUDGEMENT, derivation in the journal; the test below could have refuted it]

Test T7 (section 7) decides between "time integration" and "space discretisation" for
the drift at the crossing that the track reported.

## 4. Self-force of a compact object below the cell size (answer to Track D)

Stated in `newtonian_mode.md` sections 5.2 and 6 (amended in this package) with the
track's run ids and the map measured in test T8: a particle (or a clump smaller than a
cell) is pushed by the field of its own cloud; the force vanishes by symmetry at a mesh
vertex and at a cell centre, points away from the vertex (unstable) and towards the cell
centre (stable), and does not conserve the momentum of the object.
The fixed point mass `newton_pm_mass` is not deposited and has no self-force (T5).
The relativistic mode uses the same deposit and gather kernels, so a compact clump of
particles is expected to feel the same kind of force from its own smeared sources
[JUDGEMENT]; it has not been measured there [TO VERIFY]: the relativistic field is
evolved, not solved for, and the test needs constraint-solved data of a single compact
clump off a cell centre (the solver of package idsolve can provide them).

## 5. Multigrid on refined meshes

Test T6 (section 7).

## 6. Throughput on a card

One card job holds the checks of the new source on a card and the throughput cases
(`cases.py card`, list in `scratch/core/core-20261119-145326-d509829/card.list`): run
core-20261119-145346-2f89b86, Slurm job 4648, submitted 2026-11-19T14:53Z behind fifteen
queued jobs. Results: section 7 when it has run.

## 7. Tests of this package and their state

(filled in at the end of the session)
