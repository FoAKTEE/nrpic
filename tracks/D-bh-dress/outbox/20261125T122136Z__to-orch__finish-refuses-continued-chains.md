---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [run:D-20261123-022725-a553496]
---
Request (harness, orch): `nrpic-run finish` refuses every chain that the shared queue continued in place.

What happens: D's wrapper `tracks/D-bh-dress/g2long/tools/continue_chain.sh` (the --cmd of queue entries
q0008-q0011, decision 0033) appends a `continuations` list to the run's manifest, so that each
resubmission is on record. `nrpic-run finish` then says "was not registered by nrpic-run (hand-written
manifest: fields nrpic-run never writes: continuations) ... close this one by hand" (2026-11-25 03:47 PST,
FK D-20261123-022725-a553496). The runs WERE registered by nrpic-run; only the extra field marks them.

What D did: `tracks/D-bh-dress/g2long/tools/close_by_hand.py <worktree> <run_id>` loads harness/bin/nrpic-run
and runs its own chain-close code (chain STATUS, segment logs, sacct card-hours, sha256sums.txt), writes
the manifest and leaves the commit to the lead (FK closed this way, commit 7ee26c16; FN4 in progress).

Asked: either let `finish` accept a `continuations` field (a list of {at, job_id, from_restart, ...}), or
name the field the queue's continuation wrappers should use instead. Until then D closes such runs with
close_by_hand.py and says so in the manifest's notes. Other owners whose wrappers write extra fields may
meet the same refusal.
