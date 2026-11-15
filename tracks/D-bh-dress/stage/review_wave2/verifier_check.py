#!/usr/bin/env python3
"""Lead's wave-2 re-check of three claims of the fresh-context verifier (stage/G0/VERIFIER.md;
JOURNAL.md, predictions W7-W9). Closed forms written here; the mesh counts are read from the
AthenaK logs of the verifier's run D-20261115-171953-908afff. Writes verifier_check.json and
verifier_check.png into --out.
"""
import argparse
import glob
import json
import math
import os
import re
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

MESH = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-171953-908afff"


def mcvittie(h):
    """x = R_AH/(2m) from 1 - 2 M_MS/R = 0 with M_MS = m + H^2 R^3/2, h = mH:
    x = 1 + 4 h^2 x^3 (smaller root); M_AH = R_AH/2 = m x. EdS: d ln h/d ln a = -3/2."""
    x = brentq(lambda x: x - 1.0 - 4.0 * h * h * x ** 3, 1.0, 1.0 + 20 * h * h + 1e-12) if h > 0 else 1.0
    slope = -12.0 * h * h * x * x / (1.0 - 12.0 * h * h * x * x)
    return x, slope


def V(r, L):
    return (1.0 - 2.0 / r) * (1.0 + L * L / (r * r))


def Vmax(L):
    if L * L <= 12.0:
        return None
    rmax = 0.5 * L * L * (1.0 - math.sqrt(1.0 - 12.0 / (L * L)))
    return V(rmax, L)


def capture_threshold(rta):
    """L at which a particle at radial rest at rta is marginally captured:
    V(rta, L) = Vmax(L); captured for smaller L."""
    f = lambda L: V(rta, L) - Vmax(L)  # noqa: E731
    Ls = np.linspace(math.sqrt(12.0) + 1e-6, 6.0, 4000)
    vals = np.array([f(L) for L in Ls])
    k = np.where(np.sign(vals[:-1]) != np.sign(vals[1:]))[0]
    L = brentq(f, Ls[k[0]], Ls[k[0] + 1])
    return L, L / rta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    out = {"W7": {}, "W8": {}, "W9": {}}
    for h in (0.01, 0.03, 0.1):
        x, s = mcvittie(h)
        out["W7"][f"h={h}"] = dict(x=x, dlnM_dlna=s, leading=-12 * h * h,
                                   two_terms=-12 * h * h - 240 * h ** 4)
    for rta in (16.1, 33.4):
        L, v = capture_threshold(rta)
        out["W8"][f"r_ta={rta}"] = dict(L_threshold=L, v_tangential=v,
                                         v_static_observer=v / math.sqrt(1.0 + v * v))
    out["W8"]["Lc_E1"] = 4.0  # marginally bound: Vmax(L) = 1 at L = 4
    out["W8"]["Vmax(4)"] = Vmax(4.0)
    for log in sorted(glob.glob(os.path.join(MESH, "mesh_*.log"))):
        txt = open(log).read()
        m = re.search(r"Total number of MeshBlocks = (\d+)", txt)
        lv = re.findall(r"Physical level = (\d+) \(logical level = \d+\): (\d+) MeshBlocks", txt)
        out["W9"][os.path.basename(log)] = dict(total=int(m.group(1)) if m else None,
                                                per_level={a: int(b) for a, b in lv})
    with open(os.path.join(args.out, "verifier_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.16, top=0.95, wspace=0.3)
    hh = np.geomspace(1e-3, 0.12, 200)
    ex = np.array([mcvittie(h)[1] for h in hh])
    axs[0].loglog(hh, -ex, color=fs.PAL["red"], label="exact (lead)")
    axs[0].loglog(hh, 12 * hh ** 2, **fs.GUIDE, label=r"$12h^2$")
    axs[0].loglog(hh, 12 * hh ** 2 + 240 * hh ** 4, color=fs.PAL["blue"], ls=":", label=r"$12h^2+240h^4$")
    axs[0].set_xlabel(r"$h = mH$")
    axs[0].set_ylabel(r"$-d\ln M_{AH}/d\ln a$")
    axs[0].legend(frameon=False)
    rr = np.linspace(8, 60, 200)
    vv = [capture_threshold(r)[1] for r in rr]
    axs[1].plot(rr, vv, color=fs.PAL["red"], label="threshold (lead)")
    axs[1].plot(rr, 4.0 / rr, **fs.GUIDE, label=r"$4M/r_{ta}$")
    for rta in (16.1, 33.4):
        axs[1].plot([rta], [out["W8"][f"r_ta={rta}"]["v_tangential"]], "o", mfc="none", color=fs.PAL["blue"])
    axs[1].set_xlabel(r"$r_{ta}/M$")
    axs[1].set_ylabel(r"tangential speed $L/r_{ta}$")
    axs[1].legend(frameon=False)
    fs.save(fig, os.path.join(args.out, "verifier_check"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
