"""Full Newtonian three-body scattering driver: binary (m1, m2) passing a mass M.

This is the Newtonian frame of reference of Track F (F-pre-1). It takes the parameters a
run of the code takes (masses, binary semi-major axis and eccentricity, pericentre of the
centre-of-mass orbit, binary orientation and phase), returns the barycentric positions
and momenta at a chosen starting distance (the initial data of the three-black-hole
runs), and integrates the encounter to classify the outcome.

Units: G = 1 by default (pass G); any consistent units otherwise. Bodies are ordered
[M, m1, m2]. Frame and angle conventions: see orbits.py. The centre-of-mass orbit is the
Kepler conic of the relative vector R = x_cm(binary) - x_M with mu = G (M + m),
pericentre r_p (or D r_t with r_t = a (M/m)^(1/3), SKR prp.tex:88), eccentricity e_orb
(1 = parabolic, the case of the three papers). The effective phase is the binary's mean
anomaly extrapolated to the pericentre time of that conic without tides
(SKR prp.tex:601-610): mean anomaly at the start = phase + n_b t0, t0 < 0.

Outcome classes (field 'outcome'):
  0 SURVIVED   m1-m2 bound, apocentre < half its Hill radius about M at the end
  1 EJECT2     binary disrupted, m1 bound to M, m2 unbound (exchange)
  2 EJECT1     binary disrupted, m2 bound to M, m1 unbound (exchange)
  3 BOTHBOUND  binary disrupted, both bound to M
  4 BOTHFREE   binary disrupted, both unbound from M
  5 UNSETTLED  m1-m2 bound but wide: not settled at the end time
Energies E1, E2 are the two-body energies of each member with M,
E_i = mu_i |v_i - v_M|^2 / 2 - G M m_i / |x_i - x_M|, mu_i = M m_i/(M + m_i), and
dE = (m1/m) E2 - (m2/m) E1 (KHSR arXiv:1201.4794 ms.tex:1103), all reported in units of
(G m1 m2 / a)(M/m)^(1/3). In the limit M/m -> infinity dE equals the restricted E2.
"""
from dataclasses import dataclass, asdict, field
import numpy as np
from .integrate import integrate_many
from .orbits import binary_relative_state, conic_state, conic_time_from_pericentre

SURVIVED, EJECT2, EJECT1, BOTHBOUND, BOTHFREE, UNSETTLED = range(6)
OUTCOME_NAMES = ["survived", "m2 ejected", "m1 ejected", "both bound", "both free",
                 "unsettled"]


@dataclass
class HillsSetup:
    """Parameters of one encounter (the same as a run of the code takes).

    Give exactly one of rp (pericentre of the centre-of-mass orbit) and D = rp / r_t.
    theta, varphi: binary angular-momentum direction (orbits.py); default coplanar
    prograde. varpi: binary periapsis direction in its plane. phase: effective mean
    anomaly at the pericentre time.
    """
    M: float
    m1: float
    m2: float
    a: float
    e_b: float = 0.0
    rp: float = None
    D: float = None
    e_orb: float = 1.0
    theta: float = np.pi / 2
    varphi: float = np.pi / 2
    varpi: float = 0.0
    phase: float = 0.0
    G: float = 1.0

    @property
    def m(self):
        return self.m1 + self.m2

    @property
    def r_t(self):
        return self.a * (self.M / self.m) ** (1.0 / 3.0)

    @property
    def r_p(self):
        if (self.rp is None) == (self.D is None):
            raise ValueError("give exactly one of rp and D")
        return self.rp if self.rp is not None else self.D * self.r_t

    @property
    def penetration(self):
        return self.r_p / self.r_t

    @property
    def energy_unit(self):
        return self.G * self.m1 * self.m2 / self.a * (self.M / self.m) ** (1.0 / 3.0)


