#!/bin/bash
# Lead re-check L1 of the wave-1 packages of B-emd-gw, from a clean export of one commit.
#
#   bash tracks/B-emd-gw/analysis/lead_recheck.sh RUN_DIR COMMIT
#
# 1. git archive of COMMIT (tracks/B-emd-gw, python, cosmo) into RUN_DIR/export;
# 2. four AthenaK cases of periodic_z4c re-executed with the release processor executable
#    (same command lines as their manifests, output in RUN_DIR/athenak/<name>), in the
#    background, one core each;
# 3. every analysis script and test of the five packages rerun in the export, outputs in
#    RUN_DIR/<step>; return codes in RUN_DIR/rc.txt, logs in RUN_DIR/logs/;
# 4. analysis/compare_results.py compares the reruns with the committed / original results.
# Writes nothing outside RUN_DIR.
set -u
RUN=$1
COMMIT=$2
WT=/data/haiyangw/nrpic/wt/B-emd-gw
SCR=/data/haiyangw/nrpic/scratch/B-emd-gw
EXE=/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena
mkdir -p "$RUN/export" "$RUN/logs" "$RUN/athenak" "$RUN/tmp"
git -C "$WT" archive "$COMMIT" tracks/B-emd-gw python cosmo | tar -x -C "$RUN/export"
T="$RUN/export/tracks/B-emd-gw"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMEXPR_NUM_THREADS=4
export MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1
: > "$RUN/rc.txt"

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$RUN/steps.log"; }
step() {
  local name=$1; shift
  log "start $name"
  ( "$@" ) > "$RUN/logs/$name.out" 2>&1
  local rc=$?
  log "end $name rc=$rc"
  echo "$name $rc" >> "$RUN/rc.txt"
}

# --- 2. AthenaK re-executions (background, serial build, one core each) ---
athena_case() {  # name original_run_id input(relative to package) overrides...
  local name=$1 orig=$2 inp=$3; shift 3
  local out="$RUN/athenak/$name"
  mkdir -p "$out"
  ( cd "$out" && OMP_NUM_THREADS=1 "$EXE" -i "$T/periodic_z4c/inputs/$inp" -d "$out" "$@" \
      > "$out/stdout.txt" 2>&1; echo "$name $?" >> "$RUN/rc_athenak.txt" )
}
: > "$RUN/rc_athenak.txt"
log "start athenak re-executions"
athena_case lw_x_prod_N16 B-emd-gw-20261115-113219-0ea0f74 lw_x.athinput \
  mesh/nx1=16 meshblock/nx1=16 mesh/x1max=1.0 mesh/x2max=0.25 mesh/x3max=0.25 \
  output1/slice_x2=0.09375 output1/slice_x3=0.09375 &
athena_case lw_x_prod_N32 B-emd-gw-20261115-113220-0ea0f74 lw_x.athinput \
  mesh/nx1=32 meshblock/nx1=32 mesh/x1max=1.0 mesh/x2max=0.125 mesh/x3max=0.125 \
  output1/slice_x2=0.046875 output1/slice_x3=0.046875 &
athena_case lw3d_check_diag B-emd-gw-20261115-113216-0ea0f74 lw_3d.athinput \
  mesh/nx1=16 mesh/nx2=16 mesh/nx3=16 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 \
  problem/kx1=1.0 problem/kx2=1.0 problem/kx3=1.0 time/tlim=1.0 output1/dt=1000.0 \
  output2/dt=0.0625 output3/dt=1000.0 output4/dt=0.0625 output5/dt=1000.0 output6/dt=0.0625 &
athena_case gauge_nl_conformal_N64 B-emd-gw-20261115-115139-42096b9 gauge.athinput \
  mesh/nx1=64 meshblock/nx1=64 mesh/x1max=1.0 mesh/x2max=0.0625 mesh/x3max=0.0625 \
  z4c/lapse_oplog=0.0 z4c/lapse_harmonic=0.3333333333333333 z4c/lapse_volume=0.0 \
  z4c/lapse_kdriver=0.0 z4c/lapse_advect=0.0 z4c/shift_Gamma=0.0 z4c/shift_alpha2Gamma=0.0 \
  z4c/shift_H=0.0 z4c/shift_eta=0.0 z4c/shift_advect=0.0 \
  problem/id_file=$SCR/ids/puregauge_N64_k1.5.bin time/tlim=4.0 \
  output1/slice_x2=0.0234375 output1/slice_x3=0.0234375 output2/slice_x2=0.0234375 \
  output2/slice_x3=0.0234375 output1/dt=0.03125 output2/dt=0.03125 &

# --- 3. analyses and tests in the export ---
cp -r "$T/periodic_z4c/tables" "$RUN/pz_tables_committed"
step scope_item3 python3 "$T/scope/scripts/check_item3.py" "$RUN/scope_item3"
step scope_tt python3 "$T/scope/scripts/crossed_waves_tt.py" "$RUN/scope_tt"
step scope_regime python3 "$T/scope/scripts/regime_estimates.py" "$RUN/scope_regime"
step gw_pytest bash -c "cd '$T/gw_diag' && GWDIAG_TMP='$RUN/tmp' \
  GWDIAG_RST='$SCR/B-emd-gw-20261115-113218-0ea0f74/rst/lw3.00016.rst' \
  GWDIAG_NRFIELD=/data/haiyangw/nrpic/runs/cosmo/dav_c256_n128_t/east.field.00004.bin \
  python3 -m pytest -q -p no:cacheprovider tests/"
step gw_tt env RUN_DIR="$RUN/gw_tt" python3 "$T/gw_diag/scripts/validate_tt.py"
step gw_weyl env RUN_DIR="$RUN/gw_weyl" python3 "$T/gw_diag/scripts/validate_weyl.py"
step gw_athenak env RUN_DIR="$RUN/gw_athenak" python3 "$T/gw_diag/scripts/validate_athenak.py" \
  "$SCR/B-emd-gw-20261115-113218-0ea0f74"
step baseline python3 "$T/baseline/scripts/run_baseline.py" "$RUN/baseline"
step vc_zeldovich python3 "$T/verify_cosmo/scripts/test_zeldovich.py"
step vc_flrw python3 "$T/verify_cosmo/scripts/recheck_flrw.py" --out "$RUN/vc_flrw"
step vc_pancake python3 "$T/verify_cosmo/scripts/analyze_pancake.py" \
  --gr "$SCR/B-emd-gw-20261115-115217-69ab1db" --newton "$SCR/B-emd-gw-20261115-115239-69ab1db" \
  --gr2 "$SCR/B-emd-gw-20261115-115902-a3207d7" --newton2 "$SCR/B-emd-gw-20261115-122451-01801f6" \
  --out "$RUN/vc_pancake"
step pz_analysis bash -c "cd '$T/periodic_z4c/analysis' && python3 ana_lw.py && \
  python3 ana_check3d.py && python3 ana_awa.py && python3 ana_gauge.py && python3 ana_dump.py"

log "waiting for the athenak re-executions"
wait
log "athenak done: $(tr '\n' ' ' < "$RUN/rc_athenak.txt")"

# --- 4. comparison ---
step compare python3 "$T/analysis/compare_results.py" "$RUN"
log "done"
