#!/usr/bin/env python3
"""Check of the far-field expansion of the initial-data solver
(athenak/src/particles/nrpic_idfar.hpp), transcribed line by line: moments of point
sources, coefficients of the homogeneous polynomials, value and gradient of the expansion
against the direct sum, for lmax = 0 to 4 at three radii; and the Bowen-York limit of the
vector far field. Standard library and numpy only; prints the errors."""
import math

import numpy as np

fact = [1, 1, 2, 6, 24]
leg = [[1, 0, 0], [1, 0, 0], [1.5, -.5, 0], [2.5, -1.5, 0], [4.375, -3.75, .375]]


def idx(a, b, c):
    d = a + b + c
    return d*(d + 1)*(d + 2)//6 + (d - a)*(d - a + 1)//2 + c


def accumulate(t, w, x, y, z, lmax):
    for d in range(lmax + 1):
        for a in range(d, -1, -1):
            for b in range(d - a, -1, -1):
                c = d - a - b
                t[idx(a, b, c)] += w*x**a*y**b*z**c


def coefficients(t, lmax):
    c = np.zeros(35)
    for l in range(lmax + 1):
        for k in range(l//2 + 1):
            p = l - 2*k
            for a in range(p, -1, -1):
                for b in range(p - a, -1, -1):
                    e = p - a - b
                    tr = 0.0
                    for i in range(k, -1, -1):
                        for j in range(k - i, -1, -1):
                            m = k - i - j
                            tr += fact[k]/(fact[i]*fact[j]*fact[m])*t[idx(a+2*i, b+2*j, e+2*m)]
                    w = leg[l][k]*fact[p]/(fact[a]*fact[b]*fact[e])*tr
                    for i in range(k, -1, -1):
                        for j in range(k - i, -1, -1):
                            m = k - i - j
                            c[idx(a+2*i, b+2*j, e+2*m)] += w*fact[k]/(fact[i]*fact[j]*fact[m])
    return c


def evaluate(c, lmax, x, y, z):
    r2 = x*x + y*y + z*z
    ir2 = 1.0/r2
    rp = math.sqrt(ir2)
    phi, g = 0.0, np.zeros(3)
    q = 0
    for l in range(lmax + 1):
        h = hx = hy = hz = 0.0
        for a in range(l, -1, -1):
            for b in range(l - a, -1, -1):
                e = l - a - b
                cc = c[q]
                q += 1
                h += cc*x**a*y**b*z**e
                if a > 0:
                    hx += cc*a*x**(a-1)*y**b*z**e
                if b > 0:
                    hy += cc*b*x**a*y**(b-1)*z**e
                if e > 0:
                    hz += cc*e*x**a*y**b*z**(e-1)
        w = (2*l + 1)*h*ir2
        phi += h*rp
        g += np.array([hx - w*x, hy - w*y, hz - w*z])*rp
        rp *= ir2
    f = -1.0/(4.0*math.pi)
    return phi*f, g*f


def main():
    rng = np.random.default_rng(1)
    src = rng.uniform(-1, 1, (20, 3))
    w = rng.uniform(0.5, 1.5, 20)
    assert sorted(idx(a, b, d-a-b) for d in range(5) for a in range(d+1)
                  for b in range(d-a+1)) == list(range(35))
    print("relative error of the value and of the gradient against the direct sum")
    for R in (8.0, 16.0, 32.0):
        x = np.array([0.3, -0.5, 0.81])
        x = x/np.linalg.norm(x)*R
        d = x[None, :] - src
        dist = np.linalg.norm(d, axis=1)
        exact = -np.sum(w/dist)/(4*math.pi)
        gex = np.sum((w/dist**3)[:, None]*d, axis=0)/(4*math.pi)
        out = []
        for lmax in range(5):
            t = np.zeros(35)
            for q in range(20):
                accumulate(t, w[q], *src[q], lmax)
            phi, g = evaluate(coefficients(t, lmax), lmax, *x)
            out.append("%.1e/%.1e" % (abs(phi/exact - 1), np.linalg.norm(g - gex)
                                      / np.linalg.norm(gex)))
        print("r = %4.0f: lmax 0..4: %s" % (R, "  ".join(out)))
    # Bowen-York limit: s_i = 8 pi P_i delta at the centre
    P = np.array([0.3, -0.2, 0.5])
    cv = []
    for a in range(3):
        t = np.zeros(35)
        accumulate(t, 8*math.pi*P[a], 0.0, 0.0, 0.0, 4)
        cv.append(coefficients(t, 4))
    cu = np.zeros(35)
    x = np.array([1.3, -2.1, 0.7])
    v, gv = zip(*[evaluate(cv[a], 4, *x) for a in range(3)])
    u, gu = evaluate(cu, 4, *x)
    W = np.array([0.875*v[i] - 0.125*(gu[i] + sum(x[a]*gv[a][i] for a in range(3)))
                  for i in range(3)])
    r = np.linalg.norm(x)
    n = x/r
    by = -(7*P + n*np.dot(n, P))/(4*r)
    print("Bowen-York limit, largest difference:", np.abs(W - by).max())


if __name__ == "__main__":
    main()
