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

### Quick tests (2026-11-21T06:50Z to 06:58Z)

Builds from the clean tree at c3eb42e0, each in a new directory: threaded
`.work/build_omp_v05rc` (`scripts/build_cpu_omp.sh`, 360 s on three jobs, sha256
4d327a4d...), MPI `.work/build_cpu_mpi_v05rc` (`CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON"
scripts/build_cpu.sh`, Open MPI of `/home/emost/codes/openmpi`, 306 s, sha256
003736e1...). Correction of the entry above: the regression R took 265 s (manifest),
not 283.

Run core-20261121-065009-29b855c (driver `analysis/release/quick_v05.py`, 6 cores, 31
AthenaK runs) ended **FAIL** through two checks; both are errors of my driver, found by
looking at what differs, and the runs were evaluated again without running anything in
core-20261121-065726-bf06a85 (**PASS**; figure `fig_quick_v05.png` looked at after a
first version with overlapping labels was redrawn):
- the driver compared the whole history of the fine-shape run with the plain run and
  asked for 1e-13: 1.65e-7 of the largest number. The columns that differ are E_probe,
  E_max and E_min (14, 31, 32), which the fine shape must change; the mesh integrals
  (columns 9 to 12) agree to 5.2e-14 of sum m W. The prediction ("sums conserved to
  1e-13") was right, the check was not what it said.
- prediction Q-mpi, clause "history within 1e-11", FAILED as I wrote it: the constraint
  statistics `cl.cstat.hst` differ by 8.5e-10 between 1 and 2 ranks (column 11, the
  largest relative Hamiltonian constraint), the history of the module by 4.6e-13. I had
  taken the READY's "history 5e-13" as a bound for every history file. The package's own
  run with its branch executable (core-20261119-154814-ca46836) has 8.502235846576052e-10
  and 4.636286737306016e-13: the same digits. The check now judges the history of the
  module and reports the statistics beside the package's value.
Outcomes against the predictions Q:
- Q-s3 HELD: `sr_stochastic_gauge` (con_signed, 27 columns) and `usr_stochastic`, 12
  steps: 6 and 6 files identical to the executable of core/scalar-3.
- Q-amr HELD: `flrw_tracker` (12 steps) and `peak_amr` as case ladder of T9 (10 steps,
  64 to 120 MeshBlocks, fine-shape deposit, region norms): 5 and 5 files identical to
  the executable of core/cosmo-amr (source 1548d49).
- Q-omp HELD: two runs at 4 threads with `private` byte-identical; 4 threads against 1:
  2.1e-18 (history), 1.2e-16 (source dump in double precision); atomic at 4 threads the
  same; the serial executable prints "this executable adds atomically" and gives the
  bytes of the deck without the option, and the bytes of `athena_cpu_serial` of
  core/build-openmp. Deposit identity 5.5e-14 at worst.
  Not predicted, measured: the threaded build at ONE thread against the serial build:
  history 4.2e-22, source dump 1.1e-14 of the largest number, i.e. not the same bits
  (the two builds differ in optimisation level, -O3 -DNDEBUG against -O2).
- New combination HELD: fine-shape deposit through the per-thread copies: two runs at 4
  threads byte-identical; 4 threads against 1: 1.1e-18 (history), 2.1e-16 (dump);
  atomic at 4 threads 3.6e-16; 1 thread against the serial build 1.1e-14; tsc with
  fine shape 7.5e-15; identity 3.0e-14 at worst; the fine shape changes the dump by
  0.52 of its largest value against the plain cic deposit (so the branch is taken) and
  the integrals by 5.2e-14.
- Q-mpi: Kerr swarm on 1 and 2 ranks: 9 particle files identical (trajectories, metric
  at the particles, five snapshots, two particle restart files), 2119 particles handed
  over. Cluster on 1 and 2 ranks: positions 3.1e-15 (bound 1e-13), history of the
  module 4.6e-13 (bound 1e-11), identity 7.8e-15 and 1.7e-15 (bound 1e-14), 2786
  particles handed over and 53923 deposit packets. HELD except the clause above.
  Added after the run: every file of these four runs against the package's runs with
  its branch executable (core-20261119-145615-4c98c59, core-20261119-154814-ca46836):
  10 of 12, 11 of 13, 20 of 24 and 21 of 25 files identical; the others are the mesh
  restart files, whose data are identical outside the 36 header bytes that core-v0.4
  zeroes and whose parameter dump holds the run directory and four lines of the
  example inputs that the package edited after those runs (`deposit_comp_c`,
  `filter_compensate`, `source_density`, `source_extrap`).
- The stop added at the merge: `mpi_deposit_smr` with `deposit_fine_shape` on 2 ranks
  ends with status 1 and "<particles> deposit_fine_shape (the part of a cloud on another
  rank has no fine shape) has not been ported to more than one MPI rank"; on one rank
  of the same executable the deck runs (status 0).

### Prediction of the card check, written before the card executable exists

List `analysis/release/card_v05.list` (nine cases, decks of the quick run), judged by
`card_v05.py`: K1 every case status 0; K2 particle sums and mesh integrals (columns 4
to 12 of the history of the module) within 1e-10 of sum m W of the processor run; K3
deposit identity on the card within 1e-13; K4 MeshBlock counts of trk and peak equal
at every record, tracker path within 1e-12; K5 source dumps of the four deposit cases
within 1e-12 of the largest number; K6 the card prints the note of `deposit_threads`.
Refuted by a status other than 0 or a number above its bound. Where I am least sure:
peak (the lapse ladder decides refinement by a threshold; a rounding difference could
move a regrid by one check, though T14b of the package saw none), and cluster (40
cycles of a self-gravitating cluster: the package measured 5.4e-13 between two
one-card runs of its build).

### Regressions of the MPI and the threaded build (2026-11-21T07:16Z)

- R2, MPI build started without mpirun: HELD. Run core-20261121-065743-1202666: 75
  items identical to release core-v0.4, nothing of class a, b or other.
