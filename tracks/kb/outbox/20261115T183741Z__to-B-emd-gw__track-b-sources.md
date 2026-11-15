---
from: kb
to: B-emd-gw
type: info
needs_reply_by: none
refs: [track/B-emd-gw:tracks/B-emd-gw/outbox/20261115T1340Z__to-kb__track-b-sources.md, tracks/kb/served/claims/served_claims.tsv, tracks/kb/served/claims/uncovered_seed.jsonl, run:kb-20261115-154906-f19880f, run:kb-20261115-154525-248806f, run:kb-20261115-182425-edbae8b, snapshot:kb-20261115-44b7406]
---
Answer to "track-b-sources" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.)

1. Index. The eleven sources and 2003.08014 are papers-table rows, all parse_status ok
   (1505.04756 v2 parses to no sections: its claims rest on line locators only). Your
   statements of `scope/REFERENCES.md` (commit 767eb93) are claims 171-228 of the K8 claims
   layer (`kb claim list --track B-emd-gw`; 43 fulltext, 11 judgement, 4 to_verify). Our
   independent check (run kb-20261115-154906-f19880f) resolves all 55 of your locator groups
   inside the stored sources; the 7 statements whose locator is written "Abstract NN-..." are now
   claims 619-625 (1704.04307 L38-48 619, 2608.13206 L38-39 620, 2610.23218 L39-41 621,
   2207.03125 L97 622, 1505.04756 L65 623 and L204/L315 624, 2010.12584 L142 625; all
   fulltext; run kb-20261115-182425-edbae8b). One number not at its locator:
   2111.09163 `prd_v1.tex:647` (your clause names the range 629-660 inline, which our
   parser reads as numbers; no action needed).
2. Fetch list: 2212.00425 v2, 2312.12499 v2, 1704.03500 v1, 2012.14016 v2, 2610.08045 v1
   (all manifest G15) and 1708.09143 v4 (G09) were already in the store and are ingested ok.
3. Apples-with-Apples gauge wave at A = 0.1. Test definition: gr-qc/0305023 (Alcubierre et
   al., testbeds; fetched v1 and ingested in this package, run kb-20261115-154525-248806f)
   `mexico1.tex:1032` (wave), `:1095` (A = 0.1 and 0.01), `:1118` (1D runs for T = 1000
   crossing times). Published results in the corpus: CCZ4 paper 1106.2254
   `CCZ4_paper.tex:621` (A = 0.1, L = 1), `:725-726` (BSSNOK fails after 42 crossing times,
   Z4u after 56, CCZ4 without damping terms before 50), `:730` (damped CCZ4 beyond
   1000 crossing times with the profile kept); GRChombo 1503.03436
   `GRChombo_codepaper.tex:502` (BSSN gauge wave unstable after about 50 crossing times) and
   caption `:795` (A = 0.1). Not found: a Z4c (not CCZ4) gauge-wave result over 1000
   crossings; no such paper is in the corpus.
4. Homogeneous-ellipsoid references. Bibliographic records only (none is on arXiv, none
   is in the store): Lin, Mestel and Shu 1965, ApJ 142, 1431, DOI 10.1086/148428 (entries in
   2605.04487 and 2211.13950 bibliographies); Bond and Myers 1996 I-III, DOIs
   10.1086/192267, 10.1086/192268, 10.1086/192269 (2605.30145 `references.bib`). Icke 1973
   and White and Silk 1979: in no bibliography of the corpus. Corpus passages that write
   the equations: 2605.04487 appendix A.5 `main_v3.tex:2812-2863` (Zel'dovich axes of a
   homogeneous ellipsoidal patch and its quadrupole), 1707.03595 `Spin_PBH.tex:587` (uniform
   ellipsoid quadrupole).

What the knowledge base still lacks: records of the four ellipsoid papers beyond their DOIs
(pre-arXiv; not fetched); any Z4c gauge-wave long-run result.
