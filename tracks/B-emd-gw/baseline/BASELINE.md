# Baseline of Track B: gravitational waves of a collapsing homogeneous ellipsoid in an Einstein-de Sitter background

Package B-pre-4 under decision 0010 (no standalone or outside simulation code). Owner
B-emd-gw, helper package `baseline`, 2026-11-15. Every number below carries a run id or a
paper locator; labels [VERIFIED] (read in the source or measured in a registered run),
[BACKGROUND], [JUDGEMENT], [TO VERIFY].

Registered run of all numbers: `B-emd-gw-20261115-115752-840e994` (outputs
`scratch/B-emd-gw/B-emd-gw-20261115-115752-840e994/`, copies in `results/` and `figs/`).
Predictions and outcomes: `JOURNAL.md`. Code: `scripts/ellipsoid.py` (library),
`scripts/run_baseline.py` (checks T1-T8).

Sources (kb-data, read only): arXiv:2403.15126 v1 (Dalianis & Kouvaris),
`pII_GW_Vir_C2_Arx.tex`; arXiv:2605.04487 v2 (Escrivà, Harada, Kohri, Terada, Yoo),
`main_v3.tex`. Line numbers refer to these files.

## 1. What the two papers compute

| | 2403.15126 | 2605.04487 |
|---|---|---|
| Patch | ZA ellipsoid, mass M with t_k = 4GM/3 (l. 450), axes l. 485 | ZA deformation of a glass-like zero-quadrupole sphere, M = M_k (l. 996-1002, 2183-2234) |
| Start of N-body | turnaround t_max = (2 alpha)^-3/2 t_k (l. 499, 649-664) | turnaround of the short axis (l. 1036-1060) |
| Dynamics | Newtonian, Hubble flow neglected after t_max (l. 609-612); time axis calibrated to Delta t_col = 1.8 t_max (l. 676-682) | comoving equations with the background term plus spline-softened particle-particle force of the patch particles, semirelativistic kinematics (l. 290-296, 359-460, 484-510, 694-695) |
| Quadrupole | fitted skew-normal Q_ii(t), numerical derivatives avoided (l. 1220-1235) | analytic Q''' from positions, velocities, forces and force derivatives at synchronized steps (l. 1626-1875) |
| GW | P = (G/5c^5) Q'''Q''' (l. 898); dE/dln omega = (4 pi G/5c^5) omega^7 sum|Q~|^2 with Q~ = (1/2pi) int (l. 903, 1259) | same (l. 1883, 1929-1937) |
| Zel'dovich estimate | l. 953-1076 | appendix l. 2807-3009 |
| Today | l. 905-937, 1495-1509 | l. 1943-2132, 2538-2582 |

Statements of the papers that this package reproduces or tests:

| Statement | Locator | Status here |
|---|---|---|
| ZA spectrum dE/dln omega = (32/135 pi)(c^5/G) omega (GM/c^3)^2 S abs(E_1/3(i omega t_k) - alpha^-1 E_1/3(i omega t_col))^2, S = sum alpha^4 - sum alpha^2 beta^2 | 2605 l. 2896-2918; 2403 l. 966-970 | derived independently; equal to rounding, both papers [VERIFIED, T1] |
| ZA peak at omega ~ 1/t_col with amplitude proportional to delta_L^(7/2) | 2403 l. 1002-1007 | slopes 3.5 and 1.5 within 0.034 [VERIFIED, T2] |
| Omega_GW proportional to sigma^(7/2), omega_peak to sigma^(3/2) | 2403 l. 1031, 1074 | single-patch version exact in the Newtonian problem [VERIFIED, T6]; the ensemble average not redone |
| f_0,peak proportional to M^-1/3 T_rh^1/3, Omega(f_peak) to M^2/3 T_rh^4/3 | 2605 l. 2574-2581; 2403 l. 1500-1509 | exact with constant g_* [VERIFIED, T7] |
| t_k/t_rh = 21.03 (M/M_sun)(T_rh/GeV)^2, T_rh < 0.218 Theta^-1/2 (M/M_sun)^-1/2 GeV | 2605 l. 2539-2558 | 21.027 and 0.2181 [VERIFIED, T7] |
| Shell crossing along x at t/t_k = 22.536, along y at 29.097 (alpha ~ 0.111) | 2605 l. 2277-2279 | literal model B 22.77, 29.12; embedded model A 24.25, 31.40 [VERIFIED, T5] |
| f_peak ~ 4e-9 Hz (M/M_sun)^-1/3 (T_rh/GeV)^1/3, Omega_peak ~ 1e-6 sigma^7/2 (...) | 2403 l. 1500-1509 | f within 2.2-2.9 for t_e = 28-42 t_k; Omega off by 144-392 [VERIFIED numbers, cause TO VERIFY, T7b] |

Two slips found in passing: the t^2 term of the ZA quadrupole of 2403 (l. 959-961) is
1/alpha times the term implied by its own axes (l. 485) [VERIFIED symbolically, T1d]; it
does not radiate (d^3 t^2/dt^3 = 0), so no GW result depends on it. "<t_col> ~ 28 H_k^-1"
(2403 l. 1481) is 0.9 sigma^-3/2 t_k = 28.5 t_k, i.e. 19 H_k^-1 [JUDGEMENT: unit slip].

## 2. The semi-analytic baseline

Units G = c = 1, t_k = 1, a = (t/t_k)^(2/3), H_k = 2/3, R_L = c/H_k = 3/2 (physical
radius of the Lagrangian sphere at a = 1), M = c^3/(2 G H_k) = 3/4, rho_b = 1/(6 pi G t^2)
(2605 l. 996-1002, 2149-2156; 2403 l. 446-451, 485).

Zel'dovich ellipsoid (ZA): R_i = a R_L (1 - a lambda_i), lambda = (alpha, beta, gamma)
(2605 l. 2831-2838). With Q_ii = (M/15)(3 R_i^2 - sum_j R_j^2) (l. 2866-2875):

    Q_ii = (M R_L^2/15) [ -2 (t/t_k)^2 (3 lambda_i - sum lambda) + (t/t_k)^(8/3) (3 lambda_i^2 - sum lambda^2) ]
    Q'''_ii = (80/27) (M R_L^2/15) t_k^(-8/3) (3 lambda_i^2 - sum lambda^2) t^(-1/3)
    E(t_1, t_2) = (8/15) M c^2 S [ (t_2/t_k)^(1/3) - (t_1/t_k)^(1/3) ]
    dE/dln omega = (G omega/(5 pi c^5)) sum_i |Q'''_ii~(omega)|^2,
    int_t1^t2 t^(-1/3) e^(-i omega t) dt = t_1^(2/3) E_1/3(i omega t_1) - t_2^(2/3) E_1/3(i omega t_2).

The linear part of the deformation (the t^2 term) never radiates in EdS; only the
quadratic term does [VERIFIED, derivation checked in T1]. On [t_k, t_col], t_col =
alpha^-3/2 t_k, this is the formula of both papers [VERIFIED, T1a-c].

Homogeneous-ellipsoid equations (the "ordinary differential equations" of the package):

    R_i'' = f_i R_i,  A_i = (2/3) R_1 R_2 R_3 R_D(R_j^2, R_k^2, R_i^2) (Carlson), sum A_i = 2,
    rho_p = 3M/(4 pi R_1 R_2 R_3),
    model A (embedded):  f_i = -(4 pi G/3) rho_b - 2 pi G (rho_p - rho_b) A_i
    model B (literal 2605.04487): f_i = -(4 pi G/3) rho_b - 2 pi G rho_p A_i
    model C (static, 2403.15126): f_i = -2 pi G rho_p A_i

started from the ZA state at t_turn = (2 alpha)^-3/2 t_k. Model A is the overdensity
rho_p - rho_b inside the current ellipsoid on top of the uniform background, the standard
isolated-ellipsoid model [BACKGROUND: Icke 1973, White & Silk 1979; not fetched]. A cold
homogeneous ellipsoid with a linear velocity field stays homogeneous and passes through
each pancake (R_i -> -R_i): an exact, singular Vlasov-Poisson solution, unstable to any
departure from the affine flow [BACKGROUND]. Up to the first crossing the ODE is therefore
the zero-noise, zero-softening limit of the N-body runs; after it the continuation is
formal (no violent relaxation). Q''' is computed from R, R', R'' and the jerk (force
differentiated along the flow by a complex step), not by differencing Q.