- R2, threaded build at one thread: FAILED. Run core-20261121-070623-077b056
  (`regress_v04.py` ends FAIL by its rule): 31 of 75 items identical (geo both files,
  jeans all five, single files elsewhere), 44 differ. The differences are at rounding
  level [VERIFIED by reading the histories of both runs with `card_v05.hst_columns`]:
  every column of the module's histories above rounding agrees to 1.2e-15 (east 1.1e-15,
  c4 1.2e-15, zero in the others), the constraint statistics to 1.4e-10 (east, column
  9, H_max) and 1.9e-12 (c4, column 15); binary: the result lines of the multigrid log
  differ. All 24 runs status 0. I had predicted identity for the ten set-ups without
  multigrid, on the strength of the READY of build-openmp ("with one thread it equals
  the atomic result"), which speaks of the threaded executable against itself, not
  against the serial build. The quick test had shown the same an hour earlier (source
  dump 1.1e-14 between the threaded build at one thread and the serial build).
  Consequence for the release: `athena_cpu_omp` is not a reference for byte
  comparisons; `athena_cpu` and `athena_cpu_mpi` are.
- Cause not established. The two builds differ in two things: the flags (-O3 -DNDEBUG
  against -O2) and the Kokkos back end (OpenMP against Serial). Test R3, prediction
  written before the build: the threaded build with the flags of the serial build
  (`OMP_OPT=debug scripts/build_cpu_omp.sh`, -O2 -g, asserts on) at one thread gives
  the bytes of release core-v0.4 on the ten set-ups without multigrid (geo, boris, dep,
  east, os, c1 to c5). If it does, the flags are the cause and a track that needs
  threads AND bytes has a build for it. Refuted by any differing data byte in those
  ten: then the back end itself changes the arithmetic at one thread (other inlining
  and contraction in its kernels) and no threaded build is a byte reference. No
  prediction for jeans and binary (the multigrid average).
- R3 REFUTED in part. Run core-20261121-071842-f5a8b56 (threaded build with -O2 -g,
  `.work/build_omp_dbg_v05rc`, one thread, 6 cores, against release core-v0.4): 53 of
  75 items identical. Identical: geo, boris, dep, jeans, binary, c1, c2, c3, c5 (every
  set-up that does not evolve the spacetime, the two multigrid cases among them, for
  which I had made no prediction). Not identical: east (10 of 12 files), os (10 of
  16), c4 (2 of 4), the three with Z4c, at rounding (module histories 8.8e-16,
  constraint statistics 1.5e-10 in east and 1.8e-12 in c4); in os the first mesh and
  particle restart files are identical, so the initial data agree and the evolution
  does not. So the flags account for the particle-only set-ups (they differ with -O3
  -DNDEBUG and not with -O2) and the OpenMP build for the set-ups with Z4c (they differ
  with either flags) [VERIFIED by these two runs; which statement of the Z4c kernels is
  compiled differently was not looked for]. No threaded build is a byte reference.

### PAUSED (flag `locks/PAUSE` found at 2026-11-21T07:27Z): where I stopped

Done and pushed (origin/core/nrpic = 1b9c9f14 before this entry): the four merges
(source c3eb42e0), the four builds, the byte regression (PASS), the quick tests (PASS),
the regressions of the MPI and the threaded build, the flags test R3,
`RELEASE-v0.5.md` (first line REGRESSION PASS), `CHANGELOG.md` section core-v0.5,
`stage/G2/OPEN.md` section core-v0.5, `docs/FORMATS.md`, the last sections of
`interfaces/{mpi,threaded_build,cosmo_amr}.md`, STATUS, HANDOFF, and the published
directory `scratch/core/exe/core_nrpic_v05/` (four executables, COMMIT, SHA256SUMS,
READY, branches/).
Not done:
1. The card check. Run core-20261121-070946-1907f7b, Slurm job 4772, was still queued
   (the queue gave 08:02Z as its start). It may run on its own. `athena_gpu` of the
   candidate has not run on a card; RELEASE-v0.5.md and the READY say so. Closing
   steps: HANDOFF.md, "ONE RUN IS PENDING". Card time used by this package: none.
2. The messages to the tracks (one per track, which of its requests of
   `coord/REQUESTS.md` releases core-v0.4 and core-v0.5 serve): not started because
   of the flag. What I had read for them, so that the next session need not look it up
   again [each from the triage texts `interfaces/REQUESTS_{A2,ADF,B}.md`,
   `cosmo_gauge.md` section 7 and the source; none of it is posted]:
   - A: done in core-v0.5: `nrpic-cosmo-user-ref-func` (refinement function,
     `<particles_amr>`), `periodic-horizon-finder` items 1 to 3 (points mapped into the
     box, `<fastflow> diagnostics`, files in the `-d` directory),
     `refined-mesh-diagnostics` (`<particles> region_dcycle`), `stop-on-nonfinite`
     (`<z4c_guard>`, default on), `step-limit-coordinate-light-speed` (`<z4c>
     dt_lightspeed`), `processor-executable-threads` (`athena_cpu_omp`),
     `amr-for-first-horizon` (answered: no sub-cycling; example `peak_amr.athinput`);
     done in core-v0.4: `gauge-expanding-ball` (`<z4c> lapse_leak`; the K_ref and
     softplus forms declined with reasons in `cosmo_gauge.md` 7.1). Deferred to the
     unfinished branches: phase-1 generator, CMC slice, refined-level constraint solve,
     Zel'dovich ball (core/id-solver-2); special-relativistic push, snapshots at
     chosen times, per-species moments, which W the Newtonian history reports
     (core/newton-2). Not answered by either release: the finder keys and the restart
     question of `scouting-runs-ball`, the finder's spin projection, dispersion data.
   - B: done in core-v0.4: the linear-wave correction and the jitter tool; in
     core-v0.5: the threaded build. Deferred: TT part of the initial data; species
     history and the Poisson order (both exist on the unfinished core/newton-2); the
     new request `insitu-fourier-modes` of 2026-11-21 is unread.
   - C: nothing new in core-v0.5; collisions stop on several ranks; the four format
     requests, the ADM-mass diagnostic and collisions on refined meshes stay deferred.
   - D: done in core-v0.5: `finder-summary-outdir` (files in the `-d` directory),
     `openmp-cpu-build` (`athena_cpu_omp`), `trajmet-format-doc` (FORMATS.md: 17
     values); in core-v0.4: `lapse_leak`, `publish-gauge-exe`. Deferred: outer
     boundary (core/z4c-faces), throughput and self-force text (core/newton-2), proper
     time on analytic metrics, mass refinement near the hole. Four new requests of
     2026-11-21 are unread.
   - E: done in core-v0.5: `rng::ModeEntity`, the meaning of stream 3 and the epoch
     rule (`rng.md` sections 6 and 6.2), `con_signed`.
   - F: done in core-v0.4: `shift_eta_profile`, the card memory at 2700 MeshBlocks
     (`REQUESTS_ADF.md`, row mem2700), Gaussian clumps with momentum; in core-v0.5: the
     MPI processor build (no MPI card build released). Deferred: equilibrium clumps
     with momentum (core/clump-table). Two new requests of 2026-11-21 are unread.
3. The inbox of core holds twelve messages of 2026-11-19 to 2026-11-21 that I listed
   and did not read or acknowledge (numbers 76 to 87 of `nrpic-ctx inbox`).

## 2026-11-21T07:47Z  session core-lead-4 (batch 2b: closing release core-v0.5)

State found [VERIFIED by the commands named]: `git merge --no-edit main` brought main's
release commits (tag core-v0.5 on c3eb42e0, `coord/INTERFACES/` copies, decision 0021);
worktree clean; no pause flag; `squeue`: no job of core. `sacct`: job 4772 (the card
check) COMPLETED 07:42:27Z to 07:42:40Z, job 4763 (cosmo-amr T14b, T10g) COMPLETED
20:47 to 20:57 PST of 2026-11-20, job 4733 (mpi, two cards) COMPLETED. Release
executables: `.work/build_cpu_v05/src/athena` (sha256 222b8fa4..., 260888800 bytes)
and `.work/build_gpu_v05/src/athena` (2512c8d5...), built by the clerk from main, whose
`athenak/src` equals c3eb42e0 (`git diff c3eb42e0 9f7f85be -- athenak/src`: empty);
their checksums differ from the candidate's (b462068a..., 9d08dc13...), as
RELEASE-v0.5.md said a build in another directory may.

### Card check of the candidate (prediction K1 to K6 of the entry of 06:32Z): PASS

Run core-20261121-070946-1907f7b finished (all nine cases status 0, 13 s of card), judged
in core-20261121-074846-e830785: K1 to K6 held (sums 2.3e-13 of sum m W at worst,
identity 9.9e-16, MeshBlock counts and tracker path equal, source dumps 3.1e-14, the
note of `deposit_threads`). Panel b of `fig_card_v05.png` (looked at) is high for s3g,
usr, trk only: columns that are ratios of rounding-level residuals (trk: Mr_max, whose
numerator M_max is at most 1.7e-13; s3g, usr: pointwise max |M|/[M], while <|M|>
agrees to 4e-6 of itself) [VERIFIED from the files]. Written into RELEASE-v0.5.md
(section "Card check", now PASS) and the READY of `core_nrpic_v05` (STATUS, NOT TESTED,
CARD CHECK).

### Predictions, written before the runs of this session

S  T14b case Sf of package cosmo-amr (card run of job 4763 against T2b's processor run;
   `analysis/cosmo_amr/t14b_sf.py`, the measures `t14_card.py` applies to U, S, A): the
   bounds of the package's prediction for the homogeneous cases (its entry of 03:26):
   status 0; chi and E uniform on the card to 1e-12; alpha_max equal to the processor
   run to 1e-12 at every record; the same MeshBlock counts; identity below 1e-13.
   Refuted by any number above its bound.
R  Byte regression of the release processor build against the candidate
   (`regress_v04.py --base <candidate athena_cpu> --new .work/build_cpu_v05/src/athena`,
   twelve set-ups): all 75 items identical, classes a, b, other empty. Same source, same
   compiler and flags; the executables differ in their bytes (paths of the build
   directory in the debug information) [JUDGEMENT: nothing that enters the arithmetic].
   Refuted by one differing data byte.
G  Release card build, one short card job (the nine cases of `card_v05.list`, 13 s on a
   card): (i) `card_v05.py` against the processor runs: K1 to K6 hold with the bounds of
   06:32Z; (ii) `card_pair.py` against the candidate's card run of job 4772: s3g and usr
   (scalar field, no particles, no atomic additions) byte-identical in every file; the
   seven deposit cases not necessarily byte-identical (atomic additions in an order a
   card does not fix), their module histories within 1e-12 of each column [JUDGEMENT].
   Refuted for (ii) by a difference in s3g or usr, or by a deposit-case history column
   above 1e-12.

### Outcomes S and R (2026-11-21T08:00Z)

S HELD. Run core-20261121-075446-4944747 (`t14b_sf.py`): Sf on the card uniform to
  1.3e-14 (chi) and 2.3e-14 (E), alpha_max equal to T2b's processor run to 1.1e-15, 34
  MeshBlocks at every record, identity 4.4e-16. Figure `fig_t14b_sf.png` looked at.
R HELD. Run core-20261121-075456-a505400 (`regress_v04.py`, 6 cores): the release
  processor build `.work/build_cpu_v05/src/athena` against the candidate `athena_cpu`:
  75 of 75 items identical, classes a, b, other empty, every run status 0. Figure of
  run core-20261121-080001-5da4067 looked at (twelve bars, one colour). So the release
  executable and the candidate differ in their bytes (sha256 222b8fa4... against
  b462068a...) and not in any output of the twelve set-ups.
Also closed (package records, details in their journals): cosmo-amr T10g (two of five
predictions failed as written) and mpi P6 (rate clause of P6c failed), P7g (held).
G: card job 4775 queued (priority) since 07:54Z.

### Prediction of the chain test (decision 0021 item 6), written before it runs

Change of `scripts/submit_chain.sh`: an exit of the executable with status 137 or 143
without a line "Terminating on" and without a signal to the job itself is an outside
kill: the segment is resubmitted, at most MAX_OUTSIDE_KILLS = 2 times in a row (the count
is reset by a segment that ends at the wall clock or the time limit); the executable
runs as `chain/<PROC_NAME>`, a hard link to `chain/athena`, default `nrc-<8 hex of the
rundir>`; a PROC_NAME containing "athena" is refused; a chain whose config has no
PROC_NAME gets the default at its next segment. Test `scripts/tests/test_submit_chain.py`
(fake sbatch and squeue, a fake executable that kills its own process id), prediction:
A kill9, kill15, wall, tlim: QUEUED, QUEUED, QUEUED, DONE; 4 calls of sbatch.
B kill9 three times: QUEUED, QUEUED, FAILED "killed from outside 3 times"; 3 calls.
C kill9, kill15, wall, kill9, kill9, tlim: five times QUEUED, then DONE; 6 calls.
D exit 1 without a message: FAILED at once ("exit status 1"); 1 call.
E SIGKILL after "Terminating on time limit": FAILED ("exit status 137"); 1 call.
G old config without PROC_NAME: kill9 then tlim: QUEUED, DONE, under the default name.
H PROC_NAME=athena_run1 refused at start, no sbatch call.
Every fake process reads its own name in /proc/self/comm as nrc-<hash>, the same for
the segments of one chain and different between chains. Refuted by any other status
sequence or call count, or by a process named athena. Where I am least sure: that
/proc/self/comm of a bash script is the name of the hard link it was started through
(the kernel takes it from the file name given to execve) [JUDGEMENT, tested here].

### Outcome of the chain test, first run: FAILED by my fake, not by the script

Run core-20261121-080555-9730e2a: all six status sequences, all sbatch counts, the final
reasons and the refusal of `athena_run1` held as predicted (A to E, G, H). The name
check failed in every scenario: the fake executable recorded the process name `bash`,
because it began with `#!/usr/bin/env bash`, so `env` executed `bash` and the process
took the name of that file [VERIFIED: comm.log of each scenario]. This tests the fake,
not the chain: the name of the file the chain executes is never seen. My judgement in
the prediction ("the kernel takes it from the file name given to execve") is what the
second run tests, with `#!/bin/bash` (the kernel executes the linked script itself).
Prediction for the second run: the same statuses and counts, and the name nrc-<hash>
in every comm.log line. For AthenaK, which is an ELF binary, there is no interpreter.

### Outcome of the chain test, second run: HELD

Run core-20261121-080619-6a0793f (third run core-20261121-080635-3405fca: the same with
the legend of the figure inside it; figure `fig_submit_chain.png` looked at): every
status sequence and sbatch count as predicted (A: Q Q Q D, 4; B: Q Q F "killed from
outside 3 times in a row (exit 137)", 3; C: five Q then D, 6; D: F "exit status 1", 1;
E: F "exit status 137", 1; G: Q D, 2, under the default name although its config had
no PROC_NAME); H refused with no sbatch call. Every fake process recorded its own name
as nrc-<hash> (six different names for six chains), and `chain/athena` and
`chain/nrc-<hash>` are one file (link count 2) [VERIFIED: `comm.log`, `ls -l`]. So the
kernel names a process started through the hard link after the link, as predicted.
Not tested: a real Slurm job and a real AthenaK (the change touches neither the sbatch
line nor what AthenaK does); a running chain keeps the script it was started with
(sbatch spools it), so chains of other owners change only after they sync with main.

### Messages, triage, inbox (2026-11-21T08:05Z to 08:15Z)

- Read the twelve messages 76 to 87 of the inbox and message 88 (release announcement);
  read the requests of 2026-11-19 that `coord/REQUESTS.md` (state 14:35Z) does not list
  (64 to 75). Triage in `tracks/core/interfaces/REQUESTS_WAVE3.md`: W1 to W20, section 3
  for the older requests no triage text covered; three requests that arrived at 08:08Z to
  08:11Z (A `szekeres-dumps-kij`, C `collisions-several-ranks`, `heat-conduction-tested`)
  as W21 to W23.
- Text answers made today, so that the triage is true: `docs/FORMATS.md` snapshot row
  with the proper-time block (verified at `NrpicWriteSnapshot`; C's F3 quoted as C's
  finding, not checked); `REQUESTS_ADF.md` 2.3, what E of the accretion records is (D);
  `cosmo_gauge.md` section 8, D's ES-1G as D reports it; `collisions.md` and the READY of
  `core_collisions-2`, heat conduction tested by C. A's request for K_ij is served by the
  upstream group `variable = adm` [VERIFIED at `coordinates/adm.cpp`], not checked by
  core against a known solution.
- Posted one message per track (`20261121T0812*__to-<track>__core-v04-v05-answers.md`):
  done with option and example input (every example input checked to exist and every
  option name found in the source), deferred to which unfinished branch or to a package
  without a branch, declined with the reason; and two replies at 08:13Z for W21 to W23.
- Acknowledged every message of the inbox (0 left at 08:13Z): 76 to 88 and the three
  late ones as read today; 1 to 75 as read and triaged by earlier sessions, which never
  acknowledged them with the tool (the note says so).

### State at the end (2026-11-21T08:16Z)

Done: steps 1 to 6 of the batch-2b task except the judging of job 4775. Pending: the
release card build on the card-check list, run core-20261121-075439-58c2787, Slurm job
4775, queued for a card since 07:54Z (both cards busy with other jobs; a job of another
core session, 4777, is queued too). Prediction G stands as written; the steps to close it
are in HANDOFF.md. Card time of this session: 0.1 card-hours reserved, none used yet.

## 2026-11-21T12:55Z  session core-lead-5 (batch 3: merge of three source branches, release candidate core-v0.6)

### State found

- `core/nrpic` at 123f407e, clean, pushed; main merged (dcdc2ad8). No pause flag.
- The pending run of the last session, core-20261121-075439-58c2787 (release card build
  of core-v0.5, Slurm job 4775), has run: nine cases, status 0 each (`nrpic-run status`).
  It is judged below against prediction G of the entry of 07:47Z.
- Branches offered [VERIFIED `git log`, `git merge-base --is-ancestor c3eb42e0`]:
  core/newton-2 b7c9fc73 (closed, holds core-v0.5), core/z4c-faces 5d875275 (closed,
  holds core-v0.5), core/id-solver-2 3087526a (partial: card check Kc staged, never
  run). core/clump-table (7cc6c7b9, merged main at 04:52 PST, its session is at work)
  and core/oblate (4f01a81f of 2026-11-20, does not hold core-v0.5, no READY for a
  merged state) are not closed at 12:55Z; I look again before the builds start.

### Review of the three diffs against main (source of core-v0.5), as maintainer

core/z4c-faces (9 files, 814 lines added, none removed) [VERIFIED by reading the diff]:
- Every option is read only if present (`SbcExt::Read`, `z4c_sbc_ext.cpp` 35-101); the
  members default to the stock path (`variant = 0`, `theta_mode = 0`, `speed = 0`,
  `ghost_falloff = false`); the three hooks are `if (sbc.Extended()) return ...` at the
  top of `Z4cBoundaryRHS` and `if (sbc.ghost_falloff) GhostFalloff(...)` after the stock
  fill in `Prolongate` and `ApplyPhysicalBCs`. So the new options are off by default.
- How the failed byte regression was resolved (report of the package, journal entry 12
  of the branch): not by masking a difference. The body of the option reader stood in
  the header that `z4c.hpp` includes, and g++ 11.4 then compiled the unchanged
  `z4c_calcrhs.cpp` with two more fused multiply-adds; the reader moved to
  `z4c_sbc_ext.cpp`, the header keeps data members, the one-line `Extended()` and a
  declaration. Evidence of the package: r2, 45 files of 7 set-ups byte-identical with
  release core-v0.5, and the object comparison o1. That is the right repair; whether it
  survives the merge with two branches that add members to `Particles` is what my
  regression R tests (the cause is a compiler decision, so only a run says).
- Kernel `Z4cBoundaryRHSNonwave` writes rhs of a boundary cell from rhs of the cell one
  step inward along every direction in which it lies on a face; that cell is never a
  boundary cell (MeshBlocks have at least four cells), so no cell is read after it was
  written by another thread. `GhostFalloff` uses `Real G[4]` with p = `extrap_order`,
  which `z4c.cpp` 173 clamps to 2..4. Both divide by the distance from the mesh origin:
  a face through the origin is not guarded (documented as "not tested").
- Removed options `sbc_damp_gam`, `sbc_damp_theta` stop the run if non-zero. Accepted.

core/newton-2 (11 files, 1100 added, 37 removed) [VERIFIED by reading]:
- Hooks: five lines in `nrpic_newton.cpp` (init of the two new parts, `if (nw_fft)` in
  the potential, group sums after each kick and at the history); the two init functions
  return at once unless `newton_poisson` or `newton_ngroup` is in the input and add no
  parameter; the Fourier solver refuses a mesh that is refined, not periodic or in more
  than one pack. `particles.hpp`: one block of 38 lines of members. Accepted.

core/id-solver-2 (11 files, 1290 added, 68 removed) [VERIFIED by reading the shared
hunks and the option reader; the 840 lines of `nrpic_idsolve.cpp` only where they
decide defaults]:
- Nothing is read unless `id_solve` is present and true (`NrpicIdSolveInit` 115-117).
- `MGGravityDriver` no longer refuses `mg_bc = robin` on a refined mesh;
  `ApplyPhysicalBoundariesOctet` goes to the new `RobinBoundaryOctet` only if `robin_`.
  No released run can have reached either (the refusal stood in the way).
- Five things change in runs with `id_solve = true` without an option (section 8 of
  `id_solver2.md`): far field on by default on a mesh with no periodic face, the trace
  of the stress in the Jacobian, punctures of `nrpic_cf` enter the solve, refined
  meshes accepted, two more comment lines in the record.

### Decision: the default `id_far = multipole` stands

Asked by the package's report. Reasons: (1) against the semi-analytic continuum
solution the plain fill of the first pass has an error of W at the faces of -8.6e-3
and -9.3e-3 at 32 and 64 cells, which does not fall with the cell size, and the far
field +9.3e-4 and +2.4e-4, which falls (test W1 of the package, `id_solver2.md` section
5; off-centre: 5.6e-4 against 0.108, W2) [numbers of the package, not rerun by me];
(2) the solver was released in core-v0.4 with gate G2 of core open and its limits
listed, and no production run of a track rests on its bytes [JUDGEMENT: the tracks'
solved data are scouting runs]; (3) `id_far = robin` gives the bytes of core-v0.5 for
matter at rest (M1 of the package; my quick test Qi repeats it with the merged
executable); (4) a torus is not affected. It enters the changelog as behaviour that
changes without an option, with the sizes measured in M1.

### The nine never-set members of the mesh header (newton-2's request)

Nothing to change: `Mesh::ZeroUnusedMeshIndcs` (`mesh/mesh.cpp` 366-376) sets them to
zero since core-v0.4, in the constructor (356) and after reading a restart header
(`mesh/build_tree.cpp` 363) [VERIFIED by reading; changelog of core-v0.4, item 1 of the
corrections]. The seven differing restart files of newton-2's T11b were written by its
pre-merge build, whose source is older than core-v0.4. Prediction H below reads the
bytes from files the candidate writes.

### Predictions, written before any build or run

Base of every byte comparison: `/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena`.

- **R** (driver `regress_v04.py`, twelve set-ups, new options absent): 75 of 75 items
  identical, classes a, b and other empty. Refuted by one item that is not identical.
  If it fails in the set-ups with Z4c only (east, os, c4), the first suspect is again a
  compiler decision in files that include `z4c.hpp`; `compare_objects.py` of package
  faces then names the object.
- **Rm**: the MPI build started without mpirun: 75 of 75. **Ro** (threaded build at one
  thread, not a byte reference): every run ends with status 0; geo and jeans identical,
  the rest at rounding as for core-v0.5 (31 of 75 identical then); a difference above
  1e-9 in a history column would be a finding.
- **H**: in every mesh restart file the candidate writes in R (os, c5) the nine members
  cnx1 to cke of `mesh_indcs` are zero. Refuted by one non-zero byte.
- **Qn** (newton-2): the merged `athena_cpu` on `problems/newton/periodic_fft.athinput`
  (wave of 32^3 particles, both symbols) with one group history writes the bytes of the
  branch's `scratch/core/exe/core_newton-2/athena_cpu`, restart files included (both
  sources zero the header). Refuted by a differing file.
