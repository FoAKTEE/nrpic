# claims4: second pass over the machine-located claims never read

Package of owner kb (helper), batch 34, 2026-11-27. It answers KB-G3 OPEN.md item O7 and the
leftovers of the second verifier (VERIFIER2.md, REVIEW-wave3.md batch 17). It wrote to the working
database `kb-data/db/kb.sqlite` inside the writer lock, in registered runs only. Card time: none.

Status: done for what was planned in the time: 60 of the 389 unread machine-located claims read
(all 34 cut texts, 13 of 144 cited, 13 of 211 others), all eight leftovers settled, writes
applied, rates and figure made. 329 unread machine-located claims remain (see "Open").

## Results

| Item | Outcome | Evidence |
|---|---|---|
| Population | 389 machine-located claims (label set by the seeder, status located) that no person had read; classes C cut 34, T cited by a track 144, R rest 211, read in seeded order (seed 20261127, committed first) | run kb-20261128-003945-e1d65ba (order.tsv, order.json); `scripts/population.py` |
| Rates | right as worded: C 18/34 = 52.9 % (CP 95 % 35.1-70.2 %), T 10/13 = 76.9 % (46.2-95.0 %), R 8/13 = 61.5 % (31.6-86.1 %); T+R (random within class) 18/26 = 69.2 % (48.2-85.7 %) | run kb-20261128-005107-c2d924a (rates.json, figure) |
| Beside earlier samples | claims3 WA 18/22, verifier2 M 10/13, pooled 28/35 = 80.0 %; with this package's T+R: 46/61 = 75.4 % (62.7-85.5 %) | same run |
| Whole class | stratified estimate for the 389: right 66.5 % (s.e. 8.5 %), about 130 not right (s.e. 33), 24 of them corrected here [JUDGEMENT: extrapolation from 26 sampled claims] | same run |
| Errors | not right: 15 fragments (subject or predicate cut, a heading, a locator alone), 5 judgements or readings of a track under fulltext, 3 parts without support, 1 wrong detail | `LEDGER.tsv`, `work/verdicts_*.tsv` |
| Writes | plan `plans/P1_claims4.json`, 72 actions: 36 verify (5 with extended locators), 32 supersede (successors 896-921 written and read at the source; 339 -> 862), 1 withdraw (583), 1 relocate (741), 1 annotate (805), 1 add (922). Dry run and real run identical; all other claim rows unchanged (hash) | runs kb-20261128-004850-7a66cfe (dry), kb-20261128-004951-4e8871c (applied) |
| Leftovers of VERIFIER2 | 741 relocated to Spin_PBH.tex L1205-1209; 428 -> 916 (Ciarfella first); 804 -> 917 to_verify, 805 annotated (one rule: an instruction is not a statement); 313 -> 918; 430 -> 919; 864 -> 920 (Jena is the affiliation); 877 -> 921 (paper) + 922 (F's run, judgement) | same runs; JOURNAL entry 2 |
| Snapshot, QA | registered run kb-20261128-005138-5cef2a2 (verify-downloads, `kb qa run`, `kb snapshot`, status); see JOURNAL entry 3 for its outcome | that run's out.txt |

Figure (looked at): `figures/fig_claims4_rates.png`: (a) the right-as-worded rate per class with
CP 95 % intervals beside the earlier samples and the stratified estimate; (b) verdicts per class.
The label of the stratified band overlaps one marker; the numbers are in rates.json.

## What is here

| File | Content |
|---|---|
| `JOURNAL.md` | entry 1: population, classes, verdict rules, predictions (before the draw); entries 2-3: outcomes |
| `SEED` | 20261127 (committed in e1d65ba before the order run) |
| `work/verdicts_C.tsv`, `work/verdicts_TR.tsv` | one row per read claim: class, verdict, right, borderline, action, note |
| `LEDGER.tsv` | the verdict rows with their successor ids, plus the siblings and leftovers the plan touched |
| `plans/P1_claims4.json` | the writes, with evidence per action (committed in 7a66cfe before its runs) |
| `rates.json` | rates, CP intervals, stratified estimate, earlier samples (copy of the rates run) |
| `NOTE_TO_OWNERS.md` | the information note to the owners whose claims changed (for the lead to post) |
| `scripts/population.py` | the population, the classes and the seeded order (read-only) |
| `scripts/show.py` | prints a claim with the source lines at its locators (terminal only) |
| `scripts/rates.py` | rates, ledger, figure; `scripts/figstyle.py` copied from `python/nrpic/figstyle.py` |
| `figures/` | the figure (PNG, PDF) |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/claims4/scripts/population.py count          # read-only; today's class differs (60 now read)
python3 -I tracks/kb/claims4/scripts/show.py 476 558 --siblings   # read a claim at its locators
python3 -I tracks/kb/claims3/scripts/apply.py tracks/kb/claims4/plans/P1_claims4.json --out DIR --dry-run
python tracks/kb/claims4/scripts/rates.py --order /data/haiyangw/nrpic/scratch/kb/kb-20261128-003945-e1d65ba \
    --apply /data/haiyangw/nrpic/scratch/kb/kb-20261128-004951-4e8871c --out DIR
```
Do not apply P1 again: the supersedes are done and apply.py refuses a second supersede.

## Open

- 329 machine-located claims are still unread (T 131, R 198 in the seeded order of the order
  run; the next to read are T from k = 48 and R from k = 192 of order.tsv). At the measured rate
  about 100 of them are not right as worded.
- Borderline verdicts (10 counted right: cut starts, table debris, noun phrases, a gloss) are
  verified as they stand; their text keeps the debris. A cleaning pass would supersede them.
- 922 (added judgement) has status unlocated although its locator resolves (apply.py's add path).
- 313's successor 918 does not carry 'citing 2108.11967' or 'dispersion approaches c', which I
  did not re-read; 309's successor 909 carries C's p(0) finding unrechecked (labelled judgement).
- The track notes that quote the superseded ids still quote them (NOTE_TO_OWNERS.md).

## Requests

- **kb lead**: post `NOTE_TO_OWNERS.md` to the owners A, B, C, D, F, core (tracks/kb/outbox);
  copy the QA report of run kb-20261128-005138-5cef2a2 to kb/QA_REPORT.md if you keep it; update
  OPEN.md O7 with the rates above (the machine-located class is right about two times in three,
  not four in five); decide whether the next pass reads the remaining T before R.
- **A, B, C, D, F, core**: where a note cites a superseded claim, cite the successor (list in
  NOTE_TO_OWNERS.md).
