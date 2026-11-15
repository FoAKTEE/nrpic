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
