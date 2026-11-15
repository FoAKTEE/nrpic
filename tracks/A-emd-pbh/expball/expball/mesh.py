"""Fields on a Cartesian mesh, finite-difference constraint residuals, cloud-in-cell deposit.

Conformally flat slice: gamma_ij = psi^4 delta_ij, K^i_j = KT delta_ij + (KL - KT) n_i n_j
(mixed components; K_ij = psi^4 K^i_j). Residuals (DERIVATION.md, section 6):

    H   = -8 psi^-5 lap(psi) + K^2 - K^i_j K^j_i - 16 pi rho
    M_i = d_j K^j_i + 6 K^l_i d_l ln psi - 2 K d_i ln psi - d_i K

(the second line is D_j K^j_i - D_i K with the Christoffel symbols of psi^4 delta_ij;
sym/sym_slice.py (e) checks the general Cartesian form against the radial one, and
`residuals_general` below evaluates the general form with Christoffel symbols built by
finite differences, as a cross-check of the specialised one). Cell-centred grids,
x_i = x_0 + (i + 1/2) h, like AthenaK.
"""

import math

import numpy as np

__all__ = ["D1", "D2", "radial_source", "residuals", "residuals_general", "deposit_cic",
           "mesh_fields", "write_mesh_npz"]

D1 = {2: (-0.5, 0.0, 0.5),
      4: (1 / 12, -2 / 3, 0.0, 2 / 3, -1 / 12),
      6: (-1 / 60, 3 / 20, -3 / 4, 0.0, 3 / 4, -3 / 20, 1 / 60)}
D2 = {2: (1.0, -2.0, 1.0),
      4: (-1 / 12, 4 / 3, -5 / 2, 4 / 3, -1 / 12),
      6: (1 / 90, -3 / 20, 3 / 2, -49 / 18, 3 / 2, -3 / 20, 1 / 90)}


def _apply(f, axis, coeffs, gpad):
    """Stencil along `axis`; f carries gpad ghost layers on every side of every axis and the
    result lives on the interior (gpad layers removed everywhere)."""
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


def radial_source(ball, table=None):
    """Callable rbar -> dict(u, KL, KT, rho): the ball's own interpolant ('exact', error
    ~1e-14), or u, KL, KT from a format-2 table (Format2Table) with the exact density."""
    def src(rb):
        f = ball.fields(rb, ("u", "KL", "KT", "rho"))
        if table is not None:
            t = table(rb, ("u", "KL", "KT"))
            f.update(u=t["u"], KL=t["KL"], KT=t["KT"])
        return f
    return src


def _kmix(KL, KT, n):
    d = KL - KT
    K = {}
    for i in range(3):
        for j in range(i, 3):
            K[i, j] = d * n[i] * n[j] + (KT if i == j else 0.0)
            K[j, i] = K[i, j]
    return K


