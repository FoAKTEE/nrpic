# G1 status of A-emd-pbh (2026-11-15, updated by the lead after wave 2)

Gate G1 "pre-core baseline" (charter 9.2) with the track-specific criteria of the sheet
(charter 9.4) as amended by decision 0013 ("the G1 scan-design criterion is met on the
reference-based design; the Newtonian-mode runs are G2 work"). Harness checklist:
`CHECKLIST.md`; report `STAGE_REPORT.md`; the lead's review of the wave-2 helpers
`../REVIEW-wave2.md`. Lead's reading: **all three track criteria are met** (T3 by
decision 0013, and the Newtonian runs were made as well); the common item "analysis
pipeline validated" is now met; what G1 still lacks is the data-flow schematic of the
minimum figures and a verifier's recomputation of the note's ledger (`CHECKLIST.md`). The
gate is the orchestrator's to pass.

## 1. Track-specific criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| T1 | Constraint residuals of A-pre-1 converge at the expected order | **MET** | Offline finite-difference residuals on octant meshes N = 32-256, L2 norms over the region farther than 0.1 R_b from non-smooth radii: flat ball momentum orders 2.00, 4.00; compensated top-hat 2.00/4.00 (H and M); C^4 edge taper 1.99/3.90 over all cells; smoothed top-hat (data set 2) 3.98 (H) and 3.94 (M) at order 4 with N = 512 (runs A-emd-pbh-20261115-121654-6bfb707 / -122121-aa1c84d, -122117-aa1c84d). Lead's rerun A-emd-pbh-20261115-130402-f5566fb: 901 values identical; figure looked at. Table format 2 reproduces the exact-field residuals to 6e-7 and converges at order 4 (same runs). Independent checks: expball's generator equals core's independently written `python/nrpic/expanding_ball.py` to 5e-15 for the sharp marginally bound ball (L2) and expball's table rule equals core's reader evaluator to 7e-18 (L3), run A-20261115-130257-a7374a4. Qualification: over all cells a sharp edge does not converge (O(1/h) momentum band); evolution data therefore use the taper (SCOPE.md 10.3). AthenaK's own t = 0 constraint norms for these tables are not yet measured (needs the merged reader; core measured its own tables, `tracks/core/JOURNAL-id.md` entry 3). Limit found by the verifier (VERIFIER.md C5): the constraint test cannot tell the ball from its time reverse (K -> -K gives the same residuals); closed in wave 2 by evolution: in SR-1 and SR-2 the core shells expand and turn around at proper time 16.87 and 16.94 against the exact 16.894 (runs A-emd-pbh-20261115-153843-7172b66, -153845-7172b66; lead's reader A-20261115-182314-bebd0cf). |
| T2 | Prediction table of A-pre-2 | **MET** | `criteria/predict.py` prints rows R1-R10 (hoop, Kerr-bound spin, finite duration, exact top hat, two dispersion criteria, small-scale dispersion, profile/zeta_rms, shot noise) for (delta, e, p, sigma_v, a_end/a_H); example tables in run A-emd-pbh-20261115-120425-80492f8. Final check run A-emd-pbh-20261115-115120-2eb3117: 37 checks against printed numbers of the five papers, 33 pass; the four failures are on record (two last-digit roundings in the papers, two agreement bands set too tight) in `criteria/JOURNAL.md`. Lead's rerun A-20261115-130252-01e8b64: see section 4. Nine disagreements between the criteria over the brief's range in `criteria/README.md`. Correction: the table's delta is the central contrast, 12 mu/5 for the profile of arXiv:2609.14218, while the threshold definition uses the mean in r_m, 0.883 mu (SCOPE.md 10.1). |
| T3 | Scan design from A-pre-3 | **MET** (decision 0013; wave 2 adds the Newtonian-mode runs: top-hat second order, t_ta +7.2e-4 at 128^3; 14 scan points within 2.2e-4 to 6.3e-4 of the isolated ellipsoid; range of the full-relativity scan in `newton/SCAN.md` section 8; runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, analysis -164420-4528861, range -164757-b8bc9a3; lead's reruns A-20261115-182402-a46812c identical, own estimator A-20261115-182314-bebd0cf agrees). Wave-1 text: | `newton/SCAN.md`: 32 runs in AthenaK's Newtonian mode (shapes, amplitude, paper case, ball radius, particle number, mesh), N = 1e6, 128^3 root with two levels, cost <= 11 card-hours, acceptance tests for core's implementation (section 5), inputs `make_ic.py` lacks (section 4), and the horizon limit on the ball radius for the GR scan, delta_L (1 + 3e + p) < 1.5 (R_L/R_ball)^2 (section 3). References validated (P1-P7, run A-emd-pbh-20261115-113103-9832afd; rerun A-emd-pbh-20261115-130252-4290486 identical). What is missing: the brief asks for the design to be fixed by running the Newtonian precursor; under decision 0010 that run needs core's Newtonian mode (`core/newton`, no commit with the mode yet), so the design rests on the semi-analytic references. Decision asked of the orchestrator: accept T3 on the reference-based design, with the Newtonian-mode runs moved to G2. |

## 2. Common G1 evidence (charter 9.2)

| Item | Status | Evidence |
|---|---|---|
| Baseline results obtainable without the NRPIC coupling | MET | exact expanding-ball solution and two data sets (`expball/`, runs -121749-90764e1, -121753-90764e1, and data set 2t -130609-947c898); homogeneous-ellipsoid and top-hat references (`newton/`); the analytic criteria (`criteria/`); lapse toy and von Neumann limits (`gauge/`, runs -113614-374a41a, -113755-cac3c4b) |
| Analysis pipeline validated on them | MET (wave 2) | the invariant comparison `runs_ball/compare.py` exists and recovers the exact solution in AthenaK runs (core-shell |R/R_exact - 1| 7.6e-4 at tau = 16.894, dx = M/4, A-20261115-182657-53da696), independently re-derived by the lead's own reader (A-20261115-182314-bebd0cf); `newton/analyze_newton.py` against the cycloid and the ellipsoid on Newtonian-mode runs (above); the periodic `analyse_scouting.py` reproduced byte for byte (A-20261115-182347-8ee3fcc). Wave-1 text: PARTLY | `newton/compare_snapshots.py` recovers the first-collapse time to 1.2e-5 on synthetic AthenaK-format snapshots (run -113822-87cba08, rerun -130300-efc25b0); the gauge analysis ran on existing AthenaK cosmology runs (bh1, bh2, kd; runs -113921-ca3786e, -113810-e02c969). The invariant comparison of `gauge/DIAGNOSTICS.md` section 3 (proper time of particles against areal radius of their shell; finder mass against tau_AH) has no script yet; it is needed for SR-1/SR-2 |
| Interface proposals submitted | MET with this commit | outbox requests to core (section 5) |

## 3. The first two full-relativity scouting runs (to start when `core/id-extrinsic` is merged)

Both start from **data set 2t** (run A-emd-pbh-20261115-130609-947c898, files in
`/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/`): expball
smoothed top-hat core (mean contrast Delta = 1 inside R1 = 2.4 M, compensated at R2 = 6 M,
simultaneous bang time) inside an Einstein-de Sitter ball with H R_b = 0.5 (R_b = 8 M,
t_i = 10.667 M), C^4 edge taper of half width 1.5 M (matter to rbar = 9.5 M), total mass
M = 1.0096, rest mass 1.0159, psi(0) = 1.0138; table `..._w0p1875.tab` (format 2, 6001 rows,
drbar = 0.002375, exterior pg, alpha = 1, betar of the dust's proper-time slicing);
particles `..._w0p1875_lat38.nrp` (28768 lattice sites at (k + 1/2) h, h = 0.5 M, masses
rho psi^6 h^3, u_i = 0), which sit on the cell centres of a dx = M/2 mesh with a cell face
at the origin. End-to-end check passed (run A-emd-pbh-20261115-130846-947c898).

Common settings: `problems/ball/ball.athinput` of core (`pgen_name = nrpic_cf`,
`comp0_type = table`, `lapse = table`, `shift = zero`), mesh 256^3 over [-64, 64]^3 M
(dx = M/2; the boundary stays further than the light travel time from the matter for the
whole run, core's finding on the outflow condition), `particles/source_density = true`,
`particles/source_extrap = true`, trajectories of ~2000 tracked particles in shells
(R_i = 0.5, 1.2, 2.0, 2.4, 2.74, 3.2, 4.0, 6.0, 8.0 M), horizon finder centred at the
origin with an initial coordinate radius of 2.7 M from the times given below.

**SR-1: geodesic slicing** (lapse 1 and shift 0 held fixed: `z4c/lapse_oplog = 0`,
`z4c/lapse_harmonic = 0`, no advection, no Gamma-driver; core's case T2e, gauge rank 1 of
`gauge/GAUGE.md`). Coordinates stay comoving and t equals the proper time of every particle.
The radial coordinate speed of light in the collapsing core grows as R_i/R, so the step must
shrink in stages (restart with a smaller `time/cfl_number`): 0.25 to t = 42.30, 0.125 to
43.73, 0.0625 to 44.21, 0.03125 to 44.37 (largest stable C v = 0.618, gauge T2). Cost
0.15 card-hours (run A-20261115-130948-5a2b58a).

**SR-2: conformal-time lapse** (`z4c/lapse_oplog = 0`, `z4c/lapse_harmonic = 1/3`,
Gamma-driver `shift_Gamma = 0.75`, `shift_eta = 2`, cfl 0.25; core's most accurate measured
configuration, `tracks/core/JOURNAL-id.md` entry 7). In the homogeneous core alpha = R/R_i
and the coordinate speed of light stays near 1. tlim = 52 M. Cost 0.16 card-hours.

**Predictions** (expball exact solution, run A-20261115-130948-5a2b58a; invariants unless
marked):

| Event | Proper time tau / M | SR-1 coordinate t | SR-2 coordinate t |
|---|---|---|---|
| turnaround of every core shell (R_i <= 2.4), R_max = 1.3398 R_i | 16.894 | 16.894 | 13.82 |
| first trapped sphere: shell R_i = 2.742 (rbar_i = 2.697), m = 0.0805, areal radius 0.161 | 44.349 | 44.349 | ~49.5 (core at that tau) |
| core edge R_i = 2.4 trapped (m = 0.054) | 44.381 | 44.381 | |
| crunch of the core | 44.454 | 44.454 | 54.96 |
| envelope R_i >= 6 never turns around, R = R_i (1 + 3 tau/32)^(2/3); matter edge at R = 28.4 M at tau = 44.35 | | | |

Expected outcome and what refutes it:
- SR-1: particles stay at their coordinates (|r/r_0 - 1| < 1e-4) and t equals their proper
  time to 1e-6 (core's prediction T2e); the core shells follow the cycloid with largest
  relative areal-radius error below 2e-3 to tau = 30 (core measured 5.9e-4 over 12 M with the
  smooth-edge marginally bound ball at dx = M/2); the finder reports a first apparent
  horizon between t = 44.349 and 44.454 with area mass 0.0805 within 5 per cent. Refuted by
  an instability before t = 42 (geodesic slicing with a frozen shift is not known to be well
  posed, BACKGROUND), by a turnaround time off by more than 1 per cent, or by no horizon
  before the run ends.
- SR-2: turnaround at the shells' proper time 16.894 within 1 per cent; central lapse equal to
  R/R_i of the core within 1e-3 until a lapse front arrives; the finder's first horizon on
  a slice whose particles at its radius have proper time >= 44.349 (minus the error), mass
  0.0805 within 5 per cent. Open question the run decides: whether the conformal-time lapse
  sends a front from the taper to the centre (core saw speed 0.58 from a sharp surface; from
  rbar ~ 8 M it would arrive near t ~ 11-14 M, before the core's turnaround). Refuted (for
  the gauge, not the data) by a front that spoils the core shells (error above 1e-2) before
  turnaround.
- Both: the measured cost per cell and step within a factor 2 of 8.1e-8 card-seconds.

Dependencies: the merge of `core/id-extrinsic`; core's outcome of T2e (if geodesic slicing is
unstable, SR-1 is replaced by SR-2 at dx = M/4); the input keys of the horizon finder for a
small horizon (radius 0.16 M areal in the comoving coordinates of SR-1: about 2.7 M
coordinate) [TO VERIFY with core]; changing `cfl_number` at a restart [TO VERIFY].

## 4. The lead's rerun of the criteria package

Run A-20261115-130252-01e8b64 (`check_criteria.py`, full, 14.6 minutes on one core;
`predict.py` example), child run A-emd-pbh-20261115-130256-a7374a4: 37 checks, the same four
failures (T1.2b, T2.2d last printed digit; T2.4a, T2.4c agreement bands), and all 432 values
of `results.json` identical to the helper's final run A-emd-pbh-20261115-115120-2eb3117.
Prediction L1 holds for this package.

## 5. Interface proposals and requests sent (outbox)

| File | To | What |
|---|---|---|
| `20261115T1320Z__to-core__scouting-runs-ball.md` | core | run or enable SR-1/SR-2; finder settings for a 0.16 M horizon; cfl change at restart; t = 0 constraint norms of the expball tables |
| `20261115T1320Z__to-core__newton-mode-and-ball-ic.md` | core | Newtonian mode with the options of `newton/SCAN.md`; deformed-ball initial data; halting tests A6 as acceptance tests |
| `20261115T1320Z__to-core__phase1-generator-and-gauge-options.md` | core | phase-1 generator for the data of arXiv:2609.14218; K_ref and softplus lapse options; finder spin with projected rotation vectors; dispersion initial data |
| `20261115T1320Z__to-orch__threshold-line-in-periodic-box.md` | orch | set-up order (SCOPE.md 10.2); G1 T3 acceptance; card-hours |
| `20261115T1320Z__to-orch__harness-manifests-and-ignore.md` | orch | anchor `runs/` in `.gitignore`; `nrpic-run` robustness to manifests without `outputs` |
| `20261115T1320Z__to-kb__ingest-s1-references.md` | kb | ingest the twelve key references and four unread ones |
| `20261115T1320Z__to-B-emd-gw__periodic-slicing.md` | B-emd-gw | slicing and shift for collapse in a periodic box; shared spherical test |

## 6. Wave 2: what the scouting runs showed (details `../REVIEW-wave2.md`, `../../runs_ball/`, `../../periodic_threshold/`)

| Run | Outcome |
|---|---|
| SR-1 (geodesic slicing), dx = M, M/2, M/4 | comoving to 1e-14; core turnaround -0.13 per cent (M/2), -0.074 per cent (M/4); non-finite at t = 30.8 (M) and 33.1 (M/2), before the collapse (44.35); no horizon |
| SR-2 (conformal-time lapse + Gamma-driver), dx = M, M/2, M/4 | turnaround +0.26 per cent (M/2), +0.18 per cent (M/4); lapse pulse from the core edge (central lapse 1.86 against 1.34) at every resolution; no horizon: the first horizon (areal radius 0.161 M) is below one cell |
| S2 periodic, mu = 0.03 | 250 t_H, no horizon, relative H above 0.1 from 36 t_H on refined levels |
| S1 periodic, mu = 0.3 | lapse collapses from ~10 t_H; non-finite at 21.9 t_H without a horizon (UNDECIDED) |

Measured cost (verifier's C8 now testable): 6.3e-8 and 7.2e-8 card-seconds per cell and
step for SR-1 and SR-2 at 256^3 against the model's 8.1e-8; the periodic runs 1.3 times
the unit-cost model. Wave-2 card-hours: 1.115.
