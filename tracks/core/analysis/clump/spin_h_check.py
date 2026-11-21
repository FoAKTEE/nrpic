#!/usr/bin/env python3
"""Addendum to test T3 (tracks/core/JOURNAL-clump.md): the Hamiltonian residual added by
the spin curvature, H(with) - H(without), against -psi^-12 Abar_ij Abar_ij of the Python
reference, cell by cell (a check of the spin curvature that does not go through its
divergence). Also T7: the same for two clumps and a puncture (case 'all' against the
closed form of the summed curvature is not possible there without the K_ij = 0 run, so
'all' is compared with 'punc' through the difference of the two closed forms).

    spin_h_check.py T3_RUN_ID T7_RUN_ID   -> spin_h_check.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
from mp_common import read_bin  # noqa: E402
from nrpic import bowen_york as by  # noqa: E402
from nrpic import clumps as clm  # noqa: E402
from nrpic import smeared_bowen_york as sby  # noqa: E402

out = {}
# ---- T3: one clump with spin 0.04 along z, 128 cells
G = clm.GaussianClumps([dict(mass=0.2, sigma=1.0)])
d0 = read_bin(os.path.join(SCRATCH, sys.argv[1], "t3_n128_none", "bin", "clump.con.00000.bin"))
d1 = read_bin(os.path.join(SCRATCH, sys.argv[1], "t3_n128_curv", "bin", "clump.con.00000.bin"))
X = np.stack([d0[2], d0[3], d0[4]], axis=-1)
psi = G.psi(X)
cf = -psi ** -12 * sby.abar2(X, [((0, 0, 0), 1.0, (0, 0, 0), (0, 0, 0.04))])
diff = d1[6]["con_H"] - d0[6]["con_H"]
out["T3_spin"] = dict(max_abs_diff_minus_closed_form=float(np.abs(diff - cf).max()),
                      closed_form_peak=float(np.abs(cf).max()),
                      norm_diff=float(np.sqrt(np.sum(psi ** 6 * diff ** 2 * d0[5] ** 3))),
                      norm_closed_form=float(np.sqrt(np.sum(psi ** 6 * cf ** 2 * d0[5] ** 3))))
# ---- T7: H(all) - H(punc) = -psi^-12 (A_all^2 - A_punc^2), away from the puncture
with open(os.path.join(SCRATCH, sys.argv[2], "particles.json")) as f:
    meta = json.load(f)
G7 = clm.GaussianClumps(meta["gaussians"], meta["punctures"])
da = read_bin(os.path.join(SCRATCH, sys.argv[2], "all", "bin", "clump.con.00000.bin"))
dp = read_bin(os.path.join(SCRATCH, sys.argv[2], "punc", "bin", "clump.con.00000.bin"))
X = np.stack([da[2], da[3], da[4]], axis=-1)
b = G7.punctures[0]
far = np.sum((X - b["centre"]) ** 2, axis=-1) > 1.0
X = X[far]
psi = G7.psi(X)
Aall = G7.abar(X)
Ap = by.abar(X, b["centre"], b["P"], b["S"])
cf = -psi ** -12 * (np.sum(Aall ** 2, axis=(-1, -2)) - np.sum(Ap ** 2, axis=(-1, -2)))
diff = (da[6]["con_H"] - dp[6]["con_H"])[far]
out["T7_clumps_beside_puncture"] = dict(
    max_abs_diff_minus_closed_form=float(np.abs(diff - cf).max()),
    closed_form_peak=float(np.abs(cf).max()), cells=int(far.sum()),
    note="cells farther than 1 from the puncture; includes the cross term "
         "2 Abar(clumps):Abar(puncture)")
with open(os.path.join(HERE, "spin_h_check.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
