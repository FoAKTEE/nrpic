#!/usr/bin/env python3
"""Run configuration driver for the single-test-particle geodesic campaign.

Every run of the campaign is defined here (name, input file, command-line overrides).  Each
GPU run goes through Slurm with the project helper,

    ATHENA_EXE=.work/build_gpu_dev/src/athena TIME=00:20:00 JOB_NAME=geo \\
        scripts/gpu_run.sh runs/geodesic/<name> <athinput> [block/par=value ...]

(blocking, one GPU, one core), and CPU runs (part D) call the serial executable
.work/build_check/src/athena directly.  The exact command is written to
runs/geodesic/<name>/cmd.sh and the run metadata to runs/geodesic/<name>/run.json, which the
analysis scripts read.  A run whose log already reports a normal termination is skipped
unless --force is given.

Usage
  run_campaign.py list  [PATTERN ...]          list runs (glob patterns on the run name)
  run_campaign.py run   [PATTERN ...] [--force] [--dry-run]   one srun allocation per run
  run_campaign.py batch [PATTERN ...] [--force] [--slurm-time 00:58:00] [--budget-min 45]
      all selected unfinished GPU runs, one after the other, inside ONE srun allocation
      (one GPU, one core); scripts/gpu_run.sh then runs athena directly with the same command
      line.  Used for the campaign because the two GPUs are shared and every new allocation
      waits in the queue.  The batch script and its output are in runs/geodesic/batches/.

Run names
  kerr_passage/<pusher>_<metric>_dt<dt>      part C: e = 0.99 Kerr-Schild passage, t = 230 M
  kerr_passage_cpu/<pusher>_<metric>_dt<dt>  part D: same input on the CPU executable
  kerr_bl/<orbit>_<pusher>_dt<dt>            part B: Boyer-Lindquist orbits (ecc, inc)
  kerr_mesh/inc_<pusher>_<mesh|lat|cks>_dx<dx>  part E: inclined orbit, a = 0.9, mesh metric
  schw/<orbit>_<pusher>_<metric>_dt<dt>      part A: Schwarzschild, analytic metric
  schw_mesh/<orbit>_<pusher>_<mesh|lat>_dx<dx>  part A: Schwarzschild, mesh metric
  pushers: mid (implicit midpoint), bsym / bchol (Boris, symmetric / Cholesky triad)
  metrics: ks (analytic spherical KS), cks (analytic Cartesian KS), bl (Boyer-Lindquist),
           lat (Cartesian KS on a virtual lattice), mesh (Cartesian KS on the AthenaK mesh)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

from geo_common import (CPU_EXE, GPU_EXE, GPU_RUN, KERR_DIR, REPO, RUNS, SCHW_DIR, kerr_ref,
                        schw_ref)

PUSHERS = {
    "mid": ["particles/pusher=midpoint"],
    "bsym": ["particles/pusher=boris", "particles/triad=symmetric"],
    "bchol": ["particles/pusher=boris", "particles/triad=cholesky"],
}
METRIC_PAR = {"ks": "kerr_schild_sph", "cks": "kerr_schild", "bl": "boyer_lindquist",
              "lat": "lattice", "mesh": "mesh"}
METRIC_SYSTEM = {"ks": "ks", "cks": "cks", "bl": "bl", "lat": "cks", "mesh": "cks"}
DTS = [0.08, 0.04, 0.02, 0.01, 0.005]

KERR_INPUT = KERR_DIR / "geodesic.athinput"
KERR_MESH_INPUT = KERR_DIR / "geodesic_mesh.athinput"
SCHW_INPUT = SCHW_DIR / "geodesic.athinput"
SCHW_MESH_INPUT = SCHW_DIR / "geodesic_mesh.athinput"

# mesh layouts: (half-widths X, Y, Z) and MeshBlock size per dx
MESH_LAYOUT = {
    "schw_circ": dict(half=(10.0, 10.0, 2.0), mb={0.5: (20, 20, 8), 0.25: (20, 20, 16),
                                                  0.125: (40, 40, 32)}),
    "schw_ecc": dict(half=(12.0, 12.0, 6.0), mb={0.5: (24, 24, 24), 0.25: (24, 24, 24),
                                                 0.125: (48, 48, 48)}),
    "kerr_inc": dict(half=(10.0, 10.0, 5.0), mb={0.5: (20, 20, 20), 0.25: (20, 20, 20),
                                                 0.125: (40, 40, 40)}),
}
DXS = [0.5, 0.25, 0.125]


def r17(v):
    return repr(float(v))


def ic_overrides(x, u):
    out = []
    for k in range(3):
        out.append(f"particles/p0_x{k + 1}={r17(x[k])}")
    for k in range(3):
        out.append(f"particles/p0_u{k + 1}={r17(u[k])}")
    out.append("particles/p0_m=0.0")
    return out


def mesh_overrides(layout, dx):
    lay = MESH_LAYOUT[layout]
    out = []
    for d, h in enumerate(lay["half"]):
        n = int(round(2 * h / dx))
        out += [f"mesh/nx{d + 1}={n}", f"mesh/x{d + 1}min={r17(-h)}", f"mesh/x{d + 1}max={r17(h)}",
                f"meshblock/nx{d + 1}={lay['mb'][dx][d]}"]
    return out


def common(dt, tlim):
    return [f"particles/dt={r17(dt)}", f"time/tlim={r17(tlim)}", "particles/tolerance=2.0e-14",
            "particles/max_iterations=200", "particles/hist_dcycle=1", "particles/traj_dcycle=1",
            "particles/traj_ntrack=1", "time/ndiag=20000"]


def build_runs():
    runs = []
    kr = kerr_ref()["orbits"]

    def add(name, part, inp, ov, meta, exe="gpu", time_limit="00:20:00"):
        runs.append(dict(name=name, part=part, input=str(Path(inp).relative_to(REPO)),
                         overrides=ov, meta=meta, exe=exe, time_limit=time_limit))

    # ---------------- part C: KS passage (and part D on the CPU)
    ps = kr["ks_passage"]
    for metric in ("ks", "cks", "lat"):
        sysn = METRIC_SYSTEM[metric]
        st = ps["initial_state"][sysn]
        for pusher in ("mid", "bsym", "bchol"):
            # the Cartesian analytic runs and the extra small steps separate the time-step
            # error in Cartesian coordinates from the Hermite interpolation error
            if metric == "ks":
                dts = DTS
            elif metric == "lat":
                dts = [0.02, 0.01, 0.005, 0.0025, 0.00125]
            else:
                dts = DTS + [0.0025, 0.00125]
            for dt in dts:
                ov = PUSHERS[pusher] + [f"particles/metric={METRIC_PAR[metric]}",
                                        "particles/bh_spin=0.9", "particles/lattice_dx=0.025"]
                ov += common(dt, 230.0) + ic_overrides(st["x"], st["u"])
                meta = dict(orbit="ks_passage", a=0.9, pusher=pusher, metric=metric, system=sysn,
                            dt=dt, t_end=230.0, lattice_dx=0.025 if metric == "lat" else None,
                            t0_offset=0.0)
                add(f"kerr_passage/{pusher}_{metric}_dt{dt:g}", "C", KERR_INPUT, ov, meta)
                if dt == 0.01 and ((pusher == "mid" and metric == "ks") or
                                   (pusher == "bchol" and metric == "lat")):
                    add(f"kerr_passage_cpu/{pusher}_{metric}_dt{dt:g}", "D", KERR_INPUT, ov,
                        dict(meta, cpu=True), exe="cpu")

    # ---------------- part B: Boyer-Lindquist orbits
    for orbit, key in (("ecc", "bl_equatorial_eccentric"), ("inc", "bl_inclined")):
        o = kr[key]
        st = o["initial_state"]["bl"]
        for pusher in ("mid", "bsym", "bchol"):
            dts = [0.02, 0.01] if pusher != "bchol" else [0.01]
            for dt in dts:
                ov = PUSHERS[pusher] + ["particles/metric=boyer_lindquist", "particles/bh_spin=0.9"]
                ov += common(dt, o["t_end"]) + ic_overrides(st["x"], st["u"])
                meta = dict(orbit=key, a=0.9, pusher=pusher, metric="bl", system="bl", dt=dt,
                            t_end=o["t_end"], t0_offset=0.0)
                add(f"kerr_bl/{orbit}_{pusher}_dt{dt:g}", "B", KERR_INPUT, ov, meta,
                    time_limit="00:40:00")

    # ---------------- part E: Kerr a = 0.9 on the mesh (inclined orbit, Cartesian KS)
    o = kr["bl_inclined"]
    st = o["initial_state"]["cks"]
    t_end_mesh, dt_mesh = 600.0, 0.01
    for pusher in ("mid", "bsym"):
        for metric in ("mesh", "lat"):
            for dx in DXS:
                ov = PUSHERS[pusher] + ["particles/bh_spin=0.9"]
                if metric == "mesh":
                    inp = KERR_MESH_INPUT
                    ov += ["particles/metric=mesh"] + mesh_overrides("kerr_inc", dx)
                else:
                    inp = KERR_INPUT
                    ov += ["particles/metric=lattice", f"particles/lattice_dx={r17(dx)}"]
                ov += common(dt_mesh, t_end_mesh) + ic_overrides(st["x"], st["u"])
                meta = dict(orbit="bl_inclined", a=0.9, pusher=pusher, metric=metric, system="cks",
                            dt=dt_mesh, dx=dx, t_end=t_end_mesh, t0_offset=st["t0"])
                add(f"kerr_mesh/inc_{pusher}_{metric}_dx{dx:g}", "E", inp, ov, meta)
        ov = PUSHERS[pusher] + ["particles/bh_spin=0.9", "particles/metric=kerr_schild"]
        ov += common(dt_mesh, t_end_mesh) + ic_overrides(st["x"], st["u"])
        meta = dict(orbit="bl_inclined", a=0.9, pusher=pusher, metric="cks", system="cks",
                    dt=dt_mesh, dx=None, t_end=t_end_mesh, t0_offset=st["t0"])
        add(f"kerr_mesh/inc_{pusher}_cks", "E", KERR_INPUT, ov, meta)

    # ---------------- part A: Schwarzschild
    try:
        sr = schw_ref()["orbits"]
    except FileNotFoundError:
        sr = {}
    for orbit, o in sr.items():
        for metric in ("ks", "cks"):
            st = o["initial_state"][metric]
            for pusher in (("mid", "bsym") if metric == "ks" else ("mid", "bsym", "bchol")):
                for dt in DTS:
                    ov = PUSHERS[pusher] + [f"particles/metric={METRIC_PAR[metric]}",
                                            "particles/bh_spin=0.0"]
                    ov += common(dt, o["t_end"]) + ic_overrides(st["x"], st["u"])
                    meta = dict(orbit=orbit, a=0.0, pusher=pusher, metric=metric, system=metric,
                                dt=dt, t_end=o["t_end"], t0_offset=0.0)
                    add(f"schw/{orbit}_{pusher}_{metric}_dt{dt:g}", "A", SCHW_INPUT, ov, meta)
        if orbit in ("circ", "ecc"):
            st = o["initial_state"]["cks"]
            for pusher in ("mid", "bsym"):
                for metric in ("mesh", "lat"):
                    for dx in DXS:
                        ov = PUSHERS[pusher] + ["particles/bh_spin=0.0"]
                        if metric == "mesh":
                            inp = SCHW_MESH_INPUT
                            ov += ["particles/metric=mesh"] + mesh_overrides(f"schw_{orbit}", dx)
                        else:
                            inp = SCHW_INPUT
                            ov += ["particles/metric=lattice", f"particles/lattice_dx={r17(dx)}"]
                        ov += common(0.01, o["t_end"]) + ic_overrides(st["x"], st["u"])
                        meta = dict(orbit=orbit, a=0.0, pusher=pusher, metric=metric,
                                    system="cks", dt=0.01, dx=dx, t_end=o["t_end"], t0_offset=0.0)
                        add(f"schw_mesh/{orbit}_{pusher}_{metric}_dx{dx:g}", "A", inp, ov, meta)
    return runs


def is_done(rundir):
    logs = [p for p in sorted(Path(rundir).glob("athena.*.log")) if not p.is_symlink()]
    if not logs:
        return False
    txt = logs[-1].read_text(errors="replace")
    return "Terminating on time limit" in txt and "# exit=0" in txt


def command(run):
    rundir = RUNS / run["name"]
    inp = REPO / run["input"]
    if run["exe"] == "gpu":
        env = dict(ATHENA_EXE=str(GPU_EXE), TIME=run["time_limit"], JOB_NAME="geo")
        cmd = [str(GPU_RUN), str(rundir), str(inp)] + run["overrides"]
    else:
        env = {}
        cmd = [str(CPU_EXE), "-i", str(inp), "-d", str(rundir)] + run["overrides"]
    return env, cmd, rundir


def do_run(run, dry=False):
    env, cmd, rundir = command(run)
    if dry:
        envs = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
        print((envs + " " if envs else "") + " ".join(shlex.quote(c) for c in cmd))
        return 0
    prepare(run)
    t0 = time.time()
    if run["exe"] == "gpu":
        p = subprocess.run(cmd, env={**os.environ, **env}, cwd=REPO, capture_output=True, text=True)
        out = p.stdout + p.stderr
    else:
        # serial CPU executable on the login node; mimic the GPU log layout
        ts = time.strftime("%Y%m%d-%H%M%S")
        log = rundir / f"athena.{ts}.log"
        with open(log, "w") as fh:
            fh.write(f"# host={os.uname().nodename} cpu run\n# cmd: {' '.join(cmd)}\n")
            fh.flush()
            p = subprocess.run(cmd, cwd=rundir, stdout=fh, stderr=subprocess.STDOUT,
                               env={**os.environ, "OMP_NUM_THREADS": "1"})
            fh.write(f"# exit={p.returncode} end={time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        link = rundir / "athena.log"
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(log.name)
        out = ""
    dt = time.time() - t0
    status = "ok" if (p.returncode == 0 and is_done(rundir)) else f"FAILED rc={p.returncode}"
    print(f"[{time.strftime('%H:%M:%S')}] {run['name']}: {status} ({dt:.1f} s)", flush=True)
    if status != "ok":
        print(out[-2000:], flush=True)
    return p.returncode


def prepare(run):
    """Write cmd.sh and run.json; return the shell command line of the run."""
    env, cmd, rundir = command(run)
    envs = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
    line = (envs + " " if envs else "") + " ".join(shlex.quote(c) for c in cmd)
    rundir.mkdir(parents=True, exist_ok=True)
    (rundir / "cmd.sh").write_text("#!/usr/bin/env bash\n# run " + run["name"] + "\ncd " +
                                   shlex.quote(str(REPO)) + "\n" + line + "\n")
    with open(rundir / "run.json", "w") as fh:
        json.dump(run, fh, indent=1)
    return line


def do_batch(sel, slurm_time, budget_min):
    """Run the selected GPU runs one after the other inside a single Slurm allocation
    (srun, one GPU, one core).  Inside the allocation scripts/gpu_run.sh runs athena directly
    (its documented behaviour when a GPU is visible), with the same command line as a
    standalone run.  New runs are not started after budget_min minutes; rerun the command
    to continue (finished runs are skipped)."""
    bdir = RUNS / "batches"
    bdir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    script = bdir / f"batch.{ts}.sh"
    lines = ["#!/usr/bin/env bash", f"cd {shlex.quote(str(REPO))}", "start=$(date +%s)",
             f"budget={int(budget_min * 60)}", "echo \"# batch on $(hostname) job=$SLURM_JOB_ID\""]
    for r in sel:
        line = prepare(r)
        lines += ["if (( $(date +%s) - start > budget )); then echo 'budget exhausted'; exit 0; fi",
                  "t0=$(date +%s)",
                  line + " > /dev/null 2>&1; rc=$?",
                  f"echo \"[$(date +%H:%M:%S)] {r['name']} rc=$rc "
                  f"exe_md5=$(md5sum < {shlex.quote(str(GPU_EXE))} | cut -c1-8) "
                  f"$(( $(date +%s) - t0 )) s\""]
    script.write_text("\n".join(lines) + "\n")
    script.chmod(0o755)
    out = bdir / f"batch.{ts}.out"
    cmd = ["srun", "-p", "preempt", "--gres=gpu:1", "-c", "1", "-t", slurm_time, "-J", "geo",
           "-o", str(out), str(script)]
    print(f"[{time.strftime('%H:%M:%S')}] batch of {len(sel)} runs: {script.name}", flush=True)
    p = subprocess.run(cmd, cwd=REPO)
    print(out.read_text() if out.exists() else "(no output)", flush=True)
    return p.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["list", "run", "batch"])
    ap.add_argument("patterns", nargs="*", default=["*"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--slurm-time", default="00:58:00", help="batch: Slurm time limit")
    ap.add_argument("--budget-min", type=float, default=45.0,
                    help="batch: start no new run after this many minutes")
    args = ap.parse_args()
    runs = build_runs()
    sel = [r for r in runs if any(fnmatch.fnmatch(r["name"], p) for p in args.patterns)]
    if args.action == "list":
        for r in sel:
            done = is_done(RUNS / r["name"])
            print(f"{r['part']} {r['exe']} {'done' if done else 'todo'} {r['name']}")
        print(f"{len(sel)} runs")
        return 0
    if args.action == "batch":
        todo = [r for r in sel if r["exe"] == "gpu" and (args.force or not is_done(RUNS / r["name"]))]
        if not todo:
            print("nothing to do")
            return 0
        return do_batch(todo, args.slurm_time, args.budget_min)
    nfail = 0
    for r in sel:
        if not args.force and not args.dry_run and is_done(RUNS / r["name"]):
            continue
        nfail += do_run(r, args.dry_run) != 0
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
