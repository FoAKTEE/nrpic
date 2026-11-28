# 0040 Rulings after batch 18 (amends 0038 item 2)

Status: ACCEPTED · 2026-11-25 · orchestrator (decision 0017)

The allotments stand.

1. Track E, scope of G3. The independent review (its g3/scope_review/SCOPE_REVIEW.md)
   says: do not queue the full set as written. The lead amends section 4d of the scope
   before any production run of G3, each amendment dated and the earlier wording kept:
   the defect in the reference's bin normalisation is corrected and the reference rerun
   (as written, the comparison would have reported a difference of 7.6 standard errors
   that is the reference's own); variance and shape of the tail are judged separately;
   the tests of the zeta reader are replaced by tests that can fail at second order; the
   baseline runs as mirrored pairs; the number of seeds is set together with the size
   of the reference, whose error dominates beyond about eighty seeds. The gauge leg that
   decision 0038 item 2 asked for is withdrawn as a criterion: in this model a lapse
   driven by K coincides with the geodesic slice to one part in a million, so the leg
   cannot fail. The scope states this as a limitation, and it is carried as a
   reservation of G3. A lapse condition that depends on the field is a request to core
   for later, not for G3. The pilot (queue entry q0045) runs as it is.
2. Track A, item C18. The fresh verifier (stage/G2/VERIFIER-C18.md) reproduces which
   members form a black hole, the detection times and the orders of convergence, and
   does not reproduce four mass medians. The lead answers each finding with a
   registered analysis; criteria that failed stay failed.
3. For every owner that reads horizons (A, C, D, F, core): the summary file of the
   horizon finder repeats the last accepted surface when a search fails; whether a
   search found a horizon is only in the status file (`<fastflow> diagnostics = true`).
   Found by Track A's verifier and by core's source session independently. A claim
   "found in all N searches" or a mass read at a given time is rechecked against the
   status file before it enters a gate package.
4. Core. The branch core/restart-finder holds the source of the next release
   (core-v0.8): outputs that survive a restart (tracker file appended, history headers
   once, the conservation record kept on one rank), `<fastflow> polish_iterations_<n>`,
   `<particles> ah_exc_max_growth`, figure PDFs without a date. Processors: tests pass
   and runs without the new options are byte-identical to core-v0.7 (75 of 75). Not
   done, on record: a stop on the residual (no single threshold separates converged
   from unconverged surfaces), a guard relative to the last accepted radius, the
   conservation record on several ranks, Track D's long card test of the guard. The
   card check waits in the queue (q0049); the merge into core/nrpic and the release
   follow it. A track may use the published executable of that branch for scouting
   after the card check has passed (decision 0013).
5. Usage. The week stands at 66 per cent on Wednesday 07:02 PST and resets on Friday
   15:00 PST. No further source session on Fable before the reset; Opus sessions for
   analysis as card runs end; nothing new is launched above 90 per cent.
6. Added after batch 19 (2026-11-25 08:00 PST). Track A, item C3: decision 0039 item
   2(c) named run K4 as the test of the smoothed edge; that was the orchestrator's
   error. K4 varied the time step and the extrapolation of the source on the top hat,
   and the floor of the constraints depends on neither. The smoothed-edge test runs on
   processors next, and C3 is judged after it as 0039 item 2(c) says, with that test
   in the place of K4.
7. Track A, test A2: the lead's choice stands (the triaxial run S1L serves). Its timing
   prediction failed: first shell crossing along the predicted axis at 6.1 to 6.4
   Hubble times against the band 3.4 to 5.0. A2 is FAILED as written. The control in
   Newtonian mode with the same particles is the next test; no cause is named before it.
8. Verifier files: `VERIFIER.md` of a stage is the report of the fresh verifier of the
   whole gate. A report on one checklist item (`VERIFIER-C18.md`) is cited from the
   checklist and does not replace it; the stage tool is not changed.
9. Track E: the scope of G3 is amended (its section 4d.9, items A1 to A13, commit
   905feb7c0, before any production entry); the floor of the spectral convergence is
   second order at 256 cells too (risk R28 closed). Production entries of G3 may run.

