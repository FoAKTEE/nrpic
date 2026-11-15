#!/usr/bin/env bash
# Executable wrapper for chained AthenaK runs (scripts/submit_chain.sh) of the Hills
# passages: keeps the tracker files of every segment.
#
# AthenaK opens <base>.co_<n>.txt with truncation whenever it starts, also on a restart
# (athenak/src/z4c/compact_object_tracker.cpp line 78: ofile.open(ofname)), so a chain
# that restarts in the same directory keeps only the rows of its last segment. (The
# horizon summaries, the history and the waveforms are appended: fastflow.cpp line 252,
# history.cpp line 420, z4c_wave_extr.cpp lines 153 and 176.) Before it starts the real
# executable, this wrapper copies the tracker files in the working directory (the run
# directory: scripts/_athena_job.sh changes into it) to trk_keep/<UTC time stamp>/.
# nrread.read_trackers joins the copies and the live file; where a restart repeats
# times, the later segment wins.
#
# Use: --exe tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh with nrpic-run
# (the chain copies this file to <rundir>/chain/athena). The real executable is
# $NRPIC_REAL_ATHENA if set, else the card executable of release core-v0.3.
set -euo pipefail
REAL=${NRPIC_REAL_ATHENA:-/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena}
shopt -s nullglob
files=( *.co_*.txt )
if (( ${#files[@]} > 0 )); then
  dest="trk_keep/$(date -u +%Y%m%dT%H%M%S.%N)"
  mkdir -p "$dest"
  cp -p "${files[@]}" "$dest/"
  echo "athena_keep_trackers: kept ${#files[@]} tracker file(s) in $dest" >&2
fi
exec "$REAL" "$@"
