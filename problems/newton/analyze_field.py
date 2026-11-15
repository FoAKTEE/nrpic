#!/usr/bin/env python3
"""Tests T1 and T2 of the Newtonian mode: field of a point mass and of a homogeneous
ball on an isolated domain against the exact fields (problems/newton/README.md).

    analyze_field.py point|ball --ic FILE.json --run N:RUNDIR [--run N:RUNDIR ...]
                     --out DIR [--box 4.0] [--dt 1e-6]

Each run is one step of length dt from rest: the momentum of a particle after the step,
divided by dt, is the acceleration the code applied to it. The potential at the probes
is the lapse column of the history at cycle 0. Writes DIR/field_<kind>.png and
DIR/field_<kind>.json (errors and measured orders).
"""
import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def read_input(path):
    """Parameters of an athinput file as {block: {key: value string}}."""
    out, blk = {}, None
    with open(path) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            if line.startswith("<"):
                blk = line.strip("<>")
                out[blk] = {}
            elif "=" in line and blk is not None:
                k, v = line.split("=", 1)
                out[blk][k.strip()] = v.strip()
    return out


def probes(rundir):
    """Positions of the probes (index 0: the main probe) and the potential there."""
    inp = read_input(glob.glob(os.path.join(rundir, "*.athinput"))[0])["particles"]
    pos = [[float(inp["probe_x%d" % d]) for d in (1, 2, 3)]]
    for n in range(int(inp.get("nprobe", "0"))):
        pos.append([float(inp["probe%d_x%d" % (n + 1, d)]) for d in (1, 2, 3)])
    h = nw.read_nrpic_hst(glob.glob(os.path.join(rundir, "*.nrpic.hst"))[0])[0]
    phi = [h[12]] + [h[32 + 3*n] for n in range(len(pos) - 1)]
    return np.array(pos), np.array(phi)


def dx_axis(ax, dxs):
    """Logarithmic axis of the cell size with one labelled tick per resolution."""
    ax.set_xscale("log")
    ax.set_xticks(dxs)
    ax.set_xticklabels(["1/%d" % round(1.0/d) for d in dxs])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlim(dxs.min()/1.25, dxs.max()*1.25)
    ax.set_xlabel(r"$\Delta x$")


