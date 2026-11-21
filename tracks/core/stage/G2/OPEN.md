# What core's G2 still lacks

Two states: the release candidate core-v0.4 (2026-11-21, first section) and the list
written after the wave-1 integration (2026-11-15, below, with its numbering kept; items
that core-v0.4 changes are marked there by the first section).

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
- i. The release drivers (`tracks/core/analysis/release/`) compare one example per
  branch; the capability tests of the packages were not rerun on the merged executables.

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
