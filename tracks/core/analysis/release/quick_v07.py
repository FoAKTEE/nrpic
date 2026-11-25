#!/usr/bin/env python3
"""Quick tests of release candidate core-v0.7 on processors: one example per merged
branch from its READY against the executable the branch published, the released path
against the release before where a kernel was recompiled, the combinations the merge
creates, the stop on SIGTERM and the chain script.

    quick_v07.py --new ATHENA --base ATHENA_V06 --out DIR [--cores N]
                 [--groups noise,step,gauge,clump,combo,term,chain] [--redraw OLDDIR]

Group noise (Qn; branch executable core_noise-level2/athena_cpu):
  n_l2      problems/scalar/sr_stochastic_l2.athinput (32^3, level 2, every option of
            the branch written out), 24 cycles
Group step (Qs; branch executable core_step-limit/athena_cpu):
  s_lim     problems/tests/z4c_step_limit.athinput as written (dt_gauge = 0.9)
  s_off     the same with z4c/dt_gauge=0.0, candidate only: the warning and the guard
            stop (exit status 3) are expected
Group gauge (Qg; tracks/core/analysis/gauge2/inputs/v8_var.athinput on the coarse vacuum
  mesh of the package's test T7: no refinement, 64^3 cells of 2 M, 10 M, lapse_leak = 0.5)
  g_hole    lapse_leak_hole = 8: against core_gauge-2/athena_cpu
  g_leak    lapse_leak_hole = 0 (the first pass): against the release (--base)
Group clump (Qc; branch executable core_clump-table/athena_cpu, a core-v0.5 source):
  c_static  problems/tests/clump_table_static.athinput at 32 cells, v = 0.3, curvature
            of the boost table and the correction of psi (initial data only)
  c_solve   problems/tests/clump_table_idsolve.athinput at 32 cells, candidate only:
            status and the record of the solve (the far field of core-v0.6 acts)
Group combo (C; candidate only):
  x_l2dt    n_l2 with <z4c> dt_gauge = 0.9
  x_holedt  g_hole with <z4c> dt_gauge = 0.9
Group term: tracks/core/analysis/preempt/term_test.py --cases S1,S2 with the candidate
Group chain: scripts/tests/test_submit_chain.py
Every file AthenaK writes is compared byte for byte (classes of regress_v04.py).
Writes DIR/summary.json and DIR/fig_quick_v07.{pdf,png}; exit status 0 if every
expectation above holds.
"""
import argparse
import concurrent.futures as cf
import glob
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(HERE, "..", "cosmo_amr"))
import regress_v04 as rg                      # noqa: E402
import amrlib as A                            # noqa: E402

EXE_DIR = "/data/haiyangw/nrpic/scratch/core/exe"
PROB = os.path.join(REPO, "problems")
VDATA = "/data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-170213-d2c2131/v1"


def deck_noise(d, dtg):
    b = A.Inp(os.path.join(PROB, "scalar/sr_stochastic_l2.athinput"))
    b.set("scalar_field",
          noise_mode_file=os.path.join(PROB, "scalar/sr_stochastic_modes.txt"))
    b.set("time", nlim=24)
    if dtg:
        b.set("z4c", dt_gauge=0.9)
    return b


def deck_step(d, off):
    b = A.Inp(os.path.join(PROB, "tests/z4c_step_limit.athinput"))
    if off:
        b.set("z4c", dt_gauge=0.0)
    return b


def deck_gauge(d, hole, dtg):
    b = A.Inp(os.path.join(HERE, "..", "gauge2", "inputs", "v8_var.athinput"))
    b.set("mesh_refinement", refinement="none")
    b.set("time", tlim=10.0)
    b.set("particles", particle_file=os.path.join(VDATA, "v1.nrp"))
    b.set("problem", comp0_file=os.path.join(VDATA, "v1.tab"))
    b.set("z4c", lapse_leak=0.5, lapse_leak_hole=hole)
    if dtg:
        b.set("z4c", dt_gauge=0.9)
    return b


