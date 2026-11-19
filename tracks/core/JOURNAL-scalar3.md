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
