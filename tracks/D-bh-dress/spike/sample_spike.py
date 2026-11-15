"""P2 initial data: test particles drawn from the final (adiabatically grown) distribution
function of the spike, for the AthenaK problem generator nrpic_geodesic with the analytic
Cartesian Kerr-Schild metric, a = 0.

Species 0 (stationary): f(E, L) = f~_H(eps'(E, L)) on bound, non-captured orbits with
E <= E_cut. Orbits are drawn from dN = 8 pi^2 L T_r(E, L) f dE dL (T_r the coordinate-time
radial period), the radial phase uniformly in time, the orbital plane isotropically and
the azimuth in the plane uniformly. This is exactly stationary in Schwarzschild.

Species 1 (loss-cone boundary probe): E uniform in [E1_lo, E_cut], L^2 = L_c^2(E)(1 + s q),
q log-uniform in [q_lo, q_hi], s = +1 (just outside the loss cone: bound orbit, phase
uniform in time) or s = -1 (inside: plunging orbit, started at its apocentre moving
inward). Fate and horizon-crossing time are predicted per particle from exact geodesics.

Masses are 1e-6 / N (the run deposits nothing; they are only labels). Species 0 is split
over --nfiles files spike_<k>.nrp (one process each), species 1 goes to spike_lc.nrp.

usage: python3 sample_spike.py --out DIR --n0 N --n1 N --nfiles K [--ecut 0.99] [--seed S]
Writes spike_<k>.nrp (k = 0..K-1, particles split evenly), ic_meta.npz, ic_summary.json.
"""
import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from spike_lib import SpikeModel, Lc2, Ls2, bh_roots, bh_action_period  # noqa
from nrpic import io as nio, kerr  # noqa

warnings.simplefilter("ignore", RuntimeWarning)
E_ISCO = np.sqrt(8.0 / 9.0)


def orbit_weight(sm, E, lam):
    """w(E, lam) = L T_r f~ (L_s - L_c): density of orbits in (E, lam), L = L_c + lam (L_s - L_c)."""
    lc = np.sqrt(Lc2(E)); ls = np.sqrt(Ls2(E))
    L = lc + lam * (ls - lc)
    L2 = L * L
    I, T, ok = bh_action_period(E, L2, "canonical")
    F = sm.ftilde_rel(E, L2, "canonical")
    w = np.where(ok, L * T * F * (ls - lc), np.nan)
    return w, L2


def draw_orbits(sm, n, ecut, rng, nE=240, nl=220, lam_min=1e-8):
    tE = np.linspace(0.0, 1.0, nE)
    Eg = E_ISCO + 1e-9 + (ecut - E_ISCO - 1e-9) * tE
    lg = np.unique(np.concatenate([np.logspace(np.log10(lam_min), -2, 80),
                                   np.linspace(0.01, 1.0 - 1e-7, nl - 80)]))
    EE, LL = np.meshgrid(Eg, lg, indexing="ij")
    W, _ = orbit_weight(sm, EE, LL)
    bad_nodes = int(np.sum(~np.isfinite(W)))
    W = np.where(np.isfinite(W), W, 0.0)
    env = 1.5 * np.maximum.reduce([W[:-1, :-1], W[1:, :-1], W[:-1, 1:], W[1:, 1:]])
    area = np.diff(Eg)[:, None] * np.diff(lg)[None, :]
    P = (env * area).ravel(); P /= P.sum()
    outE, outl, nviol, ntry = [], [], 0, 0
    while sum(len(a) for a in outE) < n:
        m = 4 * n
        c = rng.choice(P.size, size=m, p=P)
        i, j = np.unravel_index(c, env.shape)
        E = Eg[i] + rng.random(m) * (Eg[i + 1] - Eg[i])
        lam = lg[j] + rng.random(m) * (lg[j + 1] - lg[j])
        w, _ = orbit_weight(sm, E, lam)
        w = np.where(np.isfinite(w), w, 0.0)
        e = env[i, j]
        nviol += int(np.sum(w > e)); ntry += m
        acc = rng.random(m) * e < w
        outE.append(E[acc]); outl.append(lam[acc])
    E = np.concatenate(outE)[:n]; lam = np.concatenate(outl)[:n]
    lc = np.sqrt(Lc2(E)); ls = np.sqrt(Ls2(E))
    L = lc + lam * (ls - lc)
    return E, L, {"envelope_violations": nviol, "trials": ntry, "bad_grid_nodes": bad_nodes,
                  "lam_min_dropped": lam_min}


