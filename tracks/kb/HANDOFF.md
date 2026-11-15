# HANDOFF of kb

State (2026-11-15 14:30 UTC). The knowledge base holds all 684 manifest arXiv ids (683 verified
TeX or PDF; gr-qc/9412071 is PostScript only), 701 papers ingested (sections, chunks with full
text search, 53862 equations, figures, 64248 bibliography entries, citation graph) and 64
repositories indexed read-only (upstream AthenaK c5a0d7f and this tree with parameter
tables). The KB-G1 package is submitted (`tracks/kb/stage/KB-G1/`); stages K4, K5, K8-K11 and
the metadata part of K1 remain. Readers use `kb-data/db/current` ->
`kb-20261115-f2fcda5.sqlite`.

No background job is running. Both arXiv downloads finished on their own: priority 3 (run
kb-20261115-112522-3ac74c2, process 966412, log
`scratch/kb/kb-20261115-112522-3ac74c2/stdout.log`) and priorities 2+1 (run
kb-20261115-124340-9048b83, process 1935449, log `scratch/kb/kb-20261115-124340-9048b83/stdout.log`).
The rerun of verify-downloads (kb-20261115-140336-29f15a1) shows 0 missing.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
(cd kb && .venv/bin/python -m pytest)                      # 110 tests
python3 -I kb/bin/kb status                                # counts, snapshot id
python3 -I kb/bin/kb verify-downloads --report kb/reports/verify-downloads.md   # picks up new store entries
python3 -I kb/bin/kb watch upstream --report kb/reports/code_watch_upstream.md # weekly; no scheduler yet
```

Every command that writes is run through `python3 -I kb/scripts/registered_run.py --purpose
"..." -- <command>` (manifest in `tracks/kb/runs/<run_id>/`, add it with `git add -f`
because the shared ignore list matches `runs/`). Then serve the inbox (below), then K8.

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; brief section 12 (lines 1218-1461).
2. `kb/README.md` (commands, modules, how to rerun each stage).
3. `tracks/kb/stage/KB-G1/{EVIDENCE,OPEN,FIRST_QUESTIONS}.md`.
4. `tracks/kb/JOURNAL.md` (lead entry: checks L0-L11) and `kb/JOURNAL.md` (the helpers'
   predictions and outcomes, K0-K1, K2-K3, K6-K7).

## Inbox (tracks/kb/inbox_acks.txt)

Five kb-requests, all queued: A (index its 12 S1 references; ingest 5 more, 2605.30145 is not
in the store), B (index 11 sources; fetch 2212.00425, 1704.03500, 2012.14016, 2610.08045 and
more), C (record source typos of 2108.11967 and gr-qc/0601112; find identifiers for SIDM
transport references), E (errata for 2502.06783 and 2610.32592). New arXiv ids only through
`python3 -I harness/bin/nrpic-fetch-arxiv <id> ...` (or `kb fetch-missing`), then
`kb verify-downloads` and `kb ingest arxiv --new --extras`. Errata and located statements
belong in the claims table (K8), which is not built.

## Decisions pending (outbox 20261115T1420Z__*)

orch: metadata path (arXiv API, INSPIRE); PDF mode and hardening of nrpic-fetch-arxiv;
ignore pattern `runs/`; brief corrections (line 130, grouping, frontier); weekly watch
scheduler; KB-G2 thresholds; embedding model download. core: tests that verify the 25
paper-code links; dead `<z4c> nco`.

## Traps

- Quality score is not correctness: two macro patterns silently dropped equations in 28
  papers with good scores. Check equation rows against an independent count when a paper
  matters (`tracks/kb/analysis/lead_checks/eqcount.py`, `eqcount_alias.py` are the lead's
  checkers; the fixed code is `kb/kbtool/tex_macros.py`, `tex_structure.py`).
- `kb/scripts/fig_inventory.py` and `fig_lead_equations.py` take an output stem without
  extension (they append .png and .pdf).
- `registered_run.py` names runs by the second; two runs started in the same second collide
  (FileExistsError); start the second one a second later.
- `kb ingest repo` needs `kb/.venv` (tree-sitter); the rest runs under `python3 -I`.
- Never execute, compile or import anything under kb-data/raw; git reads of the watch mirror
  run with `GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null` and hooks off.
- Temporary files under `scratch/kb/tmp/`, never /tmp. Kill only by numeric pid.
- Paper text never goes into git: reports carry ids, counts and our own wording.
