"""Analytic criteria for primordial-black-hole formation in an early matter era (A-pre-2).

Every function names the equation it implements as ``<arXiv id>:<line>``, the line of the
TeX source under ``kb-data/raw/arxiv/<id>/<version>/src`` (1609.01588 v2
apj_nonsphericalpbh.tex, 1707.03595 v4 Spin_PBH.tex, 2211.13950 v3 MD_threshold10.tex,
2507.18312 v3 Main.tex, 2508.10070 v1 main.tex).

Shared conventions (G = c = 1, Einstein-de Sitter background, a ~ t^(2/3)):

* Horizon entry t_H of the region: its unperturbed physical radius equals the Hubble
  radius, a(t_H) q = 1/H(t_H) [1609.01588:478, 1707.03595:760, 2211.13950:342,
  2507.18312:302, 2508.10070:250]; then M = 1/(2 H_H) = R_H / 2 [1609.01588:484-489,
  2508.10070:256].
* Amplitude ``delta``: linear growing-mode density contrast of the region at t_H.
  1609.01588 delta_L(t_i) (438, 495, normalisation b/a = a/a(t_i), 611); 1707.03595
  delta_{s,H} (1255-1258); 2211.13950 tilde delta_ent (275); 2507.18312 delta_m (184-187,
  equal to the top-hat density contrast at a = 1, 171 with epsilon = 1); 2508.10070
  sigma_h nu (peak height at the horizon entry of the region, 322-325). Treating these as
  one number is [JUDGEMENT]: they agree in definition up to the shape of the profile
  (top hat, ball with uniform deformation, peak centre).
* Deformation eigenvalues at t_H, alpha >= beta >= gamma, alpha + beta + gamma = delta;
  ellipticity e = (alpha - gamma)/(2 delta) and prolateness p = (alpha - 2 beta + gamma)
  /(2 delta), so (alpha, beta, gamma) = delta/3 (1+3e+p, 1-2p, 1-3e+p). This is the mapping
  of 2609.14218 MDPBH.tex:908 with k^2/(aH)^2 absorbed into delta.
* E(k) is the complete elliptic integral of the second kind with modulus k, E(0) = pi/2,
  E(1) = 1 [1609.01588:579-581]; scipy's ``ellipe`` takes m = k^2.
"""
import numpy as np
from scipy import integrate, optimize, special

PI = np.pi
SQ5 = np.sqrt(5.0)


def ellipE(k):
    """Complete elliptic integral of the second kind of modulus k (E(0)=pi/2, E(1)=1)."""
    return special.ellipe(np.clip(np.square(k), 0.0, 1.0))


def eigen_from_dep(delta, e, p):
    """(alpha, beta, gamma) from amplitude, ellipticity and prolateness (module docstring)."""
    return (delta / 3.0 * (1 + 3 * e + p), delta / 3.0 * (1 - 2 * p),
            delta / 3.0 * (1 - 3 * e + p))


def dep_from_eigen(a, b, c):
    """Inverse of eigen_from_dep."""
    d = a + b + c
    return d, (a - c) / (2 * d), (a - 2 * b + c) / (2 * d)


# ---------------------------------------------------------------------------------------
# 1609.01588 (Harada, Yoo, Kohri, Nakao, Jhingan): Zel'dovich approximation + hoop
# conjecture + Doroshkevich distribution.  Assumptions [VERIFIED, 461-468, 381-403]:
# Newtonian EdS, Zel'dovich approximation extrapolated to the first caustic, deformation
# uniform over a Lagrangian ball of radius q, alpha > 0, hoop C <~ 4 pi M of the pancake.
# ---------------------------------------------------------------------------------------
def hoop_h(a, b, c):
    """h(alpha,beta,gamma) = (2/pi)(alpha-gamma)/alpha^2 E(sqrt(1-((alpha-beta)/(alpha-gamma))^2))
    [1609.01588:604-607]; black hole iff h <~ 1 [596-598]; alpha > 0 required [468]."""
    a, b, c = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float),
                                  np.asarray(c, float))
    span = a - c
    safe = np.where(span > 0, span, 1.0)
    ratio = np.where(span > 0, (a - b) / safe, 0.0)
    E = ellipE(np.sqrt(np.clip(1 - ratio ** 2, 0, 1)))
    with np.errstate(divide="ignore", invalid="ignore"):
        h = 2 / PI * span / a ** 2 * E
    return np.where(a > 0, h, np.inf)


