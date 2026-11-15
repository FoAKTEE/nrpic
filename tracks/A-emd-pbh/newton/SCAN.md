# First Newtonian scan in AthenaK: design (A-pre-3 under decision 0010)

Status (wave 2, 2026-11-15): sections 1-6 are the wave-1 design, written before the
Newtonian mode existed, and are kept as written. The mode is now in release `core-v0.3`;
the spherical top-hat and the first 14 points of the scan ran in it (section 7, with what
differs from this design), and section 8 proposes the range of the full-relativity scan.
The particle generator still lacks the deformed ball (section 4, item 2; worked around
by `make_deformed_ball.py`, README). Units as in
`PAPER_SETUP.md`: G = c = 1, H_k = 1, t_k = 2/3, Lagrangian radius R_L = 1, patch mass
M = 1/2, r_g = 2GM = 1 (for files in the NRPIC001 convention, M = 1, multiply lengths
and times by 2).

## 1. What a run is

- Patch: homogeneous Lagrangian ball of radius R_L, mass M, deformed by the Zel'dovich
  map at the start a_0 = 1/(2 alpha) (the start of 2605.04487; `PAPER_SETUP.md`), with
  (alpha, beta, gamma) from (delta_L, e, p). Physical positions r_i = a_0 (1 - a_0
  lambda_i) xi_i, physical velocities v_i = H_0 a_0 (1 - 2 a_0 lambda_i) xi_i, H_0 =
  2/(3 t_0), t_0 = t_k a_0^(3/2). Physical coordinates, isolated boundary (multigrid with
  multipole boundary values, which AthenaK's `multigrid/` already has), outflow for
  particles.
- Shell (ball-radius series only): particles at background density in R_L < |xi| <
  R_ball, undeformed, Hubble velocity H_0 r. With this "compensated" construction the gap
  between the deformed patch and the sphere of radius a_0 R_L is empty, the shell's
  enclosed mass equals the background mass, and by the shell theorem the patch evolves as
  the isolated ellipsoid until the shell is tidally distorted or (gamma < 0) overlaps the
  patch. The ball radius then measures tides and late infall, not the first collapse
  [JUDGEMENT, follows from the shell theorem; to be confirmed by the series itself].
- Gravity placements (`ellipsoid.py`): "isolated" is plain Newtonian self-gravity and is
  the Newtonian limit of the expanding ball of track A (FLRW interior, vacuum exterior)
  [JUDGEMENT]. "Added" needs one extra term in
  the code: the external acceleration -(4 pi/3) G rho_b(t) r with rho_b = 1/(6 pi G t^2)
  and t = t_0 + (run time); it is used only to reproduce 2605.04487 (whose printed times
  it matches, `PAPER_SETUP.md`). "Embedded" needs the gap filled at rho_b and is not in
  the first scan.

## 2. Parameter grid

Newtonian dynamics with this start is scale free (validated to 1e-13, JOURNAL.md P7):
at fixed (e, p), times scale as delta_L^(-3/2) and lengths over r_g as 1/delta_L. One
amplitude per shape therefore suffices; the amplitude series is a test of the code.

| Block | Runs | Values |
|---|---|---|
| A shapes | 16 | e in {0, 0.02, 0.05, 0.1, 0.2, 0.3}, p in {-e, 0, +e} (one run at e = 0), delta_L = 0.2, isolated |
| B amplitude | 2 | (e, p) = (0.1, 0): delta_L = 0.05 and 0.6 (with A: three amplitudes) |
| C paper case | 2 | (alpha, beta, gamma) = (0.1114, 0.0667, 0.0219), placement "added" (and "isolated"), N = 10^5 |
| D ball radius | 4 | (e, p) = (0.05, 0) and (0.2, 0): R_ball/R_L = 1.5 and 2 (with A: 1, 1.5, 2) |
| E particles | 4 | same two shapes: N = 10^5 and 3 x 10^5 (with A at 10^6: three values) |
| F mesh | 4 | same two shapes: root cell halved, and one refinement level fewer |

32 runs. Why these shapes: the Newtonian hoop line (section 5) puts delta_L,th below 0.5
for e <~ 0.07 and at 0.86 to 0.97 for e = 0.2 to 0.3 (isolated, p = 0;
`tables/ellipsoid_first_collapse.csv`), so the
full-relativity threshold scan will live at e <~ 0.1; e up to 0.3 brackets it and covers
the paper's cases (e = 0.2 to 0.3). Prolateness enters weakly (dashed and dotted against
solid in `figs/fig_scan_hoop_time.png`), so three values suffice.

