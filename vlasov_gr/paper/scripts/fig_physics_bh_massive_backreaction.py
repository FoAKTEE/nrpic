#!/usr/bin/env python3
"""Massive-particle dynamical gravitational back-reaction around a spinning BH puncture.

Runs 4 full 3+1 Z4c+Vlasov-Hybrid+FastFlow NR simulations on the B200 GPU
(`$SCRATCH/build_gpu_iter5/src/athena`) across mass ratios
  q = m_p / M_0 in {0.00, 0.02, 0.05, 0.10}
around a spinning Bowen-York puncture (bare m = 0.65 M, spin S_z = 0.70 M^2,
initial apparent-horizon mass M_AH ~ 0.956 M, dimensionless spin chi_AH ~ 0.765)
with coupled Hamiltonian + momentum initial-data solving (`id_solve=true`,
`id_vector=true`), metric-conservative TSC filtering (`nfilter=2`, `filter_compensate=false`),
GL4 hybrid covariant pushing (`interp=quintic`, `vlasov_time_interp=quadratic`),
FastFlow apparent horizon tracking, and r = 14 M quadrupole Psi_4 extraction.

Saves reduced outputs + live q=0.10 equatorial lapse slice to:
  `vlasov_gr/paper/data/physics_bh_massive_backreaction.npz`
and renders:
  `vlasov_gr/paper/figures/fig_physics_bh_massive_backreaction.{pdf,png}`.
"""
from math import factorial
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/python")
import czstyle as cz  # noqa: E402
from nrpic import athena_bin  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
BIN_GPU = f"{SCRATCH}/build_gpu_iter5/src/athena"
RUNROOT = f"{SCRATCH}/runs/bh_massive_backreaction"
DATA_OUT = os.path.join(PAPER_DIR, "data", "physics_bh_massive_backreaction.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_physics_bh_massive_backreaction")

# Initial configuration
COMP0_MASS = 0.65
COMP0_S3 = 0.70
P0_X1 = 3.5
P0_U2 = 0.68
TLIM = 80.0
WALL_LIMIT_SEC = 390.0  # 6.5 min/run guardrail

# Execute q010 first to catch any back-reaction instability early, then q000, q005, q002.
RUN_ORDER = [
    ("q010", 0.10, True),
    ("q000", 1.0e-12, False),
    ("q005", 0.05, False),
    ("q002", 0.02, False),
]
PLOT_CASES = [
    ("q000", 0.00, r"$q = 0.00$", cz.PAL["blue"], "--"),
    ("q002", 0.02, r"$q = 0.02$", cz.PAL["green"], "-"),
    ("q005", 0.05, r"$q = 0.05$", cz.PAL["orange"], "-"),
    ("q010", 0.10, r"$q = 0.10$", cz.PAL["red"], "-"),
]


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


