# References of the Track C scope, read at the source

All sources fetched with `harness/bin/nrpic-fetch-arxiv` on 2026-11-15 into
`kb-data/raw/arxiv/<id>/<version>/src/` (read-only, untrusted data: read, never run).
Locators are `file:line` inside that directory. Third-party text is not copied here
beyond short phrases. Labels as in `SCOPE.md`.

## Core references (S3 key references, brief 392, and the threshold row of section 10)

### arXiv:2108.11967 (v2) Feng, Yu, Zhong, "Dynamical Instability of Collapsed Dark Matter Halos" — `main.tex`
- Model: truncated Maxwell-Boltzmann with Tolman-Klein temperature, parameters
  b = kT(R)/mc^2 and w(0) (main.tex:103-118); equation of state integrals and TOV
  (122-153). Reproduced by `scripts/king_sequence.py` (run C-sidm-20261115-115348-eb8b752).
- Adiabatic-index criterion reached at v(0) = 0.566 c, Z(0) = 0.750 for b = 0.1;
  0.566-0.564 c and 0.750-0.622 for b = 0.1-0.5 (274) [VERIFIED; our solver: w(0) =
  4.05115, Z(0) = 0.7500].
- Maximum of the fractional binding energy 0.0352 at v(0) = 0.506 c, Z(0) = 0.548 (b = 0.1);
  0.0352-0.0356 at 0.548-0.522 for b = 0.1-0.5 (280) [VERIFIED as the paper's grid points;
  the continuous maximum is at Z(0) = 0.5404 for b = 0.1, our run].
- Binding-energy maximum at Z(0) = 0.297, total-energy maximum at 0.087 (286).
- Agreement with Shapiro-Teukolsky N-body collapse at eps of about 0.035, Z(0) of about 0.5;
  the adiabatic criterion is sufficient, not necessary (283).
- Instability compactness 0.0236-0.0793 for b = 0.09-5.0 (297); b >= 0.1 needed for the
  classical regime (327); J1205-0000 seed 1.9e9 M_sun (324); t_seed of about 1.5e-9
  t_halo, about 69 days (355).
- Table, b = 0.1 and 0.2 (490-529).

### arXiv:2601.17117 (v2) Gu, Jiang, Chen, Li, "Non-Equilibrium Relativistic Core Collapse of SIDM Halos" — `SIDM_MS.tex`
- Misner-Sharp formalism with Eckart heat flux, spherical, fluid (abstract 52-72;
  method 235-357). Ideal-gas law P = (gamma - 1) eps rho (341); gamma = 5/3 stated for the
  non-relativistic case only (344) [the value used near horizon formation: TO VERIFY].
- Conductivity: SMFP and LMFP forms, a = (16/pi)^(1/2), b = 25 pi^(1/2)/32, C = 0.75,
  lambda = 1/(rho sigma), H = (v^2/(4 pi rho))^(1/2), t_0 = lambda/(a v) (233).
- Fiducial halo R_s = 2.6 kpc, rho_s = 0.019 M_sun/pc^3, M(<10 R_s) = 6.3e9 M_sun,
  sigma/m = 5 cm^2/g, t_0 = 0.26 Gyr (384); observed sigma/m of 1-100 cm^2/g (156).
- SMFP from rho_c of about 1e5 rho_s; transition at 445.0 t_0; SMFP mass peaks at
  5e7 M_sun (1 percent) at 445.6 t_0 and falls to 1e-4 of the halo by 445.8 t_0 (429, 440).
- Collapse slows: t_c of about 0.1 t_0 at 445.8 t_0, about 40 t_0 at 460 t_0 (474);
  quasi-static treatment of the central region in the late phase (457).
- Horizon at 580 t_0 with m of about 3e-8 M, about 200 M_sun (476); parameter table
  200, 700, 500 M_sun (503-507).
- Next steps announced: baryons, central accretion (514); velocity-dependent
  cross-sections (520). Non-equilibrium pressure factor f_P and the statement that the
  collisional Boltzmann equation is needed (672-676).

