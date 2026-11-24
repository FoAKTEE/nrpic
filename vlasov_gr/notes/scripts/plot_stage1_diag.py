"""Generate Stage 1 diagnostic 4-panel figure for the 1D Python GR-LBV reference solver."""

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "python"))

from nrpic import vlasov_gr as vg


def _setup_style():
    plt.rcParams.update({
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "legend.fontsize": 8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "axes.linewidth": 0.9,
        "figure.dpi": 200,
    })


def main():
    _setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8), constrained_layout=True)

    # (a) Relativistic boosted two-stream invariants
    ax = axes[0, 0]
    N, L = 32, 1.0
    x = (np.arange(N) + 0.5) * (L / N)
    gam = 1.0 / math.sqrt(1.0 - 0.25)
    Wb = math.sqrt(1.0 + 1.2 * 1.2)
    D = np.full((N, 2), 0.5)
    u = np.zeros((N, 2, 3))
    u[:, 0, 0] = gam * (1.2 + 0.5 * Wb)
    u[:, 1, 0] = gam * (-1.2 + 0.5 * Wb)
    Sig = np.broadcast_to(1e-14 * np.eye(3), (N, 2, 3, 3)).copy()
    st = vg.init_mfm_1d(x, D, u, Sig, L)
    M0, P0, E0 = vg.total_invariants_1d(st)
    ts, dM, dP, dE = [], [], [], []
    dt = 0.005
    for step in range(40):
        vg.step_1d_mfm(st, dt)
        M1, P1, E1 = vg.total_invariants_1d(st)
        ts.append((step + 1) * dt)
        dM.append(max(abs(M1 - M0) / M0, 1e-16))
        dP.append(max(float(np.linalg.norm(P1 - P0) / np.linalg.norm(P0)), 1e-16))
        dE.append(max(abs(E1 - E0) / E0, 1e-16))
    ax.semilogy(ts, dM, label=r"$|\Delta M| / M_0$", lw=1.6)
    ax.semilogy(ts, dP, "--", label=r"$|\Delta P_x| / |P_0|$", lw=1.5)
    ax.semilogy(ts, dE, ":", label=r"$|\Delta E| / E_0$", lw=1.8)
    ax.set_ylim(1e-17, 1e-10)
    ax.set_xlabel(r"Time $t$")
    ax.set_ylabel("Relative conservation error")
    ax.set_title(r"(a) Boosted two-stream ($\beta_0 = 0.5$, $u_0 = \pm 1.2$)")
    ax.legend(frameon=False, loc="best")

    # (b) 2nd-order relativistic density-wave convergence
    ax = axes[0, 1]
    Ns = np.array([16, 32, 64])
    errs = []
    u_w = 1.0
    v_w = u_w / math.sqrt(1.0 + u_w * u_w)
    t_end = 0.25
    for Nx in Ns:
        xx = (np.arange(Nx) + 0.5) * (L / Nx)
        mod = 1.0 + 0.2 * np.cos(2.0 * math.pi * xx / L)
        DD = np.stack([0.5 * mod, 0.5 * mod], axis=-1)
        uu = np.zeros((Nx, 2, 3)); uu[:, 0, 0] = u_w; uu[:, 1, 0] = -u_w
        SS = np.broadcast_to(1e-14 * np.eye(3), (Nx, 2, 3, 3)).copy()
        s = vg.init_mfm_1d(xx, DD, uu, SS, L)
        nsteps = 2 * int(Nx)
        for _ in range(nsteps):
            vg.step_1d_mfm(s, t_end / nsteps)
        exact_p = 0.5 * (1.0 + 0.2 * np.cos(2.0 * math.pi * (s.x - v_w * t_end) / L))
        errs.append(float(np.mean(np.abs(s.D[:, 0] - exact_p))))
    errs = np.array(errs)
    ax.loglog(Ns, errs, "o-", lw=1.7, label="GR-LBV Top-Hat")
    ref_2 = errs[0] * (Ns[0] / Ns) ** 2
    ax.loglog(Ns, ref_2, "k--", lw=1.1, label=r"$\propto N^{-2}$")
    ax.set_xlabel(r"Element count $N_x$")
    ax.set_ylabel(r"$L_1$ density error")
    ax.set_title(r"(b) Relativistic density-wave convergence ($u_x = \pm 1$)")
    ax.legend(frameon=False, loc="best")

    # (c) Empty-basis cold stream injection (C^eb vs v_only)
    ax = axes[1, 0]
    N_e, Nb = 48, 4
    xe = (np.arange(N_e) + 0.5) * (L / N_e)
    pi = 0.5 * np.exp(-((xe - 0.5) / 0.06) ** 2)
    inj = pi > 1e-6
    De = np.zeros((N_e, Nb)); ue = np.zeros((N_e, Nb, 3))
    ue[:, 0, 0] = 1.0; ue[:, 1, 0] = 0.0; ue[:, 2, 0] = -1.0; ue[:, 3, 0] = -2.0
    De[:, 0] = 0.49; De[:, 1] = 0.02; De[:, 2] = 0.49; De[:, 3] = 1e-8
    ue[inj, 3, 0] = 3.0; De[inj, 3] = pi[inj]
    De[inj, :3] *= ((1.0 - pi[inj]) / (De[inj, 0] + De[inj, 1] + De[inj, 2]))[:, None]
    Se = np.broadcast_to(1e-8 * np.eye(3), (N_e, Nb, 3, 3)).copy()
    st_eb = vg.init_mfm_1d(xe, De, ue, Se, L)
    st_vo = vg.init_mfm_1d(xe, De, ue, Se, L)
    t_c = 0.24
    for _ in range(60):
        vg.step_1d_mfm(st_eb, t_c / 60, pairing_mode="eb")
        vg.step_1d_mfm(st_vo, t_c / 60, pairing_mode="v_only")
    v_fast = 3.0 / math.sqrt(1.0 + 9.0)
    # Compare total fast-beam mass propagated past x = 0.65 into untouched slots
    D_fast_eb = np.where(st_eb.u_bar[:, :, 0] > 2.2, st_eb.D, 0.0).sum(axis=1)
    D_fast_vo = np.where(st_vo.u_bar[:, :, 0] > 2.2, st_vo.D, 0.0).sum(axis=1)
    x_shift = (xe + v_fast * t_c) % L
    idx_s = np.argsort(x_shift)
    ax.plot(x_shift[idx_s], np.where(inj, pi, 0.0)[idx_s], "k--", lw=1.2, label="Exact shifted pulse")
    ax.plot(st_eb.x, D_fast_eb, "o-", ms=3, lw=1.4, label=r"$C^{\rm eb}$ empty-basis")
    ax.plot(st_vo.x, D_fast_vo, "s:", ms=3, lw=1.4, label=r"Velocity-only")
    ax.set_xlim(0.45, 0.95)
    ax.set_ylim(-0.02, 0.56)
    ax.set_xlabel(r"Position $x$")
    ax.set_ylabel(r"Fast-stream density $D(u_x > 2.2)$")
    ax.set_title(r"(c) Empty-basis fast beam injection ($u_x = +3$, $t = 0.24$)")
    ax.legend(frameon=False, loc="upper left")

    # (d) Colliding streams: collisionless vs collisional Taub double shock
    ax = axes[1, 1]
    Nc = 64
    xc = (np.arange(Nc) + 0.5) * (L / Nc)
    left = xc < 0.5
    Dc = np.full((Nc, 2), 1e-8); uc = np.zeros((Nc, 2, 3))
    uc[:, 0, 0] = 1.0; uc[:, 1, 0] = -1.0
    Dc[left, 0] = 1.0 - 1e-8; Dc[~left, 1] = 1.0 - 1e-8
    Sc = np.broadcast_to(1e-10 * np.eye(3), (Nc, 2, 3, 3)).copy()
    st_cl = vg.init_mfm_1d(xc, Dc, uc, Sc, L)
    st_hy = vg.init_mfm_1d(xc, Dc, uc, Sc, L)
    t_end_c = 0.15
    for st_cur, sig_val in ((st_cl, 0.0), (st_hy, 500.0)):
        t_cur = 0.0
        while t_cur < t_end_c - 1e-14:
            dt_step = min(t_end_c - t_cur, 0.0025, 0.25 * float(np.min(st_cur.V)))
            vg.step_1d_mfm(st_cur, dt_step, sigma_over_mu=sig_val)
            t_cur += dt_step
    ex = vg.exact_taub_double_shock(u0=1.0, rho0=1.0)
    Vs = ex["shock_speed"]
    x_grid = np.linspace(0.25, 0.75, 400)
    D_ex_hy = np.where(np.abs(x_grid - 0.5) < Vs * t_end_c, ex["D2"], 1.0)
    D_ex_cl = np.where(np.abs(x_grid - 0.5) < ex["v0"] * t_end_c, 2.0, 1.0)
    ax.plot(x_grid, D_ex_hy, "k-", lw=1.1, label=r"Exact Taub/Synge ($D_2=4.14$)")
    ax.plot(x_grid, D_ex_cl, "k--", lw=1.0, label="Exact collisionless")
    ax.plot(st_hy.x, np.sum(st_hy.D, axis=1), "o-", ms=2.8, lw=1.3, label=r"$\sigma/\mu = 500$ (hydro)")
    ax.plot(st_cl.x, np.sum(st_cl.D, axis=1), "s-", ms=2.5, lw=1.2, label=r"$\sigma/\mu = 0$ (Vlasov)")
    ax.set_xlim(0.25, 0.75)
    ax.set_ylim(0.75, 4.9)
    ax.set_xlabel(r"Position $x$")
    ax.set_ylabel(r"Total coordinate density $D$")
    ax.set_title(r"(d) Colliding cold streams ($u_0 = \pm 1$, $t = 0.15$)")
    ax.legend(frameon=False, loc="upper right", fontsize=7.5)

    out_dir = ROOT / "vlasov_gr" / "notes" / "figs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "diag_stage1_python_1d.png"
    fig.savefig(out_png)
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
