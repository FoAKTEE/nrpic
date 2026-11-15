"""Second-order spatial-gauge piece of the flat TT projection of the conformal metric.

Setting. On one slice, let x' be the code's spatial coordinates and x coordinates in which
the conformal metric tilde gamma = det(gamma)^(-1/3) gamma has no traceless scalar or vector
part ("spatially transverse" coordinates), related by x = x' + xi(x'). With
M_ki = d_i xi_k and J = 1 + M, the conformal metric transforms exactly as

    tilde gamma'(x') = det(J)^(-2/3) J^T tilde gamma_T(x' + xi) J,

so with h = tilde gamma - delta and h_T of second order, to second order in (M, h_T)

    h' = M + M^T + M^T M - (2/3)(tr M)(M + M^T) + h_T + delta_ij (...),
    Lambda h' = Lambda h_T + G,   G = Lambda[M^T M - (2/3)(div xi)(M + M^T)],

because Lambda removes every trace and every longitudinal term d_(i V_j) exactly. xi is
recovered from the traceless non-TT part of the measured h' (first order):
h^L_ij = d_i xi_j + d_j xi_i - (2/3) delta_ij div xi, which in Fourier space inverts to
    xi_i = -i k_j h_ij / k^2 + (i/4) k_i (k_l k_m h_lm) / k^4      (k != 0).
G is "the second-order gauge piece of the flat projection" of the wave-1 caveat
(stage/G0/REVIEW.md lines 98-102); Lambda h' - G is the TT strain on the same slice in
spatially transverse coordinates, to third order. The slicing part of the gauge freedom is
not touched: on pure-gauge data with a changed slicing the residual stays second order
(tests/test_gauge.py).

Array layout as in gw_diag (grid.py): tensors (3, 3, nz, ny, nx), direction a on axis -1-a.
Products are formed on a mesh padded by 3/2 (dealiased) unless pad=False.
"""
import numpy as np

from gwdiag import tt

AX = (-3, -2, -1)


def traceless(h):
    tr = np.einsum("aa...->...", h)
    return h - np.eye(3)[:, :, None, None, None] * tr / 3.0


def _kgrid(grid):
    k = grid.kvec(real=True)
    k2 = (k ** 2).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        inv2 = np.where(k2 > 0, 1.0 / np.where(k2 > 0, k2, 1.0), 0.0)
    return k, k2, inv2


def xi_hat_from_h(h, grid):
    """Fourier coefficients (3, nz, ny, nx//2+1) of xi from the traceless non-TT part of h
    (the TT part and the trace drop out). Mean and Nyquist planes set to zero."""
    F = tt.tensor_rfft(traceless(h))
    k, k2, inv2 = _kgrid(grid)
    kF = np.einsum("b...,ab...->a...", k, F)          # k_j h_ij
    kkF = np.einsum("a...,a...->...", k, kF)          # k_i k_j h_ij
    X = -1j * kF * inv2 + 0.25j * k * kkF * inv2 ** 2
    X[:, grid.nyquist_mask(real=True)] = 0.0
    X[:, 0, 0, 0] = 0.0
    return X


def longitudinal_from_xi_hat(X, grid):
    """Fourier coefficients of d_i xi_j + d_j xi_i - (2/3) delta div xi (check of the inverse)."""
    k = grid.kvec(real=True)
    D = 1j * (k[:, None] * X[None, :] + k[None, :] * X[:, None])     # [i, j] = i(k_i xi_j + k_j xi_i)
    div = 1j * np.einsum("a...,a...->...", k, X)
    D = D - (2.0 / 3.0) * np.eye(3)[:, :, None, None, None] * div
    return D


