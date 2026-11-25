#!/usr/bin/env bash
# Entry 13, test D: S2's t = 0 slice on mesh A with another cloud (cic) and without cloud compensation (pcs0), and a
# repeat (ref); one thread, in sequence; then edge_compare-style ratios and |H| on the coarse levels.
#   edge_d.sh <outdir>
set -uo pipefail
OUT=$1
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160436-462452d
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
DECK=$HERE/../../conv_ball/decks/nest16_L16.athinput
TAB=$(ls "$D/S2"/*.tab | head -n 1)
NRP=$(ls "$D/S2/nestA"/*_track.nrp | head -n 1)
NT=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$D/S2/nestA/tracked.json")
COMMON=(problem/comp0_file=$TAB particles/particle_file=$NRP particles/traj_ntrack=$NT time/nlim=0)
rc=0
for spec in "D-ref:" "D-cic:particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0" \
            "D-pcs0:particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0"; do
  NAME=${spec%%:*}; EXTRA=${spec#*:}
  mkdir -p "$OUT/$NAME"
  # shellcheck disable=SC2086
  ATHENA_EXE=$EXE THREADS=1 "$ROOT/scripts/cpu_run.sh" "$OUT/$NAME" "$DECK" "${COMMON[@]}" $EXTRA > "$OUT/$NAME.out" 2>&1 || rc=$?
done
python "$HERE/edge_d_read.py" --run "$OUT" --ref /data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160633-594a474/S2-A0 --out "$OUT" || rc=$?
exit $rc