def _stack(setups):
    """Arrays of all parameters for a list of HillsSetup."""
    keys = ["M", "m1", "m2", "a", "e_b", "e_orb", "theta", "varphi", "varpi", "phase", "G"]
    P = {k: np.array([getattr(s, k) for s in setups], dtype=float) for k in keys}
    P["rp"] = np.array([s.r_p for s in setups], dtype=float)
    P["m"] = P["m1"] + P["m2"]
    P["r_t"] = P["a"] * (P["M"] / P["m"]) ** (1.0 / 3.0)
    return P


def initial_state_arrays(P, r0):
    """Barycentric positions x (n, 3, 3) and velocities v (n, 3, 3), bodies [M, m1, m2],
    with the binary centre of mass at distance r0 (n,) from M on the incoming branch.
    Returns x, v, t0 (time of the start relative to the pericentre, < 0)."""
    n = P["M"].size
    r0 = np.broadcast_to(np.asarray(r0, dtype=float), (n,))
    mu = P["G"] * (P["M"] + P["m"])
    if np.any(r0 < P["rp"]):
        raise ValueError("start distance inside the pericentre")
    R, V, f0 = conic_state(P["rp"], P["e_orb"], mu, r0, incoming=True)
    t0 = -conic_time_from_pericentre(P["rp"], P["e_orb"], mu, r0)
    nb = np.sqrt(P["G"] * P["m"] / P["a"] ** 3)
    r, v = binary_relative_state(P["a"], P["e_b"], nb, P["phase"] + nb * t0, P["varpi"],
                                 P["theta"], P["varphi"])
    Mt = P["M"] + P["m"]
    xM = -(P["m"] / Mt)[:, None] * R
    vM = -(P["m"] / Mt)[:, None] * V
    xc = (P["M"] / Mt)[:, None] * R
    vc = (P["M"] / Mt)[:, None] * V
    x1 = xc - (P["m2"] / P["m"])[:, None] * r
    x2 = xc + (P["m1"] / P["m"])[:, None] * r
    v1 = vc - (P["m2"] / P["m"])[:, None] * v
    v2 = vc + (P["m1"] / P["m"])[:, None] * v
    x = np.stack([xM, x1, x2], axis=1)
    vv = np.stack([vM, v1, v2], axis=1)
    return x, vv, t0


def initial_state(setup, r0=None, k0=10.0):
    """Initial data of one encounter: the binary centre of mass at r0 from M (default
    k0 r_t), incoming. Returns a dict with masses, positions, velocities and momenta
    (barycentric, zero total momentum), the time to pericentre and the parameters."""
    P = _stack([setup])
    if r0 is None:
        r0 = k0 * P["r_t"][0]
    x, v, t0 = initial_state_arrays(P, r0)
    masses = np.array([setup.M, setup.m1, setup.m2])
    return dict(names=["M", "m1", "m2"], masses=masses, positions=x[0], velocities=v[0],
                momenta=masses[:, None] * v[0], t_to_pericentre=-t0[0], r0=float(r0),
                r_t=float(P["r_t"][0]), r_p=float(P["rp"][0]), params=asdict(setup))


def initial_state_json(setup, r0=None, k0=10.0):
    """initial_state as plain JSON-serialisable lists (for a problem-generator input file)."""
    ic = initial_state(setup, r0=r0, k0=k0)
    out = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in ic.items()}
    out["frame"] = ("barycentric; orbit of the binary centre of mass in the x-y plane, "
                    "pericentre along +x, orbital angular momentum along +z; G = 1")
    return out


def _rhs_factory(masses, G):
    """Newtonian accelerations; y = (x_M, x_1, x_2, v_M, v_1, v_2), 18 components."""
    def rhs(t, y, idx):
        m = masses[idx]
        g = G[idx]
        x = y[:, :9].reshape(-1, 3, 3)
        acc = np.zeros_like(x)
        for i, j in ((0, 1), (0, 2), (1, 2)):
            d = x[:, j] - x[:, i]
            ir3 = np.sum(d * d, axis=1) ** -1.5
            acc[:, i] += (g * m[:, j] * ir3)[:, None] * d
            acc[:, j] -= (g * m[:, i] * ir3)[:, None] * d
        out = np.empty_like(y)
        out[:, :9] = y[:, 9:]
        out[:, 9:] = acc.reshape(-1, 9)
        return out
    return rhs


