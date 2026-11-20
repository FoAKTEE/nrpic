#!/usr/bin/env python3
"""Byte regression of a release candidate against the previous release on processors.

    regress_v04.py --base ATHENA --new ATHENA --out DIR [--cases geo,...] [--cores N]

The twelve set-ups of wave 1 (tracks/core/stage/G2/EVIDENCE.md): geo, boris, dep, east,
os, jeans, binary (tools/regress_relativistic.py) and c1 to c5
(analysis/rng/run_regression.py), with the arguments of those two drivers.  Every
set-up is run once with each executable in DIR/<case>/{base,new}; every output file
except the log is compared and put into one class:

  identical   the same bytes
  a           restart file (*.rst) that differs only in the 36 bytes of the nine
              never-set members of Mesh::mesh_indcs (cnx1 ... cke) of the mesh header
  b           file with an embedded parameter dump (text up to "<par_end>") that
              differs only in lines "last_time = ..." of that dump
  a+b         both
  other       anything else: a data byte, a text line, a file present in one run only

For jeans and binary the result lines of the log are compared as well.  Verdict PASS:
no file of class "other" and at least one file compared in every case.  summary.json
holds, per case, the files of every class, and for the classes a and b what differs.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/regress/ic"
OS = "os_R5_lattice_N2176_s1"
LOGKEYS = ("defect", "Potential", "Acceleration", "Error", "L1", "norm")
LOGCASES = ("jeans", "binary")


def cases(ic2):
    """name -> (input file, files linked into the run directory, arguments)."""
    prob = os.path.join(REPO, "problems")
    return {
        "geo": (prob + "/kerr/geodesic.athinput", [],
                ["time/tlim=20.0", "particles/hist_dcycle=100"]),
        "boris": (prob + "/kerr/geodesic.athinput", [],
                  ["time/tlim=20.0", "particles/hist_dcycle=100",
                   "particles/pusher=boris", "particles/metric=lattice"]),
        "dep": (prob + "/tests/deposit_smr.athinput", [IC + "/random.nrp"],
                ["time/tlim=2.0", "particles/deposit_max_level=1"]),
        "east": (prob + "/cosmo/east.athinput",
                 [IC + "/east16/particles.nrp", IC + "/east16/fields.bin"],
                 ["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                  "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=20",
                  "particles/snap_dt=0.2", "particles/traj_ntrack=46"]),
        "os": (prob + "/os/os_smr_dev.athinput",
               [IC + "/os/%s.nrp" % OS, IC + "/os/%s.tab" % OS],
               ["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "meshblock/nx1=16",
                "meshblock/nx2=16", "meshblock/nx3=16", "time/nlim=3",
                "particles/particle_file=%s.nrp" % OS, "problem/comp0_file=%s.tab" % OS,
                "particles/snap_dt=0.05", "output2/dt=0.1"]),
        "jeans": (REPO + "/athenak/inputs/tests/jeans_wave.athinput", [],
                  ["time/nlim=20", "gravity/show_defect=2"]),
        "binary": (REPO + "/athenak/inputs/tests/binary_gravity.athinput", [],
                   ["time/nlim=1"]),
        "c1": (prob + "/cluster_test/cluster_analytic.athinput", [],
               ["particles/particle_file=%s/bound.nrp" % ic2, "particles/bh_spin=0.9",
                "time/tlim=10.0"]),
        "c2": (prob + "/tests/mesh_static.athinput", [], ["time/tlim=5.0"]),
        "c3": (prob + "/cluster_test/cluster_mesh.athinput", [],
               ["particles/particle_file=%s/plunge.nrp" % ic2, "time/tlim=0.5"]),
        "c4": (prob + "/cosmo/flrw.athinput", [],
               ["particles/particle_file=%s/particles.nrp" % ic2, "time/tlim=0.5"]),
        "c5": (prob + "/tests/rng_kick_mesh.athinput", [],
               ["particles/particle_file=%s/plunge.nrp" % ic2,
                "particles/test_kick=false", "time/tlim=40.0", "particles/snap_dt=20.0",
                "output1/dt=20.0"]),
    }


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def make_ic(ic2):
    """Particle files of c1 to c5, as in analysis/rng/run_regression.py."""
    os.makedirs(ic2, exist_ok=True)
    py = sys.executable
    mk = os.path.join(REPO, "problems", "cluster_test", "make_cluster.py")
    subprocess.run([py, mk, "--N", "2000", "--a", "0.9", "--bound_only", "--out",
                    os.path.join(ic2, "bound.nrp")], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([py, mk, "--N", "2000", "--a", "0.0", "--fL", "0.3", "--out",
                    os.path.join(ic2, "plunge.nrp")], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([py, os.path.join(REPO, "cosmo", "ic", "make_lattice.py"), "--n", "32",
                    "--ppc", "1", "--noise-x", "0.01", "--noise-u", "0.001", "--out",
                    ic2], check=True, stdout=subprocess.DEVNULL,
                   cwd=os.path.join(REPO, "cosmo", "ic"))


def run(exe, rundir, spec):
    inp, links, args = spec
    os.makedirs(rundir, exist_ok=True)
    for f in links:
        dst = os.path.join(rundir, os.path.basename(f))
        if not os.path.lexists(dst):
            os.symlink(f, dst)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        proc = subprocess.run([exe, "-i", inp] + args + ["-d", rundir], cwd=rundir,
                              stdout=log, stderr=subprocess.STDOUT, env=env)
    return proc.returncode, round(time.time() - t0, 2)


def out_files(top):
    out = []
    for root, _, names in os.walk(top):
        for nm in names:
            p = os.path.join(root, nm)
            if nm == "athena.log" or os.path.islink(p):
                continue
            out.append(os.path.relpath(p, top))
    return sorted(out)


def split_dump(data):
    """(text of the embedded parameter dump, rest) or (None, data)."""
    i = data.find(b"<par_end>\n")
    if i < 0:
        return None, data
    j = i + len(b"<par_end>\n")
    return data[:j], data[j:]


def classify(name, da, db):
    """class of a pair of files and a dict with what differs."""
    if da == db:
        return "identical", {}
    ta, ra = split_dump(da)
    tb, rb = split_dump(db)
    info, cls = {}, []
    if (ta is None) != (tb is None):
        return "other", {"why": "parameter dump in one file only"}
    if ta is not None and ta != tb:
        la, lb = ta.split(b"\n"), tb.split(b"\n")
        if len(la) != len(lb):
            return "other", {"why": "parameter dumps of %d and %d lines"
                             % (len(la), len(lb))}
        block, lines = "", []
        for x, y in zip(la, lb):
            if x.startswith(b"<") and x == y:
                block = x.decode()
            if x != y:
                if not (x.strip().startswith(b"last_time") and
                        y.strip().startswith(b"last_time")):
                    return "other", {"why": "parameter line differs",
                                     "base": x.decode(errors="replace"),
                                     "new": y.decode(errors="replace")}
                lines.append([block, x.decode().split("=")[1].split("#")[0].strip(),
                              y.decode().split("=")[1].split("#")[0].strip()])
        info["last_time"] = lines
        cls.append("b")
    if ra != rb:
        if not name.endswith(".rst") or ta is None or len(ra) != len(rb):
            return "other", {"why": "data bytes differ (%d and %d bytes after the dump)"
                             % (len(ra), len(rb))}
        s = 2*4 + 9*8 + 10*4          # nmb_total, root_level, RegionSize, 10 ints
        if ra[:s] + ra[s+36:] != rb[:s] + rb[s+36:]:
            n = sum(1 for x, y in zip(ra, rb) if x != y)
            return "other", {"why": "%d data bytes differ outside the 36 unset bytes" % n}
        info["unset_bytes_base_nonzero"] = sum(1 for x in ra[s:s+36] if x != 0)
        info["unset_bytes_new_nonzero"] = sum(1 for x in rb[s:s+36] if x != 0)
        cls.insert(0, "a")
    return "+".join(cls), info


def log_results(path):
    with open(path) as f:
        return [ln for ln in f if any(k in ln for k in LOGKEYS) and "time" not in ln]


def compare(case, a, b):
    fa, fb = out_files(a), out_files(b)
    res = {"identical": [], "a": [], "b": [], "a+b": [], "other": [], "details": {}}
    for f in sorted(set(fa) | set(fb)):
        if f not in fa or f not in fb:
            res["other"].append(f)
            res["details"][f] = {"why": "missing in one run"}
            continue
        with open(os.path.join(a, f), "rb") as fh:
            da = fh.read()
        with open(os.path.join(b, f), "rb") as fh:
            db = fh.read()
        c, info = classify(f, da, db)
        res[c].append(f)
        if info:
            res["details"][f] = info
    if case in LOGCASES:
        la = log_results(os.path.join(a, "athena.log"))
        lb = log_results(os.path.join(b, "athena.log"))
        key = "athena.log (%d result lines)" % len(la)
        res["identical" if (la == lb and la) else "other"].append(key)
    res["files"] = len(set(fa) | set(fb))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default="geo,boris,dep,east,os,jeans,binary,c1,c2,c3,c4,c5")
    ap.add_argument("--cores", type=int, default=1)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    exe = {"base": os.path.abspath(a.base), "new": os.path.abspath(a.new)}
    ic2 = os.path.join(out, "ic")
    names = a.cases.split(",")
    if any(n.startswith("c") for n in names):
        make_ic(ic2)
    spec = cases(ic2)
    jobs = [(n, lab) for n in names for lab in ("base", "new")]
    walls, codes = {}, {}
    with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
        futs = {pool.submit(run, exe[lab], os.path.join(out, n, lab), spec[n]): (n, lab)
                for n, lab in jobs}
        for fut in cf.as_completed(futs):
            n, lab = futs[fut]
            codes[(n, lab)], walls[(n, lab)] = fut.result()
            print("ran %-6s %-4s exit %d  %.1f s" % (n, lab, codes[(n, lab)],
                                                     walls[(n, lab)]), flush=True)
    summary = {"base": exe["base"], "new": exe["new"],
               "sha256": {k: sha256(v) for k, v in exe.items()}, "cases": {}}
    ok = True
    for n in names:
        res = compare(n, os.path.join(out, n, "base"), os.path.join(out, n, "new"))
        res["exit"] = [codes[(n, "base")], codes[(n, "new")]]
        res["wall_time_s"] = [walls[(n, "base")], walls[(n, "new")]]
        res["input"] = os.path.relpath(spec[n][0], REPO)
        res["args"] = spec[n][2]
        good = (not res["other"]) and res["files"] > 0 and res["exit"] == [0, 0]
        res["verdict"] = "pass" if good else "FAIL"
        ok = ok and good
        summary["cases"][n] = res
        print("%-6s files %3d  identical %3d  a %d  b %d  a+b %d  other %d  %s"
              % (n, res["files"], len(res["identical"]), len(res["a"]), len(res["b"]),
                 len(res["a+b"]), len(res["other"]), res["verdict"]), flush=True)
        for f in res["other"]:
            print("       other: %s %s" % (f, res["details"].get(f, "")), flush=True)
    summary["verdict"] = "PASS" if ok else "FAIL"
    with open(os.path.join(out, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
        fp.write("\n")
    print("REGRESSION", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
