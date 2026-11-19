#!/usr/bin/env python3
"""P1 of flux_tools: test particles falling into a fixed Schwarzschild black hole on the
processors (journal entry 2).

    p1.py run --exe ATHENA [--out DIR]       particle file, exact references, AthenaK cases
                                             mesh (static mesh metric) and analytic
    p1.py analyse --run DIR [--out DIR]      readers + comparison against the exact orbits

Exact references (exact_ks.py): per particle E, L, capture, Kerr-Schild time of the
horizon passage (r = 2M), of the removal radius (alpha_KS = alpha_exc) and of every
passage through the flux spheres up to tlim. The comparison is run with the exact horizon
history of the would-be accretion, M_ex(t) = 1 + sum of m E over particles with
t_hor <= t (test-particle limit: the hole does not grow; this is the growth the fluxes
must account for), against the code's removal records (lower bound) and the sphere at
r = 3M (upper bound); the sphere at r = 2M is the horizon itself here.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare as cmp  # noqa: E402
import exact_ks as ek  # noqa: E402
import fluxio  # noqa: E402

INPUT = os.path.join(HERE, "inputs", "p1_fixed_bh.athinput")
SEED = 20261119
MP = 1.0e-4
ALPHA_EXC = 0.65
SPHERES = (2.0, 3.0, 8.0)
TLIM = 400.0
DT = 0.05
NA, NB, NC = 2000, 600, 400
RB = 12.0


def directions(rng, n):
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1)[:, None]


def tangent(rng, n):
    a = rng.normal(size=n.shape)
    a -= np.einsum("pi,pi->p", a, n)[:, None] * n
    return a / np.linalg.norm(a, axis=1)[:, None]


def L_crit(r0, M=1.0):
    """Largest L below which an orbit released at its apocentre r0 is captured."""
    def captured(L):
        E2 = (1 - 2 * M / r0) * (1 + L * L / r0 ** 2)
        if L * L <= 12 * M * M:
            return True
        rmax = (L * L - L * math.sqrt(L * L - 12 * M * M)) / (2 * M)
        Vmax = (1 - 2 * M / rmax) * (1 + L * L / rmax ** 2)
        return E2 > Vmax
    lo, hi = math.sqrt(12.0), math.sqrt(r0 ** 2 * M / (r0 - 3 * M)) * (1 - 1e-9)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if captured(mid) else (lo, mid)
    return 0.5 * (lo + hi)


def make_particles():
    rng = np.random.default_rng(SEED)
    # A: at rest relative to the static observers, uniform in volume, 3 <= r0 <= 14
    nA = directions(rng, NA)
    rA = (27.0 + rng.random(NA) * (14.0 ** 3 - 27.0)) ** (1.0 / 3.0)
    xA = rA[:, None] * nA
    uA = ek.static_u(xA)
    # B: from the apocentre r0 = 12 with angular momentum L, avoiding +-0.03 around L_crit
    Lc = L_crit(RB)
    Lcirc = math.sqrt(RB ** 2 / (RB - 3.0))
    L = rng.random(NB) * (Lcirc - 0.02)
    near = np.abs(L - Lc) < 0.03
    L[near] = Lc + np.sign(L[near] - Lc + 1e-12) * (0.03 + rng.random(near.sum()) * 0.02)
    L = np.clip(L, 0.0, Lcirc - 0.02)
    nB = directions(rng, NB)
    tB = tangent(rng, nB)
    xB = RB * nB
    q = 2.0 / RB
    EB = np.sqrt((1 - q) * (1 + L ** 2 / RB ** 2))
    uB = (q * EB / (1 - q))[:, None] * nB + (L / RB)[:, None] * tB
    # C: marginally bound radial inflow from 14-16 M
    nC = directions(rng, NC)
    rC = 14.0 + 2.0 * rng.random(NC)
    xC = rC[:, None] * nC
    uC = ek.radial_u_for_energy(xC, 1.0)
    x = np.vstack([xA, xB, xC])
    u = np.vstack([uA, uB, uC])
    sp = np.concatenate([np.zeros(NA), np.ones(NB), np.full(NC, 2)]).astype(np.int32)
    return x, u, sp, dict(L_crit=Lc, L_circ=Lcirc)


def exact_refs(x, u):
    E, L, ur, r0 = ek.invariants(x, u)
    r_exc = ek.r_of_alpha(ALPHA_EXC)
    n = x.shape[0]
    ref = dict(E=E, L=L, r0=r0, captured=np.zeros(n, bool), t_hor=np.full(n, np.nan),
               t_exc=np.full(n, np.nan), tau_hor=np.full(n, np.nan), rp=np.full(n, np.nan))
    cross = {rs: ([], []) for rs in SPHERES}
    who = {rs: ([], []) for rs in SPHERES}
    for i in range(n):
        o = ek.Orbit(r0[i], E[i], L[i], ur[i])
        ref["captured"][i] = o.captured
        if o.captured:
            ref["t_hor"][i] = o.t_in(2.0)
            ref["t_exc"][i] = o.t_in(r_exc)
            ref["tau_hor"][i] = o.tau_in(2.0)
        else:
            ref["rp"][i] = o.rp
        for rs in SPHERES:
            ins, outs = o.crossings(rs, TLIM)
            cross[rs][0].extend(ins)
            cross[rs][1].extend(outs)
            who[rs][0].extend([i] * len(ins))
            who[rs][1].extend([i] * len(outs))
    ref["r_exc"] = r_exc
    ref["cross"] = {rs: (np.array(v[0]), np.array(v[1])) for rs, v in cross.items()}
    ref["cross_who"] = {rs: (np.array(v[0], int), np.array(v[1], int)) for rs, v in who.items()}
    return ref


def cmd_run(a):
    out = a.out
    os.makedirs(out, exist_ok=True)
    x, u, sp, meta = make_particles()
    nrp = os.path.join(out, "p1.nrp")
    fluxio.write_nrp(nrp, x, u, MP, sp)
    with open(os.path.join(out, "p1_meta.json"), "w") as f:
        json.dump(dict(meta, seed=SEED, n=[NA, NB, NC], m=MP), f, indent=1)
    walls = {}
    for case, extra in (("mesh", []), ("analytic", ["particles/metric=kerr_schild"])):
        d = os.path.join(out, case)
        os.makedirs(d, exist_ok=True)
        shutil.copy(nrp, os.path.join(d, "p1.nrp"))
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            subprocess.run([a.exe, "-i", INPUT, "-d", d] + extra, cwd=d, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        walls[case] = time.time() - t0
    with open(os.path.join(out, "walls.json"), "w") as f:
        json.dump(walls, f, indent=1)
    print(json.dumps(walls))


def cmd_analyse(a):
    out = a.out
    os.makedirs(out, exist_ok=True)
    nrp = fluxio.read_nrp(os.path.join(a.run, "p1.nrp"))
    ref = exact_refs(nrp["x"], nrp["u"])
    m = nrp["m"]
    res = dict(exact=dict(n_captured=int(ref["captured"].sum()),
                          n_captured_by_species=[int((ref["captured"] & (nrp["species"] == s)).sum())
                                                 for s in range(3)],
                          r_exc=ref["r_exc"],
                          mE_captured=float((m * ref["E"])[ref["captured"]].sum()),
                          m_captured=float(m[ref["captured"]].sum()),
                          t_hor_range=[float(np.nanmin(ref["t_hor"])), float(np.nanmax(ref["t_hor"]))],
                          lag_exc_minus_hor=[float(np.nanmin(ref["t_exc"] - ref["t_hor"])),
                                             float(np.nanmax(ref["t_exc"] - ref["t_hor"]))],
                          crossings={str(rs): [len(v[0]), len(v[1])] for rs, v in ref["cross"].items()}))
    t_grid = np.arange(0.0, TLIM + 1e-9, 0.25)
    ok = ref["captured"] & (ref["t_hor"] <= TLIM)
    M_ex = 1.0 + cmp.step_cumsum(ref["t_hor"][ok], (m * ref["E"])[ok], t_grid)
    hor = dict(time=t_grid, mass=M_ex)
    cases = {}
    for case in ("mesh", "analytic"):
        d = os.path.join(a.run, case)
        rem = fluxio.read_removed(os.path.join(d, "p1.removed.bin"))
        acc = fluxio.read_hst(os.path.join(d, "p1.acc.hst"))
        hst = fluxio.read_hst(os.path.join(d, "p1.nrpic.hst"))
        tag = rem["tag"]
        r = dict(n_records=int(rem["n"]), reasons=sorted(set(rem["reason"].tolist())),
                 n_excised_acc=int(acc["n_excised"][-1]), n_excised_hst=int(hst["n_excised"][-1]),
                 n_escaped=int(hst["n_escaped"][-1]),
                 removed_tags_equal_exact=bool(np.array_equal(np.sort(tag),
                                                              np.where(ok)[0])),
                 E_relerr_max=float(np.abs(rem["E"] / ref["E"][tag] - 1).max()),
                 E_relerr_max_by_species=[float(np.abs(rem["E"] / ref["E"][tag] - 1)[nrp["species"][tag] == s].max())
                                          if np.any(nrp["species"][tag] == s) else None for s in range(3)],
                 removal_lag_steps=[float(((rem["time"] - ref["t_exc"][tag]) / DT).min()),
                                    float(((rem["time"] - ref["t_exc"][tag]) / DT).max())],
                 removal_lag_steps_by_species=[
                     [float(((rem["time"] - ref["t_exc"][tag]) / DT)[nrp["species"][tag] == s].min()),
                      float(((rem["time"] - ref["t_exc"][tag]) / DT)[nrp["species"][tag] == s].max()),
                      int(np.sum(((rem["time"] - ref["t_exc"][tag]) / DT)[nrp["species"][tag] == s] < 0)),
                      int(np.sum(((rem["time"] - ref["t_exc"][tag]) / DT)[nrp["species"][tag] == s] > 1))]
                     for s in range(3)],
                 mE_records=float((rem["m"] * rem["E"]).sum()))
        sph = {}
        t = acc["time"]
        for k, rs in enumerate(SPHERES, start=1):
            ins, outs = ref["cross"][rs]
            n_in_ex = np.searchsorted(np.sort(ins), t, side="right")
            n_out_ex = np.searchsorted(np.sort(outs), t, side="right")
            # tolerance: crossings within one step of the record time are ambiguous
            amb_in = np.searchsorted(np.sort(ins), t + DT, side="right") - np.searchsorted(np.sort(ins), t - DT, side="left")
            amb_out = np.searchsorted(np.sort(outs), t + DT, side="right") - np.searchsorted(np.sort(outs), t - DT, side="left")
            bad = (np.abs(acc[f"n_in{k}"] - n_in_ex) > amb_in) | (np.abs(acc[f"n_out{k}"] - n_out_ex) > amb_out)
            wi, wo = ref["cross_who"][rs]
            mE_in_ex = float((m[wi] * ref["E"][wi]).sum())
            mE_out_ex = float((m[wo] * ref["E"][wo]).sum())
            n_pred = acc[f"n_inside{k}"][0] + acc[f"n_in{k}"] - acc[f"n_out{k}"] - acc["n_excised"]
            sph[str(rs)] = dict(n_in=int(acc[f"n_in{k}"][-1]), n_in_exact=len(ins),
                                n_out=int(acc[f"n_out{k}"][-1]), n_out_exact=len(outs),
                                records_outside_tolerance=int(bad.sum()), n_records=int(t.size),
                                mE_in=float(acc[f"mE_in{k}"][-1]), mE_in_exact=mE_in_ex,
                                mE_out=float(acc[f"mE_out{k}"][-1]), mE_out_exact=mE_out_ex,
                                identity_n_maxerr=float(np.abs(acc[f"n_inside{k}"] - n_pred).max()))
        r["spheres"] = sph
        # the horizon sphere against the exact horizon flux at every record
        F2 = acc["mE_in1"] - acc["mE_out1"]
        F2_ex = cmp.step_cumsum(ref["t_hor"][ok], (m * ref["E"])[ok], t)
        F2_ex_lo = cmp.step_cumsum(ref["t_hor"][ok], (m * ref["E"])[ok], t - DT)
        r["horizon_sphere_vs_exact_maxabs"] = float(np.abs(F2 - F2_ex).max())
        r["horizon_sphere_outside_one_step"] = int(np.sum((F2 < F2_ex_lo - 1e-9) | (F2 > F2_ex + 1e-9)))
        # the same with a tolerance of half the smallest m E of one particle (separates a
        # crossing registered in another step from the accumulated error of the energies)
        half = 0.5 * float(np.min((m * ref["E"])[ok]))
        r["horizon_sphere_records_off_by_a_particle"] = int(np.sum((F2 < F2_ex_lo - half) | (F2 > F2_ex + half)))
        c = cmp.compare(hor, 0.0, rem=rem, acc=acc, finder_tol=1e-5, sphere=2)
        cbad = cmp.compare(dict(time=t_grid, mass=1.0 + 0.97 * (M_ex - 1.0)), 0.0, rem=rem,
                           acc=acc, finder_tol=1e-5, sphere=2)
        clate = cmp.compare(dict(time=t_grid, mass=np.interp(t_grid - 2.0, t_grid, M_ex, left=1.0)),
                            0.0, rem=rem, acc=acc, finder_tol=1e-5, sphere=2)
        r["compare_exact_horizon"] = c["summary"]
        r["compare_growth_x0.97"] = cbad["summary"]
        r["compare_horizon_late_2M"] = clate["summary"]
        cases[case] = (r, rem, acc, c)
        res[case] = r
    figures(out, nrp, ref, cases, t_grid, M_ex)
    with open(os.path.join(out, "p1_analysis.json"), "w") as f:
        json.dump(cmp.jsonable(res), f, indent=1)
    print(json.dumps(cmp.jsonable(res), indent=1))


def figures(out, nrp, ref, cases, t_grid, M_ex):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(figstyle.FULL_WIDTH, 5.8))
    r, rem, acc, c = cases["mesh"]
    tag = rem["tag"]
    sp = nrp["species"][tag]
    cols = [figstyle.PAL["blue"], figstyle.PAL["red"], figstyle.PAL["green"]]
    names = ["A: at rest, 3-14 M", "B: apocentre 12 M, L", "C: E = 1 inflow"]
    for s in range(3):
        sel = sp == s
        ax[0, 0].semilogy(ref["t_exc"][tag][sel], np.abs(rem["E"][sel] / ref["E"][tag][sel] - 1) + 1e-17,
                          ".", ms=2, color=cols[s], label=names[s])
    ra, rema, acca, ca = cases["analytic"]
    taga = rema["tag"]
    ax[0, 0].semilogy(ref["t_exc"][taga], np.abs(rema["E"] / ref["E"][taga] - 1) + 1e-17, ".", ms=1,
                      color="grey", label="analytic metric")
    ax[0, 0].set_xlabel(r"exact removal time $t_{\rm exc}\ [M]$")
    ax[0, 0].set_ylabel(r"$|E_{\rm rec}/E_{\rm exact}-1|$")
    ax[0, 0].legend(fontsize=6)
    a = ax[0, 1]
    t = acc["time"]
    ok = ref["captured"]
    F2_ex = cmp.step_cumsum(ref["t_hor"][ok], (nrp["m"] * ref["E"])[ok], t)
    a.plot(t, (acc["mE_in1"] - acc["mE_out1"]) - F2_ex, color=figstyle.PAL["blue"], lw=0.8,
           label=r"sphere $r=2M$ minus exact horizon flux")
    a.plot(t, c["F_sph"][np.searchsorted(c["t"], t).clip(0, c["t"].size - 1)] * 0 + 0, lw=0)
    a.axhline(0, **figstyle.THIN)
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel(r"$\Delta(\sum mE)\ [M]$")
    a.legend(fontsize=6)
    a = ax[1, 0]
    for k, rs, cc in ((1, 2.0, figstyle.PAL["blue"]), (2, 3.0, figstyle.PAL["red"]), (3, 8.0, figstyle.PAL["green"])):
        ins, outs = ref["cross"][rs]
        a.plot(t, acc[f"n_in{k}"], color=cc, label=f"in, $r={rs:g}$")
        a.plot(t, acc[f"n_out{k}"], color=cc, ls=":", label=f"out, $r={rs:g}$")
        a.step(np.sort(ins), np.arange(1, len(ins) + 1), where="post", **dict(figstyle.GUIDE, lw=0.7))
        if len(outs):
            a.step(np.sort(outs), np.arange(1, len(outs) + 1), where="post", **dict(figstyle.GUIDE, lw=0.7))
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel("cumulative crossings (dashed: exact)")
    a.legend(fontsize=6, ncol=2)
    a = ax[1, 1]
    a.plot(c["t"], c["dM"] - c["F_rem"], color=figstyle.PAL["red"],
           label=r"$\Delta M_{\rm exact}-F_{\rm rem}$ (code)")
    a.plot(c["t"], c["F_sph"] - c["dM"], color=figstyle.PAL["green"],
           label=r"$F_{\rm sph}(r=3M)-\Delta M_{\rm exact}$")
    a.axhline(0, **figstyle.THIN)
    a.axhline(-3e-5, **dict(figstyle.GUIDE, lw=0.8))
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel(r"bracket margins $[M]$ (dashed: $-3\sigma$)")
    a.legend(fontsize=6)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "p1_fixed_bh"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--exe", required=True)
    r.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    an = sub.add_parser("analyse")
    an.add_argument("--run", required=True)
    an.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    cmd_run(a) if a.cmd == "run" else cmd_analyse(a)


if __name__ == "__main__":
    main()
