"""Symbolic checks of the quasi-spherical Szekeres solution (JOURNAL P1-P4, DESIGN section 2).

Metric (arXiv:1708.09143, eq. (ds2), lines 290-292 of simsilun_rev.tex, here with signature
(-,+,+,+), G = c = 1):

    ds^2 = -dt^2 + (R' - R Ecal'/Ecal)^2/(1 - k) dr^2 + R^2/Ecal^2 (dp^2 + dq^2),
    Ecal = ((p - P)^2 + (q - Q)^2)/(2 S) + S/2,      (line 296)
    Rdot^2 = -k + 2 M/R + Lambda R^2/3,              (line 301)

with M, k, S, P, Q functions of r and R = R(t, r). Checks, each printed as PASS/FAIL:

  A  Einstein equations G_ab + Lambda g_ab = 8 pi rho u_a u_b, rho of eq. (szrho)
  B  kinematics: Theta (sztht), sigma^a_b = Sigma e^a_b (szshr), electric Weyl
     E^a_b = W e^a_b (szwey), magnetic Weyl zero (R_ijkt = 0 on shell)
  C  3+1 on t = const: K_ij = -(1/2) d_t gamma_ij; Hamiltonian and momentum constraints
  D  Cotton tensor of gamma_ij (conformal flatness), and flatness for k = 0, M = 0
  E  the stereographic identities behind the conformal map (n, d_r n, Ecal'/Ecal = b.n)
     and the conformal-map ODE (u, Xtilde) of szekeres/confmap.py

Method. Derivatives of R with respect to t are eliminated with Rdot = v, v^2 = F(R, r)
(F = -k + 2M/R + Lambda R^2/3); every remaining derivative of a function of r is replaced
by a plain symbol (a jet variable); a component is zero when the numerator of the
cancelled rational function, reduced modulo v^2 - F, is the zero polynomial. With
--fast the reduction is checked at random rational points (exact arithmetic) instead of
symbolically (Schwartz-Zippel). Run: python3 sym_szekeres.py [--fast] [--only A,B,...]
"""

import argparse
import itertools
import random
import sys
import time

import sympy as sp
from sympy.core.function import AppliedUndef

t, r, p, q = sp.symbols("t r p q", real=True)
Lam = sp.Symbol("Lambda", real=True)
v = sp.Symbol("v", positive=True)          # Rdot
Rs = sp.Symbol("Rs", positive=True)        # R as a plain symbol inside F
fn = {name: sp.Function(name)(r) for name in ("M", "k", "S", "P", "Q")}
M, k, S, P, Q = (fn[n] for n in ("M", "k", "S", "P", "Q"))
R = sp.Function("R")(t, r)
R3 = sp.Function("R")(r)                   # R on one slice (3-geometry checks)

Ecal = ((p - P) ** 2 + (q - Q) ** 2) / (2 * S) + S / 2
F_of = lambda Rx: -k + 2 * M / Rx + Lam * Rx ** 2 / 3   # noqa: E731
RESULTS = []


