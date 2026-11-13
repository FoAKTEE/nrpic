"""Reduce the vacuum unit-mass puncture runs to the arrays of fig_horizon_check.py.

This is the only script of the horizon-check figure that reads the simulation outputs
and the analysis modules of the repository; the figure script reads
paper/data/horizon_check.npz alone. It keeps:

- the apparent-horizon mass reported by the finder of the host code against time
  (rows where it found a surface), with its rms expansion, for the cell spacing
  dx = M/4, M/8, M/16 at the puncture with the derivatives the finder stores, and for
  dx = M/8 with the derivatives taken from the interpolant of the metric (corrected);
- the Misner-Sharp horizon mass of every restart dump that holds a trapped surface
  (analysis/diag/slicemass.py: the outermost sphere with 2m/R = 1), with its two
  uncertainties (shell binning, spread of m over the sphere);
- the corrected finder on the t = 50 M dumps of the dx = M/8 and M/16 runs. These two
  numbers were obtained with a one-cycle restart on CPU and are not in any run
  directory; they are copied from the table "Further checks of the corrected finder"
  in docs/TESTLOG.md (entry "Horizon mass calibration: results").

    python3 paper/scripts/make_data_horizon_check.py
"""
import glob
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
import slicemass as sm  # noqa: E402

PUNC = REPO / "runs" / "puncture"
RUNS = {                 # key: (run directory, cell spacing at the puncture / M, finder)
    "dx4": (PUNC / "hcal" / "dx4", 1 / 4, "stored"),
    "dx8": (PUNC / "single_v3", 1 / 8, "stored"),
    "dx16": (PUNC / "hcal" / "dx16", 1 / 16, "stored"),
    "dx8c": (PUNC / "hcal" / "dx8_fixed", 1 / 8, "interpolant"),
}
# corrected finder (tolerance 1e-5, 16 angular points) on the t = 50 M dumps, CPU
CPU_CORRECTED = {"dx8": (50.0, 1.001338), "dx16": (50.0, 0.999738)}
OUT = HERE.parent / "data" / "horizon_check.npz"


def finder(d):
    """time, mass, rms expansion of the rows where the finder found a surface."""
    a = sm.read_finder(str(d / "punc.horizon_summary_0.txt"))
    a = a[np.isfinite(a[:, 1])]
    return a[:, 0], a[:, 1], a[:, 4]


def slice_masses(d):
    """[t, M_H, uncertainty from shells, uncertainty from the spread of m] of every
    restart dump with a trapped surface."""
    rows = []
    for p in sorted(glob.glob(str(d / "rst" / "punc.[0-9][0-9][0-9][0-9][0-9].rst"))):
        A = sm.analyse(sm.rst_open(p, strict=True))
        X = A["X"][sm.NPER2_H]
        if X is None or not np.isfinite(X["RH"]):
            continue
        rows.append([A["time"], X["RH"] / 2, A["dMH_shell"], A["dMH_spread"]])
    return np.array(rows).reshape(-1, 4)


def main():
    data = {}
    for key, (d, dx, kind) in RUNS.items():
        t, m, hrms = finder(d)
        data[f"{key}_t"], data[f"{key}_M"], data[f"{key}_hrms"] = t, m, hrms
        data[f"{key}_dx"] = dx
        data[f"{key}_slice"] = slice_masses(d)
        print(f"{key} ({kind} derivatives, dx = M/{1 / dx:.0f}): finder rows {len(t)}, "
              f"t = {t[0]:g} .. {t[-1]:g}")
        for t_, M_, e1, e2 in data[f"{key}_slice"]:
            j = np.argmin(np.abs(t - t_))
            print(f"   t = {t_:6.1f}: slice M_H = {M_:.6f} (+- {e1:.0e} shells, +- {e2:.0e} "
                  f"spread); finder at t = {t[j]:g}: {m[j]:.6f}, rms expansion {hrms[j]:.1e}")
    for key, (t, m) in CPU_CORRECTED.items():
        data[f"{key}_cpu"] = np.array([t, m])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    # spot checks against docs/TESTLOG.md
    def at(key, tq):
        t, m = data[f"{key}_t"], data[f"{key}_M"]
        return m[np.argmin(np.abs(t - tq))]
    print("spot checks (TESTLOG):")
    print(f"  original finder at t = 50 M: dx = M/4 {at('dx4', 50) - 1:+.3e} (log -6.5e-2), "
          f"M/8 {at('dx8', 50):.5f} (log 0.97711), M/16 {at('dx16', 50):.5f} (log 0.94055)")
    print(f"  corrected finder on the GPU at t = 5, 8, 10, 11.5 M: "
          + ", ".join(f"{at('dx8c', x):.6f}" for x in (5, 8, 10, 11.5))
          + " (log 0.999860, 1.000044, 1.000189, 1.000323)")
    s8, s16 = data["dx8_slice"], data["dx16_slice"]
    print(f"  slice mass at t = 50 M: M/8 {s8[s8[:, 0] == 50, 1]} (log 1.0015 to 1.0017), "
          f"M/16 {s16[s16[:, 0] == 50, 1]} (log 1.000014)")


if __name__ == "__main__":
    main()
