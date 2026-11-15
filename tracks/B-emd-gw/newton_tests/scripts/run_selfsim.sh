#!/usr/bin/env bash
# Test N3 (self-similarity): the ellipsoid of the 2605.04487 shape at alpha = 0.05, 0.1,
# 0.2, each run an exact rescaling of the benchmark run (alpha_b = 0.11122237, box
# half-width 12, step 0.02, end 15.5 at mesh n): lengths times alpha_b/alpha, times
# times (alpha_b/alpha)^(3/2), the mass fixed (G M T^2/L^3 is invariant). Lengths of the
# three runs differ by exact factors of two.
#
#   run_selfsim.sh <n> [alpha ...]
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
n=$1; shift
alphas=${*:-0.05 0.1 0.2}
mb=$(( n < 64 ? n/2 : 32 ))
for al in $alphas; do
    read -r half dt tlim snap < <(python3 - "$al" <<'EOF'
import sys
ab, al = 0.11122237, float(sys.argv[1])
s = ab/al
print("%.17g %.17g %.17g %.17g" % (12.0*s, 0.02*s**1.5, 15.5*s**1.5, 3.875*s**1.5))
EOF
)
    "$here/run_case.sh" "alpha_$al" ellipsoid "--n $n --half $half --ppd 2 --alpha $al" \
        "$here/../inputs/ellipsoid.athinput" \
        mesh/nx1="$n" mesh/nx2="$n" mesh/nx3="$n" \
        meshblock/nx1="$mb" meshblock/nx2="$mb" meshblock/nx3="$mb" \
        mesh/x1min=-"$half" mesh/x1max="$half" mesh/x2min=-"$half" mesh/x2max="$half" \
        mesh/x3min=-"$half" mesh/x3max="$half" \
        particles/dt="$dt" time/tlim="$tlim" particles/snap_dt="$snap"
done
