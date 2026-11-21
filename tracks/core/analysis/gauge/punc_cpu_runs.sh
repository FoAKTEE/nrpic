#!/bin/bash
# Processor versions of tests P, E1 and E2 of the work package "gauge" on a small mesh
# (half-width 32, root cells 2, MeshBlocks of 8^3), for the case that no card is free:
# the same inputs and gauge as the card job 2, shorter runs.  Registered by grun.py, tags
# g-p-*, g-e1-*, g-e2-*.
#   punc_cpu_runs.sh p|e1|e2
WT=/data/haiyangw/nrpic/wt/core-gauge
PY=$WT/.venv/bin/python
G=$WT/tracks/core/analysis/gauge
EXE=/data/haiyangw/nrpic/scratch/core/gauge/exe/athena_cpu_b4430da
SRC=b4430da
export OMP_NUM_THREADS=1
MESH="mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 mesh/x1min=-32.0 mesh/x1max=32.0 mesh/x2min=-32.0 mesh/x2max=32.0 mesh/x3min=-32.0 mesh/x3max=32.0 meshblock/nx1=8 meshblock/nx2=8 meshblock/nx3=8"
cd "$WT"
run() {   # tag, purpose, input, arguments
  local tag=$1 purpose=$2 inp=$3; shift 3
  $PY $G/grun.py --exe $EXE --source-commit $SRC --tag "$tag" \
    --purpose "$purpose (processors, half-width 32, MeshBlocks 8^3)" --athinput $WT/$inp $MESH "$@" &
}
case "$1" in
p)
  run g-p-plain "vacuum puncture at rest, cells m/8, plain 1+log (test P)" \
      problems/puncture/by_eta.athinput mesh_refinement/num_levels=5 problem/comp0_p1=0.0 time/tlim=10.0
  run g-p-leak1 "vacuum puncture at rest, cells m/8, lapse relaxation T = 1 (test P)" \
      problems/puncture/by_eta.athinput mesh_refinement/num_levels=5 problem/comp0_p1=0.0 time/tlim=10.0 z4c/lapse_leak=1.0
  ;;
e1)
  run g-e1-eta2 "one boosted puncture, constant eta = 2 (test E1 a)" \
      problems/puncture/by_eta.athinput time/tlim=5.0
  run g-e1-eta20 "one boosted puncture, constant eta = 20 (test E1 c)" \
      problems/puncture/by_eta.athinput time/tlim=5.0 z4c/shift_eta=20.0
  run g-e1-prof20 "one boosted puncture, eta_0 = 20 with the profile, M_ref = 0.1 (test E1 d)" \
      problems/puncture/by_eta.athinput time/tlim=5.0 z4c/shift_eta=20.0 z4c/shift_eta_profile=true z4c/shift_eta_mref=0.1
  run g-e1-eta02 "one boosted puncture, constant eta = 0.2 (test E1 b)" \
      problems/puncture/by_eta.athinput time/tlim=5.0 z4c/shift_eta=0.2
  run g-e1-prof02 "one boosted puncture, eta_0 = 0.2 with the profile, M_ref = 10 (test E1 e)" \
      problems/puncture/by_eta.athinput time/tlim=5.0 z4c/shift_eta=0.2 z4c/shift_eta_profile=true z4c/shift_eta_mref=10.0
  ;;
e2)
  run g-e2-profile "unequal Bowen-York pair, mass ratio 4, damping profile eta_0 = 2, M_ref = 1 (test E2)" \
      problems/puncture/by_unequal.athinput time/tlim=2.0
  run g-e2-eta2 "unequal Bowen-York pair, mass ratio 4, constant eta = 2 (test E2)" \
      problems/puncture/by_unequal.athinput time/tlim=2.0 z4c/shift_eta_profile=false
  run g-e2-eta8 "unequal Bowen-York pair, mass ratio 4, constant eta = 8 (test E2)" \
      problems/puncture/by_unequal.athinput time/tlim=2.0 z4c/shift_eta_profile=false z4c/shift_eta=8.0
  ;;
esac
wait
