# tracks/kb/pdf_meta: PDF reader, metadata in the papers table, brief section 16, manifest additions

Helper package of kb, wave 2b (2026-11-19). Predictions and outcomes: `JOURNAL.md` (P1-P7).

## What is in this directory

| Path | What |
|---|---|
| `JOURNAL.md` | predictions P1-P7 written before each run, outcomes with run ids (failed predictions kept) |
| `BRIEF16_ERRATA.md` | brief section 16 against the arXiv and INSPIRE records: proposed rows for `coord/BRIEF_ERRATA.md` (A), titles that follow the published title (B), author order that follows INSPIRE (C), collaborations (D) |
| `brief16_comparison.tsv` | one row per section-16 entry: line, groups and priorities of sections 16 and 17, title and author classes against arXiv and INSPIRE (no titles) |
| `figures/fig_pdf_reader.{png,pdf}` | left: rare-token fraction of the three PDF papers before (grey) and after (red) the repairs; middle: repairs by kind (log); right: similarity of the located abstract to the arXiv abstract on the raw (grey) and repaired (red) text, dashed line the threshold 0.6 above which a paragraph run counts as the abstract |
| `figures/fig_brief16.{png,pdf}` | left: title classes of the 684 entries against the arXiv title; middle: author classes against the arXiv list; right: per group, the fraction of entries that agree with arXiv or INSPIRE in title and authors |
| `figures/fig_metadata.{png,pdf}` | left: similarity of the TeX-extracted title to the arXiv title (673 TeX papers with a title; dashed 0.9); middle: TeX abstract chunk against the arXiv abstract (682; dashed 0.8); right: papers per group, section 17 (blue) and manifest additions (red) |
| `figures/fig_numbers.json` | the numbers behind the figures |
| `scripts/fig_pdf_meta.py` | the figures (style `scripts/figstyle.py`, vendored from `harness/style/`) |
| `scripts/audit_repairs.py` | draws repairs of the PDF reader at random for reading (P1 precision) |

Code outside this directory (written by this package, tests in `kb/tests/`):

| Path | What |
|---|---|
| `kb/kbtool/pdf_reader.py` | which PDF (`source.pdf` of `nrpic-fetch-arxiv --pdf`, or an e-print that is a PDF), checks from the bytes against the record, `pdftotext` under limits in an empty directory, repairs (f-ligatures lost by Type-3 fonts, OT1 control characters and punctuation, cmmi Greek, line-end hyphens; every edit recorded), structure (pages, abstract located against the arXiv abstract, Roman/numbered/lettered/appendix headings, PRL run-in headings, standalone headings, captions, numbered and author-year reference lists with arXiv ids and DOIs, numeric citation markers) |
| `kb/kbtool/pdf_ingest.py` | `python -I -m kbtool.pdf_ingest --all \| --id ID`: selects the store entries without usable TeX, writes `kb-data/build/tex/<key>/{flat.tex, doc.json, pdf_raw.txt, pdf_edits.json}` and the rows (parse_status `pdf`, source_kind `pdf`) through `papers_ingest.write_paper`, then loads the metadata of the paper |
| `kb/kbtool/meta_brief16.py` | brief section 16 read by script (684 entries, groups, marks, author fields), title and author comparison classes |
| `kb/kbtool/meta_papers.py` | `python -I -m kbtool.meta_papers load` (metadata into `papers`, idempotent) and `brief16` (comparison report) |
| `kb/kbtool/meta_manifest.py` | the manifest additions file and `load_full_manifest()` (section 17 + additions) |
| `kb/manifests/arxiv_additions.tsv` | the 26 extra papers with group, priority, requester and decision (0016 item 6) |
| `kb/tests/test_pdf_reader.py`, `kb/tests/test_meta_papers.py` | 35 tests (9 + 26: hand-made PDFs, synthetic stores, the real brief); the whole kb suite, 212 tests, passes on the final code (pytest exit 0, 2026-11-19 14:5x UTC) |

## Results (run ids)

- **gr-qc/9412071 is in the knowledge base** from its stored PDF (run kb-20261119-142651-7318d01):
  4 pages, 6 run-in sections, 16 chunks with vectors, 1 caption, 19 references, 32 citation
  keys; abstract located with similarity 0.994 to the arXiv abstract. The same run re-ingested
  astro-ph/9407016 (was `failed`: a tar of PostScript; now 28 pages, 12 sections, 45 chunks, 22
  references) and 2201.03458 (an e-print that is a PDF; now 5 sections and 70 references
  instead of none). Vectors and citation edges: run kb-20261119-143251-eb99c45 (74 chunks
  embedded, 14 orphans removed, `kb embed --check --work` clean). Hybrid search ranks each of
  the three first or second for a query in other words (run kb-20261119-143441-b46b992).
- **Repairs**: 30 of 30 randomly drawn word repairs are right (run kb-20261119-143005-10376d4).
  Rare-token fraction 4.72 % -> 1.70 % (astro-ph/9407016), 6.50 % -> 4.33 % (gr-qc/9412071; the
  rest is equation index notation and names).