- **Qf** (z4c-faces): `problems/tests/z4c_faces.athinput` with `time/nlim=8`: (i) as
  written (the full set) the bytes of the branch's `athena_cpu`; (ii) with the stock
  values on the command line (`extrap_order=2 ghost_falloff=false
  sbc_variant=sommerfeld sbc_speed=unit`) the bytes of the release executable run with
  the same command line. Refuted by a differing file in (i) or (ii).
- **Qi** (id-solver-2): (i) the package's `regress_m1.py` with the merged executable
  against release core-v0.5 gives its M1: with `id_far = robin` Gaussian at rest,
  expanding ball and torus byte-identical; with the default psi differs by 1e-8 to
  1.5e-6 and nothing else of the first pass changes; (ii) `regress_r2.py --same` on the
  case directories of run core-20261121-080135-890689a: the eight second-pass cases
  byte-identical to the branch executable's files (79 files). Refuted by a differing
  file in (i, robin, matter at rest) or in (ii).
- **C** (the combinations the merge creates; none of the three branches touches the
  code of another, so I expect no interaction): the faces options together with a
  solved initial slice (`id_solve` on the expanding ball, then eight steps with the
  full set of faces options) runs to the end with finite fields and with the initial
  slice of the same run without the faces options (the solve happens before the first
  step: `ball.idsolve.txt` identical). Refuted by a non-finite stop (status 3) or a
  different record of the solve.
