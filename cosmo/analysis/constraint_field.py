"""What the Hamiltonian-constraint field of a random-field run looks like
(cosmo/TESTLOG.md, "the constraint field goes into the dumps"): for every dump of a run
with <particles> field_constraints = true, the constraint in units of 16 pi <E>, its
spectrum in shells, and least-squares fits against local fields built from the density
contrast.

    python3 constraint_field.py RUNDIR [--box 704]
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
import random_field as rf  # noqa: E402


def read(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        t = np.fromfile(f, dtype=np.float64, count=1)[0]
        n = np.fromfile(f, dtype=np.int64, count=3)
        nc = int(n[0]*n[1]*n[2])
        shape = (int(n[2]), int(n[1]), int(n[0]))
        out = {"t": float(t)}
        for key in ("E", "chi"):
            out[key] = np.fromfile(f, dtype=np.float32, count=nc).astype(np.float64) \
                .reshape(shape).transpose(2, 1, 0)
        if magic == b"NRFIELD2":
            for key in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[key] = np.fromfile(f, dtype=np.float64, count=nc).reshape(shape) \
                    .transpose(2, 1, 0)
    return out


def lap(f):
    return sum(np.roll(f, 1, a) + np.roll(f, -1, a) - 2.0*f for a in range(3))


def grad2(f):
    return sum((0.5*(np.roll(f, -1, a) - np.roll(f, 1, a)))**2 for a in range(3))


def main():
    run = sys.argv[1]
    box = 704.0
    if "--box" in sys.argv:
        box = float(sys.argv[sys.argv.index("--box") + 1])
    for path in sorted(glob.glob(os.path.join(run, "*.field.*.bin"))):
        d = read(path)
        if "H" not in d:
            continue
        a = (1.0 + 0.5*d["t"])**2
        n = d["E"].shape[0]
        delta = d["E"]/d["E"].mean() - 1.0
        h = d["H"]/(16.0*np.pi*d["E"].mean())
        print(f"\n{os.path.basename(path)}: t = {d['t']:.3f}, z = {1001/a - 1:.2f}, rms contrast "
              f"{delta.std():.3e}")
        print(f"   H/(16 pi <E>): mean {h.mean():+.3e}, rms {h.std():.3e}, max |.| "
              f"{np.abs(h).max():.3e}; Theta rms {d['Theta'].std():.2e} mean {d['Theta'].mean():+.2e}")
        k, p, nm = rf.measure_power(h - h.mean(), box, nbins=None)
        kd, pd, _ = rf.measure_power(delta, box, nbins=None)
        kf = 2.0*np.pi/box
        tot = (p*nm).sum()
        cum = np.cumsum(p*nm)/tot
        sel = [0, 1, 2, 3, 5, 8, 12, len(k) - 1]
        print("   share of the power of H below k/k_f = "
              + ", ".join(f"{k[i]/kf:.1f}: {cum[i]:.2f}" for i in sel if i < len(k)))
        print("   same for the contrast: "
              + ", ".join(f"{kd[i]/kf:.1f}: {(np.cumsum(pd*nm)/(pd*nm).sum())[i]:.2f}"
                          for i in sel if i < len(kd)))
        # least squares against local fields
        terms = {"delta": delta, "delta^2": delta**2 - (delta**2).mean(),
                 "lap delta": lap(delta), "|grad delta|^2": grad2(delta) - grad2(delta).mean(),
                 "lap delta^2": lap(delta**2), "Theta": d["Theta"] - d["Theta"].mean()}
        y = (h - h.mean()).ravel()
        for name, x in terms.items():
            x = x.ravel()
            c = float((x*y).sum()/(x*x).sum())
            r = float((x*y).sum()/np.sqrt((x*x).sum()*(y*y).sum()))
            print(f"   fit to {name:16s}: coefficient {c:+.3e}, correlation {r:+.3f}")
        A = np.stack([v.ravel() for v in terms.values()], axis=1)
        coef, res, _, _ = np.linalg.lstsq(A, y, rcond=None)
        fitted = A @ coef
        print("   joint fit: " + ", ".join(f"{nme} {c:+.2e}" for nme, c in zip(terms, coef))
              + f"; explained variance {1 - ((y - fitted)**2).sum()/(y*y).sum():.3f}")


if __name__ == "__main__":
    main()
