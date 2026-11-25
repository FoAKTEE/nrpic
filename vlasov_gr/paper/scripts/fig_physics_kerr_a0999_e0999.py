#!/usr/bin/env python3
"""Extreme near-extremal Kerr (a = 0.999 M, e = 0.999) geodesic verification & visualization.

Executes real AthenaK OpenMP geodesic runs (build_omp_iter4/src/athena, OMP_NUM_THREADS=8)
under `$SCRATCH/runs/kerr_a0999_e0999/`:
  1. e = 0.999, a = 0.999 M deep-ergosphere passage (r_p = 1.35 M < r_ergo = 2.00 M,
     r_+ = 1.04471 M, inc = 25 deg, 4.05 azimuthal whirls):
       GL4 vs Midpoint vs Boris (symmetric) vs exact DOP853 (dt = 0.02 M, t = 220 M).
  2. a = 0.999 M 3D inclined bound zoom-whirl rosette (r_p = 1.55 M, r_a = 9.5 M, inc = 40 deg,
     GL4, dt = 0.02 M, t = 450 M).
  3. a = 0.999 M 3D inclined static-mesh torus (r_p = 4.5 M, r_a = 8.0 M, inc = 25 deg,
     dx = 0.25 M, ng = 4, dt = 0.05 M, t = 500 M): GL4+Quintic vs GL4+Hermite vs Midpoint+Hermite.

Saves reduced arrays to `vlasov_gr/paper/data/physics_kerr_a0999_e0999.npz` and
renders `vlasov_gr/paper/figures/fig_physics_kerr_a0999_e0999.{pdf,png}`.
"""
import math
import os
import re
import shutil
import subprocess
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

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
RUNROOT = f"{SCRATCH}/runs/kerr_a0999_e0999"
TPL_GEO = os.path.join(REPO, "problems", "kerr", "geodesic.athinput")
TPL_MESH = os.path.join(REPO, "problems", "kerr", "geodesic_mesh.athinput")
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_kerr_a0999_e0999.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_kerr_a0999_e0999")


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


def exact_kerr_elz(r_p, r_a, inc_deg, a, M=1.0):
    """Exact Schmidt (2002) Kerr prograde orbital constants (E, Lz, Q) for (r_p, r_a, i)."""
    zm2 = math.sin(math.radians(inc_deg)) ** 2

    def coeffs(r):
        D = r * r - 2.0 * M * r + a * a
        f = (r * r + a * a) ** 2 - D * a * a * (1.0 - zm2)
        g = 2.0 * M * a * r
        h = D / (1.0 - zm2) - a * a
        d = D * (r * r + a * a * zm2)
        return f, g, h, d

    f1, g1, h1, d1 = coeffs(r_p)
    f2, g2, h2, d2 = coeffs(r_a)
    kappa = d1 * h2 - h1 * d2
    eps = d1 * g2 - g1 * d2
    rho = f1 * h2 - h1 * f2
    eta = f1 * g2 - g1 * f2
    sig = g1 * h2 - h1 * g2
    disc = sig * (sig * eps * eps + rho * eps * kappa - eta * kappa * kappa)
    E2 = (kappa * rho + 2.0 * eps * sig - 2.0 * math.sqrt(disc)) / (rho * rho + 4.0 * eta * sig)
    E = math.sqrt(E2)
    b = 2.0 * g1 * E
    c = d1 - f1 * E2
    r1 = (-b + math.sqrt(max(b * b - 4.0 * h1 * c, 0.0))) / (2.0 * h1)
    r2 = (-b - math.sqrt(max(b * b - 4.0 * h1 * c, 0.0))) / (2.0 * h1)

    def res2(Lz):
        return abs(f2 * E2 - 2.0 * g2 * E * Lz - h2 * Lz * Lz - d2)

    Lz = r1 if res2(r1) < res2(r2) else r2
    Q = zm2 * (a * a * (1.0 - E2) + Lz * Lz / (1.0 - zm2))
    return E, Lz, Q


