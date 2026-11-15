"""The static conformally flat test metric of the problem generator nrpic_geodesic
(<problem> metric_kind = static_conformal) as the particle module sees it, particle
files for it, and an independent Monte Carlo reference for what one collision does to
the energies of a pair whose members sit at different points of a collision cell.

Metric: alpha = alpha0 (1 + a_alpha cos phi), psi = psi0 (1 + a_psi cos phi),
gamma_ij = psi^4 delta_ij, beta^x = a_shift sin phi, phi = 2 pi (x - xmin)/L (mode
numbers 1, 0, 0). The code stores alpha, beta^x, gamma_xx = psi^4 at the cell centres
and reconstructs them at a particle with Catmull-Rom weights (nrpic::MeshMetric); the
class Metric does the same in one dimension (the weights of the other two directions
sum to one), so that "the metric at the particle" means here what it means in the code.

Reference (`pair_reference`): pairs of particles of one collision cell, positions
uniform in the cell, momenta from the local distribution; the collision of
`<particles> coll_energy = cell` (scattering in the frame of the cell centre, covariant
momenta exchanged unchanged) or of `coll_energy = particle` (python/nrpic/collide.py:
centre, scatter_rel, energy_root); pairs weighted with their Moller speed (constant
cross-section). No file of the code is read.
"""
import numpy as np

import common
from nrpic import collide
from nrpic.io import write_nrp


class Metric:
    """alpha, beta^x, psi^4 of the test metric on nx cells of [xmin, xmin + length)."""

    def __init__(self, nx=16, xmin=100.0, length=1.0, alpha0=1.0, psi0=1.0, a_alpha=0.0,
                 a_psi=0.0, a_shift=0.0):
        self.nx, self.xmin, self.length = nx, xmin, length
        self.dx = length/nx
        self.alpha0, self.psi0 = alpha0, psi0
        self.a_alpha, self.a_psi, self.a_shift = a_alpha, a_psi, a_shift
        xc = xmin + (np.arange(nx) + 0.5)*self.dx
        ph = 2.0*np.pi*(xc - xmin)/length
        self.alp = alpha0*(1.0 + a_alpha*np.cos(ph))
        self.psi4 = (psi0*(1.0 + a_psi*np.cos(ph)))**4
        self.bx = a_shift*np.sin(ph)

    def problem_block(self):
        """Command-line overrides that select this metric."""
        return ["problem/metric_kind=static_conformal", f"problem/alpha0={self.alpha0!r}",
                f"problem/psi0={self.psi0!r}", f"problem/alpha_amp={self.a_alpha!r}",
                f"problem/psi_amp={self.a_psi!r}", f"problem/shift_amp={self.a_shift!r}"]

    def _interp(self, v, x):
        """Catmull-Rom reconstruction of the cell-centred samples v at x (periodic)."""
        xi = (np.asarray(x, dtype=np.float64) - self.xmin)/self.dx - 0.5
        i0 = np.floor(xi).astype(np.int64)
        s = xi - i0
        s2, s3 = s*s, s*s*s
        w = [0.5*(-s + 2.0*s2 - s3), 0.5*(2.0 - 5.0*s2 + 3.0*s3),
             0.5*(s + 4.0*s2 - 3.0*s3), 0.5*(-s2 + s3)]
        out = 0.0
        for k in range(4):
            out = out + w[k]*v[(i0 + k - 1) % self.nx]
        return out

    def at(self, x):
        """(alpha, beta^x, psi^4) at the positions x, as the pusher reconstructs them."""
        return self._interp(self.alp, x), self._interp(self.bx, x), self._interp(self.psi4, x)

    def cell(self, ic, f=1):
        """(alpha, psi^4) of the collision cells with index ic (blocks of f mesh cells):
        the mean over the mesh cells of the block, as in the collision operator."""
        ic = np.asarray(ic, dtype=np.int64)
        alp = sum(self.alp[ic*f + k] for k in range(f))/f
        psi4 = sum(self.psi4[ic*f + k] for k in range(f))/f
        return alp, psi4


def theta_local(met, x, theta0, s_alpha=0.0, s_psi=0.0):
    """Local temperature theta0 (alpha/alpha0)^-s_alpha (psi/psi0)^-s_psi at x.
    s_alpha = 1, s_psi = 0: Tolman (theta alpha constant), an equilibrium of the static
    metric; s = 0: the same local temperature everywhere."""
    alp, _, psi4 = met.at(x)
    return theta0*(alp/met.alpha0)**(-s_alpha)*(psi4/met.psi0**4)**(-0.25*s_psi)


