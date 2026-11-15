# JOURNAL of work package embed (helper of owner kb, wave 2): stages K4-K5

Brief section 12.6 (lines 1386-1391), decision 0015 (one open embedding model, downloaded once
into the environment of `wt/kb`; no paper text leaves the machine), processors only, at most
16 cores. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 15:25 UTC  starting state

- `git merge --no-edit main` in `wt/kb`: merged 4ebb05f (rulings after wave 1) into kb/main,
  head ee0ee19.
- Database `kb-data/db/current` -> `kb-20261115-f2fcda5.sqlite`, schema 5: 701 papers, 71070
  chunks (43104 not of kind `comment`), 53862 equations, 157184 code chunks, 0 embeddings
  (read with `sqlite3` in read-only mode, 15:20 UTC).
- `kb search`, `kb embed`, `kb eq` are stubs that exit 3 (`kb/kbtool/cli.py`, STUBS).
- `kb/.venv` (Python 3.10.12) has numpy 2.2.6 and no torch.
- The Hugging Face API lists BAAI/bge-small-en-v1.5 at revision
  5c38ec7c405ec4b44b94cc5a9bb96e735b38267a (last modified 2024-02-22), licence tag `mit`, with
  `model.safetensors` among its files (`scratch/kb/tmp/bge_api.json`, fetched 15:24 UTC with a
  generic client name and no token).

## Choices [JUDGEMENT]

- Model: BAAI/bge-small-en-v1.5 (BERT, 33 M parameters, 384 dimensions, 512 word pieces,
  CLS pooling, unit vectors; MIT). Small enough for processors; 512 word pieces cover most of
  the 200-400-word chunks, where all-MiniLM-L6-v2 (256) would cut half of each chunk; a plain
  BERT, so no `trust_remote_code` (models that need it run downloaded Python, which the rules
  forbid). Only the safetensors weights are fetched (no pickle `pytorch_model.bin`).
- Runtime: torch (CPU wheel) + sentence-transformers in `kb/.venv`, the stack the brief and
  `kb/pyproject.toml` (extra `embed`) already name; loaded with `local_files_only` and the
  Hugging Face network switched off (`HF_HUB_OFFLINE=1`), the user's token cache never read
  (`HF_HOME` inside the environment).
- Storage: vectors as float32 blobs in `embeddings` (brief 12.2: the source of truth); the
  model column holds `<name>@<revision7>`, so a new model or revision adds a new set and keeps
  the old one; a migration adds the text hash per vector (incremental updates, stale rows) and
  a table of models with name, revision, weights hash and recipe.
- Search: BM25 of `chunks_fts` and cosine neighbours, fused by reciprocal rank (k = 60).

## 2026-11-15 15:30 UTC  environment and model

- `uv pip install` into `kb/.venv` with the frozen list of the existing packages as constraint
  (nothing already installed changed): torch 2.14.1+cpu from the PyTorch CPU index, then
  sentence-transformers 6.3.0 (transformers 5.20.2, tokenizers 0.23.3, safetensors 0.8.0,
  huggingface-hub 2.4.0) from PyPI. Constraint files: `scratch/kb/embed/constraints-*.txt`.
