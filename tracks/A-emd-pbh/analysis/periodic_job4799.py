#!/usr/bin/env python3
"""Lead's reading of periodic_threshold card job 1 (run A-20261121-131600-02b5d41, Slurm 4799):
both members stopped on the NRPIC guard (chi not positive). Plots the Hamiltonian-constraint
norm, chi_min and K_max against time from the members' histories, and writes the time at which
the constraint norm first exceeds 10 and 1e3 times its initial value.

    python3 tracks/A-emd-pbh/analysis/periodic_job4799.py --run <run dir> --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "python"))
from nrpic import figstyle as fs   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(9.0, 2.8))
    res = {}
    for m in ("P0L", "S1L"):
        z = np.loadtxt(os.path.join(a.run, m, "peak.z4c.user.hst"))
        c = np.loadtxt(os.path.join(a.run, m, "peak.cstat.hst"))
        t, H = z[:, 0], z[:, 3]
        r = dict(t_last=float(t[-1]), H0=float(H[0]), H_last=float(H[-1]))
        for f in (10.0, 1e3):
            k = np.nonzero(H > f * H[0])[0]
            r[f"t_H_above_{f:g}x"] = float(t[k[0]]) if len(k) else None
        r["chi_min_last"] = float(c[-1, 1]); r["K_max_last"] = float(c[-1, 4])
        res[m] = r
        ax[0].semilogy(t, H, label=m)
        ax[1].plot(c[:, 0], c[:, 1], label=m)
        ax[2].semilogy(c[:, 0], np.abs(c[:, 4]), label=m)
    ax[0].set_xlabel("t"); ax[0].set_ylabel(r"$\|H\|_2$")
    ax[1].set_xlabel("t"); ax[1].set_ylabel(r"$\chi_{\min}$")
    ax[2].set_xlabel("t"); ax[2].set_ylabel(r"$|K|_{\max}$")
    for x in ax:
        x.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_periodic_job4799.png"), dpi=150)
    with open(os.path.join(a.out, "periodic_job4799.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
