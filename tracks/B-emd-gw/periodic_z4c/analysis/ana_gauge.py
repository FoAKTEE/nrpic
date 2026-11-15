#!/usr/bin/env python3
"""Analysis of the record of the lapse and shift options (sets gauge_lin, gauge_nl).

Linear set (kappa = 1e-6): the mode amplitudes a_s (alpha - 1 on sin 2 pi x),
K_s (K = Khat + 2 Theta on sin), h_s (gamma_xx - 1 = gt_xx/chi - 1 on sin) and b_c
(beta^x on cos) against the linearized system refsol.gauge_linear.
Nonlinear set (kappa = 1.5): lapse profiles, the steepest lapse gradient, the time of
failure, and the pointwise identities that the slicing conditions imply with zero shift
and no advection (sqrt(gamma) = chi^(-3/2)):
  harmonic   d_t alpha = -alpha^2 K           =>  alpha chi^(3/2) = const
  onelog     d_t alpha = -2 alpha K            =>  alpha + 3 ln chi = const
  conformal  d_t alpha = -(1/3) alpha^2 K      =>  alpha chi^(1/2) = const
  volume     d_t alpha = -(1/3) chi^(-1/2) alpha K  =>  alpha - chi^(-1/2) = const
(exact when Theta = 0; the code drives alpha with Khat = K - 2 Theta).
Writes figs/gauge_*.{pdf,png}, tables/gauge.json, tables/gauge.md.

    python3 ana_gauge.py
"""
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

import common as cm
import athena_dumps as ad
import refsol as rs
from nrpic import figstyle as fs

sys.path.insert(0, cm.PKG)
from make_cases import GAUGES  # noqa: E402

KAPPA = 1.0e-6
LABEL = {"harmonic": "harmonic", "onelog": "1+log", "conformal": "conformal time",
         "volume": "volume (1/3)", "kdriver": r"conformal + K driver $\mu=1$",
         "geodesic": "geodesic", "onelog_gd": r"1+log, $\Gamma$ driver (1, 2)",
         "conf_gd": r"conformal, $\Gamma$ driver (0.75, 1)",
         "harm_hs": "harmonic, harmonic shift terms"}
IDENT = {"harmonic": lambda a, c: a*c**1.5, "onelog": lambda a, c: a + 3*np.log(c),
         "conformal": lambda a, c: a*np.sqrt(c), "volume": lambda a, c: a - c**-0.5}


def opts(g):
    o = dict(lapse_oplog=0.0, lapse_harmonicf=1.0, lapse_harmonic=0.0, lapse_volume=0.0,
             lapse_kdriver=0.0, shift_Gamma=0.0, shift_alpha2Gamma=0.0, shift_H=0.0,
             shift_eta=0.0)
    o.update(GAUGES[g])
    return o


def modes(run):
    t, y, ident, prof = [], [], [], []
    for p in cm.tab_files(run):
        d = ad.read_tab(p)
        x = d["x1v"]
        K = d["Khat"] + 2*d["Theta"]
        h = d["gxx"]/d["chi"] - 1.0
        a_s, _ = cm.project(x, d["alpha"] - 1.0, 1, 1.0)
        K_s, _ = cm.project(x, K, 1, 1.0)
        h_s, _ = cm.project(x, h, 1, 1.0)
        _, b_c = cm.project(x, d["betax"], 1, 1.0)
        t.append(d["time"])
        y.append([a_s, K_s, h_s, b_c])
        prof.append((d["time"], x, d["alpha"], d["chi"], d["Theta"]))
    o = np.argsort(t)
    return np.asarray(t)[o], np.asarray(y)[o], [prof[i] for i in o]


def linear(fig_path):
    gs = list(GAUGES)
    fig, axs = plt.subplots(3, 3, figsize=(fs.FULL_WIDTH, 7.0), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.07, top=0.93, hspace=0.28,
                        wspace=0.28)
    names = [r"$a_s$", r"$K_s$", r"$h_s$", r"$b_c$"]
    out = {}
    for ax, g in zip(axs.flat, gs):
        run = cm.find_run(f"gauge_lin_{g}_N64")
        t, y, prof = modes(run)
        ref = rs.gauge_linear(opts(g), t, KAPPA)
        dev = np.max(np.abs(y - ref), axis=0)/KAPPA
        scale = np.max(np.abs(ref), axis=0)/KAPPA
        ident = None
        if g in IDENT:
            i0 = IDENT[g](prof[0][2], prof[0][3])
            ident = max(np.max(np.abs(IDENT[g](a, c) - i0)) for _, _, a, c, _ in prof)/KAPPA
        thmax = max(np.max(np.abs(th)) for _, _, _, _, th in prof)/KAPPA
        out[g] = dict(run_id=run["run_id"], max_dev_over_kappa=dev.tolist(),
                      max_ref_over_kappa=scale.tolist(), identity_over_kappa=ident,
                      theta_max_over_kappa=thmax, F=rs.gauge_F(opts(g)),
                      eig_over_k=[[float(z.real)/(2*np.pi), float(z.imag)/(2*np.pi)]
                                  for z in rs.gauge_eigen(opts(g))])
        for i in range(4):
            ax.plot(t, y[:, i]/KAPPA, color=fs.SERIES[i], lw=1.3, label=names[i])
            ax.plot(t, ref[:, i]/KAPPA, **dict(fs.GUIDE, lw=0.9))
        ax.set_title(LABEL[g], fontsize=9)
        if g == "geodesic":
            ax.set_ylim(-21, 2)
    for ax in axs[-1]:
        ax.set_xlabel("t")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"mode amplitude / $\kappa$")
    axs[0, 0].plot([], [], **dict(fs.GUIDE, lw=0.9), label="linearized system")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=5, fontsize=8, bbox_to_anchor=(0.53, 1.0))
    fs.save(fig, fig_path)
    plt.close(fig)
    # convergence of the Gamma-driver case
    conv = {}
    for N in (32, 64, 128):
        run = cm.find_run(f"gauge_lin_onelog_gd_N{N}")
        t, y, _ = modes(run)
        ref = rs.gauge_linear(opts("onelog_gd"), t, KAPPA)
        conv[N] = dict(run_id=run["run_id"],
                       max_dev_over_kappa=(np.max(np.abs(y - ref), axis=0)/KAPPA).tolist())
    out["onelog_gd_convergence"] = conv
    return out


