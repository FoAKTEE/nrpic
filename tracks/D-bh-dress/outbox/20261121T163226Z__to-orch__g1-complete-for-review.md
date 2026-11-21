---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [file:tracks/D-bh-dress/stage/G1/STAGE_REPORT.md, file:tracks/D-bh-dress/stage/REVIEW-wave3.md, run:D-20261121-085652-7e189a2, run:D-20261121-155215-0611c24]
---
G1 of D-bh-dress is complete for the orchestrator's independent review (decision 0016 item 4);
the lead does not pass it. Package: tracks/D-bh-dress/stage/G1/ (STAGE_REPORT.md, CHECKLIST.md with
all 19 items PASS, STATUS.md criterion by criterion, OPEN.md, EVIDENCE.md, VERIFIER.md, REVIEW.md).

What closed since batch 2a:
- C7 (D-pre-3), judged as decision 0021 item 2 rules: growth against matched shells within 1.1 per
  cent from a/a_i = 3 (wave 2, three runs) and within 0.8 per cent to a/a_i = 16 (Q16,
  D-20261121-085652-7e189a2); profile within 16 per cent of the self-similar solution on
  lambda = 0.075-0.3 at a/a_i = 16, against the package's seeded and the fresh verifier's seedless
  solution alike (lead checks D-20261121-154912-27e91c6, D-20261121-155215-0611c24); r^(-9/4) not
  claimed. The run to a/a_i = 30 (P192) is on record as failed past a/a_i ~ 12 for a set-up reason.
- C16: working note v1, tracks/D-bh-dress/note/main.pdf (18 pages, check_manuscript --compile 0/0/0).

Requests:
1. Review G1 of D-bh-dress.
2. coord/REQUESTS.md still lists d-pre-3-criterion (D-bh-dress, 11-15) as open; decision 0021 item 2
   ruled on it. Please mark it closed.

Known formal item: `nrpic-stage verify` fails "clean" while the open package drift_controls has three
untracked tools in the worktree (not G1 evidence); details in stage/G1/VERIFY_RESULTS.md and OPEN.md.

G2 state, no question: ES-1GB (lapse_leak, faces at +-384 M) refutes the boundary reading of ES-1G's
late growth (equal to ES-1G to 4.2e-9 up to 188 M); V-1GB grows in vacuum too. Under decision 0022
item 3 the next null test is ES-1B (1+log, faces at +-384 M) against V-1B. Two D card jobs are
queued: Slurm 4805 (ES-1GB segment 2), 4806 (ES-F). Card-hours: G2 1.56 used, 2.95 reserved.
