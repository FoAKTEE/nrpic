"""Reduce the six test particles around an evolved puncture to the arrays of
fig_tracers.py.

This is the only script of the tracer figure that reads the simulation outputs and the
analysis modules of the repository; the figure script reads paper/data/tracers.npz alone.
It runs the tracer analysis (analysis/diag/tracers_exact.py, which reads the particle
records and the restart dumps of the run) in a temporary directory, so that its own
diagnostic figure is discarded, and keeps:

- radial infall (tag 5) and plunge (tag 4): proper time tau, areal radius R, the exact
  Schwarzschild geodesic of unit mass from the same initial data, and, for the plunge,
  the relative difference to the geodesic of the Misner-Sharp mass of the slice started
  from the particle's own state at t = 50 M;
- circular orbits (tags 0-3): the mass that makes each particle's radial acceleration
  geodesic, against coordinate time;
- restart dumps: the Misner-Sharp mass of the slice (median and percentiles over the
  shell 2.5 M < R < 16 M and over 6 M < R < 12 M, coordinate radius r > 1 M).

    python3 paper/scripts/make_data_tracers.py
"""
import contextlib
import io
import runpy
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
DIAG = REPO / "analysis" / "diag"
RUN = REPO / "runs" / "puncture" / "single_v3"
OUT = HERE.parent / "data" / "tracers.npz"
CIRC, PLUNGE, INFALL = (0, 1, 2, 3), 4, 5
SHELLS = {"wide": (2.5, 16.0), "orbit": (6.0, 12.0)}


def run_analysis():
    """Globals of tracers_exact.py after a full run on RUN; its printed report is
    returned as text."""
    sys.path.insert(0, str(DIAG))
    sys.path.insert(0, str(REPO / "python"))
    argv = sys.argv
    with tempfile.TemporaryDirectory() as tmp:
        sys.argv = [str(DIAG / "tracers_exact.py"), str(RUN), "--out", str(Path(tmp) / "x")]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                g = runpy.run_path(str(DIAG / "tracers_exact.py"))
        finally:
            sys.argv = argv
    return g, buf.getvalue()


def shell_stats(h, lo, hi):
    s = (h["R"] > lo) & (h["R"] < hi) & (h["r"] > 1.0)
    return np.percentile(h["m"][s], [50, 16, 84, 0, 100])


def main():
    g, report = run_analysis()
    Q, sep, dumps = g["Q"], g["sep"], g["dumps"]
    first_cross = g["first_cross"]
    data = {}
    for name, k in (("infall", INFALL), ("plunge", PLUNGE)):
        q = Q[k]
        data[f"{name}_tau"] = q["tau"]
        data[f"{name}_R"] = q["R"]
        data[f"{name}_Rex"] = q["Rex"]
        data[f"{name}_t"] = q["t"]
        data[f"{name}_tau_hor"] = first_cross(q["tau"], q["Rex"], 2.0)
    s = sep[PLUNGE]
    data["plunge_slice_tau"] = s["tau"]
    data["plunge_slice_res"] = s["m(t)"]
    data["slice_t0"] = 50.0
    for k in CIRC:
        data[f"circ{k}_t"] = Q[k]["Meff_t"]
        data[f"circ{k}_Meff"] = Q[k]["Meff"]
        data[f"circ{k}_R0"] = g["EX"][k]["R0"]
    data["dump_t"] = np.array([h["time"] for h in dumps])
    for key, (lo, hi) in SHELLS.items():
        data[f"dump_m_{key}"] = np.array([shell_stats(h, lo, hi) for h in dumps])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.2f} MB")

    # spot checks against docs/results_tracers.md
    for name in ("infall", "plunge"):
        res = data[f"{name}_R"] / data[f"{name}_Rex"] - 1
        out = data[f"{name}_Rex"] > 2.2
        print(f"{name}: max |R/R_exact - 1| for R_exact > 2.2 M: {np.abs(res[out]).max():.2e}; "
              f"tau at R_exact = 2M: {data[f'{name}_tau_hor']:.2f}")
    print("Misner-Sharp m - 1, median over 2.5 < R < 16:",
          ", ".join(f"t={t:.0f}: {m - 1:+.2e}" for t, m in zip(data["dump_t"],
                                                               data["dump_m_wide"][:, 0])))
    for k in CIRC:
        j = np.argmin(np.abs(data[f"circ{k}_t"] - 150.0))
        w = data[f"circ{k}_t"] >= 150.0
        print(f"circular tag {k}: M_eff - 1 at t = 150: {data[f'circ{k}_Meff'][j] - 1:+.2e}; "
              f"mean over t >= 150: {data[f'circ{k}_Meff'][w].mean() - 1:+.2e}")
    for line in report.splitlines():
        if "t = 150.0: M_eff" in line:
            print("  analysis report:", line.strip())


if __name__ == "__main__":
    main()
