#!/bin/bash
# Card job of the initial-data solver (test V4 of tracks/core/JOURNAL-idsolve.md): three
# cases at 64 cells with the card executable EXE (a copy of the build), each registered by
# run_registered.py:
#   gauss_code_n64_card        scalar solve (mode code), Gaussian at rest
#   gboost_code_n64_card       moving Gaussian, vector part in stencil form
#   gboost_vcode_n64_card      moving Gaussian, vector part in mode code
# Submit from the worktree:
#   sbatch --export=ALL,EXE=<athena_gpu> tracks/core/analysis/idsolve/card_vector.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:15:00
#SBATCH -J core-idv
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/idsolve/slurm/card-vec-%j.out
WT=/data/haiyangw/nrpic/wt/core-idsolve
IC=/data/haiyangw/nrpic/scratch/core/idsolve_ic
TMP=/data/haiyangw/nrpic/scratch/core/tmp/idsolve
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
MESH="mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32"
REG=".venv/bin/python tracks/core/tools/run_registered.py --card-hours 0.01"
date -u +"start %Y-%m-%dT%H:%M:%SZ"
$REG --purpose "initial-data solver, test V4: scalar solve on a card (gauss_code_n64)" \
    --tag idsolve-v4-gauss_code_n64_card \
    --input problems/idsolve/gaussian.athinput --input $IC/gauss_h0p25.nrp -- \
    "$EXE" -i gaussian.athinput $MESH particles/id_residual=code \
    particles/particle_file=gauss_h0p25.nrp
sleep 2
$REG --purpose "initial-data solver, test V4: vector part, stencil form, on a card (gboost_code_n64)" \
    --tag idsolve-v4-gboost_code_n64_card \
    --input problems/idsolve/gaussian_boost.athinput --input $IC/gauss_h0p25_u0p1.nrp -- \
    "$EXE" -i gaussian_boost.athinput $MESH particles/id_residual=code \
    particles/particle_file=gauss_h0p25_u0p1.nrp
sleep 2
$REG --purpose "initial-data solver, test V4: vector part, mode code, on a card (gboost_vcode_n64)" \
    --tag idsolve-v4-gboost_vcode_n64_card \
    --input $TMP/gaussian_boost_code.athinput --input $IC/gauss_h0p25_u0p1.nrp -- \
    "$EXE" -i gaussian_boost_code.athinput $MESH particles/id_residual=code \
    particles/particle_file=gauss_h0p25_u0p1.nrp
date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "card_vector finished"
