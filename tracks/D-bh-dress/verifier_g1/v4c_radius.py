"""V4c: would my reference counts equal the track's expected counts if the range boundaries
were taken in the Cartesian Kerr-Schild radius R = sqrt(x^2+y^2+z^2) = sqrt(r^2 + a^2 sin^2)
instead of the spheroidal r? (JOURNAL entry 6, outcome.) Uses only my reference grid of run
D-20261121-034048-17427b0 (n/sin(theta) at Gauss nodes in r and cos(theta)): moving the
boundary r = R1 to r1(mu) = sqrt(R1^2 - a^2 (1 - mu^2)) moves the integral
dI(R1) = sum_mu w_mu (n/sin)(R1, mu) (R1 - r1(mu)) from the range above R1 to the range below.
Also the particle counts of the run with the Cartesian radius, for completeness."""
import argparse
import glob
import json
import math
import os

import numpy as np

import vreaders as V

V4RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261121-034048-17427b0"
RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172611-1e40191"
TRACK_EXPECTED = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-174954-786ddcc/kerr_main_analysis.json"
A = 0.8
RANGES = [(0, 4), (4, 6), (6, 10), (10, 16), (16, 40)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    args = ap.parse_args()
    ref = json.load(open(V4RUN + "/v4_results.json"))
    R = ref["reference"]
    pts = np.array(R["points"])
    w = np.array(R["weights"])
    rid = np.array(R["range_id"])
    per = np.array([np.sum(pts[rid == k, 2] * w[rid == k]) for k in range(6)])
    tot = per.sum()
    N = ref["N"]
    mus = np.unique(pts[:, 1])
    xm, wm = np.polynomial.legendre.leggauss(len(mus))
    wmu = dict(zip(np.round(0.5 * (xm + 1), 12), 0.5 * wm))

    def dI(R1):
        s = 0.0
        for mu in mus:
            sel = pts[:, 1] == mu
            rr, vv = pts[sel, 0], pts[sel, 2]
            o = np.argsort(rr)
            v1 = np.interp(R1, rr[o], vv[o])
            r1 = math.sqrt(R1 * R1 - A * A * (1 - mu * mu))
            s += wmu[round(mu, 12)] * v1 * (R1 - r1)
        return s
    track = json.load(open(TRACK_EXPECTED))["ranges"]
    out = {}
    for k, (lo, hi) in enumerate(RANGES):
        Ib = per[k] + (dI(lo) if lo > 0 else 0.0) - dI(hi)
        out["%d-%d" % (lo, hi)] = dict(expected_spheroidal_r=float(N * per[k] / tot),
                                       expected_cartesian_R=float(N * Ib / tot),
                                       track_expected=float(track["%d-%d" % (lo, hi)]["expected"]))
    # particle counts with the Cartesian radius (time average over snapshots 1-200)
    cs, cc = [], []
    for ch in sorted(glob.glob(RUN + "/kerr_*")):
        snaps = sorted(glob.glob(ch + "/kerr.part.*.bin"))[1:]
        c1 = np.zeros(len(RANGES))
        c2 = np.zeros(len(RANGES))
        for sp in snaps:
            s = V.read_snapshot(sp)
            X, Y, Z = s["x"][:, 0], s["x"][:, 1], s["x"][:, 2]
            Rc = np.sqrt(X * X + Y * Y + Z * Z)
            b = Rc ** 2 - A * A
            r = np.sqrt(0.5 * (b + np.sqrt(b * b + 4 * A * A * Z * Z)))
            for k, (lo, hi) in enumerate(RANGES):
                c1[k] += np.sum((r >= lo) & (r < hi))
                c2[k] += np.sum((Rc >= lo) & (Rc < hi))
        cs.append(c1 / len(snaps))
        cc.append(c2 / len(snaps))
    cs = np.sum(cs, axis=0)
    cc = np.sum(cc, axis=0)
    for k, (lo, hi) in enumerate(RANGES):
        out["%d-%d" % (lo, hi)].update(time_avg_count_spheroidal_r=float(cs[k]), time_avg_count_cartesian_R=float(cc[k]),
                                       track_time_avg=float(track["%d-%d" % (lo, hi)]["time_avg_over_expected"] * track["%d-%d" % (lo, hi)]["expected"]))
    print(json.dumps(out, indent=1))
    with open(args.out + "/v4c_results.json", "w") as f:
        json.dump(out, f, indent=1)
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.15, top=0.96)
    lab = list(out)
    x = np.arange(len(lab))
    te = np.array([out[k]["track_expected"] for k in lab])
    ax.plot(x, [out[k]["expected_spheroidal_r"] / out[k]["track_expected"] - 1 for k in lab], "o-", color=fs.PAL["red"], label="mine, ranges in spheroidal r")
    ax.plot(x, [out[k]["expected_cartesian_R"] / out[k]["track_expected"] - 1 for k in lab], "s--", color=fs.PAL["blue"], label="mine, ranges in Cartesian R")
    ax.axhline(0, **fs.GUIDE)
    ax.set_xticks(x)
    ax.set_xticklabels([k + " M" for k in lab])
    ax.set_ylabel("my expected / track's expected - 1")
    ax.legend(loc="upper right", fontsize=8)
    fs.save(fig, args.out + "/v4c_radius")


if __name__ == "__main__":
    main()
