#!/usr/bin/env python3
"""Test A2 of Track A (SCOPE A2; decision 0039 item 2(a); periodic_threshold JOURNAL 2026-11-25 07:15 PST):
first shell crossing of the triaxial peak S1L against the Zel'dovich time of its first axis.

    a2_crossing.py --run DIR --out DIR [--box 20] [--n 64]

Reads the full particle snapshots <run>/peak.part.*.bin (docs/FORMATS.md: time, n, then n records of
x, u, m and n tags). The Lagrangian lattice index of every particle is fixed from snapshot 0 by rounding
its position to the lattice of spacing h = box/n (checked to be one-to-one). For each later snapshot and
each axis d the separation of lattice neighbours along d, Delta_d = x_d(q + h e_d) - x_d(q) (periodic),
is divided by h; a shell crossing along d is Delta_d <= 0. The first crossing time along each axis is
the linear interpolation of the minimum over the lattice between the last snapshot with min > 0 and the
first with min <= 0. Coordinate time is read as cosmic time (relaxed lapse with reference 1; H_i = 1 at
a_i = 1, matter era): t/t_H = (1 + 3 t / 2) / 6^(3/2) with a_H = 6 (k = eps_i = 1; DESIGN.md section 1).
Writes a2.json and fig_a2_crossing.png.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
    return time, rec[:, 0:3].copy(), tag.copy()


CLOCK = "coord"


def t_over_tH(t):
    # batch 20: --clock newton reads the time as the conformal time of the Newtonian mode, a = (1 + eta/2)^2
    if CLOCK == "newton":
        return (1.0 + 0.5 * np.asarray(t)) ** 3 / 6.0 ** 1.5
    return (1.0 + 1.5 * np.asarray(t)) / 6.0 ** 1.5


def scale_factor(t):
    if CLOCK == "newton":
        return (1.0 + 0.5 * np.asarray(t)) ** 2
    return (1.0 + 1.5 * np.asarray(t)) ** (2.0 / 3.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--box", type=float, default=20.0)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--clock", choices=["coord", "newton"], default="coord",
                    help="batch 20: newton = conformal time of the Newtonian mode (a = (1 + eta/2)^2)")
    ap.add_argument("--label", default="S1L")
    ap.add_argument("--overlay", action="append", default=[], help="batch 20: a2.json of other runs to draw (min along z)")
    a = ap.parse_args()
    global CLOCK
    CLOCK = a.clock
    os.makedirs(a.out, exist_ok=True)
    L, n = a.box, a.n
    h = L / n
    files = sorted(glob.glob(os.path.join(a.run, "peak.part.*.bin")))
    t0, x0, tag0 = read_snapshot(files[0])
    # lattice offset: positions modulo h cluster around one value per axis
    off = np.array([np.median(np.mod(x0[:, d] + L / 2, h)) for d in range(3)])
    idx = np.rint((x0 + L / 2 - off) / h).astype(int) % n
    lin = idx[:, 0] + n * (idx[:, 1] + n * idx[:, 2])
    one_to_one = len(np.unique(lin)) == len(lin) == n ** 3
    disp0 = float(np.max(np.abs((x0 + L / 2 - off) / h - np.rint((x0 + L / 2 - off) / h))))
    lat_of_tag = dict(zip(tag0.tolist(), lin.tolist()))
    rows = []
    for f in files:
        t, x, tag = read_snapshot(f)
        grid = np.full((n ** 3, 3), np.nan)
        li = np.array([lat_of_tag[int(g)] for g in tag])
        grid[li] = x
        grid = grid.reshape(n, n, n, 3, order="F")      # index (i, j, k) with lin = i + n j + n^2 k
        rec = dict(t=t, t_over_tH=float(t_over_tH(t)), a=float(scale_factor(t)), n_particles=int(len(tag)))
        for d, ax in enumerate("xyz"):
            dl = np.roll(grid[..., d], -1, axis=d) - grid[..., d]
            dl = dl - L * np.round((dl - h) / L)          # periodic: the unperturbed separation is +h
            r_ = dl / h
            k = np.nanargmin(r_)
            rec[f"min_{ax}"] = float(np.nanmin(r_))
            rec[f"argmin_{ax}"] = [float(v) for v in grid.reshape(-1, 3, order="F")[np.ravel_multi_index(
                np.unravel_index(k, r_.shape), (n, n, n), order="F")]]
            rec[f"n_crossed_{ax}"] = int(np.sum(r_ <= 0))
        rows.append(rec)
        print(f"t {t:8.3f}  t/tH {rec['t_over_tH']:6.3f}  min dx {rec['min_x']:+.3f} dy {rec['min_y']:+.3f} "
              f"dz {rec['min_z']:+.3f}  crossed x,y,z {rec['n_crossed_x']} {rec['n_crossed_y']} {rec['n_crossed_z']}"
              f"  N {rec['n_particles']}")
    first = {}
    for ax in "xyz":
        m = np.array([r[f"min_{ax}"] for r in rows])
        tt = np.array([r["t"] for r in rows])
        j = np.nonzero(m <= 0)[0]
        if len(j) and j[0] > 0:
            k = j[0]
            w = m[k - 1] / (m[k - 1] - m[k])
            tc = tt[k - 1] + w * (tt[k] - tt[k - 1])
            first[ax] = dict(t_interp=float(tc), t_over_tH_interp=float(t_over_tH(tc)),
                             bracket_t=[float(tt[k - 1]), float(tt[k])],
                             bracket_t_over_tH=[float(t_over_tH(tt[k - 1])), float(t_over_tH(tt[k]))])
        else:
            first[ax] = None
    # clocks (measurement added after the first reading, A-20261125-151629-bb77171): proper time of the
    # lowest lapse (alpha_min of <base>.nrpic.hst, integrated in coordinate time), the probe particle's
    # proper time, and the volume-mean lapse of <base>.region.hst integrated (the background clock)
    clocks = {}
    try:
        hn = np.loadtxt(os.path.join(a.run, "peak.nrpic.hst"), comments="#", ndmin=2)
        hr = np.loadtxt(os.path.join(a.run, "peak.region.hst"), comments="#", ndmin=2)
        def uniq(h):
            keep, tn = [], np.inf
            for i in range(len(h) - 1, -1, -1):
                if h[i, 0] < tn:
                    keep.append(i)
                    tn = h[i, 0]
            return h[keep[::-1]]
        hn, hr = uniq(hn), uniq(hr)
        ta, am = hn[:, 0], hn[:, 15]
        tau_min = np.concatenate([[0.0], np.cumsum(0.5 * (am[1:] + am[:-1]) * np.diff(ta))])
        tb, ab = hr[:, 0], hr[:, 5]
        tau_bg = np.concatenate([[0.0], np.cumsum(0.5 * (ab[1:] + ab[:-1]) * np.diff(tb))])
        for ax in "xyz":
            if first.get(ax):
                tc = first[ax]["t_interp"]
                first[ax]["tau_alpha_min"] = float(np.interp(tc, ta, tau_min))
                first[ax]["tau_probe"] = float(np.interp(tc, ta, hn[:, 14]))
                first[ax]["t_background"] = float(np.interp(tc, tb, tau_bg))
                first[ax]["alpha_min_at_t"] = float(np.interp(tc, ta, am))
                for k_ in ("tau_alpha_min", "tau_probe", "t_background"):
                    first[ax][k_ + "_over_tH"] = float(t_over_tH(first[ax][k_]))
        clocks = dict(note="alpha_min col 16 of nrpic.hst; tau_probe col 15; mean_alpha_coord col 6 of region.hst")
    except (OSError, ValueError, IndexError) as e:
        clocks = dict(error=str(e))
    res = dict(run=os.path.abspath(a.run), clocks=clocks, lattice_one_to_one=bool(one_to_one), lattice_offset=off.tolist(),
               max_initial_displacement_over_h=disp0, rows=rows, first_crossing=first,
               zeldovich_first_axis_t_over_tH=4.2, band=[3.4, 5.0], clock=CLOCK, label=a.label,
               zeldovich_lambda=dict((ax, 1.0 - rows[0][f"min_{ax}"]) for ax in "xyz"),
               zeldovich_a_sc_z=1.0 / (1.0 - rows[0]["min_z"]),
               zeldovich_t_over_tH_z=float((1.0 / (1.0 - rows[0]["min_z"]) / 6.0) ** 1.5))
    json.dump(res, open(os.path.join(a.out, "a2.json"), "w"), indent=1)
    print("lattice one-to-one:", one_to_one, " max |initial displacement|/h:", round(disp0, 3))
    print("first crossing:", json.dumps(first, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, HERE)
    import figstyle as fs
    fs.use_style()
    fig, ax_ = plt.subplots(1, 1, figsize=(fs.COL_WIDTH if hasattr(fs, "COL_WIDTH") else 3.4, 2.8))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.17, top=0.9)
    tt = np.array([r["t_over_tH"] for r in rows])
    cols = {"x": fs.PAL["blue"], "y": fs.PAL["yellow"], "z": fs.PAL["red"]}
    for axn in "xyz":
        ax_.plot(tt, [r[f"min_{axn}"] for r in rows], "o-", ms=3, color=cols[axn], label=f"min $\\Delta_{axn}/h$")
    # batch 20: the Zel'dovich line of the first axis from snapshot 0 (1 - lambda_z a), and overlays
    tz = np.geomspace(max(tt.min(), 0.05), tt.max(), 200)
    az = 6.0 * tz ** (2.0 / 3.0)
    ax_.plot(tz, 1.0 - (1.0 - rows[0]["min_z"]) * az, ls=":", color=cols["z"], lw=0.9, label="Zel'dovich $z$")
    for k_, ov in enumerate(a.overlay):
        o = json.load(open(ov))
        ax_.plot([r["t_over_tH"] for r in o["rows"]], [r["min_z"] for r in o["rows"]], "s--", ms=2, lw=0.7,
                 color=["0.2", "0.55"][k_ % 2], label=f"{o.get('label', 'S1L (GR)')} min $\\Delta_z/h$")
    ax_.set_ylim(-0.6, 1.1)
    ax_.axhline(0, color="0.5", lw=0.6)
    ax_.axvspan(3.4, 5.0, color="0.85", zorder=0, label="predicted band")
    ax_.axvline(4.2, color="0.4", ls="--", lw=0.8)
    ax_.set_xscale("log")
    ax_.set_xlabel(r"$t/t_H$ (coordinate time as cosmic time)" if CLOCK == "coord" else r"$t/t_H$ (cosmic time of the Newtonian background)")
    ax_.set_ylabel(r"min neighbour separation / $h$")
    ax_.set_title(f"A2: {a.label} first shell crossing", fontsize=8)
    ax_.legend(fontsize=6)
    fig.savefig(os.path.join(a.out, "fig_a2_crossing.png"), dpi=150)


if __name__ == "__main__":
    main()
