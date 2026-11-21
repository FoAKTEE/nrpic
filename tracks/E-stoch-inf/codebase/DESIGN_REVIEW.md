# Design review: a scalar field with stochastic sources in this repository's AthenaK (E-pre-2)

Owner E-stoch-inf; written by the E-pre-2 helper on 2026-11-15 for core (branch
`core/scalar-field`), who implements, and for the owner, who decides at G0. Decision 0010
settles the code base: Track E builds on this AthenaK; nothing here proposes an outside or
standalone code. Labels: [VERIFIED] read at the locator or checked by a registered run of
this package; [BACKGROUND] standard, not re-checked; [JUDGEMENT] design inference or
recommendation; [TO VERIFY] open. Code locators are `file:line` at commit a1c2237 of
`main` (paths under `athenak/src/`). Paper locators use the keys of
`tracks/E-stoch-inf/spec/SPEC.md` (P1 = arXiv:2512.14649 v2 `PRD_v2.tex`, P0 = 2401.08530,
P2 = 2502.06783, TH = 2610.32592), read at `kb-data/raw/arxiv/<id>/<v>/src/`.

Runs of this package: E-stoch-inf-20261115-122727-a1c2237 (memory and throughput of
periodic vacuum Z4c, processor) and E-stoch-inf-20261115-123936-b2ec5c7 (checks D1 to D4
and the cost table). Predictions and outcomes: `JOURNAL.md`. Reference code: `ref/`.

## 0. Summary for core

1. The scalar field is a second matter module of the numerical-relativity task list, built
   like `dyn_grmhd` and not like the particles. Its sources depend on the field at every
   Runge-Kutta stage, so it fills Tmunu in a stage task before `Z4c_CalcRHS`, as
   `MHD_SetTmunu` does. The particles instead deposit once per step after the update
   (section 2.4). Equations in the code's variables and signs: section 3.
2. The stochastic kicks go into the right-hand sides of `vKhat`, `vA_dd` and Pi, and of
   nothing else. They are evaluated at the stage times of the driver's RK4, which are
   c = (0, 1.19374, 0.43140, 1) (run ...-123936-b2ec5c7, D4). With the sign-safe form of
   the Pi kick and with the projector built from the stencil's wave number k_eff, the kick
   satisfies the discrete first-order momentum constraint to rounding; with the paper's
   k it misses by up to 6.9e-3 at k_max (D3). Section 5.
3. `athenak/src` has no Fourier transform (section 6.1). None is needed. Each wave
   vector's amplitude is a closed-form function of time, so the noise is synthesized
   from its Fourier coefficients MeshBlock by MeshBlock with three one-dimensional sums.
   This agrees with numpy's FFT to 1.2e-14 of the rms and is bitwise independent of the
   MeshBlock layout (D2). It costs 4 to 14 percent of a 256^3 step (section 8). The
   amplitudes are drawn once per wave vector from `core/rng` (stream 3, entity = wave
   numbers).
4. Shared with Track B: the periodic Z4c and its gauge options, which already express
   geodesic slicing with no new code; the initial-data file of `nrpic_cosmo`, which needs
   only two more arrays (phi, Pi); the diagnostics. The constraint solve through K (CTTK)
   is not needed for the two test cases. It is needed for the later field-to-particle
   hand-over, and so is an additive Tmunu (section 7).
5. Compute: one 256^3 realisation costs 0.36 to 0.51 card-hours at a Courant factor of
   0.25, or 3.6 to 5.1 at the 0.025 of P2. Memory is about 20 GB of the 80 GB card, and
   512^3 does not fit on one card (section 8, runs D1 and cost).
6. `core/scalar-field` has no interface document yet (checked 12:55 UTC, branch at
   a9fec22). Section 9 lists what it must state, as requests.

## 1. What the code has: the spacetime solver and its matter coupling

**Variables** (`z4c/z4c.hpp:47-57`): chi, gt_ij (`g_dd`), Khat, At_ij (`vA_dd`), Gt^i
(`vGam_u`), Theta, alpha, beta^i; 22 evolved fields in `u0`, with registers `u1`, `u_rhs`.
chi = psi^(chi_psi_power) with default -4 (`z4c.cpp:125`), so chi = gamma^(-1/3), the X of
P1. K = Khat + 2 Theta (`z4c_calcrhs.cpp:388`). `use_z4c = false` zeroes the Theta
right-hand side (BSSN; `z4c_calcrhs.cpp:646`, `z4c.cpp:159`). [VERIFIED]

**Signs.** d_t gt_ij = -2 alpha At_ij + L_beta gt_ij (`z4c_calcrhs.cpp:665`), so
K_ij = -(1/2 alpha)(d_t gamma_ij - L_beta gamma_ij) and K = -3H in an expanding universe;
d_t chi = (2/3) chi alpha K + ... (`:628-629` with chi_psi_power = -4). The metric is
ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i + beta^i dt)(dx^j + beta^j dt). P1 writes
(dx^i - beta^i dt) (P1:333-336, 671); with beta = 0, as in both test cases, the difference
does not arise. [VERIFIED]

**Matter coupling** (`z4c/tmunu.hpp:28-58`): undensitised E, S_i, S_ij in `u_tmunu`
(n_mu n_nu T^munu, -gamma_i^mu n^nu T_munu, gamma_i^mu gamma_j^nu T_munu). They enter
`CalcRHS` at `z4c_calcrhs.cpp:620-627` (Khat: +4 pi alpha (S + E)), `:639-644` (Theta:
-8 pi alpha E), `:648-660` (Gt^i: -16 pi alpha gt^ij S_j), and `:674-679` (At_ij:
-8 pi alpha (chi S_ij - S gt_ij/3)). They enter the constraints at `z4c_adm.cpp:480`
(H -= 16 pi E) and `:488` (M^i -= 8 pi S^i). The units are G = 1, so Mpl^-2 = 8 pi.
A second set `u_tmunu_step` holds the step's sources in density form; the solver multiplies
them by 1/sqrt(gamma) at every stage and adds Lambda (`tmunu.hpp:49-58`,
`z4c_calcrhs.cpp:155-165, 485-493`). The solver reads either `tmunu` or `tmunu_step`,
never both. [VERIFIED]

