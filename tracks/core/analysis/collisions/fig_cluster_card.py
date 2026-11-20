#!/usr/bin/env python3
"""Figure and comparison numbers of test C of coll2-close (JOURNAL-coll2.md, 2026-11-20):
the relativistic cluster y_c = 0.819 at Knudsen number 3 over 150 M on the card with
<particles> coll_energy = cell and = particle, against the wave-1 run of the release
executable (option absent, which is the behaviour of `cell`).

  fig_cluster_card.py OUT --run RUNDIR --release RELDIR [--variants VARDIR]

RUNDIR/{off,kn3_cell,kn3_particle}: the card runs of this package (st.nrpic.hst,
st.coll.hst). RELDIR/{off,kn3}: the wave-1 card runs of the release core-v0.3 (same deck,
initial data, seed). VARDIR/{kn3_f1,kn3_f2}: wave-1 runs with smaller collision cells
(another collision sequence; shown only as the size of a change of the sequence).
Writes OUT/cluster_card.json and OUT/fig_cluster_card.png.
"""
import argparse
import json
import os

import numpy as np

import common
from nrpic import collide

INT_COLS = ["ncycle", "n_part", "n_cells", "n_tested", "n_coll", "n_updated", "n_trunc",
            "max_nsub", "min_N", "n_bad_cells"]


