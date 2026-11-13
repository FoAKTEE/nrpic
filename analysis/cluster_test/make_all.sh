#!/usr/bin/env bash
# Regenerate every figure and results/*.json of the cluster test from runs/cluster_test/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
for s in fig_invariants fig_phase_mixing fig_deposit_conservation fig_density_convergence \
         fig_excision fig_throughput; do
  echo "=== $s"
  python3 "$s.py"
done
