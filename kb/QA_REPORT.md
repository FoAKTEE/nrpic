# Quality report of the knowledge base (brief 12.9)

Written by `kb qa run` (kbtool/qa_report.py) at 2026-11-19T16:16:34Z from `/data/haiyangw/nrpic/kb-data/db/kb-20261119-a782f1e.sqlite` (db/current: `kb-20261119-a782f1e.sqlite`). Ids, counts and our own wording only; no paper text.

## C1. Counts against the manifests

- Manifest: 710 arXiv ids (brief section 17: 684; additions of decision 0016 item 6: 26); downloads by status: ok 709, problem 1.
- Ingested: 710 of 710 manifest ids; 0 extras; 710 papers in all. Not ingested: none.
- Priority 3: 47 of 47 ingested, 45 with status ok.
- Priority 2: 185 of 185 ingested, 177 with status ok.
- Priority 1: 478 of 478 ingested, 462 with status ok.
- Missing or failed downloads: none.
- Verdict: counts agree.

## C2. Abstract and at least one section for every paper

- 675 of 710 papers have both. Without an abstract (0): none.
- No abstract extracted from the source (no abstract chunk; the metadata abstract may still be there) (25): 1810.03490, 1911.04505, 1911.09689, 2004.10754, 2009.08715, 2012.09255, 2109.01398, 2211.13659, 2403.15126, 2406.02417, 2501.13046, 2506.21423, 2509.01320, 2510.13129, 2602.00155, 2610.32592, astro-ph/0003278, astro-ph/0306304, astro-ph/9306009, astro-ph/9510056, gr-qc/0012059, gr-qc/0201056, gr-qc/0703035, gr-qc/9604001, gr-qc/9906015.
- Without any section (35): 0710.0879, 0710.5073, 1005.4054, 1207.1286, 1304.7791, 1306.1562, 1408.2741, 1505.04756, 1511.01105, 1511.05124, 1810.03613, 1907.08129, 2006.01172, 2104.12293, 2105.11880, 2210.11426, 2211.15674, 2302.00655, 2311.17644, 2312.03860, 2504.15978, astro-ph/0003278, astro-ph/0306304, astro-ph/9306009, astro-ph/9510056, astro-ph/9709072, gr-qc/0312117, gr-qc/0511048, gr-qc/0511103, gr-qc/0608095, gr-qc/9402041, gr-qc/9604001, gr-qc/9703066, gr-qc/9906015, hep-ph/9809574.
  - of these, no sectioning command at all in flat.tex (letters, plain TeX): 34; a sectioning command present but no section extracted: 1 (astro-ph/0003278); no flat.tex: none.

## C3. Parse failures and the review list, by cause

- 26 papers not ok: pdf 3, review 23.
- Causes (several per paper possible; from the quality components stored in papers.parse_json):
  - no abstract environment: 21
  - no \title: 20
  - no sections: 7
  - many unresolved macros: 5
  - thesis or long document: 4
  - no \documentclass (plain TeX or fragment): 4
  - PDF only (text extraction, no equations): 3
  - unresolved \input: 2

| paper | status | score | causes |
|---|---|---|---|
| 2201.03458 | pdf | 1.0 | PDF only (text extraction, no equations) |
| astro-ph/9407016 | pdf | 1.0 | PDF only (text extraction, no equations) |
| gr-qc/9412071 | pdf | 1.0 | PDF only (text extraction, no equations) |
| 0710.0879 | review | 0.7293 | no sections; many unresolved macros |
| 1810.03490 | review | 0.698 | no \title; no abstract environment |
| 1911.04505 | review | 0.6937 | no \title; no abstract environment |
| 1911.09689 | review | 0.699 | no \title; no abstract environment |
| 2004.10754 | review | 0.6997 | no \title; no abstract environment |
| 2009.08715 | review | 0.7 | no \title; no abstract environment; thesis or long document |
| 2012.09255 | review | 0.6994 | no \title; no abstract environment |
| 2403.15126 | review | 0.6993 | no \title; no abstract environment |
| 2406.02417 | review | 0.6973 | no \title; no abstract environment |
| 2506.21423 | review | 0.6988 | no \title; no abstract environment |
| 2509.01320 | review | 0.6955 | no \title; no abstract environment |
| 2510.13129 | review | 0.6961 | no \title; no abstract environment |
| 2602.00155 | review | 0.6482 | no abstract environment; many unresolved macros |
| 2610.32592 | review | 0.695 | no \title; no abstract environment; thesis or long document |
| astro-ph/0003278 | review | 0.5634 | no abstract environment; no sections; unresolved \input |
| astro-ph/0306304 | review | 0.5492 | no \title; no abstract environment; no sections |
| astro-ph/9306009 | review | 0.5281 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |
| astro-ph/9510056 | review | 0.4 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |
| astro-ph/9607124 | review | 0.729 | no \title |
| gr-qc/0012059 | review | 0.6465 | no \title; no abstract environment; thesis or long document; unresolved \input |
| gr-qc/0703035 | review | 0.699 | no \title; no abstract environment; thesis or long document |
| gr-qc/9604001 | review | 0.5355 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment) |
| gr-qc/9906015 | review | 0.5147 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |

