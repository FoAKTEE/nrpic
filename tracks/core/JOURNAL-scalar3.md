# Journal of core, package scalar3 (scalar field, third pass, for Track E)

Branch `core/scalar-3` (from `core/scalar-2` at 207424d, main merged at 34489ec), worktree
`wt/core-scalar3`. Append-only. Labels [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY];
a number carries a run id (`tracks/core/runs/<run_id>/manifest.json`, outputs
`scratch/core/<run_id>/`), a file of this repository, or a locator in a paper source under
`kb-data/raw/arxiv/`. Paper keys: P1 = arXiv:2512.14649 v2 `PRD_v2.tex`, P2 =
arXiv:2502.06783 v3 `main_V2PRD.tex`. SPEC = `tracks/E-stoch-inf/spec/SPEC.md`, RNGREQ =
`tracks/E-stoch-inf/noise/RNG_REQUIREMENTS.md`, both on `track/E-stoch-inf` at 73b0fdb.
J2 = `tracks/core/JOURNAL-scalar2.md` (tests T1 to T12b of the second package).

## 2026-11-19, entry 0: what was read, and the state found (14:22Z to 14:40Z)

Read: `CLAUDE.md`; charter to the end of "Owners"; decisions 0010, 0016, 0017;
`harness/RULES.md`; brief 493-553, 688-706, 834-860; `tracks/core/interfaces/
scalar_field.md`, `scalar_field_2.md`, `rng.md`, `cosmo_gauge.md`; J2 whole; Track E's four
requests to core of 2026-11-15T14:10Z, core's reply of 18:55Z, SPEC whole, RNGREQ, the
README of Track E's ladder; the module `athenak/src/scalar_field/` (noise, slice, rhs,
tasks), `utils/rng.hpp`, `utils/rng_mesh.hpp`, `python/nrpic/rng.py`, `sf_inflation.py`,
`scalar_field.py`; `z4c/z4c_calcrhs.cpp` 300-730 and `z4c/z4c_adm.cpp` 250-470 (which
difference operator each term of the right-hand side and of the constraints uses);
`z4c/z4c_gauge_ext.hpp` and the READY file of branch `core/gauge` (b4430da).

Found:
- `git diff a58e95b6 HEAD -- athenak/` is empty after the merge of main: the source of this
  branch is that of the published executables of `core/scalar-2`.
- [VERIFIED at the source, P1:409] The inflection potential of the code
  (`scalar_field.hpp`, `SfPotentialEval`, kind 3) is the printed one, V = Lambda v^4 phi^2
  (3 phi^2 + 2 sqrt2 phi v + 6 v^2)/(3 (3 phi^2 + 2 v^2)^2), with Lambda = 1.86e-6, v =
  0.198 Mpl, phi0 = -1.2 Mpl (P1:411-413), N* - N0 ~ 3, N_f - N* ~ 10 (P1:419-420). The
  label [TO VERIFY] of `scalar_field.md` section 3 is settled. Code units: lambda = 8 pi
  Lambda/H*^2, vev = v/sqrt(8 pi) (substitution phi = sqrt(8 pi) phi_code in the printed
  form; `sf_inflation.code_case`).
- [VERIFIED at the source, P1:538-541] P1 reports for the inflection case |M|/[M] "around
  1e-2" late, "acceptable given inhomogeneity of order 10 in R", and for the quadratic
  case that the last mode crossing lifts |M|/[M] above second order "because of the
  gradient resolution", which "a smaller k_max would fix".
- Lapse on this branch (`z4c_calcrhs.cpp` 687-708): d_t alpha = -[lapse_oplog
  lapse_harmonicf + lapse_harmonic alpha + lapse_volume chi^(-1/2)] alpha Khat -
  lapse_kdriver alpha_ref alpha (Khat - Khat_ref), the reference values (largest lapse,
  proper-volume mean of Khat) formed in `Z4c::CalcRHS` itself (lines 46-69), so the driver
  works without the particle module. The relaxed lapse of `core/gauge` (`lapse_leak`:
  d_t alpha += -(alpha/T) max(ln(alpha/alpha_0), 0), in a loop of its own after the main
  loop, seven lines in three shared files plus `z4c_gauge_ext.hpp`) is not here.
- The card queue at 14:27Z: two jobs of other users running, one waiting, four jobs of
  other core sessions and one of Track B waiting.
- Seen before any prediction below was written (unregistered smoke run of the new example
  input at 16^3, two steps, `scratch/core/scalar3/smoke/`): the run starts and prints H =
  1.000000, eps1 = 1.316389e-2, eps2 = -0.4306631 for the slice; and an unregistered
  evaluation of the reference (`scratch/core/scalar3/explore/usr_ref.py`): the background
  of the inflection case in e-folds (eps2 > 3 from 2.53 to 6.55 after N*; eps1 from
  1.3e-2 to 9.7e-13; H falls to 0.9518 H*) and the linear growth of four shells (Delta_R
  of |n| = 8 from 2.6e-11 at 3 e-folds to 1.5e-2 at 10; of |n| = 1 from 1.2e-10 to
  1.0e-5). The predictions of entry 2 on these quantities are therefore not blind; no
  output of AthenaK on the evolved case has been looked at.

## 2026-11-19, entry 1: design, and a derivation for item (3)

**(1) Mode entity.** `rng::ModeEntity(nx, ny, nz)` = `CellEntity(n + 2^20)` and
`rng::StochasticModeStream(dof)` = `Stream(kStreamStochastic, 2^16 + dof)` in
`utils/rng_mesh.hpp` (request R-1 of RNGREQ names that file), with the constants
`kModeEntityOffset`, `kStochasticModeBit`; twins `rng.mode_entity`,
`rng.stochastic_mode_stream` in `python/nrpic/rng.py`. `NoiseDrawAlpha` and
`scalar_field.mode_alpha` call them; the keys are the same integers as before, so every
amplitude is unchanged. Wording of stream 3 and of rule 2 in
`tracks/core/interfaces/rng.md` (requests R-2, R-3).

**(2) Inflection case.** No source change is expected to be needed: potential, slice,
sources and records exist. New: example input `problems/scalar/usr_stochastic.athinput`
with its mode file, drivers under `tracks/core/analysis/scalar3/`.

