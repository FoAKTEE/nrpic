"""Synthetic tracer files for testing tracers.py: the six particles of
problems/puncture/tracers_single.athinput integrated as geodesics of static
Schwarzschild in isotropic coordinates (gamma_ij = psi^4 delta_ij, psi = 1 + M/2r,
alpha = (1 - M/2r)/(1 + M/2r), beta = 0), written in the formats of
<base>.traj.bin and <base>.trajmet.bin. A particle stops (as if excised) once
alpha < 0.05. In this static slice L_z and E = alpha W are conserved and the areal
radius of a circular orbit is r psi^2, so tracers.py must show flat lines.

    python3 synth_tracers.py <outdir> [--tend 250] [--dt 0.5]
"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

from common import parse_cli

runs, opts = parse_cli(sys.argv[1:], options=("tend", "dt"))
if not runs:
    sys.exit(__doc__)
outdir = runs[0][1]
tend, dt = float(opts.get("tend", 250.0)), float(opts.get("dt", 0.5))
M = 1.0
# initial data of tracers_single.athinput: x, u_i
P = [((6, 0, 0), (0, 0.5837729484039818, 0)),
     ((8, 0, 0), (0, 0.4596785218238565, 0)),
     ((10, 0, 0), (0, 0.3891849859270371, 0)),
     ((8, 0, 0), (0, 0.3521341772643112, 0.2954756582673984)),
     ((0, 12, 0), (-0.2742177742149252, 0, 0)),
     ((0, 0, 10), (0, 0, 0))]


def metric(x):
    r = np.sqrt(x @ x)
    psi = 1 + M / (2 * r)
    alpha = (1 - M / (2 * r)) / psi
    dpsi = -M / (2 * r ** 3) * x                     # grad psi
    dalpha = (M / r ** 3) * x / psi ** 2              # grad alpha
    return r, psi, alpha, dpsi, dalpha


def rhs(t, y):
    x, u = y[:3], y[3:]
    r, psi, alpha, dpsi, dalpha = metric(x)
    gi = psi ** -4
    W = np.sqrt(1 + gi * (u @ u))
    dx = alpha * gi * u / W
    # du_i/dt = -W d_i alpha - alpha/(2W) u_j u_k d_i gamma^jk, gamma^jk = psi^-4 delta
    du = -W * dalpha + alpha / (2 * W) * (u @ u) * 4 * psi ** -5 * dpsi
    return np.concatenate([dx, du])


def excised(t, y):
    return metric(y[:3])[2] - 0.05


excised.terminal = True
os.makedirs(outdir, exist_ok=True)
times = np.arange(0.0, tend + 0.5 * dt, dt)
traj, met = [], []
for tag, (x0, u0) in enumerate(P):
    sol = solve_ivp(rhs, (0, tend), np.array(x0 + u0, dtype=float), method="DOP853",
                    rtol=1e-12, atol=1e-12, t_eval=times, events=excised)
    for t, y in zip(sol.t, sol.y.T):
        r, psi, alpha, _, _ = metric(y[:3])
        g = psi ** 4
        traj.append([t, tag, *y])
        met.append([t, tag, alpha, 0, 0, 0, g, 0, 0, g, 0, g])
    print(f"tag {tag}: {len(sol.t)} records, t_end = {sol.t[-1]:.2f}")
# records ordered by time, then tag, like the code writes them
traj = np.array(traj)
met = np.array(met)
o = np.lexsort((traj[:, 1], traj[:, 0]))
traj[o].tofile(os.path.join(outdir, "punc.traj.bin"))
met[o].tofile(os.path.join(outdir, "punc.trajmet.bin"))
print("wrote", os.path.join(outdir, "punc.traj.bin"), "and punc.trajmet.bin")
