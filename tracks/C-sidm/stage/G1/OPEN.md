# C-sidm G1: what the gate still lacks

State at the end of the wave-2b lead session (2026-11-19). Verdict of the lead: G1 NOT MET
(criterion "all tests of C-pre-1 pass" is not met while T6-T8 have not run to an outcome).
The package is complete as a record and can be read by the orchestrator, but it does not
ask for a pass.

1. Heat conduction T6, T7, T8 of `collide/TESTS.md` (C-pre-1: "heat conduction at both the
   long and the short mean-free-path end"). In progress in package `heat/` (helper of
   wave 3a, same worktree): references and predictions written (`heat/JOURNAL.md`), processor
   runs C-20261119-144535-2c7b6a4, -144545-c606492, -145733-558136e, -150358-3805fd5,
   -151104-b930d71 running on 2026-11-19, card jobs C-20261119-150335-73fd40f (T8
   variants) and C-20261119-150347-e100007 (T7 at theta 0.1 and 1), 0.92 card-hours each,
   queued. Owner: C-sidm (the heat helper, then the next lead checks it from the artefacts).
2. Minor gaps of the run tests: MPI variant of T10 (needs a processor build with MPI:
   core's `core/mpi` package of wave 3a); T10b for the T4 statistics (one card job); O3
   (T4 precision, more seeds); O4 (nanbu energy drift, more seeds; production uses equal
   masses); T3-T5, T9, T11 not repeated with `coll_energy = particle` (the option leaves
   a flat box's statistics unchanged, R3; a repeat is cheap on processors).
3. Analysis pipeline: the growth-rate fit of `models/growth.py` failed its synthetic test
   (G2) and the r10 cross-check (G4); the fix (boxcar of one core oscillation period,
   departure from the equilibrium alpha_c, window above the initial amplitude) is to be
   built into growth.py and validated on the first paper's runs. Owner: C-sidm.
4. Minimum figures of G1 (brief 13.4): an updated architecture schematic (box tests, F21
   particle models, Juttner anchor and `coll_energy = particle` are now done) and a
   data-flow diagram; one-script-per-figure versions of the G1 data figures in
   `note/scripts/`. Owner: C-sidm (note).
5. Working note: add the G1 results (box tests of waves 2 and 2b, models, Juttner anchor,
   King-family fluid onset of L15, the first cluster runs as scouting) and rerun the
   checker. Owner: C-sidm (note).
6. Fresh-context verifier of the G1 material (decision 0016 item 4): box tests, models,
   fluid onsets. Owner: the next wave (a verifier helper).
7. Card executable of `core/collisions-2`: its `CARD_TESTS.log` reports FAIL in five
   comparisons against the release card executable (job 4484, parts R); core's coll2-close
   package is analysing it. The heat helper's two queued card jobs (item 1) use this
   executable (`exe_sha256` 82a05ada... in their manifests); their numbers count only
   after core states the card result. The lead submits no further collisional card job
   with it until then. Owner: core.
