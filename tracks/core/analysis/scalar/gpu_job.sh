#!/usr/bin/env bash
# Card runs of the scalar-field work package in one short allocation:
#   (from the root of the worktree)
#   sbatch -p preempt --gres=gpu:1 -c 4 -t 00:40:00 -J core-sf -o <log> \
#          tracks/core/analysis/scalar/gpu_job.sh <card exe>
# Each part is a registered run (runreg.py --card); the card time of a part is its wall
# time inside the allocation.
set -uo pipefail
EXE=$1
REPO=${SLURM_SUBMIT_DIR:?submit with sbatch from the root of the worktree}
[[ -f $REPO/tracks/core/analysis/scalar/common.py ]] || { echo "not a worktree: $REPO"; exit 1; }
R=tracks/core/analysis/scalar
REG=tracks/core/analysis/rng/runreg.py
cd "$REPO"
nvidia-smi -L
export OMP_NUM_THREADS=1

python3 $REG --card --kind production \
  --purpose "Scalar field on one A100: cost of the field and of the stochastic sources next to Z4c, 128^3" \
  --input "$EXE" --input $R/cost.py --input problems/scalar/noise_ms.athinput -- \
  python3 "{repo}/$R/cost.py" --exe "$EXE" --n 128 --block 64 --nlim 20

python3 $REG --card --kind production \
  --purpose "Scalar field test 2 on one A100: homogeneous slow roll against Friedmann and Klein-Gordon" \
  --input "$EXE" --input $R/test2_flrw.py --input problems/scalar/flrw_slowroll.athinput -- \
  python3 "{repo}/$R/test2_flrw.py" --exe "$EXE" --workers 2

python3 $REG --card --kind production \
  --purpose "Scalar field test 4 on one A100: stochastic sources (twin, spectrum, layout, restart, lockstep, kicks)" \
  --input "$EXE" --input $R/test4_noise.py --input problems/scalar/noise_power.athinput \
  --input problems/scalar/noise_ms.athinput -- \
  python3 "{repo}/$R/test4_noise.py" --exe "$EXE" --workers 2

python3 $REG --card --kind production \
  --purpose "Scalar field test 3 on one A100: constraint-satisfying plane perturbation, N = 16, 32, 64" \
  --input "$EXE" --input $R/test3_plane.py --input problems/scalar/plane.athinput -- \
  python3 "{repo}/$R/test3_plane.py" --exe "$EXE" --workers 2

python3 $REG --card --kind production \
  --purpose "Scalar field test 1 on one A100: Klein-Gordon plane wave (orders, dissipation, potentials)" \
  --input "$EXE" --input $R/test1_wave.py --input problems/scalar/kg_wave.athinput -- \
  python3 "{repo}/$R/test1_wave.py" --exe "$EXE" --workers 2
echo "gpu_job finished"
