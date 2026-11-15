"""Vectorised adaptive Dormand-Prince 8(5,3) integration of many independent trajectories.

Every trajectory has its own time, step size and end time; one call advances all of
them together, so a scan over binary phases and orientations costs a few numpy array
operations per stage instead of one Python call per trajectory. The Butcher tableau and
the error estimator are those of Hairer, Norsett & Wanner (DOP853), read from the
installed SciPy (``scipy.integrate._ivp.dop853_coefficients``); the step-size control
mirrors SciPy's ``DOP853`` class (safety 0.9, factors 0.2..10, exponent -1/8).
"""
import numpy as np
from scipy.integrate._ivp import dop853_coefficients as _c

N_STAGES = _c.N_STAGES
A = np.array(_c.A[:N_STAGES, :N_STAGES])
B = np.array(_c.B)
C = np.array(_c.C[:N_STAGES])
E3 = np.array(_c.E3)
E5 = np.array(_c.E5)
SAFETY, MIN_FACTOR, MAX_FACTOR = 0.9, 0.2, 10.0
EXPONENT = -1.0 / 8.0


def integrate_many(rhs, t0, y0, t_end, h0, rtol=1e-10, atol=1e-12, max_steps=2_000_000,
                   monitor=None):
    """Integrate dy/dt = rhs(t, y, idx) for N trajectories from t0[i] to t_end[i].

    rhs(t, y, idx): t (n,), y (n, d), idx (n,) indices of the trajectories in the full
    set (to look up per-trajectory parameters); returns (n, d).
    monitor(t, y, idx): called after every accepted step with the accepted states.
    Returns (y_end (N, d), n_accepted (N,), ok (N,) bool).
    """
    y = np.array(y0, dtype=float, copy=True)
    N, d = y.shape
    t = np.broadcast_to(np.asarray(t0, dtype=float), (N,)).copy()
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (N,)).copy()
    h = np.broadcast_to(np.asarray(h0, dtype=float), (N,)).copy()
    nacc = np.zeros(N, dtype=np.int64)
    ok = np.ones(N, dtype=bool)
    idx_all = np.arange(N)
    f = rhs(t, y, idx_all)
    act = idx_all[t < t_end]
    it = 0
    K = None
    while act.size:
        it += 1
        if it > max_steps:
            ok[act] = False
            break
        n = act.size
        ta, ya, fa = t[act], y[act], f[act]
        ha = np.minimum(h[act], t_end[act] - ta)
        if K is None or K.shape[1] < n:
            K = np.empty((N_STAGES + 1, n, d))
        Kv = K[:, :n]
        Kv[0] = fa
        for s in range(1, N_STAGES):
            dy = np.tensordot(A[s, :s], Kv[:s], axes=(0, 0)) * ha[:, None]
            Kv[s] = rhs(ta + C[s] * ha, ya + dy, act)
        y_new = ya + ha[:, None] * np.tensordot(B, Kv[:N_STAGES], axes=(0, 0))
        t_new = ta + ha
        f_new = rhs(t_new, y_new, act)
        Kv[N_STAGES] = f_new
        scale = atol + np.maximum(np.abs(ya), np.abs(y_new)) * rtol
        e5 = np.sum((np.tensordot(E5, Kv, axes=(0, 0)) / scale) ** 2, axis=1)
        e3 = np.sum((np.tensordot(E3, Kv, axes=(0, 0)) / scale) ** 2, axis=1)
        denom = e5 + 0.01 * e3
        with np.errstate(divide="ignore", invalid="ignore"):
            err = np.where(denom > 0, np.abs(ha) * e5 / np.sqrt(denom * d), 0.0)
            fac = np.where(err > 0, SAFETY * err ** EXPONENT, MAX_FACTOR)
        bad = ~np.isfinite(err)
        err[bad] = 1e300
        fac[bad] = MIN_FACTOR
        acc = err <= 1.0
        ia = act[acc]
        y[ia] = y_new[acc]
        t[ia] = t_new[acc]
        f[ia] = f_new[acc]
        nacc[ia] += 1
        h[act] = np.where(acc, ha * np.minimum(MAX_FACTOR, fac),
                          ha * np.maximum(MIN_FACTOR, np.minimum(fac, 1.0)))
        if monitor is not None and ia.size:
            monitor(t[ia], y[ia], ia)
        done = t[act] >= t_end[act] - 1e-14 * np.maximum(np.abs(t_end[act]), 1.0)
        tiny = h[act] <= 1e-14 * np.maximum(np.abs(t[act]), 1.0)
        if np.any(tiny & ~done):
            ok[act[tiny & ~done]] = False
        act = act[~(done | tiny)]
    return y, nacc, ok
