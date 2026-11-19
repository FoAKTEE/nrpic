#!/usr/bin/env python3
"""Isobaric-mode runs of T7 and T8 (heat package).

    run_mode.py local  --theta TH --kl KL [KL ...] --eps E --seeds S [S ...] --n N
                       [--dt-frac 0.1] [--pmax 0.1] [--dx-frac 0.25] [--nsnap 24]
                       [--tend 2.0] [--sigma-scale 1] [--nproc P] [--tag NAME]
    run_mode.py prep   (same options) --list FILE [--exe-gpu]
    run_mode.py reduce BATCHDIR --prep PREPDIR [--nproc P]

lambda = 1 (rest-mass density 1, sigma/m = 1), box of one wavelength Lx = 2 pi/k along x,
nx = 2^ceil(log2(Lx/(dx_frac lambda))) cells (dx <= dx_frac lambda); transverse
Ly = Lz = n_t dx with n_t in {4, 8, 16} chosen for about 100 particles per cell;
dt = dt_frac t_coll (t_coll = 1/(rho0 sigma <v_Mol>(theta))); run to tend/Gamma_1
(Gamma_1 = kappa_1 k^2/(n c_p), the first Chapman-Enskog rate), nsnap snapshots after
t = 0. `local` makes the particle files and runs the processor executable in parallel,
reducing every snapshot to Fourier sums (heatlib.mode_fun) while the run goes on.
`prep` makes the particle files and writes a list for `nrpic-run submit --launcher batch`
(card); `reduce` reduces the snapshots of a finished batch run afterwards.
kl = 100 runs the collisionless check (sigma = k/100, mean free path 100/k).
Each case directory gets case.json (all parameters) and reduced.npz.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import conduction as cd       # noqa: E402
import rate                   # noqa: E402
import snap                   # noqa: E402


def case_params(theta, kl, eps, seed, n, dt_frac, pmax, dx_frac, nsnap, tend, tag,
                nt_fixed=None, ly_fixed=None):
    lam = 1.0
    sigma = 1.0 / lam
    k = kl / lam
    collisionless_check = kl >= 50
    if collisionless_check:
        lam = 1.0 * kl                     # k lambda = kl with k = 1
        k = 1.0
        sigma = 1.0 / lam
    Lx = 2 * np.pi / k
    tc = 1.0 / (sigma * float(rate.vmol_mean(theta)))
    if collisionless_check:
        nx = 32
        nt = 4
        dxt = Lx / nx
        vth = float(np.sqrt(theta))
        t_end = 6.0 / (k * vth) if theta < 0.5 else 6.0 / k
        dt = t_end / 600
        G1 = None
    else:
        nx = int(2 ** np.ceil(np.log2(Lx / (dx_frac * lam)) - 1e-9))
        dx = Lx / nx
        nt = 4
        for cand in (4, 8, 16):
            nt = cand
            if n / (nx * cand * cand) <= 200:
                break
        dxt = dx
        if ly_fixed:                       # T8: transverse box and cells fixed
            nt, dxt = int(nt_fixed), ly_fixed / nt_fixed
        G1 = cd.mode_rate(cd.kappa_ce_nr(theta, sigma), 1.0, theta, k)
        t_end = tend / G1
        dt = dt_frac * tc
    nsteps = int(np.ceil(t_end / dt - 1e-9))
    t_end = nsteps * dt
    snap_dt = t_end / nsnap
    box = [Lx, nt * dxt, nt * dxt]
    name = (f"{tag}th{theta:g}_kl{kl:g}_e{eps:g}_s{seed}"
            f"_dt{dt_frac:g}_p{pmax:g}_dx{dx_frac:g}")
    return dict(name=name, theta=theta, k_lambda=kl, k=k, lam=lam, sigma=sigma, eps=eps,
                seed=seed, n=n, Lx=Lx, box=box, nx=[nx, nt, nt], dt=dt, dt_frac=dt_frac,
                t_coll=tc, Gamma1=G1, t_end=t_end, nsteps=nsteps, snap_dt=snap_dt,
                nsnap=nsnap, pmax=pmax, dx_frac=dx_frac,
                per_cell=n / (nx * nt * nt), collisionless_check=collisionless_check)


def prepare(d, P, root):
    """Particle file in ROOT/pfiles/<key>/ (shared by cases with the same sample: n, box,
    theta, eps, sigma, seed), case.json in d; returns the command-line overrides."""
    os.makedirs(d, exist_ok=True)
    key = (f"n{P['n']}_th{P['theta']:g}_e{P['eps']:g}_s{P['seed']}_sig{P['sigma']:.6g}_"
           f"box{P['box'][0]:.6g}x{P['box'][1]:.6g}")
    pdir = os.path.join(root, "pfiles", key)
    if not os.path.exists(os.path.join(pdir, hl.BASE + ".json")):
        hl.make_box(pdir, "mode", n=P["n"], box=P["box"], theta=P["theta"], eps=P["eps"],
                    kmode=1, sigma=P["sigma"], seed=P["seed"])
    meta = json.load(open(os.path.join(pdir, hl.BASE + ".json")))
    P["make_box_meta"] = {k: meta[k] for k in ("k", "eps", "kmode", "theta", "sigma")}
    P["particle_file"] = os.path.join(pdir, hl.BASE + ".nrp")
    with open(os.path.join(d, "case.json"), "w") as fh:
        json.dump(P, fh, indent=1)
    return hl.overrides(P["box"], P["nx"], P["dt"], P["t_end"] * (1 + 1e-9),
                        P["snap_dt"] * (1 - 1e-9), P["sigma"], P["seed"], pmax=P["pmax"],
                        extra=[f"particles/particle_file={P['particle_file']}"])


def run_case(root, P, exe):
    d = os.path.join(root, P["name"])
    ovr = prepare(d, P, root)
    u0 = snap.read_nrp(P["particle_file"])["u"]
    red = hl.SnapReducer(d, hl.mode_fun(P["k"], u0=u0))
    r = hl.run_athena(d, ovr, exe=exe, reducer=red)
    summ = dict(name=P["name"], rc=r["rc"], wall=r["wall"])
    if r["rc"] == 0:
        summ["coll"] = hl.coll_summary(d)
    with open(os.path.join(d, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ), flush=True)
    return summ


def cases_from(a):
    out = []
    for kl in a.kl:
        for s in a.seeds:
            out.append(case_params(a.theta, kl, a.eps, s, a.n, a.dt_frac, a.pmax, a.dx_frac,
                                   a.nsnap, a.tend, a.tag))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["local", "prep", "reduce"])
    ap.add_argument("batchdir", nargs="?")
    ap.add_argument("--theta", type=float, default=0.003)
    ap.add_argument("--kl", type=float, nargs="+", default=[0.2])
    ap.add_argument("--eps", type=float, default=0.2)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--dt-frac", type=float, default=0.1)
    ap.add_argument("--pmax", type=float, default=0.1)
    ap.add_argument("--dx-frac", type=float, default=0.25)
    ap.add_argument("--nsnap", type=int, default=24)
    ap.add_argument("--tend", type=float, default=2.0)
    ap.add_argument("--nproc", type=int, default=1)
    ap.add_argument("--tag", default="")
    ap.add_argument("--list", default=None)
    ap.add_argument("--prep", default=None, help="reduce: the prep run directory")
    ap.add_argument("--append", action="store_true", help="prep: append to --list")
    ap.add_argument("--nt-fixed", type=int, default=None, help="T8: transverse cells")
    ap.add_argument("--ly-fixed", type=float, default=None, help="T8: transverse box")
    ap.add_argument("--variants", default=None,
                    help="JSON list of dicts overriding dt_frac/pmax/dx_frac (T8)")
    a = ap.parse_args()
    if a.cmd == "reduce":
        # BATCHDIR/<name>/ holds the snapshots of a card run; --prep PREPDIR/<name>/ the
        # case.json and the particle file written by `prep`
        names = sorted(x for x in os.listdir(a.batchdir)
                       if os.path.isdir(os.path.join(a.batchdir, x)) and
                       os.path.isfile(os.path.join(a.prep, x, "case.json")))
        def red(name):
            d = os.path.join(a.batchdir, name)
            P = json.load(open(os.path.join(a.prep, name, "case.json")))
            with open(os.path.join(d, "case.json"), "w") as fh:
                json.dump(P, fh, indent=1)
            u0 = snap.read_nrp(P["particle_file"])["u"]
            r = hl.SnapReducer(d, hl.mode_fun(P["k"], u0=u0))
            r.step(final=True)
            r.save()
            summ = dict(name=name, coll=hl.coll_summary(d))
            with open(os.path.join(d, "summary.json"), "w") as fh:
                json.dump(summ, fh, indent=1)
            return d
        with ThreadPoolExecutor(a.nproc) as ex:
            for d in ex.map(red, names):
                print("reduced", d, flush=True)
        return
    root = hl.outdir("mode")
    cases = []
    if a.variants:
        for v in json.loads(a.variants):
            for s in a.seeds:
                cases.append(case_params(a.theta, a.kl[0], a.eps, s, a.n,
                                         v.get("dt_frac", a.dt_frac), v.get("pmax", a.pmax),
                                         v.get("dx_frac", a.dx_frac), a.nsnap, a.tend, a.tag,
                                         nt_fixed=a.nt_fixed, ly_fixed=a.ly_fixed))
    else:
        cases = cases_from(a)
    if a.cmd == "prep":
        # particle files and case.json in ROOT/<name>/; list lines for the batch launcher
        lines = []
        for P in cases:
            d = os.path.join(root, P["name"])
            ovr = prepare(d, P, root)
            lines.append(" ".join([P["name"], "tracks/C-sidm/heat/inputs/heat.athinput"] + ovr))
            print("prepared", P["name"], flush=True)
        with open(os.path.join(root, "card.list"), "w") as fh:
            fh.write("\n".join(lines) + "\n")
        if a.list:
            with open(a.list, "a" if a.append else "w") as fh:
                fh.write("# card runs of the heat package; particle files and case.json in "
                         f"{root}\n" + "\n".join(lines) + "\n")
        return
    # longest first, so the pool ends together
    cases.sort(key=lambda P: -P["n"] * P["nsteps"])
    # particle files first, one after the other: cases that share a file must not write it
    # concurrently (2026-11-19: two threads wrote the same file at once and a third read it
    # half-written, "bad magic", runs C-20261119-154032-e450dfc and -162015-d97abac)
    for P in cases:
        prepare(os.path.join(root, P["name"]), P, root)
    with ThreadPoolExecutor(a.nproc) as ex:
        res = list(ex.map(lambda P: run_case(root, P, hl.EXE_CPU), cases))
    with open(os.path.join(root, "summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    bad = [r for r in res if r["rc"] != 0]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
