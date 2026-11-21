# JOURNAL of core

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:53Z  session core-lead (integration of wave 1)  commits 74ed745..048bd93 (and this edit)  runs: core-20261115-065452..150426, list in stage/G2/EVIDENCE.md

Helpers of this wave and their own journals: interfaces (`tracks/core/interfaces/JOURNAL.md`),
verify (`tracks/core/verify/JOURNAL.md`), id (`JOURNAL-id.md`), rng (`JOURNAL-rng.md`),
coll (`JOURNAL-coll.md`), scalar (`JOURNAL-scalar.md`), newton (`JOURNAL-newton.md`),
mp (`JOURNAL-mp.md`).

### Did (before the tests)
- Merged into core/nrpic, in this order: core/rng (fcc3179), core/collisions (c88804c),
  core/scalar-field (65648c8), core/id-extrinsic (dc93a72), core/multi-puncture
  (7c11538), core/newton (66bd4c3). Textual conflicts only in the newton merge
  (CMakeLists.txt source list, end of NrpicInit, members before `private:` of
  particles.hpp), resolved by keeping both sides.
- Two maintainer fixes on top: 0f11630 (format-2 curvature `+=` instead of `=`, so that
  the Bowen-York curvature of moving punctures survives; the hazard named by mp) and
  609a875 (collisions refused with `pusher = newton`, whose lapse slot holds the
  potential).
- test2_numbers.json (1.5 MB) of the id package replaced at the tip by its gzip copy.
- Builds from a snapshot of the source (git archive): baseline = main source at 74ed745
  (`.work/build_cpu_base`, `.work/build_gpu_base`), merged = 609a875
  (`.work/build_cpu_609a875`, `.work/build_gpu_609a875`). The merged processor build
  has the same nine compiler warnings as the baseline, none in new files.
- Independent check of the random-number twin (not a run of the code): 3000 keys incl.
  zero and all-ones counters and keys, python/nrpic/rng.py philox4x64 against numpy's
  Philox (my own counter mapping): 0 mismatches.

### Predictions (written before the runs)
P1 Byte regression, processor, baseline vs merged, newton's tool (cases geo, boris, dep,
   east, os, jeans, binary) and rng's tool (c1-c5): every output file identical except
   the 35-36 never-set bytes of mesh restart headers (offsets 8252-8287, known from the
   scalar and rng packages). Refuted by any other differing byte.
P2 nrpic_cf regression (mp's regress_cf.athinput, id's cf_table_regress.athinput),
   processor: all data files identical between baseline and merged. Refuted by any
   differing data file.
P3 Verify suite on the merged executables: G 104/104 on processors; O 13/13, F 13/13,
   L (variant number) 10/10 on a card, numbers equal to the verify package's to the
   printed digits (the card is not byte-reproducible with deposit, so O and L may differ
   in the last digits; a change above 1e-10 relative in M_AH or delta would refute).
P4 Quick tests of the merged packages, merged processor executable: rng table equal to
   the twin bit for bit; collision replay and option-absent identity as on the branch;
   scalar test 1 (wave) orders 2/4/6; Newtonian point-mass field error 1.61e-2 at N=32
   (to 3 digits); Bowen-York static data at one resolution equal to mp's numbers; id
   test-0 reader agreement 1e-16. Refuted by any verdict that differs from the branch.
P5 Combined initial data (new test, needs the fix 0f11630): K_ij of a run with a format-2
   table and a puncture with momentum equals, to rounding (1e-15 relative), K_ij of the
   same table with a momentum-free puncture plus K_ij of a format-1 table with the same
   u(r) and the moving puncture. Without the fix the Bowen-York part would be missing
   (difference of order P psi^-2/r^2). Refuted by a difference above 1e-13 of max|K|.

### P5, first outcome and revised criterion (15:04Z, before the rerun)
- Run core-20261115-150315-23eca56 (merged processor executable): K(comb) - [K(A) + K(B)]
  is 9.96e-8 of max|K| at most, while K(comb) - K(A) = K(B) is of order one (5.9 in
  K_yy): the Bowen-York part is present, but my criterion of 1e-15 failed. Cause, not
  yet tested when this is written: the `.bin` dumps are single precision (the interfaces
  helper had recorded it, diagnostics.md), so each of the three stored values carries a
  float32 rounding; I predicted with double precision in mind. A failed prediction of the
  analysis, kept on record.
- Revised criterion (written before the rerun): point by point
  |Kc - (Ka + Kb)| <= (ulp32(Kc) + ulp32(Ka) + ulp32(Kb))/2; PASS if no point of any
  component exceeds it. Refuted by a single point above the bound.
- The first combined runs inside core-20261115-145448-3629622 (processors) and
  core-20261115-145939-3629622 (card) failed before P5 started: the command line set
  parameters that regress_cf.athinput does not have (AthenaK refuses them). The P5 input
  is now written by the script.

### Outcomes (15:06Z)
Executables: processor baseline `.work/build_cpu_base` (main source 74ed745), merged
`.work/build_cpu_609a875`; card baseline `.work/build_gpu_base`, merged
`.work/build_gpu_609a875` (sha256 in `scratch/core/tmp/lead/exe_sha256.txt`).
- P1 HOLDS. Newton's tool, processors: geo, boris, dep, east, jeans, binary identical in
  every file; os identical except the restart files, which differ in 34 bytes at
  offsets 10858-10893 = the never-set mesh_indcs bytes (masked comparison: IDENTICAL,
  18 files) (runs core-20261115-145316/145317 geo, -145318/145319 boris, -145320/145325
  dep, -145329/145337 east, -145344-5407341/-145755-3629622 os, -150203/150210 jeans,
  -150217/150256 binary). rng's tool, processors (core-20261115-145323-5407341): c1-c4
  identical; c5 differs only in the three mesh restart files, 32 bytes inside
  8253-8288 (masked: IDENTICAL, 10 files). Card (job 4430, core-20261115-145921-3629622):
  c1, c2 identical; c3-c5 deposit, baseline differs from itself in the same files, no
  verdict (as predicted for the card).
