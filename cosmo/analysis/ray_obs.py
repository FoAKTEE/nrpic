"""Redshift and luminosity distance along the light rays of a relativistic run
(cosmo/PLAN.md, C3; East, Wojtak & Pretorius, arXiv:1908.05683, Sec. II C).

A bundle is a central ray and four neighbours that leave one point at one time
(cosmo/ic/ray_ic.py). Along the central ray, for the observers that move with the matter
(four-velocity from the deposited energy and momentum densities, u_i / W = S_i / E):

    1 + z = (u_a k^a)_emission / (u_a k^a)_observer,
    -u_a k^a = W (omega - gamma^ij v_j k_i),   omega = sqrt(gamma^ij k_i k_j).

The neighbours give two connecting vectors per unit of opening angle, xi_a =
(x_+a - x_-a) / (2 eps), taken at equal coordinate time. Their parts orthogonal to the
direction of the ray span the cross section of the beam, whose area does not depend on
the observer; divided by the solid angle of the bundle in the frame of the emitter it
is the square of the area distance r_s from the source, and the luminosity distance is
D_L = (1 + z) r_s.

Reference of a homogeneous matter-dominated universe that emits at the proper time
tau_e of the emitter (Hubble rate H_e = H_0 / (1 + 3 H_0 tau_e / 2)):

    D_L = (2 / H_e) (1 + z)^2 (sqrt(1 + z) - 1).
"""
import os

import numpy as np

SYM = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def full_metric(g6):
    """(..., 6) components xx, xy, xz, yy, yz, zz to (..., 3, 3)."""
    g = np.empty(g6.shape[:-1] + (3, 3))
    for n, (a, b) in enumerate(SYM):
        g[..., a, b] = g6[..., n]
        g[..., b, a] = g6[..., n]
    return g


def read_tracks(rundir, base, tags):
    """Records of the tracked particles with the given tags: dict of arrays indexed
    [time, particle]: x, u (the momentum slots), alpha, g (3x3), tau, E, S."""
    tr = np.fromfile(os.path.join(rundir, base + ".traj.bin")).reshape(-1, 8)
    tm = np.fromfile(os.path.join(rundir, base + ".trajmet.bin")).reshape(-1, 17)
    n = min(len(tr), len(tm))
    tr, tm = tr[:n], tm[:n]
    tag = tr[:, 1].astype(np.int64)
    lut = -np.ones(int(tag.max()) + 1, dtype=np.int64)
    lut[np.asarray(tags)] = np.arange(len(tags))
    col = lut[tag]
    keep = col >= 0
    tr, tm, col = tr[keep], tm[keep], col[keep]
    times, row = np.unique(tr[:, 0], return_inverse=True)
    nt, nq = len(times), len(tags)

    def table(vals):
        out = np.full((nt, nq) + vals.shape[1:], np.nan)
        out[row, col] = vals
        return out
    return {"t": times, "x": table(tr[:, 2:5]), "u": table(tr[:, 5:8]),
            "alpha": table(tm[:, 2]), "g": full_metric(table(tm[:, 6:12])),
            "tau": table(tm[:, 12]), "E": table(tm[:, 13]), "S": table(tm[:, 14:17])}


def observer_frequency(g, k, E, S):
    """-u_a k^a for the observers moving with the matter, and omega of the normal
    observers. g (..., 3, 3), k (..., 3) covariant, E (...), S (..., 3) covariant."""
    gi = np.linalg.inv(g)
    ku = np.einsum("...ij,...j->...i", gi, k)
    omega = np.sqrt(np.einsum("...i,...i->...", ku, k))
    with np.errstate(invalid="ignore", divide="ignore"):
        v = np.where(E[..., None] > 0.0, S/E[..., None], 0.0)
    v2 = np.einsum("...ij,...i,...j->...", gi, v, v)
    W = 1.0/np.sqrt(1.0 - np.minimum(v2, 0.999999))
    return W*(omega - np.einsum("...i,...i->...", ku, v)), omega, ku


def frw_distance(z, tau_e, H0=1.0):
    He = H0/(1.0 + 1.5*H0*tau_e)
    return (2.0/He)*(1.0 + z)**2*(np.sqrt(1.0 + z) - 1.0)


