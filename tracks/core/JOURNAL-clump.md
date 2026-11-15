# JOURNAL of core, work package clump (extrinsic curvature of moving matter clumps)

Branch `core/clump-curvature`, worktree `wt/core-clump`. Append-only, newest at the bottom.
Predictions are written before a test runs, outcomes after. Labels: [VERIFIED] read from
a source with a locator or measured in a registered run, [BACKGROUND], [JUDGEMENT],
[TO VERIFY]. Units G = c = 1.

## 2026-11-15  session clump-1

### Read

- `CLAUDE.md`, charter to "Owners", the brief by the named line ranges (493-553, 688-706,
  834-860), rulings after wave 1 and decisions 0010 to 0015, core's `HANDOFF.md`,
  `STATUS.md`, `stage/G2/OPEN.md` (core has no G0/G1 package; G2 is the open one).
- `coord/notes/design_wave2_initial_data.md` section 3 (the task); the request of Track F
  (`track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-core__moving-clump-initial-data.md`:
  two equilibrium clumps of 0.05 M, compactness 0.05 to 0.1, with bulk momenta, next to a
  heavy puncture; acceptance: an isolated moving clump keeps its profile for 200 M, the
  momentum-constraint residual against the closed form for P/m <= 0.3; smallest
  acceptable answer: the plan and the wave).
- `coord/INTERFACES/multi_puncture.md` (Bowen-York punctures: `comp<c>_p1..3`, `_s1..3`,
  curvature added with `+=` after the generator's `K_ij = 0`; section 3 "With matter that
  moves, the momentum constraint has a source 8 pi psi^4 Stilde^i that Bowen-York
  punctures do not supply"), `coord/INTERFACES/particle_id.md` (section 3.1 and rule 2 of
  section 5), `coord/INTERFACES/deposit.md` (sources, clouds, filter).
- `paper/sections/appendix_sampling.tex` lines 22 and 73-77 (Gaussian components: m_p =
  m_c N_c^-1 psi W_c^-1, bulk orthonormal momentum lowered with psi^2; "Orbital motion of
  the cold components on a slice with K_ij = 0 leaves a first-order violation of the
  momentum constraint, which is left uncorrected"). [VERIFIED]
- Source: `athenak/src/pgen/nrpic/nrpic_cf.cpp`, `nrpic_bowen_york.hpp`,
  `athenak/src/z4c/z4c_adm.cpp` lines 480-514 (the constraints the code evaluates:
  `M^a = D_c K^ca - D^a K - 8 pi S^a`), `outputs/history.cpp` lines 175-250 (norms),
  `particles/nrpic_io.cpp` lines 1233-1274 and `nrpic.cpp` lines 1381-1416 (the sources
  are deposited at start-up and the constraints recomputed with them, so the record at
  t = 0 contains the matter), `python/nrpic/clumps.py`, `sampling.py`,
  `problems/ic/make_ic.py`.
- The run of the first paper: `runs/jeans/n1e4_v19/chain/input.athinput` and
  `chain/config.sh` (command-line overrides: domain +-80 M, eight levels),
  `jeans_N10000_s1.json` (generator call `jeans --N 10000 --seed 1 --env-yc 0.907`),
  `notes/results_brief_selfgravity.md` lines 290-373 and 429-454 (remnant 1.0255 at
  100 M, 2.5 percent above M = 1; candidates). Its history at t = 0
  (`jeans.z4c.user.hst`, first row): H-norm2 33.9040, M-norm2 0.191587, Mx-norm2
  0.0174028, My-norm2 0.263081, Mz-norm2 0.0165197. [VERIFIED]

### Derivation [VERIFIED by `tracks/core/analysis/clump/derive_smeared_by.py`, sympy]

Conformal decomposition `gamma_ij = psi^4 delta_ij`, `K_ij = psi^-2 Abar_ij`, `K = 0`.
The code's momentum constraint `D_j K^ij - D^i K = 8 pi S^i` becomes, with flat indices,

    d_j Abar_ij = 8 pi psi^10 S^i = 8 pi psi^6 S_i = 8 pi Stilde_i,
    Stilde_i(x) = sum_p m_p u_(i,p) delta^3(x - x_p),

because the deposit forms `S_i = sum_p m_p u_(i,p) w_p/sqrt(gamma)` and
`sqrt(gamma) = psi^6` (`coord/INTERFACES/deposit.md` section 1). `Stilde_i` is the
coordinate density of the covariant particle momentum; psi drops out; the equation is
linear in `Abar_ij`, so clumps and punctures superpose.

Write `Abar_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k`; then
`lap W_i + (1/3) d_i d_k W_k = 8 pi Stilde_i`. For `Stilde_i = P_i f(r)` with a spherical
profile of unit integral let `lap phi = -4 pi f`, `lap chi = 2 phi`. Then

    W_i = -2 P_i phi + (1/4) P_j d_i d_j chi

solves it (for `f = delta^3`: `phi = 1/r`, `chi = r`, the Bowen-York vector
`-(7 P_i + n_i P.n)/(4r)`), and

    Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
            + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
    Q(r)  = 4 pi int_0^r f r'^2 dr',     I4(r) = 4 pi int_0^r f r'^4 dr'.

The first line is the Bowen-York curvature of the momentum enclosed by the sphere
through the point; the second is the regular homogeneous solution of Bowen and York
weighted by the enclosed second moment. It holds for any spherical profile. For the
Gaussian `g = (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2))`, `t = r/(sqrt 2 sigma)`:

    phi = erf(t)/r,   chi = (r + sigma^2/r) erf(t) + sigma sqrt(2/pi) exp(-t^2),
    Q  = erf(t) - (2/sqrt pi) t exp(-t^2),
    I4 = 3 sigma^2 [erf(t) - (2/sqrt pi) (t + 2 t^3/3) exp(-t^2)].

Spin analogue (cheap): the point source of the Bowen-York spin term is
`Stilde_i = -(1/2) eps_ilm S_l d_m delta^3`; smeared with the Gaussian it is
`Stilde_i = (S x x)_i g/(2 sigma^2)`, the Gaussian in rigid rotation with angular
momentum S (moment of inertia 2 m sigma^2). `W_i = (S x grad phi)_i`, divergence free,

    Abar_ij = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i],    C = Q - (4 pi/3) r^3 g.