def make_athinput(case: str, m_p: float, write_slice: bool) -> str:
    p2_bh = -(m_p * P0_U2) if m_p >= 1.0e-6 else 0.0
    slice_block = ""
    if write_slice:
        slice_block = """
<output2>
file_type = bin
variable  = z4c_alpha
slice_x3  = 0.001
dt        = 10.0
"""
    return f"""<comment>
problem = massive particle ({case}, m_p={m_p}) back-reaction on spinning BY puncture

<job>
basename = {case}

<mesh>
nghost    = 4
nx1       = 64
x1min     = -64.0
x1max     = 64.0
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = 64
x2min     = -64.0
x2max     = 64.0
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = 64
x3min     = -64.0
x3max     = 64.0
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = 16
nx2       = 16
nx3       = 16

<mesh_refinement>
refinement       = static

<refined_region1>
level = 2
x1min = -15.9
x1max = 15.9
x2min = -15.9
x2max = 15.9
x3min = -15.9
x3max = 15.9

<refined_region2>
level = 3
x1min = -5.9
x1max = 5.9
x2min = -5.9
x2max = 5.9
x3min = -5.9
x3max = 5.9

<refined_region3>
level = 5
x1min = -1.5
x1max = 1.5
x2min = -1.5
x2max = 1.5
x3min = -1.5
x3max = 1.5

<time>
evolution  = dynamic
integrator = rk3
cfl_number = 0.40
nlim       = -1
tlim       = {TLIM:.1f}
ndiag      = 200

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_advect    = 1.0
shift_Gamma     = 0.75
shift_eta       = 2.0
shift_advect    = 1.0
diss            = 0.5
chi_div_floor   = 1.0e-5
damp_kappa1     = 0.02
damp_kappa2     = 0.0
co_0_type       = BH
co_0_x          = 0.0
co_0_y          = 0.0
co_0_z          = 0.0
co_0_mass       = 1.0
co_0_radius     = 1.5
co_0_reflevel   = 5
tracker_mode    = ode
nrad_wave_extraction = 1
extraction_radius_0  = 14.0
extraction_nlev      = 6
waveform_dt          = 0.5

<fastflow>
find_every        = 24
metric_drvts      = interpolant
num_horizons      = 1
npunct            = 1
ntheta            = 16
lmax              = 8
use_puncture_0    = 0
initial_radius_0  = 0.65
flow_iterations_0 = 400
flow_alpha_beta_const_0 = 1.0
hmean_tol_0       = 100.0
mass_tol_0        = 1.0e-5
start_time_0      = 0.0
stop_time_0       = 1000.0
verbose           = false

<gravity>
four_pi_G   = 1.0
threshold   = 0.0
mg_bc       = robin
robin_x1    = 0.0
robin_x2    = 0.0
robin_x3    = 0.0
show_defect = 0

<particles>
particle_type  = nrpic
pusher         = vlasov_hybrid
vlasov_mode    = hybrid
vlasov_pusher  = gl4
vlasov_time_interp = quadratic
interp         = quintic
metric         = mesh
tolerance      = 2.0e-14
max_iterations = 200
deposit        = true
deposit_shape  = tsc
deposit_comp_c = 0.0
nfilter        = 2
filter_compensate = false
filter_metric_conservative = true
filter_mcons_unsplit = true
source_stage_extrap = true
matter_stride  = 1
id_solve       = true
id_vector      = true
id_residual    = stencil
id_vector_residual = stencil
id_psi_init    = trial
id_puncture_radius = 1.0
id_far         = multipole
id_tol         = 1.0e-9
id_maxit       = 60
id_lin_tol     = 1.0e-3
id_lin_maxit   = 50
id_mg_tol      = 1.0e-3
id_dump        = false
alpha_exc      = 0.08
ah_exc_factor  = 0.85
hist_dcycle    = 8
traj_dcycle    = 4
traj_ntrack    = 1
nparticles     = 1
p0_x1          = {P0_X1:.6f}
p0_x2          = 0.0
p0_x3          = 0.0
p0_u1          = 0.0
p0_u2          = {P0_U2:.6f}
p0_u3          = 0.0
p0_m           = {m_p:.12e}

<problem>
pgen_name   = nrpic_cf
ncomp       = 1
comp0_type  = puncture
comp0_mass  = {COMP0_MASS:.6f}
comp0_x1    = 0.0
comp0_x2    = 0.0
comp0_x3    = 0.0
comp0_p1    = 0.0
comp0_p2    = {p2_bh:.12e}
comp0_p3    = 0.0
comp0_s1    = 0.0
comp0_s2    = 0.0
comp0_s3    = {COMP0_S3:.6f}
lapse       = precollapsed
puncture_setup = false

<output1>
file_type = hst
dt        = 0.5
{slice_block}"""


def is_run_complete(rdir: str, case: str) -> bool:
    log = os.path.join(rdir, "stdout.log")
    co = os.path.join(rdir, f"{case}.co_0.txt")
    if not (os.path.isfile(log) and os.path.isfile(co)):
        return False
    txt = open(log).read()
    return "Terminating on time limit" in txt