def lapse(rundir):
    """time and central lapse (column 13 of st.nrpic.hst), last record of each cycle."""
    rows = {}
    with open(os.path.join(rundir, "st.nrpic.hst")) as fp:
        for line in fp:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            rows[int(v[1])] = (float(v[0]), float(v[12]))
    a = np.array([rows[k] for k in sorted(rows)])
    return a[:, 0], a[:, 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", required=True)
    ap.add_argument("--release", required=True)
    ap.add_argument("--variants", default="")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    res = {"run": args.run, "release": args.release, "variants": args.variants}

    t, a_off = lapse(os.path.join(args.run, "off"))
    _, a_cell = lapse(os.path.join(args.run, "kn3_cell"))
    _, a_part = lapse(os.path.join(args.run, "kn3_particle"))
    tr, a_rel = lapse(os.path.join(args.release, "kn3"))
    _, a_rel_off = lapse(os.path.join(args.release, "off"))
    n = min(len(t), len(tr))
    assert np.allclose(t[:n], tr[:n], rtol=0, atol=1e-12)
    res["lapse"] = dict(
        cell_vs_release_max=float(np.max(np.abs(a_cell[:n] - a_rel[:n]))),
        off_vs_release_off_max=float(np.max(np.abs(a_off[:n] - a_rel_off[:n]))),
        particle_vs_cell_max=float(np.max(np.abs(a_part - a_cell))),
        cell_vs_off_max=float(np.max(np.abs(a_cell - a_off))),
        end={"off": float(a_off[-1]), "kn3_cell": float(a_cell[-1]),
             "kn3_particle": float(a_part[-1]), "release_kn3": float(a_rel[-1])})

    hc = collide.read_history(os.path.join(args.run, "kn3_cell", "st.coll.hst"))
    hp = collide.read_history(os.path.join(args.run, "kn3_particle", "st.coll.hst"))
    hr = collide.read_history(os.path.join(args.release, "kn3", "st.coll.hst"))
    m = min(len(hc["time"]), len(hr["time"]))
    rows_equal = {c: bool(np.array_equal(hc[c][:m], hr[c][:m])) for c in INT_COLS}
    first_diff = {}
    for c in INT_COLS:
        d = np.nonzero(hc[c][:m] != hr[c][:m])[0]
        first_diff[c] = int(hc["ncycle"][d[0]]) if len(d) else None
    res["cell_vs_release_history"] = dict(
        rows=[len(hc["time"]), len(hr["time"])], integer_columns_equal=rows_equal,
        first_differing_cycle=first_diff,
        collisions=[int(hc["n_coll"].sum()), int(hr["n_coll"].sum())],
        dE_particles_sum_rel=[float(hc["dE_particles"].sum()/hc["sum_MW_particles"][0]),
                              float(hr["dE_particles"].sum()/hr["sum_MW_particles"][0])])
    dh_c = np.cumsum(hc["dH_particles"])/hc["sum_MH_particles"][0]
    dh_p = np.cumsum(hp["dH_particles"])/hp["sum_MH_particles"][0]
    dw_c = np.cumsum(hc["dE_particles"])/hc["sum_MW_particles"][0]
    dw_p = np.cumsum(hp["dE_particles"])/hp["sum_MW_particles"][0]
    res["sum_MH_change"] = {"kn3_cell": float(dh_c[-1]), "kn3_particle": float(dh_p[-1]),
                            "kn3_particle_max_abs": float(np.max(np.abs(dh_p)))}
    res["sum_MW_change"] = {"kn3_cell": float(dw_c[-1]), "kn3_particle": float(dw_p[-1])}
    nprop_p = float(hp["n_coll"].sum() + hp["n_balance"].sum() + hp["n_noroot"].sum())
    res["particle_rejected_share"] = float(hp["n_balance"].sum()/nprop_p)
    res["particle_noroot"] = int(hp["n_noroot"].sum())

    variants = {}
    if args.variants:
        for v in ("kn3_f1", "kn3_f2"):
            p = os.path.join(args.variants, v)
            if os.path.isdir(p):
                variants[v] = lapse(p)[1]
        res["variants_vs_release_kn3_max"] = {
            v: float(np.max(np.abs(a[:n] - a_rel[:n]))) for v, a in variants.items()}

    with open(os.path.join(out, "cluster_card.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(8.4, 5.6))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.965, wspace=0.30,
                        hspace=0.34)
    c_off, c_cell, c_part = "k", fs.PAL["red"], fs.PAL["blue"]
    ax = axs[0, 0]
    ax.plot(t, a_off, color=c_off, lw=1.2, label="no collisions")
    ax.plot(t, a_cell, color=c_cell, lw=1.2, label="cell")
    ax.plot(tr[:n], a_rel[:n], color=fs.PAL["yellow"], lw=1.0, ls=":",
            label="release, option absent")
    ax.plot(t, a_part, color=c_part, lw=1.2, label="particle")
    ax.set_ylabel(r"central lapse $\alpha_c$")
    ax.set_title("(a) central lapse, Kn = 3", fontsize=9, loc="left")
    ax.legend(fontsize=7.5, loc="lower left")

    ax = axs[0, 1]
    tiny = 1e-20
    ax.semilogy(hc["time"], np.maximum(np.abs(dh_c), tiny), color=c_cell, lw=1.2,
                label=r"cell: $\Sigma M H$")
    ax.semilogy(hp["time"], np.maximum(np.abs(dh_p), tiny), color=c_part, lw=1.2,
                label=r"particle: $\Sigma M H$")
    ax.semilogy(hc["time"], np.maximum(np.abs(dw_c), tiny), color=c_cell, lw=1.0, ls="--",
                label=r"cell: $\Sigma M W$")
    ax.semilogy(hp["time"], np.maximum(np.abs(dw_p), tiny), color=c_part, lw=1.0, ls="--",
                label=r"particle: $\Sigma M W$")
    ax.axhline(1e-12, **fs.GUIDE)
    ax.set_ylabel("|cumulative change| / initial")
    ax.set_title("(b) change by the collision steps", fontsize=9, loc="left")
    ax.legend(fontsize=7, loc="center right", ncol=1)

    ax = axs[1, 0]
    ax.plot(hc["time"], np.cumsum(hc["n_coll"]), color=c_cell, lw=1.2, label="cell")
    ax.plot(hp["time"], np.cumsum(hp["n_coll"]), color=c_part, lw=1.2, label="particle")
    ax.plot(hc["time"], np.cumsum(hc["sum_P"]), color=c_cell, lw=0.8, ls="--",
            label=r"cell: $\Sigma P$")
    ax.plot(hp["time"], np.cumsum(hp["sum_P"]), color=c_part, lw=0.8, ls="--",
            label=r"particle: $\Sigma P$")
    ax.set_ylabel("collisions (cumulative)")
    ax.set_title("(c) collisions and expected number", fontsize=9, loc="left")
    ax.legend(fontsize=7.5, loc="upper left")

    ax = axs[1, 1]
    ax.semilogy(t[:n], np.maximum(np.abs(a_cell[:n] - a_rel[:n]), tiny), color=c_cell,
                lw=1.2, label="cell minus release")
    ax.semilogy(t, np.maximum(np.abs(a_part - a_cell), tiny), color=c_part, lw=1.2,
                label="particle minus cell")
    ax.semilogy(t, np.maximum(np.abs(a_cell - a_off), tiny), color="k", lw=1.0,
                label="cell minus no collisions")
    for v, a in variants.items():
        lab = {"kn3_f1": "release, cells 0.5 M", "kn3_f2": "release, cells 1 M"}[v]
        ax.semilogy(t[:n], np.maximum(np.abs(a[:n] - a_rel[:n]), tiny), color="grey",
                    lw=0.8, ls=":" if v.endswith("f1") else "--",
                    label=lab + " minus 2 M")
    ax.set_ylabel(r"$|\Delta\alpha_c|$")
    ax.set_ylim(1e-17, 1e-1)
    ax.set_title("(d) central-lapse differences", fontsize=9, loc="left")
    ax.legend(fontsize=6.5, loc="center right")
    for a in axs.ravel():
        a.set_xlabel(r"$t/M$")
    fig.savefig(os.path.join(out, "fig_cluster_card.png"), dpi=200)


if __name__ == "__main__":
    main()
