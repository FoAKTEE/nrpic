#!/usr/bin/env python3
"""Speed-First B200 Profiling & High-CFL Integrator Sweep (`build_gpu_iter4`):
  Part A: High-CFL & Integrator Sweep on OS R0=5M (`t=25M`, `os_10k_lat`, `mcons + quintic + stageA`)
          testing `rk4` at `cfl = 0.25, 0.35, 0.40, 0.45, 0.50` and `rk3` at `cfl = 0.25, 0.35, 0.40`.
  Part B: Exact Per-Component GPU Wall-Clock Breakdown (`nlim=200` on OS AMR `N=10k` & `N=100k`
          plus M4 Kerr 6-level SMR `plain` vs `mcons`):
          1. `z4c_only` (2-particle dummy zero-mass IC on exact OS AMR grid -> Z4c + bvals floor)
          2. `+push_only` (`deposit=false`, `nfilter=0`, `find_every=100000`) at `10k` and `100k`
          3. `+deposit_plain` (`deposit=true`, `nfilter=2`, `mcons=false`, `find_every=100000`) at `10k` and `100k`
          4. `+mcons` (`deposit=true`, `nfilter=2`, `mcons=true`, `find_every=100000`) at `10k` and `100k`
          5. `+mcons+ah` (`find_every=16`) at `10k` and `100k`

Saves `vlasov_gr/paper/data/speed_profile_cfl.npz`.
"""

import os
import re
import subprocess
import sys
import time as pytime

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrpic import io as nio  # noqa: E402
from nrpic import oppenheimer_snyder as _osn  # noqa: E402
import run_repro_wave4b as w4b  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU4_BIN = os.path.join(SCRATCH, "build_gpu_iter4", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "speed_profile_cfl")
W4B_IC = os.path.join(SCRATCH, "runs", "repro_wave4b", "ic")
I3_BASE = os.path.join(SCRATCH, "runs", "iter3_verify")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "speed_profile_cfl.npz")


