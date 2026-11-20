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

Wave 3 (JOURNAL.md entry 9): growth_fit_v2, the estimator with the fix of diagnosis D1.
growth_fit (above) is kept unchanged and selectable for comparison.

growth rate v2  d = y - y_ref (or y/y_ref - 1); y_ref a number (the model's equilibrium
                value as the probe samples it: probe_reference), an array on the record
                times (a control run), or 'first' (the old y(0)). Boxcar of width one
                oscillation period P (supplied, or measured by oscillation_period on d up
                to the first time |d| reaches hi); the boxcar has exactly that width
                (boxcar_exact: fractional end weights). Initial amplitude A_init = rms of the
                raw d over the first period; window from lo = k_lo A_init to hi (as
                growth_fit otherwise), at least one e-fold. sigma = slope of ln|d_s|;
                se = (se_noise^2 + se_fit^2)^(1/2): se_noise propagates white record noise
                (level std of the second difference of d / sqrt 6 over the window and its
                boxcar support; first differences, the entry-9 definition, let a steep
                trend in: test U5, JOURNAL entry 10) exactly through boxcar and slope, se_fit is
                growth_fit's inflated residual error with n_eff = window / width.
probe reference the central probe of the particle module (athenak/src/particles/
                nrpic_io.cpp:73-135) averages the lapse of the eight cells around the
                origin, a MeshBlock corner, i.e. at isotropic radius r_p = (sqrt 3/2) dx;
                a run started with `lapse = table` therefore reads alpha_table(r_p) at
                t = 0, not the model's alpha_c.
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


# ============================================================================ wave 3: fixed estimator
sys.path.insert(0, os.path.join(REPO, "python"))


def read_deck(path):
    """Sections of an AthenaK input file: {section: {key: value string}} (comments cut)."""
    out, sec = {}, None
    for line in open(path):
        s = line.split("#", 1)[0].strip()
        if not s:
            continue
        if s.startswith("<") and s.endswith(">"):
            sec = s[1:-1].strip()
            out.setdefault(sec, {})
            continue
        if "=" in s and sec is not None:
            k, v = s.split("=", 1)
            out[sec][k.strip()] = v.strip()
    return out


def find_deck(run_dir):
    import glob
    for pat in ("*.athinput", os.path.join("chain", "*.athinput")):
        c = sorted(glob.glob(os.path.join(run_dir, pat)))
        if c:
            return c[0]
    return None


def deck_mesh(deck):
    """Root spacing, refinement kind and the candidate finest spacings at the origin."""
    m = deck["mesh"]
    dx0 = (float(m["x1max"]) - float(m["x1min"])) / int(m["nx1"])
    kind = deck.get("mesh_refinement", {}).get("refinement", "none")
    levels = []
    for sec, kv in deck.items():
        if sec.startswith("refined_region"):
            inside = all(float(kv[f"x{i}min"]) < 0.0 < float(kv[f"x{i}max"]) for i in (1, 2, 3))
            if inside:
                levels.append(int(kv["level"]))
    lmax = max(levels) if levels else 0
    cand = [lmax]
    if kind == "adaptive":
        nl = int(deck["mesh_refinement"].get("num_levels", lmax + 1))
        cand = list(range(lmax, nl))
    return dict(dx_root=dx0, refinement=kind, static_level=lmax,
                candidates={L: dx0 / 2 ** L for L in cand})


def table_lapse(path):
    """r, alpha and the header alpha_c of a `.tab` file (python/nrpic/io.read_tab)."""
    from nrpic import io as nio
    r, _, a, com = nio.read_tab(path)
    hdr = {}
    for c in com:
        if "=" in c and not c.startswith("columns"):
            k, v = c.split("=", 1)
            try:
                hdr[k.strip()] = float(v.split()[0])
            except ValueError:
                pass
    return r, a, hdr


