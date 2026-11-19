# 0017 The open decisions are settled; the orchestrator decides from here on

Status: ACCEPTED (user instruction of 2026-11-19: "continue and dont ask for my permission
again, all agreee") · orchestrator

The user agreed to every provisional ruling and asked not to be asked again. So:

1. Decisions 0002, 0005, 0006, 0007, 0013, 0014, 0015 and 0016 are ACCEPTED as written.
2. From now on the orchestrator decides what the brief leaves to "the group": gate
   sign-offs (the orchestrator's review of a stage package is the sign-off, recorded as a
   tag `stage/<ID>/G<k>-pass-<date>`), changes of gate criteria, card-time allotments,
   the scope of a track, retiring a worktree whose branch is merged. Each such decision is
   recorded here in `coord/DECISIONS/` with its reason; none waits for an answer.
3. 0002. The program builds on its own implementation. No agent contacts the authors of
   arXiv:2611.12831 or anybody else outside: writing to people is not something a session
   does for the user.
4. 0008. The proposed Claude Code configuration is adopted in two steps and only between
   waves, never while agents are running: first the git pre-commit hook of
   `harness/hooks/` after a dry run over the existing history of every owner branch shows
   it would not have refused a legitimate commit; then the session hooks and permission
   rules after one trial session in a scratch worktree. The setting that switches the
   project's auto memory off is left out: the memory holds the user's standing
   instructions.
5. What still goes to the user, as information and not as a question: results, failed
   predictions, and anything that would spend money, publish outside the repository's
   remote, or delete work.
