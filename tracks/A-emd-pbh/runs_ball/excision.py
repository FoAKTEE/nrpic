#!/usr/bin/env python3
"""Which criterion removed particles in the BH-1 runs (package runs_ball, JOURNAL entry 16,
prediction E; open question of entry 9).

The executable of these runs (scratch/core/exe/core_gauge, source b4430da) removes a particle
in the push (athenak/src/particles/nrpic.cpp at b4430da, lines 488-531) when
  (a) the lapse interpolated to the particle is below <particles> alpha_exc (0.1 here), or
  (b) it lies inside ah_exc_factor times the smallest radius of a found horizon (the
      option is absent from bh.athinput and bh_smr.athinput: default -1, off), or
  (c) its position or momentum is no longer finite after the push;
all three set the same flag (-2), and nrpic.hst counts them together ([17] n_excised,
[18] m_excised). The record does not say which, so this script looks at what each
criterion needs:
  - the smallest lapse on the mesh ([16] alpha_min of nrpic.hst, a minimum over the cells
    of every MeshBlock) against alpha_exc around each removal: (a) needs an interpolated
    lapse below 0.1, which a mesh minimum well above 0.1 rules out (the interpolant of the
    run, b-spline or Catmull-Rom, can undershoot the cell values only by a fraction of the
    variation over one cell);
  - the tracked particles that disappear: their last recorded lapse at the particle, their
    last coordinate radius, the size of their momentum and its growth over the last records
    (trajectory files, every output record of traj_dcycle);
  - every particle (snapshots part.NNNNN.bin): which tags are missing from the next snapshot,
    with their radius and |u| at the last snapshot that holds them.

    excision.py --run <run dir>:<label>:<prep lat dir> [...] --alpha-exc 0.1 --out <dir> [--figdir <dir>]
"""
import argparse
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402


