#!/usr/bin/env python3
"""Test V4 of tracks/core/JOURNAL-idsolve.md (entry 13): the card runs of card_vector.sh
(card build of a7a32cd) against the processor runs of the same cases.

    analyze_card_v4.py

Finds the card runs by their tags in tracks/core/runs/*/manifest.json, compares the
iteration records (<basename>.idsolve.txt: outer iterations, conjugate-gradient steps and
V cycles of the scalar step, V cycles of the vector step, residual histories), psi
(<basename>.idsolve.bin) and W (<basename>.idvector.bin), and writes card_v4_numbers.json
and figs/card_v4 (PDF and PNG). With NRPIC_RUN_DIR set (a run registered by nrpic-run) the
numbers and the figure are copied there as well.
"""
import glob
import json
import os
import shutil
import sys

import numpy as np

import idlib
import run_vector as rv
from nrpic import figstyle as fs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PAIRS = {   # card tag -> (processor run, basename, label)
    "idsolve-v4-gauss_code_n64_card": ("core-20261115-155051-87e189e", "gauss",
                                       "Gaussian at rest, scalar"),
    "idsolve-v4-gboost_code_n64_card": ("core-20261115-183239-ca15f8b", "gboost",
                                        "moving Gaussian, vector stencil form"),
    "idsolve-v4-gboost_vcode_n64_card": ("core-20261115-185858-a7a32cd", "gboost",
                                         "moving Gaussian, vector mode code"),
}
MARK = {"idsolve-v4-gauss_code_n64_card": "o",
        "idsolve-v4-gboost_code_n64_card": "s",
        "idsolve-v4-gboost_vcode_n64_card": "^"}


def radial_max(r, a, nb=32):
    """Largest value of a in radial bins of r (for a readable plot of 64^3 cells)."""
    edges = np.linspace(0.0, r.max()*1.0001, nb + 1)
    idx = np.digitize(r.ravel(), edges) - 1
    out = np.full(nb, np.nan)
    flat = a.ravel()
    for b in range(nb):
        sel = idx == b
        if sel.any():
            out[b] = flat[sel].max()
    return 0.5*(edges[1:] + edges[:-1]), out


