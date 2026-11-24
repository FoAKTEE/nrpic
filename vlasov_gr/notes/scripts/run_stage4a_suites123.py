#!/usr/bin/env python3
"""Stage 4a GPU Benchmark Campaign (Suites 1, 2, 3) on gb204 B200:
  Suite 1: 3D flat periodic SR Vlasov-Boltzmann (boosted two-stream C^eb vs v_only,
           warm wave 2nd-order convergence + Brent vs analytic v_F, Nb=4 empty-slot
           injection, 3D colliding beams / Taub double shock).
  Suite 2: Kerr a=0.9M Cartesian Kerr-Schild warm sheared inclined cloud vs 10^4 NRPIC.
  Suite 3: Full-GR Oppenheimer-Snyder dust collapse (R_0=5M, Z4c + AMR + FastFlow)
           vs exact cycloid / Staley bound and matched-N NRPIC midpoint.

Outputs:
  - Configs & tiny summary manifests: vlasov_gr/problems/suite{1,2,3}/
  - Raw runs: $SCRATCH_ROOT/runs/stage4a/
  - Reduced paper datasets (.npz): vlasov_gr/paper/data/
  - Diagnostic 6-panel figure: vlasov_gr/notes/figs/diag_stage4a_suites123.png
"""

import argparse
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time as pytime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
_CZ_DIR = os.path.expanduser("~/.gemini/config/skills/cz-figure-style/resources")
if not os.path.exists(_CZ_DIR):
    _CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
sys.path.insert(0, _CZ_DIR)

import czstyle as cz  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import kerr as _kerr  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402
from nrpic import sampling as _samp  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402

SCRATCH_ROOT = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU_BIN = os.path.join(SCRATCH_ROOT, "build_gpu", "src", "athena")
RUN_BASE = os.path.join(SCRATCH_ROOT, "runs", "stage4a")
PROB_BASE = os.path.join(REPO, "vlasov_gr", "problems")
DATA_BASE = os.path.join(REPO, "vlasov_gr", "paper", "data")
FIG_OUT = os.path.join(REPO, "vlasov_gr", "notes", "figs", "diag_stage4a_suites123.png")


def clean_dir(path: str):
    os.makedirs(path, exist_ok=True)
    for fn in glob.glob(os.path.join(path, "*")):
        if os.path.isfile(fn):
            os.remove(fn)


def fast_nbar_periodic(x: np.ndarray, box, h0: float) -> np.ndarray:
    """Compute MFM nbar = 1/h^3 using cKDTree (O(N log N) even for 24^3+ elements)."""
    box_arr = np.asarray(box, dtype=np.float64)
    xw = np.mod(x, box_arr[None, :])
    N = len(xw)
    tree = cKDTree(xw, boxsize=box_arr)
    pairs = tree.query_ball_point(xw, r=3.5 * h0)
    nbar = np.zeros(N, dtype=np.float64)
    for a in range(N):
        ha = h0
        nbr = np.asarray(pairs[a], dtype=np.int64)
        dv = xw[nbr] - xw[a]
        dv -= box_arr[None, :] * np.round(dv / box_arr[None, :])
        r = np.sqrt(np.sum(dv * dv, axis=1))
        for _ in range(30):
            q = r / ha
            w = np.where(
                q < 1.0,
                1.0 - 1.5 * q * q + 0.75 * q ** 3,
                np.where(q < 2.0, 0.25 * (2.0 - q) ** 3, 0.0),
            ) / (math.pi * ha ** 3)
            nb_val = float(np.sum(w))
            h_new = (1.0 / max(nb_val, 1e-300)) ** (1.0 / 3.0)
            if abs(h_new - ha) < 1e-13 * ha:
                ha = h_new
                break
            ha = 0.2 * ha + 0.8 * h_new
        nbar[a] = 1.0 / (ha ** 3)
    return nbar


def run_athena(cfg_path: str, run_dir: str, label: str):
    t0 = pytime.perf_counter()
    res = subprocess.run([GPU_BIN, "-i", cfg_path, "-d", run_dir], capture_output=True, text=True)
    elapsed = pytime.perf_counter() - t0
    with open(os.path.join(run_dir, f"{label}.stdout.log"), "w") as f:
        f.write(res.stdout)
        if res.stderr:
            f.write("\n=== STDERR ===\n")
            f.write(res.stderr)
    if res.returncode != 0:
        print(res.stdout[-2000:])
        print(res.stderr[-2000:], file=sys.stderr)
        raise RuntimeError(f"AthenaK failed for {label} (code {res.returncode})")
    print(f"  [{label}] finished in {elapsed:.2f}s", flush=True)
    return elapsed


def read_col_hst(path: str):
    """Read AthenaK/vlasov/nrpic history file returning dict of 1D arrays (deduped in time)."""
    cols = []
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                found = re.findall(r"\[\d+\]=(\S+)", line)
                if found:
                    cols.extend(found)
                continue
            s = line.strip()
            if not s:
                continue
            parts = s.split()
            if cols and len(parts) != len(cols):
                continue
            rows.append([float(x) for x in parts])
    arr = np.array(rows, dtype=np.float64)
    if len(arr) == 0:
        return {}
    _, idx = np.unique(arr[::-1, 0], return_index=True)
    arr = arr[::-1][idx]
    if not cols:
        cols = [f"c{i}" for i in range(arr.shape[1])]
    return {c: arr[:, i] for i, c in enumerate(cols)}


def read_horizon(path: str):
    out = []
    if not os.path.exists(path):
        return np.zeros((0, 6))
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            p = line.split()
            if len(p) >= 12 and p[2].lower() != "nan":
                out.append([float(p[1]), float(p[2]), float(p[7]), float(p[8]), float(p[9]), float(p[10])])
    return np.array(out, dtype=np.float64) if out else np.zeros((0, 6))


def read_nrp_snapshot(path: str):
    with open(path, "rb") as f:
        f.read(8)
        t = np.frombuffer(f.read(8), dtype=np.float64)[0]
        n = int(np.frombuffer(f.read(8), dtype=np.int64)[0])
        f.read(8)
        d = np.frombuffer(f.read(8 * 7 * n), dtype=np.float64).reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype=np.int32)
        sp = np.frombuffer(f.read(4 * n), dtype=np.int32)
    return float(t), d, tag, sp


