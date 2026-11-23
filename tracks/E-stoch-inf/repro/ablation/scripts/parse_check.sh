#!/usr/bin/env bash
# Processor parse check of the decks of repro/ablation (JOURNAL entry 0, prediction X0): each deck at
# 32^3, nmax2 = 64, two cycles, with the branch processor executable, one core. Writes one directory
# per deck under $1 and a summary file $1/parse_check.txt (deck, exit status, dumps, rmodes, modes in
# the rmodes header). Run through nrpic-run (local launcher):
#   harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/ablation \
#     --launcher local --cores 1 --allow-no-venv --purpose "..." -- \
#     bash tracks/E-stoch-inf/repro/ablation/scripts/parse_check.sh '$NRPIC_RUN_DIR'
set -uo pipefail
OUT=${1:?output directory}
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_cpu
A=/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/repro/ablation/inputs
SRM=/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/ladder/inputs/modes_n4096.txt
USM=/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/usr/inputs/modes_usr_n4096.txt
export OMP_NUM_THREADS=1
small=(mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32
       scalar_field/noise_nmax2=64 time/nlim=2)
summary=$OUT/parse_check.txt
echo "# deck exit dumps rmodes modes_in_rmodes_header" > "$summary"
for deck in "$A"/sr256_l0m.athinput "$A"/sr256_l1m.athinput "$A"/sr256_l2.athinput \
            "$A"/usr256_l0m.athinput "$A"/usr256_l1m.athinput "$A"/usr256_l2.athinput \
            "$A"/card/sr64_l1m.athinput "$A"/card/usr64_l0m.athinput; do
  name=$(basename "$deck" .athinput)
  d=$OUT/$name; mkdir -p "$d"
  case $name in sr*) mf=$SRM ;; *) mf=$USM ;; esac
  ( cd "$d" && "$EXE" -i "$deck" -d "$d" "${small[@]}" scalar_field/noise_mode_file="$mf" > "$d/log.txt" 2>&1 )
  rc=$?
  nd=$(find "$d" -maxdepth 1 -name '*.sf.*.dump' | wc -l)
  rm1=$(find "$d" -maxdepth 1 -name '*.sf.*.rmodes' | sort | head -1)
  nr=$(find "$d" -maxdepth 1 -name '*.sf.*.rmodes' | wc -l)
  if [[ -n $rm1 ]]; then
    hm=$(head -1 "$rm1" | awk '{for (i=1;i<NF;i++) if ($i=="modes") print $(i+1)}')
    nl=$(grep -cv '^#' "$rm1")
  else hm=-; nl=-; fi
  echo "$name $rc $nd $nr ${hm}/${nl}" >> "$summary"
done
cat "$summary"
