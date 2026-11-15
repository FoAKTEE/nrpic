"""Bowen-York punctures: conformal extrinsic curvature, the regular correction of the
conformal factor, and the correction tables read by the problem generator nrpic_cf
(``athenak/src/pgen/nrpic/nrpic_bowen_york.hpp``).

Conformally flat slice, gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij, K = 0. Each
puncture at x_c with momentum P and spin S contributes [Brandt & Bruegmann,
arXiv:gr-qc/9703066v2, main.tex lines 116-122, Eq. (KPJ)]

    Abar^ij = 3/(2 r^2) [P^i n^j + P^j n^i - (delta^ij - n^i n^j) P.n]
            + 3/r^3 [(S x n)^i n^j + (S x n)^j n^i],      n = (x - x_c)/r,

which is traceless and divergence free, so the momentum constraint holds for any
number of punctures. The Hamiltonian constraint is lap psi = -(1/8) psi^-7 Abar^2
(same source, line 72). With psi = psi_BL + u, psi_BL = 1 + sum_c m_c/(2 r_c), the
regular part obeys (same source, lines 207-215, with u there equal to 1 + u here)

    lap u = -(1/8) Abar_ij Abar^ij (psi_BL + u)^-7,     u -> 0 at infinity.

For one puncture with P and S along one axis the source is axisymmetric and even in
mu = n.axis:

    Abar^2 = 9 P^2 (1 + 2 mu^2)/(2 r^4) + 18 S^2 (1 - mu^2)/r^6,

and :func:`solve_axisym` solves the equation by multipoles, u = sum_l u_l(r) P_l(mu),

    u_l(r) = [ r^-(l+1) int_0^r s^(l+2) g_l ds + r^l int_r^inf s^(1-l) g_l ds ]/(2l+1),

with g_l the multipoles of g = (1/8) Abar^2 (psi_BL + u)^-7, iterated to convergence
(one pass from u = 0 is the solution to second order in P and S). The closed form of
that second-order solution, including the cross term of a puncture with momentum and
spin that are not parallel [Lousto & Zlochower, arXiv:0711.1165v2, second.tex lines
222-271, Eqs. (approx_j), (approx_p), (approx_c)], is :func:`approx_u`; the problem
generator evaluates the same expressions for ``comp<c>_corr = approx``.

Units G = c = 1. Nothing here evolves anything: reference solutions and table writer.
"""

import argparse
import math

import numpy as np
from scipy.integrate import cumulative_simpson
from scipy.interpolate import CubicSpline

__all__ = ["abar", "abar2", "psi_bl", "approx_u", "approx_u2p", "solve_axisym",
           "write_table", "read_table", "eval_table", "hamiltonian_residual",
           "adm_mass_approx"]

# Taylor coefficients of u_2^P(R) about R = 0, powers R^2 .. R^17 (derived from the closed
# form with sympy; the closed form cancels catastrophically for small R)
_U2P_SERIES = {2: 1.0 / 400.0, 5: -1.0 / 32.0, 6: 7.0 / 48.0, 7: -21.0 / 50.0,
               8: 21.0 / 22.0, 9: -15.0 / 8.0, 10: 693.0 / 208.0, 11: -11.0 / 2.0,
               12: 429.0 / 50.0, 13: -819.0 / 64.0, 14: 5005.0 / 272.0,
               15: -77.0 / 3.0, 16: 663.0 / 19.0, 17: -4641.0 / 100.0}
_U2P_SWITCH = 0.15


def _disp(x, pos):
    d = np.asarray(x, dtype=float) - np.asarray(pos, dtype=float)
    r = np.sqrt(np.sum(d * d, axis=-1))
    return d, r


def abar(x, pos, P=(0.0, 0.0, 0.0), S=(0.0, 0.0, 0.0)):
    """Conformal Bowen-York curvature Abar_ij (flat indices) of one puncture at the
    points x (..., 3). Returns an array (..., 3, 3)."""
    P = np.asarray(P, dtype=float)
    S = np.asarray(S, dtype=float)
    d, r = _disp(x, pos)
    n = d / r[..., None]
    pn = n @ P
    sxn = np.cross(np.broadcast_to(S, n.shape), n)
    eye = np.eye(3)
    nn = n[..., :, None] * n[..., None, :]
    a = (1.5 / r**2)[..., None, None] * (
        P[:, None] * n[..., None, :] + n[..., :, None] * P[None, :]
        - (eye - nn) * pn[..., None, None])
    a = a + (3.0 / r**3)[..., None, None] * (
        sxn[..., :, None] * n[..., None, :] + n[..., :, None] * sxn[..., None, :])
    return a


