#!/usr/bin/env python3
"""Processor tests T1, T2, T3, T6 and the restart check of package noise-level2
(predictions: tracks/core/JOURNAL-noise-level2.md, entry 1).

    cpu_tests.py --exe ATHENA --out DIR [--workers 6] [--analyse-only]

All runs: problems/scalar/sr_stochastic.athinput (slow roll, 32^3, nmax2 = 64), mode file
problems/scalar/sr_stochastic_modes.txt, t = 0 .. 3.2, dumps every 0.4 with the metric and
the per-mode record of the projections (noise_rmodes_dump = true).

  h2off, h1off   homogeneous slice (<problem> id = flrw), kicks off, level 2 and level 1 on
                 the mesh (noise_mode_eq = mesh): T1a (t*), T1b
  h2on, h1on     the same with the kicks: T1c, amplitude 1
  h2on3, h1on3   the same with noise_mode_scale = 1e-3: T1c
  s0             the input as it is (level 0, per-shell modes): reference of T2
  s2p, s2m       level 2, noise_mode_scale = +1, -1: T2
  s1p, s1m       level 1 on the mesh, +1, -1: T2 (sign split of level 2 - level 1)
  m0off          level 0 on the mesh, kicks off: T3 (mesh R against shells and against a
                 SciPy reference with the stencil symbol of the Laplacian)
  guard          level 2 on the homogeneous slice with Pi = 0 (Z = 0): T6, exit status 3
  r20, r20r      level 2, 20 cycles with a restart file at cycle 10, and the run restarted
                 from it: every dump and record of cycle 20 byte for byte
Writes DIR/summary.json, DIR/fig_t1t3.png, DIR/fig_t2.png."""
import argparse
import concurrent.futures as cf
import filecmp
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scalar2"))
import nl2                                  # noqa: E402
import numpy as np                          # noqa: E402
import t8_rnr                               # noqa: E402
from nrpic import scalar_field as sf        # noqa: E402

INP = os.path.join(nl2.PROB, "sr_stochastic.athinput")
MODES = os.path.join(nl2.PROB, "sr_stochastic_modes.txt")
SEED = 20261115
NMAX2 = 64
N = 32
L = 2.0*np.pi
MASS = 1.82877655899024605e-01
PHI0 = -2.66679478988261254e+00
PI0 = 2.97300406808996935e-02

BASE = {"scalar_field/noise_mode_file": MODES, "time/tlim": 3.2,
        "scalar_field/dump_dt": 0.4, "scalar_field/dump_noise": "false",
        "scalar_field/dump_constraints": "false", "scalar_field/noise_rmodes_dump": "true"}
OFF = {"scalar_field/noise_kick_pi": "false", "scalar_field/noise_kick_k": "false",
       "scalar_field/noise_kick_a": "false"}
L2 = {"scalar_field/noise_level": 2}
L1M = {"scalar_field/noise_level": 1, "scalar_field/noise_mode_eq": "mesh"}
L0M = {"scalar_field/noise_level": 0, "scalar_field/noise_mode_eq": "mesh"}
HOM = {"problem/id": "flrw"}


def cases():
    c = {
        "h2off": {**HOM, **L2, **OFF}, "h1off": {**HOM, **L1M, **OFF},
        "h2on": {**HOM, **L2}, "h1on": {**HOM, **L1M},
        "h2on3": {**HOM, **L2, "scalar_field/noise_mode_scale": 1e-3},
        "h1on3": {**HOM, **L1M, "scalar_field/noise_mode_scale": 1e-3},
        "s0": {"scalar_field/noise_rmodes_dump": "false"},
        "s2p": {**L2}, "s2m": {**L2, "scalar_field/noise_mode_scale": -1.0},
        "s1p": {**L1M}, "s1m": {**L1M, "scalar_field/noise_mode_scale": -1.0},
        "m0off": {**L0M, **OFF},
        "guard": {**HOM, **L2, "problem/pi0": 0.0, "time/nlim": 5},
        "r20": {**L2, "time/nlim": 20, "scalar_field/dump_dt": -1.0,
                "scalar_field/dump_dcycle": 10, "output9/file_type": "rst",
                "output9/dcycle": 10},
    }
    return {k: {**BASE, **v} for k, v in c.items()}


