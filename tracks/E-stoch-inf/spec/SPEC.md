# Reproduction specification: stochastic inflation in numerical relativity (E-pre-1)

Owner E-stoch-inf; written by the E-pre-1 helper on 2026-11-15. Target: the slow-roll and
ultra-slow-roll (USR) test cases of Launay, Rigopoulos and Shellard, arXiv:2512.14649,
rebuilt in this repository's AthenaK (decision 0010; decision 0004 settled). This file says
what the papers evolve and report, with locators, what they leave open, and what the
reproduction must check. Labels: [VERIFIED] read in the source at the locator (or checked by
a registered run here), [BACKGROUND] standard result not re-checked, [JUDGEMENT] our
inference or recommendation, [TO VERIFY] open.

Locators are `file:line` in the fetched sources (`kb-data/raw/arxiv/<id>/<v>/src/`):

| Key | arXiv | Version, file | What it supplies |
|---|---|---|---|
| P1 | 2512.14649 | v2, `PRD_v2.tex` | the stochastic NR code ISTORIz, both test cases (the target) |
| P0 | 2401.08530 | v2, `Stochastic_Inflation.tex` | derivation of the stochastic ADM and BSSN sources |
| P2 | 2502.06783 | v3, `main_V2PRD.tex` | STOIIC: background fixing, Bunch-Davies data, geodesic-gauge initial data, random draw, extraction |
| TH | 2610.32592 | v1, `chap_SINR.tex`, `chap_SIGR.tex`, `chap_QCl.tex`, `appendix.tex` | Launay's thesis: the same material with corrections (marked `\ylg`/`\ylc` in the source), the noise integration per Runge-Kutta stage, validity of classicality |
| BZ | 2606.14853 | v2, `Manuscript.tex` | Barker, Gladwyn, Zell: freezing of super-horizon modes fails without metric perturbations; validity criterion for FLRW lattices |

Reference computations of this package (scripts in `ref/`, figures in `fig/`, journal in
`JOURNAL.md`): runs E-stoch-inf-20261115-122806-ef0d039 (background and mode functions),
-122934-9ac98d8 (random-draw normalisation), -123146-82d2fd4 (initial data against the
linear constraints), -123236-2e87364 (figures, drift check).

## 1. Conventions

- Reduced Planck mass Mpl; metric `ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i - beta^i dt)(dx^j - beta^j dt)`
  in the ADM equations of P1 (P1:333-336), with the BSSN shift sign flipped (P1:671, P0:975-980).
  Irrelevant for the reproduction, which has beta = 0.
- Slow-roll parameters (P1:171, P2:233): eps_0 = H, eps_{i+1} = -(alpha_b H)^-1 d ln eps_i / dt.
  So eps1 = -dlnH/dN, and **eps2 = -d ln eps1 / dN**, the opposite sign of the common Hubble-flow
  convention: eps2 = -0.02 on the quadratic attractor, eps2 = +6 in USR (P1:528). [VERIFIED]
- K = -3H on the background; Pi = alpha^-1 (dot phi + beta^i d_i phi) (P2:113-115).
- e-folds: N with N = N0 at the Bunch-Davies time, N* at the start of the simulation, N_f at the
  end (P1 Table I, P1:419-424); simulation time cN = N - N* (the papers' <N>, measured as
  -1/2 ln<X>, P2:827). a* = 1 at N* (P1:519).
- Code units of the papers: Mpl = 100, "equivalent to having quantities in 0.01 Mpl units"
  (P2:469, P1:519). Its purpose there is to keep second-order constraint violations above
  round-off. [JUDGEMENT] Only ratios such as H/Mpl enter the physics, and relative constraint
  violations of 1e-10 are far above double-precision round-off in any units; the rescaling is
  not needed in AthenaK (section 2.5).
- Fourier convention of the noise: QFT ("backward") normalisation,
  `<f(x)^2> = int d^3k/(2 pi)^3 |f_k|^2` (P2:835-849, TH appendix:446-461); dimensionless
  spectrum Delta[f] = k^3 |f_k|^2 / (2 pi^2) (P1:454).

## 2. Equations evolved

### 2.1 Stochastic ADM system (continuum)

Field (P1:284-296, TH chap_SIGR:372-384):

    (1/alpha)(dot Pi + beta^i Pi_|i) - K Pi - alpha^|i phi_|i / alpha - phi_|i^|i + V'(phi) = F^-1{ S_Pi },

trace and trace-free extrinsic curvature (P1:338-350):

    dot K + beta^i K_,i + alpha^|i_|i - alpha (R + K^2) - Mpl^-2 alpha (S/2 - 3 rho/2) = F^-1{ S_K },
    dot Kt_ij + 2 alpha Kt_il Kt^l_j + beta^k Kt_ij|k - 2 beta_i^|k Kt_jk + alpha_|i|j
      - (1/3) alpha^|k_|k delta_ij - alpha (Rt_ij + K Kt_ij / 3) + Mpl^-2 alpha St_ij = F^-1{ S_Kt_ij },

with rho, J_i, S, St_ij of a minimally coupled scalar (P1:351-368). The constraints carry **no**
source (P1:378-392, P0:675-681):

    H = R + (2/3) K^2 - Kt_ij Kt^ij - 2 Mpl^-2 rho = 0,   M_i = Kt^j_i|j - (2/3) K_|i - Mpl^-2 J_i = 0.