def abar2(x, punctures):
    """Abar_ij Abar^ij of a list of punctures, each a dict with keys pos, P, S."""
    tot = 0.0
    for p in punctures:
        tot = tot + abar(x, p["pos"], p.get("P", (0, 0, 0)), p.get("S", (0, 0, 0)))
    return np.sum(tot * tot, axis=(-1, -2))


def psi_bl(x, punctures):
    """Brill-Lindquist conformal factor 1 + sum m/(2 r)."""
    psi = 1.0
    for p in punctures:
        _, r = _disp(x, p["pos"])
        psi = psi + 0.5 * p["m"] / r
    return psi


def approx_u2p(R):
    """Quadrupole radial function u_2^P(R) of a boosted puncture, R = 2 r/m
    [arXiv:0711.1165v2, second.tex lines 250-256]."""
    R = np.asarray(R, dtype=float)
    out = np.empty_like(R)
    small = R < _U2P_SWITCH
    Rs = R[small]
    acc = np.zeros_like(Rs)
    for k, c in _U2P_SERIES.items():
        acc += c * Rs**k
    out[small] = acc
    Rb = R[~small]
    ell = 1.0 / (1.0 + Rb)
    out[~small] = (15 * ell + 132 * ell**2 + 53 * ell**3 + 96 * ell**4 + 82 * ell**5
                   + 84 * ell**5 / Rb + 84 * np.log(ell) / Rb**2) / (80.0 * Rb)
    return out


def approx_u(x, pos, m, P=(0.0, 0.0, 0.0), S=(0.0, 0.0, 0.0)):
    """Correction u of one puncture to second order in P and S, closed form
    [arXiv:0711.1165v2, second.tex lines 222-271]."""
    P = np.asarray(P, dtype=float)
    S = np.asarray(S, dtype=float)
    d, r = _disp(x, pos)
    R = 2.0 * r / m
    ell = 1.0 / (1.0 + R)
    rs = np.where(r > 0.0, r, 1.0)
    calP = 2.0 * P / m
    calJ = 4.0 * S / m**2
    u = np.zeros_like(r)
    P2 = float(calP @ calP)
    J2 = float(calJ @ calJ)
    if P2 > 0.0:
        mu = (d @ P) / (math.sqrt(float(P @ P)) * rs)
        u0 = (5.0 / 32.0) * (ell - 2 * ell**2 + 2 * ell**3 - ell**4 + 0.2 * ell**5)
        u = u + P2 * (u0 + approx_u2p(R) * 0.5 * (3 * mu**2 - 1))
    if J2 > 0.0:
        mu = (d @ S) / (math.sqrt(float(S @ S)) * rs)
        u0 = (ell + ell**2 + ell**3 - 4 * ell**4 + 2 * ell**5) / 40.0
        u2 = -ell**5 / 20.0
        u = u + J2 * (u0 + u2 * R**2 * 0.5 * (3 * mu**2 - 1))
    if P2 > 0.0 and J2 > 0.0:
        u = u + ((2.0 * d / m) @ np.cross(calP, calJ)) * (1 + 5 * R + 10 * R**2) \
            * ell**5 / 80.0
    return u


def adm_mass_approx(m, P=0.0, S=0.0):
    """ADM mass of one corrected puncture to second order,
    m + (5/8) P^2/m + (2/5) S^2/m^3 [arXiv:0711.1165v2, second.tex lines 285-287]."""
    return m + 0.625 * P**2 / m + 0.4 * S**2 / m**3


def _legendre(lmax, mu):
    """P_l(mu) for l = 0..lmax, array (lmax+1, ...)."""
    mu = np.asarray(mu, dtype=float)
    out = np.empty((lmax + 1,) + mu.shape)
    out[0] = 1.0
    if lmax >= 1:
        out[1] = mu
    for l in range(2, lmax + 1):
        out[l] = ((2 * l - 1) * mu * out[l - 1] - (l - 1) * out[l - 2]) / l
    return out


