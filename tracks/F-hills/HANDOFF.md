# HANDOFF of F-hills

State in three lines (2026-11-27 18:13 PST, end of the batch-35 lead session, processors only):
- G0 signed. G1: gate review recommends PASS WITH RESERVATIONS; decision 0048 item 2 signs it once
  the passage reaches t = 200 M (queue entry q0091) and a registered reading shows it. The
  verifier's part-2 corrections are applied (batch 35). The lead did not pass G1.
- P1b at m/16 (A + A2) is recorded to 186.0 M: m1 captured by M (common horizon 137.5 M), m2
  recedes after an 8.73-M pericentre, fate undecided; Newton gives the reverse fates.
- One card entry of this owner: q0091 (A2 to 200 M), WAITING at 18:10 PST (5 of 5 account jobs).

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Check first: q0091 (A2 continued to 200 M)

`harness/bin/nrpic-queue list | grep q0091`; `squeue -n F-20261124-210400-902c650`;
`cat /data/haiyangw/nrpic/scratch/F-hills/F-20261124-210400-902c650/chain/STATUS` (DONE when tlim
200 is reached); `tail chain/events.log`. The wrapper appended a record to the manifest's
`continuations` and committed it on this branch when the dispatcher submitted it (pull nothing:
it commits in this worktree). KNOWN DEFECT of the queue: a preempted job may be listed as done.
Every job id of the chain since the continuation (events.log, `jobid`) must show COMPLETED in
`sacct -j <ids> -o JobID,State,ElapsedRaw` (or CANCELLED/PREEMPTED followed by a resubmission in
events.log). If the chain ended FAILED or below 200 M, continue it again with ONE entry:
`harness/bin/nrpic-queue add --label F-A2-to200b --priority 2 --cmd 'tracks/F-hills/binary_conv/scripts/continue_chain.sh F-20261124-210400-902c650 <cap> --extra-input tracks/F-hills/binary_conv/inputs/fastflow_diag.athinput'`
(`--reopen` only if the manifest says `stopped`; dry run first with `--dry-run`).

## Exact commands once q0091 has ended at 200 M

