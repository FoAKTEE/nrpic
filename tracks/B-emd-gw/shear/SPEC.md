# SPEC: the shearing-dust test of arXiv:2003.08014 with AthenaK particles

Package `shear` of owner B-emd-gw, wave 3 round 1 (2026-11-20). G2 multi-code row of
Track B as ruled by decision 0013 (`coord/DECISIONS/0013-gate-rulings-after-wave-1.md`):
the comparison with gevolution of the brief is replaced by the shearing-dust comparison
of Adamek, Barrera-Hinojosa, Bruni, Li, Macpherson, Mertens, "Numerical solutions to
Einstein's equations in a shearing-dust Universe: a code comparison" (arXiv:2003.08014
v2), in which gevolution, GRAMSES, the Einstein Toolkit (ET, fluid) and CosmoGRaPH
(particles) were compared on one exact-perturbation slice.

Source: `/data/haiyangw/nrpic/kb-data/raw/arxiv/2003.08014/v2/src/draft.tex` (untracked,
never committed; locators `draft.tex:<line>`). Labels: [VERIFIED] read in the source or
checked by a test or run named; [BACKGROUND] standard result; [JUDGEMENT] my inference;
[TO VERIFY] open.

## 1. Set-up of the paper

Initial slice t = t_* (draft.tex:136-158), with c = cos(2 pi y/L), s = sin(2 pi y/L):

    alpha_* = 1,  beta_* = 0,
    gamma*_ij = [[1, (b/(H L)) c, 0], [(b/(H L)) c, 1 + (b/(H L))^2 c^2, 0], [0, 0, 1]],
    K*_ij = -[[H, (b/(4L)) c, 0], [(b/(4L)) c, H - (b^2/(2 H L^2)) c^2, 0], [0, 0, H]],

H = H_* the Hubble rate of the reference Einstein-de Sitter model, L the period in y (the
data are periodic, draft.tex:160), b a dimensionless amplitude. Sign convention: K = -3H
for an expanding slice (draft.tex:495), i.e. K_ij = -(1/(2 alpha)) d_t gamma_ij, as in
the code (`nrpic_cosmo.cpp`: `id = flrw` has K = -3 hubble) [VERIFIED].
Dust T^{mu nu} = rho_0 u^mu u^nu (draft.tex:165); the constraints (draft.tex:171-172)
give (draft.tex:177-182), with Q = 16 H^2 L^2 - 3 b^2 c^2 and R = Q^2 - 64 pi^2 b^2 s^2,

    rho0* = 3 R / (128 pi G L^2 Q),    u*^x = -8 pi b s / sqrt(R),    u*^y = u*^z = 0,
    W* = alpha u^0 = Q / sqrt(R)   (draft.tex:520),
    rho_ADM* = 3 H^2/(8 pi G) - 9 b^2 c^2/(128 pi G L^2)   (draft.tex:515).

Physical range: b < 2 H^2 L^2 / pi (weak energy condition), and for H L > pi sqrt(2/3)
b < 4 sqrt(3 H^2 L^2 - pi^2)/3 (draft.tex:184).

Runs of the paper (draft.tex:287): H L = 2^n, n = -7 ... 2, and b = {0.5, 0.05, 0.005}
H^2 L^2, 30 runs per code. Grids: gevolution N = 96 (64, 48 for convergence;
draft.tex:302); GRAMSES 256^3 (draft.tex:312); ET N = 64, 80, 96 (draft.tex:321);
CosmoGRaPH N_x = N_z = 1, N_y = 64, 96, 128 with N_p = N_y^2/8 particles
(draft.tex:328). ET and CosmoGRaPH values are Richardson-extrapolated (draft.tex:343).

Below: b = beta H^2 L^2, beta in {0.005, 0.05, 0.5}; code units G = c = 1, H_* = 1, so
L = H L in numbers, t_* = 2 / H_* = 2 in conformal time, and the code's clock t_c = t - t_*
(cosmo/README.md: a = (1 + t_c/2)^2).

## 2. The slice in the code's conformally flat form (psi = 1)

The code's `nrpic_cosmo` with `id = file` takes psi, K, alpha and Ahat_ij on the cells and
sets gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K, beta = 0
(`athenak/src/pgen/nrpic/nrpic_cosmo.cpp` lines 7-19 and 196-207) [VERIFIED].