def draw_phase(E, L, rng):
    """Radius on the orbit with density dt/dr (uniform in coordinate time) and the sign
    of the radial motion."""
    ra, rp, r3, ok = bh_roots(E, L * L)
    assert np.all(ok)
    eta_g = np.linspace(0.0, np.pi, 257)

    def h(eta):
        r = rp + 0.5 * (ra - rp) * (1 - np.cos(eta))
        g = np.sqrt((1 - E * E) * (r - r3) / r**3)
        return 1.0 / ((1 - 2.0 / r) * g)

    hmax = np.max(np.stack([h(np.full_like(E, e)) for e in eta_g]), axis=0) * 1.3
    eta = np.full_like(E, np.nan)
    todo = np.ones(E.size, bool)
    nviol = 0
    while todo.any():
        k = np.where(todo)[0]
        et = rng.random(k.size) * np.pi
        hv = _h_sub(E[k], ra[k], rp[k], r3[k], et)
        nviol += int(np.sum(hv > hmax[k]))
        acc = rng.random(k.size) * hmax[k] < hv
        eta[k[acc]] = et[acc]
        todo[k[acc]] = False
    r = rp + 0.5 * (ra - rp) * (1 - np.cos(eta))
    sgn = np.where(rng.random(E.size) < 0.5, 1.0, -1.0)
    return r, sgn, ra, rp, r3, nviol


def _h_sub(E, ra, rp, r3, eta):
    r = rp + 0.5 * (ra - rp) * (1 - np.cos(eta))
    g = np.sqrt((1 - E * E) * (r - r3) / r**3)
    return 1.0 / ((1 - 2.0 / r) * g)