**(3) Where the first-order constraint violation at late entry comes from** (own
derivation; [JUDGEMENT] until test A below has compared it with the runs). Linearise the
equations the code solves about the homogeneous background in geodesic slicing with zero
shift, for one wave vector, writing the symbols of the centred differences as D1_a -> i
q_a, Dxx_a -> -kap_a, Dxy_ab -> -q_a q_b, K2 = sum_a kap_a, q^2 = sum_a q_a^2, and mu_a =
kap_a - q_a^2 (the mismatch between the second difference and the first difference
applied twice; mu/k^2 = 0.110 at k dx = pi/2 and 2.6e-3 at pi/4 for the sixth-order
stencils, from the coefficients of `utils/finite_diff.hpp`), mub = (mu_x + mu_y + mu_z)/3.
Perturbations: chi = a^-2 (1 + c), gt_ab = delta_ab + h_ab, At_ab = A_ab, Khat = -3H +
kap, Theta = th, Gamma^a = G_a, phi = phi_b + f, Pi = Pi_b + p. From `z4c_calcrhs.cpp`
(conformal Ricci tensor 0.5 (d_a G_b + d_b G_a) - 0.5 Dcc h_ab; conformal-factor part
-(1/2)(P_ab + delta_ab K2) c with P_ab = kap_a delta_ab + q_a q_b (1 - delta_ab)):

    dc/dt    = (2/3)(kap + 2 th),     dh_ab/dt = -2 A_ab
    dA_ab/dt = a^-2 [rho_ab - (1/3) delta_ab tr rho] - 3H A_ab + kick,
               rho_ab = (i/2)(q_a G_b + q_b G_a) + (1/2) K2 h_ab - (1/2)(P_ab + delta_ab K2) c
    dkap/dt  = -2H (kap + 2 th) + 4 pi (4 Pi_b p - 2 V' f) + kick
    dth/dt   = (1/2) dH_rhs   (Z4c),  dH_rhs = a^-2 (i q.G - 2 K2 c) - 4H (kap + 2 th) - 16 pi (Pi_b p + V' f)
    dG_a/dt  = -(2/3) i q_a (2 kap + th) + 16 pi Pi_b i q_a f
    df/dt    = p,    dp/dt = -a^-2 K2 f - 3H p + Pi_b (kap + 2 th) - V'' f + kick

and the constraints of `Z4c::ADMConstraints` (ADM metric, D1 for first and Dxx/Dxy for
second derivatives): dH = a^-2 (-2 K2 c - sum_ab P_ab h_ab) - 4H (kap + 2 th) - 16 pi (Pi_b
p + V' f), dM_a = i [q_b A_ab - (2/3) q_a (kap + 2 th) + 8 pi Pi_b q_a f]. The kicks
(Pi_b/H) I, -eps1 I, eps1 (delta_ab/3 - q_a q_b/q^2) I cancel in dH and, with the stencil
projector, in dM_a, exactly. Differentiating the constraints with these equations gives
(with Z_a = G_a - i q_b h_ab the connection constraint)

    d(dH_rhs)/dt = -6H dH_rhs - 4 mub a^-2 (kap - 12 pi Pi_b f) + terms in th
    d(dM_a)/dt   = -3H dM_a - (1/2) i q_a dH_rhs + i B_a,
    a^2 B_a      = (3/2) mub q_b h_ab + (1/2) q_a (3 mub - mu_a) c + (i/2) q^2 Z_a

So the linear constraints of the mesh are not preserved by the mesh's own linear
evolution: they are driven by the linear solution itself times mu, the defect of the
discrete contracted Bianchi identity. Three consequences, each a prediction of test A:
(i) the first-order part scales as mu(k dx): factor 0.110/0.0026 = 43 between k_max dx =
pi/2 and pi/4 (J2 entry 11 measured ratios 46 and 56 between N = 32, 64, 128); (ii) it
vanishes if kap_a = q_a^2 for all a, i.e. only if every second derivative is the first
difference applied twice, which is a change of the stencils of the spacetime solver (or
seven more synthesized source fields per stage built from a six-variable linear solution
per shell), not of the entering shell; (iii) it does not depend on which k^2 the mode
functions of the sources use. If (i) to (iii) hold, item (3) of the work package is an
analysis: there is no small change, and the criterion fixes k_max dx.

[JUDGEMENT] Why not the "stencil k^2 in the mode equation" of SPEC 10.3 as the
treatment: it would make the per-mode reference follow the lattice dispersion (test
T8), not remove the constraint part, and it replaces the physical k^2 of a mode by one
that is 1.8 percent low at k dx = pi/2. The twin of test A can say what it would buy
before any source is written.

**(4) Gauge.** Analysis plus three cheap tests (G1 to G3, entry 2). The sources carry the
box mean of the lapse (`kick_*_fac`, `NoiseModeRHS`), tested so far with alpha = 1 only.
[JUDGEMENT] Since the source term is a first-order tensor on a background where it
vanishes, its components do not change under a first-order change of slicing, so the
same kicks should serve any lapse condition whose background part is homogeneous; R^NR =
psi + (H/Pi_b) delta phi is invariant under a first-order time shift. G1 and G2 test this.

## 2026-11-19, entry 2: predictions (written before the registered runs)

Executable of all runs unless said: `.work/exe/athena_cpu_<commit>` of this worktree,
source of the commit that carries this entry.

**T0 mode keys** (`t0_modekey.py`, no AthenaK run). P0a: `rng.mode_entity(n)` equals
`rng.cell_entity(n + 2^20)` for the 548958 wave vectors of nmax2 = 4096 and for the
corner values -2^20 and 2^20 - 1; values outside are refused. P0b: `mode_alpha` (new
helpers) equals the amplitudes of Track E's independent `noise/ref/philox_ref.py` bit
for bit for nmax2 = 100, seeds 1 and 20261115, degrees of freedom 0 and 1, epochs 0 and
7. Refuted by one differing bit.

**R regression** (`t6_regress.py` of the second package and `tools/
regress_relativistic.py`, processors). PRa: the ten scalar-field cases of wave 1 (120
files) are byte-identical between the executable of release core-v0.3
(`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`) and the new one, but for the 36
unset header bytes of mesh restart files and the recorded restart path (J2 entry 7); the
seven relativistic set-ups (geo, boris, dep, east, os, jeans, binary) byte-identical.
PRb: the slow-roll example `sr_stochastic.athinput` (32^3, 20 steps, dumps and records)
is byte-identical between the published executable of `core/scalar-2` and the new one.
Refuted by any differing data byte.

**U inflection case, processors** (`u1_usr.py`: 32^3, nmax2 = 64, box 2 pi, seed
20261115, Courant 0.25, geodesic slicing, level 0, to t = 10.5, i.e. 10.07 e-folds; runs
p1, m1 (s = +-1), p01, m01 (s = +-0.1), z0 (s = 0), c0125 and z0c0125 (Courant 0.125),
ctl (`noise_pi_sign = -1`, to t = 3.2)). Reference: `sf.ms_reference` (SciPy, from phi0,
pi0 and the mode file).
- PU1 background (Track E's A1: 1e-4). Box means of phi and K within 1e-6 of the
  reference throughout. Pi falls by five orders with the rate 3H, which RK4 integrates
  with the relative error 3HT (3H dt)^4/120 = 4.7e-5 over the four e-folds of ultra slow
  roll at H dt = 0.049; afterwards Pi is set by V' at the place where the field came to
  rest, 2e-4 Mpl beyond the stationary point of V', so that an error of the path is
  amplified: relative error of <Pi> between 1e-5 and 1e-4 at 5 e-folds and between 5e-5
  and 1e-3 from 8 e-folds on at Courant 0.25 (A1 is then missed late for Pi at this
  step), 16 +- 4 times less at Courant 0.125. Box mean against the lockstep background
  of the same run: within 5e-6 (both carry the same integration error). e-folds from
  <chi> against ln a: below 3e-5 at the end, ratio 16 +- 2. Refuted if phi or K miss
  1e-6, if Pi is off by more than 1e-3 at Courant 0.25, or if the errors do not fall
  with the step.
- PU2 mode functions of the sources (lockstep record against SciPy at the dump times).
  For |n| <= 2 within 1e-4 at Courant 0.25; for the top shell |n| = 8 within 3e-3 (phase
  error of RK4 before the entry, (k dt)^5/120 per step with k dt = 0.39 at the start);
  where |R| passes its minimum between 3 and 4.5 e-folds the relative deviation may be
  ten times larger. Ratio Courant 0.25 to 0.125: 16 +- 4 away from that dip. The growth
  through ultra slow roll (|R| of every shell at the end 300 to 24000 times its value
  at 3 e-folds) is reproduced within these bounds. Refuted by a deviation above 3e-2
  outside the dip or by a ratio below 8.
- PU3 residual of the time integration (run z0): <|H|/[H]> between 3e-12 and 2e-10 for
  0.5 to 3 e-folds (the quadratic case had 2.9e-12; here eps1 is twice as large and
  eps2 passes from -0.4 to 5), uniform (spatial standard deviation below 1e-20), and
  16 +- 4 times less at Courant 0.125. During ultra slow roll nothing drives it and it
  decays: below 1e-13 at 8 e-folds. Refuted if it stays above 1e-12 at 8 e-folds.
- PU4 constraints of run p1. Record maxima over the run: <|H|/[H]> between 2e-11 and
  1e-9, reached between 1.5 and 3 e-folds (first-order truncation part of the entering
  shells, mu eps1 H R; 4.7e-11 in the quadratic case, J2 entry 6); <|M|/[M]> below 3e-3
  until 3 e-folds. Odd parts (dumps of p1 and m1) scale by 10.0 +- 0.5 against those of
  p01, m01 where above 1e-13, even parts minus the z0 field by 100 +- 20. [JUDGEMENT]
  In ultra slow roll the metric perturbations stay at their size of the entry (the
  growth of R is carried by delta phi/Pi_b with Pi_b falling; delta phi itself is
  frozen near 3e-6 rms and psi near 1e-6), so no constraint grows: <|H|/[H]> below
  1e-10 from 4 e-folds on and falling; <|M|/[M]> is then a ratio of two small numbers
  ([M] falls with Pi_b): between 1e-5 and 0.3 from 4 e-folds on (P1:541 reports 1e-2
  late at 256^3). Refuted by a growing Hamiltonian ratio in ultra slow roll (it would
  mean a metric response to R of order one, against the estimate), or by <|M|/[M]>
  above 1.
- PU5 curvature perturbation per mode (dumps with the metric; extraction and reference
  as test T8 of J2: R^NR_n against L^(-3/2) W R alpha_n of the lockstep record).
  (a) t = 0: within 1e-8 for the modes with W > 1e-3. (b) During the entry, up to 2.5
  e-folds: within 2e-3 for |n| <= 2, 2e-2 for |n| <= 4 and 2e-2 for all modes with W >
  1/2 (quadratic case: 2.7e-5, 7.6e-5, 2.8e-3). (c) After 6 e-folds the part of R that
  has grown is the gradient-induced one, proportional to k^2 on the lattice, so the
  error of the lattice k^2 enters fully: odd part of the pair s = +-0.1 against the
  reference: 0.5 to 2.5e-2 for the shell |n| = 8 (the second difference is 1.8 percent
  low along an axis at k dx = pi/2; the reference uses the continuum k^2), below 2e-3
  for |n| <= 4 (3.8e-4 at k dx = pi/4), below 3e-4 for |n| <= 2. (d) Higher orders: R
  per mode reaches 1e-3 and its rms 0.06 at s = 1, where delta phi is 7 percent of the
  distance of the background from the stationary point of V'; the single run p1 then
  deviates from the linear reference by 1e-2 to 0.3 for |n| <= 2 after 7 e-folds while
  the odd part of the pair s = +-0.1 stays below 3e-4 there. (e) Control: deviation
  above 0.5 for the modes that have entered.
  Refuted: (c) by a top-shell deviation below 3e-3 or above 0.1 (the estimate of the
  k^2 error would be wrong), or by low modes above 2e-3 with s = +-0.1 (an error of the
  sources or of the slice in this case); (d) if p1 alone agrees to 1e-3 for |n| <= 2
  (then nothing is non-linear at this amplitude and my estimate of delta phi against
  the potential is off).

**G gauge** (`g1_gauge.py`; quadratic case, 32^3, nmax2 = 64, Courant 0.25, to 3.3
e-folds of the background, extraction as T8).
- PG1 `lapse_harmonic = 0.05` (d_t alpha = -0.05 alpha^2 Khat: the lapse of the
  background grows from 1 to about 1.8 and is perturbed at first order). Box means
  against the lockstep background within 1e-8 (phi, Pi, K) and the mean lapse within
  1e-6 of 1/(1 - 0.15 int H dt) evaluated with the lockstep H; R^NR_n/(W R alpha_n) - 1
  within the bounds of T8 (2e-3 for |n| <= 2, 2e-2 for |n| <= 4) and within a factor 3 of
  the geodesic run of the same driver for all three classes. Refuted by a deviation of
  order eps1 (1e-2) or more for |n| <= 2: the factors alpha_b of the sources or the
  gauge independence of the kicks would be wrong.
- PG2 geodesic mean with `lapse_kdriver = 2` (d_t alpha = -2 alpha_ref alpha (Khat -
  <Khat>)): the mean lapse stays 1 within 1e-8, its rms perturbation is between 1e-8 and
  1e-5; R^NR deviations within 20 percent of the geodesic run in all three classes;
  constraint ratios within a factor 2 of the geodesic run. Refuted by a change of the
  lowest modes beyond a factor 2.
- PG3 homogeneous slow roll (`g3_homog.py`, 16^3, step 0.0491 as the 32^3 runs) under
  four lapse conditions; phi, Pi, K against the Friedmann solution at the proper time
  int <alpha> dt. (a) geodesic: within 1e-9 over 8 e-folds. (b) conformal time
  (`lapse_harmonic = 1/3`, alpha = a): the step in e-folds is H a dt; RK4 is unstable
  for a decay rate times step beyond 2.785 and chi decays at 2 H alpha, so the run
  fails where 2 H a dt = 2.785, a = 28, 3.3 e-folds (in general ln(0.885 N) e-folds
  for N cells at Courant 0.25: 5.4 at N = 256); the error of <Pi> exceeds 1e-4 before
  2.5 e-folds. (c) 1+log (`lapse_oplog = 2`): d alpha/dN = 6 on the background, alpha =
  1 + 6N within 1 percent to 3 e-folds; unstable where 2 H alpha dt = 2.785, alpha = 28,
  N = 4.6 +- 0.5. (d) 1+log with the relaxed lapse on the published processor
  executable of `core/gauge` (b4430da; pgen `scalar_field`, id = flrw; the slice of
  this package is not in that executable): `lapse_leak = 10` (T = 0.1): the lapse
  settles within a time of a few T at exp(-2 T Khat) = exp(6 H T), 1.82 for H = 1, and
  follows H afterwards within 1 percent; the background within 1e-6 over 8 e-folds
  (step in e-folds 0.09). Refuted if (b) or (c) run through 8 e-folds with errors below
  1e-4, if the settled lapse of (d) differs from exp(6HT) by more than 2 percent, or if
  the background of (d) is off by more than 1e-5.

**A truncation analysis** (`a1_twin.py`: the linear system of entry 1 per wave vector,
integrated with SciPy, against the dumps of the ladder N = 32, 64, 128 of the second
package, card run core-20261115-155404-24c88e3, s = +-1).
- PA1 The rms over the box of the odd part of H at t = 2.0 to 3.2 computed by the twin
  equals the measured one (6.57e-10, 1.42e-11, 2.53e-13 at t = 2.4, J2 entry 11) within
  25 percent at N = 32 and 64, and within a factor 2 at N = 128 (rounding floor
  4.3e-13); the same for |M|. Per mode at N = 32: the complex first-order coefficients
  of H of twin and dump agree within 30 percent of the rms coefficient for the modes of
  the three top shells.
- PA2 The per-mode deviation of R^NR from W R alpha of the twin equals the measured one
  (2.8e-3 at N = 32, 5.9e-5 at N = 64 for the largest) within 25 percent.
- PA3 With kap_a replaced by q_a^2 in the twin (evolution and constraints) the
  first-order parts of H and M vanish to the accuracy of the integration (below 1e-6 of
  the values of PA1); with the mode functions of the sources evolved with the lattice
  K2 instead of k^2 they change by less than 30 percent.
Refuted: PA1 by a disagreement beyond a factor 2 at N = 32 (the derivation of entry 1
would miss the main term); PA3 by a remaining first-order part with kap = q^2.

## 2026-11-19, entry 3: processor cores; outcomes of T0 and G3; one more prediction

**Cores.** `nrpic-run submit` refused the first run at 14:45Z: "8 cores asked, 16 busy in
live local runs of core, allotment 16 at a time (decision 0006)". The allotment is per
owner, and about ten core sessions run beside this one. The runs of this package are
therefore submitted by a small queue (`scratch/core/scalar3/queue/q1.sh`: retry every
20 s, one registered run per group of at most four cores), and everything that needs no
run is done meanwhile. Request to orch in the report.

**T0, run core-20261119-144905-cea3a49** (no figure: every difference is zero). P0a HOLDS:
`rng.mode_entity(n)` equals `rng.cell_entity(n + 2^20)` for the 548958 wave vectors of
nmax2 = 4096 and for the corners (-2^20, 2^20 - 1, 0), (2^20 - 1, -2^20, -1), (0, 0, 0);
2^20, -2^20 - 1 and a floating-point value are refused; the stream word of degree of
freedom 0 is 0x300010000. P0b HOLDS: `mode_alpha` with the new helpers equals Track E's
`philox_ref.mode_alpha` bit for bit for the 2084 modes of nmax2 = 100 in all eight
combinations of seed (1, 20261115), degree of freedom (0, 1) and epoch (0, 7).

**G3, run core-20261119-144906-69c60cc** (16^3, step 0.0491; figure
`fig_gauge_homog.png`, looked at: the lapse of the conformal-time and of the 1+log run
leave the frame within three e-folds and their step in e-folds reaches one; the relaxed
lapse sits at 1.8 and its step at 0.09; the error of <Pi> of the geodesic run is at
1e-13, that of the relaxed run flat at 6e-8).
- (a) geodesic HOLDS: phi, Pi, K within 4.2e-13, 8.0e-13, 3.0e-12 of the Friedmann
  solution over 8.04 e-folds; e-folds from <chi> within 5.5e-6 (as J2 entry 6).
- (b) conformal time: the run ends at its limit t = 0.999 after 21 steps without a
  non-finite number, so "fails where 2 H a dt = 2.785" was not reached (2.47 in the
  last step). The result is useless all the same: the lapse is 75.6 where <chi> says
  3.43 e-folds (a = 30.8), the e-folds are off by 1.20 against the Friedmann solution at
  the proper time of the mean lapse, phi and K by 3.4e-3. My prediction "error of <Pi>
  above 1e-4 before 2.5 e-folds" FAILED: <Pi> is off by 8.6e-5 at the end only; the slow
  variable Pi hardly feels the step, the scale factor does. In the first half of the
  run (to 0.7 e-folds) phi and K agree to 6.3e-6.
- (c) 1+log: alpha = 1 + 6N within 0.64 percent up to three e-folds (HOLDS); the run
  turns non-finite after 12 steps, at 3.06 e-folds by <chi> with alpha = 32.4 and a
  step of 1.5 e-folds. "Unstable at N = 4.6 +- 0.5" FAILED in the place: the estimate
  took alpha = 1 + 6N up to the stability limit, but from three e-folds on the step is
  an e-fold and the lapse overshoots. The limit 2 H alpha dt = 2.785 (alpha = 28) is
  where it broke.
- (d) relaxed 1+log (`lapse_leak = 10`, executable of `core/gauge`): the lapse reaches
  1.810 and follows exp(6 H T) of the Friedmann H within 1.2e-3 from one unit of proper
  time on (HOLDS; predicted 1 percent); 7.87 e-folds in 96 steps. Against the Friedmann
  solution at the proper time of the mean lapse: Pi 6.7e-8, phi 1.5e-5, K 1.5e-5,
  e-folds 1.2e-3: "within 1e-6" FAILED as measured, and my bound of refutation (1e-5)
  is passed by phi and K. [JUDGEMENT, to be tested by the repeat below] The comparison
  is at fault, not the run: the proper time is a trapezoid sum of the recorded mean
  lapse, and the lapse relaxes within two steps at the start (T = 0.1, step 0.049), so
  the sum is wrong by about 1e-3, which is the e-fold error found (H = 1) and gives
  Pi x 1e-3/phi = 1e-5 in phi.

G3r (repeat of the analysis on the same files, predicted before it runs; `g3_homog.py
--analyse-only` with a comparison that needs no time: <K>, <Pi> and the e-folds as
functions of <phi> against the Friedmann solution). For (d): K within 1e-7 and Pi
within 1e-6 at equal phi; e-folds within 3e-4 (fourth-order error of chi at a step of
0.09 e-folds: (0.18)^5/120 per step over 96 steps, halved for the e-folds: 8e-5). For
(a): K 1e-11, e-folds 5.5e-6. For (b) and (c) the first half of the run within 1e-4 in
K. Refuted for (d) by an error of K above 1e-6 at equal phi: then the relaxed lapse
would have changed the solution and not only the slicing.

**A, code check before the registered run** (unregistered, numbers not used below: the
twin `sf_lattice.Twin` on the 32^3 rung of the ladder, `scratch/core/scalar3/dev/
dev_twin.py`). It showed, after the predictions PA1 to PA3 were written: twin and dumps
agree in the rms of the odd parts of H and |M| to a part in a thousand from t = 2.0 on;
with every second derivative as the first difference applied twice the first-order
constraints fall to 1e-15; with the lattice K2 in the mode equation they change by 0.3
percent and the deviation of R^NR from W R alpha falls from 2.8e-3 to 1.2e-6. The
registered run A repeats this at three resolutions and adds the scan.

Added to test A before its registered run (none of these numbers has been computed):
- PA4 R^NR of the dumps against the twin itself, mode by mode (the twin carries the
  lattice dispersion that the reference W R alpha does not): N = 32, single run of T8:
  within 3e-5 for all modes with W > 1/2 at every dump (what is left: the second-order
  part, 1.2e-6 relative for the lowest modes at s = 1, J2 entry 14, and the time
  integration of the code, fourth order at H dt = 0.049). N = 64, part odd in s of the
  runs of T12: within 3e-6. Refuted by a difference above 3e-4 at N = 32: the twin
  would then not describe the mesh at first order.
- PA5 scan at fixed modes (nmax2 = 64; N = 32, 40, 48, 64, 80, 96, 128): the largest
  ratio in time of the first-order part to the measured second-order part (even part
  of the 64^3 runs of T12, minus the s = 0 field for H) falls below 1 between 8 and 10
  cells per shortest wavelength for |M| and below 0.1 between 10 and 14 cells (from
  the measured 40, 0.85, 0.016 at 4, 8, 16 cells, J2 entry 11, and mu ~ (k dx)^6 k^2);
  for H the crossings lie within one cell of those of |M|.

## 2026-11-19, entry 4: the card job of test U, predicted before it is submitted

One Slurm job (`inputs/card_usr.list`, executable `.work/exe/athena_gpu_cea3a49`, about
0.35 card-hours of the one allowed; the 256^3 production set-up is left to Track E, whose
G2 plan has it, because the queue holds eight jobs of core and four of the tracks and
the verification needs the ladder, not the size). Inflection case to t = 10.5, Courant
0.25, geodesic slicing, dumps with the metric and the constraint fields:
  L64, L128   nmax2 = 64 at N = 64, 128 (k_max dx = pi/4, pi/8): s = 1, +-0.1, 0
  K64         nmax2 = 256 at N = 64 (pi/2): s = +-1, +-0.1
  K128        nmax2 = 1024 at N = 128 (pi/2; 68532 modes entering until 3.47 e-folds,
              i.e. into the ultra-slow-roll phase): s = +-1, +-0.01, 0
Mode files: `problems/scalar/usr_stochastic_modes.txt` (64), `inputs/usr_modes_n256.txt`
(from the Bunch-Davies time N0), `inputs/usr_modes_n1024.txt` (`make_case.py --kstart
100`: another phase per shell than a start at N0, J2 entry 9).

Predictions (the processor runs of U have not run; none of this has been seen):
- PC1 background: the relative error of <Pi> against the reference scales with the
  fourth power of the step: at N = 64 one sixteenth (+- 30 percent) of the 32^3 value of
  the processor run z0 at equal e-folds, at N = 128 one 256th, so A1 (1e-4) holds
  throughout at N >= 64.
- PC2 lattice error of the grown modes (part odd in s of R^NR against W R alpha after 6
  e-folds, shell |n| = 8): N = 32, 64, 128 as the error of the lattice k^2, i.e. as
  1.8e-2, 3.8e-4, 6e-6 within a factor 2.5 (ratios 47 and 60 between the resolutions,
  within a factor 2). K64 and K128 (k_max dx = pi/2 again): their top shell as N = 32,
  0.5 to 2.5e-2; their shell |n| = 8 as L64 and L128.
- PC3 non-linearity at k_max/dk = 32 (K128): Delta_R of the reference at the top shell
  reaches order one at the end, so the run s = 1 is not a small perturbation late: its
  single-run deviation from the linear reference exceeds 0.1 for |n| <= 4 after 7
  e-folds, the even part of R^NR is comparable to the odd part there, and the rms of
  R^NR over the box stays within a factor 3 of the linear one (P1:536: "excellent
  agreement" of the spectra with Delta up to 0.1 to 1). The pair s = +-0.01 follows the
  linear reference within 2e-3 for |n| <= 8.
- PC4 constraints of K128 at s = 1: <|H|/[H]> at most 1e-9 over the run, reached before
  3 e-folds; from 4 e-folds on below 1e-10. <|M|/[M]> between 1e-5 and 0.3 from 4
  e-folds on (P1:541: about 1e-2 late at 256^3). The first-order parts at equal k_max dx
  = pi/2 (K64, K128, and the 32^3 run) agree within a factor 3 in rms at their maxima
  when divided by the rms of R^NR of the entering shells.
- PC5 cost: 0.14 to 0.17 s per step at 128^3 with 68532 modes (J2 entry 11: 1.484e7
  zone-cycles per second), 856 steps.
Refuted: PC1 by an error that does not fall with the step (a defect of the background
of the sources in ultra slow roll); PC2 by a top-shell error at k dx = pi/2 below 3e-3 or
above 0.1; PC3 if the pair s = +-0.01 misses 2e-2 for |n| <= 8 (the sources or the slice
would be wrong when modes enter during ultra slow roll, which the 32^3 runs cannot
test); PC4 by a Hamiltonian ratio above 1e-7.

## 2026-11-19, entry 5: a lapse for long runs at high resolution (G4), predicted

[JUDGEMENT] What a long inflationary run needs from the lapse: (i) a homogeneous
background part, so that the sources and their window keep a meaning (they carry
<alpha> and run in the proper time of the mean); (ii) a step in e-folds, H <alpha> dt,
that stays at the accuracy limit of the time integration (0.05: the 32^3 runs) instead
of growing or of being much smaller; (iii) a response to local contraction if large
perturbations collapse. Geodesic slicing meets (i), fails (iii), and wastes steps at
high resolution: the step is set by the cell, H dt = 2 pi C/N = 0.0061 at N = 256, eight
times below the accuracy limit, although from ln 8 = 2.1 e-folds on the coordinate
light speed alpha/a would allow a lapse of 8. Conformal time keeps the Courant number
of light and fails (ii) after ln(0.05 N/(2 pi C)) e-folds (G3: three e-folds at this
step). The two can be joined with the relaxation term of `core/gauge`: `lapse_harmonic =
1/3` (alpha = a) with `lapse_leak = 1/T`, `lapse_leak_alpha = alpha_0`: the term is off
below alpha_0, and above it holds the lapse at the root of ln(alpha/alpha_0) = H T
alpha (which exists for H T alpha_0 < 1/e), close to alpha_0. With alpha_0 = 0.05 N/(2
pi C) the run takes (1 - 1/alpha_0) N/(2 pi C) steps for the first ln alpha_0 e-folds
and 20 steps per e-fold afterwards.

G4 (homogeneous, on the published processor executable of `core/gauge`; `g3_homog.py
--only capconf`: 16^3, step 0.006136 as a 256^3 run at Courant 0.25, alpha_0 = 8, T =
0.02). Predictions: the lapse equals a within 1e-4 up to 1.5 e-folds; from 4 e-folds on
it sits at the root, 9.71 for H = 1, within 1 percent; 8 e-folds are reached in 245 +-
15 steps where geodesic slicing at the same step needs 1340; at equal field value K
within 1e-8 and the e-folds within 3e-5 of the Friedmann solution. Refuted by a lapse
that keeps growing (no root reached), by more than 300 steps, or by an error of K above
1e-6.

## 2026-11-19, entry 6: outcomes of G3r and G4; a smoke test that already refutes two predictions of U; the twin with the time integration of the code

**G3r, run core-20261119-150816-a8f9558** (analysis of the files of -144906-69c60cc at
equal field value; figure as in entry 3). HOLDS for (d): with the relaxed 1+log lapse <K>
equals the Friedmann K at equal <phi> within 3.3e-11, <Pi> within 1.1e-11, the e-folds
within 5.2e-5 (predicted 1e-7, 1e-6, 3e-4): the relaxed lapse changes the slicing, not the
solution, and the 1.5e-5 of entry 3 was the trapezoid sum of the proper time, as
suspected there. (a) geodesic: 3.3e-12 (K), 5.5e-6 (e-folds). (b), (c): at equal field
value the e-folds of the first half of the run are off by 2.1e-5 (conformal time) and
1.1e-3 (1+log); the whole run by 0.93 and 2.2 e-folds, K by 7.4e-5 and 2.9e-2. My "K
within 1e-4 in the first half" was not evaluated (the script records the e-folds of the
first half only).

**G4, run core-20261119-150838-0251a5e** (conformal-time lapse capped at 8 by the
relaxation term, step of a 256^3 run; figure `fig_gauge_homog.png` of that run, looked at:
the lapse rises as a straight line in the logarithm to 8 at 2.1 e-folds and stays at
9.5; the step in e-folds rises from 0.006 to 0.056 and stays; the last point is the step
cut at the time limit). HOLDS: lapse equal to a within 7.8e-8 up to 1.5 e-folds; from 4
e-folds on within 6.1e-4 of the root of ln(alpha/8) = 0.02 H alpha (9.52 at the end,
where H = 0.955); 7.64 e-folds in the 245 steps of the run, i.e. 8 e-folds in 252 at the
final 0.0558 e-folds per step (predicted 245 +- 15; my time limit 1.5 was 0.04 short of 8
e-folds), against 1341 steps of geodesic slicing at the same step: 5.3 times fewer. At
equal field value K within 6.8e-12 and the e-folds within 8.0e-6 of the Friedmann
solution (predicted 1e-8, 3e-5).

**Smoke test of the drivers of U** (unregistered: `u1_usr.py`, `u2_usr_analysis.py`,
`a2_twin_usr.py` at 16^3, nmax2 = 16, to t = 1, `scratch/core/scalar3/smoke_u*`; run to
find script errors while the registered runs waited for cores). It showed numbers that
bear on predictions of entry 2, before the registered runs: the s = 0 run has <|H|/[H]> =
3.5e-7 at the step 0.098 and 1.9e-8 at the step 0.049 (ratio 18): the step of the 32^3
runs. So PU3 ("between 3e-12 and 2e-10") is already known to FAIL by two orders, and
with it the record maximum of PU4, which this uniform residual will dominate. Cause
[JUDGEMENT; the twin below computes it]: I scaled the residual of the quadratic case by
eps1 only; it grows with the fourth power of the rate at which the background changes,
eps2/2 = 0.2 here against 0.01 there.

**The twin with the time integration of the code** (`sf_lattice.CodeTwin`, written after
the continuous twin had been checked: the stages of the driver's rk4 at the steps of the
run; the lockstep data; the homogeneous part of the mesh fields with the code's own
equations for phi, Pi, chi, Khat, Theta, so that its Hamiltonian residual H0 is part of
the solution; the perturbations about that homogeneous part, with delta chi as the
variable, as in the code). Code checks before any registered run (unregistered, numbers
not used below): on the 32^3 rung of the ladder of the quadratic case the rms of the
odd parts of H and |M| of twin and dumps agree to the four digits printed at all eight
dumps, also at the early ones, where the continuous twin had 1.4 percent of the
measured value; the twin's H0 is 3.03e-11 at t = 0.44 and 3.24e-11 to 3.26e-11 after
(J2 entry 7 measured exactly that); with c = delta chi/chi_0 as the variable instead the
early odd parts were 25 percent off, which is how the choice of variable was found. On
the smoke runs of the inflection case the part of R^NR odd in s equals the twin to 5e-10
and 3e-9. An evaluation at the 32^3 set-up of U (`dev_codetwin_usr.py`) gives what the
registered runs should show if the twin describes the code:

PU6 (from the twin; replaces the magnitudes of PU3, PU4, PU5c).
- Run z0: <|H|/[H]> = |H0|/[H] = 1.9e-8, 1.6e-8, 1.1e-8, 7.9e-8, 1.0e-7, 3.3e-8, 5.1e-9,
  5.3e-10 at the dumps near t = 0.5, 1.0, ..., 4.0 (within 2 percent), below 1e-12 from
  5.5 e-folds on. The same in the runs with s = 1 and 0.1 (the first-order part, rms
  7e-10 of 12 at most, is 3 orders below).
- Box means against the reference (run z0): Pi within 3e-6 to 3 e-folds, 1.6e-5 at 4.8,
  9.6e-5 at 6.3, 4.1e-4 from 8 e-folds on; phi within 3.5e-7; K within 9e-8.
- Pair s = +-0.1: the odd parts of H and |M| equal the twin's (rms 7.1e-11 and 9.6e-11
  at t = 2.5, i.e. 0.1 times 7.06e-10 and 9.60e-10) within 1e-3 while they exceed 1e-12;
  the part of R^NR odd in s equals the twin within 1e-5 for every mode with W > 1/2 at
  every dump; against the continuum reference W R alpha it deviates by 6.1e-3 for the
  top shell, 2.7e-4 for |n| <= 4 and 3.2e-5 for |n| <= 2 from 5 e-folds on (the lattice
  and the step; in place of the 0.5 to 2.5e-2, 2e-3, 3e-4 of PU5c).
Refuted by a disagreement of twin and run beyond these bounds: then the code does
something at first order that the equations of entry 1 do not contain.

PA6 (added to test A; the 32^3 rung has been seen, entries above; 64 and 128 not). Twin
with the time integration against the ladder: rms of the odd parts of H and |M| within
1e-3 at N = 32 at all dumps; at N = 64 within 1e-2 for t <= 1.2, where the measured odd
part sits at 3.6e-13 to 5e-13 and J2 took it for rounding (if it is the time error, the
twin has it), and within 1e-3 after; at N = 128 within a factor 1.5 everywhere (rounding
floor 4e-13). The twin's H0 at N = 64 equals the measured 1.75e-12 to 1.91e-12 of the s =
0 run within 1 percent. R^NR of the 32^3 run of T8 against the twin: within 3e-6 for all
modes (the second-order part of a single run at s = 1 is 1.2e-6, J2 entry 14); odd part
at 64^3: within 1e-7.

## 2026-11-19, entry 7: resumed session (15:40Z); outcomes of R a and R c

The session that wrote entries 0 to 6 stopped at about 15:38Z. Found at 15:40Z: eleven
registered runs had ended (exit status in `.nrpic/result.json`) but their manifests still
said "running" (no wrapper left to close them); closed with `nrpic-run finish` (commits
2850abb and the ten before it). Still live then: A (-151758-51d9a71), A2 (-152243-1754ebc),
U z0c0125 (-152745-0ee5e58), U c0125 (-152757-a0dc5ef); card job 4651 (U card,
-150317-a1e8ee7) waiting in the queue behind 16 jobs. The ten hand-written manifests of
the sub-runs of R c were untracked; committed (59f5794).

**R a, run core-20261119-150818-615d921, part a** (t6_regress.py; no figure: every
difference is zero). PRa HOLDS for the ten scalar-field cases of wave 1: 120 files, 110
byte-identical, the other 10 restart files of ms, msnk, msr identical but for 32 of the 36
unset header bytes and, in two files of msr, the recorded restart path (as J2 entry 7).
**Part b FAILED as a run, not as a test**: the published executable of `core/scalar-2`
stopped at once, "Parameter 'dump_dcycle' in block 'scalar_field' on command line not
found" (`parameter_input.cpp` line 400: a command line may override only parameters that
the input file has). The driver now writes the cadence into the input (32b7ef4); part b
is rerun alone (queue q4).

**R c, run core-20261119-152209-ca85372** (`regress_relativistic.py`, release core-v0.3
against `athena_cpu_cea3a49`; sub-runs -152210 to -153611, manifests committed). PRa
HOLDS for the seven relativistic set-ups: geo 2, boris 2, dep 1, east 12, os 16, jeans 5,
binary 1 files, all byte-identical, none differing.

## 2026-11-19, entry 8: test G5, the capped conformal-time lapse with the stochastic sources, predicted

G4 showed the capped conformal-time lapse on the homogeneous background only, and on the
executable of `core/gauge`, which lacks the initial slice and the sources of this branch.
What a long inflationary run needs from `core/gauge` is therefore not yet shown: that the
relaxation term and the sources work together. Test G5 builds both into one processor
executable, outside the branch: `scratch/core/tmp/gmerge/` holds `git archive` of this
branch at b8a3c1a plus `git diff f51539c 96b215c -- athenak/src` of `core/gauge` (295
lines, four files under `z4c/`, applied without conflict: this branch touches nothing
under `z4c/`), built with `scripts/build_cpu.sh` and `ATHENA_SRC` pointing there
(`SOURCE.txt`, `gauge.patch` beside it). It is a test executable, not a published one.

G5 (`g1_gauge.py --only geoc` on the executable of this branch, `--only cap` on the
merged one; quadratic case, 32^3, nmax2 = 64, seed 20261115, s = 1, Courant 1/32, i.e.
dt = 0.006136, the step of a 256^3 run at Courant 0.25):
  geoc  geodesic slicing to t = 3.3 (538 steps, 3.27 e-folds), dumps every 0.3
  cap   lapse_harmonic = 1/3, lapse_leak = 50, lapse_leak_alpha = 8 (as G4), to t = 1.0,
        dumps every 0.025
Predictions (none of these runs has been made):
- PG5a lapse of cap: <alpha> equals a within 1e-4 up to 1.5 e-folds (G4, homogeneous:
  7.8e-8; the perturbations change the mean at second order only); from 2.6 e-folds on
  within 1e-3 of the root of ln(alpha/8) = 0.02 H alpha (G4: 6.1e-4). End near 3.15
  e-folds (alpha = a up to t = 0.88, then dN/dt = H alpha = 9.4) after 163 steps,
  against 538 steps of geoc for 3.27 e-folds (3.3 times fewer; G4's 5.3 was over 8
  e-folds).
- PG5b R^NR per mode against W R alpha of the lockstep record (the comparison of PG1):
  geoc is at most the deviation of the run geo of G1 (Courant 0.25) in every class: the
  time error falls by 8^4 and the spatial (lattice k^2) part is the same, so the top
  classes (all modes with W > 1/2) agree with geo within 30 percent and |n| <= 2 is
  smaller. cap: within a factor 3 of geo in every class after the cap (its proper-time
  step, 0.058 at alpha = 9.5, is that of geo, 0.049), and of geoc before. Refuted by a
  deviation of cap above 3 times that of geo for |n| <= 2: then the kicks are not
  independent of the slicing at alpha of order 10, or the sources do not follow the
  proper time of a lapse that changes by a factor 8.
- PG5c constraints: geoc has no uniform part above 1e-13 (geo: 3e-11 from the time
  integration, J2 entry 7; 8^4 times less), so its record <|H|/[H]> is the first-order
  spatial part, within 30 percent of the odd part of geo at equal e-folds. cap: <|H|/[H]>
  and <|M|/[M]> within a factor 3 of geoc at equal e-folds (the slicing changes the
  first-order metric perturbations on which the stencil defect acts, by order one at most).
  Refuted by a ratio above 10 or a growing trend of cap against geoc.

## 2026-11-19, entry 9: option con_signed (Track E's request 3 of its USR package), test S predicted

Track E's USR package (`tracks/E-stoch-inf/usr/README.md` on `track/E-stoch-inf` at
51d8046, request 3 to core) found what PU6 of entry 6 says: at 32^3 the record of
<|H|/[H]> is the uniform residual of the background (1.1e-7 of [H] at Courant 0.25) and
hides everything else; it asks for signed box means of H and M_i in the record. Added
(source of this entry's commit): `<scalar_field> con_signed = true` appends seven
columns to `<basename>.sf.con.hst`: [21] <H>, [22-24] <M_i>, and with H' = H - <H> (the
part that is not uniform) [25] <|H'|/[H]>, [26] max |H'|/[H], [27] rms H'. A new function
`ScalarField::ConstraintSignedMeans` (two reductions, the second about the mean of the
first); `WriteConstraintHistory` calls it only with the option and otherwise writes the
same bytes (the line end of the header and of the record is now a separate fprintf).
Reader: `python/nrpic/scalar_field.py` read_con_history (names H_mean, Mx_mean, My_mean,
Mz_mean, Hp_ratio, Hp_ratio_max, Hp_rms). Example: `problems/scalar/sr_stochastic_gauge.
athinput` (the regression R b turns it off on the command line for that example, so that
the record is comparable with the executable of `core/scalar-2`).

Test S (`s1_signed.py`, inflection case 32^3, nmax2 = 64, to t = 3.0, dumps every 0.5
with H, M_i and [H]): runs sig (s = 1, con_signed), plain (s = 1, without), zsig (s = 0,
con_signed). Predictions:
- PSa every file of sig and plain byte-identical except the record; the record has the
  same first 20 columns, byte for byte, on every line, and its header extends the old one.
- PSb at the dump cycles: [21] equals the mean of H of the dump within 1e-13 relative
  (another order of summation); |[22-24] - mean M_i| below 1e-13 of rms |M|; [27] and [25]
  equal rms(H - mean H) and mean(|H - mean H|/[H]) of the dump within 1e-10 relative (H'
  is a difference of nearly equal numbers, 1e-3 to 1e-2 of H, so the order of summation
  of the mean enters at 1e-13 to 1e-12 of H').
- PSc in zsig (homogeneous) <|H'|/[H]> is rounding: below 1e-15, while <|H|/[H]> =
  |<H>|/[H] is the 1.9e-8 to 1e-7 of PU6. In sig <|H'|/[H]> carries the first-order part:
  between 1e-10 and 3e-9 from 0.5 to 3 e-folds (the twin of entry 6: rms 7e-10 of [H] at
  most for s = 1), two orders below <|H|/[H]>; <M_i> below 1e-3 of rms |M| (a mean of a
  periodic first-order field is second order).
Refuted by any differing byte in PSa, by a mismatch beyond the bounds in PSb, or by
<|H'|/[H]> of sig within a factor 10 of <|H|/[H]> (then H is not dominated by its uniform
part, against PU6).

## 2026-11-19, entry 10: regression R2 of the final source, predicted

R2 repeats R (entry 2, PRa and PRb) with the executable of 5cc2821 (`athena_cpu_5cc2821`,
the source with `con_signed`): the ten wave-1 scalar cases (120 files) byte-identical to
release core-v0.3 but for the masked restart bytes; the three stochastic examples (sr,
usr, srg, with con_signed off for srg) byte-identical to the published executable of
`core/scalar-2`, also after the restart; the seven relativistic set-ups byte-identical.
Refuted by any differing data byte.

## 2026-11-19, entry 11: card check C2 of the final card executable, predicted

The card job of test U (4651) runs `athena_gpu_cea3a49`, the source before `con_signed`.
The card executable to be published is `athena_gpu_5cc2821` (built 15:58Z, sha256
8dc2ae83...). C2 (`inputs/card_c2.list`, one Slurm job, 0.1 card-hours requested; then
`c2_compare.py`, the same input on `athena_cpu_5cc2821`): the gauge example (quadratic
case, 32^3, lapse_harmonic = 0.05, con_signed = true) for 20 steps. Predictions (from
the card check of J2: slice bit-identical, fields within 3.3e-14 after 20 steps, constraint
fields within 3.4e-13): the dump at t = 0 bit-identical; the dumps at 0.4 and 0.8 within
1e-12 of the largest value of each variable (H, M_i within 1e-11); the record columns
within 1e-10 relative, the H' columns of con_signed within 1e-8 relative (H' is 1e-3 to
1e-2 of H in this case, where the uniform part dominates, so the field difference is
amplified by that ratio). Refuted by a larger difference or by a missing column.

