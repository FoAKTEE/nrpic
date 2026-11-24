---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0033-queue-cap-five.md, CLAUDE.md]
---
Guardrail set by the user on 2026-11-24: at most FIVE jobs of this account in the Slurm queue at
once, pending, held and running together, over all owners (decision 0033; CLAUDE.md, machine
section).

Done at 12:00 PST: every owner's sequencer was stopped (A, B, C, D, F, core) and every job of ours
that was waiting in the queue was cancelled, except the four continuation runs of the reproduction
(Track E) and one running chain of Track C. A chain of C that had run for one minute was stopped
with the chain helper. Nothing that had computed for longer was stopped.

For every owner, from now on:
- `git merge main` first: your copy of `harness/bin/nrpic-run` then refuses a card run when five
  jobs are queued. Submit only through it. Never `sbatch`, `gpu_batch.sh` or `submit_chain.sh`
  directly, never jobs held behind one another, and do not start a sequencer.
- Your runs that were cancelled while waiting: close them in the run tool as stopped
  (`nrpic-run finish <id> --status stopped`), list them in HANDOFF.md with the exact command that
  submits each again (a cut chain is continued from its newest restart file), and submit them when
  the queue has room, or hand them to the shared queue `harness/bin/nrpic-queue` once it exists.
- Order while the cap binds: the reproduction's runs first, then runs a gate package waits for,
  then the rest in turn over the owners.
