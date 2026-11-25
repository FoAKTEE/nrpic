#!/usr/bin/env python3
"""Run single-particle Kerr black hole integrations in AthenaK and visualize orbits & invariants.

Executes real AthenaK runs (build_omp_iter4/src/athena, OMP_NUM_THREADS=4) under
`$SCRATCH/runs/kerr_single_particle/`:
  1. Strong-field 3D inclined zoom-whirl / precessing rosette (a = 0.95 M, t = 450 M)
  2. Ergosphere-grazing e = 0.99 passage ks_passage (a = 0.90 M, t = 230 M): GL4 vs Midpoint vs DOP853
  3. 3D inclined precessing mesh orbit bl_inclined (a = 0.90 M, t = 600 M, ng=4): Quintic vs Hermite

Saves reduced arrays to `vlasov_gr/paper/data/physics_kerr_single_particle.npz` and
renders `vlasov_gr/paper/figures/fig_physics_kerr_single_particle.{pdf,png}`.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.collections import LineCollection

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import kerr, geodesic  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
REPO = os.path.dirname(os.path.dirname(PAPER_DIR))
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
BIN_OMP = f"{SCRATCH}/build_omp_iter4/src/athena"
RUNROOT = f"{SCRATCH}/runs/kerr_single_particle"
IC_JSON = os.path.join(REPO, "problems", "kerr", "ref", "initial_conditions.json")
TPL_GEO = os.path.join(REPO, "problems", "kerr", "geodesic.athinput")
TPL_MESH = os.path.join(REPO, "problems", "kerr", "geodesic_mesh.athinput")
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_kerr_single_particle.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_kerr_single_particle")


def set_param(txt, sec, key, val):
    lines = txt.splitlines()
    out = []
    cur = None
    replaced = False
    pat = re.compile(rf"^\s*{re.escape(key)}\s*=")
    for ln in lines:
        s = ln.strip()
        if s.startswith("<") and s.endswith(">"):
            if cur == sec and not replaced:
                out.append(f"{key} = {val}")
                replaced = True
            cur = s[1:-1]
            out.append(ln)
            continue
        if cur == sec and pat.match(ln):
            out.append(f"{key} = {val}")
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        if cur == sec:
            out.append(f"{key} = {val}")
        else:
            out.append(f"<{sec}>")
            out.append(f"{key} = {val}")
    return "\n".join(out) + "\n"


def read_traj_bin(path):
    arr = np.fromfile(path, dtype=np.float64).reshape(-1, 8)
    # columns: [t, tag, x, y, z, u_x, u_y, u_z]
    m0 = arr[:, 1] == 0.0
    arr = arr[m0]
    return arr[:, 0], arr[:, 2:5], arr[:, 5:8]


def run_athena_omp(name, ath_txt):
    rdir = os.path.join(RUNROOT, name)
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir, exist_ok=True)
    ath_path = os.path.join(RUNROOT, f"{name}.athinput")
    with open(ath_path, "w") as f:
        f.write(ath_txt)
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "4"
    env["OMP_PROC_BIND"] = "spread"
    env["OMP_PLACES"] = "cores"
    log_path = os.path.join(rdir, f"{name}.stdout.log")
    with open(log_path, "w") as flog:
        rc = subprocess.run([BIN_OMP, "-i", ath_path], cwd=rdir, env=env,
                            stdout=flog, stderr=subprocess.STDOUT, check=False).returncode
    if rc != 0:
        raise RuntimeError(f"AthenaK run {name} failed (rc={rc}), see {log_path}")
    t, x, u = read_traj_bin(os.path.join(rdir, f"{name}.traj.bin"))
    return t, x, u


def build_and_run():
    if os.path.exists(DATA_OUT) and os.environ.get("RERUN_KERR", "0") != "1":
        print(f"Loading cached {DATA_OUT} (set RERUN_KERR=1 to recompute)", flush=True)
        return dict(np.load(DATA_OUT))
    os.makedirs(RUNROOT, exist_ok=True)
    with open(IC_JSON) as f:
        ic = json.load(f)
    tpl_geo = open(TPL_GEO).read()
    tpl_mesh = open(TPL_MESH).read()

    # 1. Strong-field 3D inclined precessing rosette (a = 0.95 M)
    a3d, M = 0.95, 1.0
    ra = 9.5
    Lz3d, uth3d = 1.95, 1.70
    x_bl_3d = np.array([ra, 0.5 * math.pi, 0.0])
    u_bl_3d = np.array([0.0, uth3d, Lz3d])
    _, x0_3d, u0_3d = kerr.convert_state(0.0, x_bl_3d, u_bl_3d, "bl", "cks", a=a3d, M=M)
    E0_3d, L0_3d, Q0_3d = kerr.invariants("cks", x0_3d, u0_3d, a=a3d, M=M)

    def make_geo_cfg(base, x0, u0, a, tlim, dt, pusher, vpush=None):
        txt = set_param(tpl_geo, "job", "basename", base)
        txt = set_param(txt, "time", "tlim", f"{tlim}")
        txt = set_param(txt, "particles", "metric", "kerr_schild")
        txt = set_param(txt, "particles", "bh_mass", "1.0")
        txt = set_param(txt, "particles", "bh_spin", f"{a}")
        txt = set_param(txt, "particles", "dt", f"{dt}")
        txt = set_param(txt, "particles", "tolerance", "2.0e-14")
        txt = set_param(txt, "particles", "max_iterations", "200")
        txt = set_param(txt, "particles", "pusher", pusher)
        if vpush is not None:
            txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
            txt = set_param(txt, "particles", "vlasov_pusher", vpush)
        for idx, k in enumerate(("p0_x1", "p0_x2", "p0_x3")):
            txt = set_param(txt, "particles", k, f"{x0[idx]:.17g}")
        for idx, k in enumerate(("p0_u1", "p0_u2", "p0_u3")):
            txt = set_param(txt, "particles", k, f"{u0[idx]:.17g}")
        return txt

    t_zw, x_zw, u_zw = run_athena_omp(
        "zw_a095_gl4", make_geo_cfg("zw_a095_gl4", x0_3d, u0_3d, a3d, 450.0, 0.02, "vlasov_hybrid", "gl4")
    )
    ih_zw = geodesic.invariant_history("cks", x_zw, u_zw, a=a3d, M=M, ref=(E0_3d, L0_3d, Q0_3d))

    # 2. Ergosphere-grazing e = 0.99 passage (a = 0.90 M, t = 230 M, dt = 0.02 M)
    kp = ic["orbits"]["ks_passage"]
    x0_kp = np.array(kp["initial_state"]["cks"]["x"], dtype=float)
    u0_kp = np.array(kp["initial_state"]["cks"]["u"], dtype=float)
    E0_kp = kp["invariants"]["E"]
    L0_kp = kp["invariants"]["Lz"]
    Q0_kp = kp["invariants"]["Q"]

    t_kp_gl4, x_kp_gl4, u_kp_gl4 = run_athena_omp(
        "kp_gl4", make_geo_cfg("kp_gl4", x0_kp, u0_kp, 0.9, 230.0, 0.02, "vlasov_hybrid", "gl4")
    )
    t_kp_mid, x_kp_mid, u_kp_mid = run_athena_omp(
        "kp_mid", make_geo_cfg("kp_mid", x0_kp, u0_kp, 0.9, 230.0, 0.02, "midpoint")
    )
    tr_kp_dop = geodesic.integrate(
        "cks", x0_kp, u0_kp, 230.0, t0=0.0, dt_out=0.02, rtol=1.0e-13, atol=1.0e-13, a=0.9, M=1.0
    )
    ih_kp_gl4 = geodesic.invariant_history("cks", x_kp_gl4, u_kp_gl4, a=0.9, M=1.0, ref=(E0_kp, L0_kp, Q0_kp))
    ih_kp_mid = geodesic.invariant_history("cks", x_kp_mid, u_kp_mid, a=0.9, M=1.0, ref=(E0_kp, L0_kp, Q0_kp))
    err_end_gl4 = float(np.linalg.norm(x_kp_gl4[-1] - tr_kp_dop.x[-1]))
    err_end_mid = float(np.linalg.norm(x_kp_mid[-1] - tr_kp_dop.x[-1]))

    # 3. 3D inclined precessing mesh orbit (bl_inclined, a = 0.90 M, t = 600 M, dt = 0.05 M, ng = 4)
    def run_mesh_orbit(base, interp_kind):
        txt = set_param(tpl_mesh, "job", "basename", base)
        txt = set_param(txt, "mesh", "nghost", "4")
        txt = set_param(txt, "time", "tlim", "600.0")
        txt = set_param(txt, "particles", "dt", "0.05")
        txt = set_param(txt, "particles", "hist_dcycle", "200")
        txt = set_param(txt, "particles", "traj_dcycle", "1")
        txt = set_param(txt, "particles", "pusher", "vlasov_hybrid")
        txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
        txt = set_param(txt, "particles", "vlasov_pusher", "gl4")
        txt = set_param(txt, "particles", "interp", interp_kind)
        return run_athena_omp(base, txt)

    bi = ic["orbits"]["bl_inclined"]
    E0_bi, L0_bi, Q0_bi = bi["invariants"]["E"], bi["invariants"]["Lz"], bi["invariants"]["Q"]
    t_bi_q, x_bi_q, u_bi_q = run_mesh_orbit("bi_mesh_quintic", "quintic")
    t_bi_h, x_bi_h, u_bi_h = run_mesh_orbit("bi_mesh_hermite", "hermite")
    ih_bi_q = geodesic.invariant_history("cks", x_bi_q, u_bi_q, a=0.9, M=1.0, ref=(E0_bi, L0_bi, Q0_bi))
    ih_bi_h = geodesic.invariant_history("cks", x_bi_h, u_bi_h, a=0.9, M=1.0, ref=(E0_bi, L0_bi, Q0_bi))

    # Print verified summary
    print("=== Single-Particle Kerr Integration Summary ===", flush=True)
    print(f"1) 3D Zoom-Whirl (a=0.95M, GL4, dt=0.02, t=450M): E0={E0_3d:.5f} Lz={L0_3d:.3f} Q={Q0_3d:.3f} "
          f"| max|dE/E|={ih_zw['max_abs_dE']:.2e} max|dL/L|={ih_zw['max_abs_dLz']:.2e} max|dQ/Q|={ih_zw['max_abs_dQ']:.2e}", flush=True)
    print(f"2) e=0.99 Passage (a=0.90M, dt=0.02, t=230M): "
          f"GL4 max|dE/E|={ih_kp_gl4['max_abs_dE']:.2e} max|dQ/Q|={ih_kp_gl4['max_abs_dQ']:.2e} dx_end={err_end_gl4:.2e}M | "
          f"Mid max|dE/E|={ih_kp_mid['max_abs_dE']:.2e} max|dQ/Q|={ih_kp_mid['max_abs_dQ']:.2e} dx_end={err_end_mid:.2e}M", flush=True)
    print(f"3) Mesh Inclined (a=0.90M, dx=0.25M, dt=0.05, t=600M): "
          f"Quintic max|dE/E|={ih_bi_q['max_abs_dE']:.2e} max|dQ/Q|={ih_bi_q['max_abs_dQ']:.2e} | "
          f"Hermite max|dE/E|={ih_bi_h['max_abs_dE']:.2e} max|dQ/Q|={ih_bi_h['max_abs_dQ']:.2e}", flush=True)

    # Downsample for compact npz storage
    def ds(arr, nmax=3000):
        st = max(1, len(arr) // nmax)
        s = arr[::st]
        return s

    out = dict(
        a3d=np.float64(a3d), E0_3d=np.float64(E0_3d), L0_3d=np.float64(L0_3d), Q0_3d=np.float64(Q0_3d),
        t_zw=ds(t_zw, 4500), x_zw=ds(x_zw, 4500),
        zw_max_dE=np.float64(ih_zw["max_abs_dE"]), zw_max_dQ=np.float64(ih_zw["max_abs_dQ"]),
        t_kp=ds(t_kp_gl4, 2500), x_kp_gl4=ds(x_kp_gl4, 2500), x_kp_mid=ds(x_kp_mid, 2500),
        x_kp_dop=ds(tr_kp_dop.x, 2500),
        kp_gl4_dE=ds(np.abs(ih_kp_gl4["dE"]), 2500), kp_gl4_dQ=ds(np.abs(ih_kp_gl4["dQ"]), 2500),
        kp_mid_dE=ds(np.abs(ih_kp_mid["dE"]), 2500), kp_mid_dQ=ds(np.abs(ih_kp_mid["dQ"]), 2500),
        kp_gl4_end_err=np.float64(err_end_gl4), kp_mid_end_err=np.float64(err_end_mid),
        kp_gl4_max_dE=np.float64(ih_kp_gl4["max_abs_dE"]), kp_mid_max_dE=np.float64(ih_kp_mid["max_abs_dE"]),
        t_bi=ds(t_bi_q, 2400), x_bi_q=ds(x_bi_q, 2400),
        bi_q_dE=ds(np.abs(ih_bi_q["dE"]), 2400), bi_h_dE=ds(np.abs(ih_bi_h["dE"]), 2400),
        bi_q_dQ=ds(np.abs(ih_bi_q["dQ"]), 2400), bi_h_dQ=ds(np.abs(ih_bi_h["dQ"]), 2400),
        bi_q_max_dE=np.float64(ih_bi_q["max_abs_dE"]), bi_h_max_dE=np.float64(ih_bi_h["max_abs_dE"]),
    )
    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def cks_surface(r_func, a, nth=48, nph=64):
    th = np.linspace(0.0, np.pi, nth)
    ph = np.linspace(0.0, 2.0 * np.pi, nph)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    rr = r_func(TH)
    X = np.sqrt(rr ** 2 + a ** 2) * np.sin(TH) * np.cos(PH)
    Y = np.sqrt(rr ** 2 + a ** 2) * np.sin(TH) * np.sin(PH)
    Z = rr * np.cos(TH)
    return X, Y, Z


def main():
    cz.use_style()
    D = build_and_run()

    fig = plt.figure(figsize=(8.6, 6.8))
    gs = fig.add_gridspec(2, 2, left=0.055, right=0.975, bottom=0.075, top=0.965,
                          wspace=0.25, hspace=0.28)

    # ------------------------------------------------------------------
    # Top-Left (3D): Spinning Kerr a=0.95M inclined zoom-whirl orbit
    # ------------------------------------------------------------------
    ax3d = fig.add_subplot(gs[0, 0], projection="3d")
    a3d = float(D["a3d"])
    rp3d = 1.0 + math.sqrt(1.0 - a3d * a3d)
    Xh, Yh, Zh = cks_surface(lambda th: np.full_like(th, rp3d), a3d, nth=28, nph=40)
    Xe, Ye, Ze = cks_surface(lambda th: 1.0 + np.sqrt(np.maximum(1.0 - a3d * a3d * np.cos(th) ** 2, 0.0)),
                             a3d, nth=28, nph=40)
    ax3d.plot_surface(Xh, Yh, Zh, color="0.10", alpha=0.96, shade=True, linewidth=0)
    ax3d.plot_surface(Xe, Ye, Ze, color=cz.PAL["orange"], alpha=0.16, linewidth=0.2,
                      edgecolors=(0.85, 0.45, 0.0, 0.15))

    xzw = D["x_zw"]
    tzw = D["t_zw"]
    pts3d = xzw.reshape(-1, 1, 3)
    segs3d = np.concatenate([pts3d[:-1], pts3d[1:]], axis=1)
    lc3d = Line3DCollection(segs3d, cmap="viridis", norm=plt.Normalize(0.0, float(tzw[-1])),
                            linewidth=1.15, alpha=0.92)
    lc3d.set_array(tzw[:-1])
    ax3d.add_collection3d(lc3d)
    ax3d.scatter([xzw[0, 0]], [xzw[0, 1]], [xzw[0, 2]], color=cz.PAL["green"], s=18, edgecolor="k", linewidth=0.5, zorder=10)
    ax3d.scatter([xzw[-1, 0]], [xzw[-1, 1]], [xzw[-1, 2]], color=cz.PAL["red"], s=20, marker="s", edgecolor="k", linewidth=0.5, zorder=10)
    ax3d.set_xlim(-9.6, 9.6)
    ax3d.set_ylim(-9.6, 9.6)
    ax3d.set_zlim(-6.8, 6.8)
    ax3d.set_xticks([-8, -4, 0, 4, 8])
    ax3d.set_yticks([-8, -4, 0, 4, 8])
    ax3d.set_zticks([-6, -3, 0, 3, 6])
    ax3d.set_box_aspect((1.0, 1.0, 0.72))
    ax3d.view_init(elev=22, azim=38)
    ax3d.set_xlabel(r"$x\,[M]$", labelpad=2, fontsize=8.0)
    ax3d.set_ylabel(r"$y\,[M]$", labelpad=2, fontsize=8.0)
    ax3d.set_zlabel(r"$z\,[M]$", labelpad=1, fontsize=8.0)
    ax3d.tick_params(labelsize=6.8, pad=0)
    ax3d.text2D(0.02, 0.99,
                r"Inclined rosette ($a=0.95M$, $\mathrm{GL4}$, $t=450M$)" "\n"
                rf"$E={float(D['E0_3d']):.4f},\;L_z={float(D['L0_3d']):.2f},\;Q={float(D['Q0_3d']):.2f}$",
                transform=ax3d.transAxes, ha="left", va="top", fontsize=6.5)

    # ------------------------------------------------------------------
    # Top-Right: Equatorial (x, y) zoom on e=0.99 ks_passage pericenter
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    a90 = 0.9
    rp90 = 1.0 + math.sqrt(1.0 - a90 * a90)
    r_hor_eq = math.sqrt(rp90 * rp90 + a90 * a90)
    r_erg_eq = math.sqrt(4.0 + a90 * a90)
    ph = np.linspace(0.0, 2.0 * np.pi, 240)
    ax.fill(r_hor_eq * np.cos(ph), r_hor_eq * np.sin(ph), color="0.12", zorder=5, label=r"Horizon $r_+$")
    ax.plot(r_erg_eq * np.cos(ph), r_erg_eq * np.sin(ph), color=cz.PAL["orange"], ls="--", lw=1.1, zorder=4,
            label=r"Ergosphere $r_{\rm ergo}$")

    xgl4, xmid, xdop = D["x_kp_gl4"], D["x_kp_mid"], D["x_kp_dop"]
    ax.plot(xdop[:, 0], xdop[:, 1], color="0.45", lw=2.3, alpha=0.55, zorder=2, label=r"$\mathrm{DOP853}$ exact")
    ax.plot(xgl4[:, 0], xgl4[:, 1], color=cz.PAL["red"], lw=1.35, ls="-", zorder=4, label=r"$\mathrm{GL4}$ ($\Delta t=0.02M$)")
    ax.plot(xmid[:, 0], xmid[:, 1], color=cz.PAL["blue"], lw=1.15, ls=":", zorder=3, label=r"Midpoint ($\Delta t=0.02M$)")

    ax.set_xlim(-11.5, 9.5)
    ax.set_ylim(-5.2, 9.2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$")
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.97, 0.96,
            r"$e=0.99$ Kerr passage ($r_p=1.90M < r_{\rm ergo}$)" "\n"
            rf"$\mathrm{{GL4}}$ $|\Delta\mathbf{{x}}_{{\rm end}}|={float(D['kp_gl4_end_err']):.2e}M$" "\n"
            rf"Mid $|\Delta\mathbf{{x}}_{{\rm end}}|={float(D['kp_mid_end_err']):.2e}M$",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.1, color="0.18")
    ax.legend(loc="lower right", fontsize=5.8, frameon=False, ncol=1)

    # ------------------------------------------------------------------
    # Bottom-Left: Meridional (R_cyl, z) precessing orbital envelopes
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    thh = np.linspace(0.0, np.pi, 180)
    ax.fill_betweenx(rp3d * np.cos(thh), 0.0, np.sqrt(rp3d ** 2 + a3d ** 2) * np.sin(thh),
                     color="0.12", zorder=5)
    ax.plot(np.sqrt((1.0 + np.sqrt(1.0 - a3d ** 2 * np.cos(thh) ** 2)) ** 2 + a3d ** 2) * np.sin(thh),
            (1.0 + np.sqrt(1.0 - a3d ** 2 * np.cos(thh) ** 2)) * np.cos(thh),
            color=cz.PAL["orange"], ls="--", lw=1.1, zorder=4)

    Rzw = np.hypot(xzw[:, 0], xzw[:, 1])
    Rbi = np.hypot(D["x_bi_q"][:, 0], D["x_bi_q"][:, 1])
    ax.plot(Rzw, xzw[:, 2], color=cz.PAL["blue"], lw=0.85, alpha=0.82,
            label=r"$a=0.95M$ rosette ($t=450M$)")
    ax.plot(Rbi, D["x_bi_q"][:, 2], color=cz.PAL["red"], lw=1.05, alpha=0.90,
            label=r"$a=0.90M$ mesh torus ($t=600M$)")
    ax.set_xlim(0.0, 10.6)
    ax.set_ylim(-6.6, 6.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"Cylindrical radius $\sqrt{x^2+y^2}\,[M]$")
    ax.set_ylabel(r"$z\,[M]$")
    ax.legend(loc="upper right", fontsize=6.0, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Right: Conserved Invariant Drift Histories (|dE/E0| & |dQ/Q0|)
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    tkp = D["t_kp"]
    tbi = D["t_bi"]
    ax.semilogy(tkp, np.maximum(D["kp_mid_dE"], 1.0e-16), color=cz.PAL["blue"], ls="-.", lw=1.25,
                label=r"$e=0.99$ Midpoint $|\Delta E/E_0|$")
    ax.semilogy(tkp, np.maximum(D["kp_gl4_dE"], 1.0e-16), color=cz.PAL["blue"], ls="-", lw=1.45,
                label=r"$e=0.99$ $\mathrm{GL4}$ $|\Delta E/E_0|$")
    ax.semilogy(tbi, np.maximum(D["bi_h_dE"], 1.0e-16), color=cz.PAL["orange"], ls="--", lw=1.25,
                label=r"Mesh $\mathrm{GL4}$+Hermite $|\Delta E/E_0|$")
    ax.semilogy(tbi, np.maximum(D["bi_q_dE"], 1.0e-16), color=cz.PAL["red"], ls="-", lw=1.45,
                label=r"Mesh $\mathrm{GL4}$+Quintic $|\Delta E/E_0|$")
    ax.semilogy(tbi, np.maximum(D["bi_q_dQ"], 1.0e-16), color=cz.PAL["green"], ls=":", lw=1.35,
                label=r"Mesh $\mathrm{GL4}$+Quintic $|\Delta Q/Q_0|$")

    ax.set_xlim(0.0, 600.0)
    ax.set_ylim(1.0e-16, 2.5e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Relative invariant drift")
    ax.legend(loc="lower right", fontsize=5.55, frameon=False, ncol=1)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
