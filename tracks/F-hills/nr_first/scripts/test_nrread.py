#!/usr/bin/env python3
"""Tests of nrread.py (E4 of nr_first/JOURNAL.md).

    test_nrread.py synthetic <outdir>        full Newtonian three-body run from the q = 4
                                             start state written in AthenaK's formats
    test_nrread.py single <rundir>...         card runs S1-S3 (one puncture)
    test_nrread.py three <rundir>             processor run of the three-black-hole data
                                             (one cycle)
Each prints PASS/FAIL lines and writes <outdir or rundir>/test_nrread_<mode>.json.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

Q4 = os.path.join(WT, "tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput")
RESULTS = []


def check(name, ok, detail):
    RESULTS.append(dict(test=name, ok=bool(ok), detail=detail))
    print(("PASS " if ok else "FAIL ") + name + ": " + detail, flush=True)


def read_athinput(path):
    """Problem block of an athinput -> masses (n,), positions (n, 3), momenta (n, 3)."""
    blk, d = None, {}
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("<"):
            blk = line.strip("<>")
            continue
        if "=" in line and blk == "problem":
            k, v = [s.strip() for s in line.split("=", 1)]
            d[k] = v
    n = int(d["ncomp"])
    m = np.array([float(d[f"comp{i}_mass"]) for i in range(n)])
    x = np.array([[float(d.get(f"comp{i}_x{k}", 0.0)) for k in (1, 2, 3)] for i in range(n)])
    p = np.array([[float(d.get(f"comp{i}_p{k}", 0.0)) for k in (1, 2, 3)] for i in range(n)])
    return m, x, p


def newton(m, x, p, t_end, dt_out):
    n = m.size

    def rhs(t, y):
        X = y[:3 * n].reshape(n, 3)
        A = np.zeros((n, 3))
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = X[j] - X[i]
                    A[i] += m[j] * d / np.linalg.norm(d) ** 3
        return np.concatenate([y[3 * n:], A.ravel()])

    y0 = np.concatenate([x.ravel(), (p / m[:, None]).ravel()])
    ts = np.arange(0.0, t_end + 0.5 * dt_out, dt_out)
    s = solve_ivp(rhs, (0, ts[-1]), y0, method="DOP853", t_eval=ts, rtol=1e-12, atol=1e-14)
    Y = s.y.T
    return ts, Y[:, :3 * n].reshape(-1, n, 3), Y[:, 3 * n:].reshape(-1, n, 3)


def write_tracker(path, it, t, x, v):
    with open(path, "w") as f:
        f.write("# Black Hole\n# 1:iter 2:time 3:x 4:y 5:z 6:vx 7:vy 8:vz\n")
        for k in range(len(t)):
            f.write(" ".join([str(int(it[k])), repr(float(t[k]))] +
                             ["%.19g" % c for c in x[k]] + ["%.19g" % c for c in v[k]]) + "\n")


def v5b_range():
    v = json.load(open(os.path.join(WT, "tracks/F-hills/stage/G0/checks/v5b_summary.json")))
    return v["q4"]["E_bary_late_max"] - v["q4"]["E_bary_late_min"]


def synthetic(out):
    os.makedirs(out, exist_ok=True)
    m, x, p = read_athinput(Q4)                  # comp0 = m1, comp1 = m2, comp2 = M
    M, m1, m2 = m[2], m[0], m[1]
    a0 = 5.0
    Eu = m1 * m2 / a0 * (M / (m1 + m2)) ** (1 / 3)
    dt = 0.0625
    ts, X, V = newton(m, x, p, 1500.0, dt)
    it = np.arange(len(ts)) * 16                 # cycle numbers (16 cycles per row)
    rd = os.path.join(out, "run")
    os.makedirs(os.path.join(rd, "trk_keep", "seg1"), exist_ok=True)
    # a chain of two segments: the first wrote rows up to t = 700, the second restarted
    # from t = 600 (an earlier restart file) and wrote to the end; the copy of the first
    # segment's file is in trk_keep/seg1/
    k1 = np.searchsorted(ts, 700.0, side="right")
    k2 = np.searchsorted(ts, 600.0)
    for n in range(3):
        write_tracker(os.path.join(rd, "trk_keep", "seg1", f"hills.co_{n}.txt"),
                      it[:k1], ts[:k1], X[:k1, n], V[:k1, n])
        write_tracker(os.path.join(rd, f"hills.co_{n}.txt"), it[k2:], ts[k2:], X[k2:, n],
                      V[k2:, n])
    # horizon summary appended across the restart (rows from 600 to 700 twice)
    for n in range(3):
        rows = [(16, t, m[n] * 1.03, 0, 0, 0, 0, 1.0, 1e-6, 1e-3, 0.5 * m[n], 0.49 * m[n])
                for t in ts[::16]]
        rows = [r for r in rows if r[1] <= 700.0] + [r for r in rows if r[1] >= 600.0]
        with open(os.path.join(rd, f"hills.horizon_summary_{n}.txt"), "w") as f:
            f.write("# 1:iter 2:time 3:mass 4:Sx 5:Sy 6:Sz 7:S 8:area 9:hrms 10:hmean "
                    "11:meanradius 12:minradius\n")
            for r in rows:
                f.write(" ".join("%.16e" % c for c in r) + "\n")

    trk = nr.read_trackers(rd)
    check("trackers found", sorted(trk) == [0, 1, 2], f"{sorted(trk)}")
    ok = all(len(trk[n]["t"]) == len(ts) and np.all(np.diff(trk[n]["t"]) > 0) for n in trk)
    check("merged rows: every time once, in order", ok,
          f"{[len(trk[n]['t']) for n in trk]} rows against {len(ts)}")
    err = max(float(np.max(np.abs(trk[n]["x"] - X[:, n]))) for n in trk)
    check("positions read back to the printed digits", err < 1e-12, f"max error {err:.2e}")
    hz = nr.read_horizons(rd)
    nh = [len(hz[n][0]["t"]) for n in hz]
    check("horizon rows: duplicates after the restart removed", nh == [len(ts[::16])] * 3,
          f"{nh} against {len(ts[::16])}")

    t, Xr, Vr = nr.common_times(trk)
    E = nr.member_energies(Xr, Vr, m, iM=2)
    ie = 0 if E["E_0_bc"][-1] > 0 else 1
    late = t >= 300.0
    ebc = E[f"E_{ie}_bc"][late] / Eu
    e2b = E[f"E_{ie}_M"][late] / Eu
    check("ejected member is m1 (comp0), as V5b", ie == 0, f"ejected comp{ie}")
    # E4 predicted 1e-4 and failed (run F-20261115-173719-923135a: 1.54e-4, the same range
    # as the lead's V5b, late min/max of v5b_summary.json); the residual is the coupling to
    # the captured member's orbit, not the reader. Threshold since then: 2e-4.
    check("barycentric energy constant after the encounter (< 2e-4 units)",
          float(np.ptp(ebc)) < 2e-4, f"range {np.ptp(ebc):.2e} units (V5b: "
          f"{v5b_range():.2e})")
    v5b = json.load(open(os.path.join(WT, "tracks/F-hills/stage/G0/checks/v5b_summary.json")))
    ref = v5b["q4"]["E_bary_end"]
    check("barycentric energy equals the lead's V5b value within 1e-3 units",
          abs(ebc[-1] - ref) < 1e-3, f"{ebc[-1]:.5f} against {ref:.5f} "
          "(run F-hills-20261115-145559-a314517)")
    check("two-body energy with M alone oscillates by more than 0.1 units",
          float(np.ptp(e2b)) > 0.1, f"range {np.ptp(e2b):.3f} units")
    vfit = nr.velocity_from_positions(t[:4000], Xr[:4000, 0], window=1.0)
    verr = float(np.max(np.abs(vfit - Vr[:4000, 0])))
    check("velocity from positions (1 M window) equals the true velocity within 1e-4",
          verr < 1e-4, f"max error {verr:.2e}")
    # total energy as a check of the integration itself
    Etot = (0.5 * np.sum(m[None, :, None] * Vr ** 2, axis=(1, 2))
            - sum(m[i] * m[j] / np.linalg.norm(Xr[:, i] - Xr[:, j], axis=1)
                  for i in range(3) for j in range(i + 1, 3)))
    check("integration: total energy conserved to 1e-8 relative",
          float(np.ptp(Etot) / abs(Etot[0])) < 1e-8, f"{np.ptp(Etot) / abs(Etot[0]):.1e}")

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax[0].plot(t, E["r_0M"], color=fs.PAL["blue"], label=r"$m_1$ (comp0)")
    ax[0].plot(t, E["r_1M"], color=fs.PAL["red"], label=r"$m_2$ (comp1)")
    ax[0].plot(t, E["r_12"], color=fs.PAL["yellow"], label=r"$|x_1-x_2|$")
    ax[0].axvspan(600, 700, color="grey", alpha=0.15, lw=0)
    ax[0].set_yscale("log")
    ax[0].set_xlim(0, 1500)
    ax[0].set_xlabel(r"$t\,[M]$")
    ax[0].set_ylabel(r"distance $[M]$")
    ax[0].legend(frameon=False, fontsize=7)
    ax[0].set_title("synthetic tracker files (Newton, q = 4)", fontsize=9)
    for k, col in ((0, fs.PAL["blue"]), (1, fs.PAL["red"])):
        ax[1].plot(t, E[f"E_{k}_M"] / Eu, color=col, lw=0.8, ls="--")
        ax[1].plot(t, E[f"E_{k}_bc"] / Eu, color=col, lw=1.4)
    ax[1].axhline(ref, **fs.GUIDE)
    ax[1].set_xlim(0, 1500)
    ax[1].set_ylim(-3, 3)
    ax[1].set_xlabel(r"$t\,[M]$")
    ax[1].set_ylabel(r"member energy [$(m_1m_2/a)(M/m_b)^{1/3}$]")
    ax[1].set_title("solid: against barycentre of M + other; dashed: with M", fontsize=8)
    fig.tight_layout()
    paths = fs.save(fig, os.path.join(out, "fig_test_nrread_synthetic"))
    return dict(results=RESULTS, unit=Eu, E_bc_end=float(ebc[-1]), ref=ref, figure=paths)


def single(rundirs):
    res = {}
    for rd in rundirs:
        name = os.path.basename(os.path.normpath(rd))
        trk = nr.read_trackers(rd)
        hz = nr.read_horizons(rd)
        hst = nr.read_hst([os.path.join(rd, f) for f in os.listdir(rd)
                           if f.endswith(".z4c.user.hst")][0])
        tr = trk[0]
        check(f"{name}: one tracker, time increasing", sorted(trk) == [0] and
              bool(np.all(np.diff(tr["t"]) > 0)), f"{len(tr['t'])} rows")
        steps = np.unique(np.round(np.diff(tr["t"]), 12))
        check(f"{name}: one row per cycle (constant step)", steps.size == 1,
              f"steps {steps[:4]}")
        yz = float(np.max(np.abs(tr["x"][:, 1:])))
        check(f"{name}: tracker stays on the x axis (symmetric data)", yz < 1e-8,
              f"max |y|, |z| = {yz:.1e}")
        h, nmiss = hz[0]
        check(f"{name}: horizon found in every search", nmiss == 0 and len(h["t"]) > 0,
              f"{len(h['t'])} found, {nmiss} missed")
        res[name] = dict(rows=int(len(tr["t"])), horizons=int(len(h["t"])), missed=nmiss,
                         hst_rows=int(len(hst["time"])))
    return dict(results=RESULTS, runs=res)


def three(rd):
    m, x, p = read_athinput(Q4)
    trk = nr.read_trackers(rd)
    hz = nr.read_horizons(rd)
    check("three trackers", sorted(trk) == [0, 1, 2], f"{sorted(trk)}")
    err = max(float(np.max(np.abs(trk[n]["x"][0] - x[n]))) for n in trk)
    check("trackers start at the input positions (1e-6)", err < 1e-6, f"max error {err:.1e}")
    masses = {n: (float(hz[n][0]["mass"][0]) if len(hz[n][0]["mass"]) else math.nan)
              for n in hz}
    check("three horizons from the first search", len(hz) == 3 and
          all(np.isfinite(v) for v in masses.values()), f"{masses}")
    okm = (0.128 <= masses.get(0, 0) <= 0.132 and 0.128 <= masses.get(1, 0) <= 0.132
           and 1.00 <= masses.get(2, 0) <= 1.01)
    check("horizon masses in the predicted ranges (0.128-0.132, 1.00-1.01)", okm, f"{masses}")
    return dict(results=RESULTS, horizon_masses=masses)


def main():
    mode = sys.argv[1]
    if mode == "synthetic":
        out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
        res = synthetic(out)
    elif mode == "single":
        out = sys.argv[2]
        res = single(sys.argv[2:])
    elif mode == "three":
        out = sys.argv[2]
        res = three(out)
    else:
        raise SystemExit(__doc__)
    # results go to the run directory of nrpic-run when there is one, never into the run
    # directory that is being read
    dest = os.environ.get("NRPIC_RUN_DIR") or (
        out if mode == "synthetic" else os.path.dirname(os.path.normpath(out)))
    path = os.path.join(dest, f"test_nrread_{mode}.json")
    json.dump(res, open(path, "w"), indent=1, default=str)
    n_fail = sum(not r["ok"] for r in RESULTS)
    print(f"{len(RESULTS) - n_fail}/{len(RESULTS)} passed; {path}")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
