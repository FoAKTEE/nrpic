#!/usr/bin/env python3
"""
Milestone 2 benchmark suite comparing Opt MFM (`vlasov_mfm`), Hybrid SCP-AP
(`vlasov_hybrid`), and Monte Carlo NRPIC (`midpoint`) across:
  - Suite 1D: 3D flat periodic relativistic colliding beams (coll_sigma in {0, 2, 15, 1e4})
  - Suite 2 : Kerr a=0.9M warm sheared tidal cloud (t=30M vs MC 100k truth + MC 10k)
  - Suite 3 : Dynamic 3+1 Z4c + Loehner AMR + FastFlow Oppenheimer-Snyder collapse
  - Scaling : B200 strong scaling from 5.5e2 up to 2.0e5 packets over 50 fixed cycles

Saves reduced metrics and arrays to:
  vlasov_gr/paper/data/hybrid_speed_accuracy.npz
"""

import glob
import math
import os
import re
import shutil
import subprocess
import sys
import time as pytime
import numpy as np
from scipy.spatial import cKDTree

REPO_ROOT = "/home/schmidt/ssci-haiyangw/nrpic"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, "python"))
sys.path.insert(0, SCRIPT_DIR)

import run_stage4a_suites123 as s4a
from nrpic import io as nio
from nrpic import kerr as _kerr
from nrpic import oppenheimer_snyder as _osn
from nrpic import vlasov_gr as vg

SCRATCH_ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
GPU_BIN = os.path.join(SCRATCH_ROOT, "build_gpu/src/athena")
STAGE4A_BASE = os.path.join(SCRATCH_ROOT, "runs/stage4a")
BENCH_BASE = os.path.join(SCRATCH_ROOT, "runs/hybrid_bench")
OUT_NPZ = os.path.join(REPO_ROOT, "vlasov_gr/paper/data/hybrid_speed_accuracy.npz")


