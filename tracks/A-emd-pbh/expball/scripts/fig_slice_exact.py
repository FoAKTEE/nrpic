#!/usr/bin/env python3
"""Figures of the initial slice and of the exact shell evolution (registered as a run):

    fig_initial_slice   rho/rho_b, Delta, KL/H and KT/H, psi, 2m/R, 1+2E against R
    fig_exact_shells    world lines R(tau) of shells, turnaround, horizon and crunch events,
                        and tau_ta, tau_c, tau_AH against the shell label R_i
"""

import json
import os
import shutil
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_PKG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, _PKG)

import numpy as np  # noqa: E402

from expball import exact, model as M, runlog  # noqa: E402

REPO = os.path.normpath(os.path.join(_PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RB = 8.0
CORE = dict(delta_c=1.0, R1=0.3 * RB, R2=0.75 * RB)


def main():
    with runlog.Run("A-pre-1: figures of the initial slice (flat, top-hat, smoothed top-hat) "
                    "and of the exact shell evolution", kind="production", cores=4) as run:
        fs.use_style()
        balls = dict(flat=M.Ball.from_HRb(0.5),
                     tophat=M.Ball.from_HRb(0.5, profile=M.TopHat(**CORE)),
                     smooth_tophat=M.Ball.from_HRb(0.5, profile=M.SmoothTopHat(**CORE)))
        cols = dict(flat=fs.PAL["blue"], tophat=fs.PAL["yellow"], smooth_tophat=fs.PAL["red"])
        R = np.linspace(1e-3, 1.4 * RB, 3000)
        fig, axes = plt.subplots(2, 3, figsize=(8.0, 4.8), sharex=True)
        fig.subplots_adjust(left=0.08, right=0.99, bottom=0.1, top=0.97, wspace=0.3, hspace=0.08)
        res = {}
        for name, b in balls.items():
            c = b.at(R)
            rb = b.rbar_of_R(R)
            psi = np.sqrt(R / rb)
            lab = name.replace("_", " ")
            ax = axes[0, 0]; ax.plot(R / RB, c["rho"] / b.rho_b, color=cols[name], label=lab)
            ax = axes[0, 1]; ax.plot(R / RB, c["Delta"], color=cols[name])
            ax = axes[0, 2]
            ax.plot(R / RB, c["KL"] / b.H, color=cols[name], ls="-")
            ax.plot(R / RB, c["KT"] / b.H, color=cols[name], ls="--")
            ax = axes[1, 0]; ax.plot(R / RB, psi - 1, color=cols[name])
            ax = axes[1, 1]; ax.plot(R / RB, 2 * c["m"] / R, color=cols[name])
            ax = axes[1, 2]; ax.plot(R / RB, c["f"], color=cols[name])
            res[name] = dict(psi_centre=float(psi[0]), max_2m_over_R=float(np.max(2 * c["m"] / R)),
                             min_f=float(c["f"].min()), rho_min=float(c["rho"][R < b.Rb].min() / b.rho_b))
        axes[0, 0].set_ylabel(r"$\rho/\rho_b$"); axes[0, 0].legend(fontsize=8)
        axes[0, 1].set_ylabel(r"$\Delta$ (mean contrast inside $R$)")
        axes[0, 2].set_ylabel(r"$K_L/H$ (solid), $K_T/H$ (dashed)")
        axes[1, 0].set_ylabel(r"$\psi - 1$")
        axes[1, 1].set_ylabel(r"$2m/R$")
        axes[1, 1].axhline(0.25, **fs.MASK_LINE)
        axes[1, 2].set_ylabel(r"$1 + 2E$")
        for ax in axes[1]:
            ax.set_xlabel(r"$R/R_b$", labelpad=-2)
        for ax in axes.ravel():
            ax.axvline(1.0, **fs.MASK_LINE)
        f1 = fs.save(fig, os.path.join(run.out, "fig_initial_slice"))
        plt.close(fig)
        # exact shells
        fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.0))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.25, hspace=0.25)
        for row, name in enumerate(("smooth_tophat", "tophat")):
            b = balls[name]
            Ri = np.linspace(RB / 40, RB, 40)
            sh = exact.Shells(b, Ri)
            fine = exact.Shells(b, np.linspace(RB / 2000, RB, 2000))
            fh = fine.first_horizon()
            tmax = 1.15 * float(np.min(fine.tau_c[fine.bound]))
            tau = np.linspace(0, tmax, 1500)
            Rt = sh.R(tau)
            ax = axes[row, 0]
            cmap = fs.series_colors(len(Ri))
            for k in range(len(Ri)):
                alive = (tau <= sh.tau_c[k]) if sh.bound[k] else np.ones_like(tau, bool)
                ax.plot(tau[alive], Rt[k][alive] / RB, color=cmap[k], lw=0.8)
            bb = sh.bound & (sh.tau_c < tmax)
            ax.plot(sh.tau_ta[bb], sh.R_max[bb] / RB, "o", ms=2.5, color="k", label="turnaround")
            ok = fine.bound & (fine.tau_ah < tmax)
            ax.plot(fine.tau_ah[ok], 2 * fine.m[ok] / RB, color=fs.PAL["red"], lw=1.5,
                    label=r"$R = 2m$ (trapped sphere)")
            ax.plot([fh["tau_ah"]], [2 * fh["m"] / RB], "*", ms=9, color=fs.PAL["red"])
            ax.set_xlim(0, tmax)
            ax.set_ylim(0, 2.6)
            ax.set_ylabel(r"$R/R_b$")
            ax.set_xlabel(r"proper time $\tau$ [$M$]", labelpad=-2)
            ax.set_title(name.replace("_", " ") + r": world lines of shells", fontsize=10)
            ax.legend(fontsize=7, loc="upper left")
            ax = axes[row, 1]
            for key, lab, cc in (("tau_ta", r"$\tau_{\rm ta}$", fs.PAL["blue"]),
                                 ("tau_ah", r"$\tau_{\rm AH}$", fs.PAL["red"]),
                                 ("tau_c", r"$\tau_{\rm c}$", "k")):
                v = getattr(fine, key)
                ax.plot(fine.R_i / RB, np.where(fine.bound, v, np.nan) / b.t_i, color=cc, label=lab,
                        ls="--" if key == "tau_c" else "-")
            ax.axvline(b.prof.R1 / RB, **fs.MASK_LINE)
            ax.axvline(b.prof.R2 / RB, **fs.MASK_LINE)
            ax.set_yscale("log")
            ax.set_ylim(1, 300)
            ax.set_xlabel(r"shell label $R_i/R_b$", labelpad=-2)
            ax.set_ylabel(r"proper time / $t_i$")
            ax.legend(fontsize=8)
            tsc = sh.shell_crossing(np.linspace(0, 0.999 * float(np.min(sh.tau_c[sh.bound])), 3000))
            res[name].update(first_horizon=fh, core_tau_ta=float(fine.tau_ta[0]),
                             core_tau_c=float(fine.tau_c[0]), shell_crossing_before_first_crunch=tsc,
                             t_i=b.t_i)
        f2 = fs.save(fig, os.path.join(run.out, "fig_exact_shells"))
        plt.close(fig)
        for fp in f1 + f2:
            shutil.copy(fp, os.path.join(_PKG, "figures", os.path.basename(fp)))
        with open(os.path.join(run.out, "slice_exact.json"), "w") as fh_:
            json.dump(res, fh_, indent=1, default=float)
        run.results = res
        print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
