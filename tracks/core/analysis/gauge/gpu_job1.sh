#!/bin/bash
# Card job 1 of the work package "gauge": the expanding ball at cells of M/2 with the old
# and the new lapse (L1), the bound ball at M/4 (L2), its collapse (L3), and the
# Einstein-Straus data (ES).  Every run is registered by grun.py; inside the job
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
EXE=/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_gpu_e41c24a
SRC=e41c24a
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
# L3, collapse of the bound ball with the new lapse
NT=$(python3 -c "import json;print(json.load(open('$IC/t2_bound_h0p25.json'))['traj_ntrack'])")
$PY $G/grun.py --gpu --exe $EXE --source-commit $SRC --time 00:20:00 --tag gc-collapse-leak1 \
  --purpose "bound expanding ball through turnaround and collapse to a black hole, new lapse T = 1 M (test L3)" \
  --inputs $IC/t2_bound_h0p25.nrp $IC/t2_bound_h0p25.tab $IC/t2_bound_h0p25.json \
  --athinput $WT/problems/ball/ball_collapse.athinput particles/traj_ntrack=$NT \
  particles/particle_file=$IC/t2_bound_h0p25.nrp problem/comp0_file=$IC/t2_bound_h0p25.tab
date
# ES, new lapse T = 4 M
$PY $G/grun.py --gpu --exe $EXE --source-commit $SRC --time 00:20:00 --tag gc-es-leak4 \
  --purpose "Einstein-Straus data of Track D for 30 M, lapse relaxation T = 4 M (test ES)" \
  --inputs $ES/es.nrp $ES/es.tab $ES/es.json $ES/es_reference.csv \
  --athinput $WT/problems/es/es_gauge.athinput particles/particle_file=$ES/es.nrp \
  problem/comp0_file=$ES/es.tab
date
echo "gpu_job1 finished"
