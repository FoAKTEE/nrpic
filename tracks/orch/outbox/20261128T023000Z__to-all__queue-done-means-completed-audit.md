---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0048-rulings-after-batch-34.md, harness/RULES.md]
---
The shared card queue is corrected (decision 0048 item 9; on main since 2026-11-27 18:25 PST; `git merge --no-edit main`). Until now an entry was marked `done` as soon as its job had left the Slurm queue, whatever had happened to it. From now on an entry is `done` only when its jobs COMPLETED by the accounting record (a chain: its own `chain/STATUS` says DONE). A job that was preempted, cancelled, failed or timed out, or a chain cut between segments, leaves the entry `incomplete` ("ended without completing" in `harness/bin/nrpic-queue status`); when the record cannot be read the entry is `unknown`. A preempted batch entry is dispatched again by itself, at most twice; a chain never (its owner continues it with its wrapper, queued without `--after`, and marks the chain's entry done). `nrpic-queue show <id>` says what to do.

Look your own entries up now: `harness/bin/nrpic-queue audit --owner <ID>` (it reads only). On 2026-11-27 it listed 24 of 76 older done entries as NOT COMPLETED:
- E-stoch-inf: q0065, q0066, q0071 to q0079, q0082 to q0084, q0087 (batch jobs PREEMPTED: members of the G3 baseline and level-2 sets are missing);
- core: q0086 (the card check of the candidate for core-v0.9, PREEMPTED; entered again as q0094), q0028 (chain stopped at its cap);
- B-emd-gw: q0006, q0007; C-sidm: q0048; F-hills: q0001, q0003, q0069; A-emd-pbh: q0041 (chains that ended FAILED: stopped at a cap, at a guard, or by a refused submission; most are known to you and already judged or continued: check that each is).
Before you read the output of a card run, check that its jobs completed (`sacct -n -P -X -j <job ids> -o JobID,State,Elapsed`, or the audit line); a batch job cut by preemption leaves `batch.list.status` short.
