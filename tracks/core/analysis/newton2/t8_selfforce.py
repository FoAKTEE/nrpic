#!/usr/bin/env python3
"""Test T8 of work package newton2 (request of Track D for the interface note): the
force of the mesh on the single particle that sources it, against the position of the
particle in its cell.  One particle of mass 1 (G = 1), dx = 0.125, one step of 1e-6; the
momentum after the step over the step is the acceleration.

    t8_selfforce.py --run RUNDIR_OF_cases.py_t8 [--out DIR]

Positions in units of dx from a mesh vertex: the diagonal (s, s, s) from the vertex
(s = 0) to the cell centre (s = 1/2), the line (s, 1/2, 1/2) from a face centre to the
cell centre, the edge (s, 0, 0).  Cases: isolated domain with the multigrid solver and
cloud-in-cell deposit with the Catmull-Rom gather (iso_cic), the same with the cubic
cloud and the cubic-spline gather (iso_pcs), periodic box with the Fourier solver and
cloud-in-cell (per_cic).  Force in units of G m/dx^2, its radial component along the
line counted positive away from the vertex.  Writes DIR/t8_selfforce.json and
DIR/t8_selfforce.{png,pdf}.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    rec = json.load(open(os.path.join(a.run, "cases.json")))
    dx = rec["t8_dx"]
    pts = rec["t8_points"]
    res = {"dx": dx, "unit": "G m / dx^2"}
    data = {}
    for kind in ("iso_cic", "iso_pcs", "per_cic"):
        rows = []
        for p in pts:
            d = os.path.join(a.run, "%s_%s" % (kind, p["name"]))
            snaps = sorted(glob.glob(os.path.join(d, "*.part.*.bin")))
            if len(snaps) < 2:
                rows.append(None)
                continue
            t, cyc, x, u, m, tag = nw.read_snapshot(snaps[-1])
            g = u[0]/t*dx*dx
            rows.append(dict(name=p["name"], offset=p["offset"], g=g.tolist()))
        data[kind] = rows
        res[kind] = rows
    summary = {}
    for kind, rows in data.items():
        dg = [(r["offset"][0], r["g"]) for r in rows if r and r["name"].startswith("d")]
        s = np.array([q[0] for q in dg])
        g = np.array([q[1] for q in dg])
        gr = g.sum(axis=1)/np.sqrt(3.0)        # along (1,1,1)/sqrt 3, away from the vertex
        r = s*np.sqrt(3.0)                      # distance from the vertex in dx
        xl = [(q["offset"][0], q["g"]) for q in rows if q and q["name"].startswith("x")]
        sx = np.array([q[0] for q in xl])
        gx = np.array([q[1][0] for q in xl])
        ed = [(q["offset"][0], q["g"]) for q in rows if q and q["name"].startswith("e")]
        se = np.array([q[0] for q in ed])
        ge = np.array([q[1][0] for q in ed])
        summary[kind] = dict(
            at_vertex=float(np.abs(g[0]).max()), at_centre=float(np.abs(g[-1]).max()),
            slope_at_vertex_diag=float(gr[1]/r[1]),          # d g_r / d r, units G m/dx^3
            slope_at_vertex_edge=float(ge[0]/se[0]) if len(se) else None,
            slope_at_centre_diag=float((gr[-1] - gr[-2])/(r[-1] - r[-2])),
            slope_at_centre_x=float((0.0 - gx[-1])/(0.5 - sx[-1])) if len(sx) else None,
            max_radial_diag=float(np.abs(gr).max()), max_edge=float(np.abs(ge).max()),
            max_component=float(max(np.abs(np.array(q["g"])).max() for q in rows if q)),
            efold_vertex_diag=float(1.0/np.sqrt(gr[1]/r[1])) if gr[1] > 0 else None,
            efold_vertex_edge=float(1.0/np.sqrt(ge[0]/se[0])) if len(se) and ge[0] > 0 else None,
            period_centre_x=float(2.0*np.pi/np.sqrt(-(0.0 - gx[-1])/(0.5 - sx[-1])))
            if len(sx) and gx[-1] > 0 else None)
        data[kind] = (s, gr, sx, gx, se, ge)
    res["summary"] = summary
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
    cols = {"iso_cic": fs.PAL["red"], "iso_pcs": fs.PAL["green"], "per_cic": fs.PAL["blue"]}
    labs = {"iso_cic": "isolated, CIC + Catmull-Rom", "iso_pcs": "isolated, PCS + spline",
            "per_cic": "periodic Fourier, CIC"}
    for kind in ("iso_cic", "iso_pcs", "per_cic"):
        s, gr, sx, gx, se, ge = data[kind]
        ls = "--" if kind == "per_cic" else "-"
        axs[0].plot(s, gr, "o", ls=ls, ms=3, color=cols[kind], label=labs[kind])
        axs[1].plot(se, ge, "o", ls=ls, ms=3, color=cols[kind])
        axs[2].plot(sx, gx, "o", ls=ls, ms=3, color=cols[kind])
    for ax, lab in zip(axs, (r"$s$: position $(s,s,s)\,dx$", r"$s$: position $(s,0,0)\,dx$",
                             r"$s$: position $(s,\frac{1}{2},\frac{1}{2})\,dx$")):
        ax.axhline(0.0, color="k", lw=1.0, ls="--")
        ax.set_xlabel(lab, labelpad=-1)
    axs[0].set_ylabel(r"self-force along the line $[G m/dx^2]$")
    axs[0].legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "t8_selfforce"))
    with open(os.path.join(a.out, "t8_selfforce.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
