"""V4: stationarity of the Kerr (a = 0.8) spike in AthenaK, recomputed by the verifier from
the snapshots of run D-bh-dress-20261115-172611-1e40191 (12 chunks of 4000 particles,
analytic Cartesian Kerr-Schild metric, snapshots every 100 M to 20000 M).

My own pieces (no code of the track imported):
- reader of <basename>.part.NNNNN.bin (vreaders.read_snapshot, from nrpic_io.cpp);
- Kerr-Schild geometry from athenak/src/particles/nrpic_metrics.hpp:22-85 (H, l_i; r from
  r^4 - b r^2 - a^2 z^2 = 0); E = alpha W - beta^i u_i, Lz = x u_y - y u_x,
  u_theta(BL) = (x u_x + y u_y) cot(theta) - r sin(theta) u_z (t and phi shifts of KS -> BL
  depend on r only), Q = u_theta^2 + cos^2(theta) [a^2 (1 - E^2) + Lz^2 / sin^2(theta)];
- counts in the radial ranges [0,4), [4,6), [6,10), [10,16), [16,40) of the KS = BL radius;
- reference counts from my own phase-space integral (v3_kerr.py) off the equator for the
  Hernquist DF cut at E < E_cut (0.99, the sampler's argument, ic_summary.json; checked
  against the particles' E at t = 0): number per dr dtheta dphi n = J^t Sigma^2 sin(theta),
  the same on every slice for a stationary current with J^r = 0, normalised to all particles.
"""
import argparse
import glob
import json
import math
import os

import numpy as np

import vreaders as V
import v3_kerr as K

RUN = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172611-1e40191"
A_SPIN = 0.8
RANGES = [(0, 4), (4, 6), (6, 10), (10, 16), (16, 40)]


# ------------------------------------------------------------------ invariants from KS state
def ks_invariants(x, u, a=A_SPIN, M=1.0):
    X, Y, Z = x[:, 0], x[:, 1], x[:, 2]
    b = X * X + Y * Y + Z * Z - a * a
    r2 = 0.5 * (b + np.sqrt(b * b + 4 * a * a * Z * Z))
    r = np.sqrt(r2)
    H = M * r2 * r / (r2 * r2 + a * a * Z * Z)
    s = r2 + a * a
    l = np.stack([(r * X + a * Y) / s, (r * Y - a * X) / s, Z / r], axis=1)
    f = 1 + 2 * H
    lu = np.einsum("ij,ij->i", l, u)
    uu = np.einsum("ij,ij->i", u, u)
    W = np.sqrt(1 + uu - 2 * H * lu ** 2 / f)          # gamma^{ij} = delta - 2H l l /(1+2H)
    alpha = 1 / np.sqrt(f)
    beta_u = 2 * H * lu / f                              # beta^i u_i
    E = alpha * W - beta_u
    Lz = X * u[:, 1] - Y * u[:, 0]
    cth = np.clip(Z / r, -1, 1)
    sth = np.sqrt(np.maximum(1 - cth ** 2, 1e-300))
    uth = (X * u[:, 0] + Y * u[:, 1]) * cth / sth - r * sth * u[:, 2]
    Q = uth ** 2 + cth ** 2 * (a * a * (1 - E * E) + Lz ** 2 / sth ** 2)
    return r, cth, E, Lz, Q