def order(e, dx):
    """Measured orders between consecutive resolutions."""
    return [float(np.log(e[i]/e[i+1])/np.log(dx[i]/dx[i+1])) for i in range(len(e) - 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("point", "ball"))
    ap.add_argument("--ic", required=True)
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--box", type=float, default=4.0)
    ap.add_argument("--dt", type=float, default=1.0e-6)
    ap.add_argument("--ideal-radius", action="store_true",
                    help="ball: reference with the nominal radius instead of the radius "
                         "of the ball of the same mass and the density of the lattice")
    a = ap.parse_args()
    meta = json.load(open(a.ic))
    c = np.array(meta["center"])
    gm = meta["mass"]
    nm = meta["nmassive"]
    rad = meta.get("radius", 0.0)
    if a.kind == "ball" and not a.ideal_radius:
        # The lattice points inside the sphere are not exactly (4 pi/3)(R/h)^3 in number
        # (here 0.1 per cent more), so the particles sample a homogeneous ball of the
        # same mass whose density is M/(N h^3): its radius is used for the reference.
        rad = (3.0*nm*meta["spacing"]**3/(4.0*np.pi))**(1.0/3.0)
    runs = sorted([(int(r.split(":")[0]), r.split(":", 1)[1]) for r in a.run])
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    cols = fs.SERIES

    res = dict(kind=a.kind, runs={}, N=[n for n, _ in runs], reference_radius=rad)
    data = []
    for n, d in runs:
        dx = a.box/n
        snaps = sorted(glob.glob(os.path.join(d, "*.part.*.bin")))
        t, cyc, x, u, m, tag = nw.read_snapshot(snaps[-1])
        assert t > 0.0 and np.all(tag == np.arange(len(tag)))
        g = u/a.dt
        xt, gt = x[nm:], g[nm:]
        if a.kind == "point":
            phi_e, g_e = nw.point_field(xt, c, gm)
        else:
            phi_e, g_e = nw.ball_field(xt, c, gm, rad)
        dvec = xt - c
        r = np.sqrt((dvec*dvec).sum(axis=1))
        gr = (gt*dvec).sum(axis=1)/r
        err = np.sqrt(((gt - g_e)**2).sum(axis=1))
        ge = np.sqrt((g_e**2).sum(axis=1))
        ppos, pphi = probes(d)
        if a.kind == "point":
            pe, _ = nw.point_field(ppos, c, gm)
        else:
            pe, _ = nw.ball_field(ppos, c, gm, rad)
        pr = np.sqrt(((ppos - c)**2).sum(axis=1))
        data.append(dict(n=n, dx=dx, r=r, gr=gr, err=err, ge=ge, pr=pr,
                         perr=np.abs(pphi - pe), pe=pe, self=g[0] if a.kind == "point"
                         else None))

    dxs = np.array([d["dx"] for d in data])
    if a.kind == "point":
        # far field: the same tracers at every resolution, r >= 0.5
        far = data[0]["r"] >= 0.5
        rms = np.array([np.sqrt(np.mean((d["err"][far]/d["ge"][far])**2)) for d in data])
        mx = np.array([np.max(d["err"][far]/d["ge"][far]) for d in data])
        sel = data[0]["pr"] >= 0.4               # probes away from the mass
        prel = np.array([np.max(d["perr"][sel]/np.abs(d["pe"][sel])) for d in data])
        prms = np.array([np.sqrt(np.mean((d["perr"][sel]/d["pe"][sel])**2)) for d in data])
        res.update(far_rms_rel=rms.tolist(), far_max_rel=mx.tolist(),
                   far_rms_order=order(rms, dxs), probe_max_rel=prel.tolist(),
                   probe_rms_rel=prms.tolist(), probe_rms_order=order(prms, dxs),
                   probe_each_rel=[((d["perr"]/np.abs(d["pe"]))[sel]).tolist()
                                   for d in data],
                   probe_distance=data[0]["pr"][sel].tolist(),
                   self_force_dx2=[(d["self"]*d["dx"]**2).tolist() for d in data])
        for d in data:
            x = d["r"]/d["dx"]
            band = {}
            for lo, hi in ((0.0, 2.0), (2.0, 4.0), (4.0, 8.0), (8.0, 16.0), (16.0, 60.0)):
                s = (x >= lo) & (x < hi)
                if s.sum() > 0:
                    band["%g-%g" % (lo, hi)] = [int(s.sum()),
                                                float(np.sqrt(np.mean((d["err"][s]
                                                                       / d["ge"][s])**2)))]
            res["runs"][str(d["n"])] = dict(rms_rel_by_r_over_dx=band)

        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.95, wspace=0.34)
        ax = axs[0]
        for d, col in zip(data, cols):
            ax.plot(d["r"]/d["dx"], -d["gr"]*d["r"]**2, ".", ms=2, color=col,
                    alpha=0.6, rasterized=True, label="N = %d" % d["n"])
        ax.axhline(1.0, **fs.GUIDE)
        ax.set_xscale("log")
        ax.set_xlim(0.4, 60)
        ax.set_ylim(0.0, 1.6)
        ax.set_xlabel(r"$r/\Delta x$")
        ax.set_ylabel(r"$-g_r\,r^2/GM$")
        ax.legend(loc="lower right", markerscale=4, handletextpad=0.2)
        ax = axs[1]
        for d, col in zip(data, cols):
            ax.plot(d["r"]/d["dx"], d["err"]/d["ge"], ".", ms=2, color=col, alpha=0.6,
                    rasterized=True)
        xx = np.array([2.0, 60.0])
        ax.plot(xx, 1.0/xx**2, **fs.GUIDE)
        ax.text(9, 0.03, r"$(\Delta x/r)^2$", fontsize=9)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(0.4, 60)
        ax.set_ylim(1e-5, 3)
        ax.set_xlabel(r"$r/\Delta x$")
        ax.set_ylabel(r"$|\mathbf{g}-\mathbf{g}_{\rm exact}|/g_{\rm exact}$")
        ax = axs[2]
        ax.plot(dxs, rms, "o-", color=cols[1], label=r"force, rms, $r\geq0.5$")
        ax.plot(dxs, prms, "s-", color=cols[0], label="potential, rms, 8 probes")
        ax.plot(dxs, rms[0]*(dxs/dxs[0])**2, **fs.GUIDE)
        ax.set_yscale("log")
        dx_axis(ax, dxs)
        ax.set_ylim(1e-4, 1e-1)
        ax.set_ylabel("relative error")
        ax.legend(loc="upper left", fontsize=8)
    else:
        scale = gm/rad**2
        away = np.abs(data[0]["r"] - rad) > 0.25
        rms = np.array([np.sqrt(np.mean((d["err"][away]/scale)**2)) for d in data])
        mx_all = np.array([np.max(d["err"]/scale) for d in data])
        rms_all = np.array([np.sqrt(np.mean((d["err"]/scale)**2)) for d in data])
        shell = [np.abs(d["r"] - rad) < d["dx"] for d in data]
        rms_shell = np.array([np.sqrt(np.mean((d["err"][s]/scale)**2))
                              for d, s in zip(data, shell)])
        prel = np.array([np.max(d["perr"]/np.abs(d["pe"])) for d in data])
        res.update(away_rms=rms.tolist(), away_rms_order=order(rms, dxs),
                   all_rms=rms_all.tolist(), all_rms_order=order(rms_all, dxs),
                   all_max=mx_all.tolist(), all_max_order=order(mx_all, dxs),
                   shell_rms=rms_shell.tolist(), shell_rms_order=order(rms_shell, dxs),
                   shell_count=[int(s.sum()) for s in shell],
                   probe_max_rel=prel.tolist(), probe_order=order(prel, dxs))

        fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.95, wspace=0.34)
        ax = axs[0]
        d = data[-1]
        rr = np.linspace(0.0, 1.9, 400)
        ax.plot(rr, np.where(rr < rad, rr/rad, (rad/np.maximum(rr, 1e-9))**2),
                color=cols[0], label="exact")
        ax.plot(d["r"], -d["gr"]/scale, ".", ms=2, color=cols[1], alpha=0.6,
                rasterized=True, label="code, N = %d" % d["n"])
        ax.set_xlim(0, 1.9)
        ax.set_ylim(0, 1.15)
        ax.set_xlabel(r"$r/R$")
        ax.set_ylabel(r"$-g_r\,R^2/GM$")
        ax.legend(loc="lower center", markerscale=4, handletextpad=0.3)
        ax = axs[1]
        for d, col in zip(data, cols):
            ax.plot(d["r"], d["err"]/scale, ".", ms=2, color=col, alpha=0.6,
                    rasterized=True, label="N = %d" % d["n"])
        ax.axvline(rad, **fs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_xlim(0, 1.9)
        ax.set_ylim(1e-7, 1)
        ax.set_xlabel(r"$r/R$")
        ax.set_ylabel(r"$|\mathbf{g}-\mathbf{g}_{\rm exact}|\,R^2/GM$")
        ax.legend(loc="lower right", markerscale=4, handletextpad=0.2, fontsize=8)
        ax = axs[2]
        ax.plot(dxs, rms, "o-", color=cols[1], label=r"force, rms, $|r-R|>0.25$")
        ax.plot(dxs, rms_shell, "^-", color=cols[2],
                label=r"force, rms, $|r-R|<\Delta x$")
        ax.plot(dxs, prel, "s-", color=cols[0], label="potential, probes")
        ax.plot(dxs, rms[0]*(dxs/dxs[0])**2, **fs.GUIDE)
        ax.set_yscale("log")
        dx_axis(ax, dxs)
        ax.set_ylim(1e-5, 2.0)
        ax.set_ylabel(r"error")
        ax.legend(loc="upper left", fontsize=7)
    stem = "field_%s%s" % (a.kind, "_ideal_radius" if a.ideal_radius else "")
    fig.savefig(os.path.join(a.out, stem + ".png"), dpi=200)
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
