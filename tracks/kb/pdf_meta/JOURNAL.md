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

## 2026-11-19 14:33 UTC: prediction P6 (vectors and citation edges of the three PDF papers)

P6 [prediction]. The PDF ingest (run kb-20261119-142651-7318d01) gave gr-qc/9412071 16 chunks,
astro-ph/9407016 45, 2201.03458 13, none with a vector; 14 chunk vectors are orphaned (the old
chunks of 2201.03458, deleted by the re-ingest). `kb embed --only chunks --threads 8` embeds the
74 new chunks (minus any of a kind it does not embed) and deletes exactly 14 orphans; `kb embed
--check --work` then reports no missing and no orphaned chunk vector. `kb resolve-bib` sets
in_corpus for the new citation rows; the edges of gr-qc/9412071 into the corpus are few (its 19
references are from 1977-1995 and carry no arXiv id). Refuted by: a count of new vectors other
than 74 that the embed kinds do not explain, orphans left, a check that fails.

## 2026-11-19 14:36 UTC: outcomes P1-P6 so far; prediction P7

P2 outcome (run kb-20261119-142559-387c3bc): HELD. 2107.06643 and 2201.09277 have ok records from
both services; the four INSPIRE not-found ids stay not-found when queried one at a time
(hits_total 0 for each), so INSPIRE holds no record carrying those eprints.

P1 outcome (run kb-20261119-142651-7318d01, figure fig_pdf_reader.png, inspected):
- `--all` selected exactly the three papers (2201.03458: e-print is a PDF; astro-ph/9407016 and
  gr-qc/9412071: no TeX). All three now have parse_status 'pdf'. gr-qc/9412071 is in the base:
  4 pages, 6 sections (run-in headings), 16 chunks, 1 figure caption, 19 references, 32
  citation keys.
- Pages 4, 28, 12: HELD. Abstract located with similarity 0.994, 1.000, 0.948 after repair: HELD.
  Before repair the located abstract already had 0.939 and 0.975 on the two old PDFs: the
  prediction "below 0.8 before repair" FAILED (the ligature damage touches few abstract words).
- Headings: gr-qc/9412071 the 5 named run-in headings plus Acknowledgements: HELD;
  astro-ph/9407016 I-VI with A-D and the two unnumbered ones (12): HELD; 2201.03458 is a JOSS
  paper without numbers, found by the standalone rule (Summary is taken by the abstract
  locator; Key features, Statement of Need, Key research projects, Acknowledgements, References):
  numbered headings FAILED as worded (it has none), the paper is structured.
- References: 19 numbered entries in gr-qc/9412071 (>= 15): HELD.
- Rare-token fraction: astro-ph/9407016 4.72 % -> 1.70 % (factor 2.8): HELD; gr-qc/9412071
  6.50 % -> 4.33 % (factor 1.5): FAILED. What remains rare in gr-qc/9412071 is index notation
  of the equations (Dkij, Bki, ...), names and acronyms, not ligature damage (list read in
  scratch/kb/tmp/pdf_meta, development pass). 2201.03458: no repair, 8.73 % before and after:
  HELD.
- Repair precision (run kb-20261119-143005-10376d4, 30 of 217 word repairs drawn with seed
  20261119, read by me in scratch/kb/kb-20261119-143005-10376d4/repair_sample.tsv): 30 of 30
  right: HELD. Seen in passing: a proper name with an ffi ligature (a cited author) became a
  Greek letter (the name is not in the vocabulary, so the control character fell to the cmmi
  table); counted as a known limitation, not in the sample.

P4 outcome (runs kb-20261119-142703-aaf0c4a, first pass, and kb-20261119-142905-e1d81d9 after
fixing the comparator; figure fig_brief16.png, inspected):
- Sections 16 and 17: the same 684 ids, the same group and the same priority (mark) for every
  id: HELD.
- First pass: TeX-only differences ($\mathbb U(1)$, \texttt{...}) counted as wording and
  collaboration entries as mismatches; two authors of one surname counted as an order change;
  junk author entries (";") of the arXiv API counted as extra authors. Fixed in e1d81d96, tests
  added.
- Second pass, titles: same 548, format 111 (659 = 96.3 % agree): HELD (>= 95 %); minor 17,
  differs 8 (25 <= 30): HELD.
- Authors: of 633 entries with an author field, 622 match and 5 name a collaboration (99.2 %):
  HELD; 5 order, 1 mismatch. The concentration in G20/G21 FAILED: the six are in G03, G07, G10,
  G15, G19, G21.

P3 outcome (run kb-20261119-142912-0f00e87, figure fig_metadata.png, inspected):
- 710/710 rows have the arXiv-API title, authors, abstract, primary class, submission and update
  dates (title_source arxiv-api); 706/710 an INSPIRE record number; DOI 651, journal reference
  648: HELD.
- Stored version = latest arXiv version for 710/710: HELD.
- Licence: 0/710. The stored arXiv-API answers carry no licence element (checked on
  meta/arxiv-api/2611.12831.xml: no "license" in the entry), so papers.license stays empty.
  Not predicted; a limit of the API, not of the loader.
- TeX title vs API title >= 0.9: 660 of 707 TeX papers = 93.4 %: FAILED (predicted >= 95 %).
  34 TeX papers have no extracted title at all; of the 673 with one, 660 agree (98.1 %). Of the
  13 that differ, 9 are extraction defects of the TeX title (preprint numbers, \thanks text,
  dropped macros such as the code name of 2409.16053), 4 are real differences between the
  source and the arXiv listing (shorter or other title in the source).
- TeX abstract vs API abstract >= 0.8: 664 of 682 TeX papers with an abstract chunk = 97.4 %:
  HELD.

P5 outcome (same run): 26 additions loaded, every row of papers has a group (grp NULL: 0 of
710), groups G04 1, G06 6, G14 1, G18 11, G21 7: HELD, with the one exception named before the
run (gr-qc/0608095, placeholder G06, proposed for removal).

P6 outcome (run kb-20261119-143251-eb99c45; first call kb-20261119-143242-737909d failed at
once on an option `kb embed` does not have, nothing written): 74 chunks embedded, 14 orphans
deleted, `kb embed --check --work`: chunk 43560 owners = 43560 vectors, 0 missing, 0 stale, 0
orphaned; equations unchanged (54502): HELD. 15 of the 74 chunks were truncated to the model's
length. `kb resolve-bib`: gr-qc/9412071 has 0 of 32 outgoing citations in the corpus (no arXiv
ids, as predicted) and is now the target of 36 citation rows of corpus papers.

P7 [prediction]. Hybrid search on kb.sqlite with one query per PDF paper in my own words
("first-order flux-conservative hyperbolic formulation of the Einstein equations for a family of
slicings", "equilibrium state of a self-interacting scalar field in de Sitter, stochastic
approach, Fokker-Planck", "GRChombo adaptable numerical relativity code with adaptive mesh
refinement") ranks the paper within the top 10. Refuted by any of the three outside the top 10.