## 2026-11-19, entry 12: outcomes of A and A2 (the linear twin against the ladder), of G1 and G2

**A, run core-20261119-151758-51d9a71, and A2, run core-20261119-152243-1754ebc** (A2 is A
plus part E, the twin with the time integration of the code; both read the same dumps,
and every number below is from the summary of A2; figure `fig_twin.png` of A2, looked
at: the code twin passes through every measured point of N = 32 in both upper panels and
through those of N = 64 from 1.6 on; the N = 128 points lie above the twin before t = 2;
the scan falls as a straight line of slope -6 and crosses 1 near 12.5 cells).
- PA1 HOLDS: continuous twin over measured rms of the odd part, t = 2.0 to 3.2: H 0.997
  to 0.9998 (N = 32), 0.991 to 0.9998 (64), 0.64, 0.94, 0.95, 0.92 (128, within the
  factor 2); |M| 1.01 to 0.9999, 1.03 to 0.9999, 0.39 to 0.96 (128 at t = 2.0: 0.39, outside
  a factor 2; the other three dumps inside). Per-mode coefficients of H at N = 32: largest
  difference 0.030, 0.0066, 0.0034, 0.0033 of the rms coefficient from t = 2.0 on (bound
  0.3). Before t = 1.6 the continuous twin misses (0.014 to 0.80 of the measured rms): the
  time-integration part, which entry 6 found and the code twin contains.
