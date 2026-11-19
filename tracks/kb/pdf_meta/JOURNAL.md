# JOURNAL of the kb helper package pdf_meta (wave 2b)

Package: (1) a reader for `source.pdf` entries and the ingestion of gr-qc/9412071 from its
stored PDF; (2) the metadata of every manifest entry (arXiv API, INSPIRE) read into the papers
table and titles and authors compared with brief section 16 (lines 1763-2529), the
differences as a table for `coord/BRIEF_ERRATA.md`; (3) the 26 extra papers entered into the
manifest with a group each (decision 0016 item 6).

## 2026-11-19 14:10 UTC: state found, before any test

- Worktree clean after `git merge --no-edit main` (fast-forward to 71acd0c3). No earlier
  `tracks/kb/pdf_meta/` exists: nothing stranded from wave 2 for this package.
- Store (read only, before this package): `kb-data/meta/arxiv-api/` holds 708 parsed records
  with status ok, `kb-data/meta/inspire/` 704 ok and 4 `not-found` (1609.03053, 1612.06734,
  1709.00267, 2409.16053), from run kb-20261115-182505-7e3a0b5. Missing in both: 2107.06643
  and 2201.09277 (fetched after that run). Total ids in the store and the papers table: 710
  (684 manifest + 26 extras); the papers table has 709 rows (gr-qc/9412071 absent).
- `kb.sqlite` papers: parse_status ok 684, review 23, pdf 1 (2201.03458, an e-print that is a
  PDF, title empty, score 0.2), failed 1 (astro-ph/9407016: a tar of PostScript files, "no TeX
  file in the source"). Columns primary_class, submitted, updated, doi, inspire_recid,
  journal_ref, license, brief_title, brief_authors, title_matches_brief are empty for all.
- gr-qc/9412071 v2: `source.bin` is gzipped PostScript; `kb verify-downloads` calls it a
  problem ("not an e-print: content is gzip-other") so `kb ingest` skips it. `source.pdf`
  (134365 bytes, record `meta/arxiv-pdf/gr-qc_9412071.json`, status ok) is stored beside it.
  astro-ph/9407016 v1 also has a stored `source.pdf` (243425 bytes).
- First look at `pdftotext` output of the three PDFs (scratch only): the two dvips/Ghostscript
  PDFs of 1994-95 lose the fi/fl/ff ligatures ("rst", "uid", "signi cant", "in ationary") and
  print the OT1 en-dash as "{" ("[5{7]"); 2201.03458 (xdvipdfmx, 2022) does not.
- Brief section 16 parses by script into 684 entries (one pattern; 51 entries have no author
  field, 81 "et al.", 22 "(first author)", 7 "(authors include ...)", 523 plain lists);
  marks 47/160/477 = priorities 3/2/1 of the section-17 manifest.

## Predictions (written before the runs)

P1 PDF reader [prediction]. On the three PDF papers of the store (gr-qc/9412071, astro-ph/9407016,
2201.03458) the reader gives: pdftotext text of 4, 28 and 12 pages; the abstract located on
page 1 with word-sequence similarity to the arXiv-API abstract >= 0.8 after repair (below that
on the 1994-95 PDFs before repair); sections: 4 or more run-in headings for the PRL
gr-qc/9412071 (Introduction, Evolution equations, Characteristic Fields, A new class of gauge
conditions, Conclusion), the Roman-numbered headings I-VI for astro-ph/9407016, numbered
headings for 2201.03458; reference lists with at least 15 numbered entries for gr-qc/9412071.
Ligature repair: the out-of-vocabulary fraction of alphabetic tokens (length >= 3, against the
vocabulary of the TeX-ingested corpus) falls by at least a factor 2 on the two old PDFs and
changes by less than 0.1 percentage point on 2201.03458; of 30 repairs drawn at random and
read by me, at least 27 are right. Refuted by: a page count that differs, an abstract
similarity below 0.8 after repair, fewer headings than stated, a repair precision below 27/30.

P2 metadata fetch [prediction]. `nrpic-fetch-arxiv --meta` for 2107.06643 and 2201.09277 gives
ok records from both services (both have DOIs and are journal articles). Retrying INSPIRE one id
at a time for the four not-found ids: 2409.16053 (AthenaK, astro-ph.IM) stays not-found
[JUDGEMENT: INSPIRE covers HEP and gr-qc, not all of astro-ph.IM]; I make no prediction for the
other three. Refuted by: either of the two new ids failing.

P3 metadata into papers [prediction]. All 710 papers get primary_class, submitted, updated
from the arXiv API (710/710), inspire_recid for every id with an INSPIRE record (>= 706/710),
title_source arxiv-api. The version stored (directory) equals the latest version in the
arXiv-API record for all but at most 5 papers (the store is four days old; a new version in
that time is rare). The TeX-extracted title agrees with the API title (normalised similarity
>= 0.9) for >= 95 % of the TeX papers; the TeX abstract chunk agrees with the API abstract
(similarity >= 0.8) for >= 90 % of the TeX papers that have one. Refuted by any count below.

P4 brief section 16 [prediction]. The 684 section-16 entries are the 684 ids of the section-17
manifest with the same group for every id (the two lists were produced together). Titles: at
least 95 % agree with the arXiv-API title after normalisation (case, punctuation, TeX); at
most 30 entries differ in wording. Authors: every surname the brief lists is among the arXiv
authors for at least 95 % of the 633 entries that list authors; mismatches concentrate in the
"(first author)" and "et al." entries of G21 and G20 (written later, version 2). Refuted by: a
group that differs between sections 16 and 17, title agreement below 95 %, author agreement
below 95 %.

P5 extras [prediction]. The 26 papers outside the manifest are exactly the 26 rows of the papers
table with grp NULL; each gets a group of brief section 16 (G01-G21); after loading, no row of
the papers table has grp NULL. Already seen while listing them (so not a prediction):
gr-qc/0608095 is a laser-interferometry paper that no track asked for (fetched by another
session at 11:17 UTC on 2026-11-15, `kb/JOURNAL.md:92`) and fits no group. Refuted by: a count
other than 26, a second paper that fits no group.