Coordinate change, time independent: x' = x + F(y), y' = y, z' = z with
F(y) = (b/(2 pi H)) sin(2 pi y/L), F' = (b/(H L)) c. Then
dx'^2 + dy^2 + dz^2 = dx^2 + 2F' dx dy + (1 + F'^2) dy^2 + dz^2 = gamma*_ij dx^i dx^j:
the slice is Euclidean in sheared coordinates (draft.tex:160 says so) and psi = 1.
With x = x' - F(y'), the tensor law gives (derivation; [VERIFIED] symbolically by
`tests/test_ref.py::test_sheared_slice_symbolic`):

    gamma'_ij = delta_ij,
    K'_ij = -H delta_ij + (3b/(4L)) c (delta_ix delta_jy + delta_iy delta_jx),
    K' = -3H (constant: also a CMC slice),   Ahat'_xy = (3b/(4L)) c, other Ahat' = 0,
    u'^x = u*^x,  u'_x = u*^x,  u'_y = u'_z = 0,   rho0, W unchanged (scalars),
    sqrt(gamma') = sqrt(gamma*) = 1 and the Jacobian is 1, so the rest-mass density per
    coordinate volume D = sqrt(gamma) rho0 W = 3 sqrt(R) / (128 pi L^2) is unchanged.

Constraints in the primed form: Hamiltonian K^2 - K_ij K^ij = 6H^2 - (9 b^2/(8L^2)) c^2 =
16 pi rho_ADM; momentum d_y K'^{xy} = -(3 pi b/(2 L^2)) s = 8 pi rho0 W u^x. Both hold
identically (test above). Periodicity: F(y + L) = F(y), and x -> x + L maps to x' -> x' + L,
so the torus [0, L)^3 is the same torus; all fields still depend on y only.
The events of the observable keep their coordinates: F(0) = F(-L) = 0, so O = (0, 0, 0),
A = (-L, 0, 0), B = (0, -L, 0) also in the primed coordinates; A and B are periodic images
of O. [JUDGEMENT] The planner's key observation holds.

Side remarks [JUDGEMENT, from the same algebra]: on the initial slice the primed
coordinates are the Poisson-gauge spatial coordinates of the paper at t = t_*
(draft.tex:198 at t = t_*), but the evolution here keeps zero shift (the Poisson gauge
carries B_i). The BSSN Abar*_ij printed at draft.tex:499-503 carries an overall factor 3
that does not follow from lines 149-158 and K = -3H (A*_xy = 3b/(4L) c,
A*_yy = 3 b^2 c^2/(2 H L^2) from the definitions; Gamma-bar and rho_ADM of lines 507-515
do follow); this does not enter here.

## 3. Slicing

- Paper: ET and CosmoGRaPH evolve "with a harmonic lapse condition and zero shift"
  (draft.tex:321, 328); its linear solution "for a harmonic slicing" (draft.tex:235-241)
  is alpha = t^2/t_*^2 with t conformal time and a proportional to t^2, i.e. alpha = a.
- For zero shift a Bona-Masso condition d_t alpha = -f alpha^2 K integrates to
  alpha = gamma^(f/2) from alpha_* = 1, gamma_* = 1 [BACKGROUND]; on the background
  gamma^(1/2) = a^3, so alpha = a requires f = 1/3; vector modes leave det gamma unchanged
  at first order, so the paper's linear solution has f = 1/3 at first order in b
  [VERIFIED by `tests/test_ref.py::test_linear_solution_slicing`]. The value of f the ET
  and CosmoGRaPH used is not stated in 2003.08014 [TO VERIFY; not determinable from this
  paper]; the ET's earlier cosmology paper used f = 1/4 (arXiv:1611.05447,
  kb-data .../1611.05447/v2/src, the .tex line 174-177) [VERIFIED for that paper].
- Code: `<z4c> lapse_harmonic = 1/3` gives d_t alpha = -(1/3) alpha^2 Khat
  (`athenak/src/z4c/z4c_calcrhs.cpp` lines 694-698, with lapse_oplog = 0) [VERIFIED]: the
  same slicing as the paper's linear solution. `lapse_volume = 1/3` (alpha - gamma^(1/6)
  constant) is the same slicing in the continuum (differs by Theta only), so it is not an
  independent leg; `lapse_harmonic = 1` (f = 1, literal harmonic slicing) is the second
  admissible condition: the observable is gauge invariant (draft.tex:321), so it must give
  the same cos(theta).
