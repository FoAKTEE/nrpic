# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1: independent review recommends PASS WITH
             RESERVATIONS (stage/G1/GATE_REVIEW.md). Decision 0048 item 2: signed once (a) the
             passage reaches t = 200 M and a registered reading shows it with its health checks,
             and (b) the verifier's part-2 corrections are applied. (b) DONE in batch 35;
             (a) QUEUED as q0091. Not passed by the lead.
headline:    The m/16 Hills passage P1b (A + A2) is recorded to 186.0 M: the binary is disrupted
             between 120 and 133 M, m1 is captured by the heavy hole (common horizon from 137.5 M;
             remnant 1.12291 Christodoulou, S/M^2 0.2529 at 186 M with hrms 3.4e-4), m2 keeps its
             horizon (converged searches 0.12939-0.12964) and recedes after an 8.73-M pericentre,
             fate undecided in coordinates. Newton from the same deck ejects m1 and binds m2.
last-result: - batch 35 corrections (VERIFIER.md 16-17, GATE_REVIEW 5): C8/C18/T4/OPEN rewritten;
               F1 decided for 86.6-131 M by hrms (heavy hole 1.00422, constant to 6.4e-5); 'found'
               is not converged, masses quoted with hrms; MeshBlocks 2584 was run A's (A2:
               1968-2514); 1.00444 at 133 M, 1.00531 at 135 M during m1's approach
               (F-20261128-020208-d7c6f1c, fig_b21_a2_state read, title no longer PARTIAL)
             - schematics redrawn to core-v0.8, note v2.1 (F-20261128-020409-a3edb04; numbers and
               ledger unchanged, D35-N met; 24 pages compiled)
             - continue_chain.sh --reopen: continues a chain closed `stopped` (dry run passed)
             - failed predictions this session: none judged; D35-1..9 wait for q0091
decision:    continue A2 to 200 M in place (q0091); write note v3 once, after the 200-M reading
card jobs:   q0091 (label F-A2-to200, priority 2): A2 F-20261124-210400-902c650 from
             rst/hills.00166.rst (186.002 M) to tlim 200, cap 31 counted segments (27 used),
             expected 3 segments, about 2.7 card-hours; WAITING at 18:10 PST (5 of 5 account jobs
             in Slurm). Output appends to scratch/F-hills/F-20261124-210400-902c650/.
next:        1. when q0091 has ended: sacct (every job COMPLETED or cut and resubmitted), nrpic-run
                finish, registered b21_a2_state.py + b34_horizons.py, judge D35-1..9, C8 and
                EVIDENCE.md, one line to orch with the run ids (the gate is signed on it)
             2. note v3: the passage to 200 M (figure, ledger rows, hrms beside each horizon number)
             3. G2: C2's continuation past 145 M (m/12), F1's polished-search test on A2's restart
                files, the first clump passage (decision 0013)
readers:     stage/review_wave3/b21_a2_state.py (S1-S3 record, S6 health, S7 end state),
             b34_horizons.py (status files; rows end with "# words")
blockers:    shared queue full (R27); Slurm submission I/O error once (R26)
needs:       orch: whether a --full checksum pass is needed before the tag (outbox b35); the
             retention of the passage's restart files (sizes in HANDOFF.md)
offers:      continue_chain.sh --reopen, nrread.py, b21_a2_state.py, b11_passage.py, b34_horizons.py
budget:      G1 49.89 of 60 card-hours used before q0091 (gate review, nrpic-run budget); q0091
             about 2.7 more. This session 0 card-hours (two processor runs, one core each)
