# 0039 Rulings after batch 17

Status: ACCEPTED · 2026-11-25 · orchestrator (decision 0017)

To the next gate: C 80. The other allotments stand.

1. Track E. The scope of G3 (its scope text, section 4d, commit cbe20398) goes to a
   fresh reviewer before the full set of runs is queued; the pilot (queue entry q0045)
   may run. The seven ablation runs that record the level-2 executable replaced in
   place are waived with their provenance (coord/WAIVERS.md; core's record
   tracks/core/EXE_PROVENANCE.md): the run check of the stage tool honours the waiver,
   no change of the harness is needed. From now on a published executable is never
   replaced in place (core's rule; a new directory per publication).
2. Track A. (a) The row "oblate and prolate collapse" of the brief: core's prolate test
   does not cover it for this track, because the suppression of black-hole formation by
   asphericity in a matter era is this track's own physics. Test A2 stays a G2 item in
   reduced form: one oblate member (a deformed core inside the ball) on the release
   build with the time of first shell crossing of the Zel'dovich solution as the
   reference, prediction first, six card-hours at most. If the triaxial run already
   queued (q0015) contains that collapse with that reference, it serves as A2: the lead
   decides and says which. (b) A fresh verifier for checklist item C18 is sent (batch
   18). (c) The bound of 0.1 on the Hamiltonian constraint outside the horizon, written
   at G0, stands and is not replaced by a measured one. Item C3 stays FAILED as written
   for the top-hat members. If the test of the smoothed edge (run K4) shows that the
   floor comes from the density jump and smoothed members meet the bound and converge,
   G2 is judged on smoothed members with the bound as written; if the floor stays, the
   gate review decides with the failure on record. A violation of the constraints that
   does not fall with the mesh or with the particle number is a defect to be explained,
   not a bound to be moved.
3. Track C. Twenty card-hours more toward G2 (80 in all) for the mesh leg and the gauge
   leg of the bracket at a million particles; items C7 and C9 are not judged at one
   mesh. Members of a series run on the executable and the step rule of their control
   (the card build of core-v0.6 with cfl_number 0.25, below the bound of 0.47).
4. Track D. Prediction P5 stays refuted. The null test at M/4 lies outside the
   convergent regime: M/4 is thereby excluded as a mesh for G3, and results at M/4 (the
   growth run FF4) are labelled so. Criterion N is judged at M/8 and M/16. Where item C2
   claims an order of convergence of the null test it needs three members inside the
   regime: one member at M/12 (four card-hours at most, prediction first), or the mesh
   leg of the null test is stated with two members and no order. The check run of the
   G1 gate reviewer D-20261121-165420-5d1c245 is superseded (coord/WAIVERS.md).
5. Harness, for one session after the queue tool's round 3: `nrpic-run finish` accepts a
   manifest with the field `continuations` (runs continued in place by a queue wrapper:
   C and D close them by hand meanwhile); checksums of large outputs are computed
   incrementally (cache by path, size and modification time) in `finish` and in
   `nrpic-stage verify`.
6. Core. Its script changes (the dispatcher's marker removed from the environment of
   every job; the continuation wrapper checks its dispatch) are merged into main
   (685fa17b7): this closes the marker finding of decision 0037 item 4. The release
   processor build of core-v0.7 equals the candidate (75 of 75); the card checks still
   wait in the queue. The next source session (Fable, batch 18) follows
   tracks/core/NEXT_SOURCE.md: outputs that survive a restart (Track F's G1 waits for
   the tracker file), the horizon finder's stopping rule and the excision guard (Track
   D's G2), the figure library's PDF date.
7. Track B's finding goes to A and C: in a periodic box with zero shift the core of a
   collapsing halo crunches in coordinates and stops the run; a Gamma-driver shift
   passes that point (its population journal, 2026-11-25).
8. Knowledge base. No second tag for KB-G3. A label for facts about a repository or a
   tool and locator forms for it are decided when the service mode needs them.
9. Notes for G2 (sections, schematics, rerun lists) are written in the lead sessions
   that judge the remaining runs, once, not now.
