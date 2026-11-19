"""Finite-difference constraint residuals of the Szekeres slice on a Cartesian mesh.

Conformally flat slice, gamma_ij = psi^4 delta_ij, mixed K^i_j (as `expball/expball/mesh.py`,
whose stencils D1, D2 and the residual forms are used here without spherical symmetry):

    H   = -8 psi^-5 lap(psi) + K^2 - K^i_j K^j_i - 16 pi rho
    M_i = d_j K^j_i + 6 K^l_i d_l ln psi - 2 K d_i ln psi - d_i K

Cell-centred grid of [-L, L]^3 with N cells per side (x_i = -L + (i + 1/2) h, as AthenaK).
"""

import math

import numpy as np

__all__ = ["D1", "D2", "residuals", "plane_fields"]

D1 = {2: (-0.5, 0.0, 0.5),
      4: (1 / 12, -2 / 3, 0.0, 2 / 3, -1 / 12),
      6: (-1 / 60, 3 / 20, -3 / 4, 0.0, 3 / 4, -3 / 20, 1 / 60)}
D2 = {2: (1.0, -2.0, 1.0),
      4: (-1 / 12, 4 / 3, -5 / 2, 4 / 3, -1 / 12),
      6: (1 / 90, -3 / 20, 3 / 2, -49 / 18, 3 / 2, -3 / 20, 1 / 90)}


def _apply(f, axis, coeffs, gpad):
    g = len(coeffs) // 2
    out = 0.0
    for k, c in enumerate(coeffs):
        if c == 0.0:
            continue
        off = k - g
        sl = [slice(gpad, s - gpad) for s in f.shape]
        sl[axis] = slice(gpad + off, f.shape[axis] - gpad + off)
        out = out + c * f[tuple(sl)]
    return out


def _interior(f, gpad):
    return f[tuple(slice(gpad, s - gpad) for s in f.shape)]


def residuals(cm, N, L, orders=(2, 4), regions=None, slab=8, norm=1.0, plane_axis=None,
              slab_range=None):
    """Hamiltonian and momentum residuals of the slice of ConformalMap `cm` on the cell-centred
    mesh of [-L, L]^3, for each finite-difference order. regions: dict name -> callable(r)
    -> mask on the shell label r. Returns {order: {region: norms}} (and with plane_axis=k
    the residual maps in the plane of cells nearest to x_k = 0; only k = 1 is filled).
    slab_range=(i0, i1) restricts the work to the x-index range [i0, i1) (for parallel
    callers that sum the partial results)."""
    h = 2.0 * L / N
    gpad = max(orders) // 2
    c = -L + (np.arange(-gpad, N + gpad) + 0.5) * h
    regions = regions or {"all": lambda r: np.ones_like(r, dtype=bool)}
    acc = {p: {k: dict(H1=0.0, H2=0.0, Hinf=0.0, M1=0.0, M2=0.0, Minf=0.0, n=0) for k in regions}
           for p in orders}
    mid = N // 2 - 1 if N % 2 == 0 else N // 2         # a plane next to x_k = 0
    planes = {p: (np.zeros((N, N)), np.zeros((N, N))) for p in orders}
    lo, hi = slab_range or (0, N)
    for i0 in range(lo, hi, slab):
        i1 = min(hi, i0 + slab)
        xs = c[i0:i1 + 2 * gpad]
        X, Y, Z = np.meshgrid(xs, c, c, indexing="ij")
        pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
        f = cm.fields(pts)
        shp = X.shape
        psi = f["psi"].reshape(shp)
        rho = f["rho"].reshape(shp)
        rlab = f["r"].reshape(shp)
        Km = {key: val.reshape(shp) for key, val in cm.kmix(f).items()}
        trK = Km[0, 0] + Km[1, 1] + Km[2, 2]
        lnpsi = np.log(psi)
        ri = _interior(rlab, gpad)
        for p in orders:
            lap = sum(_apply(psi, a, D2[p], gpad) for a in range(3)) / h ** 2
            KK = sum(_interior(Km[i, j] * Km[j, i], gpad) for i in range(3) for j in range(3))
            Hr = (-8.0 * _interior(psi, gpad) ** -5 * lap + _interior(trK, gpad) ** 2 - KK
                  - 16.0 * math.pi * _interior(rho, gpad)) / norm
            dl = [_apply(lnpsi, a, D1[p], gpad) / h for a in range(3)]
            trKi = _interior(trK, gpad)
            Mr = []
            for i in range(3):
                s = sum(_apply(Km[j, i], j, D1[p], gpad) for j in range(3)) / h
                s = s + 6.0 * sum(_interior(Km[l, i], gpad) * dl[l] for l in range(3))
                s = s - 2.0 * trKi * dl[i] - _apply(trK, i, D1[p], gpad) / h
                Mr.append(s / norm)
            Mabs = np.sqrt(Mr[0] ** 2 + Mr[1] ** 2 + Mr[2] ** 2)
            for name, fn in regions.items():
                msk = fn(ri)
                a = acc[p][name]
                if np.any(msk):
                    hv = np.abs(Hr[msk])
                    mv = Mabs[msk]
                    a["H1"] += hv.sum()
                    a["H2"] += (hv ** 2).sum()
                    a["Hinf"] = max(a["Hinf"], float(hv.max()))
                    a["M1"] += mv.sum()
                    a["M2"] += (mv ** 2).sum()
                    a["Minf"] = max(a["Minf"], float(mv.max()))
                    a["n"] += int(msk.sum())
            if plane_axis == 1:
                planes[p][0][i0:i1, :] = Hr[:, mid, :]
                planes[p][1][i0:i1, :] = Mabs[:, mid, :]
    out = {}
    for p in orders:
        out[p] = {}
        for name, a in acc[p].items():
            nn = max(a["n"], 1)
            out[p][name] = dict(H_L1=a["H1"] / nn, H_L2=math.sqrt(a["H2"] / nn), H_Linf=a["Hinf"],
                                M_L1=a["M1"] / nn, M_L2=math.sqrt(a["M2"] / nn), M_Linf=a["Minf"],
                                ncell=a["n"])
    if plane_axis is not None:
        return out, planes, c[gpad:N + gpad]
    return out


def plane_fields(cm, n, L, axis=1, value=0.0):
    """Fields of the slice in the plane x_axis = value: n x n points over [-L, L]^2."""
    u = -L + (np.arange(n) + 0.5) * (2 * L / n)
    A, B = np.meshgrid(u, u, indexing="ij")
    cols = [A, B]
    cols.insert(axis, np.full_like(A, value))
    pts = np.stack([cc.ravel() for cc in cols], axis=1)
    f = cm.fields(pts)
    return u, {k: (v.reshape(n, n) if np.ndim(v) == 1 else v.reshape(n, n, -1)) for k, v in f.items()}
