#!/usr/bin/env python3
"""G0 scoping estimates for Track D (black-hole growth and dark-matter dress, S4).

Semi-analytic reference only (decision 0010: nothing here simulates; it sets parameter
ranges and the compute estimate of AthenaK runs).

Part A  Cold radial shells around a point mass M in an Einstein-de Sitter background
        (Newtonian, G = c = M = 1), started at t_i = 2/(3 eps) with the unperturbed Hubble
        velocity, eps = H_i M. Before turnaround no shells cross, so each shell is a
        radial Kepler orbit with the mass it encloses (M plus the background mass M_b
        inside its initial radius). Turnaround computed in closed form and by integrating
        r'' = -(M + M_b)/r^2; the mass that has turned around, the turnaround radius and
        the frozen-in density (background density at the turnaround time) follow.
Part B  Einstein-Straus scales: radius of the vacuum bubble that holds the mass M, its
        expansion speed, the Hubble radius, the run length per factor in a.
Part C  Cost model of AthenaK runs from measured throughput (run logs named in INPUTS),
        checked against the block-cycle record of a production run.

Usage: python3 scoping_estimates.py --out <output dir>
Writes <out>/scoping.json, <out>/scoping_table.txt, <out>/scoping.{pdf,png}.
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # worktree root
RUNS = "/data/haiyangw/nrpic/runs"                             # main checkout, read-only

# measured anchors (read from these files at run time; see INPUTS in the JSON)
HCAL = {"M/4": f"{RUNS}/puncture/hcal/dx4/athena.log",
        "M/8": f"{RUNS}/puncture/hcal/dx8_tight/athena.log",
        "M/16": f"{RUNS}/puncture/hcal/dx16/athena.log"}
JEANS_SEGS = f"{RUNS}/jeans/n1e4_v19/chain/seg*.a1.log"
COSMO_PCS = f"{RUNS}/cosmo/east_d0.01_n64_pcs/athena.20261114-012440.log"
CFL = 0.25            # <time> cfl_number of the puncture inputs (hcal/dx16/horizon_calib.athinput)
Z4C_UNIFORM = 2.0e7   # zone-cycles/s, uniform 128^3, nghost 4, one A100 (docs/TESTLOG.md:46)
EPS = [0.003, 0.01, 0.03, 0.1]


def load_figstyle():
    path = os.path.join(ROOT, "python", "nrpic", "figstyle.py")
    spec = importlib.util.spec_from_file_location("figstyle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- Part A: shells
def shell_closed_form(mu, eps):
    """Turnaround of the shell enclosing background mass mu*M (closed form)."""
    t_i = 2.0 / (3.0 * eps)
    r_i = (2.0 * mu / eps**2) ** (1.0 / 3.0)
    mtot = 1.0 + mu
    energy = 0.5 * eps**2 * r_i**2 - mtot / r_i          # = -1/r_i analytically
    r_max = mtot / (-energy)
    cos_eta_i = 1.0 - 2.0 * r_i / r_max
    eta_i = np.arccos(np.clip(cos_eta_i, -1.0, 1.0))
    tscale = np.sqrt(r_max**3 / (8.0 * mtot))
    t_ta = t_i + tscale * (np.pi - (eta_i - np.sin(eta_i)))
    return dict(r_i=r_i, energy=energy, r_max=r_max, t_ta=t_ta, t_i=t_i)


def shell_ode(mu, eps):
    """Same turnaround by integrating r'' = -(1+mu)/r^2 from the Hubble flow."""
    t_i = 2.0 / (3.0 * eps)
    r_i = (2.0 * mu / eps**2) ** (1.0 / 3.0)
    mtot = 1.0 + mu

    def rhs(t, y):
        return [y[1], -mtot / y[0] ** 2]

    def turn(t, y):
        return y[1]
    turn.terminal = True
    turn.direction = -1
    cf = shell_closed_form(mu, eps)
    t_end = t_i + 4.0 * (cf["t_ta"] - t_i) + 10.0
    sol = solve_ivp(rhs, (t_i, t_end), [r_i, eps * r_i], method="DOP853",
                    rtol=1e-13, atol=1e-14 * r_i, events=turn)
    t_ta = sol.t_events[0][0]
    r_max = sol.y_events[0][0][0]
    return dict(t_ta=t_ta, r_max=r_max)


def part_a():
    out = {}
    for eps in EPS:
        mu = np.logspace(-3, 5, 400)
        cf = [shell_closed_form(m, eps) for m in mu]
        t_ta = np.array([c["t_ta"] for c in cf])
        r_max = np.array([c["r_max"] for c in cf])
        r_i = np.array([c["r_i"] for c in cf])
        energy = np.array([c["energy"] for c in cf])
        t_i = cf[0]["t_i"]
        # check of prediction 2: E = -M/r_i
        e_err = np.max(np.abs(energy * r_i + 1.0))
        rmax_err = np.max(np.abs(r_max / (r_i * (1.0 + mu)) - 1.0))
        # check of prediction 1: ODE against closed form on every 20th shell
        idx = np.arange(0, mu.size, 20)
        ode = [shell_ode(mu[k], eps) for k in idx]
        dt_rel = np.array([o["t_ta"] / t_ta[k] - 1.0 for o, k in zip(ode, idx)])
        dr_rel = np.array([o["r_max"] / r_max[k] - 1.0 for o, k in zip(ode, idx)])
        a_rel = (t_ta / t_i) ** (2.0 / 3.0)               # a(t_ta)/a_i
        coef = mu / a_rel                                  # M_b,ta / (M a/a_i)
        rho_ta = 1.0 / (6.0 * np.pi * t_ta**2)            # EdS background density at t_ta
        rho_i = 1.0 / (6.0 * np.pi * t_i**2)
        sl_r = np.gradient(np.log(r_max), np.log(a_rel))  # d ln r_ta / d ln a
        sl_rho = np.gradient(np.log(rho_ta), np.log(r_max))
        out[eps] = dict(mu=mu, t_ta=t_ta, r_ta=r_max, a=a_rel, coef=coef, rho=rho_ta / rho_i,
                        sl_r=sl_r, sl_rho=sl_rho, t_i=t_i, e_err=e_err, rmax_err=rmax_err,
                        ode_dt_max=float(np.max(np.abs(dt_rel))),
                        ode_dr_max=float(np.max(np.abs(dr_rel))),
                        ode_a=a_rel[idx], ode_coef=mu[idx] / ((t_ta[idx] * (1 + dt_rel) / t_i) ** (2 / 3)))
    return out


def at_a(d, key, a_target):
    return float(np.interp(np.log(a_target), np.log(d["a"]), d[key]))


# ---------------------------------------------------------------- Part B: scales
def part_b():
    rows = []
    for eps in EPS:
        t_i = 2.0 / (3.0 * eps)
        r_w = (2.0 / eps**2) ** (1.0 / 3.0)      # bubble with removed dust mass = M
        for af in (2.0, 4.0, 10.0):
            T = t_i * (af**1.5 - 1.0)
            rows.append(dict(eps=eps, af=af, t_i=t_i, T=T, R_w_i=r_w, R_w_f=r_w * af,
                             v_wall_i=eps * r_w, hubble_i=1.0 / eps,
                             hubble_f=(1.0 / eps) * af**1.5,
                             rho_i_M2=3.0 * eps**2 / (8.0 * np.pi),
                             k_apparent_mcvittie_i=-12.0 * eps**2,
                             dlnM_def=4.0 * eps**2 * (1.0 - af**-3)))
    return rows


# ---------------------------------------------------------------- Part C: cost
def parse_log(path):
    txt = open(path).read()
    bc = re.findall(r"MeshBlock-cycles\s*=\s*([0-9.eE+]+)", txt)
    ct = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
    zc = re.findall(r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)", txt)
    tl = re.findall(r"tlim=([0-9.eE+-]+)", txt)
    nb = re.findall(r"Total number of MeshBlocks\s*=\s*([0-9]+)", txt)
    return dict(block_cycles=float(bc[-1]) if bc else None, wall=float(ct[-1]) if ct else None,
                zc=float(zc[-1]) if zc else None, tlim=float(tl[-1]) if tl else None,
                nblocks=int(nb[0]) if nb else None)


def part_c():
    inputs = {}
    anchors = {}
    for k, p in HCAL.items():
        d = parse_log(p)
        inputs[p] = sha256(p)
        dxmin = {"M/4": 0.25, "M/8": 0.125, "M/16": 0.0625}[k]
        cyc_per_M = 1.0 / (CFL * dxmin)
        d["blocks_mean"] = d["block_cycles"] / (d["tlim"] * cyc_per_M)
        d["s_per_M"] = d["wall"] / d["tlim"]
        anchors[k] = d
    rz_smr = float(np.mean([anchors[k]["zc"] for k in anchors]))
    # production run with matter, AMR, three horizons: block-cycles and wall of every segment
    segs = sorted(glob.glob(JEANS_SEGS))
    bc = wall = 0.0
    for p in segs:
        d = parse_log(p)
        inputs[p] = sha256(p)
        if d["block_cycles"] and d["wall"]:
            bc += d["block_cycles"]
            wall += d["wall"]
    rz_amr = bc * 4096.0 / wall
    # particle cost per particle-cycle from the periodic run (64^3 cells, 64^3 particles, PCS)
    dc = parse_log(COSMO_PCS)
    inputs[COSMO_PCS] = sha256(COSMO_PCS)
    ncell = 64**3
    per_cycle = ncell / dc["zc"]
    c_p = (per_cycle - ncell / Z4C_UNIFORM) / ncell        # upper estimate (see SCOPE.md)

    # block count of the puncture nest, from the anchors: 288 (M/4) + 56 per halving
    def nest_blocks(dxmin):
        return 288.0 + 56.0 * math.log2(0.25 / dxmin)

    def cost(T, dxmin, ball_half=0.0, dx_ball=1.0, npart=0.0, rz=rz_smr):
        """Card-seconds: one global time step (no subcycling), set by dxmin.
        Puncture nest as in the anchors (root 4 M cells on +-128 M, 64 root blocks); a
        region of cells dx_ball over the cube +-ball_half; the domain grown to +-L with
        L = max(128 M, 1.25 ball_half, 0.71 T) so that the outer boundary stays out of
        causal contact with the centre for gauge modes at sqrt(2) c (docs/TESTLOG.md:
        2098-2100), by one coarser root level (one more shell of 56 blocks) per doubling."""
        cyc = T / (CFL * dxmin)
        nb = nest_blocks(dxmin)
        L = max(128.0, 1.25 * ball_half, 0.71 * T)
        nb += 56.0 * math.ceil(max(0.0, math.log2(L / 128.0)))
        if ball_half > 0.0:
            nb += max(0.0, (2.0 * ball_half / (16.0 * dx_ball)) ** 3 - 64.0)
        wall = nb * 4096.0 * cyc / rz + npart * cyc * c_p
        return dict(T=T, dxmin=dxmin, blocks=nb, cycles=cyc, wall_s=wall, card_h=wall / 3600.0,
                    npart=npart, ball_half=ball_half, dx_ball=dx_ball, L=L)

    # model check: predict the production run's wall from its own block-cycles with rz_smr
    check = dict(measured_wall_s=wall, predicted_wall_s_with_rz_smr=bc * 4096.0 / rz_smr,
                 block_cycles=bc, segments=len(segs))
    configs = []
    for dx in (0.125, 0.0625, 0.03125):                   # D-pre-4: vacuum puncture
        for T in (500.0, 1000.0):
            c = cost(T, dx)
            c["name"] = f"D-pre-4 vacuum puncture dx=M/{int(round(1 / dx))} T={int(T)}M"
            configs.append(c)
    # G2: Einstein-Straus bubble with a thick comoving dust shell R_w < R < 1.5 R_w
    # (marginally bound dust shells evolve independently, so the shell need not be thicker)
    for eps in (0.01, 0.03, 0.1):
        r_w = (2.0 / eps**2) ** (1.0 / 3.0)
        rb_i = 1.5 * r_w
        for af in (2.0, 4.0):
            T = (2.0 / (3.0 * eps)) * (af**1.5 - 1.0)
            half = 1.25 * rb_i * af
            for dx in (0.0625, 0.03125, 0.015625):
                for dxb in (1.0, 2.0):
                    npart = 1e6
                    c = cost(T, dx, ball_half=half, dx_ball=dxb, npart=npart, rz=rz_amr)
                    c["name"] = (f"G2 bubble eps={eps} a_f/a_i={af:g} dx=M/{int(round(1 / dx))} "
                                 f"dx_ball={dxb:g}M N={npart:.0e} R_w,i={r_w:.1f}M R_b,i={rb_i:.0f}M "
                                 f"H_i R_b,i={eps * rb_i:.2f}")
                    c["eps"], c["af"], c["R_b_i"], c["R_w_i"] = eps, af, rb_i, r_w
                    configs.append(c)
    return dict(anchors=anchors, rz_smr=rz_smr, rz_amr=rz_amr, c_p=c_p, check=check,
                configs=configs, inputs=inputs, cost=cost)


# ---------------------------------------------------------------- figure
def figure(A, B, C, outbase):
    fs, fs_path = load_figstyle()
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28, hspace=0.30)
    cols = fs.series_colors(len(EPS))
    # top left: coefficient of the turned-around mass
    ax = axs[0, 0]
    lss = ["-", "--", "-.", ":"]
    for c, ls, eps in zip(cols, lss, EPS):
        d = A[eps]
        ax.plot(d["a"], d["coef"], color=c, ls=ls, label=rf"$\epsilon={eps:g}$")
        ax.plot(d["ode_a"], d["ode_coef"], "o", ms=3, mfc="none", color=c)
    ax.axhline((4.0 / (3.0 * np.pi)) ** (2.0 / 3.0), **fs.GUIDE)
    ax.text(1.3, 0.62, r"$(4/3\pi)^{2/3}=0.5648$", fontsize=8)
    ax.text(1.3, 0.73, "lines: closed form; circles: integrated orbits\n"
            r"(the four $\epsilon$ coincide in these units)", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(1.0, 1e4)
    ax.set_ylim(0.0, 0.8)
    ax.set_xlabel(r"$a(t_{\rm ta})/a_i$")
    ax.set_ylabel(r"$M_{b,\rm ta}\,/\,[M\,a/a_i]$")
    ax.legend(loc="lower right", ncol=2)
    # top right: turnaround radius, bubble wall, Hubble radius
    ax = axs[0, 1]
    ag = np.logspace(0, 2, 50)
    for c, eps in zip(cols, EPS):
        d = A[eps]
        ax.plot(d["a"], d["r_ta"], color=c)
        r_w = (2.0 / eps**2) ** (1.0 / 3.0)
        ax.plot(ag, r_w * ag, color=c, ls="--", lw=1.0)
        ax.plot(ag, ag**1.5 / eps, color=c, ls=":", lw=1.0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0, 100.0)
    ax.set_ylim(1.0, 1e6)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"radius $/M$")
    ax.text(0.04, 0.92, r"solid $r_{\rm ta}$, dashed bubble wall, dotted $1/H$",
            transform=ax.transAxes, fontsize=8)
    # bottom left: frozen-in density against the turnaround radius
    ax = axs[1, 0]
    for c, eps in zip(cols, EPS):
        d = A[eps]
        ax.plot(d["r_ta"], d["rho"], color=c, label=rf"$\epsilon={eps:g}$")
    rr = np.logspace(1.5, 4, 10)
    ax.plot(rr, 30.0 * (rr / 10**1.5) ** (-2.25), **fs.GUIDE)
    ax.text(2e2, 3.0, r"$\propto r^{-9/4}$", fontsize=9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1.0, 1e4)
    ax.set_ylim(1e-7, 1e2)
    ax.legend(loc="lower left", ncol=2, fontsize=8)
    ax.set_xlabel(r"$r_{\rm ta}/M$")
    ax.set_ylabel(r"$\rho_b(t_{\rm ta})/\rho_b(t_i)$")
    # bottom right: card-hours against run length
    ax = axs[1, 1]
    T = np.logspace(1.5, 3.3, 40)
    cost = C["cost"]
    for ls, dx in zip(["-", "--", ":"], (0.125, 0.0625, 0.03125)):
        ax.plot(T, [cost(t, dx)["card_h"] for t in T], color="k", ls=ls, lw=1.0,
                label=rf"vacuum, $\Delta x_{{\min}}=M/{int(round(1 / dx))}$")
    mks = {0.0625: "s", 0.03125: "^", 0.015625: "D"}
    ecol = dict(zip(EPS, cols))
    for cfg in C["configs"]:
        if cfg["name"].startswith("G2"):
            ax.plot(cfg["T"], cfg["card_h"], mks[cfg["dxmin"]], color=ecol[cfg["eps"]], ms=4.5,
                    mfc=(ecol[cfg["eps"]] if cfg["dx_ball"] == 2.0 else "none"))
    ax.axhline(30.0, **fs.MASK_LINE)
    ax.text(12, 36, "allotment to the next gate (decision 0006)", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(8.0, 2500.0)
    ax.set_ylim(0.03, 3000.0)
    ax.set_xlabel(r"evolution time $T/M$")
    ax.set_ylabel("card-hours (estimate)")
    ax.legend(loc="lower right", fontsize=8)
    ax.text(0.03, 0.72, "markers: bubble + dust shell + $10^6$ particles,\n"
            r"$a_f/a_i=2$ and 4; square $M/16$, triangle $M/32$, diamond $M/64$;"
            "\n" r"colours: $\epsilon$ as in the other panels;" "\n"
            r"open $\Delta x_{\rm ball}=M$, filled $2M$",
            transform=ax.transAxes, fontsize=7)
    return fs.save(fig, outbase), fs_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    A = part_a()
    B = part_b()
    C = part_c()
    files, fs_path = figure(A, B, C, os.path.join(args.out, "scoping"))
    res = {"part_a": {}, "part_b": B, "part_c": {k: v for k, v in C.items() if k != "cost"}}
    for eps, d in A.items():
        res["part_a"][str(eps)] = dict(
            energy_identity_max_err=float(d["e_err"]), rmax_identity_max_err=float(d["rmax_err"]),
            ode_vs_closed_t_ta_max_rel=d["ode_dt_max"], ode_vs_closed_r_max_max_rel=d["ode_dr_max"],
            coef_at_a2=at_a(d, "coef", 2.0), coef_at_a10=at_a(d, "coef", 10.0),
            coef_at_a100=at_a(d, "coef", 100.0), coef_at_a1000=at_a(d, "coef", 1000.0),
            a_where_coef_within_1pc=float(d["a"][np.argmax(
                np.abs(d["coef"] / (4.0 / (3.0 * np.pi)) ** (2.0 / 3.0) - 1.0) < 0.01)]),
            slope_r_at_a100=at_a(d, "sl_r", 100.0), slope_r_at_a1000=at_a(d, "sl_r", 1000.0),
            slope_rho_at_a100=at_a(d, "sl_rho", 100.0), slope_rho_at_a1000=at_a(d, "sl_rho", 1000.0),
            M_ta_over_M_at_a2=1.0 + at_a(d, "coef", 2.0) * 2.0,
            M_ta_over_M_at_a4=1.0 + at_a(d, "coef", 4.0) * 4.0,
            r_ta_at_a2=float(np.exp(np.interp(np.log(2.0), np.log(d["a"]), np.log(d["r_ta"])))),
            r_ta_at_a4=float(np.exp(np.interp(np.log(4.0), np.log(d["a"]), np.log(d["r_ta"])))))
    res["inputs_sha256"] = C["inputs"]
    res["inputs_sha256"][fs_path] = sha256(fs_path)
    res["inputs_sha256"][os.path.abspath(__file__)] = sha256(os.path.abspath(__file__))
    res["figure_files"] = files
    with open(os.path.join(args.out, "scoping.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    with open(os.path.join(args.out, "scoping_table.txt"), "w") as f:
        f.write("# Part A (per eps)\n")
        for eps, d in res["part_a"].items():
            f.write(f"eps={eps} " + " ".join(f"{k}={v:.6g}" for k, v in d.items()) + "\n")
        f.write("# Part B\n")
        for r in B:
            f.write(" ".join(f"{k}={v:.4g}" for k, v in r.items()) + "\n")
        f.write("# Part C anchors\n")
        for k, v in C["anchors"].items():
            f.write(f"{k} " + " ".join(f"{a}={b}" for a, b in v.items()) + "\n")
        f.write(f"rz_smr={C['rz_smr']:.4g} rz_amr={C['rz_amr']:.4g} c_p={C['c_p']:.4g}\n")
        f.write("check " + " ".join(f"{a}={b:.6g}" for a, b in C["check"].items()) + "\n")
        for cfg in C["configs"]:
            f.write(f"{cfg['name']}: blocks={cfg['blocks']:.0f} cycles={cfg['cycles']:.0f} "
                    f"card_h={cfg['card_h']:.2f}\n")
    print(open(os.path.join(args.out, "scoping_table.txt")).read())


if __name__ == "__main__":
    sys.exit(main())
