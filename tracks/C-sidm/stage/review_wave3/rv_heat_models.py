"""Lead's wave-3 recheck L21 (heat) and L22 (models) of C-sidm, batch 2b.

L21: from the per-seed T7 values of the heat package (results/cardcpu_C-20261120-223203-b38a7d7.json,
written by the heat analyses), recompute with own code (a) each row's particle-number-weighted
mean f_w, (b) the weighted extrapolation f(k lambda) = f0 + b (k lambda)^2 to k lambda -> 0, for
theta = 0.003, 0.1, 1, and compare with the package's numbers and with the Chapman-Enskog
references of verify_g1 V1a as summary_c6 quotes them.
L22: figures of the models package's validation runs (npz of C-20261120-222716-9d86ebc and
C-20261120-223404-40668db), which the package did not draw: (a) distribution of the v2 rate
estimates on synthetic signals, v2 reference against 'first', relative to the true rate;
(b) ln|d| of the three compensated y_c = 0.5 runs with the common interval and the local slope.
Predictions: tracks/C-sidm/JOURNAL.md 2026-11-21T07:51Z.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
HEAT = os.path.join(WT, "tracks", "C-sidm", "heat", "results")


def wls_quad(x, y, se):
    X = np.column_stack([np.ones_like(x), x ** 2])
    W = 1.0 / se ** 2
    A = X.T @ (X * W[:, None])
    coef = np.linalg.solve(A, X.T @ (W * y))
    cov = np.linalg.inv(A)
    chi2 = float(np.sum(W * (y - X @ coef) ** 2))
    return float(coef[0]), float(math.sqrt(cov[0, 0])), float(coef[1]), chi2


def heat(out):
    cc = json.load(open(os.path.join(HEAT, "cardcpu_C-20261120-223203-b38a7d7.json")))
    sm = json.load(open(os.path.join(HEAT, "summary_c6_C-20261121-030328-e3ffc6d.json")))
    res = {}
    for g, v in cc["groups"].items():
        rows = []
        for r in v["rows"]:
            f = np.array([s["f"] for s in r["seeds"]])
            n = np.array([s["N"] for s in r["seeds"]], float)
            fw = float(np.sum(n * f) / np.sum(n))
            rows.append(dict(k_lambda=r["k_lambda"], f_w_own=fw, f_w_pkg=r["f_w"],
                             diff=fw - r["f_w"], se_pkg=r["f_w_se"], n_seeds=len(f)))
        x = np.array([r["k_lambda"] for r in rows])
        y = np.array([r["f_w_own"] for r in rows])
        se = np.array([r["se_pkg"] for r in rows])
        f0, f0se, b, chi2 = wls_quad(x, y, se)
        e = v["extrapolation_weighted"]
        res[g] = dict(theta=v["theta"], rows=rows, f0_own=f0, f0_se_own=f0se, b_own=b,
                      chi2_own=chi2, f0_pkg=e["f0"], f0_se_pkg=e["f0_se"], diff_f0=f0 - e["f0"])
    res["ce_reference"] = sm["ce_reference"]
    return res


def models(out):
    v = np.load(os.path.join(SCR, "C-20261120-222716-9d86ebc", "growth_v2_figdata.npz"))
    dg = np.load(os.path.join(SCR, "C-20261120-223404-40668db", "diag_v2_figdata.npz"))
    vj = json.load(open(os.path.join(SCR, "C-20261120-222716-9d86ebc", "growth_validation_v2.json")))
    dj = json.load(open(os.path.join(SCR, "C-20261120-223404-40668db", "diag_v2.json")))
    res = dict(syn={})
    for s in ("0.02", "0.05", "0.1"):
        fits = v[f"syn_{s}_v2_fits"]
        first = v[f"syn_{s}_v2_first_fits"]
        old = v[f"old_syn_{s}_fits"]
        res["syn"][s] = dict(v2_median=float(np.median(fits)), first_median=float(np.median(first)),
                             old_median=float(np.median(old)), v2_sd=float(np.std(fits)),
                             n=int(len(fits)))
    res["common"] = dg["common"].tolist()
    return res, v, dg, vj, dj


def figures(hres, v, dg, vj, out):
    sys.path.insert(0, os.path.join(WT, "python"))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    # heat
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 3.4))
    ce = hres["ce_reference"]
    for ax, (g, key) in zip(axs, [("T7_th0.003_e0.2", "0.003"), ("T7_th0.1_e0.2", "0.1"),
                                  ("T7_th1_e0.2", "1.0")]):
        r = hres[g]
        x = np.array([q["k_lambda"] for q in r["rows"]])
        y = np.array([q["f_w_own"] for q in r["rows"]])
        se = np.array([q["se_pkg"] for q in r["rows"]])
        ax.errorbar(x ** 2, y, yerr=se, fmt="o", color=fs.SERIES[0], ms=5, capsize=2,
                    label="rows (N-weighted)")
        xx = np.linspace(0, 0.17, 50)
        ax.plot(xx, r["f0_own"] + r["b_own"] * xx, **fs.REF_LINE, label="weighted fit")
        ax.errorbar([0], [r["f0_own"]], yerr=[r["f0_se_own"]], fmt="s", color=fs.SERIES[1], ms=5,
                    capsize=2, label=r"$k\lambda\to0$")
        c4 = ce[key]["order4"]
        c1 = ce[key]["order1"]
        ax.axhline(c4, **fs.GUIDE)
        ax.axhline(c1, **fs.MASK_LINE)
        ax.set_xlabel(r"$(k\lambda)^2$")
        ax.set_ylabel(r"$\kappa/\kappa_1$")
        ax.set_title(rf"$\theta={key}$ (dashed: CE order 4; grey: order 1)")
        if key == "0.003":
            ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "rv_heat"))
    # models
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 3.4))
    ax = axs[0]
    truth = vj.get("G2p", {}) if isinstance(vj, dict) else {}
    for k, s in enumerate(("0.02", "0.05", "0.1")):
        sig = float(s)
        for arr, mk, lab in ((v[f"syn_{s}_v2_fits"], "o", "v2"), (v[f"syn_{s}_v2_first_fits"], "x", "first")):
            rel = arr / sig - 1.0
            ax.plot(np.full(len(rel), k) + (0.12 if mk == "x" else -0.12), 100 * rel, mk,
                    color=fs.SERIES[0 if mk == "o" else 1], ms=3, alpha=0.6,
                    label=lab if k == 0 else None)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([r"$\sigma=0.02$", "0.05", "0.1"])
    ax.set_ylabel("rate error (percent of truth)")
    ax.set_title("synthetic signals (50 each)")
    ax.legend(frameon=False, fontsize=8)
    ax = axs[1]
    lo, hi = dg["common"][0], dg["common"][1]
    for k, n in enumerate(("dir_yc0500_comp", "dir_yc0500_comp_s2", "dir_yc0500_comp_s3")):
        ts, ds = dg[f"{n}_ts"], dg[f"{n}_ds"]
        ok = ds != 0
        ax.plot(ts[ok], np.log(np.abs(ds[ok])), color=fs.SERIES[k], lw=1.0,
                label=n.replace("dir_yc0500_", "").replace("_", " "))
    ax.axvspan(lo, hi, color="grey", alpha=0.15)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\ln|d_s|$ ($\alpha_c$, boxcar)")
    ax.set_title(r"$y_c=0.5$ compensated runs; grey: common interval")
    ax.legend(frameon=False, fontsize=8)
    ax = axs[2]
    for k, n in enumerate(("dir_yc0500_comp", "dir_yc0500_comp_s2", "dir_yc0500_comp_s3")):
        ts, ds = dg[f"{n}_ts"], dg[f"{n}_ds"]
        ok = ds != 0
        t, y = ts[ok], np.log(np.abs(ds[ok]))
        w = 10.0
        tc, sl = [], []
        for t0 in np.arange(t[0] + w / 2, t[-1] - w / 2, 2.0):
            m = (t >= t0 - w / 2) & (t <= t0 + w / 2)
            if m.sum() > 5:
                tc.append(t0)
                sl.append(np.polyfit(t[m], y[m], 1)[0])
        ax.plot(tc, sl, color=fs.SERIES[k], lw=1.0)
    ax.axvspan(lo, hi, color="grey", alpha=0.15)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"local slope of $\ln|d_s|$ (per $M$, 10 $M$ windows)")
    ax.set_title("local growth rate")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "rv_models"))


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or os.path.join(SCR, "tmp", "review_wave3")
    os.makedirs(out, exist_ok=True)
    hres = heat(out)
    mres, v, dg, vj, dj = models(out)
    with open(os.path.join(out, "rv_heat_models.json"), "w") as f:
        json.dump(dict(heat=hres, models=mres), f, indent=1)
    for g in ("T7_th0.003_e0.2", "T7_th0.1_e0.2", "T7_th1_e0.2"):
        r = hres[g]
        print(g, "f0 own %.6f +- %.6f pkg %.6f +- %.6f diff %.2e chi2 %.3f" % (
            r["f0_own"], r["f0_se_own"], r["f0_pkg"], r["f0_se_pkg"], r["diff_f0"], r["chi2_own"]),
            "row diffs", [round(q["diff"], 12) for q in r["rows"]])
    print(json.dumps(mres, indent=1))
    figures(hres, v, dg, vj, out)


if __name__ == "__main__":
    main()
