"""Conformally flat Cartesian coordinates for a slice t = const of the Szekeres model.

The slice metric gamma = (R' - R Ecal'/Ecal)^2/(1-k) dr^2 + R^2/Ecal^2 (dp^2 + dq^2) is
written as Phi^2 times the FLAT metric of a "flat Szekeres" form (k = 0, M = 0) with its
own functions rho(r), Stilde, Ptilde, Qtilde (DESIGN.md section 2; sym/sym_szekeres.py,
checks D and E). Ecal and Ecaltilde are vectors X = (a, b, c, d) on the hyperboloid
b^2 + c^2 - 4ad = -1 (Ecal = a(p^2+q^2) + b p + c q + d); with s = 1/sqrt(1-k) and
eta(U, V) = U_b V_b + U_c V_c - 2(U_a V_d + U_d V_a):

    u     = s (-(R'/R) eta(Xt, X) + eta(Xt, X')),     (ln rho)' = u,
    Xt'   = u Xt - s ((R'/R) X - X'),                  Phi = R Ecaltilde/(rho Ecal).

The flat metric is embedded in R^3 by non-concentric spheres (check E):

    x = rho(r) O(r) ntilde + C(r),   O' = -O [omt]x,   C' = -rho O bt,
    bt = -(Pt', Qt', St')/St,  omt = (-Qt', Pt', 0)/St,

ntilde the stereographic image of (p, q) with centre (Pt, Qt) and scale St. Then
gamma_ij = Phi^2 delta_ij exactly, i.e. psi = Phi^(1/2); the dust shells r = const are
round spheres of radius rho(r) centred at C(r), and K_ij = Phi^2 [KT delta_ij +
(KL - KT) N_i N_j] with N = O ntilde their unit normal.

The ODE is integrated (classical Runge-Kutta on a uniform grid in ln r) inward from r_out (outside the support of the dipole and of
the perturbation: Einstein-de Sitter, where the map is x = R(t, r) n, Phi = 1) and
tabulated for cubic Hermite interpolation. The physical direction n (of Ecal) at a point
follows from ntilde without passing through p, q (regular at every pole):

    D = St^2 (1 + nt_z) + 2 St (nt_x dP + nt_y dQ) + (dP^2 + dQ^2 + S^2)(1 - nt_z),
    n = (2S (St nt_x + dP (1 - nt_z)), 2S (St nt_y + dQ (1 - nt_z)), D - 2 S^2 (1 - nt_z))/D,
    Ecaltilde/Ecal = 2 S St / D,  dP = Pt - P, dQ = Qt - Q.
"""

import math

import numpy as np

__all__ = ["ConformalMap"]

_IDX = dict(lnrho=0, At=slice(1, 5), S=5, P=6, Q=7, O=slice(8, 17), C=slice(17, 20))


def _eta(U, V):
    return U[1] * V[1] + U[2] * V[2] - 2.0 * (U[0] * V[3] + U[3] * V[0])


