# JOURNAL of the work package gravothermal (C-pre-3)

Append-only, newest at the bottom. Predictions are written here before a test runs,
outcomes after it, also when the prediction failed.

Sources (fetched with `nrpic-fetch-arxiv`, read as data, never run):
- F21 = arXiv:2108.11967 v2 (Feng, Yu, Zhong), `kb-data/raw/arxiv/2108.11967/v2/src/main.tex`
- G26 = arXiv:2601.17117 v2 (Gu, Jiang, Chen, Li), `kb-data/raw/arxiv/2601.17117/v2/src/SIDM_MS.tex`

## 2026-11-15  helper gravothermal  (before any run)

What the papers use, read from the sources:
- F21 models the collapsed core as a truncated Maxwell-Boltzmann (Michie-King,
  Merafina-Ruffini) distribution, Eq. (C_distribution) at main.tex:111-116, with the
  Tolman-Klein relations at main.tex:118, the equation of state integrals at main.tex:122-139,
  the TOV system at main.tex:143-145 and the length unit at main.tex:147-153. Sequence: fixed
  b = kT(R)/mc^2, parameter w(0). Criteria: Chandrasekhar trial-function criterion
  <gamma> < gamma_cr (main.tex:208-219, derivation main.tex:403-463, with gamma = 1 + p/u,
  main.tex:173-175) and turning points dS/dw(0)|_b = 0 of S = E, B, eps (main.tex:231-254).
  Tables: main.tex:479-589 (b = 0.1, 0.2, 0.3, 0.5) and main.tex:597-624 (fine scan of the
  <gamma> = gamma_cr points, b = 0.09 ... 5.0).
- [JUDGEMENT, to be tested below] f of F21 depends on the phase-space point only through the
  Killing energy E = e^Phi (mc^2 + eps): with T e^Phi = const and (mu + mc^2) e^Phi = const,
  (mu - eps)/kT = const - E/kT_inf and E_c = (mc^2 + eps_c) e^Phi = const. So the F21 core is
  an exact static isotropic Einstein-Vlasov solution (the relativistic King / isothermal
  cluster of Shapiro-Teukolsky), and can be sampled as particles for NRPIC without change.
- G26 evolves a Misner-Sharp fluid with heat flux (Eqs. ms3-ms10, SIDM_MS.tex:309-348) and an
  ideal-gas EOS with fixed gamma = 5/3 (SIDM_MS.tex:338-344). It prints no equilibrium
  sequence of its own; for the onset of the dynamical instability it cites F21 qualitatively
  (SIDM_MS.tex:175 and :476). Its late phase is computed quasi-statically with GR kept
  (SIDM_MS.tex:457).

### Prediction P1 (row-by-row reproduction of F21 Table 1, 50 rows, four values of b)

