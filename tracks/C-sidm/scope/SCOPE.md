# Track C, gate G0: scope of S3 (relativistic collapse of a self-interacting core)

Helper package of owner C-sidm, 2026-11-15. Sources: the brief (lines 30-68, 232-238,
279-313, 380-393, 518-521, 544-547, 747-764, 834-860), `coord/CHARTER.md` section 9.6,
decision 0010, the first paper of this repository (`paper/`), and the references listed
with locators in `REFERENCES.md`. Numbers carry a locator: `file:line` of a paper source
under `kb-data/raw/arxiv/<id>/<version>/src/`, a run id (`tracks/C-sidm/runs/<run_id>/`),
or a file of this repository. Labels: [VERIFIED] read at the source or computed in a
registered run; [BACKGROUND] standard, not checked here; [JUDGEMENT] my inference or
design; [TO VERIFY] open. Figures: `figures/` (copies of the run outputs).

## 1. Problem statement

**Question of S3 (brief 380-393).** After gravothermal collapse has driven the core of a
self-interacting dark-matter (SIDM) halo to relativistic velocity dispersion, how much
mass ends in the black hole, and how do collisions (and later rotation, dissipation,
non-equilibrium heat flux) change that? Track C answers it with collisional
Einstein-Vlasov evolutions in this repository's AthenaK, starting from an equilibrium
core near the relativistic instability instead of evolving the whole gravothermal
history (the latter takes 445 t_0 to reach the short-mean-free-path stage and 580 t_0 to
horizon formation, t_0 = 0.26 Gyr, in the fiducial halo of arXiv:2601.17117,
SIDM_MS.tex:384, 440, 476 [VERIFIED]).

**State of the field [VERIFIED].**
- Instability of a thermalised (truncated Maxwell-Boltzmann) core: maximum of the
  fractional binding energy at Z(0) = 0.548-0.522 for b = 0.1-0.5, adiabatic-index
  criterion at v(0) = 0.566-0.564 c (2108.11967 main.tex:274, 280); our own solver puts the
  b = 0.1 maximum at Z(0) = 0.5404 (run C-sidm-20261115-115348-eb8b752; the published value
  is the grid point w(0) = 3.2).
- Seed mass from the fluid picture: earlier estimates set it to the mass of the
  short-mean-free-path (SMFP, Kn < 1) region, 1.8e-3 to 4.2e-2 of M_0 (2010.15132
  smbh.tex:151) or 1e-8 to 1e-6 of the halo (astro-ph/0111176:289-291). The only
  time-dependent general-relativistic treatment (spherical Misner-Sharp fluid with Eckart
  conduction, arXiv:2601.17117) finds a seed of 3e-8 of the halo, about 200 solar masses,
  because outward heat flux expands the envelope and removes mass from the core
  (SIDM_MS.tex:64-71, 429, 476). Its closure is a fluid with a fixed-gamma ideal-gas law
  (SIDM_MS.tex:341) and a phenomenological pressure factor where collisions become too
  slow; it states that a rigorous treatment needs the collisional Boltzmann equation
  (SIDM_MS.tex:672-676).
- The fluid model agrees with Monte Carlo N-body only for Kn >= 1 and must be calibrated
  beyond the transitional regime (1101.3097 sidm1.tex:1481-1491); its SMFP coefficient fit
  is five times below the Chapman-Enskog value.
- Collisionless limit: a near-threshold King model collapses entirely in spherical
  symmetry, "no particles remain unaffected" (2009.08163 paper.tex:1190-1193); for a
  collisionless core-halo cluster only the core collapses, for a fluid star the whole
  star (astro-ph/0110561:983-1004, citing Shapiro and Teukolsky; the cited papers are not
  on arXiv) [the core-halo statement is BACKGROUND until a source is read].

**What Track C adds [JUDGEMENT].** A three-dimensional, fully general-relativistic,
kinetic calculation with collisions: no fluid closure, no hydrostatic assumption, the
transition from collisionless to fluid set by one parameter. No such calculation exists
(brief 234, [VERIFIED] only in the sense that none of the read references contains one).

**Two observables, in order.**
1. The instability threshold of an equilibrium family as a function of Knudsen number:
   collisionless (Kn = infinity) first, which is the minimum publishable unit of the brief
   (390) and the G2 criterion of the charter.
2. The collapsed mass fraction M_BH/M at horizon formation and at the end of the run, as
   a function of Kn, converged in particle number and collision time step (G3).

