"""Helpers of the test drivers of the scalar field: run the executable, paths."""
import concurrent.futures
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
PROB = os.path.join(REPO, "problems", "scalar")


def run_case(exe, rundir, inp, args):
    """One execution of the code in rundir; returns the wall time in seconds."""
    os.makedirs(rundir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        flag = "-r" if inp.endswith(".rst") else "-i"
        proc = subprocess.run([exe, flag, inp] + list(args) + ["-d", rundir], cwd=rundir,
                              stdout=log, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {proc.returncode}")
    return round(time.time() - t0, 2)


def run_many(exe, cases, workers=12):
    """cases: list of (rundir, input, args).  Runs them in parallel on `workers` cores;
    returns the wall times in the order of the list."""
    env_threads = os.environ.get("OMP_NUM_THREADS", "1")
    os.environ["OMP_NUM_THREADS"] = env_threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(run_case, exe, *c) for c in cases]
        return [f.result() for f in futs]


def mesh_args(n1, n2, n3, b1=None, b2=None, b3=None):
    b1, b2, b3 = b1 or n1, b2 or n2, b3 or n3
    return [f"mesh/nx1={n1}", f"mesh/nx2={n2}", f"mesh/nx3={n3}",
            f"meshblock/nx1={b1}", f"meshblock/nx2={b2}", f"meshblock/nx3={b3}"]
