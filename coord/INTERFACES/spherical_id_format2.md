# Spherical initial data with extrinsic curvature: table format 2

Status: PROVISIONAL (orchestrator, 2026-11-15). Implemented by core (branch
`core/id-extrinsic`), written by Track A (expanding ball, Lemaitre-Tolman-Bondi data) and
Track D (black hole in a vacuum bubble). Changes: proposal to `orch`.

## Geometry the table describes

One spherically symmetric component centred at `x_c`. With `rbar = |x - x_c|` (the
isotropic, conformally flat radius) and `n^i = (x - x_c)^i / rbar` in the Cartesian
coordinates of the code:

- spatial metric `gamma_ij = psi^4 delta_ij`, `psi = 1 + sum over components of u_c`
  (as in format 1; `u` superposes linearly with punctures and other tables);
- extrinsic curvature `K_ij = psi^4 [ KT delta_ij + (KL - KT) n_i n_j ]`, that is, mixed
  components `K^r_r = KL`, `K^theta_theta = K^phi_phi = KT`, trace `K = KL + 2 KT`; sign
  convention of the code, `K_ij = -(1/(2 alpha)) (d_t gamma_ij - D_i beta_j - D_j beta_i)`,
  so expansion has `K < 0`. Only one component of a run may carry `KL`, `KT`;
- initial lapse `alpha` and initial shift `beta^i = betar n^i`.

## File

Text. Header lines begin with `#` and must include

    # format = 2
    # columns = rbar u KL KT alpha betar
    # exterior = pg | zero

followed by rows on a uniform grid `rbar_k = k * drbar`, `k = 0 .. N-1` (first row at
`rbar = 0`). Beyond the last row: `u` continues as `u_N rbar_N / rbar` (as in format 1);
with `exterior = pg`, `KL` and `KT` continue as `rbar^(-3/2)` and `betar` as
`rbar^(-1/2)` through the last row and `alpha` stays at its last value (exact for a
Painleve-Gullstrand exterior with `psi = 1`); with `exterior = zero`, `KL = KT = betar = 0`
and `alpha` stays. Other header lines (`# key = value`) are free and are copied to the log.

## Particles

The existing particle file (`docs/FORMATS.md`): positions in the same Cartesian
coordinates, covariant momenta `u_i` per unit mass, rest masses. Dust that is at rest with
respect to the normal observers of the slice has `u_i = 0`.

## Responsibility

The generator of a table guarantees the constraints for the matter it comes with and
ships an offline check (Hamiltonian and momentum residuals against resolution). The
problem generator only evaluates the table.