Local quantities, which depend on (b, w0) only: eps_c(0)/mc^2, rho^(0), p^(0), v(0)/c agree
with the printed six digits (relative difference < 2e-5). Global quantities: M^ and E^_rest to
< 2e-4 relative; B^ = E^_rest - M^ and eps = B^/E^_rest to < 2e-3 relative (difference of
nearly equal numbers); R^ within 2e-3 absolute (the printed R^ values end in ...001, which
suggests a radial grid of step about 1e-3 in F21's RK4 integration); C = M^/R^ and Z(0) to
< 1 per cent. <gamma> and gamma_cr to < 3e-4 absolute.
Refuted if a whole column deviates systematically beyond these bounds (that would mean a
misread normalisation, e.g. of zeta, or of e^Phi), not by isolated rows that are internally
inconsistent in the paper (possible typos: b = 0.2, w0 = 0.05 prints C = 4.0e-4 although
M^/R^ = 4.0e-3; b = 0.1, w0 = 1.1 prints p^(0) = 1.09e-3, out of the monotonic order of its
neighbours 9.9e-4 and 4.1e-2).

### Prediction P2 (turning points and the trial-function threshold)

For b = 0.1 ... 0.5: eps has a maximum 0.0352-0.0356 at Z(0) = 0.52-0.55 (F21 main.tex:280);
B^ has a maximum (8.49e-4 at v(0) = 0.395c for b = 0.1, main.tex:286); M^ has a maximum
(3.47e-2 at v(0) = 0.225c for b = 0.1). The printed underscored rows are grid points, so my
exact maxima will sit between grid rows and have values slightly above the printed ones
(by < 1 per cent). The root <gamma> = gamma_cr lands at w0 = 4.05150 (b = 0.1), 1.73635 (0.2),
1.12526 (0.3), 0.662445 (0.5) to < 2e-3 relative, and the fine scan of Table 2 (b = 0.09 ... 5)
likewise. Refuted by a root off by more than 1 per cent in w0.

### Prediction P3 (the Killing-energy form)

Number density, energy density and pressure computed by direct momentum-space integration of
f(E) = A (e^{-E/kT_inf} - e^{-E_c/kT_inf}) at a radius with lapse e^Phi agree with F21's
I-integrals to round-off (< 1e-10 relative). Refuted by any larger difference.

### Prediction P4 (the fixed-gamma EOS of G26 along the same structures)

If the perturbations carried gamma = 5/3 everywhere (G26's EOS, SIDM_MS.tex:341), the
trial-function threshold is gamma_cr = 5/3. In F21 Table 1 gamma_cr rises past 1.639 at
w0 = 4.5 (b = 0.1), slope about 0.037 per unit w0, so I expect gamma_cr = 5/3 near
w0 = 5.0-5.5 for b = 0.1, at Z(0) about 1.0-1.2, i.e. well past both the eps maximum and the
<gamma> = gamma_cr point. Refuted if gamma_cr saturates below 5/3 along the sequence (then a
fixed-5/3 gas of this structure would never be unstable by this criterion).

### Prediction P5 (exact radial pulsation versus the trial function)

The trial function xi = r e^Phi gives an upper bound to the lowest omega^2 (Rayleigh-Ritz), so
the exact zero of the fundamental mode of Chandrasekhar's equation with Gamma = 1 + p/u
lies at smaller w0 than the trial root: for b = 0.1 between w0 = 3.0 and 4.05. Refuted
(and a bug indicated) if the exact zero lies above the trial root.

## 2026-11-15  helper gravothermal  (outcomes of runs C-sidm-20261115-120715/120717/120722-38ab057)

Runs: C-sidm-20261115-120715-38ab057 (unit tests, all pass), C-sidm-20261115-120717-38ab057
(table parse: 56 rows of Table 1, 14 of Table 2), C-sidm-20261115-120722-38ab057 (sequences).

Outcome P1 (Table 1 row by row) - holds, with three printed typos and one column off:
- M^ and E^_rest: median 1.5e-6, max 1.1e-4 relative (row main.tex:503, b = 0.1, w0 = 4.5;
  the deviation grows with central concentration, as expected from a fixed-step RK4 in F21).
- B^ max 2.4e-4, eps max 1.3e-4; Z(0) max 2.1e-5; rho^(0), p^(0), v(0) max 3.7e-6;
  <gamma> max 5.1e-6 absolute, gamma_cr max 1.6e-5 absolute. R^ max 9.9e-4 absolute: the
  printed R^ sits below the exact surface by less than one step of 1e-3 (truncation to F21's
  grid), so C printed = M^/R^(printed) is up to 0.25 per cent high.
- Typos, confirmed against the paper's own other columns: main.tex:516 (b = 0.2, w0 = 0.05)
  C = 4.0e-4 for M^/R^ = 4.0e-3; main.tex:491 (b = 0.1, w0 = 0.3) C = 1.41053e-2 for
  M^/R^ = 1.141e-2 (digit transposition, not predicted); main.tex:493 (b = 0.1, w0 = 1.1)
  p^(0) = 1.09378e-3 for 1.09e-2 (factor 10).
- FAILED part: eps_c(0)/mc^2 deviates from b w0/(1 - b w0) by up to 1.3e-4 (main.tex:498),
  above the 2e-5 I predicted for local quantities, although F21's Z(0) is consistent with the
  exact eps_c(0). Cause not established; F21 presumably evaluated this column at its first
  grid point off the centre (a shift of w by ~5e-4 there would explain it) [TO VERIFY with
  the authors' data files, which are not fetched].

Outcome P2 - holds. Exact maxima (b = 0.1): E^ = 3.47261e-2 at v(0) = 0.2279 (paper grid
3.47240e-2 at 0.225), B^ = 8.48864e-4 at v(0) = 0.3970 (paper 8.48824e-4 at 0.395),
eps = 0.0351789 at Z(0) = 0.5404, w0 = 3.1652 (paper grid 0.0351754 at Z = 0.548, w0 = 3.2).
For b = 0.1 ... 0.5, eps_max = 0.03518-0.03557 at Z(0) = 0.540-0.514 (paper: 0.0352-0.0356 at
0.548-0.522, grid values). Root <gamma> = gamma_cr: w0 = 4.05115, 1.73634, 1.12525, 0.66244
(paper 4.05150, 1.73635, 1.12526, 0.662445); Table 2 roots for b = 0.09 ... 5.0 within
1.1e-4 relative in w0, 2.1e-3 in R^ and C (grid), 2.1e-4 in Z(0), 3e-6 in <gamma>.

Outcome P3 - holds: moments of f(E) equal F21's integrals to 1.2e-14 (unit test 3).

Outcome P4 - partly refuted. Along the F21 structures gamma_cr does not rise without bound:
for b = 0.1 it peaks at 1.646 < 5/3 (w0 = 4.92, Z(0) = 1.02) and falls again, so the
trial-function criterion with gamma = 5/3 never fires for b = 0.1 (the refutation clause of
P4). For b = 0.2, 0.3, 0.5 gamma_cr = 5/3 is reached at Z(0) = 0.777, 0.752, 0.737, lower
than the 1.0-1.2 I guessed by extrapolating Table 1. The exact (FEM) fluid onset with a
fixed gamma = 5/3 does exist for every b: Z(0) = 0.779 (b = 0.1), 0.700, 0.687, 0.679.

Outcome P5 - holds. The exact fundamental mode with gamma = 1 + p/u (finite elements,
converged to 2e-5 relative between N = 800 and 1600, never above the trial value) crosses
zero at w0 = 3.5871 for b = 0.1 (inside the predicted 3.0-4.05), Z(0) = 0.635; for
b = 0.2, 0.3, 0.5 at Z(0) = 0.592, 0.584, 0.579. So the trial function xi = r e^Phi is far
from the eigenfunction of these core-halo structures: at the trial root (b = 0.1,
w0 = 4.0515) the exact omega_0^2 = -3.59 (hatted units) against -6.7e-4 for the trial.

### Prediction P6 (independent check of the FEM operator: turning-point theorem)

The operator of the FEM was checked only against F21's own closed form (eta = 1), which
comes from the same printed pulsation equation; a typo there would pass that check. For a
barotropic sequence whose perturbations obey the same EOS (polytrope p = K rho_0^Gamma,
rho = rho_0 + p/(Gamma - 1), Gamma_1 = Gamma), omega_0^2 = 0 exactly at the maximum of
M(rho_c) [BACKGROUND, Harrison-Thorne-Wakano-Wheeler]. Prediction: for Gamma = 2, K = 100
(G = c = Msun = 1) the FEM zero and the maximum of M agree in rho_c to < 1e-3 relative, and
M_max is about 1.64 at rho_c about 3.2e-3 [BACKGROUND, value from memory, not a source].
Refuted if the FEM zero misses the mass maximum by more than 1 per cent in rho_c.

Outcome P6, first attempt (run C-sidm-20261115-121400-d463e1a): M_max = 1.637276 at
rho_c = 3.182422e-3 (Gamma = 2, K = 100); FEM zero at rho_c = 3.2096e-3 (N = 300),
3.1610e-3 (N = 600), 3.1837e-3 (N = 1200): within 1 per cent, but not monotone in N. A probe
(unregistered, this session) showed the cause: the node list had an extra node at the TOV
start radius r0 = 1e-6, so the first element [0, 1e-6] had quadrature points below r0 where
the splines extrapolate; with uniform nodes from r = 0 the lowest omega^2 at rho_c(M_max) is
2.7e-9 (N = 300) and 1.6e-9 (N = 1200), against 0.104 for the next mode. The F21 runs are not
affected (their structure table starts at r = 0 and their nodes are r- and mass-uniform from
r = 0; their convergence was monotone). Fixed in pulsation_check.py; rerun registered next.