**The physics hypothesis the scan tests [JUDGEMENT, from section 3 and 4 below].** Along
the truncated Maxwell-Boltzmann sequence (b = 0.1) four criteria are passed in order:
maximum of the total energy at Z(0) = 0.087, of the binding energy at 0.297, of the
fractional binding energy at 0.540 (our run) and the adiabatic-index criterion at 0.750
(2108.11967 main.tex:286, 286, our run, 274). For collisionless matter the third is a
lower bound of the dynamical threshold and, for the families tested so far without a
strong core-halo structure, the threshold itself (section 3.4). For a collision-dominated gas without conduction
(Kn -> 0) perturbations are adiabatic with gamma = 1 + p/u, and the fourth is the relevant
(sufficient) criterion. Between them, heat conduction on a time ~ t_dyn (Kn ~ 1) makes
the response non-adiabatic, the regime of gravothermal evolution. Prediction to be
tested in G1/G2: a King b = 0.1 model with 0.54 < Z(0) < 0.75 collapses when
collisionless and survives the dynamical time when Kn_c << 1, then evolves secularly at a
rate that depends on Kn. The mass-fraction curve is then expected to be non-monotonic
in Kn. Whether this ordering holds in the kinetic, three-dimensional calculation is the
first science result of the track.

## 2. What the first paper established at 10^4 particles, and what Track C must add

Source: `paper/sections/self_gravity.tex`, subsection "Relativistic clusters" (lines
60-118), Tables `paper/sections/tables/tab_setups.tex`:19-26 and
`tab_outcomes.tex`:88-153; `docs/TESTLOG.md`. All runs use the monoenergetic
(Shapiro-Teukolsky) family with N = 10^4 equal-mass macroparticles [VERIFIED by reading].

Established:
- Stable branch: y_c = 0.900 and 0.819 with a one-percent inward kick keep every
  macroparticle over 300 M; alpha_c ranges 0.886-0.892 and 0.787-0.819
  (tab_outcomes.tex:118).
- Unstable branch: y_c = 0.605 and 0.500 with the same kick collapse; first apparent
  horizon at t = 191.0 M and 104.3 M against 109 M and 73 M of Wu and Most at N = 2e6;
  M_AH/M = 1.0000 and 1.0001 at the end with 6 and 3 macroparticles left
  (tab_outcomes.tex:120-121; self_gravity.tex:100). The cause of the later collapse is
  "not determined" (self_gravity.tex:100). The unbound y_c = 0.283 disperses.
- Unperturbed y_c = 0.5 migrates to the stable branch (to 2500 M,
  tab_outcomes.tex:139-141); near-critical y_c = 0.756 collapses when compressed by ten
  percent (horizon at 147.2 M), oscillates when expanded, and shows the core oscillation
  when unperturbed (tab_outcomes.tex:144-150).
- An intrinsic core oscillation of the stable model y_c = 0.819 grows and saturates at a
  half-swing of 0.015-0.022 in alpha_c, period 75 M against a core radial period of
  66 M; it is not sampling noise, time step, constraint damping or cell size
  (self_gravity.tex:87-89; tab_outcomes.tex:105-110).
- Particle number: N = 10^3 holds the cluster over several periods, N = 10^2 loses
  equilibrium within one period (self_gravity.tex:98).
- Filtering: four binomial passes with compensation are required; plain passes soften
  gravity and bias the equilibrium (self_gravity.tex:69).
- The threshold itself is only bracketed: "the maximum of the binding energy lies
  between y_c = 0.756 and 0.605" (docs/TESTLOG.md:116).

Located here (run C-sidm-20261115-115344-eb8b752, [VERIFIED]): first maximum of E_b/M_0 at
y_c = 0.67961, z_c = 0.45529, E_b/M_0 = 0.036058, R/M = 6.5524 (compactness M/R =
0.1526); first zero at y_c = 0.39045. The models 0.756 and 0.605 have equal E_b/M_0 to
2e-4 (0.033983, 0.033976): they sit symmetrically on the two branches. The reference
module reproduces all five models of Wu and Most to the printed digits
(2611.12831 main.tex:1024-1028). Figure `figures/fig_seq_monoenergetic.png`.

What Track C must add for the collisionless threshold (G2):
1. A located threshold, not a bracket: a scan in y_c between 0.756 and 0.605 (z_c from
   0.33 to 0.59) that measures the growth or oscillation of the fundamental radial mode
   and finds where its growth rate crosses zero, with perturbations of both signs.
2. Three-way convergence of that crossing: particle number (10^4, 10^5, 10^6), cell size
   over the cluster (M/4, M/8; M/2 only as a lower anchor), and gauge or outer boundary
   (domain 512 M against 1024 M; one alternative slicing if core offers one).
3. The core oscillation separated from the unstable mode: near y_c,max both have periods
   of 24-45 M (core radial periods of the 0.605 and 0.756 models, run
   C-sidm-20261115-115400-eb8b752), so the growth rate has to be fitted over several
   periods, after the saturation phase seen at 0.819.
4. The collapse-time discrepancy against Wu and Most (191 against 109 M) tested as an
   N-dependence, which their own text suggests (self_gravity.tex:100).
