# Interface: refined meshes and horizons in periodic cosmology runs (work package cosmo-amr)

Owner core, branch `core/cosmo-amr`, wave 3a (2026-11-19). For Track A's threshold line in
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
| Coarse clouds sampled on fine leaf cells to first order | `<particles> deposit_fine_shape` | `particles/nrpic.cpp` (`NrpicDepositSources`) |
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
lattice cell of the cloud is distributed over its leaf cells as w + (dw/dx)(x - x_c), with
the analytic slope of the assignment function (cloud in cell, quadratic, cubic), instead
of uniformly. Each lattice cell keeps its weight, so the conservation identity is
unchanged (T1); the slopes of a regular lattice cancel, so a uniform distribution stays
uniform (T2); a smooth density is second-order accurate on the leaf cells. No limiter:
the weight of a single cloud at its edge can be negative, so in a sparse distribution
(about one particle per coarse cell) leaf cells can carry negative E (T1: down to -0.31
of E_max for random particles). Used only where the leaf cells are at most 32 times finer
than the cloud's cells; beyond that the released uniform spreading is used.

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
| `particles/nrpic.cpp` | include; `NrpicInit` (5 lines); `NrpicDepositSources`: slopes `gs` of the three clouds and the fine-shape branch (about 50 lines inside the kd > 0 branch) | fine-shape deposit, region options |
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
section 5.

| Test | What | Run | Result [VERIFIED] |
|---|---|---|---|
| T0 | regression, options absent: geodesics (two pushers), deposit on a static mesh, East et al. data, Oppenheimer-Snyder on a static mesh with restart, homogeneous universe, puncture with finder on a static periodic mesh | `-154346-64067cd` | every output file byte-identical to REL, restart files included |
| T1 | deposition identity on a refined periodic mesh (4096 random particles, levels 0-2, faces between levels; cic/tsc/pcs; cloud level finest/root/adaptive; uniform and fine-shape spreading) | `-154351-64067cd` | |int_E/sum mW - 1| at most 1.7e-14, momentum 1.1e-16 relative, in all 22 cases; with the source filter: 4e-4 to 5e-4 on the refined mesh (filter not conservative across levels), 4.4e-16 at t = 0 on the uniform mesh |
| T2 | homogeneous universe with refined patches: interior, faces and corner, adaptive (tracker), lohner plus `<particles_amr>`, eight particles per root cell with fine clouds, the same drifting through the patch | `-151654-e01b46e` | chi and E uniform to 1.6e-14 and 4.2e-14; |H_max - H_mean| at most 9.7e-13; alpha_max equal to the uniform run to 3.3e-15; lohner plus `<particles_amr>` creates no MeshBlock |
| T3 | linear plane wave (test B of arXiv:1904.07841) with a refined patch | `-161527-4480f58` (first run `-154357-64067cd` void: six-digit tables) | section 4.1 |
| T3c | homogeneous universe, clouds of the three shapes on the finest level of a patch | `-164329-589b34c` | cic uniform to 2e-15; tsc 0.35, pcs 0.15 (released deposit, section 8) |
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
| T14 | card check of the published card executable | `-161748-75c2405` (Slurm job 4664) | pending |
| T10 | scouting run of Track A's S1 with adaptive refinement, on a card | `-150507-8224d72` (Slurm job 4654) | pending, section 7 |

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

## 6. Regression

T0 (run core-20261119-154346-64067cd) and T0b (run core-20261119-161756-44db4b5): with
the new options absent the executable of the tests (source 901d8b3) and the published
processor executable (source 3c44b74) are byte-identical to release core-v0.3 in every
output file of seven set-ups (geodesics with both pushers, deposit on a static mesh,
East et al. data, Oppenheimer-Snyder on a static mesh, homogeneous universe, puncture
with finder on a static periodic mesh), restart files included. T12 shows that the
published executable reproduces the tested one on the cases of T1, T2 and T9.

## 7. Scouting run of S1 with adaptive refinement (T10)

Slurm job 4654 (run core-20261119-150507-8224d72, card executable of 901d8b3, 0.75
card-hours asked): pending at the time of writing (expected start 20:39 PST). Prediction
in the journal (entry 14:45, T10).

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
  `deposit_adaptive` with quadratic or cubic clouds is not tested.
- Constraint solve on the refined levels of the actual mesh and a nested particle lattice
  (A2-11): core's package idsolve-2.
- Field dumps of the particle module on multilevel meshes: not done; AthenaK's `tab` and
  `bin` outputs work on refined meshes.
- The tracker file is truncated on restart (upstream behaviour, unchanged); its position
  is in the restart file.
- Restarts on refined meshes agree with the uninterrupted run to round-off, not bit for
  bit (section 4.2); on a uniform mesh and right after a regrid they are bitwise.
- MPI: built and tested without MPI only.
