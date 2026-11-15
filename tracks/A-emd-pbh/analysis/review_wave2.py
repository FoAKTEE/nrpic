#!/usr/bin/env python3
"""Lead's independent checks of the wave-2 helper packages of A-emd-pbh.

Reads only registered run outputs under scratch/A-emd-pbh/ and uses its own readers,
estimators and exact formulas, not the helpers' analysis code (runs_ball/compare.py,
periodic_threshold/scripts/analyse_scouting.py, newton/analyze_newton.py). Results go to
<out>/review_wave2.json and one figure, <out>/fig_review_wave2.png. The comparison with
the helpers' numbers and the verdicts are in tracks/A-emd-pbh/stage/REVIEW-wave2.md.

    review_wave2.py --out DIR

Parts
  B  expanding ball SR-1/SR-2 at dx = M, M/2, M/4: areal radius of the tracked particles
     from the spatial metric at the particle, core turnaround (proper time, largest
     radius) against a cycloid fixed by the exact numbers of data set 2t, core shell error
     at tau = 16.894, comoving coordinates (SR-1), first non-finite record, largest |H|,
     central lapse against the scale factor of the core (SR-2), card cost per cell-step.
  P  periodic scouting S1/S2: background time of the constraint thresholds, the blow-up
     of S1, the central lapse, the cost per step.
  N  Newtonian mode: top-hat turnaround and largest radius from the second moments of
     the history against the analytic cycloid of the sampled ball; first collapse of one
     ellipsoid case against the reference stored with the case.
  C  arithmetic of the criteria and the verifier's C1c (closed forms).
"""
import argparse
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"

# exact numbers of data set 2t (runs A-emd-pbh-20261115-153719-91b03d1 and
# A-20261115-130948-5a2b58a; third generator of the verifier, A-20261115-161239-1c41333)
TAU_TA = 16.893769
RMAX_RI = 1.339803
T_I = 2.0 / (3.0 * 0.0625)          # data set 2t: H R_b = 0.5 with R_b = 8 M -> H_i = 1/16

BALL = {
    ("sr1", 1.0): f"{S}/A-emd-pbh-20261115-155056-ec1b816/sr1_n128",
    ("sr1", 0.5): f"{S}/A-emd-pbh-20261115-153843-7172b66/sr1",
    ("sr1", 0.25): f"{S}/A-emd-pbh-20261115-164539-0b18e84/sr1_n256_L32",
    ("sr2", 1.0): f"{S}/A-emd-pbh-20261115-155056-ec1b816/sr2_n128",
    ("sr2", 0.5): f"{S}/A-emd-pbh-20261115-153845-7172b66/sr2",
    ("sr2", 0.25): f"{S}/A-emd-pbh-20261115-164541-0b18e84/sr2_n256_L32",
}
PERIODIC = {
    "S1": f"{S}/A-emd-pbh-20261115-160349-9d232d2/run",
    "S2": f"{S}/A-emd-pbh-20261115-155754-8422a4a/run",
}
NEWTON_TH = f"{S}/A-emd-pbh-20261115-153409-dc27b98"
NEWTON_SCAN = f"{S}/A-emd-pbh-20261115-153415-dc27b98"


# ---------------------------------------------------------------- readers
def hst(path):
    """Numeric rows of a history file; a restart repeats times, the last row wins."""
    rows = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            try:
                v = [float(x) for x in line.split()]
            except ValueError:
                continue
            rows[v[0]] = v
    n = min(len(v) for v in rows.values())
    return np.array([rows[k][:n] for k in sorted(rows)])


def hst_names(path):
    with open(path) as f:
        for line in f:
            if "[1]" in line:
                return re.findall(r"\[\d+\]=\s*(\S+)", line)
    return []


def col(path, name):
    names = hst_names(path)
    return hst(path)[:, names.index(name)]


