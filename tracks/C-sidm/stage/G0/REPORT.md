# C-sidm, gate G0 (scoping): report

Owner C-sidm, branch `track/C-sidm`, lead session of 2026-11-15. Sources: the brief by line
ranges (30-68, 232-238, 279-313, 380-393, 518-521, 544-547, 674-686, 747-764, 834-860,
957-1004), `coord/CHARTER.md` 9.6, decision 0010, the four helper packages
(`tracks/C-sidm/{scope,collide,gravothermal,equilibria}/`) and the lead's review
(`tracks/C-sidm/review/`, `REVIEW.md` in this directory). Artefacts and run ids:
`EVIDENCE.md`; what the gate still lacks: `OPEN.md`; the harness checklist: `CHECKLIST.md`.
Labels: [VERIFIED] read at the source (file:line) or computed in a registered run;
[BACKGROUND] standard, not re-read; [JUDGEMENT] inference or design; [TO VERIFY] open.
Code units G = c = 1, ADM mass M = 1 unless stated.

## 1. Problem statement

**Question (S3).** After gravothermal collapse has driven the core of a self-interacting
dark-matter (SIDM) halo to a relativistic velocity dispersion, how much of it ends in the
black hole, and how does the collision rate change that? The track answers it with
three-dimensional Einstein-Vlasov evolutions with a Monte Carlo collision operator, all in
this repository's AthenaK (decision 0010), starting from an equilibrium core near the
relativistic instability, because the gravothermal history itself cannot be followed by a
dynamical-time code (below).

**State of the field (each item read at the source by the lead in this session).**
- Onset of the relativistic instability of a thermal (truncated Maxwell-Boltzmann) core:
  fractional binding energy maximum 0.0352-0.0356 at Z(0) = 0.548-0.522 for
  b = kT(R)/m = 0.1-0.5; trial-function adiabatic criterion at v(0) = 0.566-0.564 c,
  Z(0) = 0.750-0.622 (arXiv:2108.11967 `main.tex:274, 280`); the trial criterion is
  sufficient, not necessary, and Shapiro-Teukolsky N-body runs collapse at eps ~ 0.035,
  Z(0) ~ 0.5 (`main.tex:283`) [VERIFIED].
- The only time-dependent relativistic treatment is a spherical Misner-Sharp fluid with
  heat conduction and P = (gamma - 1) eps rho, gamma = 5/3 (arXiv:2601.17117
  `SIDM_MS.tex:341-344`); outward heat flux expands the envelope; seed about 3e-8 of the
  halo, ~200 M_sun, at t = 580 t_0 (`SIDM_MS.tex:64-71, 476`); the authors state that a
  rigorous treatment needs the collisional Boltzmann equation and use a phenomenological
  pressure factor instead (`SIDM_MS.tex:672-676`) [VERIFIED].
- Fluid seed estimates: the short-mean-free-path mass, 1.8e-3 M_0 with baryons and
  4.2e-2 M_0 without (arXiv:2010.15132 `smbh.tex:151`); a GR instability needs a central
  1D dispersion of about 0.3 c, reached by 1e-10 to 1e-8 of the halo, about 1 M_sun for a
  1e9 M_sun halo (arXiv:2506.17641 `sidmacc.tex:74`) [VERIFIED].
- The conducting-fluid model matches Monte Carlo N-body only for Kn >= 1, with a prefactor
  five times below Chapman-Enskog (arXiv:1101.3097 `sidm1.tex:1482-1491`) [VERIFIED].
- Collisionless clusters: the binding-energy maximum signals the onset for isotropic
  polytropes and the King model (arXiv:2009.08163, King y_max = 0.334, `paper.tex:953`),
  where the collapse takes every particle (`paper.tex:1190-1193`); for core-halo families
  there is "strong evidence against" the binding-energy hypothesis and stability can change
  twice (arXiv:2105.05556 `paper.tex:88-89, 612`) [VERIFIED].

**What the track adds [JUDGEMENT].** A fully relativistic kinetic calculation with
collisions in three dimensions: no fluid closure, no hydrostatic assumption, the transition
from collisionless to collision-dominated matter controlled by one number, Kn. None of the
sources read contains one.

**Observables, in order.** (1) The collisionless instability threshold of the chosen
families (brief 390, charter G2). (2) The collapsed mass fraction M_BH/M at horizon
formation and at the end of the run against Kn, converged in particle number and collision
sub-step (G3).

