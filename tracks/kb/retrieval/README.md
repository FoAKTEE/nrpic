# Retrieval package of kb (wave 2b, 2026-11-19)

What this package did: (1) fixed the reader of check C4 of `kb qa run` (30 papers against
INSPIRE), (2) reran the golden-question evaluation, (3) found by inspection why questions miss
the answer location, and (4) added a second retrieval stage over sentence windows, with tests
that fail before and pass after. Predictions and outcomes: `JOURNAL.md`.

## Files

| Path | What |
|---|---|
| `JOURNAL.md` | predictions, outcomes (R1 C4 reader, R2 QA rerun, R2b name folding, R3 diagnosis, R4 window re-ranking, R5 final QA run) |
| `scripts/inspect_misses.py` | R3: answer chunks of every golden question, their size in word pieces, where the answer starts, BM25/vector/hybrid ranks over the whole corpus |
| `scripts/eval_rerank.py` | R4: first stage against the window re-ranking variants on the 32 golden questions and the ten held-out questions |
| `scripts/fig_rerank.py`, `scripts/figstyle.py` | figure of R4 (style copied from `python/nrpic/figstyle.py`) |
| `fig_r4_rerank.{png,pdf}` | answer-location ranks per question and hits per mode |
| `../../../kb/kbtool/qa_report.py` | C4 reads `kb-data/meta/inspire/<key>.json` (fallback `meta/arxiv-api/<key>.json`), compares names in ASCII forms, lists disagreements; C7 has the mode `rerank` |
| `../../../kb/kbtool/search_rerank.py` | the second stage (pool, sentence windows, window BM25 and window vectors, reciprocal-rank fusion) |
| `../../../kb/tests/test_qa_c4_reader.py`, `../../../kb/tests/test_search_rerank.py` | the tests |

Paper text is never in git: the run directories under `scratch/kb/<run_id>/` hold the answer
chunks read for R3.

## Rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
(cd kb && .venv/bin/python -m pytest -q tests/test_qa_c4_reader.py tests/test_search_rerank.py)
SNAP=/data/haiyangw/nrpic/kb-data/db/kb-20261115-a848a06.sqlite
harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 8 --package tracks/kb/retrieval \
  --purpose "..." -- bash -c "OMP_NUM_THREADS=8 kb/.venv/bin/python -I \
  tracks/kb/retrieval/scripts/eval_rerank.py \"\$NRPIC_RUN_DIR\" --db $SNAP --threads 8"
# the QA report with the new mode (text, hybrid, rerank):
#   kb/.venv/bin/python -I kb/kbtool/qa_cli.py qa run --hybrid --db $SNAP --out <dir>/QA_REPORT.md --json <dir>/qa.json
# one question by hand:
kb/.venv/bin/python -I kb/kbtool/search_rerank.py "On which supercomputers were the simulations run?" --db $SNAP
```

## Results

See `JOURNAL.md` (R5) for the final numbers with run ids.

## Requests

See `JOURNAL.md`, last section, and the structured report of this package.
