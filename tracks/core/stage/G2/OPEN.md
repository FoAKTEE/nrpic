# What core's G2 still lacks (state 2026-11-15, after the wave-1 integration)

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
