#!/usr/bin/env python3
"""Test 1b of tracks/core/JOURNAL-mp.md: one moving puncture evolved. Reads the
registered runs b16_* (and the stopped 1/32 reference b_ref_v0.2844), prints the
tracker speeds, horizon masses, constraint norms and the energy of the initial burst
of radiation, writes boost_check.json and the figures figs/boost_evolution and
figs/boost_waves.

Energy through an extraction sphere: dE/dt = (1/16 pi) sum_lm |N_lm|^2 with the news
N_lm(t) = int_0^t (r psi4)_lm dt' of the modes l = 2..8 written by the code. The
integration constant and a linear drift of each N_lm (the non-radiative field of a
moving black hole at finite radius) are removed by a straight-line fit over the
analysed window before squaring; the energy without that removal is printed as well,
as a measure of how much the estimate depends on it.
"""
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mp_common as mc  # noqa: E402
from mp_common import by, figstyle  # noqa: E402

# label: (basename, legend, colour, P, expected ADM mass or None)
CASES = {
    "b16_p0.3_approx": ("byb", r"Bowen-York $P=0.3$, corrected", figstyle.PAL["red"], 0.3),
    "b16_p0.3_none": ("byb", r"Bowen-York $P=0.3$, uncorrected", figstyle.PAL["orange"],
                      0.3),
    "b16_ref_v0.2844": ("bref", r"boosted slice $v=0.284$", figstyle.PAL["blue"], None),
    "b_ref_v0.2844": ("bref", r"boosted slice, cells 1/32", figstyle.PAL2["sky"], None),
    "b16_p0.6_approx": ("byb", r"Bowen-York $P=0.6$, corrected", figstyle.PAL["green"],
                        0.6),
    "b16_spin0.3": ("byb", r"$P=0.043$, $S=0.3$, corrected", figstyle.PAL["yellow"],
                    0.043),
}


def load(label):
    try:
        man = mc.run_by_label(label, status=None)
    except KeyError:
        return None
    d = man["output_directory"]
    base = CASES[label][0]
    if not os.path.exists(os.path.join(d, base + ".co_0.txt")):
        return None
    try:
        out = {"man": man, "dir": d,
               "trk": mc.read_tracker(os.path.join(d, base + ".co_0.txt")),
               "hst": mc.read_hst(os.path.join(d, base + ".z4c.user.hst"))}
    except ValueError:        # a run that has just started: no rows yet
        return None
    out["hor"], out["hor_missed"] = mc.read_horizon(
        os.path.join(d, base + ".horizon_summary_0.txt"))
    out["waves"] = {}
    for fr in sorted(glob.glob(os.path.join(d, "waveforms", "rpsi4_real_*.txt"))):
        rad = float(os.path.basename(fr)[11:-4])
        re = mc.read_table_file(fr)
        im = mc.read_table_file(fr.replace("_real_", "_imag_"))
        _, idx = np.unique(re[:, 0], return_index=True)
        out["waves"][rad] = (re[idx, 0], re[idx, 1:] + 1j * im[idx, 1:])
    return out


def mean_speed(trk, t0, t1):
    """Mean coordinate speed between t0 and t1 from the tracker positions."""
    t, x = trk["t"], trk["x"]
    if t[-1] < t1 - 0.1:
        return float("nan")
    t1 = min(t1, t[-1])
    xa = np.array([np.interp(t0, t, x[:, a]) for a in range(3)])
    xb = np.array([np.interp(t1, t, x[:, a]) for a in range(3)])
    return float(np.linalg.norm(xb - xa) / (t1 - t0))