## 3. Particle number, ball radius and mesh

Reference geometry, delta_L = 0.2, e = 0.2, p = 0 (isolated; `ellipsoid.py`): a_0 = 4.69,
t_0 = 6.77; semi-axes at the start 2.34, 3.22, 4.10 r_g; first collapse (axis 1) at
t = 16.6 = 2.46 t_0, pancake semi-axes 2.74 and 5.56 r_g; idealized second collapse at
3.19 t_0; largest semi-axis 5.60 r_g. Over the grid the first collapse falls between 1.86
t_0 (e -> 0) and 2.9 t_0 (e = 0.5).

- Run length: to 6 t_0 (the paper's halo is virialized at 50-60 t_k for t_0 = 9.5 t_k,
  i.e. at about 6 t_0, lines 2283 and 2287 of its source).
- Domain: isolated runs half-width L = 1.5 x (largest semi-axis) ~ 2 a_0 R_L (9.4 r_g in
  the reference case); with a shell, L = 1.2 R_ball a(6 t_0)/a_0 ~ 4 R_ball a_0 (the
  shell follows the Hubble flow, a grows by 6^(2/3) = 3.3).
- Mesh: root 128^3 over [-L, L]^3 (cell 0.15 r_g, 16 cells across the short semi-axis at
  the start), two adaptive levels on particle density for the pancake and the
  post-collapse core (finest cell about 0.04 r_g; the virialized radius is about half the
  turnaround radius of the short axis [BACKGROUND, 1609.01588 lines 625-626], 1.2 r_g
  here). Refinement must be capped where a cell holds fewer than about 8 particles: the
  prolate GR run refined on sampling noise at 0.2 particles per cell (docs/TESTLOG.md,
  lines 1149-1162); the existing level cap of the deposition serves the same purpose.
- Particles: N = 10^6 for block A (about 25 particles per root cell inside the patch at
  the start: patch volume 130 r_g^3, root cell 3.2e-3 r_g^3), 10^5 and 3 x 10^5 in block
  E. N = 10^4, the number of the existing GR tests, gives 0.25 per root cell and less
  than 0.01 per finest cell, too noisy for the refinement and for second moments at the
  percent level [JUDGEMENT]. Loading: the flat-space cubic lattice with the surface-layer mass
  correction (its second-moment tensor is isotropic by cubic symmetry, which is what the
  paper's whitening step achieves, PAPER_SETUP.md), with a random rotation of the
  lattice against the deformation axes as a control, since a lattice aligned with the
  pancake plane crosses coherently.
- Ball radius: R_ball/R_L in {1, 1.5, 2} (block D). For the later GR scan the ball must
  be inside the Hubble radius at the start, a_0^(-1/2) R_ball/R_L < 1, i.e.
  delta_L (1 + 3e + p) < 1.5 (R_L/R_ball)^2. With R_ball = 2 R_L that is delta_L < 0.33
  at e = 0.05 and < 0.29 at e = 0.1 (p = 0), below the Newtonian hoop line there (0.36,
  0.59): the threshold is out of reach; R_ball = 1.5 R_L allows 0.58 and 0.51, R_ball =
  R_L allows 1.30 and 1.15 [follows from the tables; the hoop line itself is a Newtonian
  proxy]. The ball radius of the GR scan is therefore limited by the horizon, and block
  D tells how small it may be. A later start relaxes the limit: the homogeneous-ellipsoid
  state at any a_0 before the first collapse is available from `ellipsoid.evolve` and is
  exact for the cold patch, unlike the Zel'dovich map, which degrades after turnaround
  [JUDGEMENT].

## 4. Inputs the runs need

1. The Newtonian mode (core, `core/newton`): Newtonian gravity of the same particles and
   clouds with isolated boundary values; optional external acceleration of placement
   "added"; optional special-relativistic kinematics (push u = gamma v with du/dt =
   -grad Phi), because the correction is 4-5 percent at delta_L = 0.3 and 13-17 percent at
   delta_L = 1 (`tables/sr_estimate.csv`; the paper applies it to the peculiar velocity
   only).
2. A particle file with the deformation. `problems/ic/make_ic.py` cannot write it. It
   lacks:
   - a model for a homogeneous ball in flat space: its models are `os`, `st`, `prolate`,
     `jeans` (make_ic.py line 67); the ball sampler `sampling.sample_os` (sampling.py
     line 117) samples Oppenheimer-Snyder dust in isotropic coordinates, weighted by
     psi^6, at rest (u_i = 0);
   - the Zel'dovich map of positions with (alpha, beta, gamma) or (delta_L, e, p) and a
     start a_0 (default 1/(2 alpha)), and the velocity field v_i = H_0 a_0 (1 - 2 a_0
     lambda_i) xi_i (Hubble plus peculiar); for the GR data, the covariant u_i of the
     A-pre-1 slicing instead;
   - an optional background shell R_L < |xi| < R_ball with Hubble velocity, and a
     species id that separates patch and shell;
   - an option to rotate the lattice against the deformation axes, and the centring of
     the sample (centre of mass and net momentum to zero, as the paper does, its lines
     1067-1076; make_ic.py removes the net momentum only for `st` and `jeans`, line 263);
   - the paper's units (M = 1/2, r_g = 1) or a documented factor to the NRPIC001
     convention (M = 1), and JSON metadata that records a_0, t_0, H_0, t_k, (alpha, beta,
     gamma), (delta_L, e, p), R_L, R_ball, the placement, and the reference times of this
     directory (t_1, t_2, h_1 from `ellipsoid.first_collapse`), so that every run carries
     its own prediction.
   Writing this model is core's (decision 0010: initial data are fed by
   `problems/ic/`); the formulas and the reference values are here.