- **Kc** (the package's prediction, entry 15 of `JOURNAL-idsolve2.md`, card executable
  of the branch at 395e17d, sha256 0fb76bdb...): same outer iterations as processors
  (within one on refined meshes), psi and W to 1e-12 of their maxima on uniform meshes
  and 1e-9 on refined ones, P_ADM_x of `p5_mov_n64` = 0.5499999519755 to 1e-11; refuted
  if an iteration count differs by more than one or a field by more than 1e-8.
- **K6** (merged card executable, short list, at most 0.3 card-hours asked): every
  case status 0; Newtonian plane wave with the Fourier solver: particle sums of the
  history equal to processors to 1e-10 relative; faces example (8 steps, full set):
  constraint norms of the history equal to processors to 1e-7 relative; two cases of
  the id solver (`p5_mov_n64`, `g_smr1`): iteration counts as on processors (within one
  on the refined mesh); two cases of core-v0.5 (`dep`, `cluster` of `card_v05.list`):
  history columns 4 to 12 equal to processors to 1e-10 and the deposit identity below
  1e-13. Refuted by a status other than 0 or a bound exceeded.

### Amendment of prediction C before its run (13:05Z)

Read after the entry above was committed and before the quick test ran:
`nrpic_idsolve.cpp` 1787 calls `Z4c::ApplyPhysicalBCs`, which after the merge of
core/z4c-faces also applies the fall-off fill when `ghost_falloff = true`. So with
`id_residual = code` the record of the solve might differ with the faces options
(the monitor reads ghost cells); with `stencil` I still expect it identical. C is run
in both modes. (Written into this journal only now, with the outcomes; the test design
in `quick_v06.py`, committed as 7cf7db88 before the run, has both modes.)

