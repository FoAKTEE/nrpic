#!/usr/bin/env python3
"""
Pure-CPU gravitational-wave, orbital, and constraint analyzer for 1000:1 EMRI NR runs.
Extracts multi-sphere rPsi4^{(l,m)}, aligns retarded time u = t - r_*, extrapolates 1/r,
computes FFI strain r h_{lm} and fluxes F_E, F_J, measures e_NR and residual self-drag
(dL_z/dt vs -F_J), compares quantitatively against 3.5PN, 1SF (0PA), and 2SF (1PA),
and generates Cyclic-Zoom publication figures + analysis_summary.json.
"""

import argparse
import glob
import json
import math
import os
import re
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz

from pn_2sf_reference import EMRIReferenceModel


def keep_latest_monotonic(t_arr, tol=1e-12):
    n = len(t_arr)
    if n <= 1:
        return np.ones(n, dtype=bool)
    keep = np.zeros(n, dtype=bool)
    t_cap = np.inf
    for i in range(n - 1, -1, -1):
        if t_arr[i] < t_cap - tol:
            keep[i] = True
            t_cap = float(t_arr[i])
    return keep


def safe_load_table(path, min_cols=2, tcol=0):
    if not os.path.isfile(path):
        return None
    rows = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < min_cols:
                continue
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    if not rows:
        return None
    ncol = len(rows[0])
    rows = [r for r in rows if len(r) == ncol]
    if not rows:
        return None
    arr = np.asarray(rows, dtype=np.float64)
    if tcol is not None and len(arr) > 1:
        arr = arr[keep_latest_monotonic(arr[:, tcol])]
    return arr


def read_single_traj(path):
    if not os.path.isfile(path):
        return None
    sz = os.path.getsize(path)
    nrec = sz // 64
    if nrec <= 0:
        return None
    raw = np.fromfile(path, dtype="<f8", count=nrec * 8).reshape(nrec, 8)
    m0 = raw[:, 1] == 0.0
    arr = raw[m0]
    if len(arr) > 1:
        arr = arr[keep_latest_monotonic(arr[:, 0])]
    return arr  # cols: t, tag, x, y, z, ux, uy, uz


def read_single_trajmet(path):
    if not os.path.isfile(path):
        return None
    sz = os.path.getsize(path)
    nrec = sz // 136
    if nrec <= 0:
        return None
    raw = np.fromfile(path, dtype="<f8", count=nrec * 17).reshape(nrec, 17)
    m0 = raw[:, 1] == 0.0
    arr = raw[m0]
    if len(arr) > 1:
        arr = arr[keep_latest_monotonic(arr[:, 0])]
    return arr  # cols: 0=t, 1=tag, 2=alpha, 6=gxx, 9=gyy, 11=gzz


def r_areal_from_iso(r_iso, m0=1.0):
    return r_iso * ((1.0 + m0 / (2.0 * r_iso)) ** 2)


def rstar_schw(R, m0=1.0):
    return R + 2.0 * m0 * np.log(np.maximum(R / (2.0 * m0) - 1.0, 1.0e-12))


def lm_col(l, m):
    """0-indexed column in waveforms/rpsi4_{real,imag}_XXXX.txt (col 0 = time)."""
    return 1 + l * l + l + m - 4


def load_waveform_spheres(run_dir, radii):
    spheres = {}
    for rad in radii:
        tag = f"{int(round(rad)):04d}"
        re_p = os.path.join(run_dir, "waveforms", f"rpsi4_real_{tag}.txt")
        im_p = os.path.join(run_dir, "waveforms", f"rpsi4_imag_{tag}.txt")
        re_arr = safe_load_table(re_p, min_cols=6, tcol=0)
        im_arr = safe_load_table(im_p, min_cols=6, tcol=0)
        if re_arr is None or im_arr is None:
            continue
        n = min(len(re_arr), len(im_arr))
        t = re_arr[:n, 0]
        R_ar = r_areal_from_iso(float(rad))
        r_st = float(rstar_schw(R_ar))
        u = t - r_st
        spheres[float(rad)] = {
            "r_iso": float(rad),
            "R_areal": float(R_ar),
            "r_star": r_st,
            "t": t,
            "u": u,
            "re": re_arr[:n],
            "im": im_arr[:n],
        }
    return spheres


def ffi_strain_and_dh(u, psi4_c, omega_cut):
    """Fixed-frequency integration (Reisswig & Pollney 2011) of complex rPsi4 -> (rh, rdh/dt)."""
    n = len(u)
    if n < 8:
        return np.zeros_like(psi4_c), np.zeros_like(psi4_c)
    du = float(np.median(np.diff(u)))
    # Cosine taper on outer 3% to avoid wrap-around ringing when signal doesn't start/end at zero
    ntap = max(4, int(0.03 * n))
    win = np.ones(n, dtype=np.float64)
    tap = 0.5 * (1.0 - np.cos(math.pi * np.arange(ntap) / ntap))
    win[:ntap] = tap
    win[-ntap:] = tap[::-1]
    sig = psi4_c * win
    freqs = 2.0 * math.pi * np.fft.fftfreq(n, d=du)
    spec = np.fft.fft(sig)
    omega_eff = freqs.copy()
    low = np.abs(freqs) < omega_cut
    sgn = np.where(freqs >= 0.0, 1.0, -1.0)
    omega_eff[low] = sgn[low] * omega_cut
    # Psi4 = -d^2 h / dt^2 => tilde_dh = tilde_Psi4 / (i * w_eff), tilde_h = -tilde_Psi4 / w_eff^2
    dh = np.fft.ifft(spec / (1j * omega_eff))
    h = np.fft.ifft(-spec / (omega_eff ** 2))
    # Restore untapered amplitude only inside interior? Win=1 in interior already!
    return h, dh


