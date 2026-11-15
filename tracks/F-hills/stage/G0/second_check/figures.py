#!/usr/bin/env python3
"""Figures and comparison tables of the second check (reads the registered run directories).
Usage: figures.py --scan DIR --flat DIR --nrstate DIR --hrnapy DIR --selftest DIR [outdir]
Writes PNG/PDF figures and compare.json into outdir (default $NRPIC_RUN_DIR)."""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
import models as mdl  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

LEAD_V7 = os.path.normpath(os.path.join(HERE, "..", "checks", "v7_summary.json"))


def load_rows(path):
    return [json.loads(line) for line in open(path)]


def frac(rows, key):
    return float(np.mean([key(r) for r in rows])) if rows else math.nan


def main(a):
    out = a.outdir or os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    P = fs.PAL
    rows = load_rows(os.path.join(a.scan, "scan.jsonl"))
    summ = json.load(open(os.path.join(a.scan, "scan_summary.json")))
    rps = summ["rps"]
    S = summ["summary"]
    lead = json.load(open(LEAD_V7))["q10"]
    comp = {}

    # ---------------- SC1: my fractions against the lead's V7 ----------------
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax = axs[0]
    for lab, col, name in (("NF4", P["blue"], "Newton, hole fixed"), ("NT4", P["green"], "Newton, full"),
                           ("H4", P["red"], "HRNA (2404 data)")):
        ax.plot(rps, [s["separated"] for s in S[lab]], "-", color=col, label=f"{name}, this check")
    lr = [r["rp"] for r in lead]
    ax.plot(lr, [r["newton"]["separated"] for r in lead], "s", color=P["blue"], ms=4, mfc="none",
            label="lead V7")
    ax.plot(lr, [r["newton_full"]["separated"] for r in lead], "s", color=P["green"], ms=4, mfc="none")
    ax.plot(lr, [r["hrna"]["separated"] for r in lead], "s", color=P["red"], ms=4, mfc="none")
    ax.set_xlabel(r"$r_p\,[M]$")
    ax.set_ylabel("separated fraction")
    ax.set_title("SC1: separation, q = 10, prograde, 180 phases", fontsize=9)
    ax.legend(frameon=False, fontsize=6.5, loc="lower left")
    ax = axs[1]
    ax.plot(rps, [s["captured"] for s in S["H4"]], "-", color=P["red"], label="HRNA: member below 2.5 M (this check)")
    ax.plot(lr, [r["hrna"]["plunge"] for r in lead], "s", color=P["red"], ms=4, mfc="none", label="lead V7")
    ax.plot(rps, [s["member_below_4M"] for s in S["NT4"]], "-", color=P["green"],
            label="Newton full: member inside 4 M (this check)")
    ax.plot(lr, [r["newton_full"]["member_below_4M"] for r in lead], "s", color=P["green"], ms=4, mfc="none")
    ax.set_xlabel(r"$r_p\,[M]$")
    ax.set_ylabel("fraction of phases")
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    ax.set_title("SC1: close approaches", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc1_vs_lead"))
    plt.close(fig)
    comp["sc1"] = []
    for r in lead:
        i = rps.index(r["rp"]) if r["rp"] in rps else None
        if i is None:
            continue
        comp["sc1"].append(dict(rp=r["rp"],
                                NF4_sep=S["NF4"][i]["separated"], lead_newton_sep=r["newton"]["separated"],
                                NT4_sep=S["NT4"][i]["separated"], lead_full_sep=r["newton_full"]["separated"],
                                H4_sep=S["H4"][i]["separated"], lead_hrna_sep=r["hrna"]["separated"],
                                H4_cap=S["H4"][i]["captured"], lead_hrna_plunge=r["hrna"]["plunge"]))

    # ---------------- SC2: phase by phase against hrna.py ----------------
    if a.hrnapy:
        hp = load_rows(os.path.join(a.hrnapy, "hrna_py.jsonl"))
        fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 4.6), sharex=True)
        comp["sc2"] = []
        for j, (law, lab) in enumerate((("newton", "NF4"), ("hrna", "H4"))):
            for i, rp in enumerate((8.0, 13.0)):
                mine = {round(r["phase"], 9): r for r in rows if r["label"] == lab and r["rp"] == rp}
                theirs = {round(r["phase"], 9): r for r in hp if r["law"] == law and r["rp"] == rp}
                keys = sorted(set(mine) & set(theirs))
                om = np.array([mine[k]["outcome"] for k in keys])
                ot = np.array([theirs[k]["outcome"] for k in keys])
                sm = np.array([mine[k]["separated"] for k in keys])
                st = np.array([theirs[k]["separated"] for k in keys])
                cm = np.array([any(mine[k]["plunged"]) for k in keys])
                ct = np.array([theirs[k]["plunged"] > 0 for k in keys])
                stat = np.array([mine[k]["status"] for k in keys])
                good = stat != "superluminal"
                comp["sc2"].append(dict(law=law, rp=rp, n=len(keys), n_superluminal_mine=int((~good).sum()),
                                        outcome_equal=float(np.mean(om[good] == ot[good])),
                                        separated_equal=float(np.mean(sm[good] == st[good])),
                                        captured_equal=float(np.mean(cm[good] == ct[good]))))
                ax = axs[j, i]
                ph = np.array(keys) / math.pi
                ax.plot(ph, ot + 0.12, "o", ms=3, color=P["red"], label="hrna.py")
                ax.plot(ph, om - 0.12, "s", ms=2.5, color=P["blue"], label="this check")
                ax.set_yticks([0, 1, 2, 3, 4, 6])
                ax.set_title(f"SC2: law {law}, $r_p$ = {rp:g} M; equal {comp['sc2'][-1]['outcome_equal']:.3f}",
                             fontsize=9)
                if i == 0:
                    ax.set_ylabel("outcome code")
        for ax in axs[-1]:
            ax.set_xlabel(r"release phase $/\pi$")
        axs[0, 0].legend(frameon=False, fontsize=7)
        fig.tight_layout()
        fs.save(fig, os.path.join(out, "fig_sc2_phase_by_phase"))
        plt.close(fig)

    # ---------------- SC3/SC6: all models ----------------
    styles = {"NF4": (P["blue"], "-", "Newton fixed, 4 $r_t$"), "NF20": (P["blue"], ":", "Newton fixed, 20 $r_t$"),
              "NT4": (P["green"], "-", "Newton full, 4 $r_t$"),
              "H4": (P["red"], "-", "HRNA 2404 data, 4 $r_t$"), "HG4": (P["red"], "--", "HRNA $\\Gamma$-corr., 4 $r_t$"),
              "H20": (P["red"], ":", "HRNA 2404 data, 20 $r_t$"),
              "S4raw": (P["yellow"], "--", "sym. 2404 data, 4 $r_t$"), "S4": (P["yellow"], "-", "sym. $\\Gamma$-corr., 4 $r_t$"),
              "S20": (P["yellow"], ":", "sym. $\\Gamma$-corr., 20 $r_t$")}
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.1))
    for lab, (col, ls, name) in styles.items():
        axs[0].plot(rps, [s["separated"] for s in S[lab]], ls=ls, color=col, marker="o", ms=2.5, label=name)
        if not lab.startswith("N"):
            axs[1].plot(rps, [s["captured"] for s in S[lab]], ls=ls, color=col, marker="o", ms=2.5)
        else:
            axs[1].plot(rps, [s["gr_criterion_any"] for s in S[lab]], ls=ls, color=col, marker="x", ms=3)
        axs[2].plot(rps, [s["dL_cm_to_2rt_median"] for s in S[lab]], ls=ls, color=col, marker="o", ms=2.5)
    axs[0].set_ylabel("separated fraction")
    axs[1].set_ylabel("member captured (HRNA, sym.: crossed 2.5 M;\nNewton x: GR criterion on final $E, L$)",
                      fontsize=7)
    axs[2].set_ylabel(r"median $\Delta L_{\rm cm}$, release $\to 2 r_t$ $[M]$")
    axs[2].axhline(0.127, **fs.GUIDE)
    axs[2].set_yscale("symlog", linthresh=0.01)
    for ax in axs:
        ax.set_xlabel(r"$r_p\,[M]$")
    axs[0].legend(frameon=False, fontsize=5.5, loc="lower left")
    axs[0].set_title("SC3", fontsize=9)
    axs[1].set_title("SC4", fontsize=9)
    axs[2].set_title("SC6 (dashed: predicted, HRNA 4 $r_t$)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc3_sc6_models"))
    plt.close(fig)
    comp["models"] = {lab: S[lab] for lab in S}

    # ---------------- SC4: capture criterion in the (L, E) plane ----------------
    Ls = np.linspace(3.0, 8.0, 400)
    bar = [mdl.barrier_E2(L) for L in Ls]
    Eb = np.array([math.sqrt(b) if b is not None else np.nan for b in bar])
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    comp["sc4"] = {}
    for ax, lab in zip(axs, ("H4", "S4", "NF4")):
        sel = [r for r in rows if r["label"] == lab and r["rp"] in (7.0, 8.0, 9.0, 10.0)
               and r["status"] != "superluminal"]
        Lp, Ep, Lo, Eo = [], [], [], []
        consistent = []
        for r in sel:
            for k in (0, 1):
                L, E = r["L"][k], r["E"][k]
                if L is None or E is None:
                    continue
                if r["plunged"][k]:
                    Lp.append(abs(L))
                    Ep.append(E)
                    consistent.append(mdl.gr_captured(E, L, -1.0))
                else:
                    Lo.append(abs(L))
                    Eo.append(E)
        ax.plot(Lo, Eo, ".", ms=1.5, color=P["blue"], label="not captured")
        if Lp:
            ax.plot(Lp, Ep, ".", ms=1.5, color=P["red"], label="captured (crossed 2.5 M)")
        ax.plot(Ls, Eb, **fs.GUIDE)
        ax.axvline(math.sqrt(12), **fs.MASK_LINE)
        ax.set_xlim(0, 9)
        ax.set_ylim(0.9, 1.1)
        ax.set_xlabel(r"$|L|\,[M]$ of a member")
        ax.set_title(f"{lab}, $r_p$ = 7-10 M", fontsize=9)
        comp["sc4"][lab] = dict(n_plunged=len(Lp), plunges_inside_capture_region=(
            float(np.mean(consistent)) if consistent else None))
    axs[0].set_ylabel(r"$E$ (test particle; Newton: $1 + v^2/2 - M/r$)")
    axs[0].legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc4_capture_plane"))
    plt.close(fig)

    # ---------------- SC0d: flat-space moving binary ----------------
    fb = json.load(open(os.path.join(a.flat, "flat_binary.json")))
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.8))
    cols = {"hrna": P["red"], "hrna_py": P["orange"], "hrna_sym": P["yellow"], "newton": P["blue"]}
    for k, (t, y) in fb["curves"].items():
        ax.plot(t, y, color=cols.get(k, "k"), lw=1.4 if k != "hrna_py" else 0.9,
                ls="-" if k != "hrna_py" else "--", label=k)
    t = np.linspace(0, fb["summary"]["T"], 200)
    ax.plot(t, 0.5 * fb["summary"]["predicted_acc"] * t ** 2, **fs.GUIDE, label="estimate (entry 2)")
    ax.set_xlabel(r"$t\,[M]$")
    ax.set_ylabel(r"CM displacement $\perp V$ $[M]$")
    ax.set_title("SC0d: binary moving at $V = 0.28$, $M = 0$", fontsize=9)
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc0d_flat_binary"))
    plt.close(fig)
    comp["sc0d"] = fb["summary"]

    # ---------------- SC5: NR start state ----------------
    z = np.load(os.path.join(a.nrstate, "nrstate.npz"))
    nr = json.load(open(os.path.join(a.nrstate, "nrstate.json")))
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    st = {"NF": (P["blue"], "Newton fixed"), "NT": (P["green"], "Newton full"), "H": (P["red"], "HRNA"),
          "HG": (P["orange"], r"HRNA $\Gamma$-corr."), "S": (P["yellow"], r"sym. $\Gamma$-corr.")}
    for lab, (col, name) in st.items():
        t = z[lab + "_t"]
        axs[0].plot(t, z[lab + "_r1"], color=col, lw=1.2, label=f"{name}: $m_1$")
        axs[0].plot(t, z[lab + "_r2"], color=col, lw=1.0, ls="--")
        axs[1].plot(t, z[lab + "_sep"] / 3.0, color=col, lw=1.2, label=f"{name} ({nr[lab]['status']})")
    axs[0].axhline(2.5, **fs.MASK_LINE)
    axs[0].set_yscale("log")
    axs[0].set_xlim(0, 400)
    axs[0].set_ylim(1.5, 200)
    axs[0].set_xlabel(r"$t\,[M]$")
    axs[0].set_ylabel(r"distance from the heavy hole $[M]$ (solid $m_1$, dashed $m_2$)")
    axs[0].legend(frameon=False, fontsize=6, loc="upper left")
    axs[0].set_title("SC5: start state of hills_q10_m8", fontsize=9)
    axs[1].set_xlim(0, 120)
    axs[1].set_ylim(0, 3)
    axs[1].set_xlabel(r"$t\,[M]$")
    axs[1].set_ylabel(r"binary separation $/a_0$")
    axs[1].legend(frameon=False, fontsize=6, loc="upper left")
    axs[1].set_title("SC3a: the binary before pericentre", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc5_nrstate"))
    plt.close(fig)
    comp["sc5"] = {k: {kk: nr[k].get(kk) for kk in ("status", "outcome", "plunged", "plunge_t", "E_u",
                                                    "rmin", "sep_early_max", "sep_min")}
                   for k in st}

    # ---------------- SC0: self-test figure is made by selftest.py; copy numbers ----------------
    if a.selftest:
        comp["sc0"] = json.load(open(os.path.join(a.selftest, "selftest.json")))
    json.dump(comp, open(os.path.join(out, "compare.json"), "w"), indent=1, default=float)
    print(json.dumps({k: comp[k] for k in comp if k in ("sc1", "sc2", "sc4", "sc0d")}, indent=1,
                     default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", nargs="?", default=None)
    ap.add_argument("--scan", required=True)
    ap.add_argument("--flat", required=True)
    ap.add_argument("--nrstate", required=True)
    ap.add_argument("--hrnapy", default=None)
    ap.add_argument("--selftest", default=None)
    main(ap.parse_args())
