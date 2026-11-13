# Method brief for the manuscript

The facts the paper's method sections are written from. Everything here describes the code
as it is; numbers measured in tests are in `docs/TESTLOG.md` and `docs/results_*.md`.
Notation follows `NOTATION.md` (tetrad indices in parentheses, geodesic energy
\mathcal{E}, refinement indicator \varepsilon).

## 1. System

- Einstein equations G_{\mu\nu} = 8\pi T_{\mu\nu} for collisionless matter described by a
  rest-mass-weighted distribution function f on the mass shell; Vlasov equation
  u^\mu \partial_\mu f - \Gamma^\mu_{\alpha\beta} u^\alpha u^\beta \partial f/\partial u^\mu = 0.
- 3+1 form: ds^2 = -\alpha^2 dt^2 + \gamma_{ij}(dx^i + \beta^i dt)(dx^j + \beta^j dt).
- Macroparticles p = 1..N with fixed rest mass m_p, position x_p^i(t), covariant spatial
  momentum per unit mass u_{i,p}(t): six phase-space variables per particle.
  W = \sqrt{1 + \gamma^{ij} u_i u_j} = \alpha u^0.
- Characteristic equations (coordinate time):
  dx^i/dt = \alpha \gamma^{ij} u_j / W - \beta^i,
  du_i/dt = -W \partial_i\alpha + u_j \partial_i\beta^j - (\alpha/2W) u_j u_k \partial_i\gamma^{jk}.
  They follow from the Hamiltonian H = -u_0 = \alpha W - \beta^i u_i.
- Particle sources seen by normal observers:
  E = \sum_p m_p W_p \delta^3(x - x_p)/\sqrt\gamma,
  S_i = \sum_p m_p u_{i,p} \delta^3/\sqrt\gamma,
  S_{ij} = \sum_p m_p u_{i,p} u_{j,p} \delta^3/(W_p \sqrt\gamma).

## 2. One cycle from t^n to t^{n+1}

1. Keep \alpha, \beta^i, \gamma_{ij} at t^n (all cells including ghost cells).
2. Advance the Z4c variables with RK4; the particle sources deposited at t^n are held
   fixed through the four stages.
3. Push every particle with the metric at t^n and t^{n+1} (time-averaged at the midpoint).
4. Remove particles: lapse excision (interpolated \alpha(t^n, x_p^n) < \alpha_exc), particles
   that left the mesh, particles whose state is no longer finite. Reassign the others to
   their MeshBlocks.
5. Deposit E, S_i, S_ij at t^{n+1}; filter; evaluate the constraints with the new sources.
6. Diagnostics; adaptive mesh refinement; after a regrid the metric arrays, the
   ownership and the sources are rebuilt on the new mesh (particles are never split,
   merged or changed).

Particles and fields share one global time step, set by the finest cell.

## 3. Geodesic pushers

Both are implicit, second order in \Delta t, store x^i and u_i at integer time levels, and
are solved by fixed-point iteration on the six endpoint values until the largest change of
any component is below a tolerance. They see the spacetime only through a function that
returns \alpha, \beta^i, \gamma_{ij} and their first spatial derivatives at a point, so the
same code runs with analytic metrics (any spatial coordinates), with a metric sampled on a
lattice, and with mesh data.

### 3.1 Implicit midpoint pusher

\bar x = (x^n + x^{n+1})/2, \bar u = (u^n + u^{n+1})/2; fields at \bar x averaged between
t^n and t^{n+1}; \bar\gamma^{ij} by inverting the averaged \gamma_{ij};
\bar W = \sqrt{1 + \bar\gamma^{ij}\bar u_i \bar u_j};
(x^{n+1} - x^n)/\Delta t = \bar\alpha \bar\gamma^{ij}\bar u_j/\bar W - \bar\beta^i,
(u_i^{n+1} - u_i^n)/\Delta t = -\bar W \partial_i\bar\alpha + \bar u_j \partial_i\bar\beta^j
  + (\bar\alpha/2\bar W) \bar u^l \bar u^m \partial_i\bar\gamma_{lm}.
