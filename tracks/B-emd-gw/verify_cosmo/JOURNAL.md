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
