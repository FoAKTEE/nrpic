# Quality report of the knowledge base (brief 12.9)

Written by `kb qa run` (kbtool/qa_report.py) at 2026-11-15T15:55:08Z from `/data/haiyangw/nrpic/kb-data/db/kb.sqlite` (db/current: `kb-20261115-f2fcda5.sqlite`). Ids, counts and our own wording only; no paper text.

## C1. Counts against the manifests

- Manifest (brief section 17): 684 arXiv ids; downloads by status: ok 683, problem 1.
- Ingested: 683 of 684 manifest ids; 24 extras; 707 papers in all. Not ingested: gr-qc/9412071.
- Priority 3: 47 of 47 ingested, 45 with status ok.
- Priority 2: 160 of 160 ingested, 152 with status ok.
- Priority 1: 476 of 477 ingested, 461 with status ok.
- Missing or failed downloads: none.
- Verdict: counts do NOT agree (lists above).

## C2. Abstract and at least one section for every paper

- 651 of 707 papers have both. Without an abstract (27): 1810.03490, 1911.04505, 1911.09689, 2004.10754, 2009.08715, 2012.09255, 2109.01398, 2201.03458, 2211.13659, 2403.15126, 2406.02417, 2501.13046, 2506.21423, 2509.01320, 2510.13129, 2602.00155, 2610.32592, astro-ph/0003278, astro-ph/0306304, astro-ph/9306009, astro-ph/9407016, astro-ph/9510056, gr-qc/0012059, gr-qc/0201056, gr-qc/0703035, gr-qc/9604001, gr-qc/9906015.
- Without any section (37): 0710.0879, 0710.5073, 1005.4054, 1207.1286, 1304.7791, 1306.1562, 1408.2741, 1505.04756, 1511.01105, 1511.05124, 1810.03613, 1907.08129, 2006.01172, 2104.12293, 2105.11880, 2201.03458, 2210.11426, 2211.15674, 2302.00655, 2311.17644, 2312.03860, 2504.15978, astro-ph/0003278, astro-ph/0306304, astro-ph/9306009, astro-ph/9407016, astro-ph/9510056, astro-ph/9709072, gr-qc/0312117, gr-qc/0511048, gr-qc/0511103, gr-qc/0608095, gr-qc/9402041, gr-qc/9604001, gr-qc/9703066, gr-qc/9906015, hep-ph/9809574.
  - of these, no sectioning command at all in flat.tex (letters, plain TeX): 36; a sectioning command present but no section extracted: 1 (astro-ph/0003278); no flat.tex: none.

## C3. Parse failures and the review list, by cause

- 25 papers not ok: failed 1, pdf 1, review 23.
- Causes (several per paper possible; from the quality components stored in papers.parse_json):
  - no abstract environment: 21
  - no \title: 20
  - no sections: 7
  - many unresolved macros: 5
  - thesis or long document: 4
  - no \documentclass (plain TeX or fragment): 4
  - unresolved \input: 2
  - no TeX source (PostScript or nothing usable): 1
  - parser error: 1
  - PDF only (text extraction, no equations): 1

| paper | status | score | causes |
|---|---|---|---|
| astro-ph/9407016 | failed | 0.0 | no TeX source (PostScript or nothing usable); parser error |
| 2201.03458 | pdf | 0.2 | PDF only (text extraction, no equations) |
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

- Sample (random.Random(20261115), from the ingested papers): 1004.1353, 1111.2997, 1305.4634, 1403.4947, 1511.05124, 1607.00381, 1609.04724, 1610.05635, 1703.08585, 1703.10543, 1707.06079, 1707.08666, 1904.11773, 2007.04968, 2102.03774, 2103.01183, 2106.09235, 2110.00893, 2110.06265, 2308.07365, 2311.01438, 2401.06329, 2404.15416, 2409.09597, 2409.16053, 2505.03934, 2606.02712, astro-ph/0003278, gr-qc/0412063, gr-qc/9906015.
- **Blocked**: no INSPIRE or arXiv-API record exists under kb-data/meta/arxiv for any of them (the metadata stage of K1 waits for the fetch path of decision 0015). The comparison code (`qa_report.compare_meta`: title similarity, surnames found) is tested on synthetic records.

## C5. Bibliography resolution and the citation graph

- 64712 bibliography entries; with an arXiv id 38775 (59.9 %), with a DOI 20022, with any identifier 46873 (72.4 %).
- By source: bbl 47206 entries, 36529 with an id; bib 4555 entries, 4187 with an id; thebibliography 12951 entries, 6157 with an id.
- By resolution step: arxiv-id 38468, doi 8098, none 17839, title-fuzzy-corpus 307.
- Distinct citation edges (citing paper, cited arXiv id): 38406, inside the corpus 5700 (14.8 %); the definition of the K3 report.
- Citation rows (one per `\cite` occurrence): 104726; in the corpus 12415 (11.9 %); of the 75923 rows with an identifier, 16.4 % in the corpus.

## C6. Duplicates

- Papers stored in more than one version: 0 (the database holds one version per id).
- Different ids with identical flattened text: none; identical source bytes: none.
- Different ids with the same normalised title: none; same abstract start: none.

## C7. Retrieval regression (golden questions)

- 32 questions (kbtool/qa_golden.py; own wording, answers from KB-G1 and checked claims); hit within the top 10 chunks. Vectors stored for 29184 of 43398 chunks.
- Hits of papers with an empty source map (no line range; `embed_search.Locator.lines` raises IndexError there, guarded in this run): 2201.03458.
- **text**: paper hit rate 27/32 (84.4 %), locator hit rate 21/32 (65.6 %), mean reciprocal rank of the paper 0.712.
- **hybrid**: paper hit rate 22/32 (68.8 %), locator hit rate 15/32 (46.9 %), mean reciprocal rank of the paper 0.461.

