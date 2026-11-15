"""Homogeneous cold ellipsoid in an Einstein-de Sitter background.

Semi-analytic reference for the Newtonian precursor scan of track A (A-pre-3 under
decision 0010). Units and start convention of arXiv:2605.04487 (see tophat.py and
PAPER_SETUP.md): G = c = 1, H_k = 1, t_k = 2/3, a(t_k) = 1, Lagrangian radius R_L = 1,
mass M = M_k = 1/2, Schwarzschild radius r_g = 2 G M = 1.

Gravity of a homogeneous ellipsoid of mass M, semi-axes A_i (inside, along axis i):
    g_i = -2 pi G rho_e alpha_i x_i = -G M R_D(A_j^2, A_k^2, A_i^2) x_i,
    alpha_i = (2/3) A_1 A_2 A_3 R_D(A_j^2, A_k^2, A_i^2),  sum_i alpha_i = 2,
with Carlson's symmetric integral R_D [BACKGROUND: Chandrasekhar 1969; the R_D form
follows from int_0^inf dl / ((A_i^2+l) Delta(l)) = (2/3) R_D]. The product
A_i R_D(..., A_i^2) stays finite when A_i -> 0 (pancake): the code never forms
rho_e or alpha_i alone.

Three ways of placing the patch in the background (JOURNAL.md, entry 1):
    isolated : A_i'' = g_i                                   (patch alone; Lin-Mestel-Shu)
    embedded : A_i'' = g_i - (4pi/3) G rho_b A_i + 2 pi G rho_b alpha_i A_i
               (patch fills an ellipsoidal hole of a uniform background; no outer tide)
    added    : A_i'' = g_i - (4pi/3) G rho_b A_i
               (patch added on top of a uniform background; literal reading of
               2605.04487 Eqs. x_eom and force_pp)
In spherical symmetry isolated and embedded coincide (Birkhoff).

Optional special-relativistic kinematics of the axis end points ("sr=True"), following
2605.04487 Eqs. q_def_xdot, qdot_phi, gamma_of_q (source lines 382-458): comoving
x_i = A_i/a, q_i = a^2 gamma x_i', gamma = sqrt(1 + q^2/a^2), q_i' = a (g_i - (a''/a) A_i).
This keeps the end point of each axis on the homogeneous-ellipsoid field; the interior
of a relativistic patch does not stay homogeneous, so it is an estimate of the size of
the kinematic correction, not an exact solution [JUDGEMENT].

Through a pancake (A_i -> 0) the cold homogeneous ellipsoid passes through itself: the
map x -> A(t) xi changes sign for all particles at once and the density stays uniform.
The collapse event is taken at |A_i| = 1e-8 of its initial value (a sphere is
singular at A = 0; for a pancake the acceleration stays finite and the time error is of
order 1e-8 of the collapse time). The integration continues by reflection there
(A_i' -> -A_i'); events after the
first collapse describe this idealized continuation, not a real multi-stream flow.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import ellipe, elliprd

from tophat import G, M_K, T_K, a_of_t, hubble, rho_b, t_of_a

MODELS = ("isolated", "embedded", "added")
STOP = 1e-8   # collapse of axis i is registered at |A_i| = STOP x (its initial value)


# ---------------------------------------------------------------- parameters
def abg_from_dep(deltaL, e, p):
    """(alpha, beta, gamma) from the linear contrast at t_k and the ellipticity and
    prolateness, 2605.04487 Eq. abg_inverse_ep (source lines 1179-1186)."""
    return (deltaL / 3.0 * (1.0 + 3.0 * e + p), deltaL / 3.0 * (1.0 - 2.0 * p),
            deltaL / 3.0 * (1.0 - 3.0 * e + p))


def ep_from_abg(a, b, c):
    """Ellipticity and prolateness, 2605.04487 Eq. ep_def_abg (lines 1172-1177)."""
    s = a + b + c
    return (a - c) / (2.0 * s), (a - 2.0 * b + c) / (2.0 * s)


# ---------------------------------------------------------------- gravity
def rd_terms(A):
    """D_i = R_D(A_j^2, A_k^2, A_i^2) for i = 0, 1, 2."""
    s = np.asarray(A, dtype=float) ** 2
    return np.array([elliprd(s[1], s[2], s[0]), elliprd(s[2], s[0], s[1]),
                     elliprd(s[0], s[1], s[2])])


def alphas(A):
    A = np.abs(np.asarray(A, dtype=float))
    return (2.0 / 3.0) * A[0] * A[1] * A[2] * rd_terms(A)


def alphas_spheroid(a, c):
    """Closed forms for a spheroid with semi-axes (a, a, c) [BACKGROUND: Chandrasekhar
    1969, Ellipsoidal Figures of Equilibrium, Ch. 3; Binney and Tremaine Table 2.1]."""
    if c < a:                               # oblate
        e = np.sqrt(1.0 - (c / a) ** 2)
        s = np.sqrt(1.0 - e * e)
        a1 = s / e ** 3 * (np.arcsin(e) - e * s)
        a3 = 2.0 / e ** 2 * (1.0 - s * np.arcsin(e) / e)
    elif c > a:                             # prolate
        e = np.sqrt(1.0 - (a / c) ** 2)
        a3 = (1.0 - e * e) / e ** 3 * (np.log((1.0 + e) / (1.0 - e)) - 2.0 * e)
        a1 = 1.0 - 0.5 * a3
    else:
        a1 = a3 = 2.0 / 3.0
    return np.array([a1, a1, a3])


def accel(t, A, model, M=M_K):
    """Physical acceleration of the end point of each axis (signed A allowed)."""
    A = np.asarray(A, dtype=float)
    D = rd_terms(A)
    g = -G * M * A * D
    if model == "isolated":
        return g
    rb = rho_b(t)
    g = g - (4.0 * np.pi / 3.0) * G * rb * A
    if model == "added":
        return g
    if model == "embedded":
        alpha = (2.0 / 3.0) * np.prod(np.abs(A)) * D
        return g + 2.0 * np.pi * G * rb * alpha * A
    raise ValueError(model)


# ---------------------------------------------------------------- Zel'dovich
def za_axes(lams, a, RL=(1.0, 1.0, 1.0)):
    """Zel'dovich semi-axes a (1 - a lambda_i) R_Li (2605.04487 Eq. ZA_positions times a)."""
    return a * (1.0 - a * np.asarray(lams)) * np.asarray(RL)


