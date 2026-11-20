#!/usr/bin/env python3
"""C1: exact events of data set 3 from the format-2 table alone (my LTB, ltb.py).

Writes c1_exact.json and fig_c1_exact.{png,pdf} into $NRPIC_RUN_DIR.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
from ltb import TableLTB, Shells, shells_from_table   # noqa: E402


def main():
    out = P.outdir()
    T = TableLTB(P.TABLE)
    b1, b2 = np.sort(T.breaks)
    res = dict(table=P.TABLE, breaks=[b1, b2], header={k: T.hdr[k] for k in ("H", "Rb", "M", "t_i")})

    # ---------------------------------------------------------------- slice checks
    rows = T.r[1:]
    s = T.slice(rows)
    res["psi_centre"] = float(1.0 + T.d[0, 1])
    # (a) total mass from the last row (psi = 1, vacuum): m = R v^2 / 2
    sN = T.slice(np.array([T.r_last]))
    res["M_last_row"] = float(sN["m"][0])
    res["M_last_row_RKT"] = float(T.r_last ** 3 * T.d[-1, 3] ** 2 / 2.0)
    # (b) momentum constraint: KL = -dv/dR, from the spline of KT
    rr = np.concatenate([np.linspace(1e-3, b1 - 1e-4, 2000), np.linspace(b1 + 1e-4, b2 - 1e-4, 2000),
                         np.linspace(b2 + 1e-4, T.r_last - 1e-3, 2000)])
    ss = T.slice(rr)
    dv = np.empty_like(rr)
    for q in range(3):
        sel = T.piece_of(rr) == q
        dv[sel] = np.gradient(ss["v"][sel], ss["R"][sel])
    mom = (ss["KL"] + dv)
    inner = np.ones_like(rr, bool)
    for q in range(3):
        idx = np.nonzero(T.piece_of(rr) == q)[0]
        inner[idx[:2]] = False
        inner[idx[-2:]] = False
    res["momentum_KL_plus_dvdR_max"] = float(np.max(np.abs(mom[inner])))
    res["KL_scale"] = float(np.max(np.abs(ss["KL"])))
    # (c) Hamiltonian: m from the metric against int 4 pi R^2 rho dR (rho from H)
    m_int = np.zeros_like(rr)
    for q in range(3):
        idx = np.nonzero(T.piece_of(rr) == q)[0]
        f = 4 * np.pi * ss["R"][idx] ** 2 * ss["rho_H"][idx] * np.gradient(ss["R"][idx], rr[idx])
        m_int[idx] = np.concatenate([[0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(rr[idx]))])
    # offset per piece from the metric mass at the first point of the piece
    for q in range(3):
        idx = np.nonzero(T.piece_of(rr) == q)[0]
        m_int[idx] += ss["m"][idx[0]]
    res["m_metric_minus_m_rho_max"] = float(np.max(np.abs(ss["m"] - m_int)))
    # (d) rest mass and largest 2m/R
    res["rest_mass_table"] = float(T.rest_mass(rmax=T.r_last))
    two_m_R = 2 * ss["m"] / ss["R"]
    k = int(np.argmax(two_m_R))
    res["max_2m_over_R"] = float(two_m_R[k])
    res["R_at_max_2m_over_R"] = float(ss["R"][k])
    edge_in = T.slice(np.array([b1]), side="in")
    edge_out = T.slice(np.array([b1]), side="out")
    res["core_edge"] = dict(rbar=float(b1), R=float(edge_in["R"][0]), m_in=float(edge_in["m"][0]),
                            m_out=float(edge_out["m"][0]), E_in=float(edge_in["E"][0]), E_out=float(edge_out["E"][0]),
                            v_in=float(edge_in["v"][0]), v_out=float(edge_out["v"][0]),
                            rho_in=float(edge_in["rho_H"][0]), rho_out=float(edge_out["rho_H"][0]))
    s2 = T.slice(np.array([b2]), side="in")
    res["R2"] = dict(rbar=float(b2), R=float(s2["R"][0]), m=float(s2["m"][0]), E=float(s2["E"][0]))
    # matter edge: where rho_H drops to ~0
    rm_grid = np.linspace(b2 + 1e-4, T.r_last, 20000)
    sm = T.slice(rm_grid)
    nz = np.nonzero(sm["rho_H"] > 1e-10 * float(edge_in["rho_H"][0]))[0]
    res["matter_edge_rbar"] = float(rm_grid[nz[-1]]) if len(nz) else None
    res["rho_vacuum_max"] = float(np.max(np.abs(sm["rho_H"][rm_grid > 4.26])))

    # ---------------------------------------------------------------- shells
    core_r = np.linspace(1e-3, b1, 801)
    core_r[-1] = b1
    sh_core = shells_from_table(T, core_r, side="in")
    shell_r = np.concatenate([[b1], b1 + np.geomspace(1e-7, b2 - b1 - 1e-7, 3000)])
    sh_sh = shells_from_table(T, shell_r, side="out")
    env_r = np.linspace(b2, 4.249, 400)
    sh_env = shells_from_table(T, env_r, side="out")
    res["bang_time"] = dict(core_age_min=float(np.nanmin(sh_core.age)), core_age_max=float(np.nanmax(sh_core.age)),
                            shell_age_min=float(np.nanmin(sh_sh.age[sh_sh.bound])),
                            shell_age_max=float(np.nanmax(sh_sh.age[sh_sh.bound])),
                            t_i_header=float(T.hdr["t_i"]))
    # core events (homogeneous core: the same for all core shells)
    res["core"] = dict(tau_ta_min=float(np.min(sh_core.tau_ta)), tau_ta_max=float(np.max(sh_core.tau_ta)),
                       Rmax_over_Ri_min=float(np.min(sh_core.R_max / sh_core.R_i)),
                       Rmax_over_Ri_max=float(np.max(sh_core.R_max / sh_core.R_i)),
                       tau_c_min=float(np.min(sh_core.tau_c)), tau_c_max=float(np.max(sh_core.tau_c)),
                       E_over_R2_spread=float(np.ptp(sh_core.E[10:] / sh_core.R_i[10:] ** 2)))
    # first trapped sphere: minimum of tau_AH over all shells
    all_tau = np.concatenate([sh_core.tau_ah, sh_sh.tau_ah, sh_env.tau_ah])
    all_R = np.concatenate([sh_core.R_i, sh_sh.R_i, sh_env.R_i])
    all_m = np.concatenate([sh_core.m, sh_sh.m, sh_env.m])
    all_rb = np.concatenate([core_r, shell_r, env_r])
    j = int(np.argmin(all_tau))
    res["first_trapped"] = dict(tau_AH=float(all_tau[j]), R_i=float(all_R[j]), rbar_i=float(all_rb[j]),
                                m=float(all_m[j]), R_AH=float(2 * all_m[j]),
                                where="core (inner side of break 1)" if j < len(core_r) else "outside the core")
    res["core_edge_tau_AH_inner"] = float(sh_core.tau_ah[-1])
    res["core_edge_tau_AH_outer"] = float(sh_sh.tau_ah[0])
    # shell 0.02 M (areal) outside the edge
    Rl = res["core_edge"]["R"] + 0.02
    rb02 = brentq(lambda x: T.slice(np.array([x]))["R"][0] - Rl, b1 + 1e-9, b2 - 1e-9)
    res["tau_AH_edge_plus_0p02"] = float(shells_from_table(T, np.array([rb02])).tau_ah[0])
    # monotonic tau_AH outside the edge?
    d_tau = np.diff(sh_sh.tau_ah)
    res["tau_AH_monotonic_in_shell"] = bool(np.all(d_tau > 0))

    # m_AH(tau): outermost shell with tau_AH <= tau (constant-tau slices of the dust)
    tau0 = res["first_trapped"]["tau_AH"]

    def m_ah(tau):
        if tau < tau0:
            return np.nan, np.nan
        ok = np.nonzero(sh_sh.tau_ah <= tau)[0]
        if len(ok) == 0:
            return float(sh_core.m[-1]), float(b1)
        q = ok.max()
        if q + 1 >= len(shell_r):
            return float(sh_sh.m[q]), float(shell_r[q])
        x = brentq(lambda r_: shells_from_table(T, np.array([r_]), side="out").tau_ah[0] - tau,
                   shell_r[q], shell_r[q + 1], xtol=1e-14)
        sx = shells_from_table(T, np.array([x]), side="out")
        return float(sx.m[0]), float(x)

    res["m_AH"] = {f"tau_AH+{d}": dict(zip(("m", "rbar_i"), m_ah(tau0 + d))) for d in (0.0, 1.0, 2.0, 4.0, 8.0)}
    taus = np.linspace(tau0, tau0 + 12, 241)
    mah = np.array([m_ah(t)[0] for t in taus])
    res["m_AH_curve"] = dict(tau=taus.tolist(), m=mah.tolist())

    # shell crossing before the crunch: R(tau, R_i) increasing in R_i
    gr = np.concatenate([np.linspace(1e-3, b1, 300)[:-1], [b1], b1 + np.linspace(1e-6, b2 - b1, 1500)[1:],
                         np.linspace(b2, 4.249, 300)[1:]])
    sides = np.array(["in"] * 300 + ["out"] * (len(gr) - 300))
    shg = Shells(*[np.concatenate([shells_from_table(T, gr[sides == "in"], side="in").__dict__[k],
                                   shells_from_table(T, gr[sides == "out"], side="out").__dict__[k]])
                   for k in ("R_i", "m", "E")])
    tc = res["core"]["tau_c_min"]
    tg = np.linspace(0.0, 0.999 * tc, 600)
    Rg = shg.R(tg)
    dR = np.diff(Rg, axis=0)
    res["shell_crossing"] = dict(n_shells=int(len(gr)), n_times=int(len(tg)), tau_max=float(tg[-1]),
                                 min_dR_between_neighbours=float(dR.min()),
                                 crossing=bool(np.any(dR <= 0)))
    # also up to the crunch of the shell at R2 for the shells outside the core (they keep falling in)
    with open(os.path.join(out, "c1_exact.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    # ---------------------------------------------------------------- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, wspace=0.32, hspace=0.42)
    ax = fig.add_subplot(2, 2, 1)
    ax.plot(ss["R"], two_m_R, color=fs.PAL["red"], label=r"$2m/R$ (table)")
    ax.plot(ss["R"], 1 + 2 * ss["E"], color=fs.PAL["blue"], label=r"$1+2E=|DR|^2$")
    ax.plot(ss["R"], ss["rho_H"] / ss["rho_H"][0], color=fs.PAL["green"], label=r"$\rho/\rho_c$ (Hamiltonian)")
    for b in (b1, b2):
        ax.axvline(T.slice(np.array([b]), side="in")["R"][0], **fs.MASK_LINE)
    ax.set_xlabel(r"$R\,/M$ on the initial slice")
    ax.set_ylim(0, 1.25)
    ax.legend(fontsize=7, loc="upper right", frameon=False)
    ax.set_title("initial slice from the table", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    ax.plot(sh_core.R_i, sh_core.tau_ta, color=fs.PAL["blue"], label=r"$\tau_{\rm ta}$")
    ax.plot(sh_core.R_i, sh_core.tau_ah, color=fs.PAL["red"], label=r"$\tau_{\rm AH}$")
    ax.plot(sh_core.R_i, sh_core.tau_c, color="k", lw=1.0, label=r"$\tau_c$")
    ok = sh_sh.bound
    ax.plot(sh_sh.R_i[ok], sh_sh.tau_ta[ok], color=fs.PAL["blue"])
    ax.plot(sh_sh.R_i[ok], sh_sh.tau_ah[ok], color=fs.PAL["red"])
    ax.plot(sh_sh.R_i[ok], sh_sh.tau_c[ok], color="k", lw=1.0)
    ax.axhline(tau0, **fs.GUIDE)
    ax.set_ylim(0, 30)
    ax.set_xlabel(r"shell label $R_i\,/M$")
    ax.set_ylabel(r"proper time $\tau\,/M$")
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.set_title(f"events per shell; first trap {tau0:.5f}", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    ax.plot(taus - tau0, mah, color=fs.PAL["red"], label="this verifier")
    claimed = {2: 0.69610, 4: 0.70437, 8: 0.71804, 0: 0.686563}
    ax.plot(list(claimed), list(claimed.values()), "o", color=fs.PAL["blue"], ms=4, label="claimed (C1)")
    ax.set_xlabel(r"$\tau-\tau_{\rm AH}\,/M$")
    ax.set_ylabel(r"$m_{\rm AH}\,/M$ (constant-$\tau$ slices)")
    ax.legend(fontsize=8, frameon=False)
    ax.set_title("horizon mass of the exact solution", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    picks = [0.5, 1.5, b1, b1 + 0.05, b1 + 0.2, 0.5 * (b1 + b2), b2, 4.0]
    cols = fs.series_colors(len(picks), "viridis")
    tp = np.linspace(0, 20, 800)
    for c, rb in zip(cols, picks):
        side = "in" if rb == b1 else None
        sx = shells_from_table(T, np.array([rb]), side=side)
        Rt = sx.R(tp)[0]
        ok = Rt > 0
        ax.plot(tp[ok], Rt[ok], color=c, lw=1.2, label=rf"$R_i$={sx.R_i[0]:.2f}")
        ax.plot(tp, np.full_like(tp, 2 * sx.m[0]), color=c, lw=0.6, ls=":")
    ax.axvline(tau0, **fs.MASK_LINE)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$R\,/M$ (dotted: $2m$)")
    ax.set_ylim(0, 9)
    ax.legend(fontsize=6, ncol=2, frameon=False, loc="upper left")
    ax.set_title("world lines (cycloids from the table)", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c1_exact"))
    print(json.dumps({k: v for k, v in res.items() if k != "m_AH_curve"}, indent=1))


if __name__ == "__main__":
    main()