Checked symbolically at two rational points to 50 digits (every line prints ok): the
two Poisson equations, the vector equation, `(LW)_ij` against both closed forms,
tracelessness, `d_j Abar_ij = 8 pi Stilde_i` for momentum and spin, `Abar_ij Abar_ij`
(`2 a^2 P^2 + (P.n)^2 (2a^2 + 4ab + 4ac + 3b^2 + 2bc + c^2)` with a, b, c the
coefficients of `P_i n_j + P_j n_i`, `delta_ij P.n`, `n_i n_j P.n`; spin
`18 C^2 (S^2 - (S.n)^2)/r^6`), the power series of Q, I4, C used below t = 0.5 (the
closed forms cancel: Q like t^3, I4 and C like t^5), and the limits: r -> infinity
gives Bowen-York plus `3 sigma^2/(2 r^4) [..]`; r -> 0: `a -> (12 pi/5) g(0) r`,
`b -> -(8 pi/5) g(0) r`, `c -> (4 pi/35) g(0) r^3/sigma^2`, `3C/r^3 -> (4 pi/5) g(0)
r^2/sigma^2`. One slip of mine was caught by the check: I had written the limit of c as
`(4 pi/7) g(0) r^3/sigma^2` by hand; sympy gives 4 pi/35 (redone by hand: -3/20 + 5/28
= 4/140).

Hamiltonian constraint. The generator solves `lap psi = -2 pi psi^-1 Etilde`; with the
curvature the code's `H = R + K^2 - K_ij K^ij - 16 pi E` keeps
`H = -psi^-12 Abar_ij Abar_ij`, second order in P and S, algebraic (no derivative).

### What the particles must carry [JUDGEMENT, derived]

The first paper's rule gives every clump particle the orthonormal velocity v:
`u_i = psi^2 W v_i`, `m_p = (m_c/N) psi/W`, hence `m_p u_(i,p) = (m_c/N) psi^3 v_i` and
`Stilde_i = m_c v_i psi^3 g`: not the Gaussian, because psi varies across the clump. The
smeared curvature with `P = sum_p m_p u_p` then leaves `8 pi m_c v (psi^3 - <psi^3>) g`.
Second rule, exact in the continuum: every particle carries the same share of the
momentum, `m_p u_(i,p) = [P_i + (S x d_p)_i/(2 sigma^2)]/N`, and the energy
`m_p W_p = (m_c/N) psi` (which the Hamiltonian constraint fixes), so
`m_p = sqrt((m_c psi/N)^2 - |m_p u_p|^2/psi^4)`. Its orthonormal speed is
`|P + S x d/(2 sigma^2)|/(m_c psi^3)`, smaller where psi is larger. That is the
direction of a truly boosted body: the first-order Lorentz boost of a static conformally
flat solution has `u_i = alpha V_i` on its boosted slice (shift
`beta^i = -(1 - alpha^2/psi^4) V^i`), orthonormal speed `V alpha/psi^2`, which also falls
towards the centre (`Stilde_i = rho~ V_i psi alpha/W`, about `rho~ V_i/psi` in a weak
field, between the two rules). Both rules are in the generator (`velocity`, `gaussian`).

