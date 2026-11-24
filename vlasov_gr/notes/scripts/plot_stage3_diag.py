#!/usr/bin/env python3
"""Stage 3 verification & diagnostic figure: AthenaK B200 GPU vs OpenMP CPU vs Python 3D MFM parity,
plus existing NRPIC Kerr geodesic regression check."""

import glob
import math
import os
import re
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import vlasov_gr as vg  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
RUN_DIR = os.path.join(SCRATCH, "runs", "stage3_parity")
GPU_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
OMP_BIN = os.path.join(SCRATCH, "build_omp", "src", "athena")
FIG_OUT = os.path.join(REPO, "vlasov_gr", "notes", "figs", "diag_stage3_athenak_parity.png")


def build_parity_ic(ic_path: str):
    """Create 5^3 periodic oblique two-stream + warm density wave on [0, 1)^3."""
    n_lat = 5
    L = 1.0
    dx = L / n_lat
    c1 = (np.arange(n_lat) + 0.5) * dx
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    x = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N = len(x)
    Nb = 2
    kx = 2.0 * math.pi * x[:, 0]
    ky = 2.0 * math.pi * x[:, 1]
    kz = 2.0 * math.pi * x[:, 2]

    D0 = np.zeros((N, Nb), dtype=np.float64)
    D0[:, 0] = 0.60 * (1.0 + 0.18 * np.sin(kx) * np.cos(ky))
    D0[:, 1] = 0.40 * (1.0 + 0.12 * np.cos(ky) * np.sin(kz))

    u0 = np.zeros((N, Nb, 3), dtype=np.float64)
    u0[:, 0, 0] = 0.55 + 0.05 * np.cos(kz)
    u0[:, 0, 1] = 0.25 - 0.04 * np.sin(kx)
    u0[:, 0, 2] = 0.15
    u0[:, 1, 0] = -0.45 + 0.04 * np.sin(ky)
    u0[:, 1, 1] = -0.20
    u0[:, 1, 2] = -0.10 + 0.03 * np.cos(kx)

    S0 = np.zeros((N, Nb, 3, 3), dtype=np.float64)
    S0[:, 0] = np.diag([0.12**2, 0.10**2, 0.09**2])
    S0[:, 1] = np.diag([0.10**2, 0.13**2, 0.11**2])

    st = vg.init_mfm_3d(x, D0, u0, S0, box=[L, L, L])
    vg.write_grlbv(ic_path, st.x, st.m, st.u_bar, st.Sigma, time=0.0)
    return st


def write_parity_athinput(cfg_path: str, basename: str, ic_path: str, dt: float = 0.02, nsteps: int = 5):
    tlim = dt * nsteps
    text = f"""# Stage 3 parity input (auto-generated)
<comment>
problem = GR-LBV Stage 3 3D periodic parity test

<job>
basename = {basename}

<mesh>
nghost   = 2
nx1      = 8
x1min    = 0.0
x1max    = 1.0
ix1_bc   = periodic
ox1_bc   = periodic
nx2      = 8
x2min    = 0.0
x2max    = 1.0
ix2_bc   = periodic
ox2_bc   = periodic
nx3      = 8
x3min    = 0.0
x3max    = 1.0
ix3_bc   = periodic
ox3_bc   = periodic

<meshblock>
nx1      = 8
nx2      = 8
nx3      = 8

<time>
evolution  = dynamic
integrator = rk2
cfl_number = 1.0
nlim       = {nsteps}
tlim       = {tlim:.10f}
ndiag      = 10

<adm>
dynamic = false

<particles>
particle_type      = nrpic
pusher             = vlasov_mfm
metric             = mesh
deposit            = false
particle_file      = {ic_path}
vlasov_basis       = tophat
vlasov_nperp       = 3
vlasov_nq_kick     = 3
vlasov_nq_dep      = 3
vlasov_pair_mode   = covariant
vlasov_analytic_vf = false
vlasov_substeps    = 1
vlasov_bnd_detect  = false
tolerance          = 1.0e-12
dt                 = {dt:.10f}
hist_dcycle        = 1
snap_dt            = {dt:.10f}

<problem>
pgen_name   = nrpic_geodesic
metric_kind = homogeneous
alpha0      = 1.0
gxx         = 1.0
gxy         = 0.0
gxz         = 0.0
gyy         = 1.0
gyz         = 0.0
gzz         = 1.0
"""
    with open(cfg_path, "w") as f:
        f.write(text)


def load_vlasov_hst(path: str):
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data[None, :]
    return data


