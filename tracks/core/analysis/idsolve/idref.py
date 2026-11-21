"""Independent reference solutions for the tests of the initial-data solver of the code.

Not a simulation code: each function solves, with numpy and scipy, the discrete problem
that tracks/core/interfaces/id_solver.md says the code solves (mode `stencil`), from the
same particle file, by another method (direct sparse factorisation on an isolated mesh,
Fourier transforms on the torus). Agreement to the tolerances of the iterations is the
statement that the code does what the document says.
"""
import os
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "cosmo", "ic"))


def cic_open(x, w, n, lo, hi):
    """Cloud-in-cell sum of the weights w per coordinate volume on n^3 cells between lo
    and hi (the particles and their clouds lie inside the mesh)."""
    h = (hi - lo)/n
    xi = (x - lo)/h - 0.5
    i0 = np.floor(xi).astype(np.int64)
    s = xi - i0
    out = np.zeros(n*n*n)
    for cx in (0, 1):
        wx = s[:, 0] if cx else 1.0 - s[:, 0]
        for cy in (0, 1):
            wy = s[:, 1] if cy else 1.0 - s[:, 1]
            for cz in (0, 1):
                wz = s[:, 2] if cz else 1.0 - s[:, 2]
                idx = ((i0[:, 0] + cx)*n + (i0[:, 1] + cy))*n + (i0[:, 2] + cz)
                out += np.bincount(idx, weights=w*wx*wy*wz, minlength=n*n*n)
    return out.reshape(n, n, n)/h**3


def robin_laplacian(n, lo, hi):
    """Seven-point Laplacian on n^3 cells between lo and hi acting on u = psi - 1, with
    the Robin closure of the code at the six faces: the ghost value is the value of the
    mirror cell times r_mirror/r_ghost (centre at the origin). Sparse matrix on the
    cells in the order [i, j, k] flattened (C order)."""
    h = (hi - lo)/n
    c = lo + (np.arange(n) + 0.5)*h
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    idx = np.arange(n**3).reshape(n, n, n)
    diag = np.full((n, n, n), -6.0)
    rows, cols, vals = [], [], []
    coords = (X, Y, Z)
    for ax in range(3):
        for side in (-1, 1):
            sl_in = [slice(None)]*3
            sl_nb = [slice(None)]*3
            if side < 0:
                sl_in[ax] = slice(1, n)
                sl_nb[ax] = slice(0, n - 1)
                edge = [slice(None)]*3
                edge[ax] = 0
                xg = lo - 0.5*h
            else:
                sl_in[ax] = slice(0, n - 1)
                sl_nb[ax] = slice(1, n)
                edge = [slice(None)]*3
                edge[ax] = n - 1
                xg = hi + 0.5*h
            rows.append(idx[tuple(sl_in)].ravel())
            cols.append(idx[tuple(sl_nb)].ravel())
            vals.append(np.ones(rows[-1].size))
            # boundary cells: ghost = q * own value
            e = tuple(edge)
            t2 = sum(coords[b][e]**2 for b in range(3) if b != ax)
            ri = np.sqrt(coords[ax][e]**2 + t2)
            rg = np.sqrt(xg*xg + t2)
            diag[e] += ri/rg
    rows.append(idx.ravel())
    cols.append(idx.ravel())
    vals.append(diag.ravel())
    L = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(n**3, n**3))
    return L/h**2


def solve_isolated(x, m, n, lo, hi, K=None, A2=None, psi0=None, tol=1.0e-13, maxit=30,
                   verbose=False):
    """psi on n^3 cells with lap_7 psi = -A2/(8 psi^7) + K^2 psi^5/12 - 2 pi Etilde/psi,
    Etilde the cloud-in-cell density of the particles at rest (x, m), Robin faces.
    Newton iteration with a sparse direct solve. Returns psi[i, j, k] and the history of
    the largest residual."""
    et = cic_open(x, m, n, lo, hi).ravel()
    k2 = np.zeros(n**3) if K is None else (np.asarray(K, float).ravel())**2
    a2 = np.zeros(n**3) if A2 is None else np.asarray(A2, float).ravel()
    L = robin_laplacian(n, lo, hi)
    u = np.zeros(n**3) if psi0 is None else np.asarray(psi0, float).ravel() - 1.0
    hist = []
    for it in range(maxit):
        psi = 1.0 + u
        f = L @ u + a2/(8.0*psi**7) - k2*psi**5/12.0 + 2.0*np.pi*et/psi
        hist.append(float(np.abs(f).max()))
        if verbose:
            print("  reference: it %d  max|F| = %.3e" % (it, hist[-1]))
        if hist[-1] < tol:
            break
        sig = 7.0*a2/(8.0*psi**8) + 5.0*k2*psi**4/12.0 + 2.0*np.pi*et/psi**2
        d = spla.spsolve((L - sp.diags(sig)).tocsc(), -f)
        u = u + d
    return (1.0 + u).reshape(n, n, n), hist


def solve_torus(x, m, n, box, hubble, symbol="spectral", tol=2.0e-11, maxit=60):
    """psi on the torus for particles at rest and K = -3 hubble, with cosmo/ic/cosmo_id.py
    (cloud in cell, no filter). symbol = "spectral": its Fourier Laplacian;
    "seven": the symbol of the seven-point Laplacian in its place. Returns the result
    dict of cosmo_id.solve. tol is its absolute tolerance on the largest residual of the
    scalar equation (terms of order one here; rounding of the transforms sets a floor
    near 1e-12 at 64^3)."""
    import cosmo_id
    tor = cosmo_id.Torus(n, box)
    if symbol == "seven":
        h = box/n
        tor.k2 = (4.0/h**2)*(np.sin(0.5*tor.k[0]*h)**2 + np.sin(0.5*tor.k[1]*h)**2
                             + np.sin(0.5*tor.k[2]*h)**2)
    K = np.full((n, n, n), -3.0*hubble)
    return cosmo_id.solve(tor, x, np.zeros_like(x), m, K, nfilter=0, compensate=False,
                          tol=tol, maxit=maxit)
