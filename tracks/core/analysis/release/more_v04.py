#!/usr/bin/env python3
"""More examples of the READY of release candidate core-v0.4 on processors: example
inputs that quick_v04.py does not run, each started with the merged executable and with
the executable its branch published, compared byte for byte (classes of regress_v04.py).

    more_v04.py --new ATHENA --out DIR [--cores N] [--tests boost,...] [--exe-dir DIR]
    more_v04.py --new ATHENA --out DIR --replot DIR_OF_AN_EARLIER_CALL

Tests (branch; option exercised):
  boost   id-solver        idsolve/gaussian_boost.athinput at 32 cells (id_vector)
  spin    clump-curvature  clump/clump_spin.athinput (comp0_s3; initial data only)
  pairh   requests-adf     tests/pair_horizon.athinput (punc_pair_a/b; two steps)
  uneq    gauge            puncture/by_unequal.athinput, one step (shift_eta_profile
                           on a pair of mass ratio 4)
  acc     requests-adf     tests/accretion_static.athinput, 400 steps (removal_record,
                           flux spheres, pericentre counter)
  kepler  requests-adf     tests/newton_point_mass.athinput, 100 steps (newton_pm_mass)
This is a start-up and identity check, not a test of the physics: equal bytes mean the
merged executable does for these inputs what the tested branch executable does.
Writes DIR/more_summary.json and DIR/fig_more_v04.{pdf,png}.  Exit status 0 if every
run ended with status 0 and no file AthenaK wrote is of class "other".
"""
import argparse
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "tracks", "core", "analysis", "dfix"))
import regress_v04 as rg                      # noqa: E402
import quick_v04 as qk                        # noqa: E402

PROB = os.path.join(REPO, "problems")
N32 = ["mesh/nx1=32", "mesh/nx2=32", "mesh/nx3=32"]


def prep_boost(d):
    mk = os.path.join(PROB, "idsolve/make_ic.py")
    qk.sh([sys.executable, mk, "gaussian", "--h", "0.5", "--out", d], d)
    qk.sh([sys.executable, mk, "boost", "--in", os.path.join(d, "gauss_h0p5.nrp"), "--u",
           "0.1", "--out", d], d)


def prep_spin(d):
    qk.sh([sys.executable, os.path.join(PROB, "ic/make_ic.py"), "clumps", "--gaussian",
           "0.2,1,0,0,0,0,0,0,0,0,0.04", "--sampler", "lattice", "--lattice-h", "0.25",
           "--seed", "1", "--out", d, "--prefix", "particles"], d)


def prep_acc(d):
    import t3_accretion
    t3_accretion.make_particles(os.path.join(d, "acc_static.nrp"))


def prep_kepler(d):
    import t4_newton
    tmp = d + ".cases"
    t4_newton.make_cases(tmp)
    shutil.copy(os.path.join(tmp, "kepler", "npm.nrp"), os.path.join(d, "npm.nrp"))


# name -> (branch, input, preparation or None, arguments)
TESTS = {
    "boost": ("id-solver", "idsolve/gaussian_boost.athinput", prep_boost,
              N32 + ["particles/particle_file=gauss_h0p5_u0p1.nrp"]),
    "spin": ("clump-curvature", "clump/clump_spin.athinput", prep_spin, []),
    "pairh": ("requests-adf", "tests/pair_horizon.athinput", None, []),
    "uneq": ("gauge", "puncture/by_unequal.athinput", None, ["time/nlim=1"]),
    "acc": ("requests-adf", "tests/accretion_static.athinput", prep_acc,
            ["time/nlim=400"]),
    "kepler": ("requests-adf", "tests/newton_point_mass.athinput", prep_kepler,
               ["time/nlim=100"]),
}


def run(exe, d, name):
    _, inp, prep, args = TESTS[name]
    os.makedirs(d, exist_ok=True)
    if prep:
        prep(d)
    with open(d + ".prepared.json", "w") as f:
        json.dump(rg.out_files(d), f)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run([exe, "-i", os.path.join(PROB, inp), "-d", d] + args, cwd=d,
                            stdout=log, stderr=subprocess.STDOUT, env=env).returncode
    return rc, round(time.time() - t0, 1)