def tolman_density(met, x, theta_inf):
    """Coordinate density (not normalised) of the equilibrium f ~ exp(-alpha W/theta_inf)
    of the static metric without shift: psi^6 4 pi K2(z)/z with z = alpha/theta_inf."""
    from scipy import special
    alp, _, psi4 = met.at(x)
    z = alp/theta_inf
    return psi4**1.5*special.kve(2, z)*np.exp(-(z - z.min()))/z


def sample_umag(theta, uq, ngrid=257):
    """|u| of Maxwell-Juttner distributions at the temperatures theta[...] for the
    uniform deviates uq[...]: inverse distributions tabulated on a grid of temperatures
    and interpolated linearly in the temperature."""
    theta = np.asarray(theta, dtype=np.float64)
    lo, hi = float(theta.min()), float(theta.max())
    if hi - lo < 1e-14*hi:
        return collide.mj_sample(lo, uq)
    tgrid = np.linspace(lo, hi, ngrid)
    out = np.empty(theta.shape)
    ft = (theta - lo)/(tgrid[1] - tgrid[0])
    i0 = np.clip(np.floor(ft).astype(np.int64), 0, ngrid - 2)
    w1 = ft - i0
    for k in range(ngrid - 1):
        sel = i0 == k
        if not sel.any():
            continue
        a = collide.mj_sample(tgrid[k], uq[sel])
        b = collide.mj_sample(tgrid[k + 1], uq[sel])
        out[sel] = (1.0 - w1[sel])*a + w1[sel]*b
    return out


