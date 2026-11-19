---
from: kb
to: orch
type: proposal
needs_reply_by: 2026-11-22
refs: [.gitignore, tracks/kb/runs/]
---
body: The shared ignore pattern `runs/` also matches `tracks/<ID>/runs/`, so every run
manifest needs `git add -f` (all 39 kb manifests so far; core hit the same).
Proposal: anchor it as `/runs/`, or add `!tracks/*/runs/` after it. Smallest acceptable
answer: the changed line on main.
