"""V4b: is my reference count in the inner ranges converged? (JOURNAL entry 4, outcome.)
Recomputes the integrals of n = J^t Sigma^2 sin(theta) over 2.2 <= r < 4 and 4 <= r < 6 with
twice the r nodes and twice the angle nodes of run D-20261121-034048-17427b0, and the 0-4
integral without the energy cut (E < 1), and normalises with the total of that run. Also
compares the local density with the track's own curves (kerr_curves_ours.npz of run
D-bh-dress-20261115-171615-8adbbdd, E < 1) at a few points."""
import argparse
import json
import math
import os

import numpy as np

import v4_kerr_stat as W

V4RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261121-034048-17427b0"
TRACK_CURVES = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-171615-8adbbdd/kerr_curves_ours.npz"


def job(args):
    r, mu, ecut = args
    os.environ["OMP_NUM_THREADS"] = "1"
    R = W.Ref(ecut, nE=40, nL=40, npsi=16)
    return r, mu, ecut, R.n_over_sin(r, mu)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    v4 = json.load(open(V4RUN + "/v4_results.json"))["reference"]
    pts = np.array(v4["points"])
    w = np.array(v4["weights"])
    rid = np.array(v4["range_id"])
    per_old = np.array([np.sum(pts[rid == k, 2] * w[rid == k]) for k in range(6)])
    total_old = per_old.sum()
    tasks, meta = [], []
    for k, (lo, hi, nr) in enumerate(((2.2, 4.0, 24), (4.0, 6.0, 12))):
        xr, wr = np.polynomial.legendre.leggauss(nr)
        xm, wm = np.polynomial.legendre.leggauss(16)
        for ri, wri in zip(0.5 * (lo + hi) + 0.5 * (hi - lo) * xr, 0.5 * (hi - lo) * wr):
            for mi, wmi in zip(0.5 * (xm + 1), 0.5 * wm):
                tasks.append((float(ri), float(mi), 0.99))
                meta.append((k, wri * wmi))
    # E < 1 for 0-4 at the original resolution
    xr, wr = np.polynomial.legendre.leggauss(12)
    xm, wm = np.polynomial.legendre.leggauss(8)
    for ri, wri in zip(3.1 + 0.9 * xr, 0.9 * wr):
        for mi, wmi in zip(0.5 * (xm + 1), 0.5 * wm):
            tasks.append((float(ri), float(mi), 1 - 1e-12))
            meta.append((2, wri * wmi))
    # local comparison with the track's curves at E < 1
    z = np.load(TRACK_CURVES)
    comp_pts = [(r, mu) for r in (2.6, 3.0, 3.5, 5.0, 8.0) for mu in (0.0, 0.5)]
    for r, mu in comp_pts:
        tasks.append((r, mu, 1 - 1e-12))
        meta.append((3, 0.0))
    import multiprocessing as mp
    with mp.get_context("fork").Pool(args.procs) as pool:
        vals = pool.map(job, tasks)
    new = np.zeros(3)
    local = []
    for (k, wt), (r, mu, ec, v) in zip(meta, vals):
        if k < 3:
            new[k] += v * wt
        else:
            key = "1.5708" if mu == 0.0 else "1.0472"
            rr, nt = z["hern_a0.8_th%s_r" % key], z["hern_a0.8_th%s_n" % key]
            local.append(dict(r=r, mu=mu, mine=v, track=float(np.interp(r, rr, nt)), ratio=v / float(np.interp(r, rr, nt))))
    res = dict(per_range_old=per_old.tolist(), total_old=float(total_old),
               range_0_4_doubled=float(new[0]), range_4_6_doubled=float(new[1]),
               rel_change_0_4=float(new[0] / per_old[0] - 1), rel_change_4_6=float(new[1] / per_old[1] - 1),
               expected_0_4_doubled=float(48000 * new[0] / total_old), expected_4_6_doubled=float(48000 * new[1] / total_old),
               range_0_4_no_Ecut_over_cut=float(new[2] / per_old[0]), local_vs_track_E_lt_1=local)
    print(json.dumps(res, indent=1))
    with open(args.out + "/v4b_results.json", "w") as f:
        json.dump(res, f, indent=1)
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.15, top=0.96)
    for mu, c in ((0.0, fs.PAL["red"]), (0.5, fs.PAL["blue"])):
        L = [x for x in local if x["mu"] == mu]
        ax.plot([x["r"] for x in L], [x["ratio"] - 1 for x in L], "o-", color=c, label="cos theta = %.1f" % mu)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xlabel(r"$r/M$")
    ax.set_ylabel("my n / track's n - 1 (E < 1)")
    ax.legend(loc="best", fontsize=8)
    fs.save(fig, args.out + "/v4b_local")


if __name__ == "__main__":
    main()
