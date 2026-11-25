# STATUS of kb (2026-11-25 12:55 UTC, lead batch 17)

## Gates
- KB-G0, KB-G1, KB-G2: signed (coord/GATES.md).
- KB-G3: SIGNED 2026-11-24, pass with reservations (coord/GATES.md, commit 8fdb954efa, tag
  stage/kb/KB-G3-pass-20261124; decision 0037 item 1). The reservations on single claims are
  closed in this batch (below); the weak class stays a known limit (OPEN.md O7).
- No further gate of kb is defined; the knowledge base is in service mode.

## Store (db/current -> kb-20261125-56c4b53, run kb-20261125-124304-2790a38)
- 762 papers (684 brief + 78 additions), 64 repositories.
- 895 claims (881 + 14 successors). QA: C1 762/762, parse 737/762 = 96.7 %, golden hybrid 28/32 papers and 23/32 locations (rerank 28/32, 25/32); statuses checked 273, located 469, unlocated 64, partial 12, refuted 35, superseded 36, withdrawn 6.
- Downloads: one known problem row (gr-qc/9412071); 0707.4654, 1006.1632 excluded (0035).

## This batch
- VERIFIER2 checked from the artefacts (REVIEW-wave3.md, batch 17): its seven WRONG claims
  confirmed at their sources and superseded by whole-sentence claims 882-888 (553's successor
  labelled judgement); the twelve abstract claims without a locator processed (773 -> 889,
  774 -> 890, 712 -> 891 located; 709, 844 checked against metadata; 710, 711, 715 withdrawn;
  706, 794-796 -> 892-895 to_verify as repository and tool statements). Plan
  lead_b17/plans/P1_verifier2.json; runs kb-20261125-124157-537e458 (dry),
  kb-20261125-124220-191593e, check kb-20261125-124251-3855127 (figure read).
- OPEN.md O7: the machine-located rate 28/35 = 80.0 % (CP 63.1-91.6 %) beside the mixed rate
  86.5 %; EVIDENCE.md the same and VERIFIER2.md cited; CHECKLIST C5 cites VERIFIER2.md. New O8
  (closed), O9 (label set has no class for repository facts or metadata records).
- Information note to all owners whose claims changed (A, B, core, orch).

## Failed predictions
- A1 as first written: I counted 15 supersedes instead of 14; corrected in the journal before
  any run (commit after 8c405545d). The corrected A1 and A2 held.

## Next
1. Weak-class pass 2 on the machine-located stratum (about 400 claims, ~80 % right as worded):
   texts starting with a cut first; supersede, never verify a wrong text.
2. VERIFIER2 leftovers: 741's locator (Spin_PBH.tex L1206), 428's author order, 804/805 alike,
   313/430 debris, 864 "Jena", 877 split, O4 claims; then the bibliography parser formats.
3. Paper-code links M18-M25 (core messages), index the parameters of core-v0.7.

## Runs, cards
- No card job, no queue entry, nothing running. 0 card-hours this batch.
