#!/usr/bin/env python3
"""Reduce Wave 4A & 4B physics snapshots/histories to compact <2 MB .npz archives
for publication-grade physics figures in `vlasov_gr/paper/figures/`.

Reads simulation outputs under `$SCRATCH_ROOT/runs/repro_wave4{a,b}` on the compute node.
Run on a compute node:
    $SCRATCH/venv/bin/python vlasov_gr/paper/scripts/make_physics_data.py
"""
import glob
import math
import os
import re
import sys
from math import factorial
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "analysis"))

from nrpic import kerr as _kerr  # noqa: E402
from nrpic.vlasov_gr import read_grlbv  # noqa: E402
from diag.common import read_athena_hst, read_curv_hst, read_curv_slice, read_traj  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH",
    os.environ.get("SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"),
)
DATA_DIR = os.path.join(REPO, "vlasov_gr", "paper", "data")


def read_col_hst(path: str) -> dict:
    cols = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                cols = re.findall(r"\[\d+\]=([A-Za-z0-9_\-]+)", line)
    a = np.loadtxt(path)
    if a.ndim == 1:
        a = a[None, :]
    _, idx = np.unique(a[::-1, 0], return_index=True)
    a = a[len(a) - 1 - idx]
    return {c: a[:, i] for i, c in enumerate(cols) if i < a.shape[1]}


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


def horizon_radius(coef: np.ndarray, theta: np.ndarray, phi: np.ndarray, lmax: int = 8) -> np.ndarray:
    r, i = np.zeros_like(theta, dtype=float), 0
    for l in range(lmax + 1):
        re_, _ = ylm(l, 0, theta, phi)
        r += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, theta, phi)
            r += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return r


def read_shapes(path: str) -> dict:
    out, t = {}, None
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", line)
                if m:
                    t = float(m.group(1))
            elif line.strip() and t is not None:
                out[t] = np.array(line.split(), dtype=float)
    return out


def rasterize_curv_amr(arr: np.ndarray, half: float, n_pix: int = 260):
    """Paint finite-volume (x, z, dx, I, E, alpha) AMR leaf cells coarsest-to-finest."""
    xc, zc, dx, Ival, Eval = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4]
    sel = (np.abs(xc) - 0.5 * dx <= half) & (np.abs(zc) - 0.5 * dx <= half)
    xc, zc, dx, Ival, Eval = xc[sel], zc[sel], dx[sel], Ival[sel], Eval[sel]
    order = np.argsort(-dx)  # coarsest first, finest overwrites

    I_img = np.zeros((n_pix, n_pix), dtype=np.float32)
    E_img = np.zeros((n_pix, n_pix), dtype=np.float32)
    pix_size = (2.0 * half) / n_pix

    for idx in order:
        x0, x1 = xc[idx] - 0.5 * dx[idx], xc[idx] + 0.5 * dx[idx]
        z0, z1 = zc[idx] - 0.5 * dx[idx], zc[idx] + 0.5 * dx[idx]
        ix0 = max(0, int(math.floor((x0 + half) / pix_size)))
        ix1 = min(n_pix, int(math.ceil((x1 + half) / pix_size)))
        iz0 = max(0, int(math.floor((z0 + half) / pix_size)))
        iz1 = min(n_pix, int(math.ceil((z1 + half) / pix_size)))
        if ix1 > ix0 and iz1 > iz0:
            I_img[iz0:iz1, ix0:ix1] = float(Ival[idx])
            E_img[iz0:iz1, ix0:ix1] = float(Eval[idx])
    return I_img, E_img


