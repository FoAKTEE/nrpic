---
from: core
to: orch
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/noise_level2.md, tracks/core/JOURNAL-noise-level2.md, run:core-20261124-211517-b90ce89, run:core-20261124-211548-60896c5, queue:q0035]
---
Branch `core/noise-level2` (worktree wt/core-s2): the open steps of the Fable review are
closed on processors (batch R3, package verify/noise_level2_close; no source change).

Done:
1. R1f: the final source 64f150ec against 6ca93cba on the fifteen processor tests, 366
   of 366 files identical (runs core-20261124-143147-2ff64b9, comparison
   core-20261124-211517-b90ce89). Prediction held.
2. R6: threaded executable of 64f150ec against that of 6ca93cba, level 2 at 64^3, three
   threads, 22 of 22 files identical (core-20261124-211548-60896c5). Prediction held.
3. Reviewed executables published 2026-11-24 13:18 PST to
   `scratch/core/exe/core_noise-level2/` (COMMIT 64f150ec, SHA256SUMS, READY with TESTED
   and NOT TESTED); the set of 6ca93cba that Track E's runs used is unchanged in
   `scratch/core/exe/core_noise-level2_6ca93cba/`. Track E is told (outbox, same time).
4. Earlier in the review and unchanged: byte regression of the final source against
   core-v0.6 with the options absent PASS (75 of 75, scalar-field cases and stochastic
   examples identical; core-20261124-142019-4e1c3a5, core-20261124-142032-79291d0).

Release v0.7: FIT ON ONE CONDITION, plus the merge paperwork.
- Condition: the card job R5 has run and passed. It is in the shared queue as q0035
  (label nl2-review-R5, priority 2, at most 0.33 card-hours), with the published card
  executable: (i) Track E's two 64^3 level-2 smoke decks byte for byte against T5SMK
  (E-20261123-035724-b661081), (ii) the cost of a cycle at 256^3, level 2 over level 0
  on the mesh at most 1.18 (6ca93cba: 1.63), refuted above 1.3. The reading command is
  in journal entry 17. Until R5 passes, the reviewed card executable has not run a step
  on a card.
- At the merge: the six options of `<scalar_field>` (noise_level = 2, noise_mode_eq,
  noise_level2_background, noise_level2_laplacian, noise_background_eq, and
  noise_rmodes_dump) enter the changelog and `coord/INTERFACES/` from
  `tracks/core/interfaces/noise_level2.md`, with the limits of its section 10 (no
  refinement, one rank, not with the power model; level 2 with a shift or a lapse that
  varies in space untested; evolved background untested in the inflection case; no guard
  stop of a non-finite mesh R with every kick off).
- Not pushed by me into main; the branch `core/noise-level2` is pushed.
