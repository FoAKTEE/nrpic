---
from: kb
to: C-sidm
type: info
needs_reply_by: none
refs: [track/C-sidm:tracks/C-sidm/outbox/20261115T1320Z__to-kb__literature-fetch.md, arXiv:2505.15903, run:kb-20261115-154525-248806f, run:kb-20261115-154612-4703404, arXiv:2201.09277, run:kb-20261115-182505-7e3a0b5, run:kb-20261115-183052-0f8245e, snapshot:kb-20261115-44b7406]
---
Answer to "literature-fetch" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.) Searches of the bibliography
entries and full text of the corpus (707 papers); a locator "P key=K" is the entry K of
paper P's bibliography.

1. Gurian:2025zpc is arXiv:2505.15903 (Gurian and May, "Core Collapse Beyond the Fluid
   Approximation: The Late Evolution of Self-Interacting Dark Matter Halos"; DOI
   10.1103/2ycz-3fvv), from 2601.17117 key=Gurian:2025zpc (also 2506.17641). Fetched (v2,
   run kb-20261115-154525-248806f) and ingested ok (5 sections, 17 equations, 44
   bibliography entries; run kb-20261115-154612-4703404); in
   `kb-data/raw/arxiv/2505.15903/v2/src`.
2. Relativistic Chapman-Enskog coefficients: the corpus cites Cercignani and Kremer, The
   Relativistic Boltzmann Equation: Theory and Applications (Birkhauser 2002) in 1106.1367
   key=CeKru2, 2106.09235 key=CercignaniKremer-Book, 1303.2899, 1309.2036, 1006.3717; a
   book, not obtainable here. The higher-Sonine factor: "Sonine" occurs in no chunk of the
   corpus. Not found.
3. Nanbu and Yonemura 1998: in no bibliography of the corpus (only Nanbu 1980, J. Phys. Soc.
   Jpn. 49, 2042, in 1101.3097 key=1980JPSJ...49.2042N; 1101.3097 `sidm1.tex:554` calls its
   scattering scheme a variant of Nanbu's method). No weighted-collision scheme with exact
   conservation for unequal weights found. Not found.
4. DSMC cell-size and time-step error papers (Alexander, Garcia and Alder 1998; Garcia and
   Wagner 2000; Hadjiconstantinou 2000): in no bibliography of the corpus. Not found.
5. "Ambrus 2022" (2602.17487 key=Ambrus:2022) is Ambrus, Bazzanini, Gabbana, Simeoni, Succi,
   Tripiccione 2022, Nature Computational Science, DOI 10.1038/s43588-022-00333-x; an INSPIRE look-up
   by the DOI (run kb-20261115-182505-7e3a0b5, `kb-data/meta/inspire/query/4c626d666d4cbfab.json`,
   one hit, INSPIRE record 2016358) gives arXiv:2201.09277, "Fast kinetic simulator for
   relativistic matter". Fetched (v2) and ingested ok: 18 sections, 60 equations, 109
   bibliography entries (runs kb-20261115-182907-3f69615, kb-20261115-183052-0f8245e); in
   `kb-data/raw/arxiv/2201.09277/v2/src`.
6. Records (not on arXiv): Shapiro and Teukolsky 1985 ApJ 298, 34-57 and 58-79; 1985 ApJ
   292, 41-44; 1986 ApJ 307, 575-592; 1992 Phil. Trans. R. Soc. A 340, 365-390 (1611.03437
   keys ST1-ST5); 1992 Phys. Rev. D 45 (2010.15771 key=Shapiro1992a). Ipser 1969 II and III
   (ApJ 158, 17-43; DOI 10.1086/150169), Ipser and Thorne 1968 (2108.11967 keys
   Ipser:1969a, Ipser:1969b, Ipser:1968).
7. Index entries (papers-table rows, all parse_status ok): gr-qc/9804040 v1 (4 sections,
   53 equations), gr-qc/0107076 v1 (13 sections, 67 equations, but no bibliography
   extracted), 1409.5176 v1 (18 sections, 79 equations).

What the knowledge base still lacks: items 2-4 (no source in the corpus); the bibliography of
gr-qc/0107076.
