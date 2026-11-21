---
from: kb
to: orch
type: info
needs_reply_by: none
refs: [run:kb-20261121-231800-1988829, run:kb-20261121-231835-5f7d281, run:kb-20261121-232142-3378910, run:kb-20261121-232417-80127f0, run:kb-20261121-233151-3bb85dc, run:kb-20261121-233339-f153821, file:tracks/kb/claims_brief/README.md, file:tracks/kb/claims_brief/LEDGER.tsv, file:tracks/kb/claims_brief/DEFECTS.tsv, file:tracks/kb/claims_brief/REVIEW_SAMPLE.md]
---
Decision 0016 item 8: the rows of `coord/BRIEF_ERRATA.md` section 5 (defects in cited sources) are
now in kb's claims layer. Package claims_brief (kb, wave 3); details in
tracks/kb/claims_brief/README.md. KB-G3 material for the brief's own labelled statements
(brief 12.8) follows below.

**1. Section 5 of coord/BRIEF_ERRATA.md: claim ids** (run kb-20261121-233151-3bb85dc; rows
r1-r17 in the order of the table). Each printed statement is a claim labelled refuted. Where the
evidence gives the right value, a second claim supersedes it (`claims.supersedes`). That claim
is fulltext if I read the value at the locator, judgement if it was computed or read off a
figure, and abstract if it comes from a metadata record.

| Row | Source | Refuted (printed) | Superseding (label) |
|---|---|---|---|
| r1 | 2108.11967 Table 1; e^{2 Phi} | 813; 815 | 814 (judgement); none |
| r2 | gr-qc/0601112 Z_c; Table 3 | 816; 818 | 817; 819 (judgement) |
| r3 | conduction constant b (1101.3097 footnote) | 820 | 821 (fulltext) |
| r4 | 2502.06783 Eq. (17) | 822 | 823 (judgement) |
| r5 | draw prefactor, 2502.06783; 2610.32592 | 824; 826 | 825; 827 (judgement) |
| r6 | 2206.11234 weight sign; leading pole | 828; 829 | none (the runs refute, give no corrected form) |
| r7 | 2512.14649 Friedmann; USR interval and inflection | 830; 832 | 831; 833 (judgement) |
| r8 | 1305.2619 prose numbers; radial action; Fig. 3 mass | 834; 836; 838 | 835; 837; 839 (judgement) |
| r9 | 1707.06302 +35/+20 per cent | 840 | 841 (judgement) |
| r10 | 2611.12831 L729 pointer | 842 | none |
| r11 | 2604.03628 arXiv journal reference | 843 | 844 (abstract, INSPIRE record) |
| r12 | 1203.6185 two titles (no paper error) | fact 845 (abstract) | none |
| r13 | 1807.01711 abstract 1e-8 | 846 | 847 (fulltext) |
| r14 | 2512.13673 abstract r_crit; L276 pairs | 848; 850 | 849 (fulltext); 851 (judgement) |
| r15 | 2508.10070 "variance" | 852 | 853 (fulltext) |
| r16 | astro-ph/0608642 horizon mass | 854 | 855 (judgement) |
| r17 | 2607.09326 abstract without n > 3 | 856 | 857 (fulltext) |

The reports of the brief check asked for three more facts: 858 (2403.03470 proves Burnett's
conjecture without symmetry), 859 (1903.01490 horizon masses constant to 0.1 per cent) and 860
(2506.17641 v3 gives both seed estimates), all fulltext. In total 48 claims (813-860):
24 refuted, 14 judgement, 8 fulltext, 2 abstract. All 64 TeX locator rows resolve in the
database, and every paper named is ingested, so none is left unresolved. Claims 603-618 and
679-683 of other writers already hold some of the same findings; they are named in
`status_detail.existing` and were not changed.

**2. The brief's labelled statements (brief 12.8), counts for KB-G3.**

- Seeded: 112 statements of the main text, sections 1-10 and 15 (claims 701-812; run
  kb-20261121-231800-1988829; a second run added nothing). At seeding: abstract 46,
  title_only 5, background 17, judgement 20, to_verify 24. The 24 to_verify include the 15
  items of section 15, which carry the label through their heading.
- After joining the brief check (620 CHECK.md rows of 11 packages, 316 joined to 65 seeds;
  run kb-20261121-232417-80127f0):
  - verified (fulltext, located, checked): 42
  - refuted: 11 (claims 718, 737, 738, 742, 749, 752, 756, 766, 767, 782, 802)
  - open: 39. Of these, 9 have rows but not all at a full-text locator (8 located, 1 partial)
    and 30 have no CHECK.md row.
  - judgement: 20 (3 annotated with the rows on their factual parts). None is upgraded,
    per brief 12.8.
- Refutations to pass on: F-hills (claims 766, 767, brief lines 271-272) and A-emd-pbh
  (claim 742, line 208) carry those tags; the other refuted seeds carry no track tag.
- The 304 rows that joined no seed (219 on lines without a label, 85 outside the labelled
  sentence) are listed in tracks/kb/claims_brief/CHECK_UNJOINED.tsv. 17 of them are
  CORRECTED (s39_frontier 7, s5_s6 4, s31_32 2, s34_36 2, novelty 1, s33 1). Their
  corrections stand in coord/BRIEF_ERRATA.md, but they are not claims, because brief 12.8
  seeds only labelled statements.

**3. Review sample of CHECK.md** (a second agent; tracks/kb/claims_brief/REVIEW_SAMPLE.md).
I drew 30 rows (seed 20261121, run kb-20261121-232142-3378910): 3 from each of the eight
larger packages and 2 from each of novelty, s7_s8 and s39_frontier. I read every TeX locator
myself.
- Result: 30 agree, 0 disagree. The threshold was 3, so no package was held back.
- Remarks:
  - novelty #31: the package's "closest work" was not searched again.
  - s7_s8 #22: the content is right, but the class CORRECTED is strong. Errata row 2.101
    treats it as an imprecision, so claim 790 is annotated as partial, not refuted.
- An aside for the kb lead, [TO VERIFY]: 2002.12778 CKSY2021.tex:287 prints R_H^{-3} where
  the volume needs R_H^3.
