#!/usr/bin/env python3
"""Horizon finder with polishing iterations, and the growth guard of horizon excision
(core/restart-finder, item 2).

    python finder_test.py --exe NEW --ref-exe RELEASE --out DIR [--jobs 3] [--threads 2]
                          [--tlim 2.0]

Deck: problems/tests/finder_polish.athinput (vacuum puncture of mass 1, finest cells M/8,
2000 test particles that fall in, removal record), run to --tlim (the deck says 8 M; the
serial build needs 17 s per cycle, so the test takes the threaded builds of the branch
and of the release, the same number of threads for all, and a shorter time).  Runs, each
in a directory of DIR:

  prod      the deck as it is: mass_tol 1e-5, no polishing (the rule of puncture_setup)
  ref       the same with the release executable (must be byte-identical to prod)
  tight     mass_tol 1e-9, 4000 iterations: the reference mass where it is found
  def       mass_tol 1e-2 (the default of the finder), no polishing
  pol       mass_tol 1e-2, polish_iterations 100
  prodpol   mass_tol 1e-5, polish_iterations 100: the recommended setting
  g04       ah_exc_max_growth = 0.4: the guard radius (0.4 M) lies inside the horizon
            (0.47 M) from the start, so no particle may be removed inside the horizon
  g4        ah_exc_max_growth = 4.0 written out (must be byte-identical to prod)

Whether a search was found, and its number of flow iterations, come from the status
file (<fastflow> diagnostics = true in the deck): the summary file repeats the last
accepted surface when a search fails.

Writes DIR/summary.json and DIR/fig_finder_test.{pdf,png}; exit status 0 if the checks
hold.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DECK = os.path.join(REPO, "problems", "tests", "finder_polish.athinput")
BASE = "fp"
SKIP = re.compile(r"(^|/)(athena[^/]*\.log|deck\.athinput)$")
RUNS = {
    "prod": ([], None),
    "ref": ([], None),
    "tight": (["fastflow/mass_tol_0=1.0e-9", "fastflow/flow_iterations_0=4000"], None),
    "def": (["fastflow/mass_tol_0=1.0e-2"], None),
    "pol": (["fastflow/mass_tol_0=1.0e-2", "fastflow/polish_iterations_0=100"], None),
    "prodpol": (["fastflow/polish_iterations_0=100"], None),
    "g04": ([], "0.4"),
    "g4": ([], "4.0"),
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def make_infall(path, n=2000, seed=20261125, mass=1.0e-8, rmin=0.3, rmax=2.5):
    """Light particles around the puncture: radii 0.3 to 2.5 M, random momenta up to 0.4
    per unit mass plus an inward radial part of 0 to 0.6 (as make_infall of
    tracks/core/analysis/mpi/mpi_tests.py, centred on the origin)."""
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic.io import write_nrp
    rng = np.random.default_rng(seed)
    r = rng.uniform(rmin, rmax, n)
    v = rng.normal(size=(n, 3))
    nhat = v/np.linalg.norm(v, axis=1)[:, None]
    x = r[:, None]*nhat
    u = rng.uniform(-0.4, 0.4, (n, 3)) - rng.uniform(0.0, 0.6, n)[:, None]*nhat
    m = mass*rng.uniform(0.5, 1.5, n)
    write_nrp(path, x, u, m)
    return n


def one(name, exe, out, ic, tlim, threads):
    over, growth = RUNS[name]
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    deck = DECK
    if growth is not None:
        txt = open(DECK).read().replace("# ah_exc_max_growth = 4.0 ",
                                        "ah_exc_max_growth = %s  #" % growth)
        assert "\nah_exc_max_growth = %s" % growth in txt
        deck = os.path.join(d, "deck.athinput")
        with open(deck, "w") as f:
            f.write(txt)
    cmd = [exe, "-i", deck, "-d", d, "particles/particle_file=" + ic,
           "time/tlim=%s" % tlim] + over
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=d,
                            env=dict(os.environ, OMP_NUM_THREADS=str(threads),
                                     OMP_PROC_BIND="false")).returncode
    return name, rc, round(time.time() - t0, 1)


def summary_rows(d):
    rows = []
    for ln in open(os.path.join(d, BASE + ".horizon_summary_0.txt")):
        if ln.startswith("#") or not ln.strip():
            continue
        rows.append([float(v) for v in ln.split()])
    return np.array(rows)


def status_rows(d):
    """cycle, time, found, reason, flow iterations, area, area mass of every search."""
    rows = []
    for ln in open(os.path.join(d, BASE + ".horizon_status_0.txt")):
        if ln.startswith("#") or not ln.strip():
            continue
        rows.append([float(v) for v in ln.split("#")[0].split()[:7]])
    return np.array(rows)


def removed(d):
    p = os.path.join(d, BASE + ".removed.bin")
    if not os.path.exists(p):
        return np.zeros((0, 20))
    with open(p, "rb") as f:
        head = f.read(16)
        assert head[:8] == b"NRPREM01"
        a = np.fromfile(f, dtype="<f8")
    return a.reshape(-1, 20)


def files_of(d):
    fs = sorted(os.path.relpath(os.path.join(r, x), d) for r, _, xs in os.walk(d) for x in xs)
    return [x for x in fs if not SKIP.search(x)]


def differing(da, db):
    fa, fb = files_of(da), files_of(db)
    diff = [x for x in fa if not os.path.exists(os.path.join(db, x))
            or sha(os.path.join(da, x)) != sha(os.path.join(db, x))]
    return dict(files_compared=len(fa), files_differing=diff, same_file_set=(fa == fb))


def figure(out, S, T, R, tlim):
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.96, wspace=0.42)
    sty = (("def", fs.PAL["yellow"], "1e-2", "v"), ("prod", fs.PAL["green"], "1e-5", "s"),
           ("pol", fs.PAL["orange"], "1e-2, 100 polishing", "^"),
           ("prodpol", fs.PAL["red"], "1e-5, 100 polishing", "o"),
           ("tight", fs.PAL["blue"], "tight rule", "x"))
    ax = axs[0]
    for name, col, lab, mk in sty:
        f = T[name][:, 2] == 1.0
        ax.plot(T[name][f, 1], S[name][f, 2], ls="none", marker=mk, ms=4, color=col, label=lab,
                mfc="none")
    ax.set_xlabel("t / M"); ax.set_ylabel("horizon mass (found searches)")
    ax.legend(loc="lower left", fontsize=6)
    ax = axs[1]
    for name, col, lab, mk in sty:
        ax.semilogy(T[name][:, 1], np.maximum(T[name][:, 4], 1), color=col, marker=mk, ms=3,
                    mfc="none", label=lab)
        nf = T[name][:, 2] != 1.0
        ax.semilogy(T[name][nf, 1], np.maximum(T[name][nf, 4], 1), ls="none", marker="o", ms=7,
                    mfc="none", color="k")
    ax.set_xlabel("t / M"); ax.set_ylabel("flow iterations (circled: not found)")
    fs.no_minor_labels(ax)
    ax = axs[2]
    for name, col, lab in (("prod", fs.PAL["blue"], "no option (guard 4 M)"),
                           ("g04", fs.PAL["red"], "ah_exc_max_growth = 0.4")):
        r = R[name]
        t = np.sort(r[r[:, 3] == 3.0][:, 0])
        ax.step(np.concatenate([[0.0], t, [tlim]]),
                np.concatenate([[0], np.arange(1, len(t) + 1), [len(t)]]), where="post",
                color=col, label=lab, ls="-" if name == "prod" else "--")
    ax.set_xlabel("t / M"); ax.set_ylabel("removed inside the horizon")
    ax.legend(loc="center right", fontsize=7)
    return fs.save(fig, os.path.join(out, "fig_finder_test"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--ref-exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--tlim", type=float, default=2.0)
    ap.add_argument("--runs", help="judge the runs of this directory (an earlier run of "
                    "this script) instead of running them; figure and summary go to --out")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    res = {}
    if a.runs:
        src = os.path.abspath(a.runs)
        old = json.load(open(os.path.join(src, "summary.json")))
        ic = os.path.join(src, "infall.nrp")
        for n in RUNS:
            res[n] = dict(rc=old["runs"][n]["rc"], wall_s=old["runs"][n]["wall_s"])
        figout, out = out, src
    else:
        figout = out
        ic = os.path.join(out, "infall.nrp")
        if not os.path.exists(ic):
            make_infall(ic)
        with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            futs = [ex.submit(one, n, a.ref_exe if n == "ref" else a.exe, out, ic, a.tlim,
                              a.threads) for n in RUNS]
            for f in cf.as_completed(futs):
                n, rc, wall = f.result()
                res[n] = dict(rc=rc, wall_s=wall)
    S = {n: summary_rows(os.path.join(out, n)) for n in RUNS}
    T = {n: status_rows(os.path.join(out, n)) for n in RUNS}
    R = {n: removed(os.path.join(out, n)) for n in RUNS}
    ck = {}
    ck["every run ended with status 0"] = all(r["rc"] == 0 for r in res.values())
    d = differing(os.path.join(out, "prod"), os.path.join(out, "ref"))
    res["prod"]["against_release"] = d
    ck["P8: polish_iterations_0 = 0 with the new executable equals the release byte for "
       "byte (%d files)" % d["files_compared"]] = (d["files_differing"] == [] and d["same_file_set"])
    ref, reft = S["tight"], T["tight"]
    ok_ref = reft[:, 2] == 1.0                 # searches where the tight rule is found
    table = []
    for n in RUNS:
        s, t = S[n], T[n]
        same_t = (len(t) == len(reft)) and bool(np.all(t[:, 1] == reft[:, 1]))
        found = t[:, 2] == 1.0
        both = found & ok_ref if same_t else np.zeros(len(t), bool)
        dm = np.abs(s[:, 2] - ref[:, 2]) if same_t else np.full(len(s), np.nan)
        r3 = R[n][R[n][:, 3] == 3.0]
        res[n].update(searches=int(len(t)), found=int(found.sum()),
                      not_found_times=[float(x) for x in t[~found, 1]],
                      not_found_reasons=sorted(set(int(x) for x in t[~found, 3])),
                      same_times_as_tight=same_t, both_found=int(both.sum()),
                      max_abs_dmass_where_both_found=float(np.max(dm[both])) if both.any() else None,
                      n_above_2e5_where_both_found=int(np.sum(dm[both] > 2.0e-5)),
                      flow_iterations_total=int(np.sum(t[:, 4])),
                      flow_iterations_of_found=[int(x) for x in t[found, 4]],
                      hrms_of_found_max=float(np.max(s[found, 8])) if found.any() else None,
                      minradius_range=[float(np.nanmin(s[:, 11])), float(np.nanmax(s[:, 11]))],
                      removed=int(len(R[n])), removed_reason3=int(len(r3)))
    for i in range(len(reft)):
        table.append(dict(time=float(reft[i, 1]), **{
            n: dict(found=int(T[n][i, 2]), iterations=int(T[n][i, 4]), mass=float(S[n][i, 2]),
                    hrms=float(S[n][i, 8])) for n in ("tight", "prodpol", "pol", "prod", "def")}))
    res["per_search"] = table
    ck["P14: tight rule and 1e-5 with 100 polishing iterations agree within 2e-5 wherever "
       "both are found (%d searches, max %s)" % (
           res["prodpol"]["both_found"], res["prodpol"]["max_abs_dmass_where_both_found"])] = (
        res["prodpol"]["both_found"] > 0 and res["prodpol"]["n_above_2e5_where_both_found"] == 0)
    # column 9 of the last surface the tight rule accepted, carried forward
    last_h, bad = None, []
    fp = T["prodpol"][:, 2] == 1.0
    for i in range(len(reft)):
        if ok_ref[i]:
            last_h = ref[i, 8]
        if fp[i] and last_h is not None and S["prodpol"][i, 8] > 10.0*last_h:
            bad.append(float(reft[i, 1]))
    ck["P15: 1e-5 with polishing never reports found on a surface whose residual exceeds "
       "ten times that of the last tight surface (times %s)" % bad] = (bad == [])
    fpl = T["pol"][:, 2] == 1.0
    loose_bad = [float(reft[i, 1]) for i in range(len(reft)) if fpl[i] and S["pol"][i, 8] > 0.1]
    res["pol"]["found_with_residual_above_0p1"] = loose_bad
    ck["P16 (expected defect of the loose tolerance): 1e-2 with polishing reports found "
       "with a residual above 0.1 at least once (times %s)" % loose_bad] = (len(loose_bad) >= 1)
    jump = (reft[:, 1] > 0.5) & (reft[:, 1] < 1.1)
    late = reft[:, 1] >= 1.125
    res["tight"]["not_found_in_jump"] = int(np.sum(jump & ~ok_ref))
    res["prodpol"]["not_found_in_jump"] = int(np.sum(jump & ~fp))
    ck["P17: between t = 0.5 and 1.1 at least two searches are not found for the tight rule "
       "(%d) and for 1e-5 with polishing (%d)" % (res["tight"]["not_found_in_jump"],
                                                 res["prodpol"]["not_found_in_jump"])] = (
        res["tight"]["not_found_in_jump"] >= 2 and res["prodpol"]["not_found_in_jump"] >= 2)
    ck["P17: from t = 1.125 on both are found at every search (tight %d, polished %d of %d)"
       % (int(np.sum(late & ok_ref)), int(np.sum(late & fp)), int(np.sum(late)))] = bool(
        np.all(ok_ref[late]) and np.all(fp[late]))
    # guard
    d4 = differing(os.path.join(out, "prod"), os.path.join(out, "g4"))
    res["g4"]["against_prod"] = d4
    ck["P10: ah_exc_max_growth = 4.0 written out equals the run without it byte for byte "
       "(%d files)" % d4["files_compared"]] = (d4["files_differing"] == [] and d4["same_file_set"])
    ck["P10: the horizon radius stays above 0.4 M and below 4 M (%.3f to %.3f)"
       % tuple(res["prod"]["minradius_range"])] = (
        res["prod"]["minradius_range"][0] > 0.4 and res["prod"]["minradius_range"][1] < 4.0)
    ck["P10: without the option particles are removed inside the horizon (%d)"
       % res["prod"]["removed_reason3"]] = (res["prod"]["removed_reason3"] > 0)
    ck["P10: with ah_exc_max_growth = 0.4 none is (%d)" % res["g04"]["removed_reason3"]] = (
        res["g04"]["removed_reason3"] == 0)
    figs = figure(figout, S, T, R, a.tlim)
    summary = dict(runs_dir=out, exe=a.exe, exe_sha256=sha(a.exe), ref_exe=a.ref_exe,
                   ref_exe_sha256=sha(a.ref_exe), deck_sha256=sha(DECK), tlim=a.tlim,
                   threads=a.threads, particle_file_sha256=sha(ic), checks=ck, runs=res,
                   figures=figs, all_ok=all(ck.values()))
    with open(os.path.join(figout, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    for n in RUNS:
        print(n, json.dumps({k: v for k, v in res[n].items() if not isinstance(v, dict)}))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
