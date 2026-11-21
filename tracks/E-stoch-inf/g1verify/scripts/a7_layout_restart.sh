#!/usr/bin/env bash
# V7 on the G1 executable itself (P-V7c of the journal): the slow-roll L32p set-up of
# ladder/inputs/proc32.list, run with core/scalar-2's processor executable
#   (a) with 8 MeshBlocks of 16^3 instead of one of 32^3, to tlim = 1.2, restart files
#       every 12 cycles;
#   (b) restarted from (a)'s restart file of cycle 12, to the same tlim.
# The dumps are compared afterwards (v7_g1exe.py) with those of the registered L32p
# (E-20261115-172636-ce98836, one MeshBlock) and with each other.
#   a7_layout_restart.sh EXE OUTDIR
set -u
EXE=$1; OUT=$2
ROOT=$(pwd)
DECK=$ROOT/tracks/E-stoch-inf/ladder/inputs/sr_base.athinput
MODES=$ROOT/tracks/E-stoch-inf/ladder/inputs/modes_n64.txt
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false
mkdir -p "$OUT/mb8" "$OUT/rst8"
# the deck of the ladder plus a restart output (a block cannot be added on the command line)
{ cat "$DECK"; printf '\n<output1>\nfile_type = rst\ndcycle    = 12\n'; } > "$OUT/mb8/sr_base.athinput"
ARGS="mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 \
scalar_field/noise_nmax2=64 scalar_field/noise_mode_file=$MODES scalar_field/noise_mode_scale=1.0 \
time/tlim=1.2"
t0=$(date +%s)
( cd "$OUT/mb8" && "$EXE" -i sr_base.athinput $ARGS > athena.log 2>&1 ); rca=$?
t1=$(date +%s)
echo "mb8 rc=$rca wall=$((t1 - t0)) s" | tee -a "$OUT/status.txt"
rst=$(ls "$OUT"/mb8/rst/*.00001.rst 2>/dev/null | head -1)
if [[ $rca -ne 0 || -z $rst ]]; then
  echo "restart not run (rc=$rca, restart file: ${rst:-none})" | tee -a "$OUT/status.txt"
  ls -R "$OUT/mb8" | head -40 >> "$OUT/status.txt"
  exit 1
fi
( cd "$OUT/rst8" && "$EXE" -r "$rst" > athena.log 2>&1 ); rcb=$?
t2=$(date +%s)
echo "rst8 rc=$rcb wall=$((t2 - t1)) s from $rst" | tee -a "$OUT/status.txt"
exit $((rca + rcb))