Exact self-similarity [VERIFIED, T6]: with the start at t_turn the Newtonian problem has
one time scale, t_turn, so at fixed beta/alpha, gamma/alpha

    E_GW(t_turn -> t_x) = F(beta/alpha, gamma/alpha) M c^2 (2 alpha)^(7/2),
    omega_peak = w / t_turn,  t_x = tau_x t_turn,

with F = 0.0969 (A), 0.1185 (B), 0.0946 (C), tau_x = 2.544, 2.389, 2.502 for the shape of
the 2605 benchmark (spread over alpha = 0.01-0.3 below 3e-13). This is the single-patch
origin of the delta^(7/2) and sigma^(7/2) laws. A comoving softening length keeps the
symmetry; what breaks it is relativity. With R(t_turn) ~ (t_turn/t_k)^(2/3) c t_k:
GM/(R c^2) ~ (t_k/t_turn)^(2/3) ~ alpha and (v/c)^2 ~ (R/c t_turn)^2 ~ alpha, so the
relativistic correction to E_GW should start at relative order alpha [JUDGEMENT; the
prediction that the code comparison tests].

## 3. Results (run `B-emd-gw-20261115-115752-840e994`)

| Check | Result | Figure |
|---|---|---|
| T1 ZA closed form | ratio to 2605 and 2403 formulas 1 (symbolic); Fourier sum of sampled Q''' within 6.7e-5; Parseval within 2.1e-4 | `figs/t1_za_spectrum.png` |
| T2 ZA scalings | slopes 3.5 (E), 3.5 (peak), 1.5 (omega) within 0.034 for delta_L <= 1e-2; drift at large delta_L (E slope 2.83 at 0.57) | `figs/t2_za_scaling.png` |
| T3 ODE sanity | sum A_i = 2 and R_D vs quadrature to 1e-15; sphere reproduces the top hat to 1.9e-7 | `figs/t3_sphere_and_shape.png` |
| T4 Q''' and energy | stencil agrees to 5e-7 farther than 0.2 t_turn from crossings (h^2 truncation); within 0.2 t_turn the stencil is too coarse (predicted 1e-5 everywhere: failed as written). E(t_turn -> t_x) = 5.03e-4 (A), 6.15e-4 (B), 4.91e-4 (C) M c^2; ZA [t_turn, t_col] 5.15e-5: ratio 9.8 (A), 12.0 (B) | `figs/t4_t5_axes_quadrupole_power.png` |
| T5 crossing times | x: ZA 26.96, A 24.25, B 22.77, C 23.85 (paper 22.536); y: ZA 57.9, A 31.40, B 29.12, C 32.04 (paper 29.097) | same |
| T6 self-similarity | exact to 3e-13 | `figs/t6_self_similarity.png` |
| T7 redshift | slopes exact; 21.027 vs 21.03 | `figs/t7_redshift_scalings.png` |
| T8 box | comoving peak wavelength 3.56 R_L (A), 3.33 R_L (B) = 2.2 and 2.1 V_k^(1/3); proportional to alpha^-1/2 | `figs/t8_box_and_spectra.png` |