def bundle_observables(t, x, kcov, g, E, S, c_emit, g_emit, E_emit, S_emit, eps, L,
                       i_emit):
    """Redshift and distances of one bundle. Arrays over [time, ray] with the rays in
    the order centre, +e1, -e1, +e2, -e2; c_emit (5, 3) coordinate directions and
    g_emit (3, 3), E_emit, S_emit (3) at the point and time of emission. Returns a dict
    over the records after the emission."""
    sl = slice(i_emit + 1, None)
    # emission: unit vectors in the frame of the normal observer, null momentum
    cn = np.sqrt(np.einsum("ij,ai,aj->a", g_emit, c_emit, c_emit))
    d = c_emit/cn[:, None]
    D1 = (d[1] - d[2])/(2.0*eps)
    D2 = (d[3] - d[4])/(2.0*eps)
    omega_solid = np.sqrt(np.linalg.det(g_emit))*abs(np.linalg.det(np.array([d[0], D1, D2])))
    k_e = g_emit @ d[0]
    f_e, _, _ = observer_frequency(g_emit, k_e, np.asarray(E_emit), np.asarray(S_emit))
    # along the central ray
    gc, kc = g[sl, 0], kcov[sl, 0]
    f_o, omega, ku = observer_frequency(gc, kc, E[sl, 0], S[sl, 0])
    z = f_e/f_o - 1.0
    s = ku/omega[:, None]

    def connect(ip, im):
        dx = x[sl, ip] - x[sl, im]
        dx -= L*np.round(dx/L)
        xi = dx/(2.0*eps)
        par = np.einsum("tij,ti,tj->t", gc, xi, s)
        return xi - par[:, None]*s
    x1, x2 = connect(1, 2), connect(3, 4)
    G11 = np.einsum("tij,ti,tj->t", gc, x1, x1)
    G22 = np.einsum("tij,ti,tj->t", gc, x2, x2)
    G12 = np.einsum("tij,ti,tj->t", gc, x1, x2)
    area = np.sqrt(np.maximum(G11*G22 - G12**2, 0.0))
    r_s = np.sqrt(area/omega_solid)
    return {"t": t[sl], "z": z, "r_s": r_s, "D_L": (1.0 + z)*r_s, "omega": omega,
            "solid_angle": omega_solid, "x": x[sl, 0]}


def emission_proper_times(rundir, base="east"):
    """(bundle, kind, t_emit, tau_emit) of every bundle of a relativistic run: the proper
    time of the emitter (probe 0 at the overdensity for kind 0, probe 1 for kind 1) at
    the emission, from the lapse history of the probe."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(os.path.dirname(here), "ic"))
    from nrp_io import read_history
    from scipy.integrate import cumulative_simpson
    meta = np.load(os.path.join(rundir, "rays.npz"))
    h = read_history(os.path.join(rundir, base + ".nrpic.hst"))
    ok = np.isfinite(h["alpha_probe"]) & np.isfinite(h["alpha_probe1"])
    n = len(ok) if ok.all() else int(np.argmin(ok))
    t = h["time"][:n]
    tau = [cumulative_simpson(h[k][:n], x=t, initial=0.0)
           for k in ("alpha_probe", "alpha_probe1")]
    out = []
    for b in np.unique(meta["bundle"]):
        i = np.flatnonzero(meta["bundle"] == b)[0]
        te, kind = float(meta["t_emit"][i]), int(meta["kind"][i])
        if te <= t[-1]:
            out.append((int(b), kind, te, float(np.interp(te, t, tau[kind]))))
    return out


def gr_bundles(rundir, base="east", L=4.0, H0=1.0):
    """All bundles of a relativistic run. The proper time of each emitter is taken from
    the probe histories (probe 0 at the overdensity for kind 0, probe 1 for kind 1)."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(os.path.dirname(here), "ic"))
    from nrp_io import read_history
    from scipy.integrate import cumulative_simpson
    meta = np.load(os.path.join(rundir, "rays.npz"))
    tk = read_tracks(rundir, base, meta["tag"])
    h = read_history(os.path.join(rundir, base + ".nrpic.hst"))
    names = [k for k in ("alpha_probe", "alpha_probe1") if k in h]
    tau_probe = [cumulative_simpson(h[k], x=h["time"], initial=0.0) for k in names]
    out = []
    for b in np.unique(meta["bundle"]):
        idx = np.flatnonzero(meta["bundle"] == b)
        idx = idx[np.argsort(meta["role"][idx])]
        te = float(meta["t_emit"][idx[0]])
        kind = int(meta["kind"][idx[0]])
        ie = int(np.argmin(np.abs(tk["t"] - te)))
        if abs(tk["t"][ie] - te) > 1e-9 or ie >= len(tk["t"]) - 2:
            continue
        res = bundle_observables(tk["t"], tk["x"][:, idx], tk["u"][:, idx],
                                 tk["g"][:, idx], tk["E"][:, idx], tk["S"][:, idx],
                                 tk["u"][ie, idx], tk["g"][ie, idx[0]],
                                 tk["E"][ie, idx[0]], tk["S"][ie, idx[0]],
                                 float(meta["eps"]), L, ie)
        tp = tau_probe[min(kind, len(tau_probe) - 1)]
        tau_e = float(np.interp(te, h["time"], tp))
        res.update({"bundle": int(b), "kind": kind, "t_emit": te, "tau_emit": tau_e,
                    "a_emit": (1.0 + 1.5*H0*tau_e)**(2.0/3.0),
                    "D_FRW": frw_distance(res["z"], tau_e, H0)})
        out.append(res)
    return out
