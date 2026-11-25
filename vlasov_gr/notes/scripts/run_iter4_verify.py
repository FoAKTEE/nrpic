#!/usr/bin/env python3
"""Iteration 4 GPU Proof Suite (Worktree `feat/iter4-vram-quintic-backreaction`):
  4a. VRAM Slimming (`bflx` boundary-only refluxing + interior-only `e_prev`/`tm_prev`):
      - 10-step 7-level OS AMR determinism (`build_gpu_iter4` vs `build_gpu` & `build_omp_iter4` 4t)
      - Peak empirical GPU VRAM (`nvidia-smi` polling) & `t=25M` OS AMR throughput comparison
  4b. C^2 6-Node Quintic Hermite Interpolation (`interp = quintic`, zero extra `met*s` VRAM):
      - M4 6-level SMR Kerr a=0.9M cluster (`N=10^4`, `t=200M`, `gl4 + mcons`):
        `hermite (ng=4)` vs `bspline (ng=4)` vs `quintic (ng=4)` vs `quintic (ng=3)`
      - M5a OS R0=5M collapse (`t=25M`, `gl4 + mcons`): `hermite` vs `quintic`
  4c. Scheme A Stage-Accurate RK Backreaction (`source_stage_extrap = true`):
      - OS R0=5M CFL self-convergence (`cfl = 0.25, 0.125, 0.0625`, `t=10.0M`): `frozen` vs `stageA`
      - Full OS R0=5M collapse (`t=25.0M`, `cfl=0.25`): `frozen` vs `stageA` vs `stageA + quintic`
      - Nonlinear ST collapse (`yc=0.500`, `N=10^4`, Antipodal QMC + GL4 + mcons, `t=90.0M`): `frozen` vs `stageA`

Saves reduced metrics and convergence curves to `vlasov_gr/paper/data/iter4_verify.npz`.
"""

import glob
import os
import re
import subprocess
import sys
import threading
import time as pytime

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrpic import kerr as _kerr  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402
import run_repro_wave4b as w4b  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU3_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
GPU4_BIN = os.path.join(SCRATCH, "build_gpu_iter4", "src", "athena")
OMP4_BIN = os.path.join(SCRATCH, "build_omp_iter4", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "iter4_verify")
I3_BASE = os.path.join(SCRATCH, "runs", "iter3_verify")
W4B_IC = os.path.join(SCRATCH, "runs", "repro_wave4b", "ic")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "iter4_verify.npz")


def run_athena_mem(binary: str, cfg: str, rdir: str, label: str, timeout_s: float = 1800.0,
                   env_upd: dict = None, force: bool = False):
    """Run AthenaK while polling GPU memory via nvidia-smi and cache completion."""
    log_path = os.path.join(rdir, f"{label}.stdout.log")
    if (not force) and os.path.isfile(log_path):
        txt = open(log_path, "r").read()
        if ("Terminating on time limit" in txt) or ("Terminating on cycle limit" in txt):
            m_comp = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
            comp_s = float(m_comp.group(1)) if m_comp else np.nan
            m_w = re.search(r"# wall_s = ([0-9.eE+-]+)", txt)
            wall_s = float(m_w.group(1)) if m_w else comp_s
            m_v = re.search(r"# peak_vram_mib = ([0-9.eE+-]+)", txt)
            peak_mib = float(m_v.group(1)) if m_v else np.nan
            return wall_s, comp_s, peak_mib

    w4b.clean_dir(rdir)
    env = dict(os.environ)
    if env_upd:
        env.update(env_upd)

    peak_holder = [0.0]
    stop_ev = threading.Event()
    t0 = pytime.perf_counter()
    proc = subprocess.Popen(
        [binary, "-i", cfg, "-d", rdir],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
    )

    def _poll_vram():
        pid_s = str(proc.pid)
        while not stop_ev.is_set():
            try:
                out_nv = subprocess.check_output(
                    ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                    text=True, timeout=2.0,
                )
                for ln in out_nv.splitlines():
                    parts = [p.strip() for p in ln.split(",")]
                    if len(parts) == 2 and parts[0] == pid_s:
                        peak_holder[0] = max(peak_holder[0], float(parts[1]))
            except Exception:
                pass
            stop_ev.wait(0.25)

    mon = threading.Thread(target=_poll_vram, daemon=True)
    mon.start()
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    finally:
        stop_ev.set()
        mon.join(timeout=2.0)
    wall_s = pytime.perf_counter() - t0
    peak_mib = float(peak_holder[0]) if peak_holder[0] > 0.0 else np.nan

    with open(log_path, "w") as f:
        f.write(stdout)
        f.write(f"\n# wall_s = {wall_s:.6f}\n")
        f.write(f"# peak_vram_mib = {peak_mib:.3f}\n")
        if stderr:
            f.write("\n=== STDERR ===\n" + stderr)
    if proc.returncode != 0:
        raise RuntimeError(
            f"AthenaK failed ({label}, rc={proc.returncode}):\n{stdout[-1500:]}\n{stderr[-800:]}"
        )
    m_comp = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", stdout)
    comp_s = float(m_comp.group(1)) if m_comp else wall_s
    return wall_s, comp_s, peak_mib


