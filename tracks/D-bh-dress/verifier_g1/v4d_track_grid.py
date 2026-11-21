"""V4d (after the verdicts): where do the track's expected counts lose the inner particles?
Reads the track's reference grid expected.npz of run D-bh-dress-20261115-172646-ed6a510
(n_x per d ln r d cos(theta) on 73 x 10 nodes) and integrates it (a) with the trapezoid rule
as the track's analysis does, (b) with my own quadrature of the same grid values (cubic
interpolation in ln r and cos(theta), fine sub-grid), and compares both with my reference
counts of run D-20261121-034048-17427b0."""
import argparse
import json
import math
import os

import numpy as np
from scipy.interpolate import RectBivariateSpline

EXP = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172646-ed6a510/expected.npz"
V4RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261121-034048-17427b0"
RANGES = [(0, 4), (4, 6), (6, 10), (10, 16), (16, 40)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    args = ap.parse_args()
    d = np.load(EXP)
    x, mu, nx = d["x"], d["mu"], d["n_x"]
    N = 48000
    # (a) trapezoid in mu, then in x, cumulative with linear interpolation at the edges
    nm = np.trapezoid(nx, mu, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (nm[1:] + nm[:-1]) * np.diff(x))])
    tot = cum[-1]
    trap = {}
    for lo, hi in RANGES:
        a = math.log(max(lo, math.exp(x[0])))
        trap["%d-%d" % (lo, hi)] = N * (np.interp(math.log(hi), x, cum) - np.interp(a, x, cum)) / tot
    # (b) bicubic interpolation of the same values (clipped at 0), fine sub-grid, Simpson-like
    sp = RectBivariateSpline(x, mu, nx, kx=3, ky=3)
    xf = np.linspace(x[0], x[-1], 20 * len(x))
    mf = np.linspace(0, 1, 401)
    F = np.clip(sp(xf, mf), 0, None)
    nmf = np.trapezoid(F, mf, axis=1)
    cumf = np.concatenate([[0.0], np.cumsum(0.5 * (nmf[1:] + nmf[:-1]) * np.diff(xf))])
    totf = cumf[-1]
    fine = {}
    for lo, hi in RANGES:
        a = math.log(max(lo, math.exp(x[0])))
        fine["%d-%d" % (lo, hi)] = N * (np.interp(math.log(hi), xf, cumf) - np.interp(a, xf, cumf)) / totf
    mine = {k: v["expected_mine"] for k, v in json.load(open(V4RUN + "/v4_results.json"))["ranges"].items()}
    res = {k: dict(track_grid_trapezoid=trap[k], track_grid_bicubic=fine[k], mine=mine[k]) for k in trap}
    print(json.dumps(res, indent=1))
    with open(args.out + "/v4d_results.json", "w") as f:
        json.dump(res, f, indent=1)
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.15, top=0.96)
    lab = list(res)
    xx = np.arange(len(lab))
    ax.plot(xx, [res[k]["track_grid_trapezoid"] / res[k]["mine"] - 1 for k in lab], "o-", color=fs.PAL["red"], label="track's grid, trapezoid")
    ax.plot(xx, [res[k]["track_grid_bicubic"] / res[k]["mine"] - 1 for k in lab], "s--", color=fs.PAL["blue"], label="track's grid, bicubic")
    ax.axhline(0, **fs.GUIDE)
    ax.set_xticks(xx)
    ax.set_xticklabels([k + " M" for k in lab])
    ax.set_ylabel("expected / mine - 1")
    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, args.out + "/v4d_track_grid")


if __name__ == "__main__":
    main()
