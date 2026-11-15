# verify_cosmo: journal (helper of B-emd-gw)

Predictions are written before the run that can refute them; outcomes follow in later
entries, failed predictions included. Times are UTC of 2026-11-15.

## Reference solution (11:45)

Plane wave of `cosmo/ic/make_east.py --ratios 1,0,0` (and `pm.east_particles` with
ratios (1, 0, 0)): at a = 1 the Eulerian density is rho0 (1 + d sin kx) and the
velocity dx/dtau = (d/k) cos kx (code: `make_east.py` lines 121-127, `pm.py`
`east_particles`). Equations of `cosmo/newton/pm.py` (docstring): dx/dtau = p/a,
dp/dtau = -(3/2) d_x lap^-1 delta_N, a = (1 + tau/2)^2. In plane symmetry the force on a
sheet is (3/2)(x - Qt) with Qt = Q + X_cm - L/2 (Q the mass to the left over the mean
density), and Qt does not change before two sheets cross; so every sheet obeys
d/dtau(a ds/dtau) = (3/2) s, s = x - Qt, whose solutions are a and a^(-3/2). For these
data Q(x) = x + (d/k)(1 - cos kx), X_cm = L/2 - d/k, so s0 = (d/k) cos kx0 = v0: a pure
growing mode. Fluid element starting at x0: x = x0 + (a - 1)(d/k) cos kx0, dx/dtau =
a^(1/2)(d/k) cos kx0, rho/rho0 = (1 + d sin kx0)/(1 - (a - 1) d sin kx0); first crossing
at x0 = L/4 at a = 1 + 1/d (21 for d = 0.05). This is the Zel'dovich solution of the
brief's row "plane-symmetric pancake" [derivation here; the statement "exact up to shell
crossing" is the brief's [BACKGROUND] and follows from the derivation for Newtonian
gravity].
Code: `scripts/zeldovich.py`; checks `scripts/test_zeldovich.py` (all pass, 11:45):
closed form against a fourth-order integration of the sheet equations (positions
6e-15, velocities 2e-15), continuum density equal to dQ/dx (1e-8 at a = 20), discrete
sheets against the continuum 1.8e-4 (32 cells) and 4.5e-5 (64 cells) of the
displacement, second order; decaying-mode content of the lattice data 3.3e-4 and
8.2e-5 of the velocity amplitude (the discrete mass coordinate).
Discrete crossing of the lattice sheets (exact sheet solution, 32, 64, 96 sheets per
wavelength): a = 21.109, 21.027, 21.012.

## Plan and predictions for the pancake scouting runs (11:47)

Data: d = 0.05 plane wave, one particle per cell (lattice at the cell corners), box of
one initial Hubble radius (L = 1, (H0/k)^2 = 0.0253, depth of the potential
|psi_N| = (3/2)(H0/k)^2 d = 1.9e-3), meshes 32, 64, 96; one horizon-scale case L = 4
((H0/k)^2 = 0.405, |psi_N| = 0.030) at 64 cells. Relativistic runs: release executable
`.work/build_gpu_c3/src/athena`, production configuration of `cosmo/README.md` (cubic
cloud, compensation 1/6 and 7/15, no filter, spline interpolation, step limit 0.01,
damping rate 0.5 per unit of conformal time), conformal-time lapse condition, zero shift,
to t = 10.9615 (a = 42, twice the crossing). Newtonian reference
`scripts/newton_pancake.py` (pm.py unchanged) at 32 and 64 cells for L = 1; the
Newtonian equations have no scale, so the L = 1 run is also the reference of L = 4
(lengths times 4).
Why L = 1 for the main case: in this slicing with zero shift the coordinate positions
of the matter equal the Newtonian ones at linear order (Newtonian-gauge velocity equals
the Newtonian velocity for the growing mode in matter domination [BACKGROUND]); the
relativistic departures are then of relative size |psi_N|, below the accuracy goals,
so the comparison with Zel'dovich tests the code. L = 4 shows the size of the
relativistic departure.

