#!/usr/bin/env python3
"""Error analysis of the Schwarzschild (a = 0) runs of the geodesic campaign (part A).

Reads runs/geodesic/schw/*/ (analytic metric: 'ks' spherical and 'cks' Cartesian Kerr-Schild)
and runs/geodesic/schw_mesh/*/ (Cartesian Kerr-Schild on the AthenaK mesh, and the same on the
virtual lattice for comparison), with the exact solutions of problems/schwarzschild/ref/orbits.json
(make_schwarzschild_reference.py), and writes
  problems/schwarzschild/results/schw_summary.json      all numbers
  problems/schwarzschild/results/schw_convergence.json  figure data (errors vs dt and vs dx)
  problems/schwarzschild/results/schw_histories.npz     sampled error histories (diagnostic figures):
      'A_<orbit>__t', 'A_<orbit>__xref' sample times and reference (r, theta, phi);
      'A--<run>__<q>' / 'Am--<run>__<q>' (analytic / mesh+lattice runs), q = dpos (position
      error at the samples), dE, dLz, dQ (max over the records between samples), x (position at
      the samples, dt = 0.01 and mesh runs), dalpha, dgamma (mesh reconstruction error)

Position error: max(|dr|/M, |dtheta|, |dphi|) against the exact state, at t_end ('final') and the
maximum over the checkpoints (every 50 M; 4 M for the plunge).  Cartesian runs are converted to
(r, theta, phi).  Invariants E, L_z, Q with the exact metric, relative to the initial values
(absolute for Q of the equatorial circular orbit, whose Q is 0).

Usage: python3 analysis/geodesic/analyze_schwarzschild.py
"""

from __future__ import annotations

import time

import numpy as np

from geo_common import (RUNS, SCHW_RESULTS, envelope, fit_order, hist_summary, invariant_errors,
                        kerr, load_json, nearest_index, pairwise_orders, position_error, radius,
                        reference_samples_ks, run_log_info, read_traj, read_trajmet,
                        sampled_errors, save_json, schw_ref)

A = 0.0
M = 1.0


def run_dirs(group):
    d = RUNS / group
    if not d.exists():
        return []
    # finished runs only (normal termination in the newest log)
    return sorted(p for p in d.iterdir() if (p / "run.json").exists() and run_log_info(p)["ok"])


SAMPLE_DT = {"circ": 2.0, "ecc": 2.0, "plunge": 0.08}


def reference_samples(ref):
    """Sample times and reference (r, theta, phi) per orbit (DOP853 between exact checkpoints)."""
    out = {}
    for orbit, o in ref.items():
        cp = o["checkpoints"]
        n = int(round(o["t_end"] / SAMPLE_DT[orbit]))
        t_s = np.arange(n + 1) * SAMPLE_DT[orbit]
        t_s[-1] = o["t_end"]
        out[orbit] = (t_s, reference_samples_ks(A, np.array(cp["t"]), np.array(cp["x_ks"]),
                                                np.array(cp["u_ks"]), t_s))
    return out


