#!/usr/bin/env bash
# The puncture case of the regression set again, with the deck fixed (omplib.py, commit
# 501ba4f): R against S (P0) and O3 at 4 and 16 threads, two runs each, against one
# thread of O3 (P11), both series side by side. Run inside the output directory.
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
"$PY" "$HERE/regress.py" --cases punc --ref R:1 --configs S:1 --out ./serial > serial.log 2>&1 &
"$PY" "$HERE/regress.py" --cases punc --ref O3:1 --configs O3:4 O3:4#2 O3:16 O3:16#2 \
    --pairs "O3:4#2=O3:4" "O3:16#2=O3:16" --out ./atomic > atomic.log 2>&1 &
wait %1; rc1=$?
wait %2; rc2=$?
cat serial.log atomic.log
echo "serial: exit $rc1, threads: exit $rc2"
exit $(( rc1 | rc2 ))
