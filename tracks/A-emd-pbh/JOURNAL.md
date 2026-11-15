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
