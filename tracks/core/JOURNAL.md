# JOURNAL of core

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:53Z  session core-lead (integration of wave 1)  commits 74ed745..  runs: see below

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
