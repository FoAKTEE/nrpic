# Spherical initial data with extrinsic curvature: table format 2 (refined)

Status: PROPOSAL of core (branch `core/id-extrinsic`, 2026-11-15) for
`coord/INTERFACES/spherical_id_format2.md`. Implemented in
`athenak/src/pgen/nrpic/nrpic_cf.cpp` (reader, evaluation) and `python/nrpic/io.py`
(`write_tab2`, `read_tab2`, `Table2`: the same evaluation rule). Reference generator:
`python/nrpic/expanding_ball.py`, command line `problems/ic/make_ball.py`.

## What changed against the provisional text, and why

1. New optional header line `# breaks = r_1 r_2 ...`. Reason: at a sharp dust surface
   the radial eigenvalue KL of the extrinsic curvature jumps (marginally bound ball: from
   -H inside to +H/2 outside) and u has a kink in its second derivative; the same holds
   at the wall of Track D's vacuum bubble. A cubic through rows on both sides of the jump
   overshoots, and the continuation "through the last row" needs a last row that lies in
   vacuum. With a break the interpolation takes its four rows from one side only. A file
   without the line is read exactly as the provisional text says, so tables written to
   the provisional text stay valid.
2. Stated explicitly: which conformal factor multiplies the curvature (the full one, all
   components), what happens at the centre, the limits of the reader (rows, breaks), and
   the two start options of the problem generator.
3. Nothing else changed: columns, grid, exterior continuations, particles and the
   division of responsibility are those of the provisional text.

## Geometry the table describes

One spherically symmetric component centred at `x_c`. With `rbar = |x - x_c|` (the
isotropic, conformally flat radius) and `n^i = (x - x_c)^i / rbar` in the Cartesian
coordinates of the code:

- spatial metric `gamma_ij = psi^4 delta_ij`, `psi = 1 + sum over components of u_c`
  (as in format 1; `u` superposes linearly with punctures and other tables);
- extrinsic curvature `K_ij = psi^4 [ KT delta_ij + (KL - KT) n_i n_j ]` with the full
  `psi` of the run, that is, mixed components `K^r_r = KL`,
  `K^theta_theta = K^phi_phi = KT`, trace `K = KL + 2 KT`; sign convention of the code,
  `K_ij = -(1/(2 alpha)) (d_t gamma_ij - D_i beta_j - D_j beta_i)`, so expansion has
  `K < 0`. Only one component of a run may be a table of format 2. Within `1e-12 drbar`
  of the centre the direction term is dropped (regular data have `KL = KT` there);
- initial lapse `alpha` and initial shift `beta^i = betar n^i`.

## File

Text. Header lines begin with `#` and must include

    # format = 2
    # columns = rbar u KL KT alpha betar
    # exterior = pg | zero

and may include

    # breaks = r_1 r_2 ...          (at most four, increasing, inside the table)

followed by rows of six numbers on a uniform grid `rbar_k = k * drbar`, `k = 0 .. N-1`
(first row at `rbar = 0`, at least eight rows).

Breaks. A break is a radius at which the columns may be discontinuous (KL, KT, alpha,
betar: jump; u: kink). It must lie strictly between two rows (further than
`1e-6 drbar` from both; the reference generator puts it midway). The rows with
`rbar_k < r_b` belong to the piece inside the break and hold the values of the inner
side, the rows with `rbar_k > r_b` to the piece outside. Every piece needs at least four
rows.

Evaluation at `rbar` inside the table (`rbar < rbar_(N-1)`): cubic (four-point
Lagrange) through the rows `i-1 .. i+2`, `i = floor(rbar/drbar)` moved so that all four
rows lie in the piece that contains `rbar` (a point with `rbar >= r_b` is outside the
break `r_b`). Next to a break or to an end of the table the cubic is therefore
one-sided and may extrapolate by up to one row spacing.

Beyond the last row: `u` continues as `u_(N-1) rbar_(N-1) / rbar` (as in format 1);
with `exterior = pg`, `KL` and `KT` continue as `rbar^(-3/2)` and `betar` as
`rbar^(-1/2)` through the last row and `alpha` stays at its last value (exact for a
Painleve-Gullstrand exterior with `psi = 1`: the last piece must then lie in vacuum);
with `exterior = zero`, `KL = KT = betar = 0` and `alpha` stays.

Other header lines (`# key = value`) are free and are copied to the log.

## Start options of the problem generator `nrpic_cf`

    <problem>
    comp0_type = table
    comp0_file = <file of format 2>     # format detected from the header line
    lapse      = one | table | isotropic | precollapsed     (default one)
    lapse_comp = 0                      # table: the alpha column of that component
    shift      = zero | table           (default zero; read only with a format-2 table)
    shift_comp = <the format-2 component>

`lapse = table` with a format-2 component uses its alpha column (last value beyond the
table, not the Schwarzschild lapse that format 1 continues with). The other lapse
choices and the other component types (punctures, Gaussians, spheroid, format-1 tables)
are unchanged and may be superposed in `u`.

## Particles

The existing particle file (`docs/FORMATS.md`): positions in the same Cartesian
coordinates, covariant momenta `u_i` per unit mass, rest masses. Dust that is at rest with
respect to the normal observers of the slice has `u_i = 0`, whatever the shift.

## Responsibility

The generator of a table guarantees the constraints for the matter it comes with and
ships an offline check (Hamiltonian and momentum residuals against resolution;
`nrpic.expanding_ball.residuals_1d` does this for any `Table2` and density). The
problem generator only evaluates the table.
