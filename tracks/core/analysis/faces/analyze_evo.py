#!/usr/bin/env python3
"""Evolution tests of the package faces: constraint residuals by region against time,
and the difference to a reference run whose faces are twice as far away.

    analyze_evo.py --family ball|punc|boost --case name=dir [--case ...] [--ref dir]
                   --out results/x.json --fig figs/x

Regions (flib.region_stats): inner r0 <= r < 8 (r0 = 0 for the ball, 5 for the puncture
families, whose own truncation error sits further in), shell 8 <= r < 12, faces (cells
within 4 of a face of the box of half-width 16), all (r >= r0).  The reference run is
evaluated on the same regions of the inner box (L = 16 is passed explicitly).

With --ref: for every case and dump time the difference of Khat, Theta and H to the
reference on the shared blocks, its mean over the regions, its profile along the line
nearest the x axis (space-time diagram) and its value in the boundary cell at the
centre of the +x face.
"""

import argparse
import json
import os

import numpy as np

import flib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

LBOX = 16.0


def stats_history(rundir, r0):
    rows = []
    zdumps = {round(flib.Dump(q).time, 6): q for q in flib.dumps(rundir, "z4c")}
    for p in flib.dumps(rundir, "con"):
        d = flib.Dump(p)
        if rows and abs(d.time - rows[-1]["time"]) < 1e-9:
            continue
        x, y, z, dv, v = d.flat("con_H")
        _, _, _, _, mx = d.flat("con_Mx")
        _, _, _, _, my = d.flat("con_My")
        _, _, _, _, mz = d.flat("con_Mz")
        mm = np.sqrt(mx * mx + my * my + mz * mz)
        # Gamma constraint: con_Z = (1/4) gt_ij (Gam - Gam(gt))^i (Gam - Gam(gt))^j
        _, _, _, _, zz = d.flat("con_Z")
        gz = 2.0 * np.sqrt(np.maximum(zz, 0.0))
        tq = zdumps.get(round(d.time, 6))
        th = np.abs(flib.Dump(tq).flat("z4c_Theta")[4]) if tq else np.full(v.shape, np.nan)
        r = np.sqrt(x * x + y * y + z * z)
        dface = LBOX - np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
        inbox = dface > 0
        reg = {"inner": inbox & (r >= r0) & (r < 8.0),
               "shell": inbox & (r >= 8.0) & (r < 12.0),
               "faces": inbox & (dface < 4.0),
               "all": inbox & (r >= r0)}
        row = {"time": d.time}
        for name, m in reg.items():
            w = dv[m]
            row[f"H.{name}.mean"] = float(np.sum(w * np.abs(v[m])) / np.sum(w))
            row[f"H.{name}.max"] = float(np.abs(v[m]).max())
            row[f"M.{name}.mean"] = float(np.sum(w * mm[m]) / np.sum(w))
            row[f"M.{name}.max"] = float(mm[m].max())
            row[f"G.{name}.mean"] = float(np.sum(w * gz[m]) / np.sum(w))
            row[f"T.{name}.mean"] = float(np.sum(w * th[m]) / np.sum(w))
        rows.append(row)
    return {k: [q[k] for q in rows] for k in rows[0]} if rows else {}


