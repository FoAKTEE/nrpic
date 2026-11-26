# JOURNAL of A-emd-pbh

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T12:57Z  session lead (wave 1)  commits 4c6c0f7..(see end of entry)  runs (see end of entry)

Lead session of wave 1. Five helpers have finished (scope, expball, criteria, newton,
gauge); their own journals hold their predictions and outcomes:
`scope/JOURNAL.md`, `expball/JOURNAL.md`, `criteria/JOURNAL.md`, `newton/JOURNAL.md`,
`gauge/JOURNAL.md`. This entry records the lead's independent check of their artefacts,
written as predictions before each check runs and outcomes after.

### Predictions L1-L6, written 12:57 UTC before any rerun or cross-check

- L1 (reruns reproduce). Rerunning, from the committed scripts at the current commit,
  each package's checks gives the numbers its report states, to the last printed digit:
  scope T1-T5 (h-hat(0.2,0) = 0.452, mu_fd = 0.048, ball limits mu <= 0.031 (q = 3) and
  0.069 (q = 2), 5.41 card-hours for jeans/n1e4_v19, ~155 card-hours for the scan);
  expball sym checks 27/27, 36/36, 11/11, unit tests 32 pass, G1 orders 2.00/4.00 for the
  flat ball momentum constraint and the top-hat; criteria 33 of 37 checks pass with the
  same four failures (T1.2b, T2.2d, T2.4a, T2.4c); newton P1-P7 numbers (top-hat collapse
  linear contrast 1.6865, event-time offsets +0.9 and +0.1 per cent for the 'added'
  placement), snapshot self-test first-collapse time to ~1e-5; gauge T1 lapse maxima
  19.01 and 3.03, T2 limits 0.618 and 0.660, T3 crossing at t = 1.203. Refuted by any
  difference beyond the last printed digit or a check that changes from pass to fail.
- L2 (two generators of the same data agree). expball's `Ball` and core's
  `python/nrpic/expanding_ball.py` (branch core/id-extrinsic, written independently) for
  the sharp marginally bound ball with M = 1, R_b = 8 (H R_b = 0.5): KL, KT, betar and u
  agree at common radii to 1e-12 absolute, except within one table row of the edge.
  Refuted by a difference above 1e-8 anywhere else.
- L3 (one table rule). core's Python evaluator of format 2 (`nrpic.io` on
  core/id-extrinsic, the same rule as its C++ reader), applied to expball's data-set-1
  table (no `breaks` line), gives expball's own `lagrange4` values to 1e-13 at every
  radius. Refuted by a larger difference: then the rules differ and expball's G1 table
  check has to be repeated with core's rule.
- L4 (exact solution, three independent codes). For core's bound test ball (M = 1,
  R_b = 5, e0 = 0.16; core's journal gives turnaround a_max = 1.25 at tau = 9.542 M),
  expball's `exact.Shells` (fed through a small adapter), core's `ltb_turnaround` and a
  closed-form cycloid written here give the same turnaround time to 1e-9; the surface
  shell is trapped (R = 2M) at tau_AH ~ 25.4 M and crunches at tau_c ~ 26.9 M (cycloid
  estimate before the run). Refuted by a disagreement above 1e-9 between the three.
- L5 (data set 2 times, independent arithmetic). For the homogeneous core of data set 2
  (Delta = 1, H = 1/16, simultaneous bang time) a closed-form computation written here,
  not importing expball, gives tau_ta = 16.894, tau_c = 44.454 and R_max/R_i = 1.340 to
  the printed digits. Refuted by any difference in those digits.
- L6 (exterior extrinsic curvature). On the Painleve-Gullstrand exterior of expball's
  ball, K = KL + 2 KT = -(3/2) sqrt(2M/R^3) to 1e-14 relative (the gauge helper's
  derivation), and K jumps from -3H inside to -(3/2)H outside at a sharp edge.

### Predictions L7-L8, written 13:06 UTC before the runs (clock read from the machine)

- L7 (data set 2t for the first scouting runs). expball's generator with the data-set-2
  core and a C^4 edge taper of half width w = 1.5 M (`--edge-width 0.1875`, matter edge
  at rbar = 9.5 M) and a lattice of n_lat = 38 across the matter (spacing exactly
  h = 0.5 M, sites at (k + 1/2) h, so they sit at the cell centres of a dx = 0.5 M mesh with
  a cell face at the origin; n_lat = 76 for dx = 0.25 M): the predicted core times are those
  of data set 2 to all digits (tau_ta = 16.894, first trapped sphere 44.349 at R_i = 2.74,
  crunch 44.454; the taper is outside the core and spherical shells outside do not act on
  the inside); M = m(R_out) ~ 1.01; check_dataset passes as for data set 2. Refuted by any
  change of the core times or a failed end-to-end check.
- L8 (gauge-dependent coordinate times, closed-form estimates before the script). For the
  homogeneous core: geodesic slicing (lapse 1, shift 0) has t = tau, and the radial
  coordinate speed of light in the core grows as R_i/R, so a fixed step cfl dx stays below
  the von Neumann limit C v <= 0.62 (gauge T2) only while R/R_i > cfl/0.62: cfl = 0.25 holds
  to R/R_i = 0.40, near tau ~ 42; reaching the first trapped sphere (R/R_i ~ 0.06) needs
  cfl <~ 0.03 in the last stage. Conformal-time lapse: alpha_core = R/R_i, coordinate time
  t = int dtau R_i/R = (T0 R_i/A) Delta-eta, giving core turnaround at t ~ 13.8 M,
  core at tau = 44.349 near t ~ 49.5 M and the crunch near t ~ 54.9 M, with the coordinate
  speed of light ~1 throughout (no step problem). Refuted if the script's values differ
  from these estimates by more than 1 per cent.

### Outcomes of L1-L8 (written 13:19 UTC)

