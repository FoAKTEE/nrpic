"""P8: how far is the Szekeres slice from the spherical (LTB) slice with the same M and k?

For dipole amplitudes eps = 0.003125 ... 0.2 (twisted dipole), the slice fields psi, rho,
K = trace and KL - KT at 40000 random points of the conformally flat coordinates
(|x_i| <= 6.5), minus those of eps = 0 at the same points; maxima against eps, log-log
slopes. Also the l = 1 content: the difference projected on the dipole direction at fixed
shell. Writes dipole_order.json and fig_dipole_order.

    python3 scripts/run_dipole_order.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402

EPS = (0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.2)


def main():
    rdir = common.run_dir("dipole_order")
    x = np.random.default_rng(21).uniform(-6.5, 6.5, (40000, 3))
    ltb, _ = common.models()
    f0 = ConformalMap(ltb).fields(x)
    rows = []
    for eps in EPS:
        _, szk = common.models(eps=eps)
        cm = ConformalMap(szk)
        f = cm.fields(x)
        d = dict(eps=eps,
                 psi=float(np.max(np.abs(f["psi"] - f0["psi"]))),
                 rho=float(np.max(np.abs(f["rho"] - f0["rho"])) / ltb.rho_b),
                 K=float(np.max(np.abs(f["K"] - f0["K"])) / ltb.H),
                 shear=float(np.max(np.abs((f["KL"] - f["KT"]) - (f0["KL"] - f0["KT"]))) / ltb.H),
                 centre_shift=float(np.linalg.norm(cm.radial_table(np.array([1.0]))["C"][:, 0])),
                 rho_min=float(f["rho"].min() / ltb.rho_b), rho_max=float(f["rho"].max() / ltb.rho_b))
        rows.append(d)
        print(d, flush=True)
    e = np.array(EPS)
    slopes = {}
    for key in ("psi", "rho", "K", "shear", "centre_shift"):
        y = np.array([rw[key] for rw in rows])
        small = e <= 0.05
        slopes[key] = dict(fit_eps_le_0p05=float(np.polyfit(np.log(e[small]), np.log(y[small]), 1)[0]),
                           pairwise=[float(np.log(y[i + 1] / y[i]) / np.log(e[i + 1] / e[i])) for i in range(len(e) - 1)],
                           coefficient_at_small_eps=float(y[0] / e[0]))
    out = dict(run_id=common.run_id(), commit=common.git_commit(), eps=list(EPS), rows=rows, slopes=slopes,
               points=len(x), box_half=6.5)
    common.dump(os.path.join(rdir, "dipole_order.json"), out)
    print(slopes)

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.15, top=0.93)
    for key, col, lab in (("psi", fs.PAL["red"], r"$\max|\psi - \psi_{\rm LTB}|$"),
                          ("rho", fs.PAL["blue"], r"$\max|\rho - \rho_{\rm LTB}|/\rho_b$"),
                          ("K", fs.PAL["green"], r"$\max|K - K_{\rm LTB}|/H$"),
                          ("shear", fs.PAL["orange"], r"$\max|\Delta(K_L - K_T)|/H$")):
        y = np.array([rw[key] for rw in rows])
        ax.loglog(e, y, "o-", color=col, ms=4, label=lab)
    y0 = np.array([rw["rho"] for rw in rows])
    ax.loglog(e, y0[0] * e / e[0], **fs.GUIDE, label=r"$\propto \epsilon$")
    ax.set_xlabel(r"dipole amplitude $\epsilon$")
    ax.set_ylabel("Szekeres minus LTB slice")
    ax.legend(fontsize=7, loc="lower right")
    common.save_fig(fig, "fig_dipole_order", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