def clean_dir(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def run_timed(cfg_path: str, run_dir: str, label: str):
    clean_dir(run_dir)
    t0 = pytime.perf_counter()
    res = subprocess.run([GPU_BIN, "-i", cfg_path, "-d", run_dir],
                         capture_output=True, text=True)
    wall_s = pytime.perf_counter() - t0
    log_path = os.path.join(run_dir, f"{label}.stdout.log")
    with open(log_path, "w") as f:
        f.write(res.stdout)
        if res.stderr:
            f.write("\n--- STDERR ---\n" + res.stderr)
    if res.returncode != 0:
        raise RuntimeError(f"AthenaK failed ({label}, rc={res.returncode}):\n{res.stdout[-1500:]}\n{res.stderr[-1000:]}")
    compute_s = np.nan
    cycles = 0
    zcs = np.nan
    scp_line = ""
    for ln in res.stdout.splitlines():
        if "cpu time used" in ln:
            m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", ln)
            if m:
                compute_s = float(m.group(1))
        elif "MeshBlock-cycles" in ln:
            m = re.search(r"MeshBlock-cycles\s*=\s*(\d+)", ln)
            if m:
                cycles = int(m.group(1))
        elif "zone-cycles/cpu_second" in ln:
            m = re.search(r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)", ln)
            if m:
                zcs = float(m.group(1))
        elif "NRPIC Vlasov SCP:" in ln:
            scp_line = ln.strip()
    return dict(wall_s=float(wall_s), compute_s=float(compute_s),
                cycles=int(cycles), zcs=float(zcs), scp_line=scp_line)


# ----------------------------------------------------------------------------
# Config writers matching Stage 4a + explicit hybrid parameters
# ----------------------------------------------------------------------------

def write_suite1d_athinput(cfg_path: str, basename: str, ic_path: str, pusher: str,
                           coll_sigma: float, dt: float = 0.002, tlim: float = 0.55,
                           snap_dt: float = 0.55, scp_q: int = 14, scp_rot: bool = True):
    rot_s = "true" if scp_rot else "false"
    txt = f"""# Suite 1D: 3D flat periodic colliding beams
<comment>
problem = {basename}

<job>
basename = {basename}

<mesh>
nghost   = 2
nx1      = 16
x1min    = 0.0
x1max    = 1.0
ix1_bc   = periodic
ox1_bc   = periodic
nx2      = 4
x2min    = 0.0
x2max    = 0.0520833333333333
ix2_bc   = periodic
ox2_bc   = periodic
nx3      = 4
x3min    = 0.0
x3max    = 0.0520833333333333
ix3_bc   = periodic
ox3_bc   = periodic

<meshblock>
nx1 = 16
nx2 = 4
nx3 = 4

<time>
evolution  = dynamic
integrator = rk2
cfl_number = 1.0
nlim       = -1
tlim       = {tlim:.12f}
ndiag      = 200

<adm>
dynamic = false

<particles>
particle_type      = nrpic
pusher             = {pusher}
metric             = mesh
deposit            = false
particle_file      = {ic_path}
vlasov_basis       = tophat
vlasov_nperp       = 3
vlasov_nq_kick     = 3
vlasov_nq_dep      = 3
vlasov_pair_mode   = covariant
vlasov_analytic_vf = false
vlasov_substeps    = 0
vlasov_cfl         = 0.3
vlasov_max_substeps = 128
vlasov_coll_sigma  = {coll_sigma:.12g}
vlasov_bnd_detect  = false
vlasov_scp_q       = {int(scp_q)}
vlasov_scp_rotate  = {rot_s}
tolerance          = 1.0e-12
dt                 = {dt:.12f}
hist_dcycle        = 2
snap_dt            = {snap_dt:.12f}

<problem>
pgen_name   = nrpic_geodesic
metric_kind = homogeneous
alpha0      = 1.0
gxx = 1.0
gxy = 0.0
gxz = 0.0
gyy = 1.0
gyz = 0.0
gzz = 1.0
"""
    with open(cfg_path, "w") as f:
        f.write(txt)


def write_kerr_bench_athinput(cfg_path: str, basename: str, ic_path: str, pusher: str,
                              dt: float = 0.05, tlim: float = 30.0, snap_dt: float = 5.0,
                              hist_dcycle: int = 20, r_exc: float = 0.98,
                              scp_q: int = 14, scp_rot: bool = True, nlim: int = -1,
                              nx_mesh: int = 16):
    rot_s = "true" if scp_rot else "false"
    txt = f"""# Suite 2 / Scaling: Kerr a=0.9M Cartesian Kerr-Schild warm sheared cloud
<comment>
problem = {basename}

<job>
basename = {basename}

<mesh>
nghost   = 2
nx1      = {nx_mesh}
x1min    = -18.0
x1max    = 18.0
ix1_bc   = outflow
ox1_bc   = outflow
nx2      = {nx_mesh}
x2min    = -18.0
x2max    = 18.0
ix2_bc   = outflow
ox2_bc   = outflow
nx3      = {nx_mesh}
x3min    = -18.0
x3max    = 18.0
ix3_bc   = outflow
ox3_bc   = outflow

<meshblock>
nx1 = {nx_mesh}
nx2 = {nx_mesh}
nx3 = {nx_mesh}

<time>
evolution  = dynamic
integrator = rk2
cfl_number = 1.0
nlim       = {nlim}
tlim       = {tlim:.12f}
ndiag      = 200

<adm>
dynamic = false

<particles>
particle_type      = nrpic
pusher             = {pusher}
metric             = kerr_schild
bh_mass            = 1.0
bh_spin            = 0.9
deposit            = false
tolerance          = 1.0e-12
max_iterations     = 200
dt                 = {dt:.12f}
alpha_exc          = 0.0
vlasov_kerr_r_exc  = {r_exc:.6g}
vlasov_basis       = tophat
vlasov_nperp       = 3
vlasov_nq_kick     = 3
vlasov_nq_dep      = 3
vlasov_pair_mode   = covariant
vlasov_analytic_vf = false
vlasov_substeps    = 0
vlasov_cfl         = 0.3
vlasov_bnd_detect  = true
vlasov_scp_q       = {int(scp_q)}
vlasov_scp_rotate  = {rot_s}
particle_file      = {ic_path}
hist_dcycle        = {hist_dcycle}
snap_dt            = {snap_dt:.12f}

<problem>
pgen_name   = nrpic_geodesic
metric_kind = kerr_schild
bh_mass     = 1.0
bh_spin     = 0.9
"""
    with open(cfg_path, "w") as f:
        f.write(txt)


def write_os_bench_athinput(cfg_path: str, basename: str, part_file: str, tab_file: str,
                            pusher: str, tlim: float = 25.0):
    vlasov_lines = ""
    if pusher in ("vlasov_mfm", "vlasov_hybrid"):
        vlasov_lines = """vlasov_basis        = tophat
vlasov_nperp        = 3
vlasov_nq_kick      = 1
vlasov_nq_dep       = 1
vlasov_pair_mode    = covariant
vlasov_analytic_vf  = false
vlasov_substeps     = 1
vlasov_cfl          = 0.3
vlasov_bnd_detect   = true
vlasov_scp_q        = 14
vlasov_scp_rotate   = true
"""
    txt = f"""# Suite 3: Oppenheimer-Snyder collapse R_0 = 5M (Z4c + Loehner AMR + FastFlow)
<comment>
problem = {basename}

<job>
basename = {basename}

<mesh>
nghost    = 4
nx1       = 64
x1min     = -155.03721050993067
x1max     = 155.03721050993067
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = 64
x2min     = -155.03721050993067
x2max     = 155.03721050993067
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = 64
x3min     = -155.03721050993067
x3max     = 155.03721050993067
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1 = 16
nx2 = 16
nx3 = 16

<mesh_refinement>
refinement          = adaptive
num_levels          = 8
max_nmb_per_rank    = 1024
ncycle_check        = 4
refinement_interval = 8

<amr_criterion0>
method = user

<z4c_amr>
method          = lohner
lohner_refine   = 0.2
lohner_derefine = 0.02
lohner_eps      = 0.01
radius_0_rad      = 6.0
radius_0_reflevel = 4

<refined_region1>
level = 4
x1min = -6.0
x1max = 6.0
x2min = -6.0
x2max = 6.0
x3min = -6.0
x3max = 6.0

<time>
evolution  = dynamic
integrator = rk4
cfl_number = 0.25
nlim       = -1
tlim       = {tlim:.6f}
ndiag      = 20

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
damp_ch         = 0.0
damp_ch_dx      = 0.0

<fastflow>
find_every        = 16
metric_drvts      = interpolant
num_horizons      = 1
npunct            = 0
ntheta            = 16
lmax              = 8
use_puncture_0    = -1
center_x_0        = 0.0
center_y_0        = 0.0
center_z_0        = 0.0
initial_radius_0  = 1.0
flow_iterations_0 = 400
flow_alpha_beta_const_0 = 1.0
hmean_tol_0       = 100.0
mass_tol_0        = 1.0e-5
start_time_0      = 8.0
stop_time_0       = 1000.0
verbose           = false

<particles>
particle_type       = nrpic
pusher              = {pusher}
metric              = mesh
tolerance           = 1.0e-7
max_iterations      = 50
deposit             = true
nfilter             = 1
filter_compensate   = false
filter_comp_c       = -1.0
deposit_max_level   = 31
deposit_adaptive    = false
deposit_min_level   = 4
deposit_ppc         = 1.0
deposit_max_coarsen = 31
alpha_exc           = 0.1
hist_dcycle         = 1
snap_dt             = 2.5
particle_file       = {part_file}
{vlasov_lines}<problem>
pgen_name  = nrpic_cf
ncomp      = 1
comp0_type = table
comp0_file = {tab_file}
lapse      = one

<output1>
file_type = hst
dt        = 0.1
"""
    with open(cfg_path, "w") as f:
        f.write(txt)


def build_spherical_kerr_cloud_mc(n_part: int, seed: int = 42, x0=(6.0, 0.0, 1.5),
                                  R_cl: float = 1.0, sig_u: float = 0.06, a: float = 0.9, M: float = 1.0):
    rng = np.random.default_rng(seed)
    u_rad = rng.random(n_part)
    cos_th = 2.0 * rng.random(n_part) - 1.0
    sin_th = np.sqrt(np.maximum(1.0 - cos_th * cos_th, 0.0))
    phi = 2.0 * math.pi * rng.random(n_part)
    rr = R_cl * np.cbrt(u_rad)
    dx = np.column_stack([rr * sin_th * np.cos(phi), rr * sin_th * np.sin(phi), rr * cos_th])
    pts = dx + np.asarray(x0, dtype=np.float64)[None, :]

    _, x_bl, _ = _kerr.convert_state(0.0, pts, np.zeros_like(pts), "cks", "bl", a=a, M=M)
    r_bl = x_bl[:, 0]
    th_bl = x_bl[:, 1]
    sqM = math.sqrt(M)
    sq_r = np.sqrt(r_bl)
    denom = (r_bl ** 0.75) * np.sqrt(np.maximum(r_bl ** 1.5 - 3.0 * M * sq_r + 2.0 * a * sqM, 1e-12))
    Lz = sqM * (r_bl * r_bl - 2.0 * a * np.sqrt(M * r_bl) + a * a) / denom
    u_bl = np.zeros_like(pts)
    u_bl[:, 0] = -0.03
    u_bl[:, 2] = 1.02 * Lz * (np.sin(th_bl) ** 2)
    _, x_cks, u_mean = _kerr.convert_state(0.0, x_bl, u_bl, "bl", "cks", a=a, M=M)

    adm_c = _kerr.adm("cks", x_cks, a=a, M=M, derivs=False)
    L = np.linalg.cholesky(adm_c.gamma)
    du_tet = rng.uniform(-math.sqrt(3.0) * sig_u, math.sqrt(3.0) * sig_u, size=(n_part, 3))
    u_cks = u_mean + np.einsum("nij,nj->ni", L, du_tet)
    m = np.full(n_part, 1.0 / n_part, dtype=np.float64)
    sp = np.zeros(n_part, dtype=np.int32)
    return x_cks, u_cks, m, sp


def kerr_cloud_kde_and_hist(x, m, dphi_grid, phi_cm_ref=None):
    bins = np.linspace(-0.20, 0.20, 25)
    # Use common reference center-of-mass angle when provided (fair shape+phase metric)
    m_tot = np.maximum(np.sum(m), 1e-300)
    x_cm = np.sum(m[:, None] * x, axis=0) / m_tot
    phi_own = math.atan2(x_cm[1], x_cm[0])
    phi_ref = phi_own if phi_cm_ref is None else phi_cm_ref
    phi = np.arctan2(x[:, 1], x[:, 0])
    dphi = (phi - phi_ref + math.pi) % (2.0 * math.pi) - math.pi

    hist_counts, _ = np.histogram(dphi, bins=bins, weights=m, density=False)
    dx_b = bins[1] - bins[0]
    p_hist = hist_counts / np.maximum(np.trapezoid(hist_counts, dphi_grid), 1e-300)

    # Adaptive Gaussian KDE following Stage 4a bandwidth scaling
    rcm = math.hypot(x_cm[0], x_cm[1])
    tree = cKDTree(x)
    dists, _ = tree.query(x, k=min(8, len(x)))
    h_nn = float(np.median(dists[:, -1])) if dists.shape[1] > 1 else 0.2
    sig_phi = max(h_nn / max(rcm, 1e-6) * 0.65, 1.0e-3)

    diff = dphi_grid[:, None] - dphi[None, :]
    kern = np.exp(-0.5 * (diff / sig_phi) ** 2) / (math.sqrt(2.0 * math.pi) * sig_phi)
    kde_raw = kern @ m
    p_kde = kde_raw / np.maximum(np.trapezoid(kde_raw, dphi_grid), 1e-300)
    sec_diff_r = lambda y: float(np.sqrt(np.mean(np.diff(y, n=2) ** 2)) / max(float(np.mean(y)), 1e-300))
    rough_hist = sec_diff_r(p_hist)
    rough_kde = sec_diff_r(p_kde)
    return dict(x_cm=x_cm, phi_own=phi_own, p_hist=p_hist, p_kde=p_kde,
                rough_hist=rough_hist, rough_kde=rough_kde, sig_phi=sig_phi)


# ============================================================================
# Suite 1D
# ============================================================================

def benchmark_suite1d(out: dict):
    print("\n=== BENCHMARK SUITE 1D: SR Colliding Beams (vlasov_hybrid vs Opt MFM) ===", flush=True)
    ic_file = os.path.join(STAGE4A_BASE, "suite1/ic_1d_taub.grlbv")
    s1_dir = os.path.join(BENCH_BASE, "suite1d")
    os.makedirs(s1_dir, exist_ok=True)
    Ly = Lz = 0.0520833333333333
    Lbox = [1.0, Ly, Lz]

    # Binning grid for comparing discrete 67,200 SCP packets (sig=0) seamlessly against MFM
    xb_edges = np.linspace(0.0, 1.0, 81)
    xb_cent = 0.5 * (xb_edges[:-1] + xb_edges[1:])
    dx_b = xb_edges[1] - xb_edges[0]
    vol_b = dx_b * Ly * Lz
    out["s1d_xb_cent"] = xb_cent

    # Exact collisionless free-streaming reference from initial top-hat velocities (8^3 midpoint nodes/basis)
    ic_sn = vg.read_grlbv(ic_file)
    d1_ref = np.load(os.path.join(REPO_ROOT, "vlasov_gr/paper/data/suite1_sr_flat.npz"))
    out["s1d_taub_D2"] = float(d1_ref["s1d_taub_D2"])
    out["s1d_taub_e2"] = float(d1_ref["s1d_taub_e2"])
    out["s1d_taub_Vs"] = float(d1_ref["s1d_taub_Vs"])
    # Compute 512-node exact 3D top-hat advection for every populated IC basis
    x_ex_list, m_ex_list = [], []
    q1d = (np.arange(8) + 0.5) / 8.0 * 2.0 - 1.0  # [-1, 1]
    q3 = np.stack(np.meshgrid(q1d, q1d, q1d, indexing="ij"), axis=-1).reshape(-1, 3) * math.sqrt(3.0)
    w_q = 1.0 / len(q3)
    for al in range(ic_sn["m"].shape[1]):
        mask = ic_sn["m"][:, al] > 0.0
        if not np.any(mask):
            continue
        x0 = ic_sn["x"][mask, 0][:, None]
        m0 = ic_sn["m"][mask, al][:, None] * w_q
        ub = ic_sn["u_bar"][mask, al, :]
        L_u = np.linalg.cholesky(ic_sn["Sigma"][mask, al, :, :])
        u_q = ub[:, None, :] + np.einsum("nij,qj->nqj", L_u, q3)
        W_q = np.sqrt(1.0 + np.sum(u_q * u_q, axis=-1))
        vx_q = u_q[..., 0] / W_q
        x_t = (x0 + 0.55 * vx_q) % 1.0
        x_ex_list.append(x_t.ravel())
        m_ex_list.append(np.broadcast_to(m0, x_t.shape).ravel())
    hx_ex, _ = np.histogram(np.concatenate(x_ex_list), bins=xb_edges, weights=np.concatenate(m_ex_list))
    out["s1d_exact_colless_D_bin"] = hx_ex / vol_b

    sigmas = [0.0, 2.0, 15.0, 1.0e4]
    out["s1d_sigmas"] = np.array(sigmas, dtype=np.float64)

    for pusher in ("mfm", "hybrid"):
        p_key = "vlasov_mfm" if pusher == "mfm" else "vlasov_hybrid"
        for sig in sigmas:
            stag = "1e4" if sig >= 1e3 else str(int(round(sig)))
            lbl = f"s1d_{pusher}_sig{stag}"
            cfg = os.path.join(s1_dir, f"{lbl}.athinput")
            rdir = os.path.join(s1_dir, lbl)
            write_suite1d_athinput(cfg, lbl, ic_file, p_key, coll_sigma=sig)
            meta = run_timed(cfg, rdir, lbl)

            hst = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
            dm = float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0])))
            de = float(np.max(np.abs(hst["E_tot"] - hst["E_tot"][0]) / abs(hst["E_tot"][0])))
            sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
            m_tot = np.sum(sn["m"], axis=1)

            # Binned D(x) & mass-weighted <u_x>(x)
            hx, _ = np.histogram(sn["x"][:, 0], bins=xb_edges, weights=m_tot)
            D_bin = hx / vol_b
            # Also store MFM-specific pointwise smoothed density for sig>0 or sig=0 MFM
            if sn["Sigma"].shape[1] >= 1 and not (pusher == "hybrid" and sig <= 0.0):
                nbar = s4a.fast_nbar_periodic(sn["x"], Lbox, 1.0 / 150.0)
                D_pt = m_tot * nbar
                ord_x = np.argsort(sn["x"][:, 0])
                xs = sn["x"][ord_x, 0]
                Ds = D_pt[ord_x]
                step = max(1, len(xs) // 300)
                out[f"{lbl}_xs"] = xs[::step]
                out[f"{lbl}_Ds"] = Ds[::step]
            else:
                out[f"{lbl}_xs"] = xb_cent
                out[f"{lbl}_Ds"] = D_bin

            out[f"{lbl}_D_bin"] = D_bin
            out[f"{lbl}_wall_s"] = meta["wall_s"]
            out[f"{lbl}_comp_s"] = meta["compute_s"]
            out[f"{lbl}_dm"] = dm
            out[f"{lbl}_de"] = de
            out[f"{lbl}_n_elem"] = len(sn["x"])
            print(f"  [{lbl:18s}] N={len(sn['x']):6d} wall={meta['wall_s']:6.3f}s comp={meta['compute_s']:6.3f}s "
                  f"dM={dm:.2e} dE={de:.2e} | {meta['scp_line']}", flush=True)


# ============================================================================
# Suite 2
# ============================================================================

def eval_run_suite2(lbl: str, rdir: str, is_nrp: bool, dphi_grid: np.ndarray, phi_cm_ref=None):
    hst_path = os.path.join(rdir, f"{lbl}.nrpic.hst" if is_nrp else f"{lbl}.vlasov.hst")
    with open(hst_path) as f:
        lines = [l for l in f if not l.startswith("#") and l.strip()]
    h_arr = np.array([[float(x) for x in l.split()] for l in lines])

    if is_nrp:
        bfiles = sorted(glob.glob(os.path.join(rdir, f"{lbl}.part.*.bin")))
        snaps = []
        for bf in bfiles:
            t, d, _, _ = s4a.read_nrp_snapshot(bf)
            x = d[:, 0:3]
            u = d[:, 3:6]
            m = d[:, 6]
            snaps.append((t, x, m[:, None], u[:, None, :], np.zeros((len(x), 1, 3, 3))))
        n_q = 1
    else:
        bfiles = sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))
        snaps = []
        max_sig_0 = 0.0
        for bf in bfiles:
            sn = vg.read_grlbv(bf)
            if len(snaps) == 0:
                max_sig_0 = float(np.max(np.abs(sn["Sigma"])))
            snaps.append((float(sn["time"]), sn["x"], sn["m"], sn["u_bar"], sn["Sigma"]))
        n_q = 1 if max_sig_0 == 0.0 else 3

    times, Es, Lzs, Mts = [], [], [], []
    for t, x, m, u, S in snaps:
        E, Lz, *_ = s4a.kerr_killing_invariants(x, m, u, S, a=0.9, M=1.0, n_q=n_q)
        times.append(t)
        Es.append(float(E))
        Lzs.append(float(Lz))
        Mts.append(float(np.sum(m)))

    times = np.array(times)
    Es = np.array(Es)
    Lzs = np.array(Lzs)
    Mts = np.array(Mts)
    dE = np.abs(Es - Es[0]) / abs(Es[0])
    dLz = np.abs(Lzs - Lzs[0]) / abs(Lzs[0])
    dm = abs(Mts[-1] - Mts[0]) / abs(Mts[0])

    tf, xf, mf, uf, Sf = snaps[-1]
    prof = kerr_cloud_kde_and_hist(xf, np.sum(mf, axis=1), dphi_grid, phi_cm_ref=phi_cm_ref)

    return dict(
        times=times, E=Es, Lz=Lzs, M=Mts,
        max_dE=float(np.max(dE)), max_dLz=float(np.max(dLz)), end_dm=float(dm),
        x_fin=xf, m_fin=np.sum(mf, axis=1), u_fin=uf[:, 0, :],
        x_cm=prof["x_cm"], phi_own=prof["phi_own"],
        p_hist=prof["p_hist"], p_kde=prof["p_kde"],
        rough_hist=prof["rough_hist"], rough_kde=prof["rough_kde"], sig_phi=prof["sig_phi"],
        N_init=int(len(snaps[0][1])), N_fin=int(len(xf)),
    )


