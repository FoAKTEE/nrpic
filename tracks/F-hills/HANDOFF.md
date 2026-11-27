# HANDOFF of F-hills

State in three lines (2026-11-27 PST, end of the batch-34 lead session, processors only):
- G0 signed. G1: every criterion met in the lead's judgement (C8 met in batch 34); C18 PARTIAL
  until the fresh verifier reruns its readers on the completed passage. The lead did not pass G1.
- The m/16 passage P1b (A + A2) is complete to 186.0 M: binary disrupted, m1 captured by M (common
  horizon at 137.5 M), m2 recedes after an 8.73-M pericentre, fate undecided; Newton: the reverse.
- No card job of this owner is queued or running. A2, B2, C2 are closed (checksum passes of
  `nrpic-run finish` were started in the background at 15:22 PST; see "Check first").

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Check first

1. The three `nrpic-run finish` calls of batch 34 (logs in `scratch/F-hills/tmp/b34/finish_A2.log`,
   `finish_B2C2.log`) hash about 724 + 150 + 322 GB and commit each manifest at the end. If a
   manifest still says `submitted` (`python3 -c "import json;print(json.load(open('tracks/F-hills/runs/<id>/manifest.json'))['status'])"`)
   and no `nrpic-run finish` process is alive (`ps -u $USER -o pid,args | grep "nrpic-run finish"`),
   rerun (B2 closed at 15:56 PST: completed, 105 files, 3.525 card-hours, commit 2d093aaf9; A2 and
   C2 were still hashing at 16:00 PST, expected to end near 16:45 and 16:35):
   `harness/bin/nrpic-run finish F-20261124-210400-902c650 --status stopped`,
   `harness/bin/nrpic-run finish F-20261126-052133-10f9a5f`,
   `harness/bin/nrpic-run finish F-20261126-131751-89eaff8 --status stopped` (the cache makes a
   rerun cheap for files already hashed). Commit what they leave uncommitted.
2. Inbox: orch's answer to `outbox/20261127T233418Z__to-orch__g1-package-complete-passage-186m.md`
   (G1 review, verifier rerun, retention of A2's restart files) and core's answer to
   `outbox/20261127T233431Z__to-core__finder-found-flag-and-branches.md`.

## Runs of this owner (all closed; none in the queue)

| | run id | state | what | read by |
|---|---|---|---|---|
| A + A2 | F-20261121-203144-b2cf16b + F-20261124-210400-902c650 | stopped at 186.0 M (Slurm I/O error on resubmission) | P1b m/16, G1 | `stage/review_wave3/b21_a2_state.py`, `b11_passage.py`, `b34_horizons.py` (status files 133-186 M) |
| B2 | F-20261126-052133-10f9a5f | DONE at tlim 140 | pair alone m/16 from 107.85 M, G2 | `b11_cards.py` (not yet analysed) |
| C2 | F-20261126-131751-89eaff8 | stopped at 106.69 M (same Slurm error) | P1b m/12, G2 (24 card-hours; 9.37 used) | `b11_passage.py` draws C + C2 (not judged) |

C2's continuation (G2, not urgent): `tracks/F-hills/binary_conv/scripts/continue_chain.sh
F-20261126-131751-89eaff8 <cap> [--extra-input tracks/F-hills/binary_conv/inputs/fastflow_diag.athinput]`
through ONE `--cmd` queue entry, prediction first (`--dry-run` first). Its executable is the byte copy
`scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu` of core-v0.5 (do not delete it).

## Exact commands for the next session

1. If the verifier's rerun has come back (stage/G1/verifier/): answer each finding in
   `stage/REVIEW-wave3.md`, update CHECKLIST C18, then `harness/bin/nrpic-stage collect F-hills G1`,
   `verify F-hills G1` (once with `--full`, detached, before the review), `report F-hills G1`.
2. F1 test (G2 list; after core's answer): polished finder searches on 2-3 of A2's restart files
   between 87 and 133 M (prediction first; processor or card; `<fastflow> polish_iterations_2 = 100`,
   `mass_tol_2 = 1e-5`, and a second search with `mass_tol_2 = 1e-9`).
3. Note v3 (stage/G1/OPEN.md item 4): the passage to 186 M with horizons vs coordinates; HRNA and
   EIH overlays of P1b; the junk at P1b's spheres from A2's waveforms (complete to 186 M).

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | A2, B2, C2 ended | README "Results" rows for A2 (186 M), B2; C2's continuation (G2) |
| stage/review_wave3 | b21_a2_state.py, b11_passage.py, b34_horizons.py (new), b25_diag_restart.py | b11_passage: m1's energies after the merger are meaningless, M's mass is pre-merger |
| stage/G1/verifier | VERIFIER.md batch 22 (to 96.23 M) | rerun on the completed passage (OPEN.md item 2 says what and what it left unchecked) |
| note | v2 (24 pages) | v3 (OPEN.md item 4) |
| g2mesh | cut 2026-11-20; `scripts/card_analysis.py` WIP, untested | G2M-1b outcome; G2M-2/3 |
| novelty | kb's answer on claim 452 | reword NOVELTY.md if needed |
| junk_gauge, kerr, eih, p1, nr_first, khsr_note | closed | T3 junk at P1b's spheres |

## Files to read first

`CLAUDE.md`; `STATUS.md`; `JOURNAL.md`, the batch-34 entry (D34 predictions and outcomes, C25,
A2-3 to A2-5); `stage/G1/OPEN.md`, `stage/G1/STATUS.md` (T4 row), `stage/G1/VERIFIER.md`;
`stage/REVIEW-wave3.md` (batch 34); `RISKS.md` (R24, R25, R26); `coord/INTERFACES/finder_stop.md`.

## Decisions pending

- orch: retention of A2's restart files (724 GB; deleting changes the checksummed record);
  the G1 review.
- core: is "found" with |mean expansion| 24 a defect; may core-v0.8 read core-v0.5 restarts for a
  finder test. Older: HRNA pair-force spec, wave extraction beyond l = 8.

## Traps

- Status rows end with `# <reason in words>`: `nrread.read_table` skips them (the first b34 run
  failed this way); use `b34_horizons.status()`.
- "found" in the status file is the mass rule, not a vanishing expansion (R25): read the mean
  expansion and the flow iterations beside it.
- The summary's column 3 is the mass with spin; the status file's column 7 is the area mass.
- A2's directory starts at 61.80 M: always read A + A2 joined (`b11_cards.trackers("A")`).
- Horizon rows before 133 M have no status file; column 1 of the summary is the integrator stage.
- `fastflow/diagnostics=true` on the command line of a restart is FATAL; only `-i <file>` works.
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
