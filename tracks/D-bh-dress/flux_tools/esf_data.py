#!/usr/bin/env python3
"""ES-F: the first matter run after the vacuum-bubble benchmark ES-1. The bubble of ES-1
is filled: uniform dust of the ES-1 plateau density from a vacuum core around the hole
(smooth edge over 3 <= R <= 5 M) to the outer edge of ES-1 (smooth over 52 <= R <= 60 M),
moving with the unperturbed Hubble flow around the seed hole, i.e. the secondary-infall
set-up of wave 2 (`secondary_infall/`, absorbing case) with eps = H M of ES-1.

Exact data (G = c = 1, M = 1, areal radius R, isotropic rbar; derivation in README.md,
section "ES-F"). With dust at rest in the slice (u_i = 0, S_i = 0) and the slicing
f^2 = 1 - M/m(R), i.e. the LTB energy E(R) = -M/R of every shell (the Newtonian
"Hubble flow + seed", v = H R):
    m(R) = M + D(R),  D(R) = 4 pi int_{R_in}^{R} rho R'^2 dR'     (Misner-Sharp mass)
    KT = -sqrt(2 D / R^3),  KL = KT + R dKT/dR                      (momentum constraint)
    (dR/dl)^2 = 1 - 2 m (1 - f^2)/R = 1 - 2M/R  on the whole slice,
so the spatial metric is exactly Schwarzschild of mass M: psi = 1 + M/(2 rbar), the table
has u = 0 and the puncture carries m_p = M. Hamiltonian constraint: R_3 = 0 (psi harmonic)
and 4 KL KT + 2 KT^2 = 4 D'/R^2 = 16 pi rho. Each dust particle carries the conserved
Misner-Sharp energy per unit rest mass E_K = (1 + 2E)^(1/2) = (1 - 2M/R0)^(1/2); the
rest mass of a lattice particle is rho psi^6 h^3 (proper volume).

    esf_data.py [--out DIR] [--hp 1.0] [--drbar 0.02] [--rbar_max 345]

Writes into --out: esf.tab (format 2), esf.nrp (140 tracers, then the dust lattice),
esf_labels.npz (per tag: R0, E_K, m(R0), rest mass, tau_H, tau_0), energy_by_tag.npy
(for compare.py --energy_by_tag), esf_growth.csv (exact LTB growth law), v0.nrp (the
140 tracers alone, for the vacuum control V-0), esf.json, figures.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ES_DIR = os.path.join(HERE, "..", "einstein_straus")
sys.path.insert(0, HERE)
sys.path.insert(0, ES_DIR)
import es_model as em  # noqa: E402  (read-only use: smooth step, Tab2, table writer)
import fluxio  # noqa: E402

GEOM_ES1 = dict(M=1.0, Rw=40.0, w_in=4.0, Rb=56.0, w_out=4.0, R0=4.0)   # es_runs/make_data.py
TRACER_R0 = (6.0, 10.0, 20.0, 28.0, 36.0, 40.0, 48.0, 56.0, 66.0, 78.0)  # as ES-1
GL_X, GL_W = np.polynomial.legendre.leggauss(10)


def directions14():
    d = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    d += [(sx, sy, sz) for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]
    d = np.array(d, float)
    return d / np.linalg.norm(d, axis=1)[:, None]


class FilledBubble:
    def __init__(self, M=1.0, rho0=None, Rc=4.0, w_in=1.0, Rb=56.0, w_out=4.0):
        self.M, self.Rc, self.w_in, self.Rb, self.w_out = M, Rc, w_in, Rb, w_out
        if rho0 is None:
            rho0 = em.EinsteinStrausBH(**GEOM_ES1).rho0
        self.rho0 = float(rho0)
        self.H = math.sqrt(8.0 * math.pi * self.rho0 / 3.0)
        self.Rin, self.Rout = Rc - w_in, Rb + w_out
        # D(R) on a fine table by 10-point Gauss-Legendre per interval (positive pieces:
        # relative accuracy also where D is exponentially small at the inner edge)
        self._Rg = np.concatenate([np.linspace(self.Rin, self.Rc + w_in, 4001),
                                   np.linspace(self.Rc + w_in, self.Rb - w_out, 4001)[1:],
                                   np.linspace(self.Rb - w_out, self.Rout, 4001)[1:]])
        a, b = self._Rg[:-1], self._Rg[1:]
        self._Dg = np.concatenate([[0.0], np.cumsum(self._piece(a, b))])
        self.Dtot = float(self._Dg[-1])
        self.Mtot = self.M + self.Dtot

    def density(self, R):
        R = np.asarray(R, float)
        s_in = em.smooth_step((R - self.Rin) / (2.0 * self.w_in))
        s_out = 1.0 - em.smooth_step((R - (self.Rb - self.w_out)) / (2.0 * self.w_out))
        return self.rho0 * s_in * s_out

    def _piece(self, a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        h = 0.5 * (b - a)
        c = 0.5 * (b + a)
        R = c[..., None] + h[..., None] * GL_X
        return 4.0 * math.pi * h * np.sum(GL_W * self.density(R) * R * R, axis=-1)

    def D(self, R):
        """m(R) - M without cancellation."""
        R = np.atleast_1d(np.asarray(R, float))
        Rc = np.clip(R, self.Rin, self.Rout)
        k = np.clip(np.searchsorted(self._Rg, Rc, side="right") - 1, 0, self._Rg.size - 2)
        out = self._Dg[k] + self._piece(self._Rg[k], Rc)
        return np.where(R <= self.Rin, 0.0, np.where(R >= self.Rout, self.Dtot, out))

    def mass(self, R):
        return self.M + self.D(R)

    def curvature(self, R):
        """KT, KL at areal radius R (outer sheet)."""
        R = np.atleast_1d(np.asarray(R, float))
        D = self.D(R)
        Dp = 4.0 * math.pi * R * R * self.density(R)
        KT = -np.sqrt(2.0 * D / R ** 3)
        sD = np.sqrt(2.0 * D)
        with np.errstate(divide="ignore", invalid="ignore"):
            dKT = np.where(D > 0, -(Dp / sD) * R ** -1.5 + 1.5 * sD * R ** -2.5, 0.0)
        KL = KT + R * dKT
        return KT, KL

    # isotropic coordinates: psi = 1 + M/(2 rbar), R = rbar psi^2
    def psi(self, rbar):
        return 1.0 + self.M / (2.0 * np.asarray(rbar, float))

    def areal(self, rbar):
        return np.asarray(rbar, float) * self.psi(rbar) ** 2

    def rbar_of_R(self, R):
        R = np.asarray(R, float)
        return 0.5 * ((R - self.M) + np.sqrt(R * R - 2.0 * self.M * R))

    def table(self, drbar=0.02, rbar_max=345.0):
        n = int(math.ceil(rbar_max / drbar)) + 1
        rbar = drbar * np.arange(n)
        outer = rbar >= 0.5 * self.M
        R = np.where(outer, self.areal(np.where(rbar > 0, rbar, 1.0)), 0.0)
        KT = np.zeros(n)
        KL = np.zeros(n)
        if np.any(outer):
            kt, kl = self.curvature(R[outer])
            KT[outer], KL[outer] = kt, kl
        alpha = np.where(rbar > 0, self.psi(np.where(rbar > 0, rbar, 1.0)) ** -2, 0.0)
        return em.Tab2(rbar, np.zeros(n), KL, KT, alpha, np.zeros(n), exterior="zero")

    # LTB motion of the shell that starts at R0 with E = -M/R0, m = m(R0), expanding
    def shell_times(self, R0):
        R0 = np.asarray(R0, float)
        m = self.mass(R0)
        T = m / (2.0 * self.M / R0) ** 1.5
        eta0 = np.arccos(np.clip(1.0 - 2.0 * self.M / m, -1, 1))          # expanding branch
        etaH = 2.0 * math.pi - np.arccos(np.clip(1.0 - 4.0 * self.M / R0, -1, 1))
        base = eta0 - np.sin(eta0)
        tauH = T * ((etaH - np.sin(etaH)) - base)
        tau0 = T * (2.0 * math.pi - base)
        Rmax = m * R0 / self.M
        tau_ta = T * (math.pi - base)
        return dict(m=m, tauH=tauH, tau0=tau0, Rmax=Rmax, tau_ta=tau_ta)

    def lattice(self, h):
        nmax = int(math.ceil(self.rbar_of_R(self.Rout) / h)) + 2
        k = (np.arange(-nmax, nmax) + 0.5) * h
        xs, ms, Rs = [], [], []
        for xi in k:
            Y, Z = np.meshgrid(k, k, indexing="ij")
            rb = np.sqrt(xi * xi + Y * Y + Z * Z)
            sel = rb >= 0.5 * self.M
            R = np.where(sel, self.areal(np.maximum(rb, 1e-300)), 0.0)
            sel &= (R > self.Rin) & (R < self.Rout)
            if not np.any(sel):
                continue
            rho = self.density(R[sel])
            keep = rho > 0
            n = int(keep.sum())
            xs.append(np.stack([np.full(n, xi), Y[sel][keep], Z[sel][keep]], axis=1))
            ms.append(rho[keep] * self.psi(rb[sel][keep]) ** 6 * h ** 3)
            Rs.append(R[sel][keep])
        return np.concatenate(xs), np.concatenate(ms), np.concatenate(Rs)

    def rest_mass(self, R):
        """Continuum rest mass inside areal radius R: int rho 4 pi R^2 dR / W."""
        Rg = np.linspace(self.Rin, R, 200001)
        f = 4.0 * math.pi * Rg ** 2 * self.density(Rg) / np.sqrt(1.0 - 2.0 * self.M / Rg)
        return float(np.trapz(f, Rg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--hp", type=float, default=1.0)
    ap.add_argument("--drbar", type=float, default=0.02)
    ap.add_argument("--rbar_max", type=float, default=345.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fb = FilledBubble()
    tab = fb.table(a.drbar, a.rbar_max)
    hdr = [f"model = ES-F: ES-1 bubble filled (flux_tools/esf_data.py), M = {fb.M}",
           f"rho0 = {fb.rho0!r}, H = {fb.H!r}, dust {fb.Rin} < R < {fb.Rout} M (smooth edges)",
           "slicing f^2 = 1 - M/m(R) (LTB energy -M/R); spatial metric Schwarzschild of M",
           f"puncture component of bare mass m_p = {fb.M!r} required (u = 0 here)",
           "alpha = psi^-2 (unused with lapse = precollapsed); betar = 0 (unused, shift = zero)",
           f"table covers the mesh corner of ES-1 (+-192 M -> 332.6 M); M_tot = {fb.Mtot!r}"]
    em.write_tab2(os.path.join(a.out, "esf.tab"), tab, header=hdr)
    # particles: tracers first (tags 0-139), then the lattice
    dirs = directions14()
    xt = np.concatenate([fb.rbar_of_R(R0) * dirs for R0 in TRACER_R0])
    Rt = np.repeat(TRACER_R0, len(dirs))
    xl, ml, Rl = fb.lattice(a.hp)
    x = np.vstack([xt, xl])
    m = np.concatenate([np.full(len(xt), 1e-30), ml])
    R0 = np.concatenate([Rt, Rl])
    fluxio.write_nrp(os.path.join(a.out, "esf.nrp"), x, np.zeros_like(x), m)
    fluxio.write_nrp(os.path.join(a.out, "v0.nrp"), xt, np.zeros_like(xt), np.full(len(xt), 1e-30))
    EK = np.sqrt(1.0 - 2.0 * fb.M / R0)
    st = fb.shell_times(R0)
    np.save(os.path.join(a.out, "energy_by_tag.npy"), EK)
    np.savez_compressed(os.path.join(a.out, "esf_labels.npz"), R0=R0, E_K=EK, m_label=st["m"],
                        rest=m, tauH=st["tauH"], tau0=st["tau0"])
    # growth law on a fine label grid
    Rg = np.geomspace(fb.Rin * 1.0001, fb.Rout, 4000)
    sg = fb.shell_times(Rg)
    mono = bool(np.all(np.diff(sg["tauH"]) > 0))
    np.savetxt(os.path.join(a.out, "esf_growth.csv"),
               np.column_stack([Rg, sg["m"], sg["tauH"], sg["tau0"], sg["Rmax"], sg["tau_ta"]]),
               delimiter=",", header="R0,m_MisnerSharp,tau_horizon,tau_centre,R_max,tau_turnaround",
               comments="")
    lat_rest = float(ml.sum())
    lat_ms = float(np.sum(ml * np.sqrt(1.0 - 2.0 * fb.M / Rl)))
    cont_rest = fb.rest_mass(fb.Rout)
    summ = dict(rho0=fb.rho0, H=fb.H, eps=fb.H * fb.M, t_i=2.0 / (3.0 * fb.H * fb.M),
                Rin=fb.Rin, Rout=fb.Rout, Dtot=fb.Dtot, Mtot=fb.Mtot,
                n_tracers=int(len(xt)), n_dust=int(len(xl)), hp=a.hp,
                lattice_rest_mass=lat_rest, continuum_rest_mass=cont_rest,
                lattice_rest_relerr=lat_rest / cont_rest - 1.0,
                lattice_misner_sharp=lat_ms, lattice_ms_relerr=lat_ms / fb.Dtot - 1.0,
                tauH_monotonic=mono, table_rows=int(len(tab.rbar)), drbar=a.drbar,
                rbar_max=float(tab.rbar[-1]),
                growth={f"tau={t:g}": float(np.interp(t, sg["tauH"], sg["m"]))
                        for t in (25, 50, 100, 150, 200, 250, 300, 400, 600)},
                tracer_tauH={str(r): float(fb.shell_times(np.array([r]))["tauH"][0]) for r in TRACER_R0})
    with open(os.path.join(a.out, "esf.json"), "w") as f:
        json.dump(summ, f, indent=1)
    figures(a.out, fb, tab, sg)
    print(json.dumps(summ, indent=1))


def figures(out, fb, tab, sg):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    R = np.geomspace(2.05, 80, 2000)
    KT, KL = fb.curvature(R)
    ax[0].loglog(R, fb.density(R) + 1e-30, color=figstyle.PAL["blue"], label=r"$\rho$")
    ax[0].loglog(R, -KT, color=figstyle.PAL["red"], label=r"$-K_T$")
    ax[0].loglog(R, np.abs(KL) + 1e-30, color=figstyle.PAL["green"], label=r"$|K_L|$")
    ax[0].set_ylim(1e-8, 1e-1)
    ax[0].set_xlabel(r"$R\ [M]$")
    ax[0].legend(fontsize=7)
    ax[1].plot(R, fb.mass(R), color=figstyle.PAL["blue"], label=r"$m(R)$")
    ax[1].plot(R, np.sqrt(np.maximum(1 - fb.M / fb.mass(R), 0)), color=figstyle.PAL["red"],
               label=r"$f=(1-M/m)^{1/2}$")
    ax[1].set_xlabel(r"$R\ [M]$")
    ax[1].legend(fontsize=7)
    ax[2].plot(sg["tauH"], sg["m"], color=figstyle.PAL["blue"], label="exact LTB")
    ax[2].set_xlim(0, 700)
    ax[2].set_ylim(1, 1.6)
    ax[2].set_xlabel(r"proper time of the shell at the horizon $\tau\ [M]$")
    ax[2].set_ylabel(r"$M_{\rm AH}=m(R_0)\ [M]$")
    ax[2].legend(fontsize=7)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "esf_data"))
    plt.close(fig)


if __name__ == "__main__":
    main()