def _read_vlv_state(rdir: str, basename: str):
    vfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.vlasov.*.bin")))
    s = vg.read_grlbv(vfiles[-1])
    return s["x"], s["u_bar"]


def run_os_case(binary: str, lbl: str, nrp_os: str, tab_os: str, tpl_os: str,
                interp: str = "hermite", stage_extrap: bool = False,
                tlim: float = 25.0, cfl: float = 0.25, nlim: int = -1,
                hist_dcycle: int = 4, ndiag: int = 100, snap_dt: float = 25.0,
                env_upd: dict = None, force: bool = False):
    E0 = _osn.rho0(5.0, 1.0)
    p_upd = {
        "particle_file": nrp_os,
        "pusher": "vlasov_hybrid",
        "vlasov_mode": "hybrid",
        "vlasov_pusher": "gl4",
        "vlasov_time_interp": "quadratic",
        "interp": interp,
        "hist_dcycle": str(hist_dcycle),
        "snap_dt": f"{snap_dt:.12g}",
        "filter_densitized": "false",
        "filter_metric_conservative": "true",
        "source_density": "false",
        "source_extrap": "false",
        "source_stage_extrap": "true" if stage_extrap else "false",
    }
    cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
    rdir = os.path.join(RUN_BASE, lbl)
    w4b.patch_athinput(
        tpl_os, cfg,
        updates={
            "job": {"basename": lbl},
            "mesh_refinement": {"max_nmb_per_rank": "2048"},
            "time": {
                "nlim": str(nlim),
                "tlim": f"{tlim:.12g}",
                "cfl_number": f"{cfl:.12g}",
                "ndiag": str(ndiag),
            },
            "fastflow": {"metric_drvts": "interpolant", "find_every": "16"},
            "particles": p_upd,
            "problem": {"comp0_file": tab_os},
        },
        existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
    )
    wall_s, comp_s, vram_mib = run_athena_mem(binary, cfg, rdir, lbl, timeout_s=1200.0, env_upd=env_upd, force=force)
    m = w4b.extract_common_metrics(rdir, lbl, True)
    nrp_h = m["nrp"]
    tau = nrp_h["tau_probe"]
    mask_p = (tau > 0.0) & (tau <= 2.6) & (nrp_h["E_probe"] > 0.0)
    rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask_p]]) / E0
    rho_err = float(np.max(np.abs(nrp_h["E_probe"][mask_p] / E0 - rho_cyc) / rho_cyc)) if np.any(mask_p) else np.nan
    return dict(
        lbl=lbl, rdir=rdir, wall=wall_s, comp=comp_s, vram_mib=vram_mib,
        rho_err=rho_err, t_AH=m["t_ah"], M_AH=m["M_ah"],
        H0=m["H0"], H_max=m["H_max"], H_end=float(m["H_l2"][-1]),
        M_max=m["M_max"], filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        alp_end=float(nrp_h["alpha_probe"][-1]),
        E_end=float(nrp_h["E_probe"][-1]),
        tau_end=float(nrp_h["tau_probe"][-1]),
        t_last=float(nrp_h["time"][-1]),
        t_arr=nrp_h["time"], alpha_arr=nrp_h["alpha_probe"], E_arr=nrp_h["E_probe"],
        tau_arr=nrp_h["tau_probe"], zt_arr=m["z4c"]["time"], H_arr=m["H_l2"],
    )


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    out = {}

    tpl_os = os.path.join(REPO, "problems/os/os_amr.athinput")
    nrp_os = os.path.join(W4B_IC, "os", "ic_iter3_os_10k_lat.nrp")
    tab_os = os.path.join(W4B_IC, "os", "ic_iter3_os_10k_lat.tab")
    if not (os.path.isfile(nrp_os) and os.path.isfile(tab_os)):
        nrp_os, tab_os, _ = w4b.gen_ic(
            "os", "ic_iter3_os_10k_lat",
            ["--R0", "5.0", "--sampler", "lattice", "--nlat", "26", "--lattice-surface-correction"],
        )

    # ------------------------------------------------------------------
    # [Iter 4a] VRAM Slimming & Determinism Parity
    # ------------------------------------------------------------------
    print("=== [Iter 4a] VRAM Slimming (`bflx` + interior prev) Parity & Overhead ===", flush=True)
    d_gpu3 = run_os_case(GPU3_BIN, "det10_gpu3", nrp_os, tab_os, tpl_os,
                         tlim=100.0, nlim=10, hist_dcycle=1, ndiag=50, snap_dt=1e-9)
    d_gpu4 = run_os_case(GPU4_BIN, "det10_gpu4", nrp_os, tab_os, tpl_os,
                         tlim=100.0, nlim=10, hist_dcycle=1, ndiag=50, snap_dt=1e-9)
    d_omp4 = run_os_case(OMP4_BIN, "det10_omp4", nrp_os, tab_os, tpl_os,
                         tlim=100.0, nlim=10, hist_dcycle=1, ndiag=50, snap_dt=1e-9,
                         env_upd={"OMP_NUM_THREADS": "4"})
    xg3, ug3 = _read_vlv_state(d_gpu3["rdir"], "det10_gpu3")
    xg4, ug4 = _read_vlv_state(d_gpu4["rdir"], "det10_gpu4")
    xo4, uo4 = _read_vlv_state(d_omp4["rdir"], "det10_omp4")

    par_g4_g3_dx = float(np.max(np.abs(xg4 - xg3)))
    par_g4_g3_du = float(np.max(np.abs(ug4 - ug3)))
    par_g4_o4_dx = float(np.max(np.abs(xg4 - xo4)))
    par_g4_o4_du = float(np.max(np.abs(ug4 - uo4)))
    hg3 = s4a.read_col_hst(os.path.join(d_gpu3["rdir"], "det10_gpu3.nrpic.hst"))
    hg4 = s4a.read_col_hst(os.path.join(d_gpu4["rdir"], "det10_gpu4.nrpic.hst"))
    ho4 = s4a.read_col_hst(os.path.join(d_omp4["rdir"], "det10_omp4.nrpic.hst"))
    par_g4_g3_df = float(np.max(np.abs(hg4["int_E_filtered"] - hg3["int_E_filtered"]) / np.maximum(np.abs(hg3["int_E"]), 1e-30)))
    par_g4_o4_df = float(np.max(np.abs(hg4["int_E_filtered"] - ho4["int_E_filtered"]) / np.maximum(np.abs(hg4["int_E"]), 1e-30)))
    print(
        f"  [Det10 GPU4 vs GPU3] max|dx|={par_g4_g3_dx:.3e} max|du|={par_g4_g3_du:.3e} rel|d_intE_filt|={par_g4_g3_df:.3e}\n"
        f"  [Det10 GPU4 vs OMP4] max|dx|={par_g4_o4_dx:.3e} max|du|={par_g4_o4_du:.3e} rel|d_intE_filt|={par_g4_o4_df:.3e} filt4_max={d_gpu4['filt_max']:.3e}",
        flush=True,
    )
    out["par_g4_g3_dx"] = par_g4_g3_dx
    out["par_g4_g3_du"] = par_g4_g3_du
    out["par_g4_g3_df"] = par_g4_g3_df
    out["par_g4_o4_dx"] = par_g4_o4_dx
    out["par_g4_o4_du"] = par_g4_o4_du
    out["par_g4_o4_df"] = par_g4_o4_df

    print("=== [Iter 4a] Full t=25M OS VRAM & Wall-Clock (build_gpu vs build_gpu_iter4) ===", flush=True)
    os_gpu3 = run_os_case(GPU3_BIN, "os_vram_gpu3", nrp_os, tab_os, tpl_os, interp="hermite", stage_extrap=False)
    os_gpu4 = run_os_case(GPU4_BIN, "os_vram_gpu4_herm_froz", nrp_os, tab_os, tpl_os, interp="hermite", stage_extrap=False)
    for tag, r in (("os_gpu3", os_gpu3), ("os_gpu4_herm_froz", os_gpu4)):
        print(
            f"  [{tag:20s}] wall={r['wall']:6.1f}s peak_VRAM={r['vram_mib']:6.0f} MiB "
            f"rho_err={r['rho_err']:.3e} t_AH={r['t_AH']:.2f}M M_AH={r['M_AH']:.5f}M "
            f"||H||_max={r['H_max']:.3e} filt_max={r['filt_max']:.2e}",
            flush=True,
        )
        for k in ("wall", "comp", "vram_mib", "rho_err", "t_AH", "M_AH", "H_max", "filt_t0", "filt_max"):
            out[f"{tag}_{k}"] = float(r[k])
        out[f"{tag}_zt"] = r["zt_arr"]
        out[f"{tag}_H"] = r["H_arr"]
        out[f"{tag}_tau"] = r["tau_arr"]
        out[f"{tag}_E"] = r["E_arr"]

    # ------------------------------------------------------------------
    # [Iter 4b] M4 6-Level SMR Kerr Cluster: hermite vs bspline vs quintic
    # ------------------------------------------------------------------
    print("\n=== [Iter 4b] M4 6-Level SMR Kerr a=0.9M Cluster (t=200M, gl4 + mcons) ===", flush=True)
    ic_kerr = os.path.join(I3_BASE, "ic_bound_a0.9_n10000.nrp")
    if not os.path.isfile(ic_kerr):
        ic_kerr = os.path.join(RUN_BASE, "ic_bound_a0.9_n10000.nrp")
        subprocess.run(
            [
                sys.executable, os.path.join(REPO, "problems/cluster_test/make_cluster.py"),
                "--N", "10000", "--a", "0.9", "--bound_only", "--seed", "203", "--out", ic_kerr,
            ],
            check=True,
        )
    tpl_kerr = os.path.join(REPO, "problems/cluster_test/cluster_mesh.athinput")
    kerr_specs = [
        ("hermite_ng2", "hermite", 2),
        ("hermite_ng4", "hermite", 4),
        ("bspline_ng4", "bspline", 4),
        ("quintic_ng4", "quintic", 4),
    ]
    for klbl, itp, ng in kerr_specs:
        lbl = f"m4_{klbl}"
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        w4b.patch_athinput(
            tpl_kerr, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh": {"nghost": str(ng)},
                "time": {"tlim": "200.0"},
                "particles": {
                    "particle_file": ic_kerr,
                    "bh_spin": "0.9",
                    "dt": "0.05",
                    "traj_dcycle": "0",
                    "snap_dt": "200.0",
                    "hist_dcycle": "10",
                    "pusher": "vlasov_hybrid",
                    "vlasov_mode": "hybrid",
                    "vlasov_pusher": "gl4",
                    "interp": itp,
                    "filter_densitized": "false",
                    "filter_metric_conservative": "true",
                },
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(1, 6)},
        )
        wall_s, comp_s, vram_mib = run_athena_mem(GPU4_BIN, cfg, rdir, lbl, timeout_s=1200.0)
        vfiles = sorted(glob.glob(os.path.join(rdir, f"{lbl}.vlasov.*.bin")))
        s0 = vg.read_grlbv(vfiles[0])
        s1 = vg.read_grlbv(vfiles[-1])
        x0, u0 = s0["x"], s0["u_bar"][:, 0, :]
        x1, u1 = s1["x"], s1["u_bar"][:, 0, :]
        n0, n1 = len(x0), len(x1)
        E0, L0, Q0 = _kerr.invariants("cks", x0, u0, a=0.9, M=1.0)
        E1, L1, Q1 = _kerr.invariants("cks", x1, u1, a=0.9, M=1.0)
        if n1 == n0:
            dE_arr = np.abs(E1 - E0) / np.abs(E0)
            dL_arr = np.abs(L1 - L0) / np.abs(L0)
            dQK_arr = np.abs(Q1 - Q0) / (Q0 + (L0 - 0.9 * E0) ** 2)
        else:
            dE_arr = np.array([abs(np.mean(E1) - np.mean(E0)) / abs(np.mean(E0))])
            dL_arr = np.array([abs(np.mean(L1) - np.mean(L0)) / abs(np.mean(L0))])
            dQK_arr = np.array([abs(np.mean(Q1) - np.mean(Q0)) / np.mean(Q0 + (L0 - 0.9 * E0) ** 2)])
        medE, p99E, maxE = [float(v) for v in np.percentile(dE_arr, [50, 99, 100])]
        medL, p99L, maxL = [float(v) for v in np.percentile(dL_arr, [50, 99, 100])]
        medQK = float(np.median(dQK_arr))
        order = float(np.abs(np.mean(np.exp(1j * np.arctan2(x1[:, 1], x1[:, 0])))))
        nrp_h = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        rel_filt = np.abs(nrp_h["int_E_filtered"] - nrp_h["int_E"]) / np.maximum(np.abs(nrp_h["int_E"]), 1e-30)
        filt_t0 = float((nrp_h["int_E_filtered"][0] - nrp_h["int_E"][0]) / nrp_h["int_E"][0])
        filt_max = float(np.max(rel_filt))
        print(
            f"  [M4 {klbl:12s}] wall={wall_s:6.1f}s VRAM={vram_mib:5.0f}MiB surv={n1}/{n0} "
            f"dE(med/p99/max)=({medE:.2e}/{p99E:.2e}/{maxE:.2e}) dL_med={medL:.2e} "
            f"dQ/K_med={medQK:.2e} |e^iphi|={order:.4f} filt_max={filt_max:.2e}",
            flush=True,
        )
        for k, v in dict(
            wall=wall_s, comp=comp_s, vram_mib=vram_mib, surv=n1,
            medE=medE, p99E=p99E, maxE=maxE, medL=medL, p99L=p99L, maxL=maxL,
            medQK=medQK, order=order, filt_t0=filt_t0, filt_max=filt_max,
        ).items():
            out[f"m4_{klbl}_{k}"] = float(v)
        out[f"m4_{klbl}_dE_arr"] = dE_arr.astype(np.float64)
        out[f"m4_{klbl}_dL_arr"] = dL_arr.astype(np.float64)

    # M5a OS R0=5M: quintic (frozen)
    print("\n=== [Iter 4b/4c] M5a OS R0=5M Variants (t=25M, mcons) ===", flush=True)
    for tag, itp, stg in [
        ("os_gpu4_quin_froz", "quintic", False),
        ("os_gpu4_herm_stgA", "hermite", True),
        ("os_gpu4_quin_stgA", "quintic", True),
    ]:
        r = run_os_case(GPU4_BIN, tag, nrp_os, tab_os, tpl_os, interp=itp, stage_extrap=stg)
        print(
            f"  [{tag:20s}] wall={r['wall']:6.1f}s peak_VRAM={r['vram_mib']:6.0f} MiB "
            f"rho_err={r['rho_err']:.3e} t_AH={r['t_AH']:.2f}M M_AH={r['M_AH']:.5f}M "
            f"||H||_max={r['H_max']:.3e} filt_max={r['filt_max']:.2e}",
            flush=True,
        )
        for k in ("wall", "comp", "vram_mib", "rho_err", "t_AH", "M_AH", "H_max", "filt_t0", "filt_max"):
            out[f"{tag}_{k}"] = float(r[k])
        out[f"{tag}_zt"] = r["zt_arr"]
        out[f"{tag}_H"] = r["H_arr"]
        out[f"{tag}_tau"] = r["tau_arr"]
        out[f"{tag}_E"] = r["E_arr"]

    # ------------------------------------------------------------------
    # [Iter 4c] OS CFL Temporal Convergence (`t=10.0M`, frozen vs stageA)
    # ------------------------------------------------------------------
    print("\n=== [Iter 4c] OS Collapse CFL Convergence (t=10.0M, hermite + mcons) ===", flush=True)
    cfl_vals = (0.25, 0.125, 0.0625)
    cfl_res = {}
    for sname, stg in (("frozen", False), ("stageA", True)):
        cfl_res[sname] = {}
        for cfl in cfl_vals:
            lbl = f"oscfl_{sname}_cfl{str(cfl).replace('.', '')}"
            r = run_os_case(
                GPU4_BIN, lbl, nrp_os, tab_os, tpl_os,
                interp="hermite", stage_extrap=stg,
                tlim=10.0, cfl=cfl, hist_dcycle=1, ndiag=1, snap_dt=10.0,
            )
            cfl_res[sname][cfl] = r
            print(
                f"  [{sname:6s} cfl={cfl:6.4f}] t_last={r['t_last']:.6f} wall={r['wall']:5.1f}s "
                f"alp(10)={r['alp_end']:.12f} rho(10)={r['E_end']:.12e} "
                f"||H||_2(10)={r['H_end']:.10e} rho_err={r['rho_err']:.3e} filt_max={r['filt_max']:.2e}",
                flush=True,
            )
            for k in ("wall", "vram_mib", "alp_end", "E_end", "H_end", "rho_err", "filt_max"):
                out[f"{lbl}_{k}"] = float(r[k])

        # Compute empirical CFL convergence rate against finest cfl=0.0625
        for qkey, qname in (("alp_end", "alpha_c"), ("E_end", "rho_c"), ("H_end", "H_l2")):
            q025 = cfl_res[sname][0.25][qkey]
            q012 = cfl_res[sname][0.125][qkey]
            q006 = cfl_res[sname][0.0625][qkey]
            e1 = abs(q025 - q006)
            e2 = abs(q012 - q006)
            p_ord = np.log2(e1 / max(e2, 1e-30)) if e2 > 0 else np.nan
            rel1 = e1 / max(abs(q006), 1e-30)
            rel2 = e2 / max(abs(q006), 1e-30)
            print(f"  [CFL order {sname:6s} {qname:7s}] rel(0.25)={rel1:.3e} rel(0.125)={rel2:.3e} p_emp={p_ord:.2f}", flush=True)
            out[f"cfl_{sname}_{qname}_rel025"] = float(rel1)
            out[f"cfl_{sname}_{qname}_rel0125"] = float(rel2)
            out[f"cfl_{sname}_{qname}_order"] = float(p_ord)

    # ------------------------------------------------------------------
    # [Iter 4c] Nonlinear ST Collapse (yc=0.500, 10k Antipodal QMC + GL4 + mcons, tlim=90M)
    # ------------------------------------------------------------------
    print("\n=== [Iter 4c] ST Collapse yc=0.500 10k Anti QMC (tlim=90M, mcons) ===", flush=True)
    nrp_st = os.path.join(W4B_IC, "st", "ic_st_yc0500_vp01_10k_hyb_anti.nrp")
    tab_st = os.path.join(W4B_IC, "st", "ic_st_yc0500_vp01_10k_hyb_anti.tab")
    if not (os.path.isfile(nrp_st) and os.path.isfile(tab_st)):
        nrp_st, tab_st, _ = w4b.gen_ic(
            "st", "ic_st_yc0500_vp01_10k_hyb_anti",
            ["--yc", "0.500", "--N", "10000", "--vpert", "0.01", "--sampler", "qmc_antipodal",
             "--seed", "1", "--consistent-table"],
        )
    tpl_st_amr = os.path.join(REPO, "problems/st/st_cluster_amr.athinput")
    for sname, itp, stg in [
        ("st_herm_froz", "hermite", False),
        ("st_quin_stgA", "quintic", True),
    ]:
        cfg = os.path.join(RUN_BASE, f"{sname}.athinput")
        rdir = os.path.join(RUN_BASE, sname)
        w4b.patch_athinput(
            tpl_st_amr, cfg,
            updates={
                "job": {"basename": sname},
                "mesh_refinement": {"max_nmb_per_rank": "3072"},
                "time": {"tlim": "90.0", "ndiag": "500"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "32"},
                "particles": {
                    "particle_file": nrp_st,
                    "pusher": "vlasov_hybrid",
                    "vlasov_mode": "hybrid",
                    "vlasov_pusher": "gl4",
                    "vlasov_time_interp": "quadratic",
                    "interp": itp,
                    "hist_dcycle": "20",
                    "snap_dt": "90.0",
                    "filter_densitized": "false",
                    "filter_metric_conservative": "true",
                    "source_density": "false",
                    "source_extrap": "false",
                    "source_stage_extrap": "true" if stg else "false",
                },
                "problem": {"comp0_file": tab_st},
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s, vram_mib = run_athena_mem(GPU4_BIN, cfg, rdir, sname, timeout_s=1800.0)
        m = w4b.extract_common_metrics(rdir, sname, True)
        nh = m["nrp"]
        p_norm = np.sqrt(nh["sum_mux"]**2 + nh["sum_muy"]**2 + nh["sum_muz"]**2) / max(float(nh["sum_m"][0]), 1e-30)
        p_max = float(np.max(p_norm))
        print(
            f"  [{sname:14s}] wall={wall_s:6.1f}s VRAM={vram_mib:5.0f}MiB t_AH={m['t_ah']:.2f}M "
            f"M_AH={m['M_ah']:.5f}M ||H||_max={m['H_max']:.3e} |P|_max/M0={p_max:.2e} filt_max={m['filt_max']:.2e}",
            flush=True,
        )
        for k, v in dict(
            wall=wall_s, comp=comp_s, vram_mib=vram_mib,
            t_AH=m["t_ah"], M_AH=m["M_ah"], H_max=m["H_max"],
            P_max=p_max, filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        ).items():
            out[f"{sname}_{k}"] = float(v)
        out[f"{sname}_zt"] = m["z4c"]["time"]
        out[f"{sname}_H"] = m["H_l2"]
        out[f"{sname}_t"] = nh["time"]
        out[f"{sname}_ac"] = nh["alpha_probe"]

    np.savez_compressed(OUT_NPZ, **out)
    print(f"\nSaved Iteration 4 verification data: {OUT_NPZ} ({os.path.getsize(OUT_NPZ)/1e3:.1f} KB)", flush=True)


if __name__ == "__main__":
    main()
