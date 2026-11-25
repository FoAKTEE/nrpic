#!/usr/bin/env python3
"""Head-to-head comparison: NRPIC Original (Wu & Most 2026 baseline) vs Our Best GR-LBV methods.

1. Live 3+1 GPU comparison on the q = 0.05 spinning Bowen-York puncture + massive particle
   problem (`comp0_mass=0.65`, `comp0_s3=0.70`, `p0_x1=3.5`, `p0_u2=0.68`, `p0_m=0.05`,
   `tlim=80.0M`, `build_gpu_iter5/src/athena` on NVIDIA B200):
     - `orig_q005`:      RK4 (cfl=0.25), midpoint pusher, cubic Hermite, plain filter, frozen source
     - `best_q005`:      RK3 (cfl=0.40), GL4+quad time, quintic Hermite, unsplit mcons, Scheme A (reused)
     - `best_fast_q005`: RK3 (cfl=0.45), GL4+quad time, quintic Hermite, unsplit mcons, Scheme A, K_m=2

2. Cross-suite benchmark aggregation from cached datasets in `vlasov_gr/paper/data/`:
   - Kerr a=0.999, e=0.999 geodesic energy/trajectory accuracy (`physics_kerr_a0999_e0999.npz`)
   - Kerr a=0.90 null light-ring separatrix turn accuracy (`physics_kerr_a090_lightring.npz`)
   - 6-level SMR Kerr quintic vs Hermite invariant conservation (`iter4_quintic_kerr_diag.npz`)
   - 7-level OS collapse Scheme A stage accuracy & CFL/multirate B200 GPU speedups (`iter4_stagea_curves.npz`, `iter5_pareto_curves.npz`)
   - 9-level ST nonlinear collapse symmetry-exact momentum conservation & GPU speedup (`iter4_stagea_curves.npz`, `iter5_pareto_curves.npz`)

Saves reduced data to `vlasov_gr/paper/data/compare_nrpic_orig_vs_best.npz` and renders
`vlasov_gr/paper/figures/fig_compare_nrpic_orig_vs_best.{pdf,png}`.
"""
import os
import re
import shutil
import subprocess
import sys
import time
import numpy as np
import matplotlib.pyplot as plt

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
BEST_FULL_DIR = f"{SCRATCH}/runs/bh_massive_backreaction/q005"
DATA_OUT = os.path.join(DATA_DIR, "compare_nrpic_orig_vs_best.npz")
FIG_OUT = os.path.join(PAPER_DIR, "figures", "fig_compare_nrpic_orig_vs_best")

TLIM = 80.0
WALL_CAP_ORIG = 720.0  # 12 min guardrail for rk4 cfl=0.25 (5120 cyc)
WALL_CAP_FAST = 390.0  # 6.5 min guardrail for rk3 multirate


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


