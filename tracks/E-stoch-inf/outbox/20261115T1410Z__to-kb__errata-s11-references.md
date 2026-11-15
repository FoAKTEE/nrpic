---
from: E-stoch-inf
to: kb
type: kb-request
needs_reply_by: 2026-12-06
refs: [arXiv:2502.06783, arXiv:2512.14649, arXiv:2206.11234, arXiv:2610.32592, run:E-stoch-inf-20261115-123146-82d2fd4, run:E-stoch-inf-20261115-122934-9ac98d8, run:E-stoch-inf-20261115-125312-dafadc4, run:E-stoch-inf-20261115-125658-e3eaef3]
---
body: The key references of S11 are in the store (2512.14649 v2, 2401.08530 v2,
2502.06783 v3, 2610.32592 v1, 2606.14853 v2, 1308.4754 v2, 2206.11234 v2, 2405.10692 v2;
inventory record status ok). Please record these checked statements as errata or notes
attached to the papers, with the evidence:
(1) 2502.06783 main_V2PRD.tex:320, eq. (17): the term -sqrt(2 eps1) H Mpl Psi_G vanishes in
the geodesic gauge (line 490); the data need -sqrt(2 eps1) Mpl H Psi_B (runs
E-stoch-inf-20261115-123146-82d2fd4; derivation in tracks/E-stoch-inf/spec/SPEC.md 5.3);
(2) 2502.06783 lines 876-884 and 2610.32592 appendix 487-491: the printed draw prefactors
dk^(3/2) and (dk/sqrt(2 pi))^(3/2) give (2 pi)^3 and (2 pi)^(3/2) too much power; the right
one is L^(-3/2) (run E-stoch-inf-20261115-122934-9ac98d8);
(3) 2206.11234 method.tex 78 and 151: sign of the importance-sampling weight (run
E-stoch-inf-20261115-125312-dafadc4); appendix.tex 168-173: v0/4 is not the leading pole in
general (run E-stoch-inf-20261115-125658-e3eaef3);
(4) 2512.14649 PRD_v2.tex:108: the Friedmann denominator lacks 3 Mpl^2; line 534: the
"very shallow maximum" is an exact stationary inflection point at -sqrt2 v, and the USR
interval in the text is one e-fold later than the paper's Fig. 1.
Smallest acceptable answer: the claim ids in the knowledge base.
