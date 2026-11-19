# HANDOFF of kb

State (2026-11-15 19:00 UTC, end of wave 2). The knowledge base holds 709 papers (683 of the 684
manifest ids; gr-qc/9412071 is a PostScript e-print whose PDF is stored but not ingested; 26
extras fetched on the tracks' requests), 64 indexed repositories, vectors of all 43500 text
chunks and 54502 equations (bge-small-en-v1.5, local), 1140 tagged equations and 688 claims.
Readers use `kb-data/db/current` -> `kb-20261115-a848a06.sqlite`. Every kb-request of waves 1
and 2 is answered (`tracks/kb/outbox/20261115T18*`). KB-G0 and KB-G1 packages are complete
except a verifier report; KB-G2 is not met (`stage/KB-G1/OPEN.md`, section KB-G2).

No background job is running. Run next: `cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main && (cd kb && .venv/bin/python -m pytest)`

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
(cd kb && .venv/bin/python -m pytest)                        # 173 tests
python3 -I kb/bin/kb status                                  # counts, snapshot id
harness/bin/nrpic-ctx inbox                                  # new kb-requests
# every command that writes goes through nrpic-run (the tree must be committed first):
harness/bin/nrpic-run submit --kind scouting --gate G1 --allow-no-venv --purpose "..." -- \
    bash -c 'kb/.venv/bin/python -I kb/bin/kb ...'          # use kb/.venv, not bare python3
```

Then, in this order: (1) a reader for `raw/arxiv/<key>/<v>/source.pdf` in inventory and ingest,
then ingest gr-qc/9412071 (and re-ingest astro-ph/9407016, status failed, which also has a PDF);
(2) read `kb-data/meta/arxiv-api/<key>.json` and `meta/inspire/<key>.json` into the papers table
and fill `title_matches_brief` against brief section 16; (3) change `kb/kbtool/qa_report.py` C4 to
read `meta/inspire/<key>.json` and rerun `kb qa run --hybrid`; write `kb/QA_REPORT.md` and
`kb/golden/questions.yaml`; (4) after every ingest: `kb eq --apply-tags`, `kb embed`,
`kb embed --check --work`, `kb snapshot`.

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners"; brief section 12 (lines 1218-1461).
2. `kb/README.md`, `kb/EMBEDDING.md`; `tracks/kb/stage/REVIEW-wave2.md` (what each wave-2
   package established, what was wrong).
3. `tracks/kb/stage/KB-G1/{OPEN,EVIDENCE}.md`; `tracks/kb/JOURNAL.md` (lead checks L0-L11 of wave
   1, W1-W10 of wave 2); package journals `tracks/kb/{served,claims,embed}/JOURNAL.md`.

## Decisions pending

orch: verifier for kb packages; KB-G2 thresholds and the hit level (paper 28/32, answer location
23/32 on the golden set); non-arXiv PDF for core's Philox paper; the 26 extras as manifest
additions with groups (F asks G21 for seven); two lines for harness/RULES.md (literal
`$NRPIC_RUN_DIR`, PATH python). From wave 1: brief corrections; paper-code-link tests (core).
Tracks: E checks eq. (17) vs (23) of 2502.06783; D gives run ids for its measured values (claims
682, 683); C gives the file of its astro-ph/0111176 locator.

## Traps

- Since this session `wt/kb/.venv` exists (`nrpic-env create --no-kokkos`, for nrpic-stage
  verify). nrpic-run puts it first on PATH, so `python3` in a run command is that venv, which has
  no PyYAML or torch: call kb tools with `kb/.venv/bin/python -I kb/bin/kb ...` (run
  kb-20261115-182907-3f69615 failed on this).
- nrpic-run does not expand `$NRPIC_RUN_DIR` in arguments: scripts read it from the environment
  (`os.environ["NRPIC_RUN_DIR"]`), or the output lands in the worktree (run
  kb-20261115-181519-d78b8d4).
- kb's allotment is 8 cores at a time (nrpic-run refuses more); embedding uses `--threads 8`.
- Claim ids are frozen: `kb claim seed --rebuild` refuses once db/current holds claims; new
  statements go in by `kb claim add` or `kb/serve_locate.py sync-k8` (idempotent on seed keys).
- The quality score is not correctness (wave 1); the independent counters are
  `kb/kbtool/qa_eqcount.py` and `tracks/kb/analysis/lead_checks/eqcount.py` (both now number an
  empty last row after a trailing `\\`, as pdflatex does).
- Never execute, compile or import anything under kb-data/raw; metadata and e-prints only through
  `python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv`, one call at a time.
- Paper text never goes into git: reports carry ids, counts and our own wording; reading samples
  stay in scratch/kb/<run_id>/.
- Snapshots are up to 1 GB each (eight now, 6.1 GB); keep those cited in notes (f2fcda5,
  621430e, 44b7406, a848a06), prune others by name if disk becomes short.
