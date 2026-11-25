#!/usr/bin/env python3
"""Entry 13 of threshold_ball (C3S, the smoothed-edge test): constraint ratio of SCOPE section 3 on the x line,
||H||/||16 pi E|| (weights x^2 dx, x > 0; no horizon exists before t = 5 in any member), and the volume L2 norms
of H and M (ball.z4c.user.hst) of the smoothed members S1, S2 against the top-hat members of data set 3.

    python -I edge_compare.py --run <edge_runs dir> --out DIR

Top-hat references: K4-ref (A-20261125-120525-8fb946e/K4-ref; mesh A, the same processor build) and conv_ball's
card members A and B (A-20261121-075926-d10c2c1/A, /B). Writes edge.json and fig_edge.png.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from constraint_conv import load  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
REFS = {"tophat A (K4-ref)": S + "/A-20261125-120525-8fb946e/K4-ref",
        "tophat A (card)": S + "/A-20261121-075926-d10c2c1/A",
        "tophat B (card)": S + "/A-20261121-075926-d10c2c1/B"}
TIMES = (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0)


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def line_ratio(rd):
    out = []
    for f in sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab"))):
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        _, m = read_tab(g)
        x = c["x1v"]
        o = np.argsort(x)
        x, H, E = x[o], c["con_H"][o], m["tmunu_E"][o]
        pos = x > 0
        x, H, E = x[pos], H[pos], E[pos]
        w = x ** 2 * np.gradient(x)
        num = math.sqrt(np.nansum(w * H ** 2))
        den = math.sqrt(np.nansum(w * (16 * math.pi * E) ** 2))
        out.append(dict(t=t, ratio=num / den if den > 0 else float("nan"), file=os.path.basename(f), x=x, H=H, E=E))
    # repeated times (restarts): keep the last
    by_t = {}
    for r in out:
        by_t[round(r["t"], 6)] = r
    return [by_t[k] for k in sorted(by_t)]


def vol(rd):
    p = os.path.join(rd, "ball.z4c.user.hst")
    if not os.path.isfile(p):
        return None
    cz, z = load(p)
    return dict(t=z[:, 0], H=z[:, cz.index("H-norm2")], M=z[:, cz.index("M-norm2")])


def at(v, key, t):
    if v is None or len(v["t"]) == 0 or t > v["t"][-1] + 1e-9:
        return None
    return float(np.interp(t, v["t"], v[key]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mem = {}
    for name in ("S1-A0", "S2-A0", "S1-B0", "S2-B0", "S1-A", "S2-A", "S2-B"):
        rd = os.path.join(a.run, name)
        if os.path.isdir(os.path.join(rd, "tab")):
            mem[name] = rd
    mem.update(REFS)
    res = {}
    lines = {}
    for name, rd in mem.items():
        lr = line_ratio(rd)
        v = vol(rd)
        lines[name] = lr
        res[name] = dict(run=rd, n_line_outputs=len(lr),
                         t_last_line=lr[-1]["t"] if lr else None,
                         ratio=[(r["t"], r["ratio"]) for r in lr if r["t"] <= 5.0 + 1e-9],
                         ratio_t0=lr[0]["ratio"] if lr and abs(lr[0]["t"]) < 1e-9 else None,
                         max_ratio_t_le_5=max([r["ratio"] for r in lr if r["t"] <= 5.0 + 1e-9], default=None),
                         H={str(t): at(v, "H", t) for t in TIMES}, M={str(t): at(v, "M", t) for t in TIMES})
    # t = 0 slices: the evolved members repeat the slice of their nlim = 0 twin
    def r0(n):
        return (res.get(n) or {}).get("ratio_t0")
    J = {}
    s2a, s2b = r0("S2-A0") or r0("S2-A"), r0("S2-B0") or r0("S2-B")
    s1a, s1b = r0("S1-A0") or r0("S1-A"), r0("S1-B0") or r0("S1-B")
    tha, thb = r0("tophat A (K4-ref)"), r0("tophat B (card)")
    J["a"] = dict(S2_A=s2a, S2_B=s2b, fall=(s2a / s2b if s2a and s2b else None),
                  holds=(None if s2a is None or s2b is None else bool(s2a < 0.1 and s2b < 0.1 and s2a / s2b >= 2.0)),
                  S1_A=s1a, S1_B=s1b, S1_fall=(s1a / s1b if s1a and s1b else None))
    def m0(n):
        return (res.get(n) or {}).get("M", {}).get("0.0")
    J["c"] = dict(M_S2_A=m0("S2-A0"), M_S2_B=m0("S2-B0"), M_tophat_A=m0("tophat A (K4-ref)"), M_tophat_B=m0("tophat B (card)"),
                  holds=(None if not (m0("S2-A0") and m0("S2-B0")) else bool(m0("S2-B0") < m0("S2-A0"))))
    s2 = res.get("S2-A")
    if s2:
        hk = res["tophat A (K4-ref)"]["H"]
        fac = {t: (hk[t] / s2["H"][t] if (s2["H"].get(t) and hk.get(t)) else None) for t in ("1.0", "2.0", "3.0", "4.0", "5.0")}
        J["d"] = dict(t_last=s2["t_last_line"], max_ratio=s2["max_ratio_t_le_5"], H_factor_vs_K4ref=fac,
                      holds_so_far=(None if s2["max_ratio_t_le_5"] is None else bool(
                          s2["max_ratio_t_le_5"] < 0.1 and all(f is None or f >= 3.0 for k, f in fac.items() if k in ("1.0", "2.0")))))
    J["e"] = dict(tophat_A=tha, S1_A=s1a, S2_A=s2a, tophat_B=thb, S1_B=s1b, S2_B=s2b)
    out = dict(members=res, judgement=J)
    json.dump(out, open(os.path.join(a.out, "edge.json"), "w"), indent=1)
    print(json.dumps(J, indent=1))
    for n, r in res.items():
        print(f"{n:22s} ratio(t=0) {r['ratio_t0']}  max ratio t<=5 {r['max_ratio_t_le_5']}  last t {r['t_last_line']}  "
              f"H(0,1,2) {r['H']['0.0']}, {r['H']['1.0']}, {r['H']['2.0']}  M(0) {r['M']['0.0']}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(HERE, "..", "..", "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.5))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.18, top=0.88, wspace=0.38)
    sty = {"tophat A (K4-ref)": ("0.15", "-", "o"), "tophat A (card)": ("0.45", ":", None), "tophat B (card)": ("0.15", "--", "s"),
           "S1-A": (fs.PAL["blue"], "-", "o"), "S1-A0": (fs.PAL["blue"], "-", "o"), "S1-B0": (fs.PAL["blue"], "--", "s"),
           "S2-A": (fs.PAL["red"], "-", "o"), "S2-A0": (fs.PAL["red"], "-", "o"), "S2-B0": (fs.PAL["red"], "--", "s"),
           "S2-B": (fs.PAL["red"], "--", "s")}
    for n, lr in lines.items():
        if not lr or n not in sty:
            continue
        c, ls, mk = sty[n]
        tt = [r["t"] for r in lr if r["t"] <= 5.0 + 1e-9]
        rr = [r["ratio"] for r in lr if r["t"] <= 5.0 + 1e-9]
        if len(tt) == 1:
            ax[0].plot(tt, rr, ls="none", marker=mk or "o", ms=4, color=c, label=n)
        else:
            ax[0].plot(tt, rr, ls=ls, marker=mk, ms=2, color=c, lw=0.9, label=n)
    ax[0].axhline(0.1, color="0.5", lw=0.7, ls="-.")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("$t/M$")
    ax[0].set_ylabel(r"$\|H\|/\|16\pi E\|$ (x line)")
    ax[0].set_title("(a) section-3 ratio", fontsize=8)
    ax[0].legend(fontsize=5, ncol=2)
    for n, rd in mem.items():
        v = vol(rd)
        if v is None or n not in sty or n.endswith("0"):
            continue
        c, ls, _ = sty[n]
        k = v["t"] <= 5.0 + 1e-9
        ax[1].plot(v["t"][k], v["H"][k], ls=ls, color=c, lw=0.9, label=n)
    ax[1].set_yscale("log")
    ax[1].set_xlabel("$t/M$")
    ax[1].set_ylabel(r"volume $\|H\|_2$")
    ax[1].set_title("(b) Hamiltonian norm", fontsize=8)
    ax[1].legend(fontsize=5)
    for n in ("tophat A (K4-ref)", "tophat B (card)", "S2-A0", "S2-B0", "S1-A0"):
        lr = lines.get(n)
        if not lr:
            continue
        c, ls, _ = sty[n]
        ax[2].plot(lr[0]["x"], np.abs(lr[0]["H"]), ls=ls, color=c, lw=0.7, label=n)
    ax[2].set_yscale("log")
    ax[2].set_xlim(0, 8)
    ax[2].set_xlabel("$x/M$ (line, $t = 0$)")
    ax[2].set_ylabel(r"$|H|$")
    ax[2].set_title("(c) residual at $t = 0$", fontsize=8)
    ax[2].legend(fontsize=5)
    fig.savefig(os.path.join(a.out, "fig_edge.png"), dpi=150)
    fig.savefig(os.path.join(a.out, "fig_edge.pdf"))


if __name__ == "__main__":
    main()