### Outcomes (2026-11-21T13:45Z)

Merges: a1fffa58 (newton-2), 1419f19a (z4c-faces), 984bde68 (id-solver-2), no conflict.
Source commit of the candidate: 984bde68c6201c8f100ced3d6a7effbea9cafd80. Builds:
serial 164 s on 6 jobs, card 1127 s on 3, MPI 479 s on 2, threaded 289 s on 4.

- **R held.** 75 of 75 items identical with release core-v0.5, classes a, b, other
  empty (run core-20261121-130202-7cf7db8). The compiler effect of the faces header
  does not come back in the merged source.
- **Rm held** (75 of 75, core-20261121-132245-c02f6b7). **Ro held**: every run status
  0, 32 of 75 identical, geo and jeans identical, module histories within 1.2e-15,
  constraint statistics within 1.4e-10 (east) and 1.9e-12 (c4), below the 1e-9 I set
  (core-20261121-133243-74c17ff, judged in core-20261121-134007-f8513b0).
- **H held.** 12 mesh restart files, the nine members zero in each
  (core-20261121-130813-710b3cc).
- **Qn held** (28 of 28 files identical with the branch executable). **Qf held** in
  both parts (5 of 5 with the branch executable; 5 of 5 with release core-v0.5 at the
  stock values). Same run.
- **Qi held.** (i) `id_far = robin`: 8, 9, 8 files identical with core-v0.5 (Gaussian at
  rest, ball, torus); default: psi by 9.7e-9, 3.6e-8, 1.48e-6, W by 2.67e-3, the numbers
  of the package's M1 (core-20261121-131148-6efd1b8). (ii) 79 of 79 files identical
  (core-20261121-131250-f8df905).
- **C held, and the amendment's worry did not materialise**: the record of the solve
  is byte-identical with and without the faces options in both modes; four runs status
  0, finite; mean |H| after 8 steps 4.9e-4 without, 3.6e-4 with. Why the fall-off fill
  does not enter the record in mode code I have not looked up in the source (the call
  at 1787 may lie after the last residual): no cause is named.
- **Kc held** (the package's prediction): outer iterations 34, 16, 20, 27, 5 on card
  and processors, psi within 2.2e-15, W within 2.5e-14, P_ADM_x 5.499999519755e-01 on
  both (card run core-20261121-125651-edde517, 87 s; judged in
  core-20261121-133219-2c8f63c).
- **K6 open**: job 4800 (run core-20261121-132052-f330004) submitted at 13:20Z, the
  earliest moment the card build existed and a second slot of core was free; seven jobs
  of other owners are ahead of it. Steps to judge it: `RELEASE-v0.6.md`, section "Card
  check of `athena_gpu`".
- Not predicted, closed on the way: the release card build of core-v0.5 (job 4775,
  prediction G of 07:47Z) held in both parts (core-20261121-125722-91a199a,
  core-20261121-125743-84f0e42; module histories of the two card runs within 1.2e-15);
  the faces package's card check k1 (job 4782 had run at 01:40 PST and was never
  judged): 7.3e-12 from processors in both cases, bound 1e-7
  (core-20261121-134059-e3ab6f3, status failed by a side effect of the comparison
  script: it lists the card's log files as missing).

Faults of mine in this session, on record:
1. `RELEASE-v0.6.md`, `CHANGELOG.md` and the published `COMMIT` first carried forty
   hexadecimal digits for the source commit that I had written without taking them from
   git (only the first eight were right). Found when `git rev-parse` was printed beside
   the first line; corrected in all three files before anything was pushed (the commit
   after the one that adds the release file). A full hash is copied from `git
   rev-parse`, never completed by hand.
2. `hst_pair_v06.py` failed in its first registered run (core-20261121-133938-efeb8b4:
   the classes of the regression summary are lists) and in its second drew the
   non-finite history of c5 as a bar (core-20261121-133947-f7d1d50); the third run
   counts.
3. The first drawing of `fig_quick_v06.png` had the legend over two bars; drawn again
   (core-20261121-133153-89d375b).
4. The amendment of C was written into the journal after the run, not before (above).

Left out of the candidate: core/clump-table (at 13:37Z its tip 099882b3 says "merge
notes for core's lead in the interface text"; no executables with READY for that state
are published) and core/oblate (unchanged since 2026-11-20). Both go to the next
release.

Card time: 0.024 card-hours used (Kc), 0.3 asked (job 4800). Processors: at most six
cores at a time (builds and runs together).

## 2026-11-21T15:46Z  session core-lead-6 (batch 4a: closing release core-v0.6, gate package G2)

State at start: main merged (decision 0022, release core-v0.6 on main, tag on 984bde68).
Slurm job 4800 (run core-20261121-132052-f330004, card check K6 of the merged card
executable) COMPLETED in 46 s, fifteen cases with rc 0 in `batch.list.status`; not yet
judged. Release builds on main: `.work/build_cpu_v06/src/athena` (sha256 91fc59b3...),
`.work/build_gpu_v06/src/athena` (ea473498...); their checksums differ from the
candidate's (2ec1f232..., 168e5da6...), as builds in other directories do (paths in the
debug information) [VERIFIED by `sha256sum`]. No source change in this session.

