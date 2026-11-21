#!/usr/bin/env python3
"""Processor tests of the source item gauge-2 (tracks/core/JOURNAL-gauge-2.md, entry 4).

    ptests.py --new ATHENA --rel ATHENA --out DIR [--threads 2] [--jobs 3] [--only T1,T2,T3]

T1  coarse vacuum mesh (problems/es/v1_small.athinput without refinement: 64^3 cells of
    2 M, 10 M): plain 1+log, the relaxed lapse of the first pass, the relaxed lapse
    restricted to the matter (lapse_leak_rho), switched off around the tracker with a
    radius beyond the mesh (lapse_leak_hole), and with a narrow smooth onset.  Checks:
    restricted-to-matter and plain 1+log write the same bytes; the first pass differs
    from plain 1+log (the term is active); the tracker variant equals plain 1+log in
    the files both write.
T2  homogeneous dust universe (problems/cosmo/flrw_leak.athinput, rate 5): with
    lapse_leak_rho below the density the history equals that of the first pass.
T3  expanding ball L1 at cells of 1 M (problems/ball/ball_leak.athinput, t = 10 M): first
    pass with the release executable and with the new one (same bytes), and restricted
    to the matter, for T = 1 M and 0.5 M; shell errors against the exact solution and
    the lapse at the centre (the analysis of the first pass, tracks/core/analysis/id).

Every run is DIR/<case>/; results in DIR/ptests.json; figure DIR/ptests_ball.png.
The executables are threaded builds (OMP_NUM_THREADS = --threads) or serial ones.
"""
import argparse
import concurrent.futures as cf
import filecmp
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/id"))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/gauge"))
sys.path.insert(0, os.path.join(WT, "python"))

VDATA = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-170213-d2c2131/v1"
IC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball"
INP = os.path.join(HERE, "inputs")
COARSE = ["mesh_refinement/refinement=none", "time/tlim=10.0",
          f"particles/particle_file={VDATA}/v1.nrp", f"problem/comp0_file={VDATA}/v1.tab"]
RHO_BALL = "1.0e-5"        # ball of L1: density 2.4e-4 at the start, 8.5e-5 at t = 10 M


def ball_args(n=64, half=32.0, stem="t2_sharp_h1", tlim=10.0):
    with open(os.path.join(IC, stem + ".json")) as f:
        meta = json.load(f)
    dx = 2.0 * half / n
    return [f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
            f"mesh/x1min={-half}", f"mesh/x1max={half}", f"mesh/x2min={-half}",
            f"mesh/x2max={half}", f"mesh/x3min={-half}", f"mesh/x3max={half}",
            "meshblock/nx1=32", "meshblock/nx2=32", "meshblock/nx3=32",
            f"time/tlim={tlim}", f"particles/traj_dcycle={max(1, int(round(1.0 / dx)))}",
            f"particles/traj_ntrack={meta['traj_ntrack']}",
            f"particles/particle_file={IC}/{stem}.nrp", f"problem/comp0_file={IC}/{stem}.tab",
            "problem/shift=zero"]


def cases(new, rel):
    c = {}
    v = os.path.join(INP, "v8_var.athinput")
    r = os.path.join(INP, "v8_rho.athinput")
    c["T1-plain"] = (new, r, COARSE + ["z4c/lapse_leak=0.0"])
    c["T1-leak"] = (new, r, COARSE + ["z4c/lapse_leak=0.5"])
    c["T1-rho"] = (new, r, COARSE + ["z4c/lapse_leak=0.5", "z4c/lapse_leak_rho=1.0e-8"])
    c["T1-plain-tr"] = (new, v, COARSE + ["z4c/lapse_leak=0.0"])
    c["T1-hole"] = (new, v, COARSE + ["z4c/lapse_leak=0.5", "z4c/lapse_leak_hole=1000.0"])
    c["T1-leak-tr"] = (new, v, COARSE + ["z4c/lapse_leak=0.5"])
    c["T1-onset"] = (new, v, COARSE + ["z4c/lapse_leak=0.5", "z4c/lapse_leak_onset=1.0e-9"])
    f = os.path.join(INP, "flrw_rho.athinput")
    c["T2-first"] = (new, f, ["z4c/lapse_leak=5.0"])
    c["T2-rho"] = (new, f, ["z4c/lapse_leak=5.0", "z4c/lapse_leak_rho=1.0e-3"])
    b = os.path.join(INP, "ball_rho.athinput")
    for tag, rate in (("leak1", "1.0"), ("leak05", "2.0")):
        c[f"T3-{tag}-rel"] = (rel, b, ball_args() + [f"z4c/lapse_leak={rate}"])
        c[f"T3-{tag}"] = (new, b, ball_args() + [f"z4c/lapse_leak={rate}"])
        c[f"T3-{tag}-rho"] = (new, b, ball_args() + [f"z4c/lapse_leak={rate}",
                                                    f"z4c/lapse_leak_rho={RHO_BALL}"])
    return c


