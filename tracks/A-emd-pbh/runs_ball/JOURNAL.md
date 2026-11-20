# JOURNAL of the package runs_ball (helper of A-emd-pbh, wave 2)

Package: the first full-relativity runs of Track A, SR-1 (geodesic slicing) and SR-2
(conformal-time lapse) of `stage/G1/STATUS.md` section 3, on data set 2t (run
A-emd-pbh-20261115-130609-947c898), release core-v0.3. Evidence labels as in the brief.

## 2026-11-15, entry 1: what was read, set-up, and the predictions (written before any run)

Read: CLAUDE.md; coord/CHARTER.md to "Owners"; brief lines 335-365, 708-725, 834-860;
rulings `tracks/orch/outbox/20261115T1516Z__to-all__rulings-after-wave-1.md`; decisions
0010-0015; the owner's HANDOFF.md, STATUS.md, stage/G0/OPEN.md, stage/G1/STATUS.md; core's
message `tracks/core/outbox/20261115T1510Z__to-A-emd-pbh__format2-and-gauge.md`;
`tracks/core/JOURNAL-id.md` entries 7, 8 and the lead entry (T2e: lapse 1 and shift 0
held fixed is unstable for core's sharp bound ball, stable to t = 10 M for the smooth
marginally bound ball but with a steadily growing H in the edge region; the production
deposit lowers the core-shell error 55 times); `gauge/DIAGNOSTICS.md`;
`expball/README.md`; `coord/INTERFACES/spherical_id_format2.md`; the AthenaK sources of
the finder (`z4c/fastflow.cpp` options), of the trajectory and history outputs
(`particles/nrpic_io.cpp`), of the formatted-table output and of restarts
(`main.cpp`: command-line values override those of the restart file;
`driver.cpp`: the step is recomputed at the start of a restarted run, so changing
`time/cfl_number` at a restart takes effect [VERIFIED by reading the code, to be
confirmed in the logs of segment 2]).

Horizon-mass target of the source paper [VERIFIED, `refs/arxiv_2611.12831/src/main.tex`]:
line 945, Oppenheimer-Snyder fiducial run "relative error of Delta M/M_ADM <~ 1e-3";
line 1484, RMS relative horizon-mass error eps_M = 2.061e-3, 9.362e-4, 7.347e-4 for the
particle sequence A1-A3. Their quantity is the final mass after excision against the ADM
mass; ours is the mass of the first apparent horizon (0.08 of the total) against the
exact horizon mass of the same slice. Same order is the G2 criterion of the sheet.

Choices [JUDGEMENT]:
- Production deposit of `cosmo/README.md` (pcs cloud, compensation 1/6 and 7/15,
  b-spline metric, no filter) with `source_density` and `source_extrap`, because core's
  lead entry measured 24-55 times smaller shell errors with it than with the
  cloud-in-cell deposit of `stage/G1/STATUS.md` section 3.
