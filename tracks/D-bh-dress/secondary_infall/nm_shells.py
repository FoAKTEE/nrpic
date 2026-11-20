#!/usr/bin/env python3
"""Shell reference matched to a Newtonian-mode run (a reference calculation, decision 0010).

Uses the spherical-shell model of shells.py (radial shells through the centre, mode
"pass") with the set-up of an nm_ic.py particle file: eps, vacuum core R_w, dust edge
R_edge (mu_max = eps^2 R_edge^3/2), seed of mass 1, and one of three force laws:
  kernel   the mesh force measured for the clump (nm_field.py: f(q) = g_r r^2/M against
           q = r/dx, binned median), applied to the whole enclosed mass:
           a = -G M_enc sign(r) f(|r|/dx)/r^2 (f = 1 beyond the table, f ~ q^3 below it);
  plummer  a = -G M_enc r/(r^2 + s^2)^(3/2) with the fitted s_eff (or --soft);
  point    the same with a small s (the continuum limit for the comparison);
  hybrid   (wave 3) the kernel for the seed only, the dust's own gravity unsoftened outside
           r_d = --dsoft (default 0.5 dx) and that of a uniform sphere inside it:
           a = -G sign(r) [M_seed f(|r|/dx)/r^2 + M_dust,enc min(|r|, r_d)^3/(r^2 r_d^3)].
           The kernel law softens the dust like a point mass at the centre; the mesh force of
           a dust distribution that is smooth on the scale of a cell is accurate to second
           order (interface section 5.3), so the two laws bracket the run where the dust
           ball spans only a few cells (wave 3: R_edge = 4.1 dx at t = 0).
Snapshots at the nominal snapshot times of the run, t_k = k tlim/nsnap, or k snap_dt with
--snap_dt (code time; cosmic time t_i + t_k). Writes nm_shells_<label>.npz and .json into --out ($NRPIC_RUN_DIR).

Usage: python3 nm_shells.py --setup SETUP.json --law kernel --kernel kernel_nx128.txt
                            --dx 1.0625 --label N128_kernel [--nsnap 50] [--n 4000]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import shells  # noqa: E402


def make_kernel_accel(qtab, ftab, dx, hybrid_rd=0.0):
    lq, lf = np.log(qtab), np.log(np.maximum(ftab, 1e-300))
    q0, f0 = qtab[0], ftab[0]
    qmax = qtab[-1]

    def f_of(q):
        out = np.ones_like(q)
        lo = q < q0
        mid = (q >= q0) & (q <= qmax)
        out[lo] = f0 * (q[lo] / q0) ** 3
        out[mid] = np.exp(np.interp(np.log(q[mid]), lq, lf))
        return out

    def accel(r, m, j2, hasj, mbh, s2):
        ar = np.abs(r)
        order = np.argsort(ar, kind="stable")
        ms = m[order]
        cum = np.cumsum(ms) - 0.5 * ms
        menc = np.empty_like(cum)
        menc[order] = cum
        mt = mbh + menc
        d2 = r * r + s2                 # for the step control of shells.run only
        d = np.sqrt(d2)
        with np.errstate(divide="ignore", invalid="ignore"):
            if hybrid_rd > 0:
                fd = np.minimum(ar / hybrid_rd, 1.0) ** 3
                a = np.where(ar > 0, -np.sign(r) * (mbh * f_of(ar / dx) + menc * fd) / (r * r), 0.0)
            else:
                a = np.where(ar > 0, -mt * np.sign(r) * f_of(ar / dx) / (r * r), 0.0)
        return a, mt, d2, d
    return accel, f_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--setup", required=True)
    ap.add_argument("--law", choices=("kernel", "plummer", "point", "hybrid"), required=True)
    ap.add_argument("--dsoft", type=float, default=0.0,
                    help="hybrid: radius of the dust's uniform-sphere softening (default 0.5 dx)")
    ap.add_argument("--kernel", default="")
    ap.add_argument("--dx", type=float, default=0.0)
    ap.add_argument("--soft", type=float, default=0.0)
    ap.add_argument("--label", required=True)
    ap.add_argument("--nsnap", type=int, default=50)
    ap.add_argument("--snap_dt", type=float, default=0.0,
                    help="snapshot interval of the run (default tlim/nsnap); the last one at tlim")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--eta", type=float, default=0.02)
    a = ap.parse_args()
    if not a.out:
        sys.exit("no output directory")
    os.makedirs(a.out, exist_ok=True)
    with open(a.setup) as f:
        p = json.load(f)
    eps = p["eps"]
    c = dict(eps=eps, mode="pass", soft=0.0, r_abs=0.0, mu_core=eps**2 * p["r_w"]**3 / 2.0,
             mu_max=eps**2 * p["r_edge"]**3 / 2.0, n=a.n, a_end=p["a_end"], sigma=0.0, nj=1,
             vac_core=True)
    info = dict(label=a.label, law=a.law, setup=a.setup, cfg=c)
    if a.law in ("kernel", "hybrid"):
        tab = np.loadtxt(a.kernel)
        rd = (a.dsoft if a.dsoft > 0 else 0.5 * a.dx) if a.law == "hybrid" else 0.0
        accel, f_of = make_kernel_accel(tab[:, 0], tab[:, 1], a.dx, hybrid_rd=rd)
        shells.accel = accel
        c["soft"] = 0.61 * a.dx          # step control only (the fitted Plummer length)
        info.update(kernel=a.kernel, dx=a.dx, dust_soft_radius=rd)
    elif a.law == "plummer":
        c["soft"] = a.soft
    else:
        c["soft"] = a.soft if a.soft > 0 else 0.05
    info["soft"] = c["soft"]
    t_i = p["t_i"]
    if a.snap_dt > 0:
        tk = np.arange(1, int(np.floor(p["tlim"] / a.snap_dt + 1e-9)) + 1) * a.snap_dt
        if p["tlim"] - tk[-1] > 1e-6 * a.snap_dt:
            tk = np.append(tk, p["tlim"])
    else:
        tk = np.arange(1, a.nsnap + 1) * p["tlim"] / a.nsnap
    snaps_a = ((t_i + tk) / t_i) ** (2.0 / 3.0)
    snaps_a[-1] = p["a_end"]
    res = shells.run(c, snaps_a, eta=a.eta)
    st = res["st"]
    m0 = shells.setup(c)["m"]
    growth = []
    for s_ in res["snaps"]:
        growth.append(dict(t_code=s_["t"] - t_i, a=s_["a"],
                           mta=1.0 + float(m0[res["t_ta"] <= s_["t"]].sum()),
                           dress=float(s_["m"][s_["alive"] & (s_["ncross"] > 0)].sum())))
    info.update(nstep=res["nstep"], wall=res["wall"], growth=growth, n_shells=int(len(m0)),
                m_dust=float(m0.sum()))
    np.savez_compressed(
        os.path.join(a.out, f"nm_shells_{a.label}.npz"), r_i=st["r_i"], m0=m0, t_i=t_i,
        t_ta=res["t_ta"], r_ta=res["r_ta"], t_c=res["t_c"],
        snap_t=np.array([s["t"] - t_i for s in res["snaps"]]),
        snap_a=np.array([s["a"] for s in res["snaps"]]),
        snap_r=np.array([s["r"] for s in res["snaps"]]),
        snap_v=np.array([s["v"] for s in res["snaps"]]),
        snap_ncross=np.array([s["ncross"] for s in res["snaps"]]))
    with open(os.path.join(a.out, f"nm_shells_{a.label}.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps({k: v for k, v in info.items() if k != "growth"}, indent=1))
    for g in growth[::5] + [growth[-1]]:
        print("a/a_i = %.3f  M_ta = %.4f  dress = %.4f" % (g["a"], g["mta"], g["dress"]))


if __name__ == "__main__":
    main()
