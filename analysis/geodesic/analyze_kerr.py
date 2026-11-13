#!/usr/bin/env python3
"""Error analysis of the Kerr (a = 0.9) runs of the geodesic campaign (parts B, C, D, E).

Reads runs/geodesic/{kerr_passage,kerr_passage_cpu,kerr_bl,kerr_mesh}/*/ (written by
run_campaign.py) and the exact references problems/kerr/ref/initial_conditions.json, and writes
  problems/kerr/results/kerr_summary.json      all numbers (tables of docs/results_geodesic.md)
  problems/kerr/results/ks_passage_histories.npz  r(t), positions and invariant errors of the
                                                  dt = 0.01 M passage runs (figure data)
  problems/kerr/results/bl_trajectories.npz    decimated BL trajectories (figure data)
  problems/kerr/results/kerr_exact_extra.json  exact states computed here (cache)

Invariants are evaluated with the exact metric of the run's coordinate system (nrpic.kerr);
errors are relative to the run's initial values.  The final-position error is
max(|dr|/M, |dtheta|, |dphi|) against the exact (Mino-time quadrature) final state, with phi
unwrapped to the exact value; Cartesian runs are converted to spherical KS first.

Usage: python3 analysis/geodesic/analyze_kerr.py [--parts B C D E]
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import mpmath as mp
import numpy as np

from geo_common import (KERR_DIR, KERR_RESULTS, RUNS, envelope, final_position_error, fit_order,
                        hist_summary, reference_samples_ks, sampled_errors,
                        invariant_errors, kerr, kerr_ref, load_json, local_extrema,
                        pairwise_orders, position_error, radius, run_log_info, read_traj,
                        read_trajmet, save_json, to_rthph, unwrap_to)

A = 0.9
M = 1.0
EXTRA_JSON = KERR_RESULTS / "kerr_exact_extra.json"


def run_dirs(group):
    d = RUNS / group
    if not d.exists():
        return []
    # finished runs only (normal termination in the newest log)
    return sorted(p for p in d.iterdir() if (p / "run.json").exists() and run_log_info(p)["ok"])


def basic(rundir):
    meta = load_json(rundir / "run.json")
    info = run_log_info(rundir)
    out = dict(name=meta["name"], meta=meta["meta"], overrides=meta["overrides"],
               input=meta["input"], log=info)
    if (rundir / "geo.nrpic.hst").exists():
        out["hist"] = hist_summary(rundir)
    return out


# ------------------------------------------------------------------------------------------
# exact states not stored in the reference JSON (cached)
# ------------------------------------------------------------------------------------------

def exact_extra(kr, need_mesh_times):
    cache = load_json(EXTRA_JSON) if EXTRA_JSON.exists() else {}
    changed = False
    # pericentre phases of the BL orbits (exact, at the exact pericentre Mino times)
    for key in ("bl_equatorial_eccentric", "bl_inclined"):
        k = f"{key}_pericenters"
        if k in cache:
            continue
        o = kr[key]
        st = o["initial_state"]["bl"]
        orb = kerr.MinoOrbit.from_state("bl", 0.0, st["x"], st["u"], A, M, 30)
        lst = []
        with mp.workdps(30):
            for ev in o["events"]["pericenter_exact"]:
                s = orb.at_lambda(mp.mpf(ev["lam"]))
                lst.append(dict(t=float(s["t_bl"]), r=float(s["r"]), phi=float(s["phi_bl"]),
                                theta=float(s["theta"])))
            per = orb.periods()
            cache[f"{key}_periods"] = {kk: float(v) for kk, v in per.items()}
        cache[k] = lst
        changed = True
        print(f"exact pericentres of {key}: {len(lst)}", flush=True)
    # inclined orbit in Cartesian KS for the mesh runs: exact states at checkpoints
    k = "bl_inclined_cks_checkpoints"
    o = kr["bl_inclined"]
    t0 = o["initial_state"]["cks"]["t0"]
    have = {round(c["t_run"], 9) for c in cache.get(k, [])}
    todo = [t for t in need_mesh_times if round(t, 9) not in have]
    if todo:
        st = o["initial_state"]["bl"]
        orb = kerr.MinoOrbit.from_state("bl", 0.0, st["x"], st["u"], A, M, 30)
        lst = cache.get(k, [])
        lam = None
        for t in todo:
            s, lam = orb.states_at_time(t0 + t, "ks", ("ks", "cks"), guess=lam)
            lst.append(dict(t_run=t, t_ks=t0 + t, x_ks=[float(c) for c in s["ks"][1]],
                            u_ks=[float(c) for c in s["ks"][2]],
                            x_cks=[float(c) for c in s["cks"][1]],
                            u_cks=[float(c) for c in s["cks"][2]]))
        cache[k] = sorted(lst, key=lambda c: c["t_run"])
        changed = True
        print(f"exact CKS checkpoints of bl_inclined: {len(todo)} new", flush=True)
    if changed:
        save_json(EXTRA_JSON, cache)
    return cache


def nearest_index(t, tq):
    i = np.searchsorted(t, tq)
    i = np.clip(i, 1, len(t) - 1)
    return np.where(np.abs(t[i - 1] - tq) <= np.abs(t[i] - tq), i - 1, i)


HIST_NPZ = KERR_RESULTS / "kerr_histories.npz"


def save_hist(samp, group):
    """Merge sampled histories of one part into kerr_histories.npz (float32 except times).
    Keys: '<part>__t' sample times, '<part>__xref' reference (r, theta, phi) at the samples,
    '<part>--<run>__<q>' with q in dpos (position error at the samples), dE/dLz/dQ (max over
    the records between consecutive samples), x (position at the samples), dx/du (CPU-GPU)."""
    old = dict(np.load(HIST_NPZ)) if HIST_NPZ.exists() else {}
    old = {k: v for k, v in old.items() if not (k.startswith(group + "--") or
                                                k.startswith(group + "__") or
                                                k.startswith(group + "_"))}
    if group == "C":
        old = {k: v for k, v in old.items() if not k.startswith("D--")}
    for k, v in samp.items():
        v = np.asarray(v)
        old[k] = v if k.endswith("__t") else v.astype(np.float32)
    np.savez_compressed(HIST_NPZ, **old)


# ------------------------------------------------------------------------------------------
# part C (+ D)
# ------------------------------------------------------------------------------------------

def part_c(kr):
    o = kr["ks_passage"]
    fin = np.array(o["final_state"]["ks"]["x"])
    ref = np.load(KERR_DIR / "ref" / "ks_passage_ks.npz")
    t_ref, x_ref = ref["t"], ref["x"]
    peri_exact = o["events"]["pericenter_exact"][0]
    res = {}
    hist = {}
    t_s = np.arange(576) * 0.4                      # samples every 0.4 M (on all step grids)
    xref_s = x_ref[np.rint(t_s * 100).astype(int)]
    samp = dict(C__t=t_s, C__xref=xref_s)
    for rd in run_dirs("kerr_passage"):
        b = basic(rd)
        m = b["meta"]
        tr = read_traj(rd)
        inv = invariant_errors(m["system"], tr["x"], tr["u"], A, M)
        efin, dfin = final_position_error(m["system"], tr, fin, A)
        r = radius(m["system"], tr["x"], A)
        tp, rp = local_extrema(tr["t"], r, "min")
        k = int(np.argmin(rp)) if len(rp) else None
        b.update(n_records=len(tr["t"]), t_last=float(tr["t"][-1]),
                 max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
                 inv0=inv["ref"], final_pos_err=efin, final_pos_err_components=dfin,
                 r_peri=float(rp[k]) if k is not None else None,
                 t_peri=float(tp[k]) if k is not None else None,
                 r_min_sample=float(r.min()), r_final=float(r[-1]),
                 final_rthph=to_rthph(m["system"], tr["x"][-1], A).tolist())
        if b["r_peri"] is not None:
            b["r_peri_err"] = b["r_peri"] - o["turning_points"]["r_peri"]
            b["t_peri_err"] = b["t_peri"] - peri_exact["t_ks"]
        se = sampled_errors(m["system"], A, tr, inv, t_s, xref_s)
        b["max_pos_err_samples"] = float(np.nanmax(se["dpos"]))
        tag = "C--" + b["name"].split("/")[1]
        for q in ("dpos", "dE", "dLz", "dQ"):
            samp[f"{tag}__{q}"] = se[q]
        # position error history against the stored reference (dt = 0.01 grid only)
        if abs(m["dt"] - 0.01) < 1e-12 and f"{m['pusher']}_{m['metric']}" in (
                "mid_ks", "bsym_ks", "mid_lat", "bchol_lat"):
            idx = nearest_index(t_ref, tr["t"])
            q = to_rthph(m["system"], tr["x"], A)
            qe = x_ref[idx]
            q[:, 2] = unwrap_to(q[:, 2], qe[:, 2])
            dq = np.max(np.abs(q - qe), axis=1)
            b["max_pos_err_over_time"] = float(dq.max())
            b["max_time_mismatch_vs_ref_grid"] = float(np.max(np.abs(t_ref[idx] - tr["t"])))
            sl = slice(0, None, 4)
            key = f"{m['pusher']}_{m['metric']}"
            hist[key] = dict(t=tr["t"][sl], r=r[sl], x=tr["x"][sl], dE=inv["dE"][sl],
                             dLz=inv["dLz"][sl], dQ=inv["dQ"][sl], dpos=dq[sl])
        res[b["name"]] = b
        print(f"{b['name']:36s} dE {inv['max_dE']:.3e} dLz {inv['max_dLz']:.3e} "
              f"dQ {inv['max_dQ']:.3e} pos {efin:.3e} rp {b['r_peri']} unconv "
              f"{b.get('hist', {}).get('n_unconverged_steps')}", flush=True)
    # convergence fits (analytic spherical KS)
    conv = {}
    for metric in ("ks", "cks", "lat"):
        for pusher in ("mid", "bsym", "bchol"):
            rows = sorted((v["meta"]["dt"], v["final_pos_err"], v["max_dE"], v["max_dLz"],
                           v["max_dQ"]) for v in res.values()
                          if v["meta"]["metric"] == metric and v["meta"]["pusher"] == pusher)
            if len(rows) >= 2:
                dts, errs, dE, dLz, dQ = zip(*rows)
                p, c = fit_order(dts, errs)
                key = pusher if metric == "ks" else f"{pusher}_{metric}"
                conv[key] = dict(metric=metric, pusher=pusher, dt=list(dts), err=list(errs),
                                 order=p, prefactor=c, pairwise=pairwise_orders(dts, errs),
                                 dE=list(dE), dLz=list(dLz), dQ=list(dQ))
    # interpolation effect alone: lattice minus analytic Cartesian KS at the same dt
    for k, c in list(conv.items()):
        if c["metric"] != "lat":
            continue
        diffs = []
        for dt in c["dt"]:
            a = res.get(f"kerr_passage/{c['pusher']}_lat_dt{dt:g}")
            b = res.get(f"kerr_passage/{c['pusher']}_cks_dt{dt:g}")
            if a is None or b is None:
                diffs.append(None)
                continue
            qa, qb = np.array(a["final_rthph"]), np.array(b["final_rthph"])
            qa[2] = unwrap_to(qa[2], qb[2])
            diffs.append(float(np.max(np.abs(qa - qb))))
        c["lat_minus_cks_final"] = diffs
    # CPU vs GPU (part D)
    cpu = {}
    for rd in run_dirs("kerr_passage_cpu"):
        b = basic(rd)
        name = b["name"].replace("kerr_passage_cpu/", "kerr_passage/")
        g = RUNS / name
        tc, tg = read_traj(rd), read_traj(g)
        n = min(len(tc["t"]), len(tg["t"]))
        dx = np.abs(tc["x"][:n] - tg["x"][:n])
        du = np.abs(tc["u"][:n] - tg["u"][:n])
        m = b["meta"]
        dq = np.abs(position_error(m["system"], tc["x"][:n], to_rthph(m["system"], tg["x"][:n], A), A))
        b.update(n_records_cpu=len(tc["t"]), n_records_gpu=len(tg["t"]),
                 max_dt=float(np.max(np.abs(tc["t"][:n] - tg["t"][:n]))),
                 max_abs_dx=float(dx.max()), max_abs_du=float(du.max()),
                 max_abs_d_rthph=float(dq.max()),
                 final_abs_dx=float(dx[-1].max()), final_abs_du=float(du[-1].max()),
                 bitwise_identical=bool(np.array_equal(tc["x"][:n], tg["x"][:n])
                                        and np.array_equal(tc["u"][:n], tg["u"][:n])),
                 first_differing_record=int(np.argmax((dx.max(1) > 0) | (du.max(1) > 0)))
                 if (dx.max() > 0 or du.max() > 0) else None)
        tag = "D--" + b["name"].split("/")[1]
        idx = nearest_index(tc["t"][:n], np.arange(0.0, 230.0 + 1e-9, 0.1))
        samp[f"{tag}__x_cpu"] = tc["x"][idx]
        samp[f"{tag}__x_gpu"] = tg["x"][idx]
        samp[f"{tag}__dx"] = envelope(tc["t"][:n], dx.max(axis=1), t_s)
        samp[f"{tag}__du"] = envelope(tc["t"][:n], du.max(axis=1), t_s)
        inv = invariant_errors(m["system"], tc["x"], tc["u"], A, M)
        invg = invariant_errors(m["system"], tg["x"], tg["u"], A, M)
        samp[f"{tag}__dE_cpu"] = envelope(tc["t"], inv["dE"], t_s)
        samp[f"{tag}__dE_gpu"] = envelope(tg["t"], invg["dE"], t_s)
        b.update(max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
                 final_pos_err=final_position_error(m["system"], tc, fin, A)[0])
        cpu[b["name"]] = b
        print(f"CPU-GPU {b['name']}: max|dx| {b['max_abs_dx']:.3e} max|du| {b['max_abs_du']:.3e} "
              f"identical {b['bitwise_identical']}", flush=True)
    return res, conv, cpu, hist, samp


# ------------------------------------------------------------------------------------------
# part B
# ------------------------------------------------------------------------------------------

def part_b(kr, extra):
    res = {}
    traj = {}
    samp = {}
    refs = {}
    short = {"bl_equatorial_eccentric": "B_ecc", "bl_inclined": "B_inc"}
    for key, tag in short.items():
        ref = np.load(KERR_DIR / "ref" / f"{key}_bl.npz")
        t_s = np.arange(0.0, kr[key]["t_end"] + 1e-9, 10.0)
        refs[key] = (t_s, ref["x"][np.rint(t_s * 100).astype(int)])
        samp[f"{tag}__t"] = t_s
        samp[f"{tag}__xref"] = refs[key][1]
    for rd in run_dirs("kerr_bl"):
        b = basic(rd)
        m = b["meta"]
        key = m["orbit"]
        o = kr[key]
        tr = read_traj(rd)
        inv = invariant_errors("bl", tr["x"], tr["u"], A, M)
        se = sampled_errors("bl", A, tr, inv, *refs[key])
        b["max_pos_err_samples"] = float(np.nanmax(se["dpos"]))
        tag = "B--" + b["name"].split("/")[1]
        for q in ("dpos", "dE", "dLz", "dQ"):
            samp[f"{tag}__{q}"] = se[q]
        fin = o["final_state"]["bl"]
        efin, dfin = final_position_error("bl", tr, fin["x"], A)
        du = (tr["u"][-1] - np.array(fin["u"])).tolist()
        r = tr["x"][:, 0]
        tp, rp = local_extrema(tr["t"], r, "min")
        ta, ra = local_extrema(tr["t"], r, "max")
        # keep the initial pericentre (t = 0 is a pericentre for both orbits)
        tp = np.r_[0.0, tp]
        rp = np.r_[r[0], rp]
        php = np.interp(tp, tr["t"], tr["x"][:, 2])
        ex = extra[f"{key}_pericenters"]
        per = extra[f"{key}_periods"]
        n = min(len(tp), len(ex))
        t_ex = np.array([e["t"] for e in ex[:n]])
        ph_ex = np.array([e["phi"] for e in ex[:n]])
        adv_num = (php[n - 1] - php[0]) / (n - 1) - 2 * np.pi
        adv_ex = (ph_ex[-1] - ph_ex[0]) / (n - 1) - 2 * np.pi
        b.update(n_records=len(tr["t"]), t_last=float(tr["t"][-1]),
                 max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
                 dQ_relative=inv["dQ_relative"], inv0=inv["ref"],
                 final_pos_err=efin, final_pos_err_components=dfin, final_u_err=du,
                 r_min=float(r.min()), r_max=float(r.max()),
                 r_peri_refined=[float(rp.min()), float(rp.max())],
                 r_apo_refined=[float(ra.min()), float(ra.max())] if len(ra) else None,
                 n_pericenters=int(len(tp)), n_apocenters=int(len(ta)),
                 pericenter_time_err_max=float(np.max(np.abs(tp[:n] - t_ex))),
                 pericenter_phi_err_max=float(np.max(np.abs(php[:n] - ph_ex))),
                 periapsis_advance_mean=float(adv_num),
                 periapsis_advance_mean_exact=float(adv_ex),
                 periapsis_advance_mean_exact_periods=float(per["Omega_phi"] * per["T_r"] - 2 * np.pi),
                 n_radial_periods_used=int(n - 1))
        if key == "bl_inclined":
            def nodes(tt, xx):
                # ascending nodes: theta decreases through pi/2 (z goes from - to +)
                sg = xx[:, 1] - np.pi / 2
                i = np.where((sg[:-1] > 0) & (sg[1:] <= 0))[0]
                tn = tt[i] + sg[i] / (sg[i] - sg[i + 1]) * (tt[i + 1] - tt[i])
                return tn, np.interp(tn, tt, xx[:, 2])
            tn, phn = nodes(tr["t"], tr["x"])
            ref = np.load(KERR_DIR / "ref" / f"{key}_bl.npz")
            tnr, phnr = nodes(ref["t"], ref["x"])
            th = tr["x"][:, 1]
            b.update(theta_range=[float(th.min()), float(th.max())],
                     n_ascending_nodes=int(len(tn)),
                     nodal_advance_mean=float((phn[-1] - phn[0]) / (len(tn) - 1) - 2 * np.pi)
                     if len(tn) > 1 else None,
                     nodal_advance_mean_reference=float((phnr[-1] - phnr[0]) / (len(tnr) - 1)
                                                        - 2 * np.pi),
                     node_time_err_max=float(np.max(np.abs(tn - tnr))) if len(tn) == len(tnr)
                     else None,
                     nodal_advance_exact_periods=float(per["Omega_phi"] * per["T_th"] - 2 * np.pi))
        res[b["name"]] = b
        if m["pusher"] == "bsym" and abs(m["dt"] - 0.01) < 1e-12:
            step = max(1, int(round(0.2 / m["dt"])))
            traj[key] = dict(t=tr["t"][::step], x=tr["x"][::step])
        print(f"{b['name']:28s} dE {inv['max_dE']:.3e} dLz {inv['max_dLz']:.3e} dQ {inv['max_dQ']:.3e}"
              f" pos {efin:.3e} r [{r.min():.4f},{r.max():.4f}] adv {adv_num:.6f} (exact {adv_ex:.6f})"
              f" unconv {b.get('hist', {}).get('n_unconverged_steps')}", flush=True)
    return res, traj, samp


# ------------------------------------------------------------------------------------------
# part E
# ------------------------------------------------------------------------------------------

def part_e(kr):
    rds = run_dirs("kerr_mesh")
    if not rds:
        return {}, {}
    t_end = load_json(rds[0] / "run.json")["meta"]["t_end"]
    checks = list(np.arange(0.0, t_end + 1e-9, 50.0))
    extra = exact_extra(kr, checks)
    cp = extra["bl_inclined_cks_checkpoints"]
    tc = np.array([c["t_run"] for c in cp])
    xc_ks = np.array([c["x_ks"] for c in cp])
    uc_ks = np.array([c["u_ks"] for c in cp])
    t_s = np.arange(0.0, t_end + 1e-9, 2.0)
    xref_s = reference_samples_ks(A, tc, xc_ks, uc_ks, t_s)
    samp = dict(E__t=t_s, E__xref=xref_s)
    res = {}
    for rd in rds:
        b = basic(rd)
        m = b["meta"]
        tr = read_traj(rd)
        inv = invariant_errors("cks", tr["x"], tr["u"], A, M)
        se = sampled_errors("cks", A, tr, inv, t_s, xref_s)
        tag = "E--" + b["name"].split("/")[1]
        for q in ("dpos", "dE", "dLz", "dQ", "x"):
            samp[f"{tag}__{q}"] = se[q]
        b["max_pos_err_samples"] = float(np.nanmax(se["dpos"]))
        idx = nearest_index(tr["t"], tc)
        dq = np.abs(position_error("cks", tr["x"][idx], xc_ks, A)).max(axis=1)
        efin, dfin = final_position_error("cks", tr, xc_ks[-1], A)
        b.update(n_records=len(tr["t"]), t_last=float(tr["t"][-1]),
                 max_dE=inv["max_dE"], max_dLz=inv["max_dLz"], max_dQ=inv["max_dQ"],
                 final_pos_err=efin, final_pos_err_components=dfin,
                 max_pos_err_checkpoints=float(dq.max()),
                 r_range=[float(radius("cks", tr["x"], A).min()),
                          float(radius("cks", tr["x"], A).max())])
        if m["metric"] == "mesh" and (rd / "geo.trajmet.bin").exists():
            tm = read_trajmet(rd)
            ex = kerr.adm("cks", tr["x"], A, M, derivs=False)
            n = min(len(tm["t"]), len(tr["t"]))
            g6 = ex.gamma[:, [0, 0, 0, 1, 1, 2], [0, 1, 2, 1, 2, 2]]
            b["reconstruction_err"] = dict(
                alpha=float(np.max(np.abs(tm["alpha"][:n] - ex.alpha[:n]))),
                beta=float(np.max(np.abs(tm["beta"][:n] - ex.beta[:n]))),
                gamma=float(np.max(np.abs(tm["g"][:n] - g6[:n]))))
            samp[f"{tag}__dalpha"] = envelope(tr["t"][:n], tm["alpha"][:n] - ex.alpha[:n], t_s)
            samp[f"{tag}__dgamma"] = envelope(tr["t"][:n], np.max(np.abs(tm["g"][:n] - g6[:n]), axis=1),
                                              t_s)
        res[b["name"]] = b
        print(f"{b['name']:32s} dE {inv['max_dE']:.3e} dLz {inv['max_dLz']:.3e} dQ {inv['max_dQ']:.3e}"
              f" pos(final) {efin:.3e} pos(max ckpt) {dq.max():.3e}"
              f" unconv {b.get('hist', {}).get('n_unconverged_steps')}", flush=True)
    # mesh vs lattice agreement
    cmp = {}
    for name, b in res.items():
        if b["meta"]["metric"] != "mesh":
            continue
        lat = name.replace("_mesh_", "_lat_")
        if lat in res:
            a1 = read_traj(RUNS / name)
            a2 = read_traj(RUNS / lat)
            n = min(len(a1["t"]), len(a2["t"]))
            cmp[name] = dict(lattice_run=lat,
                             max_abs_dx=float(np.max(np.abs(a1["x"][:n] - a2["x"][:n]))),
                             max_abs_du=float(np.max(np.abs(a1["u"][:n] - a2["u"][:n]))),
                             bitwise_identical=bool(np.array_equal(a1["x"][:n], a2["x"][:n])))
    # dx convergence
    conv = {}
    for pusher in ("mid", "bsym"):
        for metric in ("mesh", "lat"):
            rows = sorted((v["meta"]["dx"], v["final_pos_err"], v["max_dE"], v["max_dQ"])
                          for v in res.values()
                          if v["meta"]["metric"] == metric and v["meta"]["pusher"] == pusher)
            if len(rows) >= 2:
                dxs, errs, dE, dQ = zip(*rows)
                conv[f"{pusher}_{metric}"] = dict(
                    dx=list(dxs), err=list(errs), order=fit_order(dxs, errs)[0],
                    pairwise=pairwise_orders(dxs, errs), dE=list(dE), order_dE=fit_order(dxs, dE)[0],
                    dQ=list(dQ), order_dQ=fit_order(dxs, dQ)[0])
    save_hist(samp, "E")
    return res, dict(mesh_vs_lattice=cmp, dx_convergence=conv)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parts", nargs="*", default=["B", "C", "D", "E"])
    args = ap.parse_args()
    T0 = time.time()
    kr = kerr_ref()["orbits"]
    out_path = KERR_RESULTS / "kerr_summary.json"
    out = load_json(out_path) if out_path.exists() else {}
    if "C" in args.parts or "D" in args.parts:
        res, conv, cpu, hist, samp = part_c(kr)
        save_hist(samp, "C")
        out["C"] = dict(runs=res, dt_convergence_ks=conv,
                        exact=dict(r_peri=kr["ks_passage"]["turning_points"]["r_peri"],
                                   t_peri=kr["ks_passage"]["events"]["pericenter_exact"][0]["t_ks"],
                                   final_state=kr["ks_passage"]["final_state"]["ks"],
                                   invariants=kr["ks_passage"]["invariants"]))
        out["D"] = dict(runs=cpu)
        if hist:
            np.savez_compressed(
                KERR_RESULTS / "ks_passage_histories.npz",
                **{f"{k}__{q}": (v[q].astype(np.float32) if q != "t" else v[q])
                   for k, v in hist.items() for q in v},
                keys=np.array(sorted(hist)),
                r_peri_exact=kr["ks_passage"]["turning_points"]["r_peri"],
                t_peri_exact=kr["ks_passage"]["events"]["pericenter_exact"][0]["t_ks"])
            lat = {f"lat_{v['meta']['pusher']}_dt{v['meta']['dt']:g}": v["final_pos_err"]
                   for v in res.values() if v["meta"]["metric"] == "lat"}
            save_json(KERR_RESULTS / "ks_passage_convergence.json",
                      dict(analytic_ks={k: c for k, c in conv.items() if c["metric"] == "ks"},
                           analytic_cks={c["pusher"]: c for c in conv.values() if c["metric"] == "cks"},
                           lattice={c["pusher"]: c for c in conv.values() if c["metric"] == "lat"},
                           lattice_final_pos_err=lat))
    if "B" in args.parts:
        extra = exact_extra(kr, [])
        res, traj, samp = part_b(kr, extra)
        save_hist(samp, "B")
        out["B"] = dict(runs=res, exact={k: dict(
            radial_range=[kr[k]["turning_points"]["r_peri"], kr[k]["turning_points"]["r_apo"]],
            theta_range=[kr[k]["turning_points"]["theta_min"], kr[k]["turning_points"]["theta_max"]],
            invariants=kr[k]["invariants"], periods=kr[k]["periods"], t_end=kr[k]["t_end"],
            final_state=kr[k]["final_state"]["bl"]) for k in ("bl_equatorial_eccentric", "bl_inclined")})
        if traj:
            np.savez_compressed(KERR_RESULTS / "bl_trajectories.npz",
                                **{f"{k}__{q}": v[q].astype(np.float32 if q == "x" else np.float64)
                                   for k, v in traj.items() for q in v},
                                a=A, M=M,
                                x0_ecc=np.array(kr["bl_equatorial_eccentric"]["initial_state"]["bl"]["x"]),
                                x0_inc=np.array(kr["bl_inclined"]["initial_state"]["bl"]["x"]))
    if "E" in args.parts:
        res, extra_e = part_e(kr)
        out["E"] = dict(runs=res, **extra_e)
    save_json(out_path, out)
    print(f"wrote {out_path} ({time.time() - T0:.0f} s)")


if __name__ == "__main__":
    main()
