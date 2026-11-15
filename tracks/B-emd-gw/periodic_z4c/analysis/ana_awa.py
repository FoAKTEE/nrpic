#!/usr/bin/env python3
"""Analysis of the Apples-with-Apples gauge wave (set awa_gw) in the proper-length
coordinate X of the initial slice (refsol.py, item 2).

Errors of gamma_XX = gt_xx/chi and of alpha against refsol.gw_exact_X, in units of the
amplitude A (largest over the line and root mean square); Hamiltonian and momentum
constraints from the con tables; orders between N = 50, 100, 200 at t = 20; growth to
t = 200 at N = 50. Writes figs/awa_*.{pdf,png}, tables/awa.json, tables/awa.md.

    python3 ana_awa.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt

import common as cm
import athena_dumps as ad
import refsol as rs
from nrpic import figstyle as fs


def analyse(name, A):
    m = cm.find_run(name, require_done=False)
    files = cm.tab_files(m)
    cfiles = cm.tab_files(m, "con")
    d0 = ad.read_tab(files[0])
    X = d0["x1v"]
    x = rs.gw_x_of_X(X, A)
    # time of a dump from its cycle (constant step cfl*dx, cfl = 0.25 in gauge.athinput):
    # the table header prints the time with 7 digits, i.e. 5e-5 at t = 100, which would
    # enter the comparison with the exact solution as a phase error of 3e-4
    dt_step = 0.25*(X[1] - X[0])
    t_end = ad.read_tab(files[-1])["time"]
    t, eg, ea, eg2, ea2, H, Mx, ek = [], [], [], [], [], [], [], []
    keep = {}
    for p, pc in zip(files, cfiles):
        d = ad.read_tab(p)
        c = ad.read_tab(pc)
        d["time"] = min(d["cycle"]*dt_step, t_end)
        ex = rs.gw_exact_X(X, d["time"], A, x_of_X=x)
        g = d["gxx"]/d["chi"]
        dg = (g - ex["gamma_XX"])/A
        da = (d["alpha"] - ex["alpha"])/A
        dk = (d["Khat"] + 2*d["Theta"] - ex["K"])/(2*np.pi*A)
        t.append(d["time"])
        eg.append(np.max(np.abs(dg)))
        ea.append(np.max(np.abs(da)))
        eg2.append(np.sqrt(np.mean(dg**2)))
        ea2.append(np.sqrt(np.mean(da**2)))
        ek.append(np.max(np.abs(dk)))
        H.append(np.max(np.abs(c["con_H"])))
        Mx.append(np.max(np.abs(c["con_Mx"])))
        for ts in (0.0, 10.0, 20.0, 100.0, 200.0):
            if abs(d["time"] - ts) < 1e-6:
                keep[ts] = (X.copy(), g.copy(), d["alpha"].copy(), ex["gamma_XX"],
                            ex["alpha"])
    o = np.argsort(t)
    r = {k: np.asarray(v)[o] for k, v in dict(t=t, eg=eg, ea=ea, eg2=eg2, ea2=ea2, ek=ek,
                                                H=H, Mx=Mx).items()}
    r["run_id"], r["status"], r["profiles"] = m["run_id"], m["status"], keep
    return r


def main():
    fs.use_style()
    res = {}
    for A in (0.01, 0.1):
        for N, T in ((50, 20), (100, 20), (200, 20), (50, 200)):
            res[(A, N, T)] = analyse(f"awa_gw_A{A:g}_N{N}_T{T:g}", A)

    # ---- figure 1: error histories to t = 20 and constraint norms
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.94, hspace=0.07,
                        wspace=0.24)
    for col, A in enumerate((0.01, 0.1)):
        for i, N in enumerate((50, 100, 200)):
            r = res[(A, N, 20)]
            m = r["t"] > 0
            axs[0, col].semilogy(r["t"][m], r["eg"][m], color=fs.SERIES[i], label=f"N = {N}")
            axs[0, col].semilogy(r["t"][m], r["ea"][m], color=fs.SERIES[i], ls="--", lw=1.0)
            axs[1, col].semilogy(r["t"][m], r["H"][m], color=fs.SERIES[i])
            axs[1, col].semilogy(r["t"][m], r["Mx"][m], color=fs.SERIES[i], ls="--", lw=1.0)
        axs[0, col].set_title(f"gauge wave A = {A}", fontsize=10)
        axs[1, col].set_xlabel("t (crossings)")
    axs[0, 0].set_ylabel(r"max error / A")
    axs[1, 0].set_ylabel("max |H| (solid), |M_x| (dashed)")
    axs[0, 0].plot([], [], color="k", lw=1.0, ls="--", label=r"$\alpha$ (dashed)")
    axs[0, 0].plot([], [], color="k", lw=1.5, label=r"$\gamma_{XX}$ (solid)")
    axs[0, 0].legend(fontsize=7, ncol=2, loc="lower right")
    fs.save(fig, os.path.join(cm.FIGS, "awa_history"))
    plt.close(fig)

    # ---- figure 2: long runs at N = 50 and profiles
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.92, wspace=0.27)
    for i, A in enumerate((0.01, 0.1)):
        r = res[(A, 50, 200)]
        m = r["t"] > 0
        axs[0].loglog(r["t"][m], r["eg"][m], color=fs.SERIES[i], label=f"A = {A}: " + r"$\gamma_{XX}$")
        axs[0].loglog(r["t"][m], r["H"][m]/(A*(2*np.pi)**2), color=fs.SERIES[i], ls="--",
                      lw=1.0, label=f"A = {A}: " + r"$|H|/(4\pi^2 A)$")
    tt = np.array([1.0, 200.0])
    axs[0].loglog(tt, 3e-6*tt, **dict(fs.THIN, ls=":"))
    axs[0].text(20, 3e-6*20*2.5, r"$\propto t$", fontsize=9)
    axs[0].set_xlabel("t (crossings)")
    axs[0].set_ylabel("max error / A, N = 50")
    axs[0].legend(fontsize=7, loc="upper left")
    r = res[(0.1, 50, 200)]
    for j, ts in enumerate(sorted(r["profiles"])):
        X, g, a, gex, aex = r["profiles"][ts]
        axs[1].plot(X, a, color=fs.series_colors(len(r["profiles"]))[j], lw=1.3,
                    label=f"t = {ts:g}")
        axs[1].plot(X, aex, **dict(fs.GUIDE, lw=0.8))
    axs[1].set_xlabel("X")
    axs[1].set_ylabel(r"$\alpha$ (A = 0.1, N = 50; dashed: exact)")
    axs[1].legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(cm.FIGS, "awa_long"))
    plt.close(fig)

    # ---- table
    out = {}
    L = ["Gauge wave, harmonic slicing, zero shift, production numerics, proper-length "
         "coordinates. Errors relative to A at t = 20 (largest over the line, and rms), "
         "largest |H|, |M_x|; orders between successive N. Written by analysis/ana_awa.py.",
         "", "| A | N | run id | max err gamma_XX | rms err gamma_XX | max err alpha | "
         "max err K/(2 pi A) | max H | max Mx | order max gamma | order rms gamma | order H |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for A in (0.01, 0.1):
        Ns = (50, 100, 200)
        rows = [res[(A, N, 20)] for N in Ns]
        idx = [int(np.argmin(np.abs(r["t"] - 20.0))) for r in rows]
        eg = [r["eg"][i] for r, i in zip(rows, idx)]
        e2 = [r["eg2"][i] for r, i in zip(rows, idx)]
        Hh = [r["H"][i] for r, i in zip(rows, idx)]
        og, o2, oH = cm.orders(eg), cm.orders(e2), cm.orders(Hh)
        out[str(A)] = []
        for j, (N, r, i) in enumerate(zip(Ns, rows, idx)):
            row = dict(N=N, run_id=r["run_id"], t=r["t"][i], err_g_max=r["eg"][i],
                       err_g_rms=r["eg2"][i], err_a_max=r["ea"][i], err_K_max=r["ek"][i],
                       H_max=r["H"][i], Mx_max=r["Mx"][i],
                       order_g_max=og[j - 1] if j else None,
                       order_g_rms=o2[j - 1] if j else None,
                       order_H=oH[j - 1] if j else None)
            out[str(A)].append(row)
            f = lambda v: "-" if v is None else f"{v:.2f}"
            L.append(f"| {A} | {N} | {r['run_id']} | {row['err_g_max']:.3e} | "
                     f"{row['err_g_rms']:.3e} | {row['err_a_max']:.3e} | {row['err_K_max']:.3e} | "
                     f"{row['H_max']:.2e} | {row['Mx_max']:.2e} | {f(row['order_g_max'])} | "
                     f"{f(row['order_g_rms'])} | {f(row['order_H'])} |")
        rl = res[(A, 50, 200)]
        out[f"{A}_long"] = dict(run_id=rl["run_id"], status=rl["status"],
                                t_end=float(rl["t"][-1]),
                                err_g_max={str(ts): float(rl["eg"][int(np.argmin(np.abs(rl["t"] - ts)))])
                                           for ts in (10, 20, 50, 100, 200)},
                                H_max={str(ts): float(rl["H"][int(np.argmin(np.abs(rl["t"] - ts)))])
                                       for ts in (10, 20, 50, 100, 200)})
    L += ["", "Long runs, N = 50 (output every crossing): largest error of gamma_XX / A and "
          "largest |H| at t = 10, 20, 50, 100, 200.", "",
          "| A | run id | status | t end | err 10 | err 20 | err 50 | err 100 | err 200 | "
          "H 10 | H 200 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for A in (0.01, 0.1):
        r = out[f"{A}_long"]
        e, h = r["err_g_max"], r["H_max"]
        L.append(f"| {A} | {r['run_id']} | {r['status']} | {r['t_end']:.1f} | {e['10']:.2e} | "
                 f"{e['20']:.2e} | {e['50']:.2e} | {e['100']:.2e} | {e['200']:.2e} | "
                 f"{h['10']:.2e} | {h['200']:.2e} |")
    cm.save_json(out, os.path.join(cm.TABLES, "awa.json"))
    with open(os.path.join(cm.TABLES, "awa.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
