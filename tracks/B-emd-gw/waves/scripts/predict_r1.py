#!/usr/bin/env python3
"""Predictions of wave 3, round 1, written before the runs (JOURNAL.md 2026-11-20):

F2  flat wave k = 2 pi (1, 2, 0) (a direction with nonzero discrete divergence), elliptic,
    four periods, N = 16, 32, 48, 64: the two-variable symbol predictor of predict.py and
    the whole linearized Z4c system (wlib/z4c_symbol.py, kappa1 = 0.02 of the deck), which
    adds the non-TT part at +k, Gamma^i, Theta and Khat driven by the discrete divergence;
    the symbol errors of gw_diag's order-6 Weyl evaluation along k; the same numbers for
    (1, 1, 1) as the calibration of test F.
XS  test X with the expansion step limit dt_expansion = 0.01 (reference runs), 0.001 (new
    runs) and 1e-4 (the spatial part: the time step no longer matters), with the code's
    RK4()4[2S] on the background coupled to the mode (wlib/predict.py).

    python3 predict_r1.py     (through nrpic-run; $NRPIC_RUN_DIR/predictions_r1.{json,png,pdf},
                               copies into ../results and ../figs)
"""
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import PKG  # noqa: E402
from wlib import predict as pr, refs, z4c_symbol as zs  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

NS = (16, 32, 48, 64)
AMP, AMPX, PHX = 1e-6, 5e-7, 1.0
C1 = [(1, 3 / 4), (2, -3 / 20), (3, 1 / 60)]
C2 = (-49 / 18, [(1, 3 / 2), (2, -3 / 20), (3, 1 / 90)])


def weyl_fd_error(kvec, dx):
    """relative symbol errors of gw_diag's order-6 first and second derivatives along k
    (as scripts/predict.py)."""
    th = np.asarray(kvec, float) * dx
    s1 = np.array([2 * sum(c * np.sin(m * t) for m, c in C1) / dx for t in th])
    s2 = np.array([(C2[0] + 2 * sum(c * np.cos(m * t) for m, c in C2[1])) / dx ** 2 for t in th])
    kk = np.sum(np.asarray(kvec, float) ** 2)
    return float(np.sum(kvec * s1) / kk - 1.0), float(-np.sum(s2) / kk - 1.0)


def flat_case(kc):
    kvec = 2 * np.pi * np.array(kc, float)
    kn = float(np.linalg.norm(kvec))
    tlim = 4.0 * 2 * np.pi / kn
    dt_out = tlim / 32.0
    res, curves = {}, {}
    for N in NS:
        p2 = pr.predict_flat(kvec, (1, 1, 1), (N, N, N), tlim, dt_out)
        z = zs.evolve_linear_wave(kvec, (1, 1, 1), (N, N, N), tlim, dt_out, AMP, AMPX, PHX,
                                  kappa1=0.02)
        ex = refs.wave_measures(*refs.flat_amplitudes(z["t"], kn, AMP, AMPX, PHX), kn)
        ms = refs.wave_measures(z["P"], z["X"], z["Pd"], z["Xd"], kn)
        c = refs.compare(ms, ex)
        e1, e2 = weyl_fd_error(kvec, 1.0 / N)
        res[str(N)] = {
            "nsteps": int(p2["nsteps"]), "w_h/k-1": float(p2["w_h/k-1"]),
            "two_var": {"amp_end": float(np.abs(p2["ratio"][-1]) - 1),
                        "phase_end": float(np.angle(p2["ratio"][-1]))},
            "z4c": {"amp_p_end": float(c["amp_p"][-1]), "phase_p_end": float(c["phase_p"][-1]),
                    "amp_x_end": float(c["amp_x"][-1]), "phase_x_end": float(c["phase_x"][-1]),
                    "pol_amp_maxabs": float(np.max(np.abs(c["pol_amp"]))),
                    "pol_phase_maxabs": float(np.max(np.abs(c["pol_phase"]))),
                    "back_p_max": float(np.max(c["back_p"])),
                    "nonTT_mode_max": float(np.max(z["nonTT_mode"])),
                    "nonTT_mode_end": float(z["nonTT_mode"][-1]),
                    "Gamma_abs_max": float(np.max(np.linalg.norm(z["Gamma"], axis=1))),
                    "Gamma_abs_end": float(np.linalg.norm(z["Gamma"][-1])),
                    "Theta_abs_max": float(np.max(np.abs(z["Theta"]))),
                    "Khat_abs_max": float(np.max(np.abs(z["Khat"])))},
            "discrete_divergence_rel": z["div_rel"],
            "weyl_fd6_rel_d1": e1, "weyl_fd6_rel_d2": e2}
        curves[N] = (z["t"], c, z)
    for key in ("amp_p_end", "phase_p_end", "nonTT_mode_max", "Gamma_abs_max"):
        v = [res[str(N)]["z4c"][key] for N in NS]
        res.setdefault("orders", {})[key] = [float(np.log(abs(v[i] / v[i + 1])) / np.log(NS[i + 1] / NS[i]))
                                             for i in range(len(NS) - 1)]
    res["tlim"], res["dt_out"], res["kvec"] = tlim, dt_out, kvec.tolist()
    return res, curves


