#!/usr/bin/env python3
"""Test D1 of drift/JOURNAL.md: the slow excursion of the collisionless King controls.

    python3 controls.py --out DIR NAME=RUNDIR [NAME=RUNDIR ...] [--pulsation]

NAME is cc1_kninf or cc2_kninf (it selects the model), RUNDIR an AthenaK output directory
(cc.nrpic.hst, cc.z4c.user.hst, cc.part.*.bin, cc.traj.bin, cc.trajmet.bin). Several
directories of one model (a run and its continuation) are given as NAME=DIR1,DIR2: their
records are joined in time order, later directories winning where times overlap.

Analysis only (decision 0010): readers of ../../threshold_scan/common.py, figure style
python/nrpic/figstyle.py. With --pulsation it also evaluates the lowest radial-pulsation
eigenvalue of the King family (b = 1 of gravothermal/tmb.py, as the lead's check L15, run
C-20261119-151502-cb831a8) with three adiabatic indices and converts it to a period in the
time at infinity, P/M = 2 pi / (omega_hat (1 - 2C)^(1/2) M_hat) (tmb returns omega^2 in the
proper time of a surface observer, gravothermal/README.md note V4), plus one proxy for the
collisionless mode: the F21 index scaled by the constant s that puts the onset at the
binding-energy maximum y0 = 0.334032 [JUDGEMENT: a proxy, not the Vlasov operator].

Writes DIR/controls.json and DIR/fig_drift_controls.png, fig_drift_fit.png (and
fig_drift_pulsation.png with --pulsation).
"""
import argparse
import glob
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
from scipy.optimize import curve_fit  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "threshold_scan"))
import common as C  # noqa: E402  (puts python/ on the path)

MODEL_OF = {"cc1": "king_y0p33403", "cc2": "king_y0p31400"}
FRACS = (0.1, 0.5, 0.9)


# ------------------------------------------------------------------------------ readers
def join_hst(dirs, fname):
    """Join the history `fname` of several directories; later directories win in time."""
    parts = [C.read_hst(os.path.join(d, fname)) for d in dirs if os.path.exists(os.path.join(d, fname))]
    if not parts:
        return None
    out = parts[0]
    names = list(out.keys())
    for i, p in enumerate(parts[1:], 1):
        # a run restarted into a new directory writes its NRPIC history without the header
        # line (nrpic_io.cpp NrpicStartup): the columns are those of the first directory
        if "time" not in p and "c1" in p:
            parts[i] = {names[j]: p[f"c{j + 1}"] for j in range(min(len(names), len(p)))}
    for p in parts[1:]:
        t1 = p["time"][0]
        keep = out["time"] < t1 - 1e-9
        out = {k: np.concatenate((out[k][keep], p[k])) for k in out if k in p}
    return out


def snapshots(dirs):
    """{time: path} of the particle snapshots, later directories winning."""
    snaps = {}
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "cc.part.*.bin"))):
            with open(p, "rb") as f:
                f.read(8)
                t = float(np.frombuffer(f.read(8), "<f8")[0])
            snaps[round(t, 6)] = p
    return dict(sorted(snaps.items()))


def traj_records(dirs):
    recs = {}
    for d in dirs:
        tj, tm = os.path.join(d, "cc.traj.bin"), os.path.join(d, "cc.trajmet.bin")
        if os.path.exists(tj) and os.path.exists(tm):
            for r in C.read_traj(tj, tm):
                recs[round(r["time"], 6)] = r
    return [recs[k] for k in sorted(recs)]


# ------------------------------------------------------------------------------ measures
def mass_radii(x, m):
    r = np.linalg.norm(x, axis=1)
    o = np.argsort(r)
    cm = np.cumsum(m[o])
    return [float(r[o][min(int(np.searchsorted(cm, f * cm[-1])), len(r) - 1)]) for f in FRACS], r, o


def areal_factor(rec):
    """sqrt of the angular part of gamma_ij at each particle: R_areal = r * this, from
    (tr gamma - rhat.gamma.rhat)/2 (exact for a conformally flat or spherically symmetric
    metric in these coordinates)."""
    g = rec["g"]
    x = rec["x"]
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    gxx, gxy, gxz, gyy, gyz, gzz = (g[:, i] for i in range(6))
    tr = gxx + gyy + gzz
    rr = (gxx * n[:, 0] ** 2 + gyy * n[:, 1] ** 2 + gzz * n[:, 2] ** 2
          + 2 * (gxy * n[:, 0] * n[:, 1] + gxz * n[:, 0] * n[:, 2] + gyz * n[:, 1] * n[:, 2]))
    return np.sqrt(0.5 * (tr - rr)), r