def za_initial(lams, a0, RL=(1.0, 1.0, 1.0)):
    t0 = float(t_of_a(a0))
    H0 = float(hubble(t0))
    lams = np.asarray(lams, dtype=float)
    RL = np.asarray(RL, dtype=float)
    return t0, a0 * (1.0 - a0 * lams) * RL, H0 * a0 * (1.0 - 2.0 * a0 * lams) * RL


def hoop_C(A):
    """Hoop: largest circumference, the perimeter of the principal section through the
    two largest semi-axes (for a pancake, the ellipse of 1609.01588 lines 564-567)."""
    s = np.sort(np.abs(np.asarray(A, dtype=float)))
    a, b = s[2], s[1]
    return 4.0 * a * ellipe(1.0 - (b / a) ** 2)


def hoop_h(A, M=M_K):
    """h = C / (2 pi r_g), r_g = 2 G M; black hole by the hoop criterion if h <~ 1."""
    return hoop_C(A) / (2.0 * np.pi * 2.0 * G * M)


def h_za_closed(al, be, ga):
    """Zel'dovich hoop at first collapse, 1609.01588 Eq. s_3 (lines 603-607), with
    b/a = a/a(t_i), a(t_i) = 1. E is the complete elliptic integral of the second kind of
    modulus e; scipy's ellipe takes the parameter m = e^2."""
    m = 1.0 - ((al - be) / (al - ga)) ** 2
    return 2.0 / np.pi * (al - ga) / al ** 2 * ellipe(m)


