# RISKS of A-emd-pbh

State 2026-11-15 (lead, wave 1). Likelihood and effect: H high, M medium, L low
[JUDGEMENT]. Sources: `scope/SCOPE.md` section 8, `gauge/GAUGE.md`, `expball/DERIVATION.md`,
core's `tracks/core/JOURNAL-id.md` on branch `core/id-extrinsic`.

| # | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| 1 | Lapse fronts: every condition d_t alpha = -f(alpha) alpha K reacts to K gradients at the ball edge; core saw 1+log fronts reach the centre at t = 5.5 M (R_b = 10 M) and conformal-time fronts at speed 0.58 (bound ball, sharp edge) [VERIFIED by core's runs] | H | H: core shells lose accuracy before turnaround | central lapse against R/R_i of the core in SR-2 | geodesic slicing for the spherical tests (SR-1); K_ref lapse (request to core); taper |
| 2 | Geodesic slicing with frozen shift not well posed in Z4c [BACKGROUND, unchecked] | M | M: SR-1 fails, spherical tests need a dynamical gauge | core's T2e outcome; SR-1 constraint norms | fall back to SR-2 at dx = M/4 |
| 3 | Time step: fixed dt = cfl dx is unstable once C v > 0.618 (gauge T2); in comoving coordinates v = R_i/R grows to 17 at the first trapped sphere | H in SR-1 | M | staged cfl plan (G1 STATUS section 3) | restart with smaller cfl; conformal-time lapse keeps v ~ 1 |
| 4 | The ball holds only mu <~ 0.03-0.07 (scope T3) | certain | H for the comparison with arXiv:2609.14218 | | threshold line in the periodic box (proposal to orch) |
| 5 | Phase-1 capability missing: generator for the data of arXiv:2609.14218, a slicing that survives collapse in a box, the finder in a box | H | H: G3 waits | core and B replies | requests sent; ball work meanwhile |
| 6 | Constraint violation at particle crossings (arXiv:2609.14218 MDPBH.tex:1148-1186) | H | H: spurious black holes below the hoop line (hypothesis H2) | Hamiltonian norm outside the horizon (outcome bound of SCOPE.md section 3) | Z4c damping; two mesh spacings with damping on and off |
| 7 | Curvature at caustics does not converge (arXiv:1611.07906) | H | M: diagnostics | | outcomes from horizons and constraints, not from peak curvature |
| 8 | Particle noise halts or seeds collapse near threshold | M | H | b_min against N (A6) | lattice loads aligned with the mesh; N from scope T4b; N convergence of every bracket |
| 9 | Threshold depends on the run length (hypothesis H1) | H | H: misread threshold | t_AH of every BH run | A_c(t_end) with delta_fd stated (SCOPE.md section 3) |
| 10 | Two amplitude conventions in use (central contrast 12 mu/5, mean in r_m 0.883 mu) | M | M: factor e errors in comparisons | every table names its measure | SCOPE.md 10.1; conversion row in predict.py (open) |
| 11 | Sharp ball edges in evolution data: constraint residual does not converge; expball sharp tables carry no `breaks` line (cubic overshoot ~10 % over two rows) | M | M | | C^4 taper for all evolution data (data set 2t) |
| 12 | Outflow boundary inconsistent with the r^(-3/2) fall-off of K_ij (core) | certain | L-M | tracers near the boundary | boundary beyond the light-travel distance (half-width 64 M for SR runs) |
| 13 | Finder spin biased in an expanding region (flat rotation vectors with the full K_ij; derived, not measured) | M | M for the spin deliverable | test G-R4 | projected rotation vectors (request to core) |
| 14 | Budget: first scan ~155 card-hours (band 50-470) against 60 to the next gate | H | M | `nrpic-run budget` | G2 needs 25-50; raise asked at G2 |
| 15 | Overlap with the authors of arXiv:2609.14218 (high-density regime announced, MDPBH.tex:1218) | M | M | arXiv | H1 and the converged line first |
| 16 | Newtonian precursor waits for core/newton (decision 0010) | H | L | core/newton branch | references meanwhile (newton/), A6 as acceptance tests |
