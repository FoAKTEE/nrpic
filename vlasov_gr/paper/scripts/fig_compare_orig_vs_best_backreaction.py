#!/usr/bin/env python3
"""Full 3+1 massive-particle back-reaction comparison: NRPIC Original vs Our Best GR-LBV.

Compares NRPIC Original (RK4 0.25 / midpoint / cubic Hermite / plain filter / frozen source / MC)
against Our Best GR-LBV (RK3 0.40 / GL4+quad time / C^2 quintic / unsplit mcons / Scheme A / QMC)
across three full 3+1 self-gravitating dynamical-spacetime massive-particle suites:

  1. Spinning BH + massive particle mass-ratio ladder (q in {0.02, 0.05, 0.10}, B200 GPU):
     - Runs `orig_q010` and `orig_q002` cleanly under `$SCRATCH/runs/compare_orig_vs_best/`
     - Reuses completed `orig_q005` and `bh_massive_backreaction/q{002,005,010}`
     - Compares equatorial inspiral & BH recoil tracks, delayed plunge t_exc, horizon mass M_AH(t),
       filter conservation drift |I_E^filt / I_E - 1|, quadrupole Psi_4^{22}, and GPU wall times.

  2. Live 8-level AMR Jeans binary BH formation (N = 10^4, 10^5 massive particles, t <= 20 M):
     - Reuses `$SCRATCH/runs/repro_wave4c/jeans_{10k,100k}_{strat_mid,qmc_hyb}/`
     - Compares equatorial binary orbits, out-of-plane kick |z_0(t)|, and filter conservation.

  3. Live 9-level AMR Shapiro-Teukolsky relativistic cluster collapse (y_c = 0.500, 0.605; N = 10^4):
     - Reuses `repro_wave4b/m5c/{st_yc0500_vp01_10k_mid, st_yc0605_vp01_10k_{mid,hyb}}` and
       `iter5_speed_verify/st10k_rk3_040_dir4c_s2` (2.36x B200 speedup)
     - Compares central lapse collapse alpha_c(t), horizon formation t_AH, and |P|/M_0 conservation.

Saves reduced archive `vlasov_gr/paper/data/compare_orig_vs_best_backreaction.npz` and
renders `vlasov_gr/paper/figures/fig_compare_orig_vs_best_backreaction.{pdf,png}`.
"""
from math import factorial
import os
import re
import shutil
import subprocess
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPER_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PAPER_DIR, "data")
SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
BIN_GPU = f"{SCRATCH}/build_gpu_iter5/src/athena"
CMP_ROOT = f"{SCRATCH}/runs/compare_orig_vs_best"
BEST_ROOT = f"{SCRATCH}/runs/bh_massive_backreaction"
W4C_ROOT = f"{SCRATCH}/runs/repro_wave4c"
W4B_M5C = f"{SCRATCH}/runs/repro_wave4b/m5c"
I5_ROOT = f"{SCRATCH}/runs/iter5_speed_verify"

DATA_OUT = os.path.join(DATA_DIR, "compare_orig_vs_best_backreaction.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_compare_orig_vs_best_backreaction")

TLIM_BH = 80.0
WALL_CAP_ORIG = 720.0  # 12 min guardrail on B200

