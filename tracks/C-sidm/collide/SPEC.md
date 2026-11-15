# SPEC: relativistic Monte Carlo collision operator in the NRPIC particle module

Package `collide` of C-sidm (C-pre-1 under decision 0010). The operator is written into
`athenak/src/particles/` by core on branch `core/collisions`, on top of the random numbers
of `core/rng`; this file is the specification it is checked against. Reference solutions:
`REFERENCES/`; tests with pass criteria: `TESTS.md`; random numbers:
`RNG_REQUIREMENTS.md`. Labels: [VERIFIED] read at the source (locator given),
[BACKGROUND] standard result not re-read, [JUDGEMENT] design choice or own derivation
(derivations are checked numerically where a script is named), [TO VERIFY] open.

## 0. What the operator does, in one paragraph

Once per time step, after the particles have been pushed and handed to the MeshBlock that
owns them, the particles of every mesh cell are paired at random; each pair collides with
a probability proportional to the cross-section per unit mass, the Moller relative speed of
the pair, the proper time of the step and the inverse proper volume of the cell; a pair
that collides is scattered isotropically and elastically in its centre-of-momentum frame,
which conserves the pair's four-momentum to rounding. Everything is evaluated in the
orthonormal frame of the normal observer at the cell centre. The scheme is Bird-type direct
simulation Monte Carlo with Nanbu/Takizuka-Abe random pairing [BACKGROUND], made
Lorentz-invariant by the Moller speed; Koda & Shapiro use the same pair probability in the
Newtonian limit (arXiv:1101.3097, `sidm1.tex` lines 561-574, pairs scattered together for
conservation lines 586-596) [VERIFIED].

## 1. Notation and units

- G = c = k_B = 1 (code units). One physical species of particle mass m (its value never
  enters: see 4.3). theta = T/m, zeta = 1/theta.
- Macroparticle i: rest mass M_i (`IPM`), covariant spatial four-velocity u_i (`IPVX..Z`,
  per unit rest mass), tag (`PTAG`, unique), weight w_i = M_i/m (number of physical
  particles it stands for). Null particles (M = 0) and light rays (M < 0) never collide.
- sigma_m: cross-section per unit mass of the physical particles, sigma_tot = sigma_m m,
  velocity independent, isotropic in the centre-of-momentum (CM) frame. In code units
  sigma_m has the dimension of an inverse surface density, i.e. length^2/mass = length
  (G = c = 1). Conversion from cm^2/g: sigma_m [code] = sigma_m [cm^2/g] x M_unit [g] /
  L_unit^2 [cm^2], with the code's mass and length units (C-pre-4 fixes them).
- Rest-frame quantities of a gas: number density n, rest-mass density rho_0 = n m, mean
  free path lambda = 1/(rho_0 sigma_m) = 1/(n sigma_tot) (the definition of Balberg,
  Shapiro & Inagaki, `SIDMGT_Xiv2.tex` line 389, and Koda & Shapiro line 409 [VERIFIED];
  the hard-sphere mean free path of a Maxwellian gas is lambda/sqrt 2, line 392).
