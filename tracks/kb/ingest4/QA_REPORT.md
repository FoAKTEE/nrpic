# Quality report of the knowledge base (brief 12.9)

Written by `kb qa run` (kbtool/qa_report.py) at 2026-11-24T17:25:38Z from `/data/haiyangw/nrpic/kb-data/db/kb.sqlite` (db/current: `kb-20261121-aa0a2ae.sqlite`). Ids, counts and our own wording only; no paper text.

## C1. Counts against the manifests

- Manifest: 762 arXiv ids (brief section 17: 684; additions of decision 0016 item 6: 78); downloads by status: ok 761, problem 1.
- Ingested: 762 of 762 manifest ids; 0 extras; 762 papers in all. Not ingested: none.
- Priority 3: 47 of 47 ingested, 45 with status ok.
- Priority 2: 205 of 205 ingested, 198 with status ok.
- Priority 1: 510 of 510 ingested, 494 with status ok.
- Missing or failed downloads: none.
- Parse success rate: 737 of 762 with status ok, 96.7 %; strict (an ok paper that cites but has no bibliography entry counts as failed): 737, 96.7 %. Bar 95.0 %: met.
- Verdict: counts agree.

## C2. Abstract and at least one section for every paper

- 727 of 762 papers have both. Without an abstract (0): none.
- No abstract extracted from the source (no abstract chunk; the metadata abstract may still be there) (25): 1810.03490, 1911.04505, 1911.09689, 2004.10754, 2009.08715, 2012.09255, 2109.01398, 2211.13659, 2403.15126, 2406.02417, 2501.13046, 2505.00286, 2506.21423, 2509.01320, 2510.13129, 2602.00155, 2610.32592, astro-ph/0306304, astro-ph/9306009, astro-ph/9510056, gr-qc/0012059, gr-qc/0201056, gr-qc/0703035, gr-qc/9604001, gr-qc/9906015.
- Without any section (35): 0710.0879, 0710.5073, 1005.4054, 1207.1286, 1304.7791, 1306.1562, 1408.2741, 1505.04756, 1511.01105, 1511.05124, 1611.09781, 1810.03613, 1907.08129, 2006.01172, 2104.12293, 2105.11880, 2210.11426, 2211.15674, 2302.00655, 2311.17644, 2312.03860, 2504.15978, 2610.01964, astro-ph/0306304, astro-ph/9306009, astro-ph/9510056, astro-ph/9709072, gr-qc/0312117, gr-qc/0511048, gr-qc/0511103, gr-qc/9402041, gr-qc/9604001, gr-qc/9703066, gr-qc/9906015, hep-ph/9809574.
  - of these, no sectioning command at all in flat.tex (letters, plain TeX): 35; a sectioning command present but no section extracted: 0 (none); no flat.tex: none.

## C3. Parse failures and the review list, by cause

- 25 papers not ok: pdf 3, review 22.
- Causes (several per paper possible; from the quality components stored in papers.parse_json):
  - no \title: 20
  - no abstract environment: 20
  - no sections: 6
  - many unresolved macros: 5
  - thesis or long document: 4
  - no \documentclass (plain TeX or fragment): 4
  - PDF only (text extraction, no equations): 3
  - unresolved \input: 1

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
| 2602.00155 | review | 0.6 | no abstract environment; many unresolved macros |
| 2610.32592 | review | 0.695 | no \title; no abstract environment; thesis or long document |
| astro-ph/0306304 | review | 0.5491 | no \title; no abstract environment; no sections |
| astro-ph/9306009 | review | 0.5292 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |
| astro-ph/9510056 | review | 0.4 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |
| astro-ph/9607124 | review | 0.7289 | no \title |
| gr-qc/0012059 | review | 0.6465 | no \title; no abstract environment; thesis or long document; unresolved \input |
| gr-qc/0703035 | review | 0.699 | no \title; no abstract environment; thesis or long document |
| gr-qc/9604001 | review | 0.5356 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment) |
| gr-qc/9906015 | review | 0.5139 | no \title; no abstract environment; no sections; no \documentclass (plain TeX or fragment); many unresolved macros |

