#!/usr/bin/env python3
"""Test T5 of tracks/core/JOURNAL-clump.md: the two-overdensity data of the first paper
(mesh and particles of run jeans/n1e4_v19) at t = 0 with and without the smeared
Bowen-York curvature of the clumps, on processors. One registered run:

    harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 2 --purpose "..." \
        -- python3 tracks/core/analysis/clump/run_jeans_t0.py

Cases (input: problems/jeans/jeans_mc.athinput plus an output block for the constraint
fields, no step):
  none        comp<c>_p1..3 = 0 (no curvature added), particles of the run
  curv        the momenta of the input, particles of the run
  gauss_none  particles regenerated with --clump-momentum-rule gaussian, no curvature
  gauss_curv  the same particles, their momenta
Writes <case>/ and cases_t5.json into $NRPIC_RUN_DIR (or --out).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
V19 = "/data/haiyangw/nrpic/runs/jeans/n1e4_v19"
EXE = os.environ.get("NRPIC_EXE_CPU", os.path.join(WT, ".work", "build_cpu", "src", "athena"))
ZERO = [f"problem/comp{c}_p{k}=0.0" for c in (1, 2) for k in (1, 2, 3)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    top = a.out
    os.makedirs(os.path.join(top, "ic"), exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    with open(os.path.join(WT, "problems", "jeans", "jeans_mc.athinput")) as f:
        txt = f.read()
    inp = os.path.join(top, "jeans_t0.athinput")
    with open(inp, "w") as f:
        f.write(txt + "\n<output3>\nfile_type = bin\nvariable  = con\ndt        = 100.0\n")
    # particles of the rule 'gaussian' (same seed: same positions)
    subprocess.run([sys.executable, os.path.join(WT, "problems", "ic", "make_ic.py"), "jeans",
                    "--N", "10000", "--seed", "1", "--env-yc", "0.907", "--clump-curvature",
                    "--clump-momentum-rule", "gaussian", "--out", os.path.join(top, "ic"),
                    "--prefix", "jeans_gauss"], check=True, env=env,
                   stdout=subprocess.DEVNULL)
    with open(os.path.join(top, "ic", "jeans_gauss.json")) as f:
        pg = json.load(f)["athenak"]["problem"]
    gp = [f"problem/comp{c}_p{k}={pg[f'comp{c}_p{k}']!r}" for c in (1, 2) for k in (1, 2, 3)]
    common = ["time/nlim=0", "mesh_refinement/max_nmb_per_rank=1100"]
    run_nrp = os.path.join(V19, "particles.nrp")
    g_nrp = os.path.join(top, "ic", "jeans_gauss.nrp")
    cases = [("none", run_nrp, ZERO), ("curv", run_nrp, []),
             ("gauss_none", g_nrp, ZERO), ("gauss_curv", g_nrp, gp)]

    def run(case):
        label, nrp, args = case
        d = os.path.join(top, label)
        os.makedirs(d, exist_ok=True)
        shutil.copy(nrp, os.path.join(d, "particles.nrp"))
        shutil.copy(os.path.join(V19, "envelope.tab"), d)
        t0 = time.time()
        with open(os.path.join(d, "athena.log"), "w") as log:
            st = subprocess.run([EXE, "-i", inp, "-d", d, *common, *args], cwd=d,
                                stdout=log, stderr=subprocess.STDOUT, env=env).returncode
        row = None
        if st == 0:
            with open(os.path.join(d, "jeans.z4c.user.hst")) as f:
                row = [float(v) for v in next(l for l in f if not l.startswith("#")).split()]
            dup = os.path.join(d, "bin", "jeans.con.00001.bin")
            if os.path.exists(dup):
                os.remove(dup)
        return label, dict(args=args, status=st, wall=time.time() - t0, hst0=row)

    with ThreadPoolExecutor(a.jobs) as ex:
        results = dict(ex.map(run, cases))
    with open(os.path.join(top, "cases_t5.json"), "w") as f:
        json.dump(dict(exe=EXE, input=inp, momenta_gaussian_rule=gp, cases=results), f,
                  indent=1)
    for k, v in results.items():
        h = v["hst0"]
        print(f"{k:11s} status {v['status']} wall {v['wall']:6.1f} s  "
              + (f"H2 {h[3]:.6e} M2 {h[4]:.6e} Mx2 {h[6]:.6e} My2 {h[7]:.6e} Mz2 {h[8]:.6e}"
                 if h else ""))
    return 1 if any(v["status"] != 0 for v in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
