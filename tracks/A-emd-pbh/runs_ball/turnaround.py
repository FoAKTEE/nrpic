#!/usr/bin/env python3
"""Turnaround time of the tracked dust shells without a fit window (package runs_ball,
JOURNAL entry 13; the verifier's finding 6 in stage/G1/VERIFIER.md).

The exact R(tau) of a shell is a cycloid, R = A (1 - cos eta), tau + t0 = B (eta - sin eta),
even about its turnaround. Estimators of the turnaround proper time tau_ta and of R_max per
tracked particle, from the <label>_series.npz that compare.py writes (tau, R, Ri):

  V3     vertex of the parabola through the three records around the largest R (compare.py)
  P<k>   least-squares parabola over the 2k+1 records around the largest R (k = 2..8)
  S      smoothing spline, smoothing by generalized cross-validation
         (scipy.interpolate.make_smoothing_spline, lam = None), records 0 <= tau <= 2 tau_ta^ex;
         its maximum
  C      least-squares fit of the three-parameter cycloid (A, B, t0) to the records with
         0 <= tau <= 2 tau_ta^ex (expansion and its mirror); tau_ta = pi B - t0, R_max = 2 A
  C<W>   the same on |tau - tau_ta^ex| <= W (W = 2, 3, 4, 6, 8, 12 M): window study
  Cexp   the same on 0 <= tau <= tau_ta^ex (expansion only)
  O      R = s R_exact(tau - d) of the particle's own shell (free offset d and scale s), on
         the records of C; tau_ta = tau_ta^ex + d, R_max = s R_max^ex

    turnaround.py --run <dir>:<label>:<dx>:<gauge> [...] [--prep <dir with exact.json>]
                  --out <dir> [--figdir <dir>] [--synthetic] [--breakdown <run dir>:<label> ...]

--synthetic runs the estimator test T0 of entry 13 (exact core cycloid, shift 0.02 M, records
0.25 M apart, with and without a wiggle 1e-5 R_max sin(2 pi tau / 3 M)).
--breakdown lists, per criterion, the first time at which an SR-1 run broke down (raw files:
athena.log, cstat.hst, z4c.user.hst, nrpic.hst, tab/*.adm.*.tab, traj.bin).
Outputs: turnaround.json, turnaround_<label>.npz, figures fig_turnaround_windows,
fig_turnaround_particles, fig_turnaround_synthetic.
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
WINDOWS = (2.0, 3.0, 4.0, 6.0, 8.0, 12.0)
KS = (1, 2, 3, 4, 5, 6, 8)


# ------------------------------------------------------------------ models
def cycloid_R(tau, A, B, t0):
    q = (np.asarray(tau, dtype=float) + t0) / B
    eta = XE._solve_eta(np.clip(q, 0.0, 2 * math.pi), True)
    return 2.0 * A * np.sin(0.5 * eta) ** 2, eta, q


def fit_cycloid(tp, Rp, A0, B0, t00):
    """Least squares in (A, B, t0); analytic Jacobian. Returns (tau_ta, R_max, rms, ok)."""
    from scipy.optimize import least_squares

    def res(p):
        return cycloid_R(tp, *p)[0] - Rp

    def jac(p):
        A, B, t0 = p
        R, eta, q = cycloid_R(tp, A, B, t0)
        # dR/deta = A sin(eta); deta/dq = 1/(1 - cos eta)
        with np.errstate(divide="ignore", invalid="ignore"):
            g = A * np.sin(eta) / np.maximum(1.0 - np.cos(eta), 1e-300)
        return np.stack([R / A, -g * q / B, g / B], axis=1)
    try:
        r = least_squares(res, x0=[A0, B0, t00], jac=jac, x_scale=[A0, B0, B0], method="lm",
                          xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=400)
    except Exception:
        return np.nan, np.nan, np.nan, False
    A, B, t0 = r.x
    ok = bool(r.success) and B > 0 and A > 0
    return math.pi * B - t0, 2.0 * A, float(np.sqrt(np.mean(r.fun ** 2))), ok


def fit_offset_scale(tp, Rp, shell):
    """R = s R_exact(tau - d) of a one-shell expball.Shells; returns (d, s, rms, ok)."""
    from scipy.optimize import least_squares

    def res(p):
        d, s = p
        return s * shell.R(tp - d)[0] - Rp
    try:
        r = least_squares(res, x0=[0.0, 1.0], x_scale=[0.1, 1e-3], method="lm",
                          xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=400)
    except Exception:
        return np.nan, np.nan, np.nan, False
    return float(r.x[0]), float(r.x[1]), float(np.sqrt(np.mean(r.fun ** 2))), bool(r.success)


def parabola_k(tp, Rp, i, k):
    if i - k < 0 or i + k >= len(tp):
        return np.nan, np.nan
    c = np.polyfit(tp[i - k:i + k + 1] - tp[i], Rp[i - k:i + k + 1], 2)
    if c[0] >= 0:
        return np.nan, np.nan
    tt = -c[1] / (2.0 * c[0])
    return tp[i] + tt, float(np.polyval(c, tt))


def spline_max(tp, Rp):
    from scipy.interpolate import make_smoothing_spline
    from scipy.optimize import minimize_scalar
    try:
        sp = make_smoothing_spline(tp, Rp)
    except Exception:
        return np.nan, np.nan
    i = int(np.argmax(Rp))
    lo, hi = tp[max(i - 3, 0)], tp[min(i + 3, len(tp) - 1)]
    tt = np.linspace(lo, hi, 601)
    j = int(np.argmax(sp(tt)))
    a, b = tt[max(j - 1, 0)], tt[min(j + 1, len(tt) - 1)]
    r = minimize_scalar(lambda x: -float(sp(x)), bounds=(a, b), method="bounded",
                        options=dict(xatol=1e-10))
    return float(r.x), float(sp(r.x))


def estimate_particle(tp, Rp, shell):
    """All estimators for one particle (records sorted in tau, finite). Returns dict of
    (tau_ta, R_max) per estimator name."""
    out = {}
    tta, Rmx = float(shell.tau_ta[0]), float(shell.R_max[0])
    A0, B0, t00 = 0.5 * Rmx, float(shell.T0[0]), float(shell.age_i[0])
    i = int(np.argmax(Rp))
    if not (0 < i < len(Rp) - 1):
        return out
    for k in KS:
        out["V3" if k == 1 else f"P{k}"] = parabola_k(tp, Rp, i, k)
    full = (tp >= 0) & (tp <= 2 * tta)
    if full.sum() >= 8:
        out["S"] = spline_max(tp[full], Rp[full])
        a, b, rms, ok = fit_cycloid(tp[full], Rp[full], A0, B0, t00)
        out["C"] = (a, b) if ok else (np.nan, np.nan)
        out["C_rms"] = (rms, np.nan)
        d, s, rms2, ok2 = fit_offset_scale(tp[full], Rp[full], shell)
        out["O"] = (tta + d, s * Rmx) if ok2 else (np.nan, np.nan)
    hrec = float(np.median(np.diff(tp)))
    for W in WINDOWS:
        sel = np.abs(tp - tta) <= W
        if sel.sum() >= 6 and tp[sel][0] < tta < tp[sel][-1]:
            a, b, rms, ok = fit_cycloid(tp[sel], Rp[sel], A0, B0, t00)
            out[f"C{W:g}"] = (a, b) if ok else (np.nan, np.nan)
            # one-sided window: the record ends (or starts) inside it
            out[f"C{W:g}_onesided"] = (float(tp[sel][-1] < tta + W - 2 * hrec or tp[sel][0] > tta - W + 2 * hrec),
                                       np.nan)
    sel = (tp >= 0) & (tp <= tta)
    if sel.sum() >= 8:
        a, b, rms, ok = fit_cycloid(tp[sel], Rp[sel], A0, B0, t00)
        out["Cexp"] = (a, b) if ok else (np.nan, np.nan)
    return out


# ------------------------------------------------------------------ per run
def analyse_run(spec, ball, R1core):
    parts = spec.split(":")
    d, lab, dx = parts[0], parts[1], float(parts[2])
    gauge = parts[3] if len(parts) > 3 else "?"
    ser = np.load(os.path.join(d, f"{lab}_series.npz"))
    tau, R, Ri = ser["tau"], ser["R"], ser["Ri"]
    core = np.nonzero(Ri <= R1core)[0]
    per = []
    for p in core:
        tp, Rp = tau[:, p], R[:, p]
        ok = np.isfinite(tp) & np.isfinite(Rp)
        tp, Rp = tp[ok], Rp[ok]
        if len(tp) < 8:
            continue
        o = np.argsort(tp)
        tp, Rp = tp[o], Rp[o]
        keep = np.concatenate([[True], np.diff(tp) > 1e-12])
        tp, Rp = tp[keep], Rp[keep]
        sh = XE.Shells(ball, np.array([Ri[p]]))
        est = estimate_particle(tp, Rp, sh)
        if not est:
            continue
        jta = int(np.argmin(np.abs(tp - sh.tau_ta[0])))
        row = dict(R_i=float(Ri[p]), tau_ta_exact=float(sh.tau_ta[0]),
                   spacing=float(np.median(np.diff(tp[max(jta - 3, 0):jta + 4]))))
        for k, (a_, b_) in est.items():
            if k == "C_rms" or k.endswith("_onesided"):
                row[k] = a_
                continue
            row[k] = a_ - sh.tau_ta[0]
            row[k + "_dR"] = b_ / sh.R_max[0] - 1.0
        per.append(row)
    n = len(per)
    res = dict(label=lab, dx=dx, gauge=gauge, dir=d, n_core=n,
               traj_t_end_rel=float(np.nanmedian(np.nanmax(tau[:, core], axis=0))),
               record_spacing_at_turnaround=float(np.median([r["spacing"] for r in per])) if per else None,
               tau_ta_exact_mean=float(np.mean([r["tau_ta_exact"] for r in per])) if per else None)
    keys = sorted(set(k for r in per for k in r))
    arrays = {k: np.array([r.get(k, np.nan) for r in per], dtype=float) for k in keys}
    stats = {}
    res["onesided_fraction"] = {k[:-9]: float(np.nanmean(arrays[k])) for k in keys if k.endswith("_onesided")}
    # shell error and its slope near the turnaround: the local turnaround shift is
    # 8 B^2 d(eps)/d(tau) (entry 13); median over the core particles on a common tau grid
    tg = np.linspace(-8.0, 8.0, 161)
    E_, D_ = [], []
    for p in core:
        tp, Rp = tau[:, p], R[:, p]
        okp = np.isfinite(tp) & np.isfinite(Rp)
        if okp.sum() < 8:
            continue
        tp, Rp = tp[okp], Rp[okp]
        o = np.argsort(tp)
        tp, Rp = tp[o], Rp[o]
        sh = XE.Shells(ball, np.array([Ri[p]]))
        e = Rp / sh.R(tp)[0] - 1.0
        de = np.gradient(e, tp)
        x = tp - sh.tau_ta[0]
        E_.append(np.interp(tg, x, e, left=np.nan, right=np.nan))
        D_.append(np.interp(tg, x, 8.0 * sh.T0[0] ** 2 * de, left=np.nan, right=np.nan))
    if E_:
        with np.errstate(invalid="ignore"):
            res["eps_near_turnaround"] = dict(s=tg.tolist(), eps_median=np.nanmedian(np.array(E_), axis=0).tolist(),
                                              shift_median=np.nanmedian(np.array(D_), axis=0).tolist())
    if "C_rms" in arrays:
        stats["C_rms"] = dict(median=float(np.nanmedian(arrays["C_rms"])), max=float(np.nanmax(arrays["C_rms"])))
    for k in keys:
        if k.endswith("_dR") or k.endswith("_onesided") or k in ("R_i", "tau_ta_exact", "spacing", "C_rms"):
            continue
        dt, dr = arrays[k], arrays.get(k + "_dR", np.full(n, np.nan))
        okv = np.isfinite(dt)
        if not np.any(okv):
            continue
        stats[k] = dict(n=int(okv.sum()), dtau_mean=float(np.mean(dt[okv])), dtau_median=float(np.median(dt[okv])),
                        dtau_std=float(np.std(dt[okv])), dtau_sem=float(np.std(dt[okv]) / math.sqrt(okv.sum())),
                        dtau_maxabs=float(np.max(np.abs(dt[okv]))),
                        dRmax_rel_mean=float(np.nanmean(dr[okv])), dRmax_rel_maxabs=float(np.nanmax(np.abs(dr[okv]))))
    res["stats"] = stats
    # compare.py's own V3 (tta_num) for the record: same particles, same estimator
    if "tta_num" in ser.files:
        tn = ser["tta_num"][core]
        exact = XE.Shells(ball, Ri[core]).tau_ta
        okk = np.isfinite(tn)
        res["compare_py_V3_dtau_mean"] = float(np.mean(tn[okk] - exact[okk])) if np.any(okk) else None
    return res, arrays


# ------------------------------------------------------------------ synthetic test T0
def synthetic(ball, rng_seed=12345):
    sh = XE.Shells(ball, np.array([1.2]))
    tta = float(sh.tau_ta[0])
    rng = np.random.default_rng(rng_seed)
    out = []
    for wig in (0.0, 1e-5):
        for trial in range(8):
            ph = rng.uniform(0, 0.25)
            tp = np.arange(ph, 2 * tta, 0.25)
            d = 0.02
            Rp = sh.R(tp - d)[0]
            Rp = Rp * (1.0 + wig * np.sin(2 * math.pi * tp / 3.0 + rng.uniform(0, 2 * math.pi)))
            est = estimate_particle(tp, Rp, sh)
            row = dict(wiggle=wig, phase=ph, d=d)
            for k, (a, b) in est.items():
                if k != "C_rms":
                    row[k] = a - tta - d
            out.append(row)
    return out


# ------------------------------------------------------------------ SR-1 breakdown criteria
def first_nonfinite_or_big(arr, col, big=1e10):
    t = arr[:, 0]
    v = arr[:, col]
    nf = np.nonzero(~np.isfinite(v))[0]
    bg = np.nonzero(np.isfinite(v) & (np.abs(v) > big))[0]
    return (float(t[nf[0]]) if len(nf) else None), (float(t[bg[0]]) if len(bg) else None)


def read_hst_all(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        try:
            rows.append([float(x) for x in line.split()])
        except ValueError:
            continue
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


def breakdown(spec):
    d, lab = spec.split(":")[:2]
    out = dict(label=lab, dir=d)
    log = os.path.join(d, "athena.log")
    if os.path.exists(log):
        m = re.findall(r"non-positive or non-finite metric determinant at time\s*([-+0-9.eE]+)", open(log, errors="replace").read())
        out["athena_log_first_nonpositive_det"] = float(m[0]) if m else None
    cst = os.path.join(d, "ball.cstat.hst")
    if os.path.exists(cst):
        a = read_hst_all(cst)
        nf, bg = first_nonfinite_or_big(a, 8)
        out["cstat_Hmax_first_nonfinite"], out["cstat_Hmax_first_gt_1e10"] = nf, bg
        anynf = np.nonzero(~np.all(np.isfinite(a), axis=1))[0]
        out["cstat_any_column_first_nonfinite"] = float(a[anynf[0], 0]) if len(anynf) else None
        huge = np.nonzero(~np.all(np.isfinite(a) & (np.abs(a) < 1e30), axis=1))[0]
        out["cstat_any_column_first_nonfinite_or_gt_1e30"] = float(a[huge[0], 0]) if len(huge) else None
        g1 = np.nonzero(np.isfinite(a[:, 8]) & (a[:, 8] > 1.0))[0]
        out["cstat_Hmax_first_gt_1"] = float(a[g1[0], 0]) if len(g1) else None
    z = os.path.join(d, "ball.z4c.user.hst")
    if os.path.exists(z):
        a = read_hst_all(z)
        nf, bg = first_nonfinite_or_big(a, 3)       # [4]=H-norm2
        out["z4c_Hnorm2_first_nonfinite"], out["z4c_Hnorm2_first_gt_1e10"] = nf, bg
        anynf = np.nonzero(~np.all(np.isfinite(a), axis=1))[0]
        out["z4c_any_column_first_nonfinite"] = float(a[anynf[0], 0]) if len(anynf) else None
    h = os.path.join(d, "ball.nrpic.hst")
    if os.path.exists(h):
        a = read_hst_all(h)
        anynf = np.nonzero(~np.all(np.isfinite(a), axis=1))[0]
        out["nrpic_hst_first_nonfinite"] = float(a[anynf[0], 0]) if len(anynf) else None
        out["nrpic_hst_t_end"] = float(a[-1, 0])
    first_bad = None
    for f in sorted(glob.glob(os.path.join(d, "tab", "ball.adm.*.tab"))):
        with open(f) as fh:
            m = re.search(r"time=\s*([-+0-9.eE]+)", fh.readline())
        try:
            dat = np.loadtxt(f, comments="#", ndmin=2)
        except ValueError:
            dat = np.array([[np.nan]])
        if not np.all(np.isfinite(dat)):
            t = float(m.group(1)) if m else None
            first_bad = t if first_bad is None else min(first_bad, t)
    out["adm_line_first_nonfinite"] = first_bad
    tb = os.path.join(d, "ball.traj.bin")
    if os.path.exists(tb):
        a = np.fromfile(tb, dtype="<f8")
        a = a[:len(a) // 8 * 8].reshape(-1, 8)
        fin = np.all(np.isfinite(a[:, 2:]), axis=1)
        out["traj_last_record_t"] = float(a[-1, 0])
        bad = np.nonzero(~fin)[0]
        out["traj_first_nonfinite_t"] = float(a[bad[0], 0]) if len(bad) else None
    return out


# ------------------------------------------------------------------ figures
def figures(a, runs, arrays, syn):
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    outs = []
    gname = {"sr1": "SR-1", "sr2": "SR-2", "leak": "SR-1L"}
    col = {1.0: fs.PAL["yellow"], 0.5: fs.PAL["red"], 0.25: fs.PAL["blue"]}
    gauges = [g for g in ("sr1", "sr2", "leak") if any(r["gauge"] == g for r in runs)]
    # F1 window study: mean core dtau against the half-width of the window
    fig = plt.figure(figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.88, wspace=0.30)
    for j, g in enumerate(gauges):
        ax = fig.add_subplot(1, len(gauges), j + 1)
        for r in [r for r in runs if r["gauge"] == g and r["dx"] <= 0.5]:
            st = r["stats"]
            h = r["record_spacing_at_turnaround"] or 0.25
            c_ = col.get(r["dx"], "k")
            kk = [k for k in KS if ("V3" if k == 1 else f"P{k}") in st]
            ax.plot([k * h for k in kk], [st["V3" if k == 1 else f"P{k}"]["dtau_mean"] for k in kk], "o--",
                    color=c_, ms=3, lw=1.0, label=f"parabola, $\\Delta x={r['dx']:g}$")
            ww = [W for W in WINDOWS if f"C{W:g}" in st]
            yy = [st[f"C{W:g}"]["dtau_mean"] for W in ww]
            if "C" in st:
                ww, yy = ww + [r["tau_ta_exact_mean"]], yy + [st["C"]["dtau_mean"]]
            ax.plot(ww, yy, "-", color=c_, lw=1.6, label=f"cycloid, $\\Delta x={r['dx']:g}$")
            one = [r.get("onesided_fraction", {}).get(f"C{W:g}", 0.0) > 0.5 for W in WINDOWS if f"C{W:g}" in st]
            one += [r["traj_t_end_rel"] < 2.0 * r["tau_ta_exact_mean"] - 1.0] if "C" in st else []
            for x_, y_, o_ in zip(ww, yy, one):
                ax.plot([x_], [y_], "s", ms=4, color=c_, mfc="none" if o_ else c_)
            if "S" in st:
                ax.axhline(st["S"]["dtau_mean"], color=c_, lw=0.8, ls=":")
        ax.axhline(0.0, **fs.GUIDE)
        ax.set_xscale("log")
        ax.set_xlabel("half-width of the fit window (M)")
        if j == 0:
            ax.set_ylabel(r"core: mean $\tau_{\rm ta}-\tau_{\rm ta}^{\rm exact}$ (M)")
        ax.set_title(gname[g], fontsize=10)
        ax.legend(fontsize=6, loc="best")
    fig.suptitle("turnaround estimators against window (dotted: GCV spline, no window; last square: whole record)",
                 fontsize=8)
    outs += fs.save(fig, os.path.join(a.out, "fig_turnaround_windows"))
    plt.close(fig)

    # F2 per-particle values (V3 against C) and the resolution dependence
    fig = plt.figure(figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.90, wspace=0.32)
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    pick = [r for r in runs if r["gauge"] == "sr2" and r["dx"] == 0.25] or runs[:1]
    for r in pick:
        A = arrays[r["label"]]
        if "V3" in A:
            ax1.plot(A["R_i"], A["V3"], ".", color=fs.PAL["orange"], ms=3, label="V3 (three records)")
        if "C" in A:
            ax1.plot(A["R_i"], A["C"], ".", color=fs.PAL["blue"], ms=3, label="C (cycloid, whole record)")
        ax1.set_title(f"{gname.get(r['gauge'], r['gauge'])}, $\\Delta x={r['dx']:g}$: per particle", fontsize=9)
    ax1.axhline(0.0, **fs.GUIDE)
    ax1.set_xlabel(r"$R_i\,/M$ (core)")
    ax1.set_ylabel(r"$\tau_{\rm ta}-\tau_{\rm ta}^{\rm exact}$ (M)")
    ax1.legend(fontsize=6)
    mk = {"V3": "o", "C": "s", "S": "^", "O": "D"}
    for g in gauges:
        rr = sorted([r for r in runs if r["gauge"] == g], key=lambda r: r["dx"])
        for k in ("V3", "C"):
            xs = [r["dx"] for r in rr if k in r["stats"]]
            ys = [abs(r["stats"][k]["dtau_mean"]) for r in rr if k in r["stats"]]
            ax2.loglog(xs, ys, marker=mk[k], ls="-" if k == "C" else "--", lw=1.2, ms=4,
                       color={"sr1": fs.PAL["yellow"], "sr2": fs.PAL["blue"], "leak": fs.PAL["red"]}[g],
                       label=f"{gname[g]} {k}")
            ys2 = [abs(r["stats"][k]["dRmax_rel_mean"]) for r in rr if k in r["stats"]]
            ax3.loglog(xs, ys2, marker=mk[k], ls="-" if k == "C" else "--", lw=1.2, ms=4,
                       color={"sr1": fs.PAL["yellow"], "sr2": fs.PAL["blue"], "leak": fs.PAL["red"]}[g])
    xx = np.array([0.25, 1.0])
    ax2.loglog(xx, 0.02 * (xx / 0.25) ** 2, **fs.GUIDE)
    ax2.set_xlabel(r"$\Delta x\,/M$")
    ax2.set_ylabel(r"core: $|$mean $\tau_{\rm ta}$ error$|$ (M)")
    ax2.legend(fontsize=6, ncol=2)
    ax2.set_title("turnaround time (dashed: order 2)", fontsize=9)
    ax3.set_xlabel(r"$\Delta x\,/M$")
    ax3.set_ylabel(r"core: $|$mean $R_{\max}/R_{\max}^{\rm exact}-1|$")
    ax3.set_title("largest areal radius", fontsize=9)
    outs += fs.save(fig, os.path.join(a.out, "fig_turnaround_particles"))
    plt.close(fig)

    if syn:
        fig = plt.figure(figsize=(8.0, 3.0))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.88, wspace=0.30)
        for j, wig in enumerate((0.0, 1e-5)):
            ax = fig.add_subplot(1, 2, j + 1)
            rows = [s for s in syn if s["wiggle"] == wig]
            for row in rows:
                kk = [k for k in KS if ("V3" if k == 1 else f"P{k}") in row]
                ax.plot([0.25 * k for k in kk], [row["V3" if k == 1 else f"P{k}"] for k in kk], "o--",
                        color=fs.PAL["orange"], ms=2.5, lw=0.8)
                ww = [W for W in WINDOWS if f"C{W:g}" in row]
                ax.plot(ww + [16.9], [row[f"C{W:g}"] for W in ww] + [row.get("C", np.nan)], "s-",
                        color=fs.PAL["blue"], ms=3, lw=1.0)
            ax.axhline(0.0, **fs.GUIDE)
            ax.set_xscale("log")
            ax.set_xlabel("half-width of the fit window (M)")
            ax.set_ylabel(r"recovered minus true shift (M)")
            ax.set_title("exact cycloid, shift 0.02 M" + ("" if wig == 0 else r", wiggle $10^{-5}$, period 3 M"),
                         fontsize=9)
        fig.suptitle("synthetic test T0 (orange: parabolas; blue: cycloid fits; 8 random record phases)", fontsize=8)
        outs += fs.save(fig, os.path.join(a.out, "fig_turnaround_synthetic"))
        plt.close(fig)
    # F4 shell error and the local turnaround shift 8 B^2 d(eps)/d(tau) near the turnaround
    fig = plt.figure(figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.88, wspace=0.30)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    for r in runs:
        en = r.get("eps_near_turnaround")
        if not en or r["dx"] > 0.5:
            continue
        c_ = col.get(r["dx"], "k")
        ls = {"sr1": "--", "sr2": ":", "leak": "-"}[r["gauge"]]
        lab = f"{gname[r['gauge']]}, $\\Delta x={r['dx']:g}$"
        ax1.plot(en["s"], en["eps_median"], ls=ls, color=c_, lw=1.3, label=lab)
        ax2.plot(en["s"], en["shift_median"], ls=ls, color=c_, lw=1.3, label=lab)
    for ax in (ax1, ax2):
        ax.axvline(0.0, **fs.GUIDE)
        ax.axhline(0.0, **fs.GUIDE)
        ax.set_xlabel(r"$\tau-\tau_{\rm ta}^{\rm exact}$ (M)")
    ax1.set_ylabel(r"core: median $R/R_{\rm exact}-1$")
    ax2.set_ylabel(r"core: median $8B^2\,d\epsilon/d\tau$ (M)")
    ax2.set_ylim(-0.1, 0.1)
    ax1.legend(fontsize=6)
    ax1.set_title("shell error near the turnaround", fontsize=9)
    ax2.set_title("local shift of the maximum, $8B^2\\epsilon'$", fontsize=9)
    outs += fs.save(fig, os.path.join(a.out, "fig_turnaround_eps"))
    plt.close(fig)
    if a.figdir:
        import shutil
        os.makedirs(a.figdir, exist_ok=True)
        for f in outs:
            if f.endswith(".png"):
                shutil.copy(f, os.path.join(a.figdir, os.path.basename(f)))
    print("figures:", " ".join(os.path.basename(f) for f in outs if f.endswith(".png")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--prep", default=None, help="prep directory with exact.json (default data set 2t)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--breakdown", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(os.path.join(a.prep, "exact.json")) if a.prep else {}
    ball = C.ball_from_spec(ex.get("spec"))
    R1core = float(ex.get("core", {}).get("R1", 2.4))
    out = dict(estimators="JOURNAL entry 13", windows=list(WINDOWS), ks=list(KS))
    syn = synthetic(ball) if a.synthetic else None
    if syn is not None:
        out["synthetic"] = syn
        for wig in (0.0, 1e-5):
            rows = [s for s in syn if s["wiggle"] == wig]
            keys = sorted(set(k for r in rows for k in r if k not in ("wiggle", "phase", "d")))
            out[f"synthetic_maxabs_wiggle{wig:g}"] = {k: float(np.nanmax([abs(r.get(k, np.nan)) for r in rows]))
                                                      for k in keys}
    runs, arrays = [], {}
    for spec in a.run:
        r, arr = analyse_run(spec, ball, R1core)
        runs.append(r)
        arrays[r["label"]] = arr
        np.savez_compressed(os.path.join(a.out, f"turnaround_{r['label']}.npz"), **arr)
        st = r["stats"]
        print(f"[{r['label']}] n={r['n_core']} h={r['record_spacing_at_turnaround']}",
              " ".join(f"{k}={st[k]['dtau_mean']:+.4f}" for k in st if "dtau_mean" in st[k]))
    out["runs"] = runs
    if a.breakdown:
        out["breakdown"] = [breakdown(s) for s in a.breakdown]
        for b in out["breakdown"]:
            print("breakdown", b)
    C.write_json(os.path.join(a.out, "turnaround.json"), out)
    if runs or syn:
        figures(a, runs, arrays, syn)


if __name__ == "__main__":
    main()
