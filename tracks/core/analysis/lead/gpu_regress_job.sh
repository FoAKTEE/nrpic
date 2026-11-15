#!/bin/bash
# Lead's card job: byte regression of the existing behaviour, baseline card executable
# (main source 74ed745) against the merged one (609a875), on one A100.
#   (a) rng package driver, cases c1-c5 (c3-c5 deposit particles: a card run is not
#       reproducible run to run there, so they give no verdict)
#   (b) lead's nrpic_cf checks (P2 regression of two set-ups, P5 combined curvature)
# Submit from the worktree:  sbatch tracks/core/analysis/lead/gpu_regress_job.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 2
#SBATCH -t 00:40:00
#SBATCH -J core-lead
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/lead/slurm/gpu_regress-%j.out
WT=/data/haiyangw/nrpic/wt/core
B=$WT/.work/build_gpu_base/src/athena
N=$WT/.work/build_gpu_609a875/src/athena
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
python3 tracks/core/analysis/rng/runreg.py --card --purpose "lead integration: card byte regression c1-c5, baseline 74ed745 vs merged 609a875 (job $SLURM_JOB_ID)" --input $B --input $N -- python3 {repo}/tracks/core/analysis/rng/run_regression.py --base $B --new $N
python3 tracks/core/analysis/rng/runreg.py --card --purpose "lead integration: nrpic_cf checks P2 and P5 on the card executables (job $SLURM_JOB_ID)" --input $B --input $N -- python3 {repo}/tracks/core/analysis/lead/cf_checks.py --base $B --new $N
echo "gpu_regress_job finished"