A momentum conjugate to a cyclic coordinate is conserved to round-off (seen for u_\phi in
spherical coordinates).

### 3.2 Spacetime Boris pusher

Orthonormal frame of the normal observers: e_{(0)} = n, spatial triad e^{(m)}_i with
\gamma_{ij} = \delta_{mn} e^{(m)}_i e^{(n)}_j. Tetrad momentum u_{(m)} = e^i_{(m)} u_i,
W = \sqrt{1 + \delta^{mn} u_{(m)} u_{(n)}}.

Derivation (short, can be shown): differentiate u_i = e^{(n)}_i u_{(n)} along the
trajectory, d/dt = \partial_t + v^j \partial_j with v^j = \alpha u^j/W - \beta^j, insert the
characteristic equation, and use \partial_i\gamma_{jk} = 2 e^{(n)}_{(j} \partial_i e^{(n)}_{k)}.
With c_{jk} \equiv u_{(n)} \partial_j e^{(n)}_k and c^t_k \equiv u_{(n)} \partial_t e^{(n)}_k:

du_{(m)}/d\hat t = \tilde E_{(m)} + \epsilon_{(m)(n)(k)} u_{(n)} \tilde B_{(k)}/W,   d\hat t = \alpha dt,

\alpha \tilde E_{(m)} = e^i_{(m)} [ -W \partial_i\alpha + u_l \partial_i\beta^l + \beta^j c_{ji} - c^t_i ],
\tilde B_{(k)} = \epsilon_{(k)(m)(n)} e^p_{(m)} e^q_{(n)} c_{pq}.

This is the Lorentz-force form: the gravito-electric and gravito-magnetic fields are the
tetrad field strengths F^{(a)}_{\mu\nu} = \partial_\mu e^{(a)}_\nu - \partial_\nu e^{(a)}_\mu
contracted with the momentum. The fields depend on the momentum, so the update is
implicit: evaluate \tilde E, \tilde B at the midpoint (position, time, and mean of the
endpoint tetrad momenta), then kick, rotate, kick:
u^- = u^n + (\Delta\hat t/2)\tilde E,  t = (\Delta\hat t/2W)\tilde B,  s = 2t/(1+|t|^2),
u' = u^- + u^- \times t,  u^+ = u^- + u' \times s,  u^{n+1} = u^+ + (\Delta\hat t/2)\tilde E,
and the position from the same midpoint state; iterate; convert back with the triad at
(t^{n+1}, x^{n+1}).

### 3.3 Tetrad gauge (a finding of this work)

The triad is fixed only up to a local rotation, and the truncation error of the scheme
depends on the choice. Two gauges are implemented:
- symmetric gauge: e^{(m)}_j = (\gamma^{1/2})_{mj}, the symmetric positive square root
  (eigen-decomposition; derivative from the Sylvester equation S dS + dS S = d\gamma in
  the eigenbasis);
- Cholesky gauge: e^{(m)}_j = L_{jm} with \gamma = L L^T, L lower triangular
  (Gram-Schmidt on the coordinate basis vectors in index order; closed form, cheaper).
The original paper does not state its gauge. Its invariant errors for analytic spherical
Kerr-Schild input are reproduced to all published digits by the symmetric gauge, and its
errors for the Cartesian grid input by the Cholesky gauge in (x, y, z) order; neither
gauge reproduces both sets, and the other orderings and combinations do not match.

## 4. Metric reconstruction

Cell-centred fields \alpha, \beta^i, \gamma_{ij} (covariant components; the inverse is
taken after interpolation). Tensor-product cubic Hermite (Catmull-Rom) interpolation on
the 4^3 cells around the point, weights
w_{-1} = (-s + 2s^2 - s^3)/2, w_0 = (2 - 5s^2 + 3s^3)/2, w_1 = (s + 4s^2 - 3s^3)/2,
w_2 = (-s^2 + s^3)/2; first derivatives from the derivative of the same polynomial.
Needs two ghost cells. A particle is interpolated within its own MeshBlock; where the
stencil would leave the allocated cells it is shifted inward (same cubic, extrapolated).
For tests the same reconstruction is applied to an analytic metric sampled on a virtual
lattice of cell centres, which is equivalent to an arbitrarily large uniform mesh.

