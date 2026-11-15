#!/usr/bin/env python3
"""Comparison of an AthenaK run of the expanding ball (data set 2t) with the exact
solution, in invariants only (package runs_ball; gauge/DIAGNOSTICS.md section 3).

Measured, per tracked particle (tag < n_track of prep.py):
  - areal radius R = r sqrt(g_T) of the round sphere through the particle, from the metric
    reconstructed at it (<base>.trajmet.bin), against its own proper time tau (same file),
    compared with the exact radius of its own shell: eps = R / R_exact(tau) - 1;
  - turnaround: largest R and its proper time (parabola through the three records around
    the maximum) against the exact tau_ta and R_max of the shell;
  - trapping: the proper time at which R(tau) falls through 2 m (m the shell's exact
    Misner-Sharp mass, conserved before shell crossing) against the exact tau_AH;
  - crunch (shells of the homogeneous core): extrapolation of R^(3/2), linear in tau near
    R = 0, from the last records, against tau_c.
Along the mesh line y = z = dx/2 (formatted-table outputs of adm, z4c, con, tmunu):
  - Misner-Sharp mass m = (R/2)(1 + R^2 K_T^2 - (dR/dr)^2/g_rr) against the exact m of the
    shell at that point (shell label from the comoving coordinate in SR-1, from the
    tracked particles in other gauges), compactness 2m/R, trapped cells (2m/R > 1 with
    K_T > 0), the outermost marginally trapped sphere and its mass;
  - lapse, coordinate speed of light alpha/sqrt(g_rr), shift, Hamiltonian constraint.
Apparent-horizon finder (<base>.horizon_summary_0.txt): first time found, mass (column 3)
and the area mass sqrt(A/16 pi), against the exact horizon mass of the same slice: the
outermost shell whose proper time on the slice (from the tracked particles) has reached
its trapping time tau_AH(R_i).
Histories: central lapse, density and proper time (probe at the origin) against the exact
homogeneous core, a(tau) and rho_c(tau); constraint statistics; cost per cell and step.

    compare.py --prep <prep dir> --seg <run dir> [--seg <restart dir> ...] --gauge sr1|sr2
               --dx 0.5 --label <name> --out <dir> [--figdir <dir>]
"""
import argparse
import glob
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402

XE = C.XE


# ------------------------------------------------------------------ exact helpers
def exact_R(sh, tau):
    """Exact areal radius of every shell of `sh` at its own proper times tau[..., nshell]
    (last axis = shell); 0 after the crunch, NaN for NaN tau."""
    tau = np.asarray(tau, dtype=float)
    out = np.full(tau.shape, np.nan)
    m, E, T0, age = sh.m, sh.E, sh.T0, sh.age_i
    for k in range(len(m)):
        tk = tau[..., k]
        ok = np.isfinite(tk)
        if not np.any(ok):
            continue
        t = age[k] + tk[ok]
        if E[k] < 0:
            q = t / T0[k]
            eta = XE._solve_eta(np.clip(q, 0, 2 * math.pi), True)
            A = m[k] / (-2.0 * E[k])
            Rk = 2.0 * A * np.sin(0.5 * eta) ** 2
            Rk[q >= 2 * math.pi] = 0.0
        elif E[k] == 0:
            Rk = np.cbrt(4.5 * m[k]) * np.maximum(t, 0) ** (2.0 / 3.0)
        else:
            T0u = m[k] / (2.0 * E[k]) ** 1.5
            eta = XE._solve_eta(t / T0u, False)
            Rk = 2.0 * m[k] / (2.0 * E[k]) * np.sinh(0.5 * eta) ** 2
        col = out[..., k]
        col[ok] = Rk
        out[..., k] = col
    return out


def parabola_max(t, y, i):
    c = np.polyfit(t[i - 1:i + 2] - t[i], y[i - 1:i + 2], 2)
    if c[0] >= 0:
        return np.nan, np.nan
    tt = -c[1] / (2.0 * c[0])
    return t[i] + tt, np.polyval(c, tt)


def first_crossing_down(t, y, level, after=None):
    """First t at which y falls through `level` (linear interpolation), optionally only
    for t > after; NaN if none."""
    ok = np.isfinite(t) & np.isfinite(y)
    t, y = t[ok], y[ok]
    if after is not None:
        s = t > after
        t, y = t[s], y[s]
    d = y - level
    idx = np.nonzero((d[:-1] > 0) & (d[1:] <= 0))[0]
    if len(idx) == 0:
        return np.nan
    j = idx[0]
    return t[j] + (t[j + 1] - t[j]) * d[j] / (d[j] - d[j + 1])


