#!/usr/bin/env python3
"""J3b (and J4 for P1): r psi4 extrapolated in 1/R at fixed retarded time, then energy and
momentum of the junk window by FFI (omega_0 list) and by the time-domain method.

Each mode at each sphere is interpolated (cubic spline) onto one grid of u = t - R*(R, M) with
step du over the u range common to all spheres; per u a least-squares fit
r psi4_lm(u, R) = A_lm(u) + B_lm(u)/R [+ C_lm(u)/R^2 for --order=2]; the pipeline of junk_lib
then runs on A. Writes <tag>_extrap.json and <tag>_extrap_curves.npz.
Usage: extrap_junk.py <out | -> <run dir> --tag=S2g --M=1.0383 --radii=30,40,50
                      --window=-15,30 [--w0=0.1,0.2,0.3] [--order=1] [--du=0.25]
                      [--umax=<cut the record here>]
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import junk_lib as jl  # noqa: E402

TAPER = 4.0


def parse():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    o = dict(rd=sys.argv[2], tag="S2g", M=1.0383218096698035, radii=(30, 40, 50),
             window=(-15.0, 30.0), w0=(0.1, 0.2, 0.3), order=1, du=0.25, umax=None)
    for a in sys.argv[3:]:
        k, v = a[2:].split("=")
        if k == "tag":
            o[k] = v
        elif k in ("M", "du", "umax"):
            o[k] = float(v)
        elif k == "order":
            o[k] = int(v)
        elif k == "radii":
            o[k] = tuple(int(x) for x in v.split(","))
        elif k in ("window", "w0"):
            o[k] = tuple(float(x) for x in v.split(","))
    return out, o


def extrapolate(rd, radii, M, du, order, umax=None):
    data = {}
    for R in radii:
        t, modes = jl.load_modes(rd, R)
        data[R] = (t - jl.tortoise(R, M), modes)
    ua = max(d[0][0] for d in data.values())
    ub = min(d[0][-1] for d in data.values())
    if umax is not None:
        ub = min(ub, umax)
    u = np.arange(np.ceil(ua / du) * du, ub + 1e-9, du)
    keys = list(data[radii[0]][1].keys())
    x = 1.0 / np.asarray(radii, dtype=float)
    V = np.vstack([x ** k for k in range(order + 1)]).T            # (nR, order+1)
    pinv = np.linalg.pinv(V)
    A, Bc, resid = {}, {}, {}
    fin = {}
    for k in keys:
        Z = np.stack([CubicSpline(data[R][0], data[R][1][k].real)(u)
                      + 1j * CubicSpline(data[R][0], data[R][1][k].imag)(u) for R in radii])
        c = pinv @ Z                                                 # (order+1, nu)
        A[k] = c[0]
        Bc[k] = c[1]
        resid[k] = Z - V @ c
        fin[k] = Z
    return u, A, Bc, resid, fin


def pipeline(u, modes, window, w0s, sph):
    u0, u1 = window
    out, curves = {}, {}
    for w0 in w0s:
        N = {k: jl.ffi(u, z, w0, TAPER) for k, z in modes.items()}
        dE, dP = sph.flux(N)
        e = dict(E=jl.window_integral(u, dE, u0, u1),
                 P=[jl.window_integral(u, dP[i], u0, u1) for i in range(3)])
        pre = (u >= u[0] + TAPER) & (u < u0)
        post = (u > u1) & (u <= u[-1] - TAPER)
        e["noise_E_pre"] = float(np.mean(dE[pre]) * (u1 - u0)) if np.any(pre) else None
        e["noise_E_post"] = float(np.mean(dE[post]) * (u1 - u0)) if np.sum(post) > 4 else None
        sel = (u >= u0) & (u <= u1)
        e["u_peak_dE"] = float(u[sel][np.argmax(dE[sel])])
        out[f"ffi{w0}"] = e
        curves[f"dE_ffi{w0}"] = dE
        curves[f"dP_ffi{w0}"] = dP
    Ntd = {k: jl.td_quad(u, z, window, u0 - 0.25 * (u1 - u0)) for k, z in modes.items()}
    dE, dP = sph.flux(Ntd)
    out["td"] = dict(E=jl.window_integral(u, dE, u0, u1),
                     P=[jl.window_integral(u, dP[i], u0, u1) for i in range(3)])
    curves["dE_td"] = dE
    return out, curves


def main():
    out, o = parse()
    os.makedirs(out, exist_ok=True)
    sph = jl.Sphere()
    u, A, B, resid, fin = extrapolate(o["rd"], o["radii"], o["M"], o["du"], o["order"], o["umax"])
    res = {"options": {k: (list(v) if isinstance(v, tuple) else v) for k, v in o.items()},
           "u_range": [float(u[0]), float(u[-1])]}
    r, c = pipeline(u, A, o["window"], o["w0"], sph)
    res["extrapolated"] = r
    # the same pipeline on each finite radius, on the same u grid (for comparison)
    res["finite"] = {}
    curves = {"u": u}
    for i, R in enumerate(o["radii"]):
        rr, cc = pipeline(u, {k: fin[k][i] for k in fin}, o["window"], o["w0"], sph)
        res["finite"][str(R)] = rr
        for k, v in cc.items():
            curves[f"R{R}_{k}"] = v
        for k in ((2, 0), (2, 2), (2, -2)):
            curves[f"R{R}_rpsi4_{k[0]}{k[1]}"] = fin[k][i]
    pk = {k: float(np.max(np.abs(A[k]))) for k in A}
    lo, hi = o["window"]
    late = (u >= 15.0) & (u <= hi)
    res["A_post_pulse_over_peak"] = {f"{k[0]},{k[1]}": float(np.max(np.abs(A[k][late])) / pk[k])
                                    for k in ((2, 0), (2, 2), (2, -2))} if np.any(late) else None
    res["A_peak"] = {f"{k[0]},{k[1]}": pk[k] for k in ((2, 0), (2, 2), (2, -2), (3, 0), (3, 2))}
    res["fit_resid_max_over_peak"] = {f"{k[0]},{k[1]}": float(np.max(np.abs(resid[k])) / pk[k])
                                     for k in ((2, 0), (2, 2))}
    for k, v in c.items():
        curves[f"A_{k}"] = v
    for k in ((2, 0), (2, 2), (2, -2)):
        curves[f"A_rpsi4_{k[0]}{k[1]}"] = A[k]
        curves[f"B_rpsi4_{k[0]}{k[1]}"] = B[k]
    E = [r[k]["E"] for k in r]
    res["method_spread_max_over_min"] = float(max(E) / min(E))
    print(json.dumps(res, indent=1, default=float))
    json.dump(res, open(os.path.join(out, f"{o['tag']}_extrap.json"), "w"), indent=1, default=float)
    np.savez(os.path.join(out, f"{o['tag']}_extrap_curves.npz"), **curves)


if __name__ == "__main__":
    main()