def write_flat_periodic_athinput(
    cfg_path: str,
    basename: str,
    ic_path: str,
    box,
    dt: float,
    tlim: float,
    snap_dt: float,
    pair_mode: str = "covariant",
    analytic_vf: bool = False,
    coll_sigma: float = 0.0,
    vlasov_cfl: float = 0.3,
    n_mesh=(8, 8, 8),
):
    Lx, Ly, Lz = box
    nx1, nx2, nx3 = n_mesh
    avf = "true" if analytic_vf else "false"
    txt = f"""# Suite 1: 3D flat periodic GR-LBV configuration
<comment>
problem = {basename}

<job>
basename = {basename}

<mesh>
nghost   = 2
nx1      = {nx1}
x1min    = 0.0
x1max    = {Lx:.15g}
ix1_bc   = periodic
ox1_bc   = periodic
nx2      = {nx2}
x2min    = 0.0
x2max    = {Ly:.15g}
ix2_bc   = periodic
ox2_bc   = periodic
nx3      = {nx3}
x3min    = 0.0
x3max    = {Lz:.15g}
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
nlim       = -1
tlim       = {tlim:.12f}
ndiag      = 200

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
vlasov_pair_mode   = {pair_mode}
vlasov_analytic_vf = {avf}
vlasov_substeps    = 0
vlasov_cfl         = {vlasov_cfl:.6g}
vlasov_max_substeps = 128
vlasov_coll_sigma  = {coll_sigma:.12g}
vlasov_bnd_detect  = false
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


# ============================================================================
# SUITE 1: 3D Flat Periodic SR Vlasov-Boltzmann
# ============================================================================

def run_suite1():
    print("\n=== SUITE 1: 3D Flat Periodic SR Vlasov-Boltzmann ===", flush=True)
    s1_run = os.path.join(RUN_BASE, "suite1")
    s1_prob = os.path.join(PROB_BASE, "suite1")
    os.makedirs(s1_run, exist_ok=True)
    os.makedirs(s1_prob, exist_ok=True)

    # ------------------------------------------------------------------
    # 1A: Boosted crossing relativistic streams (C^eb vs v_only)
    # ------------------------------------------------------------------
    print(" -- 1A: Boosted relativistic two-stream (|u| = 0.8, 1.5, 3.0) --", flush=True)
    n1a = 10
    c1 = (np.arange(n1a) + 0.5) / n1a
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    x1a = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N1a = len(x1a)
    V1a = 1.0 / N1a
    kx = 2.0 * math.pi * x1a[:, 0]
    ky = 2.0 * math.pi * x1a[:, 1]
    kz = 2.0 * math.pi * x1a[:, 2]

    boosts = [0.8, 1.5, 3.0]
    res1a = {}
    for u_b in boosts:
        # Both streams relativistically boosted along +x with transverse shear AND an
        # empty subregion in stream 1 (D_1 = 0, u_1 = 0) so naive Euclidean v_only pairing
        # merges stream 1 into stream 0 whereas covariant C^eb routes via empty-slot cost.
        D0 = np.zeros((N1a, 2), dtype=np.float64)
        D0[:, 0] = 0.80 * (1.0 + 0.15 * np.sin(kx))
        mask_p = np.sin(kx) > -0.2
        D0[mask_p, 1] = 0.45 * (1.0 + 0.25 * np.cos(ky[mask_p]))

        u0 = np.zeros((N1a, 2, 3), dtype=np.float64)
        u0[:, 0, 0] = u_b + 0.20
        u0[:, 0, 1] = 0.35 + 0.04 * np.cos(ky)
        u0[:, 0, 2] = 0.05 * np.sin(kz)
        u0[mask_p, 1, 0] = u_b - 0.20
        u0[mask_p, 1, 1] = -0.35 - 0.04 * np.sin(ky[mask_p])
        u0[mask_p, 1, 2] = -0.05 * np.cos(kz[mask_p])

        S0 = np.zeros((N1a, 2, 3, 3), dtype=np.float64)
        S0[:, 0] = np.diag([0.12**2, 0.12**2, 0.12**2])
        S0[:, 1] = np.diag([0.12**2, 0.12**2, 0.12**2])

        m0_arr = D0 * V1a
        ic_file = os.path.join(s1_run, f"ic_1a_u{u_b:.1f}.grlbv")
        vg.write_grlbv(ic_file, x1a, m0_arr, u0, S0, time=0.0)
        trS_init = float(np.sum(m0_arr * np.trace(S0, axis1=2, axis2=3)) / np.sum(m0_arr))
        du_init = float(np.sqrt(np.mean(np.sum((u0[mask_p, 0] - u0[mask_p, 1]) ** 2, axis=1))))

        for pmode in ("covariant", "v_only"):
            lbl = f"s1a_u{u_b:.1f}_{pmode}"
            rdir = os.path.join(s1_run, lbl)
            clean_dir(rdir)
            cfg = os.path.join(s1_prob, f"{lbl}.athinput")
            write_flat_periodic_athinput(
                cfg, lbl, ic_file, (1.0, 1.0, 1.0), dt=0.005, tlim=0.40, snap_dt=0.40,
                pair_mode=pmode, analytic_vf=False, coll_sigma=0.0, n_mesh=(8, 8, 8)
            )
            run_athena(cfg, rdir, lbl)
            hst = read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
            sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
            dm = float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0])))
            de = float(np.max(np.abs(hst["E_tot"] - hst["E_tot"][0]) / abs(hst["E_tot"][0])))
            dP = float(np.max(np.linalg.norm(
                np.column_stack([hst["P_x"], hst["P_y"], hst["P_z"]])
                - np.array([hst["P_x"][0], hst["P_y"][0], hst["P_z"][0]]), axis=1
            )))
            m_tot = np.maximum(sn["m"], 0.0)
            trS = np.trace(sn["Sigma"], axis1=2, axis2=3)
            mean_trS = float(np.sum(m_tot * trS) / np.sum(m_tot))
            mpop = sn["m"][:, 1] > 1e-6 * np.max(sn["m"][:, 0])
            du_fin = (
                float(np.sqrt(np.mean(np.sum((sn["u_bar"][mpop, 0] - sn["u_bar"][mpop, 1]) ** 2, axis=1))))
                if np.any(mpop) else 0.0
            )
            res1a[(u_b, pmode)] = dict(
                dm=dm, de=de, dP=dP,
                trS_init=trS_init, mean_trS=mean_trS, trS_ratio=mean_trS / trS_init,
                du_init=du_init, du_fin=du_fin, sep_ratio=du_fin / du_init,
                t=hst["time"], trS_hist=hst["m_trSigma"] / hst["m_tot"],
            )
            print(f"    u={u_b:.1f} {pmode:9s}: dM={dm:.2e}, dE={de:.2e}, dP={dP:.2e}, "
                  f"trS/trS0={mean_trS/trS_init:.3f}, sep/sep0={du_fin/du_init:.3f}", flush=True)

    # ------------------------------------------------------------------
    # 1B: Warm relativistic wave convergence (8^3..24^3) & Brent vs analytic v_F
    # ------------------------------------------------------------------
    print(" -- 1B: Warm wave spatial convergence (8^3..24^3) + Brent vs analytic_vf --", flush=True)
    nlats_1b = [8, 12, 16, 24]
    snaps_1b_brent = {}
    snaps_1b_an = {}
    dt_1b = 0.001
    tlim_1b = 0.08
    for nlat in nlats_1b:
        c1 = (np.arange(nlat) + 0.5) / nlat
        gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
        xb = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
        Nb_w = len(xb)
        D0 = (1.0 + 0.05 * np.cos(2.0 * math.pi * xb[:, 0]))[:, None]
        u0 = np.zeros((Nb_w, 1, 3), dtype=np.float64)
        u0[:, 0, 0] = 0.30
        S0 = np.broadcast_to((0.25**2) * np.eye(3), (Nb_w, 1, 3, 3)).copy()
        ic_file = os.path.join(s1_run, f"ic_1b_n{nlat}.grlbv")
        vg.write_grlbv(ic_file, xb, D0 / Nb_w, u0, S0, time=0.0)

        modes_vf = [("brent", False), ("analytic", True)] if nlat in (8, 16) else [("brent", False)]
        for vtag, avf in modes_vf:
            lbl = f"s1b_n{nlat}_{vtag}"
            rdir = os.path.join(s1_run, lbl)
            clean_dir(rdir)
            cfg = os.path.join(s1_prob, f"{lbl}.athinput")
            write_flat_periodic_athinput(
                cfg, lbl, ic_file, (1.0, 1.0, 1.0), dt=dt_1b, tlim=tlim_1b, snap_dt=tlim_1b,
                pair_mode="covariant", analytic_vf=avf, coll_sigma=0.0, n_mesh=(8, 8, 8)
            )
            run_athena(cfg, rdir, lbl)
            sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
            hst = read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
            nbar = fast_nbar_periodic(sn["x"], [1.0, 1.0, 1.0], 1.0 / nlat)
            D_rec = sn["m"][:, 0] * nbar
            rec = dict(nlat=nlat, x=sn["x"], m=sn["m"][:, 0], D=D_rec, u=sn["u_bar"][:, 0, 0],
                       dm=float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0]))))
            if vtag == "brent":
                snaps_1b_brent[nlat] = rec
            else:
                snaps_1b_an[nlat] = rec

    ref = snaps_1b_brent[24]
    x_ref = ref["x"][:, 0]
    def eval_ref_D(xq):
        K = 8
        A = [np.ones_like(x_ref)]
        for k in range(1, K + 1):
            A.append(np.cos(2.0 * math.pi * k * x_ref))
            A.append(np.sin(2.0 * math.pi * k * x_ref))
        A = np.column_stack(A)
        coef, *_ = np.linalg.lstsq(A, ref["D"], rcond=None)
        Aq = [np.ones_like(xq)]
        for k in range(1, K + 1):
            Aq.append(np.cos(2.0 * math.pi * k * xq))
            Aq.append(np.sin(2.0 * math.pi * k * xq))
        return np.column_stack(Aq) @ coef

    h_vals = []
    l1_D = []
    for nlat in (8, 12, 16):
        rec = snaps_1b_brent[nlat]
        D_ref_at_x = eval_ref_D(rec["x"][:, 0])
        err = float(np.mean(np.abs(rec["D"] - D_ref_at_x)))
        h_vals.append(1.0 / nlat)
        l1_D.append(err)
        print(f"    N={nlat}^3 (Brent): L1(D vs 24^3) = {err:.4e}, dM = {rec['dm']:.2e}", flush=True)
    p_8_12 = math.log(l1_D[0] / l1_D[1]) / math.log(h_vals[0] / h_vals[1])
    p_12_16 = math.log(l1_D[1] / l1_D[2]) / math.log(h_vals[1] / h_vals[2])
    p_fit = float(np.polyfit(np.log(h_vals), np.log(l1_D), 1)[0])
    vf_diff_16 = float(np.max(np.abs(snaps_1b_brent[16]["D"] - snaps_1b_an[16]["D"]) / snaps_1b_brent[16]["D"]))
    print(f"    Spatial conv orders: p(8->12)={p_8_12:.2f}, p(12->16)={p_12_16:.2f}, fit={p_fit:.2f}; "
          f"Brent vs analytic_vf max rel diff (16^3) = {vf_diff_16:.3e}", flush=True)

    # Also boosted comparison u_x = 1.5, sigma = 0.35 on 12^3
    nlat_bv = 12
    c1 = (np.arange(nlat_bv) + 0.5) / nlat_bv
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    xbv = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    Nb_bv = len(xbv)
    D_bv = (1.0 + 0.08 * np.cos(2.0 * math.pi * xbv[:, 0]))[:, None]
    u_bv = np.zeros((Nb_bv, 1, 3), dtype=np.float64)
    u_bv[:, 0, 0] = 1.5
    S_bv = np.broadcast_to((0.35**2) * np.eye(3), (Nb_bv, 1, 3, 3)).copy()
    ic_bv = os.path.join(s1_run, "ic_1b_boost15.grlbv")
    vg.write_grlbv(ic_bv, xbv, D_bv / Nb_bv, u_bv, S_bv, time=0.0)
    bv_res = {}
    for vtag, avf in [("brent", False), ("analytic", True)]:
        lbl = f"s1b_boost15_{vtag}"
        rdir = os.path.join(s1_run, lbl)
        clean_dir(rdir)
        cfg = os.path.join(s1_prob, f"{lbl}.athinput")
        write_flat_periodic_athinput(
            cfg, lbl, ic_bv, (1.0, 1.0, 1.0), dt=0.001, tlim=0.08, snap_dt=0.08,
            pair_mode="covariant", analytic_vf=avf, coll_sigma=0.0, n_mesh=(8, 8, 8)
        )
        run_athena(cfg, rdir, lbl)
        sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
        nbar = fast_nbar_periodic(sn["x"], [1.0, 1.0, 1.0], 1.0 / nlat_bv)
        bv_res[vtag] = sn["m"][:, 0] * nbar
    vf_boost_diff = float(np.max(np.abs(bv_res["brent"] - bv_res["analytic"]) / bv_res["brent"]))
    print(f"    Boosted u_x=1.5, sigma=0.35 Brent vs analytic max rel diff = {vf_boost_diff:.3e}", flush=True)

    # ------------------------------------------------------------------
    # 1C: Empty-slot injection (Nb = 4, 12^3 = 1728 elements)
    # ------------------------------------------------------------------
    print(" -- 1C: Empty-slot injection (Nb = 4, 12^3) --", flush=True)
    n1c = 12
    c1 = (np.arange(n1c) + 0.5) / n1c
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    x1c = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N1c = len(x1c)
    D1c = np.zeros((N1c, 4), dtype=np.float64)
    u1c = np.zeros((N1c, 4, 3), dtype=np.float64)
    S1c = np.broadcast_to((0.12**2) * np.eye(3), (N1c, 4, 3, 3)).copy()

    left = x1c[:, 0] < 0.5
    D1c[left, 0] = 0.65
    D1c[left, 1] = 0.35
    u1c[left, 0, 0] = 0.90; u1c[left, 0, 1] = 0.10
    u1c[left, 1, 0] = 0.45; u1c[left, 1, 1] = -0.10
    D1c[~left, 2] = 0.55
    D1c[~left, 3] = 0.45
    u1c[~left, 2, 0] = -0.90; u1c[~left, 2, 1] = -0.10
    u1c[~left, 3, 0] = -0.45; u1c[~left, 3, 1] = 0.10

    m1c = D1c / N1c
    ic_1c = os.path.join(s1_run, "ic_1c_nb4.grlbv")
    vg.write_grlbv(ic_1c, x1c, m1c, u1c, S1c, time=0.0)
    init_pop = int(np.sum(m1c > 1e-8))

    rdir = os.path.join(s1_run, "s1c_nb4")
    clean_dir(rdir)
    cfg = os.path.join(s1_prob, "s1c_nb4.athinput")
    write_flat_periodic_athinput(
        cfg, "s1c_nb4", ic_1c, (1.0, 1.0, 1.0), dt=0.005, tlim=0.30, snap_dt=0.05,
        pair_mode="covariant", analytic_vf=False, coll_sigma=0.0, n_mesh=(8, 8, 8)
    )
    run_athena(cfg, rdir, "s1c_nb4")
    sn1c_files = sorted(glob.glob(os.path.join(rdir, "s1c_nb4.vlasov.*.bin")))
    hst1c = read_col_hst(os.path.join(rdir, "s1c_nb4.vlasov.hst"))
    t_1c, pop_1c, min_eig_1c = [], [], []
    for f in sn1c_files:
        sn = vg.read_grlbv(f)
        t_1c.append(sn["time"])
        pop_1c.append(int(np.sum(sn["m"] > 1e-8)))
        eigs = np.linalg.eigvalsh(sn["Sigma"])
        min_eig_1c.append(float(np.min(eigs)))
        assert np.all(np.isfinite(sn["m"])) and np.all(sn["m"] >= -1e-15), "Non-finite or negative mass in 1C"
    dm_1c = float(np.max(np.abs(hst1c["m_tot"] - hst1c["m_tot"][0]) / abs(hst1c["m_tot"][0])))
    dP_1c = float(np.max(np.linalg.norm(
        np.column_stack([hst1c["P_x"], hst1c["P_y"], hst1c["P_z"]])
        - np.array([hst1c["P_x"][0], hst1c["P_y"][0], hst1c["P_z"][0]]), axis=1
    )))
    print(f"    Populated slots (out of {4*N1c}): init={init_pop} -> final={pop_1c[-1]}, "
          f"min Sig eig={min(min_eig_1c):.2e}, dM={dm_1c:.2e}, dP={dP_1c:.2e}", flush=True)

    # ------------------------------------------------------------------
    # 1D: 3D Relativistic Colliding Beams / Taub Double Shock
    # ------------------------------------------------------------------
    print(" -- 1D: 3D Colliding beams / Taub shock (96x5x5, sigma/mu = 0, 2, 15, 1e4) --", flush=True)
    nx_1d, ny_1d, nz_1d = 96, 5, 5
    Lx_1d = 1.0
    Ly_1d = ny_1d / nx_1d
    Lz_1d = nz_1d / nx_1d
    V_1d = (Lx_1d * Ly_1d * Lz_1d) / (nx_1d * ny_1d * nz_1d)
    cx = (np.arange(nx_1d) + 0.5) / nx_1d
    cy = (np.arange(ny_1d) + 0.5) * (Ly_1d / ny_1d)
    cz = (np.arange(nz_1d) + 0.5) * (Lz_1d / nz_1d)
    gx, gy, gz = np.meshgrid(cx, cy, cz, indexing="ij")
    x1d = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    N1d = len(x1d)
    u_in = 0.60
    D_1d = np.zeros((N1d, 2), dtype=np.float64)
    u_1d = np.zeros((N1d, 2, 3), dtype=np.float64)
    S_1d = np.broadcast_to((0.03**2) * np.eye(3), (N1d, 2, 3, 3)).copy()
    left = x1d[:, 0] < 0.5
    D_1d[left, 0] = 1.0
    u_1d[left, 0, 0] = +u_in
    u_1d[left, 1, 0] = -u_in
    D_1d[~left, 1] = 1.0
    u_1d[~left, 0, 0] = +u_in
    u_1d[~left, 1, 0] = -u_in

    ic_1d = os.path.join(s1_run, "ic_1d_taub.grlbv")
    vg.write_grlbv(ic_1d, x1d, D_1d * V_1d, u_1d, S_1d, time=0.0)
    taub = vg.exact_taub_double_shock(u0=u_in, rho0=1.0)
    print(f"    Exact Taub jump: D2={taub['D2']:.4f}, e2={taub['e2']:.4f}, p2={taub['p2']:.4f}, "
          f"theta2={taub['theta2']:.4f}, V_s={taub['shock_speed']:.4f}", flush=True)

    sigmas = [0.0, 2.0, 15.0, 1.0e4]
    res1d = {}
    t_fin_1d = 0.55
    for sig in sigmas:
        lbl = f"s1d_sig{sig:g}"
        rdir = os.path.join(s1_run, lbl)
        clean_dir(rdir)
        cfg = os.path.join(s1_prob, f"{lbl}.athinput")
        write_flat_periodic_athinput(
            cfg, lbl, ic_1d, (Lx_1d, Ly_1d, Lz_1d), dt=0.002, tlim=t_fin_1d, snap_dt=t_fin_1d,
            pair_mode="covariant", analytic_vf=False, coll_sigma=sig, vlasov_cfl=0.3, n_mesh=(16, 4, 4)
        )
        run_athena(cfg, rdir, lbl)
        sn = vg.read_grlbv(sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))[-1])
        hst = read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
        nbar = fast_nbar_periodic(sn["x"], [Lx_1d, Ly_1d, Lz_1d], 1.0 / nx_1d)
        D_tot = np.sum(sn["m"], axis=1) * nbar
        e_dens = np.zeros(len(D_tot))
        gi_eye = np.eye(3)
        for a in range(len(D_tot)):
            E_a = 0.0
            for al in range(2):
                ma = sn["m"][a, al]
                if ma <= 0.0:
                    continue
                ea, _, _ = vg.basis_stress_energy(ma * nbar[a], sn["u_bar"][a, al], sn["Sigma"][a, al], gi_eye, n_q=3)
                E_a += ea
            e_dens[a] = E_a
        order = np.argsort(sn["x"][:, 0])
        xs = sn["x"][order, 0]
        Ds = D_tot[order]
        es = e_dens[order]
        mask_c = np.abs(xs - 0.5) < 0.030
        D_cent = float(np.mean(Ds[mask_c]))
        e_cent = float(np.mean(es[mask_c]))
        dm = float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0])))
        de = float(np.max(np.abs(hst["E_tot"] - hst["E_tot"][0]) / abs(hst["E_tot"][0])))
        res1d[sig] = dict(xs=xs, Ds=Ds, es=es, D_cent=D_cent, e_cent=e_cent, dm=dm, de=de)
        errD = abs(D_cent - taub["D2"]) / taub["D2"]
        erre = abs(e_cent - taub["e2"]) / taub["e2"]
        print(f"    sig={sig:7g}: D_cent={D_cent:.4f} (vs Taub err={errD:.2%}), "
              f"e_cent={e_cent:.4f} (vs Taub err={erre:.2%}), dM={dm:.2e}, dE={de:.2e}", flush=True)

    # Save reduced Suite 1 dataset
    out_npz = os.path.join(DATA_BASE, "suite1_sr_flat.npz")
    np.savez(
        out_npz,
        boosts=np.array(boosts),
        s1a_dm_cov=np.array([res1a[(u, "covariant")]["dm"] for u in boosts]),
        s1a_dm_von=np.array([res1a[(u, "v_only")]["dm"] for u in boosts]),
        s1a_de_cov=np.array([res1a[(u, "covariant")]["de"] for u in boosts]),
        s1a_de_von=np.array([res1a[(u, "v_only")]["de"] for u in boosts]),
        s1a_trS_ratio_cov=np.array([res1a[(u, "covariant")]["trS_ratio"] for u in boosts]),
        s1a_trS_ratio_von=np.array([res1a[(u, "v_only")]["trS_ratio"] for u in boosts]),
        s1a_sep_cov=np.array([res1a[(u, "covariant")]["sep_ratio"] for u in boosts]),
        s1a_sep_von=np.array([res1a[(u, "v_only")]["sep_ratio"] for u in boosts]),
        s1b_h=np.array(h_vals),
        s1b_l1_D=np.array(l1_D),
        s1b_p_fit=p_fit,
        s1b_vf_diff16=vf_diff_16,
        s1b_vf_boost_diff=vf_boost_diff,
        s1c_t=np.array(t_1c),
        s1c_pop=np.array(pop_1c),
        s1c_total_slots=4 * N1c,
        s1c_dm=dm_1c,
        s1c_dP=dP_1c,
        s1c_min_eig=min(min_eig_1c),
        s1d_taub_D2=taub["D2"],
        s1d_taub_e2=taub["e2"],
        s1d_taub_Vs=taub["shock_speed"],
        s1d_xs_0=res1d[0.0]["xs"],
        s1d_Ds_0=res1d[0.0]["Ds"],
        s1d_xs_2=res1d[2.0]["xs"],
        s1d_Ds_2=res1d[2.0]["Ds"],
        s1d_xs_15=res1d[15.0]["xs"],
        s1d_Ds_15=res1d[15.0]["Ds"],
        s1d_xs_1e4=res1d[1.0e4]["xs"],
        s1d_Ds_1e4=res1d[1.0e4]["Ds"],
        s1d_es_1e4=res1d[1.0e4]["es"],
        s1d_D_cent_1e4=res1d[1.0e4]["D_cent"],
        s1d_e_cent_1e4=res1d[1.0e4]["e_cent"],
    )
    print(f"  Saved Suite 1 reduced data: {out_npz}", flush=True)
    return dict(res1a=res1a, h=h_vals, l1_D=l1_D, p_fit=p_fit, vf_diff16=vf_diff_16,
                vf_boost_diff=vf_boost_diff, t_1c=t_1c, pop_1c=pop_1c, N1c=N1c,
                dm_1c=dm_1c, dP_1c=dP_1c, res1d=res1d, taub=taub)


# ============================================================================
# SUITE 2: Kerr a = 0.9M Warm Sheared Inclined Cloud
# ============================================================================

def build_spherical_kerr_cloud_lat(n_cube: int, x0=(6.0, 0.0, 1.5), R_cl=1.0, sig_u=0.06, a=0.9, M=1.0):
    """Build uniform spherical lattice inside |x - x0| <= R_cl in prograde inclined Kerr orbit."""
    h = 2.0 * R_cl / n_cube
    c1 = -R_cl + (np.arange(n_cube) + 0.5) * h
    gx, gy, gz = np.meshgrid(c1, c1, c1, indexing="ij")
    d = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=-1)
    mask = np.sum(d * d, axis=1) <= R_cl * R_cl
    pts = d[mask] + np.asarray(x0, dtype=np.float64)[None, :]
    N = len(pts)

    # Set smooth prograde inclined orbital 4-velocity: evaluate local ADM & assign BL circular-like Lz
    # plus gentle radial infall so cloud orbits smoothly and experiences frame dragging & tidal shear
    r_bl_dummy = np.sqrt(np.sum(pts * pts, axis=1))
    # Convert CKS position -> BL (r, theta, phi) using kerr.convert_state with zero u
    _, x_bl, _ = _kerr.convert_state(0.0, pts, np.zeros_like(pts), "cks", "bl", a=a, M=M)
    r_bl = x_bl[:, 0]
    th_bl = x_bl[:, 1]
    sqM = math.sqrt(M)
    sq_r = np.sqrt(r_bl)
    denom = (r_bl ** 0.75) * np.sqrt(np.maximum(r_bl ** 1.5 - 3.0 * M * sq_r + 2.0 * a * sqM, 1e-12))
    Lz = sqM * (r_bl * r_bl - 2.0 * a * np.sqrt(M * r_bl) + a * a) / denom
    # Gentle radial infall & prograde grazing orbit keeping r_BL > r_+ while probing
    # strong-field frame dragging & tidal shearing around Kerr a = 0.9M
    u_bl = np.zeros_like(pts)
    u_bl[:, 0] = -0.03
    u_bl[:, 2] = 1.02 * Lz * (np.sin(th_bl) ** 2)
    _, x_cks, u_cks = _kerr.convert_state(0.0, x_bl, u_bl, "bl", "cks", a=a, M=M)

    adm_c = _kerr.adm("cks", x_cks, a=a, M=M, derivs=False)
    m_b = np.full((N, 1), 1.0 / N, dtype=np.float64)
    u_b = u_cks[:, None, :]
    Sig_b = (sig_u * sig_u) * adm_c.gamma[:, None, :, :]
    return x_cks, m_b, u_b, Sig_b, adm_c


def kerr_killing_invariants(x, m, u_bar, Sigma, a=0.9, M=1.0, n_q=3):
    """Compute mass-weighted E_inf = -u_t and L_z = u_phi across all basis cubature points."""
    N, Nb, _ = u_bar.shape
    adm_c = _kerr.adm("cks", x, a=a, M=M, derivs=False)
    E_tot = 0.0
    Lz_tot = 0.0
    m_tot = 0.0
    E_el = np.zeros(N, dtype=np.float64)
    Lz_el = np.zeros(N, dtype=np.float64)

    for idx in range(N):
        gi = np.linalg.inv(adm_c.gamma[idx])
        alp = float(adm_c.alpha[idx])
        beta = adm_c.beta[idx]
        xc = x[idx]
        for al in range(Nb):
            ma = float(m[idx, al])
            if ma <= 0.0:
                continue
            pts, ws = vg.basis_cubature_points(u_bar[idx, al], Sigma[idx, al], n_q=n_q)
            for q in range(len(ws)):
                u = pts[q]
                W = math.sqrt(1.0 + float(u @ gi @ u))
                e_q = alp * W - float(beta @ u)
                lz_q = float(xc[0] * u[1] - xc[1] * u[0])
                wm = ma * float(ws[q])
                E_tot += wm * e_q
                Lz_tot += wm * lz_q
                E_el[idx] += wm * e_q
                Lz_el[idx] += wm * lz_q
                m_tot += wm
    return E_tot / m_tot, Lz_tot / m_tot, E_el / np.maximum(np.sum(m, axis=1), 1e-30), Lz_el / np.maximum(np.sum(m, axis=1), 1e-30)


def write_kerr_athinput(cfg_path, basename, ic_path, pusher, dt, tlim, snap_dt):
    txt = f"""# Suite 2: Kerr a=0.9M Cartesian Kerr-Schild warm sheared cloud
