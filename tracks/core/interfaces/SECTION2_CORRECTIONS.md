# Corrections to section 2 of the brief (lines 84-137), from the source of arXiv:2611.12831

Work package C0 of core. Proposal for the orchestrator; the brief itself is not edited.

**Source read.** `refs/arxiv_2611.12831/src/main.tex` of the main checkout (untracked,
never copied into git), 1515 lines, sha256 `5f01b119...d900cd`, identical to
`kb-data/raw/arxiv/2611.12831/v1/src/main.tex` (same checksum): version v1. Every locator
`Lnnn` below is a line of that file. Bibliography keys are resolved to arXiv numbers
from `references.bib` of the same package (entry named by its key).

**Labels.** [VERIFIED] read in the source at the locator; [BACKGROUND] standard result
not checked against an original; [JUDGEMENT] my inference; [TO VERIFY] open. Numbers
are quoted from the source only.

**Also used.** `notes/method_brief.md`, `notes/claims_brief.md`,
`paper/sections/method.tex` (this repository's reimplementation and its paper), the code
under `athenak/src/`, `docs/TESTLOG.md`, `cosmo/TESTLOG.md`.

---

## 1. Section 2.1, item by item

### 1.1 Bibliographic data (brief line 88)

| Brief | Verdict | Evidence |
|---|---|---|
| Authors Jiaxi Wu and Elias R. Most | correct [VERIFIED] | L21-25 (both TAPIR, Caltech; Most also Walter Burke Institute) |
| Title | correct [VERIFIED] | L19 |
| 23 figures | correct [VERIFIED] | 23 `figure`/`figure*` environments (`grep -c '\\begin{figure'`); 2 tables more (L1016, L1417) |
| 37 pages, submitted 2026-11-09, categories gr-qc / astro-ph.GA / astro-ph.HE / physics.plasm-ph | not in the source; cannot be checked here [TO VERIFY by kb from the abstract record] | the file date of `main.tex` is 2026-11-09 10:20, which is consistent but is not evidence |

### 1.2 Main points of the method (brief lines 90-97)

| Brief | Verdict | Correction or precision, with locators |
|---|---|---|
| 3D Einstein-Vlasov in AthenaK (2409.16053, 2409.10383) | correct [VERIFIED] | L29-31, L674 (keys `2026ApJS..283...27S` = 2409.16053, `Zhu:2024utz` = 2409.10383) |
| Z4c with moving-puncture gauge | correct [VERIFIED] | L32, L238-397. Precision: cell-centred Z4c, "up to fourth-order finite differences and fourth-order explicit Runge-Kutta" (L674); 1+log slicing with `mu_L = 2/alpha` (L372, L380); Gamma-driver written as `d_t beta^i = alpha^2 mu_S Gamma^i - eta beta^i + ...` (L376), a variant with the auxiliary field `B^i` (L383-386), and for collapse problems a damping `eta(x,t)` that follows tracked black holes, with the same profile applied to `kappa1` (L388-397) |
| Particles on geodesics; stress-energy deposited conservatively on an adaptive mesh; "conservative" means the integrated source is conserved algebraically up to floating-point summation | correct [VERIFIED] | L727-763; the identity is L759-762, the statement "hold algebraically, up to floating-point accumulation, including for clouds crossing a coarse-fine interface" is L763. Precision: the identity is for the deposit before filtering. The paper filters every deposit (L680-686) and does not say whether the filtered sources keep the identity across refinement levels. In this repository they do not: changes of 9e-4 to 7.3e-3 of the integrals after the filter once particles cross level boundaries (`docs/TESTLOG.md`, "Test-particle clusters in Schwarzschild and Kerr") |
| At refinement boundaries the shape is evaluated on the finest nearby level and the virtual fine cells are accumulated into the coarse cells | correct, imprecise [VERIFIED] | L738-750 and the caption L734. Precisely: the level `l_p` is "the finest level among the nearest eight grid points" (L738), i.e. among the cell centres that bracket the particle; the whole cloud is laid on the uniform lattice of that level, extended virtually into coarser blocks (L740); the weight of each coarse leaf is the sum of the virtual fine weights inside it (L746-750, "volume-preserving restriction", L734). The paper also notes that each refinement level divides the particles per cell by eight and proposes adaptive resampling as future work (L763) |
| Electrodynamic form of gravity; geodesic force in Lorentz form; Boris-type pusher DGREM-Boris; tests use implicit midpoint; in fixed Kerr both second order; accuracy limited by the spacetime interpolation | correct [VERIFIED] | L62, L401, L462-582, L837-840. Precision: the paper distinguishes the "GR-Boris" of plasma codes (Strang split, L433-440) from its new "DGREM-Boris" (L62); both of its pushers are implicit and solved by fixed-point iteration to a tolerance of 1e-7 in code units in production (L459) and 2e-14 in the Kerr tests (L775). "In all tests presented here, we choose the ... implicit midpoint algorithm" (L840); the Kerr tests themselves run both (L770-833). The metric is reconstructed with "cubic Hermite" weights (L586-604), which are the Catmull-Rom weights [JUDGEMENT, by comparison of L588-591 with the Catmull-Rom formula] |
| Electrodynamic analogy from 2111.05282 and 2504.15978 | correct [VERIFIED] | keys `Olivares:2021cfa` = 2111.05282 and `Boyeneni:2025tsx` = 2504.15978, cited at L62, L401, L463, L491 |

### 1.3 Tests and numbers (brief lines 99-106)

| Test | Brief | Verdict | Source, with locators |
|---|---|---|---|
| Oppenheimer-Snyder | relative error of about 1e-3 between final horizon mass and initial ADM mass | imprecise: an upper bound | "Delta M/M_ADM <~ 10^-3" for the fiducial run (L945); "within 10^-3" (L1373). Fiducial: lattice sampling, n_lat = 124, N_p = 998,592, sum m_p = 1.155 M (L917); M = 1, R_0 = 5 M (L919); domain [-128, 128]^3 M, 64^3 root cells, seven levels, finest M/32, alpha_exc = 0.1, run to 60 M (L937); mass from Fastflow and BHaHAHA (2505.15912) (L945) [VERIFIED] |
| | at fixed mesh the error falls as N grows | correct, with the paper's caveat | AMR sequence A1-A3 (N = 125,000, 10^6, 8 x 10^6; M/8 to M/32; five seeds each, Monte Carlo sampling): RMS horizon-mass error 2.061e-3, 9.362e-4, 7.347e-4 (L1484); "slower than the initial sampling-error reduction and is not assigned an N^-1/2 convergence law" (L1485). The means with their seed scatter are 0.997943 +- 0.000140, 0.999663 +- 0.000976, 0.999535 +- 0.000636 (L1426-1428) [VERIFIED] |
| | at fixed N the error does not fall monotonically with the mesh | correct [VERIFIED] | SMR sequence S1-S3 (N = 10^6; M/4, M/8, M/16): <M_irr>/M = 1.000019, 1.000655, 1.000549 (L1430-1432); "We do not find a monotonic convergence trend ... and the constant-occupancy sequence gives a flat error" (L1485). The initial density error follows eps_E ~ [N (dx/M)^3]^-1/2, i.e. the number of particles per cell (L1476) |
| Prolate collapse | followed beyond the caustic; a common apparent horizon is found; peak curvature resolution-dependent at every resolution | correct [VERIFIED] | e = 0.9, b = 10 M, N_p = 2 x 10^6, M/8 initially, M/64 finest, alpha_exc = 0.05 (L961-969); apparent horizon in the snapshot at t = 32.00 M (L950); convergence runs at finest M/32, M/64, M/128 and N from 5 x 10^5 to 8 x 10^6: "the maximum attained during the caustic stage increases with resolution", first-horizon times differ by less than 0.1 M (L975). The paper gives no horizon mass for this test (none between L954 and L985) |
| Relativistic clusters | stability and nonlinear migration | correct, incomplete [VERIFIED] | Five monoenergetic models, N = 2 x 10^6 each (Table L1016-1031): y_c = 0.900 and 0.819 hold to 300 M; 0.605 and 0.500 collapse with horizons at about 109 M and 73 M (L1027-1028, L1138); y_c = 0.283 (E_b/M_0 = -0.0398) expands, where ST85 reported collapse (L1140), a discrepancy the authors leave open. Migration of y_c = 0.500 to 2500 M: late mean central lapse 0.833530 against the predicted target 0.859266 (L1160, L1199). Reconfiguration of y_c = 0.756 with a 10 % density perturbation, N = 10^6, to 2000 M; fitted profile a_fit = 6.52 M, p = 4.17 (L1217, L1306) |
| Two overdensities in a common envelope | M = 1, envelope 0.76 M, each clump 0.12 M; 5 million particles | correct [VERIFIED] | envelope = stable monoenergetic cluster of gravitational mass 0.76 M and areal radius 30 M; clumps of 0.12 M, Gaussian width 0.70 M, at (+-3, 0, 0) M, bulk speeds -+0.133215 along y (L1335-1336); 3 x 10^6 envelope + 10^6 per clump (L1338); domain [-512, 512]^3 M, 256^3 root, eleven levels, finest M/256, alpha_exc = 0.05 (L1338) |
| | each clump forms an apparent horizon at t ~ 8.5 M | correct [VERIFIED] | t = 8.475 M and 8.525 M (L1340) |
| | common horizon at t ~ 64.16 M with mass 0.383 M | correct, but the paper is inconsistent | L1340: t_m = 64.15625 M; L1360: "roughly t = 64.175 M", M_AH = 0.38326 M, chi = 0.50355; figure caption L1345: t/M = 64. Quote 64.15625 M with locator L1340 and note the second value |
| | orbital angular momentum falls by 27.3 % between 20 M and 60 M | correct [VERIFIED] | summed orbital angular momentum inferred from the horizon momenta; the envelope (outside regions around both horizons) gains a comparable amount (L1358) |
| | remnant horizon mass 0.647 M at t = 100 M | correct [VERIFIED] | 0.64740 M, chi = 0.17132 at 100 M; J = chi M_AH^2 constant to 2 % (L1360). Individual masses 0.08802 and 0.08772 M at 10 M, 0.17421 and 0.17605 M at 60 M (L1356) |
| | late ringdown, no inspiral signal | correct [VERIFIED] | strain at R = 40 M from Psi_4, modes 2 <= l <= 8, fixed-frequency integration (L1362) |

### 1.4 Limitations (brief line 108)

| Brief | Verdict | Source |
|---|---|---|
| no direct benchmark against established methods | partly wrong | The central lapse of the dust collapse is compared with the published curve of Staley et al. (1109.0546) (caption L926, L943); the pushers with an independent adaptive integration of the Kerr geodesic (L836); the prolate collapse and the cluster fates qualitatively with Shapiro-Teukolsky, Yoo et al., East et al. (L971, L975, L994, L1140). What is absent: a run of the same problem with another Einstein-Vlasov code [VERIFIED by reading Secs. III-IV] |
| no item-by-item ablation | partly wrong | Reported comparisons: DGREM-Boris against midpoint and analytic against grid metric (L825-833); lattice against Monte Carlo sampling (L1478); lapse against horizon-based excision, "no significant difference" without numbers (L678); higher-degree kernels, "no advantage" without numbers (L686). Not reported: the filter (number of passes, on and off), the parabolic relaxation, the shift damping profile [VERIFIED] |
| two-clump test idealized (no shear in the clumps, zero net angular momentum of the envelope) | correct [VERIFIED] | L1356 |
| cause of the rapid orbital decay not uniquely identified | correct [VERIFIED for the text, JUDGEMENT for "not uniquely"] | The paper gives two mechanisms, accretion of envelope matter without angular momentum (L1356) and a drag that moves angular momentum into the envelope (L1358), and does not separate them |

### 1.5 The three readings (brief lines 110-114), all [JUDGEMENT]

1. "Convergent in particle number but not monotonic in mesh spacing, so the tests sit in
   the noise-dominated regime." Supported by L1476 (initial error set by particles per
   cell). One correction of wording: the paper does not claim convergence in N for the
   horizon mass, only an improvement over the tested range without a law (L1485), and
   the A2 and A3 means differ by less than their seed scatter (L1427-1428).
