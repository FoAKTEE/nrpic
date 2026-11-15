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

## Entry 2: C1 outcome (run D-20261115-170002-8cefc3e), C1b prediction

C1 outcome, from `es.tab` rows only (v1_es_slice.py; figure figs/v1_es_slice.png, looked
at): Misner-Sharp mass 1 +- 2.7e-10 in the vacuum transition (4 < R < 35.5), 1 +- 3e-14
in the time-symmetric part and on the inner sheet; plateau m - H^2 R^3/2 within +-9.5e-13
(the matching "dust mass removed = M" is exact; effective sharp-wall radius
(2M/H^2)^(1/3) = 40.04 M); H from KT, KL and from the Hamiltonian density agree to 3e-13
relative; momentum residual of order 4.00, 3.99 in the transition and 3.99-3.90 at the
smooth dust edges (h = 0.02 to 0.16 M); Hamiltonian density at round-off (1e-15) in the
dust and 1e-12 in the vacuum transition (no convergence there: a floor of the table itself,
1e-12 against KT^2 ~ 1e-3...1e-5, harmless); no anti-trapped row; throat at rbar = 0.52
(grid) against b/a = 0.5243; u constant = a - 1 inside rbar 3, M = a m_p = 1, while
m_p = M would give 0.9766. Negative control (KL := KT in the transition): residual 8.7e-4
at every spacing, so the check has teeth. Reference curves of es_reference.csv equal my
closed forms to 7e-16. Particle file: 140 tracers of mass 1e-30, dust from rbar = 36.23
outward, all u_i = 0, cumulative dust mass equal to m(R) - M to 3e-4 at R = 40 and 3e-8 in
total (lattice discreteness at the start of the ramp: 14 percent at R = 37 of a mass of
7e-6). Prediction of C1 confirmed. Not checked here: the data at the G2 parameters
(eps = 0.03, 0.01); this data set has eps = H M = 5.58e-3 (R_w = 40 M).
Run-registration slip: the first run passed --out '$NRPIC_RUN_DIR' literally; outputs moved
into the run directory by hand, said so in the manifest notes.

C1b prediction (rerun of the t = 0 code check on the release processor executable
core-v0.3 instead of the wave-1 branch build 408df57): on the same table the release gives
the same constraint fields cell by cell to round-off (<= 1e-12 of the field scale) unless
core changed the format-2 reader or the constraint stencils at the merge; in either case
the regional maxima keep converging at order >= 3 in the transition and at the inner dust
edge between dx = 1 and 1/2 M. Refuted by a cell difference above 1e-9 relative without a
changelog entry, or by an order below 2.

## Entry 3: C1b outcome (run D-20261115-170224-924d1d9)

The release processor executable (core-v0.3) reproduces the wave-1 branch-build dumps of the
t = 0 check bit for bit: max |difference| = 0 in E, chi, H, M_i, Khat, alpha at dx = 1 and
1/2 M (v1b_compare.json; figure figs/v1b_code_t0.png, looked at: all points on the
diagonal). Regional maxima from the track's own analysis on the release dumps: mid
transition |H| 8.4e-9 -> 1.4e-10, |M| 2.4e-8 -> 4.4e-10; inner dust edge |M| 1.1e-5 ->
1.1e-6 (order 3.2); orders over the whole transition 5.3 (H) and 4.7 (M); puncture region
r < 3: |H| 0.76 -> 1.14 (does not converge, throat unresolved at these spacings, as the
derivation says). Prediction confirmed. Only two resolutions: an order from two points.

Side observation: a file `es.horizon_summary_0.txt` appeared in the worktree root at
09:03-09:12 local time; my t = 0 runs have no horizon finder, so it comes from another
helper's ES-1 smoke test (the finder writes into the working directory, not into -d). I
leave it alone; it blocks `nrpic-run submit` (worktree not clean outside tracks/).

C6 development note (before the registered run): my first quadrature returned a density at
r = 3 M because the plunge condition was applied only for 3 < r < 6; inside the photon
sphere every orbit plunges. Fixed (n = 0 for r <= 3); r = 3 was the only grid point
affected.

## Entry 4: development runs of C2, C3/C5, C6, C7, C8 (unregistered, scratch/tmp), then registration

The scripts were debugged on scratch/D-bh-dress/tmp before the registered runs; the
registered runs below repeat them unchanged. What the debug runs showed beyond the
predictions of entry 1 (written down here before the registered runs):
- C2: besides the secular drift, the M/8 and M/16 finder masses show excursions at
  t = 200-260 and 300-340 M of nearly the same size at both resolutions (7e-5 and 1e-4 vs
  5e-5 and 7e-5 from a linear fit): not a resolution effect. The D-pre-4 runs kept the
  domain of +-128 M of the calibration input; the scoping cost model itself asks for
  L >= 0.71 T (= 355 M for 500 M) to keep the boundary out of causal contact. A boundary
  signal is a candidate cause, [TO VERIFY] (test: the same run with L = 384 M; refuted if
  the excursions stay at the same times and size).
- C8: with the domain actually used (+-128 M) the model predicts the D-pre-4 cost to 3 per
  cent (measured/model 0.97 at both resolutions); the scoping table's 0.90 and 2.01 h
  include the domain growth that the runs did not apply. Finest level against horizon: the
  horizon's coordinate radius grows from 1.34 M (t = 50) to 1.67 M (t = 500); with the
  calibration input's requested region |x| < 1.5 M the finest level ends at 2 M for M/16
  (blocks of 1 M) but at 1.5 M for M/32 and M/64, which the horizon reaches at t = 144 M.
  Prediction for the registered run: same numbers (deterministic).