def run_athena_safe(cfg: str, rdir: str, label: str, timeout_s: float = 420.0):
    log_path = os.path.join(rdir, f"{label}.stdout.log")
    if os.path.isfile(log_path):
        txt = open(log_path, "r").read()
        if ("Terminating on time limit" in txt) or ("Terminating on cycle limit" in txt):
            m_c = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
            m_w = re.search(r"# wall_s = ([0-9.eE+-]+)", txt)
            m_cy = re.search(r"cycle\s*=\s*([0-9]+)", txt)
            m_nmb = re.search(r"Current number of MeshBlocks\s*=\s*([0-9]+)", txt)
            return dict(
                ok=True,
                wall=float(m_w.group(1)) if m_w else np.nan,
                comp=float(m_c.group(1)) if m_c else np.nan,
                cycles=int(m_cy.group(1)) if m_cy else -1,
                nmb=int(m_nmb.group(1)) if m_nmb else -1,
            )
    w4b.clean_dir(rdir)
    t0 = pytime.perf_counter()
    try:
        res = subprocess.run([GPU4_BIN, "-i", cfg, "-d", rdir], capture_output=True, text=True, timeout=timeout_s)
        wall_s = pytime.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return dict(ok=False, wall=pytime.perf_counter() - t0, comp=np.nan, cycles=-1, nmb=-1, reason="timeout")

    with open(log_path, "w") as f:
        f.write(res.stdout)
        f.write(f"\n# wall_s = {wall_s:.6f}\n")
        if res.stderr:
            f.write("\n=== STDERR ===\n" + res.stderr)

    if res.returncode != 0 or ("NaN" in res.stdout) or ("nan" in res.stderr.lower()):
        return dict(ok=False, wall=wall_s, comp=np.nan, cycles=-1, nmb=-1, reason=f"rc={res.returncode}")

    m_c = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", res.stdout)
    m_cy = re.search(r"cycle\s*=\s*([0-9]+)", res.stdout)
    m_nmb = re.search(r"Current number of MeshBlocks\s*=\s*([0-9]+)", res.stdout)
    return dict(
        ok=True,
        wall=wall_s,
        comp=float(m_c.group(1)) if m_c else wall_s,
        cycles=int(m_cy.group(1)) if m_cy else -1,
        nmb=int(m_nmb.group(1)) if m_nmb else -1,
    )


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    out = {}

    tpl_os = os.path.join(REPO, "problems/os/os_amr.athinput")
    nrp_10k = os.path.join(W4B_IC, "os", "ic_iter3_os_10k_lat.nrp")
    tab_10k = os.path.join(W4B_IC, "os", "ic_iter3_os_10k_lat.tab")
    nrp_100k = os.path.join(W4B_IC, "os", "ic_os_100k_qmc_hyb.nrp")
    tab_100k = os.path.join(W4B_IC, "os", "ic_os_100k_qmc_hyb.tab")
    E0 = _osn.rho0(5.0, 1.0)

    # ------------------------------------------------------------------
    # Part A: High-CFL & Integrator Sweep on OS R0=5M (t=25M)
    # ------------------------------------------------------------------
    print("=== [Part A] High-CFL & RK3/RK4 Sweep on OS R0=5M (t=25M, mcons+quintic+stageA) ===", flush=True)
    sweep_specs = [
        ("rk4", 0.25),
        ("rk4", 0.35),
        ("rk4", 0.40),
        ("rk4", 0.45),
        ("rk4", 0.50),
        ("rk3", 0.25),
        ("rk3", 0.35),
        ("rk3", 0.40),
    ]
    w_base = None
    for integ, cfl in sweep_specs:
        lbl = f"cfl_{integ}_{str(cfl).replace('.', '')}"
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        w4b.patch_athinput(
            tpl_os, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"max_nmb_per_rank": "2048"},
                "time": {
                    "integrator": integ,
                    "tlim": "25.0",
                    "cfl_number": f"{cfl:.12g}",
                    "ndiag": "100",
                },
                "fastflow": {"metric_drvts": "interpolant", "find_every": "16"},
                "particles": {
                    "particle_file": nrp_10k,
                    "pusher": "vlasov_hybrid",
                    "vlasov_mode": "hybrid",
                    "vlasov_pusher": "gl4",
                    "vlasov_time_interp": "quadratic",
                    "interp": "quintic",
                    "hist_dcycle": "4",
                    "snap_dt": "25.0",
                    "filter_densitized": "false",
                    "filter_metric_conservative": "true",
                    "source_density": "false",
                    "source_extrap": "false",
                    "source_stage_extrap": "true",
                },
                "problem": {"comp0_file": tab_10k},
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        res = run_athena_safe(cfg, rdir, lbl, timeout_s=360.0)
        if not res["ok"]:
            print(f"  [{integ:3s} cfl={cfl:.2f}] UNSTABLE / FAILED ({res.get('reason','')}, wall={res['wall']:.1f}s)", flush=True)
            out[f"{lbl}_ok"] = 0.0
            out[f"{lbl}_wall"] = float(res["wall"])
            continue

        m = w4b.extract_common_metrics(rdir, lbl, True)
        nrp_h = m["nrp"]
        tau = nrp_h["tau_probe"]
        mask_p = (tau > 0.0) & (tau <= 2.6) & (nrp_h["E_probe"] > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask_p]]) / E0
        rho_err = float(np.max(np.abs(nrp_h["E_probe"][mask_p] / E0 - rho_cyc) / rho_cyc)) if np.any(mask_p) else np.nan
        if not np.isfinite(m["H_max"]) or m["H_max"] > 10.0:
            print(f"  [{integ:3s} cfl={cfl:.2f}] BLOWN UP ||H||_max={m['H_max']:.3e}", flush=True)
            out[f"{lbl}_ok"] = 0.0
            continue
        if w_base is None and integ == "rk4" and abs(cfl - 0.25) < 1e-6:
            w_base = res["wall"]
        sp = (w_base / res["wall"]) if w_base else 1.0
        print(
            f"  [{integ:3s} cfl={cfl:.2f}] wall={res['wall']:6.1f}s ({sp:.2f}x) cyc={res['cycles']:4d} "
            f"rho_err={rho_err:.3e} t_AH={m['t_ah']:.2f}M M_AH={m['M_ah']:.5f}M "
            f"||H||_max={m['H_max']:.3e} filt_max={m['filt_max']:.2e}",
            flush=True,
        )
        out[f"{lbl}_ok"] = 1.0
        for k, v in dict(
            wall=res["wall"], comp=res["comp"], cycles=res["cycles"],
            rho_err=rho_err, t_AH=m["t_ah"], M_AH=m["M_ah"],
            H_max=m["H_max"], filt_max=m["filt_max"],
        ).items():
            out[f"{lbl}_{k}"] = float(v)

    # ------------------------------------------------------------------
    # Part B: Per-Component GPU Wall-Clock Decomposition (nlim=200 cycles)
    # ------------------------------------------------------------------
    print("\n=== [Part B] Per-Component B200 GPU Profiling (nlim=200 cycles) ===", flush=True)
    # Dummy minimal zero-mass particle file for z4c_only baseline
    ic_zero = os.path.join(RUN_BASE, "ic_zero_2p.nrp")
    nio.write_nrp(ic_zero, np.array([[0.1, 0.1, 0.1], [-0.1, -0.1, -0.1]]),
                  np.zeros((2, 3)), np.zeros(2))

    # Fixed 200-cycle runs across ablations
    ablations_10k = [
        ("z4c_only",      ic_zero, tab_10k, "false", "0", "false", "100000"),
        ("push_only_10k", nrp_10k, tab_10k, "false", "0", "false", "100000"),
        ("dep_plain_10k", nrp_10k, tab_10k, "true",  "2", "false", "100000"),
        ("mcons_10k",     nrp_10k, tab_10k, "true",  "2", "true",  "100000"),
        ("mcons_ah_10k",  nrp_10k, tab_10k, "true",  "2", "true",  "16"),
    ]
    ablations_100k = [
        ("push_only_100k", nrp_100k, tab_100k, "false", "0", "false", "100000"),
        ("dep_plain_100k", nrp_100k, tab_100k, "true",  "2", "false", "100000"),
        ("mcons_100k",     nrp_100k, tab_100k, "true",  "2", "true",  "100000"),
        ("mcons_ah_100k",  nrp_100k, tab_100k, "true",  "2", "true",  "16"),
    ]
    for lbl, nrp_f, tab_f, dep, nf, mc, fev in ablations_10k + ablations_100k:
        cfg = os.path.join(RUN_BASE, f"prof_{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, f"prof_{lbl}")
        w4b.patch_athinput(
            tpl_os, cfg,
            updates={
                "job": {"basename": f"prof_{lbl}"},
                "mesh_refinement": {"max_nmb_per_rank": "2048"},
                "time": {"nlim": "200", "tlim": "100.0", "cfl_number": "0.25", "ndiag": "200"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": fev},
                "particles": {
                    "particle_file": nrp_f,
                    "pusher": "vlasov_hybrid",
                    "vlasov_mode": "hybrid",
                    "vlasov_pusher": "gl4",
                    "vlasov_time_interp": "quadratic",
                    "interp": "quintic",
                    "deposit": dep,
                    "nfilter": nf,
                    "filter_densitized": "false",
                    "filter_metric_conservative": mc,
                    "source_stage_extrap": "true",
                    "hist_dcycle": "50",
                    "snap_dt": "1e9",
                },
                "problem": {"comp0_file": tab_f},
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        res = run_athena_safe(cfg, rdir, f"prof_{lbl}", timeout_s=300.0)
        ms_cyc = 1000.0 * res["comp"] / max(res["cycles"], 1)
        print(
            f"  [PROF {lbl:16s}] comp={res['comp']:6.2f}s wall={res['wall']:6.2f}s "
            f"ms/cyc={ms_cyc:6.2f} nmb={res['nmb']:4d}",
            flush=True,
        )
        out[f"prof_{lbl}_comp"] = float(res["comp"])
        out[f"prof_{lbl}_wall"] = float(res["wall"])
        out[f"prof_{lbl}_mscyc"] = float(ms_cyc)
        out[f"prof_{lbl}_nmb"] = float(res["nmb"])

    # Also profile 200 steps on M4 6-level SMR Kerr (1128 blocks) plain vs mcons (ng=4)
    print("\n=== [Part B2] M4 Kerr 6-level SMR (1128 blocks, nlim=400) plain vs mcons ===", flush=True)
    tpl_kerr = os.path.join(REPO, "problems/cluster_test/cluster_mesh.athinput")
    ic_kerr = os.path.join(I3_BASE, "ic_bound_a0.9_n10000.nrp")
    for klbl, mc in (("kerr_plain_400", "false"), ("kerr_mcons_400", "true")):
        cfg = os.path.join(RUN_BASE, f"prof_{klbl}.athinput")
        rdir = os.path.join(RUN_BASE, f"prof_{klbl}")
        w4b.patch_athinput(
            tpl_kerr, cfg,
            updates={
                "job": {"basename": f"prof_{klbl}"},
                "mesh": {"nghost": "4"},
                "time": {"nlim": "400", "tlim": "200.0", "ndiag": "400"},
                "particles": {
                    "particle_file": ic_kerr,
                    "bh_spin": "0.9",
                    "dt": "0.05",
                    "traj_dcycle": "0",
                    "snap_dt": "1e9",
                    "hist_dcycle": "100",
                    "pusher": "vlasov_hybrid",
                    "vlasov_mode": "hybrid",
                    "vlasov_pusher": "gl4",
                    "interp": "quintic",
                    "filter_densitized": "false",
                    "filter_metric_conservative": mc,
                },
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(1, 6)},
        )
        res = run_athena_safe(cfg, rdir, f"prof_{klbl}", timeout_s=300.0)
        ms_cyc = 1000.0 * res["comp"] / max(res["cycles"], 1)
        print(f"  [PROF {klbl:16s}] comp={res['comp']:6.2f}s wall={res['wall']:6.2f}s ms/cyc={ms_cyc:6.2f}", flush=True)
        out[f"prof_{klbl}_comp"] = float(res["comp"])
        out[f"prof_{klbl}_wall"] = float(res["wall"])
        out[f"prof_{klbl}_mscyc"] = float(ms_cyc)

    np.savez_compressed(OUT_NPZ, **out)
    print(f"\nSaved speed & CFL profiling data: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
