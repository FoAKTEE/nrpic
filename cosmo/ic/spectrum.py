"""Linear matter power spectrum: transfer-function fits, linear growth, normalisation.

Self-contained (numpy and scipy); no Boltzmann code. Units throughout:

    k        h/Mpc (comoving)
    r, R     Mpc/h (comoving)
    P(k)     (Mpc/h)^3, convention <delta(k) delta*(k')> = (2 pi)^3 delta_D(k - k') P(k),
             Delta^2(k) = k^3 P(k) / (2 pi^2)

The spectrum is that of the total matter density contrast (CDM + baryons) in the comoving
(synchronous, CDM-comoving) gauge, in a matter + Lambda (+ curvature) universe without
radiation: P(k, z) = P(k, 0) [D(z)/D(0)]^2 with the scale-independent growth factor D below.
Radiation, massive neutrinos and the gauge dependence on horizon scales are not modelled.

Parameter dictionaries hold
    omega_m   Omega_m at z = 0 (total matter: CDM + baryons [+ massive neutrinos])
    omega_b   Omega_b at z = 0
    omega_l   Omega_Lambda at z = 0 (curvature Omega_k = 1 - omega_m - omega_l)
    h         H0 / (100 km/s/Mpc)
    n_s       primordial spectral index
    sigma8    rms of the linear density in top-hat spheres of 8 Mpc/h at z = 0, or None
    A_s       amplitude of the primordial curvature spectrum at k_p = 0.05/Mpc
    t_cmb     CMB temperature in K (optional, default 2.7255)
    transfer  "eh" (default, Eisenstein & Hu 1998 with baryon oscillations),
              "eh_nowiggle" or "bbks" (optional)
If sigma8 is present and not None the spectrum is normalised to it; otherwise A_s is used.
"""
import functools

import numpy as np
from scipy import integrate, special

C_KMS = 299792.458                 # speed of light in km/s
HUBBLE_DISTANCE = C_KMS/100.0      # c/H0 in Mpc/h
K_PIVOT_MPC = 0.05                 # pivot of A_s in 1/Mpc (not h/Mpc)
T_CMB = 2.7255                     # K (Fixsen 2009)

# Planck 2018 results VI (arXiv:1807.06209), Table 2, column TT,TE,EE+lowE+lensing:
# Omega_b h^2 = 0.02237, H0 = 67.36, Omega_m = 0.3153 (includes one massive neutrino of
# 0.06 eV, Omega_nu h^2 = 0.00064, which the fits here treat as cold matter),
# Omega_Lambda = 0.6847 (= 1 - Omega_m: radiation is dropped so the model stays flat),
# n_s = 0.9649, ln(10^10 A_s) = 3.044, sigma8 = 0.8111.
PLANCK18 = {
    "omega_m": 0.3153,
    "omega_b": 0.02237/0.6736**2,
    "omega_l": 0.6847,
    "h": 0.6736,
    "n_s": 0.9649,
    "sigma8": 0.8111,
    "A_s": float(np.exp(3.044)*1e-10),
    "t_cmb": T_CMB,
}

# GRAMSES papers (Barrera-Hinojosa & Li, arXiv:1905.08890 Sec. 5 and arXiv:2001.07968):
# omega_m, omega_l, h as stated in Part I (cosmo/notes/spec_2001.07968.md, Sec. 6).
# Not stated in either paper: sigma8 = 0.83 and A_s = 2.1e-9 are the values the notes
# infer from the figures of Part II (spec Sec. 3.10, both marked [inferred]); omega_b
# (from Planck 2018 Omega_b h^2 = 0.02237 at h = 0.68), n_s = 0.9649 and t_cmb are
# Planck 2018 values.
GRAMSES = {
    "omega_m": 0.3072,
    "omega_b": 0.02237/0.68**2,
    "omega_l": 0.6928,
    "h": 0.68,
    "n_s": 0.9649,
    "sigma8": 0.83,
    "A_s": 2.1e-9,
    "t_cmb": T_CMB,
}


# ---------------------------------------------------------------------------------------
# transfer functions
# ---------------------------------------------------------------------------------------
def _t0_tilde(q, alpha_c, beta_c):
    """EH98 eq. (19)-(20)."""
    lg = np.log(np.e + 1.8*beta_c*q)
    c = 14.2/alpha_c + 386.0/(1.0 + 69.9*q**1.08)
    return lg/(lg + c*q*q)


