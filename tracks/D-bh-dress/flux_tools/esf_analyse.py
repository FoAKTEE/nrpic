#!/usr/bin/env python3
"""Analysis of the ES-F matter run (gate G2 of Track D: the mass growth agrees with the
integrated particle flux through the horizon), prepared before the run.

    esf_analyse.py --run <ES-F run dir> --data <ES-F data run dir> [--control <V-0 or
                   V-1 horizon summary>] [--floor 2.8e-5] [--t0 0] [--out DIR]

1. Flux bracket (compare.py) with the energy fixed per particle by the initial data,
   E_K = (1 - 2M/R0)^(1/2) (energy_by_tag.npy), not the code's gauge-dependent E:
   F_rem(t) <= dM_AH(t) <= F_sph(t), and the closure after the inflow window.
2. Per label (exact LTB, gauge invariant): every removed particle of label R0 has crossed
   the horizon, so at its removal time M_AH >= m(R0) - 3 sigma; its proper time at removal
   lies in [tau_H(R0), tau_0(R0)] (horizon crossing to the centre).
3. The growth law: M_AH against the largest m(R0) removed so far, and against the proper
   time of the removed shells, with the exact curve m(tau_H).
Writes esf_analysis.json and esf_growth.png. Partial runs are read as far as they go.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare as cmp  # noqa: E402
import fluxio  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--base", default="esf")
    ap.add_argument("--control")
    ap.add_argument("--floor", type=float, default=2.8e-5)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--sphere", type=int, default=1)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    b = os.path.join(a.run, a.base)
    hor = fluxio.read_horizon(b + ".horizon_summary_0.txt")
    rem = fluxio.read_removed(b + ".removed.bin")
    acc = fluxio.read_hst(b + ".acc.hst")
    hst = fluxio.read_hst(b + ".nrpic.hst")
    ctrl = fluxio.read_horizon(a.control) if a.control else None
    EK = np.load(os.path.join(a.data, "energy_by_tag.npy"))
    lab = np.load(os.path.join(a.data, "esf_labels.npz"))
    grow = np.loadtxt(os.path.join(a.data, "esf_growth.csv"), delimiter=",", skiprows=1)
    out = dict(run=a.run, t_end_hst=float(hst["time"][-1]), np_end=int(hst["np"][-1]),
               n_records=int(rem["n"]),
               reasons={str(k): int(np.sum(rem["reason"] == k)) for k in (1, 2, 3, 4)})
    res = None
    if hor["time"].size >= 2:
        res = cmp.compare(hor, a.t0, rem=rem, acc=acc, ctrl=ctrl, floor=a.floor,
                          sphere=a.sphere, E_by_tag=EK)
        out["bracket_energy_by_tag"] = res["summary"]
        res_code = cmp.compare(hor, a.t0, rem=rem, acc=acc, ctrl=ctrl, floor=a.floor,
                               sphere=a.sphere)
        out["bracket_code_energy"] = res_code["summary"]
        cmp.plot(res, os.path.join(a.out, "esf_bracket"),
                 "ES-F: finder mass against the horizon flux (initial-data energies)")
    # per label
    hz = np.isin(rem["reason"], (2, 3))
    tag = rem["tag"][hz]
    dust = lab["rest"][tag] > 1e-20
    if hz.any() and hor["time"].size:
        trem = rem["time"][hz]
        M_at = np.interp(trem, hor["time"], hor["mass"])
        m_lab = lab["m_label"][tag]
        tau = rem["tau"][hz]
        out["per_label"] = dict(
            n=int(hz.sum()), n_dust=int(dust.sum()),
            M_minus_mlabel_min=float(np.min(M_at - m_lab)),
            tau_below_tauH=int(np.sum(tau < lab["tauH"][tag] * (1 - 1e-6))),
            tau_above_tau0=int(np.sum(tau > lab["tau0"][tag] * (1 + 1e-6))),
            R0_max_removed=float(lab["R0"][tag][dust].max()) if dust.any() else None)
    figure(a.out, hor, rem, lab, grow, res)
    with open(os.path.join(a.out, "esf_analysis.json"), "w") as f:
        json.dump(cmp.jsonable(out), f, indent=1)
    print(json.dumps(cmp.jsonable(out), indent=1))


def figure(out, hor, rem, lab, grow, res):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0))
    ax[0].plot(hor["time"], hor["mass"], color=figstyle.PAL["blue"], label=r"$M_{\rm AH}$ (finder)")
    hz = np.isin(rem["reason"], (2, 3))
    if hz.any():
        tag = rem["tag"][hz]
        order = np.argsort(rem["time"][hz])
        mmax = np.maximum.accumulate(lab["m_label"][tag][order])
        ax[0].step(rem["time"][hz][order], mmax, where="post", color=figstyle.PAL["red"],
                   label=r"largest $m(R_0)$ removed (lower bound)")
        ax[1].plot(rem["tau"][hz], np.interp(rem["time"][hz], hor["time"], hor["mass"]), ".",
                   ms=1, color=figstyle.PAL["red"], label=r"$M_{\rm AH}$ at removal vs $\tau_{\rm rem}$")
    ax[0].set_xlabel(r"code time $t\ [M]$")
    ax[0].set_ylabel(r"$[M]$")
    ax[0].legend(fontsize=6)
    ax[1].plot(grow[:, 2], grow[:, 1], **figstyle.GUIDE, label=r"exact: $m(R_0)$ at $\tau_H(R_0)$")
    ax[1].set_xlim(0, max(50.0, float(np.nanmax(rem["tau"])) * 1.1) if rem["n"] else 300)
    ax[1].set_ylim(0.99, 1.4)
    ax[1].set_xlabel(r"proper time of the shell $\tau\ [M]$")
    ax[1].set_ylabel(r"$M_{\rm AH}\ [M]$")
    ax[1].legend(fontsize=6)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "esf_growth"))
    plt.close(fig)


if __name__ == "__main__":
    main()
