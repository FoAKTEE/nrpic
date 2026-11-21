# Interface: refined meshes and horizons in periodic cosmology runs (work package cosmo-amr)

Owner core, branch `core/cosmo-amr`, wave 3a (2026-11-19); card check and scouting run
closed in wave 3 (2026-11-20, sections 4.5 and 7); **the fine-shape deposit of the linear
cloud was found wrong and corrected on 2026-11-21 (source 1548d49; sections 2.2, 4.6):
the executables published on 2026-11-19 (source 3c44b74) are replaced.** For Track A's threshold line in
the periodic box (decisions 0013, 0016 item 5). Triage of the track's requests:
`REQUESTS_A2.md` (same directory). Predictions and outcomes of every test:
`tracks/core/JOURNAL-cosmo-amr.md`. Test scripts: `tracks/core/analysis/cosmo_amr/`
(figures under `figs/` there); run manifests under `tracks/core/runs/`. Labels:
[VERIFIED] measured in the run named or read at the locator, [JUDGEMENT], [TO VERIFY].

Published executables: `scratch/core/exe/core_cosmo-amr/` (`athena_cpu`, `athena_gpu`,
`COMMIT`, `SHA256SUMS`, `READY`).

Every new option is read only if it is present in the input; without them the executable
reproduces release core-v0.3 byte for byte (section 6). Two things act by default and
change nothing in a run that was finite and ran without adaptive refinement in
`nrpic_cosmo` before: the guard (section 2.4), which only stops runs whose fields are no
longer finite, and the refinement function of `nrpic_cosmo` (section 2.1), which the
release did not have (adaptive refinement with `nrpic_cosmo` crashed).

## 1. What exists now

| Capability | Options | Source |
|---|---|---|
| Adaptive refinement in `nrpic_cosmo` (static refinement worked before) | `<amr_criterion0> method = user`, `<z4c_amr>`, `<particles_amr>` | `particles/nrpic_refine.cpp` |
| Coarse clouds sampled on fine leaf cells with their shape (linear cloud: leaf-cell integrals of the assignment function; quadratic and cubic: first order) | `<particles> deposit_fine_shape` | `particles/nrpic.cpp` (`NrpicDepositSources`, `NrpicTentCdf`) |
| Apparent-horizon finder in a periodic box; status of every search; files in the run directory | `<fastflow> diagnostics` | `z4c/fastflow.cpp` |
| Compact-object tracker in a periodic box; refinement around it across faces; tracker that stays in a uniform lapse | `<z4c> tracker_walk_tol` | `z4c/compact_object_tracker.cpp`, `z4c/z4c_amr.cpp` |
| Stop with a diagnostic when a field is not finite | `<z4c_guard>` | `particles/nrpic_guard.cpp` |
| Step limit from the coordinate speed of light | `<z4c> dt_lightspeed` | `z4c/z4c_newdt.cpp` |
| Constraint norms inside and outside spheres on any mesh | `<particles> region_*` | `particles/nrpic_region.cpp` |
| Exact restarts of adaptive `nrpic_cosmo` runs | none (automatic) | `particles/nrpic_refine.cpp` |
| Uniform shift of the homogeneous universe (tests) | `<problem> shift_x1..3` | `pgen/nrpic/nrpic_cosmo.cpp` |

Example inputs: `problems/cosmo_amr/peak_amr.athinput` (Track A's curvature peak with
adaptive refinement: `<particles_amr>`, `deposit_fine_shape`, `dt_lightspeed`,
`<z4c_guard>`, finder with `diagnostics`, `region_*`, restart output);
`problems/cosmo_amr/flrw_tracker.athinput` (homogeneous universe in moving coordinates:
`shift_x1`, tracker in a periodic box with `<z4c_amr> method = tracker`, `dt_lightspeed`;
the walk mode with `tracker_walk_tol` in its comments);
`problems/cosmo_amr/punc_box16.athinput` (Track A's puncture deck: the finder in a periodic
box, with `mesh/i?x?_bc = periodic` on the command line).

## 2. Options and outputs

### 2.1 Adaptive refinement in `nrpic_cosmo`

`nrpic_cosmo` enrols `nrpic::CosmoRefine` as the refinement function of
`<amr_criterion0> method = user`. It applies the criteria of `<z4c_amr>` first (`trivial`,
`tracker`, `chi`, `dchi`, `lohner`, the radii, exactly as `nrpic_cf` does), then those of
`<particles_amr>`:

| Option | Default | Meaning |
|---|---|---|
| `ppc_refine` | off | refine a MeshBlock in which a cell holds more than this many particles, n = sqrt(gamma) E dV / <m W> (deposited energy of the cell over the mean energy of a particle) |
| `ppc_derefine` | `ppc_refine/16` | a MeshBlock may be derefined where every cell holds fewer; must not exceed `ppc_refine/8` (fatal error otherwise) |
| `lapse_ratio_1`, `lapse_ratio_2`, ... | off | a MeshBlock of level l-1 is refined where min(alpha) < `lapse_ratio_l` times the coordinate-volume mean of alpha over the mesh |
| `chi_ratio_1`, ... | off | the same with the conformal factor chi (the cosmological form of `method = chi`: chi itself falls everywhere as 1/a^2) |
| `hysteresis` | 0.1 | a block of level l may be derefined only where the ratio exceeds (1 + hysteresis) times threshold l |
| `max_level` | finest level of the mesh | finest level these criteria ask for (relative to the root) |
| `verbose` | false | one line per check: flags, largest particle number per cell, smallest ratios |

A block is refined if any criterion asks for it and derefined only if every active
criterion allows it. With `<z4c_amr> method = trivial` that block has no say in
derefinement; its radii still set a minimum level around the origin. None of the criteria
refines the homogeneous universe (test T2, case L). Refinement levels do not sub-cycle in
time: one global step, set by the finest level (and by `dt_lightspeed`).

Memory: AthenaK allocates every field array for `<mesh_refinement> max_nmb_per_rank`
MeshBlocks. For the deck `peak_amr.athinput` (MeshBlocks of 16^3, four ghost cells) the
card holds 33 MiB per MeshBlock of the limit [VERIFIED, run core-20261120-220538-eafed07:
10,737 MiB at 300, 40,071 MiB at 1200, 66,043 MiB at 2000; 24,111 MiB at 2000 MeshBlocks
of 8^3], so an 80 GB card takes at most about 2400. The released particle restart file
`<name>.rst.prt` stores the previous sources for the whole limit as well: 1.1 MB per
MeshBlock of the limit in every restart file (2.23 GB at 2000), whatever the mesh
(section 8).

