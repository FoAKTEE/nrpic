"""Shared helpers of work package omp (threaded processor build): the regression set-ups,
one function that runs a case with a given executable, thread count and thread placement,
and the comparison of the outputs of two runs (byte for byte, then number by number).

Nothing here is a simulation code: the functions start the AthenaK executables of this
repository and read their output files.
"""
import filecmp
import hashlib
import json
import os
import re
import resource
import subprocess
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
IC = os.path.join(SCRATCH, "regress", "ic")          # made by earlier packages of core
IC2 = os.path.join(SCRATCH, "omp", "ic")             # made by make_ic.sh of this package

EXES = {
    "R": "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena",   # release core-v0.3
    "S": os.path.join(WT, ".work/build_cpu/src/athena"),          # serial, this branch
    "O2": os.path.join(WT, ".work/build_omp_o2/src/athena"),      # OpenMP, flags of S
    "O3": os.path.join(WT, ".work/build_omp/src/athena"),         # OpenMP, -O3 -DNDEBUG
    "D": os.path.join(WT, ".work/build_omp_dbg/src/athena"),      # O3 + Kokkos debug, bounds
}

OS = "os_R5_lattice_N2176_s1"
RST = "\n<output77>\nfile_type = rst\ndcycle    = %d\n"

# name: deck (relative to the worktree), files linked into the run directory, command-line
# arguments, text appended to the deck, what the case exercises
CASES = {
    "geo": dict(inp="problems/kerr/geodesic.athinput", files=[],
                args=["time/tlim=20.0", "particles/hist_dcycle=100"],
                what="one test particle, analytic Kerr metric, implicit midpoint"),
    "boris": dict(inp="problems/kerr/geodesic.athinput", files=[],
                  args=["time/tlim=20.0", "particles/hist_dcycle=100",
                        "particles/pusher=boris", "particles/metric=lattice"],
                  what="one test particle, spacetime-Boris pusher on the virtual lattice"),
    "dep": dict(inp="problems/tests/deposit_smr.athinput", files=[IC + "/random.nrp"],
                args=["time/tlim=2.0", "particles/deposit_max_level=1"],
                what="1e4 particles, static flat metric on a refined mesh, deposit"),
    "east": dict(inp="problems/cosmo/east.athinput",
                 files=[IC + "/east16/particles.nrp", IC + "/east16/fields.bin"],
                 args=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                       "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=20",
                       "particles/snap_dt=0.2", "particles/traj_ntrack=46"],
                 append=RST % 20,
                 what="periodic cosmology with Z4c, deposit, filter, compensation, 16^3"),
    "os": dict(inp="problems/os/os_smr_dev.athinput",
               files=[IC + "/os/%s.nrp" % OS, IC + "/os/%s.tab" % OS],
               args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=16",
                     "meshblock/nx2=16", "meshblock/nx3=16", "time/nlim=3",
                     "particles/particle_file=%s.nrp" % OS,
                     "problem/comp0_file=%s.tab" % OS, "particles/snap_dt=0.05",
                     "output2/dt=0.1"],
               what="Oppenheimer-Snyder ball with Z4c on a statically refined mesh"),
    "jeans": dict(inp="athenak/inputs/tests/jeans_wave.athinput", files=[],
                  args=["time/nlim=20", "gravity/show_defect=2"],
                  what="gas with self-gravity (multigrid), periodic, uniform mesh"),
    "binary": dict(inp="athenak/inputs/tests/binary_gravity.athinput", files=[],
                   args=["time/nlim=1"],
                   what="gas with self-gravity (multigrid) on four refinement levels"),
    "newton": dict(inp="problems/newton/periodic.athinput", files=[IC2 + "/wave32.nrp"],
                   args=["time/tlim=0.2", "particles/snap_dt=0.1",
                         "particles/particle_file=wave32.nrp"],
                   what="Newtonian mode, periodic box, plane wave, 32^3, 40 steps"),
    "coll": dict(inp="problems/tests/coll_box.athinput", files=[IC2 + "/box.nrp"],
                 args=["time/tlim=0.2", "particles/snap_dt=0.1", "meshblock/nx1=16",
                       "meshblock/nx2=16", "meshblock/nx3=16"],
                 what="Monte Carlo collisions, 2e4 particles, two temperatures, 8 blocks"),
    "kg": dict(inp="problems/scalar/kg_wave.athinput", files=[],
               args=["time/tlim=0.25"], append=RST % 1000000,
               what="Klein-Gordon test field on Z4c, 16^3"),
    "noise": dict(inp="problems/scalar/noise_power.athinput", files=[],
                  args=["time/nlim=16"],
                  what="scalar field with stochastic sources (mode synthesis)"),
    "bench": dict(inp="problems/tests/z4c_bench.athinput", files=[],
                  args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "time/nlim=8"],
                  append=RST % 8,
                  what="vacuum puncture, Z4c, uniform 64^3 in eight blocks"),
    # the deck has its own restart block (output2): with dt = 1e30 it writes the initial
    # state and, at the end of the run, the final one (no second restart block: AthenaK
    # refuses two)
    "punc": dict(inp="problems/puncture/horizon_calib.athinput", files=[],
                 args=["time/nlim=5", "fastflow/find_every=4", "refined_region1/level=2",
                       "refined_region2/level=2", "output2/dt=1.0e30"],
                 what="vacuum puncture on a refined mesh, six tracers, horizon finder"),
}
REGRESS = ["geo", "boris", "dep", "east", "os", "jeans", "binary", "newton", "coll", "kg",
           "noise", "bench", "punc"]