def shell_areal(rec, m):
    """Coordinate and areal radii of the shells enclosing FRACS of the rest mass: the areal
    radius is the mass-weighted mean of r * areal_factor over the 1000 particles closest in
    coordinate radius to the shell."""
    fac, r = areal_factor(rec)
    o = np.argsort(r)
    cm = np.cumsum(m[o])
    out_c, out_a = [], []
    for f in FRACS:
        k = min(int(np.searchsorted(cm, f * cm[-1])), len(r) - 1)
        sl = o[max(0, k - 500):k + 500]
        out_c.append(float(r[o][k]))
        out_a.append(float(np.average(r[sl] * fac[sl], weights=m[sl])))
    return out_c, out_a


# ------------------------------------------------------------------------------ fits
def f_cos(t, A, P, c):
    return A * (1.0 - np.cos(2.0 * np.pi * t / P)) + c


def f_sin(t, a, b, A, P, ph):
    return a + b * t + A * np.sin(2.0 * np.pi * t / P + ph)


def smooth(t, y, width):
    """Boxcar of `width` in time on a uniform record."""
    dt = np.median(np.diff(t))
    n = max(1, int(round(width / dt)))
    if n < 2 or len(y) < n:
        return y.copy()
    k = np.ones(n) / n
    ys = np.convolve(y, k, mode="same")
    h = n // 2
    ys[:h] = np.nan
    ys[-h:] = np.nan
    return ys


def fits(t, y):
    out = {}
    ok = np.isfinite(y)
    t, y = t[ok], y[ok]
    try:
        p, cov = curve_fit(f_cos, t, y, p0=(0.5 * np.nanmax(y), 2.0 * t[np.nanargmax(y)], 0.0), maxfev=20000)
        res = y - f_cos(t, *p)
        out["cos"] = dict(A=float(p[0]), P=float(p[1]), c=float(p[2]), sd=[float(v) for v in np.sqrt(np.diag(cov))],
                          rms=float(np.sqrt(np.mean(res ** 2))), peak_to_peak=float(2 * p[0]))
    except Exception as e:  # noqa: BLE001
        out["cos"] = dict(error=str(e))
    # windows: the period of the cosine model from fits that end at 200, 250 and 300 M
    out["cos_windows"] = {}
    for tend in (200.0, 250.0, 300.0, 400.0, 600.0, 800.0, 1000.0):
        if t[-1] < tend - 1e-6:
            continue
        w = t <= tend
        try:
            p, cov = curve_fit(f_cos, t[w], y[w], p0=(0.5 * np.nanmax(y), 2.0 * t[np.nanargmax(y)], 0.0), maxfev=20000)
            out["cos_windows"][f"{tend:g}"] = dict(A=float(p[0]), P=float(p[1]), c=float(p[2]),
                                                   sdP=float(np.sqrt(cov[1, 1])))
        except Exception as e:  # noqa: BLE001
            out["cos_windows"][f"{tend:g}"] = dict(error=str(e))
    try:
        p, cov = curve_fit(f_sin, t, y, p0=(0.0, 0.0, 0.5 * np.nanmax(y), 2.0 * t[np.nanargmax(y)], -np.pi / 2),
                           maxfev=40000)
        if p[2] < 0:
            p[2], p[4] = -p[2], p[4] + np.pi
        res = y - f_sin(t, *p)
        out["sin_trend"] = dict(a=float(p[0]), b=float(p[1]), A=float(p[2]), P=float(p[3]),
                                phase=float(np.mod(p[4], 2 * np.pi)),
                                sd=[float(v) for v in np.sqrt(np.diag(cov))], rms=float(np.sqrt(np.mean(res ** 2))))
    except Exception as e:  # noqa: BLE001
        out["sin_trend"] = dict(error=str(e))
    return out


def ripple(t, y, fit):
    """Dominant period of the residual of the cosine fit between 5 and 100 M (periodogram)."""
    if "P" not in fit.get("cos", {}):
        return {}
    ok = np.isfinite(y)
    res = y[ok] - f_cos(t[ok], fit["cos"]["A"], fit["cos"]["P"], fit["cos"]["c"])
    tt = t[ok]
    res = res - np.mean(res)
    periods = np.linspace(5.0, 100.0, 1901)
    pw = []
    for P in periods:
        w = 2 * np.pi / P
        pw.append(np.abs(np.sum(res * np.exp(-1j * w * tt))) ** 2)
    pw = np.array(pw) * 4.0 / len(res) ** 2
    k = int(np.argmax(pw))
    return dict(period=float(periods[k]), amplitude=float(np.sqrt(pw[k])), rms=float(np.std(res)),
                periods=periods.tolist(), power=pw.tolist())