def hoop_threshold_delta(e, p):
    """Amplitude above which h <= 1 at fixed (e, p): delta_th = (36/pi) e E(k)/(1+3e+p)^2 with
    k = sqrt(1 - ((e+p)/(2e))^2). Derived here from 1609.01588:604-607 and eigen_from_dep;
    equals (12/5) hat-h(e,p) of 2609.14218 MDPBH.tex:918."""
    e = np.asarray(e, float)
    p = np.asarray(p, float)
    safe = np.where(e > 0, e, 1.0)
    k = np.sqrt(np.clip(1 - ((e + p) / (2 * safe)) ** 2, 0, 1))
    return np.where(e > 0, 36 / PI * e * ellipE(k) / (1 + 3 * e + p) ** 2, 0.0)


def zeldovich_turnaround_a(alpha):
    """a(t_f)/a(t_H) = 1/(2 alpha) along the first axis [1609.01588:503 with 611]."""
    return 1.0 / (2.0 * alpha)


def zeldovich_collapse_a(alpha):
    """a(t_c)/a(t_H) = 1/alpha, first caustic (pancake) [1609.01588:537 with 611]."""
    return 1.0 / alpha


def doroshkevich_w(a, b, c, sigma):
    """Doroshkevich density of ordered eigenvalues, sigma_3 = sigma/sqrt(5)
    [1609.01588:641-645, 699]."""
    s3 = sigma / SQ5
    Q = (a * a + b * b + c * c) - 0.5 * (a * b + b * c + c * a)
    return (-27.0 / (8 * SQ5 * PI * s3 ** 6) * np.exp(-3.0 / (5 * s3 ** 2) * Q)
            * (a - b) * (b - c) * (c - a))


def doroshkevich_sample(n, sigma, rng):
    """Ordered eigenvalues of a Gaussian symmetric tensor with <D11^2> = s3^2,
    <D11 D22> = <D12^2> = s3^2/3 (trace variance sigma^2 = 5 s3^2, 1609.01588:699). The
    eigenvalue law of this tensor is the Doroshkevich law [BACKGROUND]; used to check
    doroshkevich_w and the integrals independently."""
    s3 = sigma / SQ5
    g0 = rng.standard_normal(n)
    g = rng.standard_normal((n, 3))
    o = rng.standard_normal((n, 3))
    D = np.zeros((n, 3, 3))
    for i in range(3):
        D[:, i, i] = s3 * np.sqrt(2.0 / 3.0) * g[:, i] + s3 / np.sqrt(3.0) * g0
    for (i, j), col in zip(((0, 1), (1, 2), (0, 2)), range(3)):
        D[:, i, j] = D[:, j, i] = s3 / np.sqrt(3.0) * o[:, col]
    ev = np.linalg.eigvalsh(D)[:, ::-1]
    return ev[:, 0], ev[:, 1], ev[:, 2]


