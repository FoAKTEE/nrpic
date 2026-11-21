"""Linear twin of the stochastic-inflation runs on the mesh: the equations that AthenaK's
Z4c solver and scalar-field module solve (athenak/src/z4c/z4c_calcrhs.cpp, scalar_field/
scalar_field_rhs.cpp), linearised about the homogeneous background in geodesic slicing
with zero shift, for single wave vectors, with the symbols of the centred differences of
the mesh (utils/finite_diff.hpp) in place of the wave numbers.  Ordinary differential
equations per wave vector, integrated with SciPy: a semi-analytic reference, no
simulation code.

It predicts, per wave vector, what the mesh does at first order in the amplitude of the
stochastic sources: the curvature perturbation R^NR extracted from a dump, and the
first-order parts of the constraints of Z4c::ADMConstraints, which the continuum theory
has zero and the mesh has not (tracks/core/JOURNAL-scalar3.md, entry 1; interface
tracks/core/interfaces/scalar_field_3.md).

Symbols (per direction a, cell size h, phase th_a = 2 pi n_a/N):
    D1  -> i q_a,          q_a   = qh(th_a)/h
    Dxx -> -kap_a,         kap_a = kap2(th_a)/h^2
    Dxy -> -q_a q_b
    K2 = sum kap_a,  q2 = sum q_a^2,  P_ab = kap_a delta_ab + q_a q_b (1 - delta_ab)
Perturbations (code variables, G = 1, K = -3H): chi = a^-2 (1 + c), gt_ab = delta_ab +
h_ab, At_ab = A_ab, Khat = -3H + kap, Theta = th, Gamma^a = G_a, phi = phi_b + f, Pi =
Pi_b + p.  Linear equations (alpha = 1, beta = 0; z = 1 for Z4c, 0 for BSSN):

    df/dt    = p
    dp/dt    = -a^-2 K2 f - 3H p + Pi_b (kap + 2 th) - V'' f + (Pi_b/H) S
    dc/dt    = (2/3)(kap + 2 th)
    dkap/dt  = -2H (kap + 2 th) + 4 pi (4 Pi_b p - 2 V' f) + kappa1 (1 - kappa2) th - eps1 S
    dth/dt   = z {(1/2)[a^-2 (i q.G - 2 K2 c) - 4H (kap + 2 th)] - 8 pi (Pi_b p + V' f)
                  - (2 + kappa2) kappa1 th}
    dh_ab/dt = -2 A_ab
    dA_ab/dt = a^-2 [rho_ab - (1/3) delta_ab tr rho] - 3H A_ab
               + eps1 (delta_ab/3 - qp_a qp_b/qp^2) S
               rho_ab = (i/2)(q_a G_b + q_b G_a) + (1/2) K2 h_ab - (1/2)(P_ab + delta_ab K2) c
    dG_a/dt  = -(2/3) i q_a (2 kap + th) + 16 pi Pi_b i q_a f - 2 kappa1 (G_a - i q_b h_ab)

with S = L^(-3/2) {R W'' + [2 R' + (3 - eps2) H R] W'} the source of the wave vector
(R: mode function of its shell, as in scalar_field_noise.cpp).  Constraints as
Z4c::ADMConstraints forms them (ADM metric; D1 first, Dxx/Dxy second derivatives):

    dH   = a^-2 (-2 K2 c - sum_ab P_ab h_ab) - 4H (kap + 2 th) - 16 pi (Pi_b p + V' f)
    dM_a = i [q_b A_ab - (2/3) q_a (kap + 2 th) + 8 pi Pi_b q_a f]      (covariant)

`scheme` selects which symbols the second derivatives use: "mesh" (kap_a from the second
difference, as the code), "d1d1" (kap_a = q_a^2: every second derivative the first
difference applied twice; the constraints then close), "continuum" (all symbols exact).
"""
import numpy as np

from . import scalar_field as sf

IDX = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 1): 3, (1, 2): 4, (2, 2): 5,
       (1, 0): 1, (2, 0): 2, (2, 1): 4}
NV = 20      # f, p, c, kap, th, h(6), A(6), G(3)


