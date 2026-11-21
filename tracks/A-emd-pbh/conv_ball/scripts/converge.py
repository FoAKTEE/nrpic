#!/usr/bin/env python3
"""Convergence summary of the G2 series of the package conv_ball (Track A, wave 3): reads the
<label>_numbers.json that compare.py wrote for every member and tabulates, per leg, the errors
against the exact solution named in DESIGN.md section 4, the apparent orders and the
comparison with the source paper's Oppenheimer-Snyder level; one figure.

Quantities per member (definitions in DESIGN.md section 4; all from compare.py):
  ddet   first detection: proper time of the tracked particles at the finder's mean
         coordinate radius, minus the exact trapping time of the shell there
         (finder.first.tau_at_horizon - finder.first.tau_ah_exact_shell_at_r)
  dtrap  mean of tau_AH(num) - tau_AH(exact) per tracked particle of the band just inside
         the core edge (events.<band>.trapping.dtau_mean; band R2.603)
  dta    mean core turnaround error (events.core.turnaround.dtau_mean; parabola vertex), M
  dtaC   the same with the cycloid fit over the whole record (estimator C of
         runs_ball/JOURNAL.md entry 13; turnaround.py, --turnaround)
  dRmax  mean relative core R_max error (events.core.turnaround.dRmax_rel_mean)
  eta    core |R/R_exact - 1| largest at the turnaround proper time (eps_groups.core)
  dm1    finder irreducible mass against the exact horizon mass of the same slice, at first
         detection (finder.m_irr_rel_err_vs_m_exact_slice.first)
  dmmed  the same, median over all detections
  tfirst code time of the first detection

    converge.py --member NAME:LEG:X:<numbers.json> [...] --out DIR
LEG is mesh (one particle per cell), meshN (fixed particle number), N / NB (particles per
cell on mesh A / B), R / RB (ball radius factor lam on A / B) or L / LB (outer boundary in M on
A / B); X is the leg's abscissa. A member may sit in several legs (repeat it).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C            # noqa: E402

BAND = "R2.603"
OS_LEVEL = 1e-3           # main.tex:945, fiducial OS run, Delta M / M_ADM <~ 1e-3
OS_RMS = (2.061e-3, 9.362e-4, 7.347e-4)   # main.tex:1484, AMR particle sequence A1-A3


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return float("nan")
        d = d[k]
    return float(d)


def quantities(res, ex_core_tau_ta):
    q = {}
    f = res.get("finder", {}).get("first") or {}
    q["tfirst"] = get(f, "t")
    q["ddet"] = get(f, "tau_at_horizon") - get(f, "tau_ah_exact_shell_at_r")
    q["dm1"] = get(res, "finder", "m_irr_rel_err_vs_m_exact_slice", "first")
    q["dmmed"] = get(res, "finder", "m_irr_rel_err_vs_m_exact_slice", "median")
    q["nfind"] = get(res, "finder", "n")
    ev = res.get("events", {})
    q["dtrap"] = get(ev, BAND, "trapping", "dtau_mean")
    q["dta"] = get(ev, "core", "turnaround", "dtau_mean")
    q["dRmax"] = get(ev, "core", "turnaround", "dRmax_rel_mean")
    key = next((k for k in res.get("eps_groups", {}).get("core", {}) if k.startswith("eps_tau")
                and abs(float(k[7:]) - ex_core_tau_ta) < 2e-3), None)
    q["eta"] = get(res, "eps_groups", "core", key, "maxabs") if key else float("nan")
    q["t_end"] = get(res, "history", "t_end")
    q["first_trapped_slice"] = get(res, "first_trapped_slice", "t_code")
    return q


def orders(xs, es):
    """apparent orders between neighbours (xs decreasing resolution parameter)"""
    out = []
    for i in range(len(xs) - 1):
        a, b = abs(es[i]), abs(es[i + 1])
        if a > 0 and b > 0 and math.isfinite(a) and math.isfinite(b):
            out.append(math.log(a / b) / math.log(xs[i] / xs[i + 1]))
        else:
            out.append(float("nan"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--member", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--turnaround", action="append", default=[],
                    help="turnaround.json of turnaround.py (estimator C: cycloid fit over the whole record)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tac = {}
    for p in a.turnaround:
        for r in C.load_json(p).get("runs", []):
            st = r.get("stats", {}).get("C")
            if st:
                tac[r["label"]] = (st["dtau_mean"], st.get("dRmax_rel_mean", float("nan")))
    rows = []
    for spec in a.member:
        name, leg, x, path = spec.split(":", 3)
        res = C.load_json(path)
        ex = C.load_json(os.path.join(res["prep"], "exact.json"))
        q = quantities(res, float(ex["core"]["tau_ta"]))
        q["dtaC"], q["dRmaxC"] = tac.get(name, (float("nan"), float("nan")))
        rows.append(dict(name=name, leg=leg, x=float(x), numbers=path, **q))
    keys = ("ddet", "dtrap", "dta", "dtaC", "dRmax", "dRmaxC", "eta", "dm1", "dmmed")
    summary = dict(members=rows, legs={})
    lines = ["| member | leg | x | first detection t | ddet (M) | dtrap (M) | dta V3 (M) | dta C (M) | dRmax | eta | dm1 | dm median | finds |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['leg']} | {r['x']:g} | {r['tfirst']:.3f} | {r['ddet']:+.4f} | {r['dtrap']:+.4f} | "
                     f"{r['dta']:+.4f} | {r['dtaC']:+.4f} | {r['dRmax']:+.2e} | {r['eta']:.2e} | {r['dm1']:+.2e} | {r['dmmed']:+.2e} | {r['nfind']:g} |")
    for leg in ("mesh", "meshN", "N", "NB", "R", "RB", "L", "LB"):
        ismesh = leg.startswith("mesh")
        lr = sorted([r for r in rows if r["leg"] == leg], key=lambda r: -r["x"] if ismesh else r["x"])
        if len(lr) < 2:
            continue
        xs = [r["x"] for r in lr]
        d = dict(members=[r["name"] for r in lr], x=xs)
        for k in keys:
            es = [r[k] for r in lr]
            d[k] = dict(values=es, orders=orders(xs, es) if ismesh else None,
                        spread=float(np.nanmax(es) - np.nanmin(es)) if np.any(np.isfinite(es)) else None)
            if ismesh and len(es) >= 3 and all(math.isfinite(v) for v in es[:3]):
                d1, d2 = es[0] - es[1], es[1] - es[2]
                d[k]["self_order"] = (math.log(abs(d1 / d2)) / math.log(2.0)) if d1 != 0 and d2 != 0 else None
        summary["legs"][leg] = d
        lines.append("")
        lines.append(f"leg {leg}: " + ", ".join(f"{r['name']} (x = {r['x']:g})" for r in lr))
        for k in keys:
            s = d[k]
            o = s.get("orders")
            lines.append(f"  {k}: " + ", ".join(f"{v:+.3e}" for v in s["values"])
                         + (("  orders " + ", ".join(f"{v:.2f}" for v in o)) if o else "")
                         + (f"  self-order {s['self_order']:.2f}" if s.get("self_order") is not None else "")
                         + (f"  spread {s['spread']:.2e}" if s.get("spread") is not None and not ismesh else ""))
    lines.append("")
    lines.append(f"source paper OS level: Delta M/M_ADM <~ {OS_LEVEL:g} (main.tex:945); RMS of A1-A3 "
                 f"{', '.join(f'{v:.3e}' for v in OS_RMS)} (main.tex:1484)")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(a.out, "convergence.md"), "w") as f:
        f.write(txt + "\n")
    C.write_json(os.path.join(a.out, "convergence.json"), summary)

    # ---------------------------------------------------------------- figure
    sys.path.insert(0, os.path.join(C.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(11.0, 5.6))
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.10, top=0.92, wspace=0.34, hspace=0.45)
    labels = dict(ddet="first detection", dtrap="trapping (band 2.603)", dta="core turnaround (V3)",
                  dtaC="core turnaround (cycloid C)", dRmaxC="core $R_{max}$ (C)",
                  dRmax="core $R_{max}$ (rel.)", eta="core |eps| at turnaround", dm1="mass, first detection",
                  dmmed="mass, median")
    groups = [("ddet", "dtrap", "dta", "dtaC"), ("dm1", "dmmed", "eta", "dRmax")]
    ylabels = ["|time error| (M)", "|relative error|"]
    cols = dict(zip(keys, fs.series_colors(len(keys), "viridis") if hasattr(fs, "series_colors") else [None] * len(keys)))
    families = [(("mesh", "meshN"), "finest cell $h_f/M$", True), (("N", "NB"), "particles per finest cell", True),
                (("R", "RB"), r"ball radius factor $\lambda$", False), (("L", "LB"), "outer boundary $/M$", True)]
    for gi, grp in enumerate(groups):
        for fi, (legs, xl, logx) in enumerate(families):
            ax = fig.add_subplot(2, 4, 4 * gi + fi + 1)
            xt = set()
            for li, leg in enumerate(legs):
                lr = sorted([r for r in rows if r["leg"] == leg], key=lambda r: r["x"])
                if not lr:
                    continue
                xs = np.array([r["x"] for r in lr])
                xt.update(xs.tolist())
                for k in grp:
                    ys = np.abs([r[k] for r in lr])
                    if np.any(np.isfinite(ys) & (ys > 0)):
                        ax.plot(xs, ys, "o-" if li == 0 else "s--", color=cols[k], lw=1.2, ms=4,
                                label=(labels[k] if li == 0 else None))
                if leg == "mesh":
                    x0 = xs.max()
                    y0 = 3e-2 if gi == 1 else 0.3
                    for pw, ls in ((1, ":"), (2, "-.")):
                        ax.plot(xs, y0 * (xs / x0) ** pw, color="0.5", lw=0.8, ls=ls)
            if gi == 1 and fi == 0:
                ax.axhline(OS_LEVEL, **fs.GUIDE)
            if not xt:
                ax.text(0.5, 0.5, "no member analysed yet", ha="center", va="center", transform=ax.transAxes,
                        fontsize=8, color="0.4")
                ax.set_xticks([])
                ax.set_yticks([])
            if xt:
                if logx:
                    ax.set_xscale("log", base=2)
                ax.set_yscale("log")
                xs_ = sorted(xt)
                ax.set_xticks(xs_)
                ax.set_xticklabels([f"{v:g}" for v in xs_], fontsize=7)
            ax.set_xlabel(xl, fontsize=8)
            if fi == 0:
                ax.set_ylabel(ylabels[gi])
                ax.legend(fontsize=6, loc="lower right")
            ttl = {0: "mesh (solid: one per cell; dashed: fixed N)", 1: "particles (solid: mesh A; dashed: B)",
                   2: "ball radius (solid: A; dashed: B)", 3: "outer boundary (solid: A; dashed: B)"}[fi]
            if gi == 0:
                ax.set_title(ttl, fontsize=7.5)
    fig.text(0.5, 0.965, "grey: slopes 1 (dotted) and 2 (dash-dot); dashed horizontal: source OS level 1e-3",
             ha="center", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_convergence"))


if __name__ == "__main__":
    main()
