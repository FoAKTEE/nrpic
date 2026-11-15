#!/usr/bin/env python3
"""Analysis of the TT wave along x (sets lw_x_prod, lw_x_ref, lw_x_nodiss).

For every table dump: h_+ = (gt_zz - gt_yy)/2 and At_+ = (At_zz - At_yy)/2 are projected
on sin and cos of 2 pi x; amplitude error A/A0 - 1 and phase error (numerical minus exact
phase advance 2 pi t; negative = lagging) against the exact linear solution; relative
L2 error of the whole profile; largest excursion of the variables that vanish at first
order (alpha - 1, beta, chi - 1, Khat, Theta, Gamma). Writes figs/lw_x_*.{pdf,png},
tables/lw_x.json and tables/lw_x.md.

    python3 ana_lw.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt

import common as cm
import athena_dumps as ad
import predict_lw as pl
from nrpic import figstyle as fs

A0 = 1.0e-6
SETS = {"lw_x_prod": dict(ng=4, cfl=0.25, sigma=0.5, Ns=(16, 32, 64, 128)),
        "lw_x_ref": dict(ng=3, cfl=0.3, sigma=1.0, Ns=(16, 32, 64, 128)),
        "lw_x_nodiss": dict(ng=4, cfl=0.25, sigma=0.0, Ns=(32, 64))}


def analyse_run(run, cfl, N, A0=A0):
    """The time of a dump is cycle * cfl / N (constant step), capped at the end time:
    the header of a table prints the time with 7 digits only, which puts a sawtooth of
    up to 2 pi * 5e-7 rad on the phase after t = 1 when the outputs do not fall on steps."""
    t, amp, ph, l2h, l2a, ampA, phA, side = [], [], [], [], [], [], [], []
    files = cm.tab_files(run)
    t_end = ad.read_tab(files[-1])["time"]
    for p in files:
        d = ad.read_tab(p)
        d["time"] = min(d["cycle"]*cfl/N, t_end)
        x = d["x1v"]
        hp = 0.5*(d["gzz"] - d["gyy"])
        ap = 0.5*(d["Azz"] - d["Ayy"])
        s, c = cm.project(x, hp, 1, 1.0)
        z = (s + 1j*c)*np.exp(1j*2*np.pi*d["time"])     # = A e^{-i dpsi}
        t.append(d["time"])
        amp.append(abs(z)/A0 - 1.0)
        ph.append(-np.angle(z))
        # At_+ = pi A cos(2 pi x - psi): project, convert to the same convention
        sa, ca = cm.project(x, ap, 1, 1.0)
        za = (ca - 1j*sa)*np.exp(1j*2*np.pi*d["time"])/(np.pi)
        ampA.append(abs(za)/A0 - 1.0)
        phA.append(-np.angle(za))
        ex = A0*np.sin(2*np.pi*(x - d["time"]))
        exa = np.pi*A0*np.cos(2*np.pi*(x - d["time"]))
        l2h.append(np.sqrt(np.mean((hp - ex)**2))/A0)
        l2a.append(np.sqrt(np.mean((ap - exa)**2))/(np.pi*A0))
        side.append(max(np.max(np.abs(d["alpha"] - 1)), np.max(np.abs(d["chi"] - 1)),
                        np.max(np.abs(d["Khat"])), np.max(np.abs(d["Theta"])),
                        np.max(np.abs(d["betax"])), np.max(np.abs(d["Gamx"])),
                        np.max(np.abs(d["gxx"] - 1)), np.max(np.abs(d["gxy"])),
                        np.max(np.abs(d["gyz"]))))
    o = np.argsort(t)
    return {k: np.asarray(v)[o] for k, v in dict(t=t, amp=amp, ph=ph, l2h=l2h, l2a=l2a,
                                                    ampA=ampA, phA=phA, side=side).items()}


def main():
    fs.use_style()
    os.makedirs(cm.FIGS, exist_ok=True)
    res = {}
    for sname, cfg in SETS.items():
        res[sname] = {}
        for N in cfg["Ns"]:
            run = cm.find_run(f"{sname}_N{N}")
            r = analyse_run(run, cfg["cfl"], N)
            r["run_id"] = run["run_id"]
            pa, pp, _, _, _ = pl.predict(cfg["ng"], cfg["cfl"], cfg["sigma"], r["t"][-1], N)
            r["pred_amp"], r["pred_ph"] = pa, pp
            # predicted time series
            r["pred_amp_t"] = np.array([pl.predict(cfg["ng"], cfg["cfl"], cfg["sigma"],
                                                   tt, N)[0] if tt > 0 else 0.0
                                        for tt in r["t"]])
            r["pred_ph_t"] = np.array([pl.predict(cfg["ng"], cfg["cfl"], cfg["sigma"],
                                                  tt, N)[1] if tt > 0 else 0.0
                                       for tt in r["t"]])
            res[sname][N] = r

    # ---------------- figure 1: error histories, prod and ref
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.94, hspace=0.06,
                        wspace=0.22)
    for col, sname in enumerate(("lw_x_prod", "lw_x_ref")):
        for i, (N, r) in enumerate(res[sname].items()):
            colr = fs.SERIES[i]
            m = r["t"] > 0
            axs[0, col].semilogy(r["t"][m], np.abs(r["amp"][m]), color=colr, label=f"N = {N}")
            axs[0, col].semilogy(r["t"][m], np.abs(r["pred_amp_t"][m]), **dict(fs.GUIDE, lw=1.0))
            axs[1, col].semilogy(r["t"][m], np.abs(r["ph"][m]), color=colr)
            axs[1, col].semilogy(r["t"][m], np.abs(r["pred_ph_t"][m]), **dict(fs.GUIDE, lw=1.0))
        axs[0, col].set_title({"lw_x_prod": "production: ng 4, Courant 0.25, KO 0.5",
                               "lw_x_ref": "upstream input: ng 3, Courant 0.3, KO 1"}[sname],
                              fontsize=10)
        axs[1, col].set_xlabel("t (box crossings)")
        axs[0, col].set_ylabel(r"$|A/A_0 - 1|$")
        axs[1, col].set_ylabel(r"$|\delta\varphi|$ (rad)")
    axs[0, 0].plot([], [], **dict(fs.GUIDE, lw=1.0), label="Fourier symbol of the scheme")
    axs[0, 0].legend(loc="lower right", ncol=2, fontsize=8)
    fs.save(fig, os.path.join(cm.FIGS, "lw_x_history"))
    plt.close(fig)

    # ---------------- figure 2: convergence at t = 10
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.92, wspace=0.25)
    styles = {"lw_x_prod": (fs.PAL["red"], "o", "production"),
              "lw_x_ref": (fs.PAL["blue"], "s", "upstream input"),
              "lw_x_nodiss": (fs.PAL["green"], "^", "production, no KO")}
    for sname, (colr, mk, lab) in styles.items():
        Ns = np.array(sorted(res[sname]))
        ea = [abs(res[sname][N]["amp"][-1]) for N in Ns]
        ep = [abs(res[sname][N]["ph"][-1]) for N in Ns]
        pa = [abs(res[sname][N]["pred_amp"]) for N in Ns]
        pp = [abs(res[sname][N]["pred_ph"]) for N in Ns]
        axs[0].loglog(Ns, ea, mk, color=colr, label=lab, ms=6)
        axs[0].loglog(Ns, pa, color=colr, lw=1.0, ls="--")
        axs[1].loglog(Ns, ep, mk, color=colr, ms=6)
        axs[1].loglog(Ns, pp, color=colr, lw=1.0, ls="--")
    for ax, ttl in zip(axs, ("amplitude error at t = 10", "phase error at t = 10 (rad)")):
        ax.set_xlabel("cells per wavelength N")
        ax.set_title(ttl, fontsize=10)
        ax.set_xticks([16, 32, 64, 128])
        ax.set_xticklabels(["16", "32", "64", "128"])
        ax.xaxis.set_minor_formatter(plt.NullFormatter())
    Nn = np.array([16, 128.0])
    axs[1].loglog(Nn, 3e-3*(Nn/16)**-4, **dict(fs.THIN, ls=":"))
    axs[1].text(20, 3e-3*(20/16)**-4*0.25, r"$N^{-4}$", fontsize=9)
    axs[0].loglog(Nn, 2e-3*(Nn/16)**-5, **dict(fs.THIN, ls=":"))
    axs[0].text(20, 2e-3*(20/16)**-5*0.2, r"$N^{-5}$", fontsize=9)
    axs[0].plot([], [], color="k", lw=1.0, ls="--", label="Fourier symbol (prediction)")
    axs[0].legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(cm.FIGS, "lw_x_convergence"))
    plt.close(fig)

    # ---------------- table
    out = {}
    lines = ["| set | N | run id | amplitude error | predicted | phase error (rad) | predicted "
             "| L2(h+)/A | order amp | order phase | order L2 | max first-order-zero field |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sname in SETS:
        Ns = sorted(res[sname])
        oa = cm.orders([res[sname][N]["amp"][-1] for N in Ns])
        op = cm.orders([res[sname][N]["ph"][-1] for N in Ns])
        ol = cm.orders([res[sname][N]["l2h"][-1] for N in Ns])
        out[sname] = []
        for i, N in enumerate(Ns):
            r = res[sname][N]
            row = dict(N=N, run_id=r["run_id"], t=r["t"][-1], amp=r["amp"][-1],
                       pred_amp=r["pred_amp"], phase=r["ph"][-1], pred_phase=r["pred_ph"],
                       l2h=r["l2h"][-1], l2a=r["l2a"][-1], ampA=r["ampA"][-1],
                       phaseA=r["phA"][-1], side_max=float(np.max(r["side"])),
                       order_amp=oa[i - 1] if i else None,
                       order_phase=op[i - 1] if i else None,
                       order_l2=ol[i - 1] if i else None)
            out[sname].append(row)
            f = lambda v: "-" if v is None else f"{v:.2f}"
            lines.append(f"| {sname} | {N} | {r['run_id']} | {row['amp']:+.3e} | "
                         f"{row['pred_amp']:+.3e} | {row['phase']:+.3e} | "
                         f"{row['pred_phase']:+.3e} | {row['l2h']:.3e} | {f(row['order_amp'])} | "
                         f"{f(row['order_phase'])} | {f(row['order_l2'])} | "
                         f"{row['side_max']:.1e} |")
    cm.save_json(out, os.path.join(cm.TABLES, "lw_x.json"))
    os.makedirs(cm.TABLES, exist_ok=True)
    with open(os.path.join(cm.TABLES, "lw_x.md"), "w") as f:
        f.write("TT wave along x, t = 10 (ten crossings), A0 = 1e-6. Orders between "
                "successive resolutions (log2 of the error ratio). Written by "
                "analysis/ana_lw.py.\n\n")
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def roundoff():
    """Set lw_x_roundoff: does the departure from the Fourier prediction at N = 128 scale
    as 1/A? Figure figs/lw_x_roundoff, table tables/lw_x_roundoff.md."""
    cases = [("lw_x_prod_N128", 4, 0.25, 0.5, 1e-6, "prod, A = 1e-6", fs.PAL["red"], "-"),
             ("lw_x_prod_A1e-5_N128", 4, 0.25, 0.5, 1e-5, "prod, A = 1e-5", fs.PAL["red"], "--"),
             ("lw_x_ref_N128", 3, 0.3, 1.0, 1e-6, "ref (1+log), A = 1e-6", fs.PAL["blue"], ":"),
             ("lw_x_refconf_A1e-6_N128", 3, 0.3, 1.0, 1e-6, "ref numerics, conformal, A = 1e-6",
              fs.PAL["blue"], "-"),
             ("lw_x_refconf_A1e-5_N128", 3, 0.3, 1.0, 1e-5, "ref numerics, conformal, A = 1e-5",
              fs.PAL["blue"], "--"),
             ("lw_x_prod_A1e-7_N128", 4, 0.25, 0.5, 1e-7, "prod, A = 1e-7", fs.PAL["yellow"], "-"),
             ("lw_x_refconf_A1e-7_N128", 3, 0.3, 1.0, 1e-7, "ref numerics, conformal, A = 1e-7",
              fs.PAL["green"], "-")]
    fig, (ax, axr) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    L = ["| case | run id | A | phase error at t = 10 | predicted | departure | "
         "amplitude error | predicted |", "|---|---|---|---|---|---|---|---|"]
    out = []
    for nm, ng, cfl, sig, A, lab, colr, ls in cases:
        run = cm.find_run(nm)
        r = analyse_run(run, cfl, 128, A0=A)
        pa, pp, _, _, _ = pl.predict(ng, cfl, sig, r["t"][-1], 128)
        m = r["t"] > 0
        ax.plot(r["t"][m], r["ph"][m], color=colr, ls=ls, lw=1.3, label=lab)
        out.append(dict(name=nm, run_id=run["run_id"], A=A, phase=r["ph"][-1], pred_phase=pp,
                        amp=r["amp"][-1], pred_amp=pa))
        L.append(f"| {nm} | {run['run_id']} | {A:g} | {r['ph'][-1]:+.3e} | {pp:+.3e} | "
                 f"{r['ph'][-1] - pp:+.2e} | {r['amp'][-1]:+.3e} | {pa:+.3e} |")
    for ng, cfl, sig in ((4, 0.25, 0.5), (3, 0.3, 1.0)):
        tt = np.linspace(0.0625, 10, 80)
        ax.plot(tt, [pl.predict(ng, cfl, sig, x, 128)[1] for x in tt], **dict(fs.GUIDE, lw=0.9))
    ax.plot([], [], **dict(fs.GUIDE, lw=0.9), label="Fourier symbol")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\delta\varphi$ (rad), N = 128")
    ax.legend(fontsize=6, loc="upper left")
    for key, colr, mk, lab in (("prod", fs.PAL["red"], "o", "production numerics"),
                               ("ref", fs.PAL["blue"], "s", "ng 3, KO 1, Courant 0.3")):
        rows = [o for o in out if o["name"].startswith("lw_x_" + key)
                and "lw_x_ref_N128" != o["name"]]
        A = np.array([o["A"] for o in rows])
        dep = np.array([abs(o["phase"] - o["pred_phase"]) for o in rows])
        k = np.argsort(A)
        axr.loglog(A[k], dep[k], mk + "-", color=colr, lw=1.0, label=lab)
    Ag = np.array([1e-7, 1e-6])
    axr.loglog(Ag, 6e-7*(Ag/1e-7)**-1, **dict(fs.THIN, ls=":"))
    axr.text(2.5e-7, 4e-7, r"$\propto A^{-1}$", fontsize=9)
    axr.set_xlabel("wave amplitude A")
    axr.set_ylabel(r"|measured $-$ predicted phase| at t = 10")
    axr.legend(fontsize=7, loc="upper center")
    fs.save(fig, os.path.join(cm.FIGS, "lw_x_roundoff"))
    plt.close(fig)
    cm.save_json(out, os.path.join(cm.TABLES, "lw_x_roundoff.json"))
    with open(os.path.join(cm.TABLES, "lw_x_roundoff.md"), "w") as f:
        f.write("TT wave along x at N = 128, t = 10: departure of the phase from the "
                "Fourier-symbol prediction against the amplitude A and the lapse. Written by "
                "analysis/ana_lw.py.\n\n" + "\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
    roundoff()