5. A second family with a core-halo structure and a thermal distribution: the
   truncated Maxwell-Boltzmann (relativistic King) family (section 3.2). The monoenergetic
   family has no halo (R/H_c = 3.4-3.6, run ...115400) and is not an equilibrium of the
   collision operator, so with collisions on it first relaxes towards a thermal
   distribution [JUDGEMENT]; it cannot carry the mass-fraction question.

## 3. Equilibrium families and parameter ranges

Compactness and redshift are given relative to the collisionless threshold of each
family, taken as the first maximum of the fractional binding energy (a lower bound for
core-halo families, section 3.4).

### 3.1 Monoenergetic family (first paper, Wu and Most)

| model | y_c | z_c | E_b/M_0 | M/R | relative to threshold |
|---|---|---|---|---|---|
| stable, first paper | 0.819 | 0.236 | 0.0292 | 0.100 | well below |
| near-critical, first paper | 0.756 | 0.330 | 0.0340 | 0.126 | stable side |
| threshold (this run) | 0.67961 | 0.4553 | 0.03606 | 0.1526 | maximum |
| unstable, first paper | 0.605 | 0.592 | 0.0340 | 0.174 | unstable side |

Run C-sidm-20261115-115344-eb8b752 [VERIFIED]. Proposed scan for G1 [JUDGEMENT]: y_c = 0.74,
0.72, 0.70, 0.69, 0.68, 0.67, 0.66, 0.64, i.e. z_c of about 0.355 to 0.526 and M/R of
about 0.132 to 0.164 (interpolated in the sequence table of the same run).

### 3.2 Truncated Maxwell-Boltzmann (relativistic King) family

The distribution of arXiv:2108.11967 (main.tex:103-153), written in local kinetic energy
with Tolman-Klein temperature, is a function of the conserved energy E only:
f = A [exp(-E/T_inf) - exp(-E_c/T_inf)] for E <= E_c, with b = kT(R)/m = T_inf/E_c.
Derivation [JUDGEMENT, confirmed numerically by P3]: Tolman T e^Phi = const, cut-off
eps_c + m = E_c e^{-Phi}, Klein (mu + m) e^Phi = const; the factor e^{alpha(r)} cancels the
radial dependence. The King model f = (exp(1 - E/E_0) - 1)_+ of arXiv:2009.08163
(paper.tex:635) is therefore b = 1, with y_0 = -ln(1 - b w0).

Independent solver `scripts/king_sequence.py`, run C-sidm-20261115-115348-eb8b752
[VERIFIED]:
- reproduces the b = 0.1 Table of 2108.11967 (main.tex:490-503) to 8e-5 relative in M,
  E_rest, eps_b, Z(0), v(0), <gamma>, gamma_cr; R and C to 2.5e-3 (their printed radii
  sit on a 1e-3 grid). Figure `figures/fig_king_check.png`.
- maximum of eps_b: b = 0.1 at w(0) = 3.1652, Z(0) = 0.5404, eps_b = 0.035179,
  C = 0.04892, v(0) = 0.5035 c; b = 0.2, 0.3, 0.5, 1 at Z(0) = 0.5225, 0.5176, 0.5142,
  0.5119 (eps_b 0.03549-0.03559).
- adiabatic criterion <gamma> = gamma_cr: b = 0.1 at w(0) = 4.05115, Z(0) = 0.7500,
  C = 0.03866; b = 0.2 at w(0) = 1.73634.
- b = 1: maximum at y_0 = 0.33403 and first zero at y_0 = 0.78452, against 0.334 and 0.784
  of 2009.08163 (paper.tex:953). Figure `figures/fig_king_sequence.png`.

Candidate initial models (code units G = c = M = 1; run C-sidm-20261115-115400-eb8b752):

| model | Z(0) | eps_b | R/M | H_c/M | R/H_c | v_1D,c | t_dyn,c/M | T_core/M |
|---|---|---|---|---|---|---|---|---|
| King b=0.1, eps max | 0.540 | 0.03518 | 20.44 | 0.959 | 21.3 | 0.291 | 3.30 | 17.9 |
| King b=0.1, adiabatic | 0.750 | 0.03302 | 25.87 | 0.715 | 36.2 | 0.327 | 2.19 | 11.9 |
| King b=1, eps max | 0.512 | 0.03559 | 13.63 | 1.221 | 11.2 | 0.301 | 4.05 | 22.0 |
| monoenergetic, eps max | 0.455 | 0.03606 | 6.55 | 1.895 | 3.5 | 0.327 | 5.80 | 31.5 |

