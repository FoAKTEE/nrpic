#!/usr/bin/env python3
"""Design table of the late Newtonian-mode infall run (wave 3, D-pre-3 toward the
self-similar regime). A design calculation only: the derived parameters of nm_ic.py for a
grid of candidate set-ups, the turnaround radius at the end from the closed-form
turnaround mass, the mesh spacing of the isolated box and the smallest resolved lambda.

For each candidate (a_end, edge_fac, box_fac, nx):
  r_last, R_edge, r_edge(a_end)      nm_ic.derived (closed-form radial Kepler orbits)
  M_ta(a_end) = 1 + (4 pi/3) rho_i (r_last^3 - R_w^3)     (shell that turns around at a_end)
  r_ta = (M_ta t^2/kappa)^(1/3), t = t_i (a_end)^(3/2)     (nm_analyze.py's definition)
  L = box_fac r_edge(a_end), dx = 2 L/nx, lambda_min = 4 dx/r_ta
  dust mass, lattice spacing and particle mass for --ndust particles
  mass inside lambda_min and 0.3 r_ta from the self-similar m(lambda) (test 2), for the
  particle count of the inner bins.
Also r_ta and lambda_min of the same box at the intermediate a/a_i = 4, 8, 16 (with the
closed-form M_ta there).

Usage: python3 nm_design.py --out DIR --selfsim selfsimilar_profile.npz
"""
import argparse
import json
import os
import sys
from types import SimpleNamespace

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import kepler_radial, KAPPA      # noqa: E402
import nm_ic                                  # noqa: E402


def mta_closed(eps, rw, a):
    """Turnaround mass at a/a_i = a: seed + dust inside the shell that turns around then."""
    t_i = 2.0 / (3.0 * eps)
    rho_i = 3.0 * eps**2 / (8.0 * np.pi)
    T = t_i * a**1.5
    menc = lambda r: 1.0 + 4.0 * np.pi / 3.0 * rho_i * (r**3 - rw**3)
    r = brentq(lambda r: kepler_radial(r, eps * r, menc(r), t_i)["t_ta"] - T, 1.01 * rw, 1e5)
    return float(menc(r)), float(r), T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--selfsim", required=True)
    ap.add_argument("--eps", type=float, default=0.03)
    ap.add_argument("--rw", type=float, default=3.0)
    ap.add_argument("--aend", type=float, nargs="+", default=[8.0, 16.0, 30.0])
    ap.add_argument("--edge_fac", type=float, nargs="+", default=[1.2, 1.1, 1.05])
    ap.add_argument("--box_fac", type=float, nargs="+", default=[1.12, 1.06])
    ap.add_argument("--nx", type=int, nargs="+", default=[128, 192])
    ap.add_argument("--ndust", type=float, default=5e5)
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory")
    os.makedirs(a.out, exist_ok=True)
    ss = np.load(a.selfsim)
    lam_g, m_g = np.exp(ss["lngrid"]), np.exp(ss["lnm"])
    m_ss = lambda lam: float(np.interp(np.log(lam), np.log(lam_g), m_g))
    rows = []
    for ae in a.aend:
        mta, r_last_cf, T = mta_closed(a.eps, a.rw, ae)
        r_ta = (mta * T**2 / KAPPA) ** (1.0 / 3.0)
        inter = {}
        for ai in (4.0, 8.0, 16.0):
            if ai < ae:
                mi, _, Ti = mta_closed(a.eps, a.rw, ai)
                inter[ai] = (mi, (mi * Ti**2 / KAPPA) ** (1.0 / 3.0))
        for ef in a.edge_fac:
            p = nm_ic.derived(SimpleNamespace(eps=a.eps, aend=ae, rw=a.rw, edge_fac=ef,
                                              L=0.0, box_fac=1.0))
            vol = 4.0 * np.pi / 3.0 * (p["r_edge"]**3 - a.rw**3)
            m_dust = p["rho_i"] * vol
            h = (vol / a.ndust) ** (1.0 / 3.0)
            mp = m_dust / a.ndust
            for bf in a.box_fac:
                L = bf * p["r_edge_end"]
                for nx in a.nx:
                    dx = 2.0 * L / nx
                    lmin = 4.0 * dx / r_ta
                    row = dict(a_end=ae, edge_fac=ef, box_fac=bf, nx=nx, L=L, dx=dx,
                               t_code_end=p["tlim"], r_last=p["r_last"], r_edge=p["r_edge"],
                               r_edge_end=p["r_edge_end"], M_ta=mta, r_ta=r_ta,
                               L_over_rta=L / r_ta, lambda_min=lmin, dx_over_rta=dx / r_ta,
                               m_dust=m_dust, lattice_h=h, m_particle=mp,
                               n_inside_lmin=(mta * m_ss(lmin)) / mp if lmin < 1 else None,
                               n_inside_0p3=(mta * m_ss(0.3)) / mp,
                               h_over_dx=h / dx, r_edge_over_dx=p["r_edge"] / dx,
                               inter={f"{k:g}": dict(M_ta=v[0], r_ta=v[1], lambda_min=4 * dx / v[1])
                                      for k, v in inter.items()})
                    rows.append(row)
    with open(os.path.join(a.out, "nm_design.json"), "w") as f:
        json.dump(dict(eps=a.eps, rw=a.rw, ndust=a.ndust, rows=rows), f, indent=1)
    hdr = ("a_end edge box nx    L      dx    r_ta   L/r_ta lam_min  M_ta  m_dust  h/dx  "
           "R_edge/dx  N(<lmin)  lam_min@4 @8 @16")
    lines = [hdr]
    for r in rows:
        lm = " ".join(f"{r['inter'][k]['lambda_min']:.3f}" for k in ("4", "8", "16") if k in r["inter"])
        lines.append(f"{r['a_end']:5g} {r['edge_fac']:4g} {r['box_fac']:4g} {r['nx']:3d} "
                     f"{r['L']:7.1f} {r['dx']:6.2f} {r['r_ta']:6.1f} {r['L_over_rta']:6.3f} "
                     f"{r['lambda_min']:6.4f} {r['M_ta']:6.3f} {r['m_dust']:6.2f} {r['h_over_dx']:5.3f} "
                     f"{r['r_edge_over_dx']:6.2f} {r['n_inside_lmin'] or 0:9.0f}  {lm}")
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(a.out, "nm_design.txt"), "w") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
