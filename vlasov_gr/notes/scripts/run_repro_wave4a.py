#!/usr/bin/env python3
"""Phase 4 Wave 4A: Reproduce Wu & Most (2026) M1-M4 Benchmarks at N=10^4 and N=10^5:
  M1-M2: Kerr a=0.9M e=0.99 geodesics (analytic spherical KS, CKS, Hermite lattice dx=0.025M)
         and inclined BL orbit on 3D mesh (dx=0.25M, t=600M): midpoint vs vlasov_hybrid + gl4
  M3:    Dynamic Z4c Schwarzschild puncture tracers (t=250M) and binary head-on merger tracers
         (t=200M, AMR, metric_drvts=interpolant): midpoint vs vlasov_hybrid + gl4 + quadratic
  M4:    6-level SMR Kerr a=0.9M test-particle clusters at N=10^4 and N=10^5 (analytic & mesh):
         midpoint (filter_densitized=false) vs vlasov_hybrid (gl4 + filter_densitized=true)

Saves reduced metrics to `vlasov_gr/paper/data/repro_wave4a.npz`.
"""

import glob
import json
import math
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
from nrpic import kerr as _kerr  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "repro_wave4a")
IC_BASE = os.path.join(RUN_BASE, "ic")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "repro_wave4a.npz")


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


def patch_athinput(src_path: str, dst_path: str, updates: dict, drop_keys: dict = None):
    """Parse an AthenaK .athinput by <section> blocks and update/insert keys deterministically."""
    drop_keys = drop_keys or {}
    with open(src_path, "r") as f:
        lines = f.readlines()

    sections = []
    cur_name = "__header__"
    cur_lines = []
    for ln in lines:
        m = re.match(r"^\s*<([A-Za-z0-9_]+)>\s*$", ln.strip() and ln.split("#")[0].strip())
        if m:
            sections.append([cur_name, cur_lines])
            cur_name = m.group(1)
            cur_lines = [ln]
        else:
            cur_lines.append(ln)
    sections.append([cur_name, cur_lines])

    sec_map = {name: i for i, (name, _) in enumerate(sections)}

    for sec, kv in updates.items():
        if sec not in sec_map:
            sections.append([sec, [f"\n<{sec}>\n"]])
            sec_map[sec] = len(sections) - 1
        idx = sec_map[sec]
        body = sections[idx][1]
        drops = set(drop_keys.get(sec, ()))
        seen = set()
        new_body = [body[0]]
        for ln in body[1:]:
            code = ln.split("#", 1)[0]
            km = re.match(r"^\s*([A-Za-z0-9_]+)\s*=", code)
            if km:
                key = km.group(1)
                if key in drops:
                    continue
                if key in kv:
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


def run_athena(cfg: str, rdir: str, label: str, timeout_s: float = 1800.0):
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


def read_traj_bin(path: str):
    """Read <basename>.traj.bin: records of 8 float64 (time, tag, x1, x2, x3, u1, u2, u3)."""
    arr = np.fromfile(path, dtype=np.float64).reshape(-1, 8)
    by_tag = {}
    for tg in np.unique(arr[:, 1].astype(np.int64)):
        sub = arr[arr[:, 1].astype(np.int64) == tg]
        by_tag[int(tg)] = dict(t=sub[:, 0], x=sub[:, 2:5], u=sub[:, 5:8])
    return by_tag


def read_particle_state(rdir: str, basename: str):
    """Read first and last particle snapshot (.vlasov.*.bin or .part.*.bin), returning tags if available."""
    vfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.vlasov.*.bin")))
    pfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.part.*.bin")))
    out = []
    if vfiles:
        for fn in (vfiles[0], vfiles[-1]):
            sn = vg.read_grlbv(fn)
            n = len(sn["x"])
            out.append((sn["time"], sn["x"], sn["u_bar"][:, 0, :], sn["m"][:, 0], np.arange(n, dtype=np.int64)))
    elif pfiles:
        for fn in (pfiles[0], pfiles[-1]):
            t, d, tag, _ = s4a.read_nrp_snapshot(fn)
            out.append((t, d[:, 0:3], d[:, 3:6], d[:, 6], tag.astype(np.int64)))
    else:
        raise FileNotFoundError(f"No snapshots found in {rdir} for {basename}")
    return out[0], out[1]


