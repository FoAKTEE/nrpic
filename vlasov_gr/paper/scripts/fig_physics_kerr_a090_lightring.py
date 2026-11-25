#!/usr/bin/env python3
"""Kerr (a = 0.9 M) null light-ring separatrix & fall-in orbit-number test suite and visualization.

Executes real AthenaK null-geodesic (eps = 0, `<particles> zero_mass = null`) multi-particle
runs (`build_omp_iter4/src/athena`, `OMP_NUM_THREADS=8`) under `$SCRATCH/runs/kerr_a090_lightring/`
comparing 4th-order Gauss-Legendre (`vlasov_pusher = gl4`) against 2nd-order Implicit Midpoint
(`vlasov_pusher = midpoint`) across dt in {0.02, 0.05, 0.10} M against exact null DOP853:
  - 32 equatorial separatrix photons (`delta xi / xi_c+` from -1e-1 to +1e-1 in +/-3e-9..1e-1)
    probing the prograde light ring r_ph+ = 1.557855 M and fall-in / escape orbit numbers N_turns.
  - Perched prograde light-ring photon (r_0 = r_ph+, tlim = 200 M) probing Lyapunov departure
    and hold orbit number N_hold.
  - 3D inclined spherical photon-shell orbit (r_sph = 2.20 M, eta = 16.7242) and retrograde
    light-ring orbits (r_ph- = 3.910268 M).

Saves reduced data to `vlasov_gr/paper/data/physics_kerr_a090_lightring.npz` and renders
`vlasov_gr/paper/figures/fig_physics_kerr_a090_lightring.{pdf,png}`.
"""
import math
import os
import re
import shutil
import subprocess
import sys
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import io as nrp_io  # noqa: E402
from nrpic import kerr  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
REPO = os.path.dirname(os.path.dirname(PAPER_DIR))
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
BIN_OMP = f"{SCRATCH}/build_omp_iter4/src/athena"
RUNROOT = f"{SCRATCH}/runs/kerr_a090_lightring"
TPL_GEO = os.path.join(REPO, "problems", "kerr", "geodesic.athinput")
NRP_PATH = os.path.join(RUNROOT, "kerr_a090_lightring.nrp")
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_kerr_a090_lightring.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_kerr_a090_lightring")

A_SPIN = 0.9
M_BH = 1.0
RP_BH, _ = kerr.horizon_radii(a=A_SPIN, M=M_BH)
R_PH_PRO = 2.0 * M_BH * (1.0 + math.cos(2.0 / 3.0 * math.acos(-A_SPIN / M_BH)))
R_PH_RET = 2.0 * M_BH * (1.0 + math.cos(2.0 / 3.0 * math.acos(+A_SPIN / M_BH)))
R_ERGO_EQ = 2.0 * M_BH
R_SPH = 2.20


def photon_xi_eta(r, a=A_SPIN, M=M_BH):
    xi = -(r * r * (r - 3.0 * M) + a * a * (r + M)) / (a * (r - M))
    eta = -(r ** 3 * (r * (r - 3.0 * M) ** 2 - 4.0 * a * a * M)) / (a * a * (r - M) ** 2)
    return xi, eta


XI_C_PRO, _ = photon_xi_eta(R_PH_PRO)
XI_C_RET, _ = photon_xi_eta(R_PH_RET)
XI_SPH, ETA_SPH = photon_xi_eta(R_SPH)
OM_PH_PRO = 1.0 / (R_PH_PRO ** 1.5 + A_SPIN)


def compute_lyapunov_pro(r=R_PH_PRO, xi=XI_C_PRO, a=A_SPIN, M=M_BH):
    h = 1.0e-5
    def R_null(rv):
        D = rv * rv - 2.0 * M * rv + a * a
        return ((rv * rv + a * a) - a * xi) ** 2 - D * (xi - a) ** 2
    Rpp = (R_null(r + h) - 2.0 * R_null(r) + R_null(r - h)) / (h * h)
    Dp = r * r - 2.0 * M * r + a * a
    tdot = (r * r + a * a) * ((r * r + a * a) - a * xi) / Dp + a * (xi - a)
    lam_t = math.sqrt(0.5 * Rpp) / tdot
    turns_per_dec = math.log(10.0) * OM_PH_PRO / (2.0 * math.pi * lam_t)
    return lam_t, turns_per_dec


LAM_PH_PRO, TURNS_PER_DEC = compute_lyapunov_pro()


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


