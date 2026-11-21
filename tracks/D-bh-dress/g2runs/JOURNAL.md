# JOURNAL of the package g2runs (Track D, batch 3 of wave 3)

Helper of D-bh-dress for one work package: the first G2 runs with the outer faces far
(ES-1GB, its vacuum control V-1GB) and the first matter run into the hole (ES-F). Card cap
of the package: 3 card-hours. Units M = initial hole mass. Entries are appended, never edited
(except the outcome lines that an entry announces).

## Entry 0 (2026-11-21 04:58 PST): state at the start

- Worktree at c55dc733 (main merged, nothing to merge). Untracked in the worktree:
  `drift_controls/tools/{compare_runs,count_blocks,slice_profiles}.py` (another package's,
  left as found). No D job queued or running (squeue 04:53 PST: one job of another user).
- No other session of this batch works on secondary_infall (harness/workflows/batch-3.json
  on main: D has the packages g2runs and note only). secondary_infall/JOURNAL.md (last
  entries 2026-11-21T09:31-09:35Z) records the run to a/a_i = 30 as DONE in batch 2b
  (P192, D-20261121-075559-31835c4, late-time predictions failed from an edge-layer energy
  error, VERIFIED there) and the clean run to a/a_i = 16 (Q16, D-20261121-085652-7e189a2).
  What it leaves open is a clean run beyond 16 (initial ball resolved by about nine cells:
  nx ~ 450-500 or a refined centre). Cost estimate for that below (entry 2), decision there.
- Executables: release core-v0.4, `.work/build_gpu_v04/src/athena` (cards) and
  `.work/build_cpu_v04/src/athena` (processors), as the task names. `lapse_leak` is merged
  from core/gauge unchanged in definition (coord/INTERFACES/cosmo_gauge.md section 7.1);
  the merged executable reproduces the gauge branch's processor bytes on its example
  `flrw_leak` (tracks/core/RELEASE-v0.4.md, quick test, run core-20261121-025955-bd47414)
  [VERIFIED as a record of core, not rerun here]; the ES example `es_gauge` was not run
  with the merged executable (same file, "not started" list). The corrections of core-v0.4
  that act without an option (CHANGELOG section core-v0.4, items 1-6) do not touch these
  inputs: tracers carry m = 1e-30, not 0 (item 3); the metric is the mesh, not analytic
  (item 4); no collisions, no linear wave [JUDGEMENT from the item list].
- ES-1G ran on `scratch/core/exe/core_gauge/athena_gpu`, V-1 and V-1B on core-v0.3. So
  ES-1GB against ES-1G changes the faces and the executable, V-1GB against V-1B the gauge
  and the executable. A processor check that the executable change is neutral on these
  data is entry 1's prediction X1 (cheap, run while the cards work).

## Entry 1 (2026-11-21 05:00 PST, before submission): ES-1GB and V-1GB

Inputs, built by `tools/make_inputs.py` (it asserts every replacement and prints the
diffs): `inputs/es1gb_bnd384.athinput` = es_runs/inputs/es1g_dx8.athinput with the outer
faces at +-384 M (root dx 8 M; new level 1 on +-191.9 M; old levels 1, 2, 5 become 2, 3,
6), i.e. exactly the root change of drift_controls/inputs/v1b_bnd384.athinput; basename
es1gb. `inputs/v1gb_bnd384.athinput` = v1b_bnd384 plus `<z4c> lapse_leak = 0.5`,
`lapse_leak_alpha = 1.0`; basename v1gb. ES-1GB and V-1GB then differ only in the problem
line, basename, particle file and table (checked with diff against V-1B: the same four
lines plus the two lapse_leak lines). Executable: release core-v0.4 card build. Chain
launcher, tlim 200 M, scouting, gate G2.

Reference numbers (all [VERIFIED] by the lead's recheck, run D-20261121-063617-3f2036f,
stage/REVIEW-wave3.md sections 1 and 3): ES-1G M_AH(100 M) - 1 = +1.1410e-3; drift
D(t) = M_AH(t) - M_AH(100 M) on 100-165 M in [-4.17e-4, +9.46e-4], maximum +6.963e-3 at
199.5 M, minimum -4.167e-4 at 126 M; mean coordinate radius 1.398 M at 25 M, 0.776 M at
199.5 M. V-1B (faces +-384 M, plain 1+log): D on 100-199.5 M in [-4.84e-5, +1.97e-5];
V-1B and V-1 agree to 1e-15 until t ~ 90 M, separate by more than 1e-9 at 116 M and more
than 1e-6 at 133 M. ES-1G slice mass (es_runs README, K1-K2, run D-20261120-222956-6abf860):
the exterior plateau 2.7397 is lost from the faces inward (beyond r ~ 105 M at t = 100 M,
r ~ 62 M at 150 M, everywhere at 200 M); bubble mass within 1.0005-1.0020 up to 150 M.