### Design decisions [JUDGEMENT]

1. Own header `athenak/src/pgen/nrpic/nrpic_clump_curvature.hpp` (namespace
   `nrpic_clump`: moments with their series, curvature of one clump, reader). Options
   as for punctures: `comp<c>_p1..3`, `comp<c>_s1..3` on a component of type `gaussian`.
2. Hooks: `nrpic_cf.cpp` one include, one reader call after the Bowen-York reader, one
   block after the Bowen-York block of the main loop adding `psi^-2 Abar_ij` with `+=`
   (so it combines with punctures and with a table of format 2), three comment lines in
   the file header. `nrpic_bowen_york.hpp`: `BYRead` skips a Gaussian component instead
   of stopping with "need type = puncture" (two lines and the message).
3. No correction of psi for the second-order residual in this package: it is measured
   (test T2). The multipole table of the puncture correction (`corr = table`) could
   carry one later.
4. Generator side: `python/nrpic/smeared_bowen_york.py` (reference twin: moments,
   `abar`, `abar2`, `momentum_density`, `second_order_mass`); `python/nrpic/clumps.py`
   gets `clump_particles` (both rules), the option `momentum` of `JeansModel.sample`
   and the class `GaussianClumps` (isolated clumps with momentum and spin, optional
   punctures; samplers stratified, mc and a weighted lattice for noise-free tests);
   `problems/ic/make_ic.py` gets `jeans --clump-curvature`,
   `--clump-momentum-rule velocity|gaussian` and the model `clumps`.
5. Old behaviour: the new parameters are read only when present; `make_ic.py jeans`
   without the new options must write the same bytes.

### Checks without simulation (done before the tests below)

- P0, `tracks/core/analysis/clump/check_smeared_by.py` (Python reference): trace 4e-16,
  symmetric; divergence by sixth-order differences against `8 pi Stilde_i`: 1.6e-11
  (momentum), 3.1e-11 (spin), 1.7e-11 (both) of the largest source; moments against
  quadrature 9e-15; series/closed-form switch continuous to 9e-13;
  `P_ADM = P` and `J_ADM = S` on spheres of 12 and 60 sigma to 2e-14; far field equal to
  Bowen-York plus the regular term to 3e-16, 7.3e-4 away from Bowen-York alone at 40
  sigma; sigma -> 0 gives Bowen-York (2.6e-6). `(1/16 pi) int Abar^2 d^3x` =
  1.0343 P^2/sigma (momentum), 0.0940 S^2/sigma^3 (spin). [VERIFIED, no run id: analysis
  of closed forms; first version of the script failed one line because my comparison
  series for C was truncated at t^13 (2.9e-10); two more terms, then 9e-15.]
- `make_ic.py jeans --N 10000 --seed 1 --env-yc 0.907` with the changed generator:
  particle file and table have the sha256 of `runs/jeans/n1e4_v19/particles.nrp`
  (7270917f...) and `envelope.tab` (7ea9ca27...). [VERIFIED]

### Predictions (written 2026-11-15T15:45Z, before any AthenaK run of this package)

Numbers below are from `tracks/core/analysis/clump/predict.py` (quadratures of the
closed forms; one-dimensional emulation of the deposit of lattice particles; written to
`predict.json`). Norms as the history file defines them: `M-norm2 = int psi^2 sum_i
M_i^2 d^3x`, `Mx-norm2 = int psi^6 M_x^2 d^3x`, `H-norm2 = int psi^6 H^2 d^3x`.

