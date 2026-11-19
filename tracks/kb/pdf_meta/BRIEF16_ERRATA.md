# Brief section 16 against the downloaded metadata: the differences

Helper pdf_meta of kb, 2026-11-19. Proposed as a new section of `coord/BRIEF_ERRATA.md`
(owner orch); sent as `tracks/kb/outbox/*__to-orch__brief16-titles-authors.md`.

How it was established [VERIFIED by script, run kb-20261119-143702-aa436e7]: the 684 entries of
brief section 16 (lines 1763-2529, parsed by `kb/kbtool/meta_brief16.py`) were compared entry by
entry with the arXiv-API record (`kb-data/meta/arxiv-api/<key>.json`, fetched in run
kb-20261115-182505-7e3a0b5) and with the INSPIRE record (`kb-data/meta/inspire/<key>.json`, same
run; 2107.06643 and 2201.09277 in run kb-20261119-142559-387c3bc). Titles are compared after
folding case, accents, TeX and MathML; authors by surname, in order. The full table is
`brief16_comparison.tsv` (one row per entry, classes only); figure `figures/fig_brief16.png`.
Titles and author names below are bibliographic metadata copied from the records, not paper text.

## Summary

| Check | Result |
|---|---|
| Section 16 entries | 684, all with an arXiv link, groups G01-G21 with the declared counts |
| Section 16 against section 17 | the same 684 ids; group and priority (★ ◆ · = 3 2 1) equal for every id |
| Titles equal to the arXiv title (up to case, accents, TeX, punctuation) | 659 (548 identical, 111 formatting only) |
| Titles that differ from the arXiv title but equal an INSPIRE title variant (the published title) | 24 (table B) |
| Titles that differ from both | 1: gr-qc/0312117, where both records carry a typo and the brief is right (row A.4) |
| Author fields that agree with the arXiv list | 622 match, 5 name a collaboration (table D), 51 list no authors |
| Author fields that differ from the arXiv list but agree with INSPIRE | 3 (table C) |
| Author fields that differ from both | 3 (rows A.1-A.3) |
| Entries that agree with arXiv or INSPIRE in title and authors | 680 of 684 (`papers.title_matches_brief` = 1) |

## A. Proposed rows for coord/BRIEF_ERRATA.md (section "Reference list, brief section 16")

| # | Brief line | What the brief says | What is right | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| A.1 | 1838 (§16, G03) | arXiv:2310.00776 — "Andréasson" (as sole author) | Two authors: E. Ames, H. Andréasson (arXiv and INSPIRE agree) | `kb-data/meta/arxiv-api/2310.00776.json`, `meta/inspire/2310.00776.json`; run kb-20261119-143702-aa436e7 | kb (pdf_meta) |
| A.2 | 1973 (§16, G07) | arXiv:2107.06306 — "Grasso, Villa, Korzyński, Matarrese" | Two authors: Michele Grasso, Eleonora Villa; Korzyński and Matarrese are not authors of this paper (arXiv and INSPIRE agree) | `meta/arxiv-api/2107.06306.json`, `meta/inspire/2107.06306.json`; same run | kb (pdf_meta) |
| A.3 | 2389 (§16, G19) | arXiv:2204.13098 — "Hassani, Shi, Adamek, Kunz, Wittwer" | Order: Hassani, Adamek, Kunz, Shi, Wittwer (arXiv and INSPIRE agree) | `meta/arxiv-api/2204.13098.json`, `meta/inspire/2204.13098.json`; same run | kb (pdf_meta) |
| A.4 | 2341 (§16, G17) | arXiv:gr-qc/0312117 — "Numerical simulations of generic singularities" | No correction of the brief: its spelling is the paper's (`\title` at `kb-data/build/tex/gr-qc_0312117/flat.tex:12`); the arXiv and INSPIRE records both spell "singuarities". A search by the record title must allow the typo | same run | kb (pdf_meta) |

## B. Titles that follow the published title (INSPIRE), not the arXiv listing

No correction needed [JUDGEMENT]: each brief title equals one of the INSPIRE title variants. The
knowledge base keeps the arXiv title in `papers.title` and the brief's in `papers.brief_title`.

