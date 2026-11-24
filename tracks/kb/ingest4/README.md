# Package ingest4 (kb, wave 3 batch 11): sources the tracks asked for; old-style reference lists

Helper package of kb, 2026-11-24 (from 12:51 UTC). Brief: the batch-11 task "ingest4" (sources the
tracks asked for and the store does not hold; the six old-style reference lists that ingest3 left;
QA with the parse rate against the bar; answers to the requesting tracks). Predictions and outcomes:
`JOURNAL.md`. No card was used. Numbers carry their run id; outputs are under
`scratch/kb/<run_id>/`.

## What is here

| Path | What |
|---|---|
| `ids/requested12.txt` | the 12 ids of claims_tracks/README.md that the store lacked (2605.22525 of the 13 was already in) |
| `ids/additions18.txt` | the 18 additions: the 12, three for A, three for C |
| `ids/oldstyle6.txt` | the six papers with an old-style reference list |
| `ids/queries_round{1,2,3}.tsv` | the INSPIRE queries (tag, query) |
| `scripts/inspire_queries.py` | runs each query through `harness/bin/nrpic-fetch-arxiv --inspire-query` (one process, the tool's lock and gap) and tabulates the hits |
| `scripts/meta_table.py` | titles, authors, versions and TeX file counts of a list from the stored records |
| `scripts/count_markers.py` | independent count of the entries of the six old-style lists (written before the parser ran) |
| `scripts/figstyle.py` | byte copy of harness/style/figstyle.py |

Code (committed in kb/, with tests in the suite):

| File | Change |
|---|---|
| `kb/kbtool/bib_parse.py` | `heading_reference_list`: an old-style list with no environment, under the last line of the body whose words are a "References" heading, ending at `\end{document}`, `\bye`, a plain `\end`, `\endref`, a figure or table environment, or a caption/appendix heading; entries from `\item` (keys 1, 2, ...), lines that start with `[n]` (key n), or paragraphs started by one macro used at least 3 times at line starts (defined in the paper with a hanging indent or `\par`, or a known journal macro such as A&A's `\ref`; a one-argument macro takes its argument as key, a number macro `\def\Guth{1}` gives 1; no argument gives `#n`). `numeric_citations`: `[n]`, `[n,m]`, `[n--m]` outside math and not an optional argument, and one-argument macros that only wrap `#1` in brackets or a superscript (`\def\r#1{[#1]}`); every number must be a key of the list. Used only when no other source gives an entry (source `heading`). |
| `kb/kbtool/papers_ingest.py` | the bibliography is computed before chunking; an old-style list is masked from the body chunks; its numeric citations join the `\cite` ones (context sentences, chunk ids); `parse_json.bib_heading_list` |
| `kb/tests/test_bib_oldstyle.py` (new) | 9 tests on synthetic snippets: item list, plain-TeX `\i\Key` list with `\r{...}` citations, A&A `\ref` list, `[n]` lines with `\next`, LaTeX `\ref{label}` lines are no entries, a heading without entries, thebibliography wins, heading text, end to end (citation rows with chunk ids, the list not in body chunks) |
| `kb/manifests/arxiv_additions.tsv` | 18 rows (group, priority 2, requester, decision 0016-6, note) |
| `kb/tests/test_meta_papers.py` | the additions count: 78 rows, 762 papers |

## How to rerun

Every command ran under `harness/bin/nrpic-run submit --package tracks/kb/ingest4` (manifests in
tracks/kb/runs/<run_id>/; the exact command lines are there).

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I tracks/kb/ingest4/scripts/inspire_queries.py --queries tracks/kb/ingest4/ids/queries_round1.tsv --out <dir>
python3 -I harness/bin/nrpic-fetch-arxiv --ids-from tracks/kb/ingest4/ids/additions18.txt
python3 -I harness/bin/nrpic-fetch-arxiv --meta --service both --ids-from tracks/kb/ingest4/ids/additions18.txt
python3 -I tracks/kb/ingest4/scripts/meta_table.py --ids tracks/kb/ingest4/ids/additions18.txt --out <dir>
python3 -I tracks/kb/ingest4/scripts/count_markers.py --out <dir>
(cd kb && .venv/bin/python -m pytest -q tests/test_bib_oldstyle.py)          # or the whole suite
kb/.venv/bin/python -I kb/bin/kb ingest arxiv --all --jobs 4 --dry-run --out <dir>   # writes nothing
ids=$(cat tracks/kb/ingest4/ids/additions18.txt tracks/kb/ingest4/ids/oldstyle6.txt | sed 's/^/--id /')
kb/.venv/bin/python -I kb/bin/kb ingest arxiv $ids --jobs 4 --remap-claims --out <dir>
kb/.venv/bin/python -I kb/bin/kb eq --apply-tags && kb/.venv/bin/python -I kb/bin/kb embed --threads 4
kb/.venv/bin/python -I kb/bin/kb embed --check --work
kb/.venv/bin/python -I kb/bin/kb qa run --hybrid --db /data/haiyangw/nrpic/kb-data/db/kb.sqlite --out <dir>/QA_REPORT.md --json <dir>/qa.json
python3 tracks/kb/ingest4/scripts/fig_ingest4.py --before <run>/before --after <run>/after --counts <run>/marker_counts.tsv --out <dir>
```

## Results

| Step | Run | Result |
|---|---|---|
| metadata of the 12 | kb-20261124-125553-f0a7a10 | INSPIRE ok for 12; arXiv API HTTP 503 after back-off (retried below) |
| INSPIRE queries | kb-20261124-130108-5d1c671, kb-20261124-130410-9673ce1, kb-20261124-132936-4784ebb | 27 queries; Krasinski-Bolejko 2012 = 1202.5970; conformal flatness stated in 1908.02697 and 1611.09781; relativistic conductivity in 1202.4551 and 1301.1190; DSMC methodology 1304.3941; pre-arXiv records: Berger-Eardley-Olson 1977, Einstein-Straus 1945/46, Bertschinger 1985, Alexander-Garcia-Alder 1995; Croker-Weiner I = 2107.06643 (already in) |
| sources and metadata of 18 | kb-20261124-130450-5e22375 | 18 of 18 sources (all TeX) and both records |
| titles | kb-20261124-131019-d622860 | `meta_table.tsv`; each title fits its request (P1) |
| independent count | kb-20261124-130510-20ce0df | entries 11, 16, 16, 10, 27, 21 of the six lists |
| kb suite | kb-20261124-132834-12dc42b | exit 0 (one expected xfail), on commit 33bbd4e2 |
| dry run of all papers | kb-20261124-132848-81e6285 | only the six change among TeX papers (plus the three PDF-only papers, an artefact of the comparison); the 18 parse ok |
| ingest | kb-20261124-135341-e65f142 | 762 papers: ok 737, review 22, pdf 3; recorded rate 96.72 % (was 96.64 % of 744), above the 95 % bar; six lists: 101 entries, citation rows 13, 20, 0, 13, 41, 0, all with an entry; vectors check 0/0/0; claim 778 remapped (rows checked by hand: `kb claim check` checked nothing) |
| figures | kb-20261124-141642-9110c13 | `figures/fig_oldstyle.png`, `figures/fig_parse_status.png` (looked at), `figures/fig_data.tsv` |
| QA report | kb-20261124-141551-a75bc11 | STARTED, NOT READ: the PAUSE flag appeared at 14:17 UTC while it ran; close it with `harness/bin/nrpic-run finish kb-20261124-141551-a75bc11` and read `QA_REPORT.md` there (P8 open) |

Answers posted (tracks/kb/outbox/, commit 2f386306): A (szekeres-sources-ingested), C
(conductivity-dsmc-sources-ingested), D (claims-409-413-416-sources), F (claims-447-452-sources),
orch (additions-ingest4).

Not done: the six old-style papers stay `review` (no title, abstract or numbered sections are found
in their plain-TeX front matter; the bibliography does not enter the quality score). Author-year
citations (astro-ph/9510056, gr-qc/9906015) give no citation rows. The claims the new papers serve
(409, 447, 449, 450, 452) were not processed (a claims package's work). No snapshot (the lead's).

## Requests

- kb lead: finish run kb-20261124-141551-a75bc11 and read its QA report (parse rate against the bar,
  golden questions; prediction P8 in JOURNAL.md); take the snapshot so readers of db/current see the
  18 papers and the six lists; a claims package for 409, 447, 449, 450, 452 (abstract locators in the
  D and F messages); record as claims the locators A and C say they cite.
- kb lead: `kb claim check --id 778` checks nothing for a brief seed whose rows were set by relocate
  (empty "checked:" list); a check that reaches such rows would have caught a bad remap.
- kb lead (optional): plain-TeX front matter (`\centerline{\bf ...}` titles, `{\bf I. ...}` headings,
  `\eqno`) would lift the six from review to ok.
- orch: information message on the 18 additions (outbox 20261124T141719Z__to-orch__additions-ingest4.md);
  a reply only if a group should change.
