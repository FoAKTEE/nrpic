"""Minimal symbolic tensor helpers (sympy) for the derivation scripts of D-pre-1.

Written for this package; no outside code. Index conventions: Christoffel
Gamma[a][b][c] = Gamma^a_{bc}; Ricci R_{bd} = d_a Gamma^a_{bd} - d_d Gamma^a_{ba}
+ Gamma^a_{ae} Gamma^e_{bd} - Gamma^a_{de} Gamma^e_{ba}.
"""
import sympy as sp


def christoffel(g, x):
    n = len(x)
    gi = sp.simplify(g.inv())
    G = [[[0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                G[a][b][c] = sp.simplify(sum(gi[a, d] * (sp.diff(g[d, b], x[c])
                                                         + sp.diff(g[d, c], x[b])
                                                         - sp.diff(g[b, c], x[d]))
                                             for d in range(n)) / 2)
    return G


def ricci(g, x):
    n = len(x)
    G = christoffel(g, x)
    R = sp.zeros(n, n)
    for b in range(n):
        for d in range(n):
            R[b, d] = sp.simplify(
                sum(sp.diff(G[a][b][d], x[a]) for a in range(n))
                - sum(sp.diff(G[a][b][a], x[d]) for a in range(n))
                + sum(G[a][a][e] * G[e][b][d] for a in range(n) for e in range(n))
                - sum(G[a][d][e] * G[e][b][a] for a in range(n) for e in range(n)))
    return R, G


def ricci_scalar(g, x):
    R, G = ricci(g, x)
    gi = g.inv()
    return sp.simplify(sum(gi[a, b] * R[a, b] for a in range(len(x)) for b in range(len(x)))), R, G


def einstein_mixed(g, x):
    """G^a_b for the metric g."""
    Rs, R, G = ricci_scalar(g, x)
    gi = g.inv()
    n = len(x)
    Gm = sp.zeros(n, n)
    for a in range(n):
        for b in range(n):
            Gm[a, b] = sp.simplify(sum(gi[a, c] * R[c, b] for c in range(n))
                                   - (Rs / 2 if a == b else 0))
    return Gm, Rs


def covdiv_mixed(Km, G, x):
    """D_j K^j_i for a mixed tensor Km[j, i] = K^j_i with Christoffels G."""
    n = len(x)
    out = []
    for i in range(n):
        s = sum(sp.diff(Km[j, i], x[j]) for j in range(n))
        s += sum(G[j][j][k] * Km[k, i] for j in range(n) for k in range(n))
        s -= sum(G[k][j][i] * Km[j, k] for j in range(n) for k in range(n))
        out.append(sp.simplify(s))
    return out


def check_zero(expr, label):
    """Print and assert that expr simplifies to zero."""
    z = sp.simplify(sp.together(sp.expand(expr)))
    ok = (z == 0)
    print(f"[{'OK' if ok else 'FAIL'}] {label}" + ("" if ok else f": remainder {z}"))
    if not ok:
        raise AssertionError(label)
    return ok
