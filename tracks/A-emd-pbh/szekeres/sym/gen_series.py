"""Taylor coefficients of l(lambda) = ln g(lambda), the universal function of dust evolution.

With simultaneous bang time, every dust shell of an LTB or Szekeres model obeys
Rdot^2 = 2M/R - k, R(t = 0) = 0, and by scaling R = M^(1/3) t^(2/3) g(lambda) with
lambda = k t^(2/3) / M^(2/3). Bound branch (eta the cycloid angle):
    lambda = (eta - sin eta)^(2/3),   g = (1 - cos eta)/lambda;
the unbound branch is the analytic continuation eta -> i eta (lambda < 0). In w = eta^2:
    lambda = w c(w),   c(w) = (sum_n (-1)^n w^n/(2n+3)!)^(2/3),
    g = (w/lambda) sum_n (-1)^n w^n/(2n+2)!.
This script inverts lambda(w) as a power series and prints the coefficients of
l(lambda) = ln g(lambda) in floating point (mpmath, 50 digits). Output pasted into
szekeres/universal.py (the test suite regenerates and compares them).
"""

import sys

import mpmath as mp

mp.mp.dps = 50


def mul(a, b, N):
    out = [mp.mpf(0)] * N
    for i, ai in enumerate(a[:N]):
        if ai == 0:
            continue
        for j, bj in enumerate(b[:N - i]):
            out[i + j] += ai * bj
    return out


def powser(a, alpha, N):
    """(a(x))^alpha for a[0] > 0, by the J.C.P. Miller recurrence."""
    out = [mp.mpf(0)] * N
    out[0] = a[0] ** alpha
    for n in range(1, N):
        s = mp.mpf(0)
        for k in range(1, n + 1):
            if k < len(a):
                s += (alpha * k - (n - k)) * a[k] * out[n - k]
        out[n] = s / (n * a[0])
    return out


def logser(a, N):
    """ln a(x) for a[0] > 0: (ln a)' = a'/a."""
    inv = powser(a, -1, N)
    da = [(k + 1) * a[k + 1] for k in range(N - 1)] + [mp.mpf(0)]
    q = mul(da, inv, N)
    out = [mp.log(a[0])] + [q[k - 1] / k for k in range(1, N)]
    return out


def compose(f, g, N):
    """f(g(x)) for g[0] = 0."""
    out = [mp.mpf(0)] * N
    gp = [mp.mpf(1)] + [mp.mpf(0)] * (N - 1)
    for k in range(N):
        if k > 0:
            gp = mul(gp, g, N)
        for i in range(N):
            out[i] += f[k] * gp[i] if k < len(f) else 0
    return out


def coefficients(N=40):
    chi = [(-1) ** n / mp.factorial(2 * n + 3) for n in range(N)]      # chi/eta^3 in w
    phi = [(-1) ** n / mp.factorial(2 * n + 2) for n in range(N)]      # (1-cos)/eta^2 in w
    c = powser(chi, mp.mpf(2) / 3, N)                                   # lambda = w c(w)
    cinv = powser(c, -1, N)                                             # w = lambda / c(w)
    # fixed point for w(lambda) as a series in lambda: w = lambda * cinv(w)
    w = [mp.mpf(0), 1 / c[0]] + [mp.mpf(0)] * (N - 2)
    for _ in range(N + 2):
        ci = compose(cinv, w, N)
        w = [mp.mpf(0)] + ci[:N - 1]
    # g = (w/lambda) * phi(w)  ->  w/lambda = cinv(w(lambda))
    g = mul(compose(cinv, w, N), compose(phi, w, N), N)
    return logser(g, N), g


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    l, g = coefficients(N)
    print("g0 =", mp.nstr(g[0], 25), " (9/2)^(1/3) =", mp.nstr(mp.cbrt(mp.mpf(9) / 2), 25))
    print("L_COEF = (")
    for x in l:
        print(f"    {mp.nstr(x, 20, min_fixed=-1, max_fixed=-1)},")
    print(")")
