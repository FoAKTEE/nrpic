#!/usr/bin/env python3
"""T5: the corrected linear-wave generator on several MeshBlocks and across a restart
(predictions P6a, P6b of tracks/core/JOURNAL-bfix.md).

    python3 t5_blocks_restart.py --exe EXE [--out DIR]
"""
import argparse
import glob
import os
import subprocess

import numpy as np

import bfix_common as bc  # noqa: E402
from bfix_common import athena_bin  # noqa: E402

INP = os.path.join(bc.REPO, "problems", "tests", "lw_oblique.athinput")
CIRC = ["problem/amp_cross=1.0e-6", "problem/phase_cross=1.5707963267948966"]


def last_dump(rd):
    return athena_bin.read_bin(sorted(glob.glob(os.path.join(rd, "bin", "lwo.z4c.0*.bin")))[-1])


def errs(rd):
    with open(os.path.join(rd, "lwo-errs.dat")) as f:
        return f.read().strip().split("\n")[-1]


def compare(a, b):
    nd, mx = 0, 0.0
    for v in a["variables"]:
        nd += int(np.count_nonzero(a[v] != b[v]))
        mx = max(mx, float(np.abs(a[v] - b[v]).max()))
    return nd, mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    exe = os.path.abspath(a.exe)
    inp = os.path.join(out, "lw_rst.athinput")
    with open(INP) as f:
        txt = f.read()
    with open(inp, "w") as f:
        f.write(txt + "\n<output3>\nfile_type   = rst\ndt          = 0.15\n")
    m1 = bc.mesh_overrides(16)
    m8 = m1[:3] + ["meshblock/nx1=8", "meshblock/nx2=8", "meshblock/nx3=8"]
    recs = bc.run_many({
        "one_block": (exe, INP, os.path.join(out, "one_block"), m1),
        "eight_blocks": (exe, INP, os.path.join(out, "eight_blocks"), m8),
        "circ_full": (exe, inp, os.path.join(out, "circ_full"), m8 + CIRC)}, 3)
    res = {"meta": {"exe": exe, "commit": bc.git_rev()}}
    a1, a8 = last_dump(recs["one_block"]["rundir"]), last_dump(recs["eight_blocks"]["rundir"])
    nd, mx = compare(a1, a8)
    res["blocks"] = {"time": [a1["time"], a8["time"]], "cycle": [a1["cycle"], a8["cycle"]],
                     "values_differing": nd, "max_abs_diff": mx,
                     "errs_one": errs(recs["one_block"]["rundir"]),
                     "errs_eight": errs(recs["eight_blocks"]["rundir"])}
    # restart of the circular wave from its second restart file (t about 0.15)
    rst = sorted(glob.glob(os.path.join(recs["circ_full"]["rundir"], "rst", "*.rst")))
    src = rst[1]
    rd = os.path.join(out, "circ_restart")
    os.makedirs(rd, exist_ok=True)
    with open(os.path.join(rd, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-r", src, "-d", rd], cwd=rd, stdout=log,
                           stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise SystemExit("restart failed: " + rd)
    cf, cr = last_dump(recs["circ_full"]["rundir"]), last_dump(rd)
    nd, mx = compare(cf, cr)
    ef, er = errs(recs["circ_full"]["rundir"]), errs(rd)
    res["restart"] = {"source": os.path.basename(src), "n_restart_files": len(rst),
                      "time": [cf["time"], cr["time"]], "cycle": [cf["cycle"], cr["cycle"]],
                      "values_differing": nd, "max_abs_diff": mx, "errs_full": ef,
                      "errs_restart": er,
                      "rms_L1": [float(ef.split()[4]), float(er.split()[4])]}
    bc.save_json(res, os.path.join(out, "results_t5.json"))
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main()