def run(name, spec, out, threads):
    exe, inp, args = spec
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    if os.path.exists(os.path.join(d, "DONE")):
        return name, 0
    if name.startswith("T2"):
        subprocess.run([sys.executable, os.path.join(WT, "cosmo/ic/make_lattice.py"),
                        "--n", "32", "--ppc", "1", "--L", "4.0", "--H0", "1.0", "--out", d],
                       check=True, capture_output=True)
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false")
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run([exe, "-i", inp, "-d", d] + args, cwd=d, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    if rc == 0:
        open(os.path.join(d, "DONE"), "w").close()
    return name, rc


def payload(path):
    """Bytes of a file after the embedded parameter dump, if it has one."""
    with open(path, "rb") as f:
        b = f.read()
    i = b.find(b"<par_end>")
    return b if i < 0 else b[i:]


def compare(a, b, skip=("athena.log", "DONE")):
    """Files of two run directories: identical, identical after the parameter dump,
    different, present in one only."""
    res = dict(identical=[], payload=[], different=[], only=[])
    fa = {os.path.relpath(os.path.join(r, f), a) for r, _, fs_ in os.walk(a) for f in fs_}
    fb = {os.path.relpath(os.path.join(r, f), b) for r, _, fs_ in os.walk(b) for f in fs_}
    for f in sorted(fa | fb):
        if os.path.basename(f) in skip or f.endswith(".athinput"):
            continue
        if f not in fa or f not in fb:
            res["only"].append(f)
        elif filecmp.cmp(os.path.join(a, f), os.path.join(b, f), shallow=False):
            res["identical"].append(f)
        elif payload(os.path.join(a, f)) == payload(os.path.join(b, f)):
            res["payload"].append(f)
        else:
            res["different"].append(f)
    return res


def hst(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                names = [tok.split("=")[1] for tok in line[1:].split() if "=" in tok]
    data = np.loadtxt(path, ndmin=2)
    return {n: data[:, i] for i, n in enumerate(names)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--rel", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only", default="T1,T2,T3")
    a = ap.parse_args()
    a.new, a.rel, a.out = (os.path.abspath(p) for p in (a.new, a.rel, a.out))
    os.makedirs(a.out, exist_ok=True)
    sel = a.only.split(",")
    todo = {k: v for k, v in cases(a.new, a.rel).items() if k.split("-")[0] in sel}
    res = dict(runs={}, checks={})
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for name, rc in ex.map(lambda k: run(k, todo[k], a.out, a.threads), todo):
            res["runs"][name] = rc
            print(f"{name}: exit {rc}", flush=True)
    d = lambda k: os.path.join(a.out, k)                                   # noqa: E731
    ok = True

    def check(name, passed, text):
        nonlocal ok
        res["checks"][name] = dict(passed=bool(passed), detail=text)
        ok = ok and bool(passed)
        print(("PASS " if passed else "FAIL ") + name + ": " + text)

    if "T1" in sel:
        c = compare(d("T1-plain"), d("T1-rho"))
        check("T1 restricted to matter = plain 1+log",
              not c["different"] and not c["only"] and (c["identical"] or c["payload"]),
              f"{len(c['identical'])} files identical, {len(c['payload'])} identical after the "
              f"parameter dump, different {c['different']}, in one run only {c['only']}")
        c = compare(d("T1-plain"), d("T1-leak"))
        h0, h1 = hst(d("T1-plain/v1s.nrpic.hst")), hst(d("T1-leak/v1s.nrpic.hst"))
        key = [k for k in h0 if "alpha" in k and "max" in k]
        amax = {k: (float(h0[k].max()), float(h1[k].max())) for k in key}
        check("T1 first pass differs from plain 1+log (term active)", len(c["different"]) > 0,
              f"{len(c['different'])} files differ; largest lapse (plain, first pass) {amax}")
        c = compare(d("T1-plain-tr"), d("T1-hole"))
        check("T1 switched off around the tracker (radius beyond the mesh) = plain 1+log",
              not c["different"] and not c["only"],
              f"{len(c['identical'])} identical, {len(c['payload'])} after the dump, "
              f"different {c['different']}, only {c['only']}")
        c = compare(d("T1-plain"), d("T1-plain-tr"))
        check("T1 a tracker alone changes no shared file",
              not c["different"],
              f"{len(c['identical'])} identical, {len(c['payload'])} after the dump, "
              f"different {c['different']}, only in one {c['only']}")
        h2, h3 = hst(d("T1-leak-tr/v1s.z4c.user.hst")), hst(d("T1-onset/v1s.z4c.user.hst"))
        dev = max(float(np.max(np.abs(h2[k] - h3[k]) / (np.abs(h2[k]) + 1e-300)))
                  for k in h2 if k not in ("time", "dt"))
        check("T1 onset of width 1e-9 = kink to rounding", dev < 1e-6,
              f"largest relative difference of the constraint history {dev:.2e}")
    if "T2" in sel:
        h0, h1 = hst(d("T2-first/flrwleak.nrpic.hst")), hst(d("T2-rho/flrwleak.nrpic.hst"))
        dev = {k: float(np.max(np.abs(h0[k] - h1[k]) / (np.abs(h0[k]) + 1e-300)))
               for k in ("alpha_max", "alpha_min", "proper_volume")}
        check("T2 homogeneous universe: restricted to matter = first pass",
              max(dev.values()) < 1e-10,
              f"largest relative differences {dev}; lapse at the end {h1['alpha_max'][-1]:.6f}")
    if "T3" in sel:
        import idlib                                   # noqa: F401
        import test2_evolution as t2
        from lapse_ref import central_lapse
        from nrpic import figstyle as fs
        import matplotlib.pyplot as plt
        ball = {}
        for tag, rate in (("leak1", 1.0), ("leak05", 2.0)):
            c = compare(d(f"T3-{tag}-rel"), d(f"T3-{tag}"))
            check(f"T3 {tag}: first pass, new executable = release", not c["different"]
                  and not c["only"] and len(c["identical"]) > 0,
                  f"{len(c['identical'])} files identical, {len(c['payload'])} after the "
                  f"dump, different {c['different']}, only {c['only']}")
            for var in ("", "-rho"):
                name = f"T3-{tag}{var}"
                man = dict(output_directory=d(name), command=todo[name][2],
                           inputs=[dict(path=f"{IC}/t2_sharp_h1.json")], run_id=name)
                dd = t2.load(man)
                g = t2.gauge_numbers(dd)
                t = np.array(g["t"])
                rt, rtau, ra, ral = central_lapse(dd["ball"], 1.0 / rate, float(t[-1]), dt=0.01)
                ref = np.interp(t, rt, ral)
                rel = np.abs(np.array(g["alpha_centre"]) / ref - 1.0)
                grp = t2.group_numbers(dd)
                ball[name] = dict(
                    groups={k: grp[k]["maxabs_all"] for k in ("core", "mid", "outer", "surface")
                            if k in grp},
                    alpha_dev=float(rel.max()), t_dev=float(t[int(np.argmax(rel))]),
                    alpha_max=float(max(g["alpha_max"])), c_max=float(max(g["light_speed_max"])),
                    d=dd, g=g, ref=ref)
                print(f"  {name:16s} largest |eps| " + " ".join(
                    f"{k} {v:.2e}" for k, v in ball[name]["groups"].items())
                    + f"; central lapse within {rel.max():.3f} of homogeneous (t = "
                    f"{ball[name]['t_dev']:.2f}); largest lapse {ball[name]['alpha_max']:.3f}; "
                    f"largest coordinate light speed {ball[name]['c_max']:.3f}")
        for tag in ("leak1", "leak05"):
            a0, a1 = ball[f"T3-{tag}"], ball[f"T3-{tag}-rho"]
            worst = max(a1["groups"][k] / a0["groups"][k] for k in a0["groups"])
            check(f"T3 {tag}: shells with the restriction within a factor 2 of the first pass",
                  worst <= 2.0, f"largest ratio of the group errors {worst:.2f}; core "
                  f"{a1['groups']['core']:.2e} against {a0['groups']['core']:.2e}")
            check(f"T3 {tag}: central lapse with the restriction within 5 per cent of homogeneous",
                  a1["alpha_dev"] <= 0.05, f"{a1['alpha_dev']:.3f} (first pass {a0['alpha_dev']:.3f})")
        fs.use_style()
        fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0))
        fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.96, wspace=0.36,
                            hspace=0.28)
        sty = {"T3-leak1": (fs.PAL["blue"], "-", r"first pass, $T=1\,M$"),
               "T3-leak1-rho": (fs.PAL["blue"], "--", r"matter only, $T=1\,M$"),
               "T3-leak05": (fs.PAL["red"], "-", r"first pass, $T=0.5\,M$"),
               "T3-leak05-rho": (fs.PAL["red"], "--", r"matter only, $T=0.5\,M$")}
        for name, (c, ls, lab) in sty.items():
            b = ball[name]
            g, dd = b["g"], b["d"]
            ax[0, 0].plot(g["t"], g["alpha_centre"], color=c, ls=ls, label=lab)
            ax[0, 1].plot(g["t"], g["alpha_max"], color=c, ls=ls)
            reg = t2.region_constraints(dd)
            if reg:
                ax[0, 2].plot(reg[-1]["profile"]["r"], reg[-1]["profile"]["alpha"], color=c, ls=ls)
                ax[0, 2].axvline(reg[-1]["r_surface"], color="0.7", lw=0.6)
            for axx, grp in zip(ax[1], ("core", "outer", "surface")):
                idx = dd["groups"][grp]
                axx.plot(dd["tau"][:, idx].mean(axis=1), np.abs(dd["eps"][:, idx]).max(axis=1),
                         color=c, ls=ls)
        for name in ("T3-leak1", "T3-leak05"):
            ax[0, 0].plot(ball[name]["g"]["t"], ball[name]["ref"], color="k", ls=":", lw=0.8)
        ax[0, 0].plot([], [], color="k", ls=":", lw=0.8, label="homogeneous")
        ax[0, 0].legend(fontsize=6.5)
        ax[0, 0].set_ylabel("lapse at the centre")
        ax[0, 1].set_ylabel("largest lapse on the mesh")
        ax[0, 2].set_ylabel("lapse at the last dump (shell means)")
        ax[0, 2].set_xlabel(r"coordinate radius $r/M$", labelpad=1)
        for k in (0, 1):
            ax[0, k].set_xlabel(r"coordinate time $t/M$", labelpad=1)
        for axx, grp in zip(ax[1], ("core", "outer", "surface")):
            axx.set_yscale("log")
            axx.set_ylim(1e-5, 1.0)
            axx.set_xlabel(r"proper time $\tau/M$", labelpad=1)
            axx.set_title(f"{grp} shells", fontsize=9)
        ax[1, 0].set_ylabel(r"largest $|R/R_{\rm exact}-1|$")
        fs.save(fig, os.path.join(a.out, "ptests_ball"))
        plt.close(fig)
        res["ball"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("d", "g", "ref")}
                       for k, v in ball.items()}
    res["verdict"] = "PASS" if ok and all(rc == 0 for rc in res["runs"].values()) else "FAIL"
    with open(os.path.join(a.out, "ptests.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    print("verdict:", res["verdict"])


if __name__ == "__main__":
    main()