def run_all(exe, out, workers):
    walls, rcs = {}, {}

    def one(name, par):
        inp = nl2.write_input(INP, os.path.join(out, name + ".athinput"), par)
        t0 = time.time()
        rc = nl2.run(exe, os.path.join(out, name), inp)
        return name, rc, round(time.time() - t0, 2)
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(one, k, v) for k, v in cases().items()]
        for f in futs:
            k, rc, w = f.result()
            rcs[k], walls[k] = rc, w
    # restart from cycle 10
    rst = sorted(glob.glob(os.path.join(out, "r20", "rst", "*.00001.rst")))
    t0 = time.time()
    rcs["r20r"] = nl2.run(exe, os.path.join(out, "r20r"), rst[0], ["time/nlim=20"]) \
        if rst else -1
    walls["r20r"] = round(time.time() - t0, 2)
    return rcs, walls


def modes_at(rundir, k):
    return nl2.read_rmodes(os.path.join(rundir, f"sr.sf.{k:05d}.rmodes"))


def shells_at(rundir, k, n2):
    head, tab = sf.read_modes(os.path.join(rundir, f"sr.sf.{k:05d}.modes"))
    idx = np.searchsorted(tab[:, 0].astype(int), n2)
    return head, (tab[:, 1] + 1j*tab[:, 2])[idx], (tab[:, 3] + 1j*tab[:, 4])[idx]


def ndumps(rundir):
    return len(glob.glob(os.path.join(rundir, "sr.sf.?????.dump")))


def rel(a, b):
    return np.abs(a - b)/np.abs(b)


def stencil_n2(n):
    """|n|^2 with k^2 replaced by the symbol of the sixth-order second difference."""
    kh = 2.0*np.pi*n/N
    return (sf.d2_symbol(kh, 4).sum(axis=1))*(N/(2.0*np.pi))**2


def t2rnr_complex(rundir, n, n2):
    """R^NR_n per dump (complex) and the window, as t8_rnr.analyse."""
    rows = []
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        fl = d["fields"]
        head, tab = sf.read_modes(f.replace(".dump", ".modes"))
        chib = fl["chi"].mean()
        hub = -fl["K"].mean()/3.0
        pib = fl["Pi"].mean()
        psi, _ = sf.analyse(0.5*(fl["chi"]/chib - 1.0), n)
        nn = n.astype(float)
        for name, i, j in t8_rnr.SYM:
            c, _ = sf.analyse(fl[name] - (1.0 if i == j else 0.0), n)
            psi = psi + 0.25*(1.0 if i == j else 2.0)*nn[:, i]*nn[:, j]*c/n2
        dphi, _ = sf.analyse(fl["phi"] - fl["phi"].mean(), n)
        w, _ = t8_rnr.inf.window(n2, L, head["a"], head["H"], head["eps1"])
        rows.append(dict(rnr=psi + (hub/pib)*dphi, w=w))
    return rows


