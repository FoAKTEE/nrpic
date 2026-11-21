"""Survival against spin at r_p = 10 for equatorial E = 1 orbits (JOURNAL entry 5): 2402's binary,
chart 'bks', iota = pi/6, pi/3, pi/2, 24 orientations (6 nodes x 4 phases), a = -0.9 ... 0.9
(a < 0: the orbit is retrograde with respect to the hole).  Beside it the factor 1 + 3 K/(2 r_p^2)
with K = (a - L_z)^2 + Q (Marck's constant as written at main.tex:462): the ratio of the radial
tidal eigenvalue at a turning point to its Newtonian value 2 M/r^3, -(M/r^3)(2 + 3 L^2/r^2) in
Schwarzschild with L^2 -> K in Kerr [JUDGEMENT; TO VERIFY, no locator in the sources at hand].

    <venv>/bin/python -I spin_trend.py <outdir> [--workers N]
"""
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
FID = dict(mb=25.0 / 4e6, q12=10.0 / 15.0, a0=20000 * 25.0 / 4e6, r0=100.0, rp=10.0)
SPINS = [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9]
IOTAS = [math.pi / 6, math.pi / 3, math.pi / 2]


def one(job):
    import hrna_incl as H
    s = job["spin"]
    Lz = H.lz_range(FID["rp"], s)[1]
    r = H.run_incl("hrna", "bks", s, FID["mb"], FID["q12"], FID["a0"], FID["rp"], Lz, job["iota"],
                   job["Omega"], job["phase"], FID["r0"])
    return dict(job, Lz=Lz, survived=r["survived"])


def main(outdir, workers):
    os.makedirs(outdir, exist_ok=True)
    jobs = [dict(spin=s, iota=io, Omega=j * math.pi / 3, phase=l * math.pi / 4)
            for s in SPINS for io in IOTAS for j in range(6) for l in range(4)]
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(one, jobs, chunksize=8))
    import hrna_incl as H
    rows = []
    for s in SPINS:
        Lz = H.lz_range(FID["rp"], s)[1]
        Q = 0.0
        K = (s - Lz) ** 2 + Q
        sf = [float(np.mean([r["survived"] for r in res if r["spin"] == s and r["iota"] == io])) for io in IOTAS]
        rows.append(dict(spin=s, Lz=Lz, K=K, tidal_factor=1 + 1.5 * K / FID["rp"] ** 2, sf=sf))
    with open(os.path.join(outdir, "spin_trend.json"), "w") as fh:
        json.dump(dict(fiducial=FID, iotas=IOTAS, rows=rows), fh, indent=1)
    print(json.dumps(rows, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.9))
    ax = fs.inch_axes(fig, 0.6, 0.5, 2.7, 2.1)
    cols = fs.series_colors(3)
    for k, (io, c) in enumerate(zip(IOTAS, cols)):
        ax.plot(SPINS, [r["sf"][k] for r in rows], "o-", color=c, label=r"$\iota=%s$" % ["\\pi/6", "\\pi/3", "\\pi/2"][k])
    ax.set_xlabel(r"spin $a/M$ (equatorial orbit, $r_p=10$)")
    ax.set_ylabel("survival fraction (24 orientations)")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=6, loc="upper left")
    ax2 = ax.twinx()
    ax2.plot(SPINS, [r["tidal_factor"] for r in rows], "--", color="k", lw=0.8)
    ax2.set_ylabel(r"$1 + 3K/(2r_p^2)$ (dashed)")
    fs.save(fig, os.path.join(outdir, "spin_trend"))


if __name__ == "__main__":
    a = sys.argv[1:]
    w = int(a[a.index("--workers") + 1]) if "--workers" in a else 1
    main(a[0] if a and not a[0].startswith("--") else os.environ["NRPIC_RUN_DIR"], w)
