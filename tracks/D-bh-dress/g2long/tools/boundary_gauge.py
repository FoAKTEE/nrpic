#!/usr/bin/env python3
"""Boundary and gauge members of the vacuum control and of the null test (checklist C2/C10 of
stage/G2): the finder mass of the same data with the outer faces at +-192 M (V-1, ES-1),
+-384 M (V-1B) and +-768 M (V-1L, ES-1L), and with the relaxed lapse (lapse_leak 0.5, V-1GB,
ES-1GB, faces +-384 M), all at M/8.

Boundary: Delta_F(t) = M_F(t) - M_768(t) for F = 192, 384 against the arrival time of a signal
from the nearest face at the far-field gauge speed sqrt(2) (F / sqrt 2: 136 M, 272 M; g2long
JOURNAL entry 1 [JUDGEMENT]); quoted: the largest |Delta_F| before and after that time.
Gauge: M_GB(t) - M_B(t) (relaxed against plain 1+log, same faces), vacuum and bubble.
No new prediction is judged here; the numbers summarise runs judged in g2long entries 1, 5 and
in g2runs (decision 0025 item 3).

Usage: boundary_gauge.py --out DIR NAME=RUNDIR:BASE ... with names V-1, V-1B, V-1L, ES-1, ES-1L,
V-1GB, ES-1GB.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ARRIVE = {"V-1": 192 / np.sqrt(2), "ES-1": 192 / np.sqrt(2), "V-1B": 384 / np.sqrt(2)}


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t = a[:, 1]
    _, idx = np.unique(t[::-1], return_index=True)
    idx = np.sort(t.size - 1 - idx)
    return t[idx], a[idx, 2]


def diff(A, B):
    ka = np.round(A[0] * 8).astype(np.int64)
    kb = np.round(B[0] * 8).astype(np.int64)
    k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
    return k / 8.0, A[1][ia] - B[1][ib]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        R[name] = read_summary(os.path.join(rd, base + ".horizon_summary_0.txt"))
    J = {"boundary": {}, "gauge": {}}
    pairs_b = (("V-1", "V-1L"), ("V-1B", "V-1L"), ("ES-1", "ES-1L"))
    D = {}
    for x, ref in pairs_b:
        if x in R and ref in R:
            t, d = diff(R[x], R[ref])
            D[(x, ref)] = (t, d)
            ta = ARRIVE[x]
            w0, w1 = (t >= 20) & (t < ta), t >= ta
            J["boundary"][f"{x} - {ref}"] = dict(
                t_arrive=float(ta), t_end=float(t[-1]),
                max_abs_before=float(np.max(np.abs(d[w0]))) if w0.any() else None,
                max_abs_after=float(np.max(np.abs(d[w1]))) if w1.any() else None,
                first_above_1e5=float(t[(t >= 20) & (np.abs(d) > 1e-5)][0]) if np.any((t >= 20) & (np.abs(d) > 1e-5)) else None)
    pairs_g = (("V-1GB", "V-1B"), ("ES-1GB", "V-1GB"))
    for x, ref in pairs_g:
        if x in R and ref in R:
            t, d = diff(R[x], R[ref])
            D[(x, ref)] = (t, d)
            w = t >= 20
            J["gauge"][f"{x} - {ref}"] = dict(t_end=float(t[-1]), range_after_20=[float(d[w].min()), float(d[w].max())])
    with open(os.path.join(a.out, "boundary_gauge.json"), "w") as f:
        json.dump(J, f, indent=1)
    print(json.dumps(J, indent=1))
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3), constrained_layout=True)
    x = ax[0]
    cols = {("V-1", "V-1L"): fs.PAL["red"], ("V-1B", "V-1L"): fs.PAL["blue"], ("ES-1", "ES-1L"): fs.PAL["orange"]}
    for (p, ref), c in cols.items():
        if (p, ref) in D:
            t, d = D[(p, ref)]
            x.semilogy(t, np.abs(d) + 1e-16, color=c, lw=1.0, label=f"|{p} - {ref}|")
            x.axvline(ARRIVE[p], color=c, lw=0.8, ls=":")
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$|\Delta M_{\rm AH}|/M$")
    x.set_ylim(1e-16, 1e-2)
    x.legend(fontsize=7, frameon=False, loc="upper left")
    x.set_title("(a) boundary: faces +-192, +-384 against +-768 M (dotted: F/sqrt 2)", loc="left", fontsize=8)
    x = ax[1]
    for (p, ref), c in ((("V-1GB", "V-1B"), fs.PAL["green"]), (("ES-1GB", "V-1GB"), fs.PAL["yellow"])):
        if (p, ref) in D:
            t, d = D[(p, ref)]
            w = t >= 20
            x.plot(t[w], d[w], color=c, lw=1.0, label=f"{p} - {ref}")
    x.axhline(0, **fs.THIN)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$\Delta M_{\rm AH}/M$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(b) gauge: relaxed lapse (lapse_leak 0.5) against plain 1+log", loc="left", fontsize=8)
    fs.save(fig, os.path.join(a.out, "boundary_gauge"))
    plt.close(fig)


if __name__ == "__main__":
    main()
