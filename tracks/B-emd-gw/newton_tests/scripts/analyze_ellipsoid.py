#!/usr/bin/env python3
"""Tests N1 and N3 of newton_tests: the static isolated Zel'dovich ellipsoid (model C of
tracks/B-emd-gw/baseline/BASELINE.md) in AthenaK's Newtonian mode, against the ODE of
baseline/scripts/ellipsoid.py, and the self-similarity of the rescaled runs.

    analyze_ellipsoid.py --out DIR --run N:CASE [--run N:CASE ...] [--dtcheck N:CASE]
                         [--selfsim N:DIR ...]

CASE is a case directory of scripts/run_case.sh (particles.json, newton.newton.hst,
snapshots); DIR of --selfsim holds alpha_<value>/ case directories (run_selfsim.sh).
Quantities: the trace-free quadrupole Q_ij = I_ij - delta_ij I_kk/3 of the history
columns 19-42 (second moment about the origin, which is the centre of mass of the
ellipsoid) and its first three time derivatives; the first crossing t_x of the x axis as
the zero of dI_xx; the quadrupole-formula power P = (1/5) Q''':Q''' and the energy
E(t_turn -> t_x), from the raw one-step difference quotient of the history and from Q'''
averaged over a window of 0.05 t_turn (the same average applied to the ODE). The ODE is
integrated twice: from the nominal Zel'dovich state, and from the equivalent ellipsoid
of the particle lattice (same mass and second moments, velocities scaled with the axes).
Writes DIR/ellipsoid.json and figures DIR/ell_*.{pdf,png}.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "B-emd-gw", "baseline", "scripts"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402
import ellipsoid as el  # noqa: E402

WIN_FRAC = 0.05          # averaging window of Q''' in units of t_turn
COLS = {32: fs.PAL["green"], 64: fs.PAL["yellow"], 128: fs.PAL["red"]}
LS = ("-", "--", ":")


def pairs(items):
    out = []
    for s in items or []:
        n, d = s.split(":", 1)
        out.append((int(n), d))
    return out


def ode(lam, R0=None, V0=None, t_end=None, model="C"):
    """el.integrate from the nominal Zel'dovich state, or from (R0, V0) at t_turn."""
    t0 = el.t_turn(lam[0])
    if R0 is None:
        return el.integrate(np.asarray(lam), model, t_end)
    keep = el.initial_state
    try:
        el.initial_state = lambda lam_, t0_=None: (t0, np.asarray(R0, float),
                                                   np.asarray(V0, float))
        return el.integrate(np.asarray(lam), model, t_end)
    finally:
        el.initial_state = keep


def smooth(y, nhalf):
    """Moving average over 2 nhalf + 1 samples, truncated at the ends (axis 0)."""
    if nhalf <= 0:
        return y.copy()
    c = np.cumsum(np.concatenate([np.zeros((1,) + y.shape[1:]), y]), axis=0)
    n = len(y)
    i = np.arange(n)
    lo = np.maximum(i - nhalf, 0)
    hi = np.minimum(i + nhalf + 1, n)
    return (c[hi] - c[lo])/(hi - lo).reshape((-1,) + (1,)*(y.ndim - 1))


def zero_up(t, y):
    """First time where y goes from negative to non-negative (linear interpolation)."""
    s = np.flatnonzero((y[:-1] < 0.0) & (y[1:] >= 0.0))
    if len(s) == 0:
        return np.nan
    i = s[0]
    return float(t[i] - y[i]*(t[i + 1] - t[i])/(y[i + 1] - y[i]))


def energy(t, P, t1, t2):
    m = (t >= t1) & (t <= t2)
    tt, pp = t[m], P[m]
    # close the interval at t2 by linear interpolation
    if tt[-1] < t2 and np.any(t > t2):
        j = np.flatnonzero(t > t2)[0]
        p2 = P[j - 1] + (P[j] - P[j - 1])*(t2 - t[j - 1])/(t[j] - t[j - 1])
        tt, pp = np.append(tt, t2), np.append(pp, p2)
    return float(np.trapezoid(pp, tt))


def diag(Q):
    return np.stack([Q[:, 0, 0], Q[:, 1, 1], Q[:, 2, 2]], axis=1)