def null_bl_to_cks(r0, th0, xi, eta, inward=True, perched=False):
    D0 = r0 * r0 - 2.0 * M_BH * r0 + A_SPIN * A_SPIN
    if perched:
        ur0 = 0.0
        uth0 = math.sqrt(max(eta, 0.0))
    else:
        R0 = max(((r0 * r0 + A_SPIN * A_SPIN) - A_SPIN * xi) ** 2 - D0 * (eta + (xi - A_SPIN) ** 2), 0.0)
        ur0 = (-1.0 if inward else 1.0) * math.sqrt(R0) / D0
        Th0 = max(eta + math.cos(th0) ** 2 * (A_SPIN * A_SPIN - xi * xi / (math.sin(th0) ** 2)), 0.0)
        uth0 = math.sqrt(Th0)
    _, xc, uc = kerr.convert_state(
        0.0, np.array([r0, th0, 0.0]), np.array([ur0, uth0, xi]),
        "bl", "cks", a=A_SPIN, M=M_BH, u_t=-1.0,
    )
    m = kerr.adm_cks(xc, a=A_SPIN, M=M_BH, derivs=False)
    U = m.gamma_inv @ uc
    W = math.sqrt(float(uc @ U))
    E_chk = m.alpha * W - float(m.beta @ uc)
    ginv4 = kerr.ginv4_from_adm(m)
    u4 = np.array([-E_chk, uc[0], uc[1], uc[2]])
    g4norm = float(u4 @ ginv4 @ u4)
    assert abs(g4norm) < 1.0e-13 and abs(E_chk - 1.0) < 1.0e-13, f"Non-null IC: E={E_chk}, g4={g4norm}"
    return xc, uc


def build_ic_catalog():
    deltas_neg = [-1.0e-1, -3.0e-2, -1.0e-2, -3.0e-3, -1.0e-3, -3.0e-4, -1.0e-4, -3.0e-5,
                  -1.0e-5, -3.0e-6, -1.0e-6, -3.0e-7, -1.0e-7, -3.0e-8, -1.0e-8, -3.0e-9]
    deltas_pos = [-d for d in reversed(deltas_neg)]
    deltas_eq = deltas_neg + deltas_pos  # 32 equatorial separatrix photons (tags 0..31)

    xs, us = [], []
    # Tags 0..31: prograde equatorial separatrix rays from r0 = 12 M
    for drel in deltas_eq:
        xc, uc = null_bl_to_cks(12.0, 0.5 * math.pi, XI_C_PRO * (1.0 + drel), 0.0, inward=True)
        xs.append(xc)
        us.append(uc)
    # Tag 32: perched directly on prograde light ring r_ph+
    xc, uc = null_bl_to_cks(R_PH_PRO, 0.5 * math.pi, XI_C_PRO, 0.0, perched=True)
    xs.append(xc); us.append(uc)
    # Tags 33..35: 3D spherical photon-shell orbit (r_sph=2.20 M) perched + infall/scatter from r0=12 M
    xc, uc = null_bl_to_cks(R_SPH, 0.5 * math.pi, XI_SPH, ETA_SPH, perched=True)
    xs.append(xc); us.append(uc)
    xc, uc = null_bl_to_cks(12.0, 0.5 * math.pi, XI_SPH * (1.0 - 1.0e-4), ETA_SPH, inward=True)
    xs.append(xc); us.append(uc)
    xc, uc = null_bl_to_cks(12.0, 0.5 * math.pi, XI_SPH * (1.0 + 1.0e-4), ETA_SPH, inward=True)
    xs.append(xc); us.append(uc)
    # Tags 36..38: retrograde light ring r_ph- perched + infall/escape (xi_c- * (1 -/+ 1e-3))
    xc, uc = null_bl_to_cks(R_PH_RET, 0.5 * math.pi, XI_C_RET, 0.0, perched=True)
    xs.append(xc); us.append(uc)
    xc, uc = null_bl_to_cks(12.0, 0.5 * math.pi, XI_C_RET * (1.0 - 1.0e-3), 0.0, inward=True)
    xs.append(xc); us.append(uc)
    xc, uc = null_bl_to_cks(12.0, 0.5 * math.pi, XI_C_RET * (1.0 + 1.0e-3), 0.0, inward=True)
    xs.append(xc); us.append(uc)

    xs = np.asarray(xs, dtype=np.float64)
    us = np.asarray(us, dtype=np.float64)
    os.makedirs(RUNROOT, exist_ok=True)
    nrp_io.write_nrp(NRP_PATH, xs, us, np.zeros(len(xs), dtype=np.float64))
    return deltas_eq, xs, us