3. Output: particle snapshots (`<base>.part.NNNNN.bin`, docs/FORMATS.md line 44) every
   t_0/20 and at the predicted collapse times, the history file, and (requested, not
   required) the mass-weighted second-moment tensor of each species in the history, so
   that the semi-axes need no snapshots.

## 5. Quantities to record and the references they are judged against

| Quantity | From | Reference |
|---|---|---|
| semi-axes A_i(t) = sqrt(5 lambda_i(C)), C the second-moment tensor of the patch about its centre of mass; also of the inner 90 percent of the mass | snapshots or history | `ellipsoid.evolve`, placement of the run |
| times t_1, t_2 of the first minima of the semi-axes (first and second collapse), and the axis | same | `tables/ellipsoid_first_collapse.csv` (scaled by delta_L^(-3/2)) |
| hoop proxy h(t) = (perimeter of the ellipse of the two largest A_i)/(2 pi r_g), its value at t_1 and its minimum | same | same table; Zel'dovich h of 1609.01588 (its Eq. s_3) |
| compactness max_r 2 G M(<r)/r about the density maximum, after t_1 | snapshots | 1 for a horizon (Newtonian proxy only) |
| half-mass radius and virial ratio 2K/|W| after t_1; time of virialization | snapshots | paper: virialized at about 6 t_0 |
| energy and momentum conservation, centre of mass | history | exact (for "added", including the work of the external term) |
| quadrupole Q_ij(t) of the patch | snapshots | for track B and the GW of 2605.04487 |
| spherical control (e = 0): turnaround and collapse | snapshots | cycloid, `tophat.za_tophat_summary`: t_c = 1.833 t_0 from the turnaround start |

Acceptance of the Newtonian mode by this track (independent check of core's
implementation): (i) e = 0 collapses at the cycloid time within 0.5 percent at N = 10^6
on the 128^3 mesh; (ii) the first-collapse time of every block-A shape agrees with the
isolated ellipsoid within 1 percent, and t_1 delta_L^(3/2) is the same for the three
amplitudes of block B within 0.5 percent; (iii) "added" on the paper case gives t_1 and
t_2 within 1 percent of 22.733 and 29.126 (our reference) and therefore within about 1-4
percent of the paper's 22.536 and 29.097; (iv) energy conserved to 1e-3 until t_1. These
tolerances are proposals [JUDGEMENT]; the resolution blocks E and F decide whether they
can be met.

## 6. Cost

Measured costs of the existing code (full relativity, one A100):

