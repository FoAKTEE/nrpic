#!/usr/bin/env python3
"""Run the tests of the initial-data solver of the code as registered runs.

    run_tests.py --exe ATHENA [--tests t1,t2,t3,t4] [--only NAME,...] [--jobs 6]
                 [--card] [--suffix S] [--runs FILE] [--list]

Initial data are written once into scratch/core/idsolve_ic/ (problems/idsolve/make_ic.py,
problems/ic/make_ball.py). Every case is one run registered by hand with
tracks/core/tools/run_registered.py (harness/bin/nrpic-run fails on the manifests of
wave 1, see the journal); its run id is stored in runs.json of this directory under the
name of the case, replacing an earlier run of the same case.

Cases (names): tests T1 to T4 of tracks/core/JOURNAL-idsolve.md.
  t1  gauss_<mode>_n<N>[_ng<g>][_comp]   Gaussian at rest, Robin faces
  t2  ball_<edge>_<mode>_f<nfilter>_n<N> expanding ball with its table curvature
  t3  tri_<mode>_n<N>                    the ball with a triaxial strain of 0.05
                                         (mode off: without the solve)
  t4  torus_<mode>_p<ppc>_n<N>           plane wave on the torus
"""
import argparse
import concurrent.futures
import glob
import json
import os
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
IC = "/data/haiyangw/nrpic/scratch/core/idsolve_ic"
RUNS = os.path.join(HERE, "runs.json")
PY = sys.executable


