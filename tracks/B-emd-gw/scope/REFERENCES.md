# Key references of Track B, read at the source (G0)

All sources fetched on 2026-11-15 with `harness/bin/nrpic-fetch-arxiv`; paths are under
`/data/haiyangw/nrpic/kb-data/raw/arxiv/<id>/<version>/src/` (untracked, never
committed). Locators are `file:line` in that directory. Every statement below was read
at the locator in this session ([VERIFIED] in the sense of the brief: read in the
original); my own reading or consequence for Track B is marked [JUDGEMENT].

| id (version) | Authors, title | What it computes | Approximation | GW amplitude scaling given |
|---|---|---|---|---|
| 2403.15126 (v1) | Dalianis, Kouvaris, "Gravitational Waves from Collapse of Pressureless Matter in the Early Universe" | GW spectrum of collapsing triaxial overdensities in an early matter era: Zel'dovich up to turnaround, then N-body through pancake, violent relaxation, virialization; average over the Doroshkevich distribution | Newtonian N-body, N up to 1e4, started at turnaround with the Hubble flow neglected; flat-space quadrupole formula, slow motion | Omega_GW proportional to sigma^(7/2), i.e. A_s^(7/4); peak of omega^7 Q^2 at omega ~ 1/t_col, amplitude proportional to delta_L^(7/2)/t_k; peak Omega_GW today ~ 1e-6 sigma^(7/2) (M/Msun)^(2/3) (T_rh/GeV)^(4/3) |
| 2605.04487 (v2) | Escriva, Harada, Kohri, Terada, Yoo, "Gravitational wave emission from nonspherical collapse in an early matter-dominated era using N-body simulations" | Same problem with a semirelativistic N-body code; GW from the numerical quadrupole; Doroshkevich and BBKS averages | Newtonian gravity, relativistic particle kinematics; leading-order quadrupole; factor-of-order-one uncertainty stated for moderately relativistic velocities | Peak frequency proportional to M_k^(-1/3) T_rh^(1/3), peak amplitude proportional to M_k^(2/3) T_rh^(4/3); Zel'dovich-based estimates fall short of the numerical spectra at the peak (about three orders for the BBKS average) |
| 2111.09163 (v2) | Ota, Macpherson, Coulton, "Covariant transverse-traceless projection for secondary gravitational waves" | Covariant (York) TT part of the extrinsic curvature and its energy density rho_K as a gauge-invariant, hypersurface-dependent GW measure | Exact definition; second-order perturbation theory for the analysis | None (diagnostic); rho_K is half the Isaacson density for linear tensor modes |
| 1604.06065 (v2) | Adamek, Daverio, Durrer, Kunz, "gevolution: a cosmological N-body code based on General Relativity" | Weak-field N-body in Poisson gauge with all six metric degrees of freedom; equation for h_ij | Weak-field expansion, linear in B_i and h_ij, some quadratic terms in Phi | None; quasi-static h_ij is a static spin-2 field, not a free wave |
| 1704.04307 (v1) | Giblin, Mertens, Starkman, "A cosmologically motivated reference formulation of numerical relativity" | BSSN evolution of the difference from a reference (FLRW) solution | Exact GR, numerical | None; error lower by an order of magnitude or more depending on the reference |
| 2608.13206 (v3) | Ning, Cai, Wang, Yoo, "Long-term 3+1 simulations of primordial black hole formation during radiation domination" | 3D NR hydrodynamics (GRChombo) of PBH formation; cosmologically scaled Gamma-driver; conformal-time moving-puncture gauge | Exact GR, radiation fluid | None |
| 2610.23218 (v1) | Munoz, Byrnes, et al., "Simulating dust collapse: the impact of gauge choices on primordial black hole formation" | 3D NR of dust-fluid collapse in a matter era; comparison of lapse and shift conditions | Exact GR, pressureless fluid (fails at shell crossing) | None |
| 2207.03125 (v2) | Aurrekoetxea, Clough, Lim, "CTTK: A new method to solve the initial data constraints in numerical relativity" | CTT variant solving the Hamiltonian constraint algebraically for K at given conformal factor; periodic and black-hole data | Exact constraints, multigrid | None |
| 2501.13046 (v2) | Aurrekoetxea, Brady, Areste-Salo, Bamber, Chung-Jukko, Clough, et al., "GRTresna: An open-source code to solve the initial data constraints in numerical relativity" | Multigrid solver of CTTK and CTTK-hybrid, periodic boundaries | Exact constraints | None |
| 1505.04756 (v2) | Fidler, Rampf, Tram, Crittenden, Koyama, Wands, "General relativistic corrections to N-body simulations and the Zel'dovich approximation" | N-body gauge in which Newtonian N-body plus Zel'dovich initial data contain all first-order relativistic effects | First-order perturbation theory | None |
| 2010.12584 (v2) | Rampf, Hahn, "Shell-crossing in a LambdaCDM Universe" | Lagrangian perturbation theory to 40th order at the first shell crossing of random 3D data | Pressureless fluid, Newtonian | None |

