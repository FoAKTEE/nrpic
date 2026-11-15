#!/usr/bin/env python3
"""Analysis of AthenaK Newtonian-mode runs of newton_campaign.py against the references
of this directory (cycloid, homogeneous ellipsoid). Analysis of AthenaK output only.

    analyze_newton.py --tophat RUN_DIR [--scan RUN_DIR ...] [--cost RUN_DIR] --out DIR

Per case it reads `ball.json` (parameters and references of the sampled ball) and the
history `newton.newton.hst` (one record per cycle; columns of
coord/INTERFACES/newtonian_mode.md section 3). The second-moment tensor about the centre
of mass, C = I/M - X X^T, gives the semi-axes A_i = sqrt(5 c_i) (eigenvalues assigned to
the coordinate axis their eigenvector is closest to; the deformation axes are the
coordinate axes) and, for the sphere, R = sqrt(5 tr C/3), the radius of the homogeneous
ball with that moment.

Top-hat (cycloid through the Zel'dovich data of the sampled ball):
  t_ta, R_max  vertex of a parabola through R(t) where R > 0.98 max R;
  t_f          time at which R falls through f R_max(ref), f = 0.5, 0.25, 0.1 (linear
               interpolation between records), against the cycloid time of that radius;
  t_min, R_min vertex of a parabola through the 7 records around the smallest R (the
               softened collapse), against the cycloid collapse t_c;
  max |R/R_ref - 1| up to the reference time of R = 0.25 R_max on the way in;
  energy: max |K + W - E_0| / |W_0| up to t_0.25.
Ellipsoid (isolated homogeneous ellipsoid through the same data):
  t_1          first collapse: the axis whose c_i reaches its first minimum earliest;
               estimator (a) vertex of a parabola through c_i where A_i < 0.2 A_i(0) in
               that basin; (b) linear extrapolation to A_i = 0 of A_i(t) on the infall side
               between 0.35 and 0.15 A_i(0), with the bias of the same estimator on the
               reference curve removed;
  A_j(t_1), h_1 the other two semi-axes at the reference t_1 (records interpolated) and the
               hoop ratio of the two largest (ellipsoid.hoop_h), against the reference;
  t_2          first minimum of the second axis (indicative: after t_1 the run is a
               multi-stream pancake, the reference an idealized pass-through);
  energy until t_1.
"""
import argparse
import csv
import glob
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402

M_PATCH = th.M_K


# --------------------------------------------------------------------------- reading
PREP_DIRS = []      # directories of --prepare-only runs that hold ball.json of card runs


def find_meta(d):
    p = os.path.join(d, "ball.json")
    if os.path.exists(p):
        return p
    for pd in PREP_DIRS:
        q = os.path.join(pd, os.path.basename(os.path.normpath(d)), "ball.json")
        if os.path.exists(q):
            return q
    raise FileNotFoundError(f"no ball.json for {d}")


def load_case(d):
    with open(find_meta(d)) as f:
        meta = json.load(f)
    h = nw.read_newton_hst(os.path.join(d, "newton.newton.hst"))
    info = {}
    if os.path.exists(os.path.join(d, "case.json")):
        with open(os.path.join(d, "case.json")) as f:
            info = json.load(f)
    return meta, h, info


def moment_axes(h):
    """Times are code times; returns c[n, 3] per coordinate axis and trace."""
    I = nw.moment_tensor(h, 0)
    M = h["mass"]
    X = np.stack([h["X_x"], h["X_y"], h["X_z"]], axis=1)
    C = I / M[:, None, None] - X[:, :, None] * X[:, None, :]
    c = np.empty((len(M), 3))
    for k in range(len(M)):
        w, V = np.linalg.eigh(C[k])
        for j in range(3):
            c[k, np.argmax(np.abs(V[:, j]))] = w[j]
    return c, np.trace(C, axis1=1, axis2=2)


def vertex(t, y):
    a, b, _ = np.polyfit(t - t.mean(), y, 2)
    return float(-b / (2 * a) + t.mean()), float(np.polyval([a, b, _], -b / (2 * a)))


def crossing(t, y, level, after=None, falling=True):
    """First time y crosses level (falling or rising) after the given time."""
    idx = np.arange(len(t) - 1)
    if after is not None:
        idx = idx[t[:-1] >= after]
    for k in idx:
        y0, y1 = y[k], y[k + 1]
        if (falling and y0 >= level > y1) or (not falling and y0 <= level < y1):
            return float(t[k] + (level - y0) * (t[k + 1] - t[k]) / (y1 - y0))
    return float("nan")