**Physical Knudsen number and what the scan can mean [VERIFIED numbers, JUDGEMENT reading].**
With sigma/m = 5 cm^2/g (`SIDM_MS.tex:384`) a near-threshold core of 200 M_sun has
Kn_c = 4.5e-20 to 1.8e-19 and one of 1.9e9 M_sun 4e-13 to 2e-12 (run
C-sidm-20261115-115400-eb8b752; scope's H convention, section 2 item 2). Every phase of
the gravothermal history before the dynamical instability lasts at least 1e5 dynamical
times of the then-current core (run C-sidm-20261115-121412-d463e1a). Physical relativistic
SIDM cores are perfect fluids on the dynamical time. The code reaches Kn_c of about
0.3-100 (section 3). The scan therefore maps the bridge from the collisionless to the fluid
limit, and a statement about physical seeds must go through its Kn -> 0 end, anchored by
the exact fluid onset of the same equilibrium (section 2 item 3).

## 2. Decisions taken by the lead in this package [JUDGEMENT]

1. **S3 family.** Primary science family: the truncated Maxwell-Boltzmann core of
   arXiv:2108.11967 at b = 0.1 (core-halo, R/H_c = 21-36, the onset model that 2601.17117
   cites, `SIDM_MS.tex:476`). It is an exact Einstein-Vlasov steady state,
   f = A(e^{-E/T_inf} - e^{-E_c/T_inf}) with E the Killing energy (gravothermal,
   derivation and test, run C-sidm-20261115-120715-38ab057), so one model serves the
   collisionless and the collisional runs. Verification families: the King model of
   2009.08163 (the b = 1 member; 13 particle models ready, run
   C-sidm-20261115-120610-b4592be) and the monoenergetic family of the first paper.
   Cross-check only: the k = 1/2 polytrope. The shells of gr-qc/0601112 serve row 843 only
   (no core).
2. **Knudsen number.** Kn = lambda_c/H_c with lambda = 1/(rho0 sigma_m), rho0 the
   rest-mass density (astro-ph/0110561 `SIDMGT_Xiv2.tex:388-390`; 2601.17117
   `SIDM_MS.tex:233`), and H = (v1^2/(4 pi rho0))^{1/2} (`SIDMGT_Xiv2.tex:403-405`),
   v1^2 = (p + 2 p_T)/(3 rho0), at the centre (shells: the density peak). Conversion:
   sigma~ = (sigma/m)/M = K/Kn with K = 1/(rho0_c H_c); K = 168.9 for the King threshold
   model y0 = 0.334032 (two solvers agree to 1e-7, review run
   C-sidm-20261115-131130-3077a99, X4) and 154-206 across the 13 models; in physical units
   sigma/m = sigma~ x 1.097e-23 cm^2/g x (M/M_sun) (equilibria `CONVERSION.md` section 1,
   [BACKGROUND] constants). The helpers used two other conventions: scope's H with the
   energy density (K = 198.6 for the same model) and equilibria's transport mean free path
   l = 0.77 lambda (its Kn is 0.77 times this one); `REVIEW.md` converts both.
3. **Fluid reference.** The Kn -> 0 anchor is the exact radial-pulsation onset of the same
   equilibrium (finite elements, `gravothermal/tmb.py`): Z(0) = 0.6348 for b = 0.1 with
   F21's gamma = 1 + p/u (run C-sidm-20261115-120722-38ab057; the sign change reproduced
   at two resolutions by review X5). A collision-dominated Juttner gas has the lower
   adiabatic index Gamma_1 = 1 + 1/c_v at intermediate temperatures [BACKGROUND]; its
   onset is still to be computed (`OPEN.md`).
4. **Gates.** G1 holds the charter's two criteria (C-pre-1 tests pass on core's
   implementation; baseline reproduced) plus the generic G1 items. The collisionless
   threshold scans run in wave 2 as G2 work with the existing executable (scouting until
   core-v0.1 is tagged, charter "What differs" item 1).

## 3. Parameter ranges

