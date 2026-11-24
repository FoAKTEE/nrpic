#!/usr/bin/env python3
"""Fresh verifier, part 2c: sign-flip controls, convergence rungs and backreaction levels,
from the raw outputs (records .sf.con.hst and dumps) with my own readers.

  signflip     pairs (proper, flipped) of 256^3 runs: <|H|/[H]> ratio and <|M|/[M]> of the flip
  convergence  rungs 32, 64, 128 (both cases): entry maxima of the record and their orders;
               spectra of the last dump against my linear solution (lattice.py + compare.py)
  backreaction ablation dumps: shell power of R^NR (my extraction), level 2 and 1 against 0,
               and level 0 with the mode equation on the mesh against level 0 on shells

Usage: python records.py --out DIR
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lattice  # noqa: E402
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
PAIRS = {  # case: (proper, flipped)
    "sr": (f"{S}/E-20261123-035925-8439d79/sr.sf.con.hst", f"{S}/E-20261123-045030-c20bcb3/sr.sf.con.hst"),
    "usr": (f"{S}/E-20261121-211214-0377aab/usr.sf.con.hst", f"{S}/E-20261122-190341-0419be6/usr.sf.con.hst"),
}
RUNG = f"{S}/E-20261123-020704-2b99463"
ABL = {
    "l0S": f"{S}/E-20261123-153347-18e7c21/sr256_l0m", "l1S": f"{S}/E-20261123-183822-4abbcae/sr256_l1m",
    "l2S": f"{S}/E-20261123-152119-38957ba/sr256_l2", "l0U": f"{S}/E-20261123-164235-49b0945/usr256_l0m",
    "l1U": f"{S}/E-20261123-192948-348e2e5/usr256_l1m", "l2U": f"{S}/E-20261123-153146-d965002/usr256_l2",
    "shellS": f"{S}/E-20261121-202935-31520bc/P256/sr",
}


def rec(path):
    return np.loadtxt(path, comments="#")


def signflip(out):
    res = {}
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.8))
    for (case, (pp, pf)), ax in zip(PAIRS.items(), axs):
        P, F = rec(pp), rec(pf)
        nmax = min(P[-1, 2], F[-1, 2])
        sel = (F[:, 2] > 0.02) & (F[:, 2] <= nmax)
        hp = np.exp(np.interp(F[sel, 2], P[:, 2], np.log(P[:, 3])))
        ratio = F[sel, 3]/hp
        res[case] = dict(proper=pp, flipped=pf, N_overlap=float(nmax),
                         ratio_median=float(np.median(ratio)), ratio_max=float(ratio.max()),
                         ratio_at_end=float(ratio[-1]),
                         flip_H_max=float(F[:, 3].max()), proper_H_max=float(P[P[:, 2] <= nmax, 3].max()),
                         flip_M_max=float(F[:, 6].max()), proper_M_max=float(P[P[:, 2] <= nmax, 6].max()),
                         flip_M_median=float(np.median(F[sel, 6])))
        ax.semilogy(P[:, 2], P[:, 3], color=figstyle.SERIES[0], label=r"proper $\langle|H|/[H]\rangle$")
        ax.semilogy(F[:, 2], F[:, 3], color=figstyle.SERIES[0], ls="--", label="flipped")
        ax.semilogy(P[:, 2], P[:, 6], color=figstyle.SERIES[1], label=r"proper $\langle|M|/[M]\rangle$")
        ax.semilogy(F[:, 2], F[:, 6], color=figstyle.SERIES[1], ls="--", label="flipped")
        ax.set_xlim(0, max(nmax*1.5, 1.0))
        ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
        ax.set_title(case.upper(), fontsize=9)
    axs[0].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_signflip.png"), dpi=150)
    plt.close(fig)
    return res


def convergence_records(out):
    res = {}
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 2.8))
    for case, ax in zip(("S", "U"), axs):
        rows = {}
        for n, ls in zip((32, 64, 128), (":", "-.", "--")):
            f = glob.glob(f"{RUNG}/C{n}{case}/*.sf.con.hst")[0]
            R = rec(f)
            ent = R[:, 2] <= np.log(8.0) + 0.5
            d = dict(H_entry_max=float(R[ent, 3].max()), M_entry_max=float(R[ent, 6].max()),
                     N_H_entry_max=float(R[ent, 2][np.argmax(R[ent, 3])]))
            if R.shape[1] >= 26:
                d["H0_entry_max"] = float(R[ent, 24].max())
            rows[n] = d
            ax.semilogy(R[:, 2], R[:, 3], color=figstyle.SERIES[0], ls=ls, label=f"H, {n}")
            ax.semilogy(R[:, 2], R[:, 6], color=figstyle.SERIES[1], ls=ls, label=f"M, {n}")
            if R.shape[1] >= 26:
                ax.semilogy(R[:, 2], R[:, 24], color=figstyle.SERIES[2], ls=ls,
                            label=f"H - <H>, {n}")
        for q in ("H_entry_max", "M_entry_max", "H0_entry_max"):
            if q in rows[32]:
                rows[f"order_{q}_32_64"] = float(np.log2(rows[32][q]/rows[64][q]))
                rows[f"order_{q}_64_128"] = float(np.log2(rows[64][q]/rows[128][q]))
        res[case] = rows
        ax.axvline(np.log(8.0) + 0.5, **figstyle.MASK_LINE)
        ax.set_xlabel(r"$\mathcal{N}-\mathcal{N}_*$")
        ax.set_title({"S": "SR rungs", "U": "USR rungs"}[case], fontsize=9)
        ax.legend(fontsize=5, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_conv_records.png"), dpi=150)
    plt.close(fig)
    return res


def convergence_spectra(out):
    """lattice.py on every dump of each SR rung (small) and compare.py against my linear."""
    res = {}
    batch = open(f"{RUNG}/batch.list").read()
    for n in (32, 64, 128):
        name = f"C{n}S"
        line = [ln for ln in batch.splitlines() if ln.split()[0].endswith("/" + name)][0]
        nmax2 = int(re.search(r"noise_nmax2=(\d+)", line).group(1))
        modes = re.search(r"noise_mode_file=(\S+)", line).group(1)
        dumps = sorted(glob.glob(f"{RUNG}/{name}/sr.sf.*.dump"))
        if n == 128:
            dumps = dumps[::3] + ([dumps[-1]] if (len(dumps) - 1) % 3 else [])
        lat = os.path.join(out, f"lat_{name}")
        subprocess.run([sys.executable, os.path.join(HERE, "lattice.py"), "run", "--tag", "sr",
                        "--workers", "2", "--nmax2", str(nmax2), "--out", lat, "--dumps"] + dumps,
                       check=True, stdout=subprocess.DEVNULL)
        cmpd = os.path.join(out, f"cmp_{name}")
        subprocess.run([sys.executable, os.path.join(HERE, "compare.py"), "--case", "sr",
                        "--lat", lat, "--deck", f"{RUNG}/{name}/sr_paper.athinput",
                        "--modes", modes, "--run", f"{RUNG}/{name}", "--out", cmpd],
                       check=True, stdout=subprocess.DEVNULL)
        c = json.load(open(os.path.join(cmpd, "compare_sr.json")))
        last = c["per_dump"][-1]
        res[name] = dict(nmax2=nmax2, N_last=last["N"],
                         shell_max_abs_NR_over_lin_m1=last.get("shell_max_abs_NR_over_lin_m1"),
                         median_rel_all=last.get("median_rel_all"), max_rel_all=last.get("max_rel_all"),
                         series=[(d["N"], d.get("shell_max_abs_NR_over_lin_m1")) for d in c["per_dump"]])
    return res


def backreaction(out):
    res = {}
    cache = {}

    def shell(key, idx):
        k = (key, idx)
        if k not in cache:
            p = f"{ABL[key]}.sf.{idx:05d}.dump"
            r = lattice.analyse_dump(p, 4096, workers=3)
            n2 = (r["n"]**2).sum(1)
            uq = np.unique(n2)
            cache[k] = dict(uq=uq, p=r["shell_sum_R"][uq]/r["shell_cnt"][uq], t=r["time"],
                            N=r["efolds_from_mean_chi"])
        return cache[k]
    comps = [("USR_l2_vs_l0", "l2U", "l0U", 20), ("USR_l1_vs_l0", "l1U", "l0U", 20),
             ("SR_l2_vs_l0_dump15", "l2S", "l0S", 15), ("SR_l1_vs_l0", "l1S", "l0S", 17),
             ("SR_shell_vs_mesh_l0", "shellS", "l0S", 17)]
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH, 2.9))
    for (name, a, b, idx), c in zip(comps, figstyle.SERIES + ["k"]):
        A, B = shell(a, idx), shell(b, idx)
        d = A["p"]/B["p"] - 1
        k = np.sqrt(A["uq"])
        res[name] = dict(t=A["t"], N=A["N"], N_ref=B["N"], rms=float(np.sqrt(np.mean(d**2))),
                         max_abs=float(np.abs(d).max()), frac_positive=float(np.mean(d > 0)),
                         rms_k_le_32=float(np.sqrt(np.mean(d[k <= 32]**2))),
                         max_abs_k_le_32=float(np.abs(d[k <= 32]).max()))
        ax.semilogy(k, np.abs(d), ".", ms=1.5, color=c, label=name.replace("_", " "))
    ax.axhline(1e-4, **figstyle.MASK_LINE)
    ax.set_xlabel(r"$|n|$")
    ax.set_ylabel(r"$|\Delta_a/\Delta_b-1|$ per shell")
    ax.legend(fontsize=5, markerscale=4)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_backreaction.png"), dpi=150)
    plt.close(fig)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip", nargs="*", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    figstyle.use_style()
    res = {}
    for name, f in (("signflip", signflip), ("convergence_records", convergence_records),
                    ("convergence_spectra", convergence_spectra), ("backreaction", backreaction)):
        if name in a.skip:
            continue
        res[name] = f(a.out)
        print(name, json.dumps(res[name], default=float)[:2000], flush=True)
        with open(os.path.join(a.out, "records.json"), "w") as fo:
            json.dump(res, fo, indent=1, default=float)


if __name__ == "__main__":
    main()
