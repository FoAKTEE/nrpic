# HANDOFF of F-hills

State in three lines (2026-11-25 09:30 PST, end of the batch-21 lead session, processors only):
- G0 signed. G1 NOT met: the complete vacuum passage (C8) and the G1 verifier (C18) are missing
  (stage/G1/STATUS.md, OPEN.md, STAGE_REPORT.md). Everything else of G1 passes.
- The passage A + A2 (m/16) has reached 96.23 M: the pair's own closest approach (2.11 M at 76.4 M)
  passed unmerged; the pair is 13 M from M and closing; nothing of the trajectory is lost.
- A2's chain continues as it is (decision and prediction: JOURNAL.md batch 21). Its next segment
  (Slurm 5294) waits: both cards are held by another partition until about 2026-11-26 06:46 PST.

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Card runs of this owner (shared queue only, decision 0033; see `harness/bin/nrpic-queue list --owner F-hills`)

| | queue id | run id (job) | what | gate, ceiling | read by |
|---|---|---|---|---|---|
| A2 | q0001 (submitted) | F-20261124-210400-902c650 (Slurm 5294 PENDING; 13 attempts so far, 5.64 card-hours) | P1b m/16 from A's restart 23 (61.80 M) to tlim 200; restart every 1 M; last record 96.23 M (restart 63) | G1, 19.5 card-h, MAX_SEGMENTS 19 (13 used) | `stage/review_wave3/b21_a2_state.py`, `b11_passage.py` (both join A + A2) |
| B2 | q0002 (waiting) | at dispatch | pair alone m/16 from B's restart 34 (107.85 M) to 140 | G2, 5 | `b11_cards.py` |
| C2 | q0003 (after F-B2) | at dispatch | P1b m/12 from C's restart 6 (20.0 M) to 200 | G2, 24 | `b11_passage.py` (C + C2), `b11_cards.py` |

A2's chain: executable `binary_conv/scripts/athena_resume_bc.sh` -> byte copy `scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`
of core-v0.5's card build (do not delete it). The wrapper copies the tracker files into
`<rundir>/trk_keep/<UTC stamp>/` before each start; `nr_first/scripts/nrread.py` joins them
(later segment wins from its first time). Job 5294 carries the old chain script (a preempted
attempt counts); from segment 15 on the worktree's script (01747be45) does not count attempts cut
by a signal. When MAX_SEGMENTS is reached the chain ends FAILED "MAX_SEGMENTS reached": then (after
orch's answer to outbox 20261125T171002Z a2-tail-plan) raise MAX_SEGMENTS in
`scratch/F-hills/F-20261124-210400-902c650/chain/config.sh` and continue it through ONE `--cmd`
queue entry (harness/RULES.md "Shared card queue": the wrapper runs `harness/bin/nrpic-queue
check-dispatch || exit 1`, `JOB_NAME=<run_id>`, records a continuation in the manifest; dry run
first), within the 19.5 card-hours. DO NOT add `fastflow/diagnostics=true` to EXTRA_ARGS: a
parameter absent from the restart file is fatal at start-up (JOURNAL batch 21, finding).

## Exact commands for the next session

1. Read A2 again when it has new records (registered, 1 core, a minute each):

       harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/stage \
         --parent F-20261124-210400-902c650 --parent F-20261121-203144-b2cf16b \
         --purpose "A2 state to its last record; S1-S6 / A2-2" \
         -- .venv/bin/python tracks/F-hills/stage/review_wave3/b21_a2_state.py --out '$NRPIC_RUN_DIR'

   and the same form with `b11_passage.py` (add `--parent F-20261121-203247-961801d`). Judge A2-2
   (closest approach of the pair's centre of mass to M: 8-11 M at 95-115 M) and the batch-21
   prediction on the cap (125-140 M, 10-14 card-hours). Prediction first in JOURNAL.md.
2. When A2 has ended: `harness/bin/nrpic-run finish F-20261124-210400-902c650`; judge A2-3 to
   A2-5; still to add to the readers: the bound member's pericentre and eccentricity, HRNA and
   EIH overlays, the remnant near M, the waveform (p1's readers); then ask the fresh G1 verifier
   (stage/G1/OPEN.md item 2 lists the material and what the verifier must know).
3. Close the G1 package: `harness/bin/nrpic-stage collect F-hills G1`, `verify` (once with
   `--full` before review), `report`. Checksum caches of A, C, P1, R16n, R8, R12 were being built
   in the background at the end of batch 21 (`nrpic-run verify`, log
   `scratch/F-hills/tmp/cache_warm_b21.log`; it commits nothing).
4. Disk: A2 writes a 5.8 GB restart per M. When it has ended, keep every fifth restart file and
   the newest (delete by literal path, never through a shell variable), or ask orch.

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | runs A2 (chain), B2, C2 (queued) | README "Results" row for m/16 at 20 M and B's result |
| stage/review_wave3 | b21_a2_state.py, b21_horizon_recheck.py (batch 21) | rerun on A2's next records |
| note | v2 in note/ (24 pages) | v3 with the passage; legend of fig_elliptic; floats after Sec. VI; reviewer step |
| g2mesh | cut 2026-11-20; `scripts/card_analysis.py` committed as WIP, untested | G2M-1b outcome; G2M-2/3 analysis |
| novelty | kb's answer on claim 452 (2026-11-24): 2610.20594 is a Peters-equation method for triples, not PN N-body dynamics | reword NOVELTY.md if it calls both "follow-ups on PN N-body" |
| junk_gauge, kerr, eih, p1, nr_first, khsr_note | closed | T3 junk at P1b's spheres (A + A2 waveforms) |

## Files to read first

`CLAUDE.md`; decisions 0033, 0040 (items 3, 4), 0041 (items 4-6); `STATUS.md`; `JOURNAL.md`, the
batch-21 entry (predictions S1-S6, H1-H4, outcomes, the decision and its prediction, the finding on
diagnostics); `RISKS.md` (R10, R20, R22); `stage/G1/OPEN.md`; `stage/REVIEW-wave3.md` (batch 21).

## Decisions pending

- orch: A2's tail (outbox 20261125T171002Z a2-tail-plan): continuation at the cap within 19.5
  card-hours; up to 5 more card-hours of G1 if preemptions eat the margin.
- core: the finder's status file on a restart (outbox 20261125T171002Z finder-diagnostics-on-restart);
  older: HRNA pair-force spec, wave extraction beyond l = 8, H-norm2 transient in R8.

## Traps

- A preempted attempt of job 5294 still counts as a segment (old chain script in that job).
- A2's directory starts at 61.80 M: always read A + A2 joined (b11_cards.trackers("A")).
- Horizon summaries: a failed search repeats the previous row; no run of ours has status files;
  column 1 is the integrator stage, not the cycle; a sawtooth band up to 4e-3 in accepted m_AH rows
  remains (fit slopes).
- nrpic-run finish of a 100+ GB run reads everything once (B took minutes with the cache; first
  passes can take an hour on a busy disk); its commit lands at the end.
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
