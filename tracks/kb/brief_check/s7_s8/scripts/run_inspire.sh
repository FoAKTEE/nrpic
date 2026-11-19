#!/usr/bin/env bash
# Run the INSPIRE queries of specs/inspire_queries.txt one after another (never in parallel),
# through the only allowed fetch command. Prints "<tag> <path of the stored answer>" per query.
# Usage: bash run_inspire.sh <spec file> <log file>
set -u
spec="$1"; log="$2"
fetch=/data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv
grep -v '^#' "$spec" | grep -v '^[[:space:]]*$' | while IFS='|' read -r tag query size; do
  tag="$(echo "$tag" | xargs)"; query="$(echo "$query" | sed 's/^ *//; s/ *$//')"; size="$(echo "$size" | xargs)"
  out="$(python3 -I "$fetch" --inspire-query "$query" --size "$size" 2>&1 | tail -1)"
  echo "$tag | $query | $out" >> "$log"
done
echo DONE >> "$log"
