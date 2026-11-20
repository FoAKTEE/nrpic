# JOURNAL of es_runs (helper package of D-bh-dress, wave 2)

Predictions are written before each test and are not edited afterwards; outcomes are
appended below them, also when a prediction failed. Paths relative to
`tracks/D-bh-dress/`; run ids are `nrpic-run` ids (manifests in `runs/<run_id>/`).

## Entry 1 (2026-11-15): data sets ES (outer dust edge at 60 M) and V-1, offline check

Task: regenerate the Einstein-Straus data set with the outer dust edge at 60 M as the
lead decided (`HANDOFF.md`, `stage/G1/STATUS.md`: `make_es.py --Rb 56 --w_out 4`, hp = 1 M)
and build the matched vacuum table V-1 ("the same table without dust, the f-slice of a
single Schwarzschild hole, Painleve-Gullstrand beyond 36 M"). Tool: `es_runs/make_data.py`
(calls `einstein_straus/make_es.py` with its figures redirected into the run directory;
V-1 is `es_model.EinsteinStrausBH` with `matched = False, rho0 = 0`).

Predictions (before the registered run):
- D1. Dust between R = 36 and 60 M; total mass M_tot = 2.74 +- 0.01 M [JUDGEMENT: the
  plateau is matched, m = (R/40)^3 M on it, and the symmetric smooth edge about Rb = 56 M
  acts nearly as a sharp edge at 56 M: (56/40)^3 = 2.744]. Plateau H = 5.5812e-3/M, the
  same as the wave-1 data set (the matched rho_0 depends only on Rw, w_in; es.json of
  D-bh-dress-20261115-043445-b782009). Particle number 7.09e5 +- 1 per cent (lead's
  estimate 709346, `analysis/lead_checks/first_run_plan.json`). Lattice dust mass equal
  to the continuum mass to better than 1e-6 (wave-1 data: 2.8e-8).
- D2. Bare puncture mass m_p = 1.0239688282062387 and u(0) unchanged (they depend only on
  f and M inside 36 M), for ES and V-1 alike; the 140 tracers of V-1 at the same
  positions as in ES (difference below 1e-12 M).
- D3. Exact crossing times of R = 2M for the tracer groups at R0 = 6 and 10 M equal to
  those of the wave-1 data set (same f and m = M inside 36 M); the lead quoted 15.0 and
  34.6 M, read off the 0.2 M grid of `es_reference.csv` (first grid point at or below
  2M), so the interpolated values lie at most 0.2 M below them.
- D4. Offline check (`einstein_straus/offline_check.py` through `es_runs/tools/
  offline_check_es.py`, figures redirected): the 1D and 3D residuals of ES fall at fourth
  order (measured orders between 3.5 and 4.5 in every region and sub-box with resolved
  residuals, as 3.85-4.07 in run D-bh-dress-20261115-042704-f3da881); the table
  interpolation error below 1e-6 of the field scale. V-1, same checks with rho = 0:
  the same orders. Refuted by an order below 3 in any region with residuals above the
  round-off floor (then the new edge at 52-60 M is under-resolved by drbar = 0.02 or the
  generator is wrong for rho = 0).

Outcome of entry 1 (runs D-20261115-170213-d2c2131 data, D-20261115-170234-f9b7f03 check;
`results/predictions.json`, `results/offline_check_summary.json`; figures
`figs/data_compare.png`, `figs/offline_check_1d_es.png`, `figs/offline_check_3d_es.png`,
looked at):
- D1 mostly held. M_tot = 2.73967 M, H = 5.58116e-3/M as predicted; lattice dust mass
  1.7396724 M against the continuum 1.7396725 M (relative -9.0e-8). The particle number
  FAILED the 1 per cent band: 696688 dust particles (+140 tracers) against 7.09e5
  (-1.8 per cent). Cause found by reading `es_model.smooth_step`: S(x) = (1 - tanh(g/2))/2
  is exactly 0 in double precision for g > ~37, i.e. within ~0.2 M of each edge of the
  shell, and the lattice keeps only sites with rho > 0; the shell 36.21 < R < 59.79 M has
  volume 6.96e5 M^3. The mass in the dropped zones is below e^-37 of the plateau density;
  no consequence. [VERIFIED by the numbers above; the volume by hand]
- D2 held: m_p = 1.0239688282062387, u(0) = -0.023407771355917872 in both tables; the V-1
  tracers sit at the ES positions (largest difference 0.0).
- D3 held: exact crossings of R = 2M at tau = 14.83 M (R0 = 6 M) and 34.44 M (R0 = 10 M)
  in both data sets (fine tau grid); the lead's 15.0 and 34.6 are the next points of the
  0.2 M grid. Group R0 = 20 M crosses at tau = 244.7 M; the other groups do not fall in.
- D4 held, with one coarse pair below my band. ES 1D: transition H orders 3.92-3.98,
  M 3.80-3.99; inner dust edge M 3.44, 3.61, 3.85; outer dust edge M 3.41, 3.63, 3.84
  (h = 0.8 to 0.1 M; the new 8 M wide outer edge is pre-asymptotic at h = 0.8 M; the
  refutation threshold 3 is not reached); H in the dust at round-off (2e-16 relative: the
  slice satisfies the Hamiltonian constraint identically there). ES 3D: residuals fall by
  16-17 per halving in every sub-box with resolved residuals (orders 3.9-4.1), exact and
  table fields alike. V-1: M orders 3.99-4.00 in all regions beyond the transition. Table
  interpolation error: u 6.5e-13, KL 1.1e-9, KT 3.3e-11 of the column maximum; alpha
  4.5e-6 at rbar = 0.01 M (not used: the runs start from the precollapsed lapse).

## Entry 2 (2026-11-15): ES-1 and V-1 at M/8, release card executable, 1+log gauge

Configuration (decided before submission; `inputs/es1_dx8.athinput`, `inputs/v1_dx8.athinput`,
identical apart from basename, table and particle file): data of run
D-20261115-170213-d2c2131; card executable `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`
(release core-v0.3); MeshBlocks of 24^3 cells so that the refined regions end where the
specification asks (16^3 blocks snap them out to +-128 and +-64 M: 1280 blocks, measured in
the processor smoke run D-20261115-170326-dfb2a02, which is superseded); root dx = 4 M on
+-192 M (outflow), dx = 2 M on +-96 M, dx = 1 M on +-48 M (so the whole dust is at
dx <= 2 M and the wall and inner edge at 1 M), M/2 on +-24, M/4 on +-12, M/8 on +-6 M;
344 MeshBlocks (smoke run D-20261115-172413-6412daf). Gauge: the gauge that exists, 1+log
(d_t alpha = -2 alpha Khat + advection) with the Gamma-driver (eta = 2), as D-pre-4;
initial lapse precollapsed (psi^-2 of the full psi), zero shift. Finder: D-pre-4
production settings. Particles: midpoint pusher, Hermite metric interpolation, CIC with one
binomial pass, alpha_exc = 0.05, ah_exc_factor = 0.8. Tracers: the 140 tracers carry
m = 1e-30 (> 0), so the code pushes them as timelike geodesics; a zero mass would make
them null particles in this source (`athenak/src/particles/nrpic.cpp:454-460`: "a
particle without rest mass follows a null geodesic", eps = 0 for m = 0). That is my
reading of the "mis-pushed massless tracers" of `outbox/*tracer-push-release-build.md`
(the six tracers of `problems/puncture/horizon_calib.athinput` have p<n>_m = 0.0):
[TO VERIFY] by a run with m = 0 and m > 0 side by side; not a defect of the push if so.
So the wall is measured with massive tracers on the card, not with the processor
executable. tlim = 200 M coordinate time, two chain segments allowed per run.

Predictions of `stage/G1/STATUS.md`, copied before submission (verbatim, not to be changed):

> 1. M_AH(t)/M_AH(t0) - 1 stays within the floor of V-1 for 100 <= t <= 200 M; with the
>    D-pre-4 floor as the guide, |M_AH(t)/M_AH(100 M) - 1| <= 3e-5 at M/8 (D-pre-4 gives
>    2.8e-5 from t0 = 100 M before 210 M). Exact value: M_AH = M on every spherical slice
>    (Birkhoff in the vacuum bubble; the mass inside the comoving wall is constant).
>    [JUDGEMENT] The level: M_AH(100 M) - M = +1.5e-3 +- 3e-4 at M/8, the finder offset of
>    the bare puncture at this resolution (D-pre-4: +1.50e-3 at 100 M), if the interior
>    evolves as a bare puncture.
> 2. The wall tracers (tags 56-69, areal radius from the metric at the particle against
>    their proper time) follow R_w(tau) = (36^(3/2) + (3/2) 2^(1/2) tau)^(2/3) M: 46.99,
>    56.80, 65.84, 74.29 M at tau = 50, 100, 150, 200 M (`es_reference.csv`), to 3e-3 at
>    dx = 1 M (core test 2 measured 3.3e-3 at dx = 1 M in the conformal-time gauge).
> 3. The tracer groups at R = 6 M and 10 M (tags 0-27) reach R = 2M at tau = 15.0 M and
>    34.6 M and are removed; the group at 20 M turns around at about 27 M and falls in at
>    tau = 245 M (after the run); no dust particle enters R < R_w(tau).
> 4. With 1+log slicing the lapse in the dust plateau rises as 1 + 6 ln a, to about 4.9 by
>    tau = 200 M (a = 1.93); a front from the dust edges may reach the hole (core test 2).
> Refuted by: a horizon-mass change in ES-1 larger than in V-1 by more than 3 times V-1's
> floor (then the dust couples to the hole numerically: through the gauge, the deposit or
> the boundary), or a wall tracer off the exact curve by more than 1 per cent (then the
> push or the expansion is wrong; compare R1, the tracer finding of D-pre-4).

Additions of this package, written before submission (numbers from `results/predictions.json`
of run D-20261115-170213-d2c2131 unless stated):
- A1 (to 3) exact crossing times are 14.83 and 34.44 M (entry 1, D3); I take "reach R = 2M
  at the exact time" as within 0.5 M [JUDGEMENT] and refuted beyond 1.5 M. Whether group
  R0 = 20 M falls in during the run depends on the lapse along it: K is largest in the
  curvature transition (K ~ -0.03/M near rbar = 15-25 M, `figs/data_compare.png`, against
  -3H = -0.017/M in the plateau), so with 1+log its proper time may run ahead of t and
  reach 244.7 M before t = 200 M; no prediction on that.
- A2 (to 4, against coordinate time) the homogeneous 1+log model with zero shift
  (d tau/dt = alpha = 1 + 6 ln a) gives in the plateau alpha = 2.10, 3.58, 6.59, 8.97,
  10.76 and tau = 38, 108, 364, 756, 1251 M at t = 25, 50, 100, 150, 200 M: the dust is
  evolved far beyond tau = 200 M within 200 M of coordinate time. The plateau probe
  (x = 46 M) follows the model within 20 per cent to t = 50 M and departs later, when the
  edges (8 M away) have been in causal contact for many crossing times [JUDGEMENT].
  Initial slope d alpha/dt at 48 M: 0.0335/M (ES-1), 0.0128/M (V-1, Painleve-Gullstrand
  K), to 10 per cent over t <= 5 M.
- A3 near the hole (probe x = 1 M, minimum on the mesh): the precollapsed lapse falls to
  the trumpet; the minimum stays below 0.05 (0.031 at t = 0, smoke run); the lapse at
  x = 1 M agrees between ES-1 and V-1 to 1e-3 until a signal from the dust (36 M away)
  can arrive (t ~ 25 M at the gauge speed sqrt(2 alpha) ~ 1.4) [JUDGEMENT].
- A4 the wall in V-1 follows the same exact curve (test particles at R0 = 36 M with E = 0
  around M), to the same 3e-3; groups 5-9 of V-1 follow (R0^(3/2) + 1.5 sqrt(2) tau)^(2/3),
  those of ES-1 their LTB curves with m(R0) (es_model.ltb_radius). Criterion 2 (1 per cent)
  is judged for tau <= 200 M; beyond it I record the deviation without a criterion.
- A5 technical: no non-finite history (column 3 never drops to 0); particle loss only by
  excision of the infalling tracer groups (28 tracers of groups 0-1, 14 more if group 2
  falls in) and none through the boundary (the outermost tracers start at 78 M, the box
  ends at 192 M, the shift is small in the dust); push_unconverged = 0.
- A6 cost: 344 blocks of 13824 cells = 4.76e6 cells, 6400 cycles; at the 9.6e6
  zone-cycles/s of the D-pre-4 card runs (D-bh-dress-20261115-121313-284ec4f, segment log)
  0.88 card-hours per run plus the particles (0.15 card-hours for 7e5 particles, scoping
  model): ES-1 1.0, V-1 0.9 card-hours, 1.9 together, inside the 2.5 card-hours of the
  package [JUDGEMENT].

## Entry 3 (2026-11-15): does p<n>_m = 0 make a null particle in the release executables?

Question (from entry 2): the wave-1 finding "massless tracers are mis-pushed by the release
card executable" (outbox tracer-push-release-build) may be the light-ray convention of the
current source (`nrpic.cpp:454-460`: m = 0 pushes a null geodesic), not a push defect.
Test (`tools/tracer_mass_check.py`, processor executable of release core-v0.3, cheap):
`problems/kerr/geodesic_mesh.athinput` (the verified Kerr geodesic of the paper, static
mesh metric, midpoint pusher; its p0_m = 0.0) for 30 M, as it is and with
particles/p0_m = 1e-30.
Prediction: with m = 1e-30 the particle stays on its bound orbit (Boyer-Lindquist r
between about 5 and 10 M over 30 M); with m = 0 it moves off at a coordinate radial speed
near 1 and is beyond r = 25 M by t = 30 M. Refuted if the two trajectories agree (then
m = 0 is not the cause, and the card-executable defect stays open as reported).

Outcome of entry 3 (run D-20261115-172821-f800e34, `results/tracer_mass_check.json`,
`figs/tracer_mass_check.png`, looked at): the dichotomy is confirmed, the details of my
prediction are not all testable. With p0_m = 1e-30 the particle stays on its orbit
(Boyer-Lindquist r = 8.000 -> 8.097 M over 30 M, coordinate radial speed below 0.006, 6002
records). With p0_m = 0, as the verified input has it, it leaves the orbit at once and
accelerates outward (radial coordinate speed 0.26 -> 0.58) and leaves the mesh (|z| = 5 M)
at t = 9.8 M at r = 12.3 M, so "beyond 25 M by 30 M" could not be observed and "speed near
1" is not what the radial component shows (the null ray keeps a large tangential
component). [VERIFIED on the processor executable of release core-v0.3] In this source a
zero rest mass makes a null particle; the six tracers of
`problems/puncture/horizon_calib.athinput` and the geodesic of
`problems/kerr/geodesic_mesh.athinput` carry p<n>_m = 0.0 and are therefore light rays now,
which matches the wave-1 observation on the card (five tracers moving out together near
light speed). [JUDGEMENT] The card executable runs the same source, so the wave-1 blocker
is an input convention that changed when light rays were added, not a mis-push; the
card's push of massive tracers is checked by ES-1 itself. Request to core: positive
p<n>_m in those two inputs (or an explicit option for null particles), and an answer to
the outbox blocker on this basis.

Smoke runs before submission (processor executable, 2 cycles each): D-20261115-170326-dfb2a02
(16^3 blocks: 1280 MeshBlocks; superseded; its horizon summary was written into the working
directory of the command, not into -d, and was moved into that run directory as
`es.horizon_summary_0.txt.from_cwd`: fastflow writes the summary relative to the cwd) and
D-20261115-172413-6412daf (24^3 blocks: 344 MeshBlocks as designed; history finite, 696828
particles kept, M_AH(t = 0) = 0.99239, minimum lapse 0.0307; the 1+log lapse at x = 46.5 M
rises at 0.0334/M over the first two steps, -2K = 0.0335/M as in A2). ES-1 and V-1 were
submitted as chains D-20261115-172726-60ba4c2 (Slurm 4472) and D-20261115-172730-c6d151b
(Slurm 4473), two segments of at most 59 min each.

## State at the end of the helper session (2026-11-15, 17:55 UTC)

- ES-1 (D-20261115-172726-60ba4c2, Slurm 4472) and V-1 (D-20261115-172730-c6d151b, Slurm
  4473) are QUEUED behind about nine jobs (FIFO, all priority 1); not started, no card time
  used yet. Each chain may run two segments of at most 59 min (nrpic-run reserves 1.97
  card-hours each, 3.93 together; the expected use is 1.0 + 0.9 = 1.9 card-hours, A6; the
  package cap is 2.5). The second segment of each chain is submitted by the chain itself
  when the first stops at the 50 min wall clock.
- The outcome of entry 2 is therefore NOT written: no horizon-mass drift, no wall
  comparison, no crossing times yet. To finish: `tracks/D-bh-dress/es_runs/tools/finish.sh`
  from the worktree root once both chains say DONE (`--partial` analyses a running or
  stopped pair without closing the runs); then look at every figure it copies into
  `figs/` and append the outcome below entry 2, against predictions 1-4 and A1-A6 as
  written (not edited).
- What to watch first in the output: column 3 of `es.nrpic.hst` (a run that goes non-finite
  ends "successfully" with zero particles), the plateau lapse (probe 0) against the model
  of A2, and whether a lapse front from the dust edges reaches the hole (probes 1-3,
  `figs/axis_profiles.png`).
- ES-1G (`inputs/es1g_dx8.athinput`, core's `lapse_leak = 0.5`) is prepared and not run:
  `scratch/core/exe/core_gauge/READY` did not exist; it needs about 1 card-hour, which
  together with ES-1 and V-1 exceeds the 2.5 card-hours of this package: the lead decides.

## Entry 4 (2026-11-19, wave 2b): outcome of entry 2 (ES-1 and V-1)

Both chains ran in one segment each to tlim = 200 M (`scripts/submit_chain.sh --status`:
"finished: time=2.000000e+02 cycle=6400", STATUS DONE (tlim); Slurm 4472, 4473, started
2026-11-15 19:35 and 19:42 UTC). Closed with `tools/finish.sh` (nrpic-run finish of both);
analysis run D-20261119-141839-8686bd7 (`analyse.py`, t0 = 100 M):
`results/es_analysis.json`, figures `figs/horizon_mass.png`, `figs/wall.png`,
`figs/tracers_all.png`, `figs/lapse_probes.png`, `figs/axis_profiles.png`, each looked at.
Numbers of the lapse histories and drift windows below read from `es.nrpic.hst`,
`v1.nrpic.hst` and the horizon summaries of the two run directories (quoted again with
figures by the registered check of entry 6). Predictions are judged as written; nothing
in entry 2 was changed.

Prediction 1 (horizon mass):
- "M_AH(t)/M_AH(t0) - 1 stays within the floor of V-1 for 100 <= t <= 200 M": FAILED.
  max |drift| over 100-200 M: ES-1 3.40e-4, V-1 1.37e-4 (ES-1 2.5 times V-1).
- "|M_AH(t)/M_AH(100 M) - 1| <= 3e-5 at M/8": FAILED for both runs. Over 100-165 M V-1
  stays in [-4.2e-5, +2.1e-5] and ES-1 in [-5.0e-5, +9.3e-5]; from t = 165-170 M both
  drift down together (figure, middle panel), to -1.37e-4 (V-1) and -3.40e-4 (ES-1) at
  t = 199.5 M (slopes over 100-200 M: -9.5e-7/M and -3.0e-6/M).
- Level "M_AH(100 M) - M = +1.5e-3 +- 3e-4": FAILED: +9.55e-4 (ES-1), +9.37e-4 (V-1).
  The D-pre-4 mesh had M/8 on +-4 M; here the near-hole nest is wider (entry 2). Core's
  run on the same table with M/8 within +-2 M gives +9.76e-4 at t = 30 M
  (core-20261115-202901-b4430da, es.horizon_summary_0.txt). Cause of the shift not tested.
- Refutation criterion ("ES-1 change larger than V-1's by more than 3 times V-1's floor"):
  NOT met. max |drift(ES-1) - drift(V-1)| = 2.04e-4 = 1.49 times V-1's floor 1.37e-4.
- The two horizon masses agree to 9e-16 until t = 23 M (the hole region is causally cut
  off from the dust until then; `horizon_difference` of the JSON, figure bottom panel).
  Then ES-1 - V-1 swings between +3.2e-4 and -2.3e-4 during t = 27-48 M (the lapse pulse
  from the dust reaching the hole, see A3), stays +0.5e-4 to +1.2e-4 to t = 165 M and
  falls to -1.9e-4 at 199.5 M.
- [TO VERIFY] The common late drift after t = 165 M (both runs) has no established cause.
  Candidates: a signal from the outflow boundary at 192 M (core READY: outflow is not
  transparent for the Painleve-Gullstrand exterior), the slow approach of the 1+log
  slicing to its stationary state. Entry 6 tests the first through the coordinate time at
  which the tracer errors start to grow.

Prediction 2 (wall, tags 56-69, tau <= 200 M): HELD. max |R/R_exact - 1| = 2.20e-3 (ES-1),
1.59e-3 (V-1), below 3e-3 and far below the 1 per cent refutation. Beyond tau = 200 M
(recorded, no criterion, A4): ES-1 reaches tau = 283 M by t = 200 M and its wall error
grows to +1.71e-2 on the diagonal tracers and +5.8e-3 on the axis tracers (the diagonal
ones pass 1 per cent at tau ~ 255 M); V-1 (tau = 250 M at the end) +7.2e-3. Axis and
diagonal tracers separate from tau ~ 130-150 M on (axis below, diagonal above the exact
curve; `figs/wall.png`), so the late error is anisotropic, a property of the Cartesian
mesh or the boundary, not of the spherical solution [JUDGEMENT; cause not tested].
Other groups for tau <= 200 M (ES-1 / V-1): R0 = 28 M 2.1e-3 / 0.9e-3; 40 M 3.1e-3 /
1.8e-3; 48 M 3.4e-3 / 2.2e-3; 56 M 5.4e-3 / 2.6e-3; 66 M 6.2e-3 / 3.3e-3; 78 M 7.6e-3 /
4.4e-3: all below 1 per cent, growing outward (coarser cells: dx = 2 M beyond |x| = 48 M).

Prediction 3 and A1 (crossings of R = 2M):
- Group R0 = 6 M: tau = 14.8263 M (14 tracers, spread 1.7e-4 M) against the exact 14.8269
  M: off by -5.8e-4 M. Group R0 = 10 M: 34.4368 M (spread 3.9e-4) against 34.4423 M: off
  by -5.6e-3 M. HELD (A1: within 0.5 M). V-1 gives the same to 3e-4 M (14.8263, 34.4365).
  Coordinate times of the crossings: 14.74 M and 26.49 M (ES-1), 14.74 and 26.60 M (V-1).
- Both groups were removed (n_excised = 28 + 14 in ES-1, 28 in V-1); their last records
  are 0.2 M of proper time after R = 2M (tau_end 15.03 and 34.63 M).
- Group R0 = 20 M: "falls in at tau = 245 M (after the run)": in ES-1 its proper time ran
  ahead of coordinate time (A1 left this open) and it crossed during the run, at
  t = 177.1 M, tau = 244.33 M (two sets of tracers, 244.09 and 244.51 M) against the exact
  244.74 M: off by -0.41 M, inside A1's 0.5 M. In V-1 it had not crossed by t = 200 M
  (tau_end = 243.4 M). Turnaround near 27 M as predicted (figs/tracers_all.png, looked at;
  number in entry 6).
- "No dust particle enters R < R_w(tau)": no dust particle at a coordinate radius below the
  smallest wall-tracer radius in any of the nine snapshots (t = 0 to 200 M). HELD with
  that test. It is weak once the wall is anisotropic: at t = 200 M the wall tracers span
  r = 82.48-83.05 M and the innermost dust particle is at 82.79 M. A test along each
  particle's direction is in entry 6.

Prediction 4 and A2 (lapse): REFUTED. The 1+log lapse in the dust did not grow as
1 + 6 ln a. At the plateau probe (x = 46 M): 1.292, 1.662, 1.636 at t = 10, 25, 50 M against
the homogeneous model 1.377, 2.096, 3.577: -6, -21, -54 per cent, so A2 ("within 20 per
cent to t = 50 M") FAILED from t ~ 25 M on. From t ~ 50 M the lapse is 1.30-1.39 at every
probe outside 10 M, in the dust and outside it (`figs/lapse_probes.png`), and K-hat on the
x axis is near zero from the bubble to the boundary (`figs/axis_profiles.png`, bottom row):
the slicing has gone to a K ~ 0 (maximal-like) state instead of following the dust. The
probe at 46 M is no longer in the dust after t ~ 45 M (innermost dust at r = 48.07 M at
t = 50 M), so the probe's later values are not plateau values. Dust proper time at
t = 200 M: 279.5-279.9 M for group R0 = 48 M (A2 model: 1251 M). The initial slope held:
d alpha/dt at 46 M over t <= 1 M 0.0339/M (ES-1; predicted 0.0335/M at 48 M) and 0.0136/M
(V-1; predicted 0.0128/M at 48 M, which the r^(-3/2) of the Painleve-Gullstrand K makes
0.0137/M at 46 M). A front from the dust reaches the hole: yes, at t ~ 23 M (prediction 1).

A3 (near the hole): partly FAILED. The lapse at x = 1 M agrees between ES-1 and V-1 to
4e-5 at t = 25 M (0.21367, 0.21371): HELD. "The mesh minimum stays below 0.05": FAILED in
both runs: it rises from 0.031 to 0.232 at t = 5.6 M and to 0.160 at t = 15 M (identical in
the two runs), and in ES-1 again to 0.105 at t = 31 M, before it falls to 0.0042 at
t = 40.6 M (ES-1; V-1 0.0118 at 24.4 M) and settles at 0.016 (ES-1) and 0.019 (V-1) by
t = 200 M. Gauge pathology recorded: for several M of coordinate time near t = 6 and
15 M no cell has alpha < alpha_exc = 0.05, so lapse excision acts on nothing then; no
particle was near the hole at those times (the innermost tracers start at 6 M), so no
consequence here, but a run with dust near the hole would rely on ah_exc_factor alone.

A4: HELD (V-1 wall 1.59e-3 for tau <= 200 M; groups 5-9 of V-1 within 4.4e-3).
A5: HELD. History finite to the end; particles lost only by excision of the infalling
tracers (ES-1 42 = groups 0-2, V-1 28 = groups 0-1), none through the boundary; dust mass
1.739672372737941 at the first and last record; push_unconverged = 0.
A6: the cost was lower than predicted: ES-1 0.769 card-hours (46.2 min), V-1 0.672
(40.3 min), against 1.0 and 0.9; 1.44 together (manifests after `finish`).

Gauge pathologies of the 1+log run, collected: (i) the slicing drifts to K-hat ~ 0 in the
dust (the dust then moves through the normal observers; its proper time runs 1.4 times
coordinate time on average instead of following alpha); (ii) a lapse pulse from the dust
reaches the hole at t ~ 23 M and moves the horizon mass by up to 3e-4 for 25 M; (iii) the
mesh minimum of the lapse oscillates between 0.004 and 0.23 during the first 45 M;
(iv) the lapse settles at 1.3-1.4 out to the outflow boundary, not at 1; (v) late common
drift of the horizon mass after t ~ 165 M and the axis/diagonal split of the tracers
after tau ~ 130 M (causes open, entry 6).

## Entry 5 (2026-11-19): prediction for ES-1G (core's lapse_leak on the ES-1 data)

Run: `inputs/es1g_dx8.athinput` = ES-1 plus `<z4c> lapse_leak = 0.5, lapse_leak_alpha = 1.0`
(d_t alpha = [1+log] - (alpha/T) max(ln alpha, 0), T = 2 M, option 1 of
`scratch/core/exe/core_gauge/READY`); card executable
`scratch/core/exe/core_gauge/athena_gpu` (source b4430da; `git diff core-v0.3 b4430da --
athenak/src` touches only `z4c/` (242 lines) and main's `athenak/src` equals core-v0.3, so
it differs from ES-1's executable by the gauge term alone); same data, mesh, finder,
particles, outputs; tlim = 200 M, one chain segment (--gpu-hours 1.0, athena wall 56 min).
What core measured on these data (READY of 2026-11-15 lists test ES as pending; its run
core-20261115-202901-b4430da, 2 M cells in the dust, M/8 within 2 M, 30 M, which I read
before writing this): largest lapse on the mesh 1.108 at t = 5 M falling to 1.063 at
t = 30 M; M_AH = 1.000976 at t = 30 M. Homogeneous models: run D-20261119-142334-4f2bffe
(`tools/es1g_model.py`, `results/es1g_model.json`, `figs/es1g_model.png`, looked at): with
lapse_leak the plateau lapse is 1.062, 1.064, 1.057, 1.048, 1.037, 1.030, 1.025 at
t = 5, 10, 25, 50, 100, 150, 200 M (it tracks exp(6 T H) to 5e-4 after t = 10 M), the dust
proper time 10.53, 26.44, 52.75, 104.85, 156.49, 207.85 M at t = 10, 25, 50, 100, 150,
200 M; -3H = -0.0116, -0.0089, -0.0072, -0.0061/M at t = 50, 100, 150, 200 M.

Predictions [JUDGEMENT unless a number is quoted from the runs above]:
- G1 lapse in the dust: alpha at the tracers of groups R0 = 40 and 48 M (trajmet) within
  3 per cent of the leak model for 10 <= t <= 200 M; largest lapse on the mesh below 1.2
  after t = 10 M. Refuted by a dust lapse above 1.3 at any time.
- G2 slicing follows the dust: K-hat on the x axis at the coordinate radius of the axis
  tracers of group R0 = 48 M within 25 per cent of -3H of the model at t = 50, 100, 150,
  200 M (in ES-1 it was near 0). Refuted if |K-hat| there falls below half of 3H.
- G3 dust proper time: group R0 = 48 M at tau = 208 M +- 5 per cent at t = 200 M (ES-1:
  279.7 M).
- G4 wall: |R/R_exact - 1| of tags 56-69 below 3e-3 for the whole run (tau <= ~210 M);
  refuted (criterion 2) above 1 per cent.
- G5 crossings: groups R0 = 6 and 10 M reach R = 2M within 0.05 M of proper time of the
  exact 14.827 and 34.442 M and are removed; group R0 = 20 M does not reach R = 2M before
  t = 200 M (its tau at the end below 230 M).
- G6 horizon mass: M_AH(100 M) - M = +9.5e-4 +- 1e-4 (ES-1 +9.55e-4, V-1 +9.37e-4, same
  nest); |M_AH(t)/M_AH(100 M) - 1| below 1.4e-4 (V-1's floor) for 100 <= t <= 200 M; the
  swing of ES-1 during t = 25-50 M (up to 3.2e-4 away from V-1) reduced at least by half
  against V-1. Refuted (the same threshold as prediction 1) by a drift above 4.1e-4 =
  3 x V-1's floor: then relaxing the lapse does not remove the coupling of the dust to the
  measured horizon mass. No prediction on whether the late drift after t ~ 165 M of ES-1
  and V-1 appears (its cause is open).
- G7 technical: the log has no "not used" warning for lapse_leak; history finite; no
  escapes; dust mass unchanged; push_unconverged = 0; excised 28 tracers (groups 0-1);
  cost at most 0.85 card-hours (ES-1 0.77).
Gauge pathologies to look for: a start-up pulse of the relaxation (core's bound-ball runs:
a dip that grows faster than linearly with T), a lapse below 1 inside the dust, a front
from the dust edges reaching the hole, the mesh minimum of the lapse near the hole.

## Entry 6 (2026-11-19): second look at ES-1 and V-1 (tools/es_extra.py), prediction

Questions left open by entry 4, measured from the same run directories by
`tools/es_extra.py` (registered; the run id is in the outcome below). Written before the
script was first run.
- E1 dust and wall, direction by direction: the wall tracers' coordinate radius is fitted
  per snapshot as r_w(n) = a + b (n_x^4 + n_y^4 + n_z^4) and every dust particle compared
  with it. Prediction: no dust particle more than 1 M (one cell at the wall at t = 0)
  inside r_w(n) in any snapshot of ES-1; the smallest margin stays above -0.5 M. Refuted
  by any particle more than 1 M inside: then dust enters the bubble and the horizon need
  not keep its mass.
- E2 cause of the late growth [JUDGEMENT, weak; I hold the boundary hypothesis at about
  even odds]: if a disturbance from the outflow boundary at 192 M causes the growth of
  the tracer errors and the horizon drift after t ~ 165 M, then (a) the coordinate time at
  which a group's error first exceeds 2e-3 decreases with the group's coordinate radius
  (outer groups first) in both runs, and (b) the space-time diagram of log10|H| on the x
  axis shows a front moving inward from x = 192 M that reaches x < 10 M between t = 125 and
  200 M. Refuted if the onset times do not decrease outward or no inward front is seen in
  |H|, alpha or K.
- E3 slicing in the dust (measurement, ES-1): K = Khat + 2 Theta at the +x tracer of
  R0 = 48 M against -3H(tau): I expect |K| below 0.3 x 3H from t = 50 M on (from the
  K-hat profiles of entry 4), i.e. the slices no longer follow the dust.
- E4 turnaround of the group R0 = 20 M: maximum areal radius within 1e-3 of the exact
  LTB maximum, in both runs.
- E5 wall at tau = 50, 100, 150, 200 M on axis and diagonal tracers against the exact
  46.99, 56.80, 65.84, 74.29 M of entry 2: within 3e-3 (as prediction 2, now per class).

Outcome of entry 6 (run D-20261119-142929-bb375ff, `results/es_extra.json`; figures
`figs/extra_tracers_vs_t.png`, `figs/extra_spacetime_ES-1.png`, `figs/extra_spacetime_V-1.png`,
`figs/extra_plateau.png`, `figs/extra_dust_wall.png`, `figs/extra_horizon.png`, each looked at):
- E1 HELD. Along each particle's direction the innermost dust stays outside the wall in
  every snapshot of ES-1: smallest margin r_dust - r_w(n) = 0.232 M at t = 0, 0.162 M at
  50 M, 0.136 M at 200 M; no particle inside (0 of 696688). The shrinking margin is the
  geometry of marginally bound shells (dR/dR0 = (R0/R)^(1/2): 0.23 (36/83)^(1/2) = 0.15 M),
  not an approach. The wall fit has two classes only (axis, diagonal), so the fit is
  exact by construction; the anisotropy coefficient b grows from -0.005 M (t = 25 M) to
  -0.86 M (t = 200 M): at the end the wall on the axes lies 0.57 M closer to the centre in
  coordinates than on the diagonals (r = 82.48 against 83.05 M).
- E2 REFUTED as written, with a partial pattern. On the diagonal tracers the onset of
  |R/R_exact - 1| > 2e-3 does come first for the outer groups in both runs (ES-1: 117.5,
  121, 121, 130, 142, 140, 150.5 M for R0 = 78, 66, 56, 48, 40, 36, 28 M; V-1: 140, 147,
  152, 156, 162, 164.5, 174 M), an apparent inward motion at about one coordinate unit
  per M. On the axis tracers of ES-1 it does not (onsets 89-90 M for R0 = 20 and 28 M,
  115-171 M for the others, no order: the inner axis groups drift slowly negative from
  t ~ 50 M, `figs/extra_tracers_vs_t.png`). No inward front is visible in alpha, K or |H|
  on the x axis, but the slices are 10 M (z4c) and 25 M (con) apart, too sparse to see a
  front moving at speed ~1. The cause of the late growth and of the late horizon drift
  stays open [TO VERIFY]; the decisive test is a rerun of V-1 (no dust, 0.67 card-hours)
  with the outflow boundary moved from 192 M to 384 M (one more root level), not done in
  this package (request to the lead).
- E3 mostly HELD. K = Khat + 2 Theta at the +x tracer of R0 = 48 M (ES-1), in units of
  -3H(tau): 1.00 (t = 0), 0.50 (10 M), 0.62 (20 M), 0.19 (30 M), 0.10 (40 M), -0.21 (50 M),
  -0.31 (60 M), -0.18 (70 M), -0.40 (80 M), -0.11 to +0.21 from 90 to 200 M. So the slices
  stop following the dust within 30 M; between t = 40 and 90 M K is positive at the
  tracer (the normal observers converge where the dust expands); my bound |K| < 0.3 x 3H
  from t = 50 M is exceeded at t = 60 M (0.31) and 80 M (0.40). The lapse at these tracers:
  1.28, 1.63, 1.67, 1.39, 1.35, 1.36-1.37 at t = 10, 25, 50, 100, 150, 200 M; proper time
  279.5-279.9 M at t = 200 M. Note for entry 5: R0 = 40 M lies in the inner dust edge
  (GEOM: Rw = 40 M, w_in = 4 M, so 36-44 M is the edge; K there at t = 0 is -0.0127/M,
  0.76 of -3H), so only R0 = 48 M is a plateau group; predictions G1-G3 are judged on
  R0 = 48 M, and R0 = 40 M is reported without the plateau model.
- E4 HELD. Group R0 = 20 M turns around at R = 26.643-26.663 M (ES-1) and 26.658-26.661 M
  (V-1) against the exact 26.667 M (relative -9e-4 to -1.3e-4), at tau = 93.12 M (ES-1)
  and 92.90 M (V-1) against 93.15 M.
- E5 HELD. Wall at tau = 50, 100, 150, 200 M against the exact 46.985, 56.805, 65.837,
  74.286 M: ES-1 axis 46.977, 56.785, 65.800, 74.123 M (relative -1.8e-4, -3.5e-4,
  -5.6e-4, -2.20e-3); diagonal 46.985, 56.802, 65.831, 74.415 M (-1.2e-5, -5.0e-5, -8.2e-5,
  +1.74e-3). V-1 axis -5.3e-5, -1.1e-4, -4.8e-4, -1.06e-3; diagonal +3e-6, -1.0e-5,
  +1.4e-4, +1.59e-3.
- Seen in the figures, not predicted: (a) both runs show a step of the horizon mass at
  t ~ 30 M, from +1.05e-3 to +0.92e-3 in V-1 (`figs/extra_horizon.png`, top panel); the
  "level" of prediction 1 is therefore set by an event at t ~ 30 M, not by a smooth
  approach [cause not tested: finder or gauge]. (b) From t = 100 to 165 M the horizon mass
  of ES-1 oscillates with a period of about 7-8 M and an amplitude of about 5e-5, that of
  V-1 with about 2e-5. (c) The mesh maximum of the lapse reaches 2.13 (ES-1) and 1.95 (V-1)
  after t = 10 M.

## Entry 7 (2026-11-19): inward features in the lapse at the probes, prediction

E2 could not see a front because the slices are 10-25 M apart. The probes (x = 1, 4, 20,
36, 46, 56, 80, 152 M on the x axis) are written every 0.3125 M. `tools/probe_fronts.py`
forms d alpha/dt at each probe, removes a 20 M running mean, and finds for each pair of
neighbouring probes the lag that maximises the cross-correlation over t = 50-200 M
(positive lag: the outer probe sees the feature first, i.e. inward motion). Written before
the script was first run.
Prediction [JUDGEMENT, weak]: if the outflow boundary drives the late drift, the detrended
lapse rate carries an inward-moving feature: positive lags between 152 -> 80 -> 56 M with
apparent speeds between 0.8 and 2 (light or gauge speed with alpha ~ 1.2-1.4), in both
ES-1 and V-1, and the waterfall figure shows a feature reaching x = 4 M between t = 130 and
175 M. Refuted if the lags on the outer pairs are negative or the correlations below 0.3
(no coherent inward feature); then the boundary is not the visible carrier, and the slow
approach of the slicing (or the finder) stays the candidate.

Outcome of entry 7 (run D-20261119-143413-bce5e71, `results/probe_fronts.json`, figures
`figs/probe_fronts_ES-1.png`, `figs/probe_fronts_V-1.png`, looked at): REFUTED. On
t = 50-200 M the coherent features in the detrended lapse rate move OUTWARD on every outer
pair, in both runs, at the gauge speed: lags 152 -> 80 M -47.0 / -47.5 M, 80 -> 56 M
-15.5 / -16.0 M, 56 -> 46 M -6.5 / -6.75 M, 46 -> 36 M -6.5 / -6.5 M (ES-1 / V-1),
correlations 0.96-0.99, apparent speed 1.48-1.55 (sqrt(2 alpha) = 1.6 at alpha = 1.3).
Inward lags appear only near the hole: 20 -> 4 M +8.0 M (ES-1, corr 0.89) and +7.0 M
(V-1, 0.80); 36 -> 20 M +10.25 M in V-1 (0.73) but -10.5 M in ES-1 (0.93). The waterfall
figures show the features concentrated in t = 30-100 M (outgoing gauge waves after the
start); after t ~ 100 M nothing visible arrives at x = 4 M between t = 130 and 175 M at the
scale of the early features. The lag analysis is dominated by the early, large
features, so a weaker late inward signal is not excluded by it; the next paragraph
restricts the window.

Added test, prediction written before it ran: the same analysis on t = 100-200 M only
(`--tmin 100`). If a late inward signal exists (boundary reflection of the outgoing
gauge waves, which reach 192 M at t ~ 90-130 M), the outer pairs show positive lags with
correlation above 0.5 on this window [JUDGEMENT, even odds]. Refuted by negative lags or
correlations below 0.5 on the pairs 152 -> 80 and 80 -> 56 M.

Outcome of the added test (run D-20261119-143444-8a9949c, `results/probe_fronts_t100.json`,
figures `figs/probe_fronts_t100_ES-1.png`, `figs/probe_fronts_t100_V-1.png`, looked at):
REFUTED. On t = 100-200 M the outer pairs carry no coherent signal: 152 -> 80 M lag
+47.75 M with correlation 0.34 (ES-1) and +68 M with 0.32 (V-1); 80 -> 56 M +0.5 M (0.49)
and -4.75 M (0.55). The waterfalls show small oscillations of period ~6-8 M that appear
at x = 1-56 M nearly in phase (lags 0.25-1 M between 4, 20, 36, 46 M in V-1 at
t ~ 105-135 M), not a front from the boundary. The rise of every row after t ~ 190 M is an
artefact of the 20 M running mean at the end of the series (zero padding), not a signal.
So no inward signal from the outflow boundary is seen in the lapse at the probes; the
cause of the late horizon drift and of the late tracer errors is still open.
Further facts from the horizon summaries of the two runs (columns meanradius, hrms):
the horizon's coordinate radius grows through the run, 2.02 M at t = 25 M in both, then
2.45 / 2.15 M at 100 M, 2.49 / 2.20 M at 165 M, 2.56 / 2.25 M at 199.5 M (ES-1 / V-1);
the surface stays round (hrms ~ 6e-9) and nothing changes at t ~ 165 M. The near-hole
mesh is M/8 out to 6 M, so the horizon is not losing resolution. Remaining candidates
[TO VERIFY]: the slow evolution of the slicing and shift near the hole (both runs), the
finder. A cheap discriminating test (lead's decision): V-1 with the outflow boundary at
384 M, or V-1 at M/16 near the hole.

## Entry 8 (2026-11-19): pre-flight of the ES-1G input on the processors, prediction

While ES-1G (D-20261119-142633-6f72922, Slurm 4636) waits in the queue: the input
`inputs/es1g_dx8.athinput` for two cycles with history every cycle
(`time/nlim=2 particles/hist_dcycle=1`), once with core's gauge processor executable
(`scratch/core/exe/core_gauge/athena_cpu`, b4430da) and once with the release processor
executable (`.work/build_cpu_v03/src/athena`), which does not know the option.
Prediction: (a) the release log warns that `lapse_leak` and `lapse_leak_alpha` were not
used, the gauge log does not; (b) the t = 0 rows are identical (np 696828, alpha_min
0.03071291167554946, probe lapses as ES-1 at t = 0); (c) at cycles 1 and 2 the lapse at the
plateau probe (x = 46 M, alpha slightly above 1) is lower in the gauge run by between 1e-7
and 1e-4 (the term (alpha/T) ln alpha with alpha - 1 ~ 0.034 t over t <= 0.0625 M gives a
few 1e-5 at most), and the lapse at x = 1 M (alpha < 1, where the term vanishes) agrees to
1e-12. Refuted by a gauge log warning that the option was not used, or by identical
plateau lapses (the option inactive), or a difference at x = 1 M (the term acting where it
must not).

Correction to entry 4 (run D-20261119-143659-7adcad7, `es_extra.py` version 2 on the same
two runs; `results/es_extra.json` now holds its output, a superset of the first run's):
the horizon masses of ES-1 and V-1 differ by less than 1e-8 for t <= 20 M and by more than
1e-9 from t = 19.5 M on; the split becomes visible on the figure (above ~1e-5) near
t = 23 M. Entry 4's "agree to 9e-16 until t = 23 M" holds only at the sampled t = 10 M.
ES-1 minus V-1 by window: [-2.3e-4, +3.2e-4] on 25-50 M, [-2.9e-5, +1.25e-4] on 100-165 M,
[-1.9e-4, +7.6e-5] on 165-199.5 M. At the +x plateau tracer (R0 = 48 M) Khat and K = Khat +
2 Theta differ by less than 3e-5/M before t = 100 M and by up to 6e-4/M at t = 200 M
(Theta grows late); entry 6 quoted K.
Second correction to entry 4 (same history files): "from t ~ 50 M the lapse is 1.30-1.39
at every probe outside 10 M" is true from t ~ 150 M on (1.30-1.39 at t = 150 and 200 M);
at t = 50 M the probes outside 10 M read 1.21-1.67 and at t = 100 M 1.33-1.51 (the
outgoing gauge waves of entry 7 are still passing).

Outcome of entry 8 (runs D-20261119-143623-8576a6e gauge executable, 1223 s of processor
time, and D-20261119-143626-7d1fa75 release executable, 1288 s; comparison
D-20261119-150329-d1d8f03, `results/preflight.json`, `figs/preflight.png`, looked at): HELD
in every part.
(a) The release log warns "input parameter <z4c>/lapse_leak = 0.5 was not used" and the
same for lapse_leak_alpha; the gauge log has no warning: the option is read.
(b) The t = 0 rows are identical (np 696828, sum_m 1.73967237273851, alpha_min
0.0307129116755495, every probe lapse).
(c) The gauge run's lapse is lower where alpha > 1: at the plateau probe (46 M) by 8.1e-6
(cycle 1) and 3.2e-5 (cycle 2); at 36, 56, 80, 152 M by 4.8e-6 / 6.0e-6 / 2.4e-6 / 9.1e-7
(cycle 1) and 1.9e-5 / 2.4e-5 / 9.5e-6 / 3.6e-6 (cycle 2); alpha_max lower by 3.6e-5
(cycle 2). Where alpha < 1 nothing changes: x = 1 M and 4 M identical to the last digit,
x = 20 M (alpha = 0.997) different by 6.7e-15 and 5.3e-13 only (the stencils reach it from
the alpha > 1 region). So the card executable of the same source (ES-1G) runs the relaxed
lapse; the run itself is still queued.

## State at the end of the wave-2b helper session (2026-11-19, 15:05 UTC)

- Done: ES-1 and V-1 closed and judged (entries 4, 6, 7 and the corrections); ES-1G
  predicted (entry 5), checked on the processors (entry 8) and submitted.
- ES-1G (D-20261119-142633-6f72922, Slurm 4636) is QUEUED behind about fifteen jobs; no
  card time used yet; it reserves 0.98 card-hours in one segment (athena wall 56 min;
  ES-1 needed 46 min). Its outcome is NOT written. To finish: from the worktree root,
  `tracks/D-bh-dress/es_runs/tools/finish_es1g.sh` once the chain says DONE; look at every
  figure in `figs/es1g/`; judge G1-G7 of entry 5 as written (G1-G3 on the group
  R0 = 48 M, see entry 6, E3) and record every gauge pathology.
- Card-hours of this package: ES-1 0.769 + V-1 0.672 (wave 2), ES-1G at most 0.98.

## Entry 9 (2026-11-20, wave 3): closing ES-1G and judging it against entry 5

Opened 2026-11-20 22:14 UTC, before any analysis of the ES-1G output. Entry 5 stands
unchanged. `scripts/submit_chain.sh --status` on the run directory of
D-20261119-142633-6f72922: "STATUS: DONE job: 4636", "seg=1 job=4636 finished:
time=2.000000e+02 cycle=6400", started 2026-11-19 07:36:28, finished 08:24:04 PST. The
manifest still says "submitted" and reserves 0.98 card-hours.
What I am about to do, in order: (1) close the run and register `tools/es_extra.py` on
ES-1, V-1 and ES-1G with `tools/finish_es1g.sh`, then `nrpic-run verify` the run; (2) look
at every figure in `figs/es1g/`; (3) judge G1-G7 exactly as written in entry 5, with
G1-G3 on group R0 = 48 M (entry 6, E3: R0 = 40 M lies in the inner dust edge, 36-44 M)
and R0 = 40 M reported separately; (4) record the gauge pathologies entry 5 lists
(start-up pulse of the relaxation, a lapse below 1 inside the dust, a front from the dust
edges reaching the hole, the mesh minimum of the lapse near the hole against
alpha_exc = 0.05, column 16 of `es.nrpic.hst`); (5) measure, without a prediction, the
late horizon drift of ES-1G (t0 = 100 M, windows 100-165 M and 100-200 M); (6) compare with
core's ES test on 0-30 M (core_gauge READY, run core-20261115-202901-b4430da); (7) list
where `analyse.py` and `es_extra.py` use the code's particle energy E.
One fact seen before the analysis, while checking that the run is not empty (column 3):
the last row of `es.nrpic.hst` has np = 696800 (28 removed, 0 escaped), and the last row
of `es.horizon_summary_0.txt` (t = 199.5 M) reads M_AH = 1.008112, about 7e-3 above the
ES-1 value at the same time. This is recorded here before any number of the analysis;
G6 is judged on the registered analysis below.

Predictions for the measurements of `tools/es1g_judge.py` that entry 5 did not quantify,
written 2026-11-20 22:20 UTC, before `es1g_judge.py` ran and before I read any output of
`es_extra.py` on ES-1G (that analysis, D-20261120-221754-ae3dafe, was running in the
background of `finish_es1g.sh` at the time and finished as I wrote this) [JUDGEMENT
throughout]:
- J1 overlap with core's ES test (core-20261115-202901-b4430da: the same table, sha256
  9a69386c..., the same source b4430da and T = 2 M; differences: 87268 against 696828
  particles (hp 2 against 1), outer boundary at 96 against 192 M, the M/8 nest on +-2 M
  against +-6 M, cells of 2 M against 1 M in the inner dust). On 0-30 M: (i) M_AH(10 M)
  within 1e-4 of core's, and M_AH(30)/M_AH(10) - 1 within 3e-4 of core's; (ii) the lapse at
  the dust tracers (R0 = 40, 48, 56 M) over 5-30 M inside 1.03-1.07 in both runs, the two
  runs within 0.01 of each other; (iii) the largest lapse on the mesh over 0-30 M within
  0.02 of core's; (iv) the mesh minimum of the lapse above 0.2 near t = 5-6 M in both.
  Refuted by horizon masses that differ by more than 3e-4 at t = 10 M, dust lapses that
  differ by more than 0.03, or largest lapses that differ by more than 0.05.
- J2 start-up pulse: at the tracers of R0 = 48 M the lapse stays within 2 per cent of the
  lapse_leak model over 0-10 M (no dip). Refuted by a dip of more than 5 per cent below it.
- J3 lapse below 1 in the dust: after t = 5 M the lapse at the tracers of R0 = 40, 48 and
  56 M stays above 1 (at t = 0 it is psi^-2 < 1 near the inner edge, from the data).
  Refuted by any of them below 0.99 after t = 5 M.
- J4 front from the dust edges at the hole: in ES-1 a lapse pulse from the dust reached
  x = 4 M at t ~ 20-23 M (entry 4). With lapse_leak the dust lapse stays near 1.06, so the
  rms of the detrended d alpha/dt (probe_fronts.py, 20 M running mean) over t = 10-40 M at
  x = 4 and 20 M is at most one third of ES-1's. Refuted if it exceeds one half of ES-1's.
  (A departure from V-1 at the probes is measured but not judged: the relaxation acts in
  the bubble too wherever alpha > 1, so ES-1G differs from V-1 there without any dust.)
- J5 mesh minimum of the lapse (column 16) against alpha_exc = 0.05: above 0.05 during the
  start-up (t ~ 3-20 M), as in ES-1 and V-1 (the condition is plain 1+log where alpha < 1),
  and below 0.05 at every time after t = 50 M. Refuted by alpha_min > 0.05 after 50 M.

First registered judge run: D-20261120-222042-59c7d82 (`tools/es1g_judge.py` on ES-1G, ES-1,
V-1 and core-ES; `results/es1g_judge.json`). Its figures were looked at; two had a clipped
or overlapping axis label, and the K deficit of G2 (below) raised a question it did not
measure. So the script gains the tracers' Lorentz factor against the normal observers,
W = alpha dt/dtau, and v = (1 - 1/W^2)^(1/2), and wider margins, and is run once more.
- J6 prediction (written 2026-11-20 22:24 UTC, before that second run) [JUDGEMENT, weak]:
  the K deficit at the +x tracer of R0 = 48 M (K-hat = 0.67-0.81 of -3H(tau) from t = 10 M
  on, `results/es_extra_es1g.json`) means the slices of ES-1G do not follow the dust: the
  dust moves through the normal observers with v between 0.02 and 0.1 at t = 50-200 M at
  the tracers of R0 = 48 M. Refuted if v < 0.01 there (then the slices do follow the dust
  in velocity and the deficit of K has another source, for example the lapse gradient
  across the shell).

### Outcome of entry 9 (2026-11-20, written after the runs below)

Runs. ES-1G closed by `tools/finish_es1g.sh` (`nrpic-run finish`: status completed,
2856 s, 0.7936 card-hours, Slurm 4636; the 0.98 reserved card-hours are released) and
`nrpic-run verify D-20261119-142633-6f72922`: PASS (75 output files and 2 inputs match).
Analyses: `es_extra.py` on ES-1, V-1, ES-1G, D-20261120-221754-ae3dafe
(`results/es_extra_es1g.json`); `es1g_judge.py` on ES-1G, ES-1, V-1 and core-ES,
D-20261120-222042-59c7d82 (first) and D-20261120-222424-230f936 (second, adds W; its
horizon and history numbers are identical to the first; `results/es1g_judge.json`).
Fix recorded: `finish_es1g.sh` ran without error. Its "not used" check printed into my
log file was lost because `tee /dev/stderr` reopens and truncates a file that stderr
points to; the line is now `tee >(cat >&2)`. The check was repeated by hand:
`grep -c "not used" chain/seg001.job4636.a1.log` = 0.

Predictions of entry 5, judged as written (G1-G3 on R0 = 48 M; R0 = 40 M, the inner dust
edge, reported separately):
- G1 HELD. Lapse at the 14 tracers of R0 = 48 M against the lapse_leak model, max
  |alpha/alpha_model - 1| over 10 <= t <= 200 M: 1.31e-2 (at t = 34 M; the lapse lies
  below the model throughout): 1.054, 1.043, 1.035, 1.025, 1.019, 1.016 at t = 10, 25, 50,
  100, 150, 200 M against 1.064, 1.057, 1.048, 1.037, 1.030, 1.025. R0 = 40 M: 0.80e-2
  (t = 114.5 M); R0 = 56 M: 2.07e-2 (t = 20 M). Largest lapse on the mesh after t = 10 M:
  1.093 (at t = 10 M; 1.019 at 200 M), below 1.2; over the whole run 1.1086 at t = 5.3 M.
  Largest lapse at any dust or wall tracer: 1.061; refutation (dust lapse > 1.3) not met.
  (D-20261120-222424-230f936.)
- G2 FAILED, not refuted. K-hat at the +x tracer of R0 = 48 M against -3H of the leak
  model at the same t: 0.721, 0.672, 0.643, 0.627 at t = 50, 100, 150, 200 M (K-hat =
  -8.37e-3, -5.99e-3, -4.66e-3, -3.83e-3 /M; model -1.161e-2, -8.92e-3, -7.25e-3,
  -6.11e-3 /M): outside 25 per cent at every time, above the refutation bound 0.5. ES-1
  had -0.21 to +0.21 (entry 6). R0 = 40 M: 0.855, 0.776, 0.729, 0.701.
  (`results/es_extra_es1g.json`, D-20261120-221754-ae3dafe; model of entry 5.)
- G3 HELD. Proper time of R0 = 48 M at t = 200 M: 205.32-205.33 M against 208 +- 5 per
  cent (model 207.85 M; ES-1 279.7 M). R0 = 40 M: 206.18 M.
- G4 HELD. Wall (tags 56-69), max |R/R_exact - 1| over the whole run (tau <= 206.4 M):
  1.66e-4 on the axis tracers (at tau = 206.4 M), 1.68e-4 on the diagonal ones (tau =
  182.2 M); ES-1 2.2e-3 (tau <= 200 M) and 1.7e-2 (diagonal, tau = 283 M). No axis and
  diagonal split (`figs/es1g/judge_wall.png`).
- G5 HELD. R0 = 6 M: tau = 14.8261 M at R = 2M (14 tracers, spread 2e-5 M) against
  14.8269 M (-8.6e-4 M); R0 = 10 M: 34.4373-34.4432 M against 34.4423 M (-5.0e-3 to
  +0.9e-3 M); both groups removed (28 removed in all). Coordinate times 18.34 and 38.34 M
  (ES-1: 14.74, 26.49 M). R0 = 20 M did not cross; its proper time at the end 205.15 M
  (< 230 M). Its turnaround: R_max 26.6619-26.6620 M against 26.6667 M (-1.8e-4) at
  tau = 93.11 M against 93.15 M.
- G6 FAILED; the refutation criterion is met. M_AH(100 M) - M = +1.141e-3 (predicted
  +9.5e-4 +- 1e-4). M_AH(t)/M_AH(100 M) - 1: [-4.17e-4, +9.46e-4] on 100-165 M and up to
  +6.96e-3 at t = 199.5 M: 17 times the refutation threshold 4.1e-4. ES-1G minus V-1 on
  25-50 M: [-1.20e-4, +1.80e-4]; the largest value is 0.56 of ES-1's 3.23e-4, so "reduced
  at least by half" fails narrowly. The reading entry 5 attached to the refutation ("the
  dust stays coupled to the measured horizon mass") is NOT established by this run:
  there is no vacuum control with lapse_leak, and ES-1G minus V-1 mixes gauge and dust
  (the two horizon masses split at t = 8.0 M, before any signal from the dust; ES-1
  split from V-1 at 19.5 M). What the run shows (D-20261120-222424-230f936, and
  `es.horizon_summary_0.txt` columns 2, 3, 11 of D-20261119-142633-6f72922): the horizon's
  mean coordinate radius falls from 1.40 M (t = 25 M) to 1.06, 0.88, 0.78 M at t = 100,
  150, 199.5 M (8.5, 7.1, 6.2 cells of M/8), while it grows in ES-1 (2.02 to 2.56 M) and
  V-1 (2.02 to 2.25 M); the mesh minimum of the lapse rises from 0.039 (t = 50 M) to
  0.069 (200 M) and the lapse at x = 1 M from 0.33 to 0.47, where ES-1 and V-1 settle at
  0.016-0.019 and 0.15-0.19; the region of positive K around the hole shrinks inward in
  coordinates (`figs/es1g/extra_spacetime_ES-1G.png`). Core saw the same shrinking in L3
  (core_gauge READY: the hole three times smaller in coordinates than with plain 1+log;
  "give the centre cells of M/16 or finer"). Candidates [TO VERIFY]: (a) the finder loses
  accuracy as the horizon shrinks below about 8 cells; (b) the slicing near the puncture
  is not stationary under this gauge (the puncture lapse rises); (c) the dust; (d) the
  outflow boundary at 192 M (a signal at gauge speed ~1.4 from 192 M reaches the hole
  near t ~ 135 M; plausibility only). A V-1 with lapse_leak separates (c); ES-1G with an
  M/16 nest near the hole separates (a).
- G7 HELD. No "not used" warning in the log; history finite; 0 escapes; dust mass
  1.739672372737941 at the first and last record; push_unconverged 0; 28 tracers removed
  (groups 0-1; np 696828 -> 696800); cost 0.7936 card-hours (<= 0.85).

Predictions J1-J6 of this entry:
- J1 HELD, far closer than predicted. On 0-30 M ES-1G reproduces core's ES test
  (core-20261115-202901-b4430da): M_AH(10 M) 0.999952 against 0.999971 (1.9e-5);
  M_AH(29.5)/M_AH(10) - 1 = 1.029e-3 against 1.005e-3 (horizon summaries, lines 22 and
  61 of both files); lapse at the dust tracers over 5-30 M 1.034-1.061 in both, the same
  tracer to 1e-5 (R0 = 48 M peak 1.060981 against 1.060990); largest lapse 1.108612
  (t = 5.31 M) against 1.108609 (5.25 M); start-up bump of the mesh minimum 0.232 against
  0.233. Core's READY numbers (0.99997 at 10 M, drift 1.0e-3 to 30 M, dust lapse
  1.04-1.06, largest 1.11, wall to 6e-5) are all reproduced (our run: 0.99995, 1.03e-3,
  1.034-1.061, 1.109; core-ES wall 6.2e-5 in our analysis). So neither the particle
  lattice (87268 against 696828 particles), the outer boundary (96 against 192 M) nor the
  extent of the M/8 nest matters on 0-30 M at this level. Core's horizon has finder
  spikes at t = 13-15 M that ours lacks (`figs/es1g/judge_core30.png`).
- J2 HELD. Start-up: at R0 = 48 M the lapse stays within [-0.95e-2, +0.8e-4] of the model
  over 0-10 M; at R0 = 36, 40, 56 M down to -1.9e-2, -1.2e-2, -1.9e-2. No dip beyond 5 per
  cent; the mesh maximum is one smooth bump to 1.109 at t = 5.3 M.
- J3 HELD, with a correction of its parenthesis: the smallest lapse at the tracers of
  R0 = 36, 40, 48, 56 M is their t = 0 value, 1 to 1e-15, and no later value is lower. At
  t = 0 the lapse at these tracers is 1 (psi = 1 there), not psi^-2 < 1 as I wrote.
- J4 HELD. Rms of the detrended d alpha/dt over t = 10-40 M: x = 4 M 1.16e-2 (ES-1 1.31e-1,
  V-1 7.34e-2), 0.089 of ES-1; x = 20 M 1.55e-3 (ES-1 1.92e-2, V-1 8.48e-3), 0.081 of ES-1;
  x = 1 M 1.36e-2 (6.48e-2, 5.03e-2). Measured, not judged as announced: the probes leave
  V-1's values (by 1e-6) at t = 0.31, 6.25, 9.4 M at x = 20, 4, 1 M (ES-1: 8.75, 19.1,
  22.2 M), because the relaxation acts in the bubble from the start (largest lapse 1.11
  there). No front from the dust edges is visible in `judge_hole.png` or in the space-time
  diagram of ES-1G.
- J5 REFUTED. alpha_min (column 16) is above alpha_exc = 0.05 on [2.81, 13.13] M (largest
  0.232), as predicted, and again on [108.1, 200] M, rising to 0.0687 at t = 200 M. ES-1:
  [2.81, 20.0] and [29.1, 34.1] M; V-1: [2.81, 20.0] M; neither after 50 M.
- J6 HELD. Velocity of the dust against the normal observers at the R0 = 48 M tracers,
  v = (1 - 1/W^2)^(1/2) with W = alpha dt/dtau: 0.034, 0.052, 0.060, 0.063 at t = 50, 100,
  150, 200 M (R0 = 40 M: 0.020, 0.040, 0.049, 0.053; R0 = 56 M: 0.057, 0.072, 0.078, 0.080).
  ES-1: 0.297, 0.224, 0.19, 0.16-0.18; V-1 tracers: 0.24, 0.18, 0.16, 0.14. A first-order
  estimate [JUDGEMENT; outward v assumed, W ~ 1, v proportional to R^1.74 from the three
  groups, areal radius of R0 = 48 M at tau = 103.6 M about 72.8 M]: D_i v^i ~ (v/R)(2 +
  1.74) = 2.7e-3/M at t = 100 M, against the deficit -3H - K-hat = 2.9e-3/M. So the
  slices of ES-1G follow the dust in lapse and proper time but tilt against it by
  v ~ 0.03-0.06, which accounts for most of the K deficit of G2.

Gauge pathologies of ES-1G (the list of entry 5):
- start-up pulse of the relaxation: none beyond a lag of 1-2 per cent behind the
  homogeneous model in the first 20 M (J2);
- lapse below 1 inside the dust: none (J3);
- front from the dust edges reaching the hole: none seen; the near-hole lapse activity
  over 10-40 M is 0.08-0.09 of ES-1's and 0.16-0.18 of V-1's (J4);
- mesh minimum of the lapse near the hole against alpha_exc = 0.05 (risk R14): above it
  for 10.3 M during the start-up and for the whole of t >= 108 M (J5). From then on
  lapse excision acts on no cell and removal relies on ah_exc_factor = 0.8 of the horizon
  alone. No particle was near the hole then (the last infalling group, R0 = 20 M, had not
  crossed R = 2M), so nothing in this run depends on it;
- new: the horizon shrinks in coordinates and its mass grows from t ~ 126 M on (G6).

Late horizon drift, measured without a prediction (t0 = 100 M): ES-1G 100-165 M
[-4.17e-4, +9.46e-4] (minimum at t = 126 M, zero crossing at 149 M, +9.46e-4 at 165 M;
straight-line slope 1.2e-5/M); 100-199.5 M [-4.17e-4, +6.96e-3] (slope 5.8e-5/M; 1.7e-4/M
over 165-199.5 M). ES-1: [-5.0e-5, +9.3e-5] and [-3.40e-4, +9.3e-5]; V-1: [-4.2e-5,
+2.1e-5] and [-1.37e-4, +2.1e-5]. The common downward drift of ES-1 and V-1 after
t ~ 165 M does not appear in ES-1G as such: ES-1G moves the other way, by 20 to 50 times
as much, from t ~ 126 M on, so a common component of size 1e-4 cannot be separated from
it here. (D-20261120-222424-230f936.)

Figures in `figs/es1g/`, each looked at:
- `judge_horizon.png`: M_AH - 1 (symlog), drift from t = 100 M, horizon mean coordinate
  radius, for ES-1G, ES-1, V-1, core-ES. ES-1G dips to -4.2e-4 near 126 M, rises through
  zero at 149 M to +7e-3; its radius falls monotonically from 1.42 M (t = 30 M) to 0.78 M
  while ES-1 and V-1 grow; core-ES lies on ES-1G to t = 30 M.
- `judge_hole.png`: mesh minimum of the lapse (log) against 0.05: ES-1G crosses it near
  108 M and keeps rising, ES-1 and V-1 settle near 0.02; probe lapses at 1, 4, 20 M over
  0-60 M: ES-1 swings to 2.0 at 4 and 20 M, ES-1G stays at 0.82-1.1; detrended rates:
  ES-1 swings of +-0.2/M at x = 4 M near t = 20-35 M, ES-1G one bump of 0.065/M at 7 M.
- `judge_lapse.png`: dust-tracer lapse of ES-1G on the lapse_leak model (ES-1 to 1.71);
  ratio to the model between -2.1e-2 and 0 inside the +-3e-2 band; largest lapse on the
  mesh: ES-1G 1.11 then 1.02, ES-1 2.13, V-1 1.95.
- `judge_core30.png`: 0-30 M overlay of ES-1G and core-ES (horizon mass, largest and
  smallest lapse, dust-tracer lapse): the two coincide; ES-1 and V-1 part from them
  within the first 1-2 M (largest lapse) and at t ~ 11 M (smallest).
- `judge_wall.png`: wall tracers against the exact curve over their proper time: ES-1G
  within +-2e-4 to tau = 206 M; ES-1 and V-1 split into axis and diagonal after
  tau ~ 150 M.
- `extra_horizon.png` (es_extra, fixed axes): ES-1G leaves the frame after t ~ 150 M;
  that is why `judge_horizon.png` exists. Between 30 and 100 M ES-1G lies 1.0-1.25e-3
  above M, with oscillations of about 1e-4.
- `extra_plateau.png`: lapse and proper time of ES-1G at the R0 = 48 M tracers on the
  lapse_leak model; K at the +x tracer smooth, at 0.62-0.81 of -3H(tau) (G2).
- `extra_tracers_vs_t.png`: every group of ES-1G within about +-3.6e-3 of its exact
  curve to t = 200 M (largest late: R0 = 56 M axis, R0 = 20 M axis; onsets of 2e-3 at
  t = 156.5 M and 186 M); ES-1 reaches 2e-2, V-1 1.2e-2.
- `extra_dust_wall.png`: smallest margin of the dust outside the wall, ES-1G 0.232 M at
  t = 0 falling to 0.106 M at 200 M, no particle inside (ES-1 0.136 M).
- `extra_spacetime_ES-1G.png`, `extra_spacetime_ES-1.png`, `extra_spacetime_V-1.png`:
  alpha, K and log10|H| on the x axis (rows every 10 and 25 M). ES-1G: smooth lapse,
  K < 0 from ~5 M outward (the bubble keeps its expanding slicing), the K > 0 region
  around the hole shrinking from ~3 M to ~0.6 M; ES-1 and V-1: large lapse features at
  t = 10-50 M, K ~ 0 in the bubble, the K > 0 region fixed near 3.5-4 M.

Particle energy E (step 5 of the package). `analyse.py` reads E (trajmet index 13) into
the tracer records (`tracer_tracks`, line 114) and uses it nowhere. The "E" of
`exact_groups` and `ltb_radius` (analyse.py:239-297, es_extra.py:135-188) is the LTB
shell energy of the exact model (`es_model.shell_energy`, 2E = v0^2 - 2m/R0), computed
from the initial data, not the code's E. History columns used: time, np, sum_m (rest
mass, m only), sum_mW (finiteness flag only), alpha_min, alpha_max, alpha_probe*,
n_excised, n_escaped, push_unconverged; int_E, E_probe*, E_max, E_min are never read.
Proper time is the pusher's (trajmet index 12), cross-checked against the integral of
alpha/W with W from u_i and gamma^ij (analyse.py:132-135); `es1g_judge.py` forms
W = alpha dt/dtau. So no number of entries 4, 6, 7, 9 depends on the code's E: horizon
masses (finder), areal radii (metric at the particle), proper times, crossings,
turnaround, lapse and K (mesh), dust-wall margins (positions), counts and rest mass.
The finding of `flux_tools` (E = alpha W - beta^i u_i is not the Killing energy in this
gauge) does not touch these numbers; it matters only for an energy flux through the
horizon.