def make_athinput(case: str, mode: str, fast_cfl: float = 0.45, fast_stride: int = 2) -> str:
    if mode == "orig":
        integrator = "rk4"
        cfl = 0.25
        find_every = 38
        hist_dcycle = 12
        traj_dcycle = 6
        part_block = """pusher         = midpoint
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
matter_stride  = 1"""
    elif mode == "fast":
        integrator = "rk3"
        cfl = fast_cfl
        if abs(fast_cfl - 0.45) < 1e-6:
            find_every, hist_dcycle, traj_dcycle = 21, 7, 4
        else:
            find_every, hist_dcycle, traj_dcycle = 24, 8, 4
        part_block = f"""pusher         = vlasov_hybrid
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
matter_stride  = {fast_stride}"""
    else:
        raise ValueError(f"Unknown mode {mode}")

    return f"""<comment>
problem = {case} ({mode}): spinning BY puncture + massive particle (q=0.05)

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
integrator = {integrator}
cfl_number = {cfl:.4f}
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
find_every        = {find_every}
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
{part_block}
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
hist_dcycle    = {hist_dcycle}
traj_dcycle    = {traj_dcycle}
traj_ntrack    = 1
nparticles     = 1
p0_x1          = 3.500000
p0_x2          = 0.0
p0_x3          = 0.0
p0_u1          = 0.0
p0_u2          = 0.680000
p0_u3          = 0.0
p0_m           = 5.000000000000e-02

<problem>
pgen_name   = nrpic_cf
ncomp       = 1
comp0_type  = puncture
comp0_mass  = 0.650000
comp0_x1    = 0.0
comp0_x2    = 0.0
comp0_x3    = 0.0
comp0_p1    = 0.0
comp0_p2    = -3.400000000000e-02
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


def is_complete(rdir: str, case: str) -> bool:
    log = os.path.join(rdir, "stdout.log")
    co = os.path.join(rdir, f"{case}.co_0.txt")
    if not (os.path.isfile(log) and os.path.isfile(co)):
        return False
    return "Terminating on time limit" in open(log).read()


def run_live_case(case: str, mode: str, wall_cap: float):
    rdir = os.path.join(CMP_ROOT, case)
    if is_complete(rdir, case) and os.environ.get("RERUN_COMPARE", "0") != "1":
        print(f"[SKIP] {case} already completed in {rdir}", flush=True)
        return rdir

    attempts = [(0.45, 2), (0.40, 2)] if mode == "fast" else [(0.25, 1)]
    last_err = None
    for cfl, stride in attempts:
        if os.path.exists(rdir):
            shutil.rmtree(rdir)
        os.makedirs(os.path.join(rdir, "waveforms"), exist_ok=True)
        ath = os.path.join(rdir, f"{case}.athinput")
        with open(ath, "w") as f:
            f.write(make_athinput(case, mode, fast_cfl=cfl, fast_stride=stride))

        print(f"[RUN]  Starting {case} ({mode}, cfl={cfl}, K_m={stride}) on B200 GPU...", flush=True)
        t0 = time.time()
        log_path = os.path.join(rdir, "stdout.log")
        with open(log_path, "w") as flog:
            rc = subprocess.run(
                [BIN_GPU, "-i", f"{case}.athinput"],
                cwd=rdir, stdout=flog, stderr=subprocess.STDOUT, check=False,
            ).returncode
        wt = time.time() - t0
        txt = open(log_path).read() if os.path.isfile(log_path) else ""
        with open(log_path, "a") as flog:
            flog.write(f"\nwall_sec={wt:.2f}\n")

        ok = (
            rc == 0
            and "Terminating on time limit" in txt
            and not re.search(r"\bNaN\b", txt, re.IGNORECASE)
            and "converged after" in txt
        )
        ah = safe_loadtxt(os.path.join(rdir, f"{case}.horizon_summary_0.txt")) if ok else np.zeros((0, 0))
        ah = ah[np.isfinite(ah[:, 2])] if len(ah) else ah
        ah_ok = len(ah) >= 10 and float(ah[-1, 1]) >= 0.7 * TLIM
        if ok and ah_ok and wt <= wall_cap:
            print(f"[DONE] {case} (cfl={cfl}, K_m={stride}) finished in {wt:.1f} s ({wt/60:.2f} min)", flush=True)
            return rdir
        last_err = f"{case} (cfl={cfl}, K_m={stride}) failed: rc={rc}, wall={wt:.1f}s, ok={ok}, ah_ok={ah_ok}"
        print(f"[WARN] {last_err}", flush=True)

    raise RuntimeError(last_err)


def reduce_live_run(tag: str, rdir: str, prefix: str) -> dict:
    txt = open(os.path.join(rdir, "stdout.log")).read()
    m_wall = re.search(r"wall_sec=([0-9.eE+-]+)", txt)
    m_cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    cycs = re.findall(r"\bcycle=([0-9]+)", txt)
    m_adm = re.search(r"M_psi\s*=\s*([0-9.eE+-]+)", txt)
    wt = float(m_wall.group(1)) if m_wall else float(m_cpu.group(1))
    cyc = int(cycs[-1]) if cycs else 0
    m_psi = float(m_adm.group(1)) if m_adm else np.nan

    # Active pre-excision filter drift and energy floor
    nh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.nrpic.hst")), 0)
    active = (nh[:, 16] < 0.5) & (np.abs(nh[:, 8]) > 1e-12)
    nh_act = nh[active]
    filt_t = nh_act[:, 0]
    filt_drift = np.abs(nh_act[:, 23] - nh_act[:, 8]) / np.maximum(np.abs(nh_act[:, 8]), 1e-30)
    exc_rows = np.where(nh[:, 16] > 0.5)[0]
    t_exc = float(nh[int(exc_rows[0]), 0]) if len(exc_rows) else np.nan
    E_min = float(np.min(nh[:, 31]))

    # Particle and BH trajectories
    raw = np.fromfile(os.path.join(rdir, f"{prefix}.traj.bin"), dtype=np.float64).reshape(-1, 8)
    raw = raw[np.all(np.isfinite(raw), axis=1)]
    raw = dedup_time(raw, 0)
    t_p, xy_p = raw[:, 0], raw[:, 2:5]
    if np.isfinite(t_exc):
        m = t_p <= t_exc + 1e-9
        t_p, xy_p = t_p[m], xy_p[m]

    co = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.co_0.txt")), 1)
    t_bh, xy_bh = co[:, 1], co[:, 2:5]
    bh_at_p = np.column_stack([np.interp(t_p, t_bh, xy_bh[:, c]) for c in range(3)])
    r_rel = np.linalg.norm(xy_p - bh_at_p, axis=1)
    r_bh = np.linalg.norm(xy_bh, axis=1)

    # Apparent horizon
    ah = safe_loadtxt(os.path.join(rdir, f"{prefix}.horizon_summary_0.txt"))
    ah = dedup_time(ah[np.isfinite(ah[:, 2])], 1)
    ah_t, ah_M = ah[:, 1], ah[:, 2]
    ah_chi = ah[:, 6] / (ah_M ** 2)

    # Quadrupole waveform
    re_path = os.path.join(rdir, "waveforms", "rpsi4_real_0014.txt")
    im_path = os.path.join(rdir, "waveforms", "rpsi4_imag_0014.txt")
    col22 = find_col_index(re_path, "6:22")
    wr = dedup_time(safe_loadtxt(re_path), 0)
    wi = dedup_time(safe_loadtxt(im_path), 0)
    nw = min(len(wr), len(wi))
    gw_t, gw_re, gw_im = wr[:nw, 0], wr[:nw, col22], wi[:nw, col22]
    gw_peak_pj = float(np.max(np.hypot(gw_re[gw_t >= 26.0], gw_im[gw_t >= 26.0])))

    # Z4c Hamiltonian constraint RMS
    zh = dedup_time(safe_loadtxt(os.path.join(rdir, f"{prefix}.z4c.user.hst")), 0)
    H_rms = np.sqrt(np.maximum(zh[:, 3] / np.maximum(zh[:, 10], 1.0), 0.0))

    return {
        f"{tag}_wall": np.float64(wt),
        f"{tag}_cycles": np.int64(cyc),
        f"{tag}_M_psi": np.float64(m_psi),
        f"{tag}_t_exc": np.float64(t_exc),
        f"{tag}_E_min": np.float64(E_min),
        f"{tag}_filt_t": filt_t,
        f"{tag}_filt_drift": filt_drift,
        f"{tag}_filt_max": np.float64(np.max(filt_drift)),
        f"{tag}_p_t": t_p,
        f"{tag}_r_rel": r_rel,
        f"{tag}_bh_t": t_bh,
        f"{tag}_r_bh": r_bh,
        f"{tag}_ah_t": ah_t,
        f"{tag}_ah_M": ah_M,
        f"{tag}_ah_chi": ah_chi,
        f"{tag}_gw_t": gw_t,
        f"{tag}_gw_re": gw_re,
        f"{tag}_gw_im": gw_im,
        f"{tag}_gw_peak_pj": np.float64(gw_peak_pj),
        f"{tag}_H_t": zh[:, 0],
        f"{tag}_H_rms": H_rms,
        f"{tag}_H_rms_max": np.float64(np.max(H_rms)),
    }


def load_cross_suite_metrics() -> dict:
    def ld(fn):
        return dict(np.load(os.path.join(DATA_DIR, fn), allow_pickle=False))

    k999 = ld("physics_kerr_a0999_e0999.npz")
    k90 = ld("physics_kerr_a090_lightring.npz")
    q4 = ld("iter4_quintic_kerr_diag.npz")
    s4 = ld("iter4_stagea_curves.npz")
    p5 = ld("iter5_pareto_curves.npz")

    return {
        # Accuracy / conservation metrics: [orig, best]
        "acc_kerr999_dE_orig": np.float64(np.max(k999["mid_dE"])),
        "acc_kerr999_dE_best": np.float64(np.max(k999["gl4_dE"])),
        "acc_kerr999_dx_orig": np.float64(np.max(k999["mid_dx"])),
        "acc_kerr999_dx_best": np.float64(np.max(k999["gl4_dx"])),
        "acc_lr_dN_orig": np.float64(np.median(np.abs(k90["mid_dt05_turns"] - k90["dop_turns"]))),
        "acc_lr_dN_best": np.float64(np.median(np.abs(k90["gl4_dt05_turns"] - k90["dop_turns"]))),
        "acc_m4_med_dE_orig": np.float64(np.median(q4["hermite_ng4_dE"])),
        "acc_m4_med_dE_best": np.float64(np.median(q4["quintic_ng4_dE"])),
        "acc_os_alphac_orig": np.float64(s4["cfl_frozen_alpha_c_rel025"]),
        "acc_os_alphac_best": np.float64(s4["cfl_stageA_alpha_c_rel025"]),
        "acc_st_mom_orig": np.float64(np.max(s4["ref_st_yc0500_vp01_10k_mid_pnorm"])),
        "acc_st_mom_best": np.float64(np.max(s4["st_quin_stgA_pnorm"])),
        # GPU wall times (B200): [orig, best]
        "spd_os10k_orig": np.float64(p5["os10k_rk4_025_dir1_wall"]),
        "spd_os10k_best": np.float64(p5["os10k_rk3_045_uns1_s2_wall"]),
        "spd_os100k_orig": np.float64(p5["os100k_rk4_025_dir_s1_wall"]),
        "spd_os100k_best": np.float64(p5["os100k_rk3_040_uns3_s2_wall"]),
        "spd_st10k_orig": np.float64(s4["st_herm_froz_wall"]),
        "spd_st10k_best": np.float64(p5["st10k_rk3_040_dir4c_s2_wall"]),
        "spd_m4_orig": np.float64(q4["hermite_ng4_wall"]),
        "spd_m4_best": np.float64(p5["m4_uns_nf1_wall"]),
    }


def build_or_load_data() -> dict:
    if os.path.isfile(DATA_OUT) and os.environ.get("RERUN_COMPARE", "0") != "1":
        print(f"[CACHE] Loading {DATA_OUT}", flush=True)
        return dict(np.load(DATA_OUT, allow_pickle=False))

    if not is_complete(BEST_FULL_DIR, "q005"):
        raise FileNotFoundError(f"Expected completed full-rate q005 run in {BEST_FULL_DIR}")

    rdir_fast = run_live_case("best_fast_q005", "fast", WALL_CAP_FAST)
    rdir_orig = run_live_case("orig_q005", "orig", WALL_CAP_ORIG)

    out = {}
    out.update(reduce_live_run("orig", rdir_orig, "orig_q005"))
    out.update(reduce_live_run("best", BEST_FULL_DIR, "q005"))
    out.update(reduce_live_run("fast", rdir_fast, "best_fast_q005"))
    out.update(load_cross_suite_metrics())

    os.makedirs(DATA_DIR, exist_ok=True)
    np.savez_compressed(DATA_OUT, **out)
    print(f"[SAVE] {DATA_OUT} ({os.path.getsize(DATA_OUT)/1e3:.1f} KB)", flush=True)
    return out


def print_summary(D: dict):
    print("\n" + "=" * 108)
    print("LIVE 3+1 SPINNING BH + MASSIVE PARTICLE (q = 0.05, R_ext = 14M, tlim = 80M, B200 GPU)")
    print(
        f"{'Variant':<16} {'Wall[s]':>8} {'Cycles':>7} {'t_exc':>7} {'M_AH(0->T)':>17} "
        f"{'chi(0->T)':>15} {'max|dE_f/E|':>12} {'peak|rPsi4|':>13} {'max H_rms':>10}"
    )
    print("-" * 108)
    for tag, name in [("orig", "NRPIC Original"), ("best", "Our Best (Km=1)"), ("fast", "Our Best (Km=2)")]:
        wt = float(D[f"{tag}_wall"])
        cyc = int(D[f"{tag}_cycles"])
        texc = float(D[f"{tag}_t_exc"])
        ahM = D[f"{tag}_ah_M"]
        chi = D[f"{tag}_ah_chi"]
        fm = float(D[f"{tag}_filt_max"])
        gp = float(D[f"{tag}_gw_peak_pj"])
        hm = float(D[f"{tag}_H_rms_max"])
        print(
            f"{name:<16} {wt:8.1f} {cyc:7d} {texc:7.2f} {ahM[0]:7.4f}->{ahM[-1]:7.4f} "
            f"{chi[0]:6.4f}->{chi[-1]:6.4f} {fm:12.3e} {gp:13.4e} {hm:10.3e}"
        )
    print("-" * 108)
    print("CROSS-SUITE ACCURACY & GPU SPEEDUP SUMMARY (NRPIC Original vs Our Best GR-LBV):")
    pairs = [
        ("Kerr 0.999 max|dE/E0|", D["acc_kerr999_dE_orig"], D["acc_kerr999_dE_best"]),
        ("Light ring med|dN_turn|", D["acc_lr_dN_orig"], D["acc_lr_dN_best"]),
        ("6-lvl Kerr med|dE/E0|", D["acc_m4_med_dE_orig"], D["acc_m4_med_dE_best"]),
        ("OS stage alpha_c rel err", D["acc_os_alphac_orig"], D["acc_os_alphac_best"]),
        ("ST 9-lvl max|P|/M0", D["acc_st_mom_orig"], D["acc_st_mom_best"]),
        ("BH q=0.05 filter max|dE/E|", D["orig_filt_max"], D["best_filt_max"]),
    ]
    for lbl, v0, v1 in pairs:
        print(f"  {lbl:<28}: orig={float(v0):.3e}  best={float(v1):.3e}  gain={float(v0)/max(float(v1), 1e-30):.2e}x")
    spds = [
        ("BH q=0.05 (Live GPU)", D["orig_wall"], D["fast_wall"]),
        ("OS 10^4 (7-lvl AMR)", D["spd_os10k_orig"], D["spd_os10k_best"]),
        ("OS 10^5 (7-lvl AMR)", D["spd_os100k_orig"], D["spd_os100k_best"]),
        ("ST 10^4 (9-lvl AMR)", D["spd_st10k_orig"], D["spd_st10k_best"]),
        ("M4 Kerr (6-lvl SMR)", D["spd_m4_orig"], D["spd_m4_best"]),
    ]
    for lbl, t0, t1 in spds:
        print(f"  {lbl:<28}: orig={float(t0):6.1f} s -> best={float(t1):6.1f} s  ({float(t0)/float(t1):.2f}x speedup)")
    print("=" * 108 + "\n", flush=True)


def fmt_gain(g: float) -> str:
    if g >= 1.0e4:
        exp = int(np.floor(np.log10(g)))
        mant = g / (10.0 ** exp)
        if exp >= 10:
            return rf"${mant:.0f}\!\times\!10^{{{exp}}}\times$"
        return rf"${mant:.1f}\!\times\!10^{{{exp}}}\times$"
    if g >= 100.0:
        return rf"${g:.0f}\times$"
    return rf"${g:.1f}\times$"


def make_figure(D: dict):
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.5, 6.4))
    fig.subplots_adjust(left=0.095, right=0.920, bottom=0.105, top=0.950, wspace=0.41, hspace=0.36)

    styles = [
        ("orig", "NRPIC Original",           cz.PAL["blue"],  "--", 1.55),
        ("best", r"Our Best ($K_m=1$)",      cz.PAL["red"],   "-",  1.65),
        ("fast", r"Our Best Fast ($K_m=2$)", cz.PAL["green"], "-.", 1.55),
    ]

    # ------------------------------------------------------------------
    # Top-Left: Live q=0.05 Post-Junk Quadrupole Waveform r Re Psi_4^{22}
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    t_cut = 25.0
    pos_max, neg_max = 1e-7, 1e-7
    for tag, lbl, col, ls, lw in styles:
        gt = D[f"{tag}_gw_t"]
        gre = D[f"{tag}_gw_re"]
        msk = gt >= t_cut
        pos_max = max(pos_max, float(np.max(gre[msk])))
        neg_max = max(neg_max, float(-np.min(gre[msk])))
        ax.plot(gt[msk], gre[msk] * 1.0e4, color=col, ls=ls, lw=lw, label=lbl)
    ax.axhline(0.0, color="0.7", lw=0.7, zorder=1)
    ax.set_xlim(t_cut, TLIM)
    ax.set_ylim(-1.32 * neg_max * 1.0e4, 1.48 * pos_max * 1.0e4)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^{4}\,r\,\mathrm{Re}\,\Psi_4^{22}\;[M^{-1}]$")
    ax.text(
        0.04, 0.95,
        r"Spinning BH $q=0.05$" "\n" r"($R_{\rm ext}=14\,M$)",
        transform=ax.transAxes, ha="left", va="top", fontsize=7.2, color="0.18",
    )
    ax.text(
        0.04, 0.05,
        rf"Wall: {float(D['orig_wall']):.0f}s $\to$ {float(D['best_wall']):.0f}s / {float(D['fast_wall']):.0f}s",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=7.0, color="0.18",
    )
    ax.legend(loc="upper right", fontsize=6.9, frameon=False, labelspacing=0.20)

    # ------------------------------------------------------------------
    # Top-Right: Filter Conservation Drift (left log) & M_AH(t) (right linear)
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax2.tick_params(which="both", direction="in")
    floor = 1.0e-16
    h_tr = []
    for tag, lbl, col, ls, lw in styles:
        ft = D[f"{tag}_filt_t"]
        fd = np.maximum(D[f"{tag}_filt_drift"], floor)
        h, = ax.semilogy(ft, fd, color=col, ls=ls, lw=lw, label=lbl, zorder=4)
        h_tr.append(h)
        ax2.plot(D[f"{tag}_ah_t"], D[f"{tag}_ah_M"], color=col, ls=ls, lw=1.25, alpha=0.88, zorder=3)
    ax.axhline(floor, color="grey", lw=0.8, ls=":", alpha=0.6)
    ax.set_xlim(0.0, TLIM)
    ax.set_ylim(2.0e-17, 1.0e1)
    cz.no_minor_labels(ax, "y")
    ax2.set_ylim(0.930, 1.032)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Filter drift $|I_E^{\rm filt}/I_E - 1|$", labelpad=2)
    ax2.set_ylabel(r"Horizon mass $M_{\rm AH}\,[M]$ (mid)", fontsize=8.8)
    ax.text(0.97, 0.23, r"Mid curves: $M_{\rm AH}(t)$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.1, color="0.25")
    ax.legend(handles=h_tr, loc="upper right", fontsize=6.9, frameon=False, labelspacing=0.20)

    # ------------------------------------------------------------------
    # Bottom-Left: Cross-Suite Error / Conservation Drift Comparison
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    cats = [
        ("Kerr 0.999\n" r"($\Delta E$)",        float(D["acc_kerr999_dE_orig"]),  float(D["acc_kerr999_dE_best"])),
        ("Light Ring\n" r"($\Delta N_{\rm t}$)", float(D["acc_lr_dN_orig"]),     float(D["acc_lr_dN_best"])),
        ("6-Lvl Kerr\n" r"($\Delta E_{\rm med}$)", float(D["acc_m4_med_dE_orig"]), float(D["acc_m4_med_dE_best"])),
        ("OS Stage\n" r"($\Delta\alpha_c$)",    float(D["acc_os_alphac_orig"]),  float(D["acc_os_alphac_best"])),
        ("ST 9-Lvl\n" r"($|\mathbf{P}|/M_0$)",  float(D["acc_st_mom_orig"]),     float(D["acc_st_mom_best"])),
        ("BH Filter\n" r"($\Delta I_E$)",       float(D["orig_filt_max"]),       max(float(D["best_filt_max"]), 1e-16)),
    ]
    x = np.arange(len(cats), dtype=np.float64)
    w = 0.34
    v_orig = np.array([c[1] for c in cats])
    v_best = np.array([c[2] for c in cats])
    ax.bar(x - 0.5 * w, v_orig, width=w, color=cz.PAL["blue"], edgecolor="k", lw=0.6,
           label="NRPIC Original", bottom=1e-17, log=True)
    ax.bar(x + 0.5 * w, v_best, width=w, color=cz.PAL["red"], edgecolor="k", lw=0.6,
           label="Our Best GR-LBV", bottom=1e-17, log=True)
    y_mults = [3.0, 2.5, 3.0, 3.0, 2.8, 12.0]
    for xi, vo, vb, ym in zip(x, v_orig, v_best, y_mults):
        top = max(vo, vb)
        gain = vo / max(vb, 1e-30)
        ax.text(xi, top * ym, fmt_gain(gain), ha="center", va="bottom",
                fontsize=6.1, fontweight="bold", color=cz.PAL["red"])
    ax.set_xticks(x)
    ax.set_xticklabels([c[0] for c in cats], fontsize=6.1)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.55, 5.65)
    ax.set_ylim(1.0e-17, 6.0e3)
    cz.no_minor_labels(ax, "y")
    ax.set_ylabel(r"Relative error or drift")
    ax.legend(loc="upper center", ncol=2, columnspacing=0.8, fontsize=7.0, frameon=False)

    # ------------------------------------------------------------------
    # Bottom-Right: B200 GPU Wall-Time Speedup Scorecard
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    spds = [
        (r"BH $q=0.05$",      float(D["orig_wall"]),      float(D["fast_wall"])),
        (r"OS $10^4$ (7-Lvl)", float(D["spd_os10k_orig"]), float(D["spd_os10k_best"])),
        (r"OS $10^5$ (7-Lvl)", float(D["spd_os100k_orig"]),float(D["spd_os100k_best"])),
        (r"ST $10^4$ (9-Lvl)", float(D["spd_st10k_orig"]), float(D["spd_st10k_best"])),
        (r"M4 Kerr (6-Lvl)",   float(D["spd_m4_orig"]),    float(D["spd_m4_best"])),
    ]
    y = np.arange(len(spds), dtype=np.float64)[::-1]
    ratios = [t0 / t1 for _, t0, t1 in spds]
    cols_br = [cz.PAL["green"], cz.PAL["orange"], cz.PAL["blue"], "#8E24AA", cz.PAL["red"]]
    ax.barh(y, ratios, height=0.55, color=cols_br, edgecolor="k", lw=0.65)
    ax.axvline(1.0, **cz.GUIDE)
    for yi, (_, t0, t1), sp in zip(y, spds, ratios):
        ax.text(sp + 0.08, yi, rf"{sp:.2f}$\times$ ({t0:.0f}s $\to$ {t1:.0f}s)",
                va="center", ha="left", fontsize=6.9, color="0.12")
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in spds], fontsize=7.2)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(0.0, 5.25)
    ax.set_ylim(-0.55, len(spds) + 0.08)
    ax.set_xlabel(r"B200 GPU speedup ($T_{\rm orig} / T_{\rm best}$)", labelpad=1)
    ax.text(1.06, len(spds) - 0.30, r"Baseline $1\times$", fontsize=6.8, color="0.35", ha="left", va="center")

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
