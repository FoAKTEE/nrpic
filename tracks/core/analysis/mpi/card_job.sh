#!/usr/bin/env bash
#SBATCH -J core-mpi-cards
#SBATCH -p preempt
#SBATCH --gres=gpu:2
#SBATCH -c 4
#SBATCH -t 00:30:00
# Card test of work package mpi (tracks/core/JOURNAL-mpi.md, entry on the card test):
#   C1a, C1b  cluster of test T3 on one card, twice (the scatter of card runs with deposit:
#             the atomic additions of the deposit are not ordered on a card)
#   C2        the same on two cards
#   F8a       vacuum three-puncture mesh of Track F at m/8 (2332 MeshBlocks), 10 cycles,
#             one card;  F8b  the same on two cards
#   F16       the mesh at m/16 (4502 MeshBlocks, more than one card holds), 10 cycles, two
#             cards
# GPU memory and utilisation are sampled every 0.5 s into <run>/gpumem.csv.
#   sbatch --wait card_job.sh <outdir with cluster.nrp, cluster.tab> <exe> <worktree>
set -u
OUT=$1; EXE=$2; WT=$3
MPIRUN=/home/emost/codes/openmpi/bin/mpirun
BIND=$WT/tracks/core/analysis/mpi/gpu_bind.sh
CL=$WT/problems/tests/mpi_cluster.athinput
TC=$WT/problems/tests/mpi_two_card_triple.athinput
M8="mesh_refinement/num_levels=11 refined_region_punc0/level=10 refined_region_punc1/level=10 refined_region_punc2/level=6"
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false
ulimit -c 0
cd "$OUT" || exit 2
{
  echo "host=$(hostname) job=${SLURM_JOB_ID:-none}" \
       "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset} cpus=$(nproc) start=$(date -Is)"
  nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.used --format=csv
} > job.info 2>&1

run() {   # run <name> <ranks> <athena arguments...>
  local name=$1 np=$2; shift 2
  mkdir -p "$OUT/$name"
  nvidia-smi --query-gpu=timestamp,index,memory.used,utilization.gpu \
             --format=csv,noheader,nounits -lms 500 > "$OUT/$name/gpumem.csv" 2>/dev/null &
  local mon=$!
  local t0 t1 rc
  t0=$(date +%s.%N)
  "$MPIRUN" --bind-to none -np "$np" -x CUDA_VISIBLE_DEVICES -x OMP_NUM_THREADS \
            "$BIND" "$EXE" "$@" -d "$OUT/$name" > "$OUT/$name/run.log" 2>&1
  rc=$?
  t1=$(date +%s.%N)
  kill "$mon" 2>/dev/null; wait "$mon" 2>/dev/null
  echo "$name ranks=$np exit=$rc wall_s=$(python3 -c "print(round($t1 - $t0, 2))")" \
    | tee -a "$OUT/summary.txt"
}

CLA="particles/particle_file=$OUT/cluster.nrp problem/comp0_file=$OUT/cluster.tab"
# shellcheck disable=SC2086
run C1a 1 -i "$CL" $CLA
# shellcheck disable=SC2086
run C1b 1 -i "$CL" $CLA
# shellcheck disable=SC2086
run C2 2 -i "$CL" $CLA
# shellcheck disable=SC2086
run F8a 1 -i "$TC" $M8
# shellcheck disable=SC2086
run F8b 2 -i "$TC" $M8
run F16 2 -i "$TC"
echo "end=$(date -Is)" >> job.info
