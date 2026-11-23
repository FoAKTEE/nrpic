"""Run the background and all Langevin variants of repro/langevin; write npz + JSON.

usage: python3 simulate.py OUTDIR [variant ...]      (no variant: all)
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lsde  # noqa: E402

REC = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0)


def backgrounds():
    bgs = {"euler01": lsde.background("euler", 0.01, 12.0),
           "euler005": lsde.background("euler", 0.005, 12.0),
           "exact": lsde.background("rk4", 0.01, 12.0, sub=10)}
    u0t = lsde.tune_u0(3.045)
    bgs["tuned"] = lsde.background("rk4", 0.01, 12.0, u0=u0t, sub=10)
    return bgs


VARIANTS = {
    "base":        dict(bg="euler01", scheme="heun", h=0.01),
    "ito_em":      dict(bg="euler01", scheme="em_ito", h=0.01),
    "ito_naive":   dict(bg="euler01", scheme="em_naive", h=0.01),
    "heun_h001":   dict(bg="euler01", scheme="heun", h=0.001),
    "ito_em_h001": dict(bg="euler01", scheme="em_ito", h=0.001),
    "no_ito":      dict(bg="euler01", scheme="heun", h=0.01, ito_term=False),
    "a3one":       dict(bg="euler01", scheme="heun", h=0.01, a3=False),
    "off6":        dict(bg="euler01", scheme="heun", h=0.01, T=10.0,
                        record=REC + (7.0, 8.0, 10.0)),
    "h005":        dict(bg="euler01", scheme="heun", h=0.005),
    "h02":         dict(bg="euler01", scheme="heun", h=0.02),
    "bg_e005":     dict(bg="euler005", scheme="heun", h=0.005),
    "bg_exact":    dict(bg="exact", scheme="heun", h=0.01),
    "bg_tuned":    dict(bg="tuned", scheme="heun", h=0.01),
    "seed2":       dict(bg="euler01", scheme="heun", h=0.01, seed=2),
    "seed3":       dict(bg="euler01", scheme="heun", h=0.01, seed=3),
    "seed4":       dict(bg="euler01", scheme="heun", h=0.01, seed=4),
    # Ito reading of the printed equation (Euler-Maruyama, no conversion): entry 2
    "naive_s2":    dict(bg="euler01", scheme="em_naive", h=0.01, seed=2),
    "naive_s3":    dict(bg="euler01", scheme="em_naive", h=0.01, seed=3),
    "naive_h001":  dict(bg="euler01", scheme="em_naive", h=0.001),
    "naive_noito": dict(bg="euler01", scheme="em_naive", h=0.01, ito_term=False),
    "naive_tuned": dict(bg="tuned", scheme="em_naive", h=0.01),
}


def bg_summary(bg):
    N, phi, u, e1, e2 = bg["N"], bg["phi"], bg["u"], bg["eps1"], bg["eps2"]
    out = dict(scheme=bg["scheme"], h=bg["h"], sub=bg["sub"], u0=bg["u0"], V0=bg["V0"],
               N_cross_phi_c=lsde.crossing(bg), phi_at_12=float(phi[-1]))
    for Nq in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 3.04, 3.05, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0):
        j = int(round(Nq / bg["h"]))
        sig = lsde.sigma_of(e1[j], bg["H"][j])
        out[f"N={Nq:g}"] = dict(phi=float(phi[j]), u=float(u[j]), eps1=float(e1[j]),
                                eps2=float(e2[j]), H=float(bg["H"][j]), sigma=float(sig))
    # first time in USR: eps1 < 1e-2 and |eps2 - 6| < 0.03
    usr = np.nonzero((e1 < 1e-2) & (np.abs(e2 - 6.0) < 0.03))[0]
    out["N_first_usr"] = float(N[usr[0]]) if len(usr) else None
    j = int(np.argmin(np.abs(u[N > 3.0]))) + int(np.sum(N <= 3.0))
    out["N_min_absu_after3"] = float(N[j])
    out["min_absu_after3"] = float(abs(u[j]))
    return out


def main():
    outdir = sys.argv[1]
    names = sys.argv[2:] or list(VARIANTS)
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    bgs = backgrounds()
    bgsum = {k: bg_summary(v) for k, v in bgs.items()}
    bgsum["analytic_plateau_stop"] = float(
        lsde.PHI0 - np.log((np.sqrt(6) + 2.0001) / (np.sqrt(6) - 2.0001)) / np.sqrt(6))
    for k, v in bgs.items():
        np.savez(os.path.join(outdir, f"bg_{k}.npz"), **{a: v[a] for a in
                 ("N", "phi", "u", "eps1", "eps2", "H")})
    lin = lsde.linear_moments(bgs["euler01"])
    np.savez(os.path.join(outdir, "linear_euler01.npz"), N=lin[0], std_a=lin[1], std_D=lin[2])
    summ = dict(backgrounds=bgsum, variants={})
    for name in names:
        cfg = dict(VARIANTS[name])
        bg = bgs[cfg.pop("bg")]
        t1 = time.time()
        r = lsde.simulate(bg, **cfg)
        dt = time.time() - t1
        arrs = dict(N=r["N"], sigma=r["sigma"], eps1=r["eps1"], eps2=r["eps2"],
                    keep_a=r["keep_a"], keep_D=r["keep_D"])
        arrs.update({"m_" + k: v for k, v in r["moments"].items()})
        for t, (a, d) in r["samples"].items():
            arrs[f"a_{t:g}"] = a
            arrs[f"D_{t:g}"] = d
        np.savez(os.path.join(outdir, f"var_{name}.npz"), **arrs)
        m = r["moments"]
        at = {}
        for t in r["samples"]:
            j = int(round((t - r["N"][0]) / (r["N"][1] - r["N"][0])))
            at[f"{t:g}"] = {k: float(v[j]) for k, v in m.items()}
        summ["variants"][name] = dict(config=VARIANTS[name], ndead=r["ndead"],
                                      wall_s=dt, at=at)
        print(f"{name}: dead {r['ndead']}, {dt:.1f} s", flush=True)
    summ["wall_s"] = time.time() - t0
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summ, f, indent=1)


if __name__ == "__main__":
    main()
