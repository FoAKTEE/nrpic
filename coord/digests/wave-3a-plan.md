# Wave 3a: started beside wave 2b (2026-11-19T14:22Z)

The user asked for maximal parallelism (2026-11-19). The cards are the bottleneck (two,
shared with other users), the processors are not, so a second workflow (run
wf_788c1403-5d3, 27 agents) runs beside wave 2b with work that needs little or no card
time and does not depend on wave 2b's results. Its source branches are merged by core's
lead in the next wave; its track packages are handed to the tracks' next leads.

| Group | Packages |
|---|---|
| core, source in AthenaK (Fable, Opus fallback), one branch and worktree each | `core/build-openmp` threaded processor build with scaling against a card; `core/mpi` several ranks for the particle module; `core/cosmo-amr` refinement, horizon finder and tracker in periodic runs, stop on non-finite fields, step limit (Track A's requests); `core/id-solver-2` vector part, coupled solve, refined meshes, punctures, triaxial ball end to end; `core/scalar-3` mode entity, ultra-slow-roll case, late-entry truncation; `core/clump-table` boosted equilibrium clumps for Track F; `core/newton-2` higher-order Laplacian and the tracks' Newtonian requests; `core/oblate` oblate component and collapse (ladder row 3); `core/z4c-faces` outer boundaries and the constraint residual they feed |
| tracks, processor side (Opus) | C heat conduction tests T6 to T8; F post-Newtonian three-body reference; D horizon-flux analysis for G2; E preparation of the ultra-slow-roll case; B design of the halo-population run with a Newtonian-mode scouting run; A exact dust solution without symmetry as a test design |
| check of the brief (Opus), temporary worktree `wt/kb-brief`, branch `kb/brief-check` | eleven packages: the statements labelled BACKGROUND and TO VERIFY of brief sections 3.1 to 3.11, 5 (S5 to S10), 6, 7 and 8 against the sources; papers that appeared since the survey; novelty searches for S5, S7, the null test of S4 and black-hole binaries in particle dark matter |
| harness (Opus) | dry run of the pre-commit hook over the existing history (decision 0017 item 4); nothing installed |