def finite_profiles(run):
    """Profiles (t, x, alpha, chi, Theta) up to the last dump with finite fields, and the
    time of the first non-finite dump (None if all are finite)."""
    t, _, prof = modes(run)
    for i, p in enumerate(prof):
        if not (np.all(np.isfinite(p[2])) and np.all(np.isfinite(p[3]))):
            return t[:i], prof[:i], float(t[i])
    return t, prof, None


def grad_max(prof):
    return np.array([np.max(np.abs(np.roll(a, -1) - np.roll(a, 1)))/(2*(x[1] - x[0]))
                     for (_, x, a, _, _) in prof])


def nonlinear(fig_prof, fig_grad):
    gs = ["harmonic", "onelog", "conformal", "volume", "kdriver", "onelog_gd"]
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.09, top=0.94, hspace=0.25,
                        wspace=0.08)
    fig2, ax2 = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig2.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.91, wspace=0.33)
    out = {}
    colg = {"harmonic": fs.PAL["blue"], "onelog": fs.PAL["red"],
            "conformal": fs.PAL["yellow"], "volume": fs.PAL["green"],
            "kdriver": fs.PAL["orange"], "onelog_gd": "k"}
    for ax, g in zip(axs.flat, gs):
        m = cm.find_run(f"gauge_nl_{g}_N128", require_done=False)
        t, prof, tfail = finite_profiles(m)
        tsel = [0, 0.25, 1, 2, 2.5, 4.25, 6.75, 10]
        cols = fs.series_colors(len(tsel))
        for c, ts in zip(cols, tsel):
            k = int(np.argmin(np.abs(t - ts)))
            if abs(t[k] - ts) < 0.04:
                ax.plot(prof[k][1], prof[k][2], color=c, lw=1.2, label=f"t = {ts:g}")
        ttl = LABEL[g] + ("" if tfail is None else f" (fails t = {tfail:.2f})")
        ax.set_title(ttl, fontsize=8)
        grad = grad_max(prof)
        ident = []
        if g in IDENT:
            i0 = IDENT[g](prof[0][2], prof[0][3])
            ident = [np.max(np.abs(IDENT[g](a, c) - i0)) for (_, _, a, c, _) in prof]
        ax2[0].semilogy(t, grad, color=colg[g], lw=1.3, label=LABEL[g])
        if ident:
            ax2[1].semilogy(t[1:], np.maximum(ident[1:], 1e-17), color=colg[g], lw=1.3)
        out[g] = dict(run_id=m["run_id"], status=m["status"], t_end=float(t[-1]),
                      first_nonfinite_dump=tfail,
                      alpha_min=float(min(np.min(p[2]) for p in prof)),
                      alpha_max=float(max(np.max(p[2]) for p in prof)),
                      max_grad_alpha=float(np.max(grad)),
                      t_max_grad=float(t[int(np.argmax(grad))]),
                      theta_max=float(max(np.max(np.abs(p[4])) for p in prof)),
                      identity_max=float(np.max(ident)) if ident else None,
                      alpha_end_minus_1=float(np.max(np.abs(prof[-1][2] - 1.0))))
    # resolution dependence of the conformal-time lapse
    res = {}
    for N, ls in ((64, ":"), (128, "-"), (256, "--")):
        try:
            m = cm.find_run(f"gauge_nl_conformal_N{N}", require_done=False)
        except FileNotFoundError:
            continue
        t, prof, tfail = finite_profiles(m)
        gr = grad_max(prof)
        ax2[2].semilogy(t, gr, color=colg["conformal"], ls=ls, lw=1.3, label=f"N = {N}")
        res[N] = dict(run_id=m["run_id"], first_nonfinite_dump=tfail,
                      t=t.tolist(), grad=gr.tolist())
    out["conformal_resolution"] = res
    for ax in axs[-1]:
        ax.set_xlabel("x")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"$\alpha$")
    axs[0, 0].legend(loc="lower left", fontsize=6, ncol=2)
    ax2[0].set_xlabel("t")
    ax2[0].set_ylabel(r"max $|\partial_x\alpha|$ (N = 128)")
    ax2[0].set_ylim(0.05, 40)
    ax2[0].legend(fontsize=5.5, loc="lower right", ncol=2)
    ax2[1].set_xlabel("t")
    ax2[1].set_ylabel("slicing identity residual")
    ax2[2].set_xlabel("t")
    ax2[2].set_ylabel(r"max $|\partial_x\alpha|$, conformal")
    ax2[2].set_xlim(0, 4)
    ax2[2].legend(fontsize=7, loc="upper left")
    fs.save(fig, fig_prof)
    fs.save(fig2, fig_grad)
    plt.close(fig)
    plt.close(fig2)
    return out


