"""Initial conditions in the gauges of GRAMSES (Barrera-Hinojosa & Li, arXiv:2001.07968).

    python3 gramses_ic.py --n 128 --L 256 --z 49 --setting gramses --velocity fd \
        --dz 0.5 --out ic.npz [--lower] [--save-mesh]

Reproduction specification: cosmo/notes/spec_2001.07968.md ("notes:L" below is line L of
that file). Cold matter + Lambda, no radiation: the synchronous-gauge density is the
Eisenstein-Hu spectrum of spectrum.py times the scale-independent growth factor, and the
other gauges follow from the closed forms of notes Sec. 5.3 (notes:552-570), implemented
below as transfer ratios to delta^S at the same k and a.

Two settings (notes:219-224, the table of Sec. 3.3):

    "newtonian"  positions from the Zel'dovich displacement of delta^S, velocities u^i_N
                 (default 2LPTic with 2LPT off, notes:221, 233-236);
    "gramses"    positions from the displacement of the particle-number contrast of the
                 constant-mean-curvature, minimal-distortion (CMC-MD) gauge,
                 delta^p = delta^C - 3 Psi = delta^S - 3 eta (notes:224, 227), velocities
                 u^i_C = u^i_N (notes:194).

Velocities (notes Sec. 3.5, 3.6):

    "fd"        finite difference of displacements realised with the same seed from the
                spectra at z_ini -+ dz, notes:245 (II:341),
                    dx^i/dt = (H/a) [chi^i(z_-) - chi^i(z_+)] / (2 dz),
                with the spectra at z_+- built with eta frozen (notes:261, II:372) and,
                optionally, renormalised to sigma8 values like 2LPTic (notes:267-275);
    "two-step"  dx^i/dt = H f chi^i_S, with chi_S the displacement of delta^S, also in the
                gramses setting (notes:250-255, II:333-334);
    "naive"     dx^i/dt = H f chi^i of the setting's own density (wrong in the gramses
                setting, where the growth rate of delta^p depends on k; for comparison).

Units: lengths in Mpc/h (comoving), k in h/Mpc, conformal Hubble rate written as
calH = aH/c in h/Mpc, H in km/s/(Mpc/h). The returned velocity u is the variable the paper
plots (notes:347-350, 578-582), the Gadget/2LPTic convention u = a^(1/2) dx/dt with dx/dt
the comoving coordinate velocity in km/s; dxdt is returned too.

Mesh conventions of random_field.py and cosmo_id.py: n^3 cells, cell centres
(i + 1/2) L/n; the particles start on these centres (a regular lattice, notes:236-237), one
per cell, in C order of the index triple (i, j, k).
"""
import argparse
import os
import sys

import numpy as np
from scipy import integrate

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import cosmo_id as cid            # noqa: E402
import random_field as rf         # noqa: E402
import spectrum as sp             # noqa: E402

SETTINGS = ("newtonian", "gramses")
VELOCITIES = ("fd", "two-step", "naive")
SIGMA8_MODES = ("none", "linear", "scaled")

# sigma8 integrals (notes:536-537): Simpson rule in ln k on the grid of spectrum.py
K_SIGMA_MIN, K_SIGMA_MAX = 1e-6, 1e4
_LNK = np.linspace(np.log(K_SIGMA_MIN), np.log(K_SIGMA_MAX), 2**14 + 1)
_KG = np.exp(_LNK)


# ---------------------------------------------------------------------------------------
# background (matter + Lambda, no radiation)
# ---------------------------------------------------------------------------------------
def a_of_z(z):
    return 1.0/(1.0 + np.asarray(z, dtype=float))


def hubble_kms(a, params):
    """H(a) in km/s/(Mpc/h): 100 E(a), E from spectrum.hubble_e."""
    return 100.0*sp.hubble_e(a, params["omega_m"], params["omega_l"])


def conformal_hubble(a, params):
    """calH/c = a H(a)/c in h/Mpc: a E(a) / (c/H0), c/H0 = 2997.92458 Mpc/h.
    Values for the GRAMSES parameters: 1.849e-3, 1.307e-3, 8.27e-4 h/Mpc at z = 99, 49,
    19 (notes:19-20)."""
    return a*sp.hubble_e(a, params["omega_m"], params["omega_l"])/sp.HUBBLE_DISTANCE


def omega_m_a(a, params):
    """Omega_m(a) = Omega_m a^-3 / E^2 (spectrum.omega_m_of_a)."""
    return sp.omega_m_of_a(a, params["omega_m"], params["omega_l"])


def growth(a, params):
    """Linear growth factor D_1(a) of matter + Lambda (spectrum.growth_factor, D = a at
    early times); only ratios D(a1)/D(a2) are used (notes:263, 592)."""
    return sp.growth_factor(a, params["omega_m"], params["omega_l"])


def growth_rate(a, params):
    """f = d ln D_1 / d ln a (spectrum.growth_rate)."""
    return sp.growth_rate(a, params["omega_m"], params["omega_l"])


def yukawa_mass2(a, params):
    """m^2 = -3 a^2 dH/dt = 12 pi G a^2 rho_m = (9/2) Omega_m(a) calH^2 in (h/Mpc)^2, the
    Yukawa mass of the CMC lapse equation (notes:289, 555; II:476).
    m/c = 3.92e-3, 2.77e-3, 1.75e-3 h/Mpc at z = 99, 49, 19 (notes:623)."""
    return 4.5*omega_m_a(a, params)*conformal_hubble(a, params)**2


