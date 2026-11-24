#!/usr/bin/env python3
"""Suite 1D Optical-Depth Crossover Benchmark:
Compare Conservative Relativistic Cell-BGK (`vlasov_hybrid + vlasov_pbgk`),
AP-MFM (`vlasov_mfm`), and NRPIC Monte Carlo collisions (`midpoint + collisions`)
across sigma/mu in {0, 2, 15, 1e4} on the 3D flat periodic Taub colliding beams.

Also verifies GPU vs OpenMP (CPU) determinism of Cell-BGK using Philox RNG.
Saves reduced diagnostics to `vlasov_gr/paper/data/pbgk_crossover.npz`.
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
from scipy.optimize import brentq
from scipy.special import kve

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrpic import io as nio  # noqa: E402
from nrpic import qmc_sampling as qmc  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
OMP_BIN = os.path.join(SCRATCH, "build_omp", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "pbgk_crossover")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "pbgk_crossover.npz")


def clean_dir(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def run_athena(bin_path: str, cfg: str, rdir: str, label: str, extra_env=None, timeout_s=None):
    clean_dir(rdir)
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    t0 = pytime.perf_counter()
    res = subprocess.run([bin_path, "-i", cfg, "-d", rdir],
                         capture_output=True, text=True, env=env, timeout=timeout_s)
    wall_s = pytime.perf_counter() - t0
    with open(os.path.join(rdir, f"{label}.stdout.log"), "w") as f:
        f.write(res.stdout)
        if res.stderr:
            f.write("\n=== STDERR ===\n" + res.stderr)
    if res.returncode != 0:
        raise RuntimeError(
            f"AthenaK failed ({label}, rc={res.returncode}):\n"
            f"{res.stdout[-1500:]}\n{res.stderr[-1000:]}"
        )
    m_comp = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", res.stdout)
    comp_s = float(m_comp.group(1)) if m_comp else wall_s
    return wall_s, comp_s


def exact_warm_taub(D1: float, Jx1: float, e1: float, S1: float, P1: float):
    """Exact relativistic Rankine-Hugoniot jump for symmetric warm colliding beams."""
    def w_of_th(th: float) -> float:
        return float(kve(3, 1.0 / th) / kve(2, 1.0 / th)) - th

    th_lo = brentq(lambda th: w_of_th(th) - (e1 / D1), 0.01, 1.0)
    th_hi = brentq(lambda th: w_of_th(th) - (S1 / Jx1), 0.01, 1.0)
    if th_lo > th_hi:
        th_lo, th_hi = th_hi, th_lo

    def resid(th: float) -> float:
        w = w_of_th(th)
        Vs = (S1 - Jx1 * w) / (D1 * w - e1)
        D2 = D1 + Jx1 / Vs
        return (P1 + S1 * Vs) - (D2 * th)

    th_w = brentq(resid, th_lo + 1.0e-9, th_hi - 1.0e-9)
    w_w = w_of_th(th_w)
    Vs_w = (S1 - Jx1 * w_w) / (D1 * w_w - e1)
    D2_w = D1 + Jx1 / Vs_w
    e2_w = e1 + S1 / Vs_w
    return dict(D2=float(D2_w), e2=float(e2_w), theta2=float(th_w), shock_speed=float(Vs_w))


def build_taub_ics(base_dir: str):
    """Build aliasing-free colliding-beam .grlbv ICs and matched S2 icosahedral .nrp packets."""
    # 128x4x4 for AP-MFM (~2.5s GPU) and 256x4x4 for P-BGK / NRPIC (49,152 equal-mass packets)
    Ly = 4.0 / 256.0
    Lz = 4.0 / 256.0
    Lx = 1.0

    def _make_grlbv(nx, ny, nz, path):
        V_el = (Lx * Ly * Lz) / (nx * ny * nz)
        cx = (np.arange(nx) + 0.5) / nx
        cy = (np.arange(ny) + 0.5) * (Ly / ny)
        cz = (np.arange(nz) + 0.5) * (Lz / nz)
        gx, gy, gz = np.meshgrid(cx, cy, cz, indexing="ij")
        x = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
        N = len(x)
        D = np.zeros((N, 2), dtype=np.float64)
        u = np.zeros((N, 2, 3), dtype=np.float64)
        S = np.broadcast_to((0.03**2) * np.eye(3), (N, 2, 3, 3)).copy()
        left = x[:, 0] < 0.5
        D[left, 0] = 1.0
        D[~left, 1] = 1.0
        u[:, 0, 0] = +0.60
        u[:, 1, 0] = -0.60
        vg.write_grlbv(path, x, D * V_el, u, S, time=0.0)
        return x, left, V_el

    mfm_grlbv = os.path.join(base_dir, "ic_1d_taub_mfm.grlbv")
    _make_grlbv(128, 4, 4, mfm_grlbv)

    pbgk_grlbv = os.path.join(base_dir, "ic_1d_taub_256.grlbv")
    x1d, left, V1d = _make_grlbv(256, 4, 4, pbgk_grlbv)

    # Exact bit-compatible expansion matching InitializeScpOnMesh (S2 icosahedron q=12)
    dirs12, _ = qmc.lebedev_unit_vectors(12)
    xi12 = math.sqrt(3.0) * dirs12
    px, pu, pm = [], [], []
    N = len(x1d)
    for a in range(N):
        al = 0 if left[a] else 1
        R = qmc.halton_so3(a * 2 + al)
        LR = 0.03 * R
        u_pts = np.array([+0.60 if left[a] else -0.60, 0.0, 0.0])[None, :] + xi12 @ LR.T
        px.append(np.broadcast_to(x1d[a], (12, 3)))
        pu.append(u_pts)
        pm.append(np.full(12, V1d / 12.0))
    px = np.concatenate(px, axis=0)
    pu = np.concatenate(pu, axis=0)
    pm = np.concatenate(pm, axis=0)
    nrp_path = os.path.join(base_dir, "ic_1d_taub_pbgk12.nrp")
    nio.write_nrp(nrp_path, px, pu, pm, np.zeros(len(pm), dtype=np.int32))
    return pbgk_grlbv, mfm_grlbv, nrp_path, (Lx, Ly, Lz)


def write_cfg(cfg_path: str, basename: str, method: str, ic_path: str,
              Lbox, sig: float, dt: float = 0.002, tlim: float = 0.65,
              nlim: int = -1, snap_dt: float = 0.65):
    Lx, Ly, Lz = Lbox
    if method == "mfm":
        nx1, nx2, nx3 = 16, 4, 4
        pblock = f"""particle_type      = nrpic
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
vlasov_substeps    = 0
vlasov_cfl         = 0.3
vlasov_max_substeps = 128
vlasov_coll_sigma  = {sig:.12g}
vlasov_bnd_detect  = false"""
    elif method == "pbgk":
        nx1, nx2, nx3 = 256, 4, 4
        pblock = f"""particle_type         = nrpic