def bl_to_cks_state(r0, E, Lz, Q, a, M=1.0, inward=True):
    D0 = r0 * r0 - 2.0 * M * r0 + a * a
    R0 = max(((r0 * r0 + a * a) * E - a * Lz) ** 2 - D0 * (r0 * r0 + (Lz - a * E) ** 2 + Q), 0.0)
    ur_bl = (-1.0 if inward else 1.0) * math.sqrt(R0) / D0
    uth_bl = math.sqrt(max(Q, 0.0))
    _, x_c, u_c = kerr.convert_state(
        0.0, np.array([r0, 0.5 * math.pi, 0.0]), np.array([ur_bl, uth_bl, Lz]),
        "bl", "cks", a=a, M=M,
    )
    return x_c, u_c


def read_traj_bin(path):
    arr = np.fromfile(path, dtype=np.float64).reshape(-1, 8)
    m0 = arr[:, 1] == 0.0
    arr = arr[m0]
    fin = np.all(np.isfinite(arr), axis=1)
    arr = arr[fin]
    return arr[:, 0], arr[:, 2:5], arr[:, 5:8]


def run_athena_omp(name, ath_txt):
    rdir = os.path.join(RUNROOT, name)
    traj_path = os.path.join(rdir, f"{name}.traj.bin")
    if os.path.isfile(traj_path) and os.environ.get("RERUN_KERR999", "0") != "1":
        t, x, u = read_traj_bin(traj_path)
        return 0, t, x, u
    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir, exist_ok=True)
    ath_path = os.path.join(RUNROOT, f"{name}.athinput")
    with open(ath_path, "w") as f:
        f.write(ath_txt)
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "8"
    env["OMP_PROC_BIND"] = "spread"
    env["OMP_PLACES"] = "cores"
    log_path = os.path.join(rdir, f"{name}.stdout.log")
    with open(log_path, "w") as flog:
        rc = subprocess.run([BIN_OMP, "-i", ath_path], cwd=rdir, env=env,
                            stdout=flog, stderr=subprocess.STDOUT, check=False).returncode
    t, x, u = read_traj_bin(os.path.join(rdir, f"{name}.traj.bin"))
    return rc, t, x, u


def unwrapped_turns(x):
    phi = np.unwrap(np.arctan2(x[:, 1], x[:, 0]))
    return (phi - phi[0]) / (2.0 * math.pi)


def cks_r_array(x, a):
    return np.array([kerr.cks_radius(pt, a=a) for pt in x])


