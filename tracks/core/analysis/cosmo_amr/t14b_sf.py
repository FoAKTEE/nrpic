#!/usr/bin/env python3
"""T14b of the work package cosmo-amr, case Sf (the linear cloud with deposit_fine_shape on
a lattice at rest, statically refined patch): the card run of Slurm job 4763 against the
processor run of T2b, with the measures t14_card.py applies to the homogeneous cases U, S,
A (that script does not read Sf).  Prediction: tracks/core/JOURNAL-cosmo-amr.md, entry of
2026-11-21 03:26 (bounds of the homogeneous cases), repeated in tracks/core/JOURNAL.md,
entry of 2026-11-21T07:47Z.  Nothing is run here.

    t14b_sf.py --card CARD_RUN_DIR --t2 T2B_RUN_DIR --out DIR

Writes DIR/t14b_sf_summary.json and DIR/fig_t14b_sf.{pdf,png}; exit status 0 if every
bound holds."""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
import amrlib as A                             # noqa: E402
from t14_card import batch_status, rel, spread  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--t2", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    rc = batch_status(a.card).get("Sf")
    hc = A.read_hst(os.path.join(a.card, "Sf", "flrw.nrpic.hst"))
    hp = A.read_hst(os.path.join(a.t2, "Sf", "flrw.nrpic.hst"))
    sc = A.read_hst(os.path.join(a.card, "Sf", "flrw.cstat.hst"))
    sp = A.read_hst(os.path.join(a.t2, "Sf", "flrw.cstat.hst"))
    r = {"exit_card": rc,
         "records_card": int(len(hc["time"])), "records_cpu": int(len(hp["time"])),
         "chi_spread_max_card": float(np.max(spread(sc["chi_max"], sc["chi_min"]))),
         "chi_spread_max_cpu": float(np.max(spread(sp["chi_max"], sp["chi_min"]))),
         "E_spread_max_card": float(np.max(spread(hc["E_max"], hc["E_min"]))),
         "E_spread_max_cpu": float(np.max(spread(hp["E_max"], hp["E_min"]))),
         "time_vs_cpu": rel(hc["time"][1:], hp["time"][1:]),
         "alpha_max_vs_cpu": rel(hc["alpha_max"], hp["alpha_max"]),
         "nmb_card": sorted(set(int(x) for x in hc["nmb"])),
         "nmb_equal": bool(len(hc["nmb"]) == len(hp["nmb"])
                           and np.array_equal(hc["nmb"], hp["nmb"])),
         "identity_max_card": float(np.max(np.abs(hc["int_E"]/hc["sum_mW"] - 1.0))),
         "identity_max_cpu": float(np.max(np.abs(hp["int_E"]/hp["sum_mW"] - 1.0)))}
    v = {"status 0": rc == 0,
         "chi and E uniform on the card to 1e-12": max(r["chi_spread_max_card"],
                                                       r["E_spread_max_card"]) <= 1e-12,
         "alpha_max equal to the processor run to 1e-12": r["alpha_max_vs_cpu"] <= 1e-12,
         "MeshBlock counts equal at every record": r["nmb_equal"],
         "identity on the card below 1e-13": r["identity_max_card"] <= 1e-13}
    r["verdicts"] = v
    r["verdict"] = "PASS" if all(v.values()) else "FAIL"
    with open(os.path.join(out, "t14b_sf_summary.json"), "w") as f:
        json.dump(r, f, indent=1)
        f.write("\n")
    for k, x in r.items():
        if k != "verdicts":
            print(k, x)
    for k, x in v.items():
        print("  %-48s %s" % (k, "held" if x else "FAILED"))

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.2))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.17, top=0.88, wspace=0.32)
    floor = 1e-18
    for lab, h, s, c in (("card", hc, sc, fs.SERIES[0]), ("processors", hp, sp, fs.SERIES[1])):
        m = min(len(h["time"]), len(s["time"]))
        ax[0].semilogy(h["time"], np.maximum(spread(h["E_max"], h["E_min"]), floor),
                       color=c, label="E, " + lab)
        ax[0].semilogy(s["time"][:m], np.maximum(spread(s["chi_max"], s["chi_min"])[:m], floor),
                       color=c, ls="--", label="chi, " + lab)
    ax[0].axhline(1e-12, color="0.5", lw=0.8, ls=":")
    ax[0].set_xlabel("conformal time")
    ax[0].set_ylabel("max/min - 1")
    ax[0].set_title("(a) homogeneity of Sf", fontsize=9)
    ax[0].legend(frameon=False, fontsize=7)
    m = min(len(hc["time"]), len(hp["time"]))
    d = np.abs(hc["alpha_max"][:m]/hp["alpha_max"][:m] - 1.0)
    ax[1].semilogy(hc["time"][:m], np.maximum(d, floor), color=fs.SERIES[0])
    ax[1].axhline(1e-12, color="0.5", lw=0.8, ls=":")
    ax[1].set_xlabel("conformal time")
    ax[1].set_ylabel("|alpha_max card / processors - 1|")
    ax[1].set_title("(b) card against processors (dotted: bound)", fontsize=9)
    fs.save(fig, os.path.join(out, "fig_t14b_sf"))
    plt.close(fig)
    print("T14b Sf", r["verdict"])
    return 0 if r["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
