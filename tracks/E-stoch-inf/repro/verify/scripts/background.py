#!/usr/bin/env python3
"""Fresh verifier, part 2d: box means of the records against my own Friedmann/Klein-Gordon
solution (ledger rows "Lattice background"), and the one-point widths of R^NR and dphi from my
lattice outputs (ledger rows "One-point statistics").

Usage: python background.py --out DIR --latsr DIR --latusr DIR
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare  # noqa: E402  (my potential and deck parser)
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
RUNS = {
    "sr64": (f"{S}/E-20261123-020704-2b99463/M64S", "sr"),
    "usr64": (f"{S}/E-20261123-020704-2b99463/M64U", "usr"),
    "sr256": (f"{S}/E-20261121-202935-31520bc/P256", "sr"),
    "usr256": (f"{S}/E-20261123-021204-2f573ec", "usr"),
}


def my_background(case, deck, tmax):
    V, dV = compare.potential(case, deck)
    phi0 = float(compare.deck_value(deck, "phi0"))
    pi0 = float(compare.deck_value(deck, "pi0"))

    def rhs(t, y):
        H = np.sqrt(8*np.pi/3*(0.5*y[1]**2 + V(y[0])))
        return [y[1], -3*H*y[1] - dV(y[0]), H]
    sol = solve_ivp(rhs, (0, tmax), [phi0, pi0, 0.0], method="DOP853", rtol=1e-12, atol=1e-15,
                    dense_output=True)
    return sol, V, dV


def eps_of(sol, V, dV, t):
    phi, Pi, N = sol.sol(t)
    H = np.sqrt(8*np.pi/3*(0.5*Pi**2 + V(phi)))
    e1 = 4*np.pi*Pi**2/H**2
    ddphi = -3*H*Pi - dV(phi)
    # P1 convention eps2 = -dln eps1/dN = -(2 ddphi/(H Pi) + 2 eps1)
    e2 = -(2*ddphi/(H*Pi) + 2*e1)
    return phi, Pi, N, H, e1, e2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--latsr", required=True)
    ap.add_argument("--latusr", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    figstyle.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.8))
    for name, (d, case) in RUNS.items():
        deckf = glob.glob(f"{d}/*.athinput") or glob.glob(f"{d}/chain/input.athinput")
        deck = open(deckf[0]).read()
        R = np.loadtxt(glob.glob(f"{d}/*.sf.con.hst")[0], comments="#")
        t = R[:, 0]
        sol, V, dV = my_background(case, deck, t[-1])
        phiF, PiF, NF, HF, e1F, e2F = eps_of(sol, V, dV, t)
        phi, Pi, K = R[:, 16], R[:, 17], R[:, 18]
        H = -K/3
        e1 = 4*np.pi*Pi**2/H**2
        N = R[:, 2]
        e2 = -np.gradient(np.log(e1), N)
        inner = slice(2, -2)
        r = dict(deck=deckf[0], N_final_record=float(N[-1]), N_final_mine=float(NF[-1]),
                 max_V_rel=float(np.abs(V(phi)/V(phiF) - 1).max()),
                 max_eps1_rel=float(np.abs(e1/e1F - 1).max()),
                 max_eps2_abs_finite_diff=float(np.abs(e2[inner] - e2F[inner]).max()),
                 eps1_final_mine=float(e1F[-1]), eps2_final_mine=float(e2F[-1]),
                 eps1_final_record=float(e1[-1]))
        if case == "usr":
            tt = np.linspace(0, t[-1], 200001)
            _, _, Nt, _, _, e2t = eps_of(sol, V, dV, tt)
            s = np.sign(e2t - 3)
            idx = np.where(np.diff(s) != 0)[0]
            r["eps2_equals_3_at_N"] = [float(Nt[i]) for i in idx]
            r["eps2_max"] = float(e2t.max())
            r["N_of_eps2_max"] = float(Nt[np.argmax(e2t)])
            ax = axs[1]
        else:
            ax = axs[0]
        if name.endswith("256"):
            ax.plot(N, e2, color=figstyle.SERIES[0], label="records, eps2 (finite diff.)")
            ax.plot(NF, e2F, "k--", lw=1, label="my Friedmann")
            ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
            ax.set_ylabel(r"$\varepsilon_2$ (P1 convention)")
            ax.set_title(case.upper(), fontsize=9)
            ax.legend(fontsize=6)
        res[name] = r
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_background.png"), dpi=150)
    plt.close(fig)

    # one-point widths from my lattice outputs
    for case, lat in (("sr", a.latsr), ("usr", a.latusr)):
        summ = sorted(json.load(open(glob.glob(f"{lat}/*_summary.json")[0])), key=lambda r: r["time"])
        N, hw_R, rms_R, rms_dphi = [], [], [], []
        for r in summ:
            z = np.load(os.path.join(lat, f"{case}_" + os.path.basename(r["path"]).replace(".dump", ".npz")))
            p = z["R_pct"]
            hw_R.append(0.5*(p[4] - p[2]))
            rms_R.append(r["R_rms"])
            rms_dphi.append(np.sqrt(2*np.sum(np.abs(z["c_dphi"])**2))/abs(r["mean_phi"]))
            N.append(r["efolds_from_mean_chi"])
        N, hw_R, rms_R, rms_dphi = map(np.array, (N, hw_R, rms_R, rms_dphi))

        def n95(x):
            j = np.argmax(x >= 0.95*x[-1])
            if j == 0:
                return float(N[0])
            return float(N[j-1] + (0.95*x[-1] - x[j-1])/(x[j] - x[j-1])*(N[j] - N[j-1]))
        res[f"onepoint_{case}"] = dict(N=N.tolist(), halfwidth68_R_final=float(hw_R[-1]),
                                       rms_R_final=float(rms_R[-1]),
                                       N95_dphi_over_phib=n95(rms_dphi), N95_R=n95(rms_R),
                                       R_maxabs_final=summ[-1]["R_maxabs"],
                                       rms_dphi_over_phib_final=float(rms_dphi[-1]))
    with open(os.path.join(a.out, "background.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
