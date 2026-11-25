"""P8, P9 and the horizon scan: mesh members (binary alone at m/8, m/12, m/16; P1b at m/16 and
m/12), P1's merger and its remnant to 280 M, and horizon numbers of every card run of G1 by the
failure signature (no run has <fastflow> diagnostics: 'made without the diagnostics').

Run: python tracks/F-hills/stage/G1/verifier/scripts/vmesh.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vread  # noqa: E402
import vnewton  # noqa: E402
import figstyle  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
RUNS = {
    "P1": ["F-20261119-150017-b45ec5f"],
    "R8": ["F-20261121-130358-6cf186a"],
    "R12": ["F-20261121-153707-1eaa5d4"],
    "R16n": ["F-20261121-130351-04074e1", "F-20261121-203156-03efdd3"],  # R16n + B (from R16n's restart 7)
    "A": ["F-20261121-203144-b2cf16b", "F-20261124-210400-902c650"],     # A + A2
    "C": ["F-20261121-203247-961801d"],
}
HERE = os.path.dirname(os.path.abspath(__file__))
DECK_BIN = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "binary_conv", "inputs", "bin_m16.athinput"))


def sep_series(name):
    dirs = [os.path.join(SCR, r) for r in RUNS[name]]
    j0, ov0, sp0 = vread.joined_tracker(dirs, 0)
    j1, ov1, sp1 = vread.joined_tracker(dirs, 1)
    a0, a1 = vread.common_times(j0, j1)
    t = a0[:, 1]
    s = np.linalg.norm(a0[:, 2:5] - a1[:, 2:5], axis=1)
    g = vread.gaps(t)
    ovmax = max([o["max_dx"] for o in ov0 + ov1] or [0.0])
    return t, s, {"coverage": g, "n_files": len(sp0), "overlap_max_dx": ovmax}, (a0, a1)


def at(t, s, tq):
    if tq < t[0] or tq > t[-1]:
        return None
    return float(np.interp(tq, t, s))


def order3(f1, f2, f3, h1, h2, h3):
    """Order p from three members (coarse to fine) with f = f0 + C h^p."""
    r = (f1 - f2) / (f2 - f3)
    g = lambda p: (h1 ** p - h2 ** p) / (h2 ** p - h3 ** p) - r
    try:
        return float(brentq(g, 0.05, 40.0))
    except ValueError:
        return None


ALLROWS = {}


def horizon_scan(name, n, window):
    dirs = [os.path.join(SCR, r) for r in RUNS[name]]
    rows_t, rows_m, nfail, nraw, ntimes, ft = [], [], 0, 0, 0, []
    all_t, all_m = [], []
    for d in dirs:
        p = os.path.join(d, f"hills.horizon_summary_{n}.txt")
        if not os.path.exists(p):
            continue
        h = vread.read_horizon_summary(p)
        acc = ~h["failed"]
        rows_t.append(h["t"][acc]); rows_m.append(h["mass"][acc])
        all_t.append(h["t"]); all_m.append(h["mass"])
        nfail += int(h["failed"].sum()); nraw += h["n_raw"]; ntimes += len(h["t"])
        ft += h["t"][h["failed"]][:10].tolist()
    t = np.concatenate(rows_t); m = np.concatenate(rows_m)
    o = np.argsort(t, kind="stable"); t, m = t[o], m[o]
    # rows of a later run at times an earlier run also holds are both kept (they agree; see vpassage)
    med = float(np.median(m))
    w0, w1 = window
    sel = (t >= w0) & (t <= w1)
    fs = float(np.polyfit(t[sel], m[sel], 1)[0] / np.median(m[sel])) if sel.sum() > 3 else None
    ta_ = np.concatenate(all_t); ma_ = np.concatenate(all_m)
    o2 = np.argsort(ta_, kind="stable"); ta_, ma_ = ta_[o2], ma_[o2]
    fin = np.isfinite(ma_)
    ALLROWS[(name, n)] = (ta_[fin], ma_[fin])
    late = t > 1.0
    return {"n_raw": nraw, "n_times": ntimes, "n_failed": nfail, "failed_t": ft, "t_range": [float(t[0]), float(t[-1])],
            "median": med, "min": float(m.min()), "max": float(m.max()),
            "max_dev_from_median": float(np.abs(m / med - 1).max()),
            "max_dev_from_median_after_1M": float(np.abs(m[late] / med - 1).max()) if late.any() else None,
            "first3": m[:3].tolist(), "first3_t": t[:3].tolist(),
            "frac_slope_window": [w0, w1], "frac_slope": fs}, (t, m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = ap.parse_args().out
    os.makedirs(out, exist_ok=True)
    res = {"runs": RUNS}
    ser = {}
    for k in RUNS:
        t, s, info, raw = sep_series(k)
        ser[k] = (t, s, raw)
        info["s_at"] = {str(q): at(t, s, q) for q in (5.0, 7.5, 10.0, 15.0, 20.0, 22.0)}
        res[f"sep_{k}"] = info

    # Newton for the binary alone (deck bin_m16)
    mN, xN, vN = vnewton.deck_state(DECK_BIN)
    tn, X, V, _ = vnewton.integrate(mN, xN, vN, 110.0, dt_out=0.01)
    sN = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
    res["newton_binary"] = {"s_at": {str(q): at(tn, sN, q) for q in (5.0, 7.5, 10.0, 15.0, 20.0)},
                            "s_max_first": vread.minima(tn, -sN)[:2]}

    # convergence: binary alone, three members (cells m/8, m/12, m/16 -> h = 1/8, 1/12, 1/16)
    conv = {}
    for q in ("5.0", "7.5", "10.0", "15.0", "20.0"):
        f8, f12, f16 = (res[f"sep_{k}"]["s_at"][q] for k in ("R8", "R12", "R16n"))
        if None in (f8, f12, f16):
            conv[q] = None
            continue
        conv[q] = {"s8": f8, "s12": f12, "s16": f16, "s8-s16": f8 - f16, "s12-s16": f12 - f16,
                   "order_3member": order3(f8, f12, f16, 1 / 8, 1 / 12, 1 / 16)}
    res["convergence_binary_alone"] = conv
    # R12 against R16n, C against A: max |ds| on common span (interpolated onto the finer grid)
    def cmp(a, b):
        ta, sa = ser[a][0], ser[a][1]
        tb, sb = ser[b][0], ser[b][1]
        t0, t1 = max(ta[0], tb[0]), min(ta[-1], tb[-1])
        sel = (tb >= t0) & (tb <= t1)
        d = np.interp(tb[sel], ta, sa) - sb[sel]
        k = int(np.argmax(np.abs(d)))
        return {"span": [float(t0), float(t1)], "max_abs_ds": float(np.abs(d).max()), "t_at_max": float(tb[sel][k]),
                "ds_at_end": float(d[-1])}
    res["R12_vs_R16n"] = cmp("R12", "R16n")
    res["R8_vs_R16n"] = cmp("R8", "R16n")
    res["C_vs_A"] = cmp("C", "A")
    res["P1_vs_R8"] = cmp("P1", "R8")

    # P1: merger and remnant
    tP, sP, (p0, p1) = ser["P1"]
    k = int(np.argmax(sP < 0.1))
    dP = os.path.join(SCR, RUNS["P1"][0])
    jM, _, _ = vread.joined_tracker([dP], 2)
    q0, q1, qM = vread.common_times(p0, p1, jM)
    tq = q0[:, 1]
    rem = 0.5 * (q0[:, 2:5] + q1[:, 2:5])
    dRM = np.linalg.norm(rem - qM[:, 2:5], axis=1)
    after = tq > 60
    mins = [mm for mm in vread.minima(tq[after], dRM[after])]
    hzP = {}
    for n in (0, 1, 2):
        h = vread.read_horizon_summary(os.path.join(dP, f"hills.horizon_summary_{n}.txt"))
        acc = ~h["failed"]
        first = np.where(acc & (h["mass"] > 0.2))[0]
        hzP[str(n)] = {"first_above_0.2": [float(h["t"][first[0]]), float(h["mass"][first[0]])] if len(first) else None,
                       "n_failed": int(h["failed"].sum()), "n_times": int(len(h["t"]))}
        if n == 0:
            tt, mm_ = h["t"][acc], h["mass"][acc]
            def med(a, b):
                s_ = (tt >= a) & (tt < b)
                return float(np.median(mm_[s_])) if s_.any() else None
            hzP["remnant_median_by_window"] = {f"{a}-{b}": med(a, b) for a, b in ((50, 60), (60, 100), (100, 140), (140, 200), (200, 240), (240, 280))}
            m60, m280 = med(60, 100), med(240, 280.1)
            hzP["remnant_change_60_280_frac"] = (m280 - m60) / m60 if m60 and m280 else None
        if n == 2:
            tt, mm_ = h["t"][acc], h["mass"][acc]
            def med2(a, b):
                s_ = (tt >= a) & (tt < b)
                return float(np.median(mm_[s_])) if s_.any() else None
            hzP["heavy_median_by_window"] = {f"{a}-{b}": med2(a, b) for a, b in ((1, 20), (20, 60), (60, 112), (112, 200), (240, 280.1))}
    hP, _ = vread.read_hst(os.path.join(dP, "hills.z4c.user.hst"))
    rmsP = np.sqrt(hP["H-norm2"] / hP["Volume"])
    def rms_at(tq):
        kk = int(np.argmin(np.abs(hP["time"] - tq)))
        return [float(hP["time"][kk]), float(rmsP[kk])]
    h2 = vread.read_horizon_summary(os.path.join(dP, "hills.horizon_summary_2.txt"))
    k4 = int(np.argmin(np.abs(h2["t"] - 4.0)))
    kcm = int(np.argmin(np.abs(tq - 48.8125)))
    sel280 = tq >= 275
    ledger = {"row200_dist_common_horizon_to_M_at_48.8125": float(np.linalg.norm(q0[kcm, 2:5] - qM[kcm, 2:5])),
              "row201_rate_at_280": float(np.polyfit(tq[sel280], dRM[sel280], 1)[0]),
              "row205_heavy_at_4": [float(h2["t"][k4]), float(h2["mass"][k4]), bool(h2["failed"][k4])],
              "row207_rmsH_at_1_112_280": [rms_at(1.0), rms_at(112.0), rms_at(280.0)],
              "row207_rmsH_max_112_280": float(rmsP[(hP["time"] >= 112)].max())}
    res["P1_ledger"] = ledger
    res["P1"] = {"sep_below_0.1_first_t": float(tP[k]) if (sP < 0.1).any() else None,
                 "remnant_minima_after_60": mins[:5],
                 "remnant_d_at": {str(q): float(np.interp(q, tq, dRM)) for q in (112, 120, 140, 160, 200, 240, 280)},
                 "t_end": float(tq[-1]), "horizons": hzP,
                 "rmsH_range_after_1M": [float(rmsP[hP["time"] > 1].min()), float(rmsP[hP["time"] > 1].max())],
                 "rmsH_range_60_280": [float(rmsP[(hP["time"] >= 60)].min()), float(rmsP[(hP["time"] >= 60)].max())]}

    # horizon scan (H1-H4 of the owner's batch 21), every run of G1 with a finder
    scan = {}
    win = {"P1": (10, 45), "R8": (10, 21), "R12": (5, 21), "R16n": (10, 100), "A": (20, 95), "C": (5, 22.3)}
    curves = {}
    for k in RUNS:
        for n in (0, 1, 2):
            p = os.path.join(SCR, RUNS[k][0], f"hills.horizon_summary_{n}.txt")
            if not os.path.exists(p):
                continue
            w = win[k] if n < 2 else (1, 1e9)
            if k == "P1" and n < 2:
                w = (10, 45)
            info, cur = horizon_scan(k, n, w)
            scan[f"{k}_{n}"] = info
            curves[f"{k}_{n}"] = cur
    # member drifts (fraction of the window's median per M, accepted rows) in the windows the owner
    # names for H2 (b21_horizon_recheck.py lines 146-149) and in a few more
    wins = {"P1": [(10, 40), (1, 21), (10, 21), (1, 45)], "R8": [(10, 21), (1, 21)], "R12": [(3, 15), (10, 21)],
            "R16n": [(23, 60), (60, 108)], "A": [(15, 40), (40, 62), (65, 95)], "C": [(15, 22.3), (5, 22.3)]}
    drift = {}
    for k, wl in wins.items():
        for n in (0, 1):
            tt, mm_ = curves[f"{k}_{n}"]
            for w0, w1 in wl:
                sel = (tt >= w0) & (tt <= w1)
                drift[f"{k}_{n} {w0}-{w1}"] = float(np.polyfit(tt[sel], mm_[sel], 1)[0] / np.median(mm_[sel]))
                ta_, ma_ = ALLROWS[(k, n)]
                sa = (ta_ >= w0) & (ta_ <= w1)
                drift[f"{k}_{n} {w0}-{w1} all rows"] = float(np.polyfit(ta_[sa], ma_[sa], 1)[0] / np.median(ma_[sa]))
    res["member_drift_per_M"] = drift
    res["horizon_scan"] = scan

    # figures
    figstyle.use_style()
    import matplotlib.pyplot as plt
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.97, wspace=0.3, hspace=0.3)
    a = ax[0, 0]
    a.plot(tn[tn <= 25], sN[tn <= 25], **figstyle.GUIDE, label="Newton, binary alone")
    for kk, col in (("R8", P["yellow"]), ("R12", P["green"]), ("R16n", P["red"]), ("P1", P["orange"]),
                    ("A", P["blue"]), ("C", "grey")):
        tt, ss = ser[kk][0], ser[kk][1]
        sel = tt <= 25
        a.plot(tt[sel], ss[sel], color=col, lw=1.0, label=kk)
    a.set_xlabel("t [M]"); a.set_ylabel("pair separation s"); a.legend(fontsize=7, ncol=2, loc="lower left")
    a = ax[0, 1]
    for kk, col in (("R8", P["yellow"]), ("R12", P["green"])):
        tt, ss = ser[kk][0], ser[kk][1]
        t16, s16 = ser["R16n"][0], ser["R16n"][1]
        sel = (tt >= t16[0]) & (tt <= min(t16[-1], 25))
        a.plot(tt[sel], np.interp(tt[sel], t16, s16) - ss[sel], color=col, lw=1.0, label=f"R16n - {kk}")
    tt, ss = ser["C"][0], ser["C"][1]
    tA, sA = ser["A"][0], ser["A"][1]
    sel = tt <= tA[-1]
    a.plot(tt[sel], np.interp(tt[sel], tA, sA) - ss[sel], color="grey", lw=1.0, label="A - C (P1b)")
    a.axhline(0, **figstyle.THIN)
    a.set_xlabel("t [M]"); a.set_ylabel("separation difference"); a.legend(fontsize=8)
    a = ax[1, 0]
    a.plot(tq, dRM, color=P["red"], label="P1 remnant to M")
    for mm in mins:
        a.plot(mm[0], mm[1], "o", color="k", ms=4)
    a.set_xlabel("t [M]"); a.set_ylabel("coordinate distance"); a.legend(fontsize=8)
    a = ax[1, 1]
    for key, col in (("P1_0", P["orange"]), ("R8_0", P["yellow"]), ("R12_0", P["green"]), ("R16n_0", P["red"]),
                     ("A_0", P["blue"]), ("C_0", "grey")):
        tt, mm_ = curves[key]
        sel = tt <= 47
        a.plot(tt[sel], mm_[sel] / np.median(mm_[sel]) - 1, color=col, lw=0.8, label=key)
    a.set_xlabel("t [M]"); a.set_ylabel("m_AH / median - 1 (finder 0)"); a.legend(fontsize=7, ncol=2)
    figstyle.save(fig, os.path.join(out, "fig_v_mesh"))
    with open(os.path.join(out, "vmesh.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)


if __name__ == "__main__":
    main()