SKIP = ("run.log", "summary.json", "kernel_timer.txt")
# floor of the verdict measure rel_floor, as a fraction of the largest number of the file
FLOOR = 1.0e-6
# quantities decided by comparing a reduced sum with a threshold: the number of V cycles
# of the multigrid solver with threshold = 0 ("until the defect stops falling") changes
# when the grouping of the defect norm changes. Reported apart, not judged.
DECISION_COLUMNS = ("mg_cycles",)
NWT_DECISION_WORDS = (50,)   # .rst.prt.nwt: word 0 magic, 1-50 state; 50 = V cycles
LOGKEYS = ("defect", "Potential", "Acceleration", "Error", "L1", "norm")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def loadavg():
    with open("/proc/loadavg") as f:
        return float(f.read().split()[0])


def thread_env(threads, bind="", places=""):
    """Environment of a run: the session's variables are not passed on, only these."""
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": os.environ.get("HOME", "/tmp"),
           "LANG": "C", "OMP_NUM_THREADS": str(threads), "OPENBLAS_NUM_THREADS": "1",
           "MKL_NUM_THREADS": "1"}
    if bind:
        env["OMP_PROC_BIND"] = bind
    if places:
        env["OMP_PLACES"] = places
    return env


TIMER_LIB = os.path.join(SCRATCH, "omp", "tools", "libkernel_timer.so")


