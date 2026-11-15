# The embedding model of the knowledge base (stages K4-K5, brief 12.6; decision 0015)

## Model

| Item | Value | Source |
|---|---|---|
| Name | `BAAI/bge-small-en-v1.5` | https://huggingface.co/BAAI/bge-small-en-v1.5 |
| Revision | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (last modified 2024-02-22) | Hugging Face API, fetched 2026-11-15 15:24 UTC |
| Licence | MIT | model card `README.md` of that revision: front matter `license: mit` (line 2603), section "License" (line 3072) |
| Key in the database | `bge-small-en-v1.5@5c38ec7` (`embeddings.model`, `embed_models.model`) | `kbtool/embed_model.py: model_key` |
| Architecture | BERT, 12 layers, hidden size 384, 12 heads, 512 positions, vocabulary 30522 | `config.json` of the revision |
| Parameters | 33.4 million (133466304 bytes of float32) | size of `model.safetensors` |
| Weights | `model.safetensors`, sha256 `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad` | equal to the LFS hash the repository tree lists |
| Pooling | first token (CLS), then unit length | `1_Pooling/config.json`, `modules.json` |
| Queries | prefixed with "Represent this sentence for searching relevant passages: "; passages without prefix | model card (bge v1.5 usage) |

Why this model [JUDGEMENT]: small enough for the processors (33 body chunks per second on 16
threads, run kb-20261115-152906-ca81acd); 512 word pieces cover most chunks of 200-400 words,
where all-MiniLM-L6-v2 (256) would cut half of each; a plain BERT that sentence-transformers
loads without `trust_remote_code` (models that need it, such as nomic-embed, run downloaded
Python, which the rules forbid); weights as safetensors (no pickle); MIT licence; English
retrieval is what it was trained for. Decision 0015 allows one model, so no second model was
compared.

## Where it lives and how it was fetched

- Directory: `kb/.venv/models/BAAI__bge-small-en-v1.5/<revision>/` of the worktree `wt/kb`
  (ignored by git with the rest of `kb/.venv`), files read-only, with `download.json`: every
  file's size and sha256 and how it was checked.