def residuals(src, N, L, orders=(2, 4), regions=None, slab=8, octant=True,
              plane=False, norm=1.0):
    """Hamiltonian and momentum residuals on the cell-centred grid of the octant [0, L]^3
    (N cells per side), for each FD order. regions: dict name -> callable(rbar) -> mask.
    Returns {order: {region: dict(H_L1, H_L2, H_Linf, M_L1, M_L2, M_Linf, ncell)}} with the
    residuals divided by `norm`; with plane=True also the first layer z = h/2 of H and |M|."""
    h = L / N
    gpad = max(orders) // 2
    i_all = np.arange(-gpad, N + gpad)
    c = (i_all + 0.5) * h if octant else -L + (i_all + 0.5) * (2 * L / N)
    if not octant:
        h = 2 * L / N
    regions = regions or {"all": lambda r: np.ones_like(r, dtype=bool)}
    acc = {p: {k: dict(H1=0.0, H2=0.0, Hinf=0.0, M1=0.0, M2=0.0, Minf=0.0, n=0)
               for k in regions} for p in orders}
    planes = {p: (np.zeros((N, N)), np.zeros((N, N))) for p in orders} if plane else None
    for i0 in range(0, N, slab):
        i1 = min(N, i0 + slab)
        xs = c[i0:i1 + 2 * gpad]
        X = xs[:, None, None]
        Y = c[None, :, None]
        Z = c[None, None, :]
        rb = np.sqrt(X * X + Y * Y + Z * Z)
        f = src(rb)
        psi = 1.0 + f["u"]
        n = (X / rb, Y / rb, Z / rb)
        K = _kmix(f["KL"], f["KT"], n)
        trK = K[0, 0] + K[1, 1] + K[2, 2]
        lnpsi = np.log(psi)
        rbi = _interior(rb, gpad)
        for p in orders:
            lap = sum(_apply(psi, a, D2[p], gpad) for a in range(3)) / h ** 2
            KK = sum(_interior(K[i, j], gpad) ** 2 for i in range(3) for j in range(3))
            Hr = (-8.0 * _interior(psi, gpad) ** -5 * lap + _interior(trK, gpad) ** 2 - KK
                  - 16.0 * math.pi * _interior(f["rho"], gpad)) / norm
            dl = [_apply(lnpsi, a, D1[p], gpad) / h for a in range(3)]
            trKi = _interior(trK, gpad)
            Mr = []
            for i in range(3):
                s = sum(_apply(K[j, i], j, D1[p], gpad) for j in range(3)) / h
                s = s + 6.0 * sum(_interior(K[l, i], gpad) * dl[l] for l in range(3))
                s = s - 2.0 * trKi * dl[i] - _apply(trK, i, D1[p], gpad) / h
                Mr.append(s / norm)
            Mabs = np.sqrt(Mr[0] ** 2 + Mr[1] ** 2 + Mr[2] ** 2)
            for name, fn in regions.items():
                msk = fn(rbi)
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
            if plane:
                planes[p][0][i0:i1, :] = Hr[:, :, 0]
                planes[p][1][i0:i1, :] = Mabs[:, :, 0]
    out = {}
    for p in orders:
        out[p] = {}
        for name, a in acc[p].items():
            nn = max(a["n"], 1)
            out[p][name] = dict(H_L1=a["H1"] / nn, H_L2=math.sqrt(a["H2"] / nn), H_Linf=a["Hinf"],
                                M_L1=a["M1"] / nn, M_L2=math.sqrt(a["M2"] / nn), M_Linf=a["Minf"],
                                ncell=a["n"])
    if plane:
        return out, planes
    return out


def residuals_general(src, N, L, order=4, norm=1.0):
    """Cross-check on the octant: Christoffel symbols and Ricci tensor of the full metric
    gamma_ij = psi^4 delta_ij by finite differences of gamma (two stencil passes), momentum
    constraint with the general D_j K^j_i. Returns (H, |M|, rbar) on the interior cells."""
    h = L / N
    g = order // 2
    gp = 2 * g
    c = (np.arange(-gp, N + gp) + 0.5) * h
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    rb = np.sqrt(X * X + Y * Y + Z * Z)
    f = src(rb)
    psi4 = (1.0 + f["u"]) ** 4
    n = (X / rb, Y / rb, Z / rb)
    Km = _kmix(f["KL"], f["KT"], n)
    gam = np.zeros((3, 3) + rb.shape)
    Kdn = np.zeros((3, 3) + rb.shape)
    for i in range(3):
        gam[i, i] = psi4
        for j in range(3):
            Kdn[i, j] = psi4 * Km[i, j]
    st = D1[order]

    def crop(F, k):
        return F[(Ellipsis,) + tuple(slice(k, s - k) for s in F.shape[-3:])]

    def inv(G):
        a = np.moveaxis(G, (0, 1), (-2, -1))
        return np.moveaxis(np.linalg.inv(a), (-2, -1), (0, 1))

    # first pass: dg[a, i, j] = d_a gamma_ij on the region with g ghosts left
    dg = np.stack([np.stack([np.stack([_apply(gam[i, j], a, st, g) / h for j in range(3)])
                             for i in range(3)]) for a in range(3)])
    gi = inv(crop(gam, g))
    Gu = np.einsum("kl...,lij...->kij...", gi, _christoffel_lower(dg))     # Gamma^k_ij
    # second pass: dGu[a, k, i, j] = d_a Gamma^k_ij on the interior
    dGu = np.stack([np.stack([np.stack([np.stack([_apply(Gu[k, i, j], a, st, g) / h
                                                  for j in range(3)]) for i in range(3)])
                              for k in range(3)]) for a in range(3)])
    Guc = crop(Gu, g)
    # R_ij = d_k G^k_ij - d_j G^k_ik + G^k_kl G^l_ij - G^k_jl G^l_ik
    Ric = (np.einsum("kkij...->ij...", dGu) - np.einsum("jkik...->ij...", dGu)
           + np.einsum("kkl...,lij...->ij...", Guc, Guc)
           - np.einsum("kjl...,lik...->ij...", Guc, Guc))
    gii = crop(gi, g)
    Rs = np.einsum("ij...,ij...->...", gii, Ric)
    Kmix = np.einsum("ik...,kj...->ij...", gii, crop(Kdn, gp))
    trK = np.einsum("ii...->...", Kmix)
    KK = np.einsum("ij...,ji...->...", Kmix, Kmix)
    rho = crop(f["rho"], gp)
    Ham = (Rs + trK ** 2 - KK - 16 * math.pi * rho) / norm
    # momentum: D_j K^j_i - d_i K; one stencil pass on K^j_i, Christoffels of the first pass
    Kmf = np.einsum("ik...,kj...->ij...", inv(gam), Kdn)
    trKf = np.einsum("ii...->...", Kmf)
    Kmg = crop(Kmf, g)
    Mom = []
    for i in range(3):
        s = sum(_apply(Kmf[j, i], j, st, g) / h for j in range(3)) - _apply(trKf, i, st, g) / h
        s = s + np.einsum("jjl...,l...->...", Gu, Kmg[:, i]) \
            - np.einsum("lji...,jl...->...", Gu, Kmg)
        Mom.append(crop(s, g) / norm)
    Mabs = np.sqrt(sum(m ** 2 for m in Mom))
    return Ham, Mabs, crop(rb, gp)