- PA2 HOLDS: largest |R^NR/(W R alpha) - 1| at the last dump, twin against measured:
  2.83e-3 against 3.06e-3 (N = 32, 8 percent), 5.88e-5 against 7.54e-5 (N = 64 odd part,
  22 percent; bound 25).
- PA3: with every second derivative the first difference applied twice (d1d1) the
  first-order parts fall from 3.9e-10, 6.6e-10, 3.4e-10, 1.6e-10 (H, t = 2.0 to 3.2) to
  4.4e-15 to 8.5e-16, by 1.1e-5 to 5.2e-6, and |M| by 6.9e-6 to 5.9e-7. "Below 1e-6"
  FAILED for H as stated (the remainder, 1e-15 absolute, is at the relative tolerance
  1e-10 of the integration times the terms of order 1e-5; [JUDGEMENT], not tested with a
  smaller tolerance). The same variant makes the lattice dispersion of R^NR worse: largest
  deviation from W R alpha 2.0e-2 at t = 3.2 against 2.8e-3 (the first difference applied
  twice is 12.8 percent low at k dx = pi/2, the second difference 1.8 percent;
  `symbols_sixth_order`). Mode functions with the lattice K2: H and |M| change by 0.0 to
  0.3 percent (HOLDS: below 30 percent); the twin's R^NR then follows its reference to
  1.2e-6. BSSN instead of Z4c: |M| 1.6 to 5.3 times larger, H 0.65 to 1.15.
