# Novelty of a Hills-type calculation in full numerical relativity (F-pre-5)

Search made on 2026-11-15 between 04:30 and 05:00 (UTC-8) by a helper of F-hills; what
was searched and how is in `search/SEARCH_LOG.md`. Labels as in the brief: [VERIFIED]
read in the source at the locator given (arXiv source in
`kb-data/raw/arxiv/<id>/<version>/src`, or the INSPIRE abstract where marked);
[JUDGEMENT] our reading.

## Verdict

No published full-numerical-relativity calculation was found in which

1. a bound binary is tidally separated by a black hole heavier than the binary
   (q = M/m_b > 1) on an unbound or marginally bound (parabolic or hyperbolic) orbit with
   pericentre inside or near the tidal radius, the Hills geometry; or
2. a binary of matter clumps (collisionless or fluid) passes a black hole, with the
   Einstein equations solved for all three bodies.

[JUDGEMENT, with the limits below] Both objects of decision 0005, (a) a black-hole binary
and (b) a binary of collisionless clumps passing a heavier black hole, are therefore
open in full NR as of this date. The claim must be stated narrowly. Full-NR evolutions of
three black holes, including the disruption of a binary by a third hole, do exist: for
equal masses (0710.0879, 0711.1165, 2505.03934) and for a binary on a bound orbit about a
heavier hole that is not separated (2406.11985, q = 4 and 9). What is new is the
combination: a heavier perturber (q >= 4), a near-parabolic orbit, pericentre at or
inside r_t, and the measured outcome (separated or not, energy split, capture orbit)
compared with the Newtonian and the geodesic-plus-Newtonian models. For object (b) the
novelty is wider: no full-GR calculation of a matter binary passing a black hole was
found at all.

## Closest papers, one by one

### Full NR, three or more black holes

