#!/usr/bin/env python3
"""J4b: where and when P1's sources radiate, from its trackers only (no waveform is read).

Reads the three trackers of P1 (nr_first/scripts/nrread.read_trackers, segments merged, the
copies in trk_keep/ included), puts them on a uniform grid (step 0.05 M) and computes
  - the members' separation r12(t), the binary's centre of mass x_b(t) (bare masses 0.125 each)
    and its distance from the grid origin (the centre of the extraction spheres);
  - a coordinate-track quadrupole luminosity L_trk(t) = (1/5) sum_jk (d^3 Q_jk/dt^3)^2,
    Q_jk = sum_a m_a (x_j x_k - delta_jk r^2/3) with bare masses and the trackers' coordinate
    positions [JUDGEMENT: a proxy for the time profile of the emission, not a gauge-invariant
    quantity]; the third derivative by a Savitzky-Golay filter (window 4 M, order 5) of Q;
  - the circular-orbit formula L_circ = (32/5) mu^2 m_b^3 / r12^5 at the tracked separation;
  - for every emission time t_e the earliest retarded time at which its signal can reach any
    point of a sphere centred on the origin, u_near(t_e) = t_e - |x_b(t_e)| (retarded time
    u = t - R*, the tortoise radius takes the propagation delay [JUDGEMENT]).
Stops reading at t_max (default 120 M). Writes p1_geometry.json, p1_geometry.npz.
Usage: p1_geometry.py <out | -> <P1 run dir> [--tmax=120] [--tmerge=48.8]
"""
import json
import os
import sys

import numpy as np
from scipy.signal import savgol_filter

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "F-hills", "nr_first", "scripts"))
import nrread as nr  # noqa: E402

MASSES = {0: 0.125, 1: 0.125, 2: 1.0}     # bare masses of nr_first/inputs/p1_q4.athinput
DT = 0.05


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    rd = sys.argv[2]
    tmax, tmerge = 120.0, 48.8
    for a in sys.argv[3:]:
        if a.startswith("--tmax="):
            tmax = float(a[7:])
        elif a.startswith("--tmerge="):
            tmerge = float(a[9:])
    os.makedirs(out, exist_ok=True)
    trk = nr.read_trackers(rd)
    t_end = min(float(trk[n]["t"][-1]) for n in trk)
    t = np.arange(0.0, min(tmax, t_end) + 1e-9, DT)
    X = {n: np.vstack([np.interp(t, trk[n]["t"], trk[n]["x"][:, j]) for j in range(3)]).T
         for n in MASSES}
    r12 = np.linalg.norm(X[0] - X[1], axis=1)
    mb = MASSES[0] + MASSES[1]
    xb = (MASSES[0] * X[0] + MASSES[1] * X[1]) / mb
    db = np.linalg.norm(xb, axis=1)
    dh = np.linalg.norm(X[2], axis=1)
    dmem = np.maximum(np.linalg.norm(X[0], axis=1), np.linalg.norm(X[1], axis=1))
    # quadrupole of the three bodies, its third derivative
    Q = np.zeros((len(t), 3, 3))
    for n, m in MASSES.items():
        x = X[n]
        Q += m * (np.einsum("ti,tj->tij", x, x) - np.eye(3)[None] * np.sum(x * x, 1)[:, None, None] / 3)
    w = int(round(4.0 / DT)) | 1
    Q3 = savgol_filter(Q, w, 5, deriv=3, delta=DT, axis=0)
    L = np.sum(Q3 * Q3, axis=(1, 2)) / 5
    mu = MASSES[0] * MASSES[1] / mb
    Lc = 32 / 5 * mu ** 2 * mb ** 3 / np.maximum(r12, 1e-3) ** 5
    pre = t <= tmerge - 0.5
    L0 = float(np.median(L[(t >= 2) & (t <= 20)]))
    u_near = t - db
    res = dict(run_dir=rd, t_end_trackers=t_end, t_max=float(t[-1]), masses=MASSES, dt=DT,
               sg_window_M=w * DT, t_merge=tmerge, L_trk_median_2_20=L0,
               L_circ_t0=float(Lc[0]), r12_t0=float(r12[0]), d_b_t0=float(db[0]),
               d_heavy_t0=float(dh[0]), d_member_max_t0=float(dmem[0]))
    for k in (2, 3, 10):
        i = np.where(pre & (t > 20) & (L > k * L0))[0]
        res[f"t_L_above_{k}x"] = float(t[i[0]]) if len(i) else None
        res[f"u_near_at_L_above_{k}x"] = float(u_near[i[0]]) if len(i) else None
        res[f"d_b_at_L_above_{k}x"] = float(db[i[0]]) if len(i) else None
    for a_ in (4.0, 3.0, 2.0, 1.0):
        i = np.where(r12 < a_)[0]
        res[f"t_r12_below_{a_:g}"] = float(t[i[0]]) if len(i) else None
        res[f"u_near_r12_below_{a_:g}"] = float(u_near[i[0]]) if len(i) else None
    for tt in (0, 10, 20, 30, 40, 45, 48.8):
        i = int(np.argmin(np.abs(t - tt)))
        res[f"at_{tt:g}"] = dict(r12=float(r12[i]), d_b=float(db[i]), d_heavy=float(dh[i]),
                                 L_trk=float(L[i]), L_circ=float(Lc[i]), u_near=float(u_near[i]))
    # earliest retarded arrival of anything emitted after t_e, for a few t_e
    res["min_u_near_after"] = {str(te): float(np.min(u_near[t >= te])) for te in (10, 20, 30, 35, 40)}
    print(json.dumps(res, indent=1, default=float))
    json.dump(res, open(os.path.join(out, "p1_geometry.json"), "w"), indent=1, default=float)
    np.savez(os.path.join(out, "p1_geometry.npz"), t=t, r12=r12, xb=xb, db=db, dh=dh, dmem=dmem,
             L=L, Lc=Lc, u_near=u_near, xh=X[2])


if __name__ == "__main__":
    main()