def run_case(exe, case, rundir, threads=1, bind="", places="", extra_args=(), wall=3600,
             spec=None, profile=False, mode=""):
    """Runs one case in rundir (created); returns a record with the wall time, the time of
    the step loop and the zone-cycles per second that the code prints at the end."""
    c = spec if spec is not None else CASES[case]
    os.makedirs(rundir, exist_ok=True)
    deck = os.path.join(WT, c["inp"])
    text = open(deck).read() + c.get("append", "")
    if mode == "priv" and "<particles>\n" in text:
        # the new option of this package: one private copy of the sources per thread
        text = text.replace("<particles>\n", "<particles>\ndeposit_threads = private\n", 1)
    local = os.path.join(rundir, os.path.basename(deck))
    with open(local, "w") as f:
        f.write(text)
    for path in c["files"]:
        link = os.path.join(rundir, os.path.basename(path))
        if not os.path.lexists(link):
            os.symlink(path, link)
    cmd = [exe, "-i", os.path.basename(deck)] + list(c["args"]) + list(extra_args)
    places_asked = places
    if places.startswith("auto"):
        # the least busy cores right now (scripts/omp_places.py); "auto1": one hardware
        # thread per core
        pc = ["python3", os.path.join(WT, "scripts", "omp_places.py"), str(threads)]
        if places == "auto1":
            pc.append("--one-thread-per-core")
        places = subprocess.run(pc, capture_output=True, text=True, check=True).stdout.strip()
    env = thread_env(threads, bind, places)
    if profile:
        # time per kernel through the Kokkos tools interface (tools/kernel_timer.cpp)
        env["KOKKOS_TOOLS_LIBS"] = TIMER_LIB
        env["KERNEL_TIMER_OUT"] = "kernel_timer.txt"
    load0 = loadavg()
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    with open(os.path.join(rundir, "run.log"), "w") as log:
        try:
            rc = subprocess.run(cmd, cwd=rundir, stdout=log, stderr=subprocess.STDOUT,
                                env=env, timeout=wall).returncode
        except subprocess.TimeoutExpired:
            rc = -9
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_s = (ru1.ru_utime + ru1.ru_stime) - (ru0.ru_utime + ru0.ru_stime)
    rec = {"case": case, "exe": exe, "threads": threads, "bind": bind, "places": places,
           "places_asked": places_asked, "cpu_s": round(cpu_s, 3), "mode": mode,
           "cmd": cmd, "rundir": rundir, "exit": rc, "wall_s": round(time.time() - t0, 3),
           "load_before": load0, "load_after": loadavg()}
    rec.update(parse_log(os.path.join(rundir, "run.log")))
    # share of the asked processor time that the run obtained (1: every thread ran all
    # the time; hardware threads shared with other jobs do not show here)
    rec["cpu_share"] = round(cpu_s/(rec["wall_s"]*threads), 3) if rec["wall_s"] > 0 else 0.0
    if profile:
        rec["kernels"] = read_kernels(os.path.join(rundir, "kernel_timer.txt"))
    return rec


def read_kernels(path):
    """The table of tools/kernel_timer.cpp: {name: [seconds, calls]}, plus the total time
    in kernels and the run time."""
    out = {"kernels": {}}
    try:
        with open(path) as f:
            for ln in f:
                if ln.startswith("# total_in_kernels"):
                    out["total_in_kernels"] = float(ln.split()[2])
                elif ln.startswith("# run_time"):
                    out["run_time"] = float(ln.split()[2])
                elif not ln.startswith("#"):
                    sec, calls, typ, name = ln.rstrip("\n").split(" ", 3)
                    out["kernels"][name] = [float(sec), int(calls)]
    except OSError:
        pass
    return out


def parse_log(path):
    """Step-loop time, zone-cycles per second and number of cycles from an AthenaK log."""
    out = {}
    try:
        text = open(path, errors="replace").read()
    except OSError:
        return out
    m = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", text)
    if m:
        out["loop_s"] = float(m.group(1))
    m = re.search(r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)", text)
    if m:
        out["zcps"] = float(m.group(1))
    m = re.findall(r"cycle=(\d+)", text)
    if m:
        out["ncycle"] = int(m[-1])
    m = re.search(r"Terminating on (.*)", text)
    if m:
        out["end"] = m.group(1).strip()
    m = re.search(r"Number of MeshBlocks\s*=\s*(\d+)", text) or \
        re.search(r"(\d+) MeshBlocks", text)
    if m:
        out["nmb"] = int(m.group(1))
    out["nan"] = bool(re.search(r"\bnan\b|\binf\b", text))
    return out


# ------------------------------------------------------------------ comparison of two runs

def _column_names(path):
    """Names of the columns from a header line '# [1]=time [2]=...', or {}."""
    names = {}
    with open(path, errors="replace") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            for m in re.finditer(r"\[(\d+)\]=(\S+)", ln):
                names[int(m.group(1)) - 1] = m.group(2)
    return names


def _text_table(path):
    rows = []
    with open(path, errors="replace") as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            try:
                rows.append([float(v) if not re.fullmatch(r"[0-9a-fA-F]{16}", v)
                             else float(int(v, 16) % (1 << 52)) for v in ln.split()])
            except ValueError:
                return None
    if not rows or any(len(r) != len(rows[0]) for r in rows):
        return None
    return np.array(rows)