def _beta0_tu(sigma, delta_th=0.0, epsrel=1e-7):
    """Exact rewrite of the triple integral of 1609.01588:706-708 (and, with delta_th > 0,
    of 1707.03595:1304-1308 and 2211.13950:637) in the variables (t, u, z) of
    1609.01588:1257-1299, with the z integral done in closed form (z^5 exp(-A z^2) from
    z_low to infinity = (2 + 2X + X^2) exp(-X)/(2 A^3), X = A z_low^2). The density
    contrast is delta = alpha+beta+gamma = 3 t z (x = t z, 1609.01588:670, 1259)."""
    s3 = sigma / SQ5

    def integrand_t(t, u, Ek):
        A = 0.9 * (t / s3) ** 2 + 2 * (u / s3) ** 2 + 1.5 / s3 ** 2
        zl = 4 / PI * Ek / (t + 2 * u / 3 + 1) ** 2
        if delta_th > 0:
            if t <= 0:
                return 0.0
            zl = max(zl, delta_th / (3 * t))
        X = A * zl * zl
        # A^-3 / s3^6 = (A s3^2)^-3: the prefactor 1/s3^6 of 1609.01588:1296 absorbed
        return (2 + 2 * X + X * X) / (A * s3 * s3) ** 3 * np.exp(-X)

    def inner(u):
        Ek = float(ellipE(np.sqrt(1 - (u + 0.5) ** 2)))
        t0 = -1 - 2 * u / 3
        neg = 0.0
        if delta_th <= 0:
            neg = integrate.quad(integrand_t, t0, 0.0, args=(u, Ek), epsabs=0,
                                 epsrel=epsrel, limit=200)[0]
        # t > 0: the weight sits at t ~ 1/s3 for small sigma (1609.01588:1306-1309)
        f = lambda tau: integrand_t(tau / s3, u, Ek) / s3
        cuts = [0.0, 1.0]
        if delta_th > 0:
            # kinks where z* = delta_th/(3t): pi d t^2 + (2 pi d c - 12 E) t + pi d c^2 = 0
            c = 2 * u / 3 + 1
            qa, qb, qc = PI * delta_th, 2 * PI * delta_th * c - 12 * Ek, PI * delta_th * c * c
            disc = qb * qb - 4 * qa * qc
            if disc > 0:
                for r in ((-qb - np.sqrt(disc)) / (2 * qa), (-qb + np.sqrt(disc)) / (2 * qa)):
                    if r > 0:
                        cuts.append(r * s3)
        cuts = sorted(set(cuts))
        pos = sum(integrate.quad(f, lo, hi, epsabs=0, epsrel=epsrel, limit=400)[0]
                  for lo, hi in zip(cuts[:-1], cuts[1:]))
        pos += integrate.quad(f, cuts[-1], np.inf, epsabs=0, epsrel=epsrel, limit=400)[0]
        return (1 - 4 * u * u) * (neg + pos)

    val = integrate.quad(inner, -0.5, 0.5, epsabs=0, epsrel=epsrel, limit=200)[0]
    return 27.0 / (2 * SQ5 * PI) * val


def beta0_hoop(sigma):
    """Production probability with the hoop criterion, full expression
    [1609.01588:706-708], evaluated exactly through _beta0_tu."""
    return _beta0_tu(sigma)


def Ebar():
    """E-bar defined by E-bar^-5 = (3/2) int_{-1/2}^{1/2} (1-2u)(1+2u) E^-5 du
    [1609.01588:1338]; the paper quotes 1.182 [1341]."""
    f = lambda u: (1 - 2 * u) * (1 + 2 * u) * float(ellipE(np.sqrt(1 - (u + 0.5) ** 2))) ** -5
    return (1.5 * integrate.quad(f, -0.5, 0.5, epsabs=0, epsrel=1e-12)[0]) ** (-0.2)


def beta0_hoop_semianalytic_coeff(Eb=None):
    """Coefficient c in beta0 ~ c sigma^5 for sigma << 1:
    7 5^3 pi^(9/2) / (2^9 3^6 sqrt(10)) E-bar^-5 [1609.01588:1328-1331]; the paper quotes
    0.05556 [764]. Eb = pi/2 and Eb = 1 give the bounds 0.01338 and 0.1280 [771, 840, 853]."""
    Eb = Ebar() if Eb is None else Eb
    return 7 * 5 ** 3 * PI ** 4.5 / (2 ** 9 * 3 ** 6 * np.sqrt(10)) * Eb ** -5


def beta0_khlopov_polnarev_coeff():
    """Coefficient of the Khlopov-Polnarev estimate beta0 ~ c chi^5 for small chi:
    (27/(8 sqrt5 pi)) int_0^inf da e^{-9a^2/10} int (a-b) db int (a-c)(b-c) dc
    [1609.01588:926-931]; the paper quotes 0.02. The inner integrals give (a chi)^5/30."""
    f = lambda a: a ** 5 * np.exp(-0.9 * a * a)
    return 27 / (8 * SQ5 * PI) / 30.0 * integrate.quad(f, 0, np.inf)[0]


def beta0_radiation(sigma, dc=0.4135, dmax=2.0 / 3.0):
    """Radiation-era comparison erfc(dc/(sqrt2 s)) - erfc(dmax/(sqrt2 s))
    [1609.01588:1020-1029, values 1040-1041]."""
    return special.erfc(dc / (np.sqrt(2) * sigma)) - special.erfc(dmax / (np.sqrt(2) * sigma))