def run_case(case: str, m_p: float, write_slice: bool) -> float:
    rdir = os.path.join(RUNROOT, case)
    if is_run_complete(rdir, case) and os.environ.get("RERUN_BACKREACT", "0") != "1":
        txt = open(os.path.join(rdir, "stdout.log")).read()
        m_el = re.search(r"setup_wall=([0-9.eE+-]+)", txt)
        m_wt = re.search(r"wall_sec=([0-9.eE+-]+)", txt)
        if m_wt:
            wt = float(m_wt.group(1))
        else:
            m_cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
            wt = float(m_cpu.group(1)) if m_cpu else 0.0
        print(f"[SKIP] {case} (m_p={m_p:.2e}) already completed in {rdir}", flush=True)
        return wt

    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(os.path.join(rdir, "waveforms"), exist_ok=True)
    ath_path = os.path.join(rdir, f"{case}.athinput")
    with open(ath_path, "w") as f:
        f.write(make_athinput(case, m_p, write_slice))

    print(f"[RUN]  Starting {case} (m_p={m_p:.2e}, tlim={TLIM}M) on GPU...", flush=True)
    t0 = time.time()
    log_path = os.path.join(rdir, "stdout.log")
    with open(log_path, "w") as flog:
        rc = subprocess.run(
            [BIN_GPU, "-i", f"{case}.athinput"],
            cwd=rdir,
            stdout=flog,
            stderr=subprocess.STDOUT,
            check=False,
        ).returncode
    wt = time.time() - t0
    txt = open(log_path).read() if os.path.isfile(log_path) else ""
    with open(log_path, "a") as flog:
        flog.write(f"\nwall_sec={wt:.2f}\n")

    if rc != 0 or "Terminating on time limit" not in txt:
        raise RuntimeError(f"Case {case} failed (rc={rc}, wall={wt:.1f}s). Tail:\n{txt[-1500:]}")
    if re.search(r"\bNaN\b", txt, re.IGNORECASE) or "converged after" not in txt:
        raise RuntimeError(f"Case {case} id_solve/stability check failed:\n{txt[:2000]}")
    print(f"[DONE] {case} finished in {wt:.1f} s ({wt/60:.2f} min)", flush=True)
    if wt > WALL_LIMIT_SEC:
        raise RuntimeError(f"Case {case} exceeded {WALL_LIMIT_SEC:.0f} s wall cap ({wt:.1f} s)")

    # Quick sanity check on orbital survival / FastFlow before proceeding
    ah = safe_loadtxt(os.path.join(rdir, f"{case}.horizon_summary_0.txt"))
    ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
    if len(ah) < 10 or float(ah[-1, 1]) < 0.7 * TLIM:
        raise RuntimeError(f"FastFlow horizon tracking lost early in {case}: n={len(ah)}, t_last={ah[-1,1] if len(ah) else 0}")
    if case == "q000":
        nh_q = safe_loadtxt(os.path.join(rdir, f"{case}.nrpic.hst"))
        exc_q = np.where(nh_q[:, 16] > 0.5)[0]
        if len(exc_q) and float(nh_q[int(exc_q[0]), 0]) < 40.0:
            raise RuntimeError(f"Re-plan trigger: q000 plunged early at t={nh_q[int(exc_q[0]), 0]:.2f}M (< 40M)")
    return wt


def find_col_index(path: str, prefix: str) -> int:
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                for tok in ln[1:].strip().split():
                    if tok == prefix:
                        idx_1 = int(tok.split(":")[0])
                        return idx_1 - 1
    raise ValueError(f"Column {prefix!r} not found in {path}")


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
    if os.path.isfile(sh_path):
        with open(sh_path) as f:
            for ln in f:
                if ln.startswith("#"):
                    m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", ln)
                    if m:
                        t_cur = float(m.group(1))
                elif ln.strip() and t_cur is not None:
                    shapes[t_cur] = np.array(ln.split(), dtype=float)
    if not shapes:
        return np.array([]), np.array([])
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