- PA4 FAILED as stated: dumps against the continuous twin up to 3.06e-4 (N = 32; bound of
  refutation 3e-4) and 1.95e-5 (N = 64 odd part; predicted 3e-6). Against the code twin
  (PA6) they agree to 3.6e-6 and 2.6e-8: the 3e-4 is the time integration of the run,
  which the continuous twin lacks.
- PA6: rms odd parts at N = 32, code twin over measured: H 0.99996 to 1.00000, |M| 0.9998
  to 1.0000 at all eight dumps (HOLDS, bound 1e-3). N = 64: 0.78, 0.91, 0.98 (H) and 0.45,
  0.64, 0.86 (|M|) for t <= 1.2, FAILED (bound 1e-2); from 1.6 on H 0.9995 to 1.0000 and
  |M| 0.9946 to 1.0000 (FAILED at 1.6 for |M| by 5.4e-3, then 1.0000). N = 128: 0.0135 to
  0.117 before t = 1.6 and 0.66, 0.35 (H, |M|) at 2.0, FAILED; 0.92 to 0.95 from 2.4 on.
  The measured early odd parts at 64 and 128 (5e-13, 1.7e-12) are above the twin
  (3.8e-13, 2.3e-14): something the twin does not contain, [JUDGEMENT] the rounding of the
  card runs of the ladder, not tested. H0 of the twin against the s = 0 run at N = 64:
  ratio 0.987 to 1.0075 (bound 1 percent; FAILED by 0.3 percent at t = 1.2). R^NR against
  the code twin: N = 32 single run 6.2e-7 to 3.6e-6 (bound 3e-6: FAILED from t = 2.85 by
  20 percent); N = 64 odd part 2.2e-10 to 2.6e-8 (HOLDS, bound 1e-7).
