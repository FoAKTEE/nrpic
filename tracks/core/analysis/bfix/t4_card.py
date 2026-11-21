#!/usr/bin/env python3
"""T4: the new options on a card (predictions P5 of tracks/core/JOURNAL-bfix.md). Run
inside a Slurm job that sees a card (tracks/core/analysis/bfix/gpu_job.sh).

Stages:
  evol     oblique linear wave k = (1,1,1), one period, N = 16, 32, 64, 128 with the new
           card executable (stage evol of t1_linear_wave.py)
  regress  three set-ups without particle deposit (test particle with the midpoint and
           the Boris pusher; Z4c puncture benchmark, 20 steps) with the release card
           executable and the new one: every output file byte by byte
  thin     the six cases of t3_thin_jitter.py on the card, from the initial data of the
           processor run of T3 (--t3-dir), with the analysis of T3
  big      thin box of Track B's size, 256 x 256 x 16, one particle per cell and
           direction, crossed waves (1, 0.3, 0), delta = 0.01, to conformal time 1

    python3 t4_card.py --exe-new EXE --exe-base EXE --t3-dir DIR --ic256 DIR [--out DIR]
"""
import argparse
import filecmp
import glob
import json
import os

import numpy as np

import bfix_common as bc  # noqa: E402
from bfix_common import athena_bin  # noqa: E402
import t1_linear_wave as t1  # noqa: E402
import t3_thin_jitter as t3  # noqa: E402


def stage_regress(res, exe, out):
    cases = {
        "geo": ("problems/kerr/geodesic.athinput",
                ["time/tlim=20.0", "particles/hist_dcycle=100"]),
        "boris": ("problems/kerr/geodesic.athinput",
                  ["time/tlim=20.0", "particles/hist_dcycle=100", "particles/pusher=boris",
                   "particles/metric=lattice"]),
        "z4c_bench": ("problems/tests/z4c_bench.athinput", ["time/nlim=20"]),
    }
    r = {}
    for name, (inp, ov) in cases.items():
        recs = bc.run_many({f"{name}_{tag}": (exe[tag], os.path.join(bc.REPO, inp),
                                              os.path.join(out, "regress", f"{name}_{tag}"), ov)
                            for tag in ("base", "new")}, 1)
        da, db = recs[f"{name}_base"]["rundir"], recs[f"{name}_new"]["rundir"]
        names = sorted(set(os.path.relpath(p, d) for d in (da, db)
                           for p in glob.glob(os.path.join(d, "**", "*"), recursive=True)
                           if os.path.isfile(p)) - {"athena.log"})
        differ = [n for n in names
                  if not (os.path.exists(os.path.join(da, n))
                          and os.path.exists(os.path.join(db, n))
                          and filecmp.cmp(os.path.join(da, n), os.path.join(db, n),
                                          shallow=False))]
        r[name] = {"files": len(names), "differing": differ,
                   "wall_s": [recs[f"{name}_base"]["wall_s"], recs[f"{name}_new"]["wall_s"]]}
        print("regress:", name, r[name])
    res["regress"] = r


