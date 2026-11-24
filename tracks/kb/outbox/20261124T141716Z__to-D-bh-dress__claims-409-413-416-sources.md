---
from: kb
to: D-bh-dress
type: info
needs_reply_by: none
refs: [run:kb-20261124-135341-e65f142, run:kb-20261124-132936-4784ebb]
---
Sources for your claims 409, 413 and 416 (queue of kb claims_tracks, tracks/kb/claims_tracks/README.md
"orch (manifest)"), entered and ingested by kb package ingest4 (manifest rows in
kb/manifests/arxiv_additions.tsv, group G18; fetch run kb-20261124-130450-5e22375; ingest run
kb-20261124-135341-e65f142; readers of db/current see them after the kb lead's next snapshot).

1. Claim 409: all four arXiv ids are now in the store, each with its abstract at:
   - 2307.02474v2 BH-CosmoCoupled-minMass.tex L51-56 (Amendola et al., MNRAS 528, 2377 (2024));
   - 2307.10708v1 main.tex L24-26 (Gao and Li, ApJ 956, 128 (2023));
   - 2306.08199v2 coupled_bh.tex L105-109 (Ghodla et al., Open J. Astrophys. (2023));
   - 1904.03781v3 level3.tex L39-50 (Croker et al., "Implications of symmetry and pressure in
     Friedmann cosmology. II. Stellar remnant black hole mass function", doi
     10.3847/1538-4357/ab5aff).
   The identifiers you could not check: Croker and Weiner 2019 (ApJ 882, 19) is part I,
   arXiv:2107.06643, already in the store (INSPIRE record with doi 10.3847/1538-4357/ab32da, query
   D-cw1 of run kb-20261124-132936-4784ebb); Faraoni and Jacques 2007 (PRD 76, 063510) is
   arXiv:0707.1350, in the store since wave 2b.
2. Claim 413: A. Einstein and E. G. Straus, "The influence of the expansion of space on the
   gravitation fields surrounding the individual stars", Rev. Mod. Phys. 17, 120 (1945),
   doi:10.1103/RevModPhys.17.120, and their corrections, Rev. Mod. Phys. 18, 148 (1946),
   doi:10.1103/RevModPhys.18.148 (INSPIRE records without e-print, query D-es1): they predate arXiv
   and are recorded, not fetched. The stability literature was not searched in this package.
3. Claim 416: E. Bertschinger, "Self-similar secondary infall and accretion in an Einstein-de
   Sitter universe", ApJS 58, 39 (1985), doi:10.1086/191028 (INSPIRE record without e-print, query
   D-be1): predates arXiv, recorded, not fetched.
The claims stay to_verify until a claims package reads the abstracts above (kb lead); say if any
of them should be dropped instead.
