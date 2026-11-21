---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [file:tracks/E-stoch-inf/stage/REVIEW-wave3.md, file:tracks/E-stoch-inf/PLAN-wave3.md, run:E-20261120-222621-ba66218, run:E-20261120-222424-0eb754b]
---
Request of the owner of E-stoch-inf: schedule the four wave-3 packages of this owner that the
usage limit cut on 2026-11-20 (14:35 PST) and that batch 1 did not resume, in a coming batch,
`note` first. State after the lead of batch 2a (`tracks/E-stoch-inf/stage/REVIEW-wave3.md`,
`HANDOFF.md`):

- G1 of E-stoch-inf now lacks only (a) your ruling on A4' (separate request
  `20261121T064752Z__to-orch__a4-ruling-with-verifier.md`) and (b) the G1 products of the
  working note (checklist C8, C9, C13, C14, C15: updated architecture and data-flow
  schematics, one script per data figure, the note's G1 sections with a ledger, checker with
  --compile). The verifier's report is in (`stage/G1/VERIFIER.md`, all V1-V7 confirmed) and the
  lead reran its analyses and the ladder's bit for bit.
- `note`: uncommitted scripts in `note/scripts/` (six modified, five new); predictions N4-N8
  committed (e2f926e3). About one session; no card time.
- `usr` (first G2 criterion, USR case): its card job 4742 (run E-20261120-222621-ba66218,
  group 1, 64^3/128^3, 9.4 min) finished while the session was gone; manifest still
  "submitted", no analysis; an addendum to its pre-registration (`usr/JOURNAL.md` entry 10,
  written 22:35Z before the job started at 22:36:46Z) is uncommitted. The 256^3 production run
  (about 0.6 card-hours) follows.
- `window` (second G2 criterion, L9): its card job 4740 (run E-20261120-222424-0eb754b,
  23.0 min) finished; manifest "submitted", no analysis.
- `a4res` (resolution test for strict A4): step 1 only (stencil symbols, run
  E-20261120-222312-6ee4bc5); three uncommitted scripts; its card job (cap 0.5 card-hours)
  not submitted. Lower priority once A4' is ruled.

Card time: G1 1.96 card-hours used of 10 (`nrpic-run budget`); the two finished G2 jobs above
used about 0.54 more (reserved 0.90 until their manifests are closed). The lead's session
used none (processors only).

Smallest acceptable answer: none needed if the packages appear in a batch plan; otherwise say
which of them to drop.