## Locators and notes

### 2403.15126 (`pII_GW_Vir_C2_Arx.tex`)
- Abstract: lines 173-175. Zel'dovich deformation and turnaround time t_max: 427-503.
- N-body: initial conditions at turnaround, Hubble flow neglected afterwards (611); N
  up to 1e4 equal-mass particles placed at random in the ellipsoid (667-669).
- Tensor equation in conformal Newtonian gauge with TT source (879-882); quadrupole formula
  valid for slow-motion sources with v << 1 (884-887); power G/(5c^5) dddot Q^2 (898);
  spectrum dE/dln omega = (4 pi G/5c^5) omega^7 |Q(omega)|^2 (903); Omega_GW today
  (911-918).
- Zel'dovich quadrupole Q^Zel (959-961); peak of omega^7 |Q|^2 at omega ~ 1/t_2 with
  amplitude proportional to delta_L^(7/2)/t_k (1007); sigma^(7/2) and omega_peak
  proportional to sigma^(3/2) (1031); Omega_GW proportional to sigma^(7/2) = A_s^(7/4)
  (1074).
- Violent relaxation enhances the signal, at most by one order of magnitude (312);
  observable peak amplitude and frequencies (1501-1509).
- [JUDGEMENT] for Track B: the peak of the Zel'dovich part sits at omega ~ 1/t_col, i.e.
  at a wavelength 2 pi t_col = (4 pi/3)/H larger than the Hubble radius at emission, where
  the flat-space quadrupole formula has no clear meaning; the relativistic calculation
  is needed exactly there (criterion N4 of the brief).

### 2605.04487 (`main_v3.tex`)
- Abstract: line 171. Semirelativistic model (Newtonian forces, relativistic kinematics,
  "roughly horizon-sized patches"): 206-213; isolated patch in an exact EdS background
  (695).
- GW: leading-order mass quadrupole about the mass centroid; higher multipoles, stress
  and post-Newtonian terms left out; factor-of-order-one uncertainty for moderately
  relativistic velocities (1568-1590); analytic third derivatives (1741-1850);
  dE/dln omega (2891).
- Particle load: glass-like relaxation plus quadrupole clean-up lowers the initial
  |Q_ij| from about 1e-1 (random) to 1e-14, "to reduce artificial GW emission seeded
  purely by shot noise" (2234-2238).
- Representative run (sigma = 0.1, nu about 2): first shell crossing at t/t_k = 22.5,
  second axis at 29.1, peak of the virial ratio and main GW epoch at 34.3, 99 percent of
  the energy emitted by 45.0 (2275-2281).
- Velocities: for sigma = 0.01 the bulk stays nonrelativistic; for sigma = 0.1 the mean
  and median |v_pec|/c reach 0.4 to 0.5 near the emission peak (2395-2405).
- Resolution: N = 3000 and softening 0.05 chosen; N = 3000 against 9000 differ little
  (2365, 2616); the high-frequency tail depends on the softening (2354).
- Numerical spectra above the Zel'dovich ones (2512); about three orders of magnitude
  at the peak for BBKS (2625); scaling of peak frequency and amplitude with M_k, T_rh
  (2576-2581); a fully general-relativistic treatment named as future work (2630).
- [JUDGEMENT] for Track B: the representative relativistic case (v up to 0.5c) is
  inside the range the full-GR code can follow; the comparison quantity is the
  dimensionless source spectrum before the mapping to today.

### 2111.09163 (`prd_v1.tex`)
- Abstract: 68-80 (rho_K has only propagating modes on the Newtonian constant-time
  hypersurface at second order, line 76).
- York decomposition Q = Q_TT + (LV) + trace, vector Laplacian for V: 160-187.
- rho_K = (M_pl^2/2) K^TT_ab K_TT^ab (260); Hamiltonian-constraint split into rho_K,
  rho_R, rho_V, rho_div (237-270); rho_K = rho_Isaacson/2 for linear tensor modes,
  zero for linear scalars (272-274).
- Hypersurface dependence (not gauge dependence): 369-426. Conclusions, Newtonian
  hypersurface useful for purely oscillating second-order GWs (629-660, line 647).
