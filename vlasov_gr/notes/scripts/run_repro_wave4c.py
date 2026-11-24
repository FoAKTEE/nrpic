#!/usr/bin/env python3
"""Phase 4 Wave 4C: Reproduce Wu & Most / NRPIC M6 Jeans Binary BH Formation at N=10^4 and N=10^5:
  Uses verified `jeans/n1e4_v19` configuration (+-80M domain, 8 levels, finest M/64,
  tlim=20M focused on binary BH formation at t_AH~10.5M, metric_drvts=interpolant,
  ah_exc_factor=0.8, alpha_exc=0.05, flow_const=0.05, comp1/comp2 Bowen-York clump momenta).

Compares `stratified + midpoint (plain filter)` vs
`qmc_antipodal (N=10^4) / qmc_lebedev (Q=14, N=10^5) + vlasov_hybrid (gl4 + quadratic + filter_metric_conservative=true)`.
Saves reduced metrics to `vlasov_gr/paper/data/repro_wave4c.npz`.
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

from nrpic import vlasov_gr as vg  # noqa: E402
import run_stage4a_suites123 as s4a  # noqa: E402
import run_repro_wave4b as w4b  # noqa: E402

SCRATCH = os.environ.get(
    "SCRATCH_ROOT", "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
)
RUN_BASE = os.path.join(SCRATCH, "runs", "repro_wave4c")
IC_BASE = os.path.join(RUN_BASE, "ic")
OUT_NPZ = os.path.join(REPO, "vlasov_gr", "paper", "data", "repro_wave4c.npz")


def gen_jeans_ic(N: int, sampler: str, seed: int = 1):
    ntag = "10k" if N == 10000 else "100k"
    stem = f"jeans_{ntag}_{sampler}"
    out_dir = os.path.join(IC_BASE, stem)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, f"{stem}.json")
    nrp_path = os.path.join(out_dir, f"{stem}.nrp")
    if not (os.path.isfile(json_path) and os.path.isfile(nrp_path)):
        cmd = [
            sys.executable, os.path.join(REPO, "problems/ic/make_ic.py"),
            "jeans", "--N", str(N), "--seed", str(seed),
            "--env-yc", "0.907", "--clump-curvature",
            "--sampler", sampler,
            "--out", out_dir, "--prefix", stem,
        ]
        if sampler == "qmc_lebedev":
            cmd += ["--lebedev-q", "14"]
        subprocess.run(cmd, check=True)
    meta = json.load(open(json_path))
    tab_abs = os.path.join(out_dir, meta["athenak"]["problem"]["comp0_file"])
    return nrp_path, tab_abs, meta


def main():
    os.makedirs(RUN_BASE, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    tpl = os.path.join(REPO, "problems/jeans/jeans_mc.athinput")
    out = {}

    specs = [
        ("jeans_10k_strat_mid", 10000, "stratified", "mid"),
        ("jeans_10k_qmc_hyb", 10000, "qmc_antipodal", "hyb"),
        ("jeans_100k_strat_mid", 100000, "stratified", "mid"),
        ("jeans_100k_qmc_hyb", 100000, "qmc_lebedev", "hyb"),
    ]

    for lbl, N, samp, mode in specs:
        nrp, tab, meta = gen_jeans_ic(N, samp, seed=1)
        pblock = dict(meta["athenak"]["problem"])
        pblock["comp0_file"] = tab

        p_upd = {
            "particle_file": nrp,
            "hist_dcycle": "10",
            "snap_dt": "5.0",
            "ah_exc_factor": "0.8",
            "alpha_exc": "0.05",
        }
        if mode == "mid":
            p_upd["pusher"] = "midpoint"
            p_upd["filter_densitized"] = "false"
            p_upd["filter_metric_conservative"] = "false"
        else:
            p_upd["pusher"] = "vlasov_hybrid"
            p_upd["vlasov_mode"] = "hybrid"
            p_upd["vlasov_pusher"] = "gl4"
            p_upd["vlasov_time_interp"] = "quadratic"
            p_upd["filter_densitized"] = "false"
            p_upd["filter_metric_conservative"] = "true"

        cfg = os.path.join(RUN_BASE, f"{lbl}.athinput")
        rdir = os.path.join(RUN_BASE, lbl)
        existing_done = (
            os.path.isfile(os.path.join(rdir, f"{lbl}.nrpic.hst"))
            and os.path.isfile(os.path.join(rdir, f"{lbl}.horizon_summary_0.txt"))
            and os.path.isfile(os.path.join(rdir, f"{lbl}.horizon_summary_1.txt"))
        )
        if existing_done and os.environ.get("WAVE4C_OVERWRITE", "0") != "1":
            print(f"  [M6 {lbl:20s}] Reusing existing completed formation run in {rdir}", flush=True)
            wall_s, comp_s = np.nan, np.nan
        else:
            w4b.patch_athinput(
                tpl, cfg,
                updates={
                    "job": {"basename": lbl},
                    "time": {"tlim": os.environ.get("WAVE4C_TLIM", "20.0"), "ndiag": "200"},
                    "fastflow": {
                        "metric_drvts": "interpolant",
                        "find_every": "16",
                        "flow_alpha_beta_const_0": "0.05",
                        "flow_alpha_beta_const_1": "0.05",
                    },
                    "particles": p_upd,
                    "problem": pblock,
                },
                existing_only={"output2": {"dt": "1.0e9"}},
            )
            wall_s, comp_s = w4b.run_athena(cfg, rdir, lbl, timeout_s=7200.0)

        z4c = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.z4c.user.hst"))
        nrp_h = s4a.read_col_hst(os.path.join(rdir, f"{lbl}.nrpic.hst"))
        H_l2 = np.sqrt(np.maximum(z4c["H-norm2"], 0.0))
        M_l2 = np.sqrt(np.maximum(z4c["M-norm2"], 0.0))
        rel_filt = np.abs(nrp_h["int_E_filtered"] - nrp_h["int_E"]) / np.maximum(np.abs(nrp_h["int_E"]), 1e-30)

        ah_res = {}
        for hi in range(3):
            ahp = os.path.join(rdir, f"{lbl}.horizon_summary_{hi}.txt")
            if os.path.isfile(ahp):
                ah = s4a.read_horizon(ahp)
                if len(ah):
                    ah = ah[np.isfinite(ah[:, 1])]
                if len(ah):
                    # Columns (s4a.read_horizon): 0:t, 1:mass, 5:S (col 7), etc.
                    # Raw file cols: 1:iter 2:time 3:mass 4:Sx 5:Sy 6:Sz 7:S 8:area
                    ah_raw = np.loadtxt(ahp, comments="#")
                    if ah_raw.ndim == 1:
                        ah_raw = ah_raw[None, :]
                    ah_raw = ah_raw[np.isfinite(ah_raw[:, 2])]
                    if len(ah_raw):
                        m_f = float(ah_raw[-1, 2])
                        s_f = float(ah_raw[-1, 6])
                        chi_f = s_f / max(m_f * m_f, 1e-30)
                        ah_res[hi] = dict(
                            t0=float(ah_raw[0, 1]), M0=float(ah_raw[0, 2]),
                            M_fin=m_f, S_fin=s_f, chi_fin=chi_f,
                        )

        c0_t = np.loadtxt(os.path.join(rdir, f"{lbl}.co_0.txt"), comments="#") if os.path.isfile(os.path.join(rdir, f"{lbl}.co_0.txt")) else np.zeros((0, 5))
        c1_t = np.loadtxt(os.path.join(rdir, f"{lbl}.co_1.txt"), comments="#") if os.path.isfile(os.path.join(rdir, f"{lbl}.co_1.txt")) else np.zeros((0, 5))

        n_eff = int(meta.get("particles", {}).get("N", sum(c["N"] for c in meta.get("components", []))))
        print(
            f"  [M6 {lbl:20s} N={n_eff:6d}] wall={wall_s:6.1f}s comp={comp_s:6.1f}s "
            f"||H||_0={H_l2[0]:.3e} ||H||_max={np.max(H_l2):.3e} "
            f"filt(t0/max)=({(nrp_h['int_E_filtered'][0]-nrp_h['int_E'][0])/nrp_h['int_E'][0]:.2e}/{np.max(rel_filt):.2e}) "
            f"ah={ah_res}",
            flush=True,
        )
        out[f"{lbl}_N"] = float(n_eff)
        out[f"{lbl}_wall"] = wall_s
        out[f"{lbl}_comp"] = comp_s
        out[f"{lbl}_H0"] = float(H_l2[0])
        out[f"{lbl}_H_max"] = float(np.max(H_l2))
        out[f"{lbl}_M_max"] = float(np.max(M_l2))
        out[f"{lbl}_t_z4c"] = z4c["time"]
        out[f"{lbl}_H_l2"] = H_l2
        out[f"{lbl}_t_nrp"] = nrp_h["time"]
        out[f"{lbl}_alp_min"] = nrp_h["alpha_probe"] if "alpha_probe" in nrp_h else nrp_h["alpha_min"]
        out[f"{lbl}_nmb"] = nrp_h["nmb"]
        out[f"{lbl}_filt_t0"] = float((nrp_h["int_E_filtered"][0] - nrp_h["int_E"][0]) / nrp_h["int_E"][0])
        out[f"{lbl}_filt_max"] = float(np.max(rel_filt))
        for hi, hd in ah_res.items():
            for k, v in hd.items():
                out[f"{lbl}_ah{hi}_{k}"] = float(v)
        if len(c0_t) and len(c1_t):
            if c0_t.ndim == 1:
                c0_t = c0_t[None, :]
            if c1_t.ndim == 1:
                c1_t = c1_t[None, :]
            n_co = min(len(c0_t), len(c1_t))
            out[f"{lbl}_co_t"] = c0_t[:n_co, 1]
            out[f"{lbl}_co0_x"] = c0_t[:n_co, 2:5]
            out[f"{lbl}_co1_x"] = c1_t[:n_co, 2:5]

    np.savez(OUT_NPZ, **out)
    print(f"\nSaved Wave 4C reduced data: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
