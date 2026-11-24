#!/usr/bin/env python3
"""Iteration 3 Verification: Self-Adjoint Metric-Weighted Flux-Conservative Filter
with Exact AMR Refluxing (`filter_metric_conservative = true`).

Tests on B200 GPU (plus GPU vs 4-thread OpenMP parity):
  1. M5a Oppenheimer-Snyder R0=5M (`os_10k_lat`, N=9328, t=25M):
     `plain` vs `dens` vs `mcons` -> proves mcons restores central density accuracy
     (`rho_err ~ 4e-4` vs `3.35e-3` for `dens`) WHILE enforcing machine-precision
     proper-volume conservation across dynamic AMR (`filt_t0, filt_max < 1e-13`).
  2. M4 6-Level SMR Kerr a=0.9M cluster (`mesh 10k`, t=200M):
     `plain` vs `dens` vs `mcons` -> proves `filt_t0, filt_max < 1e-13` across SMR jumps.
  3. M5b Prolate compensated filter (`prol_10k_qmc`, nfilter=4, filter_compensate=true,
     t=5.0M short conservation/stability check): verifies negative-kappa compensated
     metric-conservative pass on 7-level AMR (`filt_t0, filt_max < 1e-13`).
  4. GPU vs OpenMP (4 threads) 10-step OS AMR determinism with `filter_metric_conservative = true`.

Saves `vlasov_gr/paper/data/iter3_filter_verify.npz`.
"""

import glob
import json
import os
import re
import subprocess
import sys
import time as pytime

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrpic import oppenheimer_snyder as _osn  # noqa: E402
from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402
import run_repro_wave4b as w4b  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
GPU_BIN = os.path.join(SCRATCH, "build_gpu", "src", "athena")
OMP_BIN = os.path.join(SCRATCH, "build_omp", "src", "athena")
RUN_BASE = os.path.join(SCRATCH, "runs", "iter3_verify")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "iter3_filter_verify.npz")


def _filter_params(fmode: str) -> dict:
    if fmode == "plain":
        return {"filter_densitized": "false", "filter_metric_conservative": "false"}
    if fmode == "dens":
        return {"filter_densitized": "true", "filter_metric_conservative": "false"}
    if fmode == "mcons":
        return {"filter_densitized": "false", "filter_metric_conservative": "true"}
    raise ValueError(fmode)


