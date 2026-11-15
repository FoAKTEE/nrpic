"""Initial data and exact solution of the expanding dust ball (Track A, work package A-pre-1).

Modules
    model      initial slice: profiles, Misner-Sharp mass, bound energy E, KL, KT, conformal
               factor, rest mass, high-accuracy radial interpolants (DERIVATION.md sec. 3-4)
    exact      exact evolution of every shell: areal radius against proper time, turnaround,
               crunch, apparent-horizon times (DERIVATION.md sec. 5)
    table      table format 2 (coord/INTERFACES/spherical_id_format2.md), reader, and the
               four-point Lagrange interpolation of the code's format-1 tables
    particles  lattice, stratified and Monte Carlo samples (u_i = 0), particle file writer
    mesh       fields on a Cartesian mesh, finite-difference constraint residuals, CIC deposit
    runlog     run manifests (CLAUDE.md rule 4)

Units G = c = 1. Code sign: K_ij = -(1/(2 alpha))(d_t gamma_ij - D_i beta_j - D_j beta_i).
"""

__all__ = ["model", "exact", "table", "particles", "mesh", "runlog"]