- P2 HOLDS. regress_cf IDENTICAL (16 files) on processors (core-20261115-145448-3629622)
  and on the card (core-20261115-150426-9377fe8); cf_table_regress IDENTICAL at the start
  on the card (6 files, start-only comparison); its full processor comparison is still
  running inside core-20261115-145448-3629622 at the time of writing (see the next entry).
- P3 HOLDS. G (processors, core-20261115-065452-3629622) 104/104, all 104 values equal to
  the verify run. O (core-20261115-065901-3629622) 13/13: first horizon mass
  1.000352575670864 as before, max|M_AH - 1| equal to 3e-12 relative. F
  (core-20261115-065903-3629622) 13/13, every value equal to all printed digits. L
  (core-20261115-065904-3629622) 10/10, delta/linear - 1 equal to 2e-12 absolute (card
  deposit scatter). Card job 4429, 5 min 23 s.
- P4 HOLDS for what was rerun. rng kick demonstration D1 (core-20261115-145543-3629622):
  14 of 14 expectations, checksums of a1 and n1 identical to the rng helper's build
  (run core-20261115-121609-fb0491a). Collision replay (core-20261115-145545-3629622): 7
  of 7 cases, momenta to 8.9e-16 (flat) and 9.8e-15 (curved), as on the branch.
  Scalar test 1a (core-20261115-150004-3629622): orders 1.991, 3.957, 5.918 as on the
  branch. Newtonian point mass (core-20261115-150209-3629622; the first attempt
  core-20261115-150002-3629622 failed in my driver, input not copied): rms force error
  1.609e-2 and 4.94e-3 at N = 32, 64, order 1.70, as on the branch. Bowen-York reference
  (check_bowen_york.py) and the id derivation (check_derivation.py) pass when rerun
  (pure Python, no run id). Not rerun: id test 0 reader, mp static series.
- P5: first criterion FAILED (single-precision dumps, entry above); with the revised
  criterion it HOLDS on processors (core-20261115-150404-9377fe8) and on the card
  (core-20261115-150426-9377fe8): no point of any K_ij component above the float32
  rounding bound (largest ratio 0.998), while K(comb) - K(A) = K(B) up to 5.9.
  Figure `fig_cf_combined.png` in the run directory looked at.
- The rng helper's pending card job 4414 had run (5 runs, core-20261115-135211..135312-
  a6e5c46): table equal to the twin, demonstrations D1 and D2 pass on the card, card
  regression c1, c2 identical, c3-c5 no verdict. Its five manifests, 25 manifests of the
  scalar package and 9 of the id package, left untracked in the helpers' worktrees, are
  copied into tracks/core/runs/ and committed with git add -f (harness/RULES.md).
- id package, the nine card runs that finished after its session: test2_evolution.py
  (core-20261115-145804-3629622) ran for t2 and crashed for t3 (zero-size array of the
  unstable fixed-gauge bound ball); details in JOURNAL-id.md, lead entry.
Card time of this session: 0.10 card-hours (jobs 4429, 4430, 4431).

### Check of the work packages from their artefacts (step 1 of the lead's task)
- doc: CONFIRMED at the paper source the corrections I sampled (L945 "<~ 10^-3", L641
  first-order deposit, L680-682 filter without a pass count, L1340 64.15625 M and L1360
  64.175 M, L926 Staley, L836 independent integration, L1393 no cosmology). NOT
  CONFIRMED: the D1 format read-back (not rerun; figures d1_*.png not opened by me).
  WRONG: nothing found.
- verify: CONFIRMED by rerun on the merged executables (G, O, F, L; above); paper
  locators L917, L1138, L1199, L971 checked. Small defect fixed: `options_at.py` gave
  empty results when run from its own directory as its README says (ls-tree paths are
  relative to the cwd); now `--full-tree`. NOT CONFIRMED: the prolate and cluster rows
  (re-read of earlier files only). Observation: the dust-collapse figure shows one
  lapse point at t = 25 M off by 1e-5 (OPEN.md item 17).
- rng: CONFIRMED twin = numpy Philox on 3000 new keys (my own mapping) and the kick
  demonstration D1 on the merged build with checksums equal to the branch build; the
  pending card job 4414 had run and passed. NOT CONFIRMED: the 253 statistical tests,
  the card cost numbers. Figures fig_kick_demo, fig_rng_pvalues looked at (card p-values
  run a little below the diagonal at mid quantiles, within the KS band of 58 tests).
- coll: CONFIRMED replay (7/7 on the merged build, same numbers). Figures of the
  relaxation and of the Kn = 3 cluster looked at; the cumulative energy gain in the
  figure (1.25e-5 and 0.55e-5 for f = 2, 1 at Kn = 3) agrees with the per-collision gains
  of the report times about 5200 collisions. NOT CONFIRMED: rate, conservation,
  reproducibility runs (not rerun).
- scalar: CONFIRMED test 1a orders on the merged build. NOT CONFIRMED: tests 2-6 (not
  rerun). Fixed: its 25 manifests were never committed on its branch (now added).