# ============================================================================
# M1-M2: Kerr a=0.9M Geodesic & Mesh Geodesic
# ============================================================================

def run_m1_m2(out: dict):
    print("\n=== M1-M2: Kerr a=0.9M Geodesics (e=0.99 & Mesh Inclined) ===", flush=True)
    ic_json = json.load(open(os.path.join(REPO, "problems/kerr/ref/initial_conditions.json")))
    ksp = ic_json["orbits"]["ks_passage"]
    x_end_ks = np.asarray(ksp["final_state"]["ks"]["x"], dtype=np.float64)
    x_end_cks = np.asarray(ksp["final_state"]["cks"]["x"], dtype=np.float64)

    geo_tpl = os.path.join(REPO, "problems/kerr/geodesic.athinput")
    mesh_tpl = os.path.join(REPO, "problems/kerr/geodesic_mesh.athinput")
    m12_dir = os.path.join(RUN_BASE, "m1_m2")
    os.makedirs(m12_dir, exist_ok=True)

    passage_specs = [
        ("ks_mid", "kerr_schild_sph", "midpoint", "ks"),
        ("ks_gl4", "kerr_schild_sph", "vlasov_hybrid", "ks"),
        ("cks_mid", "kerr_schild", "midpoint", "cks"),
        ("cks_gl4", "kerr_schild", "vlasov_hybrid", "cks"),
        ("lat_mid", "lattice", "midpoint", "cks"),
        ("lat_gl4", "lattice", "vlasov_hybrid", "cks"),
    ]

    for lbl, met, push, sys_name in passage_specs:
        st = ksp["initial_state"][sys_name]
        p_upd = {
            "metric": met,
            "pusher": push,
            "lattice_dx": "0.025",
            "tolerance": "2.0e-14",
            "max_iterations": "200",
            "dt": "0.01",
            "hist_dcycle": "1000",
            "traj_dcycle": "20",
            "traj_ntrack": "1",
            "p0_x1": f"{st['x'][0]:.17g}",
            "p0_x2": f"{st['x'][1]:.17g}",
            "p0_x3": f"{st['x'][2]:.17g}",
            "p0_u1": f"{st['u'][0]:.17g}",
            "p0_u2": f"{st['u'][1]:.17g}",
            "p0_u3": f"{st['u'][2]:.17g}",
        }
        if push == "vlasov_hybrid":
            p_upd["vlasov_mode"] = "hybrid"
            p_upd["vlasov_pusher"] = "gl4"
        cfg = os.path.join(m12_dir, f"{lbl}.athinput")
        rdir = os.path.join(m12_dir, lbl)
        patch_athinput(geo_tpl, cfg, {"job": {"basename": lbl}, "particles": p_upd})
        wall_s, comp_s = run_athena(cfg, rdir, lbl)

        tr = read_traj_bin(os.path.join(rdir, f"{lbl}.traj.bin"))[0]
        E, Lz, Q = _kerr.invariants(sys_name, tr["x"], tr["u"], a=0.9, M=1.0)
        E0, Lz0, Q0 = float(E[0]), float(Lz[0]), float(Q[0])
        dE = float(np.max(np.abs(E - E0) / abs(E0)))
        dLz = float(np.max(np.abs(Lz - Lz0) / abs(Lz0)))
        dQ = float(np.max(np.abs(Q - Q0) / abs(Q0)))

        # Final position error vs exact quadrature state at t=230M
        if sys_name == "ks":
            x_fin = tr["x"][-1].copy()
            dphi = ((x_fin[2] - x_end_ks[2] + math.pi) % (2.0 * math.pi)) - math.pi
            pos_err = float(max(abs(x_fin[0] - x_end_ks[0]), abs(x_fin[1] - x_end_ks[1]), abs(dphi)))
        else:
            _, ks_num, _ = _kerr.convert_state(230.0, tr["x"][-1], tr["u"][-1], "cks", "ks", a=0.9, M=1.0)
            dphi = ((ks_num[2] - x_end_ks[2] + math.pi) % (2.0 * math.pi)) - math.pi
            pos_err = float(max(abs(ks_num[0] - x_end_ks[0]), abs(ks_num[1] - x_end_ks[1]), abs(dphi)))
            # Keep exact CKS L-inf distance as additional diagnostic
            out[f"m1_{lbl}_cks_err"] = float(np.max(np.abs(tr["x"][-1] - x_end_cks)))

        print(
            f"  [e=0.99] {lbl:8s}: wall={wall_s:5.2f}s comp={comp_s:5.2f}s "
            f"dE={dE:.3e} dLz={dLz:.3e} dQ={dQ:.3e} pos_err={pos_err:.3e}",
            flush=True,
        )
        for k, v in dict(wall=wall_s, comp=comp_s, dE=dE, dLz=dLz, dQ=dQ, pos_err=pos_err).items():
            out[f"m1_{lbl}_{k}"] = float(v)

    # M2: geodesic_mesh.athinput (dx=0.25M mesh, t=600M, inclined orbit)
    for lbl, push in (("geomesh_mid", "midpoint"), ("geomesh_gl4", "vlasov_hybrid")):
        p_upd = {
            "pusher": push,
            "hist_dcycle": "2000",
            "traj_dcycle": "200",
        }
        if push == "vlasov_hybrid":
            p_upd["vlasov_mode"] = "hybrid"
            p_upd["vlasov_pusher"] = "gl4"
        cfg = os.path.join(m12_dir, f"{lbl}.athinput")
        rdir = os.path.join(m12_dir, lbl)
        patch_athinput(mesh_tpl, cfg, {"job": {"basename": lbl}, "particles": p_upd})
        wall_s, comp_s = run_athena(cfg, rdir, lbl)
        tr = read_traj_bin(os.path.join(rdir, f"{lbl}.traj.bin"))[0]
        E, Lz, Q = _kerr.invariants("cks", tr["x"], tr["u"], a=0.9, M=1.0)
        dE = float(np.max(np.abs(E - E[0]) / abs(E[0])))
        dLz = float(np.max(np.abs(Lz - Lz[0]) / abs(Lz[0])))
        dQ = float(np.max(np.abs(Q - Q[0]) / abs(Q[0])))
        print(
            f"  [mesh600] {lbl:11s}: wall={wall_s:5.2f}s comp={comp_s:5.2f}s "
            f"dE={dE:.3e} dLz={dLz:.3e} dQ={dQ:.3e}",
            flush=True,
        )
        for k, v in dict(wall=wall_s, comp=comp_s, dE=dE, dLz=dLz, dQ=dQ).items():
            out[f"m2_{lbl}_{k}"] = float(v)