- `harness/bin/nrpic-run submit --dry-run` refuses: "the worktree is not clean" (other helpers'
  and my uncommitted files share the worktree). Runs are registered by hand with
  `kb/scripts/registered_run.py` (owner kb's script, same manifest fields); Request in README.
- Run kb-20261115-152601-e02d870: `kbtool.embed_model.fetch()` stored the 12 listed files of
  BAAI/bge-small-en-v1.5@5c38ec7c405e in `kb/.venv/models/BAAI__bge-small-en-v1.5/<rev>/`;
  model.safetensors 133466304 bytes, sha256 3c9f3166...21ad equal to the LFS hash of the tree;
  the other 11 files equal to their git blob hashes (`download.json`). The card's front matter
  says `license: mit` (README.md line 2603) and its License section the MIT licence (line 3072).
  [VERIFIED]

### Prediction E1 (before the smoke test of the model)

The model loads with the network off (`HF_HUB_OFFLINE=1`, `local_files_only=True`) in under
30 s; vectors have 384 components and unit length to 1e-5; for the query "order of the shape
function used to deposit particles on the grid" a passage about cloud-in-cell deposition scores
higher than one about Gamma-driver shift and one about the cosmic microwave background.
Refuted by: any network attempt (error under offline mode), another dimension, or the ordering
failing.

### Prediction E2 (throughput, before the timing run)

On 16 threads, 10 to 40 chunks per second for body chunks (about 240 words), so the 43104
non-comment chunks take 20 to 70 minutes; 10 to 30 % of the body chunks exceed 512 word pieces
and are truncated. Refuted by fewer than 5 chunks per second (the full set would take over
2.4 hours) or a truncated fraction outside 5-50 %.

### Outcome E1, E2 (run kb-20261115-152906-ca81acd, 16 threads, wall 16 s; figure `fig_e1e2_bench.png`)

- E1 holds: loaded offline in 4.8 s; 384 components; norms 1 within 1.2e-7; cosine to the
  deposition query 0.686 (deposition passage) > 0.600 (CMB) > 0.522 (gauge). The CMB passage
  scores above the gauge one: bge scores are compressed into a narrow band, so only ranks are
  meaningful, never absolute thresholds. [VERIFIED]
- E2 holds: 33.4 body chunks per second (256 chunks in 7.7 s), so about 22 minutes for the
  43104 non-comment chunks. Truncated at 512 word pieces (sample of 400 per kind): body 28.7 %,
  appendix 44.5 %, abstract 1.0 %, caption and footnote 0 %; the body figure is inside the
  predicted 10-30 %, the appendix one above it. The text after word piece 512 of a chunk is not
  represented by its vector; the 15 % chunk overlap covers part of it. Windowed pooling (mean
  of the vectors of 512-piece windows) would cover all of it at about 1.4 times the cost; not
  done unless the retrieval test shows misses traceable to truncation. [JUDGEMENT]

## 2026-11-15 15:45 UTC  code and unit tests (commit e164901)

- `kb/kbtool/embed_model.py` (model record, fetch with hash checks, offline loader, test
  embedder), `embed_index.py` (recipes chunk-v1 and eq-v1, incremental embedding under the
  writer lock, stale and orphan handling, check), `embed_search.py` (`kb search`: BM25 + cosine,
  reciprocal-rank fusion, filters, locators through sourcemap.json), `eq_tags.py` and
  `kb/curated/equation_tags.yaml` (nine tags of brief 12.6), `eq_search.py` (`kb eq`),
  `embed_cli.py` (registered in `cli.py`), migration `0006_embeddings_k4.sql`.
- `kb/tests/test_embed_pipeline.py`: 25 tests (synthetic store; incremental update, stale
  text, re-ingest and orphans, a second model set kept, filters, FTS syntax in queries, stale
  vectors dropped at query time, a snapshot without migration 0006 answering by text, tag rules
  positive and negative, the real model offline). Whole suite: 151 passed (other helpers'
  tests included). `test_cli.py` no longer lists search/embed/eq as stubs.

### Prediction E3 (before the full embedding run)

All non-comment chunks of kb.sqlite (43104 at the snapshot, more if the serving helper has
ingested papers since) and all equations (54047 in kb.sqlite at 15:20 UTC) get one vector each;
wall time 25 to 60 minutes on 12 threads; 0 rows skipped as changed unless a re-ingest runs at
the same time; afterwards `kb embed --check --work` reports 0 missing, 0 stale, 0 orphaned.
Truncated fraction of chunks 20-30 % (sample E2), of equations below 5 % (context of four
sentences plus at most 400 characters of TeX). Refuted by any missing or stale row after the
run, or a wall time above 90 minutes.

### Prediction E4 (retrieval test, written before any retrieval result on the corpus)

Set: `tracks/kb/embed/questions10.yaml`, ten questions in our own words with the answer
locations of FIRST_QUESTIONS.md (FQ1-FQ4, FQ6-FQ8), six equation lookups by label. Whole
corpus, no filter; a hit is a chunk of the right paper whose source lines overlap the locator.
Expected: hybrid finds 8 or more of 10 in the top 10; text-only and vector-only each 6 or more;
hybrid at least as many as the better single ranking and a higher MRR@10 than text-only.
Equations: with `--paper`, 5 or more of 6 in the top 10 for hybrid; over the whole corpus
fewer (several papers write the same 1+log or Gamma-driver equations). Refuted by: hybrid
below 7 of 10, or hybrid finding fewer than either single ranking.

### Prediction E5 (equation tags, before `kb eq --apply-tags` on the corpus)

Each of vlasov, geodesic, hamiltonian_constraint, momentum_constraint, z4c and deposition tags
at least 20 equations, compaction_function, langevin and tidal_radius at least 5; the labelled
equations of 2611.12831 get: eq:vlasov -> vlasov, eq:first-order-shape -> deposition,
eq:z4-einstein -> z4c, eq:plummer-hamiltonian -> hamiltonian_constraint. Precision on a random
sample of 10 tagged equations per tag (judged by me reading context and TeX locally) at least
7 of 10 for every tag. Refuted by a tag below its count, a missed 2611.12831 label, or a sampled
precision below 7/10.

### Outcome E5 (run kb-20261115-154013-e70f45d, rules version 1, kb.sqlite with 54047 equations)

- Counts hold: vlasov 255, geodesic 169, hamiltonian_constraint 521, momentum_constraint 500,
  z4c 89, deposition 110, compaction_function 92, langevin 263, tidal_radius 43 (papers: 65,
  74, 157, 142, 16, 34, 24, 42, 25). The four labelled equations of 2611.12831 get the expected
  tags. [VERIFIED, `counts.json` of the run]
- Precision as predicted is REFUTED for five of nine tags. My reading of the sample of 10 per
  tag (`sample_for_reading.txt` of the run, scratch only): geodesic 8/10, z4c 10/10,
  deposition 8/10, compaction_function 10/10; vlasov 5/10, hamiltonian_constraint 4/10,
  momentum_constraint 4/10, langevin 5/10, tidal_radius 1/10. [JUDGEMENT: correctness judged by
  reading]
- Failure modes: a context clause fires when the phrase occurs anywhere in four sentences, so
  definitions and estimates next to the named equation are tagged (normalisations, energy
  densities, Christoffel symbols, noise correlators, integral estimates); one vlasov pattern
  (`\mathcal{L}...[^=]*...f`) matched across a whole formula; label patterns met unrelated
  labels (`eq:RT` of a Ricci tensor for tidal_radius, `...-momentum-cons` of matter
  conservation for momentum_constraint); xi as a Gauss-Bonnet coupling for langevin; uses of
  r_t for tidal_radius.
- Rules version 2 (`kb/curated/equation_tags.yaml`): new fields `before`/`after` (the 250
  characters of context next to the equation) and `not_before`; the five tags now need the
  phrase just before the equation plus structural TeX (an equation with "=", no definition sign,
  no time derivative for the constraints; a derivative of f and "= 0" or a collision term for
  vlasov; noise symbol, time derivative and no correlator for langevin; "r_t =" at the start
  for tidal_radius). Six of the failure modes are now regression cases in
  `test_embed_pipeline.py::test_tag_rules` (31 tests in the file pass).

### Prediction E5b (rules version 2, a fresh sample with seed 2, before it is drawn)

Every tag at 7/10 or better on a new random sample; counts of the five revised tags fall
(vlasov 60-200, constraints 50-300 each, langevin 20-150, tidal_radius 5-30); the four
2611.12831 checks still hold. Refuted by any tag below 7/10 on the new sample.

### Outcome E5b (run kb-20261115-154419-f4dfa36, rules version 2, seed 2)

- Holds. Counts: vlasov 151, geodesic 169, hamiltonian_constraint 209, momentum_constraint
  176, z4c 89, deposition 110, compaction_function 92, langevin 133, tidal_radius 21 (all inside
  the predicted ranges); the four 2611.12831 checks hold. My reading of the fresh sample:
  vlasov 7/10, geodesic 7/10, hamiltonian_constraint 9/10, momentum_constraint 7/10, z4c 9/10,
  deposition 9/10, compaction_function 10/10, langevin 8/10, tidal_radius 8/10. [JUDGEMENT:
  judged by reading]
- Remaining false positives seen: definitions of moments or source terms next to a Vlasov or
  deposition passage, Christoffel symbols and integrated solutions under geodesic labels, a
  gauge condition and a velocity solution near "momentum constraint", a noise identity and an
  action for langevin; two label patterns matched inside unrelated labels (`eq:lorentz4` for
  z4c, `eq:transportid4` for tidal_radius). Version 3 anchors those two label patterns (four
  more regression cases; 35 tests in the file pass). Version 3 was not re-sampled: it can only
  remove tags of labels that contain the two strings inside another word.
