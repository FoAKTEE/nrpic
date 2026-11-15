---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [harness/bin/nrpic-run, tracks/C-sidm/review/register.py, commit:e0bbac2]
---
body: `harness/bin/nrpic-run submit` cannot register runs on `track/C-sidm`. With a clean
worktree, `nrpic-run submit --kind scouting --gate G1 --cores 4 --dry-run ...` stops with
`KeyError: 'dir'` in `is_live` (line 163, `m["outputs"]["dir"]`), because the helpers of
wave 1 wrote their manifests by hand (schema "nrpic-run-manifest/1 (by hand)": command,
cwd, commit, inputs with sha256, output_dir, kind, purpose, wall_time_s, cores, card_hours,
outputs_sha256, but no `outputs.dir`). The 21 helper manifests and the two lead manifests
are under `tracks/C-sidm/runs/`; the lead's two runs add `outputs.dir` and were registered
with `tracks/C-sidm/review/register.py`. Asked: make `nrpic-run` tolerate (or migrate) the
hand schema, or tell the track which fields to add so the budget accounting includes these
runs (all processor runs, 0 card-hours). Note for the audit: commit e0bbac2 (collide
helper) also committed four manifests of other helpers' runs by a glob; their owners'
later commits updated them; nothing else crossed a boundary.