Hypotheses for ES-1G's late growth (+6.96e-3 over 100-200 M):
- HB (boundary): the outflow faces at +-192 M do not hold the Painleve-Gullstrand exterior;
  the error enters from the faces and reaches the hole after ~130 M. With the faces at
  +-384 M the front cannot reach the hole within 200 M (it moved at ~0.9 c in ES-1G:
  192 -> 105 M in 100 M; from 384 M it would be at ~200 M by t = 200 M).
- HG (gauge and resolution at the hole): lapse_leak shrinks the horizon in coordinates
  (1.40 -> 0.78 M, 6.2 cells of M/8) and the slice mass near the hole grows by itself.
  Then the growth stays when the faces move and appears in the vacuum control too.
- HD (dust): the dust outside the bubble acts on the hole through the gauge; then it
  stays in ES-1GB and is absent from V-1GB.

Predictions (HB is the favoured one [JUDGEMENT], from V-1B):
B1 ES-1GB drift from 100 M stays within [-6e-4, +1.0e-3] over 100-199.5 M, D(199.5 M) in
   [-5e-4, +1.0e-3]. PASS criterion of the question "does the growth go away": D(199.5) <
   1.0e-3 (one seventh of ES-1G's). REFUTED (the growth does not come from the boundary)
   if D(199.5) >= 3.5e-3 (half of ES-1G's or more).
B2 ES-1GB and ES-1G horizon masses agree within 5e-5 up to t = 90 M (card rounding and the
   executable; ES-1G and core's ES test agreed to 2e-5 on 0-30 M) and separate by more
   than 2e-4 only after t = 130 M. What would show that the growth is NOT from the
   boundary: ES-1GB following ES-1G within 2e-4 to 199.5 M (then the larger box changed
   nothing at the hole: HG or HD), or B1 refuted.
B3 Coordinate radius: the shrinking is the gauge at the hole, not the faces: ES-1GB's mean
   radius at 199.5 M = 0.78 +- 0.05 M. Outside that band the faces also set the coordinate
   size of the hole.
B4 Slice mass (analysis/diag/slicemass.py as for ES-1G): at t = 200 M the Misner-Sharp mass
   of ES-1GB keeps the exterior plateau within 2 per cent of 2.7397 on 70 <= R <= 150 M
   (ES-1G: 2.3 left) and the bubble mass within 1.0005-1.0030 at 150 and 200 M.
B5 Technical and cost: finite to the end (np > 0 in column 3 of es1gb.nrpic.hst), no
   escapes, 28 tracers removed as in ES-1G (G7), no "not used" warning for lapse_leak;
   400 MeshBlocks; 0.92 card-hours (0.85-1.05): ES-1G 0.794 times V-1B/V-1 = 0.7775/0.672.
V-1GB (matched vacuum control):
C1 V-1GB drift from 100 M within [-6e-4, +1.0e-3] over 100-199.5 M (HB: no growth without
   the near boundary; HG would show ES-1G-like growth > 3.5e-3 here too).
C2 Null test, ES-1GB against V-1GB: |M_ES-1GB(t) - M_V-1GB(t)| <= 2.5e-4 on 30-199.5 M,
   REFUTED if > 5e-4 anywhere there (the hole must not feel the dust outside the bubble;
   ES-1 against V-1 swung by up to 3.2e-4 in 25-50 M with plain 1+log, ES-1G against V-1
   0.56 of that).
C3 V-1GB's horizon shrinks like ES-1G's (0.78 +- 0.08 M at 199.5 M) and its M_AH(100 M) - 1
   = (1.1 +- 0.2)e-3 (the finder bias at that coordinate size); V-1B's (plain 1+log)
   grows to ~2.2 M.
C4 Cost 0.78 card-hours (0.70-0.86), finite, 28 tracers removed if they are as in V-1.
X1 (processor check, not gating) The release processor executable and core/gauge's
   (`scratch/core/exe/core_gauge/athena_cpu`) give the same bytes for ES-1G's input over
   the first two cycles (history, horizon summary, particle history); a difference other
   than a parameter-dump line refutes "the executable change is neutral".

## Entry 1b (05:08 PST, before the run): test of tools/compare_horizons.py on the parents

Runs X1 (D-20261121-125946-fe3840a, processors, 2 cores) and the two card jobs
(ES-1GB D-20261121-125900-ea4c442, Slurm 4794; V-1GB D-20261121-125909-06f856e, Slurm 4795;
both pending behind jobs of core and C at 05:00 PST) were submitted.
Prediction T1: on ES-1G, V-1B and V-1 the script reproduces the lead's numbers (run
D-20261121-063617-3f2036f): ES-1G M_AH(100) - 1 = +1.1410e-3, D on 100-165 M
[-4.17e-4, +9.46e-4], D(199.5) = +6.963e-3, radius 1.398 M (25 M) and 0.776 M (199.5 M);
V-1B D on 100-199.5 M [-4.84e-5, +1.97e-5], D(199.5) = -9.2e-6; V-1B - V-1 first above
5e-5 after 133 M. A difference in the printed digits refutes the reader (unique-time
handling or the reference sample).

Outcome T1 (run D-20261121-130316-84a54d4; figure `compare_horizons.png` there, looked at:
three curves, panel (c) empty as no pair was named): ES-1G M_AH(100) - 1 = +1.14098e-3,
D on 100-165 M [-4.1722e-4, +9.472e-4], D(199.5) = +6.9713e-3, radius 1.3976 M (25 M) and
0.7758 M (199.5 M); V-1B [-4.843e-5, +1.975e-5], D(199.5) = -9.214e-6; V-1 D(199.5) =
-1.3647e-4; 28 tracers removed in each run, none escaped. HELD for every number except
two of the lead's: D(199.5) +6.963e-3 and the maximum on 100-165 M +9.46e-4 come out here
as +6.971e-3 and +9.47e-4 (the finder file has one sample per time after t = 0, so the
difference of 8e-6 is in the lead's reference sample, as its "with my reference sample"
for V-1 says; es_runs K2 quotes +6.97e-3, as here). Irrelevant for B1 (thresholds 1e-3 and
3.5e-3). The tool reads correctly. Seen in panel (d): ES-1G's horizon shrinks steadily from
t ~ 30 M on (1.41 -> 0.78 M), long before any signal from the faces could arrive, while
V-1 and V-1B grow to 2.2 M; the shrinking is the gauge at the hole.

## Entry 2 (05:15 PST): secondary_infall's run to a/a_i = 30 is not carried here

The run to a/a_i = 30 exists (P192, D-20261121-075559-31835c4, batch 2b) and failed its
late predictions for a documented set-up reason (edge layer within one cell of the initial
ball; secondary_infall/README.md lines 415-423). A clean run needs nx ~ 450-500 (same
lines, [JUDGEMENT] of that package). Cost estimate [JUDGEMENT]: P192 took 0.70 h on six
threads for 2914 steps at nx = 192 (README line 277); cells x (480/192)^3 = 15.6 and steps
x 2.5 (dt ~ dx) give ~39 x 0.70 h ~ 27 h on six threads, five times this session's
window. C7 no longer waits on it: decision 0021 item 2 judges D-pre-3 on growth against
matched shells from a/a_i = 3 on, which Q16 and N128Lc cover. So nothing is started; the
open item stays with the secondary_infall package (a refined centre or the threaded build on
more cores, which needs an allotment beyond six cores).

## Entry 3 (05:25 PST, before any ES-F data): ES-F plan and the criteria evaluator

ES-F is submitted as pre-registered in flux_tools/JOURNAL.md entry 7 (input
flux_tools/inputs/esf_dx8.athinput unchanged, faces at +-192 M, chain, at most 1.97
card-hours, tlim 200 M), with one deviation: the executable is the release core-v0.4 card
build, not `scratch/core/exe/core_requests-adf/athena_gpu`. Reasons: the task of this
batch names the release executables; the input's own header allows "or the release that
merges them"; the release merges core/requests-adf and its quick and example tests give the
branch's bytes on processors (tracks/core/RELEASE-v0.4.md, runs
core-20261121-025955-bd47414 and -031604-dccccbb, cases tracer, acc, pairh, kepler; the
acc case differs only in restart header bytes). Card runs with deposition are not
byte-reproducible anyway. The predictions P1-P7 and criteria (i)-(iii), D1-D4 of entry 7
stand unchanged. It goes to the cards when one of the two D jobs ends.

`tools/esf_criteria.py` evaluates (iii), D1-D4 and the numbers of P1, P2, P5, P6 exactly
as entry 7 defines them (esf_analyse.py of flux_tools computes (i) and (ii) and is run
beside it unchanged). Prediction T2 for its test on the synthetic run of flux_tools
(D-20261119-150306-d0e692e/synth_exact: tau = 1.4 t, every dust shell removed at
tau_H + 0.3 (tau_0 - tau_H), M_AH = M + lattice sum over tau_H <= 1.4 t + noise 1e-5),
with V-1 as control: (iii) holds for the dust with every bin median in [0, +1e-3] (the
first sample after removal lags by at most 0.5 M of t = 0.7 M of tau at dM/dtau ~ 1e-3);
D4 minimum > 0 and no value below 0 (removal at 0.3 of the way to the centre); D3 holds;
P1 kappa_late = 1.40 to 1e-3. On synth_growth_x0.97: bin medians negative, between -0.7 %
and 0, growing in size with tau. Anything else is a defect of the evaluator.

Outcome T2 (runs D-20261121-130605-ded836f synth_exact, D-20261121-130611-46aa59c
synth_growth_x0.97; figure `esf_criteria.png` of the first looked at). synth_exact: (iii)
holds, 25 bins counted, bin medians in [+5.3e-6, +8.5e-4], overall +3.1e-4: HELD; D4 minimum
+0.433 M, none below 0: HELD; P1 kappa_late = 1.400: HELD; criterion (i) of compare.py
max violation 0.003 sigma, closure +0.86 %. D3 FAILED in the synthetic (minimum margin
-1.12e-3, 45536 of 61592 below -3e-4): the margin sits at -9.4e-4 for t > 30 M in panel
(c), which is minus V-1's finder bias (M_ctrl - 1 = +9.4e-4); the synthetic finder has no
bias, so subtracting the control's bias pushes it below. My prediction overlooked that; the
evaluator does what entry 7 defines, and D3 is meaningful only when the run's finder has
the control's bias (a real run). Not changed. synth x0.97: (iii) holds, bin medians in
[-5.2e-3, +1.4e-4], overall -2.7e-3: HELD in size (inside -0.7 % to 0) but not every
median is negative as predicted: an early bin is +1.4e-4, where the growth is small and the
finder-sample lag dominates; closure -2.2 %.
Correction of the clock: entries 2 and 3 were written at 05:03 and 05:05 PST (date), not
05:15 and 05:25 as their headings say; T2 ran at 05:06 PST.

## Entry 4 (05:07 PST, before ES-1GB has started): B4 reworded

B4 as written in entry 1 is wrong geometrically: at t = 200 M the dust of ES-1GB, on its
exact curve under lapse_leak, spans R ~ 69-116 M (a/a_i ~ 1.93 at t = 200 M for
H = 5.58e-3/M [JUDGEMENT, the homogeneous model]), so m(R) rises through it on 70-116 M and
is not the plateau there. B4 now reads (still before any ES-1GB data exist):
B4' slicemass.py on the restart dumps of ES-1GB: (a) the asymptotic mass at t = 50 and
    100 M within 1e-3 of 2.7397 (ES-1G: 2.7398, 2.7149 NOT FLAT); (b) at t = 150 and 200 M
    the shell medians of m on 130 <= R <= 190 M within 1 per cent of 2.7397 (ES-1G at 150 M:
    2.007 as its outer value; the face error of ES-1GB, entering at ~0.9 c from 384 M,
    should be beyond r ~ 200 M at t = 200 M); (c) M_H of the slice in the bubble within
    1.0005-1.0030 at 150 and 200 M (ES-1G 1.00136 and 1.00807).

## Entry 5 (06:14 PST): ES-1GB, first segment (to t = 185.5 M), outcome so far

Run D-20261121-125900-ea4c442 (Slurm 4794, started 05:24:55 PST; segment 1 ended at
t = 185.5 M at the 50-min limit; the chain continues). 400 MeshBlocks (column 23 of the
history), no "not used" warning in the segment log. Partial analysis
D-20261121-141419-b9f1089 (compare_horizons.py; figure looked at):
- ES-1GB and ES-1G horizon masses agree to 2.9e-15 up to t = 90 M and to 3.3e-9 at
  185.5 M (largest difference on 30-185.5 M: 3.3e-9; it rises above 1e-9 only after
  ~180 M). The horizon mass, the drift and the coordinate radius of the two runs lie on top
  of each other in every panel. B2 first part HELD (<= 5e-5 to 90 M); the second part
  ("separate by more than 2e-4 after 130 M", the HB expectation) did NOT happen: they
  never separate by more than 3.3e-9.
- Drift of ES-1GB from 100 M: [-4.17e-4, +9.47e-4] on 100-165 M (ES-1G's, to the last
  digit), D(185.5 M) = +3.647e-3, already above B1's refutation line 3.5e-3.
- So [VERIFIED for this pair, to t = 185.5 M] moving the outer faces from +-192 M to
  +-384 M changes the horizon mass by at most 3.3e-9: the late growth of ES-1G (+3.6e-3 by
  185.5 M, +6.97e-3 by 199.5 M) does NOT come from the outer boundary. HB is refuted for
  the horizon; the lead's reading (REVIEW-wave3 sections 1, 3: "the natural reading is
  that ES-1G's late growth comes through the outer boundary") does not hold. The
  executable change (core/gauge -> release) did not change the hole either (2.9e-15 to
  90 M; X1 on processors still running). Left: HG (gauge and resolution at the shrinking
  hole) against HD (dust): V-1GB decides; the slice mass (B4') says whether the faces
  still cost the exterior its mass.
Tool change before the final analysis: panel (c) of compare_horizons now reaches down to
1e-17 (the 1e-9 floor hid the pair's difference).

Outcome X1 (06:19 PST; runs D-20261121-125946-fe3840a, 12 cycles on one core each,
63 min, and D-20261121-141529-2664b51 locating the bytes): every output of the ES-1G input
is byte-identical between core/gauge b4430da and release core-v0.4 (history, particle
history, horizon summary and shape, particle snapshot, trajectories, the t = 0 slices,
tmunu slices) except (a) the two final slices written off schedule, which differ only in
their `last_time` lines (25 against 0: correction 2 of core-v0.4), and (b) the restart
files, which differ in `last_time` lines and in 36 bytes right after the header (the nine
zeroed members of `Mesh::mesh_indcs`: correction 1). HELD: the change of executable is
neutral on these data on processors; ES-1GB against ES-1G is one change (the faces).
No "not used" or lapse_leak warning from either executable.

Outcome B4' (06:22 PST; run D-20261121-142005-52adf6d on the dumps at t = 0, 50,
100, 150 and 188.03 M (the wall-stop dump of segment 1; the 200 M dump does not exist yet);
figure `slicemass_ES-1GB.png` looked at):
(a) asymptotic m = 2.739671 (50 M), 2.739839 (100 M): HELD (ES-1G: 2.7398, 2.7149).
(b) shell medians on R = 113-217 M: 2.7407-2.7421 at 150 M; on R = 119-223 M:
    2.7406-2.7414 at 188 M: HELD (within 0.07 per cent). The face error is visible only
    beyond R ~ 250 M (m 2.29 on r = 296-352 M at 150 M, 1.72 at 188 M): the exterior keeps
    its mass where ES-1G lost it (ES-1G: 2.007 at 150 M, 0.92 at 200 M as outer values).
(c) bubble M_H = 1.001358 at 150 M (HELD) and 1.005391 +- 1.1e-4 +- 4.0e-4 at 188 M
    against the band 1.0005-1.0030: FAILED (the finder gives 1.005298 at 188 M).
Where the extra mass sits at 188 M (shell table of the same run): m(R) falls outward from
1.0054 at the horizon (R ~ 2 M) through 1.0050 (R ~ 5.6), 1.0038 (R ~ 15), 1.0029 (R ~ 27)
to 1.0021-1.0027 at R ~ 40-58 and 1.0012 next to the wall; at 150 M it was 1.00134 at the
horizon and 1.0010-1.0011 on R = 10-40 M. So between 150 and 188 M the slice gains ~4e-3
of Misner-Sharp mass concentrated at the hole and falling off over R ~ 2-20 M, with the
exterior intact. [JUDGEMENT] A constraint violation that grows at the shrinking hole
(6.4 cells of M/8 in radius at 188 M), not an inflow from outside; V-1GB decides whether
it needs the dust.

## Entry 6 (06:47 PST): V-1GB outcome; ES-F submitted

V-1GB D-20261121-125909-06f856e (Slurm 4795, 05:59-06:46 PST, one segment, DONE at
t = 200 M, 0.7811 card-hours, closed with nrpic-run finish). ES-F submitted at 06:46 PST
as D-20261121-144631-aa7ce9b (Slurm 4806, pending), the command of entry 3.
Analysis D-20261121-144657-cf510fc (compare_horizons.py on ES-1G, ES-1GB to 188 M, V-1B,
V-1GB; figure looked at: four panels, all four runs visible, the pair differences down to
1e-17 in panel (c)).
- C1 FAILED: V-1GB drift from 100 M is [-5.60e-4, +1.265e-3] on 100-199.5 M (band
  [-6e-4, +1e-3]); D(199.5) = +1.265e-3. It dips to -5.6e-4 at ~140 M and grows from
  ~160 M, the same shape as ES-1G/ES-1GB (minimum -4.2e-4 at 126 M, +6.97e-3 at 199.5 M)
  but later and five times smaller. V-1B (same mesh, plain 1+log): within 4.8e-5.
- C2 REFUTED: |M_ES-1GB - M_V-1GB| equals rounding (1e-15) to t ~ 12 M, stays below
  1e-6 to ~30 M and below 1.0e-4 to 90 M, exceeds 2e-4 from 137.5 M on and reaches
  3.53e-3 at 188 M. On 30-100 M the null test holds at 1e-4 (C2's band 2.5e-4), not
  after ~135 M.
- C3 FAILED on the radius, HELD on the mass: V-1GB's horizon shrinks too (1.398 M at
  25 M, 0.875 M at 199.5 M; ES-1GB 0.795 M at 188 M, ES-1G 0.776 M at 199.5 M; V-1B grows
  to 2.196 M); band 0.78 +- 0.08 missed by 0.015. M_AH(100) - 1 = +1.186e-3 (band
  (1.1 +- 0.2)e-3).
- C4 HELD: 0.781 card-hours, finite, 28 tracers removed, none escaped; mesh minimum of
  the lapse 0.0475-0.0584 after 108 M (ES-1GB 0.050-0.066; V-1B 0.019-0.021).
Reading of entries 5-6 together:
- [VERIFIED] The outer boundary does not cause ES-1G's late horizon growth (entry 5: the
  hole of ES-1GB follows ES-1G to 4.2e-9 to t = 188 M while the exterior mass is kept,
  B4'); HB is refuted.
- [VERIFIED] The relaxed lapse makes the late growth even in vacuum: V-1GB grows by
  +1.27e-3 over 160-200 M where V-1B (plain 1+log, same mesh, same faces) stays within
  4.8e-5. With the dust outside the bubble the growth starts earlier and is 3-5 times
  larger (ES-1GB +4.16e-3 at 188 M against V-1GB's +0.62e-3 at 188 M, read from the same
  json).
- [JUDGEMENT] HG with a dust-dependent rate: lapse_leak shrinks the hole in coordinates
  (0.78-0.88 M, 6-7 cells of M/8 by 200 M, where plain 1+log keeps it at 2.2 M); the
  slice mass then grows in a region concentrated at the hole (B4', entry 5) as the
  horizon loses resolution; the dust outside changes the lapse and shift inside the
  bubble (the two runs separate from 12 M on, long before matter could reach the hole)
  and makes the hole shrink faster (0.795 against ~0.89 M at 188 M), hence the earlier
  growth. Not shown: that the growth falls with resolution (an M/16 nest of ES-1GB and
  V-1GB would show it; the lead's plan has it next).
- Consequence for G2: with lapse_leak at M/8 the null test (ES-1GB against V-1GB) holds
  at 1e-4 only to t ~ 100-135 M; over 100-200 M the floor is 3.5e-3, set by the gauge and
  resolution at the hole, not by the faces. The faces at +-384 M are still worth keeping
  for the exterior mass (B4').