def corr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


# ------------------------------------------------------------------------------ one run
def analyse(name, dirs, model):
    meta = model["meta"]
    h = join_hst(dirs, "cc.nrpic.hst")
    z = join_hst(dirs, "cc.z4c.user.hst")
    t = h["time"]
    ap = h["alpha_probe"]
    out = dict(name=name, dirs=dirs, t_end=float(t[-1]), records=int(len(t)))
    out["alpha_c_model"] = meta["alpha_c"]
    out["alpha_c0"] = float(ap[0])
    y = ap - ap[0]
    ys = smooth(t, y, 20.0)
    k = int(np.nanargmax(ys))
    out["excursion_max_smoothed"] = float(ys[k])
    out["t_of_max_smoothed"] = float(t[k])
    out["excursion_max_raw"] = float(np.nanmax(y))
    out["t_of_max_raw"] = float(t[int(np.nanargmax(y))])
    for tt in (100.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0):
        if tt <= t[-1] + 1e-9:
            w = np.abs(t - tt) <= 5.0
            out[f"excursion_mean_t{tt:g}pm5"] = float(np.mean(y[w]))
    out["fraction_left_at_end"] = float(np.mean(y[t >= t[-1] - 5.0]) / out["excursion_max_smoothed"])
    out["fits"] = fits(t, y)
    rp = ripple(t, y, out["fits"])
    out["ripple"] = {k_: v for k_, v in rp.items() if k_ not in ("periods", "power")}
    # bookkeeping
    out["np_min_max"] = [int(h["np"].min()), int(h["np"].max())]
    out["sum_m_identical"] = bool(np.all(h["sum_m"] == h["sum_m"][0]))
    meanW = h["sum_mW"] / h["sum_m"]
    out["meanW_0_min_max_end"] = [float(meanW[0]), float(meanW.min()), float(meanW.max()), float(meanW[-1])]
    out["corr_alpha_meanW"] = corr(y, meanW)
    out["alpha_min_grid_min"] = float(h["alpha_min"].min())
    out["push_unconverged_total"] = int(np.sum(h["push_unconverged"]))
    zt = z["time"]
    Hn = z["H-norm2"]
    yz = np.interp(zt, t, y)
    out["H_norm2_0_max_end"] = [float(Hn[0]), float(Hn.max()), float(Hn[-1])]
    out["corr_alpha_Hnorm2"] = corr(yz, Hn)
    out["M_norm2_0_max_end"] = [float(z["M-norm2"][0]), float(z["M-norm2"].max()), float(z["M-norm2"][-1])]
    # snapshots: coordinate mass radii
    sn = snapshots(dirs)
    ts, rr = [], []
    for tt, p in sn.items():
        s = C.read_snapshot(p)
        rad, _, _ = mass_radii(s["x"], s["m"])
        ts.append(tt)
        rr.append(rad)
    ts, rr = np.array(ts), np.array(rr)
    out["radii_t"] = ts.tolist()
    out["radii"] = rr.tolist()
    ys_ = np.interp(ts, t, y)
    out["corr_alpha_r10"] = corr(ys_, rr[:, 0])
    out["corr_alpha_r50"] = corr(ys_, rr[:, 1])
    out["r_rel_max"] = [float(np.max(rr[:, j]) / rr[0, j] - 1) for j in range(3)]
    out["r_rel_min"] = [float(np.min(rr[:, j]) / rr[0, j] - 1) for j in range(3)]
    # trajectories with the metric: areal radii of the mass shells, Killing energy sum
    recs = traj_records(dirs)
    Mp = float(h["sum_m"][0] / h["np"][0])     # particle mass of this run (N may differ from the model file)
    tr, rc, ra, ek, wmean = [], [], [], [], []
    for rec in recs:
        m = np.full(len(rec["tag"]), Mp)
        c_, a_ = shell_areal(rec, m)
        EK, W = C.killing_energy(rec)
        tr.append(rec["time"])
        rc.append(c_)
        ra.append(a_)
        ek.append(float(Mp * np.sum(EK)))
        wmean.append(float(np.mean(W)))
    tr, rc, ra = np.array(tr), np.array(rc), np.array(ra)
    out["traj_t"] = tr.tolist()
    out["shell_coord"] = rc.tolist()
    out["shell_areal"] = ra.tolist()
    out["EK_sum"] = ek
    out["traj_meanW"] = wmean
    if len(tr) > 1:
        dc = rc / rc[0] - 1.0
        da = ra / ra[0] - 1.0
        out["shell_rel_change_coord_max_abs"] = [float(np.max(np.abs(dc[:, j]))) for j in range(3)]
        out["shell_rel_change_areal_max_abs"] = [float(np.max(np.abs(da[:, j]))) for j in range(3)]
        out["areal_over_coord_change_r50"] = float(np.sum(da[:, 1] * dc[:, 1]) / np.sum(dc[:, 1] ** 2))
        out["corr_alpha_areal_r50"] = corr(np.interp(tr, t, y), ra[:, 1])
        out["corr_alpha_EK"] = corr(np.interp(tr, t, y), np.array(ek))
        out["EK_sum_change_max_abs"] = float(np.max(np.abs(np.array(ek) - ek[0])))
    series = dict(t=t, y=y, ys=ys, meanW=meanW, zt=zt, Hn=Hn, ts=ts, rr=rr, tr=tr, rc=rc, ra=ra,
                  ek=np.array(ek), ripple=rp)
    return out, series


