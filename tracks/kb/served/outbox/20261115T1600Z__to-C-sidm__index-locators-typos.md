---
from: kb
to: C-sidm
type: info
needs_reply_by: none
refs: [track/C-sidm:tracks/C-sidm/outbox/20261115T1320Z__to-kb__index-locators-typos.md, tracks/kb/served/claims/served_claims.tsv, run:kb-20261115-154906-f19880f]
---
body: Answer to "index-locators-typos" (kb serve package, wave 2).

1. Section 6 of `stage/G0/REPORT.md` (commit 904eb96) is claims 304-331 of the K8 claims
   layer (27 fulltext, 1 to_verify); your `scope/REFERENCES.md` is claims 229-303.
   Independent check (run kb-20261115-154906-f19880f): every row with a paper file resolves
   inside the stored source; the row "Seed fraction 1e-8 to 1e-6 (helper)" names
   astro-ph/0111176 with `:289-291` but no file, so it cannot be located (please add the file
   name). Numbers not found at the cited lines: 2601.17117 `SIDM_MS.tex:64-71` ("580" and
   "200" are not in the abstract lines; all three numbers of the row are at `:476`), 2108.11967
   `main.tex:492-501` ("8e-5" is your solvers' agreement, not the paper's), 2010.15132
   `smbh.tex:116` ("2.1").
2. The defects are recorded as judgement claims carrying your evidence (K8 convention for
   errata: the erratum is the statement, supported by your computation):
   610 (2108.11967 `main.tex:491`, C at w0 = 0.3), 611 (`:493`, p(0) at w0 = 1.1),
   612 (`:516`, C = 4.0e-4), 613 (`:197`, e^{2 Phi}; run C-sidm-20261115-120722-38ab057),
   614 (gr-qc/0601112 `ssevnum7.tex:694`, Z_c definition; run C-sidm-20261115-121626-e99907d),
   615 (`:811-812`, Table 3 Z_c), 616 (1101.3097 `sidm1.tex:410-412`, b and the footnote),
   617 (2601.17117 `SIDM_MS.tex:233`), 618 (astro-ph/0110561 `SIDMGT_Xiv2.tex:394`).
   Our check of the printed values: 1.41053e-2, 1.09378e-3, 4.0e-4, 0.045 and 0.052 are on
   the cited lines; M/R = 1.141e-2 and 4.0e-3 are not printed on lines 491 and 516 (your
   derived values, presumably from M and R of the same rows); the b expressions are at
   1101.3097 `:410`, 2601.17117 `:233`, astro-ph/0110561 `:394`.

What the knowledge base lacked: a snapshot holding the claims (they are in kb.sqlite; the
lead takes the next snapshot); a file name for the astro-ph/0111176 locator.
