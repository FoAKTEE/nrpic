"""Semi-analytic baseline of Track B (B-pre-4 under decision 0010): a homogeneous ellipsoid
(Zel'dovich pancake of finite extent) collapsing in an Einstein-de Sitter background, its
mass quadrupole and the quadrupole-formula gravitational-wave signal.

Library only (no input or output); `run_baseline.py` runs the checks.

Units: G = c = 1, horizon entry t_k = 1, a(t) = (t/t_k)^(2/3), H_k = 2/(3 t_k), Lagrangian
radius R_L = c/H_k (physical radius of the undeformed patch at a = 1), patch mass
M = c^3/(2 G H_k), background density rho_b = 1/(6 pi G t^2).
Sources of these choices: arXiv:2605.04487 main_v3.tex lines 996-1002, 2149-2156;
arXiv:2403.15126 pII_GW_Vir_C2_Arx.tex lines 446-451, 485.

Models of the semi-axes R_i(t) (principal frame; no rotation):
  "ZA": R_i = a R_L (1 - a lambda_i)                     (2605.04487 lines 2831-2838)
  "A" : R_i'' = -(4 pi G/3) rho_b R_i - 2 pi G (rho_p - rho_b) A_i R_i   (embedded)
  "B" : R_i'' = -(4 pi G/3) rho_b R_i - 2 pi G rho_p A_i R_i             (literal 2605.04487)
  "C" : R_i'' = -2 pi G rho_p A_i R_i                                    (static, 2403.15126)
with rho_p = 3 M / (4 pi R_1 R_2 R_3) and the interior shape coefficients of a homogeneous
ellipsoid A_i = R_1 R_2 R_3 int_0^inf du / ((R_i^2 + u) sqrt(prod_j (R_j^2 + u)))
= (2/3) R_1 R_2 R_3 R_D(R_j^2, R_k^2, R_i^2) (Carlson), sum_i A_i = 2.
The ODE models start from the Zel'dovich state at the first-axis turnaround
t_turn = (2 alpha)^(-3/2) t_k (2605.04487 lines 1036-1060). The cold affine flow is an
exact (singular) Vlasov-Poisson solution: it passes through R_i = 0 and stays a
homogeneous ellipsoid; the right-hand side uses |R_i|, so R_i changes sign at a crossing.

Quadrupole (trace-free, about the centre, physical coordinates):
  Q_ii = (M/15) (3 R_i^2 - sum_j R_j^2)                  (2605.04487 lines 2866-2875)
Power P = (G/(5 c^5)) sum_ij Q'''_ij Q'''_ij             (2605.04487 line 1883)
Spectrum (one-sided, X(omega) = int x(t) exp(-i omega t) dt):
  dE/dln omega = (G omega / (5 pi c^5)) sum_ij |Q'''_ij(omega)|^2.
"""
import numpy as np
import mpmath
from scipy.integrate import solve_ivp
from scipy.special import elliprd

G = 1.0
C = 1.0
TK = 1.0
HK = 2.0/(3.0*TK)
RL = C/HK
MASS = C**3/(2.0*G*HK)


def a_of_t(t):
    return (np.asarray(t, dtype=float)/TK)**(2.0/3.0)


def adot_of_t(t):
    t = np.asarray(t, dtype=float)
    return (2.0/3.0)*a_of_t(t)/t


def rho_b(t):
    return 1.0/(6.0*np.pi*G*np.asarray(t, dtype=float)**2)


def t_turn(alpha):
    """First-axis turnaround of the Zel'dovich ellipsoid, a = 1/(2 alpha)."""
    return TK*(2.0*alpha)**-1.5


def t_col_za(lam):
    """Zel'dovich collapse of an axis, a = 1/lambda (lambda > 0)."""
    return TK*lam**-1.5


def shape_S(lam):
    al, be, ga = lam
    return al**4 + be**4 + ga**4 - al**2*be**2 - al**2*ga**2 - be**2*ga**2


# ---------------------------------------------------------------- Zel'dovich ellipsoid

def za_axes(t, lam):
    t = np.atleast_1d(np.asarray(t, dtype=float))
    a = a_of_t(t)[:, None]
    return a*RL*(1.0 - a*np.asarray(lam)[None, :])


def za_axes_dot(t, lam):
    t = np.atleast_1d(np.asarray(t, dtype=float))
    a = a_of_t(t)[:, None]
    ad = adot_of_t(t)[:, None]
    return ad*RL*(1.0 - 2.0*a*np.asarray(lam)[None, :])


