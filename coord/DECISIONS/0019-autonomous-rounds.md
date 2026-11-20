# 0019 Wave 3: autonomous rounds, cooperative pause, release clerk, hook installed

Status: ACCEPTED · 2026-11-20 · orchestrator (user instructions: "maximal parallelism",
"pause the workflow when usage reaching 95% weekly", "continue and maximally span the
workflow")

1. What happened on 2026-11-19. The usage watcher reported 95 per cent of the weekly
   limit at 08:21 PST, 59 minutes after 76 per cent, with about thirty agents at work.
   The pause did not happen: stopping the workflows needed a turn of the orchestrating
   session, and that session did not get one before the limit was reached (its own model
   had run out earlier the same morning [JUDGEMENT]). Waves 2b and 3a ended at the limit
   with 39 of 65 agents finished. The work of the others is in their worktrees.
2. The pause is now cooperative. `nrpic-usage watch` writes the flag `locks/PAUSE` when
   the weekly or the five-hour window reaches 95 per cent; every agent checks the flag
   before each step and at least every ten minutes and winds down by itself (CLAUDE.md).
   `nrpic-usage resume` removes the flag after the reset; the orchestrator then starts
   the workflows again. Every step is written to be restartable.
3. Rounds. Each owner works in rounds without waiting for the orchestrator: a planner
   reads the owner's state and writes the briefs of up to six independent packages
   (`tracks/<ID>/PLAN-wave3.md`), helpers do them in parallel, the lead rechecks and
   brings the stage packages up to date, and an independent reviewer writes
   `GATE_REVIEW.md` for every gate the lead calls complete. The orchestrator signs gates
   from those reviews (`coord/GATES.md`).
4. Core. Wave 3 first merges the seven wave-2 branches (release candidate core-v0.4),
   then finishes and merges the nine wave-3a branches (core-v0.5), then works in rounds on
   the tracks' open requests in eight spare worktrees (`wt/core-s1` to `-s8`). A release
   clerk acts for the orchestrator (amends 0003): when core's lead has written
   `tracks/core/RELEASE-<version>.md` with a passing byte regression, the clerk merges
   `core/nrpic` into main, creates and pushes the tag, builds the release executables
   `.work/build_{gpu,cpu}_<version>`, copies the interface documents to
   `coord/INTERFACES/` and announces the release to all owners.
5. The git pre-commit hook is installed for all worktrees
   (`core.hooksPath = harness/hooks`), after the dry run of `coord/digests/hook-dryrun.md`
   found no true finding and the corrected hook refused no legitimate commit;
   `python/tests/**` is added to core's OWNERSHIP. The session hooks and permission
   rules stay uninstalled.
6. Waivers. The checksum failure of run B-20261115-164157-40b9f6d (outputs moved into its
   run directory after it finished) is waived; such waivers are listed in
   `coord/WAIVERS.md`, one run id per line with the reason.
7. Limits per session: six processor cores, two card jobs per owner in the queue.
