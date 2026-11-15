"""Put gw_diag and the repository's python/ on sys.path (import this first)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)                               # tracks/B-emd-gw/first_source
TRACK = os.path.dirname(PKG)                              # tracks/B-emd-gw
WT = os.path.dirname(os.path.dirname(TRACK))              # worktree root
for p in (os.path.join(TRACK, "gw_diag"), os.path.join(WT, "python"), PKG):
    if p not in sys.path:
        sys.path.insert(0, p)
