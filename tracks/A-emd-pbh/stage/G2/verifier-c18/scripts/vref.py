"""Exact reference of the verifier of item C18 (Track A, G2): the Lemaitre-Tolman-Bondi
(LTB) dust solution read off a format-2 table (coord/INTERFACES/spherical_id_format2.md).

Written by the verifier from the format document and the dust equations only; it imports
nothing of the packages it checks (conv_ball, threshold_ball, runs_ball, expball,
python/nrpic).

On the initial slice of a table with alpha = 1 and dust at rest in the slice (u_i = 0),
the slice is a slice of constant proper time of the dust, so every shell (label rbar)
starts at proper time 0 with
    psi = 1 + u,  R = psi^2 rbar  (areal radius),
    dR/dtau = -KT R  (K^theta_theta = KT, expansion has K < 0),
    dR/dl = (dR/drbar) / psi^2  (proper radial length l),
    Misner-Sharp mass m = (R/2) (1 + (dR/dtau)^2 - (dR/dl)^2),
    specific energy E = (dR/dtau)^2 / 2 - m / R.
Pressureless spherical dust conserves m and E on every shell until shells cross, and a
bound shell (E < 0) follows the cycloid
    R = A (1 - cos eta),  tau = B (eta - sin eta) - B (eta0 - sin eta0),
    A = m / (-2E),  B = m / (-2E)^(3/2).
It turns around at eta = pi and is trapped (R = 2m) at cos eta_AH = 1 + 4E on the
collapsing branch (eta_AH in (pi, 2 pi)).
"""
import numpy as np


def read_table2(path):
    """Format-2 table: header dict and the six columns (rbar u KL KT alpha betar)."""
    head = {}
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                if "=" in s:
                    k, v = s[1:].split("=", 1)
                    head[k.strip()] = v.strip()
                continue
            rows.append([float(x) for x in s.split()])
    a = np.array(rows)
    if a.shape[1] != 6:
        raise ValueError("format-2 table needs six columns, got %d" % a.shape[1])
    if head.get("format", "2") != "2":
        raise ValueError("not a format-2 table")
    breaks = [float(x) for x in head.get("breaks", "").split()] if "breaks" in head else []
    return head, a, breaks


class LTB:
    """Shell quantities of the table on its own rows (piecewise derivative inside the
    pieces between breaks) and the exact cycloid events per shell."""

    def __init__(self, path):
        self.path = path
        self.head, a, self.breaks = read_table2(path)
        self.rbar, u, self.KL, self.KT, self.alpha, self.betar = a.T
        psi = 1.0 + u
        self.psi = psi
        self.R = psi ** 2 * self.rbar
        dR = np.empty_like(self.R)
        edges = [-np.inf] + list(self.breaks) + [np.inf]
        for lo, hi in zip(edges[:-1], edges[1:]):
            sel = np.where((self.rbar > lo) & (self.rbar < hi))[0]
            if sel.size < 3:
                raise ValueError("piece with fewer than three rows")
            dR[sel] = np.gradient(self.R[sel], self.rbar[sel], edge_order=2)
        self.dRdl = dR / psi ** 2
        self.Rdot = -self.KT * self.R
        self.m = 0.5 * self.R * (1.0 + self.Rdot ** 2 - self.dRdl ** 2)
        with np.errstate(divide="ignore", invalid="ignore"):
            self.E = 0.5 * self.Rdot ** 2 - self.m / self.R
        self.E[0] = np.nan if self.R[0] == 0 else self.E[0]
        self._events()

    def _events(self):
        m, E, R, Rd = self.m, self.E, self.R, self.Rdot
        n = m.size
        self.tau_ta = np.full(n, np.nan)
        self.tau_ah = np.full(n, np.nan)
        self.eta0 = np.full(n, np.nan)
        self.Acyc = np.full(n, np.nan)
        self.Bcyc = np.full(n, np.nan)
        ok = (E < 0) & (m > 0) & (R > 0)
        A = m[ok] / (-2.0 * E[ok])
        B = m[ok] / (-2.0 * E[ok]) ** 1.5
        c0 = np.clip(1.0 - R[ok] / A, -1.0, 1.0)
        eta0 = np.arccos(c0)                       # in [0, pi]: expanding branch
        eta0 = np.where(Rd[ok] < 0, 2 * np.pi - eta0, eta0)
        phase0 = B * (eta0 - np.sin(eta0))
        cah = np.clip(1.0 + 4.0 * E[ok], -1.0, 1.0)
        eta_ah = 2 * np.pi - np.arccos(cah)
        self.eta0[ok], self.Acyc[ok], self.Bcyc[ok] = eta0, A, B
        self.tau_ta[ok] = np.where(eta0 < np.pi, B * np.pi - phase0, np.nan)
        # trapped already on the slice if R <= 2m there (eta0 >= eta_ah)
        self.tau_ah[ok] = np.where(eta_ah >= eta0, B * (eta_ah - np.sin(eta_ah)) - phase0, 0.0)

    # ---- interpolation of shell quantities to a label ----
    def piece_interp(self, rb, q):
        """Linear interpolation of a row quantity q at rbar = rb inside the piece of rb."""
        rb = np.atleast_1d(np.asarray(rb, float))
        out = np.full(rb.shape, np.nan)
        edges = [-np.inf] + list(self.breaks) + [np.inf]
        for lo, hi in zip(edges[:-1], edges[1:]):
            sel = (self.rbar > lo) & (self.rbar < hi)
            if lo == -np.inf:
                sel |= self.rbar == 0
            w = (rb >= lo) & (rb < hi)
            if np.any(w):
                out[w] = np.interp(rb[w], self.rbar[sel], q[sel])
        return out

    def shell(self, rb):
        """dict of R_i, m, E, tau_ta, tau_ah at the labels rb (initial coordinate radii)."""
        return {k: self.piece_interp(rb, getattr(self, k)) for k in
                ("R", "m", "E", "tau_ta", "tau_ah", "eta0", "Acyc", "Bcyc")}

    def areal_radius(self, rb, tau):
        """Exact areal radius of the shells rb at their proper times tau (cycloid)."""
        s = self.shell(rb)
        tau = np.broadcast_to(np.asarray(tau, float), s["R"].shape)
        A, B, e0 = s["Acyc"], s["Bcyc"], s["eta0"]
        target = tau / B + (e0 - np.sin(e0))          # eta - sin eta
        lo = np.zeros_like(target)
        hi = np.full_like(target, 2 * np.pi)
        for _ in range(80):                               # bisection, monotone in eta
            mid = 0.5 * (lo + hi)
            f = mid - np.sin(mid) - target
            hi = np.where(f > 0, mid, hi)
            lo = np.where(f > 0, lo, mid)
        eta = 0.5 * (lo + hi)
        return A * (1 - np.cos(eta))

    def core_edge(self):
        """Last row inside the first break (the edge of the top-hat core)."""
        if not self.breaks:
            raise ValueError("no break in this table")
        i = np.where(self.rbar < self.breaks[0])[0][-1]
        return i
