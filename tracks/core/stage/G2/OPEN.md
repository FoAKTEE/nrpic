# What core's G2 still lacks

Five states: the state after release core-v0.6 (2026-11-21, batch 4a, first section:
the gate as a whole and the defects found since), the release candidate core-v0.6, the
release core-v0.5, the release core-v0.4, and the list written after the wave-1
integration (2026-11-15, below, with its numbering kept; items that a release changes
are named in the section of that release).

## State after release core-v0.6 (2026-11-21, batch 4a, session core-lead-6; items u, v and the products of item 4 brought up to date in batch 8, session core-lead-8; item 2 and item 4 in batch 10a, 2026-11-23, session core-lead-10a)

**Is G2 met? No.** Criteria of the core sheet (brief 9.3, "G2: all of C3 passed,
core-v0.1 released") and of every track's G2 (charter 9.2), item by item in
`CHECKLIST.md`. What is missing, in the order it blocks:
1. Ladder row 3 (oblate and prolate collapse) is PARTIAL. Prolate: horizon at the
   paper's 32 M at two resolutions (32.00 M at M/16, 32.25 M at M/8), largest M_AH
   0.967 and 0.957, the deficit falling with resolution but 3 per cent left; a third
   resolution needs more than one card (`verify/LADDER.md`, row 3, wave 2). Oblate: no
   oblate component in any release; the component and first collapse runs exist on the
   unmerged branch core/oblate (`REQUESTS_WAVE3.md` W27), so the row has no released
   evidence.
2. Ladder row 4 (cluster stability threshold) is PARTIAL, closer than before. The
   fates of the five models agree with the paper. The M/4 bisection of wave 2 gave no
   bracket (the M/4 mesh pushes clusters outward, Track C's drift package). Batch 10a
   judged the repeat on cells of M/8 against unkicked controls, by the rule written
   before the runs (JOURNAL 2026-11-21T20:26Z): 0.605 member collapses (t_c 180.5 M),
   0.680 member and control both collapse (219.5 M, 251.5 M), 0.755 stays (D = +0.0016);
   **the threshold on M/8 with 10^4 particles is bracketed between y_c = 0.680 and
   0.755** (fates run core-20261123-020318-e952741; `verify/LADDER.md` row 4). What is
   still missing for the row: (a) the bracket narrowed: level 2 (0.69875, 0.7175,
   0.73625, each with its control; chains core-20261123-020450-7e42037 to
   -020500-9b192cd, 12 card-hours asked, predictions P5-P9 in the journal) is queued;
   (b) the threshold at a second cell size or particle number (it is not converged; the
   discrete threshold lies above the turning point 0.6796, since the 0.680 control
   collapses from noise); (c) the inward drift of the stable controls (0.026 at 0.755,
   more than the 0.01 predicted) and the growing central-lapse oscillation (+-0.03 after
   200 M) are not explained.
3. Three-way convergence (C2): each direction is shown on a different set-up
   (`verify/figs/convergence_three_way.png`: H-norm of the cluster against N, the
   expanding ball against the cell size, gauges and boundary on the ball); no single
   coupled set-up is converged in all three, and the cluster's fate is not converged in
   the mesh (item 2).
4. Products (brought up to date in batch 8): the working note exists and passed its
   checker (`note/`, C15); the fresh-context verifier's report is in (`VERIFIER.md`,
   C16, a sample of fourteen claims; its five text defects are corrected); the
   architecture schematic is redrawn for core-v0.6 (C14). The six row-4 chains of batch 5
   are closed (batch 10a), so the run check of the clean-export verify (C6) no longer
   fails on them; the six level-2 chains queued in batch 10a are open runs again; also open: the ladder rows 2 and 4 rest in part on pre-program directories, now named and
   inventoried by sha256 (`verify/preprogram/README.md`) but without manifests.

What is met: rows 1 and 2 PASS (geodesics, Oppenheimer-Snyder; `verify/LADDER.md`),
core-v0.1 to core-v0.6 tagged, constraints behave, minimal full-GR kinetic runs,
constraint-norm figures, a slice mosaic with zoom boxes (`verify/figs/prolate_mosaic.png`),
the ladder schematic, failed runs on record.

**Defects found since release core-v0.6, first for core-v0.7:**
- p. **Relaxed lapse in vacuum around a black hole** (decision 0022 item 3; Track D,
  package g2runs): with `<z4c> lapse_leak = 0.5` the horizon of a vacuum-bubble
  puncture shrinks in coordinates (1.40 to 0.875 M; 2.20 M without the option) and its
  mass grows late, by [-5.6e-4, +1.27e-3] over 100-199.5 M against [-4.8e-5, +2.0e-5]
  without the option (V-1GB against V-1B, faces at +-384 M, M/8; run
  D-20261121-125909-06f856e, analysis D-20261121-144657-cf510fc, slice mass
  D-20261121-150025-05937b2: M_H 1.00266 at 200 M) [numbers of Track D, not recomputed
  by core]. With dust outside the bubble (ES-1GB) +4.2e-3 by 188 M. The term
  `d_t alpha += -(alpha/T) max(ln(alpha/alpha_0), 0)` acts wherever alpha > alpha_0,
  matter or not (`z4c/z4c_gauge_ext.hpp` line 19) [VERIFIED by reading]. Consequence:
  `lapse_leak` is not usable around a black hole until fixed; gate-G2 null tests run
  without it (decision 0022). Fix and test: `REQUESTS_WAVE3.md` W24.
- q. Card checks of core-v0.6: the merged card executable PASSED its check (job 4800,
  `RELEASE-v0.6.md`); item l of the candidate's section is closed. The release builds
  of the main checkout against the candidate: `RELEASE-v0.6.md`, section "Release
  builds against the candidate".
- r. Not in core-v0.6, for core-v0.7: core/clump-table (equilibrium clumps with
  momentum, executables with READY since 2026-11-21 13:52Z) and core/oblate (W26, W27).
- s. Open limits of the initial-data solver after its second pass: items f to h below
  and `REQUESTS_WAVE3.md` W28.
- t. Lockstep record of the scalar field's mode functions carries RK4's phase error at
  the top shells (k^5 dt^4/600; 2.55e-3 for the top shell at 256^3; Track E, runs
  E-20261121-090057-19571c7, E-20261121-103157-96fee1d) [numbers of Track E]; not
  blocking for E's gate (k <= 32 dk); W25, core-v0.8.
- u. **Restarts are exact only for periodic set-ups and for the particle state**
  (fresh verifier, `VERIFIER.md` V6; decision 0027 item 3; added in batch 8). On the
  release processor executable of core-v0.6 a periodic Z4c run with 4096 particles
  restarted at cycle 10 of 20 repeats its restart data, trajectories, histories and
  snapshot byte for byte; an Oppenheimer-Snyder run with Z4c, static refinement and
  outflow faces restarted at cycle 3 of 6 repeats the particle state exactly and the
  histories within 5e-13, but 64 per cent of the float64 words of the mesh state in the
  restart file at cycle 6 differ (median relative 2.8e-13, 99th percentile 1.7e-7)
  (runs core-20261121-213713-952a0c4, comparison core-20261121-215228-d1f36f4). Core's
  caveat of core-v0.5 (`interfaces/mpi.md` row 4: the mesh restart path refills the
  ghost cells on the outer boundary, 1e-9 there, 1e-10 in the history after one step;
  runs core-20261119-160230-a2f1cf7, -160823-0e90ab7) is the same limit on one rank.
  Consequence: a chained asymptotically flat run (ladder row 4 on M/8; Track C and D
  chains) repeats only up to the growth of round-off; statements about it are made on
  quantities that are stable under round-off, and a convergence series compares runs of
  the same segmentation where it can (decision 0027 item 3). Which part of the restart
  path differs (ghost refill at outflow faces, prolongation at level boundaries, or both)
  is not separated by a run [TO VERIFY]; a fix that refills the ghosts as the running
  step does is for core-v0.7 (no item number yet; byte test: the os set-up of V6).
- v. **Step limit with a Gamma-driver shift** (decision 0027 item 2; Track A's request
  `periodic-gamma-driver-step`, triaged as `REQUESTS_WAVE3.md` W31; added in batch 8):
  the step limit, `dt_lightspeed` included, counts the speed of light only, and the
  shift goes unstable at the grid scale above dt/dx = 0.685 (Track A's stability
  analysis with the code's stencils, RK4 and dissipation 0.5; runs
  A-20261121-212800-d7f31a4, -212941-9e68be1, -220510-6c46032, -212853-4a52dea; numbers
  of Track A, not recomputed by core). Rule until then: `cfl_number` at 0.6 or below
  with a Gamma-driver shift (CLAUDE.md, Machine; `cosmo_amr.md` section 2.4). Item for
  core-v0.7: the gauge speeds and the stability bound of RK4 with Kreiss-Oliger
  dissipation in the step limit, as an option, with A's minimal input as its test.

Every other known defect is in the sections below, newest first: core-v0.6 items a to
o, core-v0.5 items b to m, core-v0.4, and the list of 2026-11-15.

## Release candidate core-v0.6 (2026-11-21): branches left out, items changed, defects

**Branches left out of core-v0.6**, with the reason:
- core/clump-table (equilibrium clumps with momentum from tables): not closed when the
  candidate was built. Its session was running tests at 2026-11-21T12:57Z (tip
  16cce79e, a registered run of that minute); the executables under
  `scratch/core/exe/core_clump-curvature/` are those of the first pass of 2026-11-15.
- core/oblate (oblate collapse of the verification ladder): not closed. Its tip
  4f01a81f is of 2026-11-20 14:33 PST, does not hold release core-v0.5 (`git merge-base
  --is-ancestor c3eb42e0 core/oblate` fails) and its READY of 2026-11-19 describes
  executables older than core-v0.4.
Nothing of either is in the source of the candidate. core/newton-2, core/z4c-faces and
core/id-solver-2 passed the maintainer's review and are merged
(`tracks/core/RELEASE-v0.6.md`); the byte regression against core-v0.5 passes with them
(run core-20261121-130202-7cf7db8).

Items of the lists below that core-v0.6 changes:
- "the initial-data solver on uniform meshes without punctures" (carried from
  core-v0.4): answered by core/id-solver-2 (static refinement, punctures of `nrpic_cf`),
  with the limits f to h below.
- "core/newton-2, core/z4c-faces, core/id-solver-2 unfinished" (section of core-v0.5):
  merged.
- 15 of 2026-11-15 (never-set restart bytes): unchanged since core-v0.4 (zero); asked
  again by package newton2 because its pre-merge build was older than core-v0.4.

Defects and limits of core-v0.6 itself (found by the packages or at the merge):
- a. Five things change in runs with `id_solve = true` without an option
  (`CHANGELOG.md`, section core-v0.6), first the far field at the faces: a solved
  initial slice on a mesh with no periodic face is not the slice core-v0.5 made (psi by
  1e-8 to 1.5e-6, W of moving matter by 2.7e-3 of its maximum); `id_far = robin` gives
  the old bytes for matter at rest. Decided by the maintainer (journal, 12:55Z).
- b. Faces options (`z4c_faces.md`): the faces still reflect. Expanding ball, mean |H|
  in r < 8 at t = 16: 1.69e-2 stock, 2.12e-3 with the full set, 3.9e-5 with the faces at
  twice the distance; the face layers stay 30 (vacuum puncture) to 100 (boosted) times
  above the truncation level of a mesh with distant faces [numbers of the package].
- c. Faces options: no constraint-absorbing treatment of Theta that works
  (`sbc_theta = cpbc` and `nonwave` gain nothing; leave it at `sommerfeld`); the damping
  options of the package were unstable in the ball and are removed (a non-zero
  `sbc_damp_gam` or `sbc_damp_theta` stops the run). `sbc_speed = metric` is the tested
  choice; in the vacuum puncture it is 3 per cent worse than unit speeds at t = 12.
- d. Faces options: r in every formula is the distance from the origin of the mesh; a
  far field centred elsewhere, a face through the origin (division by r = 0, not
  guarded), a mesh that is not a cube, faces nearer than 16 M, reflect, inflow or user
  faces beside outflow faces, matter near a face, adaptive refinement at a face, restart
  with the options, several ranks and the threaded build are not tested.
  `sbc_variant = nonwave` only together with `ghost_falloff = true` and
  `extrap_order = 4` (on linear stock ghosts it doubles the layer of a boosted puncture).
- e. Whole-mesh constraint norms with stock outflow faces are set from the first step
  by the monitor reading linearly extrapolated ghost cells; judge initial data by the
  region norms (`<particles> region_dcycle`), not by whole-mesh norms.
- f. Solver, vector part with `id_vector_residual = code` on a refined mesh: the
  monitor of the momentum constraint stalls at level boundaries (max|M| 2.0e-2 on the
  refined torus against 2.6e-4 uniform) [package].
- g. Solver, punctures: with momentum or spin the error of u has a floor set by the
  distance R of the faces, 2.7e-4 (16 m/R)^2 for P = 0.5 m, whatever the cell size;
  M_psi of the far-field line is not the ADM mass; three-puncture data have no
  independent reference; use `id_residual = stencil`, or `code` with
  `id_puncture_radius >= 3` [package].
- h. Solver: no far field on a mesh with some periodic faces; more than one rank stops
  with a message; trial metrics that are not conformally flat are refused; adaptive
  refinement after t = 0 and `id_solve` with `<amr_criterion0> method = user` not run.
- i. Fourier solver of the Newtonian mode: uniform periodic mesh in one pack, cell
  numbers with the factors 2, 3, 5, 7, MeshBlocks stay power-of-two cubes; not tested
  above 384^3 or with unequal cell sizes and moving particles. Group histories: at most
  eight groups; a group cut by the periodic wrap not tested.
- j. Newtonian mode, property of the scheme: a cold lattice with fewer than one
  particle per cell and direction, commensurate with the mesh, is pushed as a whole by
  the self-forces of its particles (momentum change 2.1e-3 M v at one particle per
  eight cells, 1.15e-2 with a lattice of two cells, against 1e-5 with one particle per
  cell and direction), on uniform meshes too [package newton2, tests T6, T6b, T6c].
  Sample matter with at least one particle per cell and direction of the finest level.
- k. Newtonian mode on refined meshes: one static level tested; a ball crossing the
  level boundary keeps momentum to 5e-5 M v and energy to 4e-4, five times the uniform
  coarse mesh; which term gives the drift is not separated.
- l. Card checks at the time of writing: see `RELEASE-v0.6.md`, sections "Card check";
  a row marked PENDING there is a job that had not run when the release file was
  written.
- m. Combinations: the faces options with a solved puncture ran (8 steps, finite, the
  record of the solve unchanged); nothing else of the three branches was run together,
  and none of them with adaptive refinement, threads beyond the solver's tests, or
  several ranks.
- n. As for core-v0.5: the capability tests of the packages and the verification
  ladder were not rerun on the merged executables; the release rests on the byte
  regression, on one example per branch against the branch's own executable, and on
  the solver's regressions M1 and R2 repeated byte for byte.
- o. Carried from core-v0.5 unchanged: items b to m of its section below.

## Release candidate core-v0.5 (2026-11-21): branches left out, items changed, defects

**Branches left out of core-v0.5: none of the four offered.** core/scalar-3,
core/build-openmp, core/cosmo-amr and core/mpi passed the maintainer's review and are
merged (`tracks/core/RELEASE-v0.5.md`); the byte regression against core-v0.4 passes
with them (run core-20261121-063859-e410ee3). Not part of core-v0.5 because they are
not finished (for core-v0.6): core/id-solver-2 (refined meshes and punctures in the
initial-data solve), core/clump-table (equilibrium clumps with momentum from tables),
core/newton-2 (Newtonian mode, second pass), core/oblate (oblate collapse of the
ladder), core/z4c-faces (outer faces of Z4c). Nothing of them is in the source of the
candidate.

Items of the lists below that core-v0.5 changes:
- 11 of 2026-11-15 (run continues when the state is non-finite): answered by the guard
  `<z4c_guard>`, on by default (exit status 3).
- 12 of 2026-11-15 (step ignores the lapse): answered by `<z4c> dt_lightspeed`.
- d of core-v0.4 (`hmean_tol` in a cosmological box): unchanged in the source; the
  reason of a failed search is now in `<basename>.horizon_status_<n>.txt`
  (`<fastflow> diagnostics`), and the example inputs set 1e30.
- "the particle module is single-rank" (core-v0.4, last paragraph of its changelog
  section): answered by core/mpi, with the limits below.

Defects and limits of core-v0.5 itself (found by the packages or at the merge):
- a. Five things act without an option (`CHANGELOG.md`, section core-v0.5): the guard
  stops a Z4c run with non-finite fields with exit status 3; the summary file of the
  horizon finder and the tracker file lie in the `-d` directory; surface points and
  tracker positions are mapped into a periodic box; `nrpic_cosmo` enrols a refinement
  function; a run on several ranks is no longer refused at once. None changes a byte
  of the twelve regression set-ups; the second moves files of every run that is started
  outside its run directory with `-d`.
- b. `athena_cpu_omp` (threaded build) does not give the bytes of the serial build, at
  one thread either: 44 of 75 regression items differ at rounding level (run
  core-20261121-070623-077b056; module histories 1.2e-15, constraint statistics up to
  1.4e-10). With the flags of the serial build (`OMP_OPT=debug`) the nine set-ups
  without Z4c are identical and the three with Z4c still differ at rounding (run
  core-20261121-071842-f5a8b56): no threaded build is a reference for byte comparisons.
- c. Several ranks, options that stop the run with a message: `pusher = newton`,
  `collisions`, `test_kick`, `curv_dt` (package), `removal_record`, `acc_nsphere`,
  `peri_count`, `perturb_gamma`, `id_solve`, `region_dcycle`, `deposit_fine_shape`
  (added at the merge). Tracks C (collisions), D (accretion diagnostics, Newtonian
  mode) and the initial-data solver therefore stay on one rank.
- d. Several ranks, horizon finder: with deposit, at four cells per horizon radius, the
  finder returns different surfaces on 1, 2 and 4 ranks from identical fields (masses
  1.02456, 1.02604, 1.02449; journal of package mpi, entry 27), and the particles
  removed inside the horizon then differ (43 against 41 of 2000). On ONE rank a change
  of the finder's flow constant by 1e-13 changes the same search by 4.8e-3 in the
  smallest radius and the removed number from 43 to 41 (run
  core-20261120-223502-f9a2c02 of the package, its log read by the lead; the package
  has not written the outcome). So excision by a horizon is not reproducible between
  rank counts where the finder's flow does not converge; with a converged finder it
  was identical (test particles around a moving puncture, entry 26).
- e. Several ranks: the constraint statistics `cstat.hst` differ by 8.5e-10 in the
  largest relative Hamiltonian constraint between 1 and 2 ranks of the cluster test
  (module history 4.6e-13); not tested on several ranks: tracers, clumps with
  momentum, the gauge options of core-v0.4, the scalar field, `<particles_amr>`, the
  guard; MPI with threads; a card build with MPI (the package's build ran two ranks on
  one card; its two-card job 4733 is not judged; no MPI card executable is published
  with core-v0.5).
- f. `deposit_fine_shape`: no limiter (negative leaf-cell energy in sparse regions,
  -0.10 of E_max for random particles with the linear cloud); one rank only. The
  executables that package cosmo-amr published on 2026-11-19 (source 3c44b74) deposit
  the linear cloud with a discontinuity; core-v0.5 has the corrected form (1548d49).
- g. Deposit on refined meshes with quadratic or cubic clouds placed on the level of
  their particle's MeshBlock: a uniform lattice is not uniform across a level boundary
  (35 and 15 per cent in E; found by package cosmo-amr, T3c, also in the releases
  before). Use `deposit_shape = cic` on refined meshes, or one level for every cloud.
- h. Adaptive refinement in `nrpic_cosmo`: no sub-cycling (one global step); the source
  filter acts at the cell size of each level; after the first regrid of Track A's S1
  data the largest relative constraint is about twice that of the unrefined run with
  either spreading; restarts on refined meshes agree to round-off, not bit for bit;
  the horizon surfaces found in the scouting run lie in a region that violates the
  constraints at order one (no horizon in a state that satisfies them is shown).
- i. Threads: adaptive refinement, restarts of refined meshes and of collisional runs,
  and the kernels release core-v0.4 added have not been run under threads; gas
  self-gravity and the Newtonian mode depend on the thread count through the plain sum
  of `Multigrid::CalculateAverage` (the package's diagnostic patch is not in the tree).
- j. Scalar field: nothing at 256^3; one seed; Track E's criterion A4 as written cannot
  be met at four cells per shortest wavelength (first-order part of the constraints,
  `scalar_field_3.md` section 4); two unexplained departures under `lapse_kdriver` and
  `lapse_harmonic = 0.05`.
- k. Carried from core-v0.4 unchanged: d (`hmean_tol`), e (the particle restart file
  stores the previous sources for all `max_nmb_per_rank` MeshBlocks), f (the comment in
  `particles.hpp`: no source of this release touched that line; the source commit of
  the candidate could have corrected it and I did not, to keep the merges free of
  edits that no branch made), g (id_solve), h (clumps with momentum).
- l. Requests of package cosmo-amr to the lead that are NOT done in this release: an
  excision threshold relative to the mean lapse (`alpha_exc` is absolute); a tolerance
  of the finder on the mean expansion; a particle restart file that holds only the
  MeshBlocks that exist.
- m. The release drivers ran five example inputs against the branch executables, the
  two examples of package mpi on 1 and 2 ranks against the package's runs, thirteen
  runs of the threaded deposit, and nine short cases on a card
  (`RELEASE-v0.5.md`); the capability tests of the packages and the verification ladder
  were not rerun on the merged executables. Example inputs of the READY that no run of
  the merged executables has started: `punc_box16`, `mpi_box_periodic`,
  `mpi_cluster_smr`, `mpi_cluster_amr`, `mpi_puncture_exc`, `mpi_two_card_triple`, and
  `peak_amr.athinput` at its own resolution (the 32^3 deck of T9 was run).

## Release candidate core-v0.4 (2026-11-21): branches left out, items changed, defects

**Branches left out of core-v0.4: none.** All seven wave-2 source branches passed the
maintainer's review and are merged (requests-b, gauge, scalar-2, clump-curvature,
id-solver, requests-adf, collisions-2; `tracks/core/RELEASE-v0.4.md`); the byte
regression against core-v0.3 passes with them (run core-20261120-221607-4985804).
Not part of core-v0.4 by plan (decision 0019 item 4): the nine wave-3a branches
(cosmo-amr, id-solver-2, clump-table, scalar-3, z4c-faces, newton-2, build-openmp,
mpi, oblate), which go into core-v0.5.

Items of the 2026-11-15 list that core-v0.4 changes:
- 6 (collision energy at the particles' metric): answered by `<particles> coll_energy =
  particle` (sum M H kept to 6.3e-17 over 5104 collisions of a Z4c cluster on a card,
  run core-20261119-143232-4d1e995, analysis core-20261120-220159-7418482). Open: a
  residual of one sign from the root tolerance (+1.2e-20 of sum M H per collision).
- 7 (lapse front from a sharp surface): answered by `<z4c> lapse_leak` (tests L1 to L3,
  ES of package gauge). Open: the choice of T per problem; periodic boxes of Track A.
- 9 (one shift_eta for all punctures): answered by `<z4c> shift_eta_profile`. Open: more
  than two holes, widths other than 2 on a pair, the paper's factor on kappa_1.
- 15 (36 never-set restart bytes): fixed (zero); regressions against core-v0.3 still
  mask them, regressions against core-v0.4 need no mask.
- 11 and 12 (run continues when the state is non-finite; step ignores the lapse): NOT
  in core-v0.4; package cosmo-amr of wave 3a has both (core-v0.5).

Defects and limits of core-v0.4 itself (found by the packages or at the merge):
- a. No two new capabilities were run together. The quick tests show that each branch
  keeps its own bytes in the merged executable; combinations (id_solve with moving
  clumps, coll_energy with lapse_leak, accretion diagnostics with collisions, tracers
  with the perturbing force) are untested.
- b. Four corrections act without an option and change outputs of existing inputs
  (restart header bytes, `last_time` of final outputs, tracers with m = 0 on the mesh
  metric, the oblique linear wave); `CHANGELOG.md` section core-v0.4 lists them. A track
  that compares against a core-v0.3 run must expect them.
- c. On a card, collisional runs without the new options differ from core-v0.3 at
  rounding (same pairs, momenta 2e-14): no byte regression of collisions on cards.
- d. `<fastflow> hmean_tol_<n>` (default 100) is compared with the surface integral of
  the expansion: in a cosmological box every search ends at its first iteration
  [reported by package cosmo-amr, runs core-20261120-220816-09f6f79 and
  core-20261120-222814-0b2b259; not rechecked by the lead]. Workaround: 1e30.
- e. The particle restart file stores the previous-sources array for all
  `max_nmb_per_rank` MeshBlocks (2.2 GB per file at a limit of 2000) [same package].
- f. Comment only: `particles.hpp`, `NrpicCollideOptions::ext` says history columns 32
  to 35; they are 32 to 36. Left as it is so that the published executables match the
  source commit; to be corrected with the next source change.
- g. id_solve: uniform meshes, one rank, no punctures; the vector part has a closure
  error of about one per cent at the faces; `id_vector_residual` defaults to stencil,
  which is not the recommended mode.
- h. Clumps with momentum: Gaussian components only; the sum of the particles'
  covariant momenta drifts by 1.6 per cent in 2 M (1.3 without the curvature), cause
  unknown.
- i. The release drivers (`tracks/core/analysis/release/`) ran fifteen example inputs
  against the branch executables on processors and eleven short cases on a card; the
  capability tests of the packages and the verification ladder were not rerun on the
  merged executables. Ten example inputs named in the READY were started by no run of
  the merged executable (list in `RELEASE-v0.4.md`).

## State 2026-11-15, after the wave-1 integration

Branches: all six wave-1 branches are merged into core/nrpic; none stays unmerged.

## Gate criteria (core sheet, charter 9.3: "all of C3 passed, core-v0.1 released")

1. **Tags.** core-v0.1 (7daed19), core-v0.2 (52c44eb), core-v0.3 (609a875) are proposed
   (`verify/RELEASE.md`, `CHANGELOG.md`), not created: the orchestrator's step.
2. **Ladder row 3, oblate and prolate collapse: PARTIAL.** One resolution of the prolate
   run (horizon at 32.00 M as in the paper, mass peaks at 0.9666 and falls); no second
   resolution, no oblate run. Earlier prolate run: 0.48 card-hours.
3. **Ladder row 4, cluster threshold: PARTIAL.** Fates of all five models agree with the
   paper; collapse times 1.4 to 1.75 times later (191.0, 104.3 M against about 109, 73 M,
   main.tex 1138); the threshold is not located as a number; the growing oscillation of
   the stable model is unexplained. A bisection in y_c with the current lattice and
   filter is the first wave-2 run.
4. **Three-way convergence (charter 9.2) for the coupled module** in particle number,
   mesh and gauge or boundary: shown piecewise (dust collapse particle number at fixed
   mesh, expanding ball in mesh, Newtonian collapse in mesh), not as one study.
5. **Figures of 13.4**: no ladder schematic, no slice mosaic with zoom boxes, no working
   note under `tracks/core/note/`; no verifier report (VERIFIER_REPORT.md) by an agent that
   did not produce the results.

## Large defects found in this wave (not fixed in this session)

6. **Collision energy at the particles' metric** grows by 1e-9 to 1e-8 per collision in a
   potential (cell-frame conservation only); about 5 percent of the rest mass for 1e4
   particles colliding 1e3 times each at 2 M cells. Decision needed: smaller cells, or a
   pair-energy correction with the metric at each particle (`interfaces/collisions.md`
   section 9).
7. **Lapse front from a sharp surface** (expanding ball): 1+log, conformal-time lapse and
   fixed lapse all fail in some case (`JOURNAL-id.md` entries 3-8 and the lead entry).
   Candidates not tried: `lapse_kdriver`, `lapse_volume`, a driver towards dust slicing,
   a wider smooth edge.
8. **Mesh-metric reconstruction depends on the MeshBlock edge** (1e-13): stochastic
   decisions can differ between layouts. A tested patch exists
   (`notes/rng_gather_experiment.diff`, run core-20261115-124953-8e05112); applying it moves
   existing results by 1e-13 and needs new baselines.
9. **One `shift_eta` for all punctures**: the tracker of a heavy hole stays behind (9.1
   times slower at shift_eta = 20); needed before Track F's mass-ratio-10 passage.
10. **Horizon masses of the light holes** in the three-hole run rise by 1.3 and 1.5 percent
    in 16 M in vacuum at cells of m/8; no convergence series of an evolved multi-hole run.
11. **Run continues with status 0** when the state is non-finite or all particles are
    removed (id package, run core-20261115-044359-aef2f7b).
12. **Time step ignores the lapse** (`z4c_newdt.cpp`): coordinate light speed 2.35 with
    1+log in an expanding region.

## Smaller items

13. id analysis `test2_evolution.py --prefix t3` crashes on a run without particles;
    T2d (interior rms of H) and T3 outcomes are not written (`JOURNAL-id.md`, lead entry).
14. The release executables of the main checkout are older than core-v0.2 (processor:
    no `damp_ch_chipow`, `damp_kappa_gam`); `scripts/_build.sh` records only the Kokkos
    commit. After the tag, the executables named in CLAUDE.md should be the core-v0.3
    builds (outbox to orch).
15. Restart headers carry 36 never-set bytes (`Mesh::mesh_indcs`); every byte regression
    masks them. Initialising them changes existing restart files.
16. Run-id clocks differ: the verify suite names runs in local time (PST), runreg and
    run_registered in UTC.
17. The verify figure of the dust collapse shows one point at t = 25 M where the lapse
    differs from the earlier run by about 1e-5 (end of the record); the judge compares
    only before the first horizon, so it is not explained.
18. Not exercised by any test: scalar-field outflow and reflecting boundaries, any new
    capability on refined meshes beyond one smoke run each, adaptive refinement, MPI.
19. Docs outside core's OWNERSHIP were changed by the merged branches (`docs/FORMATS.md`,
    `docs/RNG.md`, `docs/COLLISIONS.md`); the audit reports them (outbox to orch).
20. Four versions of `analysis/id/test2_numbers.json` above 1 MB remain in the history of
    core/id-extrinsic (now merged); the tip holds the gzip copy only.
