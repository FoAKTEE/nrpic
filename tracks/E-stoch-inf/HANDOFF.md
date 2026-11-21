# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) passed G0 (2026-11-20) and G1
(2026-11-21, with reservations; coord/GATES.md). G2 is in production: the USR criteria are fixed
in `spec/scope/SCOPE.md` section 4c, and package `g2prod` loads the cards unattended.

Run next: cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox --show

## Card runs in flight (package g2prod, release card build core-v0.6)

Predictions per run: `g2prod/JOURNAL.md` entry 1 (written before the first submission).
Submitted by the lead of batch 5 (2026-11-21 12:29 PST), batch jobs:
- T, timing (40 steps at 256^3, 320^3, 384^3): run E-20261121-202929-43dcc9c, Slurm 4827.
  Read: `grep -h 'cpu time\|zone-cycles\|cycle=' scratch/E-stoch-inf/E-20261121-202929-43dcc9c/T*/athena.log`
  (outputs in /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/<name>/). Judge prediction T.
- P256v6, slow roll 256^3 (G1 reservation 2): run E-20261121-202935-31520bc, Slurm 4828.
  Compare with E-20261115-172618-f948386 using `ladder/scripts/` (P256_judge as in ladder README).
Then the sequencer submits, in this order, one chain each (labels of `g2prod/queue.txt`):
U256ap, U256am, U320ap, U256bp, U256bm, U320am, U256hp, U256hm, U256nc. Output of a chain:
/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/ (dumps usr.sf.000NN.dump, records
usr.sf.hst, usr.sf.con.hst; chain state in chain/).

Sequencer (setsid, started 12:29 PST, pid in the file below; outlives sessions):
- See:   cat /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/state.tsv  (label, run id, status, time)
         tail -20 /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/seq.log
         ps -o pid,etime,cmd -p "$(cat /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/pid)"
         squeue -u $USER -o '%i %j %T %M' | grep ' E-'
- A chain: scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>
- Stop the sequencer: touch /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/STOP (exits within
  5 min; running chains go on), or kill <numeric pid from the pid file>. Stop a chain:
  harness/bin/nrpic-run stop <run_id>.
- Restart it (if it died; it skips labels already submitted or finished):
  cd /data/haiyangw/nrpic/wt/E-stoch-inf && setsid nohup bash tracks/E-stoch-inf/g2prod/scripts/sequencer.sh > /data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/nohup.out 2>&1 < /dev/null &
- It closes finished runs itself (`nrpic-run finish`, which commits the manifest on this branch);
  push those commits at the next session. It needs `tracks/E-stoch-inf/g2prod/` committed: never
  leave uncommitted edits there. A submission refused by the allotment (10 card-hours toward
  G2) is retried every 15 min; the last three labels need earlier runs closed or a larger
  allotment (asked of orch, outbox of this session).
- A chain that ends FAILED with "MAX_SEGMENTS reached" (preempted too often) resumes from its
  newest restart: edit MAX_SEGMENTS in <rundir>/chain/config.sh, then
  ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena JOB_NAME=<run_id> PROC_NAME=E-<label> MAX_SEGMENTS=<n> scripts/submit_chain.sh <rundir> tracks/E-stoch-inf/g2prod/inputs/usr_prod.athinput <athena args of the manifest's command>
  and record it in g2prod/JOURNAL.md (it is a hand restart, outside nrpic-run).
- Before U320ap starts (third label): read the timing T; if 320^3 does not fit or is slower than
  4 s per step, touch STOP and rethink the queue.

## Packages

- `g2prod` (in progress): runs above; analysis (entry 2) when they have run: reuse
  `usr/scripts/analyse_cards.py`, `floor_split.py`, `lockstep_shells.py` (U-A0..U-A3, odd/even
  parts, floor) and `window/scripts/analyse_window.py` readers; judge SCOPE 4c and the predictions
  of entry 1; figures for each criterion, looked at.
- `window`, `a4res`: finished and reviewed in this session (`stage/REVIEW-wave3.md` Part C).
- R0 restart check: run E-20261121-202941-da16544 (processors); outcome in JOURNAL (this session).

Files to read first: `STATUS.md`; `spec/scope/SCOPE.md` 4c; `g2prod/JOURNAL.md`; `stage/G2/CHECKLIST.md`;
`stage/REVIEW-wave3.md` Part C; `RISKS.md` (R1, R13, R17, R21-R24).

Decisions pending: orch: allotment toward G2 (20 asked); whether a 384^3 pair is wanted (third
rung of U-R). Owner, at the G2 package: "the USR case is reproduced" against SCOPE 4c.

Traps:
- `nrpic-stage verify` fails on `runs` while card jobs are submitted; never delete or commit
  another package's files to silence it.
- Pair dumps only at equal recorded times (|dt| <= 1e-9). Cold 256^3 dumps: read sequentially
  (seek + fromfile), never through numpy's memmap; 320^3 dumps are 5.8 GB each.
- `<abs M/[M]>` of the record is not even in s late in USR; compare pairs on dumps' odd/even parts.
- The odd halving is 2 by construction of the floor (two amplitudes): only the even halving is a
  test (SCOPE 4c, U-A4'(b)).
- Large figure PDFs stay in run directories; commit PNGs. Commit path-limited; `nrpic-run
  finish` and `nrpic-ctx post/ack` commit by themselves.
- `$NRPIC_RUN_DIR` in a command: inside `bash -c '...'`. A local `nrpic-run submit` blocks unless
  --background; never wrap it in `timeout`.
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, gates 674-686,
  verification suite 834-860, context protocol 957-1004, M11 544-547.