# ---------------------------------------------------------------------------------------
# closed forms of notes Sec. 5.3 (CDM + Lambda, no radiation), as ratios to delta^S(k, a)
# ---------------------------------------------------------------------------------------
def x_of_k(k, a, params):
    """x = (k / calH)^2 (notes:554)."""
    return (np.asarray(k, dtype=float)/conformal_hubble(a, params))**2


def _xfo(k, a, params):
    return x_of_k(k, a, params), growth_rate(a, params), omega_m_a(a, params)


def phi_T(k, a, params):
    """Bardeen potential of the Newtonian gauge, phi = psi (notes:556, 558):
        phi / delta^S = -(3/2) Omega_m(a) / x."""
    x, f, om = _xfo(k, a, params)
    return -1.5*om/x


def eta_T(k, a, params):
    """Synchronous-gauge metric perturbation eta (MB95 sign), constant in time for
    CDM + Lambda (notes:558):
        eta / delta^S = -(f + (3/2) Omega_m(a)) / x."""
    x, f, om = _xfo(k, a, params)
    return -(f + 1.5*om)/x


def deltaN_T(k, a, params):
    """Newtonian-gauge density contrast (notes:559):  delta^N / delta^S = 1 + 3 f / x."""
    x, f, om = _xfo(k, a, params)
    return 1.0 + 3.0*f/x


def deltap_T(k, a, params):
    """Particle-number contrast of the CMC-MD gauge (notes:560; II:308 delta^p =
    delta^S - 3 eta):
        delta^p / delta^S = 1 + (3 f + (9/2) Omega_m(a)) / x."""
    x, f, om = _xfo(k, a, params)
    return 1.0 + (3.0*f + 4.5*om)/x


def power_ratio_pS(k, a, params):
    """P_pp / P_SS = [1 + (3 f + (9/2) Omega_m) calH^2 / k^2]^2 (notes:561); in matter
    domination (1 + 7.5 calH^2/k^2)^2."""
    return deltap_T(k, a, params)**2


def growth_rate_p(k, a, params):
    """Growth rate of delta^p (notes:562):
        f_p = d ln delta^p / d ln a = f / [1 + (3 f + (9/2) Omega_m) / x]."""
    return growth_rate(a, params)/deltap_T(k, a, params)


def H_xi0_T(k, a, params):
    """Time shift Newtonian -> CMC-MD (notes:563), times H:
        xi_0 = -3 a^2 H f phi / (k^2 + m^2),  so  H xi_0 / delta^S = -3 f phi_T / (x + (9/2)
        Omega_m(a))  (c = 1, cosmic time; spatial shift xi_i = 0, notes:192-196)."""
    x, f, om = _xfo(k, a, params)
    return -3.0*f*phi_T(k, a, params)/(x + 4.5*om)


def shift_T(k, a, params):
    """Longitudinal minimal-distortion shift per unit coordinate velocity (notes:564):
        beta^i_par / u^i_par = -m^2 / (k^2 + m^2) = -(9/2) Omega_m / (x + (9/2) Omega_m)."""
    x, f, om = _xfo(k, a, params)
    return -4.5*om/(x + 4.5*om)


def theta_lower_T(k, a, params):
    """Lower-index velocity divergence of GRAMSES per Newtonian one (notes:565-567):
        a^-2 d_i u^C_i / d_i u^i_N = k^2 / (k^2 + m^2) = x / (x + (9/2) Omega_m)."""
    x, f, om = _xfo(k, a, params)
    return x/(x + 4.5*om)


def PsiC_T(k, a, params):
    """Spatial-metric potential of the CMC-MD gauge (notes:568):
        Psi_C = -4 pi G a^2 rho delta^p / (k^2 + m^2) = phi (x + 3 f + (9/2) Omega_m) /
        (x + (9/2) Omega_m)."""
    x, f, om = _xfo(k, a, params)
    return phi_T(k, a, params)*(x + 3.0*f + 4.5*om)/(x + 4.5*om)


def deltaC_T(k, a, params):
    """Energy-density contrast of the CMC-MD gauge (notes:569):
        delta^C = delta^p + 3 Psi_C = delta^p k^2 / (k^2 + m^2)."""
    x, f, om = _xfo(k, a, params)
    return deltap_T(k, a, params)*x/(x + 4.5*om)


def PhiC_T(k, a, params):
    """Lapse perturbation of the CMC-MD gauge, from the lapse equation II:476 with
    dP = 0 (notes:570):  Phi_C = -4 pi G a^2 rho delta^C / (k^2 + m^2)
    = -(3/2) Omega_m delta^C / (x + (9/2) Omega_m)."""
    x, f, om = _xfo(k, a, params)
    return -1.5*om*deltaC_T(k, a, params)/(x + 4.5*om)


# ---------------------------------------------------------------------------------------
# spectra in each gauge
# ---------------------------------------------------------------------------------------
def power_S(k, z, params):
    """Synchronous-gauge (= comoving) matter spectrum P_SS(k, z): spectrum.linear_power
    (Eisenstein-Hu times the matter + Lambda growth factor)."""
    return sp.linear_power(k, z, params)


def power_gauge(k, z, params, which="S"):
    """P(k, z) of delta^S ("S"), delta^p ("p"), delta^N ("N"), delta^C ("C"), eta ("eta")
    or the cross spectrum <delta^S eta> ("S-eta"), from the closed forms above."""
    a = float(a_of_z(z))
    ps = power_S(k, z, params)
    t = {"S": lambda: 1.0, "p": lambda: deltap_T(k, a, params),
         "N": lambda: deltaN_T(k, a, params), "C": lambda: deltaC_T(k, a, params),
         "eta": lambda: eta_T(k, a, params)}
    if which == "S-eta":
        return ps*eta_T(k, a, params)
    return ps*np.asarray(t[which]())**2


