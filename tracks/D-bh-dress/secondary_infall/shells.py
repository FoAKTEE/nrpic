#!/usr/bin/env python3
"""Test 3 of secondary_infall: spherical dust shells around a point-mass seed in an
Einstein-de Sitter background, with shell crossing (a reference calculation, decision
0010; it fixes the parameters of AthenaK runs and predicts their profiles).

Set-up (the scoping run's): at t_i = 2/(3 eps) uniform dust of density 3 eps^2/(8 pi) in
the unperturbed Hubble flow v = eps r around a seed of mass M = 1 (G = c = 1). The dust
is cut into shells logarithmically in the dust mass mu they enclose (a core shell holds
the dust inside mu_core). Shell k feels G (M_bh + dust inside it + half its own mass) and,
with angular momentum j_k, the barrier j_k^2/r^3; all gravity is Plummer-softened with
length s. Kick-drift-kick with a global step eta * min(dynamical time, crossing time,
angular time). By Birkhoff's theorem the dust outside the last shell does not matter.

Modes:
  pass    radial shells pass through the centre (signed radius) - the Newtonian
          reference of a softened, collisionless run (AthenaK Newtonian mode);
  absorb  a shell with j < jcap that comes within r_abs of the centre is added to the
          seed (M_bh grows) - the Newtonian proxy for capture by the hole of a
          full-relativity run (L < 4M is captured, 1305.2619 SFWpaper.tex:120).

Usage: python3 shells.py --out <dir> --config <name>   (configs below)
"""
import argparse
import json
import math
import os
import time

import numpy as np

from common import kepler_radial

CONFIGS = {
    # name: eps, mode, soft, r_abs, mu range, n radial shells, a_end, sigma_t, n_j
    "absorb_e0.01": dict(eps=0.01, mode="absorb", soft=0.0, r_abs=2.0, mu_core=1e-3,
                         mu_max=8.0, n=3000, a_end=8.0, sigma=0.0, nj=1),
    "absorb_e0.03": dict(eps=0.03, mode="absorb", soft=0.0, r_abs=2.0, mu_core=1e-3,
                         mu_max=8.0, n=3000, a_end=8.0, sigma=0.0, nj=1),
    "pass_e0.01_s0.5": dict(eps=0.01, mode="pass", soft=0.5, r_abs=0.0, mu_core=1e-3,
                            mu_max=8.0, n=4000, a_end=8.0, sigma=0.0, nj=1),
    "pass_e0.03_s0.5": dict(eps=0.03, mode="pass", soft=0.5, r_abs=0.0, mu_core=1e-3,
                            mu_max=8.0, n=4000, a_end=8.0, sigma=0.0, nj=1),
    "pass_e0.1_s5_a100": dict(eps=0.1, mode="pass", soft=5.0, r_abs=0.0, mu_core=1e-3,
                              mu_max=80.0, n=5000, a_end=100.0, sigma=0.0, nj=1),
    "pass_e0.1_s0.5_a100": dict(eps=0.1, mode="pass", soft=0.5, r_abs=0.0, mu_core=1e-3,
                                mu_max=80.0, n=5000, a_end=100.0, sigma=0.0, nj=1),
    "absorbL_e0.01_sig0.02": dict(eps=0.01, mode="absorb", soft=0.0, r_abs=4.0,
                                  mu_core=1e-3, mu_max=5.0, n=1000, a_end=4.0,
                                  sigma=0.02, nj=8),
    "absorbL_e0.01_sig0.05": dict(eps=0.01, mode="absorb", soft=0.0, r_abs=4.0,
                                  mu_core=1e-3, mu_max=5.0, n=1000, a_end=4.0,
                                  sigma=0.05, nj=8),
    "absorbL_e0.01_sig0.1": dict(eps=0.01, mode="absorb", soft=0.0, r_abs=4.0,
                                 mu_core=1e-3, mu_max=5.0, n=1000, a_end=4.0,
                                 sigma=0.1, nj=8),
    "absorbL_e0.01_sig0.2": dict(eps=0.01, mode="absorb", soft=0.0, r_abs=4.0,
                                 mu_core=1e-3, mu_max=5.0, n=1000, a_end=4.0,
                                 sigma=0.2, nj=8),
}
JCAP = 4.0          # L_c = 4 G M for a marginally bound particle (1305.2619 SFWpaper.tex:120)
R_HARD = 2.0        # any particle inside r = 2M is taken into the hole


def setup(c):
    eps = c["eps"]
    edges = np.geomspace(c["mu_core"], c["mu_max"], c["n"] + 1)
    m_rad = np.concatenate([[c["mu_core"]], np.diff(edges)])
    mu_lagr = np.concatenate([[0.5 * c["mu_core"]], edges[:-1] + 0.5 * np.diff(edges)])
    r_i = (2.0 * mu_lagr / eps**2) ** (1.0 / 3.0)
    nj = c["nj"]
    if nj == 1:
        j = np.zeros_like(r_i)
        m = m_rad
        r0, mu0 = r_i, mu_lagr
        vt = np.zeros_like(r_i)
    else:
        q = (np.arange(nj) + 0.5) / nj
        vq = c["sigma"] * np.sqrt(-2.0 * np.log(1.0 - q))   # 2D Maxwellian speed quantiles
        r0 = np.repeat(r_i, nj)
        mu0 = np.repeat(mu_lagr, nj)
        m = np.repeat(m_rad / nj, nj)
        vt = np.tile(vq, r_i.size)
        j = r0 * vt
    v0 = eps * r0
    return dict(r=r0.copy(), v=v0.copy(), m=m.copy(), j=j, mu=mu0, r_i=r0.copy(),
                v_i=v0.copy(), vt=vt, t_i=2.0 / (3.0 * eps))


