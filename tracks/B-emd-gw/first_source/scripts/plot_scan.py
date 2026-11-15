#!/usr/bin/env python3
"""Figures and summary numbers of the crossed-wave scan (P1-P6 of JOURNAL.md).

    python3 plot_scan.py <dir with cw_*.json> [<more dirs>]     (output: $NRPIC_RUN_DIR)

Reads the per-case JSON of analyze_scan.py and writes scan_summary.json and the figures
scan_kk0, scan_null, scan_gauge, scan_secondgauge (png and pdf).
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import reference as ref  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

EPS = {"cw_eps0": 0.0, "cw_eps0p1": 0.1, "cw_eps0p3": 0.3, "cw_eps1": 1.0, "cw_eps1_gd": 1.0}


def load(dirs):
    cases = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "cw_*.json"))):
            c = json.load(open(f))
            cases[c["case"]] = c
    return cases


def series(c, kind, key, part=0):
    rows = [r for r in c["rows"] if r.get("kind") == kind and "error" not in r]
    t = np.array([r["time"] for r in rows])
    if key is None:
        return t, None
    v = []
    for r in rows:
        x = r.get(key)
        if isinstance(x, list):
            x = x[part]
        v.append(np.nan if x is None else x)
    return t, np.array(v, float)


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    cases = load(sys.argv[1:])
    s1 = ref.static_amplitude(0.01, 1.0)
    summ = {"s_eps1": s1, "cases": sorted(cases)}
    fs.use_style()
    import matplotlib.pyplot as plt
    col = {"cw_eps0p1": fs.PAL["yellow"], "cw_eps0p3": fs.PAL["red"], "cw_eps1": fs.PAL["blue"],
           "cw_eps1_gd": fs.PAL["green"], "cw_eps0": "k"}
    tt_ = np.linspace(0, ref.tau_of_a(140), 2001)
    gg, _ = ref.g_of_tau(tt_)

    # ---- P2, P3: (k, k, 0) amplitude against the second-order reference
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True,
                           gridspec_kw={"height_ratios": [2, 1]})
    for j, (K, sign) in enumerate((("K1", 1.0), ("K2", -1.0))):
        ax[0, j].plot(ref.a_of_tau(tt_), sign * gg, **fs.GUIDE, label=r"$\pm s\,g(\tau)$ (second order)")
        for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1"):
            if name not in cases:
                continue
            e = EPS[name]
            t, c = series(cases[name], "bin", f"h_{K}_plus", 0)
            _, cg = series(cases[name], "bin", f"Gtot_{K}_plus", 0)
            a = ref.a_of_tau(t)
            ax[0, j].plot(a, c / (s1 * e), color=col[name], lw=1.5, label=r"$\epsilon=%g$" % e)
            ax[0, j].plot(a, (c - cg) / (s1 * e), color=col[name], lw=1.0, ls="--")
            gi = np.interp(t, tt_, gg)
            ax[1, j].plot(a, c / (sign * s1 * e * gi) - 1, color=col[name], lw=1.5)
            ax[1, j].plot(a, (c - cg) / (sign * s1 * e * gi) - 1, color=col[name], lw=1.0, ls="--")
            sel = (a >= 2) & (a <= 10)
            summ.setdefault("P2", {})[f"{name}_{K}"] = {
                "max_abs_rel_dev_a2_10": float(np.max(np.abs(c[sel] / (sign * s1 * e * gi[sel]) - 1))),
                "rel_dev_at_a": {str(av): float(np.interp(av, a, c / (sign * s1 * e * gi) - 1))
                                 for av in (5, 10, 20, 40, 60, 80, 100, 140)},
                "corrected_rel_dev_at_a": {str(av): float(np.interp(av, a, (c - cg) / (sign * s1 * e * gi) - 1))
                                           for av in (5, 10, 20, 40, 60, 80, 100, 140)},
                "c_over_eps_at_a": {str(av): float(np.interp(av, a, c / e)) for av in (5, 10, 20, 40, 60, 100, 140)},
            }
        ax[0, j].set_ylabel(r"$c_+(%s)/(s\,\epsilon)$ with $s=%.3g$" % ("K_1" if K == "K1" else "K_2", s1))
        ax[0, j].set_title(r"$K_1=(k,k,0)$" if K == "K1" else r"$K_2=(k,-k,0)$", fontsize=10)
        ax[1, j].axhline(0, **fs.MASK_LINE)
        ax[1, j].set_ylim(-0.3, 0.3)
        ax[1, j].set_xscale("log")
        ax[1, j].set_xlabel(r"$a$")
        ax[1, j].set_ylabel("relative to reference")
    ax[0, 0].legend(loc="lower right", fontsize=8)
    ax[0, 1].text(0.03, 0.05, "solid: $\\Lambda h$;  dashed: $\\Lambda h - G_{\\rm tot}$", transform=ax[0, 1].transAxes,
                  fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "scan_kk0"))

    # ---- P3: linearity in eps
    if all(n in cases for n in ("cw_eps0p1", "cw_eps0p3", "cw_eps1")):
        t1, c1 = series(cases["cw_eps0p1"], "bin", "h_K1_plus", 0)
        t3, c3 = series(cases["cw_eps0p3"], "bin", "h_K1_plus", 0)
        tA, cA = series(cases["cw_eps1"], "bin", "h_K1_plus", 0)
        n = min(len(t1), len(t3), len(tA))
        a = ref.a_of_tau(t1[:n])
        sel = (a >= 2) & (a <= 10)
        d13 = c3[:n] / 0.3 / (c1[:n] / 0.1) - 1
        d1A = cA[:n] / 1.0 / (c1[:n] / 0.1) - 1
        summ["P3"] = {"max_abs_0p3_vs_0p1_a2_10": float(np.max(np.abs(d13[sel]))),
                      "max_abs_1_vs_0p1_a2_10": float(np.max(np.abs(d1A[sel]))),
                      "at_a": {str(av): [float(np.interp(av, a, d13)), float(np.interp(av, a, d1A))]
                               for av in (10, 20, 40, 60, 80, 100, 140)}}

    # ---- P1: null
    if "cw_eps0" in cases:
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.3, 3.0))
        for kind, mk in (("bin", "-"), ("rst", "o")):
            t, m = series(cases["cw_eps0"], kind, "max_TT_mode")
            _, r = series(cases["cw_eps0"], kind, "rms_traceless")
            _, mA = series(cases["cw_eps0"], kind, "max_TT_mode_A")
            _, rA = series(cases["cw_eps0"], kind, "rms_traceless_A")
            a = ref.a_of_tau(t)
            ax.semilogy(a, np.maximum(m / r, 1e-30), mk, color=fs.PAL["blue"], ms=3,
                        label=r"$h$ (%s)" % ("single" if kind == "bin" else "double"))
            ax.semilogy(a, np.maximum(mA / rA, 1e-30), mk, color=fs.PAL["red"], ms=3,
                        label=r"$\tilde A$ (%s)" % ("single" if kind == "bin" else "double"))
            summ.setdefault("P1", {})[kind] = {"max_ratio_h": float(np.nanmax(m / r)),
                                              "max_ratio_A": float(np.nanmax(mA / rA)),
                                              "n_dumps": int(len(t))}
        ax.axhline(1e-12, **fs.GUIDE, label="criterion $10^{-12}$")
        ax.set_xscale("log")
        ax.set_xlabel(r"$a$")
        ax.set_ylabel("largest TT mode / rms traceless part")
        ax.set_title(r"null: plane wave, $\epsilon=0$", fontsize=10)
        ax.legend(fontsize=7, loc="upper left")
        fig.tight_layout()
        fs.save(fig, os.path.join(out, "scan_null"))

    # ---- P4, P5: mode content, non-TT part, gauge piece
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.2, 3.2))
    for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1", "cw_eps1_gd"):
        if name not in cases:
            continue
        t, nt = series(cases[name], "bin", "rms_nonTT")
        _, bf = series(cases[name], "bin", "box_mode_fraction")
        _, c = series(cases[name], "bin", "h_K1_plus", 0)
        _, cg = series(cases[name], "bin", "Gtot_K1_plus", 0)
        _, cg0 = series(cases[name], "bin", "G_K1_plus", 0)
        _, rt = series(cases[name], "bin", "rms_TT")
        _, rg = series(cases[name], "bin", "rms_Gtot")
        a = ref.a_of_tau(t)
        lab = r"$\epsilon=%g$" % EPS[name] + (" (Gamma driver)" if name.endswith("_gd") else "")
        ax[0].loglog(a, nt, color=col[name], label=lab)
        ax[1].semilogx(a, bf, color=col[name])
        ax[2].loglog(a, np.abs(cg / c), color=col[name])
        ax[2].loglog(a, rg / rt, color=col[name], ls=":")
        sel = a <= 20
        summ.setdefault("P5", {})[name] = {
            "max_abs_G_over_c_K1_a_le_20": float(np.nanmax(np.abs(cg[sel] / c[sel]))),
            "G_over_c_K1_at_a": {str(av): float(np.interp(av, a, cg / c)) for av in (10, 20, 40, 60, 80, 100, 140)},
            "Gquad_only_over_c_K1_at_a": {str(av): float(np.interp(av, a, cg0 / c)) for av in (10, 20, 40, 60, 80, 100, 140)},
            "rms_nonTT_at_a": {str(av): float(np.interp(av, a, nt)) for av in (5, 10, 20, 40, 60, 80, 100, 140)},
            "rmsG_over_rmsTT_at_a": {str(av): float(np.interp(av, a, rg / rt)) for av in (10, 20, 40, 60, 80, 100, 140)}}
        summ.setdefault("P4", {})[name] = {"min_box_fraction_a_le_20": float(np.nanmin(bf[(a >= 1.2) & (a <= 20)])),
                                           "box_fraction_at_a": {str(av): float(np.interp(av, a, bf))
                                                                 for av in (5, 10, 20, 40, 60, 80, 100, 140)}}
        _, zd = series(cases[name], "bin", "z_dependence")
        summ["P4"][name]["max_z_dependence"] = float(np.nanmax(zd))
    aa = np.logspace(0, np.log10(140), 50)
    ax[0].loglog(aa, 2e-5 * aa, **fs.MASK_LINE)
    ax[0].text(3, 2e-5 * 6, r"$\propto a$", color="grey")
    ax[0].set_ylabel("rms traceless non-TT part of $h$")
    ax[0].legend(fontsize=7)
    ax[1].set_ylabel(r"share of $(\pm k,\pm k,0)$ in $\langle(\Lambda h)^2\rangle$")
    ax[2].set_ylabel(r"$|G_{\rm tot}/c_+|$ at $K_1$; rms ratio (dotted)")
    for x in ax:
        x.set_xlabel(r"$a$")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "scan_gauge"))

    # ---- P6: second gauge
    if "cw_eps1" in cases and "cw_eps1_gd" in cases:
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.2, 3.2))
        tz, cz = series(cases["cw_eps1"], "bin", "h_K1_plus", 0)
        _, gz = series(cases["cw_eps1"], "bin", "Gtot_K1_plus", 0)
        _, gz0 = series(cases["cw_eps1"], "bin", "G_K1_plus", 0)
        tg, cgd = series(cases["cw_eps1_gd"], "bin", "h_K1_plus", 0)
        _, ggd = series(cases["cw_eps1_gd"], "bin", "Gtot_K1_plus", 0)
        _, ggd0 = series(cases["cw_eps1_gd"], "bin", "G_K1_plus", 0)
        n = min(len(tz), len(tg))
        a = ref.a_of_tau(tz[:n])
        raw = cz[:n] - cgd[:n]
        cor = (cz[:n] - gz[:n]) - (cgd[:n] - ggd[:n])
        cor0 = (cz[:n] - gz0[:n]) - (cgd[:n] - ggd0[:n])
        ax[0].semilogx(a, cz[:n] / s1, color=fs.PAL["blue"], label="zero shift")
        ax[0].semilogx(a, cgd[:n] / s1, color=fs.PAL["green"], label="Gamma driver")
        ax[0].semilogx(a, (cz[:n] - gz[:n]) / s1, color=fs.PAL["blue"], ls="--", label=r"$-G_{\rm tot}$")
        ax[0].semilogx(a, (cgd[:n] - ggd[:n]) / s1, color=fs.PAL["green"], ls="--")
        ax[0].set_ylabel(r"$c_+(K_1)/s$, $\epsilon=1$")
        ax[0].legend(fontsize=7)
        ax[1].loglog(a, np.abs(raw / s1), color="k", label=r"$|\Delta c_+|$ raw")
        ax[1].loglog(a, np.abs(cor / s1), color=fs.PAL["red"], ls="--", label=r"$|\Delta c_+|$ after $-G_{\rm tot}$")
        ax[1].loglog(a, np.abs(cor0 / s1), color=fs.PAL["yellow"], ls=":", label=r"after $-G$ (no cross terms)")
        ax[1].set_ylabel(r"difference between the gauges $/|s|$")
        ax[1].legend(fontsize=7)
        # B of a + wave at K1 is a x pattern with sin(K1.x): the imaginary part of c - i s
        tz2, bz = series(cases["cw_eps1"], "rst", "B_K1_cross", 1)
        tg2, bg = series(cases["cw_eps1_gd"], "rst", "B_K1_cross", 1)
        _, hz2 = series(cases["cw_eps1"], "rst", "h_K1_plus", 0)
        _, hg2 = series(cases["cw_eps1_gd"], "rst", "h_K1_plus", 0)
        m2 = min(len(tz2), len(tg2))
        if m2:
            a2 = ref.a_of_tau(tz2[:m2])
            sel = a2 > 1.5
            dB = np.abs(bz[:m2] - bg[:m2]) / np.maximum(np.abs(bz[:m2]), np.abs(bg[:m2]))
            dh = np.abs(hz2[:m2] - hg2[:m2]) / np.maximum(np.abs(hz2[:m2]), np.abs(hg2[:m2]))
            ax[2].loglog(a2[sel], dB[sel], "o-", color=fs.PAL["red"], ms=3, label=r"magnetic Weyl $B$ ($\times$, sin part)")
            ax[2].loglog(a2[sel], dh[sel], "s--", color="k", ms=3, label=r"$\Lambda h$ ($+$, cos part)")
            ax[2].set_ylabel(r"relative difference between the gauges at $K_1$")
            ax[2].legend(fontsize=7)
            summ["P6_B"] = {"a": a2.tolist(), "B_zero_shift": bz[:m2].tolist(), "B_gamma_driver": bg[:m2].tolist(),
                            "rel_diff_B": dB.tolist(), "rel_diff_h": dh.tolist()}
        for x in ax:
            x.set_xlabel(r"$a$")
        fig.tight_layout()
        fs.save(fig, os.path.join(out, "scan_secondgauge"))
        big = np.abs(raw) > 1e-3 * abs(s1)
        summ["P6"] = {"frac_points_raw_above_1e-3": float(np.mean(big)),
                      "max_ratio_cor_over_raw_where_big": float(np.nanmax(np.abs(cor[big] / raw[big]))) if big.any() else None,
                      "median_ratio_cor_over_raw_where_big": float(np.nanmedian(np.abs(cor[big] / raw[big]))) if big.any() else None,
                      "raw_over_s_at_a": {str(av): float(np.interp(av, a, raw / s1)) for av in (5, 10, 20, 40, 60, 80, 100, 140)},
                      "cor_over_s_at_a": {str(av): float(np.interp(av, a, cor / s1)) for av in (5, 10, 20, 40, 60, 80, 100, 140)},
                      "cor_quad_only_over_s_at_a": {str(av): float(np.interp(av, a, cor0 / s1)) for av in (5, 10, 20, 40, 60, 80, 100, 140)},
                      "median_ratio_cor_quad_only_over_raw_where_big": float(np.nanmedian(np.abs(cor0[big] / raw[big]))) if big.any() else None}
    with open(os.path.join(out, "scan_summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1)[:6000])


if __name__ == "__main__":
    main()
