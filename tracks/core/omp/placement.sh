#!/usr/bin/env bash
# Placement experiment: one case at a fixed thread count with four placements, interleaved
# and repeated, so that the changing load of the machine affects all of them alike.
#   placement.sh <case> <threads> <nlim-factor> <rounds> [exe]
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
case=$1; nt=$2; fac=$3; rounds=$4; exe=${5:-O3}
for r in $(seq 1 "$rounds"); do
  python3 "$HERE/scaling.py" --exe "$exe" --cases "$case" --threads "$nt" --repeat 1 --nlim-factor "$fac" --bind none --places none --tag "none$r" --out .
  python3 "$HERE/scaling.py" --exe "$exe" --cases "$case" --threads "$nt" --repeat 1 --nlim-factor "$fac" --bind spread --places cores --tag "spread$r" --out .
  python3 "$HERE/scaling.py" --exe "$exe" --cases "$case" --threads "$nt" --repeat 1 --nlim-factor "$fac" --bind close --places cores --tag "close$r" --out .
  python3 "$HERE/scaling.py" --exe "$exe" --cases "$case" --threads "$nt" --repeat 1 --nlim-factor "$fac" --bind true --places auto --tag "auto$r" --out .
done