- **arXiv:2406.11985** (Ficarra, Lousto 2024, "Close encounter of three black holes.
  III"; LazEv, moving punctures, Bowen-York data with TwoPunctures for the inner binary).
  The closest work. Section "High mass ratio" (`TBH3.tex` lines 582-626): an equal-mass
  binary orbiting a heavier hole with masses 8:1:1 and 18:1:1, co- and counter-orbiting;
  the binary merges after about one outer orbit and merger times grow with the mass
  ratio (`merger_times_massratio_table.tex`). Initial data (`massratio_table.tex` lines
  9-30): binary separation d = 1.98 M and 0.99 M, third hole at D = 12.93 M and 11.96 M
  on a quasi-circular orbit. In our variables (run `F-hills-20261115-045435-f62d553`):
  q = 4.0 and 9.0, a_b = 9.9 r_gb, D/r_t = 4.1 and 5.8. [VERIFIED] So these binaries sit
  outside the Newtonian disruption range (D < 2.1, arXiv:1804.02911 `mnras.tex` l. 361)
  and below the plunge bound a_b > 4 q^(2/3) (10.1 and 17.3): not Hills encounters, and
  no parabolic passage could separate them before plunging. [JUDGEMENT from those
  numbers] Also: scattering of a third equal-mass hole off a binary (`TBH3.tex` lines
  522-560) and a prompt disruption when the third hole starts closer than about 30 M
  (lines 686-688). The authors say the sequence "could be continued for at least until
  128:1:1" (lines 708-712): this group can reach the Hills regime and is the most likely
  to publish it first.
- **arXiv:2308.07365** (Ficarra, Ciarfella, Lousto 2023). Equal-mass, non-spinning
  hierarchical triples, inner binary d = 8 M, third hole at D = 30 M; merger delay
  ~1/D^2.5; a third hole closer than about 30 M breaks the binary up promptly (`TBH.tex`
  lines 66, 1040-1047). [VERIFIED] Equal masses, bound.
- **arXiv:2505.03934** (Heinze, Bruegmann, Dietrich, Markin 2025; BAM, multigrid
  solution of the Hamiltonian constraint for N punctures). Binary-single and
  binary-binary scattering from large separations; flybys, delayed or accelerated
  mergers, an exchange with ejection of one member (BSS-05, `apssamp.tex` lines 464-480).
  All black holes have equal mass (lines 110, 246): the single hole weighs half the
  binary (q = 0.5 in our notation). [VERIFIED] A binary is broken up by a black hole in
  full NR here, but by a lighter one, in the comparable-mass scattering regime, not by
  tidal separation. They state that NR cannot afford the ~10^3 or more scatterings that
  statistics need (line 108). Grids: 11 levels, finest spacing 0.0078 to 0.023 M for
  black holes of mass 0.5 (lines 270-290).
- **arXiv:0710.0879** (Campanelli, Lousto, Zlochower 2007) and **arXiv:0711.1165**
  (Lousto, Zlochower 2007). Three equal-mass holes, a third hole approaching a
  quasi-circular binary; outcomes prompt triple merger, elliptic binary with the third
  unbound, or disruption into three free holes (`second.tex` lines 50-60; `first.tex`
  lines 54-62). [VERIFIED] Equal masses. 0711.1165 announced unequal masses for a later
  paper (`second.tex` line 1059); 2406.11985 is that line of work.
- **arXiv:1004.1353** (Galaviz, Bruegmann, Cao 2010): three and four equal-mass holes,
  accurate initial data (`Punc_N.tex` lines 58-67). [VERIFIED] Equal masses.
- **arXiv:2108.01392** (Imbrogno, Meringolo, Servidio): three holes at rest or with
  small momenta taken from chaotic Newtonian (Burrau) configurations, masses in the
  ratio 3:4:5 or equal (`main.tex` lines 185, 269-277, 400). [VERIFIED] Comparable
  masses, no binary passing a heavier hole.
- **arXiv:2605.20320** (Cardoso, Ficarra, Redondo-Yuste, Santos 2026): head-on
  collisions of two holes from rest next to a companion of 1/3 or 1/2 of the total mass;
  all set-ups "safe against tidal disruption" by the Hills criterion R_H/d = 5 to 5.8
  (`main.tex` lines 134-160, 207-214). [VERIFIED] q = 0.5 to 1, no orbital passage.
- **arXiv:2610.09336** (Qiao, Liu 2026): head-on collisions of several holes from rest
  in symmetric configurations (`Liu_article_V2.tex` abstract, line 129). [VERIFIED]
- **arXiv:2505.01495** (Bamber, Shapiro, Ruiz, Tsokaros 2025): a cluster of 25
  equal-mass holes, one ejected after a several-body interaction. [VERIFIED: abstract]
  Equal masses.

### Relativistic but not full NR (the baselines of F-pre-2)

- **arXiv:2404.16270** (Manzaneda, Navarrete, Tejeda 2024): "Hybrid Relativistic-
  Newtonian Approximation", exact Schwarzschild acceleration plus Newtonian binary
  self-gravity, compared with Newtonian and 1PN (`article.tex` lines 123, 150). Tidal
  radius r_t = (M/m_b)^(1/3) a_0 (lines 165-176); relativistic effects significant below
  about 100 r_g (line 194); parabolic plunge limit 4 r_g (line 209); m_b = 1e-6 M and
  r_t = 101.3 r_g in their scans (lines 317-318). [VERIFIED] Point masses, extreme q.
- **arXiv:2402.02178** (Zhang, Chen 2024): binary black hole on a parabolic orbit past a
  Kerr SMBH in the free-fall frame with gravito-electromagnetic forces; they state that
  the dynamical range (outer orbit ~10^4 times the inner binary) makes full NR
  intractable (`main.tex` lines 216-226). [VERIFIED]
- **arXiv:2604.27429** (Sharma, Heger, Price, Tejeda, Grishin, Manzaneda et al. 2026):
  benchmark of three PN formulations and a scalar perturbation of the background metric
  for a binary near a SMBH; they write that a correct treatment "would require numerical
  relativity" (`template.tex` lines 45, 80). [VERIFIED]
- **arXiv:2605.22525** (Maeda, Okawa 2026): binary in the local inertial frame of Kerr
  with Riemann tidal terms; adiabatic, tidally affected, chaotic and disruptive regimes
  for unbound orbits. [VERIFIED: abstract] Not NR.
- **arXiv:1203.6185** (Cao, Yu, Lin and Bai 2012 on arXiv, `kb-data/meta/arxiv-api/1203.6185.json`; cited as "Bai et al. 2011" before 2026-11-21, errata section 5): a binary black hole in the potential of a third
  hole by a perturbative scheme, "instead of simulating the three-BH problem with a
  fully relativistic treatment". [VERIFIED: abstract]
- Matter binaries: SPH with Newtonian self-gravity on a Schwarzschild or Kerr
  background for white-dwarf binaries (arXiv:2508.03463, 2601.04870, 2609.20338),
  restricted three-body plus SPH for a star-white-dwarf binary (2608.22735); GR-SPH on a
  fixed Kerr metric with Newtonian or improved weak-field self-gravity for single stars
  (2608.16986, 2610.27775; the latter keeps "a binary of two polytropes stable over ten
  orbits" as a test only). [VERIFIED: abstracts] None evolves the spacetime.
- Single stars in full NR or full GR hydrodynamics: arXiv:1201.4389 (white dwarfs and
  spinning intermediate-mass holes), 1502.05740, 1408.1695 (brief l. 273), 2212.10891
  (white dwarfs on elliptic orbits about a 1e5 solar-mass hole), 1303.1540 (East and
  Pretorius: full Einstein equations with the truncation error of a known background
  subtracted, a star falling radially into a SMBH with mass ratio >= 1e6). [VERIFIED:
  abstracts] Single objects, no binary. The background-subtraction method of 1303.1540
  is relevant to the cost of F-pre-3 (scope, risk R2).
- Point-mass Newtonian, PN and secular studies (0911.1136, 1201.4794, 1804.02911,
  1501.07856, 1012.4423, 1108.4485, 1906.07726, 2511.00621 perturbative) are the
  references of F-pre-1 and F-pre-2, not competitors.

### Collisionless matter in NR

- The NRPIC source paper (arXiv:2611.12831, `refs/arxiv_2611.12831/src/main.tex` from
  line 1313) evolves two clumps that collapse to black holes and merge inside a common
  envelope; no third body. Web and INSPIRE searches for Einstein-Vlasov or
  particle-in-cell work with a binary passing a black hole found nothing (k06, web
  query 6).

## What may be said, and what not

May be said (with the date and these limits): "To our knowledge, the tidal separation of
a binary by a heavier black hole on a near-parabolic orbit has not been computed in full
numerical relativity; previous full-NR three-black-hole studies treat comparable masses
(0710.0879, 0711.1165, 1004.1353, 2505.03934) or binaries on bound orbits about a heavier
hole outside its tidal radius (2406.11985). No full-GR calculation of a binary of
collisionless clumps passing a black hole has been published."

Must not be said: "the first three-black-hole calculation with unequal masses" (false:
2406.11985); "the first full-NR disruption of a binary" (false: 0711.1165, 2505.03934
exchange); "first" without the date and the qualifiers.

## Limits of the search

- INSPIRE covers astro-ph only partly; full-text search covers only papers whose text
  INSPIRE has indexed. ADS was not searched; journals not on arXiv were not searched.
- Citation chasing relied on the canonical three-black-hole papers; an NR paper that
  cites none of 0710.0879, 0711.1165, 1004.1353, 2402.02178, 2404.16270 and uses other
  words (for example "triple", "tidal break-up", "binary-single") may be missed; queries
  k01, k02, k05, k08, k12 and the web searches were meant to catch such papers.
- Of query k04 (702 hits) only the 200 most cited were looked at; k12 narrowed the same
  title terms by NR method words in the full text (11 hits, none relevant).
- Theses and conference talks were found only when INSPIRE lists them (two found, not
  NR three-body work). Work in progress cannot be seen: the RIT group's stated plan to go
  to 128:1:1 (2406.11985 lines 708-712) and the BAM group's binary-single programme
  (2505.03934, and its follow-ups 2602.06961, 2610.20594 on PN N-body) are the likely
  competitors. Repeat the citation queries of 2406.11985 and 2505.03934 before any
  submission.
- The web search engine summaries were used only to find candidates; every statement
  above was checked in the source or the INSPIRE abstract at the locator given.
