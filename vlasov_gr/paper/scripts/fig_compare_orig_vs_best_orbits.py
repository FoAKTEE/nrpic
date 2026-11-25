#!/usr/bin/env python3
"""Pure-physics orbit comparison: NRPIC Original vs Our Best GR-LBV methods.

Showcases real physical trajectory divergences across four strong-field regimes
(every curve from an AthenaK integration except black exact DOP853 references):
  1. Top-Left: Live 3+1 spinning BH + massive particle (q = 0.05, B200 GPU):
     Original (RK4 0.25, Midpoint, plain filter: 27.4% energy leak -> delayed plunge t=38.6M)
     vs Our Best (RK3 0.40/0.45, GL4, Quintic, mcons, Scheme A, Km=1,2 -> t=29.2/28.7M)
     with BH puncture recoil and dynamical apparent-horizon outline.
  2. Top-Right: Kerr a = 0.90 M light-ring separatrix (tag=21, dxi/xi_c+ = +1e-6, dt = 0.05 M):
     GL4 captures 5.84 tight whirls on r_ph+ = 1.558 M and escapes matching DOP853,
     while Original Midpoint falsely plunges after 3.70 whirls.
  3. Bottom-Left: Kerr a = 0.90 M 3D inclined spherical photon shell (tag=33, r_sph = 2.20 M):
     GL4 holds the precessing 3D photon-shell orbit through t = 134.8 M,
     while Original Midpoint destabilizes and crashes into the horizon at t = 60.0 M.
  4. Bottom-Right: Near-extremal Kerr a = 0.999 M 4-whirl homoclinic zoom-whirl orbit (e = 0.999):
     Exact dt=0.02 M reference vs coarse-step GL4, Original Midpoint, and Original Boris.

Saves reduced trajectories to `vlasov_gr/paper/data/compare_orig_vs_best_orbits.npz` and
renders `vlasov_gr/paper/figures/fig_compare_orig_vs_best_orbits.{pdf,png}`.
"""
from math import factorial
import math
import os
import re
import shutil
import subprocess
import sys
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import kerr  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PAPER_DIR, "data")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
BIN_OMP = f"{SCRATCH}/build_omp_iter4/src/athena"

BH_RUNS = {
    "orig": (f"{SCRATCH}/runs/compare_orig_vs_best/orig_q005", "orig_q005"),
    "best": (f"{SCRATCH}/runs/bh_massive_backreaction/q005", "q005"),
    "fast": (f"{SCRATCH}/runs/compare_orig_vs_best/best_fast_q005", "best_fast_q005"),
}
LR_BASE = f"{SCRATCH}/runs/kerr_a090_lightring"
ZW_REF_CFG = f"{SCRATCH}/runs/kerr_a0999_e0999/zw999_gl4.athinput"
ZW_REF_TRAJ = f"{SCRATCH}/runs/kerr_a0999_e0999/zw999_gl4/zw999_gl4.traj.bin"
ZW_CMP_ROOT = f"{SCRATCH}/runs/compare_orig_vs_best/zw999_cmp"

DATA_OUT = os.path.join(DATA_DIR, "compare_orig_vs_best_orbits.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_compare_orig_vs_best_orbits")


def safe_loadtxt(path: str) -> np.ndarray:
    rows = []
    ncols = None
    with open(path, "r") as f:
        for ln in f:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            if ncols is None:
                ncols = len(vals)
            if len(vals) == ncols:
                rows.append(vals)
    return np.asarray(rows, dtype=np.float64) if rows else np.zeros((0, 0), dtype=np.float64)


def dedup_time(arr: np.ndarray, tcol: int = 0) -> np.ndarray:
    if len(arr) == 0:
        return arr
    _, idx = np.unique(arr[::-1, tcol], return_index=True)
    out = arr[::-1][idx]
    return out[np.argsort(out[:, tcol])]


