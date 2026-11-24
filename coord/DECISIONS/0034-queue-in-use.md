# 0034 The shared queue in use; rulings on the owners' wrappers

Status: ACCEPTED · 2026-11-24 · orchestrator (decision 0017)

1. Since 13:00 PST on 2026-11-24 every card run goes through `harness/bin/nrpic-queue`
   (decision 0033 item 7). Batch 12 moved the runs that had been cancelled into it: 33
   entries of A, B, C, D, F and core; the dispatcher keeps the account at five jobs. Track
   E's last sequencer, which could still submit beside the queue from a worktree that had
   not merged main, was stopped by process id at 13:15 PST; its one unfinished run is
   queued with priority 0.
2. Priorities: 0 for a run a request of the user waits for (now: the reproduction of
   decision 0028), 2 for a run a gate package waits for, 5 for the rest. An owner that
   marks more than four entries with priority 2 says in its HANDOFF which gate item each
   serves.
3. A `--cmd` wrapper of an owner may, at dispatch, make one path-limited commit of the
   run's manifest on the owner's branch in its own worktree (asked by A, C and D). It
   submits at most one job and refuses outside the dispatcher.
4. A chain cut by its segment cap or by a preemption is continued in place from its newest
   restart file, within the card-hours registered for the run (decision 0032 item 2);
   this is now done through the queue.
5. Still owed by the harness (after decision 0026 item 7): a process name for chains
   through `nrpic-run` (asked by D), incremental checksums in `nrpic-stage verify` (asked
   by B), an independent review of the queue tool's code, and the three texts that still
   name `nrpic-run` as the way to submit.