def total_energy(x, v, masses, G):
    kin = 0.5 * np.sum(masses * np.sum(v * v, axis=2), axis=1)
    pot = np.zeros(x.shape[0])
    for i, j in ((0, 1), (0, 2), (1, 2)):
        pot -= G * masses[:, i] * masses[:, j] / np.linalg.norm(x[:, j] - x[:, i], axis=1)
    return kin + pot


def total_angular_momentum(x, v, masses):
    return np.sum(masses[:, :, None] * np.cross(x, v), axis=1)


def _pair_energy(x, v, mi, mj, G, i, j):
    """Two-body energy, semi-major axis and eccentricity of the pair (i, j)."""
    d = x[:, j] - x[:, i]
    w = v[:, j] - v[:, i]
    r = np.linalg.norm(d, axis=1)
    mu_red = mi * mj / (mi + mj)
    gm = G * (mi + mj)
    eps = 0.5 * np.sum(w * w, axis=1) - gm / r          # specific energy
    h2 = np.sum(np.cross(d, w) ** 2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sma = np.where(eps < 0, -gm / (2 * eps), np.inf)
        ecc = np.sqrt(np.maximum(1 + 2 * eps * h2 / gm ** 2, 0.0))
    return mu_red * eps, sma, ecc, r


def scatter(setups, r0=None, k0=10.0, k_end=30.0, t_end=None, rtol=1e-11, atol=1e-14):
    """Integrate a list of HillsSetup from the start (r0, default k0 r_t) to the time at
    which the unperturbed centre-of-mass conic would be at k_end r_t on the way out (or
    t_end after the pericentre). Returns a dict of arrays; see the module docstring."""
    P = _stack(setups)
    n = P["M"].size
    if r0 is None:
        r0 = k0 * P["r_t"]
    x, v, t0 = initial_state_arrays(P, r0)
    masses = np.stack([P["M"], P["m1"], P["m2"]], axis=1)
    mu = P["G"] * (P["M"] + P["m"])
    if t_end is None:
        r_out = k_end * P["r_t"]
        if np.any(P["e_orb"] < 1):
            apo = P["rp"] * (1 + P["e_orb"]) / np.maximum(1 - P["e_orb"], 1e-300)
            r_out = np.where(P["e_orb"] < 1, np.minimum(r_out, apo), r_out)
        t_end = conic_time_from_pericentre(P["rp"], P["e_orb"], mu, r_out)
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (n,))
    y0 = np.concatenate([x.reshape(n, 9), v.reshape(n, 9)], axis=1)
    E0 = total_energy(x, v, masses, P["G"])
    L0 = total_angular_momentum(x, v, masses)
    r12min = np.linalg.norm(x[:, 2] - x[:, 1], axis=1)
    rMmin = np.stack([np.linalg.norm(x[:, 1] - x[:, 0], axis=1),
                      np.linalg.norm(x[:, 2] - x[:, 0], axis=1)], axis=1)

    def monitor(t, y, idx):
        xx = y[:, :9].reshape(-1, 3, 3)
        np.minimum.at(r12min, idx, np.linalg.norm(xx[:, 2] - xx[:, 1], axis=1))
        np.minimum.at(rMmin[:, 0], idx, np.linalg.norm(xx[:, 1] - xx[:, 0], axis=1))
        np.minimum.at(rMmin[:, 1], idx, np.linalg.norm(xx[:, 2] - xx[:, 0], axis=1))

    nb = np.sqrt(P["G"] * P["m"] / P["a"] ** 3)
    h0 = 1e-3 * np.minimum(2 * np.pi / nb, np.abs(t0))
    y, nacc, ok = integrate_many(_rhs_factory(masses, P["G"]), t0, y0, t_end, h0,
                                 rtol=rtol, atol=atol, monitor=monitor)
    xe = y[:, :9].reshape(n, 3, 3)
    ve = y[:, 9:].reshape(n, 3, 3)
    E1, a1, e1, _ = _pair_energy(xe, ve, P["M"], P["m1"], P["G"], 0, 1)
    E2, a2, e2, _ = _pair_energy(xe, ve, P["M"], P["m2"], P["G"], 0, 2)
    E12, a12, e12, r12 = _pair_energy(xe, ve, P["m1"], P["m2"], P["G"], 1, 2)
    xc = (P["m1"][:, None] * xe[:, 1] + P["m2"][:, None] * xe[:, 2]) / P["m"][:, None]
    Rcm = np.linalg.norm(xc - xe[:, 0], axis=1)
    rH = Rcm * (P["m"] / (3 * P["M"])) ** (1.0 / 3.0)
    bound12 = E12 < 0
    survived = bound12 & (a12 * (1 + e12) < 0.5 * rH)
    outcome = np.full(n, UNSETTLED)
    outcome[survived] = SURVIVED
    dis = ~bound12
    outcome[dis & (E1 < 0) & (E2 >= 0)] = EJECT2
    outcome[dis & (E2 < 0) & (E1 >= 0)] = EJECT1
    outcome[dis & (E1 < 0) & (E2 < 0)] = BOTHBOUND
    outcome[dis & (E1 >= 0) & (E2 >= 0)] = BOTHFREE
    unit = P["G"] * P["m1"] * P["m2"] / P["a"] * (P["M"] / P["m"]) ** (1.0 / 3.0)
    dE = (P["m1"] / P["m"]) * E2 - (P["m2"] / P["m"]) * E1
    Ef = total_energy(xe, ve, masses, P["G"])
    Lf = total_angular_momentum(xe, ve, masses)
    return dict(outcome=outcome, dE=dE / unit, E1=E1 / unit, E2=E2 / unit,
                a1=a1, e1=e1, a2=a2, e2=e2, a12=a12 / P["a"], e12=e12,
                r12min=r12min / P["a"], rMmin=rMmin, energy_error=(Ef - E0) / np.abs(E0),
                angmom_error=np.linalg.norm(Lf - L0, axis=1) / np.linalg.norm(L0, axis=1),
                t0=t0, t_end=t_end, nacc=nacc, ok=ok, x_end=xe, v_end=ve)


