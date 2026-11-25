#!/usr/bin/env python3
"""A2 control (periodic_threshold JOURNAL 2026-11-25 08:10 PST): S1L (GR) against the Newtonian members on one
clock. Reads the a2.json of each (a2_crossing.py), tabulates the smallest neighbour separation along z at the GR
snapshot times (t/t_H, linear interpolation in log t/t_H for the Newtonian members) and the first crossings, and
draws min Delta_z/h against t/t_H with the Zel'dovich line of the first axis.

    a2_compare.py --gr a2.json --member NAME=a2.json [...] --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gr", required=True)
    ap.add_argument("--member", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = {"S1L (GR)": json.load(open(a.gr))}
    for m in a.member:
        n, p = m.split("=", 1)
        runs[n] = json.load(open(p))
    gr = runs["S1L (GR)"]["rows"]
    tg = np.array([r["t_over_tH"] for r in gr])
    lam = 1.0 - gr[0]["min_z"]
    table = []
    for i, t in enumerate(tg):
        row = dict(t_over_tH=float(t), zeldovich=float(1.0 - lam * 6.0 * t ** (2.0 / 3.0)))
        for n, r in runs.items():
            tt = np.array([x["t_over_tH"] for x in r["rows"]])
            mz = np.array([x["min_z"] for x in r["rows"]])
            row[n] = float(np.interp(np.log(t), np.log(tt), mz)) if tt[0] <= t <= tt[-1] else None
        table.append(row)
    first = {n: {ax: (r["first_crossing"].get(ax) or {}).get("t_over_tH_interp") for ax in "xyz"} for n, r in runs.items()}
    bracket = {n: {ax: (r["first_crossing"].get(ax) or {}).get("bracket_t_over_tH") for ax in "xyz"} for n, r in runs.items()}
    res = dict(lambda_z_at_a1=lam, zeldovich_a_sc=1.0 / lam, zeldovich_t_sc_over_tH=float((1.0 / lam / 6.0) ** 1.5),
               table=table, first_crossing=first, bracket=bracket)
    json.dump(res, open(os.path.join(a.out, "a2_compare.json"), "w"), indent=1)
    print(json.dumps(dict(first=first, zeldovich_t_sc_over_tH=res["zeldovich_t_sc_over_tH"]), indent=1))
    hdr = "t/t_H   Zeldovich  " + "  ".join(f"{n:>18s}" for n in runs)
    print(hdr)
    for row in table:
        print(f"{row['t_over_tH']:6.3f}  {row['zeldovich']:+9.3f}  " + "  ".join(
            f"{row[n]:+18.3f}" if row[n] is not None else f"{'-':>18s}" for n in runs))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, HERE)
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(3.6, 2.9))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.9)
    cols = ["0.1", fs.PAL["red"], fs.PAL["blue"], fs.PAL["yellow"]]
    mk = ["s", "o", "^", "v"]
    for k, (n, r) in enumerate(runs.items()):
        ax.plot([x["t_over_tH"] for x in r["rows"]], [x["min_z"] for x in r["rows"]], marker=mk[k % 4],
                ms=2.5 if k == 0 else 1.5, lw=0.8, color=cols[k % 4], label=n)
    tz = np.geomspace(0.06, 20, 200)
    ax.plot(tz, 1.0 - lam * 6.0 * tz ** (2.0 / 3.0), ls=":", color="0.4", lw=0.9, label="Zel'dovich ($1-\\lambda_z a$)")
    ax.axhline(0, color="0.5", lw=0.6)
    ax.axvspan(3.4, 5.0, color="0.88", zorder=0, label="A2 band")
    ax.set_xscale("log")
    ax.set_ylim(-0.4, 1.05)
    ax.set_xlabel(r"$t/t_H$")
    ax.set_ylabel(r"min $\Delta_z/h$")
    ax.set_title("A2: first axis, GR and Newtonian control", fontsize=8)
    ax.legend(fontsize=5.5, loc="lower left")
    fig.savefig(os.path.join(a.out, "fig_a2_compare.png"), dpi=150)
    fig.savefig(os.path.join(a.out, "fig_a2_compare.pdf"))


if __name__ == "__main__":
    main()
