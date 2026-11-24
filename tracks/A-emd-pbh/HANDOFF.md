# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 11 (wave 3), 2026-11-24 06:20 PST (stopped on the pause flag);
card section rewritten by the session of batch 12, 2026-11-24 13:30 PST (card runs handed to the shared queue).

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 has an interim package (stage/G2:
9 PASS, 10 OPEN, 1 FAIL) that is NOT ready for review: the threshold scan of the expanding ball
holds (code bracket = exact bracket), but the constraint norms do not converge before t ~ 6 (C3
FAIL, cause not named) and the periodic box's horizon is not found (finder fails on four levels).

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short && squeue -u $USER -o "%.8i %.28j %.8T %.10M" | grep " A-" ; harness/bin/nrpic-queue list --owner A-emd-pbh; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112[1-9]"; harness/bin/nrpic-ctx inbox`

Files to read first: `STATUS.md`; `threshold_ball/JOURNAL.md` entries 3-10; `periodic_threshold/JOURNAL.md`
entries of 2026-11-24 (13:00Z to D0); `stage/G2/OPEN.md` and `CHECKLIST.md`; `stage/REVIEW-wave3.md`
section 7; `RISKS.md` rows 27-35.

## Card runs and what reads them (shared queue since batch 12, 2026-11-24 13:30 PST)

On 2026-11-24 12:00 PST the orchestrator stopped this owner's sequencer (pid 207327) and cancelled
the two pending segments 5177 (S1L) and 5178 (C-d0.42) under the user's cap of five queued jobs
(decision 0033). Both chains had computed (segments 5149, 5150 ran 09:43-10:33 PST to their
wall-clock stop), so neither run was closed as stopped: both are continued IN PLACE by the queue.
The two sequencer lines were never submitted (done.txt empty), so they have no run id yet: the
dispatcher registers them when it submits them (manifest committed on this branch: push it).
Every card run now goes through `harness/bin/nrpic-queue` only (RULES.md "Shared card queue"):
no sequencer, no sbatch, no scripts/submit_chain.sh by hand. Look: `harness/bin/nrpic-queue list
--owner A-emd-pbh`, `show <id>` (names the run id once submitted).

| queue id | label | prio | run | what | read by |
|---|---|---|---|---|---|
| q0012 | a-cd042-cont | 2 | A-20261122-173202-f98c79f | C-d0.42, mesh C (M/64), continued from rst/ball.00020.rst (t = 45.96 of 51), MAX_SEGMENTS 21 (16 used) | `threshold_ball/scripts/analyse.py --member C-d0.42` (T4 mesh-C half; `--member B-d0.42` for the pair); G2 OPEN item 3 |
| q0013 | a-p0l6 | 2 | new at dispatch | P0L on six static levels (`periodic_threshold/inputs/peak_leak6.athinput`, to t = 140), chain, 7 card-h asked; queue_b11 line 1 | compare_ltb.py, job2_q.py, line_trapped.py; predictions D1-D5 (periodic_threshold JOURNAL 2026-11-24 13:40Z); G2 OPEN item 2 |
| q0014 | a-cd040 | 2 | new at dispatch | C-d0.40, mesh C, data A-20261124-133456-2d00507 (dc0p4C), to t = 54, chain, 14 card-h asked; queue_b11 line 2 | analyse.py: needs a MEMBERS line `"C-d0.40": (<run dir>, "32:64", "dc0p4", "nestC", 54.0)` whose prep is `A-20261124-133456-2d00507/dc0p4C/nestC` (DATA differs: add a data-dir field); prediction T7 (threshold_ball entry 8); G2 OPEN item 3 |
| q0015 | a-s1l-cont | 5 | A-20261123-025907-97bab8d | periodic S1L, continued from rst/peak.00016.rst (t = 198.7 of 220), MAX_SEGMENTS 9 (5 used) | `periodic_threshold/scripts/job2_q.py` (Q1-Q3 again) and `analyse_scouting.py --gauge leak --run S1L=<dir>` (S1-S3, entry 2026-11-21 13:20Z) |

Priorities: 2 for the runs that items 2 and 3 of `stage/G2/OPEN.md` wait for; 5 for S1L (S1-S3 are
not a G2 item). No `--after`: none of the four needs another's output.

