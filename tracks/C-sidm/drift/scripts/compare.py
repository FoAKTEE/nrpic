#!/usr/bin/env python3
"""Tests M8 and A of drift/JOURNAL.md entry 2: the controls on two meshes and to 1000 M.

    python3 compare.py --out DIR --tag NAME LABEL=MODEL:DIR[,DIR...] [LABEL=MODEL:DIR ...]
                       [--ratio LABEL_FINE/LABEL_COARSE ...]

LABEL is a free name (for example cc2_M4, cc2_M8, cc2_A1000), MODEL is cc1 or cc2 (it
selects the model files), DIR an AthenaK output directory; several directories are joined
in time order (controls.join_hst), so the wave-2 run and its continuation give one record
from 0 to 1000 M. Every series is analysed by controls.analyse (fits, radii, areal radii,
Killing-energy sum, ripple). --ratio a/b reports A(a)/A(b) and P(a)/P(b) of the cosine and
sine-with-trend fits and of the maximum of the 20 M mean. The extrema of the 40 M mean
(times and values) are listed for the continuation test A.2.

Writes DIR/compare_<tag>.json and DIR/fig_<tag>.png.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import controls as K  # noqa: E402

import numpy as np  # noqa: E402


def extrema(t, y, width=40.0, min_sep=120.0):
    """Local maxima and minima of the `width` running mean that are extreme over +-min_sep/2."""
    out = []
    ys = K.smooth(t, y, width)
    ok = np.isfinite(ys)
    dt = np.median(np.diff(t))
    h = max(1, int(round(0.5 * min_sep / dt)))
    for i in np.flatnonzero(ok):
        lo, hi = max(0, i - h), min(len(ys), i + h + 1)
        win = ys[lo:hi]
        win = win[np.isfinite(win)]
        if len(win) < h:
            continue
        if ys[i] == win.max() and i - lo >= h // 2 and hi - i > h // 2:
            out.append(("max", float(t[i]), float(ys[i])))
        elif ys[i] == win.min() and i - lo >= h // 2 and hi - i > h // 2:
            out.append(("min", float(t[i]), float(ys[i])))
    return out


def late_mean(t, v, t0, t1):
    w = (t >= t0) & (t <= t1)
    return float(np.mean(v[w])) if np.any(w) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("series", nargs="+")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ratio", action="append", default=[])
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    res, ser = {}, {}
    models = {}
    for spec in a.series:
        label, rest = spec.split("=", 1)
        mk, dirs = rest.split(":", 1)
        dirs = dirs.split(",")
        if mk not in models:
            models[mk] = K.C.load_model(K.MODEL_OF[mk])
        r, s = K.analyse(label, dirs, models[mk])
        r["model"] = mk
        r["extrema_40M_mean"] = extrema(s["t"], s["y"])
        r["H_norm2_mean_100_300"] = late_mean(s["zt"], s["Hn"], 100.0, 300.0)
        r["H_norm2_mean_300_1000"] = late_mean(s["zt"], s["Hn"], 300.0, 1000.0)
        r["alpha_min_grid_min"] = r.get("alpha_min_grid_min")
        res[label], ser[label] = r, s
        print(label, json.dumps({k: v for k, v in r.items() if not isinstance(v, (list, dict))}), flush=True)
        print(label, "fits", json.dumps(r["fits"]), flush=True)
        print(label, "extrema", json.dumps(r["extrema_40M_mean"]), flush=True)
    ratios = {}
    for rq in a.ratio:
        f, c = rq.split("/")
        rf, rc = res[f]["fits"], res[c]["fits"]
        out = {}
        for form in ("cos", "sin_trend"):
            if "A" in rf.get(form, {}) and "A" in rc.get(form, {}):
                out[f"A_{form}"] = rf[form]["A"] / rc[form]["A"]
                out[f"P_{form}"] = rf[form]["P"] / rc[form]["P"]
        out["max_20M_mean"] = res[f]["excursion_max_smoothed"] / res[c]["excursion_max_smoothed"]
        out["H_norm2_100_300"] = (res[f]["H_norm2_mean_100_300"] / res[c]["H_norm2_mean_100_300"]
                                  if res[f]["H_norm2_mean_100_300"] and res[c]["H_norm2_mean_100_300"] else None)
        out["H_norm2_t0"] = res[f]["H_norm2_0_max_end"][0] / res[c]["H_norm2_0_max_end"][0]
        out["ripple_rms"] = res[f]["ripple"].get("rms", np.nan) / res[c]["ripple"].get("rms", np.nan)
        # do the two series share their ripple? correlation of the residuals of their own
        # cosine fits on the common times (one realisation of the particles, same seed)
        sf, sc = ser[f], ser[c]
        if "P" in rf.get("cos", {}) and "P" in rc.get("cos", {}):
            t1 = min(sf["t"][-1], sc["t"][-1])
            tt = np.arange(0.0, t1 + 1e-9, 0.25)
            ef = np.interp(tt, sf["t"], sf["y"] - K.f_cos(sf["t"], rf["cos"]["A"], rf["cos"]["P"], rf["cos"]["c"]))
            ec = np.interp(tt, sc["t"], sc["y"] - K.f_cos(sc["t"], rc["cos"]["A"], rc["cos"]["P"], rc["cos"]["c"]))
            out["residual_correlation"] = float(np.corrcoef(ef, ec)[0, 1])
        ratios[rq] = out
        print("ratio", rq, json.dumps(out), flush=True)
    res["_ratios"] = ratios
    with open(os.path.join(a.out, f"compare_{a.tag}.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=float)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = fs.SERIES
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.28, hspace=0.1)
    for j, (label, s) in enumerate(ser.items()):
        c = cols[j % len(cols)]
        fc = res[label]["fits"].get("cos", {})
        axs[0, 0].plot(s["t"], s["y"], color=c, lw=0.5, alpha=0.4)
        lab = label + (f": A = {fc['A']:.4f}, P = {fc['P']:.0f} M" if "P" in fc else "")
        axs[0, 0].plot(s["t"], s["ys"], color=c, lw=1.4, label=lab)
        if "P" in fc:
            axs[0, 0].plot(s["t"], K.f_cos(s["t"], fc["A"], fc["P"], fc["c"]), color=c, ls="--", lw=0.9)
        if len(s["tr"]) > 1:
            axs[0, 1].plot(s["tr"], s["ra"][:, 1] / s["ra"][0, 1] - 1, color=c, lw=1.2, marker=".")
        axs[1, 0].plot(s["zt"], s["Hn"], color=c, lw=1.0)
        axs[1, 1].plot(s["t"], s["meanW"] - s["meanW"][0], color=c, lw=1.0)
    axs[0, 0].axhline(0.0, **fs.MASK_LINE)
    axs[0, 0].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$ (thick: 20 M mean)")
    axs[0, 0].legend(fontsize=6, loc="best", frameon=False)
    axs[0, 1].axhline(0.0, **fs.MASK_LINE)
    axs[0, 1].set_ylabel(r"areal radius of the 50 % shell / initial $-1$")
    axs[1, 0].set_yscale("log")
    axs[1, 0].set_ylabel(r"$\|H\|_2^2$")
    axs[1, 1].axhline(0.0, **fs.MASK_LINE)
    axs[1, 1].set_ylabel(r"$\Sigma mW/\Sigma m$ $-$ initial")
    for ax in axs[1]:
        ax.set_xlabel(r"$t/M$")
    fs.save(fig, os.path.join(a.out, f"fig_{a.tag}"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