- L1 holds for every package. First attempt failed: the five `nrpic-run local` reruns ran in
  the worktree venv, which did not exist (no matplotlib; runs A-20261115-125927-6d2c1e6 and
  A-20261115-125932-{f221206, b90223c, 5a90432, 574c747}, kept as failed). After
  `nrpic-env create --no-kokkos` (numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.8, sympy 1.14.0,
  the versions the helpers used): scope A-20261115-130252-7877b7a, 291 numbers identical;
  expball A-20261115-130252-c744ff7, sym 27/27, 36/36, 11/11, 32 tests pass, convergence
  (child -130402-f5566fb) 901 values identical, noise (-130639-947c898) identical, data-set
  checks ok; criteria A-20261115-130252-01e8b64 (child -130256-a7374a4), 37 checks with the
  same four failures, 432 values identical; newton A-20261115-130252-f408a99 (children
  -130252-4290486, -130300-efc25b0), `validate.json` identical, self-test t1 to 1.2e-5;
  gauge A-20261115-130252-4290486, T1-T4 JSON identical. One traceability remark: gauge
  T4's quoted 0.068 vs 0.36 at a = 20.47 was read by hand from the history file; the
  script prints 0.12 vs 0.37 at a = 20.0 (same conclusion).
- L2 holds: expball and core generators agree to 5.4e-16 (KL), 5.3e-16 (KT), 4.8e-15
  (betar), 0 (u) at every radius, including next to the edge (run A-20261115-130257-a7374a4).
- L3 holds: the two table evaluators agree to 7e-18. Found on the way: expball's sharp-ball
  table has no `breaks` line, so the cubic smears the KL jump over two rows with an overshoot
  of about 0.1 H (figure looked at); sharp tables are for offline tests only.
- L4 holds: turnaround 9.542048138750, R = 2M at 25.407847821, crunch 26.897059616 from the
  three codes, largest disagreement 1.1e-14. (Core's `ltb_radius` fails for 0-d input; the
  script passes arrays.)
- L5 holds: y = 0.746379, R_max/R_i = 1.33980, tau_ta = 16.8938, tau_c = 44.4542,
  core edge trapped at 44.3815; expball's first horizon 44.3493 at R_i = 2.74, unchanged
  with a 1.6 M taper.
- L6 holds: exterior K/(-(3/2) sqrt(2M/R^3)) - 1 below 4.3e-15; K/H = -3 inside, -1.5 at the
  outer side of a sharp edge.