def integrate_null_dop853(x0, u0, t_max=200.0, dt_out=0.02, stop_bounds=True):
    def rhs(t, y):
        x = y[:3]
        u = y[3:]
        m = kerr.adm_cks(x, a=A_SPIN, M=M_BH, derivs=True)
        U = m.gamma_inv @ u
        W = math.sqrt(max(float(u @ U), 1.0e-30))
        dx = (m.alpha / W) * U - m.beta
        du = (-W) * m.dalpha + (m.dbeta @ u) + (0.5 * m.alpha / W) * np.einsum("ijk,j,k->i", m.dgamma, U, U)
        return np.concatenate([dx, du])

    events = []
    if stop_bounds:
        def ev_hor(t, y):
            return kerr.cks_radius(y[:3], a=A_SPIN) - (RP_BH + 0.002)
        ev_hor.terminal = True
        ev_hor.direction = -1

        def ev_esc(t, y):
            return kerr.cks_radius(y[:3], a=A_SPIN) - 12.1 if t > 1.0 else -1.0
        ev_esc.terminal = True
        ev_esc.direction = 1
        events = [ev_hor, ev_esc]

    y0 = np.concatenate([x0, u0])
    sol = solve_ivp(rhs, (0.0, t_max), y0, method="DOP853", events=events,
                    rtol=1.0e-13, atol=1.0e-13, dense_output=True)
    t_end = float(sol.t[-1])
    ts = np.arange(0.0, t_end, dt_out)
    if len(ts) == 0 or ts[-1] < t_end - 1.0e-12:
        ts = np.append(ts, t_end)
    ys = sol.sol(ts).T
    return ts, ys[:, :3], ys[:, 3:]


def run_athena_omp(name, vpush, dt, tlim=200.0):
    rdir = os.path.join(RUNROOT, name)
    traj_path = os.path.join(rdir, f"{name}.traj.bin")
    if not (os.path.isfile(traj_path) and os.environ.get("RERUN_LR", "0") != "1"):
        if os.path.exists(rdir):
            shutil.rmtree(rdir)
        os.makedirs(rdir, exist_ok=True)
        tpl = open(TPL_GEO).read()
        # Strip inline p0_* / nparticles cleanly and widen mesh bounds for r0 = 12 M
        tpl = "\n".join(ln for ln in tpl.splitlines() if not re.match(r"^\s*(?:nparticles|p0_)", ln)) + "\n"
        txt = set_param(tpl, "job", "basename", name)
        txt = set_param(txt, "mesh", "x1min", "-25.0")
        txt = set_param(txt, "mesh", "x1max", "25.0")
        txt = set_param(txt, "mesh", "x2min", "-25.0")
        txt = set_param(txt, "mesh", "x2max", "25.0")
        txt = set_param(txt, "mesh", "x3min", "-25.0")
        txt = set_param(txt, "mesh", "x3max", "25.0")
        txt = set_param(txt, "time", "tlim", f"{tlim}")
        txt = set_param(txt, "particles", "pusher", "vlasov_hybrid")
        txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
        txt = set_param(txt, "particles", "vlasov_pusher", vpush)
        txt = set_param(txt, "particles", "zero_mass", "null")
        txt = set_param(txt, "particles", "metric", "kerr_schild")
        txt = set_param(txt, "particles", "bh_mass", f"{M_BH}")
        txt = set_param(txt, "particles", "bh_spin", f"{A_SPIN}")
        txt = set_param(txt, "particles", "alpha_exc", "-1.0")
        txt = set_param(txt, "particles", "vlasov_kerr_r_exc", "0.95")
        txt = set_param(txt, "particles", "dt", f"{dt}")
        txt = set_param(txt, "particles", "tolerance", "2.0e-14")
        txt = set_param(txt, "particles", "max_iterations", "200")
        txt = set_param(txt, "particles", "hist_dcycle", "500")
        txt = set_param(txt, "particles", "traj_dcycle", "1")
        txt = set_param(txt, "particles", "traj_ntrack", "39")
        txt = set_param(txt, "particles", "particle_file", NRP_PATH)

        ath_path = os.path.join(RUNROOT, f"{name}.athinput")
        with open(ath_path, "w") as f:
            f.write(txt)
        env = dict(os.environ)
        env["OMP_NUM_THREADS"] = "8"
        env["OMP_PROC_BIND"] = "spread"
        env["OMP_PLACES"] = "cores"
        log_path = os.path.join(rdir, f"{name}.stdout.log")
        with open(log_path, "w") as flog:
            rc = subprocess.run([BIN_OMP, "-i", ath_path], cwd=rdir, env=env,
                                stdout=flog, stderr=subprocess.STDOUT, check=False).returncode
        if rc != 0:
            raise RuntimeError(f"AthenaK run {name} failed (rc={rc}), see {log_path}")

    arr = np.fromfile(traj_path, dtype=np.float64).reshape(-1, 8)
    arr = arr[np.all(np.isfinite(arr), axis=1)]
    trajs = {}
    tags = arr[:, 1].astype(np.int64)
    for k in range(39):
        sub = arr[tags == k]
        trajs[k] = (sub[:, 0], sub[:, 2:5], sub[:, 5:8])
    return trajs


