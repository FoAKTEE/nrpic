#!/usr/bin/env python3
"""Reference orbits of P1's binary alone (binary_conv BC-2): separation and orbital phase
against time, and the inspiral time.

From the punctures of an input (bare masses, positions, Bowen-York momenta P):
  newton      Newtonian two-body problem, v = P/m.
  eih_v       first post-Newtonian (EIH) equations of tracks/F-hills/eih/eih.py, v = P/m.
  eih_c       the same with P read as the canonical 1PN momenta (eih.velocities_from_momenta).
  newton_rr   Newton plus the leading-order 2.5PN dissipative Hamiltonian of Schaefer (1995)
              as given in arXiv:1805.07240v5, LRRSJarXiv_v5.tex lines 4071-4085 (Eq. H2.5PN):
                H = (2/5) Iddd_ij(t) [sum_a p_ai p_aj / m_a - m1 m2 n^i n^j / r]   (G = c = 1),
              Iddd held fixed while Hamilton's equations are formed (l. 4083-4085), then
              evaluated on the motion. Derived here:
                dx_a/dt += (4/5) Iddd . p_a / m_a
                dp_1/dt += (2/5) m1 m2 [2 Iddd . x / r^3 - 3 (x . Iddd . x) x / r^5],  dp_2 = -dp_1,
              x = x_1 - x_2; Iddd the third time derivative of the STF quadrupole of the
              Newtonian motion (the free centre of mass adds nothing), checked against a
              finite difference of I_ij along the orbit (self-test, printed).
              Integrated to a separation of 2 (m1 + m2): the inspiral time T_rr.
  peters      quadrupole-formula inspiral time (5/256) a^4 / (m1 m2 M) / F(e),
              F(e) = (1 + 73/24 e^2 + 37/96 e^4) (1 - e^2)^-7/2 [BACKGROUND formula: Peters
              1964; not on arXiv], with a, e of the Newtonian elements, for the bare masses
              and the horizon masses given with --mass.

Usage: refs.py <bin_m8.athinput> <out_dir> [--tend 100] [--mass 0.13,0.137]
Writes refs.json and fig_refs.{pdf,png}.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/eih"))
sys.path.insert(0, HERE)
import eih  # noqa: E402
import figstyle as fs  # noqa: E402


def read_punctures(path):
    blk, prob = None, {}
    for line in open(path):
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            blk = line.strip("<>")
        elif "=" in line and blk == "problem":
            k, v = [s.strip() for s in line.split("=", 1)]
            prob[k] = v
    n = int(prob["ncomp"])
    m = np.array([float(prob[f"comp{c}_mass"]) for c in range(n)])
    x = np.array([[float(prob.get(f"comp{c}_x{a}", 0)) for a in (1, 2, 3)] for c in range(n)])
    p = np.array([[float(prob.get(f"comp{c}_p{a}", 0)) for a in (1, 2, 3)] for c in range(n)])
    return m, x, p


def elements(m, x, v):
    r = x[0] - x[1]
    u = v[0] - v[1]
    M = m.sum()
    d = np.linalg.norm(r)
    E = 0.5 * u @ u - M / d
    a = -M / (2 * E)
    h = np.cross(r, u)
    e = np.sqrt(max(0.0, 1 - (h @ h) / (M * a)))
    return d, a, e


def peters_time(a, e, m1, m2):
    F = (1 + 73 / 24 * e ** 2 + 37 / 96 * e ** 4) / (1 - e ** 2) ** 3.5
    return 5 / 256 * a ** 4 / (m1 * m2 * (m1 + m2)) / F


def iddd(m, x, v):
    """Third time derivative of the STF mass quadrupole of the Newtonian relative motion."""
    M = m.sum()
    mu = m[0] * m[1] / M
    r = x[0] - x[1]
    u = v[0] - v[1]
    rn = np.linalg.norm(r)
    acc = -M * r / rn ** 3
    jerk = -M * u / rn ** 3 + 3 * M * (r @ u) * r / rn ** 5
    T = np.outer(jerk, r) + 3 * np.outer(acc, u) + 3 * np.outer(u, acc) + np.outer(r, jerk)
    T = mu * T
    return T - np.trace(T) / 3 * np.eye(3)


def quad(m, x):
    Q = sum(m[a] * np.outer(x[a], x[a]) for a in range(2))
    return Q - np.trace(Q) / 3 * np.eye(3)


def rhs_newton_rr(t, y, m, rr):
    x = y[:6].reshape(2, 3)
    p = y[6:].reshape(2, 3)
    v = p / m[:, None]
    r = x[0] - x[1]
    rn = np.linalg.norm(r)
    f = -m[0] * m[1] * r / rn ** 3
    dx = v.copy()
    dp = np.array([f, -f])
    if rr:
        I3 = iddd(m, x, v)
        dx += 0.8 * (p @ I3.T) / m[:, None]
        g = 0.4 * m[0] * m[1] * (2 * I3 @ r / rn ** 3 - 3 * (r @ I3 @ r) * r / rn ** 5)
        dp += np.array([g, -g])
    return np.concatenate([dx.ravel(), dp.ravel()])


def rhs_eih(t, y, m):
    x = y[:6].reshape(2, 3)
    v = y[6:].reshape(2, 3)
    a = eih.accel(x, v, m)
    return np.concatenate([v.ravel(), a.ravel()])


def sep_phase(X):
    d = X[:, 0] - X[:, 1]
    s = np.linalg.norm(d, axis=1)
    ph = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    return s, ph - ph[0]


def main():
    args = sys.argv[1:]
    inp, out = args[0], args[1]
    tend = float(args[args.index("--tend") + 1]) if "--tend" in args else 100.0
    hmasses = [float(s) for s in (args[args.index("--mass") + 1].split(",")
                                  if "--mass" in args else ["0.13", "0.137"])]
    os.makedirs(out, exist_ok=True)
    m, x0, p0 = read_punctures(inp)
    v0 = p0 / m[:, None]
    res = {"input": inp, "masses": m.tolist(), "tend": tend}
    d0, a0, e0 = elements(m, x0, v0)
    res["newton_elements"] = dict(sep0=d0, a=a0, e=e0, period=2 * np.pi * np.sqrt(a0 ** 3 / m.sum()),
                                  omega=np.sqrt(m.sum() / a0 ** 3))
    res["peters"] = {f"{mm:.4f}": peters_time(a0, e0, mm, mm) for mm in [m[0]] + hmasses}

    # self-test of Iddd: centred finite difference of I_ij along the Newtonian orbit
    sol = solve_ivp(rhs_newton_rr, (0, 2.0), np.concatenate([x0.ravel(), p0.ravel()]),
                    args=(m, False), method="DOP853", rtol=1e-13, atol=1e-15, dense_output=True)
    h = 0.05
    Qs = [quad(m, sol.sol(1.0 + k * h)[:6].reshape(2, 3)) for k in (-2, -1, 1, 2)]
    fd = (Qs[3] - 2 * Qs[2] + 2 * Qs[1] - Qs[0]) / (2 * h ** 3)
    y1 = sol.sol(1.0)
    an = iddd(m, y1[:6].reshape(2, 3), y1[6:].reshape(2, 3) / m[:, None])
    res["iddd_selftest_rel"] = float(np.max(np.abs(fd - an)) / np.max(np.abs(an)))
    print("Iddd self-test, relative difference to finite difference:", res["iddd_selftest_rel"])

    t = np.linspace(0, tend, int(tend * 4) + 1)
    series = {"t": t.tolist()}
    for name, rr in (("newton", False), ("newton_rr", True)):
        s = solve_ivp(rhs_newton_rr, (0, tend), np.concatenate([x0.ravel(), p0.ravel()]),
                      args=(m, rr), method="DOP853", rtol=1e-12, atol=1e-14, t_eval=t)
        X = s.y[:6].T.reshape(-1, 2, 3)
        sp, ph = sep_phase(X)
        series[name] = dict(sep=sp.tolist(), phase=ph.tolist())
    vc = eih.velocities_from_momenta(x0, p0, m)
    for name, vstart in (("eih_v", v0), ("eih_c", vc)):
        s = solve_ivp(rhs_eih, (0, tend), np.concatenate([x0.ravel(), vstart.ravel()]),
                      args=(m,), method="DOP853", rtol=1e-12, atol=1e-14, t_eval=t)
        X = s.y[:6].T.reshape(-1, 2, 3)
        sp, ph = sep_phase(X)
        series[name] = dict(sep=sp.tolist(), phase=ph.tolist())
    res["series"] = series

    # inspiral time with the 2.5PN Hamiltonian, to separation 2 (m1 + m2)
    def ev(t, y, m, rr):
        return np.linalg.norm(y[:3] - y[3:6]) - 2 * m.sum()
    ev.terminal = True
    longrun = solve_ivp(rhs_newton_rr, (0, 2e4), np.concatenate([x0.ravel(), p0.ravel()]),
                        args=(m, True), method="DOP853", rtol=1e-10, atol=1e-13, events=ev,
                        max_step=2.0)
    T_rr = float(longrun.t_events[0][0]) if len(longrun.t_events[0]) else None
    Xl = longrun.y[:6].T.reshape(-1, 2, 3)
    sl, _ = sep_phase(Xl)
    res["newton_rr_inspiral"] = dict(T_to_2M=T_rr, t=longrun.t[::50].tolist(), sep=sl[::50].tolist())
    print("T_rr (to separation 2 M_b):", T_rr, " Peters:", res["peters"])
    for k in ("newton", "newton_rr", "eih_v", "eih_c"):
        sp = np.array(series[k]["sep"])
        ph = np.array(series[k]["phase"])
        i10, i15, i20 = (np.searchsorted(t, T) for T in (10, 15, 20))
        res[f"{k}_summary"] = dict(sep10=sp[i10], sep15=sp[i15], sep20=sp[i20], sep_min=sp.min(),
                                   sep_max=sp.max(), phase10=ph[i10], phase20=ph[i20],
                                   phase_end=ph[-1])
        print(k, {kk: round(vv, 4) for kk, vv in res[f'{k}_summary'].items()})
    with open(os.path.join(out, "refs.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.7), constrained_layout=True)
    sty = {"newton": dict(color=fs.PAL["blue"], label="Newton"),
           "eih_v": dict(color=fs.PAL["red"], label="EIH, v = P/m"),
           "eih_c": dict(color=fs.PAL["orange"], ls="--", label="EIH, P canonical"),
           "newton_rr": dict(color=fs.PAL["green"], ls=":", label="Newton + 2.5PN")}
    for k, st in sty.items():
        axs[0].plot(t, series[k]["sep"], lw=1.5, **st)
        axs[1].plot(t, series[k]["phase"], lw=1.5, **st)
    axs[0].set_xlabel("t [M]")
    axs[0].set_ylabel("separation [M]")
    axs[1].set_xlabel("t [M]")
    axs[1].set_ylabel("orbital phase [rad]")
    axs[0].legend(fontsize=7, frameon=False)
    axs[2].plot(np.array(res["newton_rr_inspiral"]["t"]), res["newton_rr_inspiral"]["sep"],
                color=fs.PAL["green"], lw=1.0)
    for mm, T in res["peters"].items():
        axs[2].axvline(T, **fs.MASK_LINE)
    axs[2].set_xlabel("t [M]")
    axs[2].set_ylabel("separation [M], Newton + 2.5PN")
    axs[2].set_title(f"T(2.5PN) = {T_rr:.0f} M; Peters lines", fontsize=8)
    fs.save(fig, os.path.join(out, "fig_refs"))


if __name__ == "__main__":
    main()