- Z4c on a uniform 128^3 mesh: 2.0e7 zone-cycles/s; particle work adds about 3 percent
  at 10^4 particles (docs/TESTLOG.md, lines 44-48).
- Dust collapse to 60 M with adaptive mesh, 9328 particles: 5345 cycles, 456 MeshBlocks
  of 16^3 at the end, 1116 s, 8.8e6 zone-cycles/s (run `os/adapt_sc`,
  `runs/os/adapt_sc/athena.log` lines 290-302; docs/TESTLOG.md line 626 gives "ten
  minutes" for the collapse of the sibling run).
- Prolate collapse to 45 M, 10^4 particles, finest cell M/16: 2128 cycles, 1184
  MeshBlocks, 1719 s = 0.48 card-hours, 6.1e6 zone-cycles/s (docs/TESTLOG.md lines
  1527-1552; `runs/prolate/e09_v8/athena.20261113-125024.log` lines 131-140).

Estimate for one Newtonian run of block A [JUDGEMENT on the step cost]: the mesh work of
a Newtonian step (deposit, one multigrid solve, push) is taken to be at most that of one
Z4c RK4 step on the same mesh, so the measured Z4c rates are an upper bound. Cells:
128^3 root plus two levels over about 1/8 and 1/64 of the volume, about 6e6 cells. Steps:
the particle limit dt = 0.5 dx_finest / v_max with v_max ~ 0.5 c gives dt ~ 0.04 r_g/c
over a run of 5 t_0 ~ 34 r_g/c (reference case): about 900 cycles (a light-speed limit
dt = 0.25 dx, as in the GR runs, would be four times more). Zone-cycles 5e9; at 6e6 to
2e7 per second, 4 to 15 minutes, i.e. at most 0.25 card-hours per run. Particles: 10^6
particles at the measured GR particle cost (3 percent of a 128^3 step per 10^4
particles, about 3e-7 s per particle and cycle) would add 300 s; the Newtonian push is
cheaper (no implicit iteration, no metric interpolation), so at most another 0.1
card-hours. Per run at most 0.35 card-hours; 32 runs at most 11 card-hours. A scouting
pass of block A at 64^3 root and N = 10^5 costs about a tenth of that (about 1
card-hour), or can run on processors with the CPU executable (its zone-cycle rate is
not in docs/TESTLOG.md [TO VERIFY] before such a pass is planned).

The full-relativity scan of track A is costed separately by the scope package (commit
6c880de, about 155 card-hours); this Newtonian scan is what fixes its e range, particle
number and ball radius.

## 7. First points in the code (wave 2)

Runs (all registered under `../runs/`; predictions and outcomes in `JOURNAL.md` entries
5-8): cost A-20261115-152758-1579711; top-hat A-emd-pbh-20261115-153409-dc27b98; scan
A-emd-pbh-20261115-153415-dc27b98; card A-emd-pbh-20261115-153437-dc27b98 (particle files
A-emd-pbh-20261115-153424-dc27b98); analysis A-emd-pbh-20261115-164420-4528861; range
A-emd-pbh-20261115-164757-b8bc9a3. Executables: release `core-v0.3`
(`.work/build_cpu_v03/src/athena`, one core per case; `.work/build_gpu_v03/src/athena`, one
A100). Deck `problems/newton/isolated.athinput` with overrides only: isolated domain,
multipole boundary (order 4), cloud-in-cell, no filter, `newton_cfl = 0.2`,
`newton_mg_tol = 1e-6`, step cap t_run/400, a history record every cycle.

**What differs from sections 1-6.** Uniform 128^3 mesh, no refinement levels (the
refinement of the Newtonian mode is a trial only, interface section 6); 2.7e5 particles
(lattice spacing hxi = 0.025 R_L) instead of 1e6, with 3.4e4 and 2.1e6 as the particle
series; no shell (block D not run); no "added" placement and no SR kinematics (the mode
has neither; acceptance (iii) not run); the e = 0 point is replaced by an expanding
top-hat that turns around (the paper's start has every axis at rest, the cold collapse
core already tested). The second-moment tensor comes from the history file (every cycle),
not from snapshots.

**Spherical top-hat against the cycloid.** Zel'dovich sphere lambda = 0.1 at a0 = 1
(R0 = 0.90, expands to R_max = 2.12, turnaround t = 4.86, collapse 9.72; each case uses the
cycloid of its own lattice ball). Signed relative errors (`tables/newton_tophat.csv`,
`figs/fig_newton_tophat.png`, `fig_newton_tophat_conv.png`):

| mesh | particles | t_ta | R_max | t at R = 0.25 R_max | softened collapse (min R) | R_min/dx |
|---|---|---|---|---|---|---|
| 32^3 | 2.7e5 | +1.44e-2 | +8.6e-3 | +2.01e-2 | +6.2e-3 | 2.4 |
| 64^3 | 2.7e5 | +3.15e-3 | +1.87e-3 | +3.82e-3 | +1.03e-3 | 2.2 |
| 128^3 | 2.7e5 | +7.16e-4 | +4.31e-4 | +8.39e-4 | +2.59e-4 | 2.1 |
| 128^3 | 2.1e6 (card) | +7.22e-4 | +4.36e-4 | +8.28e-4 | +2.50e-4 | 2.0 |
| 128^3 | 3.4e4 | +1.98e-3 | +1.05e-3 | +3.27e-3 | +1.65e-3 | 3.5 |
| 128^3 | 4.2e3 | -6.4e-4 | +5.0e-3 | +1.51e-2 | +1.19e-2 | 7.9 |

Second order in the mesh (factors 4.0-6.1 per doubling over the four quantities) once the lattice spacing stays
below about one cell (2.7e5 and 2.1e6 particles agree to 1e-5); with fewer particles the
lattice, not the mesh, sets the error. The step is not limiting (cfl 0.1 changes t_ta by
8e-5); energy holds to 9.5e-5 at 128^3. Acceptance (i) of section 5 (collapse within 0.5
per cent at 128^3): met, +0.026 per cent.

**Scan points against the isolated ellipsoid.** Paper start a0 = 1/(2 alpha), 128^3 over
+-1.5 A_max, 2.7e5 particles, to 1.35 t_1 (`tables/newton_scan.csv`,
`figs/fig_newton_scan_axes.png`, `fig_newton_scan_dev.png`, `fig_newton_scan_summary.png`,
snapshots `fig_newton_snap_e0p2.png`, `_e0p2_pm.png`, `_e0p05.png`). Relative errors at
the first collapse t_1 (vertex of the second moment of the collapsing axis), of the two
other semi-axes at t_1, of the hoop ratio h_1, and of the second collapse t_2:

| delta_L | e | p | t_1 ref [t_k] | t_1 | A_2(t_1) | A_3(t_1) | h_1 | h_1 delta_L (run / ref) | t_2 |
|---|---|---|---|---|---|---|---|---|---|
| 0.2 | 0.05 | 0 | 34.16 | +2.9e-4 | +1.2e-3 | +4.1e-4 | +6.1e-4 | 0.3597 / 0.3594 | +3.1e-4 |
| 0.2 | 0.1 | 0 | 30.70 | +2.2e-4 | +6.1e-4 | +1.5e-4 | +2.7e-4 | 0.5925 / 0.5924 | +4.0e-4 |
| 0.2 | 0.2 | 0 | 24.95 | +3.7e-4 | +4.5e-4 | +1.3e-4 | +2.1e-4 | 0.8547 / 0.8545 | +5.6e-4 |
| 0.2 | 0.3 | 0 | 20.64 | +6.3e-4 | +5.1e-4 | +1.6e-4 | +2.5e-4 | 0.9685 / 0.9682 | (after end) |
| 0.2 | 0.2 | +0.2 | 22.10 | +2.9e-4 | +1.1e-4 | +1.1e-4 | +1.1e-4 | 0.9194 / 0.9193 | (after end) |
| 0.2 | 0.2 | -0.2 | 27.57 | +1.5e-3 | 0.031 r_g (ref 0) | +2.5e-4 | +3.2e-4 | 0.8636 / 0.8633 | (= t_1) |
| 0.05 | 0.1 | 0 | 245.6 | +2.2e-4 | +6.1e-4 | +1.5e-4 | +2.7e-4 | 0.5925 / 0.5924 | +4.0e-4 |
| 0.6 | 0.1 | 0 | 5.908 | +2.2e-4 | +6.1e-4 | +1.5e-4 | +2.7e-4 | 0.5925 / 0.5924 | +4.0e-4 |

Controls at e = 0.1 / 0.2: 64^3 gives t_1 errors +8.8e-4 / +1.5e-3 (second order: factors
3.9 / 4.2 to 128^3); 3.4e4 particles -2.4e-4 / -4.6e-4; 2.1e6 particles (e = 0.2, card)
+3.7e-4 (9e-6 from 2.7e5); a lattice rotated at random against the axes (e = 0.2)
+3.7e-4 (4e-6 from the aligned lattice). The three amplitudes are one computation in
scaled units and agree to 5e-7. Acceptance (ii) of section 5 (t_1 within 1 per cent; the
amplitude series within 0.5 per cent): met, with margins of 16 (e = 0.05-0.3) and 6.6
(spindle). Acceptance (iv)
(energy within 1e-3 until t_1): met to 0.9 t_1 (<= 1.9e-4), failed at the crossing
itself (1.1e-3 to 9.3e-3; 3.0e-2 for the spindle), when the pancake is thinner than a
cell; cause not established (JOURNAL entry 8). After the third collapse (e = 0.05 near
1.08 t_1, e = 0.1 near 1.22 t_1) the runs leave the pass-through reference and relax
violently; for e = 0.05 0.64 per cent of the mass leaves the box. The reference times in
t_k are those of the sampled ball (R_vol = 1.000017) and differ from
`tables/ellipsoid_first_collapse.csv` (nominal radius) by about 1.5e-5.

**Cost.** Processors (one core per case, machine load 18-66): 2.8 s per cycle at 128^3
with 2.7e5 particles, 9.5 s with 2.1e6, 13.3 s at 256^3 with 2.7e5; a scan point at
128^3 takes 400-850 cycles, 20-42 minutes. Card: 0.37 s per cycle at 128^3 with 2.1e6
particles; the three card cases took 607 s, 0.169 card-hours. Total of this package:
0.169 card-hours and 7.4 core-hours of case run time (10.0 core-hours reserved).

## 8. Proposed range of the full-relativity scan

From `tables/gr_scan_range.csv` (run A-emd-pbh-20261115-164757-b8bc9a3; reference values
of the isolated ellipsoid at the Newtonian hoop amplitude delta_L,th = h_1 delta_L, the
amplitude at which the pancake's hoop equals 2 pi r_g at the first collapse; "run" values
from the 128^3 scan above) and `figs/fig_newton_gr_range.png`.

| e | p | delta_L,th ref (run) | SR delay of t_1 | Newtonian infall speed at t_1 | t_1/t_0 | R_ball max at paper start / at t_1 | dx/M for the 128^3 resolution | seeds of delta_L |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 0 | 0.3594 (0.3597) | 6.0 % | 1.24 c | 2.05 | 1.90 / 2.42 R_L | 0.111 | 0.180 0.252 0.359 0.503 0.719 |
| 0.1 | 0 | 0.5924 (0.5925) | 8.7 % | 1.17 c | 2.22 | 1.40 / 1.82 | 0.075 | 0.296 0.415 0.592 0.829 1.185 |
| 0.2 | 0 | 0.8545 (0.8547) | 11.5 % | 1.09 c | 2.46 | 1.05 / 1.41 | 0.061 | 0.427 0.598 0.854 1.196 1.709 |
| 0.3 | 0 | 0.9682 (0.9685) | 12.6 % | 1.05 c | 2.63 | 0.90 / 1.25 | 0.062 | 0.484 0.678 0.968 1.355 1.936 |
| 0.2 | +0.2 | 0.9192 (0.9194) | 11.8 % | 1.01 c | 2.60 | 0.95 / 1.31 | 0.047 | 0.460 0.643 0.919 1.287 1.838 |
| 0.2 | -0.2 | 0.8633 (0.8636) | 13.7 % | 2.3 c (spindle) | 2.22 | 1.11 / 1.45 | 0.074 | 0.432 0.604 0.863 1.209 1.727 |

What the Newtonian precursor fixes [each item follows from the runs and tables named]:

1. **The code is a valid Newtonian baseline over the whole shape range.** At 128^3 with
   2.7e5 particles the Newtonian mode reproduces the cold ellipsoid to <= 6.3e-4 in t_1
   and <= 6.1e-4 in h_1 for e = 0.05-0.3, |p| <= e, second order in the mesh, converged in
   particle number. Differences between a full-relativity run and its Newtonian twin at
   the per-cent level are therefore physics, not the Newtonian side's error.
2. **The amplitudes to scan.** The hoop amplitude rises from 0.36 (e = 0.05) to 0.97
   (e = 0.3); it is where the Newtonian solution stops being valid (infall speed of the
   short axis at the first collapse above c for every shape), so it marks the region, not
   the threshold [JUDGEMENT]. Proposed seeds: delta_L,th x {0.5, 0.7, 1, 1.4, 2} per
   shape (last column), then bisection in ln delta_L to a ratio 1.1 (`../scope/SCOPE.md`
   section 3). The factor two either way covers the end-point SR delay (6-14 per cent in
   t_1) and leaves room for an order-one relativistic shift [JUDGEMENT]. All seeds lie
   above the finite-duration cutoff (t_H/t_end)^(2/3) = 0.025 for t_end = 250 t_H
   (`../scope/SCOPE.md` section 3; arithmetic).
3. **Shapes.** e in {0, 0.05, 0.1, 0.2, 0.3} at p = 0 and p = +-0.1 at e = 0.2, as in
   `../scope/SCOPE.md` section 5. The Newtonian runs at p = +-0.2 bracket them; p = -e is a
   spindle (two axes collapse together, the Newtonian infall speed grows without bound) and
   is a separate class, not an end of the p axis [JUDGEMENT].
4. **Amplitude convention.** delta_L = alpha + beta + gamma is the linear contrast at t_k
   of a top-hat patch whose Lagrangian radius is the horizon at t_k (`PAPER_SETUP.md`,
   2605.04487 lines 1105-1136). For a top-hat it is the mean linear contrast inside the
   patch at horizon entry, i.e. deltabar_ent of `../scope/SCOPE.md` section 3 with
   r_m = R_L [JUDGEMENT]. For the Gaussian profile of arXiv:2609.14218 the scope's
   conversion deltabar_ent = 0.883 mu applies; thresholds of different profiles are not
   interchangeable, so these seeds place the top-hat (ball) runs and serve the periodic-box
   line only as a range.
5. **Run length.** The first collapse comes at 2.05-2.63 t_0 after the paper's start
   (t_0 = t_k a0^(3/2)), the second at 1.04-1.51 t_1 (reference); a full-relativity run
   from that start needs at least 3 t_0 to pass the first collapse, and about 6 t_0 for
   the virialised state (section 3).
6. **Resolution.** The 128^3 runs had 13-33 cells across the short semi-axis at the start
   (error <= 6.3e-4; 64^3, 9-13 cells at e = 0.2 and 0.1, <= 1.5e-3) and a lattice
   spacing of half a cell.
   At the hoop amplitude the same resolution is dx = M/9 (e = 0.05) to M/21 (e = 0.2,
   p = +0.2) over the patch at the start, M the patch mass (column dx/M), and the pancake
   reaches 0.1-0.4 of that cell at the crossing. For comparison: the first scouting runs
   SR-1/SR-2 use dx = M/2 and the prolate full-relativity test reached M/16 on its finest
   level (`../stage/G1/STATUS.md` section 3; section 6 above). Particles: >= 2.7e5 per
   patch on a lattice; more does not change the Newtonian timing (2.1e6: 9e-6), so the
   particle number of the GR scan is set by the noise near threshold (scope section 5),
   not by the Newtonian side.
7. **Set-up.** The expanding ball holds the hoop amplitude at the paper's start only for
   R_ball < 1.90, 1.40, 1.05, 0.90 R_L (e = 0.05-0.3), and even with a start delayed to
   just before the first collapse (exact ellipsoid state) only for R_ball < 2.42, 1.82,
   1.41, 1.25 R_L (a background shell has R H = a^(-1/2) R_ball). A compensating shell of
   1.5 R_L therefore fits for e <= 0.1 only, and only with a later start. This supports
   decision 0013 (threshold line in the periodic box); the ball remains the set-up for
   isolated comparisons at e <= 0.1 and for amplitudes below the hoop line.

Not established here: the tidal and late-infall effect of a shell (block D), the
"added" placement and the SR push (not in the mode), refined meshes in the Newtonian mode,
and the energy through and after the crossing.