<comment>
problem = {basename}

<job>
basename = {basename}

<mesh>
nghost   = 2
nx1      = 16
x1min    = -18.0
x1max    = 18.0
ix1_bc   = outflow
ox1_bc   = outflow
nx2      = 16
x2min    = -18.0
x2max    = 18.0
ix2_bc   = outflow
ox2_bc   = outflow
nx3      = 16
x3min    = -18.0
x3max    = 18.0
ix3_bc   = outflow
ox3_bc   = outflow

<meshblock>
nx1 = 16
nx2 = 16
nx3 = 16

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
metric             = kerr_schild
bh_mass            = 1.0
bh_spin            = 0.9
deposit            = false
tolerance          = 1.0e-12
max_iterations     = 200
dt                 = {dt:.12f}
alpha_exc          = 0.0
vlasov_kerr_r_exc  = 0.98
vlasov_basis       = tophat
vlasov_nperp       = 3
vlasov_nq_kick     = 3
vlasov_nq_dep      = 3
vlasov_pair_mode   = covariant
vlasov_analytic_vf = false
vlasov_substeps    = 0
vlasov_cfl         = 0.3
vlasov_bnd_detect  = true
particle_file      = {ic_path}
hist_dcycle        = 20
snap_dt            = {snap_dt:.12f}

