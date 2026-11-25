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
  tight     mass_tol 1e-9, 4000 iterations: the reference mass
  def       mass_tol 1e-2 (the default of the finder), no polishing
  pol       mass_tol 1e-2, polish_iterations 100: the new rule
  pol30     mass_tol 1e-2, polish_iterations 30
  g04       ah_exc_max_growth = 0.4: the guard radius (0.4 M) lies inside the horizon
            (0.47 M) from the start, so no particle may be removed inside the horizon
  g4        ah_exc_max_growth = 4.0 written out (must be byte-identical to prod)

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
    "pol30": (["fastflow/mass_tol_0=1.0e-2", "fastflow/polish_iterations_0=30"], None),
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


def figure(out, S, R, tlim):
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.96, wspace=0.42)
    ref = S["tight"]
    ax = axs[0]
    for name, col, lab in (("def", fs.PAL["yellow"], "1e-2"),
                           ("prod", fs.PAL["green"], "1e-5"),
                           ("pol30", fs.PAL["orange"], "1e-2, 30 polishing"),
                           ("pol", fs.PAL["red"], "1e-2, 100 polishing")):
        s = S[name]
        n = min(len(s), len(ref))
        ax.semilogy(s[:n, 1], np.maximum(np.abs(s[:n, 2] - ref[:n, 2]), 1e-16), color=col,
                    label=lab)
    ax.axhline(2.0e-5, **fs.MASK_LINE)
    ax.set_xlabel("t / M"); ax.set_ylabel("|mass - mass of the tight rule|")
    ax.set_ylim(1e-14, 1e0)
    ax.legend(loc="upper right", fontsize=7, ncol=1)
    fs.no_minor_labels(ax)
    ax = axs[1]
    for name, col, lab in (("tight", fs.PAL["blue"], "tight rule"), ("pol", fs.PAL["red"], "1e-2, 100 polishing"),
                           ("prod", fs.PAL["green"], "1e-5"), ("def", fs.PAL["yellow"], "1e-2")):
        ax.plot(S[name][:, 1], S[name][:, 0], color=col, label=lab,
                ls="--" if name == "pol" else "-")
    ax.set_yscale("log")
    ax.set_xlabel("t / M"); ax.set_ylabel("flow iterations of a search")
    ax.legend(loc="center right", fontsize=7)
    fs.no_minor_labels(ax)
    ax = axs[2]
    for name, col, lab in (("prod", fs.PAL["blue"], "no option (guard 4 M)"),
                           ("g04", fs.PAL["red"], "ah_exc_max_growth = 0.4")):
        r = R[name]
        t = np.sort(r[r[:, 3] == 3.0][:, 0])
        ax.step(np.concatenate([[0.0], t, [tlim]]),
                np.concatenate([[0], np.arange(1, len(t) + 1), [len(t)]]), where="post",
                color=col, label=lab, ls="-" if name == "prod" else "--")
    ax.set_xlabel("t / M"); ax.set_ylabel("particles removed inside the horizon")
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
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    ic = os.path.join(out, "infall.nrp")
    if not os.path.exists(ic):
        make_infall(ic)
    res = {}
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(one, n, a.ref_exe if n == "ref" else a.exe, out, ic, a.tlim,
                          a.threads) for n in RUNS]
        for f in cf.as_completed(futs):
            n, rc, wall = f.result()
            res[n] = dict(rc=rc, wall_s=wall)
    S = {n: summary_rows(os.path.join(out, n)) for n in RUNS}
    R = {n: removed(os.path.join(out, n)) for n in RUNS}
    ck = {}
    ck["every run ended with status 0"] = all(r["rc"] == 0 for r in res.values())
    d = differing(os.path.join(out, "prod"), os.path.join(out, "ref"))
    res["prod"]["against_release"] = d
    ck["P8: polish_iterations_0 = 0 with the new executable equals the release byte for "
       "byte (%d files)" % d["files_compared"]] = (d["files_differing"] == [] and d["same_file_set"])
    ref = S["tight"]
    for n in RUNS:
        s = S[n]
        m = min(len(s), len(ref))
        same_t = (len(s) == len(ref)) and bool(np.all(s[:, 1] == ref[:, 1]))
        found = np.isfinite(s[:, 2])
        dm = np.abs(s[:m, 2] - ref[:m, 2])
        r3 = R[n][R[n][:, 3] == 3.0]
        res[n].update(searches=int(len(s)), found=int(found.sum()), same_times_as_tight=same_t,
                      max_abs_dmass=float(np.nanmax(dm)), median_abs_dmass=float(np.nanmedian(dm)),
                      n_above_2e5=int(np.sum(dm > 2.0e-5)),
                      mass_range=[float(np.nanmin(s[:, 2])), float(np.nanmax(s[:, 2]))],
                      minradius_range=[float(np.nanmin(s[:, 11])), float(np.nanmax(s[:, 11]))],
                      flow_iterations_mean=float(np.mean(s[:, 0])),
                      flow_iterations_max=int(np.max(s[:, 0])),
                      removed=int(len(R[n])), removed_reason3=int(len(r3)),
                      last_reason3=float(np.max(r3[:, 0])) if len(r3) else None)
    ck["tight rule: found at every search (%d)" % res["tight"]["searches"]] = (
        res["tight"]["found"] == res["tight"]["searches"])
    ck["P9: mass_tol 1e-2 with 100 polishing iterations within 2e-5 of the tight rule at "
       "every search (max %.2e)" % res["pol"]["max_abs_dmass"]] = (
        res["pol"]["same_times_as_tight"] and res["pol"]["n_above_2e5"] == 0
        and res["pol"]["found"] == res["pol"]["searches"])
    ck["P9: mass_tol 1e-2 alone is more than 2e-5 off at most searches (%d of %d, max %.2e)"
       % (res["def"]["n_above_2e5"], res["def"]["searches"], res["def"]["max_abs_dmass"])] = (
        res["def"]["n_above_2e5"] > res["def"]["searches"]//2)
    ck["P9: 30 polishing iterations lie between (max %.2e)" % res["pol30"]["max_abs_dmass"]] = (
        res["pol"]["max_abs_dmass"] <= res["pol30"]["max_abs_dmass"] <= res["def"]["max_abs_dmass"])
    res["prod"]["note"] = "mass_tol 1e-5 alone: max %.2e from the tight rule, %d of %d above 2e-5" % (
        res["prod"]["max_abs_dmass"], res["prod"]["n_above_2e5"], res["prod"]["searches"])
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
    figs = figure(out, S, R, a.tlim)
    summary = dict(exe=a.exe, exe_sha256=sha(a.exe), ref_exe=a.ref_exe,
                   ref_exe_sha256=sha(a.ref_exe), deck_sha256=sha(DECK), tlim=a.tlim,
                   threads=a.threads, particle_file_sha256=sha(ic), checks=ck, runs=res,
                   figures=figs, all_ok=all(ck.values()))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    for n in RUNS:
        print(n, json.dumps({k: v for k, v in res[n].items() if not isinstance(v, dict)}))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