H_c = (p_c/(4 pi rho_c^2))^{1/2} (equal to the length unit L of the monoenergetic
integration, 2611.12831 main.tex:1057), t_dyn,c = (4 pi rho_c)^{-1/2},
T_core = pi (3/(4 pi rho_c))^{1/2} (as in tab_outcomes.tex:105). The central
one-dimensional dispersion of 0.29-0.33 c matches the "about 0.3 c" of
2506.17641 sidmacc.tex:74 [VERIFIED by the run].

Parameter range proposed for the King family [JUDGEMENT]: b = 0.1 (the boundary
temperature below which the classical treatment fails, 2108.11967 main.tex:327) and
b = 1 (the published collisionless King runs); Z(0) from 0.40 to 0.75 for b = 0.1, i.e.
from below the collisionless threshold to the adiabatic criterion. Spatial range: the
b = 0.1 models reach R = 20-26 M with a core of H_c = 0.7-1.0 M, so the mesh must resolve
M/4 or finer in the core and carry the envelope to about 30 M.

### 3.3 Polytropic shells and other families

Andreasson and Rein (gr-qc/0601112) find the binding-energy maximum signals instability
for anisotropic polytropic shells (L_0 = 0.1); A > 1 perturbations collapse above
Z_c of about 0.40-0.52 depending on the case (ssevnum7.tex:767-834, 840-842) [VERIFIED].
Two defects in that source [TO VERIFY, report to kb]: its definition Z_c =
1/sqrt(alpha(0)) - 1 (ssevnum7.tex:694) is inconsistent with its metric, in which alpha is
the lapse (ssevnum7.tex:229-231; static alpha'/alpha, line 591), and Table 3 prints Z_c =
0.045 and 0.052 between 0.42 and 0.77 (lines 811-812), which can only be 0.45 and 0.52.
Gunther et al. (2009.08163) confirm the binding-energy-maximum hypothesis for isotropic
polytropes and the King model in three coordinate systems (paper.tex:1059-1091) and
define z_c to the edge of the steady state, not to infinity (paper.tex:684-689). Track C
uses these families only as cross-checks; the shells avoid the centre and do not model a
core.

### 3.4 Which criterion is the collisionless threshold [VERIFIED by reading]

- Binding-energy maximum: onset of instability for spherical collisionless steady states
  (gr-qc/0601112 ssevnum7.tex:50-53, 866-873; 2009.08163 paper.tex:1059-1065, 1157-1160;
  Wu and Most 2611.12831 main.tex:1006, 1092).
- Turning point of the mass-radius curve: fails for Einstein-Vlasov; the Einstein-Vlasov
  states stay stable past it, where the Einstein-Euler states with the same profiles are
  unstable (2009.08163 paper.tex:1155-1170).
- Only the weak form holds in general: Gunther, Straub and Rein (arXiv:2105.05556, cited
  by Wu and Most as Gunther:2021pbf, 2611.12831 main.tex:1006) confirm stability up to the
  first maximum but give "strong evidence against" instability setting in there
  (paper.tex:88-89, definitions 139-141); for core-halo models built from piecewise
  linear ansatz functions the onset sits near the second maximum (paper.tex:581), and
  for 255 <= i <= 290 stability changes twice, e.g. i = 270: stable for z_c <= 0.492,
  unstable, stable again for 0.712 <= z_c <= 0.964, unstable beyond 0.983
  (paper.tex:612). Their working definition of "stable" is no collapse within 1000 M
  after a collapse-promoting perturbation (paper.tex:559). They quote Ipser (1969): an
  exponentially growing mode for z_c above about 0.5 for Maxwell-Boltzmann and
  power-law models (paper.tex:167), and "collisionless star clusters are stable if the
  corresponding fluid star model is stable" (paper.tex:152; Ipser not read)
  [VERIFIED as statements of 2105.05556].
- Adiabatic-index criterion with a trial function: sufficient, not necessary; ST85 found
  collapse for models with positive trial frequency (2108.11967 main.tex:283).

Consequence for the King b = 0.1 family [JUDGEMENT]: it is a core-halo family
(R/H_c = 21-36), the kind for which 2105.05556 found the threshold away from the first
maximum. The eps_b maximum at Z(0) = 0.540 is therefore a lower bound of the threshold,
not its value, until the scan of G1/G2 locates it. The same caution applies to the
hypothesis of section 1: which "fluid" (barotropic with the cluster's own p(rho), as in
the Einstein-Euler comparison of 2009.08163, or adiabatic with gamma = 1 + p/u, as for a
collision-dominated gas) is compared decides the ordering of fluid and collisionless
thresholds.

## 4. Knudsen number and the conversion to cross-section per unit mass

**Definition (to be fixed in the collision-operator specification) [JUDGEMENT].**
lambda = 1/(n sigma) = m/(rho_0 sigma) in the local rest frame, rho_0 rest-mass density,
sigma the invariant (centre-of-momentum) cross-section;
H = (p/(4 pi rho^2))^{1/2} with rho the energy density; Kn = lambda/H. This is the
literature's Kn = lambda/H with H = (nu^2/(4 pi G rho))^{1/2} (2010.15132 smbh.tex:116;
2506.17641 sidmacc.tex:133) in a relativistic form. Global variant Kn_R = lambda_c/R.
Central value Kn_c labels a run.