def x_case():
    kvec = 2 * np.pi / 4.0 * np.array([1.0, 1.0, 0.0])
    res = {}
    for N in NS:
        r = {}
        for de in (0.01, 0.001, 1e-4):
            p = pr.predict_flrw_coupled(kvec, (4.0, 4.0, 4.0), (N, N, N), 10.0, 0.25,
                                        dt_expansion=de, scheme="2s")
            r[str(de)] = {"nsteps": int(p["nsteps"]),
                          "amp_end": float(np.abs(p["ratio"][-1]) - 1),
                          "phase_end": float(np.angle(p["ratio"][-1])),
                          "a_rel_err_max": float(np.max(np.abs(p["a_rel_err"]))),
                          "alpha_rel_err_max": float(np.max(np.abs(p["alpha_rel_err"]))),
                          "t": p["t"].tolist(),
                          "amp": (np.abs(p["ratio"]) - 1).tolist(),
                          "phase": np.angle(p["ratio"]).tolist()}
        sp = r["0.0001"]
        for de in ("0.01", "0.001"):
            r[de]["temporal_amp_end"] = r[de]["amp_end"] - sp["amp_end"]
            r[de]["temporal_phase_end"] = r[de]["phase_end"] - sp["phase_end"]
        res[str(N)] = r
    for de in ("0.01", "0.001", "0.0001"):
        for key in ("amp_end", "phase_end"):
            v = [res[str(N)][de][key] for N in NS]
            res.setdefault("orders", {}).setdefault(de, {})[key] = [
                float(np.log(abs(v[i] / v[i + 1])) / np.log(NS[i + 1] / NS[i])) for i in range(len(NS) - 1)]
    return res


def main():
    out = os.environ["NRPIC_RUN_DIR"]
    f120, cur120 = flat_case((1, 2, 0))
    f111, _ = flat_case((1, 1, 1))
    xs = x_case()
    res = {"flat120": f120, "flat111": f111, "x_step": xs}
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.32)
    for i, N in enumerate(NS):
        t, c, z = cur120[N]
        col = fs.SERIES[i]
        axs[0, 0].semilogy(t[1:], np.abs(c["amp_p"][1:]), color=col, label=f"N = {N}")
        axs[0, 0].semilogy(t[1:], np.abs(c["phase_p"][1:]), color=col, ls="--")
        axs[0, 1].semilogy(t[1:], z["nonTT_mode"][1:], color=col, label=f"N = {N}")
        axs[0, 1].semilogy(t[1:], np.linalg.norm(z["Gamma"][1:], axis=1) / (AMP * np.linalg.norm(f120["kvec"])),
                           color=col, ls=":")
    axs[0, 0].set_title("F2: k = 2π(1,2,0), whole Z4c symbol")
    axs[0, 0].set_ylabel("|amplitude| (solid), |phase| (dashed)")
    axs[0, 0].set_xlabel("t", labelpad=-2)
    axs[0, 0].legend(loc="lower right", fontsize=7, ncol=2)
    axs[0, 1].set_title("non-TT part at +k (solid), |Γ|/(A|k|) (dotted)")
    axs[0, 1].set_xlabel("t", labelpad=-2)
    axs[0, 1].legend(loc="lower right", fontsize=7, ncol=2)
    for i, N in enumerate(NS):
        col = fs.SERIES[i]
        for de, ls in (("0.01", "-"), ("0.001", "--"), ("0.0001", ":")):
            r = xs[str(N)][de]
            lab = f"N = {N}" if de == "0.01" else None
            axs[1, 0].semilogy(r["t"][1:], np.abs(r["amp"][1:]) + 1e-18, color=col, ls=ls, label=lab)
            axs[1, 1].semilogy(r["t"][1:], np.abs(r["phase"][1:]) + 1e-18, color=col, ls=ls, label=lab)
    axs[1, 0].set_title("X: dt_expansion 0.01 (solid), 0.001 (dashed), 1e-4 (dotted)", fontsize=9)
    axs[1, 0].set_ylabel("|amplitude error| of W")
    axs[1, 1].set_ylabel("|phase error| of W (rad)")
    for ax in axs[1]:
        ax.set_xlabel("t (conformal)", labelpad=-2)
        ax.legend(loc="lower right", fontsize=7, ncol=2)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"predictions_r1.{ext}"))
    plt.close(fig)
    with open(os.path.join(out, "predictions_r1.json"), "w") as f:
        json.dump(res, f, indent=1)
    shutil.copy(os.path.join(out, "predictions_r1.json"), os.path.join(PKG, "results", "predictions_r1.json"))
    shutil.copy(os.path.join(out, "predictions_r1.png"), os.path.join(PKG, "figs", "predictions_r1.png"))
    short = {"flat120": {N: {k: v for k, v in f120[N].items()} for N in map(str, NS)},
             "flat120_orders": f120["orders"],
             "flat111_z4c": {N: f111[N]["z4c"] for N in map(str, NS)},
             "flat111_weyl": {N: (f111[N]["weyl_fd6_rel_d1"], f111[N]["weyl_fd6_rel_d2"]) for N in map(str, NS)},
             "x_step": {N: {de: {k: v for k, v in xs[N][de].items() if k not in ("t", "amp", "phase")}
                            for de in ("0.01", "0.001", "0.0001")} for N in map(str, NS)},
             "x_orders": xs["orders"]}
    print(json.dumps(short, indent=1))


if __name__ == "__main__":
    main()