def _skew(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


class ConformalMap:
    def __init__(self, model, t=None, r_out=None, r_min_frac=1e-7, nodes=20001):
        self.m = model
        self.t = float(t if t is not None else model.t_i)
        sup = max(getattr(model.prof, "R2", 0.0), model.dip.support[1])
        self.r_out = float(r_out if r_out is not None else max(sup, 1e-3) * 1.0001)
        self.r_min = self.r_out * r_min_frac
        self.s_out, self.s_min = math.log(self.r_out), math.log(self.r_min)
        self.s_nodes = np.linspace(self.s_min, self.s_out, nodes)
        h = self.s_nodes[1] - self.s_nodes[0]
        # model quantities at the nodes and half-nodes (one vectorized evaluation), then
        # classical Runge-Kutta from r_out inward on the node grid (error ~ h^4, h = ln(r)
        # spacing; checked by halving in tests/test_szekeres.py)
        sg = np.linspace(self.s_min, self.s_out, 2 * nodes - 1)
        rg = np.exp(sg)
        sh = model.shell(self.t, rg)
        self._RpR, self._k = sh["RpR"], sh["k"]
        self._b = model.dip.b(rg)
        self._rg = rg
        R_out = float(model.shell(self.t, np.array([self.r_out]))["R"][0])
        y = np.zeros(20)
        y[0] = math.log(R_out)                          # rho(r_out) = R: Phi = 1 there
        y[1:5] = (0.5, 0.0, 0.0, 0.5)                   # S = 1, P = Q = 0
        y[5] = 1.0
        y[8:17] = np.eye(3).ravel()
        Y = np.empty((20, nodes))
        dY = np.empty((20, nodes))
        j = 2 * nodes - 2                               # index into the half-node grid
        Y[:, -1] = y
        for n in range(nodes - 1, 0, -1):
            k1 = self._rhs_i(j, y)
            k2 = self._rhs_i(j - 1, y - 0.5 * h * k1)
            k3 = self._rhs_i(j - 1, y - 0.5 * h * k2)
            k4 = self._rhs_i(j - 2, y - h * k3)
            dY[:, n] = k1
            y = y - (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            j -= 2
            Y[:, n - 1] = y
        dY[:, 0] = self._rhs_i(0, y)
        self.Y, self.dY = Y, dY
        self.R_out = R_out
        self.hyper_drift = float(np.max(np.abs(_eta(Y[1:5], Y[1:5]) + 1.0)))

    # ---------------------------------------------------------------- the ODE
    def _rhs_i(self, i, y):
        return self._rhs_vals(y, self._rg[i], self._RpR[i], self._k[i], self._b[i])

    def _rhs_vals(self, y, r, RpR, k, b):
        At = y[1:5]
        S, P, Q = y[5], y[6], y[7]
        O = y[8:17].reshape(3, 3)
        Sp, Pp, Qp = -S * b[2], -S * b[0], -S * b[1]
        X = np.array([1 / (2 * S), -P / S, -Q / S, (P * P + Q * Q) / (2 * S) + S / 2])
        Xp = np.array([-Sp / (2 * S * S), -(Pp * S - P * Sp) / (S * S), -(Qp * S - Q * Sp) / (S * S),
                       (P * Pp + Q * Qp) / S - (P * P + Q * Q) * Sp / (2 * S * S) + Sp / 2])
        sk = 1.0 / math.sqrt(1.0 - k)
        u = sk * (-RpR * _eta(At, X) + _eta(At, Xp))
        Atp = u * At - sk * (RpR * X - Xp)
        a0 = At[0]
        St = 1 / (2 * a0)
        Stp = -Atp[0] / (2 * a0 * a0)
        Ptp = -(Atp[1] * a0 - At[1] * Atp[0]) / (2 * a0 * a0)
        Qtp = -(Atp[2] * a0 - At[2] * Atp[0]) / (2 * a0 * a0)
        bt = -np.array([Ptp, Qtp, Stp]) / St
        omt = np.array([-Qtp, Ptp, 0.0]) / St
        rho = math.exp(y[0])
        dy = np.empty(20)
        dy[0] = u
        dy[1:5] = Atp
        dy[5:8] = (Sp, Pp, Qp)
        dy[8:17] = (-O @ _skew(omt)).ravel()
        dy[17:20] = -rho * (O @ bt)
        return r * dy

    # ---------------------------------------------------------------- tables
    def table(self, s):
        """State (20, n) at ln r = s by cubic Hermite interpolation of the nodes."""
        s = np.asarray(s, dtype=float)
        h = self.s_nodes[1] - self.s_nodes[0]
        j = np.clip(((s - self.s_min) / h).astype(np.int64), 0, len(self.s_nodes) - 2)
        x = (s - self.s_nodes[j]) / h
        h00 = (1 + 2 * x) * (1 - x) ** 2
        h10 = x * (1 - x) ** 2
        h01 = x * x * (3 - 2 * x)
        h11 = x * x * (x - 1)
        Y0, Y1 = self.Y[:, j], self.Y[:, j + 1]
        D0, D1 = self.dY[:, j], self.dY[:, j + 1]
        return h00 * Y0 + h10 * h * D0 + h01 * Y1 + h11 * h * D1

    def radial_table(self, r):
        """rho, centre C, tilde functions at labels r (inside r_out)."""
        Y = self.table(np.log(np.asarray(r, dtype=float)))
        return dict(rho=np.exp(Y[0]), At=Y[1:5], S=Y[5], P=Y[6], Q=Y[7],
                    O=Y[8:17].reshape((3, 3) + Y.shape[1:]), C=Y[17:20])

    # ---------------------------------------------------------------- the inverse map
    def locate(self, x):
        """Label r and unit normal N of the shell through each point x (n, 3)."""
        x = np.asarray(x, dtype=float).reshape(-1, 3)
        d = np.linalg.norm(x, axis=1)
        r = np.empty(len(x))
        N = np.empty_like(x)
        out = d >= self.R_out
        if np.any(out):                         # Einstein-de Sitter: R(t, r) = |x|
            a = (self.t / self.m.t_i) ** (2.0 / 3.0)
            r[out] = d[out] / a
            N[out] = x[out] / d[out, None]
        ins = ~out
        if np.any(ins):
            xi = x[ins]
            lo = np.full(len(xi), self.s_min)
            hi = np.full(len(xi), self.s_out)
            s = np.log(np.maximum(np.linalg.norm(xi, axis=1), 1e-300) / self.R_out) + self.s_out
            s = np.clip(s, lo, hi)
            for it in range(200):
                Y = self.table(s)
                dY = self._dtable(s)
                rho = np.exp(Y[0])
                v = xi - Y[17:20].T
                dist = np.linalg.norm(v, axis=1)
                f = dist - rho
                lo = np.where(f > 0, s, lo)
                hi = np.where(f < 0, s, hi)
                conv = (np.abs(f) <= 1e-14 * np.maximum(rho, 1e-300)) | \
                       (hi - lo <= 4e-16 * np.maximum(np.abs(s), 1.0))
                if np.all(conv):
                    break
                Nn = v / np.where(dist > 0, dist, 1.0)[:, None]
                fp = -np.einsum("ij,ij->i", Nn, dY[17:20].T) - rho * dY[0]
                sn = s - f / np.where(fp < 0, fp, -1.0)
                bad = (sn < lo) | (sn > hi) | ~np.isfinite(sn) | (fp >= 0)
                sn = np.where(bad, 0.5 * (lo + hi), sn)
                sn = np.where(conv, s, sn)          # converged points never move again
                if np.all(sn == s):                 # stagnation at round-off
                    break
                s = sn
            self.last_locate_iterations = it + 1
            Y = self.table(s)
            v = xi - Y[17:20].T
            r[ins] = np.exp(s)
            N[ins] = v / np.linalg.norm(v, axis=1)[:, None]
        return r, N

    def _dtable(self, s):
        """d/ds of the interpolated state (derivative of the Hermite interpolant)."""
        s = np.asarray(s, dtype=float)
        h = self.s_nodes[1] - self.s_nodes[0]
        j = np.clip(((s - self.s_min) / h).astype(np.int64), 0, len(self.s_nodes) - 2)
        x = (s - self.s_nodes[j]) / h
        d00 = 6 * x * x - 6 * x
        d10 = 3 * x * x - 4 * x + 1
        d01 = -6 * x * x + 6 * x
        d11 = 3 * x * x - 2 * x
        Y0, Y1 = self.Y[:, j], self.Y[:, j + 1]
        D0, D1 = self.dY[:, j], self.dY[:, j + 1]
        return (d00 * Y0 + d01 * Y1) / h + d10 * D0 + d11 * D1

    # ---------------------------------------------------------------- fields
    def fields(self, x):
        """3+1 fields of the slice at Cartesian points x (n, 3): psi, rho (energy density),
        mixed K^i_j (KL, KT and the normal N), labels r, and the scalars of model.fields."""
        x = np.asarray(x, dtype=float).reshape(-1, 3)
        r, N = self.locate(x)
        n_out = len(x)
        bn = np.zeros(n_out)
        ratio = np.ones(n_out)                    # Ecaltilde / Ecal
        rho_c = np.empty(n_out)
        ins = r <= self.r_out
        a = (self.t / self.m.t_i) ** (2.0 / 3.0)
        rho_c[~ins] = r[~ins] * a                 # Einstein-de Sitter: rho = R
        if np.any(ins):
            T = self.radial_table(r[ins])
            rho_c[ins] = T["rho"]
            At = T["At"]
            St, Pt, Qt = 1 / (2 * At[0]), -At[1] / (2 * At[0]), -At[2] / (2 * At[0])
            O = T["O"]
            nt = np.einsum("jin,nj->ni", O, N[ins])          # ntilde = O^T N
            S, P, Q = T["S"], T["P"], T["Q"]
            dP, dQ = Pt - P, Qt - Q
            omz = 1.0 - nt[:, 2]
            D = St ** 2 * (1 + nt[:, 2]) + 2 * St * (nt[:, 0] * dP + nt[:, 1] * dQ) \
                + (dP ** 2 + dQ ** 2 + S ** 2) * omz
            n = np.stack([2 * S * (St * nt[:, 0] + dP * omz), 2 * S * (St * nt[:, 1] + dQ * omz),
                          D - 2 * S ** 2 * omz], axis=1) / D[:, None]
            b = self.m.dip.b(r[ins])
            bn[ins] = np.einsum("ij,ij->i", b, n)
            ratio[ins] = 2 * S * St / D
        f = self.m.fields(self.t, r, bn)
        Phi = f["R"] / rho_c * ratio
        psi = np.sqrt(Phi)
        out = dict(r=r, N=N, bn=bn, Phi=Phi, psi=psi, rho_c=rho_c)
        out.update({k: f[k] for k in ("rho", "KL", "KT", "K", "Theta", "Sigma", "W", "R", "den")})
        return out

    def kmix(self, f):
        """Mixed K^i_j as a dict over (i, j) from fields()."""
        d = f["KL"] - f["KT"]
        N = f["N"]
        K = {}
        for i in range(3):
            for j in range(3):
                K[i, j] = d * N[:, i] * N[:, j] + (f["KT"] if i == j else 0.0)
        return K

    def summary(self):
        T = self.radial_table(np.array([self.r_min * 10, self.r_out * 0.5]))
        return dict(t=self.t, r_out=self.r_out, r_min=self.r_min, R_out=self.R_out,
                    hyperboloid_drift=self.hyper_drift, nodes=len(self.s_nodes),
                    centre_offset_at_rmin=float(np.linalg.norm(T["C"][:, 0])))
