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
  1 EJECT2     binary disrupted, m1 bound to M, m2 escapes (exchange)
  2 EJECT1     binary disrupted, m2 bound to M, m1 escapes (exchange)
  3 BOTHBOUND  binary disrupted, both bound to M
  4 BOTHFREE   binary disrupted, both unbound from M
  5 UNSETTLED  m1-m2 bound but wide, or (rare) the inner member unbound from M while the
               outer one is bound to the inner pair: not settled at the end time

Member energies (wave 2, README section "Member energies at finite mass ratio"): Jacobi
split of the hierarchy present at the end. For a disrupted binary the inner pair is M and
the member c with the lower specific two-body energy with M; the other member e is
measured against the barycentre of (M, c):
  E_c = E_in  = mu_in |v_c - v_M|^2/2 - G M m_c/|x_c - x_M|,        mu_in  = M m_c/(M+m_c)
  E_e = E_out = mu_out |v_e - V_Mc|^2/2 - G (M+m_c) m_e/|x_e - X_Mc|, mu_out = m_e (M+m_c)/M_tot
with X_Mc, V_Mc the barycentre of (M, c). E_tot = E_in + E_out + W exactly (zero total
momentum), W = O(G m_e mu_in r^2/R^3) the tidal coupling, so both converge once the outer
body recedes. The energy of the ejected member against M alone (the definition before wave
2, kept as E1_M, E2_M, dE_M) contains mu_eM beta V.v_in with beta = m_c/(M+m_c), which
oscillates with the inner orbit and never decays (lead check V5b). For m1-m2 bound the
members have no separate energies: E1 = E2 = dE = NaN, and E12 (binary) and E_orb (binary
centre of mass about M) are reported. dE = (m1/m) E2 - (m2/m) E1 (KHSR arXiv:1201.4794
ms.tex:1103) of the corrected energies equals E2 - (m2/m)(E_tot - W) and tends to the
restricted E2 as M/m -> infinity. Energies in units of (G m1 m2 / a)(M/m)^(1/3).

Initial data of the code (multi-puncture form, coord/INTERFACES/multi_puncture.md
section 2): puncture_state() gives positions and momenta when the binary's centre of mass
is at a requested distance r0 from M, either placed on the unperturbed conic or reached
by integrating the full problem from k_from r_t (the tidal history of the approach kept);
multi_puncture_block() writes them as the <problem> block of nrpic_cf.
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


