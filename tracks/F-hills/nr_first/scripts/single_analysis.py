#!/usr/bin/env python3
"""E3 of nr_first/JOURNAL.md: single Bowen-York puncture runs S1-S3 (m = 1, P = 0.25 along
+x, closed-form correction, start at the origin, spheres at 30, 40, 50 m).

Per run (directories named S1, S2, S3, and any other names given):
  tracker   x(t), coordinate speed v_x (the tracker's v = -beta), speed ratio
            f = v_x / (P / M_ADM) and lag x_boost(t) - x(t), x_boost = (P / M_ADM) t
  horizon   mass, spin, relative drift
  history   <H^2>^(1/2), <M^2>^(1/2)
  junk      radiated energy through each sphere from r psi4 (nrread.radiated_energy): raw,
            and with the slowly varying part removed outside the window [R - 8, R + 32]
Reference values (python/nrpic/bowen_york.py, recomputed here): ADM mass of the data with the
second-order correction m + (5/8) P^2/m and of the full solution; P/M_ADM; sqrt(M_ADM^2 - P^2).
Writes <out>/single_analysis.json and fig_single_{junk,gauge}.{png,pdf}.
Usage: single_analysis.py <out> [--P=<momentum>] <run dir> [<run dir> ...]
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
from nrpic import bowen_york as by  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

P, MBARE = 0.25, 1.0        # momentum of the package's input; --P=<value> for another run
RADII = (30, 40, 50)        # default; a run with other spheres uses those it has
COL = {"S1": fs.PAL["blue"], "S2": fs.PAL["red"], "S3": fs.PAL["yellow"],
       "S2g": fs.PAL["green"]}
DESC = {"S1": r"S1: $h=m/16$, $\eta m=2$", "S2": r"S2: $h=m/8$, $\eta m=0.25$",
        "S3": r"S3: $h=m/8$, $\eta m=2$", "S2g": r"S2g: $h=m/8$, mass-scaled $\eta$"}


def window_mean(t, y, t0, t1):
    s = (t >= t0) & (t < t1)
    return float(np.mean(y[s])) if np.any(s) else math.nan


def main():
    global P
    out = sys.argv[1]
    runs = [a for a in sys.argv[2:] if not a.startswith("--P=")]
    for a in sys.argv[2:]:
        if a.startswith("--P="):
            P = float(a[4:])
    os.makedirs(out, exist_ok=True)
    m_adm2 = by.adm_mass_approx(MBARE, P)
    m_full = by.solve_axisym(MBARE, P=P)["m_adm"]
    ref = dict(M_ADM_second_order=m_adm2, M_ADM_full=m_full, v_boost=P / m_adm2,
               M_rest_second_order=math.sqrt(m_adm2 ** 2 - P ** 2),
               M_rest_full=math.sqrt(m_full ** 2 - P ** 2))
    vb = ref["v_boost"]
    res = {"reference": ref}
    data = {}
    for rd in runs:
        name = os.path.basename(os.path.normpath(rd))
        trk = nr.read_trackers(rd)[0]
        hz, nmiss = nr.read_horizons(rd)[0]
        hst = nr.read_hst([os.path.join(rd, f) for f in os.listdir(rd)
                           if f.endswith(".z4c.user.hst")][0])
        t, x, v = trk["t"], trk["x"][:, 0], trk["v"][:, 0]
        f = v / vb
        lag = vb * t - (x - x[0])
        e = dict(t_end=float(t[-1]), cycles=int(trk["iter"][-1]), rows=int(len(t)),
                 f_mean={f"{a}-{b}": window_mean(t, f, a, b) for a, b in
                         ((0, 5), (5, 10), (10, 20), (20, 30), (30, 40), (40, 60), (60, 90))},
                 f_max=float(f.max()), t_f_max=float(t[np.argmax(f)]),
                 lag_at={str(tt): float(np.interp(tt, t, lag)) for tt in (10, 20, 40, 60, 89)},
                 x_end=float(x[-1]), yz_max=float(np.max(np.abs(trk["x"][:, 1:]))))
        mh = hz["mass"]
        e["horizon"] = dict(found=int(len(mh)), missed=nmiss, m_first=float(mh[0]),
                            t_first=float(hz["t"][0]),
                            m_at={str(tt): float(np.interp(tt, hz["t"], mh)) for tt in
                                  (2, 5, 10, 20, 40, 60, 80, 89)},
                            m_end=float(mh[-1]), S_max=float(np.max(np.abs(hz["S"]))),
                            drift_5_to_end=float(mh[-1] / np.interp(5.0, hz["t"], mh) - 1))
        th = hst["time"]
        e["constraints"] = dict(H_t0=float(np.sqrt(hst["H2"][0])),
                                H_max=float(np.sqrt(hst["H2"].max())),
                                t_H_max=float(th[np.argmax(hst["H2"])]),
                                H_at={str(tt): float(np.sqrt(np.interp(tt, th, hst["H2"])))
                                      for tt in (10, 20, 40, 60, 89)},
                                M_t0=float(np.sqrt(hst["M2"][0])))
        e["junk"] = {}
        wav = {}
        have = sorted(int(f[-8:-4]) for f in os.listdir(os.path.join(rd, "waveforms"))
                      if f.startswith("rpsi4_real_"))
        for R in (RADII if all(r in have for r in RADII) else have):
            try:
                tw, modes = nr.read_rpsi4(rd, R)
            except (OSError, ValueError) as err:
                print(name, "no waveform at", R, err)
                continue
            E_raw, _, _ = nr.radiated_energy(tw, modes)
            win = (R - 8.0, R + 32.0)
            E_hp, rate, zz = nr.radiated_energy(tw, modes, highpass_window=win)
            e["junk"][str(R)] = dict(E_raw_end=float(E_raw[-1]), E_hp_end=float(E_hp[-1]),
                                     E_hp_window=float(np.interp(win[1], tw, E_hp)),
                                     t_end=float(tw[-1]), complete=bool(tw[-1] >= win[1]),
                                     peak_20=float(np.max(np.abs(zz[(2, 0)]))),
                                     t_peak_20=float(tw[np.argmax(np.abs(zz[(2, 0)]))]))
            wav[R] = (tw, modes[(2, 0)], zz[(2, 0)], E_raw, E_hp)
        res[name] = e
        data[name] = dict(t=t, f=f, lag=lag, x=x, th=hz["t"], mh=mh, hst=hst, wav=wav)
        print(name, json.dumps(e, indent=1), flush=True)
    json.dump(res, open(os.path.join(out, "single_analysis.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    # junk
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    for name, dd in data.items():
        if 40 in dd["wav"]:
            tw, z20, zh20, Er, Eh = dd["wav"][40]
            ax[0].plot(tw, z20.real, color=COL.get(name, "k"), lw=1.1, label=DESC.get(name, name))
        for R, ls in zip(RADII, (":", "--", "-")):
            if R in dd["wav"]:
                tw, z20, zh20, Er, Eh = dd["wav"][R]
                ax[1].plot(tw - R, np.maximum(Eh, 1e-12), color=COL.get(name, "k"), ls=ls, lw=1.1)
    ax[0].axvspan(40 - 8, 40 + 32, color="grey", alpha=0.12, lw=0)
    ax[0].set_xlabel(r"$t\,[m]$")
    ax[0].set_ylabel(r"Re $r\psi_4^{20}$ at $R=40\,m$")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_yscale("log")
    ax[1].set_ylim(1e-8, 1e-3)
    ax[1].set_xlabel(r"$t - R\,[m]$")
    ax[1].set_ylabel(r"$E_{\rm rad}/m$ (R = 30 dotted, 40 dashed, 50 solid)")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_single_junk")):
        print("figure:", pth)
    # gauge, horizon, constraints
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    for name, dd in data.items():
        c = COL.get(name, "k")
        ax[0, 0].plot(dd["t"], dd["f"], color=c, lw=1.1, label=DESC.get(name, name))
        ax[0, 1].plot(dd["t"], dd["lag"], color=c, lw=1.1)
        ax[1, 0].plot(dd["th"], dd["mh"] / ref["M_rest_full"] - 1, color=c, lw=1.1)
        ax[1, 1].semilogy(dd["hst"]["time"], np.sqrt(dd["hst"]["H2"]), color=c, lw=1.1)
        ax[1, 1].semilogy(dd["hst"]["time"], np.sqrt(dd["hst"]["M2"]), color=c, lw=0.8, ls="--")
    for (a, b), val in zip(((10, 20), (20, 30), (30, 40)), (0.48, 0.55, 0.61)):
        ax[0, 0].plot([a, b], [val, val], **fs.REF_LINE)
    ax[0, 0].axhline(1.0, **fs.MASK_LINE)
    ax[0, 0].set_ylabel(r"$f = v_{\rm tracker}/(P/M_{\rm ADM})$")
    ax[0, 0].legend(frameon=False, fontsize=7, loc="lower right")
    ax[0, 0].set_title("black bars: core's test 1b ($P=0.3$, $\\eta m=2$, $h=m/16$)", fontsize=8)
    ax[0, 1].set_ylabel(r"lag $(P/M_{\rm ADM})\,t - \Delta x$ $[m]$")
    ax[1, 0].set_ylabel(r"$M_{\rm AH}/\sqrt{M_{\rm ADM}^2-P^2} - 1$ (full solution)")
    ax[1, 1].set_ylabel(r"$\langle H^2\rangle^{1/2}$ (solid), $\langle M^2\rangle^{1/2}$ (dashed)")
    for a in ax.ravel():
        a.set_xlabel(r"$t\,[m]$")
        a.set_xlim(0, 90)
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_single_gauge")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
