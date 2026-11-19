#!/usr/bin/env python3
"""Horizon mass growth against the integrated particle flux through the horizon (gate G2
of Track D: "with matter filled in, the mass growth agrees with the integrated particle
flux through the horizon").

Measured side: the apparent-horizon mass M_AH(t) of the finder (`horizon_summary_N.txt`),
dM(t) = M_AH(t) - M_AH(t0).
Flux side (from the accretion diagnostics of core/requests-adf, or the history of a
release run):
  F_rem(t)  = sum of m E over particles removed inside the horizon (reasons 2, 3) with
              t0 < t_removal <= t: a LOWER bound of what has crossed the horizon by t
              (a particle is removed only after it crossed); R_rem(t) the same with m;
  F_sph(t)  = net m E carried inward through the innermost flux sphere since t0
              (cumulative mE_in - mE_out of <base>.acc.hst): an UPPER bound when the
              sphere lies outside the horizon and the infall is monotone (what crosses
              the sphere has not necessarily reached the horizon yet).
So for monotone accretion F_rem(t) <= dM(t) <= F_sph(t), up to the error of dM.

Error budget of dM (one sigma, added in quadrature):
  floor(t)   the vacuum control: |dM_vac(t)| of a matched run without matter (same mesh,
             gauge, finder, t0), as an envelope max over [t0, t]; or a constant floor
             (D-pre-4: 2.0-2.5e-5 at M/16, 2.8e-5 at M/8 for windows from 100 M to 210 M);
  finder     the finder's mass tolerance (`mass_tol`, 1e-5 in the D-pre-4 settings).
The comparison reports, at every finder time after t0: dM, F_rem, F_sph, the residual
dM - F_rem, the bracket violation v(t) = max(F_rem - dM, dM - F_sph, 0) in units of the
budget, and at the end the closure (dM(t_end) - F_rem(t_end)) / F_rem(t_end).

Usage (any subset of the flux inputs):
  compare.py --horizon RUN/b.horizon_summary_0.txt [--removed RUN/b.removed.bin]
             [--acc RUN/b.acc.hst] [--hst RUN/b.nrpic.hst] [--control V/b.horizon_summary_0.txt]
             [--floor 2.5e-5] [--t0 100] [--sphere 1] [--out DIR] [--label NAME]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fluxio  # noqa: E402

HORIZON_REASONS = (2, 3)


def step_cumsum(t_events, w, t_eval):
    """Sum of w over events with t_event <= t_eval (right-continuous step)."""
    order = np.argsort(t_events, kind="stable")
    te, cw = t_events[order], np.cumsum(w[order])
    k = np.searchsorted(te, t_eval, side="right")
    return np.where(k > 0, cw[np.maximum(k - 1, 0)], 0.0)


def removal_flux(rem, t0, t_eval, reasons=HORIZON_REASONS):
    sel = np.isin(rem["reason"], reasons) & (rem["time"] > t0)
    t, m, E = rem["time"][sel], rem["m"][sel], rem["E"][sel]
    return (step_cumsum(t, m * E, t_eval), step_cumsum(t, m, t_eval), int(sel.sum()))


def sphere_flux(acc, k, t0, t_eval):
    """Net inward m E and m through sphere k (1-based) since t0, at t_eval (linear in
    time between records of acc.hst; records are every acc_dcycle cycles)."""
    t = acc["time"]
    net_mE = acc[f"mE_in{k}"] - acc[f"mE_out{k}"]
    net_m = acc[f"m_in{k}"] - acc[f"m_out{k}"]
    base_mE, base_m = np.interp(t0, t, net_mE), np.interp(t0, t, net_m)
    return (np.interp(t_eval, t, net_mE) - base_mE, np.interp(t_eval, t, net_m) - base_m,
            float(acc[f"radius{k}"][0]))


def control_envelope(ctrl, t0, t_eval):
    """max over [t0, t] of |M_vac(t') - M_vac(t0)| (finder times of the control)."""
    tc, mc = ctrl["time"], ctrl["mass"]
    m0 = np.interp(t0, tc, mc)
    after = tc >= t0
    d = np.abs(mc[after] - m0)
    env = np.maximum.accumulate(d) if d.size else d
    return np.interp(t_eval, tc[after], env, left=0.0) if d.size else np.zeros_like(t_eval)


def compare(hor, t0, rem=None, acc=None, hst=None, ctrl=None, floor=0.0, finder_tol=1e-5,
            sphere=1, k_sigma=3.0):
    t = hor["time"]
    keep = t >= t0
    t, M = t[keep], hor["mass"][keep]
    M0 = np.interp(t0, hor["time"], hor["mass"])
    dM = M - M0
    out = dict(t0=t0, M0=float(M0), t=t, dM=dM)
    if rem is not None:
        out["F_rem"], out["R_rem"], out["n_rem"] = removal_flux(rem, t0, t)
    elif hst is not None:
        # release runs: rest mass of the excised particles only (no energies)
        th = hst["time"]
        mex = hst["m_excised"]
        out["R_rem"] = np.interp(t, th, mex) - np.interp(t0, th, mex)
        out["F_rem"] = None
        out["n_rem"] = int(np.interp(t[-1], th, hst["n_excised"])
                           - np.interp(t0, th, hst["n_excised"]))
    if acc is not None:
        out["F_sph"], out["R_sph"], out["r_sph"] = sphere_flux(acc, sphere, t0, t)
    floor_t = np.full_like(t, float(floor))
    if ctrl is not None:
        out["ctrl_env"] = control_envelope(ctrl, t0, t)
        floor_t = np.maximum(floor_t, out["ctrl_env"])
    sigma = np.sqrt(floor_t ** 2 + finder_tol ** 2)
    out["sigma"] = sigma
    lo = out.get("F_rem")
    if lo is None:
        # release runs record only the rest mass of excised particles: use it as the
        # flux (exact for E = 1; for bound matter it overstates m E by the binding energy)
        lo = out.get("R_rem") if out.get("R_rem") is not None else np.zeros_like(t)
    hi = out.get("F_sph")
    viol_lo = np.maximum(lo - dM, 0.0) if lo is not None else np.zeros_like(t)
    viol_hi = np.maximum(dM - hi, 0.0) if hi is not None else np.zeros_like(t)
    viol = np.maximum(viol_lo, viol_hi) / sigma
    out["violation_sigma"] = viol
    summ = dict(t0=t0, t_end=float(t[-1]), M0=float(M0), dM_end=float(dM[-1]),
                sigma_end=float(sigma[-1]), n_finder=int(t.size),
                max_violation_sigma=float(viol.max()) if viol.size else 0.0,
                frac_inside_k_sigma=float(np.mean(viol <= k_sigma)) if viol.size else 1.0,
                k_sigma=k_sigma)
    if out.get("F_rem") is not None:
        F = out["F_rem"]
        summ.update(F_rem_end=float(F[-1]), R_rem_end=float(out["R_rem"][-1]),
                    n_removed=out["n_rem"],
                    resid_end=float(dM[-1] - F[-1]),
                    closure_end=float((dM[-1] - F[-1]) / F[-1]) if F[-1] != 0 else None)
    elif out.get("R_rem") is not None:
        summ.update(R_rem_end=float(out["R_rem"][-1]), n_removed=out["n_rem"])
    if hi is not None:
        summ.update(F_sph_end=float(hi[-1]), r_sphere=out["r_sph"])
    out["summary"] = summ
    return out


def plot(res, path, title, ref=None):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(figstyle.COLUMN_WIDTH * 1.6, 5.2),
                                 sharex=True, gridspec_kw=dict(height_ratios=[2, 1]))
    t = res["t"]
    a1.plot(t, res["dM"], color=figstyle.PAL["blue"], label=r"$\Delta M_{\rm AH}$ (finder)")
    if res.get("F_rem") is not None:
        a1.step(t, res["F_rem"], where="post", color=figstyle.PAL["red"],
                label=r"$\sum mE$ removed (lower)")
    if res.get("F_sph") is not None:
        a1.plot(t, res["F_sph"], color=figstyle.PAL["green"],
                label=rf"$\sum mE$ through $r={res['r_sph']:g}$ (upper)")
    if ref is not None:
        a1.plot(ref[0], ref[1], **figstyle.GUIDE, label=ref[2])
    a1.fill_between(t, res["dM"] - 3 * res["sigma"], res["dM"] + 3 * res["sigma"],
                    color=figstyle.PAL["blue"], alpha=0.2, lw=0)
    a1.set_ylabel(r"mass change $[M]$")
    a1.legend(fontsize=7, loc="upper left")
    a1.set_title(title, fontsize=9)
    base = res["F_rem"] if res.get("F_rem") is not None else np.zeros_like(t)
    a2.plot(t, res["dM"] - base, color=figstyle.PAL["blue"], label=r"$\Delta M_{\rm AH}-F_{\rm rem}$")
    a2.fill_between(t, -3 * res["sigma"], 3 * res["sigma"], color="grey", alpha=0.3, lw=0,
                    label=r"$\pm 3\sigma$ budget")
    if res.get("F_sph") is not None:
        a2.plot(t, res["F_sph"] - base, color=figstyle.PAL["green"], lw=1,
                label=r"$F_{\rm sph}-F_{\rm rem}$")
    a2.axhline(0, **figstyle.THIN)
    a2.set_xlabel(r"$t\ [M]$")
    a2.set_ylabel(r"residual $[M]$")
    a2.legend(fontsize=7)
    fig.tight_layout()
    figstyle.save(fig, path)
    plt.close(fig)


