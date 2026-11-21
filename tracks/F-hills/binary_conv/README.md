# binary_conv: P1's binary alone at three member resolutions (F-hills, wave 3 batch 3)

Helper package of F-hills. Question, design, cost, predictions and outcomes: `JOURNAL.md`
(BC-0 design and cost, BC-1 prediction, later entries the outcomes).

## Contents

| Path | What |
|---|---|
| `inputs/bin_m8.athinput`, `bin_m12.athinput`, `bin_m16.athinput` | P1's `<problem>` without the heavy hole; mesh R8 / R12 / R16n on +-128 (JOURNAL BC-0) |
| `scripts/athena_keep_trackers_bc.sh` | chain executable: keeps tracker files across restarts, runs the byte copy `bc-ak05-gpu` of release core-v0.5's card build |
| `scripts/tree_cost.py` | MeshBlock trees (g2mesh `tree3.py`) along the Newtonian tracks and card cost to 100 M |
| `scripts/mesh_check.sh` | `athena -m` start trees of the three inputs and `tree_cost.py` (registered analysis) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |

Results, how to rerun and the requests follow when the runs are analysed.