<problem>
pgen_name   = nrpic_geodesic
metric_kind = kerr_schild
bh_mass     = 1.0
bh_spin     = 0.9
"""
    with open(cfg_path, "w") as f:
        f.write(txt)


def run_suite2():
    print("\n=== SUITE 2: Kerr a=0.9M Warm Sheared Inclined Cloud ===", flush=True)
    s2_run = os.path.join(RUN_BASE, "suite2")
    s2_prob = os.path.join(PROB_BASE, "suite2")
    os.makedirs(s2_run, exist_ok=True)
    os.makedirs(s2_prob, exist_ok=True)

    x0 = (6.0, 0.0, 1.5)
    R_cl = 1.0
    sig_u = 0.06
    dt = 0.05
    tlim = 30.0
    snap_dt = 5.0

    # Three GR-LBV spherical resolutions: n_cube = 10 (~512), 14 (~1400), 18 (~3050)
    kerr_res = {}
    for n_cube in (10, 14, 18):
        x, m_b, u_b, Sig_b, _ = build_spherical_kerr_cloud_lat(n_cube, x0=x0, R_cl=R_cl, sig_u=sig_u, a=0.9, M=1.0)
        N_el = len(x)
        ic_path = os.path.join(s2_run, f"ic_kerr_n{n_cube}.grlbv")
        vg.write_grlbv(ic_path, x, m_b, u_b, Sig_b, time=0.0)
        E0, Lz0, _, _ = kerr_killing_invariants(x, m_b, u_b, Sig_b)

        lbl = f"s2_grlbv_n{n_cube}"
        rdir = os.path.join(s2_run, lbl)
        clean_dir(rdir)
        cfg = os.path.join(s2_prob, f"{lbl}.athinput")
        write_kerr_athinput(cfg, lbl, ic_path, "vlasov_mfm", dt=dt, tlim=tlim, snap_dt=snap_dt)
        run_athena(cfg, rdir, lbl)

        snaps = sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))
        times, E_h, Lz_h, xcm_h = [], [], [], []
        sn_final = None
        r_bl_min = 1e9
        for sf in snaps:
            sn = vg.read_grlbv(sf)
            mt = np.sum(sn["m"], axis=1)
            live = mt > 0.0
            Et, Lzt, _, _ = kerr_killing_invariants(sn["x"][live], sn["m"][live], sn["u_bar"][live], sn["Sigma"][live])
            cm = np.sum(mt[:, None] * sn["x"], axis=0) / np.sum(mt)
            _, xb_s, _ = _kerr.convert_state(0.0, sn["x"][live], np.zeros_like(sn["x"][live]), "cks", "bl", a=0.9, M=1.0)
            r_bl_min = min(r_bl_min, float(xb_s[:, 0].min()))
            times.append(sn["time"]); E_h.append(Et); Lz_h.append(Lzt); xcm_h.append(cm)
            sn_final = sn
        hst = read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
        E_h = np.array(E_h); Lz_h = np.array(Lz_h); xcm_h = np.array(xcm_h)
        dE_rel = float(np.max(np.abs(E_h - E0) / abs(E0)))
        dLz_rel = float(np.max(np.abs(Lz_h - Lz0) / abs(Lz0)))
        dm_rel = float(np.max(np.abs(hst["m_tot"] - hst["m_tot"][0]) / abs(hst["m_tot"][0])))
        kerr_res[n_cube] = dict(
            N=N_el, times=np.array(times), E_h=E_h, Lz_h=Lz_h, xcm=xcm_h,
            dE_rel=dE_rel, dLz_rel=dLz_rel, dm_rel=dm_rel, sn_final=sn_final, r_bl_min=r_bl_min,
        )
        print(f"    GR-LBV n_cube={n_cube} (N={N_el}): dM={dm_rel:.2e}, rmin={r_bl_min:.3f}M, "
              f"max|dE/E0|={dE_rel:.3e}, max|dLz/Lz0|={dLz_rel:.3e}, "
              f"final CM=({xcm_h[-1,0]:.2f}, {xcm_h[-1,1]:.2f}, {xcm_h[-1,2]:.2f})", flush=True)

    # NRPIC midpoint comparison (N = 10^4 sampled from IDENTICAL spherical uniform ball + isotropic sig_u)
    N_mc = 10000
    rng = np.random.default_rng(42)
    # Rejection / spherical uniform sampling inside |d| <= R_cl
    dir_v = rng.normal(size=(N_mc, 3))
    dir_v /= np.linalg.norm(dir_v, axis=1, keepdims=True)
    rr = R_cl * (rng.uniform(0.0, 1.0, size=N_mc) ** (1.0 / 3.0))
    pts_mc = dir_v * rr[:, None] + np.asarray(x0, dtype=np.float64)[None, :]
    _, xbl_mc, _ = _kerr.convert_state(0.0, pts_mc, np.zeros_like(pts_mc), "cks", "bl", a=0.9, M=1.0)
    r_mc, th_mc = xbl_mc[:, 0], xbl_mc[:, 1]
    denom_mc = (r_mc ** 0.75) * np.sqrt(np.maximum(r_mc ** 1.5 - 3.0 * np.sqrt(r_mc) + 2.0 * 0.9, 1e-12))
    Lz_mc0 = (r_mc ** 2 - 2.0 * 0.9 * np.sqrt(r_mc) + 0.81) / denom_mc
    ubl_mc = np.zeros_like(pts_mc)
    ubl_mc[:, 0] = -0.03
    ubl_mc[:, 2] = 1.02 * Lz_mc0 * (np.sin(th_mc) ** 2)
    _, x_mc, u_bar_mc = _kerr.convert_state(0.0, xbl_mc, ubl_mc, "bl", "cks", a=0.9, M=1.0)
    adm_mc = _kerr.adm("cks", x_mc, a=0.9, M=1.0, derivs=False)
    # Top-hat 3D uniform cube [-sqrt(3)*sig_u, +sqrt(3)*sig_u]^3 in local orthonormal triad L: L L^T = gamma
    L_chol = np.linalg.cholesky(adm_mc.gamma)
    eta_mc = rng.uniform(-math.sqrt(3.0), math.sqrt(3.0), size=(N_mc, 3)) * sig_u
    u_mc = u_bar_mc + np.einsum("aij,aj->ai", L_chol, eta_mc)
    m_mc = np.full(N_mc, 1.0 / N_mc, dtype=np.float64)

    ic_mc = os.path.join(s2_run, "ic_kerr_mc10k.nrp")
    nio.write_nrp(ic_mc, x_mc, u_mc, m_mc)
    lbl_mc = "s2_nrpic_mc10k"
    rdir_mc = os.path.join(s2_run, lbl_mc)
    clean_dir(rdir_mc)
    cfg_mc = os.path.join(s2_prob, f"{lbl_mc}.athinput")
    write_kerr_athinput(cfg_mc, lbl_mc, ic_mc, "midpoint", dt=dt, tlim=tlim, snap_dt=snap_dt)
    run_athena(cfg_mc, rdir_mc, lbl_mc)

    mc_snaps = sorted(glob.glob(os.path.join(rdir_mc, f"{lbl_mc}.part.[0-9]*.bin")))
    times_mc, E_mc_h, Lz_mc_h, cm_mc_h = [], [], [], []
    d_mc_final = None
    for sf in mc_snaps:
        t_s, d_s, _, _ = read_nrp_snapshot(sf)
        xs = d_s[:, 0:3]; us = d_s[:, 3:6]; ms = d_s[:, 6]
        adms = _kerr.adm("cks", xs, a=0.9, M=1.0, derivs=False)
        e_arr = np.zeros(len(ms))
        lz_arr = xs[:, 0] * us[:, 1] - xs[:, 1] * us[:, 0]
        for i in range(len(ms)):
            gi = np.linalg.inv(adms.gamma[i])
            W = math.sqrt(1.0 + float(us[i] @ gi @ us[i]))
            e_arr[i] = float(adms.alpha[i]) * W - float(adms.beta[i] @ us[i])
        times_mc.append(t_s)
        E_mc_h.append(float(np.sum(ms * e_arr) / np.sum(ms)))
        Lz_mc_h.append(float(np.sum(ms * lz_arr) / np.sum(ms)))
        cm_mc_h.append(np.sum(ms[:, None] * xs, axis=0) / np.sum(ms))
        d_mc_final = d_s
    E_mc_h = np.array(E_mc_h); Lz_mc_h = np.array(Lz_mc_h); cm_mc_h = np.array(cm_mc_h)
    print(f"    NRPIC midpoint (N=10^4): max|dE/E0|={np.max(np.abs(E_mc_h - E_mc_h[0])/abs(E_mc_h[0])):.3e}, "
          f"max|dLz/Lz0|={np.max(np.abs(Lz_mc_h - Lz_mc_h[0])/abs(Lz_mc_h[0])):.3e}, "
          f"final CM=({cm_mc_h[-1,0]:.2f}, {cm_mc_h[-1,1]:.2f}, {cm_mc_h[-1,2]:.2f})", flush=True)

    # Compare azimuthal neighbor-density Poisson roughness at t=30M:
    # Measure coefficient of variation of local SPH/KDE azimuthal column density along the tidal arc
    sn18 = kerr_res[18]["sn_final"]
    # Evaluate 1D KDE along azimuthal angle around median orbital angle on an annulus of core elements
    phi_lbv = np.arctan2(sn18["x"][:, 1], sn18["x"][:, 0])
    phi_mc = np.arctan2(d_mc_final[:, 1], d_mc_final[:, 0])
    m_lbv = sn18["m"][:, 0]
    m_mcf = d_mc_final[:, 6]
    phi_cm = math.atan2(kerr_res[18]["xcm"][-1, 1], kerr_res[18]["xcm"][-1, 0])
    # Wrap to phi_cm +/- 0.25 rad and compute kernel density scatter along fine bins
    def wrap_phi(p):
        d = p - phi_cm
        return (d + math.pi) % (2.0 * math.pi) - math.pi
    dphi_lbv = wrap_phi(phi_lbv)
    dphi_mc = wrap_phi(phi_mc)
    bins = np.linspace(-0.20, 0.20, 25)
    hist_mc, _ = np.histogram(dphi_mc, bins=bins, weights=m_mcf)
    # Smooth MFM density vs binned MC density smoothness (high-frequency discrete second-diff / mean)
    def sec_diff_roughness(y):
        s = np.std(np.diff(y, 2)) / max(np.mean(y), 1e-30)
        return float(s)
    # For MFM, deposit elements onto same bins via cubic spline overlap widths h_phi ~ h / r_cm
    rcm = float(np.linalg.norm(kerr_res[18]["xcm"][-1]))
    dx_mat = sn18["x"][None, :, :] - sn18["x"][:, None, :]
    d2_mat = np.sum(dx_mat * dx_mat, axis=-1)
    np.fill_diagonal(d2_mat, np.inf)
    h_nn = float(np.mean(np.sqrt(np.min(d2_mat, axis=1))))
    dphi_grid = 0.5 * (bins[:-1] + bins[1:])
    sig_phi = max(h_nn / max(rcm, 1e-6) * 0.65, 1e-3)
    # Gaussian/spline kernel weighted profile at grid points for MFM elements vs MC particles in identical kernel!
    dens_lbv = np.zeros_like(dphi_grid)
    dens_mc_k = np.zeros_like(dphi_grid)
    for gi, pg in enumerate(dphi_grid):
        dens_lbv[gi] = np.sum(m_lbv * np.exp(-0.5 * ((dphi_lbv - pg) / sig_phi) ** 2))
        dens_mc_k[gi] = np.sum(m_mcf * np.exp(-0.5 * ((dphi_mc - pg) / sig_phi) ** 2))
    rough_lbv = sec_diff_roughness(dens_lbv)
    rough_mc_hist = sec_diff_roughness(hist_mc)
    rough_mc_k = sec_diff_roughness(dens_mc_k)
    print(f"    Core arc roughness: GR-LBV(N={kerr_res[18]['N']})={rough_lbv:.4f}, "
          f"NRPIC_MC10k(hist)={rough_mc_hist:.4f}, NRPIC_MC10k(same KDE)={rough_mc_k:.4f}", flush=True)

    out_npz = os.path.join(DATA_BASE, "suite2_kerr_cloud.npz")
    np.savez(
        out_npz,
        times=kerr_res[18]["times"],
        lbv_n10_N=kerr_res[10]["N"], lbv_n14_N=kerr_res[14]["N"], lbv_n18_N=kerr_res[18]["N"],
        lbv_n10_E=kerr_res[10]["E_h"], lbv_n10_Lz=kerr_res[10]["Lz_h"], lbv_n10_cm=kerr_res[10]["xcm"],
        lbv_n14_E=kerr_res[14]["E_h"], lbv_n14_Lz=kerr_res[14]["Lz_h"], lbv_n14_cm=kerr_res[14]["xcm"],
        lbv_n18_E=kerr_res[18]["E_h"], lbv_n18_Lz=kerr_res[18]["Lz_h"], lbv_n18_cm=kerr_res[18]["xcm"],
        lbv_n10_rmin=kerr_res[10]["r_bl_min"], lbv_n14_rmin=kerr_res[14]["r_bl_min"], lbv_n18_rmin=kerr_res[18]["r_bl_min"],
        lbv_n18_x=sn18["x"], lbv_n18_m=sn18["m"][:, 0], lbv_n18_u=sn18["u_bar"][:, 0],
        mc_times=times_mc, mc_E=E_mc_h, mc_Lz=Lz_mc_h, mc_cm=cm_mc_h,
        mc_x=d_mc_final[:, 0:3], mc_m=d_mc_final[:, 6], mc_u=d_mc_final[:, 3:6],
        dphi_grid=dphi_grid, dens_lbv=dens_lbv, dens_mc_k=dens_mc_k, hist_mc=hist_mc,
        rough_lbv=rough_lbv, rough_mc_hist=rough_mc_hist, rough_mc_k=rough_mc_k,
        cm_diff_fin=float(np.linalg.norm(kerr_res[18]["xcm"][-1] - cm_mc_h[-1])),
    )
    print(f"  Saved Suite 2 reduced data: {out_npz}", flush=True)
    return dict(kerr_res=kerr_res, times_mc=times_mc, E_mc_h=E_mc_h, Lz_mc_h=Lz_mc_h,
                cm_mc_h=cm_mc_h, d_mc_final=d_mc_final, rough_lbv=rough_lbv, rough_mc_hist=rough_mc_hist)


# ============================================================================
# SUITE 3: Full-GR Oppenheimer-Snyder Collapse (R_0 = 5M, Z4c + AMR + FastFlow)
# ============================================================================

def write_os_amr_athinput(cfg_path, basename, part_file, tab_file, pusher, tlim=25.0):
    extra_vlasov = ""
    if pusher == "vlasov_mfm":
        extra_vlasov = """vlasov_basis        = tophat