def transfer_eh(k, omega_m, omega_b, h, t_cmb=T_CMB, wiggles=True):
    """Matter transfer function of Eisenstein & Hu (1998, ApJ 496, 605), T(k -> 0) = 1.

    k: wavenumber in h/Mpc (array or scalar). omega_m, omega_b: Omega_m and Omega_b at
    z = 0; h: H0/(100 km/s/Mpc); t_cmb in K.
    wiggles=True: the full fit with baryon acoustic oscillations and Silk damping, eqs.
    (2)-(24) of EH98, T = f_b T_b + f_c T_c.
    wiggles=False: the zero-baryon-oscillation ("no-wiggle") form, eqs. (26)-(31), with
    the shape parameter Gamma_eff(k) and the approximate sound horizon of eq. (26).
    """
    k = np.asarray(k, dtype=float)
    kM = k*h                                   # 1/Mpc
    theta = t_cmb/2.7
    wm = omega_m*h*h
    wb = omega_b*h*h
    fb = omega_b/omega_m
    fc = 1.0 - fb

    if not wiggles:
        s = 44.5*np.log(9.83/wm)/np.sqrt(1.0 + 10.0*wb**0.75)                  # Mpc
        a_gam = 1.0 - 0.328*np.log(431.0*wm)*fb + 0.38*np.log(22.3*wm)*fb*fb
        gam = omega_m*h*(a_gam + (1.0 - a_gam)/(1.0 + (0.43*kM*s)**4))
        q = k*theta*theta/gam
        l0 = np.log(2.0*np.e + 1.8*q)
        c0 = 14.2 + 731.0/(1.0 + 62.5*q)
        return l0/(l0 + c0*q*q)

    z_eq = 2.50e4*wm*theta**-4
    k_eq = 7.46e-2*wm*theta**-2                                                 # 1/Mpc
    q = kM/(13.41*k_eq)
    if fb <= 0.0:
        return _t0_tilde(q, 1.0, 1.0)
    b1 = 0.313*wm**-0.419*(1.0 + 0.607*wm**0.674)
    b2 = 0.238*wm**0.223
    z_d = 1291.0*wm**0.251/(1.0 + 0.659*wm**0.828)*(1.0 + b1*wb**b2)
    r_d = 31.5*wb*theta**-4*(1e3/z_d)
    r_eq = 31.5*wb*theta**-4*(1e3/z_eq)
    s = (2.0/(3.0*k_eq))*np.sqrt(6.0/r_eq)*np.log(
        (np.sqrt(1.0 + r_d) + np.sqrt(r_d + r_eq))/(1.0 + np.sqrt(r_eq)))       # Mpc
    k_silk = 1.6*wb**0.52*wm**0.73*(1.0 + (10.4*wm)**-0.95)                     # 1/Mpc

    # CDM part, eqs. (11)-(12), (17)-(18)
    a1 = (46.9*wm)**0.670*(1.0 + (32.1*wm)**-0.532)
    a2 = (12.0*wm)**0.424*(1.0 + (45.0*wm)**-0.582)
    alpha_c = a1**(-fb)*a2**(-fb**3)
    bb1 = 0.944/(1.0 + (458.0*wm)**-0.708)
    bb2 = (0.395*wm)**-0.0266
    beta_c = 1.0/(1.0 + bb1*(fc**bb2 - 1.0))
    ks = kM*s
    f = 1.0/(1.0 + (ks/5.4)**4)
    t_c = f*_t0_tilde(q, 1.0, beta_c) + (1.0 - f)*_t0_tilde(q, alpha_c, beta_c)

    # baryon part, eqs. (14)-(15), (21)-(24)
    y = (1.0 + z_eq)/(1.0 + z_d)
    sq = np.sqrt(1.0 + y)
    g_y = y*(-6.0*sq + (2.0 + 3.0*y)*np.log((sq + 1.0)/(sq - 1.0)))
    alpha_b = 2.07*k_eq*s*(1.0 + r_d)**-0.75*g_y
    beta_node = 8.41*wm**0.435
    beta_b = 0.5 + fb + (3.0 - 2.0*fb)*np.sqrt((17.2*wm)**2 + 1.0)
    with np.errstate(divide="ignore", over="ignore"):
        s_tilde = s/np.cbrt(1.0 + (beta_node/ks)**3)
        t_b = (_t0_tilde(q, 1.0, 1.0)/(1.0 + (ks/5.2)**2)
               + alpha_b/(1.0 + (beta_b/ks)**3)*np.exp(-(kM/k_silk)**1.4))
    t_b = t_b*np.sinc(kM*s_tilde/np.pi)        # j0(k s_tilde)
    return fb*t_b + fc*t_c