# Run orig_q010 first to catch any stability/wall issue early, then orig_q002
ORIG_RUN_SPECS = [
    ("orig_q010", "q010", 0.10),
    ("orig_q002", "q002", 0.02),
]
BH_QS = [
    ("q002", 0.02, r"$q = 0.02$", cz.PAL["green"]),
    ("q005", 0.05, r"$q = 0.05$", cz.PAL["orange"]),
    ("q010", 0.10, r"$q = 0.10$", cz.PAL["red"]),
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


def find_col_index(path: str, prefix: str) -> int:
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                for tok in ln[1:].strip().split():
                    if tok == prefix:
                        return int(tok.split(":")[0]) - 1
    raise ValueError(f"Column {prefix!r} not found in {path}")


def downsample_2col(x: np.ndarray, y: np.ndarray, max_pts: int = 450):
    if len(x) <= max_pts:
        return x.astype(np.float64), y.astype(np.float64)
    st = max(1, len(x) // max_pts)
    xs, ys = x[::st], y[::st]
    if xs[-1] != x[-1]:
        xs = np.append(xs, x[-1])
        ys = np.append(ys, y[-1])
    return xs.astype(np.float64), ys.astype(np.float64)


def make_orig_athinput(case: str, m_p: float) -> str:
    p2_bh = -(m_p * 0.68)
    return f"""<comment>
problem = {case} (NRPIC Original): spinning BY puncture + massive particle (m_p={m_p})

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
integrator = rk4
cfl_number = 0.25
nlim       = -1
tlim       = {TLIM_BH:.1f}
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
find_every        = 38
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
pusher         = midpoint
interp         = hermite
metric         = mesh
tolerance      = 2.0e-14
max_iterations = 200
deposit        = true
deposit_shape  = tsc
deposit_comp_c = 0.0
nfilter        = 2
filter_compensate = false
filter_metric_conservative = false
filter_densitized = false
source_stage_extrap = false
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
hist_dcycle    = 12
traj_dcycle    = 6
traj_ntrack    = 1
nparticles     = 1
p0_x1          = 3.500000
p0_x2          = 0.0
p0_x3          = 0.0
p0_u1          = 0.0
p0_u2          = 0.680000
p0_u3          = 0.0
p0_m           = {m_p:.12e}

<problem>
pgen_name   = nrpic_cf
ncomp       = 1
comp0_type  = puncture
comp0_mass  = 0.650000
comp0_x1    = 0.0
comp0_x2    = 0.0
comp0_x3    = 0.0
comp0_p1    = 0.0
comp0_p2    = {p2_bh:.12e}
comp0_p3    = 0.0
comp0_s1    = 0.0
comp0_s2    = 0.0
comp0_s3    = 0.700000
lapse       = precollapsed
puncture_setup = false

<output1>
file_type = hst
dt        = 0.5
"""


def is_complete(rdir: str, prefix: str) -> bool:
    log = os.path.join(rdir, "stdout.log")
    co = os.path.join(rdir, f"{prefix}.co_0.txt")
    return os.path.isfile(log) and os.path.isfile(co) and ("Terminating on time limit" in open(log).read())


def run_orig_case(case: str, m_p: float) -> str:
    rdir = os.path.join(CMP_ROOT, case)
    if is_complete(rdir, case) and os.environ.get("RERUN_BACKCMP", "0") != "1":
        print(f"[SKIP] {case} (m_p={m_p}) already complete in {rdir}", flush=True)
        return rdir

    if os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(os.path.join(rdir, "waveforms"), exist_ok=True)
    ath = os.path.join(rdir, f"{case}.athinput")
    with open(ath, "w") as f:
        f.write(make_orig_athinput(case, m_p))

    print(f"[RUN]  Starting {case} (NRPIC Original, m_p={m_p}, tlim={TLIM_BH}M) on B200 GPU...", flush=True)
    t0 = time.time()
    log_path = os.path.join(rdir, "stdout.log")
    with open(log_path, "w") as flog:
        rc = subprocess.run([BIN_GPU, "-i", f"{case}.athinput"], cwd=rdir, stdout=flog, stderr=subprocess.STDOUT, check=False).returncode
    wt = time.time() - t0
    txt = open(log_path).read() if os.path.isfile(log_path) else ""
    with open(log_path, "a") as flog:
        flog.write(f"\nwall_sec={wt:.2f}\n")

    if rc != 0 or ("Terminating on time limit" not in txt) or re.search(r"\bNaN\b", txt, re.I) or ("converged after" not in txt):
        raise RuntimeError(f"{case} failed validation (rc={rc}, wall={wt:.1f}s):\n{txt[-1500:]}")
    if wt > WALL_CAP_ORIG:
        raise RuntimeError(f"{case} exceeded wall cap ({wt:.1f}s > {WALL_CAP_ORIG}s)")
    ah = safe_loadtxt(os.path.join(rdir, f"{case}.horizon_summary_0.txt"))
    ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
    if len(ah) < 10 or float(ah[-1, 1]) < 0.7 * TLIM_BH:
        raise RuntimeError(f"{case} FastFlow AH coverage lost early: n={len(ah)}, t_last={ah[-1,1] if len(ah) else 0}")
    print(f"[DONE] {case} finished in {wt:.1f} s ({wt/60:.2f} min)", flush=True)
    return rdir


def ylm(l: int, m: int, theta: np.ndarray, phi: np.ndarray):
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += (((-1.0) ** k) * (c ** (2 * l + m - 2 * k)) * (s ** (2 * k - m))
              / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m)))
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_eq_ring(sh_path: str, t_target: float, cx: float, cy: float):
    shapes, t_cur = {}, None
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
    return (cx + rr * np.cos(phi)).astype(np.float32), (cy + rr * np.sin(phi)).astype(np.float32)