def analyse(rd, ref, refs, samp):
    meta = load_json(rd / "run.json")
    m = meta["meta"]
    b = dict(name=meta["name"], meta=m, overrides=meta["overrides"], input=meta["input"],
             log=run_log_info(rd))
    if (rd / "geo.nrpic.hst").exists():
        b["hist"] = hist_summary(rd)
    tr = read_traj(rd)
    o = ref[m["orbit"]]
    cp = o["checkpoints"]
    tc = np.array(cp["t"])
    xe = np.array(cp["x_ks"])
    sysn = m["system"]
    inv = invariant_errors(sysn, tr["x"], tr["u"], A, M)
    se = sampled_errors(sysn, A, tr, inv, *refs[m["orbit"]])
    tag = ("Am--" if meta["name"].startswith("schw_mesh/") else "A--") + meta["name"].split("/")[1]
    keep = ["dpos", "dE", "dLz", "dQ"]
    if m["metric"] in ("mesh", "lat") or abs(m["dt"] - 0.01) < 1e-12:
        keep.append("x")
    for q in keep:
        samp[f"{tag}__{q}"] = se[q]
    b["max_pos_err_samples"] = float(np.nanmax(se["dpos"]))
    idx = nearest_index(tr["t"], tc)
    d = np.abs(position_error(sysn, tr["x"][idx], xe, A))
    dmax = d.max(axis=1)
    # total angular momentum L^2 = Q + L_z^2 (spherical symmetry)
    L2 = inv["Q"] + inv["Lz"] ** 2
    r = radius(sysn, tr["x"], A)
    b.update(n_records=len(tr["t"]), t_last=float(tr["t"][-1]),
             max_time_mismatch_checkpoints=float(np.max(np.abs(tr["t"][idx] - tc))),
             max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
             dQ_relative=inv["dQ_relative"], max_dL=float(np.max(np.abs(np.sqrt(L2) / np.sqrt(L2[0]) - 1))),
             inv0=inv["ref"],
             final_pos_err=float(dmax[-1]), final_pos_err_components=d[-1].tolist(),
             max_pos_err=float(dmax.max()), pos_err_checkpoints=dmax.tolist(),
             r_range=[float(r.min()), float(r.max())], r_final=float(r[-1]))
    if m["metric"] == "mesh" and (rd / "geo.trajmet.bin").exists():
        tm = read_trajmet(rd)
        n = min(len(tm["t"]), len(tr["t"]))
        ex = kerr.adm("cks", tr["x"][:n], A, M, derivs=False)
        g6 = ex.gamma[:, [0, 0, 0, 1, 1, 2], [0, 1, 2, 1, 2, 2]]
        b["reconstruction_err"] = dict(
            alpha=float(np.max(np.abs(tm["alpha"][:n] - ex.alpha))),
            beta=float(np.max(np.abs(tm["beta"][:n] - ex.beta))),
            gamma=float(np.max(np.abs(tm["g"][:n] - g6))))
        t_s = refs[m["orbit"]][0]
        samp[f"{tag}__dalpha"] = envelope(tr["t"][:n], tm["alpha"][:n] - ex.alpha, t_s)
        samp[f"{tag}__dgamma"] = envelope(tr["t"][:n], np.max(np.abs(tm["g"][:n] - g6), axis=1), t_s)
    return b