def diff_history(rundir, refdir, r0):
    out = {"time": [], "line_x": None, "line": {}, "face_cell": {}, "mean": {}}
    fields = (("z4c", "z4c_Khat"), ("z4c", "z4c_Theta"), ("z4c", "z4c_Axx"),
              ("z4c", "z4c_alpha"), ("con", "con_H"))
    ref = {}
    for dv_, _ in fields:
        if dv_ not in ref:
            ref[dv_] = {round(flib.Dump(p).time, 6): p for p in flib.dumps(refdir, dv_)}
    for p in flib.dumps(rundir, "z4c"):
        d = flib.Dump(p)
        t = round(d.time, 6)
        if t not in ref["z4c"] or (out["time"] and abs(t - out["time"][-1]) < 1e-9):
            continue
        pc = [q for q in flib.dumps(rundir, "con") if abs(flib.Dump(q).time - t) < 1e-9]
        if not pc or t not in ref["con"]:
            continue
        dd = {"z4c": d, "con": flib.Dump(pc[0])}
        rr = {"z4c": flib.Dump(ref["z4c"][t]), "con": flib.Dump(ref["con"][t])}
        out["time"].append(t)
        for dv_, var in fields:
            x, y, z, vol, va, vb = flib.difference(dd[dv_], rr[dv_], var)
            dif = va - vb
            r = np.sqrt(x * x + y * y + z * z)
            dface = LBOX - np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
            for name, m in (("inner", (r >= r0) & (r < 8.0)),
                            ("shell", (r >= 8.0) & (r < 12.0)),
                            ("faces", dface < 4.0)):
                out["mean"].setdefault(f"{var}.{name}", []).append(
                    float(np.sum(vol[m] * np.abs(dif[m])) / np.sum(vol[m])))
            # line nearest the +x axis (root cells: smallest positive y, z)
            h = vol ** (1.0 / 3.0)
            m = (np.abs(y - 0.5 * h) < 1e-9) & (np.abs(z - 0.5 * h) < 1e-9) & (x > 0)
            o = np.argsort(x[m])
            if out["line_x"] is None:
                out["line_x"] = [float(q) for q in x[m][o]]
            out["line"].setdefault(var, []).append([float(q) for q in dif[m][o]])
            out["line"].setdefault(var + "_run", []).append([float(q) for q in va[m][o]])
            out["face_cell"].setdefault(var, []).append(float(dif[m][o][-1]))
            out["face_cell"].setdefault(var + "_ref", []).append(float(vb[m][o][-1]))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True, choices=["ball", "punc", "boost"])
    p.add_argument("--case", action="append", default=[])
    p.add_argument("--ref", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--fig", required=True)
    p.add_argument("--title", default="")
    a = p.parse_args()
    r0 = 0.0 if a.family == "ball" else 5.0
    res = {"family": a.family, "r0": r0, "cases": {}, "diff": {}}
    for c in a.case:
        name, d = c.split("=", 1)
        res["cases"][name] = stats_history(d, r0)
        if a.ref:
            res["diff"][name] = diff_history(d, a.ref, r0)
    if a.ref:
        res["cases"]["reference"] = stats_history(a.ref, r0)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f)

    fs.use_style()
    names = list(res["cases"].keys())
    cols = {n: c for n, c in zip([n for n in names if n != "reference"],
                                 [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"],
                                  fs.PAL["orange"], "purple", "brown", "grey"])}
    cols["reference"] = fs.PAL["blue"]
    # figure 1: residual histories by region
    fig, axs = plt.subplots(4, 4, figsize=(fs.FULL_WIDTH, 8.0), sharex=True)
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.055, top=0.95, wspace=0.33,
                        hspace=0.08)
    for j, reg in enumerate(("inner", "shell", "faces", "all")):
        for i, q in enumerate(("H", "M", "T", "G")):
            ax = axs[i, j]
            for n in names:
                h = res["cases"][n]
                if not h:
                    continue
                ax.semilogy(h["time"], np.maximum(h[f"{q}.{reg}.mean"], 1e-20),
                            color=cols[n], label=n,
                            ls="--" if n == "reference" else "-")
            if i == 0:
                ax.set_title({"inner": rf"${r0:g} \leq r < 8$", "shell": r"$8 \leq r < 12$",
                              "faces": "within 4 of a face",
                              "all": rf"whole box, $r \geq {r0:g}$"}[reg], fontsize=10)
            if i == 3:
                ax.set_xlabel(r"$t$", labelpad=-2)
            if j == 0:
                ax.set_ylabel({"H": r"mean $|H|$", "M": r"mean $|M_i|$",
                               "T": r"mean $|\Theta|$",
                               "G": r"mean $|\tilde\Gamma-\tilde\Gamma(\tilde\gamma)|$"}[q])
    axs[0, 0].legend(fontsize=7, ncol=1)
    if a.title:
        fig.suptitle(a.title, fontsize=10, y=0.995)
    fs.save(fig, a.fig + "_regions")
    plt.close(fig)

    # figure 2: space-time diagram of the difference to the reference
    if a.ref and res["diff"]:
        first = [n for n in names if n != "reference"][0]
        dh = res["diff"][first]
        if dh["time"]:
            t = np.array(dh["time"])
            x = np.array(dh["line_x"])
            fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
            fig.subplots_adjust(left=0.07, right=0.93, bottom=0.14, top=0.9, wspace=0.05)
            for ax, var, lab in zip(axs, ("z4c_Khat", "con_H", "z4c_Theta"),
                                    (r"$\hat K$", r"$H$", r"$\Theta$")):
                arr = np.abs(np.array(dh["line"][var]))
                arr = np.maximum(arr, 1e-16)
                im = ax.pcolormesh(x, t, np.log10(arr), shading="nearest",
                                   cmap=fs.CMAP["dens"], vmin=-10, vmax=-2,
                                   rasterized=True)
                tt = np.linspace(0, t.max(), 50)
                ax.plot(LBOX - np.sqrt(2.0) * tt, tt, "w--", lw=1.0)
                ax.plot(LBOX - tt, tt, "w-", lw=1.0)
                ax.set_xlim(0, LBOX)
                ax.set_ylim(0, t.max())
                ax.set_xlabel(r"$x$", labelpad=-2)
                ax.set_title(rf"$\log_{{10}}|\Delta$" + lab + r"$|$, " + first, fontsize=10)
            axs[0].set_ylabel(r"$t$")
            cax = fig.add_axes([0.94, 0.14, 0.012, 0.76])
            fig.colorbar(im, cax=cax)
            fs.save(fig, a.fig + "_spacetime")
            plt.close(fig)

    # short text summary
    for n in names:
        h = res["cases"][n]
        if not h:
            continue
        t = np.array(h["time"])
        line = [n]
        for tq in (1.0, 2.0, 4.0, 8.0, t.max()):
            k = int(np.argmin(np.abs(t - tq)))
            line.append("t=%g: in %.2e sh %.2e fa %.2e all %.2e | M fa %.2e all %.2e"
                        " | Th sh %.2e fa %.2e | G sh %.2e fa %.2e" % (
                t[k], h["H.inner.mean"][k], h["H.shell.mean"][k], h["H.faces.mean"][k],
                h["H.all.mean"][k], h["M.faces.mean"][k], h["M.all.mean"][k],
                h["T.shell.mean"][k], h["T.faces.mean"][k], h["G.shell.mean"][k],
                h["G.faces.mean"][k]))
        print("\n  ".join(line))
    for n, dh in res["diff"].items():
        if not dh["time"]:
            continue
        print("diff", n, "t", dh["time"])
        for var in ("z4c_Khat", "z4c_Axx", "z4c_Theta", "con_H"):
            print("  face cell d", var, ["%.3e" % q for q in dh["face_cell"][var]])
            print("  ref value  ", var, ["%.3e" % q for q in dh["face_cell"][var + "_ref"]])
            for reg in ("inner", "shell", "faces"):
                print("  mean |d|", var, reg, ["%.2e" % q for q in dh["mean"][f"{var}.{reg}"]])


if __name__ == "__main__":
    main()
