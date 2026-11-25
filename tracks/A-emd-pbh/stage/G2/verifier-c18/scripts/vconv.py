"""Recompute the conv_ball claims (README table) from the raw outputs with the verifier's
readers. Usage: python -I vconv.py --out DIR [--member NAME ...]"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import figstyle as fs
import matplotlib.pyplot as plt
from vmembers import CONV, table_of, member_args
from vmeasure import Member, bh_rule

# conv_ball/README.md result table (claims), in its units
CLAIM = {
    "A": (10.875, 0.193, -0.093, 7.4e-3), "B": (10.781, 0.068, -0.022, -2.1e-3),
    "C": (10.750, 0.017, -0.0077, -2.1e-4), "A-N8": (10.813, 0.109, -0.047, -1.3e-3),
    "A-N64": (10.812, 0.146, -0.048, 5.0e-4), "B-N8": (10.750, 0.071, -0.028, -3.0e-4),
    "A-R1.25": (10.906, 0.100, -0.049, 6.7e-3), "A-R1.35": (10.938, 0.164, -0.029, 1.0e-2),
    "B-R1.25": (10.750, 0.065, -0.015, -1.9e-3), "B-R1.35": (10.750, 0.107, -0.008, -1.25e-3),
}
HF = {"A": 1 / 16, "B": 1 / 32, "C": 1 / 64}


def analyse(name, d):
    m = Member(d, table_of(d))
    rule = bh_rule(m.summ)
    dd = m.ddet()
    dt = m.dtrap()
    ms = m.masses()          # t, mirr, m*, lo, hi, label, gap
    dm = ms[:, 1] / ms[:, 2] - 1
    ok = np.isfinite(dm)
    dm_lo = ms[:, 1] / ms[:, 4] - 1   # against the upper-bound mass (next band)
    dm_hi = ms[:, 1] / ms[:, 3] - 1   # against the lower-bound mass (last trapped band)
    res = {"dir": d, "table": table_of(d), "n_track": int(m.tr.tag.size),
           "rule": rule, "ddet": dd, "dtrap": dt,
           "dm_first": float(dm[0]) if ok[0] else None,
           "dm_median": float(np.median(dm[ok])) if ok.any() else None,
           "dm_median_bounds": [float(np.nanmedian(dm_lo[ok])), float(np.nanmedian(dm_hi[ok]))] if ok.any() else None,
           "n_det": int(ms.shape[0]), "n_det_with_exact": int(ok.sum()),
           "window": [float(ms[ok, 0].min()), float(ms[ok, 0].max())] if ok.any() else None,
           "gap_median": float(np.nanmedian(ms[ok, 6])) if ok.any() else None}
    series = {"t": ms[:, 0], "mirr": ms[:, 1], "mex": ms[:, 2], "mlo": ms[:, 3], "mhi": ms[:, 4]}
    return res, series


def order(e1, e2):
    return float(np.log2(abs(e1) / abs(e2))) if e1 and e2 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    names = a.member or list(CONV)
    res, ser = {}, {}
    for n in names:
        res[n], ser[n] = analyse(n, CONV[n])
        r = res[n]
        print("%-8s t1 %.4f ddet v1 %+.4f v2 %+.4f v3 %+.4f dtrap %+.4f dm1 %s dmmed %s n %d/%d gap %s" % (
            n, r["ddet"]["t"], r["ddet"]["ddet_v1"], r["ddet"]["ddet_v2"], r["ddet"]["ddet_v3"], r["dtrap"]["dtrap_mean"],
            r["dm_first"], r["dm_median"], r["n_det_with_exact"], r["n_det"], r["gap_median"]), flush=True)
    # comparison with the claims
    cmp = {}
    for n, r in res.items():
        if n in CLAIM:
            c = CLAIM[n]
            cmp[n] = {"t1": [c[0], r["ddet"]["t"]], "ddet": [c[1], r["ddet"]["ddet_v1"], r["ddet"]["ddet_v2"], r["ddet"]["ddet_v3"]],
                      "dtrap": [c[2], r["dtrap"]["dtrap_mean"]], "dmmed": [c[3], r["dm_median"]]}
    orders = {}
    if all(k in res for k in ("A", "B", "C")):
        for q, f in (("ddet_v1", lambda r: r["ddet"]["ddet_v1"]), ("ddet_v2", lambda r: r["ddet"]["ddet_v2"]), ("ddet_v3", lambda r: r["ddet"]["ddet_v3"]),
                     ("dtrap", lambda r: r["dtrap"]["dtrap_mean"]), ("dmmed", lambda r: r["dm_median"])):
            e = [f(res[k]) for k in ("A", "B", "C")]
            orders[q] = {"A": e[0], "B": e[1], "C": e[2], "p_AB": order(e[0], e[1]), "p_BC": order(e[1], e[2])}
            if e[0] is not None and e[1] is not None and e[2] is not None and (e[0] - e[1]) * (e[1] - e[2]) > 0:
                orders[q]["p_self"] = float(np.log2(abs(e[0] - e[1]) / abs(e[1] - e[2])))
    out = {"members": res, "compare": cmp, "orders": orders}
    with open(os.path.join(a.out, "vconv.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    np.savez(os.path.join(a.out, "vconv_series.npz"), **{"%s__%s" % (n, k): v for n, s in ser.items() for k, v in s.items()})
    print(json.dumps({"orders": orders}, indent=1, default=float))

    # figures
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(8, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.9, wspace=0.38)
    for k, (lab, f, cl) in enumerate((
            (r"$|\Delta\tau_{\rm det}|$ (M)", lambda r: r["ddet"]["ddet_v2"], 1),
            (r"$|\Delta\tau_{\rm trap}|$ (M)", lambda r: r["dtrap"]["dtrap_mean"], 2),
            (r"$|m_{\rm AH}/m_{\rm exact}-1|$ median", lambda r: r["dm_median"], 3))):
        hs = [HF[n] for n in ("A", "B", "C") if n in res]
        ys = [abs(f(res[n])) for n in ("A", "B", "C") if n in res]
        ax[k].loglog(hs, ys, "o-", color=fs.PAL["red"], label="verifier, mesh A,B,C")
        cy = [abs(CLAIM[n][cl]) for n in ("A", "B", "C") if n in res]
        ax[k].loglog(hs, cy, "s", mfc="none", color=fs.PAL["blue"], label="README claim")
        for n, h, mk in (("A-N8", 1 / 16, "^"), ("A-N64", 1 / 16, "v"), ("B-N8", 1 / 32, "^")):
            if n in res and f(res[n]) is not None:
                ax[k].loglog([h * 1.06], [abs(f(res[n]))], mk, color=fs.PAL["yellow"], ms=5,
                             label="N legs (A-N8, A-N64, B-N8)" if n == "A-N8" else None)
        if ys:
            hh = np.array([1 / 16, 1 / 64])
            ax[k].loglog(hh, ys[0] * (hh / hh[0]) ** 2, color="k", ls="--", lw=1.0, label="order 2")
        ax[k].set_xlabel(r"finest cell $h_f$ (M)", labelpad=-1)
        ax[k].set_title(lab, fontsize=10)
    ax[0].legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(a.out, "fig_vconv_orders"))
    plt.close(fig)

    show = [n for n in ("A", "B", "C", "B-N8", "A-N64") if n in ser]
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.1))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.95, wspace=0.3)
    cols = fs.SERIES + ["k"]
    for i, n in enumerate(show):
        s = ser[n]
        ax[0].plot(s["t"], s["mirr"], color=cols[i % len(cols)], lw=1.0, label="%s finder" % n)
        ax[0].plot(s["t"], s["mex"], color=cols[i % len(cols)], lw=1.0, ls="--")
        ax[1].plot(s["t"], s["mirr"] / s["mex"] - 1, color=cols[i % len(cols)], lw=1.0, label=n)
    ax[0].set_xlabel("coordinate time $t$ (M)")
    ax[0].set_ylabel(r"$m$ (solid finder, dashed exact on slice)")
    ax[0].legend(fontsize=7)
    ax[1].axhline(0, color="grey", lw=0.8)
    ax[1].set_xlabel("coordinate time $t$ (M)")
    ax[1].set_ylabel(r"$m_{\rm AH}/m_{\rm exact} - 1$")
    ax[1].set_ylim(-0.02, 0.03)
    ax[1].legend(fontsize=7, ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_vconv_mass"))
    plt.close(fig)


if __name__ == "__main__":
    main()
