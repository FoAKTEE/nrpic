"""Reduce the long run of the unperturbed model y_c = 0.5 to the arrays of fig_migration.py.

This is the only script of the migration figure that reads the simulation outputs and
the analysis modules of the repository; the figure script reads paper/data/migration.npz
alone. Model y_c = 0.5, past the binding-energy maximum, 10^4 stratified particles, no
perturbation, static mesh, four binomial filter passes plus the compensation pass,
evolved in a chain of job segments to 2500 M.

The run may still be in progress: the script takes whatever exists. The history file
is appended by every segment; it is concatenated without duplicated times (a segment
restarted from an earlier checkpoint supersedes every record of the previous segment
from its start time on). Snapshot files that are still being written, or that lie past
the last history record (left by an abandoned segment), are skipped.

Kept: the central lapse (probe at the origin) and the particle number against time
(thinned to at most NMAX records); from every particle snapshot, the coordinate radii
about the origin enclosing 10, 20, ..., 90 percent of the rest mass present; the central
lapse and isotropic mass-shell radii of the equilibrium model; and the extrema of the
central lapse read by eye from the migration figure of the original paper (2 x 10^6
particles), with the time and lapse ranges over which each was read.

    python3 paper/scripts/make_data_migration.py
"""
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
from common import H, read_nrpic_hst, snapshot_files  # noqa: E402
from make_data_clusters import QS, shells  # noqa: E402
from nrpic.st_cluster import STModel  # noqa: E402

RUN = REPO / "runs" / "st" / "migration_yc0500_v4"
YC = 0.5
NMAX = 5000
SNAP_DT = 2.0                         # snapshot interval of the run
# original's migration figure, read by eye from the rendered figure: t, t_lo, t_hi,
# alpha_c, alpha_lo, alpha_hi (the first maximum is a plateau from about 200 to 320 M;
# around the first minimum the curve oscillates between 0.55 and 0.63 from 440 to 520 M,
# lowest near 490 M; the second minimum is flat from 830 to 880 M)
ORIGINAL = np.array([[0.0, 0.0, 0.0, 0.56, 0.56, 0.56],
                     [260.0, 200.0, 320.0, 0.905, 0.905, 0.905],
                     [490.0, 440.0, 520.0, 0.55, 0.55, 0.63],
                     [670.0, 670.0, 670.0, 0.90, 0.90, 0.90],
                     [850.0, 830.0, 880.0, 0.765, 0.765, 0.765],
                     [1040.0, 1040.0, 1040.0, 0.865, 0.865, 0.865],
                     [1160.0, 1160.0, 1160.0, 0.78, 0.78, 0.78],
                     [1320.0, 1320.0, 1320.0, 0.865, 0.865, 0.865],
                     [1450.0, 1450.0, 1450.0, 0.80, 0.80, 0.80],
                     [1600.0, 1600.0, 1600.0, 0.85, 0.85, 0.85]])
OUT = HERE.parent / "data" / "migration.npz"


def history(d):
    """History of a chained run without duplicated times. read_nrpic_hst keeps the last
    record of each time; a segment restarted from an earlier checkpoint also supersedes
    the records of the previous segment after its start time whose times it does not
    repeat, and those are dropped here. Returns the array and the number of restarts
    that went back in time."""
    p = d / "st.nrpic.hst"
    t_raw = np.array([float(l.split()[0]) for l in open(p)
                      if l.strip() and not l.startswith("#")])
    later = np.r_[np.minimum.accumulate(t_raw[::-1])[::-1][1:], np.inf]
    keep = t_raw < later                # no later record at this time or before it
    h = read_nrpic_hst(str(p))
    return h[np.isin(h[:, H["time"]], t_raw[keep])], int(np.sum(np.diff(t_raw) <= 0))


def complete_snapshots(d, t_last):
    """Snapshot files that are completely written (particle count of the header against
    the file size) and not later than the last history record."""
    out = []
    for p in snapshot_files(str(d), "st"):
        with open(p, "rb") as f:
            head = f.read(32)
        if len(head) < 32:
            continue
        t, = struct.unpack("d", head[8:16])
        n, = struct.unpack("q", head[16:24])
        if Path(p).stat().st_size >= 32 + 64 * n and t <= t_last + SNAP_DT:
            out.append(p)
    return out


def thin(t, *ys, nmax=NMAX):
    k = int(np.ceil(len(t) / nmax))
    idx = np.unique(np.r_[np.arange(0, len(t), k), len(t) - 1])
    return (t[idx],) + tuple(y[idx] for y in ys)


