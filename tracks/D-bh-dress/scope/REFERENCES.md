# REFERENCES of Track D (S4), G0 scoping

Read at the source on 2026-11-15. Sources were fetched with
`harness/bin/nrpic-fetch-arxiv` into `kb-data/raw/arxiv/<id>/<version>/src/` (untracked,
never committed); a locator `file:line` is relative to that `src/` directory. Labels:
[VERIFIED] read in the source at the locator; [BACKGROUND] standard result not read at its
source here; [JUDGEMENT] my inference; [TO VERIFY] open.

## 1. Spikes and the dress (problem S4, brief lines 396-398, 404; sheet D-pre-2, D-pre-3)

### arXiv:1305.2619 v1, Sadeghian, Ferrer, Will, "Dark matter distributions around massive black holes: A general relativistic analysis" (`SFWpaper.tex`)
- [VERIFIED] Adiabatic growth of a black hole in a dark-matter distribution done with the
  exact Schwarzschild geometry and its adiabatic invariants (`:60-74`, `:412-419`).
- [VERIFIED] The density vanishes at r = 4Gm = 2 R_S, not 8Gm = 4 R_S as in Gondolo-Silk:
  `:67`, `:109`, `:408-409`; reason: a marginally bound particle (E = 1) is captured for
  L < L_c = 4Gm (`:120`).
- [VERIFIED] Capture angular momentum
  L_c^2 = 32 (Gm)^2 / [36 E^2 - 27 E^4 - 8 + E (9E^2 - 8)^(3/2)] (`:381`), L_c = 4Gm at
  E = 1, 2 sqrt(3) Gm at E = (8/9)^(1/2) (`:384`); lower energy limit E_min(r) (`:400-405`).
- [VERIFIED] Constant distribution function: the Gondolo-Silk profile
  rho = (4 pi f_0 / 3) (2Gm/r)^(3/2) (1 - 8Gm/r)^(3/2) (`:440`) is a factor of three below
  the relativistic peak; replacing 8Gm by 4Gm gives the right limits and a peak about
  15 percent above the relativistic one (`:443`).
- [VERIFIED] Hernquist halo (10^12 M_sun, a = 20 kpc): beyond about 50 R_S the standard
  result; near the hole a spike 2-3 times above Gondolo-Silk (`:124`).
- [VERIFIED] Numerical results are for Schwarzschild only; the Kerr formalism is set up
  (`:243-356`) but the capture condition is analytic only for Schwarzschild (`:377`).
- [VERIFIED] Adiabaticity requires the dynamical time inside the influence radius to be
  short against the growth time (`:897-903`). Track D's black holes grow on the Hubble
  time with eps = H M = 0.01 to 0.1, so the adiabatic profile is a probe-limit reference,
  not the expected outcome of the full runs [JUDGEMENT].
- Use: D-pre-2 baseline (Schwarzschild).

### arXiv:1707.06302 v2, Ferrer, da Rosa, Will, "Dark matter spikes in the vicinity of Kerr black holes" (`kerrdm.tex`)
- [VERIFIED] Exact Kerr geometry in the relativistic adiabatic-growth framework; rotation
  increases the density close to the hole (`:83-95`). Numbers not yet extracted
  [TO VERIFY at G1]. Use: the Kerr half of D-pre-2 (the brief's sheet cites only
  1305.2619, which has no Kerr numbers).

### arXiv:1901.08528 v2, Adamek, Byrnes, Gosenca, Hotchkiss, "WIMPs and stellar-mass primordial black holes are incompatible" (`PBH-UCMH-ArXiv-v2.tex`)
- [VERIFIED] Turnaround from r'' = -GM/r^2 + (a''/a) r (`:149-152`); turnaround radius in
  radiation domination r_ta = (2 G M t_ta^2)^(1/3), the numerically calibrated value,
  better than 0.1 percent (`:166-169`), against the analytic (4 G M t^2)^(1/3) (`:163`).
