"""Helpers of the test drivers of the second scalar-field package: paths, running the
executable, the test case in code units, figure style."""
import concurrent.futures
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
PROB = os.path.join(REPO, "problems", "scalar")

import numpy as np                        # noqa: E402
from nrpic import sf_inflation as inf     # noqa: E402


def run_case(exe, rundir, inp, args):
    """One execution of the code in rundir; returns the wall time in seconds."""
    os.makedirs(rundir, exist_ok=True)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        flag = "-r" if inp.endswith(".rst") else "-i"
        proc = subprocess.run([exe, flag, inp] + list(args) + ["-d", rundir], cwd=rundir,
                              stdout=log, stderr=subprocess.STDOUT, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {proc.returncode}")
    return round(time.time() - t0, 2)


def run_many(exe, cases, workers=12):
    """cases: list of (rundir, input, args); runs them in parallel on `workers` cores and
    returns the wall times in the order of the list."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(run_case, exe, *c) for c in cases]
        return [f.result() for f in futs]


def mesh_args(n, b=None):
    b = b or n
    return [f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
            f"meshblock/nx1={b}", f"meshblock/nx2={b}", f"meshblock/nx3={b}"]


def sr_case(nmax2, kstart=None):
    """The slow-roll (quadratic) case of arXiv:2512.14649 in code units."""
    return inf.code_case(inf.quadratic_model(), nmax2, kstart=kstart)


def write_case(case, outdir, name="modes.txt"):
    """Mode file of the case in outdir; returns the command-line options that set the
    background and the potential (the input file must have these parameters)."""
    os.makedirs(outdir, exist_ok=True)
    fname = os.path.join(outdir, name)
    inf.write_mode_file(fname, case["n2"], case["R"], case["dR"],
                        header=f"{case['model']} case, code units (G = 1, time unit "
                               f"1/H*), H*/Mpl = {case['h_star_planck']:.10e}")
    args = [f"problem/phi0={case['phi0']:.17e}", f"problem/pi0={case['pi0']:.17e}",
            f"scalar_field/noise_mode_file={fname}"]
    if case["potential"] == "quadratic":
        args.append(f"scalar_field/mass={case['mass']:.17e}")
    else:
        args += [f"scalar_field/lambda={case['lambda']:.17e}",
                 f"scalar_field/vev={case['vev']:.17e}"]
    return args


def dump_json(obj, fname):
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(fname, "w") as fp:
        json.dump(obj, fp, indent=1, default=conv)


def style():
    """Figure style of the repository (python/nrpic/figstyle.py)."""
    import matplotlib
    matplotlib.use("Agg")
    from nrpic import figstyle
    figstyle.use_style()
    return figstyle
