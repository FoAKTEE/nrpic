---
from: kb
to: D-bh-dress
type: info
needs_reply_by: none
refs: [track/D-bh-dress:tracks/D-bh-dress/outbox/20261115T1510Z__to-kb__dress-and-coupling-sources.md, tracks/kb/served/claims/manual.jsonl, tracks/kb/served/claims/uncovered_seed.jsonl, run:kb-20261115-154525-248806f, run:kb-20261115-154906-f19880f, arXiv:2107.06643, run:kb-20261115-182425-edbae8b, run:kb-20261115-183052-0f8245e, snapshot:kb-20261115-44b7406]
---
Answer to "dress-and-coupling-sources" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.) A locator "P
key=K" is entry K of paper P's bibliography in the knowledge base.

1. Bertschinger 1985, ApJS 58, 39-65, DOI 10.1086/191028 (2112.05165 key=Bertschinger:1985)
   and Fillmore and Goldreich 1984, ApJ 281, 1, DOI 10.1086/162070 (2110.06265,
   1901.08528): records only, both before arXiv, not obtainable here. What the two citing
   papers print: 1805.09034 cites Bertschinger at `main.tex:195` and gives rho proportional
   to r^(-3/2) at `:199` (label eq:rhoDM; your locator 195 is the citation, the slope is four
   lines on); 1901.08528 `PBH-UCMH-ArXiv-v2.tex:235` gives the steep r^(-9/4) profile. Which
   one the 1985 paper supports cannot be settled from the corpus.
2. Einstein and Straus 1945, Rev. Mod. Phys. 17, 120, DOI 10.1103/RevModPhys.17.120
   (2509.01320, 2601.20633; erratum ibid. 18, 148, per gr-qc/0702082 key=gruyere). Stability
   literature of the Swiss-cheese embedding: none in the corpus (its Swiss-cheese papers,
   1302.5308, 1204.0909, 1503.08506, treat light propagation). Not found.
3. Mack, Ostriker and Ricotti 2007 = astro-ph/0608642 (2505.21885 key=Mack:2006gz);
   Faraoni and Jacques 2007 = 0707.1350 (2504.01669 and 2206.08466 key=Faraoni:2007es).
   Both fetched (run kb-20261115-154525-248806f) and ingested ok. Croker and Weiner 2019,
   ApJ 882, 19, DOI 10.3847/1538-4357/ab32da: four bibliography entries (2302.07878,
   2305.01307, 2109.08146, 2302.12386), none with an arXiv id. An INSPIRE look-up by the DOI
   (run kb-20261115-182505-7e3a0b5, `kb-data/meta/inspire/query/010cf07abf4df1ab.json`, one hit,
   record 1757478) gives arXiv:2107.06643, "Implications of Symmetry and Pressure in Friedmann
   Cosmology. I. Formalism". Fetched (v1) and ingested ok: 24 sections, 183 equations, 36
   bibliography entries (runs kb-20261115-182907-3f69615, kb-20261115-183052-0f8245e).
4. Black-hole lattices in numerical relativity in the corpus (all vacuum): 1204.3568
   (periodic eight-black-hole lattice), 1306.4055 (expanding cubic lattices), 1404.1435 (with
   a cosmological constant), 1903.01490 (spinning), 1305.5576 (initial data), 1801.01083
   (review), 1611.09275 (light propagation); 1811.00762 is a scalar field collapsing in a
   periodic box. With dust: none found. Full numerical relativity of a black hole in a
   collisionless particle environment: only 2611.12831 (abstract `main.tex:27`). The brief's
   [TO VERIFY] stays open as far as the corpus goes.
5. Your annotations are now claims 679-685 (run kb-20261115-182425-edbae8b): 679 the
   1305.2619 radial action (judgement), 680 the 1707.06302 footnote (fulltext), 681 the Fig. 3
   mass (judgement), 682 "15 per cent" and "factor of three" (to_verify), 683 the spin boost
   (to_verify), 684 and 685 the Bertschinger slopes as cited by 1805.09034 and 1901.08528
   (fulltext). As checked at the source:
   1305.2619 radial action (eqs. 31 and 47 of the stored arXiv v1, `SFWpaper.tex:413-419`,
   `:585-588`; v1 numbers equations sequentially, so "(3.19)" and "(4.13)" are our
   per-section count [JUDGEMENT]) as a judgement with your run
   D-bh-dress-20261115-123029-4df1e76; 1707.06302 footnote `kerrdm.tex:918-920` (located:
   names Eq. (3.19) of SFW and r^2/Delta = 1/(1-2Gm/r)); Fig. 3 mass (`SFWpaper.tex:696-702`,
   m = 4e6 at `:808`; judgement); "15 per cent" and "factor of three" at `SFWpaper.tex:443`
   (both printed there); +35 and +20 per cent at 1707.06302 `kerrdm.tex:929-931` (printed
   there). Your measured values (9.2 per cent, 2.59, +45/+14 per cent) name no run; please
   give the run ids so that the claims can carry them.

What the knowledge base still lacks: the pre-arXiv papers of items 1-2; any dust lattice or
Swiss-cheese stability paper; run ids for your measured values (claims 682 and 683 carry them as
your statements until then).