def analyse(spec, alpha_exc):
    d, lab, prep = spec.split(":")[:3]
    tr = C.load_json(os.path.join(prep, "tracked.json"))
    h = C.read_hst(os.path.join(d, "ball.nrpic.hst"))
    t, nexc, mexc, nesc = h[:, 0], h[:, 16], h[:, 17], h[:, 18]
    amin, aprobe, npart = h[:, 15], h[:, 12], h[:, 2]
    out = dict(label=lab, dir=d, t_end=float(t[-1]), n_start=int(npart[0]), n_end=int(npart[-1]),
               n_excised_end=int(nexc[-1]), m_excised_end=float(mexc[-1]), n_escaped_end=int(nesc[-1]),
               alpha_min_mesh_min=float(np.nanmin(amin)), t_alpha_min_mesh_min=float(t[int(np.nanargmin(amin))]),
               alpha_probe_min=float(np.nanmin(aprobe)))
    j = np.nonzero(nexc > 0)[0]
    out["t_first_excision"] = float(t[j[0]]) if len(j) else None
    lo = np.nonzero(amin < alpha_exc)[0]
    out["t_first_alpha_min_mesh_lt_exc"] = float(t[lo[0]]) if len(lo) else None
    # removals in each history interval, and the mesh minimum of the lapse there
    dn = np.diff(nexc)
    steps = []
    for k in np.nonzero(dn > 0)[0]:
        steps.append(dict(t0=float(t[k]), t1=float(t[k + 1]), n=int(dn[k]), m=float(mexc[k + 1] - mexc[k]),
                          alpha_min_mesh=float(min(amin[k], amin[k + 1])), alpha_probe=float(aprobe[k + 1])))
    out["n_removal_intervals"] = len(steps)
    out["removals_with_alpha_min_mesh_ge_exc"] = dict(
        n=int(sum(s["n"] for s in steps if s["alpha_min_mesh"] >= alpha_exc)),
        m=float(sum(s["m"] for s in steps if s["alpha_min_mesh"] >= alpha_exc)))
    out["removals_with_alpha_min_mesh_lt_exc"] = dict(
        n=int(sum(s["n"] for s in steps if s["alpha_min_mesh"] < alpha_exc)),
        m=float(sum(s["m"] for s in steps if s["alpha_min_mesh"] < alpha_exc)))
    out["removal_intervals"] = steps[:: max(1, len(steps) // 60)]
    # tracked particles that disappear before the end
    T = C.read_traj_many([d])
    tt = T["time"]
    tags = T["tag"]
    keep = tags < tr["n_track"]
    x, u, al = T["x"][:, keep], T["u"][:, keep], T["alpha"][:, keep]
    Ri = np.array(tr["R_i"])[tags[keep]]
    fin = np.all(np.isfinite(x), axis=2)
    last = np.array([np.nonzero(fin[:, p])[0].max() if fin[:, p].any() else -1 for p in range(fin.shape[1])])
    gone = np.nonzero(last < len(tt) - 1)[0]
    rows = []
    for p in gone:
        i = last[p]
        un = np.linalg.norm(u[:, p], axis=1)
        i0 = max(0, i - 8)
        rows.append(dict(R_i=float(Ri[p]), t_last=float(tt[i]), alpha_last=float(al[i, p]),
                         alpha_min_traj=float(np.nanmin(al[:i + 1, p])),
                         r_last=float(np.linalg.norm(x[i, p])), u_last=float(un[i]),
                         u_growth_last8=float(un[i] / un[i0]) if un[i0] > 0 else None,
                         u_max_before=float(np.nanmax(un[:i + 1]))))
    out["tracked"] = dict(n=int(keep.sum()), n_gone=len(rows),
                          n_gone_alpha_last_lt_exc=int(sum(r["alpha_last"] < alpha_exc for r in rows)),
                          n_gone_alpha_last_lt_2exc=int(sum(r["alpha_last"] < 2 * alpha_exc for r in rows)),
                          alpha_last_min=float(min([r["alpha_last"] for r in rows], default=np.nan)),
                          alpha_last_median=float(np.median([r["alpha_last"] for r in rows])) if rows else None,
                          r_last_median=float(np.median([r["r_last"] for r in rows])) if rows else None,
                          u_last_median=float(np.median([r["u_last"] for r in rows])) if rows else None,
                          u_last_max=float(max([r["u_last"] for r in rows], default=np.nan)),
                          t_last_min=float(min([r["t_last"] for r in rows], default=np.nan)),
                          rows=rows[:: max(1, len(rows) // 40)])
    # all particles: snapshots
    snaps = sorted(glob.glob(os.path.join(d, "ball.part.*.bin")))
    srows = []
    prev = None
    for f in snaps:
        s = C.read_snapshot(f)
        if prev is not None:
            miss = np.setdiff1d(prev["tag"], s["tag"])
            if len(miss):
                idx = np.searchsorted(prev["tag"], miss) if np.all(np.diff(prev["tag"]) > 0) else \
                    np.nonzero(np.isin(prev["tag"], miss))[0]
                r = np.linalg.norm(prev["x"][idx], axis=1)
                un = np.linalg.norm(prev["u"][idx], axis=1)
                srows.append(dict(t_prev=prev["time"], t=s["time"], n_missing=int(len(miss)),
                                  m_missing=float(prev["m"][idx].sum()),
                                  r_prev_median=float(np.median(r)), r_prev_max=float(r.max()),
                                  u_prev_median=float(np.median(un)), u_prev_max=float(un.max())))
        o = np.argsort(s["tag"])
        prev = dict(time=s["time"], tag=s["tag"][o], x=s["x"][o], u=s["u"][o], m=s["m"][o])
    out["snapshots"] = srows
    series = dict(t=t, nexc=nexc, mexc=mexc, amin=amin, aprobe=aprobe,
                  gone_t=np.array([r["t_last"] for r in rows]), gone_alpha=np.array([r["alpha_last"] for r in rows]),
                  gone_u=np.array([r["u_last"] for r in rows]), gone_r=np.array([r["r_last"] for r in rows]))
    return out, series


def figure(a, runs, sers):
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = [fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    fig = plt.figure(figsize=(8.0, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, wspace=0.28, hspace=0.32)
    ax = [fig.add_subplot(2, 2, k + 1) for k in range(4)]
    for c, r, s in zip(cols, runs, sers):
        ax[0].plot(s["t"], s["mexc"], color=c, lw=1.5, label=f"{r['label']}: rest mass removed")
        ax[1].semilogy(s["t"], s["amin"], color=c, lw=1.5, label=f"{r['label']}: smallest lapse on the mesh")
        ax[1].semilogy(s["t"], s["aprobe"], color=c, lw=1.0, ls=":", label=f"{r['label']}: lapse at the origin")
        if len(s["gone_t"]):
            ax[2].semilogy(s["gone_t"], s["gone_alpha"], "o", ms=3, color=c, label=r["label"])
            ax[3].semilogy(s["gone_t"], s["gone_u"], "o", ms=3, color=c, label=r["label"])
    ax[1].axhline(a.alpha_exc, **fs.GUIDE)
    ax[2].axhline(a.alpha_exc, **fs.GUIDE)
    ax[0].set_ylabel("rest mass removed (M)")
    ax[1].set_ylabel("lapse")
    ax[2].set_ylabel("lapse at the particle, last record")
    ax[3].set_ylabel(r"$|u_i|$ at the last record")
    for k in range(4):
        ax[k].set_xlabel("code time t (M)")
        ax[k].legend(fontsize=6, loc="best")
    ax[0].set_title("particles removed (nrpic.hst [18])", fontsize=9)
    ax[1].set_title(r"lapse (dashed: $\alpha_{\rm exc}$)", fontsize=9)
    ax[2].set_title("tracked particles that disappear", fontsize=9)
    ax[3].set_title("their momentum before removal", fontsize=9)
    outs = fs.save(fig, os.path.join(a.out, "fig_excision"))
    plt.close(fig)
    if a.figdir:
        import shutil
        os.makedirs(a.figdir, exist_ok=True)
        for f in outs:
            if f.endswith(".png"):
                shutil.copy(f, os.path.join(a.figdir, os.path.basename(f)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--alpha-exc", type=float, default=0.1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs, sers = [], []
    for spec in a.run:
        r, s = analyse(spec, a.alpha_exc)
        runs.append(r)
        sers.append(s)
        tk = r["tracked"]
        print(f"[{r['label']}] removed {r['n_excised_end']} (mass {r['m_excised_end']:.4f}), first at "
              f"{r['t_first_excision']}; mesh alpha_min min {r['alpha_min_mesh_min']:.4f} at "
              f"{r['t_alpha_min_mesh_min']}; first mesh alpha_min < exc at {r['t_first_alpha_min_mesh_lt_exc']}; "
              f"removed while mesh alpha_min >= exc: {r['removals_with_alpha_min_mesh_ge_exc']}; "
              f"tracked gone {tk['n_gone']} (alpha_last < exc: {tk['n_gone_alpha_last_lt_exc']}, "
              f"median alpha_last {tk['alpha_last_median']}, median |u| {tk['u_last_median']}, "
              f"max |u| {tk['u_last_max']})")
        for srow in r["snapshots"]:
            print("   snapshot", srow)
    C.write_json(os.path.join(a.out, "excision.json"), dict(alpha_exc=a.alpha_exc, runs=runs))
    figure(a, runs, sers)


if __name__ == "__main__":
    main()
