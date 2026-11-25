"""Measures of the verifier of item C18 (Track A, G2), from the raw outputs of a member
(horizon summary, tracked particles, tab lines) and the exact LTB reference (vref.py).

Definitions (taken from conv_ball/DESIGN.md section 4 and threshold_ball/JOURNAL.md
entry 1 as written; the implementation is the verifier's own):
- ddet: at the finder's first detection, the proper time of the tracked particles at the
  finder's mean coordinate radius minus the exact tau_AH of the shell there. Particles
  are grouped in bands of equal initial coordinate radius; two interpolations in the
  band radii are computed (v1: of tau - tau_AH; v2: of tau and of the label, tau_AH
  then exact at the interpolated label); their difference is the interpolation spread.
- dtrap: per particle of the band nearest R_i = 2.603 M, the proper time at which the
  areal radius r sqrt(gamma_T) at the particle falls through 2 m of its shell, minus the
  exact tau_AH of the shell; mean over the band.
- dm: finder sqrt(A/16 pi) / m_exact - 1, m_exact the mass of the outermost exactly
  trapped shell on the code's slice (bands with tau >= tau_AH; the zero of
  tau_slice(label) - tau_AH(label) between the last trapped band and the next band
  outward, tau_slice linear in the label between bands, tau_AH exact on the table rows).
  Lower and upper bounds: the mass of the last trapped band and of the next band.
- BH rule (threshold_ball entry 1): found in at least three consecutive searches
  spanning at least 5 M_AH, and every later search finds it.
"""
import numpy as np
from vread import read_summary, Tracks, read_tab
from vref import LTB


