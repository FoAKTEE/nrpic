# Runbook: driving the program, and adding a second account

## What limits the speed

One account carries about a dozen agent sessions to the end of their packages per
five-hour usage window, and about four such windows per week (decision 0020, measured
2026-11-20). Cards and processors are not the limit. More agents on the same account do
not add work; more accounts at the same time do.

## The orchestrating session (this account)

- Batches: `harness/workflows/nrpic-batch-1.js` is the pattern (a fixed list of packages
  taken from the planners' briefs in `tracks/<ID>/PLAN-wave3.md`).
- Rounds per owner (planner, helpers, lead, gate review):
  `harness/workflows/nrpic-rounds.js` with arguments
  `{"owners": ["A-emd-pbh"], "rounds": 1, "aux": []}`; six helpers per owner is more than
  one window carries for more than two owners.
- Core's release pipeline: `harness/workflows/nrpic-core-wave-3.js`.
- With every launch: `python3 -u harness/bin/nrpic-usage watch --threshold 95
  --five-hour-threshold 80` and `python3 -u harness/bin/nrpic-usage resume`, both in the
  background. The watcher writes `locks/PAUSE`; agents wind down by themselves; the
  resume timer removes the flag after the reset.
- Gates: `coord/GATES.md`. Decisions: `coord/DECISIONS/`. State of every owner:
  `harness/bin/nrpic-ctx board`.

## A second session on another account

Each owner has its own worktree and branch, so two sessions do not collide as long as
they drive different owners. In a second terminal on this machine:

1. `cd /data/haiyangw/nrpic`, start Claude Code there and sign in to the other account.
2. Give it this instruction (owners as agreed with the first session, for example the
   tracks the first session is not driving in its current batch):

   > You are a second orchestrating session of the NRPIC-cosmology program. Read
   > CLAUDE.md, coord/RUNBOOK.md, coord/DECISIONS/0017 to 0020 and coord/GATES.md. Drive
   > only the owners E-stoch-inf and F-hills: run the workflow
   > harness/workflows/nrpic-rounds.js with the arguments {"owners": ["E-stoch-inf",
   > "F-hills"], "rounds": 1, "aux": [], "flag": "PAUSE2"}; beside it run, in the
   > background, NRPIC_PAUSE_FLAG=PAUSE2 python3 -u harness/bin/nrpic-usage watch
   > --threshold 95 --five-hour-threshold 80 and NRPIC_PAUSE_FLAG=PAUSE2 python3 -u
   > harness/bin/nrpic-usage resume. Do not touch main except to read it; do not sign
   > gates, merge core or create tags: report the leads' results and stop.

3. The flag name `PAUSE2` keeps the two accounts' pauses apart: each watcher reads its
   own account and stops only its own agents.
4. Only the first session writes `coord/`, signs gates, merges core into main and
   creates tags.