# ------------------------------------------------------------------ reference off the equator
class Ref(K.Spike):
    def __init__(self, ecut, **kw):
        super().__init__(A_SPIN, "hern", **kw)
        self.ecut = ecut

    def edges_th(self, r, E, s, c):
        a = self.a
        D = r * r + a * a - 2 * r
        beta = 1 - E * E
        A2 = a * a / D - 1 / (s * s)
        A1 = -4 * a * E * r / D
        A0 = (r ** 4 / D) * ((1 + a * a / r ** 2 + 2 * a * a / r ** 3) * E ** 2 - D / r ** 2) - a * a * beta * c * c
        disc = A1 ** 2 - 4 * A2 * A0
        sq = math.sqrt(max(disc, 0))
        l1 = (-A1 + sq) / (2 * A2)
        l2 = (-A1 - sq) / (2 * A2)
        return min(l1, l2), max(l1, l2), disc >= 0

    def Cth(self, E, Lz, s, c):
        return Lz ** 2 / (s * s) + self.a ** 2 * (1 - E ** 2) * c * c

    def valid_cmax(self, r, E, Lz, s, c):
        Cm = K.Cmax_eq(r, E, Lz, self.a)
        return K.valid_orbit(r, E, Cm - Lz ** 2, Lz, self.a) & (Cm >= self.Cth(E, Lz, s, c))

    def lz_iv(self, r, E, s, c, nscan=300):
        lo, hi, ok = self.edges_th(r, E, s, c)
        if not ok:
            return []
        Lg = np.linspace(lo, hi, nscan)
        v = self.valid_cmax(r, np.full(nscan, E), Lg, s, c)
        if not v.any():
            return []
        idx = np.where(v)[0]
        out = []
        for run in np.split(idx, np.where(np.diff(idx) > 1)[0] + 1):
            i0, i1 = run[0], run[-1]
            a_, b_ = Lg[i0], Lg[i1]
            if i0 > 0:
                x0, x1 = Lg[i0 - 1], Lg[i0]
                for _ in range(40):
                    xm = 0.5 * (x0 + x1)
                    if self.valid_cmax(r, np.array([E]), np.array([xm]), s, c)[0]:
                        x1 = xm
                    else:
                        x0 = xm
                a_ = x1
            if i1 < nscan - 1:
                x0, x1 = Lg[i1], Lg[i1 + 1]
                for _ in range(40):
                    xm = 0.5 * (x0 + x1)
                    if self.valid_cmax(r, np.array([E]), np.array([xm]), s, c)[0]:
                        x0 = xm
                    else:
                        x1 = xm
                b_ = x0
            out.append((a_, b_))
        return out

    def emin_th(self, r, s, c):
        if not self.lz_iv(r, self.ecut - 1e-12, s, c, nscan=200):
            return None
        lo, hi = 0.5, self.ecut - 1e-12
        for _ in range(45):
            m = 0.5 * (lo + hi)
            if self.lz_iv(r, m, s, c, nscan=150):
                hi = m
            else:
                lo = m
        return hi

    def n_over_sin(self, r, mu):
        """(J^t Sigma^2 sin theta)/sin theta = number per dr d(cos theta) dphi."""
        a = self.a
        c = mu
        s = math.sqrt(1 - mu * mu)
        D = r * r + a * a - 2 * r
        Emin = self.emin_th(r, s, c)
        if Emin is None:
            return 0.0, None
        xe, we = np.polynomial.legendre.leggauss(self.nE)
        u = 0.5 * (xe + 1)
        En = Emin + (self.ecut - Emin) * u ** 2
        wE = (self.ecut - Emin) * 2 * u * 0.5 * we
        xl, wl = np.polynomial.legendre.leggauss(self.nL)
        xp, wp = np.polynomial.legendre.leggauss(self.npsi)
        EE_, LL_, WW_ = [], [], []
        for E, w in zip(En, wE):
            for (l0, l1) in self.lz_iv(r, E, s, c):
                EE_.append(np.full(self.nL, E))
                LL_.append(0.5 * (l1 + l0) + 0.5 * (l1 - l0) * xl)
                WW_.append(w * 0.5 * (l1 - l0) * wl)
        if not EE_:
            return 0.0, Emin
        E = np.concatenate(EE_)
        Lz = np.concatenate(LL_)
        W = np.concatenate(WW_)
        Cm = K.Cmax_eq(r, E, Lz, a)
        Ct = self.Cth(E, Lz, s, c)
        v_lo = K.valid_orbit(r, E, Ct - Lz ** 2, Lz, a)
        c0, c1 = Ct.copy(), Cm.copy()
        for _ in range(50):
            cm = 0.5 * (c0 + c1)
            v = K.valid_orbit(r, E, cm - Lz ** 2, Lz, a)
            c1 = np.where(v, cm, c1)
            c0 = np.where(v, c0, cm)
        Clo = np.where(v_lo, Ct, c1)
        plo = np.arccos(np.clip(1 - 2 * (Clo - Ct) / np.maximum(Cm - Ct, 1e-300), -1, 1))
        psi = 0.5 * (np.pi + plo)[:, None] + 0.5 * (np.pi - plo)[:, None] * xp
        wpsi = 0.5 * (np.pi - plo)[:, None] * wp
        C = Ct[:, None] + (Cm - Ct)[:, None] * (1 - np.cos(psi)) / 2
        EE = np.broadcast_to(E[:, None], C.shape)
        LL = np.broadcast_to(Lz[:, None], C.shape)
        fv = self.f(EE.ravel(), C.ravel(), LL.ravel()).reshape(C.shape)
        # J_t sin = -(2/sqrt D) sum E f ; J_phi sin = (2/sqrt D) sum Lz f
        Jts = -(2 / math.sqrt(D)) * np.sum(W[:, None] * wpsi * EE * fv)
        Jps = (2 / math.sqrt(D)) * np.sum(W[:, None] * wpsi * LL * fv)
        Abig = (r * r + a * a) ** 2 - a * a * D * s * s
        return float((-Abig * Jts - 2 * a * r * Jps) / D), Emin


