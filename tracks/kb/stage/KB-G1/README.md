# KB-G1 verifier package (helper of kb, wave 2b)

This directory is the stage package of gate KB-G1 of the knowledge base. The files of the kb
lead (`CHECKLIST.md`, `EVIDENCE.md`, `OPEN.md`, `SCOPE.md`, `STAGE_REPORT.md`, `REVIEW.md`,
`VERIFY*`, `FIRST_QUESTIONS.md`, `priority3_ingestion.tsv`) are theirs; this README covers
what the verifier added:

| Path | What |
|---|---|
| `VERIFIER.md` | the verifier's report: verdicts per item, defects, requests |
| `JOURNAL.md` | predictions (written before the checks) and outcomes |
| `verifier/texcount.py` | my own TeX reader: main file, flattening, equations, numbered rows, equation numbers per label, sections, bibliography formats |
| `verifier/check_papers.py`, `fig_papers.py` | test P: 20 sampled papers against the snapshot |
| `verifier/check_claims.py` | test C: 10 sampled `fulltext` claims and their source lines (excerpts stay in scratch) |
| `verifier/check_params.py` | test K: 10 parameter rows, recall at the indexed commit, staleness against `main` |
| `verifier/check_answers.py` | test Q: equation numbers and every locator cited in `FIRST_QUESTIONS.md` |
| `verifier/check_zero_bib.py` | follow-up of P: TeX papers without bibliography entries |
| `verifier/check_locator_rows.py` | follow-up of C: locator strings against locator rows |
| `verifier/fig_summary.py`, `verdicts.tsv` | summary figure; the verdict of every item |
| `verifier/run_all.py` | runs P, C, K, Q and the figures into one directory |
| `verifier/figstyle.py` | copy of `harness/style/figstyle.py` |

Runs (manifests in `tracks/kb/runs/<run_id>/manifest.json`, hand-written; outputs under
`scratch/kb/<run_id>/`): `kb-20261119-142015-7620bd4`, `kb-20261119-142303-f38a48c`,
`kb-20261119-142448-3ea268d`.

## Rerun

From the worktree root (`/data/haiyangw/nrpic/wt/kb`), with the worktree's `.venv`
(numpy, matplotlib); everything else is the standard library:

```text
OMP_NUM_THREADS=1 .venv/bin/python -I tracks/kb/stage/KB-G1/verifier/run_all.py <outdir>
OMP_NUM_THREADS=1 .venv/bin/python -I tracks/kb/stage/KB-G1/verifier/check_zero_bib.py <outdir>
OMP_NUM_THREADS=1 .venv/bin/python -I tracks/kb/stage/KB-G1/verifier/check_locator_rows.py <outdir>
```

Or registered: `harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher local
--package tracks/kb/stage/KB-G1 --purpose "..." -- python3 -I
tracks/kb/stage/KB-G1/verifier/run_all.py` (needs a clean `kb/`). The scripts open
`kb-data/db/current` read-only and read `kb-data/raw` as data. The samples are fixed by the
seed 20261119; a new snapshot changes the populations and so the samples.

## Requests

To kb (lead), details in `VERIFIER.md`:
1. Read REVTeX-3 `references` environments, AASTeX `\reference`, `\bibitem` aliases and
   `\harvarditem`; flag a paper with `\cite` commands and zero bibliography entries.
2. Re-index `local/nrpic` at the current `main` (core-v0.3 options missing from `params`).
3. Restore locator L1084 of claim 25.
4. Keep shared code in `kb/` committed while helpers register runs, or say how helpers should
   register when the shared worktree is dirty (three manifests here are hand-written).

To others: none.
