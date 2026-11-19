"""P5, P6: the Szekeres code with no dipole against the independent LTB package `expball`.

Data set 2 of expball (smoothed top-hat, delta_c = 1, R1 = 2.4, R2 = 6, R_b = 8, H = 1/16):
initial slice (M = m, k = -2E, rho, KL, KT), the areal radius R(tau) of 400 shells on 400
proper times up to the crunch of the core, turnaround, crunch and R = 2M times, and the
conformal map (isotropic radius, psi). Writes ltb_limit.json and fig_ltb_limit.

    python3 scripts/run_ltb_limit.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402


def main():
    rdir = common.run_dir("ltb_limit")
    ltb, szk = common.models()
    ball = common.expball_ball()
    from expball.exact import Shells
    out = {}
    r = np.linspace(0.02, 7.95, 400)
    c = ball.at(r)
    f = ltb.fields(ltb.t_i, r, 0.0)
    rel = lambda a, b: np.abs(a - b) / np.maximum(np.abs(b), 1e-300)   # noqa: E731
    slice_err = {"M": rel(f["M"], c["m"]), "k": np.abs(f["k"] + 2 * c["E"]),
                 "rho": rel(f["rho"], c["rho"]), "KL": rel(f["KL"], c["KL"]), "KT": rel(f["KT"], c["KT"])}
    out["initial_slice_max"] = {k: float(v.max()) for k, v in slice_err.items()}
    sh = Shells(ball, r)
    tc_core = float(sh.tau_c[0])
    tau = np.linspace(0.0, tc_core * (1 - 1e-3), 400)
    s = ltb.shell(ltb.t_i + tau[None, :], r[:, None])
    Re = sh.R(tau)
    dR = np.abs(s["R"] - Re) / Re
    out["R_tau_rel_max"] = float(dR.max())
    out["R_tau_rel_max_before_0.9_crunch"] = float(dR[:, tau < 0.9 * tc_core].max())
    out["tau_crunch_core"] = tc_core
    b = sh.bound & (ltb.radial(r)["lam_i"] > 1e-8)
    times = {}
    for name, mine, theirs in (("turnaround", ltb.turnaround_time(r[b]) - ltb.t_i, sh.tau_ta[b]),
                               ("crunch", ltb.crunch_time(r[b]) - ltb.t_i, sh.tau_c[b]),
                               ("R=2M", ltb.horizon_time(r[b]) - ltb.t_i, sh.tau_ah[b])):
        times[name] = float(np.max(np.abs(mine - theirs) / theirs))
    out["event_times_rel_max"] = times
    cm = ConformalMap(ltb)
    rr = np.linspace(0.01, 5.99, 400)
    T = cm.radial_table(rr)
    rb = ball.rbar_of_R(rr)
    out["rbar_rel_max"] = float(np.max(np.abs(T["rho"] - rb) / rb))
    x = np.random.default_rng(11).uniform(-4.6, 4.6, (20000, 3))
    fx = cm.fields(x)
    fe = ball.fields(np.linalg.norm(x, axis=1), ("u", "KL", "KT", "rho"))
    out["mesh_point_max"] = dict(psi=float(np.max(np.abs(fx["psi"] - 1 - fe["u"]))),
                                 rho_over_rhob=float(np.max(np.abs(fx["rho"] - fe["rho"])) / ltb.rho_b),
                                 KL_over_H=float(np.max(np.abs(fx["KL"] - fe["KL"])) / ltb.H),
                                 KT_over_H=float(np.max(np.abs(fx["KT"] - fe["KT"])) / ltb.H))
    out.update(run_id=common.run_id(), commit=common.git_commit(), model=ltb.summary())
    common.dump(os.path.join(rdir, "ltb_limit.json"), out)
    print(out)

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.17, top=0.9, wspace=0.38)
    ax = axs[0]
    for j, ri in enumerate((1.0, 2.6, 3.4, 4.2, 5.0, 7.0)):
        k = int(np.argmin(np.abs(r - ri)))
        col = fs.series_colors(6)[j]
        ax.plot(tau, Re[k], color=fs.PAL["blue"], lw=3.0, alpha=0.35)
        ax.plot(tau, s["R"][k], color=col, lw=1.2, label=f"$r = {r[k]:.1f}$")
    ax.set_xlabel(r"proper time $\tau$")
    ax.set_ylabel(r"areal radius $R$")
    ax.legend(ncol=2, fontsize=7, loc="upper left")
    ax.set_title("shells (thick: expball)")
    ax = axs[1]
    ax.semilogy(tau, np.maximum(dR.max(axis=0), 1e-17), color=fs.PAL["red"], label="max over shells")
    ax.semilogy(tau, np.maximum(np.median(dR, axis=0), 1e-17), color=fs.PAL["red"], ls="--", label="median")
    ax.axvline(tc_core, **fs.MASK_LINE)
    ax.set_xlabel(r"proper time $\tau$")
    ax.set_ylabel(r"$|R - R_{\rm expball}|/R$")
    ax.legend(loc="upper left")
    ax.set_title("evolution")
    ax = axs[2]
    for (name, v), col in zip(slice_err.items(), fs.SERIES):
        ax.semilogy(r, np.maximum(v, 1e-18), color=col, lw=1.0, label=name)
    ax.semilogy(rr, np.maximum(np.abs(T["rho"] - rb) / rb, 1e-18), color="k", lw=1.0,
                label=r"$\bar r$ (map)")
    ax.set_xlabel(r"label $r$ (areal radius at $t_i$)")
    ax.set_ylabel("relative difference")
    ax.legend(ncol=2, fontsize=7, loc="upper left")
    ax.set_ylim(1e-18, 1e-8)
    ax.set_title(r"initial slice, $\epsilon = 0$")
    common.save_fig(fig, "fig_ltb_limit", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
