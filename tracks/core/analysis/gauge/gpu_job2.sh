#!/bin/bash
# Card job 2 of the work package "gauge": a puncture alone with and without the lapse
# relaxation (P), the shift damping on one hole (E1) and on an unequal pair (E2).
#   sbatch tracks/core/analysis/gauge/gpu_job2.sh
#SBATCH -p preempt
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH -t 00:28:00
#SBATCH -J core-gauge
#SBATCH -o /data/haiyangw/nrpic/scratch/core/tmp/gauge/gpu_job2-%j.out
WT=/data/haiyangw/nrpic/wt/core-gauge
PY=$WT/.venv/bin/python
G=$WT/tracks/core/analysis/gauge
EXE=/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_gpu_e41c24a
SRC=e41c24a
export OMP_NUM_THREADS=1
nvidia-smi -L
cd "$WT"
run() {   # tag, purpose, input, arguments
  local tag=$1 purpose=$2 inp=$3; shift 3
  date
  $PY $G/grun.py --gpu --exe $EXE --source-commit $SRC --time 00:20:00 --tag "$tag" \
    --purpose "$purpose" --athinput $WT/$inp "$@" -t 00:05:00
}
# E2: unequal pair, mass ratio 4, 4 M
run gc-e2-profile "unequal Bowen-York pair, mass ratio 4, damping profile eta_0 = 2, M_ref = 1 (test E2)" \
    problems/puncture/by_unequal.athinput
run gc-e2-eta2 "unequal Bowen-York pair, mass ratio 4, constant eta = 2 (test E2)" \
    problems/puncture/by_unequal.athinput z4c/shift_eta_profile=false
run gc-e2-eta8 "unequal Bowen-York pair, mass ratio 4, constant eta = 8 (test E2)" \
    problems/puncture/by_unequal.athinput z4c/shift_eta_profile=false z4c/shift_eta=8.0
# E1: one hole of unit mass, momentum 0.3, cells 1/16, 6 M
run gc-e1-eta2 "one boosted puncture, constant eta = 2 (test E1 a)" \
    problems/puncture/by_eta.athinput
run gc-e1-eta20 "one boosted puncture, constant eta = 20 (test E1 c)" \
    problems/puncture/by_eta.athinput z4c/shift_eta=20.0
run gc-e1-prof20 "one boosted puncture, eta_0 = 20 with the profile, M_ref = 0.1 (test E1 d)" \
    problems/puncture/by_eta.athinput z4c/shift_eta=20.0 z4c/shift_eta_profile=true z4c/shift_eta_mref=0.1
# P: puncture at rest, cells 1/8, 20 M, without and with the lapse relaxation
run gc-p-plain "vacuum puncture at rest, cells m/8, plain 1+log (test P)" \
    problems/puncture/by_eta.athinput mesh_refinement/num_levels=5 problem/comp0_p1=0.0 time/tlim=20.0
run gc-p-leak1 "vacuum puncture at rest, cells m/8, lapse relaxation T = 1 (test P)" \
    problems/puncture/by_eta.athinput mesh_refinement/num_levels=5 problem/comp0_p1=0.0 time/tlim=20.0 z4c/lapse_leak=1.0
# E1, under-damped side: eta m = 0.2 constant, and raised to 2 at the hole by the profile
run gc-e1-eta02 "one boosted puncture, constant eta = 0.2 (test E1 b)" \
    problems/puncture/by_eta.athinput z4c/shift_eta=0.2
run gc-e1-prof02 "one boosted puncture, eta_0 = 0.2 with the profile, M_ref = 10 (test E1 e)" \
    problems/puncture/by_eta.athinput z4c/shift_eta=0.2 z4c/shift_eta_profile=true z4c/shift_eta_mref=10.0
date
echo "gpu_job2 finished"
