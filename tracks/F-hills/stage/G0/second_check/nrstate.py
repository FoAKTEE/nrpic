#!/usr/bin/env python3
"""SC5 (and SC3a): the start state of the first NR passage, three_punctures/inputs/
hills_q10_m8.athinput (bare masses, positions, momenta P = m v of the three punctures), under
each model of models.py. Usage: nrstate.py <outdir>. Writes nrstate.json and nrstate.npz."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models as mdl  # noqa: E402

INPUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "three_punctures", "inputs",
                                      "hills_q10_m8.athinput"))


def read_problem(path):
    blk, d = None, {}
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("<"):
            blk = line.strip("<>").strip()
            continue
        if blk == "problem" and "=" in line:
            k, v = (s.strip() for s in line.split("=", 1))
            d[k] = v
    n = int(d["ncomp"])
    m = np.array([float(d[f"comp{i}_mass"]) for i in range(n)])
    x = np.array([[float(d[f"comp{i}_x{k}"]) for k in (1, 2, 3)] for i in range(n)])
    p = np.array([[float(d[f"comp{i}_p{k}"]) for k in (1, 2, 3)] for i in range(n)])
    return m, x, p


def main(out):
    os.makedirs(out, exist_ok=True)
    m, x, p = read_problem(INPUT)
    v = p / m[:, None]
    (m1, m2, M) = m
    assert abs(M - 1.0) < 1e-12
    xh, vh = x[2], v[2]
    rel = np.concatenate([x[0] - xh, v[0] - vh, x[1] - xh, v[1] - vh])
    full = np.concatenate([x[2], x[0], x[1], v[2], v[0], v[1]])
    # Gamma-corrected relative state: velocities relative to the members' CM divided by Gamma_cm
    mb = m1 + m2
    xc = (m1 * rel[0:3] + m2 * rel[6:9]) / mb
    vc = (m1 * rel[3:6] + m2 * rel[9:12]) / mb
    gam = mdl.gamma_of(xc, vc)
    relg = rel.copy()
    relg[3:6] = vc + (rel[3:6] - vc) / gam
    relg[9:12] = vc + (rel[9:12] - vc) / gam
    cases = {"NF": ("newton_fixed", rel), "NT": ("newton_full", full), "H": ("hrna", rel),
             "HG": ("hrna", relg), "S": ("hrna_sym", relg)}
    res, arrays = {}, {}
    for lab, (model, y0) in cases.items():
        r = mdl.run(model, math.nan, math.nan, m1=m1, m2=m2, a0=3.0, y0=y0, record_dt=0.5,
                    t_max=1500.0)
        R = r.pop("rec")
        t = r.pop("rec_t")
        arrays[lab + "_t"] = t
        arrays[lab + "_r1"] = np.linalg.norm(R[:, 0:3], axis=1)
        arrays[lab + "_r2"] = np.linalg.norm(R[:, 6:9], axis=1)
        arrays[lab + "_sep"] = np.linalg.norm(R[:, 0:3] - R[:, 6:9], axis=1)
        sep = arrays[lab + "_sep"]
        early = t <= 50.0
        r["sep_early_min"] = float(sep[early].min())
        r["sep_early_max"] = float(sep[early].max())
        res[lab] = {k: (None if isinstance(v_, float) and not math.isfinite(v_) else v_)
                    for k, v_ in r.items()}
        print(lab, json.dumps({k: res[lab][k] for k in ("status", "t_end", "outcome", "plunged",
                                                       "plunge_t", "E_u", "rmin", "cm_peri",
                                                       "sep_early_min", "sep_early_max",
                                                       "gr_capture_criterion")}), flush=True)
    res["gamma_cm_start"] = gam
    res["input"] = INPUT
    json.dump(res, open(os.path.join(out, "nrstate.json"), "w"), indent=1, default=float)
    np.savez(os.path.join(out, "nrstate.npz"), **arrays)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
