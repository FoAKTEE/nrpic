#!/bin/bash
# Publishes the executables of branch core/scalar-2 for the tracks' scouting runs
# (decision 0013): copies the card and processor executables built from <commit> to
# /data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/ with the files COMMIT and READY.
#   publish.sh <commit of the source> <card exe> <processor exe> <READY text file>
# Run from the worktree. The commit is resolved to its full hash (the first publication
# carried a mistyped short hash, a58e95b4 for a58e95b6), and the source under athenak/
# must be the same at that commit and at HEAD. An executable whose checksum is already
# the published one is not copied again; a new one is copied beside it and renamed over
# it, so that a run that starts during the copy never sees a partial file.
set -euo pipefail
C=$(git rev-parse --verify "$1^{commit}")
G=$2; P=$3; R=$4
if ! git diff --quiet "$C" HEAD -- athenak/; then
  echo "publish.sh: athenak/ differs between $C and HEAD" >&2
  exit 1
fi
D=/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2
mkdir -p "$D"
put() {  # put <source> <published name>
  local src=$1 dst=$D/$2
  if [ -f "$dst" ] && [ "$(sha256sum < "$src")" = "$(sha256sum < "$dst")" ]; then
    echo "unchanged: $dst"
  else
    cp "$src" "$dst.new"
    mv -f "$dst.new" "$dst"
    echo "copied: $dst"
  fi
}
put "$G" athena_gpu
put "$P" athena_cpu
{
  echo "$C"
  echo "branch core/scalar-2; source of athenak/ at this commit (git show $C:athenak/...)"
  sha256sum "$D/athena_gpu" "$D/athena_cpu"
} > "$D/COMMIT.new"
mv -f "$D/COMMIT.new" "$D/COMMIT"
cp "$R" "$D/READY.new"
mv -f "$D/READY.new" "$D/READY"
ls -la "$D"
cat "$D/COMMIT"
