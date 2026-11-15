"""Python twin of the Monte Carlo collision operator of the NRPIC module
(athenak/src/particles/nrpic_collide.{hpp,cpp}; tracks/core/interfaces/collisions.md)
and the Maxwell-Juttner reference functions its tests need.

Twin: the kernels of nrpic_collide.hpp on NumPy arrays (`gamma_rel_m1`, `moller`,
`sigma_m`, `scatter`), the triad of the cell (`triad`), and `replay`, which repeats one
collision step of the code from the state it dumped with `<particles> coll_dump_cycle`
(pairing words, order, sub-steps, probabilities, acceptances, directions, scattering),
with the random numbers of `nrpic.rng`. The draws are identical bits; the kinematics
agree to rounding (the compiler of the code may fuse a product and a sum).

Reference: one species of unit mass, theta = T/m, zeta = 1/theta, momenta per unit mass
u, W = sqrt(1 + u^2). Distribution f(u) d^3u = exp(-zeta W) d^3u / (4 pi K2(zeta)/zeta).
"""
import struct

import numpy as np
from scipy import integrate, optimize, special

from . import rng

__all__ = [
    "gamma_rel_m1", "moller", "sigma_m", "scatter", "triad", "replay", "read_dump",
    "own_energy", "centre", "scatter_rel", "energy_root", "own_metric_triad",
    "read_snapshot", "read_history", "mj_mean_w", "mj_theta_from_w", "mj_vmol",
    "mj_entropy", "mj_cdf", "mj_sample", "entropy_estimate", "isotropic",
    "relax_rate_nr",
]

SIGMA_CONSTANT, SIGMA_CUTOFF = 0, 1
TRIAD_SYMMETRIC, TRIAD_CHOLESKY = 0, 1


# ----------------------------------------------------------------------------------------
# kernels (nrpic_collide.hpp)

