"""Reference integrator for the two Langevin equations of arXiv:2401.08530, section V.

One patch in the uniform-field gauge, time = background e-folds N_b, units M_Pl = 1.
Locators refer to kb-data/raw/arxiv/2401.08530/v2/src/Stochastic_Inflation.tex (SI.tex).

  e-folds  (SI.tex:806):     dN/dN_b = sqrt(1 + (alpha^2 - 1)(1 - eps1/3))
  lapse    (SI.tex:825-826): dalpha/dN_b = 3 alpha (sqrt(...) - 1) + alpha^3 <S^2>
                             + (-3 + eps1 + eps2/2) alpha (alpha^2 - 1) + alpha^3 S
  noise    (SI.tex:838):     sqrt<S^2> = (3 / 2 pi) H / sqrt(2 eps1), on the background
  background (SI.tex:847):   V = V0 (phi >= phi_c), V0 [3 x^2 - 2 x^3] (x = phi/phi_c < 1),
                             phi* = 10, dphi/dN* = -2.0001, H* = 1e-5, phi_c = 9.056
  slow-roll signs (SI.tex:919): eps_{i+1} = -d ln eps_i / dN (eps2 = +6 in USR).

We integrate D = N - N_b instead of N (dD/dN_b = sqrt(...) - 1, written without
cancellation). This is a zero-dimensional stochastic ODE, a semi-analytic reference in the
sense of decision 0010; it is not a simulation of numerical relativity.
"""
import numpy as np

PHI_C = 9.056
PHI0 = 10.0
U0 = -2.0001
HSTAR = 1.0e-5
NOISE_ON = 2.0
NOISE_OFF = 6.0


def V0_of(u0=U0, hstar=HSTAR):
    """V0 from the Friedmann constraint at N_b = 0: H^2 (3 - u^2/2) = V (phi* > phi_c)."""
    return hstar ** 2 * (3.0 - 0.5 * u0 ** 2)


def Vn(phi):
    """V / V0."""
    x = phi / PHI_C
    return np.where(phi >= PHI_C, 1.0, 3.0 * x ** 2 - 2.0 * x ** 3)


def dVn(phi):
    """(dV/dphi) / V0."""
    x = phi / PHI_C
    return np.where(phi >= PHI_C, 0.0, 6.0 * (x - x ** 2) / PHI_C)


def bg_rhs(phi, u):
    """Background in e-folds: phi'' + (3 - eps1) phi' + (3 - eps1) V'/V = 0,
    using H^2 = V / (3 - eps1), eps1 = u^2/2."""
    e1 = 0.5 * u * u
    return u, -(3.0 - e1) * (u + dVn(phi) / Vn(phi))


def bg_derived(phi, u, V0):
    e1 = 0.5 * u * u
    _, du = bg_rhs(phi, u)
    e2 = -2.0 * du / u                      # -d ln eps1 / dN
    H = np.sqrt(V0 * Vn(phi) / (3.0 - e1))
    return e1, e2, H


def background(scheme="euler", h=0.01, T=12.0, u0=U0, sub=1):
    """Background on the grid N = 0, h, 2h, ..., T.

    scheme 'euler': forward Euler with step h (the paper's tuning, see JOURNAL entry 0);
    scheme 'rk4': classical Runge-Kutta with step h/sub (converged 'exact' solution)."""
    n = int(round(T / h))
    N = np.arange(n + 1) * h
    phi = np.empty(n + 1)
    u = np.empty(n + 1)
    phi[0], u[0] = PHI0, u0
    p, v = PHI0, u0
    hs = h / sub
    for i in range(n):
        for _ in range(sub):
            if scheme == "euler":
                a, b = bg_rhs(p, v)
                p, v = p + hs * a, v + hs * b
            elif scheme == "rk4":
                k1 = bg_rhs(p, v)
                k2 = bg_rhs(p + 0.5 * hs * k1[0], v + 0.5 * hs * k1[1])
                k3 = bg_rhs(p + 0.5 * hs * k2[0], v + 0.5 * hs * k2[1])
                k4 = bg_rhs(p + hs * k3[0], v + hs * k3[1])
                p = p + hs / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
                v = v + hs / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            else:
                raise ValueError(scheme)
            p, v = float(p), float(v)
        phi[i + 1], u[i + 1] = p, v
    V0 = V0_of(u0)
    e1, e2, H = bg_derived(phi, u, V0)
    return dict(scheme=scheme, h=h, sub=sub, u0=u0, V0=V0, N=N, phi=phi, u=u,
                eps1=e1, eps2=e2, H=H)