### arXiv:gr-qc/0601112 (v1) Andreasson, Rein, "A numerical investigation of the stability of steady states..." — `ssevnum7.tex`
- Binding-energy maximum signals onset of instability, also for non-isotropic shells
  (abstract 47-58; 866-873); A > 1 perturbations collapse for Z_c above about 0.40
  depending on the case (840-842); tables of four cases with L_0 = 0.1 (762-837).
- E_b > 0 and A < 1: oscillation; E_b < 0 and A < 1: dispersion (896-921).
- Critical collapse: unstable steady states act as critical solutions, no universality
  (152-167; section 5 from 1021).
- Defects [TO VERIFY with the authors' later papers]: Z_c = 1/sqrt(alpha(0)) - 1 (694)
  while alpha is the lapse of the metric (229-231, 591); Table 3 values 0.045, 0.052
  (811-812) must be 0.45, 0.52.

### arXiv:2009.08163 (v1) Gunther, Korner, Lebeda, Potzl, Rein, Straub, Weber, "A numerical stability analysis for the Einstein-Vlasov system" — `paper.tex`
- Polytropic and King ansatz functions (630-636); z_c measured to the edge of the steady
  state, not to infinity (684-689).
- King model: first binding-energy maximum y_max = 0.334, first zero 0.784 (948-958)
  [VERIFIED and reproduced: 0.33403, 0.78452 at b = 1, run ...115348].
- Binding-energy-maximum hypothesis confirmed for isotropic polytropes and King, three
  coordinate systems (1059-1091); the mass-radius turning point is not the threshold;
  Einstein-Euler states with the same profiles are unstable earlier (1155-1170).
- Collapsing King model: all particles end inside the trapped surface (1190-1193).

### arXiv:2105.05556 (v1) Gunther, Straub, Rein, "Collisionless equilibria in general relativity: stable configurations beyond the first binding energy maximum" — `paper.tex`
- Evidence against the strong binding-energy hypothesis; the weak one confirmed;
  multiple stability changes (abstract 87-89; definitions 139-141).
- History: Ipser 1969, growing mode for z_c above about 0.5 (Maxwell-Boltzmann, power
  law) (167); "collisionless star clusters are stable if the corresponding fluid star
  model is stable" (152).
- Core-halo configurations (488, 505); onset near the second maximum for small i (581);
  two stability changes for 255 <= i <= 290, i = 270 example (612); stability defined as
  no collapse within 1000 M (559).

### arXiv:2602.17487 (v1) Juno et al., "Modeling of Relativistic Plasmas with a Conservative Discontinuous Galerkin Method" — `sn-article.tex`, `intro.tex`, `methods.tex`, `results.tex`
- A relativistic Vlasov-Maxwell solver on a phase-space grid in Gkeyll (abstract
  sn-article.tex:91-94). The collision operator appears only as the symbol C[f]
  (intro.tex:9); its tests are collisionless (methods.tex:196; results.tex:18)
  [VERIFIED by grep for "collision" in all files]. Not a reference for collisional
  relaxation (brief row 852) and, as an outside code, excluded by decision 0010.

### arXiv:2611.12831 (v1) Wu, Most, the NRPIC source paper — `main.tex`
- Monoenergetic suite: N = 2e6, 128^3 root mesh, Table with y_c, z_c, R/M, M_0/M, L,
  dx, t_BH (1016-1031) [VERIFIED and reproduced to the printed digits, run ...115344].
- Binding-energy discussion and citation of 2105.05556 (1006); y_c sequence (1092);
  dimensionless variables, L = (P_c/(4 pi rho_c^2))^(1/2) (1055-1059).

## SIDM background (brief 232-234, 380-393)

### arXiv:astro-ph/0110561 (v2) Balberg, Shapiro, Inagaki — `SIDMGT_Xiv2.tex`
- t_r = 1/(a rho v sigma), a = (16/pi)^(1/2) for hard spheres (310-321); t_coll of about
  290 t_r (332; abstract 63-64).
- Inner core fluid-like (lambda/H << 1), exterior collisionless at the onset; the whole
  inner core expected to collapse, the outside to stay in equilibrium (983-1010); core
  loses about one decade in mass per decade in central temperature at late times
  (1031-1033).

### arXiv:astro-ph/0111176 (v3) Balberg, Shapiro — `SMBH_SIDM_Xiv2.tex`
- Seeds of 1e2-1e3 M_sun from halos formed by z = 5 (abstract 31-40); collapsing core mass
  1e-8 to 1e-6 of the halo (289-291); M_coll relation at v_c of about c/3 (167-174).

### arXiv:2010.15132 (v3) Feng, Yu, Zhong — `smbh.tex`
- Kn = lambda/H, H = (nu^2/(4 pi G rho))^(1/2), conductivities with C of about 0.75 (116).
- Mass of the Kn < 1 region 1.8e-3 M_0 with baryons, 4.2e-2 without; seed assumed equal to
  it (151); GR instability at 3D v = 0.57 c, <gamma> = gamma_cr of about 1.62, eps = 0.033
  (210).

### arXiv:2506.17641 (v3) "Dark Bondi Accretion Aided by Baryons and the Origin of JWST Little Red Dots" — `sidmacc.tex`
- 1D central dispersion of about 0.3 c triggers the instability; only 1e-10 to 1e-8 of
  the halo reaches it; about 1 M_sun for a 1e9 M_sun halo (74) [VERIFIED: the brief's
  statement in line 234 is correct].
- Kn = lambda/H with H the local Jeans length; M_smfp of about 1e-2 M_0; M_GR scaling
  and energy argument (133-142); quotes 2601.17117: M_GR/M_smfp of about 4e-6 (145).
- Asks for anisotropic-dispersion fluid models; cites Gurian 2025 (218).

### arXiv:1101.3097 (v2) Koda, Shapiro — `sidm1.tex`
- Pairwise Monte Carlo scattering inside GADGET; elastic, isotropic in the centre-of-mass
  frame; pairs scattered together because Nanbu's one-sided scheme drifted the energy by
  10 percent (516-596).
- Limits: collision probability below 0.1 per step; k = 32 neighbours inside one mean
  free path; N scales as lambda^-3 (667-697). Kn defined as 1/(rho sigma r) (722-728).
- Fluid and N-body agree for Kn >= 1 with b = 0.25, five times below Chapman-Enskog;
  calibration needed beyond the transitional regime (1481-1491).

### arXiv:2504.00075 (v2) "Massive Black Holes Seeded by Dark Matter" — `SMBH_GW.tex`
- Dissipative SIDM, semi-analytic population model; seed fraction f_col = 3e-3 fixed
  from earlier simulations (abstract 117-119; 162, 283). No relativistic dynamics.
  Background only for Track C.

### arXiv:1707.08666 (v1) Gauy, Ramos-Caro — `HernquistDF-PRD7c.tex` (Latin-1, CRLF)
- Static distribution functions of relativistic hypervirial models (abstract 77-103).
  No stability statement read. Listed in the brief's threshold row (843); its use for
  Track C is as a family of static models only.

## Not read

- Shapiro and Teukolsky 1985, 1986, 1992; Ipser 1968, 1969, 1980; Zel'dovich and
  Podurets 1965 (not on arXiv): quoted second hand only.
- gr-qc/9804040, gr-qc/0107076, 1409.5176 (critical collapse, optional row 844).
- Gurian 2025 (collisional Boltzmann SIDM; identifier unknown here).

## Corrections to the brief that follow from these sources

1. Brief 384 says the core "passes from short to long mean free path". The sources say
   the opposite direction: early long mean free path, late short
   (2601.17117 SIDM_MS.tex:62-66; astro-ph/0110561 abstract, SIDMGT_Xiv2.tex:56-62).
2. Brief 520 (M5) and row 852 of section 10 cite arXiv:2602.17487 for collisional
   cross-validation; that paper has no collision operator, and decision 0010 excludes
   outside codes. Replace by exact relativistic kinetic results (Maxwell-Juettner
   equilibrium, relaxation rates, transport coefficients) computed in this repository.
3. Brief 843 lists 1707.08666 as a stability reference; it is a construction of static
   distribution functions (abstract), not a stability study.
4. The charter's G2 phrase "the collisionless threshold reproduces the literature
   value" has no single literature value: 2105.05556 shows the threshold is a family
   property and can lie beyond the first binding-energy maximum.