# --------------------------------------------------------------------------- top-hat
def cycloid_time(cyc, f):
    """Time on the way in at which R = f R_max."""
    thv = 2 * np.pi - np.arccos(1.0 - 2.0 * f)
    return float(cyc["t_off"] + cyc["B"] * (thv - np.sin(thv)))


def analyse_tophat(d):
    meta, h, info = load_case(d)
    cyc = meta["reference"]["cycloid"]
    t = h["time"] + meta["t0"]
    _, tr = moment_axes(h)
    R = np.sqrt(5.0 * tr / 3.0)
    Rref = th.cycloid_R(cyc, t)
    m = R > 0.98 * R.max()
    t_ta, R_max = vertex(t[m], R[m])
    out = dict(name=os.path.basename(d), nx=meta["case"]["nx"], hxi=meta["case"]["hxi"],
               cfl=meta["case"]["cfl"], n=meta["n"], dx=meta["dx"], R0=cyc["R0"],
               t_ta_ref=cyc["t_ta"], t_ta=t_ta, t_ta_rel=t_ta / cyc["t_ta"] - 1,
               R_max_ref=cyc["R_max"], R_max=R_max, R_max_rel=R_max / cyc["R_max"] - 1,
               t_c_ref=cyc["t_c"], cycles=int(h["ncycle"][-1]),
               wall_s=info.get("wall_s"))
    for f in (0.5, 0.25, 0.1):
        tf = crossing(t, R, f * cyc["R_max"], after=t_ta)
        tr_ = cycloid_time(cyc, f)
        out[f"t_{f}"] = tf
        out[f"t_{f}_ref"] = tr_
        out[f"t_{f}_rel"] = tf / tr_ - 1
    k = int(np.argmin(R))
    sl = slice(max(0, k - 3), min(len(t), k + 4))
    t_min, _ = vertex(t[sl], R[sl] ** 2)
    out.update(t_min=t_min, t_min_rel=t_min / cyc["t_c"] - 1, R_min=float(R[k]),
               R_min_over_dx=float(R[k] / meta["dx"]),
               t_end_reached=float(t[-1]))
    upto = t <= out["t_0.25_ref"]
    out["R_err_max"] = float(np.max(np.abs(R[upto] / Rref[upto] - 1)))
    E = h["K"] + h["W"]
    out["E_err_max"] = float(np.max(np.abs(E[upto] - E[0])) / abs(h["W"][0]))
    return out, dict(t=t, R=R, Rref=Rref)


# --------------------------------------------------------------------------- ellipsoid
def reference_curve(meta, t_end):
    lams = np.asarray(meta["abg"])
    ref = el.evolve(lams, a0=meta["a0"], model="isolated", RL=(meta["r_vol"],) * 3,
                    M=M_PATCH, n_collapse=3, t_end=t_end,
                    max_step=(t_end - meta["t0"]) / 4000.0)
    tr, Ar = ref["t"], ref["A"].copy()
    sign = np.ones_like(Ar)
    for c in ref["collapses"]:                      # signed axes through the pass-through
        sign[tr > c["t"], c["axis"]] *= -1
    return ref, tr, sign * np.abs(Ar)


def first_min_basin(t, c, i):
    """Index range of the first local-minimum basin of c[:, i] (first record where c rises
    again after falling below 0.2^2 of its start)."""
    y = c[:, i]
    low = np.where(y < 0.04 * y[0])[0]
    if len(low) == 0:
        return None
    k0 = low[0]
    k = k0
    while k + 1 < len(y) and y[k + 1] < 0.04 * y[0]:
        k += 1
    return k0, k


def t_extrap(t, A, A0, lo=0.15, hi=0.35, after=None):
    """Infall-side linear fit of A(t) between lo and hi of A0, extrapolated to A = 0."""
    m = (A < hi * A0) & (A > lo * A0) & (np.gradient(A, t) < 0)
    if after is not None:
        m &= t >= after
    # keep the first contiguous stretch only
    idx = np.where(m)[0]
    if len(idx) < 3:
        return float("nan")
    br = np.where(np.diff(idx) > 1)[0]
    if len(br):
        idx = idx[:br[0] + 1]
    if len(idx) < 3:
        return float("nan")
    p = np.polyfit(t[idx], A[idx], 1)
    return float(-p[1] / p[0])