- C6: peak ratio relativistic/GS = 2.59 and 4Gm-variant/relativistic = 1.092, not the 3
  and 1.15 of SFW's prose (SFWpaper.tex:443) that SCOPE.md section 5 proposes as G1
  numbers; the track's rho_constf_rel agrees with my quadrature to 1.4e-5.
- C7: sympy gives M_MS = m + H^2 R^3/2 exactly for McVittie, R_h/(2m) = 1 + 4 h^2 + 48 h^4,
  d ln M_AH/d ln a = -12 h^2 - 240 h^4 (h = m H); exact roots: -1.20e-3, -1.10e-2,
  -0.151 at h = 0.01, 0.03, 0.1.

## Entry 5: C4 set-up (own radial-shell code), prediction restated

Debug run at a_f/a_i = 20, N = 1000 (scratch/tmp, unregistered): density slope fits
-2.2 to -2.7 depending on the range (caustics), enclosed-mass slope -2.11 to -2.28; the seed
(1.3 M with the inner dust) is still comparable to the dust inside 0.05 r_ta there. The
registered run goes to a_f/a_i = 100 (and 300) with N = 2000-4000, softening 1-2 M and two
step sizes. Prediction (entry 1, unchanged): slope -2.25 +- 0.1 between 0.05 and 0.3 r_ta
for the enclosed-mass estimate at a_f/a_i = 100 and 300; refuted outside +-0.15. The
density-bin fits are expected to scatter more (caustics of radial orbits).

## Entry 6: rerun of the track's self-similar test (prediction)

Rerun of `secondary_infall/selfsimilar.py --taumax 300` (the test behind the -9/4 claim of
D-pre-3, run D-bh-dress-20261115-123813-97afeea) into my own run directory. Prediction: the
numbers of selfsimilar.txt are reproduced exactly (deterministic code, same inputs);
refuted by any difference beyond the last printed digit.

## Entry 7: C8b, block counts of the finer meshes (prediction)

While checking which region the finest level covers, a debug call of the release
executable with `-m` (scratch/tmp/mesh7, unregistered) printed 344 and 400 MeshBlocks for
finest levels 5 and 6 (the anchors: confirmed) but 3200 and 4712 for levels 7 and 8 (M/32,
M/64) with the same requested region |x| < 1.5 M: from level 7 on, every coarser level is a
shell of 448 blocks instead of 56. The cost model of SCOPE.md 7 adds 56 blocks per halving
(456 and 512 blocks). Registered rerun v9_mesh.sh; prediction: the same counts (the tree
build is deterministic), and with |x| < 2 M at level 8 (horizon on the finest level for
500 M) more than 4712 blocks. Refuted by other counts.

## Entry 8: C4 outcome so far, and a new prediction

C4 (run D-20261115-171733-633d422, variants N4000/N2000 at a_f/a_i = 100 finished):
enclosed-mass slope -2.42, -2.43, -2.38 (N = 4000) and -2.40, -2.38, -2.32 (N = 2000) over
0.03-0.3, 0.05-0.3, 0.1-0.4 r_ta; the density-bin fits scatter from -1.7 to -3.1
(caustics). My prediction (-2.25 +- 0.1, refuted outside +-0.15) FAILED for these ranges.
Not yet a contradiction of the track: the track's own self-similar solution (run
D-bh-dress-20261115-123813-97afeea, selfsimilar.txt; rerun D-20261115-171818-a5aefe8
reproduces it exactly) has d ln m/d ln lambda = 0.705 over 3e-3..3e-2 and 0.741 over
1e-4..1e-3, and from its printed m(0.03) = 0.136, m(0.3) = 0.576 a mean slope 0.627, i.e.
rho ~ r^-2.37 over 0.03-0.3: -9/4 is the asymptote for lambda << 1e-2, not the slope where
my prediction looked. My prediction used the wrong range.
New prediction (before the comparison script runs): my shell-code m(lambda) = M(<lambda
r_ta)/M_ta at a_f/a_i = 100 and 300 agrees with the track's self-similar m(lambda) to within
5 percent for 0.02 < lambda < 0.5; refuted by a deviation above 10 percent there.

## Entry 9: C4 with a velocity step limit; prediction for the second registered run

Debug runs (scratch/tmp/v4v, unregistered) with the step also limited by
eta sqrt(r^2 + s^2)/|v|: median deviation of my m(lambda) from the track's self-similar
m(lambda) over 0.02 < lambda < 0.5 is -32, -23, -14 percent for N = 2000, 4000, 8000
(eta = 0.05) and -19 percent for N = 4000 at eta = 0.0125: it shrinks with N (discreteness
heating of the shells: 7, 3, 1 percent of the turned-around dust sits outside r_ta at
N = 2000, 4000, 8000) and only weakly with the step. The entry-8 prediction (5 percent)
FAILED for N <= 8000. Enclosed-mass slopes over 0.03-0.4 r_ta: -2.32 ... -2.44 in all
runs, against -2.37 of the self-similar solution there.
Prediction for the registered run v4_driver2.sh (same code, five variants in parallel):
the debug numbers are reproduced exactly (deterministic), and N = 16000 has a median
deviation below 10 percent in magnitude; refuted if N = 16000 is not closer than N = 8000.