- Resolutions: dx = M/2 (256^3 over [-64, 64]^3, the lead's plan) on the cards and dx = M
  (128^3, same domain; the h = M/2 lattice puts 8 sites per cell, symmetric about the
  centres) on the processors, which costs no card time. A run at dx = M/4 over the same
  domain needs 512^3 cells, more memory than one card has; it would need mesh
  refinement or a smaller domain (not in this package).
- Tracked particles (prep.py): the 100 nearest to each of R_i = 0.5, 1.2, 2.0, 2.4, 2.6,
  2.74, 2.8, 2.9, 3.0, 3.2, 4.0, 6.0, 8.0 M and 600 at random; dense between 2.6 and 3.2
  where the first horizon forms (R_i = 2.742) and grows.
- SR-1 step plan from the exact largest coordinate speed of light of the comoving
  coordinates (radial sqrt(1+2E)/|dR/drbar| and tangential rbar/R over all shells,
  not only the core's R_i/R), switching at 0.9 of cfl c = 0.618: cfl 0.25 to t = 42.0,
  0.03125 to 44.357, 0.0078125 to 44.447 (three segments instead of six; segment 2 is a
  little more expensive than the plan's staging but needs one restart less).
- Horizon finder: 16 polar points, l_max 8, mass tolerance 1e-6, 1000 iterations, flow
  constant 1, start radius 3.6 M coordinate (SR-1; the comoving radius of the shell
  R_i = 3.0 is 2.95 M) and 4.0 M (SR-2), from t = 44.2 (SR-1) and 46 (SR-2).

### Prediction P (SR-1, geodesic slicing), written before any run

Exact references: run A-20261115-130948-5a2b58a of the lead and, independently computed by
this package, the registered run of `prep.py` (entry 2). Core turnaround tau = 16.894,
R_max = 1.3398 R_i; first trapped sphere tau = 44.349 (R_i = 2.742, m = 0.0805); core
edge trapped 44.381; crunch 44.454.

- P1 stability: the run reaches t = 42 with finite fields and all particles; the mean
  relative Hamiltonian residual (cstat column Hr_mean) at t = 40 is not more than 10
  times its value at t = 2. Probability that P1 holds: about one half [JUDGEMENT; core's
  T2e grew steadily in the edge region of a smooth marginally bound ball, and blew up
  within 5 M for a sharp bound ball; our edge is a C^4 taper of half-width 1.5 M and the
  bound core is smooth].
- P2 comoving coordinates: |r/r_0 - 1| < 1e-4 and |tau - t| < 1e-6 for every tracked
  particle while P1 holds.
- P3 shells: at dx = M/2, largest |R/R_exact - 1| of the core shells below 2e-3 up to
  tau = 30, and below 1e-2 up to tau = 42; at dx = M the same errors 2 to 6 times larger.
- P4 turnaround of the core shells within 1 per cent of 16.894 in proper time and of
  1.3398 R_i in radius (dx = M/2); the mean error of the turnaround time below 0.05 M.
- P5 trapping per tracked particle (R(tau) falls through 2m): mean |Delta tau_AH| below
  0.01 M for the shells R_i in [2.6, 3.0] at dx = M/2. Reason: near the trapping time
  |dR/dtau| ~ 1 and R ~ 0.16, so Delta tau ~ eps R; with eps ~ 1e-2 this is 2e-3.
- P6 finder: first horizon found between t = 44.33 and 44.40 (the first finder call after
  44.349), mass within 5 per cent of 0.0805 at first detection and within 1 per cent of the
  exact m_AH(tau = t) afterwards (dx = M/2). Not reaching the source paper's 1e-3 at dx =
  M/2 is expected (the horizon is 5 to 6 cells in coordinate radius, 0.16 M areal).
- P7 Misner-Sharp mass along the x axis constant on the shells: relative error below
  1e-2 for r in [1, 9] M up to t = 42 (dx = M/2).
Refuted by: an instability before t = 42 (P1), a turnaround time off by more than 1 per
cent (P4), no horizon before the run ends (P6), or drifting particles (P2).

### Prediction Q (SR-2, conformal-time lapse with Gamma-driver), written before any run

Coordinate times from the lead's run A-20261115-130948-5a2b58a: core turnaround at
t = 13.82, the core's proper time reaches 44.349 at t ~ 49.5, crunch of the core at 54.96.

- Q1 turnaround of the core shells at tau = 16.894 within 1 per cent; R_max within 1 per
  cent.
- Q2 central lapse alpha_c = a(tau_c) within 1e-3 until a lapse front arrives. The run
  decides whether a front arrives from the taper. Prediction: a front does arrive,
  between t = 10 and 20 M (core's speed 0.58 from a surface at rbar ~ 8-9.5 M), and it is
  weaker than core's sharp-surface front: |alpha_c/a - 1| stays below 0.1 [JUDGEMENT].
- Q3 core shells: largest |eps| below 1e-2 before the turnaround (dx = M/2).
- Q4 the finder's first horizon lies on a slice where the particles at its radius have
  proper time >= 44.33, mass within 5 per cent of the exact horizon mass of that slice.
- Q5 the run reaches t = 53 (crunch of the core at 54.96) without an instability.
Refuted (for the gauge, not the data) by a front that spoils the core shells (error above
1e-2) before turnaround, or by an instability before the horizon.

### Common predictions

- C1 cost per cell and step on the card within a factor 2 of 8.1e-8 card-seconds (core's
  measurement at 192^3, quoted in `analysis/scouting_predictions.py`).
- C2 resolution: between dx = M and M/2 the core-shell error at tau = 16.9 falls by a
  factor between 2.5 and 6 (order 1.3 to 2.6) [JUDGEMENT: second order is expected from
  core's T2c, but dx = M puts only 2.4 cells across the core radius].

## 2026-11-15, entry 2: references, the processor attempt, smoke test of the comparison

Exact references, run A-emd-pbh-20261115-153719-91b03d1 (`prep.py`, registered by hand
with `runreg.py` because `harness/bin/nrpic-run submit` refused: "the worktree is not
clean", untracked manifests of other helpers of this worktree): core turnaround
tau = 16.893769, R_max/R_i = 1.339803; first trapped sphere tau = 44.349266 at
R_i = 2.74175 (rbar_i = 2.69731), m = 0.080505; core edge trapped 44.381466; crunch
44.454205; m_AH(tau) grows from 0.0805 to 0.0960 at the crunch (figure
`figs/fig_exact_references.png`, looked at: the trapping time per shell has its minimum
at R_i = 2.74 and the horizon mass rises steeply right after 44.349). These agree with
the lead's numbers (A-20261115-130948-5a2b58a) to the printed digits [VERIFIED].
1705 tracked particles; the reordered file has the same records as the lattice file
(checked in the run). SR-1 step plan from the exact largest coordinate speed: cfl 0.25 to
42.0 (the largest speed at 40 M is 1.6, in the compensating shells, not in the core),
0.125 to 43.63, 0.0625 to 44.18, 0.03125 to 44.357, 0.0156 to 44.423, 0.0078 to 44.447;
the run uses three segments: 0.25 to 42.0, 0.03125 to 44.3568, 0.0078125 to 44.4472.

Processor runs at dx = M (A-emd-pbh-20261115-153856-9d731b1 SR-1,
-153903-9d731b1 SR-2): STOPPED by me after 11 minutes at cycle 3. The release processor
executable runs on one thread (NLWP = 1) and took about 200 s per cycle at 128^3 on the
loaded machine (load 58); SR-1 would have needed about 19 hours. dx = M moved to the cards
(A-emd-pbh-20261115-155056-ec1b816, both gauges in one job, about 0.02 card-hours
expected). Card jobs queued behind core's verification runs.

Smoke test of `compare.py` on the first 0.75 M of the stopped SR-1 processor run (not a
result; output in `scratch/A-emd-pbh/tmp/smoke/`, not cited): every reader works; the
particles stay at their coordinates (r/r0 - 1 = 0, |tau - t| < 1e-15). Two findings about
the diagnostic itself:
1. The Misner-Sharp mass from the mesh line has a representation error at t = 0, before
   any evolution: 3 to 16 per cent for r in [2, 6] M at dx = M (the smoothed top-hat
   varies psi over 1 to 2 cells; 2m/R ~ 0.1 inside the ball, so the finite-difference
   error of dR/dr is amplified by R/m ~ 10-20). Changed: dR/dr now from a fourth-order
   difference along the line; the summary uses r >= 2 M only.
2. In the envelope (r = 7-9 M, where psi = 1 exactly and the t = 0 error is below 1e-4)
   the line mass already moves by about 3 per cent within 0.75 M at dx = M. Not explained
   yet [TO VERIFY with the card runs: deposit noise of 8 lattice sites per cell, or a
   transient of the data].
Amendment of P7, written before any output of the card runs was read: P7 is judged on the
drift m(t)/m(0) - 1 at fixed mesh points (SR-1) as well as on m/m_exact - 1, and the
threshold 1e-2 applies at dx = M/2 only; at dx = M the t = 0 representation error alone
exceeds it.

## 2026-11-15, entry 3: outcomes of P (SR-1) and Q (SR-2) at dx = M/2 and M

Runs (card, release core-v0.3, registered by hand with `runreg.py`): SR-1 dx = M/2
A-emd-pbh-20261115-153843-7172b66 (0.104 card-hours); SR-2 dx = M/2
A-emd-pbh-20261115-153845-7172b66 (0.149); SR-1 and SR-2 dx = M
A-emd-pbh-20261115-155056-ec1b816 (0.028 together). Analysis run
A-emd-pbh-20261115-163659-4dbacd0 (`compare.py`, `fields.py`; numbers in
`<label>_numbers.json` of its output directory; figures copied to `figs/`, every one
looked at). Two earlier analysis attempts failed on non-finite values and are on record
(A-emd-pbh-20261115-162133-208f933, -162237-a614467); -162359-d32d331 and -163141-73eb185
used the constraint columns shifted by one (corrected since; their numbers are not cited).
Card time so far 0.28 of the 1 card-hour of the package.

### SR-1 (lapse 1, shift 0 held fixed)

- P1 REFUTED. The run becomes non-finite at t = 33.0 (dx = M/2; first cells with a
  non-positive metric determinant at t = 32.875, within |x| <= 2.75 M) and at t = 30.3
  (dx = M). Largest |H| on the mesh (cstat): 0.014, 0.042, 0.051, 0.48 at t = 2, 10, 20,
  30 (dx = M/2); 0.014, 0.098, 0.24, 7.8 (dx = M). Where (`figs/sr1_n256_fields.png`,
  `sr1_n128_fields.png`): at t = 16.9 a grid-aligned ring of H in the outer part of the
  ball (r = 6-9 M, the compensating shell and the taper), at t = 30 a ring at the edge of
  the homogeneous core (peak at x, y = -2.25, -0.75, r ~ 2.4 M), where the collapsing core
  separates from the shells outside it and the comoving metric steepens. The growth is
  faster on the coarser mesh, so this is a truncation-error instability of the comoving
  coordinates, not the signature of an ill-posed system (that would grow faster on the
  finer mesh) [JUDGEMENT from two resolutions]. The finder (from t = 44.2) and segments
  2-3 were never reached: no horizon, no crunch; the restart segments were not run.
  Gauge pathology figures: `figs/sr1_n256_gauge.png` (constraint statistics, H on the x
  axis against t), `figs/sr1_n256_fields.png`.
- P2 HOLDS while finite: |r/r_0 - 1| < 1e-14 and |tau - t| < 6.3e-12 for every tracked
  particle (`sr1_coordinates` of the numbers file); the central lapse stays 1 to 4e-13.
- P3 REFUTED at dx = M/2: core shells, largest |R/R_exact - 1| 1.8e-3 at tau = 8,
  6.2e-3 at 16.9, 2.7e-2 at 30 (means 2.7e-4, 6.1e-4, -1.8e-3); the bound "below 2e-3 to
  tau = 30" fails after tau ~ 8. The largest errors sit at the core edge (band
  R_i = 2.4: mean -1.6e-2 at tau = 30).
- P4 HOLDS on the mean at dx = M/2: core turnaround proper time 16.871 against 16.894
  (mean error -0.022 M, -0.13 per cent; largest single particle 0.53 M, a parabola through
  three records 0.25 M apart on a flat maximum), largest areal radius +0.07 per cent
  (largest 0.6 per cent). Shells just outside the core: R_i = 2.4 band -0.26 M (-1.6 per
  cent), 2.6 band -0.37 M (-2.2 per cent), R_i = 3.2 band +0.18 M (+1.0 per cent): the 1
  per cent bound fails in the band where the instability later grows. At dx = M the core
  turnaround is 2.50 M early (-14.8 per cent) and R_max -2.5 per cent: dx = M does not
  resolve the 2.4 M core.
- P5, P6, P7: not testable (no collapse before the instability). The Misner-Sharp mass on
  the line drifts by more than 10 per cent by t = 17 at dx = M/2 (drift column of the
  numbers file), dominated by the grid-scale constraint violation; P7 REFUTED.

### SR-2 (conformal-time lapse, Gamma-driver)

- Q1 HOLDS on the mean at dx = M/2: core turnaround 16.937 against 16.894 (+0.043 M,
  +0.26 per cent), R_max +0.10 per cent; single particles up to 1.9 M off (flat maximum,
  wiggles of the lapse pulse). dx = M: -0.82 M (-4.8 per cent).
- Q2 REFUTED, and this is the main gauge finding: |alpha_c/a(tau_c) - 1| exceeds 1e-3 at
  t = 4.5, 1e-2 at 5.1, 0.1 at 6.6 (dx = M/2); 2.75, 4.75, 6.5 at dx = M. A lapse pulse
  reaches the centre from the edge of the homogeneous core, not from the taper (2.4-6 M
  at ~0.6 c gives t ~ 4-10), and grows the central lapse to 1.85 at t ~ 12 (exact 1.34)
  at both resolutions: a feature of the gauge, not of the mesh. Afterwards alpha_c stays
  near 1.2 while the core collapses (exact a -> 0), so the core runs through its proper
  time much faster than planned: the core's proper time reaches the crunch value 44.45
  near t = 35 instead of t = 55 (`figs/sr2_n256_gauge.png`, top left).
- Q3 HOLDS: core-shell |eps| before turnaround 2.0e-3 at tau = 12 (largest), 7.5e-3 at
  16.9. Later it grows: 4.0e-2 at tau = 30, 0.10 at 40, 0.31 at 44.
- Q4 REFUTED: no apparent horizon. The finder (from t = 46) found nothing, but the
  decisive fact is the resolution: the collapsed core sits inside the innermost cells.
  The largest 2m/R on the x axis (points beyond one cell from the axis) is 0.34, at
  t = 35.75 (`figs/sr2_n256_horizon.png`, right), and the innermost line point (r = 0.43
  coordinate) keeps R ~ 0.53-0.6 M throughout, while the first horizon has R = 0.161 M:
  in these near-Eulerian coordinates the horizon would be smaller than one cell of
  dx = M/2. The core's dust then passes through the centre and re-expands
  (`figs/sr2_n256_shells.png`, left; the proper time at the centre reaches 61 M), which
  a resolved collapse cannot do. Per particle, R(tau) falls through 2m (exact m) for 255
  core particles 0.23 M late on average (dx = M/2; first tracked particle at 44.495
  against 44.362 for its shell); 139 particles that should have been trapped never were.
- Q5 HOLDS: t = 53 reached, no non-finite values; largest |H| 0.077 at t = 44.
- Energy density at t = 30 shows a grid-aligned clumping of the envelope dust
  (`figs/sr2_n256_fields.png`, third row): the Gamma-driver moves the coordinates, the
  lattice no longer matches the cells, and the cubic cloud aliases [JUDGEMENT, not
  tested].

### Common

- C1 HOLDS: 354.8 s for 336 steps of 256^3 (SR-1) = 6.3e-8 card-s per cell-step; SR-2
  7.2e-8; within a factor 2 of 8.1e-8.
- C2 REFUTED on the high side: between dx = M and M/2 the largest core |eps| at
  tau = 16.9 falls by 9 (SR-1) and 2.8 (SR-2), the mean by 53 (SR-1); the turnaround-time
  error by 110 (SR-1) and 19 (SR-2). dx = M (2.4 cells across the core) is not in the
  asymptotic range; an order needs dx = M/4 (entry 4).
- Horizon-formation time and horizon-mass error against the source paper's 1e-3
  (main.tex:945, 1484): NOT MEASURED in any of the four runs (SR-1 unstable before the
  collapse, SR-2 cannot resolve a 0.16 M horizon at dx = M/2 in its coordinates).

## 2026-11-15, entry 4: a third resolution to t = 20 (prediction R, written before the runs)

Purpose: an order of convergence for the turnaround (G2 criterion "errors of the
turnaround time converge in mesh spacing") and the resolution dependence of the SR-1
instability and of the SR-2 lapse pulse. dx = M/4 on 256^3 over [-32, 32]^3 (512^3 over
the old domain does not fit on one card); the boundary at 32 M does not reach the core
(r <= 6 M) before t ~ 26 [JUDGEMENT: light speed ~1 from 32 to 6]; t = 0 -> 20 covers the
core turnaround (tau = 16.9; SR-2 reaches it near t = 11). New lattice of 2t with
h = M/4 (expball `particles.lattice`, n_lat = 76, one site per cell), tracked particles
chosen as before. Cost about 0.12 card-hours per gauge.

- R1 both runs reach t = 20 with finite fields.
- R2 core turnaround, mean proper-time error |Delta tau_ta| <= 0.02 M in both gauges;
  largest core |eps| at tau = 16.9 below 2.5e-3 (SR-1, 6.2e-3 at dx = M/2) and below 3e-3
  (SR-2, 7.5e-3 at dx = M/2): order >= 1.3 between M/2 and M/4.
- R3 SR-1 largest |H| at t = 20 below 0.051 (its dx = M/2 value; 0.24 at dx = M):
  the instability is driven by truncation error. Refuted by a larger value (the
  signature of an ill-posed system).
- R4 SR-2: |alpha_c/a - 1| exceeds 0.1 first between t = 6.0 and 7.0 (6.5 and 6.6 at
  dx = M and M/2) and the central lapse peaks at 1.8-1.9 near t = 12: the pulse is a
  property of the gauge.

## 2026-11-15, entry 5: state at the end of the session

- Resolution summary of dx = M and M/2: run A-emd-pbh-20261115-164733-b2aaf0c
  (`figs/fig_resolution_summary.png`, looked at): the SR-2 lapse pulse is the same curve at
  both resolutions; the SR-1 constraint violation grows exponentially after t ~ 20 with
  about the same rate at both resolutions, from a level 5 times lower on the finer mesh.
  Apparent orders between dx = M and M/2 (largest core |eps| at tau = 16.9): 3.2 (SR-1),
  1.5 (SR-2); turnaround-time error: 6.8 (SR-1), 4.2 (SR-2). Orders above 2 say that dx = M
  is outside the asymptotic range, so no order is claimed from this pair.
- The finder branch of `compare.py` (exact horizon mass of the same slice from the tracked
  particles' proper times) was exercised on a synthetic horizon file over the SR-2 dx = M
  outputs (scratch/A-emd-pbh/tmp/fake_finder, not a result): it runs, and it returns no
  exact horizon for a slice whose particles have not reached their trapping time, as it
  should. It has not met a real horizon.
- PENDING (queued, Slurm estimate several hours): dx = M/4 runs to t = 20,
  A-emd-pbh-20261115-164539-0b18e84 (SR-1, job 4461) and -164541-0b18e84 (SR-2, job 4462),
  prediction R in entry 4; close them with `runreg.py finish` and analyse them with
  `after_m4.sh` (README). Their outcome is not in this journal.
- NOT DONE: SR-1 restart segments (moot: unstable before t = 42); horizon-formation time
  and horizon-mass error (no horizon in any run; Requests in README); repeat of SR-1 with
  a new lapse condition (no `scratch/core/exe/core_gauge/READY` during the session; only
  core_requests-b and core_scalar-2 were published, neither with a lapse option).
- Card time: 0.28 card-hours used (0.104 + 0.149 + 0.028); the two pending runs ask at
  most 2 x 0.25 by their wall limits (about 0.12 each expected).

## 2026-11-15, entry 6 (lead of A-emd-pbh): outcome of prediction R (dx = M/4 to t = 20)

Runs closed with `runreg.py finish` by the lead: A-emd-pbh-20261115-164539-0b18e84 (SR-1,
357 s = 0.099 card-hours) and -164541-0b18e84 (SR-2, 361 s = 0.100), both exit 0 at t = 20.
Analysis with the commands of `after_m4.sh`, registered with `harness/bin/nrpic-run` (the
tree was clean): run A-20261115-182657-53da696 (`sr*_n256L32_*` figures and the updated
`fig_resolution_summary.png` in `figs/`, looked at). The lead's own reader agrees
(A-20261115-182314-bebd0cf: SR-1 mean dtau_ta -0.0125 M, largest core |eps| at 16.894
7.5e-4; SR-2 +0.0306 M, 3.4e-4).
- R1 HOLDS: both runs finite to t = 20.
- R2 HOLDS for SR-1 (mean turnaround error -0.0125 M, -0.074 per cent; largest core |eps|
  at tau = 16.894 7.6e-4 < 2.5e-3); for SR-2 the eps part holds (3.7e-4 < 3e-3) and the
  turnaround part FAILS (+0.031 M > 0.02 M). Apparent orders between M/2 and M/4: core
  |eps| at 16.894 3.0 (SR-1) and 4.3 (SR-2), at tau = 8 3.2 and 3.1; R_max 2.2 and 2.3;
  mean turnaround time 0.85 and 0.50. The turnaround time from a parabola through records
  0.25 M apart on a flat maximum is not in a clean power law; no order is claimed for it.
  Caveats: the dx = M/4 runs use a smaller domain ([-32, 32]^3) and a lattice with h = M/4
  (eight times more particles), so this is the joint limit of mesh and lattice.
- R3 HOLDS: SR-1 largest |H| at t = 20 is 0.040 (0.051 at M/2, 0.24 at M); but the run ends
  before the exponential phase that blows up the coarser runs after t ~ 20, so whether the
  finer mesh delays the blow-up is not tested.
- R4 HOLDS: SR-2 |alpha_c/a - 1| > 0.1 first at t = 6.625 (6.5 and 6.625 at M and M/2);
  central lapse peak 1.866 at t = 12.6 (1.80, 1.86): the pulse is a property of the gauge.
- Seen in `sr1_n256L32_fields.png`: at t = 16.9 the constraint-damping variable Theta is
  -5e-4 near |x| = 20, a signal from the outflow boundary at 32 M travelling inward through
  vacuum; the envelope edge is at R ~ 18 M then, the core is not reached before t = 20.


## 2026-11-19, entry 7 (wave 2b, helper runs3): set-up and predictions of SR-1L and BH-1, written before any card run

Read: CLAUDE.md, coord/CHARTER.md to "Owners", decisions 0010 and 0016, brief lines 335-365
and 708-725, the runs_ball report in `scratch/orch/wave2_reports/A-emd-pbh.md` and the
lead's, entries 1-6 above, HANDOFF.md of the owner; core's gauge package:
`scratch/core/exe/core_gauge/READY` and `tracks/core/JOURNAL-gauge.md` on branch core/gauge
(entries 1, 4, 5, 6). Core's executables of branch core/gauge (source b4430da), card and
processor. Core's test L3 (bound ball through collapse, AMR) never ran: run
core-20261115-203207-b4430da stopped at cycle 0 with "Number of MeshBlocks ... = 1632 ...
exceeds max_nmb_per_rank = 1024" (its athena.log) [VERIFIED]. So no collapse to a horizon
has been run with `lapse_leak` before this package.

The relaxed lapse (READY option 1): d_t alpha = [1+log] - lapse_leak alpha max(ln alpha, 0).
T = 1/lapse_leak = 0.125 M in both runs [JUDGEMENT: core's rule T <= 0.1 R/sqrt(2 alpha)
with R the smallest expanding region (2t: core radius 2.4 M; data set 3: 2.65 M) gives
T <= 0.17 M; core's bound-ball runs were best at the shortest T, and the step needs
rate x dt < 2.7: 8 x 0.25 = 2.0 at dx = M, 0.25 at dx = M/8]. Gamma-driver shift as core's
`ball_leak.athinput`; production deposit of SR-1/SR-2. Decks `sr1l.athinput`, `bh.athinput`
(commit 4b2c942 and following). Smoke test of both decks on 32^3 meshes with the processor
executable: run A-20261119-143417-ce697f0 (both exit 0 after 3 cycles; not a result).
compare.py gained the gauge `leak` (central lapse against the homogeneous reference) and
data sets other than 2t; its numbers for SR-2 at dx = M are unchanged (checked against
`A-emd-pbh-20261115-163659-4dbacd0/sr2_n128_numbers.json`: no differing value; check in
scratch/A-emd-pbh/tmp/runs3/regress, not a result).

Reference of the central lapse in a homogeneous core (run A-20261119-143309-1cc423f,
`lapse_ref.py`, figure fig_lapse_ref.png looked at): with zero shift at the centre,
d ln alpha/dt = 6 (da/dtau)/a - rate max(ln alpha, 0), d tau/dt = alpha. For 2t, rate 8:
alpha_c = 1.026, 1.016, 1.009, 1.003 at t = 2, 6, 10, 14; the core turns around at
t = 16.68; then plain 1+log: alpha_c = 0.948, 0.717, 0.436, 0.105 at t = 20, 25, 30, 40;
alpha_c < 0.1 at t = 40.3; the central proper time saturates at tau = 30.28, where
a/a_max = 0.846 = e^(-1/6) (1+log: alpha = 1 + 6 ln(a/a_ta) along a normal observer).
The source paper says of its Oppenheimer-Snyder run that the central lapse follows the
homogeneous expression only until the gauge characteristic from the surface reaches the
centre and stays above that "analytic lower limit" afterwards
(refs/arxiv_2611.12831/src/main.tex:943) [VERIFIED]: the reference is a lower bound once a
signal from the core edge has arrived.

### Prediction S (SR-1L: data set 2t, relaxed lapse; dx = M and M/2 over [-64, 64]^3 to t = 44, dx = M/4 over [-32, 32]^3 to t = 24)

- S1 stability: all three runs reach their end with finite fields; at dx = M/2 the mean
  |H| (cstat) at t = 40 is at most 10 times its value at t = 10. Probability about 0.6
  [JUDGEMENT: core's bound ball with this lapse grew by 2.3 in 10 M; ours runs 4 times
  longer and collapses].
- S2 no lapse front before turnaround: |alpha_c/alpha_ref(tau_c) - 1| <= 0.02 for t <= 16
  at dx = M/2 and M/4 (SR-2: 0.39; core's bound ball with T = 0.125 M: 0.17 per cent).
- S3 after turnaround the central lapse stays at or above the reference
  (alpha_c/alpha_ref - 1 >= -0.02 for 16 <= t <= 44, dx = M/2), and the central proper
  time at t = 44 lies between 29.9 and 40 (reference 29.96; exact first trapping 44.35):
  the centre does not reach the proper time of the first trapped sphere and no apparent
  horizon is found at any resolution [JUDGEMENT; the first horizon of 2t is also unresolved
  at these meshes, entry 3].
- S4 shells: largest core |R/R_exact - 1| at tau = 16.894: between 1e-3 and 5e-3 at dx = M/2
  (SR-1 6.2e-3, SR-2 7.5e-3), below 1.5e-3 at dx = M/4 (SR-1 7.6e-4, SR-2 3.7e-4), above
  1e-2 at dx = M (SR-1 5.6e-2, SR-2 2.1e-2). Mean core turnaround proper-time error
  |dtau_ta| <= 0.03 M at dx = M/2 and <= 0.02 M at dx = M/4; mean R_max error within 0.2
  per cent at both.
- S5 order: the core |eps| at tau = 16.894 falls by at least 3 from dx = M/2 to M/4.
- S6 coordinate light speed alpha/sqrt(g_rr) on the x axis stays below 1.5 for t <= 20
  (core's L1: 1.13 for T = 1 M; SR-2 reached 1.85 x lapse).
Refuted (for this gauge on 2t) by: a non-finite run before its end, a central-lapse
departure above 5 per cent before t = 16 (a front), or a core error at tau = 16.894 above
SR-2's 7.5e-3 at dx = M/2.

### Data set 3 and prediction B (BH-1: collapse through horizon formation)

Data set 3, run A-20261119-143524-334e553 (`prep_bh.py`; supersedes -142341-4b2c942, the
same data without the table breaks), figure fig_bh_exact.png looked at: expball compensated
top-hat, H R_b = 0.7 (R_b = 4.082 M, H = 0.1715/M, t_i = 3.887 M), delta_c = 1.5 inside
R1 = 0.65 R_b = 2.653 M, underdense shell (density 0.293 rho_b) to R2 = 0.95 R_b, Einstein-
de Sitter to the C^4 taper at R_b (half width 0.168 M, so that the matter edge is at rbar
= 4.25 M = 34 x M/8 ... a lattice site per cell at dx = M/4, M/6, M/8); M = 1.00046, rest
mass 1.14594, psi(0) = 1.1043, largest 2m/R on the slice 0.518 (at the core edge); table
breaks at rbar = 2.49367 and 3.87755 (the jumps of KL). Exact (expball/exact.py): core
turnaround tau = 3.3716 at R_max = 1.1623 R_i; the first trapped sphere is the core edge,
R_i = 2.65306, at tau_AH = 9.55109 with m = 0.686563, R_AH = 1.37313 M (from R_max: a
compression of 2.25, against 23 for 2t); crunch 10.6305; the horizon then grows by the
infall of the underdense shell, m_AH(tau) = 0.69610, 0.70437, 0.71804 at tau_AH + 2, 4, 8;
the matter edge is at R = 9.45 M at tau_AH; no shell crossing before the crunch.
Homogeneous lapse reference (rate 8): alpha_c < 0.5 at t = 6.46, < 0.1 at t = 9.49, the
central proper time saturating at 6.90 < 9.55: with a homogeneous lapse the slices would
freeze before the edge traps; the horizon forms only if the lapse at the core edge is held
up by the region outside, as in the source paper's Oppenheimer-Snyder run [JUDGEMENT].
Runs: dx = M/4, M/6, M/8 on 128^3, 192^3, 256^3 cells over [-16, 16]^3 with the lattices
n_lat = 34, 51, 68 (one particle per cell; 20672, 69599, 164968 particles), to t = 16;
particles excised where alpha < 0.1 (as problems/os/os_amr.athinput); finder from t = 8
every 0.125 M, initial coordinate radius 3.0. The outflow boundary at 16 M is reached by
the matter edge after t ~ 14 and its light signal reaches r ~ 3 M near t ~ 13.

- B1 the three runs reach t = 16 (no non-finite value in the histories and line outputs
  outside the excised region) [probability about 0.6].
- B2 the finder reports an apparent horizon in all three runs, first between code time 9
  and 14.
- B3 time of the first horizon: at the finder's first detection, the proper time of the
  tracked particles at its mean coordinate radius exceeds the exact tau_AH of their own
  shell by 0 to 0.5 M at dx = M/8 (cadence 0.125 M of coordinate time, lapse at the horizon
  0.3-0.7); the first slice that contains a trapped round sphere by the particles' own
  proper times (compare.py `first_trapped_slice`) precedes the finder's first detection
  by less than 0.5 M. Per tracked particle of the core-edge bands, the mean of
  tau_AH(numerical, R falls through 2m) - tau_AH(exact) lies within +-0.1 M at dx = M/8.
- B4 horizon mass: the finder's irreducible mass sqrt(A/16 pi) against the exact horizon
  mass of the same slice (the Misner-Sharp mass of the outermost shell that has trapped on
  that slice): |m_irr/m_exact - 1| at first detection and as median over the first 4 M
  after it below 2e-2 (M/4), 1e-2 (M/6), 5e-3 (M/8), falling with dx at order >= 1. Against
  the source paper's level (Delta M/M_ADM <~ 1e-3, main.tex:945; RMS 2.1e-3 to 7.3e-4 over
  A1-A3, main.tex:1484) the error at dx = M/8 is predicted 2 to 5 times larger [JUDGEMENT:
  R_AH = 11 cells of M/8, against the AMR of the source; the horizon forms on the jump of the
  top-hat density].
- B5 shells: largest core |eps| at tau = 3.37 (turnaround) below 2e-3 at dx = M/8, at
  tau = 9.0 below 2e-2.
- B6 lapse: alpha_c follows the homogeneous reference within 2 per cent to t = 2 and then
  departs above it before t = 6 (the signal from the core edge needs about 2.65/1.4 = 2 M).
Refuted by: no horizon at dx = M/8 by t = 16 (B2), a horizon-mass error above 5e-2 at
dx = M/8 (B4), or a run that goes non-finite before the first horizon (B1).

Card budget of this package: at most 2 card-hours. Plan: one Slurm job of six runs,
estimated 0.55-0.65 card-hours (1.1-1.3 card-seconds per step at 256^3, C1 of entry 3).

## 2026-11-19, entry 8: checks of data set 3 while the card job waits (Slurm 4642 queued)

(a) Exact events by a second method, run A-20261119-144737-b04a84e (`verify_ds3.py`,
figure fig_verify_ds3.png looked at): direct integration of d^2R/dtau^2 = -m/R^2 from the
initial slice against the closed-form cycloid of expball/exact.py for six shells (inside
the core, at its edge, in the underdense shell): turnaround and trapping times and R(tau)
agree to 1.5e-13 relative; the core mass in closed form, (1 + delta_c) H^2 R1^3/2 =
0.6865625, equals the first-trapped mass of exact.json [VERIFIED]. First trapped sphere
tau_AH = 9.551091948 at the core edge; the shell 0.02 M outside traps at 9.913.

(b) Prediction, written before the run: offline constraint residuals of the exact slice
(`constraints_ds3.py`, expball's finite differences, octant meshes N = 32 ... 256 over
1.25 times the matter radius): away from the non-smooth radii (band 0.1 R_b) order 2.0 and
4.0 (+-0.1 on the last pair) for the second- and fourth-order stencils, for H and M, as for
data set 2 (expball/README.md); over all cells the top-hat jumps leave a Hamiltonian band
that converges at order about 1/2 in L2 and a momentum band whose L2 norm grows as
h^(-1/2) (expball/README.md, "Over all cells ..."). Refuted by an order below 1.8 away from
the jumps.

Outcome of (b), run A-20261119-144826-e875712 (figure fig_constraints_ds3.png looked at;
its x tick labels overlap, cosmetic): HOLDS. Away from the non-smooth radii the orders of
the last three pairs are 2.02, 2.00, 2.00 (H) and 2.00, 2.00, 2.00 (M) with second-order
differences, 4.00, 4.00, 4.00 (H and M) with fourth-order ones; L2 residuals at N = 256
(h = 0.021 M) 1.1e-5 (H) and 1.5e-5 (M) of 6H^2. Over all cells the top-hat jumps give
H L2 orders 0.51, 0.51, 0.49 and M L2 orders -0.40, -0.47, -0.50 (the h^(-1/2) growth of a
one-cell band of an O(1/h) residual), as predicted. The data are the exact constraint-
satisfying slice except at the jumps, where any mesh sees a discontinuity of K_ij and of
the density; the code will start with that band.

## 2026-11-19, entry 9: a coarse processor run of BH-1 while the card job waits (prediction first)

The card job (Slurm 4642) is estimated to start between 10:00 and 13:00 PST. The
processor executable of core/gauge is serial (scripts/build_cpu.sh: Kokkos Serial), so
only a coarse mesh fits: BH-1 at dx = M/2 (64^3 over [-16, 16]^3, lattice n_lat = 17,
h = M/2, one particle per cell), t = 0 -> 16, same deck. Purpose: learn early whether the
relaxed lapse lets the edge of the core trap at all (B2), and a fourth resolution.
Prediction [JUDGEMENT]: the run reaches t = 16; the finder reports a horizon between t = 9
and 14 (R_AH = 1.37 M is only 2.7 cells, so it may also fail: probability of a detection
about 0.6); if found, |m_irr/m_exact(slice) - 1| below 0.1 at first detection; core-shell
largest |eps| at the turnaround (tau = 3.37) below 2e-2.

Outcome of entry 9, run A-20261119-145154-c40f0ce (processor, 4300 s), analysis
A-20261119-155636-dbc2e1b (`compare.py`, `fields.py`; figures bh_n64_gauge.png,
bh_n64_shells.png, bh_n64_horizon.png, bh_n64_fields.png in figs/, each looked at). The
finder writes its summary into the working directory, which for this processor run was
the run directory, not bh_n64/: linked into bh_n64/ before the run was closed.
- Reaches t = 16 with finite fields: HOLDS.
- Horizon: REFUTED. The finder found nothing at any of its 65 searches (t = 8 ... 16).
  The largest 2m/R on the x axis reached 0.80 at t = 12.25; by then the areal radius of
  the innermost line point (coordinate r = 0.43 M) had grown to 1.37 M, the exact R_AH:
  the 1+log/Gamma-driver coordinates squeeze the collapsing core into the first one or two
  cells of dx = M/2, where no horizon can be represented (the same failure as SR-2 on 2t,
  one scale up).
- Core |eps| at the turnaround (tau = 3.37): 1.4e-2 < 2e-2, HOLDS; core turnaround mean
  -0.085 M (-2.5 per cent), R_max -0.39 per cent. Later the core shells fall ahead of the
  exact solution: largest |eps| 0.054 at tau = 6.46, 0.15 at 8.55, 0.60 at 9.55; per
  particle, R falls through 2m 0.40 M EARLY on average (261 core particles), the
  numerical R of the core being too small.
- Gauge, recorded as a pathology at this resolution (bh_n64_gauge.png): the central lapse
  follows the homogeneous reference within 2 per cent to t = 3.6 (0.04 per cent to t = 2)
  and then stays far above it (0.86 at t = 6 against 0.49; reference 0.06 at t = 7), as
  the source paper's OS lapse does (main.tex:943); but it never collapses: minimum 0.48
  at t = 12.5, then it RISES to 0.93 at t = 16 while the central proper time passes the
  exact crunch (10.63) at t = 13.6 and the central density falls to the background: the
  core's dust passes through the centre and re-expands, as in SR-2. Largest |H| grows from
  0.034 (t = 8) to 3.3 (t = 14) in the central cells (bh_n64_fields.png: a 2-3 cell
  checkerboard of H and Theta at the centre from t = 8). 515 particles with rest mass
  0.768 were removed by the excision (alpha < 0.1 is never reached at the centre on the
  history probe; which criterion removed them is not established) between t = 14 and 16.
Conclusion for the card runs [JUDGEMENT]: dx = M/2 is below the resolution at which this
gauge forms a horizon for data set 3; dx = M/8 puts about 4 times more cells across the
collapsed core. Nothing in the queued job is changed.

## 2026-11-19, entry 10: BH-1R, one refined level (prediction, written before the run)

Reason: at dx = M/2 the 1+log/Gamma-driver coordinates put the collapsing core of data set
3 into the first one or two cells (entry 9); with the same behaviour the horizon would
lie at a coordinate radius of 0.4-0.8 M, 3 to 6 cells of the finest uniform mesh of the
queued job (M/8). BH-1R adds one static level, cells of M/16 inside [-4, 4]^3 (deck
`bh_smr.athinput`), with a lattice of h = M/16 (n_lat = 136; one particle per fine cell),
t = 0 -> 16, a second card job (estimated 0.45 card-hours; with the queued job about 1.05
of the 2 allowed).
Prediction [JUDGEMENT]: the run reaches t = 16; the finder finds the horizon, first
between t = 9 and 14; at first detection the proper time of the particles at the horizon
exceeds the exact tau_AH of their shell by 0 to 0.3 M; |m_irr/m_exact(slice) - 1| below
3e-3 at first detection and as median over the first 4 M (between the M/8 bound of B4 and
the source paper's ~1e-3); core-shell largest |eps| at the turnaround below 1.5e-3.
Refuted by: no horizon by t = 16, or a mass error above 1e-2.

Amendment of entry 10, written after a first look at the BH-1 run at dx = M/8 of the card
job (bh_n256 finished at 08:45; the registered analysis follows in entry 11) and before
BH-1R is submitted: in bh_n256 the finder (start radius 3.0 M, 1000 iterations,
tolerance 1e-6) reported nothing in 65 searches, while the Misner-Sharp mass on the x axis
(read directly from the table outputs, not yet a registered number) shows a trapped point
(2m/R > 1 with K_T > 0) from t = 11.0 at coordinate radius 0.45 M, then at 0.21-0.33 M:
the trapped region lies within 2 to 4 cells of M/8; the run went non-finite near
t = 15.5. Core's L3 (JOURNAL-gauge.md entry 9 on branch core/gauge) found the horizon of
its bound ball with initial coordinate radius 1.0 M, 400 iterations, tolerance 1e-5 (the
settings of problems/os/os_amr.athinput). BH-1R therefore uses those finder settings,
from t = 9 (`bh_smr.athinput`). The prediction of entry 10 is unchanged except that the
first detection is now expected between t = 10.5 and 13.

## 2026-11-20, entry 11 (wave 3, helper runs_ball): outcomes of S (SR-1L) and B (BH-1)

State found at 14:17 PST: both card jobs finished on 2026-11-19 (Slurm 4642: 08:36-09:03,
4665: 12:02-12:32, sacct COMPLETED; every line rc = 0 in batch.list.status), both manifests
still "submitted", no analysis registered, no manifest whose parent is one of the two card
runs, no scratch directory of a cut-off session of this package. `after_runs3.sh` was
changed to take an optional part (runs3 | bh_smr; default all unchanged, commit d58b4a1),
because its first part copies figures into figs/ and nrpic-run refuses a dirty package for
the second registration. Registered analysis: see the outcome below (written after the run).

## 2026-11-20, entry 12: outcome of entry 10 (BH-1R, one refined level)

Written after the registered analysis of BH-1R (see below).

## 2026-11-20, entry 13: a turnaround estimator that does not depend on a fit window (prediction T, written before the estimator met any run)

Why: the verifier (stage/G1/VERIFIER.md section 2.4, finding 6, section 4 point 1) found
that the SR-2 turnaround error at dx = M/4 is +0.031 M with the three-point vertex of
compare.py but +0.0245, +0.0156, +0.0088 M with least-squares parabolas over +-2, 3, 5
records, while SR-1 does not depend on the window. [BACKGROUND, derivation] The exact
R(tau) of a dust shell is a cycloid, R = A (1 - cos eta), tau + t0 = B (eta - sin eta), which
is EVEN about its turnaround (R depends on eta - pi through cos, tau - tau_ta is odd in
eta - pi), so a symmetric parabola window has no bias from the shape; near the maximum
R/R_max = 1 - s^2/(16 B^2) + O(s^4) with s = tau - tau_ta. A perturbation of relative
amplitude e and angular frequency w moves the local maximum by s ~ 8 B^2 e w: for the
core of 2t (B = T0, about 8.9 M) a wiggle of e = 1e-5 with a period of 3 M moves it by
about 0.013 M. The local maximum is therefore set by the small wiggles of the lapse pulse
(SR-2), not by the secular motion of the shell, and its value depends on how much of the
record a local fit smooths. [JUDGEMENT] A useful turnaround time for G2 is that of the
shell's secular motion: the turnaround of the cycloid that best fits the whole record.

Estimators (script `turnaround.py`; defined here before use):
- V3: vertex of the parabola through the three records around the largest R (compare.py).
- Pk: least-squares parabola over the 2k+1 records around the largest R, k = 2..8.
- S: smoothing spline with the smoothing chosen by generalized cross-validation
  (scipy.interpolate.make_smoothing_spline, lam = None) over the records with
  tau <= 2 tau_ta(exact); its maximum.
- C (primary): least-squares fit of the three-parameter cycloid (A, B, t0) to all records
  with 0 <= tau <= 2 tau_ta(exact) (the expansion and its mirror; the crunch region is left
  out); tau_ta = pi B - t0, R_max = 2 A. The exact shell is the starting guess. Window study
  C(W): records with |tau - tau_ta(exact)| <= W, W = 2, 3, 4, 6, 8, 12 M and the whole
  range; C_exp: the expansion only, 0 <= tau <= tau_ta(exact).
- O: the exact cycloid of the particle's own shell with a free time offset d and a free
  scale s, R = s R_exact(tau - d), on the same records as C; tau_ta = tau_ta(exact) + d.
Reported per run: mean over the core particles (R_i <= 2.4) of tau_ta - tau_ta(exact) and
of R_max/R_max(exact) - 1, and the spread of the per-particle values.

Prediction T [JUDGEMENT]:
- T0 (synthetic, the estimator itself): an exact core cycloid sampled every 0.25 M with a
  random phase and shifted by d = 0.02 M: C and O recover d within 1e-4 M for every
  window, V3 within 2e-3 M; with a superposed wiggle 1e-5 R_max sin(2 pi tau / 3 M) the
  parabola family Pk varies with k by more than 5e-3 M while C on the whole range stays
  within 2e-3 M of d.
- T1 SR-1 (M/2, M/4): C within 0.005 M of V3 (-0.022, -0.0125 M); C(W) varies by less than
  0.005 M over W >= 3 M.
- T2 SR-2: at M/4 C lies in [-0.005, +0.02] M, at M/2 in [0, +0.04] M (V3 +0.043); C(W)
  varies by less than 0.01 M over W >= 6 M while Pk varies by more than 0.015 M over
  k = 1..5. With C, the turnaround part of R2 (mean |dtau_ta| <= 0.02 M at M/4) HOLDS for
  SR-2 (probability about 0.6).
- T3 S lies within 0.005 M of V3 in every run (both measure the local maximum of a smooth,
  nearly noise-free record).
- T4 SR-1L: C gives mean |dtau_ta| <= 0.03 M at M/2 and <= 0.02 M at M/4 (the bounds of S4);
  at dx = M more than 0.3 M.
- T5 O agrees with C within 0.005 M for SR-1 and SR-1L at M/2 and M/4.
Refuted, for the claim "window independent", by C(W) varying by more than 0.01 M over
W >= 6 M in any run at M/2 or M/4.
SR-1 breakdown times (verifier finding 5): the same script reads the raw files of the four
SR-1 runs and lists, per criterion, the first time: non-positive metric determinant in
athena.log, largest |H| > 1e10 and first non-finite record in cstat.hst, first non-finite
record of z4c.user.hst and nrpic.hst, first non-finite line output; expected [VERIFIED by
the verifier, to be reproduced]: 32.875 / 30.25, 33.0 / 30.5, 33.125 / 30.75, 33.25 / 31.0
(dx = M/2 / M).