def fit_eccentricity(t, R_arr, R0, dr_dt_ref):
    """Fit R(t) = R_base + slp * t + A cos(w_r t) + B sin(w_r t) post-trumpet (t >= 35 M)."""
    m = t >= min(35.0, 0.25 * float(t[-1]))
    if np.sum(m) < 20:
        return {"R_base": R0, "dR_dt_fit": dr_dt_ref, "e_nr": math.nan, "d_om_frac": 0.0, "vr_corr_factor": 1.0}
    tf = t[m]
    Rf = R_arr[m]
    w_r0 = (R0 ** (-1.5)) * math.sqrt(max(1.0 - 6.0 / R0, 0.02))

    def residuals(p):
        Rbase, slp, A, B, wr = p
        return (Rbase + slp * tf + A * np.cos(wr * tf) + B * np.sin(wr * tf)) - Rf

    p0 = [float(np.mean(Rf)), dr_dt_ref, 0.0, 0.0, w_r0]
    bounds = (
        [R0 - 0.5, -0.01, -0.5, -0.5, 0.4 * w_r0],
        [R0 + 0.5, +0.01, +0.5, +0.5, 1.8 * w_r0],
    )
    res = least_squares(residuals, p0, bounds=bounds)
    Rbase, slp, A, B, wr = [float(v) for v in res.x]
    amp = math.hypot(A, B)
    e_nr = amp / Rbase
    # Nonlinear Schwarzschild circular L_c correction: if Rbase > R0, initial u_y was too high
    # so omega must be scaled DOWN (d_om_frac < 0).
    if Rbase > 6.02 and R0 > 6.02:
        lc_r0 = math.sqrt((R0 * R0) / (R0 - 3.0))
        lc_rb = math.sqrt((Rbase * Rbase) / (Rbase - 3.0))
        d_om_frac = (lc_r0 / lc_rb) - 1.0
    else:
        d_om_frac = +0.5 * max(1.0 - 6.0 / R0, 0.05) * (A / R0)
    vr_corr = 1.0 - (wr * B) / dr_dt_ref if abs(dr_dt_ref) > 1e-12 else 1.0
    vr_corr = float(np.clip(vr_corr, 0.5, 2.0))
    if float(t[-1]) < 400.0 or abs(A) > 2.0 * abs(B):
        vr_corr = 1.0
    return {
        "R_base": Rbase,
        "dR_dt_fit": slp,
        "A_cos": A,
        "B_sin": B,
        "omega_r_fit": wr,
        "omega_r_schw": w_r0,
        "e_nr": e_nr,
        "d_om_frac": d_om_frac,
        "vr_corr_factor": vr_corr,
    }