def extract_alpha_slice(rdir: str, case: str, t_p: np.ndarray, xy_p: np.ndarray,
                        t_bh: np.ndarray, xy_bh: np.ndarray, t_exc: float):
    bins = sorted(glob.glob(os.path.join(rdir, "bin", f"{case}.z4c_alpha.*.bin")))
    if not bins:
        bins = sorted(glob.glob(os.path.join(rdir, f"{case}.z4c_alpha.*.bin")))
    if not bins:
        raise FileNotFoundError(f"No z4c_alpha .bin slices found in {rdir}")

    meta = []
    for bf in bins:
        out = athena_bin.read_bin(bf)
        ts = float(out["time"])
        if ts < 5.0:
            continue
        if np.isfinite(t_exc) and ts >= t_exc - 0.5:
            continue
        px = np.interp(ts, t_p, xy_p[:, 0])
        py = np.interp(ts, t_p, xy_p[:, 1])
        bx = np.interp(ts, t_bh, xy_bh[:, 0])
        by = np.interp(ts, t_bh, xy_bh[:, 1])
        r_rel = float(np.hypot(px - bx, py - by))
        meta.append((abs(ts - 30.0) + (100.0 if r_rel < 1.5 else 0.0), ts, bf, out, (px, py), (bx, by)))
    if not meta:
        bf = bins[min(2, len(bins) - 1)]
        out = athena_bin.read_bin(bf)
        ts = float(out["time"])
        px, py = float(np.interp(ts, t_p, xy_p[:, 0])), float(np.interp(ts, t_p, xy_p[:, 1]))
        bx, by = float(np.interp(ts, t_bh, xy_bh[:, 0])), float(np.interp(ts, t_bh, xy_bh[:, 1]))
    else:
        meta.sort(key=lambda it: it[0])
        _, ts, bf, out, (px, py), (bx, by) = meta[0]

    n_g = 288
    L_g = 4.6
    edges = np.linspace(-L_g, L_g, n_g + 1)
    xc = 0.5 * (edges[:-1] + edges[1:])
    yc = xc.copy()
    grid = np.full((n_g, n_g), np.nan, dtype=np.float64)

    for b in sorted(out["blocks"], key=lambda bb: bb["level"]):
        x1min, x1max, x2min, x2max, _, _ = b["bounds"]
        if x1max <= -L_g or x1min >= L_g or x2max <= -L_g or x2min >= L_g:
            continue
        _, n3, n2, n1 = b["data"].shape
        dx1 = (x1max - x1min) / n1
        dx2 = (x2max - x2min) / n2
        imask = (xc >= x1min) & (xc <= x1max)
        jmask = (yc >= x2min) & (yc <= x2max)
        if not (np.any(imask) and np.any(jmask)):
            continue
        ii = np.clip(np.floor((xc[imask] - x1min) / dx1).astype(int), 0, n1 - 1)
        jj = np.clip(np.floor((yc[jmask] - x2min) / dx2).astype(int), 0, n2 - 1)
        k_sl = n3 // 2
        grid[np.ix_(jmask, imask)] = b["data"][0, k_sl][np.ix_(jj, ii)]

    if np.any(np.isnan(grid)):
        raise RuntimeError(f"Unfilled NaN cells in assembled lapse grid from {bf}")
    hx, hy = horizon_eq_ring(os.path.join(rdir, f"{case}.horizon_shape_0.txt"), ts, bx, by)
    return {
        "alpha_grid": grid.astype(np.float32),
        "alpha_edges": edges.astype(np.float64),
        "alpha_t": np.float64(ts),
        "alpha_p_xy": np.array([px, py], dtype=np.float64),
        "alpha_bh_xy": np.array([bx, by], dtype=np.float64),
        "alpha_hx": hx.astype(np.float64),
        "alpha_hy": hy.astype(np.float64),
    }


