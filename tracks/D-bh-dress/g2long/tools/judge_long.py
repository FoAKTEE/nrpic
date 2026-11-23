#!/usr/bin/env python3
"""Judgement of the long vacuum and null-test chains against g2long/JOURNAL.md entry 1.

Criteria and predictions read as written there (entry 1, committed 53afc1a before any run):
  D_X(t) = M_X(t) - M_X(100 M) (finder mass, column 3, unique times);
  F_V(T) = max |D_V1L(t)| over 100 <= t <= T.
  N  : max_{100<=t<=500} |D_ES1L - D_V1L| <= max(2 F_V(500), 1e-4);
       refuted if |D_ES1L - D_V1L| > 3 max(F_V(500), 5e-5) over a window longer than 50 M.
  V1 finite, horizon at every sample, no tracer leaves; V2 |M_V1L - M_V1B| <= 1e-6 for
  t <= 200 (refuted > 1e-5); V3 F_V(500) <= 1e-4 (refuted > 3e-4), mean radius at 500 M
  in 2.2-2.6 M.
  E1 |M_ES1L - M_ES1| <= 1e-5 up to 130 M (refuted > 1e-4); E2 N holds, and
  max |D_ES1L - D_V1L| <= 1e-4 on 100-300 M, <= 2e-4 on 100-500 M; E3 radius 2.6-3.1 M.
  H1 M_V1L16 - 1 on 100-300 M in [3e-5, 4e-4]; H2 F_V16(300) <= 5e-5 and below F_V(300);
  H3 max |D_ES1L16 - D_V1L16| on 100-T <= max |D_ES1L - D_V1L| on the same window
  (T = the end reached by both M/16 runs; partial if T < 300).
Costs (V4, E4, H4) are read from the chain segment logs by the caller, not here.

Usage: judge_long.py --out DIR NAME=RUNDIR:BASE ... with the names V-1L, ES-1L, V-1B, ES-1,
V-1L16, ES-1L16 (an absent name skips its items).
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


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t, m, r = a[:, 1], a[:, 2], a[:, 10]
    _, idx = np.unique(t, return_index=True)
    idx = np.sort(idx)
    return t[idx], m[idx], r[idx]


def read_hist(path):
    if not os.path.exists(path):
        return None
    a = np.loadtxt(path, comments="#", ndmin=2)
    return {"t": a[:, 0], "np": a[:, 2], "alpha_min": a[:, 15], "n_esc": a[:, 18]}


def common(ta, ya, tb, yb):
    ka = np.round(ta * 8).astype(np.int64)
    kb = np.round(tb * 8).astype(np.int64)
    k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
    return k / 8.0, ya[ia], yb[ib]


def at(t, y, t0):
    i = int(np.argmin(np.abs(t - t0)))
    return float(y[i]), float(t[i])


def drift(t, m):
    m100, _ = at(t, m, T0)
    return m - m100


def floor(t, d, T):
    w = (t >= T0) & (t <= T + 1e-9)
    return float(np.max(np.abs(d[w]))) if w.any() else None


def longest_run_above(t, x, thr):
    """Longest contiguous time span (in M) where |x| > thr."""
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
        t, m, r = read_summary(os.path.join(rd, base + ".horizon_summary_0.txt"))
        h = read_hist(os.path.join(rd, base + ".nrpic.hst"))
        R[name] = dict(t=t, m=m, r=r, h=h, dir=rd)
    out = {"runs": {k: dict(dir=v["dir"], t_last=float(v["t"][-1]), n=int(v["t"].size),
                            finite=bool(np.all(np.isfinite(v["m"]))),
                            max_gap=float(np.max(np.diff(v["t"]))),
                            M_last=float(v["m"][-1]), r_last=float(v["r"][-1]))
                    for k, v in R.items()}}
    for k, v in R.items():
        if v["h"] is not None:
            h = v["h"]
            out["runs"][k].update(np_first=float(h["np"][0]), np_last=float(h["np"][-1]),
                                  n_escaped_last=float(h["n_esc"][-1]), t_hst_last=float(h["t"][-1]))
        if v["t"][-1] >= T0:
            v["d"] = drift(v["t"], v["m"])
    J = {}
    if "V-1L" in R:
        v = R["V-1L"]
        FV500, FV300 = floor(v["t"], v["d"], 500.0), floor(v["t"], v["d"], 300.0)
        w = (v["t"] >= T0)
        J["V3"] = dict(F_V_500=FV500, F_V_300=FV300, D_range_100_500=[float(v["d"][w].min()), float(v["d"][w].max())],
                       r_500=at(v["t"], v["r"], 500.0)[0], M_100_minus_1=at(v["t"], v["m"], 100.0)[0] - 1.0,
                       holds=bool(FV500 <= 1e-4), refuted=bool(FV500 > 3e-4),
                       radius_in_range=bool(2.2 <= at(v["t"], v["r"], 500.0)[0] <= 2.6))
        J["V1"] = dict(finite=out["runs"]["V-1L"]["finite"], max_gap=out["runs"]["V-1L"]["max_gap"],
                       n_escaped=out["runs"]["V-1L"].get("n_escaped_last"),
                       np=[out["runs"]["V-1L"].get("np_first"), out["runs"]["V-1L"].get("np_last")])
        if "V-1B" in R:
            b = R["V-1B"]
            tc, x, y = common(v["t"], v["m"], b["t"], b["m"])
            s = tc <= 200.0
            dd = np.abs(x[s] - y[s])
            J["V2"] = dict(max_abs=float(dd.max()), t_max=float(tc[s][np.argmax(dd)]),
                           holds=bool(dd.max() <= 1e-6), refuted=bool(dd.max() > 1e-5),
                           first_above_1e6=float(tc[s][np.nonzero(dd > 1e-6)[0][0]]) if np.any(dd > 1e-6) else None)
    if "ES-1L" in R:
        e = R["ES-1L"]
        J["E3"] = dict(r_500=at(e["t"], e["r"], 500.0)[0],
                       holds=bool(2.6 <= at(e["t"], e["r"], 500.0)[0] <= 3.1))
        J["E1_run"] = dict(finite=out["runs"]["ES-1L"]["finite"], max_gap=out["runs"]["ES-1L"]["max_gap"])
        if "ES-1" in R:
            p = R["ES-1"]
            tc, x, y = common(e["t"], e["m"], p["t"], p["m"])
            s = tc <= 130.0
            dd = np.abs(x[s] - y[s])
            J["E1"] = dict(max_abs=float(dd.max()), t_max=float(tc[s][np.argmax(dd)]),
                           holds=bool(dd.max() <= 1e-5), refuted=bool(dd.max() > 1e-4))
        if "V-1L" in R:
            v = R["V-1L"]
            tc, de, dv = common(e["t"], e["d"], v["t"], v["d"])
            x = de - dv
            w5 = tc >= T0
            w3 = w5 & (tc <= 300.0)
            FV = J["V3"]["F_V_500"]
            thrN = max(2 * FV, 1e-4)
            thrR = 3 * max(FV, 5e-5)
            J["N"] = dict(max_abs_100_500=float(np.max(np.abs(x[w5]))), max_abs_100_300=float(np.max(np.abs(x[w3]))),
                          range_100_500=[float(x[w5].min()), float(x[w5].max())],
                          t_at_max=float(tc[w5][np.argmax(np.abs(x[w5]))]),
                          threshold_pass=thrN, threshold_refute=thrR,
                          longest_above_refute_M=longest_run_above(tc[w5], x[w5], thrR),
                          holds=bool(np.max(np.abs(x[w5])) <= thrN),
                          refuted=bool(longest_run_above(tc[w5], x[w5], thrR) > 50.0),
                          E2_300=bool(np.max(np.abs(x[w3])) <= 1e-4),
                          E2_500=bool(np.max(np.abs(x[w5])) <= 2e-4))
            R["_N8"] = dict(t=tc, x=x)
    if "V-1L16" in R:
        v6 = R["V-1L16"]
        w = (v6["t"] >= T0) & (v6["t"] <= 300.0 + 1e-9)
        bias = v6["m"][w] - 1.0
        FV16 = floor(v6["t"], v6["d"], 300.0)
        J["H1"] = dict(bias_range=[float(bias.min()), float(bias.max())],
                       holds=bool(bias.min() >= 3e-5 and bias.max() <= 4e-4))
        if "V-1L" in R:
            v = R["V-1L"]
            w8 = (v["t"] >= T0) & (v["t"] <= 300.0 + 1e-9)
            J["H1"]["bias_range_M8"] = [float(v["m"][w8].min() - 1), float(v["m"][w8].max() - 1)]
        J["H2"] = dict(F_V16_300=FV16, F_V8_300=J.get("V3", {}).get("F_V_300"),
                       holds=bool(FV16 <= 5e-5 and (J.get("V3") is None or FV16 < J["V3"]["F_V_300"])))
        if "ES-1L16" in R and "_N8" in R and R["ES-1L16"]["t"][-1] >= T0:
            e6 = R["ES-1L16"]
            tc, de, dv = common(e6["t"], e6["d"], v6["t"], v6["d"])
            x16 = de - dv
            T = float(min(tc[-1], 300.0))
            w16 = (tc >= T0) & (tc <= T)
            n8 = R["_N8"]
            w8 = (n8["t"] >= T0) & (n8["t"] <= T)
            J["H3"] = dict(T=T, partial=bool(T < 300.0 - 0.5),
                           max_abs_M16=float(np.max(np.abs(x16[w16]))), max_abs_M8=float(np.max(np.abs(n8["x"][w8]))),
                           range_M16=[float(x16[w16].min()), float(x16[w16].max())],
                           holds=bool(np.max(np.abs(x16[w16])) <= np.max(np.abs(n8["x"][w8]))))
            R["_N16"] = dict(t=tc, x=x16)
    out["judgement"] = J
    with open(os.path.join(a.out, "judge_long.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(J, indent=1))
    figure(a.out, R, J)


def figure(outdir, R, J):
    fs.use_style()
    col = {"V-1L": fs.PAL["blue"], "ES-1L": fs.PAL["red"], "V-1B": "#7f7f7f", "ES-1": "#c49a6c",
           "V-1L16": fs.PAL["green"], "ES-1L16": fs.PAL["yellow"]}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2), constrained_layout=True)
    x = ax[0, 0]
    for k in ("V-1B", "ES-1", "V-1L", "ES-1L", "V-1L16", "ES-1L16"):
        if k in R:
            x.plot(R[k]["t"], R[k]["m"] - 1.0, color=col[k], lw=1.0, label=k)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$M_{\rm AH}/M-1$")
    x.set_ylim(-2e-3, 2e-3)
    x.legend(fontsize=7, frameon=False, ncol=2)
    x.set_title("(a) finder mass (M/8 bias +9e-4; M/16 near 0)", loc="left", fontsize=9)
    x = ax[0, 1]
    for k in ("V-1L", "ES-1L", "V-1L16", "ES-1L16"):
        if k in R and "d" in R[k]:
            w = R[k]["t"] >= T0
            x.plot(R[k]["t"][w], R[k]["d"][w], color=col[k], lw=1.0, label=k)
    if "V3" in J:
        F = J["V3"]["F_V_500"]
        x.axhspan(-F, F, color="grey", alpha=0.15, lw=0, label=r"$\pm F_V(500)$")
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$D_X=M_X(t)-M_X(100\,M)$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(b) drift after 100 M", loc="left", fontsize=9)
    x = ax[1, 0]
    if "_N8" in R:
        x.plot(R["_N8"]["t"], R["_N8"]["x"], color=fs.PAL["red"], lw=1.0, label="M/8: ES-1L - V-1L")
    if "_N16" in R:
        x.plot(R["_N16"]["t"], R["_N16"]["x"], color=fs.PAL["yellow"], lw=1.0, label="M/16: ES-1L16 - V-1L16")
    if "N" in J:
        for s in (1, -1):
            x.axhline(s * J["N"]["threshold_pass"], **fs.GUIDE)
            x.axhline(s * J["N"]["threshold_refute"], color="k", lw=0.8, ls=":")
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$D_{\rm ES}-D_{\rm V}$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(c) null test N (dashed: pass, dotted: refute)", loc="left", fontsize=9)
    x = ax[1, 1]
    for k, p in (("V-1L", "V-1B"), ("ES-1L", "ES-1")):
        if k in R and p in R:
            tc, y1, y2 = common(R[k]["t"], R[k]["m"], R[p]["t"], R[p]["m"])
            x.semilogy(tc, np.abs(y1 - y2) + 1e-17, color=col[k], lw=1.0, label=f"|{k} - {p}|")
    x.axhline(1e-6, color="k", lw=0.8, ls=":")
    x.axhline(1e-5, **fs.GUIDE)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$|\Delta M_{\rm AH}|/M$")
    x.legend(fontsize=7, frameon=False)
    x.set_title("(d) against the runs with nearer faces", loc="left", fontsize=9)
    fs.save(fig, os.path.join(outdir, "judge_long"))
    plt.close(fig)


if __name__ == "__main__":
    main()
