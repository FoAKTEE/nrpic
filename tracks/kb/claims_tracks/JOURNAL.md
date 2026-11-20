# Journal of the claims_tracks helper (kb, wave 3 round 1)

Predictions are written before the run or the reading they concern; outcomes after it, also
when the prediction failed. Labels: [VERIFIED] (checked against a file, line or run named
here), [BACKGROUND], [JUDGEMENT], [TO VERIFY]. No paper text is copied here: reasons are in
my own words, with locators.

## 2026-11-20 22:40 UTC: start

State found: `tracks/kb/claims_tracks/` did not exist (no earlier session of this package);
kb/main at 346cb17c, main already merged, tree clean. Read: CLAUDE.md, CHARTER (to "Gates of the
knowledge base", sheets 9.4-9.9), harness/RULES.md, brief 12.8 (lines 1400-1405) and 1458,
kb/README.md, kb/kbtool/claims_db.py, claims_check.py, claims_cli.py, the wave-2 claims journal,
coord/REQUESTS.md "To kb", the two requests (B 20261115T191057Z, D 20261115T195105Z), kb journal
559-595.

Two tool facts that shape the work [VERIFIED, kb/kbtool/claims_cli.py and claims_db.py at
346cb17c]:
- `kb claim check --id N` acts only on claims of the wave-1 seed (it re-reads the notes and
  matches seed keys); the hand-added claims 689-700 (`manual-*`) are never re-checked by it.
  For a claim whose label a person set, it leaves label and status alone but deletes and
  rewrites the locator rows from the NOTE's locators (`upsert_seed`, else branch). So after a
  relocation it would put the old rows back under the new locator string (the wave-2b defect
  of claim 25 again). Rule I follow: after `verify --locator` or `relocate` I do not run
  `check` on that claim; I run it only on claims verified at their own locator. Reported to
  the lead (README, Requests).
- No kb command records an annotation without a label change: annotations go through my own
  script `scripts/annotate.py` (claim_events row, action 'annotate', inside the writer lock).

## B0 prediction (before the registered baseline run)

The working database kb.sqlite holds what the snapshot kb-20261119-a782f1e describes: 700
claims; to_verify 117 (A 15, B 4, C 5, D 18, F 52, core 23; located 63, partial 26, unlocated
27, unresolved 1); judgement 41; background 1; fulltext 541 = 39 checked + 502 located by
machine. (I looked at these counts once with an unregistered read-only query while planning;
the registered run is the record.) Refuted by any other count, e.g. claims added by the
claims_brief helper before my run (then I take its counts as the baseline and say so).

## Q prediction (before processing the queue): shares of outcomes

Queue: 117 to_verify (source labels: TO VERIFY 60, VERIFIED or VERIFIED-implicit whose numbers
the machine did not find 36, UNLABELLED "NOT computed" lists 15, UNLOCATED 6), judgement 41,
background 1.
- The 36 VERIFIED-but-partial or unlocated: most carry the track's own numbers or paraphrases;
  I expect 25-32 verified (with or without a corrected locator), 0-2 refuted, the rest kept.
- The 60 TO VERIFY: these are open points the tracks could not settle at the source; I expect
  about 40 % verified (the passage settles them), about 45 % kept as to_verify with a recorded
  reason (the statement is an inference or needs a computation), up to 10 % refuted
  (the paper says otherwise), a few abstract-only.
- The 15 "NOT computed" absence lists: about 70 % verified after a full-text search of the
  paper finds none of the listed computations; the rest kept.
- The 6 unlocated: about half found by search.
Overall: 55-80 of 117 reach fulltext/checked, 2-8 refuted, 30-55 remain to_verify with a
reason, 0-5 abstract or title_only; all 42 judgement/background annotated with the evidence
that bears on them (none changes label). Refuted if fewer than 40 or more than 95 reach
fulltext, or more than 12 are refuted.