- Knudsen number of a cluster run (track definition, `stage/G0/REPORT.md` decision 2;
  written here in wave 2 after the verifier's finding V5): Kn_c = lambda_c/H_c with
  lambda_c = 1/(rho_0c sigma_m) at the centre and H_c = (v1_c^2/(4 pi rho_0c))^{1/2},
  v1^2 = p/rho_0 (one-dimensional dispersion), rho_0 the rest-mass density. Then
  sigma_m = K/Kn_c in code units (M_ADM = 1) with K = 1/(rho_0c H_c), a property of the
  equilibrium: K = 168.9 for the King b = 1 threshold model (y0 = 0.334032; run
  C-sidm-20261115-131130-3077a99), 142.6 for the F21 b = 0.1 model at the eps maximum and
  84.1 at the trial root (verifier, run C-20261115-170630-1037f6a); table for all models in
  `../equilibria/CONVERSION.md`. Other conventions met in the packages and the literature
  (H on the energy density, scope: factor 1.18; transport mean free path, equilibria: 0.77;
  lambda/R, gravothermal) are not used to label runs.
- Moller speed of two particles a, b with four-velocities u_a, u_b in any frame:
  gamma_rel = -u_a . u_b = W_a W_b - u_a . u_b (spatial dot), W = sqrt(1 + |u|^2),
      v_Mol = sqrt(gamma_rel^2 - 1) / (W_a W_b),     0 <= v_Mol < 2.
  The number of collisions per unit four-volume between two streams of rest densities
  n_a, n_b is n_a n_b sigma_tot sqrt(gamma_rel^2 - 1) [BACKGROUND], a scalar; in a frame
  where the densities are n_a W_a and n_b W_b it reads (n_a W_a)(n_b W_b) sigma_tot v_Mol.

## 2. Collision rate of a Maxwell-Juttner gas (reference for test T2)

Per-particle rate in the rest frame, constant sigma_tot:
    Gamma = n sigma_tot <v_Mol> = rho_0 sigma_m <v_Mol>,
    <v_Mol>(theta) = 4 K3(2 zeta) / (zeta K2(zeta)^2).                         (R)
Derivation [JUDGEMENT, own; checked]: the thermal average of sigma v_Mol over two
Maxwell-Juttner distributions reduces to one integral over the invariant mass s,
<sigma v_Mol> = [8 m^4 T K2(zeta)^2]^-1 int_{4m^2}^inf sigma (s - 4m^2) sqrt(s)
K1(sqrt(s)/T) ds (Gondolo & Gelmini 1991, Nucl. Phys. B 360, 145 [BACKGROUND, not
re-read]). With x = sqrt(s)/T and constant sigma,
<v_Mol> = [4 zeta^4 K2^2]^-1 int_{2 zeta}^inf (x^4 - 4 zeta^2 x^2) K1(x) dx; using
d(x^nu K_nu)/dx = -x^nu K_{nu-1}: int_a^inf x^2 K1 = a^2 K2(a) and int_a^inf x^4 K1 =
a^4 K2(a) + 2 a^3 K3(a), so the integral is 16 zeta^3 K3(2 zeta), which gives (R).
Checks (`REFERENCES/rate.py`, `tests/test_rate.py`, run C-sidm-20261115-120703-9b3e868):
(R) agrees with a Monte Carlo average of v_Mol over 1e6 independently sampled pairs within
-1.3..+1.0 standard errors from theta = 1e-3 to 100, and with the one-dimensional integral
by quadrature to 1e-10; this Monte Carlo check does not use the Gondolo-Gelmini form.
Limits: theta -> 0: <v_Mol> = sqrt(16 theta/pi) (1 - 25 theta/16 + ...), i.e.
Gamma = a rho sigma_m v with a = sqrt(16/pi) and v = sqrt(T/m), the hard-sphere constant
of Balberg et al. (`SIDMGT_Xiv2.tex` lines 309-323) [VERIFIED]; theta -> inf: <v_Mol> -> 1.
Number of collision events per volume and time: n^2 sigma_tot <v_Mol>/2.
In a frame where the gas drifts with Lorentz factor Gamma_b, the number of collisions per
particle per unit frame time is Gamma/Gamma_b (time dilation; densities and v_Mol
transform so that the product per four-volume is invariant) [JUDGEMENT; test T11].

## 3. Kinematics of one pair (reference: `REFERENCES/kinematics.py`)

Input: u_a, u_b in an orthonormal frame; physical masses m_a, m_b (equal for one
species; set both to 1); a unit vector nhat. Output: u_a', u_b'.

1. g1 = gamma_rel - 1 without cancellation (the naive W_a W_b - u_a.u_b - 1 loses
   eps W^2/g1 relative). With D = u_a - u_b, S = u_a + u_b, e = S/|S|, D_par = (D.e)^2,
   D_perp = |D x e|^2, A = (W_a + W_b)^2, r = D_par/A:
   - if r <= 1/2: g1 = (D_perp + 4 r) / (2 (1 - r))   [exact identity from
     2 g1 = |D|^2 - (W_a - W_b)^2, W_a - W_b = D.S/(W_a + W_b), A - |S|^2 = 2(g1 + 2);
     at S = 0 use g1 = |D|^2/2];
   - else: g1 = S_h^2/(sqrt(1 + S_h^2) + 1) + a b (1 - cos psi), a = |u_a|, b = |u_b|,
     S_h = (a - b)(a + b)/(a W_b + b W_a) (= sinh of the rapidity difference),
     1 - cos psi = |u_a/a - u_b/b|^2 / 2. For r > 1/2, |D|^2 > 2 + (a + b)^2/2, so either
     a/b is outside [0.17, 5.8] or the angle term dominates: no cancellation.
   [JUDGEMENT, own derivation.] The first version, which used only the second form for
   all pairs, failed prediction R2 (errors up to 3.4e-13 of |u| and 1e-8 relative in g1
   for pairs with bulk Lorentz factor ~1e4; `JOURNAL.md`, `figs/ref_kinematics.png`).
2. s = (m_a + m_b)^2 + 2 m_a m_b g1; |p*| = m_a m_b sqrt(g1 (g1 + 2)) / sqrt(s);
   E_a* = sqrt(m_a^2 + |p*|^2).
3. CM direction: p_a*' = |p*| nhat, where nhat is given in the axes of the CM frame reached
   from the cell frame by the pure boost with velocity P/E (P = m_a u_a + m_b u_b,
   E = m_a W_a + m_b W_b); no rotation. nhat is the `rng::Direction` draw of the pair
   (`RNG_REQUIREMENTS.md`).
4. Boost back without dividing by |beta|:
   p_a' = p_a*' + P [ (p_a*' . P) / (sqrt(s) (E + sqrt(s))) + E_a*/sqrt(s) ],
   p_b' = P - p_a' (momentum exact by construction), u' = p'/m.
Properties (tests/test_kinematics.py, run above): agreement with a 60-digit evaluation of
the textbook formulas to 1.1e-15 of max(1, |u|) over 2e4 pairs spanning theta 1e-8..1e6
and bulk Lorentz factors 1..1e4; pair four-momentum conserved to 0.7 eps (momentum) and
2.6 eps (energy) of the pair energy; for equal masses the direction average of the
post-collision energy of either particle is (E_a + E_b)/2 exactly (since
<beta . p*'> = 0), which makes the two-temperature reference of section 6 exact.
Test vectors for the kernel of the code: `kinematics.make_test_vectors` (JSON, inputs as
exact hexadecimal doubles, outputs from the 60-digit evaluation; TESTS.md T0).

## 4. The operator on the mesh

### 4.1 Collision cell, proper volume, proper time
- Collision cell = one cell of the MeshBlock that owns the particle (at that block's
  refinement level). Option to coarsen: `coll_cell_factor` f in {1, 2, 4}: blocks of f^3
  cells form one collision cell (for low particle numbers per cell). [JUDGEMENT]
- Proper volume of the cell: V = sqrt(gamma) dx dy dz with gamma = det(gamma_ij) at the
  cell centre; proper time of the step: d_tau = alpha dt with alpha at the cell centre.
  Metric: the one the pusher uses at the end of the step (`met1`), at the cell centre, not
  interpolated per particle; with an analytic metric (`kerr_schild` etc.) its value at the
  cell centre. The same metric serves both particles of every pair of the cell.

### 4.2 Pairing (per cell, per collision sub-step)
1. N = number of colliding macroparticles in the cell (M > 0, not flagged for removal).
   N < 2: nothing happens.
2. Each particle gets a random 64-bit key from (seed, step, sub-step, tag)
   (`RNG_REQUIREMENTS.md` K1); sort the cell's particles by (key, tag); pair positions
   (0,1), (2,3), ...
3. Odd N: the first three particles of the sorted list form the pairs (0,1), (1,2), (2,0),
   each tested with half the probability of 4.3, in this order, each using the momenta as
   updated by the previous pair; the rest are paired as above from position 3.
   [BACKGROUND: Takizuka & Abe 1977 / Nanbu 1997 treatment of odd numbers, not re-read;
   the half weight keeps the expected number of collisions of each of the three particles
   equal to that of a particle in a regular pair.]

### 4.3 Collision probability and acceptance
For a tested pair (i, j) of the cell:
    P_ij = (N - 1) sigma_m M_max v_Mol,ij alpha dt / (sqrt(gamma) dx dy dz)       (P)
with M_max = max(M_i, M_j) (= M for equal masses) and v_Mol from the triad components
(section 5) [JUDGEMENT; reduces to Koda & Shapiro's P_0j with a top-hat kernel of one cell
and to the Moller-invariant rate of section 1]. Accept if U < P_ij, U the pair's uniform
deviate (`RNG_REQUIREMENTS.md` K2); accepted pairs are scattered (section 3) with
m_a = m_b = 1. Why (N - 1): each particle is tested against one partner per sub-step, but
must collide at the rate sum_{j != i} w_j sigma_tot v_Mol / V; drawing the partner uniformly
among the other N - 1 and multiplying by N - 1 gives that rate in expectation. The physical
mass m drops out: w sigma_tot = M sigma_m.
Bias from the cell population [JUDGEMENT]: the realized rate per particle is
(N - 1) w sigma_tot <v>/V, i.e. n sigma_tot <v> (1 - 1/N) when exactly N particles sit in
the cell; for positions drawn as a Poisson process E[N(N - 1)] = <N>^2, so the cell-summed
rate is unbiased; lattice ("quiet") starts are biased low by 1/N. Test boxes therefore
place particles as a Poisson process (`analysis/make_box.py`).

### 4.4 Unequal macroparticle masses
Statement [JUDGEMENT, own argument; TO VERIFY against the weighted-collision literature]:
for M_i != M_j no update of the pair alone that (a) conserves the pair's four-momentum
exactly and (b) keeps both on their mass shells can also give the correct equilibrium.
(a) and (b) leave only a rotation of the relative momentum in the CM frame of the two
macroparticles (two-body kinematics with masses M_i, M_j); such collisions conserve
sum M W and drive the macroparticles to a common temperature per macroparticle,
exp(-M W/T), so heavy macroparticles end up with a velocity dispersion smaller by
sqrt(M_light/M_heavy) in the non-relativistic limit, whereas all physical particles must
share one Maxwell-Juttner velocity distribution. Absorbing the energy excess into the
rest mass of the heavy macroparticle (the other exact option) converts kinetic energy
into rest mass at every collision and cools the gas.
Hence:
- Default and required for production runs: equal masses of all colliding
  macroparticles. Pairs with |M_i - M_j| <= 1e-12 max(M_i, M_j) are scattered exactly
  (section 3). C-pre-4 samples equal-mass particles.
- Option `coll_weights = nanbu` (not for production): Nanbu-Yonemura rule [BACKGROUND:
  Nanbu & Yonemura 1998, J. Comput. Phys. 145, 639, not re-read]: probability (P) with
  M_max; on acceptance the physical pair is scattered (m_a = m_b = 1) and the lighter
  macroparticle always adopts its post-collision u, the heavier one only if U2 < M_min/M_max
  (second uniform of the pair). Four-momentum is conserved in expectation, not per pair;
  the code accumulates the non-conserved sum_pairs (Delta P^mu) of every step and reports
  it (4.7). Each macroparticle's velocity distribution relaxes to the same Maxwell-Juttner
  distribution (each update is a physical scattering of a physical particle).
- With `coll_weights = equal` (default) a cell holding unequal masses is a fatal error,
  not a silent fallback.

### 4.5 Time step and sub-cycling
- P_max = max over tested pairs of P_ij must stay below `coll_pmax` (default 0.1, the
  bound Koda & Shapiro use, `sidm1.tex` lines 667-673 [VERIFIED]). The operator does not
  shrink the global step; it sub-cycles: per cell, n_sub = ceil(P_bound / coll_pmax) with
  P_bound = (N - 1) sigma_m M_max v_bound alpha dt / V, v_bound = min(v_1 + v_2, 2) with
  v_1, v_2 the two largest speeds of the cell's particles in its frame (core's `measured`
  rule, `coord/INTERFACES/collisions.md` lines 178-183; adopted in wave 2 at core's request:
  the first-pairing rule of the first version of this text made n_sub depend on one pairing
  and biased the rate by -0.10 to -0.12 percent, run core-20261115-132842-b33b7f3), or 2
  (the absolute bound) if `coll_subcycle = conservative`; each sub-step re-pairs (new
  keys) with dt/n_sub. The box tests of wave 2 ran with this rule (T2 rate within 1e-4,
  `../box_tests/README.md`).
  n_sub is capped by `coll_nsub_max` (default 1000); a pair with P > 1 after the cap is
  counted (`n_truncated`), clipped to 1, and is a test failure in every test of TESTS.md.
- Short-mean-free-path regime: n_sub ~ dt Gamma / 0.1 sub-steps per step; the cost is
  local (no communication). This is the stiffness named in the brief's risks; the operator
  stays explicit by design [JUDGEMENT].

### 4.6 Cell size
- Particles more than a mean free path apart must not collide: dx <~ lambda (Koda &
  Shapiro, `sidm1.tex` lines 680-692 [VERIFIED] for their neighbour radius); DSMC
  practice dx <~ lambda/3 [BACKGROUND, Bird 1994, not re-read]; transport coefficients
  converge as (dx/lambda)^2 [BACKGROUND: Alexander, Garcia & Alder 1998; TO VERIFY].
  The operator does not enforce it; it reports max over cells of dx_proper/lambda_cell
  with lambda_cell = V/(N M sigma_m) (4.7), and the short-mean-free-path tests set
  dx <= lambda/4 and check convergence in dx.
- At least ~10 to 20 macroparticles per collision cell in collisional regions
  [BACKGROUND]; reported as the minimum and mean N over cells with N >= 1.

### 4.7 Placement in the step, restarts, outputs
- Task order: push -> particle exchange between MeshBlocks/ranks -> excision -> COLLIDE ->
  deposit -> diagnostics. Collisions see the positions and momenta at t^{n+1} and the
  metric at t^{n+1}; first-order (Lie) splitting [JUDGEMENT; the stochastic operator is
  first order in dt anyway; convergence in dt is a test].
- Excised and escaped particles never collide; particles that collide in a step are not
  re-pushed.
- Restart: nothing to store beyond the cycle number and `<job> rng_seed` (both exist);
  the collision step after a restart must reproduce the uninterrupted run bit for bit
  (TESTS.md T10).
- Outputs (new history file `<base>.coll.hst`, one record every `hist_dcycle`):
  time, cycle, n_cells_with_pairs, n_pairs_tested, sum_P (expected collisions given the
  configuration), n_collisions (accepted), n_truncated, max_P, max_nsub, mean_nsub,
  min_N, mean_N (cells with N >= 1), max dx/lambda_cell, sum M W and sum M u_i over
  colliding particles before and after the collision step (relative change), and for
  `nanbu` the accumulated sum Delta P^mu. A debug option `coll_dump_cycle = c` writes the
  particle state (x, u, M, tag, cell index, n_sub of its cell) immediately before and
  after the collision step of cycle c (for the replay test T0b).

### 4.8 Options (proposal; core defines the final names in
`tracks/core/interfaces/collisions.md`)

| `<particles>` option | default | meaning |
|---|---|---|
| `collisions` | false | switch the operator on |
| `coll_sigma` | 0 | sigma_m, cross-section per unit mass, code units |
| `coll_pmax` | 0.1 | largest pair probability per sub-step |
| `coll_subcycle` | `measured` | `measured` or `conservative` (v_bound = 2) |
| `coll_nsub_max` | 1000 | cap of sub-steps per cell and step |
| `coll_cell_factor` | 1 | collision cell = f^3 mesh cells |
| `coll_weights` | `equal` | `equal` (fatal on unequal masses) or `nanbu` |
| `coll_dump_cycle` | -1 | dump before/after the collision step of this cycle |
| `<job> rng_seed` | 0 | seed (core/rng) |

## 5. Curved spacetime: what is evaluated where

- Frame: the normal observer n at the cell centre; its orthonormal spatial triad from the
  Cholesky factor of the cell's gamma_ij = (L L^T)_ij (L lower triangular, positive
  diagonal). Triad components u_hat = L^-1 u (solve; u = covariant u_i), back u = L u_hat;
  gamma^ij u_i u_j = |u_hat|^2. Energies W = alpha u^0 = sqrt(1 + |u_hat|^2) are those
  the normal observer measures. The scattering of section 3 is done on u_hat.
  `kinematics.scatter_metric` is the reference (test: covariant momentum and
  W = sqrt(1 + gamma^ij u_i u_j) conserved to rounding for a random gamma_ij).
- Conserved exactly (to rounding) per pair: sum M u_i (covariant components, coordinate
  basis, because L is linear and common to the pair) and sum M W with the cell's metric.
  Not exactly conserved: sum M W evaluated with each particle's interpolated metric at
  its own position; the difference is O(|Delta u| dx d gamma) per collision with random
  sign [JUDGEMENT]; reported by the conservation diagnostics already in the code.
- Rate: proper time alpha dt and proper volume sqrt(gamma) dV of the normal observer in
  (P); v_Mol from the triad components. The product (sigma v_Mol)(d_tau)/V counts
  collisions per proper four-volume alpha sqrt(gamma) d^4x, a scalar (section 1), so the
  choice of the normal observer affects only the O(dx) smearing of a macroparticle over
  its cell [JUDGEMENT].
- Shift: does not enter (the normal observer's frame is defined by n alone).
- Refinement: each cell at its own level; no collisions across blocks or levels (a
  particle collides only with the particles of its own cell).
- Horizon and excision: particles inside the excision region are removed before the
  collision step; no special treatment otherwise.

## 6. Relaxation of a two-temperature start (reference: `REFERENCES/relax.py`)

Two populations of the same species, rest-frame number densities n1, n2, Maxwell-Juttner
at theta1, theta2, uniform. Exact initial rate (equal masses, isotropic scattering):
    d e_1/dt = n1 n2 sigma_tot < v_Mol (E_2 - E_1)/2 >_{MJ1 x MJ2}
because the direction average of E_1' is (E_1 + E_2)/2 (section 3) and only collisions
between the populations change e_1. Non-relativistic closed form [JUDGEMENT, own
derivation; checked by Monte Carlo collision integrals, run C-sidm-20261115-120703-9b3e868]:
with v1 = V + g/2, v2 = V - g/2, <Delta E_1>_dir = -(m/2) V.g; for Maxwellians
Cov(V_k, g_k) = (T1 - T2)/(2m), Var(g_k) = (T1 + T2)/m, so <|g| V.g> =
[(T1 - T2)/(2(T1 + T2))] <|g|^3> with <|g|^3> = 8 sqrt(2/pi) ((T1 + T2)/m)^{3/2}:
    d(T1 - T2)/dt = -(4/3) sqrt(2/pi) (n1 + n2) sigma_tot sqrt((T1 + T2)/m) (T1 - T2),
valid at t = 0 for any ratio T1/T2. For n1 = n2 and T1 ~ T2 = T its rate is (2/3) of the
collision rate sqrt(16/pi) n sigma_tot sqrt(T/m). Relativistically the exact initial rate
(quadrature over |u_1|, |u_2| with the angular integral in closed form) falls below this
form: 0.995, 0.81, 0.16, 0.027 of it at theta_2 = 1e-3, 0.053, 2.8, 100 (theta_1 =
2 theta_2; run above, `figs/ref_relax.png`). Final state: Maxwell-Juttner at theta_eq with
n1 <W>(theta1) + n2 <W>(theta2) = (n1 + n2) <W>(theta_eq) (exact). The populations leave
the Maxwell-Juttner form during relaxation, so only the initial slope and the end state
are pass criteria; `relax.two_mj_model` is a guide for run lengths.

## 7. Heat conduction (reference: `REFERENCES/conduction.py`)

### 7.1 One-sided fluxes (long mean free path, two half-space reservoirs)
For a Maxwell-Juttner gas (n, theta) the number and energy fluxes through a plane from one
side are [JUDGEMENT, own derivation, checked against quadrature to 1e-9]
    Phi_N = n theta (1 + theta) e^-zeta / (2 K2(zeta)),
    Phi_E = n m theta (1 + 3 theta + 3 theta^2) e^-zeta / (2 K2(zeta)),
from Phi = pi int p^3/E f dp (number) and pi int p^3 f dp (energy) with p dp = E dE.
Limits: Phi_N -> n sqrt(T/(2 pi m)) and n c/4; Phi_E - m Phi_N -> 2 T Phi_N (non-
relativistic) and Phi_E -> 3 n T c/4 = e c/4. Between two collisionless half-space
reservoirs the net fluxes are Phi(1) - Phi(2), independent of their distance.

### 7.2 The step in a periodic box (test T6)
Left slab [0, L/2) at (n1, theta1), right slab at (n2, theta2), equal pressure
n1 theta1 = n2 theta2. Collisionless, exact for all times: each particle moves on
x + v_x t (mod L); the slab content follows from the direction average of the periodic
triangle function, <tri(v t mu)>_mu = G(v t)/(v t), G(c) = floor(c/L) L^2/4 + G0(c mod L),
G0(r) = r^2/2 (r <= L/2), L^2/4 - (L - r)^2/2 (r > L/2); then a one-dimensional
quadrature over |u| (`step_collisionless`). Initial slope: -2 (Phi(1) - Phi(2)) (two
interfaces). Short mean free path, linear in the contrast: each odd Fourier mode j of the
square wave decays as exp(-chi (j k_1)^2 t), k_1 = 2 pi/L (`step_diffusive`).

### 7.3 Isobaric mode and the conductivity (test T7)
Linear isobaric perturbation T = T0(1 + eps cos kx), n = n0(1 - eps cos kx). With Eckart's
heat flux q = -kappa (grad T + T a) (form used by arXiv:2601.17117, `SIDM_MS.tex` line 271
[VERIFIED]) and a = 0 at leading order, energy and particle conservation at constant
pressure give n (c_v + 1) d(delta T)/dt = kappa lap(delta T) (the enthalpy h = e/n + T
enters through e/n - h = -T), so
    Gamma_k = kappa k^2 / (n c_p),     c_p = c_v + 1 (per particle, Maxwell-Juttner),
to leading order in k lambda, relativistically [JUDGEMENT, own derivation].
Non-relativistic Chapman-Enskog conductivity of hard spheres, first approximation:
    kappa_1 = (75 sqrt(pi)/64) k_B sqrt(T/m) / sigma_tot = 2.077 sqrt(theta)/sigma_tot,
i.e. q = -(3/2) b (v/sigma_m) d v^2/dx with b = 25 sqrt(pi)/32 = 1.385 as in Koda &
Shapiro (`sidm1.tex` lines 402-417) and arXiv:2601.17117 (`SIDM_MS.tex` line 233, citing
Chapman & Cowling) [VERIFIED], and kappa_smfp ~ 2.1 v k_B/sigma in arXiv:2010.15132
(`smbh.tex` line 116) [VERIFIED]. Balberg et al. print b ~ 25 pi/(32 sqrt 6) = 1.002 for
the same flux law (`SIDMGT_Xiv2.tex` line 394) [VERIFIED], i.e. a conductivity smaller by
sqrt(6/pi) = 1.38; Koda & Shapiro's footnote (`sidm1.tex` lines 411-412) quotes the BSI
value as 25 sqrt(pi)/(32 sqrt 6) and "should be 25 pi/32", which matches neither
formula in either text [VERIFIED that the text says so]. The independent check of the
coefficient is T7, which measures kappa. Higher Sonine approximations raise the
hard-sphere kappa by about 2.5 percent [BACKGROUND, TO VERIFY]. Relativistic
conductivity of hard spheres: not in the sources read; arXiv:2601.17117 uses the
non-relativistic constants in its relativistic model (line 233) [VERIFIED]; T7 at
theta = 0.1 and 1 measures it (a result in its own right for S3) [TO VERIFY against
Cercignani & Kremer's relativistic Chapman-Enskog values, request to kb].
Collisionless limit of the mode (phase mixing): `mode_collisionless`.

## 8. Entropy (reference: `REFERENCES/entropy.py`, test T5)
s = -(1/n) int f ln f d^3u per particle. Maxwell-Juttner: s = zeta (<W> - 1) +
ln(4 pi K2(zeta) e^zeta/(zeta n)) (Sackur-Tetrode for theta -> 0, checked). Estimator:
radial histogram (isotropic distributions only), bins uniform in s = sqrt(zeta (W - 1)),
Miller-Madow correction; unbiased within 4 standard errors at 1e6 samples
(-0.5..+1.7 standard errors from theta = 1e-3 to 10). Entropy gap to be resolved by T5:
0.045 (theta_2 = 1e-3) to 0.123 (theta_2 = 1) per particle for theta_1 = 3 theta_2.

## 9. Cross-checks named by the brief

- arXiv:2602.17487, named by the brief (lines 520 and 852) as the continuum relativistic
  kinetic solver for cross-validation, is a collisionless discontinuous-Galerkin
  Vlasov-Maxwell solver: `results.tex` line 18 ("in the absence of collisions or
  sources"), `intro.tex` line 9 (C[f] only named) [VERIFIED]. It has no collision
  operator and cannot cross-check relaxation, rate or conduction. Correction proposed to
  the owner (README, Requests). Candidates to look for: relativistic lattice Boltzmann
  (Ambrus et al., cited there as "Ambrus:2022") and the collisional Boltzmann treatment
  of SIDM cited by 2601.17117 as "Gurian:2025zpc" (line 672) [TO VERIFY].

## 10. Sources read for this specification
arXiv:1101.3097 (Koda & Shapiro), astro-ph/0110561 (Balberg, Shapiro & Inagaki),
arXiv:2601.17117, arXiv:2010.15132, arXiv:2602.17487 (sections named above); from
`kb-data/raw/arxiv/<id>/<version>/src`. astro-ph/0111176, arXiv:2108.11967 and
arXiv:2506.17641 were fetched and scanned: they hold no collision-operator content
(instability criteria and seeding; they matter for C-pre-3 and C-pre-4).
