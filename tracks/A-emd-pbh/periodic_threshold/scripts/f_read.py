#!/usr/bin/env python3
"""Reader of S1L-F (queue entry q0090, condition (d) of decision 0047): predictions F1-F3 of the periodic_threshold
JOURNAL, 2026-11-27 16:39 PST.

  f_read.py --run RUNDIR --ref S1LDIR --out OUTDIR [--fd 190.0:7.605602 --fd 198.7:8.336185 --fd 220.0:10.73958]

F1: rows of <base>.horizon_status_0.txt (found only there): first found row, area mass and mean radius there, every
    later search (found or the reason), masses of found rows non-decreasing within 1e-3.
F2: <base>.region.hst columns 38-42 (outside the found horizon, region_horizon = 0): H2_out/E2_out at the first row
    after the first detection; also the ratio inside the horizon and outside the sphere s2 (r = 0.6), and S1L's own
    ratio outside s2 at the same times (the premise).
F3: alpha_min (nrpic.hst column 16) of the run against S1L's at t = 100 and over 0 < t < 205.
Writes OUTDIR/f_read.json and fig_s1l_finder.{png,pdf}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    """History rows with continued segments resolved: a chain continued from an earlier restart file appends rows
    whose time is not above the previous row's; the later segment supersedes the rows it repeats (batch 40: S1L's
    nrpic.hst holds a segment to t = 66.3 followed by its continuation from t ~ 50)."""
    d = np.loadtxt(path, comments="#", ndmin=2)
    keep = []
    for i in range(len(d)):
        while keep and d[keep[-1], 0] >= d[i, 0]:
            keep.pop()
        keep.append(i)
    return d[keep]


def status(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            body, _, why = ln.partition("#")
            v = body.split()
            rows.append(dict(cycle=int(v[0]), t=float(v[1]), found=int(v[2]), reason=int(v[3]), it=int(v[4]),
                             area=float(v[5]), m=float(v[6]), rmean=float(v[7]), rmin=float(v[8]),
                             theta=float(v[9]), why=why.strip()))
    return rows


def at_time(d, t, col):
    i = int(np.argmin(np.abs(d[:, 0] - t)))
    return float(d[i, 0]), float(d[i, col])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default="peak")
    ap.add_argument("--fd", action="append", default=[], help="t:m from the restart-file probes (FD)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    st = status(os.path.join(a.run, a.base + ".horizon_status_0.txt"))
    found = [r for r in st if r["found"] == 1]
    first = found[0] if found else None
    after = [r for r in st if first and r["t"] > first["t"]]
    stalls = [r for r in after if r["found"] != 1]
    mono = all(found[i + 1]["m"] >= found[i]["m"] * (1 - 1e-3) for i in range(len(found) - 1))
    res = dict(n_search=len(st), n_found=len(found), first_found=first, n_after=len(after),
               stalls=[dict(t=r["t"], reason=r["reason"], it=r["it"], m=r["m"], why=r["why"]) for r in stalls],
               masses_nondecreasing_1em3=mono,
               last_found=found[-1] if found else None)
    # F2: region norms
    rg = load(os.path.join(a.run, a.base + ".region.hst"))
    rr = load(os.path.join(a.ref, a.base + ".region.hst"))
    det = rg[rg[:, 31] > 0]
    reg = []
    for row in det[:12]:
        reg.append(dict(t=row[0], r_h=row[31], out_h=row[38] / row[39], in_h=row[33] / row[34] if row[34] > 0 else None,
                        out_s2=row[27] / row[28], whole=row[6] / row[7]))
    res["region_first_rows"] = reg
    res["region_at_detection"] = reg[0] if reg else None
    # premise: S1L's own ratio outside s2 near 190
    prem = []
    for t in (170.0, 180.0, 190.0, 200.0):
        i = int(np.argmin(np.abs(rr[:, 0] - t)))
        j = int(np.argmin(np.abs(rg[:, 0] - t)))
        prem.append(dict(t_ref=rr[i, 0], s1l_out_s2=rr[i, 27] / rr[i, 28], t_run=rg[j, 0], run_out_s2=rg[j, 27] / rg[j, 28]))
    res["out_s2_compare"] = prem
    # F3: alpha_min
    hr = load(os.path.join(a.run, a.base + ".nrpic.hst"))
    hs = load(os.path.join(a.ref, a.base + ".nrpic.hst"))
    t1, a1 = at_time(hr, 100.0, 15)
    t2, a2 = at_time(hs, 100.0, 15)
    res["alpha_min_t100"] = dict(t_run=t1, run=a1, t_ref=t2, ref=a2, rel=abs(a1 - a2) / a2)
    tt = hr[:, 0][(hr[:, 0] > 0) & (hr[:, 0] < min(hr[-1, 0], hs[-1, 0]))]
    ai = np.interp(tt, hs[:, 0], hs[:, 15])
    ar = np.interp(tt, hr[:, 0], hr[:, 15])
    rel = np.abs(ar - ai) / ai
    res["alpha_min_maxrel_0_205"] = float(rel.max())
    res["fd"] = [dict(t=float(s.split(":")[0]), m=float(s.split(":")[1])) for s in a.fd]
    json.dump(res, open(os.path.join(a.out, "f_read.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(first_found=first, n_found=len(found), n_after=len(after), n_stalls=len(stalls),
                          mono=mono, region_at_detection=res["region_at_detection"], alpha_t100=res["alpha_min_t100"],
                          alpha_maxrel=res["alpha_min_maxrel_0_205"], out_s2=prem), indent=1, default=float))

    sys.path.insert(0, HERE)
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))
    tf = [r["t"] for r in found]
    ax[0].plot(tf, [r["m"] for r in found], "o", ms=3, color=fs.PAL["blue"], label="found (S1L-F)")
    ts = [r["t"] for r in stalls]
    ax[0].plot(ts, [r["m"] for r in stalls], "x", ms=5, color=fs.PAL["red"], label="iteration limit after first find")
    for k, d in enumerate(res["fd"]):
        ax[0].plot(d["t"], d["m"], "s", mfc="none", ms=7, color="k", label="restart-file probe (FD)" if k == 0 else None)
    ax[0].axvspan(178, 195, color="0.85", zorder=0, label="F1 window")
    ax[0].set_xlabel("t"); ax[0].set_ylabel("area mass"); ax[0].set_xlim(165, 222); ax[0].legend(fontsize=7)
    ax[1].semilogy(rg[:, 0], rg[:, 27] / rg[:, 28], color=fs.PAL["blue"], label="S1L-F outside r = 0.6")
    ax[1].semilogy(rr[:, 0], rr[:, 27] / rr[:, 28], "--", color=fs.PAL["orange"], label="S1L outside r = 0.6")
    ax[1].semilogy(det[:, 0], det[:, 38] / det[:, 39], color=fs.PAL["red"], label="S1L-F outside horizon")
    ax[1].semilogy(rg[:, 0], rg[:, 6] / rg[:, 7], ":", color="0.4", label="S1L-F whole box")
    ax[1].axhline(0.1, color="k", lw=0.8)
    ax[1].set_xlabel("t"); ax[1].set_ylabel(r"$\|H\| / \|16\pi E\|$"); ax[1].legend(fontsize=7)
    ax[2].semilogy(tt, np.maximum(rel, 1e-17), color=fs.PAL["blue"])
    ax[2].axhline(1e-6, color="k", lw=0.8)
    ax[2].set_xlabel("t"); ax[2].set_ylabel(r"$|\alpha_{\min}-\alpha_{\min}^{\rm S1L}|/\alpha_{\min}^{\rm S1L}$")
    for k, s in enumerate("abc"):
        ax[k].set_title("(%s)" % s, loc="left", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_s1l_finder"))


if __name__ == "__main__":
    main()