def _words(path, size):
    """The file as words of `size` bytes, aligned at its end (the data of the binary
    formats of this code are doubles, or 4-byte reals in AthenaK's mesh files, behind a
    header)."""
    raw = np.fromfile(path, dtype=np.uint8)
    n = len(raw)//size
    return raw[len(raw) - n*size:].view(np.float64 if size == 8 else np.float32), \
        raw[:len(raw) - n*size]


def _rst_data(path):
    """(data of all MeshBlocks as float64, parameter dump) of an AthenaK restart file, or
    (None, None) if the layout is not recognised."""
    raw = open(path, "rb").read()
    i = raw.find(b"<par_end>\n")
    if i < 0:
        return None, None
    h = i + len(b"<par_end>\n")
    nmb = int(np.frombuffer(raw[h:h + 4], dtype=np.int32)[0])
    if nmb <= 0:
        return None, None
    n = len(raw)
    for p in range(h, min(n - 7, h + (1 << 20))):
        ds = int(np.frombuffer(raw[p:p + 8], dtype=np.uint64)[0])
        if ds % 8 == 0 and p + 8 + nmb*ds == n:
            return np.frombuffer(raw[p + 8:], dtype=np.float64), raw[:i]
    return None, None


def _athena_bin_start(path):
    """Offset of the data of an AthenaK binary mesh output (after the text header and the
    parameter dump: the line 'header offset=N' is followed by N bytes of dump)."""
    raw = open(path, "rb").read(1 << 16)
    m = re.search(rb"header offset=(\d+)\n", raw)
    return m.end() + int(m.group(1)) if m else 0


def _is_athena_bin(path):
    with open(path, "rb") as f:
        return f.read(20).startswith(b"Athena binary output")


