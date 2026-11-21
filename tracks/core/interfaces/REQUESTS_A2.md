# Requests of Track A for the periodic threshold line: triage and what was done

Work package cosmo-amr of core, branch `core/cosmo-amr`, wave 3a, 2026-11-19; scouting run
and card check added in wave 3, 2026-11-20 (section 5). Journal with
the predictions and outcomes of every test: `tracks/core/JOURNAL-cosmo-amr.md`. Options,
formats, lines touched, what is tested: `tracks/core/interfaces/cosmo_amr.md`. Tests:
`tracks/core/analysis/cosmo_amr/` (scripts, figures under `figs/`), run manifests under
`tracks/core/runs/`. Labels: [VERIFIED] read at the locator or measured in the run
named, [JUDGEMENT], [TO VERIFY].

The requests are the outbox files of branch `track/A-emd-pbh`
(`tracks/A-emd-pbh/outbox/20261115T1837..Z__to-core__*.md`); the track's evidence is its
`periodic_threshold/DESIGN.md` and `JOURNAL.md` (scouting runs S1, S2; decisions 0013 and
0016 item 5: the threshold line is built in the periodic box).

## 1. Triage

| # | Request (outbox file) | Ruling | What exists now |
|---|---|---|---|
| A2-1 | `nrpic-cosmo-user-ref-func`: adaptive refinement with `nrpic_cosmo` calls a null pointer | ACCEPTED, done | `nrpic_cosmo` enrols `nrpic::CosmoRefine` (the criteria of `<z4c_amr>`, as `nrpic_cf`), plus criteria made for cosmology in a new block `<particles_amr>`: section 2.1 |
| A2-2 | `periodic-horizon-finder` (1): surface points are not mapped into the periodic box | ACCEPTED, done | every surface point is mapped into the mesh in periodic directions: section 2.2 |
| A2-3 | `periodic-horizon-finder` (2): a failed search writes NaN without a reason | ACCEPTED, done | `<fastflow> diagnostics = true`: `<basename>.horizon_status_<n>.txt`, one line per search with the reason: section 2.2 |
| A2-4 | `periodic-horizon-finder` (3): summary file lands in the start directory, not in `-d` | ACCEPTED, done | the files of the finder (and of the compact-object tracker) are opened at the first search, after the change to the run directory: section 2.2 |
| A2-5 | `refined-mesh-diagnostics`: constraint norms inside and outside a sphere on refined meshes; proper-volume mean of K and of the lapse | ACCEPTED, done (the history columns, the "smallest acceptable answer") | `<particles> region_dcycle`: `<basename>.region.hst`: section 2.5. Field dumps of the particle module on multilevel meshes: NOT DONE (AthenaK's own `tab` and `bin` outputs work on refined meshes and hold E, the constraints and the Z4c fields) |
| A2-6 | `amr-for-first-horizon` (1): do refinement levels sub-cycle in time | ANSWERED: no | one global step for all levels (`Mesh::NewTimeStep` takes the smallest cell; `particles/nrpic.cpp` pushes every particle with `pm->dt`). The remedy on offer is adaptive refinement: the fine levels exist only while the collapse needs them (sections 2.1, 3) |
| A2-7 | `amr-for-first-horizon` (2): recommended refinement for a collapse to a horizon 1/60 of the ball, lattice matched to the finest level | ANSWERED with an example input | `problems/cosmo_amr/peak_amr.athinput`: particles per cell (`ppc_refine`) plus a lapse ladder, clouds on the level the local particle density supports (`deposit_adaptive`), coarse clouds reconstructed on the leaf cells (`deposit_fine_shape`). A nested particle lattice is initial-data work (A2-11) |
| A2-8 | `amr-for-first-horizon` (3): does the conservative cross-level deposit keep a homogeneous core homogeneous across level boundaries (staircases of E in S2) | ANSWERED by test T2, and the staircase removed | section 2.3 |
| A2-9 | `stop-on-nonfinite`: stop with a non-zero status and a final dump | ACCEPTED, done, default on | guard, `<z4c_guard>`: section 2.4. The restart file of the stop holds the failed state and is for a post-mortem only |
| A2-10 | `step-limit-coordinate-light-speed` | ACCEPTED, done, off by default | `<z4c> dt_lightspeed`: section 2.4 |
| A2-11 | `refined-level-constraint-solve`: constraint solve on the refined levels of the actual mesh; nested particle lattice in the periodic generator | ROUTED to core's package idsolve-2 (branch `core/id-solver-2`, its goal 3 "refined meshes in the id solver") | not this package. What this package changes for it: a run may now start uniform and refine adaptively, so that fine blocks are filled by the high-order prolongation of evolved data instead of the cubic interpolation of the file; the measured constraint jump at such a regrid is in section 3 |
| A2-12 | `phase1-generator-cmc`, `gauge-expanding-ball`, `phase1-generator-and-gauge-options` (lapse for collapse in an expanding box) | NOT THIS PACKAGE | core's packages gauge (`core/gauge`) and idsolve-2. The scouting run of section 4 uses the gauge of S1 on purpose |
| A2-13 | `processor-executable-threads` | NOT THIS PACKAGE | core's package `core/build-openmp` |

## 2. What was implemented

Everything is read from the input only if the option is present; without the new options
the executable reproduces release core-v0.3 byte for byte (test T0, section 5). Files
and lines touched: `cosmo_amr.md`, section "Lines touched".

### 2.1 Adaptive refinement in `nrpic_cosmo` (A2-1, A2-6, A2-7)

`<amr_criterion0> method = user` now calls `nrpic::CosmoRefine`
(`athenak/src/particles/nrpic_refine.cpp`): first `pz4c->pamr->Refine` (what the request
asked for: `<z4c_amr> method = trivial | tracker | chi | dchi | lohner` and the radii),
then the criteria of `<particles_amr>`:

| Option | Meaning |
|---|---|
| `ppc_refine`, `ppc_derefine` | refine a MeshBlock in which a cell holds more than `ppc_refine` particles (deposited energy of the cell over the mean energy of a particle); derefine where every cell holds fewer than `ppc_derefine` (default `ppc_refine/16`) |
| `lapse_ratio_1`, `lapse_ratio_2`, ... | a MeshBlock of level l-1 is refined where min(alpha) is below this fraction of the volume mean of alpha |
| `chi_ratio_1`, ... | the same with the conformal factor chi: the cosmological form of `method = chi` |
| `hysteresis` | derefinement of level l only above (1 + hysteresis) times threshold l (default 0.1) |
| `max_level`, `verbose` | finest level asked for; one line per check |

None of them refines the homogeneous universe (both ratios are one, the particle number
is that of the lattice). The `chi` and `dchi` criteria of `<z4c_amr>` are useless in an
expanding box (chi falls everywhere as 1/a^2), as the track noted.

### 2.2 Horizon finder and tracker in a periodic box (A2-2, A2-3, A2-4)

- `fastflow.cpp`, `MetricInterp`: in a periodic direction the surface point is mapped
  into the mesh before the interpolation stencil is built (a point inside the mesh keeps
  its coordinate bit for bit). The finder centre may lie in any image; a surface may
  cross a face or a corner of the box.
- `<fastflow> diagnostics = true` writes `<basename>.horizon_status_<n>.txt`: cycle,
  time, found, reason code, flow iterations, last area, area mass, mean and smallest
  radius, last mean expansion, smallest |mean expansion| reached, number of surface
  points outside the mesh, centre, and the reason in words (0 found; 1 area not finite;
  2 expansion not finite; 3 mean expansion above `hmean_tol`; 4 mean radius negative;
  5 surface shrank to a point; 6 iteration limit). The summary file is unchanged (after
  a failed search it still repeats the values of the last success, or NaN).
- The summary, verbose, grid and Ylm files are opened at the first search, i.e. in the
  `-d` directory. The same for the tracker file `<basename>.co_<n>.txt`.
- Tracker: the position is mapped back into the box after every update, so it follows
  its object across a face (the release stops with "couldn't find the compact object");
  `<z4c_amr> method = tracker` measures the distance to the nearest image, so the
  refined region continues across the face. `<z4c> tracker_walk_tol = eps` (mode `walk`,
  the tracker that follows the lapse minimum): move only to a neighbour whose lapse is
  below (1 - eps) of the own cell; without it the first of equal neighbours wins and
  the tracker drifts one cell per step in a uniform lapse.

### 2.3 Clouds across level boundaries (A2-8)

- The released deposit is conservative across levels and periodic faces (identity T1),
  and a uniform lattice stays uniform across a level boundary when all its clouds have
  one size, or when the lattice has the spacing of the fine cells (T2: S, P, D8, D8s).
- The staircase of S2 comes from the constant spreading of a coarse cloud over the leaf
  cells inside each of its cells. `<particles> deposit_fine_shape = true` replaces it by
  weight plus slope: inside a cloud cell the weight varies linearly with the analytic
  slope of the assignment function. Conservation and the uniform lattice are untouched;
  a smooth density is second-order accurate on the fine cells.
- Not removed: the source filter acts at the cell size of each level. Data solved with
  the filter at the root level are inconsistent with the same number of passes on a
  finer level (section 3). On refined levels this is the leading inconsistency of the
  track's present data.

### 2.4 Guard and step limit (A2-9, A2-10)

- Guard (`particles/nrpic_guard.cpp`; hooks in `Driver::Execute`, `main`): after every
  cycle the evolved fields of the spacetime solver are tested for non-finite values
  (also the initial data). On a hit: diagnostic on standard output and in
  `<basename>.guard.txt` (time, cycle, count per variable, first cell with level,
  position and field values, particles left), the driver leaves its loop, every output
  is written once, exit status 3. `<z4c_guard>`: `stop_nonfinite = false` switches it
  off; `stop_chi_nonpositive = true` also stops on chi <= 0 (off by default: chi
  undershoots next to a puncture and such runs survive); `stop_dt_below`,
  `stop_no_particles`, `check_dcycle`.
- `<z4c> dt_lightspeed = f`: the step is at most `cfl f min(dx_d / c_d)`,
  `c_d = alpha sqrt(gamma^dd) + |beta^d|` from the evolved fields, evaluated every
  cycle, and never above the released limit `cfl dx`.

### 2.5 Region norms (A2-5)

`<particles> region_dcycle = n` writes `<basename>.region.hst` every n cycles on any
mesh: proper volume, proper-volume means of K and of the lapse, coordinate-volume mean
of the lapse, and for the whole mesh and inside/outside each sphere (`region_x1..3`,
`region_radius1..4`; `region_horizon = n` adds the sphere of horizon finder n once it
is found) the norms `H2 = sqrt(<H^2>)`, `E2 = sqrt(<(16 pi E)^2>)`, `E1 = <E>` and the
largest |H|, every leaf cell weighted by its proper volume. The bound of the track's
threshold definition is `H2_out / E2_out` of the horizon sphere.

## 3. Numbers (registered runs; every figure looked at; details in `cosmo_amr.md`, section 4)

- Adaptive refinement with `nrpic_cosmo` (A2-1) [VERIFIED, run core-20261119-154404-64067cd]:
  on the track's peak data (`ic_peak0.5`, 32^3) the release dies at the first check
  (exit -11); this branch refines with `lohner` (64 -> 400 MeshBlocks), with
  `lapse_ratio_1`, `chi_ratio_1` or `ppc_refine` (the central eight blocks at cycle 4);
  particle number and rest mass unchanged, deposition identity 3.2e-14; largest relative
  Hamiltonian constraint after the regrid 0.0116 (fine-shape spreading), 0.0072 (uniform
  spreading), against 0.047 of the track's static start.
- Homogeneous universe with refinement (A2-8) [VERIFIED, run core-20261119-151654-e01b46e]:
  chi and E uniform to 1.6e-14 and 4.2e-14 with patches in the interior, on faces and
  corners, adaptive patches, a lattice drifting through a patch; `lohner` plus
  `<particles_amr>` creates no MeshBlock.
- Deposition identity across levels and periodic faces [VERIFIED, run
  core-20261119-154351-64067cd]: 1.7e-14 in 22 cases.
- Finder in a periodic box (A2-2 to A2-4) [VERIFIED, run core-20261119-152106-9332260]: unit
  puncture at the centre, on a face, at a corner, finder centre in other images: M =
  0.9915211031 in every case, equal to 3.3e-16; the release reports no horizon for a
  centre one period away and a WRONG horizon (M = 0.695) for a hole on a face.
- Guard (A2-9) [VERIFIED, same run as the homogeneous universe]: stop at the first cycle with
  non-finite fields, status 3, `<basename>.guard.txt`; with the guard off (and with the
  release) the run integrates NaN to `nlim` and exits 0.
- Light-speed step (A2-10) [VERIFIED, same run]: with the lapse d_t alpha = -(2/3) alpha^2 K
  the released step exceeds 0.25 dx/c by a factor 3.2 at t = 1; with `dt_lightspeed = 1`
  dt c/(0.25 dx) = 1 to 3e-15.
- Tracker across faces [VERIFIED, runs -151654-e01b46e and -161316-f797997]: follows its
  object across the face to 1e-13, refinement follows on both sides; walk mode with
  `tracker_walk_tol` stays put in a uniform lapse.
- Linear plane wave with a refined patch: T3, see `cosmo_amr.md` section 4.1.

## 4. Found here, not requested: restarts of adaptive runs (A2-14)

The track runs chains of one-hour segments. AthenaK's mesh restart file lacks the counter
that keeps a MeshBlock from changing again within `refinement_interval` cycles, and a
restart file written inside the loop precedes the regrid of its own cycle. With the
release mechanism a restarted adaptive run delays a regrid by up to
`refinement_interval` cycles or skips the regrid of its restart cycle (T11, OLD: 4 to 6
cycles with the wrong mesh). This branch writes the counters next to every restart file
(`<file>.rst.amr`) and performs a pending regrid on restart: the regrid schedule after a
restart equals the uninterrupted run in all ten cases tested [VERIFIED, run
core-20261119-161309-f797997]. Restarts on refined meshes agree with the uninterrupted run
to round-off, not bit for bit (largest field departure 6e-10 on the peak).

## 5. Scouting run of S1 with adaptive refinement (wave 3, 2026-11-20)

Done; the full account is `cosmo_amr.md`, section 7. In short [VERIFIED, run
core-20261120-220816-09f6f79 against the track's A-emd-pbh-20261115-160349-9d232d2]:
- S1 (mu = 0.3) with the lapse ladder ends as the run on four static levels ends, at
  t = 11.778 against 11.709, at the lapse minima on the y axis, for 75 s instead of 356 s
  of card time to t = 10. This time the run stops by itself (guard, exit status 3,
  `peak.guard.txt` with the first bad cell). The mesh was not what limited S1.
- Both runs violate the Hamiltonian constraint at order one in the centre from t = 9 on
  (largest relative value 1.4 to 1.7; |H|_2/|16 pi E|_2 = 0.3 inside r = 2.45).
- **The finder of the track's decks did not search.** `hmean_tol_0 = 100` is compared with
  the surface integral of the expansion, which is 1.3e3 to 1.8e3 for the initial sphere
  of radius 2 in this box: all 11 searches ended at their first flow iteration (reason 3
  in the new status file). The same holds for S1 and S2 [JUDGEMENT: same option and
  data]. Remedy: `hmean_tol_<n> = 1e30` (the example input has it now), and read
  `<basename>.horizon_status_<n>.txt`.
- `alpha_exc = 0.3` in the decks is an absolute lapse: in this gauge (alpha ~ a ~ 45) it
  removes particles only at 0.007 of the mean lapse (248 removed from t = 11.15 on).
- The first attempt (job 4654) died at start with a segmentation fault that did not
  repeat (five variants on a card, two on processors); unexplained.
- Closed on 2026-11-21 (section 5b): T10e and T10c.

## 5b. The fine-shape deposit of the linear cloud corrected; the finder finds surfaces (2026-11-21)

Full account: `cosmo_amr.md`, sections 2.2, 4.6 and 7. In short [VERIFIED in the runs
named there]:
- **A2-8 (clouds across level boundaries), correction.** `deposit_fine_shape` with the
  linear cloud, as published on 2026-11-19 (source 3c44b74), was wrong: a quarter of a
  particle changed its leaf cell at once when the particle passed the centre of a
  lattice cell of its cloud (T17), and on any lattice that is not regular the leaf cells
  did not converge to a smooth density (T19c). It made the jump of the largest relative
  Hamiltonian constraint from 0.01 to 0.16 in two cycles, twenty cycles after the first
  regrid of the scouting run (T10e). Corrected in source 1548d49 (the leaf cells get the
  integrals of the assignment function): continuous, second order (0.0061 to 0.0016 from
  8 to 16 cells per wavelength), conservation identity 1.65e-14, the homogeneous universe
  unchanged by a patch (4.2e-14), nothing changed without the option (byte-identical to
  the release) or with quadratic and cubic clouds. On the S1 data the jump is gone
  (0.0096 instead of 0.066; largest value to t = 3.5: 0.036, uniform spreading 0.039, no
  refinement 0.020; T10f). New executables are published; the card executable has not
  run on a card yet (job 4763 pending).
- **A2-2 (finder), on the track's case.** With `hmean_tol` out of the way and four
  surfaces, the restart of the scouting run from t = 10 (T10c, card) finds two surfaces
  at the lapse minima (0, -0.59, 0) and (0, +0.59, 0) at eight searches in a row, t = 11.26
  to 11.71: area mass 0.63 to 0.77, mean coordinate radius 0.072 to 0.091 (four cells of
  level 4). The surfaces at the centre (radii 2 and 0.8) never converge. The region
  violates the Hamiltonian constraint at order one when the surfaces appear (largest
  relative value 1.73), so they are not evidence of a black hole; they show that the
  finder searches and converges in the periodic adaptive run.
- For the track's set-up: one particle per root cell on a lattice stretched by 30 per
  cent carries a modulation of 7 per cent rms at the cell scale through the linear cloud
  (3 per cent with the quadratic cloud; T19), before any filter or refinement.
- Pending: the scouting run from t = 0 with the corrected deposit and the four surfaces
  (T10g) and the card check of the new card executable (T14b), one card job
  (core-20261121-033223-e1d596b, Slurm 4763).

## 6. Regression

Runs core-20261119-154346-64067cd (tested executable) and core-20261119-161756-44db4b5
(published executable): every output file of seven existing set-ups byte-identical to
release core-v0.3, restart files included.