**Conversion.** In code units (G = c = M_ADM = 1):
(sigma/m)_code = 1/(rho_0c H_c Kn_c), and sigma/m [cm^2/g] = (sigma/m)_code G^2 M/c^4,
i.e. 1.097e-23 cm^2/g x (M/M_sun) per code unit. For Kn_c = 1, (sigma/m)_code = 166
(King b = 0.1, eps max), 103 (King adiabatic), 199 (King b = 1), 270 (monoenergetic
maximum) (run C-sidm-20261115-115400-eb8b752).

**Physical Knudsen numbers [VERIFIED by the run, inputs from the references].** For
sigma/m = 5 cm^2/g (the fiducial value of 2601.17117 SIDM_MS.tex:384; observed range
1-100 cm^2/g, line 156) and a near-threshold core of M = 200 M_sun (its seed,
SIDM_MS.tex:476): Kn_c = 4.5e-20 to 1.8e-19 across the six candidate models; for
M = 1.9e9 M_sun (the J1205-0000 benchmark seed of 2108.11967 main.tex:324): 4e-13 to
2e-12. The cross-section that would make Kn_c = 1 at 200 M_sun is 2e-19 to 9e-19
cm^2/g. Figure `figures/fig_knudsen.png`, left.

**Consequence [JUDGEMENT].** A relativistic SIDM core is a perfect fluid on the
dynamical time: the collision time is t_r = t_dyn Kn/a (a = (16/pi)^{1/2},
astro-ph/0110561:310-321), 1e-20 of t_dyn, and conduction across the core takes of order
t_dyn/Kn, 1e20 dynamical times. The Kn reachable in the code (section 7) is 0.1 to 100.
The track's scan therefore does not sample the physical parameter; it maps the bridge
between the collisionless limit and the adiabatic-fluid limit, and the physical answer
is its Kn -> 0 limit. That limit is computable independently in this AthenaK with its
general-relativistic hydrodynamics on Z4c (`athenak/src/dyn_grmhd/`, present in the
tree; its use for this purpose is [TO VERIFY] by core) with the same equilibrium and an
ideal-gas law of the matching adiabatic index. A velocity-dependent cross-section that
falls at high speed (2601.17117 SIDM_MS.tex:520) does not change this: it would have to
fall by about 19 orders of magnitude between halo and core velocities for Kn_c ~ 1.

## 5. Exit criteria

From the charter (section 9.6) with numbers [JUDGEMENT where marked].
- G0 (this package): problem statement, parameter ranges, exit criteria, test plan,
  references at the source, risks, compute estimate. Missing items listed in section 10.
- G1 (baseline without new core work):
  (a) collisionless threshold of the monoenergetic family located to |Delta y_c| <= 0.02
      at N = 10^4 by the sign change of the radial-mode growth rate, both perturbation
      signs, consistent with y_c,max = 0.6796 [JUDGEMENT on the tolerance];
  (b) the reference solutions of section 6 in place and tested (King equilibria, the
      Maxwell-Juettner relaxation and transport references of the sibling package
      `tracks/C-sidm/collide/`, the spherical baseline of `tracks/C-sidm/gravothermal/`);
  (c) the collision-operator and random-number specifications submitted to core
      (C-pre-1, C-pre-2 as specifications under decision 0010).
- G2 (verified capability): collisionless threshold of the monoenergetic and the
  King b = 0.1 family with three-way convergence; the converged y_c (or Z(0)) agrees with
  the binding-energy maximum within the convergence error [JUDGEMENT: target 0.01 in y_c,
  0.02 in Z(0)]; with core's collision module: Minkowski-box tests of section 6 pass,
  and in curved spacetime the rest-mass, energy and momentum budgets close to the
  round-off of pairwise conservation plus the measured collisionless drift.
- G3 (science): M_BH/M against Kn_c for at least one King model on each side of the
  collisionless threshold, Kn_c from 0.1 to 100 plus the two limits, converged in
  collision sub-step and particle number (two of each) [JUDGEMENT on the counts].
- Stop or re-scope [JUDGEMENT]: if pairwise collisions cannot reach Kn_c <= 0.3 within
  the particle number a card holds, the fluid end is taken from the GR-hydro limit only
  and the claim narrows to the transitional regime.

## 6. Test plan against the rows of brief section 10 that Track C holds

