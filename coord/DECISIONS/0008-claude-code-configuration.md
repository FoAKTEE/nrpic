# 0008 Activation of the project's Claude Code configuration

Status: ACCEPTED in the staged form of decision 0017 item 4 (2026-11-19); before that provisional

The hooks, permission rules and project skills of brief section 11.5 are written and
tested under `harness/` (`harness/claude/` holds the proposed `.claude/` tree). They are
not installed as the live `.claude/settings.json` of this project until the user confirms:
installing them changes how every session in this project executes tools, including the
orchestrator's own running job, and a faulty hook would stall all tracks at once. Until
then the same rules are enforced by the session prompts, by `nrpic-ctx audit` and by the
orchestrator's review of every stage package.
