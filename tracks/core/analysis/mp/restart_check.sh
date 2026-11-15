#!/usr/bin/env bash
# Restart check of puncture_setup (processors): eight cycles uninterrupted, then cycles
# 5 to 8 again from the restart dump of cycle 4, and a comparison of the trackers, the
# horizon summary and the particle history of the two.
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/core-mp
N="python3 $WT/tracks/core/analysis/mp/nrun.py"
cd "$WT"
out=$($N --label psr_full --exe cpu --purpose "Restart check of puncture_setup: eight cycles uninterrupted, with tracers" --input problems/tests/puncture_setup_restart.athinput)
echo "$out"
id=${out%% *}
dir=/data/haiyangw/nrpic/scratch/core/$id
rst=$(ls $dir/rst/psr.*.rst | sed -n 2p)
out2=$($N --label psr_restart --exe cpu --restart "$rst" --purpose "Restart check of puncture_setup: cycles 5 to 8 from the restart dump of cycle 4 of $id" --input problems/tests/puncture_setup_restart.athinput)
echo "$out2"