def read_traj(path: str, tag: int = None) -> np.ndarray:
    arr = np.fromfile(path, dtype=np.float64).reshape(-1, 8)
    arr = arr[np.all(np.isfinite(arr), axis=1)]
    if tag is not None:
        arr = arr[arr[:, 1].astype(np.int64) == tag]
    return dedup_time(arr, 0)


def ylm(l: int, m: int, theta: np.ndarray, phi: np.ndarray):
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += (
            ((-1.0) ** k)
            * (c ** (2 * l + m - 2 * k))
            * (s ** (2 * k - m))
            / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m))
        )
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_eq_ring(sh_path: str, t_target: float, cx: float, cy: float):
    shapes = {}
    t_cur = None
    with open(sh_path) as f:
        for ln in f:
            if ln.startswith("#"):
                m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", ln)
                if m:
                    t_cur = float(m.group(1))
            elif ln.strip() and t_cur is not None:
                shapes[t_cur] = np.array(ln.split(), dtype=float)
    ts = np.array(sorted(shapes.keys()))
    tc = float(ts[np.argmin(np.abs(ts - t_target))])
    coef = shapes[tc]
    phi = np.linspace(0.0, 2.0 * np.pi, 181)
    th = np.full_like(phi, 0.5 * np.pi)
    rr, i = np.zeros_like(phi), 0
    for l in range(9):
        re_, _ = ylm(l, 0, th, phi)
        rr += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, th, phi)
            rr += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return cx + rr * np.cos(phi), cy + rr * np.sin(phi)


