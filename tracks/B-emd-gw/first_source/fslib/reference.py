"""Second-order reference for the crossed waves (1, eps, 0) before shell crossing.

Quasi-static TT strain of the weak-field equation of arXiv:1604.06065 (scope/SCOPE.md
section 3 with the lead note; scope/scripts/crossed_waves_tt.py docstring):
h^TT = (20/3) Lambda[d_i Phi d_j Phi]/|K|^2, Phi = sum_i phi_i sin(k x_i),
phi_i = -(3/2)(H/k)^2 delta r_i (cosmo/ic/make_east.py lines 9-11). At K1 = (k, k, 0):
h_+ = s cos(K1.x), s = -(5/6) phi_x phi_y, basis e+ = u u - z z, u = (1, -1, 0)/sqrt 2;
at K2 = (k, -k, 0): +(5/6) phi_x phi_y cos(K2.x) in the basis u = (1, 1, 0)/sqrt 2.
Conformally flat initial data start the mode at zero: c(tau) = s g(tau) with
g'' + 2 Hc g' + |K|^2 (g - 1) = 0, g(0) = g'(0) = 0, Hc = 1/(1 + tau/2), a = (1 + tau/2)^2
(scope/scripts/regime_estimates.py, check 3A).
"""
import numpy as np
from scipy.integrate import solve_ivp


def phis(delta, eps, L=4.0, H=1.0):
    k = 2 * np.pi / L
    return [-1.5 * (H / k) ** 2 * delta * r for r in (1.0, eps, 0.0)]


def static_amplitude(delta, eps, L=4.0, H=1.0):
    """s = -(5/6) phi_x phi_y: the + amplitude at K1 of the quasi-static strain."""
    p = phis(delta, eps, L, H)
    return -(5.0 / 6.0) * p[0] * p[1]


def g_of_tau(tau, L=4.0, m=(1, 1, 0)):
    """Response g(tau) of the box mode m from rest to a unit constant source."""
    K = 2 * np.pi / L * np.sqrt(sum(v * v for v in m))
    tau = np.atleast_1d(np.asarray(tau, float))

    def rhs(t, y):
        Hc = 1.0 / (1.0 + 0.5 * t)
        return [y[1], -2 * Hc * y[1] - K * K * (y[0] - 1.0)]
    sol = solve_ivp(rhs, (0.0, float(tau.max())), [0.0, 0.0], t_eval=np.sort(tau),
                    rtol=1e-11, atol=1e-14, method="DOP853", dense_output=True)
    y = sol.sol(tau)
    return y[0], y[1]


def a_of_tau(tau):
    return (1.0 + 0.5 * np.asarray(tau)) ** 2


def tau_of_a(a):
    return 2.0 * (np.sqrt(np.asarray(a)) - 1.0)
