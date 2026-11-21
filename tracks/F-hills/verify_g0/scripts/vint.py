"""verify_g0: vectorised Dormand-Prince 5(4) with a step size per trajectory.

Written for this verification (independent of newton3's DOP853 and geodesic_binary's DOP853).
State y has shape (N, n); each trajectory has its own time, step and end time. After every
accepted step a callback may stop trajectories or change per-trajectory parameters.
"""
import numpy as np

C = np.array([0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1])
A = [[],
     [1 / 5],
     [3 / 40, 9 / 40],
     [44 / 45, -56 / 15, 32 / 9],
     [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
     [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
     [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]]
B5 = np.array([35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0])
B4 = np.array([5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40])
E = B5 - B4


def integrate(rhs, y0, t0, t_end, rtol=1e-10, atol=1e-12, h0=1e-3, callback=None,
              max_iter=10_000_000, hmax=np.inf, max_steps=None):
    """rhs(t, y, idx) -> dy/dt for the rows idx (y has the rows idx only).
    callback(t_old, y_old, t_new, y_new, idx) -> boolean array 'stop' for rows idx, or a
    tuple (stop, y_new_modified) to change the accepted states.
    Returns t, y, done, nacc (arrays of length N)."""
    y = np.array(y0, float)
    N = y.shape[0]
    t = np.broadcast_to(np.asarray(t0, float), (N,)).copy()
    tend = np.broadcast_to(np.asarray(t_end, float), (N,)).copy()
    h = np.full(N, float(h0))
    done = t >= tend
    nacc = np.zeros(N, int)
    it = 0
    while not done.all():
        it += 1
        if it > max_iter:
            raise RuntimeError("max_iter")
        idx = np.where(~done)[0]
        yi, ti = y[idx], t[idx]
        hi = np.minimum(np.minimum(h[idx], tend[idx] - ti), hmax)
        K = []
        for s in range(7):
            ys = yi.copy()
            for j, aij in enumerate(A[s]):
                if aij != 0.0:
                    ys += (hi * aij)[:, None] * K[j]
            K.append(rhs(ti + C[s] * hi, ys, idx))
        y5 = yi + hi[:, None] * sum(B5[s] * K[s] for s in range(7) if B5[s] != 0)
        err = hi[:, None] * sum(E[s] * K[s] for s in range(7) if E[s] != 0)
        sc = atol + rtol * np.maximum(np.abs(yi), np.abs(y5))
        en = np.sqrt(np.mean((err / sc) ** 2, axis=1))
        en = np.where(np.isfinite(en), en, 1e10)
        acc = en <= 1.0
        fac = np.clip(0.9 * np.maximum(en, 1e-16) ** (-0.2), 0.2, 5.0)
        fac = np.where(acc, fac, np.minimum(fac, 1.0))
        h[idx] = hi * fac
        a_idx = idx[acc]
        if len(a_idx):
            t_old, y_old = t[a_idx].copy(), y[a_idx].copy()
            t[a_idx] = ti[acc] + hi[acc]
            y[a_idx] = y5[acc]
            nacc[a_idx] += 1
            stop = np.zeros(len(a_idx), bool)
            if callback is not None:
                res = callback(t_old, y_old, t[a_idx], y[a_idx], a_idx)
                if isinstance(res, tuple):        # (stop, modified states of the rows)
                    res, y[a_idx] = res
                stop = np.asarray(res, bool)
            fin = (t[a_idx] >= tend[a_idx] * (1 - 1e-15)) | stop
            if max_steps is not None:                 # per-trajectory cap: left unfinished (t < t_end)
                fin |= nacc[a_idx] >= max_steps
            done[a_idx[fin]] = True
    return t, y, done, nacc
