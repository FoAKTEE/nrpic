#!/usr/bin/env python3
"""Figure: member energies of P1 against t in units (m1 m2 / a0)(M / m_b)^(1/3), a0 = 5
(4.96e-3 M), with the full-Newton baseline.

E_i^bc: energy of member i against the barycentre of M and the other member (newton3_fix
convention, nrread.barycentric_energy; HANDOFF, Traps); the conserved one only once the other
member is bound to M and i has left, so NOT conserved before the separation. E_bin: binding
energy of the two members. P1: tracker positions and the trackers' own velocities (v = -beta,
coordinate quantities, bare masses); Newton: same formulas on the Newtonian solution.
Writes <out>/fig_energies.{pdf,png}.
Usage: fig_energies.py [--out=<dir>] [--rundir=<dir>] [--baselines-npz=<file>]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402
import figstyle as fs  # noqa: E402


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    t, X, V = p1lib.tracker_common(rd)
    b = p1lib.baselines(p1lib.baseline_path(sys.argv, out))
    m = p1lib.MASSES
    Eu = p1lib.energy_unit()
    E = p1lib.nr.member_energies(X, V, m, iM=2)
    tn = b["newton_t"]
    En = p1lib.nr.member_energies(b["newton_X"], b["newton_V"], m, iM=2)
    tmax = max(float(t[-1]) + 30.0, 150.0)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.93, hspace=0.06)
    ax = axs[0]
    for k, col, lab in ((0, fs.PAL["blue"], r"$m_1$"), (1, fs.PAL["red"], r"$m_2$")):
        ax.plot(t, E[f"E_{k}_bc"] / Eu, color=col, lw=1.2, label=f"{lab}: P1")
        ax.plot(tn, En[f"E_{k}_bc"] / Eu, color=col, lw=1.0, ls="--", label=f"{lab}: Newton")
    ax.axhline(0, **fs.MASK_LINE)
    ax.axvline(t[-1], **fs.MASK_LINE)
    ax.set_ylim(-4, 4)
    ax.set_ylabel(r"$E_i^{\rm bc}$ [units]")
    ax.set_title("against the barycentre of M and the other member; "
                 "not conserved before the binary separates", fontsize=8)
    ax.legend(frameon=False, fontsize=7, ncol=2, loc="lower left")
    ax = axs[1]
    ax.plot(t, E["E_bin"] / Eu, color=fs.PAL["yellow"], lw=1.2, label=r"$E_{\rm bin}$ P1")
    ax.plot(tn, En["E_bin"] / Eu, color=fs.PAL["yellow"], lw=1.0, ls="--",
            label=r"$E_{\rm bin}$ Newton")
    ax.axhline(0, **fs.MASK_LINE)
    ax.axvline(t[-1], **fs.MASK_LINE)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlim(0, tmax)
    ax.set_ylabel(r"$E_{\rm bin}$ [units]")
    ax.set_xlabel(r"$t\ [M]$")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    for p in fs.save(fig, os.path.join(out, "fig_energies")):
        print("figure:", p)


if __name__ == "__main__":
    main()
