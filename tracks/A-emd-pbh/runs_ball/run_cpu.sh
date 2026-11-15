#!/usr/bin/env bash
# Processor runs of SR-1 (all segments, restarts with a smaller step) or SR-2 at one
# resolution, in the run directory given by the harness ($NRPIC_RUN_DIR) or as argument.
#
#   run_cpu.sh <sr1|sr2> <prep dir> <n_track> [nx=128] [meshblock=32] [out dir]
#
# Executable: the release processor build of core-v0.3 (CLAUDE.md), read-only.
# SR-1 segments (stage plan of prep.py, exact.json "sr1_stages", 0.9 of the stability
# limit cfl x c = 0.618): cfl 0.25 to t = 42.0; cfl 0.03125 to 44.3568; cfl 0.0078125 to
# 44.4472, each a restart from the final restart file of the previous segment in the same
# directory (histories, trajectories and horizon summaries append).
set -euo pipefail
G=$1; PREP=$2; NT=$3; NX=${4:-128}; MB=${5:-32}
OUT=${6:-${NRPIC_RUN_DIR:?give an output directory}}
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PFILE=$(ls "$PREP"/*_lat38_track.nrp)
D=$OUT/${G}_n${NX}
mkdir -p "$D"
cp "$HERE/$G.athinput" "$D/"
MESH=(mesh/nx1=$NX mesh/nx2=$NX mesh/nx3=$NX meshblock/nx1=$MB meshblock/nx2=$MB meshblock/nx3=$MB)
PART=(particles/particle_file=$PFILE particles/traj_ntrack=$NT)
export OMP_PROC_BIND=false
cd "$D"
echo "segment 1: $(date -u +%FT%TZ)"
"$EXE" -i "$D/$G.athinput" -d "$D" "${MESH[@]}" "${PART[@]}" > "$D/athena.1.log" 2>&1
if [[ $G == sr1 ]]; then
  last_rst() { ls "$D"/rst/ball.*.rst | sort | tail -1; }
  R1=$(last_rst)
  echo "segment 2 from $R1: $(date -u +%FT%TZ)"
  "$EXE" -r "$R1" -d "$D" time/cfl_number=0.03125 time/tlim=44.3568 \
      output3/dt=0.02 output4/dt=0.02 output5/dt=0.02 output6/dt=0.02 > "$D/athena.2.log" 2>&1
  R2=$(last_rst)
  echo "segment 3 from $R2: $(date -u +%FT%TZ)"
  "$EXE" -r "$R2" -d "$D" time/cfl_number=0.0078125 time/tlim=44.4472 \
      output3/dt=0.004 output4/dt=0.004 output5/dt=0.004 output6/dt=0.004 > "$D/athena.3.log" 2>&1
fi
echo "done: $(date -u +%FT%TZ)"
