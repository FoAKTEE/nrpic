# What core's G2 still lacks

Three states: the release candidate core-v0.5 (2026-11-21, first section), the release
core-v0.4 (second section) and the list written after the wave-1 integration
(2026-11-15, below, with its numbering kept; items that a release changes are named in
the section of that release).

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