- [VERIFIED] Frozen-at-turnaround estimate rho = (rho_eq/2) t_eq^(3/2) (2GM)^(3/4) r^(-9/4)
  (`:225-234`); the radial orbits after turnaround keep the shape and raise the density
  by about 50 percent (`:235`; 53 percent in appendix A, `:468`).
- [VERIFIED] GADGET-2 N-body (Newtonian, radiation in the background), (8 kpc/h)^3,
  256^3 particles, a 30 M_sun seed (`:297-299`); inner power-law slopes alpha = 2.28 and
  2.35 for the two spectra (`:346`, `:354`), "close to 9/4" (`:323`).
- [VERIFIED] r^(-9/4) is attributed to Fillmore-Goldreich 1984 and Bertschinger 1985 for
  spherical collapse in Einstein-de Sitter (`:235`); earlier work assumed r^(-3/2), which
  the paper calls incorrect (`:442-444`).
- Use: D-pre-3 normalisation and slope; note that the paper's background is radiation
  dominated, Track D's is matter dominated.

### arXiv:2106.07480 v2, Boudaud, Lacroix, Stref, Lavalle, Salati, "In-depth analysis of the clustering of dark matter particles around primordial black holes I: density profiles"
- [VERIFIED] Radiation era, Newtonian phase-space treatment; three slopes: 3/2 (accreted
  at kinetic decoupling), 9/4 (accreted later, radial infall, large hole mass), 3/4 (inner
  caustics, small hole mass); the profile is universal in r / R_S
  (`sections/conclusion.tex:9`). An overlooked part of phase space (Y_m < 0) changes
  earlier results (`:5`). General relativity near R_S is explicitly left out (`:20`).
- Use: D-pre-3 context (which slope to expect where) and the statement that the region
  near R_S is open, which is what the full-GR run adds.

### arXiv:1607.00612 v2, Eroshenko, "Dark Matter Density Spikes around Primordial Black Holes" (`paper2.tex`)
- [VERIFIED] Spikes start at formation in the radiation era from the slow tail of the
  thermal velocity distribution, denser than secondary accretion gives (`:27-37`).
  Use: context only.