def power_p_frozen(k, z, z_ini, params):
    """Spectrum of delta^p at z near z_ini with eta frozen and the matter + Lambda growth
    factor (notes:261, II:372):
        delta^p(k; z) = [D_1(z)/D_1(z_ini)] delta^S(k; z_ini) - 3 eta(k; z_ini).
    Without radiation eta is exactly constant, so this equals power_gauge(k, z, "p")."""
    a0 = float(a_of_z(z_ini))
    r = float(growth(a_of_z(z), params)/growth(a0, params))
    return power_S(k, z_ini, params)*(r - 3.0*eta_T(k, a0, params))**2


def power_S_scaled(k, z, z_ini, params):
    """[D_1(z)/D_1(z_ini)]^2 P_SS(k; z_ini) (notes:265, inferred from II:378)."""
    r = float(growth(a_of_z(z), params)/growth(a_of_z(z_ini), params))
    return r*r*power_S(k, z_ini, params)


def theta_power_N(k, z, params):
    """Linear spectrum of theta = d_i u^i with u = a^(1/2) dx/dt in km/s (notes:578-582):
        P_thth = a H^2 f^2 P_SS,  units (km/s)^2 Mpc/h."""
    a = float(a_of_z(z))
    return a*hubble_kms(a, params)**2*growth_rate(a, params)**2*power_S(k, z, params)


def theta_power_lower(k, z, params):
    """Spectrum of the GRAMSES lower-index divergence a^-2 d_i u^C_i, in the units of
    theta_power_N: P^N_thth [k^2/(k^2 + m^2)]^2 (notes:565-567)."""
    a = float(a_of_z(z))
    return theta_power_N(k, z, params)*theta_lower_T(k, a, params)**2


def growth_rate_fd(pk, z, dz):
    """Finite-difference growth rate of notes:368 (II:349) from three spectra:
        f^FD = [sqrt(P(z - dz)) - sqrt(P(z + dz))] / [2 a dz sqrt(P(z))],
    pk(z) -> P array."""
    a = float(a_of_z(z))
    return (np.sqrt(pk(z - dz)) - np.sqrt(pk(z + dz)))/(2.0*a*dz*np.sqrt(pk(z)))


# ---------------------------------------------------------------------------------------
# sigma8 normalisation (notes:267-275, II:376-388)
# ---------------------------------------------------------------------------------------
def sigma8_of(pk, R=8.0):
    """sqrt(int dln k k^3 P(k)/(2 pi^2) W^2(k R)) for a callable P (notes:536-537), top
    hat of R Mpc/h, Simpson rule in ln k on [1e-6, 1e4] h/Mpc (16385 points, the grid of
    spectrum.py). For a signed P (a cross spectrum) the signed integral is returned as
    sign * sqrt(|integral|)."""
    v = integrate.simpson(_KG**3*np.asarray(pk(_KG))/(2.0*np.pi**2)
                          * sp.tophat_window(R*_KG)**2, x=_LNK)
    return float(np.sign(v)*np.sqrt(abs(v)))


def sigma8_targets(z_ini, dz, params, setting, mode="linear", growth_fn=None):
    """sigma8 values to which the spectra at (z_ini - dz, z_ini, z_ini + dz) are
    renormalised, as 2LPTic needs them (notes:267-275).

    mode "linear": the corrections of the paper, with r = D_1(z)/D_1(z_ini):
        newtonian  sigma8^S(z) = r sigma8^S(z_ini)                         (II:378)
        gramses    sigma8^p(z) = sqrt(r^2 [sigma8^S]^2 + 9 [sigma8^eta]^2
                                      - 6 r [sigma8^{S eta}]^2)            (II:384)
                   [sigma8^{S eta}]^2 = ([sigma8^S]^2 - [sigma8^p]^2
                                          + 9 [sigma8^eta]^2) / 6          (II:388)
        all at z_ini; sigma8 of P_SS, P_pp and P_etaeta from sigma8_of.
    mode "scaled": sigma8(z) = sigma8(z_ini) g(z)/g(z_ini) for the setting's own spectrum,
        with g = growth_fn(a) (default D_1). For "newtonian" and g = D_1 this equals
        "linear"; for "gramses" it skips II:384 (delta^p does not grow like D_1); with a
        g that is not D_1 it models sigma8 values from a code whose growth differs (the
        "def sigma8" curves of the paper's Fig. 4, notes:275, 496-497).
    Returns {"z": [z-, z_ini, z+], "sigma8": [...], plus the ingredients}."""
    zs = [z_ini - dz, z_ini, z_ini + dz]
    a0 = float(a_of_z(z_ini))
    r = [float(growth(a_of_z(z), params)/growth(a0, params)) for z in zs]
    sS = sigma8_of(lambda k: power_S(k, z_ini, params))
    out = {"z": zs, "r": r, "sigma8_S_ini": sS}
    if setting == "newtonian":
        s0 = sS
    else:
        s0 = sigma8_of(lambda k: power_gauge(k, z_ini, params, "p"))
        se = sigma8_of(lambda k: power_gauge(k, z_ini, params, "eta"))
        cross2 = (sS**2 - s0**2 + 9.0*se**2)/6.0                       # II:388
        out.update(sigma8_p_ini=s0, sigma8_eta_ini=se, sigma8_Seta2_ini=cross2,
                   sigma8_Seta2_direct=sigma8_of(
                       lambda k: power_gauge(k, z_ini, params, "S-eta"))**2
                   * np.sign(sigma8_of(lambda k: power_gauge(k, z_ini, params, "S-eta"))))
    if mode == "linear":
        if setting == "newtonian":
            vals = [ri*sS for ri in r]                                  # II:378
        else:
            vals = [float(np.sqrt(ri*ri*sS**2 + 9.0*se**2 - 6.0*ri*cross2)) for ri in r]
    elif mode == "scaled":
        g = growth_fn if growth_fn is not None else (lambda a: growth(a, params))
        g0 = float(g(a0))
        vals = [s0*float(g(a_of_z(z)))/g0 for z in zs]
    else:
        raise ValueError(f"unknown sigma8 mode {mode!r}")
    out["sigma8"] = vals
    return out