- L7 holds: data set 2t (run A-emd-pbh-20261115-130609-947c898; M = 1.00959, rest mass
  1.01590, 28768 lattice sites at h = 0.5 M) has the core times of data set 2 to all digits;
  end-to-end check A-emd-pbh-20261115-130846-947c898 ok. Its CIC check on the checker's own
  64^3 mesh (h = 0.3125) shows the lattice/mesh beat (rms 0.58), irrelevant on a dx = 0.5 M
  mesh where the sites sit on the cell centres (core's test 1: rounding).
- L8 holds within 0.17 per cent (run A-20261115-130948-5a2b58a): conformal-time coordinate
  times 13.823 (turnaround), 49.506 (core at tau = 44.349), 54.964 (crunch); geodesic
  slicing reaches the step limit at cfl 0.25 at tau = 42.30; four cfl stages, 0.15
  card-hours; SR-2 0.16 card-hours. First trapped sphere refined: R_i = 2.742, m = 0.0805.

### Session summary

did: re-checked the five helper packages from their artefacts (L1-L8); normalized and
committed all run manifests; created the worktree venv; wrote data set 2t and the
predictions of the first two scouting runs; G0 evidence, open list and checklist; G1 status
and checklist; lead's decisions in `scope/SCOPE.md` section 10; risks; seven outbox messages.
found: every helper number reproduces; the two independent generators (expball, core) agree
to rounding; two amplitude conventions differ by the factor e (SCOPE.md 10.1); the source
paper's OS horizon-mass error is <~ 1e-3 (main.tex:945, 1484); geodesic slicing needs a
shrinking step near the crunch.
changed my mind about: the order of the brief; the threshold line goes to the periodic box
(proposal to orch), the ball keeps the G2 tests.
open: REPORT.md of stage/G0 could not be written (the session's harness refuses report
files; content in SCOPE.md section 10, EVIDENCE.md, CHECKLIST.md); working note v0 and the
two schematics; fresh verifier; the scouting runs wait for the merge of core/id-extrinsic.
Helper journals: `scope/JOURNAL.md`, `expball/JOURNAL.md`, `criteria/JOURNAL.md`,
`newton/JOURNAL.md`, `gauge/JOURNAL.md`.

## 2026-11-15T18:50Z  session lead-wave2  commits 9290489..(this commit)  runs A-20261115-182021-6cb33de, -182210-d1478a0, -182314-bebd0cf, -182200-532a5f6, -182657-53da696, -182329-ad14d95, -182347-8ee3fcc, -182402-a46812c, -182502-dae304d, -182514-3bb6846

- prediction: written in `stage/REVIEW-wave2.md` section 0 and committed (6cb33de) before
  any check ran: every helper analysis reproduces exactly from its registered outputs; my
  own reader (`analysis/review_wave2.py`) confirms the helpers' numbers within stated bands
  (B1-B8, P1-P4, N1-N4, C1-C2); I predicted that the periodic helper's "1.5 t_H" and "45 t_H"
  were conversion errors (1.2 and 35-36 t_H) and that SR-2 at dx = M/4 would miss the eps
  bound of prediction R.
- did: closed the two dx = M/4 card runs (runreg.py finish) and analysed them with nrpic-run
  (A-20261115-182657-53da696; runs_ball/JOURNAL.md entry 6); reran every helper's analysis
  (runs_ball, periodic, newton, criteria2, verifier) from the registered outputs; wrote an
  independent reader of trajectories, histories and Newtonian moments; read the source lines
  behind the criteria2 and verifier claims; corrected SCOPE.md (10.9), the periodic DESIGN.md,
  RISKS.md, G1/STATUS.md; judged the G0 and G1 checklists, wrote G1 EVIDENCE/OPEN and VERIFY;
  posted 18 outbox messages (11 core, 3 orch, 1 kb, B, D) and acknowledged 8 inbox messages.
- found: all six reruns reproduce exactly (numbers JSON, CSV tables, results JSON, verify.json;
  PNGs byte-identical for the periodic analysis). My predictions held except my bracketed
  guess on SR-2 (its eps part of R2 holds, 3.7e-4; its turnaround part fails, +0.031 M > 0.02).
  dx = M/4: core-shell errors at tau = 16.894 fall at apparent order 3.0 (SR-1) and 4.3 (SR-2)
  from M/2; the turnaround-time error falls only from -0.022 to -0.013 M (SR-1). The SR-2
  lapse pulse is the same at three resolutions (peak 1.80, 1.86, 1.87). The time orientation of
  data set 2t is confirmed by evolution (verifier C5 limit closed). Verifier C1c and C4b are
  right: a q = 2 ball holds mu <= 0.0688 (contains the particle bracket); no horizon for
  mu = 0.045 by 250 t_H (MDPBH.tex:1102-1103). The 1707.03595 typo found by criteria2 is real
  (the source's own limit at Spin_PBH.tex:1925-1926 needs pi). nrpic_cosmo never sets
  user_ref_func (mesh_refinement.cpp:243 calls it). The KB snapshot holds all twelve S1
  references with 152 of 170 Track-A claims verified.
- corrections to earlier entries of this journal (the lines stay as written): line 94, the
  table interpolation at a sharp edge deviates from the exact step by up to 0.0855 = 1.37 H
  including the smeared jump (A-20261115-130257-a7374a4); "overshoot of about 0.1 H" was not
  what the run recorded. Line 101: the exterior K check gives 4.33e-15, not "below 4.3e-15".
- my own faults, on record: run A-20261115-182021-6cb33de ignored the time offset t0 of the
  Newtonian histories (part N void, fixed); run A-20261115-182329-ad14d95 passed
  '$NRPIC_RUN_DIR' unexpanded and wrote into a directory of that name in the worktree root
  (moved into the run directory, rerun as A-20261115-182347-8ee3fcc).
- evidence: figures looked at: runs_ball fig_resolution_summary (two versions),
  sr2_n256_horizon, sr1_n256L32_fields; periodic fig_scouting_histories, fig_t1_solve_change;
  newton fig_newton_scan_summary, fig_newton_gr_range; my fig_review_wave2 (two versions).
- changed my mind about: the reason for the periodic box (the ball can hold the particle
  bracket at q = 2; the box is chosen because it uses the source's data unchanged); data set 2t
  as the G2 horizon case (its first horizon is too small; a data set with a horizon of several
  M is needed); the turnaround time as the G2 convergence measure (the shell radius at fixed
  proper time converges cleanly, the parabola estimator of the turnaround time does not).
- open: a slicing that reaches a horizon (core); C18 verifier and C11 data-flow schematic;
  note Sec. IV with the wave-2 runs; data set 2h.

## 2026-11-21T07:55Z  session lead-batch2b (wave 3)  commits db43e4c0..(see end of entry)  runs (see end of entry)

Lead of A-emd-pbh in batch 2b. No lead session ran between 2026-11-15 and now (the wave-2b
lead did not return). Packages finished since then: the G1 verifier (wave 2b, run
A-20261119-142905-c813c01), szekeres (wave 3a, 14 runs), g1close (batch 1), the G1 gate review
(batch 2a). Cut on 2026-11-20 14:33 PST and not resumed in this batch: verify_bh, szekeres
round 1, periodic_threshold. Running beside me in this batch (same worktree, own commits):
runs_ball and conv_ball. State found: tree with four uncommitted periodic_threshold files
(left alone); no card job of A in `squeue`; two stranded local runs whose processes had ended
with exit 0 (`.nrpic/result.json`): I closed them with `nrpic-run finish`
(A-20261120-223123-f436c39 periodic P0L data, A-20261120-223422-8cc4241 Szekeres files).

### Predictions of the lead's re-check (written before any of it ran)

Rerun code checked first: no script, module or reference these reruns call changed since each
run's commit except two docstrings of `szekeres/szekeres/model.py` (`git diff --stat`).

- L1. G1 verifier, `stage/G1/verifier/run_all.py` rerun into my run directory: all four parts
  and the schematic exit 0; every number of `ledger.json`, `criteria.json`, `newton.json`,
  `ball.json` (and the two `*_recomputed.json`) equals the registered run's to 1e-9 relative;
  tallies 39 confirmed / 1 not confirmed / 2 wrong (ledger), 19/19, 17/17, 12/12. Refuted by
  any larger difference or another tally.
- L2. g1close `check_findings.py` rerun: `findings.json` equal to that of
  A-20261120-222454-d16dbc6; the band holds 9 of 14 Newtonian points. Refuted otherwise.
- L3. g1close `wave1_sha256.py` rerun: the same 55 files with the same sha256 as
  A-20261120-222620-0304d9d (nothing changed since). Refuted by any change.
- L4. Gate reviewer's `review_checks.py` (script in scratch, sha256 4d72c147... as its manifest
  records) rerun: checks A-F give the values of A-20261121-064537-2bcf310; 10 of 10 raw files
  match their checksums.
- L5. Szekeres `run_ltb_limit.py`, `run_dipole_order.py`, `run_error_budget.py` rerun (figure
  directory redirected so that no tracked figure is rewritten): JSON equal to
  A-20261119-151501-9cff966, -151501-3e344a4, -153842-a1db5d6 to 1e-9 relative.
- L6. Szekeres unit tests: 15 pass.
- L7. Own reading of the raw history `N32/szk.cstat.hst` of A-20261119-152010-94a9461: the first
  record with a non-finite or sentinel (1.8e308) value lies at tau in (24, 28] (the package's
  claim "fails between tau = 24 and 28"). Refuted outside that interval.
- L8. Szekeres file run A-20261120-223422-8cc4241 (which I closed): `prep_ppc1.json` gives a
  predicted relative E error of the deposit below 1e-14 at every N, and total rest masses at
  N = 32..256 that agree to 1e-2 and approach each other with N. Refuted otherwise.
- L9. Periodic P0L data run A-20261120-223123-f436c39 (which I closed) against the helper's
  prediction D3 (`periodic_threshold/JOURNAL.md`): residual below 1e-10, c in [0.05, 0.2],
  delta_N max 0.10-0.14, alpha_min 0.78-0.82, no inner solve at the 60-iteration limit. (I read
  its log while closing it, so this is a check of the helper's prediction, not a prediction of
  mine.)

### Outcomes L1-L9 (runs A-20261121-075605-351d611 and its repeat A-20261121-075933-338a6ff)

All nine hold. Every rerun is bit-identical to its registered run (L1-L5: twelve JSON files,
1 375 numbers and 680 strings, no difference); the Szekeres tests pass 15 of 15; the N32
Szekeres history is last finite at tau = 25.0 and non-finite from 26.0; the Szekeres files
conserve the rest mass to 2e-10 between N = 128 and 256 with a deposit error of 1.2e-16; the
P0L data meet every bound of D3 (residuals 6e-12 and 1e-11, c = 0.088, delta_N 0.118,
alpha_min 0.805, at most 32 inner iterations). My own fault, on record: the first run's figure
had an empty panel (every difference was exactly zero, below the axis floor); the repeat
draws the zero differences as markers. Figures looked at: fig_review_wave3 (second run),
szekeres fig_code_geodesic, fig_dipole_order, fig_mesh_constraints, g1close
fig_g1close_findings. Per-package verdicts: `stage/REVIEW-wave3.md`.

A wrong judgement of mine, corrected before it left the review: I first wrote that the
fixed-box job A-20261120-223310-a9ce31a (1 min 28 s) "probably failed early"; its status file
and logs show all three members reached t = 24 with rc = 0 (30 s each on the card).

### Predictions L10-L13 (runs_ball finished during this session; written before its re-check ran)

runs_ball closed its runs and analyses at 00:29 PST (its journal entry 20). Re-check from the
registered outputs, with the figure directory redirected to my run directory:
- L10. compare.py and fields.py on BH-1R as in A-20261121-080558-02c3188: `bh_smr_numbers.json`
  equal to 1e-9 relative. Refuted by a larger difference.
- L11. excision.py, turnaround.py --breakdown and compare.py --line-hmax as in
  A-20261121-081153-b92c08c: `excision.json`, `bd/turnaround.json`, `bh_smr_numbers.json` equal
  to 1e-9 relative.
- L12. Own reading of `bh_smr/ball.horizon_summary_0.txt` (A-20261119-164634-f1fe887): the first
  converged search is at t = 10.875 with area mass 0.701 and mean coordinate radius 0.44 M, and
  every later search converges (no NaN row after it: a persistent horizon, entry 12's claim).
- L13. Own reading of `bh_n256/ball.horizon_summary_0.txt` (A-20261119-144419-13d5601): every
  search of BH-1 at uniform M/8 returns NaN (entry 11, B2).

### Outcomes L10-L13 (run A-20261121-082814-6fadb30; figure fig_review_runs_ball looked at)

- L10 holds for every value, refuted on structure: the 1 652 numbers of `bh_smr_numbers.json`
  equal those of A-20261121-080558-02c3188 exactly; the rerun has three keys more
  (`finder_g2`, `line_hmax`, `line_light_speed`), which compare.py gained in commit ebe70b41
  after that run. I did not foresee the code change.
- L11 holds: `excision.json` (2 396 numbers), `bd/turnaround.json` (53), `bh_smr_numbers.json`
  (2 678) identical to A-20261121-081153-b92c08c. The rerun's exit status 1 is my own fault:
  I pointed `--figdir` at the output directory, and compare.py's copy of its figures then
  failed with SameFileError after the JSON files were written.
- L12 holds: BH-1R's first converged search at t = 10.875 (area mass 0.70106, mean coordinate
  radius 0.4425 M); all 41 later searches to t = 15.875 converge; the mass falls to 0.686 near
  t = 11.4 and then grows to 0.708. runs_ball's figure `bh_smr_horizon.png` (looked at) puts
  the finder mass within 1e-3 of the exact mass on the same slice from t of about 11.7 on, and
  2e-2 above it at the first detection.
- L13 holds: all 64 searches of BH-1 at uniform M/8 return NaN.

### End of the session (lead, batch 2b), 2026-11-21 ~00:50 PST

- did: re-checked every package finished since 2026-11-15 from its registered outputs (G1
  verifier, szekeres, g1close, gate review; runs_ball when it finished during the session):
  runs A-20261121-075605-351d611, -075933-338a6ff, -082814-6fadb30; closed the two stranded runs
  of cut packages; wrote `stage/REVIEW-wave3.md`; closed C20 (STATUS, JOURNAL, HANDOFF, RISKS);
  decided C18; re-collected, verified (full, with checksums) and reported stage G1; extended
  WRITING_GUIDE exception 1; copied the reviewer's script into the package; posted six outbox
  messages (orch 3, core 1, kb 1, B 1) and acknowledged 16 inbox messages.
- found: every rerun is bit-identical to its registered run (16 JSON files); my predictions
  L1-L13 hold, L10 only on values (three keys added to compare.py after the run). BH-1R has a
  persistent apparent horizon from t = 10.875 whose mass follows the exact slice mass to better
  than 1e-3 after t ~ 11.7 (runs_ball, re-checked). Every deck of the track carries
  hmean_tol_0 = 100, which core reports can stop the finder; BH-1 at M/8 never converged.
- evidence: figures looked at: fig_review_wave3 (second run), fig_review_runs_ball,
  bh_smr_horizon (L11 rerun), szekeres fig_code_geodesic, fig_dipole_order,
  fig_mesh_constraints, g1close fig_g1close_findings.
- changed my mind about: the fixed-box card job (1 min 28 s is a complete run, not an early
  failure); the Newtonian energy drift (core names its cause: deposit and gather kernels
  differ); the waiver I asked for the runs_ball manifests (not needed, they were closed).
- my faults, on record: an empty figure panel in the first re-check run; a SameFileError in the
  runs_ball rerun from my own `--figdir` redirect; a first wrong judgement of job 4748.
- open: G1 sign-off (orchestrator); verify_bh, szekeres card series, periodic_threshold
  (cut, not resumed); conv_ball card job 1 queued (Slurm 4776, run A-20261121-075926-d10c2c1).
- card-hours this session: 0. Commits 0f5972c4 .. (this commit).

## 2026-11-21T20:55Z  session lead-batch5 (wave 3)  commits 349447ac..(this commit)  runs (see end of entry)

Aim (decision 0025 items 4-5): leave the cards loaded with this owner's long runs, registered and
chained, with a HANDOFF from which a later session reads them.

- Periodic job 4799 (run A-20261121-131600-02b5d41) closed: failed, exit 3 (guard) at t = 4.815
  (P0L) and 15.076 (S1L). Own reading A-20261121-203120-eaba95f (figure looked at): norm(H) jumps by
  ~1e4 at t = 2.506 in both members. Predictions P3, P4, S1, S2 refuted (periodic_threshold journal
  entry 20:44Z). Decision: no periodic long run; request to core; note to B.
- verify_bh's open point, as far as it decides runs: horizon masses are judged on the median over
  detections (first detection +2e-2 at BH-1R, +4.5e-2 at conv_ball B); the clock item is REFUTED
  as its section 4 recommends; the slice-or-finder question stays [TO VERIFY] and the scan writes
  the dumps that answer it.
- New package threshold_ball. Reasoning [JUDGEMENT]: the top-hat core of the ball always traps
  before its crunch, so the spherical scan has only the finite-duration threshold of SCOPE
  section 3; t_end = 45 M gives the exact bracket delta_c in (0.40, 0.42]. Design run
  A-20261121-202520-3164672, data A-20261121-202812-cae4436, smoke tests A-20261121-203156-d094c56
  (FAILED: `diagnostics` not declared in conv_ball's decks; my oversight, fixed by package decks)
  and A-20261121-203211-6d3ce73 (exit 0). Predictions T1-T6 committed (c48bd33b, 12:41:43 PST)
  before the first submission (12:41:49).
- Sequencer started (pid 2666191), queue of 12 card runs (model 15 card-hours, 32.7 requested).
  Submitted by it: A-20261121-204149-c48bd33 (Slurm 4838, B-d0.42), A-20261121-204250-0bf45c7
  (Slurm 4845, B-d0.40), both PENDING at 12:45.
- Posts: core periodic-relaxed-lapse-blowup, core bh1r-inte-deficit-two-levels, B-emd-gw
  periodic-spherical-test-status, orch cards-loaded-threshold-scan; acks: kb
  re-szekeres-conformal-flatness, orch release-core-v0.6.
- Gates: G0, G1 signed; G2 not ready for review (scan running; second agent owed on conv_ball's G2
  reading; schematic names core-v0.3).
- Card-hours used this session: 0 (two chains pending). Processors: 1-4 cores for about 8 min.
- Runs: A-20261121-202520-3164672, A-20261121-202812-cae4436, A-20261121-203120-eaba95f,
  A-20261121-203156-d094c56 (failed), A-20261121-203211-6d3ce73; card A-20261121-204149-c48bd33,
  A-20261121-204250-0bf45c7 (pending).

## 2026-11-21 15:11-15:30 PST, batch 7 (short lead session, decision 0027 items 2 and 6)

Aim: three things only. (1) Post periodic_diag's request to core; (2) the periodic deck at
cfl_number 0.5 and the corrected periodic job into the sequencer's queue; (3) HANDOFF.

- Posted `outbox/20261121T231546Z__to-core__periodic-gamma-driver-step.md` (type request; the
  draft of periodic_diag unchanged, one closing paragraph added). It closes our request
  periodic-relaxed-lapse-blowup (20261121T204327Z): core need not answer that one.
- `periodic_threshold/inputs/peak_leak.athinput`: cfl_number 1.0 -> 0.5, header CORRECTION
  (cause, run ids, margin gt^xx <= 1.9). The only periodic deck of this owner with a Gamma-driver
  and a step above 0.6: peak_smr, peak_smr4, peak_amr and the Szekeres decks run zero shift at
  0.25, punc_box16 (nrpic_cf) runs 0.25; the ball decks (threshold_ball, conv_ball) run 0.25 with
  the Gamma-driver. periodic_diag's diag_uniform decks keep 1.0 on purpose: they are the
  reproducer of the instability (G0) handed to core; their cases set cfl on the command line.
- Prediction before queueing: periodic_threshold/JOURNAL.md entry 2026-11-21 23:15Z (Q1 no jump
  of norm(H) by more than 10x between history records in t in [1.5, 6], H_max < 0.1 to t = 5,
  level-4 step <= 0.5 dx, no grid-scale pattern in beta^x / alpha lines; Q2 no guard stop
  before t = 20; Q3 about 0.17 s per step, P0L ~41 min, S1L ~65 min within 2x; then P1-P4, S1-S3
  of 13:20Z unchanged). Refuted by a job-1-like jump or guard stop at a later time, grid-scale
  growth on level 4 or at a level boundary; a late failure where gt^xx > 1.9 at the centre
  refutes the margin, not the remedy. The remedy is tested on the uniform mesh only; this job is
  its test on the refined mesh. Committed (aa254891) before the lines can be submitted.
- Queue: lines 14 (P0L, chain, 2.0 card-hours requested = 2 segments) and 15 (S1L, chain, 3.0 =
  3 segments) of `threshold_ball/queue.txt`, release core-v0.6, --package periodic_threshold,
  data files checksummed as inputs (same sha256 as job 1). Both members run on the refined mesh to
  a horizon (P3: expected at coordinate 80-130 < tlim 140; S2: 97-213 < tlim 220), within the
  allotment (G2: 5.51 used, 3.93 reserved, 50.56 left; the whole queue asks 37.6, model 16.8).
  Dry runs of both lines through nrpic-run passed (clean package, inputs, 2 and 3 segments).
- Mistake on record: I first inserted a comment line at line 3 of queue.txt, which shifts the
  line numbers that done.txt keys on (old line 4 would have been resubmitted as line 5). Removed
  within a minute, before any submission (both A-jobs were pending, so the sequencer did not act;
  sequencer.log shows no entry after 12:42:50); the note now sits at the end of the file and says
  that new lines go at the end only.
- Not done (task: three things only): no review, no stage package, no RISKS update, no analysis.
  Inbox: 0 unacknowledged. Card-hours used: 0. Processors: none.

## 2026-11-24 04:51-07:30 PST, batch 11 (lead; analysis round of the card runs, decisions 0026, 0027, 0030)

First analysis session of this owner since the cards were loaded (decision 0030 item 5 put A's
round after the reset; A had no session in batch 10a). Commits a123ee24 (merge of main) to the
end of this session; runs listed below. Pause flag absent at every check.

Did:
- State: the batch-5 sequencer had submitted all 13 lines and ended normally (2026-11-23 10:40).
  Eleven runs had ended (ten DONE at tlim; the A-mesh batch exit 3 at the guard); two were cut by
  the preemptions of 2026-11-23 and closed FAILED with MAX_SEGMENTS reached: C-d0.42 at t = 42 of
  51, S1L at 66 of 220. Both continued in place from their newest restart (same run ids, notes in
  the package journals first), Slurm 5150 and 5149, PENDING. All other runs closed with
  nrpic-run finish (7.32 card-hours recorded for the eleven plus P0L).
- Periodic job 2 judged (periodic_threshold journal 2026-11-24): the cfl 0.5 remedy holds on the
  refined mesh (Q1a, c, d, Q2, Q3; A-20261124-130507-10510ac); P0L ran to 140 but no horizon was
  found (P3 refuted); F1 (A-20261124-131430-d1a2ee6): the slice traps only from t = 132, at
  coordinate r 0.075 under four finest cells; F2 (A-20261124-131232-e7b58f8): the finder converges
  from no start radius. Posted to core (refined-mesh-cfl05-result). Follow-up P0L6 on six levels
  queued with D0-D5 (D0 smoke A-20261124-133457-9264c61 passed).
- Threshold scan judged (threshold_ball entries 3-10): analysis A-20261124-131120-5c974ce. T1-T3
  hold; the code's finite-duration threshold on mesh B is 0.41033 against the exact 0.41026
  (A-20261124-140131-48c636c). T4 holds only through guard stops on mesh A; T5 and T6 partly
  refuted. The first-detection mass excess is in the slice, not the finder (verify_bh's open
  point closed). Follow-up C-d0.40 queued (T7; nestC data A-20261124-133456-2d00507).
- Constraint floor (G2 item C3): K (A-20261124-132249-2e6b5f2), K2 (-132342-d5dc06e) and K3
  (-134637-bd0d6eb) refuted: the early constraint norms fall with neither mesh nor particle
  number and are not localized at refinement boundaries or density jumps. K4 (step and source
  extrapolation) runs on processors at the end of the session.
- A-mesh guard stop: G1 (processor restart from t = 44) repeats the card stop exactly; G2 (no
  lapse_leak) stops 0.5 M later at another cell; G3 see threshold_ball entry 5 outcome.
- Stage: interim G2 package (collect, checklist judged: 9 PASS, 10 OPEN, 1 FAIL; EVIDENCE, OPEN,
  report; verify: all checks pass except open runs). REVIEW-wave3 section 7. RISKS rows 27-28
  updated, 31-35 new. Sequencer now logs why it waits (decision 0030 item 4); sequencer_b11 started.
- Outbox: core refined-mesh-cfl05-result (info); orch constraint-bound-ruling (request). Inbox:
  three messages acknowledged (kb refutation and Szekeres locators; core's two answers).

Changed my mind about: (1) mesh A at threshold: I predicted it could not hold a horizon; it finds
it and then the run dies at the guard; (2) the constraint floor: I expected mesh truncation or
particle noise; it is neither, and not localized; (3) the periodic finder: the failure is not the
initial radius alone, the horizon sits under four cells.

Mistakes of my own, no damage: a constraint-ratio range first written as 1.6-3.8 (it is 1.6-5.9),
corrected before use; a `git commit -am` that could have swept a manifest of the finish loop (it
did not; later commits path-limited).

Stopped at 06:19 PST on the pause flag (five-hour window at 80 per cent): nothing new started.
Still running by itself: processor run A-20261124-132016-ecf12c3 (G3, ~20 min left), its manifest
open. Not started: K4 (threshold_ball entry 10, command written there). Card jobs 5149, 5150 PENDING;
sequencer_b11 (pid 207327) waits for them, then submits P0L6 and C-d0.40.

## 2026-11-24 13:30 PST, batch 12 (short session): card runs handed to the shared queue

Aim, one only: decision 0033 (cap of five queued jobs of the account) and the shared queue
`harness/bin/nrpic-queue`. No analysis, no review, no stage package. Merged main first.

Found (sacct from 11:30, chain events, sequencer state): the orchestrator's cancellation at 11:57 PST
hit two pending segments of this owner, 5177 (S1L, A-20261123-025907-97bab8d) and 5178 (C-d0.42,
A-20261122-173202-f98c79f). Both chains had computed in segments 5149/5150 (09:43-10:33 PST, wall-clock
stops at t = 198.7 of 220 and t = 45.96 of 51; newest restarts peak.00016.rst and ball.00020.rst).
So neither run was closed as stopped: both are continued in place. The sequencer (pid 207327) is gone;
its done.txt is empty, so queue_b11 lines 1 (P0L6) and 2 (C-d0.40) were never submitted or registered.

Done: `threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS> [--dry-run]` (one job, same run,
exe cmp-checked, deck checked against chain/input.athinput, refuses outside the dispatcher; records the
continuation in the manifest notes and commits that path). Dry runs on both chains printed the
expected submit_chain.sh lines; the refusals outside the dispatcher and with no segment left fired;
the notes writer was tried on a scratch copy of a manifest (other fields unchanged, bytes reproduced).
Queue entries: q0012 a-cd042-cont (p2), q0013 a-p0l6 (p2), q0014 a-cd040 (p2), q0015 a-s1l-cont (p5);
p2 for the runs that stage/G2/OPEN.md items 2 and 3 wait for. No --after (no dependency). The
predictions written before these runs stand unchanged (threshold_ball entries 1 and 8: T4, T7;
periodic_threshold 2026-11-21 13:20Z: S1-S3; 2026-11-24 13:40Z: D1-D5).
Not done (outside this session's aim): judging and closing processor run A-20261124-132016-ecf12c3
(ended exit 0 at 06:31 PST); K4.

## 2026-11-25 03:46-05:00 PST, lead of batch 17 (about an hour)

- q0012 a-cd042-cont ended DONE (job 5216, t = 51). C-d0.42 (A-20261122-173202-f98c79f) closed with
  nrpic-run finish; analysed with the registered analyse.py (A-20261125-115027-17b419e) after restating
  the rule of entry 1 (threshold_ball entry 11, committed before the analysis). Outcome: black hole by
  the rule (163 of 163 searches from t = 45.906), tau_det 43.705 < 45: the mesh-C upper end of the
  bracket holds. T4 mesh-C half REFUTED as written (ddet -0.0135 vs bound 0.0075; dmmed +2.36e-2 vs
  1.4e-3); the measures were not comparable (search quantum; unequal reference windows), shown by a
  common-window measurement made after seeing the figures (A-20261125-115550-fe60ff1: 2.1e-3 vs 5.2e-3).
  A first run of that script (A-20261125-115530-a4f7dcd) had a NaN defect; fixed, kept on record.
- Queue: q0014 (C-d0.40, 14 card-h) removed: no G2 item waits for it (T7 untested, on record). Added
  q0040, q0041: the Szekeres card series (C1 iii), v0.7 executable, predictions P17-P21 standing
  (szekeres entry 10). q0013 (P0L6, C1 ii) and q0015 (S1L, SCOPE's triaxial phase-1 G2 criterion) kept.
- Stage G2: collect (20 items kept), CHECKLIST evidence for C1, C3, C7, C19, C20; OPEN.md rewritten
  item by item with the queue entry per item; verify (--no-checksums) and report rerun. Not complete.
- Inbox: eight info messages acknowledged (kb sources, core step limit dt_gauge and its refined-deck
  result, SIGTERM restarts, release v0.7). Outbox: request to orch (oblate/prolate row, C18 verifier).
- Not done: K4; closing A-20261124-132016-ecf12c3 (G3); threshold_ball/README.md.

## 2026-11-25 07:04-07:25 PST, lead of batch 19 (about an hour asked)

- Merged main; read decisions 0039, 0040, the orch note on the finder's summary file and the fresh verifier's
  report stage/G2/VERIFIER-C18.md.
- C18: predictions P12a-d written and committed before the analysis (threshold_ball entry 12); registered
  analysis c18_answer.py (A-20261125-151126-7f79a83; two failed first attempts kept: a member without a status
  file, then the figure). P12a, P12b hold; P12c, P12d refuted. The verifier is right on the masses: README
  medians near threshold lie outside the bracket the tracked particles allow; A medians were built on repeated
  summary rows. READMEs of conv_ball and threshold_ball corrected; CHECKLIST C1 (time measure), C2, C7, C8, C18.
- K4 closed (nrpic-run finish) and judged (A-20261125-150851-5545f8e, fig_k4.png): K4a-c hold. Noted that
  0039 item 2(c) calls K4 the smoothed-edge test; it is not; C3 stays FAILED; request to orch.
- A2: decided that S1L serves (prediction written first, periodic_threshold JOURNAL 07:15 PST); analysis
  a2_crossing.py (A-20261125-151629-bb77171, clocks added A-20261125-151715-66f198f): z first (holds), time
  refuted (6.1-6.4 t_H against [3.4, 5.0]).
- Stage G2: collect, verify, report; REVIEW-wave3 section 9; OPEN.md rewritten. Inbox: 4 acknowledged. Outbox:
  info c18-answered-k4-a2, request c3-smoothed-edge-test.
- Not done: Newtonian control of A2; smoothed-edge test; reading P0L6 and Szekeres (still in the queue).

## 2026-11-25 07:54-09:10 PST, lead of batch 20 (processors only; decision 0040 items 6, 7)

- Merged main (0040 items 6-9). Predictions first, committed before every run: threshold_ball entry 13 (C3S a-e,
  amended before any AthenaK run when `--edge-w` proved inadmissible on data set 3; then D and F) and
  periodic_threshold 2026-11-25 08:10 PST (second derivation of the Zel'dovich reference; AZ1, AZ2).
- C3: data S1, S2 (smooth_tophat; prep_bh.py gained --profile); t = 0 slices on M/16, M/32; test D (cloud), F1
  (CIC). Outcomes: (a) refuted, (c) holds, (e) as predicted, D holds, F1 holds. The floor is the jumps (momentum)
  and the PCS deposit at refinement boundaries (Hamiltonian). C3 stays FAILED as written. Runs:
  A-20261125-160221-b68396f and -160306-280d150 (failed, on record), -160436-462452d, -160633-594a474,
  -160849-8c01b54, -161039-cb046d7, -161154-62ce3dc (running), -161248-eecc672. S1-A and S2-B (PCS) stopped by hand
  (PIDs 2597153, 2597154) to keep six cores. Figures fig_edge.png (two versions) and fig_edge_d.png looked at.
- A2: N-z (Newton, Zel'dovich velocities) crosses at 4.55 t_H, Zel'dovich 4.35, S1L 6.35: AZ1 narrowly refuted
  (band edge 4.5); the reference, clock and reader are confirmed to 5 per cent by a run that could have failed;
  S1L departs from 1-2 t_H on. Runs A-20261125-160633-e38d321 (N-f, N-z128 continuing), -162905-d0ef1d7,
  -162951-bb0fb26; fig_a2_crossing.png, fig_a2_compare.png looked at.
- P0L6 (q0013): chain not ended (Slurm 5296 pending), the find at t = 118.1 not read (task condition).
- Stage G2: collect, verify (--no-checksums: six cores busy; FAIL only on the five unfinished runs), report.
  CHECKLIST C1 (A2) and C3, OPEN.md, EVIDENCE.md, REVIEW-wave3 section 10. Outbox: core
  pcs-deposit-refinement-boundary, orch c3-smoothed-edge-result. Inbox: nothing unacknowledged.
- Brief analyses (seconds) ran on a seventh core while the six run threads were busy.
- Later in the session: F2 REFUTED on M/16 (A-20261125-165215-e3fe168: S2 with CIC 0.129 at t = 1; PCS twin 0.53 at
  t = 4): the evolution rebuilds the floor; the mesh leg S2c-B decides (running). AZ2: N-f crosses at 0.43 t_H
  (A-20261125-165125-1640161): direction holds, band refuted. Consequence as fixed: the lag of S1L is not in the
  reference, clock, reader or initial positions; relativistic evolution or coordinates, not named further.
  Outbox: info c3-f2-refuted to orch.

## 2026-11-25 18:17-18:55 PST, lead of batch 23 (analysis round; no card time)

- Merged main (0041, 0042). Closed every ended run before reading it (`nrpic-run finish`): S2c (completed), the PCS
  twin (failed, exit 143: two members stopped by hand in batch 20), N-z/N-f/N-z128 (completed), Szekeres N64/N128
  batch (failed: guard stops, exit 3), P0L6 chain (completed, 4.87 card-hours), Szekeres N256 chain (stopped: the
  queue entry ran one segment, tau 21.2 of 40).
- Predictions written and committed before any reading: threshold_ball entry 14 (G, the C3 mesh leg) and
  periodic_threshold 18:21 PST (A2X, a crossing measure free of the coordinates).
- C3: G REFUTED (A-20261126-022624-c663e0f): orders 1.5, 1.07, 0.34, 0.36 at t = 0.25-1; C3 stays FAILED; a defect
  to explain under 0039 2(c).
- A2: A2X (i) holds; (ii) as written not decidable (the dust-clock bound from snapshots is empty; three runs kept);
  the probe column turned out to be a coordinate point's clock (source read; prediction PC, A-20261126-023551-f800cf5:
  reading withdrawn), but the central particle is at rest and a vertex of the crossing cells, so its proper time
  on the last uncrossed slice is >= int alpha_min dt = 5.99 t_H. The lag is not a coordinate effect. N-z128 crosses at 3.62 t_H (AZ1 second clause refuted): the 64^3 Newtonian control was late
  by 26 per cent. No card member queued. Runs A-20261126-022220-99b7be8, -022338-0edc27c, -022438-a08cc5f,
  -022545-5af99fb, -022631-dafbb4f; fig_a2x.png, fig_a2_compare.png looked at.
- P0L6: D1, D5 hold; D2, D3, D4 refuted; the one "found" at t = 118.1 is a false acceptance (status file read
  critically); finder stalls on a resolved horizon from t = 136 (A-20261126-022753-f9e9c40; three figures looked at).
  Outbox to core: finder-false-accept-and-stall-p0l6.
- Szekeres: the three-member analysis was too slow (~1 h per N256 dump) and was stopped by hand and closed
  (A-20261126-022804-0bc68c2, stopped), and so was the in-session N64/N128 run (A-20261126-023242-f3f0578, ~15 min
  per N128 dump); both readers now run detached (A-20261126-024724-425ed7f, A-20261126-023245-1dd80ad). P17 refuted
  for N128, holds for N64; P18 holds for N64 at tau 10 (szekeres entry 11).
- Inbox: B's gr-particle-mass-weight acknowledged (it is the reading of AZ2's N-f: psi^6 masses read as density).
  Outbox to orch: g2-state-after-batch-23 (four rulings asked).
- PC (A-20261126-023551-f800cf5): the 'probe particle' was a misreading (source: the probe is a coordinate
  point); the central particle is at rest, so int alpha_min dt bounds its proper time: crossing after 5.99 t_H on
  a crossing worldline. Correction posted to orch (a2x-probe-correction).
- Stage G2: collect, verify --no-checksums (FAIL only on three unfinished runs: S1L chain awaiting q0015 and the
  two detached Szekeres readers), report with the decision text; CHECKLIST C1, C3, C19, C20; OPEN.md rewritten;
  EVIDENCE rows; REVIEW-wave3 section 11. G2 not listed as complete: four rulings asked, note work follows them.
- Processors: up to four cores at a time (load 87-97). Detached at the end: A-20261126-024724-425ed7f,
  A-20261126-023245-1dd80ad (one core each).