pusher                = vlasov_hybrid
vlasov_mode           = hybrid
vlasov_pusher         = gl4
vlasov_scp_s2_shell   = true
vlasov_scp_s2_q       = 12
vlasov_scp_rotate     = true
vlasov_pbgk           = true
vlasov_pbgk_cell_factor = 2
vlasov_coll_sigma     = {sig:.12g}
metric                = mesh
deposit               = false
particle_file         = {ic_path}"""
    elif method == "nrpic":
        nx1, nx2, nx3 = 256, 4, 4
        coll_on = "true" if sig > 0.0 else "false"
        pblock = f"""particle_type    = nrpic
pusher           = midpoint
metric           = mesh
deposit          = false
particle_file    = {ic_path}
collisions       = {coll_on}
coll_sigma       = {sig:.12g}
coll_sigma_model = constant
coll_pmax        = 0.1
coll_subcycle    = measured
coll_nsub_max    = 1000
coll_cell_factor = 2
coll_weights     = equal
coll_hist_dcycle = 2"""
    else:
        raise ValueError(method)

    txt = f"""<comment>
problem = {basename}

<job>
basename = {basename}
rng_seed = 42

<mesh>
nghost   = 2
nx1      = {nx1}
x1min    = 0.0
x1max    = {Lx:.16g}
ix1_bc   = periodic
ox1_bc   = periodic
nx2      = {nx2}
x2min    = 0.0
x2max    = {Ly:.16g}
ix2_bc   = periodic
ox2_bc   = periodic
nx3      = {nx3}
x3min    = 0.0
x3max    = {Lz:.16g}
ix3_bc   = periodic
ox3_bc   = periodic