2. "Whether the full text discusses cosmologization is [TO VERIFY]." Answer [VERIFIED]:
   it does not. No periodic domain, expanding background or cosmological initial data
   appear. "Cosmic structure" occurs only in the opening list of applications (L51, keys
   `Springel:2006vs` = astro-ph/0604561 and `Angulo:2021kes` = 2112.05165); East et al.
   (key `East:2019chx` = 1908.05683) is cited once in a list of earlier Einstein-Vlasov
   studies (L53); "FLRW" occurs only as the interior of the Oppenheimer-Snyder solution
   (L867, L877); the conclusions do not mention cosmology (L1393). No collision operator:
   "collisional dynamics" at L1323 introduces black-hole formation in an environment and
   is not about particle collisions.
3. The two-overdensity run as the flat-space version of a primordial binary: unchanged.
   The paper's own framing is gravitational instability and hierarchical mergers (L1333,
   L1389; key `Wu:2026hth` = 2604.26912).

---

## 2. Section 2.2 (state of the public code, brief lines 116-132)

The upstream repository is outside this package (nobody outside is contacted; the weekly
check belongs to kb). What can be stated from this repository [VERIFIED in the files
named]:

- The coupling exists in this repository's AthenaK (decision 0002): the particle module
  includes `z4c/z4c.hpp`, `z4c/tmunu.hpp`, `coordinates/adm.hpp`
  (`athenak/src/particles/nrpic.cpp` lines 37-39) and deposits into `Tmunu::u_tmunu`
  (lines 654-998); the problem generators `nrpic_geodesic`, `nrpic_cf`, `nrpic_cosmo`
  are registered in `athenak/src/pgen/pgen.cpp` lines 973-977.
