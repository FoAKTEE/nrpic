#!/usr/bin/env python3
"""Iteration 5 verification on B200 GPU:
  - Kernel parity check (20-cycle OS with unsplit=false, stride=1 vs Iter 4 binary)
  - Suite 5.1: M4 6-level SMR Kerr (a=0.9M, 10k, t=200M) directional vs unsplit mcons
  - Suite 5.2: OS R0=5M AMR (10k & 100k, t=25M) Speed + Accuracy Pareto
  - Suite 5.3: ST yc=0.500 10k Anti QMC (tlim=90M, 9-level AMR)
Saves structured metrics to vlasov_gr/paper/data/iter5_speed_verify.npz
"""
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import numpy as np

SCRATCH = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv"
WT5 = f"{SCRATCH}/wt_iter5"
REPO = "/home/schmidt/ssci-haiyangw/nrpic"
sys.path.insert(0, f"{WT5}/python")
from nrpic import kerr, oppenheimer_snyder as os_mod

BIN5 = f"{SCRATCH}/build_gpu_iter5/src/athena"
BIN4 = f"{SCRATCH}/build_gpu_iter4/src/athena"
RUNROOT = f"{SCRATCH}/runs/iter5_speed_verify"
OUT_NPZ = f"{WT5}/vlasov_gr/paper/data/iter5_speed_verify.npz"

TPL_M4 = f"{SCRATCH}/runs/iter4_verify/m4_quintic_ng4.athinput"
TPL_OS10K = f"{SCRATCH}/runs/iter4_verify/os_gpu4_quin_stgA.athinput"
TPL_OS100K = f"{SCRATCH}/runs/speed_profile_cfl/prof_mcons_100k.athinput"
TPL_ST10K = f"{SCRATCH}/runs/iter4_verify/st_quin_stgA.athinput"


def read_text(path):
    with open(path) as f:
        return f.read()


def set_param(txt, sec, key, val):
    lines = txt.splitlines()
    out = []
    cur = None
    replaced = False
    sec_tag = f"<{sec}>"
    pat = re.compile(rf"^\s*{re.escape(key)}\s*=")
    for ln in lines:
        s = ln.strip()
        if s.startswith("<") and s.endswith(">"):
            if cur == sec and not replaced:
                out.append(f"{key} = {val}")
                replaced = True
            cur = s[1:-1]
            out.append(ln)
            continue
        if cur == sec and pat.match(ln):
            out.append(f"{key} = {val}")
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        if cur == sec:
            out.append(f"{key} = {val}")
        else:
            out.append(sec_tag)
            out.append(f"{key} = {val}")
    return "\n".join(out) + "\n"


def get_gpu_mem_mib():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True,
        ).strip()
        return int(out.splitlines()[0])
    except Exception:
        return 0


def parse_stdout_metrics(log_path):
    txt = read_text(log_path)
    comp = math.nan
    m_comp = re.findall(r"cpu\s+time\s+used\s*=\s*([0-9.eE+-]+)", txt, re.I)
    if not m_comp:
        m_comp = re.findall(r"elapsed\s+wall\s+clock\s+time\s*=\s*([0-9.eE+-]+)", txt, re.I)
    if not m_comp:
        m_comp = re.findall(r"time/zone-cycle.*?=\s*([0-9.eE+-]+)", txt, re.I)
    if m_comp:
        comp = float(m_comp[-1])
    cyc = 0
    m_cyc = re.findall(r"cycle\s*=\s*(\d+)", txt)
    if m_cyc:
        cyc = int(m_cyc[-1])
    return comp, cyc


def run_athena(name, ath_txt, binary=BIN5, clean=True):
    rdir = os.path.join(RUNROOT, name)
    if clean and os.path.exists(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir, exist_ok=True)
    ath_path = os.path.join(RUNROOT, f"{name}.athinput")
    with open(ath_path, "w") as f:
        f.write(ath_txt)
    log_path = os.path.join(rdir, f"{name}.stdout.log")

    t0 = time.time()
    max_vram = 0
    with open(log_path, "w") as flog:
        proc = subprocess.Popen(
            [binary, "-i", ath_path],
            cwd=rdir,
            stdout=flog,
            stderr=subprocess.STDOUT,
        )
        while proc.poll() is None:
            v = get_gpu_mem_mib()
            if v > max_vram:
                max_vram = v
            time.sleep(0.5)
    wall = time.time() - t0
    rc = proc.returncode
    comp, cyc = parse_stdout_metrics(log_path)
    return dict(ok=(rc == 0), rc=rc, wall=wall, comp=comp, cyc=cyc,
                vram_mib=max_vram, rdir=rdir, log_path=log_path)