vlasov_nperp        = 3
vlasov_nq_kick      = 1
vlasov_nq_dep       = 1
vlasov_pair_mode    = covariant
vlasov_analytic_vf  = false
vlasov_substeps     = 1
vlasov_cfl          = 0.3
vlasov_bnd_detect   = true
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
{extra_vlasov}
<problem>
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


def run_suite3():
    print("\n=== SUITE 3: Full-GR Oppenheimer-Snyder Collapse (R_0 = 5M, Z4c+AMR+FastFlow) ===", flush=True)
    s3_run = os.path.join(RUN_BASE, "suite3")
    s3_prob = os.path.join(PROB_BASE, "suite3")
    os.makedirs(s3_run, exist_ok=True)
    os.makedirs(s3_prob, exist_ok=True)

    tab_path = os.path.join(s3_run, "os_R5.tab")
    _osn.write_table(tab_path, R0=5.0, M=1.0, n_matter=4000, rmax_factor=1.5)

    runs_spec = [
        ("s3_grlbv_n20", "vlasov_mfm", 20),
        ("s3_grlbv_n26", "vlasov_mfm", 26),
        ("s3_nrpic_n26", "midpoint", 26),
    ]
    tlim = 25.0
    res3 = {}
    E0_analytic = _osn.rho0(5.0, 1.0)
    M_rest_analytic = _osn.rest_mass(5.0, 1.0)

    for lbl, pusher, nlat in runs_spec:
        x, u, m, sp = _samp.sample_os(
            method="lattice", R0=5.0, M=1.0, n_lat=nlat, surface_correction=True
        )
        N_p = len(m)
        if pusher == "vlasov_mfm":
            ic_path = os.path.join(s3_run, f"ic_{lbl}.grlbv")
            m_b = m[:, None]
            u_b = u[:, None, :]
            S_b = np.zeros((N_p, 1, 3, 3), dtype=np.float64)
            vg.write_grlbv(ic_path, x, m_b, u_b, S_b, species=sp, time=0.0)
        else:
            ic_path = os.path.join(s3_run, f"ic_{lbl}.nrp")
            nio.write_nrp(ic_path, x, u, m, species=sp)

        rdir = os.path.join(s3_run, lbl)
        clean_dir(rdir)
        cfg = os.path.join(s3_prob, f"{lbl}.athinput")
        write_os_amr_athinput(cfg, lbl, ic_path, tab_path, pusher, tlim=tlim)
        elapsed = run_athena(cfg, rdir, lbl)

        z4c = read_col_hst(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
        nrp = read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        ah = read_horizon(os.path.join(rdir, f"{lbl}.horizon_summary_0.txt"))
        vlv = read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst")) if pusher == "vlasov_mfm" else {}

        active_arr = vlv["n_active"] if pusher == "vlasov_mfm" else nrp["np"]
        sum_m_arr = vlv["m_tot"] if pusher == "vlasov_mfm" else nrp["sum_m"]
        m_exc_arr = vlv["m_excised"] if pusher == "vlasov_mfm" else nrp["m_excised"]
        t_part = vlv["time"] if pusher == "vlasov_mfm" else nrp["time"]

        t_z = z4c["time"]
        H_l2 = np.sqrt(np.maximum(z4c["H-norm2"], 0.0))
        M_l2 = np.sqrt(np.maximum(z4c["M-norm2"], 0.0))
        t_ah_first = float(ah[0, 0]) if len(ah) else np.nan
        M_ah_fin = float(ah[-1, 1]) if len(ah) else np.nan
        # Probe comparisons up to tau <= 2.6M against Staley bound & cycloid
        tau = nrp["tau_probe"]
        mask_p = (tau > 0.0) & (tau <= 2.6) & (active_arr > 0)
        a_ll = np.array([float(_osn.staley_lower_bound(x_t)) for x_t in tau[mask_p]])
        rho_cyc = np.array([float(_osn.cycloid_rho(x_t)) for x_t in tau[mask_p]]) / E0_analytic
        max_alp_err = float(np.max(np.abs(nrp["alpha_probe"][mask_p] - a_ll))) if np.any(mask_p) else np.nan
        max_rho_err = float(np.max(np.abs(nrp["E_probe"][mask_p] / E0_analytic - rho_cyc) / rho_cyc)) if np.any(mask_p) else np.nan
        # Compare t_exc: time when m_excised reaches 99% of initial mass
        m0_val = float(sum_m_arr[0])
        exc_frac = m_exc_arr / max(m0_val, 1e-30)
        idx_exc = np.nonzero(exc_frac > 0.99)[0]
        t_exc99 = float(t_part[idx_exc[0]]) if len(idx_exc) else np.nan
        unconv = int(np.max(nrp["push_unconverged"])) if "push_unconverged" in nrp else 0

        res3[lbl] = dict(
            N=N_p, elapsed=elapsed, z4c=z4c, nrp=nrp, vlv=vlv, ah=ah,
            sum_m_arr=sum_m_arr, m_exc_arr=m_exc_arr,
            H_l2=H_l2, M_l2=M_l2, t_z=t_z,
            t_ah_first=t_ah_first, M_ah_fin=M_ah_fin, t_exc99=t_exc99,
            max_alp_err=max_alp_err, max_rho_err=max_rho_err,
            H_max=float(np.max(H_l2)), M_max=float(np.max(M_l2)),
            H_fin=float(H_l2[-1]), M_fin=float(M_l2[-1]),
            unconv=unconv,
        )
        print(f"    {lbl} (N={N_p}, {elapsed:.1f}s): unconv={unconv}, "
              f"alp_err(<=2.6M)={max_alp_err:.2e}, rho_err={max_rho_err:.2e}, "
              f"t_AH={t_ah_first:.2f}M, M_AH={M_ah_fin:.4f}M, t_exc99={t_exc99:.2f}M, "
              f"||H||_max={np.max(H_l2):.3e}, ||M||_max={np.max(M_l2):.3e}", flush=True)

    # Save reduced Suite 3 dataset
    out_npz = os.path.join(DATA_BASE, "suite3_os_collapse.npz")
    save_kw = dict(E0=E0_analytic, M_rest=M_rest_analytic, tau_collapse=_osn.collapse_time(5.0, 1.0))
    for lbl in ("s3_grlbv_n20", "s3_grlbv_n26", "s3_nrpic_n26"):
        r = res3[lbl]
        p = lbl + "_"
        save_kw[p + "t_nrp"] = r["nrp"]["time"]
        save_kw[p + "tau_probe"] = r["nrp"]["tau_probe"]
        save_kw[p + "alp_probe"] = r["nrp"]["alpha_probe"]
        save_kw[p + "E_probe"] = r["nrp"]["E_probe"]
        save_kw[p + "sum_m"] = r["sum_m_arr"]
        save_kw[p + "m_excised"] = r["m_exc_arr"]
        save_kw[p + "nmb"] = r["nrp"]["nmb"]
        save_kw[p + "t_z4c"] = r["t_z"]
        save_kw[p + "H_l2"] = r["H_l2"]
        save_kw[p + "M_l2"] = r["M_l2"]
        save_kw[p + "ah_t"] = r["ah"][:, 0] if len(r["ah"]) else np.array([])
        save_kw[p + "ah_M"] = r["ah"][:, 1] if len(r["ah"]) else np.array([])
        save_kw[p + "t_AH"] = r["t_ah_first"]
        save_kw[p + "M_AH_fin"] = r["M_ah_fin"]
        save_kw[p + "t_exc99"] = r["t_exc99"]
        save_kw[p + "H_max"] = r["H_max"]
        save_kw[p + "M_max"] = r["M_max"]
    np.savez(out_npz, **save_kw)
    print(f"  Saved Suite 3 reduced data: {out_npz}", flush=True)
    return res3


# ============================================================================
# Diagnostic Overview Figure for Suites 1, 2, 3
# ============================================================================

def plot_diag():
    d1 = np.load(os.path.join(DATA_BASE, "suite1_sr_flat.npz"))
    d2 = np.load(os.path.join(DATA_BASE, "suite2_kerr_cloud.npz"))
    d3 = np.load(os.path.join(DATA_BASE, "suite3_os_collapse.npz"))

    cz.use_style()
    fig, axes = plt.subplots(3, 2, figsize=(8.0, 9.5))
    fig.subplots_adjust(left=0.105, right=0.97, bottom=0.06, top=0.96, wspace=0.29, hspace=0.38)

    # Row 1 Left: Suite 1A & 1B - Warm wave convergence & 1A/1C summary
    ax = axes[0, 0]
    h = d1["s1b_h"]; err = d1["s1b_l1_D"]
    ax.loglog(h, err, "o-", color=cz.PAL["red"], ms=4.5, lw=1.5,
              label=rf"Warm wave $L_1(D)$ (slope {d1['s1b_p_fit']:.2f})")
    ref_line = err[0] * (h / h[0]) ** 2
    ax.loglog(h, ref_line, label=r"$\propto h^2$ reference", **cz.GUIDE)
    ax.set_xticks([1.0 / 16.0, 1.0 / 12.0, 1.0 / 8.0])
    ax.set_xticklabels(["1/16", "1/12", "1/8"])
    cz.no_minor_labels(ax, "x")
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Element spacing $h$")
    ax.set_ylabel(r"$L_1(D - D_{\rm ref})$")
    ax.legend(loc="upper left", fontsize=8.2)
    ax.set_title("Suite 1A/1B: 3D wave convergence", fontsize=11)
    txt_1abc = (
        f"1A |u|=3 sep: cov={d1['s1a_sep_cov'][-1]:.3f}, v_only={d1['s1a_sep_von'][-1]:.3f}\n"
        f"1B Brent vs analytic (16^3): {d1['s1b_vf_diff16']:.2e}\n"
        f"1C Nb=4 slots: {d1['s1c_pop'][0]} -> {d1['s1c_pop'][-1]}/{int(d1['s1c_total_slots'])}"
    )
    ax.text(0.97, 0.05, txt_1abc, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.2)

    # Row 1 Right: Suite 1D - Colliding beams / Taub double shock
    ax = axes[0, 1]
    ax.plot(d1["s1d_xs_0"], d1["s1d_Ds_0"], ".", ms=2.2, color=cz.PAL["blue"], label=r"$\sigma/\mu = 0$")
    ax.plot(d1["s1d_xs_2"], d1["s1d_Ds_2"], ".", ms=2.2, color=cz.PAL["orange"], label=r"$\sigma/\mu = 2$")
    ax.plot(d1["s1d_xs_15"], d1["s1d_Ds_15"], ".", ms=2.2, color=cz.PAL["green"], label=r"$\sigma/\mu = 15$")
    ax.plot(d1["s1d_xs_1e4"], d1["s1d_Ds_1e4"], "-", lw=1.5, color=cz.PAL["red"], label=r"$\sigma/\mu = 10^4$")
    Vs = float(d1["s1d_taub_Vs"]); D2 = float(d1["s1d_taub_D2"])
    x_sh = [0.5 - Vs * 0.55, 0.5 + Vs * 0.55]
    ax.plot([0.28, x_sh[0], x_sh[0], x_sh[1], x_sh[1], 0.72], [1.0, 1.0, D2, D2, 1.0, 1.0],
            color="k", ls="--", lw=1.2, label="Exact Taub")
    ax.set_xlim(0.28, 0.72)
    ax.set_ylim(0.5, 5.75)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"Lab rest-mass density $D(x)$")
    ax.legend(ncol=2, loc="upper center", fontsize=7.8, columnspacing=1.0)
    ax.set_title(r"Suite 1D: 3D colliding beams ($t = 0.55$)", fontsize=11)

    # Row 2 Left: Suite 2 - Kerr cloud orbital snapshot (x-y projection at t=30M)
    ax = axes[1, 0]
    n18_N = int(d2["lbv_n18_N"]) if "lbv_n18_N" in d2 else len(d2["lbv_n18_x"])
    ax.scatter(d2["mc_x"][::4, 0], d2["mc_x"][::4, 1], s=4, alpha=0.45, color=cz.PAL["blue"],
               rasterized=True, label=r"NRPIC ($10^4$)")
    ax.scatter(d2["lbv_n18_x"][:, 0], d2["lbv_n18_x"][:, 1], s=6, alpha=0.72, color=cz.PAL["red"],
               rasterized=True, label=rf"GR-LBV ($N = {n18_N}$)")
    bh_c = plt.Circle((0, 0), 1.436, color="k", alpha=0.85)
    ax.add_patch(bh_c)
    ax.set_aspect("equal")
    ax.set_xlim(-6.2, 4.2)
    ax.set_ylim(-2.6, 12.8)
    ax.set_xlabel(r"$x\,[M]$")
    ax.set_ylabel(r"$y\,[M]$")
    ax.legend(loc="upper left", fontsize=8.0)
    ax.set_title(r"Suite 2: Kerr $a = 0.9M$ cloud ($t = 30\,M$)", fontsize=11)

    # Row 2 Right: Suite 2 - Killing invariants & azimuthal profile smoothness
    ax = axes[1, 1]
    t2 = d2["times"]
    n10_N = int(d2["lbv_n10_N"]) if "lbv_n10_N" in d2 else 552
    ax.semilogy(d2["mc_times"], np.maximum(np.abs(d2["mc_E"] - d2["mc_E"][0]) / abs(d2["mc_E"][0]), 1e-12),
                color=cz.PAL["blue"], ls=":", lw=1.5, label=r"NRPIC $10^4$ $|\Delta E_\infty/E_0|$")
    ax.semilogy(t2, np.maximum(np.abs(d2["lbv_n10_E"] - d2["lbv_n10_E"][0]) / abs(d2["lbv_n10_E"][0]), 1e-12),
                "o--", color=cz.PAL["orange"], ms=3.0, lw=1.2, label=rf"$|\Delta E_\infty/E_0|$ ($N = {n10_N}$)")
    ax.semilogy(t2, np.maximum(np.abs(d2["lbv_n18_E"] - d2["lbv_n18_E"][0]) / abs(d2["lbv_n18_E"][0]), 1e-12),
                "s-", color=cz.PAL["red"], ms=3.5, lw=1.5, label=rf"$|\Delta E_\infty/E_0|$ ($N = {n18_N}$)")
    ax.semilogy(t2, np.maximum(np.abs(d2["lbv_n18_Lz"] - d2["lbv_n18_Lz"][0]) / abs(d2["lbv_n18_Lz"][0]), 1e-12),
                "^-", color=cz.PAL["green"], ms=3.5, lw=1.5, label=rf"$|\Delta L_z/L_{{z0}}|$ ($N = {n18_N}$)")
    ax.set_xlabel(r"Time $t\,[M]$")
    ax.set_ylabel("Relative Killing drift")
    ax.set_ylim(1e-9, 5e-2)
    cz.no_minor_labels(ax, "y")
    ax.legend(ncol=2, loc="upper left", fontsize=7.2, columnspacing=0.8)
    ax.text(0.96, 0.06, f"Arc rough: LBV {d2['rough_lbv']:.3f} vs MC {d2['rough_mc_hist']:.3f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8)
    ax.set_title("Suite 2: Kerr Killing invariant drift", fontsize=11)

    # Row 3 Left: Suite 3 - OS collapse lapse vs analytic Staley bound
    ax = axes[2, 0]
    tt = np.linspace(0.0, min(float(np.max(d3["s3_grlbv_n26_tau_probe"])), 0.99 * float(d3["tau_collapse"])), 400)
    a_ll = np.array([float(_osn.staley_lower_bound(x_t)) for x_t in tt])
    ax.plot(d3["s3_nrpic_n26_tau_probe"], d3["s3_nrpic_n26_alp_probe"], "--", lw=1.5, color=cz.PAL["blue"],
            label="NRPIC (9328)")
    ax.plot(d3["s3_grlbv_n20_tau_probe"], d3["s3_grlbv_n20_alp_probe"], ":", lw=1.5, color=cz.PAL["green"],
            label="GR-LBV (4168)")
    ax.plot(d3["s3_grlbv_n26_tau_probe"], d3["s3_grlbv_n26_alp_probe"], "-", lw=1.5, color=cz.PAL["red"],
            label="GR-LBV (9328)")
    ax.plot(tt, a_ll, color="k", ls="--", lw=1.2, label="Staley 1+log")
    ax.set_xlabel(r"Central proper time $\tau_{\rm c}\,[M]$")
    ax.set_ylabel(r"Central lapse $\alpha_{\rm c}$")
    ax.set_ylim(-0.02, 1.08)
    ax.legend(loc="upper right", fontsize=8.0)
    ax.set_title("Suite 3: OS collapse lapse & excision", fontsize=11)

    # Row 3 Right: Suite 3 - Z4c constraints & FastFlow apparent horizon
    ax = axes[2, 1]
    ax.semilogy(d3["s3_nrpic_n26_t_z4c"], np.maximum(d3["s3_nrpic_n26_H_l2"], 1e-12), "--", lw=1.5,
                color=cz.PAL["blue"], label=r"$\|\mathcal{H}\|_2$ NRPIC 9328")
    ax.semilogy(d3["s3_grlbv_n20_t_z4c"], np.maximum(d3["s3_grlbv_n20_H_l2"], 1e-12), ":", lw=1.5,
                color=cz.PAL["green"], label=r"$\|\mathcal{H}\|_2$ GR-LBV 4168")
    ax.semilogy(d3["s3_grlbv_n26_t_z4c"], np.maximum(d3["s3_grlbv_n26_H_l2"], 1e-12), "-", lw=1.5,
                color=cz.PAL["red"], label=r"$\|\mathcal{H}\|_2$ GR-LBV 9328")
    ax.semilogy(d3["s3_grlbv_n26_t_z4c"], np.maximum(d3["s3_grlbv_n26_M_l2"], 1e-12), "-.", lw=1.3,
                color=cz.PAL["red"], alpha=0.80, label=r"$\|\mathcal{M}\|_2$ GR-LBV 9328")
    t_ah = float(d3["s3_grlbv_n26_t_AH"])
    if np.isfinite(t_ah):
        ax.axvline(t_ah, **cz.MASK_LINE)
        ax.text(t_ah + 0.35, 0.88, r"$t_{\rm AH}$", transform=ax.get_xaxis_transform(), fontsize=8.5)
    ax.set_ylim(1e-4, 3e1)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Coordinate time $t\,[M]$")
    ax.set_ylabel(r"Z4c constraint $L_2$ norm")
    ax.legend(ncol=2, loc="lower right", fontsize=7.5, columnspacing=0.9)
    ax.text(0.04, 0.94,
            rf"$M_{{\rm AH}} = {d3['s3_grlbv_n26_M_AH_fin']:.4f}$ (LBV & NRPIC)",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.0)
    ax.set_title("Suite 3: Z4c constraints & horizon", fontsize=11)

    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)
    fig.savefig(FIG_OUT, dpi=300)
    print(f"Saved diagnostic figure: {FIG_OUT}", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="all", choices=["1", "2", "3", "all", "plot"])
    args = p.parse_args()
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(PROB_BASE, exist_ok=True)
    os.makedirs(DATA_BASE, exist_ok=True)

    if args.suite in ("1", "all"):
        run_suite1()
    if args.suite in ("2", "all"):
        run_suite2()
    if args.suite in ("3", "all"):
        run_suite3()
    if args.suite in ("plot", "all"):
        plot_diag()
    print("STAGE 4A COMPLETE", flush=True)


if __name__ == "__main__":
    main()