def figure(out, summary):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    names = list(summary["tests"])
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.93, wspace=0.28)
    y = np.arange(len(names))[::-1]
    a = ax[0]
    left = np.zeros(len(names))
    for key, lab, col in (("identical", "identical", fs.PAL["blue"]),
                          ("a", "a: unset restart bytes", fs.PAL["yellow"]),
                          ("b", "b: last_time lines", fs.PAL["green"]),
                          ("a+b", "a and b", fs.PAL["orange"]),
                          ("other", "other", fs.PAL["red"])):
        n = np.array([len(summary["tests"][c][key]) for c in names], dtype=float)
        a.barh(y, n, left=left, color=col, label=lab, height=0.7)
        left += n
    a.set_yticks(y)
    a.set_yticklabels(names)
    a.tick_params(axis="y", which="minor", left=False, right=False)
    a.set_xlim(0, max(left.max(), 1.0)*2.1)
    a.set_xlabel("files AthenaK wrote, merged against branch executable", labelpad=2)
    a.legend(loc="center right", fontsize=8)
    a = ax[1]
    wn = [summary["tests"][c]["wall_time_s"]["new"] for c in names]
    wb = [summary["tests"][c]["wall_time_s"]["branch"] for c in names]
    a.barh(y + 0.18, np.maximum(wn, 0.05), height=0.34, color=fs.PAL["red"])
    a.barh(y - 0.18, np.maximum(wb, 0.05), height=0.34, color=fs.PAL["blue"])
    for yy, c in zip(y, names):
        e = summary["tests"][c]["exit"]
        a.text(0.97, yy, "exit %d, %d" % (e["new"], e["branch"]), ha="right", va="center",
               transform=a.get_yaxis_transform(), fontsize=8)
    a.set_xscale("log")
    a.set_yticks(y)
    a.set_yticklabels(names)
    a.tick_params(axis="y", which="minor", left=False, right=False)
    a.set_xlim(0.03, max(max(wn), max(wb), 1.0)*60)
    a.set_xlabel("wall time on one core (s): red merged, blue branch", labelpad=2)
    fs.save(fig, os.path.join(out, "fig_more_v04"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=1)
    ap.add_argument("--tests", default=",".join(TESTS))
    ap.add_argument("--exe-dir", default=qk.EXE_DIR)
    ap.add_argument("--replot", default=None,
                    help="directory of an earlier call: draw its more_summary.json "
                         "again into --out, run nothing")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    if a.replot:
        with open(os.path.join(a.replot, "more_summary.json")) as f:
            summary = json.load(f)
        figure(out, summary)
        print("MORE EXAMPLES", summary["verdict"], "(figure of", a.replot + ")")
        return 0 if summary["verdict"] == "PASS" else 1
    new = os.path.abspath(a.new)
    names = a.tests.split(",")
    jobs = []
    for n in names:
        jobs.append((n, "new", new))
        jobs.append((n, "branch", os.path.join(a.exe_dir, "core_" + TESTS[n][0],
                                                "athena_cpu")))
    codes, walls = {}, {}
    with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
        futs = {pool.submit(run, exe, os.path.join(out, n, lab), n): (n, lab)
                for n, lab, exe in jobs}
        for fut in cf.as_completed(futs):
            codes[futs[fut]], walls[futs[fut]] = fut.result()
            print("ran %-7s %-6s exit %d  %.1f s" % (futs[fut] + (codes[futs[fut]],
                                                                walls[futs[fut]])),
                  flush=True)
    summary = {"new": new, "sha256_new": rg.sha256(new), "tests": {}}
    ok = True
    for n in names:
        br = TESTS[n][0]
        db, dn = os.path.join(out, n, "branch"), os.path.join(out, n, "new")
        prepared = sorted(set(qk.prepared_files(db)) | set(qk.prepared_files(dn)))
        res = rg.compare(n, db, dn, skip=prepared)
        exe_b = os.path.join(a.exe_dir, "core_" + br, "athena_cpu")
        t = {"branch": br, "input": "problems/" + TESTS[n][1], "args": TESTS[n][3],
             "exit": {"new": codes[(n, "new")], "branch": codes[(n, "branch")]},
             "wall_time_s": {"new": walls[(n, "new")], "branch": walls[(n, "branch")]},
             "branch_exe": exe_b, "sha256_branch": rg.sha256(exe_b),
             "prepared": {f: qk.same_bytes(os.path.join(db, f), os.path.join(dn, f))
                          for f in prepared}}
        t.update({k: res[k] for k in ("identical", "a", "b", "a+b", "other", "details",
                                      "files")})
        good = (t["exit"] == {"new": 0, "branch": 0} and not res["other"]
                and res["files"] > 0)
        t["verdict"] = "pass" if good else "FAIL"
        ok = ok and good
        summary["tests"][n] = t
        print("%-7s vs core/%-15s exit %d %d  files %3d  identical %3d  a %d  b %d  "
              "a+b %d  other %d  %s"
              % (n, br, t["exit"]["new"], t["exit"]["branch"], res["files"],
                 len(res["identical"]), len(res["a"]), len(res["b"]), len(res["a+b"]),
                 len(res["other"]), t["verdict"]), flush=True)
        for f in res["other"]:
            print("        other: %s %s" % (f, res["details"].get(f, "")), flush=True)
    summary["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(out, "more_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    figure(out, summary)
    print("MORE EXAMPLES", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
