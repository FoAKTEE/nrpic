#!/usr/bin/env python3
"""Lead's recheck L13 of the wave-2b box_rerun package (coll_energy = particle) from its
registered outputs, against the release runs of wave 2.

Own readers (rvlib.py) and, for T2, the lead's own wave-2 function rv_box.t2 pointed at
the new run directory; nothing of box_tests/scripts is imported. Prediction L13 in
tracks/C-sidm/JOURNAL.md (2026-11-19T15:15Z). Output: $NRPIC_RUN_DIR/rv_box2b.json and
rv_box2b.{png,pdf}.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rvlib as rv  # noqa: E402
import rv_box  # noqa: E402  (lead's wave-2 recheck; t2() reads the global R_T2)

S = rv.SCR
REL_T0B = os.path.join(S, "C-20261115-170155-13ff01f")
REL_T2 = os.path.join(S, "C-20261115-165500-c67e036")
REL_SMOKE = os.path.join(S, "C-20261115-172003-6422b6a", "cc1_kn1")
R1 = os.path.join(S, "C-20261119-141502-95f0200")
R2 = os.path.join(S, "C-20261119-141711-7db7a6a")
R3 = os.path.join(S, "C-20261119-141806-af19c1c")
R4 = os.path.join(S, "C-20261119-143041-f94e350")
R5 = os.path.join(S, "C-20261119-143049-0cf699a")
R5A = os.path.join(S, "C-20261119-145925-dbcfb9c")   # helper's final T12 analysis
R6 = os.path.join(S, "C-20261119-141431-a351ac7")
RT = os.path.join(S, "C-20261119-143146-226b0e0")
CASES = [f"T0b_{v}_s{s}" for v in ("plain", "sub", "f2") for s in (1, 2)]
INTCOLS = ("n_tested", "n_coll", "n_updated", "max_nsub", "n_trunc")
ALPHA0, PSI0 = 0.8, 1.1


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r1():
    out = {}
    for c in CASES:
        files = sorted(f for f in os.listdir(os.path.join(REL_T0B, c))
                       if f not in ("athena.log", "wall.json"))
        same = {f: sha(os.path.join(R1, c, f)) == sha(os.path.join(REL_T0B, c, f)) for f in files}
        out[c] = dict(files=len(files), identical=sum(same.values()), differing=[f for f, v in same.items() if not v])
    return out


def r2():
    out = {}
    for c in CASES:
        a = rv.read_hist(os.path.join(R1, c, "box.coll.hst"))
        b = rv.read_hist(os.path.join(R2, c, "box.coll.hst"))
        eq = {k: bool(np.array_equal(a[k], b[k])) for k in INTCOLS}
        out[c] = dict(records=int(a["n_coll"].size), int_columns_equal=eq,
                      sumP_max_rel=float(np.max(np.abs(b["sum_P"] / a["sum_P"] - 1))),
                      n_noroot=float(b["n_noroot"].sum()), n_balance=float(b["n_balance"].sum()),
                      max_dlam=float(b["max_dlam"].max()), dump_version_2=open(
                          os.path.join(R2, c, "box.coll_dump.20.bin"), "rb").read(8).decode(
                              "latin1"))
    return out


def r3():
    rv_box.R_T2 = R3
    new, cost_new = rv_box.t2()
    rv_box.R_T2 = REL_T2
    old, _ = rv_box.t2()
    out = {}
    for k in new:
        a = rv.read_hist(os.path.join(REL_T2, k, "box.coll.hst"))
        b = rv.read_hist(os.path.join(R3, k, "box.coll.hst"))
        out[k] = dict(ratio_new=new[k]["ratio"], z_b_new=new[k]["z_b"], z_a_new=new[k]["z_a"],
                      ratio_release=old[k]["ratio"], ratio_diff=new[k]["ratio"] - old[k]["ratio"],
                      int_columns_equal_all_steps=all(bool(np.array_equal(a[c], b[c])) for c in INTCOLS),
                      sumP_max_rel=float(np.max(np.abs(b["sum_P"] / a["sum_P"] - 1))),
                      theta_change=new[k]["theta_change"], T1=new[k]["T1"],
                      n_noroot=float(b["n_noroot"].sum()), n_balance=float(b["n_balance"].sum()),
                      max_dlam=float(b["max_dlam"].max()))
        print("R3", k, out[k]["ratio_new"], out[k]["ratio_diff"], out[k]["int_columns_equal_all_steps"],
              flush=True)
    return out


def r4():
    ref = rv.read_snap(rv.snaps(os.path.join(R4, "mb1"))[-1])
    order = np.argsort(ref["tag"])
    out = dict(final_time=ref["t"], n=ref["n"])
    for v in ("mb8", "mb64", "rst0", "rst1", "rst2", "seed8"):
        rd = os.path.join(R4, v)
        sn = [p for p in rv.snaps(rd) if abs(rv.read_snap(p)["t"] - ref["t"]) < 1e-12]
        if not sn:
            out[v] = dict(missing=True)
            continue
        s = rv.read_snap(sn[-1])
        o = np.argsort(s["tag"])
        diff = np.any(s["u"][o] != ref["u"][order], 1) | np.any(s["x"][o] != ref["x"][order], 1)
        out[v] = dict(bytes_identical=bool(s["raw_records"] == ref["raw_records"]),
                      frac_particles_differing=float(diff.mean()))
    h = rv.read_hist(os.path.join(R4, "mb1", "box.coll.hst"))
    out["collisions_mb1"] = float(h["n_coll"].sum())
    out["n_noroot"] = float(h["n_noroot"].sum())
    out["n_balance"] = float(h["n_balance"].sum())
    return out


def cmd_value(rd, key):
    for c in json.load(open(os.path.join(rd, "wall.json")))["cmd"]:
        if c.startswith(key + "="):
            return float(c.split("=", 1)[1])
    raise KeyError(key)


def r5():
    out = {}
    psi6 = PSI0 ** 6
    for th in ("0.1", "1.0"):
        for s in (1, 2):
            cur = os.path.join(R5, f"T12_th{th}_curved_s{s}")
            flt = os.path.join(R5, f"T12_th{th}_flat_s{s}")
            hc = rv.read_hist(os.path.join(cur, "box.coll.hst"))
            hf = rv.read_hist(os.path.join(flt, "box.coll.hst"))
            rec = {}
            for kind, rd, h in (("curved", cur, hc), ("flat", flt, hf)):
                s0 = rv.read_snap(rv.snaps(rd)[0])
                scale = PSI0 ** 2 if kind == "curved" else 1.0
                W = np.sqrt(1 + np.sum((s0["u"] / scale) ** 2, 1))
                theta, _ = rv.theta_and_se(W)
                N, M = s0["n"], float(s0["m"][0])
                sig, dt = cmd_value(rd, "particles/coll_sigma"), cmd_value(rd, "particles/dt")
                lapse = ALPHA0 if kind == "curved" else 1.0
                vol = 1.0 if kind == "curved" else (PSI0 ** 2) ** 3   # coordinate volume
                # count per step = (1/2) N n_proper sigma M <v_Mol> d(proper time)
                expect = 0.5 * N * (N / (psi6 if kind == "curved" else vol)) * M * sig \
                    * rv.vmol(theta) * lapse * dt
                sp = h["sum_P"]
                se = float(sp.std(ddof=1) / math.sqrt(sp.size))
                rec[kind] = dict(theta=theta, N=N, dt=dt, expect=expect,
                                 ratio=float(sp.mean() / expect),
                                 z=float((sp.mean() - expect) / se),
                                 rate_per_coord_time_volume=float(h["n_coll"].sum() / (sp.size * dt * vol)))
            same_t = bool(np.array_equal(hc["n_tested"], hf["n_tested"]))
            same_c = bool(np.array_equal(hc["n_coll"], hf["n_coll"]))
            out[f"{th}_s{s}"] = dict(curved=rec["curved"], flat=rec["flat"],
                                     n_tested_identical=same_t, n_coll_identical=same_c,
                                     collisions=float(hc["n_coll"].sum()),
                                     twin_rate_ratio=rec["curved"]["rate_per_coord_time_volume"]
                                     / rec["flat"]["rate_per_coord_time_volume"],
                                     alpha0_psi06=ALPHA0 * psi6,
                                     n_noroot=float(hc["n_noroot"].sum()),
                                     n_balance=float(hc["n_balance"].sum()),
                                     dn_coll_series=(hc["n_coll"] - hf["n_coll"]).tolist())
            print("R5", th, s, rec["curved"]["ratio"], rec["flat"]["ratio"], same_t, same_c, flush=True)
    hj = os.path.join(R5A, "t12_cpu.json")
    if os.path.exists(hj):
        out["_helper_json"] = os.path.relpath(hj, S)
    return out


def per_coll(h, key_d, key_s):
    n = h["n_coll"].sum()
    return float(h[key_d].sum() / n / h[key_s][0]), [float(h[key_d][i] / h["n_coll"][i] / h[key_s][i])
                                                       for i in range(h["n_coll"].size)]


def r6():
    out = {}
    for kn in ("1", "0.1", "0.01"):
        for mode in ("cell", "particle"):
            h = rv.read_hist(os.path.join(R6, f"king_kn{kn}_{mode}", "cc.coll.hst"))
            w, ws = per_coll(h, "dE_particles", "sum_MW_particles")
            hh, hs = per_coll(h, "dH_particles", "sum_MH_particles")
            out[f"kn{kn}_{mode}"] = dict(n_coll=h["n_coll"].tolist(), dW_per_coll=w, dW_steps=ws,
                                         dH_per_coll=hh, dH_steps=hs,
                                         n_noroot=float(h["n_noroot"].sum()),
                                         n_balance=float(h["n_balance"].sum()),
                                         max_dlam=float(h["max_dlam"].max()),
                                         sum_P_first=float(h["sum_P"][0]))
    # cell mode at Kn = 1 against the release smoke run (columns by number)
    a = np.loadtxt(os.path.join(REL_SMOKE, "cc.coll.hst"))
    b = np.loadtxt(os.path.join(R6, "king_kn1_cell", "cc.coll.hst"))
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    out["cell_vs_release"] = dict(records=n, cols_1_29_identical=bool(np.array_equal(a[:, :29], b[:, :29])),
                                  col30_max_abs=float(np.max(np.abs(a[:, 29] - b[:, 29]))),
                                  col31_max_abs=float(np.max(np.abs(a[:, 30] - b[:, 30]))))
    return out


def timing():
    t = json.load(open(os.path.join(RT, "timing.json")))
    r = t["runs"]
    pairs = r["cell_0"]["n_tested"]
    off = [r["off_0"]["wall"], r["off_1"]["wall"]]
    cell = [r["cell_0"]["wall"], r["cell_1"]["wall"]]
    part = [r["particle_0"]["wall"], r["particle_1"]["wall"]]
    pc = (np.mean(part) - np.mean(off)) / pairs
    cc = (np.mean(cell) - np.mean(off)) / pairs
    # spread: all four combinations of repeats
    combos = [(p - o) / (c - o) for p in part for c in cell for o in off]
    return dict(per_pair_particle=pc, per_pair_cell=cc, ratio=pc / cc,
                ratio_range=[min(combos), max(combos)], whole_run_ratio=np.mean(part) / np.mean(cell))


def figure(res, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(rv.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.1, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.2, top=0.9, wspace=0.38)
    # (a) T2(b) ratio, release and coll_energy = particle
    ks = sorted(res["R3"])
    x = np.arange(len(ks))
    ax[0].plot(x, [1e4 * (res["R3"][k]["ratio_release"] - 1) for k in ks], "o", color=fs.PAL["blue"],
               ms=5, label="release v0.3")
    ax[0].plot(x, [1e4 * (res["R3"][k]["ratio_new"] - 1) for k in ks], "x", color=fs.PAL["red"],
               ms=6, label="collisions-2, particle")
    ax[0].axhline(0, **fs.GUIDE)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels([k.replace("T2_th", "").replace("_plain_", "p").replace("_sub_", "s")
                           for k in ks], rotation=90, fontsize=6)
    ax[0].set_ylabel(r"T2(b): $10^4\,(\langle\Sigma P\rangle/{\rm expected}-1)$")
    ax[0].legend(fontsize=6, frameon=False)
    # (b) T12: analytic ratio of curved and flat runs; twin count differences
    r5 = {k: v for k, v in res["R5"].items() if not k.startswith("_")}
    for i, (k, v) in enumerate(sorted(r5.items())):
        ax[1].plot(i - 0.1, 1e4 * (v["curved"]["ratio"] - 1), "s", color=fs.PAL["red"], ms=5,
                   label="curved" if i == 0 else None)
        ax[1].plot(i + 0.1, 1e4 * (v["flat"]["ratio"] - 1), "o", color=fs.PAL["blue"], ms=5,
                   label="flat twin" if i == 0 else None)
        ax[1].text(i, -3.6, "max|dn|=%d" % int(np.max(np.abs(v["dn_coll_series"]))), fontsize=5.5,
                   ha="center")
    ax[1].axhline(0, **fs.GUIDE)
    ax[1].set_ylim(-4, 4)
    ax[1].set_xticks(range(len(r5)))
    ax[1].set_xticklabels(sorted(r5), fontsize=7)
    ax[1].set_ylabel(r"T12: $10^4\,(\langle\Sigma P\rangle/{\rm expected}-1)$")
    ax[1].set_xlabel(r"$\theta$, seed")
    ax[1].legend(fontsize=6, frameon=False, loc="upper left")
    # (c) King: per-collision change of the sums, both modes
    kns = ("1", "0.1", "0.01")
    for j, kn in enumerate(kns):
        c = res["R6"][f"kn{kn}_cell"]
        p = res["R6"][f"kn{kn}_particle"]
        for val, mk, col, lab in ((c["dW_per_coll"], "o", fs.PAL["red"], r"cell: $\Sigma MW_p$"),
                                  (c["dH_per_coll"], "s", fs.PAL["red"], r"cell: $\Sigma MH_p$"),
                                  (p["dW_per_coll"], "o", fs.PAL["blue"], r"particle: $\Sigma MW_p$"),
                                  (p["dH_per_coll"], "s", fs.PAL["blue"], r"particle: $\Sigma MH_p$")):
            ax[2].plot(j, abs(val), mk, color=col, mfc=col if val > 0 else "none", ms=5,
                       label=lab if j == 0 else None)
    ax[2].axhline(1.74e-10, **fs.GUIDE)
    ax[2].set_yscale("log")
    ax[2].set_xticks(range(3))
    ax[2].set_xticklabels([f"Kn = {k}" for k in kns], fontsize=7)
    ax[2].set_ylabel("|change per collision| / sum (filled: > 0)")
    ax[2].legend(fontsize=5.5, frameon=False, loc="center right")
    fs.save(fig, os.path.join(out, "rv_box2b"))


def main():
    out = rv.outdir()
    res = dict(R1=r1(), R2=r2(), R4=r4(), R5=r5(), R6=r6(), timing=timing())
    print(json.dumps({k: res[k] for k in ("R1", "R2", "R4", "R6", "timing")}, indent=1, default=float),
          flush=True)
    res["R3"] = r3()
    figure(res, out)
    json.dump(res, open(os.path.join(out, "rv_box2b.json"), "w"), indent=1, default=float)
    print("done")


if __name__ == "__main__":
    main()