# ---------------------------------------------------------------- evolution
def evolve(lams, a0=None, model="isolated", sr=False, RL=(1.0, 1.0, 1.0),
           n_collapse=1, t_end=None, rtol=1e-11, atol=1e-13, M=None, max_step=np.inf):
    """Integrate from Zel'dovich data at a0 (default 1/(2 lambda_1), the start of
    2605.04487) until n_collapse axis collapses or t_end (default 1e6 t0).

    Returns dict: t0, a0, collapses (list of dicts: t, t_over_tk, a, axis, A, h),
    turnarounds (list of (t, axis)), samples t, A (n x 3), h_min_before_first, and the
    status of the last segment."""
    lams = np.asarray(lams, dtype=float)
    RL = np.asarray(RL, dtype=float)
    if M is None:
        M = M_K * float(np.prod(RL))
    if a0 is None:
        a0 = 0.5 / lams.max()
    t0, A0, V0 = za_initial(lams, a0, RL)
    if t_end is None:
        t_end = 1e6 * t0

    if sr:                              # True: SR end points; "comoving": same, gamma = 1
        lorentz = sr is True
        H0 = float(hubble(t0))
        xd0 = -H0 * a0 * lams * RL                    # comoving velocity, Eq. ZA_velocities
        g0 = 1.0 / np.sqrt(1.0 - a0 ** 2 * xd0 ** 2) if lorentz else np.ones(3)
        y0 = np.concatenate([A0 / a0, a0 ** 2 * g0 * xd0])

        def rhs(t, y):
            a = float(a_of_t(t))
            x, q = y[:3], y[3:]
            A = a * x
            add_over_a = -(4.0 * np.pi / 3.0) * G * rho_b(t)
            gpec = accel(t, A, model, M) - add_over_a * A
            gam = np.sqrt(1.0 + (q / a) ** 2) if lorentz else 1.0
            return np.concatenate([q / (a * a * gam), a * gpec])

        def phys(t, y):
            a = float(a_of_t(t))
            return a * y[:3]
    else:
        y0 = np.concatenate([A0, V0])

        def rhs(t, y):
            return np.concatenate([y[3:], accel(t, y[:3], model, M)])

        def phys(t, y):
            return y[:3]

    eps_stop = STOP * np.abs(y0[:3])    # collapse event of axis i at |A_i| = eps_stop[i]

    def mk_zero(i):
        def f(t, y):
            return y[i] - eps_stop[i]
        f.terminal = True
        f.direction = -1
        return f

    def mk_ta(i):                       # Newtonian runs: A_i' = 0; sr runs: q_i = 0
        def f(t, y):
            return y[3 + i]
        f.terminal = False
        f.direction = -1
        return f

    events = [mk_zero(i) for i in range(3)] + [mk_ta(i) for i in range(3)]
    out = dict(t0=t0, a0=a0, lams=lams.tolist(), model=model, sr=sr, RL=RL.tolist(),
               M=M, collapses=[], turnarounds=[])
    ts, As = [], []
    t, y = t0, y0.copy()
    status = None
    while len(out["collapses"]) < n_collapse and t < t_end:
        sol = solve_ivp(rhs, (t, t_end), y, method="DOP853", rtol=rtol, atol=atol,
                        events=events, dense_output=False, max_step=max_step)
        status = sol.status
        for i in range(3):
            for te in sol.t_events[3 + i]:
                out["turnarounds"].append((float(te), i))
        ts.append(sol.t)
        As.append(np.array([phys(tt, yy) for tt, yy in zip(sol.t, sol.y.T)]))
        hit = [(sol.t_events[i][0], i) for i in range(3) if len(sol.t_events[i])]
        if not hit:
            t = sol.t[-1]
            break
        te, i = min(hit)
        ye = sol.y_events[i][0].copy()
        Ae = phys(te, ye)
        Ae_abs = np.abs(Ae)
        Ae_abs[i] = 0.0
        out["collapses"].append(dict(t=float(te), t_over_tk=float(te / T_K),
                                     a=float(a_of_t(te)), axis=int(i),
                                     A=[float(v) for v in Ae_abs],
                                     h=float(hoop_h(Ae_abs, M))))
        # pass-through continuation (reflection)
        ye[i] = eps_stop[i] * (1.0 + 1e-6)
        ye[3 + i] = -ye[3 + i]
        t, y = te, ye
    out["status"] = status
    out["t"] = np.concatenate(ts)
    out["A"] = np.concatenate(As)
    first = out["collapses"][0]["t"] if out["collapses"] else np.inf
    m = out["t"] <= first
    hh = np.array([hoop_h(A, M) for A in out["A"][m]])
    out["h_min_before_first"] = float(min(hh.min(), out["collapses"][0]["h"])
                                      if out["collapses"] else hh.min())
    return out


def first_collapse(deltaL, e, p, model="isolated", sr=False, a0=None, **kw):
    """Time (t/t_k), scale factor, axis and hoop ratio of the first collapse."""
    lams = abg_from_dep(deltaL, e, p)
    r = evolve(lams, a0=a0, model=model, sr=sr, n_collapse=1, **kw)
    c = r["collapses"][0] if r["collapses"] else None
    return dict(deltaL=deltaL, e=e, p=p, alpha=lams[0], beta=lams[1], gamma=lams[2],
                model=model, sr=sr, t0_over_tk=r["t0"] / T_K,
                t1_over_tk=c["t_over_tk"] if c else np.nan,
                a1=c["a"] if c else np.nan, axis=c["axis"] if c else -1,
                A2_over_rg=sorted(c["A"])[1] / (2 * G * r["M"]) if c else np.nan,
                A3_over_rg=sorted(c["A"])[2] / (2 * G * r["M"]) if c else np.nan,
                h1=c["h"] if c else np.nan)