# ---------------------------------------------------------------------------------------
# 1707.03595 (Harada, Yoo, Kohri, Nakao): angular momentum and Kerr bound.
# Assumptions [VERIFIED]: Newtonian linear theory with growing modes only (360-364);
# angular momentum frozen at maximum expansion t_m = t_H delta^(-3/2) (784-797, 894);
# hypothesis |L1| ~ delta, |L2| ~ sigma delta (849-868); Kerr bound a* <= 1 as the
# condition for direct collapse (948); calculus with I = O(1) (567).
# ---------------------------------------------------------------------------------------
def spin_a1(q, delta):
    """First-order Kerr parameter a*(1) = (2/5) sqrt(3/5) q delta^(-1/2) [1707.03595:904]."""
    return 0.4 * np.sqrt(0.6) * q * np.asarray(delta, float) ** -0.5


def spin_a2(I, sigmaH, delta):
    """Second-order Kerr parameter a*(2) = (2/5) I sigma_H delta^(-3/2) [1707.03595:906]."""
    return 0.4 * I * sigmaH * np.asarray(delta, float) ** -1.5


def spin_threshold(q, I, sigmaH, tend_over_tH=np.inf):
    """delta_th = max(delta_th(1), delta_th(2), delta_fd) [1707.03595:953-960, 925] with
    delta_th(1) = 12 q^2/125, delta_th(2) = (2 I sigma_H/5)^(2/3), delta_fd = (t_H/t_end)^(2/3).
    Returns the three and their maximum."""
    d1 = 12.0 / 125.0 * q * q
    d2 = (0.4 * I * sigmaH) ** (2.0 / 3.0)
    dfd = 0.0 if not np.isfinite(tend_over_tH) else tend_over_tH ** (-2.0 / 3.0)
    return max(d1, d2, dfd), d1, d2, dfd


def spin_qc(I, sigmaH):
    """q_c = sqrt(2/3) (5/2)^(7/6) I^(1/3) sigma_H^(1/3) [1707.03595:979]; ~2.4 [72]."""
    return np.sqrt(2.0 / 3.0) * 2.5 ** (7.0 / 6.0) * I ** (1 / 3) * sigmaH ** (1 / 3)


def spin_pdf_2nd(a, I, sigmaH):
    """Unnormalised f_BH(2)(a) [1707.03595:1118-1121]."""
    a = np.asarray(a, float)
    return a ** (-5 / 3) * np.exp(-0.5 * sigmaH ** (-2 / 3) * (0.4 * I) ** (4 / 3) * a ** (-4 / 3))


def spin_pdf_1st(a, q, sigmaH):
    """Unnormalised f_BH(1)(a) [1707.03595:1127-1128]."""
    a = np.asarray(a, float)
    return a ** -3 * np.exp(-0.5 / sigmaH ** 2 * (9 * 16 / 5 ** 6) * q ** 4 * a ** -4)


def spin_pdf_mode_2nd(I, sigmaH):
    """Most probable spin of f_BH(2), min(1, (4C/5)^(3/4)), C = (2I/5)^(4/3)/(2 sigma^(2/3));
    derived from 1707.03595:1118-1121 (d ln f/da = 0). The paper reads 0.63 at sigma_H = 0.1
    and the extreme value below sigma_H ~ 0.04 [1146-1150]."""
    C = 0.5 * sigmaH ** (-2 / 3) * (0.4 * I) ** (4 / 3)
    return min(1.0, (0.8 * C) ** 0.75)


def beta0_spin_semianalytic(delta_th, sigmaH, Eb=None):
    """beta0 ~ 5 sqrt5 pi^4 / 6^9 E-bar^-5 delta_th^9 / sigma^4 exp(-delta_th^2/(2 sigma^2))
    [1707.03595:1325-1329], for sigma_H << 1 and delta_th >> sigma_H."""
    Eb = Ebar() if Eb is None else Eb
    return (5 * SQ5 * PI ** 4 / 6.0 ** 9 * Eb ** -5 * delta_th ** 9 / sigmaH ** 4
            * np.exp(-delta_th ** 2 / (2 * sigmaH ** 2)))