### arXiv:1805.09034 v3, Kavanagh, Gaggero, Bertone, "Black Holes' Dark Dress: On the merger rate of a subdominant population of primordial black holes" (`main.tex`)
- [VERIFIED] Halo growth by radial infall: r'' = -G M/r^2 + (H' + H^2) r (`:188-190`);
  M_halo = M_PBH at equality (`:193`); profile rho ~ r^(-3/2) attributed to Bertschinger
  1985 (`:195-199`); truncation R_tr(z) = 0.0063 (M_halo^eq / M_sun)^(1/3)
  (1+z_eq)/(1+z) pc (`:208`); M_halo(z) = (R_tr(z)/R_eq)^(3/2) M_PBH (`:218`).
- [VERIFIED] Binaries simulated with GADGET (Newtonian) and a generalised NFW stand-in for
  the r^(-3/2) halo because the latter is not an isolated Newtonian equilibrium
  (`:568-577`); high-resolution runs took more than 200 h on 16 CPUs (`:614`).
- Conflict [VERIFIED as a conflict, TO VERIFY at the original]: 1805.09034 (`:195`)
  and 1901.08528 (`:235`) cite Bertschinger 1985 for different slopes (3/2 and 9/4).
  Bertschinger 1985 (ApJS 58, 39) and Fillmore-Goldreich 1984 (ApJ 281, 1) are not on
  arXiv; request to kb.
- Use: the dressed-binary stage (after G3) and the brief's statement that the merger-rate
  effect is estimated in Newtonian terms (brief line 398): confirmed.

### arXiv:2109.04896 v3, "Primordial black hole formation with full numerical relativity" (`PBH_formation.tex`)
- [VERIFIED] Matter-dominated background modelled by an oscillating massive scalar
  field, the perturbation by a massless scalar (`:89`); initial PBH mass
  M H ~ 1e-2 M_Pl^2 with G = M_Pl^-2 (`:58`, `:99`, `:241`), i.e. eps = H M ~ 1e-2 in
  Track D's units; growth faster than the self-similar M ~ 1/H at first, M ~ H^(-beta)
  with beta >> 1, not followed beyond a few times the initial mass because of cost
  (`:243`).
- Use: sets the physically motivated range eps ~ 1e-2 and the "matter-era scalar-field
  result" of the brief (line 398): confirmed as a scalar-field, not a particle, result.

### arXiv:2608.13206 v3, "Long-term 3+1 simulations of primordial black hole formation during radiation domination" (`PRD.tex`)
- [VERIFIED] GRChombo hydrodynamics, radiation domination, a cosmologically scaled
  Gamma-driver (factor about 94 fewer coarse steps, `:39`); late growth fitted to the
  Zel'dovich-Novikov law dM/dt = 4 pi F R_BH^2 rho_b = (3F/2) M^2/t^2,
  M(t) = [1/M_inf + 3F/(2t)]^-1 (`:457-465`), fit from the first point with
  Psi = dM/dt / (H M) <= 0.1 (`:466-471`); F = 2.96 to 3.61 (`:473-486`); the
  efficiencies are foliation dependent (`:505`).
- Use: the template of a growth-law fit (functional form, Psi criterion) for Track D's
  collisionless case; the cosmologically scaled driver is a gauge idea to check against
  B's periodic gauge [JUDGEMENT].

### Other dress and spike references named by the brief, not read in this package
arXiv:astro-ph/9906391 (Gondolo-Silk; its formula is read through 1305.2619 `:440`),
arXiv:2411.12007, arXiv:1712.06383, arXiv:2002.10771, arXiv:2002.12811, arXiv:2211.01362,
arXiv:2402.13762, arXiv:2505.09715 [TO VERIFY when the dressed-binary stage starts].

## 2. Cosmological coupling of black holes (brief lines 237, 400; the null test)

### arXiv:2302.07878 v1, Farrah, Croker, Tarle, Faraoni et al., "Observational evidence for cosmological coupling of black holes and its implications for an astrophysical source of dark energy" (`paper_couple_rev.tex`)
- [VERIFIED] Claim: black-hole models with realistic behaviour at infinity predict that
  the gravitating mass can grow with the expansion independently of accretion or mergers,
  depending on the interior solution (`:100-101`).
- [VERIFIED] Parameterisation M(a) = M(a_i) (a/a_i)^k, a >= a_i, k >= 0 (`:165-167`); for
  identical homogeneous non-singular interiors k = -3 P/rho (`:170-171`).
- [VERIFIED] Measured k = 3.11 +1.19 -1.33 (90 percent), Gaussian fit 3.09 +- 0.76; k = 0
  disfavoured at 99.98 percent (`:103`, `:129-133`).
- [VERIFIED] k = 0 is the value expected for traditional black holes like Kerr (`:132`);
  k = 3 for vacuum-energy interiors (`:132-133`, `:174`).
- Consequence for the null test [JUDGEMENT]: an ordinary (vacuum, puncture) black hole is
  expected at k = 0 by both the claim and its critics; a null result does not test the
  claim, which concerns non-vacuum interiors (SCOPE.md, section 3).

### arXiv:2306.11588 v2, Cadoni, Sanna, Pitzalis, Banerjee, Murgia, Hazra, Branchesi, "Cosmological coupling of nonsingular black holes" (`main.tex`)
- [VERIFIED] In GR, singularity-free black holes couple; leading term from the curvature
  term, M ~ a^k with k = 1, universal for spherically symmetric objects; nonsingular
  horizonless objects have an extra model-dependent term; such objects are unlikely to be
  the dark energy (`:67`). Causality limits -3 <= k <= 3 (`:82`). Lists critiques
  (`:84`) whose identifiers are in `main.bbl:139-220`.
- Use: k = 1 as a second reference value for the wording of the null test.

### arXiv:2308.07374 v2, Gaur, Visser, "Black holes embedded in FLRW cosmologies" (`BH-in-FLRW-for-arXiv-V2-2023-08-21.tex`)
- [VERIFIED] Kottler, McVittie and Kerr-de Sitter show no coupling of the mass parameter
  to H (`:146`, `:194`, `:293`, `:379-381`, `:638`, `:673`, `:701-704`). McVittie in four
  forms (`:308-334`); at small distances it is Schwarzschild in isotropic coordinates
  with constant m and no accretion (`:370-381`). Separation-of-scales argument and
  r_* = (m / rho_FLRW)^(1/3) (`:213-224`). Most investigations of non-vacuum interiors
  find no direct coupling (`:695`).
- [JUDGEMENT, derived here from `:322-326`] In the McVittie form
  ds^2 = -(1-2m/R) dt^2 + [dR/(1-2m/R)^(1/2) - H R dt]^2 + R^2 dOmega^2 the outgoing
  radial null rays have dR/dt = (1-2m/R)^(1/2) [H R - (1-2m/R)^(1/2)], so the apparent
  horizon sits at 1 - 2m/R = H^2 R^2, R_AH = 2m (1 + 4 m^2 H^2 + ...), and the area mass
  R_AH/2 changes with H although m does not: d ln M_AH / d ln a = -12 (m H)^2 in
  Einstein-de Sitter. A definitional, not a physical, drift of the area mass in a
  non-vacuum neighbourhood; it is -1.2e-3 at m H = 0.01 (run
  D-bh-dress-20261115-120304-795eee9, `scoping_table.txt`, Part B). To be re-derived by a
  second agent before use.

### arXiv:2304.09817 v2, Mistele, "Comment on 'Observational evidence for cosmological coupling of black holes ...'" (`bh-de.tex`)
- [VERIFIED] The link to dark energy rests on a Friedmann-like equation with spatially
  averaged density and pressure derived by Croker and Weiner 2019 (`:84-111`); the
  derivation from the Einstein-Hilbert action contains a mistake (`:73-76`, `:120-121`).
- Use: the null test does not address this averaging argument (SCOPE.md, section 3).

### arXiv:2109.08146 v1, Croker, Zevin, Farrah, Nishimura, Tarle, "Cosmologically coupled compact objects: a single parameter model for LIGO-Virgo mass and redshift distributions" (`c3o_first_study_apjl.tex`)
- [VERIFIED] One parameter k of cosmological mass growth for remnants above the TOV
  limit; solutions with cosmological boundary conditions that reduce to Kerr on short
  time scales (`:35-41`); k = 0.5 raises the observable merger rate 20 times (`:49-53`).

### Observational and other critiques (abstracts and the stated bounds read)
- [VERIFIED] arXiv:2302.12386 v2, Rodriguez: NGC 3201 black holes; the coupling needed for
  dark energy requires nearly face-on orbits (probability at most 1e-4) or a formation
  mass below 2.2 M_sun (`sample631.tex:255-259`).
- [VERIFIED] arXiv:2305.01307 v1, Andrae, El-Badry: Gaia BH1 and BH2; with k = 3 the
  formation masses are below 2.2 M_sun at 70 and 77 percent; both above it jointly only
  6.9 percent (`andrae-elbadry-2023.tex:48-50`, `:184`). Restates the range -3 <= k <= 3,
  k = 1 as the comoving Schwarzschild radius of Faraoni-Jacques 2007 (`:83`).
- [VERIFIED] arXiv:2303.06630 v1, Avelino: gravastars cannot be the dark-energy source; a
  coupled mass adds a velocity-dependent acceleration (`gravastars.tex:41-45`).
- Named in 2306.11588 `main.bbl` and not read: arXiv:2302.13333 (Parnovsky),
  arXiv:2304.01059 (Wang), arXiv:2305.03408 (Lei et al., JWST, k about -1 per
  2306.11588 `:86`), arXiv:2307.02474 (Amendola et al.), arXiv:2307.10708 (Gao, Li),
  arXiv:2306.08199 (Ghodla et al.); arXiv:1904.03781 (Croker et al. 2020). Croker and
  Weiner 2019 (ApJ 882, 19) and Faraoni-Jacques 2007 (PRD 76, 063510) identifiers not
  checked [TO VERIFY].

## 3. Black holes in expanding universes as numerical relativity (the periodic version)

- [VERIFIED] arXiv:1801.01083 v1, Bentivegna, Clifton, Durk, Korzynski, Rosquist,
  "Black-Hole Lattices as Cosmological Models" (review; `main.tex:161-175`): construction,
  large-scale dynamics, "dressing of mass" between black holes, distance-redshift.
- [VERIFIED] arXiv:1204.3568 v2, Bentivegna, Korzynski, "Evolution of a periodic
  eight-black-hole lattice in numerical relativity" (`eightBH.tex:101-110`): S^3
  topology, not a torus.
- Not read: lattices on the torus and dust-plus-black-hole lattices [TO VERIFY; to be
  found through kb before the periodic version is planned].

## 4. Einstein-Straus construction (D-pre-1)

- Einstein and Straus 1945 (Rev. Mod. Phys. 17, 120) is not on arXiv; its stability
  literature not read [TO VERIFY, request to kb].
- [VERIFIED, repository] The orchestrator's construction of the slice (time-symmetric
  puncture inside, Painleve-Gullstrand-like curvature joining the comoving wall) is
  `coord/notes/derivations_to_check.md:38-53`, status [JUDGEMENT] to be re-derived by
  Track D; the data format is `coord/INTERFACES/spherical_id_format2.md`.
