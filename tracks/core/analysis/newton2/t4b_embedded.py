#!/usr/bin/env python3
"""Test T4b of work package newton2: the ellipsoid of Track B embedded in background
particles in a periodic expanding box (the track's N2), followed with the group history
of the patch, against the track's ODE (model A of baseline/scripts/ellipsoid.py: a
homogeneous ellipsoid of excess density in an Einstein-de Sitter background).

    t4b_embedded.py --run RUNDIR_OF_cases.py_t4b [--out DIR]

Semi-axes from the physical second moment about the centroid, R_i = (5 J_ii/M)^(1/2),
against the ODE at the cosmic time t_turn + T; time of the first minimum of the short
axis against the ODE crossing; quadrupole-formula energy from d3J/dT3 up to one t_k
before the crossing against the ODE (a measurement, no prediction attached).
Writes DIR/t4b_embedded.json and DIR/t4b_embedded.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402
from t3_groups import read_group  # noqa: E402


def tracefree(d):
    """Rows of six components (xx, xy, xz, yy, yz, zz) -> trace-free 3x3 tensors."""
    out = np.empty((len(d), 3, 3))
    idx = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
    for c, (i, j) in enumerate(idx):
        out[:, i, j] = out[:, j, i] = d[:, c]
    tr = np.trace(out, axis1=1, axis2=2)/3.0
    return out - tr[:, None, None]*np.eye(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--mg", default="", help="run directory of cases.py t4c (multigrid)")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    sys.path.insert(0, os.path.join(a.run, "refs", "B-emd-gw", "tracks", "B-emd-gw",
                                    "baseline", "scripts"))
    import ellipsoid as el
    setup = json.load(open(os.path.join(a.run, "ic", "embedded_setup.json")))
    icm = json.load(open(os.path.join(a.run, "ic", "embedded.json")))
    lam = np.array(setup["lam"])
    t0 = setup["t_turn"]
    res = {"setup": {k: setup[k] for k in ("t_turn", "R0", "L", "n", "rho_b", "mass")},
           "particles": {k: icm.get(k) for k in ("nball", "nbackground", "r_vol", "r_mom",
                                                 "background_mass")}}
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.16, top=0.95, wspace=0.36)
    cols = {"emb_fft": fs.PAL["red"], "emb_mg": fs.PAL["yellow"]}
    labs = {"emb_fft": "Fourier", "emb_mg": "multigrid"}
    ode = {}
    for model in ("A", "C"):
        run = el.integrate(lam, model, t0 + 17.0)
        ode[model] = run
        res["ode_%s_crossings" % model] = run["crossings"][:3]
    tx_ode = ode["A"]["crossings"][0][0]
    dirs = {"emb_fft": os.path.join(a.run, "emb_fft")}
    if a.mg:
        dirs["emb_mg"] = os.path.join(a.mg, "emb_mg")
    for name, cdir in dirs.items():
        g = read_group(os.path.join(cdir, "newton.newton.g1.hst"))
        h = nw.read_newton_hst(os.path.join(cdir, "newton.newton.hst"))
        t = t0 + g["T"]
        M = g["mass"][0]
        R = np.sqrt(5.0*g["J"][:, [0, 3, 5]]/M)
        # first minimum of the short axis: parabola through the three lowest records
        i = int(np.argmin(R[:, 0]))
        if 0 < i < len(t) - 1:
            p = np.polyfit(t[i-1:i+2], R[i-1:i+2, 0], 2)
            t_min = float(-p[1]/(2.0*p[0]))
        else:
            t_min = float(t[i])
        w = t <= tx_ode - 1.0
        s = el.sample(ode["A"], t[w])
        sc = el.sample(ode["C"], t[w])
        dev = np.abs(R[w] - np.abs(s["R"]))/el.RL
        # quadrupole-formula energy from the difference-quotient column up to t_x - 1
        q3 = tracefree(g["d3J"])
        P = np.einsum("nij,nij->n", q3, q3)/5.0
        tq = t0 + g["T_d3J"]
        ok = (g["ncycle"] > 0) & (tq <= tx_ode - 1.0)
        E = float((getattr(np, "trapezoid", None) or np.trapz)(P[ok], tq[ok]))
        E_ode = float(np.interp(tx_ode - 1.0, s["t"], s["E"]))
        out = dict(records=int(len(t)), mass=float(M), number=int(g["number"][0]),
                   R_start=R[0].tolist(), R_start_ode=np.abs(s["R"][0]).tolist(),
                   t_min_short_axis=t_min, t_cross_ode=float(tx_ode),
                   t_min_rel=float(t_min/tx_ode - 1.0),
                   t_min_rel_since_turn=float((t_min - t0)/(tx_ode - t0) - 1.0),
                   R_min_short_axis=float(R[i, 0]),
                   axes_maxdev_over_RL=dev.max(axis=0).tolist(),
                   axes_maxdev_model_C_over_RL=(np.abs(R[w] - np.abs(sc["R"]))/el.RL
                                                ).max(axis=0).tolist(),
                   centroid_shift_max=float(np.abs(g["X"] - g["X"][0]).max()),
                   centroid_shift_over_dx=float(np.abs(g["X"] - g["X"][0]).max()
                                                / (setup["L"]/setup["n"])),
                   E_to_tx_minus_1=E, E_ode_to_tx_minus_1=E_ode,
                   E_rel=float(E/E_ode - 1.0),
                   layzer_irvine=float(np.max(np.abs(h["C"] - h["C"][0]))
                                       / np.max(np.abs(h["a"]*h["W"]))),
                   last_step=float(h["dt"][-1]), d3J_last=g["d3J"][-1].tolist(),
                   d3J_before_last=g["d3J"][-2].tolist(),
                   mg_cycles_mean=float(np.mean(h["mg_cycles"][1:])))
        res[name] = out
        ax = axs[0]
        for k in range(3):
            ax.plot(t, R[:, k], color=cols[name], ls=("-", "--", ":")[k],
                    label=labs[name] if k == 0 else None)
        ax = axs[1]
        for k in range(3):
            ax.plot(t[w], (R[w, k] - np.abs(s["R"][:, k]))/el.RL, color=cols[name],
                    ls=("-", "--", ":")[k])
        ax = axs[2]
        ax.semilogy(tq[g["ncycle"] > 0], np.maximum(P[g["ncycle"] > 0], 1e-12),
                    color=cols[name], lw=1.0)
    tg = np.linspace(t0, t0 + 16.5, 600)
    sg = el.sample(ode["A"], tg)
    sgc = el.sample(ode["C"], tg)
    for k in range(3):
        axs[0].plot(tg, np.abs(sg["R"][:, k]), color=fs.PAL["blue"], ls=("-", "--", ":")[k],
                    lw=1.0, label="ODE, embedded (model A)" if k == 0 else None)
    axs[0].plot(tg, np.abs(sgc["R"][:, 0]), color="0.5", lw=1.0, alpha=0.6,
                label="ODE, static (model C), short axis")
    axs[2].semilogy(tg, np.maximum(sg["P"], 1e-12), color=fs.PAL["blue"], ls="--", lw=1.0)
    if "emb_mg" in res:
        res["solvers"] = dict(
            t_min_rel_diff=res["emb_fft"]["t_min_short_axis"]/res["emb_mg"]["t_min_short_axis"]
            - 1.0)
    axs[0].set_xlabel(r"$t/t_k$", labelpad=-1)
    axs[0].set_ylabel(r"semi-axes $(5J_{ii}/M)^{1/2}$")
    axs[0].legend(loc="lower left", fontsize=7)
    axs[1].axhline(0.0, color="k", lw=1.0, ls="--")
    axs[1].set_xlabel(r"$t/t_k$", labelpad=-1)
    axs[1].set_ylabel(r"(run $-$ ODE)$/R_L$")
    axs[2].set_xlabel(r"$t/t_k$", labelpad=-1)
    axs[2].set_ylabel(r"$P = \dddot Q_{ij}\dddot Q_{ij}/5$")
    axs[2].set_ylim(1e-9, 1e-2)
    fs.save(fig, os.path.join(a.out, "t4b_embedded"))
    with open(os.path.join(a.out, "t4b_embedded.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