# ---------------------------------------------------------------------------------------
# realisation on the lattice
# ---------------------------------------------------------------------------------------
def lattice(n, L):
    """Unperturbed particle positions: the n^3 cell centres, shape (n^3, 3), C order."""
    q1 = (np.arange(n) + 0.5)*L/n
    Q = np.meshgrid(q1, q1, q1, indexing="ij")
    return np.stack([c.ravel() for c in Q], axis=1)


def realise(n, L, pk, seed):
    """delta on the mesh with spectrum pk and seed (random_field.gaussian_field; the
    Nyquist planes are left empty so that -div chi = delta exactly) and its Zel'dovich
    displacement chi (random_field.zeldovich): (delta, [chi_x, chi_y, chi_z])."""
    d = rf.gaussian_field(n, L, pk, seed, zero_nyquist=True)
    return d, rf.zeldovich(d, L)


def _spectrum_table(setting, z, z_ini, params, spectra):
    """P(k) callable of the setting's density at z. spectra = "frozen": D_1-scaled
    delta^S and eta frozen at z_ini (notes:261); "direct": the closed form evaluated at
    z (the analogue of feeding Boltzmann-code spectra at z directly)."""
    if setting == "newtonian":
        if spectra == "frozen":
            return lambda k: power_S_scaled(k, z, z_ini, params)
        return lambda k: power_S(k, z, params)
    if spectra == "frozen":
        return lambda k: power_p_frozen(k, z, z_ini, params)
    return lambda k: power_gauge(k, z, params, "p")


def lower_index_velocity(u, L, a, params):
    """GRAMSES's one-time shift solve at z_ini (notes:282-293, Sec. 3.7), physical form:
    (Delta_L beta)^i = 16 pi G rho a^2 (u^i + beta^i), Delta_L = lap + (1/3) grad div,
    16 pi G rho a^2 = (4/3) m^2. Spectrally, with the longitudinal and transverse parts of
    the coordinate velocity u^i (three mesh arrays):
        beta_par = -m^2 / (k^2 + m^2) u_par,  beta_perp = -(4/3) m^2 / (k^2 + (4/3) m^2)
        u_perp,
    and u_i / a^2 = u^i + beta^i (II:322). Returns (beta, u + beta), each three arrays in
    the units of u. The particles are given the mesh values at their lattice sites
    (Lagrangian evaluation; GRAMSES interpolates at the displaced positions, a second-order
    difference)."""
    n = u[0].shape[0]
    tor = cid.Torus(n, L)
    m2 = float(yukawa_mass2(a, params))
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    U = [tor.fft(c) for c in u]
    kd = tor.kd
    kdotu = kd[0]*U[0] + kd[1]*U[1] + kd[2]*U[2]
    kd2 = kd[0]**2 + kd[1]**2 + kd[2]**2
    kd2s = np.where(kd2 > 0, kd2, 1.0)
    gl = -m2/(k2 + m2)
    gt = -(4.0/3.0)*m2/(k2 + (4.0/3.0)*m2)
    beta = []
    for i in range(3):
        par = np.where(kd2 > 0, kd[i]*kdotu/kd2s, 0.0)
        B = gl*par + gt*(U[i] - par)
        B[0, 0, 0] = 0.0                  # the mean velocity is zero (no k = 0 mode)
        beta.append(tor.ifft(B))
    return beta, [u[i] + beta[i] for i in range(3)]


