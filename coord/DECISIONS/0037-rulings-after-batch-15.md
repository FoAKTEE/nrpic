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

