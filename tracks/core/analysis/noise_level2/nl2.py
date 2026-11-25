"""Helpers of package noise-level2 (tracks/core/JOURNAL-noise-level2.md): input files
with set or added parameters, runs, and the readers of the per-mode record
<basename>.sf.NNNNN.rmodes written with <scalar_field> noise_rmodes_dump = true."""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROB = os.path.join(REPO, "problems", "scalar")
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "harness", "style"))


def write_input(src, dst, params):
    """Copy the input file src to dst with params {"block/name": value} set (replaced
    where the line exists, added at the top of the block otherwise)."""
    lines = open(src).read().splitlines()
    want = {}
    for key, val in params.items():
        blk, name = key.split("/")
        want.setdefault(blk, {})[name] = str(val)
    out, block, done = [], None, set()
    for ln in lines:
        s = ln.strip()
        if s.startswith("<") and s.endswith(">"):
            block = s[1:-1]
            out.append(ln)
            for name, val in want.get(block, {}).items():
                if not any(l.split("=")[0].strip() == name for l in block_lines(lines, block)):
                    out.append(f"{name} = {val}")
                    done.add((block, name))
            continue
        if block in want and "=" in s and not s.startswith("#"):
            name = s.split("=")[0].strip()
            if name in want[block]:
                out.append(f"{name} = {want[block][name]}")
                done.add((block, name))
                continue
        out.append(ln)
    for blk, d in want.items():
        rest = [(name, val) for name, val in d.items() if (blk, name) not in done]
        if rest:
            out.append(f"<{blk}>")
            out += [f"{name} = {val}" for name, val in rest]
    open(dst, "w").write("\n".join(out) + "\n")
    return dst


def block_lines(lines, block):
    res, cur = [], None
    for ln in lines:
        s = ln.strip()
        if s.startswith("<") and s.endswith(">"):
            cur = s[1:-1]
            continue
        if cur == block and "=" in s and not s.startswith("#"):
            res.append(s)
    return res


def run(exe, rundir, inp, args=(), threads=1):
    os.makedirs(rundir, exist_ok=True)
    inp = os.path.abspath(inp)
    env = dict(os.environ, OMP_NUM_THREADS=str(threads))
    with open(os.path.join(rundir, "log.txt"), "w") as fo:
        p = subprocess.run([exe, "-i", inp] + list(args), cwd=rundir, stdout=fo,
                           stderr=subprocess.STDOUT, env=env)
    return p.returncode


def read_rmodes(fname):
    """(head dict, n (M,3) int, n2 (M,), R (M,) complex, dR (M,) complex)."""
    head = {}
    with open(fname) as f:
        first = f.readline().split()
    head["time"] = float(first[2])
    head["level"] = int(first[4])
    head["background"] = int(first[6])
    d = np.loadtxt(fname, comments="#")
    n = d[:, :3].astype(int)
    return head, n, d[:, 3].astype(int), d[:, 4] + 1j*d[:, 5], d[:, 6] + 1j*d[:, 7]


def dump_json(obj, fname):
    import json

    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(fname, "w") as fp:
        json.dump(obj, fp, indent=1, default=conv)
