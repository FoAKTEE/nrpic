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