def symbols(n, nroot, length, nghost=4, scheme="mesh"):
    """q_a (M, 3) and kap_a (M, 3) of the wave vectors n (M, 3)."""
    h = length/nroot
    th = 2.0*np.pi*np.asarray(n, dtype=float)/nroot
    if scheme == "continuum":
        q = th/h
        return q, q*q
    q = sf.d1_symbol(th, nghost)/h
    if scheme == "d1d1":
        return q, q*q
    return q, sf.d2_symbol(th, nghost)/h**2


def canonical(n):
    """Wave vectors with sorted absolute components (|n_x| >= |n_y| >= |n_z| >= 0): the
    scalar outputs of the twin are the same for all wave vectors related by
    permutations and reflections.  Returns (unique canonical vectors, index of each n)."""
    c = np.sort(np.abs(np.asarray(n, dtype=np.int64)), axis=1)[:, ::-1]
    u, inv = np.unique(c, axis=0, return_inverse=True)
    return u, inv.ravel()


class Twin:
    """The linear system for a set of wave vectors n (M, 3) of a box of side `length`
    with nroot cells per side.

    v, dv, d2v: potential and its first two derivatives (code units); phi0, pi0: the
    background at t = 0 (a = 1); n2_shell, r0, dr0: shells and mode functions of the mode
    file.  mode_k2: "continuum" (the code) or "lattice" (K2 of the wave vector in the
    mode equation).  z4c: Theta evolved (use_z4c = true, the default of the inputs)."""

    def __init__(self, n, nroot, length, v, dv, d2v, phi0, pi0, n2_shell, r0, dr0,
                 nghost=4, scheme="mesh", mode_k2="continuum", sigma=1.0, sharpness=5.0,
                 z4c=True, kappa1=0.0, kappa2=0.0, projector="stencil",
                 slice_k2="stencil", windowed=True, kicks=True):
        self.n = np.asarray(n, dtype=np.int64)
        self.m = self.n.shape[0]
        self.nroot, self.length = nroot, length
        self.v, self.dv, self.d2v = v, dv, d2v
        self.phi0, self.pi0 = phi0, pi0
        self.sigma, self.s = sigma, sharpness
        self.z = 1.0 if z4c else 0.0
        self.k1, self.k2 = kappa1, kappa2
        self.kicks = kicks
        self.windowed = windowed
        n2 = (self.n*self.n).sum(axis=1)
        idx = np.searchsorted(n2_shell, n2)
        if not np.array_equal(np.asarray(n2_shell)[idx], n2):
            raise ValueError("the mode file does not cover the wave vectors")
        self.r0 = np.asarray(r0, dtype=complex)[idx]
        self.dr0 = np.asarray(dr0, dtype=complex)[idx]
        self.kc = 2.0*np.pi*np.sqrt(n2.astype(float))/length      # continuum |k|
        self.q, self.kap = symbols(self.n, nroot, length, nghost, scheme)
        self.q2 = (self.q**2).sum(axis=1)
        self.K2 = self.kap.sum(axis=1)
        # symbols of the diagnostics (always those of the scheme)
        # P_ab as a (M, 6) array in the order xx, xy, xz, yy, yz, zz
        q, kap = self.q, self.kap
        self.P = np.stack([kap[:, 0], q[:, 0]*q[:, 1], q[:, 0]*q[:, 2], kap[:, 1],
                           q[:, 1]*q[:, 2], kap[:, 2]], axis=1)
        # projector of the kick of At
        if projector == "stencil":
            qp, _ = symbols(self.n, nroot, length, nghost, "mesh")
        else:
            qp = 2.0*np.pi*self.n/length
        qp2 = (qp**2).sum(axis=1)
        self.proj = np.stack([qp[:, 0]*qp[:, 0], qp[:, 0]*qp[:, 1], qp[:, 0]*qp[:, 2],
                              qp[:, 1]*qp[:, 1], qp[:, 1]*qp[:, 2], qp[:, 2]*qp[:, 2]],
                             axis=1)/qp2[:, None]
        self.delta = np.array([1.0, 0.0, 0.0, 1.0, 0.0, 1.0])
        # k^2 of the mode equation and of the Bardeen potential of the slice
        self.kmode2 = self.kc**2 if mode_k2 == "continuum" else self.K2.copy()
        if slice_k2 == "stencil":
            _, kap_s = symbols(self.n, nroot, length, nghost, "mesh")
            self.kslice2 = kap_s.sum(axis=1)
        else:
            self.kslice2 = self.kc**2
        self.norm = length**-1.5

    # ---------------------------------------------------------------- background
    def bg(self, phi, pi):
        h = np.sqrt((8.0*np.pi/3.0)*(0.5*pi*pi + self.v(phi)))
        e1 = 4.0*np.pi*pi*pi/(h*h)
        e2 = 6.0 + 2.0*self.dv(phi)/(h*pi) - 2.0*e1
        return h, e1, e2

    def window(self, lna, h, e1, e2):
        """W, W', W'' of every wave vector (proper-time derivatives)."""
        if not self.windowed:
            one = np.ones(self.m)
            return one, 0.0*one, 0.0*one
        x = self.s*np.log(self.sigma*np.exp(lna)*h/self.kc)
        sech2 = 1.0/np.cosh(x)**2
        dl = h*(1.0 - e1)
        d2l = h*h*e1*(e2 - 1.0 + e1)
        w = 0.5*(1.0 + np.tanh(x))
        w1 = 0.5*self.s*sech2*dl
        w2 = 0.5*sech2*(self.s*d2l - 2.0*self.s**2*np.tanh(x)*dl*dl)
        return w, w1, w2

    # ---------------------------------------------------------------- initial data
    def initial(self):
        m = self.m
        h, e1, e2 = self.bg(self.phi0, self.pi0)
        w, w1, _ = self.window(0.0, h, e1, e2)
        aa = self.norm*w*self.r0
        bb = self.norm*(w1*self.r0 + w*self.dr0)
        psi = -e1*h*bb/self.kslice2
        amp = aa - psi
        y = np.zeros((m, NV), dtype=complex)
        y[:, 0] = (self.pi0/h)*amp
        y[:, 1] = (self.pi0/h)*bb - self.pi0*(e1 + 0.5*e2)*amp
        y[:, 2] = 2.0*psi
        y[:, 3] = 3.0*e1*h*amp
        return y

    # ---------------------------------------------------------------- right-hand side
    def _unpack(self, yy):
        m = self.m
        phi, pi, lna = yy[:3]
        z = yy[3:].view(complex).reshape(m, 2 + NV)
        return phi, pi, lna, z[:, 0], z[:, 1], z[:, 2:]

    def rhs(self, t, yy):
        m = self.m
        phi, pi, lna, r, dr, y = self._unpack(yy)
        h, e1, e2 = self.bg(phi, pi)
        vp, vpp = self.dv(phi), self.d2v(phi)
        ia2 = np.exp(-2.0*lna)
        out = np.empty_like(yy)
        out[:3] = (pi, -3.0*h*pi - vp, h)
        zo = out[3:].view(complex).reshape(m, 2 + NV)
        fric = (3.0 - e2)*h
        zo[:, 0] = dr
        zo[:, 1] = -fric*dr - self.kmode2*ia2*r
        w, w1, w2 = self.window(lna, h, e1, e2)
        src = self.norm*(r*w2 + (2.0*dr + fric*r)*w1) if self.kicks else 0.0*r
        f, p, c, kap, th = y[:, 0], y[:, 1], y[:, 2], y[:, 3], y[:, 4]
        hh, aa, gg = y[:, 5:11], y[:, 11:17], y[:, 17:20]
        q, K2 = self.q, self.K2
        kk = kap + 2.0*th
        d = zo[:, 2:]
        d[:, 0] = p
        d[:, 1] = -ia2*K2*f - 3.0*h*p + pi*kk - vpp*f + (pi/h)*src
        d[:, 2] = (2.0/3.0)*kk
        d[:, 3] = -2.0*h*kk + 4.0*np.pi*(4.0*pi*p - 2.0*vp*f) \
            + self.k1*(1.0 - self.k2)*th - e1*src
        qg = 1j*(q*gg).sum(axis=1)
        d[:, 4] = self.z*(0.5*(ia2*(qg - 2.0*K2*c) - 4.0*h*kk)
                          - 8.0*np.pi*(pi*p + vp*f) - (2.0 + self.k2)*self.k1*th)
        d[:, 5:11] = -2.0*aa
        # rho_ab and its trace-free part
        rho = np.empty((m, 6), dtype=complex)
        for (a, b), ix in ((k, v) for k, v in IDX.items() if k[0] <= k[1]):
            rho[:, ix] = 0.5j*(q[:, a]*gg[:, b] + q[:, b]*gg[:, a]) + 0.5*K2*hh[:, ix] \
                - 0.5*self.P[:, ix]*c
        rho -= 0.5*K2[:, None]*c[:, None]*self.delta[None, :]
        tr = rho[:, 0] + rho[:, 3] + rho[:, 5]
        d[:, 11:17] = ia2*(rho - tr[:, None]*self.delta[None, :]/3.0) - 3.0*h*aa \
            + e1*(self.delta[None, :]/3.0 - self.proj)*src[:, None]
        qh = np.empty((m, 3), dtype=complex)        # q_b h_ab
        for a in range(3):
            qh[:, a] = sum(q[:, b]*hh[:, IDX[(a, b)]] for b in range(3))
        d[:, 17:20] = -(2.0/3.0)*1j*q*(2.0*kap + th)[:, None] \
            + 16.0*np.pi*pi*1j*q*f[:, None] - 2.0*self.k1*(gg - 1j*qh)
        return out

    def integrate(self, t_eval, rtol=1e-11, atol=1e-28):
        """Integrates from t = 0 and returns the state at the times t_eval: dict with
        phi, Pi, ln_a, H, eps1, eps2 (per time), R, dR (time, mode) and y (time, mode,
        20)."""
        from scipy.integrate import solve_ivp
        m = self.m
        z0 = np.concatenate([self.r0[:, None], self.dr0[:, None], self.initial()],
                            axis=1)
        y0 = np.concatenate([[self.phi0, self.pi0, 0.0], z0.ravel().view(float)])
        t_eval = np.atleast_1d(np.asarray(t_eval, dtype=float))
        sol = solve_ivp(self.rhs, (0.0, max(t_eval[-1], 1e-300)), y0, method="DOP853",
                        t_eval=t_eval, rtol=rtol, atol=atol)
        if sol.status != 0:
            raise RuntimeError(sol.message)
        phi, pi, lna = sol.y[:3]
        h, e1, e2 = self.bg(phi, pi)
        zz = np.ascontiguousarray(sol.y[3:].T).view(complex).reshape(
            t_eval.size, m, 2 + NV)
        return dict(time=sol.t, phi=phi, Pi=pi, ln_a=lna, H=h, eps1=e1, eps2=e2,
                    R=zz[:, :, 0], dR=zz[:, :, 1], y=zz[:, :, 2:])

    # ---------------------------------------------------------------- diagnostics
    def diagnostics(self, sol):
        """Per time and wave vector: the first-order constraints dH, dM (3 covariant
        components) as Z4c::ADMConstraints forms them, the connection constraint Z_a,
        R^NR as the analysis of the dumps extracts it (psi with the continuum projector
        n_a n_b/n^2), the coarse-grained reference L^(-3/2) W R, and the window."""
        y = sol["y"]
        nt = y.shape[0]
        q, K2, P = self.q, self.K2, self.P
        out = dict(dH=np.empty((nt, self.m), dtype=complex),
                   dM=np.empty((nt, self.m, 3), dtype=complex),
                   Z=np.empty((nt, self.m, 3), dtype=complex),
                   rnr=np.empty((nt, self.m), dtype=complex),
                   ref=np.empty((nt, self.m), dtype=complex),
                   w=np.empty((nt, self.m)))
        nn = self.n.astype(float)
        n2 = (nn*nn).sum(axis=1)
        mult = np.array([1.0, 2.0, 2.0, 1.0, 2.0, 1.0])
        pn = np.stack([nn[:, 0]*nn[:, 0], nn[:, 0]*nn[:, 1], nn[:, 0]*nn[:, 2],
                       nn[:, 1]*nn[:, 1], nn[:, 1]*nn[:, 2], nn[:, 2]*nn[:, 2]],
                      axis=1)/n2[:, None]
        for it in range(nt):
            h, e1, e2 = sol["H"][it], sol["eps1"][it], sol["eps2"][it]
            pi, phi, lna = sol["Pi"][it], sol["phi"][it], sol["ln_a"][it]
            vp = self.dv(phi)
            ia2 = np.exp(-2.0*lna)
            f, p, c, kap, th = (y[it, :, i] for i in range(5))
            hh, aa, gg = y[it, :, 5:11], y[it, :, 11:17], y[it, :, 17:20]
            kk = kap + 2.0*th
            ph = (P*mult[None, :]*hh).sum(axis=1)
            out["dH"][it] = ia2*(-2.0*K2*c - ph) - 4.0*h*kk - 16.0*np.pi*(pi*p + vp*f)
            for a in range(3):
                qa = sum(q[:, b]*aa[:, IDX[(a, b)]] for b in range(3))
                qh = sum(q[:, b]*hh[:, IDX[(a, b)]] for b in range(3))
                out["dM"][it, :, a] = 1j*(qa - (2.0/3.0)*q[:, a]*kk
                                          + 8.0*np.pi*pi*q[:, a]*f)
                out["Z"][it, :, a] = gg[:, a] - 1j*qh
            psi = 0.5*c + 0.25*(pn*mult[None, :]*hh).sum(axis=1)
            out["rnr"][it] = psi + (h/pi)*f
            w, _, _ = self.window(lna, h, e1, e2)
            out["w"][it] = w
            out["ref"][it] = self.norm*w*sol["R"][it]
        return out