def reduce_case(case: str, wall_sec: float) -> dict:
    rdir = os.path.join(RUNROOT, case)
    log_txt = open(os.path.join(rdir, "stdout.log")).read()
    m_adm = re.search(r"M_psi\s*=\s*([0-9.eE+-]+)", log_txt)
    m_res = re.search(r"max\|H\|\s*[0-9.eE+-]+\s*->\s*([0-9.eE+-]+)", log_txt)
    m_v = re.search(r"vector equation: relative residual 1 -> ([0-9.eE+-]+)", log_txt)
    m_wall = re.search(r"wall_sec=([0-9.eE+-]+)", log_txt)
    wt = float(m_wall.group(1)) if m_wall else wall_sec

    # Particle trajectory
    raw = np.fromfile(os.path.join(rdir, f"{case}.traj.bin"), dtype=np.float64).reshape(-1, 8)
    raw = raw[np.all(np.isfinite(raw), axis=1)]
    raw = dedup_time(raw, 0)

    # Particle & filter history
    nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{case}.nrpic.hst")), 0)
    exc_rows = np.where(nh[:, 16] > 0.5)[0]
    t_exc = float(nh[int(exc_rows[0]), 0]) if len(exc_rows) else np.nan

    t_p = raw[:, 0]
    xy_p = raw[:, 2:5]
    if np.isfinite(t_exc):
        act = t_p <= t_exc + 1e-9
        t_p = t_p[act]
        xy_p = xy_p[act]

    # Puncture trajectory
    co = dedup_time(safe_loadtxt(os.path.join(rdir, f"{case}.co_0.txt")), 1)
    t_bh = co[:, 1]
    xy_bh = co[:, 2:5]
    bh_at_p = np.column_stack([np.interp(t_p, t_bh, xy_bh[:, c]) for c in range(3)])
    r_rel = np.linalg.norm(xy_p - bh_at_p, axis=1)
    r_bh_all = np.linalg.norm(xy_bh, axis=1)

    # Apparent horizon
    ah_all = safe_loadtxt(os.path.join(rdir, f"{case}.horizon_summary_0.txt"))
    ah_all = ah_all[np.isfinite(ah_all[:, 2])]
    ah_all = dedup_time(ah_all, 1)
    ah_t = ah_all[:, 1]
    ah_M = ah_all[:, 2]
    ah_S = ah_all[:, 6]
    ah_chi = ah_S / (ah_M ** 2)

    # Quadrupole GW (l=2, m=2) at R_ext = 14 M
    re_path = os.path.join(rdir, "waveforms", "rpsi4_real_0014.txt")
    im_path = os.path.join(rdir, "waveforms", "rpsi4_imag_0014.txt")
    col22 = find_col_index(re_path, "6:22")
    w_re = dedup_time(safe_loadtxt(re_path), 0)
    w_im = dedup_time(safe_loadtxt(im_path), 0)
    n_w = min(len(w_re), len(w_im))
    gw_t = w_re[:n_w, 0]
    gw_re = w_re[:n_w, col22]
    gw_im = w_im[:n_w, col22]
    gw_amp = np.hypot(gw_re, gw_im)

    # Z4c Hamiltonian constraint L2/RMS
    zh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{case}.z4c.user.hst")), 0)
    H_L2 = np.sqrt(np.maximum(zh[:, 3], 0.0))
    H_rms = np.sqrt(np.maximum(zh[:, 3] / np.maximum(zh[:, 10], 1.0), 0.0))

    # Filter conservation & E_min
    rel_filt = float(np.max(np.abs(nh[:, 23] - nh[:, 8]) / np.maximum(np.abs(nh[:, 8]), 1e-30)))
    E_min_min = float(np.min(nh[:, 31]))
    pj = gw_t >= 26.0
    gw_peak_pj = float(np.max(gw_amp[pj])) if np.any(pj) else np.nan

    res = {
        f"{case}_wall": np.float64(wt),
        f"{case}_M_psi": np.float64(float(m_adm.group(1)) if m_adm else np.nan),
        f"{case}_H_id": np.float64(float(m_res.group(1)) if m_res else np.nan),
        f"{case}_V_res": np.float64(float(m_v.group(1)) if m_v else np.nan),
        f"{case}_t_exc": np.float64(t_exc),
        f"{case}_p_t": t_p,
        f"{case}_p_xyz": xy_p,
        f"{case}_r_rel": r_rel,
        f"{case}_bh_t": t_bh,
        f"{case}_bh_xyz": xy_bh,
        f"{case}_r_bh": r_bh_all,
        f"{case}_ah_t": ah_t,
        f"{case}_ah_M": ah_M,
        f"{case}_ah_chi": ah_chi,
        f"{case}_gw_t": gw_t,
        f"{case}_gw_re": gw_re,
        f"{case}_gw_im": gw_im,
        f"{case}_H_t": zh[:, 0],
        f"{case}_H_L2": H_L2,
        f"{case}_H_rms": H_rms,
        f"{case}_H_rms_max": np.float64(np.max(H_rms)),
        f"{case}_filt_err": np.float64(rel_filt),
        f"{case}_E_min": np.float64(E_min_min),
        f"{case}_gw_peak_pj": np.float64(gw_peak_pj),
    }
    if case == "q010":
        res.update(extract_alpha_slice(rdir, case, t_p, xy_p, t_bh, xy_bh, t_exc))
    return res


