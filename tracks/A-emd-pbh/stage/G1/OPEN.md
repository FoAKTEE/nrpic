# What G1 of A-emd-pbh still lacks (rewritten by the g1close helper, wave 3, 2026-11-20)

The two items G1 lacked after wave 2 are closed: the data-flow schematic (C11) is drawn and
is Fig. 7 of the note, and a fresh verifier recomputed the note's ledger, `newton/` and the
criteria checks (C18, `VERIFIER.md`); its corrections are applied or rebutted with evidence
(`../../g1close/JOURNAL.md`, `README.md` section "Close-out, wave 3"). What remains, item by
item, with the smallest action that closes each:

1. **C20 (FAIL): the owner's STATUS.md, JOURNAL.md, HANDOFF.md are not current.** Last
   changed on 2026-11-15; they still give G0 as not passed, C11 and C18 as open, and the
   sentence the verifier corrected ("14 scan points within 6.3e-4", STATUS.md line 13).
   Action: the lead rewrites them at the end of wave 3 round 1 (helpers do not write them);
   the sentences to change are listed in `../../g1close/README.md`, "Requests".
2. **C18 (PASS by judgement; the gate reviewer decides): numbers of the note no fresh
   verifier recomputed.** The predicted card-hours of the two scouting runs (a cost model),
   the four cross-check differences of Table II (read from their output, checksum verified),
   and five rows that note v1 added to Table IV from the wave-2 analyses
   A-emd-pbh-20261115-163659-4dbacd0 and A-20261115-182657-53da696 (tracked-particle
   residuals, constraint norm at t = 20, two central-lapse rows, compactness on the axes).
   The note names them in App. B. Action, if the reviewer reads "every number" strictly: a
   fresh verifier recomputes these five rows from the raw outputs (processor only, about an
   hour).
3. **Wave-1 outputs: checksums recorded late.** Run A-20261120-222620-0304d9d lists the
   sha256 of the 55 files without a record of their own and the note checks its inputs
   against it, so any later change is detected; that the files are the ones the wave-1 runs
   wrote rests on the verifier's independent reconstruction of data set 2t and of the
   criteria (VERIFIER.md finding 7). Action before G2, optional: rerun the wave-1 producers
   through `nrpic-run` (seconds to minutes each; verifier weak point 3).
4. **Handled by other helpers this round, not by this package:** the SR-2 turnaround
   estimator and the re-judgement of runs_ball prediction R2 (VERIFIER.md finding 6, weak
   point 1, section 4 item 1) by the runs_ball helper; an order of the core error at a fixed
   box (weak point 2) by the conv_ball series; `docs/FORMATS.md` line 122 (`.trajmet.bin`
   records of 17 values, not 12) is core's.
5. **For G2, not gate items of G1:** AthenaK's own t = 0 constraint norms of the format-2
   tables (the cstat files of SR-1/SR-2 hold them: H_max 4.7e-4 at dx = M/2, t = 0, run
   A-emd-pbh-20261115-153845-7172b66); the cause of the energy drift of the Newtonian mode
   during sub-cell crossings (1.1e-3 to 9.3e-3, spindle 3.0e-2; analysis
   A-emd-pbh-20261115-164420-4528861).

## Automated checks (`nrpic-stage verify`) that do not pass

`nrpic-stage verify A-emd-pbh G1 --no-checksums` on 2026-11-21T03:20Z, clean export of
72ac63ce (`VERIFY_RESULTS.md`): 14 of 16 checks pass (sync, export, size, note, package,
note-pdf, style, fig-script, min-figs, status, rerun 9 of 9, compare 14 files within
tolerance, regenerate 14 of 14; run-notes WARN). Two fail, neither from this package:

- **clean**: four uncommitted paths of the periodic_threshold helper, who works in this
  worktree at the same time (`periodic_threshold/JOURNAL.md`, `inputs/peak_leak.athinput`,
  `scripts/ltb_reference.py`, `scripts/ltbref.py`). Passes when that helper commits.
- **runs**: 4 of 167 manifests are not finished, all of other helpers' runs still in
  progress this round: A-20261119-164634-f1fe887 (BH-1R card run, "submitted"; runs_ball),
  A-20261120-223310-a9ce31a (fixed-box card job, "submitted"; runs_ball),
  A-20261120-223123-f436c39 (periodic_threshold, "running"), A-20261120-223422-8cc4241
  (szekeres, "running"). Passes when those helpers finish them with `nrpic-run finish`.
  Every hand-written manifest of waves 1-2 is named in an EVIDENCE.md and waived (decision
  0016 item 3).
- **Not run in this verify: the output checksums.** The full `verify` (with checksums) was
  stopped by my 15-minute limit while it hashed about 80 GB of wave-2b card outputs
  (A-20261119-144419-13d5601: 60 GB, A-20261119-164634-f1fe887: 19 GB). The lead or the
  reviewer reruns it without `--no-checksums` when the queue of helpers is empty (about 20
  minutes of disk reading), or checks single runs with `harness/bin/nrpic-run verify <run id>`.