# ----------------------------------------------------------------------------------------
# The same system with the time integration of the code

#: low-storage RK4()4[2S] of Ketcheson (2010), the coefficients of athenak/src/driver/
#: driver.cpp (integrator = rk4)
RK4_2S = dict(
    gam0=(0.0, 0.121098479554482, -3.843833699660025, 0.546370891121863),
    gam1=(1.0, 0.721781678111411, 2.121209265338722, 0.198653035682705),
    beta=(1.193743905974738, 0.099279895495783, 1.131678018054042, 0.310665766509336),
    delta=(1.0, 0.217683334308543, 1.065841341361089, 0.0))


class CodeTwin(Twin):
    """The linear twin with the time integration of the code: the stages of the driver's
    rk4 at the steps of the run, and the background the mesh itself carries.

    Three sets of variables advance together, as in the code:
      lockstep data of the sources (scalar_field_noise.cpp, level 0): phi_b, Pi_b, ln a
        from the Friedmann equations, the mode functions R, dR/dtau;
      the homogeneous part of the mesh fields: phi_0, Pi_0, chi_0, Khat_0, Theta_0 with
        the equations of the code (K_0 = Khat_0 + 2 Theta_0 is not tied to the energy
        density: the Hamiltonian residual H0 = (2/3) K_0^2 - 16 pi E_0 of the time
        integration is part of the solution);
      the first-order perturbations of the wave vectors about that homogeneous part
        (the equations of the module docstring with -3H -> K_0, a^-2 -> chi_0, Pi_b ->
        Pi_0, and the perturbation of chi itself as the variable, as in the code),
        kicked with the coefficients Pi_b/H, eps1 and the source S of the lockstep
        data.  In the returned y the third entry is delta chi (Twin: c).
    integrate_steps(times) takes the times of the steps of the run (the time column of
    <basename>.sf.hst) and returns the state at chosen cycles."""

    def _rhs_code(self, yy):
        m = self.m
        phib, pib, lnab, phi0, pi0, chi0, kh0, th0 = yy[:8]
        z = yy[8:].view(complex).reshape(m, 2 + NV)
        r, dr, y = z[:, 0], z[:, 1], z[:, 2:]
        out = np.empty_like(yy)
        # lockstep background
        hb, e1, e2 = self.bg(phib, pib)
        out[0], out[1], out[2] = pib, -3.0*hb*pib - self.dv(phib), hb
        # homogeneous part of the mesh
        k0 = kh0 + 2.0*th0
        v0, vp, vpp = self.v(phi0), self.dv(phi0), self.d2v(phi0)
        e0 = 0.5*pi0*pi0 + v0
        out[3] = pi0
        out[4] = k0*pi0 - vp
        out[5] = (2.0/3.0)*chi0*k0
        out[6] = k0*k0/3.0 + 4.0*np.pi*(2.0*pi0*pi0 - 2.0*v0) \
            + self.k1*(1.0 - self.k2)*th0
        out[7] = self.z*(k0*k0/3.0 - 8.0*np.pi*e0 - (2.0 + self.k2)*self.k1*th0)
        # mode functions and sources (lockstep)
        zo = out[8:].view(complex).reshape(m, 2 + NV)
        fric = (3.0 - e2)*hb
        zo[:, 0] = dr
        zo[:, 1] = -fric*dr - self.kmode2*np.exp(-2.0*lnab)*r
        w, w1, w2 = self.window(lnab, hb, e1, e2)
        src = self.norm*(r*w2 + (2.0*dr + fric*r)*w1) if self.kicks else 0.0*r
        # perturbations about the homogeneous part of the mesh
        # the code evolves chi itself: the third variable is x = delta chi here (not c
        # = x/chi_0), so that the stages of the integrator act on the same variables
        # as in the code (the two differ at the order of the time error)
        f, p, x, kap, th = y[:, 0], y[:, 1], y[:, 2], y[:, 3], y[:, 4]
        c = x/chi0
        hh, aa, gg = y[:, 5:11], y[:, 11:17], y[:, 17:20]
        q, K2 = self.q, self.K2
        kk = kap + 2.0*th
        d = zo[:, 2:]
        d[:, 0] = p
        d[:, 1] = -chi0*K2*f + k0*p + pi0*kk - vpp*f + (pib/hb)*src
        d[:, 2] = (2.0/3.0)*(chi0*kk + x*k0)
        d[:, 3] = (2.0/3.0)*k0*kk + 4.0*np.pi*(4.0*pi0*p - 2.0*vp*f) \
            + self.k1*(1.0 - self.k2)*th - e1*src
        qg = 1j*(q*gg).sum(axis=1)
        d[:, 4] = self.z*(0.5*(chi0*(qg - 2.0*K2*c) + (4.0/3.0)*k0*kk)
                          - 8.0*np.pi*(pi0*p + vp*f) - (2.0 + self.k2)*self.k1*th)
        d[:, 5:11] = -2.0*aa
        rho = np.empty((m, 6), dtype=complex)
        for (a, b), ix in ((k, v) for k, v in IDX.items() if k[0] <= k[1]):
            rho[:, ix] = 0.5j*(q[:, a]*gg[:, b] + q[:, b]*gg[:, a]) + 0.5*K2*hh[:, ix] \
                - 0.5*self.P[:, ix]*c
        rho -= 0.5*K2[:, None]*c[:, None]*self.delta[None, :]
        tr = rho[:, 0] + rho[:, 3] + rho[:, 5]
        d[:, 11:17] = chi0*(rho - tr[:, None]*self.delta[None, :]/3.0) + k0*aa \
            + e1*(self.delta[None, :]/3.0 - self.proj)*src[:, None]
        qh = np.empty((m, 3), dtype=complex)
        for a in range(3):
            qh[:, a] = sum(q[:, b]*hh[:, IDX[(a, b)]] for b in range(3))
        d[:, 17:20] = -(2.0/3.0)*1j*q*(2.0*kap + th)[:, None] \
            + 16.0*np.pi*pi0*1j*q*f[:, None] - 2.0*self.k1*(gg - 1j*qh)
        return out

    def integrate_steps(self, times, record):
        """times: t_0 = 0, t_1, ... the times of the steps of the run; record: cycle
        numbers at which the state is kept.  Returns the dict of integrate() with the
        homogeneous part of the mesh added (phi0, Pi0, chi0, Khat0, Theta0, K0, H0 =
        its Hamiltonian residual) and cycle."""
        m = self.m
        z0 = np.concatenate([self.r0[:, None], self.dr0[:, None], self.initial()],
                            axis=1)
        e0 = 0.5*self.pi0**2 + self.v(self.phi0)
        u0 = np.concatenate([[self.phi0, self.pi0, 0.0, self.phi0, self.pi0, 1.0,
                              -np.sqrt(24.0*np.pi*e0), 0.0], z0.ravel().view(float)])
        times = np.asarray(times, dtype=float)
        record = sorted(int(c) for c in record)
        keep = {}
        if record and record[0] == 0:
            keep[0] = u0.copy()
        g0, g1, be, de = (RK4_2S[k] for k in ("gam0", "gam1", "beta", "delta"))
        for n in range(1, min(times.size, record[-1] + 1)):
            dt = times[n] - times[n-1]
            u1 = u0.copy()
            for s in range(4):
                if s > 0:
                    u1 += de[s]*u0
                u0 = g0[s]*u0 + g1[s]*u1 + be[s]*dt*self._rhs_code(u0)
            if n in record:
                keep[n] = u0.copy()
        cyc = [c for c in record if c in keep]
        yy = np.array([keep[c] for c in cyc])
        phib, pib, lnab = yy[:, 0], yy[:, 1], yy[:, 2]
        h, e1, e2 = self.bg(phib, pib)
        zz = np.ascontiguousarray(yy[:, 8:]).view(complex).reshape(len(cyc), m, 2 + NV)
        k0 = yy[:, 6] + 2.0*yy[:, 7]
        return dict(cycle=np.array(cyc), time=times[cyc], phi=phib, Pi=pib, ln_a=lnab,
                    H=h, eps1=e1, eps2=e2, R=zz[:, :, 0], dR=zz[:, :, 1],
                    y=zz[:, :, 2:], phi0=yy[:, 3], Pi0=yy[:, 4], chi0=yy[:, 5],
                    Khat0=yy[:, 6], Theta0=yy[:, 7], K0=k0,
                    H0=(2.0/3.0)*k0*k0 - 16.0*np.pi*(0.5*yy[:, 4]**2 + self.v(yy[:, 3])))

    def diagnostics(self, sol):
        """As Twin.diagnostics, with the homogeneous part of the mesh as the background
        of the constraints and of the extraction (H = -K_0/3 and Pi_0 are what the box
        means of a dump give)."""
        if "K0" not in sol:
            return super().diagnostics(sol)
        y = sol["y"]
        nt = y.shape[0]
        q, K2, P = self.q, self.K2, self.P
        out = dict(dH=np.empty((nt, self.m), dtype=complex),
                   dM=np.empty((nt, self.m, 3), dtype=complex),
                   Z=np.empty((nt, self.m, 3), dtype=complex),
                   rnr=np.empty((nt, self.m), dtype=complex),
                   ref=np.empty((nt, self.m), dtype=complex),
                   w=np.empty((nt, self.m)))
        nn = self.n.astype(float)
        n2 = (nn*nn).sum(axis=1)
        mult = np.array([1.0, 2.0, 2.0, 1.0, 2.0, 1.0])
        pn = np.stack([nn[:, 0]*nn[:, 0], nn[:, 0]*nn[:, 1], nn[:, 0]*nn[:, 2],
                       nn[:, 1]*nn[:, 1], nn[:, 1]*nn[:, 2], nn[:, 2]*nn[:, 2]],
                      axis=1)/n2[:, None]
        for it in range(nt):
            k0, chi0, pi0, phi0 = (sol[x][it] for x in ("K0", "chi0", "Pi0", "phi0"))
            vp = self.dv(phi0)
            f, p, x, kap, th = (y[it, :, i] for i in range(5))
            c = x/chi0
            hh, aa, gg = y[it, :, 5:11], y[it, :, 11:17], y[it, :, 17:20]
            kk = kap + 2.0*th
            ph = (P*mult[None, :]*hh).sum(axis=1)
            out["dH"][it] = chi0*(-2.0*K2*c - ph) + (4.0/3.0)*k0*kk \
                - 16.0*np.pi*(pi0*p + vp*f)
            for a in range(3):
                qa = sum(q[:, b]*aa[:, IDX[(a, b)]] for b in range(3))
                qh = sum(q[:, b]*hh[:, IDX[(a, b)]] for b in range(3))
                out["dM"][it, :, a] = 1j*(qa - (2.0/3.0)*q[:, a]*kk
                                          + 8.0*np.pi*pi0*q[:, a]*f)
                out["Z"][it, :, a] = gg[:, a] - 1j*qh
            psi = 0.5*c + 0.25*(pn*mult[None, :]*hh).sum(axis=1)
            out["rnr"][it] = psi + (-k0/3.0/pi0)*f
            w, _, _ = self.window(sol["ln_a"][it], sol["H"][it], sol["eps1"][it],
                                  sol["eps2"][it])
            out["w"][it] = w
            out["ref"][it] = self.norm*w*sol["R"][it]
        return out