Predictions (written before any of these runs):
P1 Newtonian reference against Zel'dovich (64 cells): largest position error over the
   sheets, relative to the displacement since a = 1, (a - 1) d/k, below 1e-3 for
   a <= 10, below 3e-3 at a = 15, below 3e-2 at a = 20; velocities, relative to
   a^(1/2) d/k, the same bounds. At 32 cells larger, by a factor between 2 and 16.
   Refuted if the 64-cell error exceeds these bounds or does not fall with resolution.
P2 Relativistic, L = 1, 64 cells, against Zel'dovich: the same quantities below 5e-3 for
   a <= 15; the difference relativistic minus Newtonian at equal cells smooth in x (no
   cell-scale pattern) and between 2e-4 and 2e-2 of the displacement at a = 10.
P3 First crossing (first swap of neighbouring sheets on the fiducial line): Newtonian
   and relativistic L = 1 at a within 3 percent of the exact-sheet value (21.03 at 64
   cells), later rather than earlier (the cloud smooths the force of a pancake thinner
   than a cell), approaching it with resolution; relativistic over Newtonian crossing
   within 1 percent of one at L = 1 and later by 3 to 20 percent at L = 4.
P4 Constraints (mean of the relative constraints of `.cstat.hst`): before crossing
   (a <= 15) mean H_r between 1e-8 and 1e-4 and mean M_r below 1e-2 at 64 cells, falling
   with resolution from 32 to 64 cells (any factor above 1.5); after crossing (a = 30 to
   42) both rise by more than ten over their value at a = 15 and the ratio between 64
   and 96 cells falls below two (noise of the multi-stream region, as after collapse in
   cosmo/TESTLOG.md, C2 and C5 production entries).
P5 Plane symmetry: spread of x over a lattice plane and |u_y|, |u_z| below 1e-10 (of L
   and of the velocity amplitude) before crossing in both calculations; refuted above
   1e-6.
P6 All four relativistic runs reach a = 42 with every particle kept (no horizon forms in
   plane symmetry at these amplitudes [JUDGEMENT]); refuted for L = 4 if the run stops at
   the crossing. Total card time below 20 minutes.

## First look at the constraints, and a prediction for two particles per cell (11:58)

Runs done so far in B-emd-gw-20261115-115217-69ab1db: L1_n32, L4_n64, L1_n64 (all to
a = 42, exit 0). Prediction P4 (mean H_r below 1e-4 and mean M_r below 1e-2 before the
crossing, falling with resolution) fails already: mean H_r = 1.6e-4 (64 cells) and
2.4e-4 (32 cells) at a = 10, 1.3e-3 and 1.7e-3 at a = 15; mean M_r = 0.13 and 0.14 at
a = 10 (C2 production run with three modes at d = 0.01: 3.7e-6 and 8.9e-4 at a = 10,
cosmo/TESTLOG.md, entry 07:37). Nearly no change from 32 to 64 cells.
Where it sits (field dumps of L1_n64, figure in progress): at a = 10 |H|/16 pi <E> is
1e-4 to 1e-3 in the underdense half of the box (x/L = 0.55 to 0.95) and 1e-5 to 3e-4
around the pancake; M_x likewise. Cause proposed: the lattice of one particle per cell
is stretched in the void (spacing 1.45 h at a = 10, 1.7 h at a = 15) and its cubic
cloud no longer deposits a smooth density there: depositing the exact Zel'dovich sheet
positions with the code's cloud and compensation (scripts/analyze_pancake.py,
deposit_1d) gives a density that differs from the continuum Zel'dovich density by 8.1e-2
in the void at a = 10 and 2.1e-1 at a = 15 (1e-2 elsewhere), while the relativistic
density matches that deposit to 7e-3. The field equations see the lattice ripple; the
particles move as a smooth flow; the constraints record the mismatch.
Test: the same 64-cell, L = 1 case with two particles per cell and direction
(make_east.py --ppc 2; 2,097,152 particles). The same deposit of exact positions then
differs from the continuum by 5.4e-3 (a = 10) and 2.2e-3 (a = 15) in the void.
Prediction P7, written before the run: mean H_r and mean M_r at a = 10 and a = 15 lower
than with one particle per cell by more than a factor of 5; |H| in the void at a = 15
lower by more than 10; the positions against Zel'dovich unchanged within 20 percent of
their error (the error is the relativistic offset, not the deposit). Refuted if the
mean constraints fall by less than 2.

