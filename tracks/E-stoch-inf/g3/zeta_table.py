"""Table of the zeta reader's map along the box's own relation (R41; g3/JOURNAL.md entry 10).

The map DN(phi, v) of zeta/zeta_reader.py (map_rk4, RK4 in phi to phi_e) is smooth, and the cells of a box at N_f lie
in a thin band about a straight line in (phi, v) (corr 0.999997 at 128^3, entry 9). With u = phi - <phi> and
w = v - (v0 + b u) (least squares), the map is tabulated on nu uniform nodes in u times nw Chebyshev nodes in w, each
node by the same map_rk4; per cell a not-a-knot cubic spline in u at every w node, then the Lagrange polynomial through
the w nodes. This replaces 2.1e6 map evaluations by nu * nw (28679 by default).

    dn, info = table_map(map_fn, phi, v)        # map_fn(phi_array, v_array) -> DN array
"""
import numpy as np
from scipy.interpolate import CubicSpline


def relation(phi, v):
    pm = float(phi.mean())
    u = phi - pm
    b = float(np.sum(u * (v - v.mean())) / np.sum(u * u))
    v0 = float(v.mean())
    w = v - v0 - b * u
    return pm, v0, b, u, w


def table_map(map_fn, phi, v, nu=4097, nw=7, umargin=0.02, wmargin=0.05):
    phi = np.asarray(phi, float).ravel()
    v = np.asarray(v, float).ravel()
    pm, v0, b, u, w = relation(phi, v)
    ulo, uhi = float(u.min()), float(u.max())
    du = (uhi - ulo) * umargin
    un = np.linspace(ulo - du, uhi + du, nu)
    wlo, whi = float(w.min()), float(w.max())
    wc, wh = 0.5 * (wlo + whi), 0.5 * (whi - wlo) * (1.0 + wmargin)
    wn = wc + wh * np.cos(np.pi * (2 * np.arange(nw) + 1) / (2 * nw))       # Chebyshev nodes of the first kind
    U, W = np.meshgrid(un, wn, indexing="ij")
    T = map_fn(pm + U.ravel(), v0 + b * U.ravel() + W.ravel()).reshape(nu, nw)
    # Lagrange weights in w for every cell
    lw = np.ones((nw, w.size))
    for j in range(nw):
        for m in range(nw):
            if m != j:
                lw[j] *= (w - wn[m]) / (wn[j] - wn[m])
    dn = np.zeros_like(u)
    for j in range(nw):
        dn += lw[j] * CubicSpline(un, T[:, j], bc_type="not-a-knot")(u)
    info = dict(phi_mean=pm, v0=v0, slope=b, u_range=[ulo, uhi], w_range=[wlo, whi], nu=nu, nw=nw,
                corr=float(np.corrcoef(u, v - v.mean())[0, 1]),
                w_rms_over_v_rms=float(np.std(w) / np.std(v)))
    return dn, info
