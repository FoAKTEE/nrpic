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