| question | paper | text paper rank | text locator rank | hybrid paper rank | hybrid locator rank |
|---|---|---|---|---|---|
| q01 | 2111.05282 | 1 | - | 1 | - |
| q02 | 2611.12831 | 1 | 1 | 2 | 2 |
| q03 | 2611.12831 | 1 | 1 | 1 | 1 |
| q04 | 2611.12831 | 1 | 6 | 1 | 2 |
| q05 | 2611.12831 | 2 | 2 | 3 | 3 |
| q06 | 2611.12831 | 2 | - | 10 | - |
| q07 | 2611.12831 | - | - | 5 | - |
| q08 | 2611.12831 | 1 | 2 | 1 | 1 |
| q09 | 2611.12831 | 1 | 2 | 1 | 1 |
| q10 | 2611.12831 | 1 | 1 | - | - |
| q11 | 2609.14218 | - | - | - | - |
| q12 | 2609.14218 | - | - | - | - |
| q13 | 2512.14649 | 7 | - | - | - |
| q14 | 2404.16270 | 1 | 4 | 1 | 2 |
| q15 | 2610.23218 | 1 | 1 | 1 | 1 |
| q16 | 1609.01588 | 1 | - | 1 | - |
| q17 | 2507.18312 | - | - | - | - |
| q18 | 1901.04498 | 2 | 2 | - | - |
| q19 | 2403.15126 | 1 | 1 | 1 | 1 |
| q20 | 2605.04487 | 2 | - | 1 | - |
| q21 | 2605.04487 | 1 | 1 | 1 | 1 |
| q22 | 1604.06065 | 7 | 7 | 2 | 2 |
| q23 | 2501.13046 | 1 | 1 | 4 | 4 |
| q24 | astro-ph/0110561 | - | - | 2 | - |
| q25 | 1305.2619 | 1 | - | 9 | - |
| q26 | 1707.06302 | 1 | 1 | 8 | 8 |
| q27 | 2109.04896 | 1 | 1 | 1 | 1 |
| q28 | 2302.07878 | 1 | 1 | 8 | 8 |
| q29 | 2305.01307 | 1 | 1 | - | - |
| q30 | 2505.03934 | 1 | 1 | - | - |
| q31 | 2108.01392 | 2 | 3 | - | - |
| q32 | 2610.09336 | 1 | 1 | - | - |

## C8. Independent equation count on a sample

- 41 papers (2611.12831 and 40 drawn with random.Random(20261116)): numbered display lines counted by `kbtool/qa_eqcount.py` (a stack scanner written apart from the extractor) against the equation rows with a number in the database.
- Agree exactly: 41 of 41; within 2 % or 2 lines: 41. Totals: independent 2295, database 2295.

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
| 2108.01392 | raw main file | 19 | 19 | +0 |
| 2109.13364 | raw main file | 32 | 32 | +0 |
| 2206.05624 | raw main file | 6 | 6 | +0 |
| 2208.05018 | raw main file | 25 | 25 | +0 |
| 2209.02735 | raw main file | 104 | 104 | +0 |
| 2304.01673 | raw main file | 34 | 34 | +0 |
| 2304.09817 | raw main file | 12 | 12 | +0 |
| 2310.00042 | raw main file | 30 | 30 | +0 |
| 2311.17644 | raw main file | 49 | 49 | +0 |
| 2406.05838 | raw main file | 47 | 47 | +0 |
| 2407.08775 | raw main file | 67 | 67 | +0 |
| 2408.09964 | raw main file | 63 | 63 | +0 |
| 2410.17987 | raw main file | 89 | 89 | +0 |
| 2507.17969 | raw main file | 23 | 23 | +0 |
| 2508.03463 | raw main file | 13 | 13 | +0 |
| 2509.01320 | flat.tex | 28 | 28 | +0 |
| 2510.13129 | flat.tex | 149 | 149 | +0 |
| 2511.04676 | raw main file | 137 | 137 | +0 |
| 2512.08703 | raw main file | 32 | 32 | +0 |
| astro-ph/0101406 | raw main file | 37 | 37 | +0 |
| astro-ph/0501177 | raw main file | 0 | 0 | +0 |
| astro-ph/0702575 | raw main file | 0 | 0 | +0 |
| astro-ph/9709072 | raw main file | 12 | 12 | +0 |

## C9. The claims layer (K8)

- 618 claims on 70 papers; labels: background 1, fulltext 507, judgement 37, to_verify 73; statuses: checked 29, located 516, partial 33, unlocated 39, unresolved 1.
- Locators 679, resolved 678; claims with a chunk 557; labels set by a person 29.
- By track (status counts): A-emd-pbh: checked 7, located 155, partial 5, unlocated 3; B-emd-gw: checked 6, located 39, partial 5, unlocated 8; C-sidm: checked 1, located 104, partial 6, unresolved 1; D-bh-dress: checked 7, located 70, partial 2, unlocated 10; E-stoch-inf: located 6, partial 1; F-hills: checked 3, located 16, partial 6, unlocated 7; core: checked 5, located 126, partial 8, unlocated 11.

## C10. References of the verification suite (CHARTER section 10)

- 27 arXiv ids in the section; ingested 27; missing: none.

Run time 24.8 s.