class Member:
    def __init__(self, rundir, table, summary="ball.horizon_summary_0.txt", base="ball"):
        self.rundir = rundir
        self.ltb = LTB(table)
        self.summ = read_summary("%s/%s" % (rundir, summary))
        self.tr = Tracks("%s/%s.traj.bin" % (rundir, base), "%s/%s.trajmet.bin" % (rundir, base))
        if self.tr.t[0] != 0.0:
            raise ValueError("first trajectory record is not at t = 0")
        rb0 = self.tr.r[0]
        self.rb0 = rb0
        sh = self.ltb.shell(rb0)
        self.Ri, self.mi, self.tah = sh["R"], sh["m"], sh["tau_ah"]
        key = np.round(rb0, 5)
        self.bkeys, self.band = np.unique(key, return_inverse=True)
        self.nb = self.bkeys.size
        self.brb0 = np.array([rb0[self.band == b].mean() for b in range(self.nb)])
        bs = self.ltb.shell(self.brb0)
        self.bRi, self.bm, self.btah = bs["R"], bs["m"], bs["tau_ah"]

    # ---- band means at a coordinate time ----
    def bands_at(self, t):
        r = self.tr.at(t, self.tr.r)
        tau = self.tr.at(t, self.tr.tau)
        br = np.full(self.nb, np.nan)
        btau = np.full(self.nb, np.nan)
        cnt = np.zeros(self.nb, int)
        for b in range(self.nb):
            s = self.band == b
            ok = s & np.isfinite(r) & np.isfinite(tau)
            cnt[b] = ok.sum()
            if cnt[b]:
                br[b] = r[ok].mean()
                btau[b] = tau[ok].mean()
        return br, btau, cnt

    def tau_at_radius(self, t, rf):
        """(tau_det, ddet v1, ddet v2, label at rf, monotone flag)."""
        br, btau, cnt = self.bands_at(t)
        ok = np.isfinite(br) & np.isfinite(btau)
        o = np.argsort(br[ok])
        r_s, tau_s = br[ok][o], btau[ok][o]
        rb_s, tah_s = self.brb0[ok][o], self.btah[ok][o]
        mono = bool(np.all(np.diff(rb_s) > 0))
        tau_f = np.interp(rf, r_s, tau_s)
        rb_f = np.interp(rf, r_s, rb_s)
        tah_f = self.ltb.shell(rb_f)["tau_ah"][0]
        d = tau_s - tah_s
        fin = np.isfinite(d)
        d1 = np.interp(rf, r_s[fin], d[fin])
        return tau_f, d1, tau_f - tah_f, rb_f, mono

    def ddet(self, i_first=None):
        """ddet at the first successful search (or at search index i_first)."""
        f = np.where(self.summ["found"])[0]
        if f.size == 0:
            return None
        i = f[0] if i_first is None else i_first
        t = self.summ["time"][i]
        rf = self.summ["meanradius"][i]
        tau_f, d1, d2, rb_f, mono = self.tau_at_radius(t, rf)
        return {"t": float(t), "r": float(rf), "tau_det": float(tau_f), "ddet_v1": float(d1),
                "ddet_v2": float(d2), "label": float(rb_f), "monotone": mono,
                "mirr": float(self.summ["mirr"][i])}

    def exact_mass(self, t):
        """(m_exact, m_lower, m_upper, label, gap) of the outermost trapped shell at t."""
        br, btau, cnt = self.bands_at(t)
        o = np.argsort(self.brb0)
        rb, tau, tah, m = self.brb0[o], btau[o], self.btah[o], self.bm[o]
        ok = np.isfinite(tau)
        rb, tau, tah, m = rb[ok], tau[ok], tah[ok], m[ok]
        passed = np.isfinite(tah) & (tau >= tah)
        if not passed.any():
            return (np.nan,) * 5
        b = np.where(passed)[0][-1]
        if b + 1 >= rb.size:
            return (np.nan, m[b], np.nan, np.nan, np.nan)
        # exact tau_AH on the table rows between the two bands, tau_slice linear in label
        L = self.ltb
        sel = (L.rbar > rb[b]) & (L.rbar < rb[b + 1])
        lab = np.concatenate([[rb[b]], L.rbar[sel], [rb[b + 1]]])
        tsl = np.interp(lab, [rb[b], rb[b + 1]], [tau[b], tau[b + 1]])
        tah_l = L.shell(lab)["tau_ah"]
        f = tsl - np.where(np.isfinite(tah_l), tah_l, np.inf)
        neg = np.where(f < 0)[0]
        if neg.size == 0:
            lab_star = rb[b + 1]
        else:
            j = neg[0]
            if j == 0:
                lab_star = lab[0]
            else:
                f0, f1 = f[j - 1], f[j]
                if np.isfinite(f1):
                    lab_star = lab[j - 1] + (lab[j] - lab[j - 1]) * f0 / (f0 - f1)
                else:
                    lab_star = lab[j - 1]
        m_star = L.shell(lab_star)["m"][0]
        return m_star, m[b], m[b + 1], lab_star, rb[b + 1] - rb[b]

    def masses(self):
        s = self.summ
        idx = np.where(s["found"])[0]
        out = []
        for i in idx:
            ms, lo, hi, lab, gap = self.exact_mass(s["time"][i])
            out.append((s["time"][i], s["mirr"][i], ms, lo, hi, lab, gap))
        return np.array(out).reshape(-1, 7)

    def dtrap(self, Rtarget=2.603):
        b = int(np.nanargmin(np.abs(self.bRi - Rtarget)))
        sel = np.where(self.band == b)[0]
        R = self.tr.areal_radius()
        res = []
        for p in sel:
            tau, Rp = self.tr.tau[:, p], R[:, p]
            ok = np.isfinite(tau) & np.isfinite(Rp)
            tau, Rp = tau[ok], Rp[ok]
            g = Rp - 2 * self.mi[p]
            cross = np.where((g[:-1] > 0) & (g[1:] <= 0))[0]
            if cross.size == 0:
                res.append(np.nan)
                continue
            k = cross[0]
            tc = tau[k] + (tau[k + 1] - tau[k]) * g[k] / (g[k] - g[k + 1])
            res.append(tc - self.tah[p])
        res = np.array(res)
        return {"band_Ri": float(self.bRi[b]), "n": int(sel.size),
                "n_crossed": int(np.isfinite(res).sum()), "dtrap_mean": float(np.nanmean(res))
                if np.isfinite(res).any() else float("nan"),
                "dtrap_std": float(np.nanstd(res)) if np.isfinite(res).any() else float("nan")}