def main():
    fs.use_style()
    res = {"linear": linear(os.path.join(cm.FIGS, "gauge_linear")),
           "nonlinear": nonlinear(os.path.join(cm.FIGS, "gauge_nl_profiles"),
                                  os.path.join(cm.FIGS, "gauge_nl_gradient"))}
    cm.save_json(res, os.path.join(cm.TABLES, "gauge.json"))
    L = ["Linear set: K_xx = 1e-6 sin(2 pi x), N = 64, t = 10. Largest departure of the "
         "mode amplitudes (a_s, K_s, h_s, b_c) from the linearized system, over the run, "
         "in units of kappa; largest |Theta|/kappa; for the four slicings with a local "
         "identity, its largest residual / kappa. Written by analysis/ana_gauge.py.", "",
         "| case | run id | F (v_L^2) | eigenvalues / k | dev a_s | dev K_s | dev h_s | dev b_c "
         "| max Theta | identity |", "|---|---|---|---|---|---|---|---|---|---|"]
    for g, r in res["linear"].items():
        if g == "onelog_gd_convergence":
            continue
        ev = sorted((complex(a, b) for a, b in r["eig_over_k"]),
                    key=lambda z: (abs(z.imag), z.real))
        evs = ", ".join(f"{z.real:+.3f}{z.imag:+.3f}i" for z in ev if abs(z) > 1e-9) or "0"
        d = r["max_dev_over_kappa"]
        ide = "-" if r["identity_over_kappa"] is None else f"{r['identity_over_kappa']:.1e}"
        L.append(f"| {g} | {r['run_id']} | {r['F']:.4f} | {evs} | {d[0]:.1e} | {d[1]:.1e} | "
                 f"{d[2]:.1e} | {d[3]:.1e} | {r['theta_max_over_kappa']:.1e} | {ide} |")
    L += ["", "Convergence of the Gamma-driver case (1+log, shift_Gamma 1, eta 2) to the "
          "linearized system:", "", "| N | run id | dev a_s | dev K_s | dev h_s | dev b_c |",
          "|---|---|---|---|---|---|"]
    for N, r in res["linear"]["onelog_gd_convergence"].items():
        d = r["max_dev_over_kappa"]
        L.append(f"| {N} | {r['run_id']} | {d[0]:.1e} | {d[1]:.1e} | {d[2]:.1e} | {d[3]:.1e} |")
    L += ["", "Nonlinear set: K_xx = 1.5 sin(2 pi x), N = 128, t = 10.", "",
          "| case | run id | first non-finite dump | alpha min | alpha max | max d_x alpha "
          "(at t) | max Theta | identity residual | max abs(alpha-1) at last finite dump |",
          "|---|---|---|---|---|---|---|---|---|"]
    for g, r in res["nonlinear"].items():
        if g == "conformal_resolution":
            continue
        ide = "-" if r["identity_max"] is None else f"{r['identity_max']:.1e}"
        tf = "none (t = 10 reached)" if r["first_nonfinite_dump"] is None \
            else f"{r['first_nonfinite_dump']:.4f}"
        L.append(f"| {g} | {r['run_id']} | {tf} | "
                 f"{r['alpha_min']:.4f} | {r['alpha_max']:.4f} | {r['max_grad_alpha']:.3g} "
                 f"({r['t_max_grad']:.2f}) | {r['theta_max']:.1e} | {ide} | "
                 f"{r['alpha_end_minus_1']:.1e} |")
    L += ["", "Conformal-time lapse, kappa = 1.5, resolution dependence:", "",
          "| N | run id | first non-finite dump | max d_x alpha at t = 1, 1.5, 2 |",
          "|---|---|---|---|"]
    for N, r in res["nonlinear"]["conformal_resolution"].items():
        tt = np.asarray(r["t"])
        gg = np.asarray(r["grad"])
        vals = ", ".join(f"{gg[int(np.argmin(np.abs(tt - x)))]:.3f}" for x in (1.0, 1.5, 2.0))
        tf = "none" if r["first_nonfinite_dump"] is None else f"{r['first_nonfinite_dump']:.4f}"
        L.append(f"| {N} | {r['run_id']} | {tf} | {vals} |")
    with open(os.path.join(cm.TABLES, "gauge.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
