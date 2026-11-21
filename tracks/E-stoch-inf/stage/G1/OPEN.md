# What the G1 package of E-stoch-inf still lacks or reserves (2026-11-21, lead of batch 3)

Every item of `CHECKLIST.md` is judged PASS (`STATUS.md`); the package is complete for the
independent gate review of decision 0016 item 4. G1 is not passed until that review and the
orchestrator's sign-off. Reservations a reviewer should weigh, in order of importance:

1. **Release card build untested on the SR set-up** (risk R1). The G1 runs used the tested
   branch `core/scalar-2` a58e95b (scouting, decision 0013). On processors the release
   core-v0.4 equals it word for word (run E-20261121-064707-77ec326); no card run of a release
   build has repeated P256. Remedy: P256 on `.work/build_gpu_v05/src/athena` with
   `ladder/inputs/jobA.list` (0.5 card-hours) against E-20261115-172618-f948386.
2. **Ledger part of C16 checked by the lead, not by the fresh verifier.** The verifier wrote
   before the G1 ledger existed; the lead of batch 3 compared its 45 rows with the verifier's
   independent values (`../REVIEW-wave3.md` B4): 27 of the 40 track rows agree, 13 are the
   track's alone (A2 against the stencil wave number; e-folds of the odd/even maxima; the
   convergence set-up's odd/even; the control's H range; the floor exponent of M and its
   256^3 values; the record of H at N_f; three A6 rows; two analysis rows; seconds per step),
   each reproduced by a rerun. A reviewer may ask a fresh agent for these 13.
3. **Criteria fixed after the data.** A4' (decision 0021) and A5' define "the floor" after the
   data; the strict A4 stays failed on record (odd/even 745, 655, 869, 25 at N = 32-256).
4. **Harness verify** (run with `--no-checksums`: the full checksum pass reads several hundred
   GB) can fail on `clean` and `runs` while the `a4res` helper of batch 3 works in this
   worktree: its card job 4798 (run E-20261121-131000-b23055b) stays "submitted" until its package closes it. These are not G1
   material; every other check passes (`VERIFY_RESULTS.md`).
5. **Smaller items, not needed for G1's criteria** (G2 or later): P256's constraint split after
   t = 4.0 (a P256m to t = 8.5, 0.5 card-hours; verifier W3); the R^NR floor of ~2e-6 at
   64^3-256^3 (W9); the absolute constraint levels 40-100 x below P1's statements
   ([TO VERIFY], W7, risk R18); A7 for the rank count; core's explanation of the first-order
   part (the stencil symbols, `coord/INTERFACES/scalar_field_3.md` lines 143-164) awaits the
   track's check (package `a4res`, at work in batch 3).

Pending runs: none of this owner's G1 material. G2 material: Slurm 4798 (run
E-20261121-131000-b23055b, package `a4res`, read by `a4res/scripts/`), pending at 13:30Z.