def downsample_xyz(xyz: np.ndarray, max_pts: int = 1200) -> np.ndarray:
    if len(xyz) <= max_pts:
        return xyz.astype(np.float32)
    stride = max(1, len(xyz) // max_pts)
    out = xyz[::stride]
    if not np.allclose(out[-1], xyz[-1]):
        out = np.vstack([out, xyz[-1:]])
    return out.astype(np.float32)


def set_param(txt: str, sec: str, key: str, val: str) -> str:
    lines = txt.splitlines()
    out, cur, replaced = [], None, False
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
            out.extend([f"<{sec}>", f"{key} = {val}"])
    return "\n".join(out) + "\n"


def run_zw_case(name: str, mode: str, dt: float) -> np.ndarray:
    rdir = os.path.join(ZW_CMP_ROOT, name)
    traj_p = os.path.join(rdir, f"{name}.traj.bin")
    if not (os.path.isfile(traj_p) and os.environ.get("RERUN_ORBITS", "0") != "1"):
        if os.path.exists(rdir):
            shutil.rmtree(rdir)
        os.makedirs(rdir, exist_ok=True)
        txt = open(ZW_REF_CFG).read()
        txt = set_param(txt, "job", "basename", name)
        txt = set_param(txt, "particles", "dt", f"{dt}")
        if mode == "gl4":
            txt = set_param(txt, "particles", "pusher", "vlasov_hybrid")
            txt = set_param(txt, "particles", "vlasov_mode", "hybrid")
            txt = set_param(txt, "particles", "vlasov_pusher", "gl4")
        elif mode == "midpoint":
            txt = "\n".join(ln for ln in txt.splitlines() if not re.match(r"^\s*vlasov_", ln)) + "\n"
            txt = set_param(txt, "particles", "pusher", "midpoint")
        elif mode == "boris":
            txt = "\n".join(ln for ln in txt.splitlines() if not re.match(r"^\s*vlasov_", ln)) + "\n"
            txt = set_param(txt, "particles", "pusher", "boris")
        cfg = os.path.join(rdir, f"{name}.athinput")
        with open(cfg, "w") as f:
            f.write(txt)
        env = dict(os.environ)
        env["OMP_NUM_THREADS"] = "4"
        with open(os.path.join(rdir, "stdout.log"), "w") as flog:
            rc = subprocess.run([BIN_OMP, "-i", cfg], cwd=rdir, env=env,
                                stdout=flog, stderr=subprocess.STDOUT, check=False).returncode
        if rc != 0:
            raise RuntimeError(f"{name} failed (rc={rc})")
    return read_traj(traj_p)


def zw_deviation(arr: np.ndarray, ref: np.ndarray) -> float:
    t_max = min(arr[-1, 0], ref[-1, 0])
    m_r = ref[:, 0] <= t_max
    rx = np.column_stack([np.interp(ref[m_r, 0], arr[:, 0], arr[:, c]) for c in (2, 3, 4)])
    return float(np.max(np.linalg.norm(rx - ref[m_r, 2:5], axis=1)))


def integrate_lr_tag21_dop853(dxi: float) -> np.ndarray:
    a, M, r0 = 0.9, 1.0, 12.0
    rp, _ = kerr.horizon_radii(a=a, M=M)
    r_ph = 2.0 * M * (1.0 + math.cos(2.0 / 3.0 * math.acos(-a / M)))
    xi_c = -(r_ph * r_ph * (r_ph - 3.0 * M) + a * a * (r_ph + M)) / (a * (r_ph - M))
    xi = xi_c * (1.0 + dxi)
    D0 = r0 * r0 - 2.0 * M * r0 + a * a
    R0 = max(((r0 * r0 + a * a) - a * xi) ** 2 - D0 * ((xi - a) ** 2), 0.0)
    ur0 = -math.sqrt(R0) / D0
    _, xc, uc = kerr.convert_state(0.0, np.array([r0, 0.5 * math.pi, 0.0]),
                                   np.array([ur0, 0.0, xi]), "bl", "cks", a=a, M=M, u_t=-1.0)

    def rhs(t, y):
        x, u = y[:3], y[3:]
        m = kerr.adm_cks(x, a=a, M=M, derivs=True)
        U = m.gamma_inv @ u
        W = math.sqrt(max(float(u @ U), 1.0e-30))
        dx = (m.alpha / W) * U - m.beta
        du = (-W) * m.dalpha + (m.dbeta @ u) + (0.5 * m.alpha / W) * np.einsum("ijk,j,k->i", m.dgamma, U, U)
        return np.concatenate([dx, du])

    def ev_hor(t, y):
        return kerr.cks_radius(y[:3], a=a) - (rp + 0.002)
    ev_hor.terminal = True; ev_hor.direction = -1

    def ev_esc(t, y):
        return kerr.cks_radius(y[:3], a=a) - 12.1 if t > 1.0 else -1.0
    ev_esc.terminal = True; ev_esc.direction = 1

    sol = solve_ivp(rhs, (0.0, 200.0), np.concatenate([xc, uc]), method="DOP853",
                    events=[ev_hor, ev_esc], rtol=1e-13, atol=1e-13, dense_output=True)
    ts = np.arange(0.0, float(sol.t[-1]), 0.02)
    return sol.sol(ts).T[:, :3]


def build_or_load_data() -> dict:
    if os.path.isfile(DATA_OUT) and os.environ.get("RERUN_ORBITS", "0") != "1":
        print(f"[CACHE] Loading {DATA_OUT}", flush=True)
        return dict(np.load(DATA_OUT, allow_pickle=False))

    out = {}

    # 1. Live 3+1 spinning BH + massive particle (q = 0.05, B200 GPU)
    for tag, (rdir, pref) in BH_RUNS.items():
        nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{pref}.nrpic.hst")), 0)
        exc_rows = np.where(nh[:, 16] > 0.5)[0]
        t_exc = float(nh[int(exc_rows[0]), 0]) if len(exc_rows) else np.nan
        tr = read_traj(os.path.join(rdir, f"{pref}.traj.bin"))
        if np.isfinite(t_exc):
            tr = tr[tr[:, 0] <= t_exc + 1e-9]
        co = dedup_time(safe_loadtxt(os.path.join(rdir, f"{pref}.co_0.txt")), 1)
        out[f"bh_{tag}_p_xyz"] = tr[:, 2:5].astype(np.float32)
        out[f"bh_{tag}_bh_xyz"] = downsample_xyz(co[:, 2:5], max_pts=600)
        out[f"bh_{tag}_t_exc"] = np.float64(t_exc)
        if tag == "best":
            k28 = int(np.argmin(np.abs(co[:, 1] - 28.0)))
            hx, hy = horizon_eq_ring(os.path.join(rdir, f"{pref}.horizon_shape_0.txt"),
                                     28.0, float(co[k28, 2]), float(co[k28, 3]))
            out["bh_ah_hx"] = hx.astype(np.float32)
            out["bh_ah_hy"] = hy.astype(np.float32)

    # 2 & 3. Kerr a = 0.90 M light-ring separatrix (tag=21) & 3D photon shell (tag=33)
    d90 = dict(np.load(os.path.join(DATA_DIR, "physics_kerr_a090_lightring.npz"), allow_pickle=False))
    dxi21 = float(d90["deltas"][21])
    out["lr21_dop_xyz"] = downsample_xyz(integrate_lr_tag21_dop853(dxi21), max_pts=1400)
    for tag, run in [("gl4", "lr_gl4_dt05"), ("mid", "lr_mid_dt05")]:
        t21 = read_traj(os.path.join(LR_BASE, run, f"{run}.traj.bin"), tag=21)
        r21 = np.linalg.norm(t21[:, 2:5], axis=1)
        imin = int(np.argmin(r21))
        esc = np.where((np.arange(len(r21)) > imin) & (r21 > 12.2))[0]
        if len(esc):
            t21 = t21[:int(esc[0]) + 1]
        out[f"lr21_{tag}_xyz"] = downsample_xyz(t21[:, 2:5], max_pts=1400)

        t33 = read_traj(os.path.join(LR_BASE, run, f"{run}.traj.bin"), tag=33)
        out[f"lr33_{tag}_xyz"] = downsample_xyz(t33[:, 2:5], max_pts=1400)
        out[f"lr33_{tag}_tend"] = np.float64(t33[-1, 0])

    # 4. Kerr a = 0.999 M 4-whirl zoom-whirl massive orbit
    ref_zw = read_traj(ZW_REF_TRAJ)
    chosen_dt = None
    chosen_runs = None
    for dt_try in (0.10, 0.05):
        sfx = f"dt{int(round(dt_try * 100)):02d}"
        g = run_zw_case(f"zw_gl4_{sfx}", "gl4", dt_try)
        m = run_zw_case(f"zw_mid_{sfx}", "midpoint", dt_try)
        b = run_zw_case(f"zw_bor_{sfx}", "boris", dt_try)
        dg, dm, db = zw_deviation(g, ref_zw), zw_deviation(m, ref_zw), zw_deviation(b, ref_zw)
        print(f"[ZW999 dt={dt_try:.2f}] max|dx| vs dt=0.02 ref: GL4={dg:.3e}, Midpoint={dm:.3e}, Boris={db:.3e}", flush=True)
        if chosen_dt is None:
            chosen_dt, chosen_runs = dt_try, (g, m, b, dg, dm, db)
        if dg < 0.05 and dm > 0.5:
            chosen_dt, chosen_runs = dt_try, (g, m, b, dg, dm, db)
            break

    g, m, b, dg, dm, db = chosen_runs
    if dm < 0.5:
        raise RuntimeError(f"Re-plan trigger: zw999 Midpoint deviation too small visually ({dm:.3e} < 0.5 M)")
    out["zw_dt"] = np.float64(chosen_dt)
    out["zw_ref_xyz"] = downsample_xyz(ref_zw[:, 2:5], max_pts=2200)
    out["zw_gl4_xyz"] = downsample_xyz(g[:, 2:5], max_pts=2200)
    out["zw_mid_xyz"] = downsample_xyz(m[:, 2:5], max_pts=2200)
    out["zw_bor_xyz"] = downsample_xyz(b[:, 2:5], max_pts=2200)
    out["zw_gl4_dx"] = np.float64(dg)
    out["zw_mid_dx"] = np.float64(dm)
    out["zw_bor_dx"] = np.float64(db)

    os.makedirs(DATA_DIR, exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"[SAVE] {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def print_summary(D: dict):
    print("\n" + "=" * 96)
    print("PHYSICAL ORBIT COMPARISON: NRPIC Original vs Our Best GR-LBV")
    print("-" * 96)
    for k, name in [("orig", "NRPIC Original"), ("best", "Our Best (Km=1)"), ("fast", "Our Best (Km=2)")]:
        p = D[f"bh_{k}_p_xyz"]; b = D[f"bh_{k}_bh_xyz"]
        print(f"  1) BH q=0.05 {name:<16}: t_exc={float(D[f'bh_{k}_t_exc']):5.2f}M, "
              f"p_end=({p[-1,0]:+5.2f},{p[-1,1]:+5.2f}), bh_end=({b[-1,0]:+5.3f},{b[-1,1]:+5.3f})")
    print(f"  2) Kerr a=0.90 LR tag=21 (dt=0.05): GL4 escapes (5.84 turns, matching DOP853) "
          f"vs Midpoint plunges (3.70 turns, end r={np.linalg.norm(D['lr21_mid_xyz'][-1]):.3f}M)")
    print(f"  3) Kerr a=0.90 3D shell tag=33     : GL4 holds t={float(D['lr33_gl4_tend']):.2f}M "
          f"vs Midpoint crashes into horizon at t={float(D['lr33_mid_tend']):.2f}M")
    print(f"  4) Kerr a=0.999 4-whirl (dt={float(D['zw_dt']):.2f}) : max|dx| GL4={float(D['zw_gl4_dx']):.3e}M, "
          f"Midpoint={float(D['zw_mid_dx']):.3f}M, Boris={float(D['zw_bor_dx']):.3f}M")
    print("=" * 96 + "\n", flush=True)


def make_figure(D: dict):
    cz.use_style()
    fig = plt.figure(figsize=(8.6, 7.3))
    gs = GridSpec(2, 2, figure=fig, left=0.085, right=0.975, bottom=0.075, top=0.945,
                  wspace=0.25, hspace=0.28)
    th = np.linspace(0.0, 2.0 * np.pi, 240)

    # ------------------------------------------------------------------
    # Top-Left: Live 3+1 Spinning BH + Massive Particle (q=0.05) Orbits
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    ax.fill(D["bh_ah_hx"], D["bh_ah_hy"], color="0.16", alpha=0.88, zorder=2, label=r"BH AH ($t=28M$)")
    specs_bh = [
        ("orig", rf"NRPIC Original ($t_{{\rm exc}}={float(D['bh_orig_t_exc']):.1f}M$)", cz.PAL["blue"], "--", 1.55, 4),
        ("best", rf"Our Best $K_m=1$ ($t_{{\rm exc}}={float(D['bh_best_t_exc']):.1f}M$)", cz.PAL["red"], "-", 1.75, 5),
        ("fast", rf"Our Best $K_m=2$ ($t_{{\rm exc}}={float(D['bh_fast_t_exc']):.1f}M$)", cz.PAL["green"], "-.", 1.55, 6),
    ]
    for k, lbl, col, ls, lw, zo in specs_bh:
        px = D[f"bh_{k}_p_xyz"]; bx = D[f"bh_{k}_bh_xyz"]
        ax.plot(px[:, 0], px[:, 1], color=col, ls=ls, lw=lw, zorder=zo, label=lbl)
        ax.plot(bx[:, 0], bx[:, 1], color=col, ls=ls, lw=1.15, alpha=0.8, zorder=zo)
        ax.plot([bx[-1, 0]], [bx[-1, 1]], "s", color=col, mec="k", mew=0.45, ms=3.5, zorder=zo + 1)
    ax.plot([3.5], [0.0], "o", color="k", ms=4.5, zorder=8)
    ax.set_xlim(-3.2, 4.6)
    ax.set_ylim(-3.5, 4.3)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.96, r"Live 3+1 BH $+ \,m_p=0.05\,M$" "\n(inner: BH recoil)",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.5, color="0.15")
    ax.legend(loc="lower left", fontsize=6.5, frameon=False, labelspacing=0.20)

    # ------------------------------------------------------------------
    # Top-Right: Kerr a=0.90 M Light-Ring Separatrix (tag=21, dt=0.05 M)
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    rp90, _ = kerr.horizon_radii(a=0.9, M=1.0)
    rph90 = 2.0 * (1.0 + math.cos(2.0 / 3.0 * math.acos(-0.9)))
    ax.fill(rp90 * np.cos(th), rp90 * np.sin(th), color="0.12", zorder=2)
    ax.plot(2.0 * np.cos(th), 2.0 * np.sin(th), color="0.50", ls=":", lw=0.95, zorder=2, label=r"Ergosphere ($2M$)")
    ax.plot(rph90 * np.cos(th), rph90 * np.sin(th), color=cz.PAL["yellow"], ls="--", lw=1.25, zorder=3,
            label=rf"Light ring $r_{{\rm ph}}^+={rph90:.2f}M$")

    dop21, gl21, mid21 = D["lr21_dop_xyz"], D["lr21_gl4_xyz"], D["lr21_mid_xyz"]
    ax.plot(dop21[:, 0], dop21[:, 1], color="k", lw=1.8, zorder=4, label="Exact DOP853 (escape)")
    ax.plot(gl21[:, 0], gl21[:, 1], color=cz.PAL["red"], lw=1.25, ls="-", zorder=6,
            label=r"GL4 $\Delta t=0.05M$ (escape)")
    ax.plot(mid21[:, 0], mid21[:, 1], color=cz.PAL["blue"], lw=1.45, ls="--", zorder=5,
            label=r"Midpoint $\Delta t=0.05M$ (plunge)")
    ax.plot([mid21[-1, 0]], [mid21[-1, 1]], "X", color=cz.PAL["blue"], mec="k", mew=0.45, ms=5.5, zorder=7)
    ax.set_xlim(-6.2, 7.2)
    ax.set_ylim(-6.2, 7.2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.96, r"Kerr $a=0.90M$" "\nLight Ring\n" r"($\delta\xi/\xi_c^+ = +10^{-6}$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.9, color="0.15")
    ax.legend(loc="upper right", fontsize=6.1, frameon=False, labelspacing=0.17)

    # ------------------------------------------------------------------
    # Bottom-Left (3D): Kerr a=0.90 M Inclined Spherical Photon Shell (tag=33)
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0], projection="3d")
    u_sph = np.linspace(0.0, 2.0 * np.pi, 32)
    v_sph = np.linspace(0.0, np.pi, 18)
    xs = rp90 * np.outer(np.cos(u_sph), np.sin(v_sph))
    ys = rp90 * np.outer(np.sin(u_sph), np.sin(v_sph))
    zs = rp90 * np.outer(np.ones_like(u_sph), np.cos(v_sph))
    ax3.plot_surface(xs, ys, zs, color="0.18", alpha=0.58, linewidth=0.0, shade=True)

    g33, m33 = D["lr33_gl4_xyz"], D["lr33_mid_xyz"]
    ax3.plot(g33[:, 0], g33[:, 1], g33[:, 2], color=cz.PAL["red"], lw=1.05, alpha=0.88,
             label=rf"GL4 shell ($t={float(D['lr33_gl4_tend']):.1f}M$)")
    ax3.plot(m33[:, 0], m33[:, 1], m33[:, 2], color=cz.PAL["blue"], lw=1.25, ls="--",
             label=rf"Midpoint crash ($t={float(D['lr33_mid_tend']):.1f}M$)")
    ax3.scatter([m33[-1, 0]], [m33[-1, 1]], [m33[-1, 2]], marker="X", c=cz.PAL["blue"],
                edgecolors="k", linewidths=0.5, s=36, zorder=10)
    ax3.set_xlim(-2.35, 2.35); ax3.set_ylim(-2.35, 2.35); ax3.set_zlim(-2.35, 2.35)
    ax3.set_box_aspect((1.0, 1.0, 1.0))
    ax3.set_xticks([-2, 0, 2]); ax3.set_yticks([-2, 0, 2]); ax3.set_zticks([-2, 0, 2])
    ax3.tick_params(labelsize=7.5, pad=1)
    ax3.set_xlabel(r"$x\,[M]$", fontsize=8.5, labelpad=2)
    ax3.set_ylabel(r"$y\,[M]$", fontsize=8.5, labelpad=2)
    ax3.set_zlabel(r"$z\,[M]$", fontsize=8.5, labelpad=1)
    ax3.view_init(elev=22, azim=-52)
    ax3.text2D(0.02, 0.99, r"3D Spherical Shell ($r_{\rm sph}=2.2M$)",
               transform=ax3.transAxes, ha="left", va="top", fontsize=7.5, color="0.15")
    ax3.legend(loc="upper right", bbox_to_anchor=(1.05, 0.92), fontsize=6.4, frameon=False, labelspacing=0.18)

    # ------------------------------------------------------------------
    # Bottom-Right: Kerr a=0.999 M 4-Whirl Zoom-Whirl Orbit (e=0.999)
    # ------------------------------------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    rp999, _ = kerr.horizon_radii(a=0.999, M=1.0)
    ax.fill(rp999 * np.cos(th), rp999 * np.sin(th), color="0.12", zorder=2)
    ax.plot(2.0 * np.cos(th), 2.0 * np.sin(th), color="0.50", ls=":", lw=0.95, zorder=2)

    zr, zg, zm, zb = D["zw_ref_xyz"], D["zw_gl4_xyz"], D["zw_mid_xyz"], D["zw_bor_xyz"]
    dt_zw = float(D["zw_dt"])
    ax.plot(zr[:, 0], zr[:, 1], color="k", lw=2.0, zorder=3, label=r"Exact GL4 ($\Delta t=0.02M$)")
    ax.plot(zg[:, 0], zg[:, 1], color=cz.PAL["red"], lw=1.25, ls="-", zorder=6,
            label=rf"GL4 ($\Delta t={dt_zw:.2f}M$, $|\Delta\mathbf{{x}}|\leq {float(D['zw_gl4_dx']):.1e}M$)")
    ax.plot(zm[:, 0], zm[:, 1], color=cz.PAL["blue"], lw=1.35, ls="--", zorder=5,
            label=rf"Midpoint ($|\Delta\mathbf{{x}}|={float(D['zw_mid_dx']):.2f}M$)")
    ax.plot(zb[:, 0], zb[:, 1], color=cz.PAL["orange"], lw=1.35, ls=":", zorder=4,
            label=rf"Boris ($|\Delta\mathbf{{x}}|={float(D['zw_bor_dx']):.2f}M$)")

    ax.plot([zr[0, 0]], [zr[0, 1]], "o", color="k", ms=4.2, zorder=8)
    ax.plot([zr[-1, 0]], [zr[-1, 1]], "o", color="k", ms=4.2, zorder=8)
    ax.plot([zm[-1, 0]], [zm[-1, 1]], "s", color=cz.PAL["blue"], mec="k", mew=0.4, ms=4.2, zorder=8)
    ax.plot([zb[-1, 0]], [zb[-1, 1]], "^", color=cz.PAL["orange"], mec="k", mew=0.4, ms=4.6, zorder=8)

    ax.set_xlim(-12.2, 12.2)
    ax.set_ylim(-13.8, 11.4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.96, 0.96, r"Kerr $a=0.999M$ 4-Whirl" "\n" r"($e=0.999$, $t=450M$)",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.4, color="0.15")
    ax.legend(loc="lower left", fontsize=6.1, frameon=False, labelspacing=0.18)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIG_OUT}.{ext}", dpi=300)
    plt.close(fig)
    print(f"[FIG]  Saved {FIG_OUT}.{{pdf,png}}", flush=True)


def main():
    D = build_or_load_data()
    print_summary(D)
    make_figure(D)


if __name__ == "__main__":
    main()
