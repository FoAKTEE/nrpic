#!/usr/bin/env python3
"""One registered AthenaK Newtonian-mode run of secondary infall: particle file (nm_ic.py)
and the release processor executable with nm_infall.athinput. Output in --out (default
$NRPIC_RUN_DIR, set by harness/bin/nrpic-run). Nothing here integrates particles; AthenaK
does (decision 0010).

  python3 nm_run.py --kind infall --nx 128 --aend 4 --L 68            # the evolution
  python3 nm_run.py --kind field  --nx 128 --L 68 --onestep           # field calibration
  python3 nm_run.py --kind infall --nx 128 --nlim 20                  # timing probe
"""
import argparse
import hashlib
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
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    ic = [sys.executable, os.path.join(HERE, "nm_ic.py"), "--out", a.out, "--kind", a.kind,
          "--aend", str(a.aend), "--L", str(a.L), "--edge_fac", str(a.edge_fac),
          "--ndust", str(a.ndust), "--nclump", str(a.nclump), "--rclump", str(a.rclump)]
    subprocess.run(ic, check=True, stdout=subprocess.DEVNULL)
    with open(os.path.join(a.out, "setup.json")) as f:
        p = json.load(f)
    mb = a.mb if a.mb > 0 else a.nx // 2
    tlim = p["tlim"]
    over = [f"mesh/nx{i}={a.nx}" for i in (1, 2, 3)]
    over += [f"mesh/x{i}min={-a.L}" for i in (1, 2, 3)] + [f"mesh/x{i}max={a.L}" for i in (1, 2, 3)]
    over += [f"meshblock/nx{i}={mb}" for i in (1, 2, 3)]
    over += [f"particles/particle_file={os.path.join(a.out, 'particles.nrp')}"]
    if a.onestep:
        over += ["time/nlim=1", "time/tlim=1.0", "particles/dt=1e-6", "particles/newton_cfl=0.0",
                 "particles/snap_dt=1e-6", "particles/hist_dcycle=1"]
    else:
        over += [f"time/tlim={tlim!r}", f"time/nlim={a.nlim}", f"particles/dt={a.dtmax}",
                 f"particles/newton_cfl={a.cfl}", f"particles/snap_dt={tlim / a.nsnap!r}"]
    cmd = [a.exe, "-i", DECK, "-d", a.out] + over
    meta = dict(cmd=cmd, exe=a.exe, exe_sha256=sha(a.exe), deck=DECK, deck_sha256=sha(DECK),
                particles_sha256=sha(os.path.join(a.out, "particles.nrp")), nx=a.nx, mb=mb,
                L=a.L, dx=2 * a.L / a.nx, args=vars(a))
    with open(os.path.join(a.out, "nm_run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(" ".join(cmd), flush=True)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(a.out, "athena.log"), "w") as log:
        r = subprocess.run(cmd, cwd=a.out, stdout=log, stderr=subprocess.STDOUT, env=env)
    meta.update(exit=r.returncode, wall_s=time.time() - t0)
    with open(os.path.join(a.out, "nm_run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(f"exit {r.returncode}, wall {time.time() - t0:.1f} s", flush=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
