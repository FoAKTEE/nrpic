"""Re-read the homogeneous-universe runs of cosmo/ (C0 and the step-limit check) and
compare the lapse (the scale factor in this slicing), the probe density, the mean K and
the proper volume with the exact matter-dominated solution a = (1 + t/2)^2,
rho = rho0 a^-3, K = -3 (1 + t/2)^-3, V = V0 a^3 (H0 = 1).

    python3 recheck_flrw.py --out DIR [rundir ...]

Writes DIR/flrw_recheck.json and DIR/flrw_recheck.{png,pdf}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrp_io import read_history  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

RUNS = "/data/haiyangw/nrpic/runs/cosmo"
DEFAULT = [("flrw_n32_cpu", "C0, sources held fixed"),
           ("flrw_n32_cpu_sd", "C0, densities per stage"),
           ("dtexp_test/ref", "16 cells, Courant step"),
           ("dtexp_test/lim", "16 cells, step limit 0.01")]

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
rho0 = 3.0/(8.0*np.pi)
res = {}
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
for i, (name, label) in enumerate(DEFAULT):
    path = os.path.join(RUNS, name)
    hst = [f for f in os.listdir(path) if f.endswith(".nrpic.hst")][0]
    h = read_history(os.path.join(path, hst))
    t = h["time"]
    aex = (1.0 + 0.5*t)**2
    e_alpha = h["alpha_probe"]/aex - 1.0
    e_rho = h["E_probe"]/(rho0/aex**3) - 1.0
    out = {"rundir": path, "t_end": float(t[-1]), "a_end": float(aex[-1]),
           "records": int(len(t)),
           "max_rel_err_lapse": float(np.abs(e_alpha).max()),
           "max_rel_err_density": float(np.abs(e_rho).max())}
    if "mean_K" in h:
        e_K = h["mean_K"]/(-3.0*(1.0 + 0.5*t)**-3) - 1.0
        V0 = h["proper_volume"][0]
        e_V = h["proper_volume"]/(V0*aex**3) - 1.0
        out["max_rel_err_mean_K"] = float(np.abs(e_K).max())
        out["max_rel_err_proper_volume"] = float(np.abs(e_V).max())
        out["box_side"] = float(V0**(1/3))
    cst = [f for f in os.listdir(path) if f.endswith(".cstat.hst")]
    if cst:
        c = np.loadtxt(os.path.join(path, cst[0]))
        out["Hr_max_end"] = float(c[-1, 10])
        out["Hr_mean_end"] = float(c[-1, 11])
    res[name] = out
    col = fs.SERIES[i]
    axs[0].semilogy(aex, np.abs(e_alpha), color=col, label=label)
    axs[1].semilogy(aex, np.abs(e_rho), color=col, label=label)
axs[0].set_xlabel(r"$a$")
axs[1].set_xlabel(r"$a$")
axs[0].set_ylabel(r"$|\alpha/a - 1|$")
axs[1].set_ylabel(r"$|\rho/\rho_0 a^{-3} - 1|$ at the probe")
axs[0].set_xscale("log")
axs[1].set_xscale("log")
axs[0].legend(loc="lower right", fontsize=8)
fs.save(fig, os.path.join(a.out, "flrw_recheck"))
with open(os.path.join(a.out, "flrw_recheck.json"), "w") as f:
    json.dump(res, f, indent=1)
for k, v in res.items():
    print(k, json.dumps(v))