def build_prolate_data():
    print("Building physics_prolate.npz ...", flush=True)
    d_hyb = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5b", "prol_100k_qmc_hyb")
    d_mid = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5b", "prol_100k_mc_mid")

    out = {"half": np.array([10.5, 7.2, 4.6, 2.2]), "snap_idx": np.array([0, 82, 110, 128])}

    # 4 slices rasterized + outer |z| where E > 1e-4 from every 2nd curv file
    snap_t = []
    for j, (idx, half) in enumerate(zip((0, 82, 110, 128), (10.5, 7.2, 4.6, 2.2))):
        t, arr = read_curv_slice(os.path.join(d_hyb, f"prol_100k_qmc_hyb.curv.{idx:05d}.bin"))
        snap_t.append(t)
        I_img, E_img = rasterize_curv_amr(arr, half, n_pix=260)
        out[f"s{j}_t"] = np.float64(t)
        out[f"s{j}_I"] = I_img
        out[f"s{j}_E"] = E_img
    out["snap_t"] = np.array(snap_t)

    # Axial extent of matter core (E >= 1e-3, before AH swallows) across curv sequence
    c_files = sorted(glob.glob(os.path.join(d_hyb, "prol_100k_qmc_hyb.curv.*.bin")))
    zenv_t, zenv_z = [], []
    for cf in c_files:
        tc, arr = read_curv_slice(cf)
        core = arr[:, 4] >= 1.0e-3
        zenv_t.append(tc)
        zenv_z.append(float(np.max(np.abs(arr[core, 1]))) if np.any(core) else np.nan)
    out["zenv_t"] = np.array(zenv_t)
    out["zenv_z"] = np.array(zenv_z)

    for tag, d, pref in (("hyb", d_hyb, "prol_100k_qmc_hyb"), ("mid", d_mid, "prol_100k_mc_mid")):
        ch = read_curv_hst(os.path.join(d, f"{pref}.curv.hst"))
        nh = read_col_hst(os.path.join(d, f"{pref}.nrpic.hst"))
        ah = np.loadtxt(os.path.join(d, f"{pref}.horizon_summary_0.txt"))
        zh = read_athena_hst(os.path.join(d, f"{pref}.z4c.user.hst"))

        out[f"{tag}_c_t"] = ch[:, 0]
        out[f"{tag}_c_I"] = ch[:, 1]
        out[f"{tag}_c_Ix"] = ch[:, 2]
        out[f"{tag}_c_Iy"] = ch[:, 3]
        out[f"{tag}_c_Iz"] = ch[:, 4]

        out[f"{tag}_h_t"] = nh["time"]
        out[f"{tag}_h_amin"] = nh["alpha_min"]
        out[f"{tag}_h_mfrac"] = nh["sum_m"] / nh["sum_m"][0]

        out[f"{tag}_ah_t"] = ah[:, 1]
        out[f"{tag}_ah_M"] = ah[:, 2]
        out[f"{tag}_z_t"] = zh["time"]
        out[f"{tag}_z_H"] = np.sqrt(np.maximum(zh["H-norm2"], 0.0))

    # Apparent horizon shape cross-section at first detection (t=32M) & polar radius vs time
    ah_hyb_t = out["hyb_ah_t"]
    ah_hyb_M = out["hyb_ah_M"]
    found = np.isfinite(ah_hyb_M)
    tf = ah_hyb_t[found]
    shapes = read_shapes(os.path.join(d_hyb, "prol_100k_qmc_hyb.horizon_shape_0.txt"))
    zero, pi = np.array([0.0]), np.array([np.pi])
    rp = np.array([horizon_radius(shapes[x], zero, zero)[0] for x in tf if x in shapes])
    tf_s = np.array([x for x in tf if x in shapes])
    out["hyb_ah_tf"] = tf_s
    out["hyb_ah_rp"] = rp
    t1 = float(tf_s[0])
    th = np.linspace(0.0, np.pi, 181)
    r_pos = horizon_radius(shapes[t1], th, np.zeros_like(th))
    r_neg = horizon_radius(shapes[t1], th, np.full_like(th, np.pi))
    out["ah_first_t"] = np.float64(t1)
    out["ah_sec_x"] = np.r_[r_pos * np.sin(th), -(r_neg * np.sin(th))[::-1]]
    out["ah_sec_z"] = np.r_[r_pos * np.cos(th), (r_neg * np.cos(th))[::-1]]

    p_out = os.path.join(DATA_DIR, "physics_prolate.npz")
    np.savez_compressed(p_out, **out)
    print(f"  saved {p_out} ({os.path.getsize(p_out)/1e3:.1f} KB)", flush=True)


