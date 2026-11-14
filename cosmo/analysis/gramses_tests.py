"""Tests of Barrera-Hinojosa & Li, arXiv:2001.07968 (GRAMSES Part II, initial conditions),
on initial conditions made by cosmo/ic/gramses_ic.py at reduced size.

    python3 gramses_tests.py expect                    expected numbers (closed forms only)
    python3 gramses_tests.py closed                    closed-form checks, Fig. 1 analogue
    python3 gramses_tests.py estimator [--n 128]       mesh estimator on lattice ICs
    python3 gramses_tests.py ics --L 4000 --z 49 [--n 256]   one box and redshift
    python3 gramses_tests.py fig4 [--n 256]            sigma8 variants (4 Gpc/h, z = 49)
    python3 gramses_tests.py t0prec [--n 256]          single-precision and table-rounding
                                                       emulations of the FD velocity
    python3 gramses_tests.py report [--n 256]          figures and gramses_tests.json

Specification: cosmo/notes/spec_2001.07968.md ("notes:L" = its line L). Every test is on
initial-condition data at z_ini; nothing is evolved. No Boltzmann code is used: the spectra
are Eisenstein-Hu times the matter + Lambda growth factor and the gauges follow from the
closed forms of notes Sec. 5.3, so everything that depends on radiation is discussed, not
reproduced (cosmo/notes/c6_report.md).

Estimators. Lagrangian: the particles sit on a lattice, so the particle velocities, laid
out on the lattice, are a mesh field whose spectrum is exact (it is the mesh field the
particles were made from). Eulerian: the particles are deposited with a B-spline cloud
(cosmo_id.cic_deposit) on a mesh and measured with random_field.measure_power with the
B-spline window divided out (deconvolve = degree). Bins: width k_f = 2 pi/L with edges at
integer multiples of k_f, first bin [k_f, 2 k_f) (as the paper's DTFE bins, notes:342-345),
up to the particle Nyquist frequency k_Ny = pi n/L.

Stage outputs go to .work/c6/<stage>.json and .npz; "report" merges them into
cosmo/analysis/gramses_tests.json and writes the figures cosmo/analysis/figs/gramses_*.
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
import cosmo_id as cid             # noqa: E402
import gramses_ic as gi            # noqa: E402
import random_field as rf          # noqa: E402
import spectrum as sp              # noqa: E402

WORK = os.path.join(REPO, ".work", "c6")
FIGDIR = os.path.join(HERE, "figs")
JSON_OUT = os.path.join(HERE, "gramses_tests.json")
P = sp.GRAMSES
SEED = 2001
BOXES = (4000.0, 256.0)
ZINI = (99.0, 49.0)
DZS = (1.0, 0.5, 0.25, 0.05)                 # notes:449, II:410
SHAPE, DEGREE, MESH_FACTOR = "pcs", 3, 2     # Eulerian estimator (chosen in "estimator")

# numbers read from the paper's figures (notes Sec. 4)
PAPER = {
    "fig1_k_P": [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 2e-2, 0.1, 1.0],               # notes:377
    "fig1_P": {("p", 99): [4.67e5, 1.69e4, 462, 25.7, 6.02, 4.73, 0.963, 0.0118],
               ("S", 99): [0.0636, 0.183, 0.581, 1.63, 3.79, 4.18, 0.958, 0.0118],
               ("p", 49): [4.68e5, 1.70e4, 496, 40.6, 19.2, 17.5, 3.77, 0.0461],
               ("S", 49): [0.268, 0.771, 2.45, 6.72, 15.0, 16.4, 3.78, 0.0461],
               ("p", 19): [4.69e5, 1.72e4, 609, 106, 102, 104, 23.4, 0.285],
               ("S", 19): [1.74, 4.98, 15.8, 42.5, 92.9, 101, 23.2, 0.285]},
    "fig1_k_f": [1e-4, 1e-3, 2e-3, 3e-3, 5e-3, 1e-2, 2e-2, 0.1, 0.3],          # notes:386
    "fig1_f": {("S", 99): [1.053, 1.051, 1.047, 1.040, 1.023, 0.995, 0.986, 0.981, 0.9805],
               ("p", 99): [0.0003, 0.036, 0.129, 0.251, 0.484, 0.785, 0.924, 0.978, 0.980],
               ("S", 49): [1.028, 1.025, 1.020, 1.014, 1.003, 0.994, 0.9915, 0.9903,
                           0.9903],
               ("p", 49): [0.0007, 0.071, 0.233, 0.408, 0.656, 0.879, 0.960, 0.989,
                           0.990]},
    # Fig. 2 ratio P^CMC/P^S: (bin [j, j+1) k_f, measured, linear at bin centre), notes:420
    "fig2": {(4000.0, 99): [(1, 46.7, 41.4), (2, 8.89, 7.85), (3, 4.07, 3.67),
                            (6, 1.69, 1.58)],
             (4000.0, 49): [(1, 13.7, 13.3), (2, 3.57, 3.53), (3, 2.17, 2.10),
                            (6, 1.29, 1.27)],
             (256.0, 99): [(1, 1.049, 1.043), (2, 1.016, 1.014), (4, 1.005, 1.004)],
             (256.0, 49): [(1, 1.024, 1.021), (2, 1.007, 1.007), (4, 1.0025, 1.002)]},
    # Fig. 3 subpanel means of Delta P_N / P_N (notes:461-466)
    "fig3_dP": {99: {1.0: 2.0e-4, 0.5: 5.0e-5, 0.25: 1.1e-5, 0.05: 0.0},
                49: {1.0: 8.0e-4, 0.5: 2.0e-4, 0.25: 5.1e-5, 0.05: 0.0}},
    "fig3_dP_scatter_005": {99: 3.5e-4, 49: 1e-4},
    # lower-index CMC / N in the first 4 Gpc bin, k = 0.002225 (notes:470-474)
    "fig3_lower_first": {99: 0.0754, 49: 0.191},
    "fig3_lower_first_lin": {99: 0.0611, 49: 0.155},
    "fig3_lower_mean_k_gt_0.01": {99: -0.005, 49: -0.003},
    # Fig. 4 Delta P / P^N at k = 0.0022, 0.0038, 0.0054 and plateau (notes:509-515)
    "fig4": {"fd_def_s8_N": [-0.0192, -0.0192, -0.0192, -0.0192],
             "fd_def_s8_C": [-0.080, -0.043, -0.031, -0.019],
             "fd_inc_etadot_N": [0.055, 0.036, 0.021, 0.0],
             "fd_inc_etadot_C": [0.037, 0.022, 0.015, 0.0005],
             "backscaled_N": [0.016, -0.0005, -0.009, -0.0185]},
}


# ---------------------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------------------
def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def jdump(obj, path):
    def conv(o):
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, np.ndarray):
            return conv(o.tolist())
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return o
    with open(path, "w") as fh:
        json.dump(conv(obj), fh, indent=1)


def edges(n, L):
    """Bin edges k_f [1, 2, ..., n/2] (just below each integer multiple)."""
    kf = 2.0*np.pi/L
    return kf*(np.arange(1, n//2 + 1) - 1e-6)


def a_of(z):
    return 1.0/(1.0 + z)


def meszaros_growth(a):
    """Growing mode of sub-horizon CDM in matter + smooth radiation (no Lambda, no
    baryons): D = 1 + (3/2) a/a_eq, a_eq = Omega_r/Omega_m with Omega_r h^2 = 2.4728e-5
    (T_CMB = 2.7255 K) x (1 + 0.2271 x 3.046) for photons and three massless neutrinos.
    A model of the radiation-era growth that the paper's CAMB spectra contain (used only
    to discuss, not to reproduce, the radiation-dependent curves)."""
    om_r = 2.4728e-5*(P["t_cmb"]/2.7255)**4*(1.0 + 0.2271*3.046)/P["h"]**2
    a_eq = om_r/P["omega_m"]
    return 1.0 + 1.5*np.asarray(a, dtype=float)/a_eq


def meszaros_rate(a):
    """d ln D / d ln a of meszaros_growth: y/(1 + y), y = (3/2) a/a_eq."""
    y = meszaros_growth(a) - 1.0
    return y/(1.0 + y)


def fd_factor(z, dz):
    """Exact ratio of the finite-difference velocity (II:341) to the two-step velocity
    H f chi for the matter + Lambda growth factor: (1+z) [D(z-dz) - D(z+dz)] / (2 dz f D);
    Delta P/P = factor^2 - 1 ~ 2 dz^2/(1+z)^2 (notes:584-588)."""
    D = lambda zz: float(gi.growth(a_of(zz), P))                     # noqa: E731
    return (1.0 + z)*(D(z - dz) - D(z + dz))/(2.0*dz*float(gi.growth_rate(a_of(z), P))
                                               * D(z))


def realised_average(field, L, gfun, n_edges=None):
    """sum_k |field_k|^2 g(k) / sum_k |field_k|^2 per bin (k off the Nyquist planes),
    the expectation of a measured ratio of spectra whose modes are field_k sqrt(g)."""
    n = field.shape[0]
    e = edges(n, L) if n_edges is None else edges(n_edges, L)
    F = np.fft.rfftn(field)/field.size
    pw = (F.real**2 + F.imag**2).ravel()
    k1 = 2*np.pi*np.fft.fftfreq(n, d=L/n)
    kz = 2*np.pi*np.fft.rfftfreq(n, d=L/n)
    km = np.sqrt(k1[:, None, None]**2 + k1[None, :, None]**2 + kz[None, None, :]**2).ravel()
    w = np.broadcast_to(rf._half_weights(n)[None, None, :], (n, n, n//2 + 1)).ravel()
    idx = np.searchsorted(e, km, side="right") - 1
    ok = (idx >= 0) & (idx < len(e) - 1) & (km > 0)
    g = np.asarray(gfun(km[ok]), dtype=float)
    num = np.bincount(idx[ok], weights=w[ok]*pw[ok]*g, minlength=len(e) - 1)
    den = np.bincount(idx[ok], weights=w[ok]*pw[ok], minlength=len(e) - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return num/den


# ---------------------------------------------------------------------------------------
# linear response of a B-spline deposit of a displaced particle lattice
# ---------------------------------------------------------------------------------------
def _bspline(d, p):
    """B-spline of degree p (1 CIC, 2 TSC, 3 PCS) at offset d (cells) and its derivative."""
    d = np.asarray(d, dtype=float)
    ad = np.abs(d)
    sg = np.sign(d)
    if p == 1:
        w = np.where(ad < 1, 1 - ad, 0.0)
        dw = np.where(ad < 1, -sg, 0.0)
    elif p == 2:
        w = np.where(ad < 0.5, 0.75 - d*d, np.where(ad < 1.5, 0.5*(1.5 - ad)**2, 0.0))
        dw = np.where(ad < 0.5, -2*d, np.where(ad < 1.5, -sg*(1.5 - ad), 0.0))
    else:
        w = np.where(ad < 1, 2/3 - d*d + 0.5*ad**3, np.where(ad < 2, (2 - ad)**3/6, 0.0))
        dw = np.where(ad < 1, -2*d + 1.5*sg*d*d, np.where(ad < 2, -sg*0.5*(2 - ad)**2, 0.0))
    return w, dw


def lattice_response(kc, h, p, s):
    """Linear response, per Cartesian wavenumber component kc (h/Mpc), of a B-spline
    deposit of degree p on a mesh of spacing h for particles on a lattice of spacing s h
    whose sites are the cell centres of the coarse mesh: the fine mesh (s = 2) has the
    sites on cell faces (offsets (Z + 1/2) h), the same mesh (s = 1) at cell centres.
        S(k)  = sum_d W(d) exp(-i k h d)       (kernel sampled at the offsets)
        S1(k) = sum_d W'(d) exp(-i k h d) / h  (its derivative; -> i k S for a smooth
                                                field)
    For a displaced lattice at first order the deposited density is
    delta_dep(k) = -sum_i chi_i(k) S1(k_i) prod_{j != i} S(k_j) and the deposited
    momentum u_dep(k) = prod_j S(k_j) u(k). Returns (S, S1) per kc."""
    d = np.arange(-3, 4) + (0.5 if s == 2 else 0.0)
    w, dw = _bspline(d, p)
    ph = np.exp(-1j*np.outer(np.asarray(kc), d)*h)
    return ph @ w, ph @ dw/h


def deposit_response(n, L, p, s, field=None, nb_edges=None):
    """Predicted (measured / mesh-field) power ratios per bin for an Eulerian deposit of a
    lattice IC (lattice n^3 at the cell centres of the n mesh, deposit on s n cells, degree
    p, deconvolved with the continuous window prod sinc^(p+1)(k_i h/2)) at first order in
    the displacement, for potential flow: density response
        R_d = sum_i k_i S1(k_i)/i prod_{j!=i} S(k_j) / k^2,
    velocity (momentum) response R_v = prod_j S(k_j). The bin average weights each mode by
    the realised |field_k|^2 (or by 1 if field is None). Returns (R_d^2, R_v^2) per bin."""
    h = L/(s*n)
    k1 = 2*np.pi*np.fft.fftfreq(n, d=L/n)
    kz = 2*np.pi*np.fft.rfftfreq(n, d=L/n)
    S1x, D1x = lattice_response(k1, h, p, s)
    Sz, Dz = lattice_response(kz, h, p, s)
    sinc = lambda kk: np.sinc(kk*h/(2*np.pi))**(p + 1)              # noqa: E731
    Wx, Wz = sinc(k1), sinc(kz)
    KX, KY, KZ = k1[:, None, None], k1[None, :, None], kz[None, None, :]
    SX, SY, SZ = S1x[:, None, None], S1x[None, :, None], Sz[None, None, :]
    DX, DY, DZ = D1x[:, None, None], D1x[None, :, None], Dz[None, None, :]
    k2 = KX**2 + KY**2 + KZ**2
    k2s = np.where(k2 > 0, k2, 1.0)
    Rd = ((KX*DX*SY*SZ + KY*SX*DY*SZ + KZ*SX*SY*DZ)/1j).real/k2s
    Rv = (SX*SY*SZ).real
    Wb = (Wx[:, None, None]*Wx[None, :, None]*Wz[None, None, :])
    rd2, rv2 = (Rd/Wb)**2, (Rv/Wb)**2
    if field is None:
        pw = np.ones_like(k2)
    else:
        F = np.fft.rfftn(field)
        pw = F.real**2 + F.imag**2
    e = edges(n, L) if nb_edges is None else nb_edges
    km = np.sqrt(k2).ravel()
    w = np.broadcast_to(rf._half_weights(n)[None, None, :], k2.shape).ravel()*pw.ravel()
    idx = np.searchsorted(e, km, side="right") - 1
    ok = (idx >= 0) & (idx < len(e) - 1) & (km > 0)
    den = np.bincount(idx[ok], weights=w[ok], minlength=len(e) - 1)
    out = []
    for r in (rd2, rv2):
        num = np.bincount(idx[ok], weights=w[ok]*r.ravel()[ok], minlength=len(e) - 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out.append(num/den)
    return out


# ---------------------------------------------------------------------------------------
# measurements
# ---------------------------------------------------------------------------------------
def divergence(u, L):
    """theta = d_i u_i of three mesh arrays (spectral, cosmo_id.Torus derivatives)."""
    tor = cid.Torus(u[0].shape[0], L)
    T = sum(1j*tor.kd[i]*tor.fft(u[i]) for i in range(3))
    return tor.ifft(T)


def lagrangian_power(field, L, n):
    return rf.measure_power(field, L, edges(n, L))


def eulerian_density(x, n, L, shape=SHAPE, s=MESH_FACTOR, degree=DEGREE):
    """Density contrast of the particles deposited on (s n)^3 cells; returns the field."""
    m = s*n
    rho = cid.cic_deposit(x, np.ones(len(x)), m, L, shape)
    return rho/(len(x)/L**3) - 1.0, rho


def eulerian_velocity(x, u, n, L, rho=None, shape=SHAPE, s=MESH_FACTOR, weighted=False):
    """Momentum deposit per mean particle density (weighted=False), or divided by the
    deposited density (weighted=True, mass-weighted velocity), three arrays."""
    m = s*n
    nbar = len(x)/L**3
    out = []
    for i in range(3):
        pi = cid.cic_deposit(x, u[:, i], m, L, shape)/nbar
        if weighted:
            pi = pi/(rho/nbar)
        out.append(pi)
    return out


def measure_eulerian(field, L, n, degree=DEGREE):
    return rf.measure_power(field, L, edges(n, L), deconvolve=degree)


# ---------------------------------------------------------------------------------------
# stage: expect
# ---------------------------------------------------------------------------------------
def first_bin_scatter(L, z, gfun, nreal=20000, rng_seed=7):
    """Ensemble mean and 16/50/84 percentiles, over random realisations, of the realised
    mode average sum |d_k|^2 g(k) / sum |d_k|^2 in the first bin [k_f, 2 k_f) (|n| = 1,
    sqrt 2, sqrt 3: 3 + 6 + 4 independent complex modes), with |d_k|^2 exponential of mean
    P_SS(k)."""
    kf = 2*np.pi/L
    mags = np.array([1.0]*3 + [np.sqrt(2)]*6 + [np.sqrt(3)]*4)*kf
    pk = gi.power_S(mags, z, P)
    g = gfun(mags)
    rng = np.random.default_rng(rng_seed)
    e = rng.exponential(1.0, size=(nreal, len(mags)))*pk
    vals = (e*g).sum(1)/e.sum(1)
    return {"ensemble": float((pk*g).sum()/pk.sum()),
            "p16_50_84": [float(v) for v in np.percentile(vals, [16, 50, 84])],
            "k_mean": float((np.array([6, 12, 8])*np.array([1, np.sqrt(2), np.sqrt(3)])
                             ).sum()/26*kf)}


def stage_expect(args):
    ex = {}
    # Fig. 1: closed forms at the paper's k
    kP, kF = np.array(PAPER["fig1_k_P"]), np.array(PAPER["fig1_k_f"])
    f1 = {}
    for z in (99.0, 49.0, 19.0):
        a = a_of(z)
        f1[f"z{z:g}"] = {
            "P_S": gi.power_S(kP, z, P), "P_p": gi.power_gauge(kP, z, P, "p"),
            "f_S": [float(gi.growth_rate(a, P))]*len(kF),
            "f_p": gi.growth_rate_p(kF, a, P),
            "f_meszaros": float(meszaros_rate(a)),
            "P_p_1e-4": float(gi.power_gauge(1e-4, z, P, "p")),
            "9P_eta_1e-4": float(9*gi.power_gauge(1e-4, z, P, "eta")),
            "f_p_half_k": float(np.sqrt(3*gi.growth_rate(a, P) + 4.5*gi.omega_m_a(a, P))
                                * gi.conformal_hubble(a, P)),
            "fd_minus_analytic_est": (0.5/(1 + z))**2}
    ex["fig1"] = f1
    # T0 / Fig. 3 subpanel
    t0 = {}
    for z in ZINI:
        a = a_of(z)
        f = float(gi.growth_rate(a, P))
        f06 = float(gi.omega_m_a(a, P))**0.6
        row = {}
        for dz in DZS:
            c = fd_factor(z, dz)
            row[f"{dz:g}"] = {"exact": c*c - 1.0, "approx": 2*dz*dz/(1 + z)**2,
                              "dz_over_z": dz/z}
        t0[f"z{z:g}"] = {"dP": row, "f_exact": f, "f_omega0.6": f06,
                         "two_step_0.6_vs_exact": (f06/f)**2 - 1.0,
                         "float32_rel_err_per_particle_dz0.05":
                             np.sqrt(2/3)*2.0**-24*np.sqrt(4/3)*(1 + z)/(2*0.05)}
    ex["t0"] = t0
    # Fig. 2 ratios, Fig. 3 lower-index ratios: ensemble mode averages and first-bin scatter
    f2, f3 = {}, {}
    for L in BOXES:
        n = args.n
        kf = 2*np.pi/L
        for z in ZINI:
            a = a_of(z)
            kk, ps, _, nm = rf.expected_power(n, L, lambda k: gi.power_S(k, z, P), edges(n, L))
            _, pp, _, _ = rf.expected_power(n, L, lambda k: gi.power_gauge(k, z, P, "p"),
                                            edges(n, L))
            _, tn, _, _ = rf.expected_power(n, L, lambda k: gi.theta_power_N(k, z, P),
                                            edges(n, L))
            _, tl, _, _ = rf.expected_power(n, L, lambda k: gi.theta_power_lower(k, z, P),
                                            edges(n, L))
            key = f"L{L:g}_z{z:g}"
            bins = [r[0] for r in PAPER["fig2"][(L, int(z))]]
            f2[key] = {"bins": bins, "k": [kk[j - 1] for j in bins],
                       "ratio_ensemble": [pp[j - 1]/ps[j - 1] for j in bins],
                       "ratio_at_centre": [float(gi.power_ratio_pS(kk[j - 1], a, P))
                                           for j in bins],
                       "first_bin_realisations": first_bin_scatter(
                           L, z, lambda k: gi.power_ratio_pS(k, a, P)),
                       "ratio_last_bin": pp[-1]/ps[-1], "k_last": kk[-1]}
            low = (kk > 0.01)
            # the paper's bins run to k = 0.804 (4 Gpc) / 12.57 (256 Mpc), 1024^3;
            # thin shells at k > 0.01: the bin centre stands for the mode average
            ep = edges(1024, L)
            kp = 0.5*(ep[1:] + ep[:-1])
            tnp = gi.theta_power_N(kp, z, P)
            tlp = gi.theta_power_lower(kp, z, P)
            okp = kp > 0.01
            f3[key] = {"first_bin_lower_ratio_ensemble": tl[0]/tn[0],
                       "first_bin_lower_ratio_centre": float(
                           gi.theta_lower_T(kk[0], a, P)**2),
                       "first_bin_realisations": first_bin_scatter(
                           L, z, lambda k: gi.theta_lower_T(k, a, P)**2),
                       "mean_lower_over_N_minus1_k>0.01_our_bins": float(
                           np.mean(tl[low]/tn[low] - 1)),
                       "mean_lower_over_N_minus1_k>0.01_paper_bins_to_kNy1024": float(
                           np.mean(tlp[okp]/tnp[okp] - 1)),
                       "k_Ny": np.pi*n/L}
    ex["fig2"], ex["fig3"] = f2, f3
    # estimator: predicted deposit/mesh response at k_Ny/2 and k_Ny, flat weights
    est = {}
    for p in (2, 3):
        for s in (1, 2):
            rd, rv = deposit_response(64, 256.0, p, s)
            kk = 0.5*(edges(64, 256.0)[1:] + edges(64, 256.0)[:-1])
            kny = np.pi*64/256.0
            j2 = int(np.argmin(np.abs(kk - kny/2)))
            est[f"p{p}_s{s}"] = {"density_at_kNy/2": rd[j2], "density_at_kNy": rd[-1],
                                 "velocity_at_kNy/2": rv[j2], "velocity_at_kNy": rv[-1],
                                 "k_rel_1pct_density": float(
                                     kk[np.argmax(np.abs(rd - 1) > 0.01)]/kny),
                                 "k_rel_1pct_velocity": float(
                                     kk[np.argmax(np.abs(rv - 1) > 0.01)]/kny)}
    ex["estimator"] = est
    # Fig. 4: predicted Delta P / P^N for the sigma8 variants at z = 49, dz = 0.5, 4 Gpc
    ex["fig4"] = fig4_predictions(args.n)
    os.makedirs(WORK, exist_ok=True)
    jdump(ex, os.path.join(WORK, "expect.json"))
    print(json.dumps(json.load(open(os.path.join(WORK, "expect.json"))), indent=1)[:20000])


def fig4_variants():
    """(name, setting, sigma8 mode, growth function of the sigma8 targets)."""
    return [("fd_lin_s8_N", "newtonian", "linear", None),       # II:378 (corrected)
            ("fd_lin_s8_C", "gramses", "linear", None),         # II:384, 388 (corrected)
            ("fd_D1scaled_s8_C", "gramses", "scaled", None),    # II:384 skipped
            ("fd_def_s8_N", "newtonian", "linear", meszaros_growth),   # model of "def"
            ("fd_def_s8_C", "gramses", "linear", meszaros_growth),     # model of "def"
            ("fd_none_s8_C", "gramses", "none", None)]          # no renormalisation


def fig4_factor(k, setting, mode, gfn, z=49.0, dz=0.5):
    """Predicted u_FD / u_two-step per mode: with delta(z) = delta^S(z_ini) [r(z) + G(k)]
    (G = 0 for delta^S, G = -3 eta/delta^S for delta^p) and renormalisation factors
    c_+- = target/sigma8 of the table, u_FD / u_2s = c_FD [c_-(r_- + G) - c_+(r_+ + G)]
    / (r_- - r_+), with c_FD = fd_factor(z, dz)."""
    a0 = a_of(z)
    t = gi.sigma8_targets(z, dz, P, setting, mode if mode != "none" else "linear", gfn)
    r = gi.sigma8_targets(z, dz, P, setting, "linear")["r"]        # D_1 of the tables
    G = 0.0 if setting == "newtonian" else -3.0*gi.eta_T(k, a0, P)
    if mode == "none":
        cm = cp = 1.0
    else:
        tab = [gi._spectrum_table(setting, zz, z, P, "frozen") for zz in t["z"]]
        s8 = [gi.sigma8_of(tb) for tb in tab]
        cm, cp = t["sigma8"][0]/s8[0], t["sigma8"][2]/s8[2]
    return fd_factor(z, dz)*(cm*(r[0] + G) - cp*(r[2] + G))/(r[0] - r[2])


def fig4_predictions(n, L=4000.0, z=49.0, dz=0.5):
    out = {}
    kk, _, _, _ = rf.expected_power(n, L, lambda k: gi.power_S(k, z, P), edges(n, L))
    for name, setting, mode, gfn in fig4_variants():
        g2 = lambda k, s=setting, m=mode, gg=gfn: fig4_factor(k, s, m, gg, z, dz)**2  # noqa
        _, num, _, _ = rf.expected_power(n, L, lambda k: g2(k)*gi.theta_power_N(k, z, P),
                                         edges(n, L))
        _, den, _, _ = rf.expected_power(n, L, lambda k: gi.theta_power_N(k, z, P),
                                         edges(n, L))
        d = num/den - 1.0
        out[name] = {"first3": d[:3].tolist(), "plateau_k>0.05": float(np.mean(d[kk > 0.05])),
                     "k": kk[:3].tolist()}
    return out


# ---------------------------------------------------------------------------------------
# stage: closed (closed-form checks and the Fig. 1 analogue)
# ---------------------------------------------------------------------------------------
def stage_closed(args):
    res = gi.closed_form_checks(P)
    for r in res:
        tag = ("PASS" if r["ok"] else "FAIL") if r["kind"] == "implementation" else \
            ("AGREE" if r["ok"] else "DIFFER")
        print(f"{tag:6s} {r['name']}: {r['value']:.6g} (target {r['target']:.6g})")
    k = np.logspace(-4, 0.3, 400)
    out = {"checks": res, "fig1": {}}
    for z in (99.0, 49.0, 19.0):
        a = a_of(z)
        fdS = gi.growth_rate_fd(lambda zz: gi.power_S(k, zz, P), z, 0.5)
        fdp = gi.growth_rate_fd(lambda zz: gi.power_gauge(k, zz, P, "p"), z, 0.5)
        fp = gi.growth_rate_p(k, a, P)
        out["fig1"][f"z{z:g}"] = {
            "max|fFD_p - f_p|": float(np.abs(fdp - fp).max()),
            "max|fFD_S - f|": float(np.abs(fdS - gi.growth_rate(a, P)).max()),
            "f": float(gi.growth_rate(a, P)),
            "f_meszaros": float(meszaros_rate(a)),
            "k_half": float(np.sqrt(3*gi.growth_rate(a, P) + 4.5*gi.omega_m_a(a, P))
                            * gi.conformal_hubble(a, P)),
            "P_p_1e-4": float(gi.power_gauge(1e-4, z, P, "p")),
        }
        if (("p", int(z)) in PAPER["fig1_f"]):
            kf_ = np.array(PAPER["fig1_k_f"])
            out["fig1"][f"z{z:g}"]["f_p_at_paper_k"] = gi.growth_rate_p(kf_, a, P)
            out["fig1"][f"z{z:g}"]["paper_f_p"] = PAPER["fig1_f"][("p", int(z))]
            out["fig1"][f"z{z:g}"]["paper_f_S"] = PAPER["fig1_f"][("S", int(z))]
        kp_ = np.array(PAPER["fig1_k_P"])
        out["fig1"][f"z{z:g}"]["P_S_at_paper_k"] = gi.power_S(kp_, z, P)
        out["fig1"][f"z{z:g}"]["P_p_at_paper_k"] = gi.power_gauge(kp_, z, P, "p")
        out["fig1"][f"z{z:g}"]["paper_P_S"] = PAPER["fig1_P"][("S", int(z))]
        out["fig1"][f"z{z:g}"]["paper_P_p"] = PAPER["fig1_P"][("p", int(z))]
    os.makedirs(WORK, exist_ok=True)
    jdump(out, os.path.join(WORK, "closed.json"))
    fig_closed(k)


def fig_closed(k):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = {99.0: fs.PAL["red"], 49.0: "k", 19.0: fs.PAL["blue"]}
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.4))
    ax1 = fs.inch_axes(fig, 0.75, 2.05, 3.15, 3.2)
    ax2 = fs.inch_axes(fig, 0.75, 0.5, 3.15, 1.5)
    ax3 = fs.inch_axes(fig, 4.65, 2.05, 3.15, 3.2)
    ax4 = fs.inch_axes(fig, 4.65, 0.5, 3.15, 1.5)
    kP, kF = np.array(PAPER["fig1_k_P"]), np.array(PAPER["fig1_k_f"])
    for z in (99.0, 49.0, 19.0):
        a = a_of(z)
        c = cols[z]
        ax1.loglog(k, gi.power_gauge(k, z, P, "p"), color=c, label=f"$z={z:g}$")
        ax1.loglog(k, gi.power_S(k, z, P), color=c, ls="--")
        ax1.loglog(kP, PAPER["fig1_P"][("p", int(z))], "o", mfc="none", color=c, ms=5)
        ax1.loglog(kP, PAPER["fig1_P"][("S", int(z))], "s", mfc="none", color=c, ms=4)
        ax2.semilogx(kP, np.array(PAPER["fig1_P"][("p", int(z))])
                     / gi.power_gauge(kP, z, P, "p"), "o-", mfc="none", color=c, ms=4,
                     lw=1.0)
        ax2.semilogx(kP, np.array(PAPER["fig1_P"][("S", int(z))]) / gi.power_S(kP, z, P),
                     "s--", mfc="none", color=c, ms=3.5, lw=1.0)
        fp = gi.growth_rate_p(k, a, P)
        fdp = gi.growth_rate_fd(lambda zz: gi.power_gauge(k, zz, P, "p"), z, 0.5)
        ax3.semilogx(k, fp, color=c)
        ax3.semilogx(k[::25], fdp[::25], "+", color=c, ms=6)
        ax3.semilogx(k, np.full_like(k, float(gi.growth_rate(a, P))), color=c, ls="--")
        if ("p", int(z)) in PAPER["fig1_f"]:
            ax3.semilogx(kF, PAPER["fig1_f"][("p", int(z))], "o", mfc="none", color=c, ms=5)
            ax3.semilogx(kF, PAPER["fig1_f"][("S", int(z))], "s", mfc="none", color=c, ms=4)
            fpp = np.array(PAPER["fig1_f"][("p", int(z))])
            use = fpp >= 0.03                    # read to +-0.0005: skip the k = 1e-4 point
            ax4.semilogx(kF[use], fpp[use]/gi.growth_rate_p(kF[use], a, P), "o-",
                         mfc="none", color=c, ms=4, lw=1.0)
            ax4.semilogx(kF, np.array(PAPER["fig1_f"][("S", int(z))])
                         / float(gi.growth_rate(a, P)), "s--", mfc="none", color=c, ms=3.5,
                         lw=1.0)
            ax4.axhline(float(meszaros_rate(a)), color=c, lw=1.0, ls=":")
    ax1.set_ylabel(r"$P_{\delta\delta}(k)$ [$(h^{-1}$Mpc$)^3$]")
    ax1.set_ylim(2e-3, 3e6)
    hz = ax1.get_legend_handles_labels()
    leg = ax1.legend(hz[0], hz[1], loc="lower left", fontsize=8)
    ax1.add_artist(leg)
    st = [ax1.plot([], [], color="grey")[0], ax1.plot([], [], color="grey", ls="--")[0],
          ax1.plot([], [], "o", mfc="none", color="grey")[0],
          ax1.plot([], [], "s", mfc="none", color="grey")[0]]
    ax1.legend(st, [r"$\delta^p$ (CMC-MD), closed form", r"$\delta^{\rm S}$ (synchronous)",
                    "paper, CMC", "paper, S"], loc="upper right", fontsize=8)
    ax2.axhline(1.0, **fs.THIN)
    ax2.set_ylabel("paper / ours")
    ax2.set_ylim(0.84, 1.12)
    ax2.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
    ax3.axhline(1.0, color="grey", ls=":", lw=1.0)
    ax3.set_ylim(-0.03, 1.12)
    ax3.set_ylabel(r"growth rate $f$")
    ax3.plot([], [], color="grey", label=r"$f_p$ closed form")
    ax3.plot([], [], "+", color="grey", label=r"$f^{\rm FD}$ (II:349), $\Delta z=0.5$")
    ax3.plot([], [], color="grey", ls="--", label=r"$f_{\rm S}=f$")
    ax3.legend(loc="center right", fontsize=8)
    ax4.axhline(1.0, **fs.THIN)
    ax4.set_ylabel("paper / ours")
    ax4.set_ylim(0.935, 1.065)
    ax4.plot([], [], color="grey", ls=":", lw=1.0, label=r"M$\acute{\rm e}$sz$\acute{\rm a}$ros $f$")
    ax4.legend(loc="upper right", fontsize=8)
    ax4.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
    for ax in (ax1, ax3):
        ax.set_xticklabels([])
    for ax in (ax1, ax2, ax3, ax4):
        ax.set_xlim(8e-5, 2.0)
    os.makedirs(FIGDIR, exist_ok=True)
    fs.save(fig, os.path.join(FIGDIR, "gramses_fig1_growth"))
    plt.close(fig)
    log("wrote", os.path.join(FIGDIR, "gramses_fig1_growth.png"))


# ---------------------------------------------------------------------------------------
# stage: ics (one box and redshift: Figs. 2, 3 and T0)
# ---------------------------------------------------------------------------------------
VEL_WEIGHTED = False     # Eulerian velocity: momentum deposit per mean density


def main_dz(z):
    """The Delta z of DZS closest to 1 % of z_ini (II:410)."""
    return min(DZS, key=lambda d: abs(d/z - 0.01))


def stage_ics(args):
    n, L, z = args.n, args.L, args.z
    a = a_of(z)
    tag = f"L{L:g}_z{z:g}_n{n}"
    arr, st = {}, {"n": n, "L": L, "z": z, "seed": SEED, "k_Ny": np.pi*n/L,
                   "shape": SHAPE, "mesh": MESH_FACTOR*n, "vel_weighted": VEL_WEIGHTED}
    dzm = main_dz(z)
    st["dz_main"] = dzm

    # Newtonian setting, two-step velocities (the "default 2LPTic" reference)
    icN = gi.make_ic(n, L, z, "newtonian", "two-step", seed=SEED)
    dS = icN["mesh"]["delta"]
    k, p, nm = lagrangian_power(dS, L, n)
    arr.update(k=k, nmodes=nm, P_dS_mesh=p)
    thN = divergence(icN["mesh"]["u"], L)
    arr["Pth_2s_L"] = lagrangian_power(thN, L, n)[1]
    xS, u2s = icN["x"], icN["u"]
    chi = np.stack([c.ravel() for c in icN["mesh"]["chi"]], 1)
    st["rms_chi_over_spacing"] = float(np.sqrt((chi**2).sum(1).mean())/(L/n))
    st["rms_delta_S_mesh"] = float(dS.std())
    st["u2s_rms_kms"] = float(np.sqrt((u2s**2).sum(1).mean()))
    del icN, chi
    log(tag, "newtonian two-step done")

    # Newtonian setting, finite-difference velocities, double and single precision
    keepFD = None
    for dz in DZS:
        c = fd_factor(z, dz)
        for prec, dt in (("64", np.float64), ("32", np.float32)):
            ic = gi.make_ic(n, L, z, "newtonian", "fd", dz=dz, seed=SEED, fd_dtype=dt)
            th = divergence(ic["mesh"]["u"], L)
            arr[f"Pth_fdN{prec}_dz{dz:g}_L"] = lagrangian_power(th, L, n)[1]
            st[f"fdN{prec}_dz{dz:g}"] = {
                "max|u_FD - c u_2s|/max|u_2s|": float(np.abs(ic["u"] - c*u2s).max()
                                                       / np.abs(u2s).max()),
                "rms|u_FD/(c u_2s) - 1|": float(np.sqrt(np.mean(
                    ((ic["u"] - c*u2s)**2).sum(1))/np.mean((c*u2s)**2*3))),
                "c": c, "c_minus": ic["meta"]["c_minus"], "c_plus": ic["meta"]["c_plus"],
                "sigma8": ic["meta"]["sigma8_targets"]["sigma8"]}
            if dz == dzm and prec == "64":
                keepFD = ic["u"]
                st["positions_FD_equal_two_step"] = bool(np.array_equal(ic["x"], xS))
            del ic
        log(tag, f"newtonian fd dz={dz:g} done")

    # GRAMSES setting: finite difference (u^i_C) and the lower-index velocity
    keepC = None
    for dz in DZS:
        ic = gi.make_ic(n, L, z, "gramses", "fd", dz=dz, seed=SEED, lower=True)
        th = divergence(ic["mesh"]["u"], L)
        arr[f"Pth_fdC_dz{dz:g}_L"] = lagrangian_power(th, L, n)[1]
        thl = divergence(ic["mesh"]["u_lower"], L)
        arr[f"Pth_lowC_dz{dz:g}_L"] = lagrangian_power(thl, L, n)[1]
        c = fd_factor(z, dz)
        st[f"fdC_dz{dz:g}"] = {
            "max|u_C - c u_2s|/max|u_2s|": float(np.abs(ic["u"] - c*u2s).max()
                                                  / np.abs(u2s).max()),
            "c_minus": ic["meta"]["c_minus"], "c_ini": ic["meta"]["c_ini"],
            "c_plus": ic["meta"]["c_plus"], "sigma8": ic["meta"]["sigma8_targets"]}
        if dz == dzm:
            keepC = (ic["x"], ic["u"], ic["u_lower"])
            dp = ic["mesh"]["delta"]
            arr["P_dp_mesh"] = lagrangian_power(dp, L, n)[1]
            arr["ratio_pS_realised"] = arr["P_dp_mesh"]/arr["P_dS_mesh"]
            # realised expectation of the lower/N ratio and of the FD lower spectrum
            arr["lowerN_realised"] = realised_average(
                thN, L, lambda kk: gi.theta_lower_T(kk, a, P)**2)
            tor = cid.Torus(n, L)
            Fd, FS = tor.fft(dp), tor.fft(dS)
            good = np.abs(FS) > 1e-10*np.abs(FS).max()
            kk = np.sqrt(tor.k2)[good]
            st["max|dp_k/dS_k - closed form|"] = float(np.abs(
                (Fd[good]/FS[good]).real/gi.deltap_T(kk, a, P) - 1).max())
            Ul = sum(1j*tor.kd[i]*tor.fft(ic["mesh"]["u_lower"][i]) for i in range(3))
            Uu = sum(1j*tor.kd[i]*tor.fft(ic["mesh"]["u"][i]) for i in range(3))
            g2 = np.abs(Uu) > 1e-10*np.abs(Uu).max()
            st["max|theta_lower/theta - k^2/(k^2+m^2)|"] = float(np.abs(
                (Ul[g2]/Uu[g2]).real - gi.theta_lower_T(np.sqrt(tor.k2)[g2], a, P)).max())
            del Fd, FS, Ul, Uu
        del ic
        log(tag, f"gramses fd dz={dz:g} done")

    # GRAMSES setting: two-step (paper II:333) and naive H f chi_p, Lagrangian only
    ic = gi.make_ic(n, L, z, "gramses", "two-step", seed=SEED)
    st["two_step_C_equals_N"] = float(np.abs(ic["u"] - u2s).max()/np.abs(u2s).max())
    arr["Pth_2sC_L"] = lagrangian_power(divergence(ic["mesh"]["u"], L), L, n)[1]
    del ic
    ic = gi.make_ic(n, L, z, "gramses", "naive", seed=SEED)
    arr["Pth_naiveC_L"] = lagrangian_power(divergence(ic["mesh"]["u"], L), L, n)[1]
    del ic

    # linear theory, ensemble mode averages and sample variance
    for name, fn in (("S", lambda kk: gi.power_S(kk, z, P)),
                     ("p", lambda kk: gi.power_gauge(kk, z, P, "p")),
                     ("thN", lambda kk: gi.theta_power_N(kk, z, P)),
                     ("thL", lambda kk: gi.theta_power_lower(kk, z, P))):
        _, pb, sb, _ = rf.expected_power(n, L, fn, edges(n, L))
        arr[f"lin_{name}"], arr[f"sig_{name}"] = pb, sb
    # predicted linear response of the Eulerian estimator (realised weights)
    arr["resp_dens"], _ = deposit_response(n, L, DEGREE, MESH_FACTOR, field=dS)
    arr["resp_vel"] = deposit_response(n, L, DEGREE, MESH_FACTOR, field=thN)[1]
    del thN
    log(tag, "lagrangian part done")

    # Eulerian deposits (PCS on a mesh of 2n)
    xp, uC, ulow = keepC
    dE, rhoS = eulerian_density(xS, n, L)
    arr["P_dS_E"] = measure_eulerian(dE, L, n)[1]
    del dE
    log(tag, "deposit S")
    for name, uu in (("2s", u2s), ("fdN", keepFD)):
        v = eulerian_velocity(xS, uu, n, L, rhoS, weighted=VEL_WEIGHTED)
        arr[f"Pth_{name}_E"] = measure_eulerian(divergence(v, L), L, n)[1]
        del v
        log(tag, f"deposit velocity {name}")
    del rhoS
    dE, rhoC = eulerian_density(xp, n, L)
    arr["P_dp_E"] = measure_eulerian(dE, L, n)[1]
    del dE
    v = eulerian_velocity(xp, ulow, n, L, rhoC, weighted=VEL_WEIGHTED)
    arr["Pth_lowC_E"] = measure_eulerian(divergence(v, L), L, n)[1]
    del v, rhoC
    log(tag, "deposits done")
    np.savez(os.path.join(WORK, f"ics_{tag}.npz"), **arr)
    jdump(st, os.path.join(WORK, f"ics_{tag}.json"))
    log(tag, "saved")


# ---------------------------------------------------------------------------------------
# stage: fig4 (sigma8 variants, 4 Gpc/h, z = 49, dz = 0.5)
# ---------------------------------------------------------------------------------------
def stage_fig4(args):
    n, L, z, dz = args.n, 4000.0, 49.0, 0.5
    a = a_of(z)
    ref = gi.make_ic(n, L, z, "newtonian", "two-step", seed=SEED)
    th0 = divergence(ref["mesh"]["u"], L)
    k, p0, nm = lagrangian_power(th0, L, n)
    _, pd0, _ = lagrangian_power(ref["mesh"]["delta"], L, n)
    arr = {"k": k, "Pth_ref": p0, "Pdd_ref": pd0}
    st = {}
    for name, setting, mode, gfn in fig4_variants():
        ic = gi.make_ic(n, L, z, setting, "fd", dz=dz, sigma8=mode, growth_fn=gfn, seed=SEED)
        th = divergence(ic["mesh"]["u"], L)
        arr[f"Pth_{name}"] = lagrangian_power(th, L, n)[1]
        arr[f"Pdd_{name}"] = lagrangian_power(ic["mesh"]["delta"], L, n)[1]
        arr[f"pred_{name}"] = realised_average(
            th0, L, lambda kk, s=setting, m=mode, g=gfn: fig4_factor(kk, s, m, g, z, dz)**2) - 1
        st[name] = {"c_minus": ic["meta"]["c_minus"], "c_ini": ic["meta"]["c_ini"],
                    "c_plus": ic["meta"]["c_plus"],
                    "sigma8": ic["meta"].get("sigma8_targets", {}).get("sigma8"),
                    "positions_equal_ref": bool(np.array_equal(ic["x"], ref["x"]))}
        del ic, th
        log("fig4", name)
    # back-scaling (2LPTic "inc D_1"): the z = 0 spectrum scaled back with D_1
    D = lambda zz: float(gi.growth(a_of(zz), P))                     # noqa: E731
    pk_b = lambda kk: sp.linear_power(kk, 0.0, P)*(D(z)/D(0.0))**2   # noqa: E731
    db = rf.gaussian_field(n, L, pk_b, SEED, zero_nyquist=True)
    st["backscaled_max|delta_b - delta|/max|delta|"] = float(
        np.abs(db - ref["mesh"]["delta"]).max()/np.abs(ref["mesh"]["delta"]).max())
    arr["Pdd_backscaled"] = lagrangian_power(db, L, n)[1]
    np.savez(os.path.join(WORK, f"fig4_n{n}.npz"), **arr)
    jdump(st, os.path.join(WORK, f"fig4_n{n}.json"))
    log("fig4 saved")


# ---------------------------------------------------------------------------------------
# stage: t0prec (single-precision emulations of the FD velocity, 4 Gpc/h)
# ---------------------------------------------------------------------------------------
def zeldovich32(delta, L):
    """Zel'dovich displacement with every step in single precision (scipy.fft on float32
    and complex64), as in a single-precision IC code; same operator as
    random_field.zeldovich."""
    import scipy.fft as sfft
    n = delta.shape[0]
    tor = cid.Torus(n, L)
    F = sfft.rfftn(delta.astype(np.float32))
    k2 = tor.k2.astype(np.float32)
    k2[0, 0, 0] = 1.0
    G = F/k2
    G[0, 0, 0] = 0.0
    return [sfft.irfftn((1j*kd.astype(np.float32))*G, s=(n,)*3) for kd in tor.kd]


def table_pk(pk, digits=7, kmin=1e-5, kmax=1e2, npts=1000):
    """P(k) through a table: npts log-spaced k, values rounded to `digits` significant
    digits, linear interpolation in (log k, log P)."""
    kt = np.logspace(np.log10(kmin), np.log10(kmax), npts)
    pt = np.array([float(f"{v:.{digits - 1}e}") for v in pk(kt)])
    lk, lp = np.log(kt), np.log(pt)
    return lambda k: np.exp(np.interp(np.log(k), lk, lp))


def stage_t0prec(args):
    """Delta P/P of FD against two-step with chi(z+-) (a) stored in float32 after a
    double-precision computation (as make_ic(fd_dtype=float32)) and (b) computed entirely
    in float32 (field, FFTs, difference), for the notes' inference that the paper's
    Delta z = 0.05 scatter is single-precision round-off (notes:468-469)."""
    n, L = args.n, 4000.0
    arr, st = {}, {}
    for z in ZINI:
        a = a_of(z)
        H = float(gi.hubble_kms(a, P))
        ref = gi.make_ic(n, L, z, "newtonian", "two-step", seed=SEED)
        k, p2, _ = lagrangian_power(divergence(ref["mesh"]["u"], L), L, n)
        arr["k"] = k
        # reference for (c): the two-step velocity from the tabulated z_ini spectrum (the
        # default 2LPTic reads the same kind of table, so the interpolation error cancels)
        _, x0 = gi.realise(n, L, table_pk(lambda kk: gi.power_S(kk, z, P)), SEED)
        f0 = float(gi.growth_rate(a, P))
        p2t = lagrangian_power(divergence([np.sqrt(a)*H*f0*c for c in x0], L), L, n)[1]
        del x0
        for dz in (0.25, 0.05):
            c2 = fd_factor(z, dz)**2 - 1
            dm = rf.gaussian_field(n, L, lambda kk: gi.power_S_scaled(kk, z - dz, z, P),
                                   SEED, zero_nyquist=True)
            dp = rf.gaussian_field(n, L, lambda kk: gi.power_S_scaled(kk, z + dz, z, P),
                                   SEED, zero_nyquist=True)
            cm, cp = zeldovich32(dm, L), zeldovich32(dp, L)
            fac = np.float32(np.sqrt(a)*H/a/(2.0*dz))
            u32 = [(fac*(cm[i] - cp[i])).astype(np.float64) for i in range(3)]
            r = lagrangian_power(divergence(u32, L), L, n)[1]/p2 - 1 - c2
            arr[f"full32_z{z:g}_dz{dz:g}"] = r
            ic = gi.make_ic(n, L, z, "newtonian", "fd", dz=dz, seed=SEED, fd_dtype=np.float32)
            rs = lagrangian_power(divergence(ic["mesh"]["u"], L), L, n)[1]/p2 - 1 - c2
            arr[f"store32_z{z:g}_dz{dz:g}"] = rs
            # (c) double precision, but P(k; z+-) read from tables printed with 7
            # significant digits ("%.6e", as CAMB's E15.6 output) and interpolated linearly
            # in (log k, log P) like 2LPTic's tabulated spectrum
            tm = table_pk(lambda kk: gi.power_S_scaled(kk, z - dz, z, P))
            tp = table_pk(lambda kk: gi.power_S_scaled(kk, z + dz, z, P))
            _, xm = gi.realise(n, L, tm, SEED)
            _, xp = gi.realise(n, L, tp, SEED)
            fac64 = np.sqrt(a)*H/a/(2.0*dz)
            ut = [fac64*(xm[i] - xp[i]) for i in range(3)]
            rt = lagrangian_power(divergence(ut, L), L, n)[1]/p2t - 1 - c2
            arr[f"table7_z{z:g}_dz{dz:g}"] = rt
            del xm, xp, ut
            e = np.stack([c.ravel() for c in u32], 1) - fd_factor(z, dz)*ref["u"]
            st[f"z{z:g}_dz{dz:g}"] = {
                "full32_rms": float(np.sqrt(np.mean(r**2))),
                "full32_mean": float(r.mean()), "full32_max": float(np.abs(r).max()),
                "full32_rms_first10": float(np.sqrt(np.mean(r[:10]**2))),
                "table7_rms": float(np.sqrt(np.mean(rt**2))),
                "table7_mean": float(rt.mean()), "table7_max": float(np.abs(rt).max()),
                "store32_rms": float(np.sqrt(np.mean(rs**2))),
                "store32_max": float(np.abs(rs).max()),
                "full32_particle_rel_err_rms": float(np.sqrt((e**2).sum(1).mean()
                                                             / (ref["u"]**2).sum(1).mean()))}
            log("t0prec", z, dz, st[f"z{z:g}_dz{dz:g}"])
            del ic, cm, cp, u32
    np.savez(os.path.join(WORK, f"t0prec_n{n}.npz"), **arr)
    jdump(st, os.path.join(WORK, f"t0prec_n{n}.json"))


# ---------------------------------------------------------------------------------------
# stage: estimator (Eulerian deposit of lattice ICs against the mesh field)
# ---------------------------------------------------------------------------------------
def stage_estimator(args):
    n = args.n
    out = {}
    for L in BOXES:
        for z in (49.0, 99.0):
            ic = gi.make_ic(n, L, z, "newtonian", "two-step", seed=SEED)
            d = ic["mesh"]["delta"]
            k, pm, _ = lagrangian_power(d, L, n)
            th = divergence(ic["mesh"]["u"], L)
            _, ptm, _ = lagrangian_power(th, L, n)
            q, chi = ic["q"], np.stack([c.ravel() for c in ic["mesh"]["chi"]], 1)
            row = {"k": k, "k_Ny": np.pi*n/L}
            for amp in (1.0, 1e-4):
                x = (q + amp*chi) % L
                for shape, p in (("cic", 1), ("tsc", 2), ("pcs", 3)):
                    for s in (1, 2):
                        if amp != 1.0 and z != 49.0:
                            continue
                        dd, rho = eulerian_density(x, n, L, shape, s)
                        _, pd, _ = measure_eulerian(dd/amp, L, n, p)
                        key = f"{shape}_s{s}_amp{amp:g}"
                        row[f"dens_{key}"] = pd/pm
                        if amp == 1.0 and shape in ("tsc", "pcs"):
                            for wt in (False, True):
                                v = eulerian_velocity(x, ic["u"], n, L, rho, shape, s, wt)
                                _, pv, _ = measure_eulerian(divergence(v, L), L, n, p)
                                row[f"vel_{key}_{'w' if wt else 'm'}"] = pv/ptm
                        if amp == 1.0 and shape != "cic":
                            rd, rv = deposit_response(n, L, p, s, field=d)
                            row[f"pred_dens_{shape}_s{s}"] = rd
                            rv_t = deposit_response(n, L, p, s, field=th)[1]
                            row[f"pred_vel_{shape}_s{s}"] = rv_t
                        log(f"estimator L={L:g} z={z:g} amp={amp:g} {shape} s={s}")
            out[f"L{L:g}_z{z:g}"] = row
    np.savez(os.path.join(WORK, f"estimator_n{n}.npz"),
             **{f"{a}|{b}": np.asarray(v) for a, r in out.items() for b, v in r.items()})
    summ = {}
    for key, r in out.items():
        kk, kny = np.asarray(r["k"]), r["k_Ny"]
        s = {}
        for name, v in r.items():
            if not (name.startswith("dens_") or name.startswith("vel_")
                    or name.startswith("pred_")):
                continue
            v = np.asarray(v)
            bad = np.abs(v - 1) > 0.01
            s[name] = {"k_1pct_over_kNy": float(kk[np.argmax(bad)]/kny) if bad.any() else 1.0,
                       "at_kNy/2": float(v[np.argmin(np.abs(kk - kny/2))]),
                       "at_last": float(v[-1])}
        summ[key] = s
    jdump(summ, os.path.join(WORK, f"estimator_n{n}.json"))
    for key, s in summ.items():
        print(key)
        for name, v in s.items():
            print(f"   {name:28s} 1% at k/kNy = {v['k_1pct_over_kNy']:.3f}   "
                  f"kNy/2: {v['at_kNy/2']:.4f}   last: {v['at_last']:.4f}")


# ---------------------------------------------------------------------------------------
# stage: report (summaries, figures, gramses_tests.json)
# ---------------------------------------------------------------------------------------
def _load(path):
    return json.load(open(path)) if os.path.exists(path) else None


def _first_bad(k, v, kny, tol=0.01):
    bad = np.abs(np.asarray(v) - 1.0) > tol
    return float(k[np.argmax(bad)]/kny) if bad.any() else 1.0


def summarise_ics(n):
    out = {}
    for L in BOXES:
        for z in ZINI:
            tag = f"L{L:g}_z{z:g}_n{n}"
            pz = os.path.join(WORK, f"ics_{tag}.npz")
            if not os.path.exists(pz):
                continue
            d = dict(np.load(pz))
            st = _load(os.path.join(WORK, f"ics_{tag}.json"))
            k, kny = d["k"], np.pi*n/L
            s = {"stats": st}
            # T0: FD against two-step
            t0 = {}
            for dz in DZS:
                c2 = fd_factor(z, dz)**2 - 1
                r64 = d[f"Pth_fdN64_dz{dz:g}_L"]/d["Pth_2s_L"] - 1
                r32 = d[f"Pth_fdN32_dz{dz:g}_L"]/d["Pth_2s_L"] - 1
                rC = d[f"Pth_fdC_dz{dz:g}_L"]/d["Pth_2s_L"] - 1
                t0[f"{dz:g}"] = {
                    "expected": c2, "approx": 2*dz*dz/(1 + z)**2,
                    "mean_double": float(r64.mean()),
                    "max|double - expected|": float(np.abs(r64 - c2).max()),
                    "mean_single": float(r32.mean()),
                    "rms_single_minus_expected": float(np.sqrt(np.mean((r32 - c2)**2))),
                    "max|single - expected|": float(np.abs(r32 - c2).max()),
                    "rms_single_minus_expected_k<kNy/2": float(np.sqrt(np.mean(
                        (r32 - c2)[k < kny/2]**2))),
                    "mean_CMC_upper_vs_two_step": float(rC.mean()),
                    "max|CMC - expected|": float(np.abs(rC - c2).max())}
            dzm = main_dz(z)
            rE = d["Pth_fdN_E"]/d["Pth_2s_E"] - 1
            t0["eulerian_main_dz"] = {"dz": dzm, "mean": float(rE.mean()),
                                      "max|E - expected|": float(np.abs(
                                          rE - (fd_factor(z, dzm)**2 - 1)).max())}
            s["t0"] = t0
            # Fig. 2
            rm = d["P_dp_E"]/d["P_dS_E"]
            rr = d["ratio_pS_realised"]
            ens = d["lin_p"]/d["lin_S"]
            bins = [r[0] for r in PAPER["fig2"][(L, int(z))]]
            s["fig2"] = {
                "bins": bins, "k": [float(k[j - 1]) for j in bins],
                "measured": [float(rm[j - 1]) for j in bins],
                "realised_linear": [float(rr[j - 1]) for j in bins],
                "ensemble_linear": [float(ens[j - 1]) for j in bins],
                "paper_measured": [r[1] for r in PAPER["fig2"][(L, int(z))]],
                "paper_linear_centre": [r[2] for r in PAPER["fig2"][(L, int(z))]],
                "max|meas/realised - 1|_k<kNy/2": float(np.abs(rm/rr - 1)[k < kny/2].max()),
                "max|meas/realised - 1|_all": float(np.abs(rm/rr - 1).max()),
                "mean_ratio_last_quarter": float(rm[k > 0.75*kny].mean()),
                "S_dep/mesh_1pct_at_k/kNy": _first_bad(k, d["P_dS_E"]/d["P_dS_mesh"], kny),
                "p_dep/mesh_1pct_at_k/kNy": _first_bad(k, d["P_dp_E"]/d["P_dp_mesh"], kny),
                "S_dep/mesh_at_kNy/2": float((d["P_dS_E"]/d["P_dS_mesh"])[
                    np.argmin(np.abs(k - kny/2))]),
                "S_dep/mesh_last": float(d["P_dS_E"][-1]/d["P_dS_mesh"][-1]),
                "p_dep/mesh_last": float(d["P_dp_E"][-1]/d["P_dp_mesh"][-1]),
                "pred_response_at_kNy/2": float(d["resp_dens"][np.argmin(np.abs(k - kny/2))]),
                "pred_response_last": float(d["resp_dens"][-1]),
                "chi2_mesh_S_vs_linear": float(np.mean(((d["P_dS_mesh"] - d["lin_S"])
                                                        / d["sig_S"])**2)),
                "chi2_mesh_S_vs_linear_k<0.1": float(np.mean(((d["P_dS_mesh"] - d["lin_S"])
                                                              / d["sig_S"])[k < 0.1]**2)),
                "nbins": int(len(k))}
            # Fig. 3
            c2m = fd_factor(z, dzm)**2
            lowE = d["Pth_lowC_E"]/d["Pth_2s_E"]
            lowL = d[f"Pth_lowC_dz{dzm:g}_L"]/d["Pth_2s_L"]
            real = d["lowerN_realised"]*c2m
            ensl = d["lin_thL"]/d["lin_thN"]*c2m
            sel = k > 0.01
            s["fig3"] = {
                "first_bin_lower/2s_eulerian": float(lowE[0]),
                "first_bin_lower/2s_lagrangian": float(lowL[0]),
                "first_bin_realised_expectation": float(real[0]),
                "first_bin_ensemble": float(ensl[0]),
                "max|lagr/realised - 1|": float(np.abs(lowL/real - 1).max()),
                "max|euler/realised - 1|_k<kNy/2": float(np.abs(lowE/real - 1)[k < kny/2].max()),
                "mean(lower/N - 1)_k>0.01_eulerian": float(np.mean(lowE[sel] - 1)),
                "mean(lower/N - 1)_k>0.01_expected": float(np.mean(real[sel] - 1)),
                "theta_E/L_1pct_at_k/kNy": _first_bad(k, d["Pth_2s_E"]/d["Pth_2s_L"], kny),
                "theta_E/L_at_kNy/2": float((d["Pth_2s_E"]/d["Pth_2s_L"])[
                    np.argmin(np.abs(k - kny/2))]),
                "theta_E/L_last": float(d["Pth_2s_E"][-1]/d["Pth_2s_L"][-1]),
                "pred_vel_response_last": float(d["resp_vel"][-1]),
                "naive_CMC_first_bin_over_2s": float(d["Pth_naiveC_L"][0]/d["Pth_2s_L"][0]),
                "theta_mesh_vs_linear_chi2": float(np.mean(((d["Pth_2s_L"] - d["lin_thN"])
                                                            / d["sig_thN"])**2))}
            out[f"L{L:g}_z{z:g}"] = s
    return out


def summarise_fig4(n):
    pz = os.path.join(WORK, f"fig4_n{n}.npz")
    if not os.path.exists(pz):
        return None
    d = dict(np.load(pz))
    st = _load(os.path.join(WORK, f"fig4_n{n}.json"))
    k = d["k"]
    out = {"stats": st, "k_first3": k[:3].tolist()}
    for name, *_ in fig4_variants():
        r = d[f"Pth_{name}"]/d["Pth_ref"] - 1
        pr = d[f"pred_{name}"]
        out[name] = {"measured_first3": r[:3].tolist(),
                     "measured_plateau_k>0.05": float(r[k > 0.05].mean()),
                     "predicted_first3": pr[:3].tolist(),
                     "predicted_plateau_k>0.05": float(pr[k > 0.05].mean()),
                     "max|meas - pred|": float(np.abs(r - pr).max()),
                     "dPdd_max_vs_same_setting": float(np.abs(
                         d[f"Pdd_{name}"]/(d["Pdd_ref"] if name.endswith("_N")
                                           else d["Pdd_fd_lin_s8_C"]) - 1).max())}
    out["backscaled_dPdd_max"] = float(np.abs(d["Pdd_backscaled"]/d["Pdd_ref"] - 1).max())
    return out


def stage_report(args):
    n = args.n
    rep = {"settings": {"params": P, "seed": SEED, "n": n, "boxes": BOXES, "z_ini": ZINI,
                        "dz": DZS, "shape": SHAPE, "mesh_factor": MESH_FACTOR,
                        "vel_weighted": VEL_WEIGHTED,
                        "bins": "width k_f, edges at integer multiples of k_f, to k_Ny"}}
    rep["expected"] = _load(os.path.join(WORK, "expect.json"))
    cl = _load(os.path.join(WORK, "closed.json"))
    if cl:
        rep["closed_form_checks"] = cl["checks"]
        rep["fig1"] = cl["fig1"]
    est = _load(os.path.join(WORK, "estimator_n128.json"))
    rep["estimator_n128"] = est
    rep["ics"] = summarise_ics(n)
    rep["fig4"] = summarise_fig4(n)
    rep["t0_precision"] = _load(os.path.join(WORK, f"t0prec_n{n}.json"))
    jdump(rep, JSON_OUT)
    log("wrote", JSON_OUT)
    fig_t0(n)
    fig_pdd(n)
    fig_ptt(n)
    fig_fig4(n)
    if os.path.exists(os.path.join(WORK, "estimator_n128.npz")):
        fig_estimator(128)


# ---- figures --------------------------------------------------------------------------
def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    return plt, fs


DZ_COL = {1.0: "#FF7F0E", 0.5: "#C2185B", 0.25: "#009925", 0.05: "#00ACC1"}


def fig_t0(n):
    plt, fs = _style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.6))
    ax1 = fs.inch_axes(fig, 0.8, 2.45, 3.4, 3.0)
    ax3 = fs.inch_axes(fig, 0.8, 0.45, 3.4, 1.75)
    ax2 = fs.inch_axes(fig, 5.05, 0.45, 2.8, 5.0)
    L = 4000.0
    for z, mk in ((99.0, "o"), (49.0, "s")):
        pz = os.path.join(WORK, f"ics_L{L:g}_z{z:g}_n{n}.npz")
        if not os.path.exists(pz):
            continue
        d = dict(np.load(pz))
        k = d["k"]
        for dz in DZS:
            c2 = fd_factor(z, dz)**2 - 1
            r = d[f"Pth_fdN64_dz{dz:g}_L"]/d["Pth_2s_L"] - 1
            ax1.loglog(k, r, mk, ms=2.5, color=DZ_COL[dz], mfc=DZ_COL[dz] if z == 99 else
                       "none", mew=0.7)
            ax1.axhline(c2, color=DZ_COL[dz], lw=1.0, ls="--")
    for dz in DZS:
        ax1.plot([], [], "s", color=DZ_COL[dz], ms=4, label=fr"$\Delta z={dz:g}$")
    ax1.plot([], [], "o", color="grey", ms=4, label=r"$z_{\rm ini}=99$")
    ax1.plot([], [], "s", color="grey", mfc="none", ms=4, label=r"$z_{\rm ini}=49$")
    ax1.plot([], [], ls="--", color="grey", lw=1.0, label=r"$c^2-1$")
    ax1.legend(loc="upper center", ncol=3, fontsize=7.5)
    ax1.set_ylim(1e-7, 1e-1)
    ax1.set_ylabel(r"$\Delta P_\theta/P_\theta$ (FD $-$ two-step)")
    ax1.set_xticklabels([])
    ax1.text(0.03, 0.03, r"4 $h^{-1}$Gpc, $256^3$, double precision", transform=ax1.transAxes,
             fontsize=8)
    # precision emulations at dz = 0.05 (stage t0prec)
    pp = os.path.join(WORK, f"t0prec_n{n}.npz")
    if os.path.exists(pp):
        e = dict(np.load(pp))
        k = e["k"]
        for z, mfc in ((99.0, None), (49.0, "none")):
            for key, col, lab in (("table7", fs.PAL["red"], "P(k) tables, 7 digits"),
                                  ("full32", fs.PAL["green"], "float32 FFTs"),
                                  ("store32", "grey", "float32 storage of $\\chi$")):
                ax3.semilogx(k, 1e4*e[f"{key}_z{z:g}_dz0.05"], "o", ms=2.3, color=col,
                             mfc=col if mfc is None else "none", mew=0.6,
                             label=lab if z == 99.0 else None)
    for p_ in (3.5, -3.5):
        ax3.axhline(p_, **fs.MASK_LINE)
    ax3.axhline(0.0, **fs.THIN)
    ax3.set_ylim(-8.5, 8.5)
    ax3.set_ylabel(r"$[\Delta P/P-(c^2-1)]/10^{-4}$", fontsize=9)
    ax3.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
    ax3.legend(loc="lower left", fontsize=7, ncol=3)
    ax3.text(0.98, 0.95, r"$\Delta z=0.05$; filled $z_{\rm ini}=99$, open 49; "
             "grey lines: paper's scatter", transform=ax3.transAxes, ha="right", va="top",
             fontsize=7)
    for ax in (ax1, ax3):
        ax.set_xlim(1.5e-3, 0.21)
    # quadratic law
    xx = np.logspace(-4, -1.5, 50)
    ax2.loglog(xx, 2*xx*xx, **fs.GUIDE, label=r"$2(\Delta z)^2/(1+z)^2$")
    for (L, z), mk in (((4000.0, 99.0), "o"), ((4000.0, 49.0), "s"),
                       ((256.0, 99.0), "^"), ((256.0, 49.0), "v")):
        pz = os.path.join(WORK, f"ics_L{L:g}_z{z:g}_n{n}.npz")
        if not os.path.exists(pz):
            continue
        d = dict(np.load(pz))
        xs = [dz/(1 + z) for dz in DZS]
        ys = [float(np.mean(d[f"Pth_fdN64_dz{dz:g}_L"]/d["Pth_2s_L"] - 1)) for dz in DZS]
        ax2.loglog(xs, ys, mk, color=fs.PAL["red"], mfc="none" if L == 256.0 else
                   fs.PAL["red"], ms=6, label=f"ours, {L/1000 if L > 1000 else L:g} "
                   f"{'Gpc' if L > 1000 else 'Mpc'}/$h$, $z={z:g}$")
    for z, mk in ((99, "D"), (49, "p")):
        xs = [dz/(1 + z) for dz in DZS if PAPER["fig3_dP"][z][dz] > 0]
        ys = [PAPER["fig3_dP"][z][dz] for dz in DZS if PAPER["fig3_dP"][z][dz] > 0]
        ax2.loglog(xs, ys, mk, color=fs.PAL["blue"], mfc="none", ms=8, mew=1.2,
                   label=f"paper, $z={z}$")
    ax2.set_xlabel(r"$\Delta z/(1+z_{\rm ini})$", labelpad=-2)
    ax2.set_ylabel(r"mean $\Delta P_\theta/P_\theta$ over $k$")
    ax2.legend(loc="upper left", fontsize=8)
    ax2.set_xlim(3e-4, 3e-2)
    ax2.set_ylim(1.5e-7, 3e-3)
    fs.save(fig, os.path.join(FIGDIR, "gramses_t0_fd"))
    plt.close(fig)
    log("wrote gramses_t0_fd")


def _panel_grid(fs, plt, heights, height_total):
    """2 x 2 panels (columns: boxes, rows: z), each a stack of strips of the given
    heights (inches). Returns fig, axes[row][col] = list of strip axes (top first)."""
    fig = plt.figure(figsize=(fs.FULL_WIDTH, height_total))
    W, x0s = 3.15, (0.78, 4.75)
    block = sum(heights)
    gap = 0.55
    y_top = height_total - 0.12
    axes = [[None, None], [None, None]]
    for r in range(2):
        ytop = y_top - r*(block + gap)
        for c in range(2):
            strips, y = [], ytop
            for h in heights:
                y -= h
                strips.append(fs.inch_axes(fig, x0s[c], y, W, h))
            axes[r][c] = strips
    return fig, axes


def _minor_labels(ax):
    """Label minor ticks of a log axis spanning less than about two decades."""
    from matplotlib.ticker import LogFormatterSciNotation
    ax.yaxis.set_minor_formatter(LogFormatterSciNotation(labelOnlyBase=False,
                                                         minor_thresholds=(2, 0.5)))
    ax.tick_params(axis="y", which="minor", labelsize=8)


def _box_label(L):
    return "4 $h^{-1}$Gpc" if L > 1000 else "256 $h^{-1}$Mpc"


def fig_pdd(n):
    plt, fs = _style()
    fig, axes = _panel_grid(fs, plt, (1.75, 0.95, 0.8), 8.4)
    for c, L in enumerate(BOXES):
        for r, z in enumerate(ZINI):
            pz = os.path.join(WORK, f"ics_L{L:g}_z{z:g}_n{n}.npz")
            if not os.path.exists(pz):
                continue
            d = dict(np.load(pz))
            k, kny = d["k"], np.pi*n/L
            kl = np.logspace(np.log10(k[0]*0.9), np.log10(kny*1.05), 300)
            a1, a2, a3 = axes[r][c]
            w = k**1.5
            a1.loglog(kl, kl**1.5*gi.power_S(kl, z, P), **fs.GUIDE, label="linear S")
            a1.loglog(kl, kl**1.5*gi.power_gauge(kl, z, P, "p"), color="k",
                      label="linear CMC")
            a1.loglog(k, w*d["P_dS_E"], "^", ms=3, color=fs.PAL["orange"], label="ICs, S")
            a1.loglog(k, w*d["P_dp_E"], "o", ms=3, mfc="none", color=fs.PAL["red"], mew=0.8,
                      label="ICs, CMC")
            a1.text(0.03, 0.94 if L > 1000 else 0.06,
                    f"{_box_label(L)}, $z_{{\\rm ini}}={z:g}$", transform=a1.transAxes,
                    fontsize=9, va="top" if L > 1000 else "bottom")
            if r == 0:
                a1.legend(loc="lower right" if L > 1000 else "lower left", fontsize=8,
                          ncol=2, bbox_to_anchor=None if L > 1000 else (0.0, 0.1))
            a1.set_ylabel(r"$k^{1.5}P_{\delta\delta}$")
            _minor_labels(a1)
            # ratio
            ens = d["lin_p"]/d["lin_S"]
            a2.plot(k, d["P_dp_E"]/d["P_dS_E"], "o", ms=3, mfc="none", color=fs.PAL["red"],
                    mew=0.8, label="ICs, CMC/S")
            a2.plot(k, d["ratio_pS_realised"], "-", color="grey", lw=1.0,
                    label="linear, realised modes")
            a2.plot(kl, gi.power_ratio_pS(kl, a_of(z), P), color="k", lw=1.0, ls="--",
                    label="linear, closed form")
            pp = PAPER["fig2"][(L, int(z))]
            a2.plot([k[j - 1] for j, _, _ in pp], [m for _, m, _ in pp], "s", mfc="none",
                    color=fs.PAL["blue"], ms=6, mew=1.0, label="paper")
            a2.axhline(1.0, color="grey", ls=":", lw=1.0)
            a2.set_ylabel(r"$P^{\rm CMC}/P^{\rm S}$")
            if L > 1000:
                a2.set_yscale("log")
                a2.set_ylim(0.8, 80)
            else:
                a2.set_ylim(0.995, 1.09 if z == 99 else 1.045)
            if r == 0:
                a2.legend(loc="upper right", fontsize=7, ncol=2)
            # estimator: deposit / mesh field
            a3.plot(k, d["P_dS_E"]/d["P_dS_mesh"], "^", ms=2.5, color=fs.PAL["orange"])
            a3.plot(k, d["P_dp_E"]/d["P_dp_mesh"], "o", ms=2.5, mfc="none",
                    color=fs.PAL["red"], mew=0.7)
            a3.plot(k, d["resp_dens"], color="k", lw=1.0, ls="--")
            fs.band(a3, [k[0]*0.5, kny*2], [0.99, 0.99], [1.01, 1.01], "grey", alpha=0.15)
            a3.axhline(1.0, **fs.THIN)
            a3.set_ylim(0.96, 1.08)
            a3.set_ylabel("deposit/mesh", fontsize=9)
            a3.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
            for ax in (a1, a2, a3):
                ax.set_xscale("log")
                ax.set_xlim(k[0]*0.85, kny*1.05)
            for ax in (a1, a2):
                ax.set_xticklabels([])
    fs.save(fig, os.path.join(FIGDIR, "gramses_fig2_pdd"))
    plt.close(fig)
    log("wrote gramses_fig2_pdd")


def fig_ptt(n):
    plt, fs = _style()
    fig, axes = _panel_grid(fs, plt, (1.75, 0.95, 0.8), 8.4)
    for c, L in enumerate(BOXES):
        for r, z in enumerate(ZINI):
            pz = os.path.join(WORK, f"ics_L{L:g}_z{z:g}_n{n}.npz")
            if not os.path.exists(pz):
                continue
            d = dict(np.load(pz))
            k, kny = d["k"], np.pi*n/L
            dzm = main_dz(z)
            kl = np.logspace(np.log10(k[0]*0.9), np.log10(kny*1.05), 300)
            a1, a2, a3 = axes[r][c]
            w = k**1.5
            a1.loglog(kl, kl**1.5*gi.theta_power_N(kl, z, P), **fs.GUIDE, label="linear N")
            a1.loglog(kl, kl**1.5*gi.theta_power_lower(kl, z, P), color="k",
                      label="linear CMC, lower")
            a1.loglog(k, w*d["Pth_2s_E"], "*", ms=6, mfc="none", mew=0.8,
                      color=fs.PAL["orange"], label="two-step (N)")
            a1.loglog(k, w*d["Pth_fdN_E"], "o", ms=1.8, color=DZ_COL[dzm],
                      label=fr"FD (N), $\Delta z={dzm:g}$")
            a1.loglog(k, w*d["Pth_lowC_E"], "^", ms=3, mfc="none", color=fs.PAL["red"],
                      mew=0.8, label=r"CMC, $a^{-2}\partial_iu_i$")
            a1.text(0.03, 0.94 if L > 1000 else 0.06,
                    f"{_box_label(L)}, $z_{{\\rm ini}}={z:g}$", transform=a1.transAxes,
                    fontsize=9, va="top" if L > 1000 else "bottom")
            if r == 0 and c == 0:
                a1.legend(loc="lower right", fontsize=7, ncol=2)
            a1.set_ylabel(r"$k^{1.5}P_{\theta\theta}$")
            _minor_labels(a1)
            # Delta P_N / P_N for each dz (Lagrangian) and the Eulerian one for dzm
            for dz in DZS:
                rr = d[f"Pth_fdN64_dz{dz:g}_L"]/d["Pth_2s_L"] - 1
                a2.plot(k, rr, "o", ms=2.2, color=DZ_COL[dz], label=fr"$\Delta z={dz:g}$")
                a2.axhline(fd_factor(z, dz)**2 - 1, color=DZ_COL[dz], lw=0.8, ls="--")
            rE = d["Pth_fdN_E"]/d["Pth_2s_E"] - 1
            a2.plot(k, rE, "x", ms=3.5, color="k", mew=0.7, label="Eulerian")
            a2.set_yscale("log")
            a2.set_ylim(2e-7, 0.08)
            a2.set_ylabel(r"$\Delta P_{\rm N}/P_{\rm N}$")
            if r == 0:
                a2.legend(loc="upper center", fontsize=7, ncol=5, handletextpad=0.1,
                          columnspacing=0.6)
            # lower-index CMC over N
            c2m = fd_factor(z, dzm)**2
            a3.plot(k, d["Pth_lowC_E"]/d["Pth_2s_E"], "^", ms=3, mfc="none",
                    color=fs.PAL["red"], mew=0.8)
            a3.plot(k, d["lowerN_realised"]*c2m, "-", color="grey", lw=1.0)
            a3.plot(kl, gi.theta_lower_T(kl, a_of(z), P)**2, color="k", lw=1.0, ls="--")
            if L > 1000:
                a3.plot([k[0]], [PAPER["fig3_lower_first"][int(z)]], "s", mfc="none",
                        color=fs.PAL["blue"], ms=6, mew=1.0)
                a3.set_yscale("log")
                a3.set_ylim(0.03, 1.5)
            else:
                a3.set_ylim(0.95, 1.008)
            a3.axhline(1.0, color="grey", ls=":", lw=1.0)
            a3.set_ylabel(r"CMC/N", fontsize=9)
            a3.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
            for ax in (a1, a2, a3):
                ax.set_xscale("log")
                ax.set_xlim(k[0]*0.85, kny*1.05)
            for ax in (a1, a2):
                ax.set_xticklabels([])
    fs.save(fig, os.path.join(FIGDIR, "gramses_fig3_ptt"))
    plt.close(fig)
    log("wrote gramses_fig3_ptt")


FIG4_STYLE = {"fd_lin_s8_N": ("o", "#00ACC1", "FD (N), $\\sigma_8$ corrected"),
              "fd_lin_s8_C": ("s", "#009925", "FD (CMC), $\\sigma_8$ corrected"),
              "fd_none_s8_C": ("+", "k", "FD (CMC), no renormalisation"),
              "fd_D1scaled_s8_C": ("D", "#C2185B", "FD (CMC), $\\sigma_8^p\\propto D_1$"),
              "fd_def_s8_N": ("o", "#FF7F0E", "FD (N), def. $\\sigma_8$ model"),
              "fd_def_s8_C": ("*", "#EA4335", "FD (CMC), def. $\\sigma_8$ model")}


def fig_fig4(n):
    pz = os.path.join(WORK, f"fig4_n{n}.npz")
    if not os.path.exists(pz):
        return
    plt, fs = _style()
    d = dict(np.load(pz))
    k = d["k"]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.9))
    ax1 = fs.inch_axes(fig, 0.85, 3.05, 6.95, 1.75)
    ax2 = fs.inch_axes(fig, 0.85, 0.45, 6.95, 2.55)
    w = k**1.5
    ax1.loglog(k, w*d["Pth_ref"], "v", ms=3, color="#8D6E63", label="two-step (N), reference")
    for name, (mk, col, lab) in FIG4_STYLE.items():
        ax1.loglog(k, w*d[f"Pth_{name}"], mk, ms=2.5, color=col, mfc="none", mew=0.7)
        ax2.semilogx(k, d[f"Pth_{name}"]/d["Pth_ref"] - 1, mk, ms=3.2, color=col,
                     mfc="none", mew=0.8, label=lab)
        ax2.semilogx(k, d[f"pred_{name}"], "-", color=col, lw=0.9)
    kl = np.logspace(-3, np.log10(0.21), 200)
    ax1.loglog(kl, kl**1.5*gi.theta_power_N(kl, 49.0, P), **fs.GUIDE, label="linear N")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.set_ylabel(r"$k^{1.5}P_{\theta\theta}$")
    ax1.set_xticklabels([])
    kp = list(k[:3]) + [0.1]
    pmap = {"fd_def_s8_N": ("o", "paper: def $\\sigma_8$ (N)"),
            "fd_def_s8_C": ("*", "paper: def $\\sigma_8$ (CMC)")}
    for key, (mk, lab) in pmap.items():
        ax2.semilogx(kp, PAPER["fig4"][key], mk, ms=8, mfc="none", color=fs.PAL["blue"],
                     mew=1.1, label=lab)
    for key, mk, lab in (("fd_inc_etadot_N", "d", "paper: inc $\\dot\\eta$ (N)"),
                         ("fd_inc_etadot_C", "s", "paper: inc $\\dot\\eta$ (CMC)"),
                         ("backscaled_N", "v", "paper: back-scaled")):
        ax2.semilogx(kp, PAPER["fig4"][key], mk, ms=6, mfc="none", color="grey", mew=1.0,
                     label=lab + " (not made)")
    ax2.axhline(0.0, **fs.THIN)
    ax2.set_ylim(-0.095, 0.065)
    ax2.set_ylabel(r"$\Delta P_{\theta\theta}/P^{\rm N}_{\theta\theta}$")
    ax2.set_xlabel(r"$k$ [$h$ Mpc$^{-1}$]", labelpad=-2)
    ax2.legend(loc="lower right", fontsize=7, ncol=3)
    ax2.text(0.98, 0.95, r"4 $h^{-1}$Gpc, $256^3$, $z_{\rm ini}=49$, $\Delta z=0.5$; "
             "lines: predictions", transform=ax2.transAxes, va="top", ha="right", fontsize=8)
    for ax in (ax1, ax2):
        ax.set_xlim(1.4e-3, 0.21)
    fs.save(fig, os.path.join(FIGDIR, "gramses_fig4_sigma8"))
    plt.close(fig)
    log("wrote gramses_fig4_sigma8")


def fig_estimator(n):
    plt, fs = _style()
    from matplotlib.lines import Line2D
    raw = dict(np.load(os.path.join(WORK, f"estimator_n{n}.npz")))
    get = lambda key, name: raw[f"{key}|{name}"]                     # noqa: E731
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.7))
    cols = {("tsc", 1): fs.PAL["yellow"], ("tsc", 2): fs.PAL["green"],
            ("pcs", 1): fs.PAL["blue"], ("pcs", 2): fs.PAL["red"], ("cic", 2): "grey",
            ("cic", 1): "#8D6E63"}
    for c, L in enumerate(BOXES):
        key = f"L{L:g}_z49"
        k, kny = get(key, "k"), float(get(key, "k_Ny"))
        x = k/kny
        a1 = fs.inch_axes(fig, 0.8 + c*3.55, 2.95, 3.4, 2.4)
        a2 = fs.inch_axes(fig, 0.8 + c*3.55, 0.45, 3.4, 2.4)
        for shape in ("cic", "tsc", "pcs"):
            for s in (1, 2):
                col = cols[(shape, s)]
                nm = f"dens_{shape}_s{s}_amp0.0001"
                a1.plot(x, get(key, nm), "o", ms=2.3, color=col, mfc="none", mew=0.7)
                a1.plot(x, get(key, f"dens_{shape}_s{s}_amp1"), "-", color=col, lw=1.0,
                        label=f"{shape.upper()}, {'$n^3$' if s == 1 else '$(2n)^3$'}")
                if shape != "cic":
                    a1.plot(x, get(key, f"pred_dens_{shape}_s{s}"), ls="--", color=col,
                            lw=0.8)
                    a2.plot(x, get(key, f"vel_{shape}_s{s}_amp1_m"), "-", color=col, lw=1.0)
                    a2.plot(x, get(key, f"vel_{shape}_s{s}_amp1_w"), ":", color=col, lw=1.2)
                    a2.plot(x, get(key, f"pred_vel_{shape}_s{s}"), ls="--", color=col,
                            lw=0.8)
        for ax in (a1, a2):
            fs.band(ax, [0, 1], [0.99, 0.99], [1.01, 1.01], "grey", alpha=0.15)
            ax.axhline(1.0, **fs.THIN)
            ax.set_xlim(0, 1.0)
            ax.set_ylim(0.85, 1.15)
            ax.set_yticks([0.9, 0.95, 1.0, 1.05, 1.1])
            ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8] if c == 0 else [0.2, 0.4, 0.6, 0.8, 1.0])
        a1.set_xticklabels([])
        a1.text(0.5, 0.97, f"{_box_label(L)}, $z_{{\\rm ini}}=49$, ${n}^3$",
                transform=a1.transAxes, ha="center", va="top", fontsize=9,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=1.0))
        a2.set_xlabel(r"$k/k_{\rm Ny}$", labelpad=-2)
        if c == 0:
            a1.set_ylabel(r"$P_{\delta\delta}$: deposit / mesh field")
            a2.set_ylabel(r"$P_{\theta\theta}$: deposit / mesh field")
            a1.legend(loc="lower left", fontsize=7, ncol=3)
            h = [Line2D([], [], color="k", lw=1.0), Line2D([], [], color="k", ls="",
                                                           marker="o", mfc="none", ms=3),
                 Line2D([], [], color="k", ls="--", lw=0.8)]
            l2 = a2.legend(h[:1] + [Line2D([], [], color="k", ls=":", lw=1.2), h[2]],
                           ["momentum deposit", "momentum / mass", "lattice response"],
                           loc="lower left", fontsize=7)
        else:
            a1.legend([Line2D([], [], color="k", lw=1.0),
                       Line2D([], [], color="k", ls="", marker="o", mfc="none", ms=3),
                       Line2D([], [], color="k", ls="--", lw=0.8)],
                      ["actual amplitude", "amplitude $10^{-4}$", "lattice response"],
                      loc="lower left", fontsize=7)
            for ax in (a1, a2):
                ax.set_yticklabels([])
    fs.save(fig, os.path.join(FIGDIR, "gramses_estimator"))
    plt.close(fig)
    log("wrote gramses_estimator")


# ---------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=("expect", "closed", "estimator", "ics", "fig4",
                                      "t0prec", "report"))
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--L", type=float, default=4000.0)
    ap.add_argument("--z", type=float, default=49.0)
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    globals()[f"stage_{a.stage}"](a)


if __name__ == "__main__":
    main()