def probe_reference(table, dx):
    """Equilibrium lapse as the central probe reads it on a mesh of spacing dx at the
    origin: the table lapse at r_p = (sqrt 3/2) dx (module docstring)."""
    r, a, hdr = table_lapse(table)
    rp = 0.5 * np.sqrt(3.0) * dx
    return dict(alpha_ref=float(np.interp(rp, r, a)), r_p=float(rp), dx=float(dx),
                alpha_c=hdr.get("alpha_c"), table=table)


def run_probe_reference(run_dir, alpha0=None):
    """Probe reference of a run directory from its deck and table. For an adaptive mesh
    every candidate finest level is evaluated; the one closest to alpha0 (alpha_probe at
    t = 0) is chosen and the choice is reported."""
    dk = find_deck(run_dir)
    if dk is None:
        return None
    deck = read_deck(dk)
    tab = deck["problem"]["comp0_file"]
    if not os.path.isabs(tab):
        tab = os.path.join(run_dir, tab)
    mesh = deck_mesh(deck)
    rows = {L: probe_reference(tab, dx) for L, dx in mesh["candidates"].items()}
    if alpha0 is None or len(rows) == 1:
        L = mesh["static_level"] if mesh["static_level"] in rows else sorted(rows)[0]
    else:
        L = min(rows, key=lambda k: abs(rows[k]["alpha_ref"] - alpha0))
    out = dict(rows[L], level=L, deck=dk, lapse=deck["problem"].get("lapse"),
               refinement=mesh["refinement"],
               candidates={int(k): v["alpha_ref"] for k, v in rows.items()})
    if alpha0 is not None:
        out["alpha_probe_0"] = float(alpha0)
        out["probe_minus_ref"] = float(alpha0 - out["alpha_ref"])
    return out


def _periodogram(tt, dd, trend, freqs):
    """Residual sum of squares of dd against trend columns plus (sin, cos) at each
    frequency (vectorised least squares)."""
    Q, _ = np.linalg.qr(trend)
    r0 = dd - Q @ (Q.T @ dd)
    W = 2.0 * np.pi * np.asarray(freqs)
    S = np.sin(np.outer(tt, W))
    C = np.cos(np.outer(tt, W))
    S -= Q @ (Q.T @ S)
    C -= Q @ (Q.T @ C)
    a11, a12, a22 = np.sum(S * S, 0), np.sum(S * C, 0), np.sum(C * C, 0)
    b1, b2 = S.T @ r0, C.T @ r0
    det = a11 * a22 - a12 ** 2
    red = (a22 * b1 ** 2 - 2 * a12 * b1 * b2 + a11 * b2 ** 2) / np.where(det > 0, det, np.inf)
    return float(np.sum(r0 ** 2)) - red, r0