def analyse(out):
    s = {}
    # ---- T1a: projections at t* against the mode file
    _, n, n2, r, dr = modes_at(os.path.join(out, "h2off"), 0)
    mf = np.loadtxt(MODES, comments="#")
    idx = np.searchsorted(mf[:, 0].astype(int), n2)
    rf, drf = (mf[:, 1] + 1j*mf[:, 2])[idx], (mf[:, 3] + 1j*mf[:, 4])[idx]
    s["T1a"] = dict(max_rel_R=float(rel(r, rf).max()), max_rel_dR=float(rel(dr, drf).max()))
    for lab in ("s2p", "m0off"):
        _, _, _, r, dr = modes_at(os.path.join(out, lab), 0)
        s["T1a"][lab] = dict(max_rel_R=float(rel(r, rf).max()),
                             max_rel_dR=float(rel(dr, drf).max()))
    # ---- T1b, T1c: level 2 against level 1 on the mesh, homogeneous slice
    for lab, a, b in (("T1b", "h2off", "h1off"), ("T1c_amp1", "h2on", "h1on"),
                      ("T1c_amp1e-3", "h2on3", "h1on3")):
        rows = []
        for k in range(ndumps(os.path.join(out, a))):
            ha, _, _, ra, da = modes_at(os.path.join(out, a), k)
            _, _, _, rb, db = modes_at(os.path.join(out, b), k)
            rows.append(dict(time=ha["time"], max_rel_R=float(rel(ra, rb).max()),
                             max_rel_dR=float(rel(da, db).max()),
                             rms_rel_R=float(np.sqrt(np.mean(rel(ra, rb)**2)))))
        s[lab] = rows
    # ---- T3: mesh R (level 0, uniform coefficients) against shells and the stencil ODE
    rd = os.path.join(out, "m0off")
    nd = ndumps(rd)
    times = [modes_at(rd, k)[0]["time"] for k in range(nd)]
    _, n, n2, _, _ = modes_at(rd, 0)
    n2s = stencil_n2(n)
    u, inv = np.unique(np.round(n2s, 12), return_inverse=True)
    # mode functions at t = 0 for the unique stencil values: those of the mode's shell
    first = np.array([np.where(inv == j)[0][0] for j in range(u.size)])
    v, dv = sf.potential("quadratic", mass=MASS)
    ref = sf.ms_reference(v, dv, PHI0, PI0, u, rf[first], drf[first], L, np.array(times))
    # continuum reference too (same integrator): the per-shell mode functions
    uc, invc = np.unique(n2, return_inverse=True)
    firstc = np.array([np.where(invc == j)[0][0] for j in range(uc.size)])
    refc = sf.ms_reference(v, dv, PHI0, PI0, uc, rf[firstc], drf[firstc], L,
                           np.array(times))
    t3 = []
    sym = n2s/n2
    for k in range(nd):
        h, _, _, r, dr = modes_at(rd, k)
        _, rs, _ = shells_at(rd, k, n2)
        rst = ref["R"][k][inv]
        rct = refc["R"][k][invc]
        # the time-integration error of the code is common to the mesh R and the shells:
        # the double ratio leaves the spatial operator alone
        dbl = np.abs((r/rs)/(rst/rct) - 1.0)
        t3.append(dict(time=h["time"],
                       mesh_vs_shell_le48=float(rel(r, rs)[n2 <= 48].max()),
                       double_ratio_max=float(dbl.max()),
                       mesh_vs_shell_max=float(rel(r, rs).max()),
                       mesh_vs_shell_cut=float(rel(r, rs)[n2 == NMAX2].max()),
                       mesh_vs_shell_below=float(rel(r, rs)[n2 < NMAX2].max()),
                       mesh_vs_stencil_ref_max=float(rel(r, rst).max()),
                       shell_vs_cont_ref_max=float(rel(rs, rct).max())))
    s["T3"] = dict(symbol_over_k2_cut=float(sym[n2 == NMAX2].min()),
                   symbol_over_k2_min=float(sym.min()), rows=t3)
    # per-mode deviation at the last dump (figure)
    h, _, _, r, dr = modes_at(rd, nd - 1)
    _, rs, _ = shells_at(rd, nd - 1, n2)
    rst, rct = ref["R"][nd-1][inv], refc["R"][nd-1][invc]
    t3fig = dict(q=np.sqrt(n2), dev_shell=rel(r, rs), dev_ref=rel(r, rst),
                 dev_dbl=np.abs((r/rs)/(rst/rct) - 1.0), pred=rel(rst, rct),
                 sym=sym, time=h["time"])
    # ---- T2: R^NR per mode against W R alpha (continuum lockstep), levels 0, 2, 1-mesh
    nn, nn2 = sf.mode_set(NMAX2)
    al = sf.mode_alpha(SEED, 0, 0, nn)
    t2 = {}
    t2rows = {}
    for lab in ("s0", "s2p", "s1p"):
        rows = t8_rnr.analyse(os.path.join(out, lab), nn, nn2, al, L)
        t2rows[lab] = rows
        last = rows[-1]
        ent = last["w"] > 0.5
        t2[lab] = dict(time=last["time"], efolds=last["efolds"],
                       max_dev_entered=float(last["dev"][ent].max()),
                       max_dev_below_cut=float(last["dev"][ent & (nn2 < NMAX2)].max()),
                       max_dev_cut=float(last["dev"][ent & (nn2 == NMAX2)].max())
                       if (ent & (nn2 == NMAX2)).any() else None,
                       max_dev_all_times=float(max(r["dev"][r["w"] > 0.5].max()
                                                   for r in rows)))
    # R^NR against W c_R of the run's own mesh field (projected coefficients): the
    # stencil drops out, what is left is the accuracy of the sources and the slice
    for lab in ("s2p", "s1p"):
        devs = []
        for k, row in enumerate(t2rnr_complex(os.path.join(out, lab), nn, nn2)):
            _, _, n2r, re_, _ = modes_at(os.path.join(out, lab), k)
            refm = L**-1.5*row["w"]*re_*al
            devs.append((row, np.abs(row["rnr"]/refm - 1.0)))
        row, dv = devs[-1]
        ent = row["w"] > 0.5
        t2[lab]["max_dev_le48"] = float(t2rows[lab][-1]["dev"][ent & (nn2 <= 48)].max())
        t2[lab]["own_mesh_ref_max_dev"] = float(dv[ent].max())
        t2[lab]["own_mesh_ref_max_dev_all_times"] = float(max(d[r_["w"] > 0.5].max()
                                                              for r_, d in devs))
        t2rows[lab + "_own"] = dv
    last0 = t2rows["s0"][-1]
    t2["s0"]["max_dev_le48"] = float(last0["dev"][(last0["w"] > 0.5) & (nn2 <= 48)].max())
    s["T2_rnr"] = t2
    # sign split of D = phi_L2 - phi_L1mesh under the sign of the amplitude
    split = []
    for k in range(ndumps(os.path.join(out, "s2p"))):
        f = {lab: sf.read_dump(os.path.join(out, lab, f"sr.sf.{k:05d}.dump"))["fields"]
             for lab in ("s2p", "s2m", "s1p", "s1m")}
        dp = f["s2p"]["phi"] - f["s1p"]["phi"]
        dm = f["s2m"]["phi"] - f["s1m"]["phi"]
        pert = f["s1p"]["phi"] - f["s1p"]["phi"].mean()
        ev, od = 0.5*(dp + dm), 0.5*(dp - dm)
        ev = ev - ev.mean()
        od = od - od.mean()
        rms = lambda x: float(np.sqrt(np.mean(x*x)))   # noqa: E731
        split.append(dict(dump=k, even_rms=rms(ev), odd_rms=rms(od), pert_rms=rms(pert),
                          mean_even=float(0.5*(dp + dm).mean())))
    s["T2_split"] = split
    # ---- T6 guard and restart
    s["T6_guard_log"] = [ln.strip() for ln in open(os.path.join(out, "guard", "log.txt"))
                         if "WARNING" in ln or "guard" in ln.lower()][:6]
    same, differ = [], []
    for f in sorted(os.listdir(os.path.join(out, "r20r"))):
        if not (f.startswith("sr.sf.00002") or f.endswith(".hst")):
            continue
        a, b = os.path.join(out, "r20", f), os.path.join(out, "r20r", f)
        if os.path.exists(a) and f.startswith("sr.sf.00002"):
            (same if filecmp.cmp(a, b, shallow=False) else differ).append(f)
    s["restart"] = dict(identical=same, differ=differ)
    return s, t3fig, t2rows, nn2


