#!/usr/bin/env python3
"""Test T12 of work package newton2: the example command lines of the READY file run
with the published processor executable.

    ready_examples.py [--exe ATHENA] [--out DIR] [--fftsp DIR] [--smr DIR] [--nlim N]

Three examples, each started as READY prints it (inputs of problems/newton, particle
files of problems/newton/make_ic.py), N cycles each:
  fft        periodic_fft.athinput, plane wave N = 32: Fourier solver, spectral symbol,
             one group; and the same with newton_fft_symbol = seven_point
  embedded   embedded_ellipsoid.athinput: patch (species 0) in background particles
             (species 1), group history of the patch
  smr        isolated_smr.athinput: moving, rotating ball on a lattice of the fine cell
             size inside the refined MeshBlocks (the case fine_in_smr of test T6c)
Checks: exit status 0; one record per cycle in every history; number and mass of the
patch; with --fftsp (a run directory of the case fftsp of T1 or T11b) the records of
<basename>.newton.hst of the spectral example equal those of that run as text; with
--smr (the card run of fine_in_smr) columns 5 to 18 of the history within 1e-9 of the
card run, relative to the largest value of each column.
Writes DIR/ready_examples.json and DIR/ready_examples.{png,pdf}.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import newton as nw  # noqa: E402

NEWTON = os.path.join(ROOT, "problems", "newton")
EXE = "/data/haiyangw/nrpic/scratch/core/exe/core_newton-2/athena_cpu"
# Track B's embedded ellipsoid (model A; tracks/core/analysis/newton2/cases.py
# embedded_ic, file ic/embedded_setup.json of run core-20261120-221659-da814e5)
S = ["2.2477492612322503", "3.1448230030708744", "4.052021707899205"]
D = ["-0.15721349249419472", "-0.0944697966506601", "-0.031017934277860017"]
RHO_B = "0.000583936065276324"
ENV = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MPLBACKEND="Agg")


def run(cmd, cwd, log):
    with open(log, "w") as f:
        f.write("# " + " ".join(cmd) + "\n")
        f.flush()
        return subprocess.run(cmd, cwd=cwd, env=ENV, stdout=f,
                              stderr=subprocess.STDOUT).returncode


def table(path):
    rows = [ln.split() for ln in open(path) if ln.strip() and not ln.startswith("#")]
    return np.array(rows, dtype=float)


def text_records(path):
    """Records of a history file as text, a record repeated at the end of a run once."""
    out = []
    for ln in open(path):
        if ln.strip() and not ln.startswith("#") and (not out or ln != out[-1]):
            out.append(ln)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=EXE)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--fftsp", default="")
    ap.add_argument("--smr", default="")
    ap.add_argument("--nlim", type=int, default=20)
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    mk = [sys.executable, os.path.join(NEWTON, "make_ic.py")]
    ic = os.path.join(a.out, "ic")
    os.makedirs(ic, exist_ok=True)
    wave, emb, ball = (os.path.join(ic, f) for f in ("wave32.nrp", "embedded.nrp", "ball.nrp"))
    gen = [mk + ["wave", "--out", wave, "--n", "32"],
           mk + ["ball", "--out", emb, "--center", "24", "24", "24", "--radius", "1.5",
                 "--mass", "0.75", "--spacing", "0.125", "--ntracer", "0", "--axes"] + S
           + ["--vgrad"] + D + ["--background", "0", "48", "64", RHO_B],
           mk + ["ball", "--out", ball, "--center", "0.05", "-0.05", "0.03", "--radius", "0.7",
                 "--mass", "0.343", "--spacing", "0.03125", "--ntracer", "0", "--velocity",
                 "-0.2", "0.15", "-0.1", "--omega", "0.2", "-0.3", "0.6"]]
    res = {"exe": a.exe, "nlim": a.nlim, "examples": {}, "generators": []}
    res["exe_sha256"] = subprocess.run(["sha256sum", a.exe], capture_output=True,
                                       text=True).stdout.split()[0]
    for k, g in enumerate(gen):
        rc = run(g, ic, os.path.join(ic, "make_ic.%d.log" % k))
        res["generators"].append(dict(cmd=g, exit=rc))
    n = "time/nlim=%d" % a.nlim
    ex = {
        "fft_spectral": [a.exe, "-i", os.path.join(NEWTON, "periodic_fft.athinput"),
                         "particles/particle_file=" + wave, n],
        "fft_seven_point": [a.exe, "-i", os.path.join(NEWTON, "periodic_fft.athinput"),
                            "particles/particle_file=" + wave,
                            "particles/newton_fft_symbol=seven_point", n],
        "embedded": [a.exe, "-i", os.path.join(NEWTON, "embedded_ellipsoid.athinput"),
                     "particles/particle_file=" + emb, n],
        "smr": [a.exe, "-i", os.path.join(NEWTON, "isolated_smr.athinput"),
                "particles/particle_file=" + ball, "particles/dt=0.002", n],
    }
    ok = all(g["exit"] == 0 for g in res["generators"])
    hst = {}
    for name, cmd in ex.items():
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        rc = run(cmd + ["-d", d], d, os.path.join(d, "athena.log"))
        r = dict(cmd=cmd, exit=rc)
        h = os.path.join(d, "newton.newton.hst")
        if rc == 0 and os.path.exists(h):
            hst[name] = table(h)
            r["records"] = int(len(hst[name]))
            r["finite"] = bool(np.isfinite(hst[name]).all())
        g1 = os.path.join(d, "newton.newton.g1.hst")
        if os.path.exists(g1):
            g = table(g1)
            hst[name + ".g1"] = g
            r["group_records"] = int(len(g))
            r["group_number"], r["group_mass"] = float(g[0, 4]), float(g[0, 5])
        r["ok"] = bool(rc == 0 and r.get("records", 0) >= a.nlim + 1 and r.get("finite"))
        ok = ok and r["ok"]
        res["examples"][name] = r
    e = res["examples"]
    for name in ("fft_spectral", "fft_seven_point", "embedded"):
        good = e[name].get("group_records", 0) == e[name].get("records", -1)
        e[name]["group_ok"] = bool(good)
        ok = ok and good
    if "embedded.g1" in hst:
        e["embedded"]["patch_ok"] = bool(e["embedded"]["group_number"] == 7208
                                         and abs(e["embedded"]["group_mass"] - 0.75) < 1e-12)
        ok = ok and e["embedded"]["patch_ok"]
    if a.fftsp and "fft_spectral" in hst:
        new = text_records(os.path.join(a.out, "fft_spectral", "newton.newton.hst"))
        old = text_records(os.path.join(a.fftsp, "newton.newton.hst"))
        m = len(new)
        e["fft_spectral"]["reference"] = a.fftsp
        e["fft_spectral"]["records_equal_reference"] = int(sum(x == y for x, y in
                                                               zip(new, old[:m])))
        ok = ok and e["fft_spectral"]["records_equal_reference"] == m
    if a.smr and "smr" in hst:
        card = table(os.path.join(a.smr, "newton.newton.hst"))
        m = len(hst["smr"])
        cols = slice(4, 18)
        # a column that is zero in the card run (the integral of K da without expansion)
        # is compared absolutely
        sc = np.abs(card[:, cols]).max(axis=0)
        dev = np.abs(hst["smr"][:, cols] - card[:m, cols]).max(axis=0)/np.where(sc > 0, sc, 1.0)
        e["smr"]["zero_columns"] = [int(k) + 5 for k in np.nonzero(sc == 0)[0]]
        e["smr"]["reference"] = a.smr
        e["smr"]["time_equal"] = bool(np.array_equal(hst["smr"][:, 0], card[:m, 0]))
        e["smr"]["dev_columns_5_18_max"] = float(dev.max())
        e["smr"]["dev_columns_5_18"] = dev.tolist()
        ok = ok and e["smr"]["time_equal"] and dev.max() < 1e-9
    res["ok"] = bool(ok)

    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.9, wspace=0.42)
    ax = axs[0]
    for name, col in (("fft_spectral", fs.PAL["red"]), ("fft_seven_point", fs.PAL["blue"])):
        if name in hst:
            h = hst[name]
            ax.plot(h[:, 0], h[:, 4]/np.abs(h[0, 5]), color=col, label=name[4:] + r": $K$")
            ax.plot(h[:, 0], -h[:, 5]/np.abs(h[0, 5]), color=col, ls="--",
                    label=name[4:] + r": $-W$")
    ax.set_xlabel(r"time $t$")
    ax.set_ylabel(r"$K$, $-W$ in units of $|W_0|$")
    ax.set_title("periodic_fft.athinput", fontsize=7.5)
    ax.legend(loc="center right", fontsize=6)
    ax = axs[1]
    if "embedded.g1" in hst:
        g = hst["embedded.g1"]
        for k, (c, lab) in enumerate(zip((37, 40, 42), ("x", "y", "z"))):
            ax.plot(g[:, 3], np.sqrt(5.0*g[:, c]/g[:, 5]), color=fs.SERIES[k],
                    label="axis $%s$" % lab)
    ax.set_xlabel(r"cosmic time $T$")
    ax.set_ylabel(r"$(5 J_{ii}/M)^{1/2}$ of the patch")
    ax.set_title("embedded_ellipsoid.athinput", fontsize=7.5)
    ax.legend(loc="center right", fontsize=6.5)
    ax = axs[2]
    if "smr" in hst:
        h = hst["smr"]
        dp = np.sqrt(((h[:, 9:12] - h[0, 9:12])**2).sum(axis=1))/h[0, 3]
        ax.plot(h[:, 0], 1e6*dp, color=fs.PAL["red"], label="processor (this run)")
        if a.smr:
            dc = np.sqrt(((card[:m, 9:12] - card[0, 9:12])**2).sum(axis=1))/card[0, 3]
            ax.plot(card[:m, 0], 1e6*dc, color=fs.PAL["blue"], ls="--", label="card (T6c)")
        ax.legend(loc="lower right", fontsize=6.5)
    ax.set_xlabel(r"time $t$")
    ax.set_ylabel(r"$10^6\,|\Delta P|/M$")
    ax.set_title("isolated_smr.athinput", fontsize=7.5)
    fs.save(fig, os.path.join(a.out, "ready_examples"))
    with open(os.path.join(a.out, "ready_examples.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("cmd", "dev_columns_5_18")}
                      for k, v in e.items()}, indent=1))
    print("ready_examples:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
