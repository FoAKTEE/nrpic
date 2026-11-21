#!/usr/bin/env bash
# The example input of deposit_threads (problems/tests/deposit_threads.athinput): two runs
# of the threaded executable at 4 threads (expected byte-identical), one of the serial
# executable (expected: the note that it adds atomically, and the files of the deposit
# test without the option, deposit_smr.athinput, byte for byte), one of the threaded
# executable without the option at 4 threads.
#   example_check.sh <threaded exe> <serial exe>     (run inside the output directory)
set -uo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
O=$1; S=$2
IC=/data/haiyangw/nrpic/scratch/core/regress/ic/random.nrp
args=(time/tlim=2.0 particles/deposit_max_level=1)
run() {  # dir exe threads deck
  mkdir -p "$1"; ln -sf "$IC" "$1/random.nrp"; cp "$WT/$4" "$1/"
  (cd "$1" && OMP_NUM_THREADS=$3 OMP_PROC_BIND=true OMP_PLACES=$(python3 "$WT/scripts/omp_places.py" "$3") \
     "$2" -i "$(basename "$4")" "${args[@]}" > run.log 2>&1); echo "$1 exit $?"
}
run priv4_a "$O" 4 problems/tests/deposit_threads.athinput
run priv4_b "$O" 4 problems/tests/deposit_threads.athinput
run atomic4 "$O" 4 problems/tests/deposit_smr.athinput
run serial_opt "$S" 1 problems/tests/deposit_threads.athinput
run serial_ref "$S" 1 problems/tests/deposit_smr.athinput
cmp priv4_a/dep.nrpic.hst priv4_b/dep.nrpic.hst && echo "private, 4 threads, two runs: identical"
cmp serial_opt/dep.nrpic.hst serial_ref/dep.nrpic.hst && echo "serial with and without the option: identical"
grep -h "deposit_threads\|private copy" priv4_a/run.log serial_opt/run.log