def jsonable(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, np.ndarray):
            out[k] = v.tolist()
        elif isinstance(v, (np.floating, np.integer)):
            out[k] = v.item()
        elif isinstance(v, dict):
            out[k] = jsonable(v)
        else:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--horizon", required=True)
    ap.add_argument("--removed")
    ap.add_argument("--acc")
    ap.add_argument("--hst")
    ap.add_argument("--control")
    ap.add_argument("--floor", type=float, default=0.0)
    ap.add_argument("--finder_tol", type=float, default=1e-5)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--sphere", type=int, default=1)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--label", default="compare")
    a = ap.parse_args()
    hor = fluxio.read_horizon(a.horizon)
    rem = fluxio.read_removed(a.removed) if a.removed else None
    acc = fluxio.read_hst(a.acc) if a.acc else None
    hst = fluxio.read_hst(a.hst) if a.hst else None
    ctrl = fluxio.read_horizon(a.control) if a.control else None
    res = compare(hor, a.t0, rem=rem, acc=acc, hst=hst, ctrl=ctrl, floor=a.floor,
                  finder_tol=a.finder_tol, sphere=a.sphere)
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, f"{a.label}.json"), "w") as f:
        json.dump(jsonable(res), f, indent=1)
    plot(res, os.path.join(a.out, a.label), a.label)
    print(json.dumps(res["summary"], indent=1))


if __name__ == "__main__":
    main()