### Predictions, written before the release builds run (15:46Z)

- **K6** stands as written in the entry of 12:55Z; judged now with `card_v06.py` and
  `card_v05.py` on the outputs of job 4800.
- **R6** (release processor build `.work/build_cpu_v06/src/athena` against the
  candidate `scratch/core/exe/core_nrpic_v06/athena_cpu`, `regress_v04.py`, twelve
  set-ups of wave 1): 75 of 75 items identical, classes a, b and other empty, as for
  core-v0.5 (core-20261121-075456-a505400). Refuted by one differing item.
- **G6** (release card build `.work/build_gpu_v06/src/athena` on the fifteen cases of
  `card_v06.list`; the whole list ran in 46 s in job 4800, so the full list costs no
  more card time than one case would wait for, and I ask 0.1 card-hours): (i) every case
  status 0; against the processor runs `card_v06.py` and `card_v05.py` give the verdicts
  they give for job 4800; (ii) against the candidate's card run (job 4800, `card_pair.py`)
  the vacuum cases f_full, s3g and usr byte-identical in every file (they deposit
  nothing), and every history of the other cases within 1e-12 of each column above 1e-6
  of the largest column (atomic deposition on the card is not repeatable bit for bit;
  for core-v0.5 the module histories agreed to 1.2e-15). Refuted by a status other than
  0, a difference in f_full, s3g or usr, or a history column beyond 1e-12.

### Outcomes (2026-11-21T15:56Z)

- **K6 held.** Job 4800 ran at 15:21Z (46 s), fifteen cases with status 0. Judged in
  core-20261121-154700-2de4974 (`card_v06.py`: Newtonian histories within 1.6e-11 of
  processors, bound 1e-10; f_full identical, c_cd1 1.9e-10, bound 1e-7; solver outer
  iterations 22, 34, 20 on both, psi_max equal to 2.5e-15 at worst) and
  core-20261121-154710-220c1b0 (`card_v05.py`: K1 to K6 of core-v0.5 held, deposit sums
  2.3e-13 at worst, identity 9.9e-16, dumps 3.1e-14). Not bounded and different: Hr_max
  (column 11) of `gauss.cstat.hst` of g_smr1, 1.380745 against 1.379534 (8.8e-4), while
  H_max agrees to 1.2e-12 [VERIFIED by reading both files]; the same class as trk column
  15 of core-v0.5 (0.14 again). Figures looked at; in `fig_card_v06.png` the dashed
  bounds run across all cases although each applies to its own, so the g_smr1 bar seems
  to cross one: noted in the release file, the script not changed.
- **R6 held.** Release processor build against the candidate: 75 of 75 items identical,
  classes a, b, other empty (core-20261121-154737-dc1e4c1; figure
  core-20261121-155317-1ee04bf looked at).
- **G6 open.** Job 4810 (run core-20261121-154654-d3ec487) queued at 15:47Z; commands to
  judge it in `RELEASE-v0.6.md`, section "Release builds against the candidate".

Records written: `RELEASE-v0.6.md` (first lines, card section, release builds),
`scratch/core/exe/core_nrpic_v06/READY` (athena_gpu line), `CHANGELOG.md` (section "Run
scripts" of core-v0.6: the chain script), `REQUESTS_WAVE3.md` section 5 (W24 relaxed
lapse first for core-v0.7, W25 to W29), inbox acknowledged (E lockstep, orch release).

G2 package: `nrpic-stage collect` gave 18 items (two new of decision 0012/0016, renumbered
from C12); filled: 10 PASS, 8 FAIL. G2 is not met (OPEN.md, first section): ladder rows 3
and 4 PARTIAL, no single three-way convergence study, no note, no verifier, architecture
schematic stale, no REVIEW/SCOPE documents in the stage directory. Read for it: Track C's
drift package (M/4 mesh pushes clusters outward, seven to ten times less on M/8: core's
M/4 bisection does not test the threshold) and Track D's g2runs (relaxed lapse grows a
vacuum horizon by 1.3e-3; the term acts wherever alpha > alpha_0,
`z4c_gauge_ext.hpp` line 19).

Faults of mine in this session, on record: the first wording of C1's evidence said the
ladder rows carry over "byte for byte" from the wave-1 regressions; core-v0.4 differed
in classes a and b and the full ladder runs were not repeated, so it was reworded to a
judgement before the commit.

### Stage check (2026-11-21T16:20Z)

`nrpic-stage verify core G2` with output checksums read run outputs for 13 minutes and
had reached the runs of 2026-11-19 when I stopped it by its process id (log
`scratch/core/tmp/lead_b4a/verify.log`, exit 143); with `--no-checksums` it took 5.5
minutes and FAILS on two checks: no working note, and 10 of 1405 runs with record
problems (9 runs name the executables of `core_cosmo-amr`, published again after the
runs; job 4810 not finished). The 11th of the first pass, core-20261119-143517-ec2f4fc
(gauge test E2, job 4641, both cases rc 0, never closed), is closed now with
`nrpic-run finish`. `nrpic-stage report`: verdict FAIL, eight items FAIL (C1, C2, C6,
C7, C12, C14, C15, C16); decision requested: keep core at G2 in progress.

## 2026-11-21T20:26Z  session core-lead-7 (batch 5: cards first; no source change)

State at start: main merged (decision 0025). Job 4810 (run core-20261121-154654-d3ec487,
release card build on the fifteen cases) COMPLETED at 17:21Z in 48 s, fifteen cases rc 0;
closed with `nrpic-run finish` and judged below against prediction G6 (entry of 15:46Z).

### Outcome G6 (release card build `.work/build_gpu_v06/src/athena`), 20:21Z

- (i) HELD. `card_v06.py` CARD PASS (status, newton, faces, solver held; Newtonian
  histories within 1.6e-11 of processors, c_cd1 1.9e-10; solver outer iterations 22, 34,
  20 as on processors), run core-20261121-202028-a32d12c; `card_v05.py` CARD PASS (K1 to
  K6 held; deposit sums 2.3e-13 at worst, identity 9.9e-16, dumps 3.1e-14), run
  core-20261121-202041-0b6d418. Not bounded, as for job 4800: g_smr1 `gauss.cstat.hst`
  column 11 (Hr_max) 2.8e-3 against processors.
