#!/usr/bin/env python3
"""Card checks of work package dfix: the card executable of this branch against the exact
references and against the processor runs of the same set-ups (journal, "Card checks").

    card_judge.py CARD_RUN --cpu-t1 RUN --cpu-t3 RUN --cpu-t4 RUN [--fig PREFIX]

CARD_RUN   run directory of cases/card_checks.list (subdirectories t1_circ, t3_acc,
           t4_kepler)
--cpu-t1   processor run of cases/t1_regress_cpu.list (case b_new)
--cpu-t3   processor run of t3_accretion.py (case mesh)
--cpu-t4   processor run of t4_newton.py (case kepler)
Writes card_judge.json into $NRPIC_RUN_DIR (or CARD_RUN) and PREFIX_card.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t1_tracer as t1      # noqa: E402
import t3_accretion as t3   # noqa: E402
import t4_newton as t4      # noqa: E402


def common(a, b):
    """records of two trajectory arrays (t, tag, x, y, z, ...) at the same (t, tag)"""
    ka = {(round(r[0], 9), int(r[1])): i for i, r in enumerate(a)}
    pairs = [(ka[(round(r[0], 9), int(r[1]))], j) for j, r in enumerate(b)
             if (round(r[0], 9), int(r[1])) in ka]
    ia = np.array([p[0] for p in pairs], int)
    ib = np.array([p[1] for p in pairs], int)
    return a[ia], b[ib]


def judge_t1(card, cpu):
    a, m = t1.traj(os.path.join(card, "t1_circ"), "trc")
    b, _ = t1.traj(os.path.join(cpu, "b_new"), "trc")
    r = np.linalg.norm(a[:, 2:5], axis=1)
    e = t1.energy(a, m)
    lz = a[:, 2]*a[:, 6] - a[:, 3]*a[:, 5]
    ca, cb = common(a, b)
    d = np.linalg.norm(ca[:, 2:5] - cb[:, 2:5], axis=1)
    return {"records": int(len(a)), "t_end": float(a[-1, 0]),
            "r_min": float(r.min()), "r_max": float(r.max()),
            "E_relerr_max": float(np.abs(e/e[0] - 1.0).max()),
            "Lz_relerr_max": float(np.abs(lz/lz[0] - 1.0).max()),
            "common_records": int(len(ca)),
            "card_minus_cpu_position_max": float(d.max()),
            "bytes_equal_cpu": open(os.path.join(card, "t1_circ", "trc.traj.bin"), "rb").read()
            == open(os.path.join(cpu, "b_new", "trc.traj.bin"), "rb").read()}, (ca, d)


def judge_t3(card, cpu):
    ref = t3.reference()
    cc = t3.read_case(os.path.join(card, "t3_acc"))
    pc = t3.read_case(os.path.join(cpu, "mesh"))
    jc, jp = t3.judge(cc, ref), t3.judge(pc, ref)
    out = {"card": jc, "cpu_t_end": jp["t_end"], "card_vs_cpu": {}}
    for R, s in jc["spheres"].items():
        g, h = s["got"], jp["spheres"][R]["got"]
        out["card_vs_cpu"][R] = {
            "counts_equal": all(g[k] == h[k] for k in ("n_inside", "n_in", "n_out")),
            "mE_in_rel": float(g["mE_in"]/h["mE_in"] - 1.0) if h["mE_in"] else None,
            "mE_out_rel": float(g["mE_out"]/h["mE_out"] - 1.0) if h["mE_out"] else None}
    rc = cc["removed"][np.lexsort((cc["removed"][:, 1],))]
    rp = pc["removed"][np.lexsort((pc["removed"][:, 1],))]
    out["removed_card"], out["removed_cpu"] = int(len(rc)), int(len(rp))
    if len(rc) == len(rp):
        out["removal_time_max_diff"] = float(np.abs(rc[:, 0] - rp[:, 0]).max())
        out["removal_tags_equal"] = bool(np.all(rc[:, 1] == rp[:, 1]))
        out["removal_E_max_rel_diff"] = float(np.abs(rc[:, 17]/rp[:, 17] - 1.0).max())
    out["history_cols_max_rel_diff"] = None
    hc, hp = cc["hst"], pc["hst"]
    if hc.shape == hp.shape:
        den = np.maximum(np.abs(hp), 1e-300)
        rel = np.abs(hc - hp)/den
        rel[np.abs(hp) == 0.0] = np.abs(hc - hp)[np.abs(hp) == 0.0]
        out["history_cols_max_rel_diff"] = float(rel.max())
    return out, (cc, pc)


def snapshot_counts(path):
    b = open(path, "rb").read()
    t = float(np.frombuffer(b[8:16], dtype="<f8")[0])
    n = int(np.frombuffer(b[16:24], dtype="<i8")[0])
    off = 32 + 56*n + 16*n
    return t, [int(x) for x in np.frombuffer(b[off:off + 4*n], dtype="<i4")]


def judge_t4(card, cpu):
    d = os.path.join(card, "t4_kepler")
    tr = t4.read_traj(d, "npm")
    trc = t4.read_traj(os.path.join(cpu, "kepler"), "npm")
    hst = np.loadtxt(os.path.join(d, "npm.acc.hst"))
    t_end = float(hst[-1, 0])
    out = {"t_end": t_end, "orbits": []}
    curves = []
    for tag, (a, e, n1, n2) in enumerate(t4.KEPLER):
        s = tr[tr[:, 1] == tag]
        ex = t4.kepler_state(a, e, n1, n2, s[:, 0])
        err = np.linalg.norm(s[:, 2:5] - ex, axis=1)
        sc = trc[trc[:, 1] == tag]
        ca, cb = common(s, sc)
        dd = np.linalg.norm(ca[:, 2:5] - cb[:, 2:5], axis=1)
        out["orbits"].append({"a": a, "e": e, "t_last_record": float(s[-1, 0]),
                              "max_position_error": float(err.max()),
                              "card_minus_cpu_max": float(dd.max()),
                              "common_records": int(len(ca))})
        curves.append((s[:, 0], err, ca[:, 0], dd))
    ev = [t4.kepler_events(a, e, t_end, 1.0) for (a, e, _, _) in t4.KEPLER]
    out["sphere"] = {"n_in": float(hst[-1, 17]), "n_out": float(hst[-1, 20]),
                     "n_in_exact": float(sum(len(v["cross"]["in"]) for v in ev)),
                     "n_out_exact": float(sum(len(v["cross"]["out"]) for v in ev))}
    snaps = sorted(f for f in os.listdir(d) if f.startswith("npm.part."))
    ts, cnt = snapshot_counts(os.path.join(d, snaps[-1]))
    out["snapshot"] = {"time": ts, "peri_counts": cnt,
                       "peri_exact": [len(t4.kepler_events(a, e, ts, 1.0)["peri"])
                                      for (a, e, _, _) in t4.KEPLER]}
    # history: particles with at least one and at least two passages, against the exact
    # pericentre times, at every record
    peri = [np.array(v["peri"]) for v in ev]
    want1 = np.array([sum(int(np.any(p <= t)) for p in peri) for t in hst[:, 0]])
    want2 = np.array([sum(int(np.sum(p <= t) >= 2) for p in peri) for t in hst[:, 0]])
    # a passage is detected one step after the pericentre at the latest
    dt = float(hst[1, 0] - hst[0, 0]) if len(hst) > 1 else 0.0
    want1l = np.array([sum(int(np.any(p <= t - 2*dt)) for p in peri) for t in hst[:, 0]])
    want2l = np.array([sum(int(np.sum(p <= t - 2*dt) >= 2) for p in peri) for t in hst[:, 0]])
    ok1 = np.all((hst[:, 10] <= want1) & (hst[:, 10] >= want1l))
    ok2 = np.all((hst[:, 12] <= want2) & (hst[:, 12] >= want2l))
    out["history_passages_bracketed_by_exact"] = bool(ok1 and ok2)
    return out, curves


def figure(t1c, t3c, t4c, prefix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.17, top=0.95, wspace=0.38)
    ca, d = t1c
    ax[0].semilogy(ca[1:, 0], d[1:] + 1e-18, color=fs.PAL["blue"], label="T1 circular, m = 0")
    for tag, (t, err, tc, dd) in enumerate(t4c):
        ax[0].semilogy(tc[1:], dd[1:] + 1e-18, color=fs.SERIES[1 + tag], ls="--",
                       label=f"T4 Kepler, orbit {tag + 1}")
    ax[0].set_xlabel("time")
    ax[0].set_ylabel("|card - processor| position")
    ax[0].legend(loc="lower right", fontsize=7)
    cc, pc = t3c
    for k, R in enumerate(t3.SPHERES):
        c0 = 14 + 9*k
        ax[1].plot(cc["hst"][:, 0], cc["hst"][:, c0 + 3], color=fs.SERIES[k],
                   label=f"card, r = {R:g}, in")
        ax[1].plot(pc["hst"][:, 0], pc["hst"][:, c0 + 3], color="k", ls=":", lw=1.0)
        ax[1].plot(cc["hst"][:, 0], cc["hst"][:, c0 + 6], color=fs.SERIES[k], ls="--",
                   label=f"card, r = {R:g}, out")
        ax[1].plot(pc["hst"][:, 0], pc["hst"][:, c0 + 6], color="k", ls=":", lw=1.0)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel("crossings (T3; dotted: processors)")
    ax[1].legend(loc="center right", fontsize=7)
    for tag, (t, err, tc, dd) in enumerate(t4c):
        ax[2].semilogy(t[1:], err[1:], color=fs.SERIES[1 + tag], label=f"orbit {tag + 1}")
    ax[2].set_xlabel("time")
    ax[2].set_ylabel("T4 card: distance to Kepler orbit")
    ax[2].legend(loc="lower right", fontsize=7)
    fs.save(fig, prefix + "_card")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card")
    ap.add_argument("--cpu-t1", required=True)
    ap.add_argument("--cpu-t3", required=True)
    ap.add_argument("--cpu-t4", required=True)
    ap.add_argument("--fig")
    a = ap.parse_args()
    res = {}
    res["t1_circ"], t1c = judge_t1(a.card, a.cpu_t1)
    res["t3_acc"], t3c = judge_t3(a.card, a.cpu_t3)
    res["t4_kepler"], t4c = judge_t4(a.card, a.cpu_t4)
    outdir = os.environ.get("NRPIC_RUN_DIR") or a.card
    with open(os.path.join(outdir, "card_judge.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=str)
        fp.write("\n")
    print(json.dumps(res, indent=1, default=str))
    if a.fig:
        figure(t1c, t3c, t4c, a.fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
