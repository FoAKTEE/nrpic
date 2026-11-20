#!/usr/bin/env python3
"""Test T4d of work package newton2: the embedded ellipsoid of T4b against the cell size
and against the kernels (the track's ODE, model A, is the reference as in T4b).

    t4d_convergence.py --prep PREP --case LABEL:N:SERIES:DIR [--case ...] [--out DIR]

PREP: run directory of `cases.py card2` (ic/embedded_setup.json, refs/ with the track's
ellipsoid.py).  One --case per run: a label, the number of cells per side, the series it
belongs to (cic_sp: linear cloud, spectral symbol; cic_7p: linear cloud, seven-point
operator, multigrid or Fourier; pcs_sp: cubic cloud with compensation and spline gather,
spectral symbol) and the directory that holds newton.newton.g1.hst.
For every run: time of the first minimum of the short axis (5 J_xx/M)^(1/2) against the
ODE crossing, largest |axis - ODE|/R_L up to one t_k before the crossing, quadrupole
energy to that time.  Per series: observed order between successive cell sizes.
Writes DIR/t4d_convergence.json and DIR/t4d_convergence.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
import t4b_embedded as t4b  # noqa: E402

SERIES = {"cic_sp": ("linear cloud, spectral", "red", "o"),
          "cic_7p": ("linear cloud, seven-point", "yellow", "s"),
          "pcs_sp": ("cubic cloud + comp., spectral", "blue", "^")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--case", action="append", default=[], metavar="LABEL:N:SERIES:DIR")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    sys.path.insert(0, os.path.join(a.prep, "refs", "B-emd-gw", "tracks", "B-emd-gw",
                                    "baseline", "scripts"))
    import ellipsoid as el
    setup = json.load(open(os.path.join(a.prep, "ic", "embedded_setup.json")))
    lam = np.array(setup["lam"])
    t0, L = setup["t_turn"], setup["L"]
    ode = t4b.ode_models(el, lam, t0)
    tx_ode = ode["A"]["crossings"][0][0]
    res = {"t_cross_ode": float(tx_ode), "t_turn": float(t0), "L": L, "cases": {},
           "missing": [], "series": {}}
    arrs = {}
    for spec in a.case:
        label, n, series, cdir = spec.split(":", 3)
        n = int(n)
        if series not in SERIES:
            sys.exit("unknown series %s" % series)
        if not os.path.exists(os.path.join(cdir, "newton.newton.g1.hst")):
            res["missing"].append(label)
            continue
        log = os.path.join(cdir, "athena.log")
        done = os.path.exists(log) and "Terminating on" in open(log, errors="replace").read()
        out, arr = t4b.case_numbers(el, ode, setup, cdir, dx=L/n)
        out.update(n=n, dx=L/n, series=series, dir=cdir, completed=bool(done),
                   t_last=float(arr["t"][-1]))
        res["cases"][label] = out
        arrs[label] = arr
    for series in SERIES:
        rows = sorted((c["n"], lab) for lab, c in res["cases"].items()
                      if c["series"] == series and c["completed"])
        tab = []
        for k, (n, lab) in enumerate(rows):
            c = res["cases"][lab]
            row = dict(label=lab, n=n, dx=c["dx"], t_min_rel=c["t_min_rel"],
                       axes_max=float(max(c["axes_maxdev_over_RL"])),
                       axes=c["axes_maxdev_over_RL"], E_rel=c["E_rel"])
            if k > 0:
                p = tab[-1]
                ratio = np.log(n/p["n"])
                if c["t_min_rel"] > 0 and p["t_min_rel"] > 0:
                    row["order_t_min"] = float(np.log(p["t_min_rel"]/c["t_min_rel"])/ratio)
                row["order_axes"] = float(np.log(p["axes_max"]/row["axes_max"])/ratio)
                row["axes_ratio_per_doubling"] = float((p["axes_max"]/row["axes_max"])
                                                       ** (np.log(2.0)/ratio))
            tab.append(row)
        res["series"][series] = tab
    by = {(c["series"], c["n"]): c for c in res["cases"].values() if c["completed"]}
    for n in (64, 128):
        if ("cic_sp", n) in by and ("cic_7p", n) in by:
            res["symbols_t_min_rel_diff_n%d" % n] = float(
                by[("cic_sp", n)]["t_min_short_axis"]/by[("cic_7p", n)]["t_min_short_axis"]
                - 1.0)
    with open(os.path.join(a.out, "t4d_convergence.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "cases"}, indent=1))
    for lab, c in res["cases"].items():
        print("%-16s n=%3d %-7s done=%s t_min=%.4f rel=%+.4f axes=%s E_rel=%+.3f LI=%.2e" % (
            lab, c["n"], c["series"], c["completed"], c["t_min_short_axis"],
            c["t_min_rel"], ["%.4f" % v for v in c["axes_maxdev_over_RL"]], c["E_rel"],
            c["layzer_irvine"]))

    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.95, wspace=0.36)
    ax = axs[0]
    for series, (name, col, mk) in SERIES.items():
        tab = res["series"][series]
        if not tab:
            continue
        dx = np.array([r["dx"] for r in tab])
        y = np.array([r["t_min_rel"] for r in tab])
        ax.loglog(dx, np.abs(y), mk + "-", color=fs.PAL[col], ms=5, label=name)
        neg = y < 0
        if neg.any():
            ax.loglog(dx[neg], np.abs(y[neg]), mk, color="w", ms=2.5)
    xg = np.array([0.17, 0.8])
    ax.loglog(xg, 0.0256*(xg/0.75)**2, color="k", lw=1.0, ls=":", label=r"$\propto dx^2$")
    ax.set_xlabel(r"cell size $dx/t_k$", labelpad=-1)
    ax.set_ylabel(r"$|t_{\min}/t_{\times,\rm ODE} - 1|$")
    ax.legend(loc="upper left", fontsize=6.5)
    ax = axs[1]
    lss = {64: "-", 96: "-.", 128: "--", 256: ":"}
    for lab, c in sorted(res["cases"].items(), key=lambda kv: kv[1]["n"]):
        arr = arrs[lab]
        w = arr["w"]
        ax.plot(arr["t"][w], (arr["R"][w, 0] - arr["ode_R"][:, 0])/el.RL,
                color=fs.PAL[SERIES[c["series"]][1]], ls=lss.get(c["n"], "-"), lw=1.2)
    for n, ls in lss.items():
        ax.plot([], [], color="0.3", ls=ls, lw=1.2, label=r"$%d^3$" % n)
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xlabel(r"$t/t_k$", labelpad=-1)
    ax.set_ylabel(r"short axis: (run $-$ ODE)$/R_L$")
    ax.legend(loc="upper left", fontsize=7)
    ax = axs[2]
    for series, (name, col, mk) in SERIES.items():
        tab = res["series"][series]
        if not tab:
            continue
        dx = np.array([r["dx"] for r in tab])
        for k, ls in enumerate(("-", "--", ":")):
            ax.loglog(dx, [r["axes"][k] for r in tab], mk + ls, color=fs.PAL[col], ms=4,
                      lw=1.2)
    for k, (ls, nm) in enumerate(zip(("-", "--", ":"), ("x", "y", "z"))):
        ax.plot([], [], color="0.3", ls=ls, lw=1.2, label="axis $%s$" % nm)
    ax.loglog(xg, 0.111*(xg/0.75)**2, color="k", lw=1.0, ls=":")
    ax.set_xlabel(r"cell size $dx/t_k$", labelpad=-1)
    ax.set_ylabel(r"max $|R_i - R_{i,\rm ODE}|/R_L$, $t \leq t_\times - 1$")
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "t4d_convergence"))


if __name__ == "__main__":
    main()