def cks_r(x):
    # Vectorized Kerr-Schild radius for shape (N, 3)
    b = np.sum(x * x, axis=1) - A_SPIN * A_SPIN
    r2 = 0.5 * (b + np.sqrt(np.maximum(b * b + 4.0 * A_SPIN * A_SPIN * x[:, 2] * x[:, 2], 0.0)))
    return np.sqrt(np.maximum(r2, 0.0))


def measure_separatrix_ray(t, x):
    rs = cks_r(x)
    phi = np.unwrap(np.arctan2(x[:, 1], x[:, 0]))
    turns = np.abs(phi - phi[0]) / (2.0 * math.pi)
    # Check horizon entry (crossing r_+ + 0.01M inward) or return to r = 12.0M outbound
    ih = np.where(rs <= RP_BH + 0.01)[0]
    if len(ih):
        k = int(ih[0])
        if k > 0:
            frac = ((RP_BH + 0.01) - rs[k - 1]) / (rs[k] - rs[k - 1] - 1e-30)
            frac = min(max(frac, 0.0), 1.0)
            n_val = float(turns[k - 1] + frac * (turns[k] - turns[k - 1]))
        else:
            n_val = float(turns[0])
        return 1, n_val  # 1 = FALL-IN
    imin = int(np.argmin(rs))
    ie = np.where((np.arange(len(rs)) > imin) & (rs >= 12.0))[0]
    if len(ie):
        k = int(ie[0])
        frac = (12.0 - rs[k - 1]) / (rs[k] - rs[k - 1] + 1e-30)
        frac = min(max(frac, 0.0), 1.0)
        n_val = float(turns[k - 1] + frac * (turns[k] - turns[k - 1]))
        return 0, n_val  # 0 = ESCAPE
    return -1, float(turns[-1])  # STILL NEAR RING / INCONCLUSIVE


def measure_perched(t, x):
    rs = cks_r(x)
    phi = np.unwrap(np.arctan2(x[:, 1], x[:, 0]))
    turns = np.abs(phi - phi[0]) / (2.0 * math.pi)
    dev = np.abs(rs - R_PH_PRO)
    ib = np.where(dev >= 0.05)[0]
    if len(ib):
        k = int(ib[0])
        n_hold = float(turns[k])
        t_hold = float(t[k])
    else:
        n_hold = float(turns[-1])
        t_hold = float(t[-1])
    ih = np.where(rs <= RP_BH + 0.01)[0]
    fate = "FALL-IN" if len(ih) else ("BOUND" if rs[-1] < 2.0 else "ESCAPE")
    return rs, dev, turns, n_hold, t_hold, fate