def main():
    found = {}
    for p in glob.glob(os.path.join(idlib.WT, "tracks/core/runs/*/manifest.json")):
        with open(p) as f:
            m = json.load(f)
        if m.get("tag") in PAIRS:
            found[m["tag"]] = m["run_id"]
    out, rec = {}, {}
    for tag, (cpu, base, label) in PAIRS.items():
        if tag not in found:
            print("%s: no card run yet" % tag)
            continue
        card = found[tag]
        dc, dg = idlib.run_dir(cpu), idlib.run_dir(card)
        tc, lc = idlib.read_idsolve_txt(os.path.join(dc, base + ".idsolve.txt"))
        tg, lg = idlib.read_idsolve_txt(os.path.join(dg, base + ".idsolve.txt"))
        bc = idlib.read_idsolve_bin(os.path.join(dc, base + ".idsolve.bin"))
        bg = idlib.read_idsolve_bin(os.path.join(dg, base + ".idsolve.bin"))
        n = min(tc.shape[0], tg.shape[0])
        r = dict(card=card, cpu=cpu, label=label,
                 outer_iterations_cpu=int(tc.shape[0]) - 1,
                 outer_iterations_card=int(tg.shape[0]) - 1,
                 cg_steps_cpu=[int(v) for v in tc[:, 10]],
                 cg_steps_card=[int(v) for v in tg[:, 10]],
                 v_cycles_cpu=[int(v) for v in tc[:, 11]],
                 v_cycles_card=[int(v) for v in tg[:, 11]],
                 cg_v_cycles_equal=bool(tc.shape == tg.shape
                                        and np.array_equal(tc[:, 10:12], tg[:, 10:12])),
                 max_rel_diff_residual_history=float(
                     np.max(np.abs(tc[:n, 1] - tg[:n, 1])/np.abs(tc[:n, 1]))),
                 max_rel_diff_psi=float(np.abs(bg["psi"] - bc["psi"]).max()
                                        / np.abs(bc["psi"]).max()),
                 max_abs_diff_psi_over_max_psi_minus_1=float(
                     np.abs(bg["psi"] - bc["psi"]).max()/np.abs(bc["psi"] - 1.0).max()),
                 max_H_cpu=float(np.abs(bc["H"]).max()),
                 max_H_card=float(np.abs(bg["H"]).max()),
                 summary_cpu=lc, summary_card=lg)
        rc, _, _ = idlib.mesh_r(bc)
        rr = dict(tc=tc, tg=tg, r=rc, dpsi=np.abs(bg["psi"] - bc["psi"]))
        vc = os.path.join(dc, base + ".idvector.bin")
        if os.path.exists(vc):
            wc = rv.read_idvector_bin(vc)
            wg = rv.read_idvector_bin(os.path.join(dg, base + ".idvector.bin"))
            wscale = np.abs(wc["Wx"]).max()
            dW = np.max([np.abs(wg[k] - wc[k]) for k in ("Wx", "Wy", "Wz")], axis=0)
            r["max_rel_diff_W"] = float(dW.max()/wscale)
            r["vector_v_cycles_cpu"] = [int(v) for v in tc[:, 18]]
            r["vector_v_cycles_card"] = [int(v) for v in tg[:, 18]]
            r["vector_v_cycles_equal"] = bool(tc.shape == tg.shape
                                              and np.array_equal(tc[:, 18], tg[:, 18]))
            r["relv_cpu"] = [float(v) for v in tc[:, 13]]
            r["relv_card"] = [float(v) for v in tg[:, 13]]
            rr["dW"] = dW/wscale
        out[tag] = r
        rec[tag] = rr
        for k, v in r.items():
            if not isinstance(v, list):
                print("%-34s %-40s %s" % (tag[11:], k, v))
        for k in ("v_cycles", "vector_v_cycles"):
            if k + "_cpu" in r and r[k + "_cpu"] != r[k + "_card"]:
                d = [(i, a, b) for i, (a, b) in enumerate(zip(r[k + "_cpu"], r[k + "_card"]))
                     if a != b]
                print("%-34s %-40s (iteration, processor, card) %s" % (tag[11:], k + " differ", d))
    path_json = os.path.join(idlib.HERE, "card_v4_numbers.json")
    idlib.save_json(path_json, out)

    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.95, wspace=0.3,
                        hspace=0.38)
    cpu_kw = dict(color=fs.PAL["blue"], lw=1.5)
    card_kw = dict(color=fs.PAL["red"], ls="none", ms=4, mfc="none")
    # (a) residual of the scalar equation
    ax = axs[0, 0]
    for tag, rr in rec.items():
        it = np.arange(rr["tc"].shape[0])
        ax.semilogy(it, rr["tc"][:, 1], **cpu_kw)
        ax.semilogy(np.arange(rr["tg"].shape[0]), rr["tg"][:, 1], marker=MARK[tag],
                    label=out[tag]["label"], **card_kw)
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel(r"scalar: max$|F|$ / scale")
    ax.set_title("(a) scalar residual; line processor, marker card", fontsize=9)
    ax.legend(fontsize=7, loc="lower left")
    # (b) residual of the vector equation
    ax = axs[0, 1]
    for tag, rr in rec.items():
        if "dW" not in rr:
            continue
        ax.semilogy(np.arange(rr["tc"].shape[0]), rr["tc"][:, 13], **cpu_kw)
        ax.semilogy(np.arange(rr["tg"].shape[0]), rr["tg"][:, 13], marker=MARK[tag],
                    label=out[tag]["label"], **card_kw)
    ax.axhline(1.0e-6, **fs.MASK_LINE)
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel(r"vector: max$|F_v|$ / scale")
    ax.set_title("(b) vector residual (tolerances 1e-10, 1e-6 grey)", fontsize=9)
    ax.legend(fontsize=7, loc="lower left")
    # (c) V cycles per outer iteration, card minus processor
    ax = axs[1, 0]
    off = {"idsolve-v4-gauss_code_n64_card": -0.2, "idsolve-v4-gboost_code_n64_card": 0.0,
           "idsolve-v4-gboost_vcode_n64_card": 0.2}
    for tag, rr in rec.items():
        n = min(rr["tc"].shape[0], rr["tg"].shape[0])
        it = np.arange(n) + off[tag]
        ax.plot(it, rr["tg"][:n, 11] - rr["tc"][:n, 11], marker=MARK[tag], ls="none",
                color=fs.PAL["blue"], ms=4, mfc="none")
        ax.plot(it, rr["tg"][:n, 10] - rr["tc"][:n, 10], marker=MARK[tag], ls="none",
                color=fs.PAL["green"], ms=3)
        if "dW" in rr:
            ax.plot(it, rr["tg"][:n, 18] - rr["tc"][:n, 18], marker=MARK[tag], ls="none",
                    color=fs.PAL["red"], ms=5)
    ax.plot([], [], color=fs.PAL["green"], marker="o", ls="none", ms=3,
            label="CG steps, scalar step")
    ax.plot([], [], color=fs.PAL["blue"], marker="o", ls="none", mfc="none", ms=4,
            label="V cycles, scalar step")
    ax.plot([], [], color=fs.PAL["red"], marker="o", ls="none", ms=5,
            label="V cycles, vector step")
    ax.axhline(0.0, **fs.THIN)
    ax.set_ylim(-1.6, 1.6)
    ax.set_xlabel("outer iteration")
    ax.set_ylabel("card minus processor")
    ax.set_title("(c) inner iteration counts", fontsize=9)
    ax.legend(fontsize=7, loc="lower left")
    # (d) difference of the solved fields
    ax = axs[1, 1]
    for tag, rr in rec.items():
        rb, mp = radial_max(rr["r"], rr["dpsi"])
        ax.semilogy(rb, mp, marker=MARK[tag], color=fs.PAL["blue"], ms=3, lw=1.0,
                    mfc="none")
        if "dW" in rr:
            rb, mw = radial_max(rr["r"], rr["dW"])
            ax.semilogy(rb, mw, marker=MARK[tag], color=fs.PAL["red"], ms=3, lw=1.0)
    ax.plot([], [], color=fs.PAL["blue"], label=r"$|\Delta\psi|$")
    ax.plot([], [], color=fs.PAL["red"], label=r"max$_i|\Delta W_i|$ / max$|W_x|$")
    ax.axhline(1.0e-10, **fs.MASK_LINE)
    ax.set_xlabel(r"$r$ (largest value per radial bin)")
    ax.set_ylabel("card minus processor")
    ax.set_title("(d) solved fields; grey: predicted bound 1e-10", fontsize=9)
    ax.legend(fontsize=7, loc="center right")
    path_fig = os.path.join(idlib.FIGS, "card_v4")
    fs.save(fig, path_fig)
    plt.close(fig)
    rd = os.environ.get("NRPIC_RUN_DIR")
    if rd:
        for p in (path_json, path_fig + ".png", path_fig + ".pdf"):
            shutil.copy2(p, rd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