| Quantity | Range | Source / reason |
|---|---|---|
| F21 b = 0.1 models (primary) | Z(0) = 0.40-0.80, w0 = 2.5-4.2; eps maximum Z(0) = 0.5404, fluid onset (gamma = 1 + p/u) 0.6348, trial criterion 0.7500; R/M = 20-26, r_core/M = 1.5-2.1, central lapse 0.56-0.71 | runs C-sidm-20261115-120722-38ab057, -121748-4e8d6b5; review X2 (two solvers agree to 2e-8) |
| F21 b = 0.2-0.5 (robustness) | Z(0) = 0.50-0.70 | same runs |
| King b = 1 (verification) | y0 = 0.314-0.354 (Z_c 0.479-0.545), threshold y0 = 0.334032; R/M = 13.3-14.0 | runs -120610-b4592be, -121626-e99907d; review X3 (two solvers agree to 3e-8) |
| Monoenergetic (verification) | y_c = 0.64-0.74 (z_c 0.355-0.526), threshold y_c = 0.67961 | run -115344-eb8b752 (reproduced bit for bit by the review rerun) |
| Kn_c (track definition) | infinity, 100, 10, 3, 1, 0.3; 0.1 only if N allows | rows below |
| Macroparticles N | 1e4 scouting; 1e5, 1e6 convergence; Kn_c <= 0.3 needs N >= 1.7e3 Kn^-3 (dx <= lambda, 20 per cell) to 2.3e4 Kn^-3 (dx <= lambda/3, 10 per cell) for the King threshold model | collide `SPEC.md` 4.6 with K above [JUDGEMENT] |
| Mesh | dx over the core M/4 and M/8 (M/2 lower anchor), outer boundary 512 M and 1024 M; collision cell f = 1-4 mesh cells | scope `SCOPE.md` 2, 8; collide `SPEC.md` 4.1 |
| Run length | 300-1000 M (2105.05556 calls a model stable without collapse within 1000 M, `paper.tex:559` as read by scope) | scope `SCOPE.md` 3.4 |
| Collision parameters | coll_pmax 0.1 and 0.05; sub-cycling on | 1101.3097 `sidm1.tex:667-673` [VERIFIED] |

## 4. Exit criteria

- **G0** (this package): the items of charter 9.2; missing items in `OPEN.md`.
- **G1**: (a) the tests T0-T5 and T9-T11 of `collide/TESTS.md` pass on core's operator on
  processors, with the pass criteria fixed there before any run; T6-T8 (card) pass or move
  to G2 with the orchestrator's consent; (b) the spherical baseline reproduced (met,
  `../G1/STATUS.md`); (c) the interface proposals submitted (collisions, random-number
  stream 2, perturbation recipe, static curved metric); (d) the analysis pipelines
  validated: box analysis (met on synthetic data and on the collisionless run T6-0) and the
  growth-rate extraction of the threshold runs (to be validated on the first paper's
  monoenergetic outputs).
- **G2**: the collisionless threshold of the monoenergetic, King b = 1 and F21 b = 0.1
  families with three-way convergence (N 1e4/1e5/1e6; dx M/4 and M/8; outer boundary 512 M
  and 1024 M), agreeing with the binding-energy maximum within the convergence error
  (target 0.01 in y, 0.02 in Z(0)) or with a documented departure of the kind 2105.05556
  reports; T12 passes; in curved spacetime the collision step conserves sum M u_i and
  sum M W of the cell metric to 1e-14 sqrt(n_coll + 1) relative per step, and the run's
  energy drift equals the collisionless drift within its scatter.
- **G3**: M_BH/M against Kn_c for at least one F21 b = 0.1 model on each side of the
  collisionless threshold, Kn_c from infinity to 0.3, two particle numbers and two
  collision sub-steps; the Kn -> 0 end compared with the fluid onset (decision 3).
- **Stop or re-scope**: if Kn_c <= 0.3 is out of reach on one card, the claim narrows to
  the transitional regime Kn_c >= 1 and the fluid end comes from the fluid onset only.

## 5. Test plan against the rows of brief section 10 held by C-sidm

| Row (brief line) | Test | Reference solution (path, run) | Acceptance | Status |
|---|---|---|---|---|
| Spherically symmetric Einstein-Vlasov steady states and their stability threshold (843; CORE, C) | (i) stable models hold over >= 10 core periods; (ii) growth rate of the radial mode against y_c, y0, Z(0), both perturbation signs, three-way convergence | `python/nrpic/st_cluster.py` (run -115344); `equilibria/evstatic.py` (runs -121626; 13 models -120610); `gravothermal/tmb.py` and `scope/scripts/king_sequence.py` (runs -120722, -115348; agree to 2e-8, review X2) | threshold within the convergence error of the binding-energy maximum, or a documented departure | references done and cross-checked; runs in wave 2 (card); perturbation recipe requested from core |
| Spherically symmetric critical collapse (844; C optional) | A f_s family of a King steady state, bisection in A | gr-qc/0601112 section 5 (scope `SCOPE.md` 6) | A_c = 1 for an unstable steady state within the bisection error [JUDGEMENT] | not before G2; its references not read (`OPEN.md`) |
| Collisional relaxation in a Minkowski box (852; C) | T0-T12 of `collide/TESTS.md`: kernel vectors, replay, conservation, rate, relaxation to Maxwell-Juttner, initial two-temperature rate, entropy, conduction at both mean-free-path ends, convergence, unequal masses, reproducibility, Lorentz covariance, curved metric | `collide/REFERENCES/` (62 tests, rerun passed); the closed-form rate checked by an independent 3D quadrature to 5e-7 (review X1); T6 at sigma = 0 with AthenaK reproduced bit for bit (review rerun) | criteria fixed in `TESTS.md` before any collisional run | references done; collisional runs wait for core's operator (uncommitted draft in `wt/core-coll` at 13:11Z) |
| Reproducible random numbers (853; C, E) | T10 of `TESTS.md`: 1, 8, 64 MeshBlocks, 1 and 4 ranks, restart: bit-identical states (analytic metric) | core's `tracks/core/interfaces/rng.md` (branch `core/rng`); keys K1-K3 of `collide/RNG_REQUIREMENTS.md`, adopted in core's draft collision interface | bit-identical with the analytic metric; statistical only with the mesh metric (core `rng.md` section 5: states differ to rounding between divisions) | requirements submitted; the test waits for the operator |

