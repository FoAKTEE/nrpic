#!/usr/bin/env python3
"""One registered AthenaK Newtonian-mode run of secondary infall: particle file (nm_ic.py)
and the release processor executable with nm_infall.athinput. Output in --out (default
$NRPIC_RUN_DIR, set by harness/bin/nrpic-run). Nothing here integrates particles; AthenaK
does (decision 0010).

  python3 nm_run.py --kind infall --nx 128 --aend 4 --L 68            # the evolution
  python3 nm_run.py --kind field  --nx 128 --L 68 --onestep           # field calibration
  python3 nm_run.py --kind infall --nx 128 --nlim 20                  # timing probe

Threaded executable (wave 3, scratch/core/exe/core_build-openmp/athena_cpu): --threads N
(default: $OMP_NUM_THREADS, which nrpic-run sets to --cores, else 1) and --bind, which
picks the N least busy physical cores of one NUMA node (two readings of /proc/stat),
restricts the executable to them (sched_setaffinity) and sets OMP_PROC_BIND=true,
OMP_PLACES=cores, so that the places are those cores only and not cores 0 to N-1 of the
machine (the trap of threaded_build.md section 2). The chosen cores go into nm_run.json.
--snap_dt sets the snapshot interval directly; --rst_dt writes restart files.
"""
import argparse
import glob
import hashlib
import re
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EXE_CPU = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
DECK = os.path.join(HERE, "nm_infall.athinput")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _cpu_times():
    out = {}
    with open("/proc/stat") as f:
        for ln in f:
            m = re.match(r"cpu(\d+)\s+(.*)", ln)
            if m:
                v = [int(x) for x in m.group(2).split()]
                out[int(m.group(1))] = (sum(v[:8]), v[3] + (v[4] if len(v) > 4 else 0))
    return out