Reading of T5 [JUDGEMENT]. Model B, the literal content of 2605.04487 (the background
term of its comoving equation, l. 290-296, plus the force of all patch particles, l.
484-490, and no matter outside the patch, l. 695), matches the two quoted times to 1.0 and
0.1 percent; the embedded model A is 8 percent later. Since the patch carries the full
mass of its Lagrangian sphere (l. 1000-1002), model B counts the background density inside
the patch on top of the patch matter; in linear theory it would not reproduce the growing
mode the initial data assume. Model B radiates 22 percent more than A up to the first
crossing. Not settled: the sigma = 0.01 snapshot times of the same shape (file names l.
2654-2659, not described as events) scaled by t_turn fall between A and B. Consequence: a
code run with a consistent background (section 4) should not be expected to reproduce the
2605.04487 times better than about 8 percent, and its comparison should be made with
model A, quoting model B as the reading of the paper.

Model C against 2403.15126: Delta t_col/t_max = 2.37, 1.38, 2.62 for its three benchmarks
(l. 719-721) against its calibration 1.8 (l. 680): no large systematic offset, a
configuration-dependent one of -23 to +46 percent [VERIFIED numbers; whether that paper
rescales each configuration: TO VERIFY].

## 4. The same quantity from the code

### 4.1 What can be compared (T8)

The peak of the single-patch spectrum has a comoving wavelength 2 pi c/(a(t_e)
omega_peak) = 3.6 R_L (model A, 2605 benchmark, alpha = 0.111), growing as alpha^-1/2:
6.8 R_L at alpha = 0.03 [VERIFIED, T8]. The papers' population model puts one patch in
each smoothing volume V_k (2605 l. 2032-2041, 2069-2117), a periodic box of side
V_k^(1/3) = 1.61 R_L. Such a box has no mode at the peak: its fundamental lies at twice
the peak frequency (dotted line in `figs/t8_box_and_spectra.png`). Two consequences
[JUDGEMENT]:
1. The quadrupole-formula energy of one patch is compared with the code only in a box
   that holds several peak wavelengths: L >= 3 x 3.6 R_L ~ 11 R_L at alpha = 0.11 (one
   patch in about 300 V_k, the remainder background), or in an asymptotically flat run.
