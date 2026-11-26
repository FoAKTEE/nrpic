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

## 2026-11-23T01:50Z (2026-11-22 17:50 PST), batch 10a, session core-lead-10a (analysis round; no AthenaK source change)

Task: close the six row-4 chains (all six DONE at tlim by `submit_chain.sh --status`,
segments of jobs 4839-4844), classify by the rule of 2026-11-21T20:26Z, queue the next
level; note, G2 stage, inbox answers to Track A (step limit) and kb (paper-code links).

### Prediction before the footer test of `scripts/cpu_run.sh` (Track A request (iii), 2026-11-23T01:50Z)

Track A (outbox 20261121T231546Z, item iii) reports that the footer's awk call fails with
`-v load=...` under gawk and that a non-zero exit of athena leaves the script at `wait`
under `set -e`. Fix: rename the awk variable to `ldavg`; `rc=0; wait "$apid" || rc=$?`.
Prediction: with ATHENA_EXE=/bin/true the fixed script exits 0 and writes one footer line
`# exit=0 ...`; with a stub that exits 3 it exits 3 and writes `# exit=3 ...`; the
unfixed script exits 2 on /bin/true without a footer (reproducing A). Refuted by a
missing footer or a different exit status in either case.

Outcome (2026-11-23T01:50Z; stubs in `scratch/core/tmp/lead_b10a/footer/`, not a
registered run: a shell test with /bin/true and a stub, no simulation): the unfixed script
exits 2 on /bin/true with "awk: fatal: cannot use gawk builtin `load' as variable name"
and no footer (A's report reproduced); on the exit-3 stub it exits 3 without a footer
(set -e at `wait`). Fixed script: exit 0 with `# exit=0 ...`, exit 3 with `# exit=3 ...`.
Prediction holds. (The cpu_share of a zero-second stub is meaningless, as expected.)

### Outcomes of row 4 on M/8, level 1 (2026-11-23T02:05Z): runs closed, fates by the rule of 2026-11-21T20:26Z

All six chains ended in one segment each at tlim = 300 M (jobs 4839-4844, status DONE;
`nrpic-run finish`, commits e66f7a58..cbee7c2b). Fate analysis: run
core-20261123-020318-e952741 (`verify/row4/row4_fate.py`, figure `fig_row4_m8.png` looked
at: normalised central lapse of all six, and member minus control with the 200-300 M
window); the note's figure (`note/scripts/fig_row4_m8.py`, absolute central lapse with
the equilibrium values; test render in `scratch/core/tmp/lead_b10a/figtest/`, looked at)
shows the same.

| y_c | alpha_c eq | member | control | class / side |
|---|---|---|---|---|
| 0.605 | 0.6281 | t_c 180.5 M (lapse < 0.3), first AH 188.0 M, M_AH/M 1.009 at the last search | no collapse; mean 200-300 M 0.7303 (+0.102 against its own equilibrium: moves outward, towards its equal-binding partner) | COLLAPSE / UNSTABLE |
| 0.680 | 0.6875 | t_c 219.5 M, first AH 225.0 M, M_AH/M 1.006 | t_c 251.5 M, first AH 256.0 M, M_AH/M 1.005 | COLLAPSE / UNSTABLE (control collapses too) |
| 0.755 | 0.7509 | no collapse; mean 0.7264 (-0.0246 against eq) | no collapse; mean 0.7247 (-0.0262) | STAYS, D = +0.0016 / STABLE |

Bracket by the rule: y_lo = 0.680, y_hi = 0.755, valid (no UNDECIDED member between,
monotone). **The stability threshold on cells of M/8 with 10^4 particles is bracketed
between y_c = 0.680 and 0.755** [VERIFIED by run core-20261123-020318-e952741, under the
rule as written]. The turning point y_c* = 0.6796 lies 0.0004 below the bracket.
Caveat named before the runs: the late swings of the 0.755 pair are about +-0.03 (member
minus control +0.02 near 285 M, -0.03 at 300 M; panel b), so a 100 M mean can move by
about 0.01; D = +0.0016 lies 0.008 inside the STAYS border.

Predictions:
- P1 HOLDS: 0.605 member collapses, t_c = 180.5 M in (120, 300); its control does not
  collapse at all.
- P2 PARTLY REFUTED: 0.755 member STAYS (|D| = 0.0016), no collapse in either run; but
  the control's 200-300 M mean lies 0.026 below its equilibrium, beyond the 0.01
  predicted from Track C's M/8 King controls (0.002-0.004). The drift is inward (lapse
  down), the same in member and control, so it is the mesh or the particle noise, not
  the kick [JUDGEMENT]; its cause is not tested.
- P3 REFUTED: the 0.680 member collapses (t_c = 219.5 M), and so does its control
  (251.5 M). On this mesh the model just above the turning point is unstable to the
  particle noise alone; the threshold of the discretised system lies above y_c*
  [JUDGEMENT: a model 0.0004 from a marginal point would grow slowly; collapse within
  260 M from noise points to a threshold noticeably above 0.680, not located yet].
- P4 HOLDS: 2255-2280 s of card time per run to 300 M (athena "cpu time used", chain
  logs), 7.5-7.6 s per M, 0.63 card-hours per run, 3.8 card-hours for the six; each run
  fitted one segment.

### Next level: three models with their controls, predictions before any run (02:05Z)

Design [JUDGEMENT, written now]: the rule names one next point, the midpoint 0.7175.
Card time is not the scarce resource this week, sessions are (decision 0026 item 6,
weekly window near its end); so the two points of the level after it, 0.69875 and
0.73625, run at the same time, each with its control: six chains, the same deck, seed,
particle number, kick and executable as level 1 (`verify/row4/st_m8.athinput`, release
card build `.work/build_gpu_v06/src/athena`, 300 M, `--gpu-hours 2.0` each: 12
card-hours asked at most, about 3.8 expected). Each member is classified by the same
rule; the bracket after this round is formed from all six models of levels 1 and 2 with
the same validity test (monotone, no UNDECIDED member inside). Two jobs eligible, the
other four held and released by `verify/row4/sequencer.sh` (stop file and log under
`scratch/core/tmp/lead_b10a/`). Order: 0.7175 member, 0.7175 control, 0.69875 member,
0.69875 control, 0.73625 member, 0.73625 control.

- P5. 0.69875: the member collapses within 300 M, t_c between 200 and 300 M (later than
  0.680's 219.5 M). Refuted by no collapse of the member (then the threshold lies below
  0.69875, within 0.019 of the turning point).
- P6. 0.73625: member STAYS (|D| <= 0.01), neither run collapses. Refuted by a collapse
  or |D| > 0.01.
- P7. 0.7175: no prediction of the side (it is the open middle); predicted only that it
  does not collapse before 0.69875's member if both collapse, and that the outcome is
  monotone in y_c over the five models 0.680-0.755. Refuted by a non-monotone outcome
  (a STABLE model below an UNSTABLE one).
- P8. Controls without collapse drift inward as at 0.755: their 200-300 M mean lies
  0.01 to 0.04 below their equilibrium alpha_c. Refuted by an upward drift or one beyond
  0.04.
- P9. Cost: 7.3 to 8.0 s of card time per M, 0.61-0.67 card-hours per run, one segment
  each. Refuted by more than 9 s per M.

### What was queued (02:05Z)

- Initial data: run core-20261123-020409-4fae8fb (`make_row4.py --yc 0.69875 0.7175
  0.73625`): alpha_c = 0.7029, 0.7186, 0.7346; R/M = 6.828, 7.136, 7.491; turning point
  unchanged (y_c* = 0.6796, E_b/M_0 = 0.036058). Directory tags are rounded to three
  digits (yc0p699, yc0p718, yc0p736); the files carry the exact y_c.
- Six chains with `nrpic-run submit --launcher chain --gpu-hours 2.0 --exe
  .work/build_gpu_v06/src/athena` (12 card-hours asked at most):

| Model | Run id | First job |
|---|---|---|
| 0.7175 member | core-20261123-020450-7e42037 | 4923 (eligible) |
| 0.7175 control | core-20261123-020452-e635a8e | 4924 (eligible) |
| 0.69875 member | core-20261123-020454-8fec6b2 | 4925 (held) |
| 0.69875 control | core-20261123-020456-884f550 | 4926 (held) |
| 0.73625 member | core-20261123-020458-dfc38d7 | 4927 (held) |
| 0.73625 control | core-20261123-020500-9b192cd | 4928 (held) |

  Sequencer pid 3075029 (setsid nohup; a copy of `verify/row4/sequencer.sh` with its stop
  file moved to `scratch/core/tmp/lead_b10a/sequencer.stop`; log
  `scratch/core/tmp/lead_b10a/sequencer.log`) releases 4925-4928 in that order. At 02:05Z
  seven jobs of other owners were ahead in the queue. P5-P9 open.

### Answers to the inbox (02:08Z; no AthenaK source change)

- Track A, `periodic-gamma-driver-step` (acknowledged in batch 8): answered in outbox
  20261123T020802Z. (i) gauge speeds in the step limit stay W31 for core-v0.7; the rule of
  decision 0027 item 2 holds meanwhile; `LightSpeedTimeStep` counts only the light speed
  [VERIFIED by reading z4c_newdt.cpp at HEAD]. (ii) accepted, no date (with W24/W30).
  (iii) done this session (footer test above); W31 row updated in REQUESTS_WAVE3.md.
- kb, `paper-code-links-tests` (message 105): answered in outbox 20261123T020802Z. Item 3
  confirmed by reading the source: the paper's identity is `dep_sum` of
  NrpicDepositSources (nrpic.cpp:1179-1180) written by NrpicWriteHistory
  (nrpic_io.cpp:289); NrpicWriteConservation returns on refined meshes (nrpic_io.cpp:662,
  :665). Item 4 confirmed: `<z4c> nco` is read nowhere in athenak/src (only a local
  variable in restart.cpp:154-306); the deck line stays for now because the deck's sha256
  is in the manifests of the paper's runs. Candidates offered [JUDGEMENT]: M25 and M20 the
  dust-collapse runs, M18 the id_solver tests T1 and T3 (the `code` monitor after the
  solve, 1e-11 to 1e-12), M19 stays claimed, M24 Track A's periodic_diag runs.

