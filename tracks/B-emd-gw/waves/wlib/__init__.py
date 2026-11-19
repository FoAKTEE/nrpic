"""Library of the waves package (G1 criterion 1 of Track B): exact references, the
closed-form Weyl scalar of a tensor mode, the measurement of a dump with both
diagnostics of gw_diag, and the Fourier-symbol prediction of the code's errors."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)                                  # tracks/B-emd-gw/waves
TRACK = os.path.dirname(PKG)                                 # tracks/B-emd-gw
WT = os.path.dirname(os.path.dirname(TRACK))                 # worktree root
for p in (os.path.join(TRACK, "gw_diag"), os.path.join(WT, "python"), os.path.join(WT, "cosmo", "ic")):
    if p not in sys.path:
        sys.path.insert(0, p)