- PA5 FAILED: largest ratio in time of the first-order part (twin) to the measured
  second-order part (even part of the 64^3 runs of T12) at 4, 5, 6, 8, 10, 12, 16 cells per
  shortest wavelength: H 692, 213, 77, 14.9, 4.04, 1.38, 0.25; |M| 621, 191, 69, 13.3, 3.6,
  1.23, 0.22. The crossing of 1 lies between 12 and 16 cells, not between 8 and 10, and
  0.1 is not reached in the scan. Cause of the miss: the prediction scaled the record
  ratios of J2 entry 11, but the largest ratio here falls at t = 2.4, where the
  second-order part has dropped by a factor 9 (8.2e-12 to 9.5e-13 for H between t = 2.0
  and 2.4) while the first-order part peaks. The summary keys
  `cells_for_*_first_*_second` of A and A2 are WRONG (4.0 and null): a driver error
  (interpolation on a decreasing abscissa), corrected in `a1_twin.scan_crossings`; the
  rows are right. Computed by hand from the rows before the registered recomputation
  below: crossing of 1 at 12.7 (H) and 12.4 (|M|) cells, of 0.1 at 18.7 and 18.3 cells by
  extrapolation with the slope of the last two points (-5.94, -5.95: sixth order).

Item (3) of the package, settled [VERIFIED by A2 for the slow-roll case]: the first-order
part is the defect mu of the discrete contracted Bianchi identity of the spacetime
solver's stencils, acting on every mode with large k dx; it does not depend on how a
shell enters (mode functions with the lattice K2: 0.3 percent). The only change that
removes it (second derivatives as the first difference applied twice) is a change of the
Z4c stencils, not small, and it makes the dispersion of R^NR seven times worse. So no
source change; the criterion fixes the resolution: the first-order part stays below the
second-order part (Track E's strict A4) only with at least 12.7 cells per shortest
wavelength of the sources, i.e. nmax2 <= (N/12.7)^2 (k_max <= 20 dk at 256^3, against
P1's 64 dk); below a tenth with 19 cells. In P1's set-up (4 cells) it exceeds the
second-order part by 700 at its peak, as Track E measured on its ladder (385 to 870).
A3 (registered recomputation of the crossings from the rows of A2, `a3_scan.py`,
prediction: the numbers of the previous paragraph within 0.1 cell).

**G1/G2 analysis, run core-20261119-160004-63c808c** (runs geo -152244-bc4976d, harm
-152522-845c524, kdrv -152657-ea8a240; figure `fig_gauge.png`, looked at: geodesic and
driver curves lie on each other in all panels but the solid |n| <= 2 line of the driver,
which rises after two e-folds; the harmonic lapse rises linearly in ln alpha to 1.62).
- PG1 (lapse_harmonic = 0.05): box means against the lockstep background phi 6.6e-13, Pi
  1.6e-11, K 2.1e-11 (bound 1e-8: HOLDS); mean lapse against 1/(1 - 0.15 int H dt)
  3.4e-7 (bound 1e-6: HOLDS; 1.622 at the end); R^NR within the bounds of T8: 1.06e-4
  (|n| <= 2), 1.65e-4 (|n| <= 4), 2.4e-3 (all) (HOLDS); "within a factor 3 of geo in all
  three classes" FAILED for |n| <= 2: 3.72 times geo (1.06e-4 against 2.8e-5) at the
  first dump (0.35 e-folds, nine modes in against three in geo at its 0.34); from 0.67
  e-folds on 0.55 to 1.6 times geo, at the end 1.11, 0.96, 0.80. Not explained.
- PG2 (lapse_kdriver = 2): mean lapse 1 within 6.5e-12 (HOLDS), rms of its perturbation
  up to 2.97e-6 (HOLDS, 1e-8 to 1e-5); largest R^NR deviations 1.004, 1.008, 1.000 times
  geo (HOLDS, 20 percent); record ratios 0.97 (H) and 1.86 (|M|) times geo (HOLDS, factor
  2). But the deviation of |n| <= 2 grows after two e-folds to 1.49e-5 at the end, 4.05
  times geo (3.67e-6): by the bound "a change of the lowest modes beyond a factor 2" this
  part of PG2 is REFUTED at the end of the run. [JUDGEMENT, untested] the lapse
  perturbation grows linearly (rms 3e-6 at the end) and its product with R is a
  second-order part of R^NR of that size; a pair s = +-1 under the driver would decide.

## 2026-11-19, entry 13: outcomes of A3 (resolution) and of the twin on the inflection case

**A3, run core-20261119-161111-9d05d14** (figure `fig_scan.png`, looked at: both ratios
fall on a straight line of slope -6 through the scan and cross 1 between 12 and 16
cells; in time every resolution peaks at t = 2.4). HOLDS: crossing of 1 at 12.67 (H) and
12.42 (|M|) cells per shortest wavelength, of 0.1 at 18.67 and 18.30 (extrapolated,
slopes -5.93, -5.94); the code twin gives the same largest ratios within 1.1 percent.
Largest deviation of R^NR from W R alpha at the last dump: 2.8e-3, 8.5e-4, 3.1e-4,
5.9e-5, 1.6e-5, 5.4e-6, 9.9e-7 at 4, 5, 6, 8, 10, 12, 16 cells.

**A-usr, run core-20261119-160409-50a58d9** (twin of the inflection case against the
pair p01 -151036-d3d1f78, m01 -151755-d455a15; figure `fig_twin_usr.png`, looked at: the
odd parts of H and |M| of the runs lie on the code twin from 0.5 to 7 e-folds and on a
floor of 2.5e-14 per unit s after; the per-mode deviation from the code twin stays below
3e-7 while that from the continuous twin is 1e-5 to 5e-4).
- PU6, pair part HOLDS: odd parts of H and |M| against the code twin, where the measured
  value exceeds 1e-12: largest |ratio - 1| 1.9e-4 (H, eight dumps 0.54 to 3.90 e-folds)
  and 9.8e-6 (|M|, eight dumps 1.5 to 4.8 e-folds) (bound 1e-3); at 2.45 e-folds 7.06e-11
  and 9.60e-11 (predicted 7.1e-11, 9.6e-11). The part of R^NR odd in s against the code
  twin: at most 7.1e-7 for every mode with W > 1/2 at every dump (bound 1e-5).
- PU6, against the continuum reference from 5 e-folds on: top shell 5.9e-3 to 6.2e-3
  (predicted 6.1e-3, HOLDS); |n| <= 4: 1.8e-4 to 3.9e-4 (predicted 2.7e-4, within a factor
  1.5); |n| <= 2: 1.2e-5 to 3.9e-4, rising to 3.9e-4 from 6.75 e-folds on, FAILED
  (predicted 3.2e-5, factor 12). The code twin has the same 3.9e-4 (the runs agree with it
  to 7e-8 there) and the continuous twin 5.2e-6, so the late deviation of the lowest
  modes is the time integration. [JUDGEMENT, to be checked against the background part of
  the U analysis] it is the relative error of the background Pi, which reaches 4e-4 late
  at Courant 0.25 (PU6, and Track E's 4.1e-4) and enters R^NR through H/Pi_b; the lowest
  modes, whose R grows most through ultra slow roll, carry it fully.
- The late floor of the odd parts, 2.5e-15 (H) and 3.3e-15 (|M|) for s = 0.1, is above
  the twin from 7 e-folds on: [JUDGEMENT] rounding of a pair whose metric perturbations
  have stopped growing, not tested.

## 2026-11-19, entry 14: outcomes of test U on the processors (inflection case, 32^3); a correction to entry 13

**U analysis, run core-20261119-161122-a46833e** (runs p1 -152208-cc247d6, m1
-152235-7a1ce3f, p01 -151036-d3d1f78, m01 -151755-d455a15, z0 -152234-32898c7, ctl
-152743-c122f5a, z0c0125 -152745-0ee5e58, c0125 -152757-a0dc5ef; all 214 steps to t =
10.5, 10.06 e-folds; figures `fig_usr_background.png`, `fig_usr_constraints.png`,
`fig_usr_rnr.png`, looked at: eps1 of the box means lies on the reference through its fall
by ten orders; the error of <Pi> rises in two steps at the start and the end of ultra slow
roll and sits 16 times lower at Courant 0.125; |R_k| of the four shells falls, turns at
3.5 to 4.5 e-folds and grows by 300 to 24000 to a plateau after 7 e-folds, code and
reference on each other; <|H|/[H]> is the same line for s = 1, 0.1 and 0 (the uniform
residual); the odd part of H scales with s, the even part with s^2 until both pairs reach
a floor near 3 e-folds for s = 0.1; the control lies 4 orders above in |M|/[M]).
- PU1 background (z0): phi within 3.5e-7, K within 9.3e-8 of the reference (bound 1e-6:
  HOLDS); relative error of <Pi> 2.6e-6 at 3, 1.7e-5 at 5 (predicted 1e-5 to 1e-4: HOLDS),
  4.0e-4 at 8 and 4.1e-4 at the end (predicted 5e-5 to 1e-3: HOLDS; Track E's A1 at 1e-4
  is missed late at Courant 0.25, as predicted); Courant 0.25 against 0.125: 16.3 for phi
  and Pi, 16.6 for the e-folds (HOLDS, 16 +- 4 and 16 +- 2); e-folds from <chi> 7.0e-6 at
  the end (bound 3e-5: HOLDS). Box mean against the lockstep background: Pi 7.5e-6 late
  (FAILED, predicted 5e-6; phi 6.8e-9). The background passes ultra slow roll from 2.54 to
  6.51 e-folds (eps2 > 3), eps1 reaches 9.72e-13, eps2 at most 5.99996, H 0.9518 H* at the
  end (as entry 0).
- PU2 mode functions of the sources (lockstep record against SciPy), Courant 0.25: top
  shell at most 5.6e-4 (bound 3e-3: HOLDS); |n| <= 2 within 1e-4 only to 6 e-folds, then
  rising to 4.1e-4 (FAILED); ratio of Courant 0.25 to 0.125: 13.5 to 20.1 for |n| <= 2 and
  15.6 to 17.0 for the top shell (HOLDS with one value 0.1 above 20, at 5.8 e-folds, near
  the turn of |R|); not refuted (bound 3e-2, ratio above 8). |R| of the lowest shell grows
  300 times from 3.4 e-folds to the end, as the reference.
- PU3 as written in entry 2 FAILED (known since entry 6): <|H|/[H]> of z0 is 1.6e-8 to
  1.08e-7 from 0.5 to 3 e-folds, the uniform residual; it falls with the step 17.1 times
  (median, 0.5 to 3 e-folds; predicted 16 +- 4: HOLDS) and is below 1e-14 from 6 e-folds on
  (bound 1e-12 at 8: HOLDS). PU6 for z0: largest 1.08e-7 at 2.31 e-folds, 1.86e-8 and
  1.61e-8 at 0.5 and 1.0 e-folds (twin: 1.0e-7 near t = 2.5, 1.9e-8, 1.6e-8); the 2 percent
  at equal times was not evaluated (the analysis samples the record at fixed e-folds).
- PU4: record maxima of p1 <|H|/[H]> 1.08e-7 (FAILED as written, the uniform part; PU6
  replaced it); <|M|/[M]> 4.5e-3 up to 3 e-folds (FAILED, predicted below 3e-3), 1.7e-2 at
  most (3.43 e-folds); odd parts of the pairs scale by 10.000 (9.998 to 10.000 while the
  smaller exceeds 1e-13: HOLDS, 10.0 +- 0.5); even parts minus z0 by 90 to 103 up to 3
  e-folds (HOLDS, 100 +- 20), then 74 at 3.4 and down to 1 as the even part of s = 0.1
  reaches its floor (FAILED from 3.4 e-folds; [JUDGEMENT] rounding floor of the smaller
  pair, 3e-13 in H). In ultra slow roll H does not grow: 2.6e-10 at 4 e-folds (bound
  1e-10 from 4 on: FAILED at 4.0 by 2.6, then 1.5e-14 at 6); <|M|/[M]> 3.0e-3 to 1.6e-2
  from 4 e-folds on and 3.4e-3 at the end (HOLDS, 1e-5 to 0.3; P1:541 reports 1e-2 at
  256^3). Courant 0.125 (c0125): H 6.2e-9 at most (17 times less), |M|/[M] unchanged
  (1.7e-2): the momentum ratio is spatial.
- PU5 R^NR per mode against L^(-3/2) W R alpha of the lockstep record: (a) t = 0, modes with
  W > 1e-3: 2.1e-10 (HOLDS, 1e-8). (b) to 2.5 e-folds, run p1: 7.1e-5 (|n| <= 2), 1.7e-4
  (|n| <= 4), 1.3e-3 (all with W > 1/2) (HOLDS: 2e-3, 2e-2, 2e-2). (c) odd part of s =
  +-0.1 from 6 e-folds on: top shell 6.1e-3 (FAILED as written, 0.5 to 2.5e-2; inside the
  bounds of refutation 3e-3 to 0.1); |n| <= 4 2.7e-4 (HOLDS, 2e-3); |n| <= 2 3.2e-5 (HOLDS,
  3e-4). (d) REFUTED: the single run p1 agrees with the linear reference to 2.8e-4 to
  3.1e-4 for |n| <= 2 after 7 e-folds (refutation: below 1e-3), its even part is 2.9e-4
  to 3.1e-4, ten times that of s = 0.1 (second order, small); my estimate that delta phi at
  s = 1 is 7 percent of the distance from the stationary point of V' was wrong by orders.
  The rms of R^NR at s = 1 reaches 6.7e-2 (Track E's lattice value at 32^3, nmax2 64:
  0.066). (e) control: deviation 0.46 to 2.0 (FAILED at the first dump, 0.46 < 0.5; 0.74 to
  2.0 after).
- PU6 against the reference of PU5 (the lockstep record): top shell 6.1e-3, |n| <= 4
  2.7e-4, |n| <= 2 3.2e-5 from 5 e-folds on, exactly the predicted 6.1e-3, 2.7e-4, 3.2e-5:
  HOLDS.

Correction to entry 13: there I judged the |n| <= 2 part of PU6 FAILED (3.9e-4) from run
-160409-50a58d9, whose reference is the SciPy integration (no time error), not the
lockstep record of PU5 and PU6. Against the lockstep record it HOLDS (above). The 3.9e-4
against SciPy is the time error that the lockstep mode functions themselves carry (PU2:
4.1e-4 for |n| <= 2 late at Courant 0.25, 2.5e-5 at 0.125, ratio 16.4); the "relative
error of the background Pi" of entry 13 is of the same size (4.1e-4) but not shown to be
its cause. What a user should take: at Courant 0.25 on a 32^3 step the per-mode R of the
lowest shells carries 4e-4 of time error after ultra slow roll (A2 of Track E: 2e-2); at
256^3 the step is 8 times smaller and the error 4000 times smaller.

## 2026-11-20, entry 15: resumed after the usage limit (22:00Z); state found; what runs now, predicted

The session of entries 7 to 14 was cut off on 2026-11-19 after 17:07Z by the usage limit
of the account. Found on 2026-11-20 at 22:00Z (main merged at df589aad: decisions 0018 and
0019; `git diff 5cc2821 HEAD -- athenak/ python/ problems/` is empty, so the executables
built on 2026-11-19, `.work/exe/athena_{cpu,gpu}_5cc2821`, are those of the source of
HEAD):
- Every registered run had ended, all with exit status 0, and seven manifests still said
  "running" or "submitted": G5 geoc (-163800-fe87748), R2 c (-163901-9b7e6e6), R2 a, b
  (-165411-a48c7e0), S (-165619-a6cb9fd), the G5 analysis (-170729-b99adc7), the card job
  of test U (-150317-a1e8ee7, Slurm 4651: 18 min 28 s, 0.31 card-hours, 16 runs, each
  with rc = 0) and the card job of C2 (-155551-9096ee7, Slurm 4661, 2 s). Closed with
  `nrpic-run finish`. The 14 hand-written manifests of the sub-runs of R2 c and the draft
  of the answer to Track E (`tracks/core/outbox/`, placeholders unfilled) were untracked.
- No card job of this package is queued; 0.31 of the one card-hour is spent.
- Read today before anything below was written: the summaries and figures of R2, S and
  the G5 analysis (their outcomes are entry 16; their predictions are entries 8 to 10).
  Of the card runs of U only the exit codes, the file lists and the wall time per run
  (11 s at 64^3, 123 s at 128^3 with 1054 modes, 131 s with 68532 modes, dumps included);
  of C2 the last lines of the card log (20 cycles, exit 0). No field, record or
  comparison of U on the cards or of C2 has been looked at.

**What runs now.**
1. Analysis of the card runs of U, one registered run per group (L64, K64, L128, K128;
   `u2_usr_analysis.py --prefix`). The predictions PC1 to PC5 of entry 4 stand as
   written. The driver gets two more classes of modes, which PC2 and PC3 name and it did
   not have: |n| <= 8 and the shell |n| = 8. How two statements of entry 4 are evaluated
   (fixed here, before the numbers exist): PC1 compares <Pi> against the reference at 3,
   5, 8 e-folds and at the end with the 32^3 values of run -161122-a46833e (2.56e-6,
   1.72e-5, 4.01e-4, 4.13e-4). PC4's last sentence: the largest rms over the dumps of the
   part of H (and of |M|) odd in s = +-1, divided by the rms of the reference R^NR
   (`rms_ref`) at that dump, for K64, K128 and the 32^3 pair of -161122; the dumps are
   0.5 (32^3, K64) and 1.0 (K128) apart in time, so the maxima are sampled coarsely.
2. C2 (`c2_compare.py`, entry 11; the prediction stands).
3. One check added to test S (`s2_sumcheck.py`, no AthenaK run; it reads the dumps and
   the record of run -165619-a6cb9fd). Seen: column [21] differs from the mean of H of
   the dump by 6.2e-13 to 6.3e-13 relative at all seven dumps of the run with s = 1, six
   times the bound of PSb, the same at every dump, and rms H' by half of it (3.1e-13).
   [JUDGEMENT] The equal offset is not an order-of-summation effect of H but of the
   denominator: the code divides by a running sum of 32768 equal cell volumes, and a
   running sum of equal terms rounds in one direction within a binade. Prediction PSd:
   (a) the running sum of 32768 copies of dx1 dx2 dx3 (dx = 6.283185307179586/32, as the
   code forms it) differs from 32768 dx^3 by 6.2e-13 +- 0.2e-13 relative; (b) a serial
   running sum of vol*H over the cells in the order of the reduction (i fastest), divided
   by that running sum of the volumes, equals column [21] within 1e-14 relative at every
   dump of the runs sig and zsig (bit for bit unless the compiler contracted vol*H into
   the sum); (c) the same emulation of the second reduction gives [27] within 1e-13 and
   [25] within 1e-12 relative for sig. Refuted by (a) below 3e-13 or above 1.2e-12, or by
   (b) above 1e-13: then the offset has another cause (the dump would not hold the field
   of the record).

## 2026-11-20, entry 16: C2 as predicted in entry 11 fails in its measure; the comparison in absolute units, predicted

**C2, run core-20261120-220950-9e19164** (card run -155551-9096ee7 of
`athena_gpu_5cc2821` against `athena_cpu_5cc2821`, gauge example, 20 steps; figure
`fig_c2.png`, looked at after this entry was written). As measured against entry 11:
- "The dump at t = 0 bit-identical": HOLDS for every evolved variable and the magnitudes;
  FAILED for the constraint fields, which the dump also holds: H differs by 6.6e-4 of its
  largest value, M_i by 3.4e-4 to 4.0e-4, E by 1.2e-16.
- "Dumps at 0.4 and 0.8 within 1e-12 of the largest value of each variable (H, M_i
  within 1e-11)": FAILED. At cycles 9 and 17 the largest differences are 4.4e-8 and
  4.1e-8 of the largest value for At_ij and 7.5e-3 and 5.2e-3 for H and M_i.
- "Record columns within 1e-10 relative, the H' columns within 1e-8": FAILED but for the
  five means of quantities of order one (phi, Pi, K, alpha, [H]: 6.3e-13 to 6.4e-13).
  H_ratio 1.1e-5, H_rms 5.7e-6, M_ratio 7.1e-6, H_mean 4.7e-5, Hp_ratio 3.9e-5, Hp_rms
  9.4e-6, the maxima 1.2e-3 to 4.4e-3, rms|M_bssn - M_adm| 0.10, the e-folds 1.0 (their
  value at t = 0 is rounding). All 27 columns are present.
The prediction took the bounds of the card check of J2 ("fields within 3.3e-14, constraint
fields within 3.4e-13"), which are absolute differences, as fractions of the largest
value of each variable. In this case the perturbations are small (At_ij of order 1e-7, H
of order 1e-11 with terms of order 10 that cancel), so a rounding difference of 1e-14 is
1e-7 of At_ij and 1e-3 of H. Whether the differences are of that absolute size has not
been computed; the measure above cannot tell rounding from a defect of the card
executable.

**C2b, predicted** (`c2_compare.py --cpu`, the same two runs, differences in absolute
units; no number of this kind has been seen). If the two executables differ by rounding
only (another order of the operations in the stencils and of the summation in the
reductions on the card):
- every evolved variable of the dumps (phi, Pi, chi, K, Theta, alpha, gt_ij, At_ij, the
  conformal connection) is bit-identical at t = 0 and within 1e-13 in absolute value at
  cycles 9 and 17 (J2: 3.3e-14 after 20 steps at this resolution), and the difference at
  cycle 17 is less than four times that at cycle 9 (a random walk gives 1.4);
- H within 1e-12 and M_i within 1e-12 in absolute value at all three dumps (J2: 3.4e-13),
  i.e. H within 1e-13 of its magnitude [H] = 12;
- of the record: the absolute difference of <|H|/[H]>, <|H'|/[H]> and of their maxima
  below 1e-13, of <H> and rms H' below 1e-12; <|M|/[M]> is a ratio to a magnitude of
  order 1e-6 and may differ by up to 1e-6 in absolute value.
Refuted, and then the card executable is not published as tested, by an evolved variable
that differs at t = 0, by a difference above 1e-12 at cycle 17, by growth by more than a
factor 10 between the cycles, or by a difference of H above 1e-11.
