"""Own background and Mukhanov-Sasaki references of the slow-roll case (g1verify).

Independent of tracks/E-stoch-inf/spec/ref/ and of python/nrpic/sf_inflation.py.  Derived
here from the sources:
- Physical units (Mpl = 1), quadratic potential V = m^2 phi^2/2, P1 Table I
  (PRD_v2.tex:405-424: eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl at N0), potential-position
  fixing of P2 (main_V2PRD.tex:399-405), checked by hand against Friedmann and KG:
    V(phi0) = H0^2 (3 - eps1),  phi0 = -p (3 - eps1)/(phi_N (3 - eps1 - eps2/2)),  phi_N = +sqrt(2 eps1).
- Code units (SPEC 2.5): G = 1, time unit 1/H*, phi_c = phi/sqrt(8 pi), a* = 1, box 2 pi,
  dk = 1; 3 H^2 = 8 pi (Pi^2/2 + V), dPi/dt = -3 H Pi - V', dH/dt = -4 pi Pi^2.
- Mukhanov-Sasaki in cosmic time: R'' + (3H + dln eps1/dt) R' + (k/a)^2 R = 0 with
  eps1 = 4 pi Pi^2/H^2 (code units).  Deformed (FLRW-lattice) equation of BZ
  (Manuscript.tex:192-194, 220-222, sigma = 0) rewritten for R = f/z in e-folds by hand:
    R_NN + (3 - e1 - e2) R_N + [(k/aH)^2 + 2 e1 (3 - e1 - e2)] R = 0
  (eta_BZ = e1 + e2/2 with e2 = -dln e1/dN, the sign of P1), i.e. in cosmic time an extra
  term + 2 e1 (3 - e1 - e2) H^2 R.
- Window of P1:503-506: W = (1 + tanh[s ln(sigma a H/k)])/2, s = 5, sigma = 1, with the
  Friedmann a, H (level 0).
"""
import numpy as np
from scipy.integrate import solve_ivp

FOURPI = 4.0 * np.pi
EIGHTPI = 8.0 * np.pi


# ---------------------------------------------------------------- physical units, Mpl = 1
def quadratic_fix(eps1=0.01, eps2=-0.02, h0=1.0e-5, p=2):
    phin = np.sqrt(2.0 * eps1)
    phi0 = -abs(p * (3.0 - eps1) / (phin * (3.0 - eps1 - 0.5 * eps2)))
    v0 = h0 ** 2 * (3.0 - eps1)
    lam = v0 / abs(phi0) ** p          # V = lam phi^p ; m^2 = 2 lam for p = 2
    return dict(phi0=phi0, phin0=phin, lam=lam, m=np.sqrt(2.0 * lam), h0=h0)


def phys_background(fix, n_end=13.5, rtol=1e-13, atol=1e-16):
    m2 = fix["m"] ** 2

    def rhs(n, y):
        phi, phin = y
        e1 = 0.5 * phin * phin
        h2 = 0.5 * m2 * phi * phi / (3.0 - e1)
        return [phin, -(3.0 - e1) * phin - m2 * phi / h2]

    sol = solve_ivp(rhs, (0.0, n_end), [fix["phi0"], fix["phin0"]], method="DOP853",
                    rtol=rtol, atol=atol, dense_output=True)
    return sol


def phys_state(bg, fix, n):
    phi, phin = bg.sol(n)
    e1 = 0.5 * phin ** 2
    h = np.sqrt(0.5 * fix["m"] ** 2 * phi ** 2 / (3.0 - e1))
    phinn = -(3.0 - e1) * phin - fix["m"] ** 2 * phi / h ** 2
    e2 = -2.0 * phinn / phin
    return dict(phi=phi, phin=phin, H=h, eps1=e1, eps2=e2)


def to_code(fix, st):
    """Code-unit background at N* from the physical state there (a* = 1)."""
    hs = st["H"]
    return dict(phi0=st["phi"] / np.sqrt(EIGHTPI), pi0=hs * st["phin"] / (np.sqrt(EIGHTPI) * hs),
                mass=fix["m"] / hs, hstar=hs)


def bd_modes_phys(bg, fix, nstar, kphys, rtol=1e-11):
    """R_k(N*) and dR/dt(N*) [physical units] from Bunch-Davies data at N0 = 0 (quasi de
    Sitter form v = e^{-ik tau}(1 - i/(k tau))/sqrt(2k), tau = -1/((1-eps1) a H))."""
    out = []
    for k in np.atleast_1d(kphys):
        def st(n):
            return phys_state(bg, fix, n)
        s0 = st(0.0)
        a0 = 1.0 * np.exp(-nstar)          # a* = 1
        ah = a0 * s0["H"]
        tau = -1.0 / ((1.0 - s0["eps1"]) * ah)
        v = np.exp(-1j * k * tau) / np.sqrt(2 * k) * (1.0 - 1j / (k * tau))
        dvdtau = np.exp(-1j * k * tau) / np.sqrt(2 * k) * (-1j * k * (1.0 - 1j / (k * tau)) + 1j / (k * tau ** 2))
        z = a0 * s0["phin"]
        zn_z = 1.0 - 0.5 * s0["eps2"]
        R = v / z
        RN = (dvdtau / ah) / z - zn_z * R

        def rhs(n, y):
            s = st(n)
            a = np.exp(n - nstar)
            R = y[0] + 1j * y[1]
            RN = y[2] + 1j * y[3]
            RNN = -(3.0 - s["eps1"] - s["eps2"]) * RN - (k / (a * s["H"])) ** 2 * R
            return [RN.real, RN.imag, RNN.real, RNN.imag]

        sol = solve_ivp(rhs, (0.0, nstar), [R.real, R.imag, RN.real, RN.imag], method="DOP853",
                        rtol=rtol, atol=1e-14 * abs(R))
        y = sol.y[:, -1]
        sN = st(nstar)
        out.append((y[0] + 1j * y[1], (y[2] + 1j * y[3]) * sN["H"]))
    return out


