"""Reference solutions for the stochastic-inflation set-up of the scalar-field module
(athenak/src/scalar_field/scalar_field_slice.cpp, pgen scalar_field with id = stochastic).

Nothing here is a simulation code: ordinary differential equations of the homogeneous
background in e-folds, the Mukhanov-Sasaki equation per wave number from Bunch-Davies
data, the conversion to the units of the code, the mode file the code reads, and the twin
of the perturbed initial slice (the Fourier coefficients the code must produce).

Sources (kb-data/raw/arxiv/<id>/<v>/src/; P1 = 2512.14649 v2 PRD_v2.tex, P2 = 2502.06783
v3 main_V2PRD.tex) and the specification tracks/E-stoch-inf/spec/SPEC.md (branch
track/E-stoch-inf, cited as SPEC):
- test cases: P1:405-420 (table: quadratic with eps1 = 0.01, eps2 = -0.02, H0 = 1e-5 Mpl,
  N* - N0 ~ 5, N_f - N* ~ 8; Higgs inflection with Lambda = 1.86e-6, v = 0.198 Mpl,
  phi0 = -1.2 Mpl, N* - N0 ~ 3, N_f - N* ~ 10);
- potential-position fixing of the background: P2:399-405;
- window, box and cut: P1:503-512 (s = 5, L k_sigma* = 2 pi, k_max = N k_sigma*/4), a* = 1
  and sigma = 1 at P1:519;
- initial slice: SPEC 5.3 (P2 eq. 17 with the corrected delta Pi).

Two sets of units.  "Planck": reduced Planck mass Mpl = 1, as in the papers.  "Code":
G = c = 1 and the time unit 1/H* (H* the Hubble rate at the start N* of the simulation,
a* = 1), SPEC 2.5:
    phi_code = phi/sqrt(8 pi),  V_code(phi_code) = V(phi)/(8 pi H*^2),  t_code = H* t,
    x_code = H* x,  Pi_code = (dphi/dt)/(sqrt(8 pi) H*) = (dphi/dN)(H/H*)/sqrt(8 pi),
    R dimensionless, R_k(code) = R_k H*^(3/2) for the amplitude of the convention
    R(x) = L^(-3/2) sum_n R_k alpha_n exp(i k.x).
Slow-roll parameters with the signs of P1:171: eps1 = -dln H/dN, eps2 = -dln eps1/dN.

[JUDGEMENT] The form of the Bunch-Davies data is not written in the papers (SPEC, U4);
bunch_davies() takes the mode function of constant eps1, v = exp(-i k tau)(1 - i/(k tau))
/sqrt(2k) with tau = -1/((1 - eps1) a H), the choice of tracks/E-stoch-inf/spec/ref/
ms_reference.py, so that both references agree.
"""
import numpy as np

SQ8PI = np.sqrt(8.0*np.pi)


# ----------------------------------------------------------------------------- models
def quadratic_model(eps1=0.01, eps2=-0.02, h0=1.0e-5, dn_star=5.0, dn_sim=8.0):
    """Quadratic potential V = lam phi^2 (m^2 = 2 lam) by potential-position fixing
    (P2:399-405 with p = 2): phi0 and lam from (eps1, eps2, H0) at the Bunch-Davies time
    N0; the field rolls towards positive phi, dphi/dN = +sqrt(2 eps1).  Planck units."""
    p = 2
    phi0 = -abs((3.0 - eps1)*p/(np.sqrt(2.0*eps1)*(eps2/2.0 + eps1 - 3.0)))
    lam = abs(np.sqrt(2.0*eps1)*(eps2/2.0 + eps1 - 3.0)/((3.0 - eps1)*p))**p \
        * h0**2*(3.0 - eps1)
    return dict(name="quadratic", kind="quadratic", lam=lam, m=np.sqrt(2.0*lam),
                v=lambda x: lam*x*x, dv=lambda x: 2.0*lam*x,
                phi0=phi0, dphidn0=np.sqrt(2.0*eps1), dn_star=dn_star, dn_sim=dn_sim)


