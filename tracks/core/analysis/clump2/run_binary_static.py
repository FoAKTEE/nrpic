#!/usr/bin/env python3
"""Test TD of tracks/core/JOURNAL-clump2.md: two equilibrium clusters (y_c = 0.819, mass 1
each, at x = -20 and +20, Newtonian circular speed along -y and +y) at t = 0 on a uniform
mesh of cell size 0.5, on processors: the clusters at rest in each other's conformal factor,
then moving without curvature, with the curvature of the two boost tables, and with the
two corrections of psi (problems/tests/clump_table_binary.athinput). Also the single
cluster at rest on the same cells, for the comparison of the Hamiltonian residual.

Writes into $NRPIC_RUN_DIR (or --out): ic/, one directory per case, cases.json.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
INPUT = os.path.join(WT, "problems", "tests", "clump_table_binary.athinput")
MAKE_IC = os.path.join(WT, "problems", "ic", "make_ic.py")
EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))
V = "0.111803"
Q = ["--sampler", "quiet", "--lattice-h", "0.25"]
MESH = ["mesh/nx1=192", "mesh/nx2=96", "mesh/nx3=96", "meshblock/nx1=32",
        "meshblock/nx2=32", "meshblock/nx3=32"]          # cell size 0.5
ICS = {
    "b0": ["--cluster", "0.819,1,-20,0,0,0,0,0", "--cluster", "0.819,1,20,0,0,0,0,0", *Q],
    "bv": ["--cluster", f"0.819,1,-20,0,0,0,-{V},0", "--cluster", f"0.819,1,20,0,0,0,{V},0",
           *Q],
    # one cluster of the pair alone (no partner: lam = 1), at the same place
    "single": ["--cluster", "0.819,1,-20,0,0,0,0,0", *Q],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    icd = os.path.join(a.out, "ic")
    os.makedirs(icd, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1")
    meta = {}
    for name, args in ICS.items():
        subprocess.run([sys.executable, MAKE_IC, "boosted", *args, "--out", icd,
                        "--prefix", name], check=True, env=env, stdout=subprocess.DEVNULL)
        with open(os.path.join(icd, name + ".json")) as f:
            meta[name] = json.load(f)
    P = meta["bv"]["athenak"]["problem"]
    mom = [f"problem/comp{c}_p{k}={P[f'comp{c}_p{k}']!r}" for c in (0, 1) for k in (1, 2, 3)]
    corr = ["problem/comp0_corr=table", "problem/comp1_corr=table"]
    # label -> (particles, tables of clusters 0 and 1, athena arguments)
    cases = {
        "b0": ("b0", ("b0_c0", "b0_c1"), []),
        "bv_none": ("bv", ("bv_c0", "bv_c1"), []),
        "bv_curv": ("bv", ("bv_c0", "bv_c1"), mom),
        "bv_corr": ("bv", ("bv_c0", "bv_c1"), mom + corr),
        # the single cluster: the second component is its own table placed far outside
        # the particles would be wrong, so the input is reduced to one component
        "single": ("single", ("single_c0", "single_c0"), ["problem/ncomp=1"]),
    }
    results = {}
    for label, (ic, tabs, args) in cases.items():
        d = os.path.join(a.out, label)
        os.makedirs(d, exist_ok=True)
        links = {"particles.nrp": ic + ".nrp"}
        for c, t in enumerate(tabs):
            links[f"binary_c{c}.tab"] = t + ".tab"
            links[f"binary_c{c}.bst"] = "bv_c%d.bst" % c
            links[f"binary_c{c}_corr.tab"] = "bv_c%d_corr.tab" % c
        for dst, src in links.items():
            link = os.path.join(d, dst)
            if not os.path.lexists(link):
                os.symlink(os.path.join("..", "ic", src), link)
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", INPUT, "-d", d, *MESH, *args], cwd=d,
                                stdout=log,
                                stderr=subprocess.STDOUT, env=env).returncode
        rows = []
        if st == 0:
            with open(os.path.join(d, "clump.z4c.user.hst")) as f:
                rows = [[float(v) for v in ln.split()] for ln in f if not ln.startswith("#")]
        bind = os.path.join(d, "bin")
        if os.path.isdir(bind):
            for fn in sorted(os.listdir(bind)):
                if fn.endswith(".00001.bin"):
                    os.remove(os.path.join(bind, fn))
        results[label] = dict(ic=ic, args=args, status=st, wall=time.time() - t0,
                              hst0=rows[0] if rows else None)
        print(f"{label:10s} status {st} wall {results[label]['wall']:.1f} s"
              + (f"  H-norm2 {rows[0][3]:.6e} M-norm2 {rows[0][4]:.6e}" if rows else ""))
    with open(os.path.join(a.out, "cases.json"), "w") as f:
        json.dump(dict(exe=EXE, input=INPUT, ic=meta, cases=results), f, indent=1)
    bad = [k for k, v in results.items() if v["status"] != 0]
    print("FAILED: " + ", ".join(bad) if bad else "all cases ran")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