def case_analysis(n, case):
    meta = json.load(open(os.path.join(case, "particles.json")))
    h = nw.read_newton_hst(os.path.join(case, "newton.newton.hst"))
    lam = np.array(meta["lam"])
    t0 = meta["t_turn"]
    M = meta["mass"]
    t = t0 + h["time"]
    t3 = t0 + h["time_d3I"]
    dt = float(np.median(np.diff(h["time"])))
    nhalf = int(round(0.5*WIN_FRAC*t0/dt))
    Q = [diag(nw.quadrupole(h, k)) for k in range(4)]
    off = max(float(np.abs(nw.quadrupole(h, k)[:, i, j]).max()/np.abs(Q[k]).max())
              for k in range(4) for i, j in ((0, 1), (0, 2), (1, 2)))
    R0, V0 = np.array(meta["R0"]), np.array(meta["V0"])
    I0 = np.array(meta["I0"])
    Reff = np.sqrt(5.0*np.diag(I0)/M)
    Veff = V0/R0*Reff
    t_end = t[-1] + 1.0
    runs = {"nominal": ode(lam, t_end=t_end), "equivalent": ode(lam, Reff, Veff, t_end)}
    out = {"case": case, "n": n, "alpha": float(lam[0]), "t_turn": t0, "mass": M,
           "nparticle": meta["nparticle"], "dt": dt, "window": 2*nhalf*dt,
           "R_equivalent_over_nominal": (Reff/R0).tolist(), "offdiag_max_rel": off}
    tx = t0 + zero_up(h["time"], h["dI_xx"])
    out["t_x"] = tx
    out["tau_x"] = tx/t0
    q3raw = Q[3]
    q3s = smooth(q3raw, nhalf)
    Praw = 0.2*np.sum(q3raw**2, axis=1)
    Ps = 0.2*np.sum(q3s**2, axis=1)
    out["E_raw"] = energy(t3, Praw, t0, tx)
    out["E_avg"] = energy(t3, Ps, t0, tx)
    ref = {}
    for key, r in runs.items():
        tx_o = r["crossings"][0][0]
        E_o = float(r["segments"][0].y[6, -1])
        so = el.sample(r, t)
        s3 = el.sample(r, t3)
        q3o = s3["Q"][3]
        q3os = smooth(q3o, nhalf)
        Pos = 0.2*np.sum(q3os**2, axis=1)
        win = t <= tx_o - 1.0
        win3 = t3 <= tx_o - 1.0
        e = {"t_x": tx_o, "E": E_o, "E_avg_same_window": energy(t3, Pos, t0, tx_o),
             "E_over_M": E_o/M}
        e["dt_x_rel"] = (tx - tx_o)/tx_o
        # the resolved part: up to one t_k before the ODE crossing (R_x > 0.48 there)
        te = tx_o - 1.0
        e["E_early_ode_avg"] = energy(t3, Pos, t0, te)
        e["E_early_avg"] = energy(t3, Ps, t0, te)
        e["dE_early_rel"] = (e["E_early_avg"] - e["E_early_ode_avg"])/e["E_early_ode_avg"]
        e["dE_avg_rel"] = (out["E_avg"] - E_o)/E_o
        e["dE_raw_rel"] = (out["E_raw"] - E_o)/E_o
        e["dE_avg_vs_avg_ode_rel"] = (out["E_avg"] - e["E_avg_same_window"]) \
            / e["E_avg_same_window"]
        for k, name in enumerate(("Q", "Q1", "Q2")):
            e["%s_maxerr_over_max" % name] = float(
                np.abs(Q[k][win] - so["Q"][k][win]).max()/np.abs(so["Q"][k][win]).max())
        e["Q3_raw_maxerr_over_max"] = float(
            np.abs(q3raw[win3] - q3o[win3]).max()/np.abs(q3o[win3]).max())
        e["Q3_raw_rmserr_over_max"] = float(
            np.sqrt(np.mean((q3raw[win3] - q3o[win3])**2))/np.abs(q3o[win3]).max())
        e["Q3_avg_maxerr_over_max"] = float(
            np.abs(q3s[win3] - q3os[win3]).max()/np.abs(q3os[win3]).max())
        ref[key] = e
        ref[key + "_series"] = (so, s3, q3os)
    out["ode"] = {k: v for k, v in ref.items() if not k.endswith("_series")}
    pre = t <= tx
    E_mech = h["K"] + h["W"]
    out["energy_KW_maxrel_before_tx"] = float(np.abs(E_mech[pre] - E_mech[0]).max()
                                              / np.abs(h["W"][0]))
    tx_o = out["ode"]["equivalent"]["t_x"]
    pre1 = t <= tx_o - 1.0
    out["energy_KW_maxrel_before_tx_minus_1"] = float(
        np.abs(E_mech[pre1] - E_mech[0]).max()/np.abs(h["W"][0]))
    P = np.stack([h["P_x"], h["P_y"], h["P_z"]], axis=1)
    out["momentum_max_over_M_vscale"] = float(np.abs(P[pre]).max()
                                              / (M*np.sqrt(M/np.max(R0))))
    out["com_max"] = float(np.abs(np.stack([h["X_x"], h["X_y"], h["X_z"]], 1)[pre]).max())
    out["mg_cycles_mean"] = float(np.mean(h["mg_cycles"]))
    series = dict(t=t, t3=t3, Q=Q, q3s=q3s, Praw=Praw, Ps=Ps, ref=ref, h=h, t0=t0,
                  tx=tx, M=M, case=case, meta=meta, Reff=Reff, Veff=Veff, runs=runs)
    return out, series


