---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: 2026-12-13
refs: [run:A-20261115-182329-ad14d95]
---
Harness observations from wave 2 of Track A. (1) nrpic-run submit --package works in the shared worktree once the helpers' work is committed: every lead run of this session used it. The helpers' runs were registered by hand because the --package option came after they started; their manifests say so. (2) When several helpers commit tracks/A-emd-pbh/runs/ path-limited, one helper's commit sweeps another's manifests (commits bfdd224, e104537): harmless but confusing; registering through nrpic-run (which commits each manifest itself) avoids it. (3) My own slip, for the RULES: an argument '$NRPIC_RUN_DIR' in single quotes after -- is not expanded by nrpic-run local and the script wrote into a directory of that literal name in the worktree root (run A-20261115-182329-ad14d95, output moved into its run directory). Either expand $NRPIC_RUN_DIR in the command words, or say in RULES.md to wrap such commands in bash -c.
No reply needed.
