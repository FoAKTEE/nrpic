#!/usr/bin/env python3
"""Fresh verifier, part 2b: R^NR of my reader (lattice.py) against my own linear solution.

Linear solution of one realisation (P1:485-496 and the interface text scalar_field_2.md
section 2): R_n(t) = L^(-3/2) W_q(t) R_q(t) alpha_n, with
  - R_q(t): MY integration of the Mukhanov-Sasaki equation in cosmic time (code units,
    G = 1, a(0) = 1), R'' + (3H + d ln eps1/dt) R' + (q/a)^2 R = 0, from the mode file's
    data at t = 0, on MY background (Klein-Gordon + Friedmann from phi0, pi0 of the deck);
  - W_q = (1 + tanh(s ln(sigma a H/q)))/2, s = 5, sigma = 1 (P1:504);
  - alpha_n = (z1 + i z2)/sqrt 2 with the keys of the code, drawn with core's Python twin
    of the counter-based generator (python/nrpic/rng.py; not a reader of any package).
Also: the code's lockstep record (.modes) against my R_q; records (.con.hst) against my
dump statistics; slow-roll parameters at the final time.

Usage: python compare.py --case sr|usr --lat DIR --deck DECK --modes MODEFILE --run RUNDIR
       --out DIR
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import rng  # noqa: E402  (core's twin of utils/rng.hpp)
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

L = 2*np.pi


def deck_value(text, key):
    m = re.search(rf"^\s*{key}\s*=\s*([^\s#]+)", text, re.M)
    return m.group(1) if m else None


def potential(case, deck):
    if case == "sr":
        m = float(deck_value(deck, "mass"))
        return (lambda p: 0.5*m*m*p*p), (lambda p: m*m*p)
    lam = float(deck_value(deck, "lambda"))
    v = float(deck_value(deck, "vev"))
    s2 = np.sqrt(2.0)

    def V(p):
        return lam*v**4*p**2*(3*p**2 + 2*s2*p*v + 6*v**2)/(3*(3*p**2 + 2*v**2)**2)

    def dV(p):
        num = p**2*(3*p**2 + 2*s2*p*v + 6*v**2)
        dnum = 2*p*(3*p**2 + 2*s2*p*v + 6*v**2) + p**2*(6*p + 2*s2*v)
        den = 3*(3*p**2 + 2*v**2)**2
        dden = 3*2*(3*p**2 + 2*v**2)*6*p
        return lam*v**4*(dnum*den - num*dden)/den**2
    return V, dV


def background_and_modes(V, dV, phi0, pi0, q, R0, dR0, t_eval):
    """phi, Pi, ln a and R_q for all shells q at t_eval (cosmic time, code units)."""
    nq = len(q)

    def rhs(t, y):
        phi, Pi, lna = y[0], y[1], y[2]
        H = np.sqrt(8*np.pi/3*(0.5*Pi**2 + V(phi)))
        ddphi = -3*H*Pi - dV(phi)
        eps1 = 4*np.pi*Pi**2/H**2
        fric = 3*H + 2*ddphi/Pi + 2*eps1*H
        a = np.exp(lna)
        R = y[3:3+nq] + 1j*y[3+nq:3+2*nq]
        dR = y[3+2*nq:3+3*nq] + 1j*y[3+3*nq:3+4*nq]
        ddR = -fric*dR - (q/a)**2*R
        return np.concatenate([[Pi, ddphi, H], dR.real, dR.imag, ddR.real, ddR.imag])
    y0 = np.concatenate([[phi0, pi0, 0.0], R0.real, R0.imag, dR0.real, dR0.imag])
    sc = np.concatenate([[1, 1, 1], np.full(4*nq, 1e-12)])
    sol = solve_ivp(rhs, (0, t_eval[-1]), y0, method="DOP853", t_eval=t_eval, rtol=1e-10,
                    atol=sc*1e-3, dense_output=False)
    y = sol.y
    phi, Pi, lna = y[0], y[1], y[2]
    H = np.sqrt(8*np.pi/3*(0.5*Pi**2 + V(phi)))
    R = y[3:3+nq] + 1j*y[3+nq:3+2*nq]
    return dict(phi=phi, Pi=Pi, lna=lna, H=H, R=R, nfev=sol.nfev)


def read_modes_file(path):
    rows = np.loadtxt(path, comments="#")
    return rows[:, 0].astype(np.int64), rows[:, 1] + 1j*rows[:, 2], rows[:, 3] + 1j*rows[:, 4]


def read_lockstep(path):
    """The code's .modes record: header values and R per shell."""
    hdr = {}
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                break
            for k, v in re.findall(r"(\w+) ([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)", line):
                hdr.setdefault(k, float(v))
    rows = np.loadtxt(path, comments="#")
    return hdr, rows[:, 0].astype(np.int64), rows[:, 1] + 1j*rows[:, 2]


