#!/usr/bin/env bash
# All card runs of the random-number work package in one allocation (short job):
#   sbatch -p preempt --gres=gpu:1 -c 4 -t 00:15:00 -J core-rng -o <log> \
#          tracks/core/analysis/rng/gpu_job.sh <card exe> <baseline card exe> \
#          <key file> <processor D1 directory> <processor D2 directory>
# Each part is a registered run (runreg.py --card); the card time of a part is its wall
# time inside the allocation.
set -uo pipefail
EXE=$1; BASE=$2; KEYS=$3; D1REF=$4; D2REF=$5
REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
R=tracks/core/analysis/rng
cd "$REPO"
nvidia-smi -L

python3 $R/runreg.py --card --kind production \
  --purpose "Random-number unit test on one A100, final source: table of draws, cost per call from 4e9 keys" \
  --input "$EXE" --input "$KEYS" --input problems/tests/rng_test.athinput -- \
  "$EXE" -i "{repo}/problems/tests/rng_test.athinput" "problem/key_file=$KEYS" \
  problem/ntime=4e9 -d .

python3 $R/runreg.py --card --kind production \
  --purpose "Draws keyed by cells on one A100: checksums per refinement level for seven divisions, against the Python twin" \
  --input "$EXE" --input $R/run_cell_check.py -- \
  python3 "{repo}/$R/run_cell_check.py" --exe "$EXE"

python3 $R/runreg.py --card --kind production \
  --purpose "Demonstration D1 on one A100: test kick keyed by particle tag, analytic metric, 10000 particles to t = 40; layouts, restart, controls; checksums against the processor run" \
  --input "$EXE" --input $R/run_kick_demo.py --input problems/tests/rng_kick_analytic.athinput -- \
  python3 "{repo}/$R/run_kick_demo.py" --exe "$EXE" --case analytic --np 10000 --tlim 40 \
  --ref "$D1REF"

python3 $R/runreg.py --card --kind production \
  --purpose "Demonstration D2 on one A100: test kick with the metric on a uniform mesh, 10000 particles; layouts with and without kick, restart with removal; checksums against the processor run" \
  --input "$EXE" --input $R/run_kick_demo.py --input problems/tests/rng_kick_mesh.athinput -- \
  python3 "{repo}/$R/run_kick_demo.py" --exe "$EXE" --case mesh --np 10000 --tlim 40 \
  --ref "$D2REF"

python3 $R/runreg.py --card --kind production \
  --purpose "Regression on one A100: executable built from the unmodified source against the final executable, five existing set-ups, every output file compared byte by byte" \
  --input "$BASE" --input "$EXE" --input $R/run_regression.py -- \
  python3 "{repo}/$R/run_regression.py" --base "$BASE" --new "$EXE"
echo "gpu_job finished"
