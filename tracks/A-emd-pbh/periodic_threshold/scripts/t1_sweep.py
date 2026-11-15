"""T1 sweep (JOURNAL.md): the peak data of make_peak_ic.py for several amplitudes,
start epochs, resolutions and filters; table and figure of the solve change c.

    python3 t1_sweep.py --out DIR [--only-table]
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

S6 = float(np.sqrt(6.0))
CASES = []
for mu in (0.03, 0.5):
    for eps in (0.2, 1.0, S6):
        CASES.append(dict(mu=mu, eps=eps, n=64, nfilter=2))
CASES += [dict(mu=0.03, eps=1.0, n=32, nfilter=2), dict(mu=0.03, eps=1.0, n=128, nfilter=2),
          dict(mu=0.03, eps=1.0, n=64, nfilter=0)]


def name(c):
    return f"mu{c['mu']:g}_eps{c['eps']:.3f}_n{c['n']}_f{c['nfilter']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only-table", action="store_true")
    a = ap.parse_args()
    rows = []
    for c in CASES:
        d = os.path.join(a.out, name(c))
        if not a.only_table:
            cmd = [sys.executable, "-I", os.path.join(HERE, "make_peak_ic.py"),
                   "--mu", str(c["mu"]), "--e", "0.2", "--eps-i", repr(c["eps"]),
                   "--n", str(c["n"]), "--nfilter", str(c["nfilter"]), "--out", d]
            if c["nfilter"] > 0:
                cmd.append("--compensate")
            with open(d + ".log", "w") as f:
                subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=True)
        with open(os.path.join(d, "id.json")) as f:
            info = json.load(f)
        rows.append(dict(c, name=name(c), c_ratio=info["solve_change_over_dictionary_c"],
                         psi_dict_pert=info["max_abs_psi_dict_minus_1"],
                         outer_change=info["outer_last_change_of_psi"],
                         ham=info["max_hamiltonian_residual"],
                         mom=info["max_momentum_residual"],
                         disp=info["max_displacement_over_h"],
                         mmin=info["mass_min_over_mean"], mmax=info["mass_max_over_mean"],
                         alpha_min=info["alpha_min"], ge=info["ge"]))
    with open(os.path.join(a.out, "t1_table.json"), "w") as f:
        json.dump(rows, f, indent=1)
    print(f"{'case':34s} {'c':>8s} {'psi_d-1':>9s} {'outer':>9s} {'ham':>9s} "
          f"{'disp/h':>8s} {'gt-d (GE)':>10s} {'TT frac':>8s}")
    for r in rows:
        print(f"{r['name']:34s} {r['c_ratio']:8.4f} {r['psi_dict_pert']:9.2e} "
              f"{r['outer_change']:9.2e} {r['ham']:9.2e} {r['disp']:8.4f} "
              f"{r['ge']['max_abs_gamma_tilde_minus_delta']:10.2e} "
              f"{r['ge']['tt_fraction_of_p_ij_L2']:8.4f}")

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 5.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, wspace=0.3,
                        hspace=0.32)
    # top left: c against eps_i for the two amplitudes at n = 64
    ax = fig.add_subplot(2, 2, 1)
    for mu, col in ((0.03, fs.PAL["blue"]), (0.5, fs.PAL["red"])):
        rr = [r for r in rows if r["mu"] == mu and r["n"] == 64 and r["nfilter"] == 2]
        ax.loglog([r["eps"] for r in rr], [r["c_ratio"] for r in rr], "o-", color=col,
                  label=rf"$\mu = {mu}$")
    e = np.array([0.2, S6])
    r1 = [r for r in rows if r["mu"] == 0.03 and r["n"] == 64 and r["eps"] == 1.0
          and r["nfilter"] == 2][0]
    ax.loglog(e, r1["c_ratio"]/e**2, label=r"$\propto \epsilon_i^{-2}$", **fs.GUIDE)
    ax.set_xlabel(r"$\epsilon_i = k/(a_i H_i)$")
    ax.set_ylabel(r"$c$ (solve change / dictionary)")
    ax.legend(frameon=False)
    # top right: c against cell size at mu = 0.03, eps_i = 1
    ax = fig.add_subplot(2, 2, 2)
    rr = sorted([r for r in rows if r["mu"] == 0.03 and r["eps"] == 1.0
                 and r["nfilter"] == 2], key=lambda r: r["n"])
    hh = np.array([20.0/r["n"] for r in rr])
    cc = np.array([r["c_ratio"] for r in rr])
    ax.loglog(hh, cc, "o-", color=fs.PAL["red"], label="nfilter = 2, compensated")
    r0 = [r for r in rows if r["nfilter"] == 0][0]
    ax.loglog([20.0/64], [r0["c_ratio"]], "s", color=fs.PAL["yellow"], label="nfilter = 0")
    ax.loglog(hh, cc[-1]*(hh/hh[-1])**2, label=r"$\propto h^2$", **fs.GUIDE)
    ax.set_xlabel(r"cell size $k h$")
    ax.set_ylabel(r"$c$")
    ax.legend(frameon=False)
    # bottom: psi and psi_dict along x through the peak, mu = 0.03 at the three eps_i
    for j, (mu, lab) in enumerate(((0.03, "0.03"), (0.5, "0.5"))):
        ax = fig.add_subplot(2, 2, 3 + j)
        for eps, col in ((0.2, fs.PAL["red"]), (1.0, fs.PAL["yellow"]),
                         (S6, fs.PAL["blue"])):
            d = os.path.join(a.out, name(dict(mu=mu, eps=eps, n=64, nfilter=2)))
            s = np.load(os.path.join(d, "slices.npz"))
            L = float(s["L"])
            n = int(s["n"])
            x = ((np.arange(n) + 0.5)*L/n - 0.5*L)*eps
            ax.plot(x, s["psi_line"] - 1, color=col, label=rf"solved, $\epsilon_i$ = {eps:.2f}")
            ax.plot(x, s["psi_dict_line"] - 1, color=col, ls="--")
        ax.set_xlim(-6, 6)
        ax.set_xlabel(r"$k x$ (line through the peak)")
        ax.set_ylabel(r"$\psi - 1$ (dashed: dictionary)")
        ax.text(0.03, 0.92, rf"$\mu = {lab}$", transform=ax.transAxes)
        if j == 0:
            ax.legend(frameon=False, fontsize=8, loc="upper right")
    fs.save(fig, os.path.join(a.out, "fig_t1_solve_change"))


if __name__ == "__main__":
    main()