def transfer_bbks(k, omega_m, omega_b, h):
    """Transfer function of Bardeen, Bond, Kaiser & Szalay (1986, eq. G3), T(k -> 0) = 1,
    with the shape parameter of Sugiyama (1995):
        q = k / Gamma,  Gamma = Omega_m h exp(-Omega_b - sqrt(2 h) Omega_b / Omega_m),
    k in h/Mpc. No CMB-temperature rescaling of q (the fit is for T = 2.7 K)."""
    k = np.asarray(k, dtype=float)
    gam = omega_m*h*np.exp(-omega_b - np.sqrt(2.0*h)*omega_b/omega_m)
    q = k/gam
    x = 2.34*q
    with np.errstate(invalid="ignore", divide="ignore"):
        lead = np.where(x > 1e-8, np.log1p(x)/np.where(x > 0, x, 1.0), 1.0 - 0.5*x)
    return lead*(1.0 + 3.89*q + (16.1*q)**2 + (5.46*q)**3 + (6.71*q)**4)**-0.25


# ---------------------------------------------------------------------------------------
# linear growth (matter + Lambda + curvature, no radiation)
# ---------------------------------------------------------------------------------------
# Gauss-Jacobi rule for int_0^1 u^(3/2) f(u) du, weights rescaled so that f = 1 is exact
_GJ_X, _GJ_W0 = special.roots_jacobi(96, 0.0, 1.5)
_GJ_U = 0.5*(1.0 + _GJ_X)
_GJ_W = _GJ_W0*(0.4/_GJ_W0.sum())


def _g(a, omega_m, omega_l):
    """a^3 E(a)^2 = Omega_m + Omega_k a + Omega_l a^3, E = H/H0."""
    return omega_m + (1.0 - omega_m - omega_l)*a + omega_l*a**3


def hubble_e(a, omega_m, omega_l):
    """E(a) = H(a)/H0 for matter + Lambda + curvature."""
    a = np.asarray(a, dtype=float)
    return np.sqrt(_g(a, omega_m, omega_l)/a**3)


def growth_factor(a, omega_m, omega_l):
    """Linear growing mode D(a), normalised to D = a at early times (a -> 0).

        D(a) = (5/2) Omega_m E(a) int_0^a da' / (a' E(a'))^3
             = (5/2) Omega_m a sqrt(g(a)) int_0^1 u^(3/2) g(a u)^(-3/2) du,
        g(a) = a^3 E^2 = Omega_m + Omega_k a + Omega_l a^3,  Omega_k = 1 - Omega_m - Omega_l

    (Heath 1977), valid for pressureless matter + Lambda + curvature as long as g > 0 on
    [0, a] (no recollapse). The integral is done with a 96-point Gauss-Jacobi rule for the
    weight u^(3/2); the integrand is analytic in u, and the rule is exact to rounding
    for a <~ 10 (it degrades slowly for a >> 10 in Lambda models). For Omega_m = 1,
    Omega_l = 0 it returns a to rounding. a: scalar or array (dimensionless)."""
    a = np.asarray(a, dtype=float)
    gu = _g(a[..., None]*_GJ_U, omega_m, omega_l)
    integral = gu**-1.5 @ _GJ_W
    return 2.5*omega_m*a*np.sqrt(_g(a, omega_m, omega_l))*integral


def growth_rate(a, omega_m, omega_l):
    """f = d ln D / d ln a for the D of growth_factor, from the exact derivative of the
    integral:  f = [5 Omega_m a / (2 D) - (3/2) Omega_m - Omega_k a] / g(a).
    Equals 1 to rounding for Omega_m = 1, Omega_l = 0, and tends to 1 as a -> 0."""
    a = np.asarray(a, dtype=float)
    d = growth_factor(a, omega_m, omega_l)
    ok = 1.0 - omega_m - omega_l
    with np.errstate(divide="ignore", invalid="ignore"):
        f = (2.5*omega_m*a/d - 1.5*omega_m - ok*a)/_g(a, omega_m, omega_l)
    return np.where(a > 0, f, 1.0)


def omega_m_of_a(a, omega_m, omega_l):
    """Omega_m(a) = Omega_m a^-3 / E(a)^2."""
    a = np.asarray(a, dtype=float)
    return omega_m/_g(a, omega_m, omega_l)