def _christoffel_lower(dg):
    """Gamma_kij = 1/2 (d_i g_kj + d_j g_ki - d_k g_ij) from dg[a, i, j] = d_a g_ij."""
    G = np.empty_like(dg)
    for k in range(3):
        for i in range(3):
            for j in range(3):
                G[k, i, j] = 0.5 * (dg[i, k, j] + dg[j, k, i] - dg[k, i, j])
    return G


def deposit_cic(x, m, N, L):
    """Cloud-in-cell (linear) deposit of masses m at positions x[N,3] on the cell-centred
    grid of [-L, L]^3 with N cells per side: returns the mass per cell (N, N, N)."""
    h = 2.0 * L / N
    s = (np.asarray(x) + L) / h - 0.5
    i0 = np.floor(s).astype(np.int64)
    fr = s - i0
    out = np.zeros(N ** 3)
    for dx in (0, 1):
        wx = fr[:, 0] if dx else 1 - fr[:, 0]
        ix = i0[:, 0] + dx
        for dy in (0, 1):
            wy = fr[:, 1] if dy else 1 - fr[:, 1]
            iy = i0[:, 1] + dy
            for dz in (0, 1):
                wz = fr[:, 2] if dz else 1 - fr[:, 2]
                iz = i0[:, 2] + dz
                ok = (ix >= 0) & (ix < N) & (iy >= 0) & (iy < N) & (iz >= 0) & (iz < N)
                idx = (ix[ok] * N + iy[ok]) * N + iz[ok]
                out += np.bincount(idx, weights=(m * wx * wy * wz)[ok], minlength=N ** 3)
    return out.reshape(N, N, N)


def mesh_fields(ball, N, L, table=None):
    """3+1 fields on the cell-centred grid of [-L, L]^3: dict of (N, N, N) arrays."""
    h = 2.0 * L / N
    c = -L + (np.arange(N) + 0.5) * h
    X, Y, Z = np.meshgrid(c, c, c, indexing="ij")
    rb = np.sqrt(X * X + Y * Y + Z * Z)
    f = ball.fields(rb, ("u", "KL", "KT", "rho", "betar"))
    if table is not None:
        t = table(rb, ("u", "KL", "KT", "betar"))
        f.update(t)
    psi = 1.0 + f["u"]
    n = (X / rb, Y / rb, Z / rb)
    K = _kmix(f["KL"], f["KT"], n)
    out = dict(x=c, psi=psi, alpha=np.ones_like(rb), E=f["rho"],
               Sx=np.zeros_like(rb), Sy=np.zeros_like(rb), Sz=np.zeros_like(rb))
    names = "xyz"
    for i in range(3):
        out["beta" + names[i]] = f["betar"] * n[i]
        for j in range(i, 3):
            out["g" + names[i] + names[j]] = psi ** 4 * (1.0 if i == j else 0.0) + 0 * rb
            out["K" + names[i] + names[j]] = psi ** 4 * K[i, j]
    return out


def write_mesh_npz(path, ball, N, L, table=None, meta=None):
    f = mesh_fields(ball, N, L, table)
    f["meta"] = np.array(str(meta or {}))
    np.savez_compressed(path, **f)
    return f
