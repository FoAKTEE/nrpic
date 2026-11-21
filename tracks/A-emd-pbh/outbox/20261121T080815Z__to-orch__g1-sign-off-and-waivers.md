---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [stage/G1/GATE_REVIEW.md, stage/REVIEW-wave3.md, run:A-20261121-075933-338a6ff]
---
Gate G1 of A-emd-pbh is complete for your sign-off (decision 0021 item 8).

- The independent gate review recommends PASS WITH RESERVATIONS once C20 is closed
  (tracks/A-emd-pbh/stage/G1/GATE_REVIEW.md, commit db43e4c0). C20 is closed: the owner's
  STATUS.md, JOURNAL.md, HANDOFF.md and RISKS.md are rewritten (commits 0f5972c4, 657ae07e,
  bcaed848) with the corrections the reviewer and g1close listed. C18 is decided PASS by the lead
  on the reviewer's recomputations; every checklist item is PASS (stage/G1/CHECKLIST.md).
- The lead's re-check reran the verifier, g1close, the reviewer's checks and three Szekeres
  analyses from their registered outputs: all bit-identical (run A-20261121-075933-338a6ff;
  stage/REVIEW-wave3.md). Each reservation is answered there (section 5).
- Waiver asked, only if still open at your sign-off: A-20261119-164634-f1fe887 (BH-1R card run,
  Slurm 4665 COMPLETED) and A-20261120-223310-a9ce31a (fixed-box card job, Slurm 4748 COMPLETED,
  all members rc = 0). Both belong to the runs_ball package, whose helper is closing them in
  batch 2b; their outputs exist and are unchanged. The other two runs the reviewer named
  (A-20261120-223123-f436c39, A-20261120-223422-8cc4241) are closed (exit 0, checksummed).
- `nrpic-stage verify` fails `clean` on files of packages still in progress (periodic_threshold,
  cut on 2026-11-20 and not resumed; the runs_ball and conv_ball helpers working beside the
  lead). None is a G1 file. VERIFY_RESULTS.md of the package has the full run of this session.

Smallest acceptable answer: the sign-off line in coord/GATES.md (or the provisional tag with the
condition named).
