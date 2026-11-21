#!/usr/bin/env python3
"""Lead's re-check of batch 4a (2026-11-21) of D-bh-dress: predictions Y1-Y2 of JOURNAL.md,
session lead-wave3-batch4a.

No helper code. Readers: read_summary of stage/review_wave3/wave3_check.py (finder summaries)
and analyse/snap of stage/review_wave2/infall_check.py (Newtonian-mode snapshots; turnaround
and dress flags re-implemented by the wave-2 lead from nm_analyze's docstring). Registered
outputs only:
  ES-1G  D-20261119-142633-6f72922 (es)    ES-1GB D-20261121-125900-ea4c442 (es1gb)
  V-1B   D-20261120-222625-63abd72 (v1b)   V-1GB  D-20261121-125909-06f856e (v1gb)
  Q16    D-20261121-085652-7e189a2         shells hybrid_cc D-20261121-085600-c436f4a,
                                           kernel_cc D-20261121-085559-5551b3e
  P192   D-20261121-075559-31835c4 (snapshot headers only)
Writes batch4a_check.json and batch4a_check.png/.pdf into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "review_wave2")))
from wave3_check import read_summary, fs  # noqa: E402
import infall_check as ic  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
HZ = {"ES-1G": ("D-20261119-142633-6f72922", "es"),
      "ES-1GB": ("D-20261121-125900-ea4c442", "es1gb"),
      "V-1B": ("D-20261120-222625-63abd72", "v1b"),
      "V-1GB": ("D-20261121-125909-06f856e", "v1gb")}
Q16 = "D-20261121-085652-7e189a2"
P192 = "D-20261121-075559-31835c4"
SHELLS = {"hybrid_cc": ("D-20261121-085600-c436f4a", "nm_shells_Q16_hybridcc.json"),
          "kernel_cc": ("D-20261121-085559-5551b3e", "nm_shells_Q16_kernelcc.json")}
CLAIM_Q16 = {4: (2.597, 0.795), 8: (4.815, 2.148), 12: (7.047, 3.541), 15.96: (9.302, 4.911)}


def horizons():
    S = {k: read_summary(os.path.join(SCR, rid, f"{b}.horizon_summary_0.txt"))
         for k, (rid, b) in HZ.items()}
    out = {}

    def common(a, b):
        t = np.intersect1d(S[a]["t"], S[b]["t"])
        ia = np.searchsorted(S[a]["t"], t)
        ib = np.searchsorted(S[b]["t"], t)
        return t, S[a]["m"][ia], S[b]["m"][ib]

    t, ma, mb = common("ES-1GB", "ES-1G")
    d = np.abs(ma - mb)
    out["Y1a"] = dict(max_le90=float(d[t <= 90].max()), max_le188=float(d[t <= 188].max()),
                      t_last_common=float(t[-1]))
    drift = {}
    for k in S:
        s = S[k]
        m100 = s["m"][np.argmin(np.abs(s["t"] - 100.0))]
        sel = s["t"] >= 100.0
        D = s["m"] - m100
        drift[k] = dict(t_last=float(s["t"][-1]), m100=float(m100),
                        D_last=float(D[-1]), D_min=float(D[sel].min()), D_max=float(D[sel].max()),
                        meanr_last=float(s["meanr"][-1]),
                        D_at188=float(D[np.argmin(np.abs(s["t"] - 188.0))]))
    out["drift"] = drift
    t, me, mv = common("ES-1GB", "V-1GB")
    dn = me - mv
    above2 = t[np.abs(dn) > 2e-4]
    out["Y1d"] = dict(max_le90=float(np.abs(dn[t <= 90]).max()),
                      first_t_above_2e-4=float(above2[0]) if len(above2) else None,
                      all_above_after_first=bool(np.all(np.abs(dn[t >= above2[0]]) > 2e-4)) if len(above2) else None,
                      at188=float(dn[np.argmin(np.abs(t - 188.0))]), t_last=float(t[-1]))
    return S, out


def q16():
    rows = ic.analyse(os.path.join(SCR, Q16))
    p = json.load(open(os.path.join(SCR, Q16, "setup.json")))
    files = sorted(glob.glob(os.path.join(SCR, Q16, "infall.part.*.bin")))
    n_last = ic.snap(files[-1])[1].shape[0]
    a = np.array([r["a"] for r in rows])
    sh = {}
    for lab, (rid, fn) in SHELLS.items():
        g = json.load(open(os.path.join(SCR, rid, fn)))["growth"]
        sh[lab] = (np.array([x["a"] for x in g]), np.array([x["mta"] for x in g]),
                   np.array([x["dress"] for x in g]))
    res = {}
    for aa, (cm, cd) in CLAIM_Q16.items():
        i = int(np.argmin(np.abs(a - aa)))
        r = rows[i]
        e = dict(a=r["a"], M_ta=r["M_ta"], dress=r["dress"], claim=(cm, cd),
                 rel_Mta_claim=r["M_ta"] / cm - 1, rel_dress_claim=r["dress"] / cd - 1)
        for lab, (sa, sm, sd) in sh.items():
            e[f"rel_Mta_{lab}"] = r["M_ta"] / np.interp(r["a"], sa, sm) - 1
            e[f"rel_dress_{lab}"] = r["dress"] / np.interp(r["a"], sa, sd) - 1
        e["dress_over_Mta"] = r["dress"] / r["M_ta"]
        e["Mta_over_Ma"] = r["M_ta"] / r["a"]   # seed mass 1
        res[str(aa)] = e
    return rows, sh, dict(n_total=p["n_total"], n_last=int(n_last), points=res)


def p192():
    p = json.load(open(os.path.join(SCR, P192, "setup.json")))
    files = sorted(glob.glob(os.path.join(SCR, P192, "infall.part.*.bin")))
    a, n = [], []
    for fn in files:
        with open(fn, "rb") as fh:
            assert fh.read(8) == b"NRPSNAP1"
            t = float(np.frombuffer(fh.read(8), "<f8")[0])
            k = int(np.frombuffer(fh.read(8), "<i8")[0])
        a.append(((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0))
        n.append(k)
    a, n = np.array(a), np.array(n)
    miss = p["n_total"] - n
    first = a[np.nonzero(miss > 0)[0][0]] if np.any(miss > 0) else None
    return a, n, dict(n_total=p["n_total"], n_last=int(n[-1]), missing_last=int(miss[-1]),
                      mass_missing_last=float(miss[-1] * p["m_dust_particle"]),
                      a_first_missing=float(first) if first is not None else None,
                      a_last=float(a[-1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    S, hz = horizons()
    rows, sh, q = q16()
    pa, pn, pr = p192()
    out = dict(horizons=hz, q16=q, p192=pr)
    with open(os.path.join(args.out, "batch4a_check.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 3, figsize=(11, 6.2))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.09, top=0.95, wspace=0.32, hspace=0.38)
    col = {"ES-1G": fs.PAL["red"], "ES-1GB": fs.PAL["green"], "V-1B": fs.PAL["blue"],
           "V-1GB": fs.PAL["yellow"]}
    ax = axs[0, 0]
    t = np.intersect1d(S["ES-1GB"]["t"], S["ES-1G"]["t"])
    d = np.abs(S["ES-1GB"]["m"][np.searchsorted(S["ES-1GB"]["t"], t)]
               - S["ES-1G"]["m"][np.searchsorted(S["ES-1G"]["t"], t)])
    ax.semilogy(t, np.maximum(d, 1e-17), color=fs.PAL["green"])
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$|M_{\rm AH}^{\rm ES-1GB}-M_{\rm AH}^{\rm ES-1G}|$")
    ax.set_title("(a) faces at $\\pm384\\,M$ vs $\\pm192\\,M$", fontsize=9)
    ax = axs[0, 1]
    for k, s in S.items():
        m100 = s["m"][np.argmin(np.abs(s["t"] - 100.0))]
        ax.plot(s["t"], s["m"] - m100, color=col[k], label=k)
    ax.set_xlim(90, 200)
    ax.set_ylim(-1.5e-3, 7.5e-3)
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$M_{\rm AH}(t)-M_{\rm AH}(100\,M)$")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.set_title("(b) drift from 100 M", fontsize=9)
    ax = axs[0, 2]
    t = np.intersect1d(S["ES-1GB"]["t"], S["V-1GB"]["t"])
    dn = (S["ES-1GB"]["m"][np.searchsorted(S["ES-1GB"]["t"], t)]
          - S["V-1GB"]["m"][np.searchsorted(S["V-1GB"]["t"], t)])
    ax.semilogy(t, np.maximum(np.abs(dn), 1e-17), color=fs.PAL["orange"])
    ax.axhline(2e-4, color="0.5", ls=":", lw=0.8)
    ax.axhline(1e-4, color="0.5", ls="--", lw=0.8)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$|M_{\rm AH}^{\rm ES-1GB}-M_{\rm AH}^{\rm V-1GB}|$")
    ax.set_title("(c) null test with lapse_leak", fontsize=9)
    ax = axs[1, 0]
    a = np.array([r["a"] for r in rows])
    ax.plot(a, [r["M_ta"] for r in rows], color=fs.PAL["red"], label=r"Q16 $M_{\rm ta}$")
    ax.plot(a, [r["dress"] for r in rows], color=fs.PAL["blue"], label="Q16 dress")
    sa, sm, sd = sh["hybrid_cc"]
    ax.plot(sa, sm, color="k", ls="--", lw=0.8, label="hybrid_cc shells")
    ax.plot(sa, sd, color="k", ls="--", lw=0.8)
    for aa, (cm, cd) in CLAIM_Q16.items():
        ax.plot([aa], [cm], "o", mfc="none", color=fs.PAL["green"], ms=5)
        ax.plot([aa], [cd], "s", mfc="none", color=fs.PAL["green"], ms=5)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel(r"mass [$M$]")
    ax.legend(frameon=False, fontsize=7)
    ax.set_title("(d) Q16 growth (open: README claims)", fontsize=9)
    ax = axs[1, 1]
    for lab, ls in (("hybrid_cc", "-"), ("kernel_cc", ":")):
        sa, sm, sd = sh[lab]
        ax.plot(a, 100 * (np.array([r["M_ta"] for r in rows]) / np.interp(a, sa, sm) - 1),
                color=fs.PAL["red"], ls=ls, label=r"$M_{\rm ta}$ / " + lab)
        ax.plot(a, 100 * (np.array([r["dress"] for r in rows]) / np.interp(a, sa, sd) - 1),
                color=fs.PAL["blue"], ls=ls, label="dress / " + lab)
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlim(2, 16.2)
    ax.set_ylim(-3, 3)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel("run / shells - 1 [%]")
    ax.legend(frameon=False, fontsize=6.5)
    ax.set_title("(e) Q16 against matched shells", fontsize=9)
    ax = axs[1, 2]
    ax.plot(pa, pr["n_total"] - pn, color=fs.PAL["red"])
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel("particles missing from the box")
    ax.set_title("(f) P192: lost dust", fontsize=9)
    fs.save(fig, os.path.join(args.out, "batch4a_check"))


if __name__ == "__main__":
    main()