def benchmark_suite2(out: dict):
    print("\n=== BENCHMARK SUITE 2: Kerr a=0.9M Tidal Cloud (Truth=MC100k, Opt MFM, Hybrid SCP-AP, MC10k) ===", flush=True)
    s2_dir = os.path.join(BENCH_BASE, "suite2")
    os.makedirs(s2_dir, exist_ok=True)
    bins = np.linspace(-0.20, 0.20, 25)
    dphi_grid = 0.5 * (bins[:-1] + bins[1:])
    out["s2_dphi_grid"] = dphi_grid

    ic_mc10k = os.path.join(STAGE4A_BASE, "suite2/ic_kerr_mc10k.nrp")
    ic_mc100k = os.path.join(s2_dir, "ic_kerr_mc100k.nrp")
    if not os.path.exists(ic_mc100k):
        x100, u100, m100, sp100 = build_spherical_kerr_cloud_mc(100_000, seed=2026)
        nio.write_nrp(ic_mc100k, x100, u100, m100, sp100)
        print(f"  Generated ic_kerr_mc100k.nrp ({len(m100)} particles)", flush=True)

    # Define benchmark matrix
    runs = [
        ("s2_mc100k",             ic_mc100k,                                    "midpoint",      True,  0.0,  14, True),
        ("s2_mc10k",              ic_mc10k,                                     "midpoint",      True,  0.0,  14, True),
        ("s2_opt_n10",            os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n10.grlbv"), "vlasov_mfm", False, 0.98, 14, True),
        ("s2_opt_n14",            os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n14.grlbv"), "vlasov_mfm", False, 0.98, 14, True),
        ("s2_opt_n18",            os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n18.grlbv"), "vlasov_mfm", False, 0.98, 14, True),
        ("s2_hyb_n10_q14",        os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n10.grlbv"), "vlasov_hybrid", False, 0.0, 14, True),
        ("s2_hyb_n14_q14",        os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n14.grlbv"), "vlasov_hybrid", False, 0.0, 14, True),
        ("s2_hyb_n18_q8",         os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n18.grlbv"), "vlasov_hybrid", False, 0.0,  8, True),
        ("s2_hyb_n18_q14",        os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n18.grlbv"), "vlasov_hybrid", False, 0.0, 14, True),
        ("s2_hyb_n18_q14_unrot",  os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n18.grlbv"), "vlasov_hybrid", False, 0.0, 14, False),
        ("s2_hyb_n18_q14_rexc98", os.path.join(STAGE4A_BASE, "suite2/ic_kerr_n18.grlbv"), "vlasov_hybrid", False, 0.98, 14, True),
    ]

    truth_phi_cm = None
    truth_hist = None
    truth_kde = None
    truth_x_cm = None

    for lbl, icp, pusher, is_nrp, r_exc, q, rot in runs:
        cfg = os.path.join(s2_dir, f"{lbl}.athinput")
        rdir = os.path.join(s2_dir, lbl)
        write_kerr_bench_athinput(cfg, lbl, icp, pusher, dt=0.05, tlim=30.0, snap_dt=5.0,
                                  hist_dcycle=20, r_exc=r_exc, scp_q=q, scp_rot=rot)
        meta = run_timed(cfg, rdir, lbl)
        ev = eval_run_suite2(lbl, rdir, is_nrp, dphi_grid, phi_cm_ref=truth_phi_cm)
        if lbl == "s2_mc100k":
            truth_phi_cm = ev["phi_own"]
            truth_hist = ev["p_hist"]
            truth_kde = ev["p_kde"]
            truth_x_cm = ev["x_cm"]

        # Normalized L1 & L2 errors vs MC 100k truth
        l1_hist = float(np.trapezoid(np.abs(ev["p_hist"] - truth_hist), dphi_grid))
        l2_hist = float(math.sqrt(np.trapezoid((ev["p_hist"] - truth_hist) ** 2, dphi_grid)))
        l1_kde = float(np.trapezoid(np.abs(ev["p_kde"] - truth_kde), dphi_grid))
        l2_kde = float(math.sqrt(np.trapezoid((ev["p_kde"] - truth_kde) ** 2, dphi_grid)))
        cm_err = float(np.linalg.norm(ev["x_cm"] - truth_x_cm))

        out[f"{lbl}_wall_s"] = meta["wall_s"]
        out[f"{lbl}_comp_s"] = meta["compute_s"]
        out[f"{lbl}_N_init"] = ev["N_init"]
        out[f"{lbl}_N_fin"] = ev["N_fin"]
        out[f"{lbl}_times"] = ev["times"]
        out[f"{lbl}_E"] = ev["E"]
        out[f"{lbl}_Lz"] = ev["Lz"]
        out[f"{lbl}_max_dE"] = ev["max_dE"]
        out[f"{lbl}_max_dLz"] = ev["max_dLz"]
        out[f"{lbl}_end_dm"] = ev["end_dm"]
        out[f"{lbl}_x_cm"] = ev["x_cm"]
        out[f"{lbl}_p_hist"] = ev["p_hist"]
        out[f"{lbl}_p_kde"] = ev["p_kde"]
        out[f"{lbl}_rough_hist"] = ev["rough_hist"]
        out[f"{lbl}_rough_kde"] = ev["rough_kde"]
        out[f"{lbl}_l1_hist"] = l1_hist
        out[f"{lbl}_l2_hist"] = l2_hist
        out[f"{lbl}_l1_kde"] = l1_kde
        out[f"{lbl}_l2_kde"] = l2_kde
        out[f"{lbl}_cm_err"] = cm_err
        # Save x-y positions (subsampled <= 15k for crisp scatter plots)
        if lbl in ("s2_mc10k", "s2_opt_n18", "s2_hyb_n18_q14", "s2_mc100k"):
            stride = max(1, len(ev["x_fin"]) // 12000)
            out[f"{lbl}_xy"] = ev["x_fin"][::stride, :2]

        print(f"  [{lbl:22s}] N={ev['N_init']:6d} wall={meta['wall_s']:5.2f}s comp={meta['compute_s']:5.2f}s | "
              f"|dE|={ev['max_dE']:.2e} |dLz|={ev['max_dLz']:.2e} dM={ev['end_dm']:.2e} | "
              f"R_hist={ev['rough_hist']:.4f} L1_hist={l1_hist:.4f} L1_kde={l1_kde:.4f}", flush=True)


# ============================================================================
# Suite 3
# ============================================================================

def benchmark_suite3(out: dict):
    print("\n=== BENCHMARK SUITE 3: Dynamic Z4c + Loehner AMR + FastFlow OS Collapse ===", flush=True)
    s3_dir = os.path.join(BENCH_BASE, "suite3")
    os.makedirs(s3_dir, exist_ok=True)
    tab_file = os.path.join(STAGE4A_BASE, "suite3/os_R5.tab")
    ic_grlbv = os.path.join(STAGE4A_BASE, "suite3/ic_s3_grlbv_n26.grlbv")
    ic_nrpic = os.path.join(STAGE4A_BASE, "suite3/ic_s3_nrpic_n26.nrp")

    specs = [
        ("s3_opt_n26", ic_grlbv, "vlasov_mfm"),
        ("s3_hyb_n26", ic_grlbv, "vlasov_hybrid"),
        ("s3_nrp_n26", ic_nrpic, "midpoint"),
    ]
    for lbl, pfile, pusher in specs:
        cfg = os.path.join(s3_dir, f"{lbl}.athinput")
        rdir = os.path.join(s3_dir, lbl)
        write_os_bench_athinput(cfg, lbl, pfile, tab_file, pusher, tlim=25.0)
        meta = run_timed(cfg, rdir, lbl)

        nrp = np.loadtxt(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        z4c = np.loadtxt(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
        ah_files = sorted(glob.glob(os.path.join(rdir, f"{lbl}.horizon_summary_*.txt")))
        ah = s4a.read_horizon(ah_files[0]) if ah_files else np.empty((0, 10))
        t_ah = float(ah[0, 0]) if len(ah) else float("nan")
        M_ah = float(ah[-1, 1]) if len(ah) else float("nan")
        m_tot = nrp[:, 3]
        m_ref = float(np.max(m_tot)) if len(m_tot) else 1.0
        m_exc = nrp[:, 17]
        exc_idx = np.where((nrp[:, 0] > 0.0) & (m_exc >= 0.99 * m_ref))[0]
        t_exc99 = float(nrp[exc_idx[0], 0]) if len(exc_idx) else float("nan")

        out[f"{lbl}_wall_s"] = meta["wall_s"]
        out[f"{lbl}_comp_s"] = meta["compute_s"]
        out[f"{lbl}_t_nrp"] = nrp[:, 0]
        out[f"{lbl}_tau_probe"] = nrp[:, 14]
        out[f"{lbl}_alp_probe"] = nrp[:, 12]
        out[f"{lbl}_m_excised"] = m_exc
        out[f"{lbl}_nmb"] = nrp[:, 22]
        out[f"{lbl}_t_z4c"] = z4c[:, 0]
        out[f"{lbl}_H_l2"] = z4c[:, 3]
        out[f"{lbl}_M_l2"] = z4c[:, 4]
        out[f"{lbl}_ah_t"] = ah[:, 0] if len(ah) else np.array([])
        out[f"{lbl}_ah_M"] = ah[:, 1] if len(ah) else np.array([])
        out[f"{lbl}_t_AH"] = t_ah
        out[f"{lbl}_M_AH"] = M_ah
        out[f"{lbl}_t_exc99"] = t_exc99
        out[f"{lbl}_H_max"] = float(np.max(z4c[:, 3]))
        out[f"{lbl}_M_max"] = float(np.max(z4c[:, 4]))
        print(f"  [{lbl:12s}] wall={meta['wall_s']:5.2f}s comp={meta['compute_s']:5.2f}s | "
              f"t_AH={t_ah:.4f} M_AH={M_ah:.5f} t_exc99={t_exc99:.4f} H_max={np.max(z4c[:,3]):.3f} | {meta['scp_line']}",
              flush=True)


# ============================================================================
# B200 Strong Scaling (50 fixed cycles)
# ============================================================================

def benchmark_scaling(out: dict):
    print("\n=== BENCHMARK STRONG SCALING ON B200 (50 cycles, Kerr a=0.9M) ===", flush=True)
    sc_dir = os.path.join(BENCH_BASE, "scaling")
    os.makedirs(sc_dir, exist_ok=True)
    ncubes = [10, 14, 18, 24, 30]
    mfm_N, mfm_wall, mfm_comp = [], [], []
    hyb_N, hyb_wall, hyb_comp = [], [], []
    mc_N, mc_wall, mc_comp = [], [], []

    for nc in ncubes:
        ic_lat = os.path.join(sc_dir, f"ic_kerr_n{nc}.grlbv")
        x_l, m_l, u_l, S_l, _ = s4a.build_spherical_kerr_cloud_lat(nc)
        n_el = len(x_l)
        if not os.path.exists(ic_lat):
            vg.write_grlbv(ic_lat, x_l, m_l, u_l, S_l, time=0.0)

        # Opt MFM
        lbl_m = f"sc_mfm_n{nc}"
        cfg_m = os.path.join(sc_dir, f"{lbl_m}.athinput")
        write_kerr_bench_athinput(cfg_m, lbl_m, ic_lat, "vlasov_mfm", dt=0.05, tlim=10.0,
                                  snap_dt=100.0, hist_dcycle=100, r_exc=0.98, nlim=50)
        mm = run_timed(cfg_m, os.path.join(sc_dir, lbl_m), lbl_m)
        mfm_N.append(n_el); mfm_wall.append(mm["wall_s"]); mfm_comp.append(mm["compute_s"])

        # Hybrid SCP-AP q=14 (N_pkt = 14 * n_el)
        n_pk = 14 * n_el
        lbl_h = f"sc_hyb_n{nc}"
        cfg_h = os.path.join(sc_dir, f"{lbl_h}.athinput")
        write_kerr_bench_athinput(cfg_h, lbl_h, ic_lat, "vlasov_hybrid", dt=0.05, tlim=10.0,
                                  snap_dt=100.0, hist_dcycle=100, r_exc=0.0, scp_q=14, scp_rot=True, nlim=50)
        mh = run_timed(cfg_h, os.path.join(sc_dir, lbl_h), lbl_h)
        hyb_N.append(n_pk); hyb_wall.append(mh["wall_s"]); hyb_comp.append(mh["compute_s"])

        # NRPIC MC matched particle count
        ic_mc = os.path.join(sc_dir, f"ic_mc_{n_pk}.nrp")
        if not os.path.exists(ic_mc):
            xm, um, mm_arr, spm = build_spherical_kerr_cloud_mc(n_pk, seed=100 + nc)
            nio.write_nrp(ic_mc, xm, um, mm_arr, spm)
        lbl_c = f"sc_mc_n{nc}"
        cfg_c = os.path.join(sc_dir, f"{lbl_c}.athinput")
        write_kerr_bench_athinput(cfg_c, lbl_c, ic_mc, "midpoint", dt=0.05, tlim=10.0,
                                  snap_dt=100.0, hist_dcycle=100, r_exc=0.0, nlim=50)
        mc_meta = run_timed(cfg_c, os.path.join(sc_dir, lbl_c), lbl_c)
        mc_N.append(n_pk); mc_wall.append(mc_meta["wall_s"]); mc_comp.append(mc_meta["compute_s"])

        print(f"  nc={nc:2d}: Opt-MFM N={n_el:5d} comp={mm['compute_s']:.3f}s | "
              f"Hybrid Npkt={n_pk:6d} comp={mh['compute_s']:.3f}s | "
              f"MC N={n_pk:6d} comp={mc_meta['compute_s']:.3f}s", flush=True)

    out["sc_ncubes"] = np.array(ncubes)
    out["sc_nlim"] = 50
    out["sc_mfm_N"] = np.array(mfm_N)
    out["sc_mfm_wall_s"] = np.array(mfm_wall)
    out["sc_mfm_comp_s"] = np.array(mfm_comp)
    out["sc_hyb_N"] = np.array(hyb_N)
    out["sc_hyb_wall_s"] = np.array(hyb_wall)
    out["sc_hyb_comp_s"] = np.array(hyb_comp)
    out["sc_mc_N"] = np.array(mc_N)
    out["sc_mc_wall_s"] = np.array(mc_wall)
    out["sc_mc_comp_s"] = np.array(mc_comp)


def main():
    os.makedirs(BENCH_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)

    out = {
        "base_mfm_s2_n18_wall_s": 65.99,
        "base_mfm_s1d_sig15_wall_s": 19.38,
    }
    benchmark_suite1d(out)
    benchmark_suite2(out)
    benchmark_suite3(out)
    benchmark_scaling(out)

    alias_map = {
        "s1d_xb_cent": "beam_xb_cent",
        "s1d_exact_colless_D_bin": "beam_exact_colless_D_bin",
        "s1d_mfm_sig0_D_bin": "beam_mfm_sig0_D_bin",
        "s1d_hybrid_sig0_D_bin": "beam_hybrid_sig0_D_bin",
        "s1d_hybrid_sig2_xs": "beam_hybrid_sig2_xs",
        "s1d_hybrid_sig2_Ds": "beam_hybrid_sig2_Ds",
        "s1d_hybrid_sig15_xs": "beam_hybrid_sig15_xs",
        "s1d_hybrid_sig15_Ds": "beam_hybrid_sig15_Ds",
        "s1d_hybrid_sig1e4_xs": "beam_hybrid_sig1e4_xs",
        "s1d_hybrid_sig1e4_Ds": "beam_hybrid_sig1e4_Ds",
        "s1d_taub_Vs": "beam_taub_Vs",
        "s1d_taub_D2": "beam_taub_D2",
    }
    for src_k, dst_k in alias_map.items():
        if src_k in out:
            out[dst_k] = out[src_k]

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved complete hybrid benchmark data to: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
