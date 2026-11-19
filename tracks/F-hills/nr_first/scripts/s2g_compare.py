#!/usr/bin/env python3
"""E10 of nr_first/JOURNAL.md: S2g (mass-scaled shift damping) against S3 (eta m = 2) and
S2 (eta m = 0.25) on their common times, with the criteria written in E10 before the run.

Per run: tracker speed ratio f = v_x / (P / M_ADM) (as single_analysis.py), smoothed over
1 m; horizon masses of the good searches only (found, i.e. not a repeated row, and hrms below
1e-3: the t = 0.5 searches of S3 and S2 converged in mass to surfaces with hrms 0.02, E4 rerun);
window medians; the constraint norm; the junk energy (from single_analysis.py's method).
Settling time t_s: the first time after which the smoothed f stays within 5 percent of its
mean over the last 2 m of the run (for a run that is still accelerating at its end this is
close to the end).
Usage: s2g_compare.py <out | - for $NRPIC_RUN_DIR> <run dir>... (names S3, S2, S2g taken
from the directory names; a missing run leaves its checks as "no data").
Writes s2g_compare.json and fig_s2g_compare.{png,pdf}.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
from nrpic import bowen_york as by  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

P, MBARE = 0.25, 1.0
HRMS_GOOD = 1e-3
WINDOWS = ((4, 6), (12, 14), (17, 22), (40, 50), (80, 90))
COL = {"S2": fs.PAL["red"], "S3": fs.PAL["yellow"], "S2g": fs.PAL["green"]}
DESC = {"S2": r"S2: $\eta m=0.25$", "S3": r"S3: $\eta m=2$",
        "S2g": r"S2g: $\eta m=2$ at the hole, $0.25$ far"}


def smooth(t, y, width=1.0):
    dt = np.median(np.diff(t))
    n = max(1, int(round(width / dt)))
    k = np.ones(n) / n
    ys = np.convolve(y, k, mode="same")
    ys[: n // 2] = np.nan
    ys[len(ys) - n // 2:] = np.nan
    return ys


def wmed(t, y, a, b):
    s = (t >= a) & (t <= b)
    return float(np.median(y[s])) if np.any(s) else math.nan


def load(rd, vb):
    trk = nr.read_trackers(rd)[0]
    hz, nmiss = nr.read_horizons(rd)[0]
    hst = nr.read_hst([os.path.join(rd, f) for f in os.listdir(rd)
                       if f.endswith(".z4c.user.hst")][0])
    t, x, v = trk["t"], trk["x"][:, 0], trk["v"][:, 0]
    f = v / vb
    fs_ = smooth(t, f)
    good = hz["hrms"] < HRMS_GOOD
    th, mh = hz["t"][good], hz["mass"][good]
    late = (t >= t[-1] - 2.0) & np.isfinite(fs_)
    f_late = float(np.nanmean(fs_[late]))
    off = np.abs(fs_ - f_late) > 0.05 * f_late
    idx = np.where(off & np.isfinite(fs_))[0]
    t_s = float(t[idx[-1] + 1]) if len(idx) and idx[-1] + 1 < len(t) else float(t[0])
    d = dict(t=t, f=f, fs=fs_, th=th, mh=mh, th_all=hz["t"], nmiss=nmiss,
             n_bad=int(np.sum(~good)), hst=hst)
    e = dict(t_end=float(t[-1]), f_late=f_late, t_settle=t_s,
             f_win={f"{a}-{b}": wmed(t, f, a, b) for a, b in
                    ((5, 10), (10, 14), (10, 20), (20, 22), (30, 40), (60, 90))},
             m_win={f"{a}-{b}": wmed(th, mh, a, b) for a, b in WINDOWS},
             first_good=(float(th[0]), float(mh[0])) if len(th) else None,
             searches=int(len(hz["t"]) + nmiss), missed=int(nmiss),
             found_bad_hrms=int(np.sum(~good)),
             missed_after_4=int(np.sum(hz["t"][~good] >= 4.0)),
             S_max=float(np.max(np.abs(hz["S"]))) if len(hz["S"]) else math.nan)
    th_ = hst["time"]
    H = np.sqrt(hst["H2"])
    e["H"] = dict(H_t0=float(H[0]), max_after_10=float(H[th_ >= 10].max()) if np.any(th_ >= 10)
                  else math.nan, min_after_10=float(H[th_ >= 10].min()) if np.any(th_ >= 10)
                  else math.nan,
                  growth_after_20=float(H[th_ >= 20].max() / H[th_ >= 20][0])
                  if np.any(th_ >= 20) else math.nan,
                  nonfinite=int(np.sum(~np.isfinite(H))))
    return d, e


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    m_adm2 = by.adm_mass_approx(MBARE, P)
    vb = P / m_adm2
    data, res = {}, {"v_boost": vb, "hrms_good": HRMS_GOOD, "runs": {}}
    for rd in sys.argv[2:]:
        name = os.path.basename(os.path.normpath(rd))
        d, e = load(rd, vb)
        data[name], res["runs"][name] = d, e
        print(name, json.dumps(e, indent=1), flush=True)

    # comparisons on common times: is S2g between S3 and S2 (smoothed f), window by window
    chk = {}

    def between(a, lo, hi, t0, t1, width=2.0):
        """on every 2 m window inside [t0, t1]: lo < a < hi for the window means"""
        if any(k not in data for k in (a, lo, hi)):
            return None
        tt = data[a]["t"]
        tmax = min(t1, data[a]["t"][-1], data[lo]["t"][-1], data[hi]["t"][-1])
        ok, worst = True, []
        for w0 in np.arange(t0, tmax - width + 1e-9, width):
            fa = wmed(tt, data[a]["f"], w0, w0 + width)
            fl = wmed(data[lo]["t"], data[lo]["f"], w0, w0 + width)
            fh = wmed(data[hi]["t"], data[hi]["f"], w0, w0 + width)
            worst.append((float(w0), fl, fa, fh))
            ok &= (fl < fa < fh)
        return dict(ok=bool(ok), windows=worst)

    if "S2g" in data:
        e = res["runs"]["S2g"]
        chk["1a between S3 and S2, t = 5-14"] = between("S2g", "S3", "S2", 5.0, 14.0)
        b = between("S2g", "S3", "S2", 5.0, 22.0) if "S2" in data else None
        chk["1a' between S3 and S2 up to 22 (S2 ends at 14)"] = b
        if "S3" in data:
            ok, ws = True, []
            for w0 in np.arange(5.0, min(22.0, data["S3"]["t"][-1]) - 2 + 1e-9, 2.0):
                fa = wmed(data["S2g"]["t"], data["S2g"]["f"], w0, w0 + 2)
                f3 = wmed(data["S3"]["t"], data["S3"]["f"], w0, w0 + 2)
                ws.append((float(w0), f3, fa))
                ok &= fa > f3
            chk["1b above S3, t = 5-22"] = dict(ok=bool(ok), windows=ws)
        f1020 = e["f_win"]["10-20"]
        chk["1c f(10-20) in 0.50-0.65"] = dict(ok=bool(0.50 <= f1020 <= 0.65), value=f1020)
        f3040 = e["f_win"]["30-40"]
        chk["1d f(30-40) > f(10-20)"] = dict(ok=bool(f3040 > f1020), value=f3040)
        f6090 = e["f_win"]["60-90"]
        chk["1e f(60-90) in 0.6-0.9"] = dict(ok=bool(0.6 <= f6090 <= 0.9), value=f6090)
        fg = e["first_good"]
        chk["2a first good search mass in 1.006-1.010"] = dict(
            ok=bool(fg is not None and 1.006 <= fg[1] <= 1.010), value=fg)
        if "S3" in data:
            dm = {}
            okm = True
            for w in ("4-6", "12-14", "17-22"):
                a, b3 = e["m_win"][w], res["runs"]["S3"]["m_win"][w]
                dm[w] = a - b3 if np.isfinite(a) and np.isfinite(b3) else math.nan
                okm &= bool(np.isfinite(dm[w]) and abs(dm[w]) < 5e-4)
            chk["2b medians within 5e-4 of S3 (4-6, 12-14, 17-22)"] = dict(ok=bool(okm), diff=dm)
            chk["2b' refuted if a median differs from S3 by more than 1e-3"] = dict(
                refuted=bool(any(np.isfinite(v) and abs(v) > 1e-3 for v in dm.values())))
        dr = e["m_win"]["12-14"] / e["m_win"]["4-6"] - 1
        chk["2c drift 4-6 -> 12-14 in +2.5e-4 .. +1.3e-3"] = dict(
            ok=bool(2.5e-4 <= dr <= 1.3e-3), value=dr)
        dr90 = e["m_win"]["80-90"] / e["m_win"]["4-6"] - 1
        chk["2d drift 4-6 -> 80-90 in 0.2-3 percent"] = dict(
            ok=bool(2e-3 <= dr90 <= 3e-2), value=dr90)
        chk["2e spin below 1e-3"] = dict(ok=bool(e["S_max"] < 1e-3), value=e["S_max"])
        h = e["H"]
        chk["4 H in 3e-5..1e-4 after t = 10, growth after 20 below 10"] = dict(
            ok=bool(h["min_after_10"] >= 3e-5 and h["max_after_10"] <= 1e-4
                    and h["growth_after_20"] < 10), value=h)
        chk["5 reaches t = 90, no non-finite, every search after t = 4 good"] = dict(
            ok=bool(e["t_end"] >= 89.9 and h["nonfinite"] == 0 and e["missed_after_4"] == 0),
            t_end=e["t_end"], nonfinite=h["nonfinite"], bad_after_4=e["missed_after_4"])
    # common-window comparison of S2 and S3 (no criterion, the reference numbers of E10)
    if "S2" in data and "S3" in data:
        r2, r3 = res["runs"]["S2"], res["runs"]["S3"]
        res["S2_vs_S3"] = dict(
            drift_4_6_to_12_14={n: res["runs"][n]["m_win"]["12-14"] / res["runs"][n]["m_win"]["4-6"]
                                - 1 for n in ("S2", "S3")},
            f_10_14={"S2": r2["f_win"]["10-14"], "S3": r3["f_win"]["10-14"]})
    res["checks"] = chk
    for k, v in chk.items():
        if v is None:
            print("NO DATA", k)
        elif "ok" in v:
            print("PASS" if v["ok"] else "FAIL", k)
        else:
            print("INFO", k, v)
    with open(os.path.join(out, "s2g_compare.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    for name, d in data.items():
        c = COL.get(name, "k")
        ax[0, 0].plot(d["t"], d["fs"], color=c, lw=1.1, label=DESC.get(name, name))
        e = res["runs"][name]
        ax[0, 0].axvline(e["t_settle"], color=c, lw=0.6, ls=":")
        ax[1, 0].plot(d["th"], d["mh"] - 1.0, "o-", color=c, ms=2, lw=0.8)
        for w in WINDOWS:
            v = e["m_win"][f"{w[0]}-{w[1]}"]
            if np.isfinite(v):
                ax[1, 0].plot(w, [v - 1.0] * 2, color=c, lw=2.5, alpha=0.6)
        ax[1, 1].semilogy(d["hst"]["time"], np.sqrt(d["hst"]["H2"]), color=c, lw=1.0)
    if "S3" in data:
        for name in ("S2", "S2g"):
            if name in data:
                t3, f3 = data["S3"]["t"], data["S3"]["fs"]
                tn, fn = data[name]["t"], data[name]["fs"]
                tm = min(t3[-1], tn[-1])
                tt = np.linspace(2.0, tm, 400)
                ax[0, 1].plot(tt, np.interp(tt, tn, fn) / np.interp(tt, t3, f3),
                              color=COL[name], lw=1.1, label=f"{name} / S3")
    ax[0, 1].axhline(1.27, **fs.REF_LINE)
    ax[0, 1].text(0.98, 0.04, "grey: core's E1, profile / constant ($\\eta m$ = 0.2 far)",
                  transform=ax[0, 1].transAxes, ha="right", fontsize=7)
    ax[0, 0].set_ylabel(r"$f = v_{\rm tracker}/(P/M_{\rm ADM})$, 1 $m$ mean")
    ax[0, 0].legend(frameon=False, fontsize=7, loc="lower right")
    ax[0, 0].set_title("dotted: settling time (within 5 percent of the last 2 m)", fontsize=8)
    ax[0, 1].set_ylabel("speed ratio to S3")
    ax[0, 1].legend(frameon=False, fontsize=7)
    ax[1, 0].set_ylabel(r"$M_{\rm AH}/m - 1$ (hrms $<10^{-3}$); bars: medians")
    ax[1, 1].set_ylabel(r"$\langle H^2\rangle^{1/2}$")
    tmax = max(d["t"][-1] for d in data.values())
    for a in ax.ravel():
        a.set_xlabel(r"$t\,[m]$")
        a.set_xlim(0, max(25.0, tmax))
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_s2g_compare")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