1. `harness/bin/nrpic-run finish F-20261124-210400-902c650` (no `--status`: it closes from the
   chain's STATUS; the cache makes the 720 GB cheap except the new files).
2. Readers, registered, one core each:
   `harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --purpose "A2 to 200 M: state, health, end state (D35)" -- python3 tracks/F-hills/stage/review_wave3/b21_a2_state.py --out '$NRPIC_RUN_DIR'`
   and the same with `python3 tracks/F-hills/stage/review_wave3/b34_horizons.py --out '$NRPIC_RUN_DIR'`
   (it reads the status files, whose rows end with `# <words>`). Read both figures with the Read tool.
3. Judge D35-1..9 (JOURNAL batch 35) one by one in JOURNAL; card-hours from the manifest
   (`resources.gpu_hours`, sum over jobs).
4. CHECKLIST C8 (the 200-M clause), STATUS.md T4, EVIDENCE.md (row "lead, batch 36"), OPEN.md
   item 1; `harness/bin/nrpic-stage collect F-hills G1`, `verify F-hills G1`, `report F-hills G1`.
5. One line to orch: `harness/bin/nrpic-ctx post --to orch --type info --slug g1-passage-200m --body "..."`
   with the run ids (A2, the two reader runs): decision 0048 signs G1 on it.

## Restart files (decision 0048 items 2 and 8: nothing deleted; sizes for a later decision)

| run | what | restart files | rst/ size | run dir |
|---|---|---|---|---|
| F-20261121-203144-b2cf16b | A, P1b m/16, 0-61.8 M (G1) | 24 | 134 GB | 138 GB |
| F-20261124-210400-902c650 | A2, P1b m/16, 61.8-186.0 M, continuing to 200 M (G1) | 143 | 719 GB | 724 GB |
| F-20261121-203156-03efdd3 | B, binary alone m/16 to 107.85 M (G1) | 27 | 103 GB | 103 GB |
| F-20261126-052133-10f9a5f | B2, binary alone m/16 to 140 M (G2) | 39 | 150 GB | 150 GB |
| F-20261121-203247-961801d | C, P1b m/12 to 20 M (G2) | 7 | 37 GB | 38 GB |
| F-20261126-131751-89eaff8 | C2, P1b m/12 to 106.69 M (G2; to continue) | 66 | 320 GB | 322 GB |
| F-20261119-150017-b45ec5f | P1, m/8 to 280 M (G1, closed) | 57 | 162 GB | 165 GB |
| F-20261121-130351-04074e1, -153707-1eaa5d4, -130358-6cf186a | R16n, R12, R8 binary alone | 8, 7, 6 | 31, 28, 17 GB | same |

Measured with `du --apparent-size` at 18:12 PST 2026-11-27; /data 89 percent full (12 TB free).
A2's restart files between 87 and 133 M are needed for F1's polished-search test (G2); C2's newest
(`rst/hills.00072.rst`) for its continuation; the last of A2 if the passage is continued past 200 M.

## Runs of this owner

| | run id | state | read by |
|---|---|---|---|
| A + A2 | F-20261121-203144-b2cf16b + F-20261124-210400-902c650 | A2 reopened by q0091 (waiting) | `stage/review_wave3/b21_a2_state.py`, `b34_horizons.py`, `b11_passage.py` |
| B2 | F-20261126-052133-10f9a5f | closed, DONE at 140 M (G2) | `b11_cards.py` (not analysed) |
| C2 | F-20261126-131751-89eaff8 | closed, stopped at 106.69 M (G2) | `b11_passage.py` draws C + C2 (not judged) |
| batch 35 | F-20261128-020208-d7c6f1c (reader), F-20261128-020409-a3edb04 (note run_all) | completed | |

## Packages and their state

| package | state | what remains |
|---|---|---|
| stage/G1 | corrections applied; collect/verify/report of batch 35 | the 200-M clause (above) |
| note | v2.1 (24 pages; schematics to core-v0.8) | v3: the passage to 200 M with a figure script (A + A2 trackers and finder summaries; hrms classes), ledger rows from the reader runs, the reverse fates, the junk at P1b's spheres |
| binary_conv | A2 continuing; B2, C2 closed | README "Results" rows for A2, B2; C2's continuation (G2) |
| stage/review_wave3 | b21_a2_state.py (batch 35), b34_horizons.py, b11_passage.py | b11_passage: m1's energies after the merger meaningless, M pre-merger |
| g2mesh | cut 2026-11-20 | G2M-1b outcome; G2M-2/3 |
| novelty | kb's answer on claim 452 | reword NOVELTY.md if needed |

## Files to read first

`CLAUDE.md`; `STATUS.md`; `JOURNAL.md` batch 35 (D35-1..9 predictions); `stage/G1/OPEN.md`,
`stage/G1/GATE_REVIEW.md`, `stage/G1/VERIFIER.md` sections 16-17; `stage/REVIEW-wave3.md` batch 35;
`RISKS.md` (R25-R27); `coord/DECISIONS/0048-rulings-after-batch-34.md` item 2.

## Decisions pending

- orch: a `--full` checksum pass before the tag (outbox `g1-full-checksum-pass`); retention of
  the restart files (table above).
- core (answered in batch 35, acknowledged): `<fastflow> trapped_tol_<n>` in the core-v0.9
  candidate (status column 16) for G2 runs; restart parameters on the command line from v0.9.

## Traps

- A2's manifest: the continuation record's `at` is after its `finished`, so the run is OPEN again
  until `nrpic-run finish` closes it; the stage check names it until then.
- Status rows end with `# <reason in words>`: `nrread.read_table` skips them; use
  `b34_horizons.status()` or `b21_a2_state.status_rows()`.
- 'found' is not converged: read the summary's hrms (column 9) beside every mass (R25).
- The summary's column 3 is the mass with spin; the status file's column 7 is the area mass.
- A2's directory starts at 61.80 M: always read A + A2 joined (`b11_cards.trackers("A")`).
- `fastflow/diagnostics=true` on the command line of a core-v0.5 restart is FATAL; only `-i <file>`
  works (A2 keeps its core-v0.5 executable `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`).
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
