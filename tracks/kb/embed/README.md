# tracks/kb/embed: work package "embed" of owner kb (stages K4-K5, wave 2)

Brief section 12.6 (lines 1386-1391): a local embedding model, vectors for chunks and equations,
hybrid retrieval by reciprocal-rank fusion, the equation index with tags. Decision 0015: one
open model, downloaded once into the environment of `wt/kb`; no paper text leaves the machine;
processors only, at most 16 cores. Predictions and outcomes: `JOURNAL.md` (tests E1-E5).

## What is in this directory

| Path | What |
|---|---|
| `JOURNAL.md` | starting state, choices, predictions E1-E5 written before each test, outcomes (including the refuted ones) |
| `questions10.yaml` | the retrieval test: ten questions with the answer locations of `stage/KB-G1/FIRST_QUESTIONS.md`, six equation lookups by label |
| `scripts/bench_model.py` | E1 (offline load, unit vectors, ordering) and E2 (word pieces per chunk kind, throughput) |
| `scripts/sample_tags.py` | E5: tag counts, the 2611.12831 checks, a random sample per tag for reading (sample text to scratch only) |
| `scripts/eval_questions.py` | E4/E6: text, vector and hybrid retrieval of `questions10.yaml` (or, `--set k9`, the K9 helper's 32 golden questions) over the whole corpus |
| `scripts/fusion_study.py` | E7: weighted reciprocal-rank variants chosen on the K9 set, scored on the ten |
| `scripts/fig_bench.py`, `scripts/fig_eval.py`, `scripts/fig_fusion.py`, `scripts/figstyle.py` | figures (project style, copied from `harness/style/figstyle.py`) |
| `fig_e1e2_bench.{png,pdf}` | word pieces per chunk kind against the 512 limit; E1 scores |
| `fig_e4_retrieval.{png,pdf}` | ten questions: rank of the first correct chunk per question and mode; hits within the top k |
| `fig_e6_retrieval_k9.{png,pdf}` | the same for the K9 helper's 32 golden questions |
| `fig_e7_fusion.{png,pdf}` | hits in the top 10 over the fusion grid, both sets; the chosen variant outlined |

## Results (details and run ids: `JOURNAL.md`, `kb/EMBEDDING.md` "Measured")

- Model BAAI/bge-small-en-v1.5@5c38ec7 (MIT), fetched once, every file hash-checked, loaded
  offline. Snapshot `kb-data/db/kb-20261115-621430e.sqlite` (`db/current`): 43398 chunk and
  54259 equation vectors, 0 missing, stale or orphaned; 1140 equations tagged (rules v3).
- Ten questions over the whole corpus, locator in the top 10: hybrid 5, text 4, vector 4; the
  K9 helper's 32: hybrid 23, text 21, vector 17. Hybrid adds hits but has a lower MRR than text.
  Prediction E4 (hybrid >= 8 of 10) and E6 were refuted; E7 set the fusion constant k = 10.
- Tag precision on a fresh sample: 7/10 or better for all nine tags (rules v2; v1 failed for five).

Code (outside this directory, in `kb/`): `kbtool/embed_model.py`, `embed_index.py`,
`embed_search.py`, `embed_cli.py` (registered in `kbtool/cli.py`), `eq_tags.py`, `eq_search.py`,
`curated/equation_tags.yaml`, `migrations/0006_embeddings_k4.sql`, `EMBEDDING.md` (model,
licence, source, recipes, commands), `requirements-k4.lock`, `tests/test_embed_pipeline.py`.
The modules sit in the package `kb/kbtool/` (as `code_*.py` and `papers_*.py` do), not at
`kb/embed_*.py`, so that `kb/bin/kb` can import them.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
# environment and model: kb/EMBEDDING.md ("Environment"); then once:
python3 -I kb/bin/kb embed --fetch-model
# tests (NRPIC_HOME: see Requests 2)
(cd kb && NRPIC_HOME=/data/haiyangw/nrpic/wt/kb .venv/bin/python -m pytest tests/test_embed_pipeline.py)
# E1-E2
python3 -I kb/scripts/registered_run.py --cores 16 --purpose "..." -- \
    kb/.venv/bin/python -I tracks/kb/embed/scripts/bench_model.py '{run_dir}' --threads 16
kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_bench.py <run_dir>/bench.json tracks/kb/embed/fig_e1e2_bench
# K5 tags, E5
python3 -I kb/scripts/registered_run.py --purpose "..." -- python3 -I kb/bin/kb eq --apply-tags
python3 -I kb/scripts/registered_run.py --purpose "..." -- \
    kb/.venv/bin/python -I tracks/kb/embed/scripts/sample_tags.py '{run_dir}' --seed 2
# K4 vectors (incremental; about 25 min for chunks and 10 min for equations on 12 threads)
python3 -I kb/scripts/registered_run.py --detach --cores 12 --purpose "..." -- \
    kb/.venv/bin/python -I kb/bin/kb embed --threads 12
python3 -I kb/bin/kb embed --check --work ; python3 -I kb/bin/kb snapshot
# E4, E6, E7
python3 -I kb/scripts/registered_run.py --cores 8 --purpose "..." -- \
    kb/.venv/bin/python -I tracks/kb/embed/scripts/eval_questions.py '{run_dir}' --threads 8 [--set k9]
kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_eval.py <run_dir>/results.json tracks/kb/embed/fig_e4_retrieval
python3 -I kb/scripts/registered_run.py --cores 8 --purpose "..." -- \
    kb/.venv/bin/python -I tracks/kb/embed/scripts/fusion_study.py '{run_dir}' --threads 8
kb/.venv/bin/python -I tracks/kb/embed/scripts/fig_fusion.py <run_dir>/fusion.json tracks/kb/embed/fig_e7_fusion
```

## Requests

1. **orch (harness): `nrpic-run` in a shared worktree.** `harness/bin/nrpic-run submit` refuses
   while the worktree has uncommitted files ("the worktree is not clean"), which with several
   helpers in `wt/kb` is always the case. Every run of this package is registered by hand with
   `kb/scripts/registered_run.py` (owner kb's script: same manifest fields, commit recorded
   with a dirty flag for `kb/`). Proposal: let `submit` accept `--paths <dirs>` and require only
   those to be clean.
2. **kb lead: test fixture against the new fetch command.** `kb/tests/conftest.py` loads
   `unpack` from `harness/bin/nrpic-fetch-arxiv` of `$NRPIC_HOME` (the main checkout), and main's
   commit f9ab6c7 replaced `unpack` (metadata and PDF modes, `safe_extract`, `content_of`). Since
   then every test that builds a synthetic store fails with AttributeError unless
   `NRPIC_HOME=/data/haiyangw/nrpic/wt/kb` (the worktree's older copy) is set. The fixture should
   load the copy of the checkout it runs in, or use the new functions.
3. **kb lead: ingest and K4-K5.** `kb ingest arxiv` rewrites a paper's chunks and equations with
   new ids and `tags_json` NULL. Either call `eq_tags.apply(lay, paper=pid)` and
   `embed_index.embed(lay, emb, paper=pid)` from the ingest, or run `kb eq --apply-tags`, `kb
   embed`, `kb embed --check` after every ingest (`kb/EMBEDDING.md`, "After an ingest"). The
   serving helper ingested papers while the full embedding ran; the closing incremental run of
   this package covers what existed at its start only.
4. **kb lead: migration numbers.** `0006_embeddings_k4.sql` is applied to `kb.sqlite`; the next
   free number is 0007.
5. **kb lead / QA helper: golden questions.** `questions10.yaml` (no slack) can join the K9
   set (`kbtool/qa_golden.py`); `scripts/eval_questions.py --set k9` scores that set in all
   three modes. The `IndexError` of `embed_search.Locator.lines` on an empty `sourcemap.json`
   (PDF-only papers), which `qa_report.c7_retrieval` guards against, is fixed in
   `embed_search.py` (test `test_locator_without_source_map`); the guard can go.
6. **kb lead: code chunks.** The 157184 code chunks have no vectors (brief 12.6 names code
   chunks too); `kb search --kind code` is BM25 only through `kb code`. At the measured 26-29
   rows per second on 12 threads that would take about 1.5 hours [JUDGEMENT: extrapolated from
   run kb-20261115-153805-e164901]; worth it only if code questions miss by text.
7. **kb lead: retrieval quality.** Four of the ten questions (conclusions of 2611.12831, two
   about 2609.14218, one about 2512.14649) are missed by every mode although their chunks
   exist. Candidates, not tried: shorter chunks or one vector per 512-piece window (23 % of
   chunks are truncated), the paper title in the chunk recipe, a reranker. Each needs the
   retrieval sets as the test, chosen on one and checked on the other.
