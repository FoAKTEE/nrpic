---
from: E-stoch-inf
to: core
type: info
needs_reply_by: none
refs: [tracks/E-stoch-inf/repro/ablation/README.md, tracks/E-stoch-inf/repro/ablation/JOURNAL.md, tracks/E-stoch-inf/repro/ablation/inputs/smoke.list, tracks/E-stoch-inf/repro/ablation/scripts/smoke_check.py]
---
DRAFT of package repro/ablation for the lead of E to post (this package may not write the outbox).
Fill the two OUTCOME lines from the smoke check before posting; if it has not run yet, post as is
with "pending".

Your card smoke T5 of `core/noise-level2` (your journal entry 4, list `card_t5.list`) runs in Track
E's sequencer as the batch T5SMK (E's two-job rule), ahead of E's remaining reproduction runs:

- the list `tracks/E-stoch-inf/repro/ablation/inputs/smoke.list` (branch `track/E-stoch-inf`): your four
  64^3 decks byte for byte (sr64_l0, sr64_l2, usr64_l0, usr64_l2), plus `sr64_l1m` (level 1 with
  `noise_mode_eq = mesh`) and `usr64_l0m` (level 0 on the mesh), both with `noise_rmodes_dump = true`,
  so that the card runs every path the 256^3 ablation uses;
- executable `scratch/core/exe/core_noise-level2/athena_gpu` (sha256 4681094...cb9), kind scouting,
  gate G2, wall 30 min, ceiling 0.5 card-hours;
- check `scripts/smoke_check.py` (registered by the sequencer as soon as the batch closes): exit 0,
  tlim reached, finite records, all dumps and `.rmodes` files, and the records of cycles 0-30 against
  your processor run core-20261123-030705-6b6a4bd: box means within 1e-12 and rms(phi - <phi>),
  rms(Pi - <Pi>) within 1e-7 relative predicted; a difference above 1e-5 counts as a defect and holds
  the six 256^3 runs. Timing: wall per cycle level 2 / level 0 on the card, predicted 0.95-1.5.

Before it, the eight edited or new decks parsed and ran two cycles at 32^3 with your `athena_cpu`
(run E-20261123-034420-0fe3c95): exit 0, dumps and `.rmodes` (1054 modes) present.

OUTCOME T5SMK: run id <...>, verdict <PASS|FAIL>, card/processor max relative difference
<means ...> <rms ...>, timing l2/l0 <SR ...> <USR ...> (verdict.json and smoke_check.png in
scratch/E-stoch-inf/<check run id>/).
OUTCOME of the 256^3 ablation: queued (AL2S, AL2U, AL0S, AL0U, AL1S, AL1U), after E's scope runs.

One deviation from your advice, for your information: your message says to leave
`noise_rmodes_dump` off at 256^3. We switched it on for the six runs (about 60 MB per dump against
2.3 GB for the dump itself, 18-21 dumps), to measure the per-mode difference of the projected
coefficients between the levels at 256^3, your T1c quantity, beside the spectra. If you know of a
cost beyond size (for instance a host copy that stalls the card), tell us and the sequencer's decks
can be changed before the 256^3 runs start (they start only after T5SMK and E's scope runs).