# ---------------------------------------------------------------------------------------
# normalisation and the spectrum
# ---------------------------------------------------------------------------------------
# log grid of the sigma(R) integrals: 1e-6 ... 1e4 h/Mpc, Simpson rule in ln k
_LNK = np.linspace(np.log(1e-6), np.log(1e4), 2**14 + 1)
_KGRID = np.exp(_LNK)


def tophat_window(x):
    """Fourier transform of the spherical top hat, W(x) = 3 (sin x - x cos x) / x^3."""
    x = np.asarray(x, dtype=float)
    small = np.abs(x) < 1e-2
    xs = np.where(small, 1.0, x)
    w = 3.0*(np.sin(xs) - xs*np.cos(xs))/xs**3
    x2 = x*x
    return np.where(small, 1.0 - x2/10.0 + x2*x2/280.0, w)


def transfer(k, params):
    """The transfer function selected by params["transfer"] (default "eh")."""
    kind = params.get("transfer", "eh")
    om, ob, h = params["omega_m"], params["omega_b"], params["h"]
    if kind == "eh":
        return transfer_eh(k, om, ob, h, params.get("t_cmb", T_CMB), True)
    if kind == "eh_nowiggle":
        return transfer_eh(k, om, ob, h, params.get("t_cmb", T_CMB), False)
    if kind == "bbks":
        return transfer_bbks(k, om, ob, h)
    raise ValueError(f"unknown transfer function {kind!r}")


def _key(params):
    return tuple(sorted(params.items()))


@functools.lru_cache(maxsize=128)
def _normalisation(key):
    """(A, D(a=1)) with P(k, z) = A k^n_s T(k)^2 [D(z)/D(0)]^2."""
    p = dict(key)
    om, ol = p["omega_m"], p["omega_l"]
    d0 = float(growth_factor(1.0, om, ol))
    shape = _KGRID**p["n_s"]*transfer(_KGRID, p)**2
    if p.get("sigma8") is not None:
        integrand = _KGRID**3/(2.0*np.pi**2)*shape*tophat_window(8.0*_KGRID)**2
        s2 = integrate.simpson(integrand, x=_LNK)
        amp = p["sigma8"]**2/s2
    elif p.get("A_s") is not None:
        kp = K_PIVOT_MPC/p["h"]                                      # h/Mpc
        amp = (2.0*np.pi**2*(4.0/25.0)*p["A_s"]*kp**(1.0 - p["n_s"])
               * HUBBLE_DISTANCE**4*d0**2/om**2)
    else:
        raise ValueError("params need sigma8 or A_s")
    return float(amp), d0


def linear_power(k, z, params):
    """Linear matter power spectrum P(k, z) in (Mpc/h)^3, k in h/Mpc.

        P(k, z) = A k^n_s T(k)^2 [D(z)/D(0)]^2,  D from growth_factor (no radiation).

    Normalisation:
    - sigma8 (if params["sigma8"] is not None): A such that
      sigma^2(8 Mpc/h, z=0) = int dln k Delta^2(k) W^2(8 k) = sigma8^2, with the top-hat
      window W and the integral done by Simpson's rule on a log grid (1e-6..1e4 h/Mpc,
      16385 points).
    - A_s otherwise, through the matter-era relation between the comoving density and
      the primordial curvature perturbation R, delta = (2/5) k^2 T(k) D(a) R / (Omega_m H0^2):
          Delta^2(k, z) = (4/25) A_s (k/k_p)^(n_s - 1) (k c/H0)^4 T(k)^2 D(a)^2 / Omega_m^2,
      k_p = 0.05/Mpc, c/H0 = 2997.92458 Mpc/h, D normalised to a at early times (as
      growth_factor), P = 2 pi^2 Delta^2 / k^3.
    """
    k = np.asarray(k, dtype=float)
    amp, d0 = _normalisation(_key(params))
    a = 1.0/(1.0 + z)
    dz = float(growth_factor(a, params["omega_m"], params["omega_l"]))/d0
    return amp*k**params["n_s"]*transfer(k, params)**2*dz*dz


def sigma_r(r, z, params):
    """rms linear density contrast in spherical top hats of radius r (Mpc/h) at
    redshift z: sigma^2(r) = int dln k Delta^2(k, z) W^2(k r), on the log grid of the
    normalisation. r: scalar or array."""
    r = np.asarray(r, dtype=float)
    d2 = _KGRID**3*linear_power(_KGRID, z, params)/(2.0*np.pi**2)
    w = tophat_window(r[..., None]*_KGRID)
    return np.sqrt(integrate.simpson(d2*w*w, x=_LNK, axis=-1))