- id: CONFIRMED format-1 regression and the combined curvature (P2, P5), derivation
  script passes. The nine queued card runs had finished; analysis partly done (lead
  entry in JOURNAL-id.md). Defect: the t3 analysis crashes on a run without particles.
- mp: CONFIRMED reference module (check_bowen_york.py passes) and the semantic merge
  hazard it named (fixed, P5). NOT CONFIRMED: evolved runs (used executable 7a60df2).
  Observation not discussed by the package: the light horizons drift by 1.3 to 1.5
  percent in 16 M (OPEN.md item 10).
- newton: CONFIRMED point-mass field on the merged build (same numbers). Observation:
  the potential at the probes converges by 1.5 only from N = 64 to 128 in the package's
  figure field_point.png (not discussed). NOT CONFIRMED: collapse, wave, restart (not
  rerun).
- Written by the lead: tracks/core/CHANGELOG.md (core-v0.3 = 609a875), stage/G2/
  EVIDENCE.md, OPEN.md, CHECKLIST.md (filled), STAGE_REPORT.md (nrpic-stage report).
  The write of stage/G2/REPORT.md was refused by this session's write guard for
  subagents; its content is distributed over these files and this entry.
- Changed my mind about: card regressions. I planned byte comparison on the card for
  every case; with deposit only a comparison at the start, or against the baseline's own
  scatter, is meaningful (scripts/README.md corrected).
- P2, completion (15:12Z): the processor comparison of cf_table_regress inside
  core-20261115-145448-3629622 ended IDENTICAL (9 files, never-set restart bytes masked);
  that run exits 1 because its P5 part used the first, faulty set-up (entry above). P2
  HOLDS on processors and on the card.

## 2026-11-20T22:10Z  session core-lead (wave 3: merge of the seven wave-2 branches, release candidate core-v0.4)

State found: worktree clean at d377d12d, main merged (ff1591bd). No `RELEASE-v0.4.md`,
no `scratch/core/exe/core_nrpic_v04/`: nothing of this step existed. No pause flag.

### Review of the seven branches as maintainer (git diff main...<branch> -- athenak/src python problems scripts docs)

Tips taken: core/requests-b f134b775, core/gauge 58d10777, core/scalar-2 207424d2,
core/clump-curvature 56d7335c, core/id-solver d88ff4f9, core/requests-adf b6041dbc,
core/collisions-2 8c03bc96 (the last two still write records; `athenak/src` of every
branch is unchanged since the commit of its published executables [VERIFIED: `git diff
<COMMIT of READY> <tip> -- athenak/src` empty; clump-curvature two comment lines]).

- requests-b: PASS. New parameters read with DoesParameterExist (parameter dump of old
  inputs unchanged). Two changes act without an option: (i) the 36 never-set bytes of
  `Mesh::mesh_indcs` are zero (restart files change in these bytes, G2 OPEN item 15);
  (ii) the sign of axy, ayz in `z4c_linear_wave.cpp` (upstream tensor was transverse only
  for k2 = 0 or k along an axis) and the error routine compares at the final time: an
  existing oblique linear-wave input with k2 != 0 changes. Both are documented
  corrections (docs/UPSTREAM_DEFECTS.md).
- gauge: PASS. Everything in `z4c_gauge_ext.hpp`, a loop of its own after the main
  right-hand-side loop; three hook lines.
- scalar-2: PASS. Two new files; hooks guarded by options. With all three kicks off the
  stage no longer synthesizes noise fields (nothing reads them; dumps call
  NoiseFieldsOfState themselves).
- clump-curvature: PASS. One new header, additions in nrpic_cf.cpp; a Gaussian with
  p/s keys was a fatal error before.
- id-solver: PASS. New boundary kind `mg_robin`, `SolvePoisson`; everything behind
  `<particles> id_solve`.
- requests-adf: PASS with three corrections that act without an option, to be listed in
  the changelog as behaviour changes: (1) m = 0 particles on the mesh metric are tracers
  on timelike geodesics (releases v0.2, v0.3: null); `zero_mass = null` gives the old
  rule; light rays (m = -t_e, at least -1e-30 in cosmo/ic/ray_ic.py line 11) are not
  affected [VERIFIED by reading]; (2) `Driver::Finalize` no longer advances `last_time`
  for an output written off its schedule, so the parameter dump embedded in such final
  files changes in `last_time` lines; (3) analytic metrics honour `alpha_exc` (default
  -1: off) and remove flagged particles. NRPIC_NIDATA grows from 3 to 4 (PPERI); the
  restart format keeps three integers per particle.
- collisions-2: PASS. `coll_energy` absent leaves the cell kernel arithmetic as it was;
  known from the package (JOURNAL-coll2.md, outcome D, run core-20261119-141059-f3ccf56):
  on a card collisional runs with the options absent differ from release v0.3 at rounding
  (momenta 2e-14), same pairs; processors byte-identical.

Merge order (small conflicts): requests-b, gauge (both z4c.cpp/hpp), scalar-2,
clump-curvature, id-solver, requests-adf, collisions-2 (the last three share
nrpic.cpp, particles.hpp, CMakeLists.txt, docs/FORMATS.md).

### Predictions, written before the merge is built or run

R  Byte regression on processors, merged executable against release core-v0.3
   (`.work/build_cpu_v03/src/athena` of the main checkout), twelve set-ups of wave 1
   (geo, boris, dep, east, os, jeans, binary of `tools/regress_relativistic.py`; c1-c5
   of `analysis/rng/run_regression.py`), same arguments, new options absent. Predicted:
   every output file identical except two classes, both intended corrections:
   (a) restart files: the 36 never-set bytes of the mesh header (now zero);
   (b) files that embed the parameter dump (restart, bin) and are written by
       `Driver::Finalize` when the run stops off the schedule of an output: lines
       `last_time = ...` of that dump only.
   Refuted by any other differing byte: a data value, a history line, a snapshot, a
   parameter line other than `last_time`, a missing or extra file. Then the branch that
   causes it is found by bisection over the merge commits and left out.