| Row (brief 834-860) | Owner | Track C test | Reference solution | Acceptance | Status |
|---|---|---|---|---|---|
| Spherically symmetric Einstein-Vlasov steady states and their stability threshold (843) | CORE, C | (i) equilibrium held: stable models below threshold keep alpha_c and mass radii within the core-oscillation band over >= 10 core periods; (ii) threshold: growth rate of the radial mode against y_c (monoenergetic) and Z(0) (King b = 0.1, b = 1), both perturbation signs, three-way convergence | `python/nrpic/st_cluster.py` (monoenergetic, checked to the printed digits, run ...115344); `scripts/king_sequence.py` (King, checked against two papers, run ...115348); thresholds y_c = 0.67961, Z(0) = 0.5404 (b = 0.1), y_0 = 0.33403 (b = 1) | threshold within the convergence error of the binding-energy maximum | monoenergetic: bracket only (first paper); King: no initial data in the code yet (C-pre-4) |
| Spherically symmetric critical collapse (844) | C (optional) | family A f_s of a King or shell steady state, bisection in A; mass gap (type I) expected | gr-qc/0601112 section 5 (ssevnum7.tex:1021-1090): critical solutions are the unstable steady states, A_c = 1 for an unstable static solution (line 1063) | A_c = 1 within the bisection error for an unstable steady state [JUDGEMENT] | not planned before G2 |
| Collisional relaxation in a Minkowski box (852) | C | relaxation of an anisotropic or two-temperature box to Maxwell-Juettner; collision rate against n sigma <v_rel>; monotone H-function; heat conduction at Kn >> 1 and Kn << 1; exact pairwise conservation of four-momentum | sibling package `tracks/C-sidm/collide/` (Maxwell-Juettner reference `REFERENCES/mj.py`); the cited arXiv:2602.17487 is a collisionless Vlasov-Maxwell DG solver with no collision operator (grep: only "collisionless" and the C[f] symbol, intro.tex:2, 9) and is not usable as the reference of this row [VERIFIED]; it would also be an outside code (decision 0010) | to be set by the collide package | specification in progress (sibling helper) |
| Reproducible random numbers (853) | C, E | the same collision run on 1 and 2 ranks, two MeshBlock layouts, and through a restart: identical particle states | interface `coord/INTERFACES/rng.md` (not yet written): counter-based generator keyed by run seed, counter = (global particle id or pair id, cycle, sub-step, purpose tag) (brief 546) [JUDGEMENT on the pair id] | bitwise equality of positions and momenta | C-pre-2 not started in this package |

Rows of section 10 that Track C uses but does not own: geodesics on a fixed background
and Oppenheimer-Snyder collapse (CORE; horizon-mass error of the first paper, e.g.
M_AH/M = 1.0004 at formation and 0.9987 at 60 M for the lattice dust ball,
tab_outcomes.tex:50).

## 7. Risks, with numbers

1. **Stiff collision term at short mean free path** [VERIFIED numbers from run
   C-sidm-20261115-115400-eb8b752; constraints from 1101.3097 sidm1.tex:667-697].
   A pairwise Monte Carlo operator needs a collision probability below 0.1 per step and
   its k = 32 partners within one mean free path. At the first paper's step dt = M/16:
   Kn_c = 1 needs 600-1600 macroparticles and no sub-cycling; Kn_c = 0.1 needs
   6e5-1.6e6 macroparticles and 2-7 collision sub-steps; Kn_c = 0.01 needs 6e8-1.6e9
   macroparticles and 18-65 sub-steps. N scales as Kn_c^-3. Below Kn_c of about 0.1 the
   scheme's heat flux is set by the partner distance, not by lambda (sidm1.tex:686-689).
   Mitigation [JUDGEMENT]: sub-cycled collisions down to Kn_c = 0.1; the Kn -> 0 end
   from GR hydrodynamics in the same code; an asymptotic-preserving variant (local
   Maxwell-Juettner resampling when Kn << 1) only if core judges it cheap.
2. **Relaxation time against dynamical time** [numbers VERIFIED by the run; reading
   JUDGEMENT]. Physical cores: t_r/t_dyn = Kn_c/a ~ 1e-20, conduction ~1e20 t_dyn
   (section 4). In the code: t_r = 1.46 M (King b = 0.1, Kn_c = 1) against t_dyn,c =
   3.30 M and T_core = 17.9 M; the gravothermal collapse time of a long-mean-free-path
   core is about 290 t_r (astro-ph/0110561:332), i.e. 400-4000 M for Kn_c = 1-10, within
   the 2500 M the first paper ran. The brief's risk "the whole gravothermal process
   cannot be evolved" holds for physical Kn, not for the code's Kn: the code compresses
   the gravothermal time by up to 1e20. Every statement about the physical seed mass
   must therefore pass through the Kn -> 0 limit.
