#!/usr/bin/env bash
# Download the TeX source of the reference paper (arXiv:2611.12831) into refs/.
# The source is not redistributed with this repository.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$here/arxiv_2611.12831"
mkdir -p "$dest/src"
curl -sSL -A "Mozilla/5.0 (X11; Linux x86_64) generic-client" \
     -o "$dest/src.tar" "https://arxiv.org/src/2611.12831"
tar -xzf "$dest/src.tar" -C "$dest/src" --no-same-owner --no-same-permissions
echo "extracted to $dest/src"