def make_particles(path, met, n, seed, theta0, s_alpha=0.0, s_psi=0.0, lengths=None,
                   weight="uniform", mass_ratio=1.0):
    """Particle file: positions uniform in the box (weight = "uniform") or with the
    coordinate density of the equilibrium f ~ exp(-alpha W/theta_inf) of the static
    metric without shift (weight = "tolman"): the integral of f over the covariant
    momenta, psi^6 4 pi K2(z)/z with z = alpha/theta_inf = 1/theta_local;
    momenta: Maxwell-Juttner at the local temperature in the orthonormal frame at the
    particle, u_i = psi^2 u_(i). Draws from the initial-data stream (entity = tag)."""
    from scipy import special
    lengths = [met.length, met.length, met.length] if lengths is None else list(lengths)
    uni = [common._uni(seed, 0, n, d) for d in range(4)]
    if weight == "uniform":
        x0 = met.xmin + lengths[0]*uni[0]
    else:
        xg = met.xmin + np.linspace(0.0, lengths[0], 40001)
        dens = tolman_density(met, xg, theta0/met.alpha0)
        cdf = np.concatenate(([0.0], np.cumsum(0.5*(dens[1:] + dens[:-1])*np.diff(xg))))
        cdf /= cdf[-1]
        x0 = np.interp(uni[0], cdf, xg)
    x = np.stack([x0, met.xmin + lengths[1]*uni[1], met.xmin + lengths[2]*uni[2]], axis=1)
    th = theta_local(met, x[:, 0], theta0, s_alpha, s_psi)
    umag = sample_umag(th, uni[3])
    nh = common._dirs(seed, 0, n, 4)
    _, _, psi4 = met.at(x[:, 0])
    u = (umag*np.sqrt(psi4))[:, None]*nh
    m = np.full(n, lengths[0]*lengths[1]*lengths[2]/n)
    if mass_ratio != 1.0:
        # every second particle heavier by mass_ratio, same total rest mass
        m1 = lengths[0]*lengths[1]*lengths[2]/((n - n//2) + mass_ratio*(n//2))
        m = np.where(np.arange(n) % 2 == 1, mass_ratio*m1, m1)
    write_nrp(path, x, u, m, np.zeros(n, dtype=np.int32))
    return dict(n=n, seed=seed, theta0=theta0, s_alpha=s_alpha, s_psi=s_psi,
                lengths=lengths, sha256=common.sha256(path))


def energies(met, x, u):
    """(W, H) with the metric at each particle: W = sqrt(1 + u^2/psi^4),
    H = alpha W - beta^x u_x."""
    alp, bx, psi4 = met.at(x)
    w = np.sqrt(1.0 + np.sum(u*u, axis=-1)/psi4)
    return w, alp*w - bx*u[..., 0]


def pair_reference(met, npair, seed, theta0, s_alpha=0.0, s_psi=0.0, f=1, mode="cell",
                   chunk=1000000, balance=True, density="uniform"):
    """Monte Carlo over pairs of one collision cell (see the module text). Returns a
    dict: mean change per collision of W_a + W_b and of H_a + H_b (metric at each
    particle), their standard errors, the slope c of the regression of the change of
    H of a particle on its cos(phi) minus the mean of cos(phi) over its cell (energy
    handed down the modulation per collision), and the share of pairs without a root
    (mode "particle")."""
    gen = np.random.default_rng(seed)
    ncell = met.nx//f
    h = met.dx*f
    if density == "tolman":
        # positions with the equilibrium density; a cell is chosen in proportion to its
        # number of tested pairs times the factor alpha/psi^6 of the pair probability
        xg = met.xmin + np.linspace(0.0, met.length, 16000*ncell + 1)
        dens = tolman_density(met, xg, theta0/met.alpha0)
        cdf = np.concatenate(([0.0], np.cumsum(0.5*(dens[1:] + dens[:-1])*np.diff(xg))))
        cdf /= cdf[-1]
        cedge = cdf[::16000]
        ac, p4c = met.cell(np.arange(ncell), f)
        pc = np.diff(cedge)**2*ac/p4c**1.5
        pc /= pc.sum()
    acc = dict(w=0.0, dw=0.0, dw2=0.0, dh=0.0, dh2=0.0, sxy=0.0, sxx=0.0, sxy2=0.0,
               noroot=0.0, w2=0.0, dlam=0.0, wdw2=0.0, wdh2=0.0, wxy2=0.0, rej=0.0,
               rmax=0.0, wall=0.0)
    done = 0
    while done < npair:
        nb = min(chunk, npair - done)
        done += nb
        if density == "tolman":
            ic = gen.choice(ncell, size=nb, p=pc)
            x0 = met.xmin + ic*h
            xa = np.interp(cedge[ic] + (cedge[ic + 1] - cedge[ic])*gen.random(nb), cdf, xg)
            xb = np.interp(cedge[ic] + (cedge[ic + 1] - cedge[ic])*gen.random(nb), cdf, xg)
        else:
            ic = gen.integers(0, ncell, nb)
            x0 = met.xmin + ic*h
            xa = x0 + h*gen.random(nb)
            xb = x0 + h*gen.random(nb)
        alc, psi4c = met.cell(ic, f)
        sc = np.sqrt(psi4c)                       # S of the cell: u_i = sc u_(i)
        st = {}
        for name, xx in (("a", xa), ("b", xb)):
            al, bx, p4 = met.at(xx)
            th = theta_local(met, xx, theta0, s_alpha, s_psi)
            um = sample_umag(th, gen.random(nb))
            ucov = (um*np.sqrt(p4))[:, None]*collide.isotropic(nb, gen)
            st[name] = dict(alp=al, bx=bx, psi4=p4, u=ucov, uh=ucov/sc[:, None],
                            c=np.cos(2.0*np.pi*(xx - met.xmin)/met.length))
        a, b = st["a"], st["b"]
        nh = collide.isotropic(nb, gen)
        # mean of cos(phi) over the cell (uniform positions)
        k = 2.0*np.pi/met.length
        cbar = (np.sin(k*(x0 + h - met.xmin)) - np.sin(k*(x0 - met.xmin)))/(k*h)
        if mode == "cell":
            g1, wa, wb = collide.gamma_rel_m1(a["uh"], b["uh"])
            wgt = collide.moller(g1, wa, wb)
            uan, ubn = collide.scatter(a["uh"], b["uh"], nh, g1, wa, wb)
            ok = np.ones(nb, dtype=bool)
            noroot = ~ok
            lam = np.ones(nb)
        else:
            def own(p):
                bvec = np.zeros((nb, 3))
                bvec[:, 0] = sc*p["bx"]                       # b_(m) = S beta
                gmat = np.zeros((nb, 3, 3))
                for d in range(3):
                    gmat[:, d, d] = psi4c/p["psi4"]           # S gamma^ij S
                return p["alp"], bvec, gmat
            oma, omb = own(a), own(b)
            dl = collide.centre(alc, oma, omb, a["uh"], b["uh"])
            uat, ubt = a["uh"] - dl, b["uh"] + dl
            g1, wa, wb = collide.gamma_rel_m1(uat, ubt)
            wgt = collide.moller(g1, wa, wb)
            wv = collide.scatter_rel(uat, ubt, nh, g1, wa, wb)
            pt = a["uh"] + b["uh"]
            h0 = collide.own_energy(*oma, a["uh"])[0] + collide.own_energy(*omb, b["uh"])[0]
            ha0, va0 = collide.own_energy(*oma, a["uh"])
            hb0, vb0 = collide.own_energy(*omb, b["uh"])
            ca = 0.5*pt + dl
            uan, ubn, lam, _, ok = collide.energy_root(oma, omb, pt, ca, wv, h0)
            noroot = ~ok
            if balance:
                # detailed balance: the collision takes place with probability min(1, R)
                g1n, wan, wbn = collide.gamma_rel_m1(uan - dl, ubn + dl)
                rbal = collide.balance(wgt, g1, wa + wb, lam, collide.energy_root.df,
                                       a["uh"] - ca, va0 - vb0,
                                       collide.moller(g1n, wan, wbn), g1n, wan + wbn, pt)
                rej = ok & ~(rbal >= 1.0) & ~(gen.random(nb) < rbal)
                acc["rej"] += np.sum(wgt*rej)
                acc["rmax"] = max(acc["rmax"], float(np.nanmax(np.abs(rbal[ok] - 1.0))))
                ok = ok & ~rej
        ua1 = np.where(ok[:, None], uan*sc[:, None], a["u"])
        ub1 = np.where(ok[:, None], ubn*sc[:, None], b["u"])
        wa0, ha0 = energies(met, xa, a["u"])
        wb0, hb0 = energies(met, xb, b["u"])
        wa1, ha1 = energies(met, xa, ua1)
        wb1, hb1 = energies(met, xb, ub1)
        dw = (wa1 - wa0) + (wb1 - wb0)
        dh = (ha1 - ha0) + (hb1 - hb0)
        # statistics per collision that takes place; proposals in proportion to wgt
        acc["wall"] += wgt.sum()
        acc["noroot"] += np.sum(wgt*noroot)
        wgt = wgt*ok
        acc["w"] += wgt.sum()
        acc["w2"] += np.sum(wgt*wgt)
        acc["dw"] += np.sum(wgt*dw)
        acc["dw2"] += np.sum((wgt*dw)**2)
        acc["dh"] += np.sum(wgt*dh)
        acc["dh2"] += np.sum((wgt*dh)**2)
        acc["wdw2"] += np.sum(wgt*dw*dw)
        acc["wdh2"] += np.sum(wgt*dh*dh)
        xy = (ha1 - ha0)*(a["c"] - cbar) + (hb1 - hb0)*(b["c"] - cbar)
        xx2 = (a["c"] - cbar)**2 + (b["c"] - cbar)**2
        acc["sxy"] += np.sum(wgt*xy)
        acc["sxy2"] += np.sum((wgt*xy)**2)
        acc["sxx"] += np.sum(wgt*xx2)
        acc["wxy2"] += np.sum(wgt*xy*xy)
        acc["dlam"] = max(acc["dlam"], float(np.max(np.abs(lam[ok] - 1.0))) if ok.any()
                          else 0.0)
    w = acc["w"]
    mdw, mdh = acc["dw"]/w, acc["dh"]/w
    # standard deviations over collisions (pairs drawn in proportion to their weight):
    # the standard error of a mean over n collisions of the code is sd/sqrt(n); for the
    # slope, sd_xy/(mean of the regressor square)/sqrt(n)
    return dict(mode=mode, f=f, npair=npair, theta0=theta0, s_alpha=s_alpha, s_psi=s_psi,
                dW=mdw, dW_se=float(np.sqrt(acc["dw2"])/w),
                dH=mdh, dH_se=float(np.sqrt(acc["dh2"])/w),
                dW_sd=float(np.sqrt(max(acc["wdw2"]/w - mdw*mdw, 0.0))),
                dH_sd=float(np.sqrt(max(acc["wdh2"]/w - mdh*mdh, 0.0))),
                slope=acc["sxy"]/acc["sxx"], slope_se=float(np.sqrt(acc["sxy2"])/acc["sxx"]),
                slope_sd=float(np.sqrt(max(acc["wxy2"]/w - (acc["sxy"]/w)**2, 0.0))
                               / (acc["sxx"]/w)),
                mean_vmol=acc["wall"]/npair, noroot=acc["noroot"]/acc["wall"],
                max_dlam=acc["dlam"], rejected=acc["rej"]/acc["wall"],
                max_abs_R_minus_1=acc["rmax"], balance=balance)
