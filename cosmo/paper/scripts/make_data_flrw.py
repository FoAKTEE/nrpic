"""Histories of the homogeneous-universe runs for the working paper: the coupling with
sources held fixed during a spacetime step, and the coupling with densities converted
at every stage."""
import os

import numpy as np

from common import DATA, RUNS
from nrp_io import read_history

out = {}
for key, run in (("frozen", "flrw_n32_cpu"), ("density", "flrw_n32_cpu_sd")):
    d = os.path.join(RUNS, run)
    h = read_history(os.path.join(d, "flrw.nrpic.hst"))
    z = np.loadtxt(os.path.join(d, "flrw.z4c.user.hst"))
    for k in ("time", "alpha_probe", "E_probe", "tau_probe", "proper_volume", "mean_K"):
        out[f"{key}_{k}"] = h[k]
    out[f"{key}_zt"] = z[:, 0]
    out[f"{key}_Hnorm"] = np.sqrt(z[:, 3])
    out[f"{key}_Theta"] = z[:, 9]
os.makedirs(DATA, exist_ok=True)
np.savez(os.path.join(DATA, "flrw.npz"), **out)
print("wrote", os.path.join(DATA, "flrw.npz"))