def oscillation_period(t, d, t_end=None, pmin=5.0, pmax=None, nfreq=600,
                       s_grid=tuple(np.geomspace(0.002, 0.5, 40))):
    """Period of the oscillation in d: least-squares periodogram over [t0, t_end] with a
    trend of columns 1, x, x^2 and either x^3 or e^{s t} (s on s_grid), the combination
    of smallest residual; periods from pmin to pmax (default 2/3 of the segment). The
    spacing of zero crossings of d minus the best trend is a cross-check."""
    t = np.asarray(t, float)
    d = np.asarray(d, float)
    keep = np.isfinite(d) & (t <= (t[-1] if t_end is None else t_end))
    tt, dd = t[keep], d[keep]
    T = float(tt[-1] - tt[0]) if len(tt) > 1 else 0.0
    pmax = (2.0 / 3.0) * T if pmax is None else pmax
    if len(tt) < 20 or pmax <= pmin:
        return dict(ok=False, reason=f"segment of {T:.1f} M too short for pmin = {pmin}")
    x = (tt - 0.5 * (tt[0] + tt[-1])) / (0.5 * T)
    base = [np.ones_like(x), x, x ** 2]
    trends = [("cubic", np.vstack(base + [x ** 3]).T)]
    for s in s_grid:
        e = np.exp(s * (tt - tt[-1]))
        trends.append((f"exp s={s:.4g}", np.vstack(base + [e]).T))
    f0 = np.linspace(1.0 / pmax, 1.0 / pmin, nfreq)
    best = None
    for name, tr in trends:
        rss, r0 = _periodogram(tt, dd, tr, f0)
        k = int(np.argmin(rss))
        if best is None or rss[k] < best[0]:
            best = (float(rss[k]), name, tr, k, float(np.sum(r0 ** 2)), r0)
    rss_min, name, tr, k, rss_trend, r0 = best
    df = f0[1] - f0[0]
    f1 = np.linspace(max(f0[k] - 2 * df, 1.0 / pmax), min(f0[k] + 2 * df, 1.0 / pmin), 161)
    rss1, _ = _periodogram(tt, dd, tr, f1)
    j = int(np.argmin(rss1))
    P = 1.0 / f1[j]
    # zero crossings of the detrended record, lightly smoothed (P/6)
    dt = float(np.median(np.diff(tt)))
    kk = max(1, int(round(P / 6.0 / dt)))
    rs = np.convolve(r0, np.ones(kk) / kk, mode="same")
    zc = tt[1:][np.sign(rs[1:]) != np.sign(rs[:-1])]
    p_zc = float(2.0 * np.median(np.diff(zc))) if len(zc) >= 3 else None
    at_edge = bool(P > 0.99 * pmax or P < 1.01 * pmin)
    return dict(ok=True, period=float(P), trend=name, rss_reduction=float(1.0 - rss1[j] / rss_trend),
                period_zero_crossings=p_zc, n_crossings=int(len(zc)), segment=[float(tt[0]), float(tt[-1])],
                pmin=float(pmin), pmax=float(pmax), at_edge=at_edge)


def boxcar_weights(dt, width):
    """Weights of a centred running mean of exactly `width` on records of step dt: the
    records as cells of width dt, full cells weight 1, the two end cells the fraction
    inside; normalised. (growth_fit's boxcar rounds the width to an odd number of
    records instead, which leaves 1/k of an oscillation of period `width`.)"""
    m = 0.5 * width / dt
    J = max(0, int(np.floor(m - 0.5)))
    f = m - (J + 0.5)
    w = np.ones(2 * J + 1)
    if f > 1e-12:
        w = np.concatenate([[f], w, [f]])
    return w / w.sum()