## C4. Thirty papers at random against INSPIRE

- Sample (random.Random(20261115), from the ingested papers): 1004.1353, 1109.2484, 1303.1540, 1308.6524, 1602.03520, 1607.00612, 1608.04408, 1612.03753, 1704.03500, 1706.09501, 1811.00904, 2003.04327, 2011.12190, 2102.05690, 2303.07980, 2308.07374, 2312.12499, 2403.15126, 2404.01137, 2409.16053, 2511.17701, 2604.03628, 2609.14218, astro-ph/0003278, astro-ph/0702575, astro-ph/9709072, astro-ph/9901292, gr-qc/0305023, gr-qc/0511103, math/0209336.
- 30 of 30 have metadata on disk (kb-data/meta/inspire/<key>.json, else meta/arxiv-api/<key>.json; written by nrpic-fetch-arxiv --meta); by source: arxiv-api 1, inspire 29.
- Compared: the title and authors the TeX parser stored in `papers` against the metadata record (title similarity of normalised strings; fraction of metadata surnames found in the TeX author list). Below 0.9 or 80.0 %: 2011.12190, 2403.15126, 2409.16053.

| paper | source | title ratio | authors found |
|---|---|---|---|
| 1004.1353 | inspire | 1.000 | 100.0 % |
| 1109.2484 | inspire | 1.000 | 100.0 % |
| 1303.1540 | inspire | 1.000 | 100.0 % |
| 1308.6524 | inspire | 1.000 | 100.0 % |
| 1602.03520 | inspire | 1.000 | 100.0 % |
| 1607.00612 | inspire | 1.000 | 100.0 % |
| 1608.04408 | inspire | 1.000 | 100.0 % |
| 1612.03753 | inspire | 1.000 | 100.0 % |
| 1704.03500 | inspire | 1.000 | 100.0 % |
| 1706.09501 | inspire | 0.988 | 100.0 % |
| 1811.00904 | inspire | 1.000 | 100.0 % |
| 2003.04327 | inspire | 1.000 | 100.0 % |
| 2011.12190 | inspire | 0.458 | 100.0 % |
| 2102.05690 | inspire | 1.000 | 100.0 % |
| 2303.07980 | inspire | 1.000 | 100.0 % |
| 2308.07374 | inspire | 1.000 | 100.0 % |
| 2312.12499 | inspire | 1.000 | 100.0 % |
| 2403.15126 | inspire | 0.000 | 0.0 % |
| 2404.01137 | inspire | 1.000 | 100.0 % |
| 2409.16053 | arxiv-api | 0.872 | 100.0 % |
| 2511.17701 | inspire | 0.964 | 100.0 % |
| 2604.03628 | inspire | 1.000 | 100.0 % |
| 2609.14218 | inspire | 1.000 | 100.0 % |
| astro-ph/0003278 | inspire | 1.000 | 100.0 % |
| astro-ph/0702575 | inspire | 1.000 | 100.0 % |
| astro-ph/9709072 | inspire | 1.000 | 100.0 % |
| astro-ph/9901292 | inspire | 1.000 | 100.0 % |
| gr-qc/0305023 | inspire | 1.000 | 100.0 % |
| gr-qc/0511103 | inspire | 1.000 | 100.0 % |
| math/0209336 | inspire | 1.000 | 100.0 % |

## C5. Bibliography resolution and the citation graph

- 68970 bibliography entries; with an arXiv id 41279 (59.9 %), with a DOI 22084, with any identifier 49441 (71.7 %).
- By source: bbl 48618 entries, 37248 with an id; bib 6084 entries, 5600 with an id; heading 101 entries, 1 with an id; pdf-text 111 entries, 5 with an id; thebibliography 14056 entries, 6587 with an id.
- By resolution step: arxiv-id 40162, doi 8162, doi-corpus 959, none 19529, title-fuzzy-corpus 158.
- Distinct citation edges (citing paper, cited arXiv id): 41018, inside the corpus 6756 (16.5 %); the definition of the K3 report.
- Citation rows (one per `\cite` occurrence): 111311; in the corpus 14968 (13.4 %); of the 80610 rows with an identifier, 18.6 % in the corpus.

