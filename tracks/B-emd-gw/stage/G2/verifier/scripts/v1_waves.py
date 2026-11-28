#!/usr/bin/env python3
"""V1: the linear-wave tests F (flat, k = 2 pi (1,1,1), L = 1) and X (standing tensor mode of
the matter era, k = 2 pi (1,1,0)/4, L = 4) recomputed from the raw dumps with my own exact
solutions.

  F: the forward combination W_ij = h^TT_ij(k) + i h'^TT_ij(k)/|k| (h' = -2 alpha A_ij) of the
     t = 0 dump, carried exactly by exp(-i |k| t).
  X: h = C1 j1(x)/x + C2 y1(x)/x, x = k (t + 2) (a = ((t+2)/2)^2, h'' + 4/(t+2) h' + k^2 h = 0),
     fitted to h and h' of the t = 0 dump per polarization (u = z, v = (1,-1,0)/sqrt 2,
     e+ = uu - vv, ex = uv + vu); errors of W = P + i P'/|k| at the last dump.
Errors: r = <W_ex, W>/<W_ex, W_ex>; amplitude |r| - 1, phase arg r (my sign convention).

    python3 v1_waves.py OUTDIR F:N=DIR ... X:N=DIR ...
"""
import glob
import json
import os
import sys

import numpy as np
from scipy.special import spherical_jn, spherical_yn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

G = ["z4c_gxx", "z4c_gxy", "z4c_gxz", "z4c_gyy", "z4c_gyz", "z4c_gzz"]
A = ["z4c_Axx", "z4c_Axy", "z4c_Axz", "z4c_Ayy", "z4c_Ayz", "z4c_Azz"]
IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def mode_tensor(d, names, n, sub_delta):
    """3x3 Fourier coefficient (normalised by Ntot) of the symmetric field at integer n."""
    M = np.zeros((3, 3), complex)
    for nm, (i, j) in zip(names, IDX):
        f = d[nm] - (1.0 if (sub_delta and i == j) else 0.0)
        Nz, Ny, Nx = f.shape
        # direct DFT of the one mode (exact, avoids a full FFT): sum f exp(-2 pi i n.x/N)
        ex = np.exp(-2j*np.pi*n[0]*np.arange(Nx)/Nx)
        ey = np.exp(-2j*np.pi*n[1]*np.arange(Ny)/Ny)
        ez = np.exp(-2j*np.pi*n[2]*np.arange(Nz)/Nz)
        c = np.einsum("kji,i,j,k->", f, ex, ey, ez)/f.size
        M[i, j] = M[j, i] = c
    return M


def tt(M, n):
    k = np.asarray(n, float)
    k /= np.linalg.norm(k)
    P = np.eye(3) - np.outer(k, k)
    return P @ M @ P - 0.5*P*np.trace(P @ M)


def measure(fn, n):
    d, h = vlib.read_mesh(fn, G + A + ["z4c_alpha"])
    hk = tt(mode_tensor(d, G, n, True), n)
    Ak = tt(mode_tensor(d, A, n, False), n)
    al = float(d["z4c_alpha"].mean())
    hfull = mode_tensor(d, G, n, True)
    nonTT = np.linalg.norm(hfull - hk)
    return h["time"], hk, -2.0*al*Ak, al, nonTT, h["box"]


def run_F(N, dirn):
    files = sorted(glob.glob(os.path.join(dirn, "bin", "*.z4c.*.bin")))
    n = (1, 1, 1)
    rows = []
    t0, h0, hd0, _, _, box = measure(files[0], n)
    L = box[0][1] - box[0][0]
    kk = 2*np.pi*np.sqrt(3.0)/L
    W0 = h0 + 1j*hd0/kk
    B0 = h0 - 1j*hd0/kk
    for fn in files:
        t, hk, hd, al, nonTT, _ = measure(fn, n)
        W = hk + 1j*hd/kk
        Wex = W0*np.exp(-1j*kk*(t - t0))
        r = np.vdot(Wex, W)/np.vdot(Wex, Wex)
        rows.append({"t": t, "amp_err": float(abs(r) - 1), "phase_err": float(np.angle(r)),
                     "nonTT_over_W": float(nonTT/np.linalg.norm(W)), "alpha": al})
    # polarization ratio in a fixed basis (e1 = (1,-1,0)/sqrt2, e2 = (1,1,-2)/sqrt6)
    return {"N": N, "L": L, "k": kk, "backward_over_forward_t0": float(np.linalg.norm(B0)/np.linalg.norm(W0)),
            "W0_norm": float(np.linalg.norm(W0)), "rows": rows, "last": rows[-1]}


def run_X(N, dirn):
    files = sorted(glob.glob(os.path.join(dirn, "bin", "*.z4c.*.bin")))
    n = (1, 1, 0)
    u = np.array([0, 0, 1.0])
    v = np.array([1, -1, 0])/np.sqrt(2)
    ep = np.outer(u, u) - np.outer(v, v)
    ex = np.outer(u, v) + np.outer(v, u)
    t0, h0, hd0, al0, _, box = measure(files[0], n)
    L = box[0][1] - box[0][0]
    kk = 2*np.pi*np.sqrt(2.0)/L
    pol0 = {nm: (0.5*np.sum(e*h0), 0.5*np.sum(e*hd0)) for nm, e in (("plus", ep), ("cross", ex))}

    def basis(t):
        x = kk*(t + 2.0)
        j, y = spherical_jn(1, x), spherical_yn(1, x)
        jd, yd = spherical_jn(1, x, derivative=True), spherical_yn(1, x, derivative=True)
        f = np.array([j/x, y/x])
        fd = kk*np.array([(jd*x - j)/x**2, (yd*x - y)/x**2])
        return f, fd
    f0, fd0 = basis(t0)
    Mx = np.array([f0, fd0])
    coef = {nm: np.linalg.solve(Mx, np.array([P0, Pd0])) for nm, (P0, Pd0) in pol0.items()}
    rows = []
    for fn in files:
        t, hk, hd, al, nonTT, _ = measure(fn, n)
        f, fd = basis(t)
        row = {"t": t, "a_code": al}
        for nm, e in (("plus", ep), ("cross", ex)):
            P, Pd = 0.5*np.sum(e*hk), 0.5*np.sum(e*hd)
            Pex, Pdex = f @ coef[nm], fd @ coef[nm]
            W, Wex = P + 1j*Pd/kk, Pex + 1j*Pdex/kk
            r = W/Wex
            row[nm + "_amp_err"] = float(abs(r) - 1)
            row[nm + "_phase_err"] = float(np.angle(r))
            row[nm + "_abs"] = float(abs(W))
        row["a_rel_err"] = float(al/((1 + t/2)**2) - 1)
        rows.append(row)
    return {"N": N, "L": L, "k": kk, "P0_over_Pd0": {nm: float(abs(p[0])/abs(p[1])) for nm, p in pol0.items()},
            "rows": rows, "last": rows[-1]}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {"F": [], "X": []}
    for arg in sys.argv[2:]:
        kind, rest = arg.split(":", 1)
        N, d = rest.split("=", 1)
        r = run_F(int(N), d) if kind == "F" else run_X(int(N), d)
        r["dir"] = d
        res[kind].append(r)
        last = r["last"]
        print(kind, N, {k: v for k, v in last.items()})
    json.dump(res, open(os.path.join(out, "v1_waves.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