def reduce_bh_run(key: str, rdir: str, prefix: str) -> dict:
    txt = open(os.path.join(rdir, "stdout.log")).read()
    mw = re.search(r"wall_sec=([0-9.eE+-]+)", txt)
    mc = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    wt = float(mw.group(1)) if mw else float(mc.group(1))
    cycs = re.findall(r"\bcycle=([0-9]+)", txt)
    cyc = int(cycs[-1]) if cycs else 0

    nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.nrpic.hst")), 0)
    exc = np.where(nh[:, 16] > 0.5)[0]
    t_exc = float(nh[int(exc[0]), 0]) if len(exc) else np.nan
    act = (nh[:, 16] < 0.5) & (np.abs(nh[:, 8]) > 1e-12)
    fmax = float(np.max(np.abs(nh[act, 23] - nh[act, 8]) / np.maximum(np.abs(nh[act, 8]), 1e-30)))

    raw = np.fromfile(os.path.join(rdir, f"{prefix}.traj.bin"), dtype=np.float64).reshape(-1, 8)
    raw = dedup_time(raw[np.all(np.isfinite(raw), axis=1)], 0)
    if np.isfinite(t_exc):
        raw = raw[raw[:, 0] <= t_exc + 1e-9]
    pt, px = raw[:, 0], raw[:, 2:5]

    co = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.co_0.txt")), 1)
    bt, bx = co[:, 1], co[:, 2:5]
    bh_p = np.column_stack([np.interp(pt, bt, bx[:, c]) for c in range(3)])
    r_rel = np.linalg.norm(px - bh_p, axis=1)
    r_bh_max = float(np.max(np.linalg.norm(bx, axis=1)))

    ah = safe_loadtxt(os.path.join(rdir, f"{prefix}.horizon_summary_0.txt"))
    ah = dedup_time(ah[np.isfinite(ah[:, 2])], 1)
    ah_t, ah_M = ah[:, 1], ah[:, 2]
    ah_chi = ah[:, 6] / (ah_M ** 2)

    re_p = os.path.join(rdir, "waveforms", "rpsi4_real_0014.txt")
    im_p = os.path.join(rdir, "waveforms", "rpsi4_imag_0014.txt")
    col22 = find_col_index(re_p, "6:22")
    wr = dedup_time(safe_loadtxt(re_p), 0)
    wi = dedup_time(safe_loadtxt(im_p), 0)
    nw = min(len(wr), len(wi))
    gt = wr[:nw, 0]
    amp = np.hypot(wr[:nw, col22], wi[:nw, col22])
    gw_peak = float(np.max(amp[gt >= 26.0]))

    zh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.z4c.user.hst")), 0)
    hrms_max = float(np.max(np.sqrt(np.maximum(zh[:, 3] / np.maximum(zh[:, 10], 1.0), 0.0))))

    res = {
        f"bh_{key}_wall": np.float64(wt),
        f"bh_{key}_cycles": np.int64(cyc),
        f"bh_{key}_t_exc": np.float64(t_exc),
        f"bh_{key}_filt_max": np.float64(fmax),
        f"bh_{key}_r_bh_max": np.float64(r_bh_max),
        f"bh_{key}_gw_peak": np.float64(gw_peak),
        f"bh_{key}_H_rms_max": np.float64(hrms_max),
        f"bh_{key}_p_t": pt.astype(np.float32),
        f"bh_{key}_p_xy": px[:, :2].astype(np.float32),
        f"bh_{key}_r_rel": r_rel.astype(np.float32),
        f"bh_{key}_bh_xy": bx[::max(1, len(bx)//500), :2].astype(np.float32),
        f"bh_{key}_ah_t": ah_t.astype(np.float32),
        f"bh_{key}_ah_M": ah_M.astype(np.float32),
        f"bh_{key}_ah_chi": ah_chi.astype(np.float32),
    }
    if key == "best_q005":
        k28 = int(np.argmin(np.abs(bt - 28.0)))
        hx, hy = horizon_eq_ring(os.path.join(rdir, f"{prefix}.horizon_shape_0.txt"),
                                 28.0, float(bx[k28, 0]), float(bx[k28, 1]))
        res["bh_ah_hx"] = hx
        res["bh_ah_hy"] = hy
    return res


def reduce_jeans() -> dict:
    out = {}
    specs = [
        ("j10k_orig",  "jeans_10k_strat_mid"),
        ("j10k_best",  "jeans_10k_qmc_hyb"),
        ("j100k_orig", "jeans_100k_strat_mid"),
        ("j100k_best", "jeans_100k_qmc_hyb"),
    ]
    for key, name in specs:
        rdir = os.path.join(W4C_ROOT, name)
        c0 = dedup_time(safe_loadtxt(os.path.join(rdir, f"{name}.co_0.txt")), 1)
        c1 = dedup_time(safe_loadtxt(os.path.join(rdir, f"{name}.co_1.txt")), 1)
        n = min(len(c0), len(c1))
        c0, c1 = c0[:n], c1[:n]
        m20 = c0[:, 1] <= 20.02
        c0m, c1m = c0[m20], c1[m20]
        st = max(1, len(c0m) // 350)
        nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{name}.nrpic.hst")), 0)
        m20n = nh[:, 0] <= 20.02
        filt = float(np.max(np.abs(nh[m20n, 23] - nh[m20n, 8]) / np.maximum(np.abs(nh[m20n, 8]), 1e-30)))
        pnorm = float(np.max(np.linalg.norm(nh[m20n, 5:8], axis=1)) / max(float(nh[0, 3]), 1e-30))
        d_ab = float(np.linalg.norm(c0m[-1, 2:5] - c1m[-1, 2:5]))
        z0_max = float(np.max(np.abs(c0m[:, 4])))

        out[f"{key}_t"] = c0m[::st, 1].astype(np.float32)
        out[f"{key}_co0"] = c0m[::st, 2:5].astype(np.float32)
        out[f"{key}_co1"] = c1m[::st, 2:5].astype(np.float32)
        out[f"{key}_dAB_end"] = np.float64(d_ab)
        out[f"{key}_z0_max"] = np.float64(z0_max)
        out[f"{key}_filt_max"] = np.float64(filt)
        out[f"{key}_pnorm_max"] = np.float64(pnorm)
    return out


def reduce_st() -> dict:
    out = {}
    specs = [
        ("st0500_orig", os.path.join(W4B_M5C, "st_yc0500_vp01_10k_mid"), "st_yc0500_vp01_10k_mid"),
        ("st0500_best", os.path.join(I5_ROOT, "st10k_rk3_040_dir4c_s2"), "st10k_rk3_040_dir4c_s2"),
        ("st0605_orig", os.path.join(W4B_M5C, "st_yc0605_vp01_10k_mid"), "st_yc0605_vp01_10k_mid"),
        ("st0605_best", os.path.join(W4B_M5C, "st_yc0605_vp01_10k_hyb"), "st_yc0605_vp01_10k_hyb"),
    ]
    for key, rdir, pref in specs:
        nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{pref}.nrpic.hst")), 0)
        ts, ac = downsample_2col(nh[:, 0], nh[:, 12], max_pts=450)
        pnorm = float(np.max(np.linalg.norm(nh[:, 5:8], axis=1)) / max(float(nh[0, 3]), 1e-30))
        ah = safe_loadtxt(os.path.join(rdir, f"{pref}.horizon_summary_0.txt"))
        ah = dedup_time(ah[np.isfinite(ah[:, 2])], 1)
        t_ah = float(ah[0, 1]) if len(ah) else np.nan
        m_ah = float(ah[-1, 2]) if len(ah) else np.nan
        idx_ah = int(np.argmin(np.abs(nh[:, 0] - t_ah))) if np.isfinite(t_ah) else 0
        ac_ah = float(nh[idx_ah, 12])
        # Wall time if logged
        wall = np.nan
        log_p = os.path.join(rdir, f"{pref}.stdout.log")
        if os.path.isfile(log_p):
            mw = re.search(r"# wall_s = ([0-9.eE+-]+)", open(log_p).read())
            if mw:
                wall = float(mw.group(1))
        out[f"{key}_t"] = ts.astype(np.float32)
        out[f"{key}_ac"] = ac.astype(np.float32)
        out[f"{key}_t_AH"] = np.float64(t_ah)
        out[f"{key}_M_AH"] = np.float64(m_ah)
        out[f"{key}_ac_AH"] = np.float64(ac_ah)
        out[f"{key}_pnorm_max"] = np.float64(pnorm)
        out[f"{key}_wall"] = np.float64(wall)
    return out


def build_or_load_data() -> dict:
    if os.path.isfile(DATA_OUT) and os.environ.get("RERUN_BACKCMP", "0") != "1":
        print(f"[CACHE] Loading {DATA_OUT}", flush=True)
        return dict(np.load(DATA_OUT, allow_pickle=False))

    # Run orig_q010 and orig_q002 on B200 GPU (reusing orig_q005 & best_q{002,005,010})
    for case, _, m_p in ORIG_RUN_SPECS:
        run_orig_case(case, m_p)

    out = {}
    for qtag, _, _, _ in BH_QS:
        odir = os.path.join(CMP_ROOT, f"orig_{qtag}")
        bdir = os.path.join(BEST_ROOT, qtag)
        if not is_complete(odir, f"orig_{qtag}"):
            raise FileNotFoundError(f"Missing completed orig run: {odir}")
        if not is_complete(bdir, qtag):
            raise FileNotFoundError(f"Missing completed best run: {bdir}")
        out.update(reduce_bh_run(f"orig_{qtag}", odir, f"orig_{qtag}"))
        out.update(reduce_bh_run(f"best_{qtag}", bdir, qtag))

    out.update(reduce_jeans())
    out.update(reduce_st())

    os.makedirs(DATA_DIR, exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"[SAVE] {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def print_summary(D: dict):
    print("\n" + "=" * 112)
    print("ALL-BACK-REACTION MASSIVE-PARTICLE COMPARISON: NRPIC Original vs Our Best GR-LBV")
    print("-" * 112)
    print("1) Spinning BH + Massive Particle Ladder (q in {0.02, 0.05, 0.10}, B200 GPU, tlim = 80M):")
    print(f"  {'Run':<11} {'Wall[s]':>8} {'Spd':>6} {'t_exc':>6} {'M_AH(0->T)':>15} {'chi(0->T)':>13} {'max|x_BH|':>9} {'max|dE/E|':>11} {'pk|Psi4|':>10} {'max Hrms':>9}")
    for qtag, _, _, _ in BH_QS:
        wo = float(D[f"bh_orig_{qtag}_wall"])
        wb = float(D[f"bh_best_{qtag}_wall"])
        for meth, sp_s in [("orig", "  1.00x"), ("best", f"{wo/wb:5.2f}x")]:
            k = f"{meth}_{qtag}"
            wt = float(D[f"bh_{k}_wall"])
            te = float(D[f"bh_{k}_t_exc"])
            am = D[f"bh_{k}_ah_M"]; ac = D[f"bh_{k}_ah_chi"]
            rb = float(D[f"bh_{k}_r_bh_max"]); fm = float(D[f"bh_{k}_filt_max"])
            gp = float(D[f"bh_{k}_gw_peak"]); hm = float(D[f"bh_{k}_H_rms_max"])
            lbl = f"{meth}_{qtag}"
            print(f"  {lbl:<11} {wt:8.1f} {sp_s:>6} {te:6.2f} {float(am[0]):6.4f}->{float(am[-1]):6.4f} "
                  f"{float(ac[0]):5.3f}->{float(ac[-1]):5.3f} {rb:9.4f} {fm:11.3e} {gp:10.3e} {hm:9.3e}")

    print("-" * 112)
    print("2) Live 8-level AMR Jeans Binary BH Formation (N = 10^4, 10^5 massive particles, t <= 20 M):")
    for key, name in [("j10k_orig", "Jeans 10k Original"), ("j10k_best", "Jeans 10k Best QMC+GL4"),
                      ("j100k_orig", "Jeans 100k Original"), ("j100k_best", "Jeans 100k Best QMC+GL4")]:
        print(f"  {name:<26}: dAB(20M)={float(D[f'{key}_dAB_end']):.3f}M, "
              f"max|z0|={float(D[f'{key}_z0_max']):.4f}M, max|dE_f/E|={float(D[f'{key}_filt_max']):.3e}, max|P|/M0={float(D[f'{key}_pnorm_max']):.3e}")

    print("-" * 112)
    print("3) Live 9-level AMR Shapiro-Teukolsky Relativistic Cluster Collapse (N = 10^4, yc = 0.500 & 0.605):")
    for key, name in [("st0500_orig", "ST yc=0.500 Original"), ("st0500_best", "ST yc=0.500 Best (Iter5)"),
                      ("st0605_orig", "ST yc=0.605 Original"), ("st0605_best", "ST yc=0.605 Best (QMC+GL4)")]:
        print(f"  {name:<26}: t_AH={float(D[f'{key}_t_AH']):6.2f}M, M_AH={float(D[f'{key}_M_AH']):.4f}M, "
              f"max|P|/M0={float(D[f'{key}_pnorm_max']):.3e}")
    print("=" * 112 + "\n", flush=True)


def make_figure(D: dict):
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 6.8))
    fig.subplots_adjust(left=0.085, right=0.915, bottom=0.085, top=0.945, wspace=0.35, hspace=0.30)

    # ------------------------------------------------------------------
    # Top-Left: Spinning BH + Massive Particle Ladder Equatorial Orbits
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    ax.fill(D["bh_ah_hx"], D["bh_ah_hy"], color="0.16", alpha=0.86, zorder=2)
    for qtag, _, _, col in BH_QS:
        for meth, ls, lw, zo in [("orig", "--", 1.4, 4), ("best", "-", 1.65, 5)]:
            px = D[f"bh_{meth}_{qtag}_p_xy"]
            bx = D[f"bh_{meth}_{qtag}_bh_xy"]
            ax.plot(px[:, 0], px[:, 1], color=col, ls=ls, lw=lw, zorder=zo)
            ax.plot(bx[:, 0], bx[:, 1], color=col, ls=ls, lw=1.05, alpha=0.82, zorder=zo)
    ax.plot([3.5], [0.0], "o", color="k", ms=4.5, zorder=7)
    ax.set_xlim(-3.3, 4.6)
    ax.set_ylim(-3.3, 4.6)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.96, r"Spinning BH $+ \,m_p=q M_0$" "\n(inner: recoiling BH)",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.4, color="0.15")
    h_tl = [
        Line2D([], [], color=cz.PAL["green"], lw=1.6, label=r"$q=0.02$"),
        Line2D([], [], color=cz.PAL["orange"], lw=1.6, label=r"$q=0.05$"),
        Line2D([], [], color=cz.PAL["red"], lw=1.6, label=r"$q=0.10$"),
        Line2D([], [], color="0.15", lw=1.6, ls="-", label="Our Best"),
        Line2D([], [], color="0.15", lw=1.4, ls="--", label="Original"),
    ]
    ax.legend(handles=h_tl, loc="lower left", ncol=2, columnspacing=0.65, fontsize=6.5, frameon=False)

    # ------------------------------------------------------------------
    # Top-Right: Spinning BH Ladder r_rel(t) (left) & M_AH(t) (right)
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax2.tick_params(which="both", direction="in")
    for qtag, _, _, col in BH_QS:
        for meth, ls, lw in [("orig", "--", 1.35), ("best", "-", 1.6)]:
            pt = D[f"bh_{meth}_{qtag}_p_t"]
            rr = D[f"bh_{meth}_{qtag}_r_rel"]
            at = D[f"bh_{meth}_{qtag}_ah_t"]
            aM = D[f"bh_{meth}_{qtag}_ah_M"]
            ax.plot(pt, rr, color=col, ls=ls, lw=lw, zorder=4)
            ax2.plot(at, aM, color=col, ls=ls, lw=1.15, alpha=0.88, zorder=3)
    ax.set_xlim(0.0, 52.0)
    ax.set_ylim(0.0, 4.7)
    ax2.set_ylim(0.950, 1.070)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Separation $r_{\rm rel}\,[M]$ (upper/drop)")
    ax2.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$ (lower steps)", fontsize=8.8)
    ax.text(0.04, 0.96,
            r"Filter leak $\Rightarrow$ delayed plunge $t_{\rm exc}$" "\n"
            r"GPU: $\sim 498\,\mathrm{s} \to 281\,\mathrm{s}$ ($1.77\times$)",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.9, color="0.18")
    ax.legend(handles=h_tl, loc="center right", bbox_to_anchor=(0.99, 0.68),
              ncol=2, columnspacing=0.6, fontsize=6.4, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Left: Live 8-Level AMR Jeans Binary BH Formation (10k, 100k)
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    j_specs = [
        ("j10k",  r"$N=10^4$", cz.PAL["blue"]),
        ("j100k", r"$N=10^5$", cz.PAL["red"]),
    ]
    for pfx, nlbl, col in j_specs:
        for meth, ls, lw in [("orig", "--", 1.45), ("best", "-", 1.65)]:
            k = f"{pfx}_{meth}"
            c0, c1 = D[f"{k}_co0"], D[f"{k}_co1"]
            ax.plot(c0[:, 0], c0[:, 1], color=col, ls=ls, lw=lw)
            ax.plot(c1[:, 0], c1[:, 1], color=col, ls=ls, lw=lw)
            ax.plot([c0[-1, 0], c1[-1, 0]], [c0[-1, 1], c1[-1, 1]],
                    "o" if meth == "best" else "s", color=col, mec="k", mew=0.4, ms=4.0, zorder=6)
    ax.set_xlim(-3.7, 3.7)
    ax.set_ylim(-2.5, 3.2)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$")
    ax.text(0.04, 0.96, r"Jeans Binary BH ($t \leq 20\,M$)" "\n(8-lvl AMR, 2 BHs)",
            transform=ax.transAxes, ha="left", va="top", fontsize=7.2, color="0.15")
    h_j = [
        Line2D([], [], color=cz.PAL["blue"], lw=1.6, label=r"$10^4$"),
        Line2D([], [], color=cz.PAL["red"], lw=1.6, label=r"$10^5$"),
        Line2D([], [], color="0.15", lw=1.6, ls="-", label="Best QMC+GL4"),
        Line2D([], [], color="0.15", lw=1.4, ls="--", label="Orig MC+Mid"),
    ]
    ax.legend(handles=h_j, loc="upper left", bbox_to_anchor=(0.01, 0.80), ncol=2,
              columnspacing=0.55, fontsize=6.1, frameon=False)

    # Clean inset showing vertical kick |z_0(t)| suppression (4.1x for 10k, 2.4x for 100k)
    axins = ax.inset_axes([0.54, 0.07, 0.42, 0.29])
    for pfx, _, col in j_specs:
        for meth, ls, lw in [("orig", "--", 1.1), ("best", "-", 1.3)]:
            k = f"{pfx}_{meth}"
            axins.plot(D[f"{k}_t"], np.abs(D[f"{k}_co0"][:, 2]), color=col, ls=ls, lw=lw)
    axins.set_xlim(0.0, 20.0)
    axins.set_ylim(-0.01, 0.33)
    axins.set_xticks([0, 10, 20])
    axins.set_yticks([0.0, 0.15, 0.3])
    axins.tick_params(labelsize=6.2, pad=1, direction="in", top=True, right=True)
    axins.set_title(r"$|z_0(t)|\,[M]$ ($17\% \to 10^{-15}$)", fontsize=6.0, pad=2)

    # ------------------------------------------------------------------
    # Bottom-Right: Live 9-Level AMR Shapiro-Teukolsky Cluster Collapse
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    st_specs = [
        ("st0500", r"$y_c=0.500$", cz.PAL["red"]),
        ("st0605", r"$y_c=0.605$", cz.PAL["blue"]),
    ]
    for pfx, ylbl, col in st_specs:
        for meth, ls, lw, mk in [("orig", "--", 1.45, "s"), ("best", "-", 1.70, "o")]:
            k = f"{pfx}_{meth}"
            ax.plot(D[f"{k}_t"], D[f"{k}_ac"], color=col, ls=ls, lw=lw)
            tah = float(D[f"{k}_t_AH"])
            ac_ah = float(D[f"{k}_ac_AH"])
            ax.plot([tah], [ac_ah], mk, color=col, mec="k", mew=0.5, ms=4.8, zorder=6)
    ax.set_xlim(0.0, 215.0)
    ax.set_ylim(-0.02, 0.90)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Central lapse $\alpha_c(t)$")
    ax.text(0.97, 0.96,
            r"Shapiro–Teukolsky ($10^4$, 9-lvl AMR)" "\n"
            r"$t_{\rm AH}$: $104 \to 76.7M$ ($y_c=0.500$, $2.36\times$ GPU)" "\n"
            r"$|\mathbf{P}|/M_0$: 0.12–0.23 $\to \leq 1.7\times 10^{-14}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.2, color="0.18")
    h_st = [
        Line2D([], [], color=cz.PAL["red"], lw=1.6, label=r"$y_c=0.500$"),
        Line2D([], [], color=cz.PAL["blue"], lw=1.6, label=r"$y_c=0.605$"),
        Line2D([], [], color="0.15", lw=1.6, ls="-", label=r"Best ($\bullet\,t_{\rm AH}$)"),
        Line2D([], [], color="0.15", lw=1.4, ls="--", label=r"Orig ($\blacksquare\,t_{\rm AH}$)"),
    ]
    ax.legend(handles=h_st, loc="lower left", handlelength=1.4, fontsize=6.1, frameon=False, labelspacing=0.20)

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