**How the two existing matter modules fill it.**
- `dyn_grmhd`: `MHD_SetTmunu` is a task of every stage (`dyn_grmhd/dyn_grmhd.cpp:198-201`).
  It writes (does not add) E, S_i, S_ij from the conserved variables (`:412-477`) and is
  an optional dependency of `Z4c_CalcRHS` (`z4c/z4c_tasks.cpp:48-61`). `Z4c_ExplRK` waits
  for the MHD tasks that read the metric (`:64-65`, optional `MHD_EField`). It reads the
  metric from `padm->adm`, which `ConvertZ4cToADM` refreshes at every stage only when
  `pdyngr` exists and otherwise only at the last stage (`z4c_tasks.cpp:221-226`).
  [VERIFIED]
- NRPIC particles: operator split. The metric at t^n is saved before the spacetime step,
  then after it come the push, the excision, the deposit at t^(n+1) and the conversion to
  density form (`particles/nrpic.cpp:11-18, 1208-1266, 1343-1359`; tasks in
  `particles_tasks.cpp:31-42`, lists `before_timeintegrator` and `after_timeintegrator`).
  The sources are therefore fixed over the step up to the volume element. [VERIFIED]

**Task list, integrator, boundaries, refinement.**
- `NumericalRelativity` builds the stage list from queued tasks with named dependencies.
  A task whose physics module is absent is dropped (`tasklist/numerical_relativity.hpp:
  31-93`, `numerical_relativity.cpp:40-61, 154-163`). The pack creates the NR list
  before the particles (`mesh/meshblock_pack.cpp:225-246`). [VERIFIED]
- Integrators: `rk4` is the low-storage RK4()4[2S] of Ketcheson (2010)
  (`driver/driver.cpp:144-175`): u0 <- gam0 u0 + gam1 u1 + beta dt F(u0) with
  u1 <- u1 + delta u0 (`z4c_update.cpp:37-41`, `z4c_tasks.cpp:155-186`). It is not
  classical RK4, so its stage times differ (section 5.4). `CalcRHS` reads `pmesh->time`,
  the start of the step, at every stage (`z4c_calcrhs.cpp:44`); no stage time exists.
  [VERIFIED]
- Time step: Z4c takes dt = cfl_number x min(dx) (`z4c_newdt.cpp:26-60`), independent of
  alpha and of the expansion. [VERIFIED]
- Boundaries: periodic boundaries skip the physical boundary conditions (`z4c_tasks.cpp:
  285, 306`). Sommerfeld conditions exist for non-periodic boxes (`z4c_Sbc.cpp`).
  Kreiss-Oliger dissipation acts on the 22 Z4c fields only (`z4c_calcrhs.cpp:763-773`).
  [VERIFIED]
- Mesh refinement: `z4c_amr.cpp:28-40` (trivial, tracker, chi, dchi, Lohner). Prolongation
  and restriction of `u0` are generic cell-centred operations (`z4c_tasks.cpp:268-298`).
  Restart files hold `pz4c->u0` (`outputs/restart.cpp:117-121`). Binary output is single
  precision (Track B, `periodic_z4c/README.md` on `track/B-emd-gw`). [VERIFIED]
- Finite differences: nghost = 2, 3, 4 give centred orders 2, 4, 6
  (`utils/finite_diff.hpp:24-61`), so P1's sixth order is nghost = 4. [VERIFIED]
- Constraint statistics (absolute and relative H, M, written to `.cstat.hst`) live in the
  particle module and require a deposit (`particles/nrpic_io.cpp:280-291`). Their relative
  measure divides by the root of the sum of squared terms; P1 divides by the sum of
  absolute terms, [H] (P1:735-745). [VERIFIED]

## 2. Where the scalar field goes in the code

### 2.1 Layout [JUDGEMENT]

The scalar field gets its own class (`ScalarField`, e.g. `athenak/src/z4c/scalar_field.*`
or its own directory). It has registers u0, u1, u_rhs (2 fields: phi, Pi), its own
`MeshBoundaryValuesCC`, restart entries and outputs, and it queues its tasks into
`NumericalRelativity`. This means new `TaskName` entries `SF_*`, a `Phys_SF` dependency
(`numerical_relativity.cpp:40-61`), a call in `AssembleNumericalRelativityTasks`
(`:154-163`), construction before `pnr` in `meshblock_pack.cpp:225-230`, and a `Tmunu`
when the field exists.

The alternative is to append phi and Pi to the Z4c state vector. Communication,
prolongation, restart and dissipation would then come for free. But `nz4c` is a
compile-time enum used to size buffers and loops (`z4c.hpp:47-57`,
`z4c_tasks.cpp:126, 163`, `z4c_update.cpp:35`, `restart.cpp:78`), so every vacuum and
particle run would change. The separate class keeps those runs bitwise unchanged, which is
the regression check core already uses (`tracks/core/interfaces/rng.md` on `core/rng`,
section 7, row "Existing behaviour unchanged").

### 2.2 Stage tasks and their order [JUDGEMENT]