| # | Brief line | id | Brief (= an INSPIRE title) | arXiv listing |
|---|---|---|---|---|
| B.1 | 1800 | gr-qc/9412071 | A New formalism for numerical relativity | New Formalism for Numerical Relativity |
| B.2 | 1819 | 2305.04360 | Hoop and weak cosmic censorship conjectures for the axisymmetric Einstein-Vlasov system | On the Hoop conjecture and the weak cosmic censorship conjecture for the axisymmetric Einstein-Vlasov system |
| B.3 | 1822 | 1707.08666 | Distribution functions for a family of general-relativistic hypervirial models in the collisionless regime | ... Hypervirial models in collisionless regime |
| B.4 | 1926 | 2307.11701 | Mean curvature flow method for numerical cosmology | A mean curvature flow method for numerical cosmology |
| B.5 | 1957 | 2110.00893 | Accurate relativistic observables from postprocessing light cone catalogs | ... post-processing light cone catalogues |
| B.6 | 2034 | 1502.02985 | Missing link: A nonlinear post-Friedmann framework for small and large scales | The missing link: a nonlinear post-Friedmann framework ... |
| B.7 | 2039 | 2109.13364 | ... by modifying the initial conditions | ... by modifying the initial condition |
| B.8 | 2040 | 0907.0707 | A New Perspective on Galaxy Clustering as a Cosmological Probe: General Relativistic Effects | New Perspective on Galaxy Clustering ... |
| B.9 | 2063 | hep-ph/0409038 | The effect of inhomogeneities on the expansion rate of the universe | Effect of inhomogeneities on the expansion rate of the Universe |
| B.10 | 2070 | 2509.01320 | Elements of cosmology beyond FLRW | Les Houches on Dark Universe 2025: Elements of cosmology beyond FLRW |
| B.11 | 2138 | 1404.1435 | Black hole universe with a cosmological constant | Black Hole Universe with Λ |
| B.12 | 2153 | 2011.12190 | Inhomogeneous preinflation across Hubble scales in full general relativity | Inhomogeneous initial conditions for inflation: A wibbly-wobbly timey-wimey path to salvation |
| B.13 | 2158 | 1906.08651 | Onset of inflation amid backreaction from inhomogeneities | A Bumpy Start to a Smooth Ride: Onset of Inflation amid Backreaction from Inhomogeneities |
| B.14 | 2200 | 2006.15122 | The art of simulating the early Universe -- Part I: Integration techniques and canonical cases | The art of simulating the early Universe -- Part I |
| B.15 | 2203 | 1909.11678 | Lighting the Dark: Evolution of the Postinflationary Universe | Lighting the Dark: The Evolution of the Post-Inflationary Universe |
| B.16 | 2229 | 1907.13311 | Universal threshold for primordial black hole formation | A universal threshold for primordial black hole formation |
| B.17 | 2259 | 2312.11982 | Toward supermassive primordial black holes from inflationary bubbles | Towards supermassive ... |
| B.18 | 2378 | 2106.07480 | ... primordial black holes. Part I. Density profiles | ... primordial black holes I: density profiles |
| B.19 | 2404 | 2008.07546 | K-dynamics: well-posed initial value 1+1 evolutions in K-essence | K-dynamics: well-posed 1+1 evolutions in K-essence |
| B.20 | 2408 | astro-ph/9407016 | Equilibrium state of a selfinteracting scalar field in the De Sitter background | Equilibrium State of a Massless Self-Interacting Scalar Field in the De Sitter Background (the title page of the stored PDF has no "massless": `kb-data/build/tex/astro-ph_9407016/flat.tex:2-3`) |
| B.21 | 2467 | 2403.12811 | The Inflationary Butterfly Effect: ... | Inflationary Butterfly Effect: ... |
| B.22 | 2471 | 2102.01031 | CosmoLattice: A modern code for lattice simulations of scalar and gauge field dynamics in an expanding universe | CosmoLattice (the subtitle is on the title page of the source, `build/tex/2102.01031/flat.tex:147`) |
| B.23 | 2522 | 1908.09752 | A lower bound on the primordial black hole merger rate | Lower bound on ... |
| B.24 | 2526 | 2310.00042 | ... Stellar-mass Binaries in the mHz Band | ... Stellar-Mass Binaries in the Milli-hertz Band |

## C. Author order that follows INSPIRE, not the arXiv listing

| # | Brief line | id | Brief | arXiv listing | INSPIRE |
|---|---|---|---|---|---|
| C.1 | 2136 | 1204.2411 | Yoo, Abe, Nakao, Takamori | Yoo, Abe, Takamori, Nakao | Yoo, Abe, Nakao, Takamori |
| C.2 | 2314 | hep-th/0703290 | Baumann, Steinhardt, Takahashi, Ichiki | Baumann, Ichiki, Steinhardt, Takahashi | as the brief |
| C.3 | 2500 | 1203.6185 | Bai (first author) | first author Cao (Cao, Yu, Lin, Bai, Yo) | alphabetical, six names (Bai, Cao, Han, Lin, Yo, Yu) |

C.3 is worth a row in BRIEF_ERRATA [JUDGEMENT]: "Bai (first author)" comes from INSPIRE's
alphabetical list; on the arXiv listing Bai is the fourth of five authors.

## D. Collaboration entries (no correction)

2406.05048 (L2077, "DES Collaboration": the arXiv record lists 80 individual names, not the
collaboration), 2404.03002 and 2503.14738 (L2106-2107, "DESI Collaboration", listed first on
arXiv), 2504.01669 (L2110, "CosmoVerse Network", 541 individual names), 2210.11426 (L2127,
"COMPACT Collaboration", 15 individual names).

The 51 entries with an empty author field now have their authors in `papers.authors_json`.