# ============================================================================
# M3: Dynamic Z4c Puncture Tracers (Single & Head-On Merger)
# ============================================================================

def run_m3(out: dict):
    print("\n=== M3: Dynamic Z4c Puncture Tracers & Head-On Merger ===", flush=True)
    m3_dir = os.path.join(RUN_BASE, "m3")
    os.makedirs(m3_dir, exist_ok=True)

    # Single Schwarzschild puncture (tlim=250M)
    tpl_s = os.path.join(REPO, "problems/puncture/tracers_single.athinput")
    tr_single = {}
    for push_lbl, push in (("mid", "midpoint"), ("gl4", "vlasov_hybrid")):
        lbl = f"punc_single_{push_lbl}"
        p_upd = {"pusher": push}
        if push == "vlasov_hybrid":
            p_upd["vlasov_mode"] = "hybrid"
            p_upd["vlasov_pusher"] = "gl4"
            p_upd["vlasov_time_interp"] = "quadratic"
        cfg = os.path.join(m3_dir, f"{lbl}.athinput")
        rdir = os.path.join(m3_dir, lbl)
        patch_athinput(
            tpl_s, cfg,
            {
                "job": {"basename": lbl},
                "fastflow": {"metric_drvts": "interpolant"},
                "particles": p_upd,
                "output2": {"dt": "1000.0"},
            },
        )
        wall_s, comp_s = run_athena(cfg, rdir, lbl)
        tr = read_traj_bin(os.path.join(rdir, f"{lbl}.traj.bin"))
        ah = s4a.read_horizon(os.path.join(rdir, f"{lbl}.horizon_summary_0.txt"))
        z4c = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
        tr_single[push_lbl] = tr

        # Axisymmetric Schwarzschild L = x u_y - y u_x (L_y/L_x/L_z norm) for circular tags 0..3
        l_drifts = []
        t_last = []
        for tg in range(6):
            x, u = tr[tg]["x"], tr[tg]["u"]
            Lx = x[:, 1] * u[:, 2] - x[:, 2] * u[:, 1]
            Ly = x[:, 2] * u[:, 0] - x[:, 0] * u[:, 2]
            Lz = x[:, 0] * u[:, 1] - x[:, 1] * u[:, 0]
            Lmag = np.sqrt(Lx * Lx + Ly * Ly + Lz * Lz)
            if tg <= 3:
                l_drifts.append(float(np.max(np.abs(Lmag - Lmag[0]) / max(Lmag[0], 1e-30))))
            t_last.append(float(tr[tg]["t"][-1]))

        M_ah_fin = float(ah[-1, 1]) if len(ah) else np.nan
        H_max = float(np.max(np.sqrt(np.maximum(z4c["H-norm2"], 0.0))))
        print(
            f"  [single] {lbl:16s}: wall={wall_s:6.2f}s comp={comp_s:6.2f}s "
            f"M_AH={M_ah_fin:.5f} ||H||_max={H_max:.3e} "
            f"circ |dL/L|={[round(v, 6) for v in l_drifts]} "
            f"t_plunge=({t_last[4]:.2f},{t_last[5]:.2f})",
            flush=True,
        )
        out[f"m3_{lbl}_wall"] = wall_s
        out[f"m3_{lbl}_comp"] = comp_s
        out[f"m3_{lbl}_M_AH"] = M_ah_fin
        out[f"m3_{lbl}_H_max"] = H_max
        out[f"m3_{lbl}_L_drift"] = np.array(l_drifts)
        out[f"m3_{lbl}_t_last"] = np.array(t_last)

    # Compare gl4 vs midpoint trajectories directly on common timestamps
    s_dx, s_du = [], []
    for tg in range(6):
        nmin = min(len(tr_single["mid"][tg]["t"]), len(tr_single["gl4"][tg]["t"]))
        s_dx.append(float(np.max(np.abs(tr_single["gl4"][tg]["x"][:nmin] - tr_single["mid"][tg]["x"][:nmin]))))
        s_du.append(float(np.max(np.abs(tr_single["gl4"][tg]["u"][:nmin] - tr_single["mid"][tg]["u"][:nmin]))))
    out["m3_single_gl4_vs_mid_dx"] = np.array(s_dx)
    out["m3_single_gl4_vs_mid_du"] = np.array(s_du)
    print(f"  [single] gl4 vs midpoint max|dx|={[round(v, 7) for v in s_dx]}", flush=True)

    # Head-on binary BH merger (tlim=100M: covers inspiral, merger ~42M, common AH & ringdown)
    tpl_h = os.path.join(REPO, "problems/puncture/tracers_headon.athinput")
    tr_head = {}
    for push_lbl, push in (("mid", "midpoint"), ("gl4", "vlasov_hybrid")):
        lbl = f"punc_headon_{push_lbl}"
        p_upd = {"pusher": push, "traj_dcycle": "16", "hist_dcycle": "40"}
        if push == "vlasov_hybrid":
            p_upd["vlasov_mode"] = "hybrid"
            p_upd["vlasov_pusher"] = "gl4"
            p_upd["vlasov_time_interp"] = "quadratic"
        cfg = os.path.join(m3_dir, f"{lbl}.athinput")
        rdir = os.path.join(m3_dir, lbl)
        patch_athinput(
            tpl_h, cfg,
            {
                "job": {"basename": lbl},
                "time": {"tlim": "100.0"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "32"},
                "particles": p_upd,
                "output2": {"dt": "1000.0"},
            },
        )
        wall_s, comp_s = run_athena(cfg, rdir, lbl, timeout_s=1800.0)
        tr = read_traj_bin(os.path.join(rdir, f"{lbl}.traj.bin"))
        z4c = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
        tr_head[push_lbl] = tr

        # Axisymmetry about x-axis: L_x = y u_z - z u_y for off-axis tracers 0..4 (tag 5 is on z-axis: L_x=0)
        lx_errs = []
        t_last = []
        for tg in range(6):
            x, u = tr[tg]["x"], tr[tg]["u"]
            Lx = x[:, 1] * u[:, 2] - x[:, 2] * u[:, 1]
            denom = abs(float(Lx[0])) if abs(float(Lx[0])) > 1.0 else 1.0
            lx_errs.append(float(np.max(np.abs(Lx - Lx[0]) / denom)))
            t_last.append(float(tr[tg]["t"][-1]))
        sym_x2 = float(np.max(np.abs(tr[2]["x"][:, 0])))
        ah_info = {}
        for hi in range(3):
            ahp = os.path.join(rdir, f"{lbl}.horizon_summary_{hi}.txt")
            if os.path.isfile(ahp):
                ah = s4a.read_horizon(ahp)
                if len(ah):
                    ah = ah[np.isfinite(ah[:, 1])]
                if len(ah):
                    ah_info[hi] = (float(ah[0, 0]), float(ah[-1, 1]))
        H_max = float(np.max(np.sqrt(np.maximum(z4c["H-norm2"], 0.0))))
        print(
            f"  [headon] {lbl:16s}: wall={wall_s:6.2f}s comp={comp_s:6.2f}s "
            f"||H||_max={H_max:.3e} sym_x(tag2)={sym_x2:.3e} "
            f"|dLx|={[round(v, 7) for v in lx_errs]} ah={ah_info}",
            flush=True,
        )
        out[f"m3_{lbl}_wall"] = wall_s
        out[f"m3_{lbl}_comp"] = comp_s
        out[f"m3_{lbl}_H_max"] = H_max
        out[f"m3_{lbl}_lx_err"] = np.array(lx_errs)
        out[f"m3_{lbl}_sym_x2"] = sym_x2
        out[f"m3_{lbl}_t_last"] = np.array(t_last)
        for hi, (t0_h, m_fin) in ah_info.items():
            out[f"m3_{lbl}_ah{hi}_t0"] = t0_h
            out[f"m3_{lbl}_ah{hi}_M"] = m_fin

    h_dx = []
    for tg in range(6):
        nmin = min(len(tr_head["mid"][tg]["t"]), len(tr_head["gl4"][tg]["t"]))
        h_dx.append(float(np.max(np.abs(tr_head["gl4"][tg]["x"][:nmin] - tr_head["mid"][tg]["x"][:nmin]))))
    out["m3_headon_gl4_vs_mid_dx"] = np.array(h_dx)
    print(f"  [headon] gl4 vs midpoint max|dx|={[round(v, 7) for v in h_dx]}", flush=True)