def accel(r, m, j2, hasj, mbh, s2):
    ar = np.abs(r)
    order = np.argsort(ar, kind="stable")
    ms = m[order]
    cum = np.cumsum(ms) - 0.5 * ms
    menc = np.empty_like(cum)
    menc[order] = cum
    mt = mbh + menc
    d2 = r * r + s2
    d = np.sqrt(d2)
    a = -mt * r / (d2 * d)
    if hasj.any():
        a[hasj] += j2[hasj] / r[hasj] ** 3
    return a, mt, d2, d


def run(c, snaps_a, eta=0.02, log_every=2000):
    st = setup(c)
    eps, s2 = c["eps"], c["soft"] ** 2
    t_i = st["t_i"]
    t_end = t_i * c["a_end"] ** 1.5
    r, v, m, j = st["r"], st["v"], st["m"], st["j"]
    n = r.size
    j2 = j * j
    hasj = j > 0
    alive = np.ones(n, bool)
    mbh = 1.0
    t = t_i
    t_snap = sorted(t_i * np.asarray(snaps_a) ** 1.5)
    snaps = []
    t_ta = np.full(n, np.nan)
    r_ta = np.full(n, np.nan)
    m_ta = np.full(n, np.nan)
    t_c = np.full(n, np.nan)          # first passage through the centre / pericentre
    t_abs = np.full(n, np.nan)
    ncross = np.zeros(n, int)
    a, mt, d2, d = accel(r, m, j2, hasj, mbh, s2)
    m_enc0 = mt.copy()
    series = []
    nstep = 0
    big = 1e30
    wall0 = time.time()
    while t < t_end * (1 - 1e-12):
        al = alive
        tdyn = np.sqrt(d2[al] * d[al] / mt[al])
        tcr = d[al] / (np.abs(v[al]) + 1e-30)
        dt = eta * min(tdyn.min(), tcr.min())
        hj = al & hasj
        if hj.any():
            dt = min(dt, eta * np.min(d2[hj] / j[hj]))
        nxt = t_end if not t_snap else min(t_end, t_snap[0])
        dt = min(dt, nxt - t)
        vr_old = np.where(hasj, v, np.sign(r) * v)
        r_old = r.copy()
        v += 0.5 * dt * a
        r += dt * v
        a, mt, d2, d = accel(r, m, j2, hasj, mbh, s2)
        v += 0.5 * dt * a
        t += dt
        nstep += 1
        vr_new = np.where(hasj, v, np.sign(r) * v)
        # first turnaround
        k = np.where(al & np.isnan(t_ta) & (vr_old > 0) & (vr_new <= 0))[0]
        if k.size:
            w = vr_old[k] / (vr_old[k] - vr_new[k])
            t_ta[k] = t - dt + w * dt
            r_ta[k] = np.maximum(np.abs(r_old[k]), np.abs(r[k]))
            m_ta[k] = mt[k]
        # passage through the centre (radial) or pericentre (angular momentum)
        rad = al & ~hasj & (np.sign(r) != np.sign(r_old)) & (r_old != 0)
        per = al & hasj & (vr_old < 0) & (vr_new >= 0)
        kk = np.where(rad | per)[0]
        if kk.size:
            ncross[kk] += 1
            first = kk[np.isnan(t_c[kk])]
            t_c[first] = t
        if c["mode"] == "absorb":
            # with angular momentum the capture rule scales with the current hole mass
            # (L_c = 4 M_bh, inside 4 M_bh; any particle inside 2 M_bh); the radial runs keep
            # the fixed r_abs of their closed-form check
            sc = mbh if c["nj"] > 1 else 1.0
            cap = alive & (((np.abs(r) < c["r_abs"] * sc) & (j < JCAP * sc))
                           | (np.abs(r) < R_HARD * sc))
            kc = np.where(cap)[0]
            if kc.size:
                # time of reaching r_abs by linear interpolation of the radius
                ro, rn = np.abs(r_old[kc]), np.abs(r[kc])
                w = np.clip((ro - c["r_abs"] * sc) / np.maximum(ro - rn, 1e-300), 0.0, 1.0)
                t_abs[kc] = t - dt + w * dt
                mbh += m[kc].sum()
                m[kc] = 0.0
                alive[kc] = False
                r[kc] = big
                v[kc] = 0.0
                a, mt, d2, d = accel(r, m, j2, hasj, mbh, s2)
        if t_snap and t >= t_snap[0] * (1 - 1e-12):
            snaps.append(dict(t=t, a=(t / t_i) ** (2.0 / 3.0), r=r.copy(), v=v.copy(),
                              m=m.copy(), alive=alive.copy(), ncross=ncross.copy(), mbh=mbh))
            t_snap.pop(0)
        if nstep % log_every == 0:
            series.append((t, mbh, float(m[alive & (ncross > 0)].sum()), nstep))
    series.append((t, mbh, float(m[alive & (ncross > 0)].sum()), nstep))
    return dict(cfg=c, st=st, snaps=snaps, t_ta=t_ta, r_ta=r_ta, m_ta=m_ta, t_c=t_c,
                t_abs=t_abs, m_enc0=m_enc0, series=np.array(series), nstep=nstep,
                wall=time.time() - wall0, t_end=t, mbh=mbh)