After a regrid the particle module rebuilds ownership, metric arrays and the sources on
the new hierarchy (`Particles::NrpicInitializeSources`, called by the adaptive driver);
new fine blocks are filled by the high-order prolongation of the evolved fields.

Restarts: the adaptive driver lets a block change again only `refinement_interval` cycles
after its last change, and restart files written inside the loop precede the regrid of
their cycle; neither is in AthenaK's mesh restart file. For `nrpic_cosmo` on an adaptive
mesh the counters and a "regrid pending" flag are written next to every restart file,
`rst/<basename>.NNNNN.rst.amr` (8 bytes `NRPAMR01`, int64 number of MeshBlocks, int64
cycle, int64 pending, then per MeshBlock in global order five int32: level, lx1, lx2,
lx3, cycles since its last change); a restarted run reads them and performs the pending
regrid before its first step. A restart file without `.amr` (written by an earlier
executable) starts the counters at zero, as upstream AthenaK does. Test T11.

### 2.2 Fine-shape deposit

`<particles> deposit_fine_shape = true` (default false): where a cloud lives on a level
coarser than the leaf cells it covers (level cap, `deposit_adaptive`), the weight of each
lattice cell of the cloud is distributed over its leaf cells with the shape of the
assignment function instead of uniformly.

- Quadratic and cubic clouds (`tsc`, `pcs`): to first order about the centre of the
  lattice cell, w + (dw/dx)(x - x_c), with the analytic slope of the assignment function.
- Linear cloud (`cic`), **changed on 2026-11-21 (source 1548d49)**: a leaf cell gets the
  integral of the assignment function over it (the tent of half-width one lattice cell
  centred on the particle), plus the same amount in every leaf cell of the lattice cell
  such that they sum to the weight of the lattice cell. The tent reaches half a cell into
  the lattice cells beside the two of the cloud, so with the option the linear cloud
  visits 4^3 lattice cells instead of 2^3; the outer ones carry no weight, and their leaf
  cells get shares that sum to zero. One consequence: a cloud in a coarse MeshBlock next
  to a finer one now changes leaf cells of the fine block even when every cloud sits on
  the finest level it can (T1b).

Properties, all three shapes [VERIFIED in the tests named, section 4.6]: every lattice
cell keeps its weight, so the conservation identity is unchanged (T1, T1b); a regular
lattice stays uniform (T2, T2b); the leaf cells follow the particle continuously (T17b);
a smooth density is second-order accurate on the leaf cells (T19c; T3 for the quadratic
cloud in an evolved wave). No limiter: the weight of a single cloud can be negative at
its edge (linear cloud, leaf cells half the lattice cell: at most 1/16 of the particle
per direction), so in a sparse distribution leaf cells can carry negative E (T1b, 4096
random particles: down to -0.10 of E_max with the linear cloud, -0.07 quadratic, -0.04
cubic). Used only where the leaf cells are at most 32 times finer than the cloud's
cells; beyond that the released uniform spreading is used.

**The first form of the option for the linear cloud was wrong** (source 3c44b74, the
executables published on 2026-11-19): it used the first-order form with the slopes
(+1, -1) of the tent. The tent has its kink at the particle, so the slope of a lattice
cell flips when the particle passes the centre of that cell, and a quarter of the
particle changes its leaf cell at once (T17: the shares of the two halves go from
0.625, 0.375 to 0.375, 0.625). On a regular lattice the flips cancel, which is all that
T2, T5 and the plane wave T3 (quadratic cloud) exercised; on any other lattice the leaf
cells are wrong at first order and do not converge (T19c: rms departure from a smooth
density 0.016 and 0.013 at 8 and 16 root cells per wavelength, against 0.0061 and 0.0016
with the corrected form). It made the one-cycle jump of the Hamiltonian constraint in
the scouting run (T10e, T10f; section 7). Affected results, linear cloud with
`deposit_fine_shape` on particles that are not a regular lattice at rest: the `ladder`,
`chi`, `ppc` and `lohner` cases of T9 and the `ladder` case of T14 (repeated: T9b, T14b),
and the scouting run T10b (section 7; not repeated).

When it helps [VERIFIED in the tests named]: on sources without the binomial filter it
removes the staircase of the uniform spreading (T3b: Hamiltonian constraint on the patch
20 times smaller; T19c: 13 times closer to a smooth density at 16 cells per wavelength).
On data built with the source filter at the root cell size, which the track's present
data are, it does not help at a regrid: largest relative constraint after the regrid
0.0125 with it against 0.0072 with the uniform spreading (T9b), and T10F_PLACEHOLDER
Independent of the leaf cells: one particle per root cell on a lattice stretched by 30
per cent carries a modulation of 7 per cent rms at the cell scale through the linear
cloud itself (2 sinc^2(pi h/d) for particle spacing d; 3 per cent with the quadratic
cloud; T19), which only more particles per cell or the source filter remove.

### 2.3 Horizon finder and tracker in a periodic box

- `fastflow.cpp`: in a periodic direction every surface point is mapped into the mesh
  before its interpolation stencil is built (a point inside the mesh keeps its
  coordinate bit for bit). The centre of the finder may lie in any image; the surface
  may cross faces and corners. The release leaves such points out of the surface
  integrals without a message (T4: on a face it reports a horizon 30 per cent too light).
- `<fastflow> diagnostics = true` (default false): `<basename>.horizon_status_<n>.txt`,
  one line per search: 1 cycle, 2 time, 3 found (0/1), 4 reason, 5 flow iterations,
  6 area of the last surface, 7 its area mass, 8 mean radius, 9 smallest radius, 10 mean
  expansion, 11 smallest |mean expansion| reached, 12 surface points outside the mesh,
  13-15 centre, then `# reason in words`. Reasons: 0 found, 1 area not finite, 2 mean
  expansion not finite, 3 mean expansion above `hmean_tol`, 4 mean radius negative,
  5 area mass below 1e-10 (surface shrank to a point), 6 iteration limit. The summary
  file is unchanged (after a failed search it repeats the values of the last success, or
  NaN): read the status file to know whether a line is new.
