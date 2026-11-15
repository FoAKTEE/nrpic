#!/usr/bin/env bash
# Analysis of the two D-pre-4 card runs, registered as one analysis run.
#
#   tracks/D-bh-dress/puncture_drift/tools/finish.sh [RUN8_ID RUN16_ID]
#   FINISH_RUN_ID=<analysis run id> .../finish.sh     continue an analysis run (same
#                                                      output directory; dumps already
#                                                      probed or measured are skipped)
#
# Defaults: the chains started on 2026-11-15 (manifests in tracks/D-bh-dress/runs/).
# Steps: (1) finder re-search of every restart dump of both runs on the processor
# executable (probe_finder.py, A16 and A32, 2 jobs x 8 threads); (2) Misner-Sharp mass of
# every dump (slice_masses.py); (3) analyse_drift.py on the runs, the probes, the slices
# and the probes and slices of the calibration dumps (run D-bh-dress-20261115-121427-284ec4f);
# (4) copies the text, JSON and figures into results/ and figs/ of the package.
# It works on a run that is still going (what exists is analysed); rerunning skips
# dumps already probed.
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/D-bh-dress
P=$WT/tracks/D-bh-dress/puncture_drift
S=/data/haiyangw/nrpic/scratch/D-bh-dress
R8=${1:-D-bh-dress-20261115-121313-284ec4f}
R16=${2:-D-bh-dress-20261115-121314-284ec4f}
HC=$S/D-bh-dress-20261115-121427-284ec4f
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd "$WT"
# every dump except the initial slice (t = 0, where the finder is not quotable) and
# dumps written less than 2 minutes ago (a running chain may still be writing them)
dumps=()
while IFS= read -r f; do
  [[ $f != */punc.00000.rst ]] && dumps+=("$f")
done < <(find "$S/$R8/rst" "$S/$R16/rst" -maxdepth 1 -name 'punc.*.rst' -mmin +2 2>/dev/null | sort)
if [[ -n ${FINISH_RUN_ID:-} && -f $WT/tracks/D-bh-dress/runs/$FINISH_RUN_ID/manifest.json ]]; then
  RA=$FINISH_RUN_ID
else
RA=$(python3 "$P/tools/manifest.py" new --kind production --gpus 0 --cores 16 --status running \
  --purpose "D-pre-4 analysis: finder re-search (A16/A32 x production, tight, start 2 M) and Misner-Sharp mass of every dump of $R8 (M/8) and $R16 (M/16); drift, floor, figures" \
  --cmd "[\"$P/tools/finish.sh\", \"$R8\", \"$R16\"]" \
  --env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=8 \
  --input "$P/tools/finish.sh" "$P/tools/probe_finder.py" "$P/tools/slice_masses.py" \
          "$P/tools/analyse_drift.py" "$WT/analysis/diag/slicemass.py" \
          /data/haiyangw/nrpic/.work/build_cpu_c1/src/athena \
          "$S/$R8/punc.horizon_summary_0.txt" "$S/$R16/punc.horizon_summary_0.txt" \
  --parent "$R8" "$R16" D-bh-dress-20261115-121427-284ec4f)
fi
OUT=$S/$RA
start=$(date +%s)
python3 "$P/tools/probe_finder.py" "${dumps[@]}" --out "$OUT" --tag chain --threads 8 --jobs 2 \
  >> "$OUT/probe_stdout.txt" 2>&1
python3 "$P/tools/slice_masses.py" --out "$OUT/slices.json" "${dumps[@]}" >> "$OUT/slices_stdout.txt" 2>&1
python3 "$P/tools/analyse_drift.py" --out "$OUT" --tag drift \
  --run "$R8=$S/$R8:8" "$R16=$S/$R16:16" \
  --probes "$OUT/chain/probes.json" "$HC/hcal/probes.json" \
  --slices "$OUT/slices.json" "$HC/slices.json" \
  --res dx4=4 dx8_tight=8 dx16=16 --label "$R8=M/8" "$R16=M/16" --t0 50 100 20 50:210 100:210 20:210 \
  > "$OUT/analyse_stdout.txt" 2>&1
end=$(date +%s)
cp "$OUT"/drift_drift.txt "$OUT"/drift_drift.json "$P/results/"
cp "$OUT"/drift_*.png "$OUT"/drift_*.pdf "$P/figs/"
python3 "$P/tools/manifest.py" update "$RA" --status completed --walltime-s $((end - start)) \
  --notes "finish.sh pass ended $(date -u +%FT%TZ) after $((end - start)) s on $(( ${#dumps[@]} )) dumps." \
  --card-hours 0 --ended "$(date -u +%FT%TZ)" --exit-code 0 \
  --outputs-files probe_stdout.txt chain/probes.json slices.json slices_stdout.txt \
                  analyse_stdout.txt drift_drift.txt drift_drift.json drift_history.png \
                  drift_floor.png drift_finder.png
echo "analysis run $RA: $OUT"