- (ii) PARTLY REFUTED. Against the candidate's card run (job 4800), run
  core-20261121-202057-a5b2ed6: the vacuum cases f_full (5 of 5 files), s3g (6 of 6) and
  usr (6 of 6) byte-identical: held. Every module history (`*.nrpic.hst`) within 2.2e-15
  and every `z4c.user.hst` equal or within 1.7e-29 absolute: held. The bound 1e-12 on
  every history column is refuted in the constraint-statistics files only: `cstat.hst`
  column 11 (Hr_max) of g_smr1 1.9e-3 and of cluster 7.6e-10, column 12 (Hr_mean) of
  p5_mov_n64 1.4e-11, column 15 (Mr_max) of trk 2.0e-2 and of peak 2.1e-10; H_max
  (column 9) is not among them. These columns are ratios of a residual to the sum of the
  magnitudes of its terms, taken where both are at rounding level, so they carry the
  card's non-repeatable atomic deposit at order one [JUDGEMENT; the same class as
  g_smr1 column 11 in job 4800 and trk column 15 of core-v0.5]. My prediction did not
  exclude them; it should have. Verdict on the release card build: PASS on the release
  criteria (both CARD PASS), with that bound of G6 (ii) refuted as written. Figures
  `fig_card_v06.png`, `fig_card_v05.png`, `fig_card_pair.png` looked at (the pair figure
  shows the five cstat bars, 1e-11 to 2e-2, and the module bars near 1e-14).

### Ladder row 4 on the M/8 mesh: rule, measured quantity, predictions (20:26Z, before any run)

Why again: on M/4 the mesh pushes clusters outward and stabilises them (Track C's drift
package, `git show track/C-sidm:tracks/C-sidm/drift/README.md`, requests 1-3), so core's
M/4 bisection (`verify/LADDER.md` row 4, wave 2) did not test the threshold. Why not a
growth rate: Track C's G1 gate review (`git show
track/C-sidm:tracks/C-sidm/stage/G1/GATE_REVIEW.md`, C2) found growth rates on cluster runs
window-dependent (ln|d| concave) and binds "no constant growth rate" at G2; the measured
quantity here is therefore the collapse time, or the contraction against a control.

Set-up (all six runs the same except y_c and the kick): wave-2 protocol (10^4 stratified
particles, seed 1, equilibrium table, `--no-consistent-table`), deck
`tracks/core/verify/row4/st_m8.athinput`: the release input `problems/st/st_cluster_amr.athinput`
on a STATIC mesh with the level-6 nest (M/4) inside |x|_inf < 6 M and a level-7 region
(M/8) inside |x|_inf < 3.9 M (Track C's M/8 region), nothing finer; finder every 32 cycles
(every 1 M as before); to 300 M; release card executable
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`; chains with restarts every 20 M.
- Member: one-percent uniform inward kick (`--vpert 0.01`). Control: the same model, same
  seed and particle positions, no kick (`--vpert 0`), same mesh, run as long. The control
  carries what the mesh and the particle noise do by themselves; the kick is the only
  difference [JUDGEMENT: for these collisionless runs "collisionless control" is read as
  "the run without the perturbation"].
- First level of the bisection: ends y_c = 0.605 (collapsed at 191 M on the earlier
  finer AMR mesh, `runs/st/yc0605_v5`) and 0.755 (0.756 unperturbed stayed 800 M); middle
  0.680 (turning point of E_b/M_0 at y_c* = 0.6796, run core-20261115-152805-47d8f25).

Measured quantities (script to be written for the analysis, reading `st.nrpic.hst` column
13, the central lapse at the origin probe, and `st.horizon_summary_0.txt`):
- t_c: the first time an apparent horizon is found or the central lapse falls below 0.3.
- D = mean of alpha_c over 200-300 M of the member minus the same mean of its control
  (when neither collapses by 300 M). Also kept: the mean of each run against its own
  equilibrium alpha_c, and the coordinate r50 of the particles from the snapshots.

Class of a member (fixed now):
- COLLAPSE: t_c <= 300 M. CONTRACTS: no collapse and D < -0.02. EXPANDS: no collapse and
  D > +0.02. STAYS: |D| <= 0.01. UNDECIDED: 0.01 < |D| <= 0.02.
- If the control collapses and the member does not, the model counts as unstable
  (the noise alone takes it away) and the member as UNDECIDED in D.
Side of a model: UNSTABLE if the member or the control collapses, or the member
CONTRACTS or EXPANDS; STABLE if the member STAYS and its control does not collapse.
Bracket: y_lo = the largest UNSTABLE y_c, y_hi = the smallest STABLE y_c; valid only if
y_lo < y_hi and no UNDECIDED member lies between them. Next level: the midpoint of
(y_lo, y_hi) with its control. An UNDECIDED middle is continued with its control to
600 M (restarts are exact) before any next level. A non-monotone outcome (a STABLE model
below an UNSTABLE one) gives no bracket and is recorded as such.

Predictions:
- P1. 0.605 member COLLAPSES with t_c between 120 and 300 M; its control does not
  collapse before the member. Refuted by no collapse by 300 M (then M/8 still
  stabilises at 10^4 particles, or the earlier collapse needed the AMR mesh).
- P2. 0.755 member STAYS (|D| <= 0.01), no collapse in member or control, and the
  control's own 200-300 M mean within 0.01 of its equilibrium alpha_c (Track C's M/8
  controls drifted 0.002-0.004 by 300 M). Refuted by a collapse, |D| > 0.01 or a control
  drift beyond 0.01.
- P3. 0.680 member does not collapse by 300 M and is STAYS or UNDECIDED (a growth time
  near the turning point exceeds 300 M). Refuted by a collapse (threshold above y_c*)
  or CONTRACTS/EXPANDS beyond 0.02.
- P4. Cost: 6.4 to 8.3 s of card time per M (Track C's M/8 deck with 10^5 particles:
  8.2-8.3 s per M), 0.55-0.7 card-hours per run to 300 M, 3.3-4.2 for the six runs;
  each fits one 50-minute segment. Refuted by more than 10 s per M.

Queue: six chains registered with `nrpic-run submit --launcher chain --gpu-hours 2.0`
(at most two segments each; 12 card-hours asked at most, about 4 expected); two eligible,
the other four held at once and released one at a time by
`tracks/core/verify/row4/sequencer.sh` (setsid nohup, log
`scratch/core/tmp/lead_b5/sequencer.log`). Order: 0.605 member, 0.755 member, 0.680
member, 0.605 control, 0.755 control, 0.680 control.

### What ran after the predictions (20:27Z-20:45Z)

- Initial data: run core-20261121-202643-d66c4ee (`make_row4.py`): y_c = 0.605, 0.680,
  0.755 with alpha_c = 0.6281, 0.6875, 0.7509, R/M = 5.750, 6.558, 7.902; turning point
  y_c* = 0.6796 (E_b/M_0 = 0.036058), equal to run core-20261115-152805-47d8f25. The
  0.755 cluster reaches R = 7.9 M, at the outer edge of the M/4 nest (blocks to 8 M);
  its outermost particles sit in M/2 cells, as in the wave-1 run 0.756 on M/2 [noted,
  not tested].
- Deck smoke test on processors (release processor build, 0.680 member, 4 cycles): run
  core-20261121-202702-c6a4d7d: 456 MeshBlocks, 64 of them at level 7 (M/8), dt = M/32,
  "Terminating on cycle limit", 10^4 particles kept. Same block count as Track C's M/8
  deck (456). AthenaK warns that `num_levels` is unused with static refinement.
- Six chains submitted with `nrpic-run submit --launcher chain --gpu-hours 2.0` (release
  card executable): run ids and jobs in STATUS.md and HANDOFF.md; jobs 4841-4844 held at
  once, sequencer pid 2668479 started with setsid nohup. At 20:44Z all six were waiting
  behind eleven jobs of other owners. P1-P4 open.