def analyse_ellipsoid(d):
    meta, h, info = load_case(d)
    t = h["time"] + meta["t0"]
    c, _ = moment_axes(h)
    A = np.sqrt(np.maximum(5.0 * c, 0.0))
    refc = meta["reference"]["ellipsoid_isolated"]["collapses"]
    t1r, ax1r = refc[0]["t"], refc[0]["axis"]
    ref, tr, Ar = reference_curve(meta, t[-1])
    # reference on the run's records
    Ai = np.stack([np.interp(t, tr, np.abs(Ar[:, i])) for i in range(3)], axis=1)
    cands = []
    for i in range(3):
        b = first_min_basin(t, c, i)
        if b is not None:
            cands.append((t[b[0]], i, b))
    out = dict(name=os.path.basename(d), deltaL=meta["deltaL"], e=meta["e"], p=meta["p"],
               nx=meta["case"]["nx"], hxi=meta["case"]["hxi"], rotate=meta["case"]["rotate"],
               n=meta["n"], dx=meta["dx"], half=meta["half_width"], t0=meta["t0"],
               t1_ref=t1r, axis_ref=ax1r, h1_ref=refc[0]["h"],
               A_t1_ref=sorted(refc[0]["A"])[1:], cycles=int(h["ncycle"][-1]),
               wall_s=info.get("wall_s"), t_end_reached=float(t[-1]))
    if len(refc) > 1:
        out.update(t2_ref=refc[1]["t"], axis2_ref=refc[1]["axis"])
    if not cands:
        out["t1"] = float("nan")
        return out, dict(t=t, A=A, tr=tr, Ar=Ar)
    cands.sort()
    _, ax1, (k0, k1) = cands[0]
    lo, hi = max(0, k0 - 1), min(len(t), k1 + 2)
    t1a, c1min = vertex(t[lo:hi], c[lo:hi, ax1])
    A0 = A[0, ax1]
    t1b_run = t_extrap(t, A[:, ax1], A0)
    t1b_ref = t_extrap(t, Ai[:, ax1], Ai[0, ax1])
    t1b = t1b_run - (t1b_ref - t1r)
    others = [j for j in range(3) if j != ax1]
    A_t1 = sorted(float(np.interp(t1r, t, A[:, j])) for j in others)
    h1 = float(el.hoop_h(np.array([0.0] + A_t1), M_PATCH))
    out.update(axis=int(ax1), axis_match=bool(ax1 == ax1r), t1_vertex=t1a,
               t1_vertex_rel=t1a / t1r - 1, t1_extrap=t1b, t1_extrap_rel=t1b / t1r - 1,
               A1_min=float(np.sqrt(max(5 * c1min, 0.0))),
               A1_min_over_dx=float(np.sqrt(max(5 * c1min, 0.0)) / meta["dx"]),
               A_t1=A_t1, A_t1_rel=[a / b - 1 for a, b in zip(A_t1, out["A_t1_ref"])],
               h1=h1, h1_rel=h1 / refc[0]["h"] - 1,
               h1_deltaL=h1 * meta["deltaL"], h1_ref_deltaL=refc[0]["h"] * meta["deltaL"])
    # second collapse (indicative)
    if len(refc) > 1:
        ax2 = refc[1]["axis"]
        b2 = first_min_basin(t, c, ax2) if ax2 != ax1 else None
        if b2 is not None:
            lo, hi = max(0, b2[0] - 1), min(len(t), b2[1] + 2)
            out["t2_vertex"], _ = vertex(t[lo:hi], c[lo:hi, ax2])
            out["t2_vertex_rel"] = out["t2_vertex"] / refc[1]["t"] - 1
    pre = t <= t1r
    E = h["K"] + h["W"]
    out["E_err_max_to_t1"] = float(np.max(np.abs(E[pre] - E[0])) / abs(h["W"][0]))
    early = t <= 0.8 * t1r
    out["A_err_max_to_0p8t1"] = float(np.max(np.abs(A[early] / Ai[early] - 1)))
    return out, dict(t=t, A=A, tr=tr, Ar=Ar)


