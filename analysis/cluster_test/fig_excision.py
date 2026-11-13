#!/usr/bin/env python3
"""(e) Excision bookkeeping for the plunging family (mesh metric, alpha_exc = 0.62).

- number and rest mass of excised (and escaped) particles versus time from the history,
  compared with the fraction predicted from the exact invariants of the initial data
  (radial potential, make_cluster.classify);
- for every removed particle, the exact Kerr-Schild radius and lapse at the last snapshot
  before removal (snap_dt = 1 M), and, as a check, the radius at which the exact geodesic
  started from that snapshot first has alpha < alpha_exc on the cycle grid (dt = 0.05 M):
  the code removes a particle at the push that starts from a position with interpolated
  lapse below alpha_exc;
- the invariant errors of the excised particles at their last snapshot.

Figure: figs/excision.{pdf,png}
Numbers: results/excision.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

import ct_common as C
from nrpic import figstyle as fs
from nrpic import geodesic

H = C.dc.H


def continue_to_excision(x, u, a, dt=C.DT, nsub=8, nmax=400):
    """Exact geodesic (RK4, dt/nsub) from (x, u) until the exact lapse at a cycle boundary
    drops below alpha_exc.  Returns (number of cycles, x at removal)."""
    x = x.copy(); u = u.copy()
    n = len(x)
    done = np.zeros(n, dtype=bool)
    ncyc = np.full(n, -1)
    xr = np.full_like(x, np.nan)
    h = dt / nsub
    for j in range(nmax + 1):
        al = C.lapse(x, a)
        hit = (~done) & (al < C.ALPHA_EXC)
        ncyc[hit] = j
        xr[hit] = x[hit]
        done |= hit
        if done.all():
            break
        act = ~done
        xa, ua = x[act], u[act]
        for _ in range(nsub):
            k1x, k1u = geodesic.rhs("cks", xa, ua, a, C.M)
            k2x, k2u = geodesic.rhs("cks", xa + 0.5 * h * k1x, ua + 0.5 * h * k1u, a, C.M)
            k3x, k3u = geodesic.rhs("cks", xa + 0.5 * h * k2x, ua + 0.5 * h * k2u, a, C.M)
            k4x, k4u = geodesic.rhs("cks", xa + h * k3x, ua + h * k3u, a, C.M)
            xa = xa + h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            ua = ua + h / 6 * (k1u + 2 * k2u + 2 * k3u + k4u)
        x[act], u[act] = xa, ua
    return ncyc, xr


def analyse(name, a):
    h = C.history(name)
    files = C.snapshots(name)
    t0, x0, u0, m0, tag0, _ = C.read_snap(files[0])
    N = len(tag0)
    last_x = np.full((N, 3), np.nan)
    last_u = np.full((N, 3), np.nan)
    last_t = np.full(N, np.nan)
    alive_prev = np.ones(N, dtype=bool)
    removed_after = np.full(N, np.nan)       # time of the first snapshot without it
    for f in files:
        t, x, u, m, tag, sp = C.read_snap(f)
        alive = np.zeros(N, dtype=bool)
        alive[tag] = True
        gone = alive_prev & ~alive
        removed_after[gone] = t
        last_x[tag] = x
        last_u[tag] = u
        last_t[tag] = t
        alive_prev = alive
    removed = np.isfinite(removed_after)
    r_last = kerr_r(last_x, a)
    escaped = removed & (np.max(np.abs(last_x), axis=1) > 50.0)
    excised = removed & ~escaped
    E0, L0, Q0 = C.invariants(x0, u0, a)
    El, Ll, Ql = C.invariants(last_x[excised], last_u[excised], a)
    ncyc, xr = continue_to_excision(last_x[excised], last_u[excised], a)
    r_rem = kerr_r(xr, a)
    pred = np.load(os.path.join(C.RUNS, "ic", f"plunge_a{a}_n10000.class.npy"))
    rec = dict(
        N=N, n_excised_hist=int(h[-1, H["n_excised"]]), n_escaped_hist=int(h[-1, H["n_escaped"]]),
        m_excised_hist=float(h[-1, H["m_excised"]]), m_tot=float(h[0, H["sum_m"]]),
        n_excised_snap=int(excised.sum()), n_escaped_snap=int(escaped.sum()),
        n_pred_plunge=int((pred == 1).sum()), n_pred_escape=int((pred == 2).sum()),
        confusion=dict(pred_plunge_and_excised=int(((pred == 1) & excised).sum()),
                       pred_plunge_not_excised=int(((pred == 1) & ~excised).sum()),
                       pred_bound_but_excised=int(((pred == 0) & excised).sum()),
                       pred_bound_but_escaped=int(((pred == 0) & escaped).sum())),
        t_first_excision=float(np.nanmin(removed_after[excised])) if excised.any() else None,
        t_last_excision=float(np.nanmax(removed_after[excised])) if excised.any() else None,
        r_last_pct=np.percentile(r_last[excised], [0, 10, 50, 90, 100]).tolist(),
        alpha_last_pct=np.percentile(C.lapse(last_x[excised], a),
                                     [0, 10, 50, 90, 100]).tolist(),
        r_removal_pct=np.nanpercentile(r_rem, [0, 10, 50, 90, 100]).tolist(),
        n_no_removal_found=int(np.sum(ncyc < 0)),
        cycles_after_snapshot_pct=np.percentile(ncyc[ncyc >= 0], [0, 50, 100]).tolist(),
        dE_last_pct=np.percentile(np.abs(El / E0[excised] - 1), [50, 90, 99, 100]).tolist(),
        dL_last_pct=np.percentile(np.abs(Ll / L0[excised] - 1), [50, 90, 99, 100]).tolist(),
        dQ_last_pct=np.percentile(np.abs(Ql / Q0[excised] - 1), [50, 90, 99, 100]).tolist(),
        cos_theta_last_max=float(np.max(np.abs(last_x[excised, 2]) / r_last[excised])))
    data = dict(h=h, r_last=r_last[excised], r_rem=r_rem, t_rem=removed_after[excised],
                dE=np.abs(El / E0[excised] - 1), dL=np.abs(Ll / L0[excised] - 1),
                dQ=np.abs(Ql / Q0[excised] - 1), pred_frac=float(np.mean(pred == 1)))
    return rec, data


def kerr_r(x, a):
    return C.kerr.cks_radius(x, a)


def main():
    fs.use_style()
    res = {}
    fig, axes = plt.subplots(3, 2, figsize=(8.0, 7.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.07, top=0.93, hspace=0.38,
                        wspace=0.22)
    for j, a in enumerate((0.0, 0.9)):
        name = f"plunge_a{a}_mid"
        if not C.exists(name):
            continue
        rec, d = analyse(name, a)
        res[name] = rec
        h = d["h"]
        t = h[:, H["time"]]
        N = rec["N"]
        ax = axes[0, j]
        ax.plot(t, h[:, H["n_excised"]] / N, color=fs.PAL["red"], label="excised, number")
        ax.plot(t, h[:, H["m_excised"]] / rec["m_tot"], color=fs.PAL["red"], ls="--",
                label="excised, rest mass")
        ax.plot(t, h[:, H["n_escaped"]] / N, color=fs.PAL["yellow"], label="left the mesh")
        ax.axhline(d["pred_frac"], **fs.GUIDE, label="plunging (exact invariants)")
        ax.set_xlabel("$t/M$", labelpad=-1)
        ax.set_title(f"$a = {a}\\,M$, $N = 10^4$")
        if j == 0:
            ax.set_ylabel("fraction of $N$, of $M_0$")
        ax.set_xscale("symlog", linthresh=10.0)
        ax.set_xlim(0, t[-1])
        # radii
        ax = axes[1, j]
        rp = 1 + np.sqrt(1 - a * a)
        r_exc = 2.0 / (1 / C.ALPHA_EXC ** 2 - 1)      # equatorial alpha = alpha_exc
        bins = np.linspace(0.0, 4.0, 81)
        ax.hist(d["r_last"], bins=bins, histtype="step", color=fs.PAL["red"], lw=1.5,
                label="last snapshot")
        ax.hist(d["r_rem"][np.isfinite(d["r_rem"])], bins=bins, histtype="step",
                color=fs.PAL["blue"], lw=1.5, label="removal (exact continuation)")
        ax.axvline(rp, **fs.MASK_LINE)
        ax.axvline(r_exc, **fs.GUIDE)
        ax.text(rp, ax.get_ylim()[1] * 0.92, " $r_+$", fontsize=8, va="top")
        ax.set_xlabel("Kerr-Schild $r/M$", labelpad=-1)
        if j == 0:
            ax.set_ylabel("particles per bin")
        # invariant errors of the excised particles at their last snapshot
        ax = axes[2, j]
        for key, col in (("dE", fs.PAL["red"]), ("dL", fs.PAL["yellow"]),
                         ("dQ", fs.PAL["green"])):
            ax.scatter(d["r_last"], np.maximum(d[key], 1e-16), s=1.5, lw=0, color=col,
                       rasterized=True,
                       label={"dE": r"$|\Delta E/E|$", "dL": r"$|\Delta L_z/L_z|$",
                              "dQ": r"$|\Delta Q/Q|$"}[key])
        ax.set_yscale("log")
        ax.axvline(rp, **fs.MASK_LINE)
        ax.set_xlabel("Kerr-Schild $r/M$ at the last snapshot", labelpad=-1)
        if j == 0:
            ax.set_ylabel("error at the last snapshot")
    axes[0, 0].legend(loc="center right", fontsize=8)
    axes[1, 0].legend(loc="upper right", fontsize=8)
    axes[2, 0].legend(loc="upper right", fontsize=8, markerscale=4)
    fs.save(fig, os.path.join(C.FIGS, "excision"))
    plt.close(fig)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    with open(os.path.join(C.HERE, "results", "excision.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(k, json.dumps(v, indent=1))


if __name__ == "__main__":
    main()
