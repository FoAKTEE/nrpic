"""High-accuracy reference integrator for timelike Kerr geodesics in coordinate time.

Evolves the 3+1 (Hamiltonian) form of the geodesic equations for the state (x^i, u_i):

    dx^i/dt = alpha gamma^ij u_j / W - beta^i
    du_i/dt = -W d_i alpha + u_j d_i beta^j - (alpha / 2W) u_j u_k d_i gamma^jk
            = -W d_i alpha + u_j d_i beta^j + (alpha / 2W) U^j U^k d_i gamma_jk,   U^j = gamma^jk u_k

with W = sqrt(1 + gamma^ij u_i u_j), using the analytic 3+1 fields of ``nrpic.kerr`` in any of the
systems 'bl', 'ks', 'cks'.  The right-hand side is minus the gradient of H = alpha W - beta^i u_i,
so E = H is conserved exactly by the continuous flow.  Integration uses scipy's DOP853 (default)
or Radau with user tolerances; samples at requested times come from the method's dense output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp

from . import kerr

__all__ = ["make_rhs", "rhs", "Trajectory", "integrate", "invariant_history", "uniform_times"]


def rhs(system, x, u, a=kerr.A_DEFAULT, M=kerr.M_DEFAULT):
    """Return (dx/dt, du/dt) for state(s) x, u of shape (..., 3) in `system`."""
    m = kerr.adm(system, x, a, M)
    U = np.einsum("...ij,...j->...i", m.gamma_inv, u)
    W = np.sqrt(1 + np.einsum("...i,...i->...", u, U))
    dx = (m.alpha / W)[..., None] * U - m.beta
    du = (-W)[..., None] * m.dalpha + np.einsum("...ij,...j->...i", m.dbeta, u) \
        + (0.5 * m.alpha / W)[..., None] * np.einsum("...ijk,...j,...k->...i", m.dgamma, U, U)
    return dx, du


def make_rhs(system, a=kerr.A_DEFAULT, M=kerr.M_DEFAULT):
    """Return f(t, y) for scipy, y = (x^1, x^2, x^3, u_1, u_2, u_3)."""
    admf = kerr._ADM_FUNCS[system]

    def f(t, y):
        x = y[:3]
        u = y[3:]
        m = admf(x, a, M)
        U = m.gamma_inv @ u
        W = np.sqrt(1.0 + u @ U)
        out = np.empty(6)
        out[:3] = (m.alpha / W) * U - m.beta
        out[3:] = -W * m.dalpha + m.dbeta @ u + (0.5 * m.alpha / W) * ((m.dgamma @ U) @ U)
        return out

    return f


def uniform_times(t0, t_end, dt_out):
    """t0 + k dt_out, k = 0..n, with n = (t_end - t0)/dt_out required to be an integer
    (to 1e-9) and the last sample set exactly to t_end.  If 1/dt_out is an integer m (e.g.
    dt_out = 0.01) the samples are computed as t0 + k / m, i.e. the doubles nearest k/100."""
    n = (t_end - t0) / dt_out
    nk = int(round(n))
    if abs(n - nk) > 1e-9 * max(1.0, n):
        raise ValueError("t_end - t0 must be an integer multiple of dt_out")
    m = 1.0 / dt_out
    if abs(m - round(m)) < 1e-9 * m:
        t = t0 + np.arange(nk + 1) / round(m)
    else:
        t = t0 + np.arange(nk + 1) * dt_out
    t[-1] = t_end
    return t


@dataclass
class Trajectory:
    """Result of `integrate`.

    t (N,), x (N, 3), u (N, 3): samples at the requested times (dense output).
    t_end, x_end, u_end: final state from the last integrator step (lands exactly on t_end).
    events: dict name -> (t_events, y_events) for the turning-point events, if requested.
    sol: scipy OdeResult (``sol.sol`` is the dense interpolant when dense_output=True).
    """

    system: str
    a: float
    M: float
    t: np.ndarray
    x: np.ndarray
    u: np.ndarray
    t_end: float
    x_end: np.ndarray
    u_end: np.ndarray
    rtol: float
    atol: float
    method: str
    nfev: int
    nsteps: int
    events: dict = field(default_factory=dict)
    sol: object = None

    def state(self, t):
        """Dense-output state(s) at time(s) t: returns (x, u) with shapes (..., 3)."""
        if self.sol is None or self.sol.sol is None:
            raise ValueError("integrate(..., dense_output=True) required")
        y = self.sol.sol(np.asarray(t, dtype=float))
        y = np.moveaxis(y, 0, -1)
        return y[..., :3], y[..., 3:]


def integrate(system, x0, u0, t_end, *, t0=0.0, t_eval=None, dt_out=None, rtol=1e-13, atol=1e-13,
              method="DOP853", a=kerr.A_DEFAULT, M=kerr.M_DEFAULT, dense_output=False,
              turning_points=False, max_step=np.inf):
    """Integrate a geodesic in coordinate time of `system` from t0 to t_end.

    Parameters
    ----------
    system : 'bl' | 'ks' | 'cks'
    x0, u0 : initial position and covariant spatial four-velocity (3-vectors)
    t_end : final coordinate time (the last step lands exactly on it)
    t_eval : explicit sample times, or dt_out for uniform samples t0 + k dt_out (k = 0..n)
    rtol, atol : integrator tolerances (scipy clamps rtol to >= 2.22e-14)
    method : 'DOP853' (default) or 'Radau'
    dense_output : keep the interpolant (Trajectory.state(t))
    turning_points : record events dr/dt = 0 ('peri': -/+ crossing, 'apo': +/- crossing) and
        dtheta/dt = 0 ('theta_turn'), located on the dense output.

    Returns
    -------
    Trajectory
    """
    f = make_rhs(system, a, M)
    y0 = np.concatenate([np.asarray(x0, float), np.asarray(u0, float)])
    if dt_out is not None:
        t_eval = uniform_times(t0, t_end, dt_out)
    events = None
    names = []
    if turning_points:
        def _xdot(t, y):
            return f(t, y)[:3]

        def ev_peri(t, y):
            return kerr.dr_dt(system, y[:3], _xdot(t, y), a)
        ev_peri.direction = 1.0

        def ev_apo(t, y):
            return kerr.dr_dt(system, y[:3], _xdot(t, y), a)
        ev_apo.direction = -1.0

        def ev_th(t, y):
            return kerr.dtheta_dt(system, y[:3], _xdot(t, y), a)
        ev_th.direction = 0.0
        events = [ev_peri, ev_apo, ev_th]
        names = ["peri", "apo", "theta_turn"]
    sol = solve_ivp(f, (t0, t_end), y0, method=method, t_eval=t_eval, rtol=rtol, atol=atol,
                    dense_output=dense_output, events=events, max_step=max_step)
    if sol.status != 0:
        raise RuntimeError(f"integration failed: {sol.message}")
    # Final state.  The last accepted step ends exactly on t_end.  Without t_eval sol.y[:, -1] is
    # that step's state; with t_eval (last sample = t_end) it is the step's interpolant evaluated
    # at its right endpoint, which for DOP853 reduces to y_old + (y_new - y_old), i.e. the step
    # state to within one rounding.
    yf = sol.y[:, -1]
    if abs(sol.t[-1] - t_end) > 0:
        raise RuntimeError("last sample is not at t_end")
    ev = {}
    if turning_points:
        for k, nme in enumerate(names):
            ev[nme] = (sol.t_events[k], sol.y_events[k])
    if dense_output:
        nsteps = len(sol.sol.ts) - 1
    elif t_eval is None:
        nsteps = len(sol.t) - 1
    else:
        nsteps = -1
    return Trajectory(system=system, a=a, M=M, t=sol.t, x=sol.y[:3].T.copy(), u=sol.y[3:].T.copy(),
                      t_end=float(t_end), x_end=yf[:3].copy(), u_end=yf[3:].copy(), rtol=rtol,
                      atol=atol, method=method, nfev=sol.nfev, nsteps=nsteps, events=ev, sol=sol)


def invariant_history(system, x, u, a=kerr.A_DEFAULT, M=kerr.M_DEFAULT, ref=None):
    """E, L_z, Q along a trajectory and their errors relative to `ref` (default: first sample).

    Returns dict with arrays E, Lz, Q and errors dE, dLz, dQ, where d* = (value - ref)/|ref|
    (relative), or (value - ref) if |ref| < 1e-12 (e.g. Q ~ 1e-32 of the equatorial orbit, whose
    theta0 = fl(pi/2) differs from pi/2 by 6e-17); keys *_relative say which.  Also
    max_abs_d* scalars.
    """
    E, Lz, Q = kerr.invariants(system, np.asarray(x), np.asarray(u), a, M)
    if ref is None:
        ref = (E[0], Lz[0], Q[0])
    out = dict(E=E, Lz=Lz, Q=Q)
    for name, val, r0 in zip(("E", "Lz", "Q"), (E, Lz, Q), ref):
        rel = abs(r0) > 1e-12
        d = (val - r0) / abs(r0) if rel else val - r0
        out["d" + name] = d
        out["d" + name + "_relative"] = rel
        out["max_abs_d" + name] = float(np.max(np.abs(d)))
    return out