## 5. Deposition

- First-order (cloud-in-cell) shape B_1(\xi) = 1 - |\xi| for |\xi| < 1, tensor product,
  eight receiving cells, partition of unity.
- Sources divided by \sqrt\gamma at the receiving cell and by its coordinate volume.
- Refined meshes (published scheme): particle p is represented on one level \ell_p, the
  finest among the leaf blocks that own its eight nearest cell centres; the cloud is laid
  on the uniform lattice of that level, extended virtually into coarser blocks; the
  weight of a virtual cell is accumulated in the coarse leaf cell that contains it.
  Weights sum to one over the leaf cells, so
  \sum_C (E, S_i, S_{ij})_C \sqrt{\gamma_C} \Delta V_C = \sum_p m_p (W, u_i, u_i u_j/W)_p
  to round-off (the conservation identity).
- Level cap (new here): \ell_p = min(finest local level, \ell_cap). Where the mesh is
  finer than the cap, the cloud keeps the cell size of the cap level and the density of
  each lattice cell is spread uniformly over the leaf cells inside it. The conservation
  identity holds in the same way. Reason: each refinement level divides the number of
  particles per cell by eight; once cells are smaller than the particle spacing, a cloud
  that shrinks with the mesh turns the source into isolated blobs. With the cap removed
  the scheme is the published one.
- Density-adaptive cap (new here): \ell_cap of each particle is the finest level, between
  a floor and a ceiling, whose cells hold at least a target number of particles at the
  local coordinate density \sqrt\gamma E of the previous deposit,
  \Delta x_{cap}^3 >= N_target m_p W_p/(\sqrt\gamma E). The cloud then follows the
  particle density as matter contracts, like an adaptive smoothing length.
- Binomial filter (1/4, 1/2, 1/4)^3 applied n_f times to each of the ten source
  components; ghost cells are filled before each pass (copy at equal level, restriction
  and prolongation across levels).
- Implementation: ownership and deposition are resolved by a search over the MeshBlocks
  for the block containing a point (single MPI rank); scatter with atomic adds on the GPU.

## 6. Spacetime evolution (AthenaK, used as is except where noted)

- Z4c with constraint damping \kappa_1, \kappa_2; cell-centred finite differences;
  RK4; Kreiss-Oliger dissipation; Sommerfeld outer boundaries.
- Moving-puncture gauge: 1+log lapse \partial_t\alpha = \beta^i\partial_i\alpha - 2\alpha\hat K,
  integrated Gamma-driver \partial_t\beta^i = \mu \tilde\Gamma^i - \eta\beta^i + \beta^j\partial_j\beta^i.
- AthenaK requires an even number of ghost cells with mesh refinement, so refined runs
  use sixth-order differences (four ghost cells); the original quotes fourth order.
- Added: matter sources from the particles (AthenaK had them only for
  magnetohydrodynamics); optional parabolic relaxation of the Hamiltonian constraint,
  \partial_t\chi += (c_H/2)\chi^{-1/4}\mathcal H with
  \mathcal H = R + (2/3)K^2 - \tilde A_{ij}\tilde A^{ij} - 16\pi E, c_H a length
  (constant plus a part proportional to the local cell size); refinement indicator;
  Kretschmann scalar.
- Not implemented: the variant of the shift condition with the auxiliary field B^i, and
  the position-dependent \eta and \kappa_1 tied to tracked black holes.

## 7. Adaptive mesh

- Octree block-structured mesh of AthenaK.
- Refinement indicator of q = \alpha\chi^{-7/4}: with D_a q_i = q_{i+e_a} - q_{i-e_a} and
  S_{ab,i} = \sum_{\sigma,\tau=\pm1} |q_{i+\sigma e_a+\tau e_b}|,
  \varepsilon_i^2 = \sum_{ab}(D_a q_{i+e_b} - D_a q_{i-e_b})^2 /
  \sum_{ab}(|D_a q_{i+e_b}| + |D_a q_{i-e_b}| + \epsilon S_{ab,i} + \delta)^2;
  a block is refined when its maximum exceeds the upper threshold and derefined below the
  lower one (same values as the original). A minimum level inside given radii keeps the
  matter resolved at the level of the particle lattice.