def boxcar_exact(t, y, width):
    """Centred running mean of exactly `width` on the median record step; edges dropped.
    Returns ts, ys and the weights."""
    t = np.asarray(t, float)
    dt = float(np.median(np.diff(t)))
    tt = np.arange(t[0], t[-1] + 0.5 * dt, dt)
    yy = np.interp(tt, t, y)
    w = boxcar_weights(dt, width)
    L = len(w)
    ys = np.convolve(yy, w, mode="valid")
    return tt[L // 2: len(tt) - L // 2], ys, w, tt, yy


def noise_level(x, order=2):
    """White-noise level of a record from differences of the given order (1: std(diff)/sqrt 2;
    2: std(second difference)/sqrt 6, which a smooth trend leaks into much less)."""
    x = np.asarray(x, float)
    if len(x) <= order + 1:
        return 0.0
    if order == 1:
        return float(np.std(np.diff(x)) / np.sqrt(2.0))
    return float(np.std(np.diff(x, 2)) / np.sqrt(6.0))


def growth_fit_v2(t, y, y_ref, period=None, k_lo=3.0, hi=0.1, relative=False, t_max=None,
                  width_factor=1.0, min_efolds=1.0, pmin=5.0, period_t_end=None, noise_order=2):
    """Growth rate with the fix of diagnosis D1 (module docstring, JOURNAL.md entry 9).
    Returns a dict; 'ok' False with a reason when no window exists."""
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    if isinstance(y_ref, str):
        if y_ref != "first":
            raise ValueError(y_ref)
        ref, ref_kind = float(y[0]), "first"
    elif np.ndim(y_ref) == 0:
        ref, ref_kind = float(y_ref), "value"
    else:
        ref, ref_kind = np.asarray(y_ref, float), "array"
        if ref.shape != y.shape:
            raise ValueError("array reference must have the shape of y")
    keep = np.isfinite(y) & (np.isfinite(ref) if ref_kind == "array" else True)
    if t_max is not None:
        keep &= t <= t_max
    t, y = t[keep], y[keep]
    if ref_kind == "array":
        ref = ref[keep]
    d = y / ref - 1.0 if relative else y - ref
    res = dict(k_lo=k_lo, hi=hi, relative=relative, ref_kind=ref_kind,
               ref=(float(ref) if ref_kind != "array" else None), width_factor=width_factor)
    if period is None:
        dm = np.convolve(d, np.ones(3) / 3.0, mode="same")
        big = np.nonzero(np.abs(dm) >= hi)[0]
        t_seg = float(t[big[0]]) if len(big) else float(t[-1])
        if period_t_end is not None:
            t_seg = period_t_end
        po = oscillation_period(t, d, t_end=t_seg, pmin=pmin)
        res["period_fit"] = po
        if not po["ok"]:
            res.update(ok=False, reason="period: " + po["reason"])
            return res
        P, src = po["period"], "measured"
    else:
        P, src = float(period), "supplied"
    width = width_factor * P
    res.update(period=P, period_source=src, width=width)
    ts, ds, wk, tt, yy = boxcar_exact(t, d, width)
    first = t <= t[0] + P
    A_init = float(np.sqrt(np.mean(d[first] ** 2)))
    lo = k_lo * A_init
    res.update(A_init=A_init, lo=lo)
    if not lo < hi * np.exp(-min_efolds):
        res.update(ok=False, reason=f"lo = {lo:.4g} leaves less than {min_efolds} e-fold below hi")
        return res
    big = np.nonzero(np.abs(ds) >= hi)[0]
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
    i0 = j
    tw, dw = ts[i0:i1 + 1], sgn * ds[i0:i1 + 1]
    if len(tw) < 4:
        res.update(ok=False, reason="window shorter than four points")
        return res
    A = np.vstack([np.ones_like(tw), tw]).T
    lnd = np.log(dw)
    coef, *_ = np.linalg.lstsq(A, lnd, rcond=None)
    resid = lnd - A @ coef
    n = len(tw)
    s2 = float(np.sum(resid ** 2) / max(n - 2, 1))
    Sxx = float(np.sum((tw - tw.mean()) ** 2))
    se_formal = float(np.sqrt(s2 / Sxx))
    n_eff = max((tw[-1] - tw[0]) / width, 2.0)
    se_fit = se_formal * float(np.sqrt(max(n / n_eff, 1.0)))
    # exact propagation of white record noise through the boxcar and the slope
    sup = yy[i0:i1 + len(wk)]
    s_n = noise_level(sup, noise_order)
    c = (tw - tw.mean()) / Sxx
    g = c / dw
    h = np.convolve(g, wk)
    se_noise = float(s_n * np.sqrt(np.sum(h ** 2)))
    sigma = float(coef[1])
    res.update(ok=True, sigma=sigma, se=float(np.hypot(se_noise, se_fit)), se_noise=se_noise,
               se_fit=se_fit, se_formal=se_formal, noise_level=s_n, sign=sgn,
               t_start=float(tw[0]), t_end=float(tw[-1]), n=n, n_eff=float(n_eff),
               efolds=float(np.log(dw[-1] / dw[0])), amp0=float(sgn * np.exp(coef[0])),
               rms_log_resid=float(np.sqrt(np.mean(resid ** 2))))
    res["curve"] = dict(ts=ts, ds=ds)
    return res


GRID_WIDTHS = (0.8, 1.0, 1.25)
GRID_KLO = (2.0, 3.0, 5.0)


def window_grid(t, y, y_ref, period, his, default_hi, widths=GRID_WIDTHS, k_los=GRID_KLO,
                relative=False, t_max=None):
    """growth_fit_v2 over widths x k_lo x hi (period supplied); the spread of the rates
    that exist is the window-choice error."""
    rows = []
    for wf in widths:
        for kl in k_los:
            for h in his:
                f = growth_fit_v2(t, y, y_ref, period=period, k_lo=kl, hi=h, relative=relative,
                                  t_max=t_max, width_factor=wf)
                rows.append(dict(width_factor=wf, k_lo=kl, hi=h, ok=f["ok"], sigma=f.get("sigma"),
                                 se=f.get("se"), t_start=f.get("t_start"), t_end=f.get("t_end"),
                                 reason=f.get("reason")))
    base = growth_fit_v2(t, y, y_ref, period=period, k_lo=3.0, hi=default_hi, relative=relative,
                         t_max=t_max)
    ss = np.array([r["sigma"] for r in rows if r["ok"]])
    out = dict(rows=rows, n=len(rows), n_ok=int(len(ss)))
    if len(ss) and base["ok"]:
        b = base["sigma"]
        out.update(default=b, min=float(ss.min()), max=float(ss.max()),
                   half_range=float(0.5 * (ss.max() - ss.min())),
                   max_rel_dev=float(np.max(np.abs(ss / b - 1.0))))
    return out


def slope_over(t, y, y_ref, period, t0, t1, relative=False, noise_order=2):
    """Slope of ln|d_s| over the fixed interval [t0, t1] (d and the one-period exact
    boxcar as in growth_fit_v2): used to fit a second observable over the time window of
    the first. Points where d_s changes sign are a failure (reported)."""
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    ref = float(y[0]) if (isinstance(y_ref, str) and y_ref == "first") else y_ref
    d = y / ref - 1.0 if relative else y - ref
    ts, ds, wk, tt, yy = boxcar_exact(t, d, period)
    sel = np.nonzero((ts >= t0) & (ts <= t1))[0]
    out = dict(t0=float(t0), t1=float(t1), period=float(period), n=int(len(sel)))
    if len(sel) < 4:
        out.update(ok=False, reason="fewer than four smoothed points in the interval")
        return out
    i0, i1 = int(sel[0]), int(sel[-1])
    tw, dsw = ts[i0:i1 + 1], ds[i0:i1 + 1]
    sgn = float(np.sign(dsw[-1]))
    if np.any(sgn * dsw <= 0):
        out.update(ok=False, reason="d_s changes sign inside the interval")
        return out
    dw = sgn * dsw
    lnd = np.log(dw)
    A = np.vstack([np.ones_like(tw), tw]).T
    coef, *_ = np.linalg.lstsq(A, lnd, rcond=None)
    resid = lnd - A @ coef
    n = len(tw)
    Sxx = float(np.sum((tw - tw.mean()) ** 2))
    se_formal = float(np.sqrt(np.sum(resid ** 2) / max(n - 2, 1) / Sxx))
    n_eff = max((tw[-1] - tw[0]) / period, 2.0)
    se_fit = se_formal * float(np.sqrt(max(n / n_eff, 1.0)))
    s_n = noise_level(yy[i0:i1 + len(wk)], noise_order)
    h = np.convolve(((tw - tw.mean()) / Sxx) / dw, wk)
    se_noise = float(s_n * np.sqrt(np.sum(h ** 2)))
    out.update(ok=True, sigma=float(coef[1]), se=float(np.hypot(se_noise, se_fit)), se_noise=se_noise,
               se_fit=se_fit, sign=sgn, t_start=float(tw[0]), t_end=float(tw[-1]),
               amp0=float(sgn * np.exp(coef[0])), efolds=float(np.log(dw[-1] / dw[0])),
               rms_log_resid=float(np.sqrt(np.mean(resid ** 2))), curve_ts=ts, curve_ds=ds)
    return out
