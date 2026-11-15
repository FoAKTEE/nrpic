#!/usr/bin/env python3
"""Initial data and card-job lists for ladder rows 3 and 4 (wave 2).

Writes into OUT (default $NRPIC_RUN_DIR):
  prolate/             make_ic.py prolate --e 0.9 --b 10 --N 10000 --seed 1
  st_yc<y>/            make_ic.py st --yc <y> --N 10000 --sampler stratified --seed 1
                       --vpert 0.01 --no-consistent-table   (protocol of runs/st/yc0605_v5)
  turning_point.json   first maximum of E_b/M_0 along the monoenergetic sequence and
                       E_b/M_0, R/M, alpha_c of every model generated
  sha256.txt           checksums of every file written
  job_<name>.list      lines "<name> <athinput> <athena args>" for nrpic-run --launcher batch

    python3 make_ics.py [--out DIR] [--yc 0.72 0.70 0.66 0.64] [--jobs "a:0.70,0.66" ...]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

WT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(WT / "python"))
from nrpic import st_cluster as stc  # noqa: E402

MAKE_IC = WT / "problems" / "ic" / "make_ic.py"
INP_ST = WT / "problems" / "st" / "st_cluster_amr.athinput"
INP_PRO = WT / "problems" / "prolate" / "prolate_amr.athinput"

# command-line overrides of the cards runs (everything else is the input file)
ST_ARGS = "mesh_refinement/num_levels=7 time/tlim=300"
PRO_ARGS = ("mesh_refinement/num_levels=6 mesh_refinement/max_nmb_per_rank=2000 "
            "particles/nfilter=4 particles/filter_compensate=true time/tlim=45")


def tag(y):
    return f"yc{y:.3f}".replace(".", "p")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def gen_st(out, y):
    d = out / f"st_{tag(y)}"
    d.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(MAKE_IC), "st", "--yc", f"{y}", "--N", "10000",
           "--sampler", "stratified", "--seed", "1", "--vpert", "0.01",
           "--no-consistent-table", "--out", str(d)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    (d / "make_ic.out").write_text(" ".join(cmd) + "\n" + r.stdout + r.stderr)
    nrp = sorted(d.glob("*.nrp"))[0]
    tab = sorted(d.glob("*.tab"))[0]
    return d, nrp, tab


def gen_prolate(out):
    d = out / "prolate"
    d.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(MAKE_IC), "prolate", "--e", "0.9", "--b", "10", "--N",
           "10000", "--seed", "1", "--out", str(d)]
    r = subprocess.run(cmd, check=True, capture_output=True, text=True)
    (d / "make_ic.out").write_text(" ".join(cmd) + "\n" + r.stdout + r.stderr)
    return d, sorted(d.glob("*.nrp"))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--yc", type=float, nargs="+", default=[0.72, 0.70, 0.66, 0.64])
    ap.add_argument("--jobs", nargs="+", default=["a:0.70,0.66", "b:0.72,0.64", "c:prolate"],
                    help="job lists, name:item,item (item: a y_c value or 'prolate')")
    ap.add_argument("--no-prolate", action="store_true")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    tp = stc.binding_energy_maximum()
    models = {}
    lines = {}
    for y in a.yc:
        d, nrp, tab = gen_st(out, y)
        g = stc.st_global(y)
        models[tag(y)] = dict(yc=y, Eb_over_M0=float(g["Eb_over_M0"]),
                              R_over_M=float(g["R_over_M"]), alpha_c=float(g["alpha_c"]),
                              zc=float(g["zc"]), M0_over_M=float(g["M0_over_M"]),
                              nrp=str(nrp), tab=str(tab))
        lines[f"{y}"] = (f"st_{tag(y)} {INP_ST} {ST_ARGS} particles/particle_file={nrp} "
                         f"problem/comp0_file={tab}")
    if not a.no_prolate:
        d, nrp = gen_prolate(out)
        lines["prolate"] = f"prolate_m8 {INP_PRO} {PRO_ARGS} particles/particle_file={nrp}"
    (out / "turning_point.json").write_text(json.dumps(
        dict(turning_point={k: float(v) for k, v in tp.items()}, models=models), indent=1))
    for j in a.jobs:
        name, items = j.split(":")
        sel = [lines[i] for i in items.split(",") if i in lines]
        if sel:
            (out / f"job_{name}.list").write_text("\n".join(sel) + "\n")
    with open(out / "sha256.txt", "w") as f:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "sha256.txt":
                f.write(f"{sha(p)}  {p.relative_to(out)}\n")
    print(json.dumps(tp, default=float))
    for k, v in models.items():
        print(k, f"alpha_c={v['alpha_c']:.4f} Eb/M0={v['Eb_over_M0']:.6f} R/M={v['R_over_M']:.3f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
