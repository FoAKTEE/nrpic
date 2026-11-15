#!/usr/bin/env bash
# Card runs of the work package coll2, second session (after the crash of every card run
# of the executable of 819d588, JOURNAL-coll2.md 18:40 UTC). One allocation per call:
#   (from the root of the worktree)
#   sbatch -p preempt --gres=gpu:1 -c 2 -t 00:45:00 -J core-coll2 -o <log> \
#          tracks/core/analysis/collisions/gpu_job3.sh <parts> <card exe> <release card exe> <python>
# <parts>: letters, run in this order after the smoke test
#   S  (always first) smoke test: two short decks with the new executable, the static
#      metric with collisions (mesh metric) and the perturbing force (analytic metric);
#      if either crashes: a backtrace with gdb, and the job stops
#   R  regression: five existing set-ups against the release executable; the
#      collisional box tests of wave 1 (options absent) with both executables, outputs
#      compared byte by byte
#   N  the new tests: gradient (four cases), replay of the coll_energy cases,
#      equilibrium in the potential well, homogeneous static metric (T12, G3)
#   C  the relativistic cluster at Knudsen number 3, coll_energy = cell and = particle
# Each test is a registered run (runreg.py --card); its card time is its wall time.
set -uo pipefail
PARTS=$1; EXE=$2; BASE=$3; PY=$4
REPO=${SLURM_SUBMIT_DIR:?submit with sbatch from the root of the worktree}
[[ -f $REPO/tracks/core/analysis/collisions/common.py ]] || { echo "not a worktree: $REPO"; exit 1; }
R=tracks/core/analysis/rng
C=tracks/core/analysis/collisions
S=/data/haiyangw/nrpic/scratch/core
T=$S/tmp/coll2/smoke_card_${SLURM_JOB_ID:-local}
cd "$REPO"
nvidia-smi -L
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2

# ---- S: smoke test
mkdir -p "$T/static" "$T/pert"
$PY - "$T/static.nrp" <<'EOF'
import sys
sys.path.insert(0, "tracks/core/analysis/collisions")
import scbox
met = scbox.Metric(nx=16, a_alpha=-0.2, a_psi=0.1)
scbox.make_particles(sys.argv[1], met, 20000, 7, 0.05, 1.0, 0.0, [1.0, 0.25, 0.25])
EOF
smoke_fail=0
( cd "$T/static" && "$EXE" -i "$REPO/problems/tests/coll_box_static.athinput" -d "$T/static" \
    particles/particle_file="$T/static.nrp" time/nlim=5 particles/coll_sigma=50.0 \
    > athena.log 2>&1 ); st1=$?
( cd "$T/pert" && "$EXE" -i "$REPO/problems/tests/perturb_flat.athinput" -d "$T/pert" \
    > athena.log 2>&1 ); st2=$?
echo "smoke: static exit $st1, perturb exit $st2"
if [[ $st1 -ne 0 || $st2 -ne 0 ]]; then
  smoke_fail=1
  tail -5 "$T/static/athena.log" "$T/pert/athena.log"
  ( cd "$T/static" && gdb -batch -ex run -ex bt --args "$EXE" \
      -i "$REPO/problems/tests/coll_box_static.athinput" -d "$T/static" \
      particles/particle_file="$T/static.nrp" time/nlim=5 particles/coll_sigma=50.0 \
      > gdb.log 2>&1 )
  grep -A25 "SIGSEGV\|^#0" "$T/static/gdb.log" | head -40
  echo "smoke test failed: the job stops"
  exit 1
fi

if [[ $PARTS == *R* ]]; then
  $PY $R/runreg.py --card --kind scouting \
    --purpose "R on one A100: five existing set-ups, executable of core/collisions-2 (clean build of f46f159, options absent) against the release executable core-v0.3" \
    --input "$BASE" --input "$EXE" --input $R/run_regression.py -- \
    $PY "{repo}/$R/run_regression.py" --base "$BASE" --new "$EXE"
  $PY $C/rerun_wave1.py "$S/tmp/coll2/rerun_wave1_card_f46f159.json" --exe "$EXE" --python $PY --card \
    --base "$BASE" --tests rate,relax,repro,conv_dt,curved
fi
if [[ $PARTS == *N* ]]; then
  $PY $R/runreg.py --card --kind scouting \
    --purpose "G1 G2 on one A100: one collision step in the static conformal metric, cases psi_iso, well_tolman, well_shift, psi_iso_hot, both modes, against the reference with the cell rate" \
    --input "$EXE" --input $C/run_gradient.py -- \
    $PY "{repo}/$C/run_gradient.py" "{out}" --exe "$EXE" --nproc 2 --n 2000000 \
    --ref $S/core-20261115-181655-b4b8e33/ref.json --ref $S/core-20261115-181657-426b4a8/ref.json \
    --ref $S/core-20261115-181700-726905c/ref.json --ref $S/core-20261115-181702-c93920b/ref.json \
    --cases psi_iso,well_tolman,well_shift,psi_iso_hot
  $PY $R/runreg.py --card --kind scouting \
    --purpose "G2e on one A100: replay of single collision steps by the Python twin, wave-1 cases and the cases of coll_energy" \
    --input "$EXE" --input $C/run_replay.py -- \
    $PY "{repo}/$C/run_replay.py" "{out}" --exe "$EXE" --nproc 2 --new --n 6000
  $PY $R/runreg.py --card --kind scouting \
    --purpose "G4 on one A100: equilibrium in the potential well with streaming and collisions, both modes, two seeds, theta_inf = 0.2" \
    --input "$EXE" --input $C/run_tolman.py -- \
    $PY "{repo}/$C/run_tolman.py" "{out}" --exe "$EXE" --nproc 2 --theta 0.2 \
    --ref $S/core-20261115-163914-74b3e87/ref_tolman_0.2.json
  $PY $R/runreg.py --card --kind scouting \
    --purpose "T12 and G3 on one A100: homogeneous static metric alpha0 = 0.8, psi0 = 1.1, coll_energy cell and particle, wave-1 homogeneous generator, flat box" \
    --input "$EXE" --input $C/run_static_homog.py -- \
    $PY "{repo}/$C/run_static_homog.py" "{out}" --exe "$EXE" --nproc 2
fi
if [[ $PARTS == *C* ]]; then
  $PY $R/runreg.py --card --kind scouting \
    --purpose "P11 with coll_energy on one A100: relativistic cluster y_c = 0.819 at Knudsen number 3, collision cells of 2 M, coll_energy = cell and = particle, 150 M" \
    --input "$EXE" --input $C/run_cluster.py -- \
    $PY "{repo}/$C/run_cluster.py" "{out}" --exe "$EXE" --kn 3 --skip-null --energy cell,particle
fi
echo "gpu_job3 parts $PARTS finished"