2. In the V_k box (and in the boxes of `cosmo/`) the comparison is made wave number by
   wave number between two runs of the code that differ only in gravity, not against the
   quadrupole formula.

Box energy relation for item 1: after the emission, waves redshift as 1/a, so
a(t) E_box(t) = int P_GW(t') a(t') dt', with E_box = rho_GW a^3 L^3 (physical volume)
[JUDGEMENT, derived; valid when L is several wavelengths and the images add incoherently].

### 4.2 (i) Newtonian reference mode (core, branch `core/newton`)

State read with `git show core/newton:tracks/core/interfaces/newtonian_mode.md` (commit
0b51695): sections 1-2 only. The mode reuses the multigrid module for the potential of the
same particles and clouds; periodic meshes subtract the mean source, isolated meshes use
the multipole boundary, which works on this tree (second order, runs
core-20261115-112129-b7b431d and -112130-b7b431d) [VERIFIED by reading]. The design of the
mode (section 3 onward) is not yet written, and nothing there yet provides a quadrupole
diagnostic.

What Track B needs from the mode (request R1 in `README.md`):
- History output every `n` cycles at synchronized states: time, a(t), selected mass, the
  centroid, Q_ij, Q'_ij, Q''_ij of the particles of a chosen species (patch = species 0,
  background = species 1; the particle format already carries species, `docs/FORMATS.md`
  line 44), in physical coordinates r = a x relative to the centroid, exactly as 2605 l.
  1609-1645 define them.
- Q'''_ij either from the jerk (time derivative of the interpolated acceleration along the
  particle, as 2605 l. 1741-1866) or, simpler, from a centred difference of Q''_ij over
  one step (one derivative of a smooth series; T4 shows that a five-point stencil on Q
  with h = 5e-4 t_turn is still off by 6e-4 of max|Q'''| within 0.2 t_turn of a
  crossing).
- P_GW = (G/5c^5) Q'''Q''' in the same record.

Tests of the mode against this package (acceptance numbers from run
`B-emd-gw-20261115-115752-840e994`, 2605 benchmark alpha = 0.11122237):
- N1 static isolated ellipsoid (model C): ZA state at t_turn = 9.5316 t_k, no background,
  multipole boundary. Expect x crossing at 23.852 t_k, y at 32.036, E(t_turn -> t_x) =
  4.91e-4 M c^2, within the softening and particle-number errors, converging as the
  softening falls.
- N2 embedded ellipsoid (model A): the same patch inside background particles of density
  rho_b in a periodic box of side L, mean removed. Expect 24.25 and 31.40 t_k and
  5.03e-4 M c^2 as L/R_L grows (periodic images enter as (R/L)^3 [JUDGEMENT]).
- N3 self-similarity: alpha = 0.05, 0.1, 0.2 at fixed ratios, E/(M c^2 (2 alpha)^3.5)
  constant (0.0969) to the discretization error. A trend with alpha in the Newtonian mode
  is a fault of the run, not physics.

### 4.3 (ii) Full relativity with gw_diag

The relativistic run uses the same particles in `nrpic_cosmo` with Z4c, cosmological
lapse and periodic box (`cosmo/README.md`). Initial data: the linear-start route of
`cosmo/ic/make_field.py` (Newtonian density field on the mesh, growing mode, constraint
solve) with a delta_N field whose Zel'dovich map is the ellipsoid of the papers, started
early (delta << 1) rather than at turnaround so that the linear dictionary of the tool
applies [JUDGEMENT; the field generator for a compensated ellipsoid is not written:
request R3]. The Newtonian reference starts from the same particle file, as in `cosmo/`.

Quantities from the metric (`tracks/B-emd-gw/gw_diag/gwdiag/`, package B-pre-3):
- `tt.tt_from_adm(gamma, K, grid)` -> h^TT_ij(k, t) and its normal-time derivative,
  with h = conformal metric minus delta, so no scale factor enters;
- `tt.gw_spectrum(...)` -> rho_GW(k) (kinetic, gradient, total), `tt.helicity_spectrum`;
- `weyl.electric_magnetic`, `weyl.psi4` for a gauge-invariant local check.
Quantities from the particles of the same run: Q_ij from snapshots (`part.NNNNN.bin`:
x^i, u_i, m, species) for the matter-side comparison with run (i); coordinate positions
in the code's gauge differ from Newtonian ones at order alpha [JUDGEMENT].