Set-up of T1 to T4 and T6: one Gaussian clump, conformal mass 0.2, sigma = 1 (psi = 1.0798
at the centre, like the clumps Track F asks for), momentum along x, box [-8, 8]^3,
`nghost = 4`, linear cloud, four filter passes with compensation (the setting of the
first paper's cluster runs) unless said; particles on a lattice of spacing 0.125 with
Gaussian weights (noise-free) unless said; processors.

- R (regression). Inputs without the new parameters give byte-identical data files with
  the new executable and the release executable `.work/build_cpu_v03` (restart files up
  to the known never-set header bytes). Refuted by any differing data byte.
- T1 (momentum constraint against resolution, P = 0.06, i.e. P/m = 0.3, rule gaussian).
  (a) Without curvature the residual is the deposited momentum density: M-norm 0.1651
  (Mx-norm 0.1871), the same within 2 percent at 32, 64, 128 cells per side.
  (b) With curvature the residual is what the cloud and the filter do to the Gaussian
  plus the truncation error of the derivative: ratio to (a) 0.130, 0.0202, 7.0e-4 at 32,
  64, 128 cells (within a factor 1.5; the emulation ignores the division by psi^6
  before the filter and the finite differences), i.e. order 2.7 then 4.8. Without filter
  (`nfilter = 0`): 0.040, 0.011, and at 128 cells, where every lattice particle sits on
  a cell centre, only the truncation error of the sixth-order derivative (below 1e-4).
  (c) Wrong sign of P in the curvature: exactly twice the residual of (a) (2.00).
  (d) Linear in P: residuals of (a) and (b) for P = 0.02, 0.04 are 1/3 and 2/3 of P =
  0.06 to 1e-3 (the particle masses change at second order only).
  (e) Equal-mass stratified samples at 64 cells with curvature: shot noise M-norm at
  most 0.0144, 0.0045, 0.0014 for 10^4, 10^5, 10^6 particles (Poisson; stratification
  can lower it), against the continuum part 0.0202 x 0.165 = 0.0033: the continuum part
  shows only from about 10^6 particles on; without curvature the norm is 0.165 at every
  N (noise adds in quadrature, +0.4 percent at 10^4).
  Refuted if: the ratio in (b) does not fall with resolution, or stays above 0.3; (c) is
  not 2.00 +- 0.01 (sign or normalisation wrong); the noise does not fall as N^-1/2.
- T2 (Hamiltonian residual at second order). `H(with) - H(without)` is
  `-psi^-12 Abar_ij Abar_ij` cell by cell (algebraic; agreement to the single precision
  of the dumps, 1e-6 of its peak), peak 7.65e-4 at P = 0.06 against 0.433 for the matter
  term 16 pi E; norm of the difference 6.10e-4, 2.44e-3, 5.49e-3 for P = 0.02, 0.04,
  0.06 (ratios 1 : 4 : 9). The residual without curvature (cloud and filter acting on E)
  does not depend on P. Refuted if the difference is not the closed form or scales
  otherwise.
- T3 (spin, S = 0.04 along z, rule gaussian, rotation speed 0.1 at one sigma). Without
  curvature M-norm 0.0570; with curvature the same ratios as T1 (b) within a factor 2.
- T4 (rule velocity, the first paper's rule, with the curvature of P = sum m u). The
  curvature removes the residual up to the variation of psi^3 across the clump: ratio
  0.034 at 128 cells (against 7e-4 for the rule gaussian); at 32 cells both are set by
  the cloud (0.13).
- T5 (two overdensities of the first paper at t = 0, mesh and particles of
  `n1e4_v19`, processors). Clump momenta `sum m u` after the generator's mean removal:
  (-2.5e-5, -0.0218556, -2.3e-5) and (-2.5e-5, +0.0219366, -2.3e-5).
  (a) Without the new parameters the record at t = 0 repeats the run's: H-norm2 33.904,
  M-norm2 0.19159, Mx 0.017403, My 0.26308, Mz 0.016520 (to 5 digits; the run was made
  on a card with an older executable).
  (b) The norm is shot noise: the smooth part of My-norm2 is 0.0211 (M-norm2: 0.0135)
  of 0.263 (0.192). With the curvature and the same particles My-norm2 falls by that
  amount, to 0.242 +- 0.003, M-norm2 to 0.178 +- 0.003 (7 to 8 percent of the square, 4
  percent of the norm); Mx, Mz and H change by less than 1 percent (H by the
  second-order term, 1e-5 of its square).
  (c) Projection of M_y on the smooth field `T = -8 pi psi^-6 Stilde_y` (closed form,
  rule velocity), `A = <M_y, T>/<T, T>` with the weight psi^6 dV: 1.00 +- 0.05 without
  curvature, 0.00 +- 0.05 with (what the psi^3 variation leaves is 2.9 percent of T in
  norm and nearly orthogonal to T).
  (d) Particles regenerated with the rule gaussian (same positions) and the curvature:
  as (b) and (c) within the noise.
  Refuted if My-norm2 does not fall by 0.021 +- 0.005 or the projection with curvature
  is not near zero.
- T6 (one clump evolved 2 M on processors, 64 cells, lattice of spacing 0.25, P = 0.06,
  1+log lapse, Gamma-driver shift from zero) [JUDGEMENT, weak]. With the curvature the
  momentum-constraint norm stays below 0.2 of the uncorrected run's at every record of
  the first M; the uncorrected norm starts at 0.165 and decays only as the violation
  propagates (still above 0.05 at 1 M). The sum of the particle momenta `sum m u_x`
  changes less with the curvature than without (without it the metric does not move
  with the matter at first). Refuted if the corrected run's momentum-constraint norm
  rises to the uncorrected one within 1 M.

### Prediction for the rerun of the two-overdensity case (written before any run; the run is the orchestrator's to schedule)

Input: `problems/jeans/jeans_mc.athinput` (the configuration of `n1e4_v19` with its
command-line overrides written in, plus `comp1_p1..3`, `comp2_p1..3`), the particle file
and table of `n1e4_v19` unchanged (regenerated bytes identical). One change: the
curvature.

1. The remnant-mass excess stays. [JUDGEMENT] Predicted `M_AH(100 M) = 1.025 +- 0.010`
   (run `n1e4_v19`: 1.0255), i.e. the 2.5 percent are not removed. Reasons: (i) the
   violation is first order in the orbital speed but every mass it can misplace is
   second order: kinetic energy of the two clumps 2 m_c (1 - 1/W) = 2.1e-3 M, energy of
   the curvature (1/16 pi) int psi^-7 Abar^2 = 6.0e-4 M (both from `predict.json`),
   ten times less than 0.025 M; (ii) the smooth part of the momentum-constraint
   violation is 7 percent of the squared norm at t = 0, the rest is particle noise that
   the curvature does not touch, and the norm grows 4.2-fold by 0.5 M whatever the
   start (first rows of `jeans.z4c.user.hst`: M-norm2 0.19 to 3.32); (iii) in the run
   the slice mass at 36 to 72 M stays within 0.4 percent of 1 up to 50 M and rises
   between 55 and 85 M (`notes/results_brief_selfgravity.md` item 13), so the excess
   does not leave the centre at t = 0.
   Refuted if `M_AH(100 M) < 1.010`: then the momentum constraint of the start matters
   for the excess and the candidate of the paper's open question holds.
   Not covered: the sensitivity of this 10^4-particle run to any small change of the
   start is unknown (no second complete run of this configuration exists); a change of
   the merger time by a few M would move the mass at 100 M by less than the 0.7 percent
   it still gains over the last 10 M.
2. Angular momentum. [JUDGEMENT] With K_ij = 0 the slice has J_ADM = 0 although the
   particles carry L_z = 0.1278 (clumps 0.1314); the run ends with S = 0.0890 and
   S_z + L_z = 0.091 from 57 M on (item 10 of the notes). With the curvature
   J_ADM = 0.1314 at the start. Predicted: S_z of the common horizon plus L_z of the
   remaining particles is 0.115 to 0.135 from the first common horizon on, and the
   remnant's S at 100 M is above 0.105 (chi above 0.10 instead of 0.085). Refuted if
   S(100 M) < 0.100.
3. Merger. [JUDGEMENT, weak] More orbital angular momentum reaches the pair, so the
   common horizon is first found later than 57.0 M, by 1 to 6 M (towards the 64.2 M of
   the original). Refuted if it is found earlier than 56 M.
4. Constraint norms after the first M and the individual black-hole masses at the first
   horizons (0.0976, 0.0992 M at 10.5 M) change by less than their scatter between the
   two M/64 runs of the notes (3 percent).

### Smoke run (after the predictions were written; not registered, not used for a number)

2026-11-15T15:50Z: `problems/tests/clump_static.athinput` with the processor executable
of this worktree, 64 cells, a lattice of spacing 0.25, `comp0_p1 = 0.06`, in
`scratch/core/tmp/clump/smoke/`: the input parses, the log prints "smeared Bowen-York
curvature on 1 Gaussian component(s)", 5.8 s. The executables `.work/build_cpu` and
`.work/build_gpu` were built from the working tree whose source files are those of the
first commit of this package (no source edit between the build and the commit).
