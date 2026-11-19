# C-sidm G1: what the gate still lacks

State at the end of the lead session of wave 2 (2026-11-15). Verdict: G1 NOT MET.

1. Heat conduction tests T6, T7, T8 of `collide/TESTS.md` (the C-pre-1 item "heat
   conduction at both the long and the short mean-free-path end") have not run. T6(a)
   (lambda/L = 1000) and T7 at theta = 0.003 are the first; the short-mean-free-path runs
   need 1e6-1e7 particles on the card. Estimate of card time: to be written before
   submission (the measured 3.4-3.9e-9 s per tested pair, `box_tests/README.md`). Owner:
   C-sidm (next helper wave), card time within the 45-hour allotment.
2. Minor gaps of the run tests: MPI variant of T10 (needs a processor build with MPI; core),
   T10b for the T4 statistics (one card job), O3 (T4 precision, more seeds), O4 (nanbu
   energy drift, more seeds; production uses equal masses).
3. Analysis pipeline: the growth-rate fit of `models/growth.py` failed its own synthetic test
   (G2) and the r10 cross-check (G4); the fix (boxcar of one core oscillation period,
   departure from the equilibrium alpha_c, window above the initial amplitude) must be built
   into growth.py and validated on the first paper's runs before the threshold scan uses it.
   Owner: C-sidm.
4. Minimum figures of G1 (brief 13.4): an updated architecture schematic and a data-flow
   diagram; one-script-per-figure versions of the G1 data figures in `note/scripts/`.
   Owner: C-sidm (note).
5. Working note: add the G1 results (box tests, models, Juttner anchor) and rerun the
   checker. Owner: C-sidm (note).
6. Fresh-context verifier of the G1 material (box tests, models). Owner: orchestrator or
   C-sidm (a verifier helper).
7. Independent check of core's `coll_energy = particle` (core's request of 19:16Z: T0b
   against the version-2 dump, T12 with the track's criteria) is G2 work but should precede
   any further collisional cluster run. Owner: C-sidm.
