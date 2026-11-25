# HANDOFF of D-bh-dress

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-25 04:30 PST, lead of batch 17): G0 and G1 signed (G1 with reservations, coord/GATES.md).
G2 in scouting, package NOT complete (stage/G2/OPEN.md section 1). This session closed and judged FK, FF4,
FE4 (g2long/JOURNAL.md entries 18-21) and read FN4 whole and FNQ partially. Owner D-bh-dress, branch
`track/D-bh-dress`, worktree `wt/D-bh-dress`.

Run next: `cd /data/haiyangw/nrpic/wt/D-bh-dress && git merge --no-edit main && harness/bin/nrpic-ctx inbox &&
  git status --short && harness/bin/nrpic-queue list --owner D-bh-dress && squeue -u $USER -o '%i %j %T %r' |
  grep ' D-'; harness/bin/nrpic-run status | grep -E '\?|\*'`

Files to read first: `STATUS.md`; `g2long/JOURNAL.md` entries 6 (P1-P14), 10 (N1-N4, Q1-Q3, L1-L5), 12 (XN),
15 (XQ, L5), 18-21 (this session); `stage/G2/OPEN.md` (lacks item by item, relaxed-lapse table);
`stage/REVIEW-wave3.md` sections 19-20.

## First: FN4's close (left running at the end of the session)

`g2long/tools/close_by_hand.py /data/haiyangw/nrpic/wt/D-bh-dress D-20261124-134157-b17938b` was started at
03:58 PST (pid 2709328; log `scratch/D-bh-dress/tmp/close_fn4_b17.log`). It checksums ~45 GB and then WRITES
the manifest without committing. When the log says "closed ...": check `git diff
tracks/D-bh-dress/runs/D-20261124-134157-b17938b/manifest.json` and commit it path-limited. If the process
died (session end kills it) the manifest is unchanged: run the tool again (it re-hashes everything, ~25 min;
`nohup`, one core). `nrpic-run finish` refuses this manifest (field `continuations`; request to orch
2026-11-25). Then, with predictions N1 (entry 10) and XN (entry 12) unchanged:
- N1: `nrpic-run submit --kind scouting --gate G2 --launcher local --package tracks/D-bh-dress/g2long --package
  tracks/D-bh-dress/g2runs --package tracks/D-bh-dress/flux_tools ... -- python3 tracks/D-bh-dress/g2runs/tools/
  esf_criteria.py --run $S/D-20261124-134157-b17938b --base esflk4n --data $S/D-20261124-130942-29c5de2
  --control $S/D-20261121-203124-a34cf1f/v1l.horizon_summary_0.txt --tau_max 650 --out '$NRPIC_RUN_DIR'`
- XN: `g2long/tools/xc_plane.py --out '$NRPIC_RUN_DIR' ES-FLK=$S/D-20261123-022725-a553496:esflk:0.125
  ES-FLK4N=$S/D-20261124-134157-b17938b:esflk4n:0.125` (+ ES-FLKQ when FNQ has ended; XQ).
- N2/N3 already read (np_partial D-20261125-115729-011d028, before the close): rerun np_partial after FNQ ends.

## Card runs (release core-v0.6 card executable, plain 1+log, faces +-768 M)

S = /data/haiyangw/nrpic/scratch/D-bh-dress; run directory = $S/<run id>.

| Run | Run id | Queue | State (04:30 PST) | Read by |
|---|---|---|---|---|
| FK ES-FLK (N) | D-20261123-022725-a553496 | q0008 done | closed (by hand), judged: P7-P10 hold, P11 failed | entry 19 |
| FF4 ES-FL4 (growth M/4) | D-20261123-022727-1c17e73 | - | closed, judged: P12 holds with V-1L4 control, P13 failed, P14 holds | entry 20 |
| FE4 ES-1L4 (null M/4) | D-20261123-022726-1b133af | - | closed, judged: P5 REFUTED (4.6e-3 at 300 M), P6 failed | entry 21 |
| FN4 ES-FLK4N (4N) | D-20261124-134157-b17938b | q0009 done | tlim 400 M (job 5280), close by hand running | N1, XN next |
| FNQ ES-FLKQ (N/4) | D-20261124-172725-2f426b6 | q0010 running | job 5279, ~177 M of 400 at 04:11 | Q1-Q3, XQ; np_partial |
| FL16 ES-FL16 (growth M/16) | D-20261124-172745-72472ed | q0011 waiting (prio 1 eff.) | never ran | L1-L5 (L3 with Delta M from 20 M) |

- FNQ and FL16 are continued in place by `g2long/tools/continue_chain.sh` through the queue; when a chain ends
  "FAILED (MAX_SEGMENTS reached)" before tlim, add it again: `harness/bin/nrpic-queue add --label D-FNQ-2
  --priority 2 --cmd 'tracks/D-bh-dress/g2long/tools/continue_chain.sh <run id> [new max_segments]'` (dry run
  first with `--dry-run`). Never sbatch, never submit_chain.sh by hand, no sequencer.
- Close each with `g2long/tools/close_by_hand.py` (both have `continuations`), commit the manifest yourself.
- No new queue entries were added this session (OPEN.md section 1: everything else is processor and writing
  work); none removed.

## What G2 still lacks (stage/G2/OPEN.md)

C1 G2 verifier; C2 FNQ, FL16, FN4's N1; C3 region norms (XN, XQ, L5); C6 rerun script; C10/C11 particle and
mesh figures; C13 G2/REVIEW.md or a pointer; C14-C16 note v3 and schematics; C17 verifier. C7 holds at M/8 and
M/16 but FAILS at M/4 (P5 refuted): ask orch for a ruling in the next G2 package report (whether the coarsest
member may lie outside the convergent regime). The relaxed lapse is not used in G2 (OPEN.md section 2).
`nrpic-stage verify D-bh-dress G2 --no-checksums` was run this session (log `$S/tmp/stage_verify_g2_b17_nock.log`).

## Traps (kept from earlier sessions; new ones marked)

(1) every input sets `fastflow/metric_drvts = interpolant` and `particles/ah_exc_factor = 0.8`. (2) ES data:
puncture bare mass m_p = 1.0239688282062387 (ES-F: 1.0). (3) psi = 1 outside the ES ball. (4) A non-finite run
exits 3 with `<base>.guard.txt`. (5) Tracers carry m = 1e-30. (6) trajmet records have 17 doubles; proper time
is index 12. (7) The finder writes into `-d`. (8) The finder summary repeats times across restarts: take the LAST
record (fluxio.read_horizon does). (9) Never kill by pattern; never remove files through a path built from a
shell variable. (10) `nrpic-ctx ack` renumbers the inbox: ack by file name. (12) Restart numbers are not times.
(13) `nrpic-run submit` refuses an unclean package: commit the journal first. (16) Horizon excision stops once the
smallest horizon radius exceeds 4 x initial_radius_0 (nrpic.cpp:451-455) - FK confirms this moves (iii) and D3.
(17) The production finder sits up to ~6e-5 off the converged mass. (18) Removal records of preempted segments:
fluxio.drop_overlaps. (19) NEW: `nrpic-run finish` refuses manifests with `continuations`: close_by_hand.py.
(20) NEW: the M/4 finder's t = 0 mass is 1.0330: read growth at M/4 from 20 M, and judge each mesh against
the vacuum control of the same mesh (V-1L4 for M/4). (21) NEW: closes of 40 GB chains take 10-25 min each and
several owners close at once (I/O): start them first, in the background, one at a time.