def build_and_run():
    if os.path.exists(DATA_OUT) and os.environ.get("RERUN_KERR999", "0") != "1":
        cached = np.load(DATA_OUT)
        if "gl4_dx" in cached:
            print(f"Loading cached {DATA_OUT} (set RERUN_KERR999=1 to recompute)", flush=True)
            return dict(cached)

    os.makedirs(RUNROOT, exist_ok=True)
    tpl_geo = open(TPL_GEO).read()
    tpl_mesh = open(TPL_MESH).read()
    a999, M = 0.999, 1.0
    rp_bh, _ = kerr.horizon_radii(a=a999, M=M)

    def make_geo_cfg(base, x0, u0, a, tlim, dt, pusher, vpush=None, triad="symmetric"):
        txt = set_param(tpl_geo, "job", "basename", base)
        txt = set_param(txt, "time", "tlim", f"{tlim}")
        txt = set_param(txt, "particles", "metric", "kerr_schild")
        txt = set_param(txt, "particles", "bh_mass", "1.0")
        txt = set_param(txt, "particles", "bh_spin", f"{a}")
        txt = set_param(txt, "particles", "dt", f"{dt}")
        txt = set_param(txt, "particles", "tolerance", "2.0e-14")
        txt = set_param(txt, "particles", "max_iterations", "200")
        txt = set_param(txt, "particles", "pusher", pusher)
        txt = set_param(txt, "particles", "triad", triad)
        if vpush is not None:
            txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
            txt = set_param(txt, "particles", "vlasov_pusher", vpush)
        for idx, k in enumerate(("p0_x1", "p0_x2", "p0_x3")):
            txt = set_param(txt, "particles", k, f"{x0[idx]:.17g}")
        for idx, k in enumerate(("p0_u1", "p0_u2", "p0_u3")):
            txt = set_param(txt, "particles", k, f"{u0[idx]:.17g}")
        return txt

    # 1. Extreme e = 0.999, a = 0.999 M passage (r_p = 1.35 M < r_ergo = 2.0 M, i = 25 deg)
    e_p, rp_p, inc_p = 0.999, 1.35, 25.0
    ra_p = rp_p * (1.0 + e_p) / (1.0 - e_p)
    E0_p, L0_p, Q0_p = exact_kerr_elz(rp_p, ra_p, inc_p, a999, M=M)
    x0_p, u0_p = bl_to_cks_state(20.0, E0_p, L0_p, Q0_p, a999, M=M, inward=True)

    rc_gl4, t_gl4, x_gl4, u_gl4 = run_athena_omp(
        "p999_gl4", make_geo_cfg("p999_gl4", x0_p, u0_p, a999, 220.0, 0.02, "vlasov_hybrid", "gl4")
    )
    rc_mid, t_mid, x_mid, u_mid = run_athena_omp(
        "p999_mid", make_geo_cfg("p999_mid", x0_p, u0_p, a999, 220.0, 0.02, "midpoint")
    )
    rc_bor, t_bor, x_bor, u_bor = run_athena_omp(
        "p999_boris", make_geo_cfg("p999_boris", x0_p, u0_p, a999, 220.0, 0.02, "boris", triad="symmetric")
    )
    tr_dop = geodesic.integrate(
        "cks", x0_p, u0_p, 220.0, t0=0.0, dt_out=0.02, rtol=1.0e-13, atol=1.0e-13, a=a999, M=M
    )

    ih_gl4 = geodesic.invariant_history("cks", x_gl4, u_gl4, a=a999, M=M, ref=(E0_p, L0_p, Q0_p))
    ih_mid = geodesic.invariant_history("cks", x_mid, u_mid, a=a999, M=M, ref=(E0_p, L0_p, Q0_p))
    ih_bor = geodesic.invariant_history("cks", x_bor, u_bor, a=a999, M=M, ref=(E0_p, L0_p, Q0_p))

    r_dop = cks_r_array(tr_dop.x, a999)
    r_gl4 = cks_r_array(x_gl4, a999)
    r_mid = cks_r_array(x_mid, a999)
    r_bor = cks_r_array(x_bor, a999)

    phi_dop = unwrapped_turns(tr_dop.x)
    phi_gl4 = unwrapped_turns(x_gl4)
    phi_mid = unwrapped_turns(x_mid)
    phi_bor = unwrapped_turns(x_bor)

    def endpoint_err(t_arr, x_arr):
        if len(t_arr) and abs(t_arr[-1] - tr_dop.t[-1]) < 0.05:
            return float(np.linalg.norm(x_arr[-1] - tr_dop.x[-1]))
        return float("nan")

    err_gl4 = endpoint_err(t_gl4, x_gl4)
    err_mid = endpoint_err(t_mid, x_mid)
    err_bor = endpoint_err(t_bor, x_bor)

    # 2. a = 0.999 M bound 3D inclined ergosphere-diving rosette (r_p = 1.55 M, r_a = 9.5 M, i = 40 deg)
    E0_3d, L0_3d, Q0_3d = exact_kerr_elz(1.55, 9.5, 40.0, a999, M=M)
    x0_3d, u0_3d = bl_to_cks_state(9.5, E0_3d, L0_3d, Q0_3d, a999, M=M, inward=True)
    rc_zw, t_zw, x_zw, u_zw = run_athena_omp(
        "zw999_gl4", make_geo_cfg("zw999_gl4", x0_3d, u0_3d, a999, 450.0, 0.02, "vlasov_hybrid", "gl4")
    )
    ih_zw = geodesic.invariant_history("cks", x_zw, u_zw, a=a999, M=M, ref=(E0_3d, L0_3d, Q0_3d))

    # 3. a = 0.999 M 3D inclined static-mesh torus (r_p = 4.5 M, r_a = 8.0 M, i = 25 deg, dx = 0.25 M, ng = 4)
    E0_ms, L0_ms, Q0_ms = exact_kerr_elz(4.5, 8.0, 25.0, a999, M=M)
    x0_ms, u0_ms = bl_to_cks_state(8.0, E0_ms, L0_ms, Q0_ms, a999, M=M, inward=True)

    def run_mesh999(base, pusher, interp_kind, vpush=None):
        txt = set_param(tpl_mesh, "job", "basename", base)
        txt = set_param(txt, "mesh", "nghost", "4")
        txt = set_param(txt, "time", "tlim", "500.0")
        txt = set_param(txt, "particles", "bh_mass", "1.0")
        txt = set_param(txt, "particles", "bh_spin", f"{a999}")
        txt = set_param(txt, "particles", "dt", "0.05")
        txt = set_param(txt, "particles", "hist_dcycle", "200")
        txt = set_param(txt, "particles", "traj_dcycle", "1")
        txt = set_param(txt, "particles", "pusher", pusher)
        txt = set_param(txt, "particles", "interp", interp_kind)
        if vpush is not None:
            txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
            txt = set_param(txt, "particles", "vlasov_pusher", vpush)
        for idx, k in enumerate(("p0_x1", "p0_x2", "p0_x3")):
            txt = set_param(txt, "particles", k, f"{x0_ms[idx]:.17g}")
        for idx, k in enumerate(("p0_u1", "p0_u2", "p0_u3")):
            txt = set_param(txt, "particles", k, f"{u0_ms[idx]:.17g}")
        return run_athena_omp(base, txt)

    rc_mq, t_mq, x_mq, u_mq = run_mesh999("mesh999_quintic", "vlasov_hybrid", "quintic", "gl4")
    rc_mh, t_mh, x_mh, u_mh = run_mesh999("mesh999_hermite", "vlasov_hybrid", "hermite", "gl4")
    rc_mm, t_mm, x_mm, u_mm = run_mesh999("mesh999_mid", "midpoint", "hermite")
    ih_mq = geodesic.invariant_history("cks", x_mq, u_mq, a=a999, M=M, ref=(E0_ms, L0_ms, Q0_ms))
    ih_mh = geodesic.invariant_history("cks", x_mh, u_mh, a=a999, M=M, ref=(E0_ms, L0_ms, Q0_ms))
    ih_mm = geodesic.invariant_history("cks", x_mm, u_mm, a=a999, M=M, ref=(E0_ms, L0_ms, Q0_ms))

    print("=== Near-Extremal Kerr (a=0.999M, e=0.999) AthenaK Summary ===", flush=True)
    print(f"1) e=0.999 Passage (a=0.999M, r_+={rp_bh:.5f}M, r_p=1.35M, r_a=2698.65M, inc=25deg, dt=0.02M, t=220M):", flush=True)
    print(f"   DOP853 : r_min={r_dop.min():.5f}M turns={phi_dop[-1]:.4f} r_end={r_dop[-1]:.3f}M", flush=True)
    print(f"   GL4    : rc={rc_gl4} r_min={r_gl4.min():.5f}M turns={phi_gl4[-1]:.4f} dx_end={err_gl4:.2e}M "
          f"max|dE/E|={ih_gl4['max_abs_dE']:.2e} max|dL/L|={ih_gl4['max_abs_dLz']:.2e} max|dQ/Q|={ih_gl4['max_abs_dQ']:.2e}", flush=True)
    print(f"   Midpt  : rc={rc_mid} t_end={t_mid[-1]:.2f}M r_min={r_mid.min():.5f}M turns={phi_mid[-1]:.4f} dx_end={err_mid:.2e}M "
          f"max|dE/E|={ih_mid['max_abs_dE']:.2e} max|dL/L|={ih_mid['max_abs_dLz']:.2e} max|dQ/Q|={ih_mid['max_abs_dQ']:.2e}", flush=True)
    print(f"   Boris  : rc={rc_bor} t_end={t_bor[-1]:.2f}M r_min={r_bor.min():.5f}M turns={phi_bor[-1]:.4f} dx_end={err_bor:.2e}M "
          f"max|dE/E|={ih_bor['max_abs_dE']:.2e} max|dL/L|={ih_bor['max_abs_dLz']:.2e} max|dQ/Q|={ih_bor['max_abs_dQ']:.2e}", flush=True)
    print(f"2) 3D Bound Rosette (a=0.999M, r_p=1.55M, r_a=9.5M, inc=40deg, GL4, t=450M): rc={rc_zw} "
          f"max|dE/E|={ih_zw['max_abs_dE']:.2e} max|dL/L|={ih_zw['max_abs_dLz']:.2e} max|dQ/Q|={ih_zw['max_abs_dQ']:.2e}", flush=True)
    print(f"3) 3D Mesh Torus (a=0.999M, r_p=4.5M, r_a=8.0M, dx=0.25M, dt=0.05M, t=500M):", flush=True)
    print(f"   GL4+Quintic : rc={rc_mq} max|dE/E|={ih_mq['max_abs_dE']:.2e} max|dQ/Q|={ih_mq['max_abs_dQ']:.2e}", flush=True)
    print(f"   GL4+Hermite : rc={rc_mh} max|dE/E|={ih_mh['max_abs_dE']:.2e} max|dQ/Q|={ih_mh['max_abs_dQ']:.2e}", flush=True)
    print(f"   Mid+Hermite : rc={rc_mm} max|dE/E|={ih_mm['max_abs_dE']:.2e} max|dQ/Q|={ih_mm['max_abs_dQ']:.2e}", flush=True)

    def ds(arr, nmax=3000):
        st = max(1, len(arr) // nmax)
        return arr[::st]

    def pos_err_series(t_arr, x_arr):
        ref_x = np.column_stack([
            np.interp(t_arr, tr_dop.t, tr_dop.x[:, k]) for k in range(3)
        ])
        return np.linalg.norm(x_arr - ref_x, axis=1)

    dx_gl4 = pos_err_series(t_gl4, x_gl4)
    dx_mid = pos_err_series(t_mid, x_mid)
    dx_bor = pos_err_series(t_bor, x_bor)

    out = dict(
        a999=np.float64(a999),
        E0_3d=np.float64(E0_3d), L0_3d=np.float64(L0_3d), Q0_3d=np.float64(Q0_3d),
        t_zw=ds(t_zw, 4500), x_zw=ds(x_zw, 4500),
        zw_max_dE=np.float64(ih_zw["max_abs_dE"]), zw_max_dQ=np.float64(ih_zw["max_abs_dQ"]),
        t_dop=ds(tr_dop.t, 3000), x_dop=ds(tr_dop.x, 3000), r_dop=ds(r_dop, 3000), phi_dop=ds(phi_dop, 3000),
        t_gl4=ds(t_gl4, 3000), x_gl4=ds(x_gl4, 3000), r_gl4=ds(r_gl4, 3000), phi_gl4=ds(phi_gl4, 3000),
        gl4_dE=ds(np.abs(ih_gl4["dE"]), 3000), gl4_dQ=ds(np.abs(ih_gl4["dQ"]), 3000), gl4_dx=ds(dx_gl4, 3000),
        t_mid=ds(t_mid, 3000), x_mid=ds(x_mid, 3000), r_mid=ds(r_mid, 3000), phi_mid=ds(phi_mid, 3000),
        mid_dE=ds(np.abs(ih_mid["dE"]), 3000), mid_dQ=ds(np.abs(ih_mid["dQ"]), 3000), mid_dx=ds(dx_mid, 3000),
        t_bor=ds(t_bor, 3000), x_bor=ds(x_bor, 3000), r_bor=ds(r_bor, 3000), phi_bor=ds(phi_bor, 3000),
        bor_dE=ds(np.abs(ih_bor["dE"]), 3000), bor_dQ=ds(np.abs(ih_bor["dQ"]), 3000), bor_dx=ds(dx_bor, 3000),
        err_gl4=np.float64(err_gl4), err_mid=np.float64(err_mid), err_bor=np.float64(err_bor),
        turns_dop=np.float64(phi_dop[-1]), turns_gl4=np.float64(phi_gl4[-1]),
        turns_mid=np.float64(phi_mid[-1]), turns_bor=np.float64(phi_bor[-1]),
        t_mq=ds(t_mq, 2500), mq_dE=ds(np.abs(ih_mq["dE"]), 2500), mq_dQ=ds(np.abs(ih_mq["dQ"]), 2500),
        t_mh=ds(t_mh, 2500), mh_dE=ds(np.abs(ih_mh["dE"]), 2500), mh_dQ=ds(np.abs(ih_mh["dQ"]), 2500),
        t_mm=ds(t_mm, 2500), mm_dE=ds(np.abs(ih_mm["dE"]), 2500),
    )
    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"Saved {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def cks_surface(r_func, a, nth=44, nph=60):
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
    a999 = float(D["a999"])
    rp = 1.0 + math.sqrt(1.0 - a999 * a999)

    fig = plt.figure(figsize=(8.6, 6.8))
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.965, bottom=0.075, top=0.965,
                          wspace=0.40, hspace=0.28)

    # Top-Left (3D): a = 0.999 M ergosphere-diving rosette (t = 450 M)
    ax3d = fig.add_subplot(gs[0, 0], projection="3d")
    Xh, Yh, Zh = cks_surface(lambda th: np.full_like(th, rp), a999, nth=28, nph=40)
    Xe, Ye, Ze = cks_surface(lambda th: 1.0 + np.sqrt(np.maximum(1.0 - a999 * a999 * np.cos(th) ** 2, 0.0)),
                             a999, nth=28, nph=40)
    ax3d.plot_surface(Xh, Yh, Zh, color="0.10", alpha=0.96, shade=True, linewidth=0)
    ax3d.plot_surface(Xe, Ye, Ze, color=cz.PAL["orange"], alpha=0.16, linewidth=0.2,
                      edgecolors=(0.85, 0.45, 0.0, 0.15))

    xzw, tzw = D["x_zw"], D["t_zw"]
    pts3d = xzw.reshape(-1, 1, 3)
    segs3d = np.concatenate([pts3d[:-1], pts3d[1:]], axis=1)
    lc3d = Line3DCollection(segs3d, cmap="viridis", norm=plt.Normalize(0.0, float(tzw[-1])),
                            linewidth=1.1, alpha=0.92)
    lc3d.set_array(tzw[:-1])
    ax3d.add_collection3d(lc3d)
    ax3d.scatter([xzw[0, 0]], [xzw[0, 1]], [xzw[0, 2]], color=cz.PAL["green"], s=18, edgecolor="k", lw=0.5, zorder=10)
    ax3d.scatter([xzw[-1, 0]], [xzw[-1, 1]], [xzw[-1, 2]], color=cz.PAL["red"], s=20, marker="s", edgecolor="k", lw=0.5, zorder=10)
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
                r"Ergosphere rosette ($a=0.999M$, $\mathrm{GL4}$, $t=450M$)" "\n"
                rf"$E={float(D['E0_3d']):.4f},\;L_z={float(D['L0_3d']):.2f},\;Q={float(D['Q0_3d']):.2f}$",
                transform=ax3d.transAxes, ha="left", va="top", fontsize=6.4)

    # Top-Right (x, y): Extreme e = 0.999, a = 0.999 M 4-whirl passage
    ax = fig.add_subplot(gs[0, 1])
    r_hor_eq = math.sqrt(rp * rp + a999 * a999)
    r_erg_eq = math.sqrt(4.0 + a999 * a999)
    ph = np.linspace(0.0, 2.0 * np.pi, 240)
    ax.fill(r_hor_eq * np.cos(ph), r_hor_eq * np.sin(ph), color="0.12", zorder=5, label=r"Horizon $r_+$")
    ax.plot(r_erg_eq * np.cos(ph), r_erg_eq * np.sin(ph), color=cz.PAL["orange"], ls="--", lw=1.1, zorder=4,
            label=r"Ergosphere $r_{\rm ergo}$")
    ax.plot(D["x_dop"][:, 0], D["x_dop"][:, 1], color="0.45", lw=2.3, alpha=0.55, zorder=2, label=r"$\mathrm{DOP853}$ exact")
    ax.plot(D["x_gl4"][:, 0], D["x_gl4"][:, 1], color=cz.PAL["red"], lw=1.3, ls="-", zorder=4, label=r"$\mathrm{GL4}$ ($\Delta t=0.02M$)")
    ax.plot(D["x_mid"][:, 0], D["x_mid"][:, 1], color=cz.PAL["blue"], lw=1.1, ls=":", zorder=3, label=r"Midpoint ($\Delta t=0.02M$)")
    ax.plot(D["x_bor"][:, 0], D["x_bor"][:, 1], color=cz.PAL["green"], lw=1.05, ls="-.", zorder=3, label=r"Boris ($\Delta t=0.02M$)")
    ax.set_xlim(-4.5, 9.5)
    ax.set_ylim(-5.2, 5.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$")
    ax.set_ylabel(r"$y\,[M]$")
    eg4 = float(D["err_gl4"])
    emid = float(D["err_mid"])
    ebor = float(D["err_bor"])
    fmt = lambda v: rf"{v:.2e}M" if np.isfinite(v) else r"\mathrm{plunge}"
    ax.text(0.97, 0.96,
            r"$a=0.999M,\,e=0.999$ ($r_p=1.35M$, $4.05$ turns)" "\n"
            rf"$\mathrm{{GL4}}$ $|\Delta\mathbf{{x}}_{{\rm end}}|={fmt(eg4)}$" "\n"
            rf"Mid / Boris: ${fmt(emid)}$ / ${fmt(ebor)}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=5.8, color="0.18")
    ax.legend(loc="lower right", fontsize=5.6, frameon=False, ncol=1)

    # Bottom-Left: Position error |x - x_DOP853|(t) & radius r(t) through periapsis
    ax = fig.add_subplot(gs[1, 0])
    h_bl = []
    h_bl.append(ax.semilogy(D["t_mid"], np.maximum(D["mid_dx"], 1.0e-12), color=cz.PAL["blue"], lw=1.25, ls=":",
                            label=r"Midpoint $|\Delta\mathbf{x}|$")[0])
    h_bl.append(ax.semilogy(D["t_bor"], np.maximum(D["bor_dx"], 1.0e-12), color=cz.PAL["green"], lw=1.2, ls="-.",
                            label=r"Boris $|\Delta\mathbf{x}|$")[0])
    h_bl.append(ax.semilogy(D["t_gl4"], np.maximum(D["gl4_dx"], 1.0e-12), color=cz.PAL["red"], lw=1.45, ls="-",
                            label=r"$\mathrm{GL4}$ $|\Delta\mathbf{x}|$")[0])
    ax.set_xlim(0.0, 220.0)
    ax.set_ylim(2.0e-11, 5.0e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Position error $|\mathbf{x}-\mathbf{x}_{\rm exact}|\,[M]$")

    ax2 = ax.twinx()
    h_bl.append(ax2.plot(D["t_dop"], D["r_dop"], color="0.40", lw=1.1, ls="--", alpha=0.7,
                         label=r"$r(t)$ (right)")[0])
    ax2.axhline(r_erg_eq, color=cz.PAL["orange"], lw=0.85, ls=":", alpha=0.8)
    ax2.text(216.0, r_erg_eq + 0.55, r"$r_{\rm ergo}=2M$", ha="right", va="bottom",
             fontsize=5.6, color=cz.PAL["orange"])
    ax2.set_ylim(0.0, 31.0)
    ax2.set_ylabel(r"Kerr-Schild radius $r\,[M]$", color="0.35")
    ax2.tick_params(which="both", direction="in")
    ax.legend(handles=h_bl, loc="lower right", bbox_to_anchor=(0.98, 0.14), fontsize=5.5, frameon=False, ncol=1)

    # Bottom-Right: Relative Killing Invariant Drift Histories (10^-16 to 10^-4)
    ax = fig.add_subplot(gs[1, 1])
    ax.semilogy(D["t_mid"], np.maximum(D["mid_dE"], 1.0e-16), color=cz.PAL["blue"], ls=":", lw=1.2,
                label=r"$e=0.999$ Midpoint $|\Delta E/E_0|$")
    ax.semilogy(D["t_bor"], np.maximum(D["bor_dE"], 1.0e-16), color=cz.PAL["green"], ls="-.", lw=1.15,
                label=r"$e=0.999$ Boris $|\Delta E/E_0|$")
    ax.semilogy(D["t_gl4"], np.maximum(D["gl4_dE"], 1.0e-16), color=cz.PAL["blue"], ls="-", lw=1.45,
                label=r"$e=0.999$ $\mathrm{GL4}$ $|\Delta E/E_0|$")
    ax.semilogy(D["t_mh"], np.maximum(D["mh_dE"], 1.0e-16), color=cz.PAL["orange"], ls="--", lw=1.2,
                label=r"Mesh $\mathrm{GL4}$+Hermite $|\Delta E/E_0|$")
    ax.semilogy(D["t_mq"], np.maximum(D["mq_dE"], 1.0e-16), color=cz.PAL["red"], ls="-", lw=1.4,
                label=r"Mesh $\mathrm{GL4}$+Quintic $|\Delta E/E_0|$")
    ax.semilogy(D["t_mq"], np.maximum(D["mq_dQ"], 1.0e-16), color="0.25", ls=":", lw=1.2,
                label=r"Mesh $\mathrm{GL4}$+Quintic $|\Delta Q/Q_0|$")
    ax.set_xlim(0.0, 500.0)
    ax.set_ylim(5.0e-17, 6.0e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Relative invariant drift")
    ax.legend(loc="lower right", bbox_to_anchor=(0.99, 0.01), fontsize=5.35, frameon=False, ncol=1)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
