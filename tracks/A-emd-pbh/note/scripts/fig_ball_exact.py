"""Exact solution of the expanding ball of data set 2t (note v0, Fig. ball).

Reads only the registered exact references of run A-emd-pbh-20261115-153719-91b03d1
(exact.json, the exact LTB shells of the scouting data):
  central: scale factor a(tau) and density of the bound core against proper time;
  m_ah: mass of the outermost trapped sphere on slices of constant proper time;
  sr1_speeds, sr1_stages: largest coordinate speed of light of the comoving coordinates
    (geodesic slicing) and the step plan of the scouting run SR-1, with the stability bound
    C_MAX of the Z4c discretization (gauge package, run A-emd-pbh-20261115-113755-cac3c4b).
The Einstein-de Sitter envelope a = (1 + 3 H tau / 2)^(2/3) uses H of the same file.
Panels: (a) core and envelope against tau; (b) horizon mass after the first trapped
sphere; (c) coordinate speed of light against the time left to the crunch of the core.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from czstyle import use_style, save, PAL  # noqa: E402
import common  # noqa: E402

STEM = "fig_ball_exact"


def main():
    out = common.out_dir("figures")
    d = common.load_json("ball_exact", "exact.json")
    H = d["model"]["H"]
    core = d["core"]
    ft = d["first_trapped"]
    tau = np.array(d["central"]["tau"])
    a = np.array(d["central"]["a"])
    tm = np.array(d["m_ah"]["tau"])
    m = np.array(d["m_ah"]["m"])
    ts = np.array(d["sr1_speeds"]["tau"])
    cmax = np.array(d["sr1_speeds"]["c_max"])
    stages = d["sr1_stages"]
    C = d["C_MAX"]
    tc = core["tau_c"]

    use_style()
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.4))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.19, top=0.95, wspace=0.42)

    ax = axs[0]
    tt = np.linspace(0, tc, 400)
    ax.plot(tt, (1 + 1.5 * H * tt) ** (2.0 / 3.0), color="k", ls="--", lw=1.2)
    ax.plot(tau, a, color=PAL["blue"])
    ax.axvline(core["tau_ta"], color="grey", lw=1.0, alpha=0.5)
    ax.axvline(ft["tau"], color=PAL["red"], lw=1.0, alpha=0.6)
    ax.text(core["tau_ta"] + 0.8, 0.45, "turnaround", fontsize=8, color="grey")
    ax.text(ft["tau"] - 0.8, 2.5, "first trapped\nsphere", fontsize=8, color=PAL["red"], ha="right", va="top")
    ax.text(3, 2.15, "envelope", fontsize=8)
    ax.text(22, 1.05, "core", fontsize=8, color=PAL["blue"])
    ax.set_xlim(0, 46)
    ax.set_ylim(0, 2.6)
    ax.set_xlabel(r"proper time $\tau/M$")
    ax.set_ylabel(r"scale factor $a/a_i$")
    ax.text(0.04, 0.93, "(a)", transform=ax.transAxes)

    ax = axs[1]
    ax.plot(tm - ft["tau"], m, color=PAL["red"])
    ax.axvline(core["tau_ah_edge"] - ft["tau"], color="grey", lw=1.0, alpha=0.5)
    ax.text(core["tau_ah_edge"] - ft["tau"] + 0.003, m.min() + 0.15 * (m.max() - m.min()),
            "core edge\ntrapped", fontsize=8, color="grey")
    ax.set_xlim(0, tc - ft["tau"])
    ax.set_xlabel(r"$(\tau-\tau_{\rm AH})/M$")
    ax.set_ylabel(r"horizon mass $m_{\rm AH}/M$")
    ax.text(0.04, 0.93, "(b)", transform=ax.transAxes)

    ax = axs[2]
    ok = ts < tc
    ax.plot(tc - ts[ok], cmax[ok], color="k")
    for st in stages:
        x0, x1 = tc - st["t_from"], tc - st["t_to"]
        ax.plot([x0, x1], [C / st["cfl"]] * 2, color=PAL["orange"], lw=1.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(tc, 5e-3)
    ax.set_ylim(0.7, 300)
    ax.set_xlabel(r"$(\tau_c-\tau)/M$")
    ax.set_ylabel(r"coordinate light speed")
    ax.text(0.04, 0.93, "(c)", transform=ax.transAxes)
    ax.text(25.0, 3.1, "bound", fontsize=8, color=PAL["orange"])
    ax.text(25.0, 1.12, "largest", fontsize=8)

    save(fig, os.path.join(out, STEM))
    plt.close(fig)
    common.report_checks(STEM)
    print(f"{STEM}: tau_ta = {core['tau_ta']:.3f}, R_max/R_i = {core['R_max_over_R_i']:.4f}, "
          f"tau_AH = {ft['tau']:.3f} at R_i = {ft['R_i']:.3f} (m = {ft['m']:.4f}), "
          f"core edge trapped {core['tau_ah_edge']:.3f}, crunch {tc:.3f}, m_AH at crunch {m[-1]:.4f}, "
          f"m_AH monotone {bool(np.all(np.diff(m) >= 0))}; a(tau) max at tau = {tau[np.argmax(a)]:.2f}; "
          f"stages {[(s['t_to'], s['cfl']) for s in stages]}")


if __name__ == "__main__":
    main()
