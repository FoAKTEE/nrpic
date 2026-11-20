#!/usr/bin/env bash
# Card runs of work package omp, read after they have run (journal entries 11, 12, 15):
#   1. P13: the card executable of this branch on dep and east against one thread of the
#      threaded processor executable (card_compare.py; figure figs/card_diff);
#   2. P7: table and figure of the strong scaling with the card column filled from the
#      card timing run (analyse_scaling.sh).
#   analyse_card.sh        (run inside the output directory)
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
S=/data/haiyangw/nrpic/scratch/core
"$PY" "$HERE/card_compare.py" --card "$S/core-20261119-164717-b187f36" \
    --ref "$S/core-20261119-155057-57325bc/atomic" --out . ; rc=$?
cp figs/card_diff.png figs/card_diff.pdf "$HERE/figs/"
bash "$HERE/analyse_scaling.sh" "$S/core-20261119-144437-6718c76"
echo "card_compare exit $rc"
exit $rc
