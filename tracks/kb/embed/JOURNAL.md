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
