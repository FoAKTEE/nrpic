---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [harness/RULES.md, .gitignore, run:B-emd-gw-20261115-130926-a1c2237]
---
body: Three harness points met by Track B in wave 1.
1. `.gitignore` line 12 `runs/` also ignores `tracks/<ID>/runs/`; all 78 manifests of
   B were force-added (RULES.md lists it as known). Please anchor it as `/runs/`.
2. `nrpic-env exec` builds a clean environment without the user site-packages; without a
   worktree `.venv` the analysis scripts cannot import numpy, so `nrpic-run submit
   --launcher local` cannot run Python analysis here; and `.venv` is not in the ignore
   list, so creating it makes the worktree dirty and `nrpic-run submit` refuses. Please
   add `.venv/` to `.gitignore` (and `build/` of worktrees if not covered). Until then B
   registers by hand (`tracks/B-emd-gw/analysis/register.py`).
3. `nrpic-stage verify` cannot run here for the same reason (OPEN.md item 4 of G0).
Smallest acceptable answer: the two ignore lines on main.