## Pancake runs: outcomes against P1 to P7 (12:24)

Runs: relativistic B-emd-gw-20261115-115217-69ab1db (Slurm job 4373, 17.1 min, all four
exit 0 to a = 42), B-emd-gw-20261115-115902-a3207d7 (two per cell, job 4388, 11.8 min,
exit 0); Newtonian B-emd-gw-20261115-115239-69ab1db (32 and 64 cells, 94 s and 1709 s on
one core each); analysis B-emd-gw-20261115-122240-b0e4c9d (`results/pancake.json`).
Card time 0.48 card-hours of the 1 allowed. Errors are the largest over the sheets of
the fiducial x line, positions relative to the displacement since a = 1, (a - 1) d/k,
velocities relative to a^(1/2) d/k.

P1 (Newtonian against Zel'dovich, 64 cells): positions 4.8e-5, 3.3e-4, 1.0e-3, 8.3e-4,
6.6e-4 at a = 2, 5, 10, 15, 20; velocities 1.1e-4, 7.9e-4, 1.8e-3, 1.1e-3, 9.9e-3.
Bounds: a <= 10 below 1e-3: FAILS (positions 1.02e-3 at a = 10, velocities 1.8e-3); a = 15
below 3e-3: holds; a = 20 below 3e-2: holds. 32 cells larger by 2 to 16: positions
2.3, 1.9, 2.0 at a = 2, 5, 10 (at the lower edge, fails at a = 5); velocities 2.0, 2.1,
1.9. So the reference converges at first order, not at the order of the compensated
cubic cloud. Not yet explained; a test follows (P8).
P2 (relativistic L = 1 against Zel'dovich): positions 1.85e-3, 2.6e-3, 3.2e-3, 3.8e-3 at
a = 2, 5, 10, 15 (64 cells); velocities 1.9e-3, 3.1e-3, 4.2e-3, 6.0e-3. Below 5e-3 for
a <= 15: holds for positions, fails for velocities at a = 15 (6.0e-3). The offset is the
same at 32, 64, 96 cells and with two particles per cell to three digits (3.15e-3,
3.20e-3, 3.20e-3, 3.21e-3 at a = 10): it is converged, i.e. a property of the solution in
these coordinates, not an error. Relativistic minus Newtonian at a = 10: 3.2e-3 of the
displacement (predicted 2e-4 to 2e-2: holds); smooth over the sheets, a pattern of the
first and second harmonics with no cell-scale part (figure `figs/pancake_grdiff.png`:
holds). At L = 4 the same offset is 5.2e-2 at a = 10, 16.1 times the L = 1 value;
(H0/k)^2 is 16 times larger. So the relativistic departure of the coordinate
trajectories from Zel'dovich scales as (H0/k)^2 d, about 1.7 |psi_N| at a = 10 in both
boxes. In the first two time units the velocity offset oscillates (figure
`figs/pancake_errors.png`), period close to one light crossing of the box: a gauge or
constraint transient of the initial data, not identified further [TO VERIFY].
P3 (first crossing, scale factor of the background at the coordinate time of the first
swap of neighbouring sheets): exact sheets 21.117, 21.029, 21.013, 21.002 (32, 64, 96
sheets and the 128 sheets of the two-per-cell lattice). Newtonian 21.547 (32), 21.222
(64): +2.0 and +0.9 percent; relativistic L = 1: 21.808, 21.379, 21.267 (32, 64, 96),
21.335 (64, two per cell): +3.3, +1.7, +1.2, +1.6 percent. Within 3 percent and later:
holds except the 32-cell relativistic run (3.3); approaching with resolution: holds.
Relativistic over Newtonian at equal cells 1.012 (32), 1.007 (64): within 1 percent
holds at 64 cells, fails at 32. L = 4: 22.846, later than the Newtonian run by 7.7
percent (predicted 3 to 20: holds). These are coordinate-time labels; the crossing is
an invariant event but its time label is not (the proper time of the crossing sheets is
not yet extracted) [TO VERIFY].
P4 (constraints): FAILS. Mean H_r at a = 2, 5, 10, 15: 1.2e-6, 2.4e-5, 1.6e-4, 1.3e-3
(64 cells), 1.5e-6, 3.4e-5, 2.4e-4, 1.7e-3 (32), 1.1e-6, 2.2e-5, 1.4e-4, 1.2e-3 (96);
mean M_r 1.3e-3, 2.7e-2, 0.13, 0.21 (64); nearly independent of the mesh. After the
crossing (a = 22 to 42) mean H_r 7.1e-3 to 3.8e-3, mean M_r 0.34 to 0.54 (64 cells),
less than ten times the a = 15 value (fails); the ratio 64 to 96 cells after the
crossing is below two (holds). L = 4: mean H_r 6.1e-4 (a = 10), 6.4e-3 (a = 20), 1.0e-2
(a = 25). Cause tested in P7.
P5 (plane symmetry): holds. Snapshots at a = 5.6, 14.1, 26.3: spread of x over each
lattice plane at most 4.5e-14 L, |u_y|, |u_z| at most 1.3e-12 (96 cells, a = 26.3), for
velocities of order 1e-2; Newtonian at most 2e-16 L and 5e-18.
P6: holds. All runs reach a = 42 with every particle kept (no excised, escaped or
unconverged particle in `east.nrpic.hst`), including L = 4 through the crossing; card
time of the first job 17.1 min. With one particle per cell the energy density turns
negative in some void cells after the crossing (E_min = -2.9e-7 at a = 25 against a
mean of 7.6e-6); with two per cell it stays positive.
P7 (two particles per cell and direction, 64 cells): mean H_r 3.2e-5 and 4.2e-5 at
a = 10 and 15 (lower by 4.9 and 30), mean M_r 1.0e-2 and 6.3e-3 (lower by 13 and 33);
|H|/16 pi <E> in the void at a = 15: 6.0e-5 against 6.9e-3 (115 times lower); positions
against Zel'dovich unchanged (3.21e-3 against 3.20e-3 at a = 10). Prediction (more than
5 at a = 10 and 15, more than 10 in the void, positions within 20 percent): holds,
except the Hamiltonian constraint at a = 10, lower by 4.9 instead of more than 5.
What this establishes: before the crossing the constraint violation of the
one-per-cell runs is the cubic cloud's sampling error of the lattice where it is
stretched (the void), not an error of the spacetime solver; two particles per cell and
direction remove most of it. After the crossing it sits at the pancake in both
(|H|/16 pi <E> up to 3e-2 near x = L/4 at a = 21 to 42 with either lattice), and mean
H_r is 1.3e-3 to 2.0e-3 with two per cell.

## Prediction P8: what limits the Newtonian reference (12:24)

The Newtonian error converges at first order (P1). Proposed cause: with one particle per
cell the deposited density carries a ripple at the lattice scale whose size depends on
the compression, not on the cell (TESTLOG, T1a), and one integration turns it into a
force error proportional to the cell size. Test: the Newtonian reference at 32 cells
with two particles per cell and direction (`newton_pancake.py --ppc 2`, 262,144
particles, about 15 min on one core). Prediction: position error at a = 10 below 1.0e-3
(the 64-cell, one-per-cell value) where 32 cells with one per cell gave 2.05e-3; velocity
error below 1.8e-3. Refuted if the position error at a = 10 stays above 1.5e-3, in which
case the force interpolation or the step, not the deposit, sets the error.

## P8 outcome, and the final analysis (12:39)

Run B-emd-gw-20261115-122451-01801f6 (Newtonian, 32 cells, two particles per cell and
direction, 813 s). Position error against Zel'dovich at a = 10: 4.1e-4 (32 cells one per
cell 2.05e-3, 64 cells one per cell 1.02e-3); velocity 3.6e-4 (3.4e-3, 1.8e-3); at a = 15
3.5e-4 and 1.9e-3. Prediction (below 1.0e-3 and 1.8e-3 at a = 10): holds. So the
first-order convergence of the reference at one particle per cell is the lattice
sampling of the deposit, as proposed, not the force interpolation or the step. The
crossing is set by the mesh: 21.41 at 32 cells with two per cell against 21.55 with one
(exact sheets 21.007 and 21.117).
Final analysis B-emd-gw-20261115-123852-ea4475c (supersedes B-emd-gw-20261115-122240-b0e4c9d;
`results/pancake.json`, `results/pancake_profiles.json`). Additional numbers:
- Proper time of the first crossing sheets (relativistic runs; a_p = (1 + 1.5 tau)^(2/3)):
  21.776, 21.348, 21.236 (L = 1 at 32, 64, 96 cells), 21.304 (64, two per cell), 22.280
  (L = 4, 64 cells), against the coordinate labels 21.808, 21.379, 21.267, 21.335, 22.846.
  At equal cells the L = 4 crossing comes 4.4 percent later in the proper time of the
  crossing sheets than the L = 1 crossing (22.280 against 21.348), 6.9 percent later in
  the coordinate label [JUDGEMENT: with relativistic corrections 16 times smaller at
  L = 1, this is the relativistic delay of the crossing at L = 4 to within about 0.5
  percent; the Newtonian proper time at the pancake has not been computed].