- Pusher enumeration here: drift, leap_frog, lagrangian_tracer, lagrangian_mc,
  nrpic_midpoint, nrpic_boris (`particles.hpp` lines 24-25); particle types cosmic_ray
  and nrpic (line 28). The input accepts `pusher = drift`, and for `particle_type = nrpic`
  `midpoint` or `boris` (`particles.cpp` lines 63-75); the other enumerated pushers are
  not selectable from the input.
- Periodic boundaries are used by particles and clouds (`nrpic.cpp` lines 172-181).
- The "not public" conclusion of brief line 132 concerns upstream and is not changed by
  this note; for this program the risk is retired by decision 0002.

---

## 3. Answers to the [TO VERIFY] list (brief line 134)

### 3.1 Order of the deposition shape function, and filtering

Paper [VERIFIED]: first-order B-spline (cloud in cell, `B_1(xi) = 1 - |xi|`, eight
receiving cell centres) "unless otherwise stated" (L641-660; "conservative first-order
deposition", L75). Higher-degree kernels "such as those used in smoothed particle
hydrodynamics codes" were implemented and gave "no advantage for the problems
considered" (L686). Filter: after deposition, a binomial filter with one-dimensional
weights (1/4, 1/2, 1/4), as a 3 x 3 x 3 tensor product, applied independently to each of
the ten sources E, S_i, S_ij (L680-685). Not stated: the number of passes in any test,
whether the filter is used in every test, how it treats MeshBlock and refinement
boundaries, and whether it conserves the integrals there.
This repository: `deposit.md` (shapes cic, tsc, pcs; `nfilter`, default 1; optional
compensation passes; the pass counts used by each test are in
`paper/sections/method.tex` line 151).

### 3.2 Z4c constraint-damping parameters

Paper [VERIFIED]: kappa1 and kappa2 appear only as symbols (L243-248, L290, L323-331,
L338); a position-dependent `kappa1(x,t) = kappa1_0 eta(x,t)/eta_0` when several black
holes form (L393-397). No numerical value is given anywhere for kappa1, kappa2, kappa1_0,
eta_0, mu_S or M_ref (searched L1-1515). An optional parabolic relaxation of the
Hamiltonian constraint, `d_t chi += (c_H/2) chi^(-1/4) H`, is used "in very challenging
situations" (L688-696); no value of c_H and no list of the tests that use it.
This repository: `cosmo_gauge.md` (options `damp_kappa1` default 0, `damp_kappa2`
default 0, `damp_kappa1_over_alpha`, `damp_kappa_gam`, `damp_ch`, `damp_ch_dx`,
`damp_ch_chipow`). Production inputs: kappa1 = 0.02, kappa2 = 0 for the isolated systems
(`problems/os/os_amr.athinput`, `problems/st/*.athinput`, `problems/jeans/jeans.athinput`);
kappa1 = 0.5 per unit of coordinate time with `damp_kappa1_over_alpha = true` for
cosmology (`problems/cosmo/daverio_field.athinput` lines 54-57).

### 3.3 How the particle initial data satisfy the constraints

Paper [VERIFIED]:
- Dust ball: time-symmetric, conformally flat slice, `K_ij = 0`, analytic conformal
  factor that solves the Hamiltonian constraint for uniform rho_0 (L893-903); particles at
  rest, `u_i = 0`, so the momentum constraint holds trivially; equal-mass Monte Carlo
  sampling with acceptance `psi^6/psi^6(0)` or a mass-weighted lattice with
  `m_p = rho_0 psi^6 h^3` (L905-917, L1442-1446).
- Prolate spheroid: the construction of Yoo et al. (1611.07906): uniform auxiliary
  density rho_N, `lap Phi_N = 4 pi rho_N`, `psi_bar = 1 - Phi_N`,
  `rho_ADM = 2 rho_N psi_bar^-5`, particles at rest with coordinate number density
  proportional to psi_bar (L967). Then `lap psi_bar = -2 pi psi_bar^5 rho_ADM` holds in
  the continuum [JUDGEMENT: one line of algebra from L967].
- Clusters: static Einstein-Vlasov equilibrium in areal coordinates mapped to isotropic
  ones, `K_ij = 0`, `beta^i = 0`, lapse of the equilibrium (L1033-1117); isotropic
  momenta, so the momentum density vanishes only in the mean; the stratified sampler is
  "intended to reduce ... momentum-constraint violations" (L1119-1129).
- Not stated: whether the constraints are solved again for the perturbed clusters (1 %
  inward velocity, L1138; 10 % density, L1217) and for the two moving clumps (L1335-1336),
  whose momentum density violates the momentum constraint of a `K_ij = 0` slice
  [JUDGEMENT].
- At the discrete level no solve is made with the deposited sources: the deposit seeds
  Hamiltonian and momentum violations that scale as N^-1/2 and are "propagated and damped
  by the Z4c evolution" (L1129, L1509-1511).
This repository: `particle_id.md`.

### 3.4 GPU performance numbers

Paper [VERIFIED]: none. No timing, throughput, scaling, memory or cost is given; the
only performance words are "performance-portable" (L31, L1367) and "executable on both
CPUs and GPUs" (L674). The machines are named in the acknowledgments only (NSF Vista,
NCSA Delta, Caltech Resnick HPC; L1398).
This repository: Z4c at 2.0e7 zone-cycles/s on one card with nghost 4 at 128^3, particle
work about 3 % at 10^4 particles (`docs/TESTLOG.md`, "Z4c throughput"; not rerun here).

