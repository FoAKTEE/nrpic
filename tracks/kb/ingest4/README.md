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

(filled in at the end)

## Results

(filled in at the end)

## Requests

(filled in at the end)