- `hmean_tol_<n>` (released option, unchanged) is compared with the surface INTEGRAL of
  the expansion, `sum dA H` (`fastflow.cpp`, `hmean = integrals[ihmean]`), not with its
  mean. In a cosmological box the proper area of a coordinate sphere grows as a^2: with
  the value 100 of Track A's decks every search of the scouting run ended at its first
  flow iteration with reason 3 (sphere of coordinate radius 2: area 2.5e4 to 6.6e4,
  integral 1.3e3 to 1.8e3; section 7). Set it out of the way (the example input now has
  1e30); the other reasons still end a flow that fails.
- The summary, verbose, grid and Ylm files of the finder and the tracker file
  `<basename>.co_<n>.txt` are opened at their first record, i.e. in the `-d` directory
  (the release opens them in the start directory).
- Tracker (`<z4c> co_<n>_*`): its position is mapped back into the box after every update,
  so it follows its object across a face (the release stops with "couldn't find the
  compact object"); `<z4c_amr> method = tracker` measures the distance to the nearest
  image, so the refined region continues across the face (T5).
- `<z4c> tracker_walk_tol = eps` (mode `tracker_mode = walk`, which follows the minimum
  of the lapse): move only to a neighbour whose lapse is below (1 - eps) times that of the
  own cell. Without it the first of equal neighbours wins, and in a uniform lapse the
  tracker drifts one cell per step (T13).

### 2.4 Guard and step limit

Guard, input block `<z4c_guard>` (every option read only if present):

| Option | Default | Meaning |
|---|---|---|
| `stop_nonfinite` | true | stop when a value of the evolved spacetime fields is not finite |
| `stop_chi_nonpositive` | false | also stop when chi <= 0 in a cell (off by default: chi undershoots next to a puncture and such runs survive) |
| `stop_dt_below` | off | also stop when the step falls below this value |
| `stop_no_particles` | false | also stop when a run that started with particles has none left |
| `check_dcycle` | 1 | cycles between checks |

The check runs on the initial data and after every cycle, before the outputs of that
cycle. On a stop: the diagnostic is printed and written to `<basename>.guard.txt` (time,
cycle, step, reason, last check that passed, number of non-finite values per variable,
the first such cell with MeshBlock, level, position and all field values, particles
left); the driver leaves its loop, `Driver::Finalize` writes every output once (the
failed state: for a post-mortem; its restart file cannot be continued), and the
executable exits with status 3. Under MPI the counts per variable and the first cell are
those of rank 0 [JUDGEMENT; the processor and card builds of this package have no MPI].

`<z4c> dt_lightspeed = f` (default 0, off): the step is also limited by
`cfl f min(dx_d / c_d)`, `c_d = alpha sqrt(gamma^dd) + |beta^d|` from the evolved fields,
evaluated at the end of every step; never above the released `cfl dx`. In the
conformal-time gauge of the homogeneous universe c = 1 up to the time-integration error
of the fields (T7: 2.9e-6, so the step is about 1e-6 shorter than without the option).

### 2.5 Region norms

`<particles> region_dcycle = n` (default 0, off): `<basename>.region.hst` every n cycles,
on any mesh, each leaf cell weighted by its proper volume sqrt(gamma) dV. Options:
`region_x1`, `region_x2`, `region_x3` (centre, default 0), `region_radius1..4`
(coordinate radii of spheres), `region_horizon = n` (one more sphere, centred on horizon
finder n, of radius `region_horizon_factor` (default 1) times the mean radius of its last
surface; zero until a horizon is found). Distances use the nearest periodic image.
Columns: time, ncycle, V (proper volume), mean_K, mean_alpha_V (proper-volume mean),
mean_alpha_coord, H2 = sqrt(<H^2>), E2 = sqrt(<(16 pi E)^2>), E1 = <E>; then for every
sphere `radius_s<k>`, and inside and outside it `V`, `H2`, `E2`, `E1`, `Hmax`. The bound
of the track's threshold definition is `H2_out/E2_out` of the horizon sphere.

### 2.6 Uniform shift (tests)

`<problem> shift_x1`, `shift_x2`, `shift_x3` in `nrpic_cosmo` (default 0): the
homogeneous universe in coordinates moving with the constant velocity -beta^i (the
initial shift; with a frozen shift, `shift_*` of `<z4c>` zero, it stays). Lets a lattice,
a tracker and a refined patch cross the faces in tests.

## 3. Lines of shared files touched (relative to `main` at 27b2ced9)

New files: `particles/nrpic_cosmo_ext.hpp`, `particles/nrpic_refine.cpp`,
`particles/nrpic_guard.cpp`, `particles/nrpic_region.cpp` (three lines in
`CMakeLists.txt`). Hooks in shared files (line numbers of the branch tip):

| File | Where | What |
|---|---|---|
| `driver/driver.cpp` | include; `Initialize` after the scalar-field start-up (5 lines); `Execute` loop condition (guard on the initial data, 3 lines), after `ncycle++` (guard, 3 lines), after `AdaptiveMeshRefinement` (1 line); `Finalize` message (2 lines) | guard, pending regrid, refinement counters |
| `main.cpp` | include; `return` | exit status of the guard |
| `outputs/restart.cpp` | include; one line after `NrpicWriteRestart` | `<file>.rst.amr` |
| `pgen/nrpic/nrpic_cosmo.cpp` | include; 4 lines at the top of `NrpicCosmology`; `shift_x1..3` (13 lines) and the shift in the initial data (1 line) | refinement function, counters on restart, uniform shift |
| `particles/nrpic.cpp` | include; `NrpicInit` (5 lines); new function `NrpicTentCdf` before `NrpicDepositSources`; in `NrpicDepositSources`: `fine_lin`, `nx`, `ns` after `fine_shape` (5 lines), slopes `gs` of the three clouds and `sdl`, the loop over the lattice cells (`ns` instead of `nb`, `own`; one `continue` in the kd <= 0 branch and one before the uniform spreading), the fine-shape branch (about 70 lines inside the kd > 0 branch) | fine-shape deposit, region options |
| `particles/nrpic_io.cpp` | `NrpicStartup` (3 lines), `NrpicDiagnostics` (3 lines) | region records |
| `particles/particles.hpp` | `NrpicOptions::deposit_fine`; struct `NrpicRegionOptions`; 4 members of `Particles` | |
| `z4c/z4c.cpp`, `z4c/z4c.hpp` | include; constructor (6 lines); 2 members, 1 method | `dt_lightspeed`, guard options |
| `z4c/z4c_newdt.cpp` | include; `NewTimeStep` (5 lines); new function `LightSpeedTimeStep` | step limit |
| `z4c/z4c_amr.cpp` | `RefineTracker` (27 lines) | nearest image |
| `z4c/compact_object_tracker.{hpp,cpp}` | constructor, `OpenOutput`, destructor, `EvolveTracker` (walk tolerance, mapping into the box), `WriteTracker` | |
| `z4c/fastflow.{hpp,cpp}` | constructor (periodic flags, status file name), `OpenOutput`, `Write` (status line), `Find`, `MetricInterp` (mapping), `FastFlowLoop` (reasons) | |

## 4. What is tested

Processor runs unless stated; NEW = the processor executable of this branch, REL = release
core-v0.3 (`.work/build_cpu_v03/src/athena`). Run ids of the form
`core-20261119-HHMMSS-<commit7>`. Every test has its figure (looked at) and its
prediction in the journal, written before it ran; failed predictions are listed in
section 5. The rows of this table are runs with the sources 901d8b3 and 3c44b74; the tests
of 2026-11-21, among them the repeats with the corrected fine shape of the linear cloud
(source 1548d49), are in section 4.6.

| Test | What | Run | Result [VERIFIED] |
|---|---|---|---|
| T0 | regression, options absent: geodesics (two pushers), deposit on a static mesh, East et al. data, Oppenheimer-Snyder on a static mesh with restart, homogeneous universe, puncture with finder on a static periodic mesh | `-154346-64067cd` | every output file byte-identical to REL, restart files included |
| T1 | deposition identity on a refined periodic mesh (4096 random particles, levels 0-2, faces between levels; cic/tsc/pcs; cloud level finest/root/adaptive; uniform and fine-shape spreading) | `-154351-64067cd` | |int_E/sum mW - 1| at most 1.7e-14, momentum 1.1e-16 relative, in all 22 cases; with the source filter: 4e-4 to 5e-4 on the refined mesh (filter not conservative across levels), 4.4e-16 at t = 0 on the uniform mesh |
| T2 | homogeneous universe with refined patches: interior, faces and corner, adaptive (tracker), lohner plus `<particles_amr>`, eight particles per root cell with fine clouds, the same drifting through the patch | `-151654-e01b46e` | chi and E uniform to 1.6e-14 and 4.2e-14; |H_max - H_mean| at most 9.7e-13; alpha_max equal to the uniform run to 3.3e-15; lohner plus `<particles_amr>` creates no MeshBlock |
| T3 | linear plane wave (test B of arXiv:1904.07841) with a refined patch | `-161527-4480f58` (first run `-154357-64067cd` void: six-digit tables) | section 4.1 |
| T3c | homogeneous universe, clouds of the three shapes on the finest level of a patch | `-164329-589b34c` | cic uniform to 2e-15; tsc 0.35, pcs 0.15 (released deposit, section 8) |
| T3d | the same with the density-adaptive cloud level (`deposit_adaptive`), three shapes, uniform and fine-shape spreading | `core-20261120-223058-bec243b` | adaptive level equal on both sides of the boundary (`deposit_ppc = 2`): uniform to 6.4e-15 for cic, tsc and pcs; adaptive level following the mesh level (`deposit_ppc = 0.5`): cic 2e-15, tsc 0.35, pcs 0.15, as T3c |
| T16 | the finder's `hmean_tol` on Track A's S1 data at t = 0 (uniform mesh, two cycles) | `core-20261120-222814-0b2b259` | with 100 (the track's decks) every search ends at its first iteration with reason 3 (surface integral of the expansion 184); with 1e30 the flow runs (three iterations, reason 4: no trapped surface in these data) |
| T4 | finder in a periodic box: lattice of unit punctures, hole at the centre, on a face, at a corner, finder centre in other images | `-152106-9332260` | M = 0.9915211031 in every case, equal to 3.3e-16; REL: no horizon for a centre one period away, a wrong one (M = 0.695) on a face; summary file in `-d` |
| T5 | tracker moving across a face with refinement following it, `dt_lightspeed` | `-151654-e01b46e` | tracker within 1.0e-13 of x = 2.5 + 0.5 t mapped into the box; refined blocks on both sides of the face; homogeneity 1e-13; step 0.25 dx/1.5 to 1e-13 |
| T6 | guard at a Courant number of 1.5 | `-151654-e01b46e` | NEW stops at cycle 18 with status 3 and `flrw.guard.txt`; `stop_chi_nonpositive` the same cycle; guard off and REL run to `nlim` (status 0) after losing every particle |
| T7 | `dt_lightspeed` | `-151654-e01b46e` | conformal-time lapse: dt c_max/(0.25 dx) = 1 to 2e-15 (c_max - 1 = 2.9e-6 of the fields); lapse 2/3: 1 to 3.4e-15 while the step without the option exceeds the light-speed limit by a factor 3.2 at t = 1 |
| T8 | region norms | `-151654-e01b46e` | V_in + V_out = V to 4.6e-13; V and mean K equal the history of the module to 2.4e-14; max(Hmax_in, Hmax_out) equals the constraint statistics exactly; V_in of a sphere of six root cells within 1.2 per cent of its volume |
| T9 | adaptive refinement on Track A's peak (32^3, mu = 0.5): lohner (NEW and REL), lapse ladder with fine-shape and uniform spreading, chi ratio, particles per cell | `-154404-64067cd` | REL: segmentation fault at the first check; NEW: no crash; the central eight blocks refined at cycle 4 by each `<particles_amr>` criterion; particle number and rest mass unchanged; identity 3.2e-14; largest relative H after the regrid 0.0116 (fine shape), 0.0072 (uniform spreading), 0.020 (lohner, 400 blocks) |
| T11 | restarts on adaptive meshes | `-161309-f797997` (analysis `-162944-d87b113`; first attempt `-155740-3c44b74`, script errors) | section 4.2 |
| T12 | the published executable gives the bytes of the tested one | `-162949-d87b113` | section 4.3 |
| T13 | tracker in mode walk, `tracker_walk_tol`; the example input `flrw_tracker.athinput` | `-161316-f797997` | section 4.4 |
| T0b | T0 with the published processor executable | `-161756-44db4b5` | every output file byte-identical to REL |
| T15 | guard options `stop_dt_below`, `stop_no_particles`, `check_dcycle`; `region_horizon` on a found horizon | `-164133-228c956` | stops at cycles 1, 20, 20 with status 3 and the right reason; the horizon sphere has the finder's mean radius 0.4778 from the first search on, V_in + V_out = V |
| T14 | card check of the published card executable: decks of T2 (U, S, A, M, G) and T9 (ladder) on a card | `-161748-75c2405` (Slurm job 4664; analysis `core-20261120-220634-d26a0b6`) | section 4.5: the card reproduces the processor runs to round-off |
| T10 | scouting run of Track A's S1 with adaptive refinement, on a card | first attempt `-150507-8224d72` died at start (exit 139); debugging `core-20261120-220538-eafed07`; the run `core-20261120-220816-09f6f79` (analysis `core-20261120-222419-a1850d2`) | section 7 |

### 4.1 T3, plane wave with a refined patch

Test B of arXiv:1904.07841 as in `cosmo/TESTLOG.md` (delta = 1e-7, 32 cells per
wavelength, eight particles per cell, quadratic cloud), slab 32 x 8 x 8, to t = 2 (a = 4),
all cases at the step of level 1; static level 1 on L/4 < x < 3L/4 (or across the face).
Run core-20261119-161527-4480f58:

| Case | chi amplitude / U | rms residual of chi | rms residual of E | H/(16 pi dE) at t = 0 on the patch |
|---|---|---|---|---|
| U uniform | 1 | 2.8e-7 | 2.2e-7 | 0.0010 |
| S clouds at the root, uniform spreading | 1.005 | 3.2e-4 | 0.026 (staircase) | 0.057 |
| Sf the same with `deposit_fine_shape` | 1.002 | 1.6e-4 | 2.5e-4 | 0.0029 |
| P Sf with the patch across the face | 1.002 | 1.6e-4 | 2.5e-4 | 0.0018 |
| Sx quadratic clouds on the finest level | wrong: structure at the patch boundaries 28 times the wave in E | | | 37 |
| Uq, Sq, Sfq with the source filter (data built with it) | 1, 0.9993, 1.001 | 3.5e-7, 9.4e-4, 1.9e-4 | 2.0e-7, 1.0e-3, 1.2e-3 | 0.0011, 0.0029, 0.0043 |

Phases within 3e-6 rad of U everywhere except Sx. Without the filter the fine-shape
deposit removes the staircase (constraint on the patch 20 times smaller); with the filter
both spreadings are limited by the filter acting at each level's cell size, and the
uniform spreading is slightly better (the same order as on the peak, T9).

### 4.2 T11, restarts

Ten cases, each run uninterrupted with restart files and restarted from one of them,
with the executable of T1-T9 (OLD, counters not restored) and the published one (NEW):
T5's moving tracker restarted inside the loop 2 cycles before a regrid (M_r14), at a
check cycle (M_r28), from the end of a run stopped at the regrid cycle (M_f16), from a
file written inside the loop at the regrid cycle (M_i16); T9's peak at cycle 6 (P_r6),
from the end of a run at the regrid cycle 4 (P_f4), inside the loop at cycle 4 (P_i4);
the uniform universe with the finder (U_r8), T2's static patch (S_r8), the uniform mesh
with the light-speed step (C_r8).

- Regrid schedule: with NEW the MeshBlock count equals the uninterrupted run at every
  cycle in all ten cases. With OLD it does not in M_r14 and M_i16 (the regrid of cycle 16
  comes at cycle 20) and P_i4 (the regrid of the restart cycle is skipped; field
  departure 0.81).
- Bitwise: identical on the uniform mesh (U_r8 with the finder files, C_r8) and for every
  restart made right after a regrid (M_f16, P_f4, P_i4). Restarts inside a stretch
  without regrid on a refined mesh, static or adaptive, agree to round-off only: largest
  departure 1.6e-14 in E, K, proper volume (M), 3.3e-10 in alpha_min and 5.8e-10 in K_max
  (P, a strongly evolving peak), 7.8e-11 (S), and up to 6.3e-9 in the norm H2 of the
  region file, a residual measured relative to itself. [JUDGEMENT] the source is the
  ghost zones at fine/coarse boundaries, which the running code carries from the last
  stage and a restart (or a regrid) recomputes from the stored fields.
- A restarted run writes one tracker and one finder record at the restart time; they are
  identical to the uninterrupted run's. The tracker file is truncated on restart
  (upstream behaviour): keep the files of every segment.

### 4.3 T12

The published processor executable reran the 43 cases of T1 (22), T2 (16) and T9 (5)
from their saved decks: same exit status everywhere; every output file byte-identical,
except the finder status file of T2's U, whose first column now holds the cycle instead
of the Runge-Kutta stage (header label "1:cycle"); its other columns are identical. Every
number of T1, T2 and T9 therefore holds for the published executable.

### 4.4 T13

Homogeneous universe, tracker in mode walk: without the tolerance it moves one cell per
step along (-1, -1, -1) (the first of equal neighbours), and this branch maps it back
into the box at the face (16 cycles, exit 0), while the release stops with "couldn't
find the compact object!" (exit 1) after 13 records. With `tracker_walk_tol = 1e-6` it
stays in its cell. On Track A's peak (uniform 32^3, cell 0.625) it walks three cells down
the lapse to one of the eight cells around the centre and stays there for six cycles;
without the tolerance it hops among those eight equal cells. At cycle 9 both moved one
cell outward diagonally ([TO VERIFY]: the lapse of these data nearly relaxes by then and
its minimum leaves the centre; no field dump was written). The example input
`flrw_tracker.athinput` runs as published (12 cycles, tracker at 2.5 + 0.5 t).

### 4.5 T14, the card executable against the processors

The published card executable ran the decks of T2's U, S, A, M, G and T9's ladder (run
core-20261119-161748-75c2405, 11 s of card time), compared record by record with the
processor runs (analysis core-20261120-220634-d26a0b6, figure `fig_t14_card`) [VERIFIED]:

| Case | On the card | Against the processor run |
|---|---|---|
| U, S, A (homogeneous universe: uniform, static patch, adaptive patch) | chi uniform to 1.3e-14, E to 2.2e-14 | alpha_max equal to 1.1e-15 at every record; same MeshBlock counts |
| M (tracker across the face, refinement following it, `dt_lightspeed`, fine shape) | 118 records | MeshBlock count equal at every record (27, 34, 41, 34); tracker position within 4.4e-16, record times within 6.7e-16 |
| G (guard at a Courant number of 1.5) | status 3, `flrw.guard.txt` | stop at cycle 16 instead of 18: the two unstable runs agree to 7e-15 up to record 8 and then part by a factor of about a hundred per record (rounding amplified by the instability) |
| ladder (peak, lapse ladder, fine shape) | 32,768 particles and rest mass unchanged, identity 2.2e-16 | MeshBlock counts identical (64, then 120 after the regrid of cycle 4); Hr_max within 3.9e-12, H_max within 9.8e-12, lapse extremes within 1.4e-14 at all 11 records |
| region norms of U, S, A, M | | every non-residual column within 6.7e-13 |

So the refinement function, the tracker, the light-speed step, the fine-shape deposit, the
region norms and the guard give on a card what they give on the processors, to round-off.
Not compared on a card: the finder on a known horizon (T4, T15), the walk tracker (T13).
A restart of an adaptive run on a card and the finder on found surfaces: T10c (section
7). The card executable of 1548d49: T14b (section 4.6).

### 4.6 Tests of 2026-11-21: the fine shape of the linear cloud, the repeats, the finder

PUB = the processor executable published on 2026-11-19 (source 3c44b74), NEW2 = the
processor build of source 1548d49 (`.work/build_cpu_b`), published on 2026-11-21. Run ids
`core-20261121-HHMMSS-<commit7>` unless written in full. All [VERIFIED] in the run named.

| Test | What | Run | Result |
|---|---|---|---|
| T10e | where the constraint jump of the scouting run comes from: the S1 data to t = 3.5 without refinement (u5), as the scouting run (a5), with the uniform spreading (a5c), with every cloud on the root level (a5r); PUB | `core-20261120-222729-6cfac05` | u5: smooth, largest relative H 0.020; a5: 0.0099, 0.066, 0.159 at three consecutive cycles around t = 2.946, twenty cycles after the regrid and with no change of the mesh; largest 0.169; a5c: no jump, largest 0.039; a5r equal to a5 in every digit (the adaptive cloud level is the root to t = 3.5) |
| T17, T17b | is the deposit continuous in the particle position: one particle moved through the centre of a root cell inside a level-1 patch, clouds on the root level; three shapes, uniform and fine-shape spreading; twelve offsets | PUB `-030438-e52cdb3`; NEW2 `-030910-0c046a7` | PUB, linear cloud with fine shape: the shares of the leaf cells jump by 0.25 of the particle at the cell centre. NEW2: continuous (1.0e-6 for a move of 2e-6 cells), shares equal to the integral form to 9.4e-16, smallest share -1/16. Quadratic and cubic clouds and the uniform spreading: continuous, the same numbers with both executables |
| T19, T19b, T19c | a smooth density (lattice displaced along x, contrast 30 per cent, 8 and 16 root cells per wavelength) on the leaf cells of a patch, clouds on the root level; 1, 4, 16 particles per root cell along x | `-031145-ffc12b3`, `-031330-4d924b0`, `-031446-5b1fdcd` | sixteen particles, rms departure at the two resolutions: uniform spreading 0.041, 0.021 (first order); integral form 0.0061, 0.0016 (second order); quadratic cloud 0.0105, 0.0027; first-order form of PUB 0.016, 0.013 (does not converge). With one and four particles per cell the modulation of the lattice through the cloud is what is measured (7 per cent rms; 1.7 per cent at most), and the predictions of convergence failed (section 5) |
| T0c | regression, options absent, NEW2 against REL (the seven set-ups of T0) | `-031231-75fa120` | every output file byte-identical, restart files included |
| T1b, T18a | T1 with NEW2; its bytes against T1 | `-031032-614792a`, `-032122-0f3369f` | identity at most 1.65e-14 (energy), 1.1e-16 (momentum) in the 18 unfiltered refined cases; 18 of 22 cases byte-identical to T1; the four that differ are the linear cloud with fine shape |
| T2b, T18c | T2, T5, T6, T7, T8 with NEW2; bytes against T2 | `-031920-494ac64`, `-032946-d860245` | homogeneous to 1.6e-14 (chi) and 4.2e-14 (E) with every patch; the lattice drifting through the patch with fine shape (M): 2.7e-14, 9.6e-14, tracker within 1.0e-13; 18 of 20 cases byte-identical to T2 (M differs at round-off; U only in the first column of the finder status file, section 4.3) |
| T9b, T18b | T9 with NEW2; bytes against T9 | `-031701-cff3117`, `-032213-1d17e30` | MeshBlock histories, particle number, rest mass, identity (3.2e-14) as T9; largest relative H after the regrid 0.0125 with fine shape (first-order form of T9: 0.0116), 0.0072 with the uniform spreading; the uniform-spreading and the release case byte-identical to T9 |
| T10f | case a5 of T10e with NEW2 | `core-20261121-030904-1548d49` | T10F_ROW |
| T10c | the last stretch of the scouting run again, from its restart file at t = 10, with four finder surfaces that can flow; card, published card executable of 3c44b74 | `core-20261121-025527-eb8e6b7` (Slurm job 4755, 264 s; analysis `-032345-839e721`) | section 7 |
| T14b | card check of the card executable of 1548d49 on the decks of T2b (U, S, Sf, A, M, G) and T9b (ladder) | `core-20261121-032510-c83f904` (Slurm job 4760) | T14B_ROW |

## 5. Predictions that failed (details in the journal)

- T2: "H_max = H_mean to 1e-10 relative": H itself is 1e-15 at t = 0; the absolute
  spread, 9.7e-13, is the meaningful bound (mis-specified prediction).
- T7 (a): with `dt_lightspeed = 1` in the conformal-time gauge the step is not equal to
  the step without it: the fields give c = 1 + 2.9e-6.
- T8: V_in + V_out = V to 4.6e-13, not 1e-13 (rounding of plain sums over 2e4 cells).
- T1: the filtered energy integral on a uniform mesh departs from the particle sum by
  4.7e-3 after four cycles (4.4e-16 at t = 0): the filter conserves the coordinate
  integral of E, the record is the proper-volume integral, and sqrt(gamma) is no longer
  uniform once random particles have moved the metric.
- T4: the release does not report "no horizon" for a hole on a face, but a wrong one.
- T5: "with REL the run stops at the crossing" could not be tested: the release has no
  `shift_x1` (its tracker stood still) and cannot refine adaptively with `nrpic_cosmo`;
  T13 showed the release's stop at a face with the walk tracker instead.
- T11: "every record after a restart identical as text": only on a uniform mesh and
  right after a regrid; elsewhere on refined meshes the restarted run agrees to round-off
  (section 4.2). The regrid schedule, the point of the fix, is identical.
- T3: Sx (quadratic clouds on the finest level) is not "within 1 per cent of U"; T3c
  traced it to the released deposit (section 8). The first T3 run was void (tables with
  six digits for a wave of relative amplitude 1e-7).
- T3c: the non-uniformity of tsc and pcs clouds at a level boundary is 15 to 35 times
  larger than the 1e-2 I predicted.
- T13: without the tolerance the walk tracker does not follow the same path as with it on
  the peak: it hops among the eight equal central cells.
- T15 and T11 figures: one panel each lacks a curve or clips a label (script errors noted
  in the journal); the numbers come from the summary files.
- T14: "G stops at cycle 18 on the card": it stops at cycle 16; the stop cycle of an
  unstable run is not reproducible between a card and a processor (section 4.5).
- T10d: "the crash of T10 at start repeats with the published card executable": it did
  not, in five variants (section 7).
- T10: "fine levels appear only as the lapse falls (tau > 5)": level 1 comes at t = 2.20
  (the lapse ratio of these data passes 0.9 there); "the first bad cell lies within 0.6/k
  of the centre": it lies at 0.637; "without a horizon" was not tested, the finder of the
  deck could not search (section 7).
- T10e: "with the uniform spreading the same jump within a factor two" (my reading had
  been that the source filter at each level's cell size makes the jump): there is no
  jump with the uniform spreading, and the largest relative constraint is 4.3 times
  smaller. The jump belonged to the fine-shape deposit of the linear cloud (T17).
- The design note of 2026-11-19 for `deposit_fine_shape` ("the slopes of a regular
  lattice cancel", "second-order accurate") was tested on regular lattices only; for the
  linear cloud it was wrong on every other lattice (section 2.2).
- T19 and T19b: "uniform spreading first order, integral form second order" with one and
  with four particles per root cell: nothing converges with one (7 per cent rms at both
  resolutions) and the integral form sits at 0.0072 and 0.0075 with four. The lattice of
  spacing d is modulated by 2 sinc^2(pi h/d) through a tent of half-width h, which I had
  left out (T19) and then bounded at the ends of the range of d only (T19b). T19c, with
  sixteen particles, shows the orders.
- T9b: "largest relative constraint after the regrid at most the 0.0116 of T9": 0.0125.
  On these filtered data the corrected form is not better at the regrid than the old one.
- T10c: the restarted run on the card agrees with the uninterrupted one to 2e-6 to 1e-2
  after 32 cycles, not to round-off as on the processors (T11); not separated from the
  run-to-run differences of card runs in a stretch that amplifies them (section 7).

## 6. Regression

T0 (run core-20261119-154346-64067cd) and T0b (run core-20261119-161756-44db4b5): with
the new options absent the executable of the tests (source 901d8b3) and the published
processor executable (source 3c44b74) are byte-identical to release core-v0.3 in every
output file of seven set-ups (geodesics with both pushers, deposit on a static mesh,
East et al. data, Oppenheimer-Snyder on a static mesh, homogeneous universe, puncture
with finder on a static periodic mesh), restart files included. T12 shows that the
published executable reproduces the tested one on the cases of T1, T2 and T9.

T0c (run core-20261121-031231-75fa120): the same for the processor build of source
1548d49, published on 2026-11-21. T18a, T18b, T18c: of the 48 cases of T1, T2 and T9
repeated with it, 38 are byte-identical to the runs of 2026-11-19; the ten that differ
are the nine with the linear cloud and `deposit_fine_shape` on particles that are not
at rest on the cell centres (the purpose of the change), and one finder status file
whose first column had changed before (section 4.3).

## 7. Scouting run of S1 with adaptive refinement (T10)

Track A's above-threshold case S1 (mu = 0.3, e = 0.2, data of run
A-emd-pbh-20261115-155802-9a6596f: 64^3 root, 262,144 particles, gauge E1) with the example
input `peak_amr.athinput` as it stood on 2026-11-19 (lapse ladder 0.9, 0.7, 0.55, 0.4;
eight particles per cell; fine-shape deposit; `dt_lightspeed`; guard; finder with status
file; region norms), `tlim = 16`, limit 2000 MeshBlocks. Compared with the track's run of
the same data on four static levels (A-emd-pbh-20261115-160349-9d232d2). Figures
`fig_t10_scout`, `fig_t10_lines` (looked at). Everything below [VERIFIED] in the runs
named unless labelled.

**The first attempt died at start** (run core-20261119-150507-8224d72, Slurm job 4654, card
build of 901d8b3): segmentation fault 3 s after start, inside the problem generator, before
the first step. The same command ran on the processors, and on a card with the published
executable in five variants of the MeshBlock limit, block size and finder (run
core-20261120-220538-eafed07): no crash. The source diff between the two builds touches
nothing that runs before the first step. [JUDGEMENT] a transient of the machine (the job
started in the second another card job of the account ended); not reproduced, not
explained.

**The run** (core-20261120-220816-09f6f79, published card executable, 244 s = 0.068
card-hours; analysis core-20261120-222419-a1850d2):

| | adaptive (this run) | four static levels (S1) |
|---|---|---|
| end | guard stop at t = 11.778 (cycle 871), exit status 3, `peak.guard.txt` | fields non-finite at t = 11.709, carried to t = 16 with exit status 0 |
| last sane record | t = 11.775: alpha_min = 2.3e-4 alpha_max | t = 11.704: alpha_min = 0.031 alpha_max |
| first bad cell | level 4, (-0.010, -0.635, -0.049): the lapse minimum on the y axis | not recorded |
| MeshBlocks | 64 to t = 2.20, 120 (level 1), 176 at 7.58 (level 2), 232 at 8.73 (3), 512 at 9.65 (4), 736 at 11.40, 792 at 11.66 | 288 throughout |
| card time to t = 10 / to the end | 75 s / 244 s | 356 s / 645 s (to t = 16) |
| card memory | 66 GB (limit 2000; 792 used) | 10.4 GB |
| Hr_max at t = 0, 2.2, 3.06, 5, 9, 10 | 3.3e-6, 5.7e-3, 0.10, 0.26, 1.45, 1.73 | 0.047 at t = 0, 0.16 at 5, 1.39 at 9, 1.55 at 10 |
| alpha_min/alpha_max at t = 5, 9, 10, 11, 11.5 | 0.807, 0.465, 0.310, 0.017, 1.3e-3 | 0.805, 0.512, 0.387, 0.167, 0.053 |
| E_max/<E> at t = 5, 9, 10, 11 | 4.9, 1.7e3, 3.9e3, 9.8e4 | 4.8, 4.1e2, 7.4e2, 6.5e3 |

What this says:
- The machinery works on the track's case on a card: the mesh follows the falling lapse to
  level 4 (the cell size of S1's finest static level), the rest mass and the particle
  number are constant and the deposition identity holds to 2.2e-16 until the first
  removal, the step follows the finest level, and the run stops by itself with a
  diagnostic and exit status 3 when the fields fail, instead of integrating nonsense to
  `tlim`.
- It gets as far as S1 and no further: the same end at the lapse minima on the y axis,
  0.07 later, for a fifth (to t = 10) to a half of the card time. The mesh was not what
  limited S1.
- Both runs violate the Hamiltonian constraint at order one in the centre from t = 9 on
  (Hr_max 1.4 to 1.7; region norm |H|_2/|16 pi E|_2 inside r = 2.45: 0.29 at t = 9, 0.31
  at 10, against 0.017 and 0.023 outside). What either run shows after t = 9 near the
  centre is not a solution of the constraints, and an apparent horizon found there would
  not be evidence of a black hole.
- On the uniform mesh the largest relative constraint stays below 5.7e-3 (to t = 2.2);
  0.9 after level 1 appears it is 0.10 and then follows S1 (0.26 against 0.16 at t = 5).
  Whether the refined level causes this jump is the subject of T10e (pending, below).
- With the fine-shape deposit E is negative in leaf cells from t = 7.6 on (down to
  -4.6e-3, 5 per cent of E_max; S1: -1.8e-4), and E rings around the peak where the
  particles are sparse (figure `fig_t10_lines`, |x| between 2 and 4.5): the edge weights
  of section 2.2 on real data. From t = 7.5 the adaptive run is denser at the centre than
  S1 (E_max/<E> four to fifteen times) and its lapse falls faster; which of the
  differences (mesh history, fine shape) does it is not separated.
- The finder of the deck never searched: 11 calls from t = 7.85, each ended at its first
  flow iteration with reason 3 (section 2.3, `hmean_tol`). [JUDGEMENT] S1's "no horizon
  in 44 calls" has the same cause (same options and data; S1 has no status file).
- The deck's `alpha_exc = 0.3` is an absolute lapse (0.007 of the mean at a = 45): 248
  particles were removed from t = 11.154 on, at the lapse minima. Whether that hastens
  the end is not tested.
- The particle criterion never acted (at most 7.4 particles per leaf cell, threshold 8):
  the lapse ladder alone drove the mesh.

**Open when the session was paused (2026-11-20 22:34 UTC, usage limit)**:
- T10e, the constraint jump after the first regrid: running on four processors as run
  core-20261120-222729-6cfac05 (`t10e_jump.py`: the deck to t = 3.5 without refinement, as
  run, with the uniform spreading, with every cloud on the root level; about 50 minutes).
  NOT JUDGED. Its script writes `t10e_summary.json` and `fig_t10e_jump.png` into the run
  directory when the four cases end; prediction in the journal (entries of 2026-11-20
  22:23 and 22:27).
- T10c, the last stretch again with four finder surfaces that can flow: written and
  predicted (journal, 22:23), NOT SUBMITTED (two card jobs of core were queued, then the
  pause). Command: `harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher
  batch --list tracks/core/analysis/cosmo_amr/t10c_finder.list --exe
  /data/haiyangw/nrpic/scratch/core/exe/core_cosmo-amr/athena_gpu --gpu-hours 0.25 --wall
  00:15:00 --purpose "T10c of cosmo-amr"`; analysis: `t10c_finder.py --run <case
  directory> --base <case directory of core-20261120-220816-09f6f79>`. It would also be
  the first restart of an adaptive run on a card. Card time of the package so far: 0.08
  of the one card-hour.

## 8. Not done, limits, open points

- Refinement levels do not sub-cycle in time (A2-6): one global step.
- The source filter acts at the cell size of each level; data filtered at the root level
  are inconsistent with the same passes on a finer level (journal 15:05, T3 with filter).
  The leading inconsistency on refined levels of the track's present data.
- Negative leaf-cell E with `deposit_fine_shape` in sparse regions (section 2.2).
- Released deposit, found here (T3c): with quadratic or cubic clouds placed on the level
  of their particle's MeshBlock (`deposit_max_level` above the root, no
  `deposit_adaptive`), a uniform lattice is NOT uniform across a level boundary (35 and
  15 per cent in E, relative constraint 0.14 and 0.07); linear clouds are uniform to
  1e-15. On refined meshes use `deposit_shape = cic`, or put every cloud on one level.
  With `deposit_adaptive` the same holds (T3d): uniform for every shape while the
  adaptive level is equal on both sides of the level boundary, 35 and 15 per cent for
  quadratic and cubic clouds where it follows the mesh level. Not tested: a density
  gradient across which the adaptive level changes on a uniform mesh.
- Constraint solve on the refined levels of the actual mesh and a nested particle lattice
  (A2-11): core's package idsolve-2.
- Field dumps of the particle module on multilevel meshes: not done; AthenaK's `tab` and
  `bin` outputs work on refined meshes.
- The tracker file is truncated on restart (upstream behaviour, unchanged); its position
  is in the restart file.
- Restarts on refined meshes agree with the uninterrupted run to round-off, not bit for
  bit (section 4.2); on a uniform mesh and right after a regrid they are bitwise.
- MPI: built and tested without MPI only.
- The finder on the track's case is untested: with the deck's `hmean_tol` it never flowed
  (section 7); the restart with a working finder (T10c) is pending.
- The released particle restart file stores the previous sources for all
  `max_nmb_per_rank` MeshBlocks (`nrpic_io.cpp`, the block "has_ts": the five extents of
  the array and the whole array): 2.23 GB per restart file at a limit of 2000 MeshBlocks
  of 16^3, with 64 MeshBlocks on the mesh. Not changed here (shared file, restart
  format); request to the core lead: write the MeshBlocks that exist.
- The crash of the first T10 attempt at start (exit 139) is not explained (section 7).
- `alpha_exc` is an absolute lapse; in the conformal-time gauge the lapse is of order a
  (section 7). An excision threshold relative to the mean lapse does not exist.
