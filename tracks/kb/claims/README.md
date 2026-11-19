# tracks/kb/claims: stages K8 (statements and evidence) and K9 (quality report)

Helper package of owner kb, wave 2 (brief section 12, lines 1400-1429). Predictions and
outcomes: `JOURNAL.md` (P1-P6 and one incident). Code in `kb/kbtool/claims_*.py`,
`kb/kbtool/qa_*.py`, tests in `kb/tests/test_claims.py`, `test_qa_eqcount.py`,
`test_qa_report.py` (31 tests, all pass).

## What is in this directory

| File | What |
|---|---|
| `JOURNAL.md` | predictions before each run, outcomes after it (P1-P6), the incident of the rebuild |
| `QA_REPORT.md` | the quality report of brief 12.9, checks C1-C10 (run kb-20261115-155508-2e00432); ids and counts only |
| `qa.json` | every number of that report (input of the figures) |
| `fig_qa_claims.{png,pdf}` | claims per track by status, and by label |
| `fig_qa_eqcount.{png,pdf}` | independent count of numbered display lines against the database, 41 papers |
| `fig_qa_retrieval.{png,pdf}` | rank of the expected paper and lines for the 32 golden questions, BM25 and hybrid |
| `claims_seed.tsv` | the 618 claims of the final seed (run kb-20261115-154020-7b80ccc): id, track, label as written, label, status, kind, paper, locator, numbers checked and missing, origin, the track's own wording |
| `golden_questions.yaml` | the 32 golden questions in the layout of brief 12.2 (`kb qa golden --yaml`) |

## The code

| Module | What |
|---|---|
| `claims_parse.py` | the tracks' notes (Markdown) -> claims: units (bullets, table rows, paragraphs), paper context from headings, five locator styles (`(L264-268)`, bare `(879-882)`, `main.tex:103-118`, `` `:60-74` ``, `` `TBH3.tex` lines 582-626 ``, `l. 361`), labels before and after locators, repository files and brief lines excluded; `wave1_sources()` names the nine notes |
| `claims_curated.py` | the errata requests of E-stoch-inf and C-sidm, transcribed one defect per claim with locators and run ids (label judgement) |
| `claims_check.py` | the knowledge base's own check of each locator: paper in the store, file (exact or unique base name), lines within the file, flat.tex range and chunks through `sourcemap.json`; numbers of the claim found in the cited lines +-3 (as written or rounded); cited lines that are all TeX comments make the claim partial |
| `claims_db.py` | `claims` (brief schema) plus `claim_meta`, `claim_locators`, `claim_events` (IF NOT EXISTS, no migration number taken; DDL in `CLAIMS_DDL`); label rules; verify, refute, add; a judgement is never upgraded to fulltext |
| `claims_cli.py` | `kb claim seed [--dry-run] [--tsv P] [--rebuild] / check / list / show / add / verify / refute / stats` |
| `qa_eqcount.py` | independent counter of numbered display lines (stack scanner; shorthands such as `\be`, `\bea`; rows of align-like environments; numbered empty last row, as pdflatex does) |
| `qa_golden.py` | 32 golden questions (own wording; answers from KB-G1 and from claims a person checked) and the hit test (paper; lines +-5) |
| `qa_report.py` | checks C1-C10 and the Markdown report |
| `qa_cli.py` | `kb qa run [--out] [--json] [--hybrid] [--eq-sample N]`, `kb qa golden [--yaml P]` |
| `qa_figures.py` | the three figures (style `python/nrpic/figstyle.py`) |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
(cd kb && .venv/bin/python -m pytest tests/test_claims.py tests/test_qa_eqcount.py tests/test_qa_report.py \
   --basetemp=/data/haiyangw/nrpic/scratch/kb/tmp/pytest-claims -p no:cacheprovider)