def make_ic(n, L, z_ini, setting="gramses", velocity="fd", dz=None, sigma8="linear",
            seed=2001, params=None, spectra="frozen", fd_dtype=np.float64,
            f_model="exact", growth_fn=None, lower=False, keep_mesh=True):
    """Particles on the n^3 lattice of a box of side L (Mpc/h) at redshift z_ini.

    setting   "newtonian" (positions from delta^S) or "gramses" (from delta^p, CMC-MD).
    velocity  "fd" (notes:245), "two-step" (H f chi_S, notes:253) or "naive" (H f chi of
              the setting's own density).
    dz        redshift step of "fd"; default 0.01 z_ini (Delta z / z_ini ~ 1 %, II:410).
    sigma8    "none", "linear" (II:378, 384, 388) or "scaled" (see sigma8_targets); each
              of the three spectra is renormalised to its target like 2LPTic (P -> c^2 P,
              c = target / sigma8_of(P)). For "two-step"/"naive" only z_ini is used.
    spectra   "frozen" (notes:261) or "direct" (closed form at z_+-), see _spectrum_table.
    fd_dtype  precision in which chi(z_-) and chi(z_+) are stored before they are
              differenced (np.float32 emulates a single-precision code).
    f_model   "exact" (spectrum.growth_rate) or "omega0.6" (f = Omega_m(a)^0.6, default
              2LPTic, notes:229) for "two-step"/"naive".
    lower     also return the GRAMSES lower-index velocity (lower_index_velocity).

    Returns a dict:
        q, x       lattice sites and positions (n^3, 3), Mpc/h, x wrapped into [0, L)
        u, dxdt    velocities (n^3, 3): u = a^(1/2) dx/dt (km/s), dx/dt in km/s
        u_lower    (if lower) a^(1/2) (u^i + beta^i) = a^(1/2) a^-2 u_i, km/s
        mesh       (if keep_mesh) the mesh fields: delta (setting's density at z_ini),
                   chi (3), u (3), and for "fd" chi_m, chi_p (z_-, z_+), for "two-step"
                   in the gramses setting delta_S, chi_S, for lower beta (3)
        meta       a, H, f, dz, sigma8 targets, renormalisation factors c, ...
    """
    params = sp.GRAMSES if params is None else params
    if setting not in SETTINGS or velocity not in VELOCITIES:
        raise ValueError(f"setting {setting!r} / velocity {velocity!r}")
    a = float(a_of_z(z_ini))
    H = float(hubble_kms(a, params))
    f = float(growth_rate(a, params)) if f_model == "exact" else \
        float(omega_m_a(a, params))**0.6
    meta = {"n": n, "L": L, "z_ini": z_ini, "a": a, "H_kms": H, "f": f, "seed": seed,
            "setting": setting, "velocity": velocity, "sigma8_mode": sigma8,
            "spectra": spectra, "f_model": f_model, "fd_dtype": np.dtype(fd_dtype).name}
    if velocity == "fd" and dz is None:
        dz = 0.01*z_ini
    meta["dz"] = dz

    def renorm(pk, target):
        if target is None:
            return pk, 1.0
        c = target/sigma8_of(pk)
        return (lambda k: c*c*pk(k)), float(c)

    targets = None
    if sigma8 != "none":
        targets = sigma8_targets(z_ini, dz if dz is not None else 0.0, params, setting,
                                 sigma8, growth_fn)
        meta["sigma8_targets"] = targets
    t_ini = targets["sigma8"][1] if targets else None

    pk0, c0 = renorm(_spectrum_table(setting, z_ini, z_ini, params, spectra), t_ini)
    delta, chi = realise(n, L, pk0, seed)
    meta["c_ini"] = c0
    mesh = {"delta": delta, "chi": chi}

    if velocity == "fd":
        pkm, cm = renorm(_spectrum_table(setting, z_ini - dz, z_ini, params, spectra),
                         targets["sigma8"][0] if targets else None)
        pkp, cp = renorm(_spectrum_table(setting, z_ini + dz, z_ini, params, spectra),
                         targets["sigma8"][2] if targets else None)
        _, chi_m = realise(n, L, pkm, seed)
        _, chi_p = realise(n, L, pkp, seed)
        meta.update(c_minus=cm, c_plus=cp)
        fac = H/a/(2.0*dz)                                             # II:341
        dxdt = [fac*(chi_m[i].astype(fd_dtype) - chi_p[i].astype(fd_dtype))
                .astype(np.float64) for i in range(3)]
        mesh.update(chi_m=chi_m, chi_p=chi_p)
    else:
        if velocity == "two-step" and setting == "gramses":
            pkS, cS = renorm(lambda k: power_S(k, z_ini, params),
                             sigma8_of(lambda k: power_S(k, z_ini, params))
                             if targets else None)
            dS, chiS = realise(n, L, pkS, seed)
            mesh.update(delta_S=dS, chi_S=chiS)
            src = chiS
        else:
            src = chi
        dxdt = [H*f*c for c in src]
    u = [np.sqrt(a)*c for c in dxdt]
    mesh["u"] = u

    q = lattice(n, L)
    x = (q + np.stack([c.ravel() for c in chi], axis=1)) % L
    out = {"q": q, "x": x, "u": np.stack([c.ravel() for c in u], axis=1),
           "dxdt": np.stack([c.ravel() for c in dxdt], axis=1), "meta": meta}
    if lower:
        beta, ul = lower_index_velocity(u, L, a, params)
        mesh["beta"] = beta
        mesh["u_lower"] = ul
        out["u_lower"] = np.stack([c.ravel() for c in ul], axis=1)
    if keep_mesh:
        out["mesh"] = mesh
    return out


# ---------------------------------------------------------------------------------------
# checks of the closed forms against the limits and relations of notes Sec. 5.3
# ---------------------------------------------------------------------------------------
def _dlna(fun, a, eps=1e-4):
    """d fun / d ln a by a central difference in ln a (fun(a) -> array)."""
    return (fun(a*np.exp(eps)) - fun(a*np.exp(-eps)))/(2.0*eps)


