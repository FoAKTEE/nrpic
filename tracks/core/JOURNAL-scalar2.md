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
