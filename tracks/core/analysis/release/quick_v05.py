#!/usr/bin/env python3
"""Quick tests of release candidate core-v0.5 on processors: one example per merged
branch from its READY, and the combinations that exist only in the merged source.

    quick_v05.py --serial ATHENA --omp ATHENA --mpi ATHENA --out DIR [--cores N]
                 [--groups byte,threads,mpi] [--analyse-only --runs OLDDIR]

(--analyse-only --runs OLDDIR evaluates and draws again from the runs of an earlier call,
without running anything; summary and figure go to DIR.)

Group byte (serial executable of the candidate against the processor executable the
branch published, every file AthenaK writes compared byte for byte; classes of
regress_v04.py: identical, a, b, a+b, other):
  s3g   scalar-3     problems/scalar/sr_stochastic_gauge.athinput (con_signed), 12 steps
  usr   scalar-3     problems/scalar/usr_stochastic.athinput, 12 steps
  trk   cosmo-amr    problems/cosmo_amr/flrw_tracker.athinput, 12 steps (tracker in a
                     periodic box, refinement that follows it, dt_lightspeed)
  peak  cosmo-amr    problems/cosmo_amr/peak_amr.athinput as case "ladder" of
                     analysis/cosmo_amr/t9_peak.py (32^3, three levels, 10 steps:
                     <particles_amr>, deposit_fine_shape, guard, region norms)
  dser  build-openmp problems/tests/deposit_threads.athinput against athena_cpu_serial
Group threads (threaded executable; decks are problems/tests/deposit_threads.athinput
with a dump of the sources in double precision added):
  d_p1, d_p4a, d_p4b   deposit_threads = private at 1, 4, 4 threads
  d_a4                 deposit_threads = atomic at 4 threads
  d_ser, d_ser0        serial executable with the option (it prints a note) and
                       without the line
  f_*                  the same with deposit_shape = cic and deposit_fine_shape = true
                       (fine-shape branch of core/cosmo-amr through the deposit target of
                       core/build-openmp: tested by neither branch); g_* with tsc
Group mpi (MPI executable, analysis/mpi/mpi_tests.py of the package):
  t1_kerr      test particles around a Kerr hole on the mesh, 1 and 2 ranks
  t3_cluster   self-gravitating cluster with Z4c, 1 and 2 ranks
  stop         problems/tests/mpi_deposit_smr.athinput with deposit_fine_shape on 2
               ranks: must stop with the message of NrpicMpiInit
  The runs on 1 and on 2 ranks are also compared byte for byte with the runs of the
  package made with its branch executable (PACKAGE_RUNS): mesh restart files are judged
  by their data (identical outside the 36 header bytes that release core-v0.4 zeroes)
  because their parameter dump holds the run directory and lines of the example inputs
  that the package edited after its runs.
Writes DIR/summary.json and DIR/fig_quick_v05.{pdf,png}.  Exit status 0 if every run
ended as expected, no file is of class "other" and every number lies inside its band.
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
sys.path.insert(0, os.path.join(HERE, "..", "cosmo_amr"))
import regress_v04 as rg                      # noqa: E402
import amrlib as A                            # noqa: E402
import t9_peak as T9                          # noqa: E402
from nrpic import athena_bin                  # noqa: E402

EXE_DIR = "/data/haiyangw/nrpic/scratch/core/exe"
PROB = os.path.join(REPO, "problems")
RANDOM = "/data/haiyangw/nrpic/scratch/core/regress/ic/random.nrp"
MPIRUN = "/home/emost/codes/openmpi/bin/mpirun"
PACKAGE_RUNS = {  # runs of package mpi with its branch executable (JOURNAL-mpi.md)
    "t1_kerr": "/data/haiyangw/nrpic/scratch/core/core-20261119-145615-4c98c59/t1_kerr",
    "t3_cluster": "/data/haiyangw/nrpic/scratch/core/core-20261119-154814-ca46836/t3_cluster",
}
BRANCH_EXE = {"scalar-3": "core_scalar-3/athena_cpu", "cosmo-amr": "core_cosmo-amr/athena_cpu",
              "build-openmp": "core_build-openmp/athena_cpu_serial"}


# ---------------------------------------------------------------------------------------
# decks
# ---------------------------------------------------------------------------------------
def deck_s3g(d):
    b = A.Inp(os.path.join(PROB, "scalar/sr_stochastic_gauge.athinput"))
    b.set("scalar_field", noise_mode_file=os.path.join(PROB, "scalar/sr_stochastic_modes.txt"))
    return b.set("time", nlim=12)


def deck_usr(d):
    b = A.Inp(os.path.join(PROB, "scalar/usr_stochastic.athinput"))
    b.set("scalar_field", noise_mode_file=os.path.join(PROB, "scalar/usr_stochastic_modes.txt"))
    return b.set("time", nlim=12)


def deck_trk(d):
    subprocess.run([sys.executable, os.path.join(REPO, "cosmo/ic/make_lattice.py"), "--n",
                    "24", "--ppc", "1", "--L", "6", "--xmin", "-3", "--out", d], check=True,
                   stdout=subprocess.DEVNULL)
    b = A.Inp(os.path.join(PROB, "cosmo_amr/flrw_tracker.athinput"))
    b.set("particles", particle_file=os.path.join(d, "particles.nrp"))
    return b.set("time", nlim=12)


def deck_peak(d):
    return T9.base(T9.DEF_IC)


def deck_dep(d, threads_mode="private", fine=None):
    """the deposit test with a dump of the sources in double precision; threads_mode
    None: the line deposit_threads is absent; fine: None or the cloud (cic, tsc)."""
    b = A.Inp(os.path.join(PROB, "tests/deposit_threads.athinput"))
    b.set("time", tlim=2.0)
    b.set("particles", deposit_max_level=1, particle_file=RANDOM)
    if threads_mode is None:
        b.drop("particles", "deposit_threads")
    else:
        b.set("particles", deposit_threads=threads_mode)
    if fine:
        b.set("particles", deposit_shape=fine, deposit_fine_shape=True)
    b.set("output1", file_type="bin", variable="tmunu", dt=1.0, double_precision=True)
    return b


def deck_dser(d):
    # the example as published: no dump (the executable of the branch has no
    # double_precision)
    b = deck_dep(d)
    return b.drop("output1")


BYTE = {  # name -> (branch, deck maker, basename of the run)
    "s3g": ("scalar-3", deck_s3g),
    "usr": ("scalar-3", deck_usr),
    "trk": ("cosmo-amr", deck_trk),
    "peak": ("cosmo-amr", deck_peak),
    "dser": ("build-openmp", deck_dser),
}

THREADS = {  # name -> (executable, threads, deposit_threads, fine)
    "d_ser": ("serial", 1, "private", None),
    "d_ser0": ("serial", 1, None, None),
    "d_p1": ("omp", 1, "private", None),
    "d_p4a": ("omp", 4, "private", None),
    "d_p4b": ("omp", 4, "private", None),
    "d_a4": ("omp", 4, "atomic", None),
    "f_ser": ("serial", 1, None, "cic"),
    "f_p1": ("omp", 1, "private", "cic"),
    "f_p4a": ("omp", 4, "private", "cic"),
    "f_p4b": ("omp", 4, "private", "cic"),
    "f_a4": ("omp", 4, "atomic", "cic"),
    "g_ser": ("serial", 1, None, "tsc"),
    "g_p4": ("omp", 4, "private", "tsc"),
}


def run_deck(exe, deck_maker, d, threads=1):
    os.makedirs(d, exist_ok=True)
    deck = deck_maker(d)
    with open(d + ".prepared.json", "w") as f:
        json.dump(rg.out_files(d), f)
    path = deck.write(os.path.join(d, "deck.athinput"))
    env = dict(os.environ, OMP_NUM_THREADS=str(threads))
    if threads > 1:
        places = subprocess.run([sys.executable, os.path.join(REPO, "scripts/omp_places.py"),
                                 str(threads)], capture_output=True, text=True).stdout.strip()
        env.update(OMP_PROC_BIND="true", OMP_PLACES=places)
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        rc = subprocess.run([exe, "-i", path, "-d", d], cwd=d, stdout=log,
                            stderr=subprocess.STDOUT, env=env).returncode
    return rc, round(time.time() - t0, 1)


def prepared(d):
    try:
        with open(d + ".prepared.json") as f:
            return json.load(f) + ["deck.athinput"]
    except OSError:
        return ["deck.athinput"]


# ---------------------------------------------------------------------------------------
# readers and differences
# ---------------------------------------------------------------------------------------
def table(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                rows.append([float(t) for t in s.split()])
            except ValueError:
                continue
    n = min(len(r) for r in rows)
    return np.array([r[:n] for r in rows])


def hist_diff(a, b):
    """largest difference of two histories over the largest number of the file."""
    x, y = table(a), table(b)
    if x.shape != y.shape:
        return float("inf")
    return float(np.abs(x - y).max()/np.abs(x).max())


def blocks(path):
    fd = athena_bin.read_bin(path, assemble=False)
    return {(b["level"],) + tuple(b["lloc"]): np.asarray(b["data"], dtype=np.float64)
            for b in fd["blocks"]}


def field_diff(da, db):
    """largest difference of the dumps of two run directories over the largest number
    of each dump; inf if the dumps or their MeshBlocks do not correspond."""
    fa = sorted(f for f in rg.out_files(da) if f.startswith("bin/"))
    fb = sorted(f for f in rg.out_files(db) if f.startswith("bin/"))
    if fa != fb or not fa:
        return float("inf")
    worst = 0.0
    for f in fa:
        x, y = blocks(os.path.join(da, f)), blocks(os.path.join(db, f))
        if set(x) != set(y):
            return float("inf")
        scale = max(np.abs(v).max() for v in x.values())
        if scale == 0.0:
            continue
        worst = max(worst, max(float(np.abs(x[k] - y[k]).max()) for k in x)/scale)
    return worst


def identity(d):
    """largest |mesh integral - particle sum| over sum m W: energy, momentum."""
    h = table(os.path.join(d, "dep.nrpic.hst"))
    smw = np.abs(h[:, 4])
    return float(max((np.abs(h[:, 8] - h[:, 4])/smw).max(),
                     (np.abs(h[:, 9:12] - h[:, 5:8]).max(axis=1)/smw).max()))


def same_files(da, db, skip):
    fa = [f for f in rg.out_files(da) if f not in skip]
    fb = [f for f in rg.out_files(db) if f not in skip]
    if fa != fb:
        return False, len(fa)
    for f in fa:
        with open(os.path.join(da, f), "rb") as x, open(os.path.join(db, f), "rb") as y:
            if x.read() != y.read():
                return False, len(fa)
    return True, len(fa)


def grep(path, words):
    try:
        with open(path, errors="replace") as f:
            return [ln.rstrip() for ln in f if any(w in ln for w in words)]
    except OSError:
        return []


# ---------------------------------------------------------------------------------------
def group_byte(a, out, summary):
    jobs = []
    for n, (branch, mk) in BYTE.items():
        jobs.append((n, "new", a.serial, mk))
        jobs.append((n, "branch", os.path.join(EXE_DIR, BRANCH_EXE[branch]), mk))
    codes = {}
    if not a.analyse_only:
        with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
            futs = {pool.submit(run_deck, exe, mk, os.path.join(out, "byte", n, lab)): (n, lab)
                    for n, lab, exe, mk in jobs}
            for fut in cf.as_completed(futs):
                codes[futs[fut]] = fut.result()
                print("ran byte %-5s %-6s exit %d  %.1f s" % (futs[fut] + codes[futs[fut]]),
                      flush=True)
        with open(os.path.join(out, "byte", "codes.json"), "w") as f:
            json.dump({"%s %s" % k: v for k, v in codes.items()}, f)
    else:
        with open(os.path.join(out, "byte", "codes.json")) as f:
            codes = {tuple(k.split()): tuple(v) for k, v in json.load(f).items()}
    ok = True
    res = {}
    for n, (branch, _) in BYTE.items():
        dn, db = os.path.join(out, "byte", n, "new"), os.path.join(out, "byte", n, "branch")
        skip = set(prepared(dn)) | set(prepared(db))
        r = rg.compare(n, db, dn, skip=skip)
        r["branch"] = branch
        r["exit"] = [codes[(n, "branch")][0], codes[(n, "new")][0]]
        r["wall_time_s"] = [codes[(n, "branch")][1], codes[(n, "new")][1]]
        want = [0, 0]
        good = (not r["other"]) and r["compared"] > 0 and r["exit"] == want
        r["verdict"] = "pass" if good else "FAIL"
        ok = ok and good
        res[n] = r
        print("byte %-5s (%s) files %2d identical %2d a %d b %d other %d  %s"
              % (n, branch, r["files"], len(r["identical"]), len(r["a"]), len(r["b"]),
                 len(r["other"]), r["verdict"]), flush=True)
        for f in r["other"]:
            print("      other: %s %s" % (f, r["details"].get(f, "")), flush=True)
    summary["byte"] = res
    # numbers of the candidate's runs
    num = {}
    d = os.path.join(out, "byte", "peak", "new")
    try:
        h = A.read_hst(os.path.join(d, "peak.nrpic.hst"))
        num["peak_meshblocks_first_last"] = [int(h["nmb"][0]), int(h["nmb"][-1])]
        num["peak_identity_E"] = float(np.max(np.abs(h["int_E"]/h["sum_mW"] - 1.0)))
        num["peak_particles_first_last"] = [int(h["np"][0]), int(h["np"][-1])]
    except (OSError, KeyError) as exc:
        num["peak_error"] = repr(exc)
    d = os.path.join(out, "byte", "trk", "new")
    try:
        t = np.loadtxt(os.path.join(d, "flrw.co_0.txt"), ndmin=2)
        num["trk_x_minus_line_last"] = float(t[-1, 2] - (2.5 + 0.5*t[-1, 1]))
        num["trk_records"] = int(len(t))
    except OSError as exc:
        num["trk_error"] = repr(exc)
    d = os.path.join(out, "byte", "s3g", "new")
    for f in rg.out_files(d):
        if f.endswith(".sf.con.hst"):
            num["s3g_con_columns"] = int(table(os.path.join(d, f)).shape[1])
    summary["byte_numbers"] = num
    return ok


def group_threads(a, out, summary):
    exe = {"serial": a.serial, "omp": a.omp}
    top = os.path.join(out, "threads")
    codes = {}
    if not a.analyse_only:
        def mk(mode, fine):
            return lambda d: deck_dep(d, mode, fine)
        ser = [n for n, v in THREADS.items() if v[1] == 1]
        par = [n for n, v in THREADS.items() if v[1] > 1]
        with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
            futs = {pool.submit(run_deck, exe[THREADS[n][0]], mk(THREADS[n][2], THREADS[n][3]),
                                os.path.join(top, n), 1): n for n in ser}
            for fut in cf.as_completed(futs):
                codes[futs[fut]] = fut.result()
        for n in par:                       # one at a time: each takes four cores
            e, th, mode, fine = THREADS[n]
            codes[n] = run_deck(exe[e], mk(mode, fine), os.path.join(top, n), th)
        for n in THREADS:
            print("ran threads %-6s exit %d  %.1f s" % ((n,) + codes[n]), flush=True)
        with open(os.path.join(top, "codes.json"), "w") as f:
            json.dump(codes, f)
    else:
        with open(os.path.join(top, "codes.json")) as f:
            codes = {k: tuple(v) for k, v in json.load(f).items()}
    D = lambda n: os.path.join(top, n)        # noqa: E731
    skip = {"random.nrp", "deck.athinput"}
    hst = lambda n: os.path.join(D(n), "dep.nrpic.hst")     # noqa: E731
    num, band = {}, {}

    def put(key, val, lo=None, hi=None):
        num[key] = val
        band[key] = [lo, hi]

    put("d_two_runs_4_threads_identical", same_files(D("d_p4a"), D("d_p4b"), skip)[0], 1, 1)
    put("d_p4_vs_p1_hist", hist_diff(hst("d_p4a"), hst("d_p1")), 0.0, 1.3e-12)
    put("d_p4_vs_p1_field", field_diff(D("d_p4a"), D("d_p1")), 0.0, 1.3e-12)
    put("d_a4_vs_p1_hist", hist_diff(hst("d_a4"), hst("d_p1")), 0.0, 1.3e-12)
    put("d_a4_vs_p1_field", field_diff(D("d_a4"), D("d_p1")), 0.0, 1.3e-12)
    put("d_p1_vs_serial_hist", hist_diff(hst("d_p1"), hst("d_ser")), 0.0, 1.3e-12)
    put("d_p1_vs_serial_field", field_diff(D("d_p1"), D("d_ser")), 0.0, 1.3e-12)
    with open(hst("d_ser"), "rb") as x, open(hst("d_ser0"), "rb") as y:
        put("d_serial_option_changes_nothing", x.read() == y.read(), 1, 1)
    put("d_serial_option_field", field_diff(D("d_ser"), D("d_ser0")), 0.0, 0.0)
    put("d_identity_worst", max(identity(D(n)) for n in THREADS if n.startswith("d_")),
        0.0, 1.0e-13)
    put("f_two_runs_4_threads_identical", same_files(D("f_p4a"), D("f_p4b"), skip)[0], 1, 1)
    put("f_p4_vs_p1_hist", hist_diff(hst("f_p4a"), hst("f_p1")), 0.0, 1.0e-12)
    put("f_p4_vs_p1_field", field_diff(D("f_p4a"), D("f_p1")), 0.0, 1.0e-12)
    put("f_a4_vs_p1_field", field_diff(D("f_a4"), D("f_p1")), 0.0, 1.0e-12)
    put("f_p1_vs_serial_hist", hist_diff(hst("f_p1"), hst("f_ser")), 0.0, 1.0e-12)
    put("f_p1_vs_serial_field", field_diff(D("f_p1"), D("f_ser")), 0.0, 1.0e-12)
    put("g_p4_vs_serial_field", field_diff(D("g_p4"), D("g_ser")), 0.0, 1.0e-12)
    put("f_identity_worst", max(identity(D(n)) for n in THREADS if n[0] in "fg"),
        0.0, 1.0e-13)
    # the fine shape must change the field (the branch is taken) and not the integrals
    cic0 = os.path.join(top, "c_ser0")
    if not a.analyse_only:
        codes["c_ser0"] = run_deck(a.serial, lambda d: deck_dep(d, None, None).set(
            "particles", deposit_shape="cic"), cic0, 1)
    put("f_fine_shape_changes_field", field_diff(D("f_ser"), cic0), 1.0e-3, None)
    # (columns 9 to 12, the mesh integrals of E and S_i, over sum m W; the probe and the
    # extrema of E, columns 14, 31, 32, are local and change with the shape)
    hf, h0 = table(hst("f_ser")), table(os.path.join(cic0, "dep.nrpic.hst"))
    put("f_fine_shape_changes_integrals",
        float((np.abs(hf[:, 8:12] - h0[:, 8:12]).max(axis=1)/np.abs(h0[:, 4])).max()),
        0.0, 1.0e-13)
    put("f_fine_shape_changes_whole_history", hist_diff(hst("f_ser"), os.path.join(
        cic0, "dep.nrpic.hst")), None, None)
    notes = grep(os.path.join(D("d_ser"), "athena.log"), ["deposit_threads"]) \
        + grep(os.path.join(D("d_p4a"), "athena.log"), ["private copy"])
    exits = {n: codes[n][0] for n in codes}
    ok = all(v == 0 for v in exits.values())
    for k, v in num.items():
        lo, hi = band[k]
        inside = (lo is None or v >= lo) and (hi is None or v <= hi)
        ok = ok and inside
        print("threads %-34s %-12s band [%s, %s] %s" % (k, ("%.3g" % v) if not isinstance(
            v, bool) else v, lo, hi, "" if inside else "OUTSIDE"), flush=True)
    summary["threads"] = dict(numbers=num, bands=band, exit=exits, notes=notes,
                              wall_time_s={n: codes[n][1] for n in codes})
    return ok


def group_mpi(a, out, summary):
    top = os.path.join(out, "mpi")
    os.makedirs(top, exist_ok=True)
    drv = os.path.join(HERE, "..", "mpi", "mpi_tests.py")
    res, ok = {}, True
    for case in ("t1_kerr", "t3_cluster"):
        d = os.path.join(top, case)
        if not a.analyse_only:
            with open(os.path.join(top, case + ".log"), "w") as log:
                rc = subprocess.run([sys.executable, drv, "--case", case, "--ranks", "1", "2",
                                     "--exe", a.mpi, "--out", d, "--figdir",
                                     os.path.join(top, "figs"), "--max-cores", "3"],
                                    stdout=log, stderr=subprocess.STDOUT).returncode
            print("ran mpi %s exit %d" % (case, rc), flush=True)
        with open(os.path.join(d, "compare.json")) as f:
            c = json.load(f)
        r = dict(exit=[c["runs"][k]["exit"] for k in ("1", "2")] if c.get("runs") else None,
                 particles=c.get("particles"), mpi=c.get("mpi", {}).get("np2"))
        r["files_identical"] = [k for k, v in c["bytes"].items() if v.get("np2")]
        r["files_differing"] = [k for k, v in c["bytes"].items() if not v.get("np2")]
        r["restart_rest_identical"] = all(v.get("np2_rest_identical", True)
                                          for v in c["bytes"].values())
        r["history_max_rel"] = max([v["np2"]["max_rel"] for v in c["histories"].values()
                                    if isinstance(v.get("np2"), dict)] or [0.0])
        r["history_worst"] = {k: v["np2"] for k, v in c["histories"].items()
                              if isinstance(v.get("np2"), dict)}
        snaps = [v["np2"] for v in c["snapshots"].values()]
        r["snapshot_max_abs"] = (max(snaps) if snaps and all(isinstance(s, float)
                                                             for s in snaps) else "differ")
        r["identity"] = c.get("identity")
        r["fields_max_rel"] = max([v["np2"]["max_rel"] for v in c.get("fields", {}).values()
                                   if isinstance(v.get("np2"), dict)] or [0.0])
        res[case] = r
    t1, t3 = res["t1_kerr"], res["t3_cluster"]
    # against the runs of the package with its branch executable, 1 and 2 ranks
    pk, pk_ok = {}, True
    off = 2*4 + 9*8 + 10*4
    for case, od in PACKAGE_RUNS.items():
        with open(os.path.join(od, "compare.json")) as f:
            pc = json.load(f)
        row = {"package_history_np2": {k: v["np2"]["max_rel"] for k, v in
                                       pc["histories"].items()
                                       if isinstance(v.get("np2"), dict)}}
        for n in ("np1", "np2"):
            da, db = os.path.join(od, n), os.path.join(top, case, n)
            fa = [f for f in rg.out_files(da) if f != "run.log"]
            fb = [f for f in rg.out_files(db) if f != "run.log"]
            ident, rst_ok, other, lines = [], [], [], set()
            for f in sorted(set(fa) | set(fb)):
                if f not in fa or f not in fb:
                    other.append(f)
                    continue
                with open(os.path.join(da, f), "rb") as x, open(os.path.join(db, f), "rb") as y:
                    xa, yb = x.read(), y.read()
                if xa == yb:
                    ident.append(f)
                    continue
                ta, ra = rg.split_dump(xa)
                tb, rb = rg.split_dump(yb)
                if (f.endswith(".rst") and ta is not None and tb is not None
                        and len(ra) == len(rb)
                        and ra[:off] + ra[off+36:] == rb[:off] + rb[off+36:]):
                    rst_ok.append(f)
                    sa = set(ln.split(b"#")[0].strip() for ln in ta.split(b"\n"))
                    sb = set(ln.split(b"#")[0].strip() for ln in tb.split(b"\n"))
                    lines |= set(x.decode().split("=")[0].strip() for x in sa ^ sb)
                else:
                    other.append(f)
            row[n] = dict(files=len(set(fa) | set(fb)), identical=len(ident),
                          restart_data_identical=rst_ok, other=other,
                          dump_parameters_differing=sorted(lines))
            pk_ok = pk_ok and not other
        pk[case] = row
    res["against_package_runs"] = pk
    checks = {
        "bytes_of_the_package_runs_on_1_and_2_ranks": pk_ok,
        "t1_runs_status_0": t1["exit"] == [0, 0],
        "t1_particle_files_identical": (not [f for f in t1["files_differing"]
                                             if not f.endswith(".prt")]
                                        and t1["restart_rest_identical"]),
        "t1_snapshots_identical": t1["snapshot_max_abs"] == 0.0,
        "t3_runs_status_0": t3["exit"] == [0, 0],
        "t3_positions_within_1e-13": (isinstance(t3["snapshot_max_abs"], float)
                                      and t3["snapshot_max_abs"] <= 1.0e-13),
        # the number of the READY (5e-13) is that of the history of the module; the
        # constraint statistics (largest relative constraint, a ratio of differences)
        # are reported with the package's own value beside them
        "t3_module_history_within_1e-11": t3["history_worst"].get(
            "cl.nrpic.hst", {}).get("max_rel", 1.0) <= 1.0e-11,
        "t3_identity_within_1e-14": all(v["max_dE_over_sum_mW"] <= 1.0e-14
                                        for v in (t3["identity"] or {}).values()),
        "t3_packets_sent": bool(t3["mpi"] and t3["mpi"]["deposit_packets"] > 0),
    }
    # the stop of an option that is not ported: deposit_fine_shape on two ranks
    d = os.path.join(top, "stop")
    if not a.analyse_only:
        os.makedirs(d, exist_ok=True)
        b = A.Inp(os.path.join(PROB, "tests/mpi_deposit_smr.athinput"))
        b.set("particles", deposit_fine_shape=True, particle_file=RANDOM)
        b.set("time", nlim=2)
        deck = b.write(os.path.join(d, "deck.athinput"))
        with open(os.path.join(d, "run.log"), "w") as log:
            rc = subprocess.run([MPIRUN, "--bind-to", "none", "-np", "2", a.mpi, "-i", deck,
                                 "-d", d], cwd=d, stdout=log, stderr=subprocess.STDOUT,
                                env=dict(os.environ, OMP_NUM_THREADS="1")).returncode
        with open(os.path.join(d, "exit.txt"), "w") as f:
            f.write("%d\n" % rc)
        # the same deck on one rank must run
        d1 = os.path.join(top, "stop_np1")
        os.makedirs(d1, exist_ok=True)
        with open(os.path.join(d1, "run.log"), "w") as log:
            rc1 = subprocess.run([a.mpi, "-i", deck, "-d", d1], cwd=d1, stdout=log,
                                 stderr=subprocess.STDOUT,
                                 env=dict(os.environ, OMP_NUM_THREADS="1")).returncode
        with open(os.path.join(d1, "exit.txt"), "w") as f:
            f.write("%d\n" % rc1)
    rc = int(open(os.path.join(d, "exit.txt")).read())
    rc1 = int(open(os.path.join(top, "stop_np1", "exit.txt")).read())
    msg = grep(os.path.join(d, "run.log"), ["has not been ported"])
    res["stop"] = dict(exit_two_ranks=rc, exit_one_rank=rc1, message=msg[:1])
    checks["stop_two_ranks_refused"] = (rc != 0 and bool(msg)
                                        and "deposit_fine_shape" in msg[0])
    checks["stop_one_rank_runs"] = (rc1 == 0)
    for k, v in checks.items():
        ok = ok and v
        print("mpi %-32s %s" % (k, "ok" if v else "FAILED"), flush=True)
    res["checks"] = checks
    summary["mpi"] = res
    return ok


def figure(out, summary):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(11.0, 3.4))
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.30, top=0.90, wspace=0.30)
    # (a) byte comparison per example
    if "byte" in summary:
        names = list(summary["byte"])
        x = np.arange(len(names))
        bot = np.zeros(len(names))
        for cls, col in (("identical", fs.SERIES[0]), ("a", fs.SERIES[1]),
                         ("b", fs.SERIES[2]), ("other", "k")):
            v = np.array([len(summary["byte"][n][cls]) for n in names], dtype=float)
            ax[0].bar(x, v, bottom=bot, color=col, label=cls, width=0.6)
            bot += v
        ax[0].set_xticks(x)
        ax[0].set_xticklabels(["%s\n%s" % (n, summary["byte"][n]["branch"]) for n in names],
                              fontsize=7)
        ax[0].set_ylabel("files against the branch executable")
        ax[0].legend(frameon=False, fontsize=7, ncol=2)
        ax[0].set_title("(a) one example per branch, bytes", fontsize=9)
    # (b) threads: differences and their bounds
    if "threads" in summary:
        num, band = summary["threads"]["numbers"], summary["threads"]["bands"]
        keys = [k for k in num if not isinstance(num[k], bool) and band[k][1] is not None
                and band[k][1] > 0]
        y = np.arange(len(keys))
        vals = np.array([max(num[k], 1.0e-18) for k in keys])
        ax[1].barh(y, vals, color=fs.SERIES[0], height=0.55)
        for i, k in enumerate(keys):
            ax[1].plot([band[k][1]]*2, [i - 0.4, i + 0.4], color="k", lw=1.2)
        ax[1].set_xscale("log")
        ax[1].set_xlim(1.0e-18, 1.0e-10)
        ax[1].set_yticks(y)
        ax[1].set_yticklabels([k.replace("_", " ") for k in keys], fontsize=6)
        ax[1].invert_yaxis()
        ax[1].set_xlabel("largest difference / largest number (bar: bound)")
        ax[1].set_title("(b) threaded build, deposit", fontsize=9)
    # (c) two ranks against one
    if "mpi" in summary:
        t1, t3 = summary["mpi"]["t1_kerr"], summary["mpi"]["t3_cluster"]
        idn = max(v["max_dE_over_sum_mW"] for v in t3["identity"].values())
        items = [("Kerr swarm:\nhistory", t1["history_max_rel"], None),
                 ("cluster:\npositions", t3["snapshot_max_abs"], 1.0e-13),
                 ("cluster:\nhistory", t3["history_max_rel"], 1.0e-11),
                 ("cluster:\nsource dumps", t3["fields_max_rel"], None),
                 ("cluster:\nidentity", idn, 1.0e-14)]
        x = np.arange(len(items))
        ax[2].bar(x, [max(float(v), 1.0e-18) if isinstance(v, float) else 1.0
                      for _, v, _ in items], color=fs.SERIES[0], width=0.55)
        for i, (_, _, b) in enumerate(items):
            if b:
                ax[2].plot([i - 0.4, i + 0.4], [b, b], color="k", lw=1.2)
        ax[2].set_yscale("log")
        ax[2].set_ylim(1.0e-18, 1.0e-8)
        ax[2].set_xticks(x)
        ax[2].set_xticklabels([n for n, _, _ in items], fontsize=7)
        ax[2].set_ylabel("2 ranks against 1 (bar: bound)")
        ax[2].set_title("(c) MPI build: %d particle files identical (Kerr swarm)"
                        % len(t1["files_identical"]), fontsize=9)
    fs.save(fig, os.path.join(out, "fig_quick_v05"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serial", required=True)
    ap.add_argument("--omp", default=None)
    ap.add_argument("--mpi", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--groups", default="byte,threads,mpi")
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--runs", default=None)
    a = ap.parse_args()
    figdir = os.path.abspath(a.out)
    os.makedirs(figdir, exist_ok=True)
    out = os.path.abspath(a.runs) if (a.analyse_only and a.runs) else figdir
    os.makedirs(os.path.join(out, "byte"), exist_ok=True)
    os.makedirs(os.path.join(out, "threads"), exist_ok=True)
    spath = os.path.join(figdir, "summary.json")
    summary = {}
    if os.path.exists(spath):
        with open(spath) as f:
            summary = json.load(f)
    summary.setdefault("exe", {})
    for k in ("serial", "omp", "mpi"):
        v = getattr(a, k)
        if v:
            summary["exe"][k] = dict(path=os.path.abspath(v), sha256=rg.sha256(v))
    groups = a.groups.split(",")
    ok = True
    if "byte" in groups:
        ok = group_byte(a, out, summary) and ok
    if "threads" in groups:
        ok = group_threads(a, out, summary) and ok
    if "mpi" in groups:
        ok = group_mpi(a, out, summary) and ok
    summary.setdefault("verdicts", {})
    summary["verdict"] = "PASS" if ok else "FAIL"
    summary["runs"] = out
    with open(spath, "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    summary["runs"] = out
    try:
        figure(figdir, summary)
    except Exception as exc:                  # the numbers stand without the figure
        print("figure failed:", repr(exc))
    print("QUICK", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