Comparisons, wave number by wave number:
- G1 matter side: Q_ij(t) of the patch in GR against the Newtonian mode, same data; the
  difference should scale as alpha (section 2).
- G2 field side: h^TT(k, t) of GR against the linear tensor equation in the same box
  driven by the TT part of the Newtonian stress of run (i) (the weak-field equation of
  arXiv:1604.06065 that scope check 2 used, `scope/JOURNAL.md`; its exact form beyond
  the quasi-static limit: TO VERIFY), at the box wave numbers.
- G3 energy (only in the large box of 4.1): a(t) E_box(t) from rho_GW against
  int P_GW a dt from the Newtonian mode's quadrupole history.

### 4.4 Run pairs

| Pair | Newtonian mode (i) | GR with gw_diag (ii) | Purpose |
|---|---|---|---|
| P1 | N1, static isolated cold spheroid from rest | `nrpic_cf` spheroid (time-symmetric, prolate only, `athenak/src/pgen/nrpic/nrpic_cf.cpp` l. 192-198), Psi4 extraction (`athenak/src/z4c/z4c_wave_extr.cpp`; usage TO VERIFY) | quadrupole formula in a true wave zone; ODE numbers from rest still to be produced (open item) |
| P2 | N2, V_k box (L = 1.61 R_L), alpha = 0.11 | same data, `nrpic_cosmo` | G1, G2 in the papers' box |
| P3 | N2, large box L = 11 R_L, alpha = 0.11 | same | G3, the energy against the quadrupole formula |
| P4 | N3, alpha = 0.05, 0.1, 0.2 | same, alpha = 0.05, 0.1, 0.2 | relativistic correction against alpha (predicted linear) |
| P5 | particle number and softening scan of P2 | the same scan | both modes converge before they are compared |

Card time and resolution are not estimated here (no measurement in this package); the
throughput of `cosmo/` runs is in `scope/scripts/regime_estimates.py`.

## 5. The dropped weak-field comparison with gevolution

Decision 0010 drops running gevolution (arXiv:1604.06065), which section 10 of the brief
lists for the multi-code row (weak-field regime: gevolution, GRAMSES, fluid NR;
arXiv:2003.08014, 1908.05683). What is lost: an independent implementation, with its own
discretization, particle-mesh scheme and initial data, of the weak-field relativistic
equations including the vector (frame dragging) and the second-order tensor sector, so
errors shared by our two modes (deposit, interpolation, initial-data generator) cannot be
exposed by a code that shares none of them. How the row is covered instead: (a) the
Newtonian reference mode inside AthenaK isolates the effect of the gravity solver with
everything else identical, and the independent spectral particle-mesh code in
`cosmo/newton/pm.py`, which core keeps as a check of the mode, supplies a second Newtonian
implementation; (b) the weak-field tensor equation of 1604.06065 is used analytically
(scope check 2) and as the driven reference of comparison G2; (c) published results:
`cosmo/` has redone East, Wojtak & Pretorius (1908.05683; C2-C4), Daverio, Dirian &
Mitsou (1904.07841; C5) and the GRAMSES initial conditions of Barrera-Hinojosa & Li
(2001.07968; C6) (`cosmo/README.md` l. 4-6, `cosmo/TESTLOG.md`) [VERIFIED by reading].
The task statement says 2003.08014 is also already compared in `cosmo/`; I find no such
comparison (no file under `cosmo/` names it; its source is in
`kb-data/raw/arxiv/2003.08014/v2/src`). Its published code-comparison results
(gevolution, GRAMSES, the Einstein Toolkit and CosmoGRaPH on a solution dominated by
gravitomagnetism, compared through intersecting light rays; `draft.tex` l. 77, 285)
[VERIFIED by reading] are therefore still to be compared (request R4); until then
gevolution is covered only indirectly.

## 6. Not done, open

- Ensemble averages (Doroshkevich, BBKS) and the <t_col> ~ 0.9 sigma^-3/2 t_k of 2403 l.
  1479: not redone (statistics, not needed for the single-patch baseline).
- The Omega prefactor of 2403 l. 1501 is not reproduced (factor 144-392); cause open.
- Whether 2605.04487's code is model B: inferred from two quoted times, contradicted
  weakly by snapshot names; can be settled only by its authors' code or by the code of
  this repository in Newtonian mode with both background treatments (N2 with and without
  the subtraction).
- ODE reference numbers for the from-rest prolate spheroid (pair P1): one call of the
  library with zero initial velocity; not run.
- The Newtonian mode, its diagnostics and the ellipsoid field generator do not exist yet:
  sections 4.2-4.4 are specifications.
