#!/usr/bin/env python3
"""Four-dimensional checks of DERIVATION.md, section 2 (sympy).

(a) Comoving Lemaitre-Tolman-Bondi dust, ds^2 = -dt^2 + R_r^2/(1+2E) dr^2 + R^2 dOmega^2:
    with Rdot^2 = 2m/R + 2E, G^a_b = 8 pi rho u^a u_b, rho = m_r/(4 pi R^2 R_r).
(b) The same spacetime in (tau, R), tau the proper time of the dust and R the areal radius:
    ds^2 = -dtau^2 + (dR - v dtau)^2/(1+2E) + R^2 dOmega^2, v = sqrt(2m/R + 2E), with m and
    E advected by the dust, (d_tau + v d_R) m = (d_tau + v d_R) E = 0:
    G^a_b = 8 pi rho u^a u_b, u^a = (1, v, 0, 0), rho = d_R m/(4 pi R^2).
(c) Marginally bound special cases (brief S1, line 356): v = sqrt(2M/R) is vacuum
    (Schwarzschild in outgoing Painleve-Gullstrand form); v = H(tau) R with
    dH/dtau = -(3/2) H^2 is spatially flat FLRW dust with 8 pi rho = 3 H^2.
(d) Coordinate change: R_r dr = dR - v dt turns the metric of (a) into that of (b).

Run: python3 -I sym_ltb_4d.py   (exit status 0 when every check passes)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sympy as sp  # noqa: E402

from geom import einstein_mixed  # noqa: E402

PASS = []


def check(name, expr):
    e = sp.simplify(expr)
    ok = (e == 0)
    PASS.append(ok)
    print(f"[{'ok' if ok else 'FAIL'}] {name}" + ("" if ok else f": remainder {e}"))
    return ok


th, ph = sp.symbols("theta phi", positive=True)


# ---------------------------------------------------------------- (a) comoving LTB
def part_a():
    t, r = sp.symbols("t r", positive=True)
    R = sp.Function("R")(t, r)
    E = sp.Function("E")(r)
    m = sp.Function("m")(r)
    g = sp.diag(-1, sp.diff(R, r) ** 2 / (1 + 2 * E), R ** 2, R ** 2 * sp.sin(th) ** 2)
    G, _, _ = einstein_mixed(g, [t, r, th, ph])
    V = sp.sqrt(2 * m / R + 2 * E)
    Rr = sp.diff(R, r)
    # Rddot = -m/R^2 and its r-derivative (G^theta_theta contains d_r d_t^2 R)
    rttr = sp.diff(-m / R ** 2, r)
    rules = {sp.diff(R, t, 2, r): rttr, sp.diff(R, r, t, 2): rttr,
             sp.diff(R, t, 2): -m / R ** 2,
             sp.diff(R, t, r): (sp.diff(m, r) / R - m * Rr / R ** 2 + sp.diff(E, r)) / V,
             sp.diff(R, r, t): (sp.diff(m, r) / R - m * Rr / R ** 2 + sp.diff(E, r)) / V}
    rules1 = {sp.diff(R, t): V}
    Gs = G.applyfunc(lambda x: sp.simplify(x.xreplace(rules).xreplace(rules1)))
    rho = sp.diff(m, r) / (4 * sp.pi * R ** 2 * Rr)
    # T^a_b = rho u^a u_b with u = d_t: only T^t_t = -rho
    check("(a) G^t_t = -8 pi rho, rho = m_r/(4 pi R^2 R_r)", Gs[0, 0] + 8 * sp.pi * rho)
    for (i, j) in [(1, 1), (2, 2), (3, 3), (0, 1), (1, 0)]:
        check(f"(a) G^{i}_{j} = 0", Gs[i, j])


# ---------------------------------------------------------------- (b) (tau, R) form
def part_b():
    tau, R = sp.symbols("tau R", positive=True)
    m = sp.Function("m")(tau, R)
    E = sp.Function("E")(tau, R)
    v = sp.sqrt(2 * m / R + 2 * E)
    f = 1 + 2 * E
    g = sp.Matrix([[-1 + v ** 2 / f, -v / f, 0, 0],
                   [-v / f, 1 / f, 0, 0],
                   [0, 0, R ** 2, 0],
                   [0, 0, 0, R ** 2 * sp.sin(th) ** 2]])
    G, gi, _ = einstein_mixed(g, [tau, R, th, ph], simp=lambda x: x)
    # advection rules (d_tau + v d_R) X = 0 for X = m, E, with their derivatives
    first = {sp.diff(X, tau): -v * sp.diff(X, R) for X in (m, E)}
    mixed = {}
    for X in (m, E):
        val = sp.diff(-v * sp.diff(X, R), R)
        mixed[sp.diff(X, tau, R)] = val
        mixed[sp.diff(X, R, tau)] = val
    second = {}
    for X in (m, E):
        val = sp.diff(-v * sp.diff(X, R), tau).xreplace(mixed).xreplace(first)
        second[sp.diff(X, tau, 2)] = val

    def adv(x):
        return x.xreplace(second).xreplace(mixed).xreplace(first)

    rho = sp.diff(m, R) / (4 * sp.pi * R ** 2)
    T = sp.zeros(4, 4)
    T[0, 0] = -rho          # rho u^tau u_tau, u_tau = -1
    T[1, 0] = -rho * v      # rho u^R u_tau
    # spot-check numerically at a generic point with generic profiles, then simplify
    for (i, j) in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]:
        expr = adv(G[i, j]) - 8 * sp.pi * T[i, j]
        check(f"(b) G^{i}_{j} - 8 pi T^{i}_{j} = 0 (tau, R form, E and m advected)", expr)
    # lapse and shift of the slice tau = const: g^{tau tau} = -1/alpha^2, beta^R = alpha^2 g^{tau R}
    check("(b) lapse: g^{tau tau} = -1", sp.simplify(gi[0, 0] + 1) if gi[0, 0] != -1 else 0)
    check("(b) shift: beta^R = g^{tau R} = -v", sp.simplify(gi[0, 1] + v))
    # dust 4-velocity u^a = (1, v): normal to the slice, u_R = 0, u_tau = -1
    u_dn = g * sp.Matrix([1, v, 0, 0])
    check("(b) u_R = 0 (dust at rest w.r.t. the normal observers)", u_dn[1])
    check("(b) u_tau = -1", u_dn[0] + 1)


# ---------------------------------------------------------------- (c) special cases
def part_c():
    tau, R = sp.symbols("tau R", positive=True)
    M = sp.symbols("M", positive=True)
    v = sp.sqrt(2 * M / R)
    g = sp.Matrix([[-1 + v ** 2, -v, 0, 0], [-v, 1, 0, 0], [0, 0, R ** 2, 0],
                   [0, 0, 0, R ** 2 * sp.sin(th) ** 2]])
    G, _, _ = einstein_mixed(g, [tau, R, th, ph])
    for (i, j) in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]:
        check(f"(c) vacuum v = sqrt(2M/R): G^{i}_{j} = 0", G[i, j])
    H = sp.Function("H")(tau)
    v = H * R
    g = sp.Matrix([[-1 + v ** 2, -v, 0, 0], [-v, 1, 0, 0], [0, 0, R ** 2, 0],
                   [0, 0, 0, R ** 2 * sp.sin(th) ** 2]])
    G, _, _ = einstein_mixed(g, [tau, R, th, ph])
    rules = {sp.diff(H, tau): -sp.Rational(3, 2) * H ** 2}
    rho = 3 * H ** 2 / (8 * sp.pi)
    Gs = G.applyfunc(lambda x: sp.simplify(x.xreplace(rules)))
    check("(c) FLRW v = H R: G^tau_tau = -8 pi rho, 8 pi rho = 3 H^2", Gs[0, 0] + 8 * sp.pi * rho)
    check("(c) FLRW: G^R_tau = -8 pi rho v", Gs[1, 0] + 8 * sp.pi * rho * v)
    for (i, j) in [(0, 1), (1, 1), (2, 2)]:
        check(f"(c) FLRW with dH/dtau = -(3/2) H^2: G^{i}_{j} = 0", Gs[i, j])
    # 2M/R_b = (H R_b)^2 for the ball m = (4 pi/3) rho R^3
    Rb = sp.symbols("R_b", positive=True)
    Mb = sp.Rational(4, 3) * sp.pi * rho * Rb ** 3
    check("(c) 2M/R_b = (H R_b)^2", 2 * Mb / Rb - (H * Rb) ** 2)


# ---------------------------------------------------------------- (d) coordinate change
def part_d():
    t, r = sp.symbols("t r", positive=True)
    dt, dr = sp.symbols("dt dr")
    R = sp.Function("R")(t, r)
    E = sp.Function("E")(r)
    v = sp.diff(R, t)
    dR = sp.diff(R, t) * dt + sp.diff(R, r) * dr
    ds2_comoving = -dt ** 2 + sp.diff(R, r) ** 2 * dr ** 2 / (1 + 2 * E)
    ds2_pg = -dt ** 2 + (dR - v * dt) ** 2 / (1 + 2 * E)
    check("(d) R_r dr = dR - v dt maps the comoving metric onto the (tau, R) form",
          sp.expand(ds2_comoving - ds2_pg))


if __name__ == "__main__":
    part_d()
    part_c()
    part_a()
    part_b()
    n_ok = sum(PASS)
    print(f"{n_ok}/{len(PASS)} checks passed")
    sys.exit(0 if all(PASS) else 1)