def inflection_model(lam=1.86e-6, vev=0.198, phi0=-1.2, dn_star=3.0, dn_sim=10.0):
    """Higgs-inflection potential of P1:405-413 with H0 fixing (P2:408): slow-roll
    velocity -V'/V read as dphi/dN (SPEC 5.1).  Planck units."""
    s2 = np.sqrt(2.0)
    c = lam*vev**4/3.0

    def v(x):
        pp = 3.0*x*x + 2.0*s2*x*vev + 6.0*vev*vev
        qq = 3.0*x*x + 2.0*vev*vev
        return c*x*x*pp/qq**2

    def dv(x):
        pp = 3.0*x*x + 2.0*s2*x*vev + 6.0*vev*vev
        qq = 3.0*x*x + 2.0*vev*vev
        return c*((2.0*x*pp + x*x*(6.0*x + 2.0*s2*vev))/qq**2 - 12.0*x**3*pp/qq**3)

    return dict(name="inflection", kind="inflection", lam=lam, vev=vev, v=v, dv=dv,
                phi0=phi0, dphidn0=-dv(phi0)/v(phi0), dn_star=dn_star, dn_sim=dn_sim)


# ------------------------------------------------------------------------- background
class Background:
    """Friedmann and Klein-Gordon equations in e-folds, Planck units (P2:413-423):
    H^2 = V/(3 - phi_N^2/2),  phi_NN = -(3 - eps1) phi_N - V'/H^2,  eps1 = phi_N^2/2.
    N = 0 at the Bunch-Davies time; a = exp(N - dn_star), so a = 1 at N* = dn_star."""

    def __init__(self, model, n_end=None, rtol=1e-13, atol=1e-16):
        from scipy.integrate import solve_ivp
        self.model = model
        self.n_star = model["dn_star"]
        n_end = model["dn_star"] + model["dn_sim"] if n_end is None else n_end
        self.sol = solve_ivp(self._rhs, (0.0, n_end), [model["phi0"], model["dphidn0"]],
                             method="DOP853", rtol=rtol, atol=atol, dense_output=True,
                             max_step=0.01)
        if self.sol.status != 0:
            raise RuntimeError(self.sol.message)
        self.h_star = self.state(self.n_star)["H"]

    def _rhs(self, n, y):
        f, fn = y
        h2 = self.model["v"](f)/(3.0 - 0.5*fn*fn)
        return [fn, -(3.0 - 0.5*fn*fn)*fn - self.model["dv"](f)/h2]

    def state(self, n):
        """phi, dphi/dN, eps1, eps2, H at e-fold n (scalars or arrays)."""
        f, fn = self.sol.sol(n)
        eps1 = 0.5*fn*fn
        h2 = self.model["v"](f)/(3.0 - eps1)
        fnn = -(3.0 - eps1)*fn - self.model["dv"](f)/h2
        return dict(phi=f, dphidn=fn, eps1=eps1, eps2=-2.0*fnn/fn, H=np.sqrt(h2))

    def a_h(self, n):
        return np.exp(n - self.n_star)*self.state(n)["H"]


# ----------------------------------------------------------------------- mode functions
def bunch_davies(bg, k, n_i):
    """R_k and dR_k/dN at e-fold n_i for the comoving wave number k (Planck units, a* =
    1): R = v/z, z = a sqrt(2 eps1), v the Bunch-Davies mode function of the module
    docstring."""
    st = bg.state(n_i)
    a = np.exp(n_i - bg.n_star)
    ah = a*st["H"]
    tau = -1.0/((1.0 - st["eps1"])*ah)
    ph = np.exp(-1j*k*tau)/np.sqrt(2.0*k)
    v = ph*(1.0 - 1j/(k*tau))
    dv = -1j*k*v + ph*1j/(k*tau*tau)
    z = a*np.sqrt(2.0*st["eps1"])
    dz = ah*z*(1.0 - 0.5*st["eps2"])
    return v/z, (dv/z - v*dz/z**2)/ah


