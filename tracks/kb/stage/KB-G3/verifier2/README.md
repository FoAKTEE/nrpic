# KB-G3 verifier 2: second fresh check of the knowledge base's evidence layer (kb helper, batch 15)

Fresh reader, own code, predictions first (JOURNAL.md entry 1, committed with `SEED` in
d4741a70b before any draw). Everything is read from the frozen snapshot
`kb-data/db/kb-20261125-2f97258.sqlite` (opened `mode=ro&immutable=1`) and from the raw sources
under `kb-data/raw/arxiv/`; nothing is written to kb-data and no paper text is committed (the
verdict files carry ids, line numbers and my own wording). The report is `../VERIFIER2.md`. No
card time.

## What is here

| Path | What |
|---|---|
| `SEED` | 20261126, committed before the draw |
| `JOURNAL.md` | entries 0-3: set-up, definitions and predictions, my failed run, outcomes |
| `scripts/v2lib.py` | read-only snapshot access, raw-line reader, the item-1 list, the person-read rule |
| `scripts/show.py` | terminal reader: claim, locator lines from the raw TeX (or chunk text), events, links |
| `scripts/draw.py` | item 2: population, strata P/M/Q, seeded draw of 40; item-1 list; claims3's class query rebuilt |
| `scripts/queue_check.py` | item 3, C1: to_verify claims per track and their processing actions; db/current; snapshot sha256 |
| `scripts/tally.py` | rates with Clopper-Pearson intervals (standard library), weighted and pooled estimates, two figures |
| `scripts/figstyle.py` | copied unchanged from python/nrpic (equal to harness/style) |
| `verdicts/item1.tsv` | item 1: 61 claims, verdict, label note, the lines that decide |
| `verdicts/sample_verdicts.tsv` | item 2: 40 claims, right as worded (0/1), borderline flag, class of error, lines |
| `figures/fig_item1.{png,pdf}`, `figures/fig_sample.{png,pdf}` | from run kb-20261125-042240-6c19d72; both PNGs looked at |

## Runs (manifests under tracks/kb/runs/, outputs in scratch/kb/<run_id>/)

| Run | What |
|---|---|
| kb-20261125-041256-d4741a7 | FAILED (exit 1): wrong worktree path in draw.py, before the draw |
| kb-20261125-041310-20371de | strata.json, sample.tsv, item1.tsv; queue.json, queue_unprocessed.tsv (C1); snapshot sha256 |
| kb-20261125-042218-7b7af60 | tally.json and figures (first layout) |
| kb-20261125-042240-6c19d72 | the same after a layout fix; figures copied into `figures/` |
| kb-20261125-042327-f947572 | C2: `kb status --json`, `kb show 2611.12831` (ends with the snapshot id); unlocated claims per track and label |

## How to rerun

From `/data/haiyangw/nrpic/wt/kb`, each through `harness/bin/nrpic-run submit --kind scouting
--gate G3 --package tracks/kb/stage/KB-G3/verifier2 --cores 1 [--allow-no-venv] --purpose '...'
-- ...` (exact commands in the manifests):

```bash
V=tracks/kb/stage/KB-G3/verifier2/scripts
python3 -I $V/draw.py --seed 20261126 --out "$NRPIC_RUN_DIR"
python3 -I $V/queue_check.py --sha --out "$NRPIC_RUN_DIR"
.venv/bin/python -I $V/tally.py --draw <draw run dir> --verdicts tracks/kb/stage/KB-G3/verifier2/verdicts --out "$NRPIC_RUN_DIR"
python3 -I $V/show.py --brief --width 500 --maxloc 3 781 223 574     # reading, terminal only
```

## Results in one paragraph

Item 1: 60 of 61 claims right (781 not supported as worded). Item 2: P 12/14, M 10/13,
Q 12/13; machine-located pooled with claims3's WA 28/35 = 80 % (63-92 %). Item 3: C1-C7 met,
C1 under the package's reading, with reservations. Recommendation: pass with reservations
(`../VERIFIER2.md`).

## Requests

- kb lead:
  - supersede 781, 223, 574, 553, 145, 169 and 462 with whole-sentence, correctly labelled
    claims;
  - write the machine-located stratum's rate (claims3 WA 18/22; with this sample 28/35) next to
    the mixed-class 86.5 % in OPEN O7 and EVIDENCE;
  - process or relabel the 12 claims labelled abstract that have no locator (706, 709-712, 715,
    773, 774, 794-796, 844), first 773 (bears on A) and 774;
  - fix 741's locator (Spin_PBH.tex L1206) and 428's author order;
  - treat the instructions 804 and 805 alike;
  - consider making `kb status` name db/current as the reading database.
- orch: none beyond judging KB-G3 on both verifier reports.