3. **Choice of initial model** [JUDGEMENT]. The monoenergetic family has no envelope
   (R/H_c = 3.4-3.6) and collapses completely (6 and 3 of 10^4 macroparticles left,
   tab_outcomes.tex:121); it cannot show a mass fraction below one and is not a
   collisional equilibrium. The King b = 1 model also collapses completely when
   collisionless (2009.08163 paper.tex:1190-1193). Whether the King b = 0.1 model
   (R/H_c = 21) leaves an envelope is open; if it does not, the mass fraction below one
   comes only from conduction-driven envelope expansion (2601.17117 SIDM_MS.tex:429), and
   the King b = 0.1 runs must be long enough for it (section 9).
4. **The threshold may not sit at the binding-energy maximum** [VERIFIED as a finding of
   2105.05556 for core-halo families, paper.tex:88-89, 612]: for the King b = 0.1 family
   the scan has to extend to Z(0) of about 1 and both stability changes have to be
   looked for; a "collapse within 1000 M" criterion (paper.tex:559) costs 1000 M per
   model, 2.5 times the 400 M assumed in section 8 for the monoenergetic scan.
5. **Threshold definitions differ between sources** [VERIFIED]: redshift to infinity
   (2108.11967; Wu and Most), to the edge of the steady state (2009.08163 paper.tex:687),
   and an inconsistent formula in gr-qc/0601112 (section 3.3). Comparisons go through
   y_c, w(0) or y_0, never through a quoted redshift alone.
6. **Particle noise and perturbation near threshold** [VERIFIED]: N = 10^2 loses
   equilibrium within one period, N = 10^3 drifts (self_gravity.tex:98); collapse times
   at N = 10^4 are 1.4-1.8 times those at 2e6 (tab_outcomes.tex:120). The intrinsic core
   oscillation (period near the core radial period) overlaps the unstable mode near
   threshold (section 2).
7. **Collision kinematics in curved spacetime** [JUDGEMENT]: pairs must be scattered in
   the local orthonormal frame of the cell (tetrad of the pusher), with four-momentum
   conserved there; the specification must state how pairs straddling a refinement or
   MeshBlock boundary are formed, or forbid them.
8. **Excision and collisions** [JUDGEMENT]: lapse excision removes macroparticles; the
   collision partners inside the horizon must be removed consistently so that no
   collision transfers momentum across the excision surface.
9. **Compute budget**: the G2 and G3 estimates of section 8 exceed the 20 GPU-hour
   allotment of decision 0006; see section 8.
10. **Competition** [VERIFIED as of the read sources]: the Misner-Sharp group
   (2601.17117) announces baryons and accretion next (SIDM_MS.tex:514); 2506.17641 asks
   for fluid models with anisotropic velocity dispersion and cites collisional
   Boltzmann work (sidmacc.tex:218). The cited "Gurian:2025zpc" (collisional Boltzmann
   treatment, SIDM_MS.tex:672) was not read [TO VERIFY by kb].

## 8. Compute estimate

**Measured unit costs** (one A100, N = 10^4, run C-sidm-20261115-115400-eb8b752 parsing the
AthenaK logs of the first paper; wall clock; figure `figures/fig_costs.png`) [VERIFIED]:

| setup (tab_setups.tex) | span | wall | s per M | card-h per 100 M | peak GPU memory (MiB) |
|---|---|---|---|---|---|
| static dx = M/2, L = 1024 M, y_c = 0.819 | 300 M | 501 s | 1.67 | 0.046 | 12281 |
| static dx = M/4, L = 512 M, y_c = 0.5 migration | 2500 M | 8198 s | 3.28 | 0.091 | 12283 |
| static dx = M/4, L = 1024 M, y_c = 0.756 | 800 M | 2968 s | 3.71 | 0.103 | 14135 |
| adaptive M/4 -> M/16, y_c = 0.605 collapse | 300 M | 4251 s | 14.2 | 0.39 | 32343 |
| adaptive M/4 -> M/16, y_c = 0.5 collapse | 120 M | 2098 s | 17.5 | 0.49 | 32343 |

Log files: `runs/st/yc0819_v4/athena.20261113-062220.log`,
`runs/st/migration_yc0500_v4/chain/seg00{1,2,3}*.log`,
`runs/st/yc0756_unpert/chain/seg001.job4216.a1.log`,
`runs/st/yc0605_v5/athena.20261113-{083550,100905}.log`,
`runs/st/yc0500_v5/athena.20261113-083550.log` (main checkout, untracked; sha256 in the
run manifest). Particle work: about 3 percent at 10^4 particles (docs/TESTLOG.md:47-48);
4.1e-8 s per particle and cycle from the 2.1e6-particle periodic run
`runs/cosmo/dav_c256_n64/athena.20261114-031241.log` (estimate: its Z4c share is taken
from the 1.9e7 zone-cycles/s of docs/TESTLOG.md:46, not measured in that run). At
dt = M/16 (16 cycles per M), 10^6 particles add about 0.66 s per M, 18 percent of the
static dx = M/4 cost. The cost of a collision is not measured anywhere yet.