def pick_cores(n, interval=1.0):
    """The n least busy physical cores on one NUMA node: {core: [logical cpus]}, busy."""
    node_of = {}
    for nd in glob.glob("/sys/devices/system/node/node[0-9]*"):
        k = int(re.search(r"node(\d+)$", nd).group(1))
        for c in glob.glob(os.path.join(nd, "cpu[0-9]*")):
            node_of[int(re.search(r"cpu(\d+)$", c).group(1))] = k
    cores = {}
    allowed = os.sched_getaffinity(0)
    for c in glob.glob("/sys/devices/system/cpu/cpu[0-9]*"):
        cpu = int(re.search(r"cpu(\d+)$", c).group(1))
        if cpu not in allowed:
            continue
        try:
            with open(os.path.join(c, "topology", "core_id")) as f:
                core = int(f.read())
            with open(os.path.join(c, "topology", "physical_package_id")) as f:
                pkg = int(f.read())
        except OSError:
            continue
        cores.setdefault((node_of.get(cpu, pkg), pkg, core), []).append(cpu)
    t0 = _cpu_times()
    time.sleep(interval)
    t1 = _cpu_times()
    busy = {}
    for k, cpus in cores.items():
        b = 0.0
        for c in cpus:
            dt = t1[c][0] - t0[c][0]
            b += 1.0 - (t1[c][1] - t0[c][1]) / dt if dt > 0 else 0.0
        busy[k] = b
    best = None
    for node in sorted({k[0] for k in cores}):
        ks = sorted((k for k in cores if k[0] == node), key=lambda k: busy[k])
        if len(ks) >= n:
            load = sum(busy[k] for k in ks[:n])
            if best is None or load < best[0]:
                best = (load, ks[:n])
    if best is None:
        ks = sorted(cores, key=lambda k: busy[k])[:n]
        best = (sum(busy[k] for k in ks), ks)
    chosen = sorted(best[1])
    return [sorted(cores[k]) for k in chosen], [busy[k] for k in chosen]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--kind", choices=("infall", "field", "fieldfull"), default="infall")
    ap.add_argument("--nx", type=int, default=128)
    ap.add_argument("--mb", type=int, default=0, help="MeshBlock size (default nx/2)")
    ap.add_argument("--aend", type=float, default=4.0)
    ap.add_argument("--L", type=float, default=68.0)
    ap.add_argument("--edge_fac", type=float, default=1.2)
    ap.add_argument("--ndust", type=float, default=5e5)
    ap.add_argument("--nclump", type=float, default=2e4)
    ap.add_argument("--rclump", type=float, default=0.3)
    ap.add_argument("--cfl", type=float, default=0.15)
    ap.add_argument("--dtmax", type=float, default=0.25)
    ap.add_argument("--nsnap", type=int, default=50)
    ap.add_argument("--nlim", type=int, default=-1)
    ap.add_argument("--onestep", action="store_true",
                    help="one step of 1e-6 with a snapshot after it (field measurement)")
    ap.add_argument("--exe", default=EXE_CPU)
    ap.add_argument("--shift_cells", type=float, nargs=3, default=[0.0, 0.0, 0.0],
                    help="displace the configuration by this many cells: 0.5 0.5 0.5 puts the "
                         "clump at a cell centre instead of a mesh vertex")
    ap.add_argument("--tlim", type=float, default=0.0, help="end time (default: a_end)")
    ap.add_argument("--threads", type=int, default=int(os.environ.get("OMP_NUM_THREADS", "1")),
                    help="OpenMP threads of a threaded executable (default $OMP_NUM_THREADS or 1)")
    ap.add_argument("--bind", action="store_true",
                    help="bind the threads to the least busy cores of one NUMA node")
    ap.add_argument("--snap_dt", type=float, default=0.0, help="snapshot interval (default tlim/nsnap)")
    ap.add_argument("--rst_dt", type=float, default=0.0, help="restart interval (default: none)")
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    ic = [sys.executable, os.path.join(HERE, "nm_ic.py"), "--out", a.out, "--kind", a.kind,
          "--aend", str(a.aend), "--L", str(a.L), "--edge_fac", str(a.edge_fac),
          "--ndust", str(a.ndust), "--nclump", str(a.nclump), "--rclump", str(a.rclump)]
    ic += ["--shift"] + [str(c * 2 * a.L / a.nx) for c in a.shift_cells]
    subprocess.run(ic, check=True, stdout=subprocess.DEVNULL)
    with open(os.path.join(a.out, "setup.json")) as f:
        p = json.load(f)
    mb = a.mb if a.mb > 0 else a.nx // 2
    tlim = a.tlim if a.tlim > 0 else p["tlim"]
    over = [f"mesh/nx{i}={a.nx}" for i in (1, 2, 3)]
    over += [f"mesh/x{i}min={-a.L}" for i in (1, 2, 3)] + [f"mesh/x{i}max={a.L}" for i in (1, 2, 3)]
    over += [f"meshblock/nx{i}={mb}" for i in (1, 2, 3)]
    over += [f"particles/particle_file={os.path.join(a.out, 'particles.nrp')}"]
    if a.onestep:
        over += ["time/nlim=1", "time/tlim=1.0", "particles/dt=1e-6", "particles/newton_cfl=0.0",
                 "particles/snap_dt=1e-6", "particles/hist_dcycle=1"]
    else:
        snap_dt = a.snap_dt if a.snap_dt > 0 else tlim / a.nsnap
        over += [f"time/tlim={tlim!r}", f"time/nlim={a.nlim}", f"particles/dt={a.dtmax}",
                 f"particles/newton_cfl={a.cfl}", f"particles/snap_dt={snap_dt!r}"]
        if a.rst_dt > 0:
            over += [f"output1/dt={a.rst_dt!r}"]
    cmd = [a.exe, "-i", DECK, "-d", a.out] + over
    env = dict(os.environ, OMP_NUM_THREADS=str(a.threads))
    cpus, busy = None, None
    if a.bind:
        groups, busy = pick_cores(a.threads)
        cpus = sorted(c for g in groups for c in g)
        env.update(OMP_PROC_BIND="true", OMP_PLACES="cores", OMP_DISPLAY_ENV="true")
    meta = dict(cmd=cmd, exe=a.exe, exe_sha256=sha(a.exe), deck=DECK, deck_sha256=sha(DECK),
                particles_sha256=sha(os.path.join(a.out, "particles.nrp")), nx=a.nx, mb=mb,
                L=a.L, dx=2 * a.L / a.nx, args=vars(a), threads=a.threads,
                omp_env={k: env[k] for k in env if k.startswith("OMP_")},
                affinity_cpus=cpus, affinity_busy_before=busy)
    with open(os.path.join(a.out, "nm_run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(" ".join(cmd), flush=True)
    t0 = time.time()
    pre = (lambda: os.sched_setaffinity(0, cpus)) if cpus else None
    with open(os.path.join(a.out, "athena.log"), "w") as log:
        r = subprocess.run(cmd, cwd=a.out, stdout=log, stderr=subprocess.STDOUT, env=env,
                           preexec_fn=pre)
    meta.update(exit=r.returncode, wall_s=time.time() - t0)
    with open(os.path.join(a.out, "nm_run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(f"exit {r.returncode}, wall {time.time() - t0:.1f} s", flush=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
