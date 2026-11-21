#!/usr/bin/env python3
"""Test T4 of work package dfix: external gravity of the Newtonian mode (fixed point
mass, background acceleration) and the accretion diagnostics in that mode.

    runreg.py --purpose "..." --cores 5 -- python3 tracks/core/analysis/dfix/t4_newton.py \
        --exe <athena> [--fig PREFIX]
    t4_newton.py --replot RUN --fig PREFIX

Cases (inputs problems/tests/newton_point_mass.athinput and ..._periodic.athinput, G = 1,
particles of rest mass 1e-10), each in $NRPIC_RUN_DIR/<name>/:
  kepler       point mass M = 1, s = 0: two bound orbits (a, e) = (1, 0.5) and (0.8, 0.3)
               from the apocentre, 20 time units; exact Kepler motion; sphere r = 1;
               pericentre counter
  plummer      s = 0.3: circular orbits at r = 1 and r = 0.5 of the softened potential
  background   no point mass, newton_bg_t0 = 1: growing mode r = r0 (1 + t)^(2/3) and
               decaying mode r = r0 (1 + t)^(1/3), 3 time units
  expand       periodic box, a = (1 + H t/2)^2 with H = 0.1, point mass with s = 0.1
               fixed in the comoving coordinates: two bound orbits against an ODE
               solution of dx/dt = p/a, dp/dt = -grad Phi; constancy of C of the history
  expand_phys  the same with newton_pm_soft_frame = physical (s/a)
Writes t4_newton.json into the run directory and PREFIX_newton.png.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import io as nio   # noqa: E402

ISO = os.path.join(REPO, "problems", "tests", "newton_point_mass.athinput")
PER = os.path.join(REPO, "problems", "tests", "newton_point_mass_periodic.athinput")
MP = 1.0e-10
KEPLER = ((1.0, 0.5, (1, 0, 0), (0, 1, 0)), (0.8, 0.3, (0, 1, 0), (0, 0, 1)))
SOFT = 0.3
HUB = 0.1
SOFT_EXP = 0.1


def kepler_state(a, e, n1, n2, t):
    """position of the Kepler orbit (G M = 1) started at its apocentre along n1 with the
    velocity along n2, at the times t"""
    n1, n2 = np.array(n1, float), np.array(n2, float)
    nmot = a**-1.5
    mean = np.pi + nmot*np.asarray(t, float)          # mean anomaly from the pericentre
    xi = np.array([brentq(lambda z: z - e*np.sin(z) - m, m - 1.0, m + 1.0, xtol=1e-14)
                   for m in mean])
    xp = a*(np.cos(xi) - e)                            # along the pericentre direction -n1
    yp = a*np.sqrt(1.0 - e*e)*np.sin(xi)               # along -n2 at the pericentre
    return -xp[:, None]*n1[None, :] - yp[:, None]*n2[None, :]


def kepler_events(a, e, tend, rad):
    per = 2.0*np.pi*a**1.5
    peri = [per*(k + 0.5) for k in range(100) if per*(k + 0.5) < tend]
    cross = {"in": [], "out": []}
    c = (1.0 - rad/a)/e
    if abs(c) < 1.0:
        xi = np.arccos(c)
        tx = (xi - e*np.sin(xi))*a**1.5                # time from the pericentre to r = rad
        for k in range(100):
            ti, to = per*(k + 0.5) - tx, per*(k + 0.5) + tx
            if ti < tend:
                cross["in"].append(ti)
            if to < tend:
                cross["out"].append(to)
    return {"period": per, "peri": peri, "cross": cross, "E": 1.0 - 0.5/a}


def make_cases(run):
    cases = {}
    # kepler
    x, u = [], []
    for a, e, n1, n2 in KEPLER:
        ra = a*(1.0 + e)
        va = np.sqrt((1.0 - e)/(a*(1.0 + e)))
        x.append(ra*np.array(n1, float))
        u.append(va*np.array(n2, float))
    cases["kepler"] = dict(inp=ISO, x=np.array(x), u=np.array(u), args=[])
    # plummer: circular orbits
    x, u = [], []
    for r, n1, n2 in ((1.0, (1, 0, 0), (0, 1, 0)), (0.5, (0, 0, 1), (1, 0, 0))):
        vc = r*(r*r + SOFT*SOFT)**-0.75
        x.append(r*np.array(n1, float))
        u.append(vc*np.array(n2, float))
    cases["plummer"] = dict(inp=ISO, x=np.array(x), u=np.array(u),
                            args=[f"particles/newton_pm_soft={SOFT}"])
    # background: growing (2/3) and decaying (1/3) modes, t0 = 1
    x, u = [], []
    for r0, n, pw in ((0.5, (1, 0, 0), 2.0/3.0), (0.4, (0, 0.6, 0.8), 2.0/3.0),
                      (0.8, (0, 1, 0), 1.0/3.0), (0.6, (0.57735026919, 0.57735026919, 0.57735026919),
                                                  1.0/3.0)):
        n = np.array(n, float)
        x.append(r0*n)
        u.append(pw*r0*n)
    cases["background"] = dict(inp=ISO, x=np.array(x), u=np.array(u),
                               args=["particles/newton_pm_mass=0.0", "particles/newton_bg_t0=1.0",
                                     "time/tlim=3.0", "particles/acc_radius1=0.7"])
    # expanding periodic box
    x = np.array([[0.6, 0.0, 0.0], [0.0, 0.0, -0.4]])
    u = np.array([[0.0, 0.9, 0.0], [1.0, 0.3, 0.0]])
    cases["expand"] = dict(inp=PER, x=x, u=u, args=[])
    cases["expand_phys"] = dict(inp=PER, x=x, u=u,
                                args=["particles/newton_pm_soft_frame=physical"])
    for name, c in cases.items():
        d = os.path.join(run, name)
        os.makedirs(d, exist_ok=True)
        base = "npmp" if c["inp"] == PER else "npm"
        nio.write_nrp(os.path.join(d, base + ".nrp"), c["x"], c["u"], np.full(len(c["x"]), MP))
        c["dir"], c["base"] = d, base
    return cases


def expand_reference(x0, p0, tend, physical):
    def a(t):
        return (1.0 + 0.5*HUB*t)**2

    def rhs(t, y):
        x, p = y[:3], y[3:]
        s = SOFT_EXP/a(t) if physical else SOFT_EXP
        r2 = x@x + s*s
        return np.concatenate([p/a(t), -x*r2**-1.5])
    sol = solve_ivp(rhs, (0.0, tend), np.concatenate([x0, p0]), method="DOP853", rtol=1e-12,
                    atol=1e-14, dense_output=True)
    return sol.sol


def read_traj(d, base):
    a = np.fromfile(os.path.join(d, base + ".traj.bin")).reshape(-1, 8)
    return a


def judge(run):
    res = {}
    # ---- kepler ----
    d = os.path.join(run, "kepler")
    tr = read_traj(d, "npm")
    k = {"orbits": []}
    for tag, (a, e, n1, n2) in enumerate(KEPLER):
        s = tr[tr[:, 1] == tag]
        ex = kepler_state(a, e, n1, n2, s[:, 0])
        err = np.linalg.norm(s[:, 2:5] - ex, axis=1)
        ev = kepler_events(a, e, s[-1, 0], 1.0)
        k["orbits"].append({"a": a, "e": e, "t_end": float(s[-1, 0]), "max_position_error": float(err.max()),
                            "position_error_end": float(err[-1]), "events": ev})
    hst = np.loadtxt(os.path.join(d, "npm.acc.hst"))
    end = hst[-1]
    k["sphere"] = {"n_in": float(end[17]), "m_in": float(end[18]), "mE_in": float(end[19]),
                   "n_out": float(end[20]), "m_out": float(end[21]), "mE_out": float(end[22])}
    k["sphere_ref"] = {
        "n_in": float(sum(len(o["events"]["cross"]["in"]) for o in k["orbits"])),
        "n_out": float(sum(len(o["events"]["cross"]["out"]) for o in k["orbits"])),
        "mE_in": float(sum(MP*o["events"]["E"]*len(o["events"]["cross"]["in"]) for o in k["orbits"])),
        "mE_out": float(sum(MP*o["events"]["E"]*len(o["events"]["cross"]["out"]) for o in k["orbits"]))}
    k["mE_in_relerr"] = k["sphere"]["mE_in"]/k["sphere_ref"]["mE_in"] - 1.0
    k["mE_out_relerr"] = k["sphere"]["mE_out"]/k["sphere_ref"]["mE_out"] - 1.0
    snaps = sorted(f for f in os.listdir(d) if f.startswith("npm.part."))
    last = open(os.path.join(d, snaps[-1]), "rb").read()
    n = int(np.frombuffer(last[16:24], dtype="<i8")[0])
    off = 32 + 56*n + 16*n
    k["peri_counts"] = [int(x) for x in np.frombuffer(last[off:off + 4*n], dtype="<i4")]
    k["peri_ref"] = [len(o["events"]["peri"]) for o in k["orbits"]]
    nh = np.loadtxt(os.path.join(d, "npm.newton.hst"))
    k["energy_drift_rel"] = float(np.abs((nh[:, 7] - nh[0, 7])/nh[0, 7]).max())
    res["kepler"] = k
    # ---- plummer ----
    d = os.path.join(run, "plummer")
    tr = read_traj(d, "npm")
    pl = []
    for tag, (r, n1, n2) in enumerate(((1.0, (1, 0, 0), (0, 1, 0)), (0.5, (0, 0, 1), (1, 0, 0)))):
        s = tr[tr[:, 1] == tag]
        om = (r*r + SOFT*SOFT)**-0.75
        ex = r*(np.cos(om*s[:, 0])[:, None]*np.array(n1, float) + np.sin(om*s[:, 0])[:, None]*np.array(n2, float))
        rr = np.linalg.norm(s[:, 2:5], axis=1)
        pl.append({"r": r, "omega": float(om), "radius_dev_max": float(np.abs(rr - r).max()),
                   "max_position_error": float(np.linalg.norm(s[:, 2:5] - ex, axis=1).max()),
                   "t_end": float(s[-1, 0])})
    res["plummer"] = pl
    # ---- background ----
    d = os.path.join(run, "background")
    tr = read_traj(d, "npm")
    bg = []
    for tag, (r0, pw) in enumerate(((0.5, 2.0/3.0), (0.4, 2.0/3.0), (0.8, 1.0/3.0), (0.6, 1.0/3.0))):
        s = tr[tr[:, 1] == tag]
        rr = np.linalg.norm(s[:, 2:5], axis=1)
        ex = r0*(1.0 + s[:, 0])**pw
        bg.append({"r0": r0, "power": pw, "t_end": float(s[-1, 0]), "r_end": float(rr[-1]),
                   "r_end_exact": float(ex[-1]), "max_relerr": float(np.abs(rr/ex - 1.0).max())})
    res["background"] = bg
    # ---- expanding box ----
    for name, phys in (("expand", False), ("expand_phys", True)):
        d = os.path.join(run, name)
        tr = read_traj(d, "npmp")
        x0 = np.array([[0.6, 0.0, 0.0], [0.0, 0.0, -0.4]])
        p0 = np.array([[0.0, 0.9, 0.0], [1.0, 0.3, 0.0]])
        ob = []
        for tag in range(2):
            s = tr[tr[:, 1] == tag]
            sol = expand_reference(x0[tag], p0[tag], s[-1, 0], phys)
            ex = sol(s[:, 0])[:3].T
            # the code keeps positions inside the periodic box [-2, 2): compare modulo 4
            dx = s[:, 2:5] - ex
            dx -= 4.0*np.round(dx/4.0)
            err = np.linalg.norm(dx, axis=1)
            ob.append({"t_end": float(s[-1, 0]), "max_position_error": float(err.max()),
                       "r_min": float(np.linalg.norm(ex, axis=1).min()),
                       "r_max": float(np.linalg.norm(ex, axis=1).max())})
        nh = np.loadtxt(os.path.join(d, "npmp.newton.hst"))
        scale = np.abs(nh[:, 2]*nh[:, 5]).max()        # a |W|
        res[name] = {"orbits": ob, "a_end": float(nh[-1, 2]),
                     "C_drift_over_aW": float(np.abs(nh[:, 7] - nh[0, 7]).max()/scale),
                     "aK_plus_aW_change_over_aW": float(
                         np.abs((nh[:, 2]*(nh[:, 4] + nh[:, 5]))[-1]
                                - (nh[:, 2]*(nh[:, 4] + nh[:, 5]))[0])/scale)}
    return res


def figure(run, res, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.17, top=0.95, wspace=0.36)
    tr = read_traj(os.path.join(run, "kepler"), "npm")
    for tag, (a, e, n1, n2) in enumerate(KEPLER):
        s = tr[tr[:, 1] == tag]
        ex = kepler_state(a, e, n1, n2, s[:, 0])
        ax[0].semilogy(s[1:, 0], np.linalg.norm(s[1:, 2:5] - ex[1:], axis=1), color=fs.SERIES[tag],
                       label=f"Kepler, a = {a}, e = {e}")
    tr = read_traj(os.path.join(run, "plummer"), "npm")
    for tag, (r, n1, n2) in enumerate(((1.0, (1, 0, 0), (0, 1, 0)), (0.5, (0, 0, 1), (1, 0, 0)))):
        s = tr[tr[:, 1] == tag]
        om = (r*r + SOFT*SOFT)**-0.75
        ex = r*(np.cos(om*s[:, 0])[:, None]*np.array(n1, float) + np.sin(om*s[:, 0])[:, None]*np.array(n2, float))
        ax[0].semilogy(s[1:, 0], np.linalg.norm(s[1:, 2:5] - ex[1:], axis=1), color=fs.SERIES[2 + tag],
                       ls="--", label=f"softened, circular, r = {r}")
    ax[0].set_xlabel("time")
    ax[0].set_ylabel("distance to the exact orbit")
    ax[0].set_ylim(1e-10, 1e-1)
    ax[0].legend(loc="upper left", fontsize=7)
    tr = read_traj(os.path.join(run, "background"), "npm")
    for tag, (r0, pw) in enumerate(((0.5, 2.0/3.0), (0.4, 2.0/3.0), (0.8, 1.0/3.0), (0.6, 1.0/3.0))):
        s = tr[tr[:, 1] == tag]
        rr = np.linalg.norm(s[:, 2:5], axis=1)
        ax[1].plot(1.0 + s[:, 0], rr/r0, color=fs.SERIES[tag], label=f"r0 = {r0}")
    tt = np.linspace(1.0, 4.0, 50)
    ax[1].plot(tt, tt**(2.0/3.0), **fs.GUIDE)
    ax[1].plot(tt, tt**(1.0/3.0), **fs.GUIDE)
    ax[1].text(2.6, 2.05, r"$t^{2/3}$", fontsize=9)
    ax[1].text(3.0, 1.30, r"$t^{1/3}$", fontsize=9)
    ax[1].set_xlabel(r"$t_0 + t$")
    ax[1].set_ylabel(r"$r/r_0$ (background term)")
    ax[1].legend(loc="upper left", fontsize=7, ncol=2)
    for name, phys, ls in (("expand", False, "-"), ("expand_phys", True, "--")):
        tr = read_traj(os.path.join(run, name), "npmp")
        x0 = np.array([[0.6, 0.0, 0.0], [0.0, 0.0, -0.4]])
        p0 = np.array([[0.0, 0.9, 0.0], [1.0, 0.3, 0.0]])
        for tag in range(2):
            s = tr[tr[:, 1] == tag]
            sol = expand_reference(x0[tag], p0[tag], s[-1, 0], phys)
            ex = sol(s[:, 0])[:3].T
            dx = s[:, 2:5] - ex
            dx -= 4.0*np.round(dx/4.0)
            ax[2].semilogy(s[1:, 0], np.linalg.norm(dx[1:], axis=1), color=fs.SERIES[tag], ls=ls,
                           label=f"orbit {tag + 1}, s {'physical' if phys else 'comoving'}")
    ax[2].set_xlabel("conformal time")
    ax[2].set_ylabel("distance to the ODE solution")
    ax[2].set_ylim(1e-10, 1e-1)
    ax[2].legend(loc="upper left", fontsize=7)
    fs.save(fig, out + "_newton")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe")
    ap.add_argument("--fig")
    ap.add_argument("--replot")
    args = ap.parse_args()
    run = args.replot or os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("NRPIC_RUN_DIR is not set (start through runreg.py)")
    if not args.replot:
        cases = make_cases(run)
        procs = []
        for name, c in cases.items():
            log = open(os.path.join(c["dir"], "athena.log"), "w")
            procs.append((name, subprocess.Popen([args.exe, "-i", c["inp"], "-d", c["dir"]] + c["args"],
                                                 cwd=c["dir"], stdout=log, stderr=subprocess.STDOUT)))
        for name, p in procs:
            print(name, "exit", p.wait(), flush=True)
    res = judge(run)
    with open(os.path.join(run, "t4_newton.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    k = res["kepler"]
    for o in k["orbits"]:
        print("kepler orbit", o["a"], o["e"], "max position error", o["max_position_error"],
              "peri ref", [round(x, 3) for x in o["events"]["peri"]])
    print("kepler sphere", k["sphere"], "ref", k["sphere_ref"], "relerr", k["mE_in_relerr"], k["mE_out_relerr"])
    print("kepler pericentre counts", k["peri_counts"], "ref", k["peri_ref"], "energy drift", k["energy_drift_rel"])
    for o in res["plummer"]:
        print("plummer", o)
    for o in res["background"]:
        print("background", o)
    for name in ("expand", "expand_phys"):
        print(name, res[name])
    if args.fig:
        figure(run, res, args.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
