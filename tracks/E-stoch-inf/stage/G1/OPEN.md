# What the G1 package of E-stoch-inf lacks (2026-11-21, lead of batch 2a)

G1 is not met (`STATUS.md`). The fresh-context verifier is now in (`VERIFIER.md`, C16).
Missing, in order of importance:

1. **Ruling on A4** (orchestrator): the owner's A4 (accepted with SCOPE 4 by decision 0013)
   fails in P1's set-up at every N; the verifier confirms both measured causes and
   recommends A4' with clause (d) read on the maxima over the entry and the floor defined as
   the part that does not scale with s. Proposal `../../outbox/20261119T151727Z__to-orch__a4-a5-rewording.md`,
   repeated with the verifier's evidence on 2026-11-21 (`../../outbox/`, slug
   `a4-ruling-with-verifier`). Until the ruling, C6 stays OPEN.
2. **G1 products of brief 13.4** (C8, C9, C13, C14, C15): updated architecture schematic,
   data-flow diagram, one script per data figure from registered outputs, the G1 sections of
   the working note with a ledger, the manuscript checker with `--compile`. The wave-3 package
   `note` started them (uncommitted scripts under `note/scripts/`) and was cut on 2026-11-20;
   its next session finishes them. Then the verifier's ledger recomputation (the part of C16
   that needs a ledger).
3. **Release**: scalar-2 is in release core-v0.4 since 2026-11-21. Done: L32p/L32m on the
   release processor build against core/scalar-2 (`../REVIEW-wave3.md` section 3, LR1). Open:
   one P256 rerun on the release card build (0.5 card-hours) against
   E-20261115-172618-f948386 (risk R1 on the cards).
4. **Smaller items, not needed for G1's criteria** (G2 or later): P256's constraint split
   after t = 4.0 (a P256m to t = 8.5, 0.5 card-hours; verifier W3); a halved pair at 128^3 in
   the L set-up or at 256^3 (W4; package `a4res`); the R^NR floor of ~2e-6 separated with
   `dump_metric = true` on both runs of a mirrored pair at 64^3 (W9); the absolute constraint
   levels 40-100 x below P1's statements ([TO VERIFY], W7, risk R18); A7 for the rank count and
   for the card build of the G1 executable.

Pending runs: none of this owner's G1 material. The cut wave-3 packages `usr` and `window`
have finished card jobs without analysis (runs E-20261120-222621-ba66218,
E-20261120-222424-0eb754b; G2 material).
