#!/usr/bin/env bash
# the processor checks EN, FX2 and D of work package clump2 (journal, sessions clump2-3 and
# clump2-4); run through nrpic-run, one core. EXE_OLD: the processor executable of the source
# that wrote the restart files of TC (commit cbe1e3ef), kept outside the build directory.
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
a=tracks/core/analysis/clump2
exe=${EXE_OLD:-/data/haiyangw/nrpic/scratch/core/tmp/clump2/exe_cbe1e3ef/athena_cpu}
tc=core-20261119-145433-8c4083d
st=0
python3 $a/energy_check.py --out "$out/en" > "$out/en.log" 2>&1 || st=1
python3 $a/corr_surface_check.py --tb core-20261120-222933-0a01a56/tb --out "$out/surf" > "$out/surf.log" 2>&1 || st=1
python3 $a/metric_at_particles.py --exe "$exe" --out "$out/d" \
  --cases "v0.3_t0=$tc/v0.3:0:0,v0.3_t50=$tc/v0.3:2:25,v0.1_t0=$tc/v0.1:0:0,v0.1_t50=$tc/v0.1:2:25,v0_t50=$tc/v0:2:25" \
  --v "v0.3_t0=0.3,v0.3_t50=0.3,v0.1_t0=0.1,v0.1_t50=0.1" > "$out/d.log" 2>&1 || st=1
exit $st
