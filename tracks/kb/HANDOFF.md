# HANDOFF of kb

State (2026-11-21 ~13:15 UTC, end of the kb lead session of wave 3 batch 3). The knowledge base
holds 710 papers and 64 repositories; readers use `kb-data/db/current` ->
`kb-20261119-a782f1e.sqlite`; the working kb.sqlite has the claim changes of claims_tracks
batches A1 and B1 since then. KB-G1 is signed; KB-G0 and KB-G2 packages are complete with
independent verifiers and wait for orch's review. Four packages of round 1 were cut on
2026-11-20 and are not finished (table below). No run is going; no card job.

## Run next

```bash
cd /data/haiyangw/nrpic/wt/kb && git merge --no-edit main
harness/bin/nrpic-ctx inbox --show            # orch's answers: kb-g0-g2-gate-review, kb-cut-packages-schedule
git status --short                            # expect the 11 files of claims_tracks and code_kb listed below
(cd kb && .venv/bin/python -m pytest -q)      # the test suite of kb/
```

Then resume the cut packages in this order (tracks/kb/PLAN-wave3.md, round 1, has each brief):

| Package | Committed | In the worktree, uncommitted (left on purpose) | What remains |
|---|---|---|---|
| `ingest3` | nothing | `tracks/kb/ingest3/{figures,ids,scripts}`; private copy `scratch/kb/ingest3/dev/kb` (its `kbtool/papers_cli.py` differs from the tree) | baseline; parser for REVTeX-3 `references`, `\def\bi{\bibitem}`, `\sortbibitem`, AAS `\reference`, `\harvarditem`, unreached .bbl; old-style headings (`{\bf I. ...}`, `\titlea`, `\rma`) and numbered reference lists; abstracts of review papers; claim chunk remap; re-ingest of the 20 papers (stage/KB-G2/OPEN.md) and the 24 wave-3a sources; QA stating the parse rate against the bar; snapshot |
| `claims_tracks` | B0 baseline, tooling, batches A1 (run kb-20261120-222903-226b273) and B1 (kb-20261120-223013-5330e45, ledger rows) | `decisions/{C1,D1,E1}{,_annot}.tsv`, `scripts/batch_{C1,D1,E1}.sh` (written 14:35 PST on 2026-11-20, never run) | read C1, D1, E1 before running them (they were written in the last minute before the cut); F and core batches; requests of B (claims 689-695) and D (682/683); the three kb-requests of 2026-11-21 (B arXiv:2312.12499 factor; A Szekeres conformal flatness; C conductivity sources; replies "queued" posted); audit of 40 machine-located claims; outcome of prediction Q |
| `code_kb` | watch W1, W2, message to core | `JOURNAL.md`: prediction M1 for `kb code modules` (written 22:35Z, before the tool) | `kb code modules` (K7, task-list order), tests, link tests, `<z4c> nco` |
| `claims_brief` | nothing in git | `scratch/kb/claims_brief/` only | seeder `kb claim seed-brief`, tests, join of the brief-check rows, section-5 defect claims |

After ingest3 lands: print the snapshot id in `kb show`, `kb cites` and every JSON search hit
(verifier's C6b; `kbtool/papers_cli.py`, `embed_search.py`), with a test; chmod a-w the raw
`source.bin` files (KB-G0/OPEN.md); re-index this repository at main (core-v0.4 and core-v0.5
added 86 options; the params table is at 5deee18).

## Read first

1. `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and "Gates of the knowledge base"; decisions 0016,
   0019-0021; brief section 12 (lines 1218-1461).
2. `tracks/kb/PLAN-wave3.md`; `tracks/kb/stage/REVIEW-wave3.md` (this session's review);
   `stage/KB-G2/{CHECKLIST,OPEN,VERIFIER}.md`, `stage/KB-G0/{CHECKLIST,VERIFIER}.md`.
3. `kb/README.md` (new section on tool choices), `kb/QA_REPORT.md`; package READMEs and
   journals under `tracks/kb/<package>/`.

## Decisions pending

orch: gate review of KB-G0 and KB-G2 (request kb-g0-g2-gate-review, with a waiver of the harness
"clean" check caused by the cut packages' files); schedule of the cut packages
(kb-cut-packages-schedule); licences; groups of the 26 additions and gr-qc/0608095; section-16
corrections. core: tests for the paper-code links (open since wave 1).

## Traps

- Commit with explicit paths (`git commit -- <paths>`): the worktree holds other packages'
  uncommitted files; `nrpic-run submit --package <dir>` tolerates them, `nrpic-stage verify`
  reports "clean" FAIL because of them.
- Do not edit `kb/kbtool/papers_cli.py` before ingest3 lands its private copy, or one change
  overwrites the other.
- `tracks/kb/verify_g2/heldout.yaml` is a held-out set: never tune retrieval on it.
- A re-ingest renumbers chunks and equations: claims, vectors and tags must follow (remap first).
- `kb claim check --id N` rewrites locator rows of seed claims from the note; never run it after
  `verify --locator` or `relocate` on the same claim (claims_tracks README).
- Use `kb/.venv/bin/python -I kb/bin/kb ...` in runs; never execute anything under kb-data/raw;
  arXiv only through `python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv`, one call
  at a time; paper text never goes into git.
- Snapshots about 1 GB each (nine); keep f2fcda5, 621430e, 44b7406, a848a06, a782f1e.