def za_Q3_coeff(lam):
    """Q'''_ii(t) = coeff_i t^(-1/3) for the Zel'dovich ellipsoid (my derivation:
    Q_ii = (M R_L^2/15)[-2 (t/t_k)^2 (3 l_i - sum l) + (t/t_k)^(8/3) (3 l_i^2 - sum l^2)],
    and d^3 t^2/dt^3 = 0)."""
    lam = np.asarray(lam, dtype=float)
    return (MASS*RL**2/15.0)*(80.0/27.0)*TK**(-8.0/3.0)*(3*lam**2 - np.sum(lam**2))


def za_Q3(t, lam):
    t = np.atleast_1d(np.asarray(t, dtype=float))
    return za_Q3_coeff(lam)[None, :]*t[:, None]**(-1.0/3.0)


def za_energy(t1, t2, lam):
    """Energy radiated by the Zel'dovich ellipsoid between t1 and t2 (my closed form):
    E = (8/15) M c^2 S [(t2/t_k)^(1/3) - (t1/t_k)^(1/3)]."""
    return (8.0/15.0)*MASS*C**2*shape_S(lam)*((t2/TK)**(1/3) - (t1/TK)**(1/3))


def E13(z):
    """Generalized exponential integral E_1/3(z) = int_1^inf u^(-1/3) exp(-z u) du."""
    return complex(mpmath.expint(mpmath.mpf(1)/3, z))


def za_window_ft(omega, t1, t2):
    """int_t1^t2 t^(-1/3) exp(-i omega t) dt = t1^(2/3) E(i w t1) - t2^(2/3) E(i w t2)."""
    return (t1**(2/3)*E13(1j*omega*t1) - t2**(2/3)*E13(1j*omega*t2))


def za_spectrum(omega, lam, t1, t2):
    """dE/dln omega of the Zel'dovich ellipsoid emitting on [t1, t2] (my derivation)."""
    c3 = za_Q3_coeff(lam)
    out = np.empty(len(omega))
    for n, w in enumerate(omega):
        out[n] = G*w/(5*np.pi*C**5)*np.sum(c3**2)*abs(za_window_ft(w, t1, t2))**2
    return out


def za_spectrum_2605(omega, lam):
    """Equation of arXiv:2605.04487 main_v3.tex lines 2896-2918 (window [t_k, t_col])."""
    al = lam[0]
    tc = t_col_za(al)
    out = np.empty(len(omega))
    pref = 32.0/(135.0*np.pi)*(C**5/G)*(G*MASS/C**3)**2*shape_S(lam)
    for n, w in enumerate(omega):
        out[n] = pref*w*abs(E13(1j*w*TK) - E13(1j*w*tc)/al)**2
    return out


# ---------------------------------------------------------------- ellipsoid dynamics

def shape_coeffs(R):
    """A_i of a homogeneous ellipsoid with semi-axes R (positive; real or complex)."""
    x, y, z = R[0]**2, R[1]**2, R[2]**2
    p = R[0]*R[1]*R[2]
    return np.array([(2.0/3.0)*p*elliprd(y, z, x),
                     (2.0/3.0)*p*elliprd(x, z, y),
                     (2.0/3.0)*p*elliprd(x, y, z)])


def _fcoef(t, Ra, model):
    """f_i with R_i'' = f_i R_i; Ra are the absolute values of the axes."""
    A = shape_coeffs(Ra)
    rp = 3.0*MASS/(4.0*np.pi*Ra[0]*Ra[1]*Ra[2])
    rb = rho_b(t)
    if model == "A":
        return -(4*np.pi*G/3)*rb - 2*np.pi*G*(rp - rb)*A
    if model == "B":
        return -(4*np.pi*G/3)*rb - 2*np.pi*G*rp*A
    if model == "C":
        return -2*np.pi*G*rp*A
    raise ValueError(model)


def _dfcoef_dt(t, Ra, model):
    """Partial time derivative of f at fixed axes (rho_b' = -2 rho_b / t)."""
    rbd = -2.0*rho_b(t)/t
    if model == "A":
        return -(4*np.pi*G/3)*rbd + 2*np.pi*G*rbd*shape_coeffs(Ra)
    if model == "B":
        return -(4*np.pi*G/3)*rbd*np.ones(3)
    return np.zeros(3)


def accel(t, R, model):
    R = np.asarray(R, dtype=float)
    return _fcoef(t, np.abs(R), model)*R


def jerk(t, R, V, model, h=1e-30):
    """R''' = d/dt (f R) = (df/dt) R + f V; the derivative of f along the flow by a
    complex step (exact to rounding; the Carlson function accepts complex arguments)."""
    R = np.asarray(R, dtype=float)
    V = np.asarray(V, dtype=float)
    Ra = np.abs(R)
    Va = np.sign(R)*V
    f = _fcoef(t, Ra, model)
    fc = _fcoef(t, Ra + 1j*h*Va, model)
    dfdR = np.imag(fc)/h
    fdot = dfdR + _dfcoef_dt(t, Ra, model)
    return fdot*R + f*V