Sources, all from one Gaussian draw (P1:297-310, 370-375):

    S_R(k)   = R_k Wddot_k + [ 2 Rdot_k + (3 - eps2) H R_k ] Wdot_k,     R_k(t) = R_k(t) alpha_k,
    S_Pi     = Mpl sqrt(2 eps1) S_R          (P1:299; TH chap_SIGR:387 writes (dot phi_b / H) S_R,
                                              equal when the field rolls towards positive phi),
    S_K      = -eps1 S_R,
    S_Kt_ij  = a^2 eps1 (delta_ij / 3 - k_i k_j / k^2) S_R.

[VERIFIED] The sources come from inserting the coarse-grained linear perturbations, all
written through R^> = W R (P1:173-218), into the linearised equations; the gauge-independence
is proven in P1 section II and in TH chap_SIGR:251-392 (P0 found it gauge family by gauge family,
P0:684). Graviton sources exist (P0:734-780) but are **not** implemented in P1 (P1:693).

### 2.2 BSSN form used by ISTORIz

Variables X = (det gamma)^(-1/3), gt_ij, K, At_ij = X Kt_ij, Gt^i, phi, Pi (P1:645-680). Sources
(P1:681-691, TH chap_SINR:44-51):

    S_K^BSSN = -eps1 S_R,   S_At_ij^BSSN = eps1 (delta_ij/3 - k_i k_j/k^2) S_R,   S_Pi^BSSN = sqrt(2 eps1) Mpl S_R,

all others (X, gt_ij, Gt^i, the constraints) zero. Note S_At = X S_Kt with X_b = a^-2 (P0:1025).
Use the BSSN equations of TH chap_SINR:22-42, which correct P1:653-662 (section 9, E1-E2).

### 2.3 The noise field R(t, x)

The alpha_k are drawn **once**, at N*; the real field R(t,x) = F^-1{R_k(t) alpha_k} is then
propagated by the real-space Mukhanov-Sasaki equation in first-order form (P1:312-320, TH
chap_SIGR:467-475, with the Laplacian of the background metric, TH line 472):

    Pi_R = 9 dot phi_b^2 / (alpha_b K_b^2) (d_0 R + beta^i d_i R),
    d_0 Pi_R - alpha_b K_b Pi_R + beta_b^i d_i Pi_R - 9 dot phi_b^2 alpha_b / K_b^2 Delta_b R = 0,

which is R'' + (3 - eps1 - eps2) R' + (k/aH)^2 R = 0 in e-folds, since 9 dot phi_b^2 / K_b^2 =
2 eps1 Mpl^2 (same friction factor as TH appendix:530) [JUDGEMENT: checked by hand; the
reference run integrates the e-fold form]. Its coefficients define three levels of
"stochastic backreaction" (P1:783-790, TH chap_SINR:264-274): level 0 Friedmann background
(the standard "Starobinsky approximation", noise precomputable), level 1 box averages, level 2
local values (phi_b -> phi(t,x), K_b -> K(t,x), alpha_b -> alpha(t,x), beta_b -> beta(t,x),
P1:323). The validation runs had backreaction "switched on" (P1:520), which P1:487 calls level 2;
switching it off changes the spectrum by at most about 1e-4 relative (P1:520, Fig. 9 at
P1:777-781). [VERIFIED]

### 2.4 Where and how the noise enters the update

[VERIFIED] At each Runge-Kutta **substep** (TH chap_SINR:68, correcting "each RK4 time step" of
P1:489): (a) Fourier transform R and dot R; (b) integrate the sources over the step with the
window integrated exactly and R, dot R frozen (TH chap_SINR:72-80):

    int_t^{t+dt} O_X S_R du ~ O_X(t,k) { R_k(t) [Wdot(t+dt) - Wdot(t)] + [2 Rdot_k(t) + (3 - eps2) H R_k(t)] [W(t+dt) - W(t)] },

with O_X the prefactors of section 2.2; (c) inverse transform; (d) add to each right-hand side
of the discretised BSSN. The integral is read as Stratonovich because the noise has a finite
correlation time (TH chap_SINR:81). Constraints are then satisfied to O(noise^2) (P1:496).
Time stepping RK4 (P1:480, P1:698-711).

[JUDGEMENT] What the papers do not fix (section 8, U6) is whether the increment above is
divided by the step before entering a right-hand side, and over which interval it is taken at
a substep. The reproduction should not inherit this: with alpha_k drawn once and a smooth
window (s = 5), the source is a **smooth deterministic function of time** for each
realisation, so the system is a random PDE, not a stochastic PDE driven by white noise.
Evaluate the source **rate** S_X(t_s) at the stage time t_s of every stage, with Wdot and
Wddot in closed form (section 3). The integrator then keeps its order for each realisation;
P1:711's remark that RK4 degrades to Euler-Maruyama convergence applies to white noise only
(test A6 of section 7 checks this).

### 2.5 Mapping onto this repository's AthenaK

- Formulation: Z4c with `use_z4c = false` zeroes the Theta right-hand side, which gives BSSN
  (`athenak/src/z4c/z4c_calcrhs.cpp:646`, option at `z4c.cpp:159`); constraint damping off:
  `damp_kappa1 = damp_kappa2 = 0` (defaults, `z4c.cpp:131-132`). Kreiss-Oliger off (`diss = 0`,
  P1:512 footnote "not deployed"). [VERIFIED code]
- AthenaK's K-hat equals K when Theta = 0; the sources map to rhs.vKhat += S_K, rhs.vA_dd +=
  S_At_ij, and the new scalar's Pi equation += S_Pi. chi of AthenaK is X of the papers
  (chi_psi_power = -4). With alpha = 1 the ADM placement (source of (1/alpha) dot Pi, dot K)
  and the BSSN placement (source of d_t Pi, d_t K) coincide; under any other lapse the sources
  carry a factor alpha and the window runs in background proper time. [JUDGEMENT: for core to
  confirm against z4c_calcrhs.cpp]
