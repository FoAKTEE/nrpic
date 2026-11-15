# Journal of core, package scalar2 (scalar field, second pass, for Track E)

Branch `core/scalar-2`, worktree `wt/core-scalar2`. Append-only. Labels [VERIFIED],
[BACKGROUND], [JUDGEMENT], [TO VERIFY]; a number carries a run id
(`tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`), a file of
this repository, or a locator in a paper source under `kb-data/raw/arxiv/`. Paper keys:
P1 = arXiv:2512.14649 v2 `PRD_v2.tex`, P2 = arXiv:2502.06783 v3 `main_V2PRD.tex`. SPEC =
`tracks/E-stoch-inf/spec/SPEC.md`, SCOPE = `tracks/E-stoch-inf/spec/scope/SCOPE.md`,
NOISE_SPEC = `tracks/E-stoch-inf/noise/NOISE_SPEC.md`, all on `track/E-stoch-inf` at
6330493.

## 2026-11-15, entry 0: what was read, and the state found

Read: `CLAUDE.md`; charter to the end of "Owners"; brief 493-553, 688-706, 834-860; the
rulings after wave 1 and decisions 0010 to 0015; core's `HANDOFF.md`, `STATUS.md`,
`stage/G2/OPEN.md` (core has no G0 or G1 package; the files of that name read were Track
E's `stage/G0/OPEN.md` and `stage/G1/STATUS.md`); Track E's four requests to core of
2026-11-15T14:10Z, SPEC, SCOPE, NOISE_SPEC, DESIGN_REVIEW sections 6.3, 8.1, 9, 11, the
drivers `analysis/lead/u_runs.py`, `lu_validate.sh`, the reference `noise/ref/noise_ref.py`;
the module `athenak/src/scalar_field/` and `pgen/nrpic/scalar_field_tests.cpp` whole;
`coord/INTERFACES/scalar_field.md`; `python/nrpic/scalar_field.py`.

Found:
- [VERIFIED by reading] The window increment of the test-only Markov scheme is already
  formed without cancellation in the source of release core-v0.3
  (`scalar_field_noise.cpp`, `NoiseShellFactors`: dW = sinh(x1 - x0)/(2 cosh x1 cosh x0)),
  since commit 5a6953e. Track E measured its A1 failure (1.07e-10) on the older
  executable of 836ac86, which took the difference of two tanh. So request (a) of
  `noise-unit-test-results` needs no source change; what is left is to show A1 at 1e-11.
  Track E's reference `noise_ref.py:transfer` still forms W(t) - W(t - dt) directly.
- [VERIFIED at the source] Magnitudes of the constraints, P1:735-745: [H] = |R| +
  |(2/3) K^2| + |At_ij A^ij| + |2 Mpl^-2 rho|; [M_i] = |gt^kl d_k At_il + 2 gt^kl
  Gt^m_l(i At_k)m| + |3 gt^kl At_ik d_l chi/(2 chi)| + |(2/3) K_|i| + |Mpl^-2 J_i|; [M] =
  sqrt(sum_i [M_i]^2). The figures show the box mean of the ratio, <|C|/[C]> (P1:771).
  [JUDGEMENT] The Christoffel term is printed with a plus sign; the covariant divergence
  of At_il has minus signs (gt^kl (d_k At_il - Gt^m_ki At_ml - Gt^m_kl At_im)). The code
  takes the covariant divergence; the terms differ at second order in the perturbations
  only.
- [VERIFIED at the source] Test case: P1:405-420 (quadratic: eps1 = 0.01, eps2 = -0.02,
  H0 = 1e-5 Mpl, N* - N0 ~ 5, N_f - N* ~ 8); potential-position fixing P2:399-405; window
  s = 5, L k_sigma* = 2 pi, k_max = N k_sigma*/4 at P1:503-512; a* = 1, sigma = 1, N = 256
  at P1:519.
- Builds of the unmodified source in this worktree: `.work/build_cpu`, `.work/build_gpu`
  (68 s and 216 s). Python environment made with `harness/bin/nrpic-env create
  --no-kokkos` (worked).

## 2026-11-15, entry 1: derivation and design of the initial slice

Derivation (own, in the code's variables: G = 1, K = -3H, Pi = n.d phi; eps1 = 4 pi
Pi_b^2/H^2, so sqrt(2 eps1) Mpl of the papers is Pi_b/H; eps2 = -dln eps1/dN = 6 +
2 V'/(H Pi_b) - 2 eps1, i.e. V' = Pi_b H (eps2/2 + eps1 - 3)). The slice of SPEC 5.3 with
chi_0 = E_0 = 0 is the hypersurface of the longitudinal gauge at t*: gamma_ij = a^2 (1 -
2 Psi) delta_ij with the Bardeen potential Psi = -eps1 H a^2 dR/dt / k^2. K_ij and Pi are
properties of the hypersurface, so with the longitudinal lapse 1 + Psi:
delta K = 3 (dPsi/dt + H Psi), delta Pi = d(delta phi_N)/dt - Pi_b Psi, delta phi_N =
(Pi_b/H)(R - Psi). The longitudinal momentum constraint gives dPsi/dt + H Psi = eps1 H
(R - Psi), and d(Pi_b/H)/dt = -(Pi_b/H) H eps2/2, hence
    delta phi = (Pi_b/H)(A - Psi),  delta K = 3 eps1 H (A - Psi) = 12 pi Pi_b delta phi,
    delta Pi  = (Pi_b/H) B - Pi_b (eps1 + eps2/2)(A - Psi),  chi = chi_b (1 + 2 Psi),
with A = R^> = W R and B = dR^>/dt = W' R + W R'. This is SPEC 5.3 with the corrected
delta Pi (the printed form of P2 eq. 17 adds Pi_b Psi). Linearised constraints of the
code (Z4c::ADMConstraints: H = R + K^2 - K_ij K^ij - 16 pi E; conformally flat part of R
through the second differences): delta H = -4 (k2/a^2) Psi - 4 H delta K - 16 pi (Pi_b
delta Pi + V' delta phi) = -4 (k2/a^2) Psi - 4 eps1 H B, for any (A, B); delta M_i =
-(2/3) d_i delta K + 8 pi Pi_b d_i delta phi = 0. So the linear Hamiltonian constraint
holds if Psi = -eps1 H a^2 B/k2 with k2 the symbol of the operator the constraint uses,
and the printed form leaves delta H = -16 pi Pi_b^2 Psi = -4 eps1 H^2 Psi (Track E's 4
eps1^2 H^3 a^2 k^-2 dR/dt, run E-stoch-inf-20261115-123146-82d2fd4).

Design [JUDGEMENT]:
- `<problem> id = stochastic` of pgen `scalar_field`: homogeneous background as `flrw`
  (phi0, pi0 given: the state at N* on the attractor, from the reference), then
  `ScalarField::InitialSlice` (new file `scalar_field_slice.cpp`) adds the perturbations
  with the mode set, alpha_n (dof 0, epoch 0) and `NoiseSynthesize` of the sources: three
  fields (A; B; Psi with a real factor per mode), combined cell by cell. Mode functions
  from `noise_mode_file`, the window in the code.
- `slice_k2 = stencil` (default): k2 is the symbol of the second differences, so the
  discrete linear constraint vanishes to rounding; `continuum`: (2 pi n/L)^2.
  `slice_delta_pi = printed`: negative control. `slice_window = false`: all modes in with
  W = 1 (the initial-value problem without sources, Track E's test L3).
- `noise_mode_scale`: factor on the mode functions, for amplitude scans and for the
  odd/even decomposition below (scale -1 is the mirrored realisation).
- The lockstep background is set from phi0, pi0 exactly: the box means of `MeshMeans`
  carry the rounding of a running sum (seen in a smoke run: <phi> off by 6e-13 relative
  at 32^3), which would also depend on the MeshBlock layout once the field is perturbed.
- Constraint record in a file of its own, `<basename>.sf.con.hst` (`con_dcycle`), so that
  `.sf.hst` stays as it is; magnitudes in `scalar_field_diag.cpp`, with the M_i of the
  BSSN form kept as a check against the M_i of `Z4c::ADMConstraints`.
- Dumps: layout NRSFDMP2 (names in the header) when `dump_metric`, `dump_magnitudes`,
  `dump_constraints`, `dump_noise` leave their defaults; NRSFDMP1 otherwise, unchanged.
- New options are read only if present (`DoesParameterExist`), so the parameter list in
  the restart and `bin` files of existing inputs does not change.
- Without kicks (`noise_kick_* = false`) the fields of a stage are no longer synthesized
  (nothing reads them).

Seen before the predictions below were written (two unregistered smoke runs of the
example input at 32^3, 0 and 4 steps, `scratch/core/tmp/scalar2/dev/`): the run starts;
<|H|/[H]> = 2.6e-12 and <|M|/[M]> = 1.5e-5 at t = 0; the slice equals the Python twin to
3.6e-10 (phi), 5.6e-13 (Pi), 4.2e-11 (chi), 3.3e-10 (K) of the rms coefficient. The
predictions on those four numbers are therefore not blind.

## 2026-11-15, entry 2: predictions (written before the registered runs)

Case: quadratic case of P1 in code units (`python/nrpic/sf_inflation.py`: H*/Mpl =
9.48692e-6, eps1* = 1.11071e-2, eps2* = -2.21331e-2, mass = 0.182878, phi0 = -2.666795,
pi0 = 0.0297300; SPEC 6 lists H* = 9.48692e-6, eps1 = 1.1107e-2, eps2 = -2.213e-2), box
2 pi, N = 32, nmax2 = 64 (k_max/dk = 8, the convergence set-up of P1:756), seed 20261115,
Courant 0.25, geodesic slicing.

T1 slice at t = 0.
- P1a Coefficients of delta phi, delta Pi, chi - 1, delta K from the dump equal (twin
  transfer) x (twin alpha) within 1e-8 of the rms coefficient (rounding of background
  plus perturbation, about 2e-9 per cell); gt = delta and At = 0 exactly; nothing
  outside the mode set above 1e-8 of the rms. Refuted by a larger difference.
- P1b Scale s = 1, 1/2, 1/4: <|H|/[H]> falls by 4 per halving and <|M|/[M]> by 2 (|M|
  second order, [M] first order), each within 5 percent.
- P1c Odd part O = [C(+s) - C(-s)]/2 of the constraint fields, s = 1: with the corrected
  delta Pi and the stencil k2, rms O(H) < 1e-13 (rounding of the second differences of
  psi^4; the largest linear term 4 k2 Psi has rms about 1.6e-6) and rms O(M_i) < 1e-13.
  The even part equals the constraint itself to 1e-3. Refuted by an odd part above
  1e-12.
- P1d Printed delta Pi: the coefficients of O(H) equal -4 eps1 H^2 Psi_n alpha_n within
  1e-4 of their rms; <|H|/[H]> then falls by 2 per halving of s (first order); the
  momentum constraint is unchanged.
- P1e Continuum k2 at N = 16 (nmax2 = 16): coefficients of O(H) for the six |n| = 1
  modes equal -4 (k2_stencil - k2) Psi_n alpha_n within 1 percent, relative size 6e-6 of
  4 k2 Psi; at N = 32 the same term is near the rounding floor.

T2 background (A1 of SCOPE 4: 1e-4), run to t = 8.44 (8 e-folds), slice and sources on.
- P2a Box means of phi, Pi, K against the Friedmann reference (`scalar_field.friedmann`
  from phi0, pi0): largest relative difference below 1e-7. e-folds -ln<chi>/2 against
  ln a: below 2e-5 (fourth-order error of the exponential, (2 H dt)^4/120 x 2 N with
  H dt = 0.049). Halving the Courant factor divides the e-fold error by 16 +- 2.
- P2b The lockstep background (phi_b, Pi_b, ln a of `.sf.hst`) equals the reference to
  the same accuracy. Refuted by 1e-5 or more in a mean, or by a first-order trend.

T3 constraints in time (A4, A5; P1:538-541, 747-773), runs to t = 3.2 (3 e-folds;
k_sigma passes k_max at N = 2.1), scales +1, -1, +1/2, -1/2, control `noise_pi_sign =
-1` at +1 and -1, dumps every 0.4.
- P3a <|H|/[H]> below 1e-8 and <|M|/[M]> below 1e-1 throughout for scale 1; they do not
  grow after the last crossing.
- P3b Even part E = [C(+s) + C(-s)]/2 of H and M_i (second order): rms E(1)/rms E(1/2) =
  4 +- 0.4 at every dump. Odd part O (first order, the truncation error of the
  stencils: the symbols of D1^2 and D2 differ by 11 percent at k_max dx = pi/2):
  rms O(1)/rms O(1/2) = 2 +- 0.1. [JUDGEMENT] At this resolution the odd part is not
  small against the even part once the high shells enter; if O stays below E/10
  throughout, the estimate of the truncation part is refuted.
- P3c Control: <|H|/[H]> at least 100 times that of the proper run within the first
  e-fold and odd in s (rms O > 10 rms E); <|M|/[M]> above 0.1 after one e-fold (P1:541:
  H/[H] ~ 1e-5, M/[M] ~ 1 "at first order"; own estimate of the size 8 eps1 H int S_R
  /12, 1e-7 to 1e-6).
- P3d Ladder N = 32, 64, 128 with nmax2 = 64 on a card: the odd part and, where it
  dominates, <|H|/[H]> and <|M|/[M]> at fixed time during the entry fall at order
  between 4 and 6 (A5) down to the second-order part, which does not depend on N.
- P3e rms |M_bssn - M_adm| below 0.3 rms |M| at N = 32 and falling with N at order 4 or
  more (a wrong sign of the Christoffel terms would give a difference of the size of M
  that does not converge).

T4 card against processors, same input (N = 32 case, 20 steps): at t = 0 every dumped
field within 1e-13 of its largest value; after 20 steps within 1e-11; constraint fields
within 1e-12 absolute; history columns within 1e-10 relative, constraint columns within
1e-2. 1, 8 and 64 MeshBlocks and a restart at cycle 10 give byte-identical dumps on
processors (A7).

T5 Track E's noise validation (NOISE_SPEC 9, 10) with the lead's scaled base case
(`u_base32.athinput`): U1 to U8 on processors: frozen tanh and Markov Heaviside pass
every test; Markov tanh fails A1 near 1e-10 against Track E's reference as written and
passes at 1e-11 once the reference forms the increment as the code does (a copy of the
reference in scratch with dW = sinh(s hubble dt)/(2 cosh x1 cosh x0)). Refuted if A1
still fails with the patched reference. U9 (U2 on a card): A14 below 1e-12 of the rms.

T6 existing behaviour: the processor executable of release core-v0.3 and the new one
give byte-identical files on the scalar-field inputs of wave 1 (`flrw_slowroll`, `plane`,
`kg_wave`, `noise_power`, `noise_ms`: histories, dumps, records, restart files up to the
36 unset header bytes) and on the cases geo, boris, dep, east, os, jeans, binary of
`tracks/core/tools/regress_relativistic.py`.

## 2026-11-15, entry 3: registration by hand; one more test, predicted before it ran

- `harness/bin/nrpic-run submit` fails in this worktree: `KeyError: 'outputs'` in
  `budget_state` -> `is_live` (`harness/bin/nrpic-run:163`) while it reads the manifests
  of core's wave 1, which have no `outputs` key. Runs of this package are therefore
  registered by hand with `tracks/core/analysis/scalar2/runreg.py` (same fields; the keys
  `track`, `gate`, `outputs`, `status` are added in the layout of the harness template).
  `tracks/core/tools/regress_relativistic.py` registers through `run_registered.py` of
  wave 1. Request to orch: let `nrpic-run` read manifests without `outputs`.
- Run core-20261115-154749-1b20b0f FAILED before any AthenaK run (relative path of the
  executable in the driver); fixed, no result lost.
- `scratch/core/` is shared by all core sessions; this package keeps temporary files in
  `scratch/core/tmp/scalar2/`.

T8 (added; no run of it has been looked at). End-to-end check that the slice and the
sources carry one linear solution: from dumps with the metric (32^3, nmax2 = 64, to t =
3.2), the curvature perturbation of the slice psi_n = (a^2 chi_n - 1)/2 + (1/4) n_i n_j
(gt_ij - delta_ij)_n/n^2 (own derivation from gamma_ij = a^2 [(1 - 2 psi) delta_ij + 2 d_i
d_j E]: a^2 chi - 1 = 2 psi + (2/3) k^2 E, gt_ij - delta_ij = 2 (d_i d_j - delta_ij
lap/3) E; it equals E6 of SPEC 9) and R^NR_n = psi_n + (H/Pi_b) delta phi_n with box means
for H = -<K>/3 and Pi_b = <Pi> (SPEC 7.1, P-c), against L^(-3/2) W(t) R(t) alpha_n with
R(t) of the lockstep record of the same dump.
- P8a At t = 0 the ratio R^NR_n/(W R alpha_n) is 1 within 1e-6 for the modes with W >
  1e-3 (the slice is built that way; rounding of chi and phi limits it).
- P8b At every later dump, for the modes with |n| <= 4 (k <= k_max/2) and W > 0.5, the
  ratio is 1 within 2e-2 (Track E's A2 threshold), and within 2e-3 for |n| <= 2. The
  deviation grows with |n| like the truncation error of the stencils. Refuted by a
  deviation of order one during the entry (wrong sign or factor between slice and
  kicks), or by a drift of the lowest modes after their entry (no freezing).
- P8c With the negative control `noise_pi_sign = -1` the ratio departs from 1 by more
  than 10 percent for the modes that have entered.

## 2026-11-15, entry 4: outcomes of T1, T4 (processor part), T5 (processors)

Executable of all processor runs: `.work/exe/athena_cpu_a58e95b` (sha256 c69266ec...9439e),
built from the source of commit a58e95b; the later commits change no source.

**T1, run core-20261115-154907-eb68eaa** (20 runs of zero steps, 11.5 s of AthenaK;
figure `fig_slice.png`, looked at: the slice coefficients fall with |n| as the window
does, code minus twin sits at 1e-18 to 1e-21; the three constraint lines have slopes 2,
1, 1; the odd part of H of the printed form lies on the prediction down to the rounding
floor near 1e-16, where the corrected form sits at all |n|).
- P1a HOLDS. Code against twin, largest deviation over the 1054 modes relative to the
  rms coefficient: delta phi 3.6e-10, delta Pi 5.6e-13, chi - 1 4.2e-11, delta K 3.3e-10;
  without the window 5.3e-11, 7.6e-14, 8.0e-11, 4.5e-11. Largest coefficient outside the
  mode set 4.0e-10 of the rms. gt - delta, At and alpha - 1 are exactly 0.
- P1b HOLDS. <|H|/[H]> = 2.625e-12, 6.553e-13, 1.630e-13 for s = 1, 1/2, 1/4 (factors
  4.005, 4.021); <|M|/[M]> = 1.462e-5, 7.310e-6, 3.655e-6 (2.0000, 1.9999); <|M|>
  5.038e-12, 1.259e-12, 3.149e-13 (4.0000, 3.9997). <[H]> = 12.0000013, <[M]> = 3.62e-7.
  Without the window (all 1054 modes at full amplitude): <|H|/[H]> = 3.94e-10 and
  9.84e-11 (factor 4.0000), <|M|/[M]> = 1.30e-4 and 6.48e-5 (2.0000).
- P1c HOLDS. Odd part, corrected delta Pi and stencil k2: rms O(H) = 2.7e-14 against an
  even part of 4.648e-11 and a largest linear term of 1.59e-6 (ratio 1.7e-8); rms O(M_i)
  = 1.06e-15 against 3.2e-12 to 3.9e-12. The even part equals the field to 5.8e-4 (H)
  and 3e-4 (M_i).
- P1d HOLDS, with one correction of the wording. Printed delta Pi: rms O(H) = 1.759e-8
  (387 times the even part), its coefficients equal -4 eps1 H^2 Psi_n alpha_n within
  6.1e-7 of their rms; <|H|/[H]> = 1.2003e-9, 6.001e-10, 3.001e-10 (factors 2.0000). The
  momentum constraint is unchanged at first order (odd part 1.06e-15 as before), but
  its second-order part changes by 1.1 percent (rms M_x 3.858e-12 against 3.902e-12),
  because delta Pi enters 8 pi delta Pi d_i delta phi; "unchanged" was too strong.
- P1e HOLDS. Continuum k2 at N = 16: the three |n| = 1 coefficients of O(H) equal -4
  (k2_stencil - k2) Psi_n alpha_n within 1.6e-5; relative size of the k2 error 6.39e-6;
  rms O(H) = 1.02e-11 (stencil k2 at N = 16: 6.9e-15). At N = 32: 1.02e-7, rms O(H) =
  1.6e-13 against 2.7e-14 with the stencil k2, coefficients within 0.26 percent of the
  prediction.

**T4 processor part, run core-20261115-155719-383321a** (20 steps; dumps at cycles 0,
10, 20 with 22 fields each). HOLDS: 1, 8 and 64 MeshBlocks give bit-identical fields
(66 comparisons each, largest difference 0); the run restarted at cycle 10 writes a
dump at cycle 20 that is byte-identical to that of the uninterrupted run. The columns
of `.sf.con.hst` differ between the layouts by at most 2.7e-14 relative (order of the
sums), the two maxima not at all; the first e-fold entry is pure rounding (1e-13). No
figure: the result is "all differences are zero".

**T5 processors, runs core-20261115-155122-eb68eaa (U1 to U8, validation with Track E's
files as committed at 6330493) and core-20261115-160103-3fde433 (the same outputs
against a copy of the reference with the cancellation-free increment)**. Scaled base
case of the lead (N = 32, nmax2 = 100, 120 cycles); U4 = U2 restarted at cycle 60;
U5a/U5b N = 16 and 32 with nmax2 = 36.
- Frozen tanh (U1, U2, U3, U4, U5a/b, U8): every test passes, failed 0. A1 5.3e-14; A11
  1, 8, 64 MeshBlocks bit-identical; A12 restart bit-identical; A13 3.0e-15; A10
  3.6e-15; A15 passes. Markov Heaviside (U7): every test passes, A1 2.4e-15.
- Markov tanh (U6) with the reference as written: A1 FAILS at 9.77e-11 (bound 1e-11), as
  predicted; every other test passes.
- With `window_increment` in the reference (dW = sinh(s hubble dt)/(2 cosh x1 cosh x0)):
  A1 = 3.3e-15 for Markov tanh, 3.7e-15 for frozen tanh, 2.4e-15 for Markov Heaviside;
  failed 0 in all three. HOLDS: the code needed no change; the remaining 1e-10 was the
  cancellation in the reference. The change of the reference is Track E's to make
  (13 lines; diff in `scratch/core/tmp/scalar2/Etree_patched/.../noise_ref.py`, quoted
  in the interface proposal).
- Figures looked at: `val_markov_tanh/fig_val_markov_tanh.png` of the second run (shell
  spectrum scattered about 1 inside the band but for one three-mode shell at 0.38, which
  the exact Gamma test accepts; correlation function on the expectation; |xi/G|^2
  exponential).

## 2026-11-15, entry 5: T8 outcome; T6 first run failed on a test artefact

**T8, run core-20261115-160134-3fde433** (32^3, nmax2 = 64, to t = 3.2, 9 dumps with the
metric; figure `fig_rnr.png`, looked at: the deviation rises with |n| from 1e-6 to 1e-3
and the control sits at 2 from the first dump on).
- P8a HOLDS: at t = 0 the ratio R^NR_n/(W R alpha_n) is 1 within 1.1e-11 for the three
  modes with W > 1/2 and within 2.0e-9 for the 13 modes with W > 1e-3.
- P8b HOLDS with a wide margin: largest |ratio - 1| at the later dumps 2.7e-5 for |n| <=
  2 (3.7e-6 from N = 2.0 to 3.1, no drift), 7.6e-5 for |n| <= 4, 2.8e-3 for all 1054
  modes once every mode has W > 1/2 (N = 3.14), against the bounds 2e-3 and 2e-2. The
  deviation of the high shells grows from 8e-4 at N = 2.4 to 2.8e-3 at N = 3.1.
- P8c HOLDS: with `noise_pi_sign = -1` the deviation is 1.7 at the first dump and 2.0
  afterwards (R^NR close to -W R alpha).
So the slice and the kicks carry the coarse-grained linear solution through the entry
of all shells at the coarsest resolution of the ladder.

**T6, run core-20261115-155841-bc78aa8: exit status 1.** Nine cases identical (107
files; eight restart files differ only in the 36 unset header bytes), but the case
`msr` (restart from cycle 13) reported two restart files of different size. Looked at
the files: the parameter list of a restarted run records the path of the restart file
(`<job> restart_file`), and the two executables started from `.../ms/base/rst/...` and
`.../ms/new/rst/...`; the data after `<par_end>` are byte-identical (0 differing bytes).
An artefact of the comparison, not of the executable. `t6_regress.py` now compares the
parameter list line by line (only `restart_file` may differ) and the data byte by
byte; rerun below.

## 2026-11-15, entry 6: outcomes of T2 and T3 (processors); one prediction failed

**Run core-20261115-155040-eb68eaa** (seven runs at 32^3, nmax2 = 64; wall 534 s for 172
steps at Courant 0.25, 1018 s for 344 steps at 0.125; figure `fig_evolve.png`).

T2 background (the run ends at t = 8.44, which is 8.044 e-folds):
- P2a HOLDS, by five orders more than predicted. Box means against the Friedmann
  reference, largest relative difference over the run: phi 6.4e-13, Pi 4.5e-12, K 3.6e-12
  at Courant 0.25 (6.3e-13, 3.8e-12, 9.1e-13 at 0.125); the criterion A1 of Track E is
  1e-4. These are at the rounding of the box sums (entry 1), so they do not show an
  order. e-folds -ln<chi>/2 against ln a: 5.49e-6 at the end for Courant 0.25, 3.30e-7
  for 0.125, ratio 16.6 (predicted below 2e-5 and 16 +- 2).
- P2b HOLDS: lockstep background against the reference 2.6e-13 (phi_b), 2.3e-12 (Pi_b),
  2.1e-12 (ln a, absolute). The lockstep ln a is integrated as a slow variable and is
  accurate to rounding, while chi of the mesh carries the fourth-order error of an
  exponential: the two scale factors differ by 5.5e-6 after 8 e-folds at this step.

T3 constraints in time:
- P3a HOLDS: <|H|/[H]> at most 4.7e-11 (N = 2.4), <|M|/[M]> at most 3.7e-4 (N = 2.7);
  after the entry both fall, to 3.1e-12 and 1.6e-7 at N = 8.04. P1:538-541 quotes 1e-10
  for the Hamiltonian ratio during the entry.
- P3b FAILED for the even part of H: rms E(1)/rms E(1/2) is 4.002 at t = 0 but 0.86 to
  1.05 at the later dumps, not 4. The even part is dominated by a term that does not
  depend on the amplitude: 2.4e-11 to 3.2e-11 at every dump, uniform in space. Run that
  could have refuted the cause I name: the same case at Courant 0.125 has a late-time
  floor of <|H|/[H]> of 1.8e-13 against 3.1e-12 at Courant 0.25 (factor 17, fourth order
  in the step): it is the residual of the time integration of the background. I had
  not thought of a zeroth-order part. Test T3b below separates it with a run at s = 0.
  The rest of P3b HOLDS: the odd parts scale as s (rms O(1)/rms O(1/2) = 2.000 for H
  and for M at the dumps t = 0.44 to 2.85), the even part of M as s^2 (4.000), and
  the odd part overtakes the even part of H from N = 1.6 on (ratios 0.27, 0.21, 0.46,
  2.7, 13.7, 20.3, 10.6).
- An error of the analysis, found in its output: the dumps of cycle 66 were compared
  although the short runs cut their last step at tlim = 3.2 and the long run does not
  (t = 3.2398); the numbers of that dump (even ratio of M 66, odd ratios 1.92, 1.95)
  mean nothing. T3b matches the dumps by time.
- P3c HOLDS: with `noise_pi_sign = -1`, <|H|/[H]> reaches 9.8e-8, 5.7e4 times the proper
  run within the first e-fold; rms O(H) is 5e4 times the even part (first order);
  <|M|/[M]> = 0.16 at one e-fold, at most 0.21. (P1:541 quotes 1e-5 and 1 for its sign
  flips; the size here agrees with the estimate 8 eps1 H int S_R/12 of entry 2.)
- P3e HOLDS on processors: rms |M_bssn - M_adm| is at most 3.4e-4 of rms |M| up to t =
  3.2.

T3b, predicted before it runs: the s = 0 run (homogeneous universe, same mesh and step)
has a Hamiltonian residual H0 that is uniform (spatial standard deviation below 1e-13)
and lies between 2.0e-11 and 3.5e-11 at the dumps t = 0.44 to 2.85; the second-order
part C2(s) = E(s) - H0 has rms C2(1)/rms C2(1/2) = 4 +- 0.2 at each of these dumps.
Refuted if H0 is not uniform or if the ratio is not 4.

## 2026-11-15, entry 7: outcomes of T3b and T6

**T3b, run core-20261115-161040-760b515** (one run at s = 0, 210 s; dumps of run
core-20261115-155040-eb68eaa matched by time, t = 0 to 2.85; figure `fig_parts.png`,
looked at: three separate families of curves, the control two to five orders above).
- HOLDS: the Hamiltonian residual of the s = 0 run is uniform (standard deviation at
  most 1.3e-26) and equals 3.03e-11 at t = 0.44, 3.24e-11 to 3.26e-11 afterwards
  (2.5e-12 to 2.9e-12 of [H]); its momentum constraint is rounding (below 3e-15).
- HOLDS: the second-order part C2(s) = E(s) - H0 has rms C2(1)/rms C2(1/2) = 4.002,
  4.004, 4.002, 3.994, 3.997, 3.995, 4.005, 3.999 at the eight dumps; the odd parts
  2.000 (H and M), the even part of M 4.000.
- Sizes at s = 1 (rms): second-order part of H 4.6e-11 at t = 0, 1.7e-11 at N = 0.44,
  about 1e-11 to N = 2.0, 9e-13 at N = 2.4; odd part of H 6.5e-12 at N = 0.44, 6.6e-10
  at N = 2.4 (5.7e-11 of [H]); odd part of |M| up to 8.1e-10 at N = 2.8. So at 32^3,
  where the highest shell has four cells per wavelength, the constraint violation of
  the entry phase is first order in the amplitude and comes from the stencils; the
  second-order part alone is at 1e-12 of [H]. Whether the first-order part converges
  away is the ladder on the card (T3d).

**T6.** Relativistic set-ups (`regress_relativistic.py`, runs core-20261115-155731-383321a
to -160856-a36abe3, fourteen runs): geo, boris, dep, east, os, jeans, binary identical
between the executable of release core-v0.3 and the new one (2, 2, 1, 12, 16, 5, 1
files). HOLDS.
Scalar-field inputs of wave 1: run core-20261115-160549-a36abe3 FAILED again on the
comparison (the lines of a parameter block are padded to its longest line, so the
neighbours of `restart_file` differ in padding); the files of that run compared with
the corrected script, run core-20261115-161240-61bb520: 120 files in ten cases (flrw in
two gauges, plane, wave, refined mesh, power sources frozen and Markov, Mukhanov-Sasaki
sources with and without kicks, restart): 110 byte-identical; 8 mesh restart files
differ only inside the 36 unset header bytes; 2 (the restarted case) only in the
recorded path of the restart file, their data identical. HOLDS. In particular the
histories, dumps, mode records and `.rst.sf` files of the stochastic sources are
byte-identical, also with the kicks off (the skipped synthesis changes no output).

## 2026-11-15, entry 8: one more run while the card job waits (job 4444, queued 15:54Z)

T8 at N = 64 (same case, nmax2 = 64, Courant 0.25, to t = 3.2, no control; 57 min on one
core). Predicted before it runs: the largest deviation |R^NR_n/(W R alpha_n) - 1| over all
modes at the last dump falls from 2.8e-3 (N = 32) by a factor between 16 and 64, i.e. to
between 4.4e-5 and 1.8e-4 (the stencils are sixth order, the integrator fourth, and
both the cell and the step halve); for |n| <= 2 it falls from 3.7e-6 by about 16 (time
integration), to below 5e-7. Refuted if the deviation of the high shells does not fall
by at least 16: it would then not be a truncation error.

T9 (added, predicted before it runs): the initial-value problem without sources (Track
E's test L3 in small): `slice_window = false`, the three kicks off, nmax2 = 16 (|n| <= 4,
eight cells per shortest wavelength at 32^3), to t = 3.2. All 128 modes are in the slice
at full amplitude, the upper ones four times inside the horizon; they oscillate, cross
and freeze under the evolution alone. Reference: L^(-3/2) R(t) alpha_n with the
unsourced mode functions of the lockstep record. Prediction: |R^NR_n/(R alpha_n) - 1| at
most 5e-3 for all modes and 5e-4 for |n| <= 2 at every dump (phase error of the sixth-
order second difference at k dx = pi/4, 1e-4 per radian over about 4 radians, and of
the integrator). Refuted by a deviation above 2e-2 (the path without window or
without kicks would then be wrong, or the field equation off).

## 2026-11-15, entry 9: outcome of T9; figures regenerated; a note on the mode files

**T9, run core-20261115-161659-38adbb8** (32^3, nmax2 = 16, no window, no kicks, to t =
3.2; figure `fig_rnr.png`, looked at: the deviation is flat in time after N = 1.5).
HOLDS: |R^NR_n/(R alpha_n) - 1| is 5.5e-11 at t = 0 for all 128 modes (2.1e-11 for |n| <=
2); at the later dumps at most 5.9e-6 for |n| <= 2 and 8.3e-4 for all modes (bounds 5e-4
and 5e-3), reached by N = 1.6 and constant afterwards within 4 percent: the modes
cross the horizon and freeze on the linear solution without any source. The largest
deviations belong to the axis modes |n| = 4 (k dx = pi/4).

Figures with a tidied layout come from repeats with the same executable and inputs:
T1 run core-20261115-161528-e09c0b1 (numbers identical to -154907-eb68eaa: looked at
`fig_slice.png`), T2/T3 analysis run core-20261115-161653-e09c0b1 on the data of
-155040-eb68eaa with the dumps matched by time (looked at `fig_evolve.png`).

Mode files (reference computation, no registered run): `make_case.py --kstart 100`
starts each mode from Bunch-Davies data where k/(aH) = 100 instead of at N0; for the 54
shells of the committed mode file the moduli agree with the integration from N0 to
1.6e-6, the complex phases do not (R differs by 5 percent, dR/dtau by 22 percent of the
largest value): a start at another time is another phase per shell, i.e. another,
statistically equivalent realisation. Runs that are compared mode by mode must use one
mode file. 214 shells take 35 s; the 3413 shells of nmax2 = 4096 about 9 minutes.

T10 (added, predicted before it runs): the case of T8 at 32^3 with `noise_level = 1`
(background of the sources from the box means of the mesh at every stage). The mesh
scale factor differs from the lockstep one by the fourth-order error of chi (5.5e-6
after 8 e-folds), so the window moves by that much. Prediction: the bounds of P8b hold
unchanged (2e-3 for |n| <= 2, 2e-2 for |n| <= 4), and the largest deviations agree with
those of level 0 (2.7e-5, 7.6e-5, 2.8e-3) within 20 percent. Refuted by a deviation
above the bounds: the path through the box means would then be inconsistent with the
slice.

## 2026-11-15, entry 10: outcome of T10

**T10, run core-20261115-162142-3407748** (`noise_level = 1`, otherwise the case of T8;
figure `fig_rnr.png` of that run, looked at: same picture as level 0 with the lowest
shells a factor 3 higher).
- The bounds HOLD: largest |R^NR_n/(W R alpha_n) - 1| after t = 0: 5.6e-5 for |n| <= 2,
  7.7e-5 for |n| <= 4, 2.8e-3 for all modes (bounds 2e-3, 2e-2); 1.05e-11 at t = 0.
- "Within 20 percent of level 0" FAILED for the lowest shells: 5.6e-5 against 2.7e-5 at
  the first dump and 1.34e-5 against 3.7e-6 from N = 2 on (factors 2.1 and 3.6). For
  |n| <= 4 and for all modes the two levels agree within 1 percent (7.66e-5 against
  7.59e-5; 2.83e-3 both). [JUDGEMENT, not tested] With level 1 the window and the
  kick coefficients take H and a from the mesh, whose chi carries the fourth-order
  error of the step, and the low shells enter first, when that is the only error
  present; halving the Courant factor would test it. Not followed up: the deviation
  is 150 times below Track E's bound.
The repeat of T8 at 32^3 for the figure (run core-20261115-161803-38adbb8) and of T3b
(run core-20261115-162128-9c13f9f) give the numbers of the first runs.

## 2026-11-15, entry 11: card runs (Slurm job 4444, one A100, 210 s of card time)

**Run core-20261115-155404-24c88e3** (queued 15:54Z, ran 16:32Z to 16:35Z; executable
`.work/exe/athena_gpu_a58e95b`, sha256 dd716bc9...26b1; 24 AthenaK runs, all with exit
status 0; card time 210 s = 0.058 card-hours of the one allowed).

**T4 card against processors, analysis run core-20261115-163549-7be94e4** (the 32^3
case, 20 steps; processor part repeated: layouts and restart bit-identical again;
figure `fig_card.png`, looked at: differences of the state fields between 1e-16 and
1e-13, the bars of the largest values many orders above).
- At t = 0 (the slice) HOLDS, and better than predicted: phi, Pi, chi, K, alpha, gt_ij,
  At_ij are bit-identical between the card and the processor; E differs by 1.4e-17;
  the constraint fields by 1.2e-13 (H, values up to 1.8e-10) and 4e-15 (M_i).
- After 10 and 20 steps the largest absolute differences are phi 4.9e-15, Pi 2.5e-14,
  chi 8.9e-16, K 3.3e-14, gt_ij 3.1e-15, At_ij 8.7e-15, E 9.7e-16, H 3.4e-13, M_i 1.1e-13:
  rounding of quantities of order one. The prediction "within 1e-11 of its largest
  value" FAILED as I wrote it for the fields that are pure perturbations: At_ij differs
  by 4.4e-8 of its largest value (2e-7) and the off-diagonal gt_ij by 7e-9; the
  criterion should have been absolute. alpha is identical.
- Records: box means of phi, Pi, K within 6.4e-13 (the running sum of the serial
  build against the reduction on the card), alpha 2.7e-14; <|H|/[H]> and <|M|/[M]>
  within 1.4e-5 and 1.0e-5, their maxima within 4.5e-3 and 3.4e-3 (bound 1e-2 HOLDS);
  rms |M_bssn - M_adm|, itself rounding (1.8e-15), differs by 10 percent, and the
  e-fold entry at t = 0 is rounding: these two columns FAIL the bound and mean nothing.

**T3d ladder N = 32, 64, 128 (nmax2 = 64, s = +-1), analysis run
core-20261115-163726-7be94e4** (figure `fig_ladder.png`, looked at: the ratios of N = 32
rise when the upper shells enter, those of N = 64 show a small bump, those of N = 128
none; the even parts of N = 64 and 128 coincide).
- P3d HOLDS. Odd part (first order) of H, rms at N = 32, 64, 128: t = 2.0: 3.87e-10,
  8.00e-12, 1.99e-13 (orders 5.60, 5.33); t = 2.4: 6.57e-10, 1.42e-11, 2.53e-13 (5.54,
  5.81); t = 2.8: 3.44e-10, 7.77e-12, 1.41e-13 (5.47, 5.78); t = 3.2: 1.63e-10, 3.51e-12,
  6.39e-14 (5.54, 5.78). Of |M|: t = 2.4: 7.52e-10, 1.61e-11, 2.96e-13 (5.55, 5.76); t =
  2.8 and 3.2: (5.52, 5.83), (5.55, 5.83). Before t = 1.6 the odd parts of N = 64 and 128
  sit on the rounding floor, which grows with N (2.7e-14, 1.1e-13, 4.3e-13 at t = 0).
  The dumps of the three resolutions are 0.44, 0.42, 0.40 after each multiple of 0.4
  (first step at or after it), so the orders carry an error of a few tenths.
- The even part of |M| is the same at the three resolutions within 1 percent (7.15e-12,
  7.13e-12, 7.18e-12 at t = 0.4; 1.85e-11, 1.86e-11, 1.87e-11 at t = 2.0): the
  second-order part does not depend on N. The even part of H at N = 64 and 128 (1.6e-11
  falling to 2e-12 and 5e-13) is the second-order part found at 32^3 in T3b (1.7e-11
  falling to 6e-13) plus the residual of the time integration (3.2e-11 at N = 32, one
  sixteenth of it at N = 64).
- Box-mean ratios: the largest value over the run is 4.7e-11 (H) and 3.7e-4 (M) at
  N = 32; at N = 64 and 128 the ratios never exceed their values at t = 0, 2.6e-12 and
  1.46e-5. At t = 2.4: <|H|/[H]> = 4.65e-11, 1.01e-12, 6.6e-14 (orders 5.5, 3.9), <|M|/[M]>
  = 3.0e-4, 6.5e-6, 9.0e-7 (5.5, 2.9): between 4 and 6 from 32 to 64 (Track E's A5),
  lower from 64 to 128, where the second-order part is reached.
- P3e HOLDS in part: rms |M_bssn - M_adm| is at most 8.5e-14 at N = 32 (3.2e-4 of rms
  |M|) and 4.4e-15 at N = 64 (order 4.3), but 7.3e-15 at N = 128: it has reached
  rounding and does not fall further, and relative to |M|, which falls faster, it
  rises to 6.9e-3. A wrong sign of the Christoffel terms would show at 5 to 20 percent
  of |M| ([JUDGEMENT] from Gt x At of order k (2e-7)^2 against |M| of 3e-12 to 1e-11).

**T5 on the card.** U9 (U2 of the scaled base case on the card) against the processor
runs, validation run core-20261115-163855-7be94e4 (reference as committed, hence exit
status 1 from the known A1 of Markov tanh): A14 PASSES, largest relative difference
1.3e-15 (bound 1e-12), not bit-identical. Prediction HOLDS.
Full base case of NOISE_SPEC 9 (64^3, nmax2 = 256, 300 steps, U1 to U8, 1.7 to 9.5 s
each on the card), validation run core-20261115-163910-7be94e4: with the reference as
committed frozen tanh passes every test (A1 9.8e-14; 1, 8, 64 MeshBlocks bit-identical
on the card; restart at cycle 150 bit-identical; N = 32 against 64 3.5e-15; seeds
independent), Markov Heaviside passes (A1 2.6e-15), Markov tanh fails A1 at 8.5e-10;
with the cancellation-free reference all three pass, A1 = 4.9e-15, 4.0e-15, 2.6e-15.

**Cost on one A100** (runs cost* of the card job; zone-cycles per second of the main
loop; slow-roll case with the slice, nmax2 = (N/4)^2, one MeshBlock unless said):

| Configuration | 128^3, 20 steps | 256^3, 10 steps |
|---|---|---|
| field and spacetime, kicks off (no synthesis), no constraint record | 1.634e7 | 1.654e7 (1.01 s per step) |
| with the sources (six fields synthesized at each stage; 68532 and 548958 modes) | 1.484e7 | 1.393e7 (1.20 s) |
| and the constraint record every step | 1.459e7 | 1.364e7 (1.23 s) |
| sources, eight MeshBlocks of 128^3 | | 1.290e7 (1.30 s) |

So the sources cost 10 percent at 128^3 and 19 percent at 256^3, the constraint record
2 percent; a 256^3 run of 1304 steps (Track E's slow-roll case at Courant 0.25) is
0.45 card-hours with the record every step, the 1630 steps of the other case 0.56.
The start (slice, tables) takes about 1 s at 256^3. On one processor core the 32^3
case with sources and record runs at 1.06e4 zone-cycles per second (run
core-20261115-155040-eb68eaa: 172 steps in 534 s).

## 2026-11-15, entry 12: second session; published COMMIT corrected; predictions of T12

A new session (no memory of entries 0 to 11) took the package over at 17:47Z. Read:
`CLAUDE.md`, charter to "Owners", brief 493-553, 688-706, 834-860, this journal, the
interface proposal, Track E's four requests (unchanged on `track/E-stoch-inf` since
6330493 in `outbox/`, `spec/`, `noise/`), SCOPE section 4 (A1 to A8). Merged main
(harness wave 2; nothing under `athenak/`): `git diff a58e95b6 HEAD -- athenak/` is empty.

State found and what was done:
- The executables were published at 16:43Z with READY, but the file COMMIT named
  `a58e95b4`, which is no commit (a typing error in the call of `publish.sh`; the source
  is a58e95b6ebd41a6f0fdc388f6fe3d2468ad1eebc). `publish.sh` now resolves the commit with
  `git rev-parse --verify`, refuses a commit whose `athenak/` differs from HEAD, and
  replaces files by rename (a run starting during a copy never sees a partial file);
  rerun at 17:49Z: both executables unchanged (sha256 dd716bc9...26b1 card, c69266ec...
  9439e processors), COMMIT now carries the full hash. The READY text is kept in the
  repository (`tracks/core/analysis/scalar2/READY.txt`) with a dated correction line.
- Run core-20261115-161513-e09c0b1 (T8 at N = 64, entry 8) was still "running" in its
  manifest: it stopped at cycle 74 of about 131 (t = 1.82) when the first session ended;
  no analysis ran. Manifest set to "stopped" by hand. Its prediction (entry 8) stands
  and is tested again below (T12, run p1).
- `harness/bin/nrpic-run` reads core's manifests again after the merge of main (budget:
  G2 used 2.43 of 40 card-hours); new runs are registered with `nrpic-run submit`.
- Left uncommitted by the first session and committed now (ec07103): the card rows of the
  interface proposal, the figures in `tracks/core/notes/scalar2_figs/`, one manifest.
- Looked at `fig_ladder.png`, `fig_card.png`, `fig_evolve.png`, `fig_slice.png`: they
  show what entries 4 to 11 state. `fig_card.png` has its legend over the dots of At_ij
  and the exact zeros drawn at 1e-30 without a word; redrawn below.

T12 (added; why): Track E's A4 (SCOPE 4) asks that H/[H] and M/[M] "scale with the
square of the noise amplitude when it is halved". Entries 6 and 7 tested the parts of the
constraint fields at N = 32 only, never the record's ratios in that form, and the ladder
(entry 11) has s = +-1 only. [M] (P1:735-745) is a sum of terms that vanish on the
background, so it is first order in s; [H] is background-dominated (12.0000013 in run
core-20261115-154907-eb68eaa). [JUDGEMENT] Hence a second-order M gives a factor 2 in
<|M|/[M]> per halving, not 4 (entry 4 found 2.0000 at t = 0), and a first-order one 1.
Runs: N = 64 on processors, s = 1, -1, 1/2, -1/2, 0, to t = 3.2, dumps every 0.4 with
the metric and the constraint fields (five cores, about an hour each); N = 32 from the
runs that exist (core-20261115-155040-eb68eaa: bg025, m1, p05, m05; -161040-760b515: p0).
Driver `tracks/core/analysis/scalar2/t12_halving.py`. F_H, F_M: ratio of the record
columns <|H|/[H]>, <|M|/[M]> between s = 1 and s = 1/2 at equal cycles.

Predictions (numbers used: entries 6, 7, 11; none of the quantities below has been
computed before):
- P12a t = 0: F_H = 4.00 +- 0.02 and F_M = 2.000 +- 0.002 at both N.
- P12b The s = 0 run at N = 64 has a uniform H0 (spatial standard deviation below 1e-3 of
  its mean) of 1.5e-12 to 2.5e-12 for t >= 0.8, one sixteenth of the 3.24e-11 of N = 32
  (fourth order in the step, which halves with the cell).
- P12c Second-order part C2 at N = 64: rms ratio C2(1)/C2(1/2) = 4 +- 0.2 at every dump
  with t > 0; C2(1) equal to that of N = 32 within 10 percent for t <= 1.6 (it does not
  depend on N). Odd parts: ratio 2.00 +- 0.05 where they exceed 1e-13 (rounding).
- P12d Record factors, N = 64: F_M in [1.9, 2.05] for 0.3 <= e-folds <= 1.6 and in [1.0,
  1.3] for 2.4 to 3.2 (first-order part dominant there: odd |M| 1.6e-11 against an even
  3e-12 on the card, entry 11). F_H in [2.2, 3.8] for 0.3 to 1.6 (H0 2e-12 against C2/4
  of 2.5e-12 to 4e-12 at s = 1/2) and in [1.8, 2.3] for 2.4 to 3.2. With H0 subtracted,
  G_H = rms(H(1) - H0)/rms(H(1/2) - H0) in [3.8, 4.05] for t = 0.4 to 1.6.
- P12e Record factors, N = 32: F_H in [1.0, 1.6] for 0.3 to 1.6 (H0 of 3.2e-11 dominates),
  [1.8, 2.05] for 2.4 to 3.2; F_M in [1.75, 2.0] for 0.3 to 1.2 and [1.0, 1.1] for 2.4
  to 3.2.
- So Track E's A4, read literally, fails at N = 32 and 64 during the late entry (first-
  order truncation part) and for H also early (amplitude-independent H0); the second-
  order part alone passes. Refuted if F_M is near 4 early (then [M] would not be first
  order and my reading of the magnitudes is wrong), if H0 at N = 64 is not 1.5e-12 to
  2.5e-12, or if C2 depends on N by more than 10 percent.
- P8 at N = 64 as written in entry 8: largest deviation over all modes at the last dump
  between 4.4e-5 and 1.8e-4 (2.8e-3 at N = 32 divided by 16 to 64); |n| <= 2 below 5e-7.

Run core-20261115-175447-764390e STOPPED after 3 minutes (no result): `nrpic-run` starts
the command without a shell, so the argument `--out $NRPIC_RUN_DIR` reached the driver
literally and the five runs wrote into a directory named `$NRPIC_RUN_DIR` in the
worktree. Stopped with `nrpic-run stop`, the partial output moved to
`scratch/core/core-20261115-175447-764390e/out_unexpanded/`, closed as stopped. The
driver now takes the run directory from the environment and refuses an unexpanded one.

Rerun of T12 registered as core-20261115-175842-7d54ff5 (five cores, started 17:58Z).
Figure-only repeat of the card comparison (analysis of the files of
core-20261115-163549-7be94e4 and the card run -155404-24c88e3, no AthenaK run): the
summary must equal that of -163549-7be94e4 in every number; only `fig_card.png` changes.

18:10Z, code check of the T12 analysis (not registered, numbers not used: the driver run
with --analyse-only on the partial files of -175842-7d54ff5, t <= 0.8 at N = 64, into
`scratch/core/tmp/scalar2/t12_dry/`). It showed, before the registered analysis, two
outcomes against the predictions above: at N = 32 F_H lies at 0.75 to 0.87 for 0.2 to
1.3 e-folds (P12e: [1.0, 1.6]), at N = 64 F_H rises to 5.0 at N = 0.2 (P12d: [2.2,
3.8]). G_H (H0 subtracted), F_M and the rms factors of |M| lay where predicted. I had
treated H0 and the second-order part C2 as independent in size; a box ratio below 1 and
one above 4 need a mean of C2 of the sign opposite to H0. Prediction written now, before
looking at the summary column that tests it (`H_c2_mean_1`, added to the driver at
18:11Z): the box mean of C2(s = 1) is negative, H0 positive, and <C2(1)> = -8e-12 within
30 percent at t = 0.4 to 0.8 at both N (from F_H: N = 32, |H0 + <C2>|/|H0 + <C2>/4| = 0.8
with H0 = 3.2e-11; N = 64, H0 = 2e-12 and F_H near 5 need <C2>/4 close to -H0). Refuted
by a positive mean or one of another size: then the factors come from the fluctuations,
not from the means.

## 2026-11-15, entry 13: outcome of T12 (run core-20261115-175842-7d54ff5); T12b predicted

Five runs at 64^3 on processors, 2790 to 2911 s each, exit 0; analysis by the driver at
commit 7d54ff5 (`summary.json` of the run; record factors in narrower windows and the
mean of C2 from the analysis-only repeat below, which reads the same files).
- P12a HOLDS: t = 0, F_H = 4.005 (N = 32), 4.021 (64); F_M = 2.0000 at both.
- P12b HOLDS: H0 at N = 64 uniform (standard deviation at most 2e-27 against a mean of
  1.75e-12 to 1.91e-12 for t >= 0.4); N = 32 3.03e-11 to 3.26e-11; ratio 17.1, fourth
  order in the step.
- P12c HOLDS for C2: rms ratio C2(1)/C2(1/2) 3.96 to 4.01 at every dump after t = 0
  (N = 64; N = 32 3.99 to 4.005); C2(1) of N = 64 against N = 32 at t <= 1.6: 1.740e-11
  against 1.681e-11 (t = 0.42 against 0.44, dumps not at equal times), 9.43e-12 against
  9.68e-12, 1.197e-11 against 1.186e-11, 9.902e-12 against 9.904e-12: within 3.5 percent.
  FAILED for the odd parts at N = 64 for t <= 1.2: rms 3.6e-13 to 5.0e-13 with ratios
  1.33, 1.61, 1.88 (M: 1.5e-13 to 1.8e-13, ratios 1.08 to 1.49), not 2.00. At t = 0 the
  odd part (1.07e-13) has ratio 0.999: it is rounding that does not scale with s, and
  during the evolution this floor rises to a few 1e-13 at N = 64 (entry 11 saw it grow
  with N); my "1e-13" was too low. From t = 1.6 on, where the odd part exceeds 1.4e-12,
  the ratios are 1.997 to 2.000.
- P12d: F_M HOLDS ([1.951, 1.996] for 0.3 to 1.6 e-folds; [1.001, 1.005] for 2.4 to 3.2).
  F_H FAILED: [3.31, 4.58] for 0.3 to 1.6 (predicted [2.2, 3.8]), 5.04 at 0.17 e-folds,
  and [1.52, 1.95] for 2.4 to 3.2 (predicted [1.8, 2.3]). G_H with H0 subtracted HOLDS:
  3.961, 3.988, 3.985, 3.863 at t = 0.42 to 1.62; 2.555 at 2.0 and 2.003 to 2.015 after.
- P12e: F_H FAILED below its range: [0.83, 0.87] for 0.3 to 1.2 e-folds and 0.756 at
  0.15 (predicted [1.0, 1.6]); [1.90, 1.99] for 2.4 to 3.2 HOLDS. F_M [1.777, 1.852] for
  0.3 to 1.2 HOLDS ([1.75, 2.0]), [1.000, 1.000] for 2.4 to 3.2 HOLDS.
- P8 at N = 64: largest deviation over all 1054 modes at the last dump 5.89e-5 (N = 32:
  2.8e-3, factor 47.5; predicted 4.4e-5 to 1.8e-4) HOLDS; |n| <= 4: 1.77e-6 (N = 32:
  7.6e-5, factor 43). |n| <= 2: 1.20e-6 from N = 1.2 on, constant to 1 percent, against
  3.7e-6 at N = 32 (factor 3.1): "below 5e-7" FAILED. Track E's A2 bound is 2e-2.
So Track E's A4 read on the record ratios fails at N = 32 and 64 also where the second-
order part alone passes: the uniform H0 changes F_H in both directions (0.76 at N = 32,
5.04 at N = 64). With H0 subtracted (one run at s = 0) H is second order before the late
entry at N = 64 (G_H 3.86 to 3.99), and M/[M] halves (F_M 1.95 to 2.00, second order);
during the late entry (2.4 to 3.2 e-folds) both constraints are first order at N = 32 and
64 (the truncation part of entry 11).

T12b (added, predicted before it runs): the floor of the lowest modes in P8 (1.2e-6 at
N = 64, constant after N = 1.2) [JUDGEMENT] may be the second-order part of R^NR (terms
quadratic in the perturbations, relative size of order the rms of R, about 1e-5), which
does not converge with N. Test on the dumps of the same run: the part of R^NR odd in s,
O_n = [R^NR_n(s = 1) - R^NR_n(s = -1)]/2, against L^(-3/2) W R alpha_n: for |n| <= 2
its deviation falls below 3e-7 after N = 1.2 (at least four times below 1.2e-6); the run
s = 1/2 alone gives 6e-7 +- 20 percent (half of the s = 1 value). Refuted if the odd part
keeps 1.2e-6: the floor would then be first order (an error of the evolution or of the
linear reference of the record).

Run core-20261115-184925-71663b2 FAILED at once (exit 2, no output): the analysis-only
repeat was started without a way to point at the files of -175842-7d54ff5 (an argument
the driver does not have). The driver now takes `--data`.

## 2026-11-15, entry 14: outcomes of the C2-mean prediction and of T12b

Analysis runs core-20261115-184939-657c2e4 (numbers) and -185018-5fed4ea (the same
numbers, legend moved; `fig_halving.png`, looked at: F_H of N = 64 above 4 to N = 0.6
and of N = 32 below 1 to N = 1.3, the open circles with H0 removed near 4, F_M on 2 then
on 1, the parts of H, and the lowest modes of R^NR with their odd part a factor five
lower). Parts identical to the run's own analysis.
- Mean of C2 (entry 12, 18:10Z): H0 positive at both N, <C2(1)> negative at every dump
  to t = 2.4: N = 32: -1.028e-11 (t = 0.44), -6.14e-12 (0.83); N = 64: -1.067e-11
  (0.42), -6.02e-12 (0.81). Sign HOLDS; size "-8e-12 within 30 percent" holds at three
  of the four points, -1.067e-11 is 33 percent off. <C2> is about 60 percent of the rms
  of C2 (1.68e-11, 9.7e-12): the second-order part of H is mostly a negative uniform
  shift, which offsets the positive H0 at s = 1 (N = 32: |3.03e-11 - 1.03e-11| against
  |3.03e-11 - 0.26e-11|, ratio 0.72; F_H 0.76 to 0.87) or at s = 1/2 (N = 64: H0 1.75e-12
  against <C2>/4 = -2.7e-12; F_H up to 5.04).
- T12b HOLDS at four of five dumps after N = 1.2: the part of R^NR odd in s deviates
  from W R alpha by 3.13e-7 (N = 1.19), then 2.48e-7, 2.29e-7, 2.24e-7, 2.23e-7, 2.23e-7
  for |n| <= 2 (bound 3e-7; 1.2e-6 with both orders); the run s = 1/2 alone gives 6.00e-7
  to 6.48e-7 (predicted 4.8e-7 to 7.2e-7). So the floor of the lowest modes at N = 64 is
  the second-order part of R^NR (it scales with s), not an error of the evolution; the
  first-order part agrees with the linear solution to 2.2e-7. For all modes the odd part
  equals the total (5.886e-5 against 5.889e-5 at the last dump): the deviation of the
  high shells is first order (truncation, entry 11).

## 2026-11-15, entry 15: state of the package at 18:55Z (for a reader with no memory)

Delivered on `core/scalar-2` (source of `athenak/` unchanged since a58e95b6):
`id = stochastic` (initial slice at N*), constraint magnitudes and the record
`.sf.con.hst`, dumps NRSFDMP2, `noise_mode_scale`; executables published in
`scratch/core/exe/core_scalar-2/` (COMMIT with the full hash since 17:49Z, READY updated
18:51Z with T12); interface proposal `tracks/core/interfaces/scalar_field_2.md`; reply to
Track E `tracks/core/outbox/20261115T1855Z__to-E-stoch-inf__scalar2-ready.md`. Tests T1
to T12b with predictions and outcomes in entries 2 to 14; failed predictions and failed
runs are listed in section 6 of the interface proposal. Card time used by the package:
210 s (job 4444, first session); none in the second.

Open: `rng::ModeEntity` and the rng.md wording (Track E's request (c)); the inflection
(USR) case with the slice; any run beyond 128^3 with dumps; refined meshes and a* other
than 1; a second seed; the lead's merge into `core/nrpic` and the release. Core's shared
`HANDOFF.md` and `STATUS.md` were not touched by this package (other core packages run
beside it); this entry is the package's handoff.
