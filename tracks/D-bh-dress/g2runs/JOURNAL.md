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
