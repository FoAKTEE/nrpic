# KB-G3 verifier: independent check of the knowledge base's evidence layer (kb helper, batch 11)

Fresh reader, own code, predictions first (JOURNAL.md entry 1, committed 2e05c967 with the seed
before any draw). Everything is read from the frozen snapshot
`kb-data/db/kb-20261121-aa0a2ae.sqlite` (read-only, immutable) and from the raw sources under
`kb-data/raw/arxiv/` and git objects of this repository; nothing is written to kb-data. The
report is `../VERIFIER.md`. No card time.

## What is here

| Path | What |
|---|---|
| `SEED` | 20261124, committed before the draws |
| `JOURNAL.md` | entries 0-5: set-up, predictions, smoke tests and the two fixes of my own tools, outcomes per item |
| `scripts/vcommon.py` | read-only snapshot access; my own flattening of the raw TeX (main file, \input, comments) and counts |
| `scripts/draw_sample.py` | item 1: strata, allocation (largest remainder, >= 1 per track), seeded draw of 60 claims |
| `scripts/show_claim.py` | terminal reader: a claim, its locator rows with the source lines, its events (paper text stays on the machine) |
| `scripts/draw_bib.py` | item 3: my cited keys (aliases from definitions), ten per paper drawn, source entry next to the database row |
| `scripts/bib_tally.py` | item 3: identifiers printed in the entries against the targets, drawn keys and the whole snapshot |
| `scripts/draw_code.py` | item 4: ten params rows and ten links drawn, source at the indexed commit via `git show` |
| `scripts/parse_rate.py` | item 5: parse rate by my own definition (criteria i-vi of JOURNAL entry 1) |
| `scripts/arith_checks.py` | the arithmetic behind the verdicts of items 1 and 2 |
| `scripts/tally.py`, `scripts/figstyle.py` | rates with Clopper-Pearson intervals and the four figures (figstyle copied unchanged from python/nrpic) |
| `verdicts/sample_verdicts.tsv` | item 1: one row per drawn claim, my reading and the lines that decide it |
| `verdicts/refutations.tsv` | item 2: 11 refuted brief seeds, 24 refuted printed statements, 20 superseding claims |
| `verdicts/bib_verdicts.tsv` | item 3: per paper of ingest3's twenty |
| `verdicts/code_verdicts.tsv` | item 4: ten params rows, ten links |
| `figures/` | fig_sample, fig_refutations, fig_bib, fig_parse (PNG and PDF, copied from the tally run) |

## Runs (manifests under tracks/kb/runs/, outputs in scratch/kb/<run_id>/)

| Run | What |
|---|---|
| kb-20261124-130442-e69c2e8 | draws of items 1, 3, 4 (sample/, bib/, code/) |
| kb-20261124-130450-578a535 | item 5 parse rate (parse_papers.tsv, parse_summary.json) |
| kb-20261124-132849-3ebad97 | arithmetic checks and bibliography tally (items 2, 3; whole_missed_sample.tsv) |
| kb-20261124-132859-5f1a7f3 | tally.json and the four figures (copied into figures/) |

## How to rerun

From `/data/haiyangw/nrpic/wt/kb`, each through `harness/bin/nrpic-run submit --kind scouting
--gate G3 --package tracks/kb/stage/KB-G3/verifier --cores 1 --allow-no-venv --purpose '...' --
bash -c '...'` (exact commands in the manifests):

```bash
V=tracks/kb/stage/KB-G3/verifier
python3 -I $V/scripts/draw_sample.py --seed 20261124 --out "$NRPIC_RUN_DIR/sample"
python3 -I $V/scripts/draw_bib.py --seed 20261124 --ids tracks/kb/ingest3/ids/zero20.txt --out "$NRPIC_RUN_DIR/bib"
python3 -I $V/scripts/draw_code.py --seed 20261124 --links kb/curated/paper_code_links.tsv --out "$NRPIC_RUN_DIR/code"
python3 -I $V/scripts/parse_rate.py --out "$NRPIC_RUN_DIR"
python3 -I $V/scripts/arith_checks.py --out "$NRPIC_RUN_DIR"
python3 -I $V/scripts/bib_tally.py --draw <draw run>/bib/bib_draw.tsv --out "$NRPIC_RUN_DIR"
.venv/bin/python -I $V/scripts/tally.py --draw <draw run> --parse <parse run> --bib <bib run> --verdicts $V/verdicts --out "$NRPIC_RUN_DIR"
python3 -I $V/scripts/show_claim.py --window 1 53 2 11      # reading, terminal only
```

## Requests

- kb lead: the four findings of VERIFIER.md section "What the track should do" (claim 682
  rewording, the 4 settleable brief to_verify seeds, the identifier misses of the bibliography
  parser, the abstract chunk of 5 "ok" papers); the snapshot-wide count of 4538 entries that
  print an identifier but carry no target (bib run `whole_missed_sample.tsv`).
- ingest4 (kb helper, same batch): the uncommitted kb/kbtool changes blocked `nrpic-run` for
  this package at 05:20 (JOURNAL entry 4).
- core (through the kb lead, not urgent): nothing found wrong in the ten code links; the
  matter term of the Hamiltonian in z4c_calcrhs.cpp:570 is commented out but added separately
  to Theta at :649-652, so it is consistent.
