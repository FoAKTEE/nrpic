---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0033-queue-cap-five.md, harness/RULES.md, CLAUDE.md]
---
The shared card queue exists (decision 0033 item 7). From now on card runs reach Slurm by one route.

After `git merge main`, from your worktree:

    harness/bin/nrpic-queue add --label <label> [--after <label>] [--priority N] -- <the arguments you would give nrpic-run submit>
    harness/bin/nrpic-queue add --label <label> --cmd '<one command that submits at most one job>'   # a wrapper that continues a cut chain
    harness/bin/nrpic-queue list | status | show <id> | remove <id> | retry <id>

One dispatcher submits the next waiting run when fewer than five jobs of the account are queued, by
priority (0 a request of the user, 2 a run a gate package waits for, 5 the rest) and in turn over the
owners. `nrpic-run submit` with launcher batch or chain is refused outside the dispatcher (its message
prints the `nrpic-queue add` line to use). No `sbatch`, no scripts called directly, no jobs held behind
one another, no sequencers.

Your runs that were cancelled while waiting on 2026-11-24 12:00 PST: close each in the run tool as
stopped, and add it to the queue again (a chain that had already run is continued from its newest
restart file through a `--cmd` wrapper). An entry whose worktree is not clean waits and is tried
again every ten minutes: keep the worktree committed.
