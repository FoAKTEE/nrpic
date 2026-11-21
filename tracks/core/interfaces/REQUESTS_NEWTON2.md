# The Newtonian mode, second pass: requests of tracks B, A, D and core's deferred items

Work package newton2 of core, branch `core/newton-2` (started from `core/requests-adf`),
wave 3a, 2026-11-19; closed in batch 2b, 2026-11-21, after the merge of releases
core-v0.4 and core-v0.5 into the branch. Journal with the predictions and outcomes of every test:
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
| C1 | core, deferred in `REQUESTS_ADF.md` (D5 item 2): multigrid on refined meshes | TESTED on one static level (T6, T6b, T6c), see section 5 | The solve on the refined mesh is that of the uniform fine mesh where the matter is; a ball across the level boundary conserves momentum to 5e-5 M v, five times the uniform coarse mesh; the kick of the first test was the particle lattice, not the refinement. Open: more than one level, periodic refined meshes, adaptive refinement |
| C2 | the same item: throughput at 256^3 and 384^3 with 2e6 particles on a card | MEASURED, section 6 | Card job core-20261119-145346-2f89b86 (Slurm 4648) |
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

Tests T6, T6b and T6c (`newtonian_mode.md` 7.6, with the table of all eleven runs). The
moving, rotating cold ball of the first pass on the isolated 64^3 mesh, on that mesh
with one static level, and on the uniform 128^3 mesh [VERIFIED]:
- The solver converges on the refined mesh at every step (18 V cycles per step to
  rounding, as on the uniform meshes).
- With all matter on the fine level the refined run is the run of the uniform fine mesh
  (conservation errors equal to 3 parts in 10^4 in T6b, and within 8 per cent at the
  1e-5 level in T6c).
- A ball that crosses the level boundary, sampled with one particle per fine cell and
  direction: momentum change 5.06e-5 M v, centre of mass 2.60e-5 R, angular momentum
  9.6e-6, energy 3.58e-4 over 0.7 free-fall times, that is 4.6, 5.3, 2.6 and 4.5 times
  the uniform coarse mesh. The errors grow steadily while mass lies on both sides of
  the boundary; whether the solve at the interface or the deposit there causes them was
  not separated [TO VERIFY].
- The first test (T6) had shown a momentum kick of 1.1e-3 on the refined mesh, 44 times
  the uniform value, and my prediction (within ten times) failed. T6b and T6c traced it
  to the particles, not the mesh: a cold lattice with fewer than one particle per cell
  and direction is pushed as a whole by the self-forces of its particles (the uniform
  128^3 mesh shows the same 2.1e-3; the uniform 64^3 mesh with a lattice of two cells
  1.15e-2; with a lattice of the fine cell size 1e-5 on all three meshes). This is a
  property of the scheme that every user of a refined mesh, or of a mesh finer than
  the particle lattice, has to know: `newtonian_mode.md` section 6.
Open: more than one level; a refined periodic mesh; adaptive refinement in this mode;
the cubic cloud on a refined mesh; a fixed point mass on a refined mesh.

## 6. Throughput on a card

Card job core-20261119-145346-2f89b86 (Slurm 4648, ten cases, 252 s = 0.07 card-hours;
judgement core-20261120-220427-5d8547f) [VERIFIED]. 2e6 particles, cloud-in-cell, one
A100, seconds per step from the cpu time used over 20 cycles:

| mesh | solver | s per step | V cycles per step | peak card memory |
|---|---|---|---|---|
| periodic 256^3 | Fourier | 0.143 | - | 7.3 GiB |
| periodic 256^3 | multigrid, `newton_mg_tol = 1e-6` | 0.135 | 2.9 | 6.7 GiB |
| isolated 256^3 | multigrid, `newton_mg_tol = 1e-6` | 1.20 | 5.2 | 6.7 GiB |
| periodic 384^3 | Fourier | 0.436 | - | 22.6 GiB |
| isolated 384^3 | multigrid, `newton_mg_tol = 1e-6` | 6.00 | 5.6 | 18.2 GiB |

