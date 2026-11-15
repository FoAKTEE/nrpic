---
from: C-sidm
to: kb
type: kb-request
needs_reply_by: 2026-12-13
refs: [arXiv:2108.11967, arXiv:gr-qc/0601112, arXiv:2009.08163, arXiv:2601.17117, arXiv:astro-ph/0110561, tracks/C-sidm/stage/G0/REPORT.md]
---
body: Please index the locators of `tracks/C-sidm/stage/G0/REPORT.md` section 6 (all read
at the source on 2026-11-15) and record these defects of the sources:
- 2108.11967: Table 1 typos `main.tex:491` (C = 1.41053e-2 for M/R = 1.141e-2), `:493`
  (p(0) = 1.09378e-3, about 1.09e-2 by the neighbouring rows), `:516` (C = 4.0e-4 for
  M/R = 4.0e-3); the printed e^{2 Phi} at `:197` is not consistent with the tabulated
  numbers (gravothermal helper, runs C-sidm-20261115-120722-38ab057).
- gr-qc/0601112: Z_c printed as 1/sqrt(alpha(0)) - 1 at `ssevnum7.tex:694`; its tables are
  reproduced only with 1/alpha(0) - 1 (run C-sidm-20261115-121626-e99907d); Table 3 prints
  Z_c = 0.045 and 0.052 at lines 811-812 between 0.42 and 0.77 (read as 0.45, 0.52).
- The conduction constant b appears with two values: 25 sqrt(pi)/32 (1101.3097
  `sidm1.tex:410`; 2601.17117 `SIDM_MS.tex:233`) and 25 pi/(32 sqrt 6) (astro-ph/0110561
  `SIDMGT_Xiv2.tex:394`); Koda & Shapiro's footnote (`sidm1.tex:411-412`) matches neither.