def report(name, ok, extra=""):
    RESULTS.append((name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {extra}", flush=True)


# ----------------------------------------------------------------- elimination of t-derivatives
Vf = sp.Function("V")(t, r)                 # Rdot as a function while differentiating


def _tder_of_R(nt):
    """d^nt R/dt^nt as an expression in Rs and v, with dRs/dt = v, dv/dt = F_R/2
    (from v^2 = F(R, r)); no square roots appear."""
    FR = sp.diff(F_of(Rs), Rs)
    h = v
    for _ in range(nt - 1):
        h = sp.diff(h, Rs) * v + sp.diff(h, v) * FR / 2
    return h


def _dV_list(nmax):
    """d^m V/dr^m for m = 1..nmax, with dV/dr = d_r F(R(t, r), r)/(2 V)."""
    out = [None]
    dV = sp.diff(F_of(R), r) / (2 * Vf)
    out.append(dV)
    for m in range(2, nmax + 1):
        out.append(sp.diff(out[-1], r).subs(sp.Derivative(Vf, r), dV))
    return out


def eliminate_t(expr):
    """Replace every derivative of R(t, r) that contains t by its value on shell; Rdot -> v."""
    ders = [d for d in expr.atoms(sp.Derivative) if d.expr == R]
    rep = {}
    nrmax = 0
    for d in ders:
        nt = sum(c for var, c in d.variable_count if var == t)
        nr = sum(c for var, c in d.variable_count if var == r)
        if nt:
            nrmax = max(nrmax, nr)
    dVs = _dV_list(max(nrmax, 1))
    for d in ders:
        nt = sum(c for var, c in d.variable_count if var == t)
        nr = sum(c for var, c in d.variable_count if var == r)
        if nt == 0:
            continue
        h = _tder_of_R(nt).subs({Rs: R, v: Vf})
        if nr:
            h = sp.diff(h, r, nr)
            for m in range(nr, 0, -1):
                h = h.subs(sp.Derivative(Vf, (r, m)) if m > 1 else sp.Derivative(Vf, r), dVs[m])
        rep[d] = h
    out = expr.xreplace(rep)
    return out.xreplace({Vf: v})


def jets(expr):
    """Replace derivatives of the free functions (and the functions) by symbols."""
    rep = {}
    for d in expr.atoms(sp.Derivative):
        f = d.expr
        name = f.func.__name__
        sig = "".join(f"{var}{c}" for var, c in d.variable_count)
        rep[d] = sp.Symbol(f"{name}_{sig}")
    out = expr.xreplace(rep)
    rep2 = {}
    for f in out.atoms(AppliedUndef):
        rep2[f] = sp.Symbol(f.func.__name__)
    return out.xreplace(rep2)




def _Fpoly():
    Rsym = sp.Symbol("R")
    return sp.Symbol("v") ** 2 - (-sp.Symbol("k") + 2 * sp.Symbol("M") / Rsym + Lam * Rsym ** 2 / 3)


def numer_zero(expr, fast=False, npts=3, seed=1):
    """True if expr vanishes on shell. expr may contain R(t,r) derivatives and v."""
    e = jets(eliminate_t(expr))
    vv = sp.Symbol("v")
    e = e.xreplace({v: vv})
    Fp = _Fpoly()
    num = None
    if not fast:
        num, _ = sp.fraction(sp.cancel(sp.together(e)))
        num = sp.expand(num)
        if num == 0:
            return True
        # reduce modulo v^2 = F (clear the 1/R of F first)
        Rsym = sp.Symbol("R")
        rel = sp.expand(Fp * Rsym)          # R v^2 - (-k R + 2M + Lambda R^3/3)
        prem = sp.prem(num, rel, vv)
        return sp.expand(prem) == 0
    rng = random.Random(seed)
    syms = sorted(e.free_symbols, key=lambda s: s.name)
    num_e, den_e = sp.fraction(sp.together(e))
    good = 0
    tries = 0
    while good < npts:
        tries += 1
        if tries > 20 * npts:
            raise RuntimeError("no regular random point found")
        vals = {}
        for s in syms:
            if s.name == "v":
                continue
            # wide range of rationals: accidental zeros of a denominator are unlikely,
            # and a point where one occurs is skipped below
            vals[s] = sp.Rational(rng.randint(1, 10007), rng.randint(1, 997)) * (1 if rng.random() < 0.7 else -1)
        for nm in ("R", "S", "M"):
            for s in syms:
                if s.name == nm:
                    vals[s] = abs(vals[s])
        den = sp.expand(den_e.xreplace(vals))
        Fv = None
        if vv in num_e.free_symbols or vv in den_e.free_symbols:
            Fv = (-vals.get(sp.Symbol("k"), 0) + 2 * vals.get(sp.Symbol("M"), 0) / vals.get(sp.Symbol("R"), 1)
                  + vals.get(Lam, 0) * vals.get(sp.Symbol("R"), 0) ** 2 / 3)
            if Fv <= 0:
                continue
            den = sp.rem(sp.Poly(den, vv), sp.Poly(vv ** 2 - Fv, vv)).as_expr()
        if den == 0 or den.has(sp.zoo, sp.nan):
            continue                      # singular point: draw another one
        num = sp.expand(num_e.xreplace(vals))
        if Fv is not None:
            num = sp.rem(sp.Poly(num, vv), sp.Poly(vv ** 2 - Fv, vv)).as_expr()
        if sp.expand(num) != 0:
            return False
        good += 1
    return True


# ----------------------------------------------------------------- geometry helpers
def christoffel(g, X):
    n = len(X)
    gi = sp.diag(*[1 / g[i, i] for i in range(n)]) if g.is_diagonal() else g.inv()
    G = [[[0] * n for _ in range(n)] for _ in range(n)]
    dg = [[[sp.diff(g[i, j], X[a]) for a in range(n)] for j in range(n)] for i in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(b, n):
                s = 0
                for d in range(n):
                    if gi[a, d] == 0:
                        continue
                    s += gi[a, d] * (dg[d][b][c] + dg[d][c][b] - dg[b][c][d])
                G[a][b][c] = G[a][c][b] = s / 2
    return G, gi


def riemann_down(g, G, X):
    """R_abcd (all indices down) as a dict over a<b, c<d."""
    n = len(X)
    Rud = {}
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(c + 1, n):
                    s = sp.diff(G[a][d][b], X[c]) - sp.diff(G[a][c][b], X[d])
                    for e in range(n):
                        s += G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b]
                    Rud[a, b, c, d] = s
    Rdd = {}
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(n):
                for d in range(c + 1, n):
                    Rdd[a, b, c, d] = sum(g[a, e] * Rud[e, b, c, d] for e in range(n) if g[a, e] != 0)
    return Rud, Rdd


def ricci(Rud, n):
    Ric = sp.zeros(n, n)
    for b in range(n):
        for d in range(n):
            s = 0
            for a in range(n):
                if a == d:
                    continue
                c, dd, sg = (a, d, 1) if a < d else (d, a, -1)
                s += sg * Rud[a, b, c, dd]
            Ric[b, d] = s
    return Ric


def Rdd_get(Rdd, a, b, c, d):
    if a == b or c == d:
        return 0
    s = 1
    if a > b:
        a, b, s = b, a, -s
    if c > d:
        c, d, s = d, c, -s
    return s * Rdd[a, b, c, d]


# ----------------------------------------------------------------- the spacetime
X4 = (t, r, p, q)
Ep = sp.diff(Ecal, r)
Dfac = sp.diff(R, r) - R * Ep / Ecal
g4 = sp.diag(-1, Dfac ** 2 / (1 - k), R ** 2 / Ecal ** 2, R ** 2 / Ecal ** 2)
rho8pi = 2 * (sp.diff(M, r) - 3 * M * Ep / Ecal) / (R ** 2 * Dfac)         # 8 pi rho (szrho)
Rd = sp.diff(R, t)
Rdp = sp.diff(R, t, r)
Rp = sp.diff(R, r)
Theta_paper = (Rdp + 2 * Rd * Rp / R - 3 * Rd * Ep / Ecal) / Dfac          # (sztht)
Sigma_paper = -sp.Rational(1, 3) * (Rdp - Rd * Rp / R) / Dfac              # (szshr)
W_paper = M / (3 * R ** 3) * (3 * Rp - R * sp.diff(M, r) / M) / Dfac       # (szwey)


def check_A(fast):
    t0 = time.time()
    G, gi = christoffel(g4, X4)
    Rud, Rdd = riemann_down(g4, G, X4)
    Ric = ricci(Rud, 4)
    Rsc = sum(gi[a, a] * Ric[a, a] for a in range(4))
    ok_all = True
    for a in range(4):
        for b in range(a, 4):
            Gab = Ric[a, b] - Rsc * g4[a, b] / 2 + Lam * g4[a, b]
            T = rho8pi if (a == 0 and b == 0) else 0         # u_a u_b = delta_a0 delta_b0
            ok = numer_zero(Gab - T, fast)
            ok_all &= ok
            report(f"A G_{X4[a]}{X4[b]} + Lambda g = 8 pi rho u u", ok)
    print(f"   (A took {time.time() - t0:.1f} s)")
    return G, gi, Rud, Rdd, Ric, Rsc


def check_B(fast, G, gi, Rdd, Ric, Rsc):
    # Theta = d_t ln sqrt(-g) for u = d_t
    sqrtg = Dfac / sp.sqrt(1 - k) * R ** 2 / Ecal ** 2
    Theta = sp.diff(sqrtg, t) / sqrtg
    report("B Theta = (sztht)", numer_zero(Theta - Theta_paper, fast))
    # expansion tensor theta^i_j = (1/2) g^ii d_t g_ij (diagonal)
    th = [sp.diff(g4[i, i], t) / (2 * g4[i, i]) for i in (1, 2, 3)]
    sig = [th[i] - Theta / 3 for i in range(3)]
    e = [-2, 1, 1]                                   # e^r_r, e^p_p, e^q_q
    okS = all(numer_zero(sig[i] - Sigma_paper * e[i], fast) for i in range(3))
    report("B sigma^i_j = Sigma e^i_j with (szshr), e = diag(-2, 1, 1)", okS)
    # electric Weyl E_ij = C_itjt
    gtt = -1

    def C_itjt(i, j):
        Rm = Rdd_get(Rdd, i, 0, j, 0)
        return Rm - sp.Rational(1, 2) * (g4[i, j] * Ric[0, 0] + gtt * Ric[i, j]) + Rsc / 6 * g4[i, j] * gtt

    okE = True
    for i in (1, 2, 3):
        for j in (1, 2, 3):
            Emix = gi[i, i] * C_itjt(i, j)
            target = W_paper * e[i - 1] if i == j else 0
            okE &= numer_zero(Emix - target, fast)
    report("B E^i_j = W e^i_j with (szwey), same sign as the paper", okE)
    okH = True
    for (i, j, kk) in itertools.product((1, 2, 3), repeat=3):
        if i < j:
            okH &= numer_zero(Rdd_get(Rdd, i, j, kk, 0), fast)
    report("B magnetic Weyl: R_ijkt = 0 on shell (H_ab = 0)", okH)
    # Schwarzschild limit: M' = 0, S, P, Q constant -> W = M/R^3, E^r_r = -2M/R^3
    Wj = jets(W_paper).xreplace({sp.Symbol(n): 0 for n in ("M_r1", "S_r1", "P_r1", "Q_r1")})
    report("B Schwarzschild limit: W = M/R^3, so E^r_r = -2 W = -2M/R^3 (radial stretching)",
           sp.simplify(Wj - sp.Symbol("M") / sp.Symbol("R") ** 3) == 0)


def check_C(fast):
    X3 = (r, p, q)
    g3 = g4[1:, 1:]
    Kdd = sp.diag(*[-sp.diff(g3[i, i], t) / 2 for i in range(3)])
    G3, gi3 = christoffel(g3, X3)
    Rud3, _ = riemann_down(g3, G3, X3)
    Ric3 = ricci(Rud3, 3)
    R3s = sum(gi3[i, i] * Ric3[i, i] for i in range(3))
    Kmix = [gi3[i, i] * Kdd[i, i] for i in range(3)]
    trK = sum(Kmix)
    KK = sum(km ** 2 for km in Kmix)
    Ham = R3s + trK ** 2 - KK - 2 * rho8pi - 2 * Lam
    report("C Hamiltonian constraint", numer_zero(Ham, fast))
    report("C negative control: Hamiltonian with rho doubled is NOT zero",
           not numer_zero(Ham - 2 * rho8pi, fast))
    # momentum: D_j K^j_i - d_i K (diagonal K^i_j)
    okM = True
    for i in range(3):
        # D_j K^j_i = d_j K^j_i + G^j_jl K^l_i - G^l_ji K^j_l
        s = sp.diff(Kmix[i], X3[i]) + sum(G3[j][j][i] * Kmix[i] for j in range(3)) \
            - sum(G3[l][j][i] * (Kmix[j] if l == j else 0) for j in range(3) for l in range(3)) \
            - sp.diff(trK, X3[i])
        okM &= numer_zero(s, fast)
    report("C momentum constraint D_j K^j_i - d_i K = 0", okM)
    KL = -(Rdp - Rd * Ep / Ecal) / Dfac
    KT = -Rd / R
    report("C K^r_r = -(Rdot' - Rdot Ecal'/Ecal)/(R' - R Ecal'/Ecal)", numer_zero(Kmix[0] - KL, fast))
    report("C K^p_p = K^q_q = -Rdot/R", numer_zero(Kmix[1] - KT, fast) and numer_zero(Kmix[2] - KT, fast))
    report("C K = -Theta", numer_zero(trK + Theta_paper, fast))


def cotton(g3, X3):
    G3, gi3 = christoffel(g3, X3)
    Rud3, _ = riemann_down(g3, G3, X3)
    Ric3 = ricci(Rud3, 3)
    R3s = sum(gi3[i, j] * Ric3[i, j] for i in range(3) for j in range(3) if gi3[i, j] != 0)
    Sch = Ric3 - R3s * g3 / 4

    def nabla(i, j, kk):        # nabla_k Sch_ij
        s = sp.diff(Sch[i, j], X3[kk])
        for l in range(3):
            s -= G3[l][kk][i] * Sch[l, j] + G3[l][kk][j] * Sch[i, l]
        return s

    C = {}
    for i in range(3):
        for j in range(3):
            for kk in range(j + 1, 3):
                C[i, j, kk] = nabla(i, j, kk) - nabla(i, kk, j)
    return C, Ric3, R3s


def check_D(fast):
    X3 = (r, p, q)
    Ep3 = sp.diff(Ecal, r)
    D3 = sp.diff(R3, r) - R3 * Ep3 / Ecal
    g3 = sp.diag(D3 ** 2 / (1 - k), R3 ** 2 / Ecal ** 2, R3 ** 2 / Ecal ** 2)
    t0 = time.time()
    C, Ric3, R3s = cotton(g3, X3)
    ok = True
    for key, val in C.items():
        z = numer_zero(val, fast)
        ok &= z
        if not z:
            print("   non-zero Cotton component", key)
    report("D Cotton tensor of the Szekeres slice vanishes (conformally flat)", ok,
           f"({time.time() - t0:.1f} s)")
    # negative control: a slice with an angle-dependent factor that is not of Szekeres form
    gbad = sp.diag(D3 ** 2 / (1 - k) * (1 + p * q / (1 + p ** 2)), R3 ** 2 / Ecal ** 2, R3 ** 2 / Ecal ** 2)
    Cb, _, _ = cotton(gbad, X3)
    report("D negative control: a deformed metric has a non-zero Cotton tensor",
           not all(numer_zero(val, True) for val in Cb.values()))
    # k = 0: the 3-Ricci tensor vanishes (the slice is flat)
    okf = all(numer_zero(Ric3[i, j].subs(k, 0).doit(), fast) for i in range(3) for j in range(3))
    report("D k = 0: 3-Ricci tensor vanishes (flat slice)", okf)
    # k != 0: not flat in general (sanity: the Ricci scalar is not identically zero)
    nz = not numer_zero(R3s, True)
    report("D k != 0: Ricci scalar not identically zero (not flat in general)", nz)


def check_E(fast):
    W = P + sp.I * Q
    w = p + sp.I * q
    zeta = (w - W) / S
    zr, zi = (p - P) / S, (q - Q) / S
    den = 1 + zr ** 2 + zi ** 2
    n = sp.Matrix([2 * zr / den, 2 * zi / den, (zr ** 2 + zi ** 2 - 1) / den])
    report("E |n| = 1", sp.simplify(n.dot(n) - 1) == 0)
    Sp, Pp, Qp = (sp.diff(f, r) for f in (S, P, Q))
    b = sp.Matrix([-Pp / S, -Qp / S, -Sp / S])
    om = sp.Matrix([-Qp / S, Pp / S, 0])
    dn = sp.diff(n, r)
    rhs = b - b.dot(n) * n + om.cross(n)
    report("E d_r n = (b - (b.n) n) + omega x n, b = -(P',Q',S')/S, omega = (-Q',P',0)/S",
           all(sp.simplify(jets(x)) == 0 for x in (dn - rhs)))
    report("E Ecal'/Ecal = b.n", sp.simplify(jets(sp.diff(Ecal, r) / Ecal - b.dot(n))) == 0)
    dnp, dnq = sp.diff(n, p), sp.diff(n, q)
    report("E |d_p n|^2 = |d_q n|^2 = 1/Ecal^2, d_p n.d_q n = 0",
           all(sp.simplify(x) == 0 for x in (dnp.dot(dnp) - 1 / Ecal ** 2, dnq.dot(dnq) - 1 / Ecal ** 2,
                                             dnp.dot(dnq))))
    # Ecal as a vector X = (a, b, c, d) on the hyperboloid b^2 + c^2 - 4ad = -1
    a_, b_, c_, d_ = 1 / (2 * S), -P / S, -Q / S, (P ** 2 + Q ** 2) / (2 * S) + S / 2
    report("E Ecal = a(p^2+q^2) + b p + c q + d with b^2 + c^2 - 4 a d = -1",
           sp.simplify(Ecal - (a_ * (p ** 2 + q ** 2) + b_ * p + c_ * q + d_)) == 0 and
           sp.simplify(b_ ** 2 + c_ ** 2 - 4 * a_ * d_ + 1) == 0)
    # the conformal-map ODE: with eta(A,B) = b_A b_B + c_A c_B - 2(a_A d_B + d_A a_B),
    # u = s(-(R'/R) eta(Xt,X) + eta(Xt,X')), Xt' = u Xt - s((R'/R) X - X'), the norm of Xt is
    # conserved and (ln rho)' = u makes gamma = Phi^2 (flat Szekeres metric of rho, Xt)
    A = sp.symbols("At Bt Ct Dt")                 # Xt components at one r
    X = sp.symbols("Ax Bx Cx Dx")
    Xp = sp.symbols("Axp Bxp Cxp Dxp")
    s_, RpR = sp.symbols("s RpR")

    def eta(U, V):
        return U[1] * V[1] + U[2] * V[2] - 2 * (U[0] * V[3] + U[3] * V[0])
    u = s_ * (-RpR * eta(A, X) + eta(A, Xp))
    At_p = [u * A[i] - s_ * (RpR * X[i] - Xp[i]) for i in range(4)]
    dnorm = 2 * eta(A, At_p)
    sub = {A[3]: (A[1] ** 2 + A[2] ** 2 + 1) / (4 * A[0])}       # Xt on the hyperboloid
    report("E conformal-map ODE conserves the hyperboloid norm of Xt",
           sp.simplify(dnorm.subs(sub)) == 0)
    # radial metric: Phi (rho' - rho Ecalt'/Ecalt) = s (R' - R Ecal'/Ecal) for all p, q
    pq = [p ** 2 + q ** 2, p, q, 1]
    Ecal_t = sum(A[i] * pq[i] for i in range(4))
    Ecal_x = sum(X[i] * pq[i] for i in range(4))
    Ecal_t_p = sum(At_p[i] * pq[i] for i in range(4))
    Ecal_x_p = sum(Xp[i] * pq[i] for i in range(4))
    # Phi = R Ecal_t/(rho Ecal); rho'/rho = u; R'/R = RpR
    lhs = (Ecal_t / Ecal_x) * (u - Ecal_t_p / Ecal_t)           # Phi (rho'-rho Et'/Et)/R
    rhs_ = s_ * (RpR - Ecal_x_p / Ecal_x)                        # s (R' - R E'/E)/R
    report("E radial metric of the conformal map: Phi (rho' - rho Ecalt'/Ecalt) = s (R' - R Ecal'/Ecal)",
           sp.simplify(lhs - rhs_) == 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--only", default="A,B,C,D,E")
    a = ap.parse_args()
    which = set(a.only.split(","))
    t0 = time.time()
    if "E" in which:
        check_E(a.fast)
    if "C" in which:
        check_C(a.fast)
    if "D" in which:
        check_D(a.fast)
    if which & {"A", "B"}:
        G, gi, Rud, Rdd, Ric, Rsc = check_A(a.fast) if "A" in which else (None,) * 6
        if "B" in which:
            if G is None:
                G, gi = christoffel(g4, X4)
                Rud, Rdd = riemann_down(g4, G, X4)
                Ric = ricci(Rud, 4)
                Rsc = sum(gi[i, i] * Ric[i, i] for i in range(4))
            check_B(a.fast, G, gi, Rdd, Ric, Rsc)
    nfail = sum(1 for _, ok in RESULTS if not ok)
    print(f"{len(RESULTS)} checks, {nfail} failed, {time.time() - t0:.1f} s")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
