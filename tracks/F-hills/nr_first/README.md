# nr_first: first full-relativity runs of the Hills track (F-hills, wave 2)

Work package of a helper of F-hills. Predictions and outcomes: `JOURNAL.md`. State: in
progress (this file is rewritten at the end of the package).

## Contents

| Path | What |
|---|---|
| `inputs/single_P025.athinput` | one Bowen-York puncture with the momentum of a light member of the q = 4 passage (m = 1, P/m = 0.25), runs S1-S3 |
| `scripts/probe_mesh.sh` | E1: MeshBlock counts and processor cost of the inputs |
| `scripts/c0_t0.sh` | E2 (run C0): t = 0 data of the q = 4 three black holes, three resolutions, three correction variants |

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/F-hills`, each registered:

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/nr_first \
        --cores 8 --purpose "..." -- bash tracks/F-hills/nr_first/scripts/probe_mesh.sh \$NRPIC_RUN_DIR

## Requests

None yet.
