"""Single HRNA encounters printed in 2404 (prediction P7 of JOURNAL.md).

    <venv>/bin/python -I examples.py <outdir>

Cases: beta = 5 prograde phi = 1.41 (article.tex:379-407, Fig. sep-P); beta = 5 retrograde
phi = 1.57 (:409-412, Fig. sep-R); beta = 5 retrograde phi = 2.04 (:424-433, Fig. sur-R);
beta = 8 retrograde, r0 = 10 r_t, phi = 0.2, 0.3, 0.5 (Fig. 1 caption, :189).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import hrna  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

CASES = [
    dict(name="b5_pro_1.41", beta=5.0, phase=1.41, sense=1, r0_rt=50.0, paper="separates; t_s = -0.01 T0, r_cm(t_s) = 31 r_g"),
    dict(name="b5_retro_1.57", beta=5.0, phase=1.57, sense=-1, r0_rt=50.0, paper="separates; t_s = 0.08 T0, r_cm(t_s) = 107 r_g; rotation reverses"),
    dict(name="b5_retro_2.04", beta=5.0, phase=2.04, sense=-1, r0_rt=50.0, paper="survives; rotation reverses"),
    dict(name="b8_retro_r10_0.2", beta=8.0, phase=0.2, sense=-1, r0_rt=10.0, paper="survives, more compact, very eccentric"),
    dict(name="b8_retro_r10_0.3", beta=8.0, phase=0.3, sense=-1, r0_rt=10.0, paper="survives, wider"),
    dict(name="b8_retro_r10_0.5", beta=8.0, phase=0.5, sense=-1, r0_rt=10.0, paper="separates"),
]


def series(o, law=hrna.LAW_HRNA):
    t, Y = o["rec_t"], o["rec_y"]
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    e1 = np.array([hrna.energy_lz(law, 0, 1.0, 0.0, y[0:3], y[3:6], g, gi, dg)[0] - 1 for y in Y])
    e2 = np.array([hrna.energy_lz(law, 0, 1.0, 0.0, y[6:9], y[9:12], g, gi, dg)[0] - 1 for y in Y])
    xc = 0.5 * (Y[:, 0:3] + Y[:, 6:9])
    vc = 0.5 * (Y[:, 3:6] + Y[:, 9:12])
    ec = np.array([hrna.energy_lz(law, 0, 1.0, 0.0, xc[i], vc[i], g, gi, dg)[0] - 1 for i in range(len(t))])
    d = Y[:, 0:3] - Y[:, 6:9]
    w = Y[:, 3:6] - Y[:, 9:12]
    sep = np.linalg.norm(d, axis=1)
    Eb = 0.5 * np.einsum("ij,ij->i", w, w) - 1e-6 / sep
    Lbz = d[:, 0] * w[:, 1] - d[:, 1] * w[:, 0]
    return t, Y, e1, e2, ec, sep, Eb, Lbz, xc


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    res = {}
    a0, mb = 1.013, 1e-6
    rt = (1 / mb) ** (1 / 3) * a0
    E0 = math.sqrt(mb / (a0 * rt))                 # article.tex:387
    Eb0 = mb / (2 * a0)
    for c in CASES:
        o = hrna.run_encounter(law="hrna", beta=c["beta"], phase=c["phase"], sense=c["sense"],
                               r0_rt=c["r0_rt"], record=400000)
        t, Y, e1, e2, ec, sep, Eb, Lbz, xc = series(o)
        T0 = o["T0"]
        tt = (t - o["t_peri"]) / T0
        res[c["name"]] = dict(
            paper=c["paper"], separated=o["separated"], t_s_T0=o["t_s"], rcm_ts=o["rcm_ts"],
            Eb_end=o["Eb_end"], ab_end_a0=(o["ab_end"] / a0 if np.isfinite(o["ab_end"]) else None),
            eb_end=o["eb_end"], a_min_a0=o["a_min"], eps1=o["eps1"], eps2=o["eps2"],
            vinf_kms=o["vinf"] * 299792.458, Lbz_sign_start=float(np.sign(Lbz[0])),
            Lbz_sign_end=float(np.sign(Lbz[-1])), alpha_all=o["alpha_all"], r_peri=o["r_peri"],
            t_s_in_sqrt2T0=(o["t_s"] / math.sqrt(2) if np.isfinite(o["t_s"]) else None))
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.4))
        ax1 = fs.inch_axes(fig, 0.7, 2.95, 3.0, 2.3)
        ax2 = fs.inch_axes(fig, 4.7, 2.95, 2.3, 2.3)
        ax3 = fs.inch_axes(fig, 0.7, 0.45, 3.0, 2.0)
        ax4 = fs.inch_axes(fig, 4.7, 0.45, 3.0, 2.0)
        win = np.abs(tt) < 1.5
        ax1.plot(Y[win, 0], Y[win, 1], color=fs.PAL["red"], lw=1.0, label="member 1")
        ax1.plot(Y[win, 6], Y[win, 7], color=fs.PAL["blue"], lw=1.0, label="member 2")
        ax1.plot([0], [0], "ko", ms=4)
        ax1.set_aspect("equal", adjustable="datalim")
        ax1.set_xlabel(r"$x\ [r_g]$")
        ax1.set_ylabel(r"$y\ [r_g]$")
        ax1.legend(loc="upper left", fontsize=8)
        rel = Y[:, 0:3] - xc
        win2 = (tt > -1.0) & (tt < 0.5)
        ax2.plot(rel[win2, 0], rel[win2, 1], color=fs.PAL["red"], lw=0.8)
        ax2.plot(-rel[win2, 0], -rel[win2, 1], color=fs.PAL["blue"], lw=0.8)
        ax2.set_aspect("equal", adjustable="datalim")
        ax2.set_xlabel(r"$x-x_{\rm cm}\ [r_g]$")
        ax2.set_ylabel(r"$y-y_{\rm cm}\ [r_g]$")
        win3 = (tt > -2) & (tt < 3)
        ax3.plot(tt[win3], e1[win3] / E0, color=fs.PAL["red"], label=r"$E_1$")
        ax3.plot(tt[win3], e2[win3] / E0, color=fs.PAL["blue"], label=r"$E_2$")
        ax3.set_xlabel(r"$(t-t_p)/T_0$")
        ax3.set_ylabel(r"$E_i/E_0$")
        ax3.legend(loc="upper left", fontsize=8)
        ax4.plot(tt[win3], Eb[win3] / Eb0, color=fs.PAL["red"], label=r"$E_b$")
        ax4.plot(tt[win3], ec[win3] / E0, color=fs.PAL["blue"], label=r"$E_{\rm cm}$ [$E_0$]")
        if np.isfinite(o["t_s"]):
            for ax in (ax3, ax4):
                ax.axvline(o["t_s"], **fs.MASK_LINE)
        ax4.set_xlabel(r"$(t-t_p)/T_0$")
        ax4.set_ylabel(r"$E_b/E_{b0}$, $E_{\rm cm}/E_0$")
        ax4.legend(loc="upper left", fontsize=8)
        fig.text(0.02, 0.975, f"HRNA, beta = {c['beta']}, phi = {c['phase']}, "
                 f"{'prograde' if c['sense'] > 0 else 'retrograde'}, r0 = {c['r0_rt']} r_t", fontsize=9)
        fs.save(fig, os.path.join(outdir, "ex_" + c["name"]))
        plt.close(fig)
    with open(os.path.join(outdir, "examples.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
