#!/usr/bin/env python3
"""Horizon mass, late drift and coordinate radius of the far-face runs against their parents.

Reads `<base>.horizon_summary_0.txt` (columns: 1 iter, 2 time, 3 mass, ..., 11 mean radius)
and `<base>.nrpic.hst` (column 3 np, 16 alpha_min, 17 n_excised, 19 n_escaped) of each
named run, keeps unique times (the finder writes t = 0 twice), and evaluates the
predictions B1-B3, C1-C3 of g2runs/JOURNAL.md entry 1. A run that has not reached t = 200 M
is read as far as it goes (--partial).

Usage: compare_horizons.py --out DIR NAME=RUNDIR:BASE [NAME=RUNDIR:BASE ...]
Names used by the judgement: ES-1G, ES-1GB, V-1B, V-1GB (others are plotted only).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

T0, T1, TEND = 100.0, 165.0, 199.5


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t, m, r = a[:, 1], a[:, 2], a[:, 10]
    _, idx = np.unique(t, return_index=True)   # first occurrence of each time
    idx = np.sort(idx)
    return t[idx], m[idx], r[idx]


def read_hist(path):
    if not os.path.exists(path):
        return None
    a = np.loadtxt(path, comments="#", ndmin=2)
    return {"t": a[:, 0], "np": a[:, 2], "alpha_min": a[:, 15], "n_exc": a[:, 16],
            "n_esc": a[:, 18]}


def at(t, y, t0):
    """Value at the sample nearest to t0 (finder every 16 cycles = 0.5 M here)."""
    i = int(np.argmin(np.abs(t - t0)))
    return float(y[i]), float(t[i])


def drift_stats(t, m):
    if t[-1] < T0:
        return None
    m100, t100 = at(t, m, T0)
    d = m - m100
    w1 = (t >= T0) & (t <= T1)
    w2 = (t >= T0) & (t <= TEND + 1e-9)
    out = {"t_ref": t100, "M_ref": m100, "M_ref_minus_1": m100 - 1.0,
           "D_100_165": [float(d[w1].min()), float(d[w1].max())],
           "D_100_end": [float(d[w2].min()), float(d[w2].max())],
           "t_last": float(t[w2][-1]), "D_last": float(d[w2][-1])}
    if t[-1] >= TEND - 0.25:
        out["D_199.5"] = at(t, d, TEND)[0]
    return out


def common(ta, ya, tb, yb):
    """Values of two series on their common times (finder times coincide: 0.5 M grid)."""
    ka = np.round(ta * 8).astype(np.int64)
    kb = np.round(tb * 8).astype(np.int64)
    common_k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
    return common_k / 8.0, ya[ia], yb[ib]


def first_exceed(t, d, thr):
    k = np.nonzero(np.abs(d) > thr)[0]
    return float(t[k[0]]) if len(k) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = {}
    for spec in a.runs:
        name, rest = spec.split("=", 1)
        rdir, base = rest.rsplit(":", 1)
        t, m, r = read_summary(os.path.join(rdir, f"{base}.horizon_summary_0.txt"))
        h = read_hist(os.path.join(rdir, f"{base}.nrpic.hst"))
        runs[name] = {"dir": rdir, "base": base, "t": t, "m": m, "r": r, "h": h}

    res = {"runs": {}, "pairs": {}, "judgement": {}}
    for name, R in runs.items():
        t, m, r = R["t"], R["m"], R["r"]
        e = {"dir": R["dir"], "t_max": float(t[-1]), "n_samples": int(len(t)),
             "finite": bool(np.all(np.isfinite(m))), "drift": drift_stats(t, m),
             "radius_25": at(t, r, 25.0)[0] if t[-1] >= 25 else None,
             "radius_last": float(r[-1]), "t_last": float(t[-1])}
        if t[-1] >= TEND - 0.25:
            e["radius_199.5"] = at(t, r, TEND)[0]
        if R["h"] is not None:
            h = R["h"]
            e["hist"] = {"np_min": float(h["np"].min()), "np_last": float(h["np"][-1]),
                         "n_excised_last": float(h["n_exc"][-1]),
                         "n_escaped_last": float(h["n_esc"][-1]),
                         "alpha_min_last": float(h["alpha_min"][-1]), "t_last": float(h["t"][-1])}
            late = h["t"] >= 108.0
            if late.any():
                e["hist"]["alpha_min_range_t108"] = [float(h["alpha_min"][late].min()),
                                                     float(h["alpha_min"][late].max())]
        res["runs"][name] = e

    def pair(a_, b_, label):
        if a_ not in runs or b_ not in runs:
            return None
        tc, ya, yb = common(runs[a_]["t"], runs[a_]["m"], runs[b_]["t"], runs[b_]["m"])
        d = ya - yb
        w90 = tc <= 90.0
        w30 = (tc >= 30.0) & (tc <= TEND + 1e-9)
        p = {"t_common_max": float(tc[-1]),
             "max_abs_t_le_90": float(np.abs(d[w90]).max()) if w90.any() else None,
             "max_abs_30_end": float(np.abs(d[w30]).max()) if w30.any() else None,
             "t_first_gt_2e-4": first_exceed(tc, d, 2e-4),
             "t_first_gt_5e-5": first_exceed(tc, d, 5e-5),
             "d_last": float(d[-1])}
        res["pairs"][label] = p
        return tc, d

    p_es = pair("ES-1GB", "ES-1G", "ES-1GB-ES-1G")
    p_null = pair("ES-1GB", "V-1GB", "ES-1GB-V-1GB")
    p_v = pair("V-1GB", "V-1B", "V-1GB-V-1B")

    J = res["judgement"]
    E = res["runs"].get("ES-1GB")
    if E and E["drift"]:
        d = E["drift"]
        full = "D_199.5" in d
        if full:
            dl = d["D_199.5"]
            J["B1"] = ("HELD" if (d["D_100_end"][0] >= -6e-4 and d["D_100_end"][1] <= 1.0e-3
                                  and -5e-4 <= dl <= 1.0e-3) else
                       "REFUTED (growth not from the boundary)" if dl >= 3.5e-3 else "FAILED")
            J["B1_pass_D199.5_lt_1e-3"] = bool(dl < 1.0e-3)
        else:
            J["B1"] = f"partial to t = {d['t_last']}"
    if "ES-1GB-ES-1G" in res["pairs"]:
        p = res["pairs"]["ES-1GB-ES-1G"]
        ok90 = p["max_abs_t_le_90"] is not None and p["max_abs_t_le_90"] <= 5e-5
        sep = p["t_first_gt_2e-4"]
        J["B2"] = ("HELD" if ok90 and (sep is None or sep > 130.0) else "FAILED")
        J["B2_note"] = f"max |dM| t<=90: {p['max_abs_t_le_90']}; first |dM|>2e-4 at {sep}"
    if E and "radius_199.5" in E:
        J["B3"] = "HELD" if abs(E["radius_199.5"] - 0.78) <= 0.05 else "FAILED"
    V = res["runs"].get("V-1GB")
    if V and V["drift"] and "D_199.5" in V["drift"]:
        d = V["drift"]
        J["C1"] = ("HELD" if d["D_100_end"][0] >= -6e-4 and d["D_100_end"][1] <= 1.0e-3
                   else "FAILED")
    if "ES-1GB-V-1GB" in res["pairs"]:
        p = res["pairs"]["ES-1GB-V-1GB"]
        mx = p["max_abs_30_end"]
        if mx is not None:
            J["C2"] = "HELD" if mx <= 2.5e-4 else ("REFUTED" if mx > 5e-4 else "FAILED")
    if V and "radius_199.5" in V and V["drift"]:
        okr = abs(V["radius_199.5"] - 0.78) <= 0.08
        okm = abs(V["drift"]["M_ref_minus_1"] - 1.1e-3) <= 2e-4
        J["C3"] = "HELD" if okr and okm else f"FAILED (radius {okr}, M(100) {okm})"

    json.dump(res, open(os.path.join(a.out, "compare_horizons.json"), "w"), indent=1)

    # ---- figure: (a) M_AH - 1, (b) drift from 100 M, (c) differences, (d) radius
    fs.use_style()
    col = {"ES-1G": fs.PAL["red"], "ES-1GB": fs.PAL["blue"], "V-1B": fs.PAL["green"],
           "V-1GB": fs.PAL["orange"], "V-1": fs.PAL["yellow"]}
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0), constrained_layout=True)
    for name, R in runs.items():
        c = col.get(name, "grey")
        ax[0, 0].plot(R["t"], R["m"] - 1.0, color=c, lw=1.2, label=name)
        dd = res["runs"][name]["drift"]
        if dd:
            w = R["t"] >= T0
            ax[0, 1].plot(R["t"][w], R["m"][w] - dd["M_ref"], color=c, lw=1.2, label=name)
        ax[1, 1].plot(R["t"], R["r"], color=c, lw=1.2, label=name)
    ax[0, 0].set_ylim(-2e-3, 1e-2)
    ax[0, 0].set_xlabel(r"$t/M$")
    ax[0, 0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    ax[0, 0].legend(loc="upper left", fontsize=7, frameon=False)
    ax[0, 0].set_title("(a) horizon mass", loc="left", fontsize=9)
    ax[0, 1].axhspan(-6e-4, 1e-3, color="grey", alpha=0.15, lw=0)
    ax[0, 1].axhline(3.5e-3, **fs.GUIDE)
    ax[0, 1].text(102, 3.7e-3, "refutation of B1", fontsize=7)
    ax[0, 1].set_xlabel(r"$t/M$")
    ax[0, 1].set_ylabel(r"$M_{\rm AH}(t) - M_{\rm AH}(100\,M)$")
    ax[0, 1].set_title("(b) drift from 100 M; band: B1, C1", loc="left", fontsize=9)
    for lab, pr, c in (("ES-1GB - ES-1G", p_es, fs.PAL["red"]),
                       ("ES-1GB - V-1GB (null test)", p_null, fs.PAL["blue"]),
                       ("V-1GB - V-1B (gauge)", p_v, fs.PAL["orange"])):
        if pr is not None:
            tc, d = pr
            ax[1, 0].plot(tc, np.abs(d) + 1e-17, color=c, lw=1.2, label=lab)
    ax[1, 0].set_yscale("log")
    ax[1, 0].axhline(2.5e-4, **fs.GUIDE)
    ax[1, 0].axhline(5e-5, color="k", lw=1.0, ls=":")
    ax[1, 0].set_ylim(1e-17, 3e-2)
    ax[1, 0].set_xlabel(r"$t/M$")
    ax[1, 0].set_ylabel(r"$|\Delta M_{\rm AH}|/M$")
    ax[1, 0].legend(loc="lower right", fontsize=7, frameon=False)
    ax[1, 0].set_title("(c) differences (dashed 2.5e-4: C2; dotted 5e-5: B2)", loc="left",
                       fontsize=9)
    ax[1, 1].axhspan(0.73, 0.83, color="grey", alpha=0.15, lw=0)
    ax[1, 1].set_xlabel(r"$t/M$")
    ax[1, 1].set_ylabel(r"mean coordinate radius $/M$")
    ax[1, 1].set_title("(d) horizon size; band: B3", loc="left", fontsize=9)
    for x in ax.flat:
        x.set_xlim(0, 200)
    fs.save(fig, os.path.join(a.out, "compare_horizons"))
    print(json.dumps(res["judgement"], indent=1))
    print(json.dumps({k: v["drift"] for k, v in res["runs"].items()}, indent=1))
    print(json.dumps(res["pairs"], indent=1))


if __name__ == "__main__":
    main()
