"""Leg B of flrw_conv: growth rate f = d ln D / d ln a of the plane wave of test B
(arXiv:1904.07841), amplitude errors, decaying mode, constraints; convergence in mesh
(16, 32, 64, 128 cells, one particle per cell) and particle number (1, 8, 27 per cell at
32 cells).

    python3 analyze_b.py <runs.json> [<outdir>]     (default outdir $NRPIC_RUN_DIR)

runs.json maps case names (b_n<N>_p<ppc per direction>) to '<run id>/<name>'.
Estimators and references: flrwlib.growth. Writes <outdir>/flrw_b.json and figures
fig_b_growth, fig_b_error, fig_b_conv, fig_b_constraints.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import flrwlib as fl  # noqa: E402

AREF = (1.1, 1.5, 2.0, 5.0, 10.0, 30.0, 50.0, 100.0, 300.0, 900.0)
EST = ("delta", "star", "phi")
ELAB = {"delta": r"$\delta$ (code slicing)", "star": r"$\delta_\star = \delta - 3\mathcal{H}v$",
        "phi": r"$a\,\varphi$ (Poisson)"}


def parse(name):
    _, n, p = name.split("_")
    return int(n[1:]), int(p[1:])**3


def at(g, key, a0):
    a = g["a"]
    if a0 > a[-1]*1.0001 or a0 < a[0]:
        return float("nan")
    return float(np.interp(np.log(a0), np.log(a), g[key]))


def main():
    runs = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    data, cst = {}, {}
    for name, spec in sorted(runs.items()):
        if not name.startswith("b_"):
            continue
        d = fl.rundir(spec)
        if not os.path.exists(os.path.join(d, "east.line.bin")):
            print(f"missing {name}: {d}")
            continue
        data[name] = fl.growth(d)
        cst[name] = fl.load_hst(os.path.join(d, "east.cstat.hst"))
    order = sorted(data, key=parse)
    # common range of every run (a run still in progress ends early): the convergence
    # figure compares the runs on 3 <= a <= a_common only
    a_common = min(float(g["a"][-1]) for g in data.values())/1.05
    summ = {}
    for name in order:
        g = data[name]
        n, nc = parse(name)
        s = {"n": n, "ppc": nc, "a_end": float(g["a"][-1]), "records": int(len(g["a"])),
             "finite": bool(np.isfinite(g["D_delta"]).all())}
        for key in EST:
            for q in (f"e_{key}", f"df_{key}", f"df_{key}_fd"):
                s[f"{q}_at"] = {f"{a0:g}": at(g, q, a0) for a0 in AREF}
            inner = (g["a"] >= 1.05) & (g["a"] <= g["a"][-1]/1.05)
            s[f"df_{key}_maxabs"] = float(np.abs(g[f"df_{key}"][inner]).max())
            s[f"df_{key}_fd_maxabs"] = float(np.abs(g[f"df_{key}_fd"][inner]).max())
            s[f"e_{key}_maxabs"] = float(np.abs(g[f"e_{key}"]).max())
            s[f"e_{key}_end"] = float(g[f"e_{key}"][-1])
            # plateau (3 <= a, away from the end) and early part (a <= 2) of the f error
            late = (g["a"] >= 3.0) & (g["a"] <= g["a"][-1]/1.05)
            early = (g["a"] >= 1.05) & (g["a"] <= 2.0)
            s[f"df_{key}_plateau_median"] = float(np.median(np.abs(g[f"df_{key}"][late])))
            s[f"df_{key}_plateau_max"] = float(np.abs(g[f"df_{key}"][late]).max())
            s[f"df_{key}_early_max"] = float(np.abs(g[f"df_{key}"][early]).max())
            com = (g["a"] >= 3.0) & (g["a"] <= a_common)
            s[f"df_{key}_plateau_common"] = float(np.median(np.abs(g[f"df_{key}"][com])))
            s[f"e_{key}_maxabs_common"] = float(np.abs(g[f"e_{key}"][g["a"] <= a_common]).max())
        s["a_common"] = a_common
        s["f_delta_num_at"] = {f"{a0:g}": at(g, "f_delta", a0) for a0 in AREF}
        s["fref_delta_at"] = {f"{a0:g}": at(g, "fref_delta", a0) for a0 in AREF}
        s["decaying_fit"] = fl.decaying_fit(g)
        s["decaying_fit_log"] = fl.decaying_fit_log(g)
        per, amp = fl.oscillation_period(g["t"], g["e_phi"])
        s["phi_osc_period_t"] = per
        s["phi_osc_amp"] = amp
        s["phi_osc_speed_L_over_P"] = fl.L/per
        s["phi_amp_start"] = float(g["phi_amp"][0])
        s["phi_amp_end"] = float(g["phi_amp"][-1])
        s["resid_max"] = float(g["resid"].max())
        c = cst[name]
        s["Hr_max_end"] = float(c["Hr_max"][-1])
        s["Hr_max_max"] = float(c["Hr_max"].max())
        s["Mr_max_end"] = float(c["Mr_max"][-1])
        s["bg_delta_end"] = float(g["bg_delta"][-1])
        s["bg_delta_maxabs"] = float(np.abs(g["bg_delta"]).max())
        summ[name] = s
    fl.save_json(summ, os.path.join(out, "flrw_b.json"))
    fs.use_style()
    cols = dict(zip(order, fs.series_colors(len(order))))

    def style(name):
        n, nc = parse(name)
        return dict(color=cols[name], lw=1.0, ls="-" if nc == 1 else ("--" if nc == 8 else ":"),
                    label=rf"$N={n}$, {nc}/cell")

    # ---- figure 1: f(a) and the dictionary ----------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.95, wspace=0.3)
    ref = data[order[0]]
    aa = np.geomspace(1.0, 1001.0, 400)
    k2 = fl.K_WAVE**2
    axs[0].semilogx(aa, aa/(aa + 3.0/k2), **fs.GUIDE, label=r"$f_{\rm ref} = a/(a + 3/k^2)$")
    axs[0].axhline(1.0, **fs.MASK_LINE)
    for name in order:
        g = data[name]
        st = style(name)
        axs[0].semilogx(g["a"], g["f_delta"], color=st["color"], lw=0.8, ls=st["ls"])
        axs[0].semilogx(g["a"], g["f_star"], color=st["color"], lw=0.8, ls=st["ls"], alpha=0.6)
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"$f = d\ln D/d\ln a$")
    axs[0].text(0.35, 0.3, r"upper: $\delta_\star$ ($f = 1$)" "\n" r"lower: $\delta$ of the slicing",
                transform=axs[0].transAxes, fontsize=7)
    axs[0].legend(fontsize=7, loc="lower right")
    for name in order:
        g = data[name]
        axs[1].loglog(g["a"], np.maximum(np.abs(g["df_star"]), 1e-12), **style(name))
    axs[1].axhline(1e-2, **fs.MASK_LINE)
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"$|f_\star - 1|$ (window 0.1 in $\ln a$)")
    axs[1].legend(fontsize=6.5, loc="upper right", ncol=2)
    fs.save(fig, os.path.join(out, "fig_b_growth"))
    plt.close(fig)

    # ---- figure 2: errors of f and of the amplitude, three estimators -------------
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.09, top=0.95, wspace=0.32, hspace=0.1)
    for j, key in enumerate(EST):
        for name in order:
            g = data[name]
            axs[0, j].loglog(g["a"], np.maximum(np.abs(g[f"df_{key}"]), 1e-12), **style(name))
            axs[1, j].loglog(g["a"], np.maximum(np.abs(g[f"e_{key}"]), 1e-12), **style(name))
        axs[0, j].axhline(1e-2, **fs.MASK_LINE)
        axs[0, j].set_title(ELAB[key], fontsize=9)
        axs[1, j].set_xlabel(r"$a$")
    axs[0, 0].set_ylabel(r"$|f - f_{\rm ref}|$")
    axs[1, 0].set_ylabel(r"$|D/D_{\rm ref} - 1|$")
    axs[0, 2].legend(fontsize=6, loc="upper right", ncol=2)
    fs.save(fig, os.path.join(out, "fig_b_error"))
    plt.close(fig)

    # ---- figure 3: convergence at fixed a ------------------------------------------
    # Measures that do not pass through zero: the largest amplitude error over the run, the
    # plateau of the f error (median over 3 <= a) and its early part (largest over a <= 2).
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.93, wspace=0.3)
    mesh = [k for k in order if parse(k)[1] == 1]
    ppcs = [k for k in order if parse(k)[0] == 32]
    ac = summ[order[0]]["a_common"]
    meas = ((rf"largest $|D_\delta/D_{{\rm ref}} - 1|$, $a \leq {ac:.0f}$",
             lambda s: s["e_delta_maxabs_common"], "o"),
            (rf"$|f_\delta - f_{{\rm ref}}|$, median $3 \leq a \leq {ac:.0f}$",
             lambda s: s["df_delta_plateau_common"], "s"),
            (rf"$|f_\star - 1|$, median $3 \leq a \leq {ac:.0f}$",
             lambda s: s["df_star_plateau_common"], "^"),
            (r"$|f_\star - 1|$, early ($a \leq 2$)", lambda s: s["df_star_early_max"], "v"))
    for j, (lab, fun, mk) in enumerate(meas):
        x = [parse(k)[0] for k in mesh]
        y = [fun(summ[k]) for k in mesh]
        axs[0].loglog(x, y, marker=mk, lw=0.9, color=fs.SERIES[j], label=lab)
        x = [parse(k)[1] for k in ppcs]
        y = [fun(summ[k]) for k in ppcs]
        axs[1].loglog(x, y, marker=mk, lw=0.9, color=fs.SERIES[j])
    xs = np.array([16.0, max(parse(k)[0] for k in mesh)])
    y0 = summ[mesh[0]]["df_star_plateau_common"]
    for sl in (-2.0, -4.0):
        yy = y0*(xs/16.0)**sl
        axs[0].loglog(xs, yy, **{**fs.GUIDE, "lw": 0.8}, zorder=0)
        axs[0].text(xs[-1], yy[-1], rf" $N^{{{sl:g}}}$", fontsize=7, va="center")
    axs[0].set_xlabel(r"cells per side $N$ (1 per cell)")
    axs[0].set_xticks([k for k in (16, 32, 64, 128) if k <= xs[-1]])
    axs[0].set_xticklabels([str(k) for k in (16, 32, 64, 128) if k <= xs[-1]])
    axs[0].minorticks_off()
    axs[0].set_xlim(13, xs[-1]*1.6)
    axs[0].set_ylabel("error")
    axs[1].set_xlabel(r"particles per cell $N_c$ (32 cells)")
    axs[1].set_xticks([1, 8, 27])
    axs[1].set_xticklabels(["1", "8", "27"])
    axs[1].minorticks_off()
    axs[1].set_ylabel("error")
    axs[0].legend(fontsize=6.5, loc="lower left")
    fs.save(fig, os.path.join(out, "fig_b_conv"))
    plt.close(fig)

    # ---- figure 4: constraints and potential ---------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.3)
    for name in order:
        c = cst[name]
        g = data[name]
        st = style(name)
        axs[0].loglog(fl.a_of_t(c["time"]), np.maximum(c["Hr_max"], 1e-20), **st)
        axs[1].semilogx(g["a"], g["phi_amp"]/(-1.5*fl.AMP/fl.K_WAVE**2) - 1.0, **st)
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"largest $H_r$")
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"$\varphi_{\rm amp}/\varphi_0 - 1$")
    axs[0].legend(fontsize=6.5, ncol=2, loc="lower right")
    fs.save(fig, os.path.join(out, "fig_b_constraints"))
    plt.close(fig)

    for name, s in summ.items():
        print(f"== {name}: a_end {s['a_end']:.1f}, {s['records']} records; decaying eps "
              f"{s['decaying_fit']['eps']:+.2e} (A+/A {s['decaying_fit']['A_plus_over_A']:.7f})")
        for key in EST:
            print(f"   {key:5s} max|f-fref| {s[f'df_{key}_maxabs']:.2e} (fd {s[f'df_{key}_fd_maxabs']:.2e}); "
                  f"max|e| {s[f'e_{key}_maxabs']:.2e}, end {s[f'e_{key}_end']:+.2e}")
        dl = s["decaying_fit_log"]
        print(f"   plateau median |f-fref| delta {s['df_delta_plateau_median']:.2e} star "
              f"{s['df_star_plateau_median']:.2e} phi {s['df_phi_plateau_median']:.2e}; early max "
              f"star {s['df_star_early_max']:.2e}; log fit: eps {dl['eps']:+.2e}, const f error "
              f"{dl['df_const']:+.2e}, rms {dl['rms_resid']:.1e}; phi oscillation period "
              f"{s['phi_osc_period_t']:.3f} (L/P = {s['phi_osc_speed_L_over_P']:.3f}), amp "
              f"{s['phi_osc_amp']:.1e}")
        print(f"   f_delta at a=1.1, 10, 1000: "
              + ", ".join(f"{s['f_delta_num_at'][k]:.6f}/{s['fref_delta_at'][k]:.6f}"
                          for k in ("1.1", "10", "900")))
        print(f"   Hr_max end {s['Hr_max_end']:.2e} max {s['Hr_max_max']:.2e}; mean-density "
              f"error max {s['bg_delta_maxabs']:.2e}; profile residual max {s['resid_max']:.2e}")


if __name__ == "__main__":
    main()