| Task | Reads | Writes | Must come after | Must come before |
|---|---|---|---|---|
| SF_CopyU | SF u0 | SF u1 | stage start | SF_ExplRK |
| SF_SetTmunu | SF u0 (interior and ghosts), Z4c u0 (chi, gt) | Tmunu (scalar part) | stage start | Z4c_CalcRHS, SF_ExplRK |
| SF_Noise (when stochastic) | coefficients at the stage time | noise fields I_R, T_ij | stage start | Z4c_CalcRHS, SF_CalcRHS |
| SF_CalcRHS | SF u0, Z4c u0 (chi, gt, Gt, alpha, beta, Khat, Theta), I_R | SF u_rhs | stage start | Z4c_ExplRK (Z4c u0 is overwritten there) |
| Z4c_CalcRHS (+ kick) | Z4c u0, Tmunu, I_R, T_ij | Z4c u_rhs | SF_SetTmunu, SF_Noise | Z4c_ExplRK |
| SF_ExplRK, SF_Restrict, SF_SendU/RecvU, SF_Prolong, SF_BCS | | SF u0 | SF_CalcRHS | next stage |

Two hazards to avoid:
- `SF_CalcRHS` needs the metric of the stage start, so `Z4c_ExplRK` must list it as a
  dependency, as it lists `MHD_EField` (`z4c_tasks.cpp:64-65`).
- `SF_SetTmunu` must not take gamma_ij from `padm->adm`, which is stale except at the last
  stage when `pdyngr` is null (`z4c_tasks.cpp:221-226`). Form gamma^ij = chi gt^ij from
  the Z4c u0 of the stage.

### 2.3 Other code requirements [JUDGEMENT]

- Kreiss-Oliger dissipation for phi and Pi with its own coefficient (P1 used none, P1:512
  footnote).
- Mesh refinement: generic prolongation and restriction of phi and Pi. The noise needs
  none, because it is a closed-form function that can be evaluated at any cell centre
  (section 6).
- Restart of phi and Pi, the step counter that keys the random numbers (`rng.md`
  section 5, rule 2), and the mode amplitudes (section 6.2) if they are evolved instead of
  recomputed.
- Outputs of phi and Pi in double precision. Float32 cannot resolve the perturbation
  1e-5 on chi = 1 to better than about 0.6 percent (relative precision 6e-8).
- Constraint statistics that do not depend on the particle module, with P1's [H] and [M]
  as an option.
- Time step: the light speed is unchanged, so the Courant step of Z4c covers the field.
  The mass term needs m dt << 1, which holds during inflation (m ~ H) and must be checked
  in the oscillating phase after it.

### 2.4 Tmunu when several modules are present [JUDGEMENT]

`DynGRMHD::SetTmunu` sets rather than adds (`dyn_grmhd.cpp:413-414` comment). The particles
own `u_tmunu` and `u_tmunu_step` (`nrpic.cpp:1215-1249`), and the solver reads one of the
two (`z4c_calcrhs.cpp:159-165`). The scalar field alone can use `u_tmunu`. For the
hand-over (section 7.2) the solver must read the stage-wise scalar sources plus the
step-wise particle densities in one pass, and so must the constraints and the constraint
statistics. Proposal: a separate scalar container `tmunu_sf`, summed in `CalcRHS`, in
`ADMConstraints` and in the statistics.

## 3. Equations of a minimally coupled scalar field in the code's variables

[BACKGROUND, signs checked against the code locators of section 1 and against P1:351-368
and P1:663-665.]

Definitions: Pi = n^mu d_mu phi = (d_t phi - beta^i d_i phi)/alpha. This agrees with P1's
Pi = alpha^-1 (dot phi + beta^i d_i phi) under P1's opposite shift sign (P1:227, 671).
G = 1. T_munu = d_mu phi d_nu phi - g_munu [ (1/2) g^rs d_r phi d_s phi + V(phi) ].

    |Dphi|^2 = chi gt^ij d_i phi d_j phi
    E     =  Pi^2/2 + |Dphi|^2/2 + V
    S_i   = -Pi d_i phi
    S_ij  =  d_i phi d_j phi + (gt_ij/chi) (Pi^2/2 - |Dphi|^2/2 - V)
    S     =  gamma^ij S_ij = (3/2) Pi^2 - |Dphi|^2/2 - 3 V

    d_t phi = alpha Pi + beta^i d_i phi
    d_t Pi  = beta^i d_i Pi
            + alpha [ chi gt^ij d_i d_j phi - chi Gt^k d_k phi - (1/2) gt^ij d_i chi d_j phi ]
            + chi gt^ij d_i alpha d_j phi
            + alpha K Pi - alpha V'(phi),            K = Khat + 2 Theta

The bracket is D^i D_i phi for gamma_ij = gt_ij/chi:
Delta_gamma phi = chi Delta_gt phi - (1/2) gt^ij d_i chi d_j phi, with
Delta_gt phi = gt^ij d_i d_j phi - Gt^k d_k phi. The sign of the K term gives the
Klein-Gordon friction: alpha = 1 and K = -3H yield ddot phi + 3 H dot phi + V' = 0.
Whether Gt^k is the evolved `vGam_u` or the one computed from gt_ij differs by the
connection constraint times d phi. The computed one matches how `CalcRHS` forms
D_i D_j alpha (`z4c_calcrhs.cpp:499-510`) [JUDGEMENT].

With these sources the code's equations are those of P1:645-669 with Mpl^-2 = 8 pi, up to
the errata E1 and E2 of SPEC section 9, which are mistakes of P1's text and not of the
physics. The constraints in the code's units are H = R + (2/3) K^2 - At_ij At^ij - 16 pi E
and M_i = D_j At^j_i - (2/3) d_i K - 8 pi S_i (`nrpic_io.cpp:283-284`). In the code,
eps1 = 4 pi Pi_b^2 / H_b^2 with H_b = -K_b/3. Unit mapping to P1's Mpl = 100: SPEC
section 2.5. Use the slow-roll parameters with Launay's sign, eps2 = -d ln eps1/dN
(SPEC section 1).