def clump_ic(d):
    """tables and lattice of the moving cluster (header of clump_table_static.athinput)"""
    js = os.path.join(d, "cluster.json")
    if not os.path.exists(js):
        subprocess.run([sys.executable, os.path.join(PROB, "ic/make_ic.py"), "boosted",
                        "--cluster", "0.819,1,0,0,0,0.3,0,0", "--sampler", "quiet",
                        "--lattice-h", "0.25", "--prefix", "cluster", "--out", d],
                       check=True, stdout=subprocess.DEVNULL)
    with open(js) as f:
        return json.load(f)


def deck_clump(d, solve):
    meta = clump_ic(d)
    name = "clump_table_idsolve.athinput" if solve else "clump_table_static.athinput"
    b = A.Inp(os.path.join(PROB, "tests", name))
    pr = dict(meta["athenak"]["problem"]) if "athenak" in meta else {}
    b.set("mesh", nx1=32, nx2=32, nx3=32)
    b.set("particles", particle_file=os.path.join(d, "cluster.nrp"))
    kv = dict(comp0_file=os.path.join(d, "cluster_c0.tab"),
              comp0_boost_file=os.path.join(d, "cluster_c0.bst"),
              comp0_corr_file=os.path.join(d, "cluster_c0_corr.tab"),
              comp0_corr="table")
    for k in ("comp0_p1", "comp0_p2", "comp0_p3"):
        kv[k] = pr.get(k, 0.3145 if k.endswith("1") else 0.0)
    b.set("problem", **kv)
    return b


# name -> (group, deck maker, executables, expected exit status)
CASES = {
    "n_l2": ("noise", lambda d: deck_noise(d, False), ["new", "noise"], 0),
    "s_lim": ("step", lambda d: deck_step(d, False), ["new", "step"], 0),
    "s_off": ("step", lambda d: deck_step(d, True), ["new"], 3),
    "g_hole": ("gauge", lambda d: deck_gauge(d, 8.0, False), ["new", "gauge"], 0),
    "g_leak": ("gauge", lambda d: deck_gauge(d, 0.0, False), ["new", "base"], 0),
    "c_static": ("clump", lambda d: deck_clump(d, False), ["new", "clump"], 0),
    "c_solve": ("clump", lambda d: deck_clump(d, True), ["new"], 0),
    "x_l2dt": ("combo", lambda d: deck_noise(d, True), ["new"], 0),
    "x_holedt": ("combo", lambda d: deck_gauge(d, 8.0, True), ["new"], 0),
}


def run_one(job):
    name, who, exe, top = job
    d = os.path.join(top, name, who)
    os.makedirs(d, exist_ok=True)
    CASES[name][1](os.path.join(top, name)).write(os.path.join(d, "in.athinput"))
    rc, sec = rg.run(exe, d, (os.path.join(d, "in.athinput"), [], []))
    return name, who, rc, sec


def compare(da, db):
    fa, fb = rg.out_files(da), rg.out_files(db)
    cls, other = {}, []
    for f in sorted(set(fa) | set(fb)):
        if f == "in.athinput":
            continue
        if f not in fa or f not in fb:
            c, info = "other", {"why": "in one run only"}
        else:
            with open(os.path.join(da, f), "rb") as x, open(os.path.join(db, f), "rb") as y:
                c, info = rg.classify(f, x.read(), y.read())
        cls[c] = cls.get(c, 0) + 1
        if c != "identical":
            other.append([f, c, info])
    return cls, other


def log_lines(d, key):
    p = os.path.join(d, "athena.log")
    if not os.path.exists(p):
        return []
    with open(p, errors="replace") as f:
        return [ln.rstrip() for ln in f if key in ln]


