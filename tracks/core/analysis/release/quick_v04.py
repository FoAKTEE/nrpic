#!/usr/bin/env python3
"""Quick tests of release candidate core-v0.4 on processors: one example per merged
branch (the input its READY names), run with the merged executable and with the
executable the branch published, compared byte for byte, and one physical number per
example against the value the READY of the branch states.

    quick_v04.py --new ATHENA --out DIR [--cores N] [--tests lw16,...] [--exe-dir DIR]

Tests (branch): lw16, lw32 (requests-b: oblique linear wave, 16 and 32 cells), leak, eta
(gauge: lapse relaxation in the homogeneous universe; tracker-dependent shift damping,
two steps), sr (scalar-2: stochastic slice and sources, 12 steps), clump, clump0
(clump-curvature: moving Gaussian with and without its curvature, one step), ids
(id-solver: Gaussian at rest, 32 cells), tracer (requests-adf: m = 0 on a circular
orbit, 300 M), pert, coll (collisions-2: perturbing force; collisions with the metric at
each particle in a static well, 20 steps).  lw32 and clump0 run with the merged
executable only (they serve the convergence order and the ratio).

Classes of the byte comparison: regress_v04.py (identical, a, b, a+b, other).  Files
that the preparation of a run directory wrote before AthenaK started (particle files
and the generator's records, which hold the directory name) are not output: they are
listed in DIR/<test>/<new|branch>.prepared.json and reported under "prepared".  Writes
DIR/summary.json and DIR/fig_quick_v04.{pdf,png}.  Exit status 0 if every run ended with
status 0, no file is of class "other" and every number lies inside its band.
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
import regress_v04 as rg                      # noqa: E402

EXE_DIR = "/data/haiyangw/nrpic/scratch/core/exe"
PROB = os.path.join(REPO, "problems")
N16 = ["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=16",
       "meshblock/nx2=16", "meshblock/nx3=16"]


def sh(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL)


def prep_leak(d):
    sh([sys.executable, os.path.join(REPO, "cosmo/ic/make_lattice.py"), "--n", "32",
        "--ppc", "1", "--L", "4.0", "--H0", "1.0", "--out", d], d)
    return []


def prep_clump(d):
    sh([sys.executable, os.path.join(PROB, "ic/make_ic.py"), "clumps", "--gaussian",
        "0.2,1,0,0,0,0.06,0,0", "--sampler", "lattice", "--lattice-h", "0.25", "--seed",
        "1", "--out", d, "--prefix", "particles"], d)
    with open(os.path.join(d, "particles.json")) as f:
        p = json.load(f)["athenak"]["problem"]
    return ["problem/comp0_p1=%r" % p["comp0_p1"]]


def prep_clump0(d):
    prep_clump(d)
    return ["problem/comp0_p1=0.0"]


def prep_ids(d):
    sh([sys.executable, os.path.join(PROB, "idsolve/make_ic.py"), "gaussian", "--h",
        "0.5", "--out", d], d)
    return []


def prep_coll(d):
    sh([sys.executable, "make_static_example.py", os.path.join(d, "box.nrp")],
       os.path.join(REPO, "tracks/core/analysis/collisions"))
    return []


# name -> (branch or None, input, preparation or None, arguments)
TESTS = {
    "lw16": ("requests-b", "tests/lw_oblique.athinput", None, N16),
    "lw32": (None, "tests/lw_oblique.athinput", None, []),
    "leak": ("gauge", "cosmo/flrw_leak.athinput", prep_leak, ["z4c/lapse_leak=5.0"]),
    "eta": ("gauge", "puncture/by_eta.athinput", None,
            ["z4c/shift_eta=20.0", "z4c/shift_eta_profile=true", "z4c/shift_eta_mref=0.1",
             "time/nlim=2"]),
    "sr": ("scalar-2", "scalar/sr_stochastic.athinput", None,
           ["scalar_field/noise_mode_file=" + PROB + "/scalar/sr_stochastic_modes.txt",
            "time/nlim=12"]),
    "clump": ("clump-curvature", "clump/clump_moving.athinput", prep_clump,
              ["time/nlim=1"]),
    "clump0": (None, "clump/clump_moving.athinput", prep_clump0, ["time/nlim=1"]),
    "ids": ("id-solver", "idsolve/gaussian.athinput", prep_ids,
            ["mesh/nx1=32", "mesh/nx2=32", "mesh/nx3=32",
             "particles/particle_file=gauss_h0p5.nrp"]),
    "tracer": ("requests-adf", "tests/tracer_mesh_circular.athinput", None, []),
    "pert": ("collisions-2", "tests/perturb_flat.athinput", None, []),
    "coll": ("collisions-2", "tests/coll_box_static.athinput", prep_coll,
             ["particles/coll_sigma=16.0", "time/nlim=20"]),
}


def run(exe, d, name):
    _, inp, prep, args = TESTS[name]
    os.makedirs(d, exist_ok=True)
    extra = prep(d) if prep else []
    # what the preparation wrote (particle files and their records) is no output of
    # AthenaK: listed here, beside the run directory, and compared separately
    with open(d + ".prepared.json", "w") as f:
        json.dump(rg.out_files(d), f)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run([exe, "-i", os.path.join(PROB, inp), "-d", d] + args + extra,
                            cwd=d, stdout=log, stderr=subprocess.STDOUT,
                            env=env).returncode
    return rc, round(time.time() - t0, 1)


def prepared_files(d):
    """files the preparation wrote into run directory d (empty for runs of the driver
    before it kept the list)."""
    try:
        with open(d + ".prepared.json") as f:
            return json.load(f)
    except OSError:
        return []


def same_bytes(a, b):
    try:
        with open(a, "rb") as fa, open(b, "rb") as fb:
            return fa.read() == fb.read()
    except OSError:
        return False


def hst(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                names = [tok.split("=", 1)[1] for tok in line[1:].split() if "]=" in tok]
    data = np.atleast_2d(np.loadtxt(path))
    return {n: data[:, i] for i, n in enumerate(names)}


def leak_reference(rate, tmax, dt=1.0e-4):
    """(t, alpha, a) of d ln(alpha)/dt = 6 H - rate max(ln alpha, 0), d tau/dt = alpha,
    H = 1/(1 + 3 tau/2) (the homogeneous dust universe, H_0 = 1), by RK4."""
    def rhs(y):
        return np.array([6.0/(1.0 + 1.5*y[1]) - rate*max(y[0], 0.0), np.exp(y[0])])
    y = np.zeros(2)
    out = [(0.0, 1.0, 1.0)]
    for i in range(int(round(tmax/dt))):
        k1 = rhs(y)
        k2 = rhs(y + 0.5*dt*k1)
        k3 = rhs(y + 0.5*dt*k2)
        k4 = rhs(y + dt*k3)
        y = y + dt*(k1 + 2*k2 + 2*k3 + k4)/6.0
        out.append(((i + 1)*dt, np.exp(y[0]), (1.0 + 1.5*y[1])**(2.0/3.0)))
    return np.array(out)


def evaluate(out, have):
    """numbers of the merged executable's runs; each entry: value, band, source of the
    band (READY of the branch), inside or not."""
    num, curves = {}, {}

    def put(key, value, lo, hi, src):
        num[key] = {"value": float(value), "band": [lo, hi], "from": src,
                    "inside": bool(lo <= value <= hi)}

    if "lw16" in have and "lw32" in have:
        e = {}
        for n in (16, 32):
            row = np.loadtxt(os.path.join(out, "lw%d" % n, "new", "lwo-errs.dat"))
            e[n] = float(np.atleast_2d(row)[-1, 4])
        curves["lw"] = e
        put("lw_order_16_32", np.log2(e[16]/e[32]), 3.0, 13.0,
            "requests-b READY 1: the scheme converges (sixth-order differences)")
    if "leak" in have:
        h = hst(os.path.join(out, "leak", "new", "flrwleak.nrpic.hst"))
        ref = leak_reference(5.0, float(h["time"][-1]))
        al = np.interp(h["time"], ref[:, 0], ref[:, 1])
        err = np.abs(h["alpha_max"]/al - 1.0)
        curves["leak"] = {"t": h["time"].tolist(), "alpha": h["alpha_max"].tolist(),
                          "ref_t": ref[::200, 0].tolist(), "ref": ref[::200, 1].tolist(),
                          "err": err.tolist()}
        put("leak_max_rel_err_alpha", err.max(), 0.0, 2.0e-5,
            "gauge READY 1, test H: 6e-6 for T = 0.2/H_0")
    if "sr" in have:
        h = hst(os.path.join(out, "sr", "new", "sr.sf.con.hst"))
        kh = [k for k in h if k.startswith("<|H|/[H]>")][0]
        km = [k for k in h if k.startswith("<|M|/[M]>")][0]
        curves["sr"] = {"N": h["efolds=-ln<chi>/2"].tolist(), "H": h[kh].tolist(),
                        "M": h[km].tolist()}
        put("sr_H_ratio_start", h[kh][0], 2.0e-12, 3.2e-12,
            "scalar-2 READY: initial 2.6e-12")
        put("sr_M_ratio_start", h[km][0], 1.40e-5, 1.52e-5,
            "scalar-2 READY: initial 1.46e-5")
    if "clump" in have and "clump0" in have:
        m1 = hst(os.path.join(out, "clump", "new", "clump.z4c.user.hst"))["M-norm2"][0]
        m0 = hst(os.path.join(out, "clump0", "new", "clump.z4c.user.hst"))["M-norm2"][0]
        curves["clump"] = {"with": float(m1), "without": float(m0)}
        put("clump_M_ratio_64", np.sqrt(m1/m0), 0.0, 0.05,
            "clump-curvature READY: 0.019 of the uncorrected norm at 64 cells")
    if "ids" in have:
        rec = np.loadtxt(os.path.join(out, "ids", "new", "gauss.idsolve.txt"))
        curves["ids"] = {"iter": rec[:, 0].tolist(), "rel": rec[:, 1].tolist(),
                         "maxH": rec[:, 4].tolist()}
        put("ids_iterations", rec[-1, 0], 10, 30, "id-solver READY V4: 17 at 64 cells")
        put("ids_maxH_after", rec[-1, 4], 0.0, 5.0e-11,
            "id-solver READY T1: 1.5e-11 to 2.6e-11")
    if "tracer" in have:
        a = np.fromfile(os.path.join(out, "tracer", "new", "trc.traj.bin")).reshape(-1, 8)
        r = np.linalg.norm(a[:, 2:5], axis=1)
        curves["tracer"] = {"t": a[::10, 0].tolist(), "r": r[::10].tolist()}
        put("tracer_r_min", r.min(), 7.9999, 8.0001,
            "requests-adf READY 1: r in [7.999998, 8.001151] M")
        put("tracer_r_max", r.max(), 8.0000, 8.0013, "the same")
        put("tracer_t_end", a[-1, 0], 299.9, 300.1, "the tracer stays for 300 M")
    if "coll" in have:
        h = hst(os.path.join(out, "coll", "new", "box.coll.hst"))
        rel = np.abs(h["dH_particles"])/h["sum_MH_particles"]
        curves["coll"] = {"cycle": h["ncycle"].tolist(), "rel": rel.tolist(),
                          "n_coll": h["n_coll"].tolist()}
        put("coll_sum_dH_over_H", np.abs(h["dH_particles"].sum())/h["sum_MH_particles"][0],
            0.0, 1.0e-14, "collisions-2 READY 1: 3.2e-16 over 20 steps")
        put("coll_n_noroot", h["n_noroot"].sum(), 0, 0, "collisions-2 READY 1: none")
        put("coll_collisions", h["n_coll"].sum(), 1.0e5, 2.0e5,
            "collisions-2 READY 1: 141140")
    return num, curves


def figure(out, curves):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.09, top=0.94, wspace=0.62,
                        hspace=0.48)
    red, blue = fs.PAL["red"], fs.PAL["blue"]
    a = ax[0, 0]
    if "lw" in curves:
        n = np.array([16.0, 32.0])
        e = np.array([curves["lw"][16], curves["lw"][32]])
        a.loglog(n, e, "o-", color=red, label="merged")
        a.loglog(n, e[0]*(n/16.0)**-6, label=r"$N^{-6}$", **fs.GUIDE)
        a.set_xticks([16, 32])
        a.set_xticklabels(["16", "32"])
        a.minorticks_off()
        a.legend()
    a.set_xlabel("cells per side $N$", labelpad=2)
    a.set_ylabel(r"$L_1$ error of $\tilde\gamma_{ij}$")
    a.set_title("oblique wave, one period", fontsize=10)
    a = ax[0, 1]
    if "leak" in curves:
        c = curves["leak"]
        a.plot(c["ref_t"], c["ref"], color=blue, label="exact (ODE)")
        a.plot(c["t"], c["alpha"], color=red, ls="--", label="merged")
        a.legend(loc="lower right")
        b = a.twinx()
        b.semilogy(c["t"][1:], np.maximum(c["err"][1:], 1e-16), color="grey", lw=1.0)
        a.text(0.97, 0.96, "grey, right axis:\nrelative error", transform=a.transAxes,
               ha="right", va="top", fontsize=8, color="grey")
    a.set_xlabel(r"time $t\,H_0$", labelpad=2)
    a.set_ylabel(r"lapse $\alpha$")
    a.set_title(r"lapse relaxation, $T=0.2/H_0$", fontsize=10)
    a = ax[0, 2]
    if "sr" in curves:
        c = curves["sr"]
        a.semilogy(c["N"], c["H"], color=red, label=r"$\langle|H|/[H]\rangle$")
        a.semilogy(c["N"], c["M"], color=red, ls="--", label=r"$\langle|M|/[M]\rangle$")
        a.axhline(2.6e-12, **fs.MASK_LINE)
        a.axhline(1.46e-5, **fs.MASK_LINE)
        a.legend(loc="center right")
    a.set_xlabel("e-folds", labelpad=2)
    a.set_ylabel("constraint ratio")
    a.set_title("stochastic slice and sources", fontsize=10)
    a = ax[1, 0]
    if "ids" in curves:
        c = curves["ids"]
        a.semilogy(c["iter"], c["rel"], "o-", ms=3, color=red, label="residual / scale")
        a.semilogy(c["iter"], c["maxH"], "s--", ms=3, color=red, label=r"max$|H|$")
        a.axhline(1.0e-10, **fs.GUIDE)
        a.legend()
    a.set_xlabel("outer iteration", labelpad=2)
    a.set_ylabel("initial-data solve")
    a.set_title("Gaussian at rest, 32 cells", fontsize=10)
    a = ax[1, 1]
    if "tracer" in curves:
        c = curves["tracer"]
        a.plot(c["t"], (np.array(c["r"]) - 8.0)*1.0e3, color=red, label="merged")
        a.axhline(0.0, color=blue, label="circular orbit")
        a.legend(loc="upper left")
    a.set_xlabel(r"time $t/M$", labelpad=2)
    a.set_ylabel(r"$(r - 8M)/10^{-3}M$")
    a.set_title(r"tracer ($m=0$), mesh metric", fontsize=10)
    a = ax[1, 2]
    if "coll" in curves:
        c = curves["coll"]
        a.semilogy(c["cycle"], np.maximum(c["rel"], 1e-20), "o", ms=3, color=red)
        a.axhline(2.2e-16, **fs.GUIDE)
    a.set_xlabel("step", labelpad=2)
    a.set_ylabel(r"$|\Delta\sum MH|/\sum MH$ per step")
    a.set_title("collisions, particle metric", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_quick_v04"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--tests", default=",".join(TESTS))
    ap.add_argument("--exe-dir", default=EXE_DIR,
                    help="directory of the published branch executables")
    ap.add_argument("--analyse-only", action="store_true",
                    help="reuse the runs in --runs (exit codes from its summary.json)")
    ap.add_argument("--runs", default=None,
                    help="with --analyse-only: directory of an earlier call whose runs "
                         "are compared and evaluated again (default: --out)")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    # where the runs are: --out, or the directory of an earlier call
    runs = os.path.abspath(a.runs) if (a.analyse_only and a.runs) else out
    names = a.tests.split(",")
    new = os.path.abspath(a.new)
    jobs = []
    for n in names:
        jobs.append((n, "new", new))
        if TESTS[n][0]:
            jobs.append((n, "branch", os.path.join(a.exe_dir, "core_" + TESTS[n][0],
                                                    "athena_cpu")))
    codes, walls = {}, {}
    if a.analyse_only:
        with open(os.path.join(runs, "summary.json")) as f:
            old = json.load(f)["tests"]
        for n, lab, _ in jobs:
            codes[(n, lab)] = old[n]["exit"][lab]
            walls[(n, lab)] = old[n]["wall_time_s"][lab]
    else:
        with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
            futs = {pool.submit(run, exe, os.path.join(runs, n, lab), n): (n, lab)
                    for n, lab, exe in jobs}
            for fut in cf.as_completed(futs):
                codes[futs[fut]], walls[futs[fut]] = fut.result()
                print("ran %-7s %-6s exit %d  %.1f s" % (futs[fut] + (codes[futs[fut]],
                                                                    walls[futs[fut]])),
                      flush=True)
    summary = {"new": new, "sha256_new": rg.sha256(new), "runs": runs, "tests": {}}
    ok = True
    for n in names:
        br = TESTS[n][0]
        t = {"branch": br, "input": "problems/" + TESTS[n][1], "args": TESTS[n][3],
             "exit": {"new": codes[(n, "new")]},
             "wall_time_s": {"new": walls[(n, "new")]}}
        good = codes[(n, "new")] == 0
        if br:
            t["exit"]["branch"] = codes[(n, "branch")]
            t["wall_time_s"]["branch"] = walls[(n, "branch")]
            exe_b = os.path.join(a.exe_dir, "core_" + br, "athena_cpu")
            t["branch_exe"] = exe_b
            t["sha256_branch"] = rg.sha256(exe_b)
            db, dn = os.path.join(runs, n, "branch"), os.path.join(runs, n, "new")
            prepared = sorted(set(prepared_files(db)) | set(prepared_files(dn)))
            res = rg.compare(n, db, dn, skip=prepared)
            t.update({k: res[k] for k in ("identical", "a", "b", "a+b", "other", "details",
                                          "files")})
            t["prepared"] = {f: same_bytes(os.path.join(db, f), os.path.join(dn, f))
                             for f in prepared}
            good = good and codes[(n, "branch")] == 0 and not res["other"] \
                and res["files"] > 0
            print("%-7s vs core/%-15s files %3d  identical %3d  a %d  b %d  a+b %d  "
                  "other %d" % (n, br, res["files"], len(res["identical"]), len(res["a"]),
                                len(res["b"]), len(res["a+b"]), len(res["other"])),
                  flush=True)
            for f in res["other"]:
                print("        other: %s %s" % (f, res["details"].get(f, "")), flush=True)
            for f, same in t["prepared"].items():
                print("        prepared, not compared as output: %s (%s in the two "
                      "directories)" % (f, "equal" if same else "differs"), flush=True)
        t["verdict"] = "pass" if good else "FAIL"
        ok = ok and good
        summary["tests"][n] = t
    have = [n for n in names if codes[(n, "new")] == 0]
    num, curves = evaluate(runs, have)
    summary["numbers"] = num
    for k, v in num.items():
        print("%-24s %.6g  band [%g, %g]  %s" % (k, v["value"], v["band"][0], v["band"][1],
                                                "inside" if v["inside"] else "OUTSIDE"),
              flush=True)
        ok = ok and v["inside"]
    summary["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    figure(out, curves)
    print("QUICK TESTS", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