def puncture_state(setup, r0=None, k0=None, k_from=None, rtol=1e-12, atol=1e-14):
    """Positions and momenta of the three bodies when the binary's centre of mass is at
    distance r0 (or k0 r_t) from M on the way in: the initial data of a run of the code.

    k_from None (or k_from r_t <= r0): the bodies are placed on the unperturbed conic at r0
    (initial_state; the binary undistorted, effective phase as given). k_from > r0/r_t: the
    encounter is started at k_from r_t (effective phase defined there) and the full
    three-body equations are integrated (SciPy DOP853, terminal event at
    |x_cm - x_M| = r0), so the state carries the tidal distortion and phase shift of the
    approach (P4: a comparison with a run must start from the same state). The result is
    re-centred exactly on the barycentre (the drift removed is reported).

    Returns a dict: names, masses, positions, velocities, momenta (P = m v), t (time
    relative to the pericentre of the unperturbed conic of the start), r0, r_t, r_p,
    k_from, params, and checks: binary a and e, centre-of-mass conic r_p and e
    (osculating), total energy, the re-centring shifts.
    """
    from scipy.integrate import solve_ivp
    P = _stack([setup])
    rt = float(P["r_t"][0])
    if (r0 is None) == (k0 is None):
        raise ValueError("give exactly one of r0 and k0")
    r0 = float(r0 if r0 is not None else k0 * rt)
    masses = np.array([setup.M, setup.m1, setup.m2], dtype=float)
    if k_from is None or k_from * rt <= r0:
        x, v, t0 = initial_state_arrays(P, r0)
        x, v, t = x[0], v[0], float(t0[0])
        mode = "conic"
    else:
        x, v, t0 = initial_state_arrays(P, k_from * rt)
        rhs = _rhs_factory(masses[None, :], np.array([setup.G]))
        idx0 = np.zeros(1, dtype=int)
        mb = setup.m

        def dist(t, y):
            X = y[:9].reshape(3, 3)
            xc = (setup.m1 * X[1] + setup.m2 * X[2]) / mb
            return np.linalg.norm(xc - X[0]) - r0
        dist.terminal = True
        dist.direction = -1
        mu = setup.G * (setup.M + mb)
        t_guess = conic_time_from_pericentre(P["rp"], P["e_orb"], mu, np.array([r0]))[0]
        sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], idx0)[0],
                        (t0[0], -t_guess + 10.0 * (abs(t0[0]) + 1.0)),
                        np.concatenate([x[0].ravel(), v[0].ravel()]), method="DOP853",
                        rtol=rtol, atol=atol, events=dist)
        if sol.t_events[0].size == 0:
            raise RuntimeError("the centre of mass never reached r0")
        t = float(sol.t_events[0][0])
        y = sol.y_events[0][0]
        x, v = y[:9].reshape(3, 3), y[9:].reshape(3, 3)
        mode = f"integrated from {k_from:g} r_t"
    Mt = masses.sum()
    shift_x = (masses[:, None] * x).sum(axis=0) / Mt
    shift_v = (masses[:, None] * v).sum(axis=0) / Mt
    x = x - shift_x
    v = v - shift_v
    en = member_energies(x[None], v[None], masses, setup.G)
    xc = (setup.m1 * x[1] + setup.m2 * x[2]) / setup.m
    vc = (setup.m1 * v[1] + setup.m2 * v[2]) / setup.m
    _, _, e_cm, rp_cm, r_cm = _kepler(xc - x[0], vc - v[0], setup.G * Mt)
    return dict(names=["M", "m1", "m2"], masses=masses, positions=x, velocities=v,
                momenta=masses[:, None] * v, t=t, r0=r0, r_t=rt, r_p=float(P["rp"][0]),
                k_from=k_from, mode=mode, params=asdict(setup),
                checks=dict(binary_a=float(en["a12"][0]), binary_e=float(en["e12"][0]),
                            cm_distance=float(r_cm), cm_conic_e=float(e_cm),
                            cm_conic_rp=float(rp_cm), E_tot=float(en["E_tot"][0]),
                            E_tot_units=float(en["E_tot"][0] / setup.energy_unit),
                            recentre_dx=float(np.abs(shift_x).max()),
                            recentre_dv=float(np.abs(shift_v).max())))


# the settings of the Hills inputs of three_punctures (hills_q10_m8.athinput): every key
# is a <problem> parameter of nrpic_cf (coord/INTERFACES/multi_puncture.md section 2)
PROBLEM_DEFAULTS = (("corr_background", "true"), ("lapse", "precollapsed"),
                    ("puncture_setup", "true"), ("puncture_radius", "1.8"))


def _num(val, scale):
    """Number for an input file: 13 significant digits, round-off below 1e-14 of the
    largest component of its kind written as 0.0."""
    if abs(val) < 1e-14 * scale:
        return "0.0"
    return f"{val:.13g}"