- [VERIFIED, repository] Core's format-2 implementation and its tests are on branch
  `core/id-extrinsic` (not on main): `408df57` (format 2 in `nrpic_cf`), `c9aa6d2` (test 1,
  constraints at the start), `1311b8e` (test 2, expanding ball against the exact solution
  in three gauges: areal-radius errors 3.3e-3, 1.1e-3, 4.6e-4 at dx = 1, 1/2, 1/4 M with
  the conformal-time lapse; with 1+log a lapse front from the surface reaches the centre;
  a sharp surface leaves a constraint residual that does not converge; the outflow
  condition is violated by the r^(-3/2) fall-off of K_ij).

## 5. Brief statements checked here

| Brief line | Statement | Finding |
|---|---|---|
| 398 | r^(-9/4) from Newtonian self-similar secondary infall [BACKGROUND] | Supported by 1901.08528 `:235`, `:323` and by run D-bh-dress-20261115-120304-795eee9 (frozen-in slope -2.2503 at a/a_i = 1000); the arXiv sources cite the same 1985 paper for 3/2 and 9/4; original not read [TO VERIFY] |
| 398 | Zel'dovich-Novikov law for radiation-era fluid (2608.13206) | Confirmed (`PRD.tex:457-486`) |
| 398 | Matter-era scalar-field result (2109.04896) | Confirmed: massive scalar field as the matter (`:89`) |
| 398 | Dress effect on merger rate estimated in Newtonian terms (1805.09034) | Confirmed: GADGET runs (`:290`, `:568`) |
| 400 | Null result expected | Agreed, and also expected by the claim's own authors for Kerr (2302.07878 `:132`) |
| 773 | D-pre-2 Schwarzschild and Kerr spike from 1305.2619 | 1305.2619 has Schwarzschild numbers only; Kerr: 1707.06302 |
| 775 | D-pre-4 "with public AthenaK" | This repository's AthenaK (decision 0010) |