def mode_functions(bg, k, n_out, kstart=None, rtol=1e-11, atol=1e-30):
    """R_k and dR_k/dN at the e-folds n_out (increasing) from the Mukhanov-Sasaki
    equation R_NN + (3 - eps1 - eps2) R_N + (k/aH)^2 R = 0 (SPEC 2.3), started from
    Bunch-Davies data at N = 0, or, with kstart, at the later of N = 0 and the e-fold
    where k/(aH) = kstart.  k: array of comoving wave numbers (Planck units).  Returns
    complex arrays (len(n_out), len(k))."""
    from scipy.integrate import solve_ivp
    from scipy.optimize import brentq
    k = np.atleast_1d(np.asarray(k, dtype=float))
    n_out = np.atleast_1d(np.asarray(n_out, dtype=float))
    r = np.empty((n_out.size, k.size), dtype=complex)
    d = np.empty_like(r)
    for i, kk in enumerate(k):
        n_i = 0.0
        if kstart is not None and kk/bg.a_h(0.0) > kstart:
            n_i = brentq(lambda n: kk/bg.a_h(n) - kstart, 0.0, n_out[0])
        r0, d0 = bunch_davies(bg, kk, n_i)

        def rhs(n, y, kk=kk):
            st = bg.state(n)
            kah2 = (kk/(np.exp(n - bg.n_star)*st["H"]))**2
            fr = 3.0 - st["eps1"] - st["eps2"]
            return [y[2], y[3], -fr*y[2] - kah2*y[0], -fr*y[3] - kah2*y[1]]

        t_eval = n_out
        if n_out[0] <= n_i:      # the first output is the start itself
            t_eval = n_out[1:]
        sol = solve_ivp(rhs, (n_i, n_out[-1]), [r0.real, r0.imag, d0.real, d0.imag],
                        method="DOP853", t_eval=t_eval, rtol=rtol, atol=atol)
        if sol.status != 0:
            raise RuntimeError(sol.message)
        if n_out[0] <= n_i:
            r[0, i], d[0, i] = r0, d0
            r[1:, i] = sol.y[0] + 1j*sol.y[1]
            d[1:, i] = sol.y[2] + 1j*sol.y[3]
        else:
            r[:, i] = sol.y[0] + 1j*sol.y[1]
            d[:, i] = sol.y[2] + 1j*sol.y[3]
    return r, d


# ------------------------------------------------------------- the set-up of the code
def shells(nmax2):
    """Distinct |n|^2 of the wave vectors with 0 < |n|^2 <= nmax2 (sums of three
    squares), increasing: the shells of the mode set of the code."""
    nmax = int(np.floor(np.sqrt(nmax2) + 1e-9))
    r = np.arange(0, nmax + 1)
    n2 = (r[:, None, None]**2 + r[None, :, None]**2 + r[None, None, :]**2).ravel()
    return np.unique(n2[(n2 >= 1) & (n2 <= nmax2)])


def code_case(model, nmax2, sigma=1.0, kstart=None):
    """The set-up of one test case in the units of the code: a dict with the options of
    <scalar_field> (potential, mass or lambda and vev), the background at N* (phi0, pi0
    of <problem>), the box length L = 2 pi/sigma (L k_sigma* = 2 pi, P1:510), the shells
    n2 and the mode functions R, dR/dtau at N* in the normalisation of the mode file,
    and the background quantities H* (Planck units), eps1, eps2 at N*."""
    bg = Background(model)
    st = bg.state(bg.n_star)
    hs = st["H"]
    n2 = shells(nmax2)
    length = 2.0*np.pi/sigma
    kcode = 2.0*np.pi*np.sqrt(n2)/length           # = sigma |n|
    r, d = mode_functions(bg, kcode*hs, [bg.n_star], kstart=kstart)
    out = dict(model=model["name"], potential=model["kind"], length=length, sigma=sigma,
               n2=n2, R=r[0]*hs**1.5, dR=d[0]*hs**1.5,
               phi0=st["phi"]/SQ8PI, pi0=st["dphidn"]/SQ8PI,
               h_star_planck=hs, eps1=st["eps1"], eps2=st["eps2"],
               dn_star=model["dn_star"], dn_sim=model["dn_sim"], background=bg)
    if model["kind"] == "quadratic":
        out["mass"] = model["m"]/hs
    else:
        out["lambda"] = 8.0*np.pi*model["lam"]/hs**2
        out["vev"] = model["vev"]/SQ8PI
    return out


def write_mode_file(fname, n2, r, dr, header=""):
    """The mode file of <scalar_field> noise_mode_file: rows |n|^2, Re R, Im R,
    Re dR/dtau, Im dR/dtau for every shell."""
    with open(fname, "w") as fp:
        for line in header.splitlines():
            fp.write("# " + line + "\n")
        fp.write("# n2  Re_R  Im_R  Re_dR/dtau  Im_dR/dtau\n")
        for a, b, c in zip(n2, r, dr):
            fp.write(f"{int(a)} {b.real:.17e} {b.imag:.17e} {c.real:.17e} "
                     f"{c.imag:.17e}\n")