def solve_axisym(m, P=0.0, S=0.0, lmax=8, nonlinear=True, nr=6001, rmin=1.0e-5,
                 rmax=1.0e5, nmu=48, tol=1.0e-13, maxit=200):
    """Correction u(r, mu) of one puncture of bare mass m with momentum P and spin S
    along the same axis, by multipoles l = 0, 2, .., lmax.

    Returns a dict: r (logarithmic grid, in units of length), lvals, ul (len(lvals), nr),
    u0_centre, monopole (r u_0 at infinity), m_adm = m + 2 monopole, iterations.
    nonlinear=False gives the second-order solution (source evaluated with u = 0).
    """
    lvals = list(range(0, lmax + 1, 2))
    x = np.linspace(math.log(rmin * m), math.log(rmax * m), nr)
    r = np.exp(x)
    mu, w = np.polynomial.legendre.leggauss(nmu)
    pl = _legendre(lmax, mu)                       # (lmax+1, nmu)
    a2 = (4.5 * P**2 * (1.0 + 2.0 * mu[None, :]**2) / r[:, None]**4
          + 18.0 * S**2 * (1.0 - mu[None, :]**2) / r[:, None]**6)
    psi0 = 1.0 + 0.5 * m / r
    u = np.zeros((nr, nmu))
    ul = np.zeros((len(lvals), nr))
    mono = 0.0
    u0c = 0.0
    it = 0
    for it in range(1, maxit + 1):
        g = 0.125 * a2 / (psi0[:, None] + u)**7
        unew = np.zeros_like(u)
        for q, l in enumerate(lvals):
            gl = 0.5 * (2 * l + 1) * (g * pl[l][None, :]) @ w
            # int_0^r s^(l+2) g_l ds and int_r^inf s^(1-l) g_l ds, in x = ln s
            f1 = r**(l + 3) * gl
            f2 = r**(2 - l) * gl
            # power-law ends: g_l ~ r^p at the inner end, r^-q at the outer end
            p_in = (math.log(abs(gl[1]) + 1e-300) - math.log(abs(gl[0]) + 1e-300)) \
                / (x[1] - x[0])
            q_out = -(math.log(abs(gl[-1]) + 1e-300) - math.log(abs(gl[-2]) + 1e-300)) \
                / (x[-1] - x[-2])
            i1 = cumulative_simpson(f1, x=x, initial=0.0) + f1[0] / (l + 3 + p_in)
            tail = f2[-1] / (q_out + l - 2) if q_out + l - 2 > 0 else 0.0
            c2 = cumulative_simpson(f2, x=x, initial=0.0)
            i2 = (c2[-1] - c2) + tail
            ul[q] = (r**(-(l + 1)) * i1 + r**l * i2) / (2 * l + 1)
            unew += ul[q][:, None] * pl[l][None, :]
            if l == 0:
                mono = i1[-1] + f1[-1] / (q_out - 3) if q_out > 3 else i1[-1]
                u0c = i2[0]
        err = float(np.max(np.abs(unew - u)))
        u = unew
        if not nonlinear or err < tol:
            break
    return {"r": r, "lvals": lvals, "ul": ul, "u0_centre": u0c, "monopole": mono,
            "m_adm": m + 2.0 * mono, "iterations": it, "m": m, "P": P, "S": S,
            "nonlinear": nonlinear}


def write_table(fname, sol, dr, rlast, axis=None, comment=""):
    """Write the multipoles of a :func:`solve_axisym` solution on the uniform grid
    r_k = k dr, k = 0..N-1, N = round(rlast/dr) + 1, in the puncture-correction format
    of docs/FORMATS.md. ``axis`` (3 numbers) is written to the header when given;
    otherwise the reader uses the direction of the momentum (of the spin for P = 0)."""
    n = int(round(rlast / dr)) + 1
    rg = dr * np.arange(n)
    lvals = sol["lvals"]
    cols = np.zeros((len(lvals), n))
    tails = []
    xs = np.log(sol["r"])
    for q, l in enumerate(lvals):
        spl = CubicSpline(xs, sol["ul"][q])
        cols[q, 1:] = spl(np.log(rg[1:]))
        cols[q, 0] = sol["u0_centre"] if l == 0 else 0.0
        # decay exponent beyond the table, measured over the last tenth of it
        k0 = max(1, int(0.9 * (n - 1)))
        a, b = abs(cols[q, k0]), abs(cols[q, n - 1])
        tail = math.log(a / b) / math.log(rg[n - 1] / rg[k0]) if a > 0 and b > 0 \
            else l + 1.0
        tails.append(tail)
    with open(fname, "w") as f:
        f.write("# nrpic puncture correction table (python/nrpic/bowen_york.py)\n")
        f.write("# format = mp1\n")
        f.write("# l = " + " ".join(str(l) for l in lvals) + "\n")
        f.write("# tail = " + " ".join(f"{t:.6f}" for t in tails) + "\n")
        if axis is not None:
            f.write("# axis = %.17g %.17g %.17g\n" % tuple(axis))
        f.write(f"# mass = {sol['m']:.17g}\n# momentum = {sol['P']:.17g}\n"
                f"# spin = {sol['S']:.17g}\n# nonlinear = {int(sol['nonlinear'])}\n")
        f.write(f"# m_adm = {sol['m_adm']:.12g}\n# u_centre = {sol['u0_centre']:.12g}\n")
        if comment:
            f.write("# " + comment + "\n")
        f.write("# columns = r " + " ".join(f"u_{l}" for l in lvals) + "\n")
        for k in range(n):
            f.write(f"{rg[k]:.10e} " + " ".join(f"{cols[q, k]:.16e}"
                                                 for q in range(len(lvals))) + "\n")
    return rg, cols, tails