# until the lead wires them into kb/bin/kb (Requests 1), the modules run as scripts:
python3 -I kb/kbtool/claims_cli.py claim seed --dry-run --tsv /data/haiyangw/nrpic/scratch/kb/tmp/seed.tsv
python3 -I kb/scripts/registered_run.py --purpose "..." -- python3 -I kb/kbtool/claims_cli.py claim seed --tsv '{run_dir}/claims_seed.tsv'
python3 -I kb/kbtool/claims_cli.py claim list --track C-sidm --status partial
python3 -I kb/kbtool/claims_cli.py claim show 605
python3 -I kb/kbtool/claims_cli.py claim verify N --by "<who>" --evidence "<what was read>"
python3 -I kb/kbtool/claims_cli.py claim refute N --by "<who>" --evidence "<counter-example>"   # prints the tracks to notify
python3 -I kb/kbtool/claims_cli.py claim stats
OMP_NUM_THREADS=4 python3 -I kb/scripts/registered_run.py --cores 4 --purpose "..." -- \
  kb/.venv/bin/python -I kb/kbtool/qa_cli.py qa run --hybrid --out '{run_dir}/QA_REPORT.md' --json '{run_dir}/qa.json'
kb/.venv/bin/python -I kb/kbtool/qa_figures.py <run_dir>/qa.json <out_dir>
```

Writes go to `kb-data/db/kb.sqlite` inside `locks/kb-writer.lock`; `kb qa run` only reads.
`seed` is idempotent (stable seed keys); `--rebuild` removes only rows of the K8 seed and
refuses once a snapshot holds claims or a person has set a label (it now refuses: 29
claims are checked). No snapshot was taken by this package: the claims are in kb.sqlite,
not yet in `db/current`.

## State (2026-11-15 16:00 UTC)

- [VERIFIED, run kb-20261115-154020-7b80ccc and `kb claim stats`] 618 claims on 70 papers
  from 9 sources (A, B, C, D REFERENCES.md; C's G0 report section 6; F's NOVELTY.md;
  core's SECTION2_CORRECTIONS.md; the errata requests of C and E): fulltext 507, to_verify
  73, judgement 37, background 1; 678 of 679 locators resolve; statuses checked 29,
  located 516, partial 33, unlocated 39, unresolved 1.
- [VERIFIED, audit P2] 29 of 30 sampled fulltext claims are supported by the cited lines
  (the one failure was a parser split, fixed); those 29 are marked checked by a person
  (run kb-20261115-154041-7b80ccc; its manifest's purpose says 28, its stdout lists 29).
- Errata of E-stoch-inf (answer to its kb-request: claim ids 603-609) and of C-sidm
  (610-618) are claims with label judgement and the runs as evidence
  (`claim list --track E-stoch-inf`).
- [VERIFIED, runs kb-20261115-155508-2e00432, kb-20261115-155344-596b4ce] QA: counts agree
  with the manifest except gr-qc/9412071 (PostScript only); 25 papers not ok, classified;
  INSPIRE sample blocked (no metadata on disk); 59.9 % of bibliography entries with an
  arXiv id, 14.8 % of distinct arXiv citation edges inside the corpus; no duplicates;
  BM25 golden hit rate 27/32 papers, 21/32 lines, hybrid 22/32 and 15/32; independent
  equation count 41/41 exact (2295 lines); 27/27 suite references ingested.

## Not done

- The INSPIRE comparison of 30 papers (C4): no metadata on disk; the code is tested on
  synthetic records only.
- The brief's own labelled statements (brief 12.8, first item) are not seeded: this
  package seeded the tracks' wave-1 statements as its task said; a brief seed would need
  reading the brief beyond the line ranges given to this helper.
- No snapshot; no wiring into `kb/bin/kb`; `kb/QA_REPORT.md` and `kb/golden/questions.yaml`
  are not written (outside this package's paths).
- The 39 unlocated and 73 to_verify claims are not worked through; 1 unresolved (claim
  303: C's note gives a bare line number without a paper).
- Hybrid retrieval was measured with half of the chunks embedded; to be re-run when K4
  has embedded all.
- Recall of the parser not measured by me. The serve helper's independent extraction of
  the same notes (its run kb-20261115-154906-f19880f, `tracks/kb/served/claims/`) maps 258
  of its 330 statements to K8 claims and lists 70 it found no K8 claim for in
  `tracks/kb/served/claims/uncovered_seed.jsonl` (its numbers, not rechecked here). They
  are not in the claims table yet.

## Requests

1. **lead (kb): wiring.** Add to `kb/kbtool/cli.py`, next to the other registers:
   `from . import claims_cli as _claims_cli`, `from . import qa_cli as _qa_cli`,
   `_claims_cli.register(sub)`, `_qa_cli.register(sub)`, and `_claims_cli.CLAIMS`,
   `_qa_cli.CLAIMS` in the stub filter. Then `kb qa run` writes `kb/QA_REPORT.md` (copy of
   `tracks/kb/claims/QA_REPORT.md`), and `kb qa golden --yaml kb/golden/questions.yaml`
   writes the golden set where brief 12.2 puts it. Optionally move `claims_db.CLAIMS_DDL`
   into `kb/migrations/` (next free number).
2. **lead (kb) and the serve helper: incident.** My `kb claim seed --rebuild` at 15:39:43
   and 15:40:23 UTC (runs kb-20261115-153942-e70f45d, kb-20261115-154020-7b80ccc) deleted
   the 330 claims (origin `served:*`) that run kb-20261115-153751-e164901 had loaded at
   15:37:51. Fixed since (rebuild, re-check and stale-marking touch only K8-seed rows,
   commit daa0aa2, test `test_rebuild_and_stale_leave_other_writers_rows`). Please re-run
   the serve package's `sync-k8` and do not hand the tracks claim ids from that run.
3. **lead (kb): snapshot.** Run `kb snapshot` once the serve helper's sync is in, so that
   readers see the claims and the claim ids are frozen.
4. **lead (kb) / K2: extractor defect.** astro-ph/0003278 (`separate.tex`,
   `\documentstyle{revtex}`, unbraced `\input epsf` at line 16) has `\section` at lines 80,
   145, 278, 484, 659, but the database holds 0 sections for it.
5. **lead (kb): your checker L5.** `tracks/kb/analysis/lead_checks/eqcount.py` drops a
   trailing `\\` before `\end` for ams environments; pdflatex numbers that empty row in
   align, gather and eqnarray (run kb-20261115-155344-596b4ce). kbtool's extractor is right.
6. **K4 helper (embed_search).** `Locator.lines` raises IndexError for a paper with an
   empty `sourcemap.json` (2201.03458, astro-ph/9407016); `kb search` crashes whenever such
   a paper is among the hits (my run kb-20261115-154858-b0d8c8f). Guarded in `qa_report`
   only. Hybrid retrieval scored 22/32 against 27/32 for BM25 alone with half of the chunks
   embedded: worth re-testing with the golden set (`kb qa run --hybrid`) after the full embed.
7. **lead (kb): tests of other modules.** After the merge of main, 17 tests fail in
   `tests/conftest.py:89` (`nrpic_fetch_arxiv` has no attribute `unpack`): the fixture
   loads a function of the harness fetch command that the new main no longer has.
8. **orch / harness: run registration.** `harness/bin/nrpic-run submit` refuses the shared
   kb worktree whenever another helper has an untracked file, so every run of this package
   is registered by hand with `kb/scripts/registered_run.py` (10 manifests under
   `tracks/kb/runs/`, each with a note saying so).
9. **orch: metadata.** C4 needs INSPIRE records under `kb-data/meta/arxiv/<id_>.inspire.json`
   (`qa_report._meta_record` reads `.inspire.json` or `.api.json` with `titles`/`title` and
   `authors`); the sample of 30 is fixed (seed 20261115) and listed in the report.
10. **lead (kb): the 70 uncovered statements** of the serve helper
    (`tracks/kb/served/claims/uncovered_seed.jsonl`): load them once, either with its
    `kb/serve_locate.py sync-k8` (seed keys `served:<key>`, which the K8 seed never touches
    now) or by extending `claims_parse` where they show a missed locator style; not both.
11. **tracks (through the lead):** cite literature statements by claim id
    (`kb claim list --track <ID>`); a statement whose number is missing at the cited lines
    is `partial` (33, see `claims_seed.tsv` column `missing`), most of them the tracks' own
    values next to the paper's.