def closed_forms(res):
    st = res["st"]
    kf = kepler_radial(st["r_i"], st["v_i"], res["m_enc0"], st["t_i"])
    out = dict(t_ta=kf["t_ta"], r_max=kf["r_max"], t_c=kf["t_c"])
    c = res["cfg"]
    if c["mode"] == "absorb":
        # time to fall from the apocentre to r_abs on the same radial orbit
        r_abs = c["r_abs"]
        ts = np.sqrt(kf["r_max"] ** 3 / (8.0 * res["m_enc0"]))
        eta_i = np.arccos(np.clip(1.0 - 2.0 * st["r_i"] / kf["r_max"], -1, 1))
        ok = kf["r_max"] > r_abs
        eta_a = np.where(ok, 2.0 * np.pi - np.arccos(np.clip(1.0 - 2.0 * r_abs / kf["r_max"],
                                                              -1, 1)), np.nan)
        out["t_abs"] = st["t_i"] + ts * ((eta_a - np.sin(eta_a)) - (eta_i - np.sin(eta_i)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", required=True, choices=sorted(CONFIGS))
    ap.add_argument("--eta", type=float, default=0.02)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    c = dict(CONFIGS[a.config])
    snaps_a = np.unique(np.round(np.concatenate([
        np.geomspace(1.25, c["a_end"], 40), [1.5, 2.0, 3.0, 4.0, 6.0, 8.0]]), 6))
    snaps_a = snaps_a[snaps_a <= c["a_end"]]
    res = run(c, snaps_a, eta=a.eta)
    cf = closed_forms(res)
    st = res["st"]
    # checks: turnaround before any crossing (enclosed mass unchanged at turnaround)
    ok = ~np.isnan(res["t_ta"]) & (np.abs(res["m_ta"] / res["m_enc0"] - 1.0) < 1e-12) \
        & (st["r_i"] > 100.0 * max(c["soft"], 1e-30)) & (st["j"] == 0)
    d_tta = np.abs(res["t_ta"][ok] / cf["t_ta"][ok] - 1.0)
    summary = dict(config=a.config, cfg=c, eta=a.eta, nstep=res["nstep"], wall=res["wall"],
                   t_end=res["t_end"], mbh_end=res["mbh"],
                   n_turned=int(np.sum(~np.isnan(res["t_ta"]))),
                   n_checked_ta=int(ok.sum()),
                   max_rel_err_t_ta=float(d_tta.max()) if d_tta.size else None,
                   median_rel_err_t_ta=float(np.median(d_tta)) if d_tta.size else None)
    if c["mode"] == "absorb" and c["nj"] == 1:
        oka = ~np.isnan(res["t_abs"]) & ~np.isnan(cf["t_abs"])
        d_ab = np.abs(res["t_abs"][oka] / cf["t_abs"][oka] - 1.0)
        summary.update(n_absorbed=int(oka.sum()), max_rel_err_t_abs=float(d_ab.max()),
                       median_rel_err_t_abs=float(np.median(d_ab)))
    np.savez_compressed(
        os.path.join(a.out, f"shells_{a.config}.npz"),
        cfg=json.dumps(c), r_i=st["r_i"], v_i=st["v_i"], mu=st["mu"], m0=np.array(
            [s for s in setup(c)["m"]]), j=st["j"], t_i=st["t_i"], t_ta=res["t_ta"],
        r_ta=res["r_ta"], m_ta=res["m_ta"], t_c=res["t_c"], t_abs=res["t_abs"],
        m_enc0=res["m_enc0"], cf_t_ta=cf["t_ta"], cf_r_max=cf["r_max"], cf_t_c=cf["t_c"],
        cf_t_abs=cf.get("t_abs", np.full_like(cf["t_ta"], np.nan)), series=res["series"],
        snap_t=np.array([s["t"] for s in res["snaps"]]),
        snap_a=np.array([s["a"] for s in res["snaps"]]),
        snap_r=np.array([s["r"] for s in res["snaps"]]),
        snap_v=np.array([s["v"] for s in res["snaps"]]),
        snap_m=np.array([s["m"] for s in res["snaps"]]),
        snap_alive=np.array([s["alive"] for s in res["snaps"]]),
        snap_ncross=np.array([s["ncross"] for s in res["snaps"]]),
        snap_mbh=np.array([s["mbh"] for s in res["snaps"]]))
    with open(os.path.join(a.out, f"shells_{a.config}.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