def read_table(fname):
    """Read a puncture-correction table. Returns a dict r, cols, lvals, tail, axis,
    meta (the other header entries as strings)."""
    lvals, tail, axis = None, None, None
    meta = {}
    rows = []
    with open(fname) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                body = s[1:].strip()
                if "=" in body:
                    key, val = (t.strip() for t in body.split("=", 1))
                    if key == "l":
                        lvals = [int(t) for t in val.split()]
                    elif key == "tail":
                        tail = [float(t) for t in val.split()]
                    elif key == "axis":
                        axis = [float(t) for t in val.split()]
                    else:
                        meta[key] = val
                continue
            rows.append([float(t) for t in s.split()])
    a = np.array(rows)
    if lvals is None:
        raise ValueError("no '# l = ...' header line in " + fname)
    if tail is None:
        tail = [l + 1.0 for l in lvals]
    return {"r": a[:, 0], "cols": a[:, 1:].T, "lvals": lvals, "tail": tail, "axis": axis,
            "meta": meta}


def eval_table(tab, x, pos, axis):
    """Evaluate a table at points x the way the problem generator does: four-point
    Lagrange interpolation on the uniform grid, power-law continuation beyond it."""
    d, r = _disp(x, pos)
    axis = np.asarray(axis, dtype=float)
    axis = axis / math.sqrt(float(axis @ axis))
    mu = np.where(r > 0.0, (d @ axis) / np.where(r > 0.0, r, 1.0), 0.0)
    pl = _legendre(max(tab["lvals"]), mu)
    rg = tab["r"]
    n = len(rg)
    dr = rg[1] - rg[0]
    xi = r / dr
    i = np.clip(np.floor(xi).astype(int), 1, n - 3)
    s = xi - i
    wm = -s * (s - 1) * (s - 2) / 6.0
    w0 = (s + 1) * (s - 1) * (s - 2) / 2.0
    w1 = -(s + 1) * s * (s - 2) / 2.0
    w2 = (s + 1) * s * (s - 1) / 6.0
    u = np.zeros_like(r)
    for q, l in enumerate(tab["lvals"]):
        c = tab["cols"][q]
        inside = wm * c[i - 1] + w0 * c[i] + w1 * c[i + 1] + w2 * c[i + 2]
        outside = c[-1] * (rg[-1] / np.maximum(r, rg[-1]))**tab["tail"][q]
        u = u + np.where(r >= rg[-1], outside, inside) * pl[l]
    return u


def hamiltonian_residual(x, punctures, u=None, lap_u=None):
    """Hamiltonian residual H = R + K^2 - K_ij K^ij of conformally flat Bowen-York data
    with psi = psi_BL + u at the points x:

        H = -8 psi^-5 lap(u) - psi^-12 Abar^2,

    which is -psi_BL^-12 Abar^2 without a correction (u = None). ``lap_u`` is the flat
    Laplacian of u at the same points."""
    a2 = abar2(x, punctures)
    psi = psi_bl(x, punctures)
    if u is None:
        return -a2 / psi**12
    psi = psi + u
    return -8.0 * lap_u / psi**5 - a2 / psi**12


def _main():
    ap = argparse.ArgumentParser(description="Correction table of one Bowen-York "
                                 "puncture with momentum and spin along one axis")
    ap.add_argument("--mass", type=float, required=True, help="bare mass m")
    ap.add_argument("--momentum", type=float, default=0.0, help="P along the axis")
    ap.add_argument("--spin", type=float, default=0.0, help="S along the axis")
    ap.add_argument("--lmax", type=int, default=8)
    ap.add_argument("--linear", action="store_true",
                    help="second-order solution (source with u = 0)")
    ap.add_argument("--dr", type=float, default=None, help="table spacing (m/100)")
    ap.add_argument("--rlast", type=float, default=None, help="table end (200 m)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sol = solve_axisym(a.mass, a.momentum, a.spin, lmax=a.lmax, nonlinear=not a.linear)
    dr = a.dr if a.dr is not None else a.mass / 100.0
    rlast = a.rlast if a.rlast is not None else 200.0 * a.mass
    write_table(a.out, sol, dr, rlast)
    print(f"{a.out}: l = {sol['lvals']}, iterations = {sol['iterations']}, "
          f"m_adm = {sol['m_adm']:.10f}, u(0) = {sol['u0_centre']:.10f}")


if __name__ == "__main__":
    _main()
