"""Helpers of the tests of the initial-data solver, second pass (tracks/core/JOURNAL-idsolve2.md).

A test script is one registered run (harness/bin/nrpic-run submit --launcher local): it
writes the particle files and the input files of its cases into $NRPIC_RUN_DIR/<case>/,
runs the cases side by side, and analyses them; numbers and figures are copied to this
directory."""
import concurrent.futures
import json
import os
import shutil
import struct
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FIGS = os.path.join(HERE, "figs")
sys.path.insert(0, os.path.join(HERE, "..", "idsolve"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "problems", "idsolve"))

import idlib  # noqa: E402

MAKE_IC = os.path.join(WT, "problems", "idsolve", "make_ic.py")
MAKE_BALL = os.path.join(WT, "problems", "ic", "make_ball.py")
EXE = os.path.join(WT, ".work", "build_cpu", "src", "athena")
FIRST_PASS = "/data/haiyangw/nrpic/scratch/core/exe/core_id-solver/athena_cpu"
RELEASE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"


def run_root():
    """Output directory of the registered run (or a scratch directory by hand)."""
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join("/data/haiyangw/nrpic/scratch/core/tmp/idsolve2",
                         "byhand-" + time.strftime("%H%M%S"))
    os.makedirs(d, exist_ok=True)
    return d


def run_id():
    return os.path.basename(os.environ.get("NRPIC_RUN_DIR", "").rstrip("/")) or "by hand"


def make_input(base, out, sets):
    """Copy the input file base to out with the options of sets, a dict
    {"block/key": value}: an existing line is replaced, a new one is appended to its
    block (a block that is absent is added at the end)."""
    todo = {}
    for k, v in sets.items():
        b, key = k.split("/")
        todo.setdefault(b, {})[key] = v
    lines, block = [], None

    def flush(b):
        for key, v in todo.pop(b, {}).items():
            lines.append("%-14s = %s\n" % (key, v))
    with open(base) as f:
        for line in f:
            st = line.strip()
            if st.startswith("<") and st.endswith(">"):
                if block is not None:
                    while lines and not lines[-1].strip():
                        lines.pop()
                    flush(block)
                    lines.append("\n")
                block = st[1:-1]
                lines.append(line)
                continue
            if block in todo and "=" in st and not st.startswith("#"):
                key = st.split("=")[0].strip()
                if key in todo[block]:
                    lines.append("%-14s = %s\n" % (key, todo[block].pop(key)))
                    continue
            lines.append(line)
    if block is not None:
        flush(block)
    for b in list(todo):
        lines.append("\n<%s>\n" % b)
        flush(b)
    with open(out, "w") as f:
        f.writelines(lines)


def py(*args):
    return [sys.executable] + list(args)


def run_case(case):
    """case: dict(name, dir, steps = list of argv). Returns (name, seconds, status)."""
    os.makedirs(case["dir"], exist_ok=True)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    with open(os.path.join(case["dir"], "run.log"), "a") as log:
        for argv in case["steps"]:
            log.write("$ " + " ".join(argv) + "\n")
            log.flush()
            r = subprocess.run(argv, cwd=case["dir"], stdout=log, stderr=subprocess.STDOUT,
                               env=env)
            if r.returncode != 0 and not case.get("may_fail", False):
                return case["name"], time.time() - t0, "failed (exit %d)" % r.returncode
    return case["name"], time.time() - t0, "completed"


def run_cases(cases, jobs):
    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, sec, st in ex.map(run_case, cases):
            out[name] = dict(wall_s=round(sec, 1), status=st)
            print("case %s: %s in %.0f s" % (name, st, sec), flush=True)
    return out


def mesh(n, mb, half=None):
    s = {"mesh/nx1": n, "mesh/nx2": n, "mesh/nx3": n, "meshblock/nx1": mb,
         "meshblock/nx2": mb, "meshblock/nx3": mb}
    if half is not None:
        for d in "123":
            s["mesh/x%smin" % d] = -half
            s["mesh/x%smax" % d] = half
    return s


def read_idvector(path):
    """<basename>.idvector.bin -> dict with n, box, W (3 arrays), s (3), F (3), M (3), M0 (3),
    arrays indexed [i, j, k]."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRIDVEC1":
            raise ValueError("%s: bad magic" % path)
        n = struct.unpack("3q", f.read(24))
        box = struct.unpack("6d", f.read(48))
        nf, = struct.unpack("q", f.read(8))
        nc = n[0]*n[1]*n[2]
        a = [np.fromfile(f, dtype=np.float64, count=nc).reshape(n, order="F")
             for _ in range(nf)]
    return dict(n=n, box=box, W=a[0:3], s=a[3:6], F=a[6:9], M=a[9:12], M0=a[12:15])


BLK_FIELDS = ("psi", "K", "A2", "E", "H", "F7", "H0", "Wx", "Wy", "Wz", "Mx", "My", "Mz",
              "M0x", "M0y", "M0z")


def read_blk(path):
    """<basename>.idsolve.blk.bin (refined meshes) -> dict with nmb, n (cells of a block),
    level[m], box[m] (6 numbers) and the fields as arrays [m, i, j, k]."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRIDBLK1":
            raise ValueError("%s: bad magic" % path)
        nmb, n1, n2, n3, nf = struct.unpack("5q", f.read(40))
        level = np.zeros(nmb, dtype=np.int64)
        box = np.zeros((nmb, 6))
        for m in range(nmb):
            level[m], = struct.unpack("q", f.read(8))
            box[m] = struct.unpack("6d", f.read(48))
        out = dict(nmb=nmb, n=(n1, n2, n3), level=level, box=box)
        for name in BLK_FIELDS[:nf]:
            a = np.fromfile(f, dtype=np.float64, count=nmb*n1*n2*n3)
            out[name] = a.reshape((nmb, n3, n2, n1)).transpose(0, 3, 2, 1)
    return out


def blk_coords(d):
    """Cell centres of a block dump: arrays X, Y, Z of shape [m, i, j, k], and dx[m]."""
    n1, n2, n3 = d["n"]
    X = np.zeros((d["nmb"], n1, n2, n3))
    Y = np.zeros_like(X)
    Z = np.zeros_like(X)
    dx = np.zeros(d["nmb"])
    for m in range(d["nmb"]):
        b = d["box"][m]
        x = idlib.centres(n1, b[0], b[1])
        y = idlib.centres(n2, b[2], b[3])
        z = idlib.centres(n3, b[4], b[5])
        X[m], Y[m], Z[m] = np.meshgrid(x, y, z, indexing="ij")
        dx[m] = (b[1] - b[0])/n1
    return X, Y, Z, dx


def summary(path):
    """Summary lines of <basename>.idsolve.txt as one string, and the records."""
    rows, last = idlib.read_idsolve_txt(path)
    tail = [ln[1:].strip() for ln in open(path) if ln.startswith("#")]
    return rows, [t for t in tail if t.startswith(("converged", "NOT", "vector", "far"))]


def far_line(path):
    """M_ADM, P_ADM (3), J_ADM (3) of the record, or None."""
    import re
    for ln in open(path):
        if ln.startswith("# far field:"):
            v = [float(w) for w in re.findall(r"[-+]?\d\.\d+e[-+]\d+", ln)]
            return dict(M=v[0], P=v[1:4], J=v[4:7])
    return None


def publish(files):
    """Copy numbers and figures of the run directory to this directory (tracked)."""
    for src in files:
        dst = os.path.join(FIGS if src.endswith((".png", ".pdf")) else HERE,
                           os.path.basename(src))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)


def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
        f.write("\n")