def number_diff(fa, fb):
    """How two files that differ as bytes differ as numbers. Returns a dictionary:
    kind, n (numbers compared), ndiff (numbers that differ), abs (largest difference),
    rel_file (largest difference over the largest magnitude among the numbers that
    differ: the measure used for the verdict), rel_entry (largest difference relative to
    the entry itself, 1 for an entry that is rounding noise around zero), rel_floor (the
    measure of the verdict: largest |a - b|/max(|a|, |b|, FLOOR x the largest magnitude
    of the file), so that a number of moderate size is judged against itself, and rounding
    noise of a number that cancels to nearly zero against the floor), rel_max (the
    measure of the verdict of the predictions: largest |a - b| over the largest magnitude
    in the file; for text tables over the largest number outside the integer columns)."""
    name = os.path.basename(fa)
    decision = {}
    if name.endswith(".rst"):
        # AthenaK restart file (outputs/restart.cpp): parameter dump up to '<par_end>\n',
        # a binary header (nmb_total, root level, RegionSize and RegionIndcs written as raw
        # structs, whose padding bytes are uninitialised memory and differ from run to run,
        # time, dt, cycle, locations and costs of the MeshBlocks, tracker positions), the
        # size of the data of one MeshBlock, then the data of every MeshBlock. Only the
        # data are compared; the dump differs when the deck differs (deposit_threads).
        da_, ha = _rst_data(fa)
        db_, hb = _rst_data(fb)
        if da_ is not None and db_ is not None and da_.size == db_.size:
            kind = "rst-data" + ("" if ha == hb else "+params")
            if np.array_equal(da_.view(np.uint64), db_.view(np.uint64)):
                return {"kind": kind, "n": int(da_.size), "ndiff": 0, "abs": 0.0,
                        "rel_file": 0.0, "rel_entry": 0.0, "rel_floor": 0.0, "rel_max": 0.0}
            return _real_diff(da_, db_, kind)
    if os.path.getsize(fa) != os.path.getsize(fb) and not name.endswith((".hst", ".txt",
                                                                         ".dat")):
        return {"kind": "size", "sizes": [os.path.getsize(fa), os.path.getsize(fb)]}
    a = b = None
    kind = "text"
    if name.endswith((".hst", ".txt", ".dat", ".tab", ".csv")):
        a, b = _text_table(fa), _text_table(fb)
        if a is None or b is None or a.shape != b.shape:
            return {"kind": "text-shape",
                    "shapes": [None if a is None else list(a.shape),
                               None if b is None else list(b.shape)]}
    else:
        size = 4 if _is_athena_bin(fa) else 8
        kind = "real%d" % size
        (a, ha), (b, hb) = _words(fa, size), _words(fb, size)
        if size == 4:
            # data only: the header text read as reals gives absurd magnitudes
            sa, sb = _athena_bin_start(fa), _athena_bin_start(fb)
            na, nb = (os.path.getsize(fa) - sa)//4, (os.path.getsize(fb) - sb)//4
            a, b = a[len(a) - na:], b[len(b) - nb:]
        if not np.array_equal(ha, hb):
            kind += "+head"
    if kind == "text":
        # Judged against the largest number of the table, columns of integers (cycle,
        # particle and block counts) left out: a history holds sums that cancel (net
        # momentum of a symmetric state, 1e-13) next to sums that do not (energy, 1 to
        # 100); the rounding of the first is as large as they are, and a lost update
        # would show in both at 1e-6 of the second or more.  rel_column (largest
        # difference over the largest magnitude of its own column) is recorded too.
        a2 = np.atleast_2d(np.asarray(a, dtype=np.float64))
        b2 = np.atleast_2d(np.asarray(b, dtype=np.float64)).copy()
        for c, nm in _column_names(fa).items():
            if nm in DECISION_COLUMNS and c < a2.shape[1]:
                nd_c = int(np.sum(a2[:, c] != b2[:, c]))
                if nd_c:
                    decision[nm] = {"rows_differ": nd_c,
                                    "max_abs": float(np.max(np.abs(a2[:, c] - b2[:, c])))}
                b2[:, c] = a2[:, c]
        with np.errstate(invalid="ignore", over="ignore"):
            dif = (a2 != b2) & ~(np.isnan(a2) & np.isnan(b2))
            nd = int(dif.sum())
            ad = np.where(dif, np.abs(a2 - b2), 0.0)
            bad = ~np.isfinite(ad)
            ad = np.where(bad, 0.0, ad)
            fa = np.where(np.isfinite(a2), a2, 0.0)
            fb = np.where(np.isfinite(b2), b2, 0.0)
            cscale = np.maximum(np.abs(fa), np.abs(fb)).max(axis=0)
            isint = np.all(fa == np.round(fa), axis=0) & np.all(fb == np.round(fb), axis=0)
            fscale = float(cscale[~isint].max()) if (~isint).any() else float(cscale.max())
            cold = ad.max(axis=0)
            relc = np.where(cscale > 0, cold/np.where(cscale > 0, cscale, 1.0), 0.0)
            fl = FLOOR*fscale
            den = np.maximum(np.maximum(np.abs(fa), np.abs(fb)), fl)
            relf = np.where(dif & ~bad & (den > 0), ad/np.where(den > 0, den, 1.0), 0.0)
            relf[:, isint] = 0.0
        return {"kind": kind, "n": int(a2.size), "ndiff": nd, "nonfinite": int(bad.sum()),
                "rel_floor": float(relf.max()), "decision": decision,
                "rel_max": float(cold.max()/fscale) if fscale > 0 else 0.0,
                "abs": float(cold.max()), "scale": fscale,
                "rel_file": float(cold.max()/fscale) if fscale > 0 else 0.0,
                "rel_column": float(relc.max()), "worst_column": int(np.argmax(relc)) + 1,
                "int_columns_differ": int((isint & (cold > 0)).sum())}
    a = np.asarray(a, dtype=np.float64).ravel()
    b = np.asarray(b, dtype=np.float64).ravel().copy()
    if name.endswith(".nwt"):
        for w in NWT_DECISION_WORDS:
            if w < a.size and a[w] != b[w]:
                decision["mg_cycles"] = {"values": [float(a[w]), float(b[w])]}
                b[w] = a[w]
    r = _real_diff(a, b, kind)
    if decision:
        r["decision"] = decision
    return r