Q  Quick test of every merged branch on processors: the example its READY names, run
   with the merged executable and with the branch's published `athena_cpu`, gives the
   same bytes (same exceptions (a), (b), which the branch executables do not all have).
   Refuted by a differing data byte: two branches would then interact in one kernel
   (the push kernel of nrpic.cpp is shared by requests-adf and collisions-2; gauge's
   journal entry 3 records that a term inside a kernel moved last digits of unrelated
   runs). Each example must also show the physical number its READY states (same
   executable source, so this is a check of my driver, not a new test).
C  Card executable: the examples run to their end on one A100 (exit 0) and agree with
   the processor runs to rounding where no deposit sum is involved (lw_oblique error
   norms to 1e-12 relative, id-solve iteration counts equal); with deposit, agreement
   to 1e-10 at the start. Refuted by a crash or a difference above these bounds.

### 22:08Z to 22:55Z, recorded on 2026-11-21 by the session that continued (the first one was cut at 22:34Z by the usage limit)

Merges made by the first session, one commit per branch, in the order planned: 3ab47062
(requests-b), 120aa7cf (gauge), 54dc527e (scalar-2), e2498da4 (clump-curvature), de42b294
(id-solver), 7b0fcf27 (requests-adf), f9323185 (collisions-2, 2026-11-20 22:05:31Z).
Builds, both from scratch after the last merge [VERIFIED: build logs, 221 and 225
compiled objects, configure lines of a new directory]: processors
`.work/build_cpu_v04rc` 22:05Z to 22:08:31Z (156 s), card `.work/build_gpu_v04rc`
22:16:11Z to 22:35:00Z (1129 s). The tree was clean at those times (`git.dirty = false`
in the manifests registered at 22:08:49Z, 22:16:07Z and 22:27:24Z) and `git diff f9323185
HEAD -- athenak python problems scripts` is empty today.

Outcome of R (run core-20261120-221607-4985804, 3 cores, 398 s; the first attempt
core-20261120-220849-cea5881 ended FAIL through the driver's own rule: the case binary
writes no file and had "nothing compared"; rule corrected in 49858043, same runs):
PREDICTION HELD. 12 set-ups, 73 output files and 2 sets of log result lines compared:
60 files identical, 8 of class a (the five restart files of os, the three of c5: 36
non-zero unset bytes in the release, 0 in the candidate), 5 of class b (jeans
`bin/JeansWave.hydro_w.00001.bin`: `<output2> last_time` 0.1 against 0; c3: four final
bin files, `last_time` 200 or 50 against 0), none of class a+b, none other. Every data
byte, history line and snapshot equal. sha256 of the candidate processor executable
8bff3107...d506, of the release d983155b...c25c.

Outcome of Q, first attempt (run core-20261120-222724-75e323c, 1 core, 1663 s, exit 1):
the driver printed QUICK TESTS FAIL for one item, `clump/particles.json`, class other
("2240 and 2237 bytes"). That file is not written by AthenaK: `problems/ic/make_ic.py`
writes it during the preparation of the run directory and records the output directory
in it (`.../clump/branch` against `.../clump/new`: 3 characters, the only differing
line; `diff` of the two files, checked today). Everything AthenaK wrote is of class
identical or b: lw16 3 identical + 1 b, leak 7, eta 7 + 1 b, sr 4, clump 5, ids 8,
tracer 3, pert 2, coll 4; all 13 numbers inside their bands. So Q held in substance and
the verdict line is a defect of my driver (it compared a preparation product). The run
stays on record as failed; the driver is corrected (preparation products are listed
before AthenaK starts and reported separately) and the test is run again.

## 2026-11-21T02:58Z  session core-lead-2 (wave 3, evening batch: release candidate core-v0.4, continued)

State found: branch at e22fd12c (pushed), one untracked file of the first session
(`analysis/release/fig_regress_v04.py`, complete, never run), run
core-20261120-222724-75e323c registered and not closed. No `RELEASE-v0.4.md`, no
`scratch/core/exe/core_nrpic_v04/`. No pause flag. main merged (0d35ba93; no source in it).
Late commits on two merged branches, records only [VERIFIED: `git diff --stat
HEAD...origin/core/<b>`]: requests-adf bc38aafc (READY text, card judgement figure,
REQUESTS_ADF.md, diagnostics.md, multi_puncture.md), collisions-2 6801bffb and 4c798e7a
(collisions.md, docs/COLLISIONS.md, journal, one outbox message). I merge them now: they
are the closed records of the two packages and the interface texts the release copies.
The card queue holds one job of core (4755), so one job of mine may be queued.

### Predictions, written before the runs

Q2 Quick tests again with the corrected driver, same executable (sha256 8bff3107...),
   4 cores. Predicted: every file AthenaK writes has the bytes of the first attempt
   (processor runs are reproducible), so 43 files identical and 2 of class b against
   the branch executables, none other; the 13 numbers the same in all printed digits;
   among the preparation products only `clump/particles.json` differs between the two
   directories. Refuted by any file of class other, a number outside its band, or a
   number that differs from the first attempt.