def beta0_spin(sigmaH, delta_th):
    """Numerical beta0 with theta(delta - delta_th) theta(1-h) w [1707.03595:1304-1308]."""
    return _beta0_tu(sigmaH, delta_th=delta_th)


def quadrupole_q(A1, A2, A3):
    """q = sqrt(2(mu1^2 - 3 mu2)) / ((3/5) V r0^2) for a uniform ellipsoid with i_k = V A_k^2/5,
    r0 = (A1 A2 A3)^(1/3) [1707.03595:641-645, 712-716]."""
    V = 4 * PI / 3 * A1 * A2 * A3
    i = np.array([A1 * A1, A2 * A2, A3 * A3]) * V / 5
    mu1 = i.sum()
    mu2 = i[0] * i[1] + i[1] * i[2] + i[2] * i[0]
    r0 = (A1 * A2 * A3) ** (1 / 3)
    return np.sqrt(max(2 * (mu1 ** 2 - 3 * mu2), 0.0)) / (0.6 * V * r0 * r0)


# ---------------------------------------------------------------------------------------
# 2211.13950 (Harada, Kohri, Sasaki, Terada, Yoo): velocity dispersion.
# Assumptions [VERIFIED]: two separated scales k > k_PBH (209-245); dispersion shared over
# the region at t_* and growing adiabatically, sigma_v ~ 1/R (330-334); halt when the
# crossing time equals the free-fall time (348-355); order-unity factors dropped (375).
# ---------------------------------------------------------------------------------------
def vd_halt_radius(sigv_star, R_star, R_ent):
    """R_halt = (4/9) sigma_v(t*)^2 (R(t*)/R_ent)^2 R_ent [2211.13950:352]."""
    return 4.0 / 9.0 * sigv_star ** 2 * (R_star / R_ent) ** 2 * R_ent


def vd_collapse_adiabatic(sigvR_over_M):
    """Black hole iff sigma_v(t*) R(t*) < 3 M (= 3/2 R_ent) [2211.13950:357-359, 715]."""
    return sigvR_over_M < 3.0


def vd_case(k_ratio, delta_small, delta_big):
    """'I' iff k^2 delta_ent > ktilde^2 tilde-delta_ent, else 'II' [2211.13950:297-301]."""
    return "I" if k_ratio ** 2 * delta_small > delta_big else "II"


def vd_sigma_cr(mu, L):
    """ln sigma_cr = mu L^2 - 4 L, L = ln(k_min/ktilde) [2211.13950:496-498]."""
    return np.exp(mu * L * L - 4 * L)


def vd_delta_th(sigma0, mu, L):
    """Necessary condition for formation, tilde-delta_ent > delta_th(sigma0, mu, k_min)
    [2211.13950:551-563] for the log-normal spectrum [482-488]."""
    sigma0 = np.asarray(sigma0, float)
    lo = np.exp(-0.4 * mu * L * L) * (sigma0 * np.exp(-L)) ** 0.4
    with np.errstate(invalid="ignore"):
        hi = np.exp(-2.0 / mu * (2 + np.sqrt(4 + mu * np.log(sigma0))))
    return np.where(sigma0 < vd_sigma_cr(mu, L), lo, hi)


def vd_merge_point(delta):
    """Corner (k/ktilde, sigma) = (delta^(-1/2), delta^2) of the non-formation region
    [2211.13950:466-468]."""
    return delta ** -0.5, delta ** 2


# ---------------------------------------------------------------------------------------
# 2507.18312 (Ebrahimian, Abolhasani, Mirbabayi): profile shape, shell crossing, velocity
# dispersion from typical perturbations zeta_rms. Assumptions [VERIFIED]: rare peaks nearly
# spherical with zeta_rms perturbations on top (117-121); LTB dust before shell crossing
# (206-215); parametric estimates with O(1) coefficients set to one (238, 322, 585).
# ---------------------------------------------------------------------------------------
def tophat_K(delta_m, r_m=1.0):
    """Top-hat curvature profile inside: K = (5/3) delta_m / r_m^2 [2507.18312:291-297]."""
    return 5.0 / 3.0 * delta_m / r_m ** 2