def fig_quadrupole(S, out):
    fs.use_style()
    fig, axs = plt.subplots(5, 1, figsize=(fs.COLUMN_WIDTH*1.6, 10.0), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.05, top=0.98, hspace=0.06)
    nmax = max(S)
    for n, s in sorted(S.items()):
        c = COLS.get(n, "k")
        for i in range(3):
            lab = ("N = %d" % n) if i == 0 else None
            axs[0].plot(s["t"], s["Q"][0][:, i], color=c, ls=LS[i], lw=1.0, label=lab)
            axs[1].plot(s["t"], s["Q"][2][:, i], color=c, ls=LS[i], lw=1.0)
            if n == nmax:
                axs[2].plot(s["t3"], s["Q"][3][:, i], color=c, ls=LS[i], lw=0.4,
                            alpha=0.5)
            axs[2].plot(s["t3"], s["q3s"][:, i], color=c, ls=LS[i], lw=1.0)
        axs[3].semilogy(s["t3"], s["Ps"], color=c, lw=1.0, label="N = %d, averaged" % n)
        if n == nmax:
            axs[3].semilogy(s["t3"], s["Praw"], color=c, lw=0.4, alpha=0.5,
                            label="N = %d, raw" % n)
        m = s["t3"] <= s["tx"]
        Ec = np.concatenate([[0.0], np.cumsum(0.5*(s["Ps"][m][1:] + s["Ps"][m][:-1])
                                              * np.diff(s["t3"][m]))])
        axs[4].plot(s["t3"][m], Ec/s["M"], color=c, lw=1.0)
        axs[4].plot([s["tx"]], [Ec[-1]/s["M"]], "o", color=c, ms=3)
    s = S[nmax]
    so, s3, q3os = s["ref"]["equivalent_series"]
    for i in range(3):
        lab = "ODE (model C)" if i == 0 else None
        axs[0].plot(s["t"], so["Q"][0][:, i], color=fs.PAL["blue"], ls=LS[i], lw=1.8,
                    alpha=0.6, label=lab)
        axs[1].plot(s["t"], so["Q"][2][:, i], color=fs.PAL["blue"], ls=LS[i], lw=1.8,
                    alpha=0.6)
        axs[2].plot(s["t3"], q3os[:, i], color=fs.PAL["blue"], ls=LS[i], lw=1.8, alpha=0.6)
    Pos = 0.2*np.sum(s3["Q"][3]**2, axis=1)
    axs[3].semilogy(s["t3"], Pos, color=fs.PAL["blue"], lw=1.8, alpha=0.6, label="ODE")
    r = s["runs"]["equivalent"]
    tx_o = r["crossings"][0][0]
    m = s["t3"] <= tx_o
    Eo = np.concatenate([[0.0], np.cumsum(0.5*(Pos[m][1:] + Pos[m][:-1])
                                          * np.diff(s["t3"][m]))])
    axs[4].plot(s["t3"][m], Eo/s["M"], color=fs.PAL["blue"], lw=1.8, alpha=0.6)
    axs[4].axhline(float(r["segments"][0].y[6, -1])/s["M"], color="k", ls="--", lw=1.0)
    for ax in axs:
        ax.axvline(tx_o, color="grey", lw=1.0, alpha=0.5)
    axs[0].set_ylabel(r"$Q_{ii}$")
    axs[1].set_ylabel(r"$\ddot Q_{ii}$")
    axs[2].set_ylabel(r"$\dddot Q_{ii}$")
    axs[3].set_ylabel(r"$P = \dddot Q_{ij}\dddot Q_{ij}/5$")
    axs[4].set_ylabel(r"$E(t_{\rm turn}\to t)\,/\,M c^2$")
    axs[4].set_xlabel(r"$t / t_k$")
    axs[0].legend(loc="lower left", ncol=2, fontsize=8)
    axs[3].legend(loc="upper left", ncol=2, fontsize=7)
    axs[3].set_ylim(1e-6, 2e-3)
    axs[0].text(0.45, 0.55, "x solid, y dashed, z dotted", transform=axs[0].transAxes,
                ha="left", fontsize=8)
    axs[4].set_xlim(s["t0"], s["t"][-1])
    return fs.save(fig, os.path.join(out, "ell_quadrupole"))


