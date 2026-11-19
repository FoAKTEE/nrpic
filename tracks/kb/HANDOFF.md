# HANDOFF of kb

State (2026-11-19 ~16:45 UTC, end of wave 2b). The knowledge base holds 710 papers (all 684 ids of
brief section 17, gr-qc/9412071 read from its PDF, and 26 manifest additions with groups in
`kb/manifests/arxiv_additions.tsv`), arXiv-API and INSPIRE metadata in the papers table, 64
repositories with this repository indexed at main 5deee18, vectors of all 43560 text chunks and
54502 equations, 700 claims. Readers use `kb-data/db/current` -> `kb-20261119-a782f1e.sqlite`.
KB-G1 package complete with a verifier report; KB-G2 thresholds met on a782f1e (parse ok 684/710,
golden paper 28/32) but the package lacks a verifier (`stage/KB-G2/OPEN.md`). No run is going.

Run next: `cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main && (cd kb && .venv/bin/python -m pytest -q)`

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
(cd kb && .venv/bin/python -m pytest -q)                     # 220 collected, 1 strict xfail
kb/.venv/bin/python -I kb/bin/kb status --json | head        # snapshot id, counts
harness/bin/nrpic-ctx inbox --show                           # orch answers to kb-gates-wave2b etc.
# every command that writes goes through nrpic-run (commit first; the tree must be clean):
harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 6 --allow-no-venv --purpose "..." -- \
    bash -c 'kb/.venv/bin/python -I kb/bin/kb ... > "$NRPIC_RUN_DIR/out.txt"'
```

Then, in this order: (1) bibliography parser (`kb/kbtool/tex_structure.py` or the bib module):
REVTeX-3 `\begin{references}` with `\bibitem`, AASTeX `\reference`, `\bi`/`\bib` macros, `\harvarditem`
in .bbl, a .tex with `\bibitem` the main file does not reach; status review when `\cite` is present
and no entry results; test on the 20 papers of `stage/KB-G2/OPEN.md`; (2) before re-ingesting them,
a remap of claims.chunk_id and claim_locators.chunk_ids_json from flat ranges (re-ingest renumbers
chunks; 627 claims carry a chunk); then `kb ingest arxiv --id ...`, `kb eq --apply-tags`, `kb embed`,
`kb embed --check --work`, `kb qa run --hybrid`, `kb snapshot`; (3) on orch's answer, the KB-G2
verifier and the held-out golden set (run blind, no tuning).

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and "Gates of the knowledge base"; decision 0016;
   brief section 12 (lines 1218-1461).
2. `kb/README.md` (section "Wave 2b additions" for the new commands), `kb/QA_REPORT.md`.
3. `tracks/kb/stage/REVIEW-wave2.md` (waves 2 and 2b), `stage/KB-G1/{CHECKLIST,VERIFIER,OPEN}.md`,
   `stage/KB-G2/{CHECKLIST,EVIDENCE,OPEN}.md`; `tracks/kb/JOURNAL.md` (B1-B3, D1, D2, Q1, V1).
4. Package journals `tracks/kb/{pdf_meta,retrieval}/JOURNAL.md`, `stage/KB-G1/JOURNAL.md`.

## Decisions pending

orch: KB-G1 review and whether the registered rerun (kb-20261119-161909-08df7ea) stands for the
verifier's three hand-written runs; a KB-G2 verifier; a held-out golden set; groups of the 26
additions and gr-qc/0608095; licences (arXivRaw mode or not needed); section-16 corrections
(pdf_meta's outbox 20261119T143821Z). From earlier waves: brief corrections; paper-code-link tests
(core). Tracks: none waiting on kb (B, C, D, E answered in wave 2b).

## Traps

- `kb ingest arxiv` now reads the metadata back (`kb meta load` for the ingested ids); a re-ingest
  still renumbers chunks and equations: claims, vectors and tags must follow (see Run next).
- `kb claim verify --locator` and `kb claim relocate` rewrite claim_locators; they do not change a
  claim's status (D's claims 697-700 show "unlocated" with resolved rows).
- nrpic-run refuses a dirty tree: delete or commit stray figure files before a submit (a figure
  script writes into tracks/kb/note/figures/).
- Use `kb/.venv/bin/python -I kb/bin/kb ...` in runs; `python` under nrpic-run is wt/kb/.venv
  (no torch, no PyYAML).
- Never execute anything under kb-data/raw; arXiv and metadata only through
  `python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv`, one call at a time.
- Paper text never goes into git: reading samples stay in scratch/kb/<run_id>/.
- Brief: read only the line ranges a task names; the section-16 comparison is done by code
  (`kb meta brief16`).
- Snapshots about 1 GB each (seven in kb-data/db); keep f2fcda5, 621430e, 44b7406, a848a06,
  a782f1e (cited in notes and packages).
- wt/kb-brief (branch kb/brief-check, wave 3a) also runs as owner kb and writes scratch/kb/;
  its runs are not this branch's.