def _pad(F, grid, shape_p):
    """Embed rfft coefficients of a field on grid.shape into a padded rfft array."""
    nz, ny, nx = grid.shape
    pz, py, px = shape_p
    out = np.zeros(F.shape[:-3] + (pz, py, px // 2 + 1), dtype=complex)
    hz, hy = nz // 2, ny // 2
    zs = list(range(0, hz)) + list(range(nz - hz + 1, nz))     # skip Nyquist (zeroed anyway)
    ys = list(range(0, hy)) + list(range(ny - hy + 1, ny))
    zd = [z if z < hz else z - nz + pz for z in zs]
    yd = [y if y < hy else y - ny + py for y in ys]
    nkx = nx // 2
    sub = F[..., zs, :, :][..., :, ys, :][..., :, :, :nkx]
    out[(Ellipsis,) + np.ix_(zd, yd, list(range(nkx)))] = sub
    return out * (pz * py * px) / (nz * ny * nx)


def _unpad(Fp, grid, shape_p):
    nz, ny, nx = grid.shape
    pz, py, px = shape_p
    out = np.zeros(Fp.shape[:-3] + (nz, ny, nx // 2 + 1), dtype=complex)
    hz, hy = nz // 2, ny // 2
    zs = list(range(0, hz)) + list(range(nz - hz + 1, nz))
    ys = list(range(0, hy)) + list(range(ny - hy + 1, ny))
    zd = [z if z < hz else z - nz + pz for z in zs]
    yd = [y if y < hy else y - ny + py for y in ys]
    nkx = nx // 2
    out[(Ellipsis,) + np.ix_(zs, ys, list(range(nkx)))] = Fp[(Ellipsis,) + np.ix_(zd, yd, list(range(nkx)))]
    return out * (nz * ny * nx) / (pz * py * px)


def gauge_piece(h, grid, pad=True, return_parts=False):
    """G = Lambda[M^T M - (2/3)(div xi)(M + M^T)] (real space, (3, 3, nz, ny, nx)) for the
    displacement xi recovered from h. With return_parts also xi, M and the Fourier
    coefficients of G."""
    X = xi_hat_from_h(h, grid)
    k = grid.kvec(real=True)
    Mh = 1j * k[None, :] * X[:, None]                 # M[m, i] = d_i xi_m
    if pad:
        shp = tuple(int(3 * n // 2) for n in grid.shape)
        Mp = _pad(Mh, grid, shp)
        M = np.fft.irfftn(Mp, s=shp, axes=AX)
    else:
        shp = grid.shape
        M = np.fft.irfftn(Mh, s=shp, axes=AX)
    trM = np.einsum("aa...->...", M)
    Q = np.einsum("mi...,mj...->ij...", M, M) - (2.0 / 3.0) * trM * (M + np.einsum("ij...->ji...", M))
    Qh = np.fft.rfftn(Q, axes=AX)
    if pad:
        Qh = _unpad(Qh, grid, shp)
    _, kk, kh = tt._khat(grid)
    Gh = tt.lambda_apply(Qh, kh)
    Gh[:, :, 0, 0, 0] = 0.0
    Gh[:, :, grid.nyquist_mask(real=True)] = 0.0
    G = np.empty((3, 3) + grid.shape)
    for a in range(3):
        for b in range(a, 3):
            G[a, b] = np.fft.irfftn(Gh[a, b], s=grid.shape, axes=AX)
            G[b, a] = G[a, b]
    if not return_parts:
        return G
    xi = np.fft.irfftn(X, s=grid.shape, axes=AX)
    Mg = np.fft.irfftn(Mh, s=grid.shape, axes=AX)
    return G, {"xi": xi, "M": Mg, "G_hat": Gh}


def gauge_piece_A(h, At, grid, pad=True):
    """Spatial-gauge piece of Lambda tilde A for the same displacement xi (from h).

    tilde A = det(gamma)^(-1/3) (K - gamma K/3) transforms like the conformal metric,
    tilde A'(x') = det(J)^(-2/3) J^T tilde A_T(x' + xi) J, so to second order
        Lambda tilde A' = Lambda tilde A_T + G_A,
        G_A = Lambda[M^T A + A M - (2/3)(tr M) A + (xi . grad) A],
    with A the measured tilde A (its first-order part is the same in both coordinates).
    Returns G_A in real space."""
    X = xi_hat_from_h(h, grid)
    k = grid.kvec(real=True)
    Mh = 1j * k[None, :] * X[:, None]
    FA = tt.tensor_rfft(At)
    FA[:, :, grid.nyquist_mask(real=True)] = 0.0
    dAh = 1j * k[:, None, None] * FA[None]            # [c, i, j] = d_c A_ij
    shp = tuple(int(3 * n // 2) for n in grid.shape) if pad else grid.shape
    if pad:
        M = np.fft.irfftn(_pad(Mh, grid, shp), s=shp, axes=AX)
        A = np.fft.irfftn(_pad(FA, grid, shp), s=shp, axes=AX)
        xi = np.fft.irfftn(_pad(X, grid, shp), s=shp, axes=AX)
        dA = np.fft.irfftn(_pad(dAh, grid, shp), s=shp, axes=AX)
    else:
        M = np.fft.irfftn(Mh, s=shp, axes=AX)
        A = np.fft.irfftn(FA, s=shp, axes=AX)
        xi = np.fft.irfftn(X, s=shp, axes=AX)
        dA = np.fft.irfftn(dAh, s=shp, axes=AX)
    trM = np.einsum("aa...->...", M)
    Q = (np.einsum("ki...,kj...->ij...", M, A) + np.einsum("ik...,kj...->ij...", A, M)
         - (2.0 / 3.0) * trM * A + np.einsum("c...,cij...->ij...", xi, dA))
    Qh = np.fft.rfftn(Q, axes=AX)
    if pad:
        Qh = _unpad(Qh, grid, shp)
    _, kk, kh = tt._khat(grid)
    Gh = tt.lambda_apply(Qh, kh)
    Gh[:, :, 0, 0, 0] = 0.0
    Gh[:, :, grid.nyquist_mask(real=True)] = 0.0
    G = np.empty((3, 3) + grid.shape)
    for a in range(3):
        for b in range(a, 3):
            G[a, b] = np.fft.irfftn(Gh[a, b], s=grid.shape, axes=AX)
            G[b, a] = G[a, b]
    return G


def gauge_piece_total(h, grid, pad=True):
    """G_tot = G + G_x: the quadratic piece G plus the cross terms of xi with the part of
    the target metric that the coordinates do not remove, h_T ~ Lambda h + h0 (the TT part
    and the homogeneous traceless part h0 of the box, which no periodic xi can remove):
        G_x = Lambda[M^T A + A M - (2/3)(tr M) A + (xi . grad) A],  A = Lambda h + h0.
    The cross terms matter when h_T is not small against M; with h0 they were found
    missing by the second-gauge run (JOURNAL.md, P6 at 32^3)."""
    ht = traceless(h)
    A = ht - nonTT_traceless(h, grid)                  # TT part + homogeneous traceless part
    return gauge_piece(h, grid, pad=pad) + gauge_piece_A(h, A, grid, pad=pad)


def nonTT_traceless(h, grid):
    """Traceless non-TT part of h (k != 0), real space."""
    hT = traceless(h)
    return hT - tt.tt_project(hT, grid) - hT.mean(axis=(-3, -2, -1), keepdims=True)