def closed_form_checks(params=None):
    """Checks of the closed forms: relations between them (gauge transformations of
    notes:181-198, continuity equations of notes:219-224, the linear constraints
    II:475-476), the small- and large-k limits, and the values the notes read from the
    paper's figures with these formulas (notes:394-396, 472, 572-574, 19, 623).
    Returns a list of dicts (name, value, target, tol, ok)."""
    P = sp.GRAMSES if params is None else params
    res = []

    def add(name, value, target, tol, note="", kind="implementation"):
        value, target = float(value), float(target)
        res.append({"name": name, "value": value, "target": target, "tol": tol,
                    "ok": bool(abs(value - target) <= tol), "note": note, "kind": kind})

    k = np.logspace(-5, 1, 241)
    zs = (99.0, 49.0, 19.0, 0.0)
    worst = {key: 0.0 for key in ("eta_const", "p_eq_N3phi", "fp_num", "conj",
                                  "contN", "contC", "Psi3", "dC2", "PhiC_gauge",
                                  "Ham", "beta_gauge", "K_C", "phidot")}
    for z in zs:
        a = float(a_of_z(z))
        f, om = float(growth_rate(a, P)), float(omega_m_a(a, P))
        Dk = lambda aa: growth(aa, P)                                  # noqa: E731
        dS = lambda aa: Dk(aa)                                         # delta^S(k) / T(k)
        # eta constant: d ln|eta delta^S| / d ln a (delta^S grows as D)
        eta = lambda aa: eta_T(k, aa, P)*dS(aa)                        # noqa: E731
        worst["eta_const"] = max(worst["eta_const"],
                                 np.abs(_dlna(eta, a)/eta(a)).max())
        worst["p_eq_N3phi"] = max(worst["p_eq_N3phi"], np.abs(
            deltaN_T(k, a, P) - 3*phi_T(k, a, P) - deltap_T(k, a, P)).max()
            / np.abs(deltap_T(k, a, P)).max())
        dp = lambda aa: deltap_T(k, aa, P)*dS(aa)                      # noqa: E731
        worst["fp_num"] = max(worst["fp_num"], np.abs(
            _dlna(dp, a)/dp(a) - growth_rate_p(k, a, P)).max())
        # conjugate pair {delta^p, u^i}: d delta^p/dt + theta = 0, theta = -H f delta^S
        worst["conj"] = max(worst["conj"], np.abs(
            growth_rate_p(k, a, P)*deltap_T(k, a, P) - f).max())
        # Newtonian continuity (II:232): d dN/dlna - f dS - 3 d phi/dlna = 0
        dN = lambda aa: deltaN_T(k, aa, P)*dS(aa)                      # noqa: E731
        ph = lambda aa: phi_T(k, aa, P)*dS(aa)                         # noqa: E731
        worst["contN"] = max(worst["contN"], np.abs(
            _dlna(dN, a) - f*dS(a) - 3*_dlna(ph, a)).max()/np.abs(dN(a)).max())
        worst["phidot"] = max(worst["phidot"], np.abs(
            _dlna(ph, a) - (f - 1.0)*ph(a)).max()/np.abs(ph(a)).max())
        # CMC continuity (II:288): d dC/dlna - f dS - 3 d PsiC/dlna = 0
        dC = lambda aa: deltaC_T(k, aa, P)*dS(aa)                      # noqa: E731
        Ps = lambda aa: PsiC_T(k, aa, P)*dS(aa)                        # noqa: E731
        worst["contC"] = max(worst["contC"], np.abs(
            _dlna(dC, a) - f*dS(a) - 3*_dlna(Ps, a)).max()/np.abs(dC(a)).max())
        # Psi_C three ways: closed form, -(m^2/3) delta^p/(k^2+m^2), phi - H xi_0 (II:132)
        x = x_of_k(k, a, P)
        ps1 = PsiC_T(k, a, P)
        ps2 = -1.5*om*deltap_T(k, a, P)/(x + 4.5*om)
        ps3 = phi_T(k, a, P) - H_xi0_T(k, a, P)
        worst["Psi3"] = max(worst["Psi3"], (np.abs(ps1 - ps2) + np.abs(ps1 - ps3)).max()
                            / np.abs(ps1).max())
        # delta^C two ways: closed form and delta^N - 3 H xi_0 (II:155, w = 0)
        worst["dC2"] = max(worst["dC2"], np.abs(
            deltaC_T(k, a, P) - (deltaN_T(k, a, P) - 3*H_xi0_T(k, a, P))).max()
            / np.abs(deltaC_T(k, a, P)).max())
        # Phi_C from the gauge transformation Phi' = psi + d xi_0/dt (II:126) against the
        # lapse equation (II:476). d xi_0/dt = H d(Y/H)/dlna with Y = H xi_0.
        lnH = lambda aa: np.log(hubble_kms(aa, P))                     # noqa: E731
        Y = lambda aa: H_xi0_T(k, aa, P)*dS(aa)                        # noqa: E731
        xidot = _dlna(Y, a) - Y(a)*_dlna(lnH, a)
        phic_g = phi_T(k, a, P)*dS(a) + xidot
        phic = PhiC_T(k, a, P)*dS(a)
        worst["PhiC_gauge"] = max(worst["PhiC_gauge"],
                                  np.abs(phic_g - phic).max()/np.abs(phic).max())
        # Hamiltonian constraint in CMC-MD (II:475): -x Psi_C = (3/2) Omega_m delta^C
        worst["Ham"] = max(worst["Ham"], np.abs(
            -x*ps3 - 1.5*om*(deltaN_T(k, a, P) - 3*H_xi0_T(k, a, P))).max()
            / np.abs(1.5*om*deltaC_T(k, a, P)).max())
        # shift from the gauge transformation beta_i = -d_i xi_0 (II:127), u^i = i k H f
        # delta^S / k^2: beta/u = -(H xi_0/delta^S) x / f
        worst["beta_gauge"] = max(worst["beta_gauge"], np.abs(
            -H_xi0_T(k, a, P)*x/f - shift_T(k, a, P)).max())
        # CMC slicing: delta K_C = delta K_N - 3 dH/dt xi_0 + k^2 a^-2 xi_0 = 0, with
        # delta K_N = 3 H psi + 3 dphi/dt (II:459, 464); in units of H:
        # dK_N/H = 3 phi + 3 dphi/dlna; -3 Hdot xi_0/H = -3 (dlnH/dlna) H xi_0
        dKN = 3*ph(a) + 3*_dlna(ph, a)
        dKC = dKN - 3*_dlna(lnH, a)*Y(a) + x*Y(a)
        worst["K_C"] = max(worst["K_C"], np.abs(dKC).max()/np.abs(dKN).max())
    tol = {"eta_const": 1e-6, "p_eq_N3phi": 1e-14, "fp_num": 1e-6, "conj": 1e-14,
           "contN": 1e-6, "contC": 1e-6, "Psi3": 1e-13, "dC2": 1e-10,
           "PhiC_gauge": 1e-6, "Ham": 1e-10, "beta_gauge": 1e-14, "K_C": 1e-6,
           "phidot": 1e-6}
    text = {"eta_const": "eta constant in time, max |d ln eta / d ln a| (notes:556)",
            "p_eq_N3phi": "delta^p = delta^N - 3 phi (notes:560), max rel. difference",
            "fp_num": "f_p = d ln delta^p/d ln a numerically (notes:562)",
            "conj": "conjugacy f_p delta^p = f delta^S (II:292-300)",
            "contN": "Newtonian continuity d_t dN + theta - 3 d_t phi = 0 (II:232)",
            "phidot": "d_t phi = H (f - 1) phi (notes:556)",
            "contC": "CMC continuity d_t dC + theta - 3 d_t Psi_C = 0 (II:288)",
            "Psi3": "Psi_C: closed form = -(m^2/3) dp/(k^2+m^2) = phi - H xi_0 (II:132)",
            "dC2": "delta^C = delta^p k^2/(k^2+m^2) = delta^N - 3 H xi_0 (II:155)",
            "PhiC_gauge": "Phi_C (lapse eq. II:476) = psi + d_t xi_0 (II:126)",
            "Ham": "CMC Hamiltonian constraint -k^2 Psi = 4 pi G a^2 rho dC (II:475)",
            "beta_gauge": "beta = -grad xi_0 / a^2 (II:127) = -m^2/(k^2+m^2) u (notes:564)",
            "K_C": "delta K = 0 in CMC after the time shift (II:459, 464)"}
    for key, v in worst.items():
        note = "z = 99, 49, 19, 0; 1e-5 < k < 10 h/Mpc"
        if key in ("dC2", "Ham"):
            note += "; rounding: terms of order 1/x cancel, x >= 3e-5"
        add(text[key], v, 0.0, tol[key], note)

    # limits (notes:556-570): large k, small k, matter domination
    for z in (99.0, 49.0):
        a = float(a_of_z(z))
        f, om = float(growth_rate(a, P)), float(omega_m_a(a, P))
        g = 3*f + 4.5*om
        kb = 1e4*conformal_hubble(a, P)                  # x = 1e8
        ks = 1e-4*conformal_hubble(a, P)                 # x = 1e-8
        xs = float(x_of_k(ks, a, P))
        big = max(abs(deltap_T(kb, a, P) - 1), abs(growth_rate_p(kb, a, P)/f - 1),
                  abs(theta_lower_T(kb, a, P) - 1), abs(PsiC_T(kb, a, P)/phi_T(kb, a, P)
                                                         - 1),
                  abs(deltaC_T(kb, a, P)/deltap_T(kb, a, P) - 1), abs(shift_T(kb, a, P)),
                  abs(deltaN_T(kb, a, P) - 1))
        add(f"large-k limit z={z:g} (x = 1e8): dp/dS, f_p/f, theta ratio, Psi_C/phi, "
            "dC/dp, dN/dS -> 1; beta/u -> 0", big, 0.0, 1e-7)
        small = max(abs(deltap_T(ks, a, P)/(-3*eta_T(ks, a, P)) - 1),
                    abs(growth_rate_p(ks, a, P)/(f*xs/g) - 1),
                    abs(power_ratio_pS(ks, a, P)*xs**2/g**2 - 1),
                    abs(theta_lower_T(ks, a, P)*4.5*om/xs - 1),
                    abs(shift_T(ks, a, P) + 1),
                    abs(PsiC_T(ks, a, P)/phi_T(ks, a, P) - g/(4.5*om)),
                    abs(deltaC_T(ks, a, P) - g/(4.5*om)))
        add(f"small-k limit z={z:g} (x = 1e-8): dp -> -3 eta, f_p -> f x/(3f+4.5 Om), "
            "P ratio -> (3f+4.5 Om)^2/x^2, theta ratio -> k^2/m^2, beta -> -u, Psi_C/phi "
            "and dC/dS -> (3f+4.5 Om)/(4.5 Om)", small, 0.0, 1e-7)
        # f_p = f/2 crossing at x = 3f + 4.5 Om
        kc = np.sqrt(g)*conformal_hubble(a, P)
        add(f"f_p = f/2 at k = sqrt(3f + 4.5 Om) calH, z={z:g}",
            growth_rate_p(kc, a, P)/f, 0.5, 1e-14, f"k = {kc:.4e} h/Mpc")
    md = {"omega_m": 1.0, "omega_l": 0.0, "omega_b": 0.05, "h": 0.7, "n_s": 1.0,
          "sigma8": 0.8}
    amd = 0.01
    gmd = 3*float(growth_rate(amd, md)) + 4.5*float(omega_m_a(amd, md))
    add("matter domination: 3 f + 4.5 Omega_m = 7.5 (notes:561)", gmd, 7.5, 1e-12)

    # values the notes give for these formulas (kind "notes"): they are compared, not
    # required. The two f_p values of notes:395-396 are the paper's Fig. 1 readings,
    # which include radiation (see the report); the closed form without it is ~1-2 %
    # higher.
    def at(fun, kk, z):
        return float(fun(kk, float(a_of_z(z)), P))
    add("f_p(z=49, k=3e-3) vs notes:395 (= paper Fig. 1 value)",
        at(growth_rate_p, 3e-3, 49), 0.408, 0.0015, "paper includes radiation", "notes")
    add("f_p(z=99, k=5e-3) vs notes:396 (= paper Fig. 1 value)",
        at(growth_rate_p, 5e-3, 99), 0.484, 0.0015, "paper includes radiation", "notes")
    add("P_pp/P_SS(z=99, k=0.002225) (notes:574)", at(power_ratio_pS, 0.002225, 99), 38.2,
        0.06, "", "notes")
    add("P_pp/P_SS(z=49, k=0.002225) (notes:574)", at(power_ratio_pS, 0.002225, 49), 12.9,
        0.06, "", "notes")
    add("[k^2/(k^2+m^2)]^2 (z=99, k=0.002225) (notes:472)",
        at(theta_lower_T, 0.002225, 99)**2, 0.0593, 0.0006, "", "notes")
    add("[k^2/(k^2+m^2)]^2 (z=49, k=0.002225) (notes:472)",
        at(theta_lower_T, 0.002225, 49)**2, 0.153, 0.0006, "", "notes")
    for z, v in ((99, 1.849e-3), (49, 1.307e-3), (19, 8.27e-4)):
        add(f"calH/c at z={z} (notes:19)", conformal_hubble(a_of_z(z), P), v, 0.6e-3*v, "", "notes")
    for z, v in ((99, 3.92e-3), (49, 2.77e-3), (19, 1.75e-3)):
        add(f"m/c at z={z} (notes:623)", np.sqrt(yukawa_mass2(a_of_z(z), P)), v, 0.6e-2*v, "", "notes")
    return res


