"""Runs of the shear package: initial data (make_shear_ic.py) and one AthenaK process per
case, at most --npar at a time (serial processor executable by default).

    python3 run_cases.py --list inputs/<list>.txt [--npar 4] [--exe PATH]
                         [--threads 1] [--analyze]

A list line: name beta HL ny [key=value ...], keys
  ppc_y (1), nxz (4), lapse (lapse_harmonic, 0.3333333333333333), cfl (0.25),
  tfac (tlim = tfac * L, 1.5), fanA, fanB ("centre,halfwidth,n", relative half width
  unless fan_abs=1), dtexp (dt_expansion, 0.01).
Output: $NRPIC_RUN_DIR/<name>/ (ic/ with the data, the AthenaK files, athena.log,
time.log); $NRPIC_RUN_DIR/runs.json with the wall times. With --analyze each case is
analysed after its run (analyze_rays.py), and the results go to <name>/rays.json.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DECK = os.path.join(PKG, "inputs", "shear.athinput")
EXE_DEFAULT = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"


def parse_list(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            w = line.split()
            opt = dict(kv.split("=", 1) for kv in w[4:])
            rows.append({"name": w[0], "beta": float(w[1]), "HL": float(w[2]),
                         "ny": int(w[3]), **opt})
    return rows


def prepare(row, out):
    d = os.path.join(out, row["name"])
    ic = os.path.join(d, "ic")
    os.makedirs(ic, exist_ok=True)
    args = [sys.executable, os.path.join(HERE, "make_shear_ic.py"), "--beta",
            repr(row["beta"]), "--HL", repr(row["HL"]), "--ny", str(row["ny"]),
            "--nxz", row.get("nxz", "4"), "--ppc-y", row.get("ppc_y", "1"), "--out", ic]
    for k in ("fanA", "fanB"):
        if k in row:
            args += ["--" + k, row[k]]
    if row.get("fan_abs", "0") == "1":
        args += ["--fan-abs"]
    with open(os.path.join(d, "ic.log"), "w") as lg:
        subprocess.run(args, check=True, stdout=lg, stderr=subprocess.STDOUT)
    with open(os.path.join(ic, "meta.json")) as f:
        meta = json.load(f)
    L = meta["L"]
    nxz = int(row.get("nxz", "4"))
    ny = row["ny"]
    tlim = float(row.get("tfac", "1.5"))*L
    cmd = ["-i", DECK, "-d", d,
           f"mesh/nx1={nxz}", f"mesh/nx2={ny}", f"mesh/nx3={nxz}",
           f"meshblock/nx1={nxz}", f"meshblock/nx2={ny}", f"meshblock/nx3={nxz}",
           f"mesh/x1min={-0.5*L!r}", f"mesh/x1max={0.5*L!r}",
           f"mesh/x2min={-0.5*L!r}", f"mesh/x2max={0.5*L!r}",
           f"mesh/x3min={-0.5*L!r}", f"mesh/x3max={0.5*L!r}",
           f"time/tlim={tlim!r}", f"time/cfl_number={row.get('cfl', '0.25')}",
           f"z4c/lapse_harmonic={row.get('lapse', '0.3333333333333333')}",
           f"particles/dt_expansion={row.get('dtexp', '0.01')}",
           f"particles/traj_ntrack={meta['traj_ntrack']}",
           f"particles/particle_file={os.path.join(ic, 'particles.nrp')}",
           f"problem/id_file={os.path.join(ic, 'fields.bin')}"]
    shutil.copy(DECK, d)
    with open(os.path.join(d, "case.json"), "w") as f:
        json.dump({"row": row, "athena_args": cmd, "tlim": tlim}, f, indent=1)
    return d, cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--npar", type=int, default=4)
    ap.add_argument("--exe", default=EXE_DEFAULT)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    out = os.environ["NRPIC_RUN_DIR"]
    rows = parse_list(a.list)
    env = dict(os.environ, OMP_NUM_THREADS=str(a.threads), OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", OMP_PROC_BIND="false")
    jobs = [prepare(r, out) for r in rows]
    running, done = [], []
    pending = list(zip(rows, jobs))
    while pending or running:
        while pending and len(running) < a.npar:
            row, (d, cmd) = pending.pop(0)
            lg = open(os.path.join(d, "athena.log"), "w")
            t0 = time.time()
            p = subprocess.Popen(["/usr/bin/time", "-v", "-o", os.path.join(d, "time.log"),
                                  a.exe] + cmd, cwd=d, stdout=lg, stderr=subprocess.STDOUT,
                                 env=env)
            running.append((row, d, p, t0, lg))
        time.sleep(2.0)
        still = []
        for row, d, p, t0, lg in running:
            if p.poll() is None:
                still.append((row, d, p, t0, lg))
                continue
            lg.close()
            rec = {"name": row["name"], "rc": p.returncode, "wall_s": time.time() - t0}
            if a.analyze and p.returncode == 0:
                r = subprocess.run([sys.executable, os.path.join(HERE, "analyze_rays.py"),
                                    d], capture_output=True, text=True, env=env)
                rec["analyze_rc"] = r.returncode
                with open(os.path.join(d, "analyze.log"), "w") as f:
                    f.write(r.stdout + r.stderr)
            print(json.dumps(rec), flush=True)
            done.append(rec)
        running = still
    with open(os.path.join(out, "runs.json"), "w") as f:
        json.dump(done, f, indent=1)
    sys.exit(0 if all(r["rc"] == 0 for r in done) else 1)


if __name__ == "__main__":
    main()
