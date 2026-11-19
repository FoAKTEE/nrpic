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