C  (first session, above) stays as written. What I add before the card job, with my
   own expectation where it differs:
   C1 every case of the list ends with status 0 on one A100;
   C2 the 13 numbers of the quick test, computed from the card runs, lie inside the same
      bands; exception I expect: `sr_H_ratio_start` (2.6e-12, a rounding residual of the
      slice) may leave [2e-12, 3.2e-12] on a card only if the slice differs, and the
      READY of scalar-2 says the slice is bit-identical on a card, so I predict inside;
   C3 ids: 17 outer iterations as on processors; coll: 141140 collisions and no pair
      without a root, as on processors (the READY of collisions-2: no acceptance flips);
   C4 against the processor runs of the same inputs: tracer |r_card - r_cpu| <= 1e-9 M
      over 300 M; clump M-norm2 and H-norm2 at t = 0 within 1e-10 relative; leak
      alpha_max within 1e-10 relative at every record; pert snapshots within 1e-12;
   C5 lw: I expect the first session's bound "error norms to 1e-12 relative" to FAIL as
      written: the error norm (5.3e-11 at 16 cells, 5.9e-12 at 32) is a difference of
      fields of order one, so card rounding of 1e-16 to 1e-15 in the fields is 1e-5 to
      1e-3 of it (the READY of requests-b has 7.561685e-11 against 7.561707e-11 for the
      circular wave, 2.9e-6 relative). My bound: |RMS-L1(card) - RMS-L1(cpu)| <= 1e-14
      absolute at both resolutions, order from 16 to 32 cells inside [3, 13].
   Refuted by a crash, a number outside its band, a differing count in C3, or a
   difference above the bounds of C4 and C5.

Correction of Q2 before the run (02:59Z): the counts "43 identical" above, and the
per-test counts of the first attempt, include five preparation products that were equal
(leak `particles.nrp`, clump `particles.nrp`, ids `gauss_h0p5.nrp` and `.json`, coll
`box.nrp`). Of the files AthenaK writes the first attempt has 38 identical and 2 of
class b; that is what Q2 predicts, with 6 preparation products reported separately, one
of them differing (`clump/particles.json`).
Card list `analysis/release/card_v04.list`: the eleven cases of the quick test with the
particle files that run core-20261120-222724-75e323c prepared (checksummed as inputs).

### Outcomes (2026-11-21)

Q2 (run core-20261121-025955-bd47414, 4 cores, 537 s, exit 0, QUICK TESTS PASS):
PREDICTION HELD. Of the files AthenaK writes, 38 identical and 2 of class b against the
branch executables (lw16 `bin/lwo.z4c.00001.bin`: `<output2> last_time` 1000 against 0;
eta `bin/bye.con_H.00001.bin`: `<output3> last_time` 10 against 0: the branch
executables of requests-b and gauge do not have the Finalize correction of
requests-adf), none other. Six preparation products, one differing
(`clump/particles.json`, the directory name). The 13 numbers equal those of the first
attempt bit for bit, and every file the merged executable wrote equals its file of the
first attempt (56 files compared; `particles.json` of clump and clump0 aside). So the
merged executable gives, for the example of each branch, the bytes of that branch.
Figure `fig_quick_v04.png` looked at. What it shows beyond the bands: the oblique-wave
error falls by 2^3.17 from 16 to 32 cells, not 2^6: at 32 cells it sits a factor 7 above
the sixth-order guide. The package found a part of second order in the amplitude that
does not fall with resolution after one period (READY of requests-b, test T8), which
would give this [JUDGEMENT: not tested here]; the band [3, 13] of my quick test is
therefore a weak check of the order and no more than "the generator and the error file
work". Layout defects of the figure (axis labels over tick labels and over the next
panel, one title cut) corrected in the driver; the figure is remade from the same runs
(`--analyse-only --runs`).
Regression figure: run core-20261121-030235-cc329f5 (supersedes -030223-bd2eddc, whose
legend covered a bar), looked at: 75 compared items, 62 identical, 8 a, 5 b, no other.
Option scan `verify/options_at.py core-v0.3 HEAD`: 61 added, 0 removed, 0 changed
defaults (`scratch/core/tmp/lead_v04/options_v03_v04.json`).

### Publication and records (2026-11-21T03:10Z to 03:15Z)

- Published `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`: `athena_cpu`
  (sha256 8bff3107...8955d506, the executable of R and Q2), `athena_gpu` (sha256
  ab3ee2a6...4143623b, the executable the card job holds as `batch.list.exe`), `COMMIT`
  (source f9323185), `SHA256SUMS` (checked), `READY` (19 new options or groups, one
  example input each, all 25 example inputs exist in the tree [VERIFIED: test -f]),
  `branches/READY.<branch>`.
- Written: `RELEASE-v0.4.md` (REGRESSION PASS), `CHANGELOG.md` section core-v0.4,
  `stage/G2/OPEN.md` first section (no branch left out; items 6, 7, 9, 15 changed by the
  release; defects a to i), `stage/G2/EVIDENCE.md` section of the candidate, STATUS,
  HANDOFF.
- Review of the first session's merge resolutions by reading (`git show --cc`): hand
  resolutions in z4c.cpp/hpp, CMakeLists.txt, nrpic.cpp, nrpic_io.cpp, particles.hpp,
  docs/FORMATS.md, rng.md are unions of both sides; in `NrpicPush` the order is
  perturbing kick, test kick, accretion bracket. Q2 is the test that each side kept its
  behaviour.
- Not changed: the comment of `NrpicCollideOptions::ext` (columns 32 to 35, should be
  36). A source edit after the tests would make the published executables differ from
  the source commit; it is OPEN.md item f.
- Changed my mind about: the times in my headings (I wrote estimates 03:00Z and 03:12Z
  where the clock said 02:58Z and 02:59Z; corrected from `git log`), and the count of
  Q2 (corrected before the run).
