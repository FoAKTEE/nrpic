#!/usr/bin/env python3
"""Resolution comparison of the scouting runs (package runs_ball): reads the
<label>_numbers.json and <label>_series.npz written by compare.py and draws
  - the core-shell error |R/R_exact - 1| (largest and median) against proper time,
  - the turnaround-time and largest-radius errors of the core against dx,
  - SR-1: largest |H| on the mesh against t (the instability),
  - SR-2: central lapse against the exact a(tau_c) (the lapse pulse),
for every label given as <dir>:<label>:<dx>.

    summary.py --run <dir>:sr1_n128:1.0 --run <dir>:sr1_n256:0.5 ... --out <dir> [--figdir <dir>]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--prep", required=True, help="prep dir with exact.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    a = ap.parse_args()
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    runs = []
    for spec in a.run:
        d, lab, dx = spec.split(":")
        num = C.load_json(os.path.join(d, f"{lab}_numbers.json"))
        ser = np.load(os.path.join(d, f"{lab}_series.npz"))
        runs.append(dict(lab=lab, dx=float(dx), num=num, ser=ser, gauge=num["gauge"]))
    table = []
    for r in runs:
        c = r["num"]["eps_groups"]["core"]
        ta = r["num"]["events"].get("core", {}).get("turnaround", {})
        row = dict(label=r["lab"], gauge=r["gauge"], dx=r["dx"],
                   eps_core_tau8_max=c.get("eps_tau8", {}).get("maxabs"),
                   eps_core_tau16_9_max=c.get("eps_tau16.894", {}).get("maxabs"),
                   eps_core_tau16_9_mean=c.get("eps_tau16.894", {}).get("mean"),
                   tau_ta_err_mean=ta.get("dtau_mean"), tau_ta_err_rel_mean=ta.get("rel_dtau_mean"),
                   Rmax_err_rel_mean=ta.get("dRmax_rel_mean"),
                   t_lapse_dev_gt_0p1=r["num"]["history"].get("t_lapse_dev_gt_0.1"),
                   H_max_t20=r["num"]["cstat"].get("H_max_t20"),
                   t_end=r["num"]["traj"]["t_last"])
        table.append(row)
    # orders between successive resolutions of one gauge
    orders = []
    for g in ("sr1", "sr2"):
        rr = sorted([t for t in table if t["gauge"] == g], key=lambda t: -t["dx"])
        for k in range(len(rr) - 1):
            o = dict(gauge=g, dx=[rr[k]["dx"], rr[k + 1]["dx"]])
            for key in ("eps_core_tau16_9_max", "eps_core_tau8_max", "tau_ta_err_mean", "Rmax_err_rel_mean",
                        "H_max_t20"):
                v0, v1 = rr[k][key], rr[k + 1][key]
                if v0 and v1:
                    o[key] = float(np.log(abs(v0) / abs(v1)) / np.log(rr[k]["dx"] / rr[k + 1]["dx"]))
            orders.append(o)
    os.makedirs(a.out, exist_ok=True)
    C.write_json(os.path.join(a.out, "summary.json"), dict(table=table, orders=orders))
    for t in table:
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in t.items()})
    for o in orders:
        print("order", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()})

    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    col = {1.0: fs.PAL["yellow"], 0.5: fs.PAL["red"], 0.25: fs.PAL["blue"]}
    fig = plt.figure(figsize=(8.0, 6.0))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.30, hspace=0.38)
    for j, g in enumerate(("sr1", "sr2")):
        ax = fig.add_subplot(2, 2, 1 + j)
        for r in [r for r in runs if r["gauge"] == g]:
            s = r["ser"]
            core = s["Ri"] <= 2.4
            e = np.abs(s["eps"][:, core])
            tm = np.nanmedian(s["tau"][:, core], axis=1)
            with np.errstate(invalid="ignore"):
                ax.semilogy(tm, np.nanmax(e, axis=1), color=col.get(r["dx"], "k"), lw=1.5,
                            label=fr"$\Delta x = {r['dx']:g}\,M$")
                ax.semilogy(tm, np.nanmedian(e, axis=1), color=col.get(r["dx"], "k"), lw=0.8, ls=":")
        ax.axvline(ex["core"]["tau_ta"], **fs.MASK_LINE)
        ax.set_xlabel(r"proper time $\tau\,/M$")
        ax.set_ylabel(r"core $|R/R_{\rm exact}-1|$")
        ax.set_ylim(1e-5, 1)
        ax.set_xlim(0, 46)
        ax.legend(fontsize=8, loc="upper left")
        ax.set_title(f"{g.upper().replace('SR', 'SR-')}: core shells (dotted: median)", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    for r in [r for r in runs if r["gauge"] == "sr1"]:
        cst = r["ser"]["cst"]
        ok = np.all(np.isfinite(cst[:, :10]), axis=1) & (np.abs(cst[:, 8]) < 1e30)
        ax.semilogy(cst[ok, 0], np.abs(cst[ok, 8]), color=col.get(r["dx"], "k"), lw=1.5,
                    label=fr"$\Delta x = {r['dx']:g}\,M$")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"largest $|H|$ on the mesh")
    ax.set_ylim(1e-4, 1e2)
    ax.legend(fontsize=8, loc="upper left")
    ax.set_title("SR-1: growth of the constraint violation", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    tt = np.array(ex["central"]["tau"])
    for r in [r for r in runs if r["gauge"] == "sr2"]:
        h = r["ser"]["hst"]
        ok = np.all(np.isfinite(h[:, :16]), axis=1)
        ax.plot(h[ok, 0], h[ok, 12], color=col.get(r["dx"], "k"), lw=1.5, label=fr"$\alpha_c$, $\Delta x = {r['dx']:g}\,M$")
        ax.plot(h[ok, 0], np.interp(h[ok, 14], tt, ex["central"]["a"]), color=col.get(r["dx"], "k"), lw=0.8, ls="--")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel(r"central lapse (dashed: $a(\tau_c)$)")
    ax.set_xlim(0, 40)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_title("SR-2: lapse pulse at the centre", fontsize=10)
    outs = fs.save(fig, os.path.join(a.out, "fig_resolution_summary"))
    if a.figdir:
        import shutil
        shutil.copy(outs[1], os.path.join(a.figdir, os.path.basename(outs[1])))


if __name__ == "__main__":
    main()
