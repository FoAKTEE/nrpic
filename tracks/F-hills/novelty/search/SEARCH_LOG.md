# Search log of the novelty search F-pre-5 (2026-11-15)

All requests were generic physics queries (no project, person or repository detail).
Raw INSPIRE responses (JSON, untrusted data, not committed) are in
`/data/haiyangw/nrpic/scratch/F-hills/tmp/inspire/<label>/response.json` with the query and the
time in `query.txt`; they were made with `scripts/inspire_query.py` (list sorted by
citations) and `scripts/inspire_abstracts.py` (titles, authors, abstracts), both run with
`python3 -I`. arXiv sources were fetched only with `harness/bin/nrpic-fetch-arxiv` and
read in `kb-data/raw/arxiv/<id>/<version>/src`.

## INSPIRE (inspirehep.net literature API), times UTC-8

| label | time | hits | query |
|---|---|---|---|
| c_0710.0879 | 04:33 | 47 | `refersto:recid:763024` (citations of "Close encounters of three black holes") |
| c_0711.1165 | 04:35 | 104 | `refersto:recid:767003` ("Foundations of multiple black hole evolutions") |
| c_1004.1353 | 04:35 | 39 | `refersto:recid:851223` ("Numerical evolution of multiple black holes with accurate initial data") |
| c_2402.02178 | 04:35 | 16 | `refersto:recid:2755521` (binary flying by a Kerr SMBH) |
| c_2404.16270 | 04:35 | 4 | `refersto:recid:2780811` (relativistic tidal separation, HRNA) |
| c_1501.07856 | 04:35 | 15 | `refersto:recid:1342251` ("Busting up binaries") |
| k01 | 04:35 | 19 | `t "three black holes" or t "triple black hole" or t "triple black holes" or t "three-black-hole"` |
| k02 | 04:35 | 22 | `t "Hills mechanism" or (t "tidal separation" and t binary) or (t "tidal break-up" and t binary) or (t "tidal disruption" and t "binaries" and t "black hole")` |
| k03 | 04:35 | 10 | `fulltext:"Hills mechanism" and fulltext:"numerical relativity"` |
| k04 | 04:35 | 702 | binary black hole(s) in the title and (supermassive, massive black hole, third body, tidal field or environment, triple, hierarchical) in the title; only the 200 most cited were inspected; k12 narrows it |
| abs01 | 04:36 | 14 | abstracts of the candidates found so far |
| c_2406.11985 | 04:37 | 9 | `refersto:recid:2799952` ("Close encounter of three black holes. III") |
| c_2505.03934 | 04:37 | 8 | `refersto:recid:2919080` (BAM binary-single and binary-binary encounters) |
| c_2308.07365 | 04:37 | 11 | `refersto:recid:2688287` ("Close encounter of three black holes revisited") |
| c_2505.01495 | 04:37 | 15 | `refersto:recid:2918187` (25-black-hole cluster in full GR) |
| k05 | 04:42 | 2 | `fulltext:"tidal radius" and fulltext:"Hills" and (fulltext:"BSSN" or "Z4c" or "moving puncture" or "moving-puncture" or "CCZ4")` |
| k06 | 04:42 | 17 | `(fulltext:"Einstein-Vlasov" or "particle-in-cell" or "collisionless") and fulltext:"Hills mechanism"` |
| k07 | 04:42 | 14 | binary or binaries, and (supermassive black hole, massive black hole, Kerr), and (relativistic, general relativity, numerical relativity, general-relativistic) in the title, after 2010 |
| abs02 | 04:42 | 9 | abstracts of GR-hydrodynamics and binary-SMBH candidates |
| k08 | 04:43 | 3 | (tidal, third body, triple, three-body) and (numerical relativity, fully relativistic, full general relativity, nonlinear) and black hole(s), all in the title |
| abs03 | 04:43 | 3 | two theses without arXiv numbers (Pica 2024/2025; Nee 2026) |
| k09 | 04:43 | 8 | `a Ficarra, Giuseppe and date>2024` |
| k10 | 04:43 | 6 | `a Heinze, Felix and date>2024` |
| k11 | 04:43 | 5 | `fulltext:"three black holes" and fulltext:"tidal" and fulltext:"Hills" and date>2015` |
| k12 | 04:56 | 11 | binary in the title and (supermassive, massive black hole, third body, tidal field or environment, triple, hierarchical, three-body) in the title and (BSSN, moving puncture, Z4c, CCZ4, generalized harmonic) in the full text |

## Web search (general engine, 2026-11-15)

1. numerical relativity simulation binary black hole tidally separated by a larger black hole Hills mechanism (extended mode)
2. full general relativity three black holes binary disrupted exchange ejection mass ratio simulation 2025 2026
3. general relativistic simulation binary neutron star or binary star passing supermassive black hole tidal separation fully relativistic
4. "three black holes" numerical relativity "mass ratio" hierarchical binary orbiting larger black hole merger delay 2025
5. numerical relativity binary of stars or clusters or boson stars flyby massive black hole tidal disruption of a binary full Einstein equations
6. Einstein-Vlasov collisionless matter clumps binary black hole encounter numerical relativity tidal stripping
7. 2026 numerical relativity "binary black hole" parabolic encounter "intermediate-mass black hole" tidal break-up full GR simulation puncture

No hit of the web searches was outside the INSPIRE results except older single-star
full-GR work (arXiv:1303.1540, East and Pretorius, a star falling into a SMBH) and
Newtonian/hybrid binary-star papers already listed.

## Reference chasing

Brief lines 267-278 (section 3.11) and group G21 (lines 2475-2529): every full-NR or
relativistic-three-body entry was looked up (citations above for 0710.0879, 0711.1165,
1004.1353, 2402.02178, 2404.16270, 1501.07856; abstracts for the rest). The citations of
the three closest papers found on the way (2406.11985, 2505.03934, 2308.07365) and of
2505.01495 were listed as well.

## arXiv sources read (kb-data/raw/arxiv)

0710.0879 v2, 0711.1165 v2, 1004.1353 v2, 0911.1136 v1, 1804.02911 v1, 2402.02178 v1,
2404.16270 v1 (already present); fetched for this search: 2406.11985 v1, 2308.07365 v1,
2505.03934 v2, 2605.20320 v2, 2108.01392 v3, 2604.27429 v1, 2610.09336 v1. The NRPIC
source paper `refs/arxiv_2611.12831/src/main.tex` was grepped for Hills and three-body
content (none; its binary is two clumps that collapse and merge inside an envelope,
section from line 1313).
