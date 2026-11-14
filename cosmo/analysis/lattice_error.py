"""Sampling error of the deposit of a displaced particle lattice, as a function of the
growth of the displacement (cosmo/PLAN.md, T1): a Gaussian random field with the cut-off
of the smaller box of Daverio, Dirian & Mitsou (shortest wave ten cells), Zel'dovich
displacements scaled by the growth factor D, deposited with the three clouds from
lattices of 2 and 3 particles per cell and direction, and from the lattice of 2 with
sub-particles interpolated between Lagrangian neighbours (the sheet of Abel, Hahn &
Kaehler: r^3 sub-particles per Lagrangian cell at trilinearly interpolated positions).
Reference: a lattice of 8 per cell and direction with Fourier-interpolated
displacements. Errors are relative to the mean density.

    python3 lattice_error.py [--n 32] [--figure]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
import cosmo_id as cid  # noqa: E402
import make_field as mf  # noqa: E402
import random_field as rf  # noqa: E402
import spectrum as sp  # noqa: E402


def lattice(tor, Fk, ppc):
    """Lattice points and displacements as arrays of shape (npd, npd, npd, 3)."""
    q, xi, jac, q1 = mf.lattice_fields(tor, Fk, ppc, stagger=(ppc % 2 == 1))
    npd = tor.n*ppc
    return q.reshape(npd, npd, npd, 3), xi.reshape(npd, npd, npd, 3)


def deposit(x, n, L, shape, chunk=4_000_000):
    out = np.zeros((n, n, n))
    w = np.ones(len(x))
    for i in range(0, len(x), chunk):
        out += cid.cic_deposit(np.mod(x[i:i + chunk], L), w[i:i + chunk], n, L, shape=shape)
    return out/out.mean()


def sheet_points(q, xi, D, r, L):
    """Sub-particles of the Lagrangian cells: r per direction, at trilinearly
    interpolated displacements."""
    npd = q.shape[0]
    hq = L/npd
    pts = []
    f = (np.arange(r) + 0.5)/r
    # each Lagrangian cell has its lower corner at a lattice point
    for a in f:
        for b in f:
            for c in f:
                d = np.zeros_like(xi)
                for (sa, wa) in ((0, 1 - a), (1, a)):
                    for (sb, wb) in ((0, 1 - b), (1, b)):
                        for (sc, wc) in ((0, 1 - c), (1, c)):
                            d += wa*wb*wc*np.roll(xi, (-sa, -sb, -sc), axis=(0, 1, 2))
                pts.append((q + np.array([a, b, c])*hq + D*d).reshape(-1, 3))
    return np.concatenate(pts)


def main():
    n = 32
    if "--n" in sys.argv:
        n = int(sys.argv[sys.argv.index("--n") + 1])
    cut = 40.0
    box = 4.0*n                    # 4 Mpc/h cells: the cut-off wave is ten cells long
    HC0 = (1.0/sp.HUBBLE_DISTANCE)*np.sqrt(1001.0)

    def pk(k):
        return sp.linear_power(k, 0.0, sp.PLANCK18)/1001.0**2

    delta = rf.gaussian_field(n, box, pk, 1, kcut=2*np.pi/cut, cut="sharp", zero_nyquist=True)
    L = box*HC0
    tor = cid.Torus(n, L)
    _, Fk = mf.spectral_fields(tor, delta, 1.0, 1.0)
    lat = {p: lattice(tor, Fk, p) for p in (1, 2, 3, 8)}
    h = L/n
    print(f"n = {n}, rms of the initial contrast {delta.std():.3e}, max {np.abs(delta).max():.3e}")
    res = {}
    for D in (10.0, 30.0, 91.0, 200.0, 330.0, 500.0):
        dmax = D*np.abs(delta).max()
        disp = D*np.abs(lat[2][1]).max()/h
        print(f"\nD = {D:g} (z = {1001/D - 1:.1f}): linear contrast max {dmax:.2f}, largest "
              f"displacement {disp:.2f} cells")
        for shape in ("cic", "tsc", "pcs"):
            qr, xr = lat[8]
            ref = deposit((qr + D*xr).reshape(-1, 3), n, L, shape)
            row = {}
            for name, pts in (("1 per cell", (lat[1][0] + D*lat[1][1]).reshape(-1, 3)),
                              ("2 per cell", (lat[2][0] + D*lat[2][1]).reshape(-1, 3)),
                              ("3 per cell", (lat[3][0] + D*lat[3][1]).reshape(-1, 3)),
                              ("1 + sheet 2", sheet_points(*lat[1], D, 2, L)),
                              ("1 + sheet 4", sheet_points(*lat[1], D, 4, L)),
                              ("2 + sheet 2", sheet_points(*lat[2], D, 2, L)),
                              ("2 + sheet 3", sheet_points(*lat[2], D, 3, L))):
                e = deposit(pts, n, L, shape) - ref
                row[name] = (float(np.sqrt((e*e).mean())), float(np.abs(e).max()))
            res[(D, shape)] = row
            print(f"  {shape}: rms (max) error of the density over the mean; reference "
                  f"contrast rms {ref.std():.3f}, max {ref.max() - 1:.2f}")
            print("     " + "; ".join(f"{k}: {v[0]:.1e} ({v[1]:.1e})" for k, v in row.items()))
    return res


if __name__ == "__main__":
    main()
