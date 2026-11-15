# JOURNAL of the G0/G1 verifier of D-bh-dress (wave 2)

Fresh reader. Read before writing this entry: CLAUDE.md, CHARTER (to "Owners"), brief
lines 394-405, 766-783, 834-860, rulings of orch, decisions 0010-0015, `scope/SCOPE.md`
(the scoping text that names the claims), `einstein_straus/DERIVATION.md` (a derivation),
the docstrings of the test scripts, the inputs of D-pre-4, `es.json` of the data set, and
the first and last lines of the two finder outputs of D-pre-4 (raw data, seen while
learning the file format; so the D-pre-4 prediction below is not blind to the end values).
Not read before the checks: STATUS.md, HANDOFF.md, REVIEW.md, the JOURNALs of the track
and of its packages, stage/G0/REPORT.md, EVIDENCE.md, OPEN.md, stage/G1/STATUS.md, the
`results/*.txt` of D-pre-4.

## 2026-11-15, entry 1: claims chosen, predictions before any run

Claims on which the plan of `scope/SCOPE.md` rests (my choice):

- C1 (D-pre-1, SCOPE 3.4 item 2, 4, 5): the vacuum-bubble slice is a valid constraint-
  satisfying slice; the Misner-Sharp mass of the vacuum region between throat and wall is
  M; the dust is marginally bound Einstein-de Sitter with H^2 R_w^3 = 2M; no anti-trapped
  sphere; bare puncture mass m_p = M/a; Einstein-Straus scales R_w = (2/eps^2)^(1/3) M,
  wall speed (2 eps)^(1/3).
  Prediction: from the table `es.tab` alone with my own formulas, m(R) = M to <= 1e-6 in
  the vacuum region (limited by the table's interpolation), my 1D Hamiltonian and
  momentum residuals converge at the order of my stencil, R^2 theta_+ theta_- / 4 =
  -(1 - 2m/R) and never both expansions > 0; m_p = M/a to round-off. Refuted if m differs
  from M by more than 1e-5 anywhere in the vacuum region, or a residual does not converge.
- C2 (D-pre-4, SCOPE 3.3, 5 G1): the noise floor of the horizon mass of a vacuum puncture
  is small (well below 1 percent over 450 M) and converges with resolution.
  Prediction (not blind: first and last finder lines seen): drift
  |Mbar(t0+T) - Mbar(t0)| over T = 450 M, t0 = 50 M, below 1e-3 at M/8 and below 2e-4 at
  M/16; the M/16 drift smaller than the M/8 drift by at least a factor 4 (order >= 2).
  Refuted if the M/16 drift is not smaller than the M/8 drift, or exceeds 1e-3.
- C3 (SCOPE 4): turnaround of cold dust around a point mass in EdS with pure Hubble flow:
  M_b,ta -> (4/(3 pi))^(2/3) (a/a_i) M = 0.5648 (a/a_i) M; 1.525 M and 2.63 M turned
  around (hole included) at a/a_i = 2, 4 for every eps; r_ta table; T(a_f) formula.
  Prediction: my closed form reproduces every printed number to its printed digits.
  Refuted by a disagreement in the third digit.
- C4 (SCOPE 4, D-pre-3): the self-similar secondary-infall profile onto a point-mass seed
  has rho ~ r^(-9/4) inside the turnaround radius.
  Prediction: an independent radial shell code of my own (Newtonian, shell crossing,
  EdS, point seed) gives a logarithmic slope -2.25 +- 0.1 between ~0.05 and 0.3 r_ta at
  late time; the track's selfsimilar.py rerun reproduces its own output.
  Refuted if my slope lies outside -2.25 +- 0.15.
- C5 (SCOPE 4, last paragraph): capture by the hole: L_c = 4M for E = 1; cold dust from
  r_ta = 16-34 M needs a tangential speed above 0.12-0.25 to escape capture; cold growth
  law M_BH - M -> 0.356 (a/a_i) M.
  Prediction: exact Schwarzschild L_c(E) for the E of a particle at rest radially at r_ta
  is a few percent below 4M (E < 1), so the threshold speed is a few percent below
  4M/r_ta (direction of the claim unchanged); the closed-form Kepler collapse time gives
  a slope that approaches 0.356 from below and is markedly below it at a/a_i = 2-4.
  Refuted if the threshold differs from 4M/r_ta by more than 20 percent, or the
  asymptotic slope differs from 0.356 by more than 1 percent.
- C6 (D-pre-2, SCOPE 5 G1): in the probe limit, the density of bound, non-captured
  particles with constant distribution function vanishes at r = 4M in Schwarzschild.
  Prediction: my own phase-space integral of a constant f gives rho(r) = 0 for r <= 4M
  and a positive rho above, and agrees with the track's rho_constf_rel to < 1e-3 in
  shape. Refuted if rho > 0 at r < 4M (beyond quadrature error) or the shapes differ.
- C7 (SCOPE 3.3): definitional drift of the area mass in McVittie,
  d ln M_AH / d ln a = -12 (m H)^2 to leading order; and the precision statement
  (1 percent floor gives |k| < 0.015 over one doubling).
  Prediction: sympy gives -12 (mH)^2 + O((mH)^4). Refuted by another coefficient.
- C8 (SCOPE 7): the cost model (G1 about 5, G2 about 12 card-hours, within 30); its
  prediction for D-pre-4 (0.90 h at M/8, 2.01 h at M/16 for 500 M) against what the card
  runs of D-pre-4 actually used; and two source facts the plan uses (one global step, no
  subcycling; defaults metric_drvts = stored, ah_exc_factor = -1).
  Prediction: the measured card-hours of D-pre-4 lie within a factor 1.5 of the model;
  the source facts hold at the cited lines (lines may have moved after the core-v0.3
  merge). Refuted if a run cost more than 1.5 times the model or a source fact is false.