def analyze_run(run_dir, fig_dir, fig_prefix):
    os.makedirs(fig_dir, exist_ok=True)
    with open(os.path.join(run_dir, "run_meta.json"), "r") as f:
        meta = json.load(f)
    name = meta["name"]
    R0 = float(meta["R0"])
    q = float(meta["q"])
    radii = [float(r) for r in meta["extraction_radii"]]

    # Load trajectories, horizon, constraints, nrpic
    traj = read_single_traj(os.path.join(run_dir, f"{name}.traj.bin"))
    tmet = read_single_trajmet(os.path.join(run_dir, f"{name}.trajmet.bin"))
    co0 = safe_load_table(os.path.join(run_dir, f"{name}.co_0.txt"), min_cols=5, tcol=1)
    hs = safe_load_table(os.path.join(run_dir, f"{name}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    z4c = safe_load_table(os.path.join(run_dir, f"{name}.z4c.user.hst"), min_cols=10, tcol=0)
    nrp = safe_load_table(os.path.join(run_dir, f"{name}.nrpic.hst"), min_cols=24, tcol=0)

    t_tr = traj[:, 0]
    x_p = traj[:, 2:5]
    u_p = traj[:, 5:8]
    if co0 is not None and len(co0) > 1:
        xbh = np.column_stack([
            np.interp(t_tr, co0[:, 1], co0[:, 2]),
            np.interp(t_tr, co0[:, 1], co0[:, 3]),
            np.interp(t_tr, co0[:, 1], co0[:, 4]),
        ])
    else:
        xbh = np.zeros_like(x_p)
    x_rel = x_p - xbh
    r_iso_t = np.linalg.norm(x_rel, axis=1)
    has_tmet = tmet is not None and len(tmet) > 1
    if has_tmet:
        gzz_t = np.interp(t_tr, tmet[:, 0], tmet[:, 11])
        R_ar_t = r_iso_t * np.sqrt(np.maximum(gzz_t, 1.0e-6))
    else:
        R_ar_t = r_areal_from_iso(r_iso_t)
    phi_orb = np.unwrap(np.arctan2(x_rel[:, 1], x_rel[:, 0]))
    om_orb = np.gradient(phi_orb, t_tr)
    dt_med = float(np.median(np.diff(t_tr))) if len(t_tr) > 1 else 0.1
    ks = max(1, int(round(1.3 / max(dt_med, 1.0e-6))))
    om_smooth = om_orb.copy()
    if len(t_tr) > 2 * ks + 2:
        om_smooth[ks:-ks] = (phi_orb[2 * ks:] - phi_orb[:-2 * ks]) / (t_tr[2 * ks:] - t_tr[:-2 * ks])
        om_smooth[:ks] = om_smooth[ks]
        om_smooth[-ks:] = om_smooth[-ks - 1]
    t_max = float(t_tr[-1])
    Lz_orb = x_rel[:, 0] * u_p[:, 1] - x_rel[:, 1] * u_p[:, 0]  # per unit bare mass
    m_bare = float(meta["m_bare"])
    J_orb = m_bare * Lz_orb
    # Pre-plunge inspiral slice for eccentricity & J_orb fits (stop before plunge R < 5.85 M)
    plunge_idx = np.where((t_tr > 20.0) & (R_ar_t < 5.85))[0]
    n_insp = int(plunge_idx[0]) if len(plunge_idx) > 0 else len(t_tr)
    n_insp = max(n_insp, min(len(t_tr), 10))
    t_ins = t_tr[:n_insp]
    R_ins = R_ar_t[:n_insp]
    om_sm_ins = om_smooth[:n_insp]
    J_ins = J_orb[:n_insp]
    t_ins_max = float(t_ins[-1])

    m_om = (t_ins >= min(35.0, 0.25 * t_ins_max)) & (t_ins <= max(t_ins_max - 1.5, 0.9 * t_ins_max))
    if np.sum(m_om) < 5:
        m_om = np.ones_like(t_ins, dtype=bool)
    om_min = float(np.min(np.abs(om_sm_ins[m_om])))
    om_max = float(np.max(np.abs(om_sm_ins[m_om])))
    e_omega = (math.sqrt(max(om_max, 1.0e-12)) - math.sqrt(max(om_min, 1.0e-12))) / (
        math.sqrt(max(om_max, 1.0e-12)) + math.sqrt(max(om_min, 1.0e-12))
    )
    R_om_min = float(max(om_max, 1.0e-12) ** (-2.0 / 3.0))
    R_om_max = float(max(om_min, 1.0e-12) ** (-2.0 / 3.0))
    R_om_avg = 0.5 * (R_om_min + R_om_max)

    # Load waveform extraction spheres before evolving analytical references so plunge/ringdown span is covered
    spheres = load_waveform_spheres(run_dir, radii)
    if not spheres:
        raise RuntimeError(f"No waveform files found in {run_dir}/waveforms")
    t_wf_end = max(float(sp["t"][-1]) for sp in spheres.values())
    t_ev_max = max(t_max, t_wf_end, 30.0) + 20.0

    ref = EMRIReferenceModel()
    ev_pn = ref.evolve_inspiral("3.5PN", R0=R0, q=q, t_max=t_ev_max, dt=0.25)
    ev_1sf = ref.evolve_inspiral("1SF", R0=R0, q=q, t_max=t_ev_max, dt=0.25)
    ev_2sf = ref.evolve_inspiral("2SF", R0=R0, q=q, t_max=t_ev_max, dt=0.25)

    # Eccentricity fit & next-iteration recommendation
    ecc_info = fit_eccentricity(t_ins, R_ins, R0, ref.initial_dr_dt(R0, q, model="1SF"))
    omega_scale_next = float(meta.get("omega_scale", 1.0)) * (1.0 + ecc_info["d_om_frac"])
    vr_scale_next = float(meta.get("vr_scale", 1.0)) * ecc_info["vr_corr_factor"]

    r_sorted = sorted(spheres.keys())
    u_min = max(spheres[r]["u"][0] for r in r_sorted)
    u_max = min(spheres[r]["u"][-1] for r in r_sorted)
    du = 0.25
    u_grid = np.arange(max(0.0, u_min), u_max - 0.5 * du, du)

    # Boyle-Mroue amplitude/phase 1/R_areal extrapolation on wave-zone spheres (r >= 27 M) for |m|==l
    idx_wz = [k for k, r in enumerate(r_sorted) if r >= 27.0]
    if len(idx_wz) < 2:
        idx_wz = list(range(len(r_sorted)))
    invR_wz = np.array([1.0 / spheres[r_sorted[k]]["R_areal"] for k in idx_wz])
    A_wz = np.vstack([np.ones_like(invR_wz), invR_wz]).T
    pinv_wz = np.linalg.pinv(A_wz)
    i_ref = int(np.argmin(np.abs(u_grid - min(150.0, 0.5 * float(u_grid[-1])))))

    extrap_modes = {}
    outer_modes = {}
    for l in range(2, 5):
        for m in range(-l, l + 1):
            col = lm_col(l, m)
            vals = np.zeros((len(r_sorted), len(u_grid)), dtype=np.complex128)
            for k, rad in enumerate(r_sorted):
                sp = spheres[rad]
                vr = np.interp(u_grid, sp["u"], sp["re"][:, col])
                vi = np.interp(u_grid, sp["u"], sp["im"][:, col])
                vals[k] = vr + 1j * vi
            outer_modes[(l, m)] = vals[-1]
            if len(idx_wz) >= 2 and abs(m) == l:
                sub = vals[idx_wz]
                amps = np.abs(sub)
                phs = np.unwrap(np.angle(sub), axis=1)
                for j in range(1, len(idx_wz)):
                    shift = 2.0 * math.pi * round((phs[j, i_ref] - phs[j - 1, i_ref]) / (2.0 * math.pi))
                    phs[j] -= shift
                a0 = (pinv_wz @ amps)[0]
                p0 = (pinv_wz @ phs)[0]
                extrap_modes[(l, m)] = np.maximum(a0, 0.0) * np.exp(1j * p0)
            else:
                extrap_modes[(l, m)] = vals[-1]

    # Fluxes F_E and F_J from FFI on extrapolated modes (l=2..4)
    om0 = float(meta["ic"]["omega_orb0"])
    F_E_nr = np.zeros_like(u_grid)
    F_J_nr = np.zeros_like(u_grid)
    # Check handedness sign of (2,2) waveform phase (+e^{-i w t} vs +e^{+i w t})
    phi22_raw = np.unwrap(np.angle(extrap_modes[(2, 2)]))
    dphi22_du = np.gradient(phi22_raw, u_grid)
    clean_mask = (u_grid >= min(90.0, 0.4 * u_grid[-1])) & (u_grid <= max(u_grid[-1] - 15.0, 0.9 * u_grid[-1]))
    w22_nr = np.abs(dphi22_du)

    h_modes, dh_modes = {}, {}
    for l in range(2, 5):
        for m in range(-l, l + 1):
            w_cut = 0.5 * max(abs(m), 1) * om0
            h_m, dh_m = ffi_strain_and_dh(u_grid, extrap_modes[(l, m)], w_cut)
            h_modes[(l, m)] = h_m
            dh_modes[(l, m)] = dh_m
            F_E_nr += (1.0 / (16.0 * math.pi)) * (np.abs(dh_m) ** 2)
            # Ensure positive J_flux for positive orbital angular momentum (check sign from phase)
            if m != 0:
                sgn_om = -1.0 if np.median(dphi22_du[clean_mask]) < 0 else +1.0
                F_J_nr += (1.0 / (16.0 * math.pi)) * m * sgn_om * np.imag(np.conj(h_m) * dh_m)

    # Quantitative NR vs PN/1SF/2SF summary on clean post-junk inspiral window [u_align .. u_hi]
    u_align = min(90.0, 0.45 * float(u_grid[-1]))
    u_hi = min(float(u_grid[-1]) - 15.0, t_ins_max) if u_grid[-1] > u_align + 20.0 else float(u_grid[-1])
    if u_hi <= u_align + 10.0:
        u_hi = float(u_grid[-1]) - 15.0 if u_grid[-1] > u_align + 20.0 else float(u_grid[-1])
    cm = (u_grid >= u_align) & (u_grid <= u_hi)
    if np.sum(cm) < 5:
        cm = np.ones_like(u_grid, dtype=bool)

    # Align phase at u_align
    phi_nr = np.unwrap(-np.angle(extrap_modes[(2, 2)])) if np.median(dphi22_du[cm]) < 0 else np.unwrap(np.angle(extrap_modes[(2, 2)]))
    phi_nr_al = phi_nr - np.interp(u_align, u_grid, phi_nr)

    def interp_model_phase_diff(ev):
        m_ph = np.unwrap(-np.angle(ev["rPsi4_22"]))
        ph_i = np.interp(u_grid, ev["t"], m_ph)
        ph_al = ph_i - np.interp(u_align, u_grid, ph_i)
        return phi_nr_al - ph_al

    dphi_pn = interp_model_phase_diff(ev_pn)
    dphi_1sf = interp_model_phase_diff(ev_1sf)
    dphi_2sf = interp_model_phase_diff(ev_2sf)

    # Noise floor measure: variance of high-l or pre-junk residuals & sphere spread
    amp22_med = float(np.median(np.abs(extrap_modes[(2, 2)][cm])))
    amp33_med = float(np.median(np.abs(extrap_modes[(3, 3)][cm])))
    amp44_med = float(np.median(np.abs(extrap_modes[(4, 4)][cm])))
    amp21_med = float(np.median(np.abs(extrap_modes[(2, 1)][cm])))
    fe_med = float(np.median(F_E_nr[cm]))
    fj_med = float(np.median(F_J_nr[cm]))

    amp_1sf_init = ref.mode_amps_1sf(R0, q=q)
    fe_1sf_med = float(np.median(np.interp(u_grid[cm], ev_1sf["t"], ev_1sf["F_E"])))
    fe_2sf_med = float(np.median(np.interp(u_grid[cm], ev_2sf["t"], ev_2sf["F_E"])))
    fe_pn_med = float(np.median(np.interp(u_grid[cm], ev_pn["t"], ev_pn["F_E"])))

    # Drag / angular-momentum balance check on pre-plunge inspiral
    t_bal = (t_ins >= min(60.0, 0.35 * t_ins_max)) & (t_ins <= max(t_ins_max - 5.0, 0.9 * t_ins_max))
    if np.sum(t_bal) >= 10:
        dJ_dt_orb = float(np.polyfit(t_ins[t_bal], J_ins[t_bal], 1)[0])
        gamma_orb = dJ_dt_orb / float(np.mean(J_ins[t_bal]))
        gamma_gw_1sf = -fe_1sf_med / (om0 * float(np.mean(J_ins[t_bal])))
    else:
        dJ_dt_orb, gamma_orb, gamma_gw_1sf = math.nan, math.nan, math.nan

    amp22_outer_med = float(np.median(np.abs(outer_modes[(2, 2)][cm])))
    t_merger_exc = float(t_tr[-1]) if (nrp is not None and len(nrp) > 0 and nrp.shape[1] >= 17 and nrp[-1, 16] > 0) else None
    pk_mask = u_grid >= u_align
    if np.any(pk_mask):
        u_pk_arr = u_grid[pk_mask]
        a_pk_arr = np.abs(extrap_modes[(2, 2)][pk_mask])
        k_pk = int(np.argmax(a_pk_arr))
        u_peak_22 = float(u_pk_arr[k_pk])
        amp22_peak = float(a_pk_arr[k_pk])
    else:
        u_peak_22, amp22_peak = math.nan, math.nan

    # Horizon drift
    dm_max = float(np.max(np.abs(hs[:, 2] - hs[0, 2]) / hs[0, 2])) if hs is not None and len(hs) > 0 else math.nan
    dah_end = float(2.0 * hs[-1, 11] / meta["dx_bh"]) if hs is not None and len(hs) > 0 else math.nan

    # Outer-pair extraction sphere convergence spread
    if len(r_sorted) >= 2:
        r_prev, r_last = r_sorted[-2], r_sorted[-1]
        spread_outer = float(np.median(np.abs(
            np.interp(u_grid[cm], spheres[r_prev]["u"], spheres[r_prev]["re"][:, lm_col(2, 2)])
            + 1j * np.interp(u_grid[cm], spheres[r_prev]["u"], spheres[r_prev]["im"][:, lm_col(2, 2)])
            - outer_modes[(2, 2)][cm]
        )) / max(amp22_med, 1e-12))
    else:
        spread_outer = math.nan

    summary = {
        "name": name,
        "t_max": t_max,
        "t_wf_end": float(t_wf_end),
        "t_merger_exc": t_merger_exc,
        "u_max": float(u_grid[-1]),
        "u_clean": [float(u_align), float(u_hi)],
        "R0": R0,
        "q": q,
        "e_NR": ecc_info["e_nr"],
        "e_Omega": e_omega,
        "R_Om_min": R_om_min,
        "R_Om_max": R_om_max,
        "R_Om_avg": R_om_avg,
        "omega_scale_rec": omega_scale_next,
        "vr_scale_rec": vr_scale_next,
        "dR_dt_fit": ecc_info["dR_dt_fit"],
        "dR_dt_1SF": ref.initial_dr_dt(R0, q, "1SF"),
        "abs_rPsi4_22_NR": amp22_med,
        "abs_rPsi4_22_outer": amp22_outer_med,
        "abs_rPsi4_22_1SF": float(amp_1sf_init[(2, 2)]),
        "u_peak_22": u_peak_22,
        "amp22_peak": amp22_peak,
        "abs_rPsi4_33_NR": amp33_med,
        "abs_rPsi4_33_1SF": float(amp_1sf_init[(3, 3)]),
        "abs_rPsi4_44_NR": amp44_med,
        "abs_rPsi4_44_1SF": float(amp_1sf_init[(4, 4)]),
        "abs_rPsi4_21_NR": amp21_med,
        "abs_rPsi4_21_1SF": float(amp_1sf_init[(2, 1)]),
        "F_E_NR": fe_med,
        "F_E_35PN": fe_pn_med,
        "F_E_1SF": fe_1sf_med,
        "F_E_2SF": fe_2sf_med,
        "F_J_NR": fj_med,
        "dJ_dt_orb": dJ_dt_orb,
        "gamma_orb": gamma_orb,
        "gamma_GW_1SF": gamma_gw_1sf,
        "dphi22_end_1SF": float(dphi_1sf[cm][-1]),
        "dphi22_end_2SF": float(dphi_2sf[cm][-1]),
        "dphi22_end_PN": float(dphi_pn[cm][-1]),
        "max_dM_AH": dm_max,
        "D_AH_cells": dah_end,
        "sphere_spread_outer": spread_outer,
    }
    sum_path = os.path.join(run_dir, "analysis_summary.json")
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("=== EMRI 1000:1 NR vs 3.5PN / 1SF / 2SF QUANTITATIVE COMPARISON ===")
    print(f"Run {name}: t_max={t_max:.1f} M, t_wf_end={t_wf_end:.1f} M, t_merger_exc={t_merger_exc}, u_clean=[{u_align:.1f}, {u_hi:.1f}] M, R0={R0:.2f} M, q={q:.1e}")
    print(f"Orbital e_Omega = {e_omega:.4f} (R_Om=[{R_om_min:.3f}, {R_om_max:.3f}], avg={R_om_avg:.3f}) | e_fit = {ecc_info['e_nr']:.4f} | dR/dt_fit={ecc_info['dR_dt_fit']:.3e} vs 1SF={summary['dR_dt_1SF']:.3e}")
    print(f"Next-iter recommendation: --omega-scale {omega_scale_next:.6f} --vr-scale {vr_scale_next:.6f}")
    print(f"Angular-momentum balance: dln J_orb/dt = {gamma_orb:+.3e} M^-1 vs GW (-F_J/J) = {gamma_gw_1sf:+.3e} M^-1")
    print(f"Horizon: max|dM_AH/M0| = {dm_max:.3e} | D_AH/dx = {dah_end:.1f} cells")
    print(f"|rPsi4_22|: extrap={amp22_med:.4e}, outer={amp22_outer_med:.4e} vs 1SF={summary['abs_rPsi4_22_1SF']:.4e} (ratio={amp22_med/summary['abs_rPsi4_22_1SF']:.4f}) | peak={amp22_peak:.4e} at u={u_peak_22:.1f} M")
    print(f"|rPsi4_33|: NR={amp33_med:.4e} vs 1SF={summary['abs_rPsi4_33_1SF']:.4e} (ratio={amp33_med/summary['abs_rPsi4_33_1SF']:.4f})")
    print(f"|rPsi4_44|: NR={amp44_med:.4e} vs 1SF={summary['abs_rPsi4_44_1SF']:.4e} (ratio={amp44_med/summary['abs_rPsi4_44_1SF']:.4f})")
    print(f"|rPsi4_21|: NR={amp21_med:.4e} vs 1SF={summary['abs_rPsi4_21_1SF']:.4e} (ratio={amp21_med/summary['abs_rPsi4_21_1SF']:.4f})")
    print(f"Energy Flux F_E: NR={fe_med:.4e} | 1SF={fe_1sf_med:.4e} ({fe_med/fe_1sf_med:.3f}x) | 2SF={fe_2sf_med:.4e} | 3.5PN={fe_pn_med:.4e}")
    print(f"Phase diff at u={u_hi:.1f} M (aligned u={u_align:.1f} M): dPhi(NR-1SF)={summary['dphi22_end_1SF']:+.4f} rad, dPhi(NR-2SF)={summary['dphi22_end_2SF']:+.4f} rad, dPhi(NR-PN)={summary['dphi22_end_PN']:+.4f} rad")

    # =========================================================================
    # FIGURE 1: GW vs PN / 1SF / 2SF Comparison (2 x 2 Cyclic-Zoom)
    # =========================================================================
    cz.use_style()
    fig = plt.figure(figsize=(11.6, 7.6))
    fig.subplots_adjust(left=0.085, right=0.965, bottom=0.085, top=0.895, wspace=0.28, hspace=0.33)
    axes = fig.subplots(2, 2)

    # Panel (0,0): Re(rPsi4_22) NR vs 1SF / 2SF / 3.5PN
    ax = axes[0, 0]
    scale5 = 1.0e5
    ax.axvspan(0.0, u_align, color="grey", alpha=0.12)
    nr22 = extrap_modes[(2, 2)]
    m_sgn = float(np.median(dphi22_du[cm]))
    k_al = int(np.argmin(np.abs(u_grid - u_align)))
    ang_nr_al = float(np.angle(nr22[k_al]))

    def align_model_22(ev):
        raw_c = np.conj(ev["rPsi4_22"]) if m_sgn > 0 else ev["rPsi4_22"]
        m_u = np.interp(u_grid, ev["t"], np.real(raw_c)) + 1j * np.interp(u_grid, ev["t"], np.imag(raw_c))
        rot = np.exp(1j * (ang_nr_al - float(np.angle(m_u[k_al]))))
        return np.real(m_u * rot)

    ax.plot(u_grid, scale5 * np.real(nr22), color=cz.PAL["blue"], lw=1.4, label=r"Full NR ($1/r$ extrap.)")
    psi22_1sf_u = align_model_22(ev_1sf)
    psi22_2sf_u = align_model_22(ev_2sf)
    psi22_pn_u = align_model_22(ev_pn)
    ax.plot(u_grid, scale5 * psi22_2sf_u, color=cz.PAL["red"], ls="--", lw=1.2, label="2SF (1PA)")
    ax.plot(u_grid, scale5 * psi22_1sf_u, color="k", ls=":", lw=1.2, label="1SF (RWZ)")
    ax.plot(u_grid, scale5 * psi22_pn_u, color=cz.PAL["green"], ls="-.", lw=1.0, alpha=0.8, label="3.5PN")
    ax.set_xlim(0.0, float(u_grid[-1]))
    ymax0 = max(float(np.max(np.abs(scale5 * psi22_1sf_u))) * 2.2, float(np.max(np.abs(scale5 * np.real(extrap_modes[(2, 2)][cm])))) * 1.4, 0.5)
    ax.set_ylim(-ymax0, ymax0)
    ax.set_xlabel(r"Retarded time $u\,[M]$")
    ax.set_ylabel(r"$10^5\,\mathrm{Re}\,r\Psi_4^{(2,2)}$")
    ax.legend(loc="upper right", ncol=2, fontsize=8.0, frameon=False)
    ax.set_title(r"Quadrupole $\mathrm{Re}\,r\Psi_4^{(2,2)}(u)$")

    # Panel (0,1): Multipole amplitudes |rPsi4^{(l,m)}| NR vs 1SF RWZ
    ax = axes[0, 1]
    ax.axvspan(0.0, u_align, color="grey", alpha=0.12)
    m_colors = [(2, 2, cz.PAL["blue"], r"$(2,2)$"), (3, 3, cz.PAL["red"], r"$(3,3)$"),
                (4, 4, cz.PAL["green"], r"$(4,4)$"), (2, 1, cz.PAL["orange"], r"$(2,1)$")]
    key_map = {(2, 2): "rPsi4_22", (3, 3): "rPsi4_33", (4, 4): "rPsi4_44", (2, 1): "rPsi4_21"}
    for l, m, col, lbl in m_colors:
        ax.plot(u_grid, np.clip(np.abs(extrap_modes[(l, m)]), 1e-9, None), color=col, lw=1.4, label=f"NR {lbl}")
        ax.plot(ev_1sf["t"], np.abs(ev_1sf[key_map[(l, m)]]), color=col, ls="--", lw=1.1, alpha=0.85, label=f"1SF {lbl}")
    ax.set_yscale("log")
    ax.set_xlim(0.0, float(u_grid[-1]))
    ax.set_ylim(5e-8, 2e-3)
    cz.no_minor_labels(ax, "y")
    ax.set_xlabel(r"Retarded time $u\,[M]$")
    ax.set_ylabel(r"$|r\Psi_4^{(\ell m)}|$")
    ax.legend(loc="upper right", ncol=2, fontsize=7.5, frameon=False)
    ax.set_title("Higher-multipole mode hierarchy")

    # Panel (1,0): Phase residual dPhi_22 & GW frequency w_22
    ax = axes[1, 0]
    ax.plot(u_grid[cm], dphi_2sf[cm], color=cz.PAL["red"], lw=1.5, label=r"$\Delta\Phi_{22}$ (NR $-$ 2SF)")
    ax.plot(u_grid[cm], dphi_1sf[cm], color="k", ls="--", lw=1.3, label=r"$\Delta\Phi_{22}$ (NR $-$ 1SF)")
    ax.plot(u_grid[cm], dphi_pn[cm], color=cz.PAL["green"], ls=":", lw=1.3, label=r"$\Delta\Phi_{22}$ (NR $-$ 3.5PN)")
    ax.axhline(0.0, color="grey", lw=0.8, alpha=0.6)
    ax.set_xlim(u_align, u_hi)
    ax.set_xlabel(r"Retarded time $u\,[M]$")
    ax.set_ylabel(r"GW phase residual $\Delta\Phi_{22}\,[\mathrm{rad}]$")
    loc_ph = "lower left" if summary["dphi22_end_1SF"] < -0.2 else "upper left"
    ax.legend(loc=loc_ph, fontsize=8.0, frameon=False)
    ax.set_title(rf"Phase residual (aligned at $u={u_align:.0f}\,M$)")

    # Panel (1,1): Radiated energy flux F_E(u)
    ax = axes[1, 1]
    scale10 = 1.0e10
    ax.axvspan(0.0, u_align, color="grey", alpha=0.12)
    ax.plot(u_grid, scale10 * F_E_nr, color=cz.PAL["blue"], lw=1.5, label=r"NR ($\ell=2..4$ FFI)")
    ax.plot(ev_2sf["t"], scale10 * ev_2sf["F_E"], color=cz.PAL["red"], ls="--", lw=1.3, label="2SF (1PA)")
    ax.plot(ev_1sf["t"], scale10 * ev_1sf["F_E"], color="k", ls=":", lw=1.3, label="1SF (RWZ)")
    ax.plot(ev_pn["t"], scale10 * ev_pn["F_E"], color=cz.PAL["green"], ls="-.", lw=1.1, label="3.5PN")
    ax.set_xlim(0.0, float(u_grid[-1]))
    ax.set_ylim(0.0, max(scale10 * max(fe_1sf_med, fe_med) * 2.2, 2.0))
    ax.set_xlabel(r"Retarded time $u\,[M]$")
    ax.set_ylabel(r"$10^{10}\,\mathcal{F}_E$")
    ax.legend(loc="upper right", ncol=2, fontsize=8.0, frameon=False)
    ax.set_title(rf"GW luminosity ($10^{{10}}\mathcal{{F}}_E$: NR={fe_med*1e10:.2f}, 1SF={fe_1sf_med*1e10:.2f})")

    for row in axes:
        for a in row:
            a.tick_params(which="both", direction="in", top=True, right=True)
    fig.suptitle(rf"{name}: Full 3+1 NR vs 3.5PN / 1SF / 2SF ($R_0={R0:.2f}\,M$, $q={q:.0e}$, $u_{{\max}}={u_grid[-1]:.1f}\,M$)", fontsize=12.0, y=0.96)
    gw_fig = os.path.join(fig_dir, f"fig_{fig_prefix}_gw_pn_2sf.png")
    fig.savefig(gw_fig, dpi=300)
    plt.close(fig)

    # =========================================================================
    # FIGURE 2: EMRI Orbit, Sphere Convergence, Horizon, & Drag Diagnostics (2 x 2)
    # =========================================================================
    fig = plt.figure(figsize=(11.6, 7.6))
    fig.subplots_adjust(left=0.085, right=0.965, bottom=0.085, top=0.895, wspace=0.32, hspace=0.33)
    axes = fig.subplots(2, 2)

    # (0,0) Orbital areal radius R(t) NR vs 1SF/2SF/PN + fit
    ax = axes[0, 0]
    r_lbl = r"NR $R_{\rm geom}(t)$" if has_tmet else r"NR $R_{\rm areal}(t)$"
    ax.plot(t_tr, R_ar_t, color=cz.PAL["blue"], lw=1.5, label=r_lbl)
    ax.plot(ev_1sf["t"], ev_1sf["R"], color="k", ls="--", lw=1.2, label="1SF (RWZ)")
    ax.plot(ev_2sf["t"], ev_2sf["R"], color=cz.PAL["red"], ls=":", lw=1.3, label="2SF (1PA)")
    ax.plot(ev_pn["t"], ev_pn["R"], color=cz.PAL["green"], ls="-.", lw=1.1, label="3.5PN")
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$")
    ax.set_ylabel(r"Areal separation $R\,[M]$")
    ax.legend(loc="best", ncol=2, fontsize=8.0, frameon=False)
    ax.set_title(rf"Inspiral orbit ($e_\Omega={e_omega:.4f}$, $e_{{\rm fit}}={ecc_info['e_nr']:.4f}$)")

    # (0,1) 5-sphere r_ext = 20..70 M Re(rPsi4_22) convergence
    ax = axes[0, 1]
    scols = [cz.PAL["green"], cz.PAL["orange"], cz.PAL["red"], cz.PAL["blue"], "k"]
    for idx_s, rad in enumerate(r_sorted):
        sp = spheres[rad]
        ax.plot(sp["u"], scale5 * sp["re"][:, lm_col(2, 2)], color=scols[idx_s % len(scols)], lw=1.1, alpha=0.85, label=rf"$r={rad:.0f}\,M$")
    ax.plot(u_grid, scale5 * np.real(extrap_modes[(2, 2)]), color="k", ls="--", lw=1.4, label=r"$1/r$ extrap.")
    ax.set_xlim(max(0.0, u_align), float(u_grid[-1]))
    ax.set_ylim(-ymax0, ymax0)
    ax.set_xlabel(r"Retarded time $u\,[M]$")
    ax.set_ylabel(r"$10^5\,\mathrm{Re}\,r\Psi_4^{(2,2)}$")
    ax.legend(loc="upper right", ncol=2, fontsize=7.5, frameon=False)
    ax.set_title("5-sphere extraction convergence")

    # (1,0) M_AH relative drift & D_AH
    ax = axes[1, 0]
    t_end_all = max(t_max, t_wf_end)
    if hs is not None and len(hs) > 0:
        dm_1e5 = (hs[:, 2] - hs[0, 2]) / hs[0, 2] * 1.0e5
        l1 = ax.plot(hs[:, 1], dm_1e5, color=cz.PAL["red"], lw=1.5, label=r"$\Delta M_{\rm AH}/M_0\,[10^{-5}]$")
        ax2 = ax.twinx()
        l2 = ax2.plot(hs[:, 1], 2.0 * hs[:, 11] / float(meta["dx_bh"]), color=cz.PAL["blue"], ls="--", lw=1.3, label=r"$D_{\rm AH}/\Delta x_{\rm BH}$")
        ax2.set_ylabel(r"Horizon cells $D_{\rm AH}/\Delta x_{\rm BH}$", color=cz.PAL["blue"])
        ax2.tick_params(axis="y", colors=cz.PAL["blue"], direction="in", which="both")
        lns = l1 + l2
        ax.legend(lns, [l.get_label() for l in lns], loc="best", fontsize=8.0, frameon=False)
    ax.set_xlim(0.0, t_end_all)
    ax.set_xlabel(r"Time $t\,[M]$")
    ax.set_ylabel(r"$\Delta M_{\rm AH}/M_0\,[10^{-5}]$")
    ax.set_title(rf"SMBH horizon ($\max|\Delta M/M_0|={dm_max:.2e}$)")

    # (1,1) Z4c constraint L2 norms & angular-momentum balance
    ax = axes[1, 1]
    if z4c is not None and len(z4c) > 1:
        tz = z4c[:, 0]
        ax.plot(tz, np.clip(z4c[:, 3], 1e-18, None), color=cz.PAL["red"], lw=1.4, label=r"$\|\mathcal{H}\|_2$")
        ax.plot(tz, np.clip(z4c[:, 4], 1e-18, None), color=cz.PAL["blue"], lw=1.4, label=r"$\|\mathcal{M}\|_2$")
        ax.plot(tz, np.clip(z4c[:, 9], 1e-18, None), color=cz.PAL["green"], ls=":", lw=1.4, label=r"$\|\Theta\|_2$")
        ax.set_yscale("log")
        ax.set_ylim(1.0e-18, 5.0e-1)
        cz.no_minor_labels(ax, "y")
    ax.set_xlim(0.0, t_end_all)
    ax.set_xlabel(r"Time $t\,[M]$")
    ax.set_ylabel(r"Z4c $L_2$ norm")
    ax.legend(loc="center right", fontsize=8.0, ncol=3, frameon=False)
    ax.text(
        0.04, 0.05,
        rf"$\dot L_z/L_z = {gamma_orb:+.2e}\,M^{{-1}}$ vs GW ${gamma_gw_1sf:+.2e}$" + "\n"
        + rf"Next $\omega$-scale={omega_scale_next:.5f}, $v_r$-scale={vr_scale_next:.3f}",
        transform=ax.transAxes, fontsize=8.0, va="bottom", ha="left",
    )
    ax.set_title("Constraints & orbital angular-momentum drag")

    for row in axes:
        for a in row:
            a.tick_params(which="both", direction="in", top=True, right=True)
    fig.suptitle(rf"{name}: Orbit, Waveform Extrapolation & Stability Diagnostics ($t={t_end_all:.1f}\,M$)", fontsize=12.0, y=0.96)
    diag_fig = os.path.join(fig_dir, f"fig_{fig_prefix}_diagnostics.png")
    fig.savefig(diag_fig, dpi=300)
    plt.close(fig)
    print(f"Wrote {gw_fig}, {diag_fig}, and {sum_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--fig-dir", default="/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/a654a4f4-a628-4c0f-9575-9ad989af8188")
    ap.add_argument("--fig-prefix", default="emri_it1")
    args = ap.parse_args()
    analyze_run(os.path.abspath(args.run_dir), os.path.abspath(args.fig_dir), args.fig_prefix)


if __name__ == "__main__":
    main()