def tophat_ltb(delta_m, theta, r_m=1.0):
    """Exact LTB/closed-FLRW top hat [2507.18312:211-214] with H0 r_m = 1 and
    a = (3 t/(2 r_m))^(2/3) [302]: returns (t, a(t), R(r_m, t)/r_m)."""
    K = tophat_K(delta_m, r_m)
    H0 = 1.0 / r_m
    R = H0 ** 2 / (2 * K) * r_m * (1 - np.cos(theta))
    t = H0 ** 2 / (2 * K ** 1.5) * (theta - np.sin(theta))
    a = (1.5 * t / r_m) ** (2.0 / 3.0)
    return t, a, R / r_m


def tophat_Rmax(delta_m):
    """R_max = 3 r_m/(5 delta_m) [2507.18312:304]."""
    return 3.0 / (5.0 * delta_m)


def tophat_amax(delta_m):
    """a(t_max) = 3 (6 pi)^(2/3) / (20 delta_m) ~ 1.06/delta_m [2507.18312:276, 308]."""
    return 3 * (6 * PI) ** (2 / 3) / 20.0 / delta_m


def tophat_bBH(delta_m):
    """b_BH = R/R_max at R = 2GM = r_m: 5 delta_m/3 [2507.18312:314-316]."""
    return 5.0 / 3.0 * delta_m


def tophat_aBH(delta_m):
    """Scale factor (in units of a_H) at which the contracting exact top hat reaches
    R = 2M = r_m: solve (1 - cos theta)/2 = b_BH on (pi, 2 pi). From 2507.18312:211-214, 316."""
    b = tophat_bBH(delta_m)
    if b >= 1:
        return np.nan
    th = 2 * PI - np.arccos(1 - 2 * b)
    return tophat_ltb(delta_m, th)[1]


def tophat_acoll(delta_m):
    """Scale factor of the central singularity theta = 2 pi [2507.18312:222-225]."""
    return tophat_ltb(delta_m, 2 * PI)[1]


def profile_threshold(zeta_rms, A2=None, n=None):
    """Formation threshold delta_th:
    top hat (A2 = None, n = None): zeta^(2/5) [2507.18312:336-339];
    flat atypical profile with A_2..A_{2n-2} = 0: zeta^((4n-6)/(10n)) [409-412];
    profile with A2 and A4 = 1: A2^(1/3) if zeta^(3/10) < A2 < 1, zeta^(1/10) if
    A2 < zeta^(3/10) [401-408]; a typical peak (A2 >= 1) needs delta_m ~ 1 [242]."""
    if A2 is None and n is None:
        return zeta_rms ** 0.4
    if n is not None:
        return zeta_rms ** ((4 * n - 6) / (10 * n))
    if A2 >= 1:
        return 1.0
    return A2 ** (1 / 3) if A2 > zeta_rms ** 0.3 else zeta_rms ** 0.1


def profile_spin_rms(zeta_rms, delta_m):
    """a_rms ~ zeta_rms^2 / delta_m^(5/2) [2507.18312:630-631]; ~ zeta^(7/4) at
    delta_m ~ zeta^(1/10) [633-635]."""
    return zeta_rms ** 2 / np.asarray(delta_m, float) ** 2.5


def virial_bmin(s_max, GM_over_rmax):
    """Minimum compression with an initial dispersion s (3D rms, s^2 = 3 sigma_1D^2,
    2507.18312:502-503) at maximum expansion, from the virial theorem 2K + U = 0 with
    U = -(3/5) GM^2/r_max: b_min = (5/3) s^2 r_max/(GM) [517-520, 542]."""
    return 5.0 / 3.0 * s_max ** 2 / GM_over_rmax


def shot_noise_bmin(N, coeff=1.2):
    """Poisson noise of N particles in a top hat at rest: b_min ~ 1.2 N^(-1/3)
    [2507.18312:483-489, coefficient from the fit quoted at 489]."""
    return coeff * np.asarray(N, float) ** (-1 / 3)


def zeta_peak_gaussian(delta_m):
    """Gaussian K(r): zeta(0) = (5e/12) delta_m ~ 1.13 delta_m [2507.18312:188]."""
    return 5 * np.e / 12 * delta_m


