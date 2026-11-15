#!/usr/bin/env python3
"""Processor smoke test of the decks before any card time is spent: the release processor
executable (core-v0.3) runs each named deck for a few cycles; checked are the start-up
(particles read, rest mass), the collision history and the first step's expected number of
collisions against predictions.json (run C-20261115-170404-af74c6d).

    python3 smoke.py [--out DIR] [--nlim 4] [--threads 4] [--exe EXE] RUN [RUN ...]

RUN is a deck name of inputs/ (e.g. cc1_kn1).
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
PRED = os.path.join(C.SCRATCH, "C-20261115-170404-af74c6d", "predictions.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--nlim", type=int, default=4)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--exe", default=EXE)
    a = ap.parse_args()
    pred = json.load(open(PRED))
    summary = dict(exe=a.exe, nlim=a.nlim, runs={})
    ok = True
    for name in a.runs:
        deck = os.path.join(C.HERE, "inputs", name + ".athinput")
        rd = os.path.join(a.out, name)
        os.makedirs(rd, exist_ok=True)
        env = dict(os.environ, OMP_NUM_THREADS=str(a.threads), OMP_PROC_BIND="spread",
                   OMP_PLACES="threads")
        t0 = time.time()
        with open(os.path.join(rd, "athena.log"), "w") as log:
            rc = subprocess.run([a.exe, "-i", deck, "-d", rd, f"time/nlim={a.nlim}",
                                 "particles/snap_dt=-1", "output2/dt=1e9"],
                                cwd=rd, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        wall = time.time() - t0
        r = dict(exit=rc, wall_s=round(wall, 1))
        h = C.read_hst(os.path.join(rd, "cc.nrpic.hst"))
        r["np"] = h["np"].tolist()
        r["sum_m"] = h["sum_m"].tolist()
        r["rest_mass_constant"] = bool(np.all(h["sum_m"] == h["sum_m"][0]))
        r["alpha_probe"] = h["alpha_probe"].tolist()
        good = rc == 0 and r["rest_mass_constant"] and int(h["np"][0]) == 100000
        ch = os.path.join(rd, "cc.coll.hst")
        if name.endswith("kninf"):
            r["coll_hst_present"] = os.path.exists(ch)
            good = good and not r["coll_hst_present"]
        else:
            c = C.read_hst(ch)
            mk = name.split("_")[0]
            p = pred[mk]["runs"][name]
            r.update(cycles=c["ncycle"].tolist(), sum_P=c["sum_P"].tolist(), n_coll=c["n_coll"].tolist(),
                     n_tested=c["n_tested"].tolist(), mean_nsub=c["mean_nsub"].tolist(),
                     max_P=c["max_P"].tolist(), n_trunc=c["n_trunc"].tolist(),
                     n_bad_cells=c["n_bad_cells"].tolist(), mean_N=c["mean_N"].tolist(),
                     n_cells=c["n_cells"].tolist(), n_part=c["n_part"].tolist(),
                     max_dx_mfp=c["max_dx_mfp"].tolist(), dE=c["dE"].tolist(),
                     abs_dE=c["abs_dE"].tolist(), dE_particles=c["dE_particles"].tolist(),
                     sum_MW_particles=c["sum_MW_particles"].tolist())
            k1 = int(np.argmin(c["ncycle"]))
            dev = c["sum_P"][k1] / p["sumP_step1_expected"] - 1.0
            tol = max(3.0 * p["sumP_step1_pairing_sd"] / p["sumP_step1_expected"], 0.005)
            r["sumP_step1"] = float(c["sum_P"][k1])
            r["sumP_step1_predicted"] = p["sumP_step1_expected"]
            r["sumP_step1_rel_dev"] = float(dev)
            r["sumP_step1_tol"] = float(tol)
            r["sumP_step1_ok"] = bool(abs(dev) < tol)
            good = good and r["sumP_step1_ok"] and int(np.max(c["n_trunc"])) == 0 \
                and int(np.max(c["n_bad_cells"])) == 0
        r["ok"] = bool(good)
        ok = ok and good
        summary["runs"][name] = r
        print(name, json.dumps({k: v for k, v in r.items() if not isinstance(v, list)}), flush=True)
    summary["ok"] = bool(ok)
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
