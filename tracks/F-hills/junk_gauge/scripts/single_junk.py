#!/usr/bin/env python3
"""J1/J3: junk radiation of one member, from S2g's spheres (method of JOURNAL.md J1).

Per sphere R (30, 40, 50 m): retarded time u = t - R*(R, M); the news by FFI (omega_0 = 0.1,
0.2, 0.3, taper 4 m) and by the time-domain method (quadratic outside the window); energy and
momentum radiated in the junk window u in [U0, U1]; the noise energy (mean rate before and after
the window, times the window's length); the u of the peak of dE/du; the peak of |r psi4_20|;
the share of the energy per mode group. Then E(R) = E_inf + a/R (least squares).
Writes single_junk.json and single_junk_curves.npz (read by the figure scripts).
Usage: single_junk.py <out | - for $NRPIC_RUN_DIR> <run dir> [--M=1.0383] [--radii=30,40,50]
                      [--window=-15,30] [--tag=single]   (P1: --M=1.25 --radii=40,48,70,90
                      --window=-35,50 --tag=P1; outputs <tag>_junk.json, <tag>_junk_curves.npz)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import junk_lib as jl  # noqa: E402

U0, U1 = -15.0, 30.0          # junk window in retarded time (J1)
W0S = (0.1, 0.2, 0.3)         # FFI cutoffs; 0.2 central
TAPER = 4.0


def args():
    global U0, U1
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    rd = sys.argv[2]
    M, radii = 1.0383218096698035, (30, 40, 50)    # M_ADM full solution (nr_first E3 reference)
    tag = "single"
    for a in sys.argv[3:]:
        if a.startswith("--M="):
            M = float(a[4:])
        elif a.startswith("--radii="):
            radii = tuple(int(x) for x in a[8:].split(","))
        elif a.startswith("--window="):
            U0, U1 = (float(x) for x in a[9:].split(","))
        elif a.startswith("--tag="):
            tag = a[6:]
    return out, rd, M, radii, tag


def groups(Nmodes):
    """Energy rate per mode group."""
    g = {"(2,0)": [(2, 0)], "(2,+-2)": [(2, 2), (2, -2)], "(2,+-1)": [(2, 1), (2, -1)],
         "l=3": [k for k in Nmodes if k[0] == 3], "l>=4": [k for k in Nmodes if k[0] >= 4]}
    return {n: sum(np.abs(Nmodes[k]) ** 2 for k in ks) / (16 * np.pi) for n, ks in g.items()}


def measure(rd, R, M, sph, u0=U0, u1=U1):
    t, modes = jl.load_modes(rd, R)
    Rs = jl.tortoise(R, M)
    u = t - Rs
    r = dict(R=R, R_star=Rs, t_end=float(t[-1]), u_end=float(u[-1]), dt=float(np.median(np.diff(t))),
             window_u=[u0, u1], window_t=[u0 + Rs, u1 + Rs], complete=bool(u[-1] >= u1))
    i20 = np.argmax(np.abs(modes[(2, 0)]))
    r["peak_abs_rpsi4_20"] = float(np.abs(modes[(2, 0)][i20]))
    r["u_peak_rpsi4_20"] = float(u[i20])
    curves = {"u": u}
    for w0 in W0S:
        N = {k: jl.ffi(t, z, w0, TAPER) for k, z in modes.items()}
        dE, dP = sph.flux(N)
        key = f"ffi{w0}"
        e = dict(E=jl.window_integral(u, dE, u0, min(u1, u[-1])),
                 P=[jl.window_integral(u, dP[i], u0, min(u1, u[-1])) for i in range(3)])
        pre = (u >= u[0] + TAPER) & (u < u0)
        post = (u > u1) & (u <= u[-1] - TAPER)
        e["noise_rate_pre"] = float(np.mean(dE[pre])) if np.any(pre) else None
        e["noise_rate_post"] = float(np.mean(dE[post])) if np.sum(post) > 4 else None
        e["noise_E_pre"] = e["noise_rate_pre"] * (u1 - u0) if e["noise_rate_pre"] is not None else None
        e["noise_E_post"] = e["noise_rate_post"] * (u1 - u0) if e["noise_rate_post"] is not None else None
        sel = (u >= u0) & (u <= u1)
        e["u_peak_dE"] = float(u[sel][np.argmax(dE[sel])])
        e["max_|dP|/dE"] = float(np.max(np.linalg.norm(dP[:, sel], axis=0) / np.maximum(dE[sel], 1e-300)))
        gr = groups(N)
        e["share"] = {n: jl.window_integral(u, v, u0, min(u1, u[-1])) / e["E"] for n, v in gr.items()}
        r[key] = e
        curves[f"dE_{key}"] = dE
        curves[f"dP_{key}"] = dP
        if w0 == 0.2:
            curves["N20"] = N[(2, 0)]
            curves["N22"] = N[(2, 2)]
    Ntd = {k: jl.td_quad(t, z, (u0 + Rs, u1 + Rs), u0 + Rs - 0.25 * (u1 - u0))
           for k, z in modes.items()}
    dE, dP = sph.flux(Ntd)
    r["td"] = dict(E=jl.window_integral(u, dE, u0, min(u1, u[-1])),
                   P=[jl.window_integral(u, dP[i], u0, min(u1, u[-1])) for i in range(3)])
    curves["dE_td"] = dE
    curves["rpsi4_20"] = modes[(2, 0)]
    curves["rpsi4_22"] = modes[(2, 2)]
    curves["rpsi4_2m2"] = modes[(2, -2)]
    return r, curves


def fit_inv_r(Rs, Es):
    A = np.vstack([np.ones(len(Rs)), 1.0 / np.asarray(Rs, dtype=float)]).T
    c, *_ = np.linalg.lstsq(A, np.asarray(Es), rcond=None)
    resid = np.asarray(Es) - A @ c
    return dict(E_inf=float(c[0]), a=float(c[1]), max_resid=float(np.max(np.abs(resid))))


def main():
    out, rd, M, radii, tag = args()
    os.makedirs(out, exist_ok=True)
    sph = jl.Sphere()
    res = {"run_dir": rd, "M": M, "tag": tag, "window_u": [U0, U1], "taper": TAPER, "radii": {}}
    allc = {}
    for R in radii:
        r, c = measure(rd, R, M, sph, U0, U1)
        res["radii"][str(R)] = r
        for k, v in c.items():
            allc[f"R{R}_{k}"] = v
        print(R, json.dumps(r, indent=1, default=float), flush=True)
    full = [R for R in radii if res["radii"][str(R)]["complete"]]
    res["radii_complete"] = full
    for key in [f"ffi{w}" for w in W0S] + ["td"]:
        if len(full) < 2:
            break
        Es = [res["radii"][str(R)][key]["E"] for R in full]
        f = fit_inv_r(full, Es)
        f["spread_max_over_min"] = float(max(Es) / min(Es))
        f["Px_inf"] = fit_inv_r(full, [res["radii"][str(R)][key]["P"][0] for R in full])["E_inf"]
        res[f"extrap_{key}"] = f
        print(key, f)
    json.dump(res, open(os.path.join(out, f"{tag}_junk.json"), "w"), indent=1, default=float)
    np.savez(os.path.join(out, f"{tag}_junk_curves.npz"), **allc)


if __name__ == "__main__":
    main()