def hist_finite(d):
    ok, n = True, 0
    for p in glob.glob(os.path.join(d, "*.hst")):
        try:
            a = np.atleast_2d(np.loadtxt(p))
        except ValueError:
            return False, n
        n += 1
        ok = ok and bool(np.isfinite(a).all())
    return ok, n


def figure(rep, out):
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.6))
    names = list(rep["byte"])
    y = np.arange(len(names))
    tot = [rep["byte"][c]["n_files"] for c in names]
    same = [rep["byte"][c]["classes"].get("identical", 0) for c in names]
    axs[0].barh(y, tot, color=fs.PAL["red"], label="files compared")
    axs[0].barh(y, same, color=fs.PAL["blue"], label="byte-identical")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(["%s (%s)" % (c, rep["byte"][c]["against"]) for c in names],
                           fontsize=6)
    axs[0].invert_yaxis()
    axs[0].set_xlabel("files")
    axs[0].set_xlim(0, 1.45*max(tot + [1]))
    axs[0].legend(fontsize=5, loc="lower right")
    axs[0].set_title("(a) candidate against branch or release", fontsize=7)
    ck = list(rep["checks"])
    yy = np.arange(len(ck))
    val = [1.0 if rep["checks"][c]["ok"] else 0.0 for c in ck]
    axs[1].barh(yy, [1.0]*len(ck), color=fs.PAL["red"])
    axs[1].barh(yy, val, color=fs.PAL["blue"])
    axs[1].set_yticks(yy)
    axs[1].set_yticklabels(ck, fontsize=5)
    axs[1].invert_yaxis()
    axs[1].set_xticks([0, 1])
    axs[1].set_xticklabels(["fails", "holds"], fontsize=6)
    axs[1].set_title("(b) other expectations (blue: held)", fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_quick_v07"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=3)
    ap.add_argument("--groups", default="noise,step,gauge,clump,combo,term,chain")
    ap.add_argument("--redraw", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.redraw:
        with open(os.path.join(a.redraw, "summary.json")) as f:
            figure(json.load(f), a.out)
        return 0
    exe = dict(new=os.path.abspath(a.new), base=os.path.abspath(a.base),
               noise=os.path.join(EXE_DIR, "core_noise-level2/athena_cpu"),
               step=os.path.join(EXE_DIR, "core_step-limit/athena_cpu"),
               gauge=os.path.join(EXE_DIR, "core_gauge-2/athena_cpu"),
               clump=os.path.join(EXE_DIR, "core_clump-table/athena_cpu"))
    groups = a.groups.split(",")
    jobs = [(n, w, exe[w], a.out) for n, (g, _, who, _) in CASES.items() if g in groups
            for w in who]
    for n in sorted({j[0] for j in jobs}):    # tables and lattices before the threads
        os.makedirs(os.path.join(a.out, n), exist_ok=True)
        CASES[n][1](os.path.join(a.out, n))
    status = {}
    with cf.ThreadPoolExecutor(max_workers=a.cores) as ex:
        for name, who, rc, sec in ex.map(run_one, jobs):
            status["%s/%s" % (name, who)] = dict(exit=rc, wall_s=sec)
            print("%-9s %-6s exit %d  %.0f s" % (name, who, rc, sec), flush=True)
    rep = dict(exe=exe, status=status, byte={}, checks={})
    chk = rep["checks"]
    for k, v in status.items():
        want = CASES[k.split("/")[0]][3]
        chk["exit %d of %s" % (want, k)] = dict(ok=(v["exit"] == want), got=v["exit"])
    for name, (g, _, who, _) in CASES.items():
        if g not in groups or len(who) < 2:
            continue
        cls, other = compare(*(os.path.join(a.out, name, w) for w in who))
        rep["byte"][name] = dict(against=who[1], n_files=sum(cls.values()), classes=cls,
                                 not_identical=other)
        print("%-9s against %-6s files %2d  %s" % (name, who[1], sum(cls.values()), cls))
        chk["%s byte-identical" % name] = dict(
            ok=bool(cls) and set(cls) == {"identical"}, classes=cls)
    d = lambda n, w="new": os.path.join(a.out, n, w)          # noqa: E731
    if "step" in groups:
        lim = log_lines(d("s_lim"), "Z4c step limit")
        warn = log_lines(d("s_off"), "WARNING (Z4c step limit)")
        guard = log_lines(d("s_off"), "NRPIC guard")
        rep["step"] = dict(limit_lines=lim, warning=warn, guard=guard)
        chk["s_lim: log names the limit"] = dict(ok=bool(lim))
        chk["s_off: warning in the log"] = dict(ok=bool(warn))
        chk["s_off: guard stop in the log"] = dict(ok=bool(guard))
    if "gauge" in groups:
        cls, _ = compare(d("g_hole"), d("g_leak"))
        rep["gauge"] = dict(hole_vs_leak=cls)
        chk["g_hole differs from g_leak (weight acts)"] = dict(
            ok=cls.get("other", 0) > 0, classes=cls)
    if "clump" in groups:
        rec = glob.glob(os.path.join(d("c_solve"), "*.idsolve.txt"))
        rows = []
        if rec:
            with open(rec[0]) as f:
                rows = [ln.split() for ln in f if ln.strip() and not ln.startswith("#")]
        hl = float(rows[-1][4]) if rows else float("nan")
        rep["clump"] = dict(outer=int(rows[-1][0]) if rows else None, H_last=hl,
                            H_first=float(rows[0][4]) if rows else None)
        chk["c_solve: max|H| below 1e-10 after the solve"] = dict(ok=bool(hl < 1e-10),
                                                                  H_last=hl)
    if "combo" in groups:
        for n in ("x_l2dt", "x_holedt"):
            ok, nh = hist_finite(d(n))
            lim = log_lines(d(n), "Z4c step limit")
            rep[n] = dict(histories=nh, finite=ok, limit_lines=lim,
                          guard=bool(glob.glob(os.path.join(d(n), "*.guard.txt"))))
            chk["%s: histories finite, limit in the log" % n] = dict(
                ok=ok and nh > 0 and bool(lim))
        if "noise" in groups:
            same = all(open(p, "rb").read() ==
                       open(os.path.join(d("n_l2"), os.path.basename(p)), "rb").read()
                       for p in glob.glob(os.path.join(d("x_l2dt"), "*.hst")))
            rep["x_l2dt"]["hst_identical_with_n_l2"] = same
    if "term" in groups:
        t = os.path.join(a.out, "term")
        with open(os.path.join(a.out, "term.log"), "w") as log:
            rc = subprocess.run([sys.executable,
                                 os.path.join(HERE, "..", "preempt", "term_test.py"),
                                 "--exe", exe["new"], "--out", t, "--cases", "S1,S2"],
                                stdout=log, stderr=subprocess.STDOUT).returncode
        rep["term_exit"] = rc
        chk["SIGTERM: term_test.py S1, S2"] = dict(ok=(rc == 0), exit=rc)
    if "chain" in groups:
        t = os.path.join(a.out, "chain")
        with open(os.path.join(a.out, "chain.log"), "w") as log:
            rc = subprocess.run([sys.executable,
                                 os.path.join(REPO, "scripts/tests/test_submit_chain.py"),
                                 "--out", t], stdout=log,
                                stderr=subprocess.STDOUT).returncode
        rep["chain_exit"] = rc
        chk["chain script: test_submit_chain.py"] = dict(ok=(rc == 0), exit=rc)
    bad = [k for k, v in chk.items() if not v["ok"]]
    rep["bad"] = bad
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(rep, f, indent=1)
    figure(rep, a.out)
    for k, v in chk.items():
        print("%-5s %s %s" % ("ok" if v["ok"] else "FAIL", k,
                              {x: y for x, y in v.items() if x != "ok"} or ""))
    print("QUICK", "FAIL: %s" % bad if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
