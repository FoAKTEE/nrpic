#!/usr/bin/env bash
# Executable wrapper for the chains of binary_conv: nr_first/scripts/athena_keep_trackers.sh
# with release core-v0.5's card build as the real executable.
#
# AthenaK opens <base>.co_<n>.txt with truncation whenever it starts, also on a restart
# (athenak/src/z4c/compact_object_tracker.cpp line 91 in core-v0.5: ofile.open(ofname_)),
# so before it starts the real executable this wrapper copies the tracker files of the
# run directory to trk_keep/<UTC time stamp>/ (nr_first/scripts/nrread.read_trackers joins
# them; where a restart repeats times, the later segment wins).
#
# The real executable is $NRPIC_REAL_ATHENA if set, else a byte-identical copy of
# /data/haiyangw/nrpic/.work/build_gpu_v05/src/athena (sha256 2512c8d5...61ea4) named
# bc-ak05-gpu, so that an outside `pkill -x athena` (p1 JOURNAL entry 0) does not match it.
set -euo pipefail
REAL=${NRPIC_REAL_ATHENA:-/data/haiyangw/nrpic/scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu}
if [[ ! -x $REAL ]]; then
  echo "athena_keep_trackers_bc: $REAL missing, using the release path" >&2
  REAL=/data/haiyangw/nrpic/.work/build_gpu_v05/src/athena
fi
shopt -s nullglob
files=( *.co_*.txt )
if (( ${#files[@]} > 0 )); then
  dest="trk_keep/$(date -u +%Y%m%dT%H%M%S.%N)"
  mkdir -p "$dest"
  cp -p "${files[@]}" "$dest/"
  echo "athena_keep_trackers_bc: kept ${#files[@]} tracker file(s) in $dest" >&2
fi
exec "$REAL" "$@"
