"""Newtonian particle-mesh reference for the cosmological runs (cosmo/PLAN.md, P2).

Matter-dominated background with a = (1 + H0 tau / 2)^2 in conformal time tau (a = 1 and
Hubble rate H0 at tau = 0), comoving positions x in a periodic box of side L, canonical
momenta p = a dx/dtau:

    dx/dtau = p / a,
    dp/dtau = -a grad psi_N,        lap psi_N = 4 pi a^2 rho_0(a) delta_N = (3/2) H0^2 delta_N / a,

so dp/dtau = -(3/2) H0^2 grad lap^-1 delta_N has no explicit time dependence. Kick-drift-
kick leapfrog with the drift integral of 1/a taken exactly. The mass is deposited with
the cloud shape of the relativistic run on its mesh and passed through the same
binomial filter, the Poisson equation is solved with Fourier transforms, and the force
is interpolated to the particles with cubic splines.

Observer quantities follow the dictionary of Chisari & Zaldarriaga and Green & Wald as
used by East, Wojtak & Abel (arXiv:1711.06681): at a point comoving with the matter,

    rho / rho_0 = a^-3 [1 + delta_N - 2 psi_N - 2 d psi_N / d ln a],
    d t_p / d tau = a sqrt(1 + 2 psi_N - (1 - 2 psi_N) v^2),       v = dx/dtau.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ic"))
import cosmo_id as cid  # noqa: E402


def scale_factor(tau, H0=1.0):
    return (1.0 + 0.5*H0*tau)**2


def drift_integral(tau1, tau2, H0=1.0):
    """Integral of d tau / a from tau1 to tau2."""
    return (2.0/H0)*(1.0/(1.0 + 0.5*H0*tau1) - 1.0/(1.0 + 0.5*H0*tau2))


class PM:
    def __init__(self, x, p, m, n, L, H0=1.0, nfilter=0, compensate=False, shape="cic"):
        self.x = np.array(x, dtype=float)
        self.p = np.array(p, dtype=float)
        self.m = np.array(m, dtype=float)
        self.n, self.L, self.H0 = n, L, H0
        self.nfilter, self.compensate, self.shape = nfilter, compensate, shape
        self.tor = cid.Torus(n, L)
        self.mean = self.m.sum()/L**3
        self.tau = 0.0
        self.delta = None
        self.phi = None       # lap^-1 delta_N; psi_N = (3/2) H0^2 phi / a
        self.g = None         # grad phi at the particles
        self.fields()

    def fields(self):
        """Density contrast, potential and force at the particles for the current x."""
        tor = self.tor
        rho = cid.cic_deposit(self.x, self.m, self.n, self.L, self.shape)
        if cid.DEP_COMP_C > 0.0:
            # compensation of the cloud as in the relativistic code (deposit_comp_c, _c2)
            rho = cid.compensate_density([rho], cid.DEP_COMP_C, 0.0, cid.DEP_COMP_C2)[0]
        rho = cid.binomial(rho, self.nfilter, self.compensate)
        self.delta = rho/self.mean - 1.0
        k2 = tor.k2.copy()
        k2[0, 0, 0] = 1.0
        Fk = -tor.fft(self.delta)/k2
        Fk[0, 0, 0] = 0.0
        self.phi = tor.ifft(Fk)
        self.g = np.stack([cid.interp(tor.ifft(1j*kd*Fk), self.x, self.L)
                           for kd in tor.kd], axis=1)

    def psi(self):
        """Newtonian potential on the mesh at the current time."""
        return 1.5*self.H0**2*self.phi/scale_factor(self.tau, self.H0)

    def step(self, dtau):
        c = 1.5*self.H0**2
        self.p -= 0.5*dtau*c*self.g
        self.x = np.mod(self.x + self.p*drift_integral(self.tau, self.tau + dtau, self.H0),
                        self.L)
        self.tau += dtau
        self.fields()
        self.p -= 0.5*dtau*c*self.g

    def velocity(self):
        """dx/dtau of the particles at the current time."""
        return self.p/scale_factor(self.tau, self.H0)


def corner_average(f, point, L):
    """Value of the cell-centred field f at a point, with the cloud-in-cell weights (at
    a cell corner: the mean of the eight cells around it), as the probe of the code."""
    n = f.shape[0]
    return float(cid.interp(f, np.atleast_2d(np.asarray(point, dtype=float)), L,
                            order=1)[0])


def cosmic_time(tau, H0=1.0):
    """Proper time of the homogeneous solution since tau = 0."""
    return (2.0/(3.0*H0))*((1.0 + 0.5*H0*tau)**3 - 1.0)


def run(pm, dtau, tau_end, probes=(), track=None, every=1, verbose=False, hook=None):
    """Advance to tau_end. Returns a dict of histories: tau, a, and for each probe point
    delta_N, psi_N, d psi_N / d ln a, the proper time t_p of the comoving observer there
    and the observer density contrast; for the tracked particle indices their positions,
    velocities, potential and proper time. Proper times are the exact cosmic time of the
    background plus the integral of the perturbation of the rate, advanced every step.
    hook, if given, is called after every step as hook(pm, tau0, psi0, tp0, r0, psi1,
    tp1, r1) with the potential on the mesh, the proper times of the probe observers and
    their rates d t_p / d tau at the two ends of the step (light rays, ray_newton.py)."""
    H0 = pm.H0
    out = {"tau": [], "a": []}
    for i in range(len(probes)):
        for key in ("delta_N", "psi_N", "dpsi_dlna", "t_p"):
            out[f"{key}_{i}"] = []
    if track is not None:
        track = np.asarray(track)
        out.update({"x": [], "v": [], "psi_p": [], "t_p": []})
        xu = pm.x[track].copy()        # unwrapped positions
    nstep = int(round(tau_end/dtau))

    def rates():
        """Perturbation of d t_p / d tau at the probes and at the tracked particles,
        and the potential at the probes."""
        a = scale_factor(pm.tau, H0)
        psi = pm.psi()
        pp = np.array([corner_average(psi, pt, pm.L) for pt in probes])
        rp = a*(np.sqrt(1.0 + 2.0*pp) - 1.0)
        rt = pt_ = vt = None
        if track is not None:
            vt = pm.velocity()[track]
            pt_ = cid.interp(psi, pm.x[track], pm.L)
            rt = a*(np.sqrt(np.maximum(1.0 + 2.0*pt_ - (1.0 - 2.0*pt_)*(vt*vt).sum(axis=1),
                                       0.0)) - 1.0)
        return a, pp, rp, pt_, vt, rt, psi

    a, pp, rp, ptk, vt, rt, psi_mesh = rates()
    dtp = np.zeros(len(probes))
    dtt = np.zeros(len(track)) if track is not None else None
    a_rec, pp_rec = a, pp.copy()

    def record(first):
        nonlocal a_rec, pp_rec
        out["tau"].append(pm.tau)
        out["a"].append(a)
        for i, pt in enumerate(probes):
            out[f"delta_N_{i}"].append(corner_average(pm.delta, pt, pm.L))
            out[f"psi_N_{i}"].append(pp[i])
            out[f"dpsi_dlna_{i}"].append(0.0 if first else
                                         (pp[i] - pp_rec[i])/np.log(a/a_rec))
            out[f"t_p_{i}"].append(cosmic_time(pm.tau, H0) + dtp[i])
        a_rec, pp_rec = a, pp.copy()
        if track is not None:
            out["x"].append(xu.copy())
            out["v"].append(vt.copy())
            out["psi_p"].append(ptk.copy())
            out["t_p"].append(cosmic_time(pm.tau, H0) + dtt)

    record(True)
    for s in range(nstep):
        if track is not None:
            x_before = pm.x[track].copy()
        rp0, rt0 = rp, rt
        tau0, a0, psi0 = pm.tau, a, psi_mesh
        tp0 = cosmic_time(tau0, H0) + dtp
        pm.step(dtau)
        a, pp, rp, ptk, vt, rt, psi_mesh = rates()
        dtp = dtp + 0.5*dtau*(rp + rp0)
        if hook is not None:
            hook(pm, tau0, psi0, tp0, a0 + rp0, psi_mesh,
                 cosmic_time(pm.tau, H0) + dtp, a + rp)
        if track is not None:
            dtt = dtt + 0.5*dtau*(rt + rt0)
            dx = pm.x[track] - x_before
            dx -= pm.L*np.round(dx/pm.L)
            xu += dx
        if (s + 1) % every == 0 or s == nstep - 1:
            record(False)
        if verbose and (s + 1) % 100 == 0:
            print(f"  step {s+1}/{nstep}  a = {a:.3f}  max delta_N = {pm.delta.max():.4g}")
    res = {k: np.array(v) for k, v in out.items()}
    # the first record has no time derivative of the potential: copy the second
    for i in range(len(probes)):
        if len(res[f"dpsi_dlna_{i}"]) > 1:
            res[f"dpsi_dlna_{i}"][0] = res[f"dpsi_dlna_{i}"][1]
        ar = res["a"]
        res[f"rho_over_rho0_{i}"] = (1.0 + res[f"delta_N_{i}"] - 2.0*res[f"psi_N_{i}"]
                                     - 2.0*res[f"dpsi_dlna_{i}"])/ar**3
        a_p = (1.0 + 1.5*H0*res[f"t_p_{i}"])**(2.0/3.0)
        res[f"a_p_{i}"] = a_p
        res[f"delta_obs_{i}"] = res[f"rho_over_rho0_{i}"]*a_p**3 - 1.0
    return res


def east_particles(delta, n, ppc=1, L=4.0, H0=1.0, ratios=(1.0, 0.9, 1.1)):
    """Newtonian initial conditions of East, Wojtak & Pretorius: lattice (shifted by half
    a spacing for an odd number per cell, as in the relativistic data) displaced by the
    Zel'dovich approximation, velocities of the growing mode, masses that make the
    density contrast equal to sum_i d_i sin(k x_i) at the particle positions."""
    k = 2.0*np.pi/L
    d = [delta*r for r in ratios]
    npd = n*ppc
    hq = L/npd
    q1 = (np.arange(npd) + (1.0 if ppc % 2 == 1 else 0.5))*hq
    Q = np.meshgrid(q1, q1, q1, indexing="ij")
    q = np.stack([a.ravel() for a in Q], axis=1)
    xi = np.stack([d[i]*np.cos(k*q[:, i])/k for i in range(3)], axis=1)
    jac = np.prod(1.0 - np.stack([d[i]*np.sin(k*q[:, i]) for i in range(3)], axis=1),
                  axis=1)
    x = np.mod(q + xi, L)
    dN = sum(d[i]*np.sin(k*x[:, i]) for i in range(3))
    v = np.stack([H0*d[i]*np.cos(k*x[:, i])/k for i in range(3)], axis=1)
    rho0 = 3.0*H0**2/(8.0*np.pi)
    m = rho0*(1.0 + dN)*jac*hq**3
    return x, v, m, q          # p = a v = v at a = 1