def read_record(path):
    return np.loadtxt(path, comments="#")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--lat", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--modes", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    deck = open(a.deck).read()
    V, dV = potential(a.case, deck)
    phi0 = float(deck_value(deck, "phi0"))
    pi0 = float(deck_value(deck, "pi0"))
    seed = int(deck_value(deck, "rng_seed"))
    sharp = float(deck_value(deck, "noise_sharpness"))
    sigma = float(deck_value(deck, "noise_sigma"))
    summ = json.load(open(glob.glob(os.path.join(a.lat, "*_summary.json"))[0]))
    summ = sorted(summ, key=lambda r: r["time"])
    times = np.array([r["time"] for r in summ])
    tag = os.path.basename(glob.glob(os.path.join(a.lat, "*_summary.json"))[0]).split("_")[0]
    npz = [np.load(os.path.join(a.lat, f"{tag}_" + os.path.basename(r["path"]).replace(".dump", "")
                                + ".npz")) for r in summ]
    n = npz[0]["n"]
    n2 = (n**2).sum(1)
    q2_file, R0, dR0 = read_modes_file(a.modes)
    q = np.sqrt(q2_file.astype(float))
    tt = times.copy()
    if tt[0] == 0.0:
        tt[0] = 0.0
    bg = background_and_modes(V, dV, phi0, pi0, q, R0, dR0, tt)
    out = dict(case=a.case, times=times.tolist(), nfev=int(bg["nfev"]))
    # map hemisphere modes to shells
    pos = {int(v): i for i, v in enumerate(q2_file)}
    sidx = np.array([pos[int(v)] for v in n2])
    z = rng.normal2(seed=seed, stream=rng.stochastic_mode_stream(0),
                    entity=rng.mode_entity(n[:, 0], n[:, 1], n[:, 2]), step=0, draw=0)
    alpha = (np.asarray(z[0]) + 1j*np.asarray(z[1]))/np.sqrt(2.0)
    out["alpha_mean_abs2"] = float(np.mean(np.abs(alpha)**2))

    # background against the box means of the dumps
    efold = bg["lna"]
    eps1_mine = 4*np.pi*bg["Pi"]**2/bg["H"]**2
    rows_bg = []
    for i, r in enumerate(summ):
        rows_bg.append(dict(t=r["time"], N_mine=float(efold[i]),
                            N_dump=r["efolds_from_mean_chi"],
                            phi_rel=float(r["mean_phi"]/bg["phi"][i] - 1),
                            Pi_rel=float(r["mean_Pi"]/bg["Pi"][i] - 1),
                            H_rel=float(r["H"]/bg["H"][i] - 1),
                            eps1_dump=float(4*np.pi*r["mean_Pi"]**2/r["H"]**2),
                            eps1_mine=float(eps1_mine[i])))
    out["background"] = rows_bg
    # eps2 (P1 convention -dln eps1/dN) at the final time from my background
    tf = times[-1]
    hh = 1e-3
    bb = background_and_modes(V, dV, phi0, pi0, q[:1], R0[:1], dR0[:1],
                              np.array([tf - hh, tf, tf + hh]))
    e1 = 4*np.pi*bb["Pi"]**2/bb["H"]**2
    dN = (bb["lna"][2] - bb["lna"][0])
    out["final_eps1_mine"] = float(e1[1])
    out["final_eps2_P1conv_mine"] = float(-(np.log(e1[2]) - np.log(e1[0]))/dN)
    out["final_N_mine"] = float(bb["lna"][1])

    # per mode and per shell against the linear solution of the realisation
    per_dump = []
    lock_dev = []
    for i, r in enumerate(summ):
        a_ = np.exp(efold[i])
        ks = sigma*a_*bg["H"][i]
        x = sharp*np.log(ks/np.sqrt(n2))
        W = 0.5*(1 + np.tanh(x))
        lin = L**-1.5*W*bg["R"][sidx, i]*alpha
        lin = np.where(np.abs(lin) > 0, lin, np.nan)
        cR = npz[i]["c_R"]
        cRnoE = npz[i]["c_RnoE"]
        cAlt = -npz[i]["c_Phichi"] - npz[i]["c_PhiE"] + (r["H"]/r["Pi_b"])*npz[i]["c_dphi"]
        rel = np.abs(cR - lin)/np.abs(lin)
        relnoE = np.abs(cRnoE - lin)/np.abs(lin)
        relAlt = np.abs(cAlt - lin)/np.abs(lin)
        mag = np.sqrt(n2)
        entered = W > 0.999
        d = dict(t=r["time"], N=float(efold[i]), n_entered=int(entered.sum()))
        for lab, sel in (("le2", mag <= 2), ("le8", mag <= 8), ("le32", mag <= 32),
                         ("all", mag > 0)):
            s = sel & entered
            if s.any():
                d[f"median_rel_{lab}"] = float(np.median(rel[s]))
                d[f"max_rel_{lab}"] = float(rel[s].max())
                d[f"median_rel_noE_{lab}"] = float(np.median(relnoE[s]))
                d[f"median_rel_wrongsign_{lab}"] = float(np.median(relAlt[s]))
        # shell power: NR (both hemispheres from the full transform) and linear (same alphas)
        ssum, scnt = npz[i]["shell_sum_R"], npz[i]["shell_cnt"]
        uq = np.unique(n2)
        pnr = ssum[uq]/scnt[uq]
        plin = np.array([np.mean(np.abs(lin[n2 == v])**2) for v in uq])
        pms = np.array([L**-3*np.mean((W[n2 == v]**2))*np.abs(bg["R"][pos[int(v)], i])**2
                        for v in uq])
        mcount = np.array([(n2 == v).sum() for v in uq])
        full_entered = np.array([W[n2 == v].min() > 0.999 for v in uq])
        if full_entered.any():
            rr = pnr[full_entered]/plin[full_entered] - 1
            d["shell_max_abs_NR_over_lin_m1"] = float(np.abs(rr).max())
            half = np.sqrt(uq[full_entered]) <= 32
            d["shell_max_abs_NR_over_lin_m1_kle32"] = float(np.abs(rr[half]).max())
            z_ms = (pnr[full_entered]/pms[full_entered] - 1)*np.sqrt(mcount[full_entered])
            d["frac_within_3_over_sqrtM_of_MS"] = float(np.mean(np.abs(z_ms) <= 3))
            for lab, cmin in (("cnt_gt10_both", 2*mcount > 10), ("cnt_gt10_hemi", mcount > 10)):
                s10 = cmin[full_entered]
                d[f"shell_max_abs_NR_over_lin_m1_{lab}"] = float(np.abs(rr[s10]).max())
                d[f"shell_max_abs_NR_over_lin_m1_kle32_{lab}"] = float(np.abs(rr[s10 & half]).max())
            d["n_shells"] = int(full_entered.sum())
        # power beyond the injected band, relative to the MS power at the top shell
        top = uq.max()
        beyond = np.arange(len(ssum)) > top
        beyond &= scnt > 0
        if beyond.any():
            d["power_beyond_kmax_over_top_MS"] = float((ssum[beyond]/scnt[beyond]).max()
                                                       / pms[-1]) if pms[-1] > 0 else None
        d["R_rms"] = r["R_rms"]
        d["R_maxabs"] = r["R_maxabs"]
        for k in ("mean_absH", "mean_absH_over_Hmag_mine", "max_absH_over_Hmag_mine",
                  "p99_absH_over_Hmag_mine", "mean_absH_boxmean_removed_over_Hmag_mine",
                  "mean_Hmag_mine", "mean_Hmag_dumped", "max_rel_diff_Hmag",
                  "mean_absH_over_Hmag_dumped", "mean_absM_over_Mmag_dumped", "mean_absM"):
            if k in r:
                d[k] = r[k]
        per_dump.append(d)
        # code's lockstep record at this dump against my R_q
        mf = os.path.join(os.path.dirname(r["path"]), os.path.basename(r["path"]).replace(
            ".dump", ".modes"))
        if os.path.exists(mf):
            hdr, lq2, lR = read_lockstep(mf)
            ii = np.array([pos[int(v)] for v in lq2])
            dev = np.abs(lR - bg["R"][ii, i])/np.abs(bg["R"][ii, i])
            lock_dev.append(dict(t=r["time"], median=float(np.median(dev)), max=float(dev.max()),
                                 max_le8=float(dev[np.sqrt(lq2) <= 8].max()),
                                 H_rel=float(hdr.get("H", np.nan)/bg["H"][i] - 1),
                                 eps1_rel=float(hdr.get("eps1", np.nan)/eps1_mine[i] - 1)))
        if i == len(summ) - 1:
            final = dict(uq=uq, pnr=pnr, plin=plin, pms=pms, mcount=mcount, rel=rel, mag=mag,
                         W=W)
    out["per_dump"] = per_dump
    out["lockstep_vs_mine"] = lock_dev

    # freezing: shell power of R^NR at each dump over that at the final dump
    fr = []
    for i, r in enumerate(summ):
        ssum, scnt = npz[i]["shell_sum_R"], npz[i]["shell_cnt"]
        p = ssum[final["uq"]]/scnt[final["uq"]]
        fr.append(p/final["pnr"])
    fr = np.array(fr)
    out["freeze"] = []
    for lab, sel in (("q<=4", np.sqrt(final["uq"]) <= 4), ("8<q<=16", (np.sqrt(final["uq"]) > 8)
                     & (np.sqrt(final["uq"]) <= 16)), ("32<q<=64", np.sqrt(final["uq"]) > 32)):
        out["freeze"].append(dict(band=lab, ratio_to_final=[float(np.median(fr[i][sel]))
                                                           for i in range(len(summ))]))

    # records
    rec = glob.glob(os.path.join(os.path.dirname(summ[0]["path"]), "*.sf.con.hst"))
    if rec:
        R = read_record(rec[0])
        out["record_file"] = rec[0]
        # compare at dump times: <|H|> column 12 and record <[H]> column 10
        cmp = []
        for d, r in zip(per_dump, summ):
            j = int(np.argmin(np.abs(R[:, 0] - r["time"])))
            row = dict(t=r["time"], t_rec=float(R[j, 0]), absH_rec=float(R[j, 11]),
                       absH_dump=r.get("mean_absH"), Hmag_rec=float(R[j, 9]),
                       Hmag_mine=r.get("mean_Hmag_mine"),
                       ratio_rec=float(R[j, 3]), ratio_mine=r.get("mean_absH_over_Hmag_mine"),
                       Mratio_rec=float(R[j, 6]), Mratio_dump=r.get("mean_absM_over_Mmag_dumped"))
            cmp.append(row)
        out["record_vs_dump"] = cmp
        out["record_max_mean_absH_over_Hmag"] = float(R[:, 3].max())
        out["record_N_of_max_H"] = float(R[np.argmax(R[:, 3]), 2])
        out["record_max_mean_absM_over_Mmag"] = float(R[:, 6].max())
        out["record_final"] = dict(N=float(R[-1, 2]), H=float(R[-1, 3]), M=float(R[-1, 6]))
        if R.shape[1] >= 26:
            out["record_max_mean_absH_boxmean_removed"] = float(R[:, 24].max())
            out["record_N_of_max_H_boxmean_removed"] = float(R[np.argmax(R[:, 24]), 2])
        # entry maximum: largest <|H|/[H]> before the last mode has entered (N < ln kmax + 1)
        ent = R[:, 2] < np.log(64.0) + 1.0
        out["record_entry_max_mean_absH_over_Hmag"] = float(R[ent, 3].max())
        out["record_entry_max_mean_absM_over_Mmag"] = float(R[ent, 6].max())
        # slow roll from the record at the end: eps1 = 4 pi Pi^2/H^2, H = -K/3
        Hr = -R[:, 18]/3
        e1r = 4*np.pi*R[:, 17]**2/Hr**2
        Nr = R[:, 2]
        m = Nr > Nr[-1] - 0.3
        sl = np.polyfit(Nr[m], np.log(e1r[m]), 1)[0]
        out["record_final_eps1"] = float(e1r[-1])
        out["record_final_eps2_P1conv"] = float(-sl)
        rec_arr = R
    else:
        rec_arr = None

    with open(os.path.join(a.out, f"compare_{a.case}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)

    # ---------------- figures
    figstyle.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    uq = final["uq"]
    k = np.sqrt(uq)
    pref = k**3/(2*np.pi**2)*L**3
    ax = axs[0]
    cols = figstyle.series_colors(len(summ)) if hasattr(figstyle, "series_colors") else None
    for i in range(0, len(summ), max(1, len(summ)//6)):
        ssum, scnt = npz[i]["shell_sum_R"], npz[i]["shell_cnt"]
        ax.loglog(k, pref*ssum[uq]/scnt[uq], color=cols[i] if cols is not None else None, lw=1)
    ax.loglog(k, pref*final["pms"], "k--", lw=1, label="my MS, final")
    ax.set_xlabel(r"$k/dk$")
    ax.set_ylabel(r"$\Delta[\mathcal{R}^{\rm NR}]$")
    ax.legend(fontsize=7)
    ax = axs[1]
    ax.semilogy(final["mag"], np.maximum(final["rel"], 1e-12), ",", color=figstyle.SERIES[0],
                alpha=0.4)
    ax.semilogy(k, np.abs(final["pnr"]/final["plin"] - 1), ".", ms=2, color=figstyle.SERIES[1],
                label="shell power / linear - 1")
    ax.set_xlabel(r"$|n|$")
    ax.set_ylabel("deviation at the last dump")
    ax.legend(fontsize=7)
    ax = axs[2]
    if rec_arr is not None:
        ax.semilogy(rec_arr[:, 2], rec_arr[:, 3], color=figstyle.SERIES[0],
                    label=r"record $\langle|H|/[H]\rangle$")
        ax.semilogy(rec_arr[:, 2], rec_arr[:, 6], color=figstyle.SERIES[1],
                    label=r"record $\langle|M|/[M]\rangle$")
    Nd = [d["N"] for d in per_dump]
    hm = [d.get("mean_absH_over_Hmag_mine", np.nan) for d in per_dump]
    ax.semilogy(Nd, hm, "ko", ms=3, mfc="none", label=r"my dumps $\langle|H|/[H]\rangle$")
    mm = [d.get("mean_absM_over_Mmag_dumped", np.nan) for d in per_dump]
    if np.isfinite(mm).any():
        ax.semilogy(Nd, mm, "ks", ms=3, mfc="none", label=r"my dumps $\langle|M|/[M]\rangle$")
    ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, f"fig_lattice_{a.case}.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH, 2.8))
    for fz, c in zip(out["freeze"], figstyle.SERIES):
        ax.plot(efold, fz["ratio_to_final"], "o-", ms=3, color=c, label=fz["band"])
    ax.set_yscale("log")
    ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
    ax.set_ylabel("shell power / final (median)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, f"fig_freeze_{a.case}.png"), dpi=150)
    plt.close(fig)
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_dump", "background",
                                                                 "record_vs_dump",
                                                                 "lockstep_vs_mine", "freeze")},
                     indent=1, default=float))


if __name__ == "__main__":
    main()
