#!/usr/bin/env python3
"""Test T1 of work package dfix: the tracer rule (a particle with m = 0).

    t1_tracer.py --regress RUN [--repro RUN ...] [--accept RUN] [--ref DIR] --out PREFIX

--regress  run directory of cases/t1_regress_cpu.list (static mesh metric, circular orbit)
--repro    run directories of cases/t1_repro_{cpu,gpu}.list (horizon_calib, m = 0 against
           m = 1e-300 with the release executable)
--accept   run directory of the 250 M card run of horizon_calib with the corrected
           executable; --ref the earlier run it is compared with (runs/puncture/single_v3)
Writes PREFIX.json (numbers) and PREFIX_*.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def traj(d, base):
    a = np.fromfile(os.path.join(d, base + ".traj.bin")).reshape(-1, 8)
    m = None
    p = os.path.join(d, base + ".trajmet.bin")
    if os.path.isfile(p):
        m = np.fromfile(p).reshape(-1, 17)
    return a, m


def energy(a, m, eps=1.0):
    """alpha W - beta^i u_i with the metric recorded at the particle"""
    g = np.zeros((len(a), 3, 3))
    g[:, 0, 0], g[:, 0, 1], g[:, 0, 2] = m[:, 6], m[:, 7], m[:, 8]
    g[:, 1, 1], g[:, 1, 2], g[:, 2, 2] = m[:, 9], m[:, 10], m[:, 11]
    g[:, 1, 0], g[:, 2, 0], g[:, 2, 1] = g[:, 0, 1], g[:, 0, 2], g[:, 1, 2]
    gi = np.linalg.inv(g)
    u = a[:, 5:8]
    usq = np.einsum("ni,nij,nj->n", u, gi, u)
    w = np.sqrt(eps + usq)
    return m[:, 2]*w - np.einsum("ni,ni->n", m[:, 3:6], u)


def areal_radius(a, m):
    """areal radius of the coordinate sphere through the particle on a spherically
    symmetric slice: R^2 = r^2 x (tangential part of the metric), from the trace:
    gamma_tt = (tr gamma - gamma_rr)/2 with gamma_rr = n^i n^j gamma_ij"""
    x = a[:, 2:5]
    r = np.linalg.norm(x, axis=1)
    n = x/r[:, None]
    g = np.zeros((len(a), 3, 3))
    g[:, 0, 0], g[:, 0, 1], g[:, 0, 2] = m[:, 6], m[:, 7], m[:, 8]
    g[:, 1, 1], g[:, 1, 2], g[:, 2, 2] = m[:, 9], m[:, 10], m[:, 11]
    g[:, 1, 0], g[:, 2, 0], g[:, 2, 1] = g[:, 0, 1], g[:, 0, 2], g[:, 1, 2]
    grr = np.einsum("ni,nij,nj->n", n, g, n)
    gtt = 0.5*(np.trace(g, axis1=1, axis2=2) - grr)
    return r*np.sqrt(gtt)


def regress(run, out, res):
    cases = {}
    for c in ("a_v03", "b_new", "c_new_meps", "d_new_null"):
        cases[c] = traj(os.path.join(run, c), "trc")
    r = {c: np.linalg.norm(v[0][:, 2:5], axis=1) for c, v in cases.items()}
    t = {c: v[0][:, 0] for c, v in cases.items()}
    a, m = cases["b_new"]
    e = energy(a, m)
    lz = a[:, 2]*a[:, 6] - a[:, 3]*a[:, 5]
    raw = {c: open(os.path.join(run, c, "trc.traj.bin"), "rb").read() for c in cases}
    hst = np.loadtxt(os.path.join(run, "a_v03", "trc.nrpic.hst"))
    res["regress"] = {
        "run": os.path.basename(run.rstrip("/")),
        "a_v03_last_record_time": float(t["a_v03"][-1]),
        "a_v03_last_radius": float(r["a_v03"][-1]),
        "a_v03_n_escaped_end": int(hst[-1, 18]),
        "b_new_r_min": float(r["b_new"].min()), "b_new_r_max": float(r["b_new"].max()),
        "b_new_records": int(len(a)), "b_new_t_end": float(t["b_new"][-1]),
        "b_new_E_relerr_max": float(np.abs(e/e[0] - 1.0).max()),
        "b_new_E0": float(e[0]),
        "b_new_Lz_relerr_max": float(np.abs(lz/lz[0] - 1.0).max()),
        "c_equals_b_bytes": raw["c_new_meps"] == raw["b_new"],
        "d_equals_a_bytes": raw["d_new_null"] == raw["a_v03"],
        "traj_bytes": {c: len(v) for c, v in raw.items()},
    }
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.16, top=0.95, wspace=0.22)
    ax[0].plot(t["a_v03"], r["a_v03"], color=fs.PAL["blue"], label="release core-v0.3")
    ax[0].plot(t["d_new_null"], r["d_new_null"], color=fs.PAL["yellow"], ls="--",
               label="corrected, zero_mass = null")
    ax[0].plot(t["b_new"], r["b_new"], color=fs.PAL["red"], label="corrected")
    ax[0].axhline(8.0, **fs.GUIDE)
    ax[0].set_xlim(0, 20)
    ax[0].set_ylim(7.5, 17.5)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel(r"coordinate radius $r/M$")
    ax[0].legend(loc="upper left")
    ax[1].plot(t["b_new"], (lz/lz[0] - 1.0)*1e6, color=fs.PAL["yellow"], lw=0.8,
               label=r"$10^6\,(L_z/L_{z,0} - 1)$")
    ax[1].plot(t["b_new"], (r["b_new"] - 8.0)*1e3, color=fs.PAL["red"],
               label=r"$10^3\,(r/M - 8)$")
    ax[1].plot(t["b_new"], (e/e[0] - 1.0)*1e6, color=fs.PAL["blue"], ls="--",
               label=r"$10^6\,(E/E_0 - 1)$")
    ax[1].axhline(1.2, **fs.MASK_LINE)
    ax[1].axhline(0.0, **fs.MASK_LINE)
    ax[1].set_xlim(0, 300)
    ax[1].set_ylim(-6, 9)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel("deviation (corrected, m = 0)")
    ax[1].legend(loc="upper center", ncol=3, fontsize=7, columnspacing=1.0, handlelength=1.5)
    fs.save(fig, out + "_regress")
    plt.close(fig)


def repro(runs, out, res):
    res["repro"] = []
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.95, wspace=0.26)
    psi = lambda r: 1.0 + 0.5/r
    uy = {0: 0.5837729484039818, 1: 0.4596785218238565, 2: 0.3891849859270371}
    r0 = {0: 6.0, 1: 8.0, 2: 10.0}
    styles = {"r1_m0": ("-", fs.PAL["blue"]), "r2_meps": ("-", fs.PAL["red"]),
              "r3_m0": ("--", fs.PAL["blue"]), "r4_meps": ("--", fs.PAL["red"])}
    for run in runs:
        for c in sorted(os.listdir(run)):
            if not os.path.isfile(os.path.join(run, c, "punc.traj.bin")):
                continue
            a, m = traj(os.path.join(run, c), "punc")
            hst = np.loadtxt(os.path.join(run, c, "punc.nrpic.hst"))
            rec = {"run": os.path.basename(run.rstrip("/")), "case": c,
                   "t_end": float(a[:, 0].max()),
                   "n_excised_first_record": int(hst[1, 16]),
                   "time_first_record": float(hst[1, 0]),
                   "n_excised_end": int(hst[-1, 16]), "n_escaped_end": int(hst[-1, 18]),
                   "tags_in_last_record": sorted(int(x) for x in a[a[:, 0] == a[:, 0].max(), 1]),
                   "speed": {}, "speed_null_predicted": {}, "speed_timelike_predicted": {},
                   "r_end": {}}
            for tag in range(6):
                s = a[a[:, 1] == tag]
                if len(s) < 2:
                    rec["speed"][tag] = None
                    continue
                rec["speed"][tag] = float(np.linalg.norm(s[1, 2:5] - s[0, 2:5])/(s[1, 0] - s[0, 0]))
                rec["r_end"][tag] = float(np.linalg.norm(s[-1, 2:5]))
                if tag in uy:
                    p4 = psi(r0[tag])**4
                    u2 = uy[tag]**2/p4
                    rec["speed_null_predicted"][tag] = 1.0/p4
                    rec["speed_timelike_predicted"][tag] = np.sqrt(u2/(1.0 + u2))/p4
                ls, col = styles.get(c, ("-", "k"))
                if tag < 3:
                    ax[0 if c.endswith("m0") else 1].plot(
                        s[:, 0], np.linalg.norm(s[:, 2:5], axis=1), ls=ls, color=fs.SERIES[tag],
                        label=(f"tag {tag}, " + ("processors" if c[1] in "12" else "card")))
            res["repro"].append(rec)
    for k, title in ((0, "release core-v0.3, m = 0"), (1, r"release core-v0.3, m = $10^{-300}$")):
        ax[k].set_xlabel(r"$t/M$")
        ax[k].set_ylabel(r"coordinate radius $r/M$")
        ax[k].legend(loc="upper left", ncol=2, fontsize=7, title=title)
    ax[1].set_ylim(5.5, 12.5)
    fs.save(fig, out + "_repro")
    plt.close(fig)


def accept(run, ref, out, res):
    a, m = traj(run, "punc")
    hst = np.loadtxt(os.path.join(run, "punc.nrpic.hst"))
    rec = {"run": os.path.basename(os.path.dirname(run.rstrip("/"))) or run,
           "t_end": float(a[:, 0].max()),
           "n_excised_end": int(hst[-1, 16]), "n_escaped_end": int(hst[-1, 18]), "tags": {}}
    refd = None
    if ref and os.path.isfile(os.path.join(ref, "punc.traj.bin")):
        refd = traj(ref, "punc")
        rec["reference"] = ref
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.95, wspace=0.26)
    for tag in range(6):
        sel = a[:, 1] == tag
        s, sm = a[sel], m[sel]
        R = areal_radius(s, sm)
        rc = np.linalg.norm(s[:, 2:5], axis=1)
        lz = s[:, 2]*s[:, 6] - s[:, 3]*s[:, 5]
        d = {"t_last": float(s[-1, 0]), "R0": float(R[0]),
             "R_dev_max": float(np.abs(R/R[0] - 1.0).max()),
             "r_coord_min": float(rc.min()), "r_coord_max": float(rc.max())}
        if abs(lz[0]) > 0:
            d["Lz_relerr_max"] = float(np.abs(lz/lz[0] - 1.0).max())
        if refd is not None:
            rs = refd[0][refd[0][:, 1] == tag]
            rm = refd[1][refd[0][:, 1] == tag]
            Rr = areal_radius(rs, rm)
            d["ref_t_last"] = float(rs[-1, 0])
            d["ref_R_dev_max"] = float(np.abs(Rr/Rr[0] - 1.0).max())
            if tag < 4:
                ax[0].plot(rs[:, 0], Rr/Rr[0] - 1.0, color=fs.SERIES[tag], ls=":", lw=1.0)
            else:
                ax[1].plot(rs[:, 0], Rr, color=fs.SERIES[tag - 4], ls=":", lw=1.0)
        rec["tags"][tag] = d
        if tag < 4:
            ax[0].plot(s[:, 0], R/R[0] - 1.0, color=fs.SERIES[tag], label=f"tag {tag}, $R_0$ = {R[0]:.2f}")
        else:
            ax[1].plot(s[:, 0], R, color=fs.SERIES[tag - 4], label=f"tag {tag}")
    ax[0].axhline(0.01, **fs.MASK_LINE)
    ax[0].axhline(-0.01, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel(r"$R/R_0 - 1$ (areal radius)")
    ax[0].legend(loc="lower left", ncol=2, fontsize=8)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel(r"areal radius $R/M$")
    ax[1].legend(loc="upper right")
    fs.save(fig, out + "_accept")
    plt.close(fig)
    res["accept"] = rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regress")
    ap.add_argument("--repro", action="append", default=[])
    ap.add_argument("--accept")
    ap.add_argument("--ref")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    res = {}
    if args.regress:
        regress(args.regress, args.out, res)
    if args.repro:
        repro(args.repro, args.out, res)
    if args.accept:
        accept(args.accept, args.ref, args.out, res)
    with open(args.out + ".json", "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
