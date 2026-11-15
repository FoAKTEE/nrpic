#!/usr/bin/env python3
"""C4b: the enclosed-mass profile m(lambda) = M(<lambda r_ta)/M_ta of my shell runs (run
directory of v4_driver.sh) against the track's self-similar solution (selfsimilar_profile.npz
of run D-bh-dress-20261115-123813-97afeea), and the mean density slope of the self-similar
solution over the ranges a G1 criterion might use.

Usage: v4b_compare.py --shells RUNDIR --ss SSDIR [--out DIR] [--figdir DIR]
"""
import argparse
import glob
import json
import math
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shells", required=True)
    ap.add_argument("--ss", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--figdir", default=os.path.join(HERE, "..", "figs"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ss = np.load(os.path.join(a.ss, "selfsimilar_profile.npz"))
    lng, lnm = ss["lngrid"], ss["lnm"]
    m_ss = lambda lam: np.exp(np.interp(np.log(lam), lng, lnm))
    res = {"ss_mean_density_slope": {}}
    for lo, hi in ((1e-4, 1e-3), (1e-3, 1e-2), (3e-3, 3e-2), (0.01, 0.1), (0.03, 0.3), (0.01, 0.5),
                   (0.002, 0.5), (0.05, 0.5)):
        s = math.log(m_ss(hi) / m_ss(lo)) / math.log(hi / lo)
        res["ss_mean_density_slope"][f"{lo}-{hi}"] = s - 3
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    lam = np.logspace(-4, 0, 400)
    ax[0].loglog(lam, m_ss(lam), **fs.GUIDE, label="track self-similar m(λ)")
    ax[1].axhline(0, **fs.THIN)
    res["shell_runs"] = {}
    cols = fs.SERIES
    for j, d in enumerate(sorted(glob.glob(os.path.join(a.shells, "N*")))):
        if not os.path.exists(os.path.join(d, "v4_shells.json")):
            continue
        js = json.load(open(os.path.join(d, "v4_shells.json")))
        z = np.load(os.path.join(d, "v4_shells.npz"))
        r = np.sort(z["r"])
        dm, Mc, r_ta = js["dm"], js["seed_plus_inner"], js["r_ta_af"]
        Mta_tot = Mc + dm * np.sum(r < r_ta)
        lam_s = r / r_ta
        m_tot = (Mc + dm * np.arange(1, len(r) + 1)) / Mta_tot
        name = os.path.basename(d)
        sel = (lam_s > 0.02) & (lam_s < 0.5)
        dev = m_tot[sel] / m_ss(lam_s[sel]) - 1
        sel2 = (lam_s > 0.005) & (lam_s < 0.02)
        dev2 = m_tot[sel2] / m_ss(lam_s[sel2]) - 1 if sel2.any() else np.array([np.nan])
        res["shell_runs"][name] = {"af": js["args"]["af"], "N": js["args"]["N"], "soft": js["args"]["soft"],
                                   "eta": js["args"]["eta"], "M_ta_total": float(Mta_tot),
                                   "seed_fraction_of_Mta": Mc / Mta_tot,
                                   "max_abs_dev_0.02-0.5": float(np.max(np.abs(dev))),
                                   "median_dev_0.02-0.5": float(np.median(dev)),
                                   "max_abs_dev_0.005-0.02": float(np.nanmax(np.abs(dev2))),
                                   "lambda_where_seed_equals_dust": float(
                                       lam_s[np.argmax(dm * np.arange(1, len(r) + 1) > Mc)])}
        ax[0].loglog(lam_s, m_tot, color=cols[j % len(cols)], lw=1.0, label=name)
        ax[1].semilogx(lam_s, m_tot / m_ss(lam_s) - 1, color=cols[j % len(cols)], lw=1.0, label=name)
    ax[0].set_xlabel(r"$\lambda = r/r_{\rm ta}$"); ax[0].set_ylabel(r"$m(\lambda) = M(<\lambda r_{\rm ta})/M_{\rm ta}$")
    ax[0].set_xlim(1e-4, 1); ax[0].set_ylim(1e-3, 1.2)
    ax[0].legend(frameon=False, fontsize=6)
    ax[1].set_xlabel(r"$\lambda$"); ax[1].set_ylabel("shells / self-similar - 1")
    ax[1].set_xlim(1e-3, 1); ax[1].set_ylim(-0.3, 0.3)
    for x in (0.02, 0.5):
        ax[1].axvline(x, **fs.MASK_LINE)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(a.out, "v4b_compare"))
    shutil.copy(files[1], a.figdir)
    with open(os.path.join(a.out, "v4b_compare.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