def stage_big(res, exe, out, icdir):
    info = json.load(open(os.path.join(icdir, "id.json")))
    n, box = info["n"], info["box"]
    with open(os.path.join(bc.REPO, "problems", "cosmo", "east.athinput")) as f:
        txt = f.read()
    inp = os.path.join(out, "waves_big.athinput")
    with open(inp, "w") as f:
        f.write(txt + t3.EXTRA.replace("dt               = 0.5", "dt               = 1.0")
                .replace("dt          = 0.5", "dt          = 1.0"))
    rd = os.path.join(out, "big")
    os.makedirs(rd, exist_ok=True)
    for fn in ("particles.nrp", "fields.bin"):
        if not os.path.exists(os.path.join(rd, fn)):
            os.symlink(os.path.join(icdir, fn), os.path.join(rd, fn))
    d = t3.DEP
    ov = [f"mesh/nx{a+1}={n[a]}" for a in range(3)] \
        + [f"mesh/x{a+1}max={box[a]!r}" for a in range(3)] \
        + ["meshblock/nx1=128", "meshblock/nx2=128", f"meshblock/nx3={n[2]}",
           "time/tlim=1.0", "z4c/damp_kappa1=0.5", "z4c/damp_kappa1_over_alpha=true",
           "particles/deposit_shape=pcs", f"particles/deposit_comp_c={d['dep_comp_c']!r}",
           f"particles/deposit_comp_c2={d['dep_comp_c2']!r}", "particles/interp=bspline",
           "particles/dt_expansion=0.01", "particles/nfilter=0",
           "particles/filter_compensate=false", "particles/snap_dt=1.0",
           f"particles/traj_ntrack={info['n_fiducial']}", "particles/cons_dcycle=8"] \
        + [f"particles/probe_x{a+1}={info['overdensity_point'][a]!r}" for a in range(3)] \
        + [f"particles/probe1_x{a+1}={info['underdensity_point'][a]!r}" for a in range(3)]
    rec = bc.run_many({"big": (exe, inp, rd, ov)}, 1)["big"]
    with open(os.path.join(rd, "athena.log")) as f:
        log = f.read()

    def last(key):
        v = [ln for ln in log.splitlines() if key in ln]
        return float(v[-1].split("=")[1]) if v else None

    z = [athena_bin.read_bin(p) for p in t3.dumps(rd, "z4c")]
    e = [athena_bin.read_bin(p) for p in t3.dumps(rd, "tmunu")]
    zd = max(t3.zdep(z[-1][v]) for v in t3.SCAL)
    names, h = bc.read_hst(glob.glob(os.path.join(rd, "*.z4c.user.hst"))[0])
    ok = h[:, 10] > 0
    snaps = sorted(glob.glob(os.path.join(rd, "east.part.*.bin")))
    _, ds, _ = t3.read_snapshot(snaps[-1])
    r = {"n": n, "particles": info["N"], "particles_end": int(len(ds)),
         "wall_s": rec["wall_s"], "zone_cycles_per_cpu_second": last("zone-cycles/cpu_second"),
         "particle_updates_per_cpu_second": last("particle-updates/cpu_second"),
         "cpu_s": last("cpu time used"), "cycles": int(z[-1]["cycle"]),
         "t_end": z[-1]["time"], "a_end": float(1.0/np.sqrt(z[-1]["z4c_chi"].mean())),
         "z_dependence_end": zd, "E_min": float(e[-1]["tmunu_E"].min()),
         "E_max": float(e[-1]["tmunu_E"].max()),
         "H_rms": [float(np.sqrt(h[ok, 3][0]/h[ok, 10][0])),
                   float(np.sqrt(h[ok, 3][-1]/h[ok, 10][-1]))],
         "z4c_dump_bytes": os.path.getsize(t3.dumps(rd, "z4c")[-1]),
         "terminated": [ln for ln in log.splitlines() if "Terminating" in ln][-1:]}
    res["big"] = r
    print("big:", r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe-new", required=True)
    ap.add_argument("--exe-base", required=True)
    ap.add_argument("--t3-dir", default="")
    ap.add_argument("--ic256", default="")
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stages", default="evol,regress,thin,big")
    ap.add_argument("--evol-n", default="16,32,64,128")
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    exe = {"new": os.path.abspath(a.exe_new), "base": os.path.abspath(a.exe_base)}
    resfile = os.path.join(out, "results_t4.json")
    res = {"meta": {"exe": exe, "commit": bc.git_rev(), "t3_dir": a.t3_dir,
                    "job": os.environ.get("SLURM_JOB_ID", "")}}
    st = a.stages.split(",")
    if "evol" in st:
        t1.stage_evol(res, B, exe, out, 1, [int(v) for v in a.evol_n.split(",")])
        bc.save_json(res, resfile)
        print("figures:", t1.figures(res, out))
    if "regress" in st:
        stage_regress(res, exe, out)
        bc.save_json(res, resfile)
    if "big" in st and a.ic256:
        stage_big(res, exe["new"], out, a.ic256)
        bc.save_json(res, resfile)
    if "thin" in st and a.t3_dir:
        with open(os.path.join(a.t3_dir, "results_t3.json")) as f:
            r3 = json.load(f)
        res["ic"], res["ic_dirs"] = r3["ic"], r3["ic_dirs"]
        t3.stage_run(res, exe["new"], out, 1)
        bc.save_json(res, resfile)
        t3.stage_ana(res, B, out)
        bc.save_json(res, resfile)
        print("figures:", t3.figures(res, out))


if __name__ == "__main__":
    main()
