"""Reduce the cluster runs on the smoothing filter to the arrays of fig_filter.py.

This is the only script of the filter figure that reads the simulation outputs and the
analysis modules of the repository; the figure script reads paper/data/filter.npz
alone. All runs have 10^4 stratified particles, no velocity perturbation and the net
momentum removed. It keeps the central lapse against time (every second record):

- stable model y_c = 0.819, dx = M/2, 300 M: samples (seeds) 1, 2, 3 with four plain
  binomial passes and with four passes plus the compensation pass; sample 1 with
  zero and two plain passes and two passes plus compensation;
- model y_c = 0.5 past the binding-energy maximum, 200 M: sample 1 with four plain
  passes, samples 1, 2, 3 with four passes plus compensation.

The equilibrium value of the central lapse of the stable model is stored with them.

    python3 paper/scripts/make_data_filter.py
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
NMAX = 2000                           # at most this many records per history
RUNS = {                              # key: run directory
    "s1_p4": ST / "ctl" / "s1_nf4", "s2_p4": ST / "ctl" / "s2_nf4",
    "s3_p4": ST / "ctl" / "s3_nf4", "s1_p2": ST / "ctl" / "s1_nf2",
    "s1_p0": ST / "ctl" / "s1_nf0",
    "s1_c4": ST / "ctl" / "s1_nf4c", "s2_c4": ST / "ctl" / "s2_nf4c",
    "s3_c4": ST / "ctl" / "s3_nf4c", "s1_c2": ST / "ctl" / "s1_nf2c",
    "u_s1_p4": ST / "dir_yc0500_plain", "u_s1_c4": ST / "dir_yc0500_comp",
    "u_s2_c4": ST / "dir_yc0500_comp_s2", "u_s3_c4": ST / "dir_yc0500_comp_s3",
}
OUT = HERE.parent / "data" / "filter.npz"


def main():
    data = {"alpha_eq": ALPHA_EQ}
    full = {}
    for key, d in RUNS.items():
        h = read_nrpic_hst(str(d / "st.nrpic.hst"))
        t, a = h[:, H["time"]], h[:, H["alpha_probe"]]
        full[key] = (t, a)
        k = int(np.ceil(len(t) / NMAX))
        idx = np.unique(np.r_[np.arange(0, len(t), k), len(t) - 1])
        data[f"{key}_t"], data[f"{key}_alpha"] = t[idx], a[idx]
        print(f"{key:8s} {d.relative_to(REPO)}: {len(t)} records, t = {t[0]:g} .. {t[-1]:g}, "
              f"kept {len(idx)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    # spot checks against docs/TESTLOG.md, from the full histories
    print("spot checks (TESTLOG): rise of the central lapse above equilibrium within 130 M")
    log = {"s1_p4": "0.0273 at 116", "s2_p4": "peak 0.8383 at 121", "s3_p4": "peak 0.8369 at 120",
           "s1_p2": "0.0176 at 112", "s1_p0": "0.0044 at 89", "s1_c4": "0.0065",
           "s2_c4": "0.0084", "s3_c4": "0.0061", "s1_c2": "0.0061"}
    for key, ref in log.items():
        t, a = full[key]
        w = t <= 130.0
        i = np.argmax(a[w])
        print(f"  {key}: {a[w][i] - ALPHA_EQ:.4f} (peak {a[w][i]:.4f}) at t = {t[w][i]:.1f}"
              f"   log: {ref}")
    print("  y_c = 0.5, time at which the central lapse reaches 0.60, 0.70, 0.80, 0.85:")
    for key, ref in (("u_s1_p4", "19.5, 37.5, 59.2, 81.0"), ("u_s1_c4", "37.8, 64.0, 88.0, 110.8"),
                     ("u_s2_c4", "38.2, 67.5, 86.0, 109.8"), ("u_s3_c4", "41.5, 70.0, 91.5, 122.2")):
        t, a = full[key]
        hit = [t[np.nonzero(a >= v)[0][0]] for v in (0.60, 0.70, 0.80, 0.85)]
        print(f"  {key}: " + ", ".join(f"{x:.1f}" for x in hit) + f"   log: {ref}")


if __name__ == "__main__":
    main()