def fig_convergence(rows, dtrow, out):
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    ns = np.array(sorted(rows))
    for key, mk, lab in (("nominal", "s", "nominal ZA state"),
                         ("equivalent", "o", "equivalent ellipsoid of the lattice")):
        dtx = np.array([abs(rows[n]["ode"][key]["dt_x_rel"]) for n in ns])
        dea = np.array([abs(rows[n]["ode"][key]["dE_avg_rel"]) for n in ns])
        der = np.array([abs(rows[n]["ode"][key]["dE_raw_rel"]) for n in ns])
        axs[0].loglog(ns, dtx, mk + "-", color=fs.PAL["red"], label=lab, ms=4)
        axs[1].loglog(ns, dea, mk + "-", color=fs.PAL["red"], ms=4,
                      label="averaged, " + lab)
        axs[1].loglog(ns, der, mk + ":", color=fs.PAL["orange"], ms=4,
                      label="raw, " + lab)
    if dtrow is not None:
        n, r = dtrow
        axs[0].loglog([n], [abs(r["ode"]["equivalent"]["dt_x_rel"])], "x", color="k",
                      label="step 0.01")
        axs[1].loglog([n], [abs(r["ode"]["equivalent"]["dE_avg_rel"])], "x", color="k",
                      label="step 0.01")
    for ax, y0 in ((axs[0], abs(rows[ns[0]]["ode"]["equivalent"]["dt_x_rel"])),
                   (axs[1], abs(rows[ns[0]]["ode"]["equivalent"]["dE_avg_rel"]))):
        nn = np.array([ns[0], ns[-1]], float)
        ax.loglog(nn, y0*(nn/nn[0])**-1, color="k", ls="--", lw=1.0)
        ax.loglog(nn, y0*(nn/nn[0])**-2, color="k", ls=":", lw=1.0)
        ax.set_xlabel("cells per side $N$")
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.minorticks_off()
    axs[0].set_ylabel(r"$|t_x - t_x^{\rm ODE}|\,/\,t_x^{\rm ODE}$")
    axs[1].set_ylabel(r"$|E - E^{\rm ODE}|\,/\,E^{\rm ODE}$")
    axs[0].legend(loc="lower left", fontsize=7)
    axs[1].legend(loc="lower left", fontsize=7)
    axs[0].text(0.97, 0.92, r"dashed $N^{-1}$, dotted $N^{-2}$", transform=axs[0].transAxes,
                ha="right", fontsize=8)
    return fs.save(fig, os.path.join(out, "ell_convergence"))


def fig_snapshots(s, out):
    fs.use_style()
    files = sorted(glob.glob(os.path.join(s["case"], "newton.part.*.bin")))
    if not files:
        return []
    half = min(s["meta"]["half"], 10.0*s["meta"]["half"]/12.0)
    nf = len(files)
    pw = 0.98*fs.FULL_WIDTH/nf
    H = 2*pw + 0.3
    fig = plt.figure(figsize=(fs.FULL_WIDTH, H))
    w = 0.98/nf
    r = s["runs"]["equivalent"]
    for j, f in enumerate(files):
        t, cyc, x, u, m, tag = nw.read_snapshot(f)
        so = el.sample(r, np.array([s["t0"] + t]))
        R = np.abs(so["R"][0])
        for row, (a, b) in enumerate(((0, 2), (0, 1))):
            ax = fig.add_axes([0.01 + j*w, (pw*(1 - row))/H, w, pw/H])
            H2, xe, ye = np.histogram2d(x[:, a], x[:, b], bins=128,
                                        range=[[-half, half], [-half, half]])
            ax.imshow(H2.T + 0.5, origin="lower", extent=[-half, half, -half, half],
                      cmap=fs.truncate_cmap("magma", 0.2, 1.0), norm=LogNorm(),
                      interpolation="none", rasterized=True, aspect="equal")
            ph = np.linspace(0, 2*np.pi, 200)
            ax.plot(R[a]*np.cos(ph), R[b]*np.sin(ph), color="w", lw=0.8, ls="--")
            ax.set_xticks([])
            ax.set_yticks([])
            if row == 0:
                ax.set_title(r"$t = %.2f\,t_k$" % (s["t0"] + t), fontsize=9)
            if j == 0:
                ax.text(0.04, 0.9, "x-z" if row == 0 else "x-y", color="w",
                        transform=ax.transAxes, fontsize=8)
    return fs.save(fig, os.path.join(out, "ell_snapshots"))


