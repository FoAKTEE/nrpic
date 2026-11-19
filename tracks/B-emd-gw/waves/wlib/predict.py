"""Prediction of the errors of the code on a single tensor mode from the Fourier symbol of
its discrete operators (generalization of periodic_z4c/analysis/predict_lw.py, which met
the measured errors of the axis wave to 1 per cent, to oblique wave vectors and to the
expanding background).

Linearized Z4c for a tensor mode with zero shift (the TT data of a direction whose
discrete divergence vanishes, such as (1,1,1) and (1,1,0), keep Gamma^i = 0):
    d_t h  = -2 alpha At - d h,
    d_t At = (alpha chi / 2) w_h^2 h + alpha K At - d At,
with alpha chi = 1/a, alpha K = -3 calH in the matter background (alpha = 1, K = 0 flat),
    w_h^2 = - sum_i symbol(D2)(theta_i)/dx_i^2   (sixth-order stencil for nghost = 4),
    d     = sum_i sigma 2^(-2 ng) (2 sin(theta_i/2))^(2 ng)/dx_i  (Kreiss-Oliger, per axis,
            athenak/src/z4c/z4c_calcrhs.cpp lines 768-779, z4c.cpp line 168),
theta_i = k_i dx_i, integrated with the classical RK4 of the code at its step:
    dt = min(cfl dx, dt_expansion / calH)  (z4c_newdt.cpp; nrpic.cpp lines 1314-1345,
    the particle limit is not multiplied by cfl: mesh.cpp line 648),
the last step shortened to reach tlim, mesh outputs at the first step boundary at or after
each multiple of the output interval.
"""
import numpy as np

from .refs import background, flrw_mode

D2 = {2: [1.0, -2.0], 3: [-1 / 12, 4 / 3, -5 / 2], 4: [1 / 90, -3 / 20, 3 / 2, -49 / 18]}


def symbol_d2(ng, th):
    c = D2[ng]
    n = len(c) - 1
    s = c[-1] * np.ones_like(th)
    for j in range(1, n + 1):
        s = s + 2 * c[n - j] * np.cos(j * th)
    return s


def semi_discrete(kvec, dx, ng=4, sigma=0.5):
    kvec = np.asarray(kvec, float)
    dx = np.asarray(dx, float)
    th = kvec * dx
    w2 = -np.sum(symbol_d2(ng, th) / dx ** 2)
    d = np.sum(sigma * 2.0 ** (-2 * ng) * (2 * np.sin(th / 2)) ** (2 * ng) / dx)
    return w2, d


def step_times(tlim, dtfun):
    ts = [0.0]
    while ts[-1] < tlim - 1e-12:
        t = ts[-1]
        dt = min(dtfun(t), tlim - t)
        ts.append(t + dt)
    return np.array(ts)


def output_times(ts, dt_out):
    """first step boundary at or after each multiple of dt_out (and t = 0)."""
    out = [0]
    nxt = dt_out
    for i, t in enumerate(ts):
        if i == 0:
            continue
        if t >= nxt - 1e-12 * max(1.0, nxt):
            out.append(i)
            while nxt <= t + 1e-12 * max(1.0, nxt):
                nxt += dt_out
    return np.array(sorted(set(out)))


def rk4_mode(ts, rhs, y0):
    ys = [np.array(y0, dtype=complex)]
    for i in range(len(ts) - 1):
        t, dt = ts[i], ts[i + 1] - ts[i]
        y = ys[-1]
        k1 = rhs(t, y)
        k2 = rhs(t + dt / 2, y + dt / 2 * k1)
        k3 = rhs(t + dt / 2, y + dt / 2 * k2)
        k4 = rhs(t + dt, y + dt * k3)
        ys.append(y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4))
    return np.array(ys)


def predict_flat(kvec, L, N, tlim, dt_out, cfl=0.25, ng=4, sigma=0.5):
    """Ratio W_num/W_ex at the output times for the travelling wave exp(i(k.x - |k|t))."""
    dx = np.array(L, float) / np.array(N, float)
    w2, d = semi_discrete(kvec, dx, ng, sigma)
    kn = np.linalg.norm(kvec)
    ts = step_times(tlim, lambda t: cfl * dx.min())
    lam = -d - 1j * np.sqrt(w2)              # forward mode exp(-i w t)
    z = lam * np.diff(ts)
    R = 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24
    G = np.concatenate([[1.0], np.cumprod(R)])
    idx = output_times(ts, dt_out)
    ratio = G[idx] * np.exp(1j * kn * ts[idx])
    return {"t": ts[idx], "ratio": ratio, "nsteps": len(ts) - 1, "w_h/k-1": np.sqrt(w2) / kn - 1,
            "ko_rate": d}


def predict_flrw(kvec, L, N, tlim, dt_out, cfl=0.25, ng=4, sigma=0.5, dt_expansion=0.01):
    """W = T + i T'/|k| of the numerical mode against the exact one at the output times."""
    dx = np.array(L, float) / np.array(N, float)
    w2, d = semi_discrete(kvec, dx, ng, sigma)
    kn = np.linalg.norm(kvec)

    def dtfun(t):
        _, calH, _ = background(t)
        dt = cfl * dx.min()
        if dt_expansion > 0:
            dt = min(dt, dt_expansion / calH)
        return dt

    ts = step_times(tlim, dtfun)

    def rhs(t, y):
        a, calH, alpha = background(t)
        h, At = y
        return np.array([-2 * alpha * At - d * h,
                         0.5 * w2 / a * h - 3 * calH * At - d * At])

    ys = rk4_mode(ts, rhs, [0.0, -0.5])          # T = 0, T' = -2 a At = 1 at a = 1
    idx = output_times(ts, dt_out)
    t = ts[idx]
    a, _, _ = background(t)
    Tn = ys[idx, 0].real
    Tdn = (-2 * a * ys[idx, 1]).real
    T, Td = flrw_mode(t, kn)
    Wn = Tn + 1j * Tdn / kn
    We = T + 1j * Td / kn
    return {"t": t, "ratio": Wn / We, "nsteps": len(ts) - 1, "w_h/k-1": np.sqrt(w2) / kn - 1,
            "ko_rate": d, "T": T, "Td": Td}
