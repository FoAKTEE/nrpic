#!/usr/bin/env python3
"""Test A2X of Track A (periodic_threshold JOURNAL 2026-11-25 18:21 PST, batch 23): a first-crossing measure of the
triaxial peak S1L that does not depend on the coordinates.

    a2_invariant.py --run DIR --out DIR [--box 20] [--n 64] [--gmax 1.5]

(i) Event. The Lagrangian lattice index q of every particle is fixed from snapshot 0 (as a2_crossing.py). For each
snapshot the Jacobian J = det(dx/dq) of the map q -> x is formed on the lattice, with forward differences (the cell
spanned by q, q + h e_1, q + h e_2, q + h e_3) and with centred differences, periodic separations unwrapped. A shell
crossing is J <= 0 in some cell. Under a smooth orientation-preserving change of the spatial coordinates
J' = det(dy/dx) J with det(dy/dx) > 0, so the sign of J, and the snapshot at which min J first becomes <= 0, do
not depend on the shift.
(ii) Clock. The dust's proper time since the initial slice is bounded below on every worldline by
tau_lb(t) = int_0^t alpha_min(t') / W_max dt' (alpha_min: column 16 of <base>.nrpic.hst, the lowest lapse on the
mesh; W_max = sqrt(1 + gmax max |u_i|^2) over all snapshots, gmax a margin for gamma^ij) and bounded above by
int_0^t alpha_max dt' when the history has alpha_max, else reported as the coordinate time. The probe particle's
own proper time (column 15) is reported beside them. Conversion t_c = 2/3 + tau, t/t_H = t_c / ((2/3) 6^1.5).
Writes a2x.json and fig_a2x.png.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TH = (2.0 / 3.0) * 6.0 ** 1.5          # cosmic time at a_H = 6 (H_i = 1 at a = 1, matter era)


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
    return time, rec[:, 0:3].copy(), rec[:, 3:6].copy(), tag.copy()


def tau_over_tH(tau):
    return (2.0 / 3.0 + np.asarray(tau)) / TH


def uniq(h):
    keep, tn = [], np.inf
    for i in range(len(h) - 1, -1, -1):
        if h[i, 0] < tn:
            keep.append(i)
            tn = h[i, 0]
    return h[keep[::-1]]


def jacobians(grid, L, h):
    """grid[i, j, k, c]: position component c of lattice point (i, j, k). Forward and centred det(dx/dq)."""
    out = {}
    for kind in ("fwd", "ctr"):
        M = np.empty(grid.shape[:3] + (3, 3))
        for d in range(3):
            if kind == "fwd":
                dv = np.roll(grid, -1, axis=d) - grid
                base = h
            else:
                dv = np.roll(grid, -1, axis=d) - np.roll(grid, 1, axis=d)
                base = 2.0 * h
            for c in range(3):
                unpert = base if c == d else 0.0
                v = dv[..., c]
                v = v - L * np.round((v - unpert) / L)
                M[..., c, d] = v / base
        out[kind] = np.linalg.det(M)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--box", type=float, default=20.0)
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--gmax", type=float, default=1.5)
    ap.add_argument("--reference", type=float, default=4.35, help="Zel'dovich first-axis t/t_H (second derivation)")
    ap.add_argument("--band", type=float, nargs=2, default=[3.4, 5.0])
    ap.add_argument("--label", default="S1L", help="member name in the figure title (batch 28)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L, n = a.box, a.n
    h = L / n
    files = sorted(glob.glob(os.path.join(a.run, "peak.part.*.bin")))
    t0, x0, u0, tag0 = read_snapshot(files[0])
    off = np.array([np.median(np.mod(x0[:, d] + L / 2, h)) for d in range(3)])
    idx = np.rint((x0 + L / 2 - off) / h).astype(int) % n
    lin = idx[:, 0] + n * (idx[:, 1] + n * idx[:, 2])
    one_to_one = len(np.unique(lin)) == len(lin) == n ** 3
    order = np.argsort(tag0)
    tag_sorted, lin_sorted = tag0[order], lin[order]
    rows, umax = [], 0.0
    ulat, negcells = [], []          # |u| in lattice order per snapshot; forward-J <= 0 cells per snapshot
    for f in files:
        t, x, u, tag = read_snapshot(f)
        pos = np.searchsorted(tag_sorted, tag)
        li = lin_sorted[pos]
        grid = np.full((n ** 3, 3), np.nan)
        grid[li] = x
        grid = grid.reshape(n, n, n, 3, order="F")
        J = jacobians(grid, L, h)
        ul = np.full(n ** 3, np.nan)
        ul[li] = np.sqrt(np.sum(u * u, axis=1))
        ulat.append(ul.reshape(n, n, n, order="F"))
        negcells.append(np.argwhere(J["fwd"] <= 0))
        umax = max(umax, float(np.sqrt(np.max(np.sum(u * u, axis=1)))))   # running maximum to this snapshot
        rec = dict(t=t, n_particles=int(len(tag)), u_max_to_here=umax,
                   u_p99=float(np.sqrt(np.percentile(np.sum(u * u, axis=1), 99.0))))
        for kind, Jk in J.items():
            k = int(np.nanargmin(Jk))
            ijk = np.unravel_index(k, Jk.shape)
            rec[f"minJ_{kind}"] = float(np.nanmin(Jk))
            rec[f"n_negJ_{kind}"] = int(np.sum(Jk <= 0))
            rec[f"argminJ_{kind}_x"] = [float(v) for v in grid[ijk]]
        rows.append(rec)
        print(f"t {t:8.3f}  minJ fwd {rec['minJ_fwd']:+.4f} ({rec['n_negJ_fwd']} cells <= 0)  "
              f"ctr {rec['minJ_ctr']:+.4f} ({rec['n_negJ_ctr']})  at {np.round(rec['argminJ_fwd_x'], 2)}", flush=True)
    # batch 23 correction after the first run (A-20261126-022220-99b7be8): W_max over ALL snapshots is set by
    # particles deep in the late collapse (|u| ~ 1.6e3 at t ~ 190) and makes the bound empty; the bound at the
    # snapshot t_k uses the running maximum of |u| over the snapshots up to t_k (the largest |u| between two
    # snapshots is not recorded: that is the JUDGEMENT of this bound)
    W_max = float(np.sqrt(1.0 + a.gmax * umax ** 2))
    hn = uniq(np.loadtxt(os.path.join(a.run, "peak.nrpic.hst"), comments="#", ndmin=2))
    ta, am, tp = hn[:, 0], hn[:, 15], hn[:, 14]
    int_alpha = np.concatenate([[0.0], np.cumsum(0.5 * (am[1:] + am[:-1]) * np.diff(ta))])
    for r in rows:
        r["W_max_to_here"] = float(np.sqrt(1.0 + a.gmax * r["u_max_to_here"] ** 2))
        r["tau_lb"] = float(np.interp(r["t"], ta, int_alpha)) / r["W_max_to_here"]
        r["tau_probe"] = float(np.interp(r["t"], ta, tp))
        r["alpha_min"] = float(np.interp(r["t"], ta, am))
        r["t_over_tH_coord"] = float(tau_over_tH(r["t"]))
        r["t_over_tH_lb"] = float(tau_over_tH(r["tau_lb"]))
        r["t_over_tH_probe"] = float(tau_over_tH(r["tau_probe"]))
    res = dict(run=os.path.abspath(a.run), lattice_one_to_one=bool(one_to_one), W_max=W_max, u_max=umax,
               gmax=a.gmax, reference_t_over_tH=a.reference, band=a.band, rows=rows, first={})
    for kind in ("fwd", "ctr"):
        m = np.array([r[f"minJ_{kind}"] for r in rows])
        j = np.nonzero(m <= 0)[0]
        if len(j) and j[0] > 0:
            k = int(j[0])
            last, first = rows[k - 1], rows[k]
            res["first"][kind] = dict(
                last_positive=dict(t=last["t"], minJ=last[f"minJ_{kind}"], coord=last["t_over_tH_coord"],
                                   tau_lb=last["t_over_tH_lb"], probe=last["t_over_tH_probe"]),
                first_nonpositive=dict(t=first["t"], minJ=first[f"minJ_{kind}"], coord=first["t_over_tH_coord"],
                                       tau_lb=first["t_over_tH_lb"], probe=first["t_over_tH_probe"]))
        else:
            res["first"][kind] = None
    # batch 23, local bound: the worldlines that cross first are the corners of the cells with J <= 0 at the first
    # non-positive snapshot; their largest |u| over the snapshots before it bounds their W (gamma^ij <= gmax)
    fw = res["first"].get("fwd")
    if fw:
        k = [r["t"] for r in rows].index(fw["first_nonpositive"]["t"])
        cells = negcells[k]
        corners = [cells]
        for d in range(3):
            c2 = cells.copy()
            c2[:, d] = (c2[:, d] + 1) % n
            corners.append(c2)
        corners = np.unique(np.concatenate(corners), axis=0)
        u_loc = max(float(np.nanmax(ulat[j][tuple(corners.T)])) for j in range(k))
        W_loc = float(np.sqrt(1.0 + a.gmax * u_loc ** 2))
        lp_t = fw["last_positive"]["t"]
        tau_loc = float(np.interp(lp_t, ta, int_alpha)) / W_loc
        # is the probe particle (nearest to probe_x = 0.001 at t = 0, whose proper time the code integrates in
        # column 15) one of the first-crossing worldlines? lattice distance of its index to the corner set
        p0 = np.argmin(np.sum((x0 - 0.001) ** 2, axis=1))
        pidx = idx[p0]
        dl = np.abs(corners - pidx)
        dl = np.minimum(dl, n - dl)
        fw["probe"] = dict(lattice_index=[int(v) for v in pidx], x0=[float(v) for v in x0[p0]],
                           lattice_distance_to_corner_set=int(np.min(np.max(dl, axis=1))),
                           corner_set_x0_extent=[[float((c.min() + 0.5) * h - L / 2), float((c.max() + 0.5) * h - L / 2)]
                                                 for c in corners.T],
                           tau_probe_t_over_tH_last_positive=fw["last_positive"]["probe"],
                           tau_probe_t_over_tH_first_nonpositive=fw["first_nonpositive"]["probe"])
        fw["local"] = dict(n_cells=int(len(cells)), n_corner_particles=int(len(corners)), u_max=u_loc, W_max=W_loc,
                           tau_lb_last_positive=tau_loc, t_over_tH_lb_last_positive=float(tau_over_tH(tau_loc)),
                           int_alpha_min_to_last_positive=float(np.interp(lp_t, ta, int_alpha)))
        for r in rows:
            r["t_over_tH_lb_local"] = float(tau_over_tH(float(np.interp(r["t"], ta, int_alpha)) / W_loc))

        lp = fw["local"]["t_over_tH_lb_last_positive"]
        res["verdict"] = dict(global_bound_at_last_positive=fw["last_positive"]["tau_lb"],
            dust_clock_lower_bound_at_last_positive=lp,
            above_band_edge=bool(lp > a.band[1]),
            crossing_snapshot_after_5p17=bool(fw["last_positive"]["coord"] > 5.17 or fw["first_nonpositive"]["coord"] > 5.17))
    json.dump(res, open(os.path.join(a.out, "a2x.json"), "w"), indent=1)
    print("W_max", round(W_max, 5), "u_max", round(umax, 4), "one-to-one", one_to_one)
    print(json.dumps(res["first"], indent=1))
    print(json.dumps(res.get("verdict"), indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, HERE)
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH if hasattr(fs, "FULL_WIDTH") else 7.0, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.88, wspace=0.28)
    ax = axs[0]
    for kind, key, col, lab in (("fwd", "t_over_tH_coord", fs.PAL["red"], "forward J, coordinate time"),
                                ("fwd", "t_over_tH_lb_local" if fw else "t_over_tH_lb", fs.PAL["blue"],
                                 "forward J, dust-clock bound (first-crossing particles)"),
                                ("ctr", "t_over_tH_coord", "0.4", "centred J, coordinate time")):
        ax.plot([r[key] for r in rows], [r[f"minJ_{kind}"] for r in rows], "o-", ms=3, lw=1.0, color=col, label=lab)
    ax.axhline(0, color="0.5", lw=0.6)
    ax.axvspan(a.band[0], a.band[1], color="0.85", zorder=0, label="predicted band (A2)")
    ax.axvline(a.reference, color="0.3", ls="--", lw=0.8, label=f"Zel'dovich {a.reference:g}")
    ax.set_xscale("log")
    ax.set_ylim(-0.6, 1.1)
    ax.set_xlabel(r"$t/t_H$")
    ax.set_ylabel(r"min over the lattice of $\det(\partial x/\partial q)$")
    ax.legend(fontsize=6, loc="lower left")
    ax.set_title(f"{a.label}: sign of the Lagrangian Jacobian (shift-invariant)", fontsize=8)
    ax = axs[1]
    tt = np.array([r["t"] for r in rows])
    ax.plot(tt, [r["t_over_tH_coord"] for r in rows], "o-", ms=3, color=fs.PAL["red"], label="coordinate time")
    ax.plot(tt, [r["t_over_tH_probe"] for r in rows], "s-", ms=3, color=fs.PAL["yellow"], label="probe particle")
    ax.plot(tt, [r["t_over_tH_lb"] for r in rows], "^-", ms=3, color=fs.PAL["blue"], label=r"global bound $\int\alpha_{\min}/W_{\max}$")
    if fw:
        ax.plot(tt, [r["t_over_tH_lb_local"] for r in rows], "v-", ms=3, color=fs.PAL["green"],
                label="bound for the first-crossing particles")
    ax.axhspan(a.band[0], a.band[1], color="0.85", zorder=0)
    if fw:
        ax.axvspan(fw["last_positive"]["t"], fw["first_nonpositive"]["t"], color=fs.PAL["red"], alpha=0.15,
                   label="first J <= 0 bracket")
    ax.set_xlabel("coordinate time t")
    ax.set_ylabel(r"dust proper time as $t/t_H$")
    ax.legend(fontsize=6, loc="upper left")
    ax.set_title("clocks", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_a2x.png"), dpi=150)


if __name__ == "__main__":
    main()