The Fourier solve costs as much as three V cycles and does not depend on the state;
the periodic multigrid figure is for particles at rest (three cycles from the warm
start; a collapsing configuration needs 13 to 19 cycles to rounding). The isolated
mesh is nine (256^3) and fourteen (384^3) times slower than the periodic one; where the
time goes was not profiled [TO VERIFY] (candidate: the multipole boundary, whose sums
run on the host). Smaller runs on a card: Track B's pancake at 64^3 with 262144
particles 13.5 ms per step; the embedded ellipsoid at 64^3 with 268400 particles and the
cubic cloud 3.3 s for 281 steps.
Card time of the package: 0.07 (job 4648) + 0.29 (job 4736, T6c and T4d at 64^3) = 0.36
card-hours, plus the third job (core-20261121-080215-df3af65, asked 25 minutes).

## 7. Tests of this package and their state

State on 2026-11-21. "Held" and "failed" refer to the predictions written in the
journal before each run; a failed prediction is a result, not a defect of the code,
unless the row says so. Processor runs with the pre-merge build (source c6293772) unless
marked; T11 and T12 with the build of the merged source (release core-v0.5 plus this
package, commit 67ca9ce1).

| Test | Subject | Runs (cases; judgement) | Outcome |
|---|---|---|---|
| T1 | Fourier solver against the multigrid solver, the numpy scheme, a mesh with radices 3, 5, 7 | core-20261119-144414-c629377; core-20261119-145129-e89a132 | held: 2.2e-15 of the box, 3.9e-16, 1.8e-12 |
| T2 | Track B's pancake against Zel'dovich, spectral symbol, n = 16, 32, 64 | core-20261119-150559-c1ff7ca, card core-20261119-145346-2f89b86; core-20261120-222443-f0bc314 | held: error at a = 2 lower by 17, 14.6, 7.7; within 13 and 6 per cent of `pm.py`. Failed: "mode minus `pm.py` below 5e-5 at a = 5" (6.6e-5 at n = 32) |
| T3 | group history on the exact pancake, tag range, restart | core-20261119-160919-c6a7279; core-20261120-222422-4ef2e80 | held (parallel-axis shift 3.9e-12, physical columns 7e-16, slab I and dI 340 and 129 times better with the spectral symbol, continued files identical). Failed on the low side: d3I rms 0.26 per cent, predicted 0.5 to 1.5 |
| T4a | deformed-ball generator against Track A's | core-20261119-152228-0ad3c0e; core-20261119-152928-6be4984 | held: equal in every value |
| T4b, T4c | embedded ellipsoid at 64^3 against Track B's ODE, Fourier and multigrid | core-20261119-162746-a02d334, core-20261119-162455-e05ffa1; core-20261120-222425-078bcc0 | failed in three of four parts: first minimum of the short axis +2.56 (Fourier) and +1.29 per cent (multigrid) against "within 2"; semi-axes off by up to 0.11 R_L against 0.03; solvers 1.25 per cent apart against 0.3. Not refuted (5 per cent) |
| T4d | the same with the kernels of T2, and against the cell size | card core-20261120-221835-4870ae5; core-20261121-081511-37acd23 | 64^3 with the cubic cloud: +0.92 per cent, held; "axes below 0.045" failed (0.047). 96^3 did not run (deck fault: MeshBlocks of 48^3). 96^3, 128^3, 256^3: card job core-20261121-080215-df3af65, PENDING |
| T5 | Track D's secondary infall onto `newton_pm_mass` | core-20261119-165257-61d4b78; core-20261120-222417-4ca3f76 | held: turnaround mass on the closed form at a/a_i = 2 and within 2.6e-4 at 4, both placements equal; within 0.7 per cent at all 45 snapshots |
| T6 | multigrid on a refined mesh, ball across the level boundary, lattice 0.0625 | core-20261119-160027-2c0c171; core-20261120-222437-191d56a | converges: held. Conservation within ten times the uniform mesh: failed (44 times in the momentum) |
| T6b | ball inside the fine region, lattice 0.0625 | core-20261119-165447-0b9cb1e; core-20261120-222429-8971bdb | refined equals uniform 128^3 to 3e-4: held. Momentum below 1e-4: failed (2.1e-3 on both), and the conclusion I had attached to that failure was wrong |
| T6c | the lattice against the cell size: coarser (64^3, lattice 0.125), fine (lattice 0.03125) inside and across the boundary | core-20261120-221737-74eed8b, card core-20261120-221835-4870ae5; core-20261120-222151-512227c, core-20261121-081457-ac86529, core-20261121-081505-3fa1046 | kick on a uniform mesh with a coarse lattice: held (1.15e-2; my range ended at 1e-2). No kick with a fine lattice on any mesh: held (1e-5). Ball across the boundary at most 3e-4: held (5.1e-5); "within five times the uniform mesh": 4.6, 5.3 (failed), 2.6 |
| T7 | Layzer-Irvine drift against the step | core-20261119-153710-13876fa; core-20261119-160023-99dc253 | held: unchanged at half the step (0.27 and 0.03 per cent) |
| T8 | self-force of one particle | core-20261119-152207-d4e656c; core-20261119-152742-a6810bd | held: slope 1.80 G m/dx^3 at a vertex, stable cell centre, 5.9 times smaller with the cubic cloud |
| T9 | throughput on a card (a measurement) | card core-20261119-145346-2f89b86; core-20261120-220427-5d8547f | section 6 |
| T10 | byte regression of the pre-merge build against the branch start and release core-v0.3 | core-20261119-152944-b2f41d3; core-20261119-160915-40df1d6 | held: 91 files identical to the branch start; against the release only `last_time` lines of four parameter dumps (correction of the branch start) |
| card twins | T1 and T3 on a card, pre-merge card build | card core-20261119-145346-2f89b86; core-20261120-220427-5d8547f | held: positions within 1.4e-15 of the box, K and W 7.3e-13, group columns 6e-13 |
| T11a | merged processor build against release core-v0.5, new options absent, sixteen set-ups | core-20261121-080231-a98a070, core-20261121-080229-0095e95; core-20261121-080954-30dec42 | held: 117 of 117 items identical |
| T11b | merged processor build against the files of the pre-merge build, Fourier solver and groups | core-20261121-080229-0095e95; core-20261121-080954-30dec42 | 50 result files identical; seven restart files differ in the 36 never-set bytes of the mesh header only (a class my prediction did not name) |
| T11c | card twins of T1 on the merged card build | card job core-20261121-080215-df3af65 | PENDING (Slurm 4777) |
| T12 | the example lines of READY with the published processor executable | core-20261121-081316-b153b46 | held: all run; the refined-mesh example equals the card run of T6c to 2.2e-13 over 20 steps |

