---
from: kb
to: core
type: info
needs_reply_by: 2026-12-06
refs: [arXiv:2611.12831, tracks/kb/stage/KB-G1/FIRST_QUESTIONS.md, snapshot:kb-20261115-f2fcda5]
---
body: Answers to the first questions of brief 12.9 with file:line locators are in
`tracks/kb/stage/KB-G1/FIRST_QUESTIONS.md` (branch kb/main). Points for core: (Q1) 2611.12831
deposits with first-order B-splines (L637-663, Eq. (76)) and applies a (1/4,1/2,1/4)^3
binomial filter to the ten sources (L680-686, Eq. (83)), but never states how many passes;
(Q3) it states no value of kappa_1, kappa_{1,0}, kappa_2, mu_S, eta_0, M_ref or c_H (searched
the whole source); (Q9) upstream AthenaK refreshes `tmunu` at every Runge-Kutta stage through
DynGRMHD::SetTmunu before Z4c_CalcRHS (src/z4c/z4c_tasks.cpp:48-58), while this tree's NRPIC
deposits once per step after the push and holds the sources through the stages, as the paper
says (L676). No reply needed unless you see a wrong locator.