- Code test of `row4_fate.py` on the wave-2 M/4 runs (core-20261121-204433-1c720e0; the
  pairs exercise the code, they are not member and control): it reads, classifies and
  draws (figure looked at). It shows that the late central-lapse swings of those runs
  are larger than the 0.01 band, so a 100 M mean can move by about 0.01; the rule is not
  changed after seeing this, the caveat goes with the outcome.

Faults of mine on record: none known in this session beyond the G6 (ii) bound, which
did not exclude the normalized constraint columns.

## 2026-11-21T23:16Z, batch 8, session core-lead-8 (no cards, no source change)

Task: (1) corrections after the fresh verifier's report (`stage/G2/VERIFIER.md` section 3),
C16 marked, OPEN.md items for the restart limit (decision 0027 item 3) and the step rule
with a Gamma-driver shift (0027 item 2), provenance of the pre-program run directories of
ladder rows 2 and 4; (2) core's working note for G2 under `tracks/core/note/`. The six
row-4 chains of batch 5 and their sequencer are not touched (6 core jobs in the queue at
23:15Z).

Plan and predictions, written before any run of this session:
- Q1 (inventory of pre-program directories, registered processor run, one core): each of
  `runs/os/nocap_sc`, `runs/os/nocap_v4`, `runs/prolate/e09_v8`, `runs/st/yc0900_v4`,
  `yc0819_v4`, `yc0605_v5`, `yc0500_v5`, `yc0283_v5`, `migration_yc0500_v4`,
  `yc0756_unpert` holds its input file, at least one timestamped copy of the executable
  that ran (`athena.<stamp>.exe`) and the files the ladder numbers are read from
  (`*.nrpic.hst`, `*.horizon_summary_0.txt`). Refuted by any of these missing.
- Q2 (note figures, one registered run of `note/scripts/run_all.py` reading raw outputs):
  (a) the largest relative errors of E, L_z, Q of the Kerr passage read from the
  regression-G trajectories equal LADDER row 1 to four digits; (b) the first horizon
  of `runs/os/nocap_sc` at 16.39 M with M_AH/M 1.0004 and the largest deviation to 60 M
  1.34e-3, and regression O to 25 M within 6.3e-4; (c) the central lapse of the five
  cluster models stays (0.900, 0.819), collapses (0.605 by 191 M, 0.500 by 104.3 M) and
  rises toward one (0.283) as LADDER row 4 says. Refuted by any number differing beyond
  its printed digits.

### Q1 outcome (23:18Z-23:25Z): inventory run core-20261121-231825-135474c

Held for inputs, executable copies, logs and both history files in all ten directories
(two builds: `eea69999...` and `bbb74535...`; chains keep theirs in `chain/`). FAILED as
written for the horizon summaries: absent in `st/yc0900_v4`, `st/yc0819_v4`,
`st/migration_yc0500_v4`, `st/yc0756_unpert`, where no finder ran; their ladder numbers
come from the history files, so nothing the ladder states is without its file. Figure
`fig_inventory.png` looked at. The directories are named as pre-program in
`verify/preprogram/README.md` (no manifest written after the fact: the source commit and
the command lines are not recoverable).

### Working note: story first (paper-writing Sec. 10, steps 1-3), 23:30Z

300-word version. Every science track of the program builds on one implementation of
the particle-in-cell coupling between collisionless matter and the Z4c evolution inside
AthenaK. This note says what that implementation is, what each of four releases added,
and how far it has been verified against the rows of the verification ladder that core
owns. The base pushes particles along geodesics with an implicit midpoint rule or a
spacetime Boris rule, deposits their stress-energy with clouds across refinement levels,
and feeds it to Z4c. On a fixed Kerr black hole both pushers conserve energy, angular
momentum and the Carter constant to the paper's digits and converge at second order.
A dust ball collapses to a black hole whose horizon mass agrees with the initial mass at
the paper's level at formation and drifts slightly beyond it later. A prolate spheroid
forms its horizon at the paper's time, with a mass deficit that shrinks with
resolution but does not vanish at two resolutions. The five star clusters of the paper
meet the paper's fates; the bisection of the stability threshold on a coarse mesh did
not collapse because that mesh pushes clusters outward, and its repetition on a finer
mesh is running. Four releases added collisions, scalar fields with stochastic
sources, Newtonian reference gravity, elliptic initial data, several black holes,
threads, several ranks, refinement in the periodic box and new outer faces, each tested
by its package. A fresh verifier recomputed fourteen claims from raw outputs: the numbers
hold; one general statement (exact restarts) holds only for periodic set-ups and the
particle state; five texts needed a corrected measure or count. Open for the gate: the
oblate data, the threshold on the finer mesh, three-way convergence of one coupled
set-up, and two limits for the next release (the relaxed lapse near a black hole, a step
limit with the gauge speeds).

Longer version: the outline of `WRITING_GUIDE.md` with one paragraph per subsection
(written as the main text directly; no separate 1000-word file). Step 4 (reviewer
subagents) not run: no subagent tool in this session.

### Q2 outcome (23:28Z-23:31Z): runs core-20261121-232757-f86d965, -232936-d979f1c

Held, all three parts. (a) Kerr passage largest relative errors from the raw trajectories
of regression G equal LADDER row 1 to four digits (2.781e-8, 0, 1.254e-7; 9.046e-8,
1.136e-8, 7.825e-7; 2.162e-6, 5.304e-6, 5.060e-5; 2.046e-6, 3.788e-6, 5.289e-5);
orders 2.0001/2.0003, 1.9998/1.9991, 1.9997/1.9989. (b) `runs/os/nocap_sc`: first
horizon 16.3894 M, M_AH/M 1.000353, largest deviation to 60 M 1.338e-3, all 9328
particles removed by 19.74 M; regression O: identical first horizon and mass, 6.345e-4
to 25 M. The deviation first exceeds 1e-3 at 29.11 M and stays above from 30.92 M (the
verifier's "from 31 M"). (c) the five fates as LADDER row 4 (0.900: 0.8862-0.8919;
0.819: 0.7875-0.8190; horizons 191.0 M and 104.31 M, M_AH/M 0.99999, 1.0001; 0.283 at
270 M 0.97598); M/4 bisection means equal the LADDER table to four digits. Inputs: 11
sha256 checks passed (pre-program files against the inventory), 31 inputs without a
recorded checksum (wave-1 manifests list no outputs). Figures looked at: fig_geodesic
(after one layout change: running maxima instead of raw errors), fig_collapse,
fig_clusters (legends moved off the data), schem_architecture (rescaled to page width;
legend and tags moved). The second run differs from the first only by the ledger's
escape of `<` and `>`, seen on page 8. Note compiled (8 pages, all read), checker: 0
undefined references or citations, 0 overfull boxes.

### Close of session core-lead-8 (23:32Z)

Done: verifier corrections (five texts, C3 label, C16), OPEN.md u and v, W31, the
pre-program inventory, the working note (C14, C15). No source change, no card job; the
six row-4 chains and their sequencer untouched (4839 running at 23:30Z).
Not done: `nrpic-stage verify` on the clean export (C6; the last full verify read run
outputs for 13 minutes in batch 4a); reviewer subagents of the story-first procedure
(no subagent tool); inbox messages outside the task (listed in HANDOFF.md).
Faults of mine on record: the inventory prediction Q1 was written too broadly
(horizon summaries exist only where a finder ran); the first ledger printed `<` as an
inverted exclamation mark (OT1 encoding), seen on page 8 and fixed by a second
registered run; the first architecture schematic was drawn at poster scale (text too
small at page width) and had overlapping legend labels, both seen on the PNG and fixed
before the registered run.