Rows used, not held: geodesics on a fixed background and Oppenheimer-Snyder collapse (CORE;
`paper/main.pdf`).

## 6. Key references verified at the source

Read by the lead in `kb-data/raw/arxiv/<id>/<version>/src/` in this session, except the
row marked "helper" (read by the scope helper, locator given there).

| Statement | Locator |
|---|---|
| eps_max = 0.0352 at v(0) = 0.506 c, Z(0) = 0.548 (b = 0.1); 0.0352-0.0356 at Z(0) = 0.548-0.522 for b = 0.1-0.5 | 2108.11967 `main.tex:280` |
| <gamma> = gamma_cr = 1.62 at v(0) = 0.566 c, Z(0) = 0.750 (b = 0.1); 0.566-0.564 c, Z(0) = 0.750-0.622 (b = 0.1-0.5) | 2108.11967 `main.tex:274` |
| ST85 N-body collapse at eps ~ 0.035, Z(0) ~ 0.5; the trial criterion is sufficient, not necessary | 2108.11967 `main.tex:283` |
| Chandrasekhar's pulsation equation; trial xi = r e^Phi; <gamma> and gamma_cr | 2108.11967 `main.tex:202-219` |
| Table 1, b = 0.1, rows w0 = 0.6, 1.9, 3.2, 4.0515 (transcribed; both solvers within 8e-5, review X2) | 2108.11967 `main.tex:492, 495, 498, 501` |
| Printed typos: C at w0 = 0.3 is not M/R; p(0) at w0 = 1.1 is off by ten | 2108.11967 `main.tex:491, 493` |
| Fiducial halo, sigma = 5 cm^2/g, t_0 = 0.26 Gyr | 2601.17117 `SIDM_MS.tex:384` |
| P = (gamma - 1) eps rho, gamma = 5/3 stated for the non-relativistic case | 2601.17117 `SIDM_MS.tex:341-344` |
| lambda = 1/(rho sigma), H = (v^2/(4 pi rho))^{1/2}, a = sqrt(16/pi), b = 25 sqrt(pi)/32, kappa^-1 = kappa_SMFP^-1 + kappa_LMFP^-1, C = 0.75 | 2601.17117 `SIDM_MS.tex:233` |
| Onset when the dispersion approaches c (citing 2108.11967); horizon at 580 t_0, m ~ 3e-8 M, ~200 M_sun | 2601.17117 `SIDM_MS.tex:476`, abstract `:64-71` |
| A rigorous treatment needs the collisional Boltzmann equation (Gurian:2025zpc); pressure factor f_P | 2601.17117 `SIDM_MS.tex:672-676` |
| P-bar < 0.1 per step; neighbour distance r_k <~ lambda | 1101.3097 `sidm1.tex:667-673, 680-692` |
| b = 25 sqrt(pi)/32 ~ 1.38; footnote: BSI's 1.002 "should be 25 pi/32" | 1101.3097 `sidm1.tex:408-412` |
| N-body agrees with the conducting fluid for Kn >= 1 with b = 0.25, five times below Chapman-Enskog | 1101.3097 `sidm1.tex:1482-1491` |
| a = sqrt(16/pi) for hard spheres | astro-ph/0110561 `SIDMGT_Xiv2.tex:309-323` |
| lambda = 1/(rho sigma); l = lambda/sqrt 2; b ~ 25 pi/(32 sqrt 6) ~ 1.002; H; t_d = H/v | astro-ph/0110561 `SIDMGT_Xiv2.tex:388-409` |
| kappa_smfp ~ 2.1 nu k_B/sigma; Kn = lambda/H, lambda = m/(rho sigma) | 2010.15132 `smbh.tex:116` |
| Seed = SMFP mass, 1.8e-3 M_0 (baryons), 4.2e-2 M_0 (SIDM only) | 2010.15132 `smbh.tex:151` |
| GR instability at a 1D central dispersion ~0.3 c; 1e-10 to 1e-8 of the halo; ~1 M_sun for 1e9 M_sun | 2506.17641 `sidmacc.tex:74` |
| King y_max = 0.334, y_zero = 0.784; polytropes 0.298/0.693, 0.267/0.583, 0.265/0.588 | 2009.08163 `paper.tex:953-956` |
| "no particles remain unaffected by the collapse" | 2009.08163 `paper.tex:1190-1193` |
| Strong evidence against the binding-energy hypothesis; stable up to the first maximum; multiple stability changes | 2105.05556 `paper.tex:88-89` |
| i = 270: stable for z_c <= 0.492, again for 0.712 <= z_c <= 0.964 | 2105.05556 `paper.tex:612` |
| Z_c printed as 1/sqrt(alpha(0)) - 1 (the tables follow 1/alpha(0) - 1, run C-sidm-20261115-121626-e99907d) | gr-qc/0601112 `ssevnum7.tex:694` |
| The continuum solver the brief names for collisions is collisionless ("in the absence of collisions or sources") | 2602.17487 `results.tex:18` |
| Wu-Most models y_c, z_c, R/M, M_0/M; collapse at 109 M and 73 M | 2611.12831 `main.tex:1024-1028` |
| Seed fraction 1e-8 to 1e-6 of the halo (helper) | astro-ph/0111176 `:289-291` per scope `SCOPE.md` 1 |