# --------------------------------------------------------------------------- figures
def fig_tophat(rows, curves, out):
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 4.6))
    ax1 = fs.inch_axes(fig, 0.75, 2.35, 3.05, 2.05)
    ax2 = fs.inch_axes(fig, 0.75, 0.5, 3.05, 1.75)
    cols = fs.series_colors(len(rows))
    cyc_t = np.linspace(curves[0]["t"][0], rows[0]["t_c_ref"], 600)
    any_meta = rows[0]
    for r, cv, col in zip(rows, curves, cols):
        lab = f"$N_x={r['nx']}$, $h_\\xi={r['hxi']}$" + (f", cfl {r['cfl']}" if r["cfl"] != 0.2 else "")
        ax1.plot(cv["t"], cv["R"], color=col, lw=1.0, label=lab)
        upto = cv["t"] <= r["t_0.1_ref"]
        ax2.plot(cv["t"][upto], cv["R"][upto] / cv["Rref"][upto] - 1, color=col, lw=1.0)
    ax1.plot(curves[0]["t"], curves[0]["Rref"], **fs.GUIDE, label="cycloid")
    for key in ("t_ta_ref", "t_c_ref"):
        ax1.axvline(any_meta[key], **fs.MASK_LINE)
        ax2.axvline(any_meta[key], **fs.MASK_LINE)
    ax1.set_ylabel(r"$R/r_g$")
    ax1.set_xticklabels([])
    ax1.legend(loc="upper right", fontsize=6, ncol=1)
    ax2.set_xlabel(r"$t/(r_g/c)$")
    ax2.set_ylabel(r"$R/R_{\rm cyc}-1$")
    ax2.set_yscale("symlog", linthresh=1e-3)
    for ax in (ax1, ax2):
        ax.set_xlim(curves[0]["t"][0], 1.06 * any_meta["t_c_ref"])
    fs.save(fig, os.path.join(out, "fig_newton_tophat"))
    plt.close(fig)


def fig_tophat_conv(rows, out):
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.7))
    keys = [("t_ta_rel", r"$|t_{\rm ta}/t_{\rm ta,cyc}-1|$"),
            ("t_0.25_rel", r"$|t_{0.25}/t_{0.25,cyc}-1|$"),
            ("t_min_rel", r"$|t_{\min R}/t_{c}-1|$")]
    hx = sorted({r["hxi"] for r in rows})
    cols = dict(zip(hx, fs.series_colors(len(hx))))
    for k, (key, lab) in enumerate(keys):
        ax = fs.inch_axes(fig, 0.7 + k * 2.45, 0.5, 1.95, 2.0)
        for hv in hx:
            rr = sorted([r for r in rows if r["hxi"] == hv and r["cfl"] == 0.2],
                        key=lambda r: r["dx"])
            ax.loglog([r["dx"] for r in rr], [abs(r[key]) for r in rr], "o-", color=cols[hv],
                      ms=3, label=f"$h_\\xi={hv}$")
            for r in rr:
                if r[key] < 0:
                    ax.plot(r["dx"], abs(r[key]), "o", mfc="white", mec=cols[hv], ms=5)
        for r in rows:
            if r["cfl"] != 0.2:
                ax.plot(r["dx"], abs(r[key]), "s", color="k", ms=4, mfc="none",
                        label="cfl 0.1" if k == 0 else None)
        dxs = np.array(sorted({r["dx"] for r in rows}))
        ref = [abs(r[key]) for r in rows if r["dx"] == dxs.max()]
        if ref:
            y0 = np.median(ref)
            ax.plot(dxs, y0 * (dxs / dxs.max()) ** 2, **fs.THIN, ls=":", label=r"$\propto\Delta x^2$" if k == 0 else None)
            ax.plot(dxs, y0 * (dxs / dxs.max()), **fs.THIN, ls="--", label=r"$\propto\Delta x$" if k == 0 else None)
        ax.set_xlabel(r"$\Delta x/r_g$")
        ax.set_ylabel(lab)
        if k == 0:
            ax.legend(loc="lower right", fontsize=6)
    fs.save(fig, os.path.join(out, "fig_newton_tophat_conv"))
    plt.close(fig)