## C6. Duplicates

- Papers stored in more than one version: 0 (the database holds one version per id).
- Different ids with identical flattened text: none; identical source bytes: none.
- Different ids with the same normalised title: none; same abstract start: none.

## C7. Retrieval regression (golden questions)

- 32 questions (kbtool/qa_golden.py; own wording, answers from KB-G1 and checked claims); hit within the top 10 chunks. Vectors stored for 46746 of 46746 chunks.
- Mode rerank: `kbtool/search_rerank.py`, variant w2-noexpand: the first 100 chunks of the hybrid list, cut into windows of 2 sentences (stride 1), ordered by reciprocal-rank fusion of window BM25 and window vectors.
- KB-G2 (decision 0016, item 6): at least 80 % of the golden questions with the right paper in the top ten (gating); the hit at the answer location is reported, not gating.
- **text**: paper hit rate 27/32 (84.4 %), locator hit rate 21/32 (65.6 %), mean reciprocal rank of the paper 0.676.
- **hybrid**: paper hit rate 28/32 (87.5 %), locator hit rate 23/32 (71.9 %), mean reciprocal rank of the paper 0.637.
- **rerank**: paper hit rate 28/32 (87.5 %), locator hit rate 25/32 (78.1 %), mean reciprocal rank of the paper 0.720.

| question | paper | text paper rank | text locator rank | hybrid paper rank | hybrid locator rank | rerank paper rank | rerank locator rank |
|---|---|---|---|---|---|---|---|
| q01 | 2111.05282 | 1 | - | 1 | 6 | 2 | 9 |
| q02 | 2611.12831 | 1 | 1 | 2 | 2 | 1 | 1 |
| q03 | 2611.12831 | 1 | 1 | 1 | 1 | 1 | 1 |
| q04 | 2611.12831 | 1 | 6 | 1 | 2 | 1 | 1 |
| q05 | 2611.12831 | 2 | 2 | 4 | 4 | 1 | 1 |
| q06 | 2611.12831 | 2 | - | 5 | - | - | - |
| q07 | 2611.12831 | - | - | 5 | - | 2 | - |
| q08 | 2611.12831 | 1 | 2 | 1 | 1 | 2 | 4 |
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
| q19 | 2403.15126 | 2 | 2 | 2 | 2 | 5 | 5 |
| q20 | 2605.04487 | 2 | - | 1 | - | 2 | - |
| q21 | 2605.04487 | 1 | 1 | 1 | 1 | 1 | 1 |
| q22 | 1604.06065 | 7 | 7 | 2 | 2 | 1 | 1 |
| q23 | 2501.13046 | 1 | 1 | 1 | 1 | 2 | 3 |
| q24 | astro-ph/0110561 | - | - | - | - | 1 | 2 |
| q25 | 1305.2619 | 1 | - | 2 | 5 | 1 | 1 |
| q26 | 1707.06302 | 1 | 1 | 1 | 1 | 1 | 1 |
| q27 | 2109.04896 | 1 | 1 | 2 | 2 | 1 | 1 |
| q28 | 2302.07878 | 3 | 3 | 3 | 3 | 2 | 2 |
| q29 | 2305.01307 | 1 | 1 | 1 | 1 | 1 | 1 |
| q30 | 2505.03934 | 1 | 1 | 1 | 1 | 1 | 1 |
| q31 | 2108.01392 | 2 | 3 | 2 | 7 | 1 | 1 |
| q32 | 2610.09336 | 1 | 1 | 1 | 3 | 1 | 1 |

## C8. Independent equation count on a sample

- 41 papers (2611.12831 and 40 drawn with random.Random(20261116)): numbered display lines counted by `kbtool/qa_eqcount.py` (a stack scanner written apart from the extractor) against the equation rows with a number in the database.
- Agree exactly: 40 of 41; within 2 % or 2 lines: 41. Totals: independent 3142, database 3140.