def crossing(bg):
    """First N_b where phi < phi_c (linear interpolation), or None."""
    phi, N = bg["phi"], bg["N"]
    idx = np.nonzero(phi < PHI_C)[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    return float(N[i - 1] + (phi[i - 1] - PHI_C) / (phi[i - 1] - phi[i]) * (N[i] - N[i - 1]))


def tune_u0(Ncross=3.045, h=0.01, sub=10, T=4.0):
    """dphi/dN* for which the converged background crosses phi_c at Ncross (bisection)."""
    lo, hi = -2.01, -2.0001       # lo crosses early, hi never crosses
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        nc = crossing(background("rk4", h, T, mid, sub))
        if nc is not None and nc < Ncross:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def sigma_of(e1, H):
    """Noise amplitude sqrt<S^2>, SI.tex:838 (M_Pl = 1)."""
    return 3.0 / (2.0 * np.pi) * H / np.sqrt(2.0 * e1)


def interp_bg(bg, Nq):
    """Background quantities at times Nq: state (phi, u) interpolated linearly between
    the grid points (the Euler trajectory is piecewise linear), then eps1, eps2, H."""
    phi = np.interp(Nq, bg["N"], bg["phi"])
    u = np.interp(Nq, bg["N"], bg["u"])
    e1, e2, H = bg_derived(phi, u, bg["V0"])
    return e1, e2, H


def _sq1m1(x):
    """sqrt(1 + x) - 1 without cancellation."""
    return x / (np.sqrt(1.0 + x) + 1.0)


def drift(alpha, e1, e2, s2, ito_term=True, a3=True):
    """Drift of (alpha, D) as printed; s2 = <S^2> (zero where the noise is off)."""
    x = (alpha * alpha - 1.0) * (1.0 - e1 / 3.0)
    s = _sq1m1(x)
    fa = 3.0 * alpha * s + (-3.0 + e1 + 0.5 * e2) * alpha * (alpha * alpha - 1.0)
    if ito_term:
        fa = fa + (alpha ** 3 if a3 else 1.0) * s2
    return fa, s


def diffusion(alpha, sig, a3=True):
    return (alpha ** 3 if a3 else 1.0) * sig


def simulate(bg, npaths=50000, h=0.01, N0=NOISE_ON, T=NOISE_OFF, noise_on=NOISE_ON,
             noise_off=NOISE_OFF, scheme="heun", ito_term=True, a3=True, seed=1,
             record=(3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0), nkeep=100, cap=50.0):
    """Integrate npaths realisations from alpha = 1, D = 0 at N_b = N0 to T.

    scheme 'heun'      : Stratonovich Heun (predictor-corrector) on the printed equation;
    scheme 'em_ito'    : Euler-Maruyama on the Ito-equivalent drift (+ 1/2 g dg/dalpha);
    scheme 'em_naive'  : Euler-Maruyama on the printed equation (Ito reading).
    The noise acts on steps that start in [noise_on, noise_off). A path whose |alpha| exceeds
    `cap` or becomes non-finite is frozen as dead (NaN) and counted.
    Returns per-step moments over the live paths, samples at the record times, and the
    first nkeep trajectories."""
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
    nst = int(round((T - N0) / h))
    Ns = N0 + np.arange(nst + 1) * h
    e1, e2, H = interp_bg(bg, Ns)
    sig = sigma_of(e1, H)
    s2 = sig ** 2
    on = (Ns[:-1] >= noise_on - 1e-9) & (Ns[:-1] < noise_off - 1e-9)

    alpha = np.ones(npaths)
    D = np.zeros(npaths)
    live = np.ones(npaths, bool)
    rec_idx = {int(round((r - N0) / h)): r for r in record if N0 <= r <= T + 1e-9}
    samples = {}
    keep_a = np.empty((nst + 1, nkeep))
    keep_D = np.empty((nst + 1, nkeep))
    mom = {k: np.empty(nst + 1) for k in
           ("mean_a", "std_a", "skew_a", "kurt_a", "mean_D", "std_D", "skew_D", "kurt_D",
            "med_absa", "max_absa", "med_absD", "nlive", "min_a")}

    def moments(i):
        a = alpha[live] - 1.0
        d = D[live]
        for tag, x in (("a", a), ("D", d)):
            m = x.mean()
            c = x - m
            v = (c * c).mean()
            sd = np.sqrt(v)
            mom["mean_" + tag][i] = m
            mom["std_" + tag][i] = sd
            mom["skew_" + tag][i] = (c ** 3).mean() / sd ** 3 if sd > 0 else 0.0
            mom["kurt_" + tag][i] = (c ** 4).mean() / v ** 2 - 3.0 if sd > 0 else 0.0
        mom["med_absa"][i] = np.median(np.abs(a))
        mom["max_absa"][i] = np.abs(a).max()
        mom["med_absD"][i] = np.median(np.abs(d))
        mom["min_a"][i] = alpha[live].min()
        mom["nlive"][i] = live.sum()
        keep_a[i] = alpha[:nkeep] - 1.0
        keep_D[i] = D[:nkeep]
        if i in rec_idx:
            samples[rec_idx[i]] = (alpha - 1.0).copy(), D.copy()

    moments(0)
    sq = np.sqrt(h)
    for i in range(nst):
        if on[i]:
            dW = sq * rng.standard_normal(npaths)
            s2a, s2b, sga, sgb = s2[i], s2[i + 1], sig[i], sig[i + 1]
        else:
            dW = 0.0
            s2a = s2b = sga = sgb = 0.0
        fa, fD = drift(alpha, e1[i], e2[i], s2a, ito_term, a3)
        ga = diffusion(alpha, sga, a3)
        if scheme == "heun":
            ap = alpha + fa * h + ga * dW
            fa2, fD2 = drift(ap, e1[i + 1], e2[i + 1], s2b, ito_term, a3)
            ga2 = diffusion(ap, sgb, a3)
            anew = alpha + 0.5 * (fa + fa2) * h + 0.5 * (ga + ga2) * dW
            Dnew = D + 0.5 * (fD + fD2) * h
        elif scheme == "em_ito":
            corr = 1.5 * alpha ** 5 * s2a if a3 else 0.0
            anew = alpha + (fa + corr) * h + ga * dW
            Dnew = D + fD * h
        elif scheme == "em_naive":
            anew = alpha + fa * h + ga * dW
            Dnew = D + fD * h
        else:
            raise ValueError(scheme)
        bad = live & ~(np.isfinite(anew) & (np.abs(anew) < cap))
        alpha = np.where(live, anew, alpha)
        D = np.where(live, Dnew, D)
        live &= ~bad
        alpha[~live] = np.nan
        D[~live] = np.nan
        moments(i + 1)
    return dict(N=Ns, sigma=sig, eps1=e1, eps2=e2, H=H, moments=mom, samples=samples,
                keep_a=keep_a, keep_D=keep_D, ndead=int((~live).sum()))


def linear_moments(bg, h=0.001, N0=NOISE_ON, T=NOISE_OFF, noise_on=NOISE_ON,
                   noise_off=NOISE_OFF):
    """Covariance of the linearised system (reference for the linear regime):
    da = (-3 + eps1 + eps2) a dN + sigma dW,  dD = (1 - eps1/3) a dN."""
    nst = int(round((T - N0) / h))
    Ns = N0 + np.arange(nst + 1) * h
    e1, e2, H = interp_bg(bg, Ns)
    sig = sigma_of(e1, H)
    lam = -3.0 + e1 + e2
    c = 1.0 - e1 / 3.0
    on = (Ns >= noise_on - 1e-9) & (Ns < noise_off - 1e-9)
    y = np.zeros(3)                      # Vaa, VaD, VDD
    out = np.zeros((nst + 1, 3))

    def f(y, j):
        s2 = sig[j] ** 2 if on[j] else 0.0
        return np.array([2 * lam[j] * y[0] + s2, lam[j] * y[1] + c[j] * y[0],
                         2 * c[j] * y[1]])

    for j in range(nst):                 # Heun on the moment ODE (fine step)
        k1 = f(y, j)
        k2 = f(y + h * k1, j + 1)
        y = y + 0.5 * h * (k1 + k2)
        out[j + 1] = y
    return Ns, np.sqrt(np.maximum(out[:, 0], 0)), np.sqrt(np.maximum(out[:, 2], 0))
