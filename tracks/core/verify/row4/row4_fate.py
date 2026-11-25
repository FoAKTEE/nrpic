#!/usr/bin/env python3
"""Ladder row 4 on the M/8 mesh: fates of kicked members against their unkicked controls.

Rule fixed before the runs (tracks/core/JOURNAL.md, entry of 2026-11-21T20:26Z):
  t_c       first apparent horizon (st.horizon_summary_0.txt) or central lapse < 0.3
            (st.nrpic.hst column 13, the probe at the origin)
  D         mean alpha_c over 200-300 M of the member minus that of its control
  member    COLLAPSE (t_c <= 300 M), CONTRACTS (D < -0.02), EXPANDS (D > +0.02),
            STAYS (|D| <= 0.01), UNDECIDED (0.01 < |D| <= 0.02, or the control collapses
            and the member does not)
  model     UNSTABLE if member or control collapses or the member CONTRACTS/EXPANDS;
            STABLE if the member STAYS and its control does not collapse
  bracket   y_lo = largest UNSTABLE y_c, y_hi = smallest STABLE y_c; valid if y_lo < y_hi
            and no UNDECIDED member between them; next level: the midpoint

    python3 row4_fate.py --out DIR 0.605=<member dir>,<control dir> 0.680=... 0.755=...

A run continued from another run's restart file is given as <first dir>+<continuation dir>;
the records are joined in time (the continuation's lines replace the first run's at equal or
later times). The rule above reads only t <= 300 M; beyond it the script reports, as a
supplement, the first collapse over the whole record (t_c_all) and 50-M window means of
alpha_c / alpha_c^eq (added 2026-11-24, batch 11, for the level-3 continuations to 600 M).

A run still going is read as far as it got (its classes are then provisional and marked).
"""
import argparse
import json
import os
import sys

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

T_END, W0, W1 = 300.0, 200.0, 300.0


def read_hst(path):
    rows = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        v = line.split()
        rows[float(v[0])] = [float(x) for x in v]
    return np.array([rows[t] for t in sorted(rows)])


def first_ah(path):
    if not os.path.exists(path):
        return None
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        x = line.split()
        if x[2] != "nan":
            return float(x[1])
    return None


def run(d):
    parts = d.split("+")
    rows = {}
    for q in parts:                      # later parts (continuations) win at equal times
        h = read_hst(os.path.join(q, "st.nrpic.hst"))
        t0 = h[0, 0]
        rows = {k: v for k, v in rows.items() if k < t0}
        rows.update({r[0]: r for r in h})
    h = np.array([rows[k] for k in sorted(rows)])
    t, ac = h[:, 0], h[:, 12]
    ahs = [first_ah(os.path.join(q, "st.horizon_summary_0.txt")) for q in parts]
    t_ah_all = min([x for x in ahs if x is not None], default=None)
    low = np.nonzero(ac < 0.3)[0]
    t_low_all = float(t[low[0]]) if len(low) else None
    tc_all = min([x for x in (t_ah_all, t_low_all) if x is not None], default=None)
    # the rule reads t <= T_END only
    t_ah = t_ah_all if (t_ah_all is not None and t_ah_all <= T_END) else None
    t_low = t_low_all if (t_low_all is not None and t_low_all <= T_END) else None
    tc = min([x for x in (t_ah, t_low) if x is not None], default=None)
    late = (t >= W0) & (t <= W1)
    return dict(dir=d, t_end=float(t[-1]), t_c=tc, t_first_AH=t_ah, t_alpha_below_0p3=t_low,
                t_c_all=tc_all, t_first_AH_all=t_ah_all,
                mean_200_300=float(ac[late].mean()) if late.any() else None,
                complete=bool(t[-1] >= T_END - 1.0 or tc is not None), t=t, alpha_c=ac)


def windows(r, a0, width=50.0):
    """50-M window means of alpha_c / alpha_c^eq over the whole record (supplement)."""
    t, a = r["t"], r["alpha_c"] / a0
    out = []
    w = 0.0
    while w < t[-1] - 1e-9:
        sel = (t >= w) & (t < w + width)
        if sel.any():
            out.append([w, w + width, float(a[sel].mean()), float(a[sel].min())])
        w += width
    return out


