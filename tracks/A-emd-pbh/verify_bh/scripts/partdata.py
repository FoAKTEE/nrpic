"""Tracked particles of a run, arranged as (output time) x (tag) arrays, with their shell
labels from the table (my LTB) and their areal radius from the metric at the particle."""
import os

import numpy as np

import vbio as V
import vbpaths as P
from ltb import shells_from_table


def areal_radius(x, g):
    """x: (..., 3) positions; g: (..., 6) gamma_xx, xy, xz, yy, yz, zz at the particle.
    Spherical decomposition gamma = A n n + B (delta - n n): B = (tr gamma - n.gamma.n)/2,
    R = r sqrt(B); also A = n.gamma.n."""
    r = np.sqrt(np.sum(x * x, axis=-1))
    n = x / r[..., None]
    gxx, gxy, gxz, gyy, gyz, gzz = [g[..., k] for k in range(6)]
    tr = gxx + gyy + gzz
    ngn = (n[..., 0] ** 2 * gxx + n[..., 1] ** 2 * gyy + n[..., 2] ** 2 * gzz
           + 2 * (n[..., 0] * n[..., 1] * gxy + n[..., 0] * n[..., 2] * gxz + n[..., 1] * n[..., 2] * gyz))
    B = 0.5 * (tr - ngn)
    return r, r * np.sqrt(B), ngn, B


def load(run, T):
    d = P.RUN_DIR[run]
    tr = V.read_traj(os.path.join(d, "ball.traj.bin"), os.path.join(d, "ball.trajmet.bin"))
    blocks = V.traj_by_time(tr["traj"])
    times = np.array([b[0] for b in blocks])
    tags_all = np.unique(tr["traj"][:, 1]).astype(int)
    ntag = int(tags_all.max()) + 1
    nt = len(times)
    X = np.full((nt, ntag, 3), np.nan)
    G = np.full((nt, ntag, 6), np.nan)
    TAU = np.full((nt, ntag), np.nan)
    ALP = np.full((nt, ntag), np.nan)
    EE = np.full((nt, ntag), np.nan)
    BET = np.full((nt, ntag, 3), np.nan)
    for k, (t, idx) in enumerate(blocks):
        tg = tr["traj"][idx, 1].astype(int)
        X[k, tg] = tr["traj"][idx, 2:5]
        G[k, tg] = tr["met"][idx, 6:12]
        TAU[k, tg] = tr["met"][idx, 12]
        ALP[k, tg] = tr["met"][idx, 2]
        BET[k, tg] = tr["met"][idx, 3:6]
        EE[k, tg] = tr["met"][idx, 13]
    if times[0] != 0.0:
        raise ValueError(f"{run}: first trajectory record at t = {times[0]}")
    # labels from the particle file (tags are the file order of the first traj_ntrack particles)
    x0f, u0f, m0f, _ = V.read_nrp(P.NRP[P.RUN_LAT[run]])
    same = np.allclose(x0f[:ntag], X[0], rtol=0, atol=0)
    rbar_i = np.sqrt(np.sum(X[0] ** 2, axis=1))
    sh = shells_from_table(T, rbar_i)
    r, R, A, B = areal_radius(X, G)
    return dict(run=run, times=times, X=X, G=G, tau=TAU, alpha=ALP, beta=BET, E=EE, r=r, R=R, A=A, B=B,
                rbar_i=rbar_i, sh=sh, ntag=ntag, met_reclen=tr["met_reclen"], nrec=tr["nrec"],
                tags_match_file=bool(same), m_p=m0f[:ntag])


def r_exact_at_own_tau(pd):
    """Exact areal radius of each particle's shell at the particle's own proper time,
    shape (n_time, n_tag); NaN where the particle is gone."""
    tau = pd["tau"].T                                     # (n_tag, n_time)
    tt = np.where(np.isfinite(tau), tau, 0.0)
    Rex = pd["sh"].R(tt).T
    Rex[~np.isfinite(pd["tau"])] = np.nan
    return Rex