- **Metadata in `papers`** (final load run kb-20261119-143702-aa436e7): 710 of 710 papers with
  the arXiv title, authors, abstract, primary class, dates (title_source `arxiv-api`; the TeX
  values kept in `parse_json.tex_front`); 706 with an INSPIRE record number; DOI 651, journal
  reference 648; licence 0 (the arXiv-API answer has no licence element). Stored version =
  latest arXiv version for all 710. Missing metadata fetched in run kb-20261119-142559-387c3bc
  (2107.06643, 2201.09277); 1609.03053, 1612.06734, 1709.00267, 2409.16053 have no INSPIRE
  record (queried one at a time).
- **Brief section 16** (run kb-20261119-143702-aa436e7): same ids, groups and priorities as
  section 17; 680 of 684 entries agree with arXiv or INSPIRE in title and authors
  (`papers.title_matches_brief` 1 for 680, 0 for 4, NULL for the 26 additions); 3 author errors
  and the record typo of gr-qc/0312117 are in `BRIEF16_ERRATA.md` and in the outbox message
  `tracks/kb/outbox/20261119T143821Z__to-orch__brief16-titles-authors.md`.
- **Manifest additions**: 26 rows in `kb/manifests/arxiv_additions.tsv`; every paper has a group
  (G04 1, G06 6, G14 1, G18 11, G21 7). F's seven papers are in G21 as F asked.
  gr-qc/0608095 (laser interferometry, no requester found) has the placeholder G06 and is
  proposed for removal.

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
(cd kb && .venv/bin/python -m pytest -q tests/test_pdf_reader.py tests/test_meta_papers.py \
    --basetemp=/data/haiyangw/nrpic/scratch/kb/tmp/pytest-pdfmeta)
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/kb/pdf_meta --cores 1"
# metadata of ids without records (one process, sequential, through the one fetch command)
$R --allow-no-venv --purpose "..." -- bash -c 'python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv --meta --service both <ids>'
# PDF papers (writes kb.sqlite under the writer lock; the vocabulary is built from kb.sqlite, about 4 min)
$R --purpose "..." -- kb/.venv/bin/python -I -m kbtool.pdf_ingest --all
# metadata into papers and the section-16 report (after every ingest: the ingest rewrites title, authors, abstract)
$R --purpose "..." -- bash -c 'kb/.venv/bin/python -I -m kbtool.meta_papers brief16 --out "$NRPIC_RUN_DIR"; kb/.venv/bin/python -I -m kbtool.meta_papers load --out "$NRPIC_RUN_DIR"'
# vectors of new chunks, coverage, citation edges
$R --cores 2 --purpose "..." -- bash -c 'kb/.venv/bin/python -I kb/bin/kb embed --only chunks --threads 2; kb/.venv/bin/python -I kb/bin/kb embed --check --work; kb/.venv/bin/python -I kb/bin/kb resolve-bib'
# figures
$R --purpose "..." -- bash -c 'kb/.venv/bin/python -I tracks/kb/pdf_meta/scripts/fig_pdf_meta.py "$NRPIC_RUN_DIR" <pdf run dir> <brief16 run dir> <load run dir>'
```

## Requests

To the kb lead:
1. Snapshot: `db/current` is still kb-20261115-a848a06; readers see gr-qc/9412071, the metadata
   and the groups only after `kb snapshot` (not taken here: other helpers write kb.sqlite too).
2. Wiring (files outside this package's paths): (a) `kb ingest pdf` and `kb meta load|brief16`
   in `kbtool/cli.py`; (b) the callers of `brief.load_arxiv_manifest` (`papers_cli._manifest_rows`,
   `inventory.verify`, `qa_report.c1_counts`, `cli` status and show) should use
   `meta_manifest.load_full_manifest()` so the 26 additions count as manifest rows and a
   re-ingest keeps their group; (c) `papers_ingest.store` should call
   `meta_papers.load(lay, ids=[pid])` after writing a paper, or every `kb ingest` must be
   followed by `meta_papers load` (a re-ingest rewrites title, authors, abstract, parse_json
   and grp from the TeX and the brief manifest).
3. QA (`kbtool/qa_report.py`): C2 counts `papers.abstract`, which now always holds the arXiv
   abstract: count the abstract chunk instead; C4 compares `papers.title` (now the arXiv title)
   with INSPIRE: for a check of the TeX extraction use `parse_json.tex_front`. The 3 PDF papers
   have parse_status `pdf`; whether that counts as parse success for KB-G2 is the lead's call.
4. TeX title extraction (found in P3): 9 papers carry \thanks text, preprint numbers or dropped
   macros in the extracted title (1503.07831, 1912.04213, 2103.01183, 2112.01508, 2202.10798,
   2402.12672, 2409.16053, astro-ph/9906391, gr-qc/9805063); 34 TeX papers have no extracted
   title. Harmless for `papers.title` now, still a defect of `tex_structure`.

To orch:
1. The brief-errata rows (outbox `20261119T143821Z__to-orch__brief16-titles-authors.md`).
2. gr-qc/0608095: keep (placeholder G06) or drop from the manifest additions.
3. The groups of the 26 additions are kb's [JUDGEMENT] (alternatives named in the file:
   2201.09277 G03, 2605.30145 G07, astro-ph/0608642 G13): confirm or amend.
4. Licences: the arXiv API does not return them; if `papers.license` is wanted, the fetch
   command needs a mode for the OAI-PMH arXivRaw format (a harness change).

To F-hills (information): the seven papers asked for are in G21.