def burst_energy(t, modes, t0, t1, detrend=True):
    """Energy through the sphere between t0 and t1 and the cumulative curve."""
    sel = (t >= t0) & (t <= t1)
    ts, ms = t[sel], modes[sel]
    news = np.concatenate([np.zeros((1, ms.shape[1])),
                           np.cumsum(0.5 * (ms[1:] + ms[:-1]) * np.diff(ts)[:, None],
                                     axis=0)])
    if detrend:
        for k in range(news.shape[1]):
            news[:, k] -= (np.polyval(np.polyfit(ts, news[:, k].real, 1), ts)
                           + 1j * np.polyval(np.polyfit(ts, news[:, k].imag, 1), ts))
    flux = np.sum(np.abs(news)**2, axis=1) / (16.0 * np.pi)
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (flux[1:] + flux[:-1]) * np.diff(ts))])
    return float(cum[-1]), ts, cum


def main():
    figstyle.use_style()
    runs = {lab: load(lab) for lab in CASES}
    runs = {k: v for k, v in runs.items() if v is not None}
    res = {}
    madm = {0.3: by.solve_axisym(1.0, 0.3)["m_adm"], 0.6: by.solve_axisym(1.0, 0.6)["m_adm"]}
    print(f"{'label':18s} {'run id':30s} {'t_end':>6s} {'v(10-20)':>9s} {'v(20-30)':>9s}"
          f" {'v(30-40)':>9s} {'v_last':>7s} {'M_AH first':>10s} {'M_AH last':>10s}"
          f" {'S last':>8s} {'missed':>6s}")
    for lab, r in runs.items():
        trk, hor = r["trk"], r["hor"]
        e = {"run_id": r["man"]["run_id"], "t_end": float(trk["t"][-1]),
             "v10_20": mean_speed(trk, 10, 20), "v20_30": mean_speed(trk, 20, 30),
             "v30_40": mean_speed(trk, 30, 40),
             "v_last": float(np.linalg.norm(trk["v"][-1])),
             "dir_x": float(trk["x"][-1, 0] - trk["x"][0, 0]),
             "drift_yz": float(np.max(np.abs(trk["x"][:, 1:]))),
             "mah_first": float(hor["mass"][0]) if len(hor["mass"]) else float("nan"),
             "mah_last": float(hor["mass"][-1]) if len(hor["mass"]) else float("nan"),
             "mah_min": float(np.min(hor["mass"])) if len(hor["mass"]) else float("nan"),
             "mah_max": float(np.max(hor["mass"])) if len(hor["mass"]) else float("nan"),
             "s_last": float(hor["S"][-1]) if len(hor["S"]) else float("nan"),
             "sz_last": float(hor["Sz"][-1]) if len(hor["S"]) else float("nan"),
             "hor_missed": r["hor_missed"], "hor_found": int(len(hor["mass"])),
             "wall_s": r["man"].get("wall_time_s"),
             "card_hours": r["man"].get("card_hours")}
        h = r["hst"]
        e["Hnorm0"] = float(np.sqrt(h["H-norm2"][0] / h["Volume"][0]))
        e["Hnorm_max"] = float(np.sqrt(np.max(h["H-norm2"] / h["Volume"])))
        e["Hnorm_last"] = float(np.sqrt(h["H-norm2"][-1] / h["Volume"][-1]))
        e["Mnorm_last"] = float(np.sqrt(h["M-norm2"][-1] / h["Volume"][-1]))
        for rad, (t, modes) in r["waves"].items():
            t1 = min(t[-1], 40.0)
            e[f"E_r{rad:g}"] = burst_energy(t, modes, 0.0, t1)[0]
            e[f"E_r{rad:g}_raw"] = burst_energy(t, modes, 0.0, t1, detrend=False)[0]
        res[lab] = e
        print(f"{lab:18s} {e['run_id']:30s} {e['t_end']:6.2f} {e['v10_20']:9.4f}"
              f" {e['v20_30']:9.4f} {e['v30_40']:9.4f} {e['v_last']:7.4f}"
              f" {e['mah_first']:10.5f} {e['mah_last']:10.5f} {e['s_last']:8.4f}"
              f" {e['hor_missed']:6d}")
    print("expected P/M_ADM: P = 0.3: %.4f (M_ADM %.4f), P = 0.6: %.4f (M_ADM %.4f)"
          % (0.3 / madm[0.3], madm[0.3], 0.6 / madm[0.6], madm[0.6]))
    for lab, e in res.items():
        ws = " ".join(f"{k} = {v:.3e}" for k, v in e.items() if k.startswith("E_r"))
        print(f"{lab:18s} H norm t=0 {e['Hnorm0']:.3e} max {e['Hnorm_max']:.3e} last"
              f" {e['Hnorm_last']:.3e}; M norm last {e['Mnorm_last']:.3e}; {ws}; card"
              f" hours {e['card_hours']}")
    with open(os.path.join(mc.HERE, "boost_check.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure 1: speed, position, horizon mass, Hamiltonian norm
    fig, ax = plt.subplots(2, 2, figsize=(figstyle.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.09, top=0.97, wspace=0.26,
                        hspace=0.06)
    for lab, r in runs.items():
        _, name, col, p = CASES[lab]
        trk, hor, h = r["trk"], r["hor"], r["hst"]
        ax[0, 0].plot(trk["t"], trk["v"][:, 0], color=col)
        ax[0, 1].plot(trk["t"], trk["x"][:, 0] - trk["x"][0, 0], color=col)
        ax[1, 0].plot(hor["t"], hor["mass"], color=col, label=name)
        ax[1, 1].semilogy(h["time"], np.sqrt(h["H-norm2"] / h["Volume"]), color=col)
    for p, c in ((0.3, figstyle.PAL["red"]), (0.6, figstyle.PAL["green"])):
        ax[0, 0].axhline(p / madm[p], color=c, lw=1.0, ls="--")
    ax[0, 0].text(1.0, 0.3 / madm[0.3] + 0.008, r"$P/M_{\rm ADM}$, $P=0.3$", fontsize=8)
    ax[0, 0].text(1.0, 0.6 / madm[0.6] + 0.008, r"$P/M_{\rm ADM}$, $P=0.6$", fontsize=8)
    ax[0, 0].set_ylabel(r"tracker speed $-\beta^x$")
    ax[0, 0].set_ylim(0.0, 0.55)
    ax[0, 1].set_ylabel(r"tracker displacement $x-x_0$")
    ax[1, 0].set_ylabel("horizon mass")
    ax[1, 0].set_ylim(0.99, 1.36)
    ax[1, 0].legend(fontsize=7.5, loc="upper left")
    ax[1, 1].set_ylabel(r"norm of $H$ (history)")
    for a in ax[1]:
        a.set_xlabel(r"$t/m$")
        a.set_xlim(0, 40)
    print("figure:", mc.savefig(fig, "boost_evolution"))

    # ---- figure 2: dominant modes at the outer sphere and cumulative energy
    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.95, wspace=0.26)
    rad = 0.0
    for lab, r in runs.items():
        if not r["waves"]:
            continue
        _, name, col, p = CASES[lab]
        rad = max(r["waves"])
        t, modes = r["waves"][rad]
        # l = 2 modes: columns 0..4 are m = -2..2
        ax[0].plot(t, np.sqrt(np.sum(np.abs(modes[:, :5])**2, axis=1)), color=col,
                   label=name)
        _, ts, cum = burst_energy(t, modes, 0.0, min(t[-1], 40.0))
        ax[1].semilogy(ts[1:], cum[1:], color=col)
    ax[0].set_yscale("log")
    ax[0].set_xlabel(r"$t/m$")
    ax[0].set_ylabel(r"$|r\psi_4|$, $l=2$, sphere at %g" % rad)
    ax[0].legend(fontsize=7.5, loc="lower right")
    ax[1].set_xlabel(r"$t/m$")
    ax[1].set_ylabel("energy through the sphere at %g" % rad)
    ax[1].set_ylim(1e-8, 1e-3)
    print("figure:", mc.savefig(fig, "boost_waves"))


if __name__ == "__main__":
    main()
