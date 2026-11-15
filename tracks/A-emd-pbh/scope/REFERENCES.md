# Key references of S1, read at the source

Track A, G0. Read on 2026-11-15 from the shared store; locators are
`<file>:<line>` of the extracted source under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<version>/src/` (untracked, read only; never
copied into git). "by eye" marks a value read from one of the paper's own figures,
rendered from the PDF in its source. Labels: [VERIFIED] read at the locator,
[JUDGEMENT] our reading or inference, [TO VERIFY] not settled.

What every entry answers: set-up; quantities computed; threshold and spin statements;
numerical method; particle numbers and resolution; what is NOT computed.

---

## arXiv:2609.14218 v1, Yoo, Escriva, Harada, Kohri, "Simulation of PBH formation in a matter-dominated universe" (`MDPBH.tex`)

- Set-up [VERIFIED]: BSSN with background scale factor in the metric decomposition
  (L264-268); long-wavelength (gradient-expansion) growing-mode data on a constant-mean-
  curvature slice, K = -3H, psi, gamma-tilde_ij, A-tilde_ij and lapse given in closed form
  from Psi = exp(zeta/2); E and J^i then follow from the constraints (L509-547). Profile
  ln Psi = (mu/2) exp(-k^2 r^2/6)[1 + (k^2/6)(p(2X^2-Y^2-Z^2) + 3e(Y^2-Z^2))] (L839), the
  typical BBKS peak of a narrow spectrum (L842-846). H_i = 5k = 50/L, a_i = 1 (L549);
  horizon entry k^2/(a^2H^2) = 6 at t_H = 100 sqrt(6)/k = 10 sqrt(6) L (L709-719). Domain
  0 <= X^i <= L (one octant) with the non-Cartesian "scale-up" coordinates of eta = 10
  (central cells 11 times finer, L476-487). Boundary conditions: said to be compatible
  with the coordinate map but not stated (L483) [TO VERIFY: reflective octant symmetry
  assumed].
- Gauge [VERIFIED]: new slicing (del_t - beta.del) alpha = -2 alpha (K + 3H) +
  (3/2) alpha H_k exp(-C^2 alpha_b^2/a_k^2), C = 5, alpha_b the lapse at the box corner
  (L452-457); initial lapse L460; shift: hyperbolic Gamma driver with damping 3H (L466-469).
- Matter [VERIFIED]: (i) dust fluid; (ii) collisionless particles, 3+1 geodesic equations
  for Gamma and V^i (L1019-1026); deposition by a uniform cube of one cell per particle,
  sqrt(gamma) at the particle (L1053-1060); particles on a regular lattice that fills the
  domain "with no space and no overlap", inhomogeneity carried by unequal masses
  m_p = E sqrt(gamma) dV / Gamma_p (L1064-1074).
- Resolution [VERIFIED]: 80 grid points per direction for the spherical and the e-scan
  fluid runs (L776, L942), N = 80 for the particle runs (caption, L1095); 40 points for the
  particle-LTB comparison (L1482). Particle number not stated; one per cell is implied by
  L1065-1066 [JUDGEMENT: 80^3 = 5.1e5 in the octant].
- Results [VERIFIED]: LTB analysis: globally naked for mu = 0.32, locally naked (black
  hole) for mu = 0.33, e = 0 (L766-768). Dust fluid, p = 0, e in {0, 0.01, 0.03, 0.05,
  0.1, 0.15, 0.2, 0.25} classified as "HF w/o crash", "crash w/ HF", "crash w/o HF"
  (L960-967); horizon before the crash needs about twice the analytic amplitude (abstract
  L173-174); at e = 0.2 the fluid crashes before horizon formation for mu <= 0.95
  (L1085-1086). Particles, e = 0.2: horizons for mu >= 0.05, none for mu <= 0.045 (L1101-
  1103), threshold "around mu ~ 0.045" (L1145), an order of magnitude below the analytic
  estimate (abstract L177). Particle runs plotted to 250 t_H (`alpha.pdf`, by eye); the
  smaller mu, the later the lapse collapses (T2 of `JOURNAL.md`). mu = 0.045 interpreted as
  a halo supported by velocity dispersion (L1122-1124, L1138), and "will continue to run
  unless manually stopped" (L1141-1142).
- Caveats stated by the authors [VERIFIED]: Hamiltonian constraint "significantly violated"
  in the particle runs, localised where particles cross (L1148-1149, L1176-1186).
- Analytic comparison line [VERIFIED, reproduced in run A-emd-pbh-20261115-112625-e854f12,
  T1]: eigenvalues (2 mu/15)(k^2/a^2H^2)(1+3e+p, 1-2p, 1-3e+p) (L907-908), criterion
  mu > h-hat(e,p) 6a^2H^2/k^2 with h-hat of L918, evaluated at aH = k/sqrt(6) (L987).
- NOT computed: black-hole mass (no horizon masses reported), spin, gravitational waves,
  accretion after formation, any convergence study in grid or particle number, p != 0
  (only p = 0 runs, L941), velocity dispersion in the initial data, binaries.

## arXiv:2610.23218 v1, Munoz, Byrnes, Bruni, Hawke, "Simulating dust collapse: the impact of gauge choices on PBH formation" (`main.tex`)

- Set-up [VERIFIED]: synchronous comoving initial data from ICPertFLRW, gamma_ij =
  a^2(1 - 2R_c) delta_ij - (4/5H^2) d_i d_j R_c (L63-67); R_c = sum A cos(2 pi x^i/L)
  (L72-74); initial max density contrast 0.03, wavelength 4 initial Hubble radii (L76);
  box [0, L/2]^3 with symmetric boundaries, 64^3 coarse points, up to 8 refinement levels
  added at fixed values of the rescaled time (L78, L272-275). Total mass in the box 0.47 L
  (L270).
- Method [VERIFIED]: Einstein Toolkit, McLachlan W-BSSNOK (L104-111); dust by CT_Dust
  (Wilson) and by GRHydro (Valencia, HRSC: PPM + HLLE) with p = 1e-50 rho^2 (L113,
  L161); Kreiss-Oliger dissipation epsilon = 0.2 (L170-177).
- Gauge findings [VERIFIED]: 1+log with g = K drives the lapse to ~20 before collapsing
  (L208); g = K - K_FLRW with K_FLRW from local proper time drops the lapse to ~0.5 then
  lifts it (L213-222); g = K + sqrt(24 pi rho) and g = exp(-alpha) K fail (L226-236);
  new softplus slicing g_s+ with S = 450 and a decreasing transition T is their best
  (L240-250), used with shock-avoiding f = 1 + 1/alpha^2 (L199-202, L270). Gamma driver
  fails under shell focusing; the best damping depends on the refinement level
  (eta = 1 at level 8, 0.1 at 6, 0.01 at 4) (L294); W-dependent damping tried (L297-300).
  Advection terms help or hurt depending on resolution (L307).
- Black-hole criteria [VERIFIED]: hoop ratio 2M/R-circumferential along three directions
  exceeds 1 (L352-360); a couple of grid points with Theta_out < 0 but no apparent horizon
  found by AHFinderDirect (L386); Kretschmann and Weyl/Ricci ratios still Ricci dominated
  at the centre (L440).
- NOT computed: an apparent horizon, black-hole mass or spin, particles, non-spherical
  shapes beyond the cubic-symmetric cosine (three equal amplitudes, L51), any threshold.

## arXiv:1609.01588 v2, Harada, Yoo, Kohri, Nakao, Jhingan, "PBH formation in the matter-dominated phase of the Universe" (`apj_nonsphericalpbh.tex`)

- Set-up [VERIFIED]: Newtonian Zel'dovich approximation r_i = a q_i + b p_i (L381-383),
  deformation eigenvalues alpha >= beta >= gamma (L414-418, L463); horizon entry
  a(t_i) q = c/H(t_i) = r_g (L478-490); turnaround of the first axis b/a = 1/(2 alpha)
  (L503), pancake at b/a = 1/alpha (L537).
- Criterion [VERIFIED]: hoop conjecture C <~ 2 pi r_g (L583-584), giving
  h(alpha,beta,gamma) = (2/pi)(alpha-gamma)/alpha^2 E(sqrt(1-((alpha-beta)/(alpha-gamma))^2))
  <~ 1 with b/a normalised to a/a(t_i) (L596-613). If not satisfied, a caustic forms, the
  pancake virialises at about half the maximum radius, and "may later shrink ... by
  radiating its energy", on a time much longer than the Hubble time (L619-631).
- Statistics [VERIFIED]: Doroshkevich distribution (L637-693); beta_0 ~= 0.05556 sigma^5
  for sigma << 1 (abstract L226, L764), bounds 0.01338 sigma^5 <~ beta_0 <~ 0.1280 sigma^5
  (L771); sigma = std of delta_L at horizon entry (L698-699); collapse is nearly spherical
  to O(sigma) for those that form black holes (L807-809).
- NOT computed: any simulation; spin; velocity dispersion; inhomogeneity (noted would give
  sigma^(13/2), caption L745-747); the fate of the virialised pancakes.

## arXiv:1707.03595 v4, Harada, Yoo, Kohri, Nakao, "Spins of PBHs formed in the matter-dominated phase" (`Spin_PBH.tex`)

- Set-up [VERIFIED]: Newtonian cosmological perturbations, angular momentum at first and
  second order (L369-735); assumed scalings |L_(1)| ~ q delta_s, |L_(2)| ~ I sigma delta_s
  (hypothesis, L826-868).
- Spin and threshold statements [VERIFIED]: t_m = t_H delta_s,H^(-3/2) (L894); a_* =
  max((2/5) sqrt(3/5) q delta^(-1/2), (2/5) I sigma_H delta^(-3/2)) (L900-907); Kerr bound
  a_* <= 1 as the condition for direct formation (L948); delta_th = max(delta_th(1),
  delta_th(2), delta_fd) with delta_th(1) = 12 q^2/125, delta_th(2) = ((2/5) I sigma_H)^(2/3)
  (L953-962); finite duration of the matter era gives the cutoff delta_fd = (t_H/t_end)^(2/3)
  (L919-927). Abstract: most PBHs near-extremal, a_* ~ 1 (L81-86); suppression factor
  exp(-0.15 I^(4/3) sigma_H^(-2/3)) (L76-77); beta_0 ~= 0.05556 sigma_H^5 for 0.005 <~
  sigma_H <~ 0.2 (L93-95).
- NOT computed: any simulation; angular momentum after turnaround or through shell
  crossing; accretion; the O(1) parameters q, I are free.

## arXiv:2211.13950 v3, Harada, Kohri, Sasaki, Terada, Yoo, "Threshold of PBH formation against velocity dispersion in matter-dominated era" (`MD_threshold10.tex`)

- Set-up [VERIFIED]: two scales, PBH scale k-tilde and small scale k on which caustics
  generate velocity dispersion (L198-245); Case I (small-scale halos virialise first) and
  Case II (dispersion released directly), t_vir ~ t_ent delta_ent^(-3/2) (L282), criterion
  L298-301.
- Statements [VERIFIED]: Liouville scaling sigma_v ~ R^-1 once shared (L330-334); collapse
  halts when free-fall time equals crossing time; non-formation if
  sigma_v(t_*) R(t_*) > (3/2) R_ent (L349-360); thresholds L423-427 and L550-563; for a
  log-normal spectrum delta_th ~ sigma_0^(2/5) (abstract L102-103, L606-607); order-unity
  factors ignored (L375); the result is a necessary condition for formation (L440-442).
- NOT computed: any simulation; anisotropy or spin together with dispersion (combined only
  in the abundance estimate, L613-640); O(1) coefficients.

## arXiv:2507.18312 v3, "Primordial black hole formation in matter domination" (`Main.tex`; authors not checked)

- Statements [VERIFIED]: in spherical dust (LTB) the centre reaches a shell-focusing
  singularity at t_c (L222-226); for a generic n = 1 profile 2GM/R -> 0 near the centre at
  t_c, so no horizon unless the profile is flat (A_2^(2/3) << delta_m) (L234-238); after
  t_c collisionless shells pass through the centre and re-expand: "the numerical
  simulations do not support" later black-hole formation (L240), so for a typical peak the
  threshold is delta_m ~ 1 (L242). A uniform top hat collapses to a black hole for any
  delta_m (L310); b_BH = (5/3) delta_m (L314-316). With small-scale perturbations
  zeta_rms the threshold is zeta^(2/5) for a top hat (L338) and zeta^(1/10) for the peaks
  that dominate the abundance (L399, L402-408, abstract L87); a_rms ~ zeta_rms^(7/4)
  (L635).
- Numerics [VERIFIED]: Newtonian N-body only, "evidence not for the threshold ... but for
  the halting mechanism" (L478); top hat at rest, b_min ~ 1.2 N^(-1/3) for random positions
  (L483-489); lattice b_min ~ N^(-4/9) (L522-523); N = 123 and 619 with Gaussian velocities
  (L537-538); virial coefficient 5/3 (L542); Gaussian profile at rest, N = 100-2000, and
  10000 spherical shells with Plummer softening: b_min ~= 0.41 (L547-551), "we have not
  performed a full convergence study" (L549).
- NOT computed: relativistic dynamics, a horizon in any simulation, anisotropic initial
  shapes in the simulations, O(1) coefficients of the thresholds.

## arXiv:2508.10070 v1, "Primordial Black Hole Formation and Spin in Matter Domination Revisited" (`main.tex`; authors not checked)

- Set-up [VERIFIED]: peak theory plus Zel'dovich ellipsoid plus hoop conjecture (abstract
  L78-79; criterion L315-331); peaks labelled by nine parameters (L334).
- Statements [VERIFIED]: those that form black holes collapse nearly isotropically, tidal
  terms w_i <~ O(sigma_h*) (L339-353); beta ~= A_gamma sigma_h*^5 (L80); spin
  <a>_BH ~ sigma_h*^(1/2) << 1, contrary to arXiv:1707.03595 (L82, L504, L680); for a
  monochromatic spectrum the mass function is monochromatic, spin vanishes, beta ~= 1.08
  sigma_h^5, 19 times arXiv:1609.01588 (L657-659, L682-684, table L661-670).
- Numerics [VERIFIED]: Monte Carlo integration over peak parameters (L902-990).
- NOT computed: any dynamical simulation; nonlinear contributions to the spin (L689);
  accretion (L691-692).

## arXiv:2109.04896 v3, de Jong et al., "Primordial black hole formation with full numerical relativity" (`PBH_formation.tex`)

- Set-up [VERIFIED]: background dark matter = oscillating massive scalar (m/H_0 = 62.6,
  phi_0 = 7.8e-3 M_Pl; L127-133, L344, L371); perturbation = massless scalar shell
  xi = Delta-xi tanh((r - R_0)/sigma), initially static, spherical (L135-139); conformally
  flat data, K = -3H_0, Hamiltonian constraint solved radially (L145-164); periodic box
  large enough (L143), one octant with reflective symmetry (L357).
- Method [VERIFIED]: GRChombo, CCZ4, moving-puncture gauge with mu_alpha = 0.5,
  eta_beta1 = 0.75, eta_beta2 = 1e-4 (L294-318); base grids 80, 96, 128, mass converged to
  1 percent (L354, L375).
- Statements [VERIFIED]: direct collapse and accretion-driven collapse; the latter does not
  need the hoop condition (abstract L58; L172-231); formation takes about a Hubble time;
  initial M_BH ~ 1e-2 H^-1 M_Pl^2 (L58, L241); post-formation growth M ~ H^-beta with
  beta >> 1 (L241-243); hoop-conjecture threshold Delta-xi ~ 0.1 M_Pl at R_0 H_0 = 0.65 and
  0.07 at 1.25 (caption L179).
- NOT computed: collisionless matter, non-spherical perturbations, spin, shell crossing.

## arXiv:2306.11810 v2, de Jong et al., "Spinning primordial black holes formed during a matter-dominated era" (`Spinning_PBHs.tex`)

- Set-up [VERIFIED]: as arXiv:2109.04896 with a spinning massless-scalar shell; AH mass,
  spin by isolated-horizon formulas with flat rotational Killing vectors (L188-217).
- Statements [VERIFIED]: about 10-15 percent of the mass and 5 percent of the angular
  momentum end in the black hole at formation (abstract L79, L257, L270); spin efficiency
  peaks near 25 percent and then falls as non-rotating matter is accreted (L267); with
  self-similar growth a_BH ~ H^2, a ~ 1 at formation leaves <= O(0.1) if the matter era
  lasts Delta T >~ 0.8 T_0 (L273-277). Resolution 80/96/128 base grids (L383).
- NOT computed: collisionless matter, the spin of a black hole formed from non-rotating
  but non-spherical data, growth beyond a few e-folds (L279).

## arXiv:2605.04487 v2, "Gravitational wave emission from nonspherical collapse in an early matter-dominated era using N-body simulations" (`main_v3.tex`; authors not checked)

- Set-up [VERIFIED]: isolated overdense patch in an Einstein-de Sitter background,
  Newtonian forces with semirelativistic particle kinematics (L189); comoving equations
  with the background removed (L206-340, background term cancels, L297); a glass-like,
  zero-quadrupole ball deformed by the affine Zel'dovich map (L2174-2238); (e, p) defined by
  e = (alpha-gamma)/(2(alpha+beta+gamma)), p = (alpha-2beta+gamma)/(2(alpha+beta+gamma))
  (L1172-1187); the run starts at the turnaround of the shortest axis (L1036-1063, L2277);
  alpha <= 1/2 cut (L1532-1543).
- Method [VERIFIED]: direct particle-particle summation, O(N^2), own C++/Python code
  (L2146); spline softening h = 2.8 epsilon_com (L510); N = 3000 fiducial with
  epsilon_com = 0.05, checks at N = 1000, 9000 (L2275, L2365); GW from the quadrupole
  formula (L1568-).
- Statements [VERIFIED]: Zel'dovich fails after shell crossing (L2277); 99 percent of the GW
  energy emitted by t/t_k ~ 45 for the example (L2281); peculiar speeds up to 0.4-0.5 c for
  sigma = 0.1 (L2400-2402); high-frequency tail not converged in softening (L2354).
- NOT computed: black-hole formation or any horizon criterion; relativistic gravity;
  backreaction; the matter outside the patch beyond the background (it is removed).

## arXiv:1611.07906 v2, Yoo, Harada, Okawa, "3D simulation of spindle gravitational collapse of a collisionless particle system" (`asymflat.tex`)

- Set-up [VERIFIED]: Shapiro-Teukolsky prolate spheroid at rest, conformally flat, K_ij = 0
  (L445-513), total mass 2 M_N (L526-533); particles placed randomly in proportion to the
  reference density (L536-559); domain 0 < x^i/L < 1 (L566-567).
- Method [VERIFIED]: BSSN with Hamiltonian-constraint cleaning by SOR iterations each step
  (L368-389), maximal slicing (L432), leap frog with time filter (L393), cubic-spline
  particle shape of radius r_s (L344-366). L/M = 20, b/M = 10, e = 0.9, Delta = L/120,
  N = 1e6, r_s = L/75; resolution study with r_s ~ Delta, N ~ Delta^-3 (L570-601).
- Statements [VERIFIED]: no apparent horizon for the ST parameters; Kretschmann peak grows
  with resolution, supporting a naked singularity in the continuum limit (abstract
  L97-112, L603-606); a larger-mass case forms a horizon (L838-857).
- NOT computed: cosmological expansion; spin; gravitational waves.

## arXiv:1901.04498 v2, East, "Cosmic censorship upheld in spheroidal collapse of collisionless matter" (`main.tex`)

- Set-up [VERIFIED]: ST spheroids, e = 0.9 with 2 <= b/M <= 20 and b/M = 10, e = 0.95
  (L195-199); axisymmetric 2D domain (L227-228).
- Method [VERIFIED]: harmonic gauge, then damped harmonic near collapse (L204-207); flow
  horizon finder, AH area mass and polar/equatorial circumferences, psi_4 (L210-221);
  N = 1.6e6 particles, finest dx ~ 0.02 M or 0.01 M; resolution studies with 0.75 and 1.5
  times the resolution and the fourth power in particle number (L229-234, L442).
- Statements [VERIFIED]: every case ends as a black hole plus radiation; horizon
  circumferences not more than ~25 percent above 4 pi M_BH (L238-253); P_GW up to ~2e-3
  (L284); E_GW maximal ~0.015 M near b/M ~ 12-14 for e = 0.9 (L292).
- NOT computed: three-dimensional (non-axisymmetric) collapse; cosmological expansion.

---

## Where the references disagree (input to SCOPE.md, section 2)

1. Threshold of a near-spherical pressureless peak: hoop plus Zel'dovich (1609.01588,
   2508.10070) gives mu > 0.45 at e = 0.2 in the normalisation of 2609.14218 (reproduced,
   T1); 2507.18312 argues delta ~ 1 for a typical profile because spherical shell
   crossing halts the collapse; 2609.14218 finds black holes with particles down to
   mu = 0.05 at e = 0.2. [VERIFIED as statements; which is right is the question of S1.]
2. Spin at formation: near-extremal (1707.03595) against ~sigma^(1/2) (2508.10070) and
   ~zeta_rms^(7/4) (2507.18312); scalar-field NR: falls after formation by accretion
   (2306.11810). Nobody has computed it for collisionless matter. [VERIFIED as statements.]
3. Black hole after the first caustic: 1609.01588 leaves it open (L619-631), 2507.18312
   says no for spherical shells (L240), 2109.04896 shows accretion-driven formation for a
   scalar-field background. [JUDGEMENT: the collisionless answer needs runs beyond the
   first caustic, which the particle method allows.]