def classify(y, m, c):
    a0 = float(stc.st_global(y)["alpha_c"])
    out = dict(yc=y, alpha_c_eq=a0, member={k: v for k, v in m.items() if k not in ("t", "alpha_c")},
               control={k: v for k, v in c.items() if k not in ("t", "alpha_c")})
    D = None
    if m["t_c"] is not None and m["t_c"] <= T_END:
        cls = "COLLAPSE"
    elif c["t_c"] is not None and c["t_c"] <= T_END:
        cls = "UNDECIDED"
    elif m["mean_200_300"] is None or c["mean_200_300"] is None:
        cls = "INCOMPLETE"
    else:
        D = m["mean_200_300"] - c["mean_200_300"]
        cls = ("CONTRACTS" if D < -0.02 else "EXPANDS" if D > 0.02 else
               "STAYS" if abs(D) <= 0.01 else "UNDECIDED")
    ctrl_coll = c["t_c"] is not None and c["t_c"] <= T_END
    if cls in ("COLLAPSE", "CONTRACTS", "EXPANDS") or ctrl_coll:
        side = "UNSTABLE"
    elif cls == "STAYS":
        side = "STABLE"
    else:
        side = cls
    out["member"]["windows_50M"] = windows(m, a0)
    out["control"]["windows_50M"] = windows(c, a0)
    out.update(D=D, member_class=cls, side=side,
               provisional=not (m["complete"] and c["complete"]),
               member_own_offset=None if m["mean_200_300"] is None else m["mean_200_300"] - a0,
               control_own_offset=None if c["mean_200_300"] is None else c["mean_200_300"] - a0)
    return out


def bracket(res):
    uns = [r["yc"] for r in res if r["side"] == "UNSTABLE"]
    sta = [r["yc"] for r in res if r["side"] == "STABLE"]
    lo, hi = (max(uns) if uns else None), (min(sta) if sta else None)
    ok = lo is not None and hi is not None and lo < hi and not any(
        r["side"] not in ("UNSTABLE", "STABLE") and lo < r["yc"] < hi for r in res)
    nonmono = any(s < u for s in sta for u in uns)
    return dict(y_lo=lo, y_hi=hi, valid=bool(ok), non_monotone=bool(nonmono),
                next_midpoint=0.5 * (lo + hi) if ok else None)


def figure(res, runs, out):
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    # one colour per model, ordered by y_c (sequential map; the old five-colour cycle
    # repeated colours from the sixth model on)
    cmap = plt.get_cmap("plasma")
    cols = [cmap(0.05 + 0.8 * i / max(1, len(res) - 1)) for i in range(len(res))]
    tmax = max(max(runs[r["yc"]][0]["t"][-1], runs[r["yc"]][1]["t"][-1]) for r in res)
    for i, r in enumerate(res):
        m, c = runs[r["yc"]]
        col = cols[i]
        ax[0].plot(m["t"], m["alpha_c"] / r["alpha_c_eq"], color=col, lw=1.0,
                   label=fr"$y_c={r['yc']:g}$ kick")
        ax[0].plot(c["t"], c["alpha_c"] / r["alpha_c_eq"], color=col, lw=1.0, ls="--",
                   label=fr"$y_c={r['yc']:g}$ control")
        sel = m["t"] <= c["t"][-1]
        dt = np.interp(m["t"][sel], c["t"], c["alpha_c"])
        ax[1].plot(m["t"][sel], m["alpha_c"][sel] - dt, color=col, lw=1.0,
                   label=fr"$y_c={r['yc']:g}$: {r['member_class']}")
    if tmax > T_END + 1.0:
        ax[0].axvline(T_END, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel(r"$\alpha_c/\alpha_c^{\rm eq}$")
    ax[0].set_title("(a) central lapse, member and control")
    ax[0].legend(fontsize=6, ncol=2)
    for v in (-0.02, -0.01, 0.01, 0.02):
        ax[1].axhline(v, color="0.6", lw=0.6, ls=":")
    ax[1].axvspan(W0, W1, color="0.9", zorder=0)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel(r"$\alpha_c^{\rm kick}-\alpha_c^{\rm control}$")
    ax[1].set_title("(b) member minus control; D: mean over 200-300 M")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig_row4_m8.{ext}"), dpi=150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("pairs", nargs="+", help="y_c=<member dir>,<control dir>")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, runs = [], {}
    for p in a.pairs:
        y, dirs = p.split("=")
        md, cd = dirs.split(",")
        y = float(y)
        runs[y] = (run(md), run(cd))
        res.append(classify(y, *runs[y]))
    res.sort(key=lambda r: r["yc"])
    br = bracket(res)
    json.dump(dict(rule="tracks/core/JOURNAL.md 2026-11-21T20:26Z", models=res, bracket=br),
              open(os.path.join(a.out, "row4_fate.json"), "w"), indent=1, default=float)
    for r in res:
        print(f"y_c={r['yc']:.3f} member {r['member_class']:10s} side {r['side']:9s} "
              f"D={r['D']} t_c(member)={r['member']['t_c']} t_c(control)={r['control']['t_c']} "
              f"t_end {r['member']['t_end']:.1f}/{r['control']['t_end']:.1f}"
              + (" PROVISIONAL" if r["provisional"] else "")
              + (f" | whole record: t_c_all member {r['member']['t_c_all']} control "
                 f"{r['control']['t_c_all']}" if max(r['member']['t_end'], r['control']['t_end']) > T_END + 1.0
                 else ""))
    print("bracket", json.dumps(br))
    figure(res, runs, a.out)


if __name__ == "__main__":
    main()