def multi_puncture_block(state, order=("m1", "m2", "M"), corr="approx", spins=None,
                         options=PROBLEM_DEFAULTS, header=True):
    """The <problem> block of nrpic_cf for a puncture_state() (or initial_state()) dict:
    ncomp, then per component comp<c>_type = puncture, _mass, _x1.._x3, _p1.._p3, _s1.._s3,
    _corr, then the options. order: the bodies in component order (default as the inputs
    of three_punctures: the members first, M last, so co_0 and co_1 are the members).
    Masses are written as given (the bare masses of the punctures; see README).
    spins: dict name -> (s1, s2, s3), default zero (written so that the command line can
    change them, interface section 2)."""
    idx = {nm: i for i, nm in enumerate(state["names"])}
    X = np.asarray(state["positions"], dtype=float)
    Pm = np.asarray(state["momenta"], dtype=float)
    sx, sp = np.abs(X).max(), np.abs(Pm).max()
    spins = spins or {}
    lines = []
    if header:
        lines += ["<problem>", "pgen_name       = nrpic_cf"]
    lines.append(f"ncomp           = {len(order)}")
    for c, nm in enumerate(order):
        i = idx[nm]
        s = spins.get(nm, (0.0, 0.0, 0.0))
        lines.append(f"comp{c}_type      = puncture")
        lines.append(f"comp{c}_mass      = {state['masses'][i]:.13g}")
        for k in range(3):
            lines.append(f"comp{c}_x{k + 1}        = {_num(X[i, k], sx)}")
        for k in range(3):
            lines.append(f"comp{c}_p{k + 1}        = {_num(Pm[i, k], sp)}")
        for k in range(3):
            lines.append(f"comp{c}_s{k + 1}        = {float(s[k]):.13g}")
        lines.append(f"comp{c}_corr      = {corr}")
    for key, val in options:
        lines.append(f"{key:<15} = {val}")
    return "\n".join(lines) + "\n"


def parse_problem_block(text):
    """Puncture components of an nrpic_cf <problem> block (or a whole input file):
    returns dict(masses (n,), positions (n, 3), momenta (n, 3), spins (n, 3)) in component
    order; missing momenta and spins are 0."""
    vals, inside = {}, False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("<"):
            inside = line == "<problem>"
            continue
        if inside and "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            vals[k] = v
    n = int(vals["ncomp"])
    comps = [c for c in range(n) if vals.get(f"comp{c}_type") == "puncture"]
    get = lambda c, k: float(vals.get(f"comp{c}_{k}", 0.0))  # noqa: E731
    return dict(component=np.array(comps),
                masses=np.array([get(c, "mass") for c in comps]),
                positions=np.array([[get(c, f"x{k}") for k in (1, 2, 3)] for c in comps]),
                momenta=np.array([[get(c, f"p{k}") for k in (1, 2, 3)] for c in comps]),
                spins=np.array([[get(c, f"s{k}") for k in (1, 2, 3)] for c in comps]))


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


