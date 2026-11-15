# First Newtonian scan in AthenaK: design (A-pre-3 under decision 0010)

Status: proposal; nothing of it has run in the code. The Newtonian mode does not exist
yet (branch `core/newton` had no commit beyond `main` when this was written), and the
particle generator lacks the deformed ball (section 4). The scan runs in AthenaK's
Newtonian mode once core has written it; until then the semi-analytic references of this
directory are the only Newtonian results, and the full-relativity scouting runs wait for
the expanding-ball initial data (A-pre-1, `core/id-extrinsic`). Units as in
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
  the Newtonian limit of the expanding ball of track A. "Added" needs one extra term in
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
