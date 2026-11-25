#!/usr/bin/env bash
# Test V of tracks/core/JOURNAL-gauge-2.md on processors: the reduced vacuum control
# problems/es/v1_small.athinput (Track D's V-1GB on a small mesh) with the threaded build.
#
#   vrun.sh <size> <exe> <threads> <outdir> [-z "key = value"]... [athena args...]
#
# size  V4: finest cells M/4, MeshBlocks of 8^3 (root 4 M on +-64 M, 288 MeshBlocks)
#       V8: the file as it is (finest cells M/8, MeshBlocks of 16^3)
# -z    a line added to the <z4c> block of the copy of the input in <outdir> (AthenaK
#       takes on the command line only parameters that the input has; the options of
#       the second pass are read only if present)
set -euo pipefail
size=$1; exe=$2; threads=$3; out=$4; shift 4
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WT=$(cd "$HERE/../../../.." && pwd)
DATA=${V1_DATA:-/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-170213-d2c2131/v1}
mkdir -p "$out"
inp=$out/v1s.athinput
cp "$WT/problems/es/v1_small.athinput" "$inp"
while [[ ${1:-} == -z ]]; do
  line=$2; shift 2
  # insert after the lapse_leak_alpha line of the <z4c> block
  awk -v add="$line" '{print} /^lapse_leak_alpha/ {print add}' "$inp" > "$inp.tmp"
  mv "$inp.tmp" "$inp"
done
args=(particles/particle_file="$DATA/v1.nrp" problem/comp0_file="$DATA/v1.tab")
case $size in
  V4) args+=(mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=8 meshblock/nx2=8
             meshblock/nx3=8 refined_region1/level=4) ;;
  V8) ;;
  *) echo "size must be V4 or V8" >&2; exit 1 ;;
esac
ATHENA_EXE=$exe THREADS=$threads "$WT/scripts/cpu_run.sh" "$out" "$inp" "${args[@]}" "$@" > /dev/null
tail -4 "$out/athena.log"
