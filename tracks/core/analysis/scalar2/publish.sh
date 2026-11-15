#!/bin/bash
# Publishes the executables of branch core/scalar-2 for the tracks' scouting runs
# (decision 0013): copies the card and processor executables built from <commit> to
# /data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/ with the files COMMIT and READY.
#   publish.sh <commit of the source> <card exe> <processor exe> <READY text file>
set -euo pipefail
C=$1; G=$2; P=$3; R=$4
D=/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2
mkdir -p "$D"
cp "$G" "$D/athena_gpu"
cp "$P" "$D/athena_cpu"
{
  echo "$C"
  echo "branch core/scalar-2; source of athenak/ at this commit"
  sha256sum "$D/athena_gpu" "$D/athena_cpu"
} > "$D/COMMIT"
cp "$R" "$D/READY"
ls -la "$D"
