# HANDOFF of F-hills

State in three lines (2026-11-21 13:00 PST, end of the lead session of batch 5):
- G0 signed (coord/GATES.md). G1 NOT met: no complete Hills passage yet, KHSR, note compile, G1
  verifier (stage/G1/STATUS.md, OPEN.md).
- Rule P1b-D held (clause D1): the binary alone at m/12 and m/16 gives the same orbit; P1b at
  m/16 (A) and the isolated binary's extension (B) are on the cards, P1b at m/12 (C) waits behind B.
- Open risk R19: the converged isolated pair shrinks by 0.2 M in 20 M; B shows whether it merges
  (then A and C cannot test the passage and must be stopped) or turns around (eccentric start).

Owner F-hills, branch `track/F-hills`, worktree `/data/haiyangw/nrpic/wt/F-hills`. Start every
session with `cd /data/haiyangw/nrpic/wt/F-hills && git merge --no-edit main`, then
`harness/bin/nrpic-ctx inbox`, then `test -e /data/haiyangw/nrpic/locks/PAUSE`.

## Card jobs of this owner (submitted 2026-11-21 12:31-12:33 PST)

| | run id | what | segments | first job |
|---|---|---|---|---|
| A | F-20261121-203144-b2cf16b | P1b: passage q = 4 as P1, members m/16, tlim 200 (G1) | 31 (25.9 card-h) | 4832 |
| B | F-20261121-203156-03efdd3 | R16n extension: binary alone, m/16, from R16n restart 7 (t = 23.34 M) to 120 M (G2) | 13 (10.9 card-h) | 4836 |
| C | F-20261121-203247-961801d | P1b at m/12, tlim 200 (G2), HELD until B ends | 25 (20.9 card-h) | 4837 (held) |

All three run the byte copy of release core-v0.5's card build
(`scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu`: do not delete it) behind a wrapper that keeps
tracker files across restarts in `<rundir>/trk_keep/` (A, C: `athena_keep_trackers_bc.sh`; B:
`athena_resume_bc.sh`, whose first segment ran `-r .../F-20261121-130351-04074e1/rst/hills.00007.rst`,
so B's run directory starts at t = 23.34 M: join it to R16n's directory when reading).
No lapse_leak in any of them (constant shift_eta = 2, as P1).

See them:

    squeue -u $USER -o "%i %j %T %r"
    scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/<run id>
    harness/bin/nrpic-run status <run id>

Sequencer (keeps C held while B runs, releases it when B's chain/STATUS is DONE, FAILED or
STOPPED, then exits; writes only its log): started with setsid nohup at 12:32 PST.

    cat /data/haiyangw/nrpic/scratch/F-hills/seq/seq.pid; ps -p <pid>
    tail /data/haiyangw/nrpic/scratch/F-hills/seq/seq.log
    stop it without releasing C:  touch /data/haiyangw/nrpic/scratch/F-hills/seq/STOP
    release C by hand:            scontrol release <job id of C>   (squeue -u $USER -n F-20261121-203247-961801d)
    restart it (if the machine rebooted and B still runs):
      setsid nohup /data/haiyangw/nrpic/scratch/F-hills/seq/seq_release.sh \
        /data/haiyangw/nrpic/scratch/F-hills/F-20261121-203156-03efdd3 F-20261121-203247-961801d \
        >> /data/haiyangw/nrpic/scratch/F-hills/seq/seq.log 2>&1 < /dev/null &

Stop a chain: `scripts/submit_chain.sh --stop <rundir>` (never by pattern). Close a finished one:
`harness/bin/nrpic-run finish <run id>` (checksums every file: minutes per 30 GB).

## Reading the runs (predictions and the stop criterion: JOURNAL.md, batch 5, runs A-C)

1. B first, when it has passed about 70 M (six segments): registered analysis with
   `binary_conv/scripts/analyze.py` (README "Analysis"). analyze.py reads one directory per
   run: either add a join of R16n (`F-20261121-130351-04074e1`, 0-23.34 M) and B, or pass B as
   its own run and compare from 23.34 M. Question: does s(t) reach a minimum and rise (reading E,
   eccentric start) or fall to a common horizon (reading I)?
2. If B shows a common horizon of the isolated pair before P1b's pericentre: stop A and C
   (`--stop`), record it, and plan start states from a GR quasi-circular prescription.
3. A and C, when they end: P1's reader `nr_first/scripts/p1_analysis.py <rundir>
   --baselines=nr_first/results/baselines_p1.json` and the predictions A1-A5, C.

## Packages and their state

| package | state | what remains |
|---|---|---|
| binary_conv | runs A-C in flight; reviewed (REVIEW-wave3, batch 5) | README "Results" row for 20 M at m/16 (now 4.756 M); read B, A, C |
| junk_gauge | closed, reviewed | T3 to be remeasured at P1b's spheres |
| kerr | closed, reviewed | Fermi-frame tidal reference for L_z > 0; Fig. afin; geodesic_binary S4 in 'bks'; numba in requirements |
| p1 | chain DONE, finished | analysis to t = 280 M (`p1/README.md`); no longer decides G1 |
| note | paused | corrections list (`note/JOURNAL.md`), registered `run_all.py`, compile, checker, pages |
| g2mesh | cut; `scripts/card_analysis.py` UNCOMMITTED (left alone, not mine to commit) | G2M-1b outcome; G2M-2 analysis of F-20261120-222810-e408386; cost table |
| KHSR | not started | one result of 1201.4794 with newton3 (`e_orb`; SCOPING 5) |

## Files to read first

`CLAUDE.md`; decisions 0022-0025; `STATUS.md`; `JOURNAL.md` last entry (batch 5: P1b-D outcome,
predictions of A-C); `RISKS.md` (R19, R15, R17); `stage/REVIEW-wave3.md` (batch 5 section);
`stage/G1/STATUS.md`, `OPEN.md`.

## Decisions pending

- orch: an analysis session this week to read B and apply the stop criterion (outbox
  20261121T204354Z); harness chain restart option (20261121T204401Z).
- core: stray resubmission after a chain's last segment (seen again, jobs 4820 and 4822 ended at
  once); H-norm2 transient at t = 0.5 in R8; HRNA pair-force spec; wave extraction beyond l = 8.

## Traps

- `nrpic-stage verify` fails while g2mesh's file is uncommitted and while chains run; with
  checksums it reads P1's 165 GB (over ten minutes).
- B's directory starts at t = 23.34 M; its tracker and horizon files hold only that part.
- Horizon summaries: a failed search repeats the previous row.
- 1PN references of the binary are not sharp (R17); do not judge the orbit by one of them.
- nrpic-run passes no variable of the caller to a chain: PROC_NAME, SLURM_EXTRA cannot be set.
- Never kill by pattern; `scancel`, `scripts/submit_chain.sh --stop <rundir>`, numeric PIDs.
