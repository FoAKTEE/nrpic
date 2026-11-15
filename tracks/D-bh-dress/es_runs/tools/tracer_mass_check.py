#!/usr/bin/env python3
"""Does a particle with p<n>_m = 0 follow a null geodesic in the release executables?

Runs problems/kerr/geodesic_mesh.athinput (static Kerr-Schild metric on the mesh, a = 0.9,
midpoint pusher; the verified Kerr geodesic of the paper, p0_m = 0.0 in the input) with the
release processor executable twice, unchanged (m = 0) and with particles/p0_m = 1e-30
(m > 0), for tlim = 30 M, and compares the coordinate radius and the normalisation of the
four-velocity of the two trajectories.

    tracer_mass_check.py [--exe PATH] [--out DIR] [--tlim 30]

DIR defaults to $NRPIC_RUN_DIR. Writes DIR/{m0,m1e-30}/ (AthenaK output),
DIR/tracer_mass_check.json, DIR/figs/tracer_mass_check.(png,pdf).
"""
import argparse
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

INPUT = os.path.join(WT, "problems", "kerr", "geodesic_mesh.athinput")
A, M = 0.9, 1.0


def ks_metric(x):
    """Cartesian Kerr-Schild: gamma_ij = delta_ij + 2H l_i l_j, alpha = 1/sqrt(1 + 2H)."""
    X, Y, Z = x
    R2 = X * X + Y * Y + Z * Z
    r2 = 0.5 * (R2 - A * A + np.sqrt((R2 - A * A) ** 2 + 4 * A * A * Z * Z))
    r = np.sqrt(r2)
    H = M * r ** 3 / (r ** 4 + A * A * Z * Z)
    l = np.array([(r * X + A * Y) / (r2 + A * A), (r * Y - A * X) / (r2 + A * A), Z / r])
    g = np.eye(3) + 2 * H * np.outer(l, l)
    return r, g


def run(exe, out, extra, tlim):
    os.makedirs(out, exist_ok=True)
    cmd = [exe, "-i", INPUT, "-d", out, f"time/tlim={tlim}"] + extra
    with open(os.path.join(out, "athena.log"), "w") as log:
        rc = subprocess.call(cmd, cwd=out, stdout=log, stderr=subprocess.STDOUT)
    a = np.fromfile(os.path.join(out, "geo.traj.bin"), dtype=np.float64)
    a = a[: len(a) // 8 * 8].reshape(-1, 8)
    return rc, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default="/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--tlim", type=float, default=30.0)
    a = ap.parse_args()
    res = {"exe": a.exe, "input": INPUT, "tlim": a.tlim, "cases": {}}
    traj = {}
    for name, extra in (("m0", []), ("m1e-30", ["particles/p0_m=1.0e-30"])):
        rc, tr = run(a.exe, os.path.join(a.out, name), extra, a.tlim)
        t, x, u = tr[:, 0], tr[:, 2:5], tr[:, 5:8]
        rbl, norm = [], []
        for xi, ui in zip(x, u):
            r, g = ks_metric(xi)
            rbl.append(r)
            norm.append(float(ui @ np.linalg.inv(g) @ ui))      # gamma^ij u_i u_j
        rbl, norm = np.array(rbl), np.array(norm)
        speed = np.gradient(np.linalg.norm(x, axis=1), t)
        traj[name] = (t, rbl, speed)
        res["cases"][name] = dict(exit=rc, n=int(len(t)), r_BL_start=float(rbl[0]), r_BL_end=float(rbl[-1]),
                                  r_BL_min=float(rbl.min()), r_BL_max=float(rbl.max()),
                                  gamma_uu_start=float(norm[0]), gamma_uu_end=float(norm[-1]),
                                  max_abs_coord_radial_speed=float(np.max(np.abs(speed))))
    with open(os.path.join(a.out, "tracer_mass_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 5.0), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.1, top=0.97, hspace=0.06)
    for (name, (t, r, v)), c, lab in zip(traj.items(), (fs.PAL["red"], fs.PAL["blue"]),
                                         (r"$p0\_m = 0$ (as in the input)", r"$p0\_m = 10^{-30}$")):
        axs[0].plot(t, r, color=c, label=lab)
        axs[1].plot(t, v, color=c)
    axs[0].set_ylabel(r"Boyer-Lindquist $r/M$")
    axs[0].legend(loc="upper left")
    axs[1].set_ylabel(r"$d|x|/dt$")
    axs[1].set_xlabel(r"$t/M$")
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    fs.save(fig, os.path.join(a.out, "figs", "tracer_mass_check"))


if __name__ == "__main__":
    main()