def fig_scan_axes(rows, curves, out, name):
    fs.use_style()
    n = len(rows)
    ncol = 3
    nrow = int(np.ceil(n / ncol))
    pw, ph = 2.3, 1.7
    fig = plt.figure(figsize=(0.6 + ncol * (pw + 0.35), 0.45 + nrow * (ph + 0.35)))
    for k, (r, cv) in enumerate(zip(rows, curves)):
        i, j = divmod(k, ncol)
        ax = fs.inch_axes(fig, 0.6 + j * (pw + 0.35), 0.45 + (nrow - 1 - i) * (ph + 0.35), pw, ph)
        for a, ls in zip(range(3), ("-", "--", ":")):
            ax.plot(cv["tr"] / r["t1_ref"], np.abs(cv["Ar"][:, a]) / r["half"] * 1.5, color="k", lw=1.0, ls=ls)
            ax.plot(cv["t"] / r["t1_ref"], cv["A"][:, a] / r["half"] * 1.5, color=fs.SERIES[a], lw=1.0, ls=ls,
                    alpha=0.85)
        ax.axvline(1.0, **fs.MASK_LINE)
        ax.set_xlim(cv["t"][0] / r["t1_ref"], cv["t"][-1] / r["t1_ref"])
        ax.set_ylim(0, None)
        ax.text(0.03, 0.06, r["name"] + f"\n$\\delta_L={r['deltaL']:g}$, $e={r['e']:.2g}$, $p={r['p']:.2g}$",
                transform=ax.transAxes, fontsize=6, va="bottom")
        if i == nrow - 1:
            ax.set_xlabel(r"$t/t_1^{\rm ref}$")
        if j == 0:
            ax.set_ylabel(r"$A_i/A_{\max}^{\rm ref}$")
    fs.save(fig, os.path.join(out, name))
    plt.close(fig)


def fig_scan_summary(rows, out):
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.7))
    base = [r for r in rows if r["nx"] == 128 and r["hxi"] == 0.025 and r["rotate"] is None
            and r["deltaL"] == 0.2 and r["p"] == 0.0]
    base.sort(key=lambda r: r["e"])
    ax = fs.inch_axes(fig, 0.7, 0.5, 2.0, 2.0)
    ee = np.linspace(0.02, 0.32, 60)
    ref_h = [el.first_collapse(1.0, e, 0.0)["h1"] for e in ee]
    ax.plot(ee, ref_h, **fs.GUIDE, label="ellipsoid ref.")
    ax.plot([r["e"] for r in base], [r["h1_deltaL"] for r in base], "o", color=fs.PAL["red"],
            ms=4, label="AthenaK, $128^3$")
    oth = [r for r in rows if r not in base and r["p"] == 0.0 and "t1" not in r or False]
    ax.set_xlabel("$e$ ($p=0$)")
    ax.set_ylabel(r"$h_1\,\delta_L$ (hoop line, $\delta_{L,\rm th}$)")
    ax.legend(loc="lower right", fontsize=6)
    ax2 = fs.inch_axes(fig, 3.35, 0.5, 2.0, 2.0)
    for r in rows:
        mk = "o" if (r["nx"] == 128 and r["hxi"] == 0.025) else ("s" if r["nx"] != 128 else "^")
        col = fs.PAL["blue"] if r["p"] == 0 else (fs.PAL["red"] if r["p"] > 0 else fs.PAL["yellow"])
        ax2.plot(r["e"] + (0.004 if r["nx"] == 64 else -0.004 if r["nx"] == 256 else 0.0),
                 100 * r["t1_vertex_rel"], mk, color=col, ms=3.5, mfc="none" if r.get("rotate") else col)
    ax2.axhline(0.0, **fs.THIN)
    ax2.set_xlabel("$e$")
    ax2.set_ylabel(r"$t_1/t_1^{\rm ref}-1$ [%]")
    ax3 = fs.inch_axes(fig, 6.0, 0.5, 1.85, 2.0)
    for r in rows:
        mk = "o" if (r["nx"] == 128 and r["hxi"] == 0.025) else ("s" if r["nx"] != 128 else "^")
        col = fs.PAL["blue"] if r["p"] == 0 else (fs.PAL["red"] if r["p"] > 0 else fs.PAL["yellow"])
        ax3.plot(r["e"], 100 * r["h1_rel"], mk, color=col, ms=3.5, mfc="none" if r.get("rotate") else col)
    ax3.axhline(0.0, **fs.THIN)
    ax3.set_xlabel("$e$")
    ax3.set_ylabel(r"$h_1/h_1^{\rm ref}-1$ [%]")
    fs.save(fig, os.path.join(out, "fig_newton_scan_summary"))
    plt.close(fig)


