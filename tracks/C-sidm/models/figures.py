#!/usr/bin/env python3
"""Figures of the models package from the registered run outputs (style:
python/nrpic/figstyle.py).

    python3 figures.py [--onset DIR] [--checks DIR_1e4 DIR_1e5] [--growth DIR] [--out DIR]

--onset   run directory of fluid_onset.py      -> fig_fluid_onset.{pdf,png}
--checks  run directories of check_models.py   -> fig_models.{pdf,png}
--growth  run directory of validate_growth.py  -> fig_growth.{pdf,png}
Default output: $NRPIC_RUN_DIR.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(HERE, "..", "gravothermal"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402

VC = {"F21": fs.PAL["blue"], "J_T": fs.PAL["red"], "J_E": fs.PAL["green"],
      "J_p": fs.PAL["orange"], "J_pu": fs.PAL["yellow"]}
VL = {"F21": r"F21: $1+p/u$ (truncated)", "J_T": r"$\Gamma_1(\theta_T)$",
      "J_E": r"$\Gamma_1(\theta_E)$", "J_p": r"$\Gamma_1(\theta_p)$",
      "J_pu": r"$1+p/u$ (Juttner, $\theta_T$)"}


def fig_fluid_onset(d, out):
    import tmb
    F = np.load(os.path.join(d, "fluid_onset_figdata.npz"))
    J = json.load(open(os.path.join(d, "fluid_onset.json")))
    r1 = J["results"]["0.1"]
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.98, wspace=0.42, hspace=0.3)
    a = ax[0, 0]
    a.semilogx(F["theta"], F["gamma1"], color=fs.PAL["red"], label=r"Juttner $\Gamma_1=1+1/c_v$")
    a.semilogx(F["theta"], F["gamma_pu"], color=fs.PAL["blue"], ls="--", label=r"Juttner $1+p/u$")
    c = r1["onset"]["J_E_N1200"]["central"]
    for th, lab in ((c["theta_T"], r"$\theta_T$"), (c["theta_E"], r"$\theta_E$")):
        a.axvline(th, **fs.MASK_LINE)
        a.text(th * 1.06, 1.645, lab, fontsize=8)
    a.axhline(5 / 3, **fs.THIN, ls=":")
    a.axhline(4 / 3, **fs.THIN, ls=":")
    a.set_xlabel(r"$\theta=kT/m$")
    a.set_ylabel("adiabatic index")
    a.legend(loc="center left", fontsize=8)
    # omega^2 R^3/M along b = 0.1
    a = ax[0, 1]
    w = F["b0.1_seq_w0"]
    Z = F["b0.1_seq_Z0"]
    sc = np.array([(lambda e: e["R"] ** 3 / e["E"])(tmb.solve(0.1, x)) for x in w])
    for v in ("F21", "J_T", "J_E", "J_p", "J_pu"):
        a.plot(Z, F[f"b0.1_seq_{v}"] * sc, color=VC[v], label=VL[v], marker="o", ms=2.5)
        z0 = r1["onset"][f"{v}_N1200"]["Z0"]
        a.plot([z0], [0], marker="x", color=VC[v], ms=7, mew=1.5)
    a.axhline(0, **fs.THIN)
    a.axvline(r1["eps_max"]["Z0"], **fs.GUIDE, label=r"$E_b$ maximum")
    a.set_xlabel(r"$Z(0)$")
    a.set_ylabel(r"$\omega_0^2 R^3/M$")
    a.set_ylim(-1.0, 1.0)
    a.set_xlim(Z.min(), Z.max())
    a.legend(loc="lower left", fontsize=7, ncol=2)
    # profiles at the E_b maximum
    a = ax[1, 0]
    m = F["b0.1_epsmax_M"]
    for v in ("F21", "J_T", "J_E", "J_p", "J_pu"):
        a.plot(m, F[f"b0.1_epsmax_{v}"], color=VC[v], label=VL[v])
    a2 = a.twinx()
    a2.plot(m, F["b0.1_epsmax_p"], **fs.MASK_LINE)
    a2.set_ylabel(r"$p/p_c$ (grey)", labelpad=1)
    a2.set_ylim(0, 1.05)
    a.set_xlabel(r"enclosed mass $M(r)/M$")
    a.set_ylabel(r"$\gamma(r)$ at the $E_b$ maximum, $b=0.1$")
    a.set_xlim(0, 1)
    a.set_ylim(1.3, 1.7)
    # onsets against b
    a = ax[1, 1]
    bs = sorted(J["results"], key=float)
    bx = np.array([float(b) for b in bs])
    a.plot(bx, [J["results"][b]["eps_max"]["Z0"] for b in bs], **fs.GUIDE, marker="s", ms=4,
           label=r"$E_b$ maximum")
    for v in ("F21", "J_E", "J_T"):
        y = [J["results"][b]["onset"].get(f"{v}_N600", {}).get("Z0") for b in bs]
        y = np.array([np.nan if q is None else q for q in y], float)
        a.plot(bx, y, color=VC[v], marker="o", ms=4, label=VL[v])
    a.set_xlabel(r"$b=kT(R)/m$")
    a.set_ylabel(r"onset $Z(0)$")
    a.legend(loc="lower left", fontsize=8)
    return fs.save(fig, os.path.join(out, "fig_fluid_onset"))


def fig_models(dirs, out):
    D = [np.load(os.path.join(d, "figdata.npz")) for d in dirs]
    C = [json.load(open(os.path.join(d, "checks.json"))) for d in dirs]
    F, c0 = D[0], C[0]
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.98, wspace=0.3, hspace=0.3)
    a = ax[0, 0]
    a.plot(F["tmb01_seq_Z0"], F["tmb01_seq_Eb"], color=fs.PAL["blue"], label=r"$b=0.1$ sequence")
    specs = [s for s in c0["model_set"] if s["family"] == "tmb01"]
    zs = [c0[f"model {s['tag']}"]["summary"]["Zc"] for s in specs]
    ebs = [c0[f"model {s['tag']}"]["summary"]["Eb"] for s in specs]
    a.plot(zs, ebs, ls="none", marker="o", color=fs.PAL["red"], label="particle models")
    a.set_xlabel(r"$Z(0)$")
    a.set_ylabel(r"$E_b=(M_0-M)/M_0$")
    a.legend(loc="lower center")
    a = ax[0, 1]
    tm = [s["tag"] for s in specs if "maximum" in s["role"]][0]
    for tag, col, lab in ((tm, fs.PAL["red"], r"$b=0.1$, $E_b$ max."),
                          ("king_y0p33403", fs.PAL["blue"], r"King, $E_b$ max.")):
        r = F[f"prof_{tag}_r"]
        n = F[f"prof_{tag}_n"]
        a.semilogy(r, n / n[0], color=col, label=lab)
        rb = F[f"r_{tag}_sample"]
        h, e = np.histogram(rb, bins=60, range=(0, r.max()))
        a.semilogy(0.5 * (e[1:] + e[:-1]), np.maximum(h, 0.5) / np.max(h) * 1.0, color=col,
                   ls="none", marker=".", ms=3, alpha=0.6)
    a.set_xlabel(r"isotropic radius $\bar r/M$")
    a.set_ylabel(r"$n/n_c$ (lines); radial counts (dots)")
    a.set_ylim(1e-5, 2)
    a.legend(loc="upper right")
    a = ax[1, 0]
    Fb = D[-1]
    x, pdf = Fb[f"E_{tm}_x"], Fb[f"E_{tm}_pdf"]
    a.hist(Fb[f"E_{tm}_sample"], bins=80, density=True, color=fs.PAL["red"], alpha=0.5,
           label=f"file, N = {C[-1]['N']:.0e}".replace("e+0", "e"))
    a.plot(x, pdf, color=fs.PAL["blue"], label="continuum")
    a.set_xlabel(r"$E/E_0$ ($b=0.1$, $E_b$ maximum)")
    a.set_ylabel("probability density")
    a.legend(loc="upper left")
    a = ax[1, 1]
    tags = [s["tag"] for s in c0["model_set"]]
    xs = np.arange(len(tags))
    for k, (c, mk) in enumerate(zip(C, ("o", "s"))):
        v = [abs(c[f"model {t}"]["summary"]["sum_m_W_over_psi_rel"]) for t in tags]
        a.semilogy(xs, v, ls="none", marker=mk, color=fs.SERIES[k + 1 if k else 0],
                   label=rf"$|\sum m W/\psi - M|$, N = {c['N']:.0e}".replace("e+0", "e"))
        z = [float(c[f"model {t}"]["stratified N=2e4: max z of shell moments"]["value"]) for t in tags]
    a.set_xticks(xs)
    a.set_xticklabels([t.replace("king_y0p", "K").replace("tmb01_Z0p", "T") for t in tags],
                      rotation=60, fontsize=7)
    a.axhline(1e-3, **fs.GUIDE)
    a.set_ylabel("particle form of the constraint")
    a.legend(loc="lower left", fontsize=8)
    return fs.save(fig, os.path.join(out, "fig_models"))


def fig_growth(d, out):
    F = np.load(os.path.join(d, "growth_figdata.npz"))
    J = json.load(open(os.path.join(d, "growth_validation.json")))
    fig, ax = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 9.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.06, top=0.98, wspace=0.27, hspace=0.32)
    # synthetic example
    a = ax[0, 0]
    s = 0.05
    t, dd = F[f"syn_{s:g}_t"], F[f"syn_{s:g}_d"]
    ts, ds = F[f"syn_{s:g}_ts"], F[f"syn_{s:g}_ds"]
    t0, t1, sg, A = F[f"syn_{s:g}_win"]
    a.semilogy(t, np.abs(dd), **fs.MASK_LINE, label=r"$|d|$ records")
    a.semilogy(ts, np.abs(ds), color=fs.PAL["red"], label=r"$|d_s|$ (10 M boxcar)")
    a.semilogy(t, 1e-3 * np.exp(s * t), **fs.GUIDE, label=r"$10^{-3}e^{0.05t}$ (truth)")
    tw = np.linspace(t0, t1, 50)
    a.semilogy(tw, abs(A) * np.exp(sg * tw), **fs.REF_LINE, label=rf"fit $\sigma={sg:.4f}$")
    a.axhspan(0.01, 0.1, color=fs.PAL["red"], alpha=0.08)
    a.set_ylim(1e-4, 1)
    a.set_xlabel(r"$t/M$")
    a.set_ylabel(r"$|d|$ synthetic")
    a.legend(loc="lower right", fontsize=8)
    a = ax[0, 1]
    for k, sgm in enumerate((0.02, 0.05, 0.1)):
        f = F[f"syn_{sgm:g}_fits"] / sgm
        a.plot(np.full(len(f), k) + np.linspace(-0.25, 0.25, len(f)), f, ls="none", marker=".",
               color=fs.PAL["red"], alpha=0.6)
        g = J["G2"][f"{sgm:g}"]
        a.errorbar([k + 0.35], [1 + g["mean_rel_bias"]], yerr=[g["rms_rel_err"]], color="k",
                   marker="o", ms=4, capsize=3)
        a.plot([k + 0.45], [1 + g["mean_rel_bias_nl"]], marker="s", color=fs.PAL["blue"], ms=5)
    a.axhline(1, **fs.GUIDE)
    a.set_xticks([0, 1, 2])
    a.set_xticklabels([r"$\sigma=0.02$", "0.05", "0.1"])
    a.set_ylabel(r"$\sigma_{\rm fit}/\sigma$ (50 realisations)")
    a.text(0.02, 0.04, "black: mean, rms; blue: curve_fit mean", transform=a.transAxes, fontsize=8)
    # unperturbed y_c = 0.5: alpha_c and r10
    for a, lab, yl in ((ax[1, 0], "a", r"$|\alpha_c-\alpha_c(0)|$ smoothed"),
                       (ax[1, 1], "r", r"$|r_{10}/r_{10}(0)-1|$ smoothed")):
        for k, key in enumerate(("dir_yc0500_comp", "dir_yc0500_comp_s2", "dir_yc0500_comp_s3",
                                 "dir_yc0500_plain")):
            col = fs.SERIES[[3, 1, 4, 0][k]] if key != "dir_yc0500_plain" else "grey"
            if f"{key}_{lab}_ts" not in F:
                if lab == "a":
                    tt = F[f"{key}_t"]
                    aa = F[f"{key}_alpha"]
                    a.semilogy(tt, np.abs(aa - aa[0]), color="grey", lw=1.0,
                               label="plain filter (no window)")
                continue
            ts, ds = F[f"{key}_{lab}_ts"], F[f"{key}_{lab}_ds"]
            t0, t1, sg, A, sgn = F[f"{key}_{lab}_fit"]
            a.semilogy(ts, np.abs(ds), color=col, lw=1.0,
                       label=key.replace("dir_yc0500_", "") + rf": $\sigma={sg:.3f}$")
            tw = np.linspace(t0, t1, 40)
            a.semilogy(tw, abs(A) * np.exp(sg * tw), color="k", lw=1.0)
        a.axhspan(0.01, 0.1, color="grey", alpha=0.1)
        a.set_xlim(0, 120)
        a.set_ylim(1e-3, 1)
        a.set_xlabel(r"$t/M$")
        a.set_ylabel(yl + r", $y_c=0.5$")
        a.legend(loc="lower right", fontsize=7)
    # collapsing runs
    a = ax[2, 0]
    G = J["growth"]
    for k, key in enumerate(("yc0500_v5", "yc0605_v5", "reconf_yc0756_hc")):
        col = fs.SERIES[[1, 0, 3][k]]
        a.plot(F[f"{key}_t"], F[f"{key}_alpha"], color=col, lw=1.0, label=key)
        cs = G[key]["collapse"]
        a.axvline(cs["t_AH_first"], color=col, ls="--", lw=1.0)
        a.plot([cs["t_alpha"]["0.2"]], [0.2], marker="o", color=col, ms=4)
    a.axhline(0.2, **fs.THIN, ls=":")
    a.set_xlabel(r"$t/M$")
    a.set_ylabel(r"$\alpha_c$ (dashed: first apparent horizon)")
    a.legend(loc="lower left", fontsize=8)
    a = ax[2, 1]
    for k, key in enumerate(("yc0500_v5", "yc0605_v5", "reconf_yc0756_hc")):
        col = fs.SERIES[[1, 0, 3][k]]
        if f"{key}_a_ts" not in F:
            continue
        ts, ds = F[f"{key}_a_ts"], F[f"{key}_a_ds"]
        t0, t1, sg, A, sgn = F[f"{key}_a_fit"]
        a.semilogy(ts, np.abs(ds), color=col, lw=1.0, label=rf"{key}: $\sigma={sg:.3f}$")
        tw = np.linspace(t0, t1, 40)
        a.semilogy(tw, abs(A) * np.exp(sg * tw), color="k", lw=1.0)
    a.axhspan(0.02, 0.2, color="grey", alpha=0.1)
    a.set_ylim(1e-4, 1)
    a.set_xlabel(r"$t/M$")
    a.set_ylabel(r"$|\alpha_c-\alpha_c(0)|$ smoothed")
    a.legend(loc="lower right", fontsize=7)
    return fs.save(fig, os.path.join(out, "fig_growth"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--onset")
    p.add_argument("--checks", nargs="*")
    p.add_argument("--growth")
    p.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = p.parse_args(argv)
    fs.use_style()
    os.makedirs(a.out, exist_ok=True)
    made = []
    if a.onset:
        made += fig_fluid_onset(a.onset, a.out)
    if a.checks:
        made += fig_models(a.checks, a.out)
    if a.growth:
        made += fig_growth(a.growth, a.out)
    print("\n".join(made))
    return 0


if __name__ == "__main__":
    sys.exit(main())