def quad_derivs(R, V, Acc, Jrk):
    """Diagonal Q and its first three time derivatives (rows: 0..3; columns: i)."""
    s0 = R**2
    s1 = 2*R*V
    s2 = 2*(V**2 + R*Acc)
    s3 = 2*(3*V*Acc + R*Jrk)
    out = []
    for s in (s0, s1, s2, s3):
        out.append((MASS/15.0)*(3*s - np.sum(s, axis=-1, keepdims=True)))
    return out


def power(Q3):
    return (G/(5*C**5))*np.sum(Q3**2, axis=-1)


def initial_state(lam, t0=None):
    lam = np.asarray(lam, dtype=float)
    if t0 is None:
        t0 = t_turn(lam[0])
    return t0, za_axes(t0, lam)[0], za_axes_dot(t0, lam)[0]


def integrate(lam, model, t_end, t0=None, rtol=1e-12, atol=1e-14, max_cross=12):
    """Integrate an ellipsoid model from the Zel'dovich state at t0 (default t_turn) to
    t_end. Returns a dict with the segments (dense solutions), the crossing events
    (time, axis) and the radiated energy E(t) carried as an extra state variable."""
    t0, R0, V0 = initial_state(lam, t0)

    def rhs(t, y):
        R, V = y[0:3], y[3:6]
        Acc = accel(t, R, model)
        Jrk = jerk(t, R, V, model)
        Q3 = quad_derivs(R, V, Acc, Jrk)[3]
        return np.concatenate([V, Acc, [power(Q3)]])

    events = []
    for i in range(3):
        def ev(t, y, i=i):
            return y[i]
        ev.terminal = True
        ev.direction = 0
        events.append(ev)

    y0 = np.concatenate([R0, V0, [0.0]])
    t = t0
    segs, cross = [], []
    while t < t_end and len(cross) <= max_cross:
        sol = solve_ivp(rhs, (t, t_end), y0, method="DOP853", rtol=rtol, atol=atol,
                        dense_output=True, events=events)
        segs.append(sol)
        if sol.status == 1:
            hit = [k for k in range(3) if len(sol.t_events[k]) > 0]
            k = hit[0]
            tc = sol.t_events[k][0]
            yc = sol.y_events[k][0].copy()
            cross.append((float(tc), int(k)))
            # step across the crossing: move to the other side by a tiny interval of
            # free flight so the event does not trigger again at the start
            dt = 1e-12*max(1.0, tc)
            yc[0:3] += yc[3:6]*dt
            yc[6] += 0.0
            t, y0 = tc + dt, yc
        else:
            break
    return {"lam": list(map(float, lam)), "model": model, "t0": float(t0),
            "segments": segs, "crossings": cross}


def sample(run, tgrid):
    """R, V, Acc, Jerk, Q-derivatives, P and E on tgrid (inside the integrated span)."""
    model = run["model"]
    segs = run["segments"]
    n = len(tgrid)
    R = np.empty((n, 3))
    V = np.empty((n, 3))
    E = np.empty(n)
    for s in segs:
        lo, hi = s.t[0], s.t[-1]
        m = (tgrid >= lo) & (tgrid <= hi)
        if np.any(m):
            y = s.sol(tgrid[m])
            R[m] = y[0:3].T
            V[m] = y[3:6].T
            E[m] = y[6]
    Acc = np.array([accel(t, R[j], model) for j, t in enumerate(tgrid)])
    Jrk = np.array([jerk(t, R[j], V[j], model) for j, t in enumerate(tgrid)])
    Q = quad_derivs(R, V, Acc, Jrk)
    return {"t": tgrid, "R": R, "V": V, "A": Acc, "J": Jrk, "Q": Q, "P": power(Q[3]),
            "E": E}


def ft_sum(t, x, omega):
    """Trapezoid Fourier sum X(omega) = int x(t) exp(-i omega t) dt of samples on a
    uniform grid t (x: (n,) or (n, k)); the signal is zero outside [t_0, t_n]."""
    dt = t[1] - t[0]
    w = np.full(len(t), dt)
    w[0] = w[-1] = 0.5*dt
    x2 = x if x.ndim == 2 else x[:, None]
    out = np.empty((len(omega), x2.shape[1]), dtype=complex)
    for j in range(0, len(omega), 32):
        om = omega[j:j+32]
        ph = np.exp(-1j*np.outer(om, t))*w[None, :]
        out[j:j+32] = ph @ x2
    return out if x.ndim == 2 else out[:, 0]


def spectrum_from_Q3(t, Q3, omega):
    """dE/dln omega from sampled diagonal Q''' (n, 3)."""
    X = ft_sum(t, Q3, omega)
    return G*omega/(5*np.pi*C**5)*np.sum(np.abs(X)**2, axis=1)