# ------------------------------------------------------------------ cost from the logs
def cost_from_logs(segs):
    out = []
    for d in segs:
        for f in sorted(glob.glob(os.path.join(d, "athena.*.log"))):
            txt = open(f, errors="replace").read()
            cyc = re.findall(r"cycle=(\d+)", txt)
            zc = re.search(r"zone-cycles\s*=\s*([0-9.eE+]+)", txt)
            wall = re.search(r"(?:cpu|wall) time used\s*=\s*([0-9.eE+]+)", txt)
            zps = re.search(r"zone-cycles/(?:cpu|wall)_second\s*=\s*([0-9.eE+]+)", txt)
            out.append(dict(log=f, last_cycle=int(cyc[-1]) if cyc else None,
                            zone_cycles=float(zc.group(1)) if zc else None,
                            seconds=float(wall.group(1)) if wall else None,
                            zone_cycles_per_s=float(zps.group(1)) if zps else None,
                            terminated=("Terminating on" in txt or "terminated" in txt.lower())))
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--seg", action="append", required=True)
    ap.add_argument("--gauge", choices=("sr1", "sr2"), required=True)
    ap.add_argument("--dx", type=float, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    ap.add_argument("--base", default="ball")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ball = C.ball2t()
    tr = C.load_json(os.path.join(a.prep, "tracked.json"))
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    segs = [os.path.abspath(s) for s in a.seg]
    res = dict(label=a.label, gauge=a.gauge, dx=a.dx, segments=segs, prep=os.path.abspath(a.prep))

    # ------------------------------------------------ trajectories
    T = C.read_traj_many(segs, a.base)
    tags = T["tag"]
    ntr = tr["n_track"]
    keep = tags < ntr
    tags = tags[keep]
    for k in ("x", "u", "alpha", "beta", "g", "tau", "E"):
        T[k] = T[k][:, keep]
    t = T["time"]
    Ri = np.array(tr["R_i"])[tags]
    grp = np.array(tr["group"])[tags]
    sh = XE.Shells(ball, Ri)
    R, r, grr = C.areal_radius(T["x"], T["g"])
    tau = T["tau"]
    Rex = exact_R(sh, tau)
    with np.errstate(invalid="ignore", divide="ignore"):
        eps = R / Rex - 1.0
    r0 = np.array(tr["rbar0"])[tags]
    res["traj"] = dict(n_tracked=int(len(tags)), n_records=int(len(t)), t_first=float(t[0]),
                       t_last=float(t[-1]), n_alive_last=int(np.sum(np.isfinite(R[-1]))))
    if a.gauge == "sr1":
        with np.errstate(invalid="ignore"):
            res["sr1_coordinates"] = dict(
                max_abs_r_over_r0_minus_1=float(np.nanmax(np.abs(r / r0[None, :] - 1.0))),
                max_abs_tau_minus_t=float(np.nanmax(np.abs(tau - t[:, None]))),
                max_abs_u=float(np.nanmax(np.abs(T["u"]))))

    # groups: core (R_i <= 2.4, homogeneous), the target bands, the envelope
    core = Ri <= 2.4
    groups = {"core": core}
    for gname in sorted(set(grp), key=lambda s: (s == "sample", float(s[1:]) if s[0] == "R" else 0)):
        groups[gname] = grp == gname
    taus_report = (4.0, 8.0, 12.0, 16.894, 24.0, 30.0, 36.0, 40.0, 42.0, 43.5, 44.0, 44.3)

    def eps_at(idx, tq):
        vals = []
        for p in np.nonzero(idx)[0]:
            tp, ep = tau[:, p], eps[:, p]
            ok = np.isfinite(tp) & np.isfinite(ep)
            if ok.sum() > 1 and tp[ok][-1] >= tq and tp[ok][0] <= tq:
                vals.append(np.interp(tq, tp[ok], ep[ok]))
        return np.array(vals)

    G = {}
    for gname, idx in groups.items():
        if not np.any(idx):
            continue
        d = dict(n=int(idx.sum()), R_i_range=[float(Ri[idx].min()), float(Ri[idx].max())])
        for tq in taus_report:
            e = eps_at(idx, tq)
            if len(e):
                d[f"eps_tau{tq:g}"] = dict(mean=float(e.mean()), maxabs=float(np.abs(e).max()), n=int(len(e)))
        for tl in (30.0, 42.0, 44.3):
            sel = (tau <= tl)
            e = np.where(sel[:, idx], np.abs(eps[:, idx]), np.nan)
            d[f"maxabs_eps_tau_le_{tl:g}"] = C.finite_or_none(np.nanmax(e)) if np.any(np.isfinite(e)) else None
        G[gname] = d
    res["eps_groups"] = G

    # turnaround, trapping, crunch per particle
    tta_num, Rmax_num, tah_num, tc_num = (np.full(len(tags), np.nan) for _ in range(4))
    for p in range(len(tags)):
        tp, Rp = tau[:, p], R[:, p]
        ok = np.isfinite(tp) & np.isfinite(Rp)
        tp, Rp = tp[ok], Rp[ok]
        if len(tp) < 4:
            continue
        i = int(np.argmax(Rp))
        if 0 < i < len(Rp) - 1:
            tta_num[p], Rmax_num[p] = parabola_max(tp, Rp, i)
            tah_num[p] = first_crossing_down(tp, Rp, 2.0 * sh.m[p], after=tp[i])
        if core[p] and Rp[-1] < 0.12 * Ri[p] and i < len(Rp) - 4:
            y = Rp[-4:] ** 1.5
            c = np.polyfit(tp[-4:], y, 1)
            if c[0] < 0:
                tc_num[p] = -c[1] / c[0]
    bound = np.isfinite(sh.tau_ta)
    ev = {}
    for gname, idx in groups.items():
        s = idx & bound & np.isfinite(tta_num)
        d = {}
        if np.any(s):
            dt = tta_num[s] - sh.tau_ta[s]
            dR = Rmax_num[s] / sh.R_max[s] - 1.0
            d["turnaround"] = dict(n=int(s.sum()), dtau_mean=float(dt.mean()), dtau_maxabs=float(np.abs(dt).max()),
                                   rel_dtau_mean=float(np.mean(dt / sh.tau_ta[s])),
                                   rel_dtau_maxabs=float(np.max(np.abs(dt / sh.tau_ta[s]))),
                                   dRmax_rel_mean=float(dR.mean()), dRmax_rel_maxabs=float(np.abs(dR).max()),
                                   tau_ta_num_mean=float(tta_num[s].mean()), tau_ta_exact_mean=float(sh.tau_ta[s].mean()))
        s = idx & np.isfinite(tah_num) & np.isfinite(sh.tau_ah)
        if np.any(s):
            dt = tah_num[s] - sh.tau_ah[s]
            d["trapping"] = dict(n=int(s.sum()), dtau_mean=float(dt.mean()), dtau_maxabs=float(np.abs(dt).max()),
                                 tau_ah_num_min=float(tah_num[s].min()), tau_ah_exact_min=float(sh.tau_ah[s].min()))
        s = idx & np.isfinite(tc_num)
        if np.any(s):
            dt = tc_num[s] - sh.tau_c[s]
            d["crunch"] = dict(n=int(s.sum()), dtau_mean=float(dt.mean()), dtau_maxabs=float(np.abs(dt).max()))
        if d:
            ev[gname] = d
    # trapped by end of run: particles whose exact tau_ah < their last tau but which did not trap
    late = np.isfinite(sh.tau_ah) & (np.nanmax(tau, axis=0) > sh.tau_ah + 0.01) & ~np.isfinite(tah_num)
    ev["missed_trapping"] = int(late.sum())
    s = np.isfinite(tah_num)
    if np.any(s):
        k = int(np.nanargmin(np.where(s, tah_num, np.nan)))
        ev["first_trapped_tracked"] = dict(tau_num=float(tah_num[k]), tau_exact_same_shell=float(sh.tau_ah[k]),
                                           R_i=float(Ri[k]), m=float(sh.m[k]),
                                           tau_exact_first=ex["first_trapped"]["tau"])
    res["events"] = ev

    # ------------------------------------------------ histories
    hpath = os.path.join(segs[0], a.base + ".nrpic.hst")
    hst = np.concatenate([C.read_hst(os.path.join(d, a.base + ".nrpic.hst")) for d in segs
                          if os.path.exists(os.path.join(d, a.base + ".nrpic.hst"))])
    hst = hst[np.unique(hst[:, 0], return_index=True)[1]]
    cst = np.concatenate([C.read_hst(os.path.join(d, a.base + ".cstat.hst")) for d in segs
                          if os.path.exists(os.path.join(d, a.base + ".cstat.hst"))])
    cst = cst[np.unique(cst[:, 0], return_index=True)[1]]
    th, alpha_c, E_c, tau_c = hst[:, 0], hst[:, 12], hst[:, 13], hst[:, 14]
    a_ex = np.interp(tau_c, ex["central"]["tau"], ex["central"]["a"], right=np.nan)
    rho_ex = np.interp(tau_c, ex["central"]["tau"], ex["central"]["rho"], right=np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        lapse_dev = alpha_c / a_ex - 1.0 if a.gauge == "sr2" else alpha_c - 1.0
        rho_dev = E_c / rho_ex - 1.0
    res["history"] = dict(t_end=float(th[-1]), n_particles_end=float(hst[-1, 2]),
                          n_particles_start=float(hst[0, 2]), tau_probe_end=float(tau_c[-1]),
                          alpha_min_end=float(hst[-1, 15]),
                          finite_end=bool(np.all(np.isfinite(hst[-1]))))
    for tl in (5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 44.0):
        s = (th <= tl) & np.isfinite(lapse_dev)
        if np.any(s):
            res["history"][f"lapse_dev_maxabs_t_le_{tl:g}"] = float(np.nanmax(np.abs(lapse_dev[s])))
        s = (th <= tl) & np.isfinite(rho_dev)
        if np.any(s):
            res["history"][f"rho_c_dev_maxabs_t_le_{tl:g}"] = float(np.nanmax(np.abs(rho_dev[s])))
    # lapse front: first t at which |alpha_c/a - 1| exceeds 1e-3 and 1e-2
    for lev in (1e-3, 1e-2, 1e-1):
        s = np.nonzero(np.abs(lapse_dev) > lev)[0]
        res["history"][f"t_lapse_dev_gt_{lev:g}"] = float(th[s[0]]) if len(s) else None
    res["cstat"] = dict()
    for k, nm in ((9, "H_max"), (10, "H_mean"), (12, "Hr_mean"), (14, "M_mean"), (7, "Theta_max")):
        if cst.shape[1] > k:
            for tl in (2.0, 10.0, 20.0, 30.0, 40.0, 42.0, 44.0, 50.0):
                j = np.searchsorted(cst[:, 0], tl)
                if j < len(cst) and abs(cst[j, 0] - tl) < 0.3:
                    res["cstat"][f"{nm}_t{tl:g}"] = float(cst[j, k])
            res["cstat"][f"{nm}_end"] = float(cst[-1, k])

    # ------------------------------------------------ line profiles
    adm = C.read_tab_series(segs, "adm", a.base)
    zz = {rec["cycle"]: rec for rec in C.read_tab_series(segs, "z4c", a.base)}
    con = {rec["cycle"]: rec for rec in C.read_tab_series(segs, "con", a.base)}
    tmu = {rec["cycle"]: rec for rec in C.read_tab_series(segs, "tmunu", a.base)}
    lines = []
    nonfinite_t = []
    for rec in adm:
        x = C.line_points(rec, a.dx)
        pos = x[:, 0] > 0
        g = C.tensor6(rec, "adm_g")[pos]
        K = C.tensor6(rec, "adm_K")[pos]
        if not (np.all(np.isfinite(g)) and np.all(np.isfinite(K))):
            nonfinite_t.append(rec["time"])
            continue
        ms = C.misner_sharp_line(x[pos], g, K)
        # time of the line from the history (cycle) for precision
        tl = rec["time"]
        jh = np.nonzero(hst[:, 1] == rec["cycle"])[0]
        if len(jh):
            tl = float(hst[jh[-1], 0])
        # shell label of each line point
        if a.gauge == "sr1":
            rb0 = ms["r"]
        else:
            it = int(np.argmin(np.abs(t - tl)))
            rp = r[it]
            okp = np.isfinite(rp)
            o = np.argsort(rp[okp])
            rb0 = np.interp(ms["r"], rp[okp][o], r0[okp][o], left=np.nan, right=np.nan)
        Ri_line = ball.R_of_rbar(np.where(np.isfinite(rb0), rb0, 1.0))
        Ri_line = np.where(np.isfinite(rb0), np.minimum(Ri_line, ball.R_out), np.nan)
        m_ex = np.where(np.isfinite(Ri_line), ball.at(np.nan_to_num(Ri_line, nan=1.0))["m"], np.nan)
        L = dict(t=tl, cycle=rec["cycle"], r=ms["r"], R=ms["R"], m=ms["m"], compact=ms["compact"],
                 KT=ms["KT"], grr=ms["grr"], trapped=ms["trapped"], antitrapped=ms["antitrapped"],
                 m_exact=m_ex, R_i=Ri_line)
        if rec["cycle"] in zz:
            z = zz[rec["cycle"]]
            L["alpha"] = z["z4c_alpha"][pos]
            L["betax"] = z["z4c_betax"][pos]
        if rec["cycle"] in con:
            L["H"] = con[rec["cycle"]]["con_H"][pos]
        if rec["cycle"] in tmu:
            L["E"] = tmu[rec["cycle"]]["tmunu_E"][pos]
        # outermost marginally trapped sphere on the line
        tr_idx = np.nonzero(ms["trapped"])[0]
        if len(tr_idx):
            j = tr_idx.max()
            if j + 1 < len(ms["r"]):
                c0, c1 = ms["compact"][j], ms["compact"][j + 1]
                w = (c0 - 1.0) / (c0 - c1) if c0 != c1 else 0.0
                L["horizon"] = dict(r=float(ms["r"][j] + w * (ms["r"][j + 1] - ms["r"][j])),
                                    m=float(ms["m"][j] + w * (ms["m"][j + 1] - ms["m"][j])),
                                    R=float(ms["R"][j] + w * (ms["R"][j + 1] - ms["R"][j])),
                                    m_exact_shell=float(m_ex[j] + w * (m_ex[j + 1] - m_ex[j])))
        lines.append(L)
    # Misner-Sharp error summary
    # points with r >= 2 M (the Misner-Sharp mass is a small difference of O(1) terms,
    # 2m/R ~ 0.1 inside the ball, so the finite-difference error of dR/dr is amplified
    # by R/m: unreliable near the centre); drift: m(t)/m(0) - 1 on the same shell
    # (SR-1: the same mesh point), which removes the error of representing the slice
    msum = []
    m0 = lines[0]["m"] if lines else None
    for L in lines:
        s = (L["r"] >= 2.0) & np.isfinite(L["m_exact"]) & (L["R_i"] <= ball.R_out * 0.98)
        if np.any(s):
            rel = L["m"][s] / L["m_exact"][s] - 1.0
            drift = np.nan
            if a.gauge == "sr1" and m0 is not None and len(m0) == len(L["m"]):
                drift = float(np.nanmax(np.abs(L["m"][s] / m0[s] - 1.0)))
            msum.append((L["t"], float(np.nanmax(np.abs(rel))), float(np.nanmedian(np.abs(rel))), drift))
    res["misner_sharp"] = dict(
        n_lines=len(lines), r_min=2.0,
        max_rel_err=[dict(t=v[0], maxabs=v[1], median=v[2], drift_maxabs=v[3])
                     for v in msum[:: max(1, len(msum) // 40)]],
        maxabs_t0=msum[0][1] if msum else None,
        maxabs_t_le_42=float(max([v[1] for v in msum if v[0] <= 42.0], default=np.nan)),
        maxabs_t_le_30=float(max([v[1] for v in msum if v[0] <= 30.0], default=np.nan)),
        drift_maxabs_t_le_30=float(np.nanmax([v[3] for v in msum if v[0] <= 30.0] + [np.nan])),
        drift_maxabs_t_le_42=float(np.nanmax([v[3] for v in msum if v[0] <= 42.0] + [np.nan])),
        max_compactness_t0=float(np.nanmax(lines[0]["compact"])) if lines else None)
    hl = [L for L in lines if "horizon" in L]
    res["lines_nonfinite"] = dict(n=len(nonfinite_t), first_t=min(nonfinite_t) if nonfinite_t else None)
    # where the Hamiltonian residual on the line peaks (gauge pathologies)
    res["line_H_peak"] = [dict(t=L["t"], r=float(L["r"][int(np.nanargmax(np.abs(L["H"])))]),
                               H=float(np.nanmax(np.abs(L["H"]))),
                               E_there=float(L["E"][int(np.nanargmax(np.abs(L["H"])))]) if "E" in L else None)
                          for L in lines[:: max(1, len(lines) // 50)] if "H" in L and np.any(np.isfinite(L["H"]))]
    res["line_horizon"] = dict(
        first_t=hl[0]["t"] if hl else None,
        entries=[dict(t=L["t"], **L["horizon"]) for L in hl])

    # ------------------------------------------------ horizon finder
    hz = C.read_horizon(segs, a.base)
    finder = []
    for row in hz:
        th_, mass, area, rmean = row[1], row[2], row[7], row[10]
        mirr = math.sqrt(area / (16.0 * math.pi)) if area > 0 else np.nan
        # exact horizon of this slice: tracked particles' proper times on the slice
        it = int(np.argmin(np.abs(t - th_)))
        tp = tau[it]
        okp = np.isfinite(tp) & np.isfinite(sh.tau_ah) & (Ri > ex["first_trapped"]["R_i"] - 0.05)
        m_slice = np.nan
        Ri_h = np.nan
        if np.any(okp):
            o = np.argsort(Ri[okp])
            Rs, d = Ri[okp][o], (tp[okp] - sh.tau_ah[okp])[o]
            ms_ = sh.m[okp][o]
            # outermost sign change of d from >= 0 (trapped) to < 0, smoothing over particles
            # of nearly equal R_i by a running median of 9
            if len(d) > 9:
                dm = np.array([np.median(d[max(0, i - 4):i + 5]) for i in range(len(d))])
            else:
                dm = d
            pos = np.nonzero(dm >= 0)[0]
            if len(pos) and pos.max() + 1 < len(dm):
                j = pos.max()
                w = dm[j] / (dm[j] - dm[j + 1])
                Ri_h = Rs[j] + w * (Rs[j + 1] - Rs[j])
                m_slice = float(ball.at(np.array([Ri_h]))["m"][0])
        if a.gauge == "sr1":
            m_tau = float(np.interp(th_, ex["m_ah"]["tau"], ex["m_ah"]["m"], left=np.nan, right=np.nan))
        else:
            m_tau = np.nan
        # shell at the finder's mean coordinate radius
        if a.gauge == "sr1":
            rb_h = rmean
        else:
            rp = r[it]
            okr = np.isfinite(rp)
            o2 = np.argsort(rp[okr])
            rb_h = float(np.interp(rmean, rp[okr][o2], r0[okr][o2]))
        Ri_r = float(ball.R_of_rbar(np.array([rb_h]))[0])
        m_r = float(ball.at(np.array([Ri_r]))["m"][0])
        tau_h = float(np.interp(rmean, np.sort(r[it][np.isfinite(r[it])]),
                                tau[it][np.isfinite(r[it])][np.argsort(r[it][np.isfinite(r[it])])]))
        finder.append(dict(t=float(th_), mass=float(mass), m_irr=float(mirr), r_mean=float(rmean),
                           tau_at_horizon=tau_h, m_exact_slice=m_slice, R_i_exact_slice=float(Ri_h),
                           m_exact_tau_slice=m_tau, m_exact_shell_at_r=m_r, R_i_at_r=Ri_r))
    res["finder"] = dict(n=len(finder), first=finder[0] if finder else None,
                         rows=finder[:: max(1, len(finder) // 60)])
    if finder:
        for key in ("m_exact_slice", "m_exact_tau_slice", "m_exact_shell_at_r"):
            rel = np.array([f["m_irr"] / f[key] - 1.0 for f in finder if np.isfinite(f[key])])
            if len(rel):
                res["finder"][f"m_irr_rel_err_vs_{key}"] = dict(first=float(rel[0]), median=float(np.median(rel)),
                                                                maxabs=float(np.max(np.abs(rel))), n=int(len(rel)))
    res["cost"] = cost_from_logs(segs)

    # ------------------------------------------------ write numbers
    C.write_json(os.path.join(a.out, f"{a.label}_numbers.json"), res)
    np.savez_compressed(os.path.join(a.out, f"{a.label}_series.npz"), t=t, tau=tau, R=R, eps=eps, Ri=Ri,
                        tta_num=tta_num, tah_num=tah_num, tc_num=tc_num, hst=hst, cst=cst)

    # ------------------------------------------------ figures
    figures(a, res, ball, ex, t, tau, R, eps, Ri, grp, groups, sh, tta_num, Rmax_num, tah_num, tc_num,
            r, r0, hst, cst, lapse_dev, rho_dev, tau_c, lines, finder)
    print_summary(res)


def print_summary(res):
    ev = res["events"]
    print(f"[{res['label']}] traj records {res['traj']['n_records']}, t {res['traj']['t_first']:.3f} -> "
          f"{res['traj']['t_last']:.4f}, alive {res['traj']['n_alive_last']}/{res['traj']['n_tracked']}")
    if "sr1_coordinates" in res:
        print("  SR-1 coordinates:", res["sr1_coordinates"])
    c = res["eps_groups"].get("core", {})
    for k in ("eps_tau8", "eps_tau16.894", "eps_tau30", "eps_tau40", "eps_tau44"):
        if k in c:
            print(f"  core {k}: {c[k]}")
    for g in ("core", "R2.74", "R3"):
        if g in ev:
            print(f"  events {g}: {ev[g]}")
    print("  first trapped tracked:", ev.get("first_trapped_tracked"), "missed:", ev.get("missed_trapping"))
    print("  history:", {k: v for k, v in res["history"].items() if "t_lapse" in k or "end" in k})
    print("  Misner-Sharp max rel err t<=30:", res["misner_sharp"]["maxabs_t_le_30"],
          " t<=42:", res["misner_sharp"]["maxabs_t_le_42"])
    print("  line horizon first t:", res["line_horizon"]["first_t"])
    print("  finder first:", res["finder"]["first"])
    for k, v in res["finder"].items():
        if k.startswith("m_irr_rel"):
            print(f"  finder {k}: {v}")


def figures(a, res, ball, ex, t, tau, R, eps, Ri, grp, groups, sh, tta_num, Rmax_num, tah_num, tc_num,
            r, r0, hst, cst, lapse_dev, rho_dev, tau_c, lines, finder):
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    outs = []
    lab = a.label
    gcol = {}
    names = [g for g in groups if g != "sample"]
    cols = fs.series_colors(len(names), "viridis") if hasattr(fs, "series_colors") else None
    for i, g in enumerate(names):
        gcol[g] = cols[i] if cols is not None else None

    # ---- F1 shells
    fig = plt.figure(figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.90, wspace=0.28)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    for g in names:
        idx = np.nonzero(groups[g])[0]
        if g == "core" or len(idx) == 0:
            continue
        p = idx[0]
        ok = np.isfinite(tau[:, p]) & np.isfinite(R[:, p])
        ax1.plot(tau[ok, p], R[ok, p], color=gcol[g], lw=1.5, label=g.replace("R", "$R_i\\approx$"))
        tt = np.linspace(0, np.nanmax(tau[:, p]), 400)
        sp = XE.Shells(ball, np.array([Ri[p]]))
        ax1.plot(tt, sp.R(tt)[0], color="k", lw=0.8, ls="--")
        e = np.abs(eps[:, idx])
        tm = np.nanmedian(tau[:, idx], axis=1)
        with np.errstate(invalid="ignore"):
            ax2.semilogy(tm, np.nanmax(e, axis=1), color=gcol[g], lw=1.2)
    idx = np.nonzero(groups["core"])[0]
    if len(idx):
        e = np.abs(eps[:, idx])
        ax2.semilogy(np.nanmedian(tau[:, idx], axis=1), np.nanmax(e, axis=1), color=fs.PAL["red"], lw=2.0,
                     label="core (largest)")
        ax2.semilogy(np.nanmedian(tau[:, idx], axis=1), np.nanmedian(e, axis=1), color=fs.PAL["red"], lw=1.0,
                     ls=":", label="core (median)")
    ax1.axvline(ex["core"]["tau_ta"], **fs.MASK_LINE)
    ax1.set_xlabel(r"proper time $\tau\,/M$")
    ax1.set_ylabel(r"areal radius $R\,/M$")
    ax1.set_ylim(0, 12)
    ax1.legend(ncol=2, fontsize=7, loc="upper left")
    ax1.set_title(f"{lab}: shells (dashed: exact)", fontsize=10)
    ax2.axvline(ex["core"]["tau_ta"], **fs.MASK_LINE)
    ax2.axvline(ex["first_trapped"]["tau"], **fs.GUIDE)
    ax2.set_xlabel(r"proper time $\tau\,/M$")
    ax2.set_ylabel(r"$|R/R_{\rm exact}-1|$ (largest per band)")
    ax2.legend(fontsize=8, loc="upper left")
    ax2.set_ylim(1e-6, 1)
    outs += fs.save(fig, os.path.join(a.out, f"{lab}_shells"))
    plt.close(fig)

    # ---- F2 events
    fig = plt.figure(figsize=(8.0, 6.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.30, hspace=0.38)
    ax = fig.add_subplot(2, 2, 1)
    s = np.isfinite(tta_num) & np.isfinite(sh.tau_ta)
    ax.plot(Ri[s], tta_num[s] - sh.tau_ta[s], ".", color=fs.PAL["red"], ms=3)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$\tau_{\rm ta}-\tau_{\rm ta}^{\rm exact}\;(M)$")
    ax.set_title("turnaround time", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    ax.plot(Ri[s], Rmax_num[s] / sh.R_max[s] - 1.0, ".", color=fs.PAL["red"], ms=3)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$R_{\max}/R_{\max}^{\rm exact}-1$")
    ax.set_title("largest areal radius", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    s2 = np.isfinite(tah_num)
    if np.any(s2):
        ax.plot(Ri[s2], tah_num[s2] - sh.tau_ah[s2], ".", color=fs.PAL["red"], ms=3)
    ax.axhline(0, **fs.GUIDE)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$\tau_{\rm AH}-\tau_{\rm AH}^{\rm exact}\;(M)$")
    ax.set_title(r"trapping $R=2m$ per particle", fontsize=10)
    ax = fig.add_subplot(2, 2, 4)
    idx = np.nonzero(groups["core"])[0][:40]
    for p in idx:
        ok = np.isfinite(tau[:, p]) & np.isfinite(R[:, p])
        if ok.sum() > 3:
            ax.plot(tau[ok, p], (R[ok, p] / Ri[p]) ** 1.5, color=fs.PAL["red"], lw=0.6, alpha=0.6)
    tt = np.linspace(43.0, ex["core"]["tau_c"], 300)
    sp = XE.Shells(ball, np.array([1.0]))
    ax.plot(tt, (sp.R(tt)[0] / 1.0) ** 1.5, **fs.GUIDE)
    ax.axvline(ex["core"]["tau_c"], **fs.MASK_LINE)
    ax.axvline(ex["first_trapped"]["tau"], color="k", lw=1.0, ls=":")
    ax.set_xlim(43.0, 44.5)
    ax.set_ylim(0, 0.3)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$(R/R_i)^{3/2}$, core")
    ax.set_title("approach to the crunch", fontsize=10)
    outs += fs.save(fig, os.path.join(a.out, f"{lab}_events"))
    plt.close(fig)

    # ---- F3 Misner-Sharp
    if lines:
        fig = plt.figure(figsize=(8.0, 3.4))
        fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.90, wspace=0.30)
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        pick = [0]
        for tq in (16.9, 30.0, 42.0, 44.3, 44.4, 49.0, 52.0):
            j = int(np.argmin([abs(L["t"] - tq) for L in lines]))
            if abs(lines[j]["t"] - tq) < 1.0 and j not in pick:
                pick.append(j)
        pick.append(len(lines) - 1)
        pick = sorted(set(pick))
        cc = fs.series_colors(len(pick), "plasma") if hasattr(fs, "series_colors") else [None] * len(pick)
        for c_, j in zip(cc, pick):
            L = lines[j]
            ax1.plot(L["r"], L["m"], color=c_, lw=1.2, label=f"t={L['t']:.2f}")
            ax1.plot(L["r"], L["m_exact"], color="k", lw=0.7, ls="--")
            with np.errstate(invalid="ignore", divide="ignore"):
                ax2.semilogy(L["r"], np.abs(L["m"] / L["m_exact"] - 1.0), color=c_, lw=1.0)
            ax3.plot(L["R"], L["compact"], color=c_, lw=1.2)
        ax1.set_xlabel(r"coordinate radius $r\,/M$")
        ax1.set_ylabel(r"Misner-Sharp $m\,/M$")
        ax1.set_xlim(0, 14)
        ax1.legend(fontsize=7, loc="lower right")
        ax2.set_xlabel(r"$r\,/M$")
        ax2.set_ylabel(r"$|m/m_{\rm exact}-1|$")
        ax2.set_xlim(0, 12)
        ax2.set_ylim(1e-6, 1)
        ax3.axhline(1.0, **fs.GUIDE)
        ax3.set_xscale("log")
        ax3.set_xlabel(r"areal radius $R\,/M$")
        ax3.set_ylabel(r"$2m/R$")
        ax3.set_xlim(0.03, 40)
        ax1.set_title("mass profile on the line", fontsize=10)
        ax2.set_title("relative error", fontsize=10)
        ax3.set_title("compactness", fontsize=10)
        outs += fs.save(fig, os.path.join(a.out, f"{lab}_misner_sharp"))
        plt.close(fig)

    # ---- F4 horizon
    fig = plt.figure(figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.90, wspace=0.30)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    if finder:
        ft = np.array([f["t"] for f in finder])
        ax1.plot(ft, [f["m_irr"] for f in finder], "o-", color=fs.PAL["red"], ms=3, lw=1.0, label=r"finder $\sqrt{A/16\pi}$")
        ax1.plot(ft, [f["mass"] for f in finder], "x", color=fs.PAL["orange"], ms=4, label="finder column 3")
        ax1.plot(ft, [f["m_exact_slice"] for f in finder], "-", color=fs.PAL["blue"], lw=1.5,
                 label="exact, same slice")
        if a.gauge == "sr1":
            ax1.plot(ex["m_ah"]["tau"], ex["m_ah"]["m"], **fs.GUIDE, label=r"exact $m_{\rm AH}(\tau=t)$")
        with np.errstate(invalid="ignore", divide="ignore"):
            ax2.semilogy(ft, np.abs(np.array([f["m_irr"] / f["m_exact_slice"] - 1 for f in finder])), "o-",
                         color=fs.PAL["red"], ms=3, lw=1.0, label="finder vs exact slice")
    hl = [L for L in lines if "horizon" in L]
    if hl:
        ax1.plot([L["t"] for L in hl], [L["horizon"]["m"] for L in hl], "s", color=fs.PAL["green"], ms=3,
                 label="Misner-Sharp, line")
        with np.errstate(invalid="ignore", divide="ignore"):
            ax2.semilogy([L["t"] for L in hl],
                         [abs(L["horizon"]["m"] / L["horizon"]["m_exact_shell"] - 1) for L in hl], "s",
                         color=fs.PAL["green"], ms=3, label="line MS vs exact shell")
    ax2.axhline(1e-3, **fs.GUIDE)
    ax1.set_xlabel(r"coordinate time $t\,/M$")
    ax1.set_ylabel(r"horizon mass $/M$")
    ax1.legend(fontsize=7, loc="upper left")
    ax2.set_xlabel(r"$t\,/M$")
    ax2.set_ylabel("relative mass error")
    ax2.legend(fontsize=7)
    ax1.set_title(f"{lab}: apparent horizon", fontsize=10)
    ax2.set_title("dashed: source paper OS level 1e-3", fontsize=9)
    outs += fs.save(fig, os.path.join(a.out, f"{lab}_horizon"))
    plt.close(fig)

    # ---- F5 gauge
    fig = plt.figure(figsize=(8.0, 6.4))
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.08, top=0.95, wspace=0.34, hspace=0.38)
    ax = fig.add_subplot(2, 3, 1)
    ax.plot(hst[:, 0], hst[:, 12], color=fs.PAL["red"], label=r"$\alpha_c$")
    if a.gauge == "sr2":
        ax.plot(hst[:, 0], np.interp(tau_c, ex["central"]["tau"], ex["central"]["a"]), **fs.GUIDE,
                label=r"$a(\tau_c)$ exact")
    ax.plot(hst[:, 0], hst[:, 15], color=fs.PAL["blue"], lw=1.0, label=r"$\min\alpha$")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel("lapse")
    ax.legend(fontsize=7)
    ax.set_title("central lapse", fontsize=10)
    ax = fig.add_subplot(2, 3, 2)
    with np.errstate(invalid="ignore"):
        ax.semilogy(hst[:, 0], np.abs(lapse_dev), color=fs.PAL["red"], lw=1.0,
                    label=r"$|\alpha_c/a-1|$" if a.gauge == "sr2" else r"$|\alpha_c-1|$")
        ax.semilogy(hst[:, 0], np.abs(rho_dev), color=fs.PAL["blue"], lw=1.0, label=r"$|E_c/\rho_c-1|$")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel("deviation at the centre")
    ax.legend(fontsize=7)
    ax.set_title("centre vs homogeneous core", fontsize=10)
    ax = fig.add_subplot(2, 3, 3)
    for k, nm, c_ in ((10, r"mean $|H|$", fs.PAL["red"]), (9, r"max $|H|$", fs.PAL["orange"]),
                      (14, r"mean $|M|$", fs.PAL["blue"]), (7, r"max $|\Theta|$", fs.PAL["green"])):
        if cst.shape[1] > k:
            ax.semilogy(cst[:, 0], np.abs(cst[:, k]), color=c_, lw=1.0, label=nm)
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel("constraints")
    ax.legend(fontsize=7)
    ax.set_title("constraint statistics", fontsize=10)
    # spacetime maps along the line
    if lines and "alpha" in lines[0]:
        rr = lines[0]["r"]
        tl = np.array([L["t"] for L in lines])
        AL = np.array([L["alpha"] if len(L["alpha"]) == len(rr) else np.full(len(rr), np.nan) for L in lines])
        ax = fig.add_subplot(2, 3, 4)
        im = ax.pcolormesh(rr, tl, AL, shading="nearest", cmap="viridis", rasterized=True)
        fig.colorbar(im, ax=ax, label=r"$\alpha$")
        ax.set_xlim(0, 30)
        ax.set_xlabel(r"$x\,/M$")
        ax.set_ylabel(r"$t\,/M$")
        ax.set_title("lapse on the x axis", fontsize=10)
        CS = np.array([L["alpha"] / np.sqrt(L["grr"]) if len(L["alpha"]) == len(rr) else np.full(len(rr), np.nan)
                       for L in lines])
        ax = fig.add_subplot(2, 3, 5)
        cmax = np.nanmax(np.where(np.isfinite(CS), CS, np.nan)) if np.any(np.isfinite(CS)) else 10.0
        im = ax.pcolormesh(rr, tl, CS, shading="nearest", cmap="magma", norm=LogNorm(0.1, max(10.0, cmax)),
                           rasterized=True)
        fig.colorbar(im, ax=ax, label=r"$\alpha/\sqrt{\gamma_{rr}}$")
        ax.set_xlim(0, 30)
        ax.set_xlabel(r"$x\,/M$")
        ax.set_ylabel(r"$t\,/M$")
        ax.set_title("radial coordinate light speed", fontsize=10)
    if lines and "H" in lines[0]:
        rr = lines[0]["r"]
        tl = np.array([L["t"] for L in lines])
        HH = np.array([np.abs(L["H"]) if len(L["H"]) == len(rr) else np.full(len(rr), np.nan) for L in lines])
        ax = fig.add_subplot(2, 3, 6)
        HH = np.where(np.isfinite(HH), HH, np.nan)
        vmax = np.nanmax(HH) if np.any(np.isfinite(HH)) and np.nanmax(HH) > 0 else 1.0
        im = ax.pcolormesh(rr, tl, np.maximum(HH, vmax * 1e-6), shading="nearest", cmap="magma",
                           norm=LogNorm(vmax * 1e-6, vmax), rasterized=True)
        fig.colorbar(im, ax=ax, label=r"$|H|$")
        ax.set_xlim(0, 30)
        ax.set_xlabel(r"$x\,/M$")
        ax.set_ylabel(r"$t\,/M$")
        ax.set_title("Hamiltonian constraint", fontsize=10)
    outs += fs.save(fig, os.path.join(a.out, f"{lab}_gauge"))
    plt.close(fig)

    if a.figdir:
        import shutil
        os.makedirs(a.figdir, exist_ok=True)
        for f in outs:
            if f.endswith(".png"):
                shutil.copy(f, os.path.join(a.figdir, os.path.basename(f)))
    print("figures:", " ".join(os.path.basename(f) for f in outs if f.endswith(".png")))


if __name__ == "__main__":
    main()
