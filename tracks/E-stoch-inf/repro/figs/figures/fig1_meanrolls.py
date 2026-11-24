"""Fig. 1 of arXiv:2512.14649 (P1:428-442, fig:MeanRolls): V(phi_b), eps1, eps2 against the box-mean
e-folds of the 64^3 runs M64S (quadratic) and M64U (inflection), with the Friedmann solution.

Box means from the constraint record <basename>.sf.con.hst (columns 0 time, 2 efolds = -ln<chi>/2,
16 <phi>, 17 <Pi>, 18 <K>, 19 <alpha>); H = -<K>/(3<alpha>); eps1 = 4 pi <Pi>^2/H^2, eps2 = 6 + 2 V'/(H
<Pi>) - 2 eps1 (P1's sign: eps2 = -dln eps1/dN, +6 in USR). Reference: own Friedmann integration
from (phi0, pi0) of the decks at the record times (figlib.friedmann). V in P1's units (Mpl = 100).
Writes fig1_meanrolls.{png,pdf}, fig1_residuals.png and fig1.json (scope P5, map S8, S9).

Usage: fig1_meanrolls.py OUTDIR
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402
import runs as rr  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402  (python/nrpic/figstyle.py)


def measure(label, case):
    c = fl.read_con(rr.con_path(label))
    t, N = c[:, 0], c[:, 2]
    phi, pi, K, al = c[:, 16], c[:, 17], c[:, 18], c[:, 19]
    hub = -K / (3.0 * al)
    v, _ = fl.potential_code(case, phi)
    e1, e2 = fl.rolls(case, phi, pi, hub)
    fphi, fpi, flna, fh = fl.friedmann(case, t)
    fv, _ = fl.potential_code(case, fphi)
    f1, f2 = fl.rolls(case, fphi, fpi, fh)
    return dict(t=t, N=N, V=v, e1=e1, e2=e2, fN=flna, fV=fv, f1=f1, f2=f2)


def crossings(N, y, level):
    s = np.sign(y - level)
    idx = np.flatnonzero(s[1:] != s[:-1])
    out = []
    for i in idx:
        out.append(float(N[i] + (level - y[i]) * (N[i + 1] - N[i]) / (y[i + 1] - y[i])))
    return out


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    res = {}
    data = {"sr": measure("M64S", "sr"), "usr": measure("M64U", "usr")}
    for case, d in data.items():
        res[case] = dict(
            n_lines=int(d["t"].size), N_end=float(d["N"][-1]), N_end_friedmann=float(d["fN"][-1]),
            max_rel_V=float(np.max(np.abs(d["V"] / d["fV"] - 1.0))),
            max_rel_eps1=float(np.max(np.abs(d["e1"] / d["f1"] - 1.0))),
            max_abs_eps2=float(np.max(np.abs(d["e2"] - d["f2"]))),
            max_abs_N=float(np.max(np.abs(d["N"] - d["fN"]))),
            eps1_end=float(d["e1"][-1]), eps2_end=float(d["e2"][-1]),
            eps1_min=float(d["e1"].min()), N_eps1_min=float(d["N"][np.argmin(d["e1"])]),
            eps2_eq3=crossings(d["N"], d["e2"], 3.0),
            eps2_eq3_friedmann=crossings(d["fN"], d["f2"], 3.0))
    # P5 verdicts (scope JOURNAL entry 1)
    s, u = res["sr"], res["usr"]
    res["P5"] = dict(
        sr=bool(s["max_rel_V"] < 1e-8 and s["max_rel_eps1"] < 1e-6 and s["max_abs_eps2"] < 1e-5),
        usr=bool(u["max_rel_V"] < 1e-6 and u["max_abs_eps2"] < 1e-2
                 and abs(u["eps2_end"] + 0.0276) < 0.002))
    with open(os.path.join(out, "fig1.json"), "w") as fp:
        json.dump(res, fp, indent=1)

    # ---- the figure in P1's layout: two columns, rows V, eps1, eps2
    fig, ax = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 7.0), sharex="col")
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.07, top=0.95, hspace=0.0, wspace=0.28)
    for j, (case, title) in enumerate([("sr", "Quadratic inflation (M64S)"),
                                       ("usr", "Inflection inflation (M64U)")]):
        d = data[case]
        for i, (key, fkey) in enumerate([("V", "fV"), ("e1", "f1"), ("e2", "f2")]):
            y, fy = d[key], d[fkey]
            if key == "V":
                y, fy = fl.v_to_p1(case, y), fl.v_to_p1(case, fy)
            ax[i, j].plot(d["fN"], fy, color=fs.PAL["blue"], lw=3.0, alpha=0.5,
                          label="Friedmann")
            ax[i, j].plot(d["N"], y, color=fs.PAL["red"], lw=1.2, label=r"NR box mean, $64^3$")
        ax[0, j].set_title(title, fontsize=10)
        ax[2, j].set_xlabel(r"$\langle\mathcal{N}\rangle$")
        ax[2, j].set_xlim(0, d["N"][-1])
        if case == "usr":
            for i in (1, 2):
                ax[i, j].axhline(0.0, **fs.MASK_LINE)
            ins = ax[1, j].inset_axes([0.55, 0.45, 0.4, 0.45])
            sel = d["N"] > 7.6
            ins.plot(d["fN"][sel], d["f1"][sel], color=fs.PAL["blue"], lw=3.0, alpha=0.5)
            ins.plot(d["N"][sel], d["e1"][sel], color=fs.PAL["red"], lw=1.0)
            ins.tick_params(labelsize=7)
            ins.yaxis.get_offset_text().set_fontsize(7)
    from matplotlib.ticker import MaxNLocator
    for i in (1, 2):
        for j in (0, 1):
            ax[i, j].yaxis.set_major_locator(MaxNLocator(nbins=6, prune="upper"))
    ax[0, 0].set_ylabel(r"$V(\phi_b)$  [$M_{\rm Pl}=100$]")
    ax[1, 0].set_ylabel(r"$\varepsilon_1$")
    ax[2, 0].set_ylabel(r"$\varepsilon_2$")
    ax[0, 0].legend(loc="upper right")
    fs.save(fig, os.path.join(out, "fig1_meanrolls"))
    plt.close(fig)

    # ---- residuals against Friedmann (the measure of "perfect agreement")
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.25)
    for j, case in enumerate(["sr", "usr"]):
        d = data[case]
        ax[j].semilogy(d["N"], np.abs(d["V"] / d["fV"] - 1) + 1e-18, color=fs.PAL["blue"],
                       label=r"$|V/V_F-1|$")
        ax[j].semilogy(d["N"], np.abs(d["e1"] / d["f1"] - 1) + 1e-18, color=fs.PAL["red"],
                       label=r"$|\varepsilon_1/\varepsilon_{1F}-1|$")
        ax[j].semilogy(d["N"], np.abs(d["e2"] - d["f2"]) + 1e-18, color=fs.PAL["green"],
                       label=r"$|\varepsilon_2-\varepsilon_{2F}|$")
        ax[j].set_xlabel(r"$\langle\mathcal{N}\rangle$")
        ax[j].set_title(["M64S against Friedmann", "M64U against Friedmann"][j], fontsize=10)
    ax[0].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig1_residuals"))
    plt.close(fig)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