def main():
    T0 = time.time()
    ref = schw_ref()["orbits"]
    refs = reference_samples(ref)
    samp = {}
    for orbit, (t_s, x_s) in refs.items():
        samp[f"A_{orbit}__t"] = t_s
        samp[f"A_{orbit}__xref"] = x_s
    res = {}
    for group in ("schw", "schw_mesh"):
        for rd in run_dirs(group):
            b = analyse(rd, ref, refs, samp)
            res[b["name"]] = b
            h = b.get("hist", {})
            print(f"{b['name']:34s} dE {b['max_dE']:.3e} dLz {b['max_dLz']:.3e} dQ {b['max_dQ']:.3e} "
                  f"final {b['final_pos_err']:.3e} max {b['max_pos_err']:.3e} "
                  f"unconv {h.get('n_unconverged_steps')} maxit {h.get('max_iterations')}"
                  + (f" recon {b['reconstruction_err']}" if "reconstruction_err" in b else ""),
                  flush=True)
    # dt convergence (analytic metric)
    conv_dt = {}
    for orbit in ref:
        for metric in ("ks", "cks"):
            for pusher in ("mid", "bsym", "bchol"):
                rows = sorted((v["meta"]["dt"], v["final_pos_err"], v["max_pos_err"], v["max_dE"],
                               v["max_dQ"], v["max_dLz"])
                              for v in res.values()
                              if v["name"].startswith("schw/") and v["meta"]["orbit"] == orbit
                              and v["meta"]["metric"] == metric and v["meta"]["pusher"] == pusher)
                if len(rows) < 2:
                    continue
                dts, ef, em, dE, dQ, dLz = (list(c) for c in zip(*rows))
                conv_dt[f"{orbit}_{pusher}_{metric}"] = dict(
                    orbit=orbit, pusher=pusher, metric=metric, dt=dts, final_err=ef, max_err=em,
                    dE=dE, dQ=dQ, dLz=dLz,
                    order_final=fit_order(dts, ef)[0], order_max=fit_order(dts, em)[0],
                    order_dE=fit_order(dts, dE)[0], order_dQ=fit_order(dts, dQ)[0],
                    pairwise_final=pairwise_orders(dts, ef))
    # dx convergence (mesh and lattice), with the analytic Cartesian run at the same dt
    conv_dx = {}
    cmp = {}
    for orbit in ("circ", "ecc"):
        for pusher in ("mid", "bsym"):
            for metric in ("mesh", "lat"):
                rows = sorted((v["meta"]["dx"], v["final_pos_err"], v["max_pos_err"], v["max_dE"],
                               v["max_dQ"], v["max_dLz"], v["meta"]["dt"])
                              for v in res.values()
                              if v["name"].startswith("schw_mesh/") and v["meta"]["orbit"] == orbit
                              and v["meta"]["metric"] == metric and v["meta"]["pusher"] == pusher)
                if len(rows) < 2:
                    continue
                dxs, ef, em, dE, dQ, dLz, dts = (list(c) for c in zip(*rows))
                ana = res.get(f"schw/{orbit}_{pusher}_cks_dt{dts[0]:g}")
                conv_dx[f"{orbit}_{pusher}_{metric}"] = dict(
                    orbit=orbit, pusher=pusher, metric=metric, dx=dxs, dt=dts[0], final_err=ef,
                    max_err=em, dE=dE, dQ=dQ, dLz=dLz,
                    order_final=fit_order(dxs, ef)[0], order_max=fit_order(dxs, em)[0],
                    order_dE=fit_order(dxs, dE)[0], pairwise_final=pairwise_orders(dxs, ef),
                    pairwise_max=pairwise_orders(dxs, em),
                    analytic_cks_same_dt=None if ana is None else dict(
                        final_err=ana["final_pos_err"], max_err=ana["max_pos_err"], dE=ana["max_dE"],
                        dQ=ana["max_dQ"]))
            for dx in (0.5, 0.25, 0.125):
                a1 = RUNS / f"schw_mesh/{orbit}_{pusher}_mesh_dx{dx:g}"
                a2 = RUNS / f"schw_mesh/{orbit}_{pusher}_lat_dx{dx:g}"
                if (a1 / "geo.traj.bin").exists() and (a2 / "geo.traj.bin").exists():
                    t1, t2 = read_traj(a1), read_traj(a2)
                    n = min(len(t1["t"]), len(t2["t"]))
                    cmp[f"{orbit}_{pusher}_dx{dx:g}"] = dict(
                        max_abs_dx=float(np.max(np.abs(t1["x"][:n] - t2["x"][:n]))),
                        max_abs_du=float(np.max(np.abs(t1["u"][:n] - t2["u"][:n]))),
                        bitwise_identical=bool(np.array_equal(t1["x"][:n], t2["x"][:n])
                                               and np.array_equal(t1["u"][:n], t2["u"][:n])),
                        n_records=[len(t1["t"]), len(t2["t"])])
    out = dict(runs=res, dt_convergence=conv_dt, dx_convergence=conv_dx, mesh_vs_lattice=cmp,
               orbits={k: dict(description=v["description"], params=v["params"], t_end=v["t_end"],
                               invariants=v["invariants"], initial_state=v["initial_state"],
                               final_state=v["final_state"],
                               **{q: v[q] for q in ("periods", "turning_points", "pericenter_t",
                                                    "periapsis_advance_per_radial_period",
                                                    "horizon_crossing_t", "r_end", "potential_peak",
                                                    "check") if q in v})
                       for k, v in ref.items()})
    save_json(SCHW_RESULTS / "schw_summary.json", out)
    np.savez_compressed(SCHW_RESULTS / "schw_histories.npz",
                        **{k: (v if k.endswith("__t") else np.asarray(v, dtype=np.float32))
                           for k, v in samp.items()})
    save_json(SCHW_RESULTS / "schw_convergence.json",
              dict(dt=conv_dt, dx=conv_dx, mesh_vs_lattice=cmp))
    for k, c in conv_dt.items():
        print(f"dt-order {k:22s} final {c['order_final']:.3f} max {c['order_max']:.3f} "
              f"dE {c['order_dE']:.3f} pairwise {np.round(c['pairwise_final'], 3).tolist()}")
    for k, c in conv_dx.items():
        print(f"dx-order {k:22s} final {c['order_final']:.3f} max {c['order_max']:.3f} "
              f"dE {c['order_dE']:.3f} pairwise {np.round(c['pairwise_final'], 3).tolist()}")
    print(f"wrote {SCHW_RESULTS} ({time.time() - T0:.0f} s)")


if __name__ == "__main__":
    main()