**Estimate per gate** [JUDGEMENT on run counts, durations and the multipliers marked]:
- G1, collisionless monoenergetic scan at N = 10^4: 8 models x 2 perturbation signs x
  400 M on the static dx = M/4 mesh (stop once alpha_c < 0.3): 16 x 400 x 3.71 s =
  6.6 card-h. King b = 0.1 and b = 1 scouting (needs C-pre-4 data in the code):
  6 runs x 1000 M (the stability criterion of 2105.05556, risk 4) x about 4 s per M
  (assumed equal to the static dx = M/4, L = 1024 M setup) = 6.7 card-h. Total about
  13 card-h, inside the 20 GPU-hour allotment.
- G2, three-way convergence: N = 10^5 and 10^6 for 3 models x 2 signs x 400 M at about
  4.0 and 4.4 s per M: 5.5 card-h; dx = M/8 over the core for 2 models x 2 signs, at an
  assumed 8 times the M/4 cost (finest level 8 times the cells and half the step,
  [JUDGEMENT]): 13 card-h; boundary or gauge: about 2 card-h; collisional budgets in
  curved spacetime: about 2 card-h with an assumed collision cost below the push cost.
  About 23 card-h per family, about 45 for monoenergetic plus King b = 0.1. Exceeds the
  allotment: request to raise it, or split G2 over two allotments.
- G3, mass fraction against Kn: 7 values of Kn_c (infinity, 100, 10, 3, 1, 0.3, 0.1) x
  2 particle numbers x 2 collision sub-steps for one King model, about 1000 M each on an
  adaptive mesh at an assumed 20 s per M with 10^6 particles and collisions: 28 x 1000 x
  20 s = 156 card-h (about three days of both cards); half of it for the minimum
  version (one particle number pair at three Kn values).
- Processors: the reference solutions and analysis of this package take seconds
  (runs ...115344, ...115348, ...115400: 3.3, 9.0, 3.4 s on one core).

## 9. Work plan after G0 (for the lead) [JUDGEMENT]

1. G1 collisionless scan of the monoenergetic family on the existing executable (no core
   work), with growth-rate extraction from alpha_c(t) and mass radii.
2. C-pre-4 initial data: sample the King family (b = 0.1, b = 1) as particles in
   isotropic coordinates with the Hamiltonian-constraint solve of the first paper
   (`problems/ic/make_ic.py` route, a table for `nrpic_cf`); the solver of this package
   gives the profiles; cross-check against `tracks/C-sidm/gravothermal/` (independent
   implementation by the sibling helper).
3. C-pre-1 and C-pre-2 as specifications for core (decision 0010), with the requirements
   of section 7.1 as acceptance numbers.
4. Request core's view on the GR-hydro (dyn_grmhd + Z4c) Kn -> 0 reference run of the
   same King model.

## 10. Not done in this package, open items

- C-pre-1 to C-pre-4 themselves (specifications, reference tests, initial data): other
  packages.
- No AthenaK run was made here; every simulation number is from the first paper's logs.
- Collision cost: unmeasured; G2 and G3 estimates rest on an assumed multiplier.
- [TO VERIFY] the adiabatic index used by 2601.17117 in the relativistic stage (only the
  non-relativistic value 5/3 is stated, SIDM_MS.tex:344); its code is public but outside
  the allowed fetch route.
- [TO VERIFY] Shapiro and Teukolsky 1985/1986/1992 statements quoted second hand (core-only
  collapse of collisionless core-halo clusters; collapse at eps of about 0.035 and Z(0)
  of about 0.5): not on arXiv, not read.
- [TO VERIFY] Gurian 2025 (collisional Boltzmann treatment of SIDM, cited by 2601.17117
  and 2506.17641): identifier to be found by kb. (Gunther et al. 2021 is arXiv:2105.05556,
  read; section 3.4.)
- [TO VERIFY] Ipser 1969 (via 2105.05556:152): which fluid model "corresponding" means.
- Not read: the critical-collapse references of row 844 (gr-qc/9804040, gr-qc/0107076,
  1409.5176); 1707.08666 of row 843 was read only at the abstract: it constructs
  relativistic hypervirial distribution functions (static), no stability statement.
- [TO VERIFY] whether a collisionless King b = 0.1 model near threshold leaves an
  envelope (decides whether risk 3 bites).
- Brief corrections to propose through the lead's outbox: section 10 row 852 cites
  arXiv:2602.17487 as the reference for collisional relaxation, but that paper has no
  collision operator; M5 (brief 520) cites it as a continuum solver for cross-validation,
  which decision 0010 also excludes.
