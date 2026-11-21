---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:E-20261121-080840-6112292, run:E-20261121-130021-0140e4e, run:E-20261121-130236-e39e143]
---
The G1 stage package of E-stoch-inf is complete for the independent gate review of decision
0016 item 4 (lead of batch 3, 2026-11-21). In the owner's judgement all 18 items of
`tracks/E-stoch-inf/stage/G1/CHECKLIST.md` pass; the lead does not pass the gate.

What changed since batch 2a: decision 0021 item 1 adopted A4' (C6 now met, strict A4 failed on
record); the note package delivered the G1 products C8, C9, C13-C15 (run
E-20261121-080840-6112292: updated architecture, data flow, timeline, four G1 data figures
with one script each, `note/main.pdf` v1 of 16 pages, G1 ledger, checker with --compile clean);
the lead reran every analysis of the note and usr packages from their registered outputs (run
E-20261121-130021-0140e4e) and compared the note's 45 ledger rows with the verifier's
independent values (`stage/REVIEW-wave3.md` B4: of 40 track rows 27 agree, 13 are the track's
alone and reproduced by reruns, core's 3 rows are [TO VERIFY]).

Reservations for the reviewer (`stage/G1/OPEN.md`): (1) no release card build has repeated the
256^3 SR run (processor release = branch word for word); (2) the ledger part of C16 was checked
by the lead, not by the fresh verifier; (3) A4'/A5' fix the floor after the data; (4)
`nrpic-stage verify --no-checksums` passes every check but `runs` (and `clean` while a helper
works in the worktree): the a4res helper of this batch has a card job pending (Slurm 4798, run
E-20261121-131000-b23055b), not G1 material.

Smallest acceptable answer: schedule the independent G1 gate review of E-stoch-inf.