- Geodesic slicing and zero shift: `lapse_oplog = 0`, `lapse_harmonic = 0`, `lapse_volume = 0`,
  `lapse_kdriver = 0`, `shift_Gamma = 0`, `shift_eta = 0` with alpha = 1, beta = 0 initially;
  then rhs.alpha = lapse_advect beta.d alpha = 0 and rhs.beta = 0 (`z4c_calcrhs.cpp:687-717`).
  [VERIFIED code]
- Stencils: nghost = 4 gives sixth-order centred differences (`utils/finite_diff.hpp:24-40`:
  NGHOST 2, 3, 4 -> orders 2, 4, 6), matching "6th order" of P1:512. [VERIFIED code]
- Units: AthenaK couples matter with 8 pi (G = 1; `z4c_calcrhs.cpp:676`). With G = c = 1 and the
  time unit 1/H*, map phi_code = phi / (sqrt(8 pi) Mpl), V_code(phi_code) = V(phi) / (8 pi Mpl^2 H*^2),
  t_code = H* t, x_code = H* x (a* = 1); then 3 H_code^2 = 8 pi (phi_code'^2/2 + V_code) and the
  Klein-Gordon equation keep their form, and the box of section 5 has L_code = 2 pi / sigma.
  R is dimensionless and unchanged. [JUDGEMENT: checked by substitution by hand, not run]
- Integrator: AthenaK's `rk4` is the low-storage RK4()4[2S] of Ketcheson (2010)
  (`driver/driver.cpp:144-175`), not classical RK4, and the Z4c right-hand side reads
  `pmesh->time` for every stage (`z4c_calcrhs.cpp:44`). A time-dependent source needs the
  stage abscissae c_s of that scheme. [VERIFIED code; request to core]
- Scalar field, sources and FFT: none existed on `main` when this was written (CLAUDE.md "What
  exists"). Update by the lead, 2026-11-15 14:00Z: `core/scalar-field` (836ac86, not yet
  merged) has the field (`athenak/src/scalar_field/`), sources through `Tmunu::tmunu_tot`, the
  stochastic hook with the kicks of 2.2 and the window derivatives of section 3, mode
  functions integrated in lockstep with the RK stages, and the noise synthesised without an
  FFT (DESIGN_REVIEW 6.2); level 2 backreaction and the initial slice of 5.3 are not there.
  [VERIFIED by reading the source; tests: owner JOURNAL, check L-U]

## 3. Window function

    W_k(t) = (1/2) {1 + tanh[ s ln(k_sigma(t)/k) ]},   k_sigma(t) = sigma a(t) H(t),   s = 5.0,  sigma = 1

(P1:503-506, P1:519; TH chap_SINR:91-94, 133). W_0 = 1, W -> 0 for k -> infinity (P1:177). With
x = s ln(k_sigma/k) and d ln k_sigma/dt = H (1 - eps1), dot eps1 = -H eps1 eps2 (Launay sign):

    Wdot  = (s/2) sech^2(x) H (1 - eps1),
    Wddot = (s/2) sech^2(x) { -2 s tanh(x) H^2 (1 - eps1)^2 + H^2 eps1 (eps2 - 1 + eps1) }.

[JUDGEMENT: derived here, not in the papers.] W rises from 0.05 to 0.95 while ln k_sigma
changes by 2 artanh(0.9)/s = 0.59, i.e. in about 0.6 e-folds. The papers call s "arbitrary"
and expect no late-time effect for windows meeting the conditions of Winitzki and Vilenkin
(P1:506 footnote); the sharp alternative Theta(k_sigma - k) is the classic choice (P1:177,
P0:1040-1042). A smooth window plus Fourier-space draws makes the noise non-Markovian
(P1:507, TH chap_SINR:96-97). Which a and H define k_sigma (Friedmann, box mean or local) is
not stated (U7); level 0 uses the Friedmann values.

## 4. Gauge

Geodesic (synchronous) slicing, alpha = 1, beta^i = 0 (P1:483, P2:490), with the residual
gauge freedom fixed by chi_0 = E_0 = 0 at t* (P2:270-277, TH appendix:420-442). No AMR, no
CCZ4 damping, periodic boundaries (P1:483, P2:488). P2 notes the geodesic gauge must fail at
collapse (crossing of free-fall observers) but shows the X contrast stays perturbative over
these runs (P2:770). [VERIFIED]

## 5. Initial data, lattice and random draw

### 5.1 Background (STOIIC)

The Friedmann system (P2:188-198, rewritten in e-folds at P2:413-423) is integrated from N0 to
N* and on to N_f. Two ways of fixing it (P2:397-410):

- potential-position fixing (quadratic case): for V = lambda phi^p,
  phi0 = -|(3 - eps1) p Mpl / (sqrt(2 eps1)(eps2/2 + eps1 - 3))|,
  lambda = |sqrt(2 eps1)(eps2/2 + eps1 - 3) / ((3 - eps1) p Mpl)|^p Mpl^2 H0^2 (3 - eps1) (P2:399-405),
  with eps2 = -2 eps1 on the attractor; dphi/dN = +sqrt(2 eps1) Mpl (field rolls "from left to
  right", P2:100);
- H0 fixing (inflection case): phi0 given, slow-roll velocity -Mpl^2 V'/V, H0 from the Friedmann
  constraint (P2:408). The text writes "dot phi_0"; dimensionally it is dphi/dN [JUDGEMENT],
  and that reading reproduces P1's Fig. 1 (section 6).

### 5.2 Lattice (P1:509-512, TH chap_SINR:99-102)

N cells per side, L = N dx, dk = k_min = 2 pi / L; available norms k = dk sqrt(a^2 + b^2 + c^2),
(a, b, c) in [0, N/2]^3. L is chosen so that the first mode enters at the start:
L k_sigma* = 2 pi. UV cutoff of the noise k_max^R = N k_sigma*/4 (n = 4 cells per shortest
wavelength), below Nyquist for the sixth-order stencils. Modes then enter over
ln(N/4) e-folds (4.16 for N = 256; "about 3.5-4", P1:522). In AthenaK code units (section 2.5)
with sigma = 1: L = 2 pi, dx = 2 pi / N.

### 5.3 Mode functions and the coarse-grained initial slice

- R_k and dot R_k at N* for every lattice k come from the Mukhanov-Sasaki equation solved
  with `oscode` from Bunch-Davies data at N0 (P1:485, P2:454-459). The papers recommend
  N* - N0 >= 2 (P2:457); the form of the Bunch-Davies data is not written (U4).
- The fields at t* are the linear geodesic-gauge data of P2's initial-condition equation (P2:316-329, label
  eq:eqInitialConditions; called "eq. (17)" in earlier versions of this text, see the note
  under the erratum) applied to
  the **coarse-grained** amplitudes R^> = W(t*) R and dot R^> = d(W R)/dt at t* (P1:488,
  TH chap_SINR:66-67); without this the first low-k modes come out wrong (P1:488).
  W(k_min, t*) = 1/2 by the choice of L, so the lowest shell is half in at t*.
- Background part: X_b = a*^-2 = 1, gt_ij = delta_ij, K_b = -3 H*, At_ij = 0 (P2:329).

Perturbations at t* in the geodesic gauge with chi_0 = E_0 = 0 (P2:316-329), written with
Phi_B = -eps1 H a^2 k^-2 dot R (P2:251-255), Psi_B = Phi_B:

    delta phi = sqrt(2 eps1) Mpl (R - Phi_B)
    delta Pi  = sqrt(2 eps1) Mpl (dot R - dot Phi_B - H Psi_B) - eps2 sqrt(eps1/2) H Mpl (R - Phi_B)
    delta X   = 2 Phi_B,       delta gt_ij = 0,       delta At_ij = 0
    delta K   = 3 (dot Phi_B + H Psi_B) = 3 eps1 H (R - Phi_B)
    dot Phi_B = eps1 H R + eps1 (1 + eps1) H^2 a^2 k^-2 dot R      (R ddot from the MS equation)

**Erratum.** The printed initial-condition equation of P2 (P2:319-322) carries the term -sqrt(2 eps1) H Mpl Psi_G
in delta Pi, which vanishes in the geodesic gauge (Psi_G = B_G = 0, P2:490); the term the data
need is -sqrt(2 eps1) Mpl H Psi_B. The symbolic check of run E-stoch-inf-20261115-123146-82d2fd4 (`ref/ic_constraint_check.py`)
gives a linear Hamiltonian residual 4 eps1^2 H^3 a^2 k^-2 dot R with the printed form and 0 with
the form above; the momentum constraint vanishes for both, and the two expressions for
delta K agree identically. [VERIFIED by run] The lead re-derived the term from P2's own
dictionary (2026-11-15, owner JOURNAL, check L-I): delta Pi^NR = d/dt delta phi^NR - phidot_b
Psi_G (P2:308) with delta phi^NR = sqrt(2 eps1) Mpl (R - Phi_B + H chi^NR) and chi^NR =
int (Psi_G - Psi_B) dt + chi_0 (P2:262, 270); at t* with chi_0 = 0 the derivative of the
H chi^NR part gives + sqrt(2 eps1) Mpl H (Psi_G - Psi_B), the Psi_G parts cancel, and
-sqrt(2 eps1) Mpl H Psi_B remains, for any Psi_G. The printed equation drops the chi-dot term.
[VERIFIED by derivation] Since P1 and P2 report second-order Hamiltonian violations, their
code presumably uses the complete form [JUDGEMENT].

Note on the number (lead, 2026-11-19): this text and the outbox messages of 2026-11-15
called the equation "eq. (17)". In the source the equation at P2:317-327 is the 23rd
numbered equation environment (label eq:eqInitialConditions); eq:Bardeen at P2:248-256
is the 17th (count of the lead, 2026-11-19; the same count by kb, message
20261115T183741Z__to-E-stoch-inf__errata-s11-references). The PDF number is not checked
[TO VERIFY]; the locators by line are what this specification relies on.

With coarse-graining, substitute R -> W R and dot R -> d(W R)/dt in these formulas and take
dot Phi_B from the unsourced MS equation applied to (R^>, dot R^>); any pair (R, dot R) is valid
MS data, so the linear constraints still hold at t* [JUDGEMENT; TO VERIFY by core's test of the
initial data generator: linearised H and M of the generated slice must vanish to round-off at
first order].

### 5.4 Random draw and its normalisation

- One white-noise field Delta(x) on the grid, s_k = N^(-3/2) RFFTN{Delta}, so that the alpha_k
  have the statistics of P1:121-128 and Hermitian symmetry; one draw for all quantities
  (P2:463-465, TH appendix:479-483). The papers draw in real space first ("the former method",
  P2:463).
- Field with QFT amplitude f_k: **f(x) = L^(-3/2) IRFFTN{ f_k s_k } = (dk/2 pi)^(3/2) IRFFTN{f_k s_k}**
  with IRFFTN unnormalised (RFFTN{IRFFTN} = N^3, P2:837). [VERIFIED by run
  E-stoch-inf-20261115-122934-9ac98d8: measured shell ratio 0.83 +- 0.07 (13 modes) to
  1.014 +- 0.006, all within 3/sqrt(M), `fig/fig_norm.png`.] The papers print two
  mutually inconsistent prefactors, dk^(3/2) and (dk/sqrt(2 pi))^(3/2) (P2:879-882, TH
  appendix:487-491), and C = (2 pi)^(3/2) (P2:867) versus C = (2 pi)^3 (TH appendix:477); the
  printed prefactors give powers (2 pi)^3 and (2 pi)^(3/2) too large (measured 241.8 and 15.35,
  expected 248.1 and 15.75). Their spectra agree with linear theory, so their code is right
  and the text is not [JUDGEMENT].
- In this repository the amplitudes come from the counter-based generator of `core/rng`
  (Philox-4x64), keyed **by wave vector**, not by cell: one complex unit Gaussian alpha_n per
  wave vector n of a half space, stream Stream(3, 2^16 + dof), entity CellEntity(n + 2^20),
  step = epoch (0 for the frozen draw), draw 0 (`../noise/NOISE_SPEC.md` section 4,
  `../codebase/DESIGN_REVIEW.md` 6.2; core's `scalar_field_noise.cpp` on `core/scalar-field`
  836ac86 uses these keys). This gives the same realisation at every N and in every
  MeshBlock layout and needs no forward transform; real-space white noise keyed by cell (the
  papers' route, P2:463) would give a different realisation at each N. [Aligned by the lead
  on 2026-11-15 at the request L1 of the noise package; earlier text keyed by cell.]

## 6. The two test cases

| Quantity | Quadratic (SR) | Higgs inflection (USR) | Locator |
|---|---|---|---|
| V(phi) | m^2 phi^2 / 2 | Lambda v^4 phi^2 (3 phi^2 + 2 sqrt2 phi v + 6 v^2) / (3 (3 phi^2 + 2 v^2)^2) | P1:405-409 |
| Parameters | eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl (at N0) | Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl | P1:411-413 |
| Fixing | potential position: m, phi0 from (eps1, eps2, H0) | H0 fixing: eps1(phi0), H0(eps1, phi0) | P1:414-417, P2:397-410 |
| N* - N0 | ~ 5 | ~ 3 | P1:419 |
| N_f - N* | ~ 8 (Fig. 1 axis ends at ~ 7.6) | ~ 10 (Fig. 1 axis ends at ~ 9.6) | P1:420, Fig. 1 |
| Lattice | N = 256, sigma = 1, a* = 1, Mpl = 100 | same | P1:519 |
| Window | tanh, s = 5 | same | P1:503-506 |
| Noise UV cutoff | k_max = N k_sigma*/4 = 64 dk | same | P1:512 |
| Backreaction | level 2 on (ablation <~ 1e-4 in the spectrum) | same | P1:487, 520 |
| Realisations | one seed per case | one | P1:779 ("All the same N=256 stochastic seed") |

Derived by the reference run E-stoch-inf-20261115-122806-ef0d039 (Mpl = 1) [VERIFIED by run]:

| | Quadratic | Inflection |
|---|---|---|
| phi0, dphi/dN at N0 | -14.0950, +0.141421 | -1.2, +0.102682 |
| lambda (m) | 1.50502e-12 (m = 1.73494e-6) | |
| H0, H* | 1.0e-5, 9.48692e-6 | 9.5902e-6, 9.36232e-6 |
| eps1, eps2 at N* | 1.1107e-2, -2.213e-2 | 1.3164e-2, -0.4307 |
| V(N*) in Mpl = 100 units | 2.690e-2 (Fig. 1: 2.68e-2) | 2.618e-2 (Fig. 1: 2.615e-2) |
| eps1 at N* + 8 / N* + 10 | 1.350e-2 | 1.008e-12 |
| USR (eps2 > 3) | none | cN = 2.53 to 6.55, eps2 max 6.000, eps1 min 9.7e-13 at cN = 8.33 |
| late eps2 | -2.69e-2 | -2.76e-2 (P1:534: -2.8e-2) |
| L (Mpl = 1 units), dk | 6.623e5, 9.487e-6 | 6.711e5, 9.362e-6 |

All values read off P1's Fig. 1 (eps1, eps2, V at both ends, the eps1 peak 2.4e-2 at cN ~ 1.6, the
eps1 minimum ~ 0.98e-12 at ~ 8.4, the eps2 crossings of 3.2 at ~ 2.5 and ~ 6.45) agree within the
reading precision of the figure, whose tick labels are rounded to two digits; the largest
difference is at the right end of the quadratic panels (eps2 -2.659e-2 against a reading of
-2.62e-2, V 2.234e-2 against 2.22e-2 at cN = 7.6) (`fig/fig_background.png`). The text's "USR from
N ~ 3.5 until N ~ 8" (P1:534) is about one e-fold later than its own Fig. 1. The field ends at
phi = -0.2798 Mpl, where |V'| is smallest (P2:579: inflection at |phi| ~ 0.28 Mpl); V' does not
change sign on the path, so the "very shallow maximum" of P1:534 is not a maximum of V. The
langevin package showed that the printed potential has an exact stationary inflection point
(a double root of V') at phi = -sqrt2 v = -0.2800 Mpl (`../langevin/README.md`); the field
creeps past it. [VERIFIED; harmless for the reproduction, which stops at N_f.] A second text
error: P1:108 writes H^2 = V/(1 - pi^2/(6 Mpl^2)) without the factor 3 Mpl^2 of the
Friedmann denominator (lead, read at the source).

## 7. Acceptance quantities

### 7.1 Reported by the papers [VERIFIED at the locators]

| Id | Quantity | Reported | Locator |
|---|---|---|---|
| P-a | box means of phi, Pi, K (and V, eps1, eps2) vs Friedmann | "perfect agreement" | P1:440, Fig. 1 |
| P-b | Delta[R^NR] vs Delta[R^MS] after the window has passed all modes | SR: linear physics recovered; USR: "excellent agreement" at complete overlap; departure from linear weaker than in FLRW lattices (2410.23942) | P1:522, 536, Figs. 3 and 5 (bins with more than 10 lattice modes) |
| P-c | R^NR extraction | subtract box background, Phi from X and gt, R^NR = Phi - <K>/(3 <alpha><Pi>) (phi - <phi>) | P1:522-526; TH appendix:513-522 (corrected factors) |
| P-d | relative Hamiltonian violation abs(H)/[H] during entry | ~ 1e-10 (second order, noise ~ 1e-5), then damped by expansion | P1:538-539, abs magnitudes P1:735-745 |
| P-e | relative momentum violation abs(M)/[M] | second order during entry; SR: briefly above at the last crossing; USR: ~ 1e-2 late, with R ~ 10 | P1:541 |
| P-f | negative control: flipping a sign of a noise term | H/[H] ~ 1e-5, M/[M] ~ 1 (first-order violation) | P1:541 |
| P-g | convergence N = 32, 64, 128, 256 with k_max/dk = 8 (about 2 e-folds of sourcing) | constraints: plateau then exponential decay, converging; spectra: abs(1 - Delta_NR/Delta_MS) decreasing with N | P1:747-773 |
| P-h | USR one-point statistics | R^NR outliers ~ 10, Delta[R] up to 0.1-1, delta Pi/Pi_b large late | P1:534-536 |
| P-i | backreaction level 2 vs 0 | <~ 1e-4 relative change in the spectrum | P1:520, 777-790 |
| P-j | anisotropic sector | Kt spectra decay after crossing in SR, comparable to isotropic in USR | P1:562-572 |

No tolerance is given for P-a, P-b or P-g (U12).

### 7.2 Acceptance for the reproduction in AthenaK [JUDGEMENT, for the owner to fix at G0]

- **A1 background**: box means of phi, Pi, K against the Friedmann reference of this package
  to 1e-4 relative over the run.
- **A2 per-mode linear check** (stronger than P-b, free of cosmic variance): with the same
  alpha_k, R^NR_k(t) / [W_k(t) R_k(t) alpha_k] - 1 below 2 percent for every lattice mode with
  k <= k_max/2 at N_f in the SR case. The sixth-order Laplacian has a dispersion error of
  3.8e-4 in k^2 at k dx = pi/4 and 1.8 percent at k dx = pi/2 = k_max dx (along an axis;
  arithmetic on the stencil coefficients, not a registered run); the noise reference should use the same discrete wave number as the
  lattice (section 10, item 3), or the tolerance at k_max is set by this error.
- **A3 freezing (section 7.3)**.
- **A4 constraints**: abs(H)/[H] and abs(M)/[M] of second order during entry (within a factor
  10 of P-d, P-e), and the negative control P-f reproduced.
- **A5 spatial convergence**: P-g repeated; constraint ratios converge at sixth order before
  the floor.
- **A6 temporal convergence** (not in the papers): fixed seed, Courant factor halved twice; the
  difference must fall at the order of the integrator, since the forcing is smooth (2.4).
- **A7 reproducibility** (brief M11, row "Reproducible random numbers"): same seed, different
  MeshBlock layout, rank count and restart time give the same fields to FFT round-off.
  (With the separable synthesis of core the fields are bit-identical across MeshBlock
  layouts and restarts: `../noise/NOISE_SPEC.md` A11, A12.)
- **A8 one-point statistics against stochastic delta-N** (added by the lead at the request
  of the langevin package): a variance of R^NR or delta-N on the 256^3 lattice is compared
  with the **lattice sum** of the band dk to 64 dk (1.0805 times the continuum integral in the
  quadratic case, run E-stoch-inf-20261115-130139-176cdd6), never with the continuum. The
  separate-universe Langevin numbers with sigma = 1 (the coarse-graining of the NR runs) are
  **not** a reference: they overestimate the variance by 42-45 percent; the reference is
  sigma <= 0.01 with an end surface at least 3 e-folds after the last noise
  (`../langevin/README.md`).

The thresholds A1-A8 and of 7.3 are fixed at G0 by the owner in
`../stage/G0/REPORT.md` section 4.

### 7.3 Criterion for the freezing of super-horizon modes

BZ show that dropping metric perturbations deforms the MS equation (BZ:177-189, 210-212):

    f'' + (k^2 - z''/z) f = (sigma_BZ - 1) 2 eps (3 + eps - 2 eta) cH^2 f,

so that on super-horizon scales in slow roll R_k^2 ~ (H(N)/H(N_exit))^4 instead of a constant
(BZ:152-155, 204-207); in USR the deviation is stronger (BZ:250). Their validity criterion
for FLRW lattices (BZ:264-283, 300, 511-534): Delta_A << 1 and Delta_gradB << 1 for the metric
perturbations implied by the field (necessary, not sufficient), and recomputing the observable
with first-order metric perturbations; a significant change means full NR is needed. eps << 1
is not sufficient (BZ:266, 340-371). BZ sample modes 7 e-folds after exit (BZ:239).

NR evolves the metric perturbations to all orders, so BZ's test is passed by construction; what
must be shown is its consequence. Reference curves of this package (run
E-stoch-inf-20261115-122806-ef0d039, `fig/fig_freezing.png`, `fig/fig_spectra.png`,
`fig/fig_drift.png`) [VERIFIED by run]:

- SR, full MS: final Delta_R = 1.010-1.012 x H^2/(8 pi^2 eps1 Mpl^2) at crossing for all
  sampled modes. The approach to the frozen value is the gradient correction, which decays as
  exp(-2 dN): the fitted drift of ln Delta over [N_k + 5, N_k + 6] is 0.0192 of that over
  [N_k + 3, N_k + 4] (exp(-4) = 0.0183); over [N_k + 3, N_f] it is 2.5e-4 to 1.9e-3 per e-fold.
- SR, deformed MS: d ln Delta/dN = -0.051 to -0.055 per e-fold (-4 eps1 = -0.046 to -0.054);
  at N_f the deformed spectrum is 0.65 (k = dk) to 0.79 (k = 64 dk) of the full one. Two
  independent forms of the deformed equation agree to 1.5e-11.
- USR: deformed/full at N_f is 8.40 at k = dk, 1.18 at 4 dk, 1.07 at 5.7 dk, 1.003 at 11.3 dk and
  1.0000 at 64 dk: only modes that left the horizon about one e-fold or more before the USR
  onset (cN = 2.53) discriminate. Full Delta_R at N_f rises monotonically to 1.017 at k = 64 dk.

Criterion for the reproduction [JUDGEMENT]:

- SR: for every lattice mode with N_f - N_k >= 6 (k <~ 7 dk), the per-mode power ratio
  |R^NR_k(N_f)|^2 / |R^NR_k(N_k + 4)|^2 must equal the full-MS ratio of the reference within
  1 percent. The FLRW (deformed) behaviour would lower it by exp(-0.051 x 4) = 0.82 or more
  for k = dk, about 20 times the tolerance. Equivalent statement: the measured super-horizon
  drift of ln Delta from N_k + 4 on must lie below 2.5e-3 per e-fold in magnitude, a twentieth
  of 4 eps1.
- USR: for the modes k <= 3 dk the NR power at N_f must agree with the full MS within 10
  percent, where the deformed equation is off by factors 1.4 (k = 2.8 dk) to 8.4 (k = dk).
- Both use the per-mode ratio with the known alpha_k, so they need one realisation, not an
  ensemble.

## 8. What the papers leave unstated

U1 Courant factor of the stochastic runs (P2 used dt/dx = 0.025 for its initial-value runs,
P2:492; TH chap_ICsim:141). U2 the exact N* - N0 ("~ 5", "~ 3"; P1:419); integers reproduce
Fig. 1. U3 the exact N_f ("~ 8", "~ 10"; Fig. 1 ends near 7.6 and 9.6). U4 the form of the
Bunch-Davies data and whether every mode starts at N0 (P1:485 says from N0 with oscode).
U5 whether the cutoff k_max is on |k| or per component. U6 how the per-step increment of
TH chap_SINR:72-78 enters a stage right-hand side (division by dt; substep interval).
U7 which a, H define k_sigma(t) under backreaction levels 1 and 2. U8 lattice or continuum
Laplacian in the real-space MS evolution of R(t,x). U9 seeds; one realisation per case.
U10 the normalisation constant of the draw (section 5.4). U11 the bin edges of the spectra.
U12 numerical tolerances for "perfect"/"excellent" agreement. U13 output cadence of P1 (P2:
15-50 checkpoints). U14 wall time, hardware and cost of the P1 runs (none reported). U15 whether
eps1, eps2 in S_R and in the prefactors O_X are local under level 2 (TH chap_SIGR:482 says one
"should probably not stop" at promoting phi, K, alpha, beta). U16 how delta K at t* treats the
coarse-graining (the printed initial-condition equation is incomplete, section 5.3). U17 treatment of the k = 0
mode of the noise (presumably excluded). U18 whether the noise sources are applied to all
lattice modes up to k_max or only to those with W not negligible.

## 9. Discrepancies and errata between the versions

E1 BSSN K equation: "-4 pi alpha (rho + S)" (P1:654, P0:1001, P2:930) mixes G = 1 into Mpl
units; TH chap_SINR:31 corrects it to (1/2) Mpl^-2 alpha (rho + S). E2 At equation:
"Mpl^-2 alpha S_ij" inside the alpha bracket (P1:655) vs Mpl^-2 S_ij (TH chap_SINR:32). E3
V'(phi_b) = (-3 + eps1 + eps2/2) H / dot phi_b (P1:267) vs H dot phi_b (TH chap_SIGR:358); the
latter is the correct one (it follows from the background Klein-Gordon equation and is used in
our T4 check). E4 S_Pi = Mpl sqrt(2 eps1) S_R (P1:299) vs (dot phi_b/H) S_R (TH chap_SIGR:387):
sign-safe form is the latter. E5 Laplacian d_i d^i (P1:317) vs Delta_b (TH chap_SIGR:472). E6
extraction factors -1/48, -1/16 and a missing 3 (P2:828-830) vs the corrected TH appendix:518-520
(re-derived here by hand from the dictionary P2:799-801, [JUDGEMENT: hand derivation, not run]:
Phi_k = (a^2 X_k - 1)/2 + (1/4) sum k_i k_j (gt_ij - delta_ij)/k^2,
E_k = -(3/4) sum k_i k_j (gt_ij - delta_ij)/k^4). E7 draw
normalisation (section 5.4). E8 delta Pi of P2's initial-condition equation, P2:317-327 (section 5.3). E9 "|H|/[H] << 1 and
|H|/[H] << 1" (P1:746, P2:550) for |M|/[M] (fixed at TH appendix:610). E10 P0's sources carry
"+ c.c." (P0:669-671, 1024-1026) while TH appendix:463 states the real stochastic expansion
adds no conjugate. E11 USR phase boundaries in P1's text vs its Fig. 1 (section 6). E12 P1:227
swaps the words lapse and shift. E13 P1:711 (Euler-Maruyama order) vs the smooth-forcing
argument of section 2.4. E14 BZ:204 writes eps = d ln H/dN (sign); the decay R^2 ~ H^4 and our
-4 eps1 drift agree.

## 10. What the reproduction needs from core (also in README.md, Requests)

1. A minimally coupled scalar field in AthenaK (phi, Pi; rho, J_i, S_ij into `tmunu`) with
   V(phi) selectable (quadratic; the Higgs-inflection form of section 6).
2. Stochastic sources on the right-hand sides of K-hat, At_ij and Pi, evaluated at the stage
   time of each RK stage (stage abscissae of RK4()4[2S]); off by default; bitwise neutral when
   off.
3. Noise generation: alpha_k from the `core/rng` white noise and a forward FFT at N*; the
   amplitudes R_k, dot R_k evolved per lattice wave vector (level 0: background coefficients
   and either k^2 or the stencil's discrete k^2; level 2 later: the real-space form of 2.3);
   per stage one inverse FFT of S_R and of k_i k_j/k^2 S_R (six components, or five plus the
   trace identity). Needs a GPU FFT (cuFFT through Kokkos or Kokkos-FFT); a single card holds
   a 256^3 run [JUDGEMENT]. Superseded (lead, 2026-11-15): no forward FFT is needed when the
   amplitudes are keyed by wave vector (5.4); the inverse transform is the per-MeshBlock
   separable synthesis of `../codebase/DESIGN_REVIEW.md` 6.2 (request R4 there), which core
   implemented.
4. Initial data at N* (section 5.3) from a background table and the R_k(N*) table that this
   track supplies.
5. Diagnostics: box means; the relative constraint magnitudes [H], [M] of P1:735-745; R^NR of
   P-c; the spectra of R^NR and of K, Kt by lattice shell; per-mode Fourier amplitudes for A2.

## 11. Resolutions, boxes, run lengths and costs

### 11.1 Reported [VERIFIED at the locators]

| Source | Runs | Box and modes | Length | Cost reported |
|---|---|---|---|---|
| P1 | SR and USR, one realisation each, GRTeclyn on GPUs (P1:480) | N = 256, sigma = 1, L k_sigma* = 2 pi, k_max = 64 dk (P1:510-519) | ~ 8 and ~ 10 e-folds after N* (P1:420); figures end near 7.6 and 9.6 | none (no wall time, no hardware beyond DiRAC, P1:591-592) |
| P1 | convergence ladder | N = 32, 64, 128, 256 with k_max/dk = 8 (about 2 e-folds of sourcing) | | none (P1:756, 771) |
| TH | quantum-diffusion runs (preliminary, unpublished) | "N = 64 realisations", N being the lattice-size symbol; sigma = 1, level 0 (TH chap_SINR:523, 564) | noise ends after ~ 3 e-folds | none |
| P2 | initial-value runs (no noise), GRChombo | typical 256^3; 1024^3 tested in GRTeclyn; quadratic sigma = 3, L = 64/H*; inflection sigma = 4, L = 32/H*; monodromy sigma = 4.5, L = 16/H*; UV study sigma = 1, L = 128/H* (P2:492, 535, 590, 691, 961) | last renders at <N> = 7.64 (quadratic) and 9.58 (inflection) (P2:448, 624) | Courant 0.025, 15-50 checkpoints, 256^3 "less than a few hours on 64 to 152 processors" (P2:492; TH chap_ICsim:141-142) |
| BZ | FLRW lattice (CosmoLattice) | USR 512^3, k_IR = 9.8e-7; SR 64^3, k_IR = 1.54e-3 (program units, BZ:482-488) | USR started 5.5 e-folds before the end (BZ:254) | none |

P1's step count: N_T = sigma N (N_cross + Delta N) / (2 pi theta), theta = dt/dx, and at most one
discrete mode enters per step if theta < n sigma / (2 pi) (= 0.64 for n = 4, sigma = 1)
(P1:714-730). [VERIFIED]

### 11.2 Estimate for AthenaK [JUDGEMENT]

Measured Z4c throughput on one A100: 2.0e7 zone-cycles/s at 128^3 with nghost = 4
(`docs/TESTLOG.md:46`), without a scalar field. Assuming 30 percent more for the scalar, the
sources and the FFTs (not measured), a 256^3 step costs about 1.1 s. With N_T from 11.1:

| Case | theta = 0.25 | theta = 0.025 (P2's value) |
|---|---|---|
| SR, 7.6 e-folds | 1240 steps, about 0.4 card-hours | 12400 steps, about 3.8 card-hours |
| USR, 9.6 e-folds | 1560 steps, about 0.5 card-hours | 15600 steps, about 4.8 card-hours |
| ladder N = 32-128 at k_max/dk = 8 | below 0.1 card-hours in total | below 0.5 |

At theta = 0.25 the window (0.6 e-folds wide) is crossed in about 100 steps
(H dt = 2 pi theta / N = 6.1e-3 per step). The track's allotment is 10 card-hours to the next
gate (decision 0006): both cases, the ladder and the temporal test A6 fit at theta near 0.25;
at theta = 0.025 the two production runs alone take most of it. A 256^3 Z4c state with the
scalar and the per-mode noise amplitudes (two complex numbers per wave vector) fits one card;
runs longer than an hour need `scripts/submit_chain.sh` and an exact restart of the noise
state.
