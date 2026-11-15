# 0003 Remote and pushing (D3)

Status: ACCEPTED (user instruction "always git track"; standing instruction to commit and
push promptly) · 2026-11-15

Every owner commits on its own branch at the end of every session and pushes that branch
to `origin`. Nobody force-pushes, rebases published commits or pushes another owner's
branch. Tags (`core-v*`, `stage/<ID>/G<k>-*`) are created and pushed by the orchestrator.
A push to any other remote needs the user first.
