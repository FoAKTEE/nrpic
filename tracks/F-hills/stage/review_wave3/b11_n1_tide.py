#!/usr/bin/env python3
"""N1 (lead, batch 11): is the departure of the passage P1b (run A) from the binary alone (R16n +
B) the tide of the heavy hole at Newtonian order?

Newtonian reference from the start state of the P1b deck (positions, momenta and bare masses of
its <problem> block; the lead's own integrator lead_checks.newton_full, DOP853 at rtol 1e-12):
  N1   the three bodies, against the two members alone from the same state:
       Delta_N(t) = s_3(t) - s_2(t), s the separation of the members;
  N1e  the same with the members' relative velocity scaled so that the binary alone is eccentric
       with its first pericentre at the s_min of the NR binary alone (3.12 M, run
       F-20261124-130009-33bef4d), the centre-of-mass velocity unchanged; this tests how much
       Delta_N depends on the binary's eccentricity and phase.
NR: A - B from the analysis F-20261124-130009-33bef4d (b11_cards.json and the trackers).
Output (--out): b11_n1_tide.json, fig_b11_n1_tide.png/.pdf.
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/G0/checks"))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/review_wave3"))
sys.path.insert(0, os.path.join(WT, "python"))
import lead_checks as lc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import b11_cards as bc  # noqa: E402

DECK = os.path.join(WT, "tracks/F-hills/binary_conv/inputs/p1b_R16n.athinput")
T_END = 200.0


def sep(Y, n):
    X = Y[:, :3 * n].reshape(-1, n, 3)
    return np.linalg.norm(X[:, 0] - X[:, 1], axis=1), X


def scaled(m, x, p, f):
    """Members' velocities relative to their centre of mass scaled by f (momenta of M kept)."""
    v = p / m[:, None]
    mb = m[0] + m[1]
    vc = (m[0] * v[0] + m[1] * v[1]) / mb
    v2 = v.copy()
    v2[0] = vc + f * (v[0] - vc)
    v2[1] = vc + f * (v[1] - vc)
    return v2 * m[:, None]