# ------------------------------------------------------------------------------ pulsation
def pulsation():
    sys.path.insert(0, os.path.join(TRACK, "models"))
    import fluid_onset as fo  # noqa: E402  (puts gravothermal/ on the path)
    import tmb  # noqa: E402
    from scipy.interpolate import CubicSpline  # noqa: E402
    from scipy.optimize import brentq  # noqa: E402
    B = 1.0

    def w0_of(y0):
        return 1.0 - math.exp(-y0)

    def omega2_scaled(y0, s, N=600):
        """Lowest omega^2 with gamma = s * gamma_F21 (hatted, surface time)."""
        eq, rt, Mt, wt = tmb.structure(B, w0_of(y0))
        R = eq["R"]
        Msp, wsp = CubicSpline(rt, Mt), CubicSpline(rt, wt)
        mf = Mt / Mt[-1]
        nodes = np.unique(np.concatenate((np.linspace(0.0, R, N // 2 + 1),
                                          np.interp(np.linspace(0.0, 1.0, N // 2 + 1), mf, rt))))

        def coeff(rq):
            w = np.clip(wsp(rq), 0.0, None)
            rho, p, gF = tmb.local_vec(B, w)
            return Msp(rq), rho, p, s * gF, 1.0 - B * w
        ev = tmb.fem_lowest(nodes, coeff, 1)[0]
        return float(ev[0]), eq

    def period(om2, eq):
        if om2 <= 0:
            return None
        return float(2 * math.pi / (math.sqrt(om2 * (1.0 - 2.0 * eq["C"])) * eq["E"]))

    y_max = 0.33403216106467554
    s_star = brentq(lambda s: omega2_scaled(y_max, s)[0], 0.5, 1.2, xtol=1e-9)
    res = dict(s_star=s_star, y_max=y_max, models={})
    for tag, y0 in (("king_y0p26000", 0.26), ("king_y0p31400", 0.314), ("king_y0p32400", 0.324), ("king_y0p33403", y_max)):
        eq = tmb.solve(B, w0_of(y0))
        md = json.load(open(os.path.join(C.IC_DIR, C.stem(tag) + ".json"))) if tag in MODEL_OF.values() else None
        row = dict(y0=y0, C=eq["C"], M_hat=eq["E"])
        if md:
            row["P_dyn_M"] = float(math.pi * math.sqrt(3.0 / (4.0 * math.pi * md["rho_c"])))
        for v in ("F21", "J_E", "J_p"):
            om2, eqv = fo.omega2(B, w0_of(y0), v, 600)
            om2b, _ = fo.omega2(B, w0_of(y0), v, 1200)
            row[f"omega2_{v}"] = om2
            row[f"omega2_{v}_N1200"] = om2b
            row[f"P_{v}_M"] = period(om2, eqv)
        om2, eqv = omega2_scaled(y0, s_star)
        row["omega2_scaledF21"] = om2
        row["P_scaledF21_M"] = period(om2, eqv)
        res["models"][tag] = row
        print("pulsation", tag, json.dumps(row), flush=True)
    ys = np.linspace(0.28, 0.345, 14)
    res["seq"] = dict(y0=ys.tolist(),
                      F21=[fo.omega2(B, w0_of(y), "F21", 600)[0] for y in ys],
                      J_E=[fo.omega2(B, w0_of(y), "J_E", 600)[0] for y in ys],
                      scaled=[omega2_scaled(y, s_star)[0] for y in ys])
    return res


# ------------------------------------------------------------------------------ figures
def figures(outdir, res, ser, puls, tag=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    col = {"cc1": fs.PAL["red"], "cc2": fs.PAL["blue"]}
    lab = {"cc1": "CC1 (y0 = 0.334)", "cc2": "CC2 (y0 = 0.314)"}

    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.97, wspace=0.42, hspace=0.1)
    for name, s in ser.items():
        mk = name[:3]
        c = col[mk]
        a = axs[0, 0]
        a.plot(s["t"], s["y"], color=c, lw=0.6, alpha=0.5)
        a.plot(s["t"], s["ys"], color=c, lw=1.4, label=lab[mk])
        fc = res[name]["fits"].get("cos", {})
        if "P" in fc:
            a.plot(s["t"], f_cos(s["t"], fc["A"], fc["P"], fc["c"]), color=c, ls="--", lw=1.0)
        axs[0, 1].plot(s["ts"], s["rr"][:, 0] / s["rr"][0, 0] - 1, color=c, ls=":", lw=1.2)
        axs[0, 1].plot(s["ts"], s["rr"][:, 1] / s["rr"][0, 1] - 1, color=c, ls="-", lw=1.2)
        if len(s["tr"]) > 1:
            axs[0, 2].plot(s["tr"], s["rc"][:, 1] / s["rc"][0, 1] - 1, color=c, ls="-", lw=1.2, marker=".")
            axs[0, 2].plot(s["tr"], s["ra"][:, 1] / s["ra"][0, 1] - 1, color=c, ls="--", lw=1.2, marker="x", ms=3)
            axs[1, 2].plot(s["tr"], s["ek"] - s["ek"][0], color=c, lw=1.2, marker=".")
        axs[1, 0].plot(s["t"], s["meanW"] - s["meanW"][0], color=c, lw=1.0)
        axs[1, 1].plot(s["zt"], s["Hn"], color=c, lw=1.0)
    axs[0, 0].axhline(0.0, **fs.MASK_LINE)
    axs[0, 0].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$")
    axs[0, 0].legend(fontsize=7, loc="upper left", frameon=False)
    axs[0, 0].text(0.97, 0.04, "thin: raw; thick: 20 M mean;\ndashed: A(1-cos 2πt/P)+c",
                   transform=axs[0, 0].transAxes, fontsize=6, ha="right")
    axs[0, 1].axhline(0.0, **fs.MASK_LINE)
    axs[0, 1].set_ylabel(r"$r_{10}$ (dotted), $r_{50}$ / initial $-1$")
    axs[0, 2].axhline(0.0, **fs.MASK_LINE)
    axs[0, 2].set_ylabel(r"shell 50%: coord (·), areal (x) $-1$")
    axs[1, 0].axhline(0.0, **fs.MASK_LINE)
    axs[1, 0].set_ylabel(r"$\Sigma mW/\Sigma m$ $-$ initial")
    axs[1, 1].set_ylabel(r"$\|H\|_2^2$")
    axs[1, 1].set_yscale("log")
    axs[1, 2].axhline(0.0, **fs.MASK_LINE)
    axs[1, 2].set_ylabel(r"$\Sigma M E_K$ $-$ initial $[M]$")
    for a in axs[1]:
        a.set_xlabel(r"$t/M$")
    fs.save(fig, os.path.join(outdir, "fig_drift_controls" + tag))
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.11, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    for name, s in ser.items():
        mk = name[:3]
        fc = res[name]["fits"].get("cos", {})
        if "P" in fc:
            axs[0].plot(s["t"], s["y"] - f_cos(s["t"], fc["A"], fc["P"], fc["c"]), color=col[mk], lw=0.7,
                        label=lab[mk])
        rp = s["ripple"]
        if rp:
            axs[1].plot(rp["periods"], np.sqrt(rp["power"]), color=col[mk], lw=1.0, label=lab[mk])
    axs[0].axhline(0.0, **fs.MASK_LINE)
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"$\alpha_c$ residual of the cosine fit")
    axs[0].legend(fontsize=7, frameon=False)
    axs[1].set_xlabel("period of the residual  [M]")
    axs[1].set_ylabel("amplitude spectrum")
    if puls:
        for mtag, mk in (("king_y0p33403", "cc1"), ("king_y0p31400", "cc2")):
            r = puls["models"][mtag]
            for key, ls in (("P_dyn_M", ":"), ("P_F21_M", "--")):
                if r.get(key) and r[key] < 100:
                    axs[1].axvline(r[key], color=col[mk], ls=ls, lw=1.0)
        axs[1].text(0.03, 0.95, "dotted: dynamical estimate\n(fluid F21 mode: 305-358 M, off scale)",
                    transform=axs[1].transAxes, fontsize=6, ha="left", va="top")
    fs.save(fig, os.path.join(outdir, "fig_drift_fit" + tag))
    plt.close(fig)

    if puls:
        fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
        sq = puls["seq"]
        for key, c, lb in (("F21", fs.PAL["blue"], r"F21 $\gamma=1+p/u$"), ("J_E", fs.PAL["red"], r"Juttner $\Gamma_1(\theta_E)$"),
                           ("scaled", fs.PAL["green"], r"$s^*\gamma_{\rm F21}$, onset at $E_b$ max")):
            axs[0].plot(sq["y0"], sq[key], color=c, lw=1.3, label=lb)
        axs[0].axhline(0.0, **fs.MASK_LINE)
        for y, t_ in ((0.314, "CC2"), (puls["y_max"], "CC1")):
            axs[0].axvline(y, color="0.5", lw=0.8, ls=":")
        axs[0].set_xlabel(r"$y_0$ (King, $b=1$)")
        axs[0].set_ylabel(r"lowest $\hat\omega^2$ (surface time)")
        axs[0].legend(fontsize=6, frameon=False)
        names = []
        xs = np.arange(4)
        for j, (mtag, mk) in enumerate((("king_y0p31400", "cc2"), ("king_y0p33403", "cc1"))):
            r = puls["models"][mtag]
            vals = [r.get("P_dyn_M"), r.get("P_F21_M"), r.get("P_J_E_M"), r.get("P_scaledF21_M")]
            vv = [v if v else np.nan for v in vals]
            axs[1].bar(xs + (j - 0.5) * 0.38, vv, width=0.36, color=col[mk], label=lab[mk])
            for x, v, key in zip(xs + (j - 0.5) * 0.38, vals, ("P_dyn_M", "P_F21_M", "P_J_E_M", "P_scaledF21_M")):
                if not v:
                    txt = "unstable" if key == "P_J_E_M" else "marginal"
                    axs[1].text(x, 30.0, txt, rotation=90, ha="center", va="bottom", fontsize=6, color=col[mk])
            fc = res.get(f"{mk}_kninf", {}).get("fits", {}).get("cos", {})
            if "P" in fc:
                axs[1].axhline(fc["P"], color=col[mk], ls="--", lw=1.0)
            names = ["dynamical", "fluid F21", "fluid Juttner", "scaled F21"]
        axs[1].set_xticks(xs)
        axs[1].set_xlim(-0.7, 3.75)
        axs[1].set_xticklabels(names, fontsize=7)
        axs[1].set_yscale("log")
        axs[1].set_ylabel(r"period $[M]$ (dashed: fitted excursion)")
        axs[1].legend(fontsize=6, frameon=False, loc="upper left")
        fs.save(fig, os.path.join(outdir, "fig_drift_pulsation" + tag))
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+", help="NAME=DIR[,DIR...]")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--pulsation", action="store_true")
    ap.add_argument("--tag", default="", help="suffix of the output names")
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    res, ser = {}, {}
    for spec in a.runs:
        name, dirs = spec.split("=", 1)
        dirs = dirs.split(",")
        mk = name[:3]
        model = C.load_model(MODEL_OF[mk])
        res[name], ser[name] = analyse(name, dirs, model)
        print(name, json.dumps({k: v for k, v in res[name].items() if not isinstance(v, (list, dict))}), flush=True)
        print(name, "fits", json.dumps(res[name]["fits"]), flush=True)
        print(name, "ripple", json.dumps(res[name]["ripple"]), flush=True)
    puls = pulsation() if a.pulsation else None
    if puls:
        res["_pulsation"] = puls
    with open(os.path.join(a.out, f"controls{a.tag}.json"), "w") as f:
        json.dump(res, f, indent=1)
    figures(a.out, res, ser, puls, a.tag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