Potentials needed: quadratic, and the Higgs-inflection form of P1:409. A tabulated or
functor potential is enough. V' and V'' are needed: V' for the field equation, V'' only if
level-2 backreaction is ever wanted.

## 4. Gauge

Both cases use geodesic slicing, alpha = 1, beta = 0 (P1:483). The existing options give
it with no new code: `lapse_oplog = 0`, `lapse_harmonic = 0`, `lapse_volume = 0`,
`lapse_kdriver = 0`, `lapse_advect = 0`, `shift_Gamma = 0`, `shift_eta = 0`. Then the
right-hand sides of alpha and beta vanish (`z4c_calcrhs.cpp:687-729`; option defaults at
`z4c.cpp:139-157`) [VERIFIED by code reading]. The constraint damping defaults to off
(`z4c.cpp:131-132`).

Cosmology's conformal-time lapse, d_t alpha = -(1/3) alpha^2 K (`cosmo/README.md`), is a
poor choice during inflation [JUDGEMENT]. The conformal time left after the start is
about 1/(a H), so the step dt = theta dx covers e-folds at a rate a H theta dx that grows
as e^N: the late e-folds would be resolved by a handful of steps. Cosmic time (alpha = 1)
gives a fixed H dt = 2 pi theta/(N sigma) per step (P1:721). The kicks of P1 assume
alpha_b = 1. Under another background lapse every kick carries a factor alpha_b, and W
runs in background proper time (P0 section IV B 3; SPEC section 2.5).

## 5. The stochastic sources: which, where, how

### 5.1 Which terms (P1:297-310, 370-375, 681-691; SPEC sections 2.1-2.2)

    S_R(k,t) = R_k(t) Wddot_k(t) + [ 2 Rdot_k(t) + (3 - eps2) H R_k(t) ] Wdot_k(t),   per alpha_k
    kick of Pi    :  I_Pi  = (Pi_b / H_b) S_R          (sign-safe; P1:299 writes Mpl sqrt(2 eps1) S_R)
    kick of Khat  :  I_K   = -eps1 S_R
    kick of At_ij :  I_A   =  eps1 (delta_ij/3 - q_i q_j / q^2) S_R      (q: section 5.3)
    no kick of chi, gt_ij, Gt^i, Theta, phi, alpha, beta^i.

The relative signs are fixed by the constraints. To first order the Hamiltonian constraint
of the kick is (4/3) K_b I_K - 16 pi Pi_b I_Pi, which vanishes only if I_Pi/I_K =
-(Pi_b/H_b)/eps1. So Pi_b < 0 needs I_Pi < 0. P1's sqrt(2 eps1) Mpl form assumes a field
rolling towards positive phi (SPEC erratum E4). The momentum constraint of the kick is
D_j I_A_ij - (2/3) D_i I_K. It vanishes for the projector above (section 5.3); phi has no
kick, so the matter term -Pi_b d_i(dphi) gets none either [derivation here; JUDGEMENT].
The kick goes into Khat and not into Theta, so K = Khat + 2 Theta receives it and Theta
starts only at second order. Both Z4c and BSSN (`use_z4c = false`) should be run once, as
a check that the choice is immaterial at the level of the constraints.

### 5.2 Where in the code

Add the kicks to `rhs.vKhat`, `rhs.vA_dd` and the scalar's Pi right-hand side after
`CalcRHS` has assembled them; the Kreiss-Oliger term is additive too, so the order does not
matter (`z4c_calcrhs.cpp:620-680, 763-773`). The kicks must be off by default and must
leave runs without them bitwise unchanged.

### 5.3 The projector must use the stencil's wave number [VERIFIED by run]

On the lattice the momentum constraint is evaluated with the sixth-order first derivative
(`z4c_adm.cpp:309`). Its symbol is q(k) h = (3/2) sin kh - (3/10) sin 2kh + (1/30) sin 3kh
per component, which differs from k by 6.6 percent at k h = pi/2, the k_max of P1 (P1:512).

Check D3 (64^3 box, shells of |n| = 1 ... 16; `figs/d3_momentum.png`) measured the
relative first-order residual |M| / (|D dA| + (2/3)|D dK|) of the kick:
- with P1's projector in k: 1.2e-7 at |n| = 2, 3.7e-6 at 4, 1.8e-4 at 8, 6.9e-3 at 16, and
  4.6e-3 for the whole ball;
- with the projector in q: 1e-16 to 1e-15 for every shell.

So the kick defined with k violates the discrete momentum constraint at first order, by
up to 1e-2 relative, for the modes near k_max. P1 reports |M|/[M] "momentarily a bit
higher than second order" at the last crossings and blames the gradient resolution
(P1:541); this is a plausible cause [JUDGEMENT; testable by the L5 test of section 8; L5 ran in wave 3: the projector term of a kick defined with k equals the one-step reference within 1.2 percent, ladder JOURNAL 20].
Recommendation: q_i = q(k_i) in the projector, with k in the window and in the mode
functions. The Hamiltonian constraint involves no derivative of the kick and is
unaffected.

### 5.4 Time dependence: stage times and the mode amplitudes

With alpha_k drawn once and a smooth window, the kick is a smooth deterministic function of
time for each realisation (SPEC section 2.4). Evaluating it at the stage times keeps the
integrator's order.