def bh_rule(summ, nmin=3, span_mass=5.0):
    """Entry 1 rule. Returns dict: bh, persistent_from (time), n_trailing, span, first_found."""
    f = summ["found"]
    t = summ["time"]
    res = {"first_found": float(t[f][0]) if f.any() else None, "n_found": int(f.sum()),
           "n_search": int(f.size), "last_search": float(t[-1])}
    if not f.any() or not f[-1]:
        res.update(bh=False, persistent_from=None, n_trailing=0, span=0.0,
                   reason="last search failed" if f.any() else "never found")
        return res
    j = f.size - 1
    while j > 0 and f[j - 1]:
        j -= 1
    n = f.size - j
    span = t[-1] - t[j]
    mah = np.nanmedian(summ["mirr"][j:])
    bh = (n >= nmin) and (span >= span_mass * mah)
    res.update(bh=bool(bh), persistent_from=float(t[j]), n_trailing=int(n), span=float(span),
               m_ah=float(mah), reason="ok" if bh else "trailing run too short")
    return res


def line_ratio(con_path, tmunu_path, adm_path, r_in, r_out=np.inf, matter_only=False):
    """Hamiltonian constraint over 16 pi E on the x line for r_in < |x| < r_out.
    Weights: 'r2' coordinate r^2 dr, 'r2sg' r^2 sqrt(det gamma) dr, 'line' dx."""
    tc, c = read_tab(con_path)
    te, e = read_tab(tmunu_path)
    ta, a = read_tab(adm_path)
    x = c["x1v"]
    if not (np.array_equal(x, e["x1v"]) and np.array_equal(x, a["x1v"])):
        raise ValueError("tab lines are not on the same points")
    H = c["con_H"]
    E = e["tmunu_E"]
    g = [a["adm_g%s" % k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")]
    det = (g[0] * (g[3] * g[5] - g[4] ** 2) - g[1] * (g[1] * g[5] - g[4] * g[2])
           + g[2] * (g[1] * g[4] - g[3] * g[2]))
    r = np.abs(x)
    dx = np.gradient(x)
    sel = (r > r_in) & (r < r_out)
    if matter_only:
        sel &= E > 0
    out = {"t": tc, "n": int(sel.sum())}
    for name, w in (("r2", r ** 2 * dx), ("r2sg", r ** 2 * np.sqrt(np.abs(det)) * dx),
                    ("line", dx)):
        num = np.sqrt(np.sum(w[sel] * H[sel] ** 2))
        den = np.sqrt(np.sum(w[sel] * (16 * np.pi * E[sel]) ** 2))
        out[name] = float(num / den) if den > 0 else float("inf")
    return out


def line_mots(adm_path, rmin=0.05):
    """Spherical line quantities from the adm tab: areal radius, Misner-Sharp mass and
    the outermost zero of the outgoing expansion (MOTS) on x > 0 and x < 0 separately."""
    t, a = read_tab(adm_path)
    x = a["x1v"]
    res = {"t": t}
    for side, s in (("pos", x > rmin), ("neg", x < -rmin)):
        xs = np.abs(x[s])
        o = np.argsort(xs)
        xs = xs[o]
        gxx = a["adm_gxx"][s][o]
        gT = 0.5 * (a["adm_gyy"][s][o] + a["adm_gzz"][s][o])
        KT = 0.5 * (a["adm_Kyy"][s][o] / a["adm_gyy"][s][o] + a["adm_Kzz"][s][o] / a["adm_gzz"][s][o])
        R = xs * np.sqrt(gT)
        dRdl = np.gradient(R, xs) / np.sqrt(gxx)
        th = dRdl - R * KT                       # outgoing expansion times R/2
        m = 0.5 * R * (1 - dRdl ** 2 + (R * KT) ** 2)
        z = np.where((th[:-1] <= 0) & (th[1:] > 0))[0]
        if z.size:
            k = z[-1]
            w = th[k] / (th[k] - th[k + 1])
            Rm = R[k] + w * (R[k + 1] - R[k])
            res[side] = {"x": float(xs[k] + w * (xs[k + 1] - xs[k])), "m": float(0.5 * Rm)}
        else:
            res[side] = None
        res[side + "_profile"] = (xs, R, m, th)
    return res