# ============================================================================
# M4: 6-Level SMR Kerr a=0.9M Clusters at N=10^4 and N=10^5
# ============================================================================

def run_m4(out: dict):
    print("\n=== M4: 6-Level SMR Kerr a=0.9M Clusters (N=10^4 & N=10^5) ===", flush=True)
    m4_dir = os.path.join(RUN_BASE, "m4")
    os.makedirs(m4_dir, exist_ok=True)
    os.makedirs(IC_BASE, exist_ok=True)

    ic_files = {}
    for N, seed in ((10000, 203), (100000, 204)):
        nrp = os.path.join(IC_BASE, f"bound_a0.9_n{N}.nrp")
        if not os.path.isfile(nrp):
            subprocess.run(
                [
                    sys.executable, os.path.join(REPO, "problems/cluster_test/make_cluster.py"),
                    "--N", str(N), "--a", "0.9", "--bound_only", "--seed", str(seed), "--out", nrp,
                ],
                check=True,
            )
        ic_files[N] = nrp

    tpl_ana = os.path.join(REPO, "problems/cluster_test/cluster_analytic.athinput")
    tpl_mesh = os.path.join(REPO, "problems/cluster_test/cluster_mesh.athinput")
    quiet_out = {f"output{k}": {"dt": "1.0e9"} for k in range(1, 6)}

    for N in (10000, 100000):
        ntag = "10k" if N == 10000 else "100k"
        ic_path = ic_files[N]
        for kind in ("ana", "mesh"):
            tpl = tpl_ana if kind == "ana" else tpl_mesh
            for mode in ("mid", "gl4"):
                lbl = f"m4_{kind}_{ntag}_{mode}"
                p_upd = {
                    "particle_file": ic_path,
                    "bh_spin": "0.9",
                    "dt": "0.05",
                    "traj_dcycle": "0",
                    "snap_dt": "200.0",
                    "hist_dcycle": "50" if kind == "ana" else "10",
                }
                if mode == "mid":
                    p_upd["pusher"] = "midpoint"
                    if kind == "mesh":
                        p_upd["filter_densitized"] = "false"
                else:
                    p_upd["pusher"] = "vlasov_hybrid"
                    p_upd["vlasov_mode"] = "hybrid"
                    p_upd["vlasov_pusher"] = "gl4"
                    if kind == "mesh":
                        p_upd["filter_densitized"] = "true"
                upd = {"job": {"basename": lbl}, "time": {"tlim": "200.0"}, "particles": p_upd}
                if kind == "mesh":
                    upd.update(quiet_out)
                cfg = os.path.join(m4_dir, f"{lbl}.athinput")
                rdir = os.path.join(m4_dir, lbl)
                patch_athinput(tpl, cfg, upd)
                wall_s, comp_s = run_athena(cfg, rdir, lbl)

                # Extract conservation, survival, phase mixing, and filtering metrics
                (_, x0, u0, _, tag0), (_, x1, u1, _, tag1) = read_particle_state(rdir, lbl)
                n_surv = len(x1)
                idx0_by_tag = {int(tg): i for i, tg in enumerate(tag0)}
                matched = [idx0_by_tag[int(tg)] for tg in tag1 if int(tg) in idx0_by_tag]
                if len(matched) == n_surv:
                    E0, L0, Q0 = _kerr.invariants("cks", x0[matched], u0[matched], a=0.9, M=1.0)
                    E1, L1, Q1 = _kerr.invariants("cks", x1, u1, a=0.9, M=1.0)
                    dE_rel = np.abs(E1 - E0) / np.abs(E0)
                    dL_rel = np.abs(L1 - L0) / np.abs(L0)
                    K0 = Q0 + (L0 - 0.9 * E0) ** 2
                    dQK_rel = np.abs(Q1 - Q0) / K0
                else:
                    E0, L0, Q0 = _kerr.invariants("cks", x0, u0, a=0.9, M=1.0)
                    E1, L1, Q1 = _kerr.invariants("cks", x1, u1, a=0.9, M=1.0)
                    dE_rel = np.array([abs(np.mean(E1) - np.mean(E0)) / abs(np.mean(E0))])
                    dL_rel = np.array([abs(np.mean(L1) - np.mean(L0)) / abs(np.mean(L0))])
                    K0 = np.mean(Q0 + (L0 - 0.9 * E0) ** 2)
                    dQK_rel = np.array([abs(np.mean(Q1) - np.mean(Q0)) / K0])

                phi1 = np.arctan2(x1[:, 1], x1[:, 0])
                order_param = float(np.abs(np.mean(np.exp(1j * phi1))))

                nrp = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
                if kind == "mesh" and np.any(np.abs(nrp["int_E"]) > 0.0):
                    rel_filt = np.abs(nrp["int_E_filtered"] - nrp["int_E"]) / np.maximum(np.abs(nrp["int_E"]), 1e-30)
                    filt_t0 = float((nrp["int_E_filtered"][0] - nrp["int_E"][0]) / nrp["int_E"][0])
                    filt_med = float(np.median(rel_filt))
                    filt_max = float(np.max(rel_filt))
                else:
                    filt_t0 = filt_med = filt_max = np.nan

                medE, p99E, maxE = [float(v) for v in np.percentile(dE_rel, [50, 99, 100])]
                medL, p99L, maxL = [float(v) for v in np.percentile(dL_rel, [50, 99, 100])]
                medQ = float(np.median(dQK_rel))
                print(
                    f"  [{kind:4s} {ntag:4s} {mode:3s}] wall={wall_s:6.2f}s comp={comp_s:6.2f}s surv={n_surv}/{N} "
                    f"dE(med/p99/max)=({medE:.2e}/{p99E:.2e}/{maxE:.2e}) dLz_med={medL:.2e} dQ/K_med={medQ:.2e} "
                    f"|e^iphi|={order_param:.4f} filt(t0/med/max)=({filt_t0:.2e}/{filt_med:.2e}/{filt_max:.2e})",
                    flush=True,
                )
                for k, v in dict(
                    wall=wall_s, comp=comp_s, surv=n_surv, N=N,
                    medE=medE, p99E=p99E, maxE=maxE, medL=medL, p99L=p99L, maxL=maxL,
                    medQK=medQ, order=order_param, filt_t0=filt_t0, filt_med=filt_med, filt_max=filt_max,
                ).items():
                    out[f"{lbl}_{k}"] = float(v)


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    out = {}
    run_m1_m2(out)
    run_m3(out)
    run_m4(out)
    np.savez(OUT_NPZ, **out)
    print(f"\nSaved Wave 4A reduced data: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