def build_kerr_cluster_data():
    print("Building physics_kerr_cluster.npz ...", flush=True)
    m12_dir = os.path.join(SCRATCH, "runs", "repro_wave4a", "m1_m2")
    m3_dir = os.path.join(SCRATCH, "runs", "repro_wave4a", "m3")
    m4_dir = os.path.join(SCRATCH, "runs", "repro_wave4a", "m4")

    out = {}
    for lbl in ("cks_gl4", "cks_mid", "lat_gl4", "lat_mid"):
        arr = read_traj(os.path.join(m12_dir, lbl, f"{lbl}.traj.bin"))
        E, Lz, Q = _kerr.invariants("cks", arr[:, 2:5], arr[:, 5:8], a=0.9, M=1.0)
        out[f"{lbl}_t"] = arr[:, 0]
        out[f"{lbl}_xy"] = arr[:, 2:4].astype(np.float32)
        out[f"{lbl}_dE"] = np.abs(E - E[0]) / abs(E[0])
        out[f"{lbl}_dQ"] = np.abs(Q - Q[0]) / abs(Q[0])

    # Dynamic Z4c head-on binary merger + tracers
    for tag, run in (("gl4", "punc_headon_gl4"), ("mid", "punc_headon_mid")):
        rdir = os.path.join(m3_dir, run)
        if tag == "gl4":
            co0 = np.loadtxt(os.path.join(rdir, f"{run}.co_0.txt"))
            co1 = np.loadtxt(os.path.join(rdir, f"{run}.co_1.txt"))
            out["ho_co_t"] = co0[::16, 1]
            out["ho_co0_x"] = co0[::16, 2:5].astype(np.float32)
            out["ho_co1_x"] = co1[::16, 2:5].astype(np.float32)
            ah0 = np.loadtxt(os.path.join(rdir, f"{run}.horizon_summary_0.txt"))
            ok = np.isfinite(ah0[:, 2])
            out["ho_ah_t"] = ah0[ok, 1]
            out["ho_ah_M"] = ah0[ok, 2]
            out["ho_ah_r0"] = np.float64(ah0[ok, 10][0])
            out["ho_ah_rfin"] = np.float64(ah0[ok, 10][-1])

        tr = read_traj(os.path.join(rdir, f"{run}.traj.bin"))
        for k in range(6):
            sub = tr[tr[:, 1] == k]
            if tag == "gl4":
                out[f"ho_tr{k}_t"] = sub[:, 0]
                out[f"ho_tr{k}_x"] = sub[:, 2:5].astype(np.float32)
            Lx = sub[:, 3] * sub[:, 7] - sub[:, 4] * sub[:, 6]
            denom = abs(Lx[0]) if abs(Lx[0]) > 1.0 else 1.0
            out[f"ho_{tag}_tr{k}_t"] = sub[:, 0]
            out[f"ho_{tag}_tr{k}_dLx"] = np.abs(Lx - Lx[0]) / denom

    # M4 N=10^5 6-level SMR cluster phase-mixing & invariant CDFs
    d0 = read_grlbv(os.path.join(m4_dir, "m4_mesh_100k_gl4", "m4_mesh_100k_gl4.vlasov.00000.bin"))
    d1 = read_grlbv(os.path.join(m4_dir, "m4_mesh_100k_gl4", "m4_mesh_100k_gl4.vlasov.00001.bin"))
    # Subsample 35,000 points cleanly for sharp rasterized scatter while keeping exact CDFs across all 10^5
    rng = np.random.default_rng(42)
    idx_vis = rng.choice(len(d0["x"]), size=35000, replace=False)
    out["m4_xy_t0"] = d0["x"][idx_vis, :2].astype(np.float32)
    out["m4_xy_t200"] = d1["x"][idx_vis, :2].astype(np.float32)

    qgrid = np.linspace(0.01, 0.99, 99)
    out["cdf_q"] = qgrid
    for lbl in ("ana_100k_mid", "ana_100k_gl4", "mesh_100k_mid", "mesh_100k_gl4"):
        rdir = os.path.join(m4_dir, f"m4_{lbl}")
        vfiles = sorted(glob.glob(os.path.join(rdir, "*.vlasov.*.bin")))
        pfiles = sorted(glob.glob(os.path.join(rdir, "*.part.*.bin")))
        if vfiles:
            s0 = read_grlbv(vfiles[0])
            s1 = read_grlbv(vfiles[-1])
            x0, u0 = s0["x"], s0["u_bar"][:, 0, :]
            x1, u1 = s1["x"], s1["u_bar"][:, 0, :]
        else:
            # reuse common snapshot reader
            from diag.common import read_snapshot
            _, s0_d, tg0, _ = read_snapshot(pfiles[0])
            _, s1_d, tg1, _ = read_snapshot(pfiles[-1])
            m0 = {int(t): i for i, t in enumerate(tg0)}
            idx = np.array([m0[int(t)] for t in tg1])
            x0, u0 = s0_d[idx, 0:3], s0_d[idx, 3:6]
            x1, u1 = s1_d[:, 0:3], s1_d[:, 3:6]
        E0, L0, Q0 = _kerr.invariants("cks", x0, u0, a=0.9, M=1.0)
        E1, L1, Q1 = _kerr.invariants("cks", x1, u1, a=0.9, M=1.0)
        dE = np.abs(E1 - E0) / np.abs(E0)
        K0 = Q0 + (L0 - 0.9 * E0) ** 2
        dQK = np.abs(Q1 - Q0) / K0
        out[f"cdf_{lbl}_dE"] = np.quantile(dE, qgrid)
        out[f"cdf_{lbl}_dQK"] = np.quantile(dQK, qgrid)

    p_out = os.path.join(DATA_DIR, "physics_kerr_cluster.npz")
    np.savez_compressed(p_out, **out)
    print(f"  saved {p_out} ({os.path.getsize(p_out)/1e3:.1f} KB)", flush=True)


