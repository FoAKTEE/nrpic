#!/usr/bin/env bash
# Download the TeX sources of the papers used by the cosmology extension into refs/.
# The sources are not redistributed with this repository.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for id in 1908.05683 1711.06681 1904.07841 2001.07968 1905.08890 1101.3555 1111.2997; do
  dest="$here/arxiv_$id"
  mkdir -p "$dest/src"
  curl -sSL -A "Mozilla/5.0 (X11; Linux x86_64) generic-client" \
       -o "$dest/eprint" "https://arxiv.org/e-print/$id"
  tar -xzf "$dest/eprint" -C "$dest/src" --no-same-owner --no-same-permissions \
    || gunzip -c "$dest/eprint" > "$dest/src/main.tex"
  echo "extracted $id to $dest/src"
done
