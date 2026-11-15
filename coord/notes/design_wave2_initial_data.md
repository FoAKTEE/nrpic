# Design note for wave 2: initial data beyond spherical symmetry

Status: [JUDGEMENT], orchestrator, 2026-11-15. For review by core and the leads of tracks
A, B, D and F; nothing here is implemented. Units G = c = 1; conformally flat slices,
gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij + (1/3) psi^4 delta_ij K.

## 1. What the particles fix

Macroparticles carry positions, rest masses m and covariant momenta u_i. On the mesh they
give the conformal densities

    Etilde   = psi^6 E   = sum_p m W S(x - x_p) / dV,   W = sqrt(1 + psi^-4 |u|^2),
    Stilde_i = psi^6 S_i = sum_p m u_i S(x - x_p) / dV,

with S the cloud of the code followed by its filter and compensation. Stilde_i does not
depend on psi; Etilde depends on psi only through W and not at all for u_i = 0. The
constraints read

    lap psi = -(1/8) psi^-7 Abar_ij Abar^ij + (1/12) psi^5 K^2 - 2 pi psi^-1 Etilde,
    d_j Abar^ij - (2/3) psi^6 d^i K = 8 pi psi^4 Stilde^i.

Every term on the right of the first equation has a derivative with respect to psi that is
non-negative, so the linearised operator is negative definite and the solve is well
posed: this is the particle form of the scaling argument used on the torus in `cosmo/`.
The data must be solved with the code's own deposited densities on the code's own mesh
(the cells of the level that covers the matter at the start), as `cosmo/ic` does; a
continuum density would leave the sampling noise as a constraint violation.

## 2. Dust at rest with respect to the slice (tracks A, B, D)

For irrotational dust choose the slice orthogonal to the flow: u_i = 0, Stilde_i = 0. The
whole velocity field is then in K_ij. Trial fields from a Newtonian velocity field v
(Hubble flow of the ball plus the growing-mode peculiar velocity of a Zel'dovich
deformation): psi = 1, K_ij = -d_(i v_j), which is exact for the spherical marginally
bound ball (`derivations_to_check.md`, item 1). Projection onto the constraints by the
conformal transverse-traceless decomposition: keep K = -div v, set
Abar_ij = Abar_ij(trial) + (L W)_ij, solve the vector equation for W^i and the scalar
equation for psi, iterate. For the spherical trial the solution is psi = 1, W = 0. To
first order in the density contrast delta of a growing mode the scalar equation gives
lap(dpsi) = -(5/4) H^2 delta, that is dpsi = -(5/6) Phi with Phi the Newtonian potential
perturbation: the curvature perturbation of the comoving slicing, as it should be
[to be checked by Track A]. In the vacuum exterior the trial is exact; corrections fall
off as multipoles, so Robin conditions (psi - 1 and W^i proportional to 1/r) on the
faces of a cube a few ball radii wide are enough.

Why not solve for K algebraically with psi = 1 (the scheme of arXiv:2207.03125): with
psi = 1 the perturbation sits in K, the slice is not orthogonal to the dust, u_i is then
non-zero and enters W and both densities, and the system becomes nonlinear in the particle
data. Keep that scheme as the alternative if the transverse-traceless projection fails
to converge at large amplitude.

Where to implement: first as a Python solver on a uniform mesh (finite differences,
Newton-Krylov with a multigrid preconditioner; 128^3 to 256^3 cells fit this machine),
writing psi, K and Abar_ij on that mesh; the problem generator reads the arrays and
interpolates them to the refined mesh, with the analytic exterior beyond the cube. An
elliptic solver inside the code (multigrid on the refined mesh, needed once black holes
and matter are solved together) is the later step. Owner of the solver: core (source
tree, `python/nrpic`); Track A specifies and tests it.

## 3. Moving matter clumps: curvature that satisfies the momentum constraint (tracks F, D; first paper)

The two-overdensity cluster of the first paper puts moving clumps on a slice with
K_ij = 0, so the momentum constraint is violated at first order in the orbital speed
(paper, Appendix B). With psi fixed in the source term the momentum constraint is linear
in Abar_ij and the solutions superpose: for each matter component with momentum density
Stilde^i, Abar_ij = (L W)_ij with lap W^i + (1/3) d^i d_j W^j = 8 pi psi^4 Stilde^i. For
a point momentum this is the Bowen-York curvature; for a cold Gaussian clump with one
bulk velocity it is the Bowen-York curvature smeared with the Gaussian, which has a
closed form in error functions [to be derived and checked by core]. Adding it for every
moving clump, together with the Bowen-York terms of moving punctures (branch
`core/multi-puncture`), removes the first-order violation; what remains is second order
in the momenta (the Abar^2 term of the scalar equation), which either is solved for psi
or is left and measured.

Direct test it enables: the first paper asks whether initial data that satisfy the
momentum constraint remove the excess of the remnant mass over the total mass (2.5
percent) in the two-overdensity run. Rerun `n1e4_v19` with the smeared curvature; predict
before the run.

## 4. Order of work proposed for wave 2

1. core: merge table-based curvature (spherical, format 2) and Bowen-York punctures
   (wave 1); add the smeared curvature of item 3; then the gridded import and the Python
   projection solver of item 2.
2. Track A: spherical expanding ball and bound core against the exact solution (gauge
   choice from the tests of `core/id-extrinsic`), then the first triaxial case with the
   solver of item 2.
3. Track D: the black hole in the vacuum bubble (spherical table plus puncture).
4. Track F: one vacuum passage of three black holes; then a clump binary with item 3.
