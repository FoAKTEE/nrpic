"""V1: nonlinear isobaric heat-conduction reference in the Lagrangian mass coordinate
(own semi-analytic reference; JOURNAL entries 1-2).

Equal pressure P everywhere (sound crossing fast against conduction), Eckart/Fourier flux
q = -kappa dT/dx with kappa = f kappa_1(T), kappa_1 = (75 sqrt(pi)/64) sqrt(T/m)/sigma_tot
(k_B = m = 1), constant c_p per particle. With dm = n dx (particles per unit area):

    dT/dt|_m = (1/c_p) d/dm ( n kappa dT/dm ),   n = P/T,   x(m) = int T dm / P.

For constant c_p the volume int T dm / P is conserved, so P stays constant in a box of fixed
volume (energy conservation). A factor f on kappa is a rescaling of time:
T(m, t; f) = T(m, f t; 1), used by the fits.
"""
import numpy as np
from scipy import sparse
from scipy.integrate import solve_ivp

K1C = 75*np.sqrt(np.pi)/64


def evolve(T0, dm, P, lam, cp, t_eval, rtol=1e-8, atol=1e-13):
    """T0: cell temperatures on a periodic uniform grid in m (cell size dm, particles per
    unit area); lam = 1/(n sigma_tot) at n = 1, i.e. 1/sigma_tot (rho_0 = n m, m = 1).
    Returns T[t, i]."""
    N = len(T0)

    def nk(T):
        return (P/T)*K1C*np.sqrt(T)*lam          # n kappa with kappa_1 = K1C sqrt(T)/sigma

    def rhs(t, T):
        g = nk(T)
        gf = 0.5*(g + np.roll(g, -1))             # face i+1/2
        F = gf*(np.roll(T, -1) - T)/dm
        return (F - np.roll(F, 1))/dm/cp

    S = sparse.diags([np.ones(N), np.ones(N - 1), np.ones(N - 1)], [0, 1, -1],
                     format="lil")
    S[0, N - 1] = 1
    S[N - 1, 0] = 1
    sol = solve_ivp(rhs, (0, t_eval[-1]), T0, method="BDF", t_eval=t_eval, rtol=rtol,
                    atol=atol, jac_sparsity=S.tocsc())
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y.T


def positions(T, dm, P, m_anchor_index=None):
    """Cell-centre positions x(m) = int T dm / P (cumulative, first cell centre at
    T[0] dm/(2P)); returns x[t, i] and the volume per period."""
    vol = np.cumsum(T, axis=-1)*dm/P
    x = vol - 0.5*T*dm/P
    return x, vol[..., -1]


def mode_amplitude(T, dm, P, k):
    """A_n(t) = sum_cells dm cos(k x) / sum dm, with x measured from the centre of cell 0
    shifted to the symmetry point m = 0 (cell 0 starts at m = 0)."""
    x, L = positions(T, dm, P)
    # symmetry point m = 0 sits at x = 0: shift by half a cell of the first cell
    x0 = 0.0
    return np.mean(np.cos(k*(x - x0)), axis=-1), L


def mode_initial(eps, theta0, n0, k, N, adiabatic=False):
    """Isobaric-mode start of the runs: n = n0 (1 - eps cos kx), T = theta0 (1 + eps cos kx)
    (checked against the initial snapshot in v1_mode.py). Grid uniform in m over one
    wavelength, cell 0 starting at the hot peak x = 0. Pressure P = mean of n T over x
    (= the pressure the box keeps, energy conservation). Optional adiabatic adjustment of
    each element to P (gamma = 5/3), keeping the volume."""
    L = 2*np.pi/k
    Mtot = n0*L
    dm = Mtot/N
    mc = (np.arange(N) + 0.5)*dm
    # invert m(x) = n0 (x - (eps/k) sin kx)
    x = mc/n0
    for _ in range(60):
        f = n0*(x - eps/k*np.sin(k*x)) - mc
        x -= f/(n0*(1 - eps*np.cos(k*x)))
    T = theta0*(1 + eps*np.cos(k*x))
    n = n0*(1 - eps*np.cos(k*x))
    P = theta0*n0*(1 - eps**2/2)                 # <n T>_x
    if adiabatic:
        Pl = n*T
        for _ in range(50):
            Ta = T*(P/Pl)**0.4
            P = np.sum(Ta)*dm/L
        T = Ta
    return T, dm, P, Mtot


def step_initial(theta1, theta2, n1, n2, L, N):
    """Step start: x in [0, L/2) at (n1, theta1), [L/2, L) at (n2, theta2), equal
    pressure. Grid uniform in m, cell 0 starting at x = 0."""
    M1 = n1*L/2
    M2 = n2*L/2
    Mtot = M1 + M2
    dm = Mtot/N
    mc = (np.arange(N) + 0.5)*dm
    T = np.where(mc < M1, theta1, theta2)
    # cells straddling the interface: none if M1/dm integer
    P = n1*theta1
    return T, dm, P, Mtot, M1


def slab_mass(T, dm, P, M1, L):
    """Mass in x in [0, L/2) given that the centre of the hot slab (m = M1/2) stays at
    x = L/4 (symmetry). Linear interpolation of the cumulative volume."""
    N = T.shape[-1]
    Mtot = N*dm
    me = np.arange(N + 1)*dm
    medges = np.concatenate([me[:-1] - Mtot, me[:-1], me + Mtot])
    out = []
    for Tt in np.atleast_2d(T):
        v = np.concatenate([[0.0], np.cumsum(Tt)*dm/P])
        Lp = v[-1]
        vext = np.concatenate([v[:-1] - Lp, v[:-1], v + Lp])
        xc = np.interp(M1/2, me, v)              # x(m = M1/2) in the Lagrangian frame
        xr = vext - xc + L/4                     # hot centre at x = L/4
        ma = np.interp(0.0, xr, medges)
        mb = np.interp(L/2, xr, medges)
        out.append(mb - ma)
    return np.array(out)
