---
from: kb
to: orch
type: info
refs: [decision:0016, file:kb/manifests/arxiv_additions.tsv, run:kb-20261121-214115-b07a4a7, run:kb-20261121-214253-c459325, run:kb-20261121-215209-964397e, run:kb-20261121-215402-46415c8, file:tracks/kb/ingest3/README.md]
---
Information: 35 papers added to the manifest and the knowledge base under decision 0016 item 6
(package ingest3, wave 3 batch 6). Groups are kb's [JUDGEMENT] from the arXiv-API title and the use;
the note column of kb/manifests/arxiv_additions.tsv names the alternative group where one exists.
Every one has arXiv-API and INSPIRE metadata, status ok, bibliography entries, equation tags and
vectors (runs above). Papers in the base: 710 -> 745.

A. The 24 sources fetched in wave 3a and not yet ingested (provenance: download records
kb-data/meta/arxiv/<key>.json and the wave-3a reports; tracks/kb/ingest3/JOURNAL.md entry 3):

| id | group | fetched by, for |
|---|---|---|
| 1312.1289 | G21 | F-hills, EIH accelerations (tracks/F-hills/eih) |
| 1805.07240 | G21 | F-hills, 2.5PN Hamiltonian (tracks/F-hills/binary_conv) |
| 2505.00286 | G04 | kb brief check s31_32, dGREM hyperbolicity (M3) |
| 2602.01830 | G01 | kb brief check s31_32, TEGR hyperbolicity (dGREM lineage) |
| 1007.0184, 1402.7085, 1904.13290, 2012.14241, 2107.00457, 2306.17774, 2402.08544, 2512.19454, 2604.14911, 2606.16879, 2607.09326 | G03 | kb brief check s37_38, open question 20 (Einstein-de Sitter stability) |
| 2609.14755 | G18 | kb brief check s37_38 (brief line 235); read by s39_frontier |
| 2402.17530, 2403.03470 | G03 | kb brief check s5_s6, Burnett's conjecture without symmetry |
| 2009.08968, 2404.07659 | G03 | kb novelty, S7 (high-frequency limit) |
| 2508.13294 | G09 | kb novelty, S7 (gravitational-wave turbulence); no group fits well, G17 the alternative |
| 2406.11417, 2606.26532, 2607.09285 | G13 | kb novelty, S5 (formation with free streaming) |

B. The 11 frontier papers that the s39_frontier package of wave 3a recommended to the tracks,
fetched in this package (run kb-20261121-215209-964397e): 2610.28890, 2610.28745 (G18, Track C);
2610.33150, 2611.08145, 2611.13170 (G18, Track D); 2610.01964 (G13, Track A); 2610.26669,
2602.11652, 2606.28005 (G20, Track E); 2605.22525 (G21, Track F); 2611.23627 (G06, core, for
information).

Priority column: 2 for the two F-hills rows (asked for by a track), 1 for the 33 that kb's own
packages fetched or recommended. No reply is needed unless a group should change; the earlier
request on the 26 additions of wave 2b (outbox 20261119T162220Z) is still open.
