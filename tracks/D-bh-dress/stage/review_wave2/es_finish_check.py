#!/usr/bin/env python3
"""Lead's wave-2b re-check of the ES-1 / V-1 outcome (JOURNAL.md, lead-wave2b predictions Y1-Y6).

Written without the helper's analysis code (es_runs/analyse.py, tools/es_extra.py,
tools/probe_fronts.py). Reads only the registered outputs of
  ES-1  D-20261115-172726-60ba4c2   (es.*)
  V-1   D-20261115-172730-c6d151b   (v1.*)
and the exact references of es_runs/results/predictions.json (data run
D-20261115-170213-d2c2131, checked as W1). File layouts: docs/FORMATS.md (part.*.bin) and
athenak/src/particles/nrpic_io.cpp (traj.bin: 8 doubles; trajmet.bin: 17 doubles).

Areal radius of a tracer: with a spherically symmetric 3-metric written in Cartesian
coordinates, gamma_ij = A n_i n_j + B (delta_ij - n_i n_j), so B = (tr gamma - n.gamma.n)/2
and R = r sqrt(B).

Writes es_finish_check.json and es_finish_check.png into --out (default $NRPIC_RUN_DIR).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.normpath(os.path.join(TRACK, "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = {"ES-1": (os.path.join(SCR, "D-20261115-172726-60ba4c2"), "es"),
        "V-1": (os.path.join(SCR, "D-20261115-172730-c6d151b"), "v1")}
PRED = os.path.join(TRACK, "es_runs", "results", "predictions.json")
NGROUP = 14   # tracers per group (tags 14 g .. 14 g + 13)
R0S = [6, 10, 20, 28, 36, 40, 48, 56, 66, 78]


def wall_exact(tau):
    return (36.0 ** 1.5 + 1.5 * math.sqrt(2.0) * np.asarray(tau)) ** (2.0 / 3.0)


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t, m = a[:, 1], a[:, 2]
    # the finder writes t = 0 twice (t = 0 and 0.5 carry the same row); keep unique times
    _, idx = np.unique(t, return_index=True)
    return t[idx], m[idx], a[idx, 10]


def read_traj(d, base):
    tr = np.fromfile(os.path.join(d, base + ".traj.bin"), dtype="<f8").reshape(-1, 8)
    tm = np.fromfile(os.path.join(d, base + ".trajmet.bin"), dtype="<f8").reshape(-1, 17)
    assert tr.shape[0] == tm.shape[0], "traj and trajmet differ in length"
    assert np.array_equal(tr[:, 0], tm[:, 0]) and np.array_equal(tr[:, 1], tm[:, 1])
    x = tr[:, 2:5]
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    g = tm[:, 6:12]   # xx xy xz yy yz zz
    G = np.empty((len(g), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2] = g[:, 0], g[:, 1], g[:, 2]
    G[:, 1, 0], G[:, 1, 1], G[:, 1, 2] = g[:, 1], g[:, 3], g[:, 4]
    G[:, 2, 0], G[:, 2, 1], G[:, 2, 2] = g[:, 2], g[:, 4], g[:, 5]
    tr_g = G[:, 0, 0] + G[:, 1, 1] + G[:, 2, 2]
    ngn = np.einsum("ni,nij,nj->n", n, G, n)
    B = 0.5 * (tr_g - ngn)
    R = r * np.sqrt(B)
    return {"t": tr[:, 0], "tag": tr[:, 1].astype(int), "x": x, "r": r, "R": R,
            "alpha": tm[:, 2], "tau": tm[:, 12]}


def read_hst(d, base):
    return np.loadtxt(os.path.join(d, base + ".nrpic.hst"), comments="#")


def read_snap(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic == b"NRPSNAP1", magic
        t = np.frombuffer(f.read(8), "<f8")[0]
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        _cyc = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tags = np.frombuffer(f.read(4 * n), "<i4")
    return t, rec, tags


def axis_class(x0):
    """True for a tracer on a coordinate axis (two coordinates ~ 0) at t = 0."""
    return np.sum(np.abs(x0) < 1e-6 * np.linalg.norm(x0)) == 2


def crossing(tj, tag):
    s = tj["tag"] == tag
    R, tau, t = tj["R"][s], tj["tau"][s], tj["t"][s]
    k = np.nonzero(R < 2.0)[0]
    if len(k) == 0:
        return None, None, float(tau[-1]), float(t[-1])
    k = k[0]
    w = (R[k - 1] - 2.0) / (R[k - 1] - R[k])
    return (float(tau[k - 1] + w * (tau[k] - tau[k - 1])),
            float(t[k - 1] + w * (t[k] - t[k - 1])), float(tau[-1]), float(t[-1]))


def model_1plog(H0, tmax=200.0, dt=1e-3):
    """homogeneous 1+log with zero shift: d alpha/dt = 6 alpha H, da/dt = alpha H a."""
    n = int(tmax / dt)
    t = np.linspace(0.0, tmax, n + 1)
    al, a = np.empty(n + 1), np.empty(n + 1)
    al[0], a[0] = 1.0, 1.0

    def f(y):
        A, aa = y
        H = H0 * aa ** -1.5
        return np.array([6.0 * A * H, A * H * aa])
    y = np.array([1.0, 1.0])
    for i in range(n):
        k1 = f(y)
        k2 = f(y + 0.5 * dt * k1)
        k3 = f(y + 0.5 * dt * k2)
        k4 = f(y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        al[i + 1], a[i + 1] = y
    return t, al, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pred = json.load(open(PRED))
    out = {"runs": {k: v[0] for k, v in RUNS.items()}}

    # ---- Y1 horizon mass
    hs = {}
    for k, (d, b) in RUNS.items():
        t, m, rad = read_summary(os.path.join(d, b + ".horizon_summary_0.txt"))
        hs[k] = (t, m, rad)
    y1 = {}
    for k, (t, m, _) in hs.items():
        i0 = int(np.argmin(np.abs(t - 100.0)))
        w = (t >= 100.0) & (t <= 200.0)
        dr = m[w] / m[i0] - 1.0
        y1[k] = {"t0": float(t[i0]), "M100_minus_1": float(m[i0] - 1.0),
                 "max_abs_drift_100_200": float(np.max(np.abs(dr))),
                 "t_of_max": float(t[w][np.argmax(np.abs(dr))]),
                 "t_last": float(t[-1]),
                 "max_abs_drift_100_165": float(np.max(np.abs(dr[t[w] <= 165.0])))}
    tE, mE, _ = hs["ES-1"]
    tV, mV, _ = hs["V-1"]
    common = np.intersect1d(tE, tV)
    common = common[(common >= 100.0) & (common <= 200.0)]
    dE = np.interp(common, tE, mE) / mE[np.argmin(np.abs(tE - 100))] - 1
    dV = np.interp(common, tV, mV) / mV[np.argmin(np.abs(tV - 100))] - 1
    y1["max_abs_diff_ES_minus_V"] = float(np.max(np.abs(dE - dV)))
    y1["ratio_to_V1_floor"] = y1["max_abs_diff_ES_minus_V"] / y1["V-1"]["max_abs_drift_100_200"]
    # first time the two horizon masses differ by more than 1e-9
    ct = np.intersect1d(tE, tV)
    dd = np.abs(np.interp(ct, tE, mE) - np.interp(ct, tV, mV))
    y1["first_t_split_1e-9"] = float(ct[np.argmax(dd > 1e-9)])
    out["Y1"] = y1

    # ---- Y2-Y4 from trajectories
    tj = {k: read_traj(d, b) for k, (d, b) in RUNS.items()}
    y2, y3, y4 = {}, {}, {}
    for k, T in tj.items():
        tags0 = T["tag"][T["t"] == T["t"][0]]
        x0 = {int(g): T["x"][(T["t"] == T["t"][0]) & (T["tag"] == g)][0] for g in tags0}
        # wall
        wall = {"axis": 0.0, "diag": 0.0}
        werr = {}
        for g in range(56, 70):
            s = (T["tag"] == g) & (T["tau"] <= 200.0)
            e = T["R"][s] / wall_exact(T["tau"][s]) - 1.0
            cls = "axis" if axis_class(x0[g]) else "diag"
            wall[cls] = max(wall[cls], float(np.max(np.abs(e))))
            werr[g] = (T["tau"][s], e, cls)
        y2[k] = {"max_rel_err_tau_le_200": max(wall.values()), "by_class": wall,
                 "tau_end": float(np.max(T["tau"][(T["tag"] >= 56) & (T["tag"] < 70)]))}
        tj[k]["werr"] = werr
        # crossings
        cr = {}
        for gi, R0 in enumerate(R0S[:3]):
            taus, ts, tend = [], [], []
            for g in range(gi * NGROUP, gi * NGROUP + NGROUP):
                tc, tt, te, _ = crossing(T, g)
                tend.append(te)
                if tc is not None:
                    taus.append(tc)
                    ts.append(tt)
            exact = pred["tau_reach_2M_es" if k == "ES-1" else "tau_reach_2M_v1"][
                f"group{gi}_R0={R0}"]
            cr[f"R0={R0}"] = {"n_crossed": len(taus),
                             "tau_mean": float(np.mean(taus)) if taus else None,
                             "tau_min": float(np.min(taus)) if taus else None,
                             "tau_max": float(np.max(taus)) if taus else None,
                             "t_mean": float(np.mean(ts)) if ts else None,
                             "exact": exact,
                             "tau_end_max": float(np.max(tend))}
        y3[k] = cr
        # +x tracer of R0 = 48 M (group 6)
        g48 = [g for g in range(6 * NGROUP, 7 * NGROUP)
               if x0[g][0] > 0 and axis_class(x0[g])][0]
        s = T["tag"] == g48
        y4[k] = {"tag_plus_x_R0_48": g48, "tau_at_end": float(T["tau"][s][-1]),
                 "t_end": float(T["t"][s][-1]),
                 "tau_group6_end_range": [
                     float(min(T["tau"][T["tag"] == g][-1] for g in range(84, 98))),
                     float(max(T["tau"][T["tag"] == g][-1] for g in range(84, 98)))]}
    out["Y2"], out["Y3"] = y2, y3

    # lapse at the plateau probe (column 13 = alpha_probe at x = 46 M)
    H0 = pred["plateau_H"]
    tm_, alm, _am = model_1plog(H0)
    hst = {k: read_hst(d, b) for k, (d, b) in RUNS.items()}
    for k, h in hst.items():
        y4[k]["alpha_probe46"] = {f"t={tq:g}": float(np.interp(tq, h[:, 0], h[:, 12]))
                                  for tq in (10.0, 25.0, 50.0, 100.0, 150.0, 200.0)}
    y4["model_1plog"] = {f"t={tq:g}": float(np.interp(tq, tm_, alm))
                         for tq in (10.0, 25.0, 50.0, 100.0, 150.0, 200.0)}
    out["Y4"] = y4

    # ---- Y5 dust against the wall, ES-1 snapshots at t = 100 and 200 M
    d, b = RUNS["ES-1"]
    y5 = {}
    TE = tj["ES-1"]
    for fn in ("es.part.00004.bin", "es.part.00008.bin"):
        ts, rec, tags = read_snap(os.path.join(d, fn))
        dust = rec[:, 6] > 1e-20
        xd = rec[dust, :3]
        rd = np.linalg.norm(xd, axis=1)
        nd = xd / rd[:, None]
        margins = []
        for g in range(56, 70):
            s = (TE["tag"] == g)
            j = int(np.argmin(np.abs(TE["t"][s] - ts)))
            xw = TE["x"][s][j]
            rw = np.linalg.norm(xw)
            cosang = nd @ (xw / rw)
            near = cosang > math.cos(math.radians(10.0))
            margins.append((g, float(np.min(rd[near]) - rw), int(np.sum(near)),
                            float(abs(TE["t"][s][j] - ts))))
        y5[f"t={ts:g}"] = {"min_margin": min(m[1] for m in margins),
                           "per_tracer": margins,
                           "n_dust_inside_wall_cone": int(sum(1 for m in margins if m[1] < 0)),
                           "rmin_dust": float(rd.min())}
    out["Y5"] = y5

    # ---- Y6 cost from the manifests
    y6 = {}
    for k, (dd_, _b) in RUNS.items():
        rid = os.path.basename(dd_)
        man = json.load(open(os.path.join(TRACK, "runs", rid, "manifest.json")))
        y6[k] = man["resources"]["gpu_hours"]
    y6["sum"] = sum(v for v in y6.values())
    out["Y6"] = y6

    with open(os.path.join(args.out, "es_finish_check.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    col = fs.series_colors(3)
    fig, axs = plt.subplots(2, 3, figsize=(11.0, 6.2))
    ax = axs[0, 0]
    for c, (k, (t, m, _)) in zip(col, hs.items()):
        i0 = int(np.argmin(np.abs(t - 100.0)))
        w = t >= 60.0
        ax.plot(t[w], (m[w] / m[i0] - 1.0) * 1e4, color=c, label=k)
    ax.plot(common, (dE - dV) * 1e4, color=col[2], ls="--", label="ES-1 minus V-1")
    ax.axhline(0.3, color="0.5", lw=0.6, ls=":")
    ax.axhline(-0.3, color="0.5", lw=0.6, ls=":")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$10^4\,[M_{\rm AH}(t)/M_{\rm AH}(100M)-1]$")
    ax.legend(loc="lower left")
    ax.set_title(r"(a) horizon mass, $t_0 = 100M$")

    ax = axs[0, 1]
    for k, ls in (("ES-1", "-"), ("V-1", "--")):
        for g, (tau, e, cls) in tj[k]["werr"].items():
            ax.plot(tau, e * 1e3, color=col[0] if cls == "axis" else col[1], ls=ls, lw=0.7)
    ax.axhline(3.0, color="0.5", lw=0.6, ls=":")
    ax.axhline(-3.0, color="0.5", lw=0.6, ls=":")
    ax.set_xlabel(r"$\tau/M$")
    ax.set_ylabel(r"$10^3\,(R/R_w^{\rm exact}-1)$")
    ax.set_title("(b) wall tracers")
    ax.text(0.03, 0.05, "axis blue, diagonal red;\nsolid ES-1, dashed V-1", transform=ax.transAxes)

    ax = axs[0, 2]
    T = tj["ES-1"]
    for gi in range(3):
        for g in range(gi * NGROUP, gi * NGROUP + NGROUP, 3):
            s = T["tag"] == g
            ax.plot(T["tau"][s], T["R"][s], color=col[gi], lw=0.7)
    for gi, R0 in enumerate(R0S[:3]):
        ax.axvline(pred["tau_reach_2M_es"][f"group{gi}_R0={R0}"], color=col[gi], ls=":",
                   lw=0.8)
    ax.axhline(2.0, color="0.3", lw=0.6)
    ax.set_yscale("log")
    ax.set_xlabel(r"$\tau/M$")
    ax.set_ylabel(r"$R/M$ (ES-1)")
    ax.set_title(r"(c) $R_0 = 6, 10, 20M$ (ES-1)")
    ax.text(0.03, 0.05, "exact crossings dotted", transform=ax.transAxes)

    ax = axs[1, 0]
    for c, (k, h) in zip(col, hst.items()):
        ax.plot(h[:, 0], h[:, 12], color=c, label=f"{k}, probe $x = 46M$")
    ax.plot(tm_, alm, color="0.4", ls="--", label="homogeneous 1+log model")
    ax.set_ylim(0, 4)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha$")
    ax.legend(loc="upper left")
    ax.set_title("(d) lapse in the dust region")

    ax = axs[1, 1]
    for i, (key, v) in enumerate(y5.items()):
        gs = [m[0] for m in v["per_tracer"]]
        ms = [m[1] for m in v["per_tracer"]]
        ax.plot(gs, ms, "o", color=col[i], label=key.replace("t=", "t = ") + " M")
    ax.axhline(0.0, color="0.3", lw=0.6)
    ax.set_xlabel("wall tracer tag")
    ax.set_ylabel(r"$(\min r_{\rm dust} - r_{\rm wall})/M$, cone $10^\circ$")
    ax.legend()
    ax.set_title("(e) dust outside the wall (ES-1)")

    ax = axs[1, 2]
    for c, (k, (t, _m, rad)) in zip(col, hs.items()):
        ax.plot(t, rad, color=c, label=k)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"mean radius$/M$ (M/8 region to $6M$)")
    ax.axhline(6.0, color="0.5", lw=0.6, ls=":")
    ax.legend()
    ax.set_title("(f) horizon coordinate radius")
    fig.tight_layout()
    fs.save(fig, os.path.join(args.out, "es_finish_check"))
    print(json.dumps({k: out[k] for k in ("Y1", "Y2", "Y3", "Y4", "Y6")}, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_tracer"}
                      for k, v in y5.items()}, indent=1))


if __name__ == "__main__":
    main()