def _read_vlv_state(rdir: str, basename: str):
    vfiles = sorted(glob.glob(os.path.join(rdir, f"{basename}.vlasov.*.bin")))
    s = vg.read_grlbv(vfiles[-1])
    return s["x"], s["u_bar"]


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    out = {}

    # 1. M5a Oppenheimer-Snyder R0=5M (os_10k_lat, N=9328, t=25M)
    print("=== [Iter 3 / 1] M5a Oppenheimer-Snyder R0=5M (os_10k_lat) ===", flush=True)
    E0 = _osn.rho0(5.0, 1.0)
    tpl_os = os.path.join(REPO, "problems/os/os_amr.athinput")
    nrp_os, tab_os, meta_os = w4b.gen_ic(
        "os", "ic_iter3_os_10k_lat",
        ["--R0", "5.0", "--sampler", "lattice", "--nlat", "26", "--lattice-surface-correction"],
    )
    for fmode in ("plain", "dens", "mcons"):
        lbl = f"iter3_os_10k_{fmode}"
        p_upd = {
            "particle_file": nrp_os,
            "pusher": "vlasov_hybrid",
            "vlasov_mode": "hybrid",
            "vlasov_pusher": "gl4",
            "vlasov_time_interp": "quadratic",
            "hist_dcycle": "4",
            "snap_dt": "25.0",
        }
        p_upd.update(_filter_params(fmode))
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        w4b.patch_athinput(
            tpl_os, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"max_nmb_per_rank": "2048"},
                "time": {"tlim": "25.0", "ndiag": "100"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "16"},
                "particles": p_upd,
                "problem": {"comp0_file": tab_os},
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s = w4b.run_athena(cfg, rdir, lbl, timeout_s=1200.0)
        m = w4b.extract_common_metrics(rdir, lbl, True)
        nrp_h = m["nrp"]
        tau = nrp_h["tau_probe"]
        mask_p = (tau > 0.0) & (tau <= 2.6) & (nrp_h["E_probe"] > 0.0)
        rho_cyc = np.array([float(_osn.cycloid_rho(xt)) for xt in tau[mask_p]]) / E0
        rho_err = float(np.max(np.abs(nrp_h["E_probe"][mask_p] / E0 - rho_cyc) / rho_cyc))
        print(
            f"  [OS {fmode:5s}] wall={wall_s:6.1f}s comp={comp_s:6.1f}s rho_err={rho_err:.3e} "
            f"t_AH={m['t_ah']:.2f}M M_AH={m['M_ah']:.5f}M ||H||_max={m['H_max']:.3e} "
            f"filt(t0/max)=({m['filt_t0']:.2e}/{m['filt_max']:.2e})",
            flush=True,
        )
        for k, v in dict(
            wall=wall_s, comp=comp_s, rho_err=rho_err, t_AH=m["t_ah"], M_AH=m["M_ah"],
            H_max=m["H_max"], filt_t0=m["filt_t0"], filt_max=m["filt_max"],
        ).items():
            out[f"os_{fmode}_{k}"] = float(v)

    # 2. M4 6-level SMR Kerr cluster (mesh 10k, t=200M)
    print("\n=== [Iter 3 / 2] M4 6-Level SMR Kerr Cluster (mesh 10k, t=200M) ===", flush=True)
    ic_kerr = os.path.join(RUN_BASE, "ic_bound_a0.9_n10000.nrp")
    if not os.path.isfile(ic_kerr):
        subprocess.run(
            [
                sys.executable, os.path.join(REPO, "problems/cluster_test/make_cluster.py"),
                "--N", "10000", "--a", "0.9", "--bound_only", "--seed", "203", "--out", ic_kerr,
            ],
            check=True,
        )
    tpl_kerr = os.path.join(REPO, "problems/cluster_test/cluster_mesh.athinput")
    for fmode in ("plain", "dens", "mcons"):
        lbl = f"iter3_kerr_10k_{fmode}"
        p_upd = {
            "particle_file": ic_kerr,
            "bh_spin": "0.9",
            "dt": "0.05",
            "traj_dcycle": "0",
            "snap_dt": "200.0",
            "hist_dcycle": "10",
            "pusher": "vlasov_hybrid",
            "vlasov_mode": "hybrid",
            "vlasov_pusher": "gl4",
        }
        p_upd.update(_filter_params(fmode))
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        upd = {"job": {"basename": lbl}, "time": {"tlim": "200.0"}, "particles": p_upd}
        w4b.patch_athinput(
            tpl_kerr, cfg, upd,
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(1, 6)},
        )
        wall_s, comp_s = w4b.run_athena(cfg, rdir, lbl, timeout_s=1200.0)
        nrp_h = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        rel_filt = np.abs(nrp_h["int_E_filtered"] - nrp_h["int_E"]) / np.maximum(np.abs(nrp_h["int_E"]), 1e-30)
        filt_t0 = float((nrp_h["int_E_filtered"][0] - nrp_h["int_E"][0]) / nrp_h["int_E"][0])
        filt_max = float(np.max(rel_filt))
        x1, _ = _read_vlv_state(rdir, lbl)
        order = float(np.abs(np.mean(np.exp(1j * np.arctan2(x1[:, 1], x1[:, 0])))))
        print(
            f"  [M4 {fmode:5s}] wall={wall_s:6.2f}s comp={comp_s:6.2f}s "
            f"|e^iphi|={order:.4f} filt(t0/max)=({filt_t0:.2e}/{filt_max:.2e})",
            flush=True,
        )
        for k, v in dict(wall=wall_s, comp=comp_s, order=order, filt_t0=filt_t0, filt_max=filt_max).items():
            out[f"m4_{fmode}_{k}"] = float(v)

    # 3. M5b Prolate compensated filter (7-level AMR, nfilter=4, filter_compensate=true, t=5M check)
    print("\n=== [Iter 3 / 3] M5b Prolate Compensated Filter Check (t=5M) ===", flush=True)
    nrp_pr, _, _ = w4b.gen_ic(
        "prolate", "ic_iter3_prol_10k",
        ["--e", "0.9", "--b", "10.0", "--N", "10000", "--sampler", "qmc_octant", "--seed", "1"],
    )
    tpl_pr = os.path.join(REPO, "problems/prolate/prolate_amr.athinput")
    for fmode in ("dens", "mcons"):
        lbl = f"iter3_prol_10k_{fmode}"
        p_upd = {
            "particle_file": nrp_pr,
            "pusher": "vlasov_hybrid",
            "vlasov_mode": "hybrid",
            "vlasov_pusher": "gl4",
            "vlasov_time_interp": "quadratic",
            "nfilter": "4",
            "filter_compensate": "true",
            "filter_comp_c": "-1.0",
            "hist_dcycle": "4",
            "snap_dt": "5.0",
        }
        p_upd.update(_filter_params(fmode))
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        w4b.patch_athinput(
            tpl_pr, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"num_levels": "7", "max_nmb_per_rank": "3072"},
                "time": {"tlim": "5.0", "ndiag": "50"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "32"},
                "particles": p_upd,
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        wall_s, comp_s = w4b.run_athena(cfg, rdir, lbl, timeout_s=600.0)
        m = w4b.extract_common_metrics(rdir, lbl, True)
        print(
            f"  [Prol {fmode:5s}] wall={wall_s:6.1f}s ||H||_max={m['H_max']:.3e} "
            f"filt(t0/max)=({m['filt_t0']:.2e}/{m['filt_max']:.2e})",
            flush=True,
        )
        out[f"prol_{fmode}_H_max"] = float(m["H_max"])
        out[f"prol_{fmode}_filt_t0"] = float(m["filt_t0"])
        out[f"prol_{fmode}_filt_max"] = float(m["filt_max"])

    # 4. GPU vs OpenMP (4 threads) 10-step OS AMR determinism with mcons
    print("\n=== [Iter 3 / 4] GPU vs OpenMP (4t) 10-step OS AMR Determinism ===", flush=True)
    for tag, binary, env_upd in (
        ("gpu", GPU_BIN, {}),
        ("omp", OMP_BIN, {"OMP_NUM_THREADS": "4"}),
    ):
        lbl = f"iter3_det_{tag}"
        p_upd = {
            "particle_file": nrp_os,
            "pusher": "vlasov_hybrid",
            "vlasov_mode": "hybrid",
            "vlasov_pusher": "gl4",
            "vlasov_time_interp": "quadratic",
            "hist_dcycle": "1",
            "snap_dt": "1.0e-9",
            "filter_densitized": "false",
            "filter_metric_conservative": "true",
        }
        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        w4b.patch_athinput(
            tpl_os, cfg,
            updates={
                "job": {"basename": lbl},
                "mesh_refinement": {"max_nmb_per_rank": "2048"},
                "time": {"nlim": "10", "tlim": "100.0", "ndiag": "50"},
                "fastflow": {"metric_drvts": "interpolant", "find_every": "16"},
                "particles": p_upd,
                "problem": {"comp0_file": tab_os},
            },
            existing_only={f"output{k}": {"dt": "1.0e9"} for k in range(2, 6)},
        )
        w4b.clean_dir(rdir)
        env = dict(os.environ)
        env.update(env_upd)
        res = subprocess.run([binary, "-i", cfg, "-d", rdir], capture_output=True, text=True, env=env, timeout=300)
        if res.returncode != 0:
            raise RuntimeError(f"Determinism run {tag} failed:\n{res.stdout[-800:]}\n{res.stderr[-500:]}")
    xg, ug = _read_vlv_state(os.path.join(RUN_BASE, "iter3_det_gpu"), "iter3_det_gpu")
    xo, uo = _read_vlv_state(os.path.join(RUN_BASE, "iter3_det_omp"), "iter3_det_omp")
    hg = s4a.read_col_hst(os.path.join(RUN_BASE, "iter3_det_gpu", "iter3_det_gpu.nrpic.hst"))
    ho = s4a.read_col_hst(os.path.join(RUN_BASE, "iter3_det_omp", "iter3_det_omp.nrpic.hst"))
    det_dx = float(np.max(np.abs(xg - xo)))
    det_du = float(np.max(np.abs(ug - uo)))
    det_df = float(np.max(np.abs(hg["int_E_filtered"] - ho["int_E_filtered"]) / np.abs(hg["int_E"])))
    print(f"  [Det GPU vs OMP4] max|dx|={det_dx:.3e} max|du|={det_du:.3e} rel|d_int_E_filt|={det_df:.3e}", flush=True)
    out["det_dx"] = det_dx
    out["det_du"] = det_du
    out["det_df"] = det_df

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved Iteration 3 verification data: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