- The time-independent change x -> x' keeps beta = 0 and the lapse equation (K is a
  scalar), so the primed run is the paper's foliation in relabelled spatial coordinates.

Linear solution in the code's coordinates (from draft.tex:237-241 transformed;
[VERIFIED] by the same test), with tau = t_c + 2 the paper's conformal time, a = (tau/2)^2:

    alpha = a,  gamma'_xx = gamma'_yy = gamma'_zz = a^2,
    gamma'_xy = a^2 (b/(H L)) c [ (t_*/tau)^3 - 1 ]      (first order in b).

Exact for every particle and ray: x and z are Killing directions in the primed
coordinates (no field depends on x or z, beta = 0), so the covariant components u_x, u_z
(particles) and k_x, k_z (rays) are conserved exactly [BACKGROUND].

## 4. Observable

cos(theta) between the two rays arriving at the observer comoving with the dust at O
(draft.tex:224-229); for an observer at rest with zero shift at O (both hold here by the
point symmetry (x, y, z) -> (-x, -y, -z), which leaves O fixed and makes u^x(O) = 0)
(draft.tex:536-540):

    cos(theta) = gamma^ij k^A_i k^B_j / sqrt(gamma^ij k^A_i k^A_j gamma^kl k^B_k k^B_l) at O,

with the earlier arrival parallel transported along the observer's worldline to the later
one, d k_i / dt = -alpha K^j_i k_j at O (draft.tex:541-552; d_i alpha = 0 at y = 0 by
symmetry), and gamma^ij taken at the later arrival (draft.tex:552).
Linear prediction (draft.tex:262):

    cos(theta_lin) = b [ (HL + 6)/(HL + 2)^3 + (32 pi^2/HL) Int_0^{2 pi} cos xi / (4 pi + HL xi)^3 d xi ],

limits 3b/4 for HL << 1 and 2b/(HL)^2 for HL >> 1 (draft.tex:265).

Quantity compared (draft.tex:343): Delta = cos(theta)/cos(theta_lin) - 1.

Reported results (numbers only from the text; the figures are not used):
- beta = 0.005: all codes within 0.03 per cent of linear theory at every HL
  (draft.tex:348, 381); the only resolvable departure 0.003 per cent for the ET at HL = 4
  (draft.tex:350), and one outlying CosmoGRaPH point at the smallest L (draft.tex:350, 471).
- beta = 0.05: measurable departures for HL >~ 1, below about 1 per cent in all codes; ET
  and CosmoGRaPH agree within their numerical accuracy (draft.tex:354); within 0.1 per
  cent for HL <~ 1 (draft.tex:383).
- beta = 0.5: within 1 per cent for HL <~ 1 (draft.tex:383), gevolution about 2 per cent
  off (draft.tex:357, 383); at HL = 4: Delta = -0.619 (gevolution), -0.68 (GRAMSES),
  -0.8183 +- 0.0004 (CosmoGRaPH), no connecting ray found in the ET (draft.tex:360);
  relative to CosmoGRaPH the ET is about 15 per cent off at HL = 2 (draft.tex:362).
  CosmoGRaPH (particles) is the paper's reference in this regime (draft.tex:367, 385).
- Constraint norms (draft.tex:440-451, normalised L2 norm of H): figure only, no numbers.
- Convergence of the observable (draft.tex:461-473): figure only.

## 5. Realisation with AthenaK

- Fields: `make_shear_ic.py` writes `fields.bin` (NRCOSMO1) with psi = 1, K = -3,
  alpha = 1, Ahat_xy = (3b/(4L)) c at the cell centres, other components 0
  (`cosmo/ic/nrp_io.py::write_fields`).