def main():
    os.makedirs(RUN_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)

    dt = 0.02
    nsteps = 5
    ic_path = os.path.join(RUN_DIR, "ic.grlbv")
    st_py = build_parity_ic(ic_path)

    # Track Python invariants at every step
    py_times, py_M, py_P, py_E = [], [], [], []
    m0, p0, e0 = vg.total_invariants_3d(st_py)
    py_times.append(0.0); py_M.append(m0); py_P.append(p0); py_E.append(e0)
    for k in range(nsteps):
        vg.step_3d_mfm(st_py, dt)
        mk, pk, ek = vg.total_invariants_3d(st_py)
        py_times.append((k + 1) * dt); py_M.append(mk); py_P.append(pk); py_E.append(ek)

    gpu_dir = os.path.join(RUN_DIR, "gpu")
    omp_dir = os.path.join(RUN_DIR, "omp")
    omp4b_dir = os.path.join(RUN_DIR, "omp4b")
    geo_dir = os.path.join(RUN_DIR, "geo_reg")
    for d in (gpu_dir, omp_dir, omp4b_dir, geo_dir):
        os.makedirs(d, exist_ok=True)
        for old in glob.glob(os.path.join(d, "*")):
            os.remove(old)

    gpu_cfg = os.path.join(gpu_dir, "parity.athinput")
    omp_cfg = os.path.join(omp_dir, "parity.athinput")
    omp4b_cfg = os.path.join(omp4b_dir, "parity.athinput")
    write_parity_athinput(gpu_cfg, "parity_gpu", ic_path, dt=dt, nsteps=nsteps)
    write_parity_athinput(omp_cfg, "parity_omp", ic_path, dt=dt, nsteps=nsteps)
    write_parity_athinput(omp4b_cfg, "parity_omp4b", ic_path, dt=dt, nsteps=nsteps)

    print("Running AthenaK GPU parity test...", flush=True)
    r_gpu = subprocess.run([GPU_BIN, "-i", gpu_cfg, "-d", gpu_dir], capture_output=True, text=True)
    if r_gpu.returncode != 0:
        print(r_gpu.stdout)
        print(r_gpu.stderr, file=sys.stderr)
        sys.exit(r_gpu.returncode)

    print("Running AthenaK OpenMP CPU parity test (4a & 4b)...", flush=True)
    env_omp = os.environ.copy()
    env_omp["OMP_NUM_THREADS"] = "4"
    env_omp["OMP_PROC_BIND"] = "spread"
    r_omp = subprocess.run([OMP_BIN, "-i", omp_cfg, "-d", omp_dir], capture_output=True, text=True, env=env_omp)
    if r_omp.returncode != 0:
        print(r_omp.stdout)
        print(r_omp.stderr, file=sys.stderr)
        sys.exit(r_omp.returncode)
    r_omp4b = subprocess.run([OMP_BIN, "-i", omp4b_cfg, "-d", omp4b_dir], capture_output=True, text=True, env=env_omp)
    if r_omp4b.returncode != 0:
        print(r_omp4b.stdout)
        print(r_omp4b.stderr, file=sys.stderr)
        sys.exit(r_omp4b.returncode)

    print("Running NRPIC Kerr geodesic regression on GPU...", flush=True)
    geo_inp = os.path.join(REPO, "problems", "kerr", "geodesic.athinput")
    r_geo = subprocess.run(
        [GPU_BIN, "-i", geo_inp, "-d", geo_dir, "time/tlim=20.0", "job/basename=geo_reg"],
        capture_output=True, text=True
    )
    if r_geo.returncode != 0:
        print(r_geo.stdout)
        print(r_geo.stderr, file=sys.stderr)
        sys.exit(r_geo.returncode)
    m_geo = re.findall(r"cycle=(\d+)\s+time=", r_geo.stdout)
    geo_cycles = int(m_geo[-1]) if m_geo else -1

    hst_geo_path = os.path.join(geo_dir, "geo_reg.nrpic.hst")
    geo_hst_ncycle = -1
    geo_push_unconv = None
    if os.path.exists(hst_geo_path):
        cols = []
        last_line = None
        with open(hst_geo_path) as f:
            for line in f:
                if line.startswith("#"):
                    cols.extend(re.findall(r"\[\d+\]=(\S+)", line))
                elif line.strip():
                    last_line = line.strip()
        if last_line is not None and cols:
            vals = [float(x) for x in last_line.split()]
            rec = dict(zip(cols, vals))
            geo_hst_ncycle = int(round(rec.get("ncycle", rec.get("cycle", -1))))
            if "push_unconverged" in rec:
                geo_push_unconv = int(round(rec["push_unconverged"]))

    gpu_snaps = sorted(glob.glob(os.path.join(gpu_dir, "parity_gpu.vlasov.*.bin")))
    omp_snaps = sorted(glob.glob(os.path.join(omp_dir, "parity_omp.vlasov.*.bin")))
    omp4b_snaps = sorted(glob.glob(os.path.join(omp4b_dir, "parity_omp4b.vlasov.*.bin")))
    assert gpu_snaps and omp_snaps and omp4b_snaps, "Missing AthenaK .vlasov.*.bin snapshots"
    sn_gpu = vg.read_grlbv(gpu_snaps[-1])
    sn_omp = vg.read_grlbv(omp_snaps[-1])
    sn_omp4b = vg.read_grlbv(omp4b_snaps[-1])

    def min_per_diff(a, b):
        d = a - b
        return d - np.round(d)

    err_gpu_py = {
        "x": np.abs(min_per_diff(sn_gpu["x"], st_py.x)),
        "m": np.abs(sn_gpu["m"] - st_py.m),
        "u": np.abs(sn_gpu["u_bar"] - st_py.u_bar),
        "S": np.abs(sn_gpu["Sigma"] - st_py.Sigma),
    }
    err_cpu_gpu = {
        "x": np.abs(min_per_diff(sn_omp["x"], sn_gpu["x"])),
        "m": np.abs(sn_omp["m"] - sn_gpu["m"]),
        "u": np.abs(sn_omp["u_bar"] - sn_gpu["u_bar"]),
        "S": np.abs(sn_omp["Sigma"] - sn_gpu["Sigma"]),
    }
    err_omp_det = {
        "x": np.abs(min_per_diff(sn_omp["x"], sn_omp4b["x"])),
        "m": np.abs(sn_omp["m"] - sn_omp4b["m"]),
        "u": np.abs(sn_omp["u_bar"] - sn_omp4b["u_bar"]),
        "S": np.abs(sn_omp["Sigma"] - sn_omp4b["Sigma"]),
    }

    max_gpu_py = {k: float(np.max(v)) for k, v in err_gpu_py.items()}
    max_cpu_gpu = {k: float(np.max(v)) for k, v in err_cpu_gpu.items()}
    max_omp_det = {k: float(np.max(v)) for k, v in err_omp_det.items()}
    hst_gpu = load_vlasov_hst(os.path.join(gpu_dir, "parity_gpu.vlasov.hst"))
    hst_omp = load_vlasov_hst(os.path.join(omp_dir, "parity_omp.vlasov.hst"))

    t_gpu = hst_gpu[:, 0]
    dm_gpu = np.abs(hst_gpu[:, 3] - hst_gpu[0, 3]) / abs(hst_gpu[0, 3])
    dp_gpu = np.linalg.norm(hst_gpu[:, 5:8] - hst_gpu[0, 5:8], axis=1)
    de_gpu = np.abs(hst_gpu[:, 4] - hst_gpu[0, 4]) / abs(hst_gpu[0, 4])
    de_py = np.abs(np.array(py_E) - py_E[0]) / abs(py_E[0])

    print(f"Snap time GPU={sn_gpu['time']:.6f}, OMP={sn_omp['time']:.6f}")
    print(f"Max GPU vs Python errors : {max_gpu_py}")
    print(f"Max CPU vs GPU errors    : {max_cpu_gpu}")
    print(f"Max OMP 4a vs 4b diffs   : {max_omp_det}")
    print(
        f"Geodesic regression cycle: {geo_cycles} (hst ncycle={geo_hst_ncycle}, push_unconverged={geo_push_unconv}), "
        f"rel dM_gpu={dm_gpu[-1]:.3e}, dE_gpu={de_gpu[-1]:.3e}, dP_gpu={dp_gpu[-1]:.3e}"
    )

    assert abs(sn_gpu["time"] - 0.10) < 1e-12
    assert max(max_gpu_py.values()) < 1e-11, f"GPU vs Python exceeded 1e-11: {max_gpu_py}"
    assert max(max_cpu_gpu.values()) < 1e-12, f"CPU vs GPU exceeded 1e-12: {max_cpu_gpu}"
    assert max(max_omp_det.values()) < 1e-12, f"OMP4a vs OMP4b exceeded 1e-12: {max_omp_det}"
    assert geo_cycles >= 2000, f"Expected >=2000 geodesic cycles, got {geo_cycles}"
    assert geo_hst_ncycle < 0 or geo_hst_ncycle >= 2000, f"Unexpected hst ncycle={geo_hst_ncycle}"
    assert geo_push_unconv is None or geo_push_unconv == 0, f"Geodesic push_unconverged={geo_push_unconv}"

    # Plot 4-panel Stage 3 diagnostic figure
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 10.5,
        "axes.titlesize": 10.5,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
    })
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.6), constrained_layout=True)

    # Panel (a): GPU vs Python element-wise errors
    ax = axes[0, 0]
    elem_idx = np.arange(len(st_py.x))
    ax.semilogy(elem_idx, np.max(err_gpu_py["x"], axis=1) + 1e-17, "o-", ms=3, lw=1.0, label=r"$x^i$")
    ax.semilogy(elem_idx, np.max(err_gpu_py["m"], axis=1) + 1e-17, "s-", ms=3, lw=1.0, label=r"$m_\alpha$")
    ax.semilogy(elem_idx, np.max(err_gpu_py["u"], axis=(1, 2)) + 1e-17, "^-", ms=3, lw=1.0, label=r"$\bar{u}_{\alpha i}$")
    ax.semilogy(elem_idx, np.max(err_gpu_py["S"], axis=(1, 2, 3)) + 1e-17, "d-", ms=3, lw=1.0, label=r"$\Sigma_{\alpha ij}$")
    ax.axhline(1e-11, color="k", ls="--", lw=0.9, label="threshold")
    ax.set_xlabel("Element index a")
    ax.set_ylabel("Max abs error (GPU vs Python)")
    ax.set_ylim(1e-17, 1e-10)
    ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8.5)
    ax.set_title("(a) AthenaK B200 GPU vs Python 3D parity")

    # Panel (b): OpenMP CPU vs GPU parity errors + OMP determinism
    ax = axes[0, 1]
    ax.semilogy(elem_idx, np.max(err_cpu_gpu["x"], axis=1) + 1e-17, "o-", ms=3, lw=1.0, label=r"$x^i$ (CPU vs GPU)")
    ax.semilogy(elem_idx, np.max(err_cpu_gpu["m"], axis=1) + 1e-17, "s-", ms=3, lw=1.0, label=r"$m_\alpha$ (CPU vs GPU)")
    ax.semilogy(elem_idx, np.max(err_cpu_gpu["u"], axis=(1, 2)) + 1e-17, "^-", ms=3, lw=1.0, label=r"$\bar{u}_{\alpha i}$ (CPU vs GPU)")
    ax.semilogy(elem_idx, np.max(err_cpu_gpu["S"], axis=(1, 2, 3)) + 1e-17, "d-", ms=3, lw=1.0, label=r"$\Sigma_{\alpha ij}$ (CPU vs GPU)")
    omp_det_elem = np.maximum.reduce([
        np.max(err_omp_det["x"], axis=1),
        np.max(err_omp_det["m"], axis=1),
        np.max(err_omp_det["u"], axis=(1, 2)),
        np.max(err_omp_det["S"], axis=(1, 2, 3)),
    ])
    ax.semilogy(elem_idx, omp_det_elem + 1e-17, "k:", lw=1.2, label="OMP4a vs 4b (max)")
    ax.axhline(1e-12, color="k", ls="--", lw=0.9, label="threshold")
    ax.set_xlabel("Element index a")
    ax.set_ylabel("Max abs diff")
    ax.set_ylim(1e-17, 1e-10)
    ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8.0)
    ax.set_title("(b) OpenMP CPU vs GPU parity & determinism")

    # Panel (c): Conservation history
    ax = axes[1, 0]
    ax.semilogy(t_gpu, np.maximum(dm_gpu, 1e-17), "o-", ms=4, lw=1.3, label=r"$|\Delta M / M_0|$ (GPU)")
    ax.semilogy(t_gpu, np.maximum(dp_gpu, 1e-17), "s-", ms=4, lw=1.3, label=r"$|\Delta P|$ (GPU)")
    ax.semilogy(t_gpu, np.maximum(de_gpu, 1e-17), "^-", ms=4, lw=1.3, label=r"$|\Delta E / E_0|$ (GPU)")
    ax.semilogy(py_times, np.maximum(de_py, 1e-17), "k--", lw=1.1, label=r"$|\Delta E / E_0|$ (Python)")
    ax.set_xlabel("Coordinate time t")
    ax.set_ylabel("Relative conservation residual")
    ax.set_ylim(1e-17, 1e-3)
    ax.legend(frameon=False, loc="best", fontsize=8.5)
    ax.set_title("(c) Mass, momentum, and energy evolution")

    # Panel (d): Final phase-space comparison (x_1 vs u_1 for both basis streams)
    ax = axes[1, 1]
    for al, mk, col in [(0, "o", "#1f77b4"), (1, "s", "#d62728")]:
        ax.plot(st_py.x[:, 0], st_py.u_bar[:, al, 0], mk, mfc="none", mec=col, ms=5.0, lw=1.0,
                label=f"Python stream {al}")
        ax.plot(sn_gpu["x"][:, 0], sn_gpu["u_bar"][:, al, 0], ".", color=col, ms=3.2,
                label=f"GPU stream {al}")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$\bar{u}_x$")
    ax.legend(frameon=False, ncol=2, loc="center right", fontsize=8.5)
    ax.set_title(r"(d) Final phase space at $t = 0.10$")

    fig.savefig(FIG_OUT, dpi=220)
    print(f"Saved diagnostic figure: {FIG_OUT}")
    print("STAGE 3 VERIFICATION PASSED")


if __name__ == "__main__":
    main()
