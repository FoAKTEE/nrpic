"""Growth rates, collapse times and oscillation growth of cluster runs of AthenaK's particle
module (analysis of AthenaK output only; decision 0010).

Inputs of a run directory D with basename B (as runs/st/* of the first paper):
    D/B.nrpic.hst               history of the particle module (central lapse alpha_probe,
                                particle number, removed rest mass), docs/FORMATS.md
    D/B.horizon_summary_0.txt   apparent-horizon finder summary (first row with a finite
                                mass = first apparent horizon)
    D/B.part.NNNNN.bin          particle snapshots (mass radii)
read with analysis/diag/common.py (restarts append: the last record of a time wins).

Definitions (fixed before the validation runs; JOURNAL.md, predictions G1-G6):

collapse time   t_AH: time of the first row of the horizon summary with a finite mass;
                t_alpha(L): first downward crossing of alpha_c = L, linear interpolation
                between records (a horizon-free proxy).
crossing time   first upward crossing of a level, linear interpolation between records (the
                rule of the first paper, paper/scripts/make_tables.first_cross).
growth rate     d(t) = y(t) - y(0) (y = alpha_c) or y(t)/y(0) - 1 (y = a mass radius);
                d is resampled on the median record step and smoothed by a centred boxcar
                of width w; the fit window ends at the first time |d_s| >= hi and starts
                at the last earlier time where |d_s| <= lo (so d_s keeps one sign inside);
                sigma is the least-squares slope of ln|d_s| against t in the window. Its
                standard error is the formal one inflated by sqrt(n/n_eff), n_eff the
                window length over w (smoothed points are correlated over w). A second
                estimator fits d = A e^{sigma t} + C to the unsmoothed records of the same
                window (scipy curve_fit).
half-swing      the first paper's oscillation growth (analysis/diag/cluster_osc.py, docstring
growth          of paper/scripts/make_tables.osc_fit): 4 M boxcar of alpha_c, extrema at
                least 15 M apart between 8 M and t_end - 4 M, half the difference of
                successive alternating extrema, straight-line fit against time.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "analysis", "diag"))

from common import H, read_horizon, read_nrpic_hst, read_snapshot, snapshot_files  # noqa: E402


# ---------------------------------------------------------------------------- reading
def load_run(d, base="st"):
    h = read_nrpic_hst(os.path.join(d, f"{base}.nrpic.hst"))
    ah = read_horizon(os.path.join(d, f"{base}.horizon_summary_0.txt"))
    return dict(dir=d, t=h[:, H["time"]], alpha=h[:, H["alpha_probe"]], np=h[:, H["np"]],
                sum_m=h[:, H["sum_m"]], m_exc=h[:, H["m_excised"]],
                ah_t=ah[:, 0] if len(ah) else np.zeros(0),
                ah_M=ah[:, 1] if len(ah) else np.zeros(0))


def mass_radii(d, base="st", qs=(0.1, 0.5, 0.9), tmax=None):
    """Snapshot times and coordinate radii about the origin enclosing the fractions qs of
    the rest mass present; de-duplicated in time (the last file of a time wins)."""
    rows = {}
    for p in snapshot_files(d, base):
        t, a, tag, _ = read_snapshot(p)
        if tmax is not None and t > tmax:
            continue
        if len(tag) == 0:
            rows[t] = np.full(len(qs), np.nan)
            continue
        m = a[:, 6]
        r = np.sqrt(np.sum(a[:, :3] ** 2, axis=1))
        o = np.argsort(r)
        F = np.cumsum(m[o]) / m.sum()
        rows[t] = np.interp(qs, F, r[o])
    T = np.array(sorted(rows))
    return T, np.array([rows[t] for t in T])


# ---------------------------------------------------------------------------- times
def first_crossing(t, y, level, direction=+1):
    """First crossing of `level` upward (direction +1) or downward (-1); linear
    interpolation between the two records; None if it never happens."""
    s = direction * (np.asarray(y, float) - level)
    idx = np.nonzero(s >= 0)[0]
    if len(idx) == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(t[0])
    return float(t[i - 1] + (t[i] - t[i - 1]) * (-s[i - 1]) / (s[i] - s[i - 1]))


def collapse_summary(run, levels=(0.3, 0.2, 0.1)):
    t, a = run["t"], run["alpha"]
    out = dict(t_final=float(t[-1]), alpha_0=float(a[0]), alpha_end=float(a[-1]),
               alpha_min=float(a.min()), np_start=int(run["np"][0]), np_end=int(run["np"][-1]))
    if len(run["ah_t"]):
        out.update(t_AH_first=float(run["ah_t"][0]), M_AH_first=float(run["ah_M"][0]),
                   t_AH_last=float(run["ah_t"][-1]), M_AH_last=float(run["ah_M"][-1]))
    else:
        out.update(t_AH_first=None, M_AH_first=None, t_AH_last=None, M_AH_last=None)
    out["t_alpha"] = {f"{L:g}": first_crossing(t, a, L, -1) for L in levels}
    return out


# ---------------------------------------------------------------------------- smoothing
def boxcar(t, y, width):
    """Centred running mean of width `width` on the median record step; edges dropped."""
    t = np.asarray(t, float)
    dt = float(np.median(np.diff(t)))
    tt = np.arange(t[0], t[-1] + 0.5 * dt, dt)
    yy = np.interp(tt, t, y)
    k = max(1, int(round(width / dt)))
    if k % 2 == 0:
        k += 1
    if k == 1:
        return tt, yy
    ys = np.convolve(yy, np.ones(k) / k, mode="valid")
    return tt[k // 2: len(tt) - k // 2], ys


# ---------------------------------------------------------------------------- growth rate
def growth_fit(t, y, width=10.0, lo=0.01, hi=0.1, relative=False, y_ref=None, t_max=None):
    """Exponential growth rate of the departure of y from its initial value (module
    docstring). Returns a dict; 'ok' False with a reason when no window exists."""
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    if t_max is not None:
        keep = t <= t_max
        t, y = t[keep], y[keep]
    ref = float(y[0] if y_ref is None else y_ref)
    d = y / ref - 1.0 if relative else y - ref
    ts, ds = boxcar(t, d, width)
    big = np.nonzero(np.abs(ds) >= hi)[0]
    res = dict(width=width, lo=lo, hi=hi, relative=relative, ref=ref)
    if len(big) == 0:
        res.update(ok=False, reason=f"|d_s| never reaches hi = {hi}")
        return res
    i1 = int(big[0])
    sgn = float(np.sign(ds[i1]))
    j = i1
    while j > 0 and sgn * ds[j - 1] > lo:
        j -= 1
    if j == 0 and sgn * ds[0] > lo:
        res.update(ok=False, reason="|d_s| above lo from the first smoothed point")
        return res
    i0 = j  # first point above lo (ds[j-1] <= lo)
    sl = slice(i0, i1 + 1)
    tw, dw = ts[sl], sgn * ds[sl]
    if len(tw) < 4:
        res.update(ok=False, reason="window shorter than four points")
        return res
    A = np.vstack([np.ones_like(tw), tw]).T
    coef, *_ = np.linalg.lstsq(A, np.log(dw), rcond=None)
    resid = np.log(dw) - A @ coef
    n = len(tw)
    s2 = float(np.sum(resid ** 2) / max(n - 2, 1))
    se_formal = float(np.sqrt(s2 / np.sum((tw - tw.mean()) ** 2)))
    n_eff = max((tw[-1] - tw[0]) / width, 2.0)
    se = se_formal * float(np.sqrt(max(n / n_eff, 1.0)))
    sigma = float(coef[1])
    res.update(ok=True, sigma=sigma, se=se, se_formal=se_formal, sign=sgn,
               t_start=float(tw[0]), t_end=float(tw[-1]), n=n, n_eff=float(n_eff),
               efolds=float(np.log(dw[-1] / dw[0])), amp0=float(sgn * np.exp(coef[0])),
               rms_log_resid=float(np.sqrt(np.mean(resid ** 2))))
    # second estimator: A e^{sigma t} + C on the unsmoothed records of the window
    try:
        from scipy.optimize import curve_fit
        w = (t >= tw[0]) & (t <= tw[-1])
        f = lambda x, a_, s_, c_: a_ * np.exp(s_ * (x - tw[0])) + c_  # noqa: E731
        p0 = (sgn * dw[0], sigma, 0.0)
        p, cov = curve_fit(f, t[w], d[w], p0=p0, maxfev=20000)
        res.update(sigma_nl=float(p[1]), se_nl=float(np.sqrt(cov[1, 1])), C_nl=float(p[2]))
    except Exception as e:  # noqa: BLE001
        res.update(sigma_nl=None, nl_error=str(e))
    res["curve"] = dict(ts=ts, ds=ds)
    return res


# ---------------------------------------------------------------------------- half-swing growth
def swing_growth(t, a, box=4.0, sep=15.0, t_lo=8.0, t_hi_margin=4.0):
    """The first paper's half-swing growth of alpha_c (module docstring)."""
    from scipy.signal import argrelextrema
    t = np.asarray(t, float)
    a = np.asarray(a, float)
    a0 = float(a[0])
    dt = float(np.median(np.diff(t)))
    n = max(3, int(round(box / dt)) | 1)
    sm = np.convolve(a, np.ones(n) / n, mode="same")
    order = max(2, int(round(sep / dt)))
    ext = sorted([(i, +1) for i in argrelextrema(sm, np.greater, order=order)[0]] +
                 [(i, -1) for i in argrelextrema(sm, np.less, order=order)[0]])
    ext = [(i, k) for i, k in ext if t_lo < t[i] < t[-1] - t_hi_margin]
    te, amp = [], []
    for (i0, k0), (i1, k1) in zip(ext[:-1], ext[1:]):
        if k0 != k1:
            te.append(t[i1])
            amp.append(0.5 * abs(sm[i1] - sm[i0]))
    p = np.polyfit(te, amp, 1)
    return dict(a0=a0, slope=float(p[0]), intercept=float(p[1]), n_pairs=len(te),
                extrema=[(float(t[i]), float(sm[i] - a0)) for i, _ in ext],
                t_pairs=[float(x) for x in te], half_swing=[float(x) for x in amp])
