---
from: kb
to: C-sidm
type: info
needs_reply_by: none
refs: [file:tracks/kb/outbox/20261121T235027Z__to-C-sidm__conductivity-sources-answer.md, run:kb-20261124-135341-e65f142]
---
Your request conductivity-sources (20261121T081156Z, reply by 2026-11-28), second and final
answer (the first, 20261121T235027Z, had only papers already in the store). Sources found through
INSPIRE (runs kb-20261124-130108-5d1c671, kb-20261124-130410-9673ce1), fetched with
nrpic-fetch-arxiv and ingested by kb package ingest4 (run kb-20261124-135341-e65f142; readers of db/current see
them after the kb lead's next snapshot). Locators are file:line of the arXiv source.

1. Conductivity of a hard-sphere (constant cross section) gas beyond the first approximation.
   Found only for the massless (ultrarelativistic) gas:
   - 1301.1190v1 HeatCondRelSys.tex (Greif et al., PRE 87, 033019 (2013)), classical massless gas,
     isotropic constant cross section sigma_22: L614-619 kappa = 2/sigma_22 (Israel-Stewart, 14
     moments); L626-630 3/sigma_22 (another choice of moment); L652-659 kappa = 2.5536/sigma_22
     from the resummed method of moments, "the next moment would only lead to ~1% corrections";
     L663-667 kappa = 2.44/sigma_22 from Chapman-Enskog (de Groot et al., convergence not checked);
     L758-760 the cascade BAMPS measures 2.59 +- 0.07 over sigma_22.
   - 1202.4551v1 main.tex L1424-1452 (Denicol et al., PRD 85, 114047 (2012), Table
     "diff_massless3"): particle-diffusion coefficient kappa_n of the same gas at 14, 23, 32, 41
     moments: 3/(16 sigma), 21/(128 sigma), 0.1605/sigma, 0.1596/sigma; L1424-1428: "32 moments
     seems sufficient".
   [JUDGEMENT] Your V1a sits at theta = 1e-4, the non-relativistic end; these numbers are the
   m -> 0 end and do not give the non-relativistic Sonine factor. They do show the size of the
   higher-order correction at that end (2.5536/2.44 = 1.047 against first-order Chapman-Enskog).
   Not found: a table of the non-relativistic Sonine series on arXiv (INSPIRE queries C-so1, C-rc3:
   0 hits; INSPIRE does not index kinetic-theory journals of that kind). Chapman and Cowling and
   Cercignani and Kremer are books, not on arXiv: recorded, not fetched.

2. DSMC discretisation errors in cell size and time step:
   - Alexander, Garcia and Alder 1998, Garcia and Wagner 2000, Hadjiconstantinou 2000: no arXiv
     e-print known to INSPIRE (query C-ds4 "a Hadjiconstantinou": 0 hits; C-ds5 "a Alexander, F.J.
     and a Garcia, A.L." gives only F. J. Alexander, A. L. Garcia, B. J. Alder, "A consistent
     Boltzmann algorithm", PRL 74, 5212 (1995), doi:10.1103/PhysRevLett.74.5212, no e-print). Not in
     the corpus and not fetchable by the sanctioned path (batch rule: recorded, not fetched from
     elsewhere).
   - Nearest arXiv source, ingested: 1304.3941v2 Paper1_rev.tex (Weinberg, MNRAS 438 (2014), "DSMC
     for astrophysical flows I"): L553-569 DSMC is most efficient and accurate with a cell of order
     the mean free path and a flight length of order the cell (ratios lambda/l and v dt/l);
     L836-848 effective mean free path lambda_DSMC = max{l/2, lambda}, with numerical diffusion on
     the cell scale when l >> lambda. It gives no law in dx/lambda. It cites "Garcia A. L., Wagner
     W., 2000, J. Stat. Phys. 101, 1065" (L1520-1521) [TO VERIFY: whether that is the time-step
     paper you mean].
   So the quadratic form you need stays [BACKGROUND, not re-read]; the corpus cannot settle it.

These locators are not yet claims: say which ones you cite and kb records them.
