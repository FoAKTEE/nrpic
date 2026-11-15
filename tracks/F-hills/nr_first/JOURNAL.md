# JOURNAL of the work package nr_first (F-hills, wave 2)

Helper of owner F-hills. Units G = c = 1. Labels: [VERIFIED] measured in a registered run
named here or read at a locator; [BACKGROUND] standard result, not checked in a source
here; [JUDGEMENT] my reading or choice; [TO VERIFY]. Run ids as `harness/bin/nrpic-run`
writes them; manifests under `tracks/F-hills/runs/<run_id>/`, outputs under
`scratch/F-hills/<run_id>/`. Every entry: prediction (written before the run), then the
outcome, also when the prediction failed.

Configuration of the package: mass ratio four first (decision 0013). The three-black-hole
data are `tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput` (wave 1, read only):
M = 1 (comp2), m1 = m2 = 0.125 (comp0, comp1), |P|/m = 0.234 (m1) and 0.268 (m2),
|P|/M = 0.056; members at cells m/8 (level 9 of 10), heavy hole at M/8 (level 6).
Executables: release core-v0.3, processors `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`,
cards `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`.

## 2026-11-15 E1. Mesh probe: block counts and processor cost of the inputs (prediction)

What: `scripts/probe_mesh.sh` on processors. (a) `athena -m` trees at t = 0 of the q = 4
three-black-hole data with 9, 10, 11 levels (members at m/4, m/8, m/16); (b) the
single-puncture input `inputs/single_P025.athinput` at m/8 and m/16 for 16 cycles, so that
the radius criterion of the wave zone has refined (one level per check, every 4 cycles).

