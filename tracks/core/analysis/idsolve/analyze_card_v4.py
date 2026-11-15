#!/usr/bin/env python3
"""Test V4 of tracks/core/JOURNAL-idsolve.md (entry 13): the card runs of card_vector.sh
(card build of a7a32cd) against the processor runs of the same cases.

    analyze_card_v4.py

Finds the card runs by their tags in tracks/core/runs/*/manifest.json, compares the
iteration counts (summary lines of <basename>.idsolve.txt), psi (<basename>.idsolve.bin)
and W (<basename>.idvector.bin), and writes card_v4_numbers.json.
"""
import glob
import json
import os
import sys

import numpy as np

import idlib
import run_vector as rv

PAIRS = {   # card tag -> (processor run, basename)
    "idsolve-v4-gauss_code_n64_card": ("core-20261115-155051-87e189e", "gauss"),
    "idsolve-v4-gboost_code_n64_card": ("core-20261115-183239-ca15f8b", "gboost"),
    "idsolve-v4-gboost_vcode_n64_card": ("core-20261115-185858-a7a32cd", "gboost"),
}


def main():
    found = {}
    for p in glob.glob(os.path.join(idlib.WT, "tracks/core/runs/*/manifest.json")):
        with open(p) as f:
            m = json.load(f)
        if m.get("tag") in PAIRS:
            found[m["tag"]] = m["run_id"]
    out = {}
    for tag, (cpu, base) in PAIRS.items():
        if tag not in found:
            print("%s: no card run yet" % tag)
            continue
        card = found[tag]
        dc, dg = idlib.run_dir(cpu), idlib.run_dir(card)
        tc, lc = idlib.read_idsolve_txt(os.path.join(dc, base + ".idsolve.txt"))
        tg, lg = idlib.read_idsolve_txt(os.path.join(dg, base + ".idsolve.txt"))
        bc = idlib.read_idsolve_bin(os.path.join(dc, base + ".idsolve.bin"))
        bg = idlib.read_idsolve_bin(os.path.join(dg, base + ".idsolve.bin"))
        r = dict(card=card, cpu=cpu, iterations_cpu=int(tc.shape[0]),
                 iterations_card=int(tg.shape[0]),
                 cg_v_cycles_equal=bool(np.array_equal(tc[:, 10:12], tg[:, 10:12])),
                 max_rel_diff_psi=float(np.abs(bg["psi"] - bc["psi"]).max()
                                        / np.abs(bc["psi"]).max()),
                 summary_cpu=lc, summary_card=lg)
        vc = os.path.join(dc, base + ".idvector.bin")
        if os.path.exists(vc):
            wc = rv.read_idvector_bin(vc)
            wg = rv.read_idvector_bin(os.path.join(dg, base + ".idvector.bin"))
            r["max_rel_diff_W"] = float(max(np.abs(wg[k] - wc[k]).max() for k in ("Wx", "Wy", "Wz"))
                                        / np.abs(wc["Wx"]).max())
        out[tag] = r
        for k, v in r.items():
            print("%-40s %-22s %s" % (tag, k, v))
    idlib.save_json(os.path.join(idlib.HERE, "card_v4_numbers.json"), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