# ---------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--n", type=int, default=128, help="particles per dimension")
    ap.add_argument("--L", type=float, default=256.0, help="box side, Mpc/h")
    ap.add_argument("--z", type=float, default=49.0, help="z_ini")
    ap.add_argument("--setting", choices=SETTINGS, default="gramses")
    ap.add_argument("--velocity", choices=VELOCITIES, default="fd")
    ap.add_argument("--dz", type=float, default=None, help="FD step (default 0.01 z)")
    ap.add_argument("--sigma8", choices=SIGMA8_MODES, default="linear")
    ap.add_argument("--spectra", choices=("frozen", "direct"), default="frozen")
    ap.add_argument("--seed", type=int, default=2001)
    ap.add_argument("--lower", action="store_true",
                    help="also write the GRAMSES lower-index velocity a^(1/2) a^-2 u_i")
    ap.add_argument("--save-mesh", action="store_true", help="also write the mesh fields")
    ap.add_argument("--single", action="store_true", help="positions/velocities float32")
    ap.add_argument("--check", action="store_true", help="run closed_form_checks and exit")
    ap.add_argument("--out", default="gramses_ic.npz")
    a = ap.parse_args()
    if a.check:
        res = closed_form_checks()
        for r in res:
            tag = ("PASS" if r["ok"] else "FAIL") if r["kind"] == "implementation" else \
                ("AGREE" if r["ok"] else "DIFFER")
            print(f"{tag:6s} {r['name']}: {r['value']:.6g} "
                  f"(target {r['target']:.6g} +- {r['tol']:.1g}) {r['note']}")
        imp = [r for r in res if r["kind"] == "implementation"]
        print(f"{sum(r['ok'] for r in imp)} of {len(imp)} implementation checks passed; "
              f"{sum(r['ok'] for r in res if r['kind'] != 'implementation')} of "
              f"{len(res) - len(imp)} values of the notes reproduced")
        sys.exit(0 if all(r["ok"] for r in imp) else 1)
    ic = make_ic(a.n, a.L, a.z, a.setting, a.velocity, a.dz, a.sigma8, a.seed,
                 spectra=a.spectra, lower=a.lower, keep_mesh=a.save_mesh)
    dt = np.float32 if a.single else np.float64
    out = {"x": ic["x"].astype(dt), "u": ic["u"].astype(dt), "L": a.L, "z_ini": a.z,
           "meta": repr(ic["meta"])}
    if a.lower:
        out["u_lower"] = ic["u_lower"].astype(dt)
    if a.save_mesh:
        for key, v in ic["mesh"].items():
            if isinstance(v, list):
                for i, c in enumerate(v):
                    out[f"mesh_{key}_{'xyz'[i]}"] = c
            else:
                out[f"mesh_{key}"] = v
    np.savez(a.out, **out)
    print(f"wrote {a.out}: {a.n}^3 particles, L = {a.L:g} Mpc/h, z_ini = {a.z:g}, "
          f"{a.setting}, velocity {a.velocity}, dz = {ic['meta']['dz']}")


if __name__ == "__main__":
    main()
