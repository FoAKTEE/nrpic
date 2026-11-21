#!/usr/bin/env python3
"""V6: is a restart exact? Fresh processor runs on the release executable core-v0.6.

Two set-ups of core's byte regression (tracks/core/analysis/release/regress_v04.py):
  east : periodic cosmology with Z4c and particles, 16^3, nrpic_cosmo (periodic faces)
  os   : Oppenheimer-Snyder with Z4c on a static refined mesh, outflow faces
For each: run A straight to cycle 2n with restart files every n cycles; run B restarts
from A's file of cycle n and runs to 2n. Compared: every file present in both output
directories after the restart (restart file of cycle 2n byte for byte; history files
row by row at equal times, largest relative difference per column).

usage: v6_restart.py EXE OUTDIR
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/regress/ic"
OSN = "os_R5_lattice_N2176_s1"
CASES = {
    "east": dict(inp=REPO + "/problems/cosmo/east.athinput",
                 links=[IC + "/east16/particles.nrp", IC + "/east16/fields.bin"],
                 args=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                       "meshblock/nx2=8", "meshblock/nx3=8", "particles/hist_dcycle=1"],
                 n=10),
    "os": dict(inp=REPO + "/problems/os/os_smr_dev.athinput",
               links=[IC + "/os/%s.nrp" % OSN, IC + "/os/%s.tab" % OSN],
               args=["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=16",
                     "meshblock/nx2=16", "meshblock/nx3=16", "particles/particle_file=%s.nrp" % OSN,
                     "problem/comp0_file=%s.tab" % OSN, "particles/hist_dcycle=1", "output2/dt=-1"],
               n=3),
}


def run(cmd, cwd):
    t0 = time.time()
    with open(os.path.join(cwd, "stdout.txt"), "w") as fh:
        rc = subprocess.call(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT,
                             env=dict(os.environ, OMP_NUM_THREADS="1"))
    return rc, time.time() - t0


def rst_cycle(path):
    with open(path, "rb") as fh:
        head = fh.read(4096).decode("latin1")
    m = re.search(r"cycle\s*=\s*(\d+)", head)
    return int(m.group(1)) if m else None


def read_hist(path):
    rows, names = [], None
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                if "[1]=" in line:
                    names = [m.group(1) for m in re.finditer(r"\[\d+\]=(\S+)", line)]
                continue
            s = line.split()
            if s:
                try:
                    rows.append([float(x) for x in s])
                except ValueError:
                    pass
    return names, np.array(rows) if rows else np.zeros((0, 0))


def compare_hist(pa, pb, t_restart):
    na, a = read_hist(pa)
    nb, b = read_hist(pb)
    if a.size == 0 or b.size == 0:
        return {"rows_compared": 0}
    tb = b[:, 0]
    sel_b = tb > t_restart + 1e-12
    out = {"rows_compared": 0, "max_rel_diff": 0.0, "max_abs_diff": 0.0, "worst_column": None,
           "identical_text_rows": None}
    worst = 0.0
    for row in b[sel_b]:
        i = np.where(np.abs(a[:, 0] - row[0]) <= 1e-12 * max(1.0, abs(row[0])))[0]
        if len(i) == 0:
            continue
        ra = a[i[-1]]
        n = min(len(ra), len(row))
        d = np.abs(ra[:n] - row[:n])
        scale = np.maximum(np.abs(ra[:n]), 1e-300)
        rel = np.where(d > 0, d / scale, 0.0)
        out["rows_compared"] += 1
        if d.max() > out["max_abs_diff"]:
            out["max_abs_diff"] = float(d.max())
        if rel.max() > worst:
            worst = float(rel.max())
            out["worst_column"] = (na or [None] * n)[int(np.argmax(rel))] if na else int(np.argmax(rel))
    out["max_rel_diff"] = worst
    return out


def compare_bytes(pa, pb):
    a = open(pa, "rb").read()
    b = open(pb, "rb").read()
    if a == b:
        return {"identical": True, "size": len(a)}
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), n)
    ndiff = sum(1 for i in range(n) if a[i] != b[i]) if n < 5e7 else None
    return {"identical": False, "size_a": len(a), "size_b": len(b), "first_diff_byte": first,
            "n_diff_bytes": ndiff}


def main():
    exe, out = sys.argv[1:3]
    os.makedirs(out, exist_ok=True)
    res = {"exe": exe}
    for name, c in CASES.items():
        n = c["n"]
        A, B = os.path.join(out, name, "A"), os.path.join(out, name, "B")
        for d in (A, B):
            os.makedirs(d, exist_ok=True)
            for f in c["links"]:
                dst = os.path.join(d, os.path.basename(f))
                if not os.path.exists(dst):
                    os.symlink(f, dst)
        # the command line cannot create a block: copy the input and append a restart output
        inp = os.path.join(out, name, os.path.basename(c["inp"]))
        with open(c["inp"]) as fh:
            text = fh.read()
        with open(inp, "w") as fh:
            fh.write(text + f"\n<output9>\nfile_type = rst\ndcycle    = {n}\n")
        extra = [f"time/nlim={2 * n}"]
        rcA, wA = run([exe, "-i", inp, "-d", A] + c["args"] + extra, A)
        rsts = sorted(glob.glob(os.path.join(A, "rst", "*.rst")))
        cyc = {p: rst_cycle(p) for p in rsts}
        mid = [p for p, cy in cyc.items() if cy == n]
        end = [p for p, cy in cyc.items() if cy == 2 * n]
        entry = {"rcA": rcA, "wallA_s": wA, "rst_cycles_A": {os.path.basename(p): cy for p, cy in cyc.items()}}
        if not mid:
            entry["error"] = "no restart file of cycle n"
            res[name] = entry
            continue
        rcB, wB = run([exe, "-r", mid[0], "-d", B] + c["args"] + extra, B)
        entry.update({"rcB": rcB, "wallB_s": wB, "restart_from": os.path.basename(mid[0])})
        # restart time
        names, h = read_hist(sorted(glob.glob(os.path.join(A, "*.nrpic.hst")))[0])
        t_by_cycle = {int(r[1]): r[0] for r in h} if h.size else {}
        t_restart = t_by_cycle.get(n, None)
        entry["t_restart"] = t_restart
        comp = {}
        for pb in sorted(glob.glob(os.path.join(B, "**", "*"), recursive=True)):
            if os.path.isdir(pb) or os.path.islink(pb) or pb.endswith("stdout.txt"):
                continue
            rel = os.path.relpath(pb, B)
            pa = os.path.join(A, rel)
            if not os.path.exists(pa):
                comp[rel] = "only in B"
                continue
            if rel.endswith(".hst") or rel.endswith(".txt"):
                comp[rel] = compare_hist(pa, pb, t_restart if t_restart is not None else -1)
            else:
                comp[rel] = compare_bytes(pa, pb)
        entry["compare"] = comp
        if end:
            entry["final_rst_identical"] = compare_bytes(end[0], os.path.join(B, "rst", os.path.basename(end[0])))
        res[name] = entry
        print(name, json.dumps(entry, indent=1)[:4000])
    with open(os.path.join(out, "v6_restart.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.2))
    labels, vals, cols = [], [], []
    for i, (name, e) in enumerate((k, v) for k, v in res.items() if isinstance(v, dict) and "compare" in v):
        for rel, cmpres in e["compare"].items():
            if isinstance(cmpres, dict) and "max_rel_diff" in cmpres:
                v = cmpres["max_rel_diff"]
            elif isinstance(cmpres, dict) and "identical" in cmpres:
                v = 0.0 if cmpres["identical"] else 1.0
            else:
                continue
            labels.append(f"{name}: {rel}")
            vals.append(max(v, 1e-18))
            cols.append(fs.SERIES[i])
    y = np.arange(len(labels))
    ax.barh(y, vals, color=cols)
    ax.set_xscale("log")
    ax.set_xlim(1e-18, 10)
    ax.axvline(1e-18 * 1.5, **fs.MASK_LINE)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel("restarted vs straight: largest relative difference (1e-18 = identical; 1 = binary file differs)")
    ax.set_title("V6: restart on release core-v0.6, processors", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_v6_restart"))


if __name__ == "__main__":
    main()