def ref_point(args):
    r, mu, ecut, nE = args
    os.environ["OMP_NUM_THREADS"] = "1"
    R = Ref(ecut, nE=nE, nL=nE, npsi=16)
    val, Emin = R.n_over_sin(r, mu)
    return r, mu, val


def reference_counts(ecut, procs, nE=40, quick=False):
    edges = [2.2, 4.0, 6.0, 10.0, 16.0, 40.0, 110.0]
    nr = [12, 6, 6, 6, 8, 8]
    nmu = 8
    if quick:
        nr = [3, 2, 2, 2, 2, 2]
        nmu = 3
    xm, wm = np.polynomial.legendre.leggauss(nmu)
    mu = 0.5 * (xm + 1)          # [0, 1]; symmetric about the equator
    wmu = 0.5 * wm
    pts, wts, rng_id = [], [], []
    for k in range(len(nr)):
        xr, wr = np.polynomial.legendre.leggauss(nr[k])
        rr = 0.5 * (edges[k] + edges[k + 1]) + 0.5 * (edges[k + 1] - edges[k]) * xr
        ww = 0.5 * (edges[k + 1] - edges[k]) * wr
        for ri, wri in zip(rr, ww):
            for mi, wmi in zip(mu, wmu):
                pts.append((float(ri), float(mi), ecut, nE))
                wts.append(wri * wmi)
                rng_id.append(k)
    import multiprocessing as mp
    with mp.get_context("fork").Pool(procs) as pool:
        vals = pool.map(ref_point, pts)
    v = np.array([x[2] for x in vals])
    wts = np.array(wts)
    rng_id = np.array(rng_id)
    per = np.array([np.sum(v[rng_id == k] * wts[rng_id == k]) for k in range(len(nr))])
    frac = per / per.sum()
    return dict(edges=edges, nodes_r=nr, nodes_mu=nmu, nE=nE, frac=frac.tolist(),
                points=[[x[0], x[1], x[2]] for x in vals], weights=wts.tolist(), range_id=rng_id.tolist())


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--ecut", type=float, default=0.99)
    args = ap.parse_args()
    out = args.out
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt

    chunks = sorted(glob.glob(RUN + "/kerr_*"), key=lambda p: int(p.rsplit("_", 1)[1]))
    times = None
    counts = []
    E0 = Lz0 = Q0 = None
    dE = []
    dLz = []
    dQ = []
    rmin_all = []
    rp_ok = []
    Eall0 = []
    nonfinite = 0
    for ch in chunks:
        snaps = sorted(glob.glob(ch + "/kerr.part.*.bin"))
        if args.quick:
            snaps = snaps[::20]
        ts, cs = [], []
        e0 = l0 = q0 = None
        mdE = mdL = mdQ = None
        rmin = None
        for sp in snaps:
            s = V.read_snapshot(sp)
            o = np.argsort(s["tag"])
            x, u = s["x"][o], s["u"][o]
            if not (np.all(np.isfinite(x)) and np.all(np.isfinite(u))):
                nonfinite += 1
            r, cth, E, Lz, Q = ks_invariants(x, u)
            ts.append(s["t"])
            cs.append([np.sum((r >= lo) & (r < hi)) for lo, hi in RANGES])
            if e0 is None:
                e0, l0, q0 = E.copy(), Lz.copy(), Q.copy()
                mdE = np.zeros_like(E)
                mdL = np.zeros_like(E)
                mdQ = np.zeros_like(E)
                rmin = r.copy()
                Eall0.append(E)
            mdE = np.maximum(mdE, np.abs(E / e0 - 1))
            mdL = np.maximum(mdL, np.abs(Lz - l0))
            mdQ = np.maximum(mdQ, np.abs(Q - q0) / np.maximum(q0, 1))
            rmin = np.minimum(rmin, r)
        dE.append(mdE)
        dLz.append(mdL)
        dQ.append(mdQ)
        rmin_all.append(rmin)
        counts.append(np.array(cs))
        times = np.array(ts) if times is None else times
        print(ch, len(snaps), "snapshots", flush=True)
    C = np.sum(counts, axis=0)            # (nsnap, nranges)
    dE = np.concatenate(dE)
    dLz = np.concatenate(dLz)
    dQ = np.concatenate(dQ)
    Eall0 = np.concatenate(Eall0)
    rmin_all = np.concatenate(rmin_all)
    N = len(Eall0)
    res = dict(N=int(N), nsnap=int(len(times)), t_end=float(times[-1]), nonfinite_snapshots=nonfinite,
               E0_max=float(Eall0.max()), E0_min=float(Eall0.min()), rmin_over_run=float(rmin_all.min()),
               invariants=dict(dE_over_E=[float(np.median(dE)), float(np.percentile(dE, 99)), float(dE.max())],
                               dLz=[float(np.median(dLz)), float(np.percentile(dLz, 99)), float(dLz.max())],
                               dQ_over_maxQ1=[float(np.median(dQ)), float(np.percentile(dQ, 99)), float(dQ.max())]))
    half = len(times) // 2
    early = C[1:half + 1].mean(0)
    late = C[half + 1:].mean(0)
    tavg = C[1:].mean(0)
    # uncertainty of a time average: block means of 1000 M (10 snapshots)
    nb = (len(times) - 1) // 10
    blocks = C[1:1 + nb * 10].reshape(nb, 10, -1).mean(1)
    sem_blocks = blocks.std(0, ddof=1) / math.sqrt(nb)
    res["ranges"] = {}
    print("reference counts ...", flush=True)
    ref = reference_counts(args.ecut, args.procs, quick=args.quick)
    res["reference"] = ref
    for k, (lo, hi) in enumerate(RANGES):
        exp = ref["frac"][k] * N
        res["ranges"]["%d-%d" % (lo, hi)] = dict(
            t0=int(C[0, k]), early_mean=float(early[k]), late_mean=float(late[k]),
            late_over_early=float(late[k] / early[k]),
            late_over_early_sigma=float(math.sqrt(blocks[:nb // 2, k].var(ddof=1) / (nb // 2)
                                                  + blocks[nb // 2:, k].var(ddof=1) / (nb - nb // 2)) / early[k]),
            time_avg=float(tavg[k]), time_avg_sem_blocks=float(sem_blocks[k]),
            poisson_sigma_single=float(math.sqrt(tavg[k])),
            expected_mine=float(exp), time_avg_over_expected=float(tavg[k] / exp),
            t0_over_expected=float(C[0, k] / exp))
    print(json.dumps({k: v for k, v in res.items() if k != "reference"}, indent=1), flush=True)
    with open(out + "/v4_results.json", "w") as f:
        json.dump(dict(res, times=times.tolist(), counts=C.tolist()), f, indent=1)

    # figures
    fig, axs = plt.subplots(len(RANGES), 1, figsize=(fs.COLUMN_WIDTH * 1.6, 7.5), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.07, top=0.98, hspace=0.08)
    for k, (lo, hi) in enumerate(RANGES):
        e = res["ranges"]["%d-%d" % (lo, hi)]["expected_mine"]
        axs[k].plot(times, C[:, k] / e, color=fs.PAL["red"], lw=0.8)
        axs[k].axhline(1, **fs.GUIDE)
        axs[k].axhline(tavg[k] / e, color=fs.PAL["blue"], lw=1.0)
        axs[k].set_ylabel("%d-%d M" % (lo, hi), fontsize=8)
    axs[-1].set_xlabel(r"$t/M$")
    axs[0].set_title("counts / my reference (blue: time average)", fontsize=9)
    fs.save(fig, out + "/v4_counts")
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.15, top=0.96)
    for arr, lab, c in ((dE, r"$|E/E_0-1|$", fs.PAL["red"]), (dLz, r"$|L_z-L_{z,0}|$", fs.PAL["blue"]),
                        (dQ, r"$|Q-Q_0|/\max(Q_0,1)$", fs.PAL["green"])):
        ax.hist(np.log10(np.maximum(arr, 1e-18)), bins=80, histtype="step", color=c, label=lab)
    ax.axvline(-5, **fs.GUIDE)
    ax.set_xlabel(r"$\log_{10}$ max over 20000 M per particle")
    ax.set_ylabel("particles")
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, out + "/v4_invariants")


if __name__ == "__main__":
    main()