def selfsim(n, d, bench):
    rows = {}
    for cdir in sorted(glob.glob(os.path.join(d, "alpha_*"))):
        r, s = case_analysis(n, cdir)
        rows[r["alpha"]] = (r, s)
    if bench is not None:
        rows[bench[0]["alpha"]] = bench
    tab = {}
    for al, (r, s) in sorted(rows.items()):
        tab["%.8g" % al] = {"F_avg": r["E_avg"]/r["mass"]/(2*al)**3.5,
                            "F_raw": r["E_raw"]/r["mass"]/(2*al)**3.5,
                            "tau_x": r["tau_x"],
                            "F_ode": r["ode"]["nominal"]["E"]/r["mass"]/(2*al)**3.5,
                            "case": r["case"]}
    F = np.array([v["F_avg"] for v in tab.values()])
    Fr = np.array([v["F_raw"] for v in tab.values()])
    tau = np.array([v["tau_x"] for v in tab.values()])
    summ = {"rows": tab, "spread_F_avg": float(np.ptp(F)/np.mean(F)),
            "spread_F_raw": float(np.ptp(Fr)/np.mean(Fr)),
            "spread_tau_x": float(np.ptp(tau)/np.mean(tau))}
    return summ, rows


def fig_selfsim(ss, out):
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    for n, (summ, rows) in sorted(ss.items()):
        c = COLS.get(n, "k")
        als = sorted(rows)
        F = [summ["rows"]["%.8g" % a]["F_avg"] for a in als]
        axs[0].semilogx(als, F, "o-", color=c, label="AthenaK Newton, N = %d" % n)
        for a in als:
            r, s = rows[a]
            tt = s["t3"]/s["t0"]
            sc = (2*a)**-2.5
            axs[1].plot(tt, s["q3s"][:, 0]*sc, color=c, lw=1.0)
    Fode = summ["rows"]["%.8g" % als[0]]["F_ode"]
    axs[0].axhline(Fode, **fs.GUIDE, label=r"ODE, $F_C$")
    axs[0].set_xlabel(r"$\alpha$")
    axs[0].set_ylabel(r"$E(t_{\rm turn}\to t_x)\,/\,[M c^2 (2\alpha)^{7/2}]$")
    axs[0].legend(loc="lower right", fontsize=8)
    axs[1].set_xlabel(r"$t / t_{\rm turn}$")
    axs[1].set_ylabel(r"$\dddot Q_{xx}\,(2\alpha)^{-5/2}$, averaged")
    axs[1].text(0.04, 0.9, "all alpha of one N overlap", transform=axs[1].transAxes,
                fontsize=8)
    return fs.save(fig, os.path.join(out, "ell_selfsim"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--dtcheck")
    ap.add_argument("--selfsim", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, S, rows = {}, {}, {}
    for n, case in pairs(a.run):
        r, s = case_analysis(n, case)
        res["N1_N%d" % n] = r
        rows[n], S[n] = r, s
    dtrow = None
    if a.dtcheck:
        n, case = pairs([a.dtcheck])[0]
        r, s = case_analysis(n, case)
        res["N1f_N%d_dt" % n] = r
        if n in rows:
            r["vs_step_0.02"] = {"t_x_rel": (r["t_x"] - rows[n]["t_x"])/rows[n]["t_x"],
                                 "E_avg_rel": (r["E_avg"] - rows[n]["E_avg"])/rows[n]["E_avg"],
                                 "E_raw_rel": (r["E_raw"] - rows[n]["E_raw"])/rows[n]["E_raw"]}
        dtrow = (n, r)
    figs = []
    if S:
        figs += fig_quadrupole(S, a.out)
        figs += fig_convergence(rows, dtrow, a.out)
        figs += fig_snapshots(S[max(S)], a.out)
    ss = {}
    for n, d in pairs(a.selfsim):
        bench = (rows[n], S[n]) if n in rows else None
        summ, srows = selfsim(n, d, bench)
        res["N3_N%d" % n] = summ
        ss[n] = (summ, srows)
    if ss:
        figs += fig_selfsim(ss, a.out)
    res["figures"] = figs
    res["F_C_baseline"] = 0.09464885704755792   # baseline_results.json T6 C
    with open(os.path.join(a.out, "ellipsoid.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
        f.write("\n")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