Lines of shared source files touched by this package (for the merge into `core/nrpic`;
relative to tag core-v0.5): `athenak/src/CMakeLists.txt` two lines after
`particles/nrpic_newton.cpp`; `athenak/src/particles/particles.hpp` one block of 38
lines after `NrpicNewtonReadRestart` (members `nw_fft*`, `nw_grp*`, six methods);
`athenak/src/particles/nrpic_newton.cpp`: two calls in `NrpicNewtonInit`, one in
`NrpicNewtonInitialize`, the branch around `SolveSource` in `NrpicNewtonPotential`, one
call in `NrpicNewtonFinishStep`, one at the end of `NrpicNewtonWriteHistory`. Outside
`athenak/`: `python/nrpic/newton.py` (`scheme_fields` takes the symbol),
`docs/FORMATS.md` (one line for the group file), `problems/newton/` (two inputs, the
generator options, the README). The merge
of main (core-v0.4, core-v0.5) into this branch had two conflicts, both "each side
added lines at the same place" (`CMakeLists.txt`, `particles.hpp`), resolved by keeping
both; the branch now differs from tag core-v0.5 by this package only, so its merge into
`core/nrpic` should need no resolution.

Published: `/data/haiyangw/nrpic/scratch/core/exe/core_newton-2/` (`athena_cpu`,
`athena_gpu` of the merged source; `premerge/` the pair every test before T11 ran
with; COMMIT, SHA256SUMS, READY; copies of READY and COMMIT in
`tracks/core/analysis/newton2/`).

Not done: the judgement of card job core-20261121-080215-df3af65 (T11c, T4d at 96^3,
128^3, 256^3); the relativistic self-force test of section 4; a separation of the two
candidate terms at a level boundary (section 5); a profile of the isolated solver on a
card (section 6).