def fig_snapshots(d, out, label):
    paths = sorted(glob.glob(os.path.join(d, "newton.part.*.bin")))
    if not paths:
        return
    with open(find_meta(d)) as f:
        meta = json.load(f)
    t1r = meta["reference"]["ellipsoid_isolated"]["collapses"][0]["t"]
    snaps = [nw.read_snapshot(p) for p in paths]
    times = np.array([s[0] + meta["t0"] for s in snaps])
    pick = [0, int(np.argmin(np.abs(times - 0.8 * t1r))), int(np.argmin(np.abs(times - t1r))),
            len(snaps) - 1]
    fs.use_style()
    half = meta["half_width"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.35))
    rng = np.random.default_rng(0)
    for k, ip in enumerate(pick):
        t, _, x, _, m, _ = snaps[ip]
        sel = rng.choice(len(m), size=min(len(m), 40000), replace=False)
        ax = fs.inch_axes(fig, 0.55 + k * 1.85, 0.4, 1.75, 1.75)
        ax.plot(x[sel, 0], x[sel, 2], ",", color=fs.PAL["blue"], alpha=0.5)
        ax.set_xlim(-half, half)
        ax.set_ylim(-half, half)
        ax.set_aspect("equal")
        ax.set_title(f"$t/t_1^{{\\rm ref}}={(t + meta['t0']) / t1r:.3f}$", fontsize=7)
        ax.set_xlabel("$x/r_g$")
        if k == 0:
            ax.set_ylabel("$z/r_g$")
        else:
            ax.set_yticklabels([])
    fs.save(fig, os.path.join(out, f"fig_newton_snap_{label}"))
    plt.close(fig)


def write_csv(rows, path, keys):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for r in rows:
            w.writerow([r.get(k) for k in keys])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tophat", nargs="*", default=[])
    ap.add_argument("--scan", nargs="*", default=[])
    ap.add_argument("--snap-cases", default="e0p2,e0p1,e0p2_pm")
    ap.add_argument("--prep", nargs="*", default=[],
                    help="directories of --prepare-only runs (ball.json of card runs)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    PREP_DIRS.extend(a.prep)
    os.makedirs(a.out, exist_ok=True)
    res = {}
    if a.tophat:
        rows, curves = [], []
        dirs = []
        for td in a.tophat:
            dirs += glob.glob(os.path.join(td, "th_*"))
        for d in sorted(dirs, key=os.path.basename):
            if not os.path.exists(os.path.join(d, "newton.newton.hst")):
                continue
            r, cv = analyse_tophat(d)
            rows.append(r)
            curves.append(cv)
        res["tophat"] = rows
        write_csv(rows, os.path.join(a.out, "newton_tophat.csv"),
                  ["name", "nx", "hxi", "cfl", "n", "dx", "cycles", "wall_s", "t_ta_ref", "t_ta",
                   "t_ta_rel", "R_max_ref", "R_max", "R_max_rel", "t_0.5_ref", "t_0.5_rel",
                   "t_0.25_ref", "t_0.25_rel", "t_0.1_ref", "t_0.1_rel", "t_c_ref", "t_min",
                   "t_min_rel", "R_min", "R_min_over_dx", "R_err_max", "E_err_max"])
        fig_tophat(rows, curves, a.out)
        fig_tophat_conv(rows, a.out)
    if a.scan:
        rows, curves = [], []
        for sd in a.scan:
            for d in sorted(glob.glob(os.path.join(sd, "e*"))):
                if not os.path.exists(os.path.join(d, "newton.newton.hst")):
                    continue
                r, cv = analyse_ellipsoid(d)
                r["run_dir"] = os.path.basename(os.path.normpath(sd))
                rows.append(r)
                curves.append(cv)
                if r["name"] in a.snap_cases.split(","):
                    fig_snapshots(d, a.out, r["name"])
        res["scan"] = rows
        write_csv(rows, os.path.join(a.out, "newton_scan.csv"),
                  ["name", "run_dir", "deltaL", "e", "p", "nx", "hxi", "rotate", "n", "dx",
                   "cycles", "wall_s", "t0", "t1_ref", "axis_ref", "axis", "t1_vertex",
                   "t1_vertex_rel", "t1_extrap", "t1_extrap_rel", "A_t1_ref", "A_t1",
                   "A_t1_rel", "h1_ref", "h1", "h1_rel", "h1_ref_deltaL", "h1_deltaL",
                   "A1_min_over_dx", "t2_ref", "t2_vertex", "t2_vertex_rel",
                   "A_err_max_to_0p8t1", "E_err_max_to_t1"])
        fig_scan_axes(rows, curves, a.out, "fig_newton_scan_axes")
        fig_scan_summary(rows, a.out)
    with open(os.path.join(a.out, "newton_results.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
        f.write("\n")
    for k, rows in res.items():
        for r in rows:
            print(k, json.dumps({kk: (round(v, 6) if isinstance(v, float) else v)
                                 for kk, v in r.items() if not isinstance(v, list)}))


if __name__ == "__main__":
    main()
