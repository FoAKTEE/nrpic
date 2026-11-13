"""Reduce the five star-cluster runs to the arrays of fig_clusters.py.

This is the only script of the cluster-sequence figure that reads the simulation
outputs and the analysis modules of the repository; the figure script reads
paper/data/clusters.npz alone. Five equilibrium star clusters of unit total mass,
10^4 stratified particles each, one-percent inward velocity kick:

- y_c = 0.900 and 0.819: static nest down to dx = M/2, 300 M;
- y_c = 0.605: adaptive mesh, 300 M in two job segments (0 to 150 M and 150 to 300 M)
  that append to the same history, horizon and snapshot files;
- y_c = 0.500: adaptive mesh, 120 M;
- y_c = 0.283: adaptive mesh, until the job's time limit (about 270 M).

Kept per run: every record of the central lapse (probe at the origin) and of the
particle number, removed rest mass; from every particle snapshot, the coordinate radii
about the origin that enclose 10, 20, ..., 90 percent of the rest mass of the
particles present (after removal at the lapse threshold has started, the percentiles
refer to the surviving rest mass), the number of particles present and their rest
mass; for the adaptive-mesh runs, the apparent-horizon mass against time. Also kept:
the lapse threshold of particle removal, read from each run's input file, and the
central lapse and isotropic mass-shell radii of the equilibrium model.

Both segments of y_c = 0.605 are used: the history and horizon files hold the records
of both (de-duplicated in time, the last record of a time wins), and the snapshot
numbers continue across the restart; snapshots are de-duplicated in time as well.

    python3 paper/scripts/make_data_clusters.py
"""
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
from common import H, read_horizon, read_nrpic_hst, read_snapshot, snapshot_files  # noqa: E402
from nrpic.st_cluster import STModel  # noqa: E402

ST = REPO / "runs" / "st"
RUNS = {"y0900": (0.900, ST / "yc0900_v4"), "y0819": (0.819, ST / "yc0819_v4"),
        "y0605": (0.605, ST / "yc0605_v5"), "y0500": (0.500, ST / "yc0500_v5"),
        "y0283": (0.283, ST / "yc0283_v5")}
QS = np.arange(1, 10) / 10.0
OUT = HERE.parent / "data" / "clusters.npz"


def alpha_exc(d):
    """Lapse threshold of particle removal from the run's input file."""
    for p in sorted(d.glob("*.athinput")):
        m = re.search(r"^\s*alpha_exc\s*=\s*([0-9.eE+-]+)", p.read_text(), re.M)
        if m:
            return float(m.group(1))
    raise RuntimeError(f"no alpha_exc in {d}")


def shells(files):
    """Snapshot times, mass-shell radii about the origin [n, 9], particles present,
    rest mass present; de-duplicated in time (the last file of a time wins)."""
    rows = {}
    for p in files:
        t, d, tag, _ = read_snapshot(p)
        n = len(tag)
        if n == 0:
            rows[t] = (np.full(len(QS), np.nan), 0, 0.0, np.full(len(QS), np.nan))
            continue
        m, x = d[:, 6], d[:, :3]
        r = np.sqrt((x ** 2).sum(1))
        o = np.argsort(r)
        F = np.cumsum(m[o]) / m.sum()
        # check only: the same radii about the rest-mass weighted centre
        c = (m[:, None] * x).sum(0) / m.sum()
        rc = np.sqrt(((x - c) ** 2).sum(1))
        oc = np.argsort(rc)
        Fc = np.cumsum(m[oc]) / m.sum()
        rows[t] = (np.interp(QS, F, r[o]), n, m.sum(), np.interp(QS, Fc, rc[oc]))
    T = np.array(sorted(rows))
    return (T, np.array([rows[t][0] for t in T]), np.array([rows[t][1] for t in T]),
            np.array([rows[t][2] for t in T]), np.array([rows[t][3] for t in T]))