- Matter: a lattice of particles with masses m_p = D(y_p) Delta V (rest mass per
  particle; `nrp_io.write_particles`), covariant momenta u_x = u*^x(y_p), u_y = u_z = 0.
  Chosen: masses on a lattice, not equal masses at displaced positions. Reasons
  [JUDGEMENT]: D varies only at O(b^2) (D/D_0 = sqrt(R)/(16 H^2 L^2); at s = 1 it is
  sqrt(1 - pi^2 beta^2/4), a departure of 3e-5 at beta = 0.005 and 3e-3 at beta = 0.05;
  at beta = 0.5 the variation is tens of per cent, which a lattice with unequal masses
  carries just as well), the lattice is the production start of the code (cosmo/README.md),
  a row of particles that shifts in x as a whole deposits a field that stays exactly
  independent of x (the B-spline clouds are a partition of unity), and no inverse
  cumulative distribution enters the data. Particles per cell along y: 1 (default),
  2 and 4 as a leg; one per cell in x and z.
- Observer: a tracer at O (mass 1e-30 of the particle mass scale, u_i = 0), tracked; further
  tracers at y = L/8, L/4, 3L/8, L/2 (comoving with the dust there) for the exact
  conservation of u_x and the metric along y.
- Rays: null particles of the code (`cosmo/ic/ray_ic.py`: mass -t_e, momentum slots hold
  the coordinate direction; the code launches k_i = gamma_ij c^j/|c| at t_e;
  `athenak/src/particles/nrpic.cpp` 455-480) emitted at O at t_c = 0: a fan towards +x
  (ray A, directions (1, s, 0)) and a fan towards +y (ray B, directions (s, 1, 0)). Shooting
  by interpolation over the fan: ray A must cross x = L (unwrapped) at y = 0, ray B must
  cross y = L at x = 0. Trajectories and the metric at the rays and tracers every cycle
  (`traj.bin`, `trajmet.bin`, `nrpic_io.cpp` 800-935).
- Box: [-L/2, L/2]^3, 4 cells in x and z (core/requests-b READY item 4: four cells is
  the minimum), N_y = 32, 64, 128 (more if cheap); production numerics of
  `cosmo/README.md` (pcs clouds with compensation 1/6 and 7/15, bspline metric,
  dt_expansion 0.01, nghost 4, RK4, Courant 0.25, damping 0.5 per unit conformal time).
- Executable: release core-v0.3 processor build (production kind) unless too slow.

## 6. Cases run (subset of the paper's 30, chosen to cover its three statements)

| case | beta | HL | why |
|---|---|---|---|
| S1 | 0.005 | 1 | main series; legs: particles per cell, lapse f = 1 |
| S2 | 0.005 | 1/16 | sub-horizon |
| S3 | 0.005 | 4 | super-horizon, the ET's 0.003 per cent point |
| S4 | 0.005 | 1/128 | smallest box of the paper (CosmoGRaPH's outlier) |
| M1, M2 | 0.05 | 1, 4 | the "below 1 per cent" statement |
| L1, L2 | 0.5 | 1, 4 | the 1 per cent statement; L2 is CosmoGRaPH's -0.8183 +- 0.0004 |

## 7. What counts as agreement

1. Reference: the closed form (draft.tex:262) agrees with my own linear ray tracing of
   the linear solution of section 3 (shooting, observer at rest) to 1e-6 relative.
2. Initial data: the written fields and particles satisfy the constraints to rounding
   with spectral derivatives and the analytic matter, and the code's cstat at t = 0
   converges with N_y at fourth order or faster.
3. beta = 0.005: |Delta| <= 3e-4 (the paper's 0.03 per cent band, draft.tex:348) for the
   Richardson-extrapolated value, with the numerical error (finest minus extrapolated)
   below 3e-4; the run-to-run differences converge at an order between 1.5 and 4.5.
4. beta = 0.05: |Delta| <= 1e-3 at HL = 1 (draft.tex:383), |Delta| < 1e-2 at HL = 4
   (draft.tex:354).
5. beta = 0.5: |Delta| <= 1e-2 at HL = 1 (draft.tex:383); at HL = 4, Delta within
   max(3 x own numerical error, 0.01) of CosmoGRaPH's -0.8183 (draft.tex:360).
6. Gauge: f = 1 and f = 1/3 give the same cos(theta) within the numerical error.
7. Exact checks: u_x of every tracked particle and k_x, k_z of every ray conserved to
   1e-10 relative.
The multi-code row is met if 1-4 and 6-7 hold; 5 decides whether the particle code
reproduces the strongly nonlinear, stream-crossing result of the paper's particle NR code.
