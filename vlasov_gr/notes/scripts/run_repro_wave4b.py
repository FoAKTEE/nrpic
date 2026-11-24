#!/usr/bin/env python3
"""Phase 4 Wave 4B: Reproduce Wu & Most (2026) M5a-M5c Benchmarks at N=10^4 and N=10^5:
  M5a: Oppenheimer-Snyder R0=5M Z4c+AMR collapse (N~1e4 & N~1e5; lattice & qmc_octant)
  M5b: Prolate Spheroid e=0.9, b=10M Z4c+AMR collapse (N=1e4 & N=1e5; mc vs qmc_octant)
  M5c: Shapiro-Teukolsky relativistic cluster sequence (yc in {0.900, 0.819, 0.756, 0.605, 0.500, 0.283}
       plus unperturbed yc=0.500 migration) at N=1e4 and key regimes yc in {0.819, 0.500, 0.283} at N=1e5
       (stratified + midpoint vs qmc_lebedev + vlasov_hybrid[gl4+quadratic+filter_densitized]).

Always sets <fastflow> metric_drvts = interpolant and caches completed runs by log check.
Saves reduced metrics to `vlasov_gr/paper/data/repro_wave4b.npz`.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time as pytime

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrpic import io as nio  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "repro_wave4b")
IC_BASE = os.path.join(RUN_BASE, "ic")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "repro_wave4b.npz")


def clean_dir(path: str):
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
        except OSError:
            stale = f"{path}_stale_{int(pytime.time() * 1e6)}"
            try:
                os.rename(path, stale)
                shutil.rmtree(stale, ignore_errors=True)
            except OSError:
                shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path, exist_ok=True)


def patch_athinput(src_path: str, dst_path: str, updates: dict, existing_only: dict = None):
    """Parse an AthenaK .athinput by <section> blocks, updating/inserting requested keys."""
    existing_only = existing_only or {}
    with open(src_path, "r") as f:
        lines = f.readlines()

    sections = []
    cur_name = "__header__"
    cur_lines = []
    for ln in lines:
        hdr = ln.split("#")[0].strip()
        m = re.match(r"^<([A-Za-z0-9_]+)>$", hdr)
        if m:
            sections.append([cur_name, cur_lines])
            cur_name = m.group(1)
            cur_lines = [ln]
        else:
            cur_lines.append(ln)
    sections.append([cur_name, cur_lines])
    sec_map = {name: i for i, (name, _) in enumerate(sections)}

    merged = dict(updates)
    for sec, kv in existing_only.items():
        if sec in sec_map:
            merged[sec] = kv

    for sec, kv in merged.items():
        if sec not in sec_map:
            sections.append([sec, [f"\n<{sec}>\n"]])
            sec_map[sec] = len(sections) - 1
        idx = sec_map[sec]
        body = sections[idx][1]
        seen = set()
        new_body = [body[0]]
        for ln in body[1:]:
            code = ln.split("#", 1)[0]
            km = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", code)
            if km and km.group(1) in kv:
                key = km.group(1)
                seen.add(key)
                new_body.append(f"{key} = {kv[key]}\n")
                continue
            new_body.append(ln)
        for key, val in kv.items():
            if key not in seen:
                new_body.append(f"{key} = {val}\n")
        sections[idx][1] = new_body

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w") as f:
        for _, slines in sections:
            f.writelines(slines)


def run_athena(cfg: str, rdir: str, label: str, timeout_s: float = 2400.0):
    log_path = os.path.join(rdir, f"{label}.stdout.log")
    if os.path.isfile(log_path):
        txt = open(log_path, "r").read()
        if "Terminating on time limit" in txt:
            m_comp = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
            comp_s = float(m_comp.group(1)) if m_comp else np.nan
            m_w = re.search(r"# wall_s = ([0-9.eE+-]+)", txt)
            wall_s = float(m_w.group(1)) if m_w else comp_s
            return wall_s, comp_s
    clean_dir(rdir)
    t0 = pytime.perf_counter()
    res = subprocess.run(
        [GPU_BIN, "-i", cfg, "-d", rdir], capture_output=True, text=True, timeout=timeout_s
    )
    wall_s = pytime.perf_counter() - t0
    with open(log_path, "w") as f:
        f.write(res.stdout)
        f.write(f"\n# wall_s = {wall_s:.6f}\n")
        if res.stderr:
            f.write("\n=== STDERR ===\n" + res.stderr)
    if res.returncode != 0:
        raise RuntimeError(
            f"AthenaK failed ({label}, rc={res.returncode}):\n"
            f"{res.stdout[-1500:]}\n{res.stderr[-800:]}"
        )
    m_comp = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", res.stdout)
    comp_s = float(m_comp.group(1)) if m_comp else wall_s
    return wall_s, comp_s


def gen_ic(subcmd: str, prefix: str, extra_args: list):
    out_dir = os.path.join(IC_BASE, subcmd)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, f"{prefix}.json")
    nrp_path = os.path.join(out_dir, f"{prefix}.nrp")
    if not (os.path.isfile(json_path) and os.path.isfile(nrp_path)):
        cmd = [
            sys.executable, os.path.join(REPO, "problems/ic/make_ic.py"),
            subcmd, "--out", out_dir, "--prefix", prefix,
        ] + extra_args
        subprocess.run(cmd, check=True)
    meta = json.load(open(json_path))
    tab_rel = meta.get("table_file", "") or meta.get("athenak", {}).get("problem", {}).get("comp0_file", "")
    tab_abs = os.path.join(out_dir, tab_rel) if tab_rel else ""
    if "particles" in meta and isinstance(meta["particles"], dict) and "N" in meta["particles"]:
        n_part = int(meta["particles"]["N"])
    else:
        n_part = int(meta.get("N", len(nio.read_nrp(nrp_path)[2])))
    meta["N_eff"] = n_part
    return nrp_path, tab_abs, meta


def read_last_coords(rdir: str, basename: str):
    vfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.vlasov.*.bin")))
    pfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.part.*.bin")))
    if vfiles:
        s0 = vg.read_grlbv(vfiles[0])
        s1 = vg.read_grlbv(vfiles[-1])
        return (s0["x"], s0["m"][:, 0]), (s1["x"], s1["m"][:, 0])
    _, d0, _, _ = s4a.read_nrp_snapshot(pfiles[0])
    _, d1, _, _ = s4a.read_nrp_snapshot(pfiles[-1])
    return (d0[:, 0:3], d0[:, 6]), (d1[:, 0:3], d1[:, 6])


def extract_common_metrics(rdir: str, lbl: str, is_vlasov: bool):
    z4c = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
    nrp = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
    ahp = os.path.join(rdir, f"{lbl}.horizon_summary_0.txt")
    ah = s4a.read_horizon(ahp) if os.path.isfile(ahp) else np.zeros((0, 12))
    if len(ah):
        ah = ah[np.isfinite(ah[:, 1])]

    H_l2 = np.sqrt(np.maximum(z4c["H-norm2"], 0.0))
    M_l2 = np.sqrt(np.maximum(z4c["M-norm2"], 0.0))
    t_ah = float(ah[0, 0]) if len(ah) else np.nan
    M_ah = float(ah[-1, 1]) if len(ah) else np.nan

    if np.any(np.abs(nrp["int_E"]) > 0.0):
        rel_filt = np.abs(nrp["int_E_filtered"] - nrp["int_E"]) / np.maximum(np.abs(nrp["int_E"]), 1e-30)
        filt_t0 = float((nrp["int_E_filtered"][0] - nrp["int_E"][0]) / nrp["int_E"][0])
        filt_max = float(np.max(rel_filt))
    else:
        filt_t0 = filt_max = np.nan

    vlv = {}
    if is_vlasov and os.path.isfile(os.path.join(rdir, f"{lbl}.vlasov.hst")):
        vlv = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.vlasov.hst"))
    m_arr = vlv["m_tot"] if vlv else nrp["sum_m"]
    exc_arr = vlv["m_excised"] if vlv else nrp["m_excised"]
    t_arr = vlv["time"] if vlv else nrp["time"]
    exc_frac = exc_arr / max(float(m_arr[0]), 1e-30)
    idx_e99 = np.nonzero(exc_frac > 0.99)[0]
    t_exc99 = float(t_arr[idx_e99[0]]) if len(idx_e99) else np.nan

    return dict(
        z4c=z4c, nrp=nrp, vlv=vlv, ah=ah,
        H_l2=H_l2, M_l2=M_l2,
        H0=float(H_l2[0]), H_max=float(np.max(H_l2)), M_max=float(np.max(M_l2)),
        t_ah=t_ah, M_ah=M_ah, t_exc99=t_exc99,
        exc_end=float(exc_frac[-1]),
        alp_min=float(np.min(nrp["alpha_probe"])),
        alp_end=float(nrp["alpha_probe"][-1]),
        nmb_max=int(np.max(nrp["nmb"])),
        filt_t0=filt_t0, filt_max=filt_max,
    )


def build_particle_cfg(mode: str, ic_nrp: str, tab_abs: str, hist_dcycle: int, snap_dt: float,
                       extra_part: dict = None):
    p_upd = {
        "particle_file": ic_nrp,
        "hist_dcycle": str(hist_dcycle),
        "snap_dt": f"{snap_dt:.6g}",
    }
    if mode == "mid":
        p_upd["pusher"] = "midpoint"
        p_upd["filter_densitized"] = "false"
    else:
        p_upd["pusher"] = "vlasov_hybrid"
        p_upd["vlasov_mode"] = "hybrid"
        p_upd["vlasov_pusher"] = "gl4"
        p_upd["vlasov_time_interp"] = "quadratic"
        p_upd["filter_densitized"] = "true"
    if extra_part:
        p_upd.update(extra_part)
    prob = {"comp0_file": tab_abs} if tab_abs else {}
    return p_upd, prob


# ============================================================================
# M5a: Oppenheimer-Snyder R0=5M Collapse
# ============================================================================

def run_m5a(out: dict):
    print("\n=== M5a: Oppenheimer-Snyder R0=5M Collapse (N~1e4 & N~1e5) ===", flush=True)
    tpl = os.path.join(REPO, "problems/os/os_amr.athinput")
    m5a_dir = os.path.join(RUN_BASE, "m5a")
    os.makedirs(m5a_dir, exist_ok=True)
    E0 = _osn.rho0(5.0, 1.0)

    specs = [
        ("os_10k_lat_mid", "mid", ["--sampler", "lattice", "--nlat", "26", "--lattice-surface-correction"]),
        ("os_10k_lat_hyb", "hyb", ["--sampler", "lattice", "--nlat", "26", "--lattice-surface-correction"]),
        ("os_10k_qmc_hyb", "hyb", ["--sampler", "qmc_octant", "--N", "10000", "--seed", "1"]),
        ("os_100k_lat_mid", "mid", ["--sampler", "lattice", "--nlat", "58", "--lattice-surface-correction"]),
        ("os_100k_qmc_hyb", "hyb", ["--sampler", "qmc_octant", "--N", "100000", "--seed", "1"]),
    ]

    for lbl, mode, ic_args in specs:
        nrp, tab, meta = gen_ic("os", f"ic_{lbl}", ["--R0", "5.0"] + ic_args)
        p_upd, prob = build_particle_cfg(mode, nrp, tab, hist_dcycle=4, snap_dt=5.0)
        cfg = os.path.join(m5a_dir, f"{lbl}.athinput")
        rdir = os.path.join(m5a_dir, lbl)
        patch_athinput(
            tpl, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"max_nmb_per_rank": "2048"},
                "time": {"tlim": "25.0", "ndiag": "100"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "16"},
                "particles": p_upd,
                "problem": prob,
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s = run_athena(cfg, rdir, lbl, timeout_s=2400.0)
        m = extract_common_metrics(rdir, lbl, mode == "hyb")
        nrp_h = m["nrp"]
        tau = nrp_h["tau_probe"]
        mask_p = (tau > 0.0) & (tau <= 2.6) & (nrp_h["E_probe"] > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask_p]]) / E0
        max_rho_err = float(np.max(np.abs(nrp_h["E_probe"][mask_p] / E0 - rho_cyc) / rho_cyc)) if np.any(mask_p) else np.nan
        print(
            f"  [M5a {lbl:16s} N={meta['N_eff']:6d}] wall={wall_s:6.1f}s comp={comp_s:6.1f}s "
            f"rho_err={max_rho_err:.2e} t_AH={m['t_ah']:.2f}M M_AH={m['M_ah']:.5f}M "
            f"t_exc99={m['t_exc99']:.2f}M ||H||_max={m['H_max']:.3e} filt(t0/max)=({m['filt_t0']:.2e}/{m['filt_max']:.2e})",
            flush=True,
        )
        for k, v in dict(
            N=meta["N_eff"], wall=wall_s, comp=comp_s, rho_err=max_rho_err,
            t_AH=m["t_ah"], M_AH=m["M_ah"], t_exc99=m["t_exc99"],
            H0=m["H0"], H_max=m["H_max"], M_max=m["M_max"],
            filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        ).items():
            out[f"m5a_{lbl}_{k}"] = float(v)


# ============================================================================
# M5b: Prolate Spheroid e=0.9, b=10M Collapse
# ============================================================================

def run_m5b(out: dict):
    print("\n=== M5b: Prolate Spheroid e=0.9, b=10M Collapse (N=1e4 & N=1e5) ===", flush=True)
    tpl = os.path.join(REPO, "problems/prolate/prolate_amr.athinput")
    m5b_dir = os.path.join(RUN_BASE, "m5b")
    os.makedirs(m5b_dir, exist_ok=True)

    specs = [
        ("prol_10k_mc_mid", "mid", ["--N", "10000", "--sampler", "mc", "--seed", "1"]),
        ("prol_10k_qmc_hyb", "hyb", ["--N", "10000", "--sampler", "qmc_octant", "--seed", "1"]),
        ("prol_100k_mc_mid", "mid", ["--N", "100000", "--sampler", "mc", "--seed", "1"]),
        ("prol_100k_qmc_hyb", "hyb", ["--N", "100000", "--sampler", "qmc_octant", "--seed", "1"]),
    ]

    for lbl, mode, ic_args in specs:
        nrp, _, meta = gen_ic("prolate", f"ic_{lbl}", ["--e", "0.9", "--b", "10.0"] + ic_args)
        p_upd, _ = build_particle_cfg(
            mode, nrp, "", hist_dcycle=4, snap_dt=15.0,
            extra_part={
                "nfilter": "4",
                "filter_compensate": "true",
                "filter_comp_c": "-1.0",
            },
        )
        cfg = os.path.join(m5b_dir, f"{lbl}.athinput")
        rdir = os.path.join(m5b_dir, lbl)
        patch_athinput(
            tpl, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"num_levels": "7", "max_nmb_per_rank": "3072"},
                "time": {"tlim": "45.0", "ndiag": "100"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "32"},
                "particles": p_upd,
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s = run_athena(cfg, rdir, lbl, timeout_s=2400.0)
        m = extract_common_metrics(rdir, lbl, mode == "hyb")
        (x0, m0), _ = read_last_coords(rdir, lbl)
        com0 = float(np.linalg.norm(np.sum(m0[:, None] * x0, axis=0) / np.sum(m0)))
        Qxx0 = float(np.sum(m0 * x0[:, 0] ** 2))
        Qyy0 = float(np.sum(m0 * x0[:, 1] ** 2))
        q_asym0 = abs(Qxx0 - Qyy0) / max(Qxx0 + Qyy0, 1e-30)
        print(
            f"  [M5b {lbl:17s} N={meta['N_eff']:6d}] wall={wall_s:6.1f}s comp={comp_s:6.1f}s "
            f"|COM0|={com0:.2e} q_xy0={q_asym0:.2e} t_AH={m['t_ah']:.2f}M M_AH={m['M_ah']:.5f}M "
            f"||H||_0={m['H0']:.3e} ||H||_max={m['H_max']:.3e} filt_t0={m['filt_t0']:.2e}",
            flush=True,
        )
        for k, v in dict(
            N=meta["N_eff"], wall=wall_s, comp=comp_s, com0=com0, q_asym0=q_asym0,
            t_AH=m["t_ah"], M_AH=m["M_ah"], t_exc99=m["t_exc99"],
            H0=m["H0"], H_max=m["H_max"], M_max=m["M_max"],
            filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        ).items():
            out[f"m5b_{lbl}_{k}"] = float(v)


# ============================================================================
# M5c: Shapiro-Teukolsky Cluster Sequence & Migration
# ============================================================================

def run_m5c(out: dict):
    print("\n=== M5c: Shapiro-Teukolsky Sequence (N=1e4 & Key Regimes at N=1e5) ===", flush=True)
    tpl_static = os.path.join(REPO, "problems/st/st_cluster.athinput")
    tpl_amr = os.path.join(REPO, "problems/st/st_cluster_amr.athinput")
    m5c_dir = os.path.join(RUN_BASE, "m5c")
    os.makedirs(m5c_dir, exist_ok=True)

    # (lbl, yc, N, vpert, dpert, use_amr, tlim, mode, samp, ic_prefix)
    run_specs = [
        ("st_yc0900_vp01_10k_mid",  0.900, 10000,  0.01, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0900_vp01_10k_mid"),
        ("st_yc0900_vp01_10k_hyb",  0.900, 10000,  0.01, 0.00, False, 300.0, "hyb", "qmc_lebedev",   "ic_st_yc0900_vp01_10k_hyb"),
        ("st_yc0819_vp01_10k_mid",  0.819, 10000,  0.01, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0819_vp01_10k_mid"),
        ("st_yc0819_vp01_10k_anti", 0.819, 10000,  0.01, 0.00, False, 300.0, "hyb", "qmc_antipodal", "ic_st_yc0819_vp01_10k_anti_anti"),
        ("st_yc0819_vp01_10k_hyb",  0.819, 10000,  0.01, 0.00, False, 300.0, "hyb", "qmc_lebedev",   "ic_st_yc0819_vp01_10k_hyb"),
        ("st_yc0756_dp10_10k_mid",  0.756, 10000,  0.00, 0.10, True,  175.0, "mid", "stratified",    "ic_st_yc0756_dp10_10k_mid"),
        ("st_yc0756_dp10_10k_hyb",  0.756, 10000,  0.00, 0.10, True,  175.0, "hyb", "qmc_lebedev",   "ic_st_yc0756_dp10_10k_hyb"),
        ("st_yc0605_vp01_10k_mid",  0.605, 10000,  0.01, 0.00, True,  250.0, "mid", "stratified",    "ic_st_yc0605_vp01_10k_mid"),
        ("st_yc0605_vp01_10k_hyb",  0.605, 10000,  0.01, 0.00, True,  250.0, "hyb", "qmc_antipodal", "ic_st_yc0605_vp01_10k_hyb_anti"),
        ("st_yc0500_vp01_10k_mid",  0.500, 10000,  0.01, 0.00, True,  150.0, "mid", "stratified",    "ic_st_yc0500_vp01_10k_mid"),
        ("st_yc0500_vp01_10k_hyb",  0.500, 10000,  0.01, 0.00, True,  150.0, "hyb", "qmc_antipodal", "ic_st_yc0500_vp01_10k_hyb_anti"),
        ("st_yc0283_vp01_10k_mid",  0.283, 10000,  0.01, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0283_vp01_10k_mid"),
        ("st_yc0283_vp01_10k_hyb",  0.283, 10000,  0.01, 0.00, False, 300.0, "hyb", "qmc_antipodal", "ic_st_yc0283_vp01_10k_hyb_anti"),
        ("st_yc0500_mig_10k_mid",   0.500, 10000,  0.00, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0500_mig_10k_mid"),
        ("st_yc0500_mig_10k_hyb",   0.500, 10000,  0.00, 0.00, False, 300.0, "hyb", "qmc_antipodal", "ic_st_yc0500_mig_10k_hyb_anti"),
        ("st_yc0819_vp01_100k_mid", 0.819, 100000, 0.01, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0819_vp01_100k_mid"),
        ("st_yc0819_vp01_100k_hyb", 0.819, 100000, 0.01, 0.00, False, 300.0, "hyb", "qmc_lebedev",   "ic_st_yc0819_vp01_100k_hyb"),
        ("st_yc0500_vp01_100k_mid", 0.500, 100000, 0.01, 0.00, True,  150.0, "mid", "stratified",    "ic_st_yc0500_vp01_100k_mid"),
        ("st_yc0500_vp01_100k_hyb", 0.500, 100000, 0.01, 0.00, True,  150.0, "hyb", "qmc_lebedev",   "ic_st_yc0500_vp01_100k_hyb"),
        ("st_yc0283_vp01_100k_mid", 0.283, 100000, 0.01, 0.00, False, 300.0, "mid", "stratified",    "ic_st_yc0283_vp01_100k_mid"),
        ("st_yc0283_vp01_100k_hyb", 0.283, 100000, 0.01, 0.00, False, 300.0, "hyb", "qmc_lebedev",   "ic_st_yc0283_vp01_100k_hyb"),
    ]

    for lbl, yc, N, vp, dp, use_amr, tlim, mode, samp, ic_prefix in run_specs:
        ic_args = ["--yc", f"{yc:.6g}", "--N", str(N), "--sampler", samp, "--seed", "1", "--consistent-table"]
        if vp > 0.0:
            ic_args += ["--vpert", f"{vp:.6g}"]
        if dp > 0.0:
            ic_args += ["--dpert", f"{dp:.6g}"]
        if samp == "qmc_lebedev":
            ic_args += ["--lebedev-q", "14"]
        nrp, tab, meta = gen_ic("st", ic_prefix, ic_args)

        p_upd, prob = build_particle_cfg(mode, nrp, tab, hist_dcycle=20, snap_dt=50.0)
        tpl = tpl_amr if use_amr else tpl_static
        cfg = os.path.join(m5c_dir, f"{lbl}.athinput")
        rdir = os.path.join(m5c_dir, lbl)
        upd = {
            "job": {"basename": lbl},
            "time": {"tlim": f"{tlim:.6g}", "ndiag": "500"},
            "particles": p_upd,
            "problem": prob,
        }
        if use_amr:
            upd["mesh_refinement"] = {"max_nmb_per_rank": "3072"}
            upd["fastflow"] = {"metric_drvts": "interpolant", "find_every": "32"}
        patch_athinput(
            tpl, cfg, upd,
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s = run_athena(cfg, rdir, lbl, timeout_s=2400.0)
        m = extract_common_metrics(rdir, lbl, mode == "hyb")
        (x0, m0), (x1, m1) = read_last_coords(rdir, lbl)
        com0 = float(np.linalg.norm(np.sum(m0[:, None] * x0, axis=0) / np.sum(m0)))
        com1 = float(np.linalg.norm(np.sum(m1[:, None] * x1, axis=0) / np.sum(m1))) if len(m1) else np.nan
        r50_0 = float(np.median(np.linalg.norm(x0, axis=1)))
        r50_1 = float(np.median(np.linalg.norm(x1, axis=1))) if len(x1) else np.nan
        print(
            f"  [M5c {lbl:24s} N={meta['N_eff']:6d}] wall={wall_s:6.1f}s comp={comp_s:6.1f}s "
            f"alp(min/end)=({m['alp_min']:.3f}/{m['alp_end']:.3f}) t_AH={m['t_ah']:.2f}M M_AH={m['M_ah']:.4f}M "
            f"r50=({r50_0:.2f}->{r50_1:.2f}) |COM|=({com0:.2e}->{com1:.2e}) ||H||_0={m['H0']:.2e} nmb_max={m['nmb_max']}",
            flush=True,
        )
        for k, v in dict(
            N=meta["N_eff"], yc=yc, wall=wall_s, comp=comp_s,
            alp_min=m["alp_min"], alp_end=m["alp_end"],
            t_AH=m["t_ah"], M_AH=m["M_ah"], exc_end=m["exc_end"],
            H0=m["H0"], H_max=m["H_max"], M_max=m["M_max"],
            com0=com0, com1=com1, r50_0=r50_0, r50_1=r50_1,
            nmb_max=m["nmb_max"], filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        ).items():
            out[f"m5c_{lbl}_{k}"] = float(v)


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    out = {}
    run_m5a(out)
    run_m5b(out)
    run_m5c(out)
    np.savez(OUT_NPZ, **out)
    print(f"\nSaved Wave 4B reduced data: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
