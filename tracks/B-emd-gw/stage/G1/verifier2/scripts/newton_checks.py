"""Newtonian-mode tests of Track B checked against references I derived (verifier2).

    python3 newton_checks.py OUTDIR  east:N:RUNDIR ... sin:N:RUNDIR ... ell:N:RUNDIR ...
    (OUTDIR "-": $NRPIC_RUN_DIR)

Pancakes (periodic box L = 1, comoving x, conformal time t, a = (1 + t/2)^2, H = 1 at
t = 0; momentum slots hold a dx/dt). Before any sheet crossing a plane-symmetric cold
system is exact in 1D: for the sheet with mass coordinate q (cumulative mass / total * L,
origin chosen so that the mass-uniform mean of s = x - q is zero) the force is
(3/2) calH^2 s, so s'' + calH s' = (3/2) calH^2 s, s(a) = A a + B a^(-3/2), with
s(1) = s0 and ds/da(1) = u0 (a = 1, da/dt = 1). A, B per sheet from the t = 0 snapshot.
  east: the tracked line (traj.bin) against the exact sheets; error in units of the
        displacement (a - 1) d/k (d = 0.05, k = 2 pi); first crossing of neighbouring
        tracked particles in the code and in the exact discrete sheets.
  sin:  I_xx(t) of the history against sum m (q + s(a))^2 of the exact sheets (no wrap).
Ellipsoid (isolated, no expansion, G = 1): homogeneous ellipsoid ODE
  d2R_i/dt2 = -2 pi rho A_i R_i,  A_i = (2/3) R1 R2 R3 R_D(R_j^2, R_k^2, R_i^2),
  rho = 3 M / (4 pi R1 R2 R3), from the axes and rates in particles.json (checked against
  the particle file: I_ii = M R_i^2 / 5 of the lattice, linear velocity field), to the first
  zero of R_x; the code's crossing is the first sign change of dI_xx/dt (- to +) in the
  history, linearly interpolated.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.special import elliprd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import athio  # noqa: E402
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

KW = 2*np.pi
D0 = 0.05


def sheets(snap, L=1.0):
    """Sheets of the t = 0 snapshot: x0, u0, mass, mass coordinate q (mean of s zero)."""
    x = snap["x"][:, 0]
    key = np.round(x, 11)
    ux, inv = np.unique(key, return_inverse=True)
    m = np.bincount(inv, weights=snap["m"])
    u = np.bincount(inv, weights=snap["m"]*snap["u"][:, 0])/m
    x0 = np.bincount(inv, weights=snap["m"]*x)/m
    order = np.argsort(x0)
    x0, u, m = x0[order], u[order], m[order]
    M = m.sum()
    qraw = (np.cumsum(m) - 0.5*m)/M*L
    s = x0 - qraw
    c = (m*s).sum()/M
    q = qraw + c
    s0 = x0 - q
    # sheet index of every particle
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    return {"x0": x0, "u0": u, "m": m, "q": q, "s0": s0, "pid_sheet": rank[inv],
            "P_total": float((m*u).sum())}


def exact_x(sh, a):
    A = (1.5*sh["s0"] + sh["u0"])/2.5
    B = (sh["s0"] - sh["u0"])/2.5
    return sh["q"][None, :] + A[None, :]*np.asarray(a)[:, None] + B[None, :]*np.asarray(a)[:, None]**-1.5


def first_cross_exact(sh):
    A = (1.5*sh["s0"] + sh["u0"])/2.5
    B = (sh["s0"] - sh["u0"])/2.5
    q = sh["q"]
    n = len(q)
    best = np.inf
    for i in range(n):
        j = (i + 1) % n
        dq = q[j] - q[i] + (1.0 if j == 0 else 0.0)
        f = lambda a: dq + (A[j] - A[i])*a + (B[j] - B[i])*a**-1.5
        if f(200.0) < 0:
            best = min(best, brentq(f, 1.0, 200.0, xtol=1e-12))
    return best


def east(n, rundir):
    snap = athio.read_snap(os.path.join(rundir, "newton.part.00000.bin"))
    sh = sheets(snap)
    tr = athio.read_traj(os.path.join(rundir, "newton.traj.bin"))
    tags = np.unique(tr[:, 1]).astype(int)
    tag0 = snap["tag"]
    sheet_of_tag = {int(t): int(sh["pid_sheet"][np.flatnonzero(tag0 == t)[0]]) for t in tags}
    times = np.unique(tr[:, 0])
    X = np.full((len(times), len(tags)), np.nan)
    ti = np.searchsorted(times, tr[:, 0])
    col = {t: i for i, t in enumerate(tags)}
    X[ti, [col[int(t)] for t in tr[:, 1]]] = tr[:, 2]
    a = (1.0 + times/2.0)**2
    xe_all = exact_x(sh, a)
    xe = xe_all[:, [sheet_of_tag[int(t)] for t in tags]]
    d = (X - xe + 0.5) % 1.0 - 0.5
    unit = (a - 1.0)*D0/KW
    with np.errstate(invalid="ignore", divide="ignore"):
        err = np.nanmax(np.abs(d), axis=1)/unit
    # first crossing in the code: order of the tracked line (sorted by q) changes
    qs = np.array([sh["q"][sheet_of_tag[int(t)]] for t in tags])
    o = np.argsort(qs)
    # unwrap: x = q + s with s the minimum-image deviation from the mass coordinate
    Xo = qs[o][None, :] + ((X[:, o] - qs[o][None, :] + 0.5) % 1.0 - 0.5)
    gaps = np.diff(np.concatenate([Xo, Xo[:, :1] + 1.0], axis=1), axis=1)
    bad = np.flatnonzero((gaps < 0).any(axis=1))
    a_cross_code = None
    if len(bad):
        i = bad[0]
        g0 = gaps[i - 1].min(); g1 = gaps[i].min()
        # interpolate the smallest gap linearly in a
        jj = np.argmin(gaps[i])
        ga, gb = gaps[i - 1, jj], gaps[i, jj]
        a_cross_code = float(a[i - 1] + (a[i] - a[i - 1])*ga/(ga - gb))
    out = {"n": n, "ntrack": len(tags), "P_total": sh["P_total"],
           "a_cross_exact_discrete": first_cross_exact(sh),
           "a_cross_code": a_cross_code, "err_at": {}}
    for at in (2, 5, 10, 15, 20):
        i = int(np.argmin(np.abs(a - at)))
        out["err_at"][str(at)] = {"a": float(a[i]), "err": float(err[i])}
    return out, (a, err)


def sin_case(n, rundir):
    snap = athio.read_snap(os.path.join(rundir, "newton.part.00000.bin"))
    sh = sheets(snap)
    h = np.loadtxt(os.path.join(rundir, "newton.newton.hst"))
    t, a_col, Ixx = h[:, 0], h[:, 2], h[:, 18]
    a = (1.0 + t/2.0)**2
    # exact: I_xx = sum_sheets m (q + s(a))^2 (x unwrapped)
    xe = exact_x(sh, a)
    Ie = (sh["m"][None, :]*xe**2).sum(axis=1)
    # the code sums over particles with their (wrapped) positions; sheets do not wrap
    win = (a >= 1.2) & (a <= 15.0)
    rng = np.abs(Ie[win] - Ie[0]).max()
    err = np.abs(h[:, 18] - Ie)
    return {"n": n, "a_column_vs_formula_max": float(np.abs(a_col - a).max()),
            "max_abs_Ixx_err_over_range_1p2_15": float(err[win].max()/rng),
            "Ixx_err_at_a": {str(at): float(err[int(np.argmin(np.abs(a - at)))]/rng)
                             for at in (2, 5, 10, 15)},
            "P_total": sh["P_total"]}, (a, (h[:, 18] - Ie)/rng)


def ell_ode(R0, V0, M):
    def rhs(t, y):
        R = y[:3]
        rho = 3*M/(4*np.pi*R[0]*R[1]*R[2])
        A = np.array([2.0/3.0*R[0]*R[1]*R[2]*elliprd(R[(i+1) % 3]**2, R[(i+2) % 3]**2, R[i]**2)
                      for i in range(3)])
        return np.concatenate([y[3:], -2*np.pi*rho*A*R])
    ev = lambda t, y: y[0]
    ev.terminal = True
    ev.direction = -1
    sol = solve_ivp(rhs, (0, 40), np.concatenate([R0, V0]), method="DOP853", rtol=1e-12,
                    atol=1e-13, events=ev, dense_output=True)
    return sol


def ell_case(n, rundir):
    with open(os.path.join(rundir, "particles.json")) as f:
        js = json.load(f)
    snap = athio.read_snap(os.path.join(rundir, "newton.part.00000.bin"))
    x, u, m = snap["x"], snap["u"], snap["m"]
    M = m.sum()
    com = (m[:, None]*x).sum(0)/M
    I = np.array([(m*(x[:, i] - com[i])**2).sum() for i in range(3)])
    R_lat = np.sqrt(5*I/M)
    H = np.array([(m*u[:, i]*(x[:, i] - com[i])).sum()/(m*(x[:, i] - com[i])**2).sum()
                  for i in range(3)])
    resid = np.sqrt((m[:, None]*(u - H[None, :]*(x - com))**2).sum()/M)
    R0 = np.array(js["R0"]); V0 = np.array(js["V0"])
    sol = ell_ode(R0, V0, js["mass"])
    tx_ode = float(sol.t_events[0][0])
    sol_l = ell_ode(R_lat, H*R_lat, M)
    tx_lat = float(sol_l.t_events[0][0])
    h = np.loadtxt(os.path.join(rundir, "newton.newton.hst"))
    t, dI = h[:, 0], h[:, 24]
    i = np.flatnonzero((dI[:-1] < 0) & (dI[1:] >= 0))[0]
    tx_code = float(t[i] - dI[i]*(t[i+1] - t[i])/(dI[i+1] - dI[i]))
    tt = js["t_turn"]
    return {"n": n, "t_turn": tt, "mass_json": js["mass"], "mass_particles": float(M),
            "R0_json": list(R0), "R_lattice": list(R_lat), "V0_json": list(V0),
            "V_lattice": list(H*R_lat), "velocity_residual_rms": float(resid),
            "tx_ode_json_code_time": tx_ode, "tx_ode_json_tk": tx_ode + tt,
            "tx_ode_lattice_tk": tx_lat + tt, "tx_code_tk": tx_code + tt,
            "tx_code_rel_err_vs_ode": (tx_code - tx_ode)/(tx_ode + tt)}, (sol, h)


def main():
    outdir = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(outdir, exist_ok=True)
    fs.use_style()
    res = {"east": {}, "sin": {}, "ell": {}}
    curves = {"east": {}, "sin": {}, "ell": {}}
    for spec in sys.argv[2:]:
        kind, n, rundir = spec.split(":", 2)
        n = int(n)
        f = {"east": east, "sin": sin_case, "ell": ell_case}[kind]
        r, c = f(n, rundir)
        res[kind][str(n)] = r
        curves[kind][n] = c
        print(kind, n, json.dumps(r)[:900], flush=True)
    ns = sorted(res["ell"], key=int)
    if len(ns) >= 3:
        t = [res["ell"][k]["tx_code_tk"] for k in ns]
        h = [1.0/int(k) for k in ns]
        p = np.log((t[0] - t[1])/(t[1] - t[2]))/np.log(2.0)
        res["ell_richardson"] = {"order": float(p), "t_inf": float(t[2] - (t[1] - t[2])/(2**p - 1))}
    with open(os.path.join(outdir, "newton_checks.json"), "w") as fo:
        json.dump(res, fo, indent=1)

    cols = {16: fs.PAL["yellow"], 32: fs.PAL["red"], 64: fs.PAL["blue"], 128: fs.PAL["green"]}
    if curves["east"]:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
        for n, (a, err) in sorted(curves["east"].items()):
            ax[0].plot(a, err, color=cols[n], label=f"$n={n}$")
            ax[0].axvline(res["east"][str(n)]["a_cross_exact_discrete"], color=cols[n], lw=1.0, ls=":")
        ax[0].set_yscale("log"); ax[0].set_xlim(1, 25)
        ax[0].set_xlabel(r"$a$"); ax[0].set_ylabel(r"max sheet error / $[(a-1)d/k]$")
        ax[0].legend(loc="lower right", ncol=3)
        for n, (a, e) in sorted(curves["sin"].items()):
            ax[1].plot(a, np.abs(e), color=cols[n], label=f"$n={n}$")
        ax[1].set_yscale("log"); ax[1].set_xlabel(r"$a$")
        ax[1].set_ylabel(r"$|I_{xx}-I_{xx}^{\rm exact}|$ / range")
        ax[1].legend(loc="lower right", ncol=3)
        fs.save(fig, os.path.join(outdir, "pancakes"))
        plt.close(fig)
    if curves["ell"]:
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
        anyr = None
        for n, (sol, h) in sorted(curves["ell"].items()):
            tt = res["ell"][str(n)]["t_turn"]
            M = res["ell"][str(n)]["mass_particles"]
            ax[0].plot(h[:, 0] + tt, np.sqrt(np.maximum(5*h[:, 18]/M, 0)), color=cols[n],
                       label=fr"code $N={n}$, $\sqrt{{5I_{{xx}}/M}}$")
            anyr = (sol, tt)
        sol, tt = anyr
        tg = np.linspace(0, sol.t[-1], 400)
        ax[0].plot(tg + tt, sol.sol(tg)[0], **fs.GUIDE, label=r"ODE $R_x$ (own)")
        ax[0].set_xlabel(r"$t/t_k$"); ax[0].set_ylabel(r"$R_x$")
        ax[0].legend(loc="lower left")
        Ns = np.array(sorted(int(k) for k in res["ell"]))
        tx = np.array([res["ell"][str(k)]["tx_code_tk"] for k in Ns])
        txo = res["ell"][str(Ns[0])]["tx_ode_json_tk"]
        ax[1].loglog(Ns, np.abs(tx - txo)/txo, "o-", color=fs.PAL["red"], label="code, own crossing")
        ax[1].loglog(Ns, (np.abs(tx[0] - txo)/txo)*(Ns/Ns[0])**-2.0, **fs.GUIDE, label=r"$\propto N^{-2}$")
        ax[1].set_xlabel(r"$N$"); ax[1].set_ylabel(r"$|t_x - t_x^{\rm ODE}|/t_x^{\rm ODE}$")
        ax[1].legend(loc="lower left")
        fs.save(fig, os.path.join(outdir, "ellipsoid"))
        plt.close(fig)


if __name__ == "__main__":
    main()