def gamma_rel_m1(ua, ub):
    """g1 = gamma_rel - 1 of pairs with momenta ua[..., 3], ub[..., 3]; returns
    (g1, W_a, W_b). Same branches as nrpic::CollGammaRelM1."""
    ua = np.atleast_2d(np.asarray(ua, dtype=np.float64))
    ub = np.atleast_2d(np.asarray(ub, dtype=np.float64))
    a2 = np.sum(ua*ua, axis=-1)
    b2 = np.sum(ub*ub, axis=-1)
    wa = np.sqrt(1.0 + a2)
    wb = np.sqrt(1.0 + b2)
    d = ua - ub
    s = ua + ub
    d2 = np.sum(d*d, axis=-1)
    smax = np.max(np.abs(s), axis=-1)
    zero = ~(smax > 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        e = s/np.where(zero, 1.0, smax)[..., None]
        e = e/np.sqrt(np.sum(e*e, axis=-1))[..., None]
        dpar = np.sum(d*e, axis=-1)
        c = np.cross(d, e)
        dperp2 = np.sum(c*c, axis=-1)
        wsum = wa + wb
        r = (dpar/wsum)**2
        g_small = (dperp2 + 4.0*r)/(2.0*(1.0 - r))
        a = np.sqrt(a2)
        b = np.sqrt(b2)
        sh = (a - b)*(a + b)/(a*wb + b*wa)
        g_large = sh*sh/(np.sqrt(1.0 + sh*sh) + 1.0)
        both = (a > 0.0) & (b > 0.0)
        h = ua/np.where(both, a, 1.0)[..., None] - ub/np.where(both, b, 1.0)[..., None]
        g_large = g_large + np.where(both, a*b*0.5*np.sum(h*h, axis=-1), 0.0)
    g1 = np.where(r <= 0.5, g_small, g_large)
    g1 = np.where(zero, 0.5*d2, g1)
    return g1, wa, wb


def moller(g1, wa, wb):
    """Moller speed sqrt(gamma_rel^2 - 1)/(W_a W_b)."""
    return np.sqrt(g1*(g1 + 2.0))/(wa*wb)


def sigma_m(model, sigma, w, g1):
    """Cross-section per unit mass (nrpic::CollSigma)."""
    if model == SIGMA_CUTOFF:
        v2 = g1*(g1 + 2.0)/((g1 + 1.0)*(g1 + 1.0))
        q = 1.0 + v2/(w*w)
        return sigma/(q*q)
    return sigma + 0.0*g1


def scatter(ua, ub, nhat, g1=None, wa=None, wb=None):
    """New momenta (u_a', u_b') of pairs of equal-mass particles for the directions nhat
    of particle a in the centre-of-momentum frame (nrpic::CollScatter)."""
    ua = np.atleast_2d(np.asarray(ua, dtype=np.float64))
    ub = np.atleast_2d(np.asarray(ub, dtype=np.float64))
    nhat = np.atleast_2d(np.asarray(nhat, dtype=np.float64))
    if g1 is None:
        g1, wa, wb = gamma_rel_m1(ua, ub)
    pt = ua + ub
    et = wa + wb
    rs = np.sqrt(4.0 + 2.0*g1)
    ps = np.sqrt(0.5*g1)
    ndp = np.sum(nhat*pt, axis=-1)
    cf = ps*ndp/(rs*(et + rs)) + 0.5
    uan = ps[..., None]*nhat + cf[..., None]*pt
    ubn = pt - uan
    return uan, ubn


# ----------------------------------------------------------------------------------------
# pair kinematics with the metric at each particle (<particles> coll_energy = particle;
# nrpic::CollEnergy, CollCentre, CollScatterRel, CollEnergyRoot)

def own_energy(alp, b, g, u):
    """Kinetic part of the canonical energy per unit rest mass, h = alpha (W - 1) - b.u,
    and v = dh/du = alpha g u/W - b, for triad momenta u[..., 3] and the metric at the
    particle in the triad of the cell: lapse alp[...], shift b[..., 3], inverse spatial
    metric g[..., 3, 3] (nrpic::CollEnergy). Returns (h, v)."""
    u = np.asarray(u, dtype=np.float64)
    y = np.einsum("...ij,...j->...i", g, u)
    x = np.sum(y*u, axis=-1)
    bu = np.sum(b*u, axis=-1)
    w = np.sqrt(1.0 + x)
    alp = np.asarray(alp, dtype=np.float64)
    v = alp[..., None]*y/w[..., None] - b
    return alp*x/(1.0 + w) - bu, v


def centre(alpc, ma, mb, ua, ub):
    """Momentum dl that b hands to a before the pair is treated in the cell frame
    (nrpic::CollCentre). ma, mb: tuples (alp, b, g) of the two particles."""
    q = 0.5*(ua + ub)
    _, va = own_energy(*ma, q)
    _, vb = own_energy(*mb, q)
    d = va - vb
    w0 = np.sqrt(1.0 + np.sum(q*q, axis=-1))
    qd = np.sum(q*d, axis=-1)
    c = -0.5*w0/alpc
    return np.asarray(c)[..., None]*(d + q*qd[..., None])


def scatter_rel(ua, ub, nhat, g1, wa, wb):
    """u_a' - P/2 of `scatter` without the cancellation (nrpic::CollScatterRel)."""
    pt = ua + ub
    et = wa + wb
    rs = np.sqrt(4.0 + 2.0*g1)
    ps = np.sqrt(0.5*g1)
    ndp = np.sum(nhat*pt, axis=-1)
    cf = ps*ndp/(rs*(et + rs))
    return ps[..., None]*nhat + cf[..., None]*pt


def energy_root(ma, mb, pt, ca, wv, e0):
    """New momenta u_a' = ca + lam wv, u_b' = pt - u_a' with the sum of the canonical
    energies equal to e0 (nrpic::CollEnergyRoot; the same iteration and stopping rules,
    for arrays of pairs). Returns (uan, ubn, lam, res, ok)."""
    pt = np.atleast_2d(np.asarray(pt, dtype=np.float64))
    ca = np.atleast_2d(np.asarray(ca, dtype=np.float64))
    wv = np.atleast_2d(np.asarray(wv, dtype=np.float64))
    e0 = np.atleast_1d(np.asarray(e0, dtype=np.float64))
    n = len(e0)
    ma = tuple(np.broadcast_to(np.asarray(v, dtype=np.float64), (n,) + np.shape(v)[-k:])
               if k else np.broadcast_to(np.asarray(v, dtype=np.float64), (n,))
               for v, k in zip(ma, (0, 1, 2)))
    mb = tuple(np.broadcast_to(np.asarray(v, dtype=np.float64), (n,) + np.shape(v)[-k:])
               if k else np.broadcast_to(np.asarray(v, dtype=np.float64), (n,))
               for v, k in zip(mb, (0, 1, 2)))
    cb = pt - ca
    ha, _ = own_energy(*ma, ca)
    hb, _ = own_energy(*mb, cb)
    res = ha + hb - e0
    ok = res < 0.0
    lam = np.where(ok, 1.0, 0.0)
    done = ~ok                       # finished (converged or failed)
    uan = np.array(ca)
    ubn = np.array(cb)
    scale = np.zeros(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        for _ in range(40):
            act = ~done
            if not act.any():
                break
            ua_i = ca + lam[:, None]*wv
            ub_i = pt - ua_i
            ea, va = own_energy(*ma, ua_i)
            eb, vb = own_energy(*mb, ub_i)
            r_i = ea + eb - e0
            sc_i = np.abs(ea) + np.abs(eb) + np.abs(e0)
            uan = np.where(act[:, None], ua_i, uan)
            ubn = np.where(act[:, None], ub_i, ubn)
            res = np.where(act, r_i, res)
            scale = np.where(act, sc_i, scale)
            conv = act & (np.abs(r_i) <= 3.6e-15*sc_i)
            done = done | conv
            act = act & ~conv
            df = np.sum(wv*(va - vb), axis=-1)
            bad = act & ~(df > 0.0)
            ok = ok & ~bad
            done = done | bad
            act = act & ~bad
            lam_new = lam - r_i/np.where(df > 0.0, df, 1.0)
            lam = np.where(act, lam_new, lam)
            bad = act & ~(lam > 0.0)
            ok = ok & ~bad
            done = done | bad
    late = ~done
    ok = ok & ~(late & ~(np.abs(res) <= 1.0e-12*scale))
    return uan, ubn, lam, res, ok


def own_metric_triad(s_mat, alp, beta, ginv):
    """(alp, b, g) of particles in the triad of a cell with coframe e^(m)_i = S[i, m]:
    b[m] = S[i, m] beta^i, g[m, n] = S[i, m] S[j, n] gamma^ij. beta[..., 3] and
    ginv[..., 6] (xx, xy, xz, yy, yz, zz) as dumped by the code."""
    beta = np.asarray(beta, dtype=np.float64)
    gv = np.asarray(ginv, dtype=np.float64)
    gm = np.empty(gv.shape[:-1] + (3, 3))
    gm[..., 0, 0] = gv[..., 0]; gm[..., 0, 1] = gv[..., 1]; gm[..., 0, 2] = gv[..., 2]
    gm[..., 1, 0] = gv[..., 1]; gm[..., 1, 1] = gv[..., 3]; gm[..., 1, 2] = gv[..., 4]
    gm[..., 2, 0] = gv[..., 2]; gm[..., 2, 1] = gv[..., 4]; gm[..., 2, 2] = gv[..., 5]
    b = beta @ s_mat
    g = np.einsum("im,...ij,jn->...mn", s_mat, gm, s_mat)
    return np.asarray(alp, dtype=np.float64), b, g


def triad(kind, g):
    """(S, Si) with S S^T = g for a symmetric positive-definite 3x3 matrix g:
    the symmetric square root (kind 0) or the lower Cholesky factor (kind 1), as
    nrpic::BuildTriad. Coframe e^(m)_j = S[j, m]; u_(m) = Si[m, j] u_j."""
    g = np.asarray(g, dtype=np.float64)
    if kind == TRIAD_CHOLESKY:
        s = np.linalg.cholesky(g)
    else:
        w, v = np.linalg.eigh(g)
        s = (v*np.sqrt(w)) @ v.T
    return s, np.linalg.inv(s)


# ----------------------------------------------------------------------------------------
# files written by the code

def read_dump(path):
    """Replay dump `<basename>.coll_dump.<cycle>.bin` (collisions.md, section 5)."""
    with open(path, "rb") as fp:
        magic = fp.read(8)
        if magic not in (b"NRPCOLD1", b"NRPCOLD2"):
            raise ValueError("not a collision dump: " + path)
        n, cycle, f = struct.unpack("<3q", fp.read(24))
        dt, sigma, w, pmax = struct.unpack("<4d", fp.read(32))
        model, weights, subcycle, nsub_max = struct.unpack("<4q", fp.read(32))
        seed, = struct.unpack("<Q", fp.read(8))
        tri, = struct.unpack("<q", fp.read(8))
        energy, has_own, nrec = 0, 0, 18
        if magic == b"NRPCOLD2":
            energy, has_own = struct.unpack("<2q", fp.read(16))
            nrec = 28
        r = np.fromfile(fp, dtype="<f8", count=nrec*n).reshape(n, nrec)
        q = np.fromfile(fp, dtype="<i4", count=7*n).reshape(n, 7)
    d = dict(n=n, cycle=cycle, f=f, dt=dt, sigma=sigma, w=w, pmax=pmax, model=model,
             weights=weights, subcycle=subcycle, nsub_max=nsub_max, seed=seed,
             triad=tri, x=r[:, 0:3], u0=r[:, 3:6], u1=r[:, 6:9], m=r[:, 9],
             alpha=r[:, 10], g=r[:, 11:17], vol=r[:, 17], tag=q[:, 0], level=q[:, 1],
             cell=q[:, 2:5], nsub=q[:, 5], nupd=q[:, 6], energy=energy,
             has_own=has_own)
    if nrec == 28:
        # metric at each particle: lapse, shift beta^i, inverse metric gamma^ij
        d.update(own_alpha=r[:, 18], own_beta=r[:, 19:22], own_ginv=r[:, 22:28])
    return d


def read_snapshot(path):
    """Particle snapshot `<basename>.part.NNNNN.bin` (NRPSNAP1)."""
    with open(path, "rb") as fp:
        if fp.read(8) != b"NRPSNAP1":
            raise ValueError("not a particle snapshot: " + path)
        t, = struct.unpack("<d", fp.read(8))
        n, ncycle = struct.unpack("<2q", fp.read(16))
        r = np.fromfile(fp, dtype="<f8", count=7*n).reshape(n, 7)
        tag = np.fromfile(fp, dtype="<i4", count=n)
        sp = np.fromfile(fp, dtype="<i4", count=n)
        tau = np.fromfile(fp, dtype="<f8", count=n)
    return dict(time=t, n=n, ncycle=ncycle, x=r[:, 0:3], u=r[:, 3:6], m=r[:, 6], tag=tag,
                species=sp, tau=tau)


HIST_COLUMNS = ["time", "ncycle", "n_part", "n_cells", "n_tested", "sum_P", "n_coll",
                "n_updated", "n_trunc", "max_P", "max_nsub", "mean_nsub", "min_N",
                "mean_N", "max_dx_mfp", "sum_MW", "sum_Mu1", "sum_Mu2", "sum_Mu3", "dE",
                "dP1", "dP2", "dP3", "abs_dE", "abs_dP", "n_bad_cells", "sum_W",
                "sum_MW_species0", "sum_M_species0", "sum_MW_particles", "dE_particles",
                # with <particles> coll_energy present:
                "sum_MH_particles", "dH_particles", "n_noroot", "max_dlam"]


def read_history(path):
    """`<basename>.coll.hst` as a dict of arrays; of repeated cycles (a run restarted
    from a dump older than its last record) the last occurrence is kept."""
    rows = {}
    ncol = None                 # files of earlier versions hold fewer columns
    with open(path) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            if len(v) < 26 or len(v) > len(HIST_COLUMNS):
                continue
            ncol = len(v) if ncol is None else ncol
            if len(v) != ncol:
                continue
            rows[int(v[1])] = [float(s) for s in v]
    ncol = len(HIST_COLUMNS) if ncol is None else ncol
    a = np.array([rows[k] for k in sorted(rows)], dtype=np.float64)
    if a.size == 0:
        a = np.zeros((0, ncol))
    return {name: a[:, i] for i, name in enumerate(HIST_COLUMNS[:ncol])}


# ----------------------------------------------------------------------------------------
# replay of one collision step

def _cell_groups(level, cell):
    """Indices of the particles of every collision cell (level >= 0)."""
    key = np.stack([level, cell[:, 0], cell[:, 1], cell[:, 2]], axis=1)
    ok = np.nonzero(level >= 0)[0]
    order = ok[np.lexsort(key[ok].T[::-1])]
    ks = key[order]
    cut = np.nonzero(np.any(ks[1:] != ks[:-1], axis=1))[0] + 1
    return np.split(order, cut)


def replay(d, cycle=None):
    """Repeats the collision step of a dump `d` (from `read_dump`) and returns
    (u_after[N,3], info). info: n_tested, sum_p, n_coll, n_upd, pairs (list of
    (tag_a, tag_b, sub-step, probability, accepted)), nsub per particle."""
    n = d["n"]
    step = d["cycle"] if cycle is None else cycle
    seed = d["seed"]
    st_pair = rng.stream(rng.STREAM_COLLISIONS, 0)
    st_acc = rng.stream(rng.STREAM_COLLISIONS, 1)
    st_dir = rng.stream(rng.STREAM_COLLISIONS, 2)
    u = np.array(d["u0"], dtype=np.float64)
    m = d["m"]
    tag = d["tag"].astype(np.int64)
    nsub_of = np.zeros(n, dtype=np.int64)
    nupd = np.zeros(n, dtype=np.int64)
    info = dict(n_tested=0, sum_p=0.0, n_coll=0, n_upd=0, pairs=[], max_p=0.0,
                n_noroot=0, max_dlam=0.0)
    pmode = d.get("energy", 0) == 1
    for idx in _cell_groups(d["level"], d["cell"]):
        nc = len(idx)
        p0 = idx[0]
        if not (d["alpha"][p0] > 0.0 and d["vol"][p0] > 0.0):
            continue                                   # cell skipped by the code
        if nc < 2 or not d["sigma"] > 0.0:
            continue
        gv = d["g"][p0]
        g = np.array([[gv[0], gv[1], gv[2]], [gv[1], gv[3], gv[4]], [gv[2], gv[4], gv[5]]])
        s_mat, si_mat = triad(d["triad"], g)
        fac = (nc - 1)*d["alpha"][p0]*d["dt"]/d["vol"][p0]
        mcell = np.max(m[idx])
        if pmode:
            # metric at the particles of this cell in its triad (index: particle)
            o_alp, o_b, o_g = {}, {}, {}
            ta, tb, tg = own_metric_triad(s_mat, d["own_alpha"][idx], d["own_beta"][idx],
                                          d["own_ginv"][idx])
            for k, pp in enumerate(idx):
                o_alp[pp], o_b[pp], o_g[pp] = ta[k], tb[k], tg[k]

        # sub-steps from the two largest speeds of the cell (or the bound 2)
        vbound = 2.0
        if d["subcycle"] != 1:
            uh = u[idx] @ si_mat.T
            u2 = np.sum(uh*uh, axis=1)
            vs = np.sort(np.sqrt(u2/(1.0 + u2)))
            vbound = min(vs[-1] + vs[-2], 2.0)
        rn = np.ceil(fac*d["sigma"]*mcell*vbound/d["pmax"])
        nsub = 1
        if not rn < d["nsub_max"]:
            nsub = int(d["nsub_max"])
        elif rn > 1.0:
            nsub = int(rn)
        s = 0
        while s < nsub:
            word = rng.bits(seed=seed, stream=st_pair, entity=tag[idx], step=step, draw=s)
            order = idx[np.lexsort((tag[idx], word))]
            q0 = 3 if nc % 2 == 1 else 0
            pa_list = list(order[q0::2][:(nc - q0)//2])
            pb_list = list(order[q0 + 1::2])
            wgt = [1.0]*len(pa_list)
            if q0 == 3:
                pa_list = [order[0], order[1], order[2]] + pa_list
                pb_list = [order[1], order[2], order[0]] + pb_list
                wgt = [0.5, 0.5, 0.5] + wgt
            for pa, pb, wg in zip(pa_list, pb_list, wgt):
                if tag[pa] > tag[pb]:
                    pa, pb = pb, pa
                ua = u[pa] @ si_mat.T
                ub = u[pb] @ si_mat.T
                if pmode:
                    oma = (o_alp[pa], o_b[pa], o_g[pa])
                    omb = (o_alp[pb], o_b[pb], o_g[pb])
                    dl = centre(d["alpha"][p0], oma, omb, ua, ub)
                    uat, ubt = ua - dl, ub + dl
                    g1, wa, wb = gamma_rel_m1(uat, ubt)
                else:
                    g1, wa, wb = gamma_rel_m1(ua, ub)
                mmx = max(m[pa], m[pb])
                prob = float((wg/nsub)*fac*sigma_m(d["model"], d["sigma"], d["w"], g1)[0]
                             * mmx*moller(g1, wa, wb)[0])
                uu = rng.uniform4(seed=seed, stream=st_acc, entity=tag[pa], step=step,
                                  draw=s, entity_hi=tag[pb])
                uu = np.asarray(uu).ravel()
                u_acc = float(uu[0])
                u_nan = float(uu[1])
                acc = u_acc < prob
                info["n_tested"] += 1
                info["sum_p"] += min(prob, 1.0)
                info["max_p"] = max(info["max_p"], prob)
                info["pairs"].append((int(tag[pa]), int(tag[pb]), s, prob, bool(acc)))
                if not acc:
                    continue
                nh = rng.direction(seed=seed, stream=st_dir, entity=tag[pa], step=step,
                                   draw=s, entity_hi=tag[pb])
                nh = np.asarray(nh).reshape(3)
                if pmode:
                    wv = scatter_rel(uat[None, :], ubt[None, :], nh[None, :], g1, wa, wb)
                    pt = ua + ub
                    ha0, _ = own_energy(*oma, ua)
                    hb0, _ = own_energy(*omb, ub)
                    uan, ubn, lam, _, okr = energy_root(oma, omb, pt, 0.5*pt + dl, wv,
                                                        ha0 + hb0)
                    if not okr[0]:
                        info["n_noroot"] += 1
                        continue
                    info["max_dlam"] = max(info["max_dlam"], abs(float(lam[0]) - 1.0))
                else:
                    uan, ubn = scatter(ua, ub, nh, g1, wa, wb)
                upa = upb = True
                if d["weights"] == 1 and m[pa] != m[pb]:
                    heavy = u_nan < min(m[pa], m[pb])/mmx
                    if m[pa] > m[pb]:
                        upa = heavy
                    else:
                        upb = heavy
                if upa:
                    u[pa] = uan[0] @ s_mat.T
                    nupd[pa] += 1
                if upb:
                    u[pb] = ubn[0] @ s_mat.T
                    nupd[pb] += 1
                info["n_coll"] += 1
                info["n_upd"] += int(upa) + int(upb)
            s += 1
        nsub_of[idx] = nsub
    info["nsub"] = nsub_of
    info["nupd"] = nupd
    return u, info


# ----------------------------------------------------------------------------------------
# Maxwell-Juttner reference

def mj_mean_w(theta):
    """<W> = K3(zeta)/K2(zeta) - theta (mean energy per unit rest mass)."""
    z = 1.0/np.asarray(theta, dtype=np.float64)
    return special.kve(3, z)/special.kve(2, z) - 1.0/z


def mj_theta_from_w(w):
    """Temperature of the Maxwell-Juttner gas with mean energy <W> = w."""
    w = float(w)
    lo, hi = 1e-8, 1e6
    return optimize.brentq(lambda t: mj_mean_w(t) - w, lo, hi, xtol=1e-15, rtol=1e-13)


def mj_vmol(theta):
    """Thermal average of the Moller speed of pairs of one Maxwell-Juttner gas,
    <v_Mol> = 4 K3(2 zeta)/(zeta K2(zeta)^2) (track C, SPEC.md section 2; checked here
    against a Monte Carlo average over sampled pairs, analysis/collisions/check_refs.py).
    """
    z = 1.0/np.asarray(theta, dtype=np.float64)
    # K3(2z) e^{2z} / (K2(z) e^{z})^2
    return 4.0*special.kve(3, 2.0*z)/(z*special.kve(2, z)**2)


def mj_entropy(theta):
    """s = -int f ln f d^3u for f normalised to one: zeta <W> + ln(4 pi K2(zeta)/zeta)."""
    z = 1.0/np.asarray(theta, dtype=np.float64)
    return z*mj_mean_w(theta) + np.log(4.0*np.pi*special.kve(2, z)/z) - z


def _mj_grid(theta, npts=40001):
    """Grid in u and the cumulative distribution of |u| on it."""
    z = 1.0/float(theta)
    # the density u^2 exp(-zeta (W - 1)) is negligible beyond W - 1 = 60 theta
    wmax = 1.0 + 60.0*float(theta)
    umax = np.sqrt(wmax*wmax - 1.0)
    u = np.linspace(0.0, umax, npts)
    pdf = u*u*np.exp(-z*(np.sqrt(1.0 + u*u) - 1.0))
    cdf = integrate.cumulative_simpson(pdf, x=u, initial=0.0)
    cdf /= cdf[-1]
    return u, np.maximum.accumulate(cdf)


def mj_cdf(theta):
    """Callable cumulative distribution of |u| of a Maxwell-Juttner gas."""
    u, cdf = _mj_grid(theta)
    return lambda x: np.interp(x, u, cdf, left=0.0, right=1.0)


def mj_sample(theta, uni):
    """|u| of the Maxwell-Juttner distribution for uniform deviates uni (inverse of the
    tabulated cumulative distribution)."""
    u, cdf = _mj_grid(theta)
    keep = np.concatenate(([True], np.diff(cdf) > 0.0))
    return np.interp(np.asarray(uni, dtype=np.float64), cdf[keep], u[keep])


def isotropic(n, gen):
    """n unit vectors, isotropic."""
    mu = 2.0*gen.random(n) - 1.0
    ph = 2.0*np.pi*gen.random(n)
    st = np.sqrt(1.0 - mu*mu)
    return np.stack([st*np.cos(ph), st*np.sin(ph), mu], axis=1)


def entropy_estimate(umag, theta_ref, nbins=64):
    """Entropy estimate of an isotropic sample of |u|: -sum_b p_b ln(p_b/vol_b) with the
    Miller-Madow term (B_occupied - 1)/(2 N), bins uniform in sqrt((W - 1)/theta_ref)
    up to 6 (the last bin open), vol_b the volume of the shell in u space. Returns
    (s, standard error) with the standard error from the multinomial variance of
    sum_b p_b ln(p_b/vol_b)."""
    umag = np.asarray(umag, dtype=np.float64)
    n = len(umag)
    w = np.sqrt(1.0 + umag*umag)
    q = np.sqrt((w - 1.0)/theta_ref)
    edges_q = np.linspace(0.0, 6.0, nbins + 1)
    edges_w = 1.0 + theta_ref*edges_q**2
    edges_u = np.sqrt(edges_w*edges_w - 1.0)
    umax = max(edges_u[-1], float(umag.max()))*(1.0 + 1e-12)
    edges_u = np.concatenate((edges_u[:-1], [umax]))
    cnt, _ = np.histogram(np.minimum(q, 6.0 - 1e-12), bins=edges_q)
    vol = 4.0*np.pi/3.0*(edges_u[1:]**3 - edges_u[:-1]**3)
    occ = cnt > 0
    p = cnt[occ]/n
    lnf = np.log(p/vol[occ])
    s = -np.sum(p*lnf) + (np.count_nonzero(occ) - 1)/(2.0*n)
    var = (np.sum(p*lnf*lnf) - np.sum(p*lnf)**2)/n
    return s, np.sqrt(max(var, 0.0))


def relax_rate_nr(theta1, theta2, rho_sigma):
    """Non-relativistic initial decay rate of theta_1 - theta_2 for two Maxwellian
    populations of equal density: nu_0 = (4/3) sqrt(2/pi) rho_0 sigma_m
    sqrt(theta_1 + theta_2) (track C, SPEC.md section 6)."""
    return 4.0/3.0*np.sqrt(2.0/np.pi)*rho_sigma*np.sqrt(theta1 + theta2)
