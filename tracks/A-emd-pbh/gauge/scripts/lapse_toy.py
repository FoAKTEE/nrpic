"""T1 of tracks/A-emd-pbh/gauge/JOURNAL.md: the lapse of candidate slicing conditions in two
homogeneous dust regions with zero shift.

    python3 -I lapse_toy.py --out OUTDIR [--X 56]

Regions (units H_i = 1, a_i = 1, initial proper time tau_i = 2/3):
  background  Einstein-de Sitter, a = (3 tau / 2)^(2/3), K = -2 / tau;
  top-hat     closed dust with the same big-bang time, b = A (1 - cos psi),
              tau = B (psi - sin psi), A^3 = G M B^2 with G M = 1/2, collapsing when the
              background has expanded by X (B = tau_i X^(3/2) / (2 pi)).
Each region keeps a uniform lapse, d tau / dt = alpha, K = -3 (db/dtau) / b; the lapse
obeys one of the conditions below. Lapse gradients, the shift and the region boundary
are ignored (the toy describes the centre of a region before gauge waves from its edge
arrive). The script prints a table, writes OUTDIR/lapse_toy.json and the figure
OUTDIR/lapse_toy.{png,pdf}.

Conditions (name: right-hand side d alpha / dt; source):
  geodesic      0                                     alpha = 1, beta = 0
  onelog        -2 alpha K                            lapse_oplog = 2 (z4c_calcrhs.cpp:687-692)
  onelog_Kb     -2 alpha (K - K_b(t))                 2608.13206 PRD.tex:243-246 (new source)
  kdriver2      -2 alpha_ref alpha (K - <K>)          lapse_oplog = 0, lapse_kdriver = 2
                                                      (z4c_calcrhs.cpp:46-70, 693-701)
  onelog_Kloc   -2 alpha (K + 2 / tau_local)          2610.23218 main.tex:213-216 (new source)
  expdamp       -2 alpha exp(-alpha) K                2610.23218 main.tex:232-236 (new source)
  softplus      -2 alpha g_s+(K, T), T = min(T, -g)   2610.23218 main.tex:240-249, S = 450 L,
                                                      L = 4 / H_i (main.tex:76) (new source)
  conformal     -(1/3) alpha^2 K                      lapse_harmonic = 1/3 (cosmo/README.md)
  conformal_kd  -(1/3) alpha^2 K - alpha_ref alpha (K - <K>)   cosmo E1 (lapse_kdriver = 1)
  volume        -(1/3) gamma^(1/6) alpha K            lapse_volume = 1/3 (cosmo TESTLOG 341-350)
  conformal_Kb  H_conf alpha - 2 a alpha (K - K_b)    2608.13206 PRD.tex:347-352 (new source)
In the toy <K> is the background K (the top-hat volume is negligible) and alpha_ref is
the larger of the two lapses.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic.figstyle import use_style, SERIES, GUIDE, MASK_LINE, FULL_WIDTH  # noqa: E402

GM = 0.5
TAU_I = 2.0 / 3.0


def a_bg(tau):
    return (1.5 * tau) ** (2.0 / 3.0)


def K_bg(tau):
    return -2.0 / tau


class TopHat:
    def __init__(self, X):
        self.tau_crunch = TAU_I * X ** 1.5
        self.B = self.tau_crunch / (2.0 * math.pi)
        self.A = (GM * self.B ** 2) ** (1.0 / 3.0)

    def psi(self, tau):
        """Solve psi - sin psi = tau / B on [0, 2 pi] (Newton with bisection guard)."""
        m = tau / self.B
        if m <= 0.0:
            return 0.0
        if m >= 2.0 * math.pi:
            return 2.0 * math.pi
        lo, hi = 0.0, 2.0 * math.pi
        x = (6.0 * m) ** (1.0 / 3.0) if m < 1.0 else math.pi
        for _ in range(200):
            f = x - math.sin(x) - m
            if f > 0:
                hi = x
            else:
                lo = x
            d = 1.0 - math.cos(x)
            xn = x - f / d if d > 1e-300 else 0.5 * (lo + hi)
            if not (lo < xn < hi):
                xn = 0.5 * (lo + hi)
            if abs(xn - x) < 1e-15 * max(1.0, abs(x)):
                x = xn
                break
            x = xn
        return x

    def b(self, tau):
        return self.A * (1.0 - math.cos(self.psi(tau)))

    def K(self, tau):
        p = self.psi(tau)
        c = 1.0 - math.cos(p)
        H = math.sin(p) / (self.B * c * c)
        return -3.0 * H

    def delta_lin(self, tau):
        return 0.15 * (6.0 * tau / self.B) ** (2.0 / 3.0)


def softplus(K, T, S):
    z = S * (K - T)
    if z > 50.0:
        return K
    return math.log1p(math.exp(z)) / S + T


CONDITIONS = ["geodesic", "onelog", "onelog_Kb", "kdriver2", "onelog_Kloc", "expdamp",
              "softplus", "conformal", "conformal_kd", "volume", "conformal_Kb"]
CONFORMAL = {"conformal", "conformal_kd", "volume", "conformal_Kb"}
S_SOFT = 450.0 * 4.0


def rhs(cond, t, y, th, Tstate):
    tau_b, tau_c, al_b, al_c = y
    Kb = K_bg(tau_b)
    Kc = th.K(tau_c)
    ab = a_bg(tau_b)
    bc = th.b(tau_c)
    aref = max(al_b, al_c)
    out = np.zeros(4)
    out[0] = al_b
    out[1] = al_c
    for idx, (al, K, sc, tau_loc, T) in ((2, (al_b, Kb, ab, tau_b, Tstate[0])),
                                          (3, (al_c, Kc, bc, tau_c, Tstate[1]))):
        if cond == "geodesic":
            r = 0.0
        elif cond == "onelog":
            r = -2.0 * al * K
        elif cond == "onelog_Kb":
            r = -2.0 * al * (K - Kb)
        elif cond == "kdriver2":
            r = -2.0 * aref * al * (K - Kb)
        elif cond == "onelog_Kloc":
            r = -2.0 * al * (K + 2.0 / tau_loc)
        elif cond == "expdamp":
            r = -2.0 * al * math.exp(-al) * K
        elif cond == "softplus":
            r = -2.0 * al * softplus(K, T, S_SOFT)
        elif cond == "conformal":
            r = -(1.0 / 3.0) * al * al * K
        elif cond == "conformal_kd":
            r = -(1.0 / 3.0) * al * al * K - aref * al * (K - Kb)
        elif cond == "volume":
            r = -(1.0 / 3.0) * sc * al * K
        elif cond == "conformal_Kb":
            Hb = -Kb / 3.0
            r = ab * Hb * al - 2.0 * ab * al * (K - Kb)
        else:
            raise ValueError(cond)
        out[idx] = r
    return out


def lapse_speed(cond, al, K, sc, aref, T):
    """Coordinate speed of the lapse gauge mode, sqrt(F)/sc for d_t alpha = -F K + ..."""
    if cond == "geodesic":
        F = 0.0
    elif cond in ("onelog", "onelog_Kb", "onelog_Kloc"):
        F = 2.0 * al
    elif cond == "kdriver2":
        F = 2.0 * aref * al
    elif cond == "expdamp":
        F = 2.0 * al * math.exp(-al)
    elif cond == "softplus":
        z = S_SOFT * (K - T)
        sig = 1.0 / (1.0 + math.exp(-z)) if z > -700 else 0.0
        F = 2.0 * al * sig
    elif cond == "conformal":
        F = al * al / 3.0
    elif cond == "conformal_kd":
        F = al * al / 3.0 + aref * al
    elif cond == "volume":
        F = sc * al / 3.0
    elif cond == "conformal_Kb":
        F = 2.0 * sc * al  # 2 a alpha with the background a (sc of the background)
    return math.sqrt(max(F, 0.0)) / sc


def integrate(cond, th, X, a_end_factor=3.0, alpha_floor=1e-6, t_max=2.0e4):
    """Classical RK4 in coordinate time with a step limited by the local time scales."""
    y = np.array([TAU_I, TAU_I, 1.0, 1.0])
    T = [0.0, 0.0]
    t = 0.0
    rec = {k: [] for k in ("t", "tau_b", "tau_c", "al_b", "al_c", "a", "b", "dlin",
                           "vmax_b", "vmax_c")}
    status = "running"
    t_aX = None
    nstep = 0
    while True:
        tau_b, tau_c, al_b, al_c = y
        a = a_bg(tau_b)
        b = th.b(tau_c)
        Kc = th.K(tau_c)
        Kb = K_bg(tau_b)
        aref = max(al_b, al_c)
        if True:
            rec["t"].append(t)
            rec["tau_b"].append(tau_b)
            rec["tau_c"].append(tau_c)
            rec["al_b"].append(al_b)
            rec["al_c"].append(al_c)
            rec["a"].append(a)
            rec["b"].append(b)
            rec["dlin"].append(th.delta_lin(tau_c))
            # light speed alpha/scale and the lapse mode, per region
            rec["vmax_b"].append(max(al_b / a, lapse_speed(cond, al_b, Kb, a, aref, T[0])))
            sc_c = a if cond == "conformal_Kb" else b
            rec["vmax_c"].append(max(al_c / b, lapse_speed(cond, al_c, Kc, sc_c, aref, T[1])
                                     * (sc_c / b)))
        if t_aX is None and a >= X:
            t_aX = t
        if tau_c >= th.tau_crunch * (1.0 - 1e-7):
            status = "crunch"
            break
        if al_c < alpha_floor:
            status = "frozen"
            break
        if a >= a_end_factor * X:
            status = "background_end"
            break
        if t > t_max:
            status = "t_max"
            break
        # step: resolve the background, the top-hat and the lapse
        k1 = rhs(cond, t, y, th, T)
        rate = max(abs(Kb) * al_b, abs(Kc) * al_c, abs(k1[2]) / max(al_b, 1e-300),
                   abs(k1[3]) / max(al_c, 1e-300), 1e-12)
        rem = th.tau_crunch - tau_c
        h = min(2e-3 / rate, 0.05 * rem / max(al_c, 1e-300) + 1e-14, 0.5)
        k2 = rhs(cond, t + 0.5 * h, y + 0.5 * h * k1, th, T)
        k3 = rhs(cond, t + 0.5 * h, y + 0.5 * h * k2, th, T)
        k4 = rhs(cond, t + h, y + h * k3, th, T)
        y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        y[1] = min(y[1], th.tau_crunch)
        t += h
        nstep += 1
        if cond == "softplus":
            Kb2 = K_bg(y[0])
            Kc2 = th.K(y[1])
            T[0] = min(T[0], -softplus(Kb2, T[0], S_SOFT))
            T[1] = min(T[1], -softplus(Kc2, T[1], S_SOFT))
    for k in rec:
        rec[k] = np.array(rec[k])
    return rec, status, t_aX, nstep


def t_at_a(rec, X):
    """Coordinate time at which the background reaches a = X (linear interpolation)."""
    a = rec["a"]
    i = np.searchsorted(a, X)
    if i == 0 or i >= len(a):
        return None
    f = (X - a[i - 1]) / (a[i] - a[i - 1])
    return rec["t"][i - 1] + f * (rec["t"][i] - rec["t"][i - 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--X", type=float, default=56.0)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    X = args.X
    th = TopHat(X)
    psi_i = th.psi(TAU_I)
    b_i = th.b(TAU_I)
    b_max = 2.0 * th.A
    summary = {"X": X, "tau_crunch": th.tau_crunch, "A": th.A, "B": th.B,
               "b_i": b_i, "b_max": b_max, "b_max_over_b_i": b_max / b_i,
               "delta_lin_i": th.delta_lin(TAU_I),
               "delta_i": (1.0 / b_i) ** 3 - 1.0, "psi_i": psi_i,
               "a_turnaround": a_bg(math.pi * th.B), "conditions": {}}
    print(f"X = {X}: tau_crunch = {th.tau_crunch:.4f}, b_i = {b_i:.6f}, "
          f"b_max = {b_max:.4f}, b_max/b_i = {b_max / b_i:.3f}, "
          f"delta_lin(tau_i) = {th.delta_lin(TAU_I):.5f}, "
          f"a(turnaround) = {a_bg(math.pi * th.B):.3f}")
    print("predicted (journal P1.1, P1.2): onelog top-hat max 1 + 6 ln(b_max/b_i) = "
          f"{1 + 6 * math.log(b_max / b_i):.3f}; expdamp ln(e + 6 ln(b_max/b_i)) = "
          f"{math.log(math.e + 6 * math.log(b_max / b_i)):.3f}")
    recs = {}
    hdr = (f"{'condition':13s} {'status':15s} {'max al_c':>9s} {'min al_c':>10s} "
           f"{'al_b(a=X)':>10s} {'max al_b':>9s} {'tau_c/crunch':>12s} {'b_c/b_max':>10s} "
           f"{'phase':>9s} {'t(a=X)':>9s} {'max v_b':>8s} {'max v_c':>8s}")
    print(hdr)
    for cond in CONDITIONS:
        rec, status, _, nstep = integrate(cond, th, X)
        recs[cond] = rec
        tX = t_at_a(rec, X)
        iX = np.searchsorted(rec["a"], X)
        al_b_X = float(rec["al_b"][min(iX, len(rec["a"]) - 1)])
        frac = float(rec["tau_c"][-1] / th.tau_crunch)
        psi_end = th.psi(rec["tau_c"][-1])
        phase = "expanding" if psi_end < math.pi else "collapsing"
        row = {"status": status, "steps": nstep,
               "max_alpha_c": float(rec["al_c"].max()),
               "min_alpha_c": float(rec["al_c"].min()),
               "alpha_b_at_aX": al_b_X,
               "max_alpha_b": float(rec["al_b"].max()),
               "tau_c_over_crunch_end": frac,
               "b_c_end_over_b_max": float(rec["b"][-1] / b_max),
               "phase_end": phase,
               "t_at_aX": None if tX is None else float(tX),
               "max_v_b": float(rec["vmax_b"].max()),
               "max_v_c": float(rec["vmax_c"].max()),
               "a_end": float(rec["a"][-1])}
        summary["conditions"][cond] = row
        print(f"{cond:13s} {status:15s} {row['max_alpha_c']:9.3f} {row['min_alpha_c']:10.3e} "
              f"{al_b_X:10.3f} {row['max_alpha_b']:9.3f} {frac:12.6f} "
              f"{row['b_c_end_over_b_max']:10.4f} {phase:>9s} "
              f"{(tX if tX is not None else float('nan')):9.3f} {row['max_v_b']:8.3f} "
              f"{row['max_v_c']:8.3f}")
    # P1.6 check: coordinate time to a = X
    t_cos = TAU_I * X ** 1.5 - TAU_I
    t_conf = 2.0 * (math.sqrt(X) - 1.0)
    summary["P1.6"] = {"t_cosmic_exact": t_cos, "t_conformal_exact": t_conf,
                       "ratio": t_cos / t_conf,
                       "t_cosmic_toy_onelog_Kb": summary["conditions"]["onelog_Kb"]["t_at_aX"],
                       "t_conformal_toy": summary["conditions"]["conformal"]["t_at_aX"]}
    print(f"P1.6: cosmic {t_cos:.4f} (toy {summary['P1.6']['t_cosmic_toy_onelog_Kb']}), "
          f"conformal {t_conf:.4f} (toy {summary['P1.6']['t_conformal_toy']}), "
          f"ratio {t_cos / t_conf:.3f}")
    # P1.3: conformal-family conditions without a driver, run on until the crunch
    summary["P1.3_long"] = {}
    for cond in ("conformal", "volume"):
        rec, status, _, nstep = integrate(cond, th, X, a_end_factor=1e4, t_max=1e5)
        summary["P1.3_long"][cond] = {"status": status, "t_end": float(rec["t"][-1]),
                                      "a_end": float(rec["a"][-1]),
                                      "tau_c_over_crunch": float(rec["tau_c"][-1] /
                                                                 th.tau_crunch),
                                      "alpha_c_end": float(rec["al_c"][-1])}
        print(f"P1.3 long run {cond}: {status} at t = {rec['t'][-1]:.3f}, "
              f"a = {rec['a'][-1]:.2f}, tau_c/crunch = {rec['tau_c'][-1] / th.tau_crunch:.8f}, "
              f"alpha_c = {rec['al_c'][-1]:.3e}")
    with open(os.path.join(args.out, "lapse_toy.json"), "w") as f:
        json.dump(summary, f, indent=1)

    # ---- figure ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    use_style()
    fig, axs = plt.subplots(2, 2, figsize=(FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.08, top=0.97, wspace=0.27,
                        hspace=0.28)
    cols = {"geodesic": "k", "onelog": SERIES[1], "onelog_Kb": SERIES[0],
            "kdriver2": SERIES[0], "onelog_Kloc": SERIES[3], "expdamp": SERIES[4],
            "softplus": SERIES[2], "conformal": "0.45", "conformal_kd": SERIES[1],
            "volume": "0.45", "conformal_Kb": SERIES[0]}
    ls = {"geodesic": "-", "onelog": "-", "onelog_Kb": "-", "kdriver2": ":",
          "onelog_Kloc": "-", "expdamp": "-", "softplus": "-", "conformal": "--",
          "conformal_kd": "--", "volume": ":", "conformal_Kb": "--"}
    ax = axs[0, 0]
    for c in CONDITIONS:
        r = recs[c]
        ax.plot(r["dlin"], r["al_c"], color=cols[c], ls=ls[c], lw=1.2, label=c)
    ax.axvline(1.062, **MASK_LINE)
    ax.axvline(1.686, **MASK_LINE)
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 2e2)
    ax.set_xlim(0, 1.75)
    ax.set_xlabel(r"linear contrast of the top-hat $\delta^{(1)}(\tau_c)$")
    ax.set_ylabel(r"top-hat lapse $\alpha_c$")
    ax.legend(ncol=2, fontsize=7, loc="lower left")
    ax = axs[0, 1]
    for c in CONDITIONS:
        r = recs[c]
        ax.plot(r["a"], r["al_b"], color=cols[c], ls=ls[c], lw=1.2)
    aa = np.geomspace(1, 3 * X, 200)
    ax.plot(aa, 1 + 6 * np.log(aa), **GUIDE, label=r"$1+6\ln a$")
    ax.plot(aa, aa, color="k", ls=":", lw=1.0, label=r"$a$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"background scale factor $a$")
    ax.set_ylabel(r"background lapse $\alpha_b$")
    ax.legend(loc="upper left")
    ax = axs[1, 0]
    for c in CONDITIONS:
        r = recs[c]
        tn = r["t"] / max(r["t"][-1], 1e-300)
        ax.plot(r["a"], r["tau_c"] / th.tau_crunch, color=cols[c], ls=ls[c], lw=1.2)
    ax.set_xscale("log")
    ax.set_xlabel(r"background scale factor $a$ (coordinate-time proxy)")
    ax.set_ylabel(r"top-hat proper time $\tau_c/\tau_{\rm crunch}$")
    ax.axvline(X, **MASK_LINE)
    ax = axs[1, 1]
    for c in CONDITIONS:
        r = recs[c]
        ax.plot(r["a"], np.maximum(r["vmax_b"], r["vmax_c"]), color=cols[c], ls=ls[c],
                lw=1.2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"background scale factor $a$")
    ax.set_ylabel(r"largest coordinate speed (light, lapse mode)")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(args.out, f"lapse_toy.{ext}"))
    print("wrote", os.path.join(args.out, "lapse_toy.png"))


if __name__ == "__main__":
    main()
