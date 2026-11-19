#!/usr/bin/env python3
"""Lead's check L15: fluid onset of the radial instability along the King family, to place
the collisional cluster runs CC1 (y0 = 0.334032) and CC2 (y0 = 0.314) of threshold_scan.

Reference solution only (decision 0010). The King model f = exp(1 - E/E0) - 1 of
arXiv:2009.08163 is the F21 kernel exp((1 - E/E0)/b) - 1 at b = 1 (verifier V3); in the F21
variables of gravothermal/tmb.py, 1 - b w0 = E_min/E0 = exp(-y0), so w0 = 1 - exp(-y0).
The equilibrium comes from tmb.solve/tmb.structure, the lowest omega^2 of Chandrasekhar's
pulsation equation from models/fluid_onset.omega2 (finite elements), with the adiabatic
index of the variant: F21 (1 + p/u of the truncated distribution), J_E (Juttner Gamma_1 at
the energy-matched temperature, the track's Kn -> 0 anchor), J_p (Gamma_1 at theta = p/n).
Step (a) checks tmb at b = 1 against the King model JSON (evstatic.py, an independent
solver). Prediction L15 in tracks/C-sidm/JOURNAL.md (2026-11-19T15:15Z).
Output: $NRPIC_RUN_DIR/rv_king_onset.json, rv_king_onset.{png,pdf}.
"""
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
from scipy.optimize import brentq, minimize_scalar  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402

TR = os.path.join(rv.WT, "tracks", "C-sidm")
sys.path.insert(0, os.path.join(TR, "models"))
import fluid_onset as fo  # noqa: E402  (also puts gravothermal/ and collide/REFERENCES on the path)
import tmb  # noqa: E402

B = 1.0
MODELS = os.path.join(rv.SCR, "C-sidm-20261115-120610-b4592be")
TAGS = ("king_y0p31400", "king_y0p32400", "king_y0p33403", "king_y0p34400", "king_y0p35400")


def w0_of(y0):
    return 1.0 - math.exp(-y0)


def check_models():
    out = {}
    for tag in TAGS:
        m = json.load(open(os.path.join(MODELS, f"{tag}_stratified_N10000_s1.json")))
        eq = tmb.solve(B, w0_of(m["y0"]))
        out[tag] = dict(y0=m["y0"], Zc_json=m["Zc_infinity"], Zc_tmb=eq["Z0"],
                        RM_json=m["R_areal"], RM_tmb=1.0 / eq["C"],
                        Eb_json=m["Eb_over_M0"], eps_tmb=eq["eps"],
                        rel_Zc=eq["Z0"] / m["Zc_infinity"] - 1, rel_RM=(1.0 / eq["C"]) / m["R_areal"] - 1)
        print(tag, out[tag], flush=True)
    return out


def onset(variant, N, grid):
    vals = [fo.omega2(B, w0_of(y), variant, N)[0] for y in grid]
    for i in range(len(grid) - 1):
        if vals[i] > 0 >= vals[i + 1]:
            y = brentq(lambda v: fo.omega2(B, w0_of(v), variant, N)[0], grid[i], grid[i + 1],
                       xtol=1e-8, rtol=1e-10)
            eq = tmb.solve(B, w0_of(y))
            return dict(y0=y, Z0=eq["Z0"], R_over_M=1.0 / eq["C"], scan_y0=list(map(float, grid)),
                        scan_omega2=vals)
    return dict(y0=None, scan_y0=list(map(float, grid)), scan_omega2=vals)


def main():
    out = rv.outdir()
    res = dict(models=check_models())
    # binding-energy maximum along b = 1 with tmb (V3: y_max = 0.334032 with kingsolve)
    opt = minimize_scalar(lambda y: -tmb.solve(B, w0_of(y))["eps"], bounds=(0.25, 0.42),
                          method="bounded", options=dict(xatol=1e-9))
    res["eps_max_y0"] = float(opt.x)
    grid = np.linspace(0.12, 0.42, 16)
    res["onset"] = {}
    for v in ("F21", "J_E", "J_p"):
        for N in (600, 1200):
            t0 = time.time()
            r = onset(v, N, grid)
            r["seconds"] = round(time.time() - t0, 1)
            res["onset"][f"{v}_N{N}"] = r
            print(v, N, r.get("y0"), r.get("Z0"), r["seconds"], flush=True)
    # omega^2 along the family for the figure, and the central indices at CC1, CC2
    ys = np.linspace(0.12, 0.42, 31)
    res["seq"] = dict(y0=ys.tolist(), eps=[tmb.solve(B, w0_of(y))["eps"] for y in ys],
                      **{v: [fo.omega2(B, w0_of(y), v, 600)[0] for y in ys] for v in ("F21", "J_E", "J_p")})
    res["central"] = {tag: fo.central_indices(B, w0_of(res["models"][tag]["y0"]))
                      for tag in ("king_y0p31400", "king_y0p33403")}
    json.dump(res, open(os.path.join(out, "rv_king_onset.json"), "w"), indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH * 0.95, 3.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.32)
    s = res["seq"]
    for v, c in (("F21", fs.PAL["blue"]), ("J_E", fs.PAL["red"]), ("J_p", fs.PAL["yellow"])):
        ax[0].plot(s["y0"], s[v], "-", color=c, lw=1.3, label=v)
        y = res["onset"][f"{v}_N1200"].get("y0")
        if y:
            ax[0].plot([y], [0], "o", color=c, ms=5)
    ax[0].axhline(0, **fs.GUIDE)
    ax[1].plot(s["y0"], s["eps"], "-", color="k", lw=1.3)
    for a in ax:
        for y, lab in ((0.314, "CC2"), (res["models"]["king_y0p33403"]["y0"], "CC1")):
            a.axvline(y, color="0.5", lw=0.8, ls=":")
        a.set_xlabel(r"$y_0$ (King family, $b=1$)")
    ax[0].text(0.316, ax[0].get_ylim()[1] * 0.85, "CC2", fontsize=7)
    ax[0].text(0.336, ax[0].get_ylim()[1] * 0.85, "CC1", fontsize=7)
    ax[0].set_ylabel(r"lowest $\omega^2$ (F21 units)")
    ax[0].legend(fontsize=7, frameon=False)
    ax[1].set_ylabel(r"$\epsilon$ (tmb binding energy)")
    fs.save(fig, os.path.join(out, "rv_king_onset"))
    print(json.dumps({k: res[k] for k in ("eps_max_y0", "onset")}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
