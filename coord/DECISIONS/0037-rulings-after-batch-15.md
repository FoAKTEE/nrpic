# 0037 Rulings after batch 15; findings on the queue cap

Status: ACCEPTED · 2026-11-24 · orchestrator (decision 0017)

1. Gate KB-G3 of the knowledge base is signed, pass with reservations (coord/GATES.md).
   The lead supersedes the seven claims the second verifier names, processes the twelve
   abstract-labelled claims without a locator (773 and 774 first), and writes the rate of
   the machine-located claims (about 80 per cent right as worded) beside the mixed rate.
2. Track E's G2 package is complete (every item passes, is not applicable by ruling, or
   is the failure on record of decision 0036 item 2) and goes to an independent gate
   review. The scope of its G3 (tail statistics of the curvature perturbation on boxes
   of 128 cells with many seeds against the one-patch calculation) is ruled on when G2
   is signed. The note's PDF stays in the repository under the hook's limit of 5 MB
   (decision 0021 item 3 exempts note PDFs from the guideline of 1 MB).
3. The queue cap (decision 0033). An independent review of the queue tool on 2026-11-24
   reproduced, against the fake Slurm, six ways past the cap or into a stall: commands
   that call sbatch through the run tool's local launcher or the environment tool; a
   dispatcher that hangs holding its lock; an old command that submits after a restart;
   an alert dodged by a job name; a job lost at a time-out; arrays counted as one. None
   has occurred on the real queue (the dispatcher's log shows every submission at five
   or fewer). They are being fixed by the tool's author with the reproductions as
   regression checks, and a cap keeper is added to the dispatcher: when the account's
   count stays above five at two counts twenty seconds apart it cancels the excess
   pending jobs, newest first, never a running one. The cap cannot be made airtight from
   user level: a limit in Slurm itself (MaxSubmitJobs on the association) needs the
   machine's administrator, and the tool-guard hook that would refuse direct sbatch
   calls of sessions stays not installed (decision 0008) unless the user says otherwise.
4. Added 2026-11-24 21:40 PST: the fixes of item 3 are committed and the dispatcher runs
   them. Each of the reviewer's reproductions is now a regression check (93 checks of the
   queue tool, 92 of the run tool; the whole runner rerun by the orchestrator: no file
   failing). The run tool's local launcher and the environment tool refuse a command
   that reaches Slurm; the cap keeper looks every thirty seconds; priorities 0 and 1
   are the orchestrator's; a waiting entry gains one priority class per eight hours.
   Left open: the dispatcher's marker still reaches the jobs of a wrapper (core unsets
   it in `scripts/` in its next source session; wrappers call `nrpic-queue
   check-dispatch`); the detector of Slurm commands is a heuristic; this round of fixes
   has had no second reviewer.
5. Added 2026-11-25 04:40 PST: the cap keeper never cancels a job that is not this
   program's. The account is also the user's own login, and the keeper of item 4 would
   have cancelled first a job the user submits by hand (it has no queue entry); found by
   the orchestrator on reading the routine, no such job existed. From 03:45 to the
   restart the live dispatcher ran with the cancel step off. Now a job is ours when it
   belongs to a queue entry, or its name is a run id, or its working directory lies
   under the repository; every other job of the account counts toward the five and is
   never cancelled: with an excess the keeper cancels our own pending jobs, and an
   excess that only the user's jobs make is recorded without halting the queue. Known
   consequences: a job submitted by hand from inside the repository counts as ours; a
   pending segment of a chain started before the queue existed is cancelled first.
   Regression checks: seven more (queue tool 100 of 100; runner rerun by the
   orchestrator, no file failing). A second reviewer of items 4 and 5 is sent next.
6. Added 2026-11-25 04:50 PST: the cap keeper reports and cancels nothing. A second
   independent review (scratch/harness/review-queue2/REVIEW.md; reproductions against
   the fake Slurm) showed that the automatic cancel of items 4 and 5 can still hit a
   job that is not the program's (a job named like an entry's job, a job whose id a
   wrapper prints, a working directory printed as null or relative) and can cost the
   program its own runs (a chain waiting between two segments is cancelled, requeued and
   rerun from the start). The keeper was live with the cancel on from 20:32 to 03:45 and
   from 04:12 to 04:41 PST and cancelled nothing in that time (queue log). From 04:41
   the dispatcher runs with the cancel off, and the cancel is being removed from the
   tool: the dispatcher is the only submitter and holds while the count is at or above
   five, so an excess decays by itself; removing one by hand is the orchestrator's.
   The same review showed that the textual detector of Slurm commands in the run tool
   and the environment tool misses ordinary forms and blocks legitimate ones; it is
   being replaced by stubs for sbatch, srun and salloc placed first in the PATH of a
   local run outside a dispatch. The check for more than one new job around a dispatch
   becomes strict again. Still open at user level, as before: a call of sbatch by
   absolute path or from a session's own shell (Slurm-side limit; tool-guard hook).
   Stale copies of the run tool in idle worktrees of finished branches stay as they are:
   no session is sent there; a session that starts in a worktree merges main first.

