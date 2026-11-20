# KB-G1: answers to the first questions of brief 12.9 (lines 1418-1428)

Owner kb, lead session of 2026-11-15. Database snapshot `kb-data/db/kb-20261115-f2fcda5.sqlite`
(`db/current`, run kb-20261115-141500-b2e57be). All answers are our own wording; no passage
is copied.

**Locators.** `2611.12831v1 L641-648` means lines 641 to 648 of
`kb-data/raw/arxiv/2611.12831/v1/src/main.tex` (sha256 recorded in
`kb-data/manifests/SHA256SUMS`). Other papers: `2609.14218v1` = `.../2609.14218/v1/src/MDPBH.tex`,
`2512.14649v2` = `.../2512.14649/v2/src/PRD_v2.tex`, `2404.16270v1` =
`.../2404.16270/v1/src/article.tex`. Equation, section, table and figure numbers are those
the knowledge base computed (checked against an independent count for 2611.12831, journal
check L5); read them with `python3 -I kb/bin/kb show <id> --eq <label>` or
`--section <n>`. Code locators are `repo:path:line` at the indexed commit: upstream
`IAS-Astrophysics/athenak` at c5a0d7f9155a, this repository (`local/nrpic`) at main a1c2237.

**Labels.** [VERIFIED] = read in the full text at the locator during this session.
"Not stated" answers are [VERIFIED] by reading the named sections and searching the whole
source for the listed terms (search commands in `tracks/kb/JOURNAL.md`, lead entry).
[JUDGEMENT] = our inference. [TO VERIFY] = open.

---

## 1. Shape-function order of the deposition in arXiv:2611.12831; filtering?

- First order. The default deposition kernel is the degree-one B-spline (cloud in cell):
  B1(xi) = 1 - |xi| for |xi| < 1, applied as a tensor product over at most eight cell
  centres, with partition of unity. Locator: Sec. 2.3, `2611.12831v1 L637-663`, Eq. (76)
  `eq:first-order-shape`; the B-spline family and the order convention at L625-637
  (Eqs. (74)-(75)). "Unless otherwise stated" (L641). [VERIFIED]
- Sources are deposited with sqrt(gamma) of the receiving cell centre (L664-670). Under
  AMR the whole cloud is evaluated on one level, the finest level among its eight nearest
  points, with a virtual fine lattice that extends into coarser blocks and is summed into the
  leaf cells; the weights then sum to one on the combined mesh (Sec. 2.5.2, L738-762,
  Eqs. (91) `eq:weight-unity`, (92) `eq:tmunu-source-cell`). [VERIFIED]
- Higher-degree (SPH-type) kernels were implemented and gave no advantage for the problems
  of the paper (L686). [VERIFIED]
- Filtering: yes. After deposition a binomial filter with weights (1/4, 1/2, 1/4) per
  direction (tensor product 3x3x3, centre weight 1/8) is applied independently to each of the
  ten ADM source components E, S_i, S_ij (Sec. 2.4.1, L680-686, Eq. (83)). [VERIFIED]