def traj(d):
    a = np.fromfile(os.path.join(d, "ball.traj.bin"), "<f8")
    b = np.fromfile(os.path.join(d, "ball.trajmet.bin"), "<f8")
    n = min(len(a) // 8, len(b) // 17)
    a = a[:8 * n].reshape(n, 8)
    b = b[:17 * n].reshape(n, 17)
    times = np.unique(a[:, 0])
    tags = np.unique(a[:, 1]).astype(np.int64)
    it = np.searchsorted(times, a[:, 0])
    ip = np.searchsorted(tags, a[:, 1].astype(np.int64))
    X = np.full((len(times), len(tags), 3), np.nan)
    G = np.full((len(times), len(tags), 6), np.nan)
    TAU = np.full((len(times), len(tags)), np.nan)
    X[it, ip] = a[:, 2:5]
    G[it, ip] = b[:, 6:12]
    TAU[it, ip] = b[:, 12]
    return times, tags, X, G, TAU


def areal(X, G):
    """Areal radius in spherical symmetry: R = r sqrt(g_TT), g_TT the tangential
    component (trace minus radial part, halved); g = (xx, xy, xz, yy, yz, zz)."""
    r = np.linalg.norm(X, axis=-1)
    n = X / r[..., None]
    gxx, gxy, gxz, gyy, gyz, gzz = (G[..., k] for k in range(6))
    tr = gxx + gyy + gzz
    nn = (gxx * n[..., 0] ** 2 + gyy * n[..., 1] ** 2 + gzz * n[..., 2] ** 2
          + 2 * (gxy * n[..., 0] * n[..., 1] + gxz * n[..., 0] * n[..., 2]
                 + gyz * n[..., 1] * n[..., 2]))
    return r * np.sqrt(0.5 * (tr - nn)), r


# ---------------------------------------------------------------- cycloid of the core
def core_cycloid():
    """R/R_i of the homogeneous core: R = A (1 - cos eta), t = B (eta - sin eta),
    with A = RMAX_RI/2 and B fixed by the turnaround time after the slice."""
    A = 0.5 * RMAX_RI
    eta0 = math.acos(1.0 - 1.0 / A)                 # R = R_i at tau = 0
    B = TAU_TA / (math.pi - eta0 + math.sin(eta0))
    t_bang = B * (eta0 - math.sin(eta0))           # proper time from the bang to the slice
    eta = np.linspace(eta0, 2 * math.pi, 200001)
    tau = B * (eta - np.sin(eta)) - t_bang
    f = A * (1 - np.cos(eta))
    return dict(A=A, B=B, eta0=eta0, t_bang=t_bang, tau=tau, f=f,
                tau_crunch=B * 2 * math.pi - t_bang)


def f_of_tau(cy, tq):
    return np.interp(tq, cy["tau"], cy["f"], left=np.nan, right=np.nan)


def vertex(t, y, i):
    """Vertex of the parabola through records i-1, i, i+1."""
    c = np.polyfit(t[i - 1:i + 2] - t[i], y[i - 1:i + 2], 2)
    if c[0] >= 0:
        return np.nan, np.nan
    x = -c[1] / (2 * c[0])
    return t[i] + x, np.polyval(c, x)


def ball_case(gauge, dx, d, cy):
    out = dict(dir=d)
    times, tags, X, G, TAU = traj(d)
    R, r = areal(X, G)
    Ri = R[0]
    core = Ri <= 2.35
    out["n_core"] = int(core.sum())
    out["t_last_record"] = float(times[-1])
    # first non-finite record of the constraint statistics
    cs = os.path.join(d, "ball.cstat.hst")
    t_c = col(cs, "time")
    Hm = col(cs, "H_max")
    chi = col(cs, "chi_min")
    bad = ~np.isfinite(Hm) | ~np.isfinite(chi) | (chi <= 0)
    out["t_first_nonfinite_cstat"] = float(t_c[bad][0]) if bad.any() else None
    out["t_end_cstat"] = float(t_c[-1])
    out["H_max_at"] = {f"{tq:g}": float(Hm[np.argmin(np.abs(t_c - tq))])
                       for tq in (2, 10, 20, 30) if tq <= t_c[-1] + 1e-9}
    if gauge == "sr1":
        r0 = r[0]
        fin = np.isfinite(R)
        out["max_abs_r_over_r0_minus_1"] = float(np.nanmax(np.abs(np.where(fin, r / r0 - 1, np.nan))))
        out["max_abs_tau_minus_t"] = float(np.nanmax(np.abs(np.where(fin, TAU - times[:, None], np.nan))))
    # turnaround per core particle
    dtau, drm = [], []
    for p in np.nonzero(core)[0]:
        ok = np.isfinite(TAU[:, p]) & np.isfinite(R[:, p])
        tp, Rp = TAU[ok, p], R[ok, p]
        i = int(np.argmax(Rp))
        if 0 < i < len(Rp) - 1:
            tv, Rv = vertex(tp, Rp, i)
            if np.isfinite(tv):
                dtau.append(tv - TAU_TA)
                drm.append(Rv / (RMAX_RI * Ri[p]) - 1)
    dtau, drm = np.array(dtau), np.array(drm)
    out["turnaround"] = dict(n=int(len(dtau)), dtau_mean=float(dtau.mean()) if len(dtau) else None,
                             dtau_median=float(np.median(dtau)) if len(dtau) else None,
                             rel_mean=float(dtau.mean() / TAU_TA) if len(dtau) else None,
                             dRmax_rel_mean=float(drm.mean()) if len(drm) else None)
    # shell error at tau = 16.894 and 8
    for tq in (8.0, 12.0, TAU_TA):
        e = []
        for p in np.nonzero(core)[0]:
            ok = np.isfinite(TAU[:, p]) & np.isfinite(R[:, p])
            tp, Rp = TAU[ok, p], R[ok, p]
            if len(tp) > 1 and tp[0] <= tq <= tp[-1]:
                e.append(np.interp(tq, tp, Rp) / (Ri[p] * f_of_tau(cy, tq)) - 1)
        e = np.array(e)
        out[f"eps_tau{tq:g}"] = dict(n=int(len(e)), maxabs=float(np.abs(e).max()) if len(e) else None,
                                     mean=float(e.mean()) if len(e) else None)
    # central lapse (probe at the origin) against the core scale factor (SR-2)
    nh = os.path.join(d, "ball.nrpic.hst")
    th = col(nh, "time")
    ap = col(nh, "alpha_probe")
    tp = col(nh, "tau_probe")
    rel = ap / f_of_tau(cy, tp) - 1
    out["alpha_c_peak"] = float(np.nanmax(ap[th <= 20])) if np.any(th <= 20) else None
    out["t_alpha_c_peak"] = float(th[th <= 20][np.nanargmax(ap[th <= 20])]) if np.any(th <= 20) else None
    for thr in (1e-3, 1e-2, 0.1):
        k = np.nonzero(np.abs(rel) > thr)[0]
        out[f"t_alpha_rel_gt_{thr:g}"] = float(th[k[0]]) if len(k) else None
    out["tau_probe_end"] = float(tp[-1])
    out["t_probe_reaches_crunch"] = (float(th[np.nonzero(tp >= cy["tau_crunch"])[0][0]])
                                     if np.any(tp >= cy["tau_crunch"]) else None)
    # card cost per cell-step from the AthenaK log
    logs = sorted(f for f in os.listdir(d) if re.match(r"athena\.\d{8}-\d{6}\.log$", f))
    txt = open(os.path.join(d, logs[-1])).read()
    cyc = int(re.findall(r"cycle=(\d+)", txt)[-1])
    cpu = float(re.findall(r"cpu time used\s*=\s*(\S+)", txt)[-1])
    ncell = 128 ** 3 if dx == 1.0 else 256 ** 3
    out["cost_card_s_per_cell_step"] = cpu / (ncell * cyc)
    out["cycles"] = cyc
    out["cpu_s"] = cpu
    series = dict(t_cstat=t_c.tolist(), H_max=Hm.tolist(), t_hst=th.tolist(),
                  alpha_rel=rel.tolist(), alpha_c=ap.tolist())
    return out, series


# ---------------------------------------------------------------- periodic box
def t_over_tH(tau, eps_i=1.0):
    a = (1 + tau / 2.0) ** 2
    return (a / (6.0 / eps_i ** 2)) ** 1.5


def periodic_case(label, d):
    out = dict(dir=d)
    cs = os.path.join(d, "peak.cstat.hst")
    t = col(cs, "time")
    Hr = col(cs, "Hr_max")
    chi = col(cs, "chi_min")
    for thr in (0.01, 0.1):
        k = np.nonzero(Hr > thr)[0]
        out[f"Hr_max_first_gt_{thr:g}"] = (dict(tau=float(t[k[0]]), t_over_tH=float(t_over_tH(t[k[0]])))
                                         if len(k) else None)
    out["Hr_max_t0"] = float(Hr[0])
    fin = np.isfinite(Hr) & np.isfinite(chi) & (chi > 0)
    out["Hr_max_max_finite"] = float(np.max(Hr[fin]))
    bad = np.nonzero(~fin)[0]
    out["first_nonfinite"] = (dict(tau=float(t[bad[0]]), t_over_tH=float(t_over_tH(t[bad[0]])))
                              if len(bad) else None)
    nh = os.path.join(d, "peak.nrpic.hst")
    th = col(nh, "time")
    ap = col(nh, "alpha_probe")
    amin = col(nh, "alpha_min")
    a = (1 + th / 2.0) ** 2
    okk = np.isfinite(ap) & (ap > 0) & (ap < 1e30)
    if bad.size:
        okk &= th < t[bad[0]]
    out["alpha_c_over_a_last_finite"] = float((ap / a)[okk][-1])
    out["tau_last_finite_probe"] = float(th[okk][-1])
    out["alpha_min_over_a_min_finite"] = float(np.min((amin / a)[okk & np.isfinite(amin)]))
    out["t_end_over_tH"] = float(t_over_tH(th[-1]))
    txt = open(os.path.join(d, sorted(f for f in os.listdir(d) if re.match(r"athena\.\d{8}-\d{6}\.log$", f))[-1])).read()
    cyc = int(re.findall(r"cycle=(\d+)", txt)[-1])
    cpu = float(re.findall(r"cpu time used\s*=\s*(\S+)", txt)[-1])
    out["card_s_per_step"] = cpu / cyc
    series = dict(t_over_tH=t_over_tH(t).tolist(), Hr_max=Hr.tolist())
    return out, series


# ---------------------------------------------------------------- Newtonian mode
def moments(d):
    p = os.path.join(d, "newton.newton.hst")
    names = hst_names(p)
    h = hst(p)
    c = {n: h[:, i] for i, n in enumerate(names)}
    M = c["mass"]
    X = np.stack([c["X_x"], c["X_y"], c["X_z"]], -1)
    I = np.zeros((len(M), 3, 3))
    for (i, j), n in {(0, 0): "I_xx", (0, 1): "I_xy", (0, 2): "I_xz", (1, 1): "I_yy",
                      (1, 2): "I_yz", (2, 2): "I_zz"}.items():
        I[:, i, j] = I[:, j, i] = c[n]
    Cm = I / M[:, None, None] - X[:, :, None] * X[:, None, :]
    return c["time"], Cm, c


def newton_tophat(d):
    b = json.load(open(os.path.join(d, "ball.json")))
    cy = b["reference"]["cycloid"]
    # analytic cycloid of the sampled ball (G = 1): E = V0^2/2 - M/R0, R_max = M/|E|
    Mb, R0, V0, t0 = b["mass"], cy["R0"], cy["V0"], cy["t0"]
    E = 0.5 * V0 ** 2 - Mb / R0
    Rmax = Mb / abs(E)
    A = 0.5 * Rmax
    B = math.sqrt(A ** 3 / Mb)
    eta0 = math.acos(1 - R0 / A)
    toff = t0 - B * (eta0 - math.sin(eta0))
    tta = B * math.pi + toff
    t, Cm, c = moments(d)
    t = t + b["t0"]                            # history times are code times from t0
    R = np.sqrt(5.0 * np.trace(Cm, axis1=1, axis2=2) / 3.0)
    i = int(np.argmax(R))
    sel = slice(max(i - 3, 0), i + 4)          # quartic through seven records: own estimator
    cc = np.polyfit(t[sel] - t[i], R[sel], 4)
    tt = np.linspace(t[sel][0] - t[i], t[sel][-1] - t[i], 20001)
    yy = np.polyval(cc, tt)
    k = int(np.argmax(yy))
    W0 = c["W"][0]
    e = (c["K"] + c["W"] - (c["K"][0] + c["W"][0])) / abs(W0)
    # energy until the cycloid time of R = 0.25 R_max on the way in
    eta25 = 2 * math.pi - math.acos(1 - 0.25 * Rmax / A)
    t25 = B * (eta25 - math.sin(eta25)) + toff
    return dict(name=os.path.basename(d), n=b["n"], dx=b["dx"],
                t_ta_cycloid=tta, R_max_cycloid=Rmax,
                t_ta_ref_stored=cy["t_ta"], R_max_ref_stored=cy["R_max"],
                t_ta=float(t[i] + tt[k]), R_max=float(yy[k]),
                t_ta_rel=float((t[i] + tt[k]) / tta - 1), R_max_rel=float(yy[k] / Rmax - 1),
                E_err_max_to_t025=float(np.max(np.abs(e[t <= t25]))))


def newton_scan_case(d):
    b = json.load(open(os.path.join(d, "ball.json")))
    ref = b["reference"]["ellipsoid_isolated"]["collapses"][0]["t"]
    t, Cm, _ = moments(d)
    t = t + b["t0"]                            # history times are code times from t0
    ev = np.linalg.eigvalsh(Cm)[:, 0]          # smallest eigenvalue
    i = int(np.argmin(ev[t < 1.3 * ref]))
    sel = slice(max(i - 3, 0), i + 4)
    cc = np.polyfit(t[sel] - t[i], ev[sel], 2)
    tmin = t[i] - cc[1] / (2 * cc[0]) if cc[0] > 0 else t[i]
    return dict(name=os.path.basename(d), e=b["e"], p=b["p"], n=b["n"], dx=b["dx"],
                t1_ref=ref, t1_min_eig=float(tmin), t1_rel=float(tmin / ref - 1))


# ---------------------------------------------------------------- closed forms
def closed_forms():
    out = {}
    # verifier C1b/C1c: start contrast = deltabar_ent(mu) (a_i/a_H), a_i/a_H = (q/(R_b H_i))^2
    c = 12.0 / (5.0 * math.e)                  # deltabar_ent / mu
    for q in (2, 3):
        f = (q / 0.9) ** 2
        out[f"mu_ceiling_q{q}_cap0.3"] = 0.3 / (c * f)
    out["start_contrast_mu0.05_q2"] = c * 0.05 * (2 / 0.9) ** 2
    out["start_contrast_mu0.45_q2"] = c * 0.45 * (2 / 0.9) ** 2
    out["deltabar_over_mu"] = c
    # criteria2: exact LTB (e = 0) central crunch t_s(0)/t_H = (108 pi/576) e^(3 mu) mu^(-3/2)
    for mu in (0.03, 0.3, 0.5):
        out[f"ltb_central_crunch_tH_mu{mu:g}"] = 108 * math.pi / 576 * math.exp(3 * mu) * mu ** -1.5
    return out


# ---------------------------------------------------------------- figure
def figure(series, B, P, N, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH * 1.35, 6.4))
    cols = {1.0: fs.PAL["yellow"], 0.5: fs.PAL["red"], 0.25: fs.PAL["blue"]}
    for dx in (1.0, 0.5, 0.25):
        s = series["B"][f"sr1_{dx:g}"]
        ax[0, 0].semilogy(s["t_cstat"], np.abs(s["H_max"]), color=cols[dx], label=f"dx = {dx:g} M")
        s2 = series["B"][f"sr2_{dx:g}"]
        ax[0, 1].plot(s2["t_hst"], s2["alpha_c"], color=cols[dx], label=f"dx = {dx:g} M")
    ax[0, 0].set_xlabel("t / M")
    ax[0, 0].set_ylabel(r"SR-1: max $|H|$")
    ax[0, 0].legend(frameon=False, fontsize=8)
    ax[0, 0].set_xlim(0, 34)
    ax[0, 0].set_ylim(1e-3, 1e1)
    ax[0, 1].set_xlabel("t / M")
    ax[0, 1].set_ylabel(r"SR-2: central lapse $\alpha_c$")
    ax[0, 1].axhline(RMAX_RI, **fs.GUIDE)
    ax[0, 1].text(30, RMAX_RI + 0.03, "largest exact a = 1.34", fontsize=8)
    ax[0, 1].legend(frameon=False, fontsize=8)
    # turnaround error vs dx
    for g, mk in (("sr1", "o"), ("sr2", "s")):
        x, y, z = [], [], []
        for dx in (1.0, 0.5, 0.25):
            b = B[f"{g}_{dx:g}"]
            if b["turnaround"]["dtau_mean"] is not None:
                x.append(dx)
                y.append(abs(b["turnaround"]["dtau_mean"]))
                z.append(b["eps_tau16.8938"]["maxabs"] if b["eps_tau16.8938"]["maxabs"] else np.nan)
        ax[0, 2].loglog(x, y, mk + "-", color=fs.PAL["blue"] if g == "sr1" else fs.PAL["red"],
                        label=f"{g.upper()}: |mean dtau_ta| / M")
        ax[0, 2].loglog(x, z, mk + ":", color=fs.PAL["blue"] if g == "sr1" else fs.PAL["red"],
                        label=f"{g.upper()}: max|eps| at tau_ta")
    xx = np.array([0.25, 1.0])
    ax[0, 2].loglog(xx, 0.02 * (xx / 0.25) ** 2, **fs.GUIDE, label="second order")
    ax[0, 2].set_xlabel("dx / M")
    ax[0, 2].set_xticks([0.25, 0.5, 1.0])
    ax[0, 2].set_xticklabels(["1/4", "1/2", "1"])
    ax[0, 2].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax[0, 2].set_ylabel("error")
    ax[0, 2].legend(frameon=False, fontsize=7)
    for lab, c in (("S1", fs.PAL["red"]), ("S2", fs.PAL["blue"])):
        s = series["P"][lab]
        ax[1, 0].loglog(s["t_over_tH"], s["Hr_max"], color=c, label=lab)
    for thr in (0.01, 0.1):
        ax[1, 0].axhline(thr, **fs.MASK_LINE)
    ax[1, 0].set_xlabel(r"$t/t_H$ (background)")
    ax[1, 0].set_ylabel(r"max $|H|/(16\pi E)$")
    ax[1, 0].legend(frameon=False, fontsize=8)
    # Newtonian top-hat errors vs dx (particle spacing 0.025)
    th = [n for n in N["tophat"] if n["name"].endswith("_h025")]
    th.sort(key=lambda n: -n["dx"])
    ax[1, 1].loglog([n["dx"] for n in th], [abs(n["t_ta_rel"]) for n in th], "o-",
                    color=fs.PAL["blue"], label=r"$|t_{ta}/t_{ta}^{cyc}-1|$")
    ax[1, 1].loglog([n["dx"] for n in th], [abs(n["R_max_rel"]) for n in th], "s-",
                    color=fs.PAL["red"], label=r"$|R_{max}/R_{max}^{cyc}-1|$")
    xx = np.array([th[-1]["dx"], th[0]["dx"]])
    ax[1, 1].loglog(xx, abs(th[-1]["t_ta_rel"]) * (xx / xx[0]) ** 2, **fs.GUIDE, label="second order")
    ax[1, 1].set_xlabel("mesh spacing (Newtonian top-hat)")
    ax[1, 1].set_ylabel("relative error")
    ax[1, 1].legend(frameon=False, fontsize=7)
    sc = N["scan"]
    ax[1, 2].plot([s["e"] for s in sc], [s["t1_rel"] for s in sc], "o", color=fs.PAL["blue"])
    ax[1, 2].axhline(0, **fs.MASK_LINE)
    ax[1, 2].set_xlabel("e (scan cases at 128^3)")
    ax[1, 2].set_ylabel(r"$t_1$(min eigenvalue)$/t_1^{ref}-1$")
    fig.tight_layout()
    fs.save(fig, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cy = core_cycloid()
    res = dict(cycloid=dict(A=cy["A"], B=cy["B"], eta0=cy["eta0"], t_bang=cy["t_bang"],
                            t_i_of_data=T_I, tau_crunch=cy["tau_crunch"]))
    series = dict(B={}, P={})
    B = {}
    for (g, dx), d in BALL.items():
        o, s = ball_case(g, dx, d, cy)
        B[f"{g}_{dx:g}"] = o
        series["B"][f"{g}_{dx:g}"] = s
    res["ball"] = B
    P = {}
    for lab, d in PERIODIC.items():
        o, s = periodic_case(lab, d)
        P[lab] = o
        series["P"][lab] = s
    res["periodic"] = P
    tophat = [newton_tophat(os.path.join(NEWTON_TH, n)) for n in sorted(os.listdir(NEWTON_TH))
              if n.startswith("th_") and os.path.exists(os.path.join(NEWTON_TH, n, "newton.newton.hst"))]
    scan = []
    for n in sorted(os.listdir(NEWTON_SCAN)):
        dd = os.path.join(NEWTON_SCAN, n)
        bj = os.path.join(dd, "ball.json")
        if (os.path.exists(os.path.join(dd, "newton.newton.hst")) and os.path.exists(bj)
                and json.load(open(bj))["case"]["nx"] == 128):
            try:
                scan.append(newton_scan_case(dd))
            except (KeyError, IndexError, ValueError) as err:
                scan.append(dict(name=n, error=str(err)))
    res["newton"] = dict(tophat=tophat, scan=[s for s in scan if "error" not in s],
                         scan_errors=[s for s in scan if "error" in s])
    res["closed_forms"] = closed_forms()
    with open(os.path.join(a.out, "review_wave2.json"), "w") as f:
        json.dump(res, f, indent=1)
    figure(series, B, P, res["newton"], os.path.join(a.out, "fig_review_wave2"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