- Eulerian density on the mesh (64 cells, L = 1): the Newtonian density equals the deposit
  of the exact Zel'dovich sheets (same cloud, same compensation, Newtonian masses) to
  6.2e-4 at a = 5 and 6.5e-3 at a = 15 (largest over cells); the relativistic energy
  density equals it to 4.8e-3 at a = 5, of which the linear dictionary term -2 psi_N =
  3 (H0/k)^2 d sin kx (amplitude 3.8e-3) accounts for all but 1.1e-3; at a = 15 the
  remainder is 1.7e-2 (nonlinear dictionary terms not modelled). The deposit itself
  differs from the continuum Zel'dovich density by 1.2e-2 (a = 5), 0.21 (a = 15, void) and
  2.5 (a = 20: the peak sits on a cell face, so the continuum density at the nearest
  cell centres has contrast 4.8, while both runs and the deposit of the exact sheets
  put 7.2 into those two cells).
- After the crossing (L = 1, 64 cells) the relativistic and Newtonian sheets differ by
  4.8e-3, 5.1e-3, 4.7e-3 of (a - 1) d/k in position at a = 25, 30, 42, the size of the
  offset before the crossing; at L = 4 by 7.6e-2, 8.0e-2, 7.3e-2. Phase space through
  the crossing: `figs/pancake_phase.png` (inspected: the L = 1 relativistic runs at 64
  and 96 cells lie on the Newtonian spiral; the L = 4 spiral lags).
Figures, all inspected: `figs/pancake_errors.png`, `pancake_profiles.png`,
`pancake_grdiff.png`, `pancake_phase.png`, `pancake_constraints.png`,
`pancake_constraint_profiles.png`, `pancake_ppc.png`, `flrw_recheck.png`.
Card time of the package: 0.284 + 0.197 = 0.48 card-hours.
