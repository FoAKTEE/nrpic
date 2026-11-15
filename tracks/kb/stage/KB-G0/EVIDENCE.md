# KB-G0 evidence (owner kb, 2026-11-15)

Gate definition: brief 12.10, line 1458: "KB-G0: tools chosen, directories in place".
The package was not written in wave 1 (the wave-1 lead recorded KB-G0 as met inside
`../KB-G1/EVIDENCE.md`); this directory states it on its own, as nrpic-stage expects.

| Criterion | State | Evidence |
|---|---|---|
| tools chosen | met | `kb/JOURNAL.md` sections "K0 tool choice", "K2-K3 tool choices", "Tool choice for the code index" (each with reasons, [JUDGEMENT]); `kb/EMBEDDING.md` (K4: BAAI/bge-small-en-v1.5 at revision 5c38ec7, MIT licence, weights sha256 3c9f3166...21ad, rechecked in run kb-20261115-182238-b86d2b5); frozen environments `kb/requirements-k0.lock`, `kb/requirements-k4.lock`, `kb/requirements-k6.lock` |
| directories in place | met | `kb-data/{raw/{arxiv,github},meta/{arxiv,arxiv-api,arxiv-pdf,inspire,github},build/{tex,code},db,manifests,logs}` (brief 12.2; `kb init`; listed 2026-11-15T18:30Z); `kb/{schema.sql,migrations,kbtool,curated,tests,golden-set copies}` |
| read-only access for tracks | met | `kb` opens `db/current` by default; snapshots mode 0444; `db/current` -> `kb-20261115-44b7406.sqlite` |
| snapshot at the end of the stage | met | wave-1 snapshot kb-20261115-f2fcda5; wave-2 snapshots kb-20261115-621430e, kb-20261115-3826a68 and kb-20261115-44b7406 (run kb-20261115-183052-0f8245e) |

Tests: `cd kb && .venv/bin/python -m pytest`: 173 pass (2026-11-15, after the wave-2 lead's
fixes; `tracks/kb/JOURNAL.md` W1).

Compute: 0 card-hours (allotment 0, decision 0014); at most 8 cores at a time.