def extrema(t, a, smooth=10.0, swing=0.02):
    """Extrema of the lapse: peaks and troughs of its running mean over `smooth` M with
    a prominence of at least `swing`, each moved to the extreme record within one
    smoothing width. Returns [(kind, t, alpha)] in time order."""
    from scipy.signal import find_peaks
    k = max(1, int(round(smooth / np.median(np.diff(t)))))
    s = np.convolve(a, np.ones(k) / k, mode="same")
    s[:k], s[-k:] = a[:k], a[-k:]       # no zero padding at the ends
    out = []
    for kind, sign in (("max", 1.0), ("min", -1.0)):
        for j in find_peaks(sign * s, prominence=swing)[0]:
            w = np.where(np.abs(t - t[j]) <= smooth)[0]
            r = w[np.argmax(sign * a[w])]
            out.append((kind, t[r], a[r]))
    return sorted(out, key=lambda e: e[1])


def main():
    h, nback = history(RUN)
    t, a, n = h[:, H["time"]], h[:, H["alpha_probe"]], h[:, H["np"]]
    files = complete_snapshots(RUN, t[-1])
    T, R, N, Msum, Rc = shells(files)
    mod = STModel(YC)
    data = {"yc": YC, "qs": QS, "alpha_eq": mod.alpha_c, "eq_r": np.asarray(mod.Finv(QS)),
            "t_end": t[-1], "n0": n[0], "m0": h[0, H["sum_m"]],
            "n_end": n[-1], "n_escaped": h[-1, H["n_escaped"]],
            "n_excised": h[-1, H["n_excised"]], "m_escaped": h[-1, H["m_escaped"]],
            "snap_t": T, "r": R, "snap_n": N, "snap_m": Msum, "original": ORIGINAL}
    data["t"], data["alpha"], data["np"] = thin(t, a, n)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{RUN.relative_to(REPO)}: {len(h)} history records t = {t[0]:g} .. {t[-1]:g} "
          f"({nback} restarts back in time); {len(files)} complete snapshots, {len(T)} "
          f"distinct times {T[0]:g} .. {T[-1]:g}")
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    print("summary:")
    print(f"  alpha_c start {a[0]:.4f} (equilibrium {mod.alpha_c:.4f}); range {a.min():.4f} "
          f"at {t[np.argmin(a)]:.1f} M .. {a.max():.4f} at {t[np.argmax(a)]:.1f} M; end "
          f"{a[-1]:.4f}")
    print("  extrema: " + ", ".join(f"{k} {x:.3f} at {y:.1f}" for k, y, x in extrema(t, a)))
    print(f"  particles {n[0]:.0f} -> {n[-1]:.0f}; escaped {h[-1, H['n_escaped']]:.0f} "
          f"(rest mass {h[-1, H['m_escaped']]:.2e} of {h[0, H['sum_m']]:.4f}), excised "
          f"{h[-1, H['n_excised']]:.0f}")
    for j, q in ((0, 10), (4, 50), (8, 90)):
        print(f"  r{q}: start {R[0, j]:.3f} (equilibrium {mod.Finv(QS)[j]:.3f}), range "
              f"{R[:, j].min():.3f} at {T[np.argmin(R[:, j])]:.0f} M .. {R[:, j].max():.3f} "
              f"at {T[np.argmax(R[:, j])]:.0f} M, end {R[-1, j]:.3f}")
    live = N > 0
    print(f"  largest relative difference of the radii about the centre of mass: "
          f"{np.nanmax(np.abs(R[live] - Rc[live]) / R[live]):.1e}")

    print("spot checks (TESTLOG, first 913 M; original read from its figure):")
    print(f"  start: {a[0]:.4f}   log 0.552; original 0.56")
    for kind, lo, hi, log, orig in (
            ("max", 150, 400, "0.913 at 228 M", "0.905, 200 .. 320 M"),
            ("min", 380, 600, "0.541 at 437 M (corrected)", "0.55 .. 0.63, 440 .. 520 M"),
            ("max", 580, 760, "0.894 at 631 M (corrected)", "0.90 at 670 M"),
            ("min", 740, 900, "0.753 at 783 M (corrected)", "0.765, 830 .. 880 M")):
        w = (t >= lo) & (t <= hi)
        if w.any():
            i = np.argmax(a[w]) if kind == "max" else np.argmin(a[w])
            print(f"  {kind} in {lo} .. {hi} M: {a[w][i]:.4f} at {t[w][i]:.1f} M   log "
                  f"{log}; original {orig}")


if __name__ == "__main__":
    main()