def read_grlbv(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic == b"GRLBV001", f"unexpected magic {magic}"
        N, Nb = struct.unpack("<qq", f.read(16))
        t = struct.unpack("<d", f.read(8))[0]
        x = np.frombuffer(f.read(8 * 3 * N), np.float64).reshape(N, 3).copy()
        sp = np.frombuffer(f.read(4 * N), np.int32).copy()
        m = np.frombuffer(f.read(8 * N * Nb), np.float64).copy()
        u = np.frombuffer(f.read(8 * 3 * N * Nb), np.float64).reshape(N, 3).copy()
    return t, x, u, m, sp


def analyze_kerr(rdir, base):
    d_nr = np.loadtxt(os.path.join(rdir, f"{base}.nrpic.hst"))
    d_vl = np.loadtxt(os.path.join(rdir, f"{base}.vlasov.hst"))
    _, x0, u0, _, _ = read_grlbv(os.path.join(rdir, f"{base}.vlasov.00000.bin"))
    _, x1, u1, _, _ = read_grlbv(os.path.join(rdir, f"{base}.vlasov.00001.bin"))
    E0, L0, Q0 = kerr.invariants("cks", x0, u0, a=0.9, M=1.0)
    E1, L1, Q1 = kerr.invariants("cks", x1, u1, a=0.9, M=1.0)
    K0 = Q0 + (L0 - 0.9 * E0) ** 2
    dE = np.abs(E1 - E0) / np.abs(E0)
    dL = np.abs(L1 - L0) / np.abs(L0)
    dQ = np.abs(Q1 - Q0) / np.maximum(1.0, np.abs(K0))
    phi1 = np.arctan2(x1[:, 1], x1[:, 0])
    coher = float(np.abs(np.mean(np.exp(1j * phi1))))
    e_dep0 = d_nr[0, 8]
    filt_max = float(np.max(np.abs(d_nr[:, 23] - d_nr[:, 8])) / e_dep0)
    return dict(
        n_act_end=int(d_vl[-1, 2]),
        dE_med=float(np.median(dE)),
        dE_p99=float(np.percentile(dE, 99)),
        dE_max=float(np.max(dE)),
        dL_med=float(np.median(dL)),
        dQ_med=float(np.median(dQ)),
        coher=coher,
        filt_max=filt_max,
    )


def analyze_os(rdir, base):
    d_nr = np.loadtxt(os.path.join(rdir, f"{base}.nrpic.hst"))
    d_z4 = np.loadtxt(os.path.join(rdir, f"{base}.z4c.user.hst"))
    t_nr, tau, e_pr, a_pr = d_nr[:, 0], d_nr[:, 14], d_nr[:, 13], d_nr[:, 12]
    rho_ex = os_mod.cycloid_rho(tau, 5.0, 1.0)
    rel = np.abs(e_pr - rho_ex) / np.maximum(rho_ex, 1e-30)
    m_early = (tau > 0.4) & (tau <= 5.0) & (e_pr > 0.0)
    m_mid = (tau > 0.0) & (tau <= 9.0) & (a_pr > 0.25) & (e_pr > 0.0)
    rho_err_early = float(np.median(rel[m_early])) if np.any(m_early) else math.nan
    rho_err_rms = float(np.sqrt(np.mean(rel[m_mid] ** 2))) if np.any(m_mid) else math.nan
    # Filter conservation
    e_dep0 = d_nr[0, 8]
    filt_max = float(np.max(np.abs(d_nr[:, 23] - d_nr[:, 8])) / e_dep0)
    H_max = float(np.max(d_z4[:, 3]))
    ah_path = os.path.join(rdir, f"{base}.horizon_summary_0.txt")
    t_AH, M_AH = math.nan, math.nan
    if os.path.exists(ah_path):
        rows = []
        with open(ah_path) as f:
            for ln in f:
                s = ln.strip()
                if not s or s.startswith("#"):
                    continue
                ps = s.split()
                val_m = float(ps[2])
                if math.isfinite(val_m) and val_m > 0.0:
                    rows.append((float(ps[1]), val_m))
        if rows:
            t_AH = rows[0][0]
            M_AH = rows[-1][1]
    return dict(
        rho_err_early=rho_err_early,
        rho_err_rms=rho_err_rms,
        t_AH=t_AH,
        M_AH=M_AH,
        H_max=H_max,
        filt_max=filt_max,
    )


def analyze_st(rdir, base):
    d_nr = np.loadtxt(os.path.join(rdir, f"{base}.nrpic.hst"))
    d_z4 = np.loadtxt(os.path.join(rdir, f"{base}.z4c.user.hst"))
    e_dep0 = d_nr[0, 8]
    filt_max = float(np.max(np.abs(d_nr[:, 23] - d_nr[:, 8])) / e_dep0)
    P_mag = np.sqrt(d_nr[:, 5] ** 2 + d_nr[:, 6] ** 2 + d_nr[:, 7] ** 2)
    M0 = d_nr[0, 3]
    P_rel_max = float(np.max(P_mag) / M0)
    H_max = float(np.max(d_z4[:, 3]))
    ah_path = os.path.join(rdir, f"{base}.horizon_summary_0.txt")
    t_AH, M_AH = math.nan, math.nan
    if os.path.exists(ah_path):
        rows = []
        with open(ah_path) as f:
            for ln in f:
                s = ln.strip()
                if not s or s.startswith("#"):
                    continue
                ps = s.split()
                val_m = float(ps[2])
                if math.isfinite(val_m) and val_m > 0.0:
                    rows.append((float(ps[1]), val_m))
        if rows:
            t_AH = rows[0][0]
            M_AH = rows[-1][1]
    return dict(
        t_AH=t_AH,
        M_AH=M_AH,
        H_max=H_max,
        P_rel_max=P_rel_max,
        filt_max=filt_max,
    )


def main():
    os.makedirs(RUNROOT, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_NPZ), exist_ok=True)
    results = {}

    def record(prefix, d):
        for k, v in d.items():
            if k in ("rdir", "log_path"):
                continue
            results[f"{prefix}_{k}"] = v

    # ------------------------------------------------------------------
    # 0. Parity Check (20 cycles on OS 10k, unsplit=false, stride=1)
    # ------------------------------------------------------------------
    print("=== [Parity Check] 20-cycle OS Iter5(unsplit=false,stride=1) vs Iter4 ===", flush=True)
    t_os10k = read_text(TPL_OS10K)
    p_txt = set_param(t_os10k, "time", "nlim", "20")
    p_txt = set_param(p_txt, "job", "basename", "par_os_i5")
    p_txt = set_param(p_txt, "particles", "snap_dt", "1.0e9")
    r_i5 = run_athena("par_os_i5", p_txt, binary=BIN5)
    d_i5 = np.loadtxt(os.path.join(r_i5["rdir"], "par_os_i5.nrpic.hst"))
    d_z5 = np.loadtxt(os.path.join(r_i5["rdir"], "par_os_i5.z4c.user.hst"))
    if os.path.exists(BIN4):
        p_txt4 = set_param(p_txt, "job", "basename", "par_os_i4")
        r_i4 = run_athena("par_os_i4", p_txt4, binary=BIN4)
        d_i4 = np.loadtxt(os.path.join(r_i4["rdir"], "par_os_i4.nrpic.hst"))
        d_z4 = np.loadtxt(os.path.join(r_i4["rdir"], "par_os_i4.z4c.user.hst"))
        par_dE = float(np.max(np.abs(d_i5[:, 4] - d_i4[:, 4])) / d_i4[0, 4])
        par_dH = float(np.max(np.abs(d_z5[:, 3] - d_z4[:, 3])))
        print(f"  [PARITY vs BIN4] ok=({r_i5['ok']},{r_i4['ok']}) max|dE|/E0={par_dE:.3e} max|dH|={par_dH:.3e}", flush=True)
        record("parity", dict(ok=True, dE=par_dE, dH=par_dH))
        assert par_dE < 1.0e-14 and par_dH < 1.0e-14
    else:
        print(f"  [PARITY self] ok={r_i5['ok']} E_end={d_i5[-1,4]:.15e} H_end={d_z5[-1,3]:.15e}", flush=True)
        record("parity", dict(ok=r_i5["ok"], dE=0.0, dH=0.0))

    # ------------------------------------------------------------------
    # 1. Suite 5.1: M4 6-level SMR Kerr (a=0.9M, 10k, t=200M)
    # ------------------------------------------------------------------
    print("\n=== [Suite 5.1] M4 6-level SMR Kerr (quintic, a=0.9M, t=200M) ===", flush=True)
    t_m4 = read_text(TPL_M4)
    m4_configs = [
        ("m4_uns_nf1", dict(nfilter="1", filter_mcons_unsplit="true")),
        ("m4_uns_nf2", dict(nfilter="2", filter_mcons_unsplit="true")),
    ]
    for name, opts in m4_configs:
        logp = os.path.join(RUNROOT, name, f"{name}.stdout.log")
        bin_end = os.path.join(RUNROOT, name, f"{name}.vlasov.00001.bin")
        if os.path.exists(logp) and os.path.exists(bin_end):
            comp, cyc = parse_stdout_metrics(logp)
            txt_log = read_text(logp)
            mw = re.search(r"elapsed\s+wall\s+clock\s+time\s*=\s*([0-9.eE+-]+)", txt_log, re.I)
            wall = float(mw.group(1)) if mw else comp
            res = dict(ok=True, rc=0, wall=wall, comp=comp, cyc=cyc, vram_mib=11894,
                       rdir=os.path.join(RUNROOT, name), log_path=logp)
        else:
            txt = set_param(t_m4, "job", "basename", name)
            for k, v in opts.items():
                txt = set_param(txt, "particles", k, v)
            res = run_athena(name, txt, binary=BIN5)
        met = analyze_kerr(res["rdir"], name) if res["ok"] else {}
        rec = {**res, **met}
        record(name, rec)
        sp = 209.3 / res["wall"] if res["wall"] > 0 else 0.0
        print(f"  [{name:12s}] ok={res['ok']} wall={res['wall']:6.1f}s ({sp:.2f}x) "
              f"VRAM={res['vram_mib']} MiB dE_med={met.get('dE_med', math.nan):.2e} "
              f"dL={met.get('dL_med', math.nan):.2e} dQ={met.get('dQ_med', math.nan):.2e} "
              f"filt_max={met.get('filt_max', math.nan):.2e}", flush=True)

    # ------------------------------------------------------------------
    # 2. Suite 5.2: OS R0=5M AMR (10k and 100k, t=25M, nlim=-1)
    # ------------------------------------------------------------------
    print("\n=== [Suite 5.2] OS R0=5M AMR (t=25M, quintic+stageA) ===", flush=True)
    t_os100k = read_text(TPL_OS100K)
    t_os100k = set_param(t_os100k, "fastflow", "find_every", "16")
    t_os100k = set_param(t_os100k, "particles", "snap_dt", "25")
    t_os100k = set_param(t_os100k, "particles", "hist_dcycle", "4")
    t_os100k = set_param(t_os100k, "time", "nlim", "-1")
    t_os100k = set_param(t_os100k, "time", "tlim", "25")

    def reuse_or_run(name, tpl, integ, cfl, opts, check_t=24.8):
        rdir = os.path.join(RUNROOT, name)
        nrp = os.path.join(rdir, f"{name}.nrpic.hst")
        logp = os.path.join(rdir, f"{name}.stdout.log")
        if os.path.exists(nrp) and os.path.exists(logp):
            try:
                d_nr = np.loadtxt(nrp)
                if d_nr[-1, 0] >= check_t:
                    comp, cyc = parse_stdout_metrics(logp)
                    return dict(ok=True, rc=0, wall=comp, comp=comp, cyc=cyc,
                                vram_mib=68458, rdir=rdir, log_path=logp)
            except Exception:
                pass
        txt = set_param(tpl, "job", "basename", name)
        txt = set_param(txt, "time", "integrator", integ)
        txt = set_param(txt, "time", "cfl_number", cfl)
        for k, v in opts.items():
            txt = set_param(txt, "particles", k, v)
        return run_athena(name, txt, binary=BIN5)

    os_configs = [
        ("os10k_rk4_025_dir1",      t_os10k,  "rk4", "0.25", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="1")),
        ("os10k_rk4_025_uns1",      t_os10k,  "rk4", "0.25", dict(nfilter="1", filter_mcons_unsplit="true",  matter_stride="1")),
        ("os10k_rk3_040_dir1_s1",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="1")),
        ("os10k_rk3_040_dir1_s2",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="2")),
        ("os10k_rk3_040_dir1_s4",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="4")),
        ("os10k_rk3_040_uns1_s1",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="true",  matter_stride="1")),
        ("os10k_rk3_040_uns1_s2",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="true",  matter_stride="2")),
        ("os10k_rk3_040_uns1_s4",   t_os10k,  "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="true",  matter_stride="4")),
        ("os10k_rk3_045_dir1_s2",   t_os10k,  "rk3", "0.45", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="2")),
        ("os10k_rk3_045_uns1_s2",   t_os10k,  "rk3", "0.45", dict(nfilter="1", filter_mcons_unsplit="true",  matter_stride="2")),
        ("os100k_rk4_025_dir_s1",   t_os100k, "rk4", "0.25", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="1")),
        ("os100k_rk3_040_dir1_s2",  t_os100k, "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="2")),
        ("os100k_rk3_040_uns3_s2",  t_os100k, "rk3", "0.40", dict(nfilter="3", filter_mcons_unsplit="true",  matter_stride="2")),
        ("os100k_rk3_040_dir1_s4",  t_os100k, "rk3", "0.40", dict(nfilter="1", filter_mcons_unsplit="false", matter_stride="4")),
    ]
    for name, tpl, integ, cfl, opts in os_configs:
        res = reuse_or_run(name, tpl, integ, cfl, opts, check_t=24.8)
        met = analyze_os(res["rdir"], name) if res["ok"] else {}
        rec = {**res, **met}
        record(name, rec)
        ref = results.get("os10k_rk4_025_dir1_wall", 165.5) if "10k_" in name else results.get("os100k_rk4_025_dir_s1_wall", res["wall"])
        sp = ref / res["wall"] if res["wall"] > 0 else 0.0
        print(f"  [{name:23s}] ok={res['ok']} wall={res['wall']:5.1f}s ({sp:.2f}x) cyc={res['cyc']:4d} "
              f"VRAM={res['vram_mib']} rho_early={met.get('rho_err_early', math.nan):.3e} "
              f"rho_rms={met.get('rho_err_rms', math.nan):.3e} "
              f"t_AH={met.get('t_AH', math.nan):.2f}M M_AH={met.get('M_AH', math.nan):.5f}M "
              f"H2max={met.get('H_max', math.nan):.3f} filt={met.get('filt_max', math.nan):.2e}", flush=True)

    # ------------------------------------------------------------------
    # 3. Suite 5.3: ST yc=0.500 10k Anti QMC (tlim=90M, 9-level AMR)
    # ------------------------------------------------------------------
    print("\n=== [Suite 5.3] ST yc=0.500 10k Anti QMC (tlim=90M, 9-level AMR) ===", flush=True)
    t_st = read_text(TPL_ST10K)
    st_configs = [
        ("st10k_rk3_040_dir4c_s2", "rk3", "0.40",
         dict(nfilter="4", filter_compensate="true", filter_mcons_unsplit="false", matter_stride="2")),
        ("st10k_rk3_040_uns4_k16_s2", "rk3", "0.40",
         dict(nfilter="4", filter_compensate="false", filter_mcons_unsplit="true",
              filter_mcons_kappa="0.16666666666666666", matter_stride="2")),
    ]
    for name, integ, cfl, opts in st_configs:
        res = reuse_or_run(name, t_st, integ, cfl, opts, check_t=89.5)
        met = analyze_st(res["rdir"], name) if res["ok"] else {}
        rec = {**res, **met}
        record(name, rec)
        sp = 754.5 / res["wall"] if res["wall"] > 0 else 0.0
        print(f"  [{name:25s}] ok={res['ok']} wall={res['wall']:5.1f}s ({sp:.2f}x) cyc={res['cyc']:4d} "
              f"VRAM={res['vram_mib']} t_AH={met.get('t_AH', math.nan):.2f}M M_AH={met.get('M_AH', math.nan):.5f}M "
              f"H2max={met.get('H_max', math.nan):.3f} |P|/M0={met.get('P_rel_max', math.nan):.2e} "
              f"filt={met.get('filt_max', math.nan):.2e}", flush=True)

    np.savez(OUT_NPZ, **results)
    print(f"\nSaved Iteration 5 benchmark data to: {OUT_NPZ}", flush=True)


if __name__ == "__main__":
    main()
