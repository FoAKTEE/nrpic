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