def _kepler(d, w, gm):
    """Specific energy, semi-major axis (inf if unbound), eccentricity, pericentre of the
    relative state (d, w) (..., 3) with gravitational parameter gm (...)."""
    r = np.linalg.norm(d, axis=-1)
    eps = 0.5 * np.sum(w * w, axis=-1) - gm / r
    h2 = np.sum(np.cross(d, w) ** 2, axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sma = np.where(eps < 0, -gm / (2 * eps), np.inf)
        ecc = np.sqrt(np.maximum(1 + 2 * eps * h2 / gm ** 2, 0.0))
        rp = h2 / gm / (1 + ecc)
    return eps, sma, ecc, rp, r


def member_energies(x, v, masses, G=1.0):
    """Energies of the members at the states x, v (..., 3, 3), bodies [M, m1, m2], masses
    (..., 3) or (3,), G scalar or (...). Plain energies (no unit). Returns a dict:

      E1, E2      corrected member energies (Jacobi split, module docstring): the inner
                  member against M, the outer member against the barycentre of M and the
                  inner member
      inner       1 or 2: the member with the lower specific two-body energy with M
      E_in, E_out, W, E_tot   E_tot = E_in + E_out + W (W: tidal coupling, exact remainder)
      E1_M, E2_M  two-body energy of each member with M alone (the definition before wave 2)
      a1, e1, a2, e2          osculating elements of each member's orbit about M
      a_in, e_in, rp_in       elements of the inner pair (the captured member's orbit)
      E12, a12, e12, r12      binary m1-m2
      E_orb, W_bin            binary centre of mass about M; E_tot = E12 + E_orb + W_bin
    """
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    shp = x.shape[:-2]
    ms = np.broadcast_to(np.asarray(masses, dtype=float), shp + (3,))
    G = np.broadcast_to(np.asarray(G, dtype=float), shp)
    M, m1, m2 = ms[..., 0], ms[..., 1], ms[..., 2]
    Mt = M + m1 + m2
    out = {}
    # two-body energies with M alone (old definition) and orbital elements
    epsM, smaM, eccM = [], [], []
    for i, mi in ((1, m1), (2, m2)):
        eps, sma, ecc, _, _ = _kepler(x[..., i, :] - x[..., 0, :], v[..., i, :] - v[..., 0, :],
                                      G * (M + mi))
        out[f"E{i}_M"] = M * mi / (M + mi) * eps
        out[f"a{i}"], out[f"e{i}"] = sma, ecc
        epsM.append(eps)
    inner = np.where(epsM[0] <= epsM[1], 1, 2)
    # Jacobi split with inner pair (M, c) and outer member e
    c = inner
    xc =np.where((c == 1)[..., None], x[..., 1, :], x[..., 2, :])
    vc = np.where((c == 1)[..., None], v[..., 1, :], v[..., 2, :])
    xe = np.where((c == 1)[..., None], x[..., 2, :], x[..., 1, :])
    ve = np.where((c == 1)[..., None], v[..., 2, :], v[..., 1, :])
    mc = np.where(c == 1, m1, m2)
    me = np.where(c == 1, m2, m1)
    Mc = M + mc
    XMc = (M[..., None] * x[..., 0, :] + mc[..., None] * xc) / Mc[..., None]
    VMc = (M[..., None] * v[..., 0, :] + mc[..., None] * vc) / Mc[..., None]
    eps_in, a_in, e_in, rp_in, _ = _kepler(xc - x[..., 0, :], vc - v[..., 0, :], G * Mc)
    mu_in = M * mc / Mc
    E_in = mu_in * eps_in
    eps_out, _, _, _, _ = _kepler(xe - XMc, ve - VMc, G * Mt)
    mu_out = me * Mc / Mt
    E_out = mu_out * eps_out
    E_tot = _energy_general(x, v, ms, G)
    out.update(inner=inner, E_in=E_in, E_out=E_out, E_tot=E_tot, W=E_tot - E_in - E_out,
               a_in=a_in, e_in=e_in, rp_in=rp_in)
    out["E1"] = np.where(c == 1, E_in, E_out)
    out["E2"] = np.where(c == 1, E_out, E_in)
    # binary and its centre of mass about M
    m = m1 + m2
    eps12, a12, e12, _, r12 = _kepler(x[..., 2, :] - x[..., 1, :], v[..., 2, :] - v[..., 1, :], G * m)
    Xb = (m1[..., None] * x[..., 1, :] + m2[..., None] * x[..., 2, :]) / m[..., None]
    Vb = (m1[..., None] * v[..., 1, :] + m2[..., None] * v[..., 2, :]) / m[..., None]
    eps_orb, _, _, _, _ = _kepler(Xb - x[..., 0, :], Vb - v[..., 0, :], G * Mt)
    E12 = m1 * m2 / m * eps12
    E_orb = M * m / Mt * eps_orb
    out.update(E12=E12, a12=a12, e12=e12, r12=r12, E_orb=E_orb, W_bin=E_tot - E12 - E_orb)
    return out


def _energy_general(x, v, ms, G):
    """Total energy for states (..., 3, 3) in the frame given (kinetic of the barycentre
    removed, so the Jacobi identity holds for any total momentum)."""
    Mt = ms.sum(axis=-1)
    P = np.sum(ms[..., None] * v, axis=-2)
    kin = 0.5 * np.sum(ms * np.sum(v * v, axis=-1), axis=-1) - 0.5 * np.sum(P * P, axis=-1) / Mt
    pot = 0.0
    for i, j in ((0, 1), (0, 2), (1, 2)):
        pot = pot - G * ms[..., i] * ms[..., j] / np.linalg.norm(x[..., j, :] - x[..., i, :], axis=-1)
    return kin + pot


def classify(en, x, v, masses, G=1.0):
    """Outcome classes (module docstring) from member_energies() output en at the states
    x, v (n, 3, 3). Returns (outcome with the corrected energies, outcome with the energies
    against M alone as before wave 2)."""
    ms = np.broadcast_to(np.asarray(masses, dtype=float), x.shape[:-2] + (3,))
    M, m = ms[..., 0], ms[..., 1] + ms[..., 2]
    Xb = (ms[..., 1, None] * x[..., 1, :] + ms[..., 2, None] * x[..., 2, :]) / m[..., None]
    Rcm = np.linalg.norm(Xb - x[..., 0, :], axis=-1)
    rH = Rcm * (m / (3 * M)) ** (1.0 / 3.0)
    bound12 = en["E12"] < 0
    survived = bound12 & (en["a12"] * (1 + en["e12"]) < 0.5 * rH)
    dis = ~bound12
    out = []
    for new in (True, False):
        o = np.full(bound12.shape, UNSETTLED)
        o[survived] = SURVIVED
        if new:
            cap = en["E_in"] < 0
            esc = en["E_out"] >= 0
            single = dis & cap & esc
            o[single & (en["inner"] == 1)] = EJECT2
            o[single & (en["inner"] == 2)] = EJECT1
            o[dis & cap & ~esc] = BOTHBOUND
            o[dis & ~cap & esc] = BOTHFREE
        else:
            E1, E2 = en["E1_M"], en["E2_M"]
            o[dis & (E1 < 0) & (E2 >= 0)] = EJECT2
            o[dis & (E2 < 0) & (E1 >= 0)] = EJECT1
            o[dis & (E1 < 0) & (E2 < 0)] = BOTHBOUND
            o[dis & (E1 >= 0) & (E2 >= 0)] = BOTHFREE
        out.append(o)
    return out[0], out[1]


def scatter(setups, r0=None, k0=10.0, k_end=30.0, t_end=None, rtol=1e-11, atol=1e-14):
    """Integrate a list of HillsSetup from the start (r0, default k0 r_t) to the time at
    which the unperturbed centre-of-mass conic would be at k_end r_t on the way out (or
    t_end after the pericentre). Returns a dict of arrays; see the module docstring.
    Energies in units of (G m1 m2/a)(M/m)^(1/3): E1, E2, dE (corrected; NaN while m1-m2
    are bound), E1_M, E2_M, dE_M (against M alone, as before wave 2), E_in, E_out, W_end,
    E_tot, E12, E_orb, dE_orb (change of E_orb from the start); outcome (corrected
    energies) and outcome_M (as before wave 2)."""
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
    unit = P["G"] * P["m1"] * P["m2"] / P["a"] * (P["M"] / P["m"]) ** (1.0 / 3.0)
    res = evolve_states(masses, x, v, t0, t_end, P["G"], rtol=rtol, atol=atol,
                        h_scale=np.minimum(2 * np.pi / np.sqrt(P["G"] * P["m"] / P["a"] ** 3),
                                           np.abs(t0)))
    res.update(_energies_in_units(res, masses, P["G"], unit, x, v))
    res["a12"] = res["a12"] / P["a"]
    res["r12min"] = res["r12min"] / P["a"]
    res.update(t0=t0, t_end=t_end)
    return res


def _energies_in_units(res, masses, G, unit, x0, v0):
    """Energies of evolve_states() output in units, NaN where m1-m2 are bound."""
    en = res["_en"]
    bound12 = en["E12"] < 0
    out = {}
    for k in ("E1", "E2", "E1_M", "E2_M", "E_in", "E_out", "W", "E_tot", "E12", "E_orb"):
        out[k] = en[k] / unit
    out["W_end"] = out.pop("W")
    m1, m2 = masses[:, 1], masses[:, 2]
    m = m1 + m2
    for k in ("E1", "E2"):
        out[k] = np.where(bound12, np.nan, out[k])
    out["dE"] = (m1 / m) * out["E2"] - (m2 / m) * out["E1"]
    out["dE_M"] = (m1 / m) * out["E2_M"] - (m2 / m) * out["E1_M"]
    en0 = member_energies(x0, v0, masses, G)
    out["dE_orb"] = (en["E_orb"] - en0["E_orb"]) / unit
    return out


def evolve_states(masses, x, v, t0, t_end, G=1.0, rtol=1e-11, atol=1e-14, h_scale=None):
    """Integrate states x, v (n, 3, 3) (bodies [M, m1, m2], masses (n, 3)) from t0 to t_end
    (n,) and classify the end. Returns a dict: outcome, outcome_M, member_energies() fields
    (plain energies, under '_en' and the elements a1, e1, a2, e2, a12, e12, a_in, e_in,
    rp_in, inner at the top level), r12min, rMmin (n, 2), energy_error, angmom_error,
    nacc, ok, x_end, v_end."""
    x = np.asarray(x, dtype=float)
    v = np.asarray(v, dtype=float)
    n = x.shape[0]
    masses = np.broadcast_to(np.asarray(masses, dtype=float), (n, 3))
    G = np.broadcast_to(np.asarray(G, dtype=float), (n,))
    t0 = np.broadcast_to(np.asarray(t0, dtype=float), (n,))
    t_end = np.broadcast_to(np.asarray(t_end, dtype=float), (n,))
    y0 = np.concatenate([x.reshape(n, 9), v.reshape(n, 9)], axis=1)
    E0 = total_energy(x, v, masses, G)
    L0 = total_angular_momentum(x, v, masses)
    r12min = np.linalg.norm(x[:, 2] - x[:, 1], axis=1)
    rMmin = np.stack([np.linalg.norm(x[:, 1] - x[:, 0], axis=1),
                      np.linalg.norm(x[:, 2] - x[:, 0], axis=1)], axis=1)

    def monitor(t, y, idx):
        xx = y[:, :9].reshape(-1, 3, 3)
        np.minimum.at(r12min, idx, np.linalg.norm(xx[:, 2] - xx[:, 1], axis=1))
        np.minimum.at(rMmin[:, 0], idx, np.linalg.norm(xx[:, 1] - xx[:, 0], axis=1))
        np.minimum.at(rMmin[:, 1], idx, np.linalg.norm(xx[:, 2] - xx[:, 0], axis=1))

    if h_scale is None:
        r12 = np.linalg.norm(x[:, 2] - x[:, 1], axis=1)
        h_scale = 2 * np.pi * np.sqrt(r12 ** 3 / (G * (masses[:, 1] + masses[:, 2])))
    h0 = 1e-3 * h_scale
    y, nacc, ok = integrate_many(_rhs_factory(masses, G), t0, y0, t_end, h0,
                                 rtol=rtol, atol=atol, monitor=monitor)
    xe = y[:, :9].reshape(n, 3, 3)
    ve = y[:, 9:].reshape(n, 3, 3)
    en = member_energies(xe, ve, masses, G)
    outcome, outcome_M = classify(en, xe, ve, masses, G)
    Ef = total_energy(xe, ve, masses, G)
    Lf = total_angular_momentum(xe, ve, masses)
    res = dict(outcome=outcome, outcome_M=outcome_M, _en=en,
               r12min=r12min, rMmin=rMmin, energy_error=(Ef - E0) / np.abs(E0),
               angmom_error=np.linalg.norm(Lf - L0, axis=1) / np.linalg.norm(L0, axis=1),
               nacc=nacc, ok=ok, x_end=xe, v_end=ve)
    for k in ("a1", "e1", "a2", "e2", "a12", "e12", "a_in", "e_in", "rp_in", "inner"):
        res[k] = en[k]
    return res


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