def read_mode_file(fname):
    d = np.atleast_2d(np.loadtxt(fname))
    return d[:, 0].astype(int), d[:, 1] + 1j*d[:, 2], d[:, 3] + 1j*d[:, 4]


def code_background(case):
    """V and V' of the case in code units and its background at N*: (v, dv, phi0, pi0)
    for nrpic.scalar_field.friedmann and ms_reference."""
    from . import scalar_field as sf
    if case["potential"] == "quadratic":
        v, dv = sf.potential("quadratic", mass=case["mass"])
    else:
        v, dv = sf.potential("inflection", lam=case["lambda"], vev=case["vev"])
    return v, dv, case["phi0"], case["pi0"]


def code_d2v(case):
    """V'' of the case in code units (for the linear twin nrpic.sf_lattice)."""
    from . import scalar_field as sf
    if case["potential"] == "quadratic":
        return sf.potential_d2("quadratic", mass=case["mass"])
    return sf.potential_d2("inflection", lam=case["lambda"], vev=case["vev"])


# ------------------------------------------------------------- twin of the initial slice
def window(n2, length, a, hub, eps1, sigma=1.0, sharpness=5.0):
    """W and dW/dtau of the shells (SPEC 3): W = (1 + tanh x)/2, x = s ln(sigma a H/k)."""
    k = 2.0*np.pi*np.sqrt(np.asarray(n2, dtype=float))/length
    x = sharpness*np.log(sigma*a*hub/k)
    return 0.5*(1.0 + np.tanh(x)), 0.5*sharpness*hub*(1.0 - eps1)/np.cosh(x)**2


def slice_transfer(n, n2_shell, r, dr, length, nroot, v, dv, phi0, pi0, a=1.0, sigma=1.0,
                   sharpness=5.0, nghost=4, k2="stencil", windowed=True,
                   delta_pi="corrected", scale=1.0):
    """Transfer functions of the perturbed initial slice (scalar_field_slice.cpp): for
    the wave vectors n (M, 3) of the hemisphere the complex factors T with
    field(x) = sum_n 2 Re[T_n alpha_n exp(i k_n.(x - x0))], as a dict with the keys A,
    B, Psi, phi, Pi, K, chi (chi: the factor of chi/chi_b - 1) and H_printed (the linear
    Hamiltonian residual of the printed delta Pi, -4 eps1 H^2 Psi)."""
    from . import scalar_field as sf
    n = np.asarray(n, dtype=np.int64)
    n2 = (n*n).sum(axis=1)
    hub = np.sqrt((8.0*np.pi/3.0)*(0.5*pi0*pi0 + v(phi0)))
    eps1 = 4.0*np.pi*pi0*pi0/(hub*hub)
    eps2 = 6.0 + 2.0*dv(phi0)/(hub*pi0) - 2.0*eps1
    idx = np.searchsorted(n2_shell, n2)
    if not np.array_equal(np.asarray(n2_shell)[idx], n2):
        raise ValueError("the mode functions do not cover the shells of the wave vectors")
    rr, dd = scale*np.asarray(r)[idx], scale*np.asarray(dr)[idx]
    if windowed:
        w, w1 = window(n2, length, a, hub, eps1, sigma, sharpness)
    else:
        w, w1 = np.ones(n2.size), np.zeros(n2.size)
    norm = length**-1.5
    aa = norm*w*rr
    bb = norm*(w1*rr + w*dd)
    h = length/nroot
    kh = 2.0*np.pi*n/nroot
    if k2 == "stencil":
        ksq = sf.d2_symbol(kh, nghost).sum(axis=1)/h**2
    else:
        ksq = (kh**2).sum(axis=1)/h**2
    psi = -eps1*hub*a*a*bb/ksq
    amp = aa - psi
    dpi = (pi0/hub)*bb - pi0*(eps1 + 0.5*eps2)*amp
    if delta_pi == "printed":
        dpi = dpi + pi0*psi
    return dict(A=aa, B=bb, Psi=psi, phi=(pi0/hub)*amp, Pi=dpi, K=3.0*eps1*hub*amp,
                chi=2.0*psi, H_printed=-4.0*eps1*hub*hub*psi, H=hub, eps1=eps1, eps2=eps2,
                ksq=ksq)