## C4. Thirty papers at random against INSPIRE

- Sample (random.Random(20261115), from the ingested papers): 1004.1353, 1111.2997, 1305.4634, 1403.4947, 1511.05124, 1607.00381, 1609.04724, 1610.05635, 1703.08585, 1703.10543, 1707.06079, 1707.08666, 1904.11773, 2007.04968, 2102.03774, 2103.01183, 2106.09235, 2109.13364, 2110.05982, 2307.12080, 2310.16482, 2401.02409, 2404.03002, 2409.01937, 2409.10383, 2504.17680, 2605.30145, 2611.12831, gr-qc/0312117, gr-qc/9905058.
- 30 of 30 have metadata on disk (kb-data/meta/inspire/<key>.json, else meta/arxiv-api/<key>.json; written by nrpic-fetch-arxiv --meta); by source: inspire 30.
- Compared: the title and authors the TeX parser stored in `papers` against the metadata record (title similarity of normalised strings; fraction of metadata surnames found in the TeX author list). Below 0.9 or 80.0 %: 2103.01183, gr-qc/9905058.

| paper | source | title ratio | authors found |
|---|---|---|---|
| 1004.1353 | inspire | 1.000 | 100.0 % |
| 1111.2997 | inspire | 1.000 | 100.0 % |
| 1305.4634 | inspire | 1.000 | 100.0 % |
| 1403.4947 | inspire | 1.000 | 100.0 % |
| 1511.05124 | inspire | 1.000 | 100.0 % |
| 1607.00381 | inspire | 1.000 | 100.0 % |
| 1609.04724 | inspire | 1.000 | 100.0 % |
| 1610.05635 | inspire | 1.000 | 100.0 % |
| 1703.08585 | inspire | 1.000 | 100.0 % |
| 1703.10543 | inspire | 1.000 | 100.0 % |
| 1707.06079 | inspire | 1.000 | 100.0 % |
| 1707.08666 | inspire | 0.981 | 100.0 % |
| 1904.11773 | inspire | 1.000 | 100.0 % |
| 2007.04968 | inspire | 1.000 | 100.0 % |
| 2102.03774 | inspire | 1.000 | 100.0 % |
| 2103.01183 | inspire | 0.713 | 100.0 % |
| 2106.09235 | inspire | 1.000 | 100.0 % |
| 2109.13364 | inspire | 1.000 | 100.0 % |
| 2110.05982 | inspire | 1.000 | 100.0 % |
| 2307.12080 | inspire | 1.000 | 100.0 % |
| 2310.16482 | inspire | 1.000 | 100.0 % |
| 2401.02409 | inspire | 1.000 | 100.0 % |
| 2404.03002 | inspire | 1.000 | 99.5 % |
| 2409.01937 | inspire | 1.000 | 100.0 % |
| 2409.10383 | inspire | 1.000 | 100.0 % |
| 2504.17680 | inspire | 1.000 | 100.0 % |
| 2605.30145 | inspire | 1.000 | 100.0 % |
| 2611.12831 | inspire | 1.000 | 100.0 % |
| gr-qc/0312117 | inspire | 0.989 | 100.0 % |
| gr-qc/9905058 | inspire | 0.000 | 0.0 % |

## C5. Bibliography resolution and the citation graph

- 64968 bibliography entries; with an arXiv id 39543 (60.9 %), with a DOI 20122, with any identifier 46993 (72.3 %).
- By source: bbl 47351 entries, 36639 with an id; bib 4555 entries, 4188 with an id; pdf-text 111 entries, 5 with an id; thebibliography 12951 entries, 6161 with an id.
- By resolution step: arxiv-id 38523, doi 7450, doi-corpus 913, none 17975, title-fuzzy-corpus 107.
- Distinct citation edges (citing paper, cited arXiv id): 39152, inside the corpus 6419 (16.4 %); the definition of the K3 report.
- Citation rows (one per `\cite` occurrence): 104995; in the corpus 14208 (13.5 %); of the 76098 rows with an identifier, 18.7 % in the corpus.