### 3.5 Code-availability statement

Paper [VERIFIED]: none. No data- or code-availability section, no repository address
(searched for "available", "github", "zenodo", "repository", "public": only L34 "made
available to general-relativistic gravity" and L674 "currently available Fastflow
implementation", neither about this code). The acknowledgments state which language
models were used for the work (L1398).

### 3.6 Single time step across levels

Paper [VERIFIED]: yes. "Particles and fields share a common global time step" (caption
L75); "one particle advance per global step" (L823); order of one step: spacetime from
t^n to t^n+1 with the sources of t^n held fixed through the Runge-Kutta stages, then the
push with the geometry of both times, excision, redistribution, deposition (L676). The
Courant factor is not stated.
This repository: the same order (`athenak/src/particles/particles_tasks.cpp` lines
31-44); one global step `dt = min(cfl_number x min dx, <particles> dt, step limit)`
(`athenak/src/mesh/mesh.cpp` lines 639-649, `z4c/z4c_newdt.cpp`); details in `pusher.md`.

### 3.7 Follow-up directions in the conclusions

Paper [VERIFIED], L1393: higher-order methods (`Rosswog:2023nnl` = 2306.06226,
`Boss:2026fyj` = 2605.15260), extremal black-hole formation (`Gelles:2025gxi` =
2503.04881, `East:2025nfb` = 2511.20567; see `Kehle:2024vyt` = 2402.10190), cosmic
censorship (`Shapiro:1991zza`, no eprint in the bibliography; `East:2019bwu` =
1901.04498), and gravitational instability and collapse in general. Elsewhere in the
text: adaptive particle resampling in refined regions (L763); a comparison of the pushers
in numerical spacetimes (L840); the highly relativistic nonlinear evolution of clusters,
prompted by the y_c = 0.283 discrepancy (L1140); hierarchical mergers (L1389). Cosmology
is not among them.

---

## 4. Implementation details: what the paper states and what it leaves open

### 4.1 Stated [VERIFIED]

| Detail | Locator |
|---|---|
| Phase-space variables `(x^i, u_i)`, characteristic equations in coordinate time | L191-204, L408-417 |
| Midpoint pusher: fields at the midpoint position, interpolated at t^n and t^n+1 and averaged; inverse metric from the averaged metric | L445-456 |
| Fixed-point iteration, tolerance 1e-7 (production), 2e-14 (Kerr tests) | L459, L775 |
| Boris pusher steps, midpoint Lorentz factor `W = sqrt(1 + delta^ij u_i u_j)`, `Delta t_hat = alpha^(n+1/2) Delta t` | L548-580 |
| Hermite (Catmull-Rom) reconstruction of values and first derivatives, tensor product over 4^3 cells | L586-604 |
| Cell-centred deposit, first-order shape, `sqrt(gamma)` at the receiving cell | L617-670 |
| Binomial filter (1/4, 1/2, 1/4)^3 on the ten sources | L680-685 |
| Single-level clouds across refinement boundaries, conservation identity | L727-763 |
| Order of a step, sources fixed through the Runge-Kutta stages | L676 |
| Lapse excision `alpha(t^n, x_p^n) < alpha_exc`, marked after the push, removed before redistribution and deposit; horizon-based excision exists | L678 |
| Particles keep m_p, x_p, u_i through regrids; no splitting or merging | L729 |
| Loehner indicator on `q = alpha chi^(-7/4)`, eps = 0.01, delta = 1e-99, refine above 0.2, derefine below 0.02 | L706-725 |
| Parabolic relaxation `d_t chi += (c_H/2) chi^(-1/4) H` | L688-696 |
| Gauge: 1+log, Gamma-driver `alpha^2 mu_S Gamma^i`, optional `B^i` form, tracker-dependent eta and kappa1 | L370-397 |
| Horizon finder Fastflow; external BHaHAHA for masses; Psi_4 extraction | L674, L945, L1362 |

### 4.2 Not stated (filled in independently here, see the interface documents)

| Detail | Where this repository fixes it |
|---|---|
| Values of kappa1, kappa2, mu_S, eta, c_H, Kreiss-Oliger dissipation, Courant factor | inputs under `problems/`; `cosmo_gauge.md` |
| Finite-difference order actually used ("up to fourth", L674) | sixth order with nghost 4 on refined meshes (`paper/sections/method.tex` line 167) |
| Tetrad gauge of the Boris pusher | symmetric and Cholesky gauges; each reproduces one of the two published error sets (`docs/TESTLOG.md`, "Pusher kernels"; `pusher.md`) |
| Midpoint-time fields of the Boris pusher (the time interpolation text is commented out, L606-613) | average of the two levels and `(gamma^n+1 - gamma^n)/dt` (`pusher.md`) |
| Treatment of the reconstruction stencil near MeshBlock edges and refinement boundaries | shifted inward, same cubic extrapolated; block of the particle only (`pusher.md`) |
| Number of filter passes per test; filter at refinement boundaries | `deposit.md`; per-test choices in `paper/sections/method.tex` line 151 |
| Particle removal at the outer boundary (L729 points to a section that does not describe it) | removal when the particle leaves the mesh, cloud weight outside the mesh dropped (`deposit.md`) |
| Horizon-based excision rule | `ah_exc_factor` (`pusher.md`) |
| Non-convergence of the implicit iteration | counted, the state of the last iterate is kept (`pusher.md`) |
| Constraint handling of perturbed and moving initial data | `particle_id.md` |
| Norm of the constraint diagnostics (coordinate-volume RMS in the paper, L1497-1508) | `diagnostics.md` |

### 4.3 Differences between the paper and this repository's code [VERIFIED in both]

| Item | Paper | This repository |
|---|---|---|
| Shift driver | `alpha^2 mu_S Gamma^i` (L376) | `shift_Gamma x Gamma^i` by default; the alpha^2 form through `shift_alpha2Gamma` (`z4c_calcrhs.cpp` lines 714-724) |
| `B^i` Gamma-driver, tracker-dependent eta and kappa1 | implemented (L381-397) | not implemented (`paper/sections/method.tex` line 229) |
| Horizon-based excision | exists, rule not given (L678) | particles inside `ah_exc_factor` times the smallest coordinate radius of a found horizon (`nrpic.cpp` lines 399-424) |
| Horizon finder | Fastflow as available (L674) | Fastflow with `metric_drvts = interpolant`, because the distributed version interpolates a derivative array with unfilled ghost cells (`notes/claims_brief.md` lines 67-71) |
| Higher-degree shapes | SPH-type kernels (L686) | B-splines of degree two and three, `deposit_shape = tsc, pcs` |
| Lattice masses of the dust ball | `m_p = rho_0 psi^6 h^3` (L913-916) | the same, with an optional surface rescaling; the published rule carries 1.2 % too much mass at 10^4 particles (`docs/TESTLOG.md`, "Dust collapse: the published lattice rule at 10^4 particles carries 1.2 percent too much mass") |
| Electromagnetic forces in the pusher | written into the equations (L522-529) | not implemented |