def trajectory(setup, r0=None, k0=10.0, t_end=None, k_end=30.0, n_out=2000, rtol=1e-11,
               atol=1e-14):
    """One encounter with SciPy's solve_ivp (DOP853, dense output): an integration path
    independent of integrate_many, for figures and cross-checks. Times are relative to
    the pericentre of the unperturbed centre-of-mass orbit."""
    from scipy.integrate import solve_ivp
    P = _stack([setup])
    if r0 is None:
        r0 = k0 * P["r_t"][0]
    x, v, t0 = initial_state_arrays(P, r0)
    masses = np.array([setup.M, setup.m1, setup.m2])
    if t_end is None:
        mu = setup.G * (setup.M + setup.m)
        t_end = conic_time_from_pericentre(P["rp"], P["e_orb"], mu, k_end * P["r_t"])[0]
    rhs = _rhs_factory(masses[None, :], np.array([setup.G]))
    idx0 = np.zeros(1, dtype=int)
    sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], idx0)[0], (t0[0], t_end),
                    np.concatenate([x[0].ravel(), v[0].ravel()]), method="DOP853",
                    rtol=rtol, atol=atol, dense_output=True)
    tt = np.linspace(t0[0], t_end, n_out)
    Y = sol.sol(tt).T
    return tt, Y[:, :9].reshape(-1, 3, 3), Y[:, 9:].reshape(-1, 3, 3), sol