def figures(out, s, t3fig, t2rows, nn2):
    fs = nl2_style()
    import matplotlib.pyplot as plt
    # T1, T3
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.9, wspace=0.38)
    a = ax[0]
    for lab, cl, mk in (("T1b", fs.PAL["blue"], "o"), ("T1c_amp1", fs.PAL["orange"], "s"),
                        ("T1c_amp1e-3", fs.PAL["green"], "^")):
        t = [r["time"] for r in s[lab]]
        y = [max(r["max_rel_R"], 1e-17) for r in s[lab]]
        a.semilogy(t, y, mk + "-", ms=3, color=cl, label={"T1b": "kicks off",
                   "T1c_amp1": "kicks on", "T1c_amp1e-3": "kicks on, amp. 1e-3"}[lab])
    a.set_xlabel("$t$ (1/H$_*$)")
    a.set_ylabel(r"max$_n$ $|c^{L2}_R/c^{L1}_R-1|$")
    a.set_title("(a) homogeneous slice", fontsize=8)
    a.legend(fontsize=6, loc="center right")
    a = ax[1]
    a.semilogy(t3fig["q"], np.maximum(t3fig["dev_shell"], 1e-17), ".", ms=3,
               color=fs.PAL["blue"], label="mesh R vs shells (continuum $k^2$)")
    a.semilogy(t3fig["q"], np.maximum(t3fig["dev_ref"], 1e-17), ".", ms=3,
               color=fs.PAL["orange"], label="mesh R vs ODE with stencil $k^2$")
    a.semilogy(t3fig["q"], np.maximum(t3fig["dev_dbl"], 1e-17), "x", ms=3,
               color=fs.PAL["green"], label="double ratio (time error removed)")
    a.semilogy(t3fig["q"], np.maximum(t3fig["pred"], 1e-17), "_", ms=5,
               color="0.3", label="prediction: stencil ODE vs continuum ODE")
    a.set_xlabel("$|n|$")
    a.set_ylabel(r"$|R^{\rm mesh}_n/R^{\rm ref}_n-1|$")
    a.set_title(f"(b) level 0 on the mesh, kicks off, $t={t3fig['time']:.1f}$", fontsize=8)
    a.set_ylim(1e-9, 3.0)
    a.legend(fontsize=5.5, loc="upper left", ncol=2)
    a = ax[2]
    t = [r["time"] for r in s["T3"]["rows"]]
    a.semilogy(t, [r["mesh_vs_shell_cut"] for r in s["T3"]["rows"]], "o-", ms=3,
               color=fs.PAL["blue"], label="$|n|^2=64$ vs shells")
    a.semilogy(t, [max(r["mesh_vs_shell_below"], 1e-17) for r in s["T3"]["rows"]], "s-",
               ms=3, color=fs.PAL["green"], label="$|n|^2<64$ vs shells")
    a.semilogy(t, [max(r["mesh_vs_stencil_ref_max"], 1e-17) for r in s["T3"]["rows"]],
               "^-", ms=3, color=fs.PAL["orange"], label="all vs stencil ODE")
    a.set_xlabel("$t$ (1/H$_*$)")
    a.set_ylabel("max relative deviation")
    a.set_title("(c) stencil symbol in time", fontsize=8)
    a.legend(fontsize=6, loc="lower right")
    fig.savefig(os.path.join(out, "fig_t1t3.png"), dpi=200)
    plt.close(fig)
    # T2
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.9, wspace=0.28)
    a = ax[0]
    q = np.sqrt(nn2)
    for lab, cl, nm in (("s0", fs.PAL["blue"], "level 0 (shells)"),
                        ("s2p", fs.PAL["orange"], "level 2"),
                        ("s1p", fs.PAL["green"], "level 1 (mesh)")):
        last = t2rows[lab][-1]
        sel = last["w"] > 0.5
        a.semilogy(q[sel] + {"s0": -0.08, "s2p": 0.0, "s1p": 0.08}[lab],
                   last["dev"][sel], ".", ms=3, color=cl, label=nm)
    last = t2rows["s2p"][-1]
    sel = last["w"] > 0.5
    a.semilogy(q[sel] + 0.16, t2rows["s2p_own"][sel], "x", ms=3, color=fs.PAL["red"],
               label="level 2 vs $W c_R$ of its mesh R")
    a.axhline(2e-2, color="0.4", lw=0.8, ls="--")
    a.set_xlabel("$|n|$")
    a.set_ylabel(r"$|R^{\rm NR}_n/(W R\,\alpha_n)-1|$, $W>1/2$")
    a.set_title(f"(a) $t = {t2rows['s0'][-1]['time']:.1f}$", fontsize=8)
    a.set_ylim(1e-8, 3.0)
    a.legend(fontsize=6, loc="upper left", ncol=2)
    a = ax[1]
    k = [r["dump"] for r in s["T2_split"]]
    a.semilogy(k, [max(r["even_rms"], 1e-30) for r in s["T2_split"]], "o-", ms=3,
               color=fs.PAL["orange"], label="even part of $\\delta\\phi_{L2}-\\delta\\phi_{L1}$")
    a.semilogy(k, [max(r["odd_rms"], 1e-30) for r in s["T2_split"]], "s-", ms=3,
               color=fs.PAL["blue"], label="odd part")
    a.semilogy(k, [max(r["pert_rms"], 1e-30) for r in s["T2_split"]], "^-", ms=3,
               color="0.5", label="$\\delta\\phi$ (level 1)")
    a.set_xlabel("dump (every 0.4/H$_*$)")
    a.set_ylabel("rms over the cells")
    a.set_title("(b) sign of the amplitude", fontsize=8)
    a.legend(fontsize=6, loc="center right")
    fig.savefig(os.path.join(out, "fig_t2.png"), dpi=200)
    plt.close(fig)


def nl2_style():
    import matplotlib
    matplotlib.use("Agg")
    from nrpic import figstyle
    figstyle.use_style()
    return figstyle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--from", dest="src", help="--analyse-only: the run directory of an "
                    "earlier call (read only); results go to --out")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    src = os.path.abspath(a.src) if a.src else out
    summ = dict(exe=os.path.abspath(a.exe), runs=src)
    if not a.analyse_only:
        summ["exit"], summ["wall_s"] = run_all(os.path.abspath(a.exe), out, a.workers)
    else:
        old = json.load(open(os.path.join(src, "summary.json")))
        summ["exit"], summ["wall_s"] = old.get("exit"), old.get("wall_s")
    s, t3fig, t2rows, nn2 = analyse(src)
    summ.update(s)
    nl2.dump_json(summ, os.path.join(out, "summary.json"))
    figures(out, s, t3fig, t2rows, nn2)
    print(json.dumps({k: summ[k] for k in ("exit", "T1a", "T2_rnr")}, indent=1))


if __name__ == "__main__":
    main()