def _real_diff(a, b, kind):
    """Number comparison of two arrays of reals of equal length (see number_diff)."""
    with np.errstate(invalid="ignore", over="ignore"):
        dif = (a != b) & ~(np.isnan(a) & np.isnan(b))
        nd = int(dif.sum())
        if nd == 0:
            return {"kind": kind, "n": int(a.size), "ndiff": 0, "abs": 0.0, "rel_file": 0.0,
                    "rel_entry": 0.0, "rel_floor": 0.0, "rel_max": 0.0}
        # largest magnitude of the file, over words that can be data: header words of the
        # binary formats read as reals (text, packed integers) can be absurdly large
        fin = np.isfinite(a) & np.isfinite(b) & (np.abs(a) < 1.0e30) & (np.abs(b) < 1.0e30)
        fmax = float(max(np.abs(a[fin]).max(initial=0.0), np.abs(b[fin]).max(initial=0.0)))
        da, db = a[dif], b[dif]
        ad = np.abs(da - db)
        scale = np.maximum(np.abs(da), np.abs(db))
        bad = ~np.isfinite(ad)
        smax = float(np.nanmax(np.where(np.isfinite(scale), scale, 0.0)))
        rel_entry = np.where(scale > 0, ad/np.where(scale > 0, scale, 1.0), 0.0)
        den = np.maximum(scale, FLOOR*fmax)
        rel_floor = np.where(den > 0, ad/np.where(den > 0, den, 1.0), 0.0)
        return {"kind": kind, "n": int(a.size), "ndiff": nd,
                "nonfinite": int(bad.sum()), "scale_file": fmax,
                "rel_max": float(np.nanmax(np.where(bad, 0.0, ad)))/fmax if fmax > 0 else 0.0,
                "rel_floor": float(np.nanmax(np.where(bad, 0.0, rel_floor))),
                "abs": float(np.nanmax(np.where(bad, 0.0, ad))),
                "rel_file": float(np.nanmax(np.where(bad, 0.0, ad))/smax) if smax > 0
                else 0.0,
                "rel_entry": float(np.nanmax(np.where(bad, 0.0, rel_entry)))}


def log_results(path):
    with open(path, errors="replace") as f:
        return [ln for ln in f if any(k in ln for k in LOGKEYS) and "time" not in ln]


def compare_dirs(da, db):
    """Every output file of two run directories: identical as bytes, or how it differs."""
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    same, differ = [], {}
    for n in sorted(names):
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if n in SKIP or os.path.islink(fa) or n.endswith(".athinput"):
            continue
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ[n] = {"kind": "missing"}
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ[n] = number_diff(fa, fb)
    la = log_results(os.path.join(da, "run.log"))
    lb = log_results(os.path.join(db, "run.log"))
    # V cycles of the gas multigrid solver (stop on a threshold of a reduced defect norm)
    ca = sum("MG iteration" in x for x in la)
    cb = sum("MG iteration" in x for x in lb)
    if la or lb:
        if la == lb:
            same.append("run.log result lines (%d)" % len(la))
        else:
            differ["run.log result lines"] = {"kind": "log", "n": len(la),
                                              "ndiff": sum(x != y for x, y in zip(la, lb))
                                              + abs(len(la) - len(lb))}
    worst = worst_floor = worst_max = 0.0
    hard = False
    decisions = {}
    for n, v in differ.items():
        if v["kind"] in ("missing", "size", "text-shape") or v.get("nonfinite", 0) \
                or v.get("int_columns_differ", 0):
            hard = True
        if v.get("decision"):
            decisions[n] = v["decision"]
    if ca != cb:
        decisions["run.log"] = {"mg_iterations": [ca, cb]}
        worst = max(worst, v.get("rel_file", 0.0))
        worst_floor = max(worst_floor, v.get("rel_floor", 0.0))
        worst_max = max(worst_max, v.get("rel_max", 0.0))
    return {"identical": same, "differ": differ, "worst_rel_file": worst,
            "worst_rel_floor": worst_floor, "worst_rel_max": worst_max,
            "structural_difference": hard,
            "decisions": decisions}


def dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")