def build_or_load_data() -> dict:
    if os.path.isfile(DATA_OUT) and os.environ.get("RERUN_BACKREACT", "0") != "1":
        print(f"[CACHE] Loading {DATA_OUT}", flush=True)
        return dict(np.load(DATA_OUT, allow_pickle=False))

    walls = {}
    for case, m_p, write_sl in RUN_ORDER:
        walls[case] = run_case(case, m_p, write_sl)

    out = {}
    for case, _, _ in RUN_ORDER:
        out.update(reduce_case(case, walls[case]))

    os.makedirs(os.path.dirname(DATA_OUT), exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"[SAVE] {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def print_summary(D: dict):
    print("\n" + "=" * 108)
    print(
        f"{'Case':<6} {'Wall[s]':>8} {'M_psi':>8} {'M_AH(0->T)':>17} {'chi(0->T)':>15} "
        f"{'max|x_BH|':>10} {'r_rel(0->min->end)':>21} {'t_exc':>7} {'peak|rPsi4_22|':>14} "
        f"{'max H_rms':>10} {'max|dE/E|':>10}"
    )
    print("-" * 108)
    for case, _, _, _, _ in PLOT_CASES:
        wt = float(D[f"{case}_wall"])
        mpsi = float(D[f"{case}_M_psi"])
        ahM = D[f"{case}_ah_M"]
        chi = D[f"{case}_ah_chi"]
        r_bh = D[f"{case}_r_bh"]
        rr = D[f"{case}_r_rel"]
        texc = float(D[f"{case}_t_exc"])
        gw_pk = float(D[f"{case}_gw_peak_pj"])
        hmax = float(D[f"{case}_H_rms_max"])
        ferr = float(D[f"{case}_filt_err"])
        exc_s = f"{texc:6.2f}" if np.isfinite(texc) else "   none"
        print(
            f"{case:<6} {wt:8.1f} {mpsi:8.5f} "
            f"{ahM[0]:7.4f}->{ahM[-1]:7.4f} {chi[0]:6.4f}->{chi[-1]:6.4f} "
            f"{np.max(r_bh):10.5f} {rr[0]:5.2f}->{np.min(rr):5.2f}->{rr[-1]:5.2f} {exc_s:>7} "
            f"{gw_pk:14.4e} {hmax:10.3e} {ferr:10.2e}"
        )
    print("=" * 108 + "\n", flush=True)


def make_figure(D: dict):
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.4))
    fig.subplots_adjust(left=0.085, right=0.895, bottom=0.085, top=0.945, wspace=0.40, hspace=0.28)

    # Top-Left: Live equatorial lapse slice (q=0.10) + trajectories & BH recoil tracks
    ax = axes[0, 0]
    edges = D["alpha_edges"]
    grid = D["alpha_grid"]
    cmap = cz.truncate_cmap("bone", 0.08, 0.94)
    im = ax.pcolormesh(edges, edges, grid, cmap=cmap, vmin=0.05, vmax=0.90,
                       shading="auto", rasterized=True)
    xc = 0.5 * (edges[:-1] + edges[1:])
    ax.contour(xc, xc, grid, levels=[0.20, 0.40, 0.55, 0.67, 0.72],
               colors="0.18", linewidths=0.45, alpha=0.55)

    for case, _, lbl, col, ls in PLOT_CASES:
        px = D[f"{case}_p_xyz"]
        bx = D[f"{case}_bh_xyz"]
        ax.plot(px[:, 0], px[:, 1], color=col, ls=ls, lw=1.6, label=lbl, zorder=4)
        ax.plot(bx[:, 0], bx[:, 1], color=col, ls="-", lw=1.25, alpha=0.9, zorder=5)

    t_sl = float(D["alpha_t"])
    px_sl, py_sl = D["alpha_p_xy"]
    bx_sl, by_sl = D["alpha_bh_xy"]
    ax.plot([px_sl], [py_sl], "o", color=cz.PAL["red"], mec="k", mew=0.9, ms=5.2, zorder=6)
    if len(D["alpha_hx"]):
        ax.plot(D["alpha_hx"], D["alpha_hy"], color="cyan", lw=1.1, zorder=6)
    ax.plot([bx_sl], [by_sl], "+", color="white", mew=1.1, ms=5.0, zorder=6)

    ax.text(
        0.04, 0.96,
        rf"$\alpha(x,y)$ at $t={t_sl:.1f}\,M$ ($q=0.10$)",
        transform=ax.transAxes, ha="left", va="top", color="k", fontsize=8.2,
    )
    ax.set_xlim(-4.4, 4.4)
    ax.set_ylim(-4.4, 4.4)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="lower center", ncol=2, columnspacing=0.8, fontsize=7.6, frameon=False)
    cax = make_axes_locatable(ax).append_axes("right", size="4.5%", pad=0.04)
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label(r"Lapse $\alpha$", fontsize=8.5, labelpad=2)
    cbar.ax.tick_params(labelsize=7.8)

    # Top-Right: Relative orbital separation r_rel(t) and BH recoil |x_BH(t)|
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax2.tick_params(which="both", direction="in")
    handles = []
    max_r = 3.8
    max_rec = 1e-4
    for case, _, lbl, col, ls in PLOT_CASES:
        tp = D[f"{case}_p_t"]
        rr = D[f"{case}_r_rel"]
        tb = D[f"{case}_bh_t"]
        rbh = D[f"{case}_r_bh"]
        max_r = max(max_r, float(np.max(rr)))
        max_rec = max(max_rec, float(np.max(rbh)))
        h, = ax.plot(tp, rr, color=col, ls=ls if case == "q000" else "-", lw=1.5, label=lbl)
        handles.append(h)
        ax2.plot(tb, rbh, color=col, ls=":", lw=1.4)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(0.0, max_r * 1.20)
    ax2.set_ylim(-0.02 * max_rec, max_rec * 1.25)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Separation $r_{\rm rel}\,[M]$")
    ax2.set_ylabel(r"BH recoil $|\mathbf{x}_{\rm BH}|\,[M]$ (dotted)", fontsize=9.0)
    ax.legend(handles=handles, loc="upper left", ncol=2, columnspacing=0.8, fontsize=7.6, frameon=False)

    # Bottom-Left: Post-junk quadrupole gravitational waveform r Re Psi_4^{22} at R_ext = 14 M
    ax = axes[1, 0]
    t_cut = 25.0
    gw_pos = 1e-7
    gw_neg = 1e-7
    for case, _, lbl, col, ls in PLOT_CASES:
        gt = D[f"{case}_gw_t"]
        gre = D[f"{case}_gw_re"]
        msk = gt >= t_cut
        gw_pos = max(gw_pos, float(np.max(gre[msk])))
        gw_neg = max(gw_neg, float(-np.min(gre[msk])))
        ax.plot(gt[msk], gre[msk] * 1.0e4, color=col, ls=ls, lw=1.45, label=lbl)
    ax.axhline(0.0, color="0.65", lw=0.7, ls="-", zorder=1)
    ax.set_xlim(t_cut, TLIM)
    ax.set_ylim(-1.22 * gw_neg * 1.0e4, 1.32 * gw_pos * 1.0e4)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^{4}\,r\,\mathrm{Re}\,\Psi_4^{22}\;[M^{-1}]$")
    ax.text(0.04, 0.94, r"$R_{\rm ext} = 14\,M$", transform=ax.transAxes, ha="left", va="top", fontsize=8.2)
    ax.legend(loc="upper right", ncol=2, columnspacing=0.8, fontsize=7.6, frameon=False)

    # Bottom-Right: Dynamical apparent horizon mass M_AH(t) & dimensionless spin chi_AH(t)
    ax = axes[1, 1]
    axr = ax.twinx()
    axr.tick_params(which="both", direction="in")
    ah_M_all = []
    ah_c_all = []
    h_ah = []
    for case, _, lbl, col, ls in PLOT_CASES:
        at = D[f"{case}_ah_t"]
        aM = D[f"{case}_ah_M"]
        ac = D[f"{case}_ah_chi"]
        ah_M_all.append(aM)
        ah_c_all.append(ac)
        h, = ax.plot(at, aM, color=col, ls=ls if case == "q000" else "-", lw=1.5, label=lbl)
        h_ah.append(h)
        axr.plot(at, ac, color=col, ls=":", lw=1.4)
    m_lo = min(float(np.min(a)) for a in ah_M_all)
    m_hi = max(float(np.max(a)) for a in ah_M_all)
    m_span = max(m_hi - m_lo, 5e-4)
    c_lo = min(float(np.min(a)) for a in ah_c_all)
    c_hi = max(float(np.max(a)) for a in ah_c_all)
    c_span = max(c_hi - c_lo, 5e-4)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(m_lo - 0.14 * m_span, m_hi + 0.56 * m_span)
    axr.set_ylim(c_lo - 0.52 * c_span, c_hi + 0.50 * c_span)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$ (solid)")
    axr.set_ylabel(r"Dimensionless spin $\chi_{\rm AH}$ (dotted)", fontsize=9.0)
    ax.legend(handles=h_ah, loc="upper left", ncol=2, columnspacing=0.8, fontsize=7.6, frameon=False)

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
