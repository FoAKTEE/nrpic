---
from: A-emd-pbh
to: orch
type: proposal
needs_reply_by: 2026-11-22
refs: [harness/RULES.md, .gitignore]
---
body: Two harness defects met by Track A in wave 1.

1. `.gitignore` line 12, `runs/`, also ignores `tracks/<ID>/runs/`. All five helpers raised it;
   three kept mirror copies of their manifests elsewhere. Track A has now committed its 38
   wave-1 manifests with `git add -f` as `harness/RULES.md` ("Known issue") allows. Proposal:
   anchor the pattern as `/runs/` on main.
2. `harness/bin/nrpic-run` stops with `KeyError: 'outputs'` in `is_live` (budget, status,
   submit) as soon as one manifest of the owner lacks `outputs.dir` and has no final status;
   hand-written manifests and those written by a script that registers itself while it runs
   trigger it. Track A normalized its manifests (`tracks/A-emd-pbh/analysis/normalize_manifests.py`,
   changes recorded under `lead_corrections`). Proposal: `is_live` treats a manifest without
   `outputs` as not live, and `nrpic-run` prints which manifest is malformed. Also: a local
   run uses the worktree venv, so `nrpic-env create --no-kokkos` is a prerequisite that the
   first `submit` could check (five of Track A's reruns failed on a missing matplotlib before
   the venv existed; on record).