## 7. Risks

Full list with likelihood, effect, watch and response: `tracks/C-sidm/RISKS.md`. The five
that decide the plan: (1) stiffness and particle number at small Kn (N ~ Kn^-3); (2) the
collisionless threshold of core-halo families may not sit at the binding-energy maximum
(2105.05556); (3) the collision operator is not in the code yet (core's draft is
uncommitted), so G1 is blocked on core; (4) the physical Kn (~1e-19) is out of reach and
every physical statement goes through the Kn -> 0 anchor; (5) the card budget: G2 and G3
exceed the 20 GPU-hour allotment.

## 8. Compute estimate on `anta`

Unit costs measured from the first paper's AthenaK logs (one A100, N = 1e4; run
C-sidm-20261115-115400-eb8b752, reproduced by the review rerun): 1.67 s per M (static
dx = M/2), 3.28-3.71 s per M (static dx = M/4), 14.2-17.5 s per M (adaptive to M/16,
collapse); particle work about 4.1e-8 s per particle and cycle. The cost of a collision is
not measured (the operator does not exist yet). Estimates [JUDGEMENT on counts and
multipliers]:

| Block | Runs | Card-hours |
|---|---|---|
| Wave 2, collisionless monoenergetic scan, N = 1e4 | 8 models x 2 signs x 400 M x 3.71 s/M | 6.6 |
| Wave 2, collisionless King b = 1 scouting, N = 1e4 | 5 models x 1000 M x ~4 s/M | 5.6 |
| Wave 2, first collisional cluster runs (`../G1/STATUS.md` section 4) | 6 runs x 300 M x 4-8 s/M | 2-4 |
| Wave 2, Minkowski-box tests T6-T8 on a card | 1e6-1e7 particles, 1e3-1e4 collision times | 2-4 (after T2 measures the cost per pair) |
| G2 three-way convergence (two families) | scope `SCOPE.md` 8 | about 45 |
| G3 mass fraction against Kn | 7 Kn x 2 N x 2 sub-steps, 1000 M, ~20 s/M | 80-160 |
| Processors | references, analysis, box tests T0-T5, T9-T11 | seconds to minutes each, <= 16 cores |

Wave 2 fits the 20 GPU-hours of decision 0006 (16-20); G2 and G3 do not: a raise is
requested (outbox).

## 9. Stage timeline [JUDGEMENT]

| Wave | What | Gate evidence |
|---|---|---|
| 1 (done) | references, specification, tests, initial data, baseline | G0 package; G1 items (b), (c) |
| 2 | core's operator checked (T0-T5, T9-T11 on processors; T6-T8 card); collisionless scans (monoenergetic, King b = 1); F21 b = 0.1 particle models; first collisional cluster runs | G1 package; G2 started |
| 3 | three-way convergence of the thresholds; T12 and curved-spacetime budgets | G2 package |
| 4-5 | Kn scan of M_BH/M with convergence; fluid-limit anchor | G3 package |
