"""Checks of the plane-wave reference (zeldovich.py). Run: python3 test_zeldovich.py"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "cosmo", "newton"))
import zeldovich as Z  # noqa: E402
import pm as P  # noqa: E402

ok = True


def check(name, val, tol):
    global ok
    good = bool(val < tol)
    ok &= good
    print(f"{'PASS' if good else 'FAIL'}  {name}: {val:.3e} (tolerance {tol:.1e})")


# 1. closed form of the sheet solution against a direct integration of the sheet ODE
#    d/dtau (a dx/dtau) = (3/2)(x - Qt), Qt fixed, for arbitrary data (both modes)
rng = np.random.default_rng(1)
L, N = 1.0, 40
x0 = np.sort(rng.uniform(0, L, N))
x0 = np.linspace(0, L, N, endpoint=False) + 0.003*np.sin(2*np.pi*np.arange(N)/N*3)
v0 = 0.004*rng.standard_normal(N)
m = 1.0 + 0.1*rng.uniform(size=N)
tau_end = 1.0
xr, vr = Z.sheet_solution(x0, v0, m, L, np.array([tau_end]))
M = m.sum()
Q = (np.cumsum(m) - 0.5*m)/M*L


def rhs(tau, y):
    x, p = y[:N], y[N:]
    a = Z.scale_factor(tau)
    xcm = (m*x).sum()/M
    return np.concatenate([p/a, 1.5*(x - Q - xcm + 0.5*L)])


y = np.concatenate([x0, v0])
nst = 4000
h = tau_end/nst
t = 0.0
for _ in range(nst):
    k1 = rhs(t, y); k2 = rhs(t + h/2, y + h/2*k1); k3 = rhs(t + h/2, y + h/2*k2)
    k4 = rhs(t + h, y + h*k3)
    y = y + h/6*(k1 + 2*k2 + 2*k3 + k4); t += h
check("sheet closed form vs RK4 of the sheet ODE, positions", np.abs(y[:N] - xr[0]).max(), 1e-11)
a_end = Z.scale_factor(tau_end)
check("sheet closed form vs RK4, velocities", np.abs(y[N:]/a_end - vr[0]).max(), 1e-11)
check("ordering kept (no crossing in this check)", float(np.diff(y[:N]).min() < 0), 0.5)

# 2. continuum density equals dQ/dx along the flow
d = 0.05
k = 2*np.pi/L
x0 = np.linspace(0, L, 100001)
for a in (2.0, 10.0, 20.0):
    x, v, rho = Z.continuum(x0, a, d, L)
    dQdx0 = 1.0 + d*np.sin(k*x0)
    dxdx0 = np.gradient(x, x0)
    check(f"continuum density = dQ/dx at a = {a:g}",
          np.abs(dQdx0/dxdx0/rho - 1.0)[1:-1].max(), 1e-6)

# 3. the data of pm.east_particles (ratios 1,0,0) are a pure growing mode of the
#    sheet solution, and the sheets follow the continuum to O((k h)^2) of the displacement
for n in (32, 64):
    x, vv, mm, q = P.east_particles(d, n, 1, L, ratios=(1.0, 0.0, 0.0))
    line = (np.abs(q[:, 1] - q[0, 1]) < 1e-12) & (np.abs(q[:, 2] - q[0, 2]) < 1e-12)
    xs, vs, ms = x[line, 0], vv[line, 0], mm[line]
    taus = np.array([2*(np.sqrt(10.0) - 1), 2*(np.sqrt(20.0) - 1)])
    xsh, vsh = Z.sheet_solution(xs, vs, ms, L, taus)
    for i, a in enumerate((10.0, 20.0)):
        xc, vc, _ = Z.continuum(xs, a, d, L)
        dx = xsh[i] - xc
        dx -= L*np.round(dx/L)
        err = np.abs(dx).max()/((a - 1)*d/k)
        check(f"n = {n}: discrete sheets vs continuum at a = {a:g}, position / displacement",
              err, 0.05*(k*L/n)**2)
    # growing-mode check: A = s0 (B = 0) up to the discreteness of Q
    order = np.argsort(xs)
    Mtot = ms.sum()
    Qd = (np.cumsum(ms[order]) - 0.5*ms[order])/Mtot*L
    s0 = xs[order] - Qd - (ms*xs).sum()/Mtot + 0.5*L
    check(f"n = {n}: decaying-mode content |s0 - v0| / max|v0|",
          np.abs(s0 - vs[order]).max()/np.abs(vs).max(), 0.05*(k*L/n)**2)

print("ALL PASS" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
