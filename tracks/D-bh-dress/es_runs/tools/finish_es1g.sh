#!/usr/bin/env bash
# Close the ES-1G card run and analyse it beside ES-1 and V-1 (es_runs, Track D; JOURNAL
# entry 5 has the prediction, written before submission).
#
#   tracks/D-bh-dress/es_runs/tools/finish_es1g.sh [--partial]
#
# Run from the worktree root /data/haiyangw/nrpic/wt/D-bh-dress with a clean package.
# 1. Shows the chain state; unless it is DONE it stops (--partial: analyse what exists).
# 2. Closes the run (nrpic-run finish), prints the "not used" warnings of its log.
# 3. Registers tools/es_extra.py on ES-1, V-1 and ES-1G and copies its JSON to
#    results/es_extra_es1g.json and its figures to figs/es1g/ (look at each one before use).
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/D-bh-dress
S=/data/haiyangw/nrpic/scratch/D-bh-dress
ES=D-20261115-172726-60ba4c2
V1=D-20261115-172730-c6d151b
G=D-20261119-142633-6f72922
DATA=D-20261115-170213-d2c2131
PKG=tracks/D-bh-dress/es_runs
cd "$WT"
partial=0
[[ ${1:-} == --partial ]] && partial=1
st=$(head -1 "$S/$G/chain/STATUS" 2>/dev/null || echo unknown)
echo "$G: chain $st"
if [[ $st != DONE && $partial == 0 ]]; then
  echo "ES-1G not DONE; rerun later or pass --partial"; exit 0
fi
if [[ $st == DONE ]]; then
  harness/bin/nrpic-run finish "$G" || true
fi
echo "--- warnings of the ES-1G log (lapse_leak must not be 'not used'):"
grep -h -i "not used" "$S/$G"/chain/seg*.log 2>/dev/null || echo "(none)"
out=$(harness/bin/nrpic-run submit --kind scouting --gate G1 --package "$PKG" --cores 4 \
  --parent $ES --parent $V1 --parent $G --parent $DATA \
  --purpose "ES-1G ($G) against ES-1 and V-1: lapse and K at the plateau tracers, wall, crossings, horizon mass against the control; JOURNAL entry 5$([[ $st != DONE ]] && echo ', PARTIAL run')" \
  -- python3 "$PKG/tools/es_extra.py" --run "ES-1:$S/$ES:es:es" --run "V-1:$S/$V1:v1:v1" \
     --run "ES-1G:$S/$G:es:es" --data "$S/$DATA" --t0 100 2>&1 | tee /dev/stderr)
rid=$(echo "$out" | sed -n 's/^registered \([^:]*\):.*/\1/p' | head -1)
[[ -n $rid ]] || { echo "analysis was not registered"; exit 1; }
mkdir -p "$PKG/results" "$PKG/figs/es1g"
cp "$S/$rid/es_extra.json" "$PKG/results/es_extra_es1g.json"
for f in "$S/$rid"/figs/*.png; do cp "$f" "$PKG/figs/es1g/"; done
echo "analysis run $rid; results in $PKG/results/es_extra_es1g.json, figures in $PKG/figs/es1g/"