# ---------------------------------------------------------------- code units
class CodeBackground:
    """Friedmann + Klein-Gordon in code time from (phi0, pi0, mass), a(0) = 1."""

    def __init__(self, phi0, pi0, mass, t_end=9.0, rtol=1e-13, atol=1e-16):
        self.m2 = mass * mass
        h0 = np.sqrt(EIGHTPI / 3.0 * (0.5 * pi0 ** 2 + 0.5 * self.m2 * phi0 ** 2))

        def rhs(t, y):
            phi, pi, h, lna = y
            return [pi, -3.0 * h * pi - self.m2 * phi, -FOURPI * pi * pi, h]

        self.sol = solve_ivp(rhs, (0.0, t_end), [phi0, pi0, h0, 0.0], method="DOP853",
                             rtol=rtol, atol=atol, dense_output=True)
        self.h0 = h0

    def __call__(self, t):
        phi, pi, h, lna = self.sol.sol(t)
        e1 = FOURPI * pi ** 2 / h ** 2
        dpi = -3.0 * h * pi - self.m2 * phi
        dlne1 = 2.0 * dpi / pi + 2.0 * FOURPI * pi ** 2 / h
        e2 = -dlne1 / h
        con = h ** 2 - EIGHTPI / 3.0 * (0.5 * pi ** 2 + 0.5 * self.m2 * phi ** 2)
        return dict(phi=phi, Pi=pi, H=h, K=-3.0 * h, lna=lna, a=np.exp(lna), eps1=e1,
                    eps2=e2, dlne1=dlne1, friedmann=con)


def window(k, a, h, s=5.0, sigma=1.0):
    return 0.5 * (1.0 + np.tanh(s * np.log(sigma * a * h / k)))


def ms_code(bg, k, R0, dR0, t_eval, deformed=False, rtol=1e-12):
    """Integrate the (full or deformed) MS equation in code time for wave numbers k (array)
    from complex R0, dR0 at t = 0; returns R(t_eval), dR(t_eval), arrays (len(t), len(k))."""
    k = np.asarray(k, dtype=float)
    nk = k.size
    R0 = np.asarray(R0, dtype=complex)
    dR0 = np.asarray(dR0, dtype=complex)
    y0 = np.concatenate([R0.real, R0.imag, dR0.real, dR0.imag])
    k2 = k * k

    def rhs(t, y):
        s = bg(t)
        R = y[:2 * nk]
        dR = y[2 * nk:]
        fr = 3.0 * s["H"] + s["dlne1"]
        w2 = np.tile(k2 / s["a"] ** 2, 2)
        if deformed:
            w2 = w2 + 2.0 * s["eps1"] * (3.0 - s["eps1"] - s["eps2"]) * s["H"] ** 2
        return np.concatenate([dR, -fr * dR - w2 * R])

    scale = np.concatenate([np.abs(R0), np.abs(R0), np.abs(dR0) + np.abs(R0), np.abs(dR0) + np.abs(R0)])
    t_eval = np.atleast_1d(np.asarray(t_eval, dtype=float))
    sol = solve_ivp(rhs, (0.0, float(t_eval.max())), y0, method="DOP853", rtol=rtol,
                    atol=1e-3 * rtol * scale, t_eval=t_eval)
    if not sol.success:
        raise RuntimeError(sol.message)
    Y = sol.y.T
    R = Y[:, :nk] + 1j * Y[:, nk:2 * nk]
    dR = Y[:, 2 * nk:3 * nk] + 1j * Y[:, 3 * nk:]
    return R, dR


def read_mode_file(path):
    d = np.loadtxt(path, comments="#", ndmin=2)
    n2 = d[:, 0].astype(int)
    return n2, d[:, 1] + 1j * d[:, 2], d[:, 3] + 1j * d[:, 4]


def crossing_time(bg, k, t_hi=9.0):
    """Code time and e-fold of a H = k (horizon crossing; sigma = 1)."""
    from scipy.optimize import brentq
    out = []
    for kk in np.atleast_1d(k):
        f = lambda t: np.log(bg(t)["a"] * bg(t)["H"] / kk)
        if f(0.0) >= 0:
            out.append((0.0, 0.0))
            continue
        t = brentq(f, 0.0, t_hi, xtol=1e-13)
        out.append((t, float(bg(t)["lna"])))
    return np.array(out)
