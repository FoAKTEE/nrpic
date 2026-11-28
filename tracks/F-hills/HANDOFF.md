# HANDOFF of F-hills

State in three lines (2026-11-28 08:16 PST, end of the batch-41 lead session, processors only):
- G0 signed. G1: the 200-M clause is MET (q0091 DONE at 200.0 M, read by two registered readers);
  decision 0048 item 2 signs G1 on the line to orch (outbox g1-passage-200m) and the full checksum
  pass, which RUNS detached (below). The lead did not pass G1.
- P1b at m/16 (A + A2) is recorded to 200.0 M: m1 captured by M (common horizon 137.5 M), m2
  recedes (21.07 M at 200 M); Newton gives the reverse fates. No card job of this owner queued.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Check first: the full checksum pass of G1

Started 08:06 PST 2026-11-28 with `setsid nohup harness/bin/nrpic-stage verify F-hills G1 --full`
(pid 1346011; it verifies commit f0e18c850, an export under scratch/F-hills/tmp/stage-verify/).
Log: `/data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify-full-G1-20261128-080654.log` (empty
until the end). About 2 TB to read: hours. Is it still running: `ps -p 1346011 -o etime,cmd`.
When it has ended it has rewritten `tracks/F-hills/stage/G1/VERIFY_RESULTS.{json,md}` in this
worktree (uncommitted): read the `[checksums]` line (every byte read, no cache), then commit
them path-limited (`git add tracks/F-hills/stage/G1/VERIFY_RESULTS.*`), regenerate the report
(`harness/bin/nrpic-stage report F-hills G1`), and send one line to orch with the outcome
(`harness/bin/nrpic-ctx post --to orch --type info --slug g1-full-checksum-result --body "..."`).
If it failed on a checksum: name the file and run, do not rerun anything that writes; report.
If the process is gone and the log is empty or cut: start it again the same way (it is
read-only apart from VERIFY_RESULTS) and say so.

## Runs of this owner

| | run id | state | read by |
|---|---|---|---|
| A + A2 | F-20261121-203144-b2cf16b + F-20261124-210400-902c650 | A2 closed, completed at 200.0 M (batch 41) | `stage/review_wave3/b21_a2_state.py`, `b34_horizons.py`, `b11_passage.py` |
| batch 41 readers | F-20261128-160721-f0e18c8 (b21), F-20261128-160749-2ba694f (b34) | completed | |
| B2 | F-20261126-052133-10f9a5f | closed, DONE at 140 M (G2) | `b11_cards.py` (not analysed) |
| C2 | F-20261126-131751-89eaff8 | closed, stopped at 106.69 M (G2) | `b11_passage.py` draws C + C2 (not judged) |

Queue audit (`nrpic-queue audit --owner F-hills`): q0001, q0069 (A2's earlier chains) and q0003
(C2) are "NOT COMPLETED" chains that ended FAILED; all known: A2 was continued by q0091 (DONE),
C2 stopped at its cap (continuation is G2 work).

## Restart files (decision 0048 items 2 and 8: nothing deleted; sizes for a later decision)

| run | what | restart files | rst/ size |
|---|---|---|---|
| F-20261121-203144-b2cf16b | A, P1b m/16, 0-61.8 M (G1) | 24 | 134 GB |
| F-20261124-210400-902c650 | A2, P1b m/16, 61.8-200.0 M (G1) | 157 (newest hills.00180.rst) | 791 GB (measured batch 41) |
| F-20261121-203156-03efdd3 | B, binary alone m/16 to 107.85 M (G1) | 27 | 103 GB |
| F-20261126-052133-10f9a5f | B2, binary alone m/16 to 140 M (G2) | 39 | 150 GB |
| F-20261121-203247-961801d | C, P1b m/12 to 20 M (G2) | 7 | 37 GB |
| F-20261126-131751-89eaff8 | C2, P1b m/12 to 106.69 M (G2; to continue) | 66 | 320 GB |
| F-20261119-150017-b45ec5f | P1, m/8 to 280 M (G1, closed) | 57 | 162 GB |
| R16n, R12, R8 (F-20261121-130351-04074e1, -153707-1eaa5d4, -130358-6cf186a) | binary alone | 8, 7, 6 | 31, 28, 17 GB |

Sizes of batch 35 (`du --apparent-size`), A2's updated from `nrpic-run finish` (854 GB of outputs
in all). A2's restart files between 87 and 133 M are needed for F1's polished-search test (G2);
C2's newest (`rst/hills.00072.rst`) for its continuation.

## Packages and their state

| package | state | what remains |
|---|---|---|
| stage/G1 | C8 met with the 200-M clause; collect, verify (cache) PASS, report (batch 41) | the full pass (above); the signature is orch's |
| note | v2.1 (24 pages; schematics to core-v0.8) | v3: the passage to 200 M with a figure script (A + A2 trackers and finder summaries; hrms and the integral of H beside each mass), ledger rows from the batch-41 reader runs, the reverse fates, the junk at P1b's spheres |
| binary_conv | A2 closed; B2, C2 closed | README "Results" rows for A2 (200 M), B2; C2's continuation (G2) |
| stage/review_wave3 | b21_a2_state.py, b34_horizons.py, b11_passage.py | b11_passage: m1's energies after the merger meaningless, M pre-merger; the figure label "mean expansion" of b34_horizons is status column 10, an integral |
| g2mesh | cut 2026-11-20 | G2M-1b outcome; G2M-2/3 |
| novelty | kb's claims5: claim 451 superseded by 638 | SCOPING l. 210 cites the paper locator, not the id: nothing to change |

## Files to read first

`CLAUDE.md`; `STATUS.md`; `JOURNAL.md` batch 41 (D35 outcomes); `stage/G1/OPEN.md`,
`stage/G1/CHECKLIST.md` C8, `stage/G1/GATE_REVIEW.md`; `stage/REVIEW-wave3.md` batch 41;
`RISKS.md` (R25); `coord/DECISIONS/0048-rulings-after-batch-34.md` item 2; core's outbox
`20261128T021500Z__to-F-hills__found-flag-hmean-tol-and-v05-restarts.md` (column 10 is an integral;
`hmean_tol` is an abort test; a v0.5 restart file under v0.8 is untested: one-cycle check).

## Decisions pending

- orch: the signature of G1 (0048 item 2) after the full pass; retention of the restart files.

## Traps

- Status column 10 and the summary's hmean ("mean_expansion") are the surface INTEGRAL of H
  (a length): area-mean H = col10 / (16 pi m^2). Texts before batch 41 call it a mean.
- Status rows end with `# <reason in words>`: `nrread.read_table` skips them; use
  `b34_horizons.status()` or `b21_a2_state.status_rows()`.
- 'found' is not converged: read the summary's hrms (column 9) beside every mass (R25).
- The summary's column 3 is the mass with spin; the status file's column 7 is the area mass.
- Status files hold repeated rows after restarts (517 rows for 447 search times over 186-200 M).
- A2's directory starts at 61.80 M: always read A + A2 joined (`b11_cards.trackers("A")`).
- `fastflow/diagnostics=true` on the command line of a core-v0.5 restart is FATAL; only `-i <file>`
  works (A2 kept its core-v0.5 executable `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`).
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
