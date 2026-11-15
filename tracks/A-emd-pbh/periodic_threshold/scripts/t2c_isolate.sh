#!/usr/bin/env bash
# T2c isolation: the crash of adaptive refinement in the periodic cosmological box.
#   t2c_isolate.sh <outdir> <ic_flrw dir>
# (1) the homogeneous universe with the Lohner criterion under gdb (backtrace);
# (2) the same with the trivial criterion (no block is ever flagged).
set -uo pipefail
OUT=$1; IC=$2
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
INP=$(cd "$(dirname "${BASH_SOURCE[0]}")/../inputs" && pwd)/peak_amr.athinput
COMMON="problem/id=flrw time/nlim=6 mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=8 meshblock/nx2=8 meshblock/nx3=8 fastflow/find_every=1000 particles/particle_file=$IC/particles.nrp"
mkdir -p "$OUT/lohner_gdb" "$OUT/trivial"
( cd "$OUT/lohner_gdb" && gdb -batch -ex run -ex bt -ex "info frame" --args $EXE -i $INP -d . $COMMON > gdb.log 2>&1 ) &
( cd "$OUT/trivial" && $EXE -i $INP -d . $COMMON z4c_amr/method=trivial > athena.log 2>&1; echo "exit $?" >> athena.log ) &
wait
grep -A40 "SIGSEGV\|signal" "$OUT/lohner_gdb/gdb.log" | head -60
tail -3 "$OUT/trivial/athena.log"
