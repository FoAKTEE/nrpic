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

## Results (snapshot kb-20261115-a848a06; details and run ids in JOURNAL.md)

- C4 reader fixed (R1, R2b): 30 of 30 sampled papers have an INSPIRE record; 28 agree in title
  and authors; 2103.01183 and gr-qc/9905058 differ because of parse defects (Requests).
- Golden questions (R5, run kb-20261119-151500-2721f64), top 10 of 32:

| mode | paper | answer location |
|---|---|---|
| text | 27 (84.4 %) | 21 (65.6 %) |
| hybrid (wave 2) | 28 (87.5 %) | 23 (71.9 %) |
| rerank, w2-noexpand (this package) | 28 (87.5 %) | 25 (78.1 %) |

  KB-G2 of decision 0016 (paper >= 80 %) is met; the answer location is reported (78.1 %).
  On the ten held-out questions (R4, run kb-20261119-142613-942f713): answer location 6 vs 5,
  paper 8 vs 9.
- Diagnosis (R3, R4b): the misses are ranking misses, not oversized chunks; only one answer
  lies beyond the model's 512 pieces. Expanding the pool by the first three papers hurt.
- Cost: about 11 s per question on 6 threads under a machine load near 130 (4 s of it the
  first stage), because the window vectors are computed on the fly.

## Requests

1. kb lead: `kb search --rerank` (embed_cli.py, cli.py are not this package's files); replace
   `kb/QA_REPORT.md` by the R5 report or a rerun; `kb qa golden --yaml kb/golden/questions.yaml`.
2. kb lead (parser): title of 2103.01183 carries a dedication; gr-qc/9905058 has no title or
   authors.
3. kb lead: a second held-out question set (20 or more, written without seeing R3/R4) before
   trying the post-hoc remedies of R4b.
4. kb lead: whether the abstract counts as the answer location of golden q16.
5. kb lead (ingest): smaller chunks or a stored window index would make the second stage
   cheaper.
