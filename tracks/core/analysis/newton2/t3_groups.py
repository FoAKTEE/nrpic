#!/usr/bin/env python3
"""Test T3 of work package newton2: the second-moment history of particle groups
(<basename>.newton.g<g>.hst) on Track B's exact pancake (equal-mass Zel'dovich lattice
x = q + a psi(q_x), psi = (d/k) sin(k q), a = (1 + t/2)^2).

    t3_groups.py --run RUNDIR_OF_cases.py_t3 [--card DIR_OF_chk_sin32] [--out DIR]

T3a  group 1 (all particles, reference point in the middle of the box) against the
     existing history after the parallel-axis shift.
T3b  the physical columns J, dJ/dT, d2J/dT2 against the conversion of the comoving
     columns; d3J/dT3 against the difference quotient of the d2J/dT2 column.
T3c  group 2 (the slab L/4 <= q_x < 3L/4, a tag range) against the exact solution, for
     the spectral and the seven-point symbol.
T3d  the continued run against the uninterrupted one, record by record as text.
--card: the same spectral case run on a card, compared with the processor run.
Writes DIR/t3_groups.json and DIR/t3_groups.{png,pdf}.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402

COMP = ("xx", "xy", "xz", "yy", "yz", "zz")


def read_group(path):
    d = np.atleast_2d(np.loadtxt(path))
    last = {}
    for i, c in enumerate(d[:, 1].astype(np.int64)):
        last[int(c)] = i
    d = d[[last[c] for c in sorted(last)]]
    g = dict(time=d[:, 0], ncycle=d[:, 1], a=d[:, 2], T=d[:, 3], number=d[:, 4],
             mass=d[:, 5], X=d[:, 6:9], V=d[:, 9:12], I=d[:, 12:18], dI=d[:, 18:24],
             d2I=d[:, 24:30], d3I=d[:, 30:36], time_d3I=d[:, 36], J=d[:, 37:43],
             dJ=d[:, 43:49], d2J=d[:, 49:55], d3J=d[:, 55:61], T_d3J=d[:, 61])
    return g


def records(path):
    out = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            out[int(line.split()[1])] = line.rstrip("\n")
    return out


def exact_slab(case, tags):
    x0, u0, m, _ = nio.read_nrp(os.path.join(case, "particles.nrp"))
    meta = json.load(open(os.path.join(case, "particles.json")))
    L, d = meta["L"], meta["delta"]
    k = 2.0*np.pi/L
    sel = np.zeros(len(m), dtype=bool)
    sel[tags[0]:tags[1] + 1] = True
    psi = u0[sel, 0]                     # p = psi at a = 1
    q = x0[sel, 0] - psi
    mm = m[sel]
    qc = (mm*q).sum()/mm.sum()
    pc = (mm*psi).sum()/mm.sum()
    c0 = float((mm*(q - qc)**2).sum())
    c1 = float(2.0*(mm*(q - qc)*(psi - pc)).sum())
    c2 = float((mm*(psi - pc)**2).sum())
    return dict(c0=c0, c1=c1, c2=c2, mass=float(mm.sum()), qc=float(qc), pc=float(pc),
                check_psi=float(np.abs(psi - (d/k)*np.sin(k*q)).max()))


def slab_errors(g, ex, amax):
    a = g["a"]
    c0, c1, c2 = ex["c0"], ex["c1"], ex["c2"]
    sa = np.sqrt(a)                       # da/dt
    exact = {"I": c1*a + c2*a*a, "dI": (c1 + 2.0*c2*a)*sa, "d2I": 0.5*c1 + 3.0*c2*a}
    got = {"I": g["I"][:, 0] - c0, "dI": g["dI"][:, 0], "d2I": g["d2I"][:, 0]}
    win = (a >= 1.2) & (a <= amax)
    out, curves = {}, {}
    for key in ("I", "dI", "d2I"):
        rel = np.abs(got[key] - exact[key])/np.abs(exact[key][a <= amax]).max()
        out["%s_maxerr" % key] = float(rel[win].max())
        curves[key] = rel
    a3 = nw.scale_factor(g["time_d3I"])
    ex3 = 3.0*c2*np.sqrt(a3)
    rel3 = np.abs(g["d3I"][:, 0] - ex3)/np.abs(ex3)
    w3 = (a3 >= 1.2) & (a3 <= amax) & (g["ncycle"] > 0)
    out["d3I_rms_rel"] = float(np.sqrt(np.mean(rel3[w3]**2)))
    out["d3I_mean_signed"] = float(np.mean(((g["d3I"][:, 0] - ex3)/ex3)[w3]))
    curves["d3I"] = np.where(g["ncycle"] > 0, rel3, np.nan)
    # physical: J = a^2 I(a), a = (1 + 3T/2)^(2/3), dT = a dt
    #   I(a) = c0 + c1 a + c2 a^2;  d/dT = (da/dT) d/da, da/dT = a^(-1/2)
    Iex = c0 + c1*a + c2*a*a
    Jex = a*a*Iex
    dJ = (2.0*a*Iex + a*a*(c1 + 2.0*c2*a))/sa
    #   J = c0 a^2 + c1 a^3 + c2 a^4; with a' = a^(-1/2):
    #   dJ/dT = 2 c0 a^(1/2) + 3 c1 a^(3/2) + 4 c2 a^(5/2)
    #   d2J/dT2 = c0 a^-1 + (9/2) c1 + 10 c2 a
    #   d3J/dT3 = -c0 a^(-5/2) + 10 c2 a^(-1/2)
    d2J = c0/a + 4.5*c1 + 10.0*c2*a
    aT = (1.0 + 1.5*g["T_d3J"])**(2.0/3.0)
    d3J = -c0*aT**-2.5 + 10.0*c2*aT**-0.5
    out["J_maxerr"] = float((np.abs(g["J"][:, 0] - Jex)/np.abs(Jex).max())[win].max())
    out["dJ_maxerr"] = float((np.abs(g["dJ"][:, 0] - dJ)/np.abs(dJ[a <= amax]).max())[win].max())
    out["d2J_maxerr"] = float((np.abs(g["d2J"][:, 0] - d2J)
                               / np.abs(d2J[a <= amax]).max())[win].max())
    wJ = (aT >= 1.2) & (aT <= amax) & (g["ncycle"] > 0)
    out["d3J_rms_rel"] = float(np.sqrt(np.mean((((g["d3J"][:, 0] - d3J)/d3J)[wJ])**2)))
    out["transverse_d2I_over_xx"] = float(np.abs(g["d2I"][:, 1:]).max()
                                          / np.abs(g["d2I"][:, 0]).max())
    out["centroid_shift_max"] = float(np.abs(g["X"] - g["X"][0]).max())
    return out, curves, a, a3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--card", default="")
    ap.add_argument("--n", type=int, default=32, help="particles per side of the cases")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    res = {}
    n = a.n
    tags = ((n//4)*n*n, (3*n//4)*n*n - 1)
    sp = os.path.join(a.run, "sin32_sp")
    s7 = os.path.join(a.run, "sin32_7pt")
    h = nw.read_newton_hst(os.path.join(sp, "newton.newton.hst"))
    g1 = read_group(os.path.join(sp, "newton.newton.g1.hst"))
    g2 = read_group(os.path.join(sp, "newton.newton.g2.hst"))
    amax = float(min(15.0, g1["a"].max()))

    # ---- T3a: parallel-axis shift of the existing history
    M = h["mass"]
    X = np.stack([h["X_x"], h["X_y"], h["X_z"]], axis=1)
    V = np.stack([h["P_x"], h["P_y"], h["P_z"]], axis=1)/(M*h["a"])[:, None]
    worst = {}
    for key, pre in (("I", "I"), ("dI", "dI"), ("d2I", "d2I")):
        w = 0.0
        scale = max(np.abs(g1[key]).max(), 1e-300)
        c = 0
        for i in range(3):
            for j in range(i, 3):
                col = h["%s_%s" % (pre, COMP[c])]
                if key == "I":
                    sh = col - M*X[:, i]*X[:, j]
                elif key == "dI":
                    sh = col - M*(X[:, i]*V[:, j] + V[:, i]*X[:, j])
                else:
                    sh = col - M*2.0*V[:, i]*V[:, j]       # centroid acceleration: zero
                w = max(w, float(np.abs(sh - g1[key][:, c]).max()/scale))
                c += 1
        worst[key] = w
    res["T3a"] = dict(max_rel_diff=worst, number=int(g1["number"][0]),
                      mass_rel=float(np.abs(g1["mass"] - M).max()/M[0]),
                      centroid_diff=float(np.abs(g1["X"] - X).max()))

    # ---- T3b: physical columns against the conversion of the comoving ones
    def conv(g):
        aa = g["a"]
        da = np.sqrt(aa)                 # H = 1, n = 2: da/dt = 1 + t/2
        d2a = 0.5*np.ones_like(aa)
        J = (aa*aa)[:, None]*g["I"]
        dJ = (2.0*da)[:, None]*g["I"] + aa[:, None]*g["dI"]
        d2J = (2.0*d2a/aa)[:, None]*g["I"] + (3.0*da/aa)[:, None]*g["dI"] + g["d2I"]
        return J, dJ, d2J
    tb = {}
    for name, g in (("g1", g1), ("g2", g2)):
        J, dJ, d2J = conv(g)
        q = (g["d2J"][1:] - g["d2J"][:-1])/(g["T"][1:] - g["T"][:-1])[:, None]
        consec = (g["ncycle"][1:] - g["ncycle"][:-1]) == 1
        tb[name] = dict(
            J=float(np.abs(J - g["J"]).max()/np.abs(J).max()),
            dJ=float(np.abs(dJ - g["dJ"]).max()/np.abs(dJ).max()),
            d2J=float(np.abs(d2J - g["d2J"]).max()/np.abs(d2J).max()),
            d3J_quotient=(float(np.abs(q[consec] - g["d3J"][1:][consec]).max()
                                / np.abs(g["d3J"]).max()) if consec.any() else None),
            T_cosmic=float(np.abs(g["T"] - (2.0/3.0)*((1.0 + 0.5*g["time"])**3 - 1.0)).max()),
            T_d3J_mid=(float(np.abs(g["T_d3J"][1:][consec]
                                    - 0.5*(g["T"][1:] + g["T"][:-1])[consec]).max())
                       if consec.any() else None))
    res["T3b"] = tb

    # ---- T3c: the slab against the exact solution
    ex = exact_slab(sp, tags)
    res["T3c"] = {"exact": ex, "amax": amax}
    curves = {}
    for name, case in (("spectral", sp), ("seven_point", s7)):
        g = read_group(os.path.join(case, "newton.newton.g2.hst"))
        out, cv, aa, a3 = slab_errors(g, ex, amax)
        res["T3c"][name] = out
        curves[name] = (cv, aa, a3, g)
        gall = read_group(os.path.join(case, "newton.newton.g1.hst"))
        meta = json.load(open(os.path.join(case, "particles.json")))
        c0, c1, c2 = meta["moment_coeffs"]["00"]
        # all particles: centroid at L/2, I about the centroid = (c0 - M L^2/4) + c1' a + ...
        x0, u0, m, _ = nio.read_nrp(os.path.join(case, "particles.nrp"))
        exa = exact_slab(case, (0, len(m) - 1))
        res["T3c"][name + "_all_particles"] = slab_errors(gall, exa, amax)[0]
    res["T3c"]["improvement_I"] = res["T3c"]["seven_point"]["I_maxerr"] \
        / res["T3c"]["spectral"]["I_maxerr"]
    res["T3c"]["improvement_dI"] = res["T3c"]["seven_point"]["dI_maxerr"] \
        / res["T3c"]["spectral"]["dI_maxerr"]

    # ---- T3d: continuation
    cont = os.path.join(a.run, "sin32_sp_cont")
    td = {}
    for fn in ("newton.newton.hst", "newton.newton.g1.hst", "newton.newton.g2.hst",
               "newton.nrpic.hst"):
        ra, rb = records(os.path.join(sp, fn)), records(os.path.join(cont, fn))
        diff = [c for c in sorted(rb) if ra.get(c) != rb[c]]
        td[fn] = dict(records=len(rb), first=min(rb), last=max(rb), differ=len(diff),
                      first_differing=(diff[0] if diff else None))
    res["T3d"] = td

    # ---- card
    if a.card:
        tc = {}
        for gname in ("g1", "g2"):
            gc = read_group(os.path.join(a.card, "newton.newton.%s.hst" % gname))
            gp = read_group(os.path.join(sp, "newton.newton.%s.hst" % gname))
            m = min(len(gc["time"]), len(gp["time"]))
            tc[gname] = {k: float(np.abs(gc[k][:m] - gp[k][:m]).max()
                                  / max(np.abs(gp[k][:m]).max(), 1e-300))
                         for k in ("I", "dI", "d2I", "d3I", "J", "d2J", "d3J")}
            tc[gname]["records"] = m
        res["card"] = tc

    with open(os.path.join(a.out, "t3_groups.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    # ---- figure
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.34)
    cols = {"I": fs.PAL["blue"], "dI": fs.PAL["green"], "d2I": fs.PAL["yellow"],
            "d3I": fs.PAL["red"]}
    labs = {"I": r"$I_{xx}$", "dI": r"$\dot I_{xx}$", "d2I": r"$\ddot I_{xx}$",
            "d3I": r"$\dddot I_{xx}$"}
    ax = axs[0]
    for name, ls in (("spectral", "-"), ("seven_point", "--")):
        cv, aa, a3, g = curves[name]
        for key in ("I", "dI", "d2I"):
            ax.semilogy(aa[1:], cv[key][1:], ls=ls, color=cols[key], lw=1.5 if ls == "-" else 1.0,
                        label=labs[key] if ls == "-" else None)
        ax.semilogy(a3[1:], cv["d3I"][1:], ls=ls, color=cols["d3I"],
                    lw=1.5 if ls == "-" else 1.0, label=labs["d3I"] if ls == "-" else None)
    ax.set_xlabel(r"$a$", labelpad=-1)
    ax.set_ylabel("slab: error against Zel'dovich")
    ax.set_ylim(1e-7, 1.0)
    ax.legend(loc="lower right", fontsize=8, ncol=2)
    ax.text(0.04, 0.93, "solid: spectral; dashed: seven_point", transform=ax.transAxes,
            fontsize=7)
    ax = axs[1]
    cv, aa, a3, g = curves["spectral"]
    c0, c2 = ex["c0"], ex["c2"]
    aT = (1.0 + 1.5*g["T_d3J"])**(2.0/3.0)
    ok = g["ncycle"] > 0
    ax.plot(aT[ok], 1e3*g["d3J"][ok, 0], color=fs.PAL["red"], label="code, slab")
    ag = np.linspace(1.02, aa.max(), 300)
    ax.plot(ag, 1e3*(-c0*ag**-2.5 + 10.0*c2*ag**-0.5), color=fs.PAL["blue"], ls="--",
            label="Zel'dovich")
    ax.set_xlabel(r"$a$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,d^3J_{xx}/dT^3$")
    ax.legend(loc="lower right", fontsize=8)
    ax = axs[2]
    J, dJ, d2J = conv(g1)
    floor = 1e-18
    ax.semilogy(g1["a"], np.maximum(np.abs(d2J[:, 0] - g1["d2J"][:, 0])
                                    / np.abs(d2J[:, 0]).max(), floor),
                color=fs.PAL["green"], label=r"$d^2J/dT^2$: column $-$ conversion")
    hx = h["d2I_xx"] - 0.0
    ax.semilogy(g1["a"], np.maximum(np.abs(g1["d2I"][:, 0] - hx)/np.abs(hx).max(), floor),
                color=fs.PAL["red"], label=r"$\ddot I_{xx}$: group 1 $-$ history")
    ax.set_xlabel(r"$a$", labelpad=-1)
    ax.set_ylabel("relative difference")
    ax.set_ylim(1e-18, 1e-9)
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "t3_groups"))


if __name__ == "__main__":
    main()
