#!/bin/bash
set -euo pipefail
export OMP_NUM_THREADS=12
export OMP_PROC_BIND=spread
export OMP_PLACES=threads

BIN=/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/build_gpu_iter5/src/athena
RUN_ROOT=/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/zkl_nr
SUITE_LOG="$RUN_ROOT/suite_status.log"
mkdir -p "$RUN_ROOT"

if [ "$#" -gt 0 ]; then
  RUNS=("$@")
else
  RUNS=("GR_low_a082" "FID_I82_chi0" "I20_subcrit" "GR_high_a055" "I86_high" "SPIN_p07" "SPIN_m07")
fi

echo "[$(date)] Starting Phase 1 ZKL Full-NR Suite on $(hostname) (Job ${SLURM_JOB_ID:-unknown}): ${RUNS[*]}" >> "$SUITE_LOG"

for name in "${RUNS[@]}"; do
  RUN_DIR="$RUN_ROOT/$name"
  ATH="$RUN_DIR/${name}.athinput"
  if [ ! -f "$ATH" ]; then
    echo "[$(date)] ERROR: missing $ATH" >> "$SUITE_LOG"
    exit 1
  fi
  cd "$RUN_DIR"
  echo "[$(date)] === Launching $name ===" >> "$SUITE_LOG"
  latest_rst=$(ls -1t "$RUN_DIR/rst/${name}."*.rst 2>/dev/null | head -n 1 || true)
  if [ -n "$latest_rst" ]; then
    echo "[$(date)] Resuming $name from $latest_rst" >> "$SUITE_LOG"
    "$BIN" -r "$latest_rst" -t 28:30:00 >> "$RUN_DIR/run.log" 2>&1 &
  else
    "$BIN" -i "$ATH" -t 28:30:00 >> "$RUN_DIR/run.log" 2>&1 &
  fi
  pid=$!
  echo "$pid" > "$RUN_DIR/run.pid"
  echo "$name:$pid" > "$RUN_ROOT/current_run.txt"
  wait "$pid"
  rc=$?
  echo "[$(date)] === Finished $name (rc=$rc) ===" >> "$SUITE_LOG"
  if [ "$rc" -ne 0 ]; then
    echo "[$(date)] Stopping suite because $name exited nonzero ($rc)." >> "$SUITE_LOG"
    exit "$rc"
  fi
done

echo "[$(date)] All Phase 1 ZKL Full-NR runs completed cleanly." >> "$SUITE_LOG"
