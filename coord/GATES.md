# Gate sign-offs

Ledger of the orchestrator's gate decisions (decision 0017 item 2). A sign-off is a
review of the stage package at the named commit; the tag is on that commit.

| Date | Owner | Gate | Verdict | Commit | Tag | Basis and reservations |
|---|---|---|---|---|---|---|
| 2026-11-19 | A-emd-pbh | G0 | PASS | 775b6d6297 | `stage/A-emd-pbh/G0-pass-20261119` | Package complete (scoping, references read at the source, risks, cost, working note v0 with two schematics); clean-checkout verification passes; a fresh verifier confirmed eight of ten claims and found two wrong (the ball does hold the particle bracket of arXiv:2609.14218; the predicted horizon time for the amplitude 0.045 contradicts the published curve), both corrected in `scope/SCOPE.md` section 10.9. Item C18 (ledger of the note recomputed) is judged at G1 (decision 0016 item 4). Reservation carried to G1 and G2: no slicing has reached a horizon yet in either set-up. |
| 2026-11-19 | B-emd-gw | G0 | PASS | 3c5d2e7af4 | `stage/B-emd-gw/G0-pass-20261119` | Package complete; the lead judged all twenty items pass or not applicable; the harness verdict was FAIL only for the verifier report's file name and for nine hand-written manifests, both waived (decision 0016 items 1 and 3); a fresh verifier confirmed the eight claims the plan rests on, with one wrong side estimate and the non-transverse oblique-wave generator, both since corrected (the generator by core, branch `core/requests-b`). Reservation carried to G1: the spectrum today in the semi-analytic baseline is not confirmed against the paper's own formula. |
