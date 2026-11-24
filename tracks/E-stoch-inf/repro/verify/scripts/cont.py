#!/usr/bin/env python3
"""Fresh verifier, update pass (JOURNAL entry 5): the five continued runs, from their raw outputs,
with my own readers (lattice.py) and my own reference (compare.py for the MS solution).

  joins        record lines at common cycles (each original against each of its continuations),
               steps across each seam, dumps at common indices (bytes), the joined records
  signflip     RNC256 against the joined RSF256 record, matched by cycle, over the full span;
               maxima of the proper run (records)
  constraints  <|H|/[H]>, <|M|/[M]> recomputed from every dump of RNC256 and RSF256 (my [H] where
               the dump has At), against the dumped magnitudes and the record line of that cycle
  convrec      Fig. 8: time-matched finer/coarser ratios of the record means 32 -> 256, entry
               maxima of the USR H with the box mean and their orders, late values
  convspec     Fig. 7: R^NR at N_f of the four SR rungs against the code's lockstep record and
               (compare.py) my MS solution; reference-free per-mode differences between rungs
  backreact    SR level 2 against level 0 at N_f (dump 17) and at t = 7.5 (dump 15); USR at N_f;
               against P1:520's bound 1e-4 (\\textpertenthousand)

Usage: python cont.py --out DIR [--only joins signflip ...] [--workers 3]
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "python"))
import lattice  # noqa: E402
import figstyle  # noqa: E402
from nrpic import rng  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
L = 2*np.pi
# run: (base name, original, [continuations in order])
RUNS = {
    "RSF256": ("sr", "E-20261123-035925-8439d79",
               ["E-20261124-130529-da8c917", "E-20261124-201031-4c41e7b", "E-20261124-202134-0b1ce0c",
                "E-20261124-214913-5956891"]),
    "RNC256": ("sr", "E-20261123-045030-c20bcb3", ["E-20261124-130629-61fe0b0"]),
    "CL256U": ("usr", "E-20261123-065855-265732a", ["E-20261124-130711-a5dec67", "E-20261124-201048-33a3a39"]),
    "CL256S": ("sr", "E-20261123-090727-4b6e5a5", ["E-20261124-130952-4be980b"]),
    "AL2S": ("sr256_l2", "E-20261123-152119-38957ba", ["E-20261124-131359-49afe29"]),
}
RUNG = f"{S}/E-20261123-020704-2b99463"
LATRUNG = f"{S}/E-20261124-183222-02ff27c"   # my lattice.py npz of the 32-128 SR rungs (section 2)
USF256 = f"{S}/E-20261123-021204-2f573ec/usr.sf.con.hst"
MODES64 = f"{ROOT}/tracks/E-stoch-inf/ladder/inputs/modes_n64.txt"
ABL = {"l0S": f"{S}/E-20261123-153347-18e7c21/sr256_l0m", "l2S15": f"{S}/E-20261123-152119-38957ba/sr256_l2",
       "l2S17": f"{S}/E-20261124-131359-49afe29/sr256_l2", "l0U": f"{S}/E-20261123-164235-49b0945/usr256_l0m",
       "l2U": f"{S}/E-20261123-153146-d965002/usr256_l2"}
SMOOTH = {0: "time", 2: "efolds", 3: "<|H|/[H]>", 6: "<|M|/[M]>", 16: "<phi>", 18: "<K>"}


def rec(path):
    return np.loadtxt(path, comments="#", ndmin=2)


def by_cycle(R):
    """cycle -> row; duplicated cycles (restarts inside a chain) must agree; keep the last."""
    d, dup = {}, 0.0
    for row in R:
        c = int(round(row[1]))
        if c in d:
            dup = max(dup, float(np.max(np.abs(d[c] - row)/np.maximum(np.abs(d[c]), 1e-300))))
        d[c] = row
    return d, dup


def relmax(a, b):
    den = np.maximum(np.abs(a), np.abs(b))
    m = den > 0
    return float(np.max(np.abs(a - b)[m]/den[m])) if m.any() else 0.0


def joined(name):
    base, orig, conts = RUNS[name]
    R0, dup0 = by_cycle(rec(f"{S}/{orig}/{base}.sf.con.hst"))
    j = dict(R0)
    info = dict(original=orig, orig_cycles=[min(R0), max(R0)], orig_duplicate_maxrel=dup0, conts=[])
    for c in conts:
        Rc, dupc = by_cycle(rec(f"{S}/{c}/{base}.sf.con.hst"))
        common = sorted(set(Rc) & set(j))
        diffs = [relmax(j[k], Rc[k]) for k in common]
        info["conts"].append(dict(run=c, cycles=[min(Rc), max(Rc)], n_common=len(common),
                                  common_maxrel=max(diffs) if diffs else None,
                                  n_common_not_identical=int(sum(d > 0 for d in diffs)),
                                  dup_maxrel=dupc))
        j.update(Rc)        # the later run supersedes at common cycles (identical if bit-exact)
    cyc = np.array(sorted(j))
    J = np.array([j[k] for k in cyc])
    info["joined_cycles"] = [int(cyc[0]), int(cyc[-1])]
    info["joined_gaps"] = int(np.sum(np.diff(cyc) != 1))
    info["joined_t_N_end"] = [float(J[-1, 0]), float(J[-1, 2])]
    return J, info


def seam_steps(J, c0):
    """Residual of linear extrapolation across cycle c0 against the same residual nearby."""
    cyc = J[:, 1].astype(int)
    i = int(np.where(cyc == c0)[0][0])
    out = {}
    if i < 3 or i > len(J) - 8:
        return out
    for col, lab in SMOOTH.items():
        x = J[:, col]
        if lab.startswith("<|"):
            x = np.log(x)
        r = np.abs(x[2:] - 2*x[1:-1] + x[:-2])     # r[k] centred at k + 1
        k = i - 1
        nb = np.r_[r[max(k - 10, 0):k], r[k + 1:k + 11]]
        med = float(np.median(nb))
        out[lab] = float(r[k]/med) if med > 0 else (0.0 if r[k] == 0 else float("inf"))
    return out


def dump_bytes_equal(a, b):
    if not (os.path.exists(a) and os.path.exists(b)):
        return None
    return subprocess.run(["cmp", "-s", a, b]).returncode == 0


def joins(out):
    res = {}
    fig, axs = plt.subplots(2, 3, figsize=(figstyle.FULL_WIDTH, 4.6))
    for (name, (base, orig, conts)), ax in zip(RUNS.items(), axs.ravel()):
        J, info = joined(name)
        info["seams"] = {}
        for c in conts:
            Rc = rec(f"{S}/{c}/{base}.sf.con.hst")
            c0 = int(Rc[0, 1])
            info["seams"][c] = dict(first_cycle=c0, step_over_neighbours=seam_steps(J, c0))
        # dumps at common indices
        dd = {}
        od = {os.path.basename(p): p for p in glob.glob(f"{S}/{orig}/{base}.sf.*.dump")}
        for c in conts:
            for p in sorted(glob.glob(f"{S}/{c}/{base}.sf.*.dump")):
                b = os.path.basename(p)
                if b in od:
                    dd[f"{c}:{b}"] = dump_bytes_equal(od[b], p)
        for c1 in conts:
            for c2 in conts:
                if c1 < c2:
                    for p in sorted(glob.glob(f"{S}/{c1}/{base}.sf.*.dump")):
                        q = f"{S}/{c2}/{os.path.basename(p)}"
                        if os.path.exists(q):
                            dd[f"{c1}~{c2}:{os.path.basename(p)}"] = dump_bytes_equal(p, q)
        info["dumps_common_identical"] = dd
        res[name] = info
        np.savetxt(os.path.join(out, f"joined_{name}.txt"), J)
        R0 = rec(f"{S}/{orig}/{base}.sf.con.hst")
        ax.semilogy(R0[:, 2], R0[:, 3], color=figstyle.SERIES[0], lw=3, alpha=0.4, label="original H")
        ax.semilogy(R0[:, 2], R0[:, 6], color=figstyle.SERIES[1], lw=3, alpha=0.4, label="original M")
        for c, ls in zip(conts, ("-", "--", ":", "-.")):
            Rc = rec(f"{S}/{c}/{base}.sf.con.hst")
            ax.semilogy(Rc[:, 2], Rc[:, 3], color=figstyle.SERIES[0], lw=0.8, ls=ls)
            ax.semilogy(Rc[:, 2], Rc[:, 6], color=figstyle.SERIES[1], lw=0.8, ls=ls)
            ax.axvline(Rc[0, 2], **figstyle.MASK_LINE)
        ax.set_title(name, fontsize=8)
        ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
    axs[0, 0].legend(fontsize=5)
    # zoom on the AL2S seam (no overlap)
    ax = axs.ravel()[5]
    J, _ = joined("AL2S")
    s = (J[:, 1] > 1200) & (J[:, 1] < 1260)
    ax.plot(J[s, 1], J[s, 3]/J[s, 3].mean(), ".-", ms=2, color=figstyle.SERIES[0], label="H/[H] (scaled)")
    ax.plot(J[s, 1], J[s, 6]/J[s, 6].mean(), ".-", ms=2, color=figstyle.SERIES[1], label="M/[M] (scaled)")
    ax.axvline(1227.5, **figstyle.MASK_LINE)
    ax.set_xlabel("cycle")
    ax.set_title("AL2S seam, cycles 1200-1260", fontsize=8)
    ax.legend(fontsize=5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_joins.png"), dpi=150)
    plt.close(fig)
    return res


def signflip(out):
    P, ip = joined("RSF256")
    F, iff = joined("RNC256")
    cp = {int(r[1]): r for r in P}
    rows = [(r, cp[int(r[1])]) for r in F if int(r[1]) in cp and int(r[1]) > 0]
    f = np.array([a for a, b in rows])
    p = np.array([b for a, b in rows])
    tmis = float(np.max(np.abs(f[:, 0] - p[:, 0])))
    # the flipped run's last step is shortened to reach tlim: there interpolate the proper run in t
    bad = np.abs(f[:, 0] - p[:, 0]) > 1e-12
    for col in range(3, P.shape[1]):
        if np.all(P[:, col] > 0):
            p[bad, col] = np.exp(np.interp(f[bad, 0], P[:, 0], np.log(P[:, col])))
    p[bad, 0] = f[bad, 0]
    res = dict(n_matched=len(rows), max_time_mismatch=tmis, n_lines_interpolated=int(bad.sum()),
               flipped_end_N=float(F[-1, 2]), flipped_end_t=float(F[-1, 0]),
               proper_joined_end_N=float(P[-1, 2]))
    ratio = f[:, 3]/p[:, 3]
    ratioA = f[:, 11]/p[:, 11]          # <|H|> absolute
    N = f[:, 2]
    for lab, sel in (("N_0.02_end", N > 0.02), ("N_0.5_end", N >= 0.5),
                     ("N_0.5_ln64", (N >= 0.5) & (N <= np.log(64.0)))):
        k = np.argmin(ratio[sel])
        res[lab] = dict(n=int(sel.sum()), ratio_median=float(np.median(ratio[sel])),
                        ratio_min=float(ratio[sel].min()), N_at_min=float(N[sel][k]),
                        ratio_max=float(ratio[sel].max()),
                        absH_ratio_median=float(np.median(ratioA[sel])),
                        absH_ratio_min=float(ratioA[sel].min()))
    res["flip_H_over_Hmag_max"] = float(F[:, 3].max())
    res["flip_N_of_H_max"] = float(F[np.argmax(F[:, 3]), 2])
    res["flip_M_over_Mmag_max"] = float(F[:, 6].max())
    res["flip_N_of_M_max"] = float(F[np.argmax(F[:, 6]), 2])
    res["flip_absH_max"] = float(F[:, 11].max())
    res["flip_Hmag_mean_range"] = [float(F[:, 9].min()), float(F[:, 9].max())]
    # ratio of means against mean of ratios (both runs)
    for lab, X in (("proper", P), ("flipped", F)):
        q = X[:, 5]/X[:, 3]
        res[f"{lab}_ratio_of_means_over_mean_of_ratios"] = [float(q.min()), float(q.max())]
        qm = X[:, 8]/X[:, 6]
        res[f"{lab}_M_ratio_of_means_over_mean_of_ratios"] = [float(qm.min()), float(qm.max())]
    w = P[:, 2] <= np.log(64.0)
    res["proper_H_max_N_le_ln64"] = float(P[w, 3].max())
    res["proper_N_of_H_max"] = float(P[w, 2][np.argmax(P[w, 3])])
    res["proper_M_max_N_le_ln64"] = float(P[w, 6].max())
    res["proper_N_of_M_max"] = float(P[w, 2][np.argmax(P[w, 6])])
    w2 = P[:, 2] <= F[-1, 2] + 1e-9
    res["proper_M_max_N_le_flip_end"] = float(P[w2, 6].max())
    res["proper_H_max_whole_joined"] = float(P[:, 3].max())
    res["proper_N_of_H_max_whole"] = float(P[np.argmax(P[:, 3]), 2])
    res["proper_M_max_whole_joined"] = float(P[:, 6].max())
    res["proper_N_of_M_max_whole"] = float(P[np.argmax(P[:, 6]), 2])
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.9))
    ax = axs[0]
    ax.semilogy(P[:, 2], P[:, 3], color=figstyle.SERIES[0], label=r"proper $\langle|H|/[H]\rangle$")
    ax.semilogy(F[:, 2], F[:, 3], color=figstyle.SERIES[0], ls="--", label="flipped")
    ax.semilogy(P[:, 2], P[:, 6], color=figstyle.SERIES[1], label=r"proper $\langle|M|/[M]\rangle$")
    ax.semilogy(F[:, 2], F[:, 6], color=figstyle.SERIES[1], ls="--", label="flipped")
    ax.axvline(np.log(64.0), **figstyle.MASK_LINE)
    ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
    ax.set_title("SR 256$^3$: RNC256 against joined RSF256", fontsize=8)
    ax.legend(fontsize=5)
    ax = axs[1]
    ax.semilogy(N, ratio, color=figstyle.SERIES[0], label=r"$\langle|H|/[H]\rangle$ flipped/proper")
    ax.semilogy(N, ratioA, color=figstyle.SERIES[2], ls=":", label=r"$\langle|H|\rangle$ flipped/proper")
    ax.axhline(1e3, **figstyle.MASK_LINE)
    ax.axvline(0.5, **figstyle.MASK_LINE)
    ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
    ax.legend(fontsize=5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_signflip_full.png"), dpi=150)
    plt.close(fig)
    return res


def dump_constraints(path):
    h = lattice.read_header(path)
    names = h["names"]
    want = [q for q in ("H", "Mx", "My", "Mz", "Hmag", "Mmag", "K", "E", "Axx", "Axy", "Axz", "Ayy",
                        "Ayz", "Azz") if q in names]
    _, f = lattice.read_fields(path, want)
    H = f["H"]
    Mabs = np.sqrt(f["Mx"]**2 + f["My"]**2 + f["Mz"]**2)
    r = dict(file=path, time=h["time"], cycle=h["cycle"])
    r["mean_absH_over_Hmag"] = float((np.abs(H)/f["Hmag"]).mean())
    r["mean_absH"] = float(np.abs(H).mean())
    r["mean_Hmag"] = float(f["Hmag"].mean())
    mm = f["Mmag"] > 0
    r["mean_absM_over_Mmag"] = float(np.where(mm, Mabs/np.where(mm, f["Mmag"], 1), 0).mean())
    r["max_absH_over_Hmag"] = float((np.abs(H)/f["Hmag"]).max())
    base = (2.0/3.0)*f["K"]**2 + np.abs(16*np.pi*f["E"])
    r["min_Hmag_minus_KK_E_over_Hmag"] = float(((f["Hmag"] - base)/f["Hmag"]).min())
    if "Axx" in f:
        AA = (f["Axx"]**2 + f["Ayy"]**2 + f["Azz"]**2 + 2*(f["Axy"]**2 + f["Axz"]**2 + f["Ayz"]**2))
        R3 = H - (2.0/3.0)*f["K"]**2 + AA + 16*np.pi*f["E"]
        Hm = np.abs(R3) + (2.0/3.0)*f["K"]**2 + AA + np.abs(16*np.pi*f["E"])
        r["max_rel_Hmine_vs_Hmag"] = float(np.abs(Hm/f["Hmag"] - 1).max())
        r["mean_absH_over_Hmine"] = float((np.abs(H)/Hm).mean())
    return r


def constraints(out):
    res = {}
    for name in ("RNC256", "RSF256"):
        base, orig, conts = RUNS[name]
        J, _ = joined(name)
        cmap = {int(r[1]): r for r in J}
        dumps = sorted(glob.glob(f"{S}/{orig}/{base}.sf.*.dump"))
        last = conts[-1]
        dumps += sorted(glob.glob(f"{S}/{last}/{base}.sf.*.dump"))
        rows = []
        for p in dumps:
            r = dump_constraints(p)
            row = cmap.get(int(r["cycle"]))
            if row is not None:
                r["rec_H"] = float(row[3])
                r["rec_M"] = float(row[6])
                r["rel_H_vs_record"] = float(abs(r["mean_absH_over_Hmag"]/row[3] - 1))
                r["rel_M_vs_record"] = float(abs(r["mean_absM_over_Mmag"]/row[6] - 1))
                r["rel_Hmag_vs_record"] = float(abs(r["mean_Hmag"]/row[9] - 1))
                r["rel_absH_vs_record"] = float(abs(r["mean_absH"]/row[11] - 1))
            rows.append(r)
            print(name, os.path.basename(p), {k: v for k, v in r.items() if k.startswith("rel")},
                  flush=True)
        res[name] = dict(n_dumps=len(rows), rows=rows,
                         max_rel_H_vs_record=max(r.get("rel_H_vs_record", np.nan) for r in rows),
                         max_rel_M_vs_record=max(r.get("rel_M_vs_record", np.nan) for r in rows),
                         max_rel_Hmag_vs_record=max(r.get("rel_Hmag_vs_record", np.nan) for r in rows),
                         max_rel_Hmine_vs_Hmag=max(r.get("max_rel_Hmine_vs_Hmag", 0.0) for r in rows),
                         min_Hmag_minus_KK_E=min(r["min_Hmag_minus_KK_E_over_Hmag"] for r in rows))
    return res


def rung_records(case):
    out = {}
    for n in (32, 64, 128):
        out[n] = rec(glob.glob(f"{RUNG}/C{n}{case}/*.sf.con.hst")[0])
    out[256] = joined({"S": "CL256S", "U": "CL256U"}[case])[0]
    return out


def tm_ratio(fine, coarse, col, lo=0.5, hi=np.log(8.0)):
    s = (fine[:, 2] >= lo) & (fine[:, 2] <= hi)
    c = np.interp(fine[s, 0], coarse[:, 0], np.log(coarse[:, col]))
    return float(np.median(fine[s, col]/np.exp(c)))


def convrec(out):
    res = {}
    fig, axs = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.8))
    for case, ax in zip(("S", "U"), axs[:2]):
        R = rung_records(case)
        cols = {"S": {"H": 3, "M": 6}, "U": {"M": 6, "H-<H>": 24, "H": 3}}[case]
        d = {}
        for q, col in cols.items():
            d[q] = {f"{f}/{c}": tm_ratio(R[f], R[c], col) for c, f in ((32, 64), (64, 128), (128, 256))}
            for n in R:
                x = R[n]
                ent = (x[:, 2] > 0.05) & (x[:, 2] <= np.log(8.0))
                v_end_entry = float(np.exp(np.interp(np.log(8.0), x[:, 2], np.log(x[:, col]))))
                d[q][f"entry_max_{n}"] = float(x[ent, col].max())
                d[q][f"N_entry_max_{n}"] = float(x[ent, 2][np.argmax(x[ent, col])])
                d[q][f"final_{n}"] = float(x[-1, col])
                d[q][f"N_final_{n}"] = float(x[-1, 2])
                d[q][f"final_over_entry_end_{n}"] = float(x[-1, col]/v_end_entry)
                late = x[:, 2] > np.log(8.0)
                d[q][f"late_max_over_entry_end_{n}"] = float(x[late, col].max()/v_end_entry)
            for c, f in ((32, 64), (64, 128), (128, 256)):
                d[q][f"order_entry_max_{c}_{f}"] = float(np.log2(d[q][f"entry_max_{c}"]/d[q][f"entry_max_{f}"]))
        res[case] = d
        for n, ls in zip((32, 64, 128, 256), (":", "-.", "--", "-")):
            x = R[n]
            ax.semilogy(x[:, 2], x[:, 3] if case == "S" else x[:, 24], color=figstyle.SERIES[0], ls=ls,
                        lw=1.0, label=f"H, {n}" if case == "S" else f"H-<H>, {n}")
            ax.semilogy(x[:, 2], x[:, 6], color=figstyle.SERIES[1], ls=ls, lw=1.0, label=f"M, {n}")
        ax.axvline(0.5, **figstyle.MASK_LINE)
        ax.axvline(np.log(8.0), **figstyle.MASK_LINE)
        ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
        ax.set_title({"S": "SR rungs 32-256", "U": "USR rungs 32-256"}[case], fontsize=8)
        ax.legend(fontsize=4.5, ncol=2)
    U = rec(USF256)
    ent = (U[:, 2] > 0.05) & (U[:, 2] <= np.log(8.0))
    res["USF256_H_entry_max"] = float(U[ent, 3].max())
    res["USF256_N_of_max"] = float(U[ent, 2][np.argmax(U[ent, 3])])
    ax = axs[2]
    for case, mk in (("S", "o"), ("U", "s")):
        for q, c in zip(res[case], figstyle.SERIES):
            r = [res[case][q][k] for k in ("64/32", "128/64", "256/128")]
            ax.plot([1, 2, 3], r, mk + "-", ms=3, color=c, label=f"{case} {q}")
    ax.axhline(1.0, **figstyle.MASK_LINE)
    ax.set_xticks([1, 2, 3], ["64/32", "128/64", "256/128"])
    ax.set_yscale("log")
    ax.set_ylabel("median finer/coarser, $0.5\\leq N\\leq\\ln 8$")
    ax.legend(fontsize=5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_convrec_256.png"), dpi=150)
    plt.close(fig)
    return res


def alphas(n, seed):
    z = rng.normal2(seed=seed, stream=rng.stochastic_mode_stream(0),
                    entity=rng.mode_entity(n[:, 0], n[:, 1], n[:, 2]), step=0, draw=0)
    return (np.asarray(z[0]) + 1j*np.asarray(z[1]))/np.sqrt(2.0)


def convspec(out, workers):
    import compare
    lat256 = os.path.join(out, "lat_CL256S")
    d17 = f"{S}/E-20261124-130952-4be980b/sr.sf.00017.dump"
    deck = f"{S}/E-20261123-090727-4b6e5a5/chain/input.athinput"
    if not os.path.exists(os.path.join(lat256, "sr_summary.json")):
        subprocess.run([sys.executable, os.path.join(HERE, "lattice.py"), "run", "--tag", "sr",
                        "--workers", str(workers), "--nmax2", "64", "--out", lat256, "--dumps", d17],
                       check=True, stdout=subprocess.DEVNULL)
    cmpd = os.path.join(out, "cmp_CL256S")
    subprocess.run([sys.executable, os.path.join(HERE, "compare.py"), "--case", "sr", "--lat", lat256,
                    "--deck", deck, "--modes", MODES64, "--run", f"{S}/E-20261124-130952-4be980b",
                    "--out", cmpd], check=True, stdout=subprocess.DEVNULL)
    c = json.load(open(os.path.join(cmpd, "compare_sr.json")))["per_dump"][-1]
    res = dict(mine_MS={256: {k: v for k, v in c.items() if k.startswith(("shell", "median_rel", "max_rel"))}})
    for n in (32, 64, 128):
        cc = json.load(open(f"{S}/E-20261124-184028-36a685d/C{n}S/compare_sr.json")) \
            if os.path.exists(f"{S}/E-20261124-184028-36a685d/C{n}S/compare_sr.json") else None
        if cc:
            last = cc["per_dump"][-1]
            res["mine_MS"][n] = {k: v for k, v in last.items() if k.startswith(("shell", "median_rel", "max_rel"))}
    seed = int(compare.deck_value(open(deck).read(), "rng_seed"))
    npz = {n: np.load(f"{LATRUNG}/lat_C{n}S/sr_sr.sf.00017.npz") for n in (32, 64, 128)}
    npz[256] = np.load(os.path.join(lat256, "sr_sr.sf.00017.npz"))
    modes = {n: f"{RUNG}/C{n}S/sr.sf.00017.modes" for n in (32, 64, 128)}
    modes[256] = f"{S}/E-20261124-130952-4be980b/sr.sf.00017.modes"
    n = npz[256]["n"]
    for k in (32, 64, 128):
        assert np.array_equal(npz[k]["n"], n)
    n2 = (n**2).sum(1)
    al = alphas(n, seed)
    uq = np.unique(n2)
    lock = {}
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.9))
    for N_, ls in zip((32, 64, 128, 256), (":", "-.", "--", "-")):
        hdr, lq2, lR = compare.read_lockstep(modes[N_])
        pos = {int(v): i for i, v in enumerate(lq2)}
        lin = L**-1.5*lR[[pos[int(v)] for v in n2]]*al
        cR = npz[N_]["c_R"]
        rel = cR/lin - 1
        ssum, scnt = npz[N_]["shell_sum_R"], npz[N_]["shell_cnt"]
        pnr = ssum[uq]/scnt[uq]
        plin = np.array([np.mean(np.abs(lin[n2 == v])**2) for v in uq])
        dsh = np.abs(pnr/plin - 1)
        g10 = scnt[uq] > 10
        lock[N_] = dict(lockstep_time=hdr.get("lockstep"), shell_max=float(dsh.max()),
                        shell_max_cnt_gt10=float(dsh[g10].max()), shell_median=float(np.median(dsh)),
                        shell_median_cnt_gt10=float(np.median(dsh[g10])),
                        n_at_shell_max=float(np.sqrt(uq[np.argmax(dsh)])),
                        n_at_shell_max_gt10=float(np.sqrt(uq[g10][np.argmax(dsh[g10])])),
                        permode_rel_rms=float(np.sqrt(np.mean(np.abs(rel)**2))),
                        permode_rel_rms_n_le4=float(np.sqrt(np.mean(np.abs(rel[n2 <= 16])**2))),
                        permode_rel_rms_n_gt4=float(np.sqrt(np.mean(np.abs(rel[n2 > 16])**2))),
                        permode_power_rel_rms=float(np.sqrt(np.mean((np.abs(cR)**2/np.abs(lin)**2 - 1)**2))),
                        permode_power_rel_rms_n_le4=float(np.sqrt(np.mean(
                            (np.abs(cR[n2 <= 16])**2/np.abs(lin[n2 <= 16])**2 - 1)**2))))
        axs[0].semilogy(np.sqrt(uq), dsh, ls=ls, color=figstyle.SERIES[0], lw=1.0, label=f"{N_}$^3$")
    res["vs_lockstep"] = lock
    # reference-free: per-mode differences between rungs
    dif = {}
    for a, b, c_ in ((32, 64, figstyle.SERIES[1]), (64, 128, figstyle.SERIES[2]), (128, 256, figstyle.SERIES[3])):
        d = npz[a]["c_R"] - npz[b]["c_R"]
        ref = npz[b]["c_R"]
        r = np.abs(d)/np.abs(ref)
        dif[f"{a}-{b}"] = dict(rel_rms=float(np.sqrt(np.mean(np.abs(d)**2)/np.mean(np.abs(ref)**2))),
                               rel_rms_permode=float(np.sqrt(np.mean(r**2))), rel_median=float(np.median(r)),
                               rel_max=float(r.max()),
                               rel_rms_n_le4=float(np.sqrt(np.mean(r[n2 <= 16]**2))),
                               rel_rms_n_gt4=float(np.sqrt(np.mean(r[n2 > 16]**2))))
        sh = np.array([np.sqrt(np.mean(r[n2 == v]**2)) for v in uq])
        axs[1].semilogy(np.sqrt(uq), sh, color=c_, lw=1.0, label=f"$|R_{{{a}}}-R_{{{b}}}|/|R_{{{b}}}|$")
    for x, y in (("32-64", "64-128"), ("64-128", "128-256")):
        dif[f"factor_{x}_over_{y}"] = dif[x]["rel_rms_permode"]/dif[y]["rel_rms_permode"]
    res["between_rungs"] = dif
    for N_, ls in zip((128, 256), ("--", "-")):
        hdr, lq2, lR = compare.read_lockstep(modes[N_])
        pos = {int(v): i for i, v in enumerate(lq2)}
        lin = L**-1.5*lR[[pos[int(v)] for v in n2]]*al
        r = np.abs(npz[N_]["c_R"]/lin - 1)
        sh = np.array([np.sqrt(np.mean(r[n2 == v]**2)) for v in uq])
        axs[1].semilogy(np.sqrt(uq), sh, color="k", ls=ls, lw=0.8, label=f"$|R_{{{N_}}}/R_{{\\rm lin}}-1|$")
    axs[0].set_xlabel("$|n|$")
    axs[0].set_ylabel(r"$|\Delta_{\rm NR}/\Delta_{\rm lin,lockstep}-1|$ per shell")
    axs[0].legend(fontsize=5)
    axs[1].set_xlabel("$|n|$")
    axs[1].set_ylabel("per-mode rms per shell")
    axs[1].legend(fontsize=5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_convspec_256.png"), dpi=150)
    plt.close(fig)
    return res


def shells(path, workers, nmax2=4096):
    r = lattice.analyse_dump(path, nmax2, workers=workers)
    n2 = (r["n"]**2).sum(1)
    uq = np.unique(n2)
    return dict(uq=uq, p=r["shell_sum_R"][uq]/r["shell_cnt"][uq], cnt=r["shell_cnt"][uq], c=r["c_R"],
                n2=n2, t=r["time"], N=r["efolds_from_mean_chi"])


def br_stats(A, B):
    d = A["p"]/B["p"] - 1
    k = np.sqrt(A["uq"])
    g10 = A["cnt"] > 10
    pm = np.abs(A["c"]/B["c"] - 1)
    o = dict(t=A["t"], N=A["N"], t_ref=B["t"], n_shells=int(len(d)),
             all_rms=float(np.sqrt(np.mean(d**2))), all_max=float(np.abs(d).max()),
             all_n_at_max=float(k[np.argmax(np.abs(d))]), all_frac_pos=float(np.mean(d > 0)),
             all_rms_k_le_32=float(np.sqrt(np.mean(d[k <= 32]**2))),
             gt10_rms=float(np.sqrt(np.mean(d[g10]**2))), gt10_max=float(np.abs(d[g10]).max()),
             gt10_n_at_max=float(k[g10][np.argmax(np.abs(d[g10]))]),
             gt10_frac_pos=float(np.mean(d[g10] > 0)),
             gt10_rms_k_le_32=float(np.sqrt(np.mean(d[g10 & (k <= 32)]**2))),
             frac_shells_above_1em4=float(np.mean(np.abs(d) > 1e-4)),
             frac_gt10_shells_above_1em4=float(np.mean(np.abs(d[g10]) > 1e-4)),
             permode_rel_rms=float(np.sqrt(np.mean(pm**2))))
    g10h = A["cnt"]/2 > 10      # more than 10 independent (hemisphere) modes
    o.update(gt10h_rms_k_le_32=float(np.sqrt(np.mean(d[g10h & (k <= 32)]**2))),
             gt10h_max=float(np.abs(d[g10h]).max()), gt10h_n_at_max=float(k[g10h][np.argmax(np.abs(d[g10h]))]),
             gt10h_frac_pos=float(np.mean(d[g10h] > 0)), n_gt10h=int(g10h.sum()), n_gt10=int(g10.sum()),
             gt10h_max_k_le_16=float(np.abs(d[g10h & (k <= 16)]).max()),
             frac_above_1em4_k_le_32=float(np.mean(np.abs(d[k <= 32]) > 1e-4)),
             frac_above_1em4_k_gt_32=float(np.mean(np.abs(d[k > 32]) > 1e-4)),
             max_k_le_32=float(np.abs(d[k <= 32]).max()))
    # |n| above which the running median (bins of width 4 in |n|) exceeds 1e-4
    edges = np.arange(0, 68, 4)
    med = [float(np.median(np.abs(d[(k > lo) & (k <= lo + 4)]))) if ((k > lo) & (k <= lo + 4)).any() else None
           for lo in edges]
    o["binned_median_abs"] = dict(zip([f"{lo}-{lo+4}" for lo in edges], med))
    return o, k, d


def backreact(out, workers):
    res = {}
    A17 = shells(f"{ABL['l2S17']}.sf.00017.dump", workers)
    B17 = shells(f"{ABL['l0S']}.sf.00017.dump", workers)
    o17, k, d17 = br_stats(A17, B17)
    res["SR_l2_vs_l0_dump17"] = o17
    A15 = shells(f"{ABL['l2S15']}.sf.00015.dump", workers)
    B15 = shells(f"{ABL['l0S']}.sf.00015.dump", workers)
    o15, _, d15 = br_stats(A15, B15)
    res["SR_l2_vs_l0_dump15"] = o15
    res["SR_change_15_to_17_max_over_max"] = float(np.abs(d17 - d15).max()/np.abs(d17).max())
    res["SR_change_15_to_17_rms_over_rms"] = float(np.sqrt(np.mean((d17 - d15)**2))/np.sqrt(np.mean(d17**2)))
    del A15, B15
    AU = shells(f"{ABL['l2U']}.sf.00020.dump", workers)
    BU = shells(f"{ABL['l0U']}.sf.00020.dump", workers)
    oU, kU, dU = br_stats(AU, BU)
    res["USR_l2_vs_l0_dump20"] = oU
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.9))
    for ax, (kk, dd, cnt, lab) in zip(axs, ((k, d17, A17["cnt"], "SR, level 2 - level 0, $t=8.5$"),
                                             (kU, dU, AU["cnt"], "USR, level 2 - level 0, $N_f$"))):
        g = cnt > 10
        ax.semilogy(kk[~g], np.abs(dd[~g]), ".", ms=1.5, color=figstyle.SERIES[1], label="shells of $\\leq 10$ modes")
        ax.semilogy(kk[g], np.abs(dd[g]), ".", ms=1.5, color=figstyle.SERIES[0], label="shells of $>10$ modes")
        ax.axhline(1e-4, **figstyle.REF_LINE)
        ax.axhline(1e-3, **figstyle.GUIDE)
        ax.text(1, 1.15e-4, "P1:520 bound 1e-4", fontsize=6)
        ax.text(1, 1.15e-3, "1e-3 (per mille, not the bound)", fontsize=6)
        ax.set_xlabel("$|n|$")
        ax.set_ylabel(r"$|\Delta_2/\Delta_0-1|$")
        ax.set_title(lab, fontsize=8)
        ax.legend(fontsize=5, markerscale=4)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_backreaction_Nf.png"), dpi=150)
    plt.close(fig)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    figstyle.use_style()
    path = os.path.join(a.out, "cont.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    steps = (("joins", joins), ("signflip", signflip), ("convrec", convrec),
             ("convspec", lambda o: convspec(o, a.workers)), ("constraints", constraints),
             ("backreact", lambda o: backreact(o, a.workers)))
    for name, f in steps:
        if a.only and name not in a.only:
            continue
        res[name] = f(a.out)
        print(name, json.dumps(res[name], default=float)[:3000], flush=True)
        with open(path, "w") as fo:
            json.dump(res, fo, indent=1, default=float)


if __name__ == "__main__":
    main()