def build_st_data():
    print("Building physics_st_phase.npz ...", flush=True)
    m5c = os.path.join(SCRATCH, "runs", "repro_wave4b", "m5c")
    out = {}

    # 4 radial phase-space portraits (r, u_r)
    portraits = [
        ("ps0", "st_yc0819_vp01_10k_anti", "00000"),
        ("ps1", "st_yc0819_vp01_10k_anti", "00006"),
        ("ps2", "st_yc0605_vp01_10k_hyb", "00001"),
        ("ps3", "st_yc0605_vp01_10k_hyb", "00002"),
    ]
    for key, run, idx in portraits:
        d = read_grlbv(os.path.join(m5c, run, f"{run}.vlasov.{idx}.bin"))
        x, u = d["x"], d["u_bar"][:, 0, :]
        r = np.linalg.norm(x, axis=1)
        ur = np.sum(x * u, axis=1) / np.maximum(r, 1e-12)
        out[f"{key}_t"] = np.float64(d["time"])
        out[f"{key}_r"] = r.astype(np.float32)
        out[f"{key}_ur"] = ur.astype(np.float32)

    runs = [
        "st_yc0900_vp01_10k_hyb",
        "st_yc0819_vp01_10k_anti",
        "st_yc0819_vp01_10k_mid",
        "st_yc0756_dp10_10k_hyb",
        "st_yc0756_dp10_10k_mid",
        "st_yc0605_vp01_10k_hyb",
        "st_yc0605_vp01_10k_mid",
    ]
    for r in runs:
        rd = os.path.join(m5c, r)
        nh = read_col_hst(os.path.join(rd, f"{r}.nrpic.hst"))
        out[f"{r}_t"] = nh["time"]
        out[f"{r}_amin"] = nh["alpha_min"]
        P = np.sqrt(nh["sum_mux"] ** 2 + nh["sum_muy"] ** 2 + nh["sum_muz"] ** 2) / nh["sum_m"][0]
        out[f"{r}_P"] = P
        ah_p = os.path.join(rd, f"{r}.horizon_summary_0.txt")
        if os.path.isfile(ah_p):
            ah = np.loadtxt(ah_p)
            if ah.ndim == 1:
                ah = ah[None, :]
            ok = np.isfinite(ah[:, 2])
            if np.any(ok):
                out[f"{r}_ah_t"] = ah[ok, 1]
                out[f"{r}_ah_M"] = ah[ok, 2]
                out[f"{r}_ah_a"] = ah[ok, 6] / (ah[ok, 2] ** 2)

    p_out = os.path.join(DATA_DIR, "physics_st_phase.npz")
    np.savez_compressed(p_out, **out)
    print(f"  saved {p_out} ({os.path.getsize(p_out)/1e3:.1f} KB)", flush=True)


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    build_prolate_data()
    build_kerr_cluster_data()
    build_st_data()
