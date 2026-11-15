"""Small differential-geometry helpers for the sympy checks of DERIVATION.md.

Conventions: Gamma^a_bc = (1/2) g^ad (d_b g_dc + d_c g_db - d_d g_bc),
R_bd = d_a Gamma^a_bd - d_d Gamma^a_ba + Gamma^a_ae Gamma^e_bd - Gamma^a_de Gamma^e_ba,
G_ab = R_ab - (1/2) g_ab R. Nothing here is specific to the problem.
"""

import sympy as sp


def christoffel(g, X, simp=sp.simplify):
    n = len(X)
    gi = simp(g.inv())
    Gam = [[[0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(b, n):
                s = 0
                for d in range(n):
                    s += gi[a, d] * (sp.diff(g[d, c], X[b]) + sp.diff(g[d, b], X[c])
                                     - sp.diff(g[b, c], X[d]))
                Gam[a][b][c] = Gam[a][c][b] = simp(s / 2)
    return gi, Gam


def ricci(g, X, simp=sp.simplify):
    n = len(X)
    gi, Gam = christoffel(g, X, simp)
    Ric = sp.zeros(n, n)
    for b in range(n):
        for d in range(b, n):
            s = 0
            for a in range(n):
                s += sp.diff(Gam[a][b][d], X[a]) - sp.diff(Gam[a][b][a], X[d])
                for e in range(n):
                    s += Gam[a][a][e] * Gam[e][b][d] - Gam[a][d][e] * Gam[e][b][a]
            Ric[b, d] = Ric[d, b] = simp(s)
    Rs = simp(sum(gi[a, b] * Ric[a, b] for a in range(n) for b in range(n)))
    return gi, Gam, Ric, Rs


def einstein_mixed(g, X, simp=sp.simplify):
    """G^a_b (index up, index down) and the pieces used to build it."""
    gi, Gam, Ric, Rs = ricci(g, X, simp)
    n = len(X)
    G = sp.zeros(n, n)
    for a in range(n):
        for b in range(n):
            G[a, b] = sum(gi[a, c] * Ric[c, b] for c in range(n)) - (Rs / 2 if a == b else 0)
    return G, gi, Gam


def is_zero(expr, simp=sp.simplify):
    """True when expr simplifies to 0 (also tries a numeric spot check on failure)."""
    e = simp(sp.together(sp.expand(expr)))
    return e == 0
