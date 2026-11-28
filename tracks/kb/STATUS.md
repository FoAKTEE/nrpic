# STATUS of kb (2026-11-28 03:05 UTC, lead batch 37, short session)

## Gates
gate: KB-G0, KB-G1, KB-G2, KB-G3 signed (KB-G3 2026-11-24, pass with reservations); service mode
- No further gate of kb is defined. Reservations of KB-G3: OPEN.md O7 (claims read against their
  wording), O9 (label set); O4 in part.

## Store (db/current -> kb-20261128-bd57a33, run kb-20261128-024540-477cbc9)
- 762 papers (684 brief + 78 additions), 64 repositories in the manifest (63 GitHub + this one).
- 936 claims. Statuses: checked 452, located 279, unlocated 66, partial 12, refuted 35,
  superseded 85, withdrawn 7. QA (kb/QA_REPORT.md): C1 agree, parse 737/762 = 96.7 %, golden
  hybrid 28/32 papers, 23/32 locations (rerank 28/32, 25/32), C8 equations 40/41.
- Downloads: one known problem row (gr-qc/9412071).

## Claims read against their wording (decision 0049 item 6)
- Class T (144 machine-located claims that a track cites) read in full: claims4 13 + claims5 131.
  Census 124/144 = 86.1 % right as worded (CP 95 % 79.4-91.3 %); the 20 not right corrected.
  claims5 part 114/131 (80.0-92.3 %); runs kb-20261128-024452-cfc4954 (rates),
  kb-20261128-024327-81f35d6 (writes).
- Remaining: class R, 198 unread of 211 machine-located claims no track cites (13 read: 8 right);
  33 borderline rows of claims5 verified as they stand; a second-agent sample of claims5's
  verdicts. Stratified estimate over claims4's 389: about 117 not right (s.e. 29), 41 corrected
  so far [JUDGEMENT: R rests on 13 claims].

## This session (lead b37)
- claims5 reviewed from its artefacts (REVIEW-wave3.md, batch 37): five verdicts drawn with seed
  3720261127 hold at their lines (run kb-20261128-025758-95806ac); census recount 124/144
  identical; provenance diff fcd969d -> bd57a33: only ledger ids changed, 14 new
  (run kb-20261128-025951-075cea6); QA report identical to its run. Figures read.
- Reservation: successor 931 omits the hedge of its own line (1901.08528 L468); to annotate.
- Six owner notes posted (A, B, C, D, F, core; outbox 2026-11-28T02:58Z), D's with the hedge.
- kb/QA_REPORT.md replaced by claims5's report; KB-G3 OPEN.md O7 updated with the census.
- tracks/kb/note/scripts/figstyle.py refreshed from harness/style (orch note core-v0.8 item 4).
- Inbox 1-7 acknowledged (all info).

## Failed predictions
- None this session (L1, L2, L3 held). claims5's Q1 (75 %) refuted by its own census (87 %).

## Next
1. Second-agent sample of claims5's verdicts (decision 0049 item 6), given the artefacts only.
2. The uncited class R: read the 198 unread at their locators (claims4's seeded order), supersede
   what is not right; annotate 931 with the L468 hedge in the same plan.
3. Borderline cleaning (33 rows) or VERIFIER2 leftovers (741, 428, 313/430, 864, 877, O4).

## Runs, cards
- No card job, no queue entry, nothing running. 0 card-hours this session.