def to_cks(r, sgn, E, L, rng):
    """Cartesian Kerr-Schild (a = 0) position and covariant u_i of a particle at radius r
    with energy E, angular momentum L, radial direction sgn, random orbital plane."""
    n = r.size
    lhat = rng.normal(size=(n, 3)); lhat /= np.linalg.norm(lhat, axis=1)[:, None]
    tmp = np.where(np.abs(lhat[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    e1 = np.cross(lhat, tmp); e1 /= np.linalg.norm(e1, axis=1)[:, None]
    e2 = np.cross(lhat, e1)
    psi = rng.random(n) * 2 * np.pi
    nhat = np.cos(psi)[:, None] * e1 + np.sin(psi)[:, None] * e2
    x = r[:, None] * nhat
    V = np.clip(E * E - (1 - 2 / r) * (1 + L * L / r**2), 0.0, None)
    ur_s = sgn * np.sqrt(V) / (1 - 2 / r)               # covariant u_r, Schwarzschild
    ur_ks = ur_s + 2 * E / (r - 2)                      # t_KS = t_S + 2 ln(r/2 - 1)
    u = ur_ks[:, None] * nhat + (L / r)[:, None] * np.cross(lhat, nhat)
    return x, u


def plunge_time(E, L2, r0):
    """KS coordinate time from apocentre r0 (moving inward) to r = 2:
    int_2^r0 (E r / sqrt(V) - 2)/(r - 2) dr, with r = r0 - s^2 near the turning point."""
    def V(r):
        return E * E - (1 - 2 / r) * (1 + L2 / r**2)

    rm = 0.5 * (r0 + 2.0)
    smax = np.sqrt(r0 - rm)

    def f_out(s):
        r = r0 - s * s
        if s == 0.0:
            dV = -(2 / r0**2) * (1 + L2 / r0**2) + (1 - 2 / r0) * 2 * L2 / r0**3
            return 2 * E * r0 / np.sqrt(dV) / (r0 - 2)
        return 2 * s * (E * r / np.sqrt(max(V(r), 1e-300)) - 2) / (r - 2)

    def f_in(r):
        if r - 2.0 < 1e-12:
            r = 2.0 + 1e-12
        return (E * r / np.sqrt(V(r)) - 2) / (r - 2)

    a, _ = quad(f_out, 0.0, smax, limit=400, epsabs=1e-10, epsrel=1e-10)
    b, _ = quad(f_in, 2.0, rm, limit=400, epsabs=1e-10, epsrel=1e-10)
    return a + b


def apocentre_plunging(E, L2):
    """Largest root of V for a plunging orbit with E < 1 (bisection on [4, 2/(1-E^2)+10])."""
    lo = np.full_like(E, 2.0 + 1e-12); hi = 2.0 / (1 - E * E) + 10.0
    # V decreases through the apocentre: V(lo) > 0 is not guaranteed near the horizon for
    # L < L_c (no barrier), so bisect on the outermost sign change from above
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        v = E * E - (1 - 2 / mid) * (1 + L2 / mid**2)
        lo = np.where(v > 0, mid, lo)
        hi = np.where(v > 0, hi, mid)
    return 0.5 * (lo + hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n0", type=int, default=20000)
    ap.add_argument("--n1", type=int, default=2000)
    ap.add_argument("--nfiles", type=int, default=1)
    ap.add_argument("--ecut", type=float, default=0.99)
    ap.add_argument("--e1lo", type=float, default=0.95)
    ap.add_argument("--qlo", type=float, default=1e-4)
    ap.add_argument("--qhi", type=float, default=1e-1)
    ap.add_argument("--m", type=float, default=4e6)
    ap.add_argument("--seed", type=int, default=20261115)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    sm = SpikeModel(m_sun=args.m)
    summ = {"args": vars(args)}

    # species 0
    E0, L0, info = draw_orbits(sm, args.n0, args.ecut, rng)
    r0, s0, ra0, rp0, r30, nv = draw_phase(E0, L0, rng)
    info["phase_envelope_violations"] = nv
    summ["species0"] = info
    x0, u0 = to_cks(r0, s0, E0, L0, rng)

    # species 1
    n1 = args.n1
    E1 = args.e1lo + (args.ecut - args.e1lo) * rng.random(n1)
    s = np.where(np.arange(n1) % 2 == 0, 1.0, -1.0)
    # bound probes must stay below the stable circular orbit: q <= (L_s^2/L_c^2 - 1)/2
    qhi = np.where(s > 0, np.minimum(args.qhi, 0.5 * (Ls2(E1) / Lc2(E1) - 1)), args.qhi)
    q = 10 ** (np.log10(args.qlo) + rng.random(n1) * (np.log10(qhi) - np.log10(args.qlo)))
    L1sq = Lc2(E1) * (1 + s * q)
    L1 = np.sqrt(L1sq)
    out_side = s > 0
    r1 = np.zeros(n1); sg1 = np.zeros(n1); ra1 = np.zeros(n1); rp1 = np.full(n1, np.nan)
    rr, sg, ra_, rp_, _, _ = draw_phase(E1[out_side], L1[out_side], rng)
    r1[out_side], sg1[out_side], ra1[out_side], rp1[out_side] = rr, sg, ra_, rp_
    ra_in = apocentre_plunging(E1[~out_side], L1sq[~out_side])
    r1[~out_side] = ra_in * (1 - 1e-9); sg1[~out_side] = -1.0; ra1[~out_side] = ra_in
    tcross = np.full(n1, np.inf)
    tcross[~out_side] = [plunge_time(e, l2, r) for e, l2, r in
                         zip(E1[~out_side], L1sq[~out_side], r1[~out_side])]
    x1, u1 = to_cks(r1, sg1, E1, L1, rng)

    x = np.concatenate([x0, x1]); u = np.concatenate([u0, u1])
    sp = np.concatenate([np.zeros(args.n0, int), np.ones(n1, int)])
    E = np.concatenate([E0, E1]); L = np.concatenate([L0, L1])
    # check: invariants of the converted states
    Ec, Lzc, Qc = kerr.invariants("cks", x, u, a=0.0, M=1.0)
    Lc_ = np.linalg.norm(np.cross(x, u), axis=1)
    summ["conversion_check"] = {"max_rel_dE": float(np.max(np.abs(Ec / E - 1))),
                                "max_rel_dL": float(np.max(np.abs(Lc_ / L - 1)))}
    ntot = x.shape[0]
    mass = np.full(ntot, 1e-6 / ntot)
    files = []
    # species 0 split over nfiles (for parallel processes); species 1 in its own file
    groups = [(f"spike_{k}.nrp", idx) for k, idx in
              enumerate(np.array_split(rng.permutation(np.arange(args.n0)), args.nfiles))]
    if n1 > 0:
        groups.append(("spike_lc.nrp", np.arange(args.n0, ntot)))
    for name, idx in groups:
        idx = np.sort(idx)
        fn = out / name
        nio.write_nrp(fn, x[idx], u[idx], mass[idx], sp[idx])
        files.append({"file": fn.name, "n": int(idx.size), "index": idx.tolist()})
    fate = np.concatenate([np.zeros(args.n0, int), np.where(out_side, 0, 1)])
    np.savez(out / "ic_meta.npz", E=E, L=L, species=sp, fate_plunge=fate,
             tcross=np.concatenate([np.full(args.n0, np.inf), tcross]),
             ra=np.concatenate([ra0, ra1]), rp=np.concatenate([rp0, rp1]),
             q=np.concatenate([np.full(args.n0, np.nan), s * q]), r=np.linalg.norm(x, axis=1),
             x=x, u=u)
    summ["files"] = [{"file": f["file"], "n": f["n"]} for f in files]
    summ["file_index"] = {f["file"]: f["index"] for f in files}
    summ["species1"] = {"n_plunge": int(np.sum(~out_side)), "n_bound": int(np.sum(out_side)),
                        "tcross_min_max": [float(np.min(tcross[~out_side])),
                                           float(np.max(tcross[~out_side]))]}
    summ["species0_r_quantiles"] = np.quantile(r0, [0, 0.01, 0.1, 0.5, 0.9, 0.99, 1]).tolist()
    summ["species0_rp_min"] = float(rp0.min())
    summ["species0_ra_max"] = float(ra0.max())
    (out / "ic_summary.json").write_text(json.dumps(summ))
    print(json.dumps({k: v for k, v in summ.items() if k != "file_index"}, indent=1))


if __name__ == "__main__":
    main()
