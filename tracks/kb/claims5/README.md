# claims5: the unread machine-located claims that a track cites

Package of owner kb (helper), batch 35, 2026-11-27. Continues claims4 (decision 0048 item 7): class
T of claims4's seeded order (144 claims located by machine, never read by a person, cited by a
track's note, checklist or script). It wrote to the working database `kb-data/db/kb.sqlite` inside
the writer lock, in registered runs only. Card time: none.

Status: done. All 131 unread members of T read at every stored locator (with claims4's 13, T is
read in full); writes applied; rates, figure, snapshot, QA and owner notes made.

## Results

| Item | Outcome | Evidence |
|---|---|---|
| Population | 131 unread members of T, k = 48-178 of claims4's order run kb-20261128-003945-e1d65ba (seed 20261127), read in that order; all fulltext/located/auto at the start | `work/order_T_unread.tsv`, JOURNAL entry 1 |
| Rate (this package) | right as worded 114/131 = 87.0 %, CP 95 % 80.0-92.3 %; borderline rows counted all right 90.1 %, all not right 61.8 % (33 borderline rows counted right) | run kb-20261128-024452-cfc4954 (`rates.json`) |
| T census | 124/144 = 86.1 % (CP 79.4-91.3 %); 20 not right in the class | same run |
| Beside earlier samples | claims3 WA 18/22, verifier2 M 10/13, claims4 C 18/34, T 10/13, R 8/13 (figure, panel a) | same run |
| Whole of claims4's 389 | stratified (C census 16, T census 20, R 5/13 of 211): about 117 not right (s.e. 29), right 69.9 % (s.e. 7.4 %), 41 corrected so far [JUDGEMENT: R rests on 13 claims] | same run |
| Not right (17) | wrong_label 6 (329, 230, 242, 19, 451, 484), fragment 6 (182, 193, 87, 33, 352, 252), wrong 3 (234, 306: hedge dropped; 248: method misstated), part_unsupported 2 (684, 685) | `work/verdicts_T.tsv`, `LEDGER.tsv` |
| Writes | plan `plans/P1_claims5.json` (committed in 9e8af45 before its runs), 132 actions: 114 verify (7 with extended locator), 13 supersede by new texts 923-927, 929-936 (926, 932 judgement), 4 supersede to existing (684, 685 -> 910; 451 -> 638; 306 -> 924), 1 add (928, judgement) | runs kb-20261128-024311-9e8af45 (dry), kb-20261128-024327-81f35d6 (applied); identical outputs, other 789 rows hash-unchanged |
| Snapshot, QA | 936 claims; C1 agree, C3 25, C8 40/41, C7 identical to claims4's run; snapshot kb-20261128-bd57a33 | run kb-20261128-024540-477cbc9; `work/QA_REPORT_after_P1.md` |
| Owner notes | one per citing owner: A 4, B 2, C 7, D 3, F 1 superseded, with the places they are cited; core: its seeded 484 | run kb-20261128-025251-f8edef3; `notes/` |
| Predictions | Q1 (75 %) refuted, the class is cleaner (87 %); Q2 held at the margin (6 = 6); Q3 held, not significant; Q4 held; Q5 held at its edge (20) | JOURNAL entries 2-3 |

Figure (looked at): `figures/fig_claims5_rates.png`: (a) right-as-worded rate with CP 95 % beside
the earlier samples, with a bar for the borderline range, the predicted 75 % and the stratified
estimate; (b) verdicts by track of the claim. The label of the prediction line touches the
verifier2 marker; the numbers are in `rates.json`.

## What is here