- Not stated: the number of filter passes used in the runs (the text defines "one filter
  pass"; the word "passes" does not occur in the source). [VERIFIED by search] Needed by
  core to match the paper. [TO VERIFY; only the authors can answer]
- Related but not a filter: an optional parabolic relaxation of the Hamiltonian constraint in
  the chi equation with coefficient c_H >= 0 (L688-696, Eq. (84)); no value of c_H is given.
  [VERIFIED]
- In this repository's code the corresponding options are `<particles>` deposit order,
  `nfilter`, `filter_compensate` (`kb/reports/code_params.md`; links M11, M16 of
  `kb/curated/paper_code_links.tsv`, status claimed).

## 2. How do the particle initial data of 2611.12831 satisfy the constraints?

- Every test starts on a conformally flat, time-symmetric slice: gamma_ij = psi^4 delta_ij,
  K_ij = 0, lapse one, shift zero; with K_ij = 0 and particles at rest the momentum
  constraint holds identically in the continuum. Oppenheimer-Snyder: L888-905 (interior
  conformal factor solves the Hamiltonian constraint for the uniform density and matches the
  exterior Schwarzschild data, L903; dust at rest u_i = 0, L905). Prolate spheroid: L965-967
  (time symmetric, conformally flat; following Yoo et al., a flat-space Poisson solve for an
  auxiliary Newtonian density gives psi_bar = 1 - Phi_N and the corresponding ADM density).
  Relativistic clusters: Shapiro-Teukolsky monoenergetic equilibria solved in areal
  coordinates and transformed to isotropic ones, joined to isotropic exterior Schwarzschild
  (Sec. 3.4.1, L1033-1117). Relativistic Plummer model (Sec. 3.4.3): with zero shift and
  K_ij = 0 the Hamiltonian constraint becomes a flat Laplace-type equation for psi, solved
  in closed form (L1261-1275, Eq. (128) `eq:plummer-hamiltonian`). [VERIFIED]
- The particles are then drawn from the continuum distribution (OS: Monte Carlo with
  acceptance proportional to psi^6, or a mass-weighted lattice, L905-917 and App. A L1442;
  clusters: a stratified sampler of radius, angles and isotropic momentum directions,
  L1119-1129). No constraint solve uses the deposited particle sources: the discrete sources
  violate the constraints at the sampling-noise level, and the paper reports Hamiltonian and
  momentum-constraint fluctuations scaling about as N^(-1/2), "propagated and damped" by
  Z4c (L1129; App. A L1476; App. B L1509). [VERIFIED]
- For the cluster models with moving particles, the continuum momentum density vanishes by
  isotropy, so K_ij = 0 is consistent with the momentum constraint. [JUDGEMENT]
- Not read closely: the two moving clumps of Sec. 4 (bulk velocities +-0.133215 in L1336)
  are set inside the stable cluster; how the momentum constraint is treated for them is not
  stated in Sec. 4. [TO VERIFY]

## 3. Values of the Z4c constraint-damping and gauge parameters in 2611.12831

- Formulation: Z4c with damping parameters kappa_1, kappa_2 (L238-248, Eq. (17)
  `eq:z4-einstein`; L338). Gauge: Bona-Masso slicing with mu_L = 2/alpha, i.e. 1+log
  (L371-380, Eq. (30) `eq:z4c-lapse`); Gamma-driver shift with mu_S, eta (Eq. (31)
  `eq:z4c-shift`) and a B^i variant with the factor 3/4 (L382-386). For collapse problems a
  position-dependent eta(x,t) built from tracked black-hole masses and positions, and
  kappa_1(x,t) = kappa_{1,0} eta/eta_0 (L388-397, Eqs. (33)-(34)). [VERIFIED]
- Not stated: numerical values of kappa_1, kappa_{1,0}, kappa_2, mu_S, eta_0, M_ref and c_H.
  Searched the whole source for kappa, eta_0, mu_S, c_H (all occurrences are the defining
  lines above) and read Secs. 3-4 and the appendices. [VERIFIED by search] The paper does
  state: the 1+log choice mu_L = 2/alpha (L380), the factor 3/4 (L384), the refinement
  thresholds 0.2 / 0.02 with epsilon = 0.01 (L722-725), the excision lapse alpha_exc = 0.1
  for the cluster suite (L1117) and 0.05 in Sec. 4 (L1338). [VERIFIED]
- Code defaults for comparison, not the paper's values: upstream AthenaK reads
  `<z4c> damp_kappa1` and `damp_kappa2` with default 0.0, `lapse_oplog` 2.0, `shift_eta` 2.0,
  `shift_Gamma` 1.0 (IAS-Astrophysics/athenak:src/z4c/z4c.cpp:131-148); this tree adds
  `damp_ch`, `damp_ch_dx`, `damp_kappa1_over_alpha`, `damp_kappa_gam` (local/nrpic:
  athenak/src/z4c/z4c.cpp:131-157). [VERIFIED, params index]

## 4. Code-availability statement? Follow-up directions? Cosmology, collisions, tidal?

- No code- or data-availability statement: no "available", repository address or "upon
  request" in that sense occurs in the source; the acknowledgements name the computers only
  (L1395-1399). [VERIFIED by search] The knowledge base's scan of repository addresses finds
  none in this paper (`kb/reports/code_links_explicit.tsv`).
- Follow-up directions listed in the conclusions (L1393): higher-order methods, extremal
  black-hole formation, cosmic censorship, and gravitational instability and collapse in
  general. The text also asks for adaptive particle resampling under AMR (L763). [VERIFIED]
- Cosmology: not mentioned. "FLRW" occurs only as the interior of the Oppenheimer-Snyder
  solution (L867, L877); "cosmolog" does not occur. [VERIFIED by search]
- Collisions: the matter is collisionless throughout; collisional dynamics is named once as
  context for black-hole formation in environments (L1323) and neutron stars as the fluid
  ("collisional") analogue of clusters (L1008); no collision operator. [VERIFIED]
- Tidal interactions: the word does not occur. [VERIFIED by search]

## 5. Performance numbers reported by 2611.12831

- None: no wall-clock times, node or GPU hours, particle updates per second, memory or
  scaling results. Searched for GPU, A100, H100, hours, node, rank, MPI, seconds, zone,
  timing, memory, efficien, throughput, speed, cost, scal. [VERIFIED by search]
- What is stated: Kokkos makes the code run on CPUs and GPUs (L674); the runs used NSF
  Vista, NCSA Delta and Caltech's Resnick HPC centre (L1398); problem sizes, e.g. Sec. 4 with
  5x10^6 particles, a 256^3 root grid, 32^3-cell blocks and eleven refinement levels
  (L1338), the cluster suite with N = 2x10^6 and a 128^3 root mesh (Table caption L1017).
  [VERIFIED]

## 6. Initial data, gauge and black-hole-formation threshold in arXiv:2609.14218

- Initial data (Sec. 3, `2609.14218v1 L492-549`): long-wavelength growing-mode solution
  of the gradient expansion for a given curvature perturbation zeta, written through
  Psi = exp(zeta/2): K = -3H (a constant-mean-curvature slice), psi, the conformal metric and
  A_ij to second order in 1/(aH), lapse 1 - q/(3 (aH)^2), zero shift (Eqs. (3.4)-(3.10));
  the matter E and J follow from the constraints, then rho and V from E = Gamma^2 rho.
  H_i = 5k = 50/L, a_i = 1 (L549). Profile (Sec. 5, L837-841, Eq. (5.1)): Gaussian
  ln Psi = (mu/2) exp(-k^2 r^2/6) [1 + (k^2/6)(p(2X^2 - Y^2 - Z^2) + 3e(Y^2 - Z^2))] with
  amplitude mu, ellipticity e, prolateness p. Particles (Sec. 6.2, L1063-1075, Eq. (6.10)):
  a regular lattice filling the box, the inhomogeneity carried by particle masses
  m_p = E sqrt(gamma) dx dy dz / Gamma_p. [VERIFIED]
- Gauge (Sec. 2.2, L398-469): a modified 1+log slicing (d_t - beta.d) alpha =
  -2 alpha (K + 3H) + (3/2) alpha H_k exp(-C^2 alpha_b^2 / a_k^2), with C = 5 fixed by trial
  and alpha_b the lapse at the box corner, which starts like an e-folding time and approaches
  cosmic time before horizon entry (Eq. (2.20), L452-461); a hyperbolic Gamma driver with
  the factor 3/4 and damping 3H (Eq. (2.22), L463-469); scaled non-Cartesian coordinates with
  eta = 10 (L473-487). BSSN, not Z4c (Sec. 2.1). [VERIFIED]
- Threshold: defined operationally by apparent-horizon formation. Analytic reference: the
  hoop-conjecture criterion h < 1 at horizon entry with the Zel'dovich approximation
  (Sec. 5.1, L848-910). Dust fluid: horizons form above some amplitude, smaller ones crash
  (shell crossing or focusing) before a horizon is found; the true threshold lies below the
  sufficient condition (L828-830, Fig. 6 `fig:thre_p0`, L974-994). Particles (Sec. 6.3,
  e = 0.2, N = 80 per dimension, L1084-1102): a horizon forms for mu >= 0.05, none for
  mu <= 0.045, so the threshold is near mu ~ 0.045 if the particle runs are accepted
  (L1145), below the analytic estimate; the late evolution violates the Hamiltonian
  constraint after particle crossing (L1203-1205). [VERIFIED]

## 7. Parameters and acceptance quantities of the two test cases of arXiv:2512.14649

- Common set-up (Sec. 3.1-3.3, `2512.14649v2 L476-543`): GRTeclyn (AMReX) BSSN with RK4,
  AMR and constraint damping off, geodesic slicing alpha = 1, beta^i = 0, periodic box
  (L480-483); N = 256 cells per dimension, a* = 1, units with M_Pl = 100, coarse-graining
  sigma = 1 (L519); window W_k(t) = (1 + tanh[s log(k_sigma/k)])/2 with s = 5 (L503-506,
  Eq. (33) `eq:ourWindow`); UV cut k_max = N k_sigma*/4, sixth-order gradient stencils
  (L512); stochastic backreaction on (L520). [VERIFIED]
- Case 1, quadratic slow roll (Table 1 `tab:scenarios`, L405-420): V = m^2 phi^2/2 with
  epsilon_1 = 0.01, epsilon_2 = -0.02, H_0 = 10^-5 M_Pl (m and phi_0 derived); about 5 e-folds
  from Bunch-Davies start to the NR start and about 8 e-folds of NR evolution. [VERIFIED]
- Case 2, ultra-slow roll on a Higgs-inflection potential (same table): Lambda = 1.86x10^-6,
  v = 0.198 M_Pl, phi_0 = -1.2 M_Pl (epsilon_1 and H_0 derived); about 3 + 10 e-folds; USR
  with epsilon_1 ~ 0, epsilon_2 ~ 6 (L528), followed by slow roll with
  (epsilon_1, epsilon_2) ~ (0, -2.8x10^-2) (L534). [VERIFIED]
- Acceptance quantities (L522-543): (i) the power spectrum of R^NR extracted from the BSSN
  fields against the Mukhanov-Sasaki spectrum once the window has rolled through (L522,
  L536); (ii) freezing of R on super-Hubble scales (L522, L534); (iii) constraint violation
  relative to the absolute constraint magnitudes [H], [M]: second order in the noise
  (H/[H] ~ 10^-10 for noise ~ 10^-5), with first-order violation when a noise sign is flipped
  (L538-541); (iv) convergence of constraints and spectra (App. E, L733 ff.); (v) the
  backreaction ablation changes the spectrum by at most about one part in 10^4 (L520).
  The paper gives no numerical pass/fail tolerance for (i)-(ii). [VERIFIED; tolerance
  statement by search of Sec. 3.3]

## 8. Where do the relativistic corrections of arXiv:2404.16270 become significant?

- Broadly for pericentre distances below about 100 r_g (L194, citing Tejeda et al. 2017);
  Fig. 2 (`fig2`) marks where general-relativistic effects reach 1 % or more (L204); for
  M_BH = 10^6 M_sun this means binaries with a_0 < 0.01 au (L194). Definitions: penetration
  factor beta = r_t/r_p (Eq. (1)); the direct-capture limit 4 r_g gives
  beta_max ~ 25.3 (M_BH/10^6 M_sun)^(-2/3) (m_b/M_sun)^(-1/3) (a_0/0.01 au) (Eq. (3), L211).
  [VERIFIED]
- Simulated range: m_b/M_BH = 10^-6, a_0 = 1.013 r_g, beta from 0.1 to 10, 400 phases per
  beta (L317, L348, L782). Results: prograde encounters, relativistic effects below 0.1 %
  (L788) except a few very deep ones (beta >= 9) with ejection speeds up to 2000 km/s above
  Newtonian (L790); retrograde encounters, effects are large: separation starts at
  beta ~ 2 instead of 2.5 and separation fractions are up to 30 % larger than Newtonian
  (L475, L795); HRNA and 1PN agree up to beta = 5 and differ by up to 10 % for 5 <= beta <= 10,
  i.e. r_p below about 20 r_g, where 1PN is insufficient (L477, L792). [VERIFIED]

## 9. AthenaK: Z4c vertex- or cell-centred? What does `tmunu` need, and when is it filled?

- Cell-centred. Upstream AthenaK at c5a0d7f9155a: the Z4c arrays have nx + 2 ng points per
  direction like the cell-centred hydro arrays (src/z4c/z4c.cpp:81-88), the code calls them
  cell-centred (z4c.cpp:199), and the right-hand side and the boundary condition take
  coordinates from CellCenterX (z4c_calcrhs.cpp:663-664, z4c_Sbc.cpp:81-83). The paper says
  the same (2611.12831v1 L674). [VERIFIED]
- `tmunu` holds ten cell-centred components: E, S_i (x, y, z) and the symmetric S_ij
  (xx, xy, xz, yy, yz, zz) (src/z4c/tmunu.hpp:28-43; allocation with the same cell counts,
  src/z4c/tmunu.cpp:26-32). Z4c reads E, S_d, S_dd in CalcRHS (z4c_calcrhs.cpp:129-131, 450,
  576, 584). [VERIFIED]
- When: upstream fills it only from dynamical GRMHD, `DynGRMHD::SetTmunu`, queued in the
  numerical-relativity task list's run section after `MHD_CopyU` (src/dyn_grmhd/dyn_grmhd.cpp:
  198-200, definition :415); `Z4c_CalcRHS` lists `MHD_SetTmunu` as an optional dependency
  (src/z4c/z4c_tasks.cpp:48-58; QueueTask signature src/tasklist/numerical_relativity.hpp:
  126-128). So the sources are refreshed at every Runge-Kutta stage before the Z4c right-hand
  side. [VERIFIED] In this repository the NRPIC particles deposit once per step in the
  `after_timeintegrator` list (push, excise, deposit), and the sources stay fixed through the
  Runge-Kutta stages of the next step (local/nrpic: athenak/src/particles/particles_tasks.cpp:
  30-45), as the paper describes (2611.12831v1 L676). [VERIFIED]
- Query: `python3 -I kb/bin/kb code Tmunu` answers from both repositories.