def build_and_run():
    if os.path.exists(DATA_OUT) and os.environ.get("RERUN_LR", "0") != "1":
        print(f"Loading cached {DATA_OUT} (set RERUN_LR=1 to recompute)", flush=True)
        return dict(np.load(DATA_OUT))

    deltas_eq, xs, us = build_ic_catalog()
    deltas_arr = np.asarray(deltas_eq, dtype=np.float64)

    # Exact DOP853 reference for tags 0..31 and tag 32 perched
    dop_fates = np.zeros(32, dtype=np.int32)
    dop_turns = np.zeros(32, dtype=np.float64)
    for k in range(32):
        ts, xk, _ = integrate_null_dop853(xs[k], us[k], t_max=200.0, dt_out=0.02, stop_bounds=True)
        f, n = measure_separatrix_ray(ts, xk)
        dop_fates[k] = f
        dop_turns[k] = n

    configs = [
        ("gl4_dt02", "gl4", 0.02),
        ("gl4_dt05", "gl4", 0.05),
        ("gl4_dt10", "gl4", 0.10),
        ("mid_dt02", "midpoint", 0.02),
        ("mid_dt05", "midpoint", 0.05),
        ("mid_dt10", "midpoint", 0.10),
    ]
    results = {}
    out = dict(
        a_spin=np.float64(A_SPIN),
        rp_bh=np.float64(RP_BH),
        r_ph_pro=np.float64(R_PH_PRO),
        r_ph_ret=np.float64(R_PH_RET),
        r_sph=np.float64(R_SPH),
        xi_c_pro=np.float64(XI_C_PRO),
        xi_c_ret=np.float64(XI_C_RET),
        lam_ph_pro=np.float64(LAM_PH_PRO),
        turns_per_dec=np.float64(TURNS_PER_DEC),
        deltas=deltas_arr,
        dop_fates=dop_fates,
        dop_turns=dop_turns,
    )

    print("=== Kerr a=0.90 M Null Light-Ring & Fall-In Orbit Summary ===", flush=True)
    print(f"Analytic constants: r_+={RP_BH:.6f}M, r_ph+={R_PH_PRO:.6f}M (xi_c+={XI_C_PRO:.6f}), "
          f"r_ph-={R_PH_RET:.6f}M (xi_c-={XI_C_RET:.6f}), lam_ph+={LAM_PH_PRO:.5f}/M, "
          f"theory={TURNS_PER_DEC:.4f} turns/dec", flush=True)

    for lbl, vpush, dt in configs:
        trajs = run_athena_omp(f"lr_{lbl}", vpush, dt, tlim=200.0)
        fates = np.zeros(32, dtype=np.int32)
        turns = np.zeros(32, dtype=np.float64)
        for k in range(32):
            f, n = measure_separatrix_ray(trajs[k][0], trajs[k][1])
            fates[k] = f
            turns[k] = n
        flips = int(np.sum(fates != dop_fates))
        same = fates == dop_fates
        max_dn = float(np.max(np.abs(turns[same] - dop_turns[same]))) if np.any(same) else float("nan")
        med_dn = float(np.median(np.abs(turns[same] - dop_turns[same]))) if np.any(same) else float("nan")

        t32, x32, _ = trajs[32]
        rs32, dev32, turns32, n_hold, t_hold, fate32 = measure_perched(t32, x32)

        print(f"  {lbl:9s} (dt={dt:4.2f}M): sep flips={flips:2d}/32, "
              f"max|dN|={max_dn:.3e}, med|dN|={med_dn:.3e} | "
              f"perched: N_hold={n_hold:.2f} turns (t_hold={t_hold:6.2f}M, {fate32})", flush=True)

        st32 = max(1, len(t32) // 2500)
        out[f"{lbl}_fates"] = fates
        out[f"{lbl}_turns"] = turns
        out[f"{lbl}_p32_t"] = t32[::st32]
        out[f"{lbl}_p32_dev"] = dev32[::st32]
        out[f"{lbl}_nh"] = np.float64(n_hold)
        out[f"{lbl}_th"] = np.float64(t_hold)
        results[lbl] = (trajs, fates, turns)

    # Print per-delta detail for dt=0.05 and 0.10 so we verify exact separatrix breakdown point
    print("\nSeparatrix detail (delta_xi/xi_c+, exact fate, exact N_turns | gl4_dt05, mid_dt05, mid_dt10):")
    for k, d in enumerate(deltas_eq):
        fg5, ng5 = results["gl4_dt05"][1][k], results["gl4_dt05"][2][k]
        fm5, nm5 = results["mid_dt05"][1][k], results["mid_dt05"][2][k]
        fm1, nm1 = results["mid_dt10"][1][k], results["mid_dt10"][2][k]
        print(f"  tag={k:2d} d={d:+10.1e} exact=({dop_fates[k]},{dop_turns[k]:6.3f}) | "
              f"GL4_05=({fg5},{ng5:6.3f}) Mid_05=({fm5},{nm5:6.3f}) Mid_10=({fm1},{nm1:6.3f})", flush=True)

    # Save illustrative trajectories from gl4_dt02 (3D photon shell tag 33 + selected equatorial rays)
    tr_best = results["gl4_dt02"][0]
    st33 = max(1, len(tr_best[33][0]) // 3500)
    out["shell33_t"] = tr_best[33][0][::st33]
    out["shell33_x"] = tr_best[33][1][::st33]
    # Equatorial ray tags: fall-in (-1e-1:0, -1e-3:4, -1e-5:8), escape (+1e-5:23, +1e-3:27, +1e-1:31), retro (37, 38)
    for k in (0, 4, 8, 23, 27, 31, 37, 38):
        tk, xk, _ = tr_best[k]
        # truncate escape slightly past r=12M if desired; GL4 ran to tlim=200M so crop after r=12M outbound for clean plot
        rs_k = cks_r(xk)
        im = int(np.argmin(rs_k))
        io = np.where((np.arange(len(rs_k)) > im) & (rs_k > 12.2))[0]
        end_k = int(io[0]) + 1 if len(io) else len(xk)
        st = max(1, end_k // 1500)
        out[f"ray_{k}_x"] = xk[:end_k:st, :2]

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
    a = float(D["a_spin"])
    rp = float(D["rp_bh"])
    r_php = float(D["r_ph_pro"])
    r_phr = float(D["r_ph_ret"])

    fig = plt.figure(figsize=(8.6, 6.8))
    gs = fig.add_gridspec(2, 2, left=0.075, right=0.975, bottom=0.075, top=0.950,
                          wspace=0.28, hspace=0.31)

    # ------------------------------------------------------------------
    # Top-Left (3D): Spherical Photon Shell r_sph=2.20M + light rings
    # ------------------------------------------------------------------
    ax3d = fig.add_subplot(gs[0, 0], projection="3d")
    Xh, Yh, Zh = cks_surface(lambda th: np.full_like(th, rp), a, nth=28, nph=40)
    Xe, Ye, Ze = cks_surface(lambda th: 1.0 + np.sqrt(np.maximum(1.0 - a * a * np.cos(th) ** 2, 0.0)),
                             a, nth=28, nph=40)
    ax3d.plot_surface(Xh, Yh, Zh, color="0.10", alpha=0.96, shade=True, linewidth=0)
    ax3d.plot_surface(Xe, Ye, Ze, color=cz.PAL["orange"], alpha=0.14, linewidth=0.2,
                      edgecolors=(0.85, 0.45, 0.0, 0.14))

    ph = np.linspace(0.0, 2.0 * np.pi, 200)
    r_php_c = math.sqrt(r_php ** 2 + a * a)
    r_phr_c = math.sqrt(r_phr ** 2 + a * a)
    ax3d.plot(r_php_c * np.cos(ph), r_php_c * np.sin(ph), np.zeros_like(ph),
              color=cz.PAL["red"], lw=1.2, zorder=8)
    ax3d.plot(r_phr_c * np.cos(ph), r_phr_c * np.sin(ph), np.zeros_like(ph),
              color=cz.PAL["blue"], ls="--", lw=1.0, zorder=8)

    xs = D["shell33_x"]
    ts = D["shell33_t"]
    # Plot first t <= 75 M cleanly so the spherical shell stays crisp before Lyapunov drift
    m3 = ts <= 75.0
    xs_w, ts_w = xs[m3], ts[m3]
    pts3d = xs_w.reshape(-1, 1, 3)
    segs3d = np.concatenate([pts3d[:-1], pts3d[1:]], axis=1)
    lc3d = Line3DCollection(segs3d, cmap="viridis", norm=plt.Normalize(0.0, float(ts_w[-1])),
                            linewidth=1.15, alpha=0.92)
    lc3d.set_array(ts_w[:-1])
    ax3d.add_collection3d(lc3d)
    ax3d.set_xlim(-4.2, 4.2)
    ax3d.set_ylim(-4.2, 4.2)
    ax3d.set_zlim(-2.6, 2.6)
    ax3d.set_xticks([-4, -2, 0, 2, 4])
    ax3d.set_yticks([-4, -2, 0, 2, 4])
    ax3d.set_zticks([-2, 0, 2])
    ax3d.set_box_aspect((1.0, 1.0, 0.65))
    ax3d.view_init(elev=24, azim=35)
    ax3d.set_xlabel(r"$x\,[M]$", labelpad=2, fontsize=8.0)
    ax3d.set_ylabel(r"$y\,[M]$", labelpad=2, fontsize=8.0)
    ax3d.set_zlabel(r"$z\,[M]$", labelpad=1, fontsize=8.0)
    ax3d.tick_params(labelsize=6.8, pad=0)
    ax3d.text2D(0.02, 0.99,
                r"3D photon shell ($a=0.9M$, $r_{\rm sph}=2.20M$, $\mathrm{GL4}$)" "\n"
                r"Eq. rings: $r_{\rm ph}^+=1.56M$ (red), $r_{\rm ph}^-=3.91M$ (blue)",
                transform=ax3d.transAxes, ha="left", va="top", fontsize=6.2)

    # ------------------------------------------------------------------
    # Top-Right (2D): Equatorial Light-Ring Separatrix (Fall-in vs Escape)
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    r_hor_eq = math.sqrt(rp * rp + a * a)
    r_erg_eq = math.sqrt(4.0 + a * a)
    ax.fill(r_hor_eq * np.cos(ph), r_hor_eq * np.sin(ph), color="0.12", zorder=6, label=r"Horizon $r_+$")
    ax.plot(r_php_c * np.cos(ph), r_php_c * np.sin(ph), color="k", ls="-", lw=1.0, zorder=5,
            label=r"Prograde $r_{\rm ph}^+$")
    ax.plot(r_erg_eq * np.cos(ph), r_erg_eq * np.sin(ph), color=cz.PAL["orange"], ls="--", lw=1.0, zorder=4,
            label=r"Ergosphere $r_{\rm ergo}$")
    ax.plot(r_phr_c * np.cos(ph), r_phr_c * np.sin(ph), color="0.45", ls=":", lw=1.0, zorder=4,
            label=r"Retrograde $r_{\rm ph}^-$")

    # Prograde fall-in (blue) vs escape (red) rays
    ray_specs = [
        (0,  cz.PAL["blue"],  "-.", 1.1, r"Fall-in $\delta\xi/\xi_c^+=-10^{-1}$"),
        (8,  cz.PAL["blue"],  "-",  1.35, r"Fall-in $\delta\xi/\xi_c^+=-10^{-5}$"),
        (23, cz.PAL["red"],   "-",  1.35, r"Escape $\delta\xi/\xi_c^+=+10^{-5}$"),
        (31, cz.PAL["red"],   "-.", 1.1, r"Escape $\delta\xi/\xi_c^+=+10^{-1}$"),
        (37, cz.PAL["green"], ":",  1.15, r"Retro. $\pm 10^{-3}$ ($r_{\rm ph}^-$)"),
        (38, cz.PAL["green"], ":",  1.15, None),
    ]
    for rk, col, ls, lw, lbl in ray_specs:
        xy = D[f"ray_{rk}_x"]
        ax.plot(xy[:, 0], xy[:, 1], color=col, ls=ls, lw=lw, zorder=3, label=lbl)

    ax.set_xlim(-9.2, 7.5)
    ax.set_ylim(-6.2, 6.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$")
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="upper left", fontsize=5.0, frameon=False, ncol=1)

    # ------------------------------------------------------------------
    # Bottom-Left: Fall-in & Escape Orbit Number N_turns vs |dxi / xi_c+|
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    deltas = D["deltas"]
    neg = deltas < 0.0
    pos = deltas > 0.0
    dx_neg = np.abs(deltas[neg])
    dx_pos = np.abs(deltas[pos])

    ax.semilogx(dx_neg, D["dop_turns"][neg], color=cz.PAL["blue"], lw=1.6, ls="-", label=r"Exact fall-in ($\mathrm{DOP853}$)")
    ax.semilogx(dx_pos, D["dop_turns"][pos], color=cz.PAL["red"], lw=1.6, ls="-", label=r"Exact escape ($\mathrm{DOP853}$)")

    # Overlay matched dt = 0.05 M: GL4 (open circles, 0 flips) vs Midpoint (squares / x flips)
    for mask, dfate, col_m, tag_l in [(neg, 1, cz.PAL["blue"], "fall-in"), (pos, 0, cz.PAL["red"], "escape")]:
        ok_g = D["gl4_dt05_fates"][mask] == dfate
        bad_g = ~ok_g
        d_sub = np.abs(deltas[mask])
        t_g = D["gl4_dt05_turns"][mask]
        if np.any(ok_g):
            ax.semilogx(d_sub[ok_g], t_g[ok_g], "o", color=col_m, mfc="none", ms=5.0, mew=1.0, zorder=5,
                        label=rf"$\mathrm{{GL4}}$ ($\Delta t=0.05M$)" if tag_l == "fall-in" else None)
        if np.any(bad_g):
            ax.semilogx(d_sub[bad_g], t_g[bad_g], "X", color=col_m, ms=6.0, zorder=7)

        ok_m = D["mid_dt05_fates"][mask] == dfate
        bad_m = ~ok_m
        t_m = D["mid_dt05_turns"][mask]
        if np.any(ok_m):
            ax.semilogx(d_sub[ok_m], t_m[ok_m], "s", color=cz.PAL["orange"] if tag_l == "fall-in" else cz.PAL["green"],
                        ms=3.6, zorder=4, label=r"Midpoint ($\Delta t=0.05M$)" if tag_l == "fall-in" else None)
        if np.any(bad_m):
            ax.semilogx(d_sub[bad_m], t_m[bad_m], "x", color="k", ms=6.2, mew=1.5, zorder=8,
                        label=r"Midpoint false capture" if tag_l == "escape" else None)

    ax.invert_xaxis()
    ax.set_xlim(2.0e-1, 1.5e-9)
    ax.set_ylim(0.2, 8.6)
    ax.set_xlabel(r"Impact-parameter offset $|\delta\xi/\xi_c^+|$")
    ax.set_ylabel(r"Orbit number $N_{\rm turns} = |\Delta\phi|/(2\pi)$")
    ax.text(0.04, 0.95, rf"Slope $\approx {float(D['turns_per_dec']):.3f}$ turns/dec",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.1, color="0.22")
    ax.legend(loc="lower right", fontsize=5.2, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Right: Perched Light-Ring Lyapunov Divergence & Hold Turns
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    curves = [
        ("mid_dt10", cz.PAL["orange"], ":",  1.35, r"Midpoint $\Delta t=0.10M$"),
        ("mid_dt05", cz.PAL["green"],  "-.", 1.25, r"Midpoint $\Delta t=0.05M$"),
        ("mid_dt02", cz.PAL["blue"],   "--", 1.25, r"Midpoint $\Delta t=0.02M$"),
        ("gl4_dt10", cz.PAL["red"],    ":",  1.35, r"$\mathrm{GL4}$ $\Delta t=0.10M$"),
        ("gl4_dt05", cz.PAL["red"],    "--", 1.35, r"$\mathrm{GL4}$ $\Delta t=0.05M$"),
        ("gl4_dt02", cz.PAL["red"],    "-",  1.6,  r"$\mathrm{GL4}$ $\Delta t=0.02M$"),
    ]
    for lbl, col, ls, lw, desc in curves:
        nh = float(D[f"{lbl}_nh"])
        ax.semilogy(D[f"{lbl}_p32_t"], np.maximum(D[f"{lbl}_p32_dev"], 1.0e-15),
                    color=col, ls=ls, lw=lw, label=rf"{desc} ($N_{{\rm hold}}={nh:.2f}$)")

    # Analytical Lyapunov guide exp(+lam_ph * t)
    tg = np.linspace(35.0, 155.0, 100)
    lam = float(D["lam_ph_pro"])
    ax.semilogy(tg, 1.0e-12 * np.exp(lam * (tg - 35.0)), color="0.3", ls="-", lw=1.0, alpha=0.65,
                label=rf"Exact $\propto e^{{\lambda t}}$ ($\lambda={lam:.4f}\,M^{{-1}}$)")

    ax.set_xlim(0.0, 200.0)
    ax.set_ylim(1.0e-15, 3.0)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Light-ring offset $|r(t) - r_{\rm ph}^+|\,[M]$")
    ax.legend(loc="lower right", fontsize=5.1, frameon=False, ncol=1)

    ax_top = ax.twiny()
    ax_top.set_xlim(0.0, 200.0 * OM_PH_PRO / (2.0 * math.pi))
    ax_top.set_xlabel(r"Light-ring orbits $\Omega_{\rm ph}^+ t/(2\pi)$", fontsize=7.6, labelpad=3)
    ax_top.tick_params(labelsize=6.8, direction="in")

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"Saved {FIG_OUT}.{{pdf,png}}", flush=True)


if __name__ == "__main__":
    main()
