#!/usr/bin/env python3
"""V2, V3, V5: F21 table rows and criteria, King b = 1 threshold, Knudsen conversions.

Uses only kingsolve.py and v_mono.py of this directory. Output (argv[1]): v_king.json,
fig_v2_f21.{png,pdf}, fig_v3_king_b1.{png,pdf}, fig_v5_knudsen.{png,pdf}.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))
import kingsolve as ks          # noqa: E402
import v_mono                   # noqa: E402

# F21 Table 1, b = 0.1 (kb-data/raw/arxiv/2108.11967/v2/src/main.tex lines 492, 495, 498,
# 501, 503): w0, M^, E^rest, B^, eps, R^, C, Z(0), eps_c(0), rho^(0), p^(0), v(0), <g>, g_cr
F21 = [
    (0.6, 3.47240e-2, 3.51790e-2, 4.54900e-4, 1.29311e-2, 1.63800, 2.11990e-2, 8.71214e-2,
     6.38296e-2, 5.82063e-2, 9.86165e-4, 2.25450e-1, 1.65936, 1.37799),
    (1.9, 2.72897e-2, 2.81385e-2, 8.48824e-4, 3.01659e-2, 5.81001e-1, 4.69701e-2,
     2.96903e-1, 2.34552e-1, 2.33058, 1.21454e-1, 3.95398e-1, 1.64377, 1.47651),
    (3.2, 1.84498e-2, 1.91224e-2, 6.72639e-4, 3.51754e-2, 3.78001e-1, 4.88088e-2,
     5.47883e-1, 4.70526e-1, 2.22039e1, 1.89599, 5.06132e-1, 1.62919, 1.57054),
    (4.05150, 1.42556e-2, 1.47424e-2, 4.86859e-4, 3.30243e-2, 3.68001e-1, 3.87378e-2,
     7.50107e-1, 6.81035e-1, 8.17923e1, 8.74006, 5.66189e-1, 1.62117, 1.62117),
    (4.5, 1.27271e-2, 1.31271e-2, 4.00052e-4, 3.04753e-2, 4.13001e-1, 3.08160e-2,
     8.76941e-1, 8.18182e-1, 1.60208e2, 1.89661e1, 5.95948e-1, 1.61808, 1.63933)]
COLS = ["M", "Erest", "B", "eps", "R", "C", "Z0", "epsc0", "rho_c", "p_c", "v0",
        "gamma_avg", "gamma_cr"]


def argmax(fun, lo, hi):
    o = minimize_scalar(lambda x: -fun(x), bounds=(lo, hi), method="bounded",
                        options=dict(xatol=1e-8))
    return o.x


def strip(m):
    return {k: float(v) for k, v in m.items() if k != "sol"}


def knudsen(m, label):
    """Three definitions of the central Knudsen number times sigma/m (ADM units)."""
    Wc = m["Wc0"]
    vmol = ks.vmol_avg(Wc, m["b"])
    rho0 = m["rho0c_M2"]
    return dict(label=label,
                scope_inv_rho0_H=1 / (rho0 * m["Hc_scope"]),          # SCOPE.md 4
                conv_Kn_sigma=m["vmean_c"] / (rho0 * vmol * m["Hc_conv"]),  # CONVERSION.md
                gravo_KnR_sigma=1 / (rho0 * m["R_over_M"]),           # gravothermal 5
                vmol_c=vmol, vmean_c=m["vmean_c"], rho0c_M2=rho0,
                Hc_scope=m["Hc_scope"], Hc_conv=m["Hc_conv"],
                rho_over_rho0=m["rho_c"] / m["n_c"], v1_energy=m["v1_energy"],
                v1_rest=m["v1_rest"], R_over_M=m["R_over_M"])


def main(out):
    os.makedirs(out, exist_ok=True)
    res = {}
    # V2: table rows
    rows = []
    for row in F21:
        m = ks.solve(0.1, row[0])
        rel = {c: (m[c] / row[i + 1] - 1) for i, c in enumerate(COLS)}
        rel["R_trunc_diff"] = m["R"] - row[5]
        rel["C_with_printed_R"] = m["M"] / row[5] / row[6] - 1
        rows.append(dict(w0=row[0], rel=rel, mine=strip(m)))
    res["f21_rows_b0.1"] = rows
    # criteria per b
    crit = {}
    for b in (0.1, 0.2, 0.3, 0.5):
        e = lambda w: ks.solve(b, w)["eps"]
        lo, hi = {0.1: (2.6, 3.8), 0.2: (1.2, 1.8), 0.3: (0.8, 1.2), 0.5: (0.45, 0.7)}[b]
        we = argmax(e, lo, hi)
        g = lambda w: ks.solve(b, w)["gamma_avg"] - ks.solve(b, w)["gamma_cr"]
        lo2, hi2 = {0.1: (3.8, 4.4), 0.2: (1.5, 2.0), 0.3: (1.0, 1.3), 0.5: (0.6, 0.75)}[b]
        wg = brentq(g, lo2, hi2, xtol=1e-9)
        crit[str(b)] = dict(eps_max=strip(ks.solve(b, we)), trial_root=strip(ks.solve(b, wg)))
    b = 0.1
    crit["0.1"]["E_max"] = strip(ks.solve(b, argmax(lambda w: ks.solve(b, w)["M"], 0.3, 1.0)))
    crit["0.1"]["B_max"] = strip(ks.solve(b, argmax(lambda w: ks.solve(b, w)["B"], 1.5, 2.4)))
    res["criteria"] = crit
    # V3: King b = 1 in y0
    ymax = argmax(lambda y: ks.solve(1.0, y0=y)["eps"], 0.25, 0.42)
    yzero = brentq(lambda y: ks.solve(1.0, y0=y)["eps"], 0.6, 0.95, xtol=1e-10)
    k1 = ks.solve(1.0, y0=ymax)
    res["king_b1"] = dict(y_max=ymax, y_zero=yzero, at_max=strip(k1),
                          paper=dict(y_max=0.334, y_zero=0.784, locator="2009.08163 paper.tex:953"))
    # V5: Knudsen
    mono = v_mono.model(0.679610179560908)
    kn = [knudsen(ks.solve(0.1, crit["0.1"]["eps_max"]["w0"]), "King b=0.1 eps max"),
          knudsen(ks.solve(0.1, crit["0.1"]["trial_root"]["w0"]), "King b=0.1 trial root"),
          knudsen(k1, "King b=1 eps max")]
    res["knudsen"] = kn
    res["mono_inv_rho0_H"] = mono["inv_rho0c_Hc"]
    # CODATA 2018 G and c; IAU 2015 nominal GM_sun = 1.3271244e26 cm^3 s^-2
    G, c, GMsun = 6.67430e-8, 2.99792458e10, 1.3271244e26
    unit = G * GMsun / c ** 4            # G^2 M_sun / c^4 in cm^2/g
    res["unit_cm2_per_g_per_Msun"] = unit
    phys = []
    for k in kn + [dict(label="mono max", scope_inv_rho0_H=mono["inv_rho0c_Hc"])]:
        for M in (200.0, 1.9e9):
            sig_code = 5.0 / (unit * M)
            phys.append(dict(model=k["label"], M_sun=M, sigma_code=sig_code,
                             Kn_scope=k["scope_inv_rho0_H"] / sig_code))
    res["physical_Kn_5cm2g"] = phys
    # sequences for figures
    ws = np.linspace(0.2, 5.0, 97)
    res["seq_b0.1"] = [dict(w0=float(w), **{k: float(v) for k, v in strip(ks.solve(0.1, w)).items()
                                             if k in ("Z0", "eps", "gamma_avg", "gamma_cr", "v0")})
                       for w in ws]
    ys = np.linspace(0.05, 0.95, 91)
    res["seq_b1"] = [dict(y0=float(y), eps=float(ks.solve(1.0, y0=y)["eps"])) for y in ys]
    with open(os.path.join(out, "v_king.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    figures(res, out)
    print(json.dumps(dict(rows=[(r["w0"], r["rel"]) for r in rows],
                          crit={b: {k: (v["w0"], v["Z0"], v["eps"], v["v0"], v.get("C"),
                                        v["R_over_M"])
                                    for k, v in d.items()} for b, d in crit.items()},
                          king_b1=res["king_b1"]["y_max"], y_zero=yzero, kn=kn,
                          mono=res["mono_inv_rho0_H"], unit=unit, phys=phys),
                     indent=1, default=float))


def figures(res, out):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    # V2
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.32)
    s = res["seq_b0.1"]
    Z = [r["Z0"] for r in s]
    ax = axs[0]
    ax.plot(Z, [r["eps"] for r in s], color=fs.PAL["red"], label="this check")
    ax.plot([r[7] for r in F21], [r[4] for r in F21], "o", mfc="none", color=fs.PAL["blue"],
            label="F21 Table 1")
    c = res["criteria"]["0.1"]
    ax.axvline(c["eps_max"]["Z0"], **fs.GUIDE, label=f"$\\varepsilon$ max, Z(0)={c['eps_max']['Z0']:.4f}")
    ax.axvline(c["trial_root"]["Z0"], color="k", lw=1.0, ls=":",
               label=f"trial root, Z(0)={c['trial_root']['Z0']:.4f}")
    ax.set_xlabel("$Z(0)$")
    ax.set_ylabel(r"$\varepsilon$ (b = 0.1)")
    ax.legend(loc="lower center", fontsize=8)
    ax = axs[1]
    mk = dict(M="o", Erest="s", eps="^", Z0="v", v0="D", gamma_avg="<", gamma_cr=">")
    for k, m in mk.items():
        ax.plot([r["w0"] for r in res["f21_rows_b0.1"]],
                [abs(r["rel"][k]) + 1e-9 for r in res["f21_rows_b0.1"]], m + "-", label=k,
                lw=1.0)
    ax.axhline(2e-4, color="k", lw=1.0, ls=":")
    ax.set_yscale("log")
    ax.set_xlabel("$w(0)$")
    ax.set_ylabel("|this / F21 - 1|")
    ax.legend(ncol=2, fontsize=7, loc="upper left")
    ax.set_ylim(1e-9, 1e-2)
    fs.save(fig, os.path.join(out, "fig_v2_f21"))
    # V3
    fig, ax = plt.subplots(figsize=(4, 3.2))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
    ax.plot([r["y0"] for r in res["seq_b1"]], [r["eps"] for r in res["seq_b1"]],
            color=fs.PAL["red"], label="this check, b = 1")
    ax.axvline(0.334, **fs.GUIDE, label="paper $y_{max}$, $y_{zero}$")
    ax.axvline(0.784, **fs.GUIDE)
    ax.axhline(0, color="grey", lw=0.8)
    ax.plot([res["king_b1"]["y_max"], res["king_b1"]["y_zero"]],
            [res["king_b1"]["at_max"]["eps"], 0], "o", color=fs.PAL["red"])
    ax.set_xlabel("$y_0$")
    ax.set_ylabel("$E_b$")
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_v3_king_b1"))
    # V5
    fig, ax = plt.subplots(figsize=(4, 3.2))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.2, top=0.95)
    kn = res["knudsen"]
    x = np.arange(len(kn))
    ax.bar(x - 0.27, [k["scope_inv_rho0_H"] for k in kn], 0.27, color=fs.PAL["blue"],
           label="SCOPE: $1/(\\rho_0 H)$, H on $\\rho$")
    ax.bar(x, [k["conv_Kn_sigma"] for k in kn], 0.27, color=fs.PAL["red"],
           label="CONVERSION: Moller $l$, H on $\\rho_0$")
    ax.bar(x + 0.27, [10 * k["gravo_KnR_sigma"] for k in kn], 0.27, color=fs.PAL["yellow"],
           label="gravothermal: $10\\,\\lambda/R$")
    ax.set_xticks(x)
    ax.set_xticklabels([k["label"].replace("King ", "") for k in kn], rotation=20, fontsize=8)
    ax.set_ylabel("$\\sigma/m$ [$M^{-1}$] for Kn$_c$ = 1")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_ylim(0, 290)
    fs.save(fig, os.path.join(out, "fig_v5_knudsen"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NRPIC_RUN_DIR", "."))