| paper | input | independent | database | difference |
|---|---|---|---|---|
| 2611.12831 | raw main file | 139 | 139 | +0 |
| 0710.5073 | raw main file | 24 | 24 | +0 |
| 0711.1165 | raw main file | 26 | 26 | +0 |
| 0901.0989 | raw main file | 79 | 79 | +0 |
| 1105.1432 | raw main file | 9 | 9 | +0 |
| 1502.02011 | raw main file | 183 | 181 | -2 |
| 1703.08585 | raw main file | 46 | 46 | +0 |
| 1705.02358 | raw main file | 39 | 39 | +0 |
| 1710.02865 | raw main file | 91 | 91 | +0 |
| 1712.06383 | flat.tex | 46 | 46 | +0 |
| 1801.03507 | raw main file | 55 | 55 | +0 |
| 1805.09034 | raw main file | 33 | 33 | +0 |
| 1807.01711 | raw main file | 71 | 71 | +0 |
| 1901.08528 | raw main file | 25 | 25 | +0 |
| 1905.08890 | flat.tex | 111 | 111 | +0 |
| 2009.11081 | raw main file | 73 | 73 | +0 |
| 2011.12936 | raw main file | 13 | 13 | +0 |
| 2103.11918 | raw main file | 54 | 54 | +0 |
| 2106.01347 | raw main file | 29 | 29 | +0 |
| 2202.10798 | raw main file | 106 | 106 | +0 |
| 2203.06142 | flat.tex | 149 | 149 | +0 |
| 2211.10184 | raw main file | 50 | 50 | +0 |
| 2211.13659 | flat.tex | 211 | 211 | +0 |
| 2304.13284 | raw main file | 61 | 61 | +0 |
| 2306.11588 | raw main file | 17 | 17 | +0 |
| 2402.08642 | flat.tex | 115 | 115 | +0 |
| 2402.10190 | flat.tex | 350 | 350 | +0 |
| 2402.12672 | raw main file | 44 | 44 | +0 |
| 2404.15416 | flat.tex | 340 | 340 | +0 |
| 2502.06783 | raw main file | 45 | 45 | +0 |
| 2504.00075 | raw main file | 20 | 20 | +0 |
| 2504.05937 | flat.tex | 104 | 104 | +0 |
| 2505.04731 | raw main file | 46 | 46 | +0 |
| 2505.15903 | flat.tex | 17 | 17 | +0 |
| 2506.11795 | raw main file | 16 | 16 | +0 |
| 2604.03628 | raw main file | 21 | 21 | +0 |
| 2605.15260 | flat.tex | 31 | 31 | +0 |
| 2606.09690 | raw main file | 82 | 82 | +0 |
| 2606.26532 | raw main file | 76 | 76 | +0 |
| astro-ph/0412275 | raw main file | 81 | 81 | +0 |
| gr-qc/0201056 | raw main file | 14 | 14 | +0 |

## C9. The claims layer (K8)

- 861 claims on 121 papers; labels: abstract 16, background 7, fulltext 689, judgement 76, refuted 35, to_verify 38; statuses: checked 225, located 511, partial 12, refuted 35, unlocated 78.
- Locators 1044, resolved 1044; claims with a chunk 627; labels set by a person 340.
- By track (status counts): A-emd-pbh: checked 33, located 136, unlocated 1; B-emd-gw: checked 19, located 44, partial 1, unlocated 9; C-sidm: checked 15, located 94, partial 4; D-bh-dress: checked 21, located 65, partial 4, unlocated 10; E-stoch-inf: located 6, partial 1; F-hills: checked 53, located 29, partial 1, unlocated 5; brief: checked 42, located 11, partial 1, refuted 11, unlocated 47; core: checked 34, located 111, unlocated 5; kb: checked 8, located 15, refuted 24, unlocated 1.

## C10. References of the verification suite (CHARTER section 10)

- 27 arXiv ids in the section; ingested 27; missing: none.

Run time 242.0 s.