The driver's RK4 evaluates its stages at t + c_s dt with c = (0, 1.193744, 0.431401,
1.000000), and the effective weights are b = (0.13586, -0.06484, 0.61832, 0.31067). The
quadrature conditions sum b c^m = 1/(m+1) hold to 1.5e-15 for m <= 3 (D4,
`figs/d4_stages_window.png`). For u' = cos t a source taken at the stage times converges as
dt^4; taken at the step start it converges as dt [VERIFIED by run]. The second stage lies
at 1.19 dt, past the end of the step. Core needs either a stage time from the driver
(t + c_s dt, computed once from the coefficients as in `ref/synth.py:lowstorage_tableau`)
or to carry the time-dependent data along as ODE variables updated by the same low-storage
recurrence.

The second option fits the noise. Under level 0 (Friedmann background) or level 1 (box
means) of the stochastic backreaction (P1:783-790), R_k(t) and Rdot_k(t) depend on k only
through |k| (or through the stencil's k^2, SPEC A2). There are at most a few thousand
distinct values for N = 256: integers |n|^2 <= 4096, or about 2.3e4 sorted component
triples. Integrate the background and these mode equations, R'' + (3 - eps2) H R' +
(k^2/a^2) R = 0 (P1:183), with the same low-storage update in the same stages, on the
host or as one small device array. Each stage then holds its own R_k, Rdot_k, W, Wdot,
Wddot at the stage time without extra bookkeeping. W and its derivatives are analytic:
SPEC section 3, `ref/synth.py:window_dt`, checked against finite differences, whose error
falls as h^2 to 2e-8 (D4).

Level 2, with local coefficients in the R equation (P1:323, 487), needs R(t, x) evolved on
the mesh and a forward transform at every stage. This design does not provide it. P1
measured its effect on the spectrum at "<~ 1e-4" relative (P1:520; SPEC section 2.3),
well below the per-mode tolerance of SPEC A2. [JUDGEMENT] Leave level 2 out of the
reproduction and list it as a known difference.

## 6. The window in a periodic box, and the noise without a Fourier library

### 6.1 The check [VERIFIED]

`grep -ril fft athenak/src` finds nothing. FFTW3 is linked only when the Kadath initial-data
library is built (`athenak/CMakeLists.txt:204-214`), on the host. cuFFT 11.3 ships with
CUDA 12.6 on this machine (`/usr/local/cuda-12.6/lib64/libcufft.so.11.3.0.4`), but nothing
in the code calls it. The turbulence driver already builds random forcing by direct sums
over a few Fourier modes, with per-axis cos and sin tables (`srcterms/turb_driver.cpp:
68-135`), which is a precedent for the method below.

### 6.2 Design [JUDGEMENT; algorithm VERIFIED by run D2]

On the periodic box the window acts on the discrete set of wave vectors
k = 2 pi n / L, 0 < |n| <= n_max, with n_max = N/4 for P1 (P1:510-512).
The real-space window is a circular convolution and is never formed. The zero mode carries
no kick: it is the background. The cut is on |n|, which keeps the noise isotropic (SPEC U5
leaves this open).

1. **Draw** once, at the start: alpha_n for each n of the half space, as a complex normal
   pair from `rng::` with stream `kStreamStochastic` = 3 (`utils/rng.hpp:55` on
   `core/rng`). The entity is the integer wave numbers (`rng.md`: "A Fourier mode: its
   integer wave numbers"), offset to non-negative integers, and the step is 0. The partner
   gets alpha_{-n} = conj(alpha_n). The amplitudes do not depend on the mesh, the
   MeshBlocks or the restart. The Python twin `python/nrpic/rng.py` reproduces them
   bitwise, so the reference in `ref/synth.py` can produce the identical noise field for
   a unit test. P1 draws white noise in real space and transforms it (P2:463). The
   statistics are the same; the realisation is not, and none of P1's realisations is
   available anyway.
2. **Coefficients** at each stage: c_n = S_R(|n|, t_s) alpha_n for the scalar field I_R,
   which gives I_K = -eps1 I_R and I_Pi = (Pi_b/H_b) I_R. The tensor fields are
   T_ij = sum_n (q_i q_j / q^2) S_R alpha_n e^(i k.x) for five components, with
   T_zz = I_R - T_xx - T_yy, and I_A_ij = eps1 (delta_ij I_R/3 - T_ij). That makes six
   real fields per stage.
3. **Synthesis**, MeshBlock by MeshBlock, by three one-dimensional sums:
   G1(nx, ny, z) = sum_nz c e^(i kz z), then G2(nx, y, z) = sum_ny G1 e^(i ky y), then
   f(x, y, z) = sum_nx G2 e^(i kx x). Each MeshBlock uses only its own cell coordinates,
   and the real part of a half-space sum is doubled. Check D2 (`figs/d2_synthesis.png`)
   compared this with numpy's inverse FFT for N = 32 and 64 and MeshBlocks of N/4, N/2
   and N cells. The difference is 9.1e-15 and 1.2e-14 of the rms, and the fields for
   different MeshBlock sizes are bitwise identical, because every cell sums the same
   terms in the same order. A refined MeshBlock evaluates the same function at its own
   cell centres, so refinement needs no prolongation of the noise. Nor does a restart,
   since everything is recomputed from the stage time.
4. **Cost** (D2, formula (N/b)^3 (M b + P b^2 + X b^3) checked exactly): 256^3 with
   n_max = 64 and the half space takes 2.5e9 complex multiply-adds per field with 128^3
   MeshBlocks (149 per cell) and 5.0e9 with 64^3 (299 per cell). A radix-2 FFT takes about
   15 per cell. Section 8 turns this into time.
5. **Fallback**: if the measured synthesis takes more than about 20 percent of a step,
   switch the card build to cuFFT on a gathered global array. This is a single-rank
   path, which the particle module requires anyway (`nrpic.cpp:20-21, 60-64`). The
   processor build would need FFTW. The synthesis should remain as the reference that the
   FFT path is tested against. [JUDGEMENT]

The SPEC asks for a GPU FFT (SPEC section 10, item 3). That request is no longer
necessary; see Requests R7.

### 6.3 Initial slice through the same synthesis [JUDGEMENT]

The coarse-grained initial data of P1:488 (SPEC section 5.3) are linear and algebraic in
Fourier space. delta phi, delta Pi, delta chi and delta K are combinations of
W(t*) R_k alpha_k and d(W R_k)/dt alpha_k, and gt_ij = delta_ij, At_ij = 0. The problem
generator can therefore build them with the same synthesis and the same alpha_n. That
guarantees "the same random lattice draw" for the data and the kicks (P1:375) and avoids
a file. The other route, writing the slice with a Python tool into the `nrpic_cosmo`
file format, also works (section 7.1) if the tool uses the twin `python/nrpic/rng.py` to
get identical alpha_n.

## 7. What is shared with Track B, and what the hand-over to particles needs

### 7.1 Shared now [JUDGEMENT unless marked]

- **Periodic Z4c.** Track B's B-pre-1 package (`periodic_z4c/` on `track/B-emd-gw`)
  verifies Z4c in periodic boxes: TT waves at four resolutions, the gauge wave, and a record
  of the lapse and shift options, including gauge shocks of the conformal-time and volume
  lapses at large amplitude (commit d92d6a7 on that branch). Track E uses those results
  for its vacuum part and does not redo them.
- **Gauge.** The geodesic slicing of section 4 is a set of input options; no shared module
  is needed during inflation. At the hand-over (7.2) the run switches to the cosmology
  lapse of `cosmo/`, again by options at a restart.
- **Initial-data file.** `nrpic_cosmo` reads `NRCOSMO1`: psi, K, alpha and Ahat_ij on the
  root mesh, conformally flat (`pgen/nrpic/nrpic_cosmo.cpp:7-20`). P2's geodesic-gauge
  data have gt_ij = delta_ij and At_ij = 0 (P2:316-329; SPEC section 5.3), so they fit
  this format exactly once two arrays, phi and Pi, are added (a format `NRCOSMO2`).
  Track B's gauge tests already write this format (`refsol.py` on `track/B-emd-gw`).
- **Constraint solve through the trace of K** (CTTK, arXiv:2207.03125; B-pre-5). For a
  scalar field, psi and At_ij are fixed and the Hamiltonian constraint is solved for K
  algebraically, cell by cell; the momentum constraint then needs a vector solve for the
  d_i K source. The two test cases do not need it. Their data satisfy both constraints to
  first order by construction (SPEC section 5.3, checked symbolically by run
  E-stoch-inf-20261115-123146-82d2fd4), and the kicks themselves add second-order
  violations at every step (P1:539). Track E needs CTTK, or the `cosmo/ic` projection with
  K given, only at the hand-over, where particles replace the field and the constraints
  must be re-solved with the particle sources. Decision 0010, item 4 puts that solve into
  the code; one implementation should serve Tracks A, B and E.
- **Diagnostics.** Track B's TT projection and Weyl scalars (`gw_diag/` on
  `track/B-emd-gw`) apply directly to the anisotropic sector of P1's section III D, with
  the double-precision fields of section 2.3. Both tracks need box means, shell spectra and
  the relative constraint measures, which should be one set of tools.

### 7.2 Field-to-particle hand-over (S11 item 3; later) [JUDGEMENT]

Once inflation ends the inflaton oscillates. With m >> H its time-averaged stress-energy
is that of dust: <S> -> 0, and E and S_i are smooth on scales well above 1/m. The
hand-over replaces the field by particles at one time slice. It needs:
1. **Additive sources** (section 2.4): field and particles active in the same run for at
   least the transition, and the constraints evaluated with both.
2. **A sampler in the code** that draws particles with the field's averaged E and
   S_i = -Pi d_i phi as rest-mass density and momentum density. It would use the
   `core/rng` stream for initial data (stream 1) and the deposit's cloud shape, so that the
   deposited sources reproduce the field's to the deposit noise, as the particle form of
   `cosmo/ic` does (`coord/notes/design_wave2_initial_data.md` section 1). The averaging
   over the oscillation period is a design choice to be specified by Track E with a
   reference (a homogeneous oscillating field against its dust limit).
3. **A gauge switch** at a restart, from alpha = 1 to the cosmology lapse; alpha is
   continuous at the switch.
4. **Checks**: E, S_i and the constraints continuous across the switch within the
   deposit noise; a homogeneous test (FLRW, field to dust) against the matter-era
   expansion of `cosmo/` (test C0 of `cosmo/TESTLOG.md`).
5. **One rank**: the particle module runs on a single rank (`nrpic.cpp:60-64`), which suits
   the single-card path of section 6.2.

## 8. Tests that would show the two cases are reproduced, and their cost

### 8.1 Ladder [JUDGEMENT; the acceptance numbers are the SPEC's A1-A7 (section 7.2), and the freezing criterion is SPEC 7.3]

| Id | Test | Pass | Size | Needs |
|---|---|---|---|---|
| L0 | Scalar field on frozen Minkowski (coupling off): plane wave, omega^2 = k^2 + m^2 | errors fall at order 6 in dx and 4 in dt | 32^3-64^3, processor | field RHS |
| L1 | Homogeneous field in FLRW, quadratic potential, alpha = 1, 13 e-folds | box means of phi, Pi, K against the Friedmann reference of SPEC run ...-122806-ef0d039 to 1e-6; order 4 in dt; H at rounding (A1, P-a) | 8^3-16^3 | Tmunu, coupling |
| L2 | Tmunu of a random small field on a fixed metric | E, S_i, S_ij equal the formulas of section 3 cell by cell to rounding | 32^3 | SetTmunu, double-precision output |
| L3 | Linear perturbations without kicks (P2's initial-value problem): all modes in at t* with the P2 data | per-mode R^NR_k / R^MS_k - 1 < 2 percent for k <= k_max/2 over 8 e-folds; H/[H] and M/[M] second order | 64^3, then 128^3 | initial data (6.3 or `NRCOSMO2`) |
| L4 | Noise fields for a fixed seed against `ref/synth.py` with `python/nrpic/rng.py` | 1e-13 of the rms; bitwise across MeshBlock layouts and through a restart (A7) | 32^3, 64^3 | 6.2 |
| L5 | Single kick on a homogeneous background, one shell | H/[H] proportional to amplitude^2; with q, the kick's own first-order M/[M] at rounding (an evolved run keeps a first-order M that is the fourth-order time error of the evolution, the same with either projector up to the projector term); negative control: flipping I_Pi gives a first-order H/[H] (P-f). Done in wave 3 (ladder JOURNAL 20-21, runs E-20261121-034645-02a463e, -040015-436a615): H factor 3.99999-4.0000001; continuum minus stencil = one-step reference within 1.2 percent; remaining first-order M 6e-7 of [M] at 64^3, Courant 0.25, divided by 15.5-19.5 when the step is halved; control 4.4e5 x proper | 64^3 | kicks |
| L6 | Temporal order, fixed seed, theta = 0.25, 0.125, 0.0625 | differences fall at order 4 with stage times (A6; D4 predicts 1 without them) | 64^3 | stage times |
| L7 | SR case: ladder N = 32, 64, 128 (k_max/dk = 8) and 256 (k_max = 64 dk) | A2 per mode, A3 freezing (SPEC 7.3), A4 constraints, A5 convergence (P-g) | up to 256^3 | all |
| L8 | USR case, 256^3 | A2 for k <= k_max/2 (looser near the end, non-linear); A3 for k <= 3 dk within 10 percent; P-h one-point statistics (outliers ~ 10) | 256^3 | all |
| L9 | Sensitivity (G2): s = 2.5, 5, 10; sigma = 0.5, 1, 2; Courant factor; resolution | spectrum shifts stated with their errors | 128^3 | all |

L0 to L6 decide whether the implementation is right before any science run; L7 and L8
reproduce the two cases. A run of L7 or L8 with one realisation can be accepted on the
per-mode criteria, which have no cosmic variance (SPEC 7.3).

### 8.2 Compute [measured inputs VERIFIED with locators; per-step model JUDGEMENT]

Inputs:
- Z4c on one A100: 2.0e7 zone-cycles/s at 128^3, nghost 4 (`docs/TESTLOG.md:46`).
- Processor: 1.45e4 to 1.54e4 zone-cycles/s per core (run ...-122727-a1c2237; Track B
  measured 1.4e4).
- Step count N_T = N sigma (Delta N)/(2 pi theta) (P1:721), with Delta N = 8 and 10
  (P1:420) and theta = 0.25 (production Courant factor of `cosmo/`, `cosmo/TESTLOG.md:18`)
  or 0.025 (P2:492; P1 states none).
- Assumptions: scalar field, Tmunu and kicks add 15 percent to Z4c; the synthesis
  sustains 3e12 flop/s with 8 flops per complex multiply-add, six fields per synthesis.
- Memory: fit to five processor runs (D1, within 1 percent each): 7 MB + 687 B per interior
  cell + 1257 B per ghost cell (the ghost cells carry the boundary buffers).

From `figs/cost.json` (run ...-123936-b2ec5c7):

| N | Case | theta | Steps | s/step (noise per step / per stage) | Card-hours (per step / per stage) | GB |
|---|---|---|---|---|---|---|
| 256 | SR | 0.25 | 1304 | 1.005 / 1.124 | 0.36 / 0.41 | 19.7 |
| 256 | USR | 0.25 | 1630 | 1.005 / 1.124 | 0.45 / 0.51 | 19.7 |
| 256 | SR | 0.025 | 13038 | | 3.6 / 4.1 | 19.7 |
| 256 | USR | 0.025 | 16297 | | 4.5 / 5.1 | 19.7 |
| 128 | either | 0.25 | 652-815 | 0.12 | 0.02-0.03 | 2.5 |
| 64 | either | 0.25 | 326-407 | 0.015 | 0.002 (processor: 1.8-2.3 core-hours) | 0.4 |

The synthesis takes 4 percent of a 256^3 step when done once per step and 14 percent when
done at every stage, the recommended choice. Memory: 256^3 with 128^3 MeshBlocks needs
about 20 GB (25 GB with 64^3), so it fits one 80 GB card. 512^3 needs 157 to 204 GB and
does not fit, so P2's 1024^3 runs (P2:492) are out of reach here. Small meshes run below
the 128^3 throughput: `cosmo/TESTLOG.md:201` reports 25 steps/s at 64^3 with particles,
6.6e6 zone-cycles/s. The 64^3 rows are therefore seconds of card time, not 0.002 hours,
and are better run on the processors.

Budget for L0 to L9 at theta = 0.25: L7 and L8 at 256^3 take about 0.9 card-hours per
pair, the N <= 128 ladder and L9 less than 0.3, and L0 to L6 run on processors or take
minutes of card time. That is about 1.5 to 2 card-hours with one rerun of each 256^3
case. At theta = 0.025 the two 256^3 runs alone take 8 to 9 card-hours, nearly all of
Track E's 10 GPU-hours to the next gate (decision 0006, `coord/DECISIONS/0006*.md:16`).
Recommendation: theta = 0.25. It satisfies P1's one-mode-per-step bound,
theta < n sigma/(2 pi) = 0.64 (P1:727), and resolves the window: about 100 steps per
e-fold at N = 256 against 0.6 e-folds for the window to rise from 0.05 to 0.95. L6 then
shows whether a smaller theta changes anything. Runs longer than an hour go through
`scripts/submit_chain.sh` and need the exact restart of section 2.3.

## 9. Interface document of `core/scalar-field`: none yet; what it must state

`git show core/scalar-field:tracks/core/interfaces/scalar_field.md` fails: the branch
stands at a9fec22 and has no interface (checked 2026-11-15 12:55 UTC). The items below
are what this review would compare against; they are filed as requests R1-R10.

1. Variables (phi, Pi with Pi = n.d phi), the sign conventions of section 3, and units
   G = 1.
2. Placement in the task list, with the dependencies of section 2.2.
3. Tmunu: scalar part separate and summed (section 2.4); the stage-wise metric source.
4. Potential interface: quadratic and Higgs-inflection forms, plus V', V''.
5. Kick hook: three right-hand sides, evaluated at stage times, off by default and bitwise
   neutral; sign-safe Pi kick; projector in q.
6. Noise: alpha_n from `core/rng` (stream 3, entity = wave numbers, half space); mode
   amplitudes per distinct |k| integrated with the same low-storage update; level 0 and
   level 1; synthesis per MeshBlock; the cut on |n|.
7. Initial data: in-code synthesis or `NRCOSMO2` (phi, Pi added).
8. Output in double precision, restart, constraint statistics outside the particle
   module with [H], [M].
9. Kreiss-Oliger coefficient of the field; refinement of phi and Pi.
10. Tests L0 to L6 in the code's test set, with this package's reference code.

## 10. The outside codes (one paragraph; not used, decision 0010)

GRChombo and GRTeclyn are not used, built or run here. Their papers document a few things
worth keeping. ISTORIz is built on GRTeclyn with RK4, sixth-order stencils, no refinement,
no constraint damping and no Kreiss-Oliger dissipation, and transforms R and dot R at every
step with AMReX's GPU FFT (P1:480-498, 512). Our design replaces that transform by the
per-mode amplitudes and the synthesis of section 6. P1 gives the step count and the
one-mode-per-step bound (P1:714-730), and P2 states its Courant factor of 0.025 and a cost
of "less than a few hours on 64 to 152 processors" for 256^3 without noise (P2:492), the
only cost figure in these papers. The scalar-matter equations of those codes are those
of section 3 under P1's opposite shift sign (P1:671). The BSSN equations printed in P1
carry the unit errors corrected in the thesis (SPEC E1, E2). The CTTK method of
arXiv:2207.03125 (Track B, section 7.1) comes from the same group and is a method, not a
code.

## 11. Requests (also in README.md)

To core (`core/scalar-field`, `core/rng`):
- R1 Scalar-field class with the layout of 2.1 and the task order of 2.2, its Tmunu formed
  from the stage's chi and gt (not from `padm`), and `Z4c_ExplRK` waiting for
  `SF_CalcRHS`.
- R2 Additive Tmunu (2.4): a scalar container summed in `CalcRHS`, `ADMConstraints` and
  the constraint statistics, so that particles and field can coexist.
- R3 Kicks on Khat, At_ij and Pi (5.1-5.2) at the stage times of RK4()4[2S] (5.4):
  I_Pi = (Pi_b/H_b) S_R, I_K = -eps1 S_R, I_A = eps1 (delta/3 - q q/q^2) S_R with q the
  sixth-order symbol (5.3). Off by default and bitwise neutral when off.
- R4 Noise without a Fourier library (6.2): alpha_n from `core/rng` stream 3 with
  entity = wave numbers (fix the encoding in `rng.md`); mode amplitudes per distinct
  |k| (or per discrete k^2) integrated in the same stages; the per-MeshBlock separable
  synthesis, checked against `tracks/E-stoch-inf/codebase/ref/synth.py`. cuFFT only as a
  measured fallback.
- R5 A stage time (t + c_s dt) available to every stage task, or the ODE-in-lockstep
  scheme of 5.4.
- R6 Double-precision output of phi, Pi and the Z4c fields; constraint statistics that do
  not depend on the particle module, with P1's [H] and [M] as an option; exact restart of
  the field and of the noise state.
- R7 For SPEC section 10 item 3: the GPU FFT requested there is not needed if R4 is
  accepted; the forward FFT at N* is replaced by the per-mode draw.
- R8 `nrpic_cosmo` file format with phi and Pi (`NRCOSMO2`), or the in-code initial slice
  of 6.3.

To Track B:
- R9 Agree on `NRCOSMO2` and on one set of box-mean, spectrum and constraint-ratio tools.
  Tell Track E when the in-code CTTK or projection solve (B-pre-5) is planned; Track E
  needs it only for the hand-over.

To the owner (E-stoch-inf):
- R10 Fix theta = 0.25 for G1 (8.2) unless L6 shows a dependence; accept level 0 or 1
  backreaction (5.4) as a stated difference from P1.

## 12. Not done here

- No AthenaK source was changed or built, and no card was used. The cost model's
  assumptions (15 percent scalar overhead, 3e12 flop/s for the synthesis) are not
  measured.
- The memory fit is host memory of the processor build. The card build's device memory
  is to be read from the first 256^3 run (`scripts/gpu_run.sh` samples it).
- The hand-over (7.2) is a list of requirements, not a specification. The averaging of
  the oscillating field into dust needs its own reference solution.
- Not compared with an interface document, because none exists yet (section 9).
