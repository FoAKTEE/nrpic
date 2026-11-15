#!/usr/bin/env python3
"""Test T3 of work package dfix: accretion diagnostics against exact geodesics.

    runreg.py --purpose "..." --cores 3 -- python3 tracks/core/analysis/dfix/t3_accretion.py \
        --exe <athena> [--fig PREFIX] [--card]
    t3_accretion.py --replot RUN --fig PREFIX

Set-up (problems/tests/accretion_static.athinput): Schwarzschild, M = 1, Cartesian
Kerr-Schild coordinates.  Particle file written here:
  species 0, 1, 2   64 particles each at rest at r0 = 6, 8, 11 (Fibonacci sphere), mass
                    1e-3 each: radial infall, E = (1 - 2/r0)^(1/2)
  species 3, 4      4 particles each on bound orbits (p, e) = (10, 0.3) and (9, 0.2),
                    started at the apocentre in four different planes, mass 1e-3
Cases, each in $NRPIC_RUN_DIR/<name>/:
  mesh      metric on the mesh (dx = 0.25 M), 800 M
  mesh_rs   the same, stopped at the cycle limit 8000 (t = 400 M) and continued
  analytic  particles/metric=kerr_schild (the analytic metric)
References (this file): radial infall and bound orbits integrated in closed form or by
quadrature in Schwarzschild coordinates and mapped to the Kerr-Schild time
t_KS = t_S + 2 ln(r/2 - 1).
Writes t3_accretion.json into the run directory and PREFIX_*.png.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import io as nio   # noqa: E402

INPUT = os.path.join(REPO, "problems", "tests", "accretion_static.athinput")
R0 = (6.0, 8.0, 11.0)
NSHELL = 64
ORBITS = ((10.0, 0.3), (9.0, 0.2))
MP = 1.0e-3
ALPHA_EXC = 0.62
SPHERES = (4.0, 10.0)
TEND = 800.0
DT = 0.05


def fibonacci_sphere(n):
    k = np.arange(n) + 0.5
    ct = 1.0 - 2.0*k/n
    st = np.sqrt(1.0 - ct*ct)
    ph = np.pi*(1.0 + 5.0**0.5)*k
    return np.stack([st*np.cos(ph), st*np.sin(ph), ct], axis=1)


def orbit_EL(p, e):
    E = np.sqrt(((p - 2.0)**2 - 4.0*e*e)/(p*(p - 3.0 - e*e)))
    L = p/np.sqrt(p - 3.0 - e*e)
    return E, L


def make_particles(path):
    xs, us, ms, sp = [], [], [], []
    for k, r0 in enumerate(R0):
        n = fibonacci_sphere(NSHELL)
        E = np.sqrt(1.0 - 2.0/r0)
        ur = 2.0*E/(r0 - 2.0)          # covariant Kerr-Schild radial component at rest
        xs.append(r0*n)
        us.append(ur*n)
        ms.append(np.full(NSHELL, MP))
        sp.append(np.full(NSHELL, k))
    planes = [((1, 0, 0), (0, 1, 0)), ((0, 1, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0)),
              ((0.6, 0.8, 0.0), (0.0, 0.0, -1.0))]
    for k, (p, e) in enumerate(ORBITS):
        E, L = orbit_EL(p, e)
        ra = p/(1.0 - e)
        for n1, n2 in planes:
            n1, n2 = np.array(n1, float), np.array(n2, float)
            xs.append((ra*n1)[None, :])
            us.append(((2.0*E/(ra - 2.0))*n1 + (L/ra)*n2)[None, :])
            ms.append(np.array([MP]))
            sp.append(np.array([3 + k]))
    x, u = np.concatenate(xs), np.concatenate(us)
    m, s = np.concatenate(ms), np.concatenate(sp)
    nio.write_nrp(path, x, u, m, s)
    return len(m)


# ---- references ----

def infall_time(r0, R):
    """Kerr-Schild coordinate time for dust released at rest at r0 to reach R"""
    E = np.sqrt(1.0 - 2.0/r0)

    def f(w):                      # r = r0 - w^2
        r = r0 - w*w
        q = np.sqrt(2.0/(r*r0))    # s = w q
        s = w*q
        return 2.0*w + 2.0/(q*(E + s))
    return quad(f, 0.0, np.sqrt(r0 - R), epsabs=1e-12, epsrel=1e-12)[0]


def orbit_events(p, e, tend):
    """Kerr-Schild times of the pericentre passages and of the crossings of each sphere
    (inwards, outwards) of the bound orbit started at its apocentre at t = 0"""
    def dtdchi(chi):
        c = np.cos(chi)
        return (p*p/((p - 2.0 - 2.0*e*c)*(1.0 + e*c)**2)
                * np.sqrt(((p - 2.0)**2 - 4.0*e*e)/(p - 6.0 - 2.0*e*c)))

    def t_s(chi):                  # Schwarzschild time from the apocentre chi = pi
        return quad(dtdchi, np.pi, chi, epsabs=1e-11, epsrel=1e-11, limit=400)[0]
    ra = p/(1.0 - e)

    def t_ks(chi):
        r = p/(1.0 + e*np.cos(chi))
        return t_s(chi) + 2.0*np.log((r/2.0 - 1.0)/(ra/2.0 - 1.0))
    period = t_s(3.0*np.pi)
    peri, cross = [], {R: {"in": [], "out": []} for R in SPHERES}
    k = 1
    while True:
        t = t_ks(2.0*np.pi*k)
        if t > tend:
            break
        peri.append(t)
        k += 1
    for R in SPHERES:
        cr = (p/R - 1.0)/e
        if abs(cr) >= 1.0:
            continue
        chi0 = np.arccos(cr)       # in (0, pi): outgoing branch chi0, ingoing 2 pi - chi0
        k = 0
        while True:
            t_in = t_ks(2.0*np.pi*(k + 1) - chi0)
            t_out = t_ks(2.0*np.pi*(k + 1) + chi0)
            if t_in > tend:
                break
            cross[R]["in"].append(t_in)
            if t_out <= tend:
                cross[R]["out"].append(t_out)
            k += 1
    return {"period": period, "peri": peri, "cross": cross}


def reference():
    r_exc = 2.0/(1.0/ALPHA_EXC**2 - 1.0)       # alpha = (1 + 2/r)^(-1/2)
    ref = {"r_exc": r_exc, "shells": [], "orbits": []}
    for r0 in R0:
        ref["shells"].append({"r0": r0, "E": float(np.sqrt(1.0 - 2.0/r0)),
                              "t_cross": {str(R): float(infall_time(r0, R)) for R in SPHERES
                                          if R < r0},
                              "t_exc": float(infall_time(r0, r_exc))})
    for p, e in ORBITS:
        E, L = orbit_EL(p, e)
        ev = orbit_events(p, e, TEND)
        ref["orbits"].append({"p": p, "e": e, "E": float(E), "L": float(L),
                              "period": float(ev["period"]), "peri": ev["peri"],
                              "cross": {str(R): ev["cross"][R] for R in SPHERES}})
    # totals at the end of the run
    tot = {}
    for R in SPHERES:
        n_in = m_in = e_in = n_out = e_out = 0.0
        for sh in ref["shells"]:
            if str(R) in sh["t_cross"] and sh["t_cross"][str(R)] < TEND:
                n_in += NSHELL
                e_in += NSHELL*MP*sh["E"]
        for ob in ref["orbits"]:
            c = ob["cross"][str(R)]
            n_in += 4*len(c["in"])
            e_in += 4*MP*ob["E"]*len(c["in"])
            n_out += 4*len(c["out"])
            e_out += 4*MP*ob["E"]*len(c["out"])
        tot[str(R)] = {"n_in": n_in, "m_in": n_in*MP, "mE_in": e_in, "n_out": n_out,
                       "m_out": n_out*MP, "mE_out": e_out}
    ref["totals"] = tot
    ref["mE_excised"] = float(sum(NSHELL*MP*sh["E"] for sh in ref["shells"]))
    return ref


# ---- reading the output of a case ----

def read_case(d):
    hst = np.loadtxt(os.path.join(d, "acc.acc.hst"))
    blob = open(os.path.join(d, "acc.removed.bin"), "rb").read()
    assert blob[:8] == b"NRPREM01"
    nf = int(np.frombuffer(blob[8:16], dtype="<i8")[0])
    rem = np.frombuffer(blob[16:], dtype="<f8").reshape(-1, nf)
    snaps = sorted(f for f in os.listdir(d) if f.startswith("acc.part."))
    last = open(os.path.join(d, snaps[-1]), "rb").read()
    n = int(np.frombuffer(last[16:24], dtype="<i8")[0])
    off = 32 + 56*n
    tag = np.frombuffer(last[off:off + 4*n], dtype="<i4")
    spc = np.frombuffer(last[off + 4*n:off + 8*n], dtype="<i4")
    cnt = np.frombuffer(last[off + 8*n + 8*n:off + 8*n + 8*n + 4*n], dtype="<i4")
    t_last = float(np.frombuffer(last[8:16], dtype="<f8")[0])
    return {"hst": hst, "removed": rem, "snap_time": t_last, "snap_tag": tag,
            "snap_species": spc, "snap_peri": cnt}


def judge(case, ref):
    hst, rem = case["hst"], case["removed"]
    out = {}
    end = hst[-1]
    out["t_end"] = float(end[0])
    out["n_excised"], out["m_excised"], out["mE_excised"] = int(end[5]), float(end[6]), float(end[7])
    out["mE_excised_ref"] = ref["mE_excised"]
    out["spheres"] = {}
    for k, R in enumerate(SPHERES):
        c0 = 14 + 9*k
        got = {"n_inside": end[c0 + 1], "m_inside": end[c0 + 2], "n_in": end[c0 + 3],
               "m_in": end[c0 + 4], "mE_in": end[c0 + 5], "n_out": end[c0 + 6],
               "m_out": end[c0 + 7], "mE_out": end[c0 + 8]}
        want = ref["totals"][str(R)]
        # identity: content now = content at t = 0 + in - out - removed (all removals
        # happen inside both spheres)
        ident = np.abs((hst[:, c0 + 2] - hst[0, c0 + 2])
                       - (hst[:, c0 + 4] - hst[:, c0 + 7] - hst[:, 6])).max()
        identn = np.abs((hst[:, c0 + 1] - hst[0, c0 + 1])
                        - (hst[:, c0 + 3] - hst[:, c0 + 6] - hst[:, 5])).max()
        out["spheres"][str(R)] = {"got": {a: float(b) for a, b in got.items()}, "ref": want,
                                  "mass_identity_maxerr": float(ident),
                                  "number_identity_maxerr": float(identn),
                                  "mE_in_relerr": float(got["mE_in"]/want["mE_in"] - 1.0)
                                  if want["mE_in"] else None,
                                  "mE_out_relerr": float(got["mE_out"]/want["mE_out"] - 1.0)
                                  if want["mE_out"] else None}
    # removal record, per shell
    out["shells"] = []
    for k, sh in enumerate(ref["shells"]):
        r = rem[rem[:, 2] == k]
        rr = np.linalg.norm(r[:, 4:7], axis=1)
        out["shells"].append({
            "r0": sh["r0"], "records": int(len(r)),
            "reasons": sorted(set(int(x) for x in r[:, 3])),
            "E_ref": sh["E"], "E_maxrelerr": float(np.abs(r[:, 17]/sh["E"] - 1.0).max()),
            "t_exc_ref": sh["t_exc"], "t_min": float(r[:, 0].min()), "t_max": float(r[:, 0].max()),
            "r_min": float(rr.min()), "r_max": float(rr.max()),
            "alpha_max": float(r[:, 12].max()),
            "peri_counts": sorted(set(int(x) for x in r[:, 19]))})
    out["removed_total"] = int(len(rem))
    out["removed_other_species"] = int(np.sum(rem[:, 2] > 2.5))
    # pericentre counters of the bound orbits at the last snapshot
    out["orbits"] = []
    for k, ob in enumerate(ref["orbits"]):
        sel = case["snap_species"] == 3 + k
        want = int(np.sum(np.array(ob["peri"]) < case["snap_time"]))
        out["orbits"].append({"p": ob["p"], "e": ob["e"], "snapshot_time": case["snap_time"],
                              "peri_counts": [int(x) for x in case["snap_peri"][sel]],
                              "peri_ref": want, "peri_times_ref": ob["peri"]})
    out["infall_peri_counts_in_snapshot"] = sorted(
        set(int(x) for x in case["snap_peri"][case["snap_species"] < 3]))
    return out


def figure(res, cases, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    ref = res["reference"]
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.95, wspace=0.34)
    for name, col, ls in (("mesh", fs.PAL["red"], "-"), ("analytic", fs.PAL["yellow"], "--")):
        if name not in cases:
            continue
        hst = cases[name]["hst"]
        ax[0].plot(hst[:, 0], hst[:, 14 + 3], color=col, ls=ls, label=f"{name}: in, r = 4")
        ax[0].plot(hst[:, 0], hst[:, 14 + 9 + 3], color=col, ls=ls, lw=0.9)
        ax[0].plot(hst[:, 0], hst[:, 14 + 9 + 6], color=col, ls=ls, lw=0.9)
        ax[2].plot(hst[:, 0], hst[:, 10], color=col, ls=ls, label=f"{name}: one or more")
        ax[2].plot(hst[:, 0], hst[:, 12], color=col, ls=ls, lw=0.9)
    # reference staircases
    t = np.linspace(0.0, TEND, 4001)
    for R, kind in ((4.0, "in"), (10.0, "in"), (10.0, "out")):
        n = np.zeros_like(t)
        if kind == "in":
            for sh in ref["shells"]:
                if str(R) in sh["t_cross"]:
                    n += NSHELL*(t >= sh["t_cross"][str(R)])
        for ob in ref["orbits"]:
            for tc in ob["cross"][str(R)][kind]:
                n += 4*(t >= tc)
        ax[0].plot(t, n, **fs.GUIDE, zorder=0)
    ax[0].text(600, 198, "in, r = 4", fontsize=8)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel("particles through a sphere (cumulative)")
    ax[0].set_xlim(0, TEND)
    n1, n2 = np.zeros_like(t), np.zeros_like(t)
    for ob in ref["orbits"]:
        if len(ob["peri"]) > 0:
            n1 += 4*(t >= ob["peri"][0])
        if len(ob["peri"]) > 1:
            n2 += 4*(t >= ob["peri"][1])
    ax[2].plot(t, n1, **fs.GUIDE, zorder=0, label="exact orbits")
    ax[2].plot(t, n2, **fs.GUIDE, zorder=0)
    ax[2].set_xlabel(r"$t/M$")
    ax[2].set_ylabel("particles with 1+ and 2+ pericentre passages")
    ax[2].set_xlim(0, TEND)
    ax[2].set_ylim(-0.5, 11.5)
    ax[2].legend(loc="upper left", fontsize=7)
    # energies of the removed particles and removal times
    for name, col, mk in (("mesh", fs.PAL["red"], "o"), ("analytic", fs.PAL["yellow"], "x")):
        if name not in cases:
            continue
        rem = cases[name]["removed"]
        for k, sh in enumerate(ref["shells"]):
            r = rem[rem[:, 2] == k]
            ax[1].plot(r[:, 0] - sh["t_exc"], (r[:, 17]/sh["E"] - 1.0)*1e3, mk, color=col, ms=3,
                       label=name if k == 0 else None)
    ax[1].axvline(0.0, **fs.MASK_LINE)
    ax[1].axvline(DT, **fs.MASK_LINE)
    ax[1].axhline(0.0, **fs.MASK_LINE)
    ax[1].set_xlabel(r"removal time $-$ exact time at the threshold, $M$")
    ax[1].set_ylabel(r"$10^3\,(E/E_{\rm exact} - 1)$ at removal")
    ax[1].legend(loc="best", fontsize=7)
    fs.save(fig, out + "_accretion")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe")
    ap.add_argument("--fig")
    ap.add_argument("--replot")
    ap.add_argument("--only-mesh", action="store_true")
    args = ap.parse_args()
    run = args.replot or os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("NRPIC_RUN_DIR is not set (start through runreg.py)")
    names = ["mesh", "mesh_rs", "analytic"]
    if not args.replot:
        procs = []
        for name in names:
            d = os.path.join(run, name)
            os.makedirs(d, exist_ok=True)
            npart = make_particles(os.path.join(d, "acc_static.nrp"))
            extra = []
            if name == "analytic":
                extra = ["particles/metric=kerr_schild"]
            if name == "mesh_rs":
                extra = ["time/nlim=8000"]
            log = open(os.path.join(d, "athena.log"), "w")
            procs.append((name, d, subprocess.Popen([args.exe, "-i", INPUT, "-d", d] + extra,
                                                    cwd=d, stdout=log, stderr=subprocess.STDOUT)))
        for name, d, p in procs:
            rc = p.wait()
            print(name, "exit", rc, "particles", npart, flush=True)
        d = os.path.join(run, "mesh_rs")
        rst = sorted(f for f in os.listdir(os.path.join(d, "rst")) if f.endswith(".rst"))[-1]
        with open(os.path.join(d, "athena2.log"), "w") as log:
            rc = subprocess.run([args.exe, "-r", os.path.join(d, "rst", rst), "-d", d,
                                 "time/nlim=-1"], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT).returncode
        print("mesh_rs continued from", rst, "exit", rc, flush=True)
    ref = reference()
    cases = {n: read_case(os.path.join(run, n)) for n in names}
    res = {"reference": ref, "cases": {n: judge(cases[n], ref) for n in names}}
    same = {}
    for f in ("acc.acc.hst", "acc.removed.bin", "acc.nrpic.hst"):
        a = open(os.path.join(run, "mesh", f), "rb").read()
        b = open(os.path.join(run, "mesh_rs", f), "rb").read()
        same[f] = (a == b)
    sa = sorted(f for f in os.listdir(os.path.join(run, "mesh")) if f.startswith("acc.part."))[-1]
    same["last snapshot"] = (open(os.path.join(run, "mesh", sa), "rb").read()
                             == open(os.path.join(run, "mesh_rs", sa), "rb").read())
    res["restart_identical"] = same
    with open(os.path.join(run, "t3_accretion.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    for n in names:
        c = res["cases"][n]
        print(f"== {n}: n_excised {c['n_excised']} mE_excised {c['mE_excised']:.9f} "
              f"(ref {c['mE_excised_ref']:.9f})")
        for R, s in c["spheres"].items():
            print(f"   sphere {R}: got {s['got']}")
            print(f"              ref {s['ref']}  identity {s['mass_identity_maxerr']:.2e} "
                  f"{s['number_identity_maxerr']:.1f}  mE_in relerr {s['mE_in_relerr']} "
                  f"mE_out relerr {s['mE_out_relerr']}")
        for sh in c["shells"]:
            print("   shell", sh)
        for ob in c["orbits"]:
            print("   orbit", {k: v for k, v in ob.items() if k != "peri_times_ref"})
        print("   infall counters in the last snapshot:", c["infall_peri_counts_in_snapshot"],
              "removed, other species:", c["removed_other_species"])
    print("restart identical:", same)
    if args.fig:
        figure(res, cases, args.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
