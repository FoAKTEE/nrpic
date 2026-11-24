# 0033 At most five jobs of the account in the Slurm queue (supersedes 0025 item 5 and 0031 item 5)

Status: SET BY THE USER · 2026-11-24 ("add guardrail - from now on do not queue more than 5
jobs (including running ones) at once")

1. The rule. At most five jobs of this account are in the Slurm queue at any time:
   pending, held and running jobs count alike, over all owners together. It replaces the
   rule of two eligible jobs per owner with further jobs held behind them (0025 item 5)
   and the exception of six for Track E (0031 item 5).
2. What was done at once (2026-11-24 12:00 PST). The queue held 23 jobs of ours. The six
   sequencers of A, B, C, D, F and core were stopped by process id; one chain of Track C
   that had run for a minute was stopped with the chain helper; seventeen pending or held
   jobs were cancelled. Five jobs remained: one running chain of Track C and the four
   continuation runs of the reproduction (decision 0028) that were still queued. No run
   that had computed for more than a minute was stopped. The runs that were cancelled
   while waiting are named in their owners' HANDOFF files and manifests; they are
   submitted again under the cap.
3. Enforcement. `harness/bin/nrpic-run submit` refuses a card run (launchers batch and
   chain) when five jobs of the account are queued or running, and when `squeue` does
   not answer; no option or environment variable lifts it (`QUEUE_CAP`). The check is in
   every worktree's copy once the owner has merged main, which every session does first.
   Sessions submit only through that tool. Owners start no sequencers of their own.
4. A chain resubmits its next segment from inside the running job, so for the seconds of
   the hand-over the ending job and its successor are both listed. That is accepted; a
   chain never holds more than one job otherwise.
5. A shared queue for all owners (`harness/bin/nrpic-queue`: one dispatcher that submits
   the next waiting run when fewer than five jobs are queued, in turn over the owners) is
   being built by a harness session; until it exists, runs that wait are listed in the
   owners' HANDOFF files and submitted by sessions. The fixture test of the cap in
   `harness/tests/test_nrpic_run.py` is part of that work.
6. Order while the cap binds: the runs of the reproduction first, then runs that a gate
   package waits for, then the rest in turn over the owners.