# ---------------------------------------------------------------------------------------
# 2508.10070 (Ye, Gong, Harada, Kang, Kohri, Saito, Yoo): peak theory + Zel'dovich + hoop.
# Assumptions [VERIFIED]: Gaussian field, overdense region bounded by delta = 0 around a
# peak, approximated by the ellipsoid of the quadratic expansion (229-243); Zel'dovich
# collapse driven by the tidal tensor at the peak (210-222); hoop C <~ 4 pi M (317); spin
# frozen at t_c, first order in D (482, 689).
# ---------------------------------------------------------------------------------------
def pancake_hoop_general(lam, Dt, sigma_h_star):
    """General criterion x_l <~ x_th = pi nu d_max sigma_h*/(E(e) (l1 l2 l3)^(1/2))
    [2508.10070:309-331]. lam: shape eigenvalues (frame of -delta_ij/sigma2); Dt: rescaled
    tidal tensor D/sigma0 in that frame (3x3, trace nu = D_A, 790). Returns
    (x_l, x_th, e, d_max, collapse)."""
    lam = np.asarray(lam, float)
    Dt = np.asarray(Dt, float)
    nu = np.trace(Dt)
    d = np.linalg.eigvalsh(Dt)
    dmax = d.max()
    T = np.eye(3) - Dt / dmax                      # T(t_c), sigma0(t_c) = 1/d_max [306]
    Mq = T @ np.diag(1 / lam) @ T                  # [309]
    ev = np.sort(np.linalg.eigvalsh(Mq))[::-1]
    xl, xs = np.sqrt(max(ev[0], 0)), np.sqrt(max(ev[1], 0))
    e = np.sqrt(max(1 - (xs / xl) ** 2, 0)) if xl > 0 else 0.0
    xth = PI * nu * dmax * sigma_h_star / (float(ellipE(e)) * np.sqrt(np.prod(lam)))
    return xl, xth, e, dmax, xl <= xth


