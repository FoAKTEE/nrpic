# 0018 Pause at 95 per cent of the weekly usage limit

Status: ACCEPTED (user instruction of 2026-11-19: "pause the workflow when usage reaching
95% weekly") · orchestrator

- The orchestrator keeps `harness/bin/nrpic-usage watch --threshold 95` running in the
  background whenever a workflow runs. It reads the weekly utilisation of the account
  from the `rate_limit_event` of a minimal non-interactive call on the small model
  (Claude Code has no command for plan usage; the status line's `rate_limits` field is
  the only documented source and needs an interactive session). Readings:
  `locks/usage.json`, history `locks/usage.log`.
- When the watcher reports 95 per cent, the orchestrator stops every running workflow at
  once, records which run ids were stopped, and resumes them (same scripts, cached
  results of finished agents) after the weekly window has reset. Agents stopped in the
  middle leave their work in their worktrees, as after the cut-off of 2026-11-15; the
  resumed agents continue from it.
- No new workflow is launched above 90 per cent.
- Six probes in a row without a reading count as unknown, and unknown is treated as at
  the threshold.
- First readings (2026-11-19 07:22 PST): weekly 76 per cent, window resets the same day
  at 14:00 PST; usage beyond the limit is disabled for the organisation, so nothing is
  billed past it.
