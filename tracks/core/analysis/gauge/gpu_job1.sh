#!/bin/bash
# Card job 1 of the work package "gauge": the expanding ball at cells of M/2 with the old
# and the new lapse (L1), and the bound ball at M/4 (L2).  Every run is registered by grun.py; inside the job
# scripts/gpu_run.sh runs the executable directly.
#   sbatch tracks/core/analysis/gauge/gpu_job1.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:32:00
#SBATCH -J core-gauge
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/gauge/gpu_job1-%j.out
WT=/data/haiyangw/nrpic/wt/core-gauge
PY=$WT/.venv/bin/python
G=$WT/tracks/core/analysis/gauge
EXE=/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_gpu_b4430da
SRC=b4430da
IC=/data/haiyangw/nrpic/scratch/core/id/ic_ball
ES=/data/haiyangw/nrpic/scratch/core/gauge/ic_es
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
date
# L1, cells M/2
$PY $G/ball_runs.py --gpu --jobs 1 --exact --only mp-n128,leak1-n128,leak2-n128,mp-edge2-n128,leak1-edge2-n128
date
# L2, cells M/4
$PY $G/ball_runs.py --gpu --jobs 1 --exact --only bound-leak1-n160,bound-leak05-n160
date
# The copy of this script that Slurm holds for job 4449 goes on with ES (tag gc-es-leak4)
# and L3 (tag gc-collapse-leak1); both tags are listed in skip_tags.txt and are not run:
# those two tests moved to gpu_job3.sh with shorter relaxation times.
date
echo "gpu_job1 finished"