def hoop_peak_ratio(a, b, c):
    """Monochromatic peak (shape eigenvalues = tidal eigenvalues, w = 0, 582-586):
    criterion (2/pi)(l1-l3)E(e)/l1^2 <~ l3^(1/3)/(l1 l2)^(1/6) sigma_h(q0) [596-598] with
    e^2 = 1 - ((l1-l2)/(l1-l3))^2 l3/l2 [593]. Written for the deformation eigenvalues at the
    horizon entry of the region, alpha_i = sigma_h(q0) lambda_i (322-325), the criterion is
    H <= 1 with H = (2/pi)(a-c) E(e)/a^2 (a b)^(1/6)/c^(1/3) (scale-free rewrite, derived
    here). Needs c > 0 (a density peak, 854)."""
    a, b, c = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float),
                                  np.asarray(c, float))
    span = a - c
    safe = np.where(span > 0, span, 1.0)
    ratio = np.where(span > 0, (a - b) / safe, 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        e2 = np.clip(1 - ratio ** 2 * c / b, 0, 1)
        H = 2 / PI * span * ellipE(np.sqrt(e2)) / a ** 2 * (a * b) ** (1 / 6) / c ** (1 / 3)
    return np.where(c > 0, H, np.nan)


def hoop_peak_threshold_delta(e, p):
    """Amplitude above which hoop_peak_ratio <= 1 at fixed (e, p) (H scales as 1/delta)."""
    a, b, c = eigen_from_dep(1.0, e, p)
    return hoop_peak_ratio(a, b, c)


def spin_tidal_sq(lam, w, nu, sigma_h_star, dmax):
    """a~^2(t_c) = (2/25) l1 l2 l3/(nu sigma_h* d_max^3) [w1^2 (1/l2-1/l3)^2 + w2^2 (1/l3-1/l1)^2
    + w3^2 (1/l1-1/l2)^2] [2508.10070:486-493]."""
    l1, l2, l3 = lam
    w1, w2, w3 = w
    br = (w1 ** 2 * (1 / l2 - 1 / l3) ** 2 + w2 ** 2 * (1 / l3 - 1 / l1) ** 2
          + w3 ** 2 * (1 / l1 - 1 / l2) ** 2)
    return 2.0 / 25.0 * l1 * l2 * l3 / (nu * sigma_h_star * dmax ** 3) * br


MONO_NORM = 4 * PI / 3 * 1.5 ** 3.5 * (5 / PI) ** 2.5   # (4 pi/3) x prefactor of 891-898


def _mono_weight(l1, l2, l3):
    nu = l1 + l2 + l3
    ex = np.exp(-0.5 * nu ** 2 - 1.25 * ((l1 - l2) ** 2 + (l2 - l3) ** 2 + (l1 - l3) ** 2))
    return ex * l1 * l2 * l3 * (l1 - l2) * (l2 - l3) * (l1 - l3)


def beta_monochromatic(sigma_star, epsrel=1e-6):
    """PBH mass fraction and number for a monochromatic spectrum: eq. 384-388 with the peak
    density 891-898, mass M/M* = (2 nu)^(3/2)/(l1 l2 l3)^(1/2) (381) and the criterion
    (2/pi)(l1-l3)E(e)/l1^2 <= 2 nu sigma*/sqrt(l1 l2) (596-598 with 322-325).
    Variables l3 = w, Delta = l1 - l3, s = (l1-l2)/Delta. Returns (beta, N_BH, Mbar/M*)."""

    def cond(w, s, D):
        """<= 0 where a black hole forms; vectorised in D."""
        l1, l2, l3 = w + D, w + (1 - s) * D, w
        e2 = np.clip(1 - s * s * l3 / l2, 0.0, 1.0)
        lhs = 2 / PI * D * ellipE(np.sqrt(e2)) / l1 ** 2
        return lhs - 2 * (l1 + l2 + l3) * sigma_star / np.sqrt(l1 * l2)

    Dgrid = np.concatenate([[0.0], np.geomspace(1e-12, 30.0, 400)])

    def dens(D, w, s, mass):
        l1, l2, l3 = w + D, w + (1 - s) * D, w
        f = _mono_weight(l1, l2, l3) * D            # Jacobian d^3 lambda = Delta dw dDelta ds
        if mass:
            f *= (2 * (l1 + l2 + l3)) ** 1.5 / np.sqrt(l1 * l2 * l3)
        return f

    def inner(s, w, mass):
        # intervals of Delta where cond <= 0: scan on a log grid, refine the roots
        Dg = Dgrid
        with np.errstate(divide="ignore", invalid="ignore"):
            cg = cond(w, s, Dg)
        cg[0] = -1.0
        tot = 0.0
        start = 0.0
        inside = True
        for i in range(1, len(Dg)):
            if (cg[i] <= 0) != inside:
                r = optimize.brentq(lambda D: cond(w, s, D), Dg[i - 1], Dg[i], xtol=1e-14,
                                    rtol=1e-12) if Dg[i - 1] > 0 else Dg[i]
                if inside:
                    tot += integrate.quad(dens, start, r, args=(w, s, mass), epsabs=0,
                                          epsrel=epsrel, limit=200)[0]
                else:
                    start = r
                inside = not inside
        if inside:
            tot += integrate.quad(dens, start, Dg[-1], args=(w, s, mass), epsabs=0,
                                  epsrel=epsrel, limit=200)[0]
        return tot

    def outer(w, mass):
        return integrate.quad(inner, 0.0, 1.0, args=(w, mass), epsabs=0, epsrel=epsrel,
                              limit=100)[0]

    res = []
    for mass in (True, False):
        v = integrate.quad(outer, 0.0, 1.0, args=(mass,), epsabs=0, epsrel=epsrel,
                           limit=100)[0]
        v += integrate.quad(outer, 1.0, 6.0, args=(mass,), epsabs=0, epsrel=epsrel,
                            limit=100)[0]
        res.append(MONO_NORM * v)
    beta, nbh = res
    return beta, nbh, beta / nbh


def beta_mono_smallsigma_coeff(Eb=None):
    """Small-sigma limit derived here from beta_monochromatic: near-spherical peaks with
    Delta <= 3 pi lambda^2 sigma*/E, giving beta ~ c sigma*^5 with
    c = MONO_NORM 6^(3/2) [Gamma(7)/2 (2/9)^7] (3 pi)^5/5 E-bar^-5/6. In units of
    sigma-bar = 6 sigma* (2508.10070:654) the paper quotes beta ~ 1.08 sigma-bar^5 [657]."""
    Eb = Ebar() if Eb is None else Eb
    lam_int = 0.5 * special.gamma(7) * (2.0 / 9.0) ** 7
    return MONO_NORM * 6 ** 1.5 * lam_int * (3 * PI) ** 5 / 5 * Eb ** -5 / 6
