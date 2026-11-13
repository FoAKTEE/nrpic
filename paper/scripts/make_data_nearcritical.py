"""Reduce the three runs of the near-critical model y_c = 0.756 to the arrays of
fig_nearcritical.py.

This is the only script of the near-critical figure that reads the simulation outputs
and the analysis modules of the repository; the figure script reads
paper/data/nearcritical.npz alone. Model y_c = 0.756, next to the binding-energy
maximum, 10^4 stratified particles, four binomial filter passes plus the compensation
pass:

- plus: density raised by ten percent by a homologous compression, conformal factor
  solving the Hamiltonian constraint, adaptive mesh with the apparent-horizon finder,
  stopped after the collapse (about 160 M);
- minus: density reduced by ten percent by a homologous expansion, otherwise as plus,
  600 M;
- unpert: no perturbation, static mesh, 800 M.

Runs may still be in progress: the script takes whatever exists (history and snapshots
concatenated across restarts as in make_data_migration.py).

Kept per run: the central lapse (probe at the origin), the particle number and the
removed rest mass against time (thinned to at most NMAX records); from every particle
snapshot, the coordinate radii about the origin enclosing 10, 20, ..., 90 percent of the
rest mass present, and the rest mass present; the apparent-horizon mass against time
(empty when no horizon was found). Also kept: the central lapse and isotropic mass-shell
radii of the equilibrium model, and the range of the central lapse about which the
curve of the original paper's figure for this model oscillates, read by eye.

    python3 paper/scripts/make_data_nearcritical.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
from common import H, read_horizon  # noqa: E402
from make_data_clusters import QS, shells  # noqa: E402
from make_data_migration import complete_snapshots, extrema, history, thin  # noqa: E402
from nrpic.st_cluster import STModel  # noqa: E402

ST = REPO / "runs" / "st"
YC = 0.756
RUNS = {"plus": ST / "reconf_yc0756_hc", "minus": ST / "reconf_yc0756_hc_m",
        "unpert": ST / "yc0756_unpert"}
ORIGINAL_BAND = (0.74, 0.75)          # (kept for reference; not drawn)
# central lapse of the original's perturbed run, extrema read by eye from its rendered
# figure (t/M, alpha_c); reading accuracy about 10 M and 0.005. After 650 M the curve
# has no clear extrema; the last rows are values of the slowly falling curve.
ORIGINAL = np.array([[0, 0.748], [35, 0.755], [60, 0.745], [90, 0.763], [115, 0.738],
                     [140, 0.772], [165, 0.720], [195, 0.774], [220, 0.705],
                     [250, 0.777], [275, 0.696], [305, 0.770], [330, 0.710],
                     [360, 0.757], [395, 0.718], [430, 0.757], [460, 0.720],
                     [490, 0.754], [520, 0.722], [555, 0.764], [590, 0.737],
                     [650, 0.720], [800, 0.735]], dtype=float)
OUT = HERE.parent / "data" / "nearcritical.npz"


def main():
    mod = STModel(YC)
    data = {"keys": np.array(list(RUNS)), "yc": YC, "qs": QS, "alpha_eq": mod.alpha_c,
            "eq_r": np.asarray(mod.Finv(QS)), "original_band": np.array(ORIGINAL_BAND), "original": ORIGINAL}
    full = {}
    for key, d in RUNS.items():
        h, nback = history(d)
        t, a = h[:, H["time"]], h[:, H["alpha_probe"]]
        files = complete_snapshots(d, t[-1])
        T, R, N, Msum, Rc = shells(files)
        ah = read_horizon(str(d / "st.horizon_summary_0.txt"))
        data[f"{key}_t"], data[f"{key}_alpha"], data[f"{key}_np"], data[f"{key}_m_exc"] = \
            thin(t, a, h[:, H["np"]], h[:, H["m_excised"]])
        data[f"{key}_t_end"] = t[-1]
        data[f"{key}_m0"] = h[0, H["sum_m"]]
        data[f"{key}_snap_t"], data[f"{key}_r"] = T, R
        data[f"{key}_snap_n"], data[f"{key}_snap_m"] = N, Msum
        data[f"{key}_ah_t"], data[f"{key}_ah_M"] = ah[:, 0], ah[:, 1]
        full[key] = (h, T, R, N, Msum, Rc, ah)
        print(f"{key} {d.relative_to(REPO)}: {len(h)} history records t = {t[0]:g} .. "
              f"{t[-1]:g} ({nback} restarts back in time); {len(files)} complete "
              f"snapshots, {len(T)} distinct times {T[0]:g} .. {T[-1]:g}; {len(ah)} "
              f"horizon rows")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    print(f"summary (equilibrium alpha_c {mod.alpha_c:.4f}; r10, r50, r90 "
          f"{mod.Finv(QS)[0]:.3f}, {mod.Finv(QS)[4]:.3f}, {mod.Finv(QS)[8]:.3f}):")
    for key, (h, T, R, N, Msum, Rc, ah) in full.items():
        t, a, n = h[:, H["time"]], h[:, H["alpha_probe"]], h[:, H["np"]]
        print(f"  {key}: alpha_c start {a[0]:.4f}, range {a.min():.4f} at {t[np.argmin(a)]:.1f}"
              f" M .. {a.max():.4f} at {t[np.argmax(a)]:.1f} M, end {a[-1]:.4f} at "
              f"{t[-1]:.1f} M; mean over the run {a.mean():.4f}")
        ex = extrema(t, a, smooth=5.0, swing=0.01)
        if ex:
            print("      extrema: " + ", ".join(f"{k} {x:.3f} at {y:.0f}" for k, y, x in ex))
        lost = n < n[0]
        print(f"      particles {n[0]:.0f} -> {n[-1]:.0f}"
              + (f"; removal from t = {t[np.argmax(lost)]:.2f} M, removed rest mass "
                 f"{h[-1, H['m_excised']]:.4f} of {h[0, H['sum_m']]:.4f}" if lost.any() else "")
              + f"; escaped {h[-1, H['n_escaped']]:.0f}")
        live = Msum >= 0.5 * Msum[0]
        for j, q in ((0, 10), (8, 90)):
            r = R[live, j]
            print(f"      r{q}: start {R[0, j]:.3f}, range {r.min():.3f} at "
                  f"{T[live][np.argmin(r)]:.0f} M .. {r.max():.3f} at "
                  f"{T[live][np.argmax(r)]:.0f} M (while half the rest mass remains, "
                  f"to {T[live][-1]:.0f} M)")
        if len(ah):
            print(f"      first apparent horizon t = {ah[0, 0]:.3f} M, mass {ah[0, 1]:.4f}; "
                  f"last t = {ah[-1, 0]:.2f} M, mass {ah[-1, 1]:.5f}")

    print("spot checks (TESTLOG):")

    def at(t, y, tq):
        return y[np.argmin(np.abs(t - tq))]

    h = full["plus"][0]
    t, a = h[:, H["time"]], h[:, H["alpha_probe"]]
    print("  plus: alpha_c at 0, 5, 10, 20, 30, 40, 50, 60, 80, 100, 120 M: "
          + ", ".join(f"{at(t, a, x):.4f}" for x in (0, 5, 10, 20, 30, 40, 50, 60, 80, 100, 120))
          + "; log 0.7488, 0.7448, 0.7480, 0.7466, 0.7376, 0.7351, 0.7213, 0.7124, "
          "0.6857, 0.6295, 0.5761")
    ah = full["plus"][6]
    print(f"        first horizon {ah[0, 0]:.1f} M, mass {ah[0, 1]:.3f}; log 147.2 M, 0.990; "
          f"removal from {t[np.argmax(h[:, H['np']] < h[0, H['np']])]:.1f} M (log 148.8); "
          f"particles at the end {h[-1, H['np']]:.0f} (log 0)")
    h, T, R = full["minus"][:3]
    t, a = h[:, H["time"]], h[:, H["alpha_probe"]]
    print("  minus: alpha_c at 0, 100, 160, 251, 400 M: "
          + ", ".join(f"{at(t, a, x):.4f}" for x in (0, 100, 160, 251, 400))
          + "; log 0.7554, 0.811, 0.819, 0.728, 0.827")
    print(f"         r90 {R[:, 8].min():.2f} .. {R[:, 8].max():.2f} (start {R[0, 8]:.2f}), "
          f"r10 {R[:, 0].min():.2f} .. {R[:, 0].max():.2f} (start {R[0, 0]:.2f}); log 6 .. 9 "
          "(6.4), 1.8 .. 3.8 (2.4)")


if __name__ == "__main__":
    main()