- [JUDGEMENT] for Track B: on a torus the York decomposition has a harmonic part (the
  kernel of the TT conditions); for plane symmetry it is one global mode (check 1C), to
  be reported apart from the radiation.

### 1604.06065 (`compendium_arxiv.tex`)
- Metric and Poisson gauge kept beyond perturbation theory: 142-154.
- Traceless space-space equation for chi, B_i, h_ij with 2 dPhi dPhi + 4 Phi ddPhi
  terms and 8 pi G a^2 Pi on the right: 294-298; spin-2 projector: 1394.
- h_ij not evolved in that version; quasi-static h_ij is "a static spin-2 perturbation
  of the geometry", oscillations only where the adiabatic approximation fails: 1427-1444;
  Wronskian (unequal-time correlator) method for the spectrum: 1446-1452.
- [JUDGEMENT] for Track B: decision 0010 rules out running gevolution; its h_ij
  equation evaluated on AthenaK particle snapshots (outside `athenak/src/`) is the
  weak-field reference. Check 2 uses its quasi-static limit.

### 1704.04307 (`nonlinear_cosmo_reference.tex`)
- Abstract 38-48: evolving differences from a reference solution lowers the error by an
  order of magnitude or more, depending on how well the reference approximates the
  solution. [JUDGEMENT] option for B-pre-2; `cosmo/` evolves the full variables with a
  conformal-time lapse and reaches 1e-6 on the homogeneous universe at 32 cells
  (`cosmo/TESTLOG.md` lines 65-68).

### 2608.13206 (`PRD.tex`)
- Abstract 38-39: GRChombo hydrodynamics, cosmologically scaled Gamma-driver with a time
  step growing with the scale factor, about 94 times fewer coarse-level advances,
  conformal-time moving-puncture gauge; threshold mu_c = 0.7958 for a Gaussian profile.
  [JUDGEMENT] gauge reference for the strong-field end (with Track A).

### 2610.23218 (`main.tex`)
- Abstract 39-41: in matter-era dust collapse, black-hole lapse conditions must be
  adapted; the Gamma-driver fails at shell focusing; shift damping depends on the
  resolution of the focusing region. Shell crossing ends fluid runs (introduction,
  line 51). [JUDGEMENT] consistent with `cosmo/TESTLOG.md` E1 (lines 494-516,
  809-826): no stable run through black-hole formation yet.

### 2207.03125 (`paper.tex`)
- Abstract 97-...: CTTK solves an algebraic equation for K at given conformal factor.
- Periodic domains: four integrability conditions; with constant K, no net momentum
  over the slice (184-205). [JUDGEMENT] `cosmo/ic/cosmo_id.py` instead solves for the
  conformal factor at given K and removes the mean of the momentum source
  (`removed_momentum_source_mean` in `cosmo/ic/make_east.py`).

### 2501.13046 (`main.tex`)
- Summary and features: lines 62-103 (CTTK and CTTK-hybrid, periodic boundaries,
  scalar-field sources only in the current version). [JUDGEMENT] method reference only;
  decision 0010 rules out adopting it.

### 1505.04756 (`finalpaper.tex`)
- Abstract 65-...: in most gauges the Zel'dovich displacements of N-body initial data
  receive a first-order relativistic correction; in the N-body gauge they do not, and a
  Newtonian simulation contains all first-order relativistic effects (also 204, 315).
  [JUDGEMENT] defines what "the Newtonian prediction" of a GR run means at first order;
  `cosmo/` uses the Chisari-Zaldarriaga and Green-Wald dictionary instead
  (`cosmo/ic/make_east.py` lines 11-15).

### 2010.12584 (`nLPT-arxiv-v2.tex`)
- Abstract 142-...: LPT to 40th order converges at the first shell crossing of random
  3D data. First-shell-crossing regions are fairly ellipsoidal; quasi-one-dimensional
  collapse rarely is the source of the first shell crossing (404-407); the Zel'dovich
  approximation is insufficient for the eigenvalues at shell crossing (956).
  [JUDGEMENT] the exactly plane-symmetric pancake is a test case, not the typical first
  collapse; LPT beyond first order is the pre-shell-crossing reference for the
  crossed-wave source.

## Not fetched in this package, needed later
2212.00425, 2312.12499 (Newtonian box GW spectra, the S2 wavenumber comparison),
1002.3278, 1704.03500, 2012.14016 (gauge of induced GWs), 1708.09143 (Szekeres row),
1908.05683 and 1711.06681 (the single-wavelength data of `cosmo/`, already in `refs/`).