def main():
    data = {"keys": np.array(list(RUNS)), "qs": QS}
    full = {}
    for key, (yc, d) in RUNS.items():
        h = read_nrpic_hst(str(d / "st.nrpic.hst"))
        files = snapshot_files(str(d), "st")
        T, R, N, Msum, Rc = shells(files)
        ah = read_horizon(str(d / "st.horizon_summary_0.txt"))
        mod = STModel(yc)
        data[f"{key}_yc"] = yc
        data[f"{key}_t"] = h[:, H["time"]]
        data[f"{key}_alpha"] = h[:, H["alpha_probe"]]
        data[f"{key}_np"] = h[:, H["np"]]
        data[f"{key}_m0"] = h[0, H["sum_m"]]
        data[f"{key}_m_exc"] = h[:, H["m_excised"]]
        data[f"{key}_snap_t"] = T
        data[f"{key}_r"] = R
        data[f"{key}_snap_n"] = N
        data[f"{key}_snap_m"] = Msum
        data[f"{key}_ah_t"], data[f"{key}_ah_M"] = ah[:, 0], ah[:, 1]
        data[f"{key}_alpha_exc"] = alpha_exc(d)
        data[f"{key}_eq_alpha"] = mod.alpha_c
        data[f"{key}_eq_r"] = np.asarray(mod.Finv(QS))
        full[key] = (h, T, R, N, Msum, Rc, ah, mod)
        t = h[:, 0]
        print(f"{key} {d.relative_to(REPO)}: {len(h)} history records t = {t[0]:.2f} .. "
              f"{t[-1]:.4f} (steps back in time: {int(np.sum(np.diff(t) <= 0))}); "
              f"{len(files)} snapshots, {len(T)} distinct times {T[0]:.1f} .. {T[-1]:.1f}; "
              f"{len(ah)} horizon rows; alpha_exc {data[f'{key}_alpha_exc']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    # spot checks against docs/TESTLOG.md
    print("spot checks (TESTLOG):")

    def at(t, y, tq):
        return y[np.argmin(np.abs(t - tq))]

    for key, (h, T, R, N, Msum, Rc, ah, mod) in full.items():
        t, a = h[:, H["time"]], h[:, H["alpha_probe"]]
        live = N > 0
        dev = np.nanmax(np.abs(R[live] - Rc[live]) / R[live])
        print(f"  {key}: alpha_c {a[0]:.4f} (equilibrium {mod.alpha_c:.4f}), range "
              f"{a.min():.4f} .. {a.max():.4f}, end {a[-1]:.4f}; N {N[0]} -> {N[-1]}; "
              f"removed rest mass {h[-1, H['m_excised']]:.4f} of {h[0, H['sum_m']]:.4f}")
        print(f"      r10 {R[0, 0]:.3f} -> {R[-1, 0]:.3f}, r50 {R[0, 4]:.3f} -> {R[-1, 4]:.3f}, "
              f"r90 {R[0, 8]:.3f} -> {R[-1, 8]:.3f}; equilibrium r10, r50, r90 "
              f"{mod.Finv(QS)[0]:.3f}, {mod.Finv(QS)[4]:.3f}, {mod.Finv(QS)[8]:.3f}; "
              f"largest relative difference of the radii about the centre of mass "
              f"{dev:.1e}")
        if len(ah):
            print(f"      first horizon t = {ah[0, 0]:.2f}, M = {ah[0, 1]:.4f}; last t = "
                  f"{ah[-1, 0]:.2f}, M = {ah[-1, 1]:.5f}; removal starts t = "
                  f"{t[np.argmax(h[:, H['np']] < h[0, H['np']])]:.2f}")
    h, T, R = full["y0900"][:3]
    print("  y0900 log: alpha_c 0.886 .. 0.892 (eq 0.8891); r10 5.66 -> 5.42, r90 13.96 -> 14.20")
    h, T, R = full["y0819"][:3]
    w = T >= 250
    print(f"  y0819: r10 range for t >= 250: {R[w, 0].min():.2f} .. {R[w, 0].max():.2f}; "
          "log: 2.5 .. 3.5 at the end (eq 3.13); alpha_c minima 0.7875 at 282 M")
    h, T, R, N, Msum, Rc, ah, mod = full["y0605"]
    t, a = h[:, 0], h[:, H["alpha_probe"]]
    print(f"  y0605: alpha_c at 52, 77, 90, 104, 128, 142 M: "
          + ", ".join(f"{at(t, a, x):.3f}" for x in (52, 77, 90, 104, 128, 142))
          + "; log 0.641, 0.616, 0.650, 0.590, 0.655, 0.534")
    print(f"         alpha_c at 160, 170, 180, 190 M: "
          + ", ".join(f"{at(t, a, x):.2f}" for x in (160, 170, 180, 190))
          + "; log 0.62, 0.53, 0.36, 0.17")
    print(f"         r50 at 0, 120, 150 M: "
          + ", ".join(f"{at(T, R[:, 4], x):.2f}" for x in (0, 120, 150))
          + "; log 2.84, 2.84, 2.29; r10 at 0: "
          + f"{R[0, 0]:.2f} (log 1.42)")
    print(f"         horizon mass at 195, 200, 210, 220, 240, 260, 280 M: "
          + ", ".join(f"{at(ah[:, 0], ah[:, 1], x):.4f}" for x in (195, 200, 210, 220, 240, 260, 280))
          + "; log 0.908, 0.953, 0.990, 0.9973, 0.9985, 0.9972, 0.9994")
    print(f"         particles at 297 M: {at(h[:, 0], h[:, H['np']], 297):.0f} (log 7)")
    h, T, R, N, Msum, Rc, ah, mod = full["y0500"]
    t, a = h[:, 0], h[:, H["alpha_probe"]]
    w = t <= 50
    print(f"  y0500: alpha_c for t <= 50 M {a[w].min():.3f} .. {a[w].max():.3f} (log 0.545 .. "
          f"0.556); at 70, 80, 90, 100, 110, 120 M: "
          + ", ".join(f"{at(t, a, x):.3f}" for x in (70, 80, 90, 100, 110, 120))
          + "; log 0.514, 0.536, 0.38, 0.23, 0.045, 0.016")
    print(f"         horizon mass at 106.3, 109.3, 114.3, 119 M: "
          + ", ".join(f"{at(ah[:, 0], ah[:, 1], x):.4f}" for x in (106.3, 109.3, 114.3, 119))
          + "; log 0.949, 0.992, 0.9992, 1.0000")
    h, T, R, N, Msum, Rc, ah, mod = full["y0283"]
    t, a = h[:, 0], h[:, H["alpha_probe"]]
    print(f"  y0283: alpha_c at 31, 60, 80, 100, 150, 200, 268 M: "
          + ", ".join(f"{at(t, a, x):.3f}" for x in (31, 60, 80, 100, 150, 200, 268))
          + "; log 0.388, 0.49, 0.76, 0.86, 0.94, 0.964, 0.976; minimum "
          + f"{a.min():.3f} at {t[np.argmin(a)]:.1f} M")
    print(f"         r50 {R[0, 4]:.2f} -> {at(T, R[:, 4], 268):.2f} at 268 M, "
          f"{R[-1, 4]:.2f} at {T[-1]:.1f} M (log 1.69 -> 47.6)")


if __name__ == "__main__":
    main()