## C6. Duplicates

- Papers stored in more than one version: 0 (the database holds one version per id).
- Different ids with identical flattened text: none; identical source bytes: none.
- Different ids with the same normalised title: none; same abstract start: none.

## C7. Retrieval regression (golden questions)

- 32 questions (kbtool/qa_golden.py; own wording, answers from KB-G1 and checked claims); hit within the top 10 chunks. Vectors stored for 43560 of 43560 chunks.
- Mode rerank: `kbtool/search_rerank.py`, variant w2-noexpand: the first 100 chunks of the hybrid list, cut into windows of 2 sentences (stride 1), ordered by reciprocal-rank fusion of window BM25 and window vectors.
- KB-G2 (decision 0016, item 6): at least 80 % of the golden questions with the right paper in the top ten (gating); the hit at the answer location is reported, not gating.
- **text**: paper hit rate 27/32 (84.4 %), locator hit rate 21/32 (65.6 %), mean reciprocal rank of the paper 0.712.
- **hybrid**: paper hit rate 28/32 (87.5 %), locator hit rate 23/32 (71.9 %), mean reciprocal rank of the paper 0.657.
- **rerank**: paper hit rate 28/32 (87.5 %), locator hit rate 25/32 (78.1 %), mean reciprocal rank of the paper 0.721.

| question | paper | text paper rank | text locator rank | hybrid paper rank | hybrid locator rank | rerank paper rank | rerank locator rank |
|---|---|---|---|---|---|---|---|
| q01 | 2111.05282 | 1 | - | 1 | 6 | 2 | 9 |
| q02 | 2611.12831 | 1 | 1 | 2 | 2 | 1 | 1 |
| q03 | 2611.12831 | 1 | 1 | 1 | 1 | 1 | 1 |
| q04 | 2611.12831 | 1 | 6 | 1 | 2 | 1 | 1 |
| q05 | 2611.12831 | 2 | 2 | 4 | 4 | 1 | 1 |
| q06 | 2611.12831 | 2 | - | 6 | - | - | - |
| q07 | 2611.12831 | - | - | 5 | - | 2 | - |
| q08 | 2611.12831 | 1 | 2 | 1 | 1 | 2 | 5 |
| q09 | 2611.12831 | 1 | 2 | 1 | 1 | 1 | 2 |
| q10 | 2611.12831 | 1 | 1 | 6 | 6 | 3 | 3 |
| q11 | 2609.14218 | - | - | - | - | 2 | 2 |
| q12 | 2609.14218 | - | - | - | - | - | - |
| q13 | 2512.14649 | 7 | - | - | - | - | - |
| q14 | 2404.16270 | 1 | 4 | 1 | 1 | 1 | 1 |
| q15 | 2610.23218 | 1 | 1 | 1 | 1 | 1 | 1 |
| q16 | 1609.01588 | 1 | - | 1 | - | 1 | - |
| q17 | 2507.18312 | - | - | 4 | - | - | - |
| q18 | 1901.04498 | 2 | 2 | 1 | 1 | 1 | 1 |
| q19 | 2403.15126 | 1 | 1 | 2 | 2 | 4 | 4 |
| q20 | 2605.04487 | 2 | - | 1 | - | 2 | - |
| q21 | 2605.04487 | 1 | 1 | 1 | 1 | 1 | 1 |
| q22 | 1604.06065 | 7 | 7 | 2 | 2 | 1 | 1 |
| q23 | 2501.13046 | 1 | 1 | 1 | 1 | 2 | 3 |
| q24 | astro-ph/0110561 | - | - | - | - | 1 | 2 |
| q25 | 1305.2619 | 1 | - | 2 | 6 | 1 | 1 |
| q26 | 1707.06302 | 1 | 1 | 1 | 1 | 1 | 1 |
| q27 | 2109.04896 | 1 | 1 | 2 | 2 | 1 | 1 |
| q28 | 2302.07878 | 1 | 1 | 1 | 1 | 1 | 1 |
| q29 | 2305.01307 | 1 | 1 | 1 | 1 | 2 | 2 |
| q30 | 2505.03934 | 1 | 1 | 1 | 1 | 1 | 1 |
| q31 | 2108.01392 | 2 | 3 | 2 | 7 | 1 | 1 |
| q32 | 2610.09336 | 1 | 1 | 1 | 3 | 1 | 1 |