Prediction [JUDGEMENT from the measured trees of wave 1, three_punctures PLAN section 4,
and core's counts, interface multi_puncture.md section 5]:
- q = 4 at m/8: 1716 MeshBlocks at t = 0 (the wave-1 count of the same tree, run
  F-hills-20261115-131933-907e5fe); m/4 about 1716 - 400 = 1300 +- 200; m/16 between 2400
  and 3700 (wave 1: 2416 with radii 1.2 m, 3690 for q = 10 with radii 1.8 m).
- single puncture after the wave-zone refinement: 500-900 MeshBlocks at m/8, 700-1200 at
  m/16; the t = 0 tree (before the wave zone is refined) below 300.
Refuted if the q = 4 m/8 count differs from 1716 (the tree builder would then not be
what wave 1 measured), or if a single-puncture count exceeds 1600 (the slot limit of the
input).

## 2026-11-15 E2. Constraint residual of the q = 4 three-black-hole data at t = 0 against resolution (prediction)

What (run C0): `hills_q4_m8.athinput` with `time/nlim=0` on processors; variants
(i) `approx` with the background factor (the input) at m/4, m/8, m/16; (ii) no correction
(`problem/comp<c>_corr=none`) at m/4, m/8, m/16; (iii) plain sum
(`problem/corr_background=false`) at m/8. Analysis `scripts/c0_constraints.py`: the history
norm <H^2>^(1/2) (sum of H^2 sqrt(gamma) dV over psi^4 <= 16, over the same volume:
outputs/history.cpp, core's definition in tracks/core/analysis/mp/triple_static.py), and the
closed-form residual of the same data on the same cells (`python/nrpic/bowen_york.py` through
core's `closed_forms`), so that code minus closed form is the truncation error alone.

Prediction [JUDGEMENT; reference numbers VERIFIED by core for its own triple at m/8,
interface section 8 test 3: none 2.25e-5, background factor 8.5e-6, plain sum 1.50e-5 in
the code's norm; closed form 2.15e-5, 2.2e-6, 1.23e-5]:
1. Order of the three variants at m/8 as in core's triple: approx < plain sum < none.
   Ratio none/approx in the code's norm between 2 and 30.
2. `none`: the residual is algebraic, -psi^-12 Abar^2 (core test 1a); its code norm
   changes by less than 30 percent between m/8 and m/16 and is within 30 percent of the
   closed form at m/16.
3. `approx`: the code norm falls with resolution (truncation error at the light holes
   dominates at m/8, as in core's triple: 8.5e-6 code against 2.2e-6 closed form), by a
   factor 2 or more from m/8 to m/16, and approaches the closed form; the closed form of the
   data (the resolution-independent part) lies between 1/30 and 1/3 of the `none` closed form.
4. The norm of (code - closed form) falls with resolution at an order between 3 and 7 for
   both variants (sixth-order differences, nghost = 4; lower near the punctures).
Refuted if (1) the order of the variants differs, (2) the `none` norm changes by more
than 30 percent with resolution, (3) the `approx` norm does not fall from m/8 to m/16, or
(4) the difference does not converge.

## 2026-11-15 E3. Two single-puncture card runs: junk energy and gauge settling of the light member (prediction)

Runs (package `inputs/single_P025.athinput`; m = 1, P = 0.25 along +x, closed-form
correction, spheres 30, 40, 50 m; t = 0 to 90 m; card executable of the release):
- S3: as the file: cells m/8 (resolution of the members of the passage), eta m = 2.
- S2: `z4c/shift_eta=0.25`: eta m = 0.25, the damping a member of mass 0.125 sees in the
  q = 4 passage with one shift_eta = 2/M.
- S1: `mesh_refinement/num_levels=8`: cells m/16, eta m = 2 (junk at higher resolution).
The two runs the lead named are S3 + S2 (junk energy; gauge settling of the light member at
the passage's resolution and damping); S1 is the resolution partner of the junk if the
card-hours allow (all three together are predicted below 1.5 card-hours).

Reference numbers [VERIFIED with `python/nrpic/bowen_york.py` in this session, the
reference module, no simulation; recomputed by `scripts/single_analysis.py`]: ADM mass of
the data (second-order correction) 1.039063 m (full solution 1.038322 m); P/M_ADM = 0.2406;
the rest mass of a boosted hole with that energy sqrt(M_ADM^2 - P^2) = 1.0085 m (second
order) or 1.0078 m (full solution). Core's test 1b (interface section 8) for P = 0.3 at
m/16: first-search horizon 1.0107 against 1.011 expected, constant to 2e-4 over 40 m;
tracker speed 0.48, 0.55, 0.61 of P/M_ADM over t = 10-20, 20-30, 30-40 m with eta m = 2.

Predictions:
1. Horizon mass at the first search 1.006-1.010 m in all three runs (spin |S| < 1e-3 m^2).
   Drift over 90 m: S1 below 0.3 percent; S3 (m/8) larger than S1, between 0.2 and 3
   percent (core's light holes at m/8 rose 1.3-1.5 percent in 32 m of their own mass,
   test 3) [JUDGEMENT]; S2 within a factor two of S3 (the stationary state of the
   Gamma-driver does not contain eta; eta sets how it is approached) [JUDGEMENT].
2. Tracker: moves along +x with y and z equal to zero to round-off (the data are symmetric
   under y -> -y and z -> -z). With eta m = 2 (S3, S1) the speed ratio f = v_tracker /
   (P/M_ADM) is 0.4-0.6 over t = 10-20 m and 0.5-0.7 over 30-40 m (core's 1b). With
   eta m = 0.25 (S2) the tracker is faster at every t < 40 m than in S3 (core: early speed
   about proportional to 1/eta) and f reaches 0.8 or more before t = 40 m; it may overshoot
   and oscillate (weakly damped driver) [JUDGEMENT]. Refuted if S2 is slower than S3.
3. Junk energy E_junk/m through the spheres (after removal of the slowly varying near-zone
   part, `three_punctures/scripts/junk_energy.py` method): between 1e-5 and 5e-4 (core's
   scaling 1.3e-2 (P/m)^4 gives 5e-5; the floor of core's 14 m sphere was 6e-5, the
   lead's reading up to ten times more); equal at 30, 40, 50 m within 25 percent; S2 equal
   to S3 within 25 percent (the radiated energy does not depend on the gauge); S1 equal to
   S3 within a factor two (junk of approximate data need not converge, 1004.1353
   `Punc_N.tex` lines 1253-1261 per three_punctures PLAN).
4. Constraint norm <H^2>^(1/2): at t = 0 S1 below S3 (finer cells); from t = 10 m on set
   by the evolved puncture, flat or slowly falling, no growth by more than ten after
   t = 20 m.
5. Cost: S3 and S2 0.2-0.4 card-hours each, S1 0.5-0.9; no non-finite value.
Consequence for the passage P1 [JUDGEMENT, to be read after the runs]: each member's junk
in units of M is 0.125 E_junk/m; it cannot propagate on the wave-zone cells of the passage
(member quasinormal wavelength 2.1 M on cells of 2 M); the passage burst for comparison is
3.7e-4 M (three_punctures PLAN section 5, quadrupole formula, BACKGROUND, locator missing).

## 2026-11-15 E4. Readers of trackers, horizons and member energies (prediction)

What: `scripts/nrread.py` (readers of `<base>.co_<n>.txt`, `<base>.horizon_summary_<n>.txt`,
`<base>.z4c.user.hst`, `waveforms/rpsi4_*.txt`; energy of each member relative to the
large hole, two definitions: two-body with M alone, and against the barycentre of M and the
other member when that one is bound, the definition of the lead's V5b) and
`scripts/test_nrread.py`.
Tests and predictions:
1. Synthetic: a full Newtonian three-body trajectory from the q = 4 start state
   (positions and momenta of `hills_q4_m8.athinput`) written in the tracker and horizon
   formats of AthenaK, read back: positions to the printed digits; the barycentric energy of
   the ejected member constant to 1e-4 units after the encounter and equal to the lead's
   +1.312 units (run F-hills-20261115-145559-a314517, `stage/G0/checks/v5b_summary.json`)
   within 1e-3; the two-body energy with M alone oscillating by more than 0.1 units (as V5b
   found). Refuted otherwise.
2. On the card runs S1-S3: number of tracker rows equal to the number of cycles; time
   column monotonic; horizon rows every 16 cycles, all found.
3. On the processor three-black-hole runs (E2, one cycle): three trackers at the input
   positions to 1e-6; three horizons from the first search, members 0.125 Lambda-close
   (0.128-0.132 M), heavy 1.00-1.01 M [JUDGEMENT from core's 0.541/0.550 for holes of 0.5
   and 10.40 for 10 with spin].

## 2026-11-15 Incidents of the first submissions (no result lost)

- Runs F-20261115-173106-57c4b4c (E1) and F-20261115-173112-a9e18a3 (E2) were stopped by me
  (kill by process id) after three minutes: AthenaK writes the tracker files
  (`<base>.co_<n>.txt`) and horizon summaries into the working directory, not into `-d`, so
  they landed in the worktree root and made the tree dirty. The stray files are kept in
  `stray_from_worktree_root/` of the two run directories. Fixed in the scripts (athena runs
  inside each case directory); reruns F-20261115-173543-29e87e8 (E1) and
  F-20261115-173547-a02af7d (E2).
- The processor build of the release is serial (`-DAthena_ENABLE_OPENMP=OFF`, cmake flags in
  the card manifest; one core at 100 percent in `ps`): the first two runs asked for 8 cores
  and used one. The reruns ask for one.
- Run F-20261115-173719-923135a (E4 test 1): the output argument `'$NRPIC_RUN_DIR'` was passed
  literally (no shell), so the output went to a directory of that name in the worktree root;
  moved to `out/` of the run directory. The scripts now take the run directory from the
  environment when no argument is given.

## 2026-11-15 E4 test 1, outcome (run F-20261115-173719-923135a, synthetic Newtonian trajectory)

7 of 10 checks passed. [VERIFIED, figure `out/fig_test_nrread_synthetic.png` of the run, read]
- Passed: three trackers; merged rows across a restart overlap (t = 600-700 written twice):
  24001 rows, every time once, in order; positions read back exactly; horizon rows with the
  duplicates removed (1501 each); the ejected member is m1 (comp0); its barycentric energy at
  the end +1.31187 units, the lead's V5b value +1.31187 (run F-hills-20261115-145559-a314517);
  the two-body energy with M alone oscillates over 0.734 units.
- FAILED prediction: the barycentric energy is constant to 1.54e-4 units after t = 300, not
  1e-4. The lead's V5b has the same range (late max - min = 1.54e-4, `v5b_summary.json`), so
  it is the coupling to the captured member's orbit, not the reader; my threshold was too
  tight. The test now uses 2e-4 and says why.
- Failed check of my own helper: the velocity from positions (line fit over 1 M) was off by
  8.3e-4 (one-sided windows at the ends see the acceleration as a bias). Changed to the
  derivative of a quadratic fit; rerun below.
- Failed check of the test's integrator: total energy conserved to 1.2e-9, not 1e-10
  (DOP853, rtol 1e-12, 1500 M with close passes); threshold 1e-8 is enough for a test of
  readers.
Reading of the figure [JUDGEMENT]: for the ejected member the barycentric energy is the
conserved one (flat from t = 120 on); for the captured member it is the two-body energy with M
(flat at -1.63 units from t = 120 on). In the 280 M of the passage both settle by t = 120 in
Newtonian dynamics.

## 2026-11-15 E4 test 1 rerun (run F-20261115-173821-b2c969a)

10/10 checks passed after the fixes (velocity from positions within 3.0e-5 of the true one;
barycentric energy range 1.54e-4 = V5b's). [VERIFIED]

## 2026-11-15 E5. Tracker files across chain segments (prediction)

Found while preparing P1 (reading the source, [VERIFIED] at the locators): AthenaK opens the
tracker file `<base>.co_<n>.txt` with truncation at every start, also on a restart
(`athenak/src/z4c/compact_object_tracker.cpp` line 78, `ofile.open(ofname)`), while the
horizon summaries, the history and the waveforms are appended (`fastflow.cpp` line 252,
`outputs/history.cpp` line 420, `z4c_wave_extr.cpp` lines 153, 176). `scripts/submit_chain.sh`
restarts every segment in the same run directory and keeps no copies, so a chained passage
would keep the trajectories of its last segment only. Remedy without source change:
`scripts/athena_keep_trackers.sh`, given as the executable, copies the tracker files to
`trk_keep/<time>/` before it starts the real executable; `nrread.read_trackers` joins them.
Test `scripts/test_keep_trackers.sh` (processors, small mesh): segment 1 to cycle 8, segment 2
restarted from the end of segment 1 to cycle 12.
Prediction: the live file after segment 2 starts at cycle 8 (or 9) - the truncation is real;
the wrapper kept one copy; the merged tracker has cycles 0-12 once each; a cycle written by
both segments has identical positions (processor runs are byte reproducible); the horizon
summary has no duplicate times after the reader. Refuted if the live file still holds
cycles 0-7 (then the truncation reading of the source is wrong and the wrapper is not
needed).

## 2026-11-15 E6. Baseline predictions for P1 at q = 4, time-resolved over the run (prediction)

What: `scripts/baselines_p1.py inputs/p1_q4.athinput` (the lead's functions of
`stage/G0/checks/lead_checks.py`, read only; HRNA of `geodesic_binary/hrna.py`): full Newton,
HRNA with the hole fixed and Newton with the hole fixed, from the P1 start state, with the
events inside the 280 M of the run (who leaves, when the binary is wider than 2 a_b, the
captured member's turning points, distances at t = 280).
Prediction: it reproduces the lead's V5/V5b/V6a numbers for q = 4 exactly (same functions,
same state; runs F-hills-20261115-145251-090f5dc, -145559-a314517): Newton full ejects m1
(comp0) with +1.3119 units against the barycentre (unit 4.96e-3 M), m2 bound with
a = 7.75, e = 0.25, pericentre 5.81 M, closest approach 5.78 M; HRNA ejects m2 with +0.970
units and binds m1 (E1 = -0.500) with a first pericentre of 7.26 M at t = 121; Newton with
the hole fixed ejects m1 (+1.83) and binds m2 (pericentre 6.11 M at t = 142). New numbers
(no prediction beyond [JUDGEMENT]): the binary is wider than 2 a_b between t = 100 and 140 in
all three; at t = 280 the ejected member is beyond 60 M in all three. Refuted if any of the
reproduced numbers differs in the third digit.

## 2026-11-15 E6, outcome (run F-20261115-174102-ffa764f; `results/baselines_p1.json`, `figures/fig_baselines_p1.png`, read)

Reproduced in every printed digit [VERIFIED]: Newton full ejects m1 (comp0), barycentric energy
+1.31187 units (range 1.54e-4 after t = 300), m2 captured with two-body energy -1.6265 units,
closest approach 5.777 M (pericentres 5.777 at t = 122.1, 5.806 at 250.9; apocentres 9.685 at
186.9, 314.7); HRNA ejects m2 with +0.97030 units and binds m1 (E1 = -0.49995), first pericentre
7.262 M at t = 121.0, apocentre 41.97 M at t = 566, then falls through 5.2 M (model stopped at
t = 987, `status` 1); Newton with the hole fixed ejects m1 (+1.835) and binds m2 (pericentre
6.107 M at t = 142.1). The binary is wider than 2 a_b (a_b = 5.111) at t = 115.7 (Newton full),
121.3 (hole fixed), 134.6 (HRNA): inside the predicted 100-140.
Failed part of the [JUDGEMENT]: at t = 280 the ejected member is at 76.0 M (Newton full) and
79.2 M (hole fixed), but at 51.7 M in HRNA (m2), not beyond 60 M.
What P1 decides inside its 280 M [JUDGEMENT]: the two baselines disagree about WHICH member
leaves. Newton: m1 (comp0) leaves (r_1M = 76 at t = 280), m2 (comp1) bound between 5.8 and
9.7 M with its second pericentre at t = 251. HRNA: m2 leaves (51.7 M at t = 280), m1 bound on a
wide orbit (27.9 M at t = 280, outbound). The two differ from t = 100 on (m1 at 12 M in Newton
against 7.3 M in HRNA at t = 120). The heavy hole of the full Newtonian problem moves 13.3 M
by t = 280 (recoil): the NR trackers must be read relative to the heavy hole's tracker.

## 2026-11-15 E1, outcome (run F-20261115-173543-29e87e8, stopped after part (a))

(a) Trees at t = 0 of the q = 4 three-black-hole data [VERIFIED, `counts.txt` of the run]:
1128 MeshBlocks at m/4 (9 levels), 1716 at m/8 (10), 2514 at m/16 (11). The m/8 count is the
wave-1 count (F-hills-20261115-131933-907e5fe): prediction met; m/4 inside 1300 +- 200 (at the
lower edge); m/16 inside 2400-3700. 2514 blocks at m/16 fit one card at t = 0 (slots about
3000, interface multi_puncture.md section 5); along the passage they will grow.
(b) Not done: the single-puncture probe needs 186 s per cycle on one processor core (the
processor build is serial; the machine's load was 40), so 16 cycles at m/8 and m/16 would
take about two hours. Stopped by process id; the card runs S1-S3 print the same counts.

## 2026-11-15 E7. P1 smoke test on a card (prediction)

What: `inputs/p1_q4.athinput` with `time/nlim=400` (t = 1.5625 M) on one card, release card
executable (batch run). Purpose: the numbers the cost of P1 rests on, measured on the actual
input, and the first rows of its trackers and finders for the readers.
Predictions [JUDGEMENT, from E1 and wave 1]: 1716 MeshBlocks at the start, between 1716 and
2000 at cycle 400 (the wave-zone criteria fall inside the padding of the punctures); rate
1800-2400 MeshBlock-cycles per second; card memory 55-75 GB at 2700 slots (26 MB per slot,
three finders); three horizons from the first search, members 0.128-0.132 M (bare 0.125 times
the background factor about 1.03 plus the momentum), heavy 1.00-1.01 M; trackers start at the
input positions; no non-finite value. Cost then [arithmetic]: 71680 cycles for 280 M at
dt = 0.25 x 0.015625; at the measured rate and a mean of 1.11 times the t = 0 count (core's
growth in its three-hole run) about 15-19 card-hours.

## 2026-11-15 E5, outcome (run F-20261115-173930-deef41a)

3 of 4 checks passed; the failed one was my expectation of the row convention, not the
wrapper. [VERIFIED, `run.log`, `run/single.co_0.txt`, `seg1_co_0.txt` of the run]
- The truncation is real: after the restart at cycle 8 the live tracker file holds rows 8-11
  only; segment 1 had written rows 0-7. The wrapper kept segment 1's file in
  `trk_keep/20261115T175420.453753791/`.
- FAILED expectation: "merged cycles 0-12". The tracker writes the row of cycle n at the start
  of cycle n, before the step: a segment that stops at nlim = 8 holds rows 0-7 and the
  restarted one writes row 8 first; after 12 cycles the rows are 0-11. The merge gave exactly
  0-11, once each: complete. No cycle was written twice, so the identity of repeated rows was
  not tested here (the synthetic test of E4 covers an overlap).
- Horizon at t = 0 not found at this coarse test resolution (cells m/2): not a check of the
  finder.
- Processor speed of the release build: 10689 zone-cycles per cpu second (2.6
  MeshBlock-cycles per second; `seg2.log`).
Follow-up: `scripts/check_keep_trackers.py` repeats the checks on the same output with the
convention above, plus continuity of the position across the junction (prediction: all
pass; refuted if the merged rows are not 0-11 or the position jumps at row 8).

## 2026-11-15 E5 follow-up, outcome (run F-20261115-181049-ab04d03)

7/7 checks passed on the same output with AthenaK's row convention: segment 1 rows 0-7, the
live file after the restart rows 8-11 only, the kept copy equal to segment 1, merged rows 0-11
once each with a constant step 0.125, and the position at row 8 within 1.2e-5 of the
quadratic extrapolation of rows 5-7 (third difference 1.1e-5). [VERIFIED] The wrapper and
the merging reader are ready for the chain of P1.

## 2026-11-15 E2, outcome (C0: run F-20261115-173547-a02af7d; analysis F-20261115-181053-d52f22d)

Numbers [VERIFIED, `c0_constraints.json` of the analysis run; the norm recomputed from the
dumps equals the history file's to the printed digits, volume 1.3660e8 both]:

| case | blocks | code | closed form | code - closed |
|---|---|---|---|---|
| none, m/4 | 1128 | 1.207e-2 | 1.633e-5 | 1.207e-2 |
| none, m/8 | 1716 | 5.024e-5 | 1.635e-5 | 4.833e-5 |
| none, m/16 | 2514 | 1.633e-5 | 1.635e-5 | 2.465e-7 |
| approx, m/4 | 1128 | 1.191e-2 | 4.899e-7 | 1.191e-2 |
| approx, m/8 | 1716 | 4.713e-5 | 4.909e-7 | 4.711e-5 |
| approx, m/16 | 2514 | 5.514e-7 | 4.908e-7 | 2.298e-7 |
| plain sum, m/8 | 1716 | 4.709e-5 | 3.018e-6 | 4.688e-5 |

At m/8 the residual near the members (r < 1 M) is 4.57e-5 (approx) and near the heavy hole
(r < 4 M) 1.15e-5; elsewhere 1.0e-7, equal to the closed form. Order of the truncation error
(log2 of successive ratios of code - closed): 7.96 and 7.62 (none), 7.98 and 7.68 (approx).
Figure `fig_c0_constraints.png` of the analysis run, read: at m/16 the profile of |H| through
m1 lies on the closed form outside about 0.1 M of the puncture for both variants; at m/4 the
corrected data's residual is wrong by orders of magnitude within 0.4 M.

Against the predictions:
1. FAILED at m/8 in the code's norm: approx (4.713e-5) and plain sum (4.709e-5) are equal to
   0.1 percent and only 6 percent below none (5.02e-5); ratio none/approx 1.07, not 2-30. At
   m/8 truncation at the punctures is about 100 times the residual of the corrected data.
   The order approx < plain < none holds in the closed form (4.9e-7 < 3.0e-6 < 1.6e-5) and in
   the code at m/16 (ratio none/approx 29.6).
2. FAILED in its first half: the `none` norm falls by 3.1 from m/8 to m/16 (truncation still
   larger than the algebraic residual at m/8). Second half met: at m/16 it equals the closed
   form within 0.1 percent.
3. Met: the `approx` norm falls 85 times from m/8 to m/16 and is 1.12 times its closed form at
   m/16. The resolution-independent residual of the corrected data is 1/33 of the
   uncorrected one, just outside the predicted 1/30-1/3 (the correction does better).
4. FAILED on the high side: order 7.6-8.0, not 3-7 (pre-asymptotic; I name no cause).
Reading for P1 [JUDGEMENT]: at the passage's resolution m/8 the t = 0 constraint violation
is set by the mesh, not by the data; the data's own violation (4.9e-7 with the correction,
1.6e-5 without) is visible only from m/16 on. The correction is still needed for the
members' masses (three_punctures PLAN section 5: 2.5e-3 M per member without it at q = 10).

## 2026-11-15 E4 test 3, outcome (run F-20261115-181805-f9c3473 on C0's case approx at m/8)

2 of 4 checks passed [VERIFIED, `test_nrread_three.json` of the run; rows of
`hills.horizon_summary_<n>.txt` and `hills.co_<n>.txt` of C0's `approx_L10`]:
- three trackers, at the input positions within 4.1e-9;
- FAILED: the finder of m2 (comp1, P/m = 0.268) returned no horizon at t = 0 (NaN row); m1 and
  the heavy hole were found;
- FAILED narrowly: m1 0.12778 M (predicted 0.128-0.132) and the heavy hole 0.99607 M
  (predicted 1.00-1.01). Both lie 0.7-0.8 percent below bare mass times the background factor
  (factors 1.0296 and 1.0040: `results/c0_constraints.json`, `lam`). [JUDGEMENT] At m/8 and
  M/8 the horizon radius is about 4 cells; the single-puncture runs at m/8 and m/16 (E3) will
  show how the finder's mass depends on resolution. No cause is named for the missing m2
  horizon until a run has tested one (E7 has 25 searches).
Note: the first version of the test wrote its JSON into the directory it read (C0's
`approx_L10`); moved to the run directory of F-20261115-181805-f9c3473, and the script now
writes to `$NRPIC_RUN_DIR`.

## 2026-11-15 E3a. The single-puncture analysis on core's run A (prediction)

Before the card runs start: `scripts/single_analysis.py` (with `nrread.py`) on core's
registered run A of test 1b, core-20261115-121046-0c197fb (m = 1, P = 0.3 corrected, cells
m/16, eta m = 2, 40 m, spheres 10 and 14 m; read only). Prediction: it reproduces the numbers
core published for that run (interface `multi_puncture.md` section 8, test 1b): horizon mass
1.0107 at the first search, constant to 2e-4; tracker speed ratios 0.48, 0.55, 0.61 of
P/M_ADM over t = 10-20, 20-30, 30-40 (to +-0.02; core's M_ADM may be the full solution
1.0547 or the second order 1.0563, a 0.15 percent difference); H norm 2.3e-6 at t = 0.
Refuted if any differs beyond these tolerances (then my readers or my reading of core's
definitions are wrong).

## 2026-11-15 E3a, outcome (run F-20261115-182100-613c9c6; output in `out/` of the run)

Met [VERIFIED, `out/single_analysis.json`, figure `out/fig_single_gauge.png` read]: with
P/M_ADM = 0.3/1.05625 (second-order ADM mass, the data on the mesh) the tracker speed ratio is
0.480, 0.557, 0.616 over t = 10-20, 20-30, 30-40 (core: 0.48, 0.55, 0.61); horizon mass at the
first search 1.010719 (core: 1.0107), at the end 1.010807 (first to end +8.9e-5, inside core's
"constant to 2e-4"); <H^2>^(1/2) = 2.35e-6 at t = 0 (core: 2.3e-6). The readers and my reading
of core's definitions agree with core's published numbers.
Seen in the figure: the horizon mass has single-search dips of up to 1.8e-3 between t = 20 and
36 (finder noise, not a trend); drifts are therefore read from medians over windows, not
from single rows. The junk estimate is meaningless for this run (spheres at 10 and 14 m, run
ends at 40 m before the window closes; flagged `complete: false`).

## 2026-11-15 E8. Why the finder of m2 finds nothing at t = 0 (prediction)

What: `scripts/finderdiag.sh`: the P1 data (`inputs/p1_q4_finderdiag.athinput`, a copy with
`<fastflow> verbose = true`) for one cycle on processors. Source read first [VERIFIED at the
locators]: the first guess of a puncture's finder is a sphere of radius
max(m/2, min(m, d/2)) with d the largest distance to any puncture
(`athenak/src/z4c/fastflow.cpp` lines 470-476), i.e. radius m = 0.125 for both members; a
search fails on a non-finite area or mean expansion, on |hmean| > hmean_tol (100 for both,
`nrpic_puncture_setup.hpp` line 178), on a negative mean radius or a mass below 1e-10, or
after 400 iterations without |dmass| < mass_tol = 1.25e-6 (lines 742-800 of fastflow.cpp).
Prediction [JUDGEMENT]: m1 and the heavy hole converge as in C0 (0.12778, 0.99607); m2 fails
by reaching 400 iterations (its larger momentum distorts the horizon, and the flow constant
m^2 = 0.0156 moves the surface slowly on 4 cells per radius), not by a non-finite value.
Refuted if the verbose file shows another reason; then the request to core names that one.

## 2026-11-15 E8, outcome (run F-20261115-182223-17ca48a; `hills.horizon_verbose_<n>.txt` of the run)

[VERIFIED, read in the verbose files] All three searches start from a sphere of radius 0.125
(members) and 1.0 (heavy hole) at cycle 4's search time t = 0.
- m1 (horizon 0): the flow shrinks the surface for 25 iterations and settles; found at
  iteration 30, mass 0.127780, mean radius 0.0588 (3.8 cells of 0.015625).
- m2 (horizon 1): the same approach for 25 iterations (mass 0.1283 at iteration 23), then the
  surface does not settle: over the last 100 of 400 iterations the mass jumps between 0.1264
  and 0.1367 (mean 0.1285) and hmean changes sign with |hmean| up to 4.6; "Failed, reached max
  iterations 400". No non-finite value.
- heavy hole (horizon 2): found (as in C0).
Prediction: met in the outcome (400 iterations, no non-finite value), FAILED in the mechanism I
wrote: the flow is not slow; it reaches the horizon's neighbourhood as fast as for m1 and then
oscillates by about 8 percent in mass, far above mass_tol = 1.25e-6. I name no cause; what
differs from m1 is the momentum (P/m 0.268 against 0.234) and the position of the puncture
relative to the cells. For P1 [JUDGEMENT]: the mean over the oscillation (0.1285) is close to
the found value of m1 scaled by the background factors (0.12778 x 1.0273/1.0296 = 0.1275), but
it is not a horizon; member horizon masses at m/8 may be intermittent. Request to core
(README): a convergence test that does not require |dmass| < 1e-5 m when the surface
oscillates on about 4 cells per radius, or advice on the flow constant; E7 shows whether the
search succeeds later in the evolution.

## 2026-11-15 S1 withdrawn before it started (run F-20261115-173606-efcbf69, Slurm job 4475)

The card queue had six jobs ahead of this package's at 18:37 UTC. With S1's wall limit the
three card jobs could have used up to 2.25 card-hours, above the two the task allows; S1 was
the optional resolution partner of the junk measurement. Cancelled (scancel through
`nrpic-run stop`) before it started; no card time used. It can be resubmitted with
`inputs/batch_S1.list` when S3 and S2 have given the rate. E3's prediction 3 (S1 against
S3 within a factor two) stays untested.

## 2026-11-15 E9. The passage analysis on the synthetic three-body files (prediction)

What: `scripts/p1_analysis.py` (the readers applied to a passage: distances, member energies,
horizons, history, waveforms) on the synthetic run directory of E4 test 1 (run
F-20261115-173821-b2c969a, `run/`: the full Newtonian q = 4 trajectory to t = 1500 in
AthenaK's tracker format, split into two segments with an overlap, and horizon summaries),
with the baselines of E6. Prediction: receding member m1 (comp0); at the end its barycentric
energy +1.3119 units and m2's two-body energy with M -1.6265 units (E6); the binary wider
than 2 x 5 between t = 115 and 116; no history and no waveforms reported (absent), the
script does not fail on their absence. Refuted otherwise.

## 2026-11-15 E9, outcome (run F-20261115-183737-49f0a7f; figure `fig_p1_analysis.png` of the run, read)

Met [VERIFIED, `p1_analysis.json` of the run]: receding member m1 (comp0); at t = 1500 its
barycentric energy +1.31187 units (two-body with M +1.6404), m2's two-body energy with M
-1.62654 units; binary wider than 10 M from t = 115.19; the merged segments and the horizon
files read; absent history and waveforms skipped. Only change after the run: a shorter label
of the energy panel (it was cut off in the figure).

## 2026-11-15 State at hand-over (19:50 UTC)

Done and checked: E1 (trees), E2 (t = 0 constraints against resolution), E3a (the analysis
reproduces core's test 1b), E4 tests 1 and 3, E5 (tracker truncation and the wrapper), E6
(baselines of P1), E8 (the missing m2 horizon at m/8), E9 (passage analysis on synthetic
files). P1 is prepared (README, "P1") and not submitted.
Not done: E3 (S3, S2) and E7 (P1 smoke) are queued on the cards (jobs 4474, 4476; no card
time used so far); their predictions above stand and their outcomes are not recorded; S1
withdrawn; the S2 repeat with core's mass-scaled shift damping waits for core's READY. The
commands to close and analyse the pending runs are in README, "Pending".
Card-hours used by this package: 0 (reserved for the two queued jobs: at most 1.4).
Processor time: about 1.6 core-hours (C0 35 min, wrapper test 22 min, finder diagnostic 13 min,
stopped probes 13 min, analyses).