| File | Content |
|---|---|
| `JOURNAL.md` | entry 1 predictions (before reading); 2 reading, writes, rates; 3 QA prediction and outcome; 4 notes |
| `README.md` | this file |
| `work/order_T_unread.tsv` | the 131 (k, claim id) read, from claims4's order run |
| `work/verdicts_T.tsv` | one row per claim read: k, class, id, verdict, right, borderline, action, note (what the source says, locator, grep) |
| `work/QA_REPORT_after_P1.md` | copy of the QA report of run kb-20261128-024540-477cbc9 |
| `plans/P1_claims5.json` | the writes with evidence per action, built by `scripts/make_plan.py` |
| `LEDGER.tsv`, `rates.json` | copies from run kb-20261128-024452-cfc4954 (ledger with successor ids, track) |
| `notes/NOTE_<owner>.md` | the information notes for the lead to post (copies from run kb-20261128-025251-f8edef3; one line added by hand to C's) |
| `figures/` | the figure (PNG, PDF) |
| `scripts/show.py`, `scripts/figstyle.py` | copies of claims4's reader and of `python/nrpic/figstyle.py` (identical by diff) |
| `scripts/make_plan.py` | verdicts -> plan; holds the successor texts and the extended locators |
| `scripts/rates.py` | rates, CP intervals, census, stratified estimate, ledger, figure |
| `scripts/notes.py` | the owner notes |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/claims5/scripts/show.py 182 234 --siblings      # read claims at their locators
python3 -I tracks/kb/claims5/scripts/make_plan.py --out DIR/P1.json  # rebuild the plan (identical)
python3 -I tracks/kb/claims3/scripts/apply.py tracks/kb/claims5/plans/P1_claims5.json --out DIR --dry-run
python tracks/kb/claims5/scripts/rates.py --order /data/haiyangw/nrpic/scratch/kb/kb-20261128-003945-e1d65ba \
    --apply /data/haiyangw/nrpic/scratch/kb/kb-20261128-024327-81f35d6 \
    --claims4 /data/haiyangw/nrpic/scratch/kb/kb-20261128-005107-c2d924a/rates.json --out DIR
python3 -I tracks/kb/claims5/scripts/notes.py --order /data/haiyangw/nrpic/scratch/kb/kb-20261128-003945-e1d65ba \
    --apply /data/haiyangw/nrpic/scratch/kb/kb-20261128-024327-81f35d6 --out DIR
```
Do not apply P1 again: the supersedes are done and apply.py refuses a second supersede (a dry run
now fails for the same reason; the dry run above reproduces only before the writes).

## Open

- The rate depends strongly on the borderline rule (33 rows counted right: noun phrases, note or
  locator debris such as "| 2108.11967 `main.tex:283`", glosses). They are verified as they stand;
  a cleaning pass would supersede them with whole sentences. claims4 left the same open point.
- Class R of claims4 is still sampled by 13 of 211; it carries most of the remaining uncertainty
  (about 81 of the 117 estimated not-right claims).
- 928 (added judgement) has status unlocated although its locator resolves (apply.py's add path,
  as in claims3 and claims4).
- New successors have origin_line empty (origin `tracks/kb/claims5`), as in claims4.
- The notes name the citing places at the branch state of 2026-11-27 17:05 PST (claims4's
  classifier); lines may have moved since.
- I did not re-run Track C's king_sequence.py; 928 carries C's run as C's judgement.

## Requests

- **kb lead**: post the six notes in `notes/` to tracks/kb/outbox (to A-emd-pbh, B-emd-gw, C-sidm,
  D-bh-dress, F-hills, core); copy `work/QA_REPORT_after_P1.md` to kb/QA_REPORT.md if you keep it;
  update KB-G3 OPEN.md O7 (class T read in full: 124/144 right as worded; the remaining unread
  machine-located claims are R, 198 of 211); decide whether the next pass reads R or cleans the
  borderline rows.
- **A, B, C, D, F**: where your files cite a superseded claim, cite its successor (list and places
  in your note). C: your reproduction of 2108.11967 is claim 928 [judgement].
- **core**: your seeded claim 484 (SECTION2_CORRECTIONS.md row on the OS mass error) is superseded by
  934; the verdict 'imprecise: an upper bound' stays in your file, not in the paper claim.