Continuations: `threshold_ball/scripts/continue_chain.sh <run_id> <MAX_SEGMENTS> [--dry-run]` (written
this session; dry runs of both printed the expected command; it refuses outside the dispatcher, with
a job of the chain in squeue, a DONE chain, a changed deck or executable, or no segment left). It
resumes the SAME registered run (same exe, deck, arguments, JOB_NAME = run id, PROC_NAME), submits one
job, appends a line to the manifest's "notes" and commits that path (so pull before you push). If a
chain again closes FAILED with MAX_SEGMENTS reached before tlim (preemption), queue it again:
`harness/bin/nrpic-queue add --label <label>-2 --priority 2 --cmd
'tracks/A-emd-pbh/threshold_ball/scripts/continue_chain.sh <run_id> <higher MAX_SEGMENTS>'`.
Close each run with `harness/bin/nrpic-run finish <run id>` once `scripts/submit_chain.sh --status
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>` says DONE (finish counts every Slurm job in
chain/events.log, the continued segments included).

## The old sequencer (stopped; do not restart)

`threshold_ball/scripts/sequencer.sh` with queue `periodic_threshold/queue_b11.txt` and state
`scratch/A-emd-pbh/sequencer_b11/` was stopped by the orchestrator on 2026-11-24 12:00 PST; both of its
lines are now queue entries q0013 and q0014. Sequencers are forbidden (decision 0033); the script
and queue file stay as a record.

## Processor runs of this session

- A-20261124-132016-ecf12c3 (G1-G3, A-mesh guard stop from the t = 44 restart): G1 repeated the card
  stop exactly (t = 47.921875, cycle 3067, same first cell) [VERIFIED]; G2 (lapse_leak 0) and G3
  (alpha_exc 0.3) see threshold_ball entry 5 outcome (written at the end of the session if they
  finished; otherwise read `scratch/A-emd-pbh/A-20261124-132016-ecf12c3/run.log` and `G2/`, `G3/`,
  then `nrpic-run finish`). Batch 12 saw: run.log ends "exit=0 end=2026-11-24T14:31:16Z" (06:31 PST),
  but the run tool still lists it as "running?": judge G2/G3 against entry 5, then finish it.
- K4 (entry 10): NOT started (pause flag at 06:18 PST); the start command is at the end of threshold_ball/JOURNAL.md.

## Packages and what remains

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | scan judged (entry 4); constraint tests K-K3 refuted (6-9); K4 (10) | mesh C at threshold (C-d0.42, C-d0.40); README.md with the results table; cause of the constraint floor; A-mesh guard stop |
| `periodic_threshold/` | job 2 judged (Q, P, F, D0); S1L continuing; P0L6 queued | S1-S3; D1-D5; README table and DESIGN 7.1; request to core only if the finder fails with the horizon resolved |
| `conv_ball/` | done | second agent on its G2 reading (C18) |
| `verify_bh/` | done; slice-or-finder answered by the scan (entry 4) | nothing |
| `szekeres/` round 1 | cut 2026-11-20 | card series N = 64, 128, 256 to tau = 40 (G2 C1) |
| `periodic_diag/`, `runs_ball/`, `g1close/` | done | nothing |

## Decisions pending

- orch: constraint-bound-ruling (outbox 20261124T133627Z): the 0.1 bound of SCOPE section 3 fails from
  t = 0 in every run; ruling asked after the next constraint test.
- core: refined-mesh-cfl05-result (info, 20261124T133506Z) answers their step-limit-in-work;
  periodic-gamma-driver-step (W31, in work in core's batch 11); bh1r-inte-deficit-two-levels.
- kb: Szekeres conformal-flatness locators (acknowledged) to be cited when szekeres resumes.

## Traps

- With a Gamma-driver keep cfl_number <= 0.6 (decision 0027); lapse_leak x dt below ~2 on the coarsest level.
- No `<z4c> lapse_leak` around an existing black hole for long runs (decision 0025 item 3); the ball
  collapse runs stop 4-8 M after the horizon forms.
- The processor build reads card restart files (F2, G1-G3): cheap processor diagnostics from restarts.
- Chain histories repeat times after a restart from an older restart file: readers must keep the
  records written last (job2_q.py, constraint_conv.py do).
- Markdown tables: never write `||H||` inside a table row (the pipes split the cell).
- Helpers sharing the worktree: commit path-limited; kill processes by numeric PID only.