- Particles keep m_p, x_p, u_p through every regrid.

## 8. Numerical methods (last method subsection)

- Excision: lapse threshold; apparent-horizon-based excision is not implemented.
- Apparent horizons: AthenaK's flow finder, with its stopping tolerance tightened (the
  default leaves a surface with residual expansion and underestimates the area).
- Central diagnostics: lapse and energy density interpolated to the origin (average of
  the eight central cells); proper time \tau_c = \int \alpha_c dt.
- Kretschmann scalar from the Gauss, Codazzi and Ricci equations with Einstein's
  equations for the term with two normals:
  I = G_{abcd}G^{abcd} - 4 C_{abc}C^{abc} + 4 Z_{ab}Z^{ab},
  G_{abcd} = {}^{(3)}R_{abcd} + K_{ac}K_{bd} - K_{ad}K_{bc}, C_{abc} = D_aK_{bc} - D_bK_{ac},
  Z_{ab} = {}^{(3)}R_{ab} + K K_{ab} - K_{ac}K^c{}_b - 8\pi[S_{ab} - \gamma_{ab}(S - E)/2];
  checked against 48M^2/R^6.
- Initial data: conformally flat, time-symmetric slices with
  \psi = 1 + \sum_c u_c, each u_c solving the flat Poisson equation for a conformal source,
  so the superposition solves the Hamiltonian constraint for \rho = \tilde\rho\psi^{-5};
  components: tabulated spherical profile, puncture m/2r, Gaussian, homogeneous prolate
  spheroid (closed form). Equal-mass particles then have coordinate number density
  proportional to \rho_0\psi^6.
- Samplers: mass-weighted lattice (dust ball; aligned with the mesh so the initial
  deposited density is exact), randomized stratified sampling in radius, both position
  angles and both velocity angles (clusters), Monte Carlo with reflection and
  half-turn symmetry (spheroid).
- Performance portability through Kokkos; all runs on a single GPU; the particle work is
  a few percent of the cost of the spacetime update at these particle numbers.

## 9. How the code was assembled (for the dedicated section and the hypergraph)

Capabilities taken from existing codes and methods (nodes):
1. AthenaK mesh: octree blocks, AMR, ghost exchange, prolongation and restriction.
2. AthenaK Z4c solver and moving-puncture gauge.
3. AthenaK particle container (arrays, tags) and its drift pusher.
4. AthenaK matter-source interface of the Z4c solver (from the magnetohydrodynamics
   coupling).
5. AthenaK apparent-horizon finder, puncture tracker, wave extraction.
6. Kokkos performance portability.
7. Implicit midpoint geodesic integration from general-relativistic plasma PIC codes.
8. Boris rotation from plasma PIC.
9. Tetrad (electromagnetism-like) form of gravity (DGREM).
10. Cloud-in-cell deposition and binomial filtering from plasma PIC.
11. Single-level deposition across refinement boundaries (WarpX).
12. Loehner refinement indicator.
13. Lapse-based excision from particle hydrodynamics in numerical relativity.
14. Parabolic constraint relaxation.
15. Analytic solutions used as tests: Kerr geodesics, Oppenheimer-Snyder collapse,
    monoenergetic cluster sequence, spheroid potential.
16. The published description of the NRPIC method (text only).

Components of this code (hyperedges, each combining several nodes):
- A. Geodesic pushers = {7, 8, 9, 16, 6}
- B. Mesh metric reconstruction = {1, 16, 6}
- C. Conservative deposition with level cap = {10, 11, 1, 3, 16, 6}
- D. Coupled cycle = {2, 4, A, C, 16}
- E. Adaptive mesh for particles = {1, 12, 3, C}
- F. Excision and horizon diagnostics = {13, 5}
- G. Constraint control = {2, 14, 10}
- H. Initial data and validation = {15, 16}
The whole was built by language-model agents working from the published text:
a lead model for design, derivations and solver source; worker models for builds, runs,
reference solutions and analysis; a third model for the manuscript text.
