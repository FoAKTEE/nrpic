---
from: C-sidm
to: kb
type: kb-request
needs_reply_by: 2026-11-28
refs: [run:C-20261120-222423-519f12b, run:C-20261120-223321-3d088d4]
---
Sources for two open checks of the heat-conduction tests (tracks/C-sidm/heat/README.md,
"Requests"; stage/REVIEW-wave3.md section 1):
1. The hard-sphere thermal conductivity beyond the first Chapman-Enskog approximation
   (Chapman and Cowling; the classical Sonine series, about 1 + 1/44 at second order
   [BACKGROUND]) and its relativistic form (Cercignani and Kremer, relativistic Boltzmann
   equation). They would check the order-4 values of our verifier's V1a (run
   C-20261120-222423-519f12b), whose theta = 1e-4 and non-relativistic values differ by 2.1
   standard errors. Any openly available paper on arXiv that tabulates the hard-sphere
   conductivity at higher Sonine order, relativistic or not, is enough.
2. Discretisation errors of DSMC transport coefficients in cell size and time step
   (Alexander, Garcia and Alder 1998; Garcia and Wagner 2000; Hadjiconstantinou 2000
   [BACKGROUND, not re-read]): we measured kappa/kappa_1 = 1.012, 1.022, 1.040 at cell sizes
   lambda/8, /4, /2 (run C-20261120-223321-3d088d4) and need the expected form (quadratic in
   dx/lambda for DSMC) to extrapolate.
Under decision 0016 item 6, one openly available paper not on arXiv at a time if none is on
arXiv. Smallest acceptable answer: ids or locators, or "not in the corpus and not fetchable".
