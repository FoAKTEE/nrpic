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
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.07, top=0.96, hspace=0.28,
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
            ident = max(np.max(np.abs(IDENT[g](a, c) - 1.0)) for _, _, a, c, _ in prof)/KAPPA
        thmax = max(np.max(np.abs(th)) for _, _, _, _, th in prof)/KAPPA
        out[g] = dict(run_id=run["run_id"], max_dev_over_kappa=dev.tolist(),
                      max_ref_over_kappa=scale.tolist(), identity_over_kappa=ident,
                      theta_max_over_kappa=thmax, F=rs.gauge_F(opts(g)),
                      eig_over_k=[complex(z)/(2*np.pi) for z in rs.gauge_eigen(opts(g))])
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
    axs[0, 0].legend(loc="lower left", ncol=3, fontsize=7)
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


def nonlinear(fig_prof, fig_grad):
    gs = ["harmonic", "onelog", "conformal", "volume", "kdriver", "onelog_gd"]
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.09, top=0.94, hspace=0.25,
                        wspace=0.28)
    fig2, ax2 = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig2.subplots_adjust(left=0.09, right=0.99, bottom=0.15, top=0.92, wspace=0.27)
    out = {}
    for j, (ax, g) in enumerate(zip(axs.flat, gs)):
        m = cm.find_run(f"gauge_nl_{g}_N128", require_done=False)
        t, y, prof = modes(m)
        tsel = [0, 1, 2, 4, 6, 8, 10]
        cols = fs.series_colors(len(tsel))
        for c, ts in zip(cols, tsel):
            k = int(np.argmin(np.abs(t - ts)))
            if abs(t[k] - ts) < 0.04:
                ax.plot(prof[k][1], prof[k][2], color=c, lw=1.2, label=f"t = {ts}")
        ax.set_title(LABEL[g], fontsize=9)
        grad = []
        ident = []
        for (tt, x, a, c, th) in prof:
            dx = x[1] - x[0]
            grad.append(np.max(np.abs(np.roll(a, -1) - np.roll(a, 1)))/(2*dx))
            if g in IDENT:
                i0 = IDENT[g](prof[0][2], prof[0][3])
                ident.append(np.max(np.abs(IDENT[g](a, c) - i0)))
        ax2[0].semilogy(t, grad, color=fs.SERIES[j % 5] if j < 5 else "k", lw=1.3,
                        label=LABEL[g])
        if ident:
            ax2[1].semilogy(t, np.maximum(ident, 1e-17), color=fs.SERIES[j % 5], lw=1.3,
                            label=LABEL[g])
        last = t[-1]
        out[g] = dict(run_id=m["run_id"], status=m["status"], last_dump_time=float(last),
                      alpha_min=float(min(np.min(p[2]) for p in prof)),
                      alpha_max=float(max(np.max(p[2]) for p in prof)),
                      max_grad_alpha=float(np.max(grad)),
                      t_max_grad=float(t[int(np.argmax(grad))]),
                      identity_max=float(np.max(ident)) if ident else None)
    for ax in axs[-1]:
        ax.set_xlabel("x")
    for ax in axs[:, 0]:
        ax.set_ylabel(r"$\alpha$")
    axs[0, 0].legend(loc="upper right", fontsize=7, ncol=2)
    ax2[0].set_xlabel("t")
    ax2[0].set_ylabel(r"max $|\partial_x\alpha|$")
    ax2[1].set_xlabel("t")
    ax2[1].set_ylabel("max departure from the slicing identity")
    ax2[0].legend(fontsize=7, loc="upper left")
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
        ev = sorted(r["eig_over_k"], key=lambda z: (abs(z.imag), z.real))
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
          "| case | run id | status | last dump | alpha min | alpha max | max d_x alpha "
          "(at t) | identity residual |", "|---|---|---|---|---|---|---|---|"]
    for g, r in res["nonlinear"].items():
        ide = "-" if r["identity_max"] is None else f"{r['identity_max']:.1e}"
        L.append(f"| {g} | {r['run_id']} | {r['status']} | {r['last_dump_time']:.3f} | "
                 f"{r['alpha_min']:.4f} | {r['alpha_max']:.4f} | {r['max_grad_alpha']:.3g} "
                 f"({r['t_max_grad']:.2f}) | {ide} |")
    with open(os.path.join(cm.TABLES, "gauge.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
