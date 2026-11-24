#!/usr/bin/env python3
"""Judgement of the three mesh members (M/4, M/8, M/16) against g2long/JOURNAL.md entry 6.

Predictions as written there (committed ab5d9830 before any follow-up card run):
  P1 V-1L4 finite to 300 M; horizon found at every sample after 20 M.
  P2 M_V1L4 - 1 on 100-300 M in [+4e-3, +2.5e-2]; refuted (M/4 not in the convergent
     regime, no three-member order quoted) if below 0 or above 5e-2.
  P3 the vacuum drift step of V-1L and V-1L16 at 240-300 M appears again within 10 M in
     time and within a factor 2 in size; refuted if absent.
  P5 null test at M/4: max |D_ES1L4 - D_V1L4| on 100-300 M in [1e-4, 4e-4] and within 1e-4
     of the M/8 difference at every common sample after 110 M; refuted if it departs from
     the M/8 difference by more than 2e-4 over a window longer than 20 M.
Definitions of entry 1: D_X(t) = M_X(t) - M_X(100 M) (finder mass, column 3, unique times).

The step measure of P3 (defined here, before FE4 has run; V-1L4 was looked at first, so it
is a description, not a blind test): S = median of M on 260-300 M minus median on 200-240 M,
for each vacuum member; for M/4 also after removing the straight line fitted on 150-240 M
(its secular decline), S_detr. The first time after 225 M at which M departs from its
200-225 M median by more than 4e-5 is t_step.

Three-member orders: for each time t in (0, 100, 200, 300) M the finder offsets e(h) = M - 1
at h = M/4, M/8, M/16; ratio q = (e4 - e8)/(e8 - e16); a convergent sequence has q > 1 and
order p = log2(q).

Usage: judge_conv.py --out DIR NAME=RUNDIR:BASE ... with names V-1L4, V-1L, V-1L16, ES-1L4,
ES-1L, ES-1L16 (an absent name skips its items).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

T0 = 100.0
H = {"V-1L4": 0.25, "V-1L": 0.125, "V-1L16": 0.0625}


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t = a[:, 1]
    _, idx = np.unique(t, return_index=True)
    idx = np.sort(idx)
    return dict(t=t[idx], m=a[idx, 2], hrms=a[idx, 8], r=a[idx, 10])


def at(t, y, t0):
    i = int(np.argmin(np.abs(t - t0)))
    return float(y[i])


def common(ta, ya, tb, yb):
    ka = np.round(ta * 8).astype(np.int64)
    kb = np.round(tb * 8).astype(np.int64)
    k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
    return k / 8.0, ya[ia], yb[ib]


def longest_run_above(t, x, thr):
    above = np.abs(x) > thr
    best, start = 0.0, None
    for i in range(len(t)):
        if above[i] and start is None:
            start = t[i]
        if (not above[i] or i == len(t) - 1) and start is not None:
            end = t[i] if above[i] else t[i - 1]
            best = max(best, end - start)
            start = None
    return best


def med(t, y, a, b):
    w = (t >= a) & (t <= b)
    return float(np.median(y[w])) if w.any() else None


def step_measure(v):
    t, m = v["t"], v["m"]
    s = med(t, m, 260, 300) - med(t, m, 200, 240)
    w = (t >= 150) & (t <= 240)
    c = np.polyfit(t[w], m[w], 1)
    res = m - np.polyval(c, t)
    sd = med(t, res, 260, 300) - med(t, res, 200, 240)
    base = med(t, m, 200, 225)
    late = (t > 225) & (t <= 300)
    dep = np.nonzero(np.abs(m[late] - base) > 4e-5)[0]
    tstep = float(t[late][dep[0]]) if dep.size else None
    base_r = med(t, res, 200, 225)
    dep_r = np.nonzero(np.abs(res[late] - base_r) > 4e-5)[0]
    tstep_r = float(t[late][dep_r[0]]) if dep_r.size else None
    return dict(S=s, S_detr=float(sd), slope_150_240=float(c[0]), t_step=tstep,
                t_step_detr=tstep_r), res


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
        R[name]["dir"] = rd
        R[name]["d"] = R[name]["m"] - at(R[name]["t"], R[name]["m"], T0)
    out = {"runs": {k: dict(dir=v["dir"], t_first=float(v["t"][0]), t_last=float(v["t"][-1]),
                            n=int(v["t"].size), finite=bool(np.all(np.isfinite(v["m"]))),
                            max_gap=float(np.max(np.diff(v["t"]))),
                            sample=float(np.median(np.diff(v["t"]))))
                    for k, v in R.items()}}
    J = {}
    if "V-1L4" in R:
        v = R["V-1L4"]
        w20 = v["t"] >= 20.0
        J["P1"] = dict(finite=bool(np.all(np.isfinite(v["m"]))), t_last=float(v["t"][-1]),
                       max_gap_after_20=float(np.max(np.diff(v["t"][w20]))),
                       sample=out["runs"]["V-1L4"]["sample"],
                       holds=bool(np.all(np.isfinite(v["m"])) and v["t"][-1] >= 299.0 and
                                  np.max(np.diff(v["t"][w20])) <= 1.0 + 1e-9))
        w = (v["t"] >= T0) & (v["t"] <= 300.0 + 1e-9)
        b = v["m"][w] - 1.0
        J["P2"] = dict(bias_range=[float(b.min()), float(b.max())],
                       holds=bool(b.min() >= 4e-3 and b.max() <= 2.5e-2),
                       refuted=bool(b.min() < 0.0 or b.max() > 5e-2))
    # three-member orders at fixed times
    if all(k in R for k in H):
        rows = []
        for t0 in (0.0, 20.0, 100.0, 200.0, 300.0):
            e = {k: at(R[k]["t"], R[k]["m"], t0) - 1.0 for k in H}
            q = (e["V-1L4"] - e["V-1L"]) / (e["V-1L"] - e["V-1L16"])
            rows.append(dict(t=t0, e4=e["V-1L4"], e8=e["V-1L"], e16=e["V-1L16"], q=q,
                             p=float(np.log2(q)) if q > 0 else None,
                             monotone=bool((e["V-1L4"] - e["V-1L"]) * (e["V-1L"] - e["V-1L16"]) > 0)))
        J["orders"] = rows
    # P3 step
    steps = {}
    for k in H:
        if k in R and R[k]["t"][-1] >= 299.0:
            st, res = step_measure(R[k])
            R[k]["res"] = res
            steps[k] = st
    if steps:
        J["P3"] = dict(steps=steps)
        if "V-1L4" in steps and "V-1L" in steps:
            s4, s8 = steps["V-1L4"], steps["V-1L"]
            ratio = s4["S_detr"] / s8["S"] if s8["S"] else None
            dt = (s4["t_step_detr"] - s8["t_step"]) if (s4["t_step_detr"] and s8["t_step"]) else None
            J["P3"].update(ratio_detr_M4_over_M8=ratio, dt_step_detr=dt,
                           holds=bool(ratio is not None and 0.5 <= ratio <= 2.0 and dt is not None
                                      and abs(dt) <= 10.0),
                           refuted=bool(ratio is None or ratio < 0.25))
    # null tests at each resolution
    nulls = {}
    for v, e, tag in (("V-1L4", "ES-1L4", "M4"), ("V-1L", "ES-1L", "M8"), ("V-1L16", "ES-1L16", "M16")):
        if v in R and e in R and R[e]["t"][-1] >= T0:
            tc, de, dv = common(R[e]["t"], R[e]["d"], R[v]["t"], R[v]["d"])
            x = de - dv
            T = float(min(tc[-1], 300.0))
            w = (tc >= T0) & (tc <= T)
            nulls[tag] = dict(t=tc, x=x, T=T, max_abs=float(np.max(np.abs(x[w]))),
                              range=[float(x[w].min()), float(x[w].max())],
                              t_at_max=float(tc[w][np.argmax(np.abs(x[w]))]))
    J["null"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("t", "x")} for k, v in nulls.items()}
    if "M4" in nulls and "M8" in nulls:
        n4, n8 = nulls["M4"], nulls["M8"]
        tc, x4, x8 = common(n4["t"], n4["x"], n8["t"], n8["x"])
        w = (tc >= 110.0) & (tc <= min(n4["T"], 300.0))
        dd = x4[w] - x8[w]
        J["P5"] = dict(max_abs_M4=n4["max_abs"], max_abs_M8_100_300=nulls["M8"]["max_abs"],
                       max_dev_from_M8=float(np.max(np.abs(dd))),
                       longest_dev_above_2e4=longest_run_above(tc[w], dd, 2e-4),
                       holds=bool(1e-4 <= n4["max_abs"] <= 4e-4 and np.max(np.abs(dd)) <= 1e-4),
                       refuted=bool(longest_run_above(tc[w], dd, 2e-4) > 20.0))
    out["judgement"] = J
    with open(os.path.join(a.out, "judge_conv.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(J, indent=1))
    figure(a.out, R, J, nulls)


def figure(outdir, R, J, nulls):
    fs.use_style()
    col = {"V-1L4": fs.PAL["orange"], "V-1L": fs.PAL["blue"], "V-1L16": fs.PAL["green"],
           "ES-1L4": fs.PAL["orange"], "ES-1L": fs.PAL["blue"], "ES-1L16": fs.PAL["green"]}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4), constrained_layout=True)
    x = ax[0, 0]
    for k in ("V-1L4", "V-1L", "V-1L16"):
        if k in R:
            x.plot(R[k]["t"], R[k]["m"] - 1.0, color=col[k], lw=1.0, label=f"{k} (h = M/{int(round(1/H[k]))})")
    x.set_yscale("symlog", linthresh=1e-4)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$M_{\rm AH}/M-1$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(a) finder offset, vacuum, three meshes", loc="left", fontsize=9)
    x = ax[0, 1]
    for k in ("V-1L4", "V-1L", "V-1L16"):
        if k in R:
            w = R[k]["t"] >= T0
            y = R[k]["res"] if (k == "V-1L4" and "res" in R[k]) else R[k]["d"]
            if k == "V-1L4" and "res" in R[k]:
                # detrended M/4 record, shown from 150 M (the fit window) and set to zero
                # on 200-225 M, the base of the step measure
                y = y - np.median(y[(R[k]["t"] >= 200) & (R[k]["t"] <= 225)])
                w = R[k]["t"] >= 150.0
            lab = k + (" minus line fit 150-240 M (zero on 200-225 M)" if k == "V-1L4" and "res" in R[k] else "")
            x.plot(R[k]["t"][w], y[w], color=col[k], lw=1.0, label=lab)
    for tt in (240.0, 300.0):
        x.axvline(tt, **fs.MASK_LINE)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$D_X=M_X(t)-M_X(100\,M)$")
    x.set_ylim(-3e-4, 3e-4)
    x.legend(fontsize=7, frameon=False, loc="lower left")
    x.set_title("(b) drift after 100 M (P3: step at 240-300 M)", loc="left", fontsize=9)
    x = ax[1, 0]
    for tag, k in (("M4", "ES-1L4"), ("M8", "ES-1L"), ("M16", "ES-1L16")):
        if tag in nulls:
            n = nulls[tag]
            w = (n["t"] >= T0) & (n["t"] <= 300.0)
            x.plot(n["t"][w], n["x"][w], color=col[k], lw=1.0, label=f"{tag}: ES - V")
    for s in (1, -1):
        x.axhline(s * 2.51e-4, **fs.GUIDE)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$D_{\rm ES}-D_{\rm V}$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(c) null test at three meshes (dashed: N threshold)", loc="left", fontsize=9)
    x = ax[1, 1]
    if "orders" in J:
        hs = np.array([0.25, 0.125, 0.0625])
        for r, c in zip(J["orders"], fs.series_colors(len(J["orders"]))):
            e = np.array([r["e4"], r["e8"], r["e16"]])
            x.loglog(hs, np.abs(e), "-", color=c, lw=1.0, label=f"t = {r['t']:.0f} M")
            for hh, ee in zip(hs, e):
                x.plot(hh, abs(ee), "o" if ee > 0 else "v", color=c, ms=5,
                       mfc=c if ee > 0 else "white")
        hh = np.array([0.0625, 0.25])
        x.loglog(hh, 4e-2 * (hh / 0.25) ** 2, **fs.GUIDE, label=r"$\propto h^2$")
        x.legend(fontsize=7, frameon=False, loc="lower right")
    x.set_xlabel(r"$h/M$ (finest level)")
    x.set_ylabel(r"$|M_{\rm AH}/M-1|$ (filled $>0$, open $<0$)")
    x.set_title("(d) finder offset against mesh spacing", loc="left", fontsize=9)
    fs.save(fig, os.path.join(outdir, "judge_conv"))
    plt.close(fig)


if __name__ == "__main__":
    main()