## C8. Independent equation count on a sample

- 41 papers (2611.12831 and 40 drawn with random.Random(20261116)): numbered display lines counted by `kbtool/qa_eqcount.py` (a stack scanner written apart from the extractor) against the equation rows with a number in the database.
- Agree exactly: 41 of 41; within 2 % or 2 lines: 41. Totals: independent 3154, database 3154.

| paper | input | independent | database | difference |
|---|---|---|---|---|
| 2611.12831 | raw main file | 139 | 139 | +0 |
| 0710.5073 | raw main file | 24 | 24 | +0 |
| 0711.1165 | raw main file | 26 | 26 | +0 |
| 0901.0989 | raw main file | 79 | 79 | +0 |
| 1105.5280 | raw main file | 71 | 71 | +0 |
| 1503.08747 | raw main file | 162 | 162 | +0 |
| 1706.09896 | raw main file | 10 | 10 | +0 |
| 1707.06302 | flat.tex | 46 | 46 | +0 |
| 1801.02378 | flat.tex | 52 | 52 | +0 |
| 1802.10085 | raw main file | 13 | 13 | +0 |
| 1804.08577 | raw main file | 80 | 80 | +0 |
| 1805.09034 | raw main file | 33 | 33 | +0 |
| 1809.07010 | raw main file | 220 | 220 | +0 |
| 1810.05203 | raw main file | 52 | 52 | +0 |
| 1905.07345 | flat.tex | 73 | 73 | +0 |
| 1908.06919 | raw main file | 39 | 39 | +0 |
| 2011.03547 | raw main file | 67 | 67 | +0 |
| 2102.05690 | raw main file | 101 | 101 | +0 |
| 2107.12735 | raw main file | 169 | 169 | +0 |
| 2109.09768 | raw main file | 162 | 162 | +0 |
| 2207.06376 | raw main file | 24 | 24 | +0 |
| 2208.05018 | raw main file | 25 | 25 | +0 |
| 2303.06630 | raw main file | 14 | 14 | +0 |
| 2304.01673 | raw main file | 34 | 34 | +0 |
| 2309.00431 | raw main file | 329 | 329 | +0 |
| 2311.08780 | raw main file | 19 | 19 | +0 |
| 2406.02417 | raw main file | 55 | 55 | +0 |
| 2406.05838 | raw main file | 47 | 47 | +0 |
| 2407.08775 | raw main file | 67 | 67 | +0 |
| 2410.13683 | flat.tex | 54 | 54 | +0 |
| 2507.04114 | raw main file | 63 | 63 | +0 |
| 2507.18312 | raw main file | 144 | 144 | +0 |
| 2508.10070 | raw main file | 90 | 90 | +0 |
| 2510.11611 | raw main file | 61 | 61 | +0 |
| 2510.13129 | flat.tex | 149 | 149 | +0 |
| 2511.20567 | raw main file | 38 | 38 | +0 |
| 2611.15050 | flat.tex | 140 | 140 | +0 |
| astro-ph/0309084 | raw main file | 39 | 39 | +0 |
| astro-ph/0608642 | raw main file | 56 | 56 | +0 |
| astro-ph/9510056 | flat.tex | 0 | 0 | +0 |
| hep-th/0703290 | raw main file | 88 | 88 | +0 |

## C9. The claims layer (K8)

- 700 claims on 80 papers; labels: background 1, fulltext 541, judgement 41, to_verify 117; statuses: checked 39, located 583, partial 34, unlocated 43, unresolved 1.
- Locators 777, resolved 776; claims with a chunk 627; labels set by a person 43.
- By track (status counts): A-emd-pbh: checked 8, located 155, partial 4, unlocated 3; B-emd-gw: checked 13, located 46, partial 5, unlocated 8; C-sidm: checked 2, located 104, partial 6, unresolved 1; D-bh-dress: checked 7, located 77, partial 2, unlocated 14; E-stoch-inf: located 6, partial 1; F-hills: checked 4, located 69, partial 8, unlocated 7; core: checked 5, located 126, partial 8, unlocated 11.

## C10. References of the verification suite (CHARTER section 10)

- 27 arXiv ids in the section; ingested 27; missing: none.

Run time 551.7 s.