def rp_two_body(m, x, p):
    """Pericentre of the members' Kepler orbit (bare masses) from the state."""
    mb = m[0] + m[1]
    r = x[0] - x[1]
    v = p[0] / m[0] - p[1] / m[1]
    E = 0.5 * v @ v - mb / np.linalg.norm(r)
    a = -mb / (2 * E)
    h = np.cross(r, v)
    e = np.sqrt(max(0.0, 1 - (h @ h) / (mb * a)))
    return a * (1 - e), a, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cards", default="/data/haiyangw/nrpic/scratch/F-hills/F-20261124-130009-33bef4d")
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    m, x, p = lc.read_athinput(DECK)
    nout = int(T_END / 0.05) + 1
    res = {"deck": DECK, "masses": m.tolist()}

    cases = {}
    rp0, a0, e0 = rp_two_body(m, x, p)
    res["binary_start"] = dict(rp=rp0, a=a0, e=e0)
    f_e = brentq(lambda f: rp_two_body(m, x, scaled(m, x, p, f))[0] - 3.12, 0.6, 1.0)
    rpe, ae, ee = rp_two_body(m, x, scaled(m, x, p, f_e))
    res["N1e_scale"] = dict(f=f_e, rp=rpe, a=ae, e=ee)
    cj = json.load(open(os.path.join(o.cards, "b11_cards.json")))["horizons"]
    mu = (cj["A"]["0"]["m_first"] + cj["A"]["1"]["m_first"]) / (cj["B"]["0"]["m_first"] + cj["B"]["1"]["m_first"])
    res["mu_mass_ratio_A_over_B"] = mu
    mm = m.copy()
    mm[:2] *= mu
    pe = scaled(m, x, p, f_e)
    for name, pp, m3, m2a, m2b in (("N1", p, m, m, m), ("N1e", pe, m, m, m),
                                   ("N1em", pe, None, mm, m), ("N1emt", pe, mm, None, m)):
        t = np.linspace(0.0, T_END, nout)
        _, Y2 = lc.newton_full(m2b[:2], x[:2], pp[:2], t_end=T_END, nout=nout)
        s2, _ = sep(Y2, 2)
        if m3 is not None:
            _, Y3 = lc.newton_full(m3, x, pp, t_end=T_END, nout=nout)
            s3, X3 = sep(Y3, 3)
        else:                               # members alone with the other masses
            _, Y3 = lc.newton_full(m2a[:2], x[:2], pp[:2], t_end=T_END, nout=nout)
            s3, _ = sep(Y3, 2)
            X3 = np.concatenate([Y3[:, :6].reshape(-1, 2, 3), np.full((nout, 1, 3), np.nan)], axis=1)
        rcm = np.linalg.norm(0.5 * (X3[:, 0] + X3[:, 1]) - X3[:, 2], axis=1)  # equal masses
        d = s3 - s2
        cases[name] = dict(t=t, s3=s3, s2=s2, d=d, rcm=rcm)
        res[name] = dict(
            delta_at={f"{T:g}": float(np.interp(T, t, d)) for T in (10, 20, 30, 40, 50, 60, 70, 80)},
            s3_at={f"{T:g}": float(np.interp(T, t, s3)) for T in (20, 40, 60, 80, 100)},
            s2_at={f"{T:g}": float(np.interp(T, t, s2)) for T in (20, 40, 60, 80, 100)},
            rcm_at={f"{T:g}": float(np.interp(T, t, rcm)) for T in (0, 20, 40, 60, 80, 100)}
            if np.isfinite(rcm).any() else None,
            t_cm_peri=float(t[np.nanargmin(rcm)]) if np.isfinite(rcm).any() else None,
            rcm_min=float(np.nanmin(rcm)) if np.isfinite(rcm).any() else None,
            s2_min=float(s2.min()), t_s2_min=float(t[np.argmin(s2)]))

    # NR A - B
    TR = {k: bc.trackers(k) for k in ("A", "B")}
    tA, sA, _, _ = bc.pair(TR["A"])
    tB, sB, _, _ = bc.pair(TR["B"])
    k = tA <= tB[-1]
    dNR = sA[k] - np.interp(tA[k], tB, sB)
    res["NR_A_minus_B_at"] = {f"{T:g}": float(np.interp(T, tA[k], dNR)) for T in (10, 20, 30, 40, 50, 60)}
    # relative: Delta / s_alone
    res["N1_rel_at60"] = res["N1"]["delta_at"]["60"] / res["N1"]["s2_at"]["60"]
    res["N1e_rel_at60"] = res["N1e"]["delta_at"]["60"] / res["N1e"]["s2_at"]["60"]
    res["NR_rel_at60"] = res["NR_A_minus_B_at"]["60"] / float(np.interp(60, tB, sB))
    with open(os.path.join(o.out, "b11_n1_tide.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(6.4, 6.0), sharex=True)
    axs[0].plot(tB, sB, color=fs.PAL["green"], lw=1.4, label="NR binary alone m/16 (R16n + B)")
    axs[0].plot(tA, sA, color=fs.PAL["blue"], lw=1.4, label="NR passage P1b m/16 (A)")
    for name, ls in (("N1", "--"), ("N1e", ":")):
        c = cases[name]
        axs[0].plot(c["t"], c["s2"], color="0.4", ls=ls, lw=1.0, label=f"{name} Newton binary alone")
        axs[0].plot(c["t"], c["s3"], color="k", ls=ls, lw=1.0, label=f"{name} Newton with $M$")
    axs[0].set_ylabel(r"separation $s$ [$M$]")
    axs[0].set_xlim(0, 110)
    axs[0].set_ylim(0, 6)
    axs[0].legend(fontsize=6.5, ncol=2, loc="lower left")
    axs[1].plot(tA[k], dNR, color=fs.PAL["blue"], lw=1.6, label="NR: A $-$ (R16n + B)")
    for name, ls, cc, lab in (("N1", "--", "k", "N1 tide, deck start"),
                              ("N1e", ":", "k", "N1e tide, eccentric start"),
                              ("N1em", "-.", fs.PAL["orange"], r"N1em members' masses $\times\mu$, no $M$"),
                              ("N1emt", "-", fs.PAL["red"], r"N1emt masses $\times\mu$ and tide")):
        c = cases[name]
        axs[1].plot(c["t"], c["d"], color=cc, ls=ls, lw=1.0, label=lab + " (Newton)")
    axs[1].axhline(0, color="0.6", lw=0.6)
    axs[1].set_ylabel(r"$\Delta s$ [$M$]")
    axs[1].set_xlabel(r"$t$ [$M$]")
    axs[1].set_ylim(-1.5, 0.5)
    axs[1].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b11_n1_tide"))
    print(json.dumps({kk: res[kk] for kk in ("binary_start", "N1e_scale", "mu_mass_ratio_A_over_B", "N1",
                                             "N1e", "N1em", "N1emt", "NR_A_minus_B_at",
                                             "N1_rel_at60", "N1e_rel_at60", "NR_rel_at60")}, indent=1, default=str))


if __name__ == "__main__":
    main()
