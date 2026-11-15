#!/usr/bin/env python3
"""Test 4 of JOURNAL.md: AthenaK's nrpic_cf reads the new table and particle file.

    python3 smoke_athenak.py --ic BUILD_RUN_DIR --stem STEM --out DIR [--exe PATH] [--nlim 2]

Writes a small static-mesh deck, runs the processor executable on the new model and on the
paper's monoenergetic y_c = 0.819 model (problems/ic/make_ic.py), and compares the first
history records. Output: DIR/<case>/..., DIR/smoke.json.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

DECK = """<comment>
problem   = C-sidm smoke test: nrpic_cf reads a table and a particle file

<job>
basename  = smoke

<mesh>
nghost    = 4
nx1       = 32
x1min     = -128.0
x1max     = 128.0
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = 32
x2min     = -128.0
x2max     = 128.0
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = 32
x3min     = -128.0
x3max     = 128.0
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = 16
nx2       = 16
nx3       = 16

<mesh_refinement>
refinement       = static
max_nmb_per_rank = 4096

<refined_region1>
level = 4
x1min = -15.9
x1max = 15.9
x2min = -15.9
x2max = 15.9
x3min = -15.9
x3max = 15.9

<time>
evolution  = dynamic
integrator = rk4
cfl_number = 0.25
nlim       = {nlim}
tlim       = 100.0
ndiag      = 1

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_advect    = 1.0
shift_Gamma     = 0.75
shift_eta       = 2.0
shift_advect    = 1.0
diss            = 0.5
chi_div_floor   = 1.0e-5
damp_kappa1     = 0.02
damp_kappa2     = 0.0
damp_ch         = 0.0
damp_ch_dx      = 0.0

<particles>
particle_type  = nrpic
pusher         = midpoint
metric         = mesh
tolerance      = 1.0e-7
max_iterations = 50
deposit        = true
nfilter        = 4
filter_compensate = true
filter_comp_c  = -1.0
deposit_max_level = 31
deposit_adaptive  = false
deposit_min_level = 4
deposit_ppc       = 2.0
deposit_max_coarsen = 31
alpha_exc      = 0.1
hist_dcycle    = 1
snap_dt        = 1000.0
particle_file  = {nrp}

<problem>
pgen_name  = nrpic_cf
ncomp      = 1
comp0_type = table
comp0_file = {tab}
lapse      = table

<output1>
file_type = hst
dt        = 0.01
"""


def read_hst(path):
    rows = []
    cols = None
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                if "[1]=" in line:
                    cols = [c.split("=")[1] for c in line[1:].split() if "=" in c]
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    return cols, rows


def run_case(name, nrp, tab, out, exe, nlim, threads):
    d = os.path.join(out, name)
    os.makedirs(d)
    shutil.copy(nrp, os.path.join(d, os.path.basename(nrp)))
    shutil.copy(tab, os.path.join(d, os.path.basename(tab)))
    deck = os.path.join(d, "smoke.athinput")
    with open(deck, "w") as f:
        f.write(DECK.format(nlim=nlim, nrp=os.path.basename(nrp), tab=os.path.basename(tab)))
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false")
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as lo:
        rc = subprocess.run([exe, "-i", deck], cwd=d, env=env, stdout=lo,
                            stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    res = dict(name=name, exit_code=rc, wall_s=round(wall, 1))
    nh = os.path.join(d, "smoke.nrpic.hst")
    zh = os.path.join(d, "smoke.z4c.user.hst")
    if os.path.exists(nh):
        cols, rows = read_hst(nh)
        res["nrpic_first"] = dict(zip(cols, rows[0]))
        res["nrpic_last"] = dict(zip(cols, rows[-1]))
        res["nrpic_records"] = len(rows)
    if os.path.exists(zh):
        cols, rows = read_hst(zh)
        res["z4c_first"] = dict(zip(cols, rows[0]))
        res["z4c_last"] = dict(zip(cols, rows[-1]))
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ic", required=True)
    p.add_argument("--stem", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--exe", default="/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena")
    p.add_argument("--nlim", type=int, default=2)
    p.add_argument("--threads", type=int, default=4)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = json.load(open(os.path.join(a.ic, a.stem + ".json")))
    # reference: the paper's monoenergetic y_c = 0.819 model through the existing tool
    ref = os.path.join(a.out, "ic_st")
    subprocess.run([sys.executable, os.path.join(WT, "problems", "ic", "make_ic.py"), "st",
                    "--yc", "0.819", "--N", "10000", "--seed", "1", "--out", ref,
                    "--prefix", "st_yc0p819"], check=True)
    refmeta = json.load(open(os.path.join(ref, "st_yc0p819.json")))
    out = dict(stem=a.stem, exe=a.exe, nlim=a.nlim,
               new=run_case("new", os.path.join(a.ic, a.stem + ".nrp"),
                            os.path.join(a.ic, a.stem + ".tab"), a.out, a.exe, a.nlim, a.threads),
               ref=run_case("ref_st0819", os.path.join(ref, "st_yc0p819.nrp"),
                            os.path.join(ref, "st_yc0p819.tab"), a.out, a.exe, a.nlim, a.threads))
    out["expected"] = dict(new_M0=meta["M0"], new_sum_m=meta["particles"]["sum_m"],
                           ref_M0=refmeta["M0"])
    try:
        n, r = out["new"], out["ref"]
        out["checks"] = dict(
            new_np=n["nrpic_first"]["np"], new_sum_m=n["nrpic_first"]["sum_m"],
            new_sum_m_rel=n["nrpic_first"]["sum_m"] / meta["particles"]["sum_m"] - 1,
            new_sum_mW_vs_int_E=n["nrpic_first"]["int_E"] / n["nrpic_first"]["sum_mW"] - 1,
            ref_sum_mW_vs_int_E=r["nrpic_first"]["int_E"] / r["nrpic_first"]["sum_mW"] - 1,
            H_norm2_new=n["z4c_first"]["H-norm2"], H_norm2_ref=r["z4c_first"]["H-norm2"],
            H_norm2_ratio_new_over_ref=n["z4c_first"]["H-norm2"] / r["z4c_first"]["H-norm2"],
            M_norm2_new=n["z4c_first"]["M-norm2"], M_norm2_ref=r["z4c_first"]["M-norm2"],
            cycles_new=n["nrpic_last"]["ncycle"], cycles_ref=r["nrpic_last"]["ncycle"])
    except (KeyError, IndexError) as e:
        out["checks"] = dict(error=repr(e))
    with open(os.path.join(a.out, "smoke.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out["checks"], indent=1))
    return 0 if out["new"]["exit_code"] == 0 and out["ref"]["exit_code"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