- Card check: job 4758 queued at 02:59Z behind 4755 (core), 4756 (C), 4757 (E); both
  cards busy until about 03:27Z and 03:36Z (squeue at 03:12Z). Its outcome is recorded
  below when it has run; until then RELEASE-v0.4.md and READY say PENDING.

### Prediction S, written before the run (2026-11-21T03:16Z; processor work while job 4758 waits)

The quick test runs nine example inputs; the READY I published names others that no
run of the merged executable has started. S: six of them on processors, merged
executable against the executable of the branch (driver `analysis/release/more_v04.py`):
boost (`idsolve/gaussian_boost.athinput`, 32 cells: id_vector), spin
(`clump/clump_spin.athinput`: comp0_s3, initial data), pairh
(`tests/pair_horizon.athinput`: pair surface, two steps), uneq
(`puncture/by_unequal.athinput`, one step: shift_eta_profile on a pair), acc
(`tests/accretion_static.athinput`, 400 steps: removal record, flux spheres, pericentre
counter), kepler (`tests/newton_point_mass.athinput`, 100 steps: newton_pm_mass).
Predicted: all twelve runs end with status 0 and every file AthenaK writes is identical
or differs in class a or b only. Refuted by a file of class other, or by a non-zero
status of the merged executable where the branch executable ends with 0. If both end
non-zero for a case, my arguments are at fault and the case says nothing about the
merge. Not covered by any run of the merged executable even then: waveform_at_new_time,
lapse_leak on a ball, the restart schedule after a stop, the periodic Newtonian box.

Outcome of S (run core-20261121-031604-dccccbb, 4 cores, 285 s, exit 0, MORE EXAMPLES
PASS): PREDICTION HELD. All twelve runs status 0. 42 files AthenaK wrote: 40 identical,
2 of class a (`rst/acc.0000{0,1}.rst`: 36 non-zero unset bytes with the executable of
requests-adf, none with the merged one), none of class b, none other. Per case (files):
boost 7, spin 4, pairh 8, uneq 9, acc 8 (6 + 2 a), kepler 6. Preparation products equal
in both directories except `spin/particles.json` (directory name). Wall times of merged
and branch executable within 3 per cent of each other except acc (3.6 against 4.0 s).
Figure `scratch/core/core-20261121-032134-8dd42e4/fig_more_v04.png` looked at (third
drawing: the first had its legend over the exit labels, the second a cut axis label).
With Q2: fifteen example inputs of the READY give, with the merged executable, the
bytes of the branch that wrote them. Still started by no run of the merged executable:
`waveform_at_new_time`, `lapse_leak` on a ball (`ball_leak`, `es_gauge`), the restart
after a stop (`restart_schedule`), the periodic Newtonian box, `clump_puncture`,
`jeans_mc`, the id-solver ball and torus, `accretion_tracker`.

Outcome of C (card run core-20261121-025945-54dc669, Slurm job 4758, one A100, 34 s =
0.0094 card-hours, started 03:27:57Z; judged by run core-20261121-033000-f1c0f5d, which
supersedes core-20261121-032851-5f911b8: same data and checks, labels of the figure):
CARD CHECK PASS.
- C1 held: all eleven cases status 0.
- C2 held: the thirteen numbers inside their bands on the card. `sr_H_ratio_start`
  2.6247552e-12 against 2.62475534e-12 on processors (5.4e-8 relative): inside, as
  predicted.
- C3 held: 17 outer iterations on both, conjugate-gradient steps and V cycles equal in
  every iteration; collisions equal in each of the 20 steps (141140), no pair without a
  root on either, 848 rejected on both.
- C4: tracer |r_card - r_cpu| at most 2.4e-13 M over 300 M (bound 1e-9; positions
  1.0e-12); lapse of the homogeneous universe within 2.6e-15 at all 65 records (bound
  1e-10); snapshots of the perturbing-force case bit-equal (bound 1e-12): held. Clump:
  `M-norm2` and `H-norm2` at t = 0 are equal in the six digits that file prints, which
  resolves 5e-6 and not my bound of 1e-10: that item, as I wrote it, is NOT TESTED by
  the file I named. The 21 columns of `clump.nrpic.hst` that do not vanish by symmetry
  (16 digits) agree to 5.0e-14 at t = 0 and 6.1e-11 after one step, so the first
  session's "with deposit, agreement to 1e-10 at the start" HELD on that file.
- C5 held: |RMS-L1(card) - RMS-L1(cpu)| = 9.0e-17 at 16 cells and 4.8e-16 at 32 cells
  (bound 1e-14); the order from 16 to 32 cells is 3.1677 on the card, 3.1676 on
  processors.
- The first session's bound "lw_oblique error norms to 1e-12 relative" FAILED as
  written: 1.7e-6 and 8.1e-5 relative. I expected this before the run (C5 above): the
  error norm is 5e-11 and 6e-12 on fields of order one, so rounding of 1e-16 in the
  fields is that fraction of it. Its other parts held (status 0, iteration counts).
- Reported, not judged (figure, middle panel): the largest difference of a history
  column over the column maximum. Over the columns above 1e-10 it is below 1e-10 in
  twelve of eighteen files; larger in `leak/flrwleak.cstat.hst` (Mr_mean 0.45, Mr_max
  0.2: |M|/[M] where both are at rounding in a homogeneous universe, M_max 2.7e-14),
  `leak/flrwleak.z4c.user.hst` (1.5e-6: one unit of the last of six printed digits of
  H-norm2), `sr` (max|H| and max |M|/[M]: 1e-3 to 2e-3 relative, 1.9e-13 and 8.7e-8
  absolute), `ids/gauss.cstat.hst` (Hr_max 2.4e-5), and the constraint norms of the
  linear wave (1e-21, differing at 1e-2). [JUDGEMENT] each is a quantity at rounding
  level or at the tolerance of a solve; none was tested further.
