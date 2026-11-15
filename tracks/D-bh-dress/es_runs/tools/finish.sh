#!/usr/bin/env bash
# Close the ES-1 and V-1 card runs and analyse them (es_runs, Track D).
#
#   tracks/D-bh-dress/es_runs/tools/finish.sh [--partial]
#
# Run from the worktree root /data/haiyangw/nrpic/wt/D-bh-dress with a clean package.
# 1. Shows the chain state of both runs. Unless both chains are DONE it stops here; with
#    --partial it goes on and analyses what exists (no `finish`).
# 2. Closes both runs with `harness/bin/nrpic-run finish` (wall time, card-hours, checksums).
# 3. Registers the analysis (analyse.py) with nrpic-run, 4 cores, and copies its JSON and
#    figures into tracks/D-bh-dress/es_runs/{results,figs}/ (look at every figure before
#    using it; append the outcome to JOURNAL.md under entry 2).
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/D-bh-dress
S=/data/haiyangw/nrpic/scratch/D-bh-dress
ES=D-20261115-172726-60ba4c2
V1=D-20261115-172730-c6d151b
DATA=D-20261115-170213-d2c2131
PKG=tracks/D-bh-dress/es_runs
cd "$WT"
partial=0
[[ ${1:-} == --partial ]] && partial=1
done_all=1
for r in $ES $V1; do
  st=$(head -1 "$S/$r/chain/STATUS" 2>/dev/null || echo unknown)
  echo "$r: chain $st"
  [[ $st == DONE ]] || done_all=0
done
if [[ $done_all == 0 && $partial == 0 ]]; then
  echo "not both DONE; rerun later or pass --partial to analyse what exists"; exit 0
fi
if [[ $done_all == 1 ]]; then
  for r in $ES $V1; do harness/bin/nrpic-run finish "$r" || true; done
fi
out=$(harness/bin/nrpic-run submit --kind scouting --gate G1 --package "$PKG" --cores 4 \
  --parent $ES --parent $V1 --parent $DATA \
  --purpose "analysis of ES-1 ($ES) and V-1 ($V1): horizon-mass drift against the control, wall and tracers against the exact curves, crossing times of R = 2M, lapse; JOURNAL entry 2$([[ $done_all == 0 ]] && echo ', PARTIAL runs')" \
  -- python3 "$PKG/analyse.py" --es "$S/$ES" --v1 "$S/$V1" --data "$S/$DATA" --t0 100 2>&1 | tee /dev/stderr)
rid=$(echo "$out" | sed -n 's/^registered \([^:]*\):.*/\1/p' | head -1)
[[ -n $rid ]] || { echo "analysis was not registered"; exit 1; }
mkdir -p "$PKG/results" "$PKG/figs"
cp "$S/$rid/es_analysis.json" "$PKG/results/es_analysis.json"
for f in "$S/$rid"/figs/*.png; do cp "$f" "$PKG/figs/"; done
echo "analysis run $rid; results in $PKG/results/es_analysis.json, figures in $PKG/figs/"
