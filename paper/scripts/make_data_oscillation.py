"""Reduce the long runs of the stable cluster to the arrays of fig_oscillation.py.

This is the only script of the oscillation figure that reads the simulation outputs and
the analysis modules of the repository; the figure script reads
paper/data/oscillation.npz alone. Stable model y_c = 0.819, 10^4 stratified particles,
dx = M/2, four binomial filter passes plus the compensation pass. It keeps the central
lapse against time for:

- base: sample 1, no perturbation, net momentum removed, 0 to 300 M, continued by a
  restart to 600 M (and to 1200 M once that continuation exists: it is appended
  automatically when its history file is present);
- samples 2 and 3 of the same setup, 300 M;
- a one-percent inward velocity kick, sample 1, with 10^4 and with 10^3 particles,
  300 M;
- controls of the base run, as differences from it on its own record times (records
  of the half-step run interpolated linearly): half the time step, constraint damping
  kappa_1 = 0.1 and 0 (base 0.02), parabolic relaxation of the Hamiltonian constraint,
  and a compensation pass that cancels the width of the cloud as well (the control's
  own central lapse on the same times is kept too).

Histories are thinned to at most NMAX records.

    python3 paper/scripts/make_data_oscillation.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
from common import H, read_nrpic_hst  # noqa: E402

ST = REPO / "runs" / "st"
ALPHA_EQ = 0.80939                    # central lapse of the equilibrium y_c = 0.819
NMAX = 2000
BASE = [ST / "ctl" / "s1_nf4c", ST / "osc" / "long", ST / "osc" / "long2"]
RUNS = {"s2": ST / "ctl" / "s2_nf4c", "s3": ST / "ctl" / "s3_nf4c",
        "kick_n4": ST / "yc0819_v4", "kick_n3": ST / "yc0819_n1e3_v4"}
CONTROLS = {"dt2": ST / "osc" / "dt2", "k1_0p1": ST / "osc" / "k1_0p1",
            "k1_0": ST / "osc" / "k1_0", "ch": ST / "osc" / "ch0p05",
            "ccloud": ST / "osc" / "ccloud"}
OUT = HERE.parent / "data" / "oscillation.npz"


def history(d):
    h = read_nrpic_hst(str(d / "st.nrpic.hst"))
    return h[:, H["time"]], h[:, H["alpha_probe"]]


def thin(t, *ys):
    k = int(np.ceil(len(t) / NMAX))
    idx = np.unique(np.r_[np.arange(0, len(t), k), len(t) - 1])
    return (t[idx],) + tuple(y[idx] for y in ys)


def main():
    data = {"alpha_eq": ALPHA_EQ}
    # base run and its continuations (each starts after the end of the previous one)
    tb, ab, parts = np.zeros(0), np.zeros(0), []
    for d in BASE:
        if not (d / "st.nrpic.hst").exists():
            print(f"base: {d.relative_to(REPO)} has no history yet, not used")
            continue
        t, a = history(d)
        w = t > (tb[-1] if len(tb) else -np.inf)
        tb, ab = np.r_[tb, t[w]], np.r_[ab, a[w]]
        parts.append(t[w][-1])
        print(f"base: {d.relative_to(REPO)} t = {t[w][0]:g} .. {t[w][-1]:g}")
    data["base_t"], data["base_alpha"] = thin(tb, ab)
    data["base_t_end"] = tb[-1]
    full = {"base": (tb, ab)}
    for key, d in RUNS.items():
        t, a = history(d)
        full[key] = (t, a)
        data[f"{key}_t"], data[f"{key}_alpha"] = thin(t, a)
        print(f"{key}: {d.relative_to(REPO)} t = {t[0]:g} .. {t[-1]:g}")
    t0, a0 = full["base"]
    w0 = t0 <= 300.0 + 1e-9
    t0, a0 = t0[w0], a0[w0]
    for key, d in CONTROLS.items():
        t, a = history(d)
        ac = np.interp(t0, t, a)
        diff = ac - a0
        data[f"ctl_{key}_t"], data[f"ctl_{key}_diff"], data[f"ctl_{key}_alpha"] = \
            thin(t0, diff, ac)
        print(f"control {key}: {d.relative_to(REPO)} t = {t[0]:g} .. {t[-1]:g}, "
              f"largest |difference| {np.abs(diff).max():.1e} at t = {t0[np.argmax(np.abs(diff))]:.0f}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    # spot checks against docs/TESTLOG.md
    print("spot checks (TESTLOG):")
    t, a = full["base"]
    for tq, ref in ((359, "-0.0065"), (392, "+0.0126"), (495, "-0.0262"), (564, "-0.0249")):
        w = np.abs(t - tq) < 6
        i = np.argmax(np.abs(a[w] - ALPHA_EQ))
        print(f"  base extremum near t = {tq} M: {a[w][i] - ALPHA_EQ:+.4f} at {t[w][i]:.1f}   log: {ref}")
    for key, tq, ref in (("s2", 277, "0.7924"), ("s3", 217, "0.8033")):
        t, a = full[key]
        w = np.abs(t - tq) < 8
        print(f"  {key} minimum near t = {tq} M: {a[w].min():.4f} at {t[w][np.argmin(a[w])]:.1f}"
              f"   log: {ref}")
    for key, tq, ref in (("k1_0p1", 280, "-0.0111 against -0.0108"),
                         ("dt2", 281, "-0.0104 against -0.0108"),
                         ("k1_0", 280, "-0.0107")):
        t, a = history(CONTROLS[key])
        w = np.abs(t - tq) < 6
        print(f"  {key} last minimum: {a[w].min() - ALPHA_EQ:+.4f} at {t[w][np.argmin(a[w])]:.1f}"
              f"   log: {ref}")


if __name__ == "__main__":
    main()