Figure `scratch/core/core-20261121-033000-f1c0f5d/fig_card_v04.png` looked at. Card time
of this package: 0.0094 card-hours of the one allowed.

## 2026-11-21T06:32Z  session core-lead-3 (batch 2a: merge of four wave-3a branches, release candidate core-v0.5)

State found [VERIFIED by the commands named]: `git merge --no-edit main` was a fast
forward to 66254fe4 (main carries release core-v0.4 and its tag); worktree clean; no
pause flag; no `RELEASE-v0.5.md`, no `scratch/core/exe/core_nrpic_v05/`. `squeue`: no
job of core queued or running (4769 of F runs, 4770 of C waits). Tips to merge (local =
origin): core/build-openmp 983351aa (source a9c34e7a), core/scalar-3 88544a5b (source
5cc28211), core/cosmo-amr bb360ef2 (source 1548d49c, the corrected fine-shape deposit),
core/mpi f9a2c022 (source ca46836a; since then only example inputs under
`problems/tests/`). Slurm job 4763 of package cosmo-amr (T14b, T10g) ended COMPLETED
after 9 min 55 s (`sacct -j 4763`); it is not judged by its package yet. Of package mpi
two finished runs are unjudged in its worktree: the one-rank flow-perturbation run
core-20261120-223502-f9a2c02 (manifest untracked there) and the two-card job 4733
(COMPLETED, 78 s). I do not write into those worktrees.

Review of the four diffs against main (`git diff main...<branch> -- athenak/src python
problems scripts docs`), overlaps found before merging [VERIFIED by reading the diffs]:
- build-openmp replaces the two `Kokkos::atomic_add` of the deposit kernel by
  `dep.Add` and brackets the particle loop by `thread_dep.Begin/End`; with
  `deposit_threads = private` the source array is OVERWRITTEN in `End` by the sum of
  the per-thread copies.
- cosmo-amr adds a third addition into the source array (branch `deposit_fine_shape`)
  with `Kokkos::atomic_add`: in the merged kernel it must become `dep.Add`, or the
  private mode would lose those shares.
- mpi adds `NrpicMpiDepositRemote()` after the particle loop (packets of clouds that
  reach other ranks, added with atomic additions through `nrpic_cloud.hpp`, a second
  copy of the leaf-cell loop): it must come AFTER `thread_dep.End`, and its copy of the
  kernel has no fine-shape branch, so `deposit_fine_shape` on several ranks would give
  the uniform spreading for the remote part of a cloud and the fine shape for the local
  part. Resolution planned: stop with a message on more than one rank for
  `deposit_fine_shape`, as mpi does for the options it has not ported; the same stop for
  the options of release core-v0.4 that write files or change particles outside the
  ported functions (to be listed from the merged source), and for the files of
  cosmo-amr written per rank.
- scalar-3 touches the scalar field and `utils/rng_mesh.hpp` only; it contains the
  commits of scalar-2, which release core-v0.4 has.

### Predictions, written before any merged executable exists

M  Order scalar-3, build-openmp, cosmo-amr, mpi (one merge commit each). Conflicts
   expected in `nrpic.cpp` (deposit kernel: omp against cosmo-amr against mpi),
   `particles.hpp`, `CMakeLists.txt`, `tracks/core/interfaces/rng.md` (scalar-3 against
   the stream registry of release core-v0.4) and the shared records (`STATUS.md`,
   `HANDOFF.md`). All four build as serial processor, card, threaded (omp) and MPI
   processor executables.
R  Byte regression of the serial processor executable against release core-v0.4
   (`/data/haiyangw/nrpic/.work/build_cpu_v04/src/athena`), the twelve set-ups of
   `regress_v04.py`, new options absent: all 75 items identical; classes a and b empty
   (release core-v0.4 has both corrections). Refuted by one differing file. Where I
   think it could fail: cosmo-amr changes code that runs without an option (the
   horizon finder and tracker for periodic meshes, the step limit in `z4c_newdt.cpp`,
   `nrpic_cosmo.cpp` setting the refinement function, the guard call in the driver);
   its own regression (T0c) was against core-v0.3 on seven set-ups.
R2 The MPI processor build started without mpirun and the threaded build at one thread:
   the same 75 items identical to release core-v0.4. (Against core-v0.3 the MPI build
   differed in 36 unset header bytes of the mesh restart files; core-v0.4 zeroes them,
   so I predict no difference now.) The threaded build at one thread: READY of
   build-openmp says its serial executable reproduces the release and the threaded one
   at one thread equals the atomic result; for gas with multigrid (jeans, binary) the
   iterates may differ between the Serial and the OpenMP back end even at one thread
   [JUDGEMENT: the plain sum in `Multigrid::CalculateAverage` is a reduction whose
   order the back end chooses]; I predict identical for the ten set-ups without
   multigrid and make no prediction for jeans and binary.