def sh(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError("%s\n%s\n%s" % (" ".join(cmd), out.stdout, out.stderr))
    return out.stdout


def fmt(v):
    return ("%g" % v).replace(".", "p")


def ic_gauss(h):
    stem = "gauss_h" + fmt(h)
    if not os.path.exists(os.path.join(IC, stem + ".nrp")):
        sh([PY, os.path.join(WT, "problems/idsolve/make_ic.py"), "gaussian", "--h", str(h),
            "--out", IC, "--prefix", stem])
    return os.path.join(IC, stem + ".nrp")


def ic_ball(h, edge):
    stem = "ball_h" + fmt(h) + ("_w" + fmt(edge) if edge > 0 else "")
    if not os.path.exists(os.path.join(IC, stem + ".nrp")):
        cmd = [PY, os.path.join(WT, "problems/ic/make_ball.py"), "--Rb", "10", "--h", str(h),
               "--tracers", "", "--sample", "0", "--out", IC, "--prefix", stem]
        if edge > 0:
            cmd += ["--edge", str(edge)]
        sh(cmd)
    return os.path.join(IC, stem + ".nrp"), os.path.join(IC, stem + ".tab")


def ic_tri(h, e):
    nrp, tab = ic_ball(h, 0.0)
    stem = "tri_h" + fmt(h) + "_e" + fmt(e)
    if not os.path.exists(os.path.join(IC, stem + ".nrp")):
        sh([PY, os.path.join(WT, "problems/idsolve/make_ic.py"), "strain", "--in", nrp,
            "--e", str(e), "--out", IC, "--prefix", stem])
    return os.path.join(IC, stem + ".nrp"), tab


def ic_wave(n, ppc):
    stem = "wave_n%d_p%d" % (n, ppc)
    if not os.path.exists(os.path.join(IC, stem + ".nrp")):
        sh([PY, os.path.join(WT, "problems/idsolve/make_ic.py"), "wave", "--n", str(n),
            "--ppc", str(ppc), "--out", IC, "--prefix", stem])
    return os.path.join(IC, stem + ".nrp")


def mesh_args(n, mb):
    return ["mesh/nx1=%d" % n, "mesh/nx2=%d" % n, "mesh/nx3=%d" % n,
            "meshblock/nx1=%d" % mb, "meshblock/nx2=%d" % mb, "meshblock/nx3=%d" % mb]


def cases(tests):
    out = {}
    if "t1" in tests:
        for n in (32, 64, 128):
            dx = 32.0/n
            mb = 16 if n == 32 else 32
            for mode in ("stencil", "code"):
                out["gauss_%s_n%d" % (mode, n)] = dict(
                    test="t1", inp="problems/idsolve/gaussian.athinput",
                    files=[lambda dx=dx: ic_gauss(dx/2)], pfile=0,
                    args=mesh_args(n, mb) + ["particles/id_residual=" + mode],
                    meta=dict(n=n, dx=dx, mode=mode, ng=4))
            if n < 128:
                out["gauss_code_n%d_comp" % n] = dict(
                    test="t1", inp="problems/idsolve/gaussian.athinput",
                    files=[lambda dx=dx: ic_gauss(dx/2)], pfile=0,
                    args=mesh_args(n, mb) + ["particles/id_residual=code",
                                              "particles/deposit_comp_c=0.08333333333333333"],
                    meta=dict(n=n, dx=dx, mode="code", ng=4, comp=1.0/12.0))
        for ng in (2, 3):
            out["gauss_code_n64_ng%d" % ng] = dict(
                test="t1", inp="problems/idsolve/gaussian.athinput",
                files=[lambda: ic_gauss(0.25)], pfile=0,
                args=mesh_args(64, 32) + ["particles/id_residual=code",
                                          "mesh/nghost=%d" % ng],
                meta=dict(n=64, dx=0.5, mode="code", ng=ng))
    if "t2" in tests:
        for n in (32, 64, 128):
            dx = 64.0/n
            mb = 16 if n == 32 else 32
            combos = [("sharp", "code", 0), ("sharp", "stencil", 0), ("sharp", "code", 1),
                      ("smooth", "code", 0)]
            for edge, mode, nf in combos:
                w = 2.0 if edge == "smooth" else 0.0
                out["ball_%s_%s_f%d_n%d" % (edge, mode, nf, n)] = dict(
                    test="t2", inp="problems/idsolve/ball.athinput",
                    files=[lambda dx=dx, w=w: ic_ball(dx/2, w)], pfile=0, tfile=1,
                    args=mesh_args(n, mb) + ["particles/id_residual=" + mode,
                                              "particles/nfilter=%d" % nf],
                    meta=dict(n=n, dx=dx, mode=mode, nfilter=nf, edge=w))
    if "t3" in tests:
        for n in (32, 64, 128):
            dx = 64.0/n
            mb = 16 if n == 32 else 32
            for mode in ("code", "stencil"):
                out["tri_%s_n%d" % (mode, n)] = dict(
                    test="t3", inp="problems/idsolve/ball.athinput",
                    files=[lambda dx=dx: ic_tri(dx/2, 0.05)], pfile=0, tfile=1,
                    args=mesh_args(n, mb) + ["particles/id_residual=" + mode,
                                              "particles/nfilter=0"],
                    meta=dict(n=n, dx=dx, mode=mode, nfilter=0, e=0.05))
            # the trial data as the code starts from them without the solve
            out["tri_off_n%d" % n] = dict(
                test="t3", inp="problems/idsolve/ball.athinput",
                files=[lambda dx=dx: ic_tri(dx/2, 0.05)], pfile=0, tfile=1,
                args=mesh_args(n, mb) + ["particles/id_solve=false", "particles/nfilter=0"],
                meta=dict(n=n, dx=dx, mode="off", nfilter=0, e=0.05))
    if "t4" in tests:
        for n in (32, 64):
            mb = 16 if n == 32 else 32
            for ppc in (1, 2):
                for mode in ("stencil", "code"):
                    out["torus_%s_p%d_n%d" % (mode, ppc, n)] = dict(
                        test="t4", inp="problems/idsolve/torus.athinput",
                        files=[lambda n=n, ppc=ppc: ic_wave(n, ppc)], pfile=0,
                        args=mesh_args(n, mb) + ["particles/id_residual=" + mode],
                        meta=dict(n=n, dx=2.0/n, mode=mode, ppc=ppc))
    return out


def run_case(name, c, exe, card):
    files = []
    for f in c["files"]:
        r = f()
        files += list(r) if isinstance(r, tuple) else [r]
    args = list(c["args"])
    args.append("particles/particle_file=" + os.path.basename(files[c["pfile"]]))
    if "tfile" in c:
        args.append("problem/comp0_file=" + os.path.basename(files[c["tfile"]]))
    cmd = [PY, os.path.join(WT, "tracks/core/tools/run_registered.py"),
           "--purpose", "initial-data solver, test %s, case %s" % (c["test"].upper(), name),
           "--tag", "idsolve-" + name, "--cores", "1",
           "--input", os.path.join(WT, c["inp"])]
    for f in files:
        cmd += ["--input", f]
    cmd += ["--"]
    if card:
        cmd += ["srun", "-p", "preempt", "--gres=gpu:1", "-c", "1", "-t", "00:15:00"]
    cmd += [exe, "-i", os.path.basename(c["inp"])] + args
    # run ids carry the second of the start: two runs must not start in the same second
    with START:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        time.sleep(1.2)
    so, se = proc.communicate()
    lines = so.strip().splitlines()
    if len(lines) < 2:
        return name, "", "failed to start: " + se.strip()[-300:], args
    return name, lines[-1], lines[-2], args


START = threading.Lock()


def collect(cs, runs, suffix):
    """Run ids of the cases from the manifests (tag idsolve-<case>), the latest finished
    run of each case; for runs whose id did not reach the file of run ids."""
    found = {}
    for mf in sorted(glob.glob(os.path.join(WT, "tracks/core/runs/*/manifest.json"))):
        with open(mf) as f:
            m = json.load(f)
        tag = m.get("tag", "")
        if not tag.startswith("idsolve-") or m.get("state") != "finished":
            continue
        name = tag[len("idsolve-"):]
        card = any(w == "srun" for w in m["command"]) or m.get("card_hours", 0.0) > 0.0
        if name in cs and (suffix == "_card") == bool(card):
            found[name] = m          # sorted by run id: the latest wins
    for name, m in found.items():
        i = m["command"].index("-i")
        runs[name + suffix] = dict(
            run_id=m["run_id"], status="exit %d, wall %.1f s, output %s" % (
                m["exit_status"], m["wall_time_s"], m["output_directory"]),
            args=m["command"][i + 2:], exe=m["command"][i - 1], **cs[name]["meta"],
            test=cs[name]["test"])
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=os.path.join(WT, ".work/build_cpu/src/athena"))
    ap.add_argument("--tests", default="t1,t2,t3,t4")
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--card", action="store_true")
    ap.add_argument("--suffix", default="", help="appended to the case names in runs.json")
    ap.add_argument("--runs", default=RUNS, help="file that collects the run ids")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--collect", action="store_true",
                    help="no runs: rebuild the file of run ids from the manifests")
    a = ap.parse_args()
    cs = cases(a.tests.split(","))
    if a.only:
        cs = {k: v for k, v in cs.items() if k in a.only.split(",")}
    if a.list:
        for k in cs:
            print(k)
        return 0
    if a.collect:
        runs = {}
        if os.path.exists(a.runs):
            with open(a.runs) as f:
                runs = json.load(f)
        found = collect(cs, runs, a.suffix)
        with open(a.runs, "w") as f:
            json.dump(runs, f, indent=1, sort_keys=True)
            f.write("\n")
        print("collected %d of %d cases" % (len(found), len(cs)))
        for k in cs:
            if k not in found:
                print("  no finished run:", k)
        return 0
    os.makedirs(IC, exist_ok=True)
    # initial data first, one after the other (several cases share a file)
    for c in cs.values():
        for f in c["files"]:
            f()
    runs = {}
    if os.path.exists(a.runs):
        with open(a.runs) as f:
            runs = json.load(f)
    bad = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(run_case, k, v, a.exe, a.card) for k, v in cs.items()]
        for fut in concurrent.futures.as_completed(futs):
            name, run_id, status, args = fut.result()
            runs[name + a.suffix] = dict(run_id=run_id, status=status, args=args,
                                         exe=a.exe, **cs[name]["meta"], test=cs[name]["test"])
            print("%-28s %s  %s" % (name + a.suffix, run_id, status))
            bad += 0 if status.startswith("exit 0") else 1
            with open(a.runs, "w") as f:
                json.dump(runs, f, indent=1, sort_keys=True)
                f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