<meshblock>
nx1 = {nx1}
nx2 = {nx2}
nx3 = {nx3}

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
{pblock}
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


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)

    pbgk_grlbv, mfm_grlbv, nrp_path, Lbox = build_taub_ics(RUN_BASE)
    _, Ly, Lz = Lbox
    taub = vg.exact_taub_double_shock(u0=0.60, rho0=1.0)
    # Compute exact warm Rankine-Hugoniot jump from initial S2 packet beam moments
    xp0, up0, mp0, _ = nio.read_nrp(nrp_path)
    Wp0 = np.sqrt(1.0 + np.sum(up0 * up0, axis=1))
    left0 = xp0[:, 0] < 0.5
    v_half = 0.5 * Ly * Lz
    D1 = float(np.sum(mp0[left0]) / v_half)
    Jx1 = float(np.sum(mp0[left0] * up0[left0, 0] / Wp0[left0]) / v_half)
    e1 = float(np.sum(mp0[left0] * Wp0[left0]) / v_half)
    S1 = float(np.sum(mp0[left0] * up0[left0, 0]) / v_half)
    P1 = float(np.sum(mp0[left0] * (up0[left0, 0] ** 2) / Wp0[left0]) / v_half)
    taub_w = exact_warm_taub(D1, Jx1, e1, S1, P1)
    print(f"Exact COLD Taub (u0=0.60): D2={taub['D2']:.6f}, e2={taub['e2']:.6f}, "
          f"theta2={taub['theta2']:.6f}, Vs={taub['shock_speed']:.6f}", flush=True)
    print(f"Exact WARM Taub (sig_v=0.03): D2={taub_w['D2']:.6f}, e2={taub_w['e2']:.6f}, "
          f"theta2={taub_w['theta2']:.6f}, Vs={taub_w['shock_speed']:.6f}", flush=True)

    tlim_run = 0.65
    xb_edges = np.linspace(0.0, 1.0, 65)  # commensurate dx=1/64 with nx1=128 and 256
    xb_cent = 0.5 * (xb_edges[:-1] + xb_edges[1:])
    vol_b = (xb_edges[1] - xb_edges[0]) * Ly * Lz
    plateau_mask = (np.abs(xb_cent - 0.5) >= 0.025) & (
        np.abs(xb_cent - 0.5) <= 0.70 * taub_w["shock_speed"] * tlim_run
    )

    sigmas = [0.0, 2.0, 15.0, 1.0e4]
    out = dict(
        sigmas=np.array(sigmas, dtype=np.float64),
        xb_cent=xb_cent,
        taub_D2=float(taub["D2"]),
        taub_e2=float(taub["e2"]),
        taub_Vs=float(taub["shock_speed"]),
        warm_taub_D2=float(taub_w["D2"]),
        warm_taub_e2=float(taub_w["e2"]),
        warm_taub_theta2=float(taub_w["theta2"]),
        warm_taub_Vs=float(taub_w["shock_speed"]),
    )

    for method in ("pbgk", "mfm", "nrpic"):
        ic_use = pbgk_grlbv if method == "pbgk" else (mfm_grlbv if method == "mfm" else nrp_path)
        walls, comps, dms, des, d_errs, e_errs, d_w_errs, e_w_errs = [], [], [], [], [], [], [], []
        print(f"\n=== Method: {method} ===", flush=True)
        for sig in sigmas:
            stag = "1e4" if sig >= 1e3 else str(int(round(sig)))
            lbl = f"{method}_sig{stag}"
            cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
            rdir = os.path.join(RUN_BASE, lbl)
            write_cfg(cfg, lbl, method, ic_use, Lbox, sig, tlim=tlim_run, snap_dt=tlim_run)
            timed_out = False
            try:
                wall_s, comp_s = run_athena(GPU_BIN, cfg, rdir, lbl, timeout_s=180.0)
            except subprocess.TimeoutExpired:
                timed_out = True
                cfg_s = os.path.join(RUN_BASE, f"{lbl}_short20.athinput")
                rdir_s = os.path.join(RUN_BASE, f"{lbl}_short20")
                write_cfg(cfg_s, lbl, method, ic_use, Lbox, sig, tlim=tlim_run, nlim=20, snap_dt=tlim_run)
                w20, c20 = run_athena(GPU_BIN, cfg_s, rdir_s, f"{lbl}_short20", timeout_s=180.0)
                nsteps_full = int(round(tlim_run / 0.002))
                wall_s = w20 * (nsteps_full / 20.0)
                comp_s = c20 * (nsteps_full / 20.0)
                out[f"{lbl}_timed_out"] = True
                out[f"{lbl}_short20_wall_s"] = w20
                out[f"{lbl}_short20_comp_s"] = c20
                print(
                    f"  sig={sig:7g}: TIMED OUT >180s; nlim=20 measured wall={w20:.3f}s comp={c20:.3f}s "
                    f"-> projected full ({nsteps_full} steps) wall={wall_s:.1f}s comp={comp_s:.1f}s",
                    flush=True,
                )

            if timed_out:
                walls.append(wall_s)
                comps.append(comp_s)
                dms.append(np.nan)
                des.append(np.nan)
                d_errs.append(np.nan)
                e_errs.append(np.nan)
                d_w_errs.append(np.nan)
                e_w_errs.append(np.nan)
                out[f"{lbl}_D_bin"] = np.full(len(xb_cent), np.nan)
                out[f"{lbl}_e_bin"] = np.full(len(xb_cent), np.nan)
                continue

            if method in ("pbgk", "mfm"):
                hst = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
                dm = float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0])))
                de = float(np.max(np.abs(hst["E_tot"] - hst["E_tot"][0]) / abs(hst["E_tot"][0])))
                sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
                xp = sn["x"][:, 0]
                if method == "pbgk":
                    mp = sn["m"][:, 0]
                    up = sn["u_bar"][:, 0, :]
                    Wp = np.sqrt(1.0 + np.sum(up * up, axis=1))
                    ep = mp * Wp
                else:
                    mp = np.sum(sn["m"], axis=1)
                    ep = np.zeros(len(mp))
                    gi_eye = np.eye(3)
                    for a in range(len(mp)):
                        for al in range(sn["m"].shape[1]):
                            ma = sn["m"][a, al]
                            if ma > 0.0:
                                ea, _, _ = vg.basis_stress_energy(
                                    ma, sn["u_bar"][a, al], sn["Sigma"][a, al], gi_eye, n_q=3
                                )
                                ep[a] += ea
            else:
                hst = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
                dm = float(np.max(np.abs(hst["sum_m"] - hst["sum_m"][0]) / abs(hst["sum_m"][0])))
                snaps = sorted(glob.glob(os.path.join(rdir, f"{lbl}.part.*.bin")))
                _, d, _, _ = s4a.read_nrp_snapshot(snaps[-1])
                if abs(hst["sum_mW"][0]) > 0.0:
                    de = float(np.max(np.abs(hst["sum_mW"] - hst["sum_mW"][0]) / abs(hst["sum_mW"][0])))
                else:
                    _, d0, _, _ = s4a.read_nrp_snapshot(snaps[0])
                    E0 = float(np.sum(d0[:, 6] * np.sqrt(1.0 + np.sum(d0[:, 3:6] ** 2, axis=1))))
                    E1 = float(np.sum(d[:, 6] * np.sqrt(1.0 + np.sum(d[:, 3:6] ** 2, axis=1))))
                    de = abs(E1 - E0) / abs(E0)
                xp = d[:, 0]
                up = d[:, 3:6]
                mp = d[:, 6]
                ep = mp * np.sqrt(1.0 + np.sum(up * up, axis=1))

            D_bin = np.histogram(xp, bins=xb_edges, weights=mp)[0] / vol_b
            e_bin = np.histogram(xp, bins=xb_edges, weights=ep)[0] / vol_b
            D_c = float(np.mean(D_bin[plateau_mask]))
            e_c = float(np.mean(e_bin[plateau_mask]))
            err_D = abs(D_c - taub["D2"]) / taub["D2"]
            err_e = abs(e_c - taub["e2"]) / taub["e2"]
            err_D_w = abs(D_c - taub_w["D2"]) / taub_w["D2"]
            err_e_w = abs(e_c - taub_w["e2"]) / taub_w["e2"]

            walls.append(wall_s)
            comps.append(comp_s)
            dms.append(dm)
            des.append(de)
            d_errs.append(err_D)
            e_errs.append(err_e)
            d_w_errs.append(err_D_w)
            e_w_errs.append(err_e_w)
            out[f"{lbl}_D_bin"] = D_bin
            out[f"{lbl}_e_bin"] = e_bin
            print(
                f"  sig={sig:7g}: wall={wall_s:6.3f}s comp={comp_s:6.3f}s "
                f"dM/M={dm:.2e} dE/E={de:.2e} D2={D_c:.4f} (errW={err_D_w:.2%}, errC={err_D:.2%}) "
                f"e2={e_c:.4f} (errW={err_e_w:.2%}, errC={err_e:.2%})",
                flush=True,
            )
            if method == "pbgk":
                assert dm < 1e-14, f"P-BGK mass conservation failed: {dm}"
                assert de < 1e-13, f"P-BGK energy conservation failed: {de}"
                if sig >= 1.0e3:
                    assert err_D_w < 0.02, f"P-BGK warm Taub D2 jump error {err_D_w:.2%} >= 2%"
                    assert err_e_w < 0.02, f"P-BGK warm Taub e2 jump error {err_e_w:.2%} >= 2%"

        out[f"{method}_wall_s"] = np.array(walls)
        out[f"{method}_comp_s"] = np.array(comps)
        out[f"{method}_dm"] = np.array(dms)
        out[f"{method}_de"] = np.array(des)
        out[f"{method}_err_D"] = np.array(d_errs)
        out[f"{method}_err_e"] = np.array(e_errs)
        out[f"{method}_err_D_warm"] = np.array(d_w_errs)
        out[f"{method}_err_e_warm"] = np.array(e_w_errs)

    # GPU vs OpenMP determinism check for P-BGK (5 steps at sig=15)
    print("\n=== GPU vs OpenMP P-BGK Determinism Check ===", flush=True)
    det_cfg_g = os.path.join(RUN_BASE, "pbgk_det_gpu.athinput")
    det_cfg_o = os.path.join(RUN_BASE, "pbgk_det_omp.athinput")
    write_cfg(det_cfg_g, "pbgk_det_gpu", "pbgk", pbgk_grlbv, Lbox, 15.0, nlim=5, snap_dt=0.01)
    write_cfg(det_cfg_o, "pbgk_det_omp", "pbgk", pbgk_grlbv, Lbox, 15.0, nlim=5, snap_dt=0.01)
    run_athena(GPU_BIN, det_cfg_g, os.path.join(RUN_BASE, "det_gpu"), "det_gpu")
    run_athena(
        OMP_BIN, det_cfg_o, os.path.join(RUN_BASE, "det_omp"), "det_omp",
        extra_env={"OMP_NUM_THREADS": "4", "OMP_PROC_BIND": "spread"},
    )
    sg = vg.read_grlbv(sorted(glob.glob(os.path.join(RUN_BASE, "det_gpu", "pbgk_det_gpu.vlasov.*.bin")))[-1])
    so = vg.read_grlbv(sorted(glob.glob(os.path.join(RUN_BASE, "det_omp", "pbgk_det_omp.vlasov.*.bin")))[-1])
    dx_diff = float(np.max(np.abs(sg["x"] - so["x"])))
    du_diff = float(np.max(np.abs(sg["u_bar"] - so["u_bar"])))
    print(f"  [DET] GPU vs OMP(4t): max|dx|={dx_diff:.3e}, max|du|={du_diff:.3e}", flush=True)
    assert dx_diff < 1e-12 and du_diff < 1e-12
    out["det_dx_diff"] = dx_diff
    out["det_du_diff"] = du_diff

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved {OUT_NPZ}")


if __name__ == "__main__":
    main()