- Fetched once by `kb embed --fetch-model` (run kb-20261115-152601-e02d870): urllib, a
  generic client name, no token (the user's Hugging Face cache and token are never read), the
  twelve files listed in `kbtool/embed_model.py: MODEL["files"]` only (no `pytorch_model.bin`,
  no ONNX), into a new empty directory, each file checked against the repository tree (LFS
  sha256 for the weights, git blob sha1 for the rest) before the directory is moved into place.
- Loading (`STEmbedder`): `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, telemetry off,
  `HF_HOME` inside `kb/.venv/models`, `local_files_only=True`, `trust_remote_code=False`,
  `token=False`; every file's sha256 is recomputed against `download.json` before loading
  (`check_local`). No paper text leaves the machine: the model runs here, on the processors.

## Environment

`kb/.venv` (Python 3.10.12) with, in addition to the K0/K6 packages: torch 2.14.1+cpu (from the
PyTorch CPU index, no CUDA libraries), sentence-transformers 6.3.0, transformers 5.20.2,
tokenizers 0.23.3, safetensors 0.8.0, huggingface-hub 2.4.0. Full list: `requirements-k4.lock`.
Installed with the frozen list of the existing packages as constraint, so nothing already
installed changed:

```bash
cd /data/haiyangw/nrpic/wt/kb && export UV_CACHE_DIR=/data/haiyangw/nrpic/scratch/kb/tmp/uvcache
uv pip freeze --python kb/.venv/bin/python | grep -v '^-e' > ../../scratch/kb/tmp/constraints.txt
uv pip install --python kb/.venv/bin/python -c ../../scratch/kb/tmp/constraints.txt \
    --index-url https://download.pytorch.org/whl/cpu torch
uv pip install --python kb/.venv/bin/python -c ../../scratch/kb/tmp/constraints.txt sentence-transformers
python3 -I kb/bin/kb embed --fetch-model            # once; does nothing when the model is present
```

## What is embedded (recipes)

The string embedded for each owner is fixed by a recipe; its sha256 is stored per vector
(`embeddings.text_sha256`, migration 0006), so a changed chunk or recipe is re-embedded by the
next `kb embed` and a vector whose text changed is never used (dropped at query time and
counted as stale).

- `chunk-v1`: section number and title, a newline, `chunks.text`, for the chunk kinds abstract
  (heading "Abstract"), body, appendix, caption, footnote. Comments are never embedded.
- `eq-v1`: section number and title, a newline, `equations.context` (two sentences before and
  after), a newline, the first 400 characters of `tex_norm`.

Text beyond 512 word pieces is cut by the model: 28.7 % of body chunks and 44.5 % of appendix
chunks are longer (sample of 400 each, run kb-20261115-152906-ca81acd); the 15 % chunk overlap
covers part of the tail. Per-row word-piece counts and a truncation flag are stored.

A second model or revision gets a new key and a second set of rows; the old set is kept
(brief 12.6). `embed_models` records name, full revision, dimension, pooling, query prefix,
weights hash, licence, source, the recipes and the library versions of the last run.

## Commands

```bash
python3 -I kb/bin/kb embed [--only chunks|equations] [--paper ID] [--threads 12]   # incremental
python3 -I kb/bin/kb embed --check [--work]           # coverage, stale and orphaned vectors; exit 1 if any
python3 -I kb/bin/kb search "QUERY" [-k 10] [--kind all|text|caption|eq|code] [--group G08] [--paper ID]
                            [--hybrid | --text-only | --vector-only] [--json]
python3 -I kb/bin/kb eq "LATEX or keywords" [-k 10] [--tag vlasov] [--paper ID] [--json]
python3 -I kb/bin/kb eq --list-tags ; python3 -I kb/bin/kb eq --apply-tags [--paper ID]
```

- `kb search` fuses the BM25 ranking of `chunks_fts` and the cosine ranking of the chunk
  vectors by reciprocal rank (k = 10, 100 candidates from each; k = 10 rather than the usual 60
  after test E7 of `tracks/kb/embed/JOURNAL.md`); every hit carries paper,
  version, kind, section, the character range in `build/tex/<id>/flat.tex` and the source file
  and lines (through `sourcemap.json`). `--text-only` needs the standard library only; vector and
  hybrid search re-execute under `kb/.venv` and load the model (about 5 s).
- `kb eq` does the same over `equations_fts` (tex_norm and context) and the equation vectors; a
  query with a backslash, ^, _ or = is normalized like the stored tex_norm first. `--tag`
  filters by the tags of `kb/curated/equation_tags.yaml` (written into `equations.tags_json` by
  `--apply-tags`).
- A database without migration 0006 (an older snapshot) still answers, by text only, with a
  note.
- Threads: `--threads` or `KB_EMBED_THREADS` (default 8, at most 16; CLAUDE.md).

## After an ingest

`kb ingest arxiv` rewrites a paper's chunks and equations (new ids, `tags_json` empty), so after
it: `kb eq --apply-tags` (seconds), `kb embed` (only the new or changed rows; orphaned vectors
are deleted), `kb embed --check`, `kb snapshot`.

## Measured (snapshot kb-20261115-621430e; runs and predictions in `tracks/kb/embed/JOURNAL.md`)

| What | Result | Run |
|---|---|---|
| Vectors | 43398 chunks, 54259 equations; 0 missing, stale or orphaned | kb-20261115-153805-e164901, kb-20261115-163855-5aca10c |
| Throughput (12 threads, loaded machine) | 28.8 chunks/s, 25.9 equations/s; 60 min for the whole corpus | kb-20261115-153805-e164901 |
| Truncated at 512 word pieces | 23.2 % of chunks, 14.3 % of equation strings | same |
| Ten questions, locator in the top 10, whole corpus | hybrid 5, text 4, vector 4 (MRR 0.21, 0.35, 0.24) | kb-20261115-164540-5aca10c |
| K9 golden set (32, slack 5 lines) | hybrid 23, text 21, vector 17 (MRR 0.49, 0.50, 0.30) | kb-20261115-164558-5aca10c |
| Equation lookups by label with `--paper` | 6 of 6 in every mode; hybrid ranks 1, 1, 1, 2, 4, 2 | kb-20261115-164540-5aca10c |
| Fusion constant | k = 10 chosen on the K9 set (23 against 21 for k = 60), 5 against 4 on the held-out ten | kb-20261115-164430-5aca10c |
| Latency of one `kb search` | hybrid 9.5 s and 0.73 GB (model load), `--text-only` 0.1 s | JOURNAL, E4b |

Reading [JUDGEMENT]: vectors find answers that BM25 misses (and the reverse), so hybrid answers
one or two more questions per set, but its first places are less often right than BM25's; use
`--text-only` when the words of the answer are known, hybrid when they are not. Four of the ten
questions are missed by every mode although their chunks exist; finer chunks or a second
vector per long chunk are the next things to try (not done).
