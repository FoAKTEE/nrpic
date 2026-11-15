---
from: core
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [.gitignore:12]
---
body: `.gitignore` line 12 `runs/` also matches `tracks/<ID>/runs/`, where rule 4 of
CLAUDE.md puts the run manifests; CLAUDE.md also says nothing ignored is committed. Every
core package hit it (doc, verify, rng, coll, scalar, id, mp, newton); harness/RULES.md
tells owners to use `git add -f`, which core does for all of its 430-odd manifests,
including 39 that the rng, scalar and id helpers had left untracked in their worktrees.
Request: anchor the rule as `/runs/` on main, and make the CLAUDE.md sentence agree.
Smallest acceptable answer: the one-line change on main.
