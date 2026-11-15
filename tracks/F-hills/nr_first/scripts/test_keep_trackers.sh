#!/usr/bin/env bash
# E5 of nr_first/JOURNAL.md: the tracker-keeping wrapper and the merging reader across a
# restart in the same directory, on processors (small mesh, a few cycles):
#   segment 1: wrapper -i single_P025 (5 levels, coarse wave zone), 8 cycles; restart files
#              at t = 0 (start) and at the end (Finalize)
#   segment 2: wrapper -r <restart of the end of segment 1>, to cycle 12 (a chain segment)
# Then nrread.read_trackers must give cycles 0-12 once each, a repeated row equal to that
# of segment 1 (processor runs are byte reproducible), and the horizon summary without
# duplicates. (A restart from an older file, as after a preemption, is the overlap case of
# test_nrread.py synthetic.)
# Usage (from the worktree root, through nrpic-run): test_keep_trackers.sh [outdir]
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/F-hills
W=$WT/tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh
S=$WT/tracks/F-hills/nr_first/inputs/single_P025.athinput
OUT=$(cd "${1:-${NRPIC_RUN_DIR:?outdir}}" && pwd)
export NRPIC_REAL_ATHENA=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
D=$OUT/run
mkdir -p "$D"
SMALL="mesh_refinement/num_levels=5 z4c_amr/radius_0_reflevel=1 mesh_refinement/max_nmb_per_rank=400"
# shellcheck disable=SC2086
(cd "$D" && "$W" -i "$S" -d "$D" $SMALL time/nlim=8 > "$OUT/seg1.log" 2>&1)
cp -p "$D/single.co_0.txt" "$OUT/seg1_co_0.txt"
last=$(ls "$D"/rst/single.*.rst | sort | tail -1)
(cd "$D" && "$W" -r "$last" -d "$D" time/nlim=12 > "$OUT/seg2.log" 2>&1)
ls -R "$D/trk_keep" > "$OUT/trk_keep.listing"
"$WT/.venv/bin/python" - "$D" "$OUT" <<'EOF'
import json, os, sys
import numpy as np
sys.path.insert(0, "/data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/scripts")
import nrread as nr
d, out = sys.argv[1], sys.argv[2]
res = []
def check(name, ok, det):
    res.append(dict(test=name, ok=bool(ok), detail=det)); print(("PASS " if ok else "FAIL ") + name + ": " + det)
live = nr.read_tracker(os.path.join(d, "single.co_0.txt"))
seg1 = nr.read_tracker(os.path.join(out, "seg1_co_0.txt"))
check("live tracker file holds only segment 2 (truncated on restart)", live["iter"][0] in (8, 9),
      f"live cycles {live['iter'][0]}..{live['iter'][-1]} ({len(live['iter'])} rows)")
files = nr.tracker_files(d, 0)
check("wrapper kept a copy of segment 1", len(files) == 2, f"{files}")
m = nr.read_trackers(d)[0]
check("merged: cycles 0-12 once each", list(m["iter"]) == list(range(13)), f"{list(m['iter'])}")
ov = np.intersect1d(seg1["iter"], live["iter"])
if ov.size:
    a = seg1["x"][np.searchsorted(seg1["iter"], ov)]
    b = live["x"][np.searchsorted(live["iter"], ov)]
    check("repeated cycles identical in both segments", np.array_equal(a, b), f"cycles {ov.tolist()}, max diff {np.max(np.abs(a - b)):.1e}")
h, nmiss = nr.read_horizon([os.path.join(d, f) for f in os.listdir(d) if "horizon_summary_0" in f][0])
raw = nr.read_table([os.path.join(d, f) for f in os.listdir(d) if "horizon_summary_0" in f][0])
check("horizon summary: duplicates removed", len(np.unique(h["t"])) == len(h["t"]), f"{len(raw)} rows written, {len(h['t'])} kept, {nmiss} without a horizon")
json.dump(res, open(os.path.join(out, "test_keep_trackers.json"), "w"), indent=1)
sys.exit(0 if all(r["ok"] for r in res) else 1)
EOF