Q  One example per merged branch, merged serial executable against the branch's
   published processor executable, byte for byte (branches lack the two corrections of
   core-v0.4, so classes a and b may appear in restart files and final dumps):
   Q-s3  `problems/scalar/sr_stochastic_gauge.athinput` (con_signed), 12 steps:
         identical. And `usr_stochastic.athinput`, 12 steps: identical.
   Q-amr `problems/cosmo_amr/flrw_tracker.athinput` and `peak_amr.athinput` (short):
         identical to `core_cosmo-amr/athena_cpu` (source 1548d49).
   Q-omp `problems/tests/deposit_threads.athinput` with the threaded build: two runs at
         4 threads with `private` byte-identical; 1 against 4 threads within 1.3e-12 of
         the largest number of a file (READY section 3); the serial executable prints
         the note and gives the files of the deck without the option.
   Q-mpi `mpi_kerr_swarm.athinput` on 1 and 2 ranks: particle files byte-identical;
         `mpi_cluster.athinput` on 1 and 2 ranks: positions within 1e-13, history
         within 1e-11 (READY T3: 4e-15 and 5e-13 after 40 cycles), deposit identity
         1e-14. One rank of the MPI build against the serial executable: identical.
   New in the merged source and tested by no branch: `deposit_threads = private` with
   the fine-shape branch (threaded build, `peak_amr` or the refined deposit test with
   `deposit_fine_shape`): 1 against 4 threads within 1e-12 of the largest number, and
   sums conserved to 1e-13. Refuted by a difference of order of a cloud share (then
   an addition bypasses the private copies).
   Refuted in general by a file of class other, or a number outside the bound named.
C  Card (at most one card-hour; one job): the card executable runs one short example
   of each branch that deposits or evolves on a card (flrw_tracker, sr_stochastic_gauge,
   deposit_threads deck without private, one mpi example on one rank) with status 0 and
   within 1e-10 of the processor run in the conserved sums. If the queue does not give
   a card in time, the job is named as pending and the release says what did not run.

### Outcomes (2026-11-21)

M  [VERIFIED: `git log --first-parent`] Four merge commits: scalar-3 604e9ad8,
   build-openmp 0d0f5ba5, cosmo-amr e103b3e3, mpi c3eb42e0 (source commit of the
   candidate: the last one that changes `athenak/`). Conflicts as predicted in
   `rng.md` (rows 1, 2 and section 6.1 of core-v0.4 kept, row 3 of scalar-3 taken, its
   table became section 6.2), `particles.hpp` (three times), `CMakeLists.txt`,
   `nrpic.cpp` (cosmo-amr and mpi); NOT in `STATUS.md` or `HANDOFF.md` (the branches
   did not touch them), and build-openmp merged `nrpic.cpp` without a conflict (I had
   expected one). Three resolutions that no conflict marker asked for, each in its
   merge commit: the additions of the fine-shape branch go through `dep.Add`;
   `thread_dep.End` comes before `NrpicMpiDepositRemote`; `NrpicMpiInit` stops a run
   on several ranks for `removal_record`, `acc_nsphere`, `peri_count`, `perturb_gamma`,
   `id_solve`, `region_dcycle`, `deposit_fine_shape`.
   Found by reading the cosmo-amr diff, three things act without an option: the guard
   (`<z4c_guard> stop_nonfinite`, default true) stops a Z4c run whose fields are not
   finite, exit status 3; `nrpic_cosmo` enrols a refinement function; the summary file
   of the horizon finder and the tracker file are opened at the first record, i.e. in
   the run directory of `-d` and no longer in the directory the executable was started
   in [VERIFIED: `main.cpp` 359 to 386, `AddCoordinatesAndPhysics` before
   `ChangeRunDir`]. The release drivers start AthenaK inside the run directory, so they
   cannot see the third.
   Serial processor build `.work/build_cpu_v05rc` from the clean tree at c3eb42e0:
   156 s on six jobs, no error (sha256 b462068a...).
R  HELD. Run core-20261121-063859-e410ee3 (6 cores, 283 s): the serial candidate against
   release core-v0.4 (`.work/build_cpu_v04`, sha256 daada48f...), twelve set-ups, 75
   items, all identical; classes a, b, other empty; every run status 0.
T14b of package cosmo-amr (card job 4763, finished, not judged by its package): judged
   here with the package's script, read-only on its outputs, run
   core-20261121-063923-5ed0a51. Against the prediction of its journal (entry 03:26):
   homogeneous cases uniform to 2.2e-14 (U, S, A) and 1.1e-13 (M) in E on the card
   (bound 1e-12); alpha_max equal to the processor runs to 1.8e-15 (bound 1e-12);
   M: MeshBlock counts equal at every record, tracker within 4.4e-16; ladder: 64 to 120
   MeshBlocks at cycle 5 on both, 32768 particles and the rest mass unchanged, identity
   2.2e-16 (bound 1e-13), Hr_max within 9.2e-12 of the processor value (bound 1e-9);
   G: status 3 with its file, stop at cycle 16 against 18 on processors (not
   predicted; the script prints FAIL for the cycle, as in T14). HELD. Sf is not judged
   by the script. Figure `fig_t14_card.png` of that run looked at (three panels: lapse
   ratio at 1e-16 to 1e-15, the unstable run departing from record 9 on, MeshBlock
   counts on one line). So the card executable of source 1548d49 (the deposit of the
   candidate) has run on a card with the processor result. T10g of the same job (the
   scouting run for Track A) ended with the guard at t = 12.504, cycle 1101, "conformal
   factor chi not positive" (`s1g/peak.guard.txt`); its judgement against the
   prediction of entry 03:33 is the package's and Track A's, not done here.
Read, not judged: run core-20261120-223502-f9a2c02 of package mpi (its `run.log`): on
   ONE rank a change of the finder's flow constant by 1e-13 changes the search of
   t = 0.1875 by 4.8e-3 in the smallest radius and the removed particles from 43 to 41,
   while the three searches before agree to 1.9e-10 or better. This is the outcome its
   entry 28 (P7g) asked for; the entry is the package's to write.
