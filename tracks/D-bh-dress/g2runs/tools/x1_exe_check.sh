#!/bin/bash
# X1 (g2runs JOURNAL entry 1): is the change of executable from core/gauge (b4430da, the
# executable of ES-1G) to release core-v0.4 neutral on the ES-1G input? Runs the input for
# NLIM cycles with both processor executables, each in its own directory under
# $NRPIC_RUN_DIR, then compares every file AthenaK wrote byte for byte.
# Usage (under nrpic-run, two cores): x1_exe_check.sh <input> [nlim]
set -u
INPUT=$1
NLIM=${2:-12}
OUT=${NRPIC_RUN_DIR:?run under nrpic-run}
OLD=/data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_cpu
NEW=/data/haiyangw/nrpic/.work/build_cpu_v04/src/athena
export OMP_NUM_THREADS=1
for tag in gauge v04; do mkdir -p "$OUT/$tag"; done
sha256sum "$OLD" "$NEW" > "$OUT/exe_sha256.txt"
# outputs at t = 0 and the final ones; restart output switched off (dt beyond tlim)
ARGS="time/nlim=$NLIM output2/dt=1.0e9"
(cd "$OUT/gauge" && "$OLD" -i "$INPUT" $ARGS > athena.log 2>&1; echo "exit $?" >> athena.log) &
P1=$!
(cd "$OUT/v04" && "$NEW" -i "$INPUT" $ARGS > athena.log 2>&1; echo "exit $?" >> athena.log) &
P2=$!
wait $P1 $P2
cd "$OUT"
{
  echo "# X1: byte comparison, core/gauge b4430da (gauge/) against release core-v0.4 (v04/), nlim=$NLIM"
  for f in $(cd gauge && find . -type f ! -name athena.log | sort); do
    if [ ! -e "v04/$f" ]; then echo "only-gauge $f"; continue; fi
    if cmp -s "gauge/$f" "v04/$f"; then echo "identical $f"; else echo "differs $f"; fi
  done
  for f in $(cd v04 && find . -type f ! -name athena.log | sort); do
    [ -e "gauge/$f" ] || echo "only-v04 $f"
  done
  echo "# exit codes: gauge $(tail -1 gauge/athena.log), v04 $(tail -1 v04/athena.log)"
  echo "# warnings mentioning lapse_leak:"
  grep -i "lapse_leak\|not used" gauge/athena.log v04/athena.log || echo "none"
} > x1_compare.txt
cat x1_compare.txt