### Close of session core-lead-10a (2026-11-23T02:15Z)

Done: six row-4 chains closed and judged (bracket 0.680-0.755 on M/8, run
core-20261123-020318-e952741); level 2 queued (six chains, 12 card-hours asked, two
eligible, sequencer pid 3075029); note rebuilt (core-20261123-020543-eb1cd2a, 9 pages,
checker clean, pages read); stage G2 OPEN/CHECKLIST, verify (FAIL only on the six queued
chains and on main's two new commits, merged after) and report rerun; cpu_run.sh footer
fixed with a stub test; answers to A and kb posted, kb's message acknowledged. G2 not met.
Faults of mine on record: the first journal header of this session carried the date of
the shell's local time (2026-11-22) with a UTC hour; corrected to 2026-11-23T01:50Z
before the commit. Not done: inbox messages 1-8, 103 and D's new 11 (task scope).

## 2026-11-24T12:51Z (2026-11-24 04:51 PST), batch 11, session core-lead-11 (analysis round; no AthenaK source change)

Task: close the six level-2 chains of row 4 on M/8 (all DONE at tlim 300 M in one segment
each, jobs 4923-4928, by `submit_chain.sh --status`), classify by the rule of
2026-11-21T20:26Z, say whether the threshold is bracketed, queue the next level
(release card executable of core-v0.6, at most twelve card-hours, two jobs eligible);
note, G2 stage, answers to Track A (step limit) and kb (paper-code links), and the
outcome of T5 of branch core/noise-level2 (Track E's card smoke). Sequencer of batch 10a
(pid 3075029): released 4925-4928 by 06:08Z on 2026-11-23 and exited at 06:09Z ("all
jobs released"); nothing of core was queued at the start of this session.

### Outcomes of row 4 on M/8, level 2 (2026-11-24T13:01Z): fates by the rule of 2026-11-21T20:26Z

Six chains closed (`nrpic-run finish`, one segment each). Fates of all six models of
levels 1 and 2: run core-20261124-130055-9fc9901 (`verify/row4/row4_fate.py`, as of commit
9fc99012: same rule; it now colours by y_c and joins continuations; figure
`fig_row4_m8.png` looked at: panel (a) shows member and control of every model falling
together from 0.680 to 0.7175, the collapse later the larger y_c, and the 0.73625 and
0.755 pairs dipping to 0.86-0.93 of their equilibrium lapse near 270 M and coming back;
panel (b) shows member minus control inside +-0.035 for 0.7175, 0.73625 and 0.755).

| y_c | alpha_c eq | member | control | class / side |
|---|---|---|---|---|
| 0.605 | 0.6281 | t_c 180.5 M | no collapse (moves outward) | COLLAPSE / UNSTABLE (level 1) |
| 0.680 | 0.6875 | t_c 219.5 M | t_c 251.5 M | COLLAPSE / UNSTABLE (level 1) |
| 0.69875 | 0.7029 | t_c 244.25 M (lapse < 0.3), first AH 252.0 M | t_c 259.75 M, first AH 264.0 M | COLLAPSE / UNSTABLE |
| 0.7175 | 0.7186 | t_c 294.25 M (lapse < 0.3; no AH by 300 M) | t_c 293.5 M (lapse < 0.3; no AH by 300 M) | COLLAPSE / UNSTABLE |
| 0.73625 | 0.7346 | no collapse; mean 200-300 M 0.6930 (-0.0416 against eq) | no collapse; mean 0.6916 (-0.0430) | STAYS, D = +0.0014 / STABLE |
| 0.755 | 0.7509 | no collapse; mean 0.7264 | no collapse; mean 0.7247 | STAYS, D = +0.0016 / STABLE (level 1) |

Bracket by the rule: y_lo = 0.7175, y_hi = 0.73625, valid (monotone, no UNDECIDED
member inside); next midpoint 0.726875. **On cells of M/8 with 10^4 particles the
threshold of collapse within 300 M is bracketed between y_c = 0.7175 and 0.73625**
[VERIFIED by run core-20261124-130055-9fc9901, under the rule as written]. The turning
point y_c* = 0.6796 lies 0.038 below the bracket.

Predictions of 2026-11-23T02:05Z:
- P5 HOLDS: the 0.69875 member collapses at 244.25 M, inside (200, 300) and later than
  0.680's 219.5 M.
- P6 HOLDS: the 0.73625 member STAYS (|D| = 0.0014), neither run collapses.
- P7 HOLDS: the 0.7175 member collapses (294.25 M) after the 0.69875 member (244.25 M);
  the five models 0.680-0.755 are monotone (UNSTABLE 0.680, 0.69875, 0.7175; STABLE
  0.73625, 0.755).
- P8 REFUTED (just): the only control without collapse at level 2, 0.73625, has its
  200-300 M mean 0.0430 below its equilibrium, beyond the bound 0.04 written; the drift is
  inward as predicted. With 0.755 (0.026) the drift grows towards the bracket.
- P9 HOLDS: 2258-2280 s of card time per run to 300 M (athena "cpu time used" of the
  chain logs), 7.53-7.60 s per M, 0.63 card-hours per run, 3.8 for the six; one segment
  each.

What else the runs show (read from the same histories; supplement of the fate run,
`windows_50M` in its `row4_fate.json`):
- Near the bracket the kick no longer matters: at 0.7175 member and control collapse
  0.75 M apart; at 0.69875 15.5 M apart, at 0.680 32 M apart. The controls' collapse
  times rise with y_c (251.5, 259.75, 293.5 M).
- The stable pairs drift inward steadily, member and control alike. Means of
  alpha_c / alpha_c^eq over 50-M windows from 0 to 300 M: 0.73625 member 0.9997, 0.9968,
  0.9855, 0.9696, 0.9532, 0.9333 (control 1.0039, 1.0054, 0.9911, 0.9685, 0.9485, 0.9343);
  0.755 member 1.0000, 0.9966, 0.9899, 0.9821, 0.9711, 0.9638 (control 1.0033, 1.0029,
  0.9922, 0.9769, 0.9663, 0.9640). The 0.7175 pair stood at 0.95 over 175-200 M and at
  0.91-0.93 over 200-250 M before it ran away; the 0.73625 pair stands at 0.933 over
  250-300 M.
- So the bracket of the rule may be set by the 300-M window rather than by a stability
  threshold: a model that drifts inward at a steady rate reaches the runaway later the
  larger its y_c [JUDGEMENT; not tested yet: no run longer than 300 M exists on this
  mesh]. Level 3 is designed to test exactly this (below).

### T5 of branch core/noise-level2: card smoke run by Track E (read 2026-11-24T12:56Z)

Track E ran core's pending card smoke T5 of `<scalar_field> noise_level = 2` through its
sequencer (decision 0031 item 3): batch T5SMK, run E-20261123-035724-b661081, branch card
executable `scratch/core/exe/core_noise-level2/athena_gpu` (source 6ca93cba), six 64^3
decks (core's four of `card_t5.list` byte for byte, plus sr64_l1m and usr64_l0m with
`noise_rmodes_dump`); check SMOKECHK, run E-20261123-090718-6203c87 (`verdict.json`,
`smoke_check.png` in its directory; the figure looked at: card/processor differences of
rms and means against cycle, the six rms(phi - <phi>) curves on top of each other, wall
per cycle). Verdict PASS:
- all six exit 0 and reach tlim (SR t = 8.44 in 344 cycles, USR 10.5 in 428), records
  finite, dumps 9 of 9 and 22 of 22, `.rmodes` 9 and 22 where asked;
- card against core's processor run core-20261123-030705-6b6a4bd over cycles 0-30: box
  means within 1.7e-13 relative, rms(phi - <phi>) and rms(Pi - <Pi>) within 2.0e-11
  (E's bands 1e-12 and 1e-7 held);
- wall per cycle, level 2 over level 0: SR 1.156, USR 1.136. Core's T5 prediction
  (JOURNAL-noise-level2.md on the branch, entry 1: completes, finite; level 2 costs +5
  to +20 per cent at 64^3) HOLDS on the card; on processors it had been refuted on the
  low side (1.027, 0.992, entry 4).
- E's preview at the end of the 64^3 runs: SR level 2 against level 1 on the mesh 1.5e-6
  relative (E's bar 1e-4), USR level 2 against level 0 on the mesh -6.4e-6 (bar 1e-2).
After it E ran the six 256^3 ablation runs with the branch executable: five completed;
AL2S (E-20261123-152119-38957ba) was cut at t = 7.53 of 8.5 by its segment cap after a
preemption (every segment exit 0, the third segment refused by MAX_SEGMENTS = 2; chain
`events.log`), not by a fault of the executable; E's package repro/continue continues it.
T5 is closed. Still open on that branch: the Fable review of its diff (running beside this
session in worktree wt/core-s2; not touched), and the card cost at 256^3 (E's runs carry
it).

### Level 3 of row 4 on M/8: design and predictions (2026-11-24T13:05Z, before any run)

Design [JUDGEMENT, written now]. The rule names one next point, the midpoint 0.726875,
with its control. The question the level-2 runs raise is whether the "STABLE" side holds
beyond the window of the rule. Level 3 therefore runs:
- A. 0.726875 member and control from t = 0 to 600 M (tlim 600; the same deck, seed,
  particle number, kick and executable as levels 1 and 2). Classified by the rule exactly
  as written (it reads t <= 300 M only); 300-600 M is a supplement.
- B. The 0.73625 member and control continued from their 300-M restart files
  (`rst/st.00015.rst` of core-20261123-020458-dfc38d7 and -020500-9b192cd) to 600 M, in new
  run directories, with the same release card executable (wrapper
  `verify/row4/athena_resume.sh`: the first segment starts with `-r <restart>`).
- C. The 0.755 member and control continued the same way (core-20261121-204232-f74c942,
  -204237-ae00ca2) to 600 M.
Each chain `--gpu-hours 1.97` (two segments of 59 min): 11.82 card-hours asked, about 5.1
expected (P15). Two eligible, four held, released by `verify/row4/sequencer.sh` (stop file
and log under `scratch/core/tmp/lead_b11/`). Order: 0.726875 member, 0.73625 control
continued, 0.726875 control, 0.73625 member continued, 0.755 control continued, 0.755
member continued. The fates of all models are then read with the same script, the
continuations joined to their first parts (`<dir>+<continuation dir>`).

Predictions:
- P10. 0.726875 by the rule: neither run collapses by 300 M (the controls' collapse times
  rose 33.75 M over the last 0.01875 in y_c, so at least about 16 M more over 0.009375:
  310 M or later); |D| <= 0.01, the member STAYS, the model is STABLE, and the bracket
  becomes (0.7175, 0.726875). Refuted by a collapse of either run at or before 300 M.
- P11. 0.726875 beyond 300 M: member and control both collapse between 300 and 420 M,
  within 30 M of each other. Refuted by no collapse by 600 M, by a collapse after 420 M,
  or by collapse times more than 30 M apart.
- P12. 0.73625 continued: member and control both collapse between 320 and 500 M (their
  250-300 M level, 0.933 of the equilibrium lapse, is where 0.7175 stood about 50-75 M
  before its runaway; the drift has not slowed). Refuted by no collapse by 600 M (the
  drift stops and 0.73625 is stable over twice the window), or by a collapse before 320 M.
- P13. 0.755 continued: no collapse before 450 M, and the drift goes on: the 400-450 M
  mean of alpha_c / alpha_c^eq lies at least 0.01 below the 250-300 M mean (0.9638
  member, 0.9640 control) in both runs. Whether it collapses by 600 M is not predicted.
  Refuted by a collapse before 450 M, or by a 400-450 M mean less than 0.01 below the
  250-300 M mean in either run.
- P14. The continuations join their first parts without a jump: the central lapse of the
  continuation's first record at or after 300 M differs from the first part's record at
  300 M by less than the largest change between consecutive records over 280-300 M of
  the first part. Refuted by a larger jump (a restart that does not carry the state).
- P15. Cost: 7.5 to 7.7 s of card time per M: the two 600-M runs 1.25-1.3 card-hours in
  two segments each, the four continuations 0.63-0.65 in one segment each, 5.0-5.3 in
  all. Refuted by more than 9 s per M.

What the outcomes would mean (written now): if P11 and P12 hold, the 300-M bisection
measures how long a model resists a common inward drift, not a stability threshold;
row 4 on M/8 is then reported as "collapse within 300 M bracketed between 0.7175 and
0.726875 (or 0.73625)", the drift becomes the open item of the row, and a criterion that
does not depend on the window is proposed to orch (the drift rate against cell size and
particle number). If P12 is refuted (0.73625 holds to 600 M), the 300-M bracket stands as
an estimate of the threshold with the window doubled.

### What was queued (2026-11-24T13:04Z)

- Initial data: run core-20261124-130236-68d4ee5 (`make_row4.py --yc 0.726875`):
  alpha_c = 0.7266, E_b/M_0 = 0.035258, R/M = 7.307 (inside the M/4 nest), turning point
  unchanged (y_c* = 0.6796, E_b/M_0 = 0.036058). Directory tag yc0p727; the files carry
  the exact y_c.
- Six chains, `--gpu-hours 1.97` each (two segments; 11.82 card-hours asked):

| Model | Run id | Parent (300-M restart) | First job |
|---|---|---|---|
| 0.726875 member, 0-600 M | core-20261124-130310-597d9ca | - | 5154 (eligible) |
| 0.73625 control, 300-600 M | core-20261124-130321-ed96d4d | core-20261123-020500-9b192cd | 5155 (eligible) |
| 0.726875 control, 0-600 M | core-20261124-130340-31cf5e8 | - | 5156 (held) |
| 0.73625 member, 300-600 M | core-20261124-130347-7d6a10d | core-20261123-020458-dfc38d7 | 5157 (held) |
| 0.755 control, 300-600 M | core-20261124-130356-d9d09bf | core-20261121-204237-ae00ca2 | 5158 (held) |
| 0.755 member, 300-600 M | core-20261124-130406-09319a0 | core-20261121-204232-f74c942 | 5159 (held) |

  The 600-M runs use the release card executable directly; the continuations use
  `verify/row4/athena_resume.sh` (same executable, copied as chain/nrcr-<hash>, sha256
  checked; its restart file and `.prt` are inputs of the manifest with their checksums).
  Sequencer pid 3904230 (setsid nohup; copy of `verify/row4/sequencer.sh` in
  `scratch/core/tmp/lead_b11/`, stop file `scratch/core/tmp/lead_b11/sequencer.stop`, log
  `sequencer.log` there; it now logs every 15 min why the next job waits) releases
  5156-5159 in that order. At 13:04Z seven jobs of other owners were pending ahead.
  P10-P15 open.

### Stub test of the resume wrapper (2026-11-24T13:09Z; not a registered run: a shell test with /bin/echo, no simulation)

Prediction: a copy of `verify/row4/athena_resume.sh` with REAL=/bin/echo (and its sha256)
prints, in a run directory without `rst/*.rst`, `-r <restart> -d ... -t ... time/tlim=600`
(the `-i <deck>` pair replaced, `nrpic_resume=` removed), and with an own restart file
present the arguments unchanged except `nrpic_resume=` removed; it copies the binary to
`chain/nrcr-<hash>`. Refuted by any other argument list. Outcome
(`scratch/core/tmp/lead_b11/wraptest/`): exactly that, both cases; `chain/nrcr-12bf4aa7`
written. Held. The first card segments of the four continuations will show the same
line in their logs.

### Note, stage, answers (2026-11-24T13:30Z-14:10Z)

- Working note rebuilt by run core-20261124-133602-3e31713 (`run_all.py`): Fig. 5 now shows
  levels 1+2 in units of the equilibrium lapse (one colour per model from a sequential map;
  crosses at the collapse times) and, in panel (b), the two models without collapse with
  50-M window means (the drift); 20 new ledger rows (134 in all); 37 inputs sha256 ok, 31
  without a recorded checksum (wave-1, unchanged). Section III D rewritten: the bracket
  of collapse within 300 M, then why it may be set by the window, and what level 3 tests;
  abstract and summary follow; the abstract carries no mathematics now (checker item
  2.5). Compiled (10 pages), checker clean on references, citations and overfull boxes;
  pages 1, 4, 5, 7-9 read. A LaTeX error on the first preview (a caret in two ledger
  descriptions) was fixed before the registered run.
- The note scripts now default their output to `note/` when called without OUTDIR: the
  stage verify calls them without arguments, and in batch 10a it was run with
  `--no-rerun`, so the rerun check had never passed (four IndexErrors in this session's
  first verify). Fault of mine on record: writing the new `note/.gitignore` with printf
  replaced the existing one (LaTeX patterns); restored in the next commit.
- Stage G2: OPEN.md item 2 (level 2, the drift, level 3) and item 4 (open chains),
  CHECKLIST C1 and C7; collect (18 items kept), verify, report.
- Outbox 20261124T130733Z to Track A: W31 (gauge speeds in the step limit, warnings for
  the bound and for lapse_leak x dt) is written this batch by core's source slot
  "step-limit" with A's reproducing inputs as its tests; that slot posts the executable
  itself; rule cfl <= 0.6 meanwhile. Outbox 20261124T130734Z to kb: correction of core's
  answer of 2026-11-23 on link M18. The monitor after the solve cannot test the factor of
  the matter term, because in mode `code` the solver drives the very residual the monitor
  reads (F = -(psi^5/8) H, nrpic_idsolve.cpp:994-996, H from ADMConstraints with
  `-16*M_PI*tmunu.E` at z4c_adm.cpp:486) [VERIFIED by reading the source]. The test that
  depends on the factor is id_solver T1 in mode `code`: psi converges at second order to
  the continuum solution with the right matter term (-1.92e-2, -5.22e-3, -1.33e-3 at
  dx = 1, 0.5, 0.25). Fault of mine on record: the argument of batch 10a was wrong.

### Close of session core-lead-11 (2026-11-24T14:20Z): PAUSED

The pause flag `locks/PAUSE` was found at 14:19Z; nothing new was started after it.
Done: six level-2 chains closed and judged (collapse within 300 M bracketed between
y_c = 0.7175 and 0.73625, run core-20261124-130055-9fc9901; the surviving pairs drift
inward steadily, so the bracket may be set by the window); level 3 queued with
predictions P10-P15 (six chains, 11.82 card-hours asked, jobs 5154/5155 eligible,
5156-5159 held, sequencer pid 3904230); T5 of core/noise-level2 recorded (PASS on the
card, Track E's check); note rebuilt (core-20261124-133602-3e31713, 10 pages); stage G2
collect, verify (rerun PASS for the first time; runs FAIL only on the open chains), report;
outbox to A (W31 in work) and kb (M18 correction). Where I stopped: nothing half-done;
the next session reads level 3 with the commands in HANDOFF.md. G2 not met.
Faults of mine on record: the argument for M18 of batch 10a (corrected); the overwritten
note/.gitignore (restored); two wait loops of mine matched their own command line with
`pgrep -f` and never ended (stopped by their task ids, no process killed by pattern).
Not done (task scope): inbox messages 1-10.

## 2026-11-24T21:05Z (2026-11-24 13:05 PST), batch 12, session core-lead-12 (card runs into the shared queue; no AthenaK source change, no analysis)

Task: hand core's waiting card runs to the shared queue (decision 0033 items 1-7;
harness/RULES.md, section "Shared card queue"; orch outbox 20261124T201500Z and
20261124T210500Z). Sequencer pid 3904230 was stopped by orch at 12:00 PST (20:00Z); its log
`scratch/core/tmp/lead_b11/sequencer.log` ends at 19:49Z with 5156-5159 still held.

State of the six level-3 chains of row 4 on M/8 (sacct from 2026-11-24T04:00 PST;
`submit_chain.sh --status`):

| Run id | Model | What happened | Own restart |
|---|---|---|---|
| core-20261124-130310-597d9ca | 0.726875 member, 0-600 M | job 5154 ran 37:45 (10:39-11:17 PST) to t = 287.5 M, PREEMPTED; resubmission 5182 CANCELLED at 11:57 PST | rst/st.00014.rst (t = 280 M) |
| core-20261124-130321-ed96d4d | 0.73625 control, 300-600 M | job 5155 ran 57 s (300 -> 306.5 M), PREEMPTED; resubmission 5189 CANCELLED | none |
| core-20261124-130340-31cf5e8 | 0.726875 control, 0-600 M | job 5156 held, CANCELLED, never ran | none |
| core-20261124-130347-7d6a10d | 0.73625 member, 300-600 M | job 5157 held, CANCELLED | none |
| core-20261124-130356-d9d09bf | 0.755 control, 300-600 M | job 5158 held, CANCELLED | none |
| core-20261124-130406-09319a0 | 0.755 member, 300-600 M | job 5159 held, CANCELLED | none |

Decisions [JUDGEMENT]:
- 597d9ca had computed 37 min and holds its own restart at 280 M: it is CONTINUED IN PLACE
  (not closed), through the queue with `--cmd` and a new wrapper
  `verify/row4/continue_chain.sh` (one `submit_chain.sh` start on its own directory, the
  chain's registered settings, MAX_SEGMENTS = the registered 2; segment 1 is used, so one
  more segment of 50 min; 320 M left at 7.55 s/M of segment 1 is about 40 min).
- ed96d4d computed 6.5 M and wrote no restart file of its own; continuing it in place would
  start again from the parent's 300-M restart and append a second copy of 300-306.5 M to
  its history files. It is closed as stopped and run again as a new registered run with
  the same arguments, which starts from that same newest restart (the parent's
  rst/st.00015.rst). Its 26 history rows stay on record in its directory.
- The four held runs never ran: closed as stopped (`nrpic-run finish --status stopped`,
  commits dc9e210f..a58b5692) and queued again with the arguments they were registered with
  (`--launcher chain --gpu-hours 1.97 --exe ...`; the continuations `--exe
  tracks/core/verify/row4/athena_resume.sh` with the parent and its restart files as
  `--input`).
- Priority 2: the G2 stage package of core waits for these six (OPEN.md item 2; CHECKLIST
  C1, C7). No `--after`: the six are independent, and the order of adding is the plan's
  order (0.726875 member, 0.73625 control, 0.726875 control, 0.73625 member, 0.755 control,
  0.755 member). Predictions P10-P15 (entry 2026-11-24T13:05Z) stand unchanged; their run
  ids change for the five new runs (HANDOFF.md maps queue entries to models).

### Dry-run test of continue_chain.sh (prediction, 21:05Z; a shell test, no job, not a registered run)

Prediction: (a) `DRY=1 continue_chain.sh core-20261124-130310-597d9ca` prints one
`submit_chain.sh` line on that run directory with the deck
`tracks/core/verify/row4/st_m8.athinput`, the three overrides of its manifest, ATHENA_EXE =
the release card build of core-v0.6, JOB_NAME = the run id, PROC_NAME = nrc-f97a0e86,
MAX_SEGMENTS = 2, names rst/st.00014.rst as the restart it resumes from and one segment
left, and submits nothing (squeue unchanged). (b) Without DRY and without the dispatcher's
marker it refuses with a non-zero exit. (c) On ed96d4d it refuses (finished manifest, no
own restart). Refuted by any submission, by a different argument list, or by (b) or (c)
going through.

Outcome (21:06Z): (a) as predicted: one line, `env ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
JOB_NAME=core-20261124-130310-597d9ca MAX_SEGMENTS=2 PROC_NAME=nrc-f97a0e86 ATHENA_WALL=00:50:00
SLURM_TIME=00:59:00 CPUS=1 PARTITION=preempt MAX_OUTSIDE_KILLS=2 SLURM_EXTRA= CHECK_CMD=
scripts/submit_chain.sh <rundir> .../verify/row4/st_m8.athinput` with the three overrides of
the manifest; "resumes in place from .../rst/st.00014.rst (1 of 2 segments used, 1 left)";
exit 0; squeue of the account the same before and after (5206-5209, none of core); no
`continuations.log` written, events.log unchanged. (b) exit 3, "refused: not called by the
dispatcher". (c) exit 1, "manifest status is 'stopped'". Held. A first version failed
(a) and (b) with "squeue did not answer": `squeue -j 5182` exits non-zero for a job Slurm
no longer lists; the wrapper now reads the account's whole queue and matches the job id and
the job name. Fixed before any entry was queued.

Correction (21:10Z): the first commit of this entry (e9f87bf3) carried estimated clock times
for the prediction (21:10Z) and the outcome (21:14Z) and in the note of manifest 597d9ca
(21:15Z); the clock says prediction 21:05Z, test 21:06:07-21:06:20Z (squeue snapshots in
scratch/core/tmp/), commit 21:06:54Z. Corrected; fault of mine on record.

### Queue hand-over (21:08Z)

`harness/bin/nrpic-queue add` (script scratch/core/tmp/lead_b12/queue_add.sh; each `add`
checked its arguments with `nrpic-run submit --dry-run`): q0028 row4-l3-0p726875-member-cont
(`--cmd 'tracks/core/verify/row4/continue_chain.sh core-20261124-130310-597d9ca 2'`), q0029
row4-l3-0p73625-control, q0030 row4-l3-0p726875-control, q0031 row4-l3-0p73625-member,
q0032 row4-l3-0p755-control, q0033 row4-l3-0p755-member; all priority 2, waiting; the
account's queue was at 5 of 5 (jobs of B, C, D, F). Budget at 21:08Z: G2 used 15.76,
reserved 2.07, left 22.17 of 40.

### Close of session core-lead-12 (21:12Z)

Done: the six level-3 runs of row 4 are in the shared queue (q0028-q0033); five cancelled
runs closed as stopped; 597d9ca continued in place by the new wrapper (dry-run test held);
HANDOFF (queue ids beside the models, read commands), STATUS (card plan). Nothing
half-done; no run computed in this session; P10-P15 open. G2 not met.

## 2026-11-25T02:12Z (2026-11-24 18:12 PST), batch 14, session core-lead-14 (merge of four source branches, release candidate core-v0.7)

### State found

- `core/nrpic` at 16e4942a after `git merge main` (4f4e0e81, decision 0035), clean. No
  pause flag. `tracks/core/RELEASE-v0.7.md` does not exist: nothing of this task was
  done before.
- Branches offered (decision 0035 item 4) [VERIFIED `git log`, `git merge-base
  --is-ancestor core-v0.6 <branch>`, READY of each under `scratch/core/exe/`]:
  core/noise-level2 5c98beef (source 64f150ec, reviewed on Fable, holds core-v0.6; card
  run R5 = queue entry q0035, waiting), core/step-limit 3a9a3498 (source 5c4b644f,
  holds core-v0.6; card smoke run q0036, waiting), core/gauge-2 61c8fc4d (source
  984110c3, holds core-v0.6, closed on 2026-11-21), core/clump-table ff11719d (source
  7cc6c7b9, holds core-v0.5 and NOT core-v0.6, READY of 2026-11-21, worktree clean, no
  commit since). core/oblate: left out as the task says.
- core/clump-table, the card check M2 its READY names as outstanding: the run
  core-20261121-132629-47ccb97 (Slurm 4803) DID run on 2026-11-21 07:36 PST, status 0
  (`batch.list.status`), and nobody judged it: the branch has no entry after its
  publication. Its prediction M2 was written before the run (JOURNAL-clump2.md of the
  branch, session clump2-4, "The merged source: predictions M1, R5, M2"): first record
  equal to 1e-11; minimum lapse, sum m u_x, sum m W within 1e-9 at every common record
  to 50 M; refuted by a difference above 1e-6 within the first 10 M. I judge it now with
  the branch's own script (`analysis/clump2/compare_two_runs.py --a <M2>/v0.3 --b
  core-20261119-145433-8c4083d/v0.3`), before I decide on the branch. My own
  expectation [JUDGEMENT]: the refutation criterion (1e-6 in 10 M) is not met; the bound
  1e-9 to 50 M may fail, because two card runs of one executable do not repeat each
  other (atomic deposit) and 10^4 particles amplify that over 50 M. The branch is taken
  if the early criterion holds and nothing looks like a systematic offset.

### Review of the four diffs against core/nrpic (source of core-v0.6), as maintainer

core/noise-level2 (8 files, 833 added, 23 removed) [VERIFIED by reading the hunks of the
six existing files in full; of the new `scalar_field_noise_mesh.cpp` (545 lines) the
header, the option reader and the guards]:
- Hooks: `nvar_sf` replaces `nsf` in the allocation, the buffers, `CopyU`, the update;
  `nvar_sf = nsf` unless `MeshModeRequested(pin)`, which reads only parameters that
  exist and returns false unless `noise = mukhanov_sasaki` with `noise_mode_eq = mesh`
  or `noise_level = 2`. `NoiseMeshRHS`, `NoiseMeshInit`, `NoiseMeshCoefficients` are
  called behind `nopt.mesh_r`. Lockstep array: `+2` only with `bg_evolved`; the loop of
  `mode_scale` now ends at `4+4*nshell`, the same range as before when `bg_evolved` is
  off. `NoiseSynthesize` gets a branch on `per_mode` inside its kernel: the released
  path is the else branch with unchanged arithmetic, but the kernel is recompiled, so
  only the byte comparison says that the bytes stay (the package: 13 scalar cases with
  restarts and 75 of 75 against core-v0.6).
- `noise_level = 2` used to stop the run ("not implemented"); now it runs. An input
  that set it had no released behaviour.
- Guards: refined mesh refused (`pm->multilevel`); one rank is the restriction of the
  scalar field itself; level 2 takes window, H, eps and kick factors from box means
  (uniform), and is tested only for a lapse that is uniform in space (1 and a(t)):
  with a lapse that varies in space, and with a shift, NOT tested (READY). These three
  go to OPEN.md. Accepted.

core/step-limit (15 files, 1071 added, 31 removed) [VERIFIED by reading every hunk of
`driver.cpp`, `main.cpp`, `z4c.cpp`, `z4c.hpp`, `z4c_newdt.cpp`, `term_signal.{cpp,hpp}`
and the function `GaugeStepLimit`; of the kernel `GaugeTimeStep` the header]:
- `dt_gauge` is read only if present; `GaugeStepLimit` is called at the end of
  `Z4c::NewTimeStep` in three dimensions and returns at once after its first call unless
  `dt_gauge > 0`. At the first call it evaluates the bound (one reduction over the
  cells, read-only) and prints at most two warnings on rank 0. It writes `dtnew` only
  inside `if (dt_gauge > 0 ...)`. So without the option: a log line or none, no change
  of the step. Under MPI one more `MPI_Allreduce` at the first call.
- SIGTERM: the handler sets two `sig_atomic_t` and nothing else; `Check()` is the last
  condition of the main loop (one `MPI_Allreduce` per cycle under MPI, a read of a
  flag otherwise); `Finalize` skips non-restart outputs and the problem generator's
  final function only if `Stopped()`; `main` returns 143 only then. A run that gets no
  signal executes the same statements on its data as before. Prediction below: no
  output file changes.
- `rst` outputs on the signal are written through the unchanged end-of-run path of
  `Finalize`, which already forces an off-schedule dump at the end of a run. Accepted.
- `scripts/submit_chain.sh`, `scripts/tests/test_submit_chain.py`, `scripts/README.md`:
  the package's 58 checks (run core-20261125-000640-5c4b644); I repeat the test script
  with the merged tree.

core/gauge-2 (3 files, 439 added, 3 removed; one source file) [VERIFIED by reading the
whole diff of `z4c_gauge_ext.hpp`]:
- `lapse_leak_hole` read only if present; `nhole = 0` without it or without trackers;
  the kernel takes the old statement `if (leak && !leak2)` and the weighted one only
  `if (leak2)`. The struct captured by the kernel grows by 26 reals and an int: the
  bytes of runs with `lapse_leak` are again a matter of the compiler (the package: L1
  17 of 17 files against core-v0.6, T7). My quick test repeats one case with
  `lapse_leak` on and the option absent against the release.
- It enters as a MITIGATION (decision 0025 item 3): its own 200 M vacuum run shows the
  horizon radius falling again after 110 M. Named so in changelog and OPEN.md.

core/clump-table (11 files, 1825 added, 3 removed) [VERIFIED by reading the hunks of
`nrpic_cf.cpp` and `nrpic_bowen_york.hpp`, the header and the reader of
`nrpic_clump_table.hpp`; `python/nrpic/boosted_cluster.py` not read]:
- `TClumpRead` skips every component without `comp<c>_boost_file`; then `tcl.n = 0`,
  `tcl.ncorr = 0`, both loops in the kernel are empty and `if (tcl.n > 0)` is false.
  `BYRead`: one more `continue` for a component that has a boost file. The kernel of
  `nrpic_cf` captures two more structs: bytes again by test (the package: R5, 50 files
  against core-v0.5; my regression has the set-ups os, c1, c2, c3, c5 of `nrpic_cf`).
- The branch does not hold core-v0.6: the merge brings its three source files onto a
  tree that has `id_solver2` (punctures of `nrpic_cf` in the solve). The one overlap is
  `clump_table_idsolve.athinput` (table clump under `id_solve`): with core-v0.6 the far
  field is on by default, so that example will not give the bytes of the branch
  executable. I run it for status and convergence only.

### Predictions (written before any merge or build)

- **R (byte regression, serial candidate against release core-v0.6
  `.work/build_cpu_v06/src/athena`, `regress_v04.py`, twelve set-ups, every new option
  absent).** 75 of 75 items identical; classes a, b and other empty. The three changes
  that act without an option touch no compared file: the start-up warning of the step
  limit goes to the log (the log is compared only in its result lines for jeans and
  binary, which have no Z4c); the SIGTERM handler does nothing without a signal; the
  chain script is not part of a run. Refuted by any item that is not identical: then
  either a hook is not inert or, as for core/z4c-faces in core-v0.6, the compiler
  contracted an unchanged kernel differently because of a header (candidates:
  `z4c.hpp` with three new members, `z4c_gauge_ext.hpp` with the larger struct,
  `scalar_field.hpp`, the kernel of `nrpic_cf`). Each branch passed 75 of 75 alone
  (noise-level2 core-20261124-142032-79291d0, step-limit core-20261125-000250-6dc7307,
  gauge-2 core-20261121-190715-f702a98); the four together have not been compiled.
- **Rm.** `athena_cpu_mpi` started without mpirun: 75 of 75 identical.
- **Ro.** `athena_cpu_omp` at one thread: every run status 0; not a byte reference;
  about 32 of 75 identical and the rest at rounding level (module histories 1.2e-15,
  constraint statistics 1.4e-10 east, 1.9e-12 c4: the numbers of core-v0.6). Refuted by
  a status that is not 0 or a difference above 1e-8 in a large column.
- **Qn (noise-level2).** `problems/scalar/sr_stochastic_l2.athinput` (32^3, level 2):
  every file byte-identical with `core_noise-level2/athena_cpu` (64f150ec).
- **Qs (step-limit).** (i) `problems/tests/z4c_step_limit.athinput`: every file
  byte-identical with `core_step-limit/athena_cpu`; the log names the limit. (ii) the
  same with `z4c/dt_gauge=0.0`: the warning in the log and the guard stop (exit status
  3), as the READY says (cycle 9). (iii) `problems/tests/term_signal_periodic.athinput`:
  a run signalled part-way exits with status 143, prints "Terminating on signal
  SIGTERM" and leaves one more restart file; continued with `-r` from that file it
  ends with a final restart file byte-identical with that of the run never signalled.
  Refuted by any other exit status, a missing restart file or a different final state.
- **Qg (gauge-2).** Coarse vacuum mesh (`problems/es/v1_small.athinput` without
  refinement, 10 M, Track D's slice): (i) with `lapse_leak_hole = 8`: every file
  byte-identical with `core_gauge-2/athena_cpu`; (ii) with `lapse_leak` on and the new
  option absent: every file byte-identical with release core-v0.6; (iii) (i) and (ii)
  differ (the weight acts).
- **Qc (clump-table).** One moving cluster at 32 cells, initial data only
  (`problems/tests/clump_table_static.athinput`, v = 0.3, curvature, correction): the
  history files and dumps byte-identical with `core_clump-table/athena_cpu` (a
  core-v0.5 source; nothing of core-v0.6 acts on `nrpic_cf` data without `id_solve`).
  `clump_table_idsolve.athinput`: status 0, the solve converges (max|H| below 1e-10);
  its bytes are NOT those of the branch executable (far field on by default since
  core-v0.6): no byte comparison.
- **C (the combination the merge creates).** The level-2 example with `<z4c> dt_gauge =
  0.9` added (the step limit evaluated on a scalar-field run in an expanding box):
  status 0; the start-up line of the limit in the log; history files byte-identical
  with Qn if the limit never sets the step, else the log names the sector. Either is
  acceptable; refuted by a non-finite history or a guard stop.
- **T (chain script).** `python3 scripts/tests/test_submit_chain.py` with the merged
  tree: every check passes (58 in the package's run).
- **K7 (card check of the merged card executable; NOT run in this session: handed to
  the shared queue).** Every case of the list ends with status 0; the fifteen cases of
  core-v0.6 meet K6 of that release (`card_v06.py`, `card_v05.py`); the new cases agree
  with the processor runs of the quick test: level-2 histories and mode files within
  1e-9 (no deposit: only rounding of the reductions), the step-limit example with the
  same number of cycles and the constraint history within 1e-7, the clump-table and
  gauge cases within 1e-7 in every large history column.

### K7 amended before the card entry was queued (03:01Z; nothing of it has run)

Writing the judging script (`analysis/release/card_v07.py`) I saw that two bounds of K7
as first written do not fit what the cases measure, and changed them before queueing:
- `s_lim` (flat space with noise of 1e-10 on every field): its one history measures
  the noise, and rounding of 1e-16 of a field of order one is 1e-6 of that. The bound
  is 1e-3 on the large columns of `flat.z4c.user.hst`, with the same number of records
  (growth at the grid scale against decay differs by orders of magnitude, so 1e-3
  still discriminates). The first text said 1e-7.
- level 2 (`n_l2`, `x_l2dt`): 1e-9 holds for `sr.sf.hst` and for the per-mode records
  `*.rmodes` (relative to their largest entry); `sr.sf.con.hst` (constraint means, in
  part differences of rounding-level numbers) is reported and not bounded.
The other cases as written: `g_hole`, `x_holedt`, `c_static`, `c_solve` within 1e-7 in
`*.nrpic.hst` and `*.z4c.user.hst`; `c_solve` with the same number of outer iterations
and psi_max to 1e-12. The fifteen cases of core-v0.6 by `card_v06.py` (against the
processor runs of core-20261121-130813-710b3cc and core-20261121-131250-f8df905: decks
unchanged; the processor data are those of the core-v0.6 candidate, to which this
candidate is byte-identical where the regression compares) and `card_v05.py`. The script
was tried by hand on processor data in place of card data (CARD PASS, which says nothing
about the card) and with the first-pass run in place of `g_hole` (CARD FAIL at 8.8e-2).

### Outcomes (03:10Z)

Merges, one commit per branch, no conflict: da904f55 (noise-level2), 76ac67a2
(step-limit), 31ae23e6 (gauge-2), 5f75e5b9 (clump-table) = the source commit. Builds:
serial 312 s, MPI 326 s, threaded 382 s, card 1065 s, three jobs each, two at a time.

- **M2 of core/clump-table (judged before the merge): HELD, and my expectation was
  wrong.** Run core-20261125-021225-382dbc7: over 401 common records to 50 M the two
  card runs (merged build of 2026-11-21, build before the merge of 2026-11-19) differ by
  at most 3.3e-15 in the minimum lapse, 2.2e-16 in sum m u_x, 1.1e-15 in sum m W; the
  constraint norms agree in every printed digit. I had written that the bound 1e-9
  might fail because card runs with deposition do not repeat; this pair repeats to
  rounding of the printed sums. (The histories hold sums and norms, not the particle
  state: the statement is about them.) Figure looked at; its legend covers curves.
- **R: HELD.** Run core-20261125-023046-30aba6c: 75 of 75 items identical with release
  core-v0.6, classes a, b, other empty. No file differs because of the three changes
  that act without an option. The four recompiled kernels I named as candidates for a
  different contraction (`z4c.hpp`, `z4c_gauge_ext.hpp`, `scalar_field.hpp`, `nrpic_cf`)
  wrote the released bytes. Figure core-20261125-030148-94dcc0b looked at.
- **Rm: HELD.** core-20261125-023646-eca713c, 75 of 75.
- **Ro: HELD.** core-20261125-025505-10f6611 (the driver reports FAIL, as it must for a
  build that is not a byte reference; every AthenaK run status 0), judged in
  core-20261125-030151-8c0c306: 32 of 75 identical; module histories within 1.2e-15,
  constraint statistics 1.1e-10 (east) and 6.0e-12 (c4). The last two are not the
  numbers of core-v0.6 (1.4e-10, 1.9e-12) that I had written as "about": same order,
  different bytes of the threaded build. Figure looked at.
- **Qn, Qs, Qg, Qc, C, T: HELD**, run core-20261125-023641-7a1c47d (QUICK PASS, 28
  expectations): 65 of 65 files identical in the five byte comparisons (8, 33, 9, 9, 6);
  s_off stops at cycle 9 with exit status 3 after the warning; S1 and S2 of
  `term_test.py` (26 checks) with status 143 and a restart file 0.28 s and 0.35 s after
  the signal; g_hole and g_leak differ in 7 of 9 files; c_solve converges in 25 outer
  iterations to max|H| 2.0e-12; x_l2dt writes the histories of n_l2 (the limit never
  sets the step); x_holedt finite; chain test 58 checks. Two things seen that no
  prediction covered: (i) with geodesic slicing and zero shift the start-up line of
  `dt_gauge` prints 1.73304e+39 for the two sectors that are not evolved (the largest
  float over the cell): cosmetic, OPEN.md item e; (ii) S2 shows both restart defects of
  the step-limit package with the merged build (`tsq.cons.hst` lacks the record at
  t = 1.6875 in the continued run; header lines of `*.z4c.user.hst` 2 against 4): OPEN.md
  items a and b. Figure looked at (panel b is crowded).
- **K7: NOT RUN.** Queue entry q0039 (`core-v07-card`, priority 2, 0.3 card-hours asked),
  added 03:02Z after the amendment above; not waited for. Commands that judge it:
  `tracks/core/RELEASE-v0.7.md`, section "Card checks pending".

Found while writing the changelog, not tested by a run [VERIFIED by reading
`git show core-v0.6:scripts/submit_chain.sh` 268, 282]: the chain script of core-v0.6
takes status 143 together with a line "Terminating on" for a failure, so a chain started
with that script and an executable of core-v0.7 ends FAILED when the executable is
signalled from outside the job. The script of this release handles it (scenario M of its
test). Written into the changelog (run scripts, item 5), READY and OPEN.md item g.

Not done: the capability tests of the four packages were not rerun on the merged
executables; nothing ran on several ranks or on a card; core/oblate was not looked at
beyond its tip. Card time of this session: none. Processor time: builds about 35
core-minutes of wall on 3 jobs each; runs about 45 minutes on 3 cores.

Published: `scratch/core/exe/core_nrpic_v07/` (four executables, COMMIT, SHA256SUMS
checked with `sha256sum -c`, READY, branches/). Written: `RELEASE-v0.7.md` (first line
REGRESSION PASS), changelog section core-v0.7, OPEN.md section core-v0.7, drivers
`analysis/release/{quick_v07.py,card_v07.py,card_v07.list}`.

## 2026-11-25T11:52Z (2026-11-25 03:52 PST), batch 17, session core-lead-17 (no change of athenak/src or python/nrpic)

State at start: main merged (release core-v0.7 on main, tag on 5f75e5b9; merge b399f946;
decisions 0036-0038; batch-17 spec). Worktree clean. Queue: q0028 (job 5221, chain ended
FAILED "MAX_SEGMENTS=2 reached" after a second SIGTERM, at t = 405.25 M of 600) and q0029
(job 5274, DONE at 600 M) are done; q0030-q0033, q0035, q0036, q0039 wait (no card job of
core in squeue at 11:47Z: five jobs of A, B, D, F hold the cap). Pause flag absent.

### Predictions, written before the runs of this session (11:52Z)

- **M1** (queue marker out of the jobs; decision 0037 item 4). After the change of
  `scripts/{gpu_run.sh,gpu_batch.sh,submit_chain.sh,_athena_job.sh}` (every variable
  NRPIC_QUEUE_* removed at the top of each script, and from the environment `sbatch` and
  `srun` are called with), with NRPIC_QUEUE_DISPATCH=q9001:<token> set in the caller and,
  as a worst case, in the job's own environment: (a) no fake `sbatch` or `srun` call of
  gpu_run.sh (BATCH=1 and blocking), gpu_batch.sh and submit_chain.sh (start, and the
  resubmission from inside a job, after a wall-clock stop and after SIGTERM) sees the
  variable; (b) no fake executable sees it; (c) the chain still resubmits its own next
  segment (one sbatch per segment, chain DONE at its time limit); (d) the scripts as they
  were before the change (HEAD 65116a08) show the variable to sbatch and to the
  executable in the same set-up (the test can fail); (e) the 13 scenarios of
  `scripts/tests/test_submit_chain.py` keep their outcomes, and no sbatch call or
  executable of theirs sees the marker. Refuted by any sighting of the marker in (a),
  (b), (e), by a chain that does not resubmit or submits twice, or by (d) showing no
  marker (then the test proves nothing).
- **R7** (release processor build `.work/build_cpu_v07/src/athena` against the candidate
  `scratch/core/exe/core_nrpic_v07/athena_cpu`, `regress_v04.py`, twelve set-ups, 3
  cores): 75 of 75 items identical, as R6 for core-v0.6 (the trees of the tag 5f75e5b9
  and of main after merge b399f946 are the same: checked below). Refuted by one
  differing item. The release card build `.work/build_gpu_v07/src/athena` cannot run on
  processors (CUDA build); for it this session checks only that it was built from the
  same tree, and names its card check as not done.

### Outcomes (12:00Z-12:12Z)

- **M1: HELD.** (a)-(d): run core-20261125-120211-08f4fb9 (`scripts/tests/test_queue_marker.py`,
  fake Slurm of `harness/tests/rc_fixture.py`, TEST PASS, nine checks): with the marker
  in the caller (and, case E, in the job), gpu_run.sh BATCH=1 (sbatch 0/1, executable 0/1
  saw it), gpu_run.sh via srun (0/1, 0/1), gpu_batch.sh (sbatch 0/1, srun 0/2, runs
  0/2), the chain (sbatch 0/2 at start and at the hand-over inside the job, segments 0/2,
  STATUS DONE after two segments), in-job gpu_batch.sh and _athena_job.sh (executable
  0/1 each). Control (d): the scripts of 367021876 in the same set-up show the marker to
  sbatch 1/1 and 2/2 and to the executables 1/1 and 2/2, the chain's second job included
  (the leak of decision 0037 item 4, reproduced); so the test can fail. (e): run
  core-20261125-120145-665b6a0 (`test_submit_chain.py`, TEST PASS): the 13 scenarios keep
  their statuses and sbatch counts, and no sbatch call or executable of any scenario saw
  the marker. Figures `t/fig_queue_marker.png` and `fig_submit_chain.png` looked at (the
  marker figure's title says "orange" for a colour that renders red: cosmetic). Both runs
  registered BY HAND (`tracks/core/tools/hand_run.py`, CLAUDE.md rule 4): nrpic-run's local
  launcher refused the first attempt ("a local run may not submit Slurm jobs ... would run
  submit_chain.sh (in scripts/tests/test_submit_chain.py)"), although every Slurm program
  the tests reach is a fake on PATH. Before the registered runs, two unregistered tries
  under `scratch/core/tmp/` (the first failed its control because files written by `git
  show >` were not executable: the test now sets the mode itself).
- **R7: HELD.** Run core-20261125-115428-3670218: 75 of 75 items identical, classes a, b,
  other empty, REGRESSION PASS; figure run core-20261125-120456-07a671a looked at (twelve
  bars, one colour). The release card build was not run (CUDA build; no card job asked).
- **Card checks q0039, q0035, q0036: NOT RUN** (waiting in the shared queue at 12:10Z;
  five jobs of A, B, D, F held the cap). Nothing judged; no CLAUDE.md sentence sent.
- **Provenance of E's ablation executable** (no prediction was written for it: a check of
  identity, done before this entry was written; recorded as found): all seven run
  directories hold the copy that ran (`batch.list.exe`, `chain/athena` with
  `chain/nrc-*` the same inode), each hashing 468109496c82..., equal to
  `scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu`, source 6ca93cbabfe6; set 2 of
  the published directory (d7069a4e..., source 64f150ec) replaced it in place on
  2026-11-24 06:17 PST. Record: `tracks/core/EXE_PROVENANCE.md`, `PROVENANCE` and hard
  links `superseded/6ca93cba/` in the published directory (`sha256sum -c` OK); answer to
  E in the outbox.
- **Row 4, level 3, two of six runs** (fates run core-20261125-120724-246d2a5,
  `row4_fate.py` now takes a model whose control has not run; figure looked at: panel (a)
  shows the 0.726875 member falling at about 338 M and the 0.73625 control at about
  420 M, legend crowded over the curves):
  - P10: member part HOLDS (no collapse by 300 M; 250-300 M mean 0.8916 of its
    equilibrium lapse, its own 200-300 M offset -0.060); D and the model's side PENDING
    (control q0030).
  - P11: member part HOLDS (lapse < 0.3 at 338.25 M, AH 344.0 M, inside 300-420 M); the
    30-M pairing PENDING.
  - P12: control part HOLDS (0.73625 control: lapse < 0.3 at 421.25 M, AH 427.0 M, inside
    320-500 M; window means 0.9124, 0.830, 0.336 over 300-450 M); member PENDING (q0031).
  - P13: PENDING (q0032, q0033).
  - P14: HOLDS for the control's join: first continued record (300.25 M) 0.705611 against
    the parent's 0.706051 at 300 M, a jump of 4.4e-4 below the largest step 1.02e-3 over
    280-300 M.
  - P15: HOLDS on the rate: dcc9ea1 2263 s of card time ("cpu time used") for 300 M,
    7.54 s per M, one segment. The member 597d9ca did not reach 600 M: its chain (started
    with the chain script of core-v0.6) counted both preempted attempts and stopped at its
    cap at 405.25 M; closed as stopped, not continued (the collapse it was to show came at
    338.25 M). Its history holds 280.25-287.5 M twice (79 repeated times, one step back);
    `row4_fate.py` keeps the later records, as it does for continuations (the [TO VERIFY]
    of the batch-12 handoff).
  - Bracket by the rule: (0.7175, 0.73625), valid, 0.726875 pending inside. What the
    written meaning says (entry of 2026-11-24T13:05Z): P11 and P12 hold so far in their
    halves; a model on the STABLE side of the 300-M bracket (0.73625) collapses by 421 M
    in its control; so the 300-M bisection measures how long a model resists the common
    inward drift [JUDGEMENT; the full reading waits for q0030-q0033]. The note
    (`note/`, section III D, Fig. 5) is not updated: it waits for the complete level 3.
- NEXT_SOURCE.md written (items 1-3 for the Fable session: outputs that survive a
  restart; finder stopping rule and excision growth guard; figstyle without a date).

Not done: the release card build has no check; the note was not rebuilt; inbox items
1-10 and 14-15, 18 not answered beyond NEXT_SOURCE.md (C and F got the SIGTERM answer,
E the provenance). Card time of this session: none. Processor time: R7 about 6 minutes on
3 cores; tests and analyses under a minute each.

Closed at 12:27Z: core-20261125-080049-dcc9ea1 completed (0.6294 card-hours, job 5274);
core-20261124-130310-597d9ca stopped (0.8953 card-hours over jobs 5154, 5182, 5221, 5227),
manifests committed by `nrpic-run finish`. Branch pushed.

## 2026-11-26T02:25Z (2026-11-25 18:25 PST), batch 23, session core-lead-23 (no change of athenak/src or python/nrpic)

Task: (1) queue order of core's entries; (2) close q0030, q0031 of row 4 level 3; (3) Track
A's question on the PCS cloud at boundaries of static refinement; (4) NEXT_SOURCE item
for `<fastflow> diagnostics` on a continued run (0042 item 4); (5) merge of
`origin/core/restart-finder` on processors, build, byte regression, quick tests; release
waits for q0049.

(1) Done 02:20Z: q0033 (`row4-l3-0p755-member`, waiting, priority 2, arguments saved in
`scratch/core/tmp/b23_q0033.json`) removed and added again as **q0059** with the same 26
arguments, priority 2, `--after step-limit-card` (q0036, the check the dispatcher takes
last: effective priority 2 against 1 for q0035, q0039, q0049). q0032 (0.755 control) was
already in Slurm (job 5346, pending): not touched. No other row-4 entry of core waits.

### Predictions D1-D5 (deposit across a static refinement boundary), before any run

Reading of `NrpicDepositSources` (`athenak/src/particles/nrpic.cpp` 739-1116) [VERIFIED
by reading]: a particle's cloud is laid on the lattice of level `ldep` = the finest level
among the MeshBlocks that own the nb^3 nearest cell centres of the lattice of the
particle's own MeshBlock (lines 911-937); the part of a fine cloud that falls into a
coarser MeshBlock goes into the coarse leaf cell that contains the virtual fine cell
(1009-1021). The weights of each particle sum to one over the leaf cells (conservation),
but nothing makes the clouds of a regular lattice add up to a uniform density across a
level change: the first coarse particles next to a finer block get a cloud of the fine
width while their neighbours keep the coarse width, and the partition of unity of the
B-splines holds only for clouds of one width on a lattice of that spacing.
`deposit_fine_shape` acts only where a leaf is finer than `ldep` (1022-1032), that is
only with a level cap.

Test (`tracks/core/analysis/deposit_levels/dep_levels.py`, release processor build
core-v0.7): flat metric (`nrpic_geodesic`, no hole, `<adm> dynamic = false`), periodic box
32 x 8 x 8 (cells of 1), one static level in the slab |x1| < 8 (cells of 1/2; planar
boundaries at x1 = +-8), particles at rest, one per local cell at the cell centres
(mass rho0 times the cell volume), one step; E on the x1 line, and the same with the
lattice shifted by a quarter cell in x2 and x3. My own 1D emulation of the rule above
(the problem is planar) is the reference.

- **D1** CIC, cell-centred lattice: E uniform to round-off (|E/rho0 - 1| < 1e-13) on
  both levels: every CIC cloud of a particle at a cell centre lies inside its own cell.
- **D2** TSC: first coarse cell next to the fine level +18.75 per cent (1 + 1/8 + 1/16),
  second coarse cell -12.5 per cent, last fine cell -12.5 per cent; all other cells
  uniform to round-off. PCS: +20.83, -14.58, -12.5 per cent (46/48 + 1/6 + 1/12; 1/48 +
  2/3 + 1/6; 1/12 + 1/3 + 1/48). Mass sum exact to round-off in every case.
- **D3** AthenaK equals the emulation to 1e-12 relative in every leaf cell of the line,
  for every shape and both lattices. A difference above that is a defect of the code (a
  wrong cell or weight), not a property of the rule.
- **D4** `deposit_fine_shape = true` without a level cap changes no byte of the output
  (the branch is never entered). With `deposit_max_level = 0` (every cloud of root
  width, spread over the fine leaves) E is uniform to round-off for all three shapes,
  with and without `deposit_fine_shape`.
- **D5** Track A's compensation (`deposit_comp_c = 1/6`, `deposit_comp_c2 = 0.4667`) on
  the PCS case enlarges the boundary errors, by at most about a factor two (gain of the
  pass at the grid scale in x1 only, 1 + 4c + c2 = 2.13), and leaves the interior
  uniform.

Refuted: D1 by any CIC cell off by more than 1e-13; D3 by a cell where code and emulation
differ (a defect); D4 by a byte difference without a cap or a non-uniform capped deposit.
If D3 holds, the answer to A is "property of the deposit rule", with the cap or CIC as
the options for nested static meshes.

Amendment to D3 (02:33Z, before any run): for the lattice shifted in x2 and x3, the one
fine leaf on the line next to the boundary that receives the PCS tail of a coarse particle
(cloud of fine width in x2, x3 on a lattice of coarse spacing) need not equal the planar
emulation on a line at fixed x2, x3; D3 for the shifted cases is judged on the code's
mass sum and on all other cells, and that one cell is reported.

### Outcomes D1-D5 (02:30Z), runs core-20261126-022953-21b8455 (judged; figure looked at)

Earlier attempts on record: core-20261126-022652-fa293a1 (failed: the reader looked for
the tables beside the deck, AthenaK writes them into `tab/`), core-20261126-022724-382f943
(failed: my emulation asked for the leaf of a root lattice cell whose centre lies on a
fine face), core-20261126-022813-2d6c617 (same data as the judged run; its figure put the
capped cases on a scale of 1e-13 and was unreadable). The script's verdict line says FAIL
for every run: what failed is listed here.

- **D1 HOLDS.** CIC, cell-centred lattice: E/rho0 - 1 = 0 exactly in all 48 leaf cells of
  the line (also with the shift in x2, x3).
- **D2 HOLDS, to the digit.** TSC: +0.1875 (first coarse cell, x1 = 8.5), -0.125 (9.5),
  -0.125 (last fine cell, 7.75); PCS: +0.208333, -0.145833, -0.125, as computed by hand;
  every cell more than three cells from the boundaries uniform to 2.2e-16. At the left
  boundary (x1 = -8) PCS differs (+0.0625 at -8.5, +0.1458 at -9.5, -0.1458 at -10.5,
  -0.125 at -7.75): the stencil that picks the level has four cells, offsets -1..+2 for a
  particle at a cell centre, so two coarse particles on the left take the fine width and
  one on the right (the fourth cell carries weight 0 but counts for the level). The
  emulation reproduces it. The scripted "D2_mass" check failed only for the shifted PCS
  lattice (line sum 31.977 instead of 32): the amended cell, below.
- **D3 HOLDS where the emulation models the code** (every case without
  `deposit_fine_shape` and without compensation, ten cases): code minus emulation at most
  1.1e-15 in every leaf cell. Shifted PCS: the reported fine cell next to the boundary
  differs by 0.0231 on the line x2 = x3 = 0.1, as the amendment foresaw; all other cells
  8.9e-16. The scripted D3 failed on cases the emulation does not model: `pcs_capfs`
  (3.9e-3: the slopes of deposit_fine_shape are not in the emulation) and `cic_fs` (below).
  **So the boundary error of the PCS (and TSC) cloud is the rule of the deposit, coded as
  documented: a property, not a coding defect.**
- **D4 FAILED, in both parts.**
  (a) Without a cap, `deposit_fine_shape = true` is inert for TSC and PCS (tables
  byte-identical) but NOT for CIC: `cic_fs` puts -0.125 and +0.125 into the two fine cells
  next to each boundary (x1 = 7.25, 7.75), mass conserved. Cause, by reading
  (`nrpic.cpp` 993-1010, 1032-1072) [VERIFIED by this run against `cic`]: with the linear
  cloud and fine shape the lattice cells BESIDE the cloud are visited too (`ns = nb + 2`);
  for a coarse particle next to a finer block such a side cell lies in the fine block
  (kd = 1 > 0) and enters the fine-shape branch, which gives it the tent integral minus a
  constant (a zero-sum dipole), while the cloud's own cells are coarse leaves (kd = 0)
  that keep the plain weight: the dipole that should cancel against the slope of the own
  cells has nothing to cancel against. A defect of the option (it was meant for capped
  clouds); it does not touch Track A, which deposits PCS without the option.
  NEXT_SOURCE.md item 0.
  (b) A level cap does NOT make the deposit uniform: with `deposit_max_level = 0`
  (root-width clouds everywhere) CIC +0.125 (8.5) and -0.125 (7.25, 7.75), TSC 0.031, PCS
  0.027, with and without fine shape; the code equals the emulation (0 to 5.6e-16). My
  prediction was wrong because I took the fine particles as a union of 2^3 coarse
  lattices, each uniform; each of those lattices ends at the boundary at a different
  offset from the first coarse particle (0.75 and 1.25 coarse cells), so the particle
  lattice itself has a seam there that any cloud wider than its own cell sees. The cap
  makes TSC and PCS 6 to 8 times better, not exact.
- **D5 HOLDS in substance, the scripted check FAILED.** With Track A's compensation the
  largest boundary error of PCS grows by a factor 1.79 (0.373 against 0.208, inside the
  predicted <= 2.13); the interior (|x1| < 6.25, |x1| > 12.5) stays uniform to 2e-16. The
  check used a margin of three cells and the filter carries the error at -10.5 two cells
  further (+0.046 at -11.5): my margin, not the code. Not predicted: the compensated
  deposit is NOT conservative across the level boundary: the line sum is 32.0413 instead
  of 32 (+0.13 per cent of the mass; by the symmetry in x2, x3 the same for the volume
  integral). The non-flux pass (-c, 1+2c, -c) with ghost values from the other level is
  not conservative at a level face. NEXT_SOURCE.md item 0b (`deposit_comp_limit > 0`, the
  flux form, not tried).

What this answers for Track A: the O(0.1) error of the PCS cloud in the first coarse cells
of a lattice of one particle per local cell is the documented rule (level of a cloud =
finest level among its stencil's owners; partition of unity holds only within one cloud
width on one lattice spacing), made larger by the compensation (x1.8) and, for a
spacing jump of the particle lattice, present even with a cap. CIC with particles at cell
centres is exact on both sides (D1), which is A's factor of twenty. Answer posted to A.

### Outcomes P10-P15 so far (02:31Z), run core-20261126-023040-b755cdc (figure looked at)

Closed first: core-20261125-180320-3dad12c (q0030, 0.726875 control, 0-600 M, completed,
1.2981 card-hours over 4 jobs of its chain) and core-20261125-225600-d2db1ed (q0031, 0.73625
member continued from core-20261123-020458-dfc38d7 at 300 M, completed, 0.6325 card-hours,
one job), by `nrpic-run finish` (manifests committed 846c3b6b, cdb695ab).

- **P10 HOLDS.** 0.726875: neither run collapses by 300 M (member and control), D =
  +0.0061 (|D| <= 0.01), member STAYS, model STABLE: **bracket by the 300-M rule
  (0.7175, 0.726875)**, valid, nothing pending inside; next midpoint 0.7221875.
- **P11 HOLDS.** 0.726875 beyond 300 M: member 338.25 M, control 333.75 M (lapse < 0.3),
  both in 300-420 M, 4.5 M apart (<= 30).
- **P12 HOLDS.** 0.73625: member 405.0 M, control 421.25 M, both in 320-500 M.
- **P13 PENDING** (q0032 in Slurm as job 5346; the member is q0059 after the checks).
- **P14** for the member's join: not computed in this session (`row4_fate.py` does not
  print joins); the control's join held in batch 17.
- **P15 HOLDS** on the bound (no run above 9 s per M): 3dad12c 1.2981 card-hours for 600 M
  = 7.79 s per M over 4 jobs (two attempts preempted, their lost minutes included);
  d2db1ed 7.59 s per M in one job.

What it means (the reading written on 2026-11-24 before the runs): P11 and P12 hold, so
the 300-M bisection measures how long a model resists a common inward drift, not a
stability threshold: every model from 0.605 to 0.73625 collapses by 421 M on M/8, and the
collapse time grows smoothly with y_c (180.5, 219.5, 244.25, 294.25, 338.25, 405.0 M for
the members). Row 4 on M/8 is reported as "collapse within 300 M bracketed between 0.7175
and 0.726875"; the drift (its dependence on cell size and particle number) is the open
item [JUDGEMENT]. 0.755 (q0032, q0059) decides whether it reaches the most stable model.

### Prediction F1 (02:36Z): `<fastflow> diagnostics` in a run continued from a restart file

Reading [VERIFIED by reading]: `main.cpp` 279-291 loads the parameters from the restart file,
then from `-i <file>` if given (`LoadFromFile` adds or replaces lines), then
`ParameterInput::ModifyFromCmdline` (`parameter_input.cpp` 370-409), which exits with
"Parameter '<name>' in block '<block>' on command line not found" for any parameter not
already present; `fastflow.cpp` 299-300 reads `diagnostics` only if it exists, and the
status file is opened in append mode with its header only when new (454-457).
Test (`tracks/core/analysis/restart_diag/diag_restart.py`, release processor build
core-v0.7, `problems/tests/by_horizon_coarse.athinput` with a restart output, one cycle,
then continued to cycle 2):
- **F1a** `-r <rst> fastflow/diagnostics=true`: exit status 1 with that message, no
  status file. (The defect Tracks D and F reported.)
- **F1b** `-r <rst> -i add.athinput` where `add.athinput` holds only `<fastflow>
  diagnostics = true`: exit status 0 and a status file `hc.horizon_status_0.txt` with a
  header and one record per search of the continued run. (A workaround today, if it holds.)
- **F1c** `-r <rst>` alone: exit 0, no status file.
Refuted: F1a by a run that starts; F1b by a failure or a missing status file.

### Predictions R8, Q8 (02:45Z): merge of core/restart-finder into core/nrpic

Merge b755cdcf (no conflict; the changelog section of the branch sits at the top). The
source of the merged tree (`athenak/src`, `python`, `problems`, `docs`, `scripts`) is the
branch's (git diff empty against `origin/core/restart-finder`), i.e. source commit 01d4aeeb.
Serial build `scratch/core/b23_build_cpu/src/athena` (628 s, 4 jobs; sha256 7599042f...,
not the published branch binary's d7306809..., as build paths are in the debug data).
- **R8** byte regression (`regress_v04.py`, twelve set-ups) against release core-v0.7
  `.work/build_cpu_v07/src/athena`: 75 of 75 identical, as the branch's final build gave
  (run core-20261125-142602-33f4005). Refuted by any item not identical.
- **Q8** quick test of the release's new behaviour: `restart_test.py` (T1: restart outputs,
  tracker and history files across a continuation) with the merged build against the
  release: every check holds as in run core-20261125-142556-a424739 (branch final build).
  Refuted by any failed check.

### Outcome F1 (02:50Z), run core-20261126-023323-c8fad52 (figure looked at)

- **F1a HOLDS**: `-r <rst> fastflow/diagnostics=true` exits with status 1 and "on command
  line not found"; no status file.
- **F1b HOLDS**: `-r <rst> -i add.athinput` (only `<fastflow> diagnostics = true`) exits 0
  and writes `hc.horizon_status_0.txt` with its header and two records (cycles 0 and 1,
  both found, 3 and 2 flow iterations). The continuation started from `hc.00000.rst` (the
  first of the three restart files of the first run, written at t = 0), still a run read
  from a restart file.
- **F1c HOLDS**: the control writes no status file.
So Tracks D and F can switch the status file on in a continued run today with `-i`; the
source fix (add a parameter on restart) is NEXT_SOURCE.md item 1, with this test.

### Outcome Q8 (02:54Z), run core-20261126-024518-e1e16dc (figure looked at)

**Q8 HOLDS**: `restart_test.py` with the merged build, 19 checks "ok", ALL OK, as in run
core-20261125-142556-a424739 of the branch build: the uninterrupted run equals the release
byte for byte; the four cuts K24-K27 (every residue of the record interval) and the chain
(segments cut with status 143, last segment 0) give every output file byte-identical to
the uninterrupted run, with restart and `.prt` files identical; the release, cut the same
way, loses the tracker records before the cut, the `cons.hst` record at t = 1.6875 (cuts 26,
27) and writes 4 header lines in the mesh history instead of 2 (the figure shows all three).

### Outcome R8 (03:15Z), run core-20261126-024438-1fa17dd (figure core-20261126-031446-af637b5 looked at)

**R8 HOLDS**: 75 of 75 items identical with release core-v0.7 (geo 2, boris 2, dep 1, east
12, os 16, jeans 5, binary 1, c1 5, c2 3, c3 14, c4 4, c5 10; classes a, b, a+b, other
empty), REGRESSION PASS, as the branch's build gave (core-20261125-142602-33f4005). The
release candidate core-v0.8 (source 01d4aeeb, tree of core/nrpic b755cdcf) is prepared on
processors; `RELEASE-v0.8.md` written with its card check PENDING (q0049). Not released.

### Close of the session (03:17Z)

Not done: q0049 has not run (nothing to judge with `card_check.py`); no executable of v0.8
was published (the branch's executables of the same source stay at
`scratch/core/exe/core_restart-finder/`); P14 for the 0.73625 member's join; the note
(waits for 0.755); A's new request `finder-false-accept-and-stall-p0l6` not read. Card time
of this session: none. Processor time: build 628 s on 4 jobs; tests and analyses on one
core each, about 50 core-minutes in all (R8 30 min, F1 11 min, Q8 8 min).

## 2026-11-26T11:55Z (03:55 PST), session core-lead-27 (batch 27): release core-v0.8; prediction for the MPI build

Card check q0049 judged (outcome in `JOURNAL-restart-finder.md` entries 21 to 23): PASS for
what the release changes; K3 failed for the rule without polishing. Release record final.
MPI build of the merged tree: `.work/build_cpu_mpi_v08rc` (4 jobs, 11:51Z to 11:53Z; rc 0),
copied to `scratch/core/exe/core_nrpic_v08/athena_cpu_mpi`. Prediction before its smoke test
(`analysis/release/mpi_smoke_v08.py`, deck `problems/tests/restart_outputs.athinput`): M1 the
MPI build started without mpirun writes every output file of the serial build of v0.8 byte
for byte (logs and restart files excluded); M2 on two ranks status 0 and the records of
`cons.hst`, the tracker file and the mesh history as on one rank, every column within 1e-6
relative (the deposit in shared cells adds in another order; `mpi.md` section 7). Refuted by
any differing file in M1 or any column above 1e-6 in M2.
